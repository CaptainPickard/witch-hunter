"""
blender_dagger_clips.py -- dagger 3-chain flurry clips for the WH player rig
(Blender 4.5 headless, bpy). Adapted from scratch/blender_chain_clips.py (the
ASSET SOURCE OF TRUTH pattern: FK, arm solver, Hermite bake, NLA stash and
export settings are verbatim). ASSET SOURCE OF TRUTH for WH_DagSlashR2L /
WH_DagSlashL2R / WH_DagSlashR2Lb in human-hunter-male.combat-dagger.glb
(io/missions/2026-10-09-dagger.md, Phase A2).

    /opt/blender-4.5.4-linux-x64/blender --background --factory-startup \
        --python scratch/blender_dagger_clips.py -- IN.glb OUT.glb [--log OUT.json]
    # QA grids (no export; IN = the exported GLB, dagger-curved proxy on R_Hand
    # for framing only - preview mode never exports, so the proxy never ships):
    ... --python scratch/blender_dagger_clips.py -- IN.glb --preview DIR

IN is the combat-dagger COPY of human-hunter-male.rigged.glb (the original is
never opened for writing). Pipeline: glTF import -> author 3 actions (24 fps
baked, every bone keyed) -> stash each on its own muted NLA track next to the
6 imported WH_* tracks -> glTF export.

Dagger differences vs the chain script: clip lengths are the EXACT CONFIG
phase sums (0.38 / 0.38 / 0.70 s = 9.12 / 9.12 / 16.8 frames) - every integer
frame is baked plus the phase-boundary subframes and the fractional end key,
so the exported last key sits at the spec duration. Choreography is small:
torso yaw <= 12 deg, no hip drop (feet never sink), the arc is carried by the
forearm + wrist (blade direction leads the hand) and the elbow is pinned
bent at windup and extended at follow-through (wrist-led, elbow finish).

Export uses export_force_sampling=False: the imported WH_Attack1/Death/Hit/
Idle/Run/Walk are 30 fps LINEAR clips; re-sampling them at the 24 fps scene
rate shortened WH_Run (0.600 -> 0.583 s) and WH_Death. Unsampled export keeps
their keys exactly (round trip measured < 1e-5), and the new clips are
already baked on every frame here, so nothing is lost. Bone rest frames /
inverse binds also round-trip < 1e-5, so the R_Hand weapon socket basis
(CONFIG.assets.weaponMount) is untouched.

Conventions (same as tools/rigging/scripts/rig_wh_humanoid.py):
  Blender armature space: X = character's left, -Y = forward, Z = up.
  A pose is {bone: {rx, ry, rz (deg), lx, ly, lz (armature units)}}; the
  rotation q = Rz @ Ry @ Rx is about ARMATURE axes, applied at the bone head
  in the parent's posed frame (roll-independent). rz > 0 turns the chest to
  the character's LEFT (forward -Y swings toward +X).
  The weapon socket: game.js mounts the blade along R_Hand node-local +Z
  (player.js setWeapon), which is the Blender bone's local Z axis
  (verified against the GLB: rest blade = forward). The right-arm pose of
  every key is SOLVED (small Nelder-Mead over UpperArm/Forearm/Hand) to hit
  an authored hand position + blade direction, so the tip follows the arc.

Timing: clip key times sit at the CONFIG stage proportions (anim.js seeks
per-move clips proportionally to the move's windup/strike/recover):
  R2L / L2R 0.10/0.12/0.16 -> 0.38 s, windup ends 26.3 %, strike ends 57.9 %;
  R2Lb      0.10/0.12/0.48 -> 0.70 s, windup ends 14.3 %, strike ends 31.4 %;
            its 0.48 recover IS the pause: hold the follow-through, then
            settle back to the rest/guard pose the chain closes on.
Between keys: cubic Hermite per channel. Extreme keys (rest, windup,
follow-through, recover hold) have zero tangents = ease-in-out; the
mid-strike CONTACT key is a pass-through (Catmull-Rom tangent) so the blade
does not stop at contact. Every integer frame is baked plus the exact
phase-boundary subframes, all LINEAR (glTF has no Bezier).
Root is keyed at identity on every frame (no root motion).
"""
import bpy
import sys
import os
import math
import json
from mathutils import Vector, Quaternion, Matrix

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if not argv:
    raise SystemExit("usage: blender --background --python blender_chain_clips.py -- IN.glb OUT.glb [--log X.json] | IN.glb --preview DIR")
