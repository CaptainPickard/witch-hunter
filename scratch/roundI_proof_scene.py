#!/usr/bin/env python3
"""Round I proof: three Blender shot lists for roundH_proof_render.py (reused as-is), built
from the wall mirror, the scatter mirror plan and CONFIG, with the same night rig as
roundH_proof_scene.py (moon, hemi, sky, FogExp2 at the player position, lantern-post light
pool + player lantern, dirt path).
  roundI_proof_scene.py <repo-root> <scatter-plan.json> <out-shots.json>
Shot 1 01-variants-lineup: synthetic stage. reachTreeA/B/C stand side by side, each scaled to
        17 m in-world height (the middle of the scatter's 15.5-18.5 band). A back row of world
        yews/witchwoods stands 30-60 m behind them for the mist. Region A fog at its base density.
Shot 2 02-reacht-enclosure: the most isolated broad (A/B) reach tree. The camera stands inside
        the canopy drip line at eye height and looks up past the trunk into the limbs.
Shot 3 03-world-mix: the region-A cluster where CONFIG reachTreeA + reachTreeC stand next to a
        witchwood (x 22-28, z -5..-11), camera bearing searched for a clear sightline (see code).
"""
import json, math, sys
from pathlib import Path

root, plan_p, out_p = Path(sys.argv[1]).resolve(), sys.argv[2], sys.argv[3]
sys.argv = [sys.argv[0], str(root)]
sys.path.insert(0, str(Path(__file__).parent))
import wall_mirror as WM   # noqa: E402  (module reads sys.argv[1] = repo root)

CFG, MANIFEST = WM.CFG, WM.MANIFEST
wplan = WM.wall_plan()
W = CFG['boundaryWall']
splan = json.load(open(plan_p))
RA = CFG['regionA']
DP = CFG['world']['dirtPath']
LT = CFG['lighting']
P = CFG['player']


def glb(name):
    return str(root / MANIFEST[name])


def obj(name, x, z, rot, sx, sy=None, sz=None, y=0.0, kind='prop'):
    return {'glb': glb(name), 'name': name, 'x': x, 'y': y, 'z': z, 'rotY': rot,
            'sx': sx, 'sy': sx if sy is None else sy, 'sz': sx if sz is None else sz, 'kind': kind}


ALL = []
for s in wplan['segments']:
    ALL.append(obj(s['asset'], s['x'], s['z'], s['rotY'], s['sx'], s['sy'], s['sz'], -W['sinkM'], s['kind']))
for rid, rp in splan.items():
    for p in rp['props']:
        if p['asset'] in MANIFEST:
            ALL.append(obj(p['asset'], p['x'], p['z'], p.get('rotY', 0) or 0, p['scale'], y=p.get('y', 0) or 0))
    # the plan's props already carry the scatter trees (roundH_proof_scene.py drew them twice)
    have = {(p['asset'], p['x'], p['z']) for p in rp['props']}
    for t in rp['trees']:
        if (t['asset'], t['x'], t['z']) not in have:
            ALL.append(obj(t['asset'], t['x'], t['z'], t['rotY'], t['scale'], kind='scatterTree'))
    for name, lst in rp['instances'].items():
        for it in lst:
            ALL.append(obj(name, it['x'], it['z'], it['rotY'], it['scale'], kind='instanced'))


def near(cx, cz, rad):
    return [o for o in ALL if math.hypot(o['x'] - cx, o['z'] - cz) <= rad]


def path_x(z):
    return DP['swayAmp'] * math.sin(2 * math.pi * (z - DP['zFrom']) / DP['swayPeriod'])


PATH = [[round(path_x(z), 4), z] for z in [DP['zFrom'] - i * 0.5 for i in range(int((DP['zFrom'] - DP['zTo']) / 0.5) + 1)]]
CF = RA['cemeteryFog']
ZONE = [k for k in CFG['scatter']['keepOut'] if k['regionId'] == CF['zoneKeepOutRegionId']][0]


def hexrgb(h):
    return [((h >> 16) & 255) / 255, ((h >> 8) & 255) / 255, (h & 255) / 255]


