#!/usr/bin/env python3
"""CC-C17v2 step 3 RUIN ACCENT: okRuinArch + 2 okRuinColumn ADDED to the CC-C13b
(-101,-207) church-kit cluster (no removals). Deterministic scan (no RNG): candidate
arc slots around the cluster centre, r 6-11 m step 0.5, angle step 5 deg; pick the
placement that maximises the min distance to every NON-cluster prop.
Gates: CLUSTER ENVELOPE rule (v2 brief) - the cluster centre (mean of the 5 kit rows
+ 3 new) vs non-cluster props >= 26 is reported; the C4a boulder field (16 m) is the
brief's sanctioned tight-cluster case. Per-row sanity: >= 6 m to non-cluster props,
>= 3.5 m to cluster rows, roads >= 35, fires >= 45, loops >= 30 (row), zones 48."""
import math, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe_lib as P
W = P.World()
KIT = [(-101.0, -207.0), (-104.5, -205.0), (-100.5, -210.5), (-98.5, -203.5), (-104.0, -210.0)]
kit_idx = {i for i, (a, x, z) in enumerate(W.props) if (x, z) in KIT}
assert len(kit_idx) == 5, kit_idx
CX = sum(k[0] for k in KIT) / 5; CZ = sum(k[1] for k in KIT) / 5
def row_ok(x, z, others):
    d, w = W.d_props(x, z, skip=kit_idx)
    dk = min(math.hypot(x - kx, z - kz) for kx, kz in KIT + others) if (KIT + others) else 99
    if d < 6 or dk < 3.5: return None
    if W.d_road(x, z)[0] < 35 or W.d_fire(x, z)[0] < 45 or W.d_loop(x, z)[0] < 30: return None
    if min(W.zones(x, z).values()) < 48: return None
    return d
slots = []
for ang in range(0, 360, 5):
    for r2 in [6 + 0.5 * k for k in range(11)]:
        a = math.radians(ang); x, z = CX + r2 * math.sin(a), CZ - r2 * math.cos(a)
        slots.append((ang, r2, round(x, 1), round(z, 1)))
best = None
# arch first (best slot), then 2 columns flanking the arch's axis (+-, 4-6 m off the arch)
for ang, r2, x, z in slots:
    d = row_ok(x, z, [])
    if d is None: continue
    # arch faces the cluster centre (its opening reads from outside in)
    rot = math.atan2(CX - x, CZ - z)
    for off in (5.0, 5.5, 6.0):  # arch half-width 2.6 + column half-width 1.9 = 4.5 -> >= 5.0 (no interpenetration)
        cols = []
        for s in (1, -1):
            cx = x + s * off * math.cos(rot); cz = z - s * off * math.sin(rot)
            cols.append((round(cx, 1), round(cz, 1)))
        dc = [row_ok(c[0], c[1], [(x, z)]) for c in cols]
        if None in dc: continue
        sc = min([d] + dc)
        if best is None or sc > best[0]: best = (sc, ang, r2, x, z, rot, off, cols)
sc, ang, r2, x, z, rot, off, cols = best
print('best min non-cluster prop dist %.1f  arch slot ang %d r %.1f (%.1f, %.1f) rot %.2f col off %.1f' % (sc, ang, r2, x, z, rot, off), cols)
rows = [dict(asset='okRuinArch', x=x, z=z, rotY=round(rot % (2 * math.pi), 2), scale=3.79, cullM=120, _c='CC-C17 ruin arch (7.2 m), opening faces the cluster')]
for i, (cx, cz) in enumerate(cols):
    rows.append(dict(asset='okRuinColumn', x=cx, z=cz, rotY=round((rot + 0.7 + 1.9 * i) % (2 * math.pi), 2), scale=3.95, cullM=120, _c='CC-C17 ruin column (7.5 m) flanking the arch'))
allp = KIT + [(r['x'], r['z']) for r in rows]
ccx = sum(p[0] for p in allp) / len(allp); ccz = sum(p[1] for p in allp) / len(allp)
dcen, who = W.d_props(ccx, ccz, skip=kit_idx)
env = max(math.hypot(p[0] - ccx, p[1] - ccz) for p in allp)
print('cluster centre (%.1f, %.1f) envelope r %.1f -> nearest non-cluster prop %.1f %s; road %.1f fire %.1f loop %.1f zones %s' % (
    ccx, ccz, env, dcen, who, W.d_road(ccx, ccz)[0], W.d_fire(ccx, ccz)[0], W.d_loop(ccx, ccz)[0], {k: round(v, 1) for k, v in W.zones(ccx, ccz).items()}))
for r in rows:
    d, w = W.d_props(r['x'], r['z'], skip=kit_idx); print(' ', r['asset'], r['x'], r['z'], 'non-cluster prop %.1f' % d, w, 'road %.1f loop %.1f' % (W.d_road(r['x'], r['z'])[0], W.d_loop(r['x'], r['z'])[0]))
json.dump(rows, open(os.path.join(P.HERE, 'rows_ruin.json'), 'w'), indent=0)
