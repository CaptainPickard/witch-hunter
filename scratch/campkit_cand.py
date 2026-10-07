#!/usr/bin/env python3
"""Rule-candidate renders, this time with the actual texture colors (identifiable)."""
import os, sys
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

src = sys.argv[1]
outdir = sys.argv[2]
os.makedirs(outdir, exist_ok=True)
m = trimesh.load(src, force='mesh')
tex = m.visual.material.baseColorTexture
arr = np.asarray(tex.convert('RGB')).astype(float) / 255.0
H, W = arr.shape[:2]
uv = np.asarray(m.visual.uv)
fuv = uv[m.faces].mean(axis=1)
px = np.clip((fuv[:, 0] % 1.0) * (W - 1), 0, W - 1).astype(int)
py = np.clip((1 - fuv[:, 1] % 1.0) * (H - 1), 0, H - 1).astype(int)
col = arr[py, px]
lum = (col * 255.0) @ np.array([0.299, 0.587, 0.114])
fc = np.asarray(m.triangles_center)


def render_mask(name, sel, views=('front', 'top')):
    sub = m.submesh([np.where(sel)[0]], append=True, repair=False)
    if isinstance(sub, list):
        sub = trimesh.util.concatenate(sub)
    sub.merge_vertices(merge_tex=False, merge_norm=False)
    print(name, 'faces', len(sub.faces))
    if len(sub.faces) == 0:
        print('  EMPTY'); return
    tri = np.asarray(sub.triangles)
    fn = np.asarray(sub.face_normals)
    for view in views:
        if view == 'front':
            S, Y, D = tri[:, :, 0], tri[:, :, 1], tri[:, :, 2].mean(1)
            L = np.array([0, 0, 1.0])
        else:
            S, Y, D = tri[:, :, 0], -tri[:, :, 2], tri[:, :, 1].mean(1)
            L = np.array([0, 1.0, 0])
        light = L * 0.6 + np.array([0, 0.8, 0.3]); light /= np.linalg.norm(light)
        shade = 0.55 + 0.45 * np.abs(fn @ light)
        fc2 = np.clip(col[sel] * shade[:, None] * 1.5, 0, 1)
        o = np.argsort(D)
        polys = np.stack([S, Y], axis=-1)[o]
        fig = plt.figure(figsize=(7, 6), dpi=100)
        ax = fig.add_axes([0.05, 0.05, 0.9, 0.85])
        ax.add_collection(PolyCollection(polys, facecolors=fc2[o], edgecolors=fc2[o], linewidths=0.12))
        ax.set_aspect('equal', adjustable='datalim'); ax.autoscale()
        ax.set_facecolor('#c0c0c0'); ax.set_title(f'{name} {view}', fontsize=9)
        fig.savefig(os.path.join(outdir, f'{name}_{view}.png'), dpi=100); plt.close(fig)
    print('  rendered', name)


canvas = (lum >= 88) & (fc[:, 0] < -0.20)
mouth = (fc[:, 0] > -0.60) & (fc[:, 0] < -0.42) & (fc[:, 1] > -0.17)
midzone = (fc[:, 0] >= -0.05) & (fc[:, 0] <= 0.45) & (fc[:, 1] > -0.38)
pitdisc = ((fc[:, 0] - 0.66) ** 2 + fc[:, 2] ** 2 < 0.32 ** 2) & (fc[:, 1] > -0.40)
render_mask('canvas', canvas)
render_mask('mouth', mouth)
render_mask('midzone', midzone)
render_mask('pitdisc', pitdisc)