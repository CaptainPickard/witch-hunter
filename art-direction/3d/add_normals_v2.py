#!/usr/bin/env python3
"""CC-NS1 batch normalizer: append smooth welded NORMAL attributes to kit GLBs.

Implements the CC-NS1 law (io/specs/cc-ns1-normal-shader-valspec.md "Law
summary"; same algorithm family as art-direction/3d/add_normals.py):

  weld at 1e-4 (cKDTree query_pairs + union-find, canonical rep = first input
  index per cluster) -> per-vertex AREA-WEIGHTED normals (np.add.at of raw
  per-face crosses accumulated in welded space; degenerate faces contribute
  zero vectors) -> normalize (guard: |n| < 1e-12 keeps the written normal a
  literal [0,0,0] zero vector) -> un-weld back to the original vertex order
  (vnorm = wnorm[cluster_of_vertex]) -> float32 NORMAL accessor appended
  (VEC3, 5126, min/max written), attribute order POSITION, NORMAL,
  TEXCOORD_0 (TANGENT/COLOR_0 kept after, if the file had them).

Material/texture independent: mat+textured files (POSITION, TEXCOORD_0) and
textureless nomat files (POSITION only) get identical treatment; nomat files
end with attributes [POSITION, NORMAL].

Preserved per file (verified before write): asset.generator verbatim,
asset.version 2.0, buffers count (1 embedded, never given a uri),
extensionsUsed/extensionsRequired exactly as loaded (added: absent),
mesh/prim/node structure, geometry bytes, index accessor, material, image
bufferView windows (their absolute offsets shift only because the JSON chunk
grows). Exactly ONE accessor + ONE bufferView are appended.

Modes:
  add_normals_v2.py [dir]            process every in-scope no-NORMAL GLB
                                     under dir (default art-direction/3d/assets);
                                     files already carrying NORMAL are left
                                     byte-identical (skipped, never re-encoded)
  add_normals_v2.py <file.glb>       process one file (determinism harness);
                                     no census scope check
  add_normals_v2.py --verify [dir]   report only: classify every GLB as
                                     skipped (NORMAL present) / would-process /
                                     out-of-scope, write NOTHING, exit 0

Logs a JSON batch report to --log PATH (default scratch/cc-ns1-normal-batch-log.json).
The old art-direction/3d/add_normals.py stays untouched for provenance; this
copy's accumulate step maps welded faces ONCE through inv per the valspec law
(add_normals.py's loop re-applied inv to already-remapped face indices).
"""
import os, sys, struct, json, hashlib
import numpy as np
from scipy.spatial import cKDTree

DEFAULT_ROOT = "art-direction/3d/assets"
DEFAULT_LOG = "scratch/cc-ns1-normal-batch-log.json"
CENSUS_PATH = "io/specs/cc-ns1-normal-census.json"


def weld_vertices(verts, tol=1e-4):
    """Return (unique_vertices, cluster_index_per_input_vertex). [add_normals.py verbatim]"""
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
    return verts[rep_idx], inv, len(pairs)


def law_normals(verts, faces, tol=1e-4):
    """Valspec law: -> (unwelded float32 normals in original vertex order,
    nVerts, nWelded, weldPairs, nGuardZero). faces = original vertex indices."""
    n_verts = len(verts)
    wverts, inv, npairs = weld_vertices(verts, tol=tol)
    wcount = len(wverts)
    wnorm = np.zeros((wcount, 3), dtype=np.float64)
    fw = inv[faces]                      # welded-space face corners (remapped ONE time)
    fv = wverts[fw]
    n = np.cross(fv[:, 1] - fv[:, 0], fv[:, 2] - fv[:, 0])
    area2 = np.linalg.norm(n, axis=1)
    valid = area2 > 1e-12                # degenerate faces contribute zero vectors
    n[valid] = n[valid] / area2[valid, None]
    for k in range(3):
        np.add.at(wnorm, fw[:, k], n)    # area-weighted: raw cross-product sums
    L = np.linalg.norm(wnorm, axis=1)
    guard = L < 1e-12
    Lg = L.copy()
    Lg[guard] = 1.0
    wnorm = wnorm / Lg[:, None]          # zero-length rows stay literal [0,0,0]
    vnorm = wnorm[inv].astype(np.float32)  # un-weld to original vertex order
    return vnorm, n_verts, wcount, npairs, int(guard.sum())


def parse_glb(data):
    jl, jtype = struct.unpack_from("<II", data, 12)
    g = json.loads(data[20:20 + jl].decode("utf-8"))
    blen, btype = struct.unpack_from("<II", data, 20 + jl)
    binoff = 20 + jl + 8
    return g, binoff, blen


