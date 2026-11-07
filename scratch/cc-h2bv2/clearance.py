#!/usr/bin/env python3
"""CC-H2b live CONFIG/connection clearance, adapted from cc-h2/clearance.py."""
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
cfg = (ROOT / 'prototype/js/CONFIG.js').read_text()
rdefs = (ROOT / 'prototype/js/region-defs.js').read_text()
fails = []
checks = 0


def ok(label, condition, detail=''):
    global checks
    checks += 1
    if not condition:
        fails.append(label)
    print('%s: %s %s' % (label, 'PASS' if condition else 'FAIL', detail))


def minimum(label, value, threshold):
    ok(label, value + 1e-8 >= threshold, 'raw=%.4f >= %.4f' % (value, threshold))


def maximum(label, value, threshold):
    ok(label, value <= threshold + 1e-8, 'raw=%.4f <= %.4f' % (value, threshold))


def block(source, key):
    match = re.search(r'\n  %s: \{' % re.escape(key), source)
    assert match, 'missing region ' + key
    rest = source[match.start():]
    next_block = re.search(r'\n  [a-zA-Z_]+: \{', rest[10:])
    return rest[:10 + next_block.start()] if next_block else rest


def number(source, key):
    match = re.search(r'\b%s: (-?[\d.]+)' % re.escape(key), source)
    assert match, 'missing ' + key
    return float(match.group(1))


def point(source, name):
    match = re.search(r'\b%s:\s*\{ x: (-?[\d.]+), z: (-?[\d.]+)' % re.escape(name), source)
    assert match, 'missing point ' + name
    return float(match.group(1)), float(match.group(2))


def rows(source, kind):
    text = source.split(kind + ': [', 1)[1].split('\n    ]', 1)[0]
    if kind == 'enemies':
        return [(m.group(1), float(m.group(2)), float(m.group(3))) for m in
                re.finditer(r"\{ type: '(\w+)', x: (-?[\d.]+), z: (-?[\d.]+) \}", text)]
    return [dict(asset=m.group(1), x=float(m.group(2)), z=float(m.group(3)),
                 rotY=float(m.group(4)), scale=float(m.group(5)),
                 wall=int(m.group(6)) if m.group(6) else None) for m in
            re.finditer(r"\{ asset: '(\w+)',\s*x: (-?[\d.]+), z: (-?[\d.]+), rotY: (-?[\d.]+), scale: (-?[\d.]+)(?:, sy: [\d.]+, sz: [\d.]+, y: [\d.-]+, wall: (\d+))? \}", text)]


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def colliders(walls, axis_length, radius):
    result = []
    for row in walls:
        length = axis_length * row['scale']
        ax, az = math.cos(row['rotY']), -math.sin(row['rotY'])
        for k in range(row['wall']):
            t = ((k + 0.5) / row['wall'] - 0.5) * length
            result.append((row['x'] + ax * t, row['z'] + az * t, radius))
    return result


def nearest(point_, circles):
    return min(dist(point_, (x, z)) - radius for x, z, radius in circles)


i = block(cfg, 'regionI')
h = block(cfg, 'regionH')
g = block(cfg, 'regionG')
center, seat, land_i, land_h = point(i, 'center'), point(i, 'spawn'), point(i, 'armory_deep'), point(i, 'fort_garrison')
center_h = point(h, 'center')
ri, rh = number(i, 'groundRadius'), number(h, 'groundRadius')
plane, hw = number(i, 'planeZ'), number(i, 'doorHalfWidth')
enemies, props = rows(i, 'enemies'), rows(i, 'props')
walls = [r for r in props if r['wall'] is not None]
dress = [r for r in props if r['wall'] is None]
# Region-manager's whWall shape: local-X length 1.899, collider radius from CONFIG.
wall_cfg = block(cfg, 'boundaryWall')
collider_radius = number(wall_cfg.split('collider:', 1)[1], 'r')
circles = colliders(walls, 1.899, collider_radius)

ok('I spawn and land same seat', seat == land_i, str((seat, land_i)))
for label, p in [('spawn', seat), ('landI', land_i)]:
    maximum('I %s rho within r-1.5' % label, dist(p, center), ri - 1.5)
ok('two ghouls', len(enemies) == 2 and all(t == 'ghoul' for t, _, _ in enemies), str(enemies))
for n, (_, x, z) in enumerate(enemies):
    minimum('ghoul%d from seat' % n, dist((x, z), seat), 8.0)
    minimum('ghoul%d ring walk-clear (r-rho)' % n, ri - dist((x, z), center), 4.45)
    minimum('ghoul%d ring collider edge (extra)' % n, nearest((x, z), circles), 4.45)
minimum('ghoul mutual', dist(enemies[0][1:], enemies[1][1:]), 12.5)
ok('ring: ten rows, eighty colliders', len(walls) == 10 and len(circles) == 80, str((len(walls), len(circles))))
ok('ring scale and wall count', all(w['scale'] == 5.8581 and w['wall'] == 8 for w in walls))
lane = [(x / 4, plane) for x in range(int(-hw * 4), int(hw * 4) + 1)]
lane_min = min(nearest(p, circles) for p in lane)
minimum('door lane nearest collider edge', lane_min, 1.0)
window = [(x, z) for x, z, r in circles if abs(x) <= hw + r and abs(z - plane) <= 0.5 + r]
ok('zero colliders overlapping lane window +/-0.5', not window, 'count=%d' % len(window))
for n, row in enumerate(dress):
    p = row['x'], row['z']
    minimum('prop%02d %s ring raw' % (n, row['asset']), nearest(p, circles) + collider_radius, 4.0)
    minimum('prop%02d ring walk-clear (r-rho)' % n, ri - dist(p, center), 4.0)
    minimum('prop%02d ring collider edge (extra)' % n, nearest(p, circles), 4.0)
    minimum('prop%02d from seat' % n, dist(p, seat), 6.0)
