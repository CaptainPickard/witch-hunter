#!/usr/bin/env python3
"""CC-C8 offline row generator (io/missions/2026-10-12-cc-c8-rotmother-den.md).
Prints the CONFIG rows for (1) the region C outcrop + doorway + stain trail and
(2) the regionD den build (ring + shoulders + furniture + nest egg sacs), plus
a site check of the outcrop vs region C's giant trunk rows and a tri ledger.
Usage: python3 -I scratch/cc-c8/gen_den.py prototype/js/CONFIG.js
No game run, no browser: pure arithmetic over CONFIG text + measured GLB tris.
"""
import math, re, sys

CFG = open(sys.argv[1]).read() if len(sys.argv) > 1 else ''

# measured GLB tris (scratch/cc-c8/glb_tris.py) + raw extents (x width, y height, z depth)
TRIS = {'mossBoulder': 21599, 'whWallA': 4118, 'whWallB': 4375, 'cemeteryGate': 20585,
        'bramble': 2288, 'graveMound': 2000, 'blightcap': 5786, 'stoneSteps': 4843,
        'skullPile': 4733, 'b6Bones': 10889}
WALL_W = {'whWallA': 1.899, 'whWallB': 1.899}
WALL_H = {'whWallA': 0.77, 'whWallB': 0.779}

def r2(v): return round(v + 0.0, 2)

def row(asset, x, z, rotY, scale, extra=''):
    return "      { asset: '%s', x: %.1f, z: %.1f, rotY: %.2f, scale: %.2f%s }," % (
        asset, x, z, rotY % (2 * math.pi), scale, extra)

# ---------------------------------------------------------------- 1. OUTCROP
OC = (-136.0, -219.0)                       # outcrop centre (C-local (-136, +147))
GLADE = (-175.0, -271.0)                    # the old open lair (C-local (-175, +95))
gx, gz = GLADE[0] - OC[0], GLADE[1] - OC[1]
gl = math.hypot(gx, gz)
U = (gx / gl, gz / gl)                      # front = toward the glade (SW)
T = (-U[1], U[0])                           # tangent (a axis)
FACE = math.atan2(U[0], U[1])               # rotY whose local +Z = U (front face out)

def W(a, b):
    return (OC[0] + T[0] * a + U[0] * b, OC[1] + T[1] * a + U[1] * b)

out = []
tris_c = 0
out.append('      // -- outcrop wall core: 5 vinestone segments, per-axis (scale = length,')
out.append('      //    sy = height, sz = thickness; wall = collider circles r 0.45 along it)')
walls = [  # (a, b, along, lengthM, heightM)
    (-7.4, 5.5, 'T', 10.0, 15.0),           # front-left facade
    (7.4, 5.5, 'T', 10.0, 15.0),            # front-right facade
    (-2.8, 3.0, 'U', 5.6, 13.0),            # recess left
    (2.8, 3.0, 'U', 5.6, 13.0),             # recess right
    (0.0, 0.4, 'T', 6.4, 13.0),             # recess back (the black void card hangs before it)
]
for i, (a, b, al, L, H) in enumerate(walls):
    asset = 'whWallA' if i % 2 == 0 else 'whWallB'
    x, z = W(a, b)
    rot = FACE if al == 'T' else FACE + math.pi / 2
    sx = L / WALL_W[asset]; sy = H / WALL_H[asset]; sz = 2.0
    out.append("      { asset: '%s', x: %.1f, z: %.1f, rotY: %.2f, scale: %.2f, sy: %.2f, sz: %.2f, y: -0.4, wall: 3 },"
               % (asset, x, z, rot % (2 * math.pi), sx, sy, sz))
    tris_c += TRIS[asset]
out.append('      // -- doorway: m1 gate pair flanking the 4.6 m opening (scale 5.2), splayed')
gate_w = 1.895 * 5.2
for sd in (-1, 1):
    x, z = W(sd * (2.3 + gate_w / 2), 7.0)
    out.append(row('cemeteryGate', x, z, FACE - sd * 0.12, 5.2))
    tris_c += TRIS['cemeteryGate']
