#!/usr/bin/env python3
"""CC-C17v2 step 5 SPOOKY DRESSING (existing manifest assets only).
(a) den corridor: 2 deadTree + 2 blightcap + 1 skullPile in the bearing-225 band,
    r 200-235 from the Stone, mutually spaced >= 26 m (brief). A 26 m gate vs EVERY
    prop is infeasible in this band (scan: 3 grid points of 3,321 clear, all one
    spot) - the outcrop + 2 giants + the camp-3 fire crowd it - so the prop gate
    here is the dressing gate: >= 10 m to every prop row (outcrop rows included),
    den opening >= 12 m, rot stains >= 4 m + radius, corridor axis (bearing 225
    line) lateral >= 6 m (the walking line stays open) and <= 32 m, fires >= 26,
    loops >= 20, camp-3 guards >= 12. Selection: seeded search (random.Random
    20261020, 4000 draws) maximising the min prop distance; deadTrees one per
    side of the axis.
(b) ring fragment: 3 mossBoulder (scale 2.2-2.8) on an 8 m arc (+-0.75 rad: ~5.8 m chords, no overlap), half-swallowed
    (y sink = 0.3 x height) at the ridge, nominal bearing 200 r 238; fragment
    centre = the cluster gate (props >= 26), rows >= 10 m to props, slope <=
    31 deg, nearest clear slot to the nominal (deterministic scan)."""
import math, json, sys, os, random, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe_lib as P
W = P.World()
# the brief's deadTree (30,174 tris). It fits the ledger only after the ROW SHAPE LAW
# alignment (scratch/cc-c17/apply_giant_cull.py: giants cullM 140); before it, 2 deadTree
# with NO fragment = 2,006,979 (100.35%) on the west plateau.
DEAD = 'deadTree'
RL = W.cfg['rotLair']
GUARDS = [(e['x'], e['z']) for e in W.cfg['enemies'] if e['type'] == 'bandit' and P.dist((e['x'], e['z']), (-207.8, -246)) < 15]
AX = (math.sin(math.radians(225)), -math.cos(math.radians(225)))  # axis dir from the Stone

def heights(pts):
    return json.loads(subprocess.check_output(['node', os.path.join(P.HERE, 'heights.js'), P.ROOT], input=json.dumps(pts).encode()))

def lateral(x, z):
    vx, vz = x - 0, z + 366
    return vx * AX[1] - vz * AX[0]  # signed side of the bearing-225 axis

def ok_a(x, z):
    b, r = P.bearing_r(x, z)
    if not (200 <= r <= 235): return None
    lat = lateral(x, z)
    if not (6 <= abs(lat) <= 32): return None
    if P.dist((x, z), P.DEN_OPEN) < 12: return None
    if any(P.dist((x, z), (s['x'], s['z'])) < 4 + s['radius'] for s in RL['stains']): return None
    if W.d_fire(x, z)[0] < 26 or W.d_loop(x, z)[0] < 20: return None
    if any(P.dist((x, z), g) < 12 for g in GUARDS): return None
    d = W.d_props(x, z)[0]
    return d if d >= 10 else None

grid = []
for b10 in range(2000, 2501, 5):
    for r in range(200, 236):
        x, z = P.polar(b10 / 10, r); d = ok_a(x, z)
        if d: grid.append((round(x, 1), round(z, 1), d, lateral(x, z)))
print('corridor grid points clear:', len(grid))
rng = random.Random(20261020)
best = None
for it in range(4000):
    pick = []
    pool = grid[:]
    rng.shuffle(pool)
    for p in pool:
        if all(P.dist(p[:2], q[:2]) >= 26 for q in pick): pick.append(p)
        if len(pick) == 5: break
    if len(pick) < 5: continue
    sides = [p[3] > 0 for p in pick]
    if all(sides) or not any(sides): continue
    sc = min(p[2] for p in pick)
    if best is None or sc > best[0]: best = (sc, pick)
sc, pick = best
# deadTrees = the two clearest picks on opposite sides; the rest small dressing
pick.sort(key=lambda p: -p[2])
L = [p for p in pick if p[3] > 0]; R = [p for p in pick if p[3] <= 0]
dead = [L[0], R[0]]; rest = [p for p in pick if p not in dead]
rest.sort(key=lambda p: P.dist(p[:2], P.DEN_OPEN))  # skull pile nearest the mouth
rows = []
for i, p in enumerate(dead):
    rows.append(dict(asset=DEAD, x=p[0], z=p[1], rotY=round(1.1 + 2.3 * i, 2), scale=round(8.6 + 0.6 * i, 2), cullM=140,
                     _c='CC-C17 den-corridor dead tree (%s of the approach)' % ('N' if p[3] > 0 else 'S')))
rows.append(dict(asset='skullPile', x=rest[0][0], z=rest[0][1], rotY=2.40, scale=1.2, cullM=120, _c='CC-C17 den-corridor skull pile (nearest the mouth)'))
for i, p in enumerate(rest[1:]):
    rows.append(dict(asset='blightcap', x=p[0], z=p[1], rotY=round(0.5 + 1.7 * i, 2), scale=round(1.4 + 0.2 * i, 2), cullM=120, _c='CC-C17 den-corridor blightcap'))
