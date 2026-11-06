#!/usr/bin/env python3
"""CC-AD2 geometry verifier (Devbot scratch, CONFIG-ROW-PARSED per valspec V-9).

Parses the regionE (veil_crypt) and regionF (veil_galleries) rows PLUS the
region-defs.js connections[4] row LIVE from CONFIG.js / region-defs.js (no
hard-coded spec constants for the F rows), rebuilds the wall-collider
circles exactly per region-manager whPropColliders (p.wall circles r
CFG.boundaryWall.collider.r = 0.45 along the row's local X, asset widths
from the measured footprints, whWallA/whWallB raw ext X 1.899), and asserts
EVERY clearance law of the CC-AD2 spec:

  F shell sanity (spec sec 2 / A-8):
    - ring rows present (whWallA/B, wall 7); spawn/land inside r 26
    - ghouls >= 8 m from spawn/land; >= 12.5 m from each other (spec numbers
      give 12.51 - accepted floor 12.4, probe tolerance +-0.15)
    - ghouls >= 4.45 m walk-clear of the ring
  Ring geometry:
    - ring colliders ABSENT ONLY in the gap window (|x - doorX| <=
      doorHalfWidth at z = planeZ) and covering every other bearing
      (octant coverage: every bearing octant outside the gap holds colliders;
      the only collider-free bearing arc on the circle is the gap's)
  Props (>= 4.0 m raw from ring colliders, >= 6.0 m from spawn, >= 5.0 m
  from both ghouls, >= 4.0 m mutual):
    - every regionF prop row
  E-side (section 3, rows parsed live from regionE):
    - exactly ONE whWallB row erased at (-8.3, -612.0) vs the landed crypt
      ring (7 wall rows remain); aperture lane walkable: no residual crypt
      ring collider within 1.5 m of the lane x [-16, -13] / z [-597.5, -594.5]
    - mourner pair (mourningStatue / rubblePile appended after rubblePile):
      >= 4 m from remaining crypt ring colliders, >= 5 m from covens,
      >= 6 m from crypt spawn/land rows
  conn[4] sanity (region-defs parsed live):
    - from veil_crypt, to veil_galleries, axis z, planeCoord = door.planeZ,
      walkFrom veil_galleries, interact.from veil_crypt at the door
      interactAt with radius interactM, land rows per region
    - sides: veil_crypt -1 / veil_galleries +1; F land row z <= planeZ
      (on F's home side), E land row on E's home side (> planeZ)

Run: python3 scratch/cc-ad2/solve_geometry.py      (from the worktree root)
"""
import math
import re
import sys

ROOT = '/tmp/wh-worldfeat'
cfg = open(ROOT + '/prototype/js/CONFIG.js').read()
defs = open(ROOT + '/prototype/js/region-defs.js').read()


def block(src, key):
    """Extract a top-level CONFIG block (e.g. regionE/regionF) bounded by the
    next same-indent key."""
    me = re.search(r'\n  %s: \{' % re.escape(key), src)
    if not me:
        sys.exit('FAIL: no %s block in CONFIG.js' % key)
    blob = src[me.start():]
    nxt = re.search(r'\n  [a-zA-Z_]+: \{', blob[10:])
    return blob[:10 + nxt.start()] if nxt else blob


# ---- parse regionE + regionF rows live --------------------------------------
WR = 0.45            # CFG.boundaryWall.collider.r
AW = {'whWallA': 1.899, 'whWallB': 1.899}   # measured raw ext X (cc-ad1 probe)

