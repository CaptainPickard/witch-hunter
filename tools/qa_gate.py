#!/usr/bin/env python3
"""S6: scripted QA gate for sprite batches.

1. Flicker: adjacent-frame mean abs diff (alpha-weighted).
2. Silhouette: alpha coverage at 25 percent downscale.
3. Accent audit: hue census among opaque pixels.

Usage: python3 qa_gate.py FRAME_DIR [--report OUT.json]
"""
import sys, os, json
from PIL import Image, ImageChops

def frame_diff(a_path, b_path):
    a = Image.open(a_path).convert('RGBA')
    b = Image.open(b_path).convert('RGBA')
    diff = ImageChops.difference(a, b)
    px = diff.load(); apx = a.load()
    w, h = diff.size
    total = n = 0
    for y in range(0, h, 8):
        for x in range(0, w, 8):
            r, g, bb, al = px[x, y]
            if al > 10 or apx[x, y][3] > 10:
                total += (r + g + bb)/3
                n += 1
    return round(total/max(1, n), 1)

def coverage(path):
    im = Image.open(path).convert('RGBA')
    small = im.resize((im.size[0]//4, im.size[1]//4), Image.LANCZOS)
    px = small.load()
    opaque = sum(1 for y in range(small.size[1]) for x in range(small.size[0]) if px[x, y][3] > 128)
    return round(100*opaque/(small.size[0]*small.size[1]), 1)

def accent_census(path):
    im = Image.open(path).convert('RGBA')
    px = im.load()
    counts = {'green':0, 'blue':0, 'warm':0, 'gray':0, 'other':0}
    for y in range(0, im.size[1], 4):
        for x in range(0, im.size[0], 4):
            r, g, b, a = px[x, y]
            if a > 128:
                if g > 110 and g >= r*1.2 and g > b: counts['green'] += 1
                elif b > r and b > g: counts['blue'] += 1
                elif r > g and r > b: counts['warm'] += 1
                elif abs(r-g) < 25 and abs(g-b) < 25: counts['gray'] += 1
                else: counts['other'] += 1
    return counts

if __name__ == '__main__':
    d = sys.argv[1]
    report = {'flicker': [], 'coverage': {}, 'accents': {}}
    pngs = sorted(f for f in os.listdir(d) if f.endswith('.png') and 'atlas' not in f)
    paths = [os.path.join(d, f) for f in pngs]
    for i in range(len(paths)-1):
        report['flicker'].append({f'{pngs[i]}->{pngs[i+1]}': frame_diff(paths[i], paths[i+1])})
    for f, p in zip(pngs, paths):
        report['coverage'][f] = coverage(p)
        report['accents'][f] = accent_census(p)
    out = sys.argv[sys.argv.index('--report')+1] if '--report' in sys.argv else None
    print(json.dumps(report, indent=1))
    if out:
        with open(out, 'w') as fp: json.dump(report, fp, indent=1)
        print('saved', out)
