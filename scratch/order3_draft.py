#!/usr/bin/env python3
"""Order 3 placement draft (NOT applied - Astrabot owns the worktree right now).

Redesign of the region A forest with Nicko's 10-03 corrections:
1. Trees form a circle AROUND the whole graveyard - NOTHING inside the yard.
2. Dirt path ENDS at the graveyard entrance (south fence line, z ~ 32).
3. Many more enemies strewn through the forest outside the yard.

Geometry truth (from CONFIG regionA props):
- Yard footprint: fenced east (picketFence x 12-15, z 12-13) + west/north iron
  fence (x -7..-5, z 29-31; x -19..-21, z 7..13 line) - the ground the yard
  occupies: centered ~(0, 8), radius ~26 covers all graves/fences/statue.
- Tree ring: annulus around the yard: centroid dist from (0,8) in [28, 62],
  clamped to playable r 84 (world center), z > -21 (plane margin -25 - 4).
- Path: zFrom 86 (south rim) -> zTo 32 (fence threshold): the walk ENDS at
  first entry to the graveyard. Alley flanks z 86..34 ONLY.
- Lanterns: path span only (z 62, 51, 39.5, 34.5 alternating) + the 2 canon
  yard posts (existing at (-2,30), (4,-2)) stay untouched.
- Enemies: ring-straddling encounters between trees: bandit/ghoul pairs,
  outside yard, off-path 7+, spawn-clear 10+, z > -21, r < 84.
"""
import math

# --- shared path curve (SAME as shipped cf82f1f, unclamped sway) ----------
def path_x(z):
    return 1.6 * math.sin(2 * math.pi * (z - 48.0) / 34.0)

# --- deterministic rng (fixed seed so re-runs are stable) -------------------
def mulberry32(seed):
    def rng():
        seed[0] = (seed[0] + 0x6D2B79F5) & 0xFFFFFFFF
        t = seed[0]
        t = (t ^ (t >> 15)) * (t | 1) & 0xFFFFFFFF
        t = (t + (t ^ (t >> 7)) * (t | 61)) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296
    return rng, [20261003]

rng, sbox = mulberry32(20261003)
rng = (lambda f, box: lambda: f(box[1]))  # noqa - simple wrapper, see below

# simpler: closure-style rng
def make_rng(seed):
    state = seed
    def r():
        nonlocal state
        state = (state + 0x6D2B79F5) & 0xFFFFFFFF
        t = state
        t = ((t ^ (t >> 15)) * (t | 1)) & 0xFFFFFFFF
        t = (t + ((t ^ (t >> 7)) * (t | 61))) & 0xFFFFFFFF
        return ((t ^ (t >> 14))) / 4294967296
    return r
rng = make_rng(20261003)

# --- constraints -----------------------------------------------------------
YARD_C = (0.0, 8.0)      # graveyard centroid
YARD_R = 26.0            # yard clearance radius (trees NEVER inside)
R_PLAY = 84.0            # radial clearance cap (playable 88.5 - margin)
Z_MIN = -21.0            # north plane margin (boundary -25, keep 4 clear)
PATH_HW = 3.25           # path half width (5.4m path -> 6.5 clearance used)
SPAWN = (0, 45)
CLOAK = [(  # keep-clear list from regionA props that must stay reachable
    'lanternPost', (-2, 30)), ('lanternPost', (4, -2)),
]

EXISTING_TREES = [   # healthy m5 yew already placed (keep, no collision dup)
    (29.4, 1.3),   # yewTree 6.5
]

ENEMIES = [(-6, -8), (10, -14), (2, -23.5)]  # existing bandits/ghoul

def in_yard(x, z):
    return math.hypot(x - YARD_C[0], z - YARD_C[1]) < YARD_R

placed = []          # (x, z) tree positions
rejects = {}
lanterns = []

