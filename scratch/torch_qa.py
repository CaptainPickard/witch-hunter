#!/usr/bin/env python3
"""Torch asset QA sheet (2026-10-05): ortho front / side / top (scratch/tree_ortho.py
renderer: no decimation, true side + top elevations, per-face texture color),
the 512px posterized atlas shown NEAREST with a zoomed crop (pixelation evident),
and an area-weighted palette check: which faces are the amber accent and where
they sit along the torch height (accent must be the head only).

  torch_qa.py <pixelated.glb> <out_dir>
Writes <out_dir>/torch-qa-sheet.png and <out_dir>/torch-qa.json
"""
import os, sys, json, colorsys
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tree_ortho import face_colors

# amber accent band (HSV): orange-amber hue, saturated, bright enough to read as glow
AMBER_HUE = (15 / 360, 50 / 360)
AMBER_MIN_S = 0.55
AMBER_MIN_V = 0.45


def project(m, view):
    tri = m.triangles
    if view == 'front':    # camera +Z
        return tri[:, :, 0], tri[:, :, 1], tri[:, :, 2].mean(1), np.array([0, 0, 1.0])
    if view == 'side':     # camera +X, screen x = -Z
        return -tri[:, :, 2], tri[:, :, 1], tri[:, :, 0].mean(1), np.array([1.0, 0, 0])
    # top: camera +Y looking down, screen x = X, screen y = -Z
    return tri[:, :, 0], -tri[:, :, 2], tri[:, :, 1].mean(1), np.array([0, 1.0, 0])


def draw(ax, m, cols, view, ylo=None):
    sx, sy, depth, cam = project(m, view)
    if ylo is not None:                           # close-up: keep faces above ylo only
        keep = sy.min(1) >= ylo
        sx, sy, depth, cols, fnm = sx[keep], sy[keep], depth[keep], cols[keep], m.face_normals[keep]
    else:
        fnm = m.face_normals
    light = cam * 0.6 + np.array([0, 0.8, 0.3])
    light /= np.linalg.norm(light)
    shade = 0.45 + 0.55 * np.abs(fnm @ light)
    fc = np.clip(cols * shade[:, None] * 1.35, 0, 1)
    order = np.argsort(depth)
    polys = np.stack([sx, sy], axis=-1)[order]
    ax.add_collection(PolyCollection(polys, facecolors=fc[order], edgecolors=fc[order], linewidths=0.15))
    xs, ys = polys[..., 0], polys[..., 1]
    px, py = (xs.max() - xs.min()) * 0.06 + 0.01, (ys.max() - ys.min()) * 0.04 + 0.01
    ax.set_xlim(xs.min() - px, xs.max() + px)
    ax.set_ylim(ys.min() - py, ys.max() + py)
    ax.set_aspect('equal', adjustable='datalim')
    ax.set_facecolor('#c8c8c8')
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(view, fontsize=10)


def amber_mask(cols):
    hsv = np.array([colorsys.rgb_to_hsv(*c) for c in cols])
    return ((hsv[:, 0] >= AMBER_HUE[0]) & (hsv[:, 0] <= AMBER_HUE[1]) &
            (hsv[:, 1] >= AMBER_MIN_S) & (hsv[:, 2] >= AMBER_MIN_V))


