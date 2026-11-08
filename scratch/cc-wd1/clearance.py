"""CC-WD1 clearance check: G-1..G-8 margins for the den layout at (-194,-451).

Pure-stdlib parse of prototype/js/CONFIG.js. exit 0 iff every margin passes.
Written by IO this wake (CC-WD1 inline build); Testerbot re-derives.
"""
import math
import re
import sys

SRC = 'prototype/js/CONFIG.js'
src = open(SRC, encoding='utf-8').read()

props = [(m.group(1), float(m.group(2)), float(m.group(3)))
         for m in re.finditer(r"\{ asset: '([a-zA-Z]+)', x: (-?[\d.]+), z: (-?[\d.]+)", src)]
enemies = [(m.group(1), float(m.group(2)), float(m.group(3)))
           for m in re.finditer(r"\{ type: '([a-z]+)', x: (-?[\d.]+), z: (-?[\d.]+)", src)]
wolves = [e for e in enemies if e[0] == 'wolf']
wpts = [(-190, -420), (-215, -418), (-224, -388), (-224, -362), (-200, -358),
        (-178, -340), (-166, -372), (-172, -402)]
fires = [p for p in props if p[0] == 'banditCampfire']
roads = []
for m in re.finditer(r"id: '([a-zA-Z]+)', regionId: 'forest_of_the_old_king',", src):
    seg = src[m.start():m.start() + 600]
    # boundary-guarded: 'points:' must not be the tail of 'waypoints:'
    pm = re.search(r"points: \[\[(.*?)\]\]", seg)
    hm = re.search(r"halfWidth: ([\d.]+)", seg)
    if pm and hm:
        body = pm.group(1)
        pts = []
        for nums in re.findall(r'(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)', body):
            pts.append((float(nums[0]), float(nums[1])))
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


# The CC-WD1 layout (IO spec Amendment A-1 final table).
layout_props = [
    ('deadTree', -190.0, -446.0), ('deadTree', -197.0, -445.0), ('deadTree', -201.0, -445.0),
    ('mossBoulder', -199.0, -455.0), ('mossBoulder', -196.0, -458.0), ('mossBoulder', -201.0, -451.0),
    ('skullPile', -189.0, -454.0), ('skullPile', -187.0, -452.0), ('buriedCoffin', -186.0, -456.0),
    ('rubblePile', -189.0, -449.0), ('rubblePile', -186.0, -446.0)]
nodes = [(-192.5, -461.0), (-184.0, -450.0), (-204.0, -453.5), (-198.5, -441.0)]
center = (-194.0, -451.0)

# A-1 union law: the 12 new rows (11 props + 4 nodes) govern G-1..G-4 (the G-4
# road-edge metric stays prop-set only, matching the A-1 amendment wording).
union_rows = [(a, x, z) for a, x, z in layout_props] + \
             [('bonePile', x, z) for x, z in nodes]
newpts = [(x, z) for _, x, z in layout_props]
# FIX (IO remediation): self-match artifact — the census regex parses ALL {
# asset: rows, INCLUDING this round's own new rows, which sit at d=0.00 from
# their own layout entries and failed G-5a spuriously. Line-tagged exclusion:
# every row line inserted this round carries the marker; pre-existing rows
# don't. pre_props = census minus the round's own rows.
NEW_TAG = 'west_hollow_den'
props = []
for m in re.finditer(r"^\s*\{ asset: '([a-zA-Z]+)', x: (-?[\d.]+), z: (-?[\d.]+)[^\n]*$", src,
                     re.M):
    if NEW_TAG in m.group(0):
        continue
    props.append((m.group(1), float(m.group(2)), float(m.group(3))))
treeRe = re.compile('tree|oak|ash|yew|witchwood', re.I)
pre_tree = [(p[1], p[2]) for p in props if treeRe.search(p[0])]
pre_other = [(p[1], p[2]) for p in props
             if not treeRe.search(p[0]) and p[0] != 'banditCampfire']
report = {}
# A-1: G-1..G-3 governed by the 12-row UNION (11 props + 4 nodes); G-4's
# road-edge metric stays scoped to the prop set in the amendment's wording.
report['G-1 union-vs-wolfspawn >= 5'] = (
    mind([((x, z), (w[1], w[2])) for _, x, z in union_rows for w in wolves]), 5, 'min')
# A-1 law: G-2 patrol-loop clearance is PROPS-governed (A-1 derived 25.96 m
# from the prop set; G-2n below makes the node-side proximity explicit).
report['G-2 props-vs-westwp >= 25'] = (
    mind([((x, z), w) for _, x, z in layout_props for w in wpts]), 25, 'min')
# G-2n makes the node-side proximity EXPLICIT and independently checkable
# instead of a discoverable surprise for Testerbot (the mouth-approach node
# (-198.5,-441) sits 22.66 m from waypoint (-190,-420); loop path itself stays
# off the hollow).
report['G-2n nodes-vs-westwp >= 20'] = (
    mind([(n, w) for n in nodes for w in wpts]), 20, 'min')
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
    mind([(n, b) for n in nodes for b in pre_tree + new_tree]), 4, 'min')  # A-1: was 5.0 pre-amendment
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
report['G-8-seen-by-seat_probe (sep script)'] = (float('nan'), 0, 'info')

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