def clear(x, z):
    if math.hypot(x, z) > R_PLAY: return 'radius'
    if z < Z_MIN: return 'z-plane'
    if in_yard(x, z): return 'graveyard'          # THE new hard rule
    if math.hypot(x - SPAWN[0], z - SPAWN[1]) < 8: return 'spawn'
    for ex, ez in ENEMIES:
        if math.hypot(x - ex, z - ez) < 7.5: return 'enemy'
    for tx, tz in placed + EXISTING_TREES:
        if math.hypot(x - tx, z - tz) < 5.0: return 'spacing'
    if abs(x - path_x(z)) < 6.5 and 30.0 <= z: return 'path'
    if CORRIDOR['x0'] <= x <= CORRIDOR['x1'] and CORRIDOR['z0'] <= z <= CORRIDOR['z1']:
        return 'corridor'
    return None

CORRIDOR = {'x0': -9, 'x1': 9, 'z0': -31.5, 'z1': -18.5}

# --- 1. tree wall: annulus AROUND the yard (full circle, both hemispheres) --
import json
arc_tries = 0
N_TARGET = 46
placed_ring = 0
while placed_ring < N_TARGET and arc_tries < N_TARGET * 40:
    arc_tries += 1
    ang = rng() * 2 * math.pi
    rad = YARD_R + 2.5 + rng() * (34 - 2.5)
    x = YARD_C[0] + math.cos(ang) * rad
    z = YARD_C[1] + math.sin(ang) * rad
    why = clear(x, z)
    if why:
        rejects[why] = rejects.get(why, 0) + 1
        continue
    placed.append((x, z))
    placed_ring += 1

# --- 2. outer rim scatter (between ring and world edge) --------------------
rim = 0
rim_tries = 0
while rim < 34 and rim_tries < 1600:
    rim_tries += 1
    x = (rng() * 2 - 1) * R_PLAY
    z = Z_MIN + rng() * (86 - Z_MIN)
    why = clear(x, z)
    if why:
        rejects[why] = rejects.get(why, 0) + 1
        continue
    placed.append((x, z))
    rim += 1

# --- 3. lanterns on the retained path span only -----------------------------
for zz in (62.0, 51.0, 39.5, 34.5):
    lanterns.append((round(path_x(zz) + (3.2), 2), zz))

# --- 4. forest enemies strewn between trees ---------------------------------
new_enemies = []
tries = 0
while len(new_enemies) < 8 and tries < 2000:
    tries += 1
    x = (rng() * 2 - 1) * (R_PLAY - 12)
    z = Z_MIN + rng() * (80 - Z_MIN)
    if math.hypot(x, z) > R_PLAY - 10: continue
    if in_yard(x, z): continue
    if abs(x - path_x(z)) < 7.0: continue
    if math.hypot(x - SPAWN[0], z - SPAWN[1]) < 14: continue
    ok = True
    for ex, ez in ENEMIES + new_enemies:
        if math.hypot(ex - x, ez - z) < 11: ok = False
    for tx, tz in placed:
        if math.hypot(x - tx, z - tz) < 4: ok = False
    if ok:
        new_enemies.append((round(x, 1), round(z, 1)))

types = ['bandit', 'ghoul', 'bandit', 'bandit', 'ghoul', 'ghoul', 'bandit', 'ghoul']

print(f"trees: ring={placed_ring} rim={rim} total={len(placed)}")
print(f"rejects: {rejects}")
print(f"lanterns (path span): {lanterns}")
print(f"new enemies ({len(new_enemies)}):")
for (ex, ez), t in zip(new_enemies, types):
    print(f"      {{ type: '{t}', x: {ex}, z: {ez} }},")
print()
print("=== regionA forest lines (ADD) ===")
for x, z in placed:
    sc = round(8.4 + rng() * 2.4, 2)
    print(f"      {{ asset: 'yewTree', x: {round(x, 2)}, z: {round(z, 2)}, rotY: {round(rng() * 6.283, 2)}, scale: {sc} }},")
print()
print("=== regionA lantern lines (ADD; z 20/8/-5/-16.5 posts REMOVED) ===")
for lx, lz in lanterns:
    print(f"      {{ asset: 'lanternPost', x: {lx}, z: {lz}, rotY: 0.0, scale: 2.4 }},")