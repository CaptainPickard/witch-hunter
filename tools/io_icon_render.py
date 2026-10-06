#!/usr/local/bin/python3
"""AB1 icon lane (IO): render item GLBs to 48x48 pixel-register icons.

Pattern of proven scratch/tree_ortho.py (painter 2D projection, per-face
texture sampling), adapted: 3/4 yaw view, transparent background, no
annotations, 512 render -> NEAREST 48 -> 5-bit posterize.

Usage: /usr/local/bin/python3 tools/io_icon_render.py  (from repo root)
"""
import os, sys
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from PIL import Image

ROOT = '/tmp/wh-worldfeat'
REC = 512          # icon render size (square)
OUT = 48           # final HUD size
LEVELS = 32        # 5 bits per channel

# (config id, glb path, yaw 3/4 view, zoom >1 fills frame, screen rollDeg)
# Round 2 (QA pivot): NON-pixelated GLB sources - their smooth texture
# atlases centroid-sample far stabler than the posterized ones at 48px.
# Screen roll lays blades/shafts diagonal to fill the square (RPG icon read).
ITEMS = [
    ('roundShield', 'art-direction/3d/assets/weapons/round-shield.glb', 25, 1.25, 0),
    ('longsword',   'art-direction/3d/assets/weapons/longsword.glb',   -25, 1.35, 40),
    ('torch',       'art-direction/3d/assets/weapons/torch.glb',        20, 1.3, 20),
]

AMBER_BOOST = {'torch': True}   # brighten amber-hue faces (flame must read)

def face_colors(m, glb):
    """tree_ortho: per-face sRGB from texture at UV centroid."""
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

def posterize(img):
    a = np.asarray(img.convert('RGBA')).astype(float)
    rgb = np.round(a[..., :3] / 255.0 * (LEVELS - 1)) / (LEVELS - 1) * 255.0
    out = a.copy()
    out[..., :3] = rgb
    return Image.fromarray(out.astype(np.uint8), 'RGBA')

def render_icon(mesh, cols, out_path, yaw_deg, zoom, roll_deg=0,
                amber_boost=False):
    yaw = np.radians(yaw_deg)
    c, s = np.cos(yaw), np.sin(yaw)
    R = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    tri = mesh.triangles @ R.T                 # rotate verts (yaw about Y)
    fn = mesh.face_normals @ R.T
    cols = cols.copy()
    if amber_boost:
        # saturate amber/orange faces (torch flame must read at 48px)
        mx = cols.max(axis=1)
        mn = cols.min(axis=1)
        sat = mx - mn
        amber = (cols[:, 0] > 0.35) & (cols[:, 0] > cols[:, 2] * 1.6) & (sat > 0.12)
        cols[amber] = np.clip(cols[amber] * np.array([1.35, 1.1, 0.55]), 0, 1)
    # screen-space roll about Z so blades/shafts lie diagonal
    if roll_deg:
        rr = np.radians(roll_deg)
        cr, sr = np.cos(rr), np.sin(rr)
        Rz = np.array([[cr, -sr, 0], [sr, cr, 0], [0, 0, 1]])
        tri = tri @ Rz.T
        fn = fn @ Rz.T
    sx, sy, depth = tri[:, :, 0], tri[:, :, 1], tri[:, :, 2].mean(1)
    cam = np.array([0, 0, 1.0])
    light = cam * 0.6 + np.array([0, 0.8, 0])
    light /= np.linalg.norm(light)
    shade = 0.7 + 0.3 * np.abs(fn @ light)     # mostly flat, hint of form
    fc = np.clip(cols * shade[:, None] * 1.3, 0, 1)
    order = np.argsort(depth)
    polys = np.stack([sx, sy], axis=-1)[order]

    b0 = tri.reshape(-1, 3).min(axis=0)
    b1 = tri.reshape(-1, 3).max(axis=0)
    cx = (b0[0] + b1[0]) / 2
    cy = (b0[1] + b1[1]) / 2
    r = max(b1[0] - b0[0], b1[1] - b0[1]) / 2 / zoom
    if r <= 0:
        r = 1.0

    fig = plt.figure(figsize=(REC / 100, REC / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.add_collection(PolyCollection(polys, facecolors=fc[order],
                                     edgecolors=fc[order], linewidths=0.15))
    ax.set_xlim(cx - r, cx + r)
    ax.set_ylim(cy - r, cy + r)
    ax.set_aspect('equal')
    ax.set_axis_off()
    fig.savefig(out_path, transparent=True)
    plt.close(fig)

def pixelize(src512, dst48):
    im = Image.open(src512).convert('RGBA')
    im = im.resize((OUT, OUT), Image.NEAREST)
    im = posterize(im)
    im.save(dst48)

def main():
    tmp = os.path.join(ROOT, 'scratch', 'io_icons512')
    fin = os.path.join(ROOT, 'prototype', 'js', 'icons')
    os.makedirs(tmp, exist_ok=True)
    os.makedirs(fin, exist_ok=True)
    for icon_id, rel, yaw, zoom, roll in ITEMS:
        glb = os.path.join(ROOT, rel)
        m = trimesh.load(glb, force='mesh', process=False)
        cols = face_colors(m, glb)
        p512 = os.path.join(tmp, f'{icon_id}.png')
        render_icon(m, cols, p512, yaw, zoom, roll_deg=roll,
                    amber_boost=AMBER_BOOST.get(icon_id, False))
        pixelize(p512, os.path.join(fin, f'{icon_id}.png'))
        print('icon', icon_id, 'ok')

if __name__ == '__main__':
    main()