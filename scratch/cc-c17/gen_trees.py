#!/usr/bin/env python3
"""CC-C17v2 step 4 TREES: 2 okTreeOak sentinels framing the den approach (nominal
bearing 210 / 240, r 232 from the Stone) + 1 okTreePine at the N road bend (nominal
(-15, -570)). The nominal slots fail the 26 m gate (210: boulder 17.8 m; 240: camp-3
fire 8.0 m; pine: scree boulder 22.7 m), so each takes the NEAREST clear slot
(deterministic scan, no RNG: oak bearing +-12 deg step 1 x r 218-246 step 1; pine
+-20 m grid step 1). Gates: props >= 26, fires >= 26 (tree vs a lit camp), road
centreline >= 8 + trunk r (CC-C4a rule), den opening >= 26 (doorway stays open),
loops >= 6 (trunk off the patrol line), seat slope <= 31 deg over the trunk (C4b
CLIFF rule: rows steeper than the sprint cap were commented out), zones 48 (spawn/
Stone). Oak scales 13 / 12.5 (brief 12-14), pine 12 (brief). Trunk r = width x
scale / 2 x 0.25 (oak 1.85, pine 0.82 GLB widths)."""
import math, json, sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe_lib as P
W = P.World()

def heights(pts):
    return json.loads(subprocess.check_output(['node', os.path.join(P.HERE, 'heights.js'), P.ROOT], input=json.dumps(pts).encode()))

def gates(x, z, trunk):
    dp = W.d_props(x, z)[0]; df = W.d_fire(x, z)[0]; dr = W.d_road(x, z)[0]; dl = W.d_loop(x, z)[0]
    dd = P.dist((x, z), P.DEN_OPEN); zs = W.zones(x, z)
    ok = dp >= 26 and df >= 26 and dr >= 8 + trunk and dd >= 26 and dl >= 6 and zs['spawn'] >= 48 and zs['stone'] >= 48
    return ok, dict(prop=round(dp, 1), fire=round(df, 1), road=round(dr, 1), loop=round(dl, 1), den=round(dd, 1))

def slope(x, z, rr):
    pts = [[x, z]] + [[x + rr * math.cos(a * math.pi / 4), z + rr * math.sin(a * math.pi / 4)] for a in range(8)]
    h = heights(pts)
    return max(math.degrees(math.atan(abs(h[k] - h[0]) / rr)) for k in range(1, 9)), h[0]

def nearest(cands, nominal, trunk):
    ok = [(P.dist(c, nominal), c) for c in cands if gates(c[0], c[1], trunk)[0]]
    ok.sort()
    for d, c in ok[:400]:
        s, h = slope(c[0], c[1], max(2.0, trunk))
        if s <= 31: return c, d, s, h
    return None

out = []
for b0, sc, taken in ((210, 13.0, None), (240, 12.5, None)):
    trunk = 1.85 * sc / 2 * 0.25
    nom = P.polar(b0, 232)
    cands = [tuple(round(v, 1) for v in P.polar(b0 + db, r)) for db in range(-12, 13) for r in range(218, 247)]
    cands = [c for c in cands if all(P.dist(c, (o['x'], o['z'])) >= 26 for o in out)]
    c, d, s, h = nearest(cands, nom, trunk)
    b, r = P.bearing_r(*c)
    print('oak', b0, '->', c, 'bearing %.1f r %.1f moved %.1f slope %.1f h %.2f' % (b, r, d, s, h), gates(c[0], c[1], trunk)[1])
    out.append(dict(asset='okTreeOak', x=c[0], z=c[1], rotY=round((b0 * 0.37) % 6.28, 2), scale=sc, cullM=140,
                    _c='CC-C17 den-approach sentinel oak (nominal bearing %d r 232; nearest clear slot)' % b0))
trunk = 0.82 * 12 / 2 * 0.25
cands = [(-15 + dx, -570 + dz) for dx in range(-20, 21) for dz in range(-20, 21)]
c, d, s, h = nearest(cands, (-15, -570), trunk)
print('pine ->', c, 'moved %.1f slope %.1f h %.2f' % (d, s, h), gates(c[0], c[1], trunk)[1])
out.append(dict(asset='okTreePine', x=float(c[0]), z=float(c[1]), rotY=1.20, scale=12.0, cullM=140,
                _c='CC-C17 N road bend pine (nominal -15, -570; nearest clear slot)'))
json.dump(out, open(os.path.join(P.HERE, 'rows_trees.json'), 'w'), indent=0)
