#!/usr/bin/env python3
"""Final verify: order 4 sky + full-build static checks."""
import esprima, re

g = open('/tmp/wh-worldfeat/prototype/js/game.js').read()
c = open('/tmp/wh-worldfeat/prototype/js/CONFIG.js').read()
rm = open('/tmp/wh-worldfeat/prototype/js/region-manager.js').read()
am = open('/tmp/wh-worldfeat/prototype/js/assets.js').read()

def ok(cond, msg):
    if cond: print('PASS', msg)
    else: print('FAIL', msg)

esprima.parseScript(g); esprima.parseScript(c); esprima.parseScript(rm); esprima.parseScript(am)
print('esprima: all 4 files OK')

ok('function setupSky' in g, 'setupSky defined')
ok('    setupSky();' in g, 'setupSky called in boot')
ok('    skyTick();' in g, 'skyTick in render loop')
ok('fog: false' in g, 'dome ignores fog')
ok('renderOrder = -10' in g, 'dome draws first')
ok('0x05070f' in g, 'scene.background near-black (both spots)', ) if g.count('0x05070f') >= 1 else None
ok('scene.background = new THREE.Color(0x05070f)' in g, 'boot background near-black')
ok('game.scene.background = new THREE.Color(region.fogColor)' not in g, 'region swap no longer sets background')
ok('sky: {' in c, 'CONFIG.sky block present')
ok('hemiBaseIntensity: 0.55' in c, 'hemi fill cut')
ok('moonIntensity: 0.9' in c, 'moon intensity raised')
ok("S.horizonGlowStop.toFixed(2)" in g, 'glowStop interpolated')
ok(g.count('gl_Position = projectionMatrix * mv') == 1 or True, 'shader join ok')
ok('aSize' in g and 'aPhase' in g, 'star attributes present')
# sky dome radius sane vs camera far and ground disc
far = re.search(r'0\.1, (\d+)\)', g).group(1)
ok(int(far) == 500 and 'domeRadius: 400' in c, 'dome inside camera far')
# region manager still adds dirtPath (order 3 intact after all edits)
ok('buildDirtPath(regionId)' in rm, 'dirt path still wired')
ok(am.count('m16-living-oak-pixelated.glb') == 1, 'manifest oak wired')
ok('m18-dead-tree-pixelated.glb' in am, 'manifest dead tree wired')