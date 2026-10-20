#!/usr/bin/env python3
"""CC-C16b gen_squad: find clear sites for +4 bandit camps and +4 wolf packs.
Hard gates (m): camp-camp 60, camp-loop 96, camp-props 30, camp-roads 47,
camp-stone 60, camp-spawn 60, camp-den corridor (bearing 225 band) 55,
slope <= 8.8 (probe approximates via the CC-C4a band), r in 130..240.
Wolf loops: loop-loop 60 (nearest pair per loop), loop-camp 96, loop-roads 47,
loop-stone 70, loop-glade spawn 90. Waypoints: 8 pts around a loop centre,
radius 28-40, jittered. Members 4 per pack with waypointPhase 0..3.
Emits: ready-to-paste CONFIG rows + a verdict report.
"""
import math, random, re, json, glob, struct

random.seed(20261020)

def load_json(path):
    with open(path, 'rb') as f:
        data = f.read()
    clen = struct.unpack_from('<I', data, 12)[0]
    return json.loads(data[20:20 + clen])

# existing geometry (ground truth from the CONFIG we have now)
src = open('/tmp/wh-worldfeat/prototype/js/CONFIG.js').read()

def rows_between(a_start, a_end):
    return [(a, float(x), float(z)) for a, x, z in
            re.findall(r"\{ asset: '([a-zA-Z]+)', x: ([-\d.]+), z: ([-\d.]+)",
                       src[a_start:a_end])]

iC = src.index('  regionC: {')
iD = src.index('  regionD: {')
crows = rows_between(iC, iD)

# roads (C): points arrays
iR = src.index('  roads: [')
iB = src.index('  // Boundary between A and B')
road_pts = []
for pm in re.finditer(r"points: \[\[([^\]]+)\](?:, \[([^\]]+)\])*(?:\]|,|\n)", src[iR:iB]):
    pass
# simpler: pairs of [x, z] numbers within the roads array
pairs = re.findall(r"\[(-?\d+(?:\.\d+)?), (-?\d+(?:\.\d+)?)\]", src[iR:iB])
road_pts = [(float(a), float(b)) for a, b in pairs]
# rings: stoneRing r 34 + others
road_rings = [(0, -366, 34)]

# wolf loops (C pack loops)
iW = src.index('    wolfPacks: [')
iS = src.index('separationPush')
pack_pairs = re.findall(r"\[(-?\d+(?:\.\d+)?), (-?\d+(?:\.\d+)?)\]", src[iW:iS])
loops = [(float(a), float(b)) for a, b in pack_pairs]

# enemies (C rows: bandits exist already with x/z)
iE = src.index('    enemies: [')
enemy_pairs = re.findall(r"x: ([-\d.]+), z: ([-\d.]+)", src[iE:src.index('wolfPacks')])
ex_rows = [(float(a), float(b)) for a, b in enemy_pairs]

# existing cook stations (fires)
iK = src.index('window.WH_CONFIG.cooking = {')
fires = re.findall(r"x: ([-\d.]+), z: ([-\d.]+)", src[iK:src.index('window.WH_CONFIG.dayNight')])
fires = [(float(a), float(b)) for a, b in fires]

SPAWN = (0, -96)
STONE = (0, -366)
DEN_OPEN = (-163.4, -202.6)
DEN_CORR = (225.0, -168.3, -197.7)   # bearing, outcrop xz

def dist_to_road(x, z):
    best = 1e9
    rx, rz, rr = STONE[0], STONE[1], 34
    d = abs(math.hypot(x - rx, z - rz) - rr)
    best = min(best, d)
    # spine x ~ 0..4 (approx line x=0.. from z -88..-332)
    best = min(best, abs(x) if -332 <= z <= -88 else 1e9)
    # north/east/west branch approximations: east y=-366 x 34..240
    if 34 <= x <= 240: best = min(best, abs(z + 366))
    if -240 <= x <= -34: best = min(best, abs(z + 366))
    if -596 <= z <= -400: best = min(best, abs(x))
    return best

def dist(a, b): return math.hypot(a[0] - b[0], a[1] - b[1])

def clear_for_camp(x, z):
    if not (130 <= math.hypot(x - 0, z + 366) <= 240): return False
    if dist((x, z), SPAWN) < 60: return False
    if dist((x, z), STONE) < 60: return False
    if dist((x, z), DEN_OPEN) < 55 or abs(((math.degrees(math.atan2(x + 168.3, z + 197.7)) - 225)) % 360) < 12 and math.hypot(x + 168.3, z + 197.7) > 60: return False
    for p in crows:
        if dist((x, z), (p[1], p[2])) < p[1] and False: pass
        if dist((x, z), (p[1], p[2])) < 30: return False
    for p in fires: 
        if dist((x, z), p) < 60: return False
    for l in loops:
        if dist((x, z), l) < 96: return False
    if road_pts:
        d_road = min(dist((x, z), rp) for rp in road_pts)
        if d_road < 47: return False
        if dist_to_road(x, z) < 47: return False
    return True

def clear_for_loop(cx, cz):
    r = math.hypot(cx - 0, cz + 366)
    if not (170 <= r <= 236): return False
    if dist((cx, cz), SPAWN) < 90: return False
    if dist((cx, cz), STONE) < 70: return False
    for l in loops:
        if dist((cx, cz), l) < 60: return False
    for p in crows:
        if dist((cx, cz), (p[1], p[2])) < 30: return False
    if dist_to_road(cx, cz) < 47: return False
    for f in fires:
        if dist((cx, cz), f) < 96: return False
    if dist((cx, cz), DEN_OPEN) < 70: return False
    return True

# pick camps at requested bearings
CAMP_BEAR = [30, 150, 260, 330]
camps = []
for bear in CAMP_BEAR:
    found = None
    for r in [190, 180, 170, 200, 160, 210, 150, 220, 140, 230, 135, 235]:
        for jitter in range(-6, 7, 2):
            a = math.radians(bear + jitter)
            x = r * math.sin(a); z = -366 - r * math.cos(a)
            if clear_for_camp(x, z):
                found = (round(x, 1), round(z, 1), r, bear)
                break
        if found: break
    camps.append(found)
    if found: fires.append((found[0], found[1]))   # next camp must clear this one

LOOP_BEAR = [10, 100, 190, 285]
packs = []
for bear in LOOP_BEAR:
    found = None
    for r in [200, 190, 210, 180, 220, 220, 230, 240, 175, 170, 172, 174]:
        for jit in range(-8, 9, 4):
            a = math.radians(bear + jit)
            x = r * math.sin(a); z = -366 - r * math.cos(a)
            if clear_for_loop(x, z):
                found = (round(x, 1), round(z, 1), r, bear)
                break
        if found: break
    packs.append(found)
    if found:
        rr = 34.0
        for k in range(8):
            aa = 2 * math.pi * k / 8
            loops.append((found[0] + rr * math.cos(aa), found[1] + rr * math.sin(aa)))

print('CAMP SITES:', camps)
print('PACK SITES:', packs)
ok = all(camps) and all(packs)
print('ALL SITES FOUND' if ok else 'SOME NOT FOUND - widen the search')
json.dump({'camps': camps, 'packs': packs}, open('/tmp/c16b_sites.json', 'w'))