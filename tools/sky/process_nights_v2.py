#!/usr/bin/env python3
"""Witch Hunter night pano v2: moon LOW-LEFT, higher fidelity (sky law change).

Contract (vision-measured): moon u ~0.21-0.25 left, v ~0.56-0.64 top, full
disc, crisp. Fidelity: sky panos drop posterize + NEAREST; ship at the
generator's native pixel shape (2172x724 with soft Lanczos to 2048x682) so
the dome keeps HD gradients. All 12 non-night panos re-emit with the SAME
smooth treatment for a consistent set.
"""
import os
from PIL import Image

CACHE = '/home/hermeswebui/.hermes/profiles/io/cache/images'
OUT = '/tmp/wh-worldfeat/art-direction/textures/sky2v2'
MASTERS = '/tmp/wh-worldfeat/scratch/sky-masters-v2'

# night v2 generations (moon low-left contract)
NIGHTS = {
    'sky2v2-nightA.jpg': 'openai_codex_gpt-image-2-high_20261006_054217_bd05a9e8.png',
    'sky2v2-nightB.jpg': 'openai_codex_gpt-image-2-high_20261006_054209_a6e9bc16.png',
    'sky2v2-nightC.jpg': 'openai_codex_gpt-image-2-high_20261006_054214_7d6b96b1.png',
}

# non-night panos re-emit (smooth, same seam fix, masters already in repo)
REEMIT = [
    ('sky2', 'sky-masters', 'dawn-master-seamfixed.png'),
    ('sky2', 'sky-masters', 'day-master-seamfixed.png'),
    ('sky2', 'sky-masters', 'dusk-master-seamfixed.png'),
    ('sky3', 'sky-masters2', 'day-master.png', 'dayA'),
    ('sky3', 'sky-masters2', 'dusk-master.png', 'duskA'),
    ('sky3', 'sky-masters3', 'dayB-master.png', 'dayB'),
    ('sky3', 'sky-masters3', 'dayC-master.png', 'dayC'),
    ('sky3', 'sky-masters3', 'dayD-master.png', 'dayD'),
    ('sky3', 'sky-masters3', 'dawnB-master.png', 'dawnB'),
    ('sky3', 'sky-masters3', 'dawnC-master.png', 'dawnC'),
    ('sky3', 'sky-masters3', 'dawnD-master.png', 'dawnD'),
    ('sky3', 'sky-masters3', 'duskB-master.png', 'duskB'),
    ('sky3', 'sky-masters3', 'duskC-master.png', 'duskC'),
    ('sky3', 'sky-masters3', 'duskD-master.png', 'duskD'),
]

def smooth_fit(img):
    """Fit 4:1 by squish (content-preserving), keep HD: native ~2172x724 ->
    2048 wide WITHOUT posterize; soft NEAREST-free upscale of the vertical."""
    img = img.resize((2048, 682), Image.LANCZOS)
    return img

def seam_fix(img, feather=220):
    """Ensure left/right edges meet (mirrored feather blend) - idempotent on
    the seam-fixed masters."""
    w, h = img.size
    strip = img.crop((0, 0, feather, h))
    mirror = strip.transpose(Image.FLIP_LEFT_RIGHT)
    grad = Image.linear_gradient('L').rotate(-90, expand=True).resize((feather, h))
    base = img.copy()
    base.paste(mirror, (w - feather, 0), grad)
    return base

os.makedirs(OUT, exist_ok=True)
os.makedirs(MASTERS, exist_ok=True)

report = []
for out_name, src in NIGHTS.items():
    src_path = os.path.join(CACHE, src)
    img = Image.open(src_path).convert('RGB')
    sf = seam_fix(img)
    sf.save(os.path.join(MASTERS, out_name.replace('.jpg', '-master.png')))
    out = smooth_fit(sf)
    out.save(os.path.join(OUT, out_name), quality=88)
    report.append((out_name, out.size, os.path.getsize(os.path.join(OUT, out_name))))

for item in REEMIT:
    if len(item) == 3:
        suffix, pool, name = item
        alt = name.replace('-master-seamfixed.png', '')
    else:
        suffix, pool, name, alt = item
    src_path = f'/tmp/wh-worldfeat/scratch/{pool}/{name}'
    img = Image.open(src_path).convert('RGB')
    img = seam_fix(img)  # set-3 masters are RAW (pre-seam-fix)
    out = smooth_fit(img)
    out_name = f'{suffix}-{alt}.jpg'
    out.save(os.path.join(OUT, out_name), quality=88)
    report.append((out_name, out.size, os.path.getsize(os.path.join(OUT, out_name))))

for name, size, bytes_ in sorted(report):
    print(name, size, bytes_)
print('V2_DONE')