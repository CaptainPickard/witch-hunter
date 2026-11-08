#!/usr/bin/env python3
"""Curved dagger rigid normalize (A1c, io/missions/2026-10-09-dagger.md).
RIGID TRANSFORM ONLY: the Meshy GLB already stands upright (grip low, blade
tip up along raw +Y), so the transform is a pure translation - grip butt
(pommel bottom, XZ-centred on the bottom 5% slice) to the origin. Applied to
the POSITION accessor bytes in place (+ accessor min/max); every other byte
(indices, UVs, normals, texture, node tree) is untouched, tri count unchanged.

  dagger_normalize.py <meshy.glb> <out.glb>
"""
import json, struct, sys
import numpy as np

src, out = sys.argv[1], sys.argv[2]
b = bytearray(open(src, 'rb').read())
jl = struct.unpack_from('<I', b, 12)[0]
J = json.loads(bytes(b[20:20 + jl]))
bin0 = 20 + jl + 8
assert len(J['meshes']) == 1 and len(J['meshes'][0]['primitives']) == 1
prim = J['meshes'][0]['primitives'][0]
for n in J['nodes']:
    assert not any(k in n for k in ('rotation', 'scale', 'translation')), 'non-identity node xform'
    assert np.allclose(n.get('matrix', np.eye(4).ravel()), np.eye(4).ravel()), 'non-identity node matrix'
ai = prim['attributes']['POSITION']
a = J['accessors'][ai]; v = J['bufferViews'][a['bufferView']]
assert a['componentType'] == 5126 and v.get('byteStride', 12) == 12
off = bin0 + v.get('byteOffset', 0) + a.get('byteOffset', 0)
P = np.frombuffer(bytes(b[off:off + a['count'] * 12]), '<f4').reshape(-1, 3).astype(np.float64)
y0, y1 = P[:, 1].min(), P[:, 1].max()
butt = P[P[:, 1] < y0 + 0.05 * (y1 - y0)]
cx = (butt[:, 0].min() + butt[:, 0].max()) / 2
cz = (butt[:, 2].min() + butt[:, 2].max()) / 2
T = np.array([-cx, -y0, -cz])
Q = (P + T).astype('<f4')
b[off:off + a['count'] * 12] = Q.tobytes()
a['min'] = Q.min(0).tolist(); a['max'] = Q.max(0).tolist()
js = json.dumps(J, separators=(',', ':')).encode()
js += b' ' * ((4 - len(js) % 4) % 4)
rest = bytes(b[20 + jl:])
o = bytearray(b'glTF') + struct.pack('<II', 2, 12 + 8 + len(js) + len(rest))
o += struct.pack('<I', len(js)) + b'JSON' + js + rest
open(out, 'wb').write(o)
print('translate', np.round(T, 6).tolist(), 'raw y %.4f..%.4f' % (y0, y1),
      'new min', np.round(Q.min(0), 4).tolist(), 'max', np.round(Q.max(0), 4).tolist())
