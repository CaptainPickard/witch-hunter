#!/usr/bin/env python3
"""Build the self-contained arsenal-viewer.html from the template.

Inlines: three.js core + OrbitControls + GLTFLoader (extracted from the
spike demo) and every pixelated GLB as a base64 data URI in an ASSETS
manifest. Output: art-direction/3d/arsenal-viewer.html (single file,
no network).
"""
import base64
import json
import re
from pathlib import Path

ROOT = Path('/workspace/witch-hunter')
SPIKE = ROOT / 'art-direction/3d-spike/gravedigger-equip-demo-v2.html'
TPL = ROOT / 'art-direction/3d/arsenal-viewer.template.html'
OUT = ROOT / 'art-direction/3d/arsenal-viewer.html'
ASSETS = ROOT / 'art-direction/3d/assets'

# 1. extract the three libraries from the spike demo (index-based slicing)
spike = SPIKE.read_text()
i = spike.find('<script>/**')
j = spike.find('</script>', i) + len('</script>')
three_core = spike[i+len('<script>'):j-len('</script>')]
k = spike.find('<script>', j)
l = spike.find('</script>', k) + len('</script>')
orbit = spike[k+len('<script>'):l-len('</script>')]
g = spike.find('<script>', l)
ge = spike.find('</script>', g) + len('</script>')
gltf = spike[g+len('<script>'):ge-len('</script>')]
assert 'Three.js Authors' in three_core, 'three core not found'
assert 'THREE.OrbitControls = OrbitControls' in orbit, 'orbit controls not found'
assert 'THREE.GLTFLoader = GLTFLoader' in gltf, 'gltf loader not found'

# 2. build ASSETS registry with base64 pixelated GLBs
# cat = the category the UI selects filter on; slots = equip destinations
CATS = {'races': 'races', 'weapons': 'weapons', 'armor': 'armor', 'church-kit': 'props', 'graveyard': 'props', 'crypt': 'props'}
HEAD_PIECES = {'light-court-helm', 'dark-court-helm', 'shadow-court-hood'}
CHEST_PIECES = {'light-court-chest', 'dark-court-breastplate', 'undead-husk-armor'}
HAND_PIECES = {'longsword', 'greatsword', 'hand-axe', 'war-mace', 'halberd', 'dagger',
               'hunting-bow', 'round-shield', 'tower-shield', 'buckler', 'gravedigger-lantern'}

entries = {}
for cat_dir in sorted(ASSETS.iterdir()):
    if not cat_dir.is_dir():
        continue
    for glb in sorted(cat_dir.glob('*.glb')):
        if glb.name.endswith('-pixelated.glb'):
            name = glb.name[:-len('-pixelated.glb')]
            e = entries.setdefault(name, {'cat': CATS[cat_dir.name]})
            e['url'] = 'data:model/gltf-binary;base64,' + base64.b64encode(glb.read_bytes()).decode()
            slot = []
            if name in HEAD_PIECES: slot.append('head')
            if name in CHEST_PIECES: slot.append('chest')
            if name in HAND_PIECES: slot.append('rh'); slot.append('lh')
            if cat_dir.name == 'races': slot.append('body')
            e['slots'] = slot

assets_js = 'var ASSETS = ' + json.dumps(entries) + ';'

# 3. assemble: template with the three placeholders + assets registry
tpl = TPL.read_text()
html = tpl.replace('/*THREE_JS_PLACEHOLDER*/', three_core)
html = html.replace('/*ORBIT_CONTROLS_PLACEHOLDER*/', orbit)
html = html.replace('/*GLTF_LOADER_PLACEHOLDER*/', gltf)
# inject ASSETS right before the btnLH handler (function refs in same script scope)
anchor = "document.getElementById('btnLH').onclick"
idx = html.find(anchor)
assert idx > 0, 'btnLH handler not found in template'
html = html[:idx] + assets_js + '\n\n' + html[idx:]
# append the select population calls at the very end of the main script
fill_calls = '''
// populate selects (runs after fillSelect is defined)
fillSelect("selBody", ["races"]);
fillSelect("selHead", ["armor"]);
fillSelect("selChest", ["armor"]);
fillSelect("selRH", ["weapons"]);
fillSelect("selLH", ["weapons"]);
</script></body>'''
html = html.replace('</script>\n</body></html>', fill_calls.replace('</script></body>', '</script>\n</body></html>'), 1)
OUT.write_text(html)
size_mb = OUT.stat().st_size / 1e6
print(f'built {OUT} ({size_mb:.1f} MB, {len(entries)} assets)')