"""
blender_shield_clips.py -- Order D shield / block / parry clips for the WH
player rig (Blender 4.5 headless, bpy). ASSET SOURCE OF TRUTH for
WH_ShieldRaise / WH_ShieldImpact / WH_ParrySwipe / WH_GuardBreakStagger in
human-hunter-male.combat-chain.glb.

    B=/opt/blender-4.5.4-linux-x64/blender
    $B --background --factory-startup --python scratch/blender_shield_clips.py -- \
        BASE9.glb /tmp/shield_clips.glb [--log X.json] [--preview DIR]
    python3 scratch/glb_append_clips.py BASE9.glb /tmp/shield_clips.glb OUT.glb \
        WH_ShieldRaise WH_ShieldImpact WH_ParrySwipe WH_GuardBreakStagger

BASE9 is the 9-clip combat-chain GLB (6 whanim1 + 3 chain clips, blob of commit
0ffa64e). Blender only AUTHORS here: its export is a temp file. The 4 new
animations are then appended to BASE9 by glb_append_clips.py, which copies
their accessors onto the END of the BIN chunk and appends JSON entries - every
pre-existing byte of BIN and every pre-existing JSON entry is untouched, so the
9 original clips, skin and mesh are byte-identical by construction (asserted).

Conventions are blender_chain_clips.py's (rig_wh_humanoid.py):
  armature space X = character's left, -Y = forward, Z = up; a pose is
  {bone: {rx, ry, rz (deg), lx, ly, lz}}, q = Rz Ry Rx about ARMATURE axes at
  the bone head in the parent's posed frame. rx > 0 pitches forward (spine
  lean / head drop), thigh rx < 0 lifts the knee forward, shin rx > 0 bends
  the knee, rz > 0 turns the chest to the character's LEFT.
The shield: game.js mounts round-shield-pixelated.glb on L_Hand with
CONFIG.assets.shieldMount faceAxis / upAxis (hand-local). Measured at bind
(= WH_Idle frame 0 within 0.03) those axes are, in armature space,
FACE_REST (0.940, -0.340, -0.035) and UP_REST (0, -0.105, 0.995), so a posed
L_Hand with deformation Q shows the boss along Q @ FACE_REST. The left arm of
every shield key is SOLVED (Nelder-Mead over L_UpperArm/L_Forearm/L_Hand) to
an authored hand position + boss direction + disc-up direction.

Guard pose = the END frame of Raise / Impact / ParrySwipe (identical by
construction: the same GUARD dict, zero tangent), so a clamped hold after any
of them is continuous. Raise starts at bind (the chain clips' rest guard; the
idle->raise crossfade covers WH_Idle's breathing offset). Stagger starts at
GUARD (guard break always fires mid-block) and ends in a low crouch, which the
game holds (clampWhenFinished) for the rest of the stun.
Feet: every key re-plants the lower foot at its bind height by shifting Hips
lz (knee bends do not float/sink the body).
24 fps baked, every bone T/R/S keyed on every frame, LINEAR, Root static.
"""
import bpy
import sys
import os
import math
import json
from mathutils import Vector, Quaternion, Matrix

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if len(argv) < 2:
    raise SystemExit("usage: blender --background --python blender_shield_clips.py -- BASE9.glb TMP_OUT.glb [--log X.json] [--preview DIR]")
IN_PATH = os.path.abspath(argv[0])
OUT_PATH = os.path.abspath(argv[1])
opts = {}
rest = argv[2:]
for i in range(0, len(rest), 2):
    opts[rest[i].lstrip("-")] = rest[i + 1]

FPS = 24
BONES = ["Root", "Hips", "Spine", "Chest", "Neck", "Head",
         "L_Shoulder", "L_UpperArm", "L_Forearm", "L_Hand",
         "R_Shoulder", "R_UpperArm", "R_Forearm", "R_Hand",
         "L_Thigh", "L_Shin", "L_Foot", "R_Thigh", "R_Shin", "R_Foot"]
