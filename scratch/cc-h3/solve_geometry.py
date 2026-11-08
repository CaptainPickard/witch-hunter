#!/usr/bin/env python3
"""CC-H3 live CONFIG/region-defs geometry audit. Run from worktree root.

Seats, walls, door, and connection are evaluated from the JS source, not copied
from the spec. Wall width and prop footprints are measured asset widths (X)
from the GLBs; collider radii follow region-manager whPropColliders.
"""
import collections
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
JS = r"""
const fs = require('fs');
global.window = {};
eval(fs.readFileSync('prototype/js/CONFIG.js', 'utf8'));
eval(fs.readFileSync('prototype/js/region-defs.js', 'utf8'));
const C = window.WH_CONFIG, D = window.WH_REGION_DEFS;
const conn = D.connections[8];
console.log(JSON.stringify({J:C.regionJ,F:C.regionF,wall:C.boundaryWall.collider,
  c:conn, count:D.connections.length,
  forward:D.connectionBetween(C.regionF.id,C.regionJ.id)===conn,
  reverse:D.connectionBetween(C.regionJ.id,C.regionF.id)===conn,
  sideIn:D.sideIn(conn,C.regionJ.id),
  sideOfPlane:D.sideOfPlane(conn,C.regionJ.spawn.z),
  planeInF:D.planeIn(conn,C.regionF.id),
  planeInJ:D.planeIn(conn,C.regionJ.id)}));
"""
try:
    data = json.loads(subprocess.check_output(['node', '-e', JS], cwd=ROOT, text=True))
except (subprocess.CalledProcessError, ValueError, OSError) as exc:
    sys.exit('FAIL loading live CONFIG/region-defs: %s' % exc)
J, F, c = data['J'], data['F'], data['c']
failures = []
checks = 0


def check(label, passed, detail=''):
    global checks
    checks += 1
    if not passed:
        failures.append(label)
    print('%s: %s %s' % (label, 'PASS' if passed else 'FAIL', detail))


def floor(label, value, limit):
    check(label, value + 1e-8 >= limit, '%.4f >= %.4f' % (value, limit))


def point(row):
    return (row['x'], row['z'])


def distance(a, b):
    return math.dist(a, b)


def rings(region):
    return [p for p in region['props'] if p['asset'] in ('whWallA', 'whWallB')]


# Measured raw GLB X extents; region-manager uses width*scale/2 for non-tree
# props. The wall widths are the cc-ad1/cc-h2 lineage's 1.899-m footprint.
WIDTH = {'whWallA': 1.899, 'whWallB': 1.899,
         'mourningStatue': 1.862, 'stoneSteps': 1.94825,
         'okRuinColumn': 0.957085, 'blightcap': 1.692074,
         'lanternPost': 0.585384, 'skullPile': 2.0,
         'mossBoulder': 1.897361}
WR = data['wall']['r']


def colliders(region):
    result = []
    for row in rings(region):
        length = WIDTH[row['asset']] * row['scale']
        ax, az = math.cos(row['rotY']), -math.sin(row['rotY'])
        for k in range(row['wall']):
            t = ((k + 0.5) / row['wall'] - 0.5) * length
            result.append((row['x'] + ax*t, row['z'] + az*t, WR, row))
    return result


def nearest(p, circles, edge=True):
    return min(distance(p, (x, z)) - (r if edge else 0) for x, z, r, _ in circles)


jw, fw = colliders(J), colliders(F)
jrows = [p for p in J['props'] if p not in rings(J)]
frows = [p for p in F['props'] if p not in rings(F)]
jc, fc = point(J['center']), point(F['center'])
seat, landj = point(J['spawn']), point(J['door']['land'][J['id']])
landf = point(J['door']['land'][F['id']])
hook = point(J['door']['interact'])
ghouls = [point(e) for e in J['enemies']]
fghouls = [point(e) for e in F['enemies']]

# Conn is the evaluated source object, including the engine helpers.
check('conn[8] lookup and endpoints', data['count'] == 9 and data['forward'] and data['reverse']
      and c['from'] == F['id'] and c['to'] == J['id'] and c['axis'] == 'z')
check('conn[8] walkFrom/interact/land/plane', c['planeCoord'] == J['door']['planeZ']
      and c['door']['walkFrom'] == J['id'] and c['door']['interact']['from'] == F['id']
      and c['door']['interact']['x'] == hook[0] and c['door']['interact']['z'] == hook[1]
      and c['door']['interact']['radius'] == J['door']['interact']['radius']
      and c['door']['land'] == J['door']['land'])
check('conn[8] sides/planeIn', c['sides'][F['id']] == -1
      and c['sides'][J['id']] == data['sideIn'] == data['sideOfPlane'] == 1
      and not data['planeInF'] and data['planeInJ'])
check('J ring 10 rows / 90 colliders', len(rings(J)) == 10 and len(jw) == 90,
      '%d rows / %d circles, radius %.3f' % (len(rings(J)), len(jw), WR))
