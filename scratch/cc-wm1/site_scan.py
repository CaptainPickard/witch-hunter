"""CC-WM1 site scanner: find the Redseam seat (doc 42 Part 5 rich iron seam,
darkwood entry tier, region C).

Adapted from scratch/cc-ed1/site_scan.py (proven pattern). Mine constraint set
differs from dens: destination-tier rim band (r 180-256), ROAD-READABLE
(12-60 m from a road centerline - findable, not on it), far from both dens
(>= 100 m), bandit camps (>= 80 m), wolf loops (>= 42 m), rot outcrop
(>= 50 m), keepOut sockets (>= 30 m), existing props (>= 16 m), larder bone
nodes (>= 20 m). Terrain: slope <= 6 deg, |y| <= 3 (pass 2, node one-shot).
Run from /tmp/wh-worldfeat (scratch only). Pure stdlib + node one-shot.
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
bandits = [p for p in enemies if p[2] == 'bandit']
# gather node seats (8 den larder bonePile + any others)
nodes = []
for m in re.finditer(r"\{ type: '([a-zA-Z]+)', x: (-?[\d.]+), z: (-?[\d.]+) \}", src):
    nodes.append((float(m.group(2)), float(m.group(3)), m.group(1)))

# all wolf pack waypoints (7 packs, CONFIG.wolfPacks)
wp_pts = []
for m in re.finditer(r"waypoints: \[(.*?)\]\s*\}", src, re.S):
    for a, b in re.findall(r'(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)', m.group(1)):
        wp_pts.append((float(a), float(b)))

fires = [(float(m.group(2)), float(m.group(3)))
         for m in re.finditer(r"\{ asset: '(banditCampfire)', x: (-?[\d.]+), z: (-?[\d.]+)", src)]

roads = []
for m in re.finditer(r"{ id: '([a-zA-Z]+)', regionId: 'forest_of_the_old_king',", src):
    seg = src[m.start():m.start() + 700]
    pm = re.search(r"points: \[\[(.*?)\]\]", seg)
    hm = re.search(r"halfWidth: ([\d.]+)", seg)
    if pm and hm:
        pts = [(float(a), float(b)) for a, b in
               re.findall(r'(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)', pm.group(1))]
        if len(pts) >= 2:
            roads.append((m.group(1), pts, float(hm.group(1))))
print(f'census: props={len(props)} enemies={len(enemies)} wolves={len(wolves)} '
      f'bandits={len(bandits)} nodes={len(nodes)} waypoints={len(wp_pts)} fires={len(fires)} roads={len(roads)}')


def sd(px, pz, a, b):
    dx, dz = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dz * dz
    t = max(0.0, min(1.0, ((px - a[0]) * dx + (pz - a[1]) * dz) / L2))
    return math.hypot(px - (a[0] + t * dx), pz - (a[1] + t * dz))


def dmin(px, pz, pts):
    return min(math.hypot(px - q[0], pz - q[1]) for q in pts)


KEEPOUTS = [(0, -366, 30), (0, -596, 18), (240, -366, 18), (-240, -366, 18), (-136, -219, 22)]
DEN_CTR = [(-194, -451), (210, -445)]
CAMP_CTR = [(-106.2, -469.4), (118.9, -445.9), (-208.1, -243.3), (144.1, -534.2)]


def cand_ok(cx, cz):
    why = []
    r = math.hypot(cx, cz + 366)
    if not (180 <= r <= 256):
        why.append(f'regionr{r:.0f}')
    if dmin(cx, cz, wp_pts) < 42:
        why.append(f'wolfwp{dmin(cx, cz, wp_pts):.0f}')
    d_en = dmin(cx, cz, [(p[0], p[1]) for p in enemies])
    if d_en < 42:
        why.append(f'enemyrow{d_en:.0f}')
    d_np = dmin(cx, cz, [(p[0], p[1]) for p in nodes])
    if d_np < 20:
        why.append(f'gathernode{d_np:.0f}')
    if dmin(cx, cz, fires) < 30:
        why.append('fire')
    dro = min(min(sd(cx, cz, pts[i], pts[i + 1]) for i in range(len(pts) - 1)) - w
              for _, pts, w in roads)
    if not (12 <= dro <= 60):
        why.append(f'road{dro:.0f}')
    if dmin(cx, cz, [(p[0], p[1]) for p in props]) < 16:
        why.append('prop')
    for dx, dz in DEN_CTR:
        if math.hypot(cx - dx, cz - dz) < 100:
            why.append(f'den{math.hypot(cx-dx, cz-dz):.0f}')
    for dx, dz in CAMP_CTR:
        if math.hypot(cx - dx, cz - dz) < 80:
            why.append(f'banditcamp{math.hypot(cx-dx, cz-dz):.0f}')
    for kx, kz, kr in KEEPOUTS:
        if math.hypot(cx - kx, cz - kz) < kr + 30:
            why.append(f'keepout{kx},{kz}')
    return why


# coarse grid over the full ring (both flanks; site_scan decides the flank)
best = []
whycount = {}
for gx in range(-260, 261, 5):
    for gz in range(-600, -139, 5):
        why = cand_ok(gx, gz)
        if why:
            for w in why:
                whycount[w.split('0')[0].split('.')[0][:12] if not w[0].isdigit() else w[:12]] = \
                    whycount.get(w.split('0')[0].split('.')[0][:12] if not w[0].isdigit() else w[:12], 0) + 1
        else:
            best.append((gx, gz))
print(f'{len(best)} coarse candidate centers')
if not best:
    from collections import Counter
    c = Counter(whycount)
    print(c.most_common(20))
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
r = subprocess.run(['node', '-e', probe_js, '--'] + [f'{x},{z}' for x, z in best],
                   capture_output=True, text=True, timeout=600)
if r.returncode != 0:
    print('NODE FAIL', r.stderr[:500]); sys.exit(2)
seats = json.loads(r.stdout)

good = [s for s in seats if abs(s['y']) <= 3.0 and s['deg'] <= 6.0]
print(f'{len(good)} after terrain pass (<=6 deg, |y|<=3):')
for s in sorted(good, key=lambda s: (abs(s['y']) + s['deg'] / 6.0))[:30]:
    dr = min(min(sd(s['x'], s['z'], pts[i], pts[i + 1]) for i in range(len(pts) - 1)) - w
             for _, pts, w in roads)
    dw = dmin(s['x'], s['z'], wp_pts)
    print(f"  ({s['x']},{s['z']}) y={s['y']:.2f} slope={s['deg']:.1f}deg road={dr:.0f}m wolfwp={dw:.0f}m")