out.append('      // -- lintel mass over the opening (raised; noCollide keeps the lane open)')
x, z = W(0.0, 6.4)
out.append(row('mossBoulder', x, z, FACE + 0.4, 1.6, ', y: 7.0, noCollide: true'))
tris_c += TRIS['mossBoulder']
out.append('      // -- horseshoe: 7 mossBoulder against the core sides + back')
shoe = [(-13.0, 3.0, 2.2), (-12.0, -2.5, 1.8), (-6.5, -4.5, 2.0), (0.0, -5.0, 1.4),
        (6.5, -4.5, 2.1), (12.0, -2.5, 1.6), (13.0, 3.0, 2.0)]
for k, (a, b, s) in enumerate(shoe):
    x, z = W(a, b)
    out.append(row('mossBoulder', x, z, FACE + 0.9 * k, s))
    tris_c += TRIS['mossBoulder']
out.append('      // -- the blackened face: 6 bramble + 4 rot egg sacs (graveMound, rot tint) at the mouth')
br = [(-3.4, 8.4, 1.8), (3.4, 8.2, 2.1), (-4.9, 10.2, 1.4), (4.8, 10.4, 2.4), (-1.9, 11.8, 1.6), (2.2, 12.6, 1.5)]
for k, (a, b, s) in enumerate(br):
    x, z = W(a, b)
    out.append(row('bramble', x, z, FACE + 1.3 * k, s))
    tris_c += TRIS['bramble']
eg = [(-3.6, 12.6), (4.0, 11.8), (-6.0, 9.0), (6.2, 13.4)]
for k, (a, b) in enumerate(eg):
    x, z = W(a, b)
    out.append(row('graveMound', x, z, FACE + 2.1 * k, 1.1, ', tint: 0x6f7a4a'))
    tris_c += TRIS['graveMound']

door = W(0.0, 6.0)                         # interact point (opening centre)
land_c = W(0.0, 11.0)                       # exit landing in C (out of the 3.5 m prompt)
face_c = W(0.0, 20.0)
void = W(0.0, 0.9)
mouth = W(0.0, 9.5)
gedge = (GLADE[0] - U[0] * 12, GLADE[1] - U[1] * 12)   # old pool rim (r 12) facing the outcrop
trail = []
for f, r in ((0.22, 1.8), (0.5, 1.4), (0.78, 1.0)):   # mouth pool edge -> glade edge
    sx_, sz_ = mouth[0] + U[0] * 5.0, mouth[1] + U[1] * 5.0
    trail.append((sx_ + (gedge[0] - sx_) * f, sz_ + (gedge[1] - sz_) * f, r))

print('// ===== region C outcrop rows (%d rows) =====' % sum(1 for l in out if l.strip().startswith('{')))
print('\n'.join(out))
print('// interact point', [r2(v) for v in door], ' exit landing', [r2(v) for v in land_c],
      ' face', [r2(v) for v in face_c])
print('// void card', [r2(v) for v in void], ' rotY %.2f' % (FACE % (2 * math.pi)))
print('// mouth pool', [r2(v) for v in mouth], ' trail', [(r2(a), r2(b), r) for a, b, r in trail])
print('// glade edge', [r2(v) for v in gedge], ' U', [round(v, 3) for v in U], ' FACE %.3f' % FACE)

# giant trunk rows (yew / witchwood / deadTree) vs the outcrop pieces
giants = []
for m in re.finditer(r"\{ asset: '(yewTree|witchwoodTree|deadTree|treeStump|mossBoulder)',\s*x: (-?[\d.]+), z: (-?[\d.]+)", CFG):
    if CFG[:m.start()].rfind('// C4b-CLIFF') > CFG[:m.start()].rfind('\n'):
        continue
    giants.append((m.group(1), float(m.group(2)), float(m.group(3))))
near = sorted((math.hypot(x - OC[0], z - OC[1]), n, x, z) for n, x, z in giants)
print('// nearest trunk/rock rows to the outcrop centre:', [(round(d, 1), n, x, z) for d, n, x, z in near[:5]])
for name, pt in (('door', door), ('mouth', mouth)) + tuple(('trail%d' % i, (a, b)) for i, (a, b, r) in enumerate(trail)):
    d = min(math.hypot(x - pt[0], z - pt[1]) for n, x, z in giants)
    print('//   %s nearest trunk/rock row %.1f m' % (name, d))

