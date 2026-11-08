#!/usr/bin/env python3
"""CC-C16b apply: append 4 bandit camps + 4 wolf packs to CONFIG.js.
Pattern parity: CC-C6 bandit camps (fire + bedrolls + guards as patrol rows)
and CC-C5 wolf packs (packId/waypointPhase members + wolfPacks defs).
Fires = kind 'campfire' (CC-C6C night-atmospheric; tutorial cook fire stays
the only cookable one). Deterministic row emission from sites.json."""
import json, math, re

src = open('/tmp/wh-worldfeat/prototype/js/CONFIG.js').read()
S = json.load(open('/tmp/wh-worldfeat/scratch/cc-c16/sites.json'))
PACK_IDS = ['sw', 'se', 'ss', 'nw2']

# ---- 1. regionC.enemies: append after the last wolf row (north pack, phase 3)
iE = src.index('    enemies: [', src.index('  regionC: {'))
# find the LAST wolf row in regionC enemies (the north pack's phase 3)
m = re.search(r"\{ type: 'wolf', x: -6\.9, z: -519\.6, packId: 'north', waypointPhase: 3 \},", src)
assert m, 'last wolf row not found'
ins_at = src.index('\n', m.end()) + 1
enemy_rows = []
n_en = 0
# bandit camps: guards 3 each (packless bandits, CC-C6's pattern row shape)
for ci, c in enumerate(S['camps']):
    x, z = c[0], c[1]
    # guard placement: 3 offsets in a wedge facing the ring road side
    for gi, (dx, dz) in enumerate([(2.2, 2.6), (-2.6, 2.0), (0.0, 3.4)]):
        enemy_rows.append("      { type: 'bandit', x: %.1f, z: %.1f },   // CC-C16b camp %d guard %d" % (x + dx, z + dz, ci + 1, gi + 1))
        n_en += 1
# wolf packs: 4 members each, phases 0..3 around the loop
for pi, pts in enumerate(S['loops']):
    pid = PACK_IDS[pi]
    for wi in range(4):
        pt = pts[wi]   # members 0-3 ride the first four waypoints' phase
        enemy_rows.append("      { type: 'wolf', x: %.1f, z: %.1f, packId: '%s', waypointPhase: %d }," % (pt[0], pt[1], pid, wi))
        n_en += 1
src = src[:ins_at] + '\n'.join(enemy_rows) + '\n' + src[ins_at:]
print('enemy rows appended:', n_en)

# ---- 2. wolfPacks defs
iW = src.index('    wolfPacks: [')
m = re.search(r"(separationPush: 6\.0,)", src)
assert m
pack_defs = []
for pi, pts in enumerate(S['loops']):
    pts_txt = ', '.join("[%s, %s]" % (p[0], p[1]) for p in pts)
    pack_defs.append("      { id: '%s', regionId: 'forest_of_the_old_king', members: 4, spawnSpread: 6,   // CC-C16b densify pack %d\n        waypoints: [%s] }," % (PACK_IDS[pi], pi + 1, pts_txt))
src = src[:m.start()] + '\n'.join(pack_defs) + '\n    ' + src[m.start():]
print('pack defs appended:', len(pack_defs))

# ---- 3. fires: regionC.props (banditCampfire, m15 pattern) + cooking.stations rows
# props anchor: the last graveMound row + ruins block end (before rotLair)
m = re.search(r"      \{ asset: 'stoneCrossTilted',     x: -26\.5,  z: -146\.5, rotY: 3\.0, scale: 1\.55 \}\n", src)
assert m, 'ruins tail not found'
props_txt = "      // CC-C16b DENSIFY: 4 bandit camp fires (CC-C6C kind campfire, night-only atmospheric; the STARTING tutorial fire stays the only cookable one)"
for ci, c in enumerate(S['camps']):
    props_txt += "\n      { asset: 'banditCampfire', x: %.1f, z: %.1f, rotY: %.2f, scale: 2.02, cullM: 140 },   // CC-C16b camp %d fire" % (c[0], c[1], (ci * 0.7) % 6.28, ci + 1)
src = src[:m.end()] + props_txt + '\n' + src[m.end():]
print('fire props appended:', len(S['camps']))

# ---- 4. cooking.stations rows
iS2 = src.index('window.WH_CONFIG.cooking = {')
m = re.search(r"    \{ id: 'banditFireC', kind: 'campfire', regionId: 'forest_of_the_old_king',\n      asset: 'banditCampfire', x: -140\.0, z: -506\.0, startLit: true \} ?// L6 Charlie\n", src)
if not m:
    m = re.search(r"\{ id: 'banditFireC', kind: 'campfire', regionId: 'forest_of_the_old_king',\n      asset: 'banditCampfire', x: -140\.0, z: -506\.0, startLit: true \}", src)
assert m, 'Charlie fire row not found'
rows2 = []
for ci, c in enumerate(S['camps']):
    rows2.append("    { id: 'banditFireD%d', kind: 'campfire', regionId: 'forest_of_the_old_king',\n      asset: 'banditCampfire', x: %.1f, z: %.1f, startLit: true },    // CC-C16b camp %d" % (ci + 1, c[0], c[1], ci + 1))
src = src[:m.end()] + ',\n' + '\n'.join(rows2) + src[m.end():]
print('cooking rows appended:', len(rows2))

open('/tmp/wh-worldfeat/prototype/js/CONFIG.js', 'w').write(src)
print('WROTE')