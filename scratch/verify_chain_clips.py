#!/usr/bin/env python3
"""Round-trip QA for human-hunter-male.combat-chain.glb (plain python: struct/json
GLB parse + numpy forward kinematics; no Blender, no browser).

    python3 scratch/verify_chain_clips.py ORIGINAL.rigged.glb COMBAT_CHAIN.glb

Checks: 9 animations (6 originals + 3 chain clips), 20 skin joints, bone rest
TRS + inverse binds unchanged, original 6 clips unchanged (keys resampled at
the original times), images byte-identical, Root never moves in the new
clips. Prints R_Hand socket position + blade (hand-local +Z, the weapon tip
axis used by player.js setWeapon) at every phase key of the new clips, in
glTF/game model space: +Z = forward, -X = character's right, +Y = up.
"""
import hashlib
import json
import struct
import sys

import numpy as np

NEW = {"WH_SlashR2L": (0.14, 0.20, 0.30), "WH_SlashL2R": (0.14, 0.20, 0.30),
       "WH_Thrust": (0.16, 0.14, 0.40)}
ORIG = ["WH_Attack1", "WH_Death", "WH_Hit", "WH_Idle", "WH_Run", "WH_Walk"]
CT = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}
fails = []


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        fails.append(msg)


def load(p):
    b = open(p, "rb").read()
    assert b[:4] == b"glTF"
    off, js, bn = 12, None, None
    while off < len(b):
        ln, ty = struct.unpack_from("<II", b, off)
        off += 8
        if ty == 0x4E4F534A:
            js = json.loads(b[off:off + ln])
        elif ty == 0x004E4942:
            bn = b[off:off + ln]
        off += ln
    return js, bn


def acc(js, bn, i):
    a = js["accessors"][i]
    bv = js["bufferViews"][a["bufferView"]]
    n, dt = NC[a["type"]], np.dtype(CT[a["componentType"]])
    start = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    stride = bv.get("byteStride", 0)
    if stride and stride != n * dt.itemsize:
        return np.array([np.frombuffer(bn, dt, n, start + k * stride) for k in range(a["count"])])
    return np.frombuffer(bn, dt, a["count"] * n, start).reshape(a["count"], n)


def qmat(q):
    x, y, z, w = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


class Rig:
    def __init__(self, path):
        self.js, self.bn = load(path)
        self.nodes = self.js["nodes"]
        self.parent = {c: i for i, n in enumerate(self.nodes) for c in n.get("children", [])}
        self.idx = {n.get("name"): i for i, n in enumerate(self.nodes)}
        self.anims = {}
        for an in self.js.get("animations", []):
            d = {}
            for ch in an["channels"]:
                sm = an["samplers"][ch["sampler"]]
                d[(ch["target"]["node"], ch["target"]["path"])] = (
                    acc(self.js, self.bn, sm["input"]).ravel(), acc(self.js, self.bn, sm["output"]),
                    sm.get("interpolation", "LINEAR"))
            self.anims[an["name"]] = d

    def channel(self, anim, i, path, t):
        ti, vo, _ = self.anims[anim][(i, path)]
        v = np.array([np.interp(t, ti, vo[:, c]) for c in range(vo.shape[1])])
        return v / np.linalg.norm(v) if path == "rotation" else v

    def local(self, i, anim=None, t=0.0):
        n = self.nodes[i]
        T = np.array(n.get("translation", [0, 0, 0]), float)
        R = np.array(n.get("rotation", [0, 0, 0, 1]), float)
        S = np.array(n.get("scale", [1, 1, 1]), float)
        if anim:
            if (i, "translation") in self.anims[anim]:
                T = self.channel(anim, i, "translation", t)
            if (i, "rotation") in self.anims[anim]:
                R = self.channel(anim, i, "rotation", t)
            if (i, "scale") in self.anims[anim]:
                S = self.channel(anim, i, "scale", t)
        M = np.eye(4)
        M[:3, :3] = qmat(R) * S[None, :]
        M[:3, 3] = T
        return M

    def world(self, name, anim=None, t=0.0):
        i, M = self.idx[name], np.eye(4)
        while i is not None:
            M = self.local(i, anim, t) @ M
            i = self.parent.get(i)
        return M

    def duration(self, anim):
        return max(v[0][-1] for v in self.anims[anim].values())

    def images(self):
        out = []
        for im in self.js.get("images", []):
            bv = self.js["bufferViews"][im["bufferView"]]
            o = bv.get("byteOffset", 0)
            out.append((im.get("name"), im.get("mimeType"),
                        hashlib.sha256(self.bn[o:o + bv["byteLength"]]).hexdigest()))
        return out


