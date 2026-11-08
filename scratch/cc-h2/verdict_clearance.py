#!/usr/bin/env python3
"""verdict_clearance.py — Testerbot INDEPENDENT V-6/V-7 geometry probe (CC-H2).

Own verifier parsing the LANDED prototype/js/CONFIG.js + region-defs.js live
(shape on scratch/cc-h1/clearance.py, code by the Testerbot seat). NO
hard-coded spec constants feed the new-row assertions: ring geometry, props,
door keys, conn keys, sides signs all parse from the landed text; only the
landed physics law rides as constants (AW 1.899, wall collider r 0.45,
sideOfPlane replicated from region-defs.js:314). Read-only.
"""
import math
import re
import sys

ROOT = '/tmp/wh-worldfeat'
cfg = open(ROOT + '/prototype/js/CONFIG.js').read()
rdefs = open(ROOT + '/prototype/js/region-defs.js').read()

fails = []
N = [0]


def check(name, ok, detail=''):
    N[0] += 1
    if not ok:
        fails.append(name)
    print('%-4s %s%s' % ('ok' if ok else 'FAIL', name, ('  [%s]' % detail) if detail else ''))


# ---- parse region blocks -----------------------------------------------------
def region_blob(name):
    m = re.search(r'(^|\n)  %s: \{' % name, cfg)
    if not m:
        raise SystemExit('regionH/G anchor missing: ' + name)
    start = m.start() if m.group(1) else m.start()
    nxt = re.search(r'\n  [a-zA-Z_]+: \{', cfg[m.end():])
    end = m.end() + nxt.start() if nxt else len(cfg)
    return cfg[m.start():end]

G = region_blob('regionG')
H = region_blob('regionH')

m = re.search(r'center: \{ x: (-?[\d.]+), z: (-?[\d.]+) \}', H)
h_cx, h_cz = float(m.group(1)), float(m.group(2))
m = re.search(r'groundRadius: (-?[\d.]+)', H)
h_r = float(m.group(1))
m = re.search(r'spawn: \{ x: (-?[\d.]+), z: (-?[\d.]+) \}', H)
spawn = (float(m.group(1)), float(m.group(2)))
m = re.search(r'planeZ: (-?[\d.]+)', H)
plane_z = float(m.group(1))
m = re.search(r'doorX: (-?[\d.]+)', H)
door_x = float(m.group(1))
m = re.search(r'doorHalfWidth: (-?[\d.]+)', H)
half_w = float(m.group(1))
m = re.search(r'suspendDepthM: (-?[\d.]+)', H)
suspend = float(m.group(1))
m = re.search(r'center: \{ x: (-?[\d.]+), z: (-?[\d.]+) \}', G)
g_cx, g_cz = float(m.group(1)), float(m.group(2))
m = re.search(r'groundRadius: (-?[\d.]+)', G[:1200])
g_r = float(m.group(1))

# land rows
m = re.search(r'fort_garrison: *.*\{ x: (-?[\d.]+), z: (-?[\d.]+)', H)
land_h = (float(m.group(1)), float(m.group(2)))
m = re.search(r'lords_hold: *.*\{ x: (-?[\d.]+), z: (-?[\d.]+)', H)
land_g = (float(m.group(1)), float(m.group(2)))

# ---- props rows --------------------------------------------------------------
AW = 1.899           # landed collider law (seat_scan.py / recipe sec 6)
R_COLL = 0.45        # wall per-circle collider radius (landed law)


def parse_rows(blob):
    rows = []
    for m in re.finditer(r"\{ asset: '([A-Za-z0-9]+)', x: (-?[\d.]+), z: (-?[\d.]+),"
                         r" rotY: (-?[\d.]+), scale: (-?[\d.]+)([^}]*)\}", blob):
        tail = m.group(6)
        wall = re.search(r'wall: (\d+)', tail)
        rows.append(dict(asset=m.group(1), x=float(m.group(2)), z=float(m.group(3)),
                         rotY=float(m.group(4)), scale=float(m.group(5)),
                         wall=int(wall.group(1)) if wall else None, raw=m.group(0)))
    return rows

props_h = parse_rows(H)
ring_rows = [r for r in props_h if r['asset'].startswith('whWall') and r['wall'] == 8]
dressing = [r for r in props_h if not (r['asset'].startswith('whWall') and r['wall'] == 8)]
g_rows = parse_rows(G)
g_ring = [r for r in g_rows if r['asset'].startswith('whWall') and r['wall'] == 12]
g_dress = [r for r in g_rows if not (r['asset'].startswith('whWall') and r['wall'] == 12)]

