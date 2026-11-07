#!/usr/bin/env python3
"""CC-H2 dressing manifest scan (IO pre-spec probe, scratch/cc-h2/). Verifies
the FULL prop list proposed for regionHfort_garrison against the site-scan's
frozen ring rows + G's post-erasure ring, BEFORE the spec freezes. Every
number prints FROZEN; the spec quotes this manifest verbatim.

Laws (doc 66 sec 6 + H1 precedent):
  - every prop >= 4.0 m raw from BOTH rings (G post-erasure + H2 full)
  - every prop >= 6.0 m from spawn (0,-955) and both land rows
  - every prop >= 4.0 m mutual
  - every prop >= 5.0 m from BOTH bandit sentries
  - every prop rho <= 78.5 (playRadius = 80 - 1.5) from center (0,-1024)
  - the 2 warm sockets (brazier + gate lanternPost) = ONE amber family;
    zero other light-carrying rows
Run: python3 scratch/cc-h2/props_scan.py   (from the worktree root)
"""
import math, re, sys

ROOT = '/tmp/wh-worldfeat'
cfg = open(ROOT + '/prototype/js/CONFIG.js').read()

def block(src, key):
    me = re.search(r'\n  %s: \{' % re.escape(key), src)
    blob = src[me.start():]
    nxt = re.search(r'\n  [a-zA-Z_]+: \{', blob[10:])
    return blob[:10 + nxt.start()] if nxt else blob

gblock = block(cfg, 'regionG')
GC = (0.0, -822.0)
AW = 1.899
WR = 0.45

# G ring rebuild (all 89 rows), then erase the pole pair
G_WALLS = []
in_props = False
for ln in gblock.splitlines():
    if re.match(r'\s*props: \[', ln):
        in_props = True
        continue
    if in_props and re.match(r'\s*\]', ln):
        break
    if not in_props:
        continue
    wm = re.search(r"\{ asset: '(whWall[AB])', x: (-?[\d.]+), z: (-?[\d.]+), rotY: (-?[\d.]+), "
                   r"scale: (-?[\d.]+), sy: (-?[\d.]+), sz: (-?[\d.]+), y: (-?[\d.]+), wall: (\d+) \}", ln)
    if wm:
        G_WALLS.append(dict(asset=wm.group(1), x=float(wm.group(2)), z=float(wm.group(3)),
                            rotY=float(wm.group(4)), scale=float(wm.group(5)), n=int(wm.group(9))))
def colliders(walls):
    out = []
    for wr in walls:
        L = AW * wr['scale']
        ax, az = math.cos(wr['rotY']), -math.sin(wr['rotY'])
        for k in range(wr['n']):
            t = ((k + 0.5) / wr['n'] - 0.5) * L
            out.append((wr['x'] + ax * t, wr['z'] + az * t))
    return out
G_ERASE = {(4.4, -947.92), (-4.4, -947.92)}
G_WALLS_POST = [w for w in G_WALLS if (w['x'], w['z']) not in G_ERASE]
GC_W_POST = colliders(G_WALLS_POST)

# H2 frozen ring rows from the seat scan output
frz = open(ROOT + '/scratch/cc-h2/seat_scan_output.txt').read()
frz = frz[frz.index('RING ROWS'):]
H2_WALLS = []
for ln in frz.splitlines():
    wm = re.search(r"\{ asset: '(whWall[AB])', x: (-?[\d.]+), z: (-?[\d.]+), rotY: (-?[\d.]+), "
                   r"scale: (-?[\d.]+), sy: (-?[\d.]+), sz: (-?[\d.]+), y: (-?[\d.]+), wall: (\d+) \}", ln)
    if wm:
        H2_WALLS.append(dict(asset=wm.group(1), x=float(wm.group(2)), z=float(wm.group(3)),
                             rotY=float(wm.group(4)), scale=float(wm.group(5)), n=int(wm.group(9))))
H2_W = colliders(H2_WALLS)
print('inputs: G ring post-erase colliders %d | H2 ring colliders %d' % (len(GC_W_POST), len(H2_W)))

C2 = (0.0, -1024.0)
SPAWN = (0.0, -955.0)
LAND_H2 = (0.0, -955.0)
LAND_G = (0.0, -941.0)
EN = [(-10.0, -975.0), (11.0, -976.0)]

