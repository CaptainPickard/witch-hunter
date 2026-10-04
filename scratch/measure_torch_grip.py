"""Stage 2 S3: torch grip + flame-head measure (static GLB parse, no browser).
XZ half-width per raw-Y slice; amber (flame) texel faces are not decoded -
the head is located by the widening profile at the top."""
import json, struct, numpy as np
p = 'art-direction/3d/assets/weapons/torch-pixelated.glb'
b = open(p, 'rb').read()
jl = struct.unpack('<I', b[12:16])[0]
J = json.loads(b[20:20 + jl]); bin0 = 20 + jl + 8
CT = {5126: np.float32}
def acc(i):
    a = J['accessors'][i]; v = J['bufferViews'][a['bufferView']]
    n = {'VEC3': 3, 'VEC2': 2, 'SCALAR': 1}[a['type']]
    off = bin0 + v.get('byteOffset', 0) + a.get('byteOffset', 0)
    return np.frombuffer(b, CT[a['componentType']], a['count'] * n, off).reshape(-1, n)
P = np.vstack([acc(pr['attributes']['POSITION']) for m in J['meshes'] for pr in m['primitives']])
y0, y1 = P[:, 1].min(), P[:, 1].max(); H = y1 - y0
print('raw y %.4f..%.4f  H %.4f' % (y0, y1, H))
for k in range(20):
    lo = y0 + H * k / 20; hi = lo + H / 20
    s = P[(P[:, 1] >= lo) & (P[:, 1] < hi)]
    r = np.hypot(s[:, 0], s[:, 2]).max() if len(s) else 0
    print('holder y %.3f-%.3f (%.0f%%)  rXZ %.3f  n %d' % (lo - y0, hi - y0, 100 * k / 20, r, len(s)))
