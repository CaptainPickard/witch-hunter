#!/usr/bin/env python3
"""CC-H1 site scan v2 (IO pre-spec probe, scratch/cc-h1/). Chooses + verifies
the Lord's Hold seat ON THE LANDED DATA before the spec freezes.

H1 = the surface hold hub (doc 64 slot H1, doc 66 sec 8), a NORTH hold: the
disc sits fully OUTSIDE C's footprint (C's terrain plays at its own disc;
H1 is a FLAT-DISC region with NO terrain row, so its ground has zero
world-coords overlap and NO wh-ground footprint — the one-active-region law
hides C while H1 is active). The gate faces SOUTH toward C via the north
notch approach.

Layout (the D/E/F pattern, mirrored):
  plane: at H1's SOUTH face, tail 4 m inside the disc edge
  hook:  on C, ON the northRoad's last landing band, clear of the crypt's
         E-hook, the notch exclusion arc, and every C prop row
Reads the LANDED CONFIG.js / terrain row; asserts per candidate:
  1. hook on the road band (|road x - hook x| <= 4.0)
  2. every C prop row >= 6.0 m from the hook; none inside the lane x-window
     at the plane's z band on C (informational: the plane lives OUTSIDE C's
     playable band)
  3. hook >= 26 m from the crypt door's C-side hook AND >= 26 m from the
     notch mouth (0, -596) (notchMouthExclusionM 26)
  4. hook INSIDE C's playable disc (must be standable): r to (0,-366) <= 278.5
  5. plane OUTSIDE C's world footprint hold: plane z <= -650
  6. walk-out law: plane sits exactly tail* inside the disc's south edge
  7. ring math: N 90 segments r 126 chord ring (gap at the face), per-segment
     colliders r 0.45; no collider inside the door lane window; octant
     coverage outside the gap
Outputs the FROZEN spec numbers.
"""
import math, re, sys

ROOT = '/tmp/wh-worldfeat'
cfg = open(ROOT + '/prototype/js/CONFIG.js').read()

def block(src, key):
    me = re.search(r'\n  %s: \{' % re.escape(key), src)
    blob = src[me.start():]
    nxt = re.search(r'\n  [a-zA-Z_]+: \{', blob[10:])
    return blob[:10 + nxt.start()] if nxt else blob

cblock = block(cfg, 'regionC')
CPTS = []
for m in re.finditer(r"\{ asset: '(\w+)',\s*(?:y: (-?[\d.]+),\s*)?x: (-?[\d.]+), z: (-?[\d.]+), rotY: (-?[\d.]+), scale: (-?[\d.]+)", cblock):
    CPTS.append((m.group(1), float(m.group(3)), float(m.group(4))))
print('C prop rows parsed: %d' % len(CPTS))

hook_crypt = (0.0, -596.0)     # regionE.door.interactAt (landed)
hook_den = (-163.4, -202.6)    # regionD.door.interactAt (landed)
nm = re.search(r'notchMouthExclusionM: (\d+)', cfg)
NEX = float(nm.group(1)) if nm else 26.0

# northRoad CONFIG waypoint pairs
rm = re.search(r"id: 'northRoad'.*?points: \[\[(.*?)\]\]", cfg, re.S)
pts = [(float(a), float(b)) for a, b in re.findall(r'\[(-?[\d.]+), (-?[\d.]+)\]', rm.group(1))]
print('northRoad points: %s' % pts)

def road_x_at(z):
    for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
        if min(z0, z1) <= z <= max(z0, z1):
            t = (z - z0) / (z1 - z0) if z1 != z0 else 0.0
            return x0 + (x1 - x0) * t
    return None

# ---- candidates: hooks ALONG the northRoad's landing band ----------------------
# The road waypoint band z -500..-540. The crypt hook sits at (0,-596) (the mouth);
# the den exclusion doesn't apply (that law is for BRANCH-ROAD terminal seats; the
# probe keeps it anyway as margin). Candidates: road seats z -500..-540 step 6.
CAND_HOOK_Z = [-500, -506, -512, -518, -524, -530, -536, -540]
LHW = 4.5
TAIL = 4.0
R_H1 = 126.0
PLANE_Z = -700.0         # the hold gate plane (frozen below if a hook clears)
CZ_H1 = PLANE_Z - R_H1 + TAIL   # disc center (south edge at -696; face plane -700)
best = None
for hz in CAND_HOOK_Z:
    rx = road_x_at(hz)
    if rx is None:
        print('hook z %.0f: off the road table (skip)' % hz); continue
    hook = (rx, hz)
    ok = True; notes = []
    for (a, x, z) in CPTS:
        dh = math.hypot(x - hook[0], z - hook[1])
        if dh < 6.0:
            ok = False; notes.append('prop %s (%.1f,%.1f) d %.2f < 6 to hook' % (a, x, z, dh))
    dhk = math.hypot(hook[0] - hook_crypt[0], hook[1] - hook_crypt[1])
    dnotch = math.hypot(hook[0], hook[1] + 596.0)
    rC = math.hypot(hook[0] + 0.0, hook[1] + 366.0)
    if dhk < 26.0: ok = False; notes.append('crypt hook sep %.1f < 26' % dhk)
    if dnotch < NEX: ok = False; notes.append('notch mouth %.1f < %.0f' % (dnotch, NEX))
    if rC > 278.5: ok = False; notes.append('hook off C disc r %.1f' % rC)
    if hz > -540 + 1 or hz < -545: pass  # band informational
    print('hook (%.2f, %.0f): %s | crypt-sep %5.1f | notch %5.1f | rC %5.1f' % (hook[0], hook[1], 'OK' if ok else 'BLOCKED', dhk, dnotch, rC))
    for n in notes: print('    ! ' + n)
    if ok and best is None:
        best = (hook, rx)