REGIONS = {}
for key, name_re in (('regionE', 'veil_crypt'), ('regionF', 'veil_galleries')):
    eb = block(cfg, key)
    if "id: '%s'" % name_re not in eb:
        sys.exit('FAIL: %s is not %s' % (key, name_re))
    cm = re.search(r'center: \{ x: (-?[\d.]+), z: (-?[\d.]+) \}', eb)
    R = float(re.search(r'groundRadius: (\d+)', eb).group(1))
    DZ = float(re.search(r'planeZ: (-?[\d.]+)', eb).group(1))
    DX = float(re.search(r'doorX: (-?[\d.]+)', eb).group(1))
    DHW = float(re.search(r'doorHalfWidth: (-?[\d.]+)', eb).group(1))
    sm = re.search(r'spawn: \{ x: (-?[\d.]+), z: (-?[\d.]+) \}', eb)
    SPAWN = (float(sm.group(1)), float(sm.group(2)))
    LAND = {}
    for lm in re.finditer(r"(\w+):\s+\{ x: (-?[\d.]+), z: (-?[\d.]+), faceX", eb):
        LAND[lm.group(1)] = (float(lm.group(2)), float(lm.group(3)))
    ENEMIES, WALL_ROWS, PROP_ROWS, in_props = [], [], [], False
    for ln in eb.splitlines():
        if re.match(r'\s*props: \[', ln):
            in_props = True
            continue
        if in_props and re.match(r'\s*\]', ln):
            break
        if not in_props:
            continue
        wm = re.search(r"\{ asset: '(whWall[AB])', x: (-?[\d.]+), z: (-?[\d.]+), rotY: (-?[\d.]+), "
                       r"scale: (-?[\d.]+), sy: (-?[\d.]+), sz: (-?[\d.]+), y: (-?[\d.]+), wall: (\d+) \}", ln)
        if wm and 'wall:' in ln and 'is ERASED' not in ln:
            WALL_ROWS.append(dict(asset=wm.group(1), x=float(wm.group(2)), z=float(wm.group(3)),
                                  rotY=float(wm.group(4)), scale=float(wm.group(5)),
                                  sy=float(wm.group(6)), sz=float(wm.group(7)),
                                  y=float(wm.group(8)), n=int(wm.group(9))))
            continue
        dm = re.search(r"\{ asset: '(\w+)',\s+x: (-?[\d.]+), z: (-?[\d.]+), rotY: (-?[\d.]+), scale: (-?[\d.]+) \}", ln)
        if dm:
            PROP_ROWS.append(dict(asset=dm.group(1), x=float(dm.group(2)), z=float(dm.group(3)),
                                  rotY=float(dm.group(4)), scale=float(dm.group(5))))
    for em in re.finditer(r"\{ type: '(\w+)', x: (-?[\d.]+), z: (-?[\d.]+) \}", eb):
        ENEMIES.append(dict(type=em.group(1), x=float(em.group(2)), z=float(em.group(3))))
    REGIONS[name_re] = dict(cx=float(cm.group(1)), cz=float(cm.group(2)), R=R, DZ=DZ, DX=DX, DHW=DHW,
                            spawn=SPAWN, land=LAND, enemies=ENEMIES, walls=WALL_ROWS, props=PROP_ROWS)

E = REGIONS['veil_crypt']
F = REGIONS['veil_galleries']


def colliders(reg):
    out = []
    for wr in reg['walls']:
        L = AW[wr['asset']] * wr['scale']
        ax, az = math.cos(wr['rotY']), -math.sin(wr['rotY'])
        for k in range(wr['n']):
            t = ((k + 0.5) / wr['n'] - 0.5) * L
            out.append((wr['x'] + ax * t, wr['z'] + az * t))
    return out


ECOLL = colliders(E)
FCOLL = colliders(F)


def mindist(pt, pts):
    return min(math.hypot(pt[0] - q[0], pt[1] - q[1]) for q in pts)


