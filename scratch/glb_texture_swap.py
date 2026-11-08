#!/usr/bin/env python3
"""Texture-swap-in-place: rigged GLB -> pixelated rigged GLB (WOLF-RIG sec. 4).

v3 pixelation (art-direction/3d/regen_pipeline_v3.py pixelate_colors: 512px
NEAREST downscale + 5-bit posterize, PNG) applied to the embedded atlas WITHOUT
re-exporting through any mesh library (trimesh/v3 export drops skins).

Byte law (asserted):
  - only the image's bufferView payload, that view's byteLength (and, if the
    PNG outgrows the slot, its byteOffset -> relocated to the END of the BIN,
    the regrade_atlas.py pattern), images[0].mimeType and buffers[0].byteLength
    may change;
  - every other bufferView range is byte-identical (POSITION/NORMAL/
    TEXCOORD_0/JOINTS_0/WEIGHTS_0/indices/IBM/animation samplers), every other
    JSON key is equal (skins, animations, nodes, materials, samplers...).
  - The header length is recomputed by glb_append_clips.save (the v3 header
    bug class: total length is asserted on re-parse).

    python3 scratch/glb_texture_swap.py RIGGED.glb OUT.pixelated.glb
"""
import copy
import io
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from glb_append_clips import parse, save  # noqa: E402


def pixelate_colors(tex):
    """== regen_pipeline_v3.pixelate_colors (copied: that module runs its batch at import)."""
    t = tex.convert('RGB').resize((512, 512), Image.NEAREST)
    arr = np.asarray(t)
    arr = (arr >> 3) << 3
    return Image.fromarray(arr)


def swap(src_path, out_path):
    assert Path(src_path).resolve() != Path(out_path).resolve()
    doc, blob = parse(src_path)
    out = copy.deepcopy(doc)
    data = bytearray(blob)
    assert len(doc['images']) == 1
    vi = doc['images'][0]['bufferView']
    view = out['bufferViews'][vi]
    off, length = view.get('byteOffset', 0), view['byteLength']
    src = Image.open(io.BytesIO(bytes(blob[off:off + length])))
    buf = io.BytesIO()
    pixelate_colors(src).save(buf, format='PNG', optimize=True)
    png = buf.getvalue()
    if len(png) <= length:
        data[off:off + len(png)] = png
        data[off + len(png):off + length] = b'\0' * (length - len(png))   # stale tail zeroed
        mode = f'in place (slot {length} B, {length - len(png)} B slack zeroed)'
    else:
        data.extend(b'\0' * (-len(data) % 4))
        view['byteOffset'] = len(data)
        data.extend(png)
        mode = f'relocated to BIN end @ {view["byteOffset"]} (outgrew {length} B slot)'
    view['byteLength'] = len(png)
    out['images'][0]['mimeType'] = 'image/png'
    out['buffers'][0]['byteLength'] = len(data)
    save(out_path, out, data)

    # ---- byte law
    chk, cbin = parse(out_path)
    for i, (a, b) in enumerate(zip(doc['bufferViews'], chk['bufferViews'])):
        if i == vi:
            continue
        assert a == b, f'bufferView {i} JSON changed'
        o, n = a.get('byteOffset', 0), a['byteLength']
        assert blob[o:o + n] == cbin[o:o + n], f'bufferView {i} bytes changed'
    for k in doc:
        if k not in ('bufferViews', 'buffers', 'images'):
            assert doc[k] == chk[k], k
    v = chk['bufferViews'][vi]
    got = cbin[v['byteOffset']:v['byteOffset'] + v['byteLength']]
    assert got == png
    return len(png), length, mode


if __name__ == '__main__':
    n, old, mode = swap(*sys.argv[1:3])
    print(f'{sys.argv[2]}: atlas {old} B JPEG 2048 -> {n} B PNG 512 NEAREST + 5-bit, {mode}; '
          f'all other bufferViews + JSON byte-identical')
