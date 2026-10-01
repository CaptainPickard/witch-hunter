"""
rig_wh_humanoid.py -- Witch Hunter humanoid auto-rig + procedural clips (Blender 4.3, bpy).

Pipeline:  import GLB -> detect landmarks from the mesh -> build 20-bone WH rig
           -> automatic (heat) weights + repair -> generate WH_* actions -> export GLB.

Usage (verified form; `blender -b in.glb` does NOT work because Blender tries to
open the .glb as a .blend file):

    scripts/bl.sh --python scripts/rig_wh_humanoid.py -- IN.glb OUT.glb [options]

  where scripts/bl.sh = PATH/LD_PRELOAD fix + `blender -b --factory-startup`.

Options (all optional):
    --clips WH_Idle,WH_Walk,...   subset of clips to generate (default: all in CLIPS)
    --fps 30                      scene/clip frame rate
    --hip-ratio 0.52              hip joint height as fraction of mesh height
    --knee-ratio 0.28             knee height fraction
    --save-blend PATH             also save the rigged .blend (default: OUT with .blend)
    --clips-only                  IN is an already-rigged .blend from a previous run:
                                  skip rigging, (re)generate the requested clips, export.

Conventions (binding, consumed by the Three.js AnimationMixer state machine):
    * Bones: Root, Hips, Spine, Chest, Neck, Head,
             L_/R_ Shoulder, UpperArm, Forearm, Hand, Thigh, Shin, Foot   (20 bones)
      L_ = character's left = +X in Blender (character faces -Y).
      No '.' in names: three.js PropertyBinding strips '.', ':', '/', '[', ']'.
    * Actions: WH_Idle, WH_Walk, WH_Run, WH_Attack1, WH_Hit, WH_Death.
    * In place: Root is never keyed; Hips may bob in Z but loops end where they start.
"""
import bpy
import sys
import math
import os
import numpy as np
from mathutils import Vector, Quaternion, Matrix

# --------------------------------------------------------------------------- args
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if len(argv) < 2:
    raise SystemExit("usage: blender -b --python rig_wh_humanoid.py -- IN OUT.glb [options]")
IN_PATH, OUT_PATH = os.path.abspath(argv[0]), os.path.abspath(argv[1])
opts = {}
i = 2
while i < len(argv):
    key = argv[i].lstrip("-").replace("-", "_")
    if key in ("clips_only",):
        opts[key] = True
        i += 1
    else:
        opts[key] = argv[i + 1]
        i += 2
FPS = int(opts.get("fps", 30))
HIP_RATIO = float(opts.get("hip_ratio", 0.52))
KNEE_RATIO = float(opts.get("knee_ratio", 0.28))
SAVE_BLEND = os.path.abspath(opts.get("save_blend", os.path.splitext(OUT_PATH)[0] + ".blend"))

BONE_NAMES = ["Root", "Hips", "Spine", "Chest", "Neck", "Head"] + [
    f"{s}_{b}" for s in ("L", "R")
    for b in ("Shoulder", "UpperArm", "Forearm", "Hand", "Thigh", "Shin", "Foot")]


def log(*a):
    print("[WH]", *a, flush=True)


# --------------------------------------------------------------------------- import
def import_glb(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=path)
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    if len(meshes) != 1:
        # Meshy exports are a single mesh; if not, join (geometry itself is untouched).
        bpy.ops.object.select_all(action="DESELECT")
        for o in meshes:
            o.select_set(True)
        bpy.context.view_layer.objects.active = meshes[0]
        bpy.ops.object.join()
    mesh = [o for o in bpy.data.objects if o.type == "MESH"][0]
    mesh.name = "WH_Body"
    # Bake any node transform into identity so the rig and mesh share one space.
    bpy.context.view_layer.objects.active = mesh
    mesh.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return mesh