ok('bier tableaux trio present', len([r for r in dress if r['asset'] in ('stoneSarcophagus', 'stoneSteps')]) == 3)

# H seats recomputed against LIVE H props/nodes and regionG pole flank rows.
hprops = rows(h, 'props')
hdress = [r for r in hprops if r['wall'] is None]
hnodes = [(t, float(x), float(z)) for t, x, z in re.findall(r"\{ type: '(\w+)', x: (-?[\d.]+),\s*z: (-?[\d.]+) \}", h.split('nodes: [', 1)[1])]
dais = [r for r in hdress if r['asset'] == 'stoneSteps' and r['x'] == 0 and r['z'] == -1097]
torches = [r for r in hdress if r['asset'] == 'torch' and r['z'] == -1093]
interaction = point(i, 'interact') if re.search(r'interact: \{ x:', i) else (-7.5, -1088.5)
# Parse the multi-line interact object directly, not the literal commentary.
im = re.search(r"interact:\s*\{\s*from: '([^']+)',[^\n]*\n\s*x: (-?[\d.]+), z: (-?[\d.]+), radius: (-?[\d.]+)", i)
assert im, 'missing live interact row'
interaction = float(im.group(2)), float(im.group(3))
ok('interact from H and radius', im.group(1) == 'fort_garrison' and float(im.group(4)) == 3.5)
maximum('landH rho within r-1.5', dist(land_h, center_h), rh - 1.5)
ok('landH north/home of I plane', land_h[1] > plane)
ok('dais and torch rows present', len(dais) == 1 and len(torches) == 2)
minimum('landH dais raw minus 2m', dist(land_h, (dais[0]['x'], dais[0]['z'])) - 2, 11.0)
for n, t in enumerate(torches):
    minimum('landH torch%d raw minus 1m' % n, dist(land_h, (t['x'], t['z'])) - 1, 8.85)
minimum('interact torchL raw', min(dist(interaction, (t['x'], t['z'])) for t in torches), 5.7)
minimum('interact dais raw minus 2m', dist(interaction, (dais[0]['x'], dais[0]['z'])) - 2, 9.3)
maximum('interact rho within H r-1.5', dist(interaction, center_h), rh - 1.5)
minimum('landH dressing clearance excluding dais/torch (raw)',
        min(dist(land_h, (r['x'], r['z'])) for r in hdress if r not in dais + torches), 4.0)
minimum('landH nodes clearance (raw)', min(dist(land_h, (x, z)) for _, x, z in hnodes), 4.0)
gprops = rows(g, 'props')
poles = [r for r in gprops if r['asset'] == 'bannerPole' and r['z'] < -900]
if poles:
    minimum('landH G pole flank nearest raw', min(dist(land_h, (p['x'], p['z'])) for p in poles), 14.7)
else:
    print('DISCLOSURE: G bannerPole flank rows absent from landed regionG props')

cm = re.search(r'var ID = CFG\.regionI\.door;\s*connections\.push\(\{(.*?)\}\);', rdefs, re.S)
assert cm, 'missing conn7 block'
c7 = cm.group(1)
for label, expr in [('from H', 'from: CFG.regionH.id'), ('to I', 'to: CFG.regionI.id'),
                    ('axis z', "axis: 'z'"), ('plane from ID', 'planeCoord: ID.planeZ'),
                    ('walkFrom I', 'walkFrom: CFG.regionI.id'), ('H interact', 'from: CFG.regionH.id, x: ID.interact.x'),
                    ('land both', 'land: ID.land'), ('text and fades', 'text: ID.text')]:
    ok('conn7 ' + label, expr in c7)
ok('conn7 plane value', plane == -1136)
for key, side in [('regionH', -1), ('regionI', 1)]:
    m = re.search(r'connections\[7\]\.sides\[CFG\.%s\.id\] = ([+-]?\d);' % key, rdefs)
    ok('conn7 %s side table' % key, m is not None and int(m.group(1)) == side)
ok('I sideOfPlane(center) == sideIn(I)', center[1] > plane)
ok('I sideOfPlane(land) == sideIn(I)', land_i[1] > plane)
ok('H underground plane inactive', 'walkFrom: CFG.regionI.id' in c7 and land_h[1] > plane)
ok('H underground exception: side table -1 vs geometric +1', land_h[1] > plane and re.search(r'connections\[7\]\.sides\[CFG\.regionH\.id\] = -1;', rdefs) is not None)
print('E precedent conn[2]: ' + ' / '.join(re.findall(r'connections\[2\]\.sides\[CFG\.region[CD]\.id\] = [+-]?\d;', rdefs)))
print('E precedent conn[3]: ' + ' / '.join(re.findall(r'connections\[3\]\.sides\[CFG\.region[CE]\.id\] = [+-]?\d;', rdefs)))
print('---')
print('checks: %d' % checks)
if fails:
    print('ALL CONSTRAINTS: FAIL (%d checks, %d failed)' % (checks, len(fails)))
    for label in fails:
        print('  FAIL: ' + label)
    sys.exit(1)
print('ALL CONSTRAINTS: PASS (%d checks)' % checks)
