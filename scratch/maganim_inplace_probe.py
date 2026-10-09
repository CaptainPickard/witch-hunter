"""MAGANIM A1 in-place check: source Mixamo hips travel per FBX (measure only).

blender -b --factory-startup --python-exit-code 1 --python scratch/maganim_inplace_probe.py -- \
    --clips scratch/mixamo_player_magic.json --out REPORT.json [--limit 0.3]

Travel = max horizontal (world XY, metres) distance of mixamorig:Hips head from
its first-frame position over the clip; also reports net end-start XY and the
vertical range. A clip over --limit is REPORTED as a violator - never doctored
(mixamo_retarget.py already discards horizontal hips displacement in the bake).
"""
import argparse
import json
from pathlib import Path
import sys

import bpy


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--clips', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--limit', type=float, default=0.3)
    args = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
    clips = json.loads(Path(args.clips).read_text())
    report = {'limit_m': args.limit, 'metric': 'max |hips_xy(t) - hips_xy(start)|, world metres',
              'clips': {}}
    for name, fbx in clips.items():
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=fbx)
        arm = [o for o in bpy.data.objects if o.type == 'ARMATURE']
        assert len(arm) == 1, name
        arm = arm[0]
        act = arm.animation_data.action
        start, end = map(lambda x: int(round(x)), act.frame_range)
        hips = arm.pose.bones['mixamorig:Hips']
        scene = bpy.context.scene
        pts = []
        for f in range(start, end + 1):
            scene.frame_set(f)
            pts.append(arm.matrix_world @ hips.head)
        p0 = pts[0]
        horiz = [((v.x - p0.x) ** 2 + (v.y - p0.y) ** 2) ** .5 for v in pts]
        net = ((pts[-1].x - p0.x) ** 2 + (pts[-1].y - p0.y) ** 2) ** .5
        zs = [v.z for v in pts]
        rec = {'src': fbx, 'frames': [start, end], 'bones': len(arm.pose.bones),
               'max_hips_travel_xy_m': max(horiz), 'net_hips_travel_xy_m': net,
               'hips_z_range_m': max(zs) - min(zs), 'in_place': max(horiz) < args.limit}
        report['clips'][name] = rec
        print('[inplace]', name, rec['bones'], round(rec['max_hips_travel_xy_m'], 4),
              round(net, 4), round(rec['hips_z_range_m'], 4), rec['in_place'], flush=True)
    report['violators'] = [n for n, r in report['clips'].items() if not r['in_place']]
    report['pass'] = not report['violators']
    Path(args.out).write_text(json.dumps(report, indent=2) + '\n')
    print('[inplace] violators', report['violators'], flush=True)


if __name__ == '__main__':
    main()
