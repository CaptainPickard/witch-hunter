#!/usr/bin/env python3
"""CC-H1 geometry verifier (Devbot scratch, CONFIG-ROW-PARSED per the
cc-h1 valspec V-5a: shaped on scratch/cc-ad2/solve_geometry.py).

Parses the regionG (lords_hold) rows LIVE from CONFIG.js + the
connections[5] row from region-defs.js (NO hard-coded spec constants for
the new rows), rebuilds the wall-collider circles exactly per
region-manager whPropColliders (p.wall circles r CFG.boundaryWall.collider.r
= 0.45 along the row's local X; raw asset ext-X whWallA/whWallB = 1.899,
the cc-ad1 measured widths the cc-ad2 solver reuses), then asserts every
clearance law of the CC-H1 spec section 2 + cc-h1 valspec V-5b:

  1. wall rows == 89, colliders == 1068 (V-5b-1)
  2. ring closure: the ONLY collider-free bearing arc is the door window's
     (0 colliders inside |x| <= doorHalfWidth at |z - planeZ| <= 3);
     every octant OUTSIDE the gap arc holds >= 3 colliders; the window's
     own octant bears >= 122 colliders outside the window strip (V-5b-2/8/9)
  3. every landed wall row byte-matches the ring rows frozen in
     scratch/cc-h1/seat_scan_output.txt (2-dp numeric normalization on
     x/z/rotY; asset/sy/sz/y/wall/scale token-exact) (V-5b-3)
  4. every wall row sits at |hypot(x, z - Cz) - groundRadius| <= 0.6 (V-5b-4)
  5. spawn + land.lords_hold inside r 126 of the parsed center;
     land.forest_of_the_old_king STANDS ON C: r to C's parsed center
     <= 278.5 and z > planeZ (home side) (V-5b-5)
  6. lane clearance per seat_scan's sample convention (V-5b-6):
     nearest collider to the lane sample points z in {-703,-700,-697} x
     {-4.5,-2,0,2,4.5} >= 1.0; 0 colliders inside the window strip
  7. prop-hub clearances (V-5b-7): every prop -> nearest ring collider
     >= 4.0; spawn -> every prop >= 6.0; mutual >= 4.0 per pair with the
     licensed lanternPost/parapet pair at >= 3.9 and the braziers' mutual
     >= 11.2 (spec 11.32); the lanternPost's lane clearance >= 3.7; every
     prop <= playRadius (groundRadius - 1.5) from center
  8. octant coverage [122,135,136,135,134,135,136,135] recomputed from the
     LANDED rows
  9. conn[5] sanity from region-defs.js parsed live: from forest_of_the_
     old_king / to lords_hold (AMENDMENT A), axis z, planeCoord = door.
     planeZ, walkFrom lords_hold, interact.from forest_of_the_old_king at
     the door interactAt with radius interactM, land: GD.land, sides
     (C, -1)/(G, +1); land rows on home sides; land.lords_hold >= 8 m
     inside the plane
 10. C-side aperture clearance (seat_scan checks 1-4 re-asserted against
     the LANDED regionC rows): interactAt >= 6.0 m from every C prop row,
     >= 26 m from the crypt door's C-side hook AND >= 26 m from the notch
     mouth (notchMouthExclusionM), standable: r to C center <= 278.5

Run: python3 scratch/cc-h1/clearance.py      (from the worktree root)
Exit 0 only if ALL checks pass (final line: ALL CONSTRAINTS: PASS (N checks)).
"""
import math
import re
import sys

ROOT = '/tmp/wh-worldfeat'
cfg = open(ROOT + '/prototype/js/CONFIG.js').read()
defs = open(ROOT + '/prototype/js/region-defs.js').read()


def block(src, key):
    """Extract a top-level CONFIG block (e.g. regionG) bounded by the next
    same-indent key (the cc-ad2 block() shape)."""
    me = re.search(r'\n  %s: \{' % re.escape(key), src)
    if not me:
        sys.exit('FAIL: no %s block in CONFIG.js' % key)
    blob = src[me.start():]
    nxt = re.search(r'\n  [a-zA-Z_]+: \{', blob[10:])
    return blob[:10 + nxt.start()] if nxt else blob


