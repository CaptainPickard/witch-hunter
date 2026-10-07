#!/usr/bin/env python3
"""Campkit probe render: front/top ortho with unit grid + x-window zooms (top view).
Flat-shaded painter renderer cloned from scratch/tree_ortho.py, plus grid overlay.
  campkit_grid.py <glb> <outdir>
"""
import os, sys
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

src, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
m = trimesh.load(src, force='mesh')
tex = m.visual.material.baseColorTexture
arr = np.asarray(tex.convert('RGB')).astype(float) / 255.0
h, w = arr.shape[:2]
uv = np.asarray(m.visual.uv)
fuv = uv[m.faces].mean(axis=1)
px = np.clip((fuv[:, 0] % 1.0 * w).astype(int), 0, w - 1)
py = np.clip(((1 - fuv[:, 1] % 1.0) * h).astype(int), 0, h - 1)
cols = arr[py, px]
tri = np.asarray(m.triangles)
fn = np.asarray(m.face_normals)


def draw(view, out, xlim=None, zwin=None, grid=True):
    if view == 'front':
        S, Y, D = tri[:, :, 0], tri[:, :, 1], tri[:, :, 2].mean(1)
        L = np.array([0, 0, 1.0])
    else:  # top: screen x = X, screen y = -Z (camera looking down -Y)
        S, Y, D = tri[:, :, 0], -tri[:, :, 2], tri[:, :, 1].mean(1)
        L = np.array([0, 1.0, 0])
    light = L * 0.6 + np.array([0, 0.8, 0.3]); light /= np.linalg.norm(light)
    shade = 0.45 + 0.55 * np.abs(fn @ light)
    fc = np.clip(cols * shade[:, None] * 1.45, 0, 1)
    order = np.argsort(D)
    polys = np.stack([S, Y], axis=-1)[order]
    fig = plt.figure(figsize=(13, 9), dpi=110)
    ax = fig.add_axes([0.04, 0.04, 0.94, 0.9])
    ax.add_collection(PolyCollection(polys, facecolors=fc[order], edgecolors=fc[order], linewidths=0.12))
    lo, hi = m.bounds[0], m.bounds[1]
    if view == 'front':
        ax.set_xlim(lo[0] - 0.05, hi[0] + 0.05); ax.set_ylim(lo[1] - 0.05, hi[1] + 0.05)
        ax.set_xlabel('X'); ax.set_ylabel('Y (up)')
    else:
        ax.set_xlim(lo[0] - 0.05, hi[0] + 0.05); ax.set_ylim(-hi[2] - 0.05, -lo[2] + 0.05)
        ax.set_xlabel('X'); ax.set_ylabel('-Z (screen)')
    if grid:
        for gx in np.arange(-1.0, 1.01, 0.1):
            ax.axvline(gx, color='w', lw=0.3, alpha=0.5)
            if abs(gx * 10 - round(gx * 10)) < 1e-6 and round(gx, 1) * 10 % 2 == 0:
                ax.axvline(gx, color='r', lw=0.5, alpha=0.6)
        ax.axhline(0, color='b', lw=0.5, alpha=0.6)
    b = m.bounds
    r = max(b[1] - b[0]) * 0.7
    cx = (b[0,0]+b[1,0])/2; cz = (b[0,2]+b[1,2])/2
    if xlim is not None:
        ax.set_xlim(xlim)
        ax.set_ylim(zwin)   # for top: window on -Z axis, inverted screen
    ax.set_aspect('equal', adjustable='datalim')
    ax.set_facecolor('#9a9a9a')
    ax.set_title(f'{view} {out} faces={len(m.faces)}', fontsize=9)
    fig.savefig(out, dpi=110); plt.close(fig)
    print('wrote', out)


draw('front', os.path.join(outdir, 'front_grid.png'))
draw('top', os.path.join(outdir, 'top_grid.png'))
# top zooms on x windows
for tag, x0, x1 in [('tent', -1.0, -0.30), ('mid', -0.40, 0.20), ('pit', 0.15, 1.00)]:
    draw('top', os.path.join(outdir, f'top_{tag}.png'), xlim=(x0, x1), zwin=(-0.78, 0.78), grid=True)
    draw('front', os.path.join(outdir, f'front_{tag}.png'), xlim=(x0, x1), zwin=None, grid=True)