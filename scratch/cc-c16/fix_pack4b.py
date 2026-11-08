#!/usr/bin/env python3
"""CC-C16b: fix pack 4 (the last violations) with a wide honest scan and NO
near-miss: every loop point >= 30 from old loops, >= 45 from every fire,
>= 14 from props, road >= 30; centre >= 62 from all camps + B. Also checks
the FINAL camp set."""
import math, json, re, random

src = open('/tmp/wh-worldfeat/prototype/js/CONFIG.js').read()
S = json.load(open('/tmp/wh-worldfeat/scratch/cc-c16/sites.json'))
camp_pts = [(c[0], c[1]) for c in S['camps']]
B = (95.0, -236.0); A = (-60.0, -186.0); C6 = (-140.0, -506.0)
def dist(a, b): return math.hypot(a[0] - b[0], a[1] - b[1])
iC = src.index('  regionC: {')
props_txt = src[iC:src.index('      // CC-C16b DENSIFY')]
crows = [(float(m[0]), float(m[1])) for m in re.findall(r"\{ asset: '[a-zA-Z]+', x: ([-\d.]+), z: ([-\d.]+)", props_txt)]
iW = src.index('    wolfPacks: ['); iS = src.index('separationPush')
old_loops = []
for m in re.finditer(r"id: '(\w+)', regionId: 'forest_of_the_old_king', members: 4, spawnSpread: 6,\s*(?://[^\n]*\n\s*)?waypoints: (\[\[[^\]]+\](?:,\s*\[[^\]]+\])*\])", src[iW:iS]):
    pts = re.findall(r"\[(-?\d+(?:\.\d+)?), (-?\d+(?:\.\d+)?)\]", m.group(2))
    old_loops.append((m.group(1), [(float(a), float(b)) for a, b in pts]))
old_pts = [p for pid, pts in old_loops for p in pts]
ROAD_SEG = [((0, -88), (0, -332)), ((34, -366), (240, -366)), ((-34, -366), (-240, -366)), ((0, -400), (0, -596))]
def d_road(x, z):
    best = max(0.0, math.hypot(x, z + 366) - 34)
    for (a, b) in ROAD_SEG:
        ax, az = a; bx, bz = b
        ex_, ez_ = bx - ax, bz - az
        t = max(0, min(1, ((x - ax) * ex_ + (z - az) * ez_) / (ex_ * ex_ + ez_ * ez_)))
        best = min(best, math.hypot(x - (ax + ex_ * t), z - (az + ez_ * t)))
    return best

random.seed(777_004)
found = None
for attempt in range(16000):
    bear = random.uniform(15, 95)
    r = random.uniform(150, 244)
    cx, cz = r * math.sin(math.radians(bear)), -366 - r * math.cos(math.radians(bear))
    if any(dist((cx, cz), c) < 62 for c in camp_pts + [B, A, C6]): continue
    if d_road(cx, cz) < 40: continue
    rr = random.uniform(24, 34)
    pts, ok = [], True
    for k in range(8):
        for _try in range(18):
            aa = 2 * math.pi * k / 8 + random.random() * 0.35
            rad = rr * (0.8 + random.random() * 0.35)
            p = (round(cx + rad * math.sin(aa), 1), round(cz - rad * math.cos(aa), 1))
            if dist(p, B) >= 45 and dist(p, A) >= 45 and dist(p, C6) >= 45 \
               and all(dist(p, q) >= 30 for q in old_pts) \
               and all(dist(p, c) >= 45 for c in camp_pts) \
               and all(dist(p, q) >= 14 for q in crows) and d_road(*p) >= 30:
                pts.append(p); break
        else:
            ok = False; break
    if ok:
        found = pts
        print('NEW pack4 loop @ (%.0f,%.0f) r=%.0f bear=%.0f' % (cx, cz, r, bear))
        break
if not found:
    raise SystemExit('NO PACK4 SITE — escalate to IO')
S['loops'][3] = found
S['packs'][3] = (round(sum(p[0] for p in found)/8, 1), round(sum(p[1] for p in found)/8, 1), r, round(bear, 1))
json.dump(S, open('/tmp/wh-worldfeat/scratch/cc-c16/sites.json', 'w'), indent=1)
print('centre:', S['packs'][3][0], S['packs'][3][1])