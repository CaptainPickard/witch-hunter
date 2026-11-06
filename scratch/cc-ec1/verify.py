#!/usr/bin/env python3
"""CC-EC1 pre-commit verification battery (valspec V-stepping)."""
import subprocess, re, math, sys

R = '/tmp/wh-worldfeat'
def g(cmd):
    return subprocess.run(cmd, shell=True, cwd=R, capture_output=True, text=True).stdout

ok = 0; fail = 0
def check(name, cond, extra=''):
    global ok, fail
    if cond: ok += 1; print(f'  PASS {name} {extra}')
    else: fail += 1; print(f'  FAIL {name} {extra}')

cfg = open(R + '/prototype/js/CONFIG.js').read()

# NE-1 coven row numbers
cov = re.search(r'coven: \{(.*?)\n    \},', cfg, re.S).group(1)
for k, v in [('hpMax: 60.0', 'hpMax 60'), ('moveSpeed: 3.4', 'mv 3.4'), ('chaseSpeed: 4.6', 'chase 4.6'),
             ('attackDamage: 0.0', 'dmg 0'), ('attackRange: 0,', 'range 0'), ('attackCooldown: 0,', 'cd 0'),
             ('sightRadius: 20.0', 'sight 20'), ('leashRadius: 40.0', 'leash 40'),
             ('staggerTime: 0.45', 'stagger .45'), ('radius: 0.7', 'radius .7'),
             ('aggroPingInterval: 0.2', 'ping .2'),
             ('windup: 0.55', 'windup .55'), ('active: 0.12', 'active .12'), ('recover: 0.85', 'recover .85'),
             ('hitArcDeg: 50', 'arc 50'), ('trackDegPerSec: 180', 'track 180'), ('castRange: 22.0', 'castRange 22')]:
    check('NE-1 ' + v, k in cov)

# NE-2 covenBolt
eb = re.search(r'enemySpell: \{(.*?)\n  \},', cfg, re.S).group(1)
for k, v in [("kind: 'projectile'", 'kind'), ('focusCost: 0', 'focus 0'), ('damage: 14', 'dmg 14'),
             ('speed: 16', 'speed 16'), ('hitRadius: 0.8', 'hr .8'), ('maxRange: 22', 'range 22'),
             ('castWindup: 0.55', 'windup .55'), ('castCooldown: 2.6', 'cd 2.6'),
             ('schoolColor: 0x4fd8c8', 'cyan'), ("name: 'Coven Bolt'", 'name'), ("glyph: 'CB'", 'glyph'),
             ('intensity: 6.0, distance: 9, decay: 2, flickerPct: 8', 'light row'),
             ('intensity: 2.0, distance: 6, decay: 2, flickerPct: 10', 'projLight row')]:
    check('NE-2 ' + v, k in eb)

# NE-4 placement: enemySpell top-level sibling, covenBolt only in enemySpell
check('NE-4 enemySpell sibling', bool(re.search(r'\n  enemySpell: \{', cfg)))
check('NE-4 covenBolt not in spell', 'covenBolt' not in re.search(r'\n  spell: \{(.*?)\n  \},', cfg, re.S).group(1))
check('NE-4 player.radius untouched=0.7', 'radius: 0.7,                      // collision circle' in cfg)

# kill_coven
check('V4 kill_coven: 30', 'kill_coven: 30' in cfg)

# regionC: coven rows at array end, indices 50/51
cblk = re.findall(r'enemies: \[(.*?)\n    \]', cfg, re.S)[2]
rows = re.findall(r"\{ type: '(\w+)', x: (-?[\d.]+), z: (-?[\d.]+)", cblk)
check('V3 regionC 52 rows', len(rows) == 52, f'got {len(rows)}')
check('V3 rows 50/51 are coven spec coords',
      rows[50] == ('coven', '-118.4', '-238.2') and rows[51] == ('coven', '-99.2', '-249.1'),
      f'{rows[50]} {rows[51]}')

# assets
assets = open(R + '/prototype/js/assets.js').read()
check('V2 manifest covenBody elf', "covenBody: 'art-direction/3d/assets/races_regen/rigged/elf-dawn-refuser-male.rigged.glb'" in assets)
check('V2 CHARACTERS covenBody 6', 'covenBody: 6' in assets)
check('ED-2 BODY_PNG untouched (no coven key)', 'covenBody' not in re.search(r'BODY_PNG = \{(.*?)\};', assets, re.S).group(1))

