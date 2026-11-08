"""MAGICLASS M2 verify gate for WH_Mag_Cast1H_L (all PASS required).
Pristine prefix + JSON equality vs /tmp/magiclass_pristine.glb, 43 animations,
FK (same method as mag_cast_peak.py): L_Hand forward peak z +0.92..+1.02 near
fraction 0.46, R_Hand home (|z| <= 0.15), per-frame x/z mirror symmetry with
Cast1H, ground clamp (feet y unchanged), unit quats, Hips y (crouch) unchanged.
Writes scratch/verify_mirror_cast.json.
"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from glb_append_clips import parse, accessor_values

GLB = 'art-direction/3d/assets/races_regen/rigged/human-hunter-male.combat-sword.glb'
PRISTINE = '/tmp/magiclass_pristine.glb'
doc, blob = parse(GLB)
res = {}


def gate(k, ok, info):
    res[k] = {'pass': bool(ok), 'info': info}
    print('%-22s %s  %s' % (k, 'PASS' if ok else 'FAIL', info))


raw, praw = Path(GLB).read_bytes(), Path(PRISTINE).read_bytes()
pdoc, pbin = parse(PRISTINE)
gate('prefixBin', blob[:len(pbin)] == pbin, '%d pristine BIN bytes' % len(pbin))
jsonok = all((doc[k][:len(v)] == v) if k in ('animations', 'accessors', 'bufferViews')
             else (doc[k] == v) for k, v in pdoc.items() if k != 'buffers')
gate('prefixJSON', jsonok, 'all non-buffer keys equal / append-only')
gate('count43', len(doc['animations']) == 43 and doc['animations'][-1]['name'] == 'WH_Mag_Cast1H_L',
     '%d animations, last %s' % (len(doc['animations']), doc['animations'][-1]['name']))
names = [n.get('name') for n in doc['nodes']]
parent = {c: i for i, n in enumerate(doc['nodes']) for c in n.get('children', [])}
order, seen = [], set()


def walk(i):
    if i in seen:
        return
    seen.add(i)
    if i in parent:
        walk(parent[i])
    order.append(i)


for i in range(len(names)):
    walk(i)


def qmat(t, r, s):
    x, y, z, w = r / np.linalg.norm(r)
    R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                  [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                  [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    M = np.eye(4)
    M[:3, :3] = R @ np.diag(s)
    M[:3, 3] = t
    return M


def fk(name):
    a = next(a for a in doc['animations'] if a['name'] == name)
    tr = {}
    for c in a['channels']:
        s = a['samplers'][c['sampler']]
        tr[(names[c['target']['node']], c['target']['path'])] = np.array(
            accessor_values(doc, blob, s['output']), np.float64)
    n = len(next(iter(tr.values())))
    frames = []
    for f in range(n):
        W = {}
        for i in order:
            nd, nm = doc['nodes'][i], names[i]
            t = tr[(nm, 'translation')][f] if (nm, 'translation') in tr else np.array(nd.get('translation', [0, 0, 0]), float)
            r = tr[(nm, 'rotation')][f] if (nm, 'rotation') in tr else np.array(nd.get('rotation', [0, 0, 0, 1]), float)
            s = tr[(nm, 'scale')][f] if (nm, 'scale') in tr else np.array(nd.get('scale', [1, 1, 1]), float)
            L = qmat(t, r, s)
            W[i] = W[parent[i]] @ L if i in parent else L
        frames.append({nm: W[names.index(nm)][:3, 3] for nm in
                       ('Hips', 'L_Hand', 'R_Hand', 'L_Foot', 'R_Foot')})
    a_ch = len(a['channels'])
    qs = np.concatenate([v for (nm, p), v in tr.items() if p == 'rotation'])
    return frames, a_ch, float(np.abs(np.linalg.norm(qs, axis=1) - 1).max())


R, chR, _ = fk('WH_Mag_Cast1H')
L, chL, qerr = fk('WH_Mag_Cast1H_L')
n = len(L)
gate('dense60', chL == 60 and chR == 60 and n == len(R) == 70, '%d channels, %d frames' % (chL, n))
gate('unitQuats', qerr < 1e-4, 'max | |q|-1 | %.2e' % qerr)
lz = np.array([fr['L_Hand'][2] for fr in L])
pk = int(np.argmax(lz))
gate('lHandPeak', 0.92 <= lz[pk] <= 1.02 and abs(pk / (n - 1) - 0.4638) <= 0.05,
     'L_Hand z peak %+.4f at frame %d (fraction %.4f); f32 z %+.4f' % (lz[pk], pk, pk / (n - 1), lz[32]))
rz = np.array([fr['R_Hand'][2] for fr in L])
rzr = np.array([fr['L_Hand'][2] for fr in R])
drh = float(np.abs(rz - rzr).max())
# IO ruling A (2026-10-10): rHandHome |z| <= 0.15 was a WRONG ASSUMPTION - the
# source Cast1H swings its off-hand fwd/back through the whole clip (L_Hand z
# -0.58..+0.78) and the game already shows that swing on the glove hand every
# right-hand cast. Amended: Cast1H_L's R_Hand z must mirror Cast1H's L_Hand z
# within 2 cm per frame (same counter-swing, mirrored).
gate('rHandHome', drh <= 0.02, 'IO-A amended: |Cast1H_L R_Hand z - mirror(Cast1H L_Hand z)| max %.4f m (range %.3f..%.3f)' % (drh, rz.min(), rz.max()))
sym = 0.0
for fl, fr in zip(L, R):
    for a, b in (('L_Hand', 'R_Hand'), ('R_Hand', 'L_Hand'), ('L_Foot', 'R_Foot'), ('Hips', 'Hips')):
        p, q = fl[a], fr[b] * np.array([-1, 1, 1])
        sym = max(sym, float(np.abs(p - q).max()))
gate('mirrorSymmetry', sym <= 0.02, 'max |mirror(Cast1H) - Cast1H_L| %.4f m (rig L/R asym ~8mm)' % sym)
fy = max(abs(fl[k][1] - fr[o][1]) for fl, fr in zip(L, R) for k, o in (('L_Foot', 'R_Foot'), ('R_Foot', 'L_Foot')))
gate('groundClamp', fy <= 0.01, 'feet y delta vs mirrored source %.4f m' % fy)
hy = max(abs(fl['Hips'][1] - fr['Hips'][1]) for fl, fr in zip(L, R))
gate('noCrouchChange', hy <= 1e-4, 'Hips y delta %.2e m' % hy)
res['lHandZByFrame'] = [round(float(v), 4) for v in lz]
json.dump(res, open('scratch/verify_mirror_cast.json', 'w'), indent=1)
bad = [k for k, v in res.items() if isinstance(v, dict) and not v['pass']]
print('ALL PASS' if not bad else 'FAIL: %s' % bad)
sys.exit(1 if bad else 0)
