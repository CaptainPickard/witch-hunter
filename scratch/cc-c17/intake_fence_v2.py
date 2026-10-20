#!/usr/bin/env python3
"""CC-C17 intake: census + pixelate the regenerated ok-fence-corner-v2."""
import os, sys, struct, json
import numpy as np
import trimesh
from PIL import Image

sys.path.insert(0, '/tmp/wh-worldfeat/scratch/cc-c17')

def count_tris(glb):
    with open(glb, 'rb') as f:
        d = f.read()
    clen = struct.unpack_from('<I', d, 12)[0]
    js = json.loads(d[20:20 + clen])
    n = 0
    for m in js.get('meshes', []):
        for p in m.get('primitives', []):
            idx = p.get('indices')
            if idx is not None:
                n += js['accessors'][idx].get('count', 0) // 3
    return n

def posterize512(img):
    img = img.convert('RGBA')
    w, h = img.size
    scale = 512.0 / max(w, h)
    if scale < 1.0:
        img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.NEAREST)
    arr = np.array(img)
    for c in (0, 1, 2):
        arr[..., c] = (arr[..., c] >> 3) << 3
    return Image.fromarray(arr)

raw = '/tmp/wh-worldfeat/scratch/treegen/old_king/raw/ok-fence-corner-v2-meshy.glb'
out = '/tmp/wh-worldfeat/art-direction/3d/assets/old_king/ok-fence-corner-v2-pixelated.glb'
if not os.path.exists(raw):
    raise SystemExit('raw missing')
tri = count_tris(raw)
print('v2 raw tris:', tri, '(cap 2600)')
if tri > 4000:
    raise SystemExit('OVER CAP - reject')
if os.path.exists(out):
    print('skip exists')
else:
    obj = trimesh.load(raw)
    s = obj if isinstance(obj, trimesh.Scene) else trimesh.Scene({'m': obj})
    for name, geom in s.geometry.items():
        mat = getattr(geom.visual, 'material', None)
        tex = getattr(mat, 'baseColorTexture', None) if mat is not None else None
        if tex is not None:
            try:
                mat.baseColorTexture = posterize512(tex)
            except Exception as e:
                print('tex fail', name, e)
    s.export(out)
    print('baked ->', out, count_tris(out), 'tris', os.path.getsize(out) // 1024, 'KB')