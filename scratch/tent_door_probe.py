#!/usr/bin/env python3
"""C3.1c door-axis probe: textured 4-azimuth renders of wh-tent-pixelated.glb.
The door is the azimuth whose view shows the OPENING (dark interior + flaps).
Signed: IO, 2026-10-06.
"""
import numpy as np, trimesh, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

BASE = 'art-direction/3d/assets/camp'
m = trimesh.load(BASE + '/wh-tent-pixelated.glb')
mesh = list(m.geometry.values())[0]
V, F, UV = mesh.vertices, mesh.faces, mesh.visual.uv
tex = np.asarray(mesh.visual.material.baseColorTexture.convert('RGB'))
H, W = tex.shape[:2]
fu = UV[F].mean(axis=1)
tx = np.clip((fu[:,0]*(W-1)).round().astype(int), 0, W-1)
ty = np.clip(((1-fu[:,1])*(H-1)).round().astype(int), 0, H-1)
cols = tex[ty,tx] / 255.0
tri = V[F]
cen = tri.mean(axis=1)

def shade(cols, normals, light):
    lam = np.clip(normals @ light, 0.15, 1.0)[:, None]
    return np.clip(cols * lam, 0, 1)

import trimesh.triangles as tt
normals = tt.normals(np.asarray(tri))[0]
if normals.shape != (len(tri), 3):
    normals = mesh.face_normals

for name, (lx, lz) in {'az0_from+Z': (0, -1), 'az90_from+X': (-1, 0),
                       'az180_from-Z': (0, 1), 'az270_from-X': (1, 0)}.items():
    # ortho project: screen right = perpendicular of light dir, up = Y
    fwd = np.array([-lx, 0, -lz], dtype=float)   # camera looks along -lx, -lz? camera on (lx,0,lz) looking at origin
    right = np.cross([0,1,0], -fwd).astype(float); right /= np.linalg.norm(right)
    depth = tri @ np.array([lx, 0, lz])
    sx = tri @ right
    sy = tri[:,1]
    order = np.argsort(depth)[::-1]        # painter: far first -> depth decreasing? far = largest proj onto cam pos
    # simpler: sort by depth descending (draw far first)
    L = shade(cols, normals, np.array([0.4, 0.8, 0.3]) / np.sqrt(0.16+0.64+0.09))
    fig, ax = plt.subplots(figsize=(5,5))
    poly = np.dstack([sx, sy])[order]
    fc = L[order]
    pc = PolyCollection(poly.reshape(-1, 3, 2), facecolors=fc.reshape(-1, 3), edgecolors='none')
    ax.add_collection(pc)
    ax.set_xlim(-1.3, 1.3); ax.set_ylim(-0.15, 1.45); ax.set_aspect('equal'); ax.set_axis_off()
    p = f'/tmp/tent_door_{name}.png'
    fig.savefig(p, dpi=100, bbox_inches='tight'); plt.close(fig)
    print('wrote', p)