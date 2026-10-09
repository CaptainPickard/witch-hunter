#!/usr/bin/env python3
"""Round-trip + motion QA for human-hunter-male.combat-dagger.glb (adapted from
scratch/verify_chain_clips.py; plain python: struct/json GLB parse + numpy FK
and linear-blend skinning; no Blender, no browser).

    python3 scratch/verify_dagger_clips.py ORIGINAL.rigged.glb COMBAT_DAGGER.glb [--json OUT]

Checks: STRUCTURE identical to the source (node names + hierarchy, mesh /
primitive attributes / vertex + index data, skin joints, materials, images)
with ONLY the 3 dagger clips added; round-trip law < 1e-5 (bone rest TRS,
inverse binds, the 6 original clips resampled at their own key times); new
clips 60 LINEAR channels, Root static, durations within 5 % of spec, start and
end in guard; NO GROUND PENETRATION (every WH_Body vertex skinned at every
1/24 s + phase boundary of every new clip, plus the 0.35 m dagger tip, must
stay at or above the ground y = -1); WRIST SWEEP sanity (side-to-side
direction, amplitude, monotone through the strike, blade near-horizontal,
hand below the shoulder = no big shoulder swings). Model space: +Z forward,
-X = character's right, +Y up.
"""
import hashlib
import json
import struct
import sys

import numpy as np

NEW = {"WH_DagSlashR2L": (0.10, 0.12, 0.16), "WH_DagSlashL2R": (0.10, 0.12, 0.16),
       "WH_DagSlashR2Lb": (0.10, 0.12, 0.48)}
SWEEP = {"WH_DagSlashR2L": +1, "WH_DagSlashL2R": -1, "WH_DagSlashR2Lb": +1}   # sign of hand dx (model +X = char left)
GROUND_Y = -1.0
DAGGER_LEN = 0.35   # dagger_measure.json weaponTargetHeight (armature units, body-local)
RT_LAW = 1e-5
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


def lbs_setup(R):
    pr = R.js["meshes"][0]["primitives"][0]
    P = acc(R.js, R.bn, pr["attributes"]["POSITION"]).astype(float)
    J = acc(R.js, R.bn, pr["attributes"]["JOINTS_0"]).astype(int)
    a = R.js["accessors"][pr["attributes"]["WEIGHTS_0"]]
    W = acc(R.js, R.bn, pr["attributes"]["WEIGHTS_0"]).astype(float)
    if a["componentType"] == 5121:
        W /= 255.0
    elif a["componentType"] == 5123:
        W /= 65535.0
    W /= W.sum(1, keepdims=True)
    ibm = acc(R.js, R.bn, R.js["skins"][0]["inverseBindMatrices"]).reshape(-1, 4, 4).transpose(0, 2, 1)
    names = [R.nodes[j]["name"] for j in R.js["skins"][0]["joints"]]
    return P, J, W, ibm, names


def skin_min_y(R, S, anim, t):
    P, J, W, ibm, names = S
    M = np.array([R.world(n, anim, t) @ ibm[k] for k, n in enumerate(names)])   # (20,4,4)
    Ph = np.c_[P, np.ones(len(P))]
    out = np.zeros(len(P))
    for c in range(J.shape[1]):
        Mv = np.einsum("nij,nj->ni", M[J[:, c]], Ph)
        out += W[:, c] * Mv[:, 1]
    return out.min()


def struct_sig(R):
    nodes = sorted((n.get("name"), R.nodes[R.parent[i]].get("name") if i in R.parent else None,
                    "mesh" in n, "skin" in n) for i, n in enumerate(R.nodes))
    prims = [(sorted(p["attributes"]), R.js["accessors"][p["attributes"]["POSITION"]]["count"],
              R.js["accessors"][p["indices"]]["count"]) for m in R.js["meshes"] for p in m["primitives"]]
    return nodes, prims, len(R.js.get("skins", [])), len(R.js["meshes"])


