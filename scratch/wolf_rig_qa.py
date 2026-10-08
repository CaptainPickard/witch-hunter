#!/usr/bin/env python3
"""Full-size per-clip QA grids for the rigged wolf (WOLF-RIG round, sec. 3).

The tree_ortho.py renderer law: NO decimation, every face drawn, painter-sorted
orthographic projection, per-face texture colour (sampled at the UV centroid)
x lambert shade. Geometry = the GLB's own linear-blend skinning (Rig from
verify_wolf_rig.py), so what is drawn is what ships.

One PNG per clip: 6 frames across (evenly spaced; loops skip the duplicate seam
frame, one-shots include first + last), two rows: SIDE (camera +X, head left)
and FRONT (camera +Z, facing the viewer). Panels are 520 x 460 px each
(3120 x 920 sheet) -- full size, not contact-scale. The grey line = ground
(raw sole height); the panel title carries t, key index and the measured
lowest-vertex height above ground.

    python3 scratch/wolf_rig_qa.py RIGGED.glb OUT_DIR [tag]
"""
import io
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_wolf_rig import Rig, GROUND, SPEC, LOOPS, image_bytes  # noqa: E402

PANEL_W, PANEL_H = 5.2, 4.6


def face_colors(R):
    tex = Image.open(io.BytesIO(image_bytes(R.doc, R.bin))).convert('RGB')
    arr = np.asarray(tex).astype(float) / 255.0
    h, w = arr.shape[:2]
    fuv = R.uv[R.idx].mean(axis=1)
    px = np.clip((fuv[:, 0] % 1.0 * w).astype(int), 0, w - 1)
    py = np.clip((fuv[:, 1] % 1.0 * h).astype(int), 0, h - 1)    # glTF UV origin = top-left
    return arr[py, px]


def draw(ax, v, faces, cols, view):
    tri = v[faces]
    fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12)
    if view == 'side':
        sx, sy, depth, cam = -tri[:, :, 2], tri[:, :, 1], tri[:, :, 0].mean(1), np.array([1.0, 0, 0])
    else:
        sx, sy, depth, cam = tri[:, :, 0], tri[:, :, 1], tri[:, :, 2].mean(1), np.array([0, 0, 1.0])
    light = cam * 0.6 + np.array([0, 0.8, 0])
    light /= np.linalg.norm(light)
    shade = 0.45 + 0.55 * np.abs(fn @ light)
    fc = np.clip(cols * shade[:, None] * 1.35, 0, 1)
    order = np.argsort(depth)
    polys = np.stack([sx, sy], axis=-1)[order]
    ax.add_collection(PolyCollection(polys, facecolors=fc[order], edgecolors=fc[order], linewidths=0.15))
    ax.axhline(GROUND, color='#777', lw=0.8)
    if view == 'side':
        ax.set_xlim(-1.25, 1.25)
    else:
        ax.set_xlim(-1.25, 1.25)
    ax.set_ylim(GROUND - 0.12, GROUND - 0.12 + 2.5 * PANEL_H / PANEL_W)
    ax.set_aspect('equal')
    ax.set_axis_off()


def pick_frames(times, loop, n=6):
    last = len(times) - 1
    if loop:                        # spread over the cycle, skip the seam duplicate
        return [int(round(i * last / n)) for i in range(n)]
    return [int(round(i * last / (n - 1))) for i in range(n)]


def grid(R, cols, clip, out, tag):
    times, _, _ = R.clips[clip]
    ks = pick_frames(times, clip in LOOPS)
    fig = plt.figure(figsize=(PANEL_W * len(ks), PANEL_H * 2), dpi=100)
    lows = []
    for c, k in enumerate(ks):
        v, _, _ = R.skin(clip, k)
        lo = v[:, 1].min() - GROUND
        lows.append(lo)
        for r, view in enumerate(('side', 'front')):
            ax = fig.add_axes([c / len(ks), (1 - r) / 2, 1 / len(ks), 0.5])
            draw(ax, v, R.idx, cols, view)
            ax.text(0.02, 0.97, f"{clip}  {view}  t={times[k]:.3f}s  key {k}/{len(times) - 1}"
                    + (f"  lowest {lo * 100:+.1f}cm" if r == 0 else ""),
                    transform=ax.transAxes, va='top', fontsize=9, color='#222')
    fig.text(0.995, 0.005, tag, ha='right', va='bottom', fontsize=8, color='#444')
    fig.savefig(out, facecolor='#c8c8c8')
    plt.close(fig)
    return ks, lows


def main(path, outdir, tag=''):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    R = Rig(path)
    cols = face_colors(R)
    for clip in SPEC:
        out = outdir / f"{clip}.png"
        ks, lows = grid(R, cols, clip, out, tag or Path(path).name)
        print(f"{out}  keys {ks}  lowest-above-ground cm {[round(l * 100, 1) for l in lows]}")


if __name__ == '__main__':
    main(*sys.argv[1:4])
