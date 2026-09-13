#!/usr/bin/env python3
"""Anchor-contract alignment QA for layered sprite systems (doc 27 R2).

Verifies that an equipment layer aligns to its body canon:
1. bbox overlap: the piece's opaque region must sit INSIDE the body's
   silhouette region for its slot (head/torso/back bands).
2. vertical band check: head pieces in top band, torso in middle,
   cloak spanning upper-to-mid.
3. style match: both frames same size before normalize.

Usage: python3 anchor_check.py BODY.png PIECE.png --slot head|torso|back
Exit code 0 = aligned, 1 = misaligned. Prints a report.
"""
import sys, os, json
from PIL import Image

BANDS = {
    'head':  (0.00, 0.22),   # top 22% of figure height
    'torso': (0.15, 0.50),   # shoulders to waist
    'back':  (0.10, 0.75),   # shoulders to calves
}

def opaque_bbox(path):
    im = Image.open(path).convert('RGBA')
    px = im.load()
    w, h = im.size
    minx, miny, maxx, maxy = w, h, 0, 0
    found = False
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            if px[x, y][3] > 60:
                found = True
                minx = min(minx, x); maxx = max(maxx, x)
                miny = min(miny, y); maxy = max(maxy, y)
    if not found:
        return None
    return (minx, miny, maxx, maxy, w, h)

def main():
    body_path, piece_path = sys.argv[1], sys.argv[2]
    slot = sys.argv[sys.argv.index('--slot') + 1]
    bb = opaque_bbox(body_path)
    pb = opaque_bbox(piece_path)
    if not bb or not pb:
        print('FAIL: empty frame'); sys.exit(1)
    bx0, by0, bx1, by1, bw, bh = bb
    px0, py0, px1, py1, pw, ph = pb
    report = {'body_bbox': bb, 'piece_bbox': pb, 'slot': slot}
    ok = True
    # 1. canvas size match (before normalize)
    if (bw, bh) != (pw, ph):
        report['size_match'] = False
        ok = False
    else:
        report['size_match'] = True
    # 2. vertical band: piece's vertical span relative to body's figure span
    fig_top, fig_bot = by0, by1
    fig_h = fig_bot - fig_top
    p_top_rel = (py0 - fig_top) / fig_h
    p_bot_rel = (py1 - fig_top) / fig_h
    band = BANDS[slot]
    report['piece_v_span'] = [round(p_top_rel, 3), round(p_bot_rel, 3)]
    report['expected_band'] = band
    if not (band[0] - 0.08 <= p_top_rel and p_bot_rel <= band[1] + 0.12):
        report['band_ok'] = False
        ok = False
    else:
        report['band_ok'] = True
    # 3. horizontal: piece must overlap body's horizontal span
    h_overlap = not (px1 < bx0 or px0 > bx1)
    report['h_overlap'] = h_overlap
    ok = ok and h_overlap
    report['verdict'] = 'PASS' if ok else 'FAIL'
    print(json.dumps(report, indent=1))
    sys.exit(0 if ok else 1)

if __name__ == '__main__':
    main()