#!/usr/bin/env python3
"""Round F: measure the b3-gate passable opening from the GLB itself.

Front silhouette (projection along Z, so geometry at ANY depth blocks) is
rasterized at RES px per GLB unit; per row the free run that contains the
silhouette's center column is the opening at that height. Reports the
opening width per height band, its fraction of ext X, and the opening apex
(lowest occupied pixel above the floor in the center column = the underside
of the arch top).   gate_opening.py <glb> [--json]
"""
import sys, json
import numpy as np
import trimesh
from PIL import Image, ImageDraw

RES = 800
p = sys.argv[1]
m = trimesh.load(p, force='mesh')
b = m.bounds
ext = b[1] - b[0]
W, H = int(ext[0] * RES) + 3, int(ext[1] * RES) + 3
img = Image.new('L', (W, H), 0)
d = ImageDraw.Draw(img)
for tri in m.triangles:
    pts = [((v[0] - b[0][0]) * RES + 1, (b[1][1] - v[1]) * RES + 1) for v in tri]
    d.polygon(pts, fill=255)
sil = np.asarray(img) > 0
cols = np.where(sil.any(axis=0))[0]
cx = int(round((cols.min() + cols.max()) / 2))
rows = []
for r in range(H):
    row = sil[r]
    if row[cx]:
        rows.append((r, 0.0, None, None)); continue
    left = cx
    while left > 0 and not row[left - 1]: left -= 1
    right = cx
    while right < W - 1 and not row[right + 1]: right += 1
    if left == 0 or right == W - 1:
        rows.append((r, None, None, None)); continue   # open to the side: not inside the frame
    rows.append((r, (right - left + 1) / RES, (left - 1) / RES + b[0][0], (right) / RES + b[0][0]))
# apex: scanning the center column up from the floor, skip the floor sill
# (occupied run at the bottom), cross the free doorway, stop at the first
# occupied pixel = underside of the arch top.
colc = sil[:, cx]
r = H - 1
while r > 0 and not colc[r]: r -= 1      # raster padding below the floor
while r > 0 and colc[r]: r -= 1          # sill
sill_top_r = r + 1
while r > 0 and not colc[r]: r -= 1      # doorway
free_bottom = r
apex_y = b[1][1] - (free_bottom + 1 - 1) / RES
# narrowest opening over the walkable band (floor .. 60% of the opening height)
def y_of(rr): return b[1][1] - (rr - 1) / RES
sill_y = y_of(sill_top_r)
band_rows = [(w, l, rt) for (rr, w, l, rt) in rows if w and y_of(rr) < b[0][1] + 0.6 * (apex_y - b[0][1]) and y_of(rr) > sill_y + 0.01]
band = [w for (w, l, rt) in band_rows]
narrow = min(band_rows) if band_rows else None
out = dict(glb=p, ext=[round(float(e), 4) for e in ext], ymin=round(float(b[0][1]), 4),
           center_x=round(float(b[0][0] + (cx - 1) / RES), 4),
           opening_min=round(min(band), 4) if band else None,
           opening_median=round(float(np.median(band)), 4) if band else None,
           opening_frac_min=round(min(band) / ext[0], 4) if band else None,
           opening_min_edges=[round(narrow[1], 4), round(narrow[2], 4)] if narrow else None,
           opening_center_x=round((narrow[1] + narrow[2]) / 2, 4) if narrow else None,
           depth_frac=round(float(ext[2] / ext[0]), 4), height_frac_of_width=round(float(ext[1] / ext[0]), 4),
           apex_y=round(float(apex_y), 4), sill_y=round(float(sill_y), 4), apex_above_floor=round(float(apex_y - b[0][1]), 4),
           apex_frac=round(float((apex_y - b[0][1]) / ext[1]), 4))
for frac in (0.05, 0.2, 0.4, 0.6, 0.8, 0.95):
    yy = b[0][1] + frac * (apex_y - b[0][1])
    rr = int(round((b[1][1] - yy) * RES + 1))
    w = rows[rr]
    out['w@%.2f' % frac] = [round(w[1], 4) if w[1] is not None else None,
                            round(w[2], 4) if w[2] is not None else None,
                            round(w[3], 4) if w[3] is not None else None]
# outer pillar feet: occupied x-extent of the silhouette in the bottom 5% rows
low = sil[int(H * 0.95):H - 1].any(axis=0)
lc = np.where(low)[0]
out['feet_x'] = [round(float(lc.min() / RES + b[0][0]), 4), round(float(lc.max() / RES + b[0][0]), 4)]
if '--png' in sys.argv:
    Image.fromarray((sil * 255).astype(np.uint8)).save(sys.argv[sys.argv.index('--png') + 1])
print(json.dumps(out, indent=None if '--json' in sys.argv else 1))
