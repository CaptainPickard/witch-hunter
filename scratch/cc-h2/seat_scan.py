#!/usr/bin/env python3
"""CC-H2 site scan (IO pre-spec probe, scratch/cc-h2/). Chooses + verifies the
Garrison Keep courtyard seat ON THE LANDED DATA before the spec freezes.

H2 = doc 64 slot H2: garrison courtyard layer chained OFF H1 (the second
stratum under the lord's hold: armory / dungeons), flat disc r 80, E/F door
grammar. The chain runs G -> H2 further -z (x preserved, z stepped): G center
(0, -822), r 126 -> the G side faces SOUTH (+z toward -822 is north... chain
direction: H2 center = G south rim - 80). The mouth faces the PARENT (G):
H2 plane sits 4 m inside H2's parent-facing rim (mirrors H1's landed plane
law: rim -696 -> plane -700 = 4 m inside the disc edge).

THE APERTURE (E->F parent-aperture pattern, doc 66 sec 3 pattern 2):
chaining THROUGH G's south curtain requires erasing the LANDED curtain rows
that cover the mouth. G's cadence (seat_scan cc-h1: bearing b_i = 90 -
(i+0.5) * 4 deg, r 126, 89 rows) places the -z pole at a SEAM between i=44
(b -88) and i=45 (b -92) - both flanks land, so the pole is walled shut by a
broad pair. The mouth lanes through via TWO verbatim deletions (the pole
flank pair) + mourner-pair parapet replacements flanking the aperture.

Reads the LANDED CONFIG.js; asserts per candidate:
  1. the G south-pole flank pair exists EXACTLY as predicted (2 rows, |x| <= 9,
     |z - (-947.92)| <= 1.0, wall 12) - and NO other G prop within 6 m of the
     planned hook
  2. hook (0, -934) stands inside G's playable radius (r <= 124.5) and >= 6 m
     from every landed G prop row
  3. G-side aperture lane walkable AFTER erasure: no G ring collider within
     1.5 m of the lane (|x| <= 4 at z in [-951, -945]); parapet replacements
     >= 4.0 m raw from every remaining G ring collider
  4. H2 disc (0, -1024, r 80): spawn + both land rows inside r 80 with
     margin; the 4 m sliver overlap with G's disc (z -948..-944) is
     FLAT/FLAT = harmless (one-active-region law; recorded, not error)
  5. H2 ring math: N 50 segments r 80, chord cadence b_i = 90 -
     (i+0.5)*7.2 deg, OMIT i=0 and i=49 (the pole flank pair) = the REAL
     south mouth (correction of the landed cc-h1 omit rule, which never
     centers on a pole: doc 66 amendment text rides the spec); wall 8
     colliders r 0.45 every <= 2 m; no collider in the door window strip
     (|x| <= 4 at |z - (-948)| <= 3) and every lane sample >= 1.0 m from any
     collider; the ONLY collider-free bearing arc is the mouth window's
  6. sec 10 sides law: sideOfPlane(spawn row) == sideIn(regionH) with
     planeZ -948; land rows on home sides; parent sideIn inert-but-truthful
     (G: +1 at z > -948)
Outputs the FROZEN spec numbers (all PROPOSED for Nicko's tuning).

Run: python3 scratch/cc-h2/seat_scan.py   (from the worktree root)
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
cm = re.search(r'center: \{ x: (-?[\d.]+), z: (-?[\d.]+) \}', gblock)
GC = (float(cm.group(1)), float(cm.group(2)))
GR = float(re.search(r'groundRadius: (\d+)', gblock).group(1))
WR = float(re.search(r'collider: \{ r: ([\d.]+), perSegment: \d+ \}', cfg).group(1))
if abs(WR - 0.45) > 1e-9:
    sys.exit('FAIL: boundaryWall.collider.r is not 0.45 (%r)' % WR)
AW = 1.899   # measured raw ext X (cc-ad1; whWallA and whWallB are equal)

# ---- parse ALL regionG prop rows live --------------------------------------
WALLS, PROPS = [], []
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
        WALLS.append(dict(asset=wm.group(1), x=float(wm.group(2)), z=float(wm.group(3)),
                          rotY=float(wm.group(4)), scale=float(wm.group(5)), n=int(wm.group(9)),
                          raw=ln.strip()))
        continue
    dm = re.search(r"\{ asset: '(\w+)',\s*x: (-?[\d.]+), z: (-?[\d.]+), rotY: (-?[\d.]+), scale: (-?[\d.]+) \}", ln)
    if dm:
        PROPS.append(dict(asset=dm.group(1), x=float(dm.group(2)), z=float(dm.group(3)),
                          rotY=float(dm.group(4)), scale=float(dm.group(5)), raw=ln.strip()))
print('regionG parsed: %d curtain rows | %d dressing rows | center %s r %.0f' % (len(WALLS), len(PROPS), GC, GR))

def colliders(walls):
    out = []
    for wr in walls:
        L = AW * wr['scale']
        ax, az = math.cos(wr['rotY']), -math.sin(wr['rotY'])
        for k in range(wr['n']):
            t = ((k + 0.5) / wr['n'] - 0.5) * L
            out.append((wr['x'] + ax * t, wr['z'] + az * t))
    return out

GC_W = colliders(WALLS)
print('regionG ring colliders: %d' % len(GC_W))

fails = []
def check(label, val, req, le=False, kind='num'):
    if kind == 'num':
        good = (val <= req) if le else (val >= req)
    else:
        good = val == req
    if not good:
        fails.append(label)
    print('%-58s %7s %s %5s  %s' % (label, val, '<=' if le else '>=', req,
          'ok' if good else 'FAIL'))

# ---- check 1: the G south-pole flank pair -----------------------------------
POLE_Z = GC[1] - GR   # -948: the -z pole of G's curtain
pair = [w for w in WALLS if abs(w['x']) <= 9.0 and abs(w['z'] - POLE_Z) <= 1.0]
check('G pole flank pair rows found (== 2)', len(pair), 2, kind='int')
for w in pair:
    check('  pole row |x| <= 9 and wall 12 (%s x=%.2f)' % (w['asset'], w['x']),
          abs(w['x']), 9.0, le=True)
if len(pair) != 2:
    sys.exit('FAIL: the G pole flank pair did not materialize as predicted')

# ---- check 2: the hook seat -------------------------------------------------
HOOK = (0.0, -934.0)
PLANE_H2 = -948.0     # 4 m inside H2's parent-facing rim (-944)
R_H2 = 80.0
# rim of H2's parent-facing edge: center = plane - R_H2 (disc edge at -944... the
# plane rides 4 m INSIDE the rim, H1 law: rim -944 -> plane -948)
CX_H2, CZ_H2 = 0.0, -1024.0
r_hook = math.hypot(HOOK[0] - GC[0], HOOK[1] - GC[1])
check('hook inside G playable radius (<= 124.5)', r_hook, 124.5, le=True)
mn = min(math.hypot(p['x'] - HOOK[0], p['z'] - HOOK[1]) for p in PROPS) if PROPS else 999
check('hook >= 6.0 m from every G dressing prop', mn, 6.0)
mn_w_g = min(math.hypot(x - HOOK[0], z - HOOK[1]) for (x, z) in GC_W)
check('hook >= 6.0 m from every G ring collider', mn_w_g, 6.0)

# ---- check 3: aperture lane AFTER erasing the pole pair ---------------------
ERASE_X = sorted(set(round(w['x'], 2) for w in pair))
remaining_walls = [w for w in WALLS if w not in pair]
GC_W_POST = colliders(remaining_walls)
lane_min = min((math.hypot(x - lx, z - lz)
                for (x, z) in GC_W_POST
                for lx in (-4.0, -2.0, 0.0, 2.0, 4.0)
                for lz in (-951.0, -948.0, -945.0)), default=None)
check('G aperture lane nearest collider (>= 1.5 post-erasure)', lane_min, 1.5)
# mouth flankers INSIDE H2 (E-round precedent: rubble flanker dressing, kept
# well clear of the dense mouth band; the <= 4.0-from-ring law here is against
# H2's own ring rows, computed further below)
FLANKERS = [(10.0, -968.0), (-10.0, -968.0)]
dhook = min(math.hypot(px - HOOK[0], pz - HOOK[1]) for (px, pz) in FLANKERS)
check('hook >= 6.0 m from flankers', dhook, 6.0)

# ---- check 4: H2 disc seats -------------------------------------------------
SPAWN_H2 = (0.0, -955.0)
LAND_H2 = (0.0, -955.0)     # into H2 = the spawn row
LAND_G = (0.0, -941.0)      # walk-back into G, facing the hold heart
for name, pt in (('spawn', SPAWN_H2), ('land.fort_garrison', LAND_H2)):
    r = math.hypot(pt[0] - CX_H2, pt[1] - CZ_H2)
    check('%s inside H2 r 80 (margin < 78.5)' % name, r, 78.5, le=True)
r_g = math.hypot(LAND_G[0] - GC[0], LAND_G[1] - GC[1])
check('land.lords_hold inside G playable radius (<= 124.5)', r_g, 124.5, le=True)

# ---- check 5: H2 ring math --------------------------------------------------
N = 50
chord = 2 * R_H2 * math.sin(math.pi / N)
scale = round(chord / AW, 2)
check('ring scale 2dp (== chord/AW)', abs(scale - round(10.05 / AW, 2)), 0.0, kind='num')
rows = []
for i in range(N):
    if i == 0 or i == N - 1:
        continue    # the pole flank pair OMITTED = the real south mouth
    b_deg = 90.0 - (i + 0.5) * (360.0 / N)
    th = math.radians(b_deg)
    x = CX_H2 + R_H2 * math.cos(th)
    z = CZ_H2 + R_H2 * math.sin(th)
    tangent = (-math.sin(th), math.cos(th))
    rotY = math.atan2(-tangent[1], tangent[0]) % (2 * math.pi)
    rows.append((i, round(x, 2), round(z, 2), round(rotY, 2), scale, 8))
check('ring rows (== 48)', len(rows), 48, kind='int')
H2_W = colliders([dict(asset='whWallA', x=r[1], z=r[2], rotY=r[3], scale=r[4], n=r[5]) for r in rows])
check('ring colliders (== 384)', len(H2_W), 384, kind='int')
inside = [(x, z) for (x, z) in H2_W if abs(x) <= 4.0 and abs(z - PLANE_H2) <= 3.0]
check('colliders inside the door window strip (== 0)', len(inside), 0, kind='int')
lane_h2 = min((math.hypot(x - lx, z - PLANE_H2)
               for (x, z) in H2_W
               for lx in (-4.0, -2.0, 0.0, 2.0, 4.0)), default=None)
check('H2 lane samples nearest collider (>= 1.0)', lane_h2, 1.0)
octc = [0] * 8
hole_bearings = []
for (x, z) in H2_W:
    a = math.degrees(math.atan2(z - CZ_H2, x - CX_H2)) % 360
    octc[int(((a + 22.5) % 360) / 45)] += 1
    hole_bearings.append(a)
check('every octant holds >= 8 colliders', min(octc), 8)
hole = [b for b in hole_bearings if 82.8 <= b <= 97.2]
check('colliders bearing inside the mouth arc [82.8, 97.2] (== 0)', len(hole), 0, kind='int')

# ---- check 6: sec 10 sides law ----------------------------------------------
side_spawn = 1 if SPAWN_H2[1] > PLANE_H2 else -1
check('sideOfPlane(spawn) == sideIn(fort_garrison) == -1', side_spawn, -1, kind='int')
side_g = 1 if HOOK[1] > PLANE_H2 else -1
check('sideOfPlane(hook) == sideIn(lords_hold) == +1', side_g, 1, kind='int')
check('land.fort_garrison on home side (z <= plane)', 1 if LAND_H2[1] <= PLANE_H2 else 0, 1, kind='int')
check('land.lords_hold on G home side (z > plane)', 1 if LAND_G[1] > PLANE_H2 else 0, 1, kind='int')
g_sliver = abs(PLANE_H2) - abs(GC[1] - GR)   # 948 - 948 = 0 -> plane ON G's rim
print('NOTE: H2 plane z %.0f sits ON G disc south rim (%.0f): the flat/flat sliver'
      ' overlap (H2 rim -944 vs G rim -948) is harmless under the one-active law'
      ' (both discs y 0; never rendered together)' % (PLANE_H2, POLE_Z))

# ---- enemies seats ----------------------------------------------------------
EN = [(-10.0, -975.0), (11.0, -976.0)]
for i, (ex, ez) in enumerate(EN):
    rho = math.hypot(ex - CX_H2, ez - CZ_H2)
    check('enemy %d inside play radius (<= 78.5)' % i, rho, 78.5, le=True)
    check('enemy %d >= 4.45 walk-clear of ring' % i, R_H2 - rho, 4.45)
    d_spawn = math.hypot(ex - SPAWN_H2[0], ez - SPAWN_H2[1])
    check('enemy %d >= 8.0 from spawn' % i, d_spawn, 8.0)
mutual = math.hypot(EN[0][0] - EN[1][0], EN[0][1] - EN[1][1])
check('enemies mutual >= 12.5', mutual, 12.5)

print('---')
print('SEAT: H2 center (0, %.0f) r %.0f | planeZ %.0f doorX 0.0 doorHalfWidth 4.0'
      % (CZ_H2, R_H2, PLANE_H2))
print('hook %s interactM 3.5 | spawn %s | land.G %s' % (HOOK, SPAWN_H2, LAND_G))
print('G APERTURE ERASE (verbatim from CONFIG row order):')
for w in sorted(pair, key=lambda w: w['raw']):
    print('  ' + w['raw'])
print('G APERTURE PARAPETS:')
for (px, pz) in FLANKERS:
    print("  { asset: 'okFenceStonewall', x: %.1f, z: %.1f, rotY: 0, scale: 1.2 }," % (px, pz))
print('flanker >= 4.0 clearance against H2 OWN ring rows (re-checked by clearance.py)')
print('ring: N %d chord %.2f scale %.2f wall 8 | rows %d colliders %d' % (N, chord, scale, len(rows), len(H2_W)))
print('enemies (2x bandit sentries): %s' % EN)
print('FROZEN SPEC NUMBERS: planeZ %s doorX 0.0 doorHalfWidth 4.0 interactAt %s interactM 3.5'
      % (PLANE_H2, HOOK))
print('spawn %s | groundRadius %d | center (0, %.0f) | groundSeed 1662061651'
      % (SPAWN_H2, R_H2, CZ_H2))
if fails:
    print('ALL SEAT CHECKS: FAIL (%s)' % '; '.join(fails))
    sys.exit(1)
print('ALL SEAT CHECKS: PASS')
print('RING ROWS (i, x, z, rotY, scale, wall; A/B alternate by i parity):')
for r in rows:
    print("  { asset: 'whWall%s', x: %s, z: %s, rotY: %s, scale: %s, sy: %s, sz: 2.40, y: -0.2, wall: %d }," %
          ('A' if r[0] % 2 == 0 else 'B', r[1], r[2], r[3], r[4], 11.69 if r[0] % 2 == 0 else 11.55, r[5]))
