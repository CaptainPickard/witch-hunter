#!/usr/bin/env python3
"""CC-C16b probe v2: correct scope - the new rows are camp dressing and guard
positions BY DESIGN close to each other (own-fire exclusions for guards too)."""
import math, json, re

src = open('/tmp/wh-worldfeat/prototype/js/CONFIG.js').read()
S = json.load(open('/tmp/wh-worldfeat/scratch/cc-c16/sites.json'))
iC = src.index('  regionC: {')
iK = src.index('window.WH_CONFIG.cooking = {')
iKend = src.index('window.WH_CONFIG.dayNight = {')
ig = src.index('window.WH_CONFIG.gather = {')
# props BEFORE our appended fires exist? our fire rows sat inside the enemy
# scope (regionC.props) - the appended guard/enemy rows are in regionC.enemies.
# Build obstacle sets EXCLUDING own-camp dressing: camp fire + that camp's guards.
camp_pts = [(c[0], c[1]) for c in S['camps']]
guard_offsets = [(2.2, 2.6), (-2.6, 2.0), (0.0, 3.4)]
own = set()
for (x, z) in camp_pts:
    own.add((x, z))
    for dx, dz in guard_offsets:
        own.add((round(x + dx, 1), round(z + dz, 1)))
crows_raw = [(float(m[0]), float(m[1])) for m in re.findall(r"x: ([-\d.]+), z: ([-\d.]+)", src[iC:iK])]
crows_raw += [(float(m[0]), float(m[1])) for m in re.findall(r"x: ([-\d.]+), z: ([-\d.]+)", src[iKend:ig])]
crows = [p for p in crows_raw if p not in own]
fires_raw = [(float(m[0]), float(m[1])) for m in re.findall(r"x: ([-\d.]+), z: ([-\d.]+)", src[iK:iKend])]
iW = src.index('    wolfPacks: ['); iS = src.index('separationPush')
old_loops = [(float(m[0]), float(m[1])) for m in re.findall(r"\[(-?\d+(?:\.\d+)?), (-?\d+(?:\.\d+)?)\]", src[iW:iS])]
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
# camps vs OTHERS' dressing + zones + old fires + roads + old loops
for i, (x, z) in enumerate(camp_pts):
    if dist((x, z), SPAWN) < 48: viol.append(('camp-spawn', i))
    if dist((x, z), STONE) < 48: viol.append(('camp-stone', i))
    if dist((x, z), DEN_OPEN) < 48: viol.append(('camp-den', i))
    for p in crows:
        if dist((x, z), p) < 26: viol.append(('camp-prop', i, p))
    for f in fires_raw:
        if dist((x, z), f) < 45: viol.append(('camp-fire', i, f))
    for l in old_loops:
        if dist((x, z), l) < 58: viol.append(('camp-loop', i, l))
    if d_road(x, z) < 35: viol.append(('camp-road', i))
    for j, o in enumerate(camp_pts):
        if i != j and dist((x, z), o) < 55: viol.append(('camp-camp', i, j))
# guards vs OTHER camps' fires only (own-fire adjacency is the design)
for i, (x, z) in enumerate(camp_pts):
    for dx, dz in guard_offsets:
        gp = (round(x + dx, 1), round(z + dz, 1))
        for j, o in enumerate(camp_pts):
            if i != j and dist(gp, o) < 26: viol.append(('guard-foreign-fire', i, j))
        if d_road(*gp) < 20: viol.append(('guard-road', i))
# packs + loop pts
new_pairs = [tuple(map(float, pt)) for loop in S['loops'] for pt in loop]
for p in S['packs']:
    x, z = p[0], p[1]
    for l in old_loops:
        if dist((x, z), l) < 60: viol.append(('pack-loop', p, l))
    for c in camp_pts:
        if dist((x, z), c) < 60: viol.append(('pack-camp', p, c))
    if d_road(x, z) < 36: viol.append(('pack-road', p))
    if dist((x, z), DEN_OPEN) < 48: viol.append(('pack-den', p))
for np_ in new_pairs:
    for l in old_loops:
        if dist(np_, l) < 30: viol.append(('looppt-loop', np_, l))
    for f in fires_raw:
        if dist(np_, f) < 40: viol.append(('looppt-fire', np_, f))
    if not any(dist(np_, p) >= 14 for p in crows):
        viol.append(('looppt-prop', np_))

print('violations:', len(viol))
for v in viol[:12]: print(' ', v)
import sys
sys.exit(1 if viol else 0)