# --------------------------------------------------------------------------- landmarks
def detect_landmarks(mesh):
    """Return dict of joint positions (Blender space, Z up, facing -Y) measured from
    the mesh's own vertex distribution. Ratios are only used for joints that cannot
    be seen in a silhouette (hips, knees)."""
    n = len(mesh.data.vertices)
    V = np.empty(n * 3, np.float64)
    mesh.data.vertices.foreach_get("co", V)
    V = V.reshape(-1, 3)
    z0, z1 = V[:, 2].min(), V[:, 2].max()
    H = z1 - z0

    def band(f0, f1):
        return V[(V[:, 2] >= z0 + f0 * H) & (V[:, 2] < z0 + f1 * H)]

    def half_width(f0, f1):
        s = band(f0, f1)
        return np.percentile(np.abs(s[:, 0]), 99) if len(s) else 0.0

    def core_y(f0, f1):
        s = band(f0, f1)
        s = s[np.abs(s[:, 0]) < 0.08 * H]
        if len(s) < 5:
            return 0.0
        y = 0.5 * (np.percentile(s[:, 1], 5) + np.percentile(s[:, 1], 95))
        return float(np.clip(y, -0.08 * H, 0.08 * H))

    # Shoulder top: scanning down from the head, first slice whose width reaches
    # 75% of the widest upper-torso slice (head/neck are much narrower than shoulders).
    step = 0.0125
    torso_w = max(half_width(f, f + step) for f in np.arange(0.70, 0.85, step))
    shoulder_top = 0.82
    for f in np.arange(0.95, 0.70, -step):
        if half_width(f, f + step) >= 0.75 * torso_w:
            shoulder_top = f + step
            break
    sh_w = half_width(shoulder_top - 0.05, shoulder_top)

    # Hands: the most lateral vertices in the arm band (A-pose hands hang at ~0.4-0.75H).
    def hand(side):
        s = band(0.35, shoulder_top - 0.08)
        s = s[s[:, 0] * side > 0]
        xm = np.abs(s[:, 0]).max()
        pts = s[np.abs(s[:, 0]) > xm - 0.03 * H]
        return Vector(pts.mean(axis=0))

    # Feet: below the shortest cloak/robe the boots are separate blobs.
    def foot(side):
        s = band(0.0, 0.12)
        s = s[s[:, 0] * side > 0.01 * H]
        ankle_s = band(0.05, 0.12)
        ankle_s = ankle_s[ankle_s[:, 0] * side > 0.01 * H]
        x = float(np.median(ankle_s[:, 0])) if len(ankle_s) > 5 else float(np.median(s[:, 0]))
        ay = 0.5 * (ankle_s[:, 1].min() + ankle_s[:, 1].max()) if len(ankle_s) > 5 else 0.0
        toe_y = float(np.percentile(s[:, 1], 2))
        return x, float(ay), toe_y

    L = {"z0": z0, "z1": z1, "H": H, "shoulder_top": shoulder_top}
    zf = lambda f: z0 + f * H
    y_hip, y_chest, y_neck = core_y(HIP_RATIO - .05, HIP_RATIO + .05), core_y(.65, .75), core_y(shoulder_top, shoulder_top + .05)
    y_head = core_y(0.9, 1.0)
    L["hips"] = Vector((0, y_hip, zf(HIP_RATIO)))
    L["spine"] = Vector((0, y_hip, zf(HIP_RATIO + 0.07)))
    L["chest"] = Vector((0, y_chest, zf(0.5 * (HIP_RATIO + 0.07 + shoulder_top))))
    L["neck"] = Vector((0, y_neck, zf(shoulder_top + 0.01)))
    L["head"] = Vector((0, y_neck, zf(shoulder_top + 0.06)))
    L["head_top"] = Vector((0, y_head, z1))
    for side, p in ((1, "L"), (-1, "R")):
        sh_joint = Vector((side * 0.75 * sh_w, y_neck, zf(shoulder_top - 0.035)))
        hnd = hand(side)
        d = (hnd - sh_joint).normalized()
        wrist = hnd - d * 0.035 * H
        elbow = sh_joint.lerp(wrist, 0.5) + Vector((0, 0.015 * H, 0))   # elbow slightly back
        fx, ay, toe_y = foot(side)
        hip_x = side * float(np.clip(0.75 * abs(fx), 0.04 * H, 0.08 * H))
        ankle = Vector((fx, ay, zf(0.06)))
        L[p] = {
            "clav": Vector((side * 0.02 * H, y_neck, zf(shoulder_top - 0.02))),
            "shoulder": sh_joint, "elbow": elbow, "wrist": wrist,
            "hand_tip": hnd + d * 0.035 * H,
            "hip": Vector((hip_x, y_hip, zf(HIP_RATIO - 0.03))),
            "knee": Vector((0.5 * (hip_x + fx), y_hip - 0.015 * H, zf(KNEE_RATIO))),
            "ankle": ankle, "toe": Vector((fx, toe_y, zf(0.01))),
        }
        L[p]["arm_angle_deg"] = math.degrees(math.atan2(abs(d.x), abs(d.z)))
    log(f"bounds z0={z0:.3f} z1={z1:.3f} H={H:.3f} shoulder_top={shoulder_top:.3f}H "
        f"arm angle from vertical L={L['L']['arm_angle_deg']:.1f} R={L['R']['arm_angle_deg']:.1f} deg "
        f"(~0=arms down, 20-50=A-pose, ~90=T-pose)")
    return L


