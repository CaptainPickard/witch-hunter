#!/usr/bin/env python3
"""Round H proof: three Blender shot lists for roundH_proof_render.py, built
from the wall mirror, the scatter mirror plan and CONFIG. Every shot carries
the game's night rig for that player position:
  - fog = FogExp2 at the cemetery-ramp density/color for the PLAYER position
    (game.js cemeteryFogTick: one global fog per frame, not a local volume);
  - moon (azimuth/elevation/color/intensity), hemi fill;
  - light pool = the 4 nearest lanternPost sockets (heightFraction/offset)
    plus the player's lantern at hip height;
  - the dirt-path ribbon (centerline sway, halfWidth);
  - third-person camera = player + camDistance behind at camPitch 20 deg
    (eye = camHeight + camDistance * sin 20), like the Round G eye line.
  roundH_proof_scene.py <repo-root> <scatter-plan.json> <out-shots.json>
Shot 1: the new spawn, facing map center (faceTowards(0, 0)).
Shot 2: the player on the path end at the graveyard fence mouth, facing in.
Shot 3 (continuation run): the fullest region-A young-tree snare ring next to
        its nearest free bramble (biome_library/wh-bramble-pixelated.glb), seen
        from the map-centre side of the line between them (wall behind), with the player lantern.
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
    for t in rp['trees']:
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
    """game.js cemeteryFogTick, verbatim math (sRGB lerp is done in linear in
    three: THREE.Color stores linear; the renderer converts both ends)."""
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
    """yaw_to = (x, z) the player faces; camera behind at pitch 20 deg."""
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


def shot(stem, px, pz, face, lens, radius, extra=None):
    cam, aim, lights = rig(px, pz, face)
    s = {'stem': stem, 'objects': near(px, pz, radius), 'cam': cam, 'aim': aim, 'lens': lens,
         'lights': lights, 'fog': fog_at(px, pz), 'moon': MOON, 'hemi': HEMI, 'sky': SKY,
         'path': PATH, 'pathHalfWidth': DP['halfWidth'], 'pathY': DP['y'], 'player': [px, pz]}
    s.update(extra or {})
    return s


sp = RA['spawn']
shot1 = shot('01-spawn-view', sp['x'], sp['z'], (0.0, 0.0), 20, 110)
# fence mouth = the path end (DP.zTo is "AT the graveyard fence mouth"), facing into the yard
mz = DP['zTo']
shot2 = shot('02-cemetery-fog-approach', path_x(mz), mz, (ZONE['x'], ZONE['z']), 20, 110)

ra = splan[RA['id']]
snares = ra['instances'].get('whBushSnare', [])
brambles = ra['instances'].get('bramble', [])
young = [t for t in ra['trees'] if t['asset'] in ('youngBirch', 'youngDeadTree')]


def ring_n(t):
    return sum(1 for b in snares if math.hypot(b['x'] - t['x'], b['z'] - t['z']) < 3)


def near_bramble(t):
    return min(brambles, key=lambda b: math.hypot(b['x'] - t['x'], b['z'] - t['z']))


# continuation: host = the young tree with the fullest snare ring, ties -> nearest free bramble,
# so one frame holds both the ring and a bramble
host = min(young, key=lambda t: (-ring_n(t), math.hypot(near_bramble(t)['x'] - t['x'], near_bramble(t)['z'] - t['z'])))
hx, hz = host['x'], host['z']
br = near_bramble(host)
mx, mz3 = (hx + br['x']) / 2, (hz + br['z']) / 2
ux, uz = br['x'] - hx, br['z'] - hz
ul = math.hypot(ux, uz); ux, uz = ux / ul, uz / ul
nx, nz = -uz, ux
if nx * (ZONE['x'] - mx) + nz * (ZONE['z'] - mz3) < 0:   # stand on the inner (map-centre) side
    nx, nz = -nx, -nz                                     # so the boundary wall is backdrop, not occluder
# player (and lantern) 2.5 m in front of the pair; camera 7.3 m back, behind the player like
# the third-person rig, so the 7.6 m pair spans ~55 deg of the 24 mm frame
px3, pz3 = mx + nx * 2.5, mz3 + nz * 2.5
cx3, cz3 = mx + nx * 7.3, mz3 + nz * 7.3
shot3 = shot('03-bramble-snare-closeup', px3, pz3, (mx, mz3), 24, 45,
             {'host': {'asset': host['asset'], 'x': hx, 'z': hz, 'ring': ring_n(host),
                       'bramble': {'x': br['x'], 'z': br['z'], 'scale': br['scale'],
                                   'dist': round(ul, 2)}}})
# closeup camera: lower and nearer than the gameplay rig so ring + bramble fill the frame
shot3['cam'] = [cx3, 2.2, cz3]
shot3['aim'] = [mx, 0.5, mz3]

json.dump([shot1, shot2, shot3], open(out_p, 'w'))
for s in (shot1, shot2, shot3):
    kinds = {}
    for o in s['objects']:
        kinds[o['name']] = kinds.get(o['name'], 0) + 1
    print(s['stem'], 'player', [round(v, 2) for v in s['player']], 'cam', [round(v, 1) for v in s['cam']],
          'fog d/w/density', s['fog']['d'], s['fog']['w'], round(s['fog']['density'], 4),
          'lights', len(s['lights']), kinds, s.get('host', ''))
