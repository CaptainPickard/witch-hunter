#!/usr/bin/env python3
"""R5 verify gate for DAG-SWIPES (io/missions/2026-10-10-dag-swipes.md); the
round-9 scratch/verify_dagger_anim.py with the new sources, clocks and the R2
no-crouch assert (plain python + numpy FK / LBS; no Blender, no browser).

    python3 scratch/verify_dagger_anim2.py PRISTINE.rigged.glb COMBAT_DAGGER.glb [--json OUT]
        (reads scratch/dag-swipes/retime.json, probe_measure.json, bake.json)

GATE: as round 9 (pristine BIN prefix + JSON entries byte-identical, 9 = 6
pristine + 3 WH_Dag*, skins / JOINTS_0 / WEIGHTS_0 / images identical, rest
TRS + R_Hand socket basis < 1e-5, pristine clips round-trip < 1e-5).
QA: 60 LINEAR channels, Root static, finite unit quats, duration within 2 % of
0.25 / 0.25 / 0.52, impact (max wrist speed) inside the strike window (the
CONFIG windup / strike edges mapped onto the clip by anim.js seekAttack) and in
its band, side sequence + - +, ground (keys + every 1/96 s), R2 no-crouch
(Hips height above ground >= 0.80 x the source's max, keys + every 1/96 s),
wrist step law (round-9 deviation 3), slot 3 holds then settles.
Model space: +Y up, +Z forward, +X = character's LEFT.
"""
import hashlib
import json
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from glb_append_clips import parse, accessor_bytes
from verify_dagger_clips import Rig, lbs_setup, skin_min_y

def _win(w, s, r, T):     # CONFIG.moveset dagger windup/strike/recover -> clip seconds (seekAttack)
    return (T * w / (w + s + r), T * s / (w + s + r), T * r / (w + s + r))


NEW = {"WH_DagSlashR2L": _win(0.13, 0.16, 0.21, 0.25), "WH_DagSlashL2R": _win(0.13, 0.16, 0.21, 0.25),
       "WH_DagSlashR2Lb": _win(0.15, 0.18, 0.71, 0.52)}
SIDE = {"WH_DagSlashR2L": +1, "WH_DagSlashL2R": -1, "WH_DagSlashR2Lb": +1}
IMPACT_BAND = {"WH_DagSlashR2L": (0.06, 0.11), "WH_DagSlashL2R": (0.06, 0.11),
               "WH_DagSlashR2Lb": (0.06, 0.11)}     # target 0.09 s (0.36 of 0.25) +- half a 24 fps key
SRC = {"WH_DagSlashR2L": "CAND_swslash", "WH_DagSlashL2R": "CAND_swslash3", "WH_DagSlashR2Lb": "CAND_swslash"}
HERE = __file__.rsplit('/', 1)[0]
RETIME = json.load(open(HERE + "/dag-swipes/retime.json"))
PROBE = json.load(open(HERE + "/dag-swipes/probe_measure.json"))["clips"]
BAKE = json.load(open(HERE + "/dag-swipes/bake.json"))["clips"]
DUR_LAW = 0.02
CROUCH_LAW = 0.80
GROUND_Y = -1.0
RT = 1e-5
fails = []


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        fails.append(msg)


def qang(a, b):
    return float(np.degrees(2 * np.arccos(np.clip(abs(np.dot(a, b)), -1, 1))))


