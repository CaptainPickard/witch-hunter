#!/usr/bin/env python3
"""Alpha-matte a white-background ref: flood-fill from the border over near-white /
light-grey (incl. the soft floor shadow) -> transparent, then crop to the subject.
Usage: ref_matte.py in.png out.png [tol=60] [--dark]
--dark (Round H): the ref is on a plain BLACK background; near-black neutral -> transparent."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
dark = '--dark' in sys.argv
argv = [x for x in sys.argv if x != '--dark']
src, out = argv[1], argv[2]
tol = int(argv[3]) if len(argv) > 3 else 60
a = np.asarray(Image.open(src).convert('RGB')).astype(int)
bright = (a.max(axis=2) <= tol) if dark else (a.min(axis=2) >= 255 - tol)   # bg-tone pixels
spread = a.max(axis=2) - a.min(axis=2) < 25            # neutral grey/white (not foliage/bark)
bg_cand = bright & spread
lab, _ = ndimage.label(bg_cand)
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.isin(lab, list(border))
# enclosed background pockets (sky between branches) larger than 150px are background too
sizes = np.bincount(lab.ravel())
pockets = np.where(sizes > 150)[0]
bg |= np.isin(lab, pockets[pockets > 0])
fg = ~bg
fg = ndimage.binary_opening(fg, iterations=1)
# keep the largest subject blob only
lab2, n = ndimage.label(fg)
if n > 1:
    sizes = ndimage.sum(fg, lab2, range(1, n + 1))
    fg = lab2 == (1 + int(np.argmax(sizes)))
rgba = np.dstack([a, (fg * 255)]).astype(np.uint8)
ys, xs = np.where(fg)
pad = 24
y0, y1 = max(0, ys.min() - pad), min(a.shape[0], ys.max() + pad)
x0, x1 = max(0, xs.min() - pad), min(a.shape[1], xs.max() + pad)
Image.fromarray(rgba[y0:y1, x0:x1], 'RGBA').save(out)
print('saved', out, 'fg px', int(fg.sum()), 'crop', (x0, y0, x1, y1))