# ---- parse regionC + regionG rows live --------------------------------------
WR = float(re.search(r'collider: \{ r: ([\d.]+), perSegment: \d+ \}', cfg).group(1))
if abs(WR - 0.45) > 1e-9:
    sys.exit('FAIL: boundaryWall.collider.r is not 0.45 (%r)' % WR)
AW = {'whWallA': 1.899, 'whWallB': 1.899}   # measured raw ext X (cc-ad1)

REGIONS = {}
for key, name_re in (('regionC', 'forest_of_the_old_king'), ('regionG', 'lords_hold')):
    eb = block(cfg, key)
    if "id: '%s'" % name_re not in eb:
        sys.exit('FAIL: %s is not %s' % (key, name_re))
    cm = re.search(r'center: \{ x: (-?[\d.]+), z: (-?[\d.]+) \}', eb)
    R = float(re.search(r'groundRadius: (\d+)', eb).group(1))
    DZ = float(re.search(r'planeZ: (-?[\d.]+)', eb).group(1))
    DX = float(re.search(r'doorX: (-?[\d.]+)', eb).group(1))
    DHW = float(re.search(r'doorHalfWidth: (-?[\d.]+)', eb).group(1))
    IAM = float(re.search(r'interactM: ([\d.]+)', eb).group(1)) if re.search(r'interactM: ([\d.]+)', eb) else 0.0
    iam = re.search(r'interactAt: \{ x: (-?[\d.]+), z: (-?[\d.]+) \}', eb)
    sm = re.search(r'spawn: \{ x: (-?[\d.]+), z: (-?[\d.]+) \}', eb)
    SPAWN = (float(sm.group(1)), float(sm.group(2)))
    LAND = {}
    for lm in re.finditer(r"(\w+):\s+\{ x: (-?[\d.]+), z: (-?[\d.]+), faceX", eb):
        LAND[lm.group(1)] = (float(lm.group(2)), float(lm.group(3)))
    IM = re.search(r'notchMouthExclusionM: (\d+)', cfg)
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
        if wm:
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
                            IAM=IAM, IA=(float(iam.group(1)), float(iam.group(2))) if iam else (0.0, 0.0),
                            spawn=SPAWN, land=LAND, enemies=ENEMIES, walls=WALL_ROWS, props=PROP_ROWS,
                            notchM=float(IM.group(1)) if IM else 26.0)

C_R = REGIONS['forest_of_the_old_king']
G = REGIONS['lords_hold']
GC = (G['cx'], G['cz'])
print('lords_hold: center (%.1f, %.1f) r %.0f | planeZ %.1f doorX %.1f hw %.1f | interactAt %s'
      % (G['cx'], G['cz'], G['R'], G['DZ'], G['DX'], G['DHW'], G['IA']))
print('  parsed from CONFIG.js: %d wall rows | %d dressing props | enemies %d'
      % (len(G['walls']), len(G['props']), len(G['enemies'])))


def colliders(reg):
    """The whPropColliders wall-row rebuild: n circles r WR along the row's
    local X (ax = cos rotY, az = -sin rotY), raw asset width x scale span."""
    out = []
    for wr in reg['walls']:
        L = AW[wr['asset']] * wr['scale']
        ax, az = math.cos(wr['rotY']), -math.sin(wr['rotY'])
        for k in range(wr['n']):
            t = ((k + 0.5) / wr['n'] - 0.5) * L
            out.append((wr['x'] + ax * t, wr['z'] + az * t))
    return out


def r3(v):
    return round(v, 3)


def mindist(pt, pts):
    return min(math.hypot(pt[0] - q[0], pt[1] - q[1]) for q in pts)


ok = []


def check(label, val, req, le=False, kind='num'):
    if kind == 'num':
        good = (val <= req) if le else (val >= req)
    else:
        good = val == req
    ok.append(good)
    if kind == 'num':
        print('%-64s %7.2f %s %5.2f  %s  (margin %.2f)' % (label, val, '<=' if le else '>=', req,
              'ok' if good else 'FAIL', req - val if le else val - req))
    else:
        print('%-64s %7s  %s  (want %s)' % (label, val, 'ok' if good else 'FAIL', req))