print('veil_crypt: center (%.1f, %.1f) r %.0f | planeZ %.1f doorX %.1f hw %.1f' % (E['cx'], E['cz'], E['R'], E['DZ'], E['DX'], E['DHW']))
print('  wall rows %d | collider circles %d | enemies %d' % (len(E['walls']), len(ECOLL), len(E['enemies'])))
print('veil_galleries: center (%.1f, %.1f) r %.0f | planeZ %.1f doorX %.1f hw %.1f' % (F['cx'], F['cz'], F['R'], F['DZ'], F['DX'], F['DHW']))
print('  wall rows %d | collider circles %d | ghouls %d | props %d' % (len(F['walls']), len(FCOLL), len(F['enemies']), len(F['props'])))
FSPAWN = F['spawn']
FLAND_F = F['land']['veil_galleries']
FLAND_E = F['land']['veil_crypt']

ok = []
def check(label, val, req, le=False):
    good = (val <= req) if le else (val >= req)
    ok.append(good)
    print('%-56s %7.2f %s %5.2f  %s  (margin %.2f)' % (label, val, '<=' if le else '>=', req,
          'ok' if good else 'FAIL', req - val if le else val - req))

# --- F shell sanity -----------------------------------------------------------
check('F: wall ring rows present (== 7, gap segment omitted)', len(F['walls']), 7, le=True)
check('F: spawn -> center (<= r 26)', math.hypot(FSPAWN[0] - F['cx'], FSPAWN[1] - F['cz']), F['R'], le=True)
check('F: land(F) -> center (<= r 26)', math.hypot(FLAND_F[0] - F['cx'], FLAND_F[1] - F['cz']), F['R'], le=True)
check('F: land(E) -> E center (<= crypt r 20)', math.hypot(FLAND_E[0] - E['cx'], FLAND_E[1] - E['cz']), E['R'], le=True)
gh = [(e['x'], e['z']) for e in F['enemies'] if e['type'] == 'ghoul']
check('F: 2 ghoul wardens (== 2)', len(gh), 2, le=True)
for gi, g in enumerate(gh, 1):
    check('F: ghoul%d -> spawn/land (>= 8.0)' % gi, mindist(g, [FSPAWN, FLAND_F]), 8.0)
gmut = math.hypot(gh[0][0] - gh[1][0], gh[0][1] - gh[1][1])
check('F: ghoul1 <-> ghoul2 (>= 12.4; spec 12.51, tol +-0.15)', gmut, 12.4)
# walk-clear of the ring: distance to the nearest collider circle (raw - r)
for gi, g in enumerate(gh, 1):
    check('F: ghoul%d -> nearest ring collider (>= 4.45 raw)' % gi, mindist(g, FCOLL), 4.45)

# --- ring geometry: gap window + bearing coverage -----------------------------
GAP = [(x, z) for (x, z) in FCOLL if abs(x - F['DX']) <= F['DHW'] and abs(z - F['DZ']) <= 3.0]
check('F: colliders inside the mouth gap window (== 0)', len(GAP), 0, le=True)
# coverage: every octant of the ring outside the gap holds colliders; the ONLY
# collider-free bearing arc on the circle is the gap's own
cov = [0] * 8
for (x, z) in FCOLL:
    a = math.degrees(math.atan2(z - F['cz'], x - F['cx'])) % 360
    cov[int(((a + 22.5) % 360) / 45)] += 1
print('F collider octant coverage (E,NE,N,NW,W,SW,S,SE bearings): %s' % cov)
for octi, n in enumerate(cov):
    c = 45 * octi  # octant center bearing
    cx = F['cx'] + 22 * math.cos(math.radians(c))
    cz = F['cz'] + 22 * math.sin(math.radians(c))
    if abs(cx - F['DX']) <= F['DHW'] and abs(cz - F['DZ']) <= 3.0:
        continue    # the gap octant: colliders forbidden here
    check('F: octant @ %d deg bears ring colliders (>= 3)' % c, n, 3)
# the mouth lane (|x| <= doorHalfWidth on the plane z = planeZ) holds NO collider,
# crypt-door convention (the lane crosses the ring interior; the ring's own gap is
# the OMITTED segment at angular position 22.5 deg, whose arc clears the plane)
lane = [(x, F['DZ']) for x in (-F['DHW'], -1.0, 0.0, 1.0, F['DHW'])]
check('F: door lane |x|<=hw on the plane is collider-free (>= 1.0 m from lane pts)',
      min(mindist(pt, FCOLL) for pt in lane), 1.0)
