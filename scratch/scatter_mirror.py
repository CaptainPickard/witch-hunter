#!/usr/bin/env python3
"""Round E: line-by-line Python mirror of region-manager.js whScatterPlan.

No JS engine on this box (no node), so the per-region counts in the Round E
report come from this mirror. It reads CONFIG.js through esprima (literal
values only), emulates mulberry32 / FNV-1a with JS int32 semantics, and
measures asset footprints the way three's Box3.setFromObject does (geometry
bbox corners through the node world matrix, X extent = width, Y = height).
The game logs the authoritative counts once per region: '[WH scatter] <id> {...}'.
Math.sin/cos may differ from V8 by an ulp, which could flip a knife-edge
rejection; counts are expected to match exactly in practice.

  scatter_mirror.py <repo-root> [--json out.json]
"""
import json, math, re, sys
from pathlib import Path
import numpy as np
import esprima
import trimesh

ROOT = Path(sys.argv[1]).resolve()
JS = ROOT / 'prototype' / 'js'


# ---- JS int32 helpers ---------------------------------------------------------
def u32(x): return x & 0xFFFFFFFF
def i32(x):
    x = u32(x)
    return x - 0x100000000 if x >= 0x80000000 else x
def imul(a, b): return i32(u32(a) * u32(b))
def ushr(x, n): return u32(x) >> n
def xor(a, b): return i32(u32(a) ^ u32(b))


def wh_rng(seed):
    st = [i32(seed)]
    def f():
        s = i32(st[0])
        s = i32(s + 0x6D2B79F5)
        st[0] = s
        t = imul(xor(s, ushr(s, 15)), i32(1 | u32(s)))
        t = xor(t + imul(xor(t, ushr(t, 7)), i32(61 | u32(t))), t)
        return ushr(xor(t, ushr(t, 14)), 0) / 4294967296
    return f


def wh_hash(s):
    h = 2166136261
    for ch in s:
        h = xor(h, ord(ch))
        h = imul(h, 16777619)
    return u32(h)


# ---- CONFIG / MANIFEST literal extraction ------------------------------------
def lit(n):
    t = n.type
    if t == 'Literal':
        return n.value
    if t == 'UnaryExpression' and n.operator == '-':
        v = lit(n.argument)
        return -v if isinstance(v, (int, float)) else None
    if t == 'ObjectExpression':
        out = {}
        for p in n.properties:
            k = p.key.name if p.key.type == 'Identifier' else p.key.value
            out[k] = lit(p.value)
        return out
    if t == 'ArrayExpression':
        return [lit(e) for e in n.elements]
    return None


def find_obj(node, pred):
    stack = [node]
    while stack:
        n = stack.pop()
        if pred(n):
            return n
        for k, v in vars(n).items() if hasattr(n, '__dict__') else []:
            if isinstance(v, list):
                stack.extend(x for x in v if hasattr(x, 'type'))
            elif hasattr(v, 'type'):
                stack.append(v)
    return None


cfg_ast = esprima.parseScript((JS / 'CONFIG.js').read_text())
cfg_node = find_obj(cfg_ast, lambda n: n.type == 'AssignmentExpression' and
                    getattr(n.left, 'property', None) is not None and
                    getattr(n.left.property, 'name', '') == 'WH_CONFIG')
CFG = lit(cfg_node.right)
as_ast = esprima.parseScript((JS / 'assets.js').read_text())
man_node = find_obj(as_ast, lambda n: n.type == 'VariableDeclarator' and n.id.name == 'MANIFEST')
MANIFEST = lit(man_node.init)

# ---- footprints like Box3.setFromObject (non-precise) ------------------------
_meta = {}
def meta(name):
    if name in _meta:
        return _meta[name]
    rel = MANIFEST.get(name)
    if rel is None:
        _meta[name] = None
        return None
    sc = trimesh.load(str(ROOT / rel), force='scene')
    lo = np.full(3, np.inf); hi = np.full(3, -np.inf)
    for node in sc.graph.nodes_geometry:
        T, gname = sc.graph[node]
        g = sc.geometry[gname]
        b = np.asarray(g.vertices, dtype=np.float32).astype(float)
        bmin, bmax = b.min(0), b.max(0)
        corners = np.array([[x, y, z] for x in (bmin[0], bmax[0]) for y in (bmin[1], bmax[1])
                            for z in (bmin[2], bmax[2])])
        w = (np.c_[corners, np.ones(8)] @ np.asarray(T).T)[:, :3]
        lo = np.minimum(lo, w.min(0)); hi = np.maximum(hi, w.max(0))
    _meta[name] = {'width': float(hi[0] - lo[0]), 'height': float(hi[1] - lo[1])}
    return _meta[name]


# ---- mirror of region-manager.js ---------------------------------------------
TRUNK_RATIO = 0.25
TRUNK_ASSETS = {'livingOak', 'witchwoodTree', 'birchTree', 'deadTree', 'deadTree2', 'ancientOak',
                'hangingTree', 'twistedSapling', 'thornbush', 'bramble', 'largeFern', 'deadShrub',
                'mossyStump', 'hollowStump'}
