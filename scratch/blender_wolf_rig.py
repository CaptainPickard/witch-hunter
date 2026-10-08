"""
blender_wolf_rig.py -- WOLF-RIG round (io/missions/2026-10-08-wolf-rig.md).
Skeleton + capsule-region skin + 6 WH_Wolf_* clips on the RAW Meshy wolf
(Blender 4.5 headless, bpy). Adapted from scratch/blender_chain_clips.py
(KEYS pattern, armature-axis FK, Hermite keys, Nelder-Mead pose solve, LINEAR
bake of every frame, Root identity on every frame).

    /opt/blender-4.5.4-linux-x64/blender --background --factory-startup \
        --python scratch/blender_wolf_rig.py -- RAW.glb OUT.glb [--log OUT.json]

RAW is only READ (glTF import); nothing is ever written next to it.

Measured orientation (raw glTF, printed again at run time):
  head/snout + ears at glTF +Z (z 0.75..1.0, ear tips y 0.596), tail at -Z
  (tip z -1.0, y -0.37), up = +Y (paw soles y -0.593 = ground), wolf's LEFT
  = +X (x is mirror-symmetric, |x| <= 0.20).  Blender import maps glTF
  (x, y, z) -> (x, -z, y), so in Blender: X = wolf's left, -Y = forward,
  Z = up -- the same armature convention as the humanoid rigs.

Pose convention (same as blender_chain_clips.py): {bone: {rx, ry, rz (deg),
lx, ly, lz, s}}; q = Rz @ Ry @ Rx about ARMATURE axes at the bone head in the
parent's posed frame. For down-pointing legs rx > 0 swings the leg BACK; for
forward bones (spine/head/jaw) rx > 0 pitches the tip DOWN; ry < 0 rolls the
body onto its RIGHT side; rz > 0 yaws a forward bone to the wolf's LEFT.
`s` = uniform scale (Idle breathing only; children counter-scaled).

Skin: capsule-region rule. Each deform bone = capsule (segment + radius).
nd = distance / radius. Region bone = argmin nd over the bones whose spatial
mask admits the vertex (side masks for legs, tail box, no Jaw outside the
mouth slab, no Head/Neck behind the shoulders). Only region + parent +
children may keep weight. u_i = nd_region / nd_i; w_i = ((u_i - 0.65) /
0.35)^2 for u_i > 0.65, else 0 -> rigid to the region bone whenever every
neighbour is beyond 1/0.65 of the region distance, smooth (continuous) blend
near joints. Max 4 influences, normalized. Jaw = explicit mouth slab (under
the measured lip line, z > 0.74) ramped in over z 0.74..0.80. Weights are a
pure function of position, so coincident (UV-seam-split) vertices get
identical weights -- no seam tearing.
"""
import bpy
import sys
import os
import math
import json
import numpy as np
from mathutils import Vector, Quaternion, Matrix

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if len(argv) < 2:
    raise SystemExit("usage: blender --background --python blender_wolf_rig.py -- RAW.glb OUT.glb [--log X.json]")
IN_PATH = os.path.abspath(argv[0])
OUT_PATH = os.path.abspath(argv[1])
opts = {}
rest_args = argv[2:]
for i in range(0, len(rest_args), 2):
    opts[rest_args[i].lstrip("-")] = rest_args[i + 1]

FPS = 30
GROUND = -0.593273          # raw glTF y min (paw soles) == Blender z min
REPORT = {}


def log(*a):
    print("[WOLF]", *a, flush=True)


def B(g):
    """glTF (x, y, z) -> Blender (x, -z, y)."""
    return Vector((g[0], -g[2], g[1]))


# --------------------------------------------------------------------- skeleton (glTF coords, measured)
# name: (head, tail, parent). Left legs at +X; right legs mirrored.
SKELETON = [
    ("Root",  (0, 0, 0), (0, 0.10, 0), None),
    ("Spine", (0, 0.15, -0.58), (0, 0.18, -0.10), "Root"),
    ("Chest", (0, 0.18, -0.10), (0, 0.25, 0.38), "Spine"),
    ("Neck",  (0, 0.25, 0.38), (0, 0.40, 0.64), "Chest"),
    ("Head",  (0, 0.40, 0.64), (0, 0.32, 0.98), "Neck"),
    ("Jaw",   (0, 0.265, 0.74), (0, 0.225, 0.96), "Head"),
    ("Tail1", (0, 0.27, -0.72), (0, 0.12, -0.84), "Spine"),
    ("Tail2", (0, 0.12, -0.84), (0, -0.08, -0.90), "Tail1"),
    ("Tail3", (0, -0.08, -0.90), (0, -0.36, -0.985), "Tail2"),
]
LEG_FRONT = [((0.11, 0.08, 0.34), (0.11, -0.12, 0.27)),
             ((0.11, -0.12, 0.27), (0.105, -0.47, 0.31)),
             ((0.105, -0.47, 0.31), (0.12, -0.575, 0.45))]
LEG_HIND = [((0.12, 0.10, -0.55), (0.12, -0.12, -0.50)),
            ((0.12, -0.12, -0.50), (0.115, -0.32, -0.69)),
            ((0.115, -0.32, -0.69), (0.12, -0.575, -0.53))]
