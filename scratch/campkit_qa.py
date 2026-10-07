#!/usr/bin/env python3
"""Campkit QA sheet + 3-angle proof stills + underside probe (2026-10-07).
Clone of the torch_qa / tree_ortho pattern:
  - ortho front / side / top of wh-campkit-pixelated.glb (per-face texel color)
  - three azimuth proof angles 0/120/240 with 35-deg elevation (Round J probe)
  - pit close-up + amber accent area (ONE accent law)
  - 512 atlas panel + NEAREST zoom
  - static geometry probe: down-facing faces above ground (underside law)
Written to scratch/campkitqa/: campkit-qa-sheet.png, campkit-qa.json,
proof-000.png, proof-120.png, proof-240.png, underside.json
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

OUT = 'scratch/campkitqa'
SRC = 'art-direction/3d/assets/camp/wh-campkit-pixelated.glb'
os.makedirs(OUT, exist_ok=True)

scene = trimesh.load(SRC)
parts, cols, node = [], [], []
for nm, gm in scene.geometry.items():
    parts.append(gm); cols.append(face_colors(gm)); node += [nm] * len(gm.faces)
m = trimesh.util.concatenate(parts)
cols = np.vstack(cols); node = np.array(node)
print('scene faces', len(m.faces), 'nodes', {n: int((node == n).sum()) for n in set(node)})

AMBER_HUE = (15 / 360, 50 / 360)
AMBER_MIN_S = 0.50
AMBER_MIN_V = 0.40

def project(tri, view):
    if view == 'front':
        return tri[:, :, 0], tri[:, :, 1], tri[:, :, 2].mean(1)
    if view == 'side':
        return -tri[:, :, 2], tri[:, :, 1], tri[:, :, 0].mean(1)
    if view == 'top':
        return tri[:, :, 0], -tri[:, :, 2], tri[:, :, 1].mean(1)
    raise ValueError(view)

def draw(ax, tric, view, title, lightdir=None):
    tri = tric
    if view == 'front':
        S, Y, D = tri[:, :, 0], tri[:, :, 1], tri[:, :, 2].mean(1)
        L = np.array([0, 0, 1.0])
    elif view == 'side':
        S, Y, D = -tri[:, :, 2], tri[:, :, 1], tri[:, :, 0].mean(1)
        L = np.array([1.0, 0, 0])
    elif view == 'top':
        S, Y, D = tri[:, :, 0], -tri[:, :, 2], tri[:, :, 1].mean(1)
        L = np.array([0, 1.0, 0])
    else:
        az, el = view
        a = np.deg2rad(az); c, s = np.cos(a), np.sin(a)
        R = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
        V = np.einsum('ij,fkj->fki', R, tri)
        e = np.deg2rad(el)
        S = V[:, :, 0]
        Y = V[:, :, 1] * np.cos(e) - V[:, :, 2] * np.sin(e)
        D = (V[:, :, 1] * np.sin(e) + V[:, :, 2] * np.cos(e)).mean(axis=1)
        L = R @ np.array([0, 0, 1.0])
    light = (L * 0.55 + np.array([0, 0.85, 0]))
    light = light / np.linalg.norm(light)
    shade = 0.5 + 0.5 * np.abs(np.asarray(m.face_normals) @ light)
    fc = np.clip(cols * shade[:, None] * 1.3, 0, 1)
    o = np.argsort(D)
    polys = np.stack([S, Y], axis=-1)[o]
    ax.add_collection(PolyCollection(polys, facecolors=fc[o], edgecolors=fc[o], linewidths=0.12))
    xs, ys = polys[..., 0], polys[..., 1]
    ax.set_xlim(xs.min() - 0.1, xs.max() + 0.1)
    ax.set_ylim(ys.min() - 0.1, ys.max() + 0.1)
    ax.set_aspect('equal', adjustable='datalim')
    ax.set_facecolor('#c8c8c8'); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title, fontsize=10)

tri = np.asarray(m.triangles)

# ---- per-angle proof stills (0/120/240, elev 35) ----
for az in (0, 120, 240):
    fig = plt.figure(figsize=(8, 6), dpi=110)
    ax = fig.add_axes([0, 0, 1, 1])
    draw(ax, tri, (az, 35), f'proof az {az} el 35')
    fig.savefig(f'{OUT}/proof-{az:03d}.png', facecolor='#c8c8c8')
    plt.close(fig)
    print('wrote', f'{OUT}/proof-{az:03d}.png')

# ---- amber accent ----
hsv = np.array([colorsys.rgb_to_hsv(*c) for c in cols])
amb = ((hsv[:, 0] >= AMBER_HUE[0]) & (hsv[:, 0] <= AMBER_HUE[1]) &
       (hsv[:, 1] >= AMBER_MIN_S) & (hsv[:, 2] >= AMBER_MIN_V))
area = m.area_faces
amb_area = float(area[amb].sum() / area.sum())
amb_nodes = {n: float(area[amb & (node == n)].sum() / max(area[amb].sum(), 1e-9)) for n in set(node)}
lum = cols @ np.array([0.299, 0.587, 0.114])
rest = ~amb
rest_mean = (cols[rest] * area[rest, None]).sum(0) / area[rest].sum() * 255
sat = hsv[:, 1]

# ---- atlas + zoom ----
tex = trimesh.load(SRC, force='mesh').visual.material.baseColorTexture
arr = np.asarray(tex.convert('RGB'))
five = bool(all((arr[..., c] & 7 == 0).all() for c in range(3)))
yy, xx = np.where((arr[..., 0].astype(int) - arr[..., 2]) > 30)
zoom = (48, 48, 0, 0)
if len(yy):
    y0 = int(np.clip(yy.min() - 24, 0, arr.shape[0] - 48)); x0 = int(np.clip(xx.min() - 24, 0, arr.shape[1] - 48))
    zoom = (y0, x0, 48, 48)

# ---- underside probe: down-facing faces above ground ----
fn = np.asarray(m.face_normals)
downy = fn[:, 1] < -0.5
fcy = np.asarray(m.triangles_center)[:, 1]
low_vis = downy & (fcy > 0.05)
underside = {'down_faces_total': int(downy.sum()),
             'down_faces_above_0.05m': int(low_vis.sum()),
             'down_faces_above_0.05m_area_pct': round(float(area[low_vis].sum() / area.sum() * 100), 3)}
if low_vis.sum():
    c = np.asarray(m.triangles_center)[low_vis]
    underside['samples'] = c[np.argsort(-c[:, 1])][:10].round(3).tolist()

# ---- QA sheet ----
fig = plt.figure(figsize=(17, 9), dpi=100, facecolor='#e8e8e8')
gs = fig.add_gridspec(2, 5, left=0.02, right=0.99, top=0.86, bottom=0.02)
ax = fig.add_subplot(gs[:, 0]); draw(ax, tri, 'front', 'front (+Z)')
ax = fig.add_subplot(gs[:, 1]); draw(ax, tri, 'side', 'side (+X)')
ax = fig.add_subplot(gs[0, 2]); draw(ax, tri, 'top', 'top')
ax = fig.add_subplot(gs[0, 3])
acc = np.where(amb[:, None], np.array([1.0, 0.6, 0.2]), np.array([0.28, 0.28, 0.28]))
# amber map on the top view: where is the accent on the ground plane
tri2 = tri.copy()
save_cols = cols
cols_override = acc
def draw_acc(ax, view, title):
    S, Y, D = project(tri, view)
    o = np.argsort(D)
    polys = np.stack([S, Y], axis=-1)[o]
    ao = acc[o]
    ax.add_collection(PolyCollection(polys, facecolors=ao, edgecolors=ao, linewidths=0.12))
    xs, ys = polys[..., 0], polys[..., 1]
    ax.set_xlim(xs.min() - 0.1, xs.max() + 0.1); ax.set_ylim(ys.min() - 0.1, ys.max() + 0.1)
    ax.set_aspect('equal', adjustable='datalim')
    ax.set_facecolor('#c8c8c8'); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title, fontsize=10)
draw_acc(ax, 'top', f'accent map (amber faces) {amb_area * 100:.2f}% area')
ax = fig.add_subplot(gs[0, 4])
ax.imshow(arr, interpolation='nearest'); ax.set_xticks([]); ax.set_yticks([])
ax.set_title(f'atlas {tex.size[0]}x{tex.size[1]} 5-bit={five}', fontsize=10)
ax = fig.add_subplot(gs[1, 2])
fy = np.asarray(m.triangles_center)[:, 1]
keep = np.asarray(m.triangles_center)[:, 0] > 0.75
sub = tri[keep]
if keep.any():
    S2 = sub[:, :, 0]; Y2 = -sub[:, :, 2]
    o = np.argsort(sub[:, :, 1].mean(1))
    polys = np.stack([S2, Y2], axis=-1)[o]
    ao = acc[keep][o]
    ax.add_collection(PolyCollection(polys, facecolors=ao, edgecolors=ao, linewidths=0.2))
    xs, ys = polys[..., 0], polys[..., 1]
    ax.set_xlim(xs.min() - 0.05, xs.max() + 0.05); ax.set_ylim(ys.min() - 0.05, ys.max() + 0.05)
    ax.set_aspect('equal', adjustable='datalim')
ax.set_facecolor('#c8c8c8'); ax.set_xticks([]); ax.set_yticks([])
ax.set_title('pit close-up (x>0.75, top)', fontsize=10)
ax = fig.add_subplot(gs[1, 3])
if len(yy):
    ax.imshow(arr[zoom[0]:zoom[0] + 48, zoom[1]:zoom[1] + 48], interpolation='nearest')
ax.set_xticks([]); ax.set_yticks([]); ax.set_title('NEAREST zoom 48x48 (warmest)', fontsize=10)
ax = fig.add_subplot(gs[1, 4])
ax.imshow(arr[256 - 24:256 + 24, 256 - 24:256 + 24], interpolation='nearest')
ax.set_xticks([]); ax.set_yticks([]); ax.set_title('NEAREST zoom @ atlas centre', fontsize=10)
fig.text(0.01, 0.99, '\n'.join([
    'wh-campkit-pixelated.glb',
    f"faces {len(m.faces)}  nodes " + ' '.join(f'{n}:{int((node == n).sum())}' for n in ('tent', 'bedroll', 'firepit', 'pegs')),
    f"kit bounds x {m.bounds[0][0]:+.2f}..{m.bounds[1][0]:+.2f}  y {m.bounds[0][1]:.3f}..{m.bounds[1][1]:.2f}  z {m.bounds[0][2]:+.2f}..{m.bounds[1][2]:+.2f}",
    f'amber accent area {amb_area * 100:.2f}% of faces  by node ' + ' '.join(f'{k}:{v * 100:.0f}%' for k, v in amb_nodes.items()),
    f'non-accent mean RGB {rest_mean.round(0).astype(int).tolist()}  mean sat {sat[rest].mean() * 100:.0f}%',
    f'underside probe: {underside["down_faces_above_0.05m"]} down-facing faces above 0.05 m ({underside["down_faces_above_0.05m_area_pct"]}% area)',
]), va='top', family='monospace', fontsize=9)
fig.savefig(f'{OUT}/campkit-qa-sheet.png', facecolor=fig.get_facecolor())
plt.close(fig)
print('wrote', f'{OUT}/campkit-qa-sheet.png')

rep = {'faces': int(len(m.faces)),
       'tris_by_node': {n: int((node == n).sum()) for n in ('tent', 'bedroll', 'firepit', 'pegs')},
       'bounds': [[round(float(v), 3) for v in r] for r in m.bounds],
       'tex': list(tex.size), 'five_bit': five,
       'amber_area_pct': round(amb_area * 100, 3),
       'amber_area_by_node_pct': {k2: round(v2 * 100, 1) for k2, v2 in amb_nodes.items()},
       'non_accent_mean_rgb': [int(v) for v in rest_mean.round(0)],
       'non_accent_mean_sat_pct': round(float(sat[rest].mean() * 100), 1),
       'underside': underside}
json.dump(rep, open(f'{OUT}/campkit-qa.json', 'w'), indent=1)
json.dump(underside, open(f'{OUT}/underside.json', 'w'), indent=1)
print(json.dumps(rep))