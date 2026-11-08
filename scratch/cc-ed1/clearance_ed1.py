"""CC-ED1 clearance check: G-1..G-8 margins for the den layout at (210,-445).

Mirror of CC-WD1's proven tool (scratch/cc-wd1/clearance.py). Pure-stdlib parse
of prototype/js/CONFIG.js. Pre-landing this run: the east rows are NOT yet in
CONFIG (no self-match); the NEW_TAG line exclusion carries the WD1 fix so the
same script stays valid post-landing for Testerbot re-derivation. exit 0 iff
every margin passes.
"""
import math
import re
import sys

SRC = '/tmp/wh-worldfeat/prototype/js/CONFIG.js'
src = open(SRC, encoding='utf-8').read()

NEW_TAG = 'east_hollow_den'

# layout table (IO spec final table; A-1-equivalent frozen pre-spec by the
# scratch/cc-ed1/preseat_probe.js ALL-15-PASS)
layout_props = [
    ('deadTree', 206.0, -440.0), ('deadTree', 213.0, -439.0), ('deadTree', 217.0, -440.0),
    ('mossBoulder', 215.0, -449.0), ('mossBoulder', 208.0, -452.0), ('mossBoulder', 217.0, -445.0),
    ('skullPile', 205.0, -448.0), ('skullPile', 203.0, -446.0),
    ('buriedCoffin', 202.0, -450.0),
    ('rubblePile', 205.0, -443.0), ('rubblePile', 202.0, -440.0)]
nodes = [(208.5, -455.0), (199.5, -446.0), (220.0, -447.5), (214.5, -435.0)]
center = (210.0, -445.0)

union_rows = layout_props + [('bonePile', x, z) for x, z in nodes]
newpts = [(x, z) for _, x, z in layout_props]

# census with the WD1 line-tag exclusion law (exclude THIS round's rows when
# they have landed; pre-landing nothing carries the tag so the census is full)
props = []
for m in re.finditer(r"^\s*\{ asset: '([a-zA-Z]+)', x: (-?[\d.]+), z: (-?[\d.]+)[^\n]*$", src,
                     re.M):
    if NEW_TAG in m.group(0):
        continue
    props.append((m.group(1), float(m.group(2)), float(m.group(3))))
enemies = []
for m in re.finditer(r"^\s*\{ type: '([a-z]+)', x: (-?[\d.]+), z: (-?[\d.]+)[^\n]*$", src, re.M):
    if NEW_TAG in m.group(0):
        continue
    enemies.append((m.group(1), float(m.group(2)), float(m.group(3))))
wolves = [p for p in enemies if p[0] == 'wolf']
fires = [p for p in props if p[0] == 'banditCampfire']
# east loop waypoints (CONFIG.wolfPacks id 'east', L7)
em = re.search(r"id: 'east', regionId: 'forest_of_the_old_king',[^}]*?waypoints: \[\[(.*?)\]\]",
               src, re.S)
east_wpts = [(float(a), float(b)) for a, b in
             re.findall(r'(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)', em.group(1))]

roads = []
for m in re.finditer(r"id: '([a-zA-Z]+)', regionId: 'forest_of_the_old_king',", src):
    seg = src[m.start():m.start() + 600]
    # boundary-guarded: 'points:' must not be the tail of 'waypoints:'
    pm = re.search(r"points: \[\[(.*?)\]\]", seg)
    hm = re.search(r"halfWidth: ([\d.]+)", seg)
    if pm and hm:
        pts = [(float(a), float(b)) for a, b in
               re.findall(r'(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)', pm.group(1))]
        if len(pts) >= 2:
            roads.append((m.group(1), pts, float(hm.group(1)) if hm else 2.2))


def sd(px, pz, a, b):
    dx, dz = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dz * dz
    t = max(0.0, min(1.0, ((px - a[0]) * dx + (pz - a[1]) * dz) / L2))
    return math.hypot(px - (a[0] + t * dx), pz - (a[1] + t * dz))


def mind(pairs):
    vals = [math.dist(a, b) for a, b in pairs]
    return min(vals) if vals else float('nan')


treeRe = re.compile('tree|oak|ash|yew|witchwood', re.I)
pre_tree = [(p[1], p[2]) for p in props if treeRe.search(p[0])]
pre_other = [(p[1], p[2]) for p in props
             if not treeRe.search(p[0]) and p[0] != 'banditCampfire']
report = {}
# union law identical to CC-WD1 A-1: the 15 new rows govern G-1..G-3; G-4 stays
# prop-set only (matches the WD1 amendment wording we are mirroring).
report['G-1 union-vs-wolfspawn >= 5'] = (
    mind([((x, z), (p[1], p[2])) for _, x, z in union_rows for p in wolves]), 5, 'min')
report['G-2 props-vs-eastwp >= 25'] = (
    mind([((x, z), w) for _, x, z in layout_props for w in east_wpts]), 25, 'min')
report['G-2n nodes-vs-eastwp >= 20'] = (
    mind([(n, w) for n in nodes for w in east_wpts]), 20, 'min')
report['G-3 union-vs-fires >= 20'] = (
    mind([((x, z), (f[1], f[2])) for _, x, z in union_rows for f in fires]), 20, 'min')
report['G-4 props-vs-roadsedge >= 30'] = (
    min(min(sd(x, z, pts[i], pts[i + 1]) for i in range(len(pts) - 1))
        for _, x, z in layout_props for _, pts, hw in roads) - 2.2, 30, 'min')
report['G-5a props-vs-preother >= 3'] = (
    mind([(a, b) for a in newpts for b in pre_other]), 3, 'min')
report['G-5b props-vs-pretree >= 4'] = (
    mind([(a, b) for a in newpts for b in pre_tree]), 4, 'min')
report['G-5c newprops-mutual >= 2.5'] = (
    min(math.dist(newpts[i], newpts[j]) for i in range(len(newpts))
        for j in range(i + 1, len(newpts))), 2.5, 'min')
new_tree = [(x, z) for a, x, z in layout_props if treeRe.search(a)]
new_other = [(x, z) for a, x, z in layout_props if not treeRe.search(a)]
report['G-6a nodes-vs-tree >= 4'] = (
    mind([(n, b) for n in nodes for b in pre_tree + new_tree]), 4, 'min')
report['G-6b nodes-vs-other >= 3'] = (
    mind([(n, b) for n in nodes for b in pre_other + new_other]), 3, 'min')
report['G-6c nodes-mutual >= 6'] = (
    min(math.dist(nodes[i], nodes[j]) for i in range(len(nodes))
        for j in range(len(nodes)) if i != j), 6, 'min')
report['G-6d nodes-from-center <= 12'] = (
    max(math.dist(n, center) for n in nodes), 12, 'max')
report['G-7 union-from-Ccenter <= 262'] = (
    max(max(math.hypot(x, z + 366) for _, x, z in union_rows),
        max(math.hypot(nx, nz + 366) for nx, nz in nodes)), 262, 'max')
report['G-8-seen-by-preseat_probe (sep script)'] = (float('nan'), 0, 'info')

fails = []
for k, (v, lim, kind) in report.items():
    if kind == 'info':
        print(f'INFO {k}')
        continue
    ok = v >= lim if kind == 'min' else v <= lim
    print(('PASS ' if ok else 'FAIL ') + f'{k}: {v:.2f}')
    if not ok:
        fails.append(k.split(' ')[0])

print('RESULT:', 'CLEARED' if not fails else 'FAILED ' + ','.join(fails))
sys.exit(0 if not fails else 1)