# --------------------------------------------------------------------------- rig
def build_armature(L):
    H = L["H"]
    arm_data = bpy.data.armatures.new("WH_Armature")
    arm = bpy.data.objects.new("WH_Armature", arm_data)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm_data.edit_bones

    def bone(name, head, tail, parent=None, connect=False, deform=True):
        b = eb.new(name)
        b.head, b.tail = head, tail
        b.use_deform = deform
        if parent:
            b.parent = eb[parent]
            b.use_connect = connect
        # Roll: point local Z forward (-Y) where possible, else up. Animation code is
        # roll-independent (see to_local_quat), so roll only matters for future tooling.
        ref = Vector((0, -1, 0)) if abs((tail - head).normalized().y) < 0.9 else Vector((0, 0, 1))
        b.align_roll(ref)
        return b

    bone("Root", Vector((0, 0, L["z0"])), Vector((0, 0, L["z0"] + 0.1 * H)), deform=False)
    bone("Hips", L["hips"], L["spine"], "Root")
    bone("Spine", L["spine"], L["chest"], "Hips", True)
    bone("Chest", L["chest"], L["neck"], "Spine", True)
    bone("Neck", L["neck"], L["head"], "Chest", True)
    bone("Head", L["head"], L["head_top"], "Neck", True)
    for p in ("L", "R"):
        s = L[p]
        bone(f"{p}_Shoulder", s["clav"], s["shoulder"], "Chest")
        bone(f"{p}_UpperArm", s["shoulder"], s["elbow"], f"{p}_Shoulder", True)
        bone(f"{p}_Forearm", s["elbow"], s["wrist"], f"{p}_UpperArm", True)
        bone(f"{p}_Hand", s["wrist"], s["hand_tip"], f"{p}_Forearm", True)
        bone(f"{p}_Thigh", s["hip"], s["knee"], "Hips")
        bone(f"{p}_Shin", s["knee"], s["ankle"], f"{p}_Thigh", True)
        bone(f"{p}_Foot", s["ankle"], s["toe"], f"{p}_Shin", True)
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
    assert sorted(b.name for b in arm_data.bones) == sorted(BONE_NAMES)
    return arm


