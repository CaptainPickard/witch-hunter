#!/usr/bin/env python3
"""Composite the dagger QA cells (scratch/blender_dagger_clips.py --preview)
into one full-size 6-frame grid per clip (3 x 2, 512 px cells, labelled with
moment + time), named after the clip.

  python3 scratch/dagger_grid.py CELL_DIR OUT_DIR
"""
import os, sys
from PIL import Image, ImageDraw

CLIPS = {"WH_DagSlashR2L": (0.10, 0.12, 0.16), "WH_DagSlashL2R": (0.10, 0.12, 0.16),
         "WH_DagSlashR2Lb": (0.10, 0.12, 0.48)}
cells, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
for name, (w, s, r) in CLIPS.items():
    mid = (0.36, "hold end") if name == "WH_DagSlashR2Lb" else (w + s + 0.5 * r, "mid recover")
    moments = [("rest", 0.0), ("windup end", w), ("contact", w + 0.5 * s), ("strike end", w + s),
               (mid[1], mid[0]), ("end", w + s + r)]
    ims = [Image.open(os.path.join(cells, f"{name}_c{c}.png")).convert("RGB") for c in range(6)]
    cw, ch = ims[0].size
    g = Image.new("RGB", (3 * cw, 2 * ch + 28), (20, 20, 24))
    d = ImageDraw.Draw(g)
    d.text((8, 8), f"{name}  {w:.2f}/{s:.2f}/{r:.2f} s = {w + s + r:.2f} s   (front-right 3/4, ortho; ground z=-1; dagger-curved proxy @0.35)",
           fill=(230, 230, 230))
    for c, (im, (label, t)) in enumerate(zip(ims, moments)):
        x, y = (c % 3) * cw, 28 + (c // 3) * ch
        g.paste(im, (x, y))
        d.rectangle([x, y, x + 210, y + 22], fill=(0, 0, 0))
        d.text((x + 6, y + 5), f"{c + 1}. {label}  t={t:.2f}s", fill=(255, 220, 120))
    p = os.path.join(out, f"{name}.png")
    g.save(p, optimize=True)
    print(p, g.size, os.path.getsize(p) // 1024, "KB")
