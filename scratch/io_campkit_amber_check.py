#!/usr/local/bin/python3
"""IO resume: amber ownership check on the PIXELATED campkit GLB."""
import json, struct
import numpy as np

path = '/tmp/wh-worldfeat/art-direction/3d/assets/camp/wh-campkit-pixelated.glb'
b = open(path, 'rb').read()
jl = struct.unpack_from('<I', b, 12)[0]
g = json.loads(b[20:20 + jl])
binoff = 20 + jl + 8

node_name = {i: n.get('name') for i, n in enumerate(g['nodes'])}
mesh_of_node = {i: n.get('mesh') for i, n in enumerate(g['nodes'])}

img = g['images'][0]
bv = g['bufferViews'][img['bufferView']]
o = binoff + bv.get('byteOffset', 0)
data = b[o:o + bv['byteLength']]
import io as _io
from PIL import Image
tex = Image.open(_io.BytesIO(bytes(data))).convert('RGB')
arr = np.asarray(tex).astype(int)
h, w = arr.shape[:2]
rf, gf, bf = arr[..., 0], arr[..., 1], arr[..., 2]
amber = (rf > 115) & (rf > gf * 1.25) & (rf > bf * 2.0)
print('atlas', w, 'x', h, 'amber texels:', int(amber.sum()))

for ni in sorted(mesh_of_node):
    mi = mesh_of_node[ni]
    if mi is None:
        continue
    prim = g['meshes'][mi]['primitives'][0]
    name = node_name.get(ni, str(ni))
    acc = g['accessors'][prim['indices']]
    nfaces = acc['count'] // 3
    uvacc = g['accessors'][prim['attributes']['TEXCOORD_0']]
    uvbv = g['bufferViews'][uvacc['bufferView']]
    uvo = binoff + uvbv.get('byteOffset', 0) + uvacc.get('byteOffset', 0)
    uvs = np.frombuffer(b, np.float32, uvacc['count'] * 2, uvo).reshape(-1, 2)
    ibv = g['bufferViews'][acc['bufferView']]
    io_ = binoff + ibv.get('byteOffset', 0) + acc.get('byteOffset', 0)
    idx = np.frombuffer(b, np.uint32, acc['count'], io_)
    tri_uv = uvs[idx.reshape(-1, 3)].mean(axis=1)
    px = np.clip((tri_uv[:, 0] % 1.0 * w).astype(int), 0, w - 1)
    py = np.clip(((1 - tri_uv[:, 1] % 1.0) * h).astype(int), 0, h - 1)
    hit = amber[py, px]
    print(f'{name}: faces {nfaces}, amber-flag faces {int(hit.sum())} '
          f'({100*hit.sum()/max(1,nfaces):.2f}%)')