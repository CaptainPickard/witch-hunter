"""Probe swordpack FBX motion: frames, hips travel (WH Z-up axes), yaw turn, hips height.

blender -b --factory-startup --python scratch/swordpack_probe.py -- OUT.json
Mixamo FBX import: world Z-up after Blender conversion; character faces -Y.
"""
import bpy, json, math, sys
from pathlib import Path
from mathutils import Vector

DIR = Path('/workspace/witch-hunter/scratch/mixamo-fbx/swordpack')
out = Path(sys.argv[sys.argv.index('--') + 1])
res = {}
for fbx in sorted(DIR.glob('*.fbx')):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(fbx))
    arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    act = arm.animation_data.action
    s, e = map(lambda x: int(round(x)), act.frame_range)
    sc = bpy.context.scene
    hips = arm.pose.bones['mixamorig:Hips']
    def sample(f):
        sc.frame_set(f)
        m = arm.matrix_world @ hips.matrix
        fwd = m.to_3x3() @ Vector((0, 0, 1))  # Mixamo hips local Z = facing
        return (m.translation.copy(), math.degrees(math.atan2(fwd.x, -fwd.y)))
    rest_z = (arm.matrix_world @ hips.bone.head_local).z
    p0, y0 = sample(s)
    zs, yaws, prev = [], [], y0
    acc = 0.0
    for f in range(s, e + 1):
        p, y = sample(f)
        d = (y - prev + 180) % 360 - 180
        acc += d
        prev = y
        zs.append(p.z)
    p1, _ = sample(e)
    res[fbx.name] = {'frames': e - s + 1, 'sec': round((e - s) / 30, 2),
        'travel_xy_m': [round(p1.x - p0.x, 2), round(p1.y - p0.y, 2)],
        'yaw_start': round(y0, 1), 'yaw_delta': round(acc, 1),
        'hips_z_rel_rest': round(min(zs) / rest_z, 2)}
    print('[probe]', fbx.name, res[fbx.name], flush=True)
out.write_text(json.dumps(res, indent=1) + '\n')
