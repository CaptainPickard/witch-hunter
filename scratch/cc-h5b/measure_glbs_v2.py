#!/usr/bin/env python3
"""CC-H5b GLB width measurement v2 — Box3.setFromObject-equivalent (node transforms).

v1 (accessor-only, parent wake) ignored glTF node transforms; v2 composes each
node's world matrix and transforms the 8 AABB corners of every primitive's
POSITION min/max through it, mirroring THREE.Box3.setFromObject (AABB-of-OBB).
Output: X extent (width) and Y extent per asset, the numbers the runtime
colliderRadius() actually consumes.
"""
import json
import struct
import sys


def glb_json(path):
    with open(path, "rb") as f:
        magic, ver, length = struct.unpack("<III", f.read(12))
        clen, ctype = struct.unpack("<II", f.read(8))
        assert ctype == 0x4E4F534A, hex(ctype)
        data = f.read(clen)
        return json.loads(data.decode("utf-8", errors="replace"))


def mat_mul(a, b):
    return [sum(a[i * 4 + k] * b[k * 4 + j] for k in range(4)) for j in range(4) for i in range(4)]


def identity():
    return [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]


def compose(n, base):
    m = list(base)
    if "matrix" in n:  # column-major in glTF -> row-major here
        cm = n["matrix"]
        m = mat_mul(m, [cm[c * 4 + r] for c in range(4) for r in range(4)])
    t = n.get("translation")
    if t:
        m = mat_mul(m, [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, t[0], t[1], t[2], 1])
    r = n.get("rotation")  # xyzw quaternion
    if r:
        x, y, z, w = r
        rot = [
            1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w), 0,
            2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w), 0,
            2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y), 0,
            0, 0, 0, 1,
        ]
        m = mat_mul(m, rot)
    s = n.get("scale")
    if s:
        m = mat_mul(m, [s[0], 0, 0, 0, 0, s[1], 0, 0, 0, 0, s[2], 0, 0, 0, 0, 1])
    return m


def xform(m, x, y, z):
    return (m[0] * x + m[4] * y + m[8] * z + m[12],
            m[1] * x + m[5] * y + m[9] * z + m[13],
            m[2] * x + m[6] * y + m[10] * z + m[14])


def measure(path):
    g = glb_json(path)
    acc, nodes, scenes = g["accessors"], g["nodes"], g["scenes"]
    lo_x = hi_x = lo_y = hi_y = None

    def walk(idx, base):
        nonlocal lo_x, hi_x, lo_y, hi_y
        n = nodes[idx]
        m = compose(n, base)
        if "mesh" in n:
            for p in g["meshes"][n["mesh"]].get("primitives", []):
                pa = p.get("attributes", {}).get("POSITION")
                if pa is None:
                    continue
                a = acc[pa]
                if not (a.get("min") and a.get("max")):
                    continue
                for cx in (a["min"][0], a["max"][0]):
                    for cy in (a["min"][1], a["max"][1]):
                        for cz in (a["min"][2], a["max"][2]):
                            px, py, _ = xform(m, cx, cy, cz)
                            lo_x = px if lo_x is None else min(lo_x, px)
                            hi_x = px if hi_x is None else max(hi_x, px)
                            lo_y = py if lo_y is None else min(lo_y, py)
                            hi_y = py if hi_y is None else max(hi_y, py)
        for c in n.get("children", []):
            walk(c, m)

    root_nodes = []
    for sc in scenes:
        root_nodes.extend(sc["nodes"])
    for r in root_nodes:
        walk(r, identity())

    return ((hi_x - lo_x) if hi_x is not None else 0,
            (hi_y - lo_y) if hi_y is not None else 0)


for name, p in [
    ("mourningStatue",
     "/tmp/wh-worldfeat/art-direction/3d/assets/biome_library/m3-pixelated.glb"),
    ("okRuinColumn",
     "/tmp/wh-worldfeat/art-direction/3d/assets/old_king/ok-ruin-column-pixelated.glb"),
    ("stoneSteps",
     "/tmp/wh-worldfeat/art-direction/3d/assets/crypt/stone-steps-pixelated.glb"),
    ("skullPile",
     "/tmp/wh-worldfeat/art-direction/3d/assets/crypt/skull-pile-pixelated.glb"),
]:
    try:
        w, h = measure(p)
        print("%s  width %.3f  height %.3f  (half %.3f)" % (name, w, h, w / 2))
    except Exception as e:
        print(name, "ERR", type(e).__name__, e)
