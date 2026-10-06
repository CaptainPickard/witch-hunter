"""Round D: classify in-place swordpack attack clips by swing direction + shape.

For each candidate FBX, tracks the RIGHT-hand world position across the action
and reports: hand lateral crossing (which side it starts/ends, sign of x), max
hand height (overhead detection), max forward reach (thrust detection), and
arm extension. Character faces -Y after Blender Mixamo import (Z-up).
blender -b --factory-startup --python scratch/swordpack_probe2.py -- OUT.json
"""
import bpy, json, sys
from pathlib import Path
from mathutils import Vector

CANDS = [
    'sword and shield attack (4).fbx',
    'sword and shield slash.fbx',
    'sword and shield slash (3).fbx',
    'sword and shield slash (5).fbx',
    'sword and shield slash (4).fbx',
]
DIR = Path('/workspace/witch-hunter/scratch/mixamo-fbx/swordpack')
out = Path(sys.argv[sys.argv.index('--') + 1])
res = {}
for name in CANDS:
    fbx = DIR / name
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(fbx))
    arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    act = arm.animation_data.action
    s, e = map(lambda x: int(round(x)), act.frame_range)
    sc = bpy.context.scene
    # mixamo rigs: RightHand on the sword side
    names = [b.name for b in arm.pose.bones]
    hand = next(n for n in names if 'RightHand' in n or 'right_hand' in n.lower())
    hips = next(n for n in names if 'Hips' in n)
    spine = next(n for n in names if 'Spine1' in n or 'Spine' in n and 'Spine2' not in n)
    hb = arm.pose.bones[hand]
    def sample(f):
        sc.frame_set(f)
        m = arm.matrix_world @ hb.matrix
        return m.translation.copy()
    # rest hand pos for offsets
    h0 = sample(s)
    pts = [(f, sample(f)) for f in range(s, e + 1, 2)]
    xs = [p.x - h0.x for _, p in pts]
    ys = [p.y - h0.y for _, p in pts]
    zs = [p.z for _, p in pts]
    # hand height rel to hips rest to detect overhead
    hipz = (arm.matrix_world @ arm.pose.bones[hips].bone.head_local).z
    max_h = max(zs)
    # extension: max horizontal dist from spine root
    spine_w = arm.matrix_world @ arm.pose.bones[spine].bone.head_local
    ext = max(((p.x - spine_w.x) ** 2 + (p.y - spine_w.y) ** 2) ** 0.5 for _, p in pts)
    res[name] = {
        'frames': e - s + 1, 'sec': round((e - s) / 30, 2),
        'hand_x_start': round(xs[0], 2), 'hand_x_end': round(xs[-1], 2),
        'hand_x_min': round(min(xs), 2), 'hand_x_max': round(max(xs), 2),
        'hand_y_min': round(min(ys), 2), 'hand_y_max': round(max(ys), 2),
        'hand_z_max_rel_hips': round(max_h / hipz, 2),
        'hand_ext_max_m': round(ext, 2),
    }
    print('[probe2]', name, res[name], flush=True)
out.write_text(json.dumps(res, indent=1) + '\n')