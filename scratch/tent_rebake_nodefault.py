#!/usr/bin/env python3
"""C3.1c re-bake: door already faces +Z in raw Meshy space -> NO rotation,
identity orientation. Everything else unchanged (30k decimated, per-face UV
medoid, unshared flat verts, 512+5bit, ground-align).
Signed: IO, 2026-10-06.
"""
import os, shutil
import numpy as np
import trimesh
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

V3 = verts[faces.reshape(-1)]
UV3 = np.repeat(uv_face, 3, axis=0)
Vb = V3 - [0, V3[:, 1].min(), 0]      # ground: min y -> 0 (door faces +Z untouched)

tm = trimesh.Trimesh(Vb, np.arange(len(faces) * 3, dtype=np.int64).reshape(-1, 3), process=False)
tm.vertex_normals                      # flat normals on unshared verts
mat = trimesh.visual.material.PBRMaterial()

def emit(path, texture):
    mat.baseColorTexture = texture
    tm.visual = trimesh.visual.texture.TextureVisuals(uv=UV3, material=mat, image=texture)
    tm.export(path, file_type='glb')
    print('wrote', path, os.path.getsize(path) // 1024, 'KB')

emit(BASE + '/wh-tent.glb', img.copy())
emit(BASE + '/wh-tent-pixelated.glb', posterize512(img))
shutil.copyfile('/tmp/meshy_tent.glb', BASE + '/raw/wh-tent.glb')
shutil.copyfile('/tmp/meshy_tent_thumb.jpg', BASE + '/refs/wh-tent-ref.png')
print('bounds x', Vb[:,0].min().round(2), Vb[:,0].max().round(2),
      'y', Vb[:,1].min().round(2), Vb[:,1].max().round(2),
      'z', Vb[:,2].min().round(2), Vb[:,2].max().round(2))