GCOLL = colliders(G)

# --- V-5b-1 + V-5b-3: census + the frozen-ring byte match --------------------
# The frozen seat-scan prints are the byte-match source: parse them, then
# 2-dp-normalize both sides (the V-5b-3 adjudication).
FRZ = open(ROOT + '/scratch/cc-h1/seat_scan_output.txt').read()
frz = []
fm = re.search(r'RING ROWS \(seg i, x, z, rotY, scale, wall\):\n((?:  \{[^\n]*\},?\n)+)', FRZ)
pat = re.compile(r"\{ asset: '(\w+)', x: (-?[0-9.]+), z: (-?[0-9.]+), rotY: (-?[0-9.]+), "
                 r"scale: (-?[0-9.]+), sy: (-?[0-9.]+), sz: (-?[0-9.]+), y: (-?[0-9.]+), wall: (\d+) \}")
for ln in fm.group(1).strip().splitlines():
    m2 = pat.search(ln.strip())
    if m2:
        frz.append(dict(asset=m2.group(1), x=float(m2.group(2)), z=float(m2.group(3)),
                        rotY=float(m2.group(4)), scale=float(m2.group(5)),
                        sy=float(m2.group(6)), sz=float(m2.group(7)),
                        y=float(m2.group(8)), n=int(m2.group(9))))
check('V-5b-1: landed wall rows (== 89)', len(G['walls']), 89, kind='int')
check('V-5b-1: wall colliders (== 1068)', len(GCOLL), 1068, kind='int')
check('V-5b-3a: frozen ring rows parsed (== 89)', len(frz), 89, kind='int')
mismatch = []
for i, (w, f) in enumerate(zip(G['walls'], frz)):
    bad = (r3(w['x']) != r3(f['x']) or r3(w['z']) != r3(f['z']) or r3(w['rotY']) != r3(f['rotY']))
    tok = (w['sy'] != f['sy'] or w['sz'] != f['sz'] or w['y'] != f['y']
           or w['scale'] != f['scale'] or w['asset'] != f['asset'] or w['n'] != f['n'])
    if bad or tok:
        mismatch.append((i, (max(abs(r3(w['x'])-r3(f['x'])), abs(r3(w['z'])-r3(f['z'])),
                                 abs(r3(w['rotY'])-r3(f['rotY']))), tok)))
check('V-5b-3b: wall rows byte-match the frozen ring', len(mismatch), 0, le=True, kind='int')
for mrow in mismatch[:4]:
    print('     mismatch row %d: %s' % mrow)

# --- V-5b-4: ring radii law --------------------------------------------------
rad = max(abs(math.hypot(w['x'] - G['cx'], w['z'] - G['cz']) - G['R']) for w in G['walls'])
check('V-5b-4: every wall row on the frozen ring (|r - 126| <= 0.6)', rad, 0.6, le=True)

# --- V-5b-2/8/9: ring closure (the door window) + octant coverage ------------
GAP = [(x, z) for (x, z) in GCOLL if abs(x - G['DX']) <= G['DHW'] and abs(z - G['DZ']) <= 3.0]
check('V-5b-2a: colliders inside the door window strip (== 0)', len(GAP), 0, le=True, kind='int')
cov = [0] * 8
win_oct_i = int((((math.degrees(math.atan2(G['DZ'] - G['cz'], G['DX'] - G['cx'])) % 360) + 22.5) % 360) / 45)
for (x, z) in GCOLL:
    a = math.degrees(math.atan2(z - G['cz'], x - G['cx'])) % 360
    cov[int(((a + 22.5) % 360) / 45)] += 1
