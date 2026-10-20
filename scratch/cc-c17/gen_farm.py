#!/usr/bin/env python3
"""CC-C17v2 step 2 FARM site scan + layout (deterministic grid scan, no RNG;
seed label: GRID bear 60..180 step 2 x r 150..200 step 2, tie-break = scan order).
Layout (local frame: cottage at origin, door +Z = toward the nearest road point,
the C3.1c tent door convention; three.js rotY maps local +Z -> (sin, cos)):
  cottage (0,0) | well (-4.5, 8) | yard front line z=13: gate centred (x 0),
  2 rail sections each side (x +-3.0, +-6.5) | corner-v2 brackets (+-8.7, 13) |
  each side line (x +-8.7): stonewall (z 9.9, len 4.75) + rail section (z 5.6)
  -> 6 rail sections + 2 stonewall + gate + 2 corners | lanternPost outside the
  gate (2.2, 14.6) = the amber beacon.
Scales (RUN_TASK scale law; fence pieces by MEASURED height - see REPORT):
  cottage 3.68 (7.0 m) | well 1.26 (2.4 m) | okFencePost 1.85 (rail section,
  1.2 m tall / 3.5 m long: the GLB's 1.9 units are its LENGTH, height 0.65) |
  okFenceStonewall 2.5 (= len 4.75 / 1.9) | gate 1.32 | corner-v2 1.5 (brief)."""
import json, math, sys, subprocess, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe_lib as P

FP_S, SW_S = 1.85, 2.5
FP_LEN, SW_LEN = 1.9 * FP_S, 1.9 * SW_S
LOCAL = [  # (asset, lx, lz, rot offset, scale, extra)
    ('okFarmCottage', 0.0, 0.0, 0.0, 3.68, {}),
    ('okFarmWell', -4.5, 8.0, 0.6, 1.26, {}),
    ('okFenceGate', 0.0, 13.0, 0.0, 1.32, {'wall': 2}),
    ('okFencePost', 3.0, 13.0, 0.0, FP_S, {'wall': 3}),
    ('okFencePost', 6.5, 13.0, 0.0, FP_S, {'wall': 3}),
    ('okFencePost', -3.0, 13.0, 0.0, FP_S, {'wall': 3}),
    ('okFencePost', -6.5, 13.0, 0.0, FP_S, {'wall': 3}),
    ('okFenceCornerV2', 8.7, 13.0, 0.0, 1.5, {}),
    ('okFenceCornerV2', -8.7, 13.0, math.pi, 1.5, {}),
    ('okFenceStonewall', 8.7, 9.9, math.pi / 2, SW_S, {'wall': 4}),
    ('okFenceStonewall', -8.7, 9.9, math.pi / 2, SW_S, {'wall': 4}),
    ('okFencePost', 8.7, 5.6, math.pi / 2, FP_S, {'wall': 3}),
    ('okFencePost', -8.7, 5.6, math.pi / 2, FP_S, {'wall': 3}),
    ('lanternPost', 2.2, 14.6, 0.0, 2.535, {}),
]
YARD_C = (0.0, 7.0)  # local yard centroid (cluster centre)

def to_world(cx, cz, th, lx, lz):
    return (cx + lx * math.cos(th) + lz * math.sin(th), cz - lx * math.sin(th) + lz * math.cos(th))

def layout(cx, cz, th):
    rows = []
    for a, lx, lz, ro, s, ex in LOCAL:
        x, z = to_world(cx, cz, th, lx, lz)
        r = dict(asset=a, x=round(x, 1), z=round(z, 1), rotY=round((th + ro) % (2 * math.pi), 2), scale=s, cullM=120)
        r.update(ex); rows.append(r)
    return rows