# spells
sp = open(R + '/prototype/js/spells.js').read()
check('V6 WH_CovenBolt class', 'function WH_CovenBolt' in sp)
check('V6 spawnEnemyBolt reads enemySpell', 'window.WH_CONFIG.enemySpell[spellId]' in sp)
check('V6 radius sphere 0.22', 'SphereGeometry(0.22' in sp)
check('V6 hitRadius + player.radius live', 'window.WH_CONFIG.player.radius' in sp)
# V6 no PointLight in the CC-EC1 coven slice (Radiance predates it)
coven_slice = sp[sp.index('---- Coven Bolt'):sp.index('---- Radiance follow-light')]
check('V6 no PointLight in coven slice', 'PointLight' not in coven_slice)
check('V6 spawnEnemyBolt null for unknown', "if (!ES || !ES[spellId]) return null;" in sp)
check('V6 kind gate projectile', "if (ES[spellId].kind !== 'projectile') return null;" in sp)

# enemy.js
en = open(R + '/prototype/js/enemy.js').read()
check('V5.1 spawnEnemyBolt call (NOT spawn())', "window.WH_SPELLS.spawnEnemyBolt(window.WH_GAME.scene, 'covenBolt'" in en)
check('V5.1 origin y+1.2, +0.3 toward player', 'this.pos.y + 1.2' in en and 'sdirX * 0.3' in en)
check('V5.2 keep-distance 8/16 bands, x0.6/x0.5', 'distToPlayer < 8' in en and 'distToPlayer > 16' in en)
check('V5.2 attack-hold keep-distance', bool(re.search(r"fsm === 'attack'.*?isCoven", en, re.S)))
check('V5.3 castRange cancel', 'distToPlayer > this.covenCastRange' in en)
check('V5.4 staggers via existing machinery', 'staggerTime' in en and 'enterStagger = function' in en)
check('V5.6 aggro path untouched', bool(re.search(r"sight \* 0\.8\).*?\n.*?setFsm\('chase'\)", en)))
check('V5 isCoven gate', "this.isCoven = type === 'coven'" in en)

# game.js
gm = open(R + '/prototype/js/game.js').read()
check('V8 enemyBolts init sibling', 'enemyBolts: []' in gm)
check('V8 loop after firebolts loop', gm.index('enemyBolts.length') > gm.index('game.firebolts.length'))
check('V7 MD exactly-once call site', gm.count('WH_LEVEL.magicDefense()') == 1)
check('V7 Math.round form', 'Math.round(dmgEB * (1 - window.WH_LEVEL.magicDefense()))' in gm)
check('V7 bare isSpell attacker', gm.count('isSpell: true') == 1)
check('V7 no enterStagger in attacker', 'enterStagger' not in gm[gm.index('damagePlayerFromEnemy(reducedEB', 4000):])
check('V8 one-hit spent/hitFlash', 'boltEB.spent' in gm)
# player.js untouched
check('V7.1 player.js diff EMPTY', g('git diff -- prototype/js/player.js').strip() == '')
check('R1 leveling.js EMPTY', g('git diff -- prototype/js/leveling.js').strip() == '')
check('R1 anim.js EMPTY', g('git diff -- prototype/js/anim.js').strip() == '')
check('R1 light.js EMPTY', g('git diff -- prototype/js/light.js').strip() == '')

# V9 art greps
check('V9.1 cyan in CONFIG', '0x4fd8c8' in cfg)
check('V9.1 cyan in spells', '0x4fd8c8' in sp)
check('V9.1 cyan in enemy glow', '0x4fd8c8' in en)
check('V9.2 char-09 in CONFIG', 'char-09-coven-wizard' in cfg)
check('V9.2 ONE cyan accent', 'ONE cyan accent' in cfg)
check('V9.2 no red', 'NO red/orange' in cfg)
check('V9.2 magicDefense line in CONFIG', 'magicDefense is' in cfg)
diffnew = g("git diff | grep '^+'")
check('V9.3 no red/orange hexes added', not re.search(r'0xff7722|0xff0000|0xcc0000|0xff3333', diffnew))

# builds
build = open(R + '/prototype/builds/v8-playable.html').read()
n = build.count('coven')
check('V11.2 marker >= 4', n >= 4, f'count={n}')

# clearance (re-run: unchanged coords -> prior result)
cov1, cov2 = (-118.4, -238.2), (-99.2, -249.1)
# spot-check the two binding nearest members
d1 = math.hypot(cov1[0] + 112.5, cov1[1] + 276.1)
d2 = math.hypot(cov2[0] + 112.5, cov2[1] + 276.1)
dd1 = math.hypot(cov1[0] + 163.4, cov1[1] + 202.6)
dd2 = math.hypot(cov2[0] + 163.4, cov2[1] + 202.6)
check('V10 coven1 swWP 38.4', abs(d1 - 38.44) < 0.2, f'{d1:.1f}')
check('V10 coven2 swWP 30.1', abs(d2 - 30.15) < 0.2, f'{d2:.1f}')
check('V10 coven1 door 57.4', abs(dd1 - 57.44) < 0.3, f'{dd1:.1f}')
check('V10 coven2 door 79.3', abs(dd2 - 79.26) < 0.3, f'{dd2:.1f}')

print(f'\n=== {ok} PASS / {fail} FAIL ===')
sys.exit(1 if fail else 0)
