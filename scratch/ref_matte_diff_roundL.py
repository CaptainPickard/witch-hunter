#!/usr/bin/env python3
"""Round L: matte a dark-on-near-black ref whose silhouette is NOT symmetric (arm-hook post).

ref_matte.py --dark floods into the post's shadow side (same tone as the bg), and Round K's
rowspan matte mirrors each row about the pillar axis, which would erase a side arm. Here:
  1. bg model = 2nd-order polynomial fitted to the image border (the bg is a soft vignette);
  2. fg candidate = |pixel - bg| > DIFF on any channel OR local texture (3x3 std) > TEX;
  3. closing, fill enclosed holes smaller than HOLE px (glass panes, pillar shadow streaks;
     the large open gap between arm and pillar is not enclosed so it stays bg), opening,
     largest connected blob, crop with pad.
Usage: ref_matte_diff_roundL.py in.png out.png [diff=7] [tex=3.0]
Signed: Claude Code (Round L), 2026-10-05.
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

src, out = sys.argv[1], sys.argv[2]
DIFF = float(sys.argv[3]) if len(sys.argv) > 3 else 7
TEX = float(sys.argv[4]) if len(sys.argv) > 4 else 3.0
HOLE = 4000
a = np.asarray(Image.open(src).convert('RGB')).astype(float)
H, W = a.shape[:2]
yy, xx = np.mgrid[0:H, 0:W]
b = 12
edge = np.zeros((H, W), bool)
edge[:b] = edge[-b:] = True
edge[:, :b] = edge[:, -b:] = True
X, Y = xx / W - 0.5, yy / H - 0.5
basis = np.stack([np.ones_like(X), X, Y, X * X, Y * Y, X * Y], -1)
bg = np.zeros_like(a)
for c in range(3):
    coef, *_ = np.linalg.lstsq(basis[edge], a[..., c][edge], rcond=None)
    bg[..., c] = basis @ coef
diff = np.abs(a - bg).max(axis=2)
g = a.mean(axis=2)
std = np.sqrt(np.maximum(ndimage.uniform_filter(g * g, 3) - ndimage.uniform_filter(g, 3) ** 2, 0))
fg = (diff > DIFF) | (std > TEX)
fg = ndimage.binary_closing(fg, iterations=2)
lab, n = ndimage.label(~fg)
sizes = np.bincount(lab.ravel())
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
small = [i for i in range(1, n + 1) if sizes[i] < HOLE and i not in border]
fg |= np.isin(lab, small)
fg = ndimage.binary_opening(fg, iterations=1)
lab2, n2 = ndimage.label(fg)
if n2 > 1:
    s = ndimage.sum(fg, lab2, range(1, n2 + 1))
    fg = lab2 == (1 + int(np.argmax(s)))
ys, xs = np.where(fg)
pad = 24
y0, y1 = max(0, ys.min() - pad), min(H, ys.max() + pad)
x0, x1 = max(0, xs.min() - pad), min(W, xs.max() + pad)
rgba = np.dstack([a.astype(np.uint8), (fg * 255).astype(np.uint8)])
Image.fromarray(rgba[y0:y1, x0:x1], 'RGBA').save(out)
print(f'fg px {int(fg.sum())} blobs_before_keep {n2} crop y{y0}:{y1} x{x0}:{x1}')
