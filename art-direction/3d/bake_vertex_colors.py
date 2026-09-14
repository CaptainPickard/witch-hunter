#!/usr/bin/env python3
"""Bake per-vertex COLOR_0 attributes into race pixelated GLBs.

Defect: per-triangle black/bright patch contrast in the browser. The atlas is
spatially smooth (19 colors, neighbor delta ~4.7/255) but NearestFilter
magnification + per-triangle lighting on the faceted 15k mesh produces harsh
value jumps along triangle boundaries. Vertex-color bake guarantees coherent
shading: each welded vertex gets a bilinearly-sampled atlas color, smoothed
across face-neighbors, stored as COLOR_0 (VEC4 float). The viewer renders
pixelated mode with vertexColors=true + map=null: PSX chunk comes from the low
vertex density at INTERNAL_H=540, with zero per-texel sampling noise.

Usage: bake_vertex_colors.py [dir] (default art-direction/3d/assets/races)
"""
import os, sys, struct, json, io
import numpy as np
from scipy.spatial import cKDTree
from PIL import Image


def weld_vertices(verts, tol=1e-4):
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
    canon = {}
    for i, c in enumerate(inv):
        if c not in canon:
            canon[c] = i
    rep_idx = np.array([canon[c] for c in range(len(uniq))])
    return verts[rep_idx], inv


def bake(path):
    data = open(path, "rb").read()
    jl, _ = struct.unpack_from("<II", data, 12)
    g = json.loads(data[20:20+jl])

    prim = g["meshes"][0]["primitives"][0]
    attrs = prim["attributes"]
    accessors = g["accessors"]
    buffer_views = g["bufferViews"]

    # single binary chunk: starts right after the JSON chunk header
    binoff = 20 + jl + 8
    blen, _ = struct.unpack_from("<II", data, 20 + jl)
    bin_data = bytearray(data[binoff: binoff + blen])

    # --- read positions
    acc = accessors[attrs["POSITION"]]
    bv = buffer_views[acc["bufferView"]]
    poff = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    count = acc["count"]
    pstride = bv.get("byteStride", 12)
    verts = np.empty((count, 3), dtype=np.float32)
    for i in range(count):
        verts[i] = struct.unpack_from("<fff", bin_data, poff + i * pstride)

    # --- read uvs
    acc = accessors[attrs["TEXCOORD_0"]]
    bv = buffer_views[acc["bufferView"]]
    uoff = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    ustride = bv.get("byteStride", 8)
    uvs = np.empty((count, 2), dtype=np.float64)
    for i in range(count):
        u, v = struct.unpack_from("<ff", bin_data, uoff + i * ustride)
        uvs[i] = (u, v)

    # --- extract atlas image
    img = g["images"][0]
    ibv = buffer_views[img["bufferView"]]
    tex = Image.open(io.BytesIO(bin_data[ibv["byteOffset"]: ibv["byteOffset"] + ibv["byteLength"]])).convert("RGB")
    arr = np.asarray(tex, dtype=np.float64)
    h, w = arr.shape[:2]

    # --- weld; representative uv per welded cluster = first uv seen
    wverts, inv = weld_vertices(verts, tol=1e-4)
    wcount = len(wverts)
    wuv = np.empty((wcount, 2), dtype=np.float64)
    seen = np.zeros(wcount, dtype=bool)
    for i, c in enumerate(inv):
        if not seen[c]:
            seen[c] = True
            wuv[c] = uvs[i]

    # --- bilinear sample with clamp
    px = np.clip(wuv[:, 0] * w - 0.5, 0, w - 1)
    py = np.clip((1.0 - wuv[:, 1]) * h, 0, h - 1)
    x0 = np.floor(px).astype(int); x1 = np.clip(x0 + 1, 0, w - 1)
    y0 = np.floor(py).astype(int); y1 = np.clip(y0 + 1, 0, h - 1)
    fx = (px - x0)[:, None]; fy = (py - y0)[:, None]
    c00 = arr[y0, x0]; c10 = arr[y0, x1]; c01 = arr[y1, x0]; c11 = arr[y1, x1]
    col = (c00 * (1 - fx) * (1 - fy) + c10 * fx * (1 - fy) +
           c01 * (1 - fx) * fy + c11 * fx * fy)

    # --- read indices, remap into welded space
    ia = accessors[prim["indices"]]
    ibv = buffer_views[ia["bufferView"]]
    ioff = ibv.get("byteOffset", 0) + ia.get("byteOffset", 0)
    icount = ia["count"]
    comp = ia["componentType"]
    fmt, sz = ("<I", 4) if comp == 5125 else ("<H", 2)
    istride = ibv.get("byteStride", sz)
    flat = np.empty(icount, dtype=np.int64)
    for i in range(icount):
        flat[i] = struct.unpack_from(fmt, bin_data, ioff + i * istride)[0]
    faces = inv[flat.reshape(-1, 3)]

    # --- 2 rounds of face-adjacency smoothing (kills residual per-vertex jumps)
    smooth = col.copy()
    for _ in range(2):
        nbr_sum = np.zeros((wcount, 3), dtype=np.float64)
        nbr_cnt = np.zeros(wcount, dtype=np.float64)
        for k in range(3):
            a, b, c = faces[:, k], faces[:, (k + 1) % 3], faces[:, (k + 2) % 3]
            for src, dst in ((a, b), (a, c), (b, a), (b, c), (c, a), (c, b)):
                np.add.at(nbr_sum, dst, smooth[src])
                np.add.at(nbr_cnt, dst, 1.0)
        mask = nbr_cnt > 0
        smooth[mask] = 0.6 * smooth[mask] + 0.4 * (nbr_sum[mask] / nbr_cnt[mask, None])

    # --- map back to original vertex order, normalize
    vcol = np.clip(smooth[inv] / 255.0, 0, 1)
    coldata = np.concatenate([vcol, np.ones((len(vcol), 1))], axis=1).astype(np.float32)

    # --- append COLOR_0 bufferView + accessor (in-place GLB surgery)
    while len(bin_data) % 4:
        bin_data += b"\x00"
    start = len(bin_data)
    bin_data += coldata.tobytes()
    while len(bin_data) % 4:
        bin_data += b"\x00"
    buffer_views.append({
        "buffer": 0, "byteOffset": start, "byteLength": coldata.nbytes, "target": 34962,
    })
    accessors.append({
        "bufferView": len(buffer_views) - 1, "componentType": 5126,
        "count": len(vcol), "type": "VEC4",
    })
    g["buffers"][0]["byteLength"] = len(bin_data)

    new_attrs = {"COLOR_0": len(accessors) - 1}
    new_attrs.update(attrs)
    prim["attributes"] = new_attrs

    json_out = json.dumps(g, separators=(",", ":")).encode()
    pad = (4 - len(json_out) % 4) % 4
    json_out += b" " * pad
    out = b"glTF" + struct.pack("<II", 2, len(json_out) + 8 + len(bin_data)) \
          + struct.pack("<II", len(json_out), 0x4E4F534A) + json_out \
          + struct.pack("<II", len(bin_data), 0x004E4942) + bytes(bin_data)
    with open(path, "wb") as fh:
        fh.write(out)
    os.chmod(path, 0o644)
    return wcount, count


if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else "/workspace/witch-hunter/art-direction/3d/assets/races"
    for fn in sorted(os.listdir(d)):
        if fn.endswith("-pixelated.glb"):
            wv, total = bake(os.path.join(d, fn))
            print(f"baked COLOR_0: {fn} welded={wv} verts={total}")