#!/usr/bin/env python3
"""S5c: normalize sprite frames to a fixed canvas and pack atlases.

Feet anchored to the bottom margin, uniform scale per frame.
Packs N frames horizontally into one atlas sheet.

Usage: python3 atlas_pack.py IN_DIR OUT_DIR PREFIX [--views]
Produces: PREFIX-fNN normalized frames + PREFIX-atlas.png sheet.
"""
import sys, os
from PIL import Image

CANVAS = (512, 512)

def normalize(src, dest):
    im = Image.open(src).convert('RGBA')
    w, h = im.size
    scale = (CANVAS[1] - 20) / h
    im = im.resize((max(1, int(w*scale)), CANVAS[1]-20), Image.LANCZOS)
    bg = Image.new('RGBA', CANVAS, (0, 0, 0, 0))
    x = (CANVAS[0] - im.size[0])//2
    y = CANVAS[1] - 10 - im.size[1]
    bg.paste(im, (x, y), im)
    bg.save(dest)

if __name__ == '__main__':
    src, dst, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(dst, exist_ok=True)
    files = sorted(f for f in os.listdir(src) if f.endswith('.png'))
    normed = []
    for i, f in enumerate(files, 1):
        dest = os.path.join(dst, f'{prefix}-f{i:02d}.png')
        normalize(os.path.join(src, f), dest)
        normed.append(dest)
        print('normalized', dest)
    frames = [Image.open(p) for p in normed]
    sheet = Image.new('RGBA', (CANVAS[0]*len(frames), CANVAS[1]), (0,0,0,0))
    for i, fr in enumerate(frames):
        sheet.paste(fr, (i*CANVAS[0], 0), fr)
    sheet.save(os.path.join(dst, f'{prefix}-atlas.png'))
    print('atlas packed:', sheet.size)
