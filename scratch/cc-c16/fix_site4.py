#!/usr/bin/env python3
"""CC-C16b: relocate camp 4 + pack 4 (nw2) away from banditFireB (95,-236) and
re-check. Camp 4 sits 42.4 m from Bravo's fire; needs >= 45. nudge r outward
along the same bearing until clear of B by 45+ and all other gates."""
import math, json, re

src = open('/tmp/wh-worldfeat/prototype/js/CONFIG.js').read()
S = json.load(open('/tmp/wh-worldfeat/scratch/cc-c16/sites.json'))
B = (95.0, -236.0)
A = (-60.0, -186.0); C6C = (-140.0, -506.0); D1 = (-106.1, -472.1); D2 = (118.0, -448.6); D3 = (-207.8, -246.0)
def dist(a, b): return math.hypot(a[0] - b[0], a[1] - b[1])

iC = src.index('  regionC: {')
props_txt = src[iC:src.index('      // CC-C16b DENSIFY')]
crows = [(float(m[0]), float(m[1])) for m in re.findall(r"\{ asset: '[a-zA-Z]+', x: ([-\d.]+), z: ([-\d.]+)", props_txt)]
SPAWN = (0, -96); STONE = (0, -366); DEN_OPEN = (-163.4, -202.6)
ROAD_SEG = [((0, -88), (0, -332)), ((34, -366), (240, -366)), ((-34, -366), (-240, -366)), ((0, -400), (0, -596))]
def d_road(x, z):
    best = max(0.0, math.hypot(x, z + 366) - 34)
    for (a, b) in ROAD_SEG:
        ax, az = a; bx, bz = b
        ex_, ez_ = bx - ax, bz - az
        t = max(0, min(1, ((x - ax) * ex_ + (z - az) * ez_) / (ex_ * ex_ + ez_ * ez_)))
        best = min(best, math.hypot(x - (ax + ex_ * t), z - (az + ez_ * t)))
    return best

def camp_ok(x, z):
    if dist((x, z), SPAWN) < 48 or dist((x, z), STONE) < 48: return False
    if dist((x, z), DEN_OPEN) < 48: return False
    for p in crows:
        if dist((x, z), p) < 26: return False
    for f in (A, B, C6C, D1, D2, D3):
        if dist((x, z), f) < 45: return False
    if d_road(x, z) < 35: return False
    return True

# camp 4: expand search around bearing ~130, r 150..210
found = None
for r in range(210, 150, -3):
    for jit in range(-14, 15, 2):
        a = math.radians(130 + jit)
        x, z = r * math.sin(a), -366 - r * math.cos(a)
        if camp_ok(x, z):
            found = (round(x, 1), round(z, 1), r, 130 + jit)
            break
    if found: break
print('NEW camp4:', found)
S['camps'][3] = found

# pack 4 (nw2) currently loops near (115..165, -500..-552) - vs camp 4 new + fireB:
# regenerate nw2's loop in a sector clear of D2/D3/B and the new camp4.
iW = src.index('    wolfPacks: ['); iS = src.index('separationPush')
old_loops = []
for m in re.finditer(r"id: '(\w+)', regionId: 'forest_of_the_old_king', members: 4, spawnSpread: 6,\s*(?://[^\n]*\n\s*)?waypoints: (\[\[[^\]]+\](?:,\s*\[[^\]]+\])*\])", src[iW:iS]):
    pts = re.findall(r"\[(-?\d+(?:\.\d+)?), (-?\d+(?:\.\d+)?)\]", m.group(2))
    old_loops.append((m.group(1), [(float(a), float(b)) for a, b in pts]))
old_pts = [p for pid, pts in old_loops for p in pts]
import itertools, random
random.seed(2026102004)
found_loop = None
for attempt in range(4000):
    bear = random.uniform(30, 55)
    r = random.uniform(185, 235)
    cx, cz = r * math.sin(math.radians(bear)), -366 - r * math.cos(math.radians(bear))
    rr = random.uniform(26, 34)
    pts = []
    good = True
    for k in range(8):
        aa = 2 * math.pi * k / 8 + random.random() * 0.3
        rad = rr * (0.85 + random.random() * 0.3)
        p = (round(cx + rad * math.sin(aa), 1), round(cz - rad * math.cos(aa), 1))
        if dist(p, B) < 45 or any(dist(p, q) < 30 for q in old_pts) or dist(p, (found[0], found[1])) < 48 \
           or dist(p, D2) < 45 or dist(p, D3) < 45 or any(dist(p, q) < 14 for q in crows):
            good = False; break
        pts.append(p)
    if not good: continue
    if dist((cx, cz), B) < 60 or dist((cx, cz), (found[0], found[1])) < 60: continue
    if d_road(cx, cz) < 36: continue
    found_loop = pts
    break
print('NEW loop4 pts:', found_loop)
S['loops'][3] = found_loop
S['packs'][3] = (found[0], found[1], found[2], found[3])
json.dump(S, open('/tmp/wh-worldfeat/scratch/cc-c16/sites.json', 'w'), indent=1)
print('sites.json updated')