IN_PATH = os.path.abspath(argv[0])
opts = {}
rest = argv[1:]
OUT_PATH = None
if rest and not rest[0].startswith("--"):
    OUT_PATH = os.path.abspath(rest[0])
    rest = rest[1:]
for i in range(0, len(rest), 2):
    opts[rest[i].lstrip("-")] = rest[i + 1]

FPS = 24
BONES = ["Root", "Hips", "Spine", "Chest", "Neck", "Head",
         "L_Shoulder", "L_UpperArm", "L_Forearm", "L_Hand",
         "R_Shoulder", "R_UpperArm", "R_Forearm", "R_Hand",
         "L_Thigh", "L_Shin", "L_Foot", "R_Thigh", "R_Shin", "R_Foot"]
ORIGINAL_CLIPS = ["WH_Attack1", "WH_Death", "WH_Hit", "WH_Idle", "WH_Run", "WH_Walk"]


def log(*a):
    print("[DAG]", *a, flush=True)


# --------------------------------------------------------------------- import
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=IN_PATH)
scene = bpy.context.scene
scene.render.fps = FPS
arm = bpy.data.objects["WH_Armature"]
assert [b.name for b in arm.data.bones] and sorted(b.name for b in arm.data.bones) == sorted(BONES), \
    "unexpected skeleton"
assert arm.matrix_world == Matrix.Identity(4)
REST = {}
for b in arm.data.bones:
    REST[b.name] = {"head": b.head_local.copy(), "rot": b.matrix_local.to_quaternion(),
                    "parent": b.parent.name if b.parent else None}
BLADE_REST = REST["R_Hand"]["rot"] @ Vector((0, 0, 1))   # hand-local +Z = weapon tip


# --------------------------------------------------------------------- FK
def axis_quat(c):
    return (Quaternion((0, 0, 1), math.radians(c.get("rz", 0.0)))
            @ Quaternion((0, 1, 0), math.radians(c.get("ry", 0.0)))
            @ Quaternion((1, 0, 0), math.radians(c.get("rx", 0.0))))


def fk(pose, upto=None):
    """Deformation (Q, t) per bone: x -> Q x + t (armature space)."""
    D = {}
    for name in BONES:   # BONES is parent-before-child
        r = REST[name]
        c = pose.get(name, {})
        q = axis_quat(c)
        h = r["head"]
        d = Vector((c.get("lx", 0.0), c.get("ly", 0.0), c.get("lz", 0.0)))
        if r["parent"]:
            Qp, tp = D[r["parent"]]
        else:
            Qp, tp = Quaternion(), Vector()
        # D_b(x) = D_p(d + h + q (x - h))
        Q = Qp @ q
        t = Qp @ (d + h - q @ h) + tp
        D[name] = (Q, t)
        if name == upto:
            break
    return D


def hand_state(pose):
    D = fk(pose, upto="R_Hand")
    Qf, tf = D["R_Forearm"]
    pos = Qf @ REST["R_Hand"]["head"] + tf
    blade = D["R_Hand"][0] @ BLADE_REST
    return pos, blade


# --------------------------------------------------------------------- arm solver
ARM_KEYS = [("R_UpperArm", "rx"), ("R_UpperArm", "ry"), ("R_UpperArm", "rz"),
            ("R_Forearm", "rx"), ("R_Forearm", "ry"),
            ("R_Hand", "rx"), ("R_Hand", "ry"), ("R_Hand", "rz")]
ARM_BOUNDS = [(-200, 70), (-130, 90), (-95, 95),
              (-145, -4), (-25, 25),
              (-75, 75), (-75, 75), (-75, 75)]