# THE MANIFEST (14 rows) - the spec quotes this block verbatim
MANIFEST = [
    # armory corner (east)
    ("whTent",          44.0, -1058.0, 5.75, 1.0),
    ("whCampkit",       38.0, -1052.0, 0.5,  1.0),
    ("whCampkit",       41.0, -1064.0, 1.2,  1.0),
    ("okRuinColumn",    52.0, -1050.0, 5.9,  1.4),
    # dungeon mouth corner (west)
    ("stoneSteps",     -46.0, -1064.0, 1.57, 1.3),
    ("skullPile",      -50.0, -1050.0, 4.4,  1.0),
    ("b6Bones",        -42.0, -1076.0, 2.4,  1.0),
    ("rubblePile",     -34.0, -1072.0, 5.8,  1.1),
    # war-table hub (the H1 dais trick)
    ("stoneSteps",       0.0, -1097.0, 0.0,  1.4),
    ("torch",            4.0, -1093.0, 0.0,  1.0),
    ("torch",           -4.0, -1093.0, 0.0,  1.0),
    # mid-yard sentry brazier + gate lantern (the TWO warm sockets)
    ("banditCampfire",   0.0,  -990.0, 0.0,  1.8),
    ("lanternPost",      6.5,  -954.0, 4.72, 2.535),
    # yard scatter
    ("mossBoulder",     26.0, -1000.0, 2.0,  2.0),
    ("mossBoulder",    -24.0, -1030.0, 4.9,  2.2),
    ("rubblePile",      58.0,  -992.0, 3.62, 1.1),
]

fails = []
def check(label, val, req, le=False, kind='num'):
    if kind == 'num':
        good = (val <= req) if le else (val >= req)
    else:
        good = val == req
    if not good:
        fails.append(label)
    print('%-58s %8.2f %s %5.1f  %s' % (label, val, '<=' if le else '>=', req,
          'ok' if good else 'FAIL'))

pts = [(a, x, z) for (a, x, z, r, s) in MANIFEST]
# mutual >= 4.0
for i in range(len(pts)):
    for j in range(i + 1, len(pts)):
        d = math.hypot(pts[i][1] - pts[j][1], pts[i][2] - pts[j][2])
        if d < 4.0:
            check('mutual %s(%d)-%s(%d) >= 4.0' % (pts[i][0], i, pts[j][0], j), d, 4.0)
for i, (a, x, z, r, s) in enumerate(MANIFEST):
    rho = math.hypot(x - C2[0], z - C2[1])
    check('%d %s (%.0f,%.0f) rho <= 78.5' % (i, a, x, z), rho, 78.5, le=True)
    dg = min(math.hypot(x - gx, z - gz) for (gx, gz) in GC_W_POST)
    check('%d %s raw >= 4.0 from G ring post-erase' % (i, a), dg, 4.0)
    dh = min(math.hypot(x - hx, z - hz) for (hx, hz) in H2_W)
    check('%d %s raw >= 4.0 from H2 ring' % (i, a), dh, 4.0)
    ds = min(math.hypot(x - sx, z - sz) for (sx, sz) in (SPAWN, LAND_H2, LAND_G))
    check('%d %s >= 6.0 from spawn/lands' % (i, a), ds, 6.0)
    de = min(math.hypot(x - ex, z - ez) for (ex, ez) in EN)
    check('%d %s >= 5.0 from both sentries' % (i, a), de, 5.0)

# flankers (the okFenceStonewall pair printed by seat_scan at (±10,-968)) —
# they are G-side aperture dressing, asserted here against H2's ring only
for (fx, fz) in ((10.0, -968.0), (-10.0, -968.0)):
    dh = min(math.hypot(fx - hx, fz - hz) for (hx, hz) in H2_W)
    check('flanker (%.0f,%.0f) raw >= 16.0 from H2 ring (margin law)' % (fx, fz), dh, 16.0)
    dg = min(math.hypot(fx - gx, fz - gz) for (gx, gz) in GC_W_POST)
    check('flanker (%.0f,%.0f) raw >= 4.0 from G ring post-erase' % (fx, fz), dg, 4.0)
    dfl = min(math.hypot(fx - mx, fz - mz) for (a, mx, mz, r, s) in MANIFEST)
    check('flanker (%.0f,%.0f) >= 4.0 mutual from manifest' % (fx, fz), dfl, 4.0)

print('---')
print('MANIFEST: %d rows' % len(MANIFEST))
for (a, x, z, r, s) in MANIFEST:
    print("  { asset: '%s', x: %s, z: %s, rotY: %s, scale: %s }," % (a, x, z, r, s))
if fails:
    print('MANIFEST CHECKS: FAIL (%s)' % '; '.join(fails))
    sys.exit(1)
print('MANIFEST CHECKS: PASS')