for pre, segs, par in (("FL", LEG_FRONT, "Chest"), ("FR", LEG_FRONT, "Chest"),
                       ("BL", LEG_HIND, "Spine"), ("BR", LEG_HIND, "Spine")):
    sx = 1 if pre[1] == "L" else -1
    p = par
    for part, (h, t) in zip(("UpperLeg", "Leg", "Foot"), segs):
        SKELETON.append((f"{pre}_{part}", (sx * h[0], h[1], h[2]), (sx * t[0], t[1], t[2]), p))
        p = f"{pre}_{part}"
BONES = [s[0] for s in SKELETON]                  # parent-before-child
PARENT = {s[0]: s[3] for s in SKELETON}
CHILDREN = {b: [c for c in BONES if PARENT[c] == b] for b in BONES}
LEGS = ("FL", "FR", "BL", "BR")
CLIP_SPEC = {"WH_Wolf_Idle": 3.0, "WH_Wolf_Walk": 1.0, "WH_Wolf_Run": 0.55,
             "WH_Wolf_Attack1": 0.7, "WH_Wolf_Hit": 0.4, "WH_Wolf_Death": 1.1}

# --------------------------------------------------------------------- import
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=IN_PATH)
scene = bpy.context.scene
scene.render.fps = FPS
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
assert len(meshes) == 1, [o.name for o in meshes]
body = meshes[0]
body.name = "WH_Wolf_Body"
assert body.matrix_world == Matrix.Identity(4), body.matrix_world
assert body.parent is None
NV = len(body.data.vertices)
V = np.empty(NV * 3)
body.data.vertices.foreach_get("co", V)
V = V.reshape(-1, 3)
G = np.stack([V[:, 0], V[:, 2], -V[:, 1]], 1)     # back to glTF coords for masks
log(f"raw mesh: {NV} verts, {len(body.data.polygons)} polys")

# orientation measurement (head cluster = the z end holding the ear tips)
front = G[G[:, 2] > 0.6]
back = G[G[:, 2] < -0.6]
orient = {"front_z>0.6_ymax": round(float(front[:, 1].max()), 3), "back_z<-0.6_ymax": round(float(back[:, 1].max()), 3),
          "ground_y": round(float(G[:, 1].min()), 6), "x_range": [round(float(G[:, 0].min()), 3), round(float(G[:, 0].max()), 3)],
          "snout_tip_z": round(float(G[:, 2].max()), 3), "tail_tip_z": round(float(G[:, 2].min()), 3)}
assert orient["front_z>0.6_ymax"] > 0.55 and orient["back_z<-0.6_ymax"] < 0.40, orient
orient["mapping"] = "head=+Z(glTF)/-Y(Blender), up=+Y/+Z, wolf-left=+X"
REPORT["orientation"] = orient
log("orientation:", orient)

# --------------------------------------------------------------------- armature
arm_data = bpy.data.armatures.new("WH_Wolf_Armature")
arm = bpy.data.objects.new("WH_Wolf_Armature", arm_data)
scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
arm.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
for name, h, t, par in SKELETON:
    eb = arm_data.edit_bones.new(name)
    eb.head, eb.tail = B(h), B(t)
    eb.roll = 0.0
    if par:
        eb.parent = arm_data.edit_bones[par]
        eb.use_connect = (arm_data.edit_bones[par].tail - eb.head).length < 1e-6
    eb.use_deform = True
bpy.ops.object.mode_set(mode="OBJECT")
assert [b.name for b in arm_data.bones] == BONES or sorted(b.name for b in arm_data.bones) == sorted(BONES)
REST = {}
for b in arm.data.bones:
    REST[b.name] = {"head": b.head_local.copy(), "tail": b.tail_local.copy(),
                    "rot": b.matrix_local.to_quaternion(), "parent": b.parent.name if b.parent else None}


# --------------------------------------------------------------------- skin (capsule-region rule)
def seg_dist_np(P, a, b):
    ab = b - a
    t = np.clip(((P - a) @ ab) / (ab @ ab), 0.0, 1.0)
    return np.linalg.norm(P - (a + t[:, None] * ab), axis=1)


RADIUS = {"Spine": 0.20, "Chest": 0.22, "Neck": 0.15, "Head": 0.13, "Jaw": 0.05,
          "Tail1": 0.10, "Tail2": 0.08, "Tail3": 0.07}
for pre in LEGS:
    front_leg = pre[0] == "F"
    RADIUS[f"{pre}_UpperLeg"] = 0.08 if front_leg else 0.10
    RADIUS[f"{pre}_Leg"] = 0.05 if front_leg else 0.06
    RADIUS[f"{pre}_Foot"] = 0.05
DEFORM = [b for b in BONES if b != "Root"]
x, y, z = G[:, 0], G[:, 1], G[:, 2]
MOUTH_Y = 0.247 + 0.08 * (0.95 - z)                 # measured lip line (head zoom render)
jaw_slab = (z > 0.74) & (y < MOUTH_Y) & (y > 0.17)


