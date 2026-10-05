#!/usr/bin/env python3
"""Order 3 final placement generator v3 (Nicko 10-03 orders) -> forest_plan2.txt.

Ring 46 @ ~4.2m spacing on r 27.5-31.5 band around yard center (0,11), mouth
sector + gate corridor excluded. Alley yew+ash flanks. Rim yews. Dead accents.
Path lanterns trimmed to the shortened path span (z 86->32). Enemies 8."""
import math

RS = [20261003]

def rand():
    state = RS[0]
    RS[0] = (RS[0] + 0x6D2B79F5) & 0xFFFFFFFF
    t = state ^ (state >> 15)
    t = (t * (t | 1)) & 0xFFFFFFFF
    t = ((t + ((t ^ (t >> 7)) + (t | 0))) & 0xFFFFFFFF) | 0
    t = (state ^ (state >> 61)) ^ t
    t = (t * (t | 1)) & 0xFFFFFFFF
    t ^= t >> 14
    return t / 4294967296

YARD_C = (0.0, 11.0)
MOUTH_HALF = 0.30
SPAWN = (0.0, 45.0)
ENEMIES_EXISTING = [(-6, -8), (10, -14), (2, -23.5)]
# lanterns that survive order 3: path span (z 86->32) + 2 canon yard posts
LANTERNS = [(5.04, 62.0), (-4.2, 51.0), (2.6, 39.5), (-2, 30), (4, -2)]
GRAVE_PROPS = [
    (-10, 20), (-13, 17), (12, 22), (-5, 15), (8, 12), (3, 24), (15, 6),
    (-18, 5), (15.4, 13.2), (12.2, 12.2), (-19.1, 10.8), (-19.8, 7.6),
    (-20.8, 13.3), (-5.6, 28.9), (-7.6, 31.1), (7.2, 18.4), (-8.4, 8.3),
    (-13.0, -7.1), (-11.4, 12.7), (5.5, 8.5), (-2.5, -6.5), (10.5, -14.5),
    (-15.5, 3.5), (15.5, -2.5), (-4.5, -12.5), (12.5, 2.5), (16.5, 10.5),
    (18.5, 14.5), (20.5, 11.5), (-14.5, 20.5), (-17.5, 24.5), (6.5, 12.5),
    (-20.5, -12.5), (20.5, 2.5), (29.4, 1.3), (-27.8, -19.9), (26.0, 9.0)]

def in_yard(x, z):
    if -1 <= z <= 24 and abs(x) <= 21: return True
    if 24 < z <= 32.5 and abs(x) <= 4: return True
    return False

def in_corridor(x, z):
    return -5.5 <= x <= 5.5 and -32.0 <= z <= -18.0

def path_x(z):
    return 1.6 * math.sin(2 * math.pi * (z - 48.0) / 34.0)

placed_trees = []

def ok(x, z, minsep, path_clear):
    if x * x + z * z > 84 ** 2: return 'radius'
    if z <= -23.2: return 'z-plane'
    if in_corridor(x, z): return 'corridor'
    if in_yard(x, z): return 'graveyard'
    if path_clear is not None and abs(x - path_x(z)) < path_clear: return 'path'
    if math.hypot(x - SPAWN[0], z - SPAWN[1]) < 9: return 'spawn'
    for ex, ez in ENEMIES_EXISTING:
        if math.hypot(x - ex, z - ez) < 7.5: return 'enemy'
    for lx, lz in LANTERNS:
        if math.hypot(x - lx, z - lz) < 4.0: return 'lantern'
    for px, pz in GRAVE_PROPS:
        if math.hypot(x - px, z - pz) < 5.0: return 'prop'
    for t in placed_trees:
        if math.hypot(x - t[1], z - t[2]) < minsep: return 'spacing'
    return None

def fmt(asset, x, z, sc):
    return "      { asset: '%s', x: %.2f, z: %.2f, rotY: %.2f, scale: %.2f }," % (
        asset, x, z, rand() * 6.283, sc)

ring_lines, alley_lines, rim_lines, dead_lines = [], [], [], []
rejects = {}

# ---- 1. ring 46 ----
ARC = 2 * math.pi - 2 * MOUTH_HALF
placed_ring, slot = 0, 0
while placed_ring < 46 and slot < 400:
    base_a = (slot * ARC / 46.0) + MOUTH_HALF
    slot += 1
    for _ in range(14):   # radius jitter attempts per slot
        a = base_a + (rand() - 0.5) * 0.14
        r = 27.5 + rand() * 4.0
        x = YARD_C[0] + math.sin(a) * r
        z = YARD_C[1] + math.cos(a) * r
        if in_yard(x, z):
            rejects['graveyard'] = rejects.get('graveyard', 0) + 1
            continue
        roll = rand()
        kind = 'yewTree' if roll < 0.55 else (
            'livingOak' if roll < 0.8 else 'witchwoodTree')
        sc = 8.4 + rand() * 2.4
        rej = ok(x, z, 4.2, 5.8)
        if rej:
            rejects[rej] = rejects.get(rej, 0) + 1
            continue
        placed_trees.append((kind, x, z))
        ring_lines.append(fmt(kind, x, z, sc))
        placed_ring += 1
        break

