"""Fail-closed GLB retarget verification with exact old-clip byte identity.
python3 scratch/verify_retarget.py OLD NEW --clips MANIFEST --bake-log LOG --out JSON
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
from glb_append_clips import parse, accessor_bytes, accessor_values


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify(old, new, expected, bake=None):
    jo, bo = parse(old)
    jn, bn = parse(new)
    original_names = [a['name'] for a in jo['animations']]
    names = [a['name'] for a in jn['animations']]
    assertions = {}
    def check(name, value):
        assertions[name] = bool(value)
    check('original_count_six', len(original_names) == 6)
    check('exact_animation_names', len(names) == len(set(names)) and
          set(names) == set(original_names) | set(expected))
    check('binary_prefix_identical', bn[:len(bo)] == bo)
    for key, value in jo.items():
        if key == 'buffers':
            continue
        actual = jn.get(key)
        equal = (actual[:len(value)] == value if key in
                 ('animations', 'accessors', 'bufferViews') else actual == value)
        check('original_json_' + key, equal)
    report = {'input': str(Path(old).resolve()), 'output': str(Path(new).resolve()),
              'source_sha256': sha(Path(old).read_bytes()),
              'output_sha256': sha(Path(new).read_bytes()),
              'original_bin_sha256': sha(bo), 'output_prefix_sha256': sha(bn[:len(bo)]),
              'originals': {}, 'new_clips': {}, 'assertions': assertions}
    by_name = {a['name']: a for a in jn['animations']}
    for anim in jo['animations']:
        name = anim['name']
        new_anim = by_name.get(name)
        hashes = []
        identical = new_anim == anim
        if new_anim:
            for old_s, new_s in zip(anim['samplers'], new_anim['samplers']):
                for field in ('input', 'output'):
                    left = accessor_bytes(jo, bo, old_s[field])
                    right = accessor_bytes(jn, bn, new_s[field])
                    identical &= left == right
                    hashes.append(sha(left))
        report['originals'][name] = {'channels': len(anim['channels']),
            'shape_identical': new_anim == anim, 'source_data_identical': bool(identical),
            'ordered_sampler_bytes_sha256': sha(''.join(hashes).encode())}
        check('original_' + name, identical)
    joints = set(jn['skins'][0]['joints'])
    for name in expected:
        if name not in by_name:
            check('new_' + name, False)
            report['new_clips'][name] = {'error': 'missing'}
            continue
        anim = by_name[name]
        targets = [(c['target']['node'], c['target']['path']) for c in anim['channels']]
        shape = Counter(path for _, path in targets)
        valid = (len(targets) == 60 and len(set(targets)) == 60 and
                 set(targets) == {(j, p) for j in joints for p in ('translation','rotation','scale')})
        sample_counts, durations = set(), set()
        max_rotation_span = 0.0
        max_quaternion_error = 0.0
        root_span = 0.0
        for channel in anim['channels']:
            sampler = anim['samplers'][channel['sampler']]
            times = [x[0] for x in accessor_values(jn, bn, sampler['input'])]
            values = accessor_values(jn, bn, sampler['output'])
            sample_counts.add(len(times))
            durations.add(round(times[-1], 6))
            valid &= sampler.get('interpolation','LINEAR') == 'LINEAR'
            valid &= len(values) == len(times) and len(times) >= 2 and abs(times[0]) < 1e-6
            valid &= all(abs((b-a)-1/30) < 2e-6 for a,b in zip(times,times[1:]))
            valid &= all(math.isfinite(x) for row in values for x in row)
            path = channel['target']['path']
            if path == 'rotation':
                max_quaternion_error = max(max_quaternion_error,
                    max(abs(sum(x*x for x in row)-1) for row in values))
                span = max(max(row[i] for row in values)-min(row[i] for row in values) for i in range(4))
                max_rotation_span = max(max_rotation_span, span)
            if path == 'scale':
                valid &= all(abs(x-1) < 1e-4 for row in values for x in row)
            if jn['nodes'][channel['target']['node']]['name'] == 'Root':
                root_span = max(root_span, max(max(row[i] for row in values)-min(row[i] for row in values)
                                              for i in range(len(values[0]))))
        valid &= (max_quaternion_error < 1e-4 and max_rotation_span > .01 and root_span < 1e-6
                  and len(sample_counts) == 1 and len(durations) == 1)
        record = {'channels': len(targets), 'by_path': dict(shape),
            'samples': sorted(sample_counts), 'duration_seconds': sorted(durations),
            'max_rotation_component_span': max_rotation_span,
            'max_quaternion_norm_error': max_quaternion_error,
            'root_channel_span': root_span, 'dense_30fps': bool(valid)}
        if bake:
            source = bake['clips'].get(name, {})
            record['bake'] = source
            valid &= (source.get('fcurves') == 200 and
                      sample_counts == {source.get('samples')} and
                      abs(next(iter(durations))-source.get('duration_seconds',-1)) < 1e-5)
        record['pass'] = bool(valid)
        report['new_clips'][name] = record
        check('new_' + name, valid)
    report['pass'] = all(assertions.values())
    report['failed_assertions'] = [k for k,v in assertions.items() if not v]
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('old')
    p.add_argument('new')
    p.add_argument('--clips', required=True)
    p.add_argument('--bake-log')
    p.add_argument('--out')
    args = p.parse_args()
    expected = list(json.loads(Path(args.clips).read_text()))
    bake = json.loads(Path(args.bake_log).read_text()) if args.bake_log else None
    report = verify(args.old, args.new, expected, bake)
    text = json.dumps(report, indent=2) + '\n'
    if args.out:
        Path(args.out).write_text(text)
    print(text)
    raise SystemExit(0 if report['pass'] else 1)


if __name__ == '__main__':
    main()