def mask(bn):
    if bn == "Jaw":
        return np.zeros(NV, bool)                    # explicit slab below
    if bn.startswith("Tail"):
        return (z < -0.68) & (np.abs(x) < 0.12) & ((y > 0.0) | (z < -0.78))
    if bn in ("Head",):
        return z > 0.55
    if bn == "Neck":
        return z > 0.20
    if bn[:2] in LEGS:
        side = (x > -0.01) if bn[1] == "L" else (x < 0.01)
        zone = (z > 0.0) if bn[0] == "F" else (z < -0.25)
        return side & zone & (y < 0.25)
    return np.ones(NV, bool)


ND = np.full((NV, len(DEFORM)), np.inf)
for j, bn in enumerate(DEFORM):
    d = seg_dist_np(G, np.array(dict((s[0], s[1]) for s in SKELETON)[bn], float),
                    np.array(dict((s[0], s[2]) for s in SKELETON)[bn], float)) / RADIUS[bn]
    m = mask(bn)
    ND[m, j] = d[m]
region = ND.argmin(1)
W = np.zeros((NV, len(DEFORM)))
idx = {b: j for j, b in enumerate(DEFORM)}
for j, bn in enumerate(DEFORM):
    sel = region == j
    if not sel.any():
        continue
    allowed = [bn] + ([PARENT[bn]] if PARENT[bn] in idx else []) + CHILDREN[bn]
    cols = [idx[a] for a in allowed]
    nd = ND[np.ix_(sel, cols)]
    u = nd[:, :1] / np.maximum(nd, 1e-9)            # region column -> 1
    w = np.where(u > 0.65, ((u - 0.65) / 0.35) ** 2, 0.0)
    W[np.ix_(np.where(sel)[0], cols)] = w
# Jaw slab: ramp in from the mouth corner, taking weight from the head side
s = np.clip((z - 0.74) / 0.06, 0, 1)
s = s * s * (3 - 2 * s)
s = np.where(jaw_slab, s, 0.0)
W = W * (1 - s)[:, None]
W[:, idx["Jaw"]] += s
# top-4 + normalize
order = np.argsort(-W, 1)
keep = np.zeros_like(W, bool)
np.put_along_axis(keep, order[:, :4], True, 1)
W = np.where(keep, W, 0.0)
W = W / W.sum(1, keepdims=True)
assert np.isfinite(W).all() and (W.sum(1) > 0.999).all()
# law checks: jaw/tail never on neck/chest territory
jaw_bad = int(((W[:, idx["Jaw"]] > 0) & ~jaw_slab).sum())
tail_cols = [idx[t] for t in ("Tail1", "Tail2", "Tail3")]
tail_bad = int(((W[:, tail_cols].sum(1) > 0) & (z > -0.68)).sum())
assert jaw_bad == 0 and tail_bad == 0, (jaw_bad, tail_bad)
for bn in DEFORM:
    g = body.vertex_groups.new(name=bn)
    col = W[:, idx[bn]]
    nz = np.where(col > 0)[0]
    for i in nz:
        g.add([int(i)], float(col[i]), "REPLACE")
per_bone = {bn: int((W[:, idx[bn]] > 0).sum()) for bn in DEFORM}
rigid = int((W.max(1) > 0.9999).sum())
infl = np.bincount((W > 0).sum(1), minlength=5).tolist()
REPORT["skin"] = {"per_bone_verts": per_bone, "rigid_verts": rigid, "influence_hist": infl,
                  "jaw_slab_verts": int(jaw_slab.sum()), "jaw_outside_slab": jaw_bad, "tail_in_body": tail_bad}
log("skin:", REPORT["skin"])
assert all(per_bone[b] > 0 for b in DEFORM), per_bone

body.parent = arm
mod = body.modifiers.new("Armature", "ARMATURE")
mod.object = arm
mod.use_vertex_groups = True


# --------------------------------------------------------------------- FK (from blender_chain_clips.py)
def axis_quat(c):
    return (Quaternion((0, 0, 1), math.radians(c.get("rz", 0.0)))
            @ Quaternion((0, 1, 0), math.radians(c.get("ry", 0.0)))
            @ Quaternion((1, 0, 0), math.radians(c.get("rx", 0.0))))


def fk(pose, need=None):
    """Deformation (Q, t) per bone: x -> Q x + t (armature space). Ignores `s`
    (only Idle breathing scales; legs are never solved there)."""
    D = {}
    for name in BONES:
        if need is not None and name not in need:
            continue
        r = REST[name]
        c = pose.get(name, {})
        q = axis_quat(c)
        h = r["head"]
        d = Vector((c.get("lx", 0.0), c.get("ly", 0.0), c.get("lz", 0.0)))
        if r["parent"]:
            Qp, tp = D[r["parent"]]
        else:
            Qp, tp = Quaternion(), Vector()
        D[name] = (Qp @ q, Qp @ (d + h - q @ h) + tp)
    return D


def chain(bn):
    out = []
    while bn:
        out.append(bn)
        bn = PARENT[bn]
    return set(out)


LEG_NEED = {pre: chain(f"{pre}_Foot") for pre in LEGS}


def paw(pose, pre):
    D = fk(pose, LEG_NEED[pre])
    Q, t = D[f"{pre}_Foot"]
    r = REST[f"{pre}_Foot"]
    return Q @ r["tail"] + t, (Q @ (r["tail"] - r["head"])).normalized()


