#!/usr/bin/env python3
"""Bake one Meshy tree into biome_library with the m5 bake law (v3 discipline):
raw mesh AS-IS, normals injected, color pixelation only (512px NEAREST + 5-bit
posterize). Reuses biome_pixelate.py's posterize512/export verbatim.

  tree_bake.py <meshy.glb> <id>   e.g. tree_bake.py scratch/treegen/m16-living-oak-meshy.glb m16-living-oak
Writes biome_library/raw/<id>.glb (Meshy original, byte copy),
       biome_library/<id>.glb (raw mesh re-export, same as m5.glb),
       biome_library/<id>-pixelated.glb
"""
import os, sys, shutil
import trimesh
sys.path.insert(0, 'art-direction/3d')
from biome_pixelate import posterize512, export, OUT

src, mid = sys.argv[1], sys.argv[2]
for p in (os.path.join(OUT, 'raw', mid + '.glb'), os.path.join(OUT, mid + '.glb'), os.path.join(OUT, mid + '-pixelated.glb')):
    if os.path.exists(p) and '--force' not in sys.argv:
        sys.exit(f'refusing to overwrite existing {p}')
shutil.copyfile(src, os.path.join(OUT, 'raw', mid + '.glb'))
scene = trimesh.load(src)
assert len(scene.geometry) == 1, f'expected 1 geometry, got {len(scene.geometry)}'
mesh = list(scene.geometry.values())[0]
img = mesh.visual.material.baseColorTexture
raw_out = os.path.join(OUT, mid + '.glb')
mesh.export(raw_out, file_type='glb')
pix_out = os.path.join(OUT, mid + '-pixelated.glb')
export(pix_out, mesh, posterize512(img))
print(mid, 'faces', len(mesh.faces), 'tex', img.size, 'raw', os.path.getsize(raw_out) // 1024, 'KB, pixelated', os.path.getsize(pix_out) // 1024, 'KB')
