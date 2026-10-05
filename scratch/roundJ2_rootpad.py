#!/usr/bin/env python3
"""Round J2: close the reach-tree trunk undersides with a ROOT PAD.
The Meshy trunks have no open boundary loop near the base (0 boundary edges in
the bottom 30%), so there's no loop to fill. The 'hole' is a raised root arch:
the closed trunk surface rises 0.03-0.09 GLB units between the root flares.
The pad is a closed plug filling the space under the root arch:
  footprint R(theta): walk out from the trunk axis while the mesh overhangs
            (underside < H_CAP), stop where a flare meets the ground
  top surface follows the mesh underside + EPS (hidden inside the shell)
  wall from the top edge down to y = ymin + BOT (buried by groundSink)
  bottom disk concave: center pressed down toward ymin (never below it, so
            assets.js groundAlign and the accessor min stay unchanged)
  the wall + top surface + bottom disk make a closed plug.
From the side the pad wall fills the arch gaps with bark; from above it's
inside the trunk section. UVs = nearest trunk vertex UV (bark colour).
Explicit normals; the existing verts/normals aren't touched. Appends to the
single primitive and rewrites the GLB (JSON/BIN chunks, 4-byte aligned).
Stage 2 (roundJ2_webs.py) closes the see-through slits between flares and
trunk 1.3-1.8 m up with leak-filtered web volumes.
usage: roundJ2_rootpad.py <in.glb> <out.glb> [nseg=48]"""
import json, struct, sys
import numpy as np
import trimesh
sys.path.insert(0, __import__('os').path.dirname(__file__))
from roundJ2_webs import webs

src, dst = sys.argv[1], sys.argv[2]
NSEG = int(sys.argv[3]) if len(sys.argv) > 3 else 48
DOME = 0.06          # requested concave depth (GLB units), clamped to ymin
BOT = 0.003          # bottom ring height above ymin
SHRINK = 0.95
H_CAP = 0.20        # max underside height the pad fills up to (2 m at scale 10)
U_GROUND = 0.008    # underside this low = root flare on the ground
EPS = 0.004         # pad top tucked this far above the underside (inside the shell)

d = open(src, 'rb').read()
jl, = struct.unpack_from('<I', d, 12)
assert d[16:20] == b'JSON'
g = json.loads(d[20:20 + jl])
bo = 20 + jl
bl, = struct.unpack_from('<I', d, bo)
assert d[bo + 4:bo + 8] == b'BIN\x00'
B = d[bo + 8:bo + 8 + bl]
prim = g['meshes'][0]['primitives'][0]
assert len(g['meshes']) == 1 and len(g['meshes'][0]['primitives']) == 1

def acc(i):
    a = g['accessors'][i]; bv = g['bufferViews'][a['bufferView']]
    dt = {5126: '<f4', 5125: '<u4', 5123: '<u2'}[a['componentType']]
    w = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3}[a['type']]
    off = bv['byteOffset'] + a.get('byteOffset', 0)
    return np.frombuffer(B, dt, a['count'] * w, off).reshape(a['count'], w).copy()

at = prim['attributes']
P = acc(at['POSITION']).astype(np.float64)
UV = acc(at['TEXCOORD_0'])
N = acc(at['NORMAL'])
I = acc(prim['indices']).ravel().astype(np.int64)
F = I.reshape(-1, 3)
y = P[:, 1]; ymin, ymax = y.min(), y.max(); H = ymax - ymin
band = (y > ymin + 0.10 * H) & (y < ymin + 0.25 * H)
ax = np.median(P[band][:, [0, 2]], 0)

