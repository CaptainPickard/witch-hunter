#!/usr/bin/env python3
"""Round F: line-by-line Python mirror of region-manager.js whWallPlan.

No JS engine on this box, so the Round F placement counts come from this
mirror (same pattern as scratch/scatter_mirror.py): CONFIG.js / assets.js are
read through esprima (literal values only), mulberry32 / FNV-1a run with JS
int32 semantics, footprints are measured like three's Box3.setFromObject
(geometry bbox corners through the node world matrix; X extent = width,
Y = height). The game logs the authoritative stats once: '[WH wall] {...}'.

  wall_mirror.py <repo-root> [--json out.json] [--positions]
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


# ---- mirror of whWallPlan ------------------------------------------------------
def wall_plan():
    W = CFG['boundaryWall']
    plan = {'segments': [], 'colliders': [], 'arch': None, 'lantern': None, 'sockets': [],
            'stats': dict(ring=0, chordE=0, chordW=0, nudged=0, drops=0, dropReasons=[],
                          overDropLimit=False, colliders=0)}
    TWO_PI = math.pi * 2; DEG = math.pi / 180
    stream = lambda layer: wh_rng(i32(xor(W['seed'], wh_hash('wall:' + layer))))
    props = []
    for key in ('regionA', 'regionB'):
        reg = CFG[key]
        for i, p in enumerate(reg['props']):
            pm = meta(p['asset'])
            r = collider_radius(p['asset'], pm['width'], p['scale']) if pm else 0
            if r > 0:
                props.append({'id': '%s#%d:%s' % (reg['id'], i, p['asset']), 'x': p['x'], 'z': p['z'], 'r': r})
    L = W['segmentLengthUnits']; CR = W['collider']['r']; CN = W['collider']['perSegment']
    EX = W['exclusion']

    def seg_circles(x, z, rot):
        ax, az = math.cos(rot), -math.sin(rot)
        return [{'x': x + ax * ((k + 0.5) / CN - 0.5) * L, 'z': z + az * ((k + 0.5) / CN - 0.5) * L}
                for k in range(CN)]

    def clash(cs):
        for c in cs:
            for p in props:
                lim = p['r'] + EX['clearM'] + CR
                dx = c['x'] - p['x']; dz = c['z'] - p['z']
                if dx * dx + dz * dz < lim * lim:
                    return p['id']
        return None

    scales = {}
    for a in W['assets']:
        am = meta(a)
        sx = L / am['width'] if am and am['width'] > 0 else 1
        scales[a] = {'sx': sx, 'sy': W['heightM'] / am['height'] if am and am['height'] > 0 else sx,
                     'sz': sx * W['depthScale']}

    def add(kind, i, asset, x, z, rot, cs):
        s = scales[asset]
        plan['segments'].append(dict(kind=kind, i=i, asset=asset, x=x, z=z, rotY=rot, **s))
        for k, c in enumerate(cs):
            plan['colliders'].append({'index': 'wall-%s%d.%d' % (kind, i, k), 'x': c['x'], 'z': c['z'], 'r': CR})

    def drop(kind, i, why):
        plan['stats']['drops'] += 1
        plan['stats']['dropReasons'].append('%s%d vs %s' % (kind, i, why))
        if plan['stats']['drops'] > EX['maxDrops']:
            plan['stats']['overDropLimit'] = True

    R = W['radius']
    N = math.ceil(TWO_PI * R / (L - W['overlapM']))
    rr = stream('ring')
    raw, rotj = [], []
    for i in range(N):
        raw.append(rr() * 2 - 1)
        rotj.append((rr() * 2 - 1) * W['jitter']['rotJitterDeg'] * DEG)
    plan['ringN'] = N
    for i in range(N):
        sm = (raw[(i + N - 1) % N] + 2 * raw[i] + raw[(i + 1) % N]) / 4
        r0 = max(W['minRadius'], R + W['jitter']['radial'] * sm)
        th = i * TWO_PI / N
        rot = -th - math.pi / 2 + rotj[i]
        asset = W['assets'][i % len(W['assets'])]
        placed, why = False, None
        nd = 0
        while nd <= EX['nudgeMaxM'] + 1e-9:
            rx = (r0 - nd) * math.cos(th); rz = (r0 - nd) * math.sin(th)
            cs = seg_circles(rx, rz, rot)
            hit = clash(cs)
            if not hit:
                add('ring', i, asset, rx, rz, rot, cs)
                if nd > 0:
                    plan['stats']['nudged'] += 1
                placed = True
                break
            if why is None:
                why = hit
            nd += EX['nudgeStepM']
        if placed:
            plan['stats']['ring'] += 1
        else:
            drop('ring', i, why)

    zc = W['chordZ']
    x_end = math.sqrt(max(0, R * R - zc * zc)) if W['chordToRim'] else W['chordFromX'] + L
    span = x_end - W['chordFromX']
    nc = max(1, math.ceil(span / (L - W['overlapM'])))
    step = span / nc
    rc = stream('chord')
    plan['chordN'], plan['chordStep'], plan['chordEndX'] = nc, step, x_end
    for sd in (1, -1):
        for c in range(nc):
            face = 0 if rc() < 0.5 else math.pi
            rj = (rc() * 2 - 1) * W['jitter']['rotJitterDeg'] * DEG
            cx = sd * (W['chordFromX'] + (c + 0.5) * step)
            crot = face + rj
            ccs = seg_circles(cx, zc, crot)
            chit = clash(ccs)
            kind = 'chordE' if sd == 1 else 'chordW'
            if chit:
                drop(kind, c, chit); continue
            add(kind, c, W['assets'][c % len(W['assets'])], cx, zc, crot, ccs)
            plan['stats'][kind] += 1

    A = W['arch']
    gm = meta(A['asset'])
    if gm and gm['width'] > 0:
        s = A['fitOpening'] / (A['openingFrac'] * gm['width'])
        sz = s * A['depthScale']
        ca, sa = math.cos(A['rotY']), math.sin(A['rotY'])
        to_world = lambda lx, lz: (A['x'] + lx * ca + lz * sa, A['z'] - lx * sa + lz * ca)
        opening = A['openingFrac'] * gm['width'] * s
        xi = opening / 2; xo = gm['width'] * s / 2
        hd = A['depthFrac'] * gm['width'] * sz / 2
        apex = A['apexFrac'] * gm['height'] * s
        plan['arch'] = dict(asset=A['asset'], x=A['x'], z=A['z'], rotY=A['rotY'],
                            offsetX=-A['openingCenterFrac'] * gm['width'] * s, scale=s, scaleZ=sz,
                            opening=opening, halfWidth=xo, halfDepth=hd, apexY=apex, height=gm['height'] * s)
        LG = A['legs']
        legs, plugs = [], []
        for sd in (1, -1):
            x0, x1, z0, z1 = xi + LG['r'], xo - LG['r'], -hd + LG['r'], hd - LG['r']
            nx = max(1, math.ceil((x1 - x0) / LG['spacingM']))
            nz = max(1, math.ceil((z1 - z0) / LG['spacingM']))
            pts = []
            pts += [(x0 + (x1 - x0) * a / nx, z1) for a in range(nx)]
            pts += [(x1, z1 - (z1 - z0) * a / nz) for a in range(nz)]
            pts += [(x1 - (x1 - x0) * a / nx, z0) for a in range(nx)]
            pts += [(x0, z0 + (z1 - z0) * a / nz) for a in range(nz)]
            for pt in pts:
                wx, wz = to_world(sd * pt[0], pt[1])
                legs.append({'x': wx, 'z': wz, 'r': LG['r']})
            if A['plugCorners']:
                for pz in (hd, -hd):
                    wx, wz = to_world(sd * (xi + A['plugR']), pz)
                    plugs.append({'x': wx, 'z': wz, 'r': A['plugR']})
        plan['colliders'] += legs + plugs
        plan['stats']['archLegs'] = len(legs); plan['stats']['archPlugs'] = len(plugs)
        plan['legs'], plan['plugs'] = legs, plugs
        LT = W['lantern']
        lm = meta(LT['asset'])
        if lm and lm['height'] > 0:
            lh = LT['heightM'] * LT['scale']
            ly = apex - LT['topBelowApexM'] - lh
            plan['lantern'] = dict(asset=LT['asset'], localY=ly, scale=lh / lm['height'], height=lh)
            SK = CFG['lightSockets'].get(A['asset'])
            if SK:
                sx_, sz_ = to_world(SK['offset'][0], SK['offset'][1])
                plan['sockets'].append(dict(id=A['asset'] + '@lantern', x=sx_, y=ly + lh * SK['heightFraction'],
                                            z=sz_, intensity=SK['intensity']))
    plan['stats']['colliders'] = len(plan['colliders'])
    return plan


def region_counts(plan):
    """whPropColliders join: wall circles on each region's side (pad 3 m)."""
    pad = 3; plane = CFG['boundary']['z']
    return {CFG['regionA']['id']: sum(1 for c in plan['colliders'] if (c['z'] - plane) > -pad),
            CFG['regionB']['id']: sum(1 for c in plan['colliders'] if -(c['z'] - plane) > -pad)}


