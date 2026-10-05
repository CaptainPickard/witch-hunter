#!/usr/bin/env python3
"""Exact shaft-straightening roll: after lift65+bend15, find the hand-local
rotation that brings the torch shaft to true world-vertical. Verifies."""
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

chain = ['L_Shoulder', 'L_UpperArm', 'L_Forearm', 'L_Hand']
M = IDENT
for b in chain:
    m = trs(nodes[names.index(b)])
    if b.endswith('UpperArm'):
        m = mat_mul(m, rot_local_x(65))
    if b.endswith('Forearm'):
        m = mat_mul(m, rot_local_x(15))
    M = mat_mul(M, m)

# t_target: hand-local dir mapping to world +Y  =>  M^T * [0,1,0]
t = (M[1][0], M[1][1], M[1][2])
n = math.sqrt(sum(c*c for c in t))
t = (t[0]/n, t[1]/n, t[2]/n)
print('t_target (hand-local) =', tuple(round(c, 4) for c in t))

# minimal rotation qShaft: from [0,0,1] to t
shaft = (0.0, 0.0, 1.0)
dot = max(-1.0, min(1.0, shaft[2] * t[2] + shaft[1] * t[1] + shaft[0] * t[0]))
ang = math.acos(dot)
axis = (0*t[2] - 1*t[1], 1*t[0] - 0*t[2], 0*t[1] - 0*t[0])  # cross([0,0,1], t)
an = math.sqrt(sum(c*c for c in axis))
axis = (axis[0]/an, axis[1]/an, axis[2]/an)
deg = math.degrees(ang)
print('qShaft: axis =', tuple(round(c, 4) for c in axis), ' deg =', round(deg, 4))

# verify: rotate [0,0,1] by qShaft -> t, then M*t -> vertical
def qrot(q, v):
    x, y, z, w = q; vx, vy, vz = v
    tx = 2*(y*vz - z*vy); ty = 2*(z*vx - x*vz); tz = 2*(x*vy - y*vx)
    return (vx + w*tx + (y*tz - z*ty), vy + w*ty + (z*tx - x*tz), vz + w*tz + (x*ty - y*tx))

q = (axis[0]*math.sin(ang/2), axis[1]*math.sin(ang/2), axis[2]*math.sin(ang/2), math.cos(ang/2))
t2 = qrot(q, (0, 0, 1))
print('t after qShaft        =', tuple(round(c, 4) for c in t2))
w = M[0][2]*t2[0] + M[0][1]*t2[1] + M[0][0]*t2[2]  # placeholder guard
# M * t2 (column-vector): result_j = sum_i M[j][i] * t2[i]
shaftw = (M[0][0]*t2[0] + M[0][1]*t2[1] + M[0][2]*t2[2],
          M[1][0]*t2[0] + M[1][1]*t2[1] + M[1][2]*t2[2],
          M[2][0]*t2[0] + M[2][1]*t2[1] + M[2][2]*t2[2])
print('shaft world (want 0,1,0) =', tuple(round(c, 4) for c in shaftw))