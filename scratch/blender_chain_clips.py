"""
blender_chain_clips.py -- longsword 3-chain attack clips for the WH player rig
(Blender 4.5 headless, bpy). ASSET SOURCE OF TRUTH for WH_SlashR2L /
WH_SlashL2R / WH_Thrust in human-hunter-male.combat-chain.glb.

    /opt/blender-4.5.4-linux-x64/blender --background --factory-startup \
        --python scratch/blender_chain_clips.py -- IN.glb OUT.glb [--log OUT.json]
    # QA renders (no export; IN = an exported GLB, sword proxy on R_Hand):
    ... --python scratch/blender_chain_clips.py -- IN.glb --preview DIR

IN is the combat-chain COPY of human-hunter-male.rigged.glb (the original is
never opened for writing). Pipeline: glTF import -> author 3 actions (24 fps
baked, every bone keyed) -> stash each on its own muted NLA track next to the
6 imported WH_* tracks -> glTF export.

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
  slashes 0.14/0.20/0.30 -> 15 frames (0.625 s), windup ends 21.9 %,
          strike ends 53.1 % (strike = 31 %);
  thrust  0.16/0.14/0.40 -> 16 frames (0.667 s), windup ends 22.9 %,
          strike ends 42.9 % (strike = 20 %).
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
    print("[CHAIN]", *a, flush=True)


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


def solve_arm(body, target_pos, target_blade, guess):
    """Fill R_UpperArm/R_Forearm/R_Hand of `body` so the R_Hand socket lands
    on target_pos with the blade along target_blade. guess = 8 floats (deg),
    also the regularization anchor (keeps the elbow/twist choice coherent)."""
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


# Right-arm targets: (hand socket position, blade direction) in armature space.
# Reference: R shoulder joint (-0.242, 0.0, 0.555), arm reach ~0.55,
# rest hand (-0.415, -0.108, 0.042) with blade forward (0.06, -0.98, 0.18).
G_UP = [-60, 0, 0, -40, 0, 0, 0, 0]

KEYS = {}

# ---- WH_SlashR2L: cocked high back-right -> flat sweep through the front -> follow-through left
R2L_WINDUP = merge(twist(-38, lean=-4, hips=-8), {
    "R_Shoulder": {"rz": -8, "ry": 8},
    "L_UpperArm": {"rx": -30, "ry": 8}, "L_Forearm": {"rx": -55},
    "L_Thigh": {"rx": -6}, "R_Thigh": {"rx": 8}, "Hips": {"lz": -0.01}})
R2L_CONTACT = merge(twist(0, lean=8, hips=0), {
    "L_UpperArm": {"rx": 10, "ry": -15}, "L_Forearm": {"rx": -35},
    "L_Thigh": {"rx": -10}, "R_Thigh": {"rx": 6}, "R_Shin": {"rx": 8}, "Hips": {"lz": -0.025}})
R2L_FOLLOW = merge(twist(42, lean=10, hips=10), {
    "R_Shoulder": {"rz": 10},
    "L_UpperArm": {"rx": 28, "ry": -30}, "L_Forearm": {"rx": -30},
    "L_Thigh": {"rx": -8}, "R_Thigh": {"rx": 10}, "R_Shin": {"rx": 12}, "Hips": {"lz": -0.03}})
KEYS["WH_SlashR2L"] = dict(
    frames=15, boundaries=(0.14 / 0.64, 0.34 / 0.64),
    keys=[  # (time fraction, body pose, arm target or None, guess, pass-through?)
        (0.0, {}, None, None, False),
        (0.14 / 0.64, R2L_WINDUP, ((-0.50, 0.12, 0.80), (-0.55, 0.55, 0.62)), [-150, -40, 20, -60, 0, 0, 0, 0], False),
        (0.24 / 0.64, R2L_CONTACT, ((-0.12, -0.50, 0.50), (0.05, -1.0, 0.05)), [-95, -10, 10, -25, 0, 0, 0, 0], True),
        (0.34 / 0.64, R2L_FOLLOW, ((0.32, -0.30, 0.42), (0.88, -0.30, -0.12)), [-80, 40, 40, -30, 0, 0, 0, 0], False),
        (1.0, {}, None, None, False)])

# ---- WH_SlashL2R: coiled low-left -> rising diagonal -> finish high right
L2R_WINDUP = merge(twist(34, lean=14, hips=10), {
    "R_Shoulder": {"rz": 8, "ry": -6},
    "L_UpperArm": {"rx": 22, "ry": -20}, "L_Forearm": {"rx": -40},
    "L_Thigh": {"rx": -18}, "L_Shin": {"rx": 26}, "R_Thigh": {"rx": -10}, "R_Shin": {"rx": 22},
    "Hips": {"lz": -0.06}})
L2R_CONTACT = merge(twist(0, lean=6, hips=0), {
    "L_UpperArm": {"rx": 5, "ry": -10}, "L_Forearm": {"rx": -35},
    "L_Thigh": {"rx": -10}, "L_Shin": {"rx": 12}, "R_Thigh": {"rx": -4}, "R_Shin": {"rx": 10},
    "Hips": {"lz": -0.03}})
L2R_FOLLOW = merge(twist(-40, lean=-8, hips=-10), {
    "R_Shoulder": {"rz": -10, "ry": 14},
    "L_UpperArm": {"rx": -25, "ry": -35}, "L_Forearm": {"rx": -20},
    "L_Thigh": {"rx": 4}, "R_Thigh": {"rx": -6}, "R_Foot": {"rx": -10},
    "Hips": {"lz": 0.005}})
KEYS["WH_SlashL2R"] = dict(
    frames=15, boundaries=(0.14 / 0.64, 0.34 / 0.64),
    keys=[
        (0.0, {}, None, None, False),
        (0.14 / 0.64, L2R_WINDUP, ((0.22, -0.22, 0.02), (0.55, 0.30, -0.78)), [-70, 30, 40, -70, 0, 0, 0, 0], False),
        (0.24 / 0.64, L2R_CONTACT, ((-0.12, -0.50, 0.36), (-0.30, -0.80, 0.52)), [-85, -5, 5, -25, 0, 0, 0, 0], True),
        (0.34 / 0.64, L2R_FOLLOW, ((-0.52, -0.22, 0.88), (-0.62, -0.05, 0.78)), [-160, -40, -10, -30, 0, 0, 0, 0], False),
        (1.0, {}, None, None, False)])

# ---- WH_Thrust: chamber at the right hip -> straight lunge -> hold -> back to guard
TH_WINDUP = merge(twist(-30, lean=-6, hips=-8), {
    "R_Shoulder": {"rz": -6, "ry": 6},
    "L_UpperArm": {"rx": -35, "ry": -12}, "L_Forearm": {"rx": -60},
    # weight back on the rear (left) leg
    "L_Thigh": {"rx": -10}, "L_Shin": {"rx": 18}, "R_Thigh": {"rx": 4}, "R_Shin": {"rx": 8},
    "Hips": {"lz": -0.03}})
TH_EXTEND = merge(twist(22, lean=16, hips=8), {
    "R_Shoulder": {"rz": 12, "ry": -4},
    "L_UpperArm": {"rx": 35, "ry": -25}, "L_Forearm": {"rx": -15},
    # lunge step: right leg forward and bent, left leg extended behind
    "R_Thigh": {"rx": -42}, "R_Shin": {"rx": 40}, "R_Foot": {"rx": 8},
    "L_Thigh": {"rx": 22}, "L_Shin": {"rx": 8}, "L_Foot": {"rx": -18},
    "Hips": {"lz": -0.07}})
KEYS["WH_Thrust"] = dict(
    frames=16, boundaries=(0.16 / 0.70, 0.30 / 0.70),
    keys=[
        (0.0, {}, None, None, False),
        (0.16 / 0.70, TH_WINDUP, ((-0.36, 0.20, 0.30), (0.02, -1.0, 0.02)), [-10, -20, 0, -115, 0, 0, 0, 0], False),
        (0.30 / 0.70, TH_EXTEND, ((-0.12, -0.62, 0.50), (0.02, -1.0, 0.0)), [-85, -5, 0, -8, 0, 0, 0, 0], False),
        (0.40 / 0.70, TH_EXTEND, ((-0.12, -0.60, 0.48), (0.02, -1.0, 0.0)), [-85, -5, 0, -10, 0, 0, 0, 0], False),
        (1.0, {}, None, None, False)])


def build_keys(spec, name, report):
    out = []
    for k, (t, body, target, guess, through) in enumerate(spec["keys"]):
        pose = head_counter(merge(body))
        if target:
            pose, ep, eb = solve_arm(pose, target[0], target[1], guess)
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
    L = spec["frames"]
    frames = sorted(set([float(f) for f in range(L + 1)] + [round(t * L, 4) for t, _, _ in keys]))
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
        pose = sample(keys, tans, f / L)
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
    report[name]["key_frames"] = [round(t * L, 4) for t, _, _ in keys]
    report[name]["boundaries_s"] = [round(b * L / FPS, 4) for b in spec["boundaries"]]
    report[name]["path"] = [{"frame": f, "hand": [round(v, 3) for v in p], "blade": [round(v, 3) for v in b]}
                            for f, p, b in path]
    log(f"clip {name}: {len(frames)} keys ({L} frames @ {FPS} fps = {L / FPS:.3f}s), "
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
def preview(outdir):
    os.makedirs(outdir, exist_ok=True)
    sc = scene
    sc.render.engine = "BLENDER_EEVEE_NEXT"
    sc.eevee.taa_render_samples = 4
    sc.render.resolution_x = sc.render.resolution_y = 320
    world = bpy.data.worlds.new("W")
    sc.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.3, 0.3, 0.35, 1)
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 3
    sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
    sc.collection.objects.link(sun)
    # sword proxy: 1.0 long blade along R_Hand local +Z, red tip
    bpy.ops.mesh.primitive_cube_add(size=1)
    blade = bpy.context.active_object
    blade.scale = (0.02, 0.05, 0.5)
    blade.location = (0, 0, 0.5)
    bpy.ops.object.transform_apply(location=True, scale=True)
    mat = bpy.data.materials.new("tip")
    mat.diffuse_color = (0.9, 0.1, 0.1, 1)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.9, 0.1, 0.1, 1)
    blade.data.materials.append(mat)
    # bone parent: child space = bone TAIL frame; offset back to the head
    blade.parent = arm
    blade.parent_type = "BONE"
    blade.parent_bone = "R_Hand"
    hb = arm.data.bones["R_Hand"]
    blade.matrix_parent_inverse = Matrix.Translation((0, -hb.length, 0))
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 3.0
    sc.collection.objects.link(cam)
    sc.camera = cam
    views = {"front": ((0, -8, 0.1), (math.radians(90), 0, 0)),
             "side": ((8, 0, 0.1), (math.radians(90), 0, math.radians(90))),
             "top": ((0, 0, 8), (0, 0, 0))}
    acts = {a.name: a for a in bpy.data.actions}
    for name in ("WH_SlashR2L", "WH_SlashL2R", "WH_Thrust", "WH_Attack1"):
        act = acts[name]
        arm.animation_data.action = act
        fs = sorted(set(int(round(f)) for f in [0] + list(act.frame_range) + [act.frame_range[1] * x for x in (0.22, 0.375, 0.53, 0.75)]))
        for f in fs:
            sc.frame_set(f)
            for vn, (loc, rot) in views.items():
                cam.location, cam.rotation_euler = loc, rot
                sc.render.filepath = os.path.join(outdir, f"{name}_f{f:02d}_{vn}.png")
                bpy.ops.render.render(write_still=True)
    log("previews ->", outdir)


# --------------------------------------------------------------------- main
if "preview" in opts:
    preview(opts["preview"])
    raise SystemExit(0)

have = sorted(a.name for a in bpy.data.actions)
assert have == ORIGINAL_CLIPS, f"input clips {have}"
report = {}
acts = {}
for name, spec in KEYS.items():
    acts[name] = bake(name, spec, report)
for name, act in acts.items():
    for f in report[name]["key_frames"]:
        if abs(f - round(f)) < 1e-6:
            ep, eb = check_fk_against_blender(act, f)
            assert ep < 1e-3 and eb < 0.5, f"FK mismatch {name} f{f}: {ep} {eb}"
log("FK cross-check vs Blender pose eval: OK")
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