def nelder_mead(f, x0, step=12.0, iters=2500, tol=1e-9):
    n = len(x0)
    pts = [list(x0)]
    for i in range(n):
        p = list(x0)
        p[i] += step
        pts.append(p)
    vals = [f(p) for p in pts]
    for _ in range(iters):
        order = sorted(range(n + 1), key=lambda k: vals[k])
        pts = [pts[k] for k in order]
        vals = [vals[k] for k in order]
        if abs(vals[-1] - vals[0]) < tol:
            break
        cen = [sum(p[i] for p in pts[:-1]) / n for i in range(n)]
        xr = [cen[i] + (cen[i] - pts[-1][i]) for i in range(n)]
        fr = f(xr)
        if fr < vals[0]:
            xe = [cen[i] + 2 * (cen[i] - pts[-1][i]) for i in range(n)]
            fe = f(xe)
            pts[-1], vals[-1] = (xe, fe) if fe < fr else (xr, fr)
        elif fr < vals[-2]:
            pts[-1], vals[-1] = xr, fr
        else:
            xc = [cen[i] + 0.5 * (pts[-1][i] - cen[i]) for i in range(n)]
            fc = f(xc)
            if fc < vals[-1]:
                pts[-1], vals[-1] = xc, fc
            else:
                for k in range(1, n + 1):
                    pts[k] = [pts[0][i] + 0.5 * (pts[k][i] - pts[0][i]) for i in range(n)]
                    vals[k] = f(pts[k])
    k = min(range(n + 1), key=lambda j: vals[j])
    return pts[k], vals[k]


def solve_arm(body, target_pos, target_blade, guess, elbow_w=0.0):
    """Fill R_UpperArm/R_Forearm/R_Hand of `body` so the R_Hand socket lands
    on target_pos with the blade along target_blade. guess = 8 floats (deg),
    also the regularization anchor (keeps the elbow/twist choice coherent).
    elbow_w > 0 pins the elbow (R_Forearm rx) toward guess[3] (thrust reach)."""
    tp = Vector(target_pos)
    tb = Vector(target_blade).normalized()

    def build(x):
        p = {k: dict(v) for k, v in body.items()}
        for (bn, ch), v in zip(ARM_KEYS, x):
            p.setdefault(bn, {})[ch] = v
        return p

    def cost(x):
        pos, blade = hand_state(build(x))
        c = 100.0 * (pos - tp).length_squared + 1.0 * (blade - tb).length_squared
        c += elbow_w * (x[3] - guess[3]) ** 2
        for v, g, (lo, hi), (bn, _) in zip(x, guess, ARM_BOUNDS, ARM_KEYS):
            c += 4e-6 * (v - g) ** 2
            if bn == "R_Hand":
                c += 1.5e-5 * v * v          # wrists prefer neutral
            if v < lo:
                c += 1e-3 * (lo - v) ** 2
            elif v > hi:
                c += 1e-3 * (v - hi) ** 2
        return c

    best = None
    for start_step in (12.0, 30.0):
        x, v = nelder_mead(cost, guess, step=start_step)
        x, v = nelder_mead(cost, x, step=4.0)
        if best is None or v < best[1]:
            best = (x, v)
    pose = build(best[0])
    pos, blade = hand_state(pose)
    err_p = (pos - tp).length
    err_b = math.degrees(blade.angle(tb))
    return pose, err_p, err_b


# --------------------------------------------------------------------- key poses
def twist(deg, lean=0.0, hips=0.0):
    """Torso yaw split Hips/Spine/Chest (+ forward lean rx)."""
    return {"Hips": {"rz": hips},
            "Spine": {"rz": 0.4 * deg, "rx": 0.4 * lean},
            "Chest": {"rz": 0.6 * deg, "rx": 0.6 * lean}}


def merge(*ps):
    out = {}
    for p in ps:
        for bn, c in p.items():
            out.setdefault(bn, {}).update(c)
    return out


def head_counter(p, k=0.5):
    """Head/neck counter-rotate the torso yaw so the eyes stay on target."""
    sp = p.get("Spine", {}).get("rz", 0.0) + p.get("Chest", {}).get("rz", 0.0) + p.get("Hips", {}).get("rz", 0.0)
    p.setdefault("Neck", {})["rz"] = -0.4 * k * sp
    p.setdefault("Head", {})["rz"] = -0.6 * k * sp
    return p


# Right-arm targets: (hand socket position, blade direction[, elbow pin]) in
# armature space. Reference: R shoulder joint (-0.242, 0.0, 0.555), arm reach
# ~0.55, rest hand (-0.415, -0.108, 0.042) with blade forward (0.06, -0.98, 0.18).
# Dagger plane: hand at belly/low-chest height (z 0.30-0.36), 0.25-0.46 in
# front; blade z-component kept small (flat cuts). Guess = 8 floats (deg),
# guess[3] = R_Forearm rx is the elbow pin target when the 3rd target slot set.
KEYS = {}
KEY_PHASES = {}   # filled from KEYS below (grid moments)

