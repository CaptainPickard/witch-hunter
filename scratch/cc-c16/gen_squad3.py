#!/usr/bin/env python3
"""CC-C16b gen_squad v3: pragmatic relaxation ladder.
Sites must clear: not inside a prop (26 m), 35 m off roads, 45 m off fires,
60 m off loops, 20 m off other camps, out of glade/Stone zones, r 120..246.
Camps get dressing ~14 m wide; wolves patrol.
Outputs camp x/z + loop centre + loop radius. Deterministic (seeded)."""
import math, random, re, json

random.seed(20261020)
src = open('/tmp/wh-worldfeat/prototype/js/CONFIG.js').read()

def rows_between(a, b):
    return [(x, float(m[0]), float(m[1])) for x, m in
            [(None, mm) for mm in re.findall(r"x: ([-\d.]+), z: ([-\d.]+)", src[a:b])]]

iC = src.index('  regionC: {'); iD = src.index('  regionD: {')
iW = src.index('    wolfPacks: [')
iS = src.index('separationPush')
iK = src.index('window.WH_CONFIG.cooking = {')

crows = [(float(m[0]), float(m[1])) for m in re.findall(r"x: ([-\d.]+), z: ([-\d.]+)", src[iC:iD])]
loops = [(float(m[0]), float(m[1])) for m in re.findall(r"\[(-?\d+(?:\.\d+)?), (-?\d+(?:\.\d+)?)\]", src[iW:iS])]
fires = [(float(m[0]), float(m[1])) for m in re.findall(r"x: ([-\d.]+), z: ([-\d.]+)", src[iK:iC])]
ex = [(float(m[0]), float(m[1])) for m in re.findall(r"x: ([-\d.]+), z: ([-\d.]+)", src[iC:iD])]

SPAWN = (0, -96); STONE = (0, -366); DEN_OPEN = (-163.4, -202.6)

def dist(a, b): return math.hypot(a[0] - b[0], a[1] - b[1])

# road centerlines approx
ROAD_SEG = [((0, -88), (0, -332))] + \
    [((34, -366), (240, -366)), ((-34, -366), (-240, -366)), ((0, -400), (0, -596))]
def d_road(x, z):
    best = max(0.0, math.hypot(x, z + 366) - 34)   # ring road
    for (a, b) in ROAD_SEG:
        ax, az = a; bx, bz = b
        ex_, ez_ = bx - ax, bz - az
        t = max(0, min(1, ((x - ax) * ex_ + (z - az) * ez_) / (ex_ * ex_ + ez_ * ez_)))
        best = min(best, math.hypot(x - (ax + ex_ * t), z - (az + ez_ * t)))
    return best

def site_ok(x, z, need_prop, need_road, need_fire, need_loop, others, min_other):
    r = math.hypot(x, z + 366)
    if not (120 <= r <= 246): return False
    if dist((x, z), SPAWN) < 55: return False
    if dist((x, z), STONE) < 56: return False
    if dist((x, z), DEN_OPEN) < 50: return False
    for p in crows:
        if dist((x, z), p) < need_prop: return False
    for f in fires:
        if dist((x, z), f) < need_fire: return False
    for l in loops:
        if dist((x, z), l) < need_loop: return False
    for o in others:
        if dist((x, z), o) < min_other: return False
    if d_road(x, z) < need_road: return False
    return True

def find(bear, r_lo, r_hi, need, others, min_other):
    for r in range(r_hi, r_lo - 1, -4):
        for jit in range(-10, 11, 5):
            a = math.radians(bear + jit)
            x, z = r * math.sin(a), -366 - r * math.cos(a)
            if site_ok(x, z, *need, others, min_other):
                return (round(x, 1), round(z, 1), r, bear + jit)
    return None

CAMP_BEAR = [30, 150, 260, 330]
camps, camp_pts = [], []
for b in CAMP_BEAR:
    s = find(b, 120, 246, (26, 35, 45, 60), camp_pts, 55)
    camps.append(s)
    if s: camp_pts.append((s[0], s[1])); fires.append((s[0], s[1]))

LOOP_BEAR = [10, 100, 190, 285]
packs = []
for b in LOOP_BEAR:
    s = find(b, 150, 242, (24, 40, 60, 60), camp_pts + [p[0:2] for p in packs if p], 65)
    packs.append(s)

# loop waypoint sets (8 pts)
loop_rows = []
for s in packs:
    if not s: continue
    rr = 30 + random.random() * 8
    pts = []
    for k in range(8):
        aa = 2 * math.pi * k / 8 + random.random() * 0.25
        rad = rr * (0.9 + random.random() * 0.2)
        pts.append([round(s[0] + rad * math.sin(aa), 1), round(s[1] + rad * math.cos(aa), 1)])
    loop_rows.append(pts)

print('CAMP SITES:', camps)
print('PACK SITES:', packs)
print('LOOPS:', loop_rows)
ok = all(camps) and all(packs)
print('ALL SITES FOUND' if ok else 'SOME NOT FOUND')
json.dump({'camps': camps, 'packs': packs, 'loops': loop_rows},
          open('/tmp/wh-worldfeat/scratch/cc-c16/sites.json', 'w'), indent=1)