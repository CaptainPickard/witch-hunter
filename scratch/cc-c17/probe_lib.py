#!/usr/bin/env python3
"""CC-C17v2 probe lib (offline, no game run). Obstacles come from the live
CONFIG via scratch/cc-c17/dump_cfg.js (node): regionC props, C roads
(polylines + the Stone ring), C cook stations (fires), C wolf-pack loops
(waypoints AND loop segments), zones (spawn / Stone / den opening).
Gates (v2 brief): cluster-centre vs props >= 26, roads >= 35, fires >= 45,
loops >= 60, zones 48."""
import json, math, subprocess, os

ROOT = '/tmp/wh-worldfeat'
HERE = os.path.join(ROOT, 'scratch/cc-c17')
SPAWN = (0.0, -96.0); STONE = (0.0, -366.0); DEN_OPEN = (-163.4, -202.6)

def load_cfg():
    out = subprocess.check_output(['node', os.path.join(HERE, 'dump_cfg.js'), ROOT])
    return json.loads(out)

def dist(a, b): return math.hypot(a[0] - b[0], a[1] - b[1])

def seg_d(p, a, b):
    ex, ez = b[0] - a[0], b[1] - a[1]
    L = ex * ex + ez * ez
    t = 0 if L == 0 else max(0, min(1, ((p[0] - a[0]) * ex + (p[1] - a[1]) * ez) / L))
    return math.hypot(p[0] - (a[0] + ex * t), p[1] - (a[1] + ez * t))

def polar(bear_deg, r):
    """bearing from the Stone (0 = -z north, 90 = +x east; the C16 probes' convention)"""
    a = math.radians(bear_deg)
    return (r * math.sin(a), -366.0 - r * math.cos(a))

def bearing_r(x, z):
    return (math.degrees(math.atan2(x, -(z + 366.0))) % 360, math.hypot(x, z + 366.0))

class World:
    def __init__(self, cfg=None):
        self.cfg = cfg or load_cfg()
        self.props = [(p['asset'], p['x'], p['z']) for p in self.cfg['props']]
        self.fires = [(s['id'], s['x'], s['z']) for s in self.cfg['stations']]
        self.loops = [(p['id'], [tuple(w) for w in p['waypoints']]) for p in self.cfg['packs']]
        self.roads = []
        for r in self.cfg['roads']:
            if 'ring' in r: self.roads.append((r['id'], 'ring', r['ring']))
            else: self.roads.append((r['id'], 'line', [tuple(q) for q in r['points']]))

    def d_road(self, x, z):
        best, who = 1e9, None
        for rid, kind, g in self.roads:
            if kind == 'ring': d = abs(math.hypot(x - g['x'], z - g['z']) - g['r'])
            else: d = min(seg_d((x, z), g[i], g[i + 1]) for i in range(len(g) - 1))
            if d < best: best, who = d, rid
        return best, who

    def d_props(self, x, z, skip=None):
        best, who = 1e9, None
        for i, (a, px, pz) in enumerate(self.props):
            if skip and i in skip: continue
            d = math.hypot(px - x, pz - z)
            if d < best: best, who = d, (a, px, pz)
        return best, who

    def d_fire(self, x, z):
        return min(((math.hypot(fx - x, fz - z), fid) for fid, fx, fz in self.fires))

    def d_loop(self, x, z):
        best = (1e9, None)
        for pid, pts in self.loops:
            n = len(pts)
            for i in range(n):
                d = seg_d((x, z), pts[i], pts[(i + 1) % n])
                if d < best[0]: best = (d, pid)
        return best

    def zones(self, x, z):
        return {'spawn': dist((x, z), SPAWN), 'stone': dist((x, z), STONE), 'den': dist((x, z), DEN_OPEN)}

def fmt(d): return round(d, 1)
