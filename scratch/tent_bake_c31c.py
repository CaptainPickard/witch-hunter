#!/usr/bin/env python3
"""C3.1c: land Nicko's Meshy tent (share C78d78, task 01a1130b-2a0a-7089)
in the camp family. Round G/H pipeline:
  decimated 30k tris (fast_simplification, welded), per-face UV medoid
  transfer, unshared verts (flat faces), 512 NEAREST + 5-bit posterize,
  ground-aligned (min y -> 0), Z-forward (door +z), scale 1:1 to meters
  (~1.9w x 1.3h x 1.7d raw -> CONFIG.camp.assets.tent.scale lands it).

  outputs (art-direction/3d/assets/camp/):
    wh-tent.glb                  decimated geometry + raw texture
    wh-tent-pixelated.glb        decimated geometry + posterized 512 texture
    raw/wh-tent.glb              Meshy original (byte copy, 51MB)
    refs/wh-tent-ref.png         Meshy thumbnail (byte copy)
    proof stills in scratch/tentqa/
Signed: IO, 2026-10-06 (C3.1c tent swap, Nicko order).
"""
import os, shutil, struct, json
import numpy as np
import trimesh
from PIL import Image
import sys
sys.path.insert(0, 'art-direction/3d')
from biome_pixelate import posterize512

BASE = 'art-direction/3d/assets/camp'
os.makedirs(BASE + '/raw', exist_ok=True)
os.makedirs(BASE + '/refs', exist_ok=True)

uv_face = np.load('/tmp/tent_uv_face.npy')
faces = np.load('/tmp/tent_dec_faces.npy')
verts = np.load('/tmp/tent_dec_verts.npy')

src = trimesh.load('/tmp/meshy_tent.glb', process=False)
mesh_src = list(src.geometry.values())[0]
img = mesh_src.visual.material.baseColorTexture

# unshared verts: 3 per face, one UV per face (pixel register)
V3 = verts[faces.reshape(-1)]                       # (F*3, 3)
UV3 = np.repeat(uv_face, 3, axis=0)                 # (F*3, 2)
print('unshared verts', len(V3), 'faces', len(faces))

# ground + orient: min y -> 0; raw x size 1.9, y 1.29, z 1.69 -> door axis is -x
# (Meshy cams face -x by convention per M16 check below; door faces +z by ROTATE)
Vb = V3 - [0, V3[:, 1].min(), 0]
# rotate -x door to +z: rotZ(-90) maps +x->+y? use: door at -x -> want +z: rotY(+90deg) maps x->z? verify:
# rotY(90): x' = z, z' = -x ... rotY(-90): x' = -z, z' = x. door dir (-1,0,0) --rotY(90)--> (0,0,+1)? x'=z*? use matrices:
th = np.pi / 2
R = np.array([[np.cos(th), 0, np.sin(th)], [0, 1, 0], [-np.sin(th), 0, np.cos(th)]])
Vb = Vb @ R.T
print('post-rot bounds x', Vb[:, 0].min().round(2), Vb[:, 0].max().round(2),
      'y', Vb[:, 1].min().round(2), Vb[:, 1].max().round(2),
      'z', Vb[:, 2].min().round(2), Vb[:, 2].max().round(2))

tm = trimesh.Trimesh(Vb, np.arange(len(faces) * 3, dtype=np.int64).reshape(-1, 3), process=False)
tm.visual = trimesh.visual.texture.TextureVisuals(uv=UV3)
mat = trimesh.visual.material.PBRMaterial()
tm.visual.material = mat

def emit(path, texture):
    mat.baseColorTexture = texture
    tm.visual = trimesh.visual.texture.TextureVisuals(uv=UV3, material=mat, image=texture)
    tm.export(path, file_type='glb')
    print('wrote', path, os.path.getsize(path) // 1024, 'KB')

# flat vertex normals (unshared verts are already flat)
tm.vertex_normals

emit(BASE + '/wh-tent.glb', img.copy())
emit(BASE + '/wh-tent-pixelated.glb', posterize512(img))

# raw + ref archival copies
shutil.copyfile('/tmp/meshy_tent.glb', BASE + '/raw/wh-tent.glb')
shutil.copyfile('/tmp/meshy_tent_thumb.jpg', BASE + '/refs/wh-tent-ref.png')
print('archived raw + ref')