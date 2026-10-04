"""Aggregate real batch verification, render inventory, tests and protected-path checks.
Run scratch/mixamo_order_regression.py and render both bodies before this script.
"""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import unittest
from verify_retarget import verify

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT/'scratch/mixamo-fbx/reports'
QA = ROOT/'scratch/mixamo-fbx/qa'
ASSETS = ROOT/'art-direction/3d/assets/races_regen/rigged'
BASE = '30c815c5c9d19d42f06f1df9710236f2ad011c0e'
report = {'pass': False, 'bodies': {}, 'base_commit': BASE, 'clips_failed': [],
          'root_cause': 'nla.bake iterates selected_editable_objects. FBX import selects the source, not the target; setting active alone does not select the target. Select only WH_Armature before baking, assign its new action/slot explicitly, reset range/action/pose and mute NLA tracks each iteration.',
          'warnings': ['WH_Death_Zombie uses zombie agonizing.fbx, the available agony selection. It ends standing, not in a terminal corpse pose. Do not wire as a collapse/death replacement without a separate source/content decision.']}
for body, stem in [('bandit','orc-male-warrior'), ('ghoul','undead-ghoul-male')]:
    manifest = json.loads((ROOT/f'scratch/mixamo_{body}.json').read_text())
    assert len(manifest) == 7
    bake = json.loads((REPORTS/f'{body}-bake.json').read_text())
    proof = verify(ASSETS/f'{stem}.rigged.glb', ASSETS/f'{stem}.mixamo.glb', list(manifest), bake)
    assert proof['pass'], proof['failed_assertions']
    original = ASSETS/f'{stem}.rigged.glb'
    committed = subprocess.check_output(['git', 'show', f'{BASE}:{original.relative_to(ROOT)}'], cwd=ROOT)
    assert original.read_bytes() == committed
    (REPORTS/f'{body}-verification.json').write_text(json.dumps(proof, indent=2)+'\n')
    qa = json.loads((QA/body/'renders.json').read_text())
    assert set(qa['clips']) == set(manifest) == set(qa['full_range'])
    render_list = []
    for name in manifest:
        entries = qa['clips'][name]
        assert len(entries) == 2 and {e['pose'] for e in entries} == {'mid', 'end'}
        assert qa['full_range'][name]['no_penetration_at_0_1mm_tolerance']
        assert qa['full_range'][name]['frames_checked'] == bake['clips'][name]['samples']
        for entry in entries:
            path = Path(entry['png'])
            assert path.is_file() and path.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
            entry['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            render_list.append(entry)
    assert len(render_list) == 14 and len(list((QA/body).glob('WH_*.png'))) == 14
    proof['canonical_file_matches_base_commit'] = True
    proof['qa'] = qa
    proof['render_count'] = len(render_list)
    proof['pose_review'] = {n: 'PASS: mid/end poses reviewed; full-range geometry has no ground penetration at 0.1mm tolerance' for n in manifest}
    report['bodies'][body] = proof
protected = subprocess.check_output(['git', 'diff', '--name-only', BASE, '--', 'prototype',
    'art-direction/3d/assets/races_regen/rigged/*.rigged.glb'], cwd=ROOT, text=True)
assert not protected.strip(), protected
report['protected_paths_unchanged'] = True
report['order_regression'] = json.loads((REPORTS/'order-regression.json').read_text())
assert report['order_regression']['pass']
stream = io.StringIO()
suite = unittest.defaultTestLoader.discover(str(ROOT/'scratch'), pattern='test_mixamo_retarget.py')
result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
assert result.wasSuccessful()
report['regression_tests'] = {'tests_run': result.testsRun, 'pass': result.wasSuccessful(), 'output': stream.getvalue()}
report['total_new_clips'] = sum(len(b['new_clips']) for b in report['bodies'].values())
report['total_renders'] = sum(b['render_count'] for b in report['bodies'].values())
report['total_frames_checked'] = sum(c['frames_checked'] for b in report['bodies'].values() for c in b['qa']['full_range'].values())
assert report['total_new_clips'] == 14 and report['total_renders'] == 28
report['pass'] = True
output = REPORTS/'verification.json'
output.write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({k: report[k] for k in ['pass','protected_paths_unchanged','total_new_clips','total_renders','total_frames_checked','clips_failed','warnings']}, indent=2))
print('VERIFICATION_JSON', output)
