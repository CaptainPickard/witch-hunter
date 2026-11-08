#!/usr/bin/env python3
"""Bake the curved dagger (A3) with the m5 bake law (v3 discipline), adapted from
scratch/torch_bake.py: raw mesh AS-IS, normals kept/injected, color pixelation
only (512px NEAREST + 5-bit posterize); reuses biome_pixelate.py's
posterize512/export verbatim. Input is the already-normalized dagger-curved.glb
(scratch/dagger_normalize.py), so this script never writes the raw GLB.

  dagger_bake.py <concept.png> [--force]
Writes weapons/dagger-curved-ref.png (concept downscaled to 512 LANCZOS) and
weapons/dagger-curved-pixelated.glb. Stock dagger.glb / dagger-pixelated.glb
are never opened.
"""
import os, sys, json, struct
import trimesh
from PIL import Image
sys.path.insert(0, 'art-direction/3d')
from biome_pixelate import posterize512, export

OUT = 'art-direction/3d/assets/weapons'
MID = 'dagger-curved'
concept = sys.argv[1]
raw = os.path.join(OUT, MID + '.glb')
ref_out = os.path.join(OUT, MID + '-ref.png')
pix_out = os.path.join(OUT, MID + '-pixelated.glb')
for p in (ref_out, pix_out):
    if os.path.exists(p) and '--force' not in sys.argv:
        sys.exit(f'refusing to overwrite existing {p}')
im = Image.open(concept).convert('RGB')
im.resize((512, 512 * im.height // im.width), Image.LANCZOS).save(ref_out, optimize=True)
scene = trimesh.load(raw)
assert len(scene.geometry) == 1, f'expected 1 geometry, got {len(scene.geometry)}'
mesh = list(scene.geometry.values())[0]
img = mesh.visual.material.baseColorTexture
export(pix_out, mesh, posterize512(img))
b = open(pix_out, 'rb').read(); jl = struct.unpack('<I', b[12:16])[0]
attrs = json.loads(b[20:20 + jl])['meshes'][0]['primitives'][0]['attributes']
assert 'NORMAL' in attrs, 'pixelated GLB lost NORMAL'
px = trimesh.load(pix_out); pm = list(px.geometry.values())[0]
print(MID, 'faces', len(mesh.faces), '->', len(pm.faces), 'tex', img.size, '->',
      pm.visual.material.baseColorTexture.size, 'attrs', sorted(attrs),
      'bounds', px.bounds.round(4).tolist(),
      'raw', os.path.getsize(raw) // 1024, 'KB, pixelated', os.path.getsize(pix_out) // 1024, 'KB')