# underside heights (vertical rays inside trunk footprint, as roundJ_underside)
low = P[y < ymin + 0.3]
rt = np.sort(np.linalg.norm(low[:, [0, 2]] - ax, axis=1))[len(low) // 10]
T = P[F]; T = T[T[:, :, 1].min(1) < ymin + 0.5 * H]
a_, b_, c_ = T[:, 0], T[:, 1], T[:, 2]
den = (b_[:, 2] - c_[:, 2]) * (a_[:, 0] - c_[:, 0]) + (c_[:, 0] - b_[:, 0]) * (a_[:, 2] - c_[:, 2])
ok = np.abs(den) > 1e-14; den = np.where(ok, den, 1.0)
hits = []
for px in np.linspace(-rt, rt, 21):
    for pz in np.linspace(-rt, rt, 21):
        if px * px + pz * pz >= rt * rt: continue
        X, Z = px + ax[0], pz + ax[1]
        l1 = ((b_[:, 2] - c_[:, 2]) * (X - c_[:, 0]) + (c_[:, 0] - b_[:, 0]) * (Z - c_[:, 2])) / den
        l2 = ((c_[:, 2] - a_[:, 2]) * (X - c_[:, 0]) + (a_[:, 0] - c_[:, 0]) * (Z - c_[:, 2])) / den
        ins = ok & (l1 >= 0) & (l2 >= 0) & (1 - l1 - l2 >= 0)
        if ins.any():
            hits.append((l1[ins] * a_[ins, 1] + l2[ins] * b_[ins, 1] + (1 - l1[ins] - l2[ins]) * c_[ins, 1]).min() - ymin)
hits = np.array(hits)

# pad footprint R(theta): walk out from the axis while the mesh overhangs
# (vertical ray hits with underside height < H_CAP); stop at a miss, a high
# overhang, or where a root flare meets the ground (u < U_GROUND).
def under(X, Z):
    l1 = ((b_[:, 2] - c_[:, 2]) * (X - c_[:, 0]) + (c_[:, 0] - b_[:, 0]) * (Z - c_[:, 2])) / den
    l2 = ((c_[:, 2] - a_[:, 2]) * (X - c_[:, 0]) + (a_[:, 0] - c_[:, 0]) * (Z - c_[:, 2])) / den
    ins = ok & (l1 >= 0) & (l2 >= 0) & (1 - l1 - l2 >= 0)
    if not ins.any(): return np.nan
    return (l1[ins] * a_[ins, 1] + l2[ins] * b_[ins, 1] + (1 - l1[ins] - l2[ins]) * c_[ins, 1]).min() - ymin
th = np.linspace(0, 2 * np.pi, NSEG, endpoint=False)
dirs = np.column_stack([np.cos(th), np.sin(th)])
RMAX, STEP = min(3.0 * rt, 0.6), 0.004
R = np.zeros(NSEG)
for k in range(NSEG):
    rho = 0.0
    while rho + STEP <= RMAX:
        u = under(*(ax + dirs[k] * (rho + STEP)))
        if np.isnan(u) or u > H_CAP or (u < U_GROUND and rho > 0.3 * rt): break
        rho += STEP
    R[k] = rho
R0 = R.copy()
R = np.minimum(R, np.minimum(np.roll(R, 1), np.roll(R, -1))) * SHRINK   # no chords out over open ground
n = NSEG
FR = [0.0, 0.35, 0.7, 1.0]                      # radial fractions of the top surface
def upt(xz): u = under(*xz); return (0.0 if np.isnan(u) else u) + EPS
topg = []                                        # [frac][k] -> xyz
for f in FR[1:]:
    topg.append([[*(ax + dirs[k] * R[k] * f)] for k in range(n)])
topP = [np.array([[x, ymin + upt((x, z)), z] for x, z in row]) for row in topg]
ct = np.array([[ax[0], ymin + upt(ax), ax[1]]])
edge = topP[-1]
ring = ax + dirs * R[:, None]
def v3(xz, h): return np.column_stack([xz[:, 0], np.full(len(xz), ymin + h), xz[:, 1]])
bot = v3(ring, BOT)
depth = min(DOME, BOT - 0.0005)
mid = v3(ax + (ring - ax) * 0.5, BOT - depth * 0.5)
cb = np.array([[ax[0], ymin + BOT - depth, ax[1]]])
padP = np.vstack([edge, bot,                     # wall: top edge / bottom ring
                  ct, *topP,                     # top surface: center + rings
                  bot, mid, cb])                 # bottom concave disk
o_tw, o_bw = 0, n
c_t = 2 * n; o_t = [c_t + 1 + i * n for i in range(len(topP))]
o_bc = c_t + 1 + len(topP) * n; o_mid = o_bc + n; c_b = o_mid + n
faces = []
for k in range(n):
    k1 = (k + 1) % n
    faces += [[o_tw + k, o_tw + k1, o_bw + k], [o_bw + k, o_tw + k1, o_bw + k1]]
    faces += [[c_t, o_t[0] + k, o_t[0] + k1]]
    for i in range(len(o_t) - 1):
        faces += [[o_t[i] + k, o_t[i + 1] + k, o_t[i] + k1], [o_t[i] + k1, o_t[i + 1] + k, o_t[i + 1] + k1]]
    faces += [[o_bc + k, o_bc + k1, o_mid + k], [o_mid + k, o_bc + k1, o_mid + k1],
              [o_mid + k, o_mid + k1, c_b]]
faces = np.array(faces)
radial = np.column_stack([dirs[:, 0], np.zeros(n), dirs[:, 1]])
padN = np.vstack([radial, radial, np.tile([0, 1, 0], (1 + len(topP) * n, 1)),
                  np.tile([0, -1, 0], (2 * n + 1, 1))]).astype(float)
# orient each face so its geometric normal agrees with the vertex normals
tri = padP[faces]
fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
flip = (fn * padN[faces].mean(1)).sum(1) < 0
faces[flip] = faces[flip][:, [0, 2, 1]]
# bark UVs: nearest original vertex below H_CAP + 0.05
trunk = np.where(y < ymin + H_CAP + 0.05)[0]
dd = ((padP[:, None, :] - P[trunk][None]) ** 2).sum(2)
padUV = UV[trunk[dd.argmin(1)]]
wallh = edge[:, 1] - ymin

# stage 2: webs over the slits between flares and trunk (see roundJ2_webs.py)
nv0 = len(P)
npadv, npadf = len(padP), len(faces)
wV, wF, wst = webs(np.vstack([P, padP]), np.vstack([F, faces + nv0]), ymin, ax, 0.6)
wm = trimesh.Trimesh(wV, wF, process=False)
wN = np.asarray(wm.vertex_normals)
wN = np.where(np.isfinite(wN).all(1, keepdims=True) & (np.linalg.norm(wN, axis=1, keepdims=True) > 0.5), wN, [0, 1, 0])
dd = ((wV[:, None, :] - P[trunk][None]) ** 2).sum(2) if len(wV) else np.zeros((0, 1))
wUV = UV[trunk[dd.argmin(1)]] if len(wV) else np.zeros((0, 2))
faces = np.vstack([faces, wF + len(padP)]) if len(wF) else faces
padP = np.vstack([padP, wV]); padN = np.vstack([padN, wN]); padUV = np.vstack([padUV, wUV])
wV_min = wV[:, 1].min() - ymin if len(wV) else float('nan')

nv = len(P)
P2 = np.vstack([P, padP]).astype('<f4')
N2 = np.vstack([N, padN]).astype('<f4')
N2 /= np.linalg.norm(N2, axis=1, keepdims=True)
UV2 = np.vstack([UV, padUV]).astype('<f4')
I2 = np.concatenate([I, (faces + nv).ravel()]).astype('<u4')
assert P2[:, 1].min() >= np.float32(ymin), 'pad/webs must not lower ymin'

# rebuild BIN: same bufferView order, replacing the four geometry views
repl = {prim['indices']: I2, at['POSITION']: P2, at['TEXCOORD_0']: UV2, at['NORMAL']: N2}
bv_new = {g['accessors'][k]['bufferView']: v for k, v in repl.items()}
out = bytearray()
for i, bv in enumerate(g['bufferViews']):
    chunk = bv_new[i].tobytes() if i in bv_new else B[bv['byteOffset']:bv['byteOffset'] + bv['byteLength']]
    out += b'\0' * ((-len(out)) % 4)
    bv['byteOffset'] = len(out); bv['byteLength'] = len(chunk)
    out += chunk
out += b'\0' * ((-len(out)) % 4)
for k, v in repl.items():
    a = g['accessors'][k]; a['count'] = len(v); a.pop('byteOffset', None)
    if a['type'] != 'SCALAR':
        a['min'] = v.min(0).astype(float).tolist(); a['max'] = v.max(0).astype(float).tolist()
    else:
        a['min'] = [int(v.min())]; a['max'] = [int(v.max())]
g['buffers'][0]['byteLength'] = len(out)
js = json.dumps(g, separators=(',', ':')).encode(); js += b' ' * ((-len(js)) % 4)
glb = (struct.pack('<4sII', b'glTF', 2, 12 + 8 + len(js) + 8 + len(out)) +
       struct.pack('<I', len(js)) + b'JSON' + js + struct.pack('<I', len(out)) + b'BIN\x00' + bytes(out))
open(dst, 'wb').write(glb)
print(f"ROUNDJ2 {src.split('/')[-1]}: arch hits p50/p95={np.percentile(hits,50):.4f}/{np.percentile(hits,95):.4f} "
      f"R med/min/max={np.median(R):.3f}/{R.min():.3f}/{R.max():.3f} (raw max {R0.max():.3f}, rt {rt:.3f}) wall h med/max={np.median(wallh):.3f}/{wallh.max():.3f} "
      f"pad verts={npadv} faces={npadf} concave depth={depth:.4f} (asked {DOME}) "
      f"V {nv}->{len(P2)} F {len(F)}->{len(I2)//3}\n   webs: verts={len(wV)} faces={len(wF)} {wst} min y above ymin={wV_min:.4f}")
