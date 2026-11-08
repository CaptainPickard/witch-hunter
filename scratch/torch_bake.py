#!/usr/bin/env python3
"""Bake the Meshy torch into assets/weapons/ with the m5 bake law (v3 discipline):
raw mesh AS-IS, normals injected, color pixelation only (512px NEAREST + 5-bit
posterize). Same chain as scratch/tree_bake.py; reuses biome_pixelate.py's
posterize512/export verbatim. Weapons-dir naming (like round-shield):

  torch_bake.py <meshy.glb> <ref.png> [--force]
Writes weapons/torch.glb (Meshy original, byte copy), weapons/torch-ref.png
(the exact image sent to Meshy), weapons/torch-pixelated.glb
"""
import os, sys, shutil
import trimesh
sys.path.insert(0, 'art-direction/3d')
from biome_pixelate import posterize512, export

OUT = 'art-direction/3d/assets/weapons'
MID = 'torch'
src, ref = sys.argv[1], sys.argv[2]
raw_out = os.path.join(OUT, MID + '.glb')
ref_out = os.path.join(OUT, MID + '-ref.png')
pix_out = os.path.join(OUT, MID + '-pixelated.glb')
for p in (raw_out, ref_out, pix_out):
    if os.path.exists(p) and '--force' not in sys.argv:
        sys.exit(f'refusing to overwrite existing {p}')
shutil.copyfile(src, raw_out)
shutil.copyfile(ref, ref_out)
scene = trimesh.load(src)
assert len(scene.geometry) == 1, f'expected 1 geometry, got {len(scene.geometry)}'
mesh = list(scene.geometry.values())[0]
img = mesh.visual.material.baseColorTexture
export(pix_out, mesh, posterize512(img))
print(MID, 'faces', len(mesh.faces), 'tex', img.size, 'raw', os.path.getsize(raw_out) // 1024,
      'KB, pixelated', os.path.getsize(pix_out) // 1024, 'KB')