def road_face(W, x, z):
    # direction to the nearest road point (sampled)
    best = (1e9, 0, 0)
    for rid, kind, g in W.roads:
        if kind == 'ring':
            a = math.atan2(x - g['x'], z - g['z']); q = (g['x'] + g['r'] * math.sin(a), g['z'] + g['r'] * math.cos(a))
            cand = [q]
        else:
            cand = []
            for i in range(len(g) - 1):
                for k in range(21):
                    t = k / 20; cand.append((g[i][0] + (g[i + 1][0] - g[i][0]) * t, g[i][1] + (g[i + 1][1] - g[i][1]) * t))
        for q in cand:
            d = math.hypot(q[0] - x, q[1] - z)
            if d < best[0]: best = (d, q[0], q[1])
    return math.atan2(best[1] - x, best[2] - z)

def check(W, rows, centre, verbose=False):
    v = []; m = {}
    cx, cz = centre
    b, r = P.bearing_r(cx, cz)
    m['bearing'], m['r'] = round(b, 1), round(r, 1)
    if not (150 <= r <= 200): v.append(('r-band', round(r, 1)))
    if abs(((b - 225 + 180) % 360) - 180) < 15: v.append(('den-bearing', b))
    dp, who = W.d_props(cx, cz); m['centre_prop'] = (P.fmt(dp), who)
    if dp < 26: v.append(('centre-prop', P.fmt(dp), who))
    dr, rid = W.d_road(cx, cz); m['centre_road'] = (P.fmt(dr), rid)
    if dr < 35: v.append(('centre-road', P.fmt(dr), rid))
    df, fid = W.d_fire(cx, cz); m['centre_fire'] = (P.fmt(df), fid)
    if df < 45: v.append(('centre-fire', P.fmt(df), fid))
    dl, pid = W.d_loop(cx, cz); m['centre_loop'] = (P.fmt(dl), pid)
    if dl < 60: v.append(('centre-loop', P.fmt(dl), pid))
    for k, d in P.zones(cx, cz).items() if hasattr(P, 'zones') else W.zones(cx, cz).items():
        if d < 48: v.append(('zone-' + k, P.fmt(d)))
    # per-row envelope sanity: every row >= 8 m from every non-farm prop, >= 20 m off roads, loops >= 45
    mins = [1e9, 1e9, 1e9]
    for rw in rows:
        d, w = W.d_props(rw['x'], rw['z'])
        if d < 8: v.append(('row-prop', rw['asset'], P.fmt(d), w))
        dr2, _ = W.d_road(rw['x'], rw['z'])
        if dr2 < 20: v.append(('row-road', rw['asset'], P.fmt(dr2)))
        dl2, _ = W.d_loop(rw['x'], rw['z'])
        if dl2 < 45: v.append(('row-loop', rw['asset'], P.fmt(dl2)))
        mins = [min(mins[0], d), min(mins[1], dr2), min(mins[2], dl2)]
    m['row_min_prop_road_loop'] = [P.fmt(q) for q in mins]
    return v, m

def heights(pts):
    out = subprocess.check_output(['node', os.path.join(P.HERE, 'heights.js'), P.ROOT], input=json.dumps(pts).encode())
    return json.loads(out)

if __name__ == '__main__':
    W = P.World()
    cands = []
    for bear in range(60, 182, 2):
        for r in range(150, 202, 2):
            x, z = P.polar(bear, r)
            th = road_face(W, x, z)
            yc = to_world(x, z, th, *YARD_C)
            rows = layout(x, z, th)
            v, m = check(W, rows, yc)
            if v: continue
            score = min(m['centre_prop'][0] / 26, m['centre_road'][0] / 35, m['centre_fire'][0] / 45, m['centre_loop'][0] / 60,
                        m['row_min_prop_road_loop'][0] / 8)
            cands.append((score, bear, r, x, z, th, yc, m))
    cands.sort(key=lambda c: -c[0])
    print('clear candidates:', len(cands))
    # flatness for the top 25
    top = []
    for c in cands[:40]:
        _, bear, r, x, z, th, yc, m = c
        ring = [to_world(x, z, th, lx, lz) for lx in (-10, -5, 0, 5, 10) for lz in (-4, 0, 4, 8, 12, 15)]
        h = heights(ring)
        top.append((round(c[0], 3), bear, r, round(max(h) - min(h), 2), round(max(h), 2), m))
    for t in top: print(t)