# ---------------------------------------------------------------- 2. DEN
DC = (-175.0, -271.0)
R = 24.0
GAP = 4.6
th_gap = math.atan2(-24.0, 0.0)                 # local (0, -24): world z = cz + r sin th
half = math.asin((GAP / 2 + 0.6) / R)           # opening + the wall end's half-thickness
arc = 2 * math.pi - 2 * half
N = 10
d_th = arc / N
den = []
tris_d = 0
den.append('      // -- cavern ring: 10 vinestone segments r 24 (heightM 9, thickness scale 2.4),')
den.append('      //    the exit gap (4.6 m) at local (0, -24) = the open-arch pattern (no segment)')
for i in range(N):
    th = th_gap + half + d_th * (i + 0.5)
    chord = 2 * R * math.sin(d_th / 2) + 0.6
    asset = 'whWallA' if i % 2 == 0 else 'whWallB'
    x = DC[0] + R * math.cos(th); z = DC[1] + R * math.sin(th)
    rot = -th - math.pi / 2                       # local +Z faces the den centre
    sx = chord / WALL_W[asset]; sy = 9.0 / WALL_H[asset]
    nC = int(math.ceil(chord / 2.0))
    den.append("      { asset: '%s', x: %.1f, z: %.1f, rotY: %.2f, scale: %.2f, sy: %.2f, sz: 2.40, y: -0.2, wall: %d },"
               % (asset, x, z, rot % (2 * math.pi), sx, sy, nC))
    tris_d += TRIS[asset]
den.append('      // -- 9 mossBoulder shoulders at the wall foot (r 20.5-21.5), clear of the mouth')
for k in range(9):
    th = th_gap + 0.62 + (2 * math.pi - 1.24) * k / 8
    rr = 20.5 + (k % 2)
    s = 1.6 + 0.8 * ((k * 37) % 9) / 8
    den.append(row('mossBoulder', DC[0] + rr * math.cos(th), DC[1] + rr * math.sin(th), 0.7 * k, s))
    tris_d += TRIS['mossBoulder']
den.append('      // -- brood furniture: 4 stone-steps, 2 skull-piles, 3 egg sacs, 6 blightcap')
# den-local (x, z): z + toward the nest; the mouth lane |x| < 5 for z < -4 stays open
furn = [('stoneSteps', -12.0, -14.0, 1.2), ('stoneSteps', 13.5, -12.0, 1.1),
        ('stoneSteps', -17.0, 4.0, 1.3), ('stoneSteps', 16.0, 8.0, 1.2),
        ('skullPile', -9.0, -17.0, 1.0), ('skullPile', 10.5, 18.0, 1.1),
        ('graveMound', -15.0, -6.0, 1.1), ('graveMound', 15.0, -3.0, 1.0), ('graveMound', -6.0, 19.5, 1.2),
        ('blightcap', -7.5, -11.0, 0.9), ('blightcap', 8.0, -15.5, 1.1), ('blightcap', -16.5, 12.0, 1.2),
        ('blightcap', 17.0, 15.0, 0.8), ('blightcap', 4.0, 19.0, 1.0), ('blightcap', -12.5, -1.0, 0.9)]
for k, (a, lx, lz, s) in enumerate(furn):
    extra = ', tint: 0x6f7a4a' if a == 'graveMound' else ''
    den.append(row(a, DC[0] + lx, DC[1] + lz, 1.1 * k, s, extra))
    tris_d += TRIS[a]
den.append('      // -- the nest (den-local (0, +6)): 5 egg sacs ring r 7.5 (moved in from the open lair)')
NEST = (DC[0], DC[1] + 6.0)
for k in range(5):
    th = math.pi / 2 + 2 * math.pi * k / 5 + 0.3
    den.append(row('graveMound', NEST[0] + 7.5 * math.cos(th), NEST[1] + 7.5 * math.sin(th), 1.7 * k, 1.1,
                   ', tint: 0x6f7a4a'))
    tris_d += TRIS['graveMound']
print('// ===== regionD den rows =====')
print('\n'.join(den))
print('// gap edges th', round(th_gap - half, 3), round(th_gap + half, 3), ' exit plane z %.1f' % (DC[1] - R - 0.6))

# ---------------------------------------------------------------- 3. LEDGER
removed = 6 * TRIS['b6Bones']
print('// LEDGER region C: outcrop + %d, - 6 b6Bones %d, - rotmother body 17573 + 3 spawn 6282 (now den-only)'
      % (tris_c, removed))
print('//   net C = %+d' % (tris_c - removed - 17573 - 6282))
print('// LEDGER regionD (own region; C is hidden/not drawn while inside): %d + boss 17573 + 3 spawn 6282 = %d'
      % (tris_d, tris_d + 17573 + 6282))