ELBOW_PIN = 2e-4         # same weight as the chain thrust reach pin


def ready(yaw, lean=4.0):
    """Light ready stance: small torso yaw, slight forward lean, knees soft
    (thigh fwd + shin back = foot lifts, never sinks; the foot counter-rotates
    the net thigh+shin pitch so the sole stays level - no toe dip), off hand
    tucked in a chest guard (elbow by the ribs, fist up)."""
    return merge(twist(yaw, lean=lean, hips=0.25 * yaw), {
        "L_UpperArm": {"rx": -14, "ry": -6}, "L_Forearm": {"rx": -105},
        "L_Thigh": {"rx": -6}, "L_Shin": {"rx": 9}, "L_Foot": {"rx": -3},
        "R_Thigh": {"rx": -4}, "R_Shin": {"rx": 7}, "R_Foot": {"rx": -3}})


# ---- WH_DagSlashR2L: wrist cocked out right -> flat cut across the belly -> elbow snaps out left
R2L_W = ready(-10)
R2L_C = ready(0, lean=6)
R2L_F = ready(12, lean=7)
T_R2L_W = ((-0.40, -0.26, 0.34), (-0.80, -0.58, 0.02), ELBOW_PIN)
T_R2L_C = ((-0.16, -0.44, 0.33), (0.10, -1.0, 0.02))
T_R2L_F = ((0.10, -0.42, 0.32), (0.90, -0.42, -0.04), ELBOW_PIN)
G_R2L_W = [-55, -35, -10, -95, 0, 0, 0, 0]
G_R2L_C = [-72, -5, 15, -55, 0, 0, 0, 0]
G_R2L_F = [-80, 25, 35, -20, 0, 0, 0, 0]
KEYS["WH_DagSlashR2L"] = dict(
    phases=(0.10, 0.12, 0.16),
    keys=[  # (time s, body pose, arm target or None, guess, pass-through?)
        (0.0, {}, None, None, False),
        (0.10, R2L_W, T_R2L_W, G_R2L_W, False),
        (0.16, R2L_C, T_R2L_C, G_R2L_C, True),
        (0.22, R2L_F, T_R2L_F, G_R2L_F, False),
        (0.38, {}, None, None, False)])

# ---- WH_DagSlashL2R: backhand cocked across the belly -> flat cut out -> elbow snaps open right
L2R_W = ready(10, lean=6)
L2R_C = ready(0, lean=6)
L2R_F = ready(-12, lean=4)
T_L2R_W = ((0.06, -0.36, 0.34), (0.85, -0.52, 0.02), ELBOW_PIN)
T_L2R_C = ((-0.18, -0.44, 0.34), (-0.10, -1.0, 0.02))
T_L2R_F = ((-0.44, -0.30, 0.33), (-0.88, -0.46, 0.04), ELBOW_PIN)
G_L2R_W = [-70, 20, 30, -100, 0, 0, 0, 0]
G_L2R_C = [-72, -5, 15, -55, 0, 0, 0, 0]
G_L2R_F = [-65, -35, -10, -25, 0, 0, 0, 0]
KEYS["WH_DagSlashL2R"] = dict(
    phases=(0.10, 0.12, 0.16),
    keys=[
        (0.0, {}, None, None, False),
        (0.10, L2R_W, T_L2R_W, G_L2R_W, False),
        (0.16, L2R_C, T_L2R_C, G_L2R_C, True),
        (0.22, L2R_F, T_L2R_F, G_L2R_F, False),
        (0.38, {}, None, None, False)])

# ---- WH_DagSlashR2Lb: the finisher - same flat R2L cut a touch wider, then
# THE PAUSE: hold the follow-through (blade out left, a beat of stillness),
# then settle back to the rest/guard pose the chain closes on (chainCap reset).
R2Lb_W = ready(-12)
R2Lb_C = ready(0, lean=7)
R2Lb_F = ready(14, lean=8)
R2Lb_H = ready(12, lean=6)
T_R2Lb_W = ((-0.42, -0.24, 0.35), (-0.82, -0.56, 0.02), ELBOW_PIN)
T_R2Lb_C = ((-0.16, -0.45, 0.33), (0.10, -1.0, 0.0))
T_R2Lb_F = ((0.13, -0.41, 0.31), (0.92, -0.38, -0.06), ELBOW_PIN)
T_R2Lb_H = ((0.10, -0.38, 0.29), (0.88, -0.44, -0.10), ELBOW_PIN)
KEYS["WH_DagSlashR2Lb"] = dict(
    phases=(0.10, 0.12, 0.48),
    keys=[
        (0.0, {}, None, None, False),
        (0.10, R2Lb_W, T_R2Lb_W, G_R2L_W, False),
        (0.16, R2Lb_C, T_R2Lb_C, G_R2L_C, True),
        (0.22, R2Lb_F, T_R2Lb_F, G_R2L_F, False),
        (0.36, R2Lb_H, T_R2Lb_H, G_R2L_F, False),
        (0.70, {}, None, None, False)])


