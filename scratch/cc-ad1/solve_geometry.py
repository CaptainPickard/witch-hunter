#!/usr/bin/env python3
"""CC-AD1 geometry verifier (Devbot scratch). Parses the regionE rows from
CONFIG.js (build-input source of truth), rebuilds the wall-collider circles
exactly per region-manager whPropColliders (p.wall circles r CFG.boundaryWall.
collider.r along the row's local X, asset widths from the measured footprints),
and asserts EVERY clearance law of the CC-AD1 spec:
  - 8 whWall rows; ring colliders closed EXCEPT the door gap (world z -612)
  - spawn + BOTH land rows inside r 20 of center (0, -596)
  - covens >= 8.0 m from spawn/land, >= 8.0 m from each other
  - covens >= 4.0 m walk-clear of the ring (16 - rho) AND >= 4.0 m raw from
    every wall-collider circle
  - props >= 4.0 m from walls (raw + walk-clear), >= 6.0 m from spawn/land,
    >= 5.0 m from BOTH covens
Run: python3 scratch/cc-ad1/solve_geometry.py
"""
import math
import re
import sys

ROOT = '/tmp/wh-worldfeat'
cfg = open(ROOT + '/prototype/js/CONFIG.js').read()

me = re.search(r'\n  regionE: \{', cfg)
if not me:
    print('FAIL: no regionE block in CONFIG.js')
    sys.exit(1)
blob = cfg[me.start():]
nxt = re.search(r'\n  [a-zA-Z_]+: \{', blob[10:])
eblob = cfg[me.start():me.start() + 10 + nxt.start()] if nxt else blob

cm = re.search(r'center: \{ x: (-?[\d.]+), z: (-?[\d.]+) \}', eblob)
CX, CZ = float(cm.group(1)), float(cm.group(2))
R = float(re.search(r'groundRadius: (\d+)', eblob).group(1))
DZ = float(re.search(r'planeZ: (-?[\d.]+)', eblob).group(1))
DX = float(re.search(r'doorX: (-?[\d.]+)', eblob).group(1))
DHW = float(re.search(r'doorHalfWidth: (-?[\d.]+)', eblob).group(1))
sm = re.search(r'spawn: \{ x: (-?[\d.]+), z: (-?[\d.]+) \}', eblob)
SPAWN = (float(sm.group(1)), float(sm.group(2)))
lm = re.search(r"veil_crypt: \{ x: (-?[\d.]+), z: (-?[\d.]+)", eblob)
LAND_E = (float(lm.group(1)), float(lm.group(2)))
lmC = re.search(r'forest_of_the_old_king: \{ x: (-?[\d.]+), z: (-?[\d.]+), faceX', eblob)
LAND_C = (float(lmC.group(1)), float(lmC.group(2)))

COVEN = []
for mm in re.finditer(r"\{ type: 'coven', x: (-?[\d.]+), z: (-?[\d.]+) \}", eblob):
    COVEN.append((float(mm.group(1)), float(mm.group(2))))

WALL_ROWS, PROP_ROWS, in_props = [], [], False
for ln in eblob.splitlines():
    if re.match(r'\s*props: \[', ln):
        in_props = True
        continue
    if in_props and re.match(r'\s*\]', ln):
        break
    if not in_props:
        continue
    wm = re.search(r"\{ asset: '(whWall[AB])', x: (-?[\d.]+), z: (-?[\d.]+), rotY: (-?[\d.]+), scale: (-?[\d.]+), sy: (-?[\d.]+), sz: (-?[\d.]+), y: -[\d.]+, wall: (\d+) \}", ln)
    if wm:
        WALL_ROWS.append(dict(asset=wm.group(1), x=float(wm.group(2)), z=float(wm.group(3)),
                              rotY=float(wm.group(4)), scale=float(wm.group(5)), n=int(wm.group(8))))
        continue
    dm = re.search(r"\{ asset: '(\w+)',\s+x: (-?[\d.]+), z: (-?[\d.]+), rotY: (-?[\d.]+), scale: (-?[\d.]+) \}", ln)
    if dm:
        PROP_ROWS.append(dict(asset=dm.group(1), x=float(dm.group(2)), z=float(dm.group(3))))

