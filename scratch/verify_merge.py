#!/usr/bin/env python3
"""Semantic merge verification: every integrity fix from dev's 33d0d80/8f777bb
must either exist in the merged tree or be superseded (documented).
Also: no references to deleted keys, chain framework intact, clips intact."""
import re, esprima

p = 'prototype/js/'
merged = {f: open(p + f).read() for f in
          ['player.js', 'CONFIG.js', 'assets.js', 'game.js', 'anim.js',
           'enemy.js']}
ok = lambda cond, msg: print(('PASS ' if cond else 'FAIL ') + msg)

# dev 33d0d80 fixes to check survive in merged code:
g = merged['game.js']
ok("guardBreak" in g or "guardBreak" in merged['player.js'], 'guard break present')
ok('NaN' in merged['player.js'] + merged['enemy.js'], 'NaN containment present')
ok('corpseFinalY' in merged['enemy.js'] or 'deadFall' in merged['enemy.js'], 'enemy corpse/state logic present')

# combat-integrity: anim latch (attack anim keeps running during swing)
ok('attackPhase' in merged['anim.js'], 'anim attack phase latch present')

# whanim3: CSP intake in assets.js
a = merged['assets.js']
ok('registerEmbeddedImagePlugin' in a, 'CSP-safe plugin present')
ok('WHGLTFLoader(mgr)' in a, 'loader constructed with manager')
ok(a.count('function loadOne') == 1, 'exactly one loadOne')
ok('registerEmbeddedImagePlugin(loader, mgr)' in a, 'plugin registered in loadAttempt')

# feat framework intact:
ok("chain: ['slashR2L', 'slashL2R', 'thrust']" in merged['CONFIG.js'], 'longsword chain order')
ok('MOVE_NAMES' in merged['anim.js'], 'anim MOVE_NAMES mapping')
ok('combat-chain' in merged['assets.js'] or 'combat-chain' in open(p+'CONFIG.js').read(), 'combat-chain GLB referenced')
ok('camAutoFollow' not in merged['player.js'] + merged['CONFIG.js'], 'auto-follow keys gone')
ok('internalResDiv' in merged['CONFIG.js'], 'pixel tuner knob present')
ok('dirtPath' in merged['CONFIG.js'], 'dirt path config present')

# deleted keys really gone from game code (enemy CONFIG rows still use
# attackDamage/attackRange by design - enemy stats, not player moveset)
ok('CFG.moveset.comboChainCap' not in merged['game.js'] + merged['player.js'], 'no dangling comboChainCap')
ok('CFG.player.attackDuration' not in merged['game.js'] + merged['player.js'], 'no dangling attackDuration')

# region A/B props intact (merge didn't clobber forest)
cfg = merged['CONFIG.js']
ok("asset: 'yewTree'" in cfg and 'livingOak' in cfg, 'forest species intact')

for f, s in merged.items():
    esprima.parseScript(s)
print('syntax all OK')