def build_keys(spec, name, report):
    out = []
    for k, (t, body, target, guess, through) in enumerate(spec["keys"]):
        pose = head_counter(merge(body))
        if target:
            pose, ep, eb = solve_arm(pose, target[0], target[1], guess,
                                     target[2] if len(target) > 2 else 0.0)
            pos, blade = hand_state(pose)
            arm_vals = {bn: {ch: round(pose[bn][ch], 1) for ch in ("rx", "ry", "rz") if ch in pose[bn]}
                        for bn in ("R_UpperArm", "R_Forearm", "R_Hand")}
            log(f"{name} key{k} t={t:.3f} solved: pos err {ep * 100:.1f} cm, blade err {eb:.1f} deg, {arm_vals}")
            report.setdefault(name, {}).setdefault("solve", []).append(
                {"key": k, "t": round(t, 4), "pos_err_cm": round(ep * 100, 2), "blade_err_deg": round(eb, 1),
                 "arm": arm_vals})
        out.append((t, pose, through))
    return out


# --------------------------------------------------------------------- interpolation
CHANNELS = ("rx", "ry", "rz", "lx", "ly", "lz")


def hermite_tangents(keys):
    """Per key: True -> Catmull-Rom tangent (pass-through), else 0 (ease)."""
    tans = []
    for i, (t, pose, through) in enumerate(keys):
        if not through or i == 0 or i == len(keys) - 1:
            tans.append(None)
            continue
        t0, p0, _ = keys[i - 1]
        t1, p1, _ = keys[i + 1]
        tan = {}
        for bn in set(p0) | set(p1) | set(pose):
            for ch in CHANNELS:
                a = p0.get(bn, {}).get(ch, 0.0)
                b = p1.get(bn, {}).get(ch, 0.0)
                tan[(bn, ch)] = (b - a) / (t1 - t0)
        tans.append(tan)
    return tans


def sample(keys, tans, t):
    for i in range(len(keys) - 1):
        t0, p0, _ = keys[i]
        t1, p1, _ = keys[i + 1]
        if t0 <= t <= t1:
            h = t1 - t0
            u = (t - t0) / h if h > 0 else 1.0
            h00 = 2 * u ** 3 - 3 * u ** 2 + 1
            h10 = u ** 3 - 2 * u ** 2 + u
            h01 = -2 * u ** 3 + 3 * u ** 2
            h11 = u ** 3 - u ** 2
            out = {}
            for bn in BONES:
                c = {}
                for ch in CHANNELS:
                    a = p0.get(bn, {}).get(ch, 0.0)
                    b = p1.get(bn, {}).get(ch, 0.0)
                    m0 = tans[i][(bn, ch)] if tans[i] and (bn, ch) in tans[i] else 0.0
                    m1 = tans[i + 1][(bn, ch)] if tans[i + 1] and (bn, ch) in tans[i + 1] else 0.0
                    c[ch] = h00 * a + h10 * h * m0 + h01 * b + h11 * h * m1
                out[bn] = c
            return out
    return keys[-1][1]