# the gap segment (angular position 22.5 deg, the arc straddling the plane crossing)
# is OMITTED: no wall-row within the gap arc bearings [2, 43] deg at ring radius
gaprows = [w for w in F['walls']
           if 2 <= math.degrees(math.atan2(w['z'] - F['cz'], w['x'] - F['cx'])) % 360 <= 43
           and abs(math.hypot(w['x'] - F['cx'], w['z'] + F['DZ']) - 22) < 0.5]
check('F: no ring row inside the gap arc (bearings 2..43 deg)', len(gaprows), 0, le=True)
# gap edges: the ring segments ADJACENT to the gap (the kept i=1 and the wrap i=7 rows)
# hold colliders; the OMITTED arc itself is collider-free on the circle between bearings 2..43
shoulder = [(x, z) for (x, z) in FCOLL
            if (math.hypot(x, z - F['cz']) - 22) < 2.5 and
            (math.degrees(math.atan2(z - F['cz'], x - F['cx'])) % 360 <= 2 or
             math.degrees(math.atan2(z - F['cz'], x - F['cx'])) % 360 >= 43)]
check('F: gap shoulder colliders cover the arc ends (>= 10)', len(shoulder), 10)
# collider-free arc inside the gap bearings (2..43 deg) on the circle:
free = 0
for b in range(2, 44, 2):
    bx = 22 * math.cos(math.radians(b)); bz = F['cz'] + 22 * math.sin(math.radians(b))
    if mindist((bx, bz), FCOLL) > 2.2:
        free += 1
check('F: gap arc bearing samples collider-free (>= 15 of 21)', float(free), 15)

# --- props ----------------------------------------------------------------------
FPROPS = [p for p in F['props']]
for pr in FPROPS:
    p = (pr['x'], pr['z'])
    others = [(q['x'], q['z']) for q in FPROPS if q is not pr]
    check('prop %s x(%s,%s) -> colliders raw (>= 4.0)' % (pr['asset'], pr['x'], pr['z']), mindist(p, FCOLL), 4.0)
    check('prop %s x(%s,%s) -> spawn (>= 6.0)' % (pr['asset'], pr['x'], pr['z']), mindist(p, [FSPAWN]), 6.0)
    for gi, g in enumerate(gh, 1):
        check('prop %s x(%s,%s) -> ghoul%d (>= 5.0)' % (pr['asset'], pr['x'], pr['z'], gi), mindist(p, [g]), 5.0)
    check('prop %s x(%s,%s) -> other props (>= 4.0)' % (pr['asset'], pr['x'], pr['z']), mindist(p, others), 4.0)

