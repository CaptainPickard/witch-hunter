#!/usr/bin/env python3
"""Round K: matte the lantern-post-v2 ref. scratch/ref_matte.py --dark fails on it because
the pillar's shadow side is the SAME tone as the plain near-black bg (24-28 vs bg 26-27),
so a colour flood-fill splits the post into pieces (tol 31-45 kept only the base or the head).
Here fg = pixels that differ from the bg tone by > DIFF (largest connected edge set only), then every row is filled symmetrically
about the pillar axis to its lit left half-width (convex, bilateral cross-sections), then
closing + largest blob + crop, same output layout as ref_matte.py.
  ref_matte_rowspan_roundK.py in.png out.png [diff=7]
Signed: Claude Code (Round K), 2026-10-05.
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

src, out = sys.argv[1], sys.argv[2]
diff = int(sys.argv[3]) if len(sys.argv) > 3 else 7
a = np.asarray(Image.open(src).convert('RGB')).astype(int)
bg = np.median(np.concatenate([a[:8].reshape(-1, 3), a[-8:].reshape(-1, 3)]), axis=0)
edge = np.abs(a - bg).max(axis=2) > diff
edge = ndimage.binary_opening(edge, iterations=1)       # drop bg noise specks
# keep only the subject's edge set (largest blob after a bridging close): stray bg specks
# would otherwise stretch their row's span out to the right
lab, n = ndimage.label(ndimage.binary_closing(edge, iterations=3))
if n > 1:
    big = 1 + int(np.argmax(ndimage.sum(np.ones_like(edge), lab, range(1, n + 1))))
    edge &= lab == big
# symmetric span about the pillar axis: the bg carries a faint halo on the right of the post
# that survives the threshold, and the post's right half is in shadow (bg tone), so each row
# mirrors its LIT LEFT half-width about the axis (the post is bilateral)
rows = [(y, np.where(edge[y])[0]) for y in range(edge.shape[0])]
rows = [(y, xs.min(), xs.max()) for y, xs in rows if len(xs) >= 2]
axis = float(np.median([(l + r) / 2 for _, l, r in rows]))
fg = np.zeros_like(edge)
for y, l, r in rows:
    hw = axis - l
    if hw > 0:
        fg[y, int(round(axis - hw)):int(round(axis + hw)) + 1] = True
fg = ndimage.binary_closing(fg, iterations=2)
lab, n = ndimage.label(fg)
if n > 1:
    sizes = ndimage.sum(fg, lab, range(1, n + 1))
    fg = lab == (1 + int(np.argmax(sizes)))
rgba = np.dstack([a, fg * 255]).astype(np.uint8)
ys, xs = np.where(fg)
pad = 24
y0, y1 = max(0, ys.min() - pad), min(a.shape[0], ys.max() + pad)
x0, x1 = max(0, xs.min() - pad), min(a.shape[1], xs.max() + pad)
Image.fromarray(rgba[y0:y1, x0:x1], 'RGBA').save(out)
print('saved', out, 'bg', bg.tolist(), 'fg px', int(fg.sum()), 'crop', (x0, y0, x1, y1))