# --------------------------------------------------------------------- bake
def bake(name, spec, report):
    keys = build_keys(spec, name, report)
    tans = hermite_tangents(keys)
    L = round(sum(spec["phases"]) * FPS, 4)     # fractional: exact spec duration
    frames = sorted(set([float(f) for f in range(int(math.floor(L + 1e-6)) + 1)]
                        + [round(t * FPS, 4) for t, _, _ in keys]))
    assert abs(frames[-1] - L) < 1e-6
    old = bpy.data.actions.get(name)
    if old:
        bpy.data.actions.remove(old)
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    arm.animation_data_create()
    arm.animation_data.action = act
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
    path = []
    for f in frames:
        pose = sample(keys, tans, f / FPS)
        for pb in arm.pose.bones:
            c = pose.get(pb.name, {}) if pb.name != "Root" else {}
            rq = REST[pb.name]["rot"]
            pb.rotation_quaternion = rq.inverted() @ axis_quat(c) @ rq
            d = Vector((c.get("lx", 0.0), c.get("ly", 0.0), c.get("lz", 0.0)))
            pb.location = rq.inverted() @ d
            pb.scale = (1, 1, 1)
            for prop in ("rotation_quaternion", "location", "scale"):
                pb.keyframe_insert(prop, frame=f, group=pb.name)
        pos, blade = hand_state(pose)
        path.append((f, pos, blade))
    for fc in act.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
    tr = arm.animation_data.nla_tracks.new()
    tr.name = name
    tr.strips.new(name, 0, act)
    tr.mute = True
    arm.animation_data.action = None
    report.setdefault(name, {})["frames"] = L
    report[name]["duration_s"] = round(L / FPS, 4)
    report[name]["key_frames"] = [round(t * FPS, 4) for t, _, _ in keys]
    w, st, _ = spec["phases"]
    report[name]["boundaries_s"] = [round(w, 4), round(w + st, 4)]
    report[name]["path"] = [{"frame": f, "hand": [round(v, 3) for v in p], "blade": [round(v, 3) for v in b]}
                            for f, p, b in path]
    log(f"clip {name}: {len(frames)} keys ({L} frames @ {FPS} fps = {L / FPS:.4f}s), "
        f"phase keys at frames {report[name]['key_frames']}")
    return act


def check_fk_against_blender(act, frame):
    """The solver FK must agree with Blender's own pose evaluation."""
    arm.animation_data.action = act
    scene.frame_set(int(frame))
    bpy.context.view_layer.update()
    pb = arm.pose.bones["R_Hand"]
    m = pb.matrix
    bl_pos, bl_blade = m.translation.copy(), (m.to_3x3() @ Vector((0, 0, 1))).normalized()
    pose = {}
    for b in arm.pose.bones:   # read back the baked local quats -> armature-axis pose
        rq = REST[b.name]["rot"]
        q = rq @ b.rotation_quaternion @ rq.inverted()
        e = q.to_euler("XYZ")
        pose[b.name] = {"rx": math.degrees(e.x), "ry": math.degrees(e.y), "rz": math.degrees(e.z)}
        loc = rq @ b.location
        pose[b.name].update({"lx": loc.x, "ly": loc.y, "lz": loc.z})
    pos, blade = hand_state(pose)
    arm.animation_data.action = None
    return (pos - bl_pos).length, math.degrees(blade.angle(bl_blade)) if blade.length and bl_blade.length else 0.0


# --------------------------------------------------------------------- preview
DAGGER_GLB = "art-direction/3d/assets/weapons/dagger-curved-pixelated.glb"
MEASURE_JSON = "scratch/dagger_measure.json"
CELL = 512


def grid_times(name):
    """6 QA moments per clip (seconds): rest, windup end, contact, strike end,
    mid recover (R2Lb: end of the follow-through hold = start of the settle), end."""
    w, s, r = KEY_PHASES[name]
    mid = 0.36 if name == "WH_DagSlashR2Lb" else w + s + 0.5 * r
    return [("rest", 0.0), ("windup end", w), ("contact", w + 0.5 * s), ("strike end", w + s),
            ("hold end" if name == "WH_DagSlashR2Lb" else "mid recover", mid), ("end", w + s + r)]


