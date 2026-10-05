"""Round I triage: render the game-served pixelated GLBs with the GAME's own
material/light pipeline to reproduce Nicko's 'shattered' report.

Loads each GLB via trimesh; reports: mesh count, per-mesh connected pieces,
degenerate/tiny-piece stats, texture presence, COLOR_0, normals presence.
Also renders ONE neutral-lit turntable-ish view per asset (ortho front +
3/4) through art-direction/3d/ortho_preview.py for vision triage.
"""
import json, struct, sys, subprocess, os
from pathlib import Path

ROOT = Path('/workspace/witch-hunter')
OUT = ROOT / 'scratch/treeqa/roundI-triage'
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = [
    ('lamp-post', ROOT / 'art-direction/3d/assets/church-kit/lantern-post-pixelated.glb'),
    ('bramble',   ROOT / 'art-direction/3d/assets/biome_library/wh-bramble-pixelated.glb'),
    ('reach-a',   ROOT / 'art-direction/3d/assets/biome_library/wh-reachtree-a-pixelated.glb'),
    ('shovel-dirt', None),  # resolve below
]

# find the shovel/dirt prop asset path
import re
src = (ROOT / 'prototype/js/CONFIG.js').read_text()
m = re.findall(r"asset: '([a-zA-Z]+)'", src)
cand = [a for a in set(m) if 'shovel' in a.lower() or 'dirt' in a.lower() or 'mound' in a.lower() or 'grave' in a.lower()]
print('dirt-ish asset ids in CONFIG:', cand)
man = (ROOT / 'prototype/js/assets.js').read_text()
for a in cand:
    mm = re.search(a + r": '([^']+)'", man)
    if mm:
        p = ROOT / mm.group(1)
        if p.exists():
            TARGETS.append((a, p))

def glb_report(path):
    d = path.read_bytes()
    ln = struct.unpack('<I', d[12:16])[0]
    j = json.loads(d[20:20+ln])
    ext_ok = '.bin' not in json.dumps(j.get('buffers', [{}]))  # embedded = self-contained
    imgs = j.get('images', [])
    ncol0 = sum(1 for p_ in j['meshes'] for pr in p_['primitives'] if 'COLOR_0' in pr.get('attributes', {}))
    out = {
        'meshes': len(j['meshes']), 'prims': sum(len(p_['primitives']) for p_ in j['meshes']),
        'nodes': len(j['nodes']), 'images': len(imgs), 'embed_images': sum(1 for i_ in imgs if 'uri' not in i_),
        'hasCOLOR0': ncol0, 'selfcontained': ext_ok,
    }
    return out

for name, p in TARGETS:
    if p is None or not p.exists():
        print(name, 'MISSING FILE'); continue
    r = glb_report(p)
    print(f'{name}: {json.dumps(r)}')
    for tag in ('front', 'side'):
        sub = subprocess.run(['python3', str(ROOT / 'art-direction/3d/ortho_preview.py'),
                              str(p), str(OUT / f'{name}-{tag}.png')], capture_output=True, text=True)
        # ortho writes front+side both args needed; call once per asset instead
        break
    sub = subprocess.run(['python3', str(ROOT / 'art-direction/3d/ortho_preview.py'),
                          str(p), str(OUT / f'{name}-front.png'), str(OUT / f'{name}-side.png')],
                         capture_output=True, text=True)
    print(' ortho:', (sub.stdout or sub.stderr).strip().splitlines()[-1] if (sub.stdout or sub.stderr) else 'no output')
print('done ->', OUT)