def gap_report(plan):
    """Largest gap between consecutive ring collider circles (edge to edge) and
    the min radius of any ring segment / circle - wall continuity check."""
    ring = [s for s in plan['segments'] if s['kind'] == 'ring']
    rs = [math.hypot(s['x'], s['z']) for s in ring]
    cs = [c for c in plan['colliders'] if c.get('index', '').startswith('wall-ring')]
    ang = sorted(cs, key=lambda c: math.atan2(c['z'], c['x']))
    gaps = []
    for a, b in zip(ang, ang[1:] + ang[:1]):
        gaps.append(math.hypot(a['x'] - b['x'], a['z'] - b['z']) - a['r'] - b['r'])
    return {'ringRadiusMin': round(min(rs), 4), 'ringRadiusMax': round(max(rs), 4),
            'ringCircleEdgeGapMax': round(max(gaps), 4),
            'playerCanSlipThrough': max(gaps) > 2 * CFG['player']['radius']}


def clearance_report(plan):
    """Closest approach of any wall/arch circle to a CONFIG prop collider (edge to edge)."""
    best = (math.inf, None, None)
    for key in ('regionA', 'regionB'):
        for i, p in enumerate(CFG[key]['props']):
            pm = meta(p['asset'])
            r = collider_radius(p['asset'], pm['width'], p['scale']) if pm else 0
            if r <= 0:
                continue
            for c in plan['colliders']:
                d = math.hypot(c['x'] - p['x'], c['z'] - p['z']) - r - c['r']
                if d < best[0]:
                    best = (d, '%s#%d:%s' % (CFG[key]['id'], i, p['asset']), c.get('index', 'arch'))
    return {'minEdgeGapM': round(best[0], 4), 'prop': best[1], 'circle': best[2]}