def preview(outdir):
    """QC framing only: the dagger-curved proxy is parented to R_Hand here and
    this mode never exports. Writes <outdir>/<clip>_c<k>.png cells (CELL px);
    scratch/dagger_grid.py composites them into the 6-frame grids."""
    os.makedirs(outdir, exist_ok=True)
    sc = scene
    sc.render.engine = "CYCLES"            # EEVEE needs libEGL (absent headless)
    sc.cycles.device = "CPU"
    sc.cycles.samples = 12
    sc.cycles.use_denoising = False
    sc.render.resolution_x = sc.render.resolution_y = CELL
    world = bpy.data.worlds.new("W")
    sc.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.3, 0.3, 0.35, 1)
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 3
    sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
    sc.collection.objects.link(sun)
    # ground plane at the Root (glTF y = -1 -> armature z = -1)
    bpy.ops.mesh.primitive_plane_add(size=3, location=(0, 0, -1.0))
    gm = bpy.data.materials.new("ground")
    gm.use_nodes = True
    gm.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.18, 0.16, 0.14, 1)
    bpy.context.active_object.data.materials.append(gm)
    # dagger-curved proxy: raw +Y blade (glTF) = Blender +Z after import; grip
    # butt at origin; scaled to the measured in-hand height (A4 JSON).
    meas = json.load(open(MEASURE_JSON))
    k = meas["weaponTargetHeight"] / meas["height_m"]
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.abspath(DAGGER_GLB))
    new = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    assert len(new) == 1, f"dagger import: {len(new)} meshes"
    dag = new[0]
    dag.parent = None
    dag.matrix_world = Matrix.Diagonal((k, k, k, 1.0)) @ Matrix.Diagonal((meas["bladeAxisY"], 1, meas["bladeAxisY"], 1))
    # bone parent: child space = bone TAIL frame; offset back to the head
    dag.parent = arm
    dag.parent_type = "BONE"
    dag.parent_bone = "R_Hand"
    hb = arm.data.bones["R_Hand"]
    dag.matrix_parent_inverse = Matrix.Translation((0, -hb.length, 0))
    log(f"dagger proxy scale {k:.4f} ({meas['weaponTargetHeight']} / {meas['height_m']})")
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 2.3
    sc.collection.objects.link(cam)
    sc.camera = cam
    # elevated front-right 3/4 (character faces -Y, its right is -X): the flat
    # arcs read as left/right travel with visible depth.
    tgt = Vector((-0.05, -0.15, -0.05))
    cam.location = Vector((-3.4, -6.4, 3.0))
    cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
    acts = {a.name: a for a in bpy.data.actions}
    for name in KEYS:
        act = acts[name]
        arm.animation_data.action = act
        for c, (label, t) in enumerate(grid_times(name)):
            f = t * FPS
            sc.frame_set(int(math.floor(f + 1e-6)), subframe=f - math.floor(f + 1e-6))
            sc.render.filepath = os.path.join(outdir, f"{name}_c{c}.png")
            bpy.ops.render.render(write_still=True)
            log(f"cell {name} c{c} {label} t={t:.3f}s frame {f:.2f}")
    log("previews ->", outdir)


# --------------------------------------------------------------------- main
KEY_PHASES.update({n: sp["phases"] for n, sp in KEYS.items()})
if "preview" in opts:
    preview(opts["preview"])
    raise SystemExit(0)

have = sorted(a.name for a in bpy.data.actions)
assert have == ORIGINAL_CLIPS, f"input clips {have}"
report = {}
acts = {}
for name, spec in KEYS.items():
    acts[name] = bake(name, spec, report)
for name, act in acts.items():   # every integer frame (dagger phase keys sit on subframes)
    for f in range(int(math.floor(report[name]["frames"])) + 1):
        ep, eb = check_fk_against_blender(act, f)
        assert ep < 1e-3 and eb < 0.5, f"FK mismatch {name} f{f}: {ep} {eb}"
log("FK cross-check vs Blender pose eval (every integer frame): OK")
for pb in arm.pose.bones:
    pb.rotation_quaternion = (1, 0, 0, 0)
    pb.location = (0, 0, 0)
arm.animation_data.action = None
log("NLA tracks:", [t.name for t in arm.animation_data.nla_tracks])

if OUT_PATH:
    bpy.ops.export_scene.gltf(
        filepath=OUT_PATH, export_format="GLB",
        export_animation_mode="ACTIONS",
        export_skins=True, export_def_bones=False,
        export_apply=False, export_image_format="AUTO",
        export_yup=True,
        export_force_sampling=False,       # keep the 30 fps originals exact (see header)
        export_optimize_animation_size=False,
        export_anim_slide_to_zero=True, export_reset_pose_bones=True,
        export_extras=False, export_cameras=False, export_lights=False)
    log(f"exported {OUT_PATH} ({os.path.getsize(OUT_PATH) / 1e6:.2f} MB)")
if "log" in opts:
    with open(opts["log"], "w") as fh:
        json.dump(report, fh, indent=1)
    log("log ->", opts["log"])