BASE_CLIPS = ["WH_Attack1", "WH_Death", "WH_Hit", "WH_Idle", "WH_Run",
              "WH_SlashL2R", "WH_SlashR2L", "WH_Thrust", "WH_Walk"]
NEW_CLIPS = ["WH_ShieldRaise", "WH_ShieldImpact", "WH_ParrySwipe", "WH_GuardBreakStagger"]
FACE_REST = Vector((0.9396, -0.3404, -0.0352)).normalized()
UP_REST = Vector((-0.0003, -0.1046, 0.9945)).normalized()


def log(*a):
    print("[SHIELD]", *a, flush=True)


# --------------------------------------------------------------------- import
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=IN_PATH)
scene = bpy.context.scene
scene.render.fps = FPS
arm = bpy.data.objects["WH_Armature"]
bone_names = [b.name for b in arm.data.bones]
assert sorted(bone_names) == sorted(BONES), f"unexpected skeleton {bone_names}"
log("skeleton verified:", len(bone_names), "bones", bone_names)
assert arm.matrix_world == Matrix.Identity(4)
have = sorted(a.name for a in bpy.data.actions)
assert have == BASE_CLIPS, f"input clips {have} (expected the 9-clip base)"
log("input clips verified:", have)
REST = {}
for b in arm.data.bones:
    REST[b.name] = {"head": b.head_local.copy(), "rot": b.matrix_local.to_quaternion(),
                    "parent": b.parent.name if b.parent else None}
BLADE_REST = REST["R_Hand"]["rot"] @ Vector((0, 0, 1))


# --------------------------------------------------------------------- FK
def axis_quat(c):
    return (Quaternion((0, 0, 1), math.radians(c.get("rz", 0.0)))
            @ Quaternion((0, 1, 0), math.radians(c.get("ry", 0.0)))
            @ Quaternion((1, 0, 0), math.radians(c.get("rx", 0.0))))


def fk(pose):
    D = {}
    for name in BONES:
        r = REST[name]
        c = pose.get(name, {})
        q = axis_quat(c)
        h = r["head"]
        d = Vector((c.get("lx", 0.0), c.get("ly", 0.0), c.get("lz", 0.0)))
        Qp, tp = D[r["parent"]] if r["parent"] else (Quaternion(), Vector())
        D[name] = (Qp @ q, Qp @ (d + h - q @ h) + tp)
    return D


def joint_pos(D, bone):
    Qp, tp = D[REST[bone]["parent"]]
    return Qp @ REST[bone]["head"] + tp


def l_hand_state(pose):
    D = fk(pose)
    Q = D["L_Hand"][0]
    return joint_pos(D, "L_Hand"), Q @ FACE_REST, Q @ UP_REST


def r_hand_state(pose):
    D = fk(pose)
    return joint_pos(D, "R_Hand"), D["R_Hand"][0] @ BLADE_REST


FOOT_REST_Z = min(REST["L_Foot"]["head"].z, REST["R_Foot"]["head"].z)


def plant_feet(pose):
    """Shift Hips lz so the lower foot sits at its bind height."""
    D = fk(pose)
    low = min(joint_pos(D, "L_Foot").z, joint_pos(D, "R_Foot").z)
    pose.setdefault("Hips", {})
    pose["Hips"]["lz"] = pose["Hips"].get("lz", 0.0) - (low - FOOT_REST_Z)
    return pose


# --------------------------------------------------------------------- solver
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


def arm_keys(side):
    return [(side + "_UpperArm", "rx"), (side + "_UpperArm", "ry"), (side + "_UpperArm", "rz"),
            (side + "_Forearm", "rx"), (side + "_Forearm", "ry"),
            (side + "_Hand", "rx"), (side + "_Hand", "ry"), (side + "_Hand", "rz")]


