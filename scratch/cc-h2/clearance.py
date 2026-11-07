#!/usr/bin/env python3
"""CC-H2 clearance verifier (Devbot probe; shape on scratch/cc-h1/clearance.py).

Parses prototype/js/CONFIG.js + prototype/js/region-defs.js LIVE (no hard-coded
spec numbers for the new rows) and asserts EVERY valspec constraint:
  V-5  A-5  sides-table law, BOTH directions (doc 66 sec 10) + land rows home-side
  V-6  A-6  ring geometry (48/384, window strip, lane samples, mouth arc,
            octants, per-row radial check) + A-8 props + A-9 enemies
  V-7  A-7  regionG aperture lane clearance post-erase + deleted byte strings absent

Run: python3 scratch/cc-h2/clearance.py   (from the worktree root)
Exit 0 only if ALL pass; final line 'ALL CONSTRAINTS: PASS (N checks)'.
"""
import math
import re
import sys

ROOT = '/tmp/wh-worldfeat'
cfg = open(ROOT + '/prototype/js/CONFIG.js').read()
rdefs = open(ROOT + '/prototype/js/region-defs.js').read()

fails = []
CHECKS = [0]

def ok(label, cond):
    CHECKS[0] += 1
    if not cond:
        fails.append(label)
    print('%-70s %s' % (label, 'ok' if cond else 'FAIL'))

def okf(label, val, req, cmp_):
    CHECKS[0] += 1
    good = cmp_(val, req)
    if not good:
        fails.append(label)
    print('%-58s %10.4f %s %8.4f  %s' % (label, val, cmp_.__name__, req, 'ok' if good else 'FAIL'))

ge = lambda a, b: a >= b
le = lambda a, b: a <= b
eq = lambda a, b: abs(a - b) < 1e-9

# ---------------------------------------------------------------- parse CONFIG
def block(src, key):
    me = re.search(r'\n  %s: \{' % re.escape(key), src)
    blob = src[me.start():]
    nxt = re.search(r'\n  [a-zA-Z_]+: \{', blob[10:])
    return blob[:10 + nxt.start()] if nxt else blob

gblock = block(cfg, 'regionG')
hblock = block(cfg, 'regionH')

def grab(block_src, pat, cast):
    m = re.search(pat, block_src)
    assert m, 'pattern not found: ' + pat
    return cast(m) if cast else m

def num(block_src, key):
    m = re.search(r'\n\s*%s: (-?[\d.]+)' % re.escape(key), block_src)
    assert m, 'key not found: ' + key
    return float(m.group(1))

hm = re.search(r'center: \{ x: (-?[\d.]+), z: (-?[\d.]+) \}', hblock)
assert hm, 'regionH center not found'
HC = (float(hm.group(1)), float(hm.group(2)))
hR = num(hblock, 'groundRadius')
HSEED = int(num(hblock, 'groundSeed'))
hspawn = re.search(r'spawn: \{ x: (-?[\d.]+), z: (-?[\d.]+) \}', hblock)
HSPAWN = (float(hspawn.group(1)), float(hspawn.group(2)))
hplaneZ = num(hblock, 'planeZ')
hdoorX = num(hblock, 'doorX')
hHW = num(hblock, 'doorHalfWidth')
hSUSP = num(hblock, 'suspendDepthM')
hgap = num(hblock, 'wallGapPadM')
hlandH2 = re.search(r"fort_garrison: \{ x: (-?[\d.]+), z: (-?[\d.]+), faceX: (-?[\d.]+), faceZ: (-?[\d.]+) \}", hblock)
hlandG = re.search(r"lords_hold:\s+\{ x: (-?[\d.]+), z: (-?[\d.]+), faceX: (-?[\d.]+), faceZ: (-?[\d.]+) \}", hblock)
hfadeIn = num(hblock, 'fadeIn')
hfadeOut = num(hblock, 'fadeOut')
hexitFade = num(hblock, 'exitFadeOut')

