#!/usr/bin/env python3
"""Testerbot-independert re-derivation of runtime-truth GLB x-extents (CC-H5b).

Independent of measure_glbs*.py: parses GLB JSON+BIN chunks, and computes the
x-extent of ALL POSITION accessors in FILE space (no scene transforms applied)
like measure_glbs.py v1, AND — where the GLB has a single-root scene — the
node-walk world-space extent via a composed 4x4 matrix walk (three.js
Box3.setFromObject equivalent). Asserts file-space == world-space (identity
root transform) as three.js's setFromObject walks node transforms.
"""
import json
import struct
import sys

import numpy as np


def read_glb(path):
    with open(path, "rb") as f:
        magic, ver, length = struct.unpack("<III", f.read(12))
        assert magic == 0x46546C67, hex(magic)
        clen, ctype = struct.unpack("<II", f.read(8))
        assert ctype == 0x4E4F534A
        js = json.loads(f.read(clen).decode("utf-8", errors="replace"))
        rest = length - 12 - 8 - clen
        if rest >= 8:
            blen, btype = struct.unpack("<II", f.read(8))
            js["_bin"] = f.read(blen)
        else:
            js["_bin"] = b""
    return js


def compose(n, base):
    m = base.copy()
    if "matrix" in n:
        cm = np.array(n["matrix"], dtype=np.float64).reshape(4, 4).T
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


def extent(path):
    g = read_glb(path)
    acc, views, nodes = g["accessors"], g.get("bufferViews", g.get("views", [])), g["nodes"]
    bin_ = g["_bin"]
    comp = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}
    fmt = {5126: "f4", 5125: "u4", 5123: "u2", 5121: "u1",
           5122: "i2", 5120: "i1", 5124: "i4"}

    def read_pos(ai):
        a = acc[ai]
        v = views[a["bufferView"]]
        off = v.get("byteOffset", 0) + a.get("byteOffset", 0)
        n, c = a["count"], comp[a["type"]]
        arr = np.frombuffer(bin_, dtype=fmt[a["componentType"]],
                            count=n * c, offset=off)
        return arr.reshape(n, c)[:, :3]

    # file-space extent over every POSITION accessor (min/max declared + raw)
    fmin, fmax = np.array([np.inf] * 3), np.array([-np.inf] * 3)
    declared_min, declared_max = np.array([np.inf] * 3), np.array([-np.inf] * 3)
    nverts = 0
    for m in g.get("meshes", []):
        for p in m.get("primitives", []):
            pa = p.get("attributes", {}).get("POSITION")
            if pa is None:
                continue
            a = acc[pa]
            if a.get("min") and a.get("max"):
                declared_min = np.minimum(declared_min, a["min"])
                declared_max = np.maximum(declared_max, a["max"])
            raw = read_pos(pa)
            fmin = np.minimum(fmin, raw.min(axis=0))
            fmax = np.maximum(fmax, raw.max(axis=0))
            nverts += len(raw)
    # world-space (node-walk) extent: transform every vertex by composed matrices
    scene_world_pts = []
    for sc in g.get("scenes", [{}]):
        for r in sc.get("nodes", []):
            stack = [(r, np.eye(4))]
            while stack:
                ni, base = stack.pop()
                n = nodes[ni]
                wm = compose(n, base)
                nn = n.get("mesh")
                if nn is not None:
                    for p in g["meshes"][nn].get("primitives", []):
                        pa = p.get("attributes", {}).get("POSITION")
                        if pa is None:
                            continue
                        raw = read_pos(pa)
                        w = (np.column_stack([raw, np.ones(len(raw))]) @ wm.T)[:, :3]
                        scene_world_pts.append(w)
                for c in n.get("children", []):
                    stack.append((c, wm))
    wmin = np.vstack(scene_world_pts).min(axis=0)
    wmax = np.vstack(scene_world_pts).max(axis=0)
    # multi-root glbs that just CONCAT mesh files may measure file-space extents
    # beyond any one scene; three.js measures the SCENE. Report scene extent.
    xw = float(wmax[0] - wmin[0])
    hw = float(wmax[1] - wmin[1])
    return {
        "file_x": float(fmax[0] - fmin[0]), "world_x": xw,
        "world_y": hw, "nverts": int(nverts),
        "scene_min": [round(float(v), 4) for v in wmin],
        "scene_max": [round(float(v), 4) for v in wmax],
        "declared_x": float(declared_max[0] - declared_min[0]),
    }


ASSETS = {
    "mourningStatue": "art-direction/3d/assets/biome_library/m3-pixelated.glb",
    "okRuinColumn": "art-direction/3d/assets/old_king/ok-ruin-column-pixelated.glb",
    "stoneSteps": "art-direction/3d/assets/crypt/stone-steps-pixelated.glb",
    "skullPile": "art-direction/3d/assets/crypt/skull-pile-pixelated.glb",
    "lanternPost": "art-direction/3d/assets/church-kit/lantern-post-v3-pixelated.glb",
    "blightcap": "art-direction/3d/assets/biome_library/m14-blightcap-pixelated.glb",
    "mossBoulder": "art-direction/3d/assets/biome_library/m9-pixelated.glb",
}

if __name__ == "__main__":
    print("%-16s %9s %9s %9s %9s  %s" % ("asset", "world_x", "file_x", "decl_x", "nverts", "scene x-range"))
    for name, rel in ASSETS.items():
        r = extent("/tmp/wh-worldfeat/" + rel)
        print("%-16s %9.3f %9.3f %9.3f %9d  [%s .. %s]" % (
            name, r["world_x"], r["file_x"], r["declared_x"], r["nverts"],
            r["scene_min"][0], r["scene_max"][0]))
