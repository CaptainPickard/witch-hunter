#!/usr/bin/env python3
"""Verify mirrored straightening: SRS(qShaft) on the R chain with lift65+bend15
=> shaft world == (0,1,0)? Also exact t_R from M_R^T * Y."""
import json, struct, math

path = '/tmp/wh-worldfeat/art-direction/3d/assets/races_regen/rigged/human-hunter-male.combat-chain.glb'
with open(path, 'rb') as f:
    data = f.read()
off = 12
chunk_len, _ = struct.unpack('<II', data[off:off+8])
gltf = json.loads(data[off+8:off+8+chunk_len].decode('utf-8'))
nodes = gltf['nodes']
names = [n.get('name', '') for n in nodes]

def qmat(x, y, z, w):
    return [[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w), 0],
            [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w), 0],
            [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y), 0],
            [0, 0, 0, 1]]

def mat_mul(a, b):
    return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]

def rot_local_x(deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return [[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]]

def trs(n):
    t = n.get('translation', [0, 0, 0]); r = n.get('rotation', [0, 0, 0, 1]); s = n.get('scale', [1, 1, 1])
    m = qmat(*r)
    for i in range(3):
        for j in range(3):
            m[i][j] *= s[j]
    m[0][3], m[1][3], m[2][3] = t
    return m

IDENT = [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]

def chain(side, lift, bend):
    ch = [f'{side}_Shoulder', f'{side}_UpperArm', f'{side}_Forearm', f'{side}_Hand']
    M = IDENT
    for b in ch:
        m = trs(nodes[names.index(b)])
        if b.endswith('UpperArm'): m = mat_mul(m, rot_local_x(lift))
        if b.endswith('Forearm'): m = mat_mul(m, rot_local_x(bend))
        M = mat_mul(M, m)
    return M

ML = chain('L', 65, 15)
MR = chain('R', 65, 15)

def mvec(M, v):
    return (M[0][0]*v[0]+M[0][1]*v[1]+M[0][2]*v[2],
            M[1][0]*v[0]+M[1][1]*v[1]+M[1][2]*v[2],
            M[2][0]*v[0]+M[2][1]*v[1]+M[2][2]*v[2])

def mvec_T(M, v):  # M^T * v
    return (M[0][0]*v[0]+M[1][0]*v[1]+M[2][0]*v[2],
            M[0][1]*v[0]+M[1][1]*v[1]+M[2][1]*v[2],
            M[0][2]*v[0]+M[1][2]*v[1]+M[2][2]*v[2])

tL = mvec_T(ML, (0, 1, 0))
tR = mvec_T(MR, (0, 1, 0))
print('tL =', tuple(round(c, 4) for c in tL))
print('tR =', tuple(round(c, 4) for c in tR))
print('mirror(tL) =', (-tL[0], tL[1], tL[2]))
print('tR vs mirror(tL) delta =', tuple(round(tR[i]-(-tL[0], tL[1], tL[2])[i], 4) for i in range(3)))

# apply qShaft (built from L) premultiplied; mirrored hand uses mirrorQuat(qShaft)
# rotation of shaft dir: shaft hand-local starts at Z; q: Z -> t
shaft_L = mvec(ML, tL)
shaft_R = mvec(MR, tR)
print('L shaft world with exact tL =', tuple(round(c, 4) for c in shaft_L))
print('R shaft world with exact tR =', tuple(round(c, 4) for c in shaft_R))

# Now the RUNTIME path: q_straight built ONCE from L (setFromUnitVectors Z->tL),
# mirrored via SRS for R: mapping Z -> mirror(tL). Apply to R chain:
# shaft_R_runtime = MR * mirror(tL)
mt = (-tL[0], tL[1], tL[2])
shaft_R_m = mvec(MR, mt)
err = math.degrees(math.acos(max(-1, min(1, shaft_R_m[1]))))
print('R shaft world via mirrored tL =', tuple(round(c, 4) for c in shaft_R_m),
      ' error from vertical = %.2f deg' % err)

# And if runtime instead uses tR (per-axis CONFIG pair): exact 0 for both.
# Deg error if R uses raw L t (no mirror at all, same quat both hands):
shaft_R_raw = mvec(MR, tL)
err2 = math.degrees(math.acos(max(-1, min(1, shaft_R_raw[1]))))
print('R shaft world via raw L t    =', tuple(round(c, 4) for c in shaft_R_raw),
      ' error = %.2f deg' % err2)