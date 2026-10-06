#!/usr/local/bin/python3
"""AB1 icon lane: pixelize image_generate base art into 48x48 icons.
Key out the flat #101010 background, center-crop to content, pad square,
NEAREST downscale to 48, 5-bit posterize. Also builds a QA contact sheet.

Usage: /usr/local/bin/python3 tools/io_icon_pixelize.py
"""
import base64, json, os
import numpy as np
from PIL import Image

ROOT = '/tmp/wh-worldfeat'
CACHE = '/home/hermeswebui/.hermes/profiles/io/cache/images'
OUT = 48
LEVELS = 32
CROP_FRAC = 0.78          # keep the middle 78% (kills edge vignette junk)

# icon id -> generated cache file (AB1 batch 2026-10-06)
GEN = {
    'roundShield':   'openai_codex_gpt-image-2-high_20261006_215720_9d8b6134.png',
    'torch':         'openai_codex_gpt-image-2-high_20261006_215717_750be468.png',
    'magicGlove':    'openai_codex_gpt-image-2-high_20261006_215720_1474e660.png',
    'firebolt':      'openai_codex_gpt-image-2-high_20261006_215725_888b2fd8.png',
    'radiance':      'openai_codex_gpt-image-2-high_20261006_215746_fe9a6a12.png',
    'healthPotion':  'openai_codex_gpt-image-2-high_20261006_215842_0c1f93da.png',
    'bandage':       'openai_codex_gpt-image-2-high_20261006_215837_8a0e2bc3.png',
    'graveSoup':     'openai_codex_gpt-image-2-high_20261006_215838_c45f65c7.png',
    'blandMush':     'openai_codex_gpt-image-2-high_20261006_215840_ab7bdf76.png',
    'wildMushroom':  'openai_codex_gpt-image-2-high_20261006_215911_34e75633.png',
    'graveMoss':     'openai_codex_gpt-image-2-high_20261006_220112_735caa24.png',
    'boneShard':     'openai_codex_gpt-image-2-high_20261006_215943_2bb027a9.png',
    'forestHerb':    'openai_codex_gpt-image-2-high_20261006_215945_5d82b2d4.png',
    'deadwood':      'openai_codex_gpt-image-2-high_20261006_215944_a0e87432.png',
    'stolenCoin':    'openai_codex_gpt-image-2-high_20261006_220114_b146cb59.png',
}

def key_background(im):
    """Punch out the flat dark backdrop: alpha = distance from dark bg."""
    a = np.asarray(im.convert('RGB')).astype(float)
    lum = a.mean(axis=2)
    # bg is ~16/255 + paint noise; anything clearly brighter than bg = content
    alpha = np.clip((lum - 26) * 12.0, 0, 255)
    # keep full alpha inside definitely-bright cores (anti-alias edges softly)
    alpha[lum >= 36] = 255
    alpha[lum <= 20] = 0
    # despeckle: zero alpha on isolated dim pixels via neighborhood count
    am = alpha > 0
    keep = np.zeros_like(am)
    keep[1:-1, 1:-1] = (am[:-2, 1:-1] & am[2:, 1:-1]) | (am[1:-1, :-2] & am[1:-1, 2:])
    alpha[(am & ~keep) & (alpha < 200)] = 0
    out = np.dstack([a, alpha]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')

def crop_content(im):
    a = np.asarray(im)
    am = a[..., 3] > 8
    if not am.any():
        return im
    ys, xs = np.where(am)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    # square crop around the content bbox (use the larger extent, centered)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    ext = max(x1 - x0, y1 - y0) + 4
    half = ext / 2
    H, W = a.shape[:2]
    xa, xb = int(max(0, cx - half)), int(min(W, cx + half))
    ya, yb = int(max(0, cy - half)), int(min(H, cy + half))
    return im.crop((xa, ya, xb, yb))

def posterize(im):
    a = np.asarray(im).astype(float)
    rgb = np.round(a[..., :3] / 255.0 * (LEVELS - 1)) / (LEVELS - 1) * 255.0
    a[..., :3] = rgb
    return Image.fromarray(a.astype(np.uint8), 'RGBA')

def pixelize_file(src, dst):
    im = Image.open(src)
    im = key_background(im)
    im = crop_content(im)
    # pad to square, then NEAREST to 48
    w, h = im.size
    side = max(w, h)
    canvas = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    canvas.paste(im, ((side - w) // 2, (side - h) // 2), im)
    im = canvas.resize((OUT, OUT), Image.NEAREST)
    im = posterize(im)
    im.save(dst)

def main():
    fin = os.path.join(ROOT, 'prototype', 'js', 'icons')
    os.makedirs(fin, exist_ok=True)
    for icon_id, fn in GEN.items():
        src = os.path.join(CACHE, fn)
        dst = os.path.join(fin, f'{icon_id}.png')
        pixelize_file(src, dst)
        print('pixelized', icon_id)
    # QA contact sheet: 8 per row, 16px checkerboard-ish bg (magnified x2)
    ids = sorted(GEN.keys()) + ['longsword']   # + the GLB-render survivor
    ids = sorted(set(ids))
    cell, pad, cols = 112, 8, 8
    rows = (len(ids) + cols - 1) // cols
    sheet = Image.new('RGBA', (cols * cell, rows * cell), (60, 56, 48, 255))
    from PIL import ImageDraw
    for i, icon_id in enumerate(ids):
        r, c = divmod(i, cols)
        tile = Image.open(os.path.join(fin, f'{icon_id}.png')).resize((96, 96), Image.NEAREST)
        x, y = c * cell + pad, r * cell + pad
        sheet.paste(tile, (x, y), tile)
        ImageDraw.Draw(sheet).text((x + 2, y + 97), icon_id[:14], fill=(230, 226, 210, 255))
    sheet_path = os.path.join(ROOT, 'scratch', 'io_icons512', 'qa_sheet.png')
    sheet.save(sheet_path)
    print('sheet', sheet_path)

if __name__ == '__main__':
    main()