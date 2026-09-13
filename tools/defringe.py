#!/usr/bin/env python3
"""S5b: defringe pass for alpha-extracted sprites.

Median-filters RGB under the semi-transparent matte and hardens the
alpha band, removing background-color halos left by chroma keying.

Usage: python3 defringe.py IN_DIR OUT_DIR
"""
import sys, os
from PIL import Image, ImageFilter

def defringe(src, dest):
    im = Image.open(src).convert('RGBA')
    px = im.load()
    w, h = im.size
    med = im.convert('RGB').filter(ImageFilter.MedianFilter(3))
    medpx = med.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if 0 < a < 250:
                nr, ng, nb = medpx[x, y]
                px[x, y] = (nr, ng, nb, a)
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 40: px[x, y] = (r, g, b, 0)
            elif a > 215: px[x, y] = (r, g, b, 255)
    im.save(dest)
    return im.size

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    os.makedirs(dst, exist_ok=True)
    for f in sorted(os.listdir(src)):
        if f.endswith('.png'):
            defringe(os.path.join(src, f), os.path.join(dst, f))
            print('defringed', f)