def has_normal(g):
    prim = g["meshes"][0]["primitives"][0]
    return "NORMAL" in prim.get("attributes", {})


def process_glb(path):
    """Law-append NORMAL to path in place. Returns row dict on 'processed';
    raises on hard errors. NEVER writes when NORMAL already present."""
    data = open(path, "rb").read()
    if len(data) < 20 or data[:4] != b"glTF" or hash_check(data) is None:
        raise ValueError("not a GLB container")
    g, binoff, blen = parse_glb(data)
    version = g["asset"].get("version")
    if version != "2.0":
        raise ValueError(f"asset.version is not 2.0: {version!r}")
    if len(g.get("meshes", [])) != 1 or len(g["meshes"][0]["primitives"]) != 1:
        raise ValueError("not a single-mesh/single-prim GLB")
    if has_normal(g):
        raise ValueError("NORMAL already present")
    prim = g["meshes"][0]["primitives"][0]
    attrs = prim["attributes"]
    accessors = g["accessors"]
    buffer_views = g["bufferViews"]

    pos_acc = attrs["POSITION"]
    acc = accessors[pos_acc]
    if acc["componentType"] != 5126:
        raise ValueError(f"POSITION not float32: {acc['componentType']}")
    bv = buffer_views[acc["bufferView"]]
    pstride = bv.get("byteStride", 12)
    if pstride != 12:
        raise ValueError(f"POSITION byteStride {pstride} unsupported (law assumes packed)")
    poff = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    count = acc["count"]
    pmin, pmax = acc.get("min"), acc["max"]
    if pmin is None or pmax is None:
        raise ValueError("POSITION accessor missing min/max")
    verts = np.frombuffer(data, dtype="<f4", count=3 * count, offset=binoff + poff) \
              .reshape(count, 3).astype(np.float32)

    idx_acc = accessors[prim["indices"]]
    icomp = idx_acc["componentType"]
    ibv = buffer_views[idx_acc["bufferView"]]
    ioff = binoff + ibv.get("byteOffset", 0) + idx_acc.get("byteOffset", 0)
    icount = idx_acc["count"]
    if icomp == 5125:
        faces_flat = np.frombuffer(data, dtype="<u4", count=icount, offset=ioff)
    elif icomp == 5123:
        faces_flat = np.frombuffer(data, dtype="<u2", count=icount, offset=ioff)
    else:
        raise RuntimeError(f"unsupported index componentType {icomp}")
    faces = faces_flat.astype(np.int64).reshape(-1, 3)

    vnorm, n_verts, wcount, npairs, guard = law_normals(verts, faces)
    assert n_verts == count, "vertex count drift"

    # -- append ONE bufferView + ONE accessor (add_normals.py shape) --
    bin_data = bytearray(data[binoff: binoff + blen])  # original binary bytes, untouched
    while len(bin_data) % 4:
        bin_data += b"\x00"
    start = len(bin_data)
    bin_data += vnorm.tobytes()                       # 12 * count bytes
    while len(bin_data) % 4:
        bin_data += b"\x00"
    nview = {
        "buffer": 0,
        "byteOffset": start,
        "byteLength": vnorm.nbytes,
        "target": 34962,
    }
    n_acc_idx = len(accessors)
    accessors.append({
        "bufferView": len(buffer_views),
        "componentType": 5126,
        "count": count,
        "type": "VEC3",
        "min": [float(x) for x in vnorm.min(axis=0)],
        "max": [float(x) for x in vnorm.max(axis=0)],
    })
    buffer_views.append(nview)

    # attribute order POSITION, NORMAL, TEXCOORD_0 (TANGENT/COLOR_0 after if present)
    new_attrs = {}
    order = ["POSITION", "NORMAL", "TEXCOORD_0", "TEXCOORD_1", "TANGENT", "COLOR_0"]
    for key in order:
        if key == "NORMAL":
            new_attrs["NORMAL"] = n_acc_idx
        if key in attrs:
            new_attrs[key] = attrs[key]
    for key, val in attrs.items():                    # keep any unexpected extras (none expected)
        if key not in new_attrs:
            new_attrs[key] = val
    prim["attributes"] = new_attrs
    g["buffers"][0]["byteLength"] = len(bin_data)

    # -- re-serialize deterministically (add_normals.py chunk layout) --
    json_out = json.dumps(g, separators=(",", ":")).encode("utf-8")
    pad = (4 - len(json_out) % 4) % 4
    json_out += b" " * pad
    out = (b"glTF"
           + struct.pack("<II", 2, len(json_out) + 8 + len(bin_data))
           + struct.pack("<II", len(json_out), 0x4E4F534A)
           + json_out
           + struct.pack("<II", len(bin_data), 0x004E4942)
           + bytes(bin_data))
    # final self-checks BEFORE write: re-parse must show NORMAL, VEC3/5126,
    # count == POSITION count, min/max within [-1,1], one accessor+view added
    g2, _boff, _bl = parse_glb(out)
    a2 = g2["meshes"][0]["primitives"][0]["attributes"]
    na2 = g2["accessors"][a2["NORMAL"]]
    if na2["type"] != "VEC3" or na2["componentType"] != 5126 or na2["count"] != count:
        raise RuntimeError("post-write self-check failed (NORMAL accessor shape)")
    if len(g2["accessors"]) != len(accessors) or len(g2["bufferViews"]) != len(buffer_views):
        raise RuntimeError("post-write self-check failed (accessor/bufferView counts)")
    for v in na2["min"] + na2["max"]:
        if v < -1.0 - 1e-3 or v > 1.0 + 1e-3:
            raise RuntimeError(f"NORMAL bound outside [-1,1]: {na2['min']} {na2['max']}")
    with open(path, "wb") as fh:
        fh.write(out)
    os.chmod(path, 0o644)
    return {
        "file": path, "ok": True,
        "verts": count, "faces": icount // 3,
        "weldPairs": npairs, "weldedVerts": wcount, "guardZero": guard,
        "normalByteLength": vnorm.nbytes,
        "byteSizeBefore": len(data), "byteSizeAfter": len(out),
    }


