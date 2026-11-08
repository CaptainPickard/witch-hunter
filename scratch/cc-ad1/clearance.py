#!/usr/bin/env python3
"""CC-AD1 clearance checker (valspec V12). Regex-scans CONFIG.js's regionE
block for enemy rows / prop rows / door.interactAt / land rows, computes pure
Euclidean distances, prints one line per pair with ok/FAIL + margin. Exit 0 =
every row ok. Wall-distance law: ring centerline r 18, inner walking edge
r ~16 -> distance to nearest wall ~ (16 - rho) for interior points.
Run: python3 scratch/cc-ad1/clearance.py
"""
import math
import re
import sys

CONFIG = 'prototype/js/CONFIG.js'

src = open(CONFIG, encoding='utf-8').read()
m = re.search(r'  regionE: \{(.*?)\n  \},\n', src, re.S)
if not m:
    print('regionE block not found'); sys.exit(1)
block = m.group(1)

CX, CZ = 0.0, -596.0                     # crypt center (world)
R_INNER = 16.0                           # ring inner walking edge
WALL_MIN = 4.0
SPAWN_MIN = 6.0
COVEN_MIN = 5.0
LAND_MIN = 8.0

def rows(pat):
    out = []
    for line in block.splitlines():
        mm = re.search(pat, line)
        if mm:
            out.append(line.strip())
    return out

# enemies: { type: 'coven', x: 5, z: -592 }
enemies = []
for line in rows(r"type:\s*'coven'"):
    x = float(re.search(r'x:\s*(-?[\d.]+)', line).group(1))
    z = float(re.search(r'z:\s*(-?[\d.]+)', line).group(1))
    enemies.append((x, z))

# props: { asset: 'name', x: .., z: .., ... }  (ring walls carry wall: N)
props = []
for line in rows(r"asset:\s*'[a-zA-Z]+'"):
    if 'wall:' in line:
        continue
    x = float(re.search(r'x:\s*(-?[\d.]+)', line).group(1))
    z = float(re.search(r'z:\s*(-?[\d.]+)', line).group(1))
    name = re.search(r"asset:\s*'([a-zA-Z]+)'", line).group(1)
    props.append((name, x, z))

# wall rows (ring): asset whWallA/whWallB with wall: N; colliders approximated
# as N points spread evenly along each row's chord (row width = scale x 1.899)
walls = []
for line in rows(r"asset:\s*'whWall[AB]'"):
    if 'wall:' not in line:
        continue
    x = float(re.search(r'x:\s*(-?[\d.]+)', line).group(1))
    z = float(re.search(r'z:\s*(-?[\d.]+)', line).group(1))
    ry = float(re.search(r'rotY:\s*(-?[\d.]+)', line).group(1))
    sc = float(re.search(r'scale:\s*([\d.]+)', line).group(1))
    n = int(re.search(r'wall:\s*(\d+)', line).group(1))
    chord = sc * 1.899
    ax, az = math.cos(ry), -math.sin(ry)          # region-manager whPropColliders local-X axis
    for k in range(n):
        t = ((k + 0.5) / n - 0.5) * chord
        walls.append((x + ax * t, z + az * t))

# spawn/land: the door.land.veil_crypt row
land = None
mm = re.search(r"veil_crypt:\s*\{\s*x:\s*(-?[\d.]+),\s*z:\s*(-?[\d.]+)", block)
if mm:
    land = (float(mm.group(1)), float(mm.group(2)))

ok_all = True
def say(label, val, req, le=False):
    global ok_all
    good = (val <= req) if le else (val >= req)
    ok_all = ok_all and good
    print('%-52s %7.2f %s %4.1f  %s  (margin %.2f)' % (
        label, val, '<=' if le else '>=', req, 'ok' if good else 'FAIL',
        (req - val) if le else (val - req)))

print('coven rows: %d | prop rows: %d | wall rows: %d | land: %s' % (
    len(enemies), len(props), len(walls), land))

say('land -> center (inside r 20)', math.hypot(land[0] - CX, land[1] - CZ), 20.0, le=True)
for i, c in enumerate(enemies, 1):
    say('coven%d -> land (>= %.1f)' % (i, LAND_MIN), math.hypot(c[0] - land[0], c[1] - land[1]), LAND_MIN)
if len(enemies) == 2:
    say('coven1 <-> coven2 (>= 8.0)', math.hypot(enemies[0][0] - enemies[1][0], enemies[0][1] - enemies[1][1]), 8.0)
for i, c in enumerate(enemies, 1):
    rho = math.hypot(c[0] - CX, c[1] - CZ)
    say('coven%d -> nearest wall (>= %.1f, 16-rho law)' % (i, WALL_MIN), R_INNER - rho, WALL_MIN, le=False)
for name, x, z in props:
    rho = math.hypot(x - CX, z - CZ)
    say('prop %-16s -> nearest wall (>= %.1f)' % (name, WALL_MIN), R_INNER - rho, WALL_MIN)
    say('prop %-16s -> land (>= %.1f)' % (name, SPAWN_MIN), math.hypot(x - land[0], z - land[1]), SPAWN_MIN)
    for j, c in enumerate(enemies, 1):
        d = math.hypot(x - c[0], z - c[1])
        say('prop %-16s -> coven%d (>= %.1f)' % (name, j, COVEN_MIN), d, COVEN_MIN)

print('\nALL CONSTRAINTS: %s' % ('PASS' if ok_all else 'FAIL'))
sys.exit(0 if ok_all else 1)