# --------------------------------------------------------------------------- weights
def weight_stats(mesh):
    """(#vertices with zero total weight, {deform bone: #verts with weight>0})"""
    names = {g.index: g.name for g in mesh.vertex_groups}
    per_bone = {g.name: 0 for g in mesh.vertex_groups}
    zero = 0
    for v in mesh.data.vertices:
        tot = 0.0
        for g in v.groups:
            if g.weight > 0:
                tot += g.weight
                per_bone[names[g.group]] += 1
        if tot <= 1e-6:
            zero += 1
    return zero, per_bone


def seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
    return (p - (a + ab * t)).length


# Arm bones may only influence vertices within this distance (fraction of H) of the bone.
# Heat weighting on the welded proxy lets hand/forearm weights leak into the cloak that
# hangs next to them (cloak then "flies" with the arms in WH_Hit/WH_Death).
ARM_RADIUS = {"UpperArm": 0.07, "Forearm": 0.06, "Hand": 0.06}


def bone_radius(name, H):
    part = name.split("_", 1)[-1]
    return ARM_RADIUS[part] * H if part in ARM_RADIUS else None


def clamp_arm_weights(mesh, arm, H):
    """Remove arm-chain weights from vertices farther than ARM_RADIUS from the bone."""
    removed = 0
    for b in arm.data.bones:
        r = bone_radius(b.name, H)
        g = mesh.vertex_groups.get(b.name)
        if r is None or g is None:
            continue
        far = []
        for v in mesh.data.vertices:
            for vg in v.groups:
                if vg.group == g.index and vg.weight > 0 and seg_dist(v.co, b.head_local, b.tail_local) > r:
                    far.append(v.index)
        if far:
            g.remove(far)
            removed += len(far)
    return removed


def nearest_bone_fill(mesh, arm, only_unweighted=True):
    """Assign weight 1.0 to the nearest deform-bone segment for every vertex with no
    weight. Fallback for heat-weighting failures on open/non-manifold Meshy shells."""
    H = arm.data.bones["Head"].tail_local.z - arm.data.bones["Root"].head_local.z
    segs = [(b.name, b.head_local.copy(), b.tail_local.copy(), bone_radius(b.name, H))
            for b in arm.data.bones if b.use_deform]
    groups = {n: (mesh.vertex_groups.get(n) or mesh.vertex_groups.new(name=n)) for n, _, _, _ in segs}
    filled = 0
    for v in mesh.data.vertices:
        if only_unweighted and any(g.weight > 0 for g in v.groups):
            continue
        best, bd = None, 1e9
        for n, a, b, r in segs:
            d = seg_dist(v.co, a, b)
            if r is not None and d > r:      # respect arm radius limits
                continue
            if d < bd:
                best, bd = n, d
        groups[best].add([v.index], 1.0, "REPLACE")
        filled += 1
    return filled


def coords_hash(mesh):
    co = np.empty(len(mesh.data.vertices) * 3, np.float32)
    mesh.data.vertices.foreach_get("co", co)
    return hash(co.tobytes())


def select_only(*objs, active=None):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = active or objs[0]


def heat_weight_proxy(mesh, arm, H):
    """Bone Heat on the raw Meshy mesh FAILS for every bone ("failed to find solution")
    -- open, unwelded shells. Verified workaround: on a throw-away COPY, weld by distance
    and scale x10 (heat solver has absolute-size thresholds), heat-weight that, scale
    back. Returns the weighted proxy object. The visible mesh is never modified."""
    proxy = bpy.data.objects.new("WH_WeightProxy", mesh.data.copy())
    bpy.context.scene.collection.objects.link(proxy)
    tmp_arm = bpy.data.objects.new("WH_TmpArm", arm.data.copy())
    bpy.context.scene.collection.objects.link(tmp_arm)
    select_only(proxy)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=0.002 * H)       # weld -- proxy only
    bpy.ops.object.mode_set(mode="OBJECT")
    for o in (proxy, tmp_arm):
        o.scale = (10, 10, 10)
    select_only(proxy, tmp_arm, active=tmp_arm)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")       # Bone Heat weighting
    zero, _ = weight_stats(proxy)
    log(f"heat weights on proxy: {zero} / {len(proxy.data.vertices)} proxy vertices unweighted")
    for m in list(proxy.modifiers):
        proxy.modifiers.remove(m)
    proxy.parent = None
    proxy.scale = (0.1, 0.1, 0.1)
    select_only(proxy)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.data.objects.remove(tmp_arm)
    return proxy


