"""Census 2: full node list + per-clip channel coverage of the cast clip (which nodes move)."""
import json, struct
p = '/tmp/wh-worldfeat/art-direction/3d/assets/races_regen/rigged/human-hunter-male.combat-sword.glb'
b = open(p, 'rb').read()
jl = struct.unpack('<I', b[12:16])[0]
J = json.loads(b[20:20 + jl])
names = [n.get('name', '?') for n in J['nodes']]
parent = {}
for i, nd in enumerate(J['nodes']):
    for c in nd.get('children', []):
        parent[c] = i
print('FULL NODE LIST (idx name parent):')
for i, n in enumerate(names):
    print(' %2d %-22s parent=%s' % (i, n, names[parent[i]] if i in parent else 'ROOT'))
anim = next(a for a in J['animations'] if a.get('name') == 'WH_Mag_Cast1H')
cov = {}
for ch in anim['channels']:
    t = ch['target']
    nm = names[t['node']] if 'node' in t else '?'
    cov.setdefault(nm, set()).add(t['path'])
print('\nWH_Mag_Cast1H channel coverage:')
for nm in names:
    if nm in cov:
        print('  %-22s %s' % (nm, sorted(cov[nm])))
    else:
        print('  %-22s (no channels in this clip)' % nm)
# count locomotion clip coverage too (WalkF)
anim2 = next(a for a in J['animations'] if a.get('name') == 'WH_Mag_WalkF')
cov2 = {}
for ch in anim2['channels']:
    nm = names[ch['target']['node']]
    cov2.setdefault(nm, set()).add(ch['target']['path'])
print('\nWH_Mag_WalkF has channels on %d nodes: %s' % (len(cov2), sorted(cov2.keys())))
# CAST1H2 (2026-10-10): R9 partition proof over EVERY clip of the player GLB -
# each channel's node must fall in exactly one of UPPER / LOWER (no overlap, no
# orphan), written to scratch/mag_cast_track_partition.json.
UPPER = ['Spine', 'Chest', 'Neck', 'Head', 'L_Shoulder', 'L_UpperArm', 'L_Forearm', 'L_Hand',
         'R_Shoulder', 'R_UpperArm', 'R_Forearm', 'R_Hand']
LOWER = ['Hips', 'Root', 'L_Thigh', 'L_Shin', 'L_Foot', 'R_Thigh', 'R_Shin', 'R_Foot']
overlap = sorted(set(UPPER) & set(LOWER))
per_clip = {}
orphans = set()
for a in J['animations']:
    nodes = sorted({names[ch['target']['node']] for ch in a['channels']})
    up = [n for n in nodes if n in UPPER]
    lo = [n for n in nodes if n in LOWER]
    orph = [n for n in nodes if n not in UPPER and n not in LOWER]
    orphans.update(orph)
    per_clip[a.get('name', '?')] = {'channels': len(a['channels']), 'upperNodes': len(up),
                                    'lowerNodes': len(lo), 'orphanNodes': orph}
out = {'glb': p.split('/wh-worldfeat/')[-1], 'upper': UPPER, 'lower': LOWER,
       'overlap': overlap, 'orphanNodes': sorted(orphans),
       'neverAnimated': [n for n in names if all(n not in
                         {names[ch['target']['node']] for ch in a['channels']} for a in J['animations'])],
       'clips': per_clip}
json.dump(out, open('/tmp/wh-worldfeat/scratch/mag_cast_track_partition.json', 'w'), indent=1)
print('\nR9 PARTITION: upper %d lower %d overlap %s orphans %s clips %d neverAnimated %s' % (
    len(UPPER), len(LOWER), overlap, sorted(orphans), len(per_clip), out['neverAnimated']))