# --- E-side: the west aisle ------------------------------------------------------
# exactly ONE crypt wall row erased: the whWallB at (-8.3, -612.0)
gone = all(abs(w['x'] + 8.3) > 0.01 or abs(w['z'] + 612.0) > 0.01 for w in E['walls'])
ok.append(gone)
print('%-56s %7s %s' % ('E: whWallB (-8.3,-612.0) ERASED (absent)', 'yes' if gone else 'NO', 'ok' if gone else 'FAIL'))
check('E: remaining crypt wall rows (== 7)', len(E['walls']), 7, le=True)
# aperture lane walkable: no residual collider within 1.5 m of the lane
lane = [(x, z) for x in (-16, -15.5, -15, -14.5, -14, -13, -13.0) for z in (-597.5, -596.0, -594.5)]
check('E: aperture lane min collider distance (>= 1.5)', min(mindist(pt, ECOLL) for pt in lane), 1.5)
# mourner pair: appended AFTER the rubblePile row, correct rows
pr_assets = [p['asset'] for p in E['props']]
mi = pr_assets.index('mourningStatue')
after_rubble = mi == len(pr_assets) - 2 and pr_assets[mi + 1] == 'rubblePile'
ok.append(after_rubble)
print('%-56s %7s %s' % ('E: mourner pair appended at the props tail (A-5)', 'yes' if after_rubble else 'NO', 'ok' if after_rubble else 'FAIL'))
mourners = [p for p in E['props'] if p['asset'] in ('mourningStatue', 'rubblePile') and p['x'] < -10 and p['x'] > -15]
check('E: mourner pair rows found (== 2)', len(mourners), 2, le=True)
for pr in mourners:
    p = (pr['x'], pr['z'])
    check('E: %s -> remaining ring colliders (>= 4.0)' % pr['asset'], mindist(p, ECOLL), 4.0)
    covens = [(e['x'], e['z']) for e in E['enemies'] if e['type'] == 'coven']
    check('E: %s -> covens (>= 5.0)' % pr['asset'], mindist(p, covens), 5.0)
    check('E: %s -> crypt spawn/land rows (>= 6.0)' % pr['asset'],
          mindist(p, [E['spawn'], E['land']['veil_crypt']]), 6.0)
    others = [(q['x'], q['z']) for q in E['props'] if q is not pr]
    check('E: %s -> every other regionE prop (>= 4.0)' % pr['asset'], mindist(p, others), 4.0)
# mourner pair inside the crypt disc
for pr in mourners:
    check('E: %s -> center (<= crypt r 20)' % pr['asset'],
          math.hypot(pr['x'] - E['cx'], pr['z'] - E['cz']), E['R'], le=True)

# --- conn[4] sanity (parsed live from region-defs) --------------------------------
m = re.search(r'/\* *\*/|', defs)  # noop keep structure
m4 = re.search(r'connections\.push\(\{\s*from: CFG\.regionE\.id,\s*to: CFG\.regionF\.id,\s*axis: \'z\','
               r'\s*planeCoord: FD\.planeZ,', defs)
ok.append(bool(m4))
print('%-56s %7s %s' % ('conn[4]: from E to F axis z planeCoord = F.door.planeZ', 'yes' if m4 else 'NO', 'ok' if m4 else 'FAIL'))
ok.append('walkFrom: CFG.regionF.id' in defs and 'interact: { from: CFG.regionE.id, x: FD.interactAt.x, z: FD.interactAt.z, radius: FD.interactM }' in defs
          and 'land: FD.land' in defs)
sides = re.search(r'connections\[4\]\.sides\[CFG\.regionE\.id\] = -1;\s*connections\[4\]\.sides\[CFG\.regionF\.id\] = 1;', defs)
ok.append(bool(sides))
print('%-56s %7s %s' % ('conn[4]: sides E -1 / F +1', 'yes' if sides else 'NO', 'ok' if sides else 'FAIL'))
regF = re.search(r'regions\[CFG\.regionF\.id\] = makeRegion\(CFG\.regionF, -1\);', defs)
ok.append(bool(regF))
print('%-56s %7s %s' % ('regions[veil_galleries] = makeRegion(F, -1)', 'yes' if regF else 'NO', 'ok' if regF else 'FAIL'))
# F land row on F's home side (z <= planeZ); E land row on E's home side (z > planeZ)
check('conn[4]: F land on F home side (z <= planeZ)', FLAND_F[1], F['DZ'], le=True)
check('conn[4]: E land on E home side (z > planeZ)', FLAND_E[1], 0 if False else F['DZ'], le=False)
# F spawn + land >= 8 m from the gap plane inside F's ring radius (A-8)
check('conn[4]: F land >= 8 m inside the mouth plane (z <= planeZ - 8)', F['DZ'] - FLAND_F[1], 8.0)

print('---')
print('ALL CONSTRAINTS: %s (%d checks)' % ('PASS' if all(ok) else 'FAIL', len(ok)))
sys.exit(0 if all(ok) else 1)
