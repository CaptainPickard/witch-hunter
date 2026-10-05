#!/usr/bin/env python3
"""Verify the RUNTIME composition exactly as the code will compute it:
q_total = q_existing * qt, qt = setFromUnitVectors(Y -> q_existing^-1 * t).
Check L = exact vertical, R via SRS mirror of q_total."""
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

def qrot(q, v):
    x, y, z, w = q; vx, vy, vz = v
    tx = 2*(y*vz - z*vy); ty = 2*(z*vx - x*vz); tz = 2*(x*vy - y*vx)
    return (vx + w*tx + (y*tz - z*ty), vy + w*ty + (z*tx - x*tz), vz + w*tz + (x*ty - y*tx))

def qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return (aw*bx + ax*bw + ay*bz - az*by,
            aw*by + ay*bw + az*bx - ax*bz,
            aw*bz + az*bw + ax*by - ay*bx,
            aw*bw - ax*bx - ay*by - az*bz)

def qinv(q):
    x, y, z, w = q
    n = x*x + y*y + z*z + w*w
    return (-x/n, -y/n, -z/n, w/n)

def qset_from(u, v):
    # shortest arc u -> v (three.js setFromUnitVectors math)
    dot = u[0]*v[0] + u[1]*v[1] + u[2]*v[2]
    if dot < -0.9995:
        axis = (1, 0, 0)  # arbitrary perpendicular; not hit here
        if abs(axis[0]*u[0]+axis[1]*u[1]+axis[2]*u[2]) > 0.9: axis = (0, 1, 0)
        axis = (axis[1]*u[2]-axis[2]*u[1], axis[2]*u[0]-axis[0]*u[2], axis[0]*u[1]-axis[1]*u[0])
        axis = tuple(c/math.sqrt(sum(c*c for c in axis)) for c in axis)
        return tuple(c*math.sin(math.pi/2) for c in axis) + (0.0,)
    s = math.sqrt(max(0.0, 2*(1+dot)))
    inv = 1/s
    axis = ((u[1]*v[2]-u[2]*v[1])*inv, (u[2]*v[0]-u[0]*v[2])*inv, (u[0]*v[1]-u[1]*v[0])*inv)
    return (axis[0], axis[1], axis[2], s/2)

def mvec(M, v):
    return (M[0][0]*v[0]+M[0][1]*v[1]+M[0][2]*v[2],
            M[1][0]*v[0]+M[1][1]*v[1]+M[1][2]*v[2],
            M[2][0]*v[0]+M[2][1]*v[1]+M[2][2]*v[2])

def mvec_T(M, v):
    return (M[0][0]*v[0]+M[1][0]*v[1]+M[2][0]*v[2],
            M[0][1]*v[0]+M[1][1]*v[1]+M[2][1]*v[2],
            M[0][2]*v[0]+M[1][2]*v[1]+M[2][2]*v[2])

tL = mvec_T(ML, (0, 1, 0))
headAxis = (0, 0, 1)
q_existing = qset_from((0, 1, 0), headAxis)
tgt = qrot(qinv(q_existing), tL)   # q_existing^-1 * t
qt = qset_from((0, 1, 0), tgt)
q_total = qmul(q_existing, qt)
shaft_L = qrot(q_total, (0, 1, 0))         # shaft in hand frame
shaft_L_world = mvec(ML, shaft_L)
print('L: tgt(q^-1*t) =', tuple(round(c, 4) for c in tgt))
print('L: shaft hand   =', tuple(round(c, 4) for c in shaft_L), ' (should equal tL)')
print('L: shaft WORLD  =', tuple(round(c, 4) for c in shaft_L_world))

# R: mirror q_total by SRS
S = [[-1,0,0],[0,1,0],[0,0,1]]
def srs(q):
    # S^T * R(q) * S as quaternion: mirror x-components
    x, y, z, w = q
    # R(S v) for mirrored: (x,y,z,w) -> (-x, y, -z, w)? derive: mirroring a rotation
    # through mirror plane x: R' = S R S. For quaternion (w, xyz): R' = (w, -x, y, -z).
    return (w, -x, y, -z)

def qtup(q4):
    return (q4[1], q4[2], q4[3], q4[0])  # (x,y,z,w) from (w,x,y,z)

qr = srs((q_total[3], q_total[0], q_total[1], q_total[2]))  # input (w,x,y,z)
qR = (qr[1], qr[2], qr[3], qr[0])  # back to (x,y,z,w)
shaft_R = qrot(qR, (0, 1, 0))
shaft_R_world = mvec(MR, shaft_R)
err = math.degrees(math.acos(max(-1, min(1, shaft_R_world[1]))))
print('R: shaft hand   =', tuple(round(c, 4) for c in shaft_R))
print('R: shaft WORLD  =', tuple(round(c, 4) for c in shaft_R_world), ' err=%.2f deg' % err)

# NOTE: runtime mirror uses mirrorQuat = S R S matrix compose on the quat; the
# srs() above is exactly S R S for the x-plane. Confirm same as three.js path.