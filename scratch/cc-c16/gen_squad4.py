#!/usr/bin/env python3
"""CC-C16b gen_squad v4: the honest scan - the map is dense (162 prop rows,
47 fires/props near ring roads). Strategy relaxes to the actual gaps:
scan a polar GRID (bear 0-355 step 5, r 120-245 step 6) and pick the best-N
clear sites per category (camp / pack) by max-min distance to everything.
Deterministic, no bearings forced."""
import math, random, re, json

random.seed(20261020)
src = open('/tmp/wh-worldfeat/prototype/js/CONFIG.js').read()

iC = src.index('  regionC: {'); iD = src.index('  regionD: {')
iW = src.index('    wolfPacks: ['); iS = src.index('separationPush')
iK = src.index('window.WH_CONFIG.cooking = {')
crows = [(float(m[0]), float(m[1])) for m in re.findall(r"x: ([-\d.]+), z: ([-\d.]+)", src[iC:iD])]
loops = [(float(m[0]), float(m[1])) for m in re.findall(r"\[(-?\d+(?:\.\d+)?), (-?\d+(?:\.\d+)?)\]", src[iW:iS])]
fires = [(float(m[0]), float(m[1])) for m in re.findall(r"x: ([-\d.]+), z: ([-\d.]+)", src[iK:iC])]

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

def q(x, z, taken, kind):
    # quality: min distance to all obstacles; rejects zones
    r = math.hypot(x, z + 366)
    if not (120 <= r <= 244): return 0
    for p in crows:
        if dist((x, z), p) < 22: return 0
    if dist((x, z), SPAWN) < 48 or dist((x, z), STONE) < 48 or dist((x, z), DEN_OPEN) < 48: return 0
    d = [d_road(x, z) / (40 if kind == 'camp' else 36),
         min((dist((x, z), p) for p in crows), default=999) / 24,
         min((dist((x, z), f) for f in fires), default=999) / (42 if kind == 'camp' else 60),
         min((dist((x, z), l) for l in loops), default=999) / (58 if kind == 'camp' else 60),
         min((dist((x, z), t) for t in taken), default=999) / (55 if kind == 'camp' else 62)]
    return min(d)

def best_sites(kind, n, taken):
    cands = []
    for bear in range(0, 360, 5):
        a = math.radians(bear)
        for r in range(120, 245, 6):
            x, z = r * math.sin(a), -366 - r * math.cos(a)
            qq = q(x, z, taken, kind)
            if qq > 0.99: cands.append((qq, bear, r, round(x, 1), round(z, 1)))
    cands.sort(reverse=True)
    out = []
    for qq, bear, r, x, z in cands:
        if all(dist((x, z), o) > (55 if kind == 'camp' else 62) for o in out + taken):
            out.append((x, z, r, bear, round(qq, 2)))
            if len(out) == n: break
    return out

camps = best_sites('camp', 4, [])
print('CAMPS:', camps)
fires.extend((c[0], c[1]) for c in camps)
packs = best_sites('pack', 4, camps[:2])
print('PACKS:', packs)

# 8-pt loops around each pack centre (r 28-36)
loop_rows = []
random.seed(99)
for s in packs:
    cx, cz = s[0], s[1]
    rr = 28 + random.random() * 8
    pts = []
    for k in range(8):
        aa = 2 * math.pi * k / 8 + random.random() * 0.3
        rad = rr * (0.85 + random.random() * 0.3)
        pts.append([round(cx + rad * math.sin(aa), 1), round(cz - rad * math.cos(aa), 1)])
    loop_rows.append(pts)
print('LOOPS:', loop_rows)

json.dump({'camps': [c[:4] for c in camps], 'packs': [p[:4] for p in packs],
           'loops': loop_rows}, open('/tmp/wh-worldfeat/scratch/cc-c16/sites.json', 'w'), indent=1)
print('WROTE sites.json')