#!/usr/bin/env python3
"""Round G proof: three Blender shot lists for roundG_proof_render.py, built
from the wall mirror (scratch/wall_mirror.py, heightM 7.2) and the scatter
mirror plan (scratch/scatter_mirror.py --json, rings = whBushSnare).
  roundG_proof_scene.py <repo-root> <scatter-plan.json> <out-shots.json>
Shot 1: wall-height close-up - two ring segments with the ring line receding
        along the arc (camera just inside the ring, looking along the tangent).
Shot 2: wide ring view from inside at game-camera eye height (camHeight +
        camDistance * sin 20 deg), so the 7.2 m wall top sits above the eye;
        camera spot searched clear of props/trees.
Shot 3: snare-bush ring close-up at the base of the region-A young birch
        with >= 3 ring bushes and the most grass tufts within 5 m.
"""
import json, math, sys
from pathlib import Path

root, plan_p, out_p = Path(sys.argv[1]).resolve(), sys.argv[2], sys.argv[3]
sys.argv = [sys.argv[0], str(root)]
sys.path.insert(0, str(Path(__file__).parent))
import wall_mirror as WM   # noqa: E402  (module reads sys.argv[1] = repo root)

CFG, MANIFEST = WM.CFG, WM.MANIFEST
wplan = WM.wall_plan()
W = CFG['boundaryWall']
splan = json.load(open(plan_p))


def glb(name):
    return str(root / MANIFEST[name])


def obj(name, x, z, rot, sx, sy=None, sz=None, y=0.0, kind='prop'):
    return {'glb': glb(name), 'name': name, 'x': x, 'y': y, 'z': z, 'rotY': rot,
            'sx': sx, 'sy': sx if sy is None else sy, 'sz': sx if sz is None else sz, 'kind': kind}


ALL = []
for s in wplan['segments']:
    ALL.append(obj(s['asset'], s['x'], s['z'], s['rotY'], s['sx'], s['sy'], s['sz'], -W['sinkM'], s['kind']))
A = wplan['arch']
ca, sa = math.cos(A['rotY']), math.sin(A['rotY'])
ALL.append(obj(A['asset'], A['x'] + A['offsetX'] * ca, A['z'] - A['offsetX'] * sa, A['rotY'],
               A['scale'], A['scale'], A['scaleZ'], 0.0, 'arch'))
for rid, rp in splan.items():
    for p in rp['props']:
        if p['asset'] in MANIFEST:
            ALL.append(obj(p['asset'], p['x'], p['z'], p.get('rotY', 0) or 0, p['scale'], y=p.get('y', 0) or 0))
    for t in rp['trees']:
        ALL.append(obj(t['asset'], t['x'], t['z'], t['rotY'], t['scale'], kind='scatterTree'))
    for name, lst in rp['instances'].items():
        for it in lst:
            ALL.append(obj(name, it['x'], it['z'], it['rotY'], it['scale'], kind='instanced'))


def near(cx, cz, rad):
    return [o for o in ALL if math.hypot(o['x'] - cx, o['z'] - cz) <= rad]


ring = [s for s in wplan['segments'] if s['kind'] == 'ring']
N = len(ring)
wallH = W['heightM']
P = CFG['player']
eye = P['camHeight'] + P['camDistance'] * math.sin(math.radians(20))

# shot 1: segments 10/11 (north-east arc, clear of the gate), camera 5 m
# inside the ring two segments back, looking along the arc
th = lambda i: 2 * math.pi * i / N
i0 = 10
c_th, a_th = th(i0 - 2), th(i0 + 1)
cam1 = [82.5 * math.cos(c_th), 1.7, 82.5 * math.sin(c_th)]
aim1 = [87.0 * math.cos(a_th), wallH * 0.45, 87.0 * math.sin(a_th)]
shot1 = {'stem': '01-wall-height-closeup', 'objects': near(cam1[0], cam1[2], 40),
         'cam': cam1, 'aim': aim1, 'lens': 22, 'segments': [i0, i0 + 1]}

# shot 2: from inside region A toward the arc ahead; the camera spot is the
# first (by angle) region-A point at r 66 that is >= 8 m from every
# prop / scatter tree and whose view line (25 m ahead) is >= 5 m clear
tall = [o for o in ALL if o['kind'] in ('prop', 'scatterTree')]
def clear(x, z, m):
    return all(math.hypot(o['x'] - x, o['z'] - z) >= m for o in tall)
for deg in range(30, 151, 3):
    c2 = math.radians(deg)
    cx, cz = 66.0 * math.cos(c2), 66.0 * math.sin(c2)
    ax, az = 87.0 * math.cos(c2 + math.radians(55)), 87.0 * math.sin(c2 + math.radians(55))
    dl = math.hypot(ax - cx, az - cz)
    if clear(cx, cz, 8) and all(clear(cx + (ax - cx) * t / dl, cz + (az - cz) * t / dl, 5)
                                for t in range(4, 26, 3)):
        break
cam2 = [cx, eye, cz]
aim2 = [ax, eye - 0.6, az]
shot2 = {'stem': '02-wall-ring-wide', 'objects': near(cam2[0], cam2[2], 95),
         'cam': cam2, 'aim': aim2, 'lens': 16, 'eyeY': round(eye, 2), 'wallH': wallH}

# shot 3: region-A young scatter tree with the busiest snare ring
ra = splan[CFG['regionA']['id']]
snares = ra['instances'].get('whBushSnare', [])
grass = ra['instances'].get('grassTuft', [])
def score(t):
    nb = sum(1 for b in snares if math.hypot(b['x'] - t['x'], b['z'] - t['z']) < 3)
    ng = sum(1 for g in grass if math.hypot(g['x'] - t['x'], g['z'] - t['z']) < 5)
    return (min(nb, 3), ng, nb)                # >= 3 ring bushes, then most grass
# youngBirch only: on the fat youngDeadTree base the 1.1-1.6x collider-trunk
# ring radius sits INSIDE the visible flare and the trunk swallows the briars
young = [t for t in ra['trees'] if t['asset'] == 'youngBirch']
host = max(young, key=score)
hx, hz = host['x'], host['z']
# camera on the side facing the most grass, 4.2 m out, low
gx = sum(g['x'] - hx for g in grass if math.hypot(g['x'] - hx, g['z'] - hz) < 5) or 1.0
gz = sum(g['z'] - hz for g in grass if math.hypot(g['x'] - hx, g['z'] - hz) < 5)
gl = math.hypot(gx, gz); gx, gz = gx / gl, gz / gl
cam3 = [hx + gx * 4.2 - gz * 1.0, 1.35, hz + gz * 4.2 + gx * 1.0]
shot3 = {'stem': '03-snare-ring-closeup', 'objects': near(hx, hz, 30),
         'cam': cam3, 'aim': [hx, 0.75, hz], 'lens': 24,
         'host': {'asset': host['asset'], 'x': hx, 'z': hz, 'ring': score(host)[2], 'grass5m': score(host)[1]}}

json.dump([shot1, shot2, shot3], open(out_p, 'w'))
for s in (shot1, shot2, shot3):
    kinds = {}
    for o in s['objects']:
        kinds[o['name']] = kinds.get(o['name'], 0) + 1
    print(s['stem'], 'cam', [round(v, 1) for v in s['cam']], 'aim', [round(v, 1) for v in s['aim']], kinds,
          s.get('host', ''), s.get('eyeY', ''))
