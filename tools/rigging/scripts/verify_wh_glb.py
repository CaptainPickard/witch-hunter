"""
verify_wh_glb.py -- validator for a rigged Witch Hunter GLB (see VERIFY.md).

    scripts/bl.sh --python scripts/verify_wh_glb.py -- RIGGED.glb SOURCE.glb \
        [--render DIR] [--frames WH_Idle:1,WH_Walk:8,...] [--require WH_Idle,WH_Walk,...]

Two layers of checks:
  A. Raw glTF JSON/binary (what three.js GLTFLoader actually sees).
  B. Blender re-import (armature, vertex groups, evaluated in-place-ness).
Exit code 1 (and "VERIFY FAIL" lines) if any check fails; "VERIFY PASS" at the end otherwise.
Optional: headless EEVEE preview frames (front + side) for eyeball QA.
"""
import bpy
import sys
import os
import json
import struct
import hashlib
import math
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
RIGGED, SOURCE = os.path.abspath(argv[0]), os.path.abspath(argv[1])
opts = {argv[i].lstrip("-"): argv[i + 1] for i in range(2, len(argv) - 1, 2)}

EXPECTED_BONES = ["Root", "Hips", "Spine", "Chest", "Neck", "Head"] + [
    f"{s}_{b}" for s in ("L", "R")
    for b in ("Shoulder", "UpperArm", "Forearm", "Hand", "Thigh", "Shin", "Foot")]
ALL_CLIPS = ["WH_Idle", "WH_Walk", "WH_Run", "WH_Attack1", "WH_Hit", "WH_Death"]
LOOPS = {"WH_Idle", "WH_Walk", "WH_Run"}
REQUIRED = opts.get("require", ",".join(ALL_CLIPS)).split(",")
failures = []


def check(ok, msg):
    print(("  ok   " if ok else "VERIFY FAIL ") + msg, flush=True)
    if not ok:
        failures.append(msg)


# ------------------------------------------------------------------ A. raw glTF
def read_glb(path):
    d = open(path, "rb").read()
    jlen = struct.unpack("<I", d[12:16])[0]
    j = json.loads(d[20:20 + jlen])
    off = 20 + jlen
    blen = struct.unpack("<I", d[off:off + 4])[0]
    return j, d[off + 8:off + 8 + blen]


def accessor(j, binb, idx):
    a = j["accessors"][idx]
    bv = j["bufferViews"][a["bufferView"]]
    comps = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}[a["type"]]
    dt = {5126: np.float32, 5125: np.uint32, 5123: np.uint16, 5121: np.uint8}[a["componentType"]]
    start = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    stride = bv.get("byteStride", 0)
    item = comps * np.dtype(dt).itemsize
    if stride and stride != item:
        raw = np.frombuffer(binb, np.uint8, a["count"] * stride, start).reshape(a["count"], stride)[:, :item]
        arr = np.frombuffer(raw.tobytes(), dt)
    else:
        arr = np.frombuffer(binb, dt, a["count"] * comps, start)
    arr = arr.reshape(a["count"], comps)
    if a.get("normalized") and dt != np.float32:
        arr = arr / np.iinfo(dt).max
    return arr


def image_bytes(j, binb, i=0):
    bv = j["bufferViews"][j["images"][i]["bufferView"]]
    return binb[bv.get("byteOffset", 0):bv.get("byteOffset", 0) + bv["byteLength"]]


print("== A. raw glTF checks:", RIGGED)
rj, rb = read_glb(RIGGED)
sj, sb = read_glb(SOURCE)
check(len(rj.get("meshes", [])) == 1, f"exactly 1 mesh (found {len(rj.get('meshes', []))})")
check(len(rj.get("skins", [])) == 1, f"exactly 1 skin (found {len(rj.get('skins', []))})")
skin = rj["skins"][0]
joint_names = [rj["nodes"][n]["name"] for n in skin["joints"]]
check(sorted(joint_names) == sorted(EXPECTED_BONES),
      f"skin joints == 20 WH bones (found {len(joint_names)}: missing {set(EXPECTED_BONES) - set(joint_names)}, extra {set(joint_names) - set(EXPECTED_BONES)})")
