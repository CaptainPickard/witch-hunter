#!/usr/bin/env python3
"""S5a: alpha extraction for sprite frames.

Corner-sampled chroma-key against the known studio background color.
Input: PNG frames on flat dark-gray background.
Output: RGBA frames with alpha matte, cropped to content bbox.

Usage: python3 alpha_extract.py IN_DIR OUT_DIR
"""
import sys, os, math, statistics
from PIL import Image

def alpha_extract(path, dest):
    im = Image.open(path).convert('RGBA')
    px = im.load()
    w, h = im.size
    corners = [px[5,5][:3], px[w-6,5][:3], px[5,h-6][:3], px[w-6,h-6][:3]]
    bg = tuple(int(statistics.median([c[i] for c in corners])) for i in range(3))
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            dist = math.sqrt((r-bg[0])**2 + (g-bg[1])**2 + (b-bg[2])**2)
            if dist < 18: alpha = 0
            elif dist > 60: alpha = 255
            else: alpha = int(255 * (dist-18) / 42)
            px[x, y] = (r, g, b, min(a, alpha))
    bbox = im.getbbox()
    if bbox: im = im.crop(bbox)
    im.save(dest)
    return im.size

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    os.makedirs(dst, exist_ok=True)
    for f in sorted(os.listdir(src)):
        if f.endswith('.png'):
            sz = alpha_extract(os.path.join(src, f), os.path.join(dst, f.replace('.png','-alpha.png')))
            print(f, sz)