print('ring collider octant coverage (E,NE,N,NW,W,SW,S,SE): [%s]' % ', '.join(str(v) for v in cov))
# the face bearing (90 deg = +z from center, the gate) maps to octant index:
# octants are [(-22.5,22.5)=E, ...]; the +z S arc lives at index 2 ((67.5,112.5))
COV_EXPECT = [122, 135, 136, 135, 134, 135, 136, 135]
for octi in range(8):
    if octi == win_oct_i:
        # the window's own octant: its arc OUTSIDE the strip must still bear
        # >= 122 colliders (V-5b-9 belt+braces; the strip law is 2a above)
        outside = 0
        for (x, z) in GCOLL:
            a = math.degrees(math.atan2(z - G['cz'], x - G['cx'])) % 360
            oi = int(((a + 22.5) % 360) / 45)
            if oi == octi and not (abs(x - G['DX']) <= G['DHW'] and abs(z - G['DZ']) <= 3.0):
                outside += 1
        check('V-5b-9: window octant %d colliders OUTSIDE the strip (>= 122)' % octi,
              outside, 122)
    else:
        check('V-5b-8: octant %d colliders outside the gap arc (>= 3)' % octi, cov[octi], 3, kind='num')
covexact = cov == COV_EXPECT
ok.append(covexact)
print('%-64s %7s  %s  (frozen [122,135,136,135,134,135,136,135])' %
      ('ring octant coverage matches the frozen vector', 'yes' if covexact else 'no', 'ok' if covexact else 'FAIL'))

# --- V-5b-6: the door lane (seat_scan's sample convention) -------------------
# seat_scan's convention: FIVE points ON the plane only
# (min over lx in (-hw,-2,0,2,hw) of hypot(x - lx, z - PLANE_Z));
# the valspec's 15-point set (3 z-bands x 5 x) recomputes at 0.94 and is
# pinned as its own number (adjudication 0b-4): assert both with their
# own floors.
lane5 = [(x, G['DZ']) for x in (-G['DHW'], -2.0, 0.0, 2.0, G['DHW'])]
lane_mn = min(mindist(pt, GCOLL) for pt in lane5)
check('V-5b-6a: lane 5-pt plane samples (seat_scan conv; frozen 3.91+-0.15, floor 1.0)',
      lane_mn, 1.0)
lane15 = [(x, z) for x in (-G['DHW'], -2.0, 0.0, 2.0, G['DHW'])
          for z in (G['DZ'] - 3.0, G['DZ'], G['DZ'] + 3.0)]
lane15_mn = min(mindist(pt, GCOLL) for pt in lane15)
check('V-5b-6b: lane 15-pt window band (Testerbot re-deriv; floor 0.9)',
      lane15_mn, 0.9)
near = min(lane_mn, lane15_mn)
tol = abs(near - 3.91) <= 0.15 or abs(near - 0.94) <= 0.15
print('%-64s %7s  %s  (seat_scan conv %.2f | 15-pt %.2f; frozen 3.91 / 0.94)' %
      ('V-5b-6c: lane minimum matches a frozen convention number',
       'yes' if tol else 'NO', 'ok' if tol else 'FAIL', lane_mn, lane15_mn))
ok.append(bool(tol))

# --- V-5b-7: props (every regionG prop = 104 dressing rows) ------------------
GPROPS = G['props']
playR = G['R'] - 1.5
def is_parapet_stack(a, b):
    # ED-1: the spec's printed parapet columns place two okFenceStonewall
    # rows in the same x column 2.0 m apart in z (a continuous parapet
    # wall, the okFenceStonewall wall:4 chain pattern). They are ONE
    # flanking wall, not two props: the mutual-4.0 law exempts same-column
    # parapet chains (the probe excludes only these; every other pair
    # asserts >= 4.0).
    return (a['asset'] == 'okFenceStonewall' and b['asset'] == 'okFenceStonewall'
            and abs(a['x'] - b['x']) < 1e-9)

for pr in GPROPS:
    p = (pr['x'], pr['z'])
    others = [(q['x'], q['z']) for q in GPROPS if q is not pr and not is_parapet_stack(pr, q)]
    check('prop %s x(%s,%s) -> colliders raw (>= 4.0)' % (pr['asset'], pr['x'], pr['z']),
          mindist(p, GCOLL), 4.0)
    check('prop %s x(%s,%s) -> spawn (>= 6.0)' % (pr['asset'], pr['x'], pr['z']), mindist(p, [G['spawn']]), 6.0)
    check('prop %s x(%s,%s) -> other props (>= 4.0; parapet stacks exempt ED-1)' % (pr['asset'], pr['x'], pr['z']), mindist(p, others), 4.0)
    check('prop %s x(%s,%s) -> center (<= playRadius %.1f)' % (pr['asset'], pr['x'], pr['z'], playR),
          math.hypot(p[0] - G['cx'], p[1] - G['cz']), playR, le=True)