print('corridor min prop dist %.1f' % sc)
for r in rows:
    b, rr = P.bearing_r(r['x'], r['z'])
    print('  %-9s (%.1f, %.1f) bear %.1f r %.1f prop %.1f %s den %.1f lat %.1f' % (r['asset'], r['x'], r['z'], b, rr, *W.d_props(r['x'], r['z']), P.dist((r['x'], r['z']), P.DEN_OPEN), lateral(r['x'], r['z'])))
mind = min(P.dist((a['x'], a['z']), (b['x'], b['z'])) for i, a in enumerate(rows) for b in rows[i + 1:])
print('  mutual spacing min %.1f' % mind)

# (b) ring fragment - LEDGER IN THE LOOP: slots sorted by distance to the nominal
# (bearing 200 r 238); the first slot that passes every gate AND keeps the real
# ledger2 probe (ledger2_probe.js, both centres, these rows as extras) <= LEDGER_CAP
# wins. The nominal slot itself = 2,018,688 (100.9%): the west plateau is full.
LEDGER_CAP = 1970000  # 10 k under the 1,980,000 gate (scatter re-plan margin)
def frag(cx, cz):
    a0 = math.atan2(cx - 0, cz + 366)  # outward direction (toward the ridge)
    out = []
    for k, (da, sc, rot) in enumerate(((-0.75, 2.8, 0.9), (0.0, 2.2, 3.1), (0.75, 2.5, 5.0))):
        a = a0 + math.pi + da  # arc bowed toward the map (the ridge swallows its far side)
        out.append((round(cx + 8 * math.sin(a), 1), round(cz + 8 * math.cos(a), 1), sc, rot))
    return out
def frag_rows(fr):
    return [dict(asset='mossBoulder', x=x, z=z, rotY=rot, scale=sc, y=round(-0.3 * 1.402 * sc, 2), cullM=120,
                 _c='CC-C17 ring fragment (half-swallowed, sink 0.3 x height)') for x, z, sc, rot in fr]
def ledger(extra):
    tmp = os.path.join(P.HERE, '_ledger_extra.json')
    json.dump([{k: v for k, v in r.items() if k != '_c'} for r in extra], open(tmp, 'w'))
    res = [json.loads(subprocess.check_output(['node', os.path.join(P.HERE, 'ledger2_probe.js'), P.ROOT, c[0], c[1], '170', tmp]))['worst']
           for c in (('0', '-366'), ('-175', '-266'))]
    os.remove(tmp); return res
nom = P.polar(200, 238)
cands = []
for db in range(-80, 81, 5):
    for r in range(226, 262, 2):
        cx, cz = P.polar(200 + db / 10, r)
        dc = W.d_props(cx, cz)[0]
        if dc < 26 or min(W.zones(cx, cz).values()) < 48 or W.d_road(cx, cz)[0] < 35 or W.d_fire(cx, cz)[0] < 45: continue
        fr = frag(cx, cz)
        if any(W.d_props(x, z)[0] < 10 or W.d_loop(x, z)[0] < 20 for x, z, _, _ in fr): continue
        if any(P.dist((x, z), (rw['x'], rw['z'])) < 10 for x, z, _, _ in fr for rw in rows): continue
        cands.append((P.dist((cx, cz), nom), round(cx, 1), round(cz, 1), dc, fr))
cands.sort()
print('nominal-slot ledger (corridor + fragment at the nearest gate-clear slot):', ledger(rows + frag_rows(cands[0][4])))
chosen = None
for d, cx, cz, dc, fr in cands:
    sl = []
    for x, z, sc, _ in fr:
        rr = 1.897 * sc / 2
        h = heights([[x, z]] + [[x + rr * math.cos(q * math.pi / 4), z + rr * math.sin(q * math.pi / 4)] for q in range(8)])
        sl.append(max(math.degrees(math.atan(abs(h[q] - h[0]) / rr)) for q in range(1, 9)))
    if max(sl) > 31:
        print("  slot (%.1f, %.1f) slope %.1f > 31: skip" % (cx, cz, max(sl))); continue
    lw = ledger(rows + frag_rows(fr))
    print("  slot (%.1f, %.1f) bear %.1f r %.1f ledger %s" % (cx, cz, *P.bearing_r(cx, cz), lw))
    if max(lw) <= LEDGER_CAP: chosen = (d, cx, cz, dc, fr, sl, lw); break
d, cx, cz, dc, fr, sl, lw = chosen
b, rr = P.bearing_r(cx, cz)
print('fragment centre (%.1f, %.1f) bear %.1f r %.1f moved %.1f centre->props %.1f slopes %s ledger %s' % (cx, cz, b, rr, d, dc, [round(s, 1) for s in sl], lw))
for r in frag_rows(fr):
    rows.append(r)
    print('  boulder (%.1f, %.1f) s %.1f prop %.1f %s' % (r['x'], r['z'], r['scale'], *W.d_props(r['x'], r['z'])))
json.dump(rows, open(os.path.join(P.HERE, 'rows_spooky.json'), 'w'), indent=0)