REST_PAW = {pre: (REST[f"{pre}_Foot"]["tail"].copy(), (REST[f"{pre}_Foot"]["tail"] - REST[f"{pre}_Foot"]["head"]).normalized())
            for pre in LEGS}


def nelder_mead(f, x0, step=12.0, iters=1500, tol=1e-10):
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


def solve_leg(pose, pre, target, foot_pitch=0.0, flat_w=0.02, guess=(0.0, 0.0, 0.0, 0.0)):
    """Pose-solve (the chain_clips arm-solver pattern): place the paw tip on
    `target` (armature space) with the paw pitched `foot_pitch` deg from rest
    (rx > 0 = paw curls back). DOF: UpperLeg rx + ry (abduction, follows the
    body's roll/yaw), Leg rx, Foot rx. Fills pose in place; returns error (m)."""
    tp = Vector(target)
    fd = (Quaternion((1, 0, 0), math.radians(foot_pitch)) @ REST_PAW[pre][1]).normalized()
    slots = ((f"{pre}_UpperLeg", "rx"), (f"{pre}_Leg", "rx"), (f"{pre}_Foot", "rx"), (f"{pre}_UpperLeg", "ry"))
    guess = list(guess) + [0.0] * (4 - len(guess))
    front_leg = pre[0] == "F"

    def build(xv):
        for (bn, cn), v in zip(slots, xv):
            pose.setdefault(bn, {})[cn] = v
        return pose

    def cost(xv):
        p, d = paw(build(xv), pre)
        c = 400.0 * (p - tp).length_squared + flat_w * (d - fd).length_squared
        for v in xv[:3]:
            c += 2e-7 * v * v                        # prefer the bind configuration (no branch drift)
        c += 1e-4 * xv[3] ** 2                       # abduction only as needed
        # elbow flexes with the forearm swinging FORWARD (rx < 0); the stifle with
        # the shin swinging BACK (rx > 0): soft limits on hyperextension + over-flex
        flex = -xv[1] if front_leg else xv[1]
        c += 1e-3 * max(0.0, -flex - 10) ** 2
        c += 1e-3 * max(0.0, flex - 80) ** 2
        c += 1e-3 * max(0.0, abs(xv[0]) - 45) ** 2  # shoulder/hip swing limit
        return c

    best = None
    for start in (guess, [0.0, 0.0, 0.0, 0.0]):    # previous frame + bind pose starts
        for st in (10.0, 25.0):
            xv, v = nelder_mead(cost, list(start), step=st, iters=3000)
            xv, v = nelder_mead(cost, xv, step=3.0, iters=3000)
            xv, v = nelder_mead(cost, xv, step=0.5, iters=3000)
            if best is None or v < best[1]:
                best = (xv, v)
    build(best[0])
    p, d = paw(pose, pre)
    return (p - tp).length


def leg_state(pose, pre):
    return (pose[f"{pre}_UpperLeg"]["rx"], pose[f"{pre}_Leg"]["rx"], pose[f"{pre}_Foot"]["rx"],
            pose[f"{pre}_UpperLeg"].get("ry", 0.0))


def merge(*ps):
    out = {}
    for p in ps:
        for bn, c in p.items():
            out.setdefault(bn, {}).update(c)
    return out


def plant(pose, legs=LEGS, guesses=None):
    """Keep paws on their rest footprints while the body moves (attack/hit)."""
    err = 0.0
    for pre in legs:
        g = (guesses or {}).get(pre, (0.0, 0.0, 0.0, 0.0))
        e = solve_leg(pose, pre, REST_PAW[pre][0], 0.0, 5.0, g)   # paw orientation locked
        if os.environ.get("WOLF_DEBUG"):
            log("plant", pre, f"{e * 100:.2f}cm", [round(v, 1) for v in leg_state(pose, pre)])
        err = max(err, e)
    return err


def legs_flat(pose, legs=LEGS):
    for pre in legs:
        for part in ("UpperLeg", "Leg", "Foot"):
            pose.setdefault(f"{pre}_{part}", {})
    return pose


# --------------------------------------------------------------------- clips (KEYS)
KEYS = {}
TAU = 2 * math.pi