prims = rj["meshes"][0]["primitives"]
check(len(prims) == 1, f"single primitive (found {len(prims)})")
pr = prims[0]
check("JOINTS_0" in pr["attributes"] and "WEIGHTS_0" in pr["attributes"], "JOINTS_0/WEIGHTS_0 present")
src_tris = sum(sj["accessors"][p["indices"]]["count"] // 3 for p in sj["meshes"][0]["primitives"])
out_tris = sum(rj["accessors"][p["indices"]]["count"] // 3 for p in prims)
check(out_tris == src_tris, f"triangle count unchanged ({out_tris} vs source {src_tris})")
src_v = sj["accessors"][sj["meshes"][0]["primitives"][0]["attributes"]["POSITION"]]["count"]
out_v = rj["accessors"][pr["attributes"]["POSITION"]]["count"]
# Blender's exporter splits a few vertices (+60 on the sample) because per-loop custom
# normals round-trip with tiny float differences. Allow <=0.5% extra vertices, but require
# the set of distinct (position, uv) pairs to be identical to the source.
check(src_v <= out_v <= src_v * 1.005, f"vertex count within +0.5% of source ({out_v} vs {src_v}, +{out_v - src_v})")
def pos_uv_set(j, b, p):
    P = accessor(j, b, p["attributes"]["POSITION"]); U = accessor(j, b, p["attributes"]["TEXCOORD_0"])
    return np.unique(np.hstack([P, U]).round(5), axis=0)
su, ou = pos_uv_set(sj, sb, sj["meshes"][0]["primitives"][0]), pos_uv_set(rj, rb, pr)
check(su.shape == ou.shape and np.array_equal(su, ou), f"distinct (position, uv) pairs identical to source ({len(ou)} vs {len(su)})")
W = accessor(rj, rb, pr["attributes"]["WEIGHTS_0"])
wsum = W.sum(axis=1)
check(bool((wsum > 0.99).all() and (wsum < 1.01).all()),
      f"every vertex weighted, sums≈1 (min {wsum.min():.4f}, max {wsum.max():.4f}, zero={int((wsum <= 1e-6).sum())})")
# bounds of the bind-pose geometry must match the source (geometry untouched)
sp = accessor(sj, sb, sj["meshes"][0]["primitives"][0]["attributes"]["POSITION"])
op = accessor(rj, rb, pr["attributes"]["POSITION"])
check(np.allclose(sp.min(0), op.min(0), atol=1e-4) and np.allclose(sp.max(0), op.max(0), atol=1e-4),
      f"bind-pose bounds unchanged (src {sp.min(0).round(3)}..{sp.max(0).round(3)})")
# texture intact
check(len(rj.get("images", [])) == len(sj.get("images", [])), f"image count {len(rj.get('images', []))} == source")
for i in range(len(sj.get("images", []))):
    a, b = hashlib.sha256(image_bytes(sj, sb, i)).hexdigest(), hashlib.sha256(image_bytes(rj, rb, i)).hexdigest()
    check(a == b and rj["images"][i].get("mimeType") == sj["images"][i].get("mimeType"),
          f"image {i} bytes bit-identical ({sj['images'][i].get('mimeType')}, sha256 {a[:12]}… vs {b[:12]}…)")
ss, rs = sj.get("samplers", [{}])[0], rj.get("samplers", [{}])[0]
check(ss.get("magFilter") == rs.get("magFilter"),
      f"sampler magFilter preserved (src {ss.get('magFilter')}, out {rs.get('magFilter')}; 9728=NEAREST 9729=LINEAR)")
if ss.get("minFilter") != rs.get("minFilter"):
    print(f"  note minFilter differs: src {ss.get('minFilter')} out {rs.get('minFilter')} (see VERIFY.md §texture)")
anims = {a["name"]: a for a in rj.get("animations", [])}
check(all(c in anims for c in REQUIRED), f"required clips present {REQUIRED} (found {sorted(anims)})")
root_idx = [n for n in skin["joints"] if rj["nodes"][n]["name"] == "Root"][0]
for name, a in sorted(anims.items()):
    tgt = [(rj["nodes"][c["target"]["node"]]["name"], c["target"]["path"]) for c in a["channels"]]
    root_ch = [t for t in tgt if t[0] == "Root"]
    times = accessor(rj, rb, a["samplers"][0]["input"])
    dur = float(times.max())
    trans = [c for c in a["channels"] if c["target"]["path"] == "translation"]
    drift = 0.0
    for c in trans:  # horizontal (glTF X/Z) drift between first and last key of loops
        v = accessor(rj, rb, a["samplers"][c["sampler"]]["output"])
        if rj["nodes"][c["target"]["node"]]["name"] == "Hips" and name in LOOPS:
            drift = max(drift, float(np.abs(v[-1] - v[0]).max()))
    root_static = True
    for c in a["channels"]:
        if c["target"]["node"] == root_idx:
            v = accessor(rj, rb, a["samplers"][c["sampler"]]["output"])
            root_static &= bool(np.allclose(v, v[0], atol=1e-5))
    check(root_static, f"{name}: {dur:.3f}s, {len(a['channels'])} channels, Root static ({len(root_ch)} Root channels)")
    if name in LOOPS:
        check(drift < 1e-4, f"{name}: loop closes (Hips translation first==last, drift {drift:.2e})")

# Rotation deltas are measured against each glTF joint's authored rest quaternion,
# not against identity: different arm rolls can otherwise inflate apparent motion.
MAJOR_BONES = ("L_Thigh", "R_Thigh", "L_UpperArm", "R_UpperArm", "Spine")
for name, a in sorted(anims.items()):
    excursions = {}
    for bone in MAJOR_BONES:
        node_idx = next(i for i in skin["joints"] if rj["nodes"][i]["name"] == bone)
        rest = np.asarray(rj["nodes"][node_idx].get("rotation", [0, 0, 0, 1]), dtype=np.float64)
        rest /= np.linalg.norm(rest)
        peak = 0.0
        for ch in a["channels"]:
            if ch["target"]["node"] != node_idx or ch["target"]["path"] != "rotation":
                continue
            samples = accessor(rj, rb, a["samplers"][ch["sampler"]]["output"]).astype(np.float64)
            samples /= np.linalg.norm(samples, axis=1)[:, None]
            peak = max(peak, float(np.max(2 * np.arccos(np.clip(np.abs(samples @ rest), 0, 1)))))
        excursions[bone] = round(peak, 4)
    print(f"  EXCURSION {name}: " + " ".join(f"{bone}={excursions[bone]:.4f}rad" for bone in MAJOR_BONES), flush=True)

# ------------------------------------------------------------------ B. Blender re-import
print("== B. Blender re-import checks")
bpy.ops.wm.read_factory_settings(use_empty=True)
# The importer converts glTF seconds -> frames at the scene fps; factory default is 24,
# which puts loop ends on fractional frames. Match the rig script's fps.
bpy.context.scene.render.fps = int(opts.get("fps", 30))
bpy.ops.import_scene.gltf(filepath=RIGGED)
arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
# The importer also creates a hidden icosphere mesh used as bone display shape; ignore it.
meshes = [o for o in bpy.data.objects if o.type == "MESH" and o.users_collection
          and any(m.type == "ARMATURE" for m in o.modifiers)]
check(len(arms) == 1 and len(meshes) == 1, f"1 armature + 1 mesh (got {len(arms)} + {len(meshes)})")
arm, mesh = arms[0], meshes[0]
check(sorted(b.name for b in arm.data.bones) == sorted(EXPECTED_BONES), f"armature has the 20 WH bones ({len(arm.data.bones)})")
check(any(m.type == "ARMATURE" and m.object == arm for m in mesh.modifiers), "mesh skinned to armature (Armature modifier)")
vg = {g.name for g in mesh.vertex_groups}
check(vg >= set(EXPECTED_BONES) - {"Root"}, f"vertex groups for all 19 deform bones (missing {set(EXPECTED_BONES) - {'Root'} - vg})")
unweighted = sum(1 for v in mesh.data.vertices if not any(g.weight > 0 for g in v.groups))
check(unweighted == 0, f"every vertex in >=1 vertex group ({unweighted} unweighted of {len(mesh.data.vertices)})")
counts = {g.name: 0 for g in mesh.vertex_groups}
idx = {g.index: g.name for g in mesh.vertex_groups}
for v in mesh.data.vertices:
    for g in v.groups:
        if g.weight > 0.05:
            counts[idx[g.group]] += 1
check(all(counts.get(b, 0) > 0 for b in EXPECTED_BONES if b != "Root"),
      f"no empty deform bone (weight>0.05 counts: {counts})")
tris = sum(len(p.vertices) - 2 for p in mesh.data.polygons)
check(tris == src_tris, f"Blender triangle count {tris} == source {src_tris}")

# Action name mapping: the Blender importer may suffix action names with the object
# name; three.js uses the glTF animation name (checked in A). Map back here.
acts = {}
for a in bpy.data.actions:
    base = next((c for c in ALL_CLIPS if a.name == c or a.name.startswith(c + "_")), None)
    if base:
        acts[base] = a
print("  Blender action names:", sorted(a.name for a in bpy.data.actions))
check(all(c in acts for c in REQUIRED), f"re-imported actions cover {REQUIRED}")
sc = bpy.context.scene
arm.animation_data_create()
root, hips = arm.pose.bones["Root"], arm.pose.bones["Hips"]
for name, act in sorted(acts.items()):
    arm.animation_data.action = act
    f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
    rp, hp = [], []
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        rp.append((arm.matrix_world @ root.matrix).translation.copy())
        hp.append((arm.matrix_world @ hips.matrix).translation.copy())
    rdrift = max((p - rp[0]).length for p in rp)
    hxy = max(math.hypot(p.x - hp[0].x, p.y - hp[0].y) for p in hp)
    check(rdrift < 1e-5, f"{name}: Root world position constant over clip (max drift {rdrift:.2e})")
    if name in LOOPS:
        close = (hp[-1] - hp[0]).length
        check(close < 1e-3, f"{name}: Hips returns to start ({close:.2e}); horizontal sway {hxy:.3f} (<0.05 expected)")
        check(hxy < 0.05, f"{name}: Hips horizontal sway {hxy:.3f} < 0.05 (in place)")
arm.animation_data.action = None


# ------------------------------------------------------------------ previews
def render_previews(outdir, spec):
    os.makedirs(outdir, exist_ok=True)
    sc.render.engine = "BLENDER_EEVEE_NEXT"     # Cycles: build lacks OIDN; Workbench: no texture by default
    sc.eevee.taa_render_samples = 8             # QA poses need silhouettes, not 64-sample beauty renders
    sc.render.resolution_x = sc.render.resolution_y = 384
    sc.render.film_transparent = False
    world = bpy.data.worlds.new("W"); sc.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.25, 0.25, 0.3, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 3
    sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
    sc.collection.objects.link(sun)
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    cam.data.type = "ORTHO"
    sc.collection.objects.link(cam)
    sc.camera = cam
    zs = [(mesh.matrix_world @ v.co).z for v in mesh.data.vertices]
    zc, h = 0.5 * (min(zs) + max(zs)), max(zs) - min(zs)
    cam.data.ortho_scale = 1.6 * h
    views = {"front": ((0, -5 * h, zc), (math.radians(90), 0, 0)),
             "side": ((5 * h, 0, zc), (math.radians(90), 0, math.radians(90)))}
    for item in spec.split(","):
        clip, frame = item.split(":")
        act = acts.get(clip)
        if clip != "REST" and not act:
            print("  skip preview, no action", clip)
            continue
        arm.animation_data.action = act if clip != "REST" else None
        sc.frame_set(int(frame))
        for vn, (loc, rot) in views.items():
            cam.location, cam.rotation_euler = loc, rot
            sc.render.filepath = os.path.join(outdir, f"{clip}_f{int(frame):03d}_{vn}.png")
            bpy.ops.render.render(write_still=True)
            print("  preview", sc.render.filepath)


if "render" in opts:
    render_previews(opts["render"], opts.get("frames", "REST:1,WH_Idle:1,WH_Walk:8,WH_Walk:23,WH_Attack1:5,WH_Attack1:9"))

print("VERIFY PASS" if not failures else f"VERIFY FAILED ({len(failures)} checks)")
sys.exit(1 if failures else 0)