def fog_at(px, pz):
    """game.js cemeteryFogTick (roundH_proof_scene.py, verbatim)."""
    d = math.hypot((px - ZONE['x']) / ZONE['rx'], (pz - ZONE['z']) / ZONE['rz'])
    t = min(1, max(0, (d - CF['rampStart']) / (CF['rampEnd'] - CF['rampStart'])))
    w = t * t * (3 - 2 * t)
    return {'d': round(d, 4), 'w': round(w, 4),
            'density': RA['fogDensity'] + (CF['density'] - RA['fogDensity']) * w,
            'baseColor': hexrgb(RA['fogColor']), 'targetColor': hexrgb(CF['color'])}


SOCK = CFG['lightSockets']['lanternPost']
post_h = WM.meta('lanternPost')['height']
POSTS = []
for p in RA['props']:
    if p['asset'] != 'lanternPost':
        continue
    c, s = math.cos(p['rotY']), math.sin(p['rotY'])
    ox, oz = SOCK['offset'][0] * p['scale'], SOCK['offset'][1] * p['scale']
    POSTS.append({'x': p['x'] + ox * c + oz * s, 'z': p['z'] - ox * s + oz * c,
                  'y': post_h * p['scale'] * SOCK['heightFraction']})


def rig(px, pz, yaw_to):
    fx, fz = yaw_to[0] - px, yaw_to[1] - pz
    fl = math.hypot(fx, fz); fx, fz = fx / fl, fz / fl
    pitch = math.radians(20)
    back = P['camDistance'] * math.cos(pitch)
    eye = P['camHeight'] + P['camDistance'] * math.sin(pitch)
    cam = [px - fx * back, eye, pz - fz * back]
    aim = [px + fx * 14, 1.2, pz + fz * 14]
    pool = sorted(POSTS, key=lambda q: math.hypot(q['x'] - px, q['z'] - pz))[:CFG['lightPool']['size']]
    lights = [{'x': q['x'], 'y': q['y'], 'z': q['z'], 'cd': SOCK['intensity'],
               'color': hexrgb(CFG['lightPool']['color'])} for q in pool]
    lights.append({'x': px, 'y': LT['lanternAnchorOffset'][1], 'z': pz, 'cd': LT['lanternIntensity'],
                   'color': hexrgb(LT['lanternColor'])})
    return cam, aim, lights


MOON = {'azDeg': LT['moonAzimuthDeg'], 'elDeg': LT['moonElevationDeg'], 'color': hexrgb(LT['moonColor']),
        'intensity': LT['moonIntensity']}
HEMI = {'sky': hexrgb(LT['hemiSkyColor']), 'ground': hexrgb(LT['hemiGroundColor']),
        'intensity': LT['hemiBaseIntensity'] * RA['ambientLightLevel']}
SKY = {k: hexrgb(CFG['sky'][k]) for k in ('zenithColor', 'horizonBand', 'horizonGlow')}
SKY['glowStop'] = CFG['sky']['horizonGlowStop']


def shot(stem, px, pz, face, lens, objects, extra=None):
    cam, aim, lights = rig(px, pz, face)
    s = {'stem': stem, 'objects': objects, 'cam': cam, 'aim': aim, 'lens': lens,
         'lights': lights, 'fog': fog_at(px, pz), 'moon': MOON, 'hemi': HEMI, 'sky': SKY,
         'path': PATH, 'pathHalfWidth': DP['halfWidth'], 'pathY': DP['y'], 'player': [px, pz]}
    s.update(extra or {})
    return s


ra_props = RA['props']
rb_props = CFG['regionB']['props']

# ---- shot 1: variants lineup (synthetic stage, out past region A's east side) ------------------
# Stage centre (60, 20) in region A, and only the staged trees + backdrop are passed in (no
# world objects), so nothing from the map occludes. The camera looks -z toward the moon so
# the limbs read as backlit silhouettes against the sky glow.
SX, SZ, HM = 60.0, 20.0, 17.0
line = []
for i, (v, rot) in enumerate((('A', 0.4), ('B', 2.2), ('C', 5.1))):
    mt = WM.meta('reachTree' + v)
    line.append(obj('reachTree' + v, SX + (i - 1) * 21.0, SZ, rot, HM / mt['height']))
