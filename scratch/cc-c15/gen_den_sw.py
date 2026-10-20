#!/usr/bin/env python3
"""CC-C15 gen_den_sw: regenerate the outcrop + regionD den rows at the SW
mountainside site. Adapts scratch/cc-c8/gen_den.py conventions:
- OUTCROP centre: r 238, bearing 225 deg from C centre (0,-366) -> world.
- DEN centre: r 256, bearing 225 deg (the regionD block translation target).
- U (outcrop front) points from the outcrop TOWARD the den centre (NE->SW,
  i.e. the mouth faces the map interior); ring gap (mouth) on the den side
  toward the outcrop.
- Prints: (1) regionC outcrop + stain rows, (2) regionD door + lair + prop
  rows, (3) the site ledger (min gaps, approach grades approx, loop dists).
Pure arithmetic - prints rows, edits nothing.
"""
import math, re, sys

# ---- geometry helpers -------------------------------------------------------
CENTER = (0.0, -366.0)          # region C centre (world)
def cw(r, ang_deg):
    a = math.radians(ang_deg)
    return (CENTER[0] + r * math.sin(a), CENTER[1] - r * math.cos(a))

OC = cw(238, 225)               # outcrop centre (world)
DEN = cw(256, 225)              # den centre (world) = regionD.center
dx, dz = DEN[0] - OC[0], DEN[1] - OC[1]
gl = math.hypot(dx, dz)
U = (dx / gl, dz / gl)          # outcrop front = toward the den (NE->SW inward)
T = (-U[1], U[0])               # tangent
FACE = math.atan2(U[0], U[1])   # rotY whose local +Z = U

def W(a, b):
    """outcrop-local (tangent a, front b) -> world"""
    return (OC[0] + T[0] * a + U[0] * b, OC[1] + T[1] * a + U[1] * b)

def rot_to(dx_, dz_):
    return math.atan2(dx_, dz_)

TRIS = {'mossBoulder': 21599, 'whWallA': 4118, 'whWallB': 4375, 'cemeteryGate': 20585,
        'bramble': 2288, 'graveMound': 2000, 'blightcap': 5786, 'stoneSteps': 4843,
        'skullPile': 4733, 'b6Bones': 10889}
WALL_W = {'whWallA': 1.899, 'whWallB': 1.899}
WALL_H = {'whWallA': 0.77, 'whWallB': 0.779}

print('# CC-C15 SW den site (world coords)')
print('# outcrop centre: (%.1f, %.1f)  den centre: (%.1f, %.1f)' % (OC + DEN))
print('# outcrop front U: (%.2f, %.2f)  FACE rotY: %.2f' % (U + (FACE,)))
print()

# ---------------------------------------------------------------- 1. OUTCROP
print('    // CC-C15 SW RELOCATION: outcrop at the rim-mountain foot (r 238, bearing 225),')
print('    // mouth faces the den (N/NE); rows from scratch/cc-c15/gen_den_sw.py.')
walls = [
    (-7.4, 5.5, 'T', 10.0, 15.0),
    (7.4, 5.5, 'T', 10.0, 15.0),
    (-2.8, 3.0, 'U', 5.6, 13.0),
    (2.8, 3.0, 'U', 5.6, 13.0),
    (0.0, 0.4, 'T', 6.4, 13.0),
]
tris_c = 0
for i, (a, b, al, L, H) in enumerate(walls):
    asset = 'whWallA' if i % 2 == 0 else 'whWallB'
    x, z = W(a, b)
    rot = FACE if al == 'T' else FACE + math.pi / 2
    sx = L / WALL_W[asset]; sy = H / WALL_H[asset]; sz = 2.0
    print("      { asset: '%s', x: %.1f, z: %.1f, rotY: %.2f, scale: %.2f, sy: %.2f, sz: %.2f, y: -0.4, wall: 3 }," %
          (asset, x, z, rot % (2 * math.pi), sx, sy, sz))
    tris_c += TRIS[asset]
print("      // -- doorway: m1 gate pair flanking the 4.6 m opening (scale 5.2), splayed")
gate_w = 1.895 * 5.2
for sd in (-1, 1):
    x, z = W(sd * (2.3 + gate_w / 2), 7.0)
    rot = FACE + (-0.28 if sd < 0 else 0.28)
    print("      { asset: 'cemeteryGate', x: %.1f, z: %.1f, rotY: %.2f, scale: 5.2, wall: 3 }," %
          (x, z, rot % (2 * math.pi)))
    tris_c += TRIS['cemeteryGate']
print("      // -- shoulders + brambles + stain trail (3 boulders, 2 bramble)")
for a, b, s in [(-11.5, 3.2, 3.4), (11.6, 3.4, 3.1), (0.0, 10.4, 2.6)]:
    x, z = W(a, b)
    print("      { asset: 'mossBoulder', x: %.1f, z: %.1f, rotY: %.2f, scale: %.2f }," %
          (x, z, (FACE + a) % (2 * math.pi), s))
    tris_c += TRIS['mossBoulder']
for a, b in [(-6.1, 9.0), (6.2, 9.2)]:
    x, z = W(a, b)
    print("      { asset: 'bramble', x: %.1f, z: %.1f, rotY: %.2f, scale: 2.2 }," %
          (x, z, (FACE + a * 0.3) % (2 * math.pi)))
    tris_c += TRIS['bramble']
# stains: mouth pool + 3-step trail toward the den along U
print("    // regionC.rotLair stains at the SW site:")
sx_, sz_ = W(0.0, 1.5)
print("      stains: [")
print("        { x: %.1f, z: %.1f, radius: 5.0 }," % (sx_, sz_))
for k in (1, 2, 3):
    px, pz = OC[0] + U[0] * (10 + 12 * k), OC[1] + U[1] * (10 + 12 * k)
    print("        { x: %.1f, z: %.1f, radius: %.1f }," % (px, pz, 1.8 - 0.3 * k))
