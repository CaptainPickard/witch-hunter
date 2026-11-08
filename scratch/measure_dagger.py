"""A4 curved-dagger measure (static GLB parse, no browser) - adapted from
scratch/measure_torch_grip.py. Reads the FINAL normalized dagger-curved.glb raw
POSITION (node is identity) and emits scratch/dagger_measure.json, the SINGLE
SOURCE for Phase B CONFIG.equip values.
  gripHolderY: post-groundAlign holder-local Y of the grip point (handAxe
    pattern: grip butt at holder 0) = buttY - minY.
  bladeAxisY: sign(tipY - guardY); guard = widest XZ slice, tip = the Y end
    farther from the guard (handAxe +1 / longsword -1 convention)."""
import json, struct, numpy as np
p = 'art-direction/3d/assets/weapons/dagger-curved.glb'
b = open(p, 'rb').read()
jl = struct.unpack('<I', b[12:16])[0]
J = json.loads(b[20:20 + jl]); bin0 = 20 + jl + 8
CT = {5126: np.float32}
def acc(i):
    a = J['accessors'][i]; v = J['bufferViews'][a['bufferView']]
    n = {'VEC3': 3, 'VEC2': 2, 'SCALAR': 1}[a['type']]
    off = bin0 + v.get('byteOffset', 0) + a.get('byteOffset', 0)
    return np.frombuffer(b, CT[a['componentType']], a['count'] * n, off).reshape(-1, n)
prims = [pr for m in J['meshes'] for pr in m['primitives']]
P = np.vstack([acc(pr['attributes']['POSITION']) for pr in prims]).astype(np.float64)
tri = sum(J['accessors'][pr['indices']]['count'] // 3 for pr in prims)
lo, hi = P.min(0), P.max(0); ext = hi - lo
y0, y1 = lo[1], hi[1]; H = y1 - y0
rows = []
for k in range(20):
    a = y0 + H * k / 20; c = a + H / 20
    s = P[(P[:, 1] >= a) & (P[:, 1] < c + (1e-9 if k == 19 else 0))]
    r = np.hypot(s[:, 0], s[:, 2]).max() if len(s) else 0
    rows.append((a, r))
    print('holder y %.3f-%.3f (%.0f%%)  rXZ %.3f  zHalf %.3f  n %d' % (
        a - y0, c - y0, 100 * k / 20, r, np.abs(s[:, 2]).max() if len(s) else 0, len(s)))
guardY = max(rows, key=lambda t: t[1])[0] + H / 40
tipY = y1 if abs(y1 - guardY) > abs(y0 - guardY) else y0
buttY = y0 if tipY == y1 else y1
print('guard y %.4f  tip y %.4f  butt y %.4f  blade len %.4f  grip len %.4f' % (
    guardY, tipY, buttY, abs(tipY - guardY), abs(guardY - buttY)))
out = {
    'triCount': int(tri),
    'height_m': round(float(H), 4),
    'weaponTargetHeight': 0.35,
    'gripHolderY': round(float(buttY - y0), 4),
    'bladeAxisY': 1 if tipY > guardY else -1,
    'extentsXYZ': [round(float(e), 4) for e in ext],
}
print('scale @0.35 = %.4f' % (0.35 / H))
json.dump(out, open('scratch/dagger_measure.json', 'w'), indent=2)
open('scratch/dagger_measure.json', 'a').write('\n')
print(json.dumps(out, indent=2))
