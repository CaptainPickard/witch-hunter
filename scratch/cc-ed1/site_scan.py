"""CC-ED1 site scanner: find a low-slope east-flank seat for the second den.

A-1 lesson (CC-WD1): do NOT lock a site in the spec until WH_GROUND terrain
proves it. This scans a candidate grid on the east flank, enumerates conflicts
from CONFIG.js itself (east loop waypoints, all wolf spawn rows, regionC props,
roads), and reports the best seats. Run from /tmp/wh-worldfeat (scratch only).

Pure stdlib + node one-shot (seat math delegated to a node child below).
"""
import json
import math
import re
import subprocess
import sys

SRC = '/tmp/wh-worldfeat/prototype/js/CONFIG.js'
src = open(SRC, encoding='utf-8').read()


def rows(tag):
    out = []
    for m in re.finditer(r'^\s*\{ ' + tag + r": '([a-zA-Z]+)', x: (-?[\d.]+), z: (-?[\d.]+)", src, re.M):
        out.append((float(m.group(2)), float(m.group(3)), m.group(1)))
    return out


props = rows('asset')
enemies = rows('type')
wolves = [p for p in enemies if p[2] == 'wolf']

# east loop waypoints (CONFIG.wolfPacks id 'east', L7)
em = re.search(r"id: 'east', regionId: 'forest_of_the_old_king'[^}]*?waypoints: \[\[(.*?)\]\]", src, re.S)
east_wpts = [tuple(map(float, p)) for p in
             re.findall(r'(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)', em.group(1))]

# nearest fire anywhere in C
fires = [(x, z) for a, x, z, _ in [(m.group(1), float(m.group(2)), float(m.group(3)), None) for m in
         re.finditer(r"\{ asset: '(banditCampfire)', x: (-?[\d.]+), z: (-?[\d.]+)", src)]]

roads = []
for m in re.finditer(r"id: '([a-zA-Z]+)', regionId: 'forest_of_the_old_king',", src):
    seg = src[m.start():m.start() + 600]
    pm = re.search(r"points: \[\[(.*?)\]\]", seg)
    hm = re.search(r"halfWidth: ([\d.]+)", seg)
    if pm and hm:
        pts = [(float(a), float(b)) for a, b in
               re.findall(r'(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)', pm.group(1))]
        if len(pts) >= 2:
            roads.append((m.group(1), pts, float(hm.group(1))))


def sd(px, pz, a, b):
    dx, dz = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dz * dz
    t = max(0.0, min(1.0, ((px - a[0]) * dx + (pz - a[1]) * dz) / L2))
    return math.hypot(px - (a[0] + t * dx), pz - (a[1] + t * dz))


def cand_ok(cx, cz):
    why = []
    if not (150 <= math.hypot(cx, cz + 366) <= 235):
        why.append(f'region r {math.hypot(cx, cz + 366):.0f} outside 150-235')
    dwp = min(math.hypot(cx - wx, cz - wz) for wx, wz in east_wpts)
    if dwp < 36:
        why.append(f'eastwaypt {dwp:.0f}')
    dwl = min(math.hypot(cx - p[0], cz - p[1]) for p in wolves)
    if dwl < 18:
        why.append(f'wolfsrow {dwl:.0f}')
    dfi = min(math.hypot(cx - x, cz - z) for x, z in fires)
    if dfi < 25:
        why.append(f'fire {dfi:.0f}')
    dro = min(min(sd(cx, cz, pts[i], pts[i + 1]) for i in range(len(pts) - 1))
              for _, pts, _ in roads) - 2.2
    if dro < 12:
        why.append(f'road {dro:.0f}')
    dpr = min(math.hypot(cx - p[0], cz - p[1]) for p in props)
    if dpr < 14:
        why.append(f'prop {dpr:.0f}')
    # west den must stay far: no twin-site confusion
    dwd = math.hypot(cx + 194, cz + 451)
    if dwd < 300:
        why.append(f'westden {dwd:.0f}')
    return why


# coarse grid on the east flank
best = []
for gx in range(110, 261, 5):
    for gz in range(-520, -260, 5):
        why = cand_ok(gx, gz)
        if not why:
            best.append((gx, gz))
print(f'{len(best)} coarse candidate centers')
if not best:
    # relax one band at a time, report why the grid failed
    from collections import Counter
    c = Counter()
    for gx in range(110, 261, 5):
        for gz in range(-520, -260, 5):
            for w in cand_ok(gx, gz):
                c[w.split(chr(32))[0]] += 1
    print(c.most_common())
    sys.exit(1)

# seat probe via node one-shot (WH_GROUND.heightAt + slopeTan per center)
probe_js = r'''
globalThis.window = globalThis; globalThis.self = globalThis;
const path = require('path');
const R = '/tmp/wh-worldfeat';
require(path.join(R, 'prototype/vendor/three.classic.js'));
require(path.join(R, 'prototype/js/CONFIG.js'));
require(path.join(R, 'prototype/js/wh-ground.js'));
const G = window.WH_GROUND; const RID = 'forest_of_the_old_king';
const pts = process.argv.slice(2).map(p => p.split(',').map(Number));
const out = [];
for (const [x, z] of pts) {
  const y = G.heightAt(RID, x, z);
  const deg = Math.atan(G.slopeTan(RID, x, z)) * 180 / Math.PI;
  out.push({ x, z, y, deg });
}
console.log(JSON.stringify(out));
'''
r = subprocess.run(['node', '-e', probe_js] + [f'{x},{z}' for x, z in best],
                   capture_output=True, text=True, timeout=300)
if r.returncode != 0:
    print('NODE FAIL', r.stderr[:500]); sys.exit(2)
seats = json.loads(r.stdout)

# pass 2: slope<=6 deg, |y|<=3, then refine local relief in the node probe too
good = [s for s in seats if abs(s['y']) <= 3.0 and s['deg'] <= 6.0]
print(f'{len(good)} after terrain pass (<=6 deg, |y|<=3):')
for s in sorted(good, key=lambda s: (abs(s['y']), s['deg']))[:24]:
    wp = min(math.hypot(s['x'] - w[0], s['z'] - w[1]) for w in east_wpts)
    print(f"  ({s['x']},{s['z']}) y={s['y']:.2f} slope={s['deg']:.1f}deg eastwp={wp:.0f}m")