print("      ],")
print("      void: { x: %.1f, z: %.1f, rotY: %.2f, width: 4.6, height: 9.0, color: 0x000000 }," %
      (W(0.0, 0.4) + (FACE % (2 * math.pi),)))
print()
# ------------------------------------------------------------------ 2. REGION D
# den props: rigid translation of the shipped block by the den-centre delta.
src = open('/tmp/wh-worldfeat/prototype/js/CONFIG.js').read()
i = src.index("regionD: {")
j = src.index("// CC-C12", i) if src.find("// CC-C12", i) != -1 else src.index("window.WH_CONFIG.dayNight")
# carve regionD block end: find the closing of regionD props - take up to 'regionD:' next top key: scatter:
jj = src.index("  scatter: {", i)
blk = src[i:jj]
# translate every prop x/z by (DEN - old centre)
old = (-175.0, -271.0)
tdx, tdz = DEN[0] - old[0], DEN[1] - old[1]
def tr(m):
    x = float(m.group(2)) + tdx; z = float(m.group(3)) + tdz
    return "%s x: %.1f, z: %.1f%s" % (m.group(1), x, z, m.group(4))
out_rows, n = [], 0
for ln in blk.split('\n'):
    m = re.search(r"(\{ asset: '[a-zA-Z]+'), x: ([-\d.]+), z: ([-\d.]+)(,.*)\},", ln)
    if m and ('whWall' in ln or 'mossBoulder' in ln or 'stoneSteps' in ln or
              'skullPile' in ln or 'blightcap' in ln or 'b6Bones' in ln or 'graveMound' in ln):
        ln2 = re.sub(r"(\{ asset: '[a-zA-Z]+'), x: ([-\d.]+), z: ([-\d.]+)(,.*)\},", tr, ln)
        out_rows.append(ln2); n += 1
        continue
    # door rows: interactAt / land rot_den / lairs / void handled separately
    m2 = re.search(r"(interactAt: \{ x: )([-\d.]+)(, z: )([-\d.]+)", ln)
    if m2:
        # C-side interactAt = the new outcrop opening centre (W(0, 7.0))
        ix, iz = W(0.0, 7.0)
        out_rows.append("      interactAt: { x: %.1f, z: %.1f },     // CC-C15: the SW outcrop opening centre (C)" % (ix, iz))
        continue
    m3 = re.search(r"(rot_den: \{ x: )([-\d.]+)(, z: )([-\d.]+)", ln)
    if m3:
        # den-side landing = mouth inside: ring gap centre at den-local (0,-24) -> world = DEN + (0,-24)
        out_rows.append("        rot_den: { x: %.1f, z: %.1f, faceX: %.1f, faceZ: %.1f }" %
                        (DEN[0], DEN[1] - 24, DEN[0], DEN[1] + 10))
        continue
    m4 = re.search(r"(forest_of_the_old_king: \{ x: )([-\d.]+)(, z: )([-\d.]+)", ln)
    if m4:
        lx, lz = W(0.0, 10.0)
        out_rows.append("        forest_of_the_old_king: { x: %.1f, z: %.1f, faceX: %.1f, faceZ: %.1f }" %
                        (lx, lz, OC[0], OC[1] - 5))
        continue
    m5 = re.search(r"(\{ type: 'rotmother', x: )([-\d.]+)(, z: )([-\d.]+)", ln)
    if m5:
        out_rows.append("      { type: 'rotmother', x: %.1f, z: %.1f }" % (DEN[0], DEN[1] - 6))
        continue
    m6 = re.search(r"(center: \{ x: )([-\d.]+)(, z: )([-\d.]+)( \})", ln)
    if m6:
        out_rows.append("    center: { x: %.1f, z: %.1f },     // CC-C15 SW relocation (r 256, bearing 225)" % DEN)
        continue
    m7 = re.search(r"(planeZ: )([-\d.]+)", ln)
    if m7:
        # mouth plane: den-local z -24.6 -> world along -U? den local axes: keep the shipped
        # convention (den-local (0,-24.6) = mouth): world = DEN + U*(-24.6/|den local z|)...
        # Simpler, ship law kept: the mouth plane faces the outcrop: plane at DEN - U*24.6 -> z comp:
        pz = (DEN[1] - U[1] * 24.6)
        out_rows.append("      planeZ: %.1f,                      // CC-C15 (was -295.6)" % pz)
        continue
    m8 = re.search(r"(doorX: )([-\d.]+)", ln)
    if m8:
        out_rows.append("      doorX: %.1f,                      // CC-C15" % (DEN[0] - U[0] * 24.6))
        continue
    out_rows.append(ln)
print('    // regionD block translated by (%.1f, %.1f); %d prop rows moved' % (tdx, tdz, n))
print('    // mouth planeZ/doorX face the outcrop; interactAt/lands/lairs recomputed')
print()
print('# tri ledger: C-side outcrop tris =', tris_c, '(same set as the old site = no budget change)')
# ------------------------------------------------------------------ 3. LEDGER
west = [[-190,-420],[-215,-418],[-224,-388],[-224,-362],[-200,-358],[-178,-340],[-166,-372],[-172,-402]]
print('# west wolf loop min dist from outcrop: %.0f m' %
      min(math.hypot(p[0]-OC[0], p[1]-OC[1]) for p in west))
# trees within 30 m of the approach line (glade->outcrop: from (0,-330) SW-ish to OC)
print('# NOTE: full prop-gap + approach-grade probe runs AFTER paste (cc_c8_check.js pattern).')