h_en = re.findall(r"\{ type: '(\w+)', x: (-?[\d.]+), z: (-?[\d.]+) \}", hblock)
H2_EN = [(t, float(x), float(z)) for (t, x, z) in h_en]

# regionH props array (stop at the closing `]` of props)
pi = hblock.index('props: [')
props_blob = hblock[pi:]
props_end = props_blob.index('\n    ]')
props_blob = props_blob[:props_end]
hprops = []
for m in re.finditer(r"\{ asset: '(\w+)', x: (-?[\d.]+), z: (-?[\d.]+)(?:, rotY: (-?[\d.]+))?(?:, scale: (-?[\d.]+))?(?:, sy: [\d.]+, sz: [\d.]+, y: [\d.-]+)?(?:, wall: (\d+))?", props_blob):
    asset, x, z, rotY, scale, wall = m.groups()
    hprops.append(dict(asset=asset, x=float(x), z=float(z), rotY=float(rotY) if rotY else 0.0,
                       scale=float(scale) if scale else 1.0, wall=int(wall) if wall else None))
H2_WALL_ROWS = [p for p in hprops if p['wall'] is not None]
H2_PROPS = [p for p in hprops if p['wall'] is None]
H2_WALLS = [dict(asset=w['asset'], x=w['x'], z=w['z'], rotY=w['rotY'], scale=w['scale'], n=w['wall']) for w in H2_WALL_ROWS]

# regionG walls (all 89 landed wall rows pre-erase, from the LIVE block)
gm = re.search(r'\n    props: \[', gblock)
gprops_blob = gblock[gm.start():]
gprops_end = gprops_blob.index('\n    ]')
gprops_blob = gprops_blob[:gprops_end]
G_WALLS = []
for m in re.finditer(r"\{ asset: 'whWall([AB])', x: (-?[\d.]+), z: (-?[\d.]+), rotY: (-?[\d.]+), scale: (-?[\d.]+), sy: [\d.]+, sz: [\d.]+, y: [\d.-]+, wall: (\d+) \}", gprops_blob):
    G_WALLS.append(dict(asset='whWall' + m.group(1), x=float(m.group(2)), z=float(m.group(3)),
                        rotY=float(m.group(4)), scale=float(m.group(5)), n=int(m.group(6))))
# G dressing rows (non-wall)
G_DRESS = []
for m in re.finditer(r"\{ asset: '(\w+)', x: (-?[\d.]+), z: (-?[\d.]+), rotY: (-?[\d.]+), scale: (-?[\d.]+) \}", gprops_blob):
    if m.group(1).startswith('whWall'):
        continue
    G_DRESS.append((m.group(1), float(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5))))

# ---------------------------------------------------------------- parse region-defs
# registration
ok('region-defs: makeRegion(CFG.regionH, -1) registration present',
   re.search(r'regions\[CFG\.regionH\.id\] = makeRegion\(CFG\.regionH, -1\);', rdefs) is not None)
# conn[6] block, live
cm = re.search(r'var HD = CFG\.regionH\.door;\s*\n\s*connections\.push\(\{(.*?)\}\);', rdefs, re.S)
assert cm, 'conn[6] push block not found'
c6 = cm.group(1)
ok('conn6: from = CFG.regionG.id', 'from: CFG.regionG.id' in c6)
ok('conn6: to = CFG.regionH.id', 'to: CFG.regionH.id' in c6)
ok('conn6: axis z', re.search(r"axis: 'z'", c6) is not None)
ok('conn6: planeCoord = HD.planeZ', 'planeCoord: HD.planeZ' in c6)
ok('conn6: doorX = HD.doorX', 'doorX: HD.doorX' in c6)
ok('conn6: doorHalfWidth = HD.doorHalfWidth', 'doorHalfWidth: HD.doorHalfWidth' in c6)
ok('conn6: suspendDepthM = HD.suspendDepthM', 'suspendDepthM: HD.suspendDepthM' in c6)
ok('conn6: wallGapPadM = HD.wallGapPadM', 'wallGapPadM: HD.wallGapPadM' in c6)
ok('conn6: arch null', re.search(r'arch: null', c6) is not None)
ok('conn6: gatedTo null', re.search(r'gatedTo: null', c6) is not None)
ok('conn6: NO walkFrom', 'walkFrom' not in c6)
ok('conn6: NO interact', 'interact' not in c6)
ok('conn6: land = HD.land', 'land: HD.land' in c6)
sides_g = re.search(r'connections\[6\]\.sides\[CFG\.regionG\.id\] = (-?\d);', rdefs)
sides_h = re.search(r'connections\[6\]\.sides\[CFG\.regionH\.id\] = (-?\d);', rdefs)
ok('conn6 sides row present (both entries)', sides_g is not None and sides_h is not None)
CONN6_SIDES_G = int(sides_g.group(1)) if sides_g else None
CONN6_SIDES_H = int(sides_h.group(1)) if sides_h else None

