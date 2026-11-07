#!/usr/bin/env python3
"""CC-H5b GLB width measurement v3 — numpy, per-VERTEX world transform.

v2 walked node transforms over accessor AABB corners (Box3.setFromObject
equivalent). v3 transforms EVERY vertex to world space (trimesh-scene /
exact-geometry equivalent) - both bounds conventions, one tool. Disagreement
between v2 (AABB-of-OBB) and v3 (exact vertices) would say the models carry
only axis-aligned parts.
"""
import json
import struct

import numpy as np


def glb_json(path):
    with open(path, "rb") as f:
        magic, ver, length = struct.unpack("<III", f.read(12))
        clen, ctype = struct.unpack("<II", f.read(8))
        assert ctype == 0x4E4F534A, hex(ctype)
        data = f.read(clen)
        return json.loads(data.decode("utf-8", errors="replace"))


def read_accessor(acc, views, bins, idx):
    a = acc[idx]
    v = views[a["bufferView"]]
    off = v.get("byteOffset", 0) + a.get("byteOffset", 0)
    n, comp = a["count"], {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[a["type"]]
    fmt = {5126: "f4", 5125: "u4", 5123: "u2", 5121: "u1", 5122: "i2", 5120: "i1", 5124: "i4"}
    arr = np.frombuffer(bins[v.get("buffer", 0)], dtype=fmt[a["componentType"]],
                        count=n * comp, offset=off)
    return arr.reshape(n, comp)


def compose(n, base):
    m = base.copy()
    if "matrix" in n:
        cm = np.array(n["matrix"], dtype=np.float64).reshape(4, 4).T  # col->row
        m = m @ cm
    if "translation" in n:
        t = np.eye(4)
        t[:3, 3] = n["translation"]
        m = m @ t
    if "rotation" in n:
        x, y, z, w = n["rotation"]
        r = np.eye(4)
        r[:3, :3] = np.array([
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ])
        m = m @ r
    if "scale" in n:
        s = np.diag(list(n["scale"]) + [1.0])
        m = m @ s
    return m


def measure(path, g=None):
    if g is None:
        g = glb_json(path)
    bin_chunk = bytes(g["_bin"])
    acc, nodes, scenes = g["accessors"], g["nodes"], g["scenes"]
    pts = []

    def walk(idx, base):
        n = nodes[idx]
        m = compose(n, base)
        if "mesh" in n:
            for p in g["meshes"][n["mesh"]].get("primitives", []):
                pa = p.get("attributes", {}).get("POSITION")
                if pa is None:
                    continue
                arr = read_accessor(acc, g["bufferViews"] if "bufferViews" in g
                                    else g.get("views", []), bin_chunk, pa)[:, :3]
                w = (np.column_stack([arr, np.ones(len(arr))]) @ m.T)[:, :3]
                pts.append(w)
        for c in n.get("children", []):
            walk(c, m)

    for sc in scenes:
        for r in sc["nodes"]:
            walk(r, np.eye(4))
    P = np.vstack(pts)
    return P[:, 0].max() - P[:, 0].min(), P[:, 1].max() - P[:, 1].min()


def glb_with_bin(path):
    with open(path, "rb") as f:
        magic, ver, length = struct.unpack("<III", f.read(12))
        clen, ctype = struct.unpack("<II", f.read(8))
        js = json.loads(f.read(clen).decode("utf-8", errors="replace"))
        rest = length - 12 - 8 - clen
        blen, btype = struct.unpack("<II", f.read(8))
        js["_bin"] = f.read(blen)
    return js


for name, p in [
    ("mourningStatue", "/tmp/wh-worldfeat/art-direction/3d/assets/biome_library/m3-pixelated.glb"),
    ("okRuinColumn", "/tmp/wh-worldfeat/art-direction/3d/assets/old_king/ok-ruin-column-pixelated.glb"),
    ("stoneSteps", "/tmp/wh-worldfeat/art-direction/3d/assets/crypt/stone-steps-pixelated.glb"),
    ("skullPile", "/tmp/wh-worldfeat/art-direction/3d/assets/crypt/skull-pile-pixelated.glb"),
]:
    try:
        g = glb_with_bin(p)
        g["bufferViews"] = g.get("bufferViews", g.get("views", []))
        measure.__globals__["glb_json"] = lambda pp: g  # reuse path
        w, h = measure(p)
        print("%s  exact-vertex width %.3f  height %.3f  (half %.3f)" % (name, w, h, w / 2))
    except Exception as e:
        import traceback
        print(name, "ERR", type(e).__name__, e)
