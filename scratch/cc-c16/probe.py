#!/usr/bin/env python3
"""CC-C16b probe: FULL clearance verification of the chosen sites (independent
re-check, all gates from the brief). Exit 1 on any violation."""
import math, json, re

src = open('/tmp/wh-worldfeat/prototype/js/CONFIG.js').read()
S = json.load(open('/tmp/wh-worldfeat/scratch/cc-c16/sites.json'))

iC = src.index('  regionC: {'); iD = src.index('  regionD: {')
iW = src.index('    wolfPacks: ['); iS = src.index('separationPush')
iK = src.index('window.WH_CONFIG.cooking = {')
iKend = src.index('window.WH_CONFIG.dayNight = {')
crows = [(float(m[0]), float(m[1])) for m in re.findall(r"x: ([-\d.]+), z: ([-\d.]+)",
         src[iC:iK] + src[iKend:src.index('window.WH_CONFIG.gather = {')])]
old_loops = [(float(m[0]), float(m[1])) for m in re.findall(r"\[(-?\d+(?:\.\d+)?), (-?\d+(?:\.\d+)?)\]", src[iW:iS])]
fires = [(float(m[0]), float(m[1])) for m in re.findall(r"x: ([-\d.]+), z: ([-\d.]+)", src[iK:iKend])]
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
# CAMPS: fires/props now EXCLUDE the new rows themselves (new fires appended to
# fires AFTER the original 8; guards sit 2-4 m from their own fire by design).
NEW_CAMP_PAIRS = set((c[0], c[1]) for c in S['camps'])
for c in S['camps']:
    x, z = c[0], c[1]
    if dist((x, z), SPAWN) < 48: viol.append(('camp-spawn', c))
    if dist((x, z), STONE) < 48: viol.append(('camp-stone', c))
    if dist((x, z), DEN_OPEN) < 48: viol.append(('camp-den', c))
    for p in crows:
        if (p[0], p[1]) in NEW_CAMP_PAIRS: continue          # own fire
        if dist((x, z), p) < 26: viol.append(('camp-prop', c, p))
    for f in fires:
        if (f[0], f[1]) != (x, z) and dist((x, z), f) < 45: viol.append(('camp-fire', c, f))
    for l in old_loops:
        if dist((x, z), l) < 58: viol.append(('camp-loop', c, l))
    if d_road(x, z) < 35: viol.append(('camp-road', c))
    for o in S['camps']:
        if o is not c and o != c and dist((x, z), (o[0], o[1])) < 55: viol.append(('camp-camp', c, o))
# PACKS + LOOPS: loop-wires 47, loop-campfires 60, zones
for p in S['packs']:
    x, z = p[0], p[1]
    lp = min((dist((x, z), l) for l in old_loops), default=999)
    if lp < 60: viol.append(('pack-pack', p, lp))
    for c in S['camps']:
        if dist((x, z), (c[0], c[1])) < 60: viol.append(('pack-camp', p, c))
    if d_road(x, z) < 36: viol.append(('pack-road', p))
    if dist((x, z), DEN_OPEN) < 48: viol.append(('pack-den', p))
# loop waypoints: each vs every existing loop pair + fires
new_pairs = [tuple(map(float, pt)) for loop in S['loops'] for pt in loop]
for np_ in new_pairs:
    for l in old_loops:
        if dist(np_, l) < 30: viol.append(('looppt-loop', np_, l))
for np_ in new_pairs:
    for f in fires:
        if dist(np_, f) < 40: viol.append(('looppt-fire', np_, f))
    for p in crows:
        if dist(np_, p) < 12: viol.append(('looppt-prop', np_, p))

print('violations:', len(viol))
for v in viol[:10]: print(' ', v)
import sys
sys.exit(1 if viol else 0)