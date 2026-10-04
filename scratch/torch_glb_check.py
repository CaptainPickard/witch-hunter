#!/usr/bin/env python3
"""T1 static GLB parse (no browser): validates the GLB container the way
THREE.GLTFLoader reads it - magic/version/length, JSON + BIN chunks, every
accessor's bufferView in-bounds, primitive attributes, embedded image decodes -
then reports the bounds assets.js groundAlign() measures (GROUND_META.height).
  torch_glb_check.py <file.glb>
"""
import sys, io, json, struct
import numpy as np
from PIL import Image

p = sys.argv[1]
d = open(p, 'rb').read()
magic, ver, total = struct.unpack_from('<4sII', d, 0)
assert magic == b'glTF' and ver == 2 and total == len(d), (magic, ver, total, len(d))
jl, jt = struct.unpack_from('<II', d, 12)
assert jt == 0x4E4F534A, 'first chunk not JSON'
g = json.loads(d[20:20 + jl])
bl, bt = struct.unpack_from('<II', d, 20 + jl)
assert bt == 0x004E4942, 'second chunk not BIN'
binc = d[28 + jl:28 + jl + bl]
assert len(binc) == bl and g['buffers'][0]['byteLength'] <= bl
SZ = {5126: 4, 5125: 4, 5123: 2, 5121: 1}
N = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}
for i, a in enumerate(g['accessors']):
    bv = g['bufferViews'][a['bufferView']]
    need = a.get('byteOffset', 0) + a['count'] * SZ[a['componentType']] * N[a['type']]
    assert need <= bv['byteLength'], f'accessor {i} overruns its bufferView'
    assert bv.get('byteOffset', 0) + bv['byteLength'] <= bl, f'bufferView of {i} overruns BIN'
assert len(g['meshes']) == 1 and len(g['meshes'][0]['primitives']) == 1
prim = g['meshes'][0]['primitives'][0]
attrs = prim['attributes']
pa = g['accessors'][attrs['POSITION']]
bv = g['bufferViews'][pa['bufferView']]
o = bv.get('byteOffset', 0) + pa.get('byteOffset', 0)
pos = np.frombuffer(binc[o:o + pa['count'] * 12], '<f4').reshape(-1, 3)
counts = {k: g['accessors'][v]['count'] for k, v in attrs.items()}
assert len(set(counts.values())) == 1, counts
ia = g['accessors'][prim['indices']]
img = g['images'][0]
ibv = g['bufferViews'][img['bufferView']]
im = Image.open(io.BytesIO(binc[ibv.get('byteOffset', 0):ibv.get('byteOffset', 0) + ibv['byteLength']]))
im.load()
mat = g['materials'][prim.get('material', 0)]
skinned = 'skins' in g or any('JOINTS_0' in pr['attributes'] for m in g['meshes'] for pr in m['primitives'])
lo, hi = pos.min(0), pos.max(0)
print(json.dumps({
    'file': p, 'bytes': len(d), 'attributes': sorted(attrs), 'vertex_count': pa['count'],
    'triangles': ia['count'] // 3, 'image': [img.get('mimeType'), im.size, im.mode],
    'material': {k: v for k, v in mat.items() if k != 'pbrMetallicRoughness'},
    'skinned': skinned, 'animations': len(g.get('animations', [])),
    'pos_min': lo.round(4).tolist(), 'pos_max': hi.round(4).tolist(),
    'ext': (hi - lo).round(4).tolist(), 'groundAlign_height': round(float(hi[1] - lo[1]), 4)}))
print('T1 PASS: GLB container + accessors + image parse clean')
