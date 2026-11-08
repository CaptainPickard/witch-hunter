#!/usr/bin/env python3
"""CC-C16b: fix pack 4 (all wolf gates, no near-miss band). Wider scan."""
import math, json, re, random

src = open('/tmp/wh-worldfeat/prototype/js/CONFIG.js').read()
S = json.load(open('/tmp/wh-worldfeat/scratch/cc-c16/sites.json'))
B = (95.0, -236.0)
iC = src.index('  regionC: {')
props_txt = src[iC:src.index('      // CC-C16b DENSIFY')]
crows = [(float(m[0]), float(m[1])) for m in re.findall(r"\{ asset: '[a-zA-Z]+', x: ([-\d.]+), z: ([-\d.]+)", props_txt)]
iW = src.index('    wolfPacks: ['); iS = src.index('separationPush')
old_loops = []
for m in re.finditer(r"id: '(\w+)', regionId: 'forest_of_the_old_king', members: 4, spawnSpread: 6,\s*(?://[^\n]*\n\s*)?waypoints: (\[\[[^\]]+\](?:,\s*\[[^\]]+\])*\])", src[iW:iS]):
    pts = re.findall(r"\[(-?\d+(?:\.\d+)?), (-?\d+(?:\.\d+)?)\]", m.group(2))
    old_loops.append((m.group(1), [(float(a), float(b)) for a, b in pts]))
old_pts = [p for pid, pts in old_loops for p in pts]
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
camp4 = S['camps'][3]; D2 = S['camps'][1]; D3 = S['camps'][2]
# gates the brief actually needs: loop pts >= 30 from old loop pts, >= 40 from OLD
# fires, >= 14 from props, 36 off roads; loop centre >= 60 from camps + B.
random.seed(4242)
found = None
for attempt in range(9000):
    bear = random.uniform(20, 80)
    r = random.uniform(170, 240)
    cx, cz = r * math.sin(math.radians(bear)), -366 - r * math.cos(math.radians(bear))
    if dist((cx, cz), B) < 62: continue
    if any(dist((cx, cz), (c[0], c[1])) < 62 for c in S['camps']): continue
    if d_road(cx, cz) < 36: continue
    rr = random.uniform(24, 34)
    pts, ok = [], True
    for k in range(8):
        for _try in range(14):
            aa = 2 * math.pi * k / 8 + random.random() * 0.3
            rad = rr * (0.85 + random.random() * 0.3)
            p = (round(cx + rad * math.sin(aa), 1), round(cz - rad * math.cos(aa), 1))
            if dist(p, B) < 45: continue
            if any(dist(p, q) < 30 for q in old_pts): continue
            if any(dist(p, q) < 14 for q in crows): continue
            if dist(p, (camp4[0], camp4[1])) < 40: continue
            if dist(p, (D2[0], D2[1])) < 40 or dist(p, (D3[0], D3[1])) < 40: continue
            if d_road(*p) < 30: continue
            pts.append(p); break
        else:
            ok = False; break
    if ok and len(pts) == 8:
        found = pts
        print('NEW loop4 @ (%.0f, %.0f) r=%.0f bear=%.0f' % (cx, cz, r, bear))
        break
if not found:
    print('NO SITE — widen radius/bearing band')
    raise SystemExit(1)
S['loops'][3] = found
S['packs'][3][0], S['packs'][3][1] = round(sum(p[0] for p in found) / 8, 1), round(sum(p[1] for p in found) / 8, 1)
json.dump(S, open('/tmp/wh-worldfeat/scratch/cc-c16/sites.json', 'w'), indent=1)
print('sites.json updated: pack4 loop centre (%.1f, %.1f)' % (S['packs'][3][0], S['packs'][3][1]))