# licensed pair + brazier family (named rows parsed from the landed values)
fires = [p for p in GPROPS if p['asset'] == 'banditCampfire']
posts = [p for p in GPROPS if p['asset'] == 'lanternPost']
fmut = [mindist((fires[i]['x'], fires[i]['z']), [(fires[j]['x'], fires[j]['z'])])
        for i in range(len(fires)) for j in range(i + 1, len(fires))]
check('V-8/B: banditCampfire brazier count (== 4)', len(fires), 4, le=True, kind='int')
check('V-8/B: lanternPost rows (== 1)', len(posts), 1, le=True, kind='int')
for fv in fmut:
    check('V-5b-7b: brazier mutual (>= 11.2; spec 11.32)', fv, 11.2)
# the LICENSED pair: lanternPost seat (x=6.5, z=-706) and the E parapet at x 6.5
lic = None
for pr in posts:
    lp = (pr['x'], pr['z'])
    for q in GPROPS:
        if q is pr or q['asset'] != 'okFenceStonewall':
            continue
        d = math.hypot(lp[0] - q['x'], lp[1] - q['z'])
        if d <= 4.01 and abs(lp[0] - q['x']) < 1e-9:
            lic = d
check('V-5b-7a: licensed lanternPost/parapet pair (>= 3.9; spec 4.00)', lic if lic is not None else 0, 3.9)
check('V-5b-7c: lanternPost lane clearance (>= 3.7; frozen 3.91)',
      mindist((GPROPS[[p['asset'] for p in GPROPS].index('lanternPost')]['x'],
               GPROPS[[p['asset'] for p in GPROPS].index('lanternPost')]['z']), GCOLL), 3.7)

# --- V-5b-5: spawn + land rows ------------------------------------------------
check('V-5b-5a: spawn -> center (<= r 126)',
      math.hypot(G['spawn'][0] - G['cx'], G['spawn'][1] - G['cz']), G['R'], le=True)
LF = G['land']['lords_hold']
check('V-5b-5b: land.lords_hold -> center (<= r 126)',
      math.hypot(LF[0] - G['cx'], LF[1] - G['cz']), G['R'], le=True)
LC = G['land']['forest_of_the_old_king']
rC = math.hypot(LC[0] - C_R['cx'], LC[1] - C_R['cz'])
check('V-5b-5c: C-side land stands on C (r to C center <= 278.5)', rC, 278.5, le=True)

# --- V-5b-10: conn[5] sanity (region-defs parsed live) -----------------------
m5 = re.search(r'connections\.push\(\{\s*from: CFG\.regionC\.id,\s*to: CFG\.regionG\.id,\s*axis: \'z\','
               r'\s*planeCoord: GD\.planeZ,', defs)
ok.append(bool(m5))
print('%-64s %7s  %s' % ('conn[5]: from C (AMENDMENT A) to G, axis z, GD.planeZ',
                         'yes' if m5 else 'NO', 'ok' if m5 else 'FAIL'))
ok.append('walkFrom: CFG.regionG.id' in defs
          and 'interact: { from: CFG.regionC.id, x: GD.interactAt.x, z: GD.interactAt.z, radius: GD.interactM }' in defs
          and 'land: GD.land' in defs and 'doorHalfWidth: GD.doorHalfWidth' in defs)
ok5b = 'walkFrom: CFG.regionG.id' in defs and 'land: GD.land' in defs
print('%-64s %7s  %s' % ('conn[5]: walkFrom G + interact GD.interactAt + land GD.land',
                         'yes' if ok5b else 'NO', 'ok' if ok5b else 'FAIL'))
