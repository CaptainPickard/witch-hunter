#!/usr/bin/env python3
"""Add NORMAL attributes to Witch Hunter race pixelated GLBs.

Root cause of the black-speckle render defect: fast_simplification decimation
returns a bare (positions, faces) result, and the retexture pass rebuilds a
TextureVisuals mesh WITHOUT normals. The exported GLB therefore has
POSITION + TEXCOORD_0 only. three.js r147 lighting (ambient + 3 directionals +
point) renders a normal-less mesh with all lights contributing zero -> the
figure is a flat black silhouette with nearest-filter speckle.

Fix: for each vertex compute the area-weighted average face normal over faces
that share it. Vertices are welded at 1e-4 first so shared edges get smooth
normals. Normal attribute is appended to the existing GLB (POSITION, NORMAL,
TEXCOORD_0), material/texture untouched.

Usage: add_normals.py [dir]   (default: art-direction/3d/assets/races)
"""
import os, sys, io, struct, json
import numpy as np
from scipy.spatial import cKDTree


def weld_vertices(verts, tol=1e-4):
    """Return (unique_vertices, cluster_index_per_input_vertex)."""
    t = cKDTree(verts)
    pairs = t.query_pairs(tol, output_type="ndarray")
    parent = list(range(len(verts)))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in pairs:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    roots = np.array([find(i) for i in range(len(verts))])
    uniq, inv = np.unique(roots, return_inverse=True)
    # canonical representative per cluster = first input index in cluster
    canon = {}
    for i, c in enumerate(inv):
        if c not in canon:
            canon[c] = i
    rep_idx = np.array([canon[c] for c in range(len(uniq))])
    return verts[rep_idx], inv


def add_normals_inplace(path):
    data = open(path, "rb").read()
    jl, jtype = struct.unpack_from("<II", data, 12)
    g = json.loads(data[20:20+jl])

    scene = g["scenes"][g.get("scene", 0)]
    nodes = g["nodes"]
    meshes = g["meshes"]
    accessors = g["accessors"]
    buffer_views = g["bufferViews"]

    # single binary chunk
    pos = 20 + jl
    blen, btype = struct.unpack_from("<II", data, pos)
    binoff = pos + 8
    bin_data = bytearray(data[binoff: binoff + blen])

    # pad bin to 4-byte alignment for appending
    while len(bin_data) % 4:
        bin_data += b"\x00"

    # We'll append new buffer(s) at the end; track cursor
    added_views = []
    def append_buffer(arr, target=34962):
        nonlocal bin_data
        start = len(bin_data)
        bin_data += arr.tobytes()
        while len(bin_data) % 4:
            bin_data += b"\x00"
        added_views.append({
            "buffer": 0,
            "byteOffset": start,
            "byteLength": arr.nbytes,
            "target": target,
        })
        return len(buffer_views) + len(added_views) - 1

    mesh_index = 0
    prim = meshes[mesh_index]["primitives"][0]
    attrs = prim["attributes"]
    pos_acc = attrs["POSITION"]
    acc = accessors[pos_acc]
    bv = buffer_views[acc["bufferView"]]
    poff = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    count = acc["count"]
    pstride = bv.get("byteStride", 12)
    ptype = acc["componentType"]  # expect 5126 float
    assert ptype == 5126, f"POSITION not float32: {ptype}"
    pmin = acc.get("min")
    pmax = acc["max"]

    # read positions
    verts = np.empty((count, 3), dtype=np.float32)
    for i in range(count):
        verts[i] = struct.unpack_from("<fff", bin_data, poff + i * pstride)

    # read indices (expect 5125 uint32; all prod GLBs use uint32 per check)
    idx_acc = accessors[prim["indices"]]
    ibv = buffer_views[idx_acc["bufferView"]]
    ioff = ibv.get("byteOffset", 0) + idx_acc.get("byteOffset", 0)
    icount = idx_acc["count"]
    icomp = idx_acc["componentType"]
    if icomp == 5125:
        fmt, sz = "<I", 4
    elif icomp == 5123:
        fmt, sz = "<H", 2
    else:
        raise RuntimeError(f"unsupported index componentType {icomp}")
    istride = ibv.get("byteStride", sz)
    faces = np.empty((icount // 3, 3), dtype=np.int64)
    flat = np.empty(icount, dtype=np.int64)
    for i in range(icount):
        flat[i] = struct.unpack_from(fmt, bin_data, ioff + i * istride)[0]
    faces = flat.reshape(-1, 3)

    # welded vertices + per-vertex area-weighted normals
    wverts, inv = weld_vertices(verts, tol=1e-4)
    wcount = len(wverts)
    wnorm = np.zeros((wcount, 3), dtype=np.float64)
    warea = np.zeros(wcount, dtype=np.float64)
    faces = inv[faces]  # remap face indices into welded space
    fverts = wverts[faces]
    n = np.cross(fverts[:, 1] - fverts[:, 0], fverts[:, 2] - fverts[:, 0])
    area2 = np.linalg.norm(n, axis=1)
    valid = area2 > 1e-12
    n[valid] /= area2[valid, None]
    # accumulate area-weighted: sum of cross products at each corner vertex
    for k in range(3):
        np.add.at(wnorm, inv[faces[:, k]], n)
    # weld tree query_pairs may link vertices that share no face, that's fine;
    # normalize
    L = np.linalg.norm(wnorm, axis=1)
    L[L < 1e-12] = 1.0
    wnorm /= L[:, None]
    # map welded normals back to original vertex order
    vnorm = wnorm[inv]

    # float32 for GL
    vnorm = vnorm.astype(np.float32)

    # append new bufferView
    nview = append_buffer(vnorm)

    # add accessor
    accessors.append({
        "bufferView": nview,
        "componentType": 5126,
        "count": count,
        "type": "VEC3",
        "min": [float(x) for x in vnorm.min(axis=0)],
        "max": [float(x) for x in vnorm.max(axis=0)],
    })
    n_acc_idx = len(accessors) - 1

    # write into primitive attributes, NORMAL after POSITION, UV after
    new_attrs = {}
    order = ["POSITION", "NORMAL", "TEXCOORD_0", "TANGENT", "COLOR_0"]
    for key in order:
        if key == "NORMAL":
            new_attrs["NORMAL"] = n_acc_idx
        if key in attrs:
            new_attrs[key] = attrs[key]
    prim["attributes"] = new_attrs

    # flush appended buffer bytes into bin_data (already in place)
    buffer_views.extend(added_views)
    # update top-level buffer byteLength
    g["buffers"][0]["byteLength"] = len(bin_data)

    # re-serialize
    json_out = json.dumps(g, separators=(",", ":")).encode()
    pad = (4 - len(json_out) % 4) % 4
    json_out += b" " * pad
    out = b"glTF" + struct.pack("<II", 2, len(json_out) + 8 + len(bin_data)) \
          + struct.pack("<II", len(json_out), 0x4E4F534A) + json_out \
          + struct.pack("<II", len(bin_data), 0x004E4942) + bytes(bin_data)
    with open(path, "wb") as fh:
        fh.write(out)
    os.chmod(path, 0o644)
    return count


if __name__ == "__manual__" or True:
    d = sys.argv[1] if len(sys.argv) > 1 else "/workspace/witch-hunter/art-direction/3d/assets/races"
    for fn in sorted(os.listdir(d)):
        if fn.endswith("-pixelated.glb"):
            add_normals_inplace(os.path.join(d, fn))
            print("normals added:", fn)