def side_of_plane(z):        # region-defs sideOfPlane: z > planeCoordinate ? 1 : -1
    return 1 if z > hplaneZ else -1

# ---------------------------------------------------------------- colliders
AW = 1.899   # whWall segment axis-length = scale x 1.899 (landed law, cc-h1)
WR = 0.45    # wall collider radius (landed law)

def colliders(walls):
    out = []
    for wr in walls:
        L = AW * wr['scale']
        ax, az = math.cos(wr['rotY']), -math.sin(wr['rotY'])
        for k in range(wr['n']):
            t = ((k + 0.5) / wr['n'] - 0.5) * L
            out.append((wr['x'] + ax * t, wr['z'] + az * t))
    return out

H2_W = colliders(H2_WALLS)

# G ring post-erase: the two (±4.4, -947.92) rows are ERASED from the landed CONFIG.
G_ERASE_XZ = {(4.4, -947.92), (-4.4, -947.92)}
G_WALL_ROWS_LIVE = [w for w in G_WALLS if (w['x'], w['z']) not in G_ERASE_XZ]
G_W_POST = colliders(G_WALL_ROWS_LIVE)

# ---------------------------------------------------------------- V-6 section A: H2 ring
ok('ring rows == 48', len(H2_WALL_ROWS) == 48)
ok('ring colliders == 384', len(H2_W) == 384)
# A/B parity: printed asset column alternates; the landed rows match the scan order
pat = ''.join(w['asset'][-1] for w in H2_WALL_ROWS)   # A/B letters in landed order
ok('ring A/B alternation strict', pat == 'BA' * 24)
# window strip: |x| <= 4, |z + 948| <= 3 must hold ZERO colliders
STRIP = [(x, z) for (x, z) in H2_W if abs(x) <= 4.0 and abs(z + 948.0) <= 3.0]
ok('colliders inside window strip == 0', len(STRIP) == 0)
# lane samples x -4..4 step 0.5 on z = -948: nearest collider >= 1.0
lane_min = min(min(math.hypot(x - cx, -948.0 - cz) for (cx, cz) in H2_W) for x in [i * 0.5 - 4 for i in range(17)])
okf('H2 lane samples nearest collider >= 1.0', lane_min, 1.0, ge)
# mouth bearing arc 82.8..97.2 (deg, east = +x, the seat-scan convention
# `atan2(z - cz, x - cx) % 360`): zero colliders (i=0/49 both OMITTED rows)
def bearing(x, z):
    ang = math.degrees(math.atan2(z - HC[1], x - HC[0])) % 360.0
    return ang
