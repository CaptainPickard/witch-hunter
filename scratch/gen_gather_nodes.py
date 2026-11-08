"""Stage 2 gather-node placement (deterministic, seed 20261005).

Reads regionA/regionB props + enemies + spawn straight out of CONFIG.js and
scatters node positions on open forest floor with clearances:
  - dirt path corridor (centerline x = amp*sin(2pi(z-zFrom)/period), z 32..86)
  - graveyard zone (A): ellipse around the cemetery + its tree ring
  - every prop (trees wider), enemy spawns, player spawn, gate corridor
  - min spacing between nodes
Prints CONFIG-ready nodes arrays + a placement table for the report.
"""
import math, random, re

SRC = open('/tmp/wh-worldfeat/prototype/js/CONFIG.js').read()

def block(name):
    i = SRC.index('  %s: {' % name)
    j = SRC.index('\n  },', i)
    return SRC[i:j]

def parse(name):
    b = block(name)
    props = []
    for m in re.finditer(r"\{ asset: '(\w+)',([^}]*)\}", b):
        kv = dict(re.findall(r"(\w+): (-?[\d.]+)", m.group(2)))
        props.append((m.group(1), float(kv['x']), float(kv['z'])))
    enemies = [(float(x), float(z)) for x, z in
               re.findall(r"type: '\w+', x: (-?[\d.]+), z: (-?[\d.]+)", b)]
    sx, sz = re.search(r"spawn: \{ x: (-?[\d.]+), z: (-?[\d.]+)", b).groups()
    return props, enemies, (float(sx), float(sz))

TREE = re.compile(r'tree|oak|ash|yew|witchwood', re.I)
PATH = dict(zFrom=86.0, zTo=32.0, half=2.7, amp=1.6, period=34.0)

def path_x(z):
    return PATH['amp'] * math.sin(2 * math.pi * (z - PATH['zFrom']) / PATH['period'])

def on_path(x, z, margin):
    if z < PATH['zTo'] - margin or z > PATH['zFrom'] + margin:
        return False
    return abs(x - path_x(z)) < PATH['half'] + margin

def in_graveyard(x, z):
    # cemetery props span x -21..21, z -15..32 with the tree ring outside
    # at ~29-33m; keep nodes outside an ellipse hugging that ring
    return ((x - 0) / 36.0) ** 2 + ((z - 10.0) / 33.0) ** 2 < 1.0

def place(rng, n, props, enemies, spawn, taken, ok_zone, spacing):
    out, tries = [], 0
    while len(out) < n and tries < 20000:
        tries += 1
        x = round(rng.uniform(-78, 78), 1)
        z = round(rng.uniform(-82, 82), 1)
        if math.hypot(x, z) > 78 or not ok_zone(x, z):
            continue
        if any(math.hypot(x - px, z - pz) < (4.0 if TREE.search(a) else 3.0)
               for a, px, pz in props):
            continue
        if any(math.hypot(x - ex, z - ez) < 5.0 for ex, ez in enemies):
            continue
        if math.hypot(x - spawn[0], z - spawn[1]) < 6.0:
            continue
        if any(math.hypot(x - tx, z - tz) < spacing for tx, tz in taken):
            continue
        out.append((x, z))
        taken.append((x, z))
    assert len(out) == n, 'placement starved'
    return out

def zone_a(x, z):
    # region A = z > boundary(-25); stay clear of the gate corridor too
    return (z > -17 and not in_graveyard(x, z) and not on_path(x, z, 2.5))

def zone_b(x, z):
    # region B darkwood: z < -25, inside the dressed forest band
    return -82 < z < -31 and abs(x) < 42

rng = random.Random(20261005)
for region, plan, zone, spacing in (
        ('regionA', [('herbBundle', 6), ('deadwoodPile', 4), ('mushroomCluster', 4)], zone_a, 9.0),
        ('regionB', [('graveMoss', 5), ('bonePile', 4)], zone_b, 6.0)):
    props, enemies, spawn = parse(region)
    taken = []
    print('=== %s nodes (props %d, enemies %d, spawn %s) ===' % (region, len(props), len(enemies), spawn))
    for t, n in plan:
        for x, z in place(rng, n, props, enemies, spawn, taken, zone, spacing):
            near = min(math.hypot(x - px, z - pz) for _, px, pz in props)
            print("      { type: '%s', x: %.1f, z: %.1f },   // nearest prop %.1fm" % (t, x, z, near))