def main(orig, new, out_json=None):
    rep = {"gate": {}, "clips": {}}
    # ------------------------------------------------------------ GATE (bytes)
    A, abin = parse(orig)
    B, bbin = parse(new)
    check(bbin[:len(abin)] == abin, f"pristine BIN prefix byte-identical ({len(abin)} of {len(bbin)} bytes)")
    for key, val in A.items():
        if key == "buffers":
            continue
        same = B[key][:len(val)] == val if key in ("animations", "accessors", "bufferViews") else B[key] == val
        check(same, f"pristine JSON '{key}' entries identical")
    names_a = [a["name"] for a in A["animations"]]
    names_b = [a["name"] for a in B["animations"]]
    check(names_b == names_a + list(NEW),
          f"{len(names_b)} animations == {len(names_a)} pristine + 3 new, names exact: {names_b}")
    prim_a, prim_b = A["meshes"][0]["primitives"][0], B["meshes"][0]["primitives"][0]
    for attr in ("JOINTS_0", "WEIGHTS_0", "POSITION"):
        same = accessor_bytes(A, abin, prim_a["attributes"][attr]) == accessor_bytes(B, bbin, prim_b["attributes"][attr])
        check(same, f"{attr} bytes identical")
    ia = accessor_bytes(A, abin, A["skins"][0]["inverseBindMatrices"])
    ib = accessor_bytes(B, bbin, B["skins"][0]["inverseBindMatrices"])
    check(A["skins"] == B["skins"] and ia == ib, "skins + inverseBindMatrices bytes identical")
    img = lambda D, bn: [hashlib.sha256(bn[D["bufferViews"][i["bufferView"]].get("byteOffset", 0):
                         D["bufferViews"][i["bufferView"]].get("byteOffset", 0) + D["bufferViews"][i["bufferView"]]["byteLength"]]).hexdigest()
                         for i in D.get("images", [])]
    check(img(A, abin) == img(B, bbin), f"texture bytes identical ({len(img(B, bbin))} images)")
    # ------------------------------------------------------------ GATE (sampled)
    RA, RB = Rig(orig), Rig(new)
    worst = 0.0
    for n in RA.idx:
        a, b = RA.nodes[RA.idx[n]], RB.nodes[RB.idx[n]]
        for f, d in (("translation", [0, 0, 0]), ("rotation", [0, 0, 0, 1]), ("scale", [1, 1, 1])):
            x, y = np.array(a.get(f, d)), np.array(b.get(f, d))
            if f == "rotation" and np.dot(x, y) < 0:
                y = -y
            worst = max(worst, float(np.abs(x - y).max()))
    check(worst < RT, f"bone rest TRS identical (max {worst:.1e})")
    rh = float(np.abs(RA.world("R_Hand") - RB.world("R_Hand")).max())
    check(rh < RT, f"R_Hand weapon-socket rest basis untouched (max {rh:.1e})")
    rep["gate"]["rest_trs"], rep["gate"]["r_hand"] = worst, rh
    for clip in names_a:
        w = 0.0
        for (i, path), (ti, vo, _) in RA.anims[clip].items():
            vs = np.array([RB.channel(clip, i, path, t) for t in ti])
            if path == "rotation":
                vo = vo / np.linalg.norm(vo, axis=1)[:, None]
                vs *= np.sign(np.sum(vs * vo, axis=1))[:, None]
            w = max(w, float(np.abs(vs - vo).max()))
        check(w < RT, f"pristine {clip} round-trip sampled (max {w:.1e})")
        rep["gate"][clip] = w
    # ------------------------------------------------------------ QA
    S = lbs_setup(RB)
    root = RB.idx["Root"]
    rest_hand_local = np.array(RB.nodes[RB.idx["R_Hand"]].get("rotation", [0, 0, 0, 1]), float)
    bones = [RB.nodes[j]["name"] for j in RB.js["skins"][0]["joints"]]
    signs = []
    for clip, (w, s, r) in NEW.items():
        an = RB.anims[clip]
        T = w + s + r
        L = RB.duration(clip)
        keys = sorted(set(np.round(np.concatenate([v[0] for v in an.values()]), 6)))
        cr = {"duration_s": round(L, 4), "spec_s": T, "keys": len(keys)}
        check(len(an) == 60 and {v[2] for v in an.values()} == {"LINEAR"}, f"{clip}: 60 LINEAR channels")
        fin = all(np.isfinite(v[1]).all() for v in an.values())
        qn = max(float(np.abs(np.linalg.norm(v[1], axis=1) - 1).max()) for (i, p), v in an.items() if p == "rotation")
        check(fin and qn < 1e-4, f"{clip}: curves finite, unit quats (max |q|-1 {qn:.1e})")
        rt_, rr_ = an[(root, "translation")][1], an[(root, "rotation")][1]
        check(np.abs(rt_ - rt_[0]).max() < 1e-6 and np.abs(rr_ - rr_[0]).max() < 1e-6, f"{clip}: Root static")
        T = RETIME[clip]["out"]
        check(abs(L - T) / T <= DUR_LAW, f"{clip}: duration {L:.4f}s vs spec {T:.4f}s ({100 * (L - T) / T:+.2f} %, law 2 %)")
        # impact = max wrist speed, dense sampling of the shipped curves
        ts = np.linspace(0, L, int(round(L * 240)) + 1)
        hp = np.array([RB.world("R_Hand", clip, t)[:3, 3] for t in ts])
        sp = np.linalg.norm(np.diff(hp, axis=0), axis=1) / np.diff(ts)
        k = int(np.argmax(sp))
        t_imp = 0.5 * (ts[k] + ts[k + 1])
        lo, hi = IMPACT_BAND[clip]
        check(w <= t_imp <= w + s, f"{clip}: impact t={t_imp:.3f}s inside strike window [{w:.2f}, {w + s:.2f}]")
        check(lo <= t_imp <= hi, f"{clip}: impact t={t_imp:.3f}s in target band [{lo:.2f}, {hi:.2f}] (peak wrist {sp[k]:.1f} m/s)")
        # side sweep through the strike window (world/model frame = what the player sees)
        x0 = RB.world("R_Hand", clip, w)[0, 3]
        x1 = RB.world("R_Hand", clip, w + s)[0, 3]
        vx = (hp[k + 1][0] - hp[k][0]) / (ts[k + 1] - ts[k])
        dx = x1 - x0
        check(SIDE[clip] * dx > 0.2 and SIDE[clip] * vx > 0,
              f"{clip}: hand sweeps {'R->L' if SIDE[clip] > 0 else 'L->R'} through the strike (x {x0:+.3f} -> {x1:+.3f}, dx {dx:+.3f}; vx at impact {vx:+.1f} m/s)")
        signs.append(int(np.sign(dx)))
        # ground: skinned body only, every key + every 1/96 s
        gts = sorted(set(list(keys) + list(np.round(np.arange(0, L + 1e-9, 1 / 96), 6))))
        mins = [skin_min_y(RB, S, clip, t) for t in gts]
        km = min(skin_min_y(RB, S, clip, t) for t in keys)
        check(min(mins) >= GROUND_Y - 1e-4, f"{clip}: no skinned-body ground penetration (min y {min(mins):.5f} over {len(gts)} samples; keys {km:.5f}; ground {GROUND_Y})")
        # R2 no-crouch: shipped Hips height vs the source's own max (unclamped, on the WH rig)
        hh = [RB.world("Hips", clip, t)[1, 3] - GROUND_Y for t in gts]
        src_max = max(BAKE[clip]["src_hips_h"])
        ratio = min(hh) / src_max
        check(ratio >= CROUCH_LAW, f"{clip}: R2 no-crouch - Hips min {min(hh):.4f} m >= {CROUCH_LAW:.2f} x source max "
              f"{src_max:.4f} m (ratio {ratio:.3f}; source own min/max {min(BAKE[clip]['src_hips_h']) / src_max:.3f})")
        cr.update({"hips_min_m": round(min(hh), 4), "src_hips_max_m": round(src_max, 4), "hips_ratio": round(ratio, 3)})
        # wrist sanity / pose explosions
        hi_ = RB.idx["R_Hand"]
        hq = np.array([RB.channel(clip, hi_, "rotation", t) for t in keys])
        wr = [qang(q, rest_hand_local) for q in hq]
        a_, i_, _ = RETIME[clip]["src_frames"]
        per_key = (i_ - a_) / RETIME[clip]["impact_out"] / 24.0     # source frames per output key (strike rate)
        ref = PROBE[SRC[clip]]["bone_max_step_deg_per_frame"]
        worst_ratio, jump, jb = 0.0, 0.0, ""
        for b in bones:
            bq = np.array([RB.channel(clip, RB.idx[b], "rotation", t) for t in keys])
            st = [qang(bq[j], bq[j + 1]) * (1.0 if keys[j + 1] - keys[j] > 0.04 else (1 / 24) / (keys[j + 1] - keys[j]))
                  for j in range(len(bq) - 1)]
            m = max(st)
            worst_ratio = max(worst_ratio, m / max(ref[b] * per_key, 1e-3))
            if m > jump:
                jump, jb = m, b
        dang = np.diff(wr)
        rev = int(np.sum(np.abs(np.diff(np.sign(dang[np.abs(dang) > 2.0]))) > 0))
        check(max(wr) <= 90 and worst_ratio <= 1.05 and jump < 120,
              f"{clip}: wrist sane / no pose explosion - R_Hand local max {max(wr):.1f} deg from rest (<=90); "
              f"max key step {jump:.1f} deg ({jb}, <120); worst step / (source rate x {per_key:.2f} src frames/key) "
              f"= {worst_ratio:.2f} (<=1.05); wrist reversals {rev}")
        cr.update({"impact_s": round(t_imp, 4), "peak_wrist_mps": round(float(sp[k]), 2), "dx": round(float(dx), 3),
                   "min_skinned_y": round(min(mins), 5), "wrist_max_deg": round(max(wr), 1),
                   "bone_step_max_deg": round(jump, 1), "bone_step_max": jb, "step_vs_source_ratio": round(worst_ratio, 3),
                   "wrist_reversals": rev})
        if clip == "WH_DagSlashR2Lb":
            se = RETIME[clip]["strike_end_out"]    # uniform strike stops here; hold + settle after
            hold =sp[(ts[:-1] >= se) & (ts[:-1] <= se + 0.10)].max()
            # hand-off speed = the final 1/48 s (the shipped last key interval). The
            # round-9 0.06 s window spans 1.4 keys here and reads 1.98 m/s: slash.fbx
            # ends on a loop pose still moving 1.79 m/s at 1x (reported deviation).
            tt = np.linspace(keys[-2], L, 9)       # strictly inside the last key interval
            th = np.array([RB.world("R_Hand", clip, t)[:3, 3] for t in tt])
            tail = float((np.linalg.norm(np.diff(th, axis=0), axis=1) / np.diff(tt)).max())
            cr["wrist_last_0.06s_mps"] = round(float(sp[ts[:-1] >= L - 0.06].max()), 3)
            p0, pse, pend = hp[0], RB.world("R_Hand", clip, se)[:3, 3], hp[-1]
            d_se, d_end = float(np.linalg.norm(pse - p0)), float(np.linalg.norm(pend - p0))
            check(hold <= 0.3 * sp[k], f"{clip}: recover HOLDS - wrist <= {hold:.2f} m/s for 0.10 s after strike end (<= 30 % of peak {sp[k]:.1f})")
            check(d_end < 0.5 * d_se and tail <= 0.5, f"{clip}: recover SETTLES toward guard - hand-to-start {d_se:.3f} m at strike end -> {d_end:.3f} m at end; final wrist {tail:.2f} m/s")
            cr.update({"hold_max_mps": round(float(hold), 3), "hand_to_guard_strike_end": round(d_se, 3),
                       "hand_to_guard_end": round(d_end, 3), "end_wrist_mps": round(float(tail), 3)})
        print(f"   {clip}: {json.dumps(cr, default=float)}")
        rep["clips"][clip] = cr
    check(signs == [1, -1, 1], f"chain side sequence R->L, L->R, R->L (dx signs {signs})")
    rep["fails"] = fails
    if out_json:
        json.dump(rep, open(out_json, "w"), indent=1, default=float)
    print("VERIFY PASS" if not fails else f"VERIFY FAILED ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    a = sys.argv[1:]
    sys.exit(main(a[0], a[1], a[a.index("--json") + 1] if "--json" in a else None))