def skin(mesh, arm):
    H = arm.data.bones["Head"].tail_local.z - arm.data.bones["Root"].head_local.z
    before = coords_hash(mesh)
    proxy = heat_weight_proxy(mesh, arm, H)
    # Transfer weights proxy -> real mesh (interpolated from nearest proxy face).
    for b in arm.data.bones:
        if b.use_deform and b.name not in mesh.vertex_groups:
            mesh.vertex_groups.new(name=b.name)
    dt = mesh.modifiers.new("WH_WeightTransfer", "DATA_TRANSFER")
    dt.object = proxy
    dt.use_vert_data = True
    dt.data_types_verts = {"VGROUP_WEIGHTS"}
    dt.vert_mapping = "POLYINTERP_NEAREST"
    dt.layers_vgroup_select_src = "ALL"
    dt.layers_vgroup_select_dst = "NAME"
    select_only(mesh)
    bpy.ops.object.modifier_apply(modifier=dt.name)
    bpy.data.objects.remove(proxy)
    zero, per_bone = weight_stats(mesh)
    log(f"transferred weights: {zero} / {len(mesh.data.vertices)} vertices unweighted")
    log(f"arm radius clamp removed {clamp_arm_weights(mesh, arm, H)} arm-bone weights")
    zero, per_bone = weight_stats(mesh)
    empty = [b for b in BONE_NAMES if b != "Root" and per_bone.get(b, 0) == 0]
    if empty:
        log("WARNING bones with no weighted vertices:", empty)
    if zero:
        log(f"nearest-bone fill assigned {nearest_bone_fill(mesh, arm)} vertices")
    # Bind: parent + Armature modifier, keeping the vertex groups we just made.
    select_only(mesh, arm, active=arm)
    bpy.ops.object.parent_set(type="ARMATURE")
    assert coords_hash(mesh) == before, "mesh geometry changed during skinning!"
    select_only(mesh)
    bpy.ops.object.vertex_group_clean(group_select_mode="ALL", limit=0.01)
    zero, _ = weight_stats(mesh)
    if zero:   # cleaning can zero out vertices that only had tiny weights
        nearest_bone_fill(mesh, arm)
    # glTF / three.js skinning uses 4 influences per vertex: limit + normalize here so
    # what we validate is what ships.
    select_only(mesh)
    bpy.ops.object.vertex_group_limit_total(group_select_mode="ALL", limit=4)
    bpy.ops.object.vertex_group_normalize_all(group_select_mode="ALL", lock_active=False)
    zero, per_bone = weight_stats(mesh)
    log(f"final weights: {zero} unweighted; per-bone vertex counts: {per_bone}")
    if zero:
        raise RuntimeError(f"{zero} vertices still unweighted")


# --------------------------------------------------------------------------- clips
# A pose is {bone: {"rx": deg, "ry": deg, "rz": deg, "lx": H, "ly": H, "lz": H}}.
# Rotations are about the ARMATURE axes (X = character's left, -Y = forward, Z = up),
# evaluated in each bone's parent frame, so they are independent of bone roll:
#   rx > 0 : bone tip goes toward -Y for an up-pointing bone (spine leans FORWARD),
#            toward +Y for a down-pointing bone (thigh/arm swing BACK, knee BEND).
#   ry     : side bend.  For L_ limbs (pointing down) ry < 0 lifts the arm outward;
#            use the `S` side sign below so L/R are mirrored automatically.
#   rz > 0 : yaw to the character's right... (turns the chest counter-clockwise seen from above)
# Locations are in units of mesh height H, armature space (only Hips should move).