if __name__ == '__main__':
    plan = wall_plan()
    W = CFG['boundaryWall']
    st = plan['stats']
    seg_by_asset = {}
    for s in plan['segments']:
        seg_by_asset[s['asset']] = seg_by_asset.get(s['asset'], 0) + 1
    A = plan['arch']; LN = plan['lantern']
    rep = {
        'ringN': plan['ringN'], 'ring': st['ring'],
        'ringChordLenM': round(2 * W['radius'] * math.sin(math.pi / plan['ringN']), 4),
        'chordPerSide': plan['chordN'], 'chordE': st['chordE'], 'chordW': st['chordW'],
        'chordStepM': round(plan['chordStep'], 4), 'chordEndX': round(plan['chordEndX'], 4),
        'nudged': st['nudged'], 'drops': st['drops'], 'dropReasons': st['dropReasons'],
        'overDropLimit': st['overDropLimit'],
        'instancesPerAsset': seg_by_asset,
        'segmentScale': None,   # filled below (first segment per asset)
        'colliders': st['colliders'], 'archLegs': st.get('archLegs'), 'archPlugs': st.get('archPlugs'),
        'collidersJoinedPerRegion': region_counts(plan),
        'arch': {k: (round(v, 4) if isinstance(v, float) else v) for k, v in A.items()} if A else None,
        'archOpeningM': round(A['opening'], 4) if A else None,
        'legPositionsE': [[round(c['x'], 3), round(c['z'], 3)] for c in plan['legs'] if c['x'] > 0],
        'legPositionsW': [[round(c['x'], 3), round(c['z'], 3)] for c in plan['legs'] if c['x'] < 0],
        'plugPositions': [[round(c['x'], 3), round(c['z'], 3), c['r']] for c in plan['plugs']],
        'passableLaneM': round(min(c['x'] - c['r'] for c in plan['legs'] + plan['plugs'] if c['x'] > 0) -
                               max(c['x'] + c['r'] for c in plan['legs'] + plan['plugs'] if c['x'] < 0), 4),
        'lantern': {k: (round(v, 4) if isinstance(v, float) else v) for k, v in LN.items()} if LN else None,
        'sockets': [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in s.items()} for s in plan['sockets']],
        'continuity': gap_report(plan),
        'propClearance': clearance_report(plan),
    }
    seen = {}
    for s in plan['segments']:
        seen.setdefault(s['asset'], {'sx': round(s['sx'], 4), 'sy': round(s['sy'], 4), 'sz': round(s['sz'], 4)})
    rep['segmentScale'] = seen
    rep['meta'] = {k: {kk: round(vv, 4) for kk, vv in v.items()} for k, v in _meta.items()
                   if k in W['assets'] + [W['arch']['asset'], W['lantern']['asset']]}
    if '--positions' in sys.argv:
        rep['segments'] = [[s['kind'], s['i'], s['asset'], round(s['x'], 4), round(s['z'], 4), round(s['rotY'], 5)]
                           for s in plan['segments']]
    out = json.dumps(rep, indent=1)
    print(out)
    if '--json' in sys.argv:
        Path(sys.argv[sys.argv.index('--json') + 1]).write_text(out + '\n')