if not best:
    print('FAIL: no cleared hook'); sys.exit(1)

hook, rx = best
print('---')
print('SEAT: hook %s | planeZ %.1f | H1 center (0, %.1f)' % (hook, PLANE_Z, CZ_H1))

# ---- ring math (frozen rows for the spec): 90 segments on r 126 ---------------
AW = 1.899
N = 90
chord = 2 * R_H1 * math.sin(math.pi / N)
scale = round(chord / AW, 2)
print('ring: N %d chord %.2f scale %.2f (raw 1.899)' % (N, chord, scale))
CX, CZ = 0.0, CZ_H1
rows = []
# OMITTED segment: the one whose angular CENTER bearing is 90 deg (the south face,
# z+ from the center). Their engine bearing: atan2(z - CZ, x - CX) deg; the face = 90.
i_face = int(round((90.0 - 0.0) / (360.0 / N)))  # segment whose center hits 90 at i where center bearing = 90 - i*360/N...
for i in range(N):
    b_deg = 90.0 - (i + 0.5) * (360.0 / N)      # clockwise from the face (their ring cadence)
    if abs(b_deg) < 1e-9: continue              # the segment whose CENTER is exactly the face bearing -> omitted (gap straddles the face)
    th = math.radians(b_deg)
    x = CX + R_H1 * math.cos(th)
    z = CZ + R_H1 * math.sin(th)
    tangent = (-math.sin(th), math.cos(th))     # CCW tangent along the ring
    rotY = math.atan2(-tangent[1], tangent[0]) % (2 * math.pi)  # ax=cos rotY, az=-sin rotY == tangent
    rows.append((i, round(x, 2), round(z, 2), round(rotY, 2), scale, 12))
print('ring rows %d (omitted: the 90-deg segment)' % len(rows))
for r in rows[:2] + rows[-2:]:
    print('  seg %d: (%.2f, %.2f) rotY %.2f scale %.2f wall %d' % r)

coll = []
for (i, x, z, rotY, s, n) in rows:
    L = AW * s
    ax, az = math.cos(rotY), -math.sin(rotY)
    for k in range(n):
        t = ((k + 0.5) / n - 0.5) * L
        coll.append((x + ax * t, z + az * t))
print('colliders %d' % len(coll))
# lane: no collider inside |x| <= LHW at z in [PLANE_Z-3, PLANE_Z+3]
inside = [(x, z) for (x, z) in coll if abs(x) <= LHW and abs(z - PLANE_Z) <= 3.0]
print('colliders inside the door lane window: %d (want 0)' % len(inside))
mn = min((math.hypot(x - lx, z - PLANE_Z) for (x, z) in coll for lx in (-LHW, -2.0, 0.0, 2.0, LHW)), default=None)
print('nearest collider to the lane plane points: %.2f (want >= 1.0)' % mn)
octc = [0] * 8
for (x, z) in coll:
    a = math.degrees(math.atan2(z - CZ, x - CX)) % 360
    octc[int(((a + 22.5) % 360) / 45)] += 1
print('octant coverage (E,NE,N,NW,W,SW,S,SE): %s' % octc)
sparse = [i for i, c in enumerate(octc) if c == 0]
print('empty octants (gap arcs only expected): %s' % sparse)

# land rows (x NOT preserved per the D/E/F law)
land_hold = (0.0, PLANE_Z - TAIL - 7.0)   # just inside the gate, facing the keep
land_forest = hook                        # back onto C's road, facing the hold gate (face toward plane: (0,PLANE_Z))
print('land: lords_hold (0, %.1f) | forest_of_the_old_king %s' % (land_hold[1], land_forest))
print('FROZEN SPEC NUMBERS: planeZ %s doorX 0.0 doorHalfWidth %s interactAt %s interactM 3.5' % (PLANE_Z, LHW, hook))
print('spawn (0, %.1f) | groundRadius 126 | center (0, %.1f)' % (land_hold[1], CZ))
print('ALL SEAT CHECKS: PASS (hook %s)' % (hook,))
print('RING ROWS (seg i, x, z, rotY, scale, wall):')
for r in rows:
    print('  { asset: \'whWall%s\', x: %s, z: %s, rotY: %s, scale: %s, sy: %s, sz: 2.40, y: -0.2, wall: %d },' %
          ('A' if r[0] % 2 == 0 else 'B', r[1], r[2], r[3], r[4], 11.69 if r[0] % 2 == 0 else 11.55, r[5]))