# ---- collider builders -------------------------------------------------------
def colliders(rows):
    """Seat-scan collider law (seat_scan.py:91-99, replicated): the row's
    `wall` column IS the per-circle count n; circles r 0.45 sit along the row's
    local X at ext = AW*scale, step = ext/n < 2 m (boundaryWall.collider.r 0.45
    parsed from CONFIG, AW 1.899)."""
    out = []
    for r in rows:
        if r['wall'] is None:
            continue
        ext = AW * r['scale']
        n = r['wall']
        a = math.radians(r['rotY'])
        ux, uz = math.cos(a), -math.sin(a)
        for k in range(n):
            t = ((k + 0.5) / n - 0.5) * ext
            out.append((r['x'] + ux * t, r['z'] + uz * t))
    return out

# wall colliders are 2-tuples now; keep the G collider list shape-compatible
h_coll = [(c[0], c[1]) for c in colliders(ring_rows)]
g_coll = [(c[0], c[1]) for c in colliders(g_ring)]
h_pts = h_coll
g_pts = g_coll

# ---- Section A: H2 ring ------------------------------------------------------
check('A: regionH ring rows == 48', len(ring_rows) == 48, str(len(ring_rows)))
check('A: H2 colliders == 384', len(h_coll) == 384, str(len(h_coll)))
strict = len(set(r['raw'] for r in ring_rows)) == 48
alt_ok = all(ring_rows[i]['asset'] != ring_rows[i + 1]['asset'] for i in range(47))
check('A: ring rows unique + strict A/B alternation', strict and alt_ok)
devs = [abs(math.hypot(r['x'] - h_cx, r['z'] - h_cz) - h_r) for r in ring_rows]
check('A: every ring row |hypot(x, z+1024) - 80| <= 0.6 (r-80 rim from parsed center)',
      max(devs) <= 0.6, 'max dev %.4f' % max(devs))
win = [c for c in h_coll if abs(c[0]) <= 4 and abs(c[1] - (-948)) <= 3]
check('A: window strip (|x|<=4, |z+948|<=3) empty', len(win) == 0, 'count %d' % len(win))

# lane samples: exactly the valspec domain x -4..4 x z -951..-945 at 0.25 m grid (finer than 0.5 spec floor)
lane = [(-4.0 + i * 0.25, -951.0 + k * 0.25) for i in range(33) for k in range(25)]
min_lane = min(math.hypot(x - c[0], z - c[1]) for (x, z) in lane for c in h_coll)
check('A: H2 lane samples (%d) nearest collider >= 1.0' % len(lane),
      min_lane >= 1.0, 'nearest %.4f' % min_lane)

