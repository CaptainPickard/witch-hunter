#!/usr/bin/env python3
"""Round F proof: turn the wall-mirror plan (scratch/wall_mirror.py, same
formulas as region-manager whWallPlan) into three Blender shot lists for
roundF_proof_render.py. Objects are in game coords with per-axis scale.
  roundF_proof_scene.py <repo-root> <out-shots.json>
Shot 1: ring segment pair close-up (ivy faces point at the disc center).
Shot 2: wide shot from inside the ring: the wall receding behind region B's
        far witchwood (the closest prop to the wall), canopy over the wall.
Shot 3: gate arch front view from region A at night with the hung lantern
        (emissive glass + a warm point light at the socket).
"""
import json, math, sys
from pathlib import Path

root, out_p = Path(sys.argv[1]).resolve(), sys.argv[2]
sys.argv = [sys.argv[0], str(root)]
sys.path.insert(0, str(Path(__file__).parent))
import wall_mirror as WM   # noqa: E402  (module reads sys.argv[1] = repo root)

CFG, MANIFEST = WM.CFG, WM.MANIFEST
plan = WM.wall_plan()
W = CFG['boundaryWall']


def glb(name):
    return str(root / MANIFEST[name])


def wall_objs():
    out = []
    for s in plan['segments']:
        out.append({'glb': glb(s['asset']), 'name': s['asset'], 'x': s['x'], 'y': -W['sinkM'], 'z': s['z'],
                    'rotY': s['rotY'], 'sx': s['sx'], 'sy': s['sy'], 'sz': s['sz'], 'kind': s['kind']})
    return out


def arch_objs():
    A, LN = plan['arch'], plan['lantern']
    ca, sa = math.cos(A['rotY']), math.sin(A['rotY'])
    gx = A['x'] + A['offsetX'] * ca
    gz = A['z'] - A['offsetX'] * sa
    out = [{'glb': glb(A['asset']), 'name': A['asset'], 'x': gx, 'y': 0.0, 'z': gz, 'rotY': A['rotY'],
            'sx': A['scale'], 'sy': A['scale'], 'sz': A['scaleZ'], 'kind': 'arch'}]
    if LN:
        out.append({'glb': glb(LN['asset']), 'name': LN['asset'], 'x': A['x'], 'y': LN['localY'], 'z': A['z'],
                    'rotY': A['rotY'], 'sx': LN['scale'], 'sy': LN['scale'], 'sz': LN['scale'], 'kind': 'lantern'})
    return out


def prop_objs():
    out = []
    for key in ('regionA', 'regionB'):
        for p in CFG[key]['props']:
            if p['asset'] not in MANIFEST:
                continue
            s = p['scale']
            out.append({'glb': glb(p['asset']), 'name': p['asset'], 'x': p['x'], 'y': p.get('y', 0) or 0,
                        'z': p['z'], 'rotY': p.get('rotY', 0) or 0, 'sx': s, 'sy': s, 'sz': s, 'kind': 'prop'})
    return out


def near(objs, cx, cz, rad):
    return [o for o in objs if math.hypot(o['x'] - cx, o['z'] - cz) <= rad]


ALL = wall_objs() + arch_objs() + prop_objs()

# shot 1: ring segments 0 and 1 (east, +x), camera inside the ring
s0, s1 = [s for s in plan['segments'] if s['kind'] == 'ring'][:2]
mx, mz = (s0['x'] + s1['x']) / 2, (s0['z'] + s1['z']) / 2
rm = math.hypot(mx, mz); ux, uz = mx / rm, mz / rm
shot1 = {'stem': '01-wall-pair-closeup', 'objects': near(ALL, mx, mz, 14),
         'cam': [mx - ux * 6.0 - uz * 1.2, 1.7, mz - uz * 6.0 + ux * 1.2],
         'aim': [mx, 1.2, mz], 'lens': 28, 'night': False}

# shot 2: from inside the ring toward the far witchwood, wall receding behind it
clr = WM.clearance_report(plan)
rid, rest = clr['prop'].split('#')
idx = int(rest.split(':')[0])
key = 'regionA' if CFG['regionA']['id'] == rid else 'regionB'
tree = CFG[key]['props'][idx]
phi = math.atan2(tree['z'], tree['x'])
cphi = phi - math.radians(18)
cam2 = [72.0 * math.cos(cphi), 3.2, 72.0 * math.sin(cphi)]
shot2 = {'stem': '02-wall-ring-wide-canopy', 'objects': near(ALL, cam2[0], cam2[2], 75),
         'cam': cam2, 'aim': [tree['x'], 5.0, tree['z']], 'lens': 20, 'night': False,
         'tree': {'asset': tree['asset'], 'x': tree['x'], 'z': tree['z']}}

# shot 3: gate arch front from region A, night, lantern light at the socket
A = plan['arch']
sk = plan['sockets'][0] if plan['sockets'] else None
shot3 = {'stem': '03-gate-arch-lantern', 'objects': near(ALL, A['x'], A['z'], 40),
         'cam': [A['x'] + 1.5, 1.7, A['z'] + 15.0], 'aim': [A['x'], 4.6, A['z']], 'lens': 24,
         'night': True, 'light': {'x': sk['x'], 'y': sk['y'], 'z': sk['z'], 'watts': 900} if sk else None}

json.dump([shot1, shot2, shot3], open(out_p, 'w'))
for s in (shot1, shot2, shot3):
    kinds = {}
    for o in s['objects']:
        kinds[o['name']] = kinds.get(o['name'], 0) + 1
    print(s['stem'], 'cam', [round(v, 1) for v in s['cam']], 'aim', [round(v, 1) for v in s['aim']], kinds)
