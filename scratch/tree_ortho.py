#!/usr/bin/env python3
"""Full-resolution textured orthographic front+side QA render for tree GLBs.

Why not art-direction/3d/ortho_preview.py as-is (out of this mission's edit scope):
  - it decimates meshes > 8000 faces with fast_simplification on the UV-seam-split
    (unwelded) mesh, which itself shreds the silhouette - even intact m5 renders as
    confetti, so it cannot distinguish healthy from shattered trees;
  - its 'side' view rotates about the camera depth axis, i.e. it is the front view
    rolled 90 degrees, not a side elevation.
This renderer: NO decimation, every face drawn, painter-sorted 2D ortho projection,
per-face texture color (sampled at UV centroid) * lambert shade.
  front = camera on +Z looking -Z (screen x=X, y=Y);  side = camera on +X (screen x=-Z, y=Y)

Usage: tree_ortho.py <glb> <front.png> <side.png> [title]
"""
import sys
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection


def face_colors(m):
    tex = getattr(getattr(m.visual, 'material', None), 'baseColorTexture', None)
    uv = getattr(m.visual, 'uv', None)
    if tex is None or uv is None:
        return np.full((len(m.faces), 3), 0.45)
    arr = np.asarray(tex.convert('RGB')).astype(float) / 255.0
    h, w = arr.shape[:2]
    fuv = np.asarray(uv)[m.faces].mean(axis=1)
    px = np.clip((fuv[:, 0] % 1.0 * w).astype(int), 0, w - 1)
    py = np.clip(((1 - fuv[:, 1] % 1.0) * h).astype(int), 0, h - 1)
    return arr[py, px]


def render(m, cols, out, view, title):
    tri = m.triangles
    fn = m.face_normals
    if view == 'front':
        sx, sy, depth, cam = tri[:, :, 0], tri[:, :, 1], tri[:, :, 2].mean(1), np.array([0, 0, 1.0])
    else:
        sx, sy, depth, cam = -tri[:, :, 2], tri[:, :, 1], tri[:, :, 0].mean(1), np.array([1.0, 0, 0])
    light = cam * 0.6 + np.array([0, 0.8, 0])
    light /= np.linalg.norm(light)
    shade = 0.45 + 0.55 * np.abs(fn @ light)          # two-sided (game renders DoubleSide foliage)
    fc = np.clip(cols * shade[:, None] * 1.35, 0, 1)
    order = np.argsort(depth)                          # far first
    polys = np.stack([sx, sy], axis=-1)[order]
    fig = plt.figure(figsize=(6, 8), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.add_collection(PolyCollection(polys, facecolors=fc[order], edgecolors=fc[order], linewidths=0.15))
    b = m.bounds
    r = max(b[1] - b[0]) * 0.62
    cx = 0.0
    cy = (b[0][1] + b[1][1]) / 2
    ax.set_xlim(cx - r, cx + r)
    ax.set_ylim(cy - r * 4 / 3, cy + r * 4 / 3)
    ax.set_aspect('equal')
    ax.axhline(b[0][1], color='#888', lw=0.6)       # ground line at ymin
    ax.set_axis_off()
    ax.text(0.02, 0.98, f'{title} {view}  faces={len(m.faces)}', transform=ax.transAxes,
            va='top', fontsize=9, color='#333')
    fig.savefig(out, facecolor='#c8c8c8')
    plt.close(fig)


def main(src, out_front, out_side, title=''):
    m = trimesh.load(src, force='mesh')
    cols = face_colors(m)
    render(m, cols, out_front, 'front', title)
    render(m, cols, out_side, 'side', title)
    print('saved', out_front, out_side)


if __name__ == '__main__':
    main(*sys.argv[1:5])