def main(orig_path, new_path, out_json=None):
    A, B = Rig(orig_path), Rig(new_path)
    rep = {"round_trip": {}, "clips": {}}
    names = sorted(B.anims)
    print("animations:", names)
    check(sorted(B.anims) == sorted(ORIG + list(NEW)), f"exactly 6 originals + 3 dagger clips (got {len(B.anims)})")
    # ---- structure identity
    sa, sb = struct_sig(A), struct_sig(B)
    check(sa[0] == sb[0], f"node names + hierarchy identical ({len(sb[0])} nodes)")
    check(sa[1] == sb[1], f"mesh primitives identical (attrs/vert/index counts {sb[1]})")
    check(sa[2:] == sb[2:], f"skin count {sb[2]}, mesh count {sb[3]} identical")
    joints = [B.nodes[j]["name"] for j in B.js["skins"][0]["joints"]]
    check(joints == [A.nodes[j]["name"] for j in A.js["skins"][0]["joints"]] and len(joints) == 20,
          f"skin joints identical, order unchanged ({len(joints)})")
    pa, pb_ = A.js["meshes"][0]["primitives"][0], B.js["meshes"][0]["primitives"][0]
    vdiff = {}
    for k in sorted(pa["attributes"]):
        x = acc(A.js, A.bn, pa["attributes"][k]).astype(float)
        y = acc(B.js, B.bn, pb_["attributes"][k]).astype(float)
        vdiff[k] = float(np.abs(x - y).max())
    ia_, ib_ = acc(A.js, A.bn, pa["indices"]), acc(B.js, B.bn, pb_["indices"])
    vdiff["indices"] = float(np.abs(ia_.astype(int) - ib_.astype(int)).max())
    check(max(vdiff.values()) < RT_LAW, f"vertex/index data identical (max diff per attr { {k: f'{v:.1e}' for k, v in vdiff.items()} })")
    rep["round_trip"]["vertex_data_max_diff"] = vdiff
    check(A.images() == B.images(), f"embedded images byte-identical {[(n, m, h[:12]) for n, m, h in B.images()]}")
    check([m.get("name") for m in A.js["materials"]] == [m.get("name") for m in B.js["materials"]],
          "material names unchanged")
    # ---- round-trip law: rest frames / inverse binds (R_Hand weapon socket basis)
    worst = 0.0
    for n in joints:
        a, b = A.nodes[A.idx[n]], B.nodes[B.idx[n]]
        for f, d in (("translation", [0, 0, 0]), ("rotation", [0, 0, 0, 1]), ("scale", [1, 1, 1])):
            x, y = np.array(a.get(f, d)), np.array(b.get(f, d))
            if f == "rotation" and np.dot(x, y) < 0:
                y = -y
            worst = max(worst, np.abs(x - y).max())
    check(worst < RT_LAW, f"bone rest TRS round-trip (max diff {worst:.2e} < {RT_LAW:.0e})")
    rh = np.abs(A.world("R_Hand") - B.world("R_Hand")).max()
    check(rh < RT_LAW, f"R_Hand socket rest basis untouched (max diff {rh:.2e})")
    ia = acc(A.js, A.bn, A.js["skins"][0]["inverseBindMatrices"])
    ib = acc(B.js, B.bn, B.js["skins"][0]["inverseBindMatrices"])
    check(np.abs(ia - ib).max() < RT_LAW, f"inverse bind matrices round-trip (max diff {np.abs(ia - ib).max():.2e})")
    rep["round_trip"].update({"rest_trs": worst, "r_hand_socket": float(rh), "ibm": float(np.abs(ia - ib).max())})
    for clip in ORIG:
        worst, dur_a, dur_b = 0.0, A.duration(clip), B.duration(clip)
        for (i, path), (ti, vo, _) in A.anims[clip].items():
            j = B.idx[A.nodes[i]["name"]]
            vs = np.array([B.channel(clip, j, path, t) for t in ti])
            if path == "rotation":
                vs *= np.sign(np.sum(vs * vo, axis=1))[:, None]
            worst = max(worst, np.abs(vs - vo).max())
        check(worst < RT_LAW and abs(dur_a - dur_b) < RT_LAW,
              f"{clip} round-trip ({len(A.anims[clip])} ch, {dur_b:.4f}s, max diff {worst:.1e})")
        rep["round_trip"][clip] = float(worst)
    # ---- new clips
    S = lbs_setup(B)
    bind_min = skin_min_y(B, S, None, 0.0)
    idle_min = skin_min_y(B, S, "WH_Idle", 0.0)
    print(f"ground ref: bind-pose min vertex y {bind_min:.4f}, WH_Idle t0 min y {idle_min:.4f}, ground {GROUND_Y}")
    rep["ground_ref"] = {"bind_min_y": bind_min, "idle_t0_min_y": idle_min}
    root = B.idx["Root"]
    sh = B.world("R_UpperArm")[1, 3]
    for clip, (w, s, r) in NEW.items():
        an = B.anims[clip]
        L = B.duration(clip)
        T = w + s + r
        cr = {"duration_s": round(L, 4), "spec_s": T, "duration_err_pct": round(100 * (L - T) / T, 3)}
        times = sorted(set(np.round(np.concatenate([v[0] for v in an.values()]), 5)))
        check(len(an) == 60, f"{clip}: 60 channels (T/R/S x 20 bones) (got {len(an)})")
        check(set(v[2] for v in an.values()) == {"LINEAR"}, f"{clip}: LINEAR baked")
        rt = an[(root, "translation")][1]
        rr = an[(root, "rotation")][1]
        check(np.abs(rt - rt[0]).max() < 1e-6 and np.abs(rr - rr[0]).max() < 1e-6,
              f"{clip}: Root static (no root motion)")
        check(abs(L - T) / T <= 0.05, f"{clip}: duration {L:.4f}s vs spec {T:.2f}s ({cr['duration_err_pct']:+.2f} %, law 5 %)")
        b1, b2 = w, w + s
        print(f"{clip}: {L:.4f}s, {len(times)} keys, windup [0,{b1:.4f}) strike [{b1:.4f},{b2:.4f}) "
              f"recover [{b2:.4f},{L:.4f}] (strike {100 * s / T:.0f}%)")
        marks = [("first", 0.0), ("windup end", b1), ("contact", b1 + 0.5 * s), ("strike end", b2), ("last", L)]
        rows = {}
        for label, t in marks:
            M = B.world("R_Hand", clip, t)
            rows[label] = (M[:3, 3], M[:3, 2])
            print(f"   {label:11s} t={t:.4f}  R_Hand pos {np.round(M[:3, 3], 3)}  blade {np.round(M[:3, 2], 3)}")
        # ground: every 1/24 s + boundaries, skinned body + dagger tip
        ts = sorted(set(list(np.arange(0.0, L + 1e-9, 1.0 / 24)) + [b1, b2, L] + list(times)))
        mins = [skin_min_y(B, S, clip, t) for t in ts]
        tips = []
        for t in ts:
            M = B.world("R_Hand", clip, t)
            tips.append((M[:3, 3] + DAGGER_LEN * M[:3, 2])[1])
        bm, tm_ = min(mins), min(tips)
        check(bm >= GROUND_Y - 1e-4, f"{clip}: no ground penetration - min skinned vertex y {bm:.4f} over {len(ts)} samples (ground {GROUND_Y})")
        check(tm_ > GROUND_Y, f"{clip}: dagger tip min y {tm_:.4f} > ground")
        cr.update({"ground_samples": len(ts), "min_vertex_y": round(bm, 5), "min_tip_y": round(tm_, 4)})
        # wrist sweep sanity
        xs = [B.world("R_Hand", clip, t)[0, 3] for t in np.linspace(b1, b2, 13)]
        dx = rows["strike end"][0][0] - rows["windup end"][0][0]
        mono = all(SWEEP[clip] * (xs[k + 1] - xs[k]) >= -1e-4 for k in range(len(xs) - 1))
        blades = [rows[k][1] for k in ("windup end", "contact", "strike end")]
        yaw = np.degrees(np.arccos(np.clip(np.dot(blades[0][[0, 2]] / np.linalg.norm(blades[0][[0, 2]]),
                                                    blades[2][[0, 2]] / np.linalg.norm(blades[2][[0, 2]])), -1, 1)))
        tilt = max(abs(float(np.degrees(np.arcsin(np.clip(b[1], -1, 1))))) for b in blades)
        hand_y = max(B.world("R_Hand", clip, t)[1, 3] for t in ts)
        check(SWEEP[clip] * dx > 0, f"{clip}: hand sweeps {'right->left' if SWEEP[clip] > 0 else 'left->right'} (x {rows['windup end'][0][0]:.3f} -> {rows['strike end'][0][0]:.3f}, dx {dx:+.3f})")
        check(0.3 <= abs(dx) <= 0.8, f"{clip}: sweep amplitude |dx| {abs(dx):.3f} in [0.30, 0.80] (flat dagger arc, not a longsword swing)")
        check(mono, f"{clip}: hand x monotone through the strike (13 samples)")
        check(yaw >= 90, f"{clip}: blade yaw sweep {yaw:.1f} deg >= 90 (wrist-led arc)")
        check(tilt <= 25, f"{clip}: blade near-horizontal at windup/contact/strike end (max |pitch| {tilt:.1f} deg <= 25)")
        check(hand_y < sh, f"{clip}: hand stays below the shoulder (max hand y {hand_y:.3f} < shoulder {sh:.3f})")
        p0, p1 = rows["first"][0], rows["last"][0]
        check(np.abs(p0 - p1).max() < 1e-3, f"{clip}: starts and ends in guard (rest)")
        cr.update({"hand_dx": round(float(dx), 4), "blade_yaw_deg": round(float(yaw), 1),
                   "blade_max_pitch_deg": round(tilt, 1), "max_hand_y": round(float(hand_y), 4),
                   "shoulder_y": round(float(sh), 4)})
        rep["clips"][clip] = cr
    # chain oscillation: R2L -> L2R -> R2Lb alternates sides
    sg = [np.sign(rep["clips"][c]["hand_dx"]) for c in NEW]
    check(sg == [1, -1, 1], f"chain wrist oscillation alternates sides (dx signs {sg})")
    rep["fails"] = fails
    if out_json:
        json.dump(rep, open(out_json, "w"), indent=1, default=float)
    print("VERIFY PASS" if not fails else f"VERIFY FAILED ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    a = sys.argv[1:]
    oj = a[a.index("--json") + 1] if "--json" in a else None
    sys.exit(main(a[0], a[1], oj))