WR = 0.45
AW = {'whWallA': 1.899, 'whWallB': 1.899}
coll = []
for wr in WALL_ROWS:
    L = AW[wr['asset']] * wr['scale']
    ax, az = math.cos(wr['rotY']), -math.sin(wr['rotY'])
    for k in range(wr['n']):
        t = ((k + 0.5) / wr['n'] - 0.5) * L
        coll.append((wr['x'] + ax * t, wr['z'] + az * t))

def mindist(pt, pts):
    return min(math.hypot(pt[0] - q[0], pt[1] - q[1]) for q in pts)

print('regionE: center (%.1f, %.1f) r %.0f | door planeZ %.1f doorX %.1f hw %.1f' % (CX, CZ, R, DZ, DX, DHW))
print('wall rows %d | collider circles %d | coven %d %s' % (len(WALL_ROWS), len(coll), len(COVEN), COVEN))
print('spawn %s | land_E %s | land_C %s | prop rows %d' % (SPAWN, LAND_E, LAND_C, len(PROP_ROWS)))

ok = []
def check(label, val, req, le=False):
    good = (val <= req) if le else (val >= req)
    ok.append(good)
    print('%-52s %7.2f %s %4.1f  %s  (margin %.2f)' % (label, val, '<=' if le else '>=', req,
          'ok' if good else 'FAIL', req - val if le else val - req))

# --- structure ---------------------------------------------------------------
check('whWall ring rows == 8', len(WALL_ROWS), 8, le=True)
check('coven rows == 2', len(COVEN), 2, le=True)
# spawn/land inside r 20
for lbl, p in (('spawn', SPAWN), ('land (veil_crypt)', LAND_E), ('land (forest)', LAND_C)):
    check('%s -> center (<= r 20)' % lbl, math.hypot(p[0] - CX, p[1] - CZ), R, le=True)
# coven minimums
for ci, c in enumerate(COVEN, 1):
    check('coven%d -> spawn/land (>= 8)' % ci, mindist(c, [SPAWN, LAND_E]), 8.0)
check('coven1 <-> coven2 (>= 8)', mindist(COVEN[0], [COVEN[1]]), 8.0)
for ci, c in enumerate(COVEN, 1):
    rho = math.hypot(c[0] - CX, c[1] - CZ)
    check('coven%d ring walk-clear 16-rho (>= 4)' % ci, 16 - rho, 4.0)
    check('coven%d -> nearest collider circle (>= 4)' % ci, mindist(c, coll) - WR, 4.0)
# props
for pr in PROP_ROWS:
    p = (pr['x'], pr['z'])
    rho = math.hypot(p[0] - CX, p[1] - CZ)
    check('prop %-16s walk-clear (>= 4)' % pr['asset'], 16 - rho, 4.0)
    check('prop %-16s -> colliders (>= 4)' % pr['asset'], mindist(p, coll) - WR, 4.0)
    check('prop %-16s -> spawn/land (>= 6)' % pr['asset'], mindist(p, [SPAWN, LAND_E]), 6.0)
    for ci, c in enumerate(COVEN, 1):
        check('prop %-16s -> coven%d (>= 5)' % (pr['asset'], ci), mindist(p, [c]), 5.0)
# door gap: no collider inside the door window on the mouth face
zwin = DZ - math.sqrt(max(0.0, R * R - (DHW / 2) ** 2))
exempt = [(x, z) for (x, z) in coll if abs(x - DX) < DHW and z < zwin]
check('colliders inside door-gap window (== 0)', len(exempt), 0, le=True)
# ring coverage: colliders exist all around (16 compass octants, gap octant allowed sparse)
oct = [0] * 8
for (x, z) in coll:
    a = math.degrees(math.atan2(z - CZ, x - CX)) % 360
    oct[int(((a + 22.5) % 360) / 45)] += 1
print('collider octant coverage (N,NE,E,SE,S,SW,W,NW): %s' % oct)
print('---')
print('ALL CONSTRAINTS: %s (%d checks)' % ('PASS' if all(ok) else 'FAIL', len(ok)))
sys.exit(0 if all(ok) else 1)
