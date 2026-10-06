"""Round D probe3: absolute hand-vs-spine trajectory at 5 normalized phases.

Character faces -Y (world), Z up: world X+ = character's LEFT, Y- = FORWARD.
Report hand offset from spine at start/25/50/75/end + max height ratio.
blender -b --factory-startup --python scratch/swordpack_probe3.py -- OUT.json
"""
import bpy, json, sys
from pathlib import Path

CANDS = [
    'sword and shield attack (4).fbx',
    'sword and shield slash.fbx',
    'sword and shield slash (3).fbx',
    'sword and shield slash (5).fbx',
    'sword and shield slash (4).fbx',
    'sword and shield attack.fbx',
    'sword and shield attack (2).fbx',
    'sword and shield attack (3).fbx',
]
DIR = Path('/workspace/witch-hunter/scratch/mixamo-fbx/swordpack')
out = Path(sys.argv[sys.argv.index('--') + 1])
res = {}
for name in CANDS:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(DIR / name))
    arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    act = arm.animation_data.action
    s, e = map(lambda x: int(round(x)), act.frame_range)
    sc = bpy.context.scene
    names = [b.name for b in arm.pose.bones]
    hand = next(n for n in names if 'RightHand' in n)
    spine = next(n for n in names if 'Spine' in n)
    hb, spb = arm.pose.bones[hand], arm.pose.bones[spine]
    hipz = (arm.matrix_world @ arm.pose.bones[next(n for n in names if 'Hips' in n)].bone.head_local).z
    sw = arm.matrix_world @ spb.bone.head_local  # static spine root (rest)
    def sample(f):
        sc.frame_set(f)
        return (arm.matrix_world @ hb.matrix).translation.copy()
    frames = range(s, e + 1)
    pts = [sample(f) for f in frames]
    span = len(pts) - 1
    marks = {}
    for label, fi in [('start', 0), ('p25', int(span * .25)), ('p50', int(span * .5)),
                      ('p75', int(span * .75)), ('end', span)]:
        p = pts[fi]
        marks[label] = [round(p.x - sw.x, 2), round(p.y - sw.y, 2), round(p.z, 2)]
    res[name] = {
        'frames': e - s + 1, 'sec': round((e - s) / 30, 2),
        'hand_offset_from_spine_lateralX_forwardMinusY_heightZ': marks,
        'hand_zmax_over_hipsZ': round(max(p.z for p in pts) / hipz, 2),
    }
    print('[probe3]', name, json.dumps(res[name]), flush=True)
out.write_text(json.dumps(res, indent=1) + '\n')