TRUNK_RE = re.compile(r'tree|oak|birch|sapling|bush|bramble|fern|shrub|stump', re.I)


def collider_radius(name, width, scale):
    r = width * scale / 2
    if name in TRUNK_ASSETS or TRUNK_RE.search(name):
        return r * TRUNK_RATIO
    return r


def play_radius():
    return CFG['world']['groundRadius'] - CFG['world']['playerMargin']


def meets_corridor(x, z, r):
    hw = CFG['chokepoint']['width'] / 2
    hd = CFG['world']['colliderCorridorHalfDepth']
    cx = CFG['chokepoint']['centerX']; bz = CFG['boundary']['z']
    nx = max(cx - hw, min(cx + hw, x)); nz = max(bz - hd, min(bz + hd, z))
    dx = x - nx; dz = z - nz
    return dx * dx + dz * dz <= r * r


def path_cx(DP, z):
    return DP['swayAmp'] * math.sin(2 * math.pi * (z - DP['zFrom']) / DP['swayPeriod'])


def dist_to_path(DP, x, z):
    span = DP['zFrom'] - DP['zTo']
    n = math.ceil(span)
    best = math.inf
    ax = path_cx(DP, DP['zFrom']); az = DP['zFrom']
    for i in range(1, n + 1):
        bz = DP['zFrom'] - min(span, i)
        bx = path_cx(DP, bz)
        ex = bx - ax; ez = bz - az
        l2 = ex * ex + ez * ez
        t = ((x - ax) * ex + (z - az) * ez) / l2 if l2 > 0 else 0
        t = max(0, min(1, t))
        dx = x - (ax + ex * t); dz = z - (az + ez * t)
        d = math.sqrt(dx * dx + dz * dz)
        if d < best:
            best = d
        ax, az = bx, bz
    return best


def pick_weighted(rand, rows):
    total = sum(r[1] for r in rows)
    u = rand() * total
    for r in rows:
        u -= r[1]
        if u < 0:
            return r
    return rows[-1]