def main(src, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    m = trimesh.load(src, force='mesh')
    cols = face_colors(m)
    tex = m.visual.material.baseColorTexture
    arr = np.asarray(tex.convert('RGB'))
    area = m.area_faces
    amb = amber_mask(cols)
    b = m.bounds
    h = b[1][1] - b[0][1]
    cy = m.triangles_center[:, 1]
    hn = (cy - b[0][1]) / h                       # 0 = butt, 1 = top
    amb_area = float(area[amb].sum() / area.sum())
    amb_hmin = float(hn[amb].min()) if amb.any() else None
    amb_below_head = float(area[amb & (hn < 0.70)].sum() / max(area[amb].sum(), 1e-9))
    lum = cols @ np.array([0.299, 0.587, 0.114])
    rest = ~amb
    rest_mean = (cols[rest] * area[rest, None]).sum(0) / area[rest].sum() * 255
    levels = [int(len(np.unique(arr[..., c]))) for c in range(3)]
    five_bit = bool(all((arr[..., c] & 7 == 0).all() for c in range(3)))

    fig = plt.figure(figsize=(16, 9), dpi=100, facecolor='#e8e8e8')
    gs = fig.add_gridspec(2, 5, height_ratios=[1, 1], left=0.02, right=0.99, top=0.80, bottom=0.02)
    for i, v in enumerate(('front', 'side')):
        ax = fig.add_subplot(gs[:, i])
        draw(ax, m, cols, v)
    ax = fig.add_subplot(gs[0, 2]); draw(ax, m, cols, 'top')
    ax = fig.add_subplot(gs[0, 4]); draw(ax, m, cols, 'front', ylo=b[0][1] + 0.70 * h)
    ax.set_title('head close-up (top 30%, front)', fontsize=10)
    # accent map: amber faces highlighted, everything else grey (front view)
    ax = fig.add_subplot(gs[1, 2])
    acc = np.where(amb[:, None], np.array([1.0, 0.63, 0.25]), np.array([0.25, 0.25, 0.25]))
    draw(ax, m, acc, 'front')
    ax.set_title(f'accent map (amber faces) {amb_area * 100:.1f}% area', fontsize=10)
    ax = fig.add_subplot(gs[0, 3])
    ax.imshow(arr, interpolation='nearest'); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(f'atlas {tex.size[0]}x{tex.size[1]} 5-bit={five_bit}', fontsize=10)
    # zoom: 48x48 texel crop around the brightest amber texel (head), NEAREST
    hsv = np.asarray(tex.convert('HSV')).astype(int)
    score = np.where((hsv[..., 0] > 10) & (hsv[..., 0] < 36) & (hsv[..., 1] > 140), hsv[..., 2], 0)
    yy, xx = np.unravel_index(np.argmax(score), score.shape)
    y0 = int(np.clip(yy - 24, 0, arr.shape[0] - 48)); x0 = int(np.clip(xx - 24, 0, arr.shape[1] - 48))
    ax = fig.add_subplot(gs[1, 3])
    ax.imshow(arr[y0:y0 + 48, x0:x0 + 48], interpolation='nearest'); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(f'NEAREST zoom 48x48 @ ({x0},{y0})', fontsize=10)
    ax = fig.add_subplot(gs[1, 4])
    ax.imshow(arr[256 - 24:256 + 24, 256 - 24:256 + 24], interpolation='nearest')
    ax.set_xticks([]); ax.set_yticks([]); ax.set_title('NEAREST zoom 48x48 @ atlas centre', fontsize=10)
    fig.text(0.01, 0.99, '\n'.join([
        'torch-pixelated.glb',
        f'faces {len(m.faces)}  verts {len(m.vertices)}',
        f'ext X/Y/Z {m.extents[0]:.3f} / {m.extents[1]:.3f} / {m.extents[2]:.3f}',
        f'channel levels R/G/B {levels}',
        f'amber accent area {amb_area * 100:.1f}%',
        f'amber lowest face at {amb_hmin:.2f} of height' if amb_hmin is not None else 'no amber',
        f'amber area below 0.70 h: {amb_below_head * 100:.1f}%',
        f'non-accent mean RGB {rest_mean.round(0).astype(int).tolist()}',
    ]), va='top', family='monospace', fontsize=9)
    out_png = os.path.join(out_dir, 'torch-qa-sheet.png')
    fig.savefig(out_png, facecolor=fig.get_facecolor())
    plt.close(fig)
    rep = {'faces': int(len(m.faces)), 'verts': int(len(m.vertices)),
           'extents': [round(float(e), 4) for e in m.extents],
           'bounds': [[round(float(v), 4) for v in r] for r in b],
           'tex': list(tex.size), 'five_bit': five_bit, 'channel_levels': levels,
           'amber_area_pct': round(amb_area * 100, 2),
           'amber_lowest_face_hnorm': None if amb_hmin is None else round(amb_hmin, 3),
           'amber_area_below_0p70h_pct': round(amb_below_head * 100, 2),
           'non_accent_mean_rgb': [int(v) for v in rest_mean.round(0)]}
    json.dump(rep, open(os.path.join(out_dir, 'torch-qa.json'), 'w'), indent=1)
    print(out_png); print(json.dumps(rep))


if __name__ == '__main__':
    main(*sys.argv[1:3])