def main(orig_path, new_path):
    A, B = Rig(orig_path), Rig(new_path)
    names = sorted(B.anims)
    print("animations:", names)
    check(all(n in B.anims for n in ORIG), "original 6 clips present")
    check(all(n in B.anims for n in NEW), "3 chain clips present")
    check(len(B.anims) == 9, f"animation count 9 (got {len(B.anims)})")
    joints = [B.nodes[j]["name"] for j in B.js["skins"][0]["joints"]]
    check(len(joints) == 20, f"skin joints 20 (got {len(joints)})")
    check(joints == [A.nodes[j]["name"] for j in A.js["skins"][0]["joints"]], "joint order unchanged")
    check(len(B.js["meshes"]) == 1 and B.idx.get("WH_Body") is not None, "single mesh node WH_Body")
    # rest frames / inverse binds (the R_Hand weapon socket basis)
    worst = 0.0
    for n in joints:
        a, b = A.nodes[A.idx[n]], B.nodes[B.idx[n]]
        for f, d in (("translation", [0, 0, 0]), ("rotation", [0, 0, 0, 1]), ("scale", [1, 1, 1])):
            x, y = np.array(a.get(f, d)), np.array(b.get(f, d))
            if f == "rotation" and np.dot(x, y) < 0:
                y = -y
            worst = max(worst, np.abs(x - y).max())
    check(worst < 1e-4, f"bone rest TRS unchanged (max diff {worst:.2e})")
    ia = acc(A.js, A.bn, A.js["skins"][0]["inverseBindMatrices"])
    ib = acc(B.js, B.bn, B.js["skins"][0]["inverseBindMatrices"])
    check(np.abs(ia - ib).max() < 1e-4, f"inverse bind matrices unchanged (max diff {np.abs(ia - ib).max():.2e})")
    check(A.images() == B.images(), f"embedded images byte-identical {[(n, m, h[:12]) for n, m, h in B.images()]}")
    check([m.get("name") for m in A.js["materials"]] == [m.get("name") for m in B.js["materials"]],
          "material names unchanged")
    # original clips: sample the new file at the original key times
    for clip in ORIG:
        worst, dur_a, dur_b = 0.0, A.duration(clip), B.duration(clip)
        for (i, path), (ti, vo, _) in A.anims[clip].items():
            j = B.idx[A.nodes[i]["name"]]
            vs = np.array([B.channel(clip, j, path, t) for t in ti])
            if path == "rotation":
                vs *= np.sign(np.sum(vs * vo, axis=1))[:, None]
            worst = max(worst, np.abs(vs - vo).max())
        check(worst < 1e-4 and abs(dur_a - dur_b) < 1e-4,
              f"{clip} unchanged ({len(A.anims[clip])} ch, {dur_b:.4f}s, max diff {worst:.1e})")
    # new clips
    root = B.idx["Root"]
    for clip, (w, s, r) in NEW.items():
        an = B.anims[clip]
        L = B.duration(clip)
        times = sorted(set(np.round(np.concatenate([v[0] for v in an.values()]), 5)))
        check(len(an) == 60, f"{clip}: 60 channels (T/R/S x 20 bones) (got {len(an)})")
        check(set(v[2] for v in an.values()) == {"LINEAR"}, f"{clip}: LINEAR baked")
        rt = an[(root, "translation")][1]
        rr = an[(root, "rotation")][1]
        check(np.abs(rt - rt[0]).max() < 1e-6 and np.abs(rr - rr[0]).max() < 1e-6,
              f"{clip}: Root static (no root motion)")
        T = w + s + r
        b1, b2 = L * w / T, L * (w + s) / T
        print(f"{clip}: {L:.4f}s, {len(times)} keys, windup [0,{b1:.4f}) strike [{b1:.4f},{b2:.4f}) "
              f"recover [{b2:.4f},{L:.4f}] (strike {100 * s / T:.0f}%)")
        marks = [("first", 0.0), ("windup end", b1), ("mid strike", 0.5 * (b1 + b2)),
                 ("strike end", b2), ("last", L)]
        rows = {}
        for label, t in marks:
            M = B.world("R_Hand", clip, t)
            rows[label] = (M[:3, 3], M[:3, 2])
            print(f"   {label:11s} t={t:.4f}  R_Hand pos {np.round(M[:3, 3], 3)}  blade {np.round(M[:3, 2], 3)}")
        # sweep sanity in model space (+Z forward, -X right)
        hw, he = rows["windup end"][0], rows["strike end"][0]
        if clip == "WH_SlashR2L":
            check(hw[0] < -0.3 and he[0] > 0.2, f"{clip}: hand sweeps right->left (x {hw[0]:.2f} -> {he[0]:.2f})")
            check(hw[1] > 0.6, f"{clip}: windup raised (hand y {hw[1]:.2f})")
        elif clip == "WH_SlashL2R":
            check(hw[0] > 0.1 and he[0] < -0.3, f"{clip}: hand sweeps left->right (x {hw[0]:.2f} -> {he[0]:.2f})")
            check(he[1] - hw[1] > 0.4, f"{clip}: rising diagonal (hand y {hw[1]:.2f} -> {he[1]:.2f})")
        else:
            check(hw[2] < 0 and he[2] > 0.5, f"{clip}: chamber behind -> extends forward (z {hw[2]:.2f} -> {he[2]:.2f})")
            check(rows["strike end"][1][2] > 0.9, f"{clip}: blade points forward at full extension "
                                                   f"(blade z {rows['strike end'][1][2]:.2f})")
        p0, p1 = rows["first"][0], rows["last"][0]
        check(np.abs(p0 - p1).max() < 1e-3, f"{clip}: starts and ends in guard")
    print("VERIFY PASS" if not fails else f"VERIFY FAILED ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
