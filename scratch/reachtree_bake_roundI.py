#!/usr/bin/env python3
"""Round I: land the three Meshy reach-tree variants in biome_library via the TEXTURE path.

scratch/bramble_bake_roundH.py adapted for three variants. Each raw Meshy GLB carries a
baseColor texture. It goes through scratch/decimate_roundI.py (3500-tri budget, --snap tip
reattach, per-face UV transfer), then biome_pixelate.posterize512 (512 NEAREST + 5-bit) + export.
Per variant v in a/b/c:
  raw/wh-reachtree-<v>.glb          Meshy original, byte copy
  refs/wh-reachtree-<v>-ref.png     Meshy t2i ref (unmatted), byte copy
  wh-reachtree-<v>.glb              decimated geometry + raw texture
  wh-reachtree-<v>-pixelated.glb    decimated geometry + posterized 512 texture
  reachtree_bake_roundI.py [a b c]
Signed: Claude Code (Round I), 2026-10-05.
"""
import os, shutil, subprocess, sys
import trimesh
sys.path.insert(0, 'art-direction/3d')
from biome_pixelate import posterize512, export, OUT

for v in (sys.argv[1:] or ['a', 'b', 'c']):
    RAW = f'scratch/treegen/roundI/wh-reachtree-{v}-meshy.glb'
    REF = f'scratch/treegen/roundI/wh-reachtree-{v}-ref.png'
    MID = f'wh-reachtree-{v}'
    dec = os.path.join(OUT, MID + '.glb')
    shutil.copyfile(RAW, os.path.join(OUT, 'raw', MID + '.glb'))
    shutil.copyfile(REF, os.path.join(OUT, 'refs', MID + '-ref.png'))
    subprocess.check_call([sys.executable, 'scratch/decimate_roundI.py', RAW, dec, '3500', '--snap'])
    scene = trimesh.load(dec)
    mesh = list(scene.geometry.values())[0]
    img = mesh.visual.material.baseColorTexture
    pix = os.path.join(OUT, MID + '-pixelated.glb')
    # unshared faces -> flat normals; compute here so trimesh writes NORMAL (bramble_bake_roundH.py)
    mesh.vertex_normals
    export(pix, mesh, posterize512(img))
    print(MID, 'faces', len(mesh.faces), 'tex', img.size, 'dec', os.path.getsize(dec) // 1024,
          'KB, pixelated', os.path.getsize(pix) // 1024, 'KB')
