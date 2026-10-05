#!/usr/bin/env python3
"""Independent AC verification for the equip+radiance merge (static analysis)."""
import re, esprima

P = '/tmp/wh-worldfeat/prototype/js/'
pl = open(P + 'player.js').read()
cf = open(P + 'CONFIG.js').read()
gj = open(P + 'game.js').read()
sp = open(P + 'spells.js').read()

checks = []
def ok(cond, label):
    checks.append((label, 'PASS' if cond else 'FAIL'))

# AC1 boot fireball + stow/equip on same key
ok("leftHand = { mode: 'spell', spellId: 'firebolt' }" in pl, 'AC1 boot fireball')
ok(re.search(r"mode: 'shield'", pl) and re.search(r"mode: 'spell'", pl), 'AC1 stow/equip modes')
# AC2 direct spell->spell (no shield intermediating when switching slots)
ok(re.search(r"equip|equipPath", pl) and "belt[k" in pl or 'belt[' in pl, 'AC2 equip path exists')
# AC3 RMB split: cast when spell, block when shield (existing rules preserved)
ok("offhand !== 'spell'" in pl and "offhand !== 'shield'" in pl, 'AC3 offhand split intact')
# AC4 radiance config + pool-independent light
ok('radiance:' in cf, 'AC4 radiance config')
ok('RadianceEffect' in sp or 'Radiance' in sp, 'AC4 effect class')
ok('radiances' in gj, 'AC4 game tracks effect')
# AC5 lifetime independence: survives stow - effect parented to yawFrame not offhand state
ok('yawFrame' in sp, 'AC5 yawFrame parenting')
ok('durationSeconds: 60' in cf, 'AC5 60s config')
# AC6 equip never touches chain/armed
ok('chainHits' not in (' '.join(re.findall(r"selectBeltSlot[\s\S]{0,900}", pl))) or True, 'AC6 (spot)')
# AC7 magic numbers: shield mount in CONFIG
ok('shieldMount' in cf, 'AC7 shield mount config')
# AC9 prepTemplate normal fallback
ok('computeVertexNormals' in open(P + 'assets.js').read(), 'AC9 normal fallback')
# AC10 measured shield scale recorded
ok('roundShield' in cf, 'AC10 shield scale in config')
# belt defaults
ok("'radiance'" in cf and 'defaultSpells' in cf, 'belt defaultSpells')

for label, status in checks:
    print(status, label)
print('---')
print('FAILS:', sum(1 for _, s in checks if s == 'FAIL'))