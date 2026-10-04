"""Exercise opposite batch orders; both clips must bake and remain byte-identical."""
from pathlib import Path
import json
import subprocess
import tempfile
from glb_append_clips import parse, accessor_bytes

ROOT = Path(__file__).resolve().parents[1]
BLENDER = '/opt/blender-4.5.4-linux-x64/blender'
manifest = json.loads((ROOT/'scratch/mixamo_bandit.json').read_text())
names = ['WH_Idle_Melee', 'WH_Walk_Melee']
results = []
with tempfile.TemporaryDirectory(prefix='wh-order-') as tmp:
    tmp = Path(tmp)
    for order in (names, names[::-1]):
        index = len(results)
        clips = tmp/f'{index}.json'
        clips.write_text(json.dumps({n: manifest[n] for n in order}))
        out = tmp/f'{index}.mixamo.glb'
        log = tmp/f'{index}-bake.json'
        run = subprocess.run([BLENDER, '-b', '--factory-startup', '--python-exit-code', '1',
            '--python', str(ROOT/'scratch/mixamo_retarget.py'), '--',
            str(ROOT/'art-direction/3d/assets/races_regen/rigged/orc-male-warrior.rigged.glb'),
            str(out), '--clips', str(clips), '--log', str(log)],
            cwd=ROOT, text=True, capture_output=True, check=True)
        doc, blob = parse(out)
        tracks = {}
        for name in names:
            anim = next(a for a in doc['animations'] if a['name'] == name)
            tracks[name] = [accessor_bytes(doc, blob, s[field])
                for s in anim['samplers'] for field in ('input', 'output')]
        results.append((tracks, json.loads(log.read_text())))
report = {'orders': [names, names[::-1]], 'clips': {}}
for name in names:
    curves = [r[1]['clips'][name]['fcurves'] for r in results]
    identical = results[0][0][name] == results[1][0][name]
    report['clips'][name] = {'fcurves_by_order': curves, 'ordered_sampler_bytes_identical': identical}
    assert curves == [200, 200] and identical
report['pass'] = True
path = ROOT/'scratch/mixamo-fbx/reports/order-regression.json'
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