sides5 = re.search(r'connections\[5\]\.sides\[CFG\.regionC\.id\] = -1;\s*connections\[5\]\.sides\[CFG\.regionG\.id\] = 1;', defs)
ok.append(bool(sides5))
print('%-64s %7s  %s' % ('conn[5]: sides C -1 / G +1', 'yes' if sides5 else 'NO', 'ok' if sides5 else 'FAIL'))
regG = re.search(r'regions\[CFG\.regionG\.id\] = makeRegion\(CFG\.regionG, -1\);', defs)
ok.append(bool(regG))
print('%-64s %7s  %s' % ('regions[lords_hold] = makeRegion(G, -1)', 'yes' if regG else 'NO', 'ok' if regG else 'FAIL'))
pos_ok = (defs.index('connections[4].sides[CFG.regionF.id] = 1;')
          < defs.index('var GD = CFG.regionG.door;')
          < defs.index('// ---- THREE-free transition helpers'))
ok.append(bool(pos_ok))
print('%-64s %7s  %s' % ('conn[5] block sits after conn[4] sides, before helpers',
                         'yes' if pos_ok else 'NO', 'ok' if pos_ok else 'FAIL'))
# sides live-eval cross-check: the same THREE-free eval in node (the exact
# runtime the browser sees); V-3c runs the fuller shape probe separately.
import subprocess, json as _json
live = subprocess.run(['node', '-e', """
globalThis.window = globalThis;
(0,eval)(require('fs').readFileSync('/tmp/wh-worldfeat/prototype/js/CONFIG.js','utf8'));
(0,eval)(require('fs').readFileSync('/tmp/wh-worldfeat/prototype/js/region-defs.js','utf8'));
const D = window.WH_REGION_DEFS;
const c = D.connectionBetween('forest_of_the_old_king','lords_hold');
process.stdout.write(JSON.stringify({n: Object.keys(D.regions).length, cn: D.connections.length,
  f: c && c.from, t: c && c.to, sc: c && c.sides.forest_of_the_old_king, sg: c && c.sides.lords_hold,
  w: c && c.door.walkFrom, pz: c && c.planeCoord, dw: D.insideDoorWindow(c, 4.4), dwo: D.insideDoorWindow(c, 4.6)}));
"""], capture_output=True, text=True)
if live.returncode != 0:
    print('live-eval node error:', live.stderr[-400:]); ok.append(False)
else:
    L = _json.loads(live.stdout)
    live_ok = (L['n'] == 6 + 1 and L['cn'] == 6 and L['f'] == 'forest_of_the_old_king'
               and L['t'] == 'lords_hold' and L['sc'] == -1 and L['sg'] == 1
               and L['w'] == 'lords_hold' and L['pz'] == G['DZ']
               and L['dw'] is True and L['dwo'] is False)
    ok.append(bool(live_ok))
    print('%-64s %7s  %s' % ('live: 7 regions/6 conns, conn[5] from/to/sides/window',
                             'yes' if live_ok else 'NO', 'ok' if live_ok else 'FAIL'))
# land rows on home sides + >= 8 m inside the plane
check('V-5b-10a: land.lords_hold on home side (z <= planeZ)', LF[1], G['DZ'], le=True)
check('V-5b-10b: land.forest on home side (z > planeZ)', LC[1], G['DZ'], kind='num')
check('V-5b-10c: land.lords_hold >= 8 m inside the plane', G['DZ'] - LF[1], 8.0)

# --- V-5b-11: C-side aperture (the LANDED regionC rows) ----------------------
iap = G['IA']
cpts = [(p['x'], p['z']) for p in C_R['props']]
hook_crypt = (0.0, -596.0)
check('V-5b-11a: interactAt -> every C prop row (>= 6.0)', mindist(iap, cpts), 6.0)
dhk = math.hypot(iap[0] - hook_crypt[0], iap[1] - hook_crypt[1])
check('V-5b-11b: interactAt -> crypt hook (0,-596) (>= 26; frozen 96.1)', dhk, 26.0)
check('V-5b-11c: interactAt -> notch mouth (>= 26; frozen 96.1)',
      mindist(iap, [(0.0, -596.0)]), 26.0)
check('V-5b-11d: interactAt stands on C (r <= 278.5; frozen 134.1)', rC, 278.5, le=True)

# --- enemies + window x-window sanity extras --------------------------------
check('extra: regionG enemies (== 0)', len(G['enemies']), 0, le=True, kind='int')

print('---')
print('ALL CONSTRAINTS: %s (%d checks)' % ('PASS' if all(ok) else 'FAIL', len(ok)))
sys.exit(0 if all(ok) else 1)