def S(side):
    return 1.0 if side == "L" else -1.0


def smooth(a, b, t):
    t = t * t * (3 - 2 * t)
    return a + (b - a) * t


def keyposes(keys):
    """keys: [(time_fraction, pose)] -> pose(t) with smoothstep between keys."""
    def f(t):
        for (t0, p0), (t1, p1) in zip(keys, keys[1:]):
            if t0 <= t <= t1:
                u = (t - t0) / (t1 - t0) if t1 > t0 else 1.0
                out = {}
                for bn in set(p0) | set(p1):
                    c0, c1 = p0.get(bn, {}), p1.get(bn, {})
                    out[bn] = {ch: smooth(c0.get(ch, 0.0), c1.get(ch, 0.0), u) for ch in set(c0) | set(c1)}
                return out
        return keys[-1][1]
    return f


def pose_idle(t):
    b = math.sin(2 * math.pi * t)            # one breath per loop
    p = {"Chest": {"rx": -1.5 * b}, "Spine": {"rx": 0.8 * b},
         "Neck": {"rx": 0.8 * b}, "Head": {"rx": -0.5 * b, "rz": 1.5 * math.sin(2 * math.pi * t + 1)},
         "Hips": {"lz": -0.002 * (1 - b)}}
    for s in ("L", "R"):
        p[f"{s}_Shoulder"] = {"ry": -S(s) * 1.5 * b}
        p[f"{s}_UpperArm"] = {"rx": 1.5 * b}
        p[f"{s}_Forearm"] = {"rx": -6 - 2 * b}
    return p


def gait(t, stride, knee, arm, elbow, bob, lean, yaw, counter_yaw, foot_pitch):
    """Shared walk/run cycle; angular amplitudes in radians, poses in degrees."""
    ph = 2 * math.pi * t
    p = {"Hips": {"lz": bob * math.cos(2 * ph), "rz": math.degrees(yaw * math.sin(ph))},
         "Spine": {"rx": math.degrees(lean * 0.35)},
         "Chest": {"rx": math.degrees(lean), "rz": math.degrees(-counter_yaw * math.sin(ph))},
         "Head": {"rx": math.degrees(-lean * 0.6)}}
    for s, off in (("L", 0.0), ("R", math.pi)):
        q = ph + off
        p[f"{s}_Thigh"] = {"rx": math.degrees(-stride * math.sin(q))}
        p[f"{s}_Shin"] = {"rx": math.degrees(knee * max(0.0, math.cos(q)) ** 1.5)}
        p[f"{s}_Foot"] = {"rx": math.degrees(foot_pitch * math.sin(q))}
        p[f"{s}_UpperArm"] = {"rx": math.degrees(arm * math.sin(q))}  # counters same-side leg
        p[f"{s}_Forearm"] = {"rx": math.degrees(-elbow * (1 + 0.4 * max(0.0, -math.sin(q))))}
    return p


def pose_walk(t):
    return gait(t, stride=0.45, knee=0.55, arm=0.25, elbow=0.20,
                bob=0.010, lean=0.04, yaw=0.12, counter_yaw=0.08, foot_pitch=0.25)


def pose_run(t):
    return gait(t, stride=0.75, knee=0.90, arm=0.60, elbow=1.13,
                bob=0.022, lean=0.18, yaw=0.14, counter_yaw=0.10, foot_pitch=0.25)


R_WINDUP = {"R_UpperArm": {"rx": math.degrees(-1.9), "ry": 15}, "R_Forearm": {"rx": -70},
            "Chest": {"rz": math.degrees(-0.35), "rx": -6}, "Spine": {"rx": -5},
            "L_UpperArm": {"rx": math.degrees(-1.1)}, "R_Thigh": {"rx": 6}, "L_Thigh": {"rx": -8}}
