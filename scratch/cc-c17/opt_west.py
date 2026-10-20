#!/usr/bin/env python3
"""CC-C17v2 west-sector budget optimiser (offline). Base field = ledger2 field of
CONFIG WITHOUT the step-4 tree block (farm + ruin pasted). Items: oak@210-ish,
oak@240-ish, 5 corridor rows, 3-boulder fragment (centre; arc as gen_spooky).
Coordinate descent over each item's gate-valid candidate slots (same gates as
gen_trees.py / gen_spooky.py), objective = the field's worst point. Deterministic
(fixed scan order, start = the gen_* picks). usage: opt_west.py <deadAsset>"""
import sys, os, json, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe_lib as P, field_lib as FL
DEAD = sys.argv[1] if len(sys.argv) > 1 else 'deadTree'
T = dict(FL.T, okTreeOak=28721, youngDeadTree=3630)
F = FL.Field(os.path.join(P.HERE, 'field_noTrees.json'))
W = P.World()  # live CONFIG (contains the tree block: exclude those rows from gates)
tree_idx = {i for i, (a, x, z) in enumerate(W.props) if a in ('okTreeOak', 'okTreePine')}
RL = W.cfg['rotLair']
GUARDS = [(e['x'], e['z']) for e in W.cfg['enemies'] if e['type'] == 'bandit' and P.dist((e['x'], e['z']), (-207.8, -246)) < 15]
AX = (math.sin(math.radians(225)), -math.cos(math.radians(225)))
def lateral(x, z): return x * AX[1] - (z + 366) * AX[0]
def dprop(x, z): return W.d_props(x, z, skip=tree_idx)[0]
def oak_ok(x, z, sc):
    tr = 1.85 * sc / 2 * 0.25
    return dprop(x, z) >= 26 and W.d_fire(x, z)[0] >= 26 and W.d_road(x, z)[0] >= 8 + tr and P.dist((x, z), P.DEN_OPEN) >= 26 and W.d_loop(x, z)[0] >= 6
oakA = [c for c in (tuple(round(v, 1) for v in P.polar(b, r)) for b in range(198, 223) for r in range(218, 247)) if oak_ok(*c, 13.0)]
oakB = [c for c in (tuple(round(v, 1) for v in P.polar(b, r)) for b in range(228, 253) for r in range(218, 247)) if oak_ok(*c, 12.5)]
def cor_ok(x, z):
    b, r = P.bearing_r(x, z)
    if not (200 <= r <= 235): return False
    if not (6 <= abs(lateral(x, z)) <= 32): return False
    if P.dist((x, z), P.DEN_OPEN) < 12: return False
    if any(P.dist((x, z), (s['x'], s['z'])) < 4 + s['radius'] for s in RL['stains']): return False
    if W.d_fire(x, z)[0] < 26 or W.d_loop(x, z)[0] < 20: return False
    if any(P.dist((x, z), g) < 12 for g in GUARDS): return False
    return dprop(x, z) >= 10
COR = [c for c in (tuple(round(v, 1) for v in P.polar(b10 / 10, r)) for b10 in range(2000, 2501, 10) for r in range(200, 236, 2)) if cor_ok(*c)]
def frag(cx, cz):
    a0 = math.atan2(cx, cz + 366); out = []
    for da, sc, rot in ((-0.75, 2.8, 0.9), (0.0, 2.2, 3.1), (0.75, 2.5, 5.0)):
        a = a0 + math.pi + da; out.append((round(cx + 8 * math.sin(a), 1), round(cz + 8 * math.cos(a), 1), sc, rot))
    return out
FRAG = []
for db in range(-80, 81, 4):
    for r in range(226, 252, 2):
        cx, cz = P.polar(200 + db / 10, r)
        if dprop(cx, cz) < 26 or min(W.zones(cx, cz).values()) < 48 or W.d_road(cx, cz)[0] < 35 or W.d_fire(cx, cz)[0] < 45: continue
        if any(dprop(x, z) < 10 or W.d_loop(x, z)[0] < 20 for x, z, _, _ in frag(cx, cz)): continue
        FRAG.append((round(cx, 1), round(cz, 1)))
print('candidates oakA %d oakB %d corridor %d frag %d' % (len(oakA), len(oakB), len(COR), len(FRAG)))
# precompute per-candidate masks lazily
cache = {}
def mask(x, z, c):
    k = (x, z, c)
    if k not in cache: cache[k] = (F.x - x) ** 2 + (F.z - z) ** 2 <= c * c
    return cache[k]
ASSET = ['okTreeOak', 'okTreeOak', DEAD, DEAD, 'skullPile', 'blightcap', 'blightcap', 'frag']
CULL = [140, 140, 120 if DEAD == 'youngDeadTree' else 140, 120 if DEAD == 'youngDeadTree' else 140, 120, 120, 120, 120]
def contrib(i, pos):
    if ASSET[i] == 'frag':
        t = np.zeros_like(F.t)
        for x, z, _, _ in frag(*pos): t += mask(x, z, 120) * 21599
        return t
    return mask(pos[0], pos[1], CULL[i]) * T[ASSET[i]]
def feasible(sel):
    cor = sel[2:7]
    for i in range(5):
        for j in range(i + 1, 5):
            if P.dist(cor[i], cor[j]) < 26: return False
    if not (lateral(*cor[0]) > 0) != (lateral(*cor[1]) > 0): return False
    pts = [sel[0], sel[1]] + cor + [(x, z) for x, z, _, _ in frag(*sel[7])]
    if P.dist(sel[0], sel[1]) < 26: return False
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if (i < 7 or j < 7) and not (i >= 7 and j >= 7) and P.dist(pts[i], pts[j]) < 10: return False
    return True
start = json.load(open(os.path.join(P.HERE, 'rows_trees.json')))[:2]
sp = json.load(open(os.path.join(P.HERE, 'rows_spooky.json')))
sel = [(start[0]['x'], start[0]['z']), (start[1]['x'], start[1]['z'])] + [(r['x'], r['z']) for r in sp[:5]]
fc = [r for r in sp if r['asset'] == 'mossBoulder']
sel.append(min(FRAG, key=lambda c: P.dist(c, P.polar(200, 243))))
cands = [oakA, oakB, COR, COR, COR, COR, COR, FRAG]
parts = [contrib(i, sel[i]) for i in range(8)]
def total(): return F.t + sum(parts)
best = total().max(); print('start worst', int(best), 'feasible', feasible(sel))
for rnd in range(4):
    improved = False
    for i in range(8):
        others = F.t + sum(parts[k] for k in range(8) if k != i)
        bi = None
        for c in cands[i]:
            s2 = sel[:]; s2[i] = c
            if not feasible(s2): continue
            w = (others + contrib(i, c)).max()
            if w < best - 1: best, bi = w, c
        if bi is not None:
            sel[i] = bi; parts[i] = contrib(i, bi); improved = True
    print('round', rnd, 'worst', int(best))
    if not improved: break
t = total(); k = int(t.argmax())
print('FINAL worst %d (%.2f%%) at (%.0f, %.0f) dead=%s' % (best, best / 2e4, F.x[k], F.z[k], DEAD))
json.dump({'dead': DEAD, 'sel': sel, 'worst': float(best)}, open(os.path.join(P.HERE, 'opt_west_%s.json' % DEAD), 'w'))
print(sel)