# ---- 1b. ring filler: top the ring up on an outer band 32.5..37.5 ----
while placed_ring < 46:
    a = rand() * 2 * math.pi
    r = 32.5 + rand() * 5.0
    x = YARD_C[0] + math.sin(a) * r
    z = YARD_C[1] + math.cos(a) * r
    if in_yard(x, z): continue
    roll = rand()
    kind = 'yewTree' if roll < 0.55 else (
        'livingOak' if roll < 0.8 else 'witchwoodTree')
    sc = 8.4 + rand() * 2.4
    rej = ok(x, z, 4.0, 5.8)
    if rej: continue
    placed_trees.append((kind, x, z))
    ring_lines.append(fmt(kind, x, z, sc))
    placed_ring += 1

# ---- 2. alley z 84..33: path_clear must be SMALLER than the tree's own offset ----
z = 84.0
while z > 33:
    for side in (-1, 1):
        off = 6.6 + rand() * 3.6
        jz = z + (rand() * 3.0 - 1.5)
        x = path_x(jz) + side * off
        roll = rand()
        if roll < 0.75:
            kind, sc = 'yewTree', 8.6 + rand() * 2.0
        else:
            kind, sc = 'youngAsh', 8.0 + rand() * 1.6
        rej = ok(x, jz, 5.0, max(0.0, off - 1.9))
        if rej:
            continue
        placed_trees.append((kind, x, jz))
        alley_lines.append(fmt(kind, x, jz, sc))
    z -= 6.2

# ---- 3. rim ----
rim, tries = 0, 0
while rim < 26 and tries < 600:
    tries += 1
    x = (rand() * 2 - 1) * 82
    z = -22.0 + rand() * 108
    if ok(x, z, 7.0, 6.0): continue
    if math.hypot(x - YARD_C[0], z - YARD_C[1]) < 36: continue
    placed_trees.append(('yewTree', x, z))
    rim_lines.append(fmt('yewTree', x, z, 8.2 + rand() * 2.4))
    rim += 1

# ---- 4. dead accents ----
dead, tries = 0, 0
while dead < 4 and tries < 400:
    tries += 1
    x = (rand() * 2 - 1) * 80
    z = -20.0 + rand() * 104
    if ok(x, z, 8.5, 6.0): continue
    if math.hypot(x - YARD_C[0], z - YARD_C[1]) < 34: continue
    if math.hypot(x, z - 45) < 30: continue
    placed_trees.append(('deadTree', x, z))
    dead_lines.append(fmt('deadTree', x, z, 7.5 + rand() * 2.0))
    dead += 1

# ---- 5. forest enemies (8) ----
enemy_lines = []
prev_positions = []
need = ['bandit', 'ghoul', 'bandit', 'ghoul', 'bandit', 'ghoul', 'bandit', 'ghoul']
spawned, tries = 0, 0
while spawned < 8 and tries < 800:
    tries += 1
    x = (rand() * 2 - 1) * 74
    z = -20.0 + rand() * 100
    if abs(x - path_x(z)) < 10: continue
    if math.hypot(x - SPAWN[0], z - SPAWN[1]) < 16: continue
    if in_yard(x, z) or in_corridor(x, z): continue
    if math.hypot(x - YARD_C[0], z - YARD_C[1]) < 30: continue
    bad = False
    for ex, ez in ENEMIES_EXISTING + prev_positions:
        if math.hypot(x - ex, z - ez) < 12: bad = True
    for t in placed_trees:
        if math.hypot(x - t[1], z - t[2]) < 4.5: bad = True
    for lx, lz in LANTERNS:
        if math.hypot(x - lx, z - lz) < 6: bad = True
    if bad: continue
    prev_positions.append((x, z))
    enemy_lines.append("      { type: '%s', x: %.1f, z: %.1f }," % (need[spawned], x, z))
    spawned += 1

print('ring=%d alley=%d rim=%d dead=%d enemies=%d total_trees=%d maxR=%.1f' % (
    len(ring_lines), len(alley_lines), len(rim_lines), len(dead_lines),
    len(enemy_lines), len(ring_lines) + len(alley_lines) + len(rim_lines) + len(dead_lines),
    max(math.hypot(t[1], t[2]) for t in placed_trees) if placed_trees else 0))
print('ring rejects:', dict(sorted(rejects.items(), key=lambda kv: -kv[1])[:5]))

with open('/workspace/forest_plan2.txt', 'w') as f:
    for name, lines in (('ring', ring_lines), ('alley', alley_lines),
                        ('rim', rim_lines), ('dead', dead_lines),
                        ('enemies', enemy_lines)):
        f.write('# === %s %d ===\n' % (name, len(lines)))
        f.write('\n'.join(lines) + '\n')