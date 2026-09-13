#!/usr/bin/env python3
"""Layer compositor for the paper-doll equipment system (doc 27).

Places alpha-extracted equipment pieces onto a body canvas using the
proportional band anchor contract, applies punch-through masking for
occluding pieces over soft geometry (hair under helms), and composites
the z-ordered stack.

Usage: python3 layer_compose.py BODY.png --place PIECE.png out.png
           --band top bottom --width frac [--punch]
       python3 layer_compose.py --composite OUT.png LAYER1 LAYER2 ...
"""
import sys, os, math, statistics, json
from PIL import Image, ImageFilter

CANVAS = (512, 512)
FIG_H = 460
TOP_Y = 502 - FIG_H

def alpha_extract(path, dest=None):
    im = Image.open(path).convert('RGBA')
    px = im.load(); w, h = im.size
    corners = [px[5,5][:3], px[w-6,5][:3], px[5,h-6][:3], px[w-6,h-6][:3]]
    bg = tuple(int(statistics.median([c[i] for c in corners])) for i in range(3))
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            dist = math.sqrt((r-bg[0])**2+(g-bg[1])**2+(b-bg[2])**2)
            if dist < 18: alpha = 0
            elif dist > 60: alpha = 255
            else: alpha = int(255*(dist-18)/42)
            px[x, y] = (r, g, b, min(a, alpha))
    px = im.load()
    minx, miny, maxx, maxy = w, h, 0, 0
    for y in range(h):
        for x in range(w):
            if px[x, y][3] > 60:
                minx=min(minx,x); maxx=max(maxx,x); miny=min(miny,y); maxy=max(maxy,y)
    im = im.crop((minx, miny, maxx+1, maxy+1))
    if dest: im.save(dest)
    return im

def normalize_body(path, dest, fig_h=FIG_H):
    body = alpha_extract(path)
    bw = int(body.size[0] * fig_h / body.size[1])
    body_n = body.resize((bw, fig_h), Image.LANCZOS)
    c = Image.new('RGBA', CANVAS, (0,0,0,0))
    c.paste(body_n, ((CANVAS[0]-bw)//2, TOP_Y + fig_h - body_n.size[1]), body_n)
    c.save(dest)
    return c

def place_piece(piece_path, dest, band_top, band_bot, width_frac):
    piece = alpha_extract(piece_path)
    th = int((band_bot - band_top) * FIG_H)
    tw = int(piece.size[0] * th / piece.size[1])
    mw = int(width_frac * FIG_H)
    if tw > mw:
        tw = mw; th = int(piece.size[1] * tw / piece.size[0])
    pn = piece.resize((tw, th), Image.LANCZOS)
    c = Image.new('RGBA', CANVAS, (0,0,0,0))
    c.paste(pn, ((CANVAS[0]-tw)//2, int(TOP_Y + band_top*FIG_H)), pn)
    c.save(dest)
    return c

def punch_through(body_path, occluder_path, dest, start_dilation=9, max_dilation=41):
    """Erase body pixels under the occluder, with adaptive dilation until
    no soft-geometry (hair) pixels remain uncovered. Returns dilation used."""
    body = Image.open(body_path).convert('RGBA')
    occ_a = Image.open(occluder_path).convert('RGBA').split()[3]
    # hair-ish pixel mask in the head band (brown-ish opaque pixels)
    bpx = body.load()
    hair = Image.new('L', body.size, 0)
    hpx = hair.load()
    for y in range(0, 90):
        for x in range(body.size[0]):
            r, g, b, a = bpx[x, y]
            if a > 100 and r > g > b and r > 90 and (r-b) > 25:
                hpx[x, y] = 255
    k = start_dilation
    while k <= max_dilation:
        dil = occ_a.filter(ImageFilter.MaxFilter(k))
        dpx = dil.load(); hpx2 = hair.load()
        uncovered = sum(1 for y in range(body.size[1]) for x in range(body.size[0])
                        if hpx2[x, y] > 100 and dpx[x, y] <= 100)
        if uncovered == 0:
            break
        k += 6
    bp = body.load(); dp = dil.load()
    for y in range(body.size[1]):
        for x in range(body.size[0]):
            if dp[x, y] > 100:
                r, g, b, a = bp[x, y]
                bp[x, y] = (r, g, b, 0)
    body.save(dest)
    return k

def composite(dest, layer_paths):
    c = Image.new('RGBA', CANVAS, (0,0,0,0))
    for p in layer_paths:
        c = Image.alpha_composite(c, Image.open(p).convert('RGBA'))
    c.save(dest)
    return c

# simple CLI: --demo runs the knight pilot pipeline
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--composite':
        composite(sys.argv[2], sys.argv[3:])
        print('composited', sys.argv[2])
    else:
        print('see --composite; band placement is called from pipeline scripts')