# right-arm bounds from blender_chain_clips.py; left = mirror (ry, rz negate)
R_BOUNDS = [(-200, 70), (-130, 90), (-95, 95), (-145, -4), (-25, 25), (-75, 75), (-75, 75), (-75, 75)]
L_BOUNDS = [(-200, 70), (-90, 130), (-95, 95), (-145, -4), (-25, 25), (-75, 75), (-75, 75), (-75, 75)]


def solve(body, side, target, guesses):
    """side 'L': target = (pos, face, up, w_face, w_up); 'R': (pos, blade, w_blade).
    Several guesses (elbow choices); the lowest cost wins."""
    keys = arm_keys(side)
    bounds = L_BOUNDS if side == "L" else R_BOUNDS
    tp = Vector(target[0])
    if side == "L":
        tf, tu = Vector(target[1]).normalized(), Vector(target[2]).normalized()
        wf, wu = target[3], target[4]
    else:
        tb, wb = Vector(target[1]).normalized(), target[2]

    def build(x):
        p = {k: dict(v) for k, v in body.items()}
        for (bn, ch), v in zip(keys, x):
            p.setdefault(bn, {})[ch] = v
        return p

    def cost_for(guess):
        def cost(x):
            p = build(x)
            if side == "L":
                pos, face, up = l_hand_state(p)
                c = 100.0 * (pos - tp).length_squared + wf * (face - tf).length_squared + wu * (up - tu).length_squared
            else:
                pos, blade = r_hand_state(p)
                c = 100.0 * (pos - tp).length_squared + wb * (blade - tb).length_squared
            for v, g, (lo, hi), (bn, _) in zip(x, guess, bounds, keys):
                c += 4e-6 * (v - g) ** 2
                if bn.endswith("_Hand"):
                    c += 1.5e-5 * v * v
                if v < lo:
                    c += 1e-3 * (lo - v) ** 2
                elif v > hi:
                    c += 1e-3 * (v - hi) ** 2
            return c
        return cost

    best = None
    for guess in guesses:
        cost = cost_for(guess)
        for start_step in (12.0, 30.0):
            x, v = nelder_mead(cost, guess, step=start_step)
            x, v = nelder_mead(cost, x, step=4.0)
            if best is None or v < best[1]:
                best = (x, v)
    pose = build(best[0])
    if side == "L":
        pos, face, up = l_hand_state(pose)
        errs = ((pos - tp).length * 100, math.degrees(face.angle(tf)), math.degrees(up.angle(tu)))
    else:
        pos, blade = r_hand_state(pose)
        errs = ((pos - tp).length * 100, math.degrees(blade.angle(tb)), 0.0)
    return pose, errs


# --------------------------------------------------------------------- poses
def merge(*ps):
    out = {}
    for p in ps:
        for bn, c in p.items():
            out.setdefault(bn, {}).update(c)
    return out


def torso(yaw, lean=0.0, hips=0.0):
    return {"Hips": {"rz": hips},
            "Spine": {"rz": 0.4 * yaw, "rx": 0.4 * lean},
            "Chest": {"rz": 0.6 * yaw, "rx": 0.6 * lean}}


def head_counter(p, k=0.6):
    sp = sum(p.get(b, {}).get("rz", 0.0) for b in ("Hips", "Spine", "Chest"))
    for bone, share in (("Neck", 0.4), ("Head", 0.6)):
        c = p.setdefault(bone, {})
        c["rz"] = c.get("rz", 0.0) - share * k * sp
    return p


def stance(knee, split=0.0):
    """Both knees bent by `knee` deg (thigh forward, shin back, foot flat);
    split > 0 puts the left leg forward / right leg back."""
    t = knee * 0.5
    return {"L_Thigh": {"rx": -t - split}, "L_Shin": {"rx": knee}, "L_Foot": {"rx": -t + split},
            "R_Thigh": {"rx": -t + split}, "R_Shin": {"rx": knee}, "R_Foot": {"rx": -t - split}}


