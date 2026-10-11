"""MAGICLASS M2: derive WH_Mag_Cast1H_L = sagittal mirror of WH_Mag_Cast1H and
byte-splice APPEND it to combat-sword.glb (in-place law, current bytes).

Mirror across the x=0 plane (character faces +z, right = -x):
  - L_* <-> R_* node tracks swapped (center bones keep their own node)
  - rotation (x, y, z, w) -> (x, -y, -z, w)   (reflect S=diag(-1,1,1): S R S)
  - translation (x, y, z) -> (-x, y, z) for center bones (Hips/Root/...);
    paired limb bones keep their OWN translation track (every limb track in
    Cast1H is constant == rest, so own == x-negated other within the rig's
    few-mm L/R asymmetry; swapping would move joints off the skin bind)
  - scale tracks swapped as-is (mirror invariant)
  - same input times (one fresh copy), LINEAR, 60 channels dense.
Usage: python3 scratch/mirror_cast1h.py   (from repo root)
"""
import copy, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from glb_append_clips import parse, save, accessor_bytes, accessor_values
import struct

GLB = Path('art-direction/3d/assets/races_regen/rigged/human-hunter-male.combat-sword.glb')
PRISTINE = Path('/tmp/magiclass_pristine.glb')
SRC, NEW = 'WH_Mag_Cast1H', 'WH_Mag_Cast1H_L'


def other(name):
    if name.startswith('L_'):
        return 'R_' + name[2:]
    if name.startswith('R_'):
        return 'L_' + name[2:]
    return name


def main():
    if not PRISTINE.exists():
        shutil.copyfile(GLB, PRISTINE)
    base, base_bin = parse(PRISTINE)
    assert GLB.read_bytes() == PRISTINE.read_bytes(), 'GLB changed since pristine copy'
    assert NEW not in {a['name'] for a in base['animations']}
    assert len(base['animations']) == 42
    out = copy.deepcopy(base)
    blob = bytearray(base_bin)
    names = [n.get('name') for n in base['nodes']]
    idx = {n: i for i, n in enumerate(names)}
    src = next(a for a in base['animations'] if a['name'] == SRC)
    track = {(names[c['target']['node']], c['target']['path']): src['samplers'][c['sampler']]
             for c in src['channels']}

    def put(acc_tmpl, payload):
        blob.extend(b'\0' * (-len(blob) % 4))
        out['bufferViews'].append({'buffer': 0, 'byteOffset': len(blob), 'byteLength': len(payload)})
        blob.extend(payload)
        acc = copy.deepcopy(acc_tmpl)
        acc['bufferView'] = len(out['bufferViews']) - 1
        acc.pop('byteOffset', None)
        out['accessors'].append(acc)
        return len(out['accessors']) - 1

    inputs = {s['input'] for s in src['samplers']}
    assert len(inputs) == 1, inputs
    in_old = inputs.pop()
    in_new = put(base['accessors'][in_old], accessor_bytes(base, base_bin, in_old))

    anim = {'name': NEW, 'channels': [], 'samplers': []}
    for c in src['channels']:
        dst = names[c['target']['node']]
        path = c['target']['path']
        paired = other(dst) != dst
        from_node = dst if (path == 'translation' and paired) else other(dst)
        s = track[(from_node, path)]
        acc = base['accessors'][s['output']]
        vals = accessor_values(base, base_bin, s['output'])
        if path == 'rotation':
            vals = [(x, -y, -z, w) for x, y, z, w in vals]
        elif path == 'translation' and not paired:
            vals = [(-x, y, z) for x, y, z in vals]
        payload = b''.join(struct.pack('<' + 'f' * len(v), *v) for v in vals)
        tmpl = copy.deepcopy(acc)
        if 'min' in tmpl:
            tmpl['min'] = [min(v[k] for v in vals) for k in range(len(vals[0]))]
            tmpl['max'] = [max(v[k] for v in vals) for k in range(len(vals[0]))]
        o = put(tmpl, payload)
        anim['samplers'].append({'input': in_new, 'output': o,
                                 'interpolation': s.get('interpolation', 'LINEAR')})
        anim['channels'].append({'sampler': len(anim['samplers']) - 1,
                                 'target': {'node': idx[dst], 'path': path}})
    out['animations'].append(anim)
    out['buffers'][0]['byteLength'] = len(blob)
    tmp = GLB.with_suffix('.glb.tmp')
    save(tmp, out, blob)
    check, check_bin = parse(tmp)
    assert check_bin[:len(base_bin)] == base_bin
    for key, value in base.items():
        if key == 'buffers':
            continue
        assert (check[key][:len(value)] == value if key in
                ('animations', 'accessors', 'bufferViews') else check[key] == value), key
    tmp.replace(GLB)
    print('appended %s: %d channels, animations %d, bytes %d -> %d' % (
        NEW, len(anim['channels']), len(check['animations']),
        PRISTINE.stat().st_size, GLB.stat().st_size))


if __name__ == '__main__':
    main()
