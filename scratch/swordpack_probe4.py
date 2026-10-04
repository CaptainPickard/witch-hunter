"""Round D probe4: impact-frame finder for the 3 chosen swordpack attacks.

Impact frame = global max |hand velocity| (fastest wrist point of the swing),
normalized from the action start. Feeds CONFIG.attackPhase durations:
windup = impact_t, strike = follow-through window, recover = remainder.
Also measures hand height at impact (chop sanity).
blender -b --factory-startup --python scratch/swordpack_probe4.py -- OUT.json
"""
import bpy, json, sys
from pathlib import Path
from mathutils import Vector

CANDS = {
    'R2L': 'sword and shield slash.fbx',          # 46f 1.5s in-place right-to-left
    'L2R': 'sword and shield slash (3).fbx',      # 51f 1.67s in-place left-to-right
    'SUB': 'sword and shield attack (4).fbx',     # 31f 1.0s in-place chop, thrust sub
}
DIR = Path('/workspace/witch-hunter/scratch/mixamo-fbx/swordpack')
out = Path(sys.argv[sys.argv.index('--') + 1])
res = {}
for role, name in CANDS.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(DIR / name))
    arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    act = arm.animation_data.action
    s, e = map(lambda x: int(round(x)), act.frame_range)
    fps = bpy.context.scene.render.fps
    sc = bpy.context.scene
    names = [b.name for b in arm.pose.bones]
    hand = next(n for n in names if 'RightHand' in n)
    hb = arm.pose.bones[hand]
    frames = range(s, e + 1)
    pts = []
    for f in frames:
        sc.frame_set(f)
        pts.append((arm.matrix_world @ hb.matrix).translation.copy())
    vels = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]
    vi = max(range(len(vels)), key=lambda i: vels[i])
    impact_f = frames.start + vi
    t_imp = (impact_f - s) / (e - s)
    dur = (e - s) / fps
    # follow-through: frame where velocity drops below 20% of peak after impact
    ft = e
    for i in range(vi, len(vels)):
        if vels[i] < 0.2 * vels[vi]:
            ft = frames.start + i
            break
    res[role] = {
        'file': name, 'frames_total': e - s + 1, 'dur_sec': round(dur, 3), 'fps': fps,
        'impact_frame_global': impact_f,
        'windup_sec': round(t_imp * dur, 3),          # start -> impact
        'strike_fallback_sec': round((ft - impact_f) / fps, 3),  # impact -> settle
        'impact_time': round(t_imp, 3),               # fraction of clip
        'peak_speed_mps': round(vels[vi] * fps, 1),
    }
    print('[probe4]', role, json.dumps(res[role]), flush=True)
out.write_text(json.dumps(res, indent=1) + '\n')