R_STRIKE = {"R_UpperArm": {"rx": math.degrees(1.1), "ry": 5}, "R_Forearm": {"rx": -10}, "R_Hand": {"rx": 15},
            "Chest": {"rz": math.degrees(0.55), "rx": 10}, "Spine": {"rx": 10}, "Head": {"rx": -8},
            "L_UpperArm": {"rx": math.degrees(1.1)}, "Hips": {"lz": -0.02},
            "R_Thigh": {"rx": 12}, "R_Shin": {"rx": 15}, "L_Thigh": {"rx": -14}, "L_Shin": {"rx": 18}}
# Windup/strike/recover boundaries match the 0.30/0.25/0.45 CONFIG fractions.
pose_attack1 = keyposes([(0.0, {}), (0.30, R_WINDUP), (0.55, R_STRIKE), (1.0, {})])

HIT = {"Spine": {"rx": -10}, "Chest": {"rx": math.degrees(-0.35), "rz": 8}, "Neck": {"rx": -8}, "Head": {"rx": -15, "rz": -10},
       "L_UpperArm": {"rx": -20, "ry": -15}, "R_UpperArm": {"rx": -25, "ry": 15},
       "L_Forearm": {"rx": -30}, "R_Forearm": {"rx": -30}, "Hips": {"lz": -0.01}}
pose_hit = keyposes([(0.0, {}), (0.25, HIT), (1.0, {})])


def pose_death_builder(L):
    H = L["H"]
    drop = (L["hips"].z - L["z0"]) / H - 0.07      # hips end ~0.07H above the floor
    buckle = {"Hips": {"lz": -0.12, "rx": -10}, "Spine": {"rx": 15}, "Head": {"rx": 15},
              "L_Thigh": {"rx": -35}, "R_Thigh": {"rx": -20}, "L_Shin": {"rx": 60}, "R_Shin": {"rx": 45},
              "L_UpperArm": {"rx": -15, "ry": -20}, "R_UpperArm": {"rx": -15, "ry": 20}}
    down = {"Hips": {"lz": -drop, "rx": -88}, "Spine": {"rx": -4}, "Neck": {"rx": -5}, "Head": {"rx": -10, "rz": 25},
            "L_Thigh": {"rx": 4, "ry": -8}, "R_Thigh": {"rx": 2, "ry": 10}, "L_Shin": {"rx": 6}, "R_Shin": {"rx": 10},
            "L_Foot": {"rx": 40}, "R_Foot": {"rx": 40},
            "L_UpperArm": {"rx": -10, "ry": -55}, "R_UpperArm": {"rx": -20, "ry": 50},
            "L_Forearm": {"rx": -20}, "R_Forearm": {"rx": -35}}
    return keyposes([(0.0, {}), (0.3, buckle), (0.75, down), (1.0, down)])


# name -> (pose function factory(landmarks), duration seconds, loop?)
# TO ADD A CLIP: write pose_xxx(t) (t = 0..1 over the clip), register it here with a
# WH_ name, then rerun this script (full rebuild) or use --clips-only on the saved .blend.
CLIPS = {
    "WH_Idle":    (lambda L: pose_idle,    2.0,  True),
    "WH_Walk":    (lambda L: pose_walk,    1.0,  True),
    "WH_Run":     (lambda L: pose_run,     0.6,  True),
    "WH_Attack1": (lambda L: pose_attack1, 0.5,  False),
    "WH_Hit":     (lambda L: pose_hit,     10 / 30, False),
    "WH_Death":   (pose_death_builder,     1.2,  False),
}


def to_local_quat(pb, rx, ry, rz):
    """Armature-axis rotation (deg) -> pose-bone local quaternion (conjugate by rest)."""
    q = (Quaternion((0, 0, 1), math.radians(rz)) @ Quaternion((0, 1, 0), math.radians(ry))
         @ Quaternion((1, 0, 0), math.radians(rx)))
    rest = pb.bone.matrix_local.to_quaternion()
    return rest.inverted() @ q @ rest


def bake_clip(arm, L, name, pose_fn, duration, loop):
    H = L["H"]
    frames = max(2, round(duration * FPS))
    act = bpy.data.actions.get(name)
    if act:
        bpy.data.actions.remove(act)
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    arm.animation_data_create()
    arm.animation_data.action = act
    animated = [pb for pb in arm.pose.bones if pb.name != "Root"]   # Root is never keyed
    for f in range(frames + 1):
        t = f / frames
        pose = pose_fn(0.0 if (loop and f == frames) else t)          # loops: last key == first
        for pb in animated:
            c = pose.get(pb.name, {})
            pb.rotation_quaternion = to_local_quat(pb, c.get("rx", 0), c.get("ry", 0), c.get("rz", 0))
            delta = Vector((c.get("lx", 0), c.get("ly", 0), c.get("lz", 0))) * H
            pb.location = pb.bone.matrix_local.to_3x3().inverted() @ delta
            pb.keyframe_insert("rotation_quaternion", frame=f + 1, group=pb.name)
            if pb.name == "Hips":
                pb.keyframe_insert("location", frame=f + 1, group=pb.name)
    # Every frame is keyed, so linear interpolation reproduces the sampled curve.
    for fc in act.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
    # Each action on its own NLA track so the glTF exporter (mode ACTIONS) emits it.
    tr = arm.animation_data.nla_tracks.new()
    tr.name = name
    tr.strips.new(name, 1, act)
    tr.mute = True
    arm.animation_data.action = None
    log(f"clip {name}: {frames + 1} keys @ {FPS} fps = {frames / FPS:.3f}s loop={loop}")


def generate_clips(arm, L, names):
    bpy.context.scene.render.fps = FPS
    ad = arm.animation_data
    if ad:   # drop old NLA tracks for clips we are regenerating
        for tr in list(ad.nla_tracks):
            if tr.name in names:
                ad.nla_tracks.remove(tr)
    for n in names:
        factory, dur, loop = CLIPS[n]
        bake_clip(arm, L, n, factory(L), dur, loop)
    for pb in arm.pose.bones:   # leave rest pose active
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)


# --------------------------------------------------------------------------- export
def export_glb(path):
    bpy.ops.export_scene.gltf(
        filepath=path, export_format="GLB",
        export_animation_mode="ACTIONS",   # every action -> one glTF animation (clip)
        export_skins=True, export_def_bones=False,
        export_apply=False,                # NEVER apply modifiers: would bake the armature
        export_image_format="AUTO",        # keep source JPEG/PNG bytes (verified bit-exact)
        export_yup=True, export_force_sampling=True,
        export_optimize_animation_size=False,
        export_anim_slide_to_zero=True,
        export_reset_pose_bones=True,
        export_extras=False, export_cameras=False, export_lights=False)
    log(f"exported {path} ({os.path.getsize(path) / 1e6:.2f} MB)")


# --------------------------------------------------------------------------- main
def main():
    names = opts["clips"].split(",") if "clips" in opts else list(CLIPS)
    unknown = [n for n in names if n not in CLIPS]
    if unknown:
        raise SystemExit(f"unknown clips {unknown}; known: {list(CLIPS)}")
    if opts.get("clips_only"):
        bpy.ops.wm.open_mainfile(filepath=IN_PATH)
        arm = bpy.data.objects["WH_Armature"]
        mesh = bpy.data.objects["WH_Body"]
        L = detect_landmarks(mesh)     # same mesh -> same landmarks (used by WH_Death drop)
    else:
        mesh = import_glb(IN_PATH)
        L = detect_landmarks(mesh)
        arm = build_armature(L)
        skin(mesh, arm)
    generate_clips(arm, L, names)
    bpy.ops.wm.save_as_mainfile(filepath=SAVE_BLEND)
    log(f"saved {SAVE_BLEND}")
    export_glb(OUT_PATH)


main()