# Left-arm guesses (deg): forward raise + elbow flex, a few elbow twists.
L_GUESSES = [[-55, 20, 20, -95, 0, 0, 0, 0], [-70, -10, 40, -110, 0, 0, 0, 0],
             [-40, 40, -10, -80, 0, 0, 0, 0]]
FWD = (0.0, -1.0, 0.0)

# GUARD: left side turned in, shield square to the front at chest height,
# boss angled 15 deg out-left, disc top tipped 8 deg back; knees soft.
GUARD_BODY = merge(torso(-14, lean=6), stance(16, split=6), {
    "L_Shoulder": {"rz": -6, "rx": 4}})
GUARD_L = ((0.13, -0.30, 0.44), (0.26, -0.97, 0.0), (0.0, 0.14, 0.99), 2.0, 1.0)
# right (sword) arm: tucked guard by the right hip, blade forward-up
GUARD_R = ((-0.33, -0.16, 0.20), (0.10, -0.85, 0.52), 1.0)
R_GUESS = [[-60, 0, 0, -50, 0, 0, 0, 0]]

# IMPACT recoil: shield driven back toward the chest + up, top tipped back,
# shoulder compressed, torso rocked back.
IMPACT_BODY = merge(torso(-20, lean=-10), stance(20, split=4), {
    "L_Shoulder": {"rz": -2, "rx": -6, "ly": 0.012}})
IMPACT_L = ((0.16, -0.17, 0.49), (0.38, -0.88, 0.28), (0.0, 0.42, 0.91), 2.0, 1.0)
# settle: small overshoot forward before the guard
SETTLE_BODY = merge(torso(-12, lean=8), stance(17, split=6), {"L_Shoulder": {"rz": -7, "rx": 5}})
SETTLE_L = ((0.13, -0.32, 0.43), (0.24, -0.97, -0.03), (0.0, 0.10, 0.99), 2.0, 1.0)

# PARRY: coil (shield in, torso wound right), then a hard angled shove out
# to the front-left with the boss turned outward (deflect), back to guard.
COIL_BODY = merge(torso(-26, lean=4), stance(18, split=6), {"L_Shoulder": {"rz": -10}})
COIL_L = ((0.04, -0.24, 0.42), (-0.10, -0.99, 0.0), (0.0, 0.10, 0.99), 2.0, 1.0)
SHOVE_BODY = merge(torso(18, lean=12, hips=6), stance(22, split=10), {
    "L_Shoulder": {"rz": 4, "rx": 8}})
SHOVE_L = ((0.32, -0.38, 0.46), (0.72, -0.66, 0.20), (-0.22, 0.10, 0.97), 2.0, 1.0)

# GUARD BREAK: reel back (arms flung, head back) -> head drops -> low crouch.
REEL_BODY = merge(torso(-24, lean=-22, hips=-6), stance(14, split=-10), {
    "Neck": {"rx": -12}, "Head": {"rx": -16}, "L_Shoulder": {"rx": -10, "rz": 6},
    "R_Shoulder": {"rx": -8}})
REEL_L = ((0.40, -0.06, 0.40), (0.70, -0.20, 0.68), (0.30, 0.60, 0.74), 0.4, 0.2)
REEL_R = ((-0.46, -0.04, 0.22), (-0.40, -0.40, 0.82), 0.3)
SLUMP_BODY = merge(torso(-10, lean=18, hips=-2), stance(34, split=-6), {
    "Neck": {"rx": 16}, "Head": {"rx": 22}, "L_Shoulder": {"rx": 8}, "R_Shoulder": {"rx": 8}})
SLUMP_L = ((0.37, -0.18, 0.18), (0.80, -0.30, -0.50), (0.10, -0.60, 0.79), 0.4, 0.2)
SLUMP_R = ((-0.32, -0.20, 0.10), (-0.10, -0.60, -0.80), 0.3)
CROUCH_BODY = merge(torso(-8, lean=22), stance(40, split=-4), {
    "Neck": {"rx": 18}, "Head": {"rx": 24}, "L_Shoulder": {"rx": 10}, "R_Shoulder": {"rx": 10}})