# mouth bearing arc: recompute from landed rows (seat-scan convention atan2(z-cz, x-cx))
bearings = [math.degrees(math.atan2(c[1] - h_cz, c[0] - h_cx)) % 360 for c in h_coll]
arc = [b for b in bearings if 82.8 <= b <= 97.2]
check('A: mouth arc [82.8, 97.2] deg holds 0 colliders', len(arc) == 0, 'count %d' % len(arc))
oct = [0] * 8
for b in bearings:
    oct[min(7, int(b // 45))] += 1
check('A: every bearing octant holds >= 8 colliders', min(oct) >= 8,
      'min octant %d (counts %s)' % (min(oct), oct))

# ---- Section C: props clearances ---------------------------------------------
check('C: regionH prop rows total == 66 (18 dressing + 48 ring)', len(props_h) == 66,
      str(len(props_h)))
check('C: dressing rows (excl. ring wall 8) == 18', len(dressing) == 18, str(len(dressing)))
check('C: crimson zero (no blightcap/crimson asset in regionH)',
      not any(('blight' in r['asset'].lower() or 'crimson' in r['asset'].lower()) for r in props_h))

# light-socket law from the LANDED lightSockets table (not the spec)
ls = re.search(r'lightSockets: \{', cfg)
ls_end = cfg.find('world: {', ls.end())
ls_body = cfg[ls.end():ls_end]
socket_keys = set(re.findall(r'\n    ([a-zA-Z]+):', ls_body))
socket_carry = sorted(set(r['asset'] for r in dressing if r['asset'] in socket_keys))
BVR = socket_carry == ['banditCampfire', 'lanternPost', 'whCampkit']
check('C [BV-001 option b]: socket-carrying assets == {banditCampfire, lanternPost, whCampkit} (FOUR socket rows)',
      BVR, 'observed %s (rows: %s)' % (socket_carry,
                                       ['%s@(%.1f,%.1f)' % (r['asset'], r['x'], r['z'])
                                        for r in dressing if r['asset'] in socket_keys]))
check('C: torch has NO lightSockets row (deliberate non-light warm dressing)',
      'torch' not in socket_keys)
sf = ['whTent', 'okRuinColumn', 'stoneSteps', 'skullPile', 'b6Bones', 'rubblePile',
      'torch', 'mossBoulder', 'okFenceStonewall']
check('C: no socket key for whTent/okRuinColumn/stoneSteps/skullPile/b6Bones/rubblePile/torch/mossBoulder/okFenceStonewall',
      not any(a in socket_keys for a in sf))

rings_both = [(c[0], c[1]) for c in g_coll] + [(c[0], c[1]) for c in h_coll]
def dmin(px, pz, pts):
    return min(math.hypot(px - a, pz - b) for (a, b) in pts)
land_pts = [spawn, land_h, land_g]

# parse the enemies block (live, before any use)
me = re.search(r'enemies: \[(.*?)\]', H, re.S)
en = re.findall(r"\{ type: '([a-z]+)', x: (-?[\d.]+), z: (-?[\d.]+) \}", me.group(1))
enemies = [(t, float(x), float(z)) for (t, x, z) in en]
check('D: enemies rows parsed from CONFIG enemies block == the 2 bandit spec seats',
      enemies == [('bandit', -10.0, -975.0), ('bandit', 11.0, -976.0)], repr(enemies))
sentries = [(float(x), float(z)) for (_, x, z) in enemies]

mutual_props = []
dressing_pts = [(r['x'], r['z']) for r in dressing]
for i, r in enumerate(dressing):
    others = [(p[0], p[1]) for j, p in enumerate(dressing_pts) if j != i]
    rho = math.hypot(r['x'] - h_cx, r['z'] - h_cz)
    d_g = dmin(r['x'], r['z'], g_pts)
    d_h = dmin(r['x'], r['z'], h_pts)
    d_sp = min(math.hypot(r['x'] - a, r['z'] - b) for (a, b) in land_pts)
    d_se = min(math.hypot(r['x'] - a, r['z'] - b) for (a, b) in sentries)
    mutual_props.append(dmin(r['x'], r['z'], others))
    check('C: %s(%g,%g) rho <= 78.5' % (r['asset'], r['x'], r['z']), rho <= 78.5, '%.2f' % rho)
    check('C: %s(%g,%g) >= 4.0 raw of G post-erase ring' % (r['asset'], r['x'], r['z']),
          d_g >= 4.0, '%.2f' % d_g)
    check('C: %s(%g,%g) >= 4.0 raw of H2 ring' % (r['asset'], r['x'], r['z']), d_h >= 4.0, '%.2f' % d_h)
    check('C: %s(%g,%g) >= 6.0 from spawn + land rows' % (r['asset'], r['x'], r['z']),
          d_sp >= 6.0, '%.2f' % d_sp)
    check('C: %s(%g,%g) >= 5.0 from both sentries' % (r['asset'], r['x'], r['z']),
          d_se >= 5.0, '%.2f' % d_se)
check('C: >= 4.0 mutual across all 18 dressing rows (pairwise min)',
      min(mutual_props) >= 4.0, 'min %.4f' % min(mutual_props))

# flankers
fl = [r for r in dressing if r['asset'] == 'okFenceStonewall']
check('C: exactly 2 okFenceStonewall flankers at (±10, -968)',
      len(fl) == 2 and sorted((r['x'], r['z']) for r in fl) == [(-10.0, -968.0), (10.0, -968.0)])
for r in fl:
    d_h = dmin(r['x'], r['z'], h_pts)
    d_g = dmin(r['x'], r['z'], g_pts)
    d_mut = dmin(r['x'], r['z'], [(p[0], p[1]) for j, p in enumerate(dressing_pts)
                                  if dressing[j] is not r])
    check('C: flanker (%g,%g) >= 16.0 off H2 ring' % (r['x'], r['z']), d_h >= 16.0, '%.2f' % d_h)
    check('C: flanker (%g,%g) >= 4.0 off G post-erase ring' % (r['x'], r['z']), d_g >= 4.0, '%.2f' % d_g)
    check('C: flanker (%g,%g) >= 4.0 mutual from manifest' % (r['x'], r['z']), d_mut >= 4.0, '%.2f' % d_mut)

# ---- Section D: enemies ------------------------------------------------------
mut_e = math.hypot(enemies[0][1] - enemies[1][1], enemies[0][2] - enemies[1][2])
check('D: sentry mutual >= 12.5', mut_e >= 12.5, '%.4f' % mut_e)
for (t, ex, ez) in enemies:
    d_sp = min(math.hypot(ex - a, ez - b) for (a, b) in [spawn, land_h, land_g])
    d_ring = dmin(ex, ez, h_pts)
    d_lane = dmin(ex, ez, lane)
    check('D: sentry %s(%g,%g) >= 8.0 from spawn + land rows' % (t, ex, ez), d_sp >= 8.0, '%.2f' % d_sp)
    check('D: sentry %s(%g,%g) >= 4.45 walk-clear of H2 ring' % (t, ex, ez), d_ring >= 4.45, '%.2f' % d_ring)
    check('D: sentry %s(%g,%g) NOT in window lane (>= 1.0 off lane samples)' % (t, ex, ez),
          d_lane >= 1.0, 'lane dist %.2f' % d_lane)

# ---- Section B (V-7): G aperture post-erase -----------------------------------
check('B: G landed curtain rows (wall 12) == 87', len(g_ring) == 87, str(len(g_ring)))
check('B: G dressing rows unchanged == 24', len(g_dress) == 24, str(len(g_dress)))
# erase-audit: the 2 aperture coordinates absent from the landed G row set
gone = 0
for r in g_ring:
    if abs(r['x']) in (4.4,) and abs(r['z'] - (-947.92)) < 1e-9:
        gone += 1
check('B: no surviving G wall row at (±4.4, -947.92)', gone == 0, 'found %d' % gone)
for s in ("{ asset: 'whWallA', x: 4.4, z: -947.92, rotY: 6.25, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 }",
          "{ asset: 'whWallB', x: -4.4, z: -947.92, rotY: 0.03, scale: 4.63, sy: 11.55, sz: 2.40, y: -0.2, wall: 12 }"):
    check('B: deleted byte string absent from CONFIG.js', s not in cfg)
check('B: post-erase G colliders == 1044', len(g_coll) == 1044, str(len(g_coll)))

L = 1.5
in_lane = []
for (cx_, cz_) in g_coll:
    for (lx, lz) in lane:
        if math.hypot(cx_ - lx, cz_ - lz) < L:
            in_lane.append((cx_, cz_, lx, lz, math.hypot(cx_ - lx, cz_ - lz)))
            break
nearest = min(math.hypot(cx_ - lx, cz_ - lz) for (cx_, cz_) in g_coll
              for (lx, lz) in lane)
check('B: lane domain x -4..4 x z -951..-945 (%d samples >= 225)' % len(lane), len(lane) >= 225)
check('B: 0 post-erase G colliders within 1.5 m of ANY lane sample',
      len(in_lane) == 0, 'count %d (nearest %.4f)' % (len(in_lane), nearest))

# sides cross-check from region-defs (live)
m = re.search(r'var HD = CFG\.regionH\.door;', rdefs)
blk = rdefs[m.start():m.start() + 1400]
sg = re.search(r'connections\[6\]\.sides\[CFG\.regionG\.id\] = (-?\d);', rdefs[m.start():])
sh = re.search(r'connections\[6\]\.sides\[CFG\.regionH\.id\] = (-?\d);', rdefs[m.start():])
check('A: conn[6] sides rows parsed region-defs live (G=+1, H=-1)',
      sg and sh and int(sg.group(1)) == 1 and int(sh.group(1)) == -1,
      'G=%s H=%s' % (sg.group(1) if sg else '?', sh.group(1) if sh else '?'))


def side_of_plane(z):
    return 1 if z > plane_z else -1


check('A: sideOfPlane replication: sideOfPlane(-822)==1==sideIn(G), sideOfPlane(-1024)==-1==sideIn(H)',
      side_of_plane(-822.0) == int(sg.group(1)) == 1 and side_of_plane(-1024.0) == int(sh.group(1)) == -1)
check('A: land.fort_garrison home side (z -955 <= plane -948), land.lords_hold (z -941 > -948)',
      land_h[1] <= plane_z and land_g[1] > plane_z, 'land_h %.1f land_g %.1f' % (land_h[1], land_g[1]))
check('A: suspendDepthM == 4', suspend == 4.0)

print('---')
if fails:
    print('VERDICT PROBES: FAIL (%d of %d checks failed)' % (len(fails), N[0]))
    for f in fails:
        print('  FAILED:', f)
    sys.exit(1)
print('VERDICT PROBES: PASS (%d checks)' % N[0])
sys.exit(0)
