"""Offline measurement for the left-hand shield mount (Astrabot 10-04).
Shield GLB bounds/face side + L_Hand basis in body space at WH_Idle."""
import struct, json, math
import numpy as np

def load(p):
    d = open(p, 'rb').read()
    jl, = struct.unpack_from('<I', d, 12)
    g = json.loads(d[20:20 + jl])
    bl, = struct.unpack_from('<I', d, 20 + jl)
    return g, d[20 + jl + 8:20 + jl + 8 + bl]

COMP = {5120: 'i1', 5121: 'u1', 5122: 'i2', 5123: 'u2', 5125: 'u4', 5126: 'f4'}
NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}
def acc(g, B, ai):
    a = g['accessors'][ai]; bv = g['bufferViews'][a['bufferView']]
    off = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    nc = NC[a['type']]; dt = np.dtype('<' + COMP[a['componentType']])
    st = bv.get('byteStride')
    if st and st != nc * dt.itemsize:
        return np.array([np.frombuffer(B, dt, nc, off + i * st) for i in range(a['count'])], float)
    return np.frombuffer(B, dt, a['count'] * nc, off).reshape(-1, nc).astype(float)

# ---- shield
g, B = load('art-direction/3d/assets/weapons/round-shield-pixelated.glb')
P = acc(g, B, g['meshes'][0]['primitives'][0]['attributes']['POSITION'])
mn, mx = P.min(0), P.max(0)
print('shield raw min', mn.round(4), 'max', mx.round(4), 'ext', (mx - mn).round(4))
r = np.hypot(P[:, 0], P[:, 1])
core = r < 0.25
print('center-core z mean %.3f  min %.3f max %.3f (n=%d)' % (P[core, 2].mean(), P[core, 2].min(), P[core, 2].max(), core.sum()))
rim = r > 0.85
print('rim z mean %.3f  min %.3f max %.3f' % (P[rim, 2].mean(), P[rim, 2].min(), P[rim, 2].max()))
print('nodes', g['nodes'])

# ---- rig
g, B = load('art-direction/3d/assets/races_regen/rigged/human-hunter-male.combat-chain.glb')
nodes = g['nodes']; parent = {}
for i, n in enumerate(nodes):
    for c in n.get('children', []): parent[c] = i
idx = {n.get('name'): i for i, n in enumerate(nodes)}

def quatm(q):
    x, y, z, w = q
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                     [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                     [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])

def trs(i, ov):
    n = nodes[i]
    t = ov.get((i, 'translation'), n.get('translation', [0, 0, 0]))
    q = ov.get((i, 'rotation'), n.get('rotation', [0, 0, 0, 1]))
    s = ov.get((i, 'scale'), n.get('scale', [1, 1, 1]))
    M = np.eye(4); M[:3, :3] = quatm(q) * np.array(s); M[:3, 3] = t
    return M

def world(i, ov):
    M = trs(i, ov); p = parent.get(i)
    while p is not None:
        M = trs(p, ov) @ M; p = parent.get(p)
    return M

def overrides(clip, frame):
    ov = {}
    A = [a for a in g['animations'] if a['name'] == clip][0]
    for ch in A['channels']:
        s = A['samplers'][ch['sampler']]
        out = acc(g, B, s['output'])
        k = min(frame, len(out) - 1)
        ov[(ch['target']['node'], ch['target']['path'])] = list(out[k])
    return ov

print('armature chain:', [(nodes[j].get('name'), nodes[j].get('scale'), nodes[j].get('rotation')) for j in [idx['WH_Armature'], idx['Root'], idx['Hips']]])
for label, ov in [('rest', {}), ('idle f0', overrides('WH_Idle', 0)), ('idle f15', overrides('WH_Idle', 15))]:
    for h in ['L_Hand', 'R_Hand']:
        M = world(idx[h], ov)
        R = M[:3, :3]; sc = np.linalg.norm(R, axis=0)
        Rn = R / sc
        print('%-8s %s pos %s scale %s' % (label, h, M[:3, 3].round(3), sc.round(4)))
        for nm, v in [('+X', 0), ('+Y', 1), ('+Z', 2)]:
            print('     local %s -> world %s' % (nm, Rn[:, v].round(3)))
# body-forward check (feet toes)

# ---- skinned mesh: hand blob in L_Hand local frame (rest pose = bind)
sn = [i for i, n in enumerate(nodes) if 'mesh' in n and 'skin' in n][0]
skin = g['skins'][nodes[sn]['skin']]
prim = g['meshes'][nodes[sn]['mesh']]['primitives'][0]
PV = acc(g, B, prim['attributes']['POSITION'])
J = acc(g, B, prim['attributes']['JOINTS_0']).astype(int)
W = acc(g, B, prim['attributes']['WEIGHTS_0'])
Mn = world(sn, {})
Pw = (Mn[:3, :3] @ PV.T).T + Mn[:3, 3]
print('mesh node', nodes[sn].get('name'), 'world bounds', Pw.min(0).round(3), Pw.max(0).round(3))
IBM = acc(g, B, skin['inverseBindMatrices']).reshape(-1, 4, 4).transpose(0, 2, 1)
jn = [nodes[j].get('name') for j in skin['joints']]
dom = J[np.arange(len(J)), W.argmax(1)]
def local_blob(bone, frame_bone='L_Hand'):
    k = jn.index(bone); kf = jn.index(frame_bone)
    pts = PV[dom == k]
    # bind-space vertex -> frame bone local via that bone's inverse bind
    loc = (IBM[kf][:3, :3] @ pts.T).T + IBM[kf][:3, 3]
    return loc
for b in ['L_Hand', 'L_Thigh', 'L_Shin', 'Hips']:
    L = local_blob(b)
    print('%-8s in L_Hand-local: centroid %s min %s max %s' % (b, L.mean(0).round(3), L.min(0).round(3), L.max(0).round(3)))

# ---- derive the hand-local shield mount from a body-space target at WH_Idle f0
TURN_FWD_DEG = 20.0     # face = body-left turned this far toward body-forward
SCALE = 1.0 / (mx[1] - mn[1]) if False else None
M = world(idx['L_Hand'], overrides('WH_Idle', 0))
R = M[:3, :3] / np.linalg.norm(M[:3, :3], axis=0)
t = math.radians(TURN_FWD_DEG)
faceW = np.array([math.cos(t), 0, math.sin(t)])     # +X = body left, +Z = forward
upW = np.array([0, 1, 0.])
faceL = R.T @ faceW; upL = R.T @ upW
upL = upL - faceL * (upL @ faceL); upL /= np.linalg.norm(upL)
print('faceAxis (hand-local)', faceL.round(3), ' upAxis', upL.round(3))
fist = local_blob('L_Hand')
c = fist.mean(0)
d = ((fist - c) @ faceL).max()
print('fist centroid', c.round(3), 'fist extent along face %.3f' % d)
GAP = 0.01
off = c + faceL * (d + GAP)
print('offset (shield back plane origin, hand-local)', off.round(3))
# leg clearance: min distance along face from offset plane for thigh/shin verts
for b in ['L_Thigh', 'L_Shin', 'Hips']:
    L = local_blob(b)
    print(b, 'signed dist to back plane (neg = behind plane, good) max %.3f' % ((L - off) @ faceL).max())