check('J ring segment dimensions', all(w['wall'] == 9 and w['scale'] == 13.019
      and w['sy'] == (11.69 if w['asset'] == 'whWallA' else 11.55)
      and w['sz'] == 2.4 and w['y'] == -0.2 for w in rings(J)))
check('J ring radius and bearings', all(abs(distance(point(w), jc) - J['groundRadius']) <= 0.05
      and abs(math.atan2(w['x'] - jc[0], w['z'] - jc[1]) % (2*math.pi)
              - k*2*math.pi/len(rings(J))) < 0.002
      for k, w in enumerate(rings(J))), 'diameter %.1f' % (2*J['groundRadius']))
check('J row counts', len(jrows) == 15 and len(ghouls) == 2)
check('J spawn = J land', seat == landj)

# A continuous door lane: minimum distance to the x interval at planeZ,
# subtract collider radius; zero overlap for expanded +/-0.5-m window.
plane, half, doorx = J['door']['planeZ'], J['door']['doorHalfWidth'], J['door']['doorX']
lane_edge = min(math.hypot(max(abs(x-doorx)-half, 0), z-plane)-r for x,z,r,_ in jw)
floor('J lane collider-edge clearance', lane_edge, 1.0)
window_hits = [(x,z) for x,z,r,_ in jw if
               math.hypot(max(abs(x-doorx)-half-0.5, 0), max(abs(z-plane)-0.5, 0)) <= r]
check('J lane +/-0.5 window overlap', not window_hits, 'hits=%d' % len(window_hits))

if len(ghouls) == 2:
    floor('J ghoul mutual', distance(*ghouls), 12.5)
for i, g in enumerate(ghouls):
    for title, p in [('spawn', seat), ('landJ', landj)]:
        floor('J ghoul%d %s' % (i, title), distance(g, p), 8.0)
    floor('J ghoul%d ring walk-clear' % i, J['groundRadius']-distance(g,jc), 4.45)
    floor('J ghoul%d wall edge' % i, nearest(g,jw), 4.0)
    for n, row in enumerate(jrows):
        floor('J ghoul%d prop%d %s raw' % (i,n,row['asset']), distance(g,point(row)), 5.0)
for i, row in enumerate(jrows):
    p = point(row)
    floor('J prop%d %s wall raw' % (i,row['asset']), nearest(p,jw,False), 4.0)
    floor('J prop%d ring walk-clear' % i, J['groundRadius']-distance(p,jc), 4.0)
    for title, dest in [('spawn',seat),('landJ',landj)]:
        floor('J prop%d %s' % (i,title),distance(p,dest),6.0)
    for j, other in enumerate(jrows[:i]):
        floor('J props %d/%d mutual' % (j,i),distance(point(other),p),4.0)

# F side: check all landed prop, ring, enemy, and F's own landing seats.
floor('F hook nearest prop', min(distance(hook,point(r)) for r in frows), 4.0)
floor('F hook ring edge',nearest(hook,fw),4.0)
floor('F hook ghoul',min(distance(hook,g) for g in fghouls),5.0)
for name, row in F['door']['land'].items():
    floor('F hook own land '+name,distance(hook,point(row)),6.0)
check('F hook outside F walk-out lane', abs(hook[0]-F['door']['doorX']) > F['door']['doorHalfWidth'])
check('F land within F disc (1.5 margin)',distance(landf,fc) <= F['groundRadius']-1.5)
for n,row in enumerate(frows):
    floor('F land prop%d %s' % (n,row['asset']),distance(landf,point(row)),6.0)
floor('F land ring edge',nearest(landf,fw),4.0)

# V-9 (AMEND-1, IO ruling 2026-11-07 wake 21): the original requirement
# (>=12 m at (0,-702)) placed the circle center INSIDE the root column's
# own collider — spec-author error, re-ruled to >= 6.0 m at (0,-709).
# Per-row collider radius is measured width*scale/2; ghoul seats are
# points (radius 0). All non-ring props and ring circles count.
center_north = (jc[0], jc[1]-9)  # adjudicated (0,-709) relative to J center
obstacles = [(distance(center_north,point(row))-WIDTH[row['asset']]*row['scale']/2,
              '%s at %s' % (row['asset'],point(row))) for row in jrows]
obstacles.extend((distance(center_north,(x,z))-r,'wall at (%.2f,%.2f)' % (x,z))
                 for x,z,r,_ in jw)
obstacles.extend((distance(center_north,g),'ghoul at %s' % (g,)) for g in ghouls)
clear, binding = min(obstacles)
print('V-9 center-north %s clear radius %.4f m; binding %s' % (center_north,clear,binding))
print('V-9 footprint widths (m): %s; wall r %.3f, ghoul r 0' % (WIDTH,WR))
floor('V-9 clear radius',clear,6.0)
print('--- %d checks; %d failures ---' % (checks,len(failures)))
for label in failures:
    print('FAIL: '+label)
sys.exit(1 if failures else 0)