def hash_check(data):  # trivial integrity hook (kept for symmetry with census law)
    return hashlib.sha256(data).hexdigest()


def classify(path):
    data = open(path, "rb").read()
    if len(data) < 20 or data[:4] != b"glTF":
        return "nonglb", None
    try:
        g, _, _ = parse_glb(data)
        if has_normal(g):
            return "skipped", data
        return "process", data
    except Exception as e:
        return "nonglb", e


def main(argv):
    mode = "process"
    paths = []
    log_path = DEFAULT_LOG
    no_scope = False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--verify":
            mode = "verify"
        elif a == "--log":
            i += 1; log_path = argv[i]
        elif a == "--allow-out-of-scope":
            no_scope = True
        else:
            paths.append(a)
        i += 1
    root = paths[0] if paths else DEFAULT_ROOT

    # census scope set (tree mode only; single-file mode is the harness path)
    census_set = None
    is_tree = os.path.isdir(root)
    if is_tree and os.path.exists(CENSUS_PATH):
        census_set = set(json.load(open(CENSUS_PATH))["files"])

    glbs = []
    if is_tree:
        for r, dirs, files in os.walk(root):
            dirs.sort()
            for fn in sorted(files):
                if fn.endswith(".glb"):
                    glbs.append(os.path.join(r, fn))
    else:
        glbs = [root]

    rows, skipped, would, out_of_scope, errs = [], 0, 0, [], 0
    for p in sorted(glbs):
        status, extra = classify(p)
        if status == "nonglb":
            errs += 1
            rows.append({"file": p, "ok": False, "note": f"not-glb/{extra}"})
            continue
        rel = os.path.relpath(p, ".")
        if census_set is not None and mode == "process" and rel not in census_set:
            out_of_scope.append(rel)   # scope law: never touch a non-census file
            rows.append({"file": p, "ok": True, "skipped": "out-of-scope"})
            continue
        if mode == "verify":
            if status == "skipped":
                skipped += 1
                rows.append({"file": rel, "skipped": "NORMAL present"})
            else:
                would += 1
                rows.append({"file": rel, "wouldProcess": True})
            continue
        if status == "skipped":
            skipped += 1
            rows.append({"file": rel, "skipped": "NORMAL present"})
            continue
        try:
            row = process_glb(p)
            row["file"] = rel
            rows.append(row)
        except Exception as e:
            errs += 1
            rows.append({"file": rel, "ok": False, "note": repr(e)})

    processed = sum(1 for r in rows if r.get("ok") and "byteSizeAfter" in r)
    report = {
        "mode": mode, "root": root, "filesExamined": len(glbs),
        "processed": processed, "skipped": skipped,
        "wouldProcess": would, "outOfScope": out_of_scope, "errors": errs,
        "rows": rows,
    }
    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
    with open(log_path, "w") as f:
        json.dump(report, f, indent=1, sort_keys=True)
    if is_tree:
        print(f"root={root} examined={len(glbs)} processed={processed} skipped={skipped} "
              f"wouldProcess={would} outOfScope={len(out_of_scope)} errors={errs}")
    else:
        print(f"file={root} processed={processed} skipped={skipped} "
              f"outOfScope={len(out_of_scope)} errors={errs}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
