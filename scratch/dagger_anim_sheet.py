#!/usr/bin/env python3
"""Composite scratch/dagger_anim_render.py cells into labelled sheets.

    python3 scratch/dagger_anim_sheet.py CELLS.json CELL_DIR OUT_DIR strip|grid [--title-json T.json]

strip: one 6x1 contact strip per clip (A1 candidates); grid: 3x2 full-size
6-frame grid per clip (A4, scratch/dagger_grid.py convention). Titles come
from T.json {clip: "title line"} when given.
"""
import json
import os
import sys

from PIL import Image, ImageDraw

cells_json, cell_dir, out, mode = sys.argv[1:5]
titles = json.load(open(sys.argv[sys.argv.index('--title-json') + 1])) if '--title-json' in sys.argv else {}
os.makedirs(out, exist_ok=True)
for name, moments in json.load(open(cells_json)).items():
    ims = [Image.open(os.path.join(cell_dir, f'{name}_c{c}.png')).convert('RGB') for c in range(len(moments))]
    cw, ch = ims[0].size
    cols = len(ims) if mode == 'strip' else 3
    rows = -(-len(ims) // cols)
    g = Image.new('RGB', (cols * cw, rows * ch + 28), (20, 20, 24))
    d = ImageDraw.Draw(g)
    d.text((8, 8), titles.get(name, name), fill=(230, 230, 230))
    for c, (im, (label, t)) in enumerate(zip(ims, moments)):
        x, y = (c % cols) * cw, 28 + (c // cols) * ch
        g.paste(im, (x, y))
        d.rectangle([x, y, x + 200, y + 22], fill=(0, 0, 0))
        d.text((x + 6, y + 5), f'{c + 1}. {label}  t={t:.3f}s', fill=(255, 220, 120))
    p = os.path.join(out, f'{name}.png')
    g.save(p, optimize=True)
    print(p, g.size, os.path.getsize(p) // 1024, 'KB')
