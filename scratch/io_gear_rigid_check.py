"""Rigid-follow test: gear center offset to driving bone must be constant across poses.
Run: blender --background --factory-startup --python wh_rigid.py -- SPLICE
"""
import bpy, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=argv[0])
arm = bpy.data.objects["WH_Armature"]
action = next(a for a in bpy.data.actions if a.name.startswith("WH_Run"))
arm.animation_data_create()
arm.animation_data.action = action
scene = bpy.context.scene

def center(o):
    ws = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return sum(ws, Vector()) / 8

results = {}
for t in (0.05, 0.30, 0.55):
    scene.frame_set(int(round(t * scene.render.fps)))
    bpy.context.view_layer.update()
    head = arm.pose.bones["Head"]
    head_w = arm.matrix_world @ head.head  # head bone world pos
    hips = arm.pose.bones["Hips"]
    hips_w = arm.matrix_world @ hips.head
    hat = bpy.data.objects["WH_Hat"]; sat = bpy.data.objects["WH_Satchel"]
    dh = center(hat) - head_w
    ds = center(sat) - hips_w
    results[t] = (dh.length, ds.length)
    print("T=%.2f hat_offset=%.4f sat_offset=%.4f" % (t, dh.length, ds.length))
h = [v[0] for v in results.values()]
s = [v[1] for v in results.values()]
print("RIGID hat_spread=%.4f sat_spread=%.4f -> %s" % (
    max(h)-min(h), max(s)-min(s),
    "RIGID_FOLLOW" if (max(h)-min(h) < 0.01 and max(s)-min(s) < 0.01) else "DETACHED"))