CROUCH_L = ((0.35, -0.20, 0.16), (0.85, -0.25, -0.45), (0.05, -0.55, 0.83), 0.4, 0.2)
CROUCH_R = ((-0.30, -0.22, 0.08), (-0.05, -0.55, -0.83), 0.3)


SOLVE_LOG = {}


def key_pose(name, label, body, l_target, r_target=GUARD_R):
    pose = plant_feet(head_counter(merge(body)))   # legs/torso first: arms solve in the planted body
    pose, el = solve(pose, "L", l_target, L_GUESSES)
    pose, er = solve(pose, "R", r_target, R_GUESS)
    log(f"{name} {label}: L pos {el[0]:.1f}cm face {el[1]:.1f}deg up {el[2]:.1f}deg | "
        f"R pos {er[0]:.1f}cm blade {er[1]:.1f}deg | hips lz {pose['Hips']['lz']:+.3f}")
    SOLVE_LOG.setdefault(name, []).append({
        "key": label, "L_pos_cm": round(el[0], 2), "L_face_deg": round(el[1], 1), "L_up_deg": round(el[2], 1),
        "R_pos_cm": round(er[0], 2), "R_blade_deg": round(er[1], 1),
        "arm": {bn: {ch: round(pose[bn].get(ch, 0.0), 1) for ch in ("rx", "ry", "rz")}
                for bn in ("L_UpperArm", "L_Forearm", "L_Hand", "R_UpperArm", "R_Forearm", "R_Hand")}})
    return pose


_guard_cache = {}


def guard(name):
    # one solve, reused, so every guard frame is the IDENTICAL pose
    if "g" not in _guard_cache:
        _guard_cache["g"] = key_pose("GUARD", "guard", GUARD_BODY, GUARD_L)
    return _guard_cache["g"]


CLIPS = {
    # name: (frames, [(t, pose_fn, pass_through)])
    "WH_ShieldRaise": (6, [
        (0.0, lambda n: {}, False),
        (1.0, guard, False)]),
    "WH_ShieldImpact": (8, [
        (0.0, guard, False),
        (0.22, lambda n: key_pose(n, "recoil", IMPACT_BODY, IMPACT_L), False),
        (0.62, lambda n: key_pose(n, "settle", SETTLE_BODY, SETTLE_L), True),
        (1.0, guard, False)]),
    "WH_ParrySwipe": (10, [
        (0.0, guard, False),
        (0.18, lambda n: key_pose(n, "coil", COIL_BODY, COIL_L), False),
        (0.42, lambda n: key_pose(n, "shove", SHOVE_BODY, SHOVE_L), False),
        (1.0, guard, False)]),
    "WH_GuardBreakStagger": (19, [
        (0.0, guard, False),
        (0.2, lambda n: key_pose(n, "reel", REEL_BODY, REEL_L, REEL_R), False),
        (0.55, lambda n: key_pose(n, "slump", SLUMP_BODY, SLUMP_L, SLUMP_R), True),
        (1.0, lambda n: key_pose(n, "crouch", CROUCH_BODY, CROUCH_L, CROUCH_R), False)]),
}


# --------------------------------------------------------------------- interpolation
CHANNELS = ("rx", "ry", "rz", "lx", "ly", "lz")


def tangents(keys):
    tans = []
    for i, (t, pose, through) in enumerate(keys):
        if not through or i == 0 or i == len(keys) - 1:
            tans.append(None)
            continue
        t0, p0, _ = keys[i - 1]
        t1, p1, _ = keys[i + 1]
        tans.append({(bn, ch): (p1.get(bn, {}).get(ch, 0.0) - p0.get(bn, {}).get(ch, 0.0)) / (t1 - t0)
                     for bn in BONES for ch in CHANNELS})
    return tans


