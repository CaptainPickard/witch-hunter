#!/usr/bin/env python3
"""Locate amber texel faces in the mesh: where do they sit spatially?
Amber is legal ONLY on the fire pit stones' inner faces (brief)."""
import numpy as np, trimesh
m = trimesh.load('scratch/campkitgen/wh-campkit-meshy-dec30k.glb', force='mesh')
tex = m.visual.material.baseColorTexture
arr = np.asarray(tex.convert('RGB')).astype(float)
H, W = arr.shape[:2]
uv = np.asarray(m.visual.uv)
fuv = uv[m.faces].mean(axis=1)
px = np.clip((fuv[:, 0] % 1.0) * (W - 1), 0, W - 1).astype(int)
py = np.clip((1 - fuv[:, 1] % 1.0) * (H - 1), 0, H - 1).astype(int)
col = arr[py, px]
r, g, b = col[:, 0], col[:, 1], col[:, 2]
amber = (r > 120) & (r > g * 1.35) & (g > b * 1.05) & (g > 45) & (col.max(1) - col.min(1) > 50)
fc = np.asarray(m.triangles_center)
print('amber faces:', int(amber.sum()))
if amber.sum():
    p = fc[amber]
    print('bbox x', p[:, 0].min().round(2), p[:, 0].max().round(2),
          'y', p[:, 1].min().round(2), p[:, 1].max().round(2),
          'z', p[:, 2].min().round(2), p[:, 2].max().round(2))
    print('centroid', p.mean(0).round(2))
    print('dist to pit center (0.66,0):', round(float(np.linalg.norm(p[:, [0, 2]] - [0.66, 0]).mean()), 3))
    # sample atlas coords of amber px
    uus = np.unique(np.stack([px[amber], py[amber]], 1), axis=0)
    print('amber atlas px sample:', uus[:10].tolist(), 'n px', len(uus))
    print('amber colors sample:', col[amber][:5].astype(int).tolist())
# where are they in the ATLAS image (island context): uv bbox
if amber.sum():
    a_uv = fuv[amber]
    print('amber uv u', a_uv[:, 0].min().round(2), a_uv[:, 0].max().round(2),
          'v', a_uv[:, 1].min().round(2), a_uv[:, 1].max().round(2))