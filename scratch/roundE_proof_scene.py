#!/usr/bin/env python3
"""Round E proof: turn the scatter-mirror plan (scatter_mirror.py --json) into
two Blender shot lists (objects in game coords + camera), for
roundE_proof_render.py.
  roundE_proof_scene.py <repo-root> <plan.json> <out-shots.json>
Shot 1: region-A ground patch around a scatter tree cluster (every CONFIG prop,
scatter tree, ring bush, free bush and grass tuft inside the patch radius).
Shot 2: close-up of the ring host (scatter tree preferred) with the most ring
bushes + grass tufts within 6 m.
"""
import json, math, sys
from pathlib import Path
import esprima

root, plan_p, out_p = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
sys.argv = [sys.argv[0], str(root)]
exec(open(Path(__file__).with_name('scatter_mirror.py')).read().split('# ---- footprints')[0])
plan = json.load(open(plan_p))['hold_outskirts']


def objs_within(cx, cz, rad):
    out = []
    def add(name, x, z, rot, sc, y=0.0, kind='prop'):
        if math.hypot(x - cx, z - cz) <= rad:
            out.append({'glb': str(root / MANIFEST[name]), 'name': name, 'x': x, 'z': z,
                        'y': y, 'rotY': rot, 'scale': sc, 'kind': kind})
    for p in plan['props']:
        if 'scatter' in p:
            continue
        add(p['asset'], p['x'], p['z'], p['rotY'], p['scale'], p.get('y', 0) or 0)
    for t in plan['trees']:
        add(t['asset'], t['x'], t['z'], t['rotY'], t['scale'], kind='scatterTree')
    for name, lst in plan['instances'].items():
        for it in lst:
            add(name, it['x'], it['z'], it['rotY'], it['scale'], kind='instanced')
    return out


# shot 1: densest scatter-tree neighbourhood
best = max(plan['trees'], key=lambda t: sum(
    1 for u in plan['trees'] + [p for p in plan['props'] if p.get('trunk', 0) > 0]
    if math.hypot(u['x'] - t['x'], u['z'] - t['z']) < 16))
cx, cz = best['x'], best['z']
shot1 = {'stem': '01-regionA-patch', 'objects': objs_within(cx, cz, 26),
         'cam': [cx - 4.5, 2.6, cz - 6.0], 'aim': [cx + 1.0, 2.2, cz + 2.0], 'lens': 18}

# shot 2: ring host with most rings + nearby grass
grass = plan['instances'].get('grassTuft', [])
def host_score(h):
    rings = sum(1 for r in plan['rings'] if r['host'] == h)
    g = sum(1 for it in grass if math.hypot(it['x'] - h[0], it['z'] - h[1]) < 6)
    return rings * 10 + g
hosts = {tuple(r['host']) for r in plan['rings']}
scatter_hosts = [h for h in hosts if any(abs(t['x'] - h[0]) < 1e-9 and abs(t['z'] - h[1]) < 1e-9
                                         for t in plan['trees'])]
hx, hz = max(scatter_hosts or hosts, key=lambda h: host_score(list(h)))
shot2 = {'stem': '02-bush-ring-closeup', 'objects': objs_within(hx, hz, 30),
         'cam': [hx - 5.5, 2.4, hz - 6.0], 'aim': [hx, 0.9, hz], 'lens': 30,
         'host': [hx, hz]}
json.dump([shot1, shot2], open(out_p, 'w'))
for s in (shot1, shot2):
    kinds = {}
    for o in s['objects']:
        kinds[o['name']] = kinds.get(o['name'], 0) + 1
    print(s['stem'], 'center', [round(v, 1) for v in s['aim']], kinds)
