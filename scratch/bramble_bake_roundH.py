#!/usr/bin/env python3
"""Round H continuation: land the Meshy bramble in biome_library via the TEXTURE path.

The raw Meshy GLB carries a baseColor texture, so this is tree_bake.py's register
treatment (biome_pixelate.posterize512 = 512 NEAREST + 5-bit posterize, plus export with
NORMAL injection). It runs on the decimated mesh from scratch/decimate_roundH.py
(2500-tri budget, per-face UV transfer), not on the 28k-tri raw mesh.
  raw/wh-bramble.glb            Meshy original, byte copy
  refs/wh-bramble-ref.png       Meshy t2i ref, byte copy
  wh-bramble.glb                decimated geometry + raw texture
  wh-bramble-pixelated.glb      decimated geometry + posterized 512 texture
Signed: Claude Code (Round H continuation), 2026-10-05.
"""
import os, shutil, subprocess, sys
import trimesh
sys.path.insert(0, 'art-direction/3d')
from biome_pixelate import posterize512, export, OUT

RAW = 'scratch/treegen/roundH/wh-bramble-meshy.glb'
REF = 'scratch/treegen/roundH/wh-bramble-ref.png'
MID = 'wh-bramble'
dec = os.path.join(OUT, MID + '.glb')
shutil.copyfile(RAW, os.path.join(OUT, 'raw', MID + '.glb'))
shutil.copyfile(REF, os.path.join(OUT, 'refs', MID + '-ref.png'))
subprocess.check_call([sys.executable, 'scratch/decimate_roundH.py', RAW, dec, '2500'])
scene = trimesh.load(dec)
mesh = list(scene.geometry.values())[0]
img = mesh.visual.material.baseColorTexture
pix = os.path.join(OUT, MID + '-pixelated.glb')
# faces are unshared, so these are flat normals. Computing them here makes trimesh write NORMAL;
# export()'s injection fallback misreads this file's index view (IndexError), so it is skipped
mesh.vertex_normals
export(pix, mesh, posterize512(img))
print(MID, 'faces', len(mesh.faces), 'tex', img.size, 'dec', os.path.getsize(dec) // 1024,
      'KB, pixelated', os.path.getsize(pix) // 1024, 'KB')