back = []
for j, (name, dx, dz, h) in enumerate((('yewTree', -34, -32, 17), ('witchwoodTree', -12, -40, 16),
                                       ('yewTree', 9, -52, 18), ('witchwoodTree', 27, -36, 17),
                                       ('yewTree', 41, -58, 16), ('witchwoodTree', -45, -60, 18))):
    back.append(obj(name, SX + dx, SZ + dz, j * 1.3, h / WM.meta(name)['height']))
shot1 = shot('01-variants-lineup', SX, SZ + 30, (SX, SZ), 22, line + back,
             {'lineup': [{'asset': o['name'], 'x': o['x'], 'z': o['z'], 'scale': round(o['sx'], 3)} for o in line]})
shot1['lights'] = shot1['lights'][-1:]                    # player lantern only, no posts out here
shot1['lights'][0].update({'x': SX, 'z': SZ + 12})
shot1['fog'] = dict(shot1['fog'], density=RA['fogDensity'], w=0.0)
shot1['cam'] = [SX, 2.6, SZ + 44.0]
shot1['aim'] = [SX, 8.0, SZ]

# ---- shot 2: under the most isolated broad reach tree (A or B) ---------------------------------
# The CONFIG reachTreeB row stands in a yew cluster, and in the first render the neighbours' foliage
# filled the frame. So the host is the A/B reach tree (CONFIG or scatter, either region) whose
# nearest other tree is farthest away.
TREES = [(rid, q) for rid, rp in splan.items() for q in rp['props']
         if any(k in q['asset'] for k in ('Tree', 'Oak', 'Ash', 'Birch'))]


def nn(q):
    return min(math.hypot(o['x'] - q['x'], o['z'] - q['z']) for _, o in TREES if o is not q)


rid2, hostB = max(((r, q) for r, q in TREES if q['asset'] in ('reachTreeA', 'reachTreeB')),
                  key=lambda t: (nn(t[1]), t[1]['asset'], t[1]['x']))
mB = WM.meta(hostB['asset'])
crown = mB['width'] * hostB['scale'] / 2                     # canopy half-width (m)
# stand 0.45 x crown out from the trunk on the map-centre side, face back past the trunk, look up
ux, uz = -hostB['x'], -hostB['z']
ul = math.hypot(ux, uz); ux, uz = ux / ul, uz / ul
# swung 45 deg off the map-centre bearing: the straight bearing put the camera on a root buttress
ca, sa = math.cos(math.radians(45)), math.sin(math.radians(45))
ux, uz = ux * ca - uz * sa, ux * sa + uz * ca
px2, pz2 = hostB['x'] + ux * crown * 0.45, hostB['z'] + uz * crown * 0.45
shot2 = shot('02-reacht-enclosure', px2, pz2, (hostB['x'], hostB['z']), 14, near(hostB['x'], hostB['z'], 60),
             {'host': {'asset': hostB['asset'], 'region': rid2, 'x': round(hostB['x'], 2), 'z': round(hostB['z'], 2),
                       'scale': round(hostB['scale'], 3), 'nearest_tree_m': round(nn(hostB), 1),
                       'height_m': round(mB['height'] * hostB['scale'], 2), 'crown_halfwidth_m': round(crown, 2)}})
if rid2 == CFG['regionB']['id']:                             # region B rig: its own fog + fill
    RB = CFG['regionB']
    shot2['fog'] = {'d': None, 'w': 0.0, 'density': RB['fogDensity'], 'baseColor': hexrgb(RB['fogColor']),
                    'targetColor': hexrgb(RB['fogColor'])}
    shot2['hemi'] = dict(HEMI, intensity=LT['hemiBaseIntensity'] * RB['ambientLightLevel'] * LT['regionBFillMult'])
shot2['cam'] = [px2 + ux * 1.2, 1.7, pz2 + uz * 1.2]
# aim: the trunk at ~2/3 tree height, a steep upward look into the limbs
shot2['aim'] = [hostB['x'] - ux * 2.0, mB['height'] * hostB['scale'] * 0.72, hostB['z'] - uz * 2.0]

