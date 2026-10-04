"""Independent GLB quaternion FK + channel scope check for bandit bend fixes.
Usage: python3 scratch/verify_bandit_clamp.py BEFORE.mixamo.glb AFTER.mixamo.glb --out JSON
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from glb_append_clips import parse, accessor_bytes, accessor_values

CLIPS = ('WH_Hit_Large_L', 'WH_Attack_Horiz')
BONES = ('Spine', 'Chest')


def sample_bends(path):
    doc, blob = parse(path)
    nodes = doc['nodes']
    parents = {child: i for i, node in enumerate(nodes) for child in node.get('children', [])}
    selected = {n: next(i for i, v in enumerate(nodes) if v.get('name') == n) for n in BONES}
    rest = {i: Rotation.from_quat(node.get('rotation', [0, 0, 0, 1])) for i, node in enumerate(nodes)}
    def world(i, rotations):
        return world(parents[i], rotations) * rotations[i] if i in parents else rotations[i]
    rest_axes = {n: world(i, rest).apply([0, 1, 0]) for n, i in selected.items()}
    result = {}
    for anim in doc['animations']:
        if anim['name'] not in CLIPS:
            continue
        rotations = {}
        for channel in anim['channels']:
            if channel['target']['path'] == 'rotation':
                sampler = anim['samplers'][channel['sampler']]
                rotations[channel['target']['node']] = accessor_values(doc, blob, sampler['output'])
        count = len(next(iter(rotations.values())))
        series = {n: {'world': [], 'local': []} for n in BONES}
        for frame in range(count):
            pose = dict(rest)
            pose.update({i: Rotation.from_quat(v[frame]) for i, v in rotations.items()})
            for name, i in selected.items():
                a = world(i, pose).apply([0, 1, 0])
                series[name]['world'].append(float(np.degrees(np.arccos(np.clip(a @ rest_axes[name], -1, 1)))))
                a = (rest[i].inv() * pose[i]).apply([0, 1, 0])
                series[name]['local'].append(float(np.degrees(np.arccos(np.clip(a[1], -1, 1)))))
        result[anim['name']] = {n: {kind: {'max_degrees': max(values),
            'max_frame': int(np.argmax(values)), 'mid_degrees': values[round((count - 1) / 2)],
            'end_degrees': values[-1]} for kind, values in kinds.items()} for n, kinds in series.items()}
    return result


def verify_scope(before, after):
    old, ob = parse(before)
    new, nb = parse(after)
    changes = []
    unchanged = 0
    for anim in old['animations']:
        other = next(a for a in new['animations'] if a['name'] == anim['name'])
        channels = {(new['nodes'][c['target']['node']]['name'], c['target']['path']): c for c in other['channels']}
        for channel in anim['channels']:
            name, path = old['nodes'][channel['target']['node']]['name'], channel['target']['path']
            a = anim['samplers'][channel['sampler']]
            b = other['samplers'][channels[(name, path)]['sampler']]
            assert accessor_bytes(old, ob, a['input']) == accessor_bytes(new, nb, b['input'])
            identical = accessor_bytes(old, ob, a['output']) == accessor_bytes(new, nb, b['output'])
            if not identical:
                changes.append([anim['name'], name, path])
                assert anim['name'] in CLIPS and name in BONES and path == 'rotation', changes[-1]
            else:
                unchanged += 1
    assert set(map(tuple, changes)) == {(c, b, 'rotation') for c in CLIPS for b in BONES}
    return {'changed_channels': changes, 'identical_channels': unchanged,
            'all_input_times_identical': True, 'only_requested_torso_rotations_changed': True}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('before')
    p.add_argument('after')
    p.add_argument('--out', required=True)
    a = p.parse_args()
    report = {'before': str(Path(a.before).resolve()), 'after': str(Path(a.after).resolve()),
        'before_sha256': hashlib.sha256(Path(a.before).read_bytes()).hexdigest(),
        'after_sha256': hashlib.sha256(Path(a.after).read_bytes()).hexdigest(),
        'metric': 'independent quaternion FK: world bone Y relative to rest world Y; local swing relative to rest local rotation',
        'before_bends': sample_bends(a.before), 'after_bends': sample_bends(a.after),
        'scope': verify_scope(a.before, a.after)}
    assert all(b['world']['max_degrees'] <= 25.002 for c in report['after_bends'].values() for b in c.values())
    report['pass'] = True
    Path(a.out).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