def sample(keys, tans, t):
    for i in range(len(keys) - 1):
        t0, p0, _ = keys[i]
        t1, p1, _ = keys[i + 1]
        if t0 <= t <= t1:
            h = t1 - t0
            u = (t - t0) / h if h > 0 else 1.0
            h00, h10 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u
            h01, h11 = -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
            out = {}
            for bn in BONES:
                c = {}
                for ch in CHANNELS:
                    a = p0.get(bn, {}).get(ch, 0.0)
                    b = p1.get(bn, {}).get(ch, 0.0)
                    m0 = tans[i][(bn, ch)] if tans[i] else 0.0
                    m1 = tans[i + 1][(bn, ch)] if tans[i + 1] else 0.0
                    c[ch] = h00 * a + h10 * h * m0 + h01 * b + h11 * h * m1
                out[bn] = c
            return out
    return keys[-1][1]


def bake(name, frames, spec, report):
    keys = [(t, fn(name), through) for t, fn, through in spec]
    tans = tangents(keys)
    fr = sorted(set([float(f) for f in range(frames + 1)] + [round(t * frames, 4) for t, _, _ in keys]))
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
    for f in fr:
        pose = sample(keys, tans, f / frames)
        for pb in arm.pose.bones:
            c = pose.get(pb.name, {}) if pb.name != "Root" else {}
            rq = REST[pb.name]["rot"]
            pb.rotation_quaternion = rq.inverted() @ axis_quat(c) @ rq
            pb.location = rq.inverted() @ Vector((c.get("lx", 0.0), c.get("ly", 0.0), c.get("lz", 0.0)))
            pb.scale = (1, 1, 1)
            for prop in ("rotation_quaternion", "location", "scale"):
                pb.keyframe_insert(prop, frame=f, group=pb.name)
        pos, face, up = l_hand_state(pose)
        path.append({"frame": f, "L_hand": [round(v, 3) for v in pos], "face": [round(v, 3) for v in face]})
    for fc in act.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
    tr = arm.animation_data.nla_tracks.new()
    tr.name = name
    tr.strips.new(name, 0, act)
    tr.mute = True
    arm.animation_data.action = None
    report[name] = {"frames": frames, "duration_s": round(frames / FPS, 4),
                    "key_frames": [round(t * frames, 4) for t, _, _ in keys], "path": path}
    log(f"clip {name}: {len(fr)} keys ({frames} frames @ {FPS} fps = {frames / FPS:.3f}s)")
    return act, keys


def check_fk(act, frame):
    """Solver FK vs Blender's own pose evaluation (L_Hand position + boss)."""
    arm.animation_data.action = act
    scene.frame_set(int(frame))
    bpy.context.view_layer.update()
    pose = {}
    for b in arm.pose.bones:
        rq = REST[b.name]["rot"]
        e = (rq @ b.rotation_quaternion @ rq.inverted()).to_euler("XYZ")
        loc = rq @ b.location
        pose[b.name] = {"rx": math.degrees(e.x), "ry": math.degrees(e.y), "rz": math.degrees(e.z),
                        "lx": loc.x, "ly": loc.y, "lz": loc.z}
    pos, face, _ = l_hand_state(pose)
    m = arm.pose.bones["L_Hand"].matrix
    bl_face = (m.to_quaternion() @ REST["L_Hand"]["rot"].inverted()) @ FACE_REST
    arm.animation_data.action = None
    return (pos - m.translation).length, math.degrees(face.angle(bl_face))