# ---- shot 3: reach-tree + witchwood mix (region A east cluster) ------------------------------
cluster = [p for p in ra_props if p['asset'] in ('reachTreeA', 'reachTreeC', 'witchwoodTree')
           and 18 < p['x'] < 30 and -12 < p['z'] < -4]
cx3 = sum(p['x'] for p in cluster) / len(cluster)
cz3 = sum(p['z'] for p in cluster) / len(cluster)
# camera bearing search: the hand-picked west and NE views were swamped by neighbour yew/oak
# crowns. Candidates sit every 10 deg on a ring around the cluster centre (R = 20/24/28 m, region A
# side). Each foreign tree crown is a disc of radius 0.6 x half-width. Score: fewest crown discs
# hit by the camera -> member segments (a camera inside a crown counts 10), then the widest
# on-screen angular spread of the three members. Deterministic (no RNG).
def crown_r(q):
    return WM.meta(q['asset'])['width'] * q['scale'] / 2 * 0.6


def seg_d(px, pz, ax, az, bx, bz):
    vx, vz = bx - ax, bz - az
    t = max(0.0, min(1.0, ((px - ax) * vx + (pz - az) * vz) / (vx * vx + vz * vz)))
    return math.hypot(px - ax - t * vx, pz - az - t * vz)


foreign = [q for _, q in TREES if not any(q['x'] == c['x'] and q['z'] == c['z'] for c in cluster)]
best3 = None
for R in (20.0, 24.0, 28.0):
    for k in range(36):
        th = math.radians(10 * k)
        qx, qz = cx3 + R * math.cos(th), cz3 + R * math.sin(th)
        if qz < CFG['boundary']['z'] + 3 or math.hypot(qx, qz) > 80:
            continue
        hits = 0
        for q in foreign:
            r = crown_r(q)
            if math.hypot(q['x'] - qx, q['z'] - qz) < r:
                hits += 10
            hits += sum(1 for c in cluster if seg_d(q['x'], q['z'], qx, qz, c['x'], c['z']) < r)
        angs = [math.atan2(c['z'] - qz, c['x'] - qx) for c in cluster]
        spread = max(abs(math.remainder(a1 - a2, 2 * math.pi)) for a1 in angs for a2 in angs)
        key = (hits, -round(spread, 4), R, k)
        if best3 is None or key < best3[0]:
            best3 = (key, qx, qz)
(hits3, nspread3, R3, k3), qx3, qz3 = best3
dx3, dz3 = (cx3 - qx3) / R3, (cz3 - qz3) / R3
px3, pz3 = qx3 + dx3 * 6.0, qz3 + dz3 * 6.0                   # player 6 m ahead of the camera
shot3 = shot('03-world-mix', px3, pz3, (cx3, cz3), 18, near(cx3, cz3, 90),
             {'cluster': [{'asset': p['asset'], 'x': p['x'], 'z': p['z'], 'scale': p['scale'],
                           'height_m': round(WM.meta(p['asset'])['height'] * p['scale'], 1)} for p in cluster],
              'bearing': {'R': R3, 'deg': 10 * k3, 'crown_hits': hits3, 'spread_deg': round(math.degrees(-nspread3), 1)}})
shot3['cam'] = [qx3, 2.4, qz3]
shot3['aim'] = [cx3, 8.0, cz3]

json.dump([shot1, shot2, shot3], open(out_p, 'w'))
for s in (shot1, shot2, shot3):
    kinds = {}
    for o in s['objects']:
        kinds[o['name']] = kinds.get(o['name'], 0) + 1
    print(s['stem'], 'cam', [round(v, 1) for v in s['cam']], 'aim', [round(v, 1) for v in s['aim']],
          'fog density', round(s['fog']['density'], 4), 'lights', len(s['lights']),
          {k: v for k, v in kinds.items() if 'ree' in k or 'Oak' in k},
          s.get('host', ''), s.get('cluster', ''), s.get('lineup', ''), s.get('bearing', ''))
