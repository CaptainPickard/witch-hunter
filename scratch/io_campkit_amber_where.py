#!/usr/local/bin/python3
"""IO: where ARE the amber texels, and where does the firepit sample UVs?"""
import json, struct
import numpy as np
import io as _io
from PIL import Image

path = '/tmp/wh-worldfeat/art-direction/3d/assets/camp/wh-campkit-pixelated.glb'
b = open(path, 'rb').read()
jl = struct.unpack_from('<I', b, 12)[0]
g = json.loads(b[20:20 + jl])
binoff = 20 + jl + 8
img = g['images'][0]
bv = g['bufferViews'][img['bufferView']]
o = binoff + bv.get('byteOffset', 0)
tex = Image.open(_io.BytesIO(bytes(b[o:o + bv['byteLength']]))).convert('RGB')
arr = np.asarray(tex).astype(int)
h, w = arr.shape[:2]
rf, gf, bf = arr[..., 0], arr[..., 1], arr[..., 2]
amber = (rf > 115) & (rf > gf * 1.25) & (rf > bf * 2.0)
ys, xs = np.nonzero(amber)
print('amber texel bbox: x', xs.min(), '-', xs.max(), ' y', ys.min(), '-', ys.max(),
      'count', len(xs))

node_name = {i: n.get('name') for i, n in enumerate(g['nodes'])}
mesh_of_node = {i: n.get('mesh') for i, n in enumerate(g['nodes'])}
for ni in sorted(mesh_of_node):
    mi = mesh_of_node[ni]
    if mi is None:
        continue
    prim = g['meshes'][mi]['primitives'][0]
    uvacc = g['accessors'][prim['attributes']['TEXCOORD_0']]
    uvbv = g['bufferViews'][uvacc['bufferView']]
    uvo = binoff + uvbv.get('byteOffset', 0) + uvacc.get('byteOffset', 0)
    uvs = np.frombuffer(b, np.float32, uvacc['count'] * 2, uvo).reshape(-1, 2)
    print(f'{node_name.get(ni)}: UV bbox x {uvs[:,0].min():.3f}-{uvs[:,0].max():.3f} '
          f'y {uvs[:,1].min():.3f}-{uvs[:,1].max():.3f}')