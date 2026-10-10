"""mag_cast_peak.py - measure the R_Hand extension peak of WH_Mag_Cast1H
(cross-check Cast2H) on the player body GLB, offline, numpy only.

Method: full FK per frame on the glTF node hierarchy using the animation's
own TRS channels (dense 30fps bake -> LINEAR interpolation on quats).
Extension metric = distance from R_Hand world position to the torso axis
(line through Hips and Chest world positions) - hand away from body = cast
extension. Peak frame -> time fraction of clip duration.

Output: scratch/mag_cast_peak.json + stdout table.
"""
import json, struct
import numpy as np

GLB = 'art-direction/3d/assets/races_regen/rigged/human-hunter-male.combat-sword.glb'
CLIPS = ['WH_Mag_Cast1H', 'WH_Mag_Cast2H']

b = open(GLB, 'rb').read()
jl = struct.unpack('<I', b[12:16])[0]
J = json.loads(b[20:20 + jl])
bin0 = 20 + jl + 8

def acc(i):
    a = J['accessors'][i]
    n = {'VEC3': 3, 'VEC4': 4, 'SCALAR': 1}[a['type']]
    ct = {5126: np.float32, 5123: np.int16, 5125: np.uint32}[a['componentType']]
    v = J['bufferViews'][a['bufferView']]
    off = bin0 + v.get('byteOffset', 0) + a.get('byteOffset', 0)
    return np.frombuffer(b, ct, a['count'] * n, off).reshape(-1, n)

names = [nd.get('name', '?') for nd in J['nodes']]
parent = {}
for i, nd in enumerate(J['nodes']):
    for c in nd.get('children', []):
        parent[c] = i

def static_trs(nd):
    t = np.array(nd.get('translation', [0, 0, 0]), np.float64)
    r = np.array(nd.get('rotation', [0, 0, 0, 1]), np.float64)
    s = np.array(nd.get('scale', [1, 1, 1]), np.float64)
    return t, r, s

def trs_mat(t, r, s):
    x, y, z, w = r / np.linalg.norm(r)
    R = np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    M = np.eye(4)
    M[:3, :3] = R @ np.diag(s)
    M[:3, 3] = t
    return M

# order nodes so parents come first
order = []
seen = set()
def walk(i):
    if i in seen:
        return
    seen.add(i)
    if i in parent:
        walk(parent[i])
    order.append(i)
for i in range(len(J['nodes'])):
    walk(i)

def sample_track(sampler, t):
    ti = acc(sampler['input'])[:, 0].astype(np.float64)
    tv = acc(sampler['output'])
    if tv.shape[1] == 4:  # quat: nlerp (dense keys, tiny deltas)
        if t <= ti[0]:
            return tv[0].copy()
        if t >= ti[-1]:
            return tv[-1].copy()
        k = np.searchsorted(ti, t) - 1
        u = (t - ti[k]) / max(ti[k + 1] - ti[k], 1e-9)
        if t == ti[k + 1]:
            u = 0.0
        v = tv[k] * (1 - u) + tv[k + 1] * u
        return v / np.linalg.norm(v)
    v = tv[:, 0]
    if len(ti) <= 1:
        return np.full(tv.shape[1:], v[0])
    return np.stack([np.interp(t, ti, tv[:, c]) for c in range(tv.shape[1])])

def measure(anim_name):
    anim = next(a for a in J['animations'] if a.get('name') == anim_name)
    # channel overrides per node/path
    ch = {(names[c['target']['node']], c['target']['path']): anim['samplers'][c['sampler']]
          for c in anim['channels']}
    dur = max(float(np.max(acc(s['input']))) for s in anim['samplers'])
    frames = int(round(dur * 30)) + 1
    rows = []
    for f in range(frames):
        t = min(f / 30.0, dur)
        world = {}
        for i in order:
            nd = J['nodes'][i]
            nm = names[i]
            st, sr, ss = static_trs(nd)
            tt = sample_track(ch[(nm, 'translation')], t) if (nm, 'translation') in ch else st
            tr = sample_track(ch[(nm, 'rotation')], t) if (nm, 'rotation') in ch else sr
            ts = sample_track(ch[(nm, 'scale')], t) if (nm, 'scale') in ch else ss
            local = trs_mat(tt, tr, ts)
            world[i] = world[parent[i]] @ local if i in parent else local
        def P(n):
            return world[names.index(n)][:3, 3]
        hips, chest, hand = P('Hips'), P('Chest'), P('R_Hand')
        axis = chest - hips
        axis = axis / np.linalg.norm(axis)
        d = hand - hips
        ext = float(np.linalg.norm(d - np.dot(d, axis) * axis))  # dist hand->torso line
        rows.append({'frame': f, 't': round(t, 4), 'hand': [round(v, 4) for v in hand],
                     'ext': round(ext, 4)})
    peak = max(rows, key=lambda r: r['ext'])
    return {'clip': anim_name, 'duration_s': round(dur, 4), 'frames': frames,
            'peak_frame': peak['frame'], 'peak_t': peak['t'],
            'peak_fraction': round(peak['t'] / dur, 4), 'peak_ext': peak['ext'],
            'rows': rows}

out = {c: measure(c) for c in CLIPS}
for c, r in out.items():
    print('%s  dur %.3fs  frames %d  PEAK frame %d (t %.3fs)  fraction %.4f  ext %.4f'
          % (c, r['duration_s'], r['frames'], r['peak_frame'], r['peak_t'],
             r['peak_fraction'], r['peak_ext']))
    band = [x for x in r['rows'] if x['ext'] >= 0.9 * r['peak_ext']]
    print('  90%%-band frames %d..%d  (t %.3f..%.3s)' % (
        band[0]['frame'], band[-1]['frame'], band[0]['t'], band[-1]['t']))
    # every 5th frame ext for the report
    print('  ext by 5s:', [[x['frame'], x['ext']] for x in r['rows'][::5]])
json.dump(out, open('scratch/mag_cast_peak.json', 'w'))
print('wrote scratch/mag_cast_peak.json')