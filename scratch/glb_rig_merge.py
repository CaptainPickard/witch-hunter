"""Merge a Blender-authored rig (skin + armature nodes + clips) onto the RAW
wolf GLB, byte-surgically -- the scratch/glb_append_clips.py pattern applied to
a first rig. Never re-exports the raw mesh/texture.

Why not ship the Blender export directly: its mesh is NOT the raw's (Blender
re-splits loops on export: 13087 vertices vs the raw 13085), so the mesh gate
(bitwise-equal to raw) can only hold if the raw bytes are kept.

Contract (asserted at the end, like append_clips):
  - raw BIN is a byte-identical PREFIX of the output BIN;
  - every raw JSON value is preserved: arrays are prefix-equal, objects are
    supersets. The ONLY additions: primitive JOINTS_0/WEIGHTS_0, nodes[0].skin,
    the armature nodes, skins[0], animations, scenes[0].nodes += armature,
    appended accessors/bufferViews, buffers[0].byteLength.
  - JOINTS_0/WEIGHTS_0 are the Blender export's, mapped onto the raw vertex
    order by exact POSITION bytes (Blender's (x,-z,y) round trip is exact);
    every exported vertex sharing a position must carry identical skin bytes.
  - channel/joint node indices remapped BY NAME, never by index.

    python3 scratch/glb_rig_merge.py RAW.glb BLENDER_EXPORT.glb OUT.glb
"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from glb_append_clips import parse, accessor_bytes, save, COMPONENTS, WIDTHS  # noqa: E402


def superset(base, out, path="$"):
    """Every base value preserved in out (arrays prefix-wise, dicts key-wise)."""
    if isinstance(base, dict):
        assert isinstance(out, dict), path
        for k, v in base.items():
            assert k in out, f"{path}.{k} dropped"
            superset(v, out[k], f"{path}.{k}")
    elif isinstance(base, list):
        assert isinstance(out, list) and len(out) >= len(base), path
        for i, v in enumerate(base):
            superset(v, out[i], f"{path}[{i}]")
    else:
        assert base == out, f"{path}: {base!r} != {out!r}"


def merge_rig(raw_path, src_path, out_path):
    assert Path(raw_path).resolve() != Path(out_path).resolve()
    base, base_bin = parse(raw_path)
    src, src_bin = parse(src_path)
    assert 'skins' not in base and 'animations' not in base, "raw already rigged?"
    out = copy.deepcopy(base)
    blob = bytearray(base_bin)
    acc_map = {}

    def add_accessor(idx, payload=None, target=None):
        if payload is None and idx in acc_map:
            return acc_map[idx]
        acc = copy.deepcopy(src['accessors'][idx])
        data = accessor_bytes(src, src_bin, idx) if payload is None else payload
        blob.extend(b'\0' * (-len(blob) % 4))
        view = {'buffer': 0, 'byteOffset': len(blob), 'byteLength': len(data)}
        if target:
            view['target'] = target
        out['bufferViews'].append(view)
        blob.extend(data)
        acc['bufferView'] = len(out['bufferViews']) - 1
        acc.pop('byteOffset', None)
        out['accessors'].append(acc)
        if payload is None:
            acc_map[idx] = len(out['accessors']) - 1
        return len(out['accessors']) - 1

    # ---- skin attributes, mapped to the raw vertex order by position bytes
    rprim = base['meshes'][0]['primitives'][0]
    sprim = [p for m in src['meshes'] for p in m['primitives']]
    assert len(base['meshes']) == 1 and len(base['meshes'][0]['primitives']) == 1 and len(sprim) == 1
    sprim = sprim[0]
    rpos = accessor_bytes(base, base_bin, rprim['attributes']['POSITION'])
    spos = accessor_bytes(src, src_bin, sprim['attributes']['POSITION'])
    sj = accessor_bytes(src, src_bin, sprim['attributes']['JOINTS_0'])
    sw = accessor_bytes(src, src_bin, sprim['attributes']['WEIGHTS_0'])
    jw = WIDTHS['VEC4'] * COMPONENTS[src['accessors'][sprim['attributes']['JOINTS_0']]['componentType']][1]
    ww = 16
    by_pos = {}
    for i in range(len(spos) // 12):
        key = spos[i * 12:i * 12 + 12]
        skin = (sj[i * jw:i * jw + jw], sw[i * ww:i * ww + ww])
        if key in by_pos:
            assert by_pos[key] == skin, f"exported vertex {i}: coincident vertices disagree on skin bytes"
        by_pos[key] = skin
    nraw = len(rpos) // 12
    joints = bytearray()
    weights = bytearray()
    for i in range(nraw):
        j, w = by_pos[rpos[i * 12:i * 12 + 12]]       # KeyError = a raw vertex Blender lost
        joints += j
        weights += w
    ja = add_accessor(sprim['attributes']['JOINTS_0'], bytes(joints), 34962)
    wa = add_accessor(sprim['attributes']['WEIGHTS_0'], bytes(weights), 34962)
    out['accessors'][ja]['count'] = nraw
    out['accessors'][wa]['count'] = nraw
    oprim = out['meshes'][0]['primitives'][0]
    oprim['attributes']['JOINTS_0'] = ja
    oprim['attributes']['WEIGHTS_0'] = wa

    # ---- armature nodes (everything but the exported mesh node)
    smesh = [i for i, n in enumerate(src['nodes']) if 'mesh' in n]
    assert len(smesh) == 1
    smesh = smesh[0]
    node_map = {smesh: 0}                                 # raw node 0 = the mesh
    for i, n in enumerate(src['nodes']):
        if i != smesh:
            node_map[i] = len(out['nodes'])
            out['nodes'].append(None)
    for i, n in enumerate(src['nodes']):
        if i == smesh:
            continue
        m = copy.deepcopy(n)
        if 'children' in m:
            m['children'] = [node_map[c] for c in m['children'] if c != smesh]
            if not m['children']:
                del m['children']
        assert 'mesh' not in m and 'skin' not in m
        out['nodes'][node_map[i]] = m
    names = [n.get('name') for n in out['nodes']]
    assert len(set(n for n in names if n)) == len([n for n in names if n]), "node names must be unique"
    by_name = {n: i for i, n in enumerate(names) if n}
    sroots = [i for i in src['scenes'][src.get('scene', 0)]['nodes']]
    for r in sroots:
        assert r != smesh
        out['scenes'][out.get('scene', 0)]['nodes'].append(node_map[r])

    # ---- skin
    assert len(src['skins']) == 1
    sk = copy.deepcopy(src['skins'][0])
    sk['joints'] = [by_name[src['nodes'][j]['name']] for j in sk['joints']]
    if 'skeleton' in sk:
        sk['skeleton'] = by_name[src['nodes'][sk['skeleton']]['name']]
    sk['inverseBindMatrices'] = add_accessor(sk['inverseBindMatrices'])
    out['skins'] = [sk]
    out['nodes'][0]['skin'] = 0

    # ---- animations (append_clips: accessors appended, targets BY NAME)
    out['animations'] = []
    for a in src['animations']:
        anim = copy.deepcopy(a)
        for c in anim['channels']:
            c['target']['node'] = by_name[src['nodes'][c['target']['node']]['name']]
        for s in anim['samplers']:
            s['input'] = add_accessor(s['input'])
            s['output'] = add_accessor(s['output'])
        out['animations'].append(anim)

    out['buffers'][0]['byteLength'] = len(blob)
    save(out_path, out, blob)
    check, check_bin = parse(out_path)
    assert check_bin[:len(base_bin)] == base_bin, "raw BIN is not a byte-identical prefix"
    expect = copy.deepcopy(base)
    expect['buffers'][0]['byteLength'] = check['buffers'][0]['byteLength']   # the one allowed edit
    superset(expect, check)
    return check


if __name__ == '__main__':
    doc = merge_rig(*sys.argv[1:4])
    print(f"merged -> {sys.argv[3]} ({Path(sys.argv[3]).stat().st_size} bytes): "
          f"{len(doc['skins'][0]['joints'])} joints, {len(doc['animations'])} clips, "
          f"{len(doc['nodes'])} nodes; raw BIN prefix + JSON superset OK")
