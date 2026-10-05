#!/usr/bin/env python3
"""Measure torch-carry pose: bind axes + lifted-arm shaft direction.
Pure stdlib (no numpy) - hand-rolled 4x4 matrix math on the GLB node TRS."""
import json, struct, math

path = '/tmp/wh-worldfeat/art-direction/3d/assets/races_regen/rigged/human-hunter-male.combat-chain.glb'
with open(path, 'rb') as f:
    data = f.read()
off = 12
chunk_len, chunk_type = struct.unpack('<II', data[off:off+8])
gltf = json.loads(data[off+8:off+8+chunk_len].decode('utf-8'))
nodes = gltf['nodes']
names = [n.get('name', '') for n in nodes]

def qmat(x, y, z, w):
    return [
        [1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w), 0],
        [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w), 0],
        [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y), 0],
        [0, 0, 0, 1],
    ]

def mat_mul(a, b):
    out = [[0.0]*4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            out[i][j] = sum(a[i][k]*b[k][j] for k in range(4))
    return out

def rot_local_x(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]]

def trs(n):
    t = n.get('translation', [0, 0, 0])
    r = n.get('rotation', [0, 0, 0, 1])
    s = n.get('scale', [1, 1, 1])
    m = qmat(*r)
    for i in range(3):
        for j in range(3):
            m[i][j] *= s[j]
    m[0][3], m[1][3], m[2][3] = t
    return m

IDENT = [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]

def chain_world(bone_names, lift=0.0, bend=0.0):
    M = IDENT
    for b in bone_names:
        m = trs(nodes[names.index(b)])
        if b.endswith('UpperArm') and lift:
            m = mat_mul(m, rot_local_x(lift))
        if b.endswith('Forearm') and bend:
            m = mat_mul(m, rot_local_x(bend))
        M = mat_mul(M, m)
    return M

def axes(M):
    return (round(M[0][0], 3), round(M[1][0], 3), round(M[2][0], 3)), \
           (round(M[0][1], 3), round(M[1][1], 3), round(M[2][1], 3)), \
           (round(M[0][2], 3), round(M[1][2], 3), round(M[2][2], 3))

chain = ['L_Shoulder', 'L_UpperArm', 'L_Forearm', 'L_Hand']
for tag, lift, bend in (('bind', 0, 0), ('lift65/bend15', 65, 15), ('lift75/bend20', 75, 20)):
    M = chain_world(chain, lift, bend)
    x, y, z = axes(M)
    hx, hy, hz = M[0][3], M[1][3], M[2][3]
    # shaft = hand-local +Z (headAxis) in world
    shaft = (M[0][2], M[1][2], M[2][2])
    ang = math.degrees(math.acos(max(-1.0, min(1.0, shaft[1]))))
    print(f'{tag}: handX={x} handY={y} handZ(shaft)={z}')
    print(f'   hand pos=({hx:.3f},{hy:.3f},{hz:.3f})  angle(shaft,world+Y)={ang:.1f}deg')

# Right-hand mirror sanity: lift about right UpperArm local X should also raise.
Mr = chain_world(['R_Shoulder', 'R_UpperArm', 'R_Forearm', 'R_Hand'], 65, 15)
z = (Mr[0][2], Mr[1][2], Mr[2][2])
angR = math.degrees(math.acos(max(-1.0, min(1.0, z[1]))))
print(f'R-hand lift65/bend15: shaft={tuple(round(c,3) for c in z)} angle->Y={angR:.1f}deg')