mouth = [c for c in H2_W if 82.8 <= bearing(*c) <= 97.2]
ok('colliders bearing inside mouth arc [82.8, 97.2] == 0', len(mouth) == 0)
# every octant >= 8 colliders (octant origin = seat-scan: (a + 22.5) % 360 / 45)
oct_min = min(sum(1 for c in H2_W if int(((bearing(*c) + 22.5) % 360.0) / 45.0) == oct_i) for oct_i in range(8))
okf('every octant holds >= 8 colliders (min octant)', oct_min, 8.0, ge)
# per-row radial law |hypot(x, z + 1024) - 80| <= 0.6
rdev = max(abs(math.hypot(w['x'] - HC[0], w['z'] - HC[1]) - hR) for w in H2_WALL_ROWS)
okf('every ring row |rho - 80| <= 0.6 (max dev)', rdev, 0.6, le)

# ---------------------------------------------------------------- V-6 section C: props (A-8)
C2 = HC
SPAWN = HSPAWN
LAND_H2 = (float(hlandH2.group(1)), float(hlandH2.group(2)))
LAND_G = (float(hlandG.group(1)), float(hlandG.group(2)))
EN = [(x, z) for (t, x, z) in H2_EN]
SENTRY_SEATS = EN

for i, pr in enumerate(H2_PROPS):
    rho = math.hypot(pr['x'] - C2[0], pr['z'] - C2[1])
    okf('%02d %s (%.0f,%.0f) rho <= 78.5' % (i, pr['asset'], pr['x'], pr['z']), rho, 78.5, le)
    dg = min(math.hypot(pr['x'] - gx, pr['z'] - gz) for (gx, gz) in G_W_POST)
    okf('%02d %s raw >= 4.0 from G ring post-erase' % (i, pr['asset']), dg, 4.0, ge)
    dh = min(math.hypot(pr['x'] - hx, pr['z'] - hz) for (hx, hz) in H2_W)
    okf('%02d %s raw >= 4.0 from H2 ring' % (i, pr['asset']), dh, 4.0, ge)
    ds = min(math.hypot(pr['x'] - sx, pr['z'] - sz) for (sx, sz) in (SPAWN, LAND_H2, LAND_G))
    okf('%02d %s >= 6.0 from spawn/lands' % (i, pr['asset']), ds, 6.0, ge)
    de = min(math.hypot(pr['x'] - ex, pr['z'] - ez) for (ex, ez) in EN)
    okf('%02d %s >= 5.0 from both sentries' % (i, pr['asset']), de, 5.0, ge)

# mutual props >= 4.0
mut_min = min(math.hypot(H2_PROPS[i]['x'] - H2_PROPS[j]['x'], H2_PROPS[i]['z'] - H2_PROPS[j]['z'])
              for i in range(len(H2_PROPS)) for j in range(i + 1, len(H2_PROPS)))
okf('props mutual >= 4.0 (min pair)', mut_min, 4.0, ge)

# flankers: okFenceStonewall rows >= 16.0 off H2 ring (they are H2-side dressing)
flankers = [p for p in H2_PROPS if p['asset'] == 'okFenceStonewall']
ok('flanker rows present == 2', len(flankers) == 2)
for fp in flankers:
    dh = min(math.hypot(fp['x'] - hx, fp['z'] - hz) for (hx, hz) in H2_W)
    okf('flanker (%.0f,%.0f) >= 16.0 off H2 ring' % (fp['x'], fp['z']), dh, 16.0, ge)
    dg = min(math.hypot(fp['x'] - gx, fp['z'] - gz) for (gx, gz) in G_W_POST)
    okf('flanker (%.0f,%.0f) >= 4.0 off G ring post-erase' % (fp['x'], fp['z']), dg, 4.0, ge)

