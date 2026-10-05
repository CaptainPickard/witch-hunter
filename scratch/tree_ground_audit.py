#!/usr/bin/env python3
"""Tree ground-contact audit: ymin/ext per tree GLB in use + CONFIG y-sinks."""
import trimesh, numpy as np, re

FILES = {
    'm5 yew':        '/tmp/wh-worldfeat/art-direction/3d/assets/biome_library/m5-pixelated.glb',
    'm16 oak':       '/tmp/wh-worldfeat/art-direction/3d/assets/biome_library/m16-living-oak-pixelated.glb',
    'm17 witchwood': '/tmp/wh-worldfeat/art-direction/3d/assets/biome_library/m17-witchwood-pixelated.glb',
    'm18 deadtree':  '/tmp/wh-worldfeat/art-direction/3d/assets/biome_library/m18-dead-tree-pixelated.glb',
    'm19 ash':       '/tmp/wh-worldfeat/art-direction/3d/assets/biome_library/m19-birch-pixelated.glb',
}
for label, path in FILES.items():
    try:
        m = trimesh.load(path, force='mesh')
        ext = m.bounds[1] - m.bounds[0]
        print(f"{label:14s} ymin={m.bounds[0][1]: .3f} ymax={m.bounds[1][1]: .3f} "
              f"extY={ext[1]:.2f} extXZ={ext[0]:.2f}/{ext[2]:.2f}")
    except Exception as e:
        print(label, 'ERR', e)

cfg = open('/tmp/wh-worldfeat/prototype/js/CONFIG.js').read()
print()
print("--- every tree row with y != 0 or missing y ---")
for m in re.finditer(r"\{ asset: '(yewTree|livingOak|witchwoodTree|deadTree|youngAsh)', x: (-?[\d.]+), y: (-?[\d.]+), z: (-?[\d.]+)[^}]*scale: ([\d.]+) \}", cfg):
    asset, x, y, z, sc = m.groups()
    if abs(float(y)) > 0.001:
        print(f"{asset:14s} y={y:>7s} scale={sc}  @({x},{z})")
print("--- tree rows WITHOUT y field (default 0 = groundAlign rest) ---")
n = 0
for line in cfg.splitlines():
    if re.search(r"asset: '(yewTree|livingOak|witchwoodTree|deadTree|youngAsh)'", line) and 'y:' not in line:
        print(line.strip()); n += 1
print('no-y rows:', n)