def scatter_plan(region_key):
    SC = CFG['scatter']
    reg = CFG[region_key]
    rid = reg['id']
    side = 1 if region_key == 'regionA' else -1
    plan = {'trees': [], 'instances': {}, 'rings': [],
            'stats': dict(trees=0, treeMisses=0, ringBushes=0, ringSkipped=0, freeBushes=0, grass=0)}
    C = SC['clear']; plane = CFG['boundary']['z']; rPlay = play_radius()
    DP = CFG['world'].get('dirtPath'); has_path = bool(DP and DP['regionId'] == rid)
    gx = CFG['chokepoint']['centerX']; TWO_PI = math.pi * 2
    lerp = lambda rg, u: rg[0] + (rg[1] - rg[0]) * u
    stream = lambda layer: wh_rng(i32(SC['seed'] ^ wh_hash(rid + ':' + layer)))
    hosts = set(SC['bushes']['ringHosts'])
    circles, trees = [], []
    for p in reg['props']:
        pm = meta(p['asset'])
        c = {'x': p['x'], 'z': p['z'], 'r': collider_radius(p['asset'], pm['width'], p['scale']) if pm else 0,
             'trunk': pm['width'] * p['scale'] / 2 * TRUNK_RATIO if (pm and p['asset'] in hosts) else 0,
             'asset': p['asset'], 'scale': p['scale'], 'rotY': p['rotY'], 'y': p.get('y', 0) or 0}
        circles.append(c)
        if c['trunk'] > 0:
            trees.append(c)
    enemies = reg.get('enemies') or []; nodes = reg.get('nodes') or []
    points = enemies + nodes; ne = len(enemies)

    def in_region(x, z, pad):
        if math.sqrt(x * x + z * z) > rPlay - pad:
            return False
        return z > plane + pad if side == 1 else z < plane - pad

    def clear_world(x, z, pathM):
        dx = x - reg['spawn']['x']; dz = z - reg['spawn']['z']
        if dx * dx + dz * dz < C['spawnM'] ** 2: return False
        dx = x - gx; dz = z - plane
        if dx * dx + dz * dz < C['gateM'] ** 2: return False
        if meets_corridor(x, z, 0): return False
        if has_path and dist_to_path(DP, x, z) < pathM: return False
        return True

    keep = [k for k in (SC.get('keepOut') or []) if k['regionId'] == rid]

    def clear_points(x, z):
        for k in keep:
            if ((x - k['x']) / k['rx']) ** 2 + ((z - k['z']) / k['rz']) ** 2 < 1: return False
        for i, pt in enumerate(points):
            lim = C['enemyM'] if i < ne else C['nodeM']
            dx = x - pt['x']; dz = z - pt['z']
            if dx * dx + dz * dz < lim * lim: return False
        return True

    def hits(x, z, pad, skip):
        for c in circles:
            if c is skip: continue
            lim = c['r'] + pad
            dx = x - c['x']; dz = z - c['z']
            if dx * dx + dz * dz < lim * lim: return True
        return False

    def sample(rand):
        rr = rPlay * math.sqrt(rand()); th = TWO_PI * rand()
        return rr * math.cos(th), rr * math.sin(th)

    def add(name, x, z, rot, sc):
        plan['instances'].setdefault(name, []).append({'x': x, 'z': z, 'rotY': rot, 'scale': sc})

    T = SC['treesExtra']; rt = stream('trees')
    for _ in range(T['targetCount'].get(rid, 0)):
        best = None; best_gap = -1
        for _k in range(T['candidates']):
            x, z = sample(rt)
            if (not in_region(x, z, C['edgeM']) or not clear_world(x, z, C['pathM']) or
                    not clear_points(x, z) or hits(x, z, T['propClearM'], None)):
                continue
            tg = math.inf
            for q in trees:
                tg = min(tg, math.sqrt((x - q['x']) ** 2 + (z - q['z']) ** 2))
            if tg < T['minSpacingM']: continue
            gap = min(tg, rPlay - math.sqrt(x * x + z * z), abs(z - plane))
            if gap > best_gap: best = (x, z); best_gap = gap
        pick = pick_weighted(rt, T['assets']); rot = rt() * TWO_PI; h = lerp([pick[2], pick[3]], rt())
        if best is None:
            plan['stats']['treeMisses'] += 1; continue
        tm = meta(pick[0]); sc = h / tm['height']
        row = {'asset': pick[0], 'x': best[0], 'z': best[1], 'rotY': rot, 'scale': sc,
               'r': collider_radius(pick[0], tm['width'], sc)}
        plan['trees'].append(row)
        tc = {'x': row['x'], 'z': row['z'], 'r': row['r'], 'trunk': tm['width'] * sc / 2 * TRUNK_RATIO,
              'asset': pick[0], 'scale': sc, 'rotY': rot, 'y': 0, 'scatter': True}
        circles.append(tc); trees.append(tc)
    plan['stats']['trees'] = len(plan['trees'])

    B = SC['bushes']; G = SC['grass']
    grass_path = DP['halfWidth'] + G['pathPadM'] if has_path else 0

    def bush_pick(rand):
        bp = pick_weighted(rand, B['assets']); h = lerp([bp[2], bp[3]], rand())
        bm = meta(bp[0]); sc = h / bm['height']
        return bp[0], sc, bm['width'] * sc / 2 * B['selfRadiusFrac'], rand() * TWO_PI

    R = B['atTreeRing']; rr2 = stream('rings')
    for host in trees:
        n = R['count'][0] + math.floor(rr2() * (R['count'][1] - R['count'][0] + 1))
        a0 = rr2() * TWO_PI
        for slot in range(n):
            ang = a0 + slot * TWO_PI / n + (rr2() - 0.5) * (TWO_PI / n) * 0.5
            rad = host['trunk'] * lerp(R['radiusFrac'], rr2())
            name, sc, own, rot = bush_pick(rr2)
            bx = host['x'] + math.cos(ang) * rad; bz = host['z'] + math.sin(ang) * rad
            if not in_region(bx, bz, 0) or not clear_world(bx, bz, grass_path) or hits(bx, bz, own, host):
                plan['stats']['ringSkipped'] += 1; continue
            add(name, bx, bz, rot, sc); plan['stats']['ringBushes'] += 1
            plan['rings'].append({'host': [host['x'], host['z']], 'bush': [bx, bz]})

    rf = stream('freeBushes'); fa = 0
    while fa < B['freeBushes'] * 30 and plan['stats']['freeBushes'] < B['freeBushes']:
        x, z = sample(rf); name, sc, own, rot = bush_pick(rf); fa += 1
        if (not in_region(x, z, C['edgeM']) or not clear_world(x, z, C['pathM']) or
                not clear_points(x, z) or hits(x, z, T['propClearM'], None)):
            continue
        add(name, x, z, rot, sc); plan['stats']['freeBushes'] += 1

    gm = meta(G['asset']); rg = stream('grass'); ga = 0
    while ga < G['count'] * 10 and plan['stats']['grass'] < G['count']:
        x, z = sample(rg); h = lerp(G['height'], rg()); rot = rg() * TWO_PI; ga += 1
        sc = h / gm['height']; own = gm['width'] * sc / 2
        if not in_region(x, z, 0) or not clear_world(x, z, grass_path) or hits(x, z, own, None):
            continue
        add(G['asset'], x, z, rot, sc); plan['stats']['grass'] += 1
    plan['stats']['grassAttempts'] = ga; plan['stats']['freeAttempts'] = fa
    plan['configTrees'] = [c for c in trees if not c.get('scatter')]
    plan['props'] = circles
    return plan


if __name__ == '__main__':
    out = {}
    for key in ('regionA', 'regionB'):
        p = scatter_plan(key)
        rid = CFG[key]['id']
        inst = {k: len(v) for k, v in p['instances'].items()}
        print(rid, json.dumps(p['stats']), 'InstancedMesh:', inst,
              'trees:', [(t['asset'], round(t['x'], 1), round(t['z'], 1)) for t in p['trees']])
        out[rid] = p
    if '--json' in sys.argv:
        Path(sys.argv[sys.argv.index('--json') + 1]).write_text(json.dumps(out))