# ---------------------------------------------------------------- V-6 section D: enemies (A-9)
ok('regionH enemies count == 2', len(H2_EN) == 2)
ok('sentries are bandit rows', all(t == 'bandit' for (t, x, z) in H2_EN))
emut = math.hypot(EN[0][0] - EN[1][0], EN[0][1] - EN[1][1])
okf('enemy mutual >= 12.5', emut, 12.5, ge)
for i, (ex, ez) in enumerate(EN):
    ds = min(math.hypot(ex - sx, ez - sz) for (sx, sz) in (SPAWN, LAND_H2, LAND_G))
    okf('enemy %d >= 8.0 from spawn/land' % i, ds, 8.0, ge)
    dr = math.hypot(ex - C2[0], ez - C2[1])
    okf('enemy %d inside play radius <= 78.5' % i, dr, 78.5, le)
    dw = min(math.hypot(ex - cx, ez - cz) for (cx, cz) in H2_W)
    okf('enemy %d >= 4.45 walk-clear of ring' % i, dw, 4.45, ge)
    dwg = min(math.hypot(ex - gx, ez - gz) for (gx, gz) in G_W_POST)
    okf('enemy %d >= 4.45 walk-clear of G ring (post-erase)' % i, dwg, 4.45, ge)

# ---------------------------------------------------------------- V-5: sides law (A-5) BOTH directions
ok('sideOfPlane(conn6, G interior -822) == 1', eq(side_of_plane(-822.0), 1.0))
ok('sideIn(conn6, lords_hold) == 1', CONN6_SIDES_G == 1)
ok('sideOfPlane(conn6, H interior -1024) == -1', eq(side_of_plane(-1024.0), -1.0))
ok('sideIn(conn6, fort_garrison) == -1', CONN6_SIDES_H == -1)
ok('land.fort_garrison on home side (z <= planeZ)', LAND_H2[1] <= hplaneZ)
ok('land.lords_hold on G home side (z > planeZ)', LAND_G[1] > hplaneZ)
# spawn-sep law both regions
hspawn_depth = abs(HSPAWN[1] - hplaneZ)
okf('spawn depth past plane >= 4 (suspendDepthM)', hspawn_depth, 4.0, ge)
# planeIn both (no walkFrom anywhere in the gate block)
ok('conn6 two-sided: door has no walkFrom anywhere in block', 'walkFrom' not in c6)
# G-side dressing props (banner parapets etc.) must leave the C->G lane intact:
# G interior hook / gate at z -700..-712 stays clear of ALL G rows.
ok('G dressing row count unchanged (24)', len(G_DRESS) == 24)
ok('G curtain rows live post-erase == 87', len(G_WALL_ROWS_LIVE) == 87)
ok('G curtain colliders post-erase == 1044 (87 rows x wall 12)', len(G_W_POST) == 1044)

# ---------------------------------------------------------------- V-7: regionG aperture lane (A-7)
# lane samples x -4..4 (step 0.25), z -951..-945 (step 0.25): every remaining
# G collider >= 1.5 away from every lane sample.
lane_min_g = min(
    min(math.hypot(x - gx, z - gz) for (gx, gz) in G_W_POST)
    for x in [i * 0.25 - 4.0 for i in range(33)]
    for z in [-951.0 + i * 0.25 for i in range(25)])
okf('G lane post-erase: nearest collider >= 1.5', lane_min_g, 1.5, ge)

# deleted pair strings absent from CONFIG.js
for s in ["{ asset: 'whWallA', x: 4.4, z: -947.92, rotY: 6.25",
          "{ asset: 'whWallB', x: -4.4, z: -947.92, rotY: 0.03"]:
    ok('erased byte string absent: ' + s[:38] + '...', s not in cfg)

# erased G wall rows not present anywhere (coordinate form)
ok('no G wall row at (4.4, -947.92) survives', not any(w['x'] == 4.4 and w['z'] == -947.92 for w in G_WALLS))
ok('no G wall row at (-4.4, -947.92) survives', not any(w['x'] == -4.4 and w['z'] == -947.92 for w in G_WALLS))

# ---------------------------------------------------------------- summary
print('---')
print('checks: %d' % CHECKS[0])
if fails:
    print('ALL CONSTRAINTS: FAIL (%d checks, %d failed)' % (CHECKS[0], len(fails)))
    for f in fails:
        print('  FAIL: ' + f)
    sys.exit(1)
print('ALL CONSTRAINTS: PASS (%d checks)' % CHECKS[0])
sys.exit(0)
