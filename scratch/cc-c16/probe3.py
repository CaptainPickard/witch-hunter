#!/usr/bin/env python3
"""CC-C16b probe3: ground-truth scope (old fires = the 4 CONFIG stations BEFORE
C16b + the 2 C3/C1 fires; old loops = the 3 CC-C5 pack loops ONLY).
The new fires/loops ARE the subjects; old sets are the obstacles."""
import math, json, re

src = open('/tmp/wh-worldfeat/prototype/js/CONFIG.js').read()
S = json.load(open('/tmp/wh-worldfeat/scratch/cc-c16/sites.json'))
camp_pts = [(c[0], c[1]) for c in S['camps']]

# OLD fires = the original cooking.stations rows BEFORE C16b (D* = new, excluded)
iK = src.index('window.WH_CONFIG.cooking = {')
iKend = src.index('window.WH_CONFIG.dayNight = {')
st_txt = src[iK:iKend]
old_fires = []
for m in re.finditer(r"\{ id: '([^']+)', kind: '[^']+'[^}]*x: ([-\d.]+), z: ([-\d.]+)", st_txt):
    if m.group(1).startswith('banditFireD'): continue
    old_fires.append((m.group(1), float(m.group(2)), float(m.group(3))))
print('old stations:', [f[0] for f in old_fires])

# OLD loops = east/west/north only
iW = src.index('    wolfPacks: ['); iS = src.index('separationPush')
pack_txt = src[iW:iS]
old_loops = []
for m in re.finditer(r"id: '(\w+)', regionId: 'forest_of_the_old_king', members: 4, spawnSpread: 6,\s*(?://[^\n]*\n\s*)?waypoints: (\[\[[^\]]+\](?:,\s*\[[^\]]+\])*\])", pack_txt):
    pid = m.group(1)
    if pid in ('sw', 'se', 'ss', 'nw2'): continue
    pts = re.findall(r"\[(-?\d+(?:\.\d+)?), (-?\d+(?:\.\d+)?)\]", m.group(2))
    old_loops.append((pid, [(float(a), float(b)) for a, b in pts]))
print('old loops:', [l[0] for l in old_loops])

# obstacles for camps: old fires + all C props (the true props block) + old loop pts
iC = src.index('  regionC: {')
props_txt = src[iC:src.index('      // CC-C16b DENSIFY')]
crows = [(float(m[0]), float(m[1])) for m in re.findall(r"\{ asset: '[a-zA-Z]+', \s*x: ([-\d.]+), z: ([-\d.]+)", props_txt.replace(', x:', ', x:'))]
crows = [(float(m[0]), float(m[1])) for m in re.findall(r"\{ asset: '[a-zA-Z]+', x: ([-\d.]+), z: ([-\d.]+)", props_txt)]
old_pts = [p for _, pts in old_loops for p in pts]
SPAWN = (0, -96); STONE = (0, -366); DEN_OPEN = (-163.4, -202.6)
def dist(a, b): return math.hypot(a[0] - b[0], a[1] - b[1])
ROAD_SEG = [((0, -88), (0, -332)), ((34, -366), (240, -366)), ((-34, -366), (-240, -366)), ((0, -400), (0, -596))]
def d_road(x, z):
    best = max(0.0, math.hypot(x, z + 366) - 34)
    for (a, b) in ROAD_SEG:
        ax, az = a; bx, bz = b
        ex_, ez_ = bx - ax, bz - az
        t = max(0, min(1, ((x - ax) * ex_ + (z - az) * ez_) / (ex_ * ex_ + ez_ * ez_)))
        best = min(best, math.hypot(x - (ax + ex_ * t), z - (az + ez_ * t)))
    return best

viol = []
for i, (x, z) in enumerate(camp_pts):
    if dist((x, z), SPAWN) < 48: viol.append(('camp-spawn', i))
    if dist((x, z), STONE) < 48: viol.append(('camp-stone', i))
    if dist((x, z), DEN_OPEN) < 48: viol.append(('camp-den', i))
    for fx, fy, fz in old_fires:
        if dist((x, z), (fy, fz)) < 45: viol.append(('camp-oldfire', i, fx))
    for p in crows:
        if dist((x, z), p) < 26: viol.append(('camp-prop', i, p, round(dist((x, z), p), 1)))
    for l in old_pts:
        if dist((x, z), l) < 58: viol.append(('camp-oldloop', i, l))
    if d_road(x, z) < 35: viol.append(('camp-road', i, round(d_road(x, z), 1)))
    for j, o in enumerate(camp_pts):
        if i != j and dist((x, z), o) < 55: viol.append(('camp-camp', i, j))
new_pairs = [tuple(map(float, pt)) for loop in S['loops'] for pt in loop]
for pi, pts in enumerate(S['loops']):
    cx, cz = pts[0][0], pts[0][1]
    for l in old_pts:
        if dist((float(l[0]), float(l[1])), (cx, cz)) < 30:
            viol.append(('loop-oldloop', pi, l))
    for p in new_pairs:
        for fx, fy, fz in old_fires:
            if dist(p, (fy, fz)) < 40: viol.append(('looppt-oldfire', pi, fx))
    for ci, o in enumerate(camp_pts):
        if dist((o[0], o[1]), (cx, cz)) < 60:
            viol.append(('loop-camp', pi, ci))
    for p in new_pairs:
        near = min((dist(p, q) for q in crows), default=999)
        if near < 14: viol.append(('looppt-prop', p, round(near, 1)))

print('camps:', camp_pts)
print('violations:', len(viol))
for v in viol[:14]: print(' ', v)
import sys
sys.exit(1 if viol else 0)