# --------------------------------------------------------------------- preview
def preview(outdir, acts):
    os.makedirs(outdir, exist_ok=True)
    sc = scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 6
    sc.cycles.use_denoising = False
    sc.render.resolution_x = sc.render.resolution_y = 320
    world = bpy.data.worlds.new("W")
    sc.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.3, 0.3, 0.35, 1)
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 3
    sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
    sc.collection.objects.link(sun)
    # shield proxy: 0.48-unit disc (1.0 m in game at the body scale), boss
    # along the posed FACE axis, placed 0.05 in front of the fist
    bpy.ops.mesh.primitive_cylinder_add(radius=0.24, depth=0.02, vertices=24)
    disc = bpy.context.active_object
    mat = bpy.data.materials.new("amber")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.9, 0.5, 0.1, 1)
    disc.data.materials.append(mat)
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 2.0
    sc.collection.objects.link(cam)
    sc.camera = cam
    views = {"front": ((0, -8, 0.4), (math.radians(90), 0, 0)),
             "side": ((8, 0, 0.4), (math.radians(90), 0, math.radians(90))),
             "q34": ((5.6, -5.6, 2.0), (math.radians(78), 0, math.radians(45)))}
    for name, act in acts.items():
        arm.animation_data.action = act
        L = int(act.frame_range[1])
        for f in sorted(set([0, L // 4, L // 2, (3 * L) // 4, L])):
            sc.frame_set(f)
            bpy.context.view_layer.update()
            m = arm.pose.bones["L_Hand"].matrix
            Q = m.to_quaternion() @ REST["L_Hand"]["rot"].inverted()
            face, up = Q @ FACE_REST, Q @ UP_REST
            x = up.cross(face).normalized()
            y = face.cross(x).normalized()
            rot = Matrix((x, y, face)).transposed().to_4x4()   # disc normal (local Z) = face
            disc.matrix_world = Matrix.Translation(m.translation + face * 0.05) @ rot
            for vn, (loc, r) in views.items():
                cam.location, cam.rotation_euler = loc, r
                sc.render.filepath = os.path.join(outdir, f"{name}_f{f:02d}_{vn}.png")
                bpy.ops.render.render(write_still=True)
    arm.animation_data.action = None
    log("previews ->", outdir)


# --------------------------------------------------------------------- main
report = {}
acts = {}
for name in NEW_CLIPS:
    frames, spec = CLIPS[name]
    acts[name], keys = bake(name, frames, spec, report)
for name, act in acts.items():
    for f in report[name]["key_frames"]:
        if abs(f - round(f)) < 1e-6:
            ep, ef = check_fk(act, f)
            assert ep < 1e-3 and ef < 0.5, f"FK mismatch {name} f{f}: {ep} {ef}"
log("FK cross-check vs Blender pose eval: OK")
g_end = {n: report[n]["path"][-1] for n in ("WH_ShieldRaise", "WH_ShieldImpact", "WH_ParrySwipe")}
log("guard end frames (L_Hand, boss):", g_end)
assert len({json.dumps([v["L_hand"], v["face"]]) for v in g_end.values()}) == 1, "guard ends differ"
assert report["WH_GuardBreakStagger"]["path"][0]["L_hand"] == g_end["WH_ShieldRaise"]["L_hand"], "stagger must start at guard"
for pb in arm.pose.bones:
    pb.rotation_quaternion = (1, 0, 0, 0)
    pb.location = (0, 0, 0)
arm.animation_data.action = None
log("NLA tracks:", [t.name for t in arm.animation_data.nla_tracks])

bpy.ops.export_scene.gltf(
    filepath=OUT_PATH, export_format="GLB",
    export_animation_mode="ACTIONS",
    export_skins=True, export_def_bones=False,
    export_apply=False, export_image_format="AUTO",
    export_yup=True,
    export_force_sampling=False,
    export_optimize_animation_size=False,
    export_anim_slide_to_zero=True, export_reset_pose_bones=True,
    export_extras=False, export_cameras=False, export_lights=False)
log(f"exported temp {OUT_PATH} ({os.path.getsize(OUT_PATH) / 1e6:.2f} MB) - append the 4 new clips with glb_append_clips.py")
if "log" in opts:
    with open(opts["log"], "w") as fh:
        json.dump({"solve": SOLVE_LOG, "clips": report}, fh, indent=1)
    log("log ->", opts["log"])
if "preview" in opts:
    preview(opts["preview"], acts)
