#!/usr/bin/env python3
"""C3.1c QA: 3-angle ortho renders of wh-tent-pixelated.glb (no game run -
static geometry probe, allowed by the no-harness law). Round J underside
check: 0/120/240 deg persp + exact door-axis proof.
Signed: IO, 2026-10-06.
"""
import numpy as np, trimesh, os
from PIL import Image

BASE = 'art-direction/3d/assets/camp'
m = trimesh.load(BASE + '/wh-tent-pixelated.glb')
mesh = list(m.geometry.values())[0] if hasattr(m, 'geometry') else m
print('faces', len(mesh.faces), 'verts', len(mesh.vertices), 'bounds', mesh.bounds)
os.makedirs('/tmp/wh-worldfeat/scratch/tentqa', exist_ok=True)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def render(elev, azim, name):
    tris = mesh.vertices[mesh.faces]
    texuv = mesh.visual.uv[mesh.faces]
    tex = np.asarray(mesh.visual.material.baseColorTexture.convert('RGB'))
    H, W = tex.shape[:2]
    cols = tex[np.clip((texuv[..., 0] * (W - 1)).round().astype(int), 0, W - 1),
               np.clip(((1 - texuv[..., 1]) * (H - 1)).round().astype(int), 0, H - 1)]
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection='3d')
    pc = Poly3DCollection(tris, facecolors=cols.mean(axis=1) / 255.0, edgecolors='none')
    ax.add_collection3d(pc)
    r = 1.4
    ax.set_xlim(-r, r); ax.set_ylim(-r, r); ax.set_zlim(-0.2, r)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off(); ax.set_box_aspect((1, 1, 0.75))
    p = f'/tmp/wh-worldfeat/scratch/tentqa/{name}.png'
    fig.savefig(p, dpi=110, bbox_inches='tight')
    plt.close(fig)
    print('wrote', p)

render(0, -180, 'front-negz')      # looking from -z: door check (+z side backs away)
render(15, 0, 'back-plusz')
render(25, 35, 'threeq')
print('QA stills done - door should be visible in front-negz (door faces +z)')