def smooth01(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def gait_paw(pre, ph, stride, lift, duty):
    """In-place paw tip target (armature space) at leg phase ph in [0,1):
    stance sweeps the sole back along the ground, swing arcs it forward."""
    rest = REST_PAW[pre][0]
    if ph < duty:
        f = stride / 2 - stride * (ph / duty)
        h = 0.0
        u = ph / duty
        pitch = 25.0 * max(0.0, (u - 0.75) / 0.25)          # heel-off before lift
    else:
        u = (ph - duty) / (1 - duty)
        f = -stride / 2 + stride * smooth01(u)
        h = lift * math.sin(math.pi * u)
        pitch = 25.0 + 45.0 * math.sin(math.pi * min(1.0, u * 1.3)) if pre[0] == "F" else -15.0 * math.sin(math.pi * u)
        pitch *= (1 - smooth01((u - 0.7) / 0.3))
    return Vector((rest.x, rest.y - f, rest.z + h)), pitch


def solve_gait(pose, ph, gait, prev):
    """Per-frame pose-solve of all four paws onto their in-place gait path."""
    worst = 0.0
    for pre in LEGS:
        off, stride, lift, duty = gait[pre]
        tgt, pitch = gait_paw(pre, (ph + off) % 1.0, stride, lift, duty)
        worst = max(worst, solve_leg(pose, pre, tgt, pitch, 0.02, prev.get(pre, (0.0, 0.0, 0.0, 0.0))))
        prev[pre] = leg_state(pose, pre)
    return worst


def body_keys(n, body_fn):
    """n evenly spaced phase keys of the BODY (+ the wrap key == key 0);
    legs are solved per baked frame (solve_gait)."""
    keys = [(k / n, body_fn(k / n), True) for k in range(n)]
    return keys + [(1.0, keys[0][1], True)]


def tail_sway(ph, amp, lag=0.12, droop=0.0):
    return {"Tail1": {"rz": amp * math.sin(TAU * ph), "rx": droop},
            "Tail2": {"rz": amp * 1.1 * math.sin(TAU * (ph - lag)), "rx": droop * 0.6},
            "Tail3": {"rz": amp * 1.3 * math.sin(TAU * (ph - 2 * lag)), "rx": droop * 0.4}}


# ---- WH_Wolf_Idle: breathing (chest scale 1.00..1.03, 2 breaths), slow head/tail sway
def idle_body(ph):
    br = 0.5 - 0.5 * math.cos(2 * TAU * ph)                # 0..1, 2 breaths / 3 s
    sc = 1.0 + 0.03 * br
    return merge({"Chest": {"s": sc},
                  "Neck": {"s": 1.0 / sc, "rx": 1.5 * math.sin(TAU * ph), "rz": 2.0 * math.sin(TAU * ph + 0.7)},
                  "FL_UpperLeg": {"s": 1.0 / sc}, "FR_UpperLeg": {"s": 1.0 / sc},
                  "Head": {"rz": 3.5 * math.sin(TAU * ph), "ry": 2.0 * math.sin(TAU * ph + 1.3),
                           "rx": -1.0 * math.sin(2 * TAU * ph)},
                  "Jaw": {"rx": 1.5 * br}},
                 tail_sway(ph, 7.0, 0.1))


KEYS["WH_Wolf_Idle"] = dict(dur=3.0, loop=True,
                            keys=[(k / 12, idle_body(k / 12), True) for k in range(12)] + [(1.0, idle_body(0.0), True)])


# ---- WH_Wolf_Walk: diagonal pairs FL+BR / FR+BL, minimal bob, tail synced to stride
def walk_body(ph):
    return merge({"Spine": {"lz": -0.004 + 0.004 * math.cos(2 * TAU * ph), "ry": 5.5 * math.sin(TAU * ph),
                            "rz": 2.0 * math.sin(TAU * ph), "rx": 1.0 * math.cos(2 * TAU * ph)},
                  "Chest": {"ry": -6.5 * math.sin(TAU * ph), "rz": -3.0 * math.sin(TAU * ph)},
                  "Neck": {"rx": 3.0 * math.cos(2 * TAU * ph + 0.5), "rz": 1.5 * math.sin(TAU * ph)},
                  "Head": {"rx": -2.0 * math.cos(2 * TAU * ph + 0.5)}},
                 tail_sway(ph, 9.0, 0.1, droop=-4.0))


WALK_GAIT = {"name": "WH_Wolf_Walk",
             "FL": (0.0, 0.24, 0.08, 0.6), "BR": (0.0, 0.26, 0.07, 0.6),
             "FR": (0.5, 0.24, 0.08, 0.6), "BL": (0.5, 0.26, 0.07, 0.6)}


# ---- WH_Wolf_Run: two-beat gallop (gather / extend), big spine pitch, head low/forward
def run_body(ph):
    c = math.cos(TAU * ph)            # +1 gather (hinds under, back rounded), -1 extend
    return merge({"Spine": {"lz": 0.005 + 0.02 * math.sin(TAU * ph + 0.6), "rx": 6.0 * c},
                  "Chest": {"rx": -9.0 * c},
                  "Neck": {"rx": 16.0 + 6.0 * c, "ly": 0.0},
                  "Head": {"rx": -10.0 - 5.0 * c},
                  "Jaw": {"rx": 6.0}},
                 {"Tail1": {"rx": -14.0 + 8.0 * c}, "Tail2": {"rx": -10.0 + 8.0 * math.cos(TAU * (ph - 0.12))},
                  "Tail3": {"rx": -6.0 + 9.0 * math.cos(TAU * (ph - 0.24))}})


RUN_GAIT = {"name": "WH_Wolf_Run",
            "BL": (0.0, 0.46, 0.13, 0.38), "BR": (0.94, 0.46, 0.13, 0.38),
            "FL": (0.5, 0.38, 0.15, 0.36), "FR": (0.44, 0.38, 0.15, 0.36)}


def planted(body, err_tag):
    p = legs_flat(merge(body))
    e = plant(p)
    REPORT.setdefault("solve_err_cm", {}).setdefault(err_tag, []).append(round(e * 100, 2))
    return p


# ---- WH_Wolf_Attack1: windup (rear shift, head back, jaw 35) -> lunge -> SNAP at contact -> recover
ATK_WINDUP = {"Spine": {"ly": 0.06, "lz": -0.05, "rx": 2.0}, "Chest": {"rx": -1.0},
              "Neck": {"rx": -18.0}, "Head": {"rx": -12.0}, "Jaw": {"rx": 35.0},
              "Tail1": {"rx": -10.0}, "Tail2": {"rx": -6.0}}
ATK_LUNGE = {"Spine": {"ly": -0.05, "lz": -0.035, "rx": 3.0}, "Chest": {"rx": 5.0},
             "Neck": {"rx": 22.0}, "Head": {"rx": -6.0}, "Jaw": {"rx": 35.0},
             "Tail1": {"rx": 6.0}, "Tail2": {"rx": 4.0}}
ATK_CONTACT = {"Spine": {"ly": -0.075, "lz": -0.045, "rx": 4.0}, "Chest": {"rx": 7.0},
               "Neck": {"rx": 34.0}, "Head": {"rx": 2.0}, "Jaw": {"rx": 0.0},
               "Tail1": {"rx": 8.0}, "Tail2": {"rx": 6.0}}
ATK_RECOVER = {"Spine": {"ly": -0.04, "lz": -0.01, "rx": 1.0}, "Chest": {"rx": 2.0},
               "Neck": {"rx": 8.0}, "Head": {"rx": 1.0}, "Jaw": {"rx": 2.0},
               "Tail1": {"rx": 2.0}}

# ---- WH_Wolf_Hit: recoil up/back + head shake + body dip
HIT_RECOIL = {"Spine": {"ly": 0.04, "lz": -0.05, "rx": 0.0, "ry": 3.0}, "Chest": {"rx": -1.0},
              "Neck": {"rx": -16.0, "rz": 6.0}, "Head": {"rz": 16.0, "ry": 8.0}, "Jaw": {"rx": 10.0},
              "Tail1": {"rx": 12.0}, "Tail2": {"rx": 8.0}}
HIT_SHAKE = {"Spine": {"ly": 0.03, "lz": -0.03, "ry": -2.0}, "Chest": {"rx": -2.0},
             "Neck": {"rx": -6.0, "rz": -5.0}, "Head": {"rz": -14.0, "ry": -6.0}, "Jaw": {"rx": 6.0},
             "Tail1": {"rx": 8.0}, "Tail2": {"rx": 5.0}}
HIT_SETTLE = {"Spine": {"ly": 0.01, "lz": -0.012}, "Neck": {"rx": -2.0}, "Head": {"rz": 5.0, "ry": 2.0},
              "Jaw": {"rx": 2.0}, "Tail1": {"rx": 3.0}}

# ---- WH_Wolf_Death: stagger -> legs buckle under -> roll onto the right side -> settle flat, tail limp
DEATH_STAGGER = {"Spine": {"lz": -0.03, "ly": 0.03, "ry": -3.0}, "Neck": {"rx": -12.0}, "Head": {"rx": -6.0, "rz": 8.0},
                 "Jaw": {"rx": 14.0}, "Tail1": {"rx": 10.0}}
FOLD_F = {"UpperLeg": {"rx": -28.0}, "Leg": {"rx": 70.0}, "Foot": {"rx": 60.0}}
FOLD_B = {"UpperLeg": {"rx": -45.0}, "Leg": {"rx": 70.0}, "Foot": {"rx": -60.0}}
LIMP_F = {"UpperLeg": {"rx": -22.0}, "Leg": {"rx": 28.0}, "Foot": {"rx": 25.0}}
LIMP_B = {"UpperLeg": {"rx": -12.0}, "Leg": {"rx": 22.0}, "Foot": {"rx": -18.0}}


def legs(fr, bk, droop=0.0):
    """Leg set; droop > 0 sags the upper-side (left) legs toward the ground
    (body's right once rolled)."""
    out = {}
    for pre in LEGS:
        src = fr if pre[0] == "F" else bk
        for part, c in src.items():
            out[f"{pre}_{part}"] = dict(c)
        out[f"{pre}_UpperLeg"]["ry"] = droop if pre[1] == "L" else 0.0
    return out


def limp_tail(k):
    """ry > 0 swings the hanging tail toward the body's right = the ground once rolled."""
    return {"Tail1": {"rx": 10.0 * k, "ry": 5.0 * k}, "Tail2": {"ry": 8.0 * k, "rx": 4.0 * k},
            "Tail3": {"ry": 6.0 * k}}


DEATH_BUCKLE = merge(legs(FOLD_F, FOLD_B), {"Spine": {"lz": -0.36, "ly": 0.02, "ry": -12.0, "rx": 2.0},
                                            "Chest": {"rx": 4.0, "ry": -4.0}, "Neck": {"rx": 10.0, "rz": -6.0},
                                            "Head": {"rx": 6.0}, "Jaw": {"rx": 10.0},
                                            "Tail1": {"rx": 8.0}, "Tail2": {"rx": 4.0}})
DEATH_ROLL = merge(legs(LIMP_F, LIMP_B, 10.0), {"Spine": {"lz": -0.50, "ry": -70.0},
                                                 "Chest": {"ry": -8.0}, "Neck": {"rx": 4.0, "rz": -6.0},
                                                 "Head": {"rx": 4.0, "rz": -4.0}, "Jaw": {"rx": 8.0}},
                   limp_tail(0.6))
DEATH_OVER = merge(legs(LIMP_F, LIMP_B, 16.0), {"Spine": {"lz": -0.55, "ry": -96.0},
                                                 "Chest": {"ry": -4.0}, "Neck": {"rx": 2.0, "rz": -8.0},
                                                 "Head": {"rz": -6.0}, "Jaw": {"rx": 6.0}},
                   limp_tail(1.1))
DEATH_PRONE = merge(legs(LIMP_F, LIMP_B, 14.0), {"Spine": {"lz": -0.55, "ry": -90.0},
                                                  "Chest": {"ry": -2.0}, "Neck": {"rx": 2.0, "rz": -7.0},
                                                  "Head": {"rz": -5.0}, "Jaw": {"rx": 5.0}},
                    limp_tail(1.0))


# --------------------------------------------------------------------- interpolation (chain_clips Hermite)
CHANNELS = ("rx", "ry", "rz", "lx", "ly", "lz", "s")
DEFAULT = {"s": 1.0}


def ch(p, bn, c):
    return p.get(bn, {}).get(c, DEFAULT.get(c, 0.0))


def hermite_tangents(keys, cyclic):
    """Per key: True -> Catmull-Rom tangent (pass-through), else 0 (ease).
    cyclic: tangents wrap (key 0 == key -1), so the loop seam is C1."""
    n = len(keys)
    tans = []
    for i, (t, pose, through) in enumerate(keys):
        if cyclic:
            ia = (i - 1) % (n - 1) if i > 0 else n - 2
            ib = (i + 1) if i < n - 1 else 1
            t0 = keys[ia][0] - (1.0 if ia > i else 0.0)
            t1 = keys[ib][0] + (1.0 if ib < i else 0.0)
        else:
            if not through or i == 0 or i == n - 1:
                tans.append(None)
                continue
            ia, ib = i - 1, i + 1
            t0, t1 = keys[ia][0], keys[ib][0]
        p0, p1 = keys[ia][1], keys[ib][1]
        tans.append({(bn, c): (ch(p1, bn, c) - ch(p0, bn, c)) / (t1 - t0) for bn in BONES for c in CHANNELS})
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
                for cn in CHANNELS:
                    a, b = ch(p0, bn, cn), ch(p1, bn, cn)
                    m0 = tans[i][(bn, cn)] if tans[i] else 0.0
                    m1 = tans[i + 1][(bn, cn)] if tans[i + 1] else 0.0
                    c[cn] = h00 * a + h10 * h * m0 + h01 * b + h11 * h * m1
                out[bn] = c
            return out
    return keys[-1][1]


# --------------------------------------------------------------------- mesh evaluation (ground clamp)
def apply_pose(pose):
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
        c = pose.get(pb.name, {}) if pb.name != "Root" else {}
        rq = REST[pb.name]["rot"]
        pb.rotation_quaternion = rq.inverted() @ axis_quat(c) @ rq
        pb.location = rq.inverted() @ Vector((c.get("lx", 0.0), c.get("ly", 0.0), c.get("lz", 0.0)))
        sv = c.get("s", 1.0)
        pb.scale = (sv, sv, sv)


def eval_mesh(pose):
    apply_pose(pose)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body.evaluated_get(dg)
    me = ev.to_mesh()
    co = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get("co", co)
    ev.to_mesh_clear()
    return co.reshape(-1, 3)


def clamp_ground(pose, floor=GROUND - 1e-4):
    """Lift the body (Spine lz) if any skinned vertex sinks below the floor."""
    co = eval_mesh(pose)
    lo = float(co[:, 2].min())
    if lo < floor:
        pose.setdefault("Spine", {})["lz"] = pose.get("Spine", {}).get("lz", 0.0) + (floor - lo)
    return lo


def settle(pose, floor=GROUND + 0.003):
    """Exact rest-on-ground: shift Spine lz so the lowest vertex touches the floor."""
    co = eval_mesh(pose)
    lo = float(co[:, 2].min())
    pose.setdefault("Spine", {})["lz"] = pose.get("Spine", {}).get("lz", 0.0) + (floor - lo)
    return lo


# --------------------------------------------------------------------- build all KEYS
KEYS["WH_Wolf_Walk"] = dict(dur=1.0, loop=True, gait=WALK_GAIT, keys=body_keys(16, walk_body))
KEYS["WH_Wolf_Run"] = dict(dur=0.55, loop=True, gait=RUN_GAIT, keys=body_keys(16, run_body))
REST_POSE = legs_flat({})
KEYS["WH_Wolf_Attack1"] = dict(dur=0.7, loop=False, plant_until=1.0, keys=[
    (0.0, REST_POSE, False),
    (0.34, ATK_WINDUP, False),
    (0.48, ATK_LUNGE, True),
    (0.56, ATK_CONTACT, False),
    (0.78, ATK_RECOVER, False),
    (1.0, REST_POSE, False)])
KEYS["WH_Wolf_Hit"] = dict(dur=0.4, loop=False, plant_until=1.0, keys=[
    (0.0, REST_POSE, False),
    (0.22, HIT_RECOIL, False),
    (0.48, HIT_SHAKE, True),
    (0.72, HIT_SETTLE, False),
    (1.0, REST_POSE, False)])
log("settling death keys on the ground ...")
death_stagger = planted(DEATH_STAGGER, "WH_Wolf_Death")
dk = [merge(DEATH_BUCKLE), merge(DEATH_ROLL), merge(DEATH_OVER), merge(DEATH_PRONE)]
lows = [clamp_ground(dk[0]), clamp_ground(dk[1])]
lows += [settle(dk[2], GROUND + 0.001), settle(dk[3], GROUND + 0.003)]
REPORT["death_key_lowest_before_fix"] = [round(v, 4) for v in lows]
KEYS["WH_Wolf_Death"] = dict(dur=1.1, loop=False, ground=True, plant_until=0.14, keys=[
    (0.0, REST_POSE, False),
    (0.14, death_stagger, False),
    (0.40, dk[0], True),
    (0.66, dk[1], True),
    (0.80, dk[2], False),
    (0.92, dk[3], False),
    (1.0, dk[3], False)])                     # hold: the clip ENDS on the settled prone rest


# --------------------------------------------------------------------- bake (chain_clips pattern)
def bake(name, spec):
    keys = spec["keys"]
    tans = hermite_tangents(keys, spec["loop"])
    L = spec["dur"] * FPS                     # may be fractional (Run 16.5 frames)
    N = max(2, round(L))
    frames = sorted(set([round(i * L / N, 5) for i in range(N + 1)] + [round(t * L, 5) for t, _, _ in keys]))
    old = bpy.data.actions.get(name)
    if old:
        bpy.data.actions.remove(old)
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    arm.animation_data_create()
    arm.animation_data.action = act
    prev = {}
    first = None
    worst = 0.0
    for f in frames:
        u = f / L
        if spec["loop"] and f == frames[-1]:
            pose = first                       # seam: last frame == first frame exactly
        else:
            pose = sample(keys, tans, u)
            if "gait" in spec:                 # per-frame paw solve on the gait path
                worst = max(worst, solve_gait(pose, u, spec["gait"], prev))
            elif u <= spec.get("plant_until", -1.0) + 1e-9:
                worst = max(worst, plant(pose, guesses=prev))
                prev = {pre: leg_state(pose, pre) for pre in LEGS}
            if spec.get("ground"):
                clamp_ground(pose)
        if first is None:
            first = pose
        apply_pose(pose)
        for pb in arm.pose.bones:
            for prop in ("rotation_quaternion", "location", "scale"):
                pb.keyframe_insert(prop, frame=f, group=pb.name)
    for fc in act.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
    tr = arm.animation_data.nla_tracks.new()
    tr.name = name
    tr.strips.new(name, 0, act)
    tr.mute = True
    arm.animation_data.action = None
    REPORT.setdefault("clips", {})[name] = {"duration_s": round(frames[-1] / FPS, 5), "keys": len(frames),
                                           "leg_solve_worst_cm": round(worst * 100, 3),
                                           "key_times": [round(t * spec["dur"], 4) for t, _, _ in keys]}
    log(f"clip {name}: {len(frames)} keys, {frames[-1] / FPS:.4f}s, loop={spec['loop']}, "
        f"worst paw-solve miss {worst * 100:.2f} cm")
    return act


for name in CLIP_SPEC:
    bake(name, KEYS[name])

# FK cross-check vs Blender pose evaluation (chain_clips check_fk_against_blender)
worst = 0.0
for name in ("WH_Wolf_Walk", "WH_Wolf_Attack1"):
    act = bpy.data.actions[name]
    arm.animation_data.action = act
    for f in (0, 3, 7, 10):
        scene.frame_set(f)
        bpy.context.view_layer.update()
        pose = {}
        for pb in arm.pose.bones:
            rq = REST[pb.name]["rot"]
            q = rq @ pb.rotation_quaternion @ rq.inverted()
            e = q.to_euler("XYZ")
            loc = rq @ pb.location
            pose[pb.name] = {"rx": math.degrees(e.x), "ry": math.degrees(e.y), "rz": math.degrees(e.z),
                             "lx": loc.x, "ly": loc.y, "lz": loc.z}
        for pre in LEGS:
            p, _ = paw(pose, pre)
            m = arm.pose.bones[f"{pre}_Foot"].tail
            worst = max(worst, (p - m).length)
arm.animation_data.action = None
assert worst < 1e-3, worst
log(f"FK cross-check vs Blender pose eval: max paw err {worst * 1000:.3f} mm")
apply_pose({})
REPORT["fk_crosscheck_mm"] = round(worst * 1000, 4)
log("NLA tracks:", [t.name for t in arm.animation_data.nla_tracks])

bpy.ops.export_scene.gltf(
    filepath=OUT_PATH, export_format="GLB",
    export_animation_mode="ACTIONS",
    export_skins=True, export_def_bones=False,
    export_apply=False, export_image_format="AUTO",
    export_yup=True,
    export_force_sampling=False,           # keys are already baked on every frame (exact times)
    export_optimize_animation_size=False,
    export_anim_slide_to_zero=True, export_reset_pose_bones=True,
    export_extras=False, export_cameras=False, export_lights=False)
log(f"exported {OUT_PATH} ({os.path.getsize(OUT_PATH) / 1e6:.2f} MB)")
if "log" in opts:
    with open(opts["log"], "w") as fh:
        json.dump(REPORT, fh, indent=1)
    log("log ->", opts["log"])
