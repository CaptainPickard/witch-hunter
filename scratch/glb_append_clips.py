"""Append only new GLB animations; never re-export the canonical asset.

Dense accessor reader honors both the BIN chunk header and byteStride.
Only buffers[0].byteLength and append-only arrays may change in the base JSON.
"""
import copy
import json
import struct
from pathlib import Path

COMPONENTS = {5120: ('b', 1), 5121: ('B', 1), 5122: ('h', 2),
              5123: ('H', 2), 5125: ('I', 4), 5126: ('f', 4)}
WIDTHS = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}


def parse(path):
    raw = Path(path).read_bytes()
    magic, version, length = struct.unpack_from('<4sII', raw)
    assert magic == b'glTF' and version == 2 and length == len(raw)
    chunks = {}
    pos = 12
    while pos < len(raw):
        size, kind = struct.unpack_from('<I4s', raw, pos)
        chunks[kind] = raw[pos + 8:pos + 8 + size]
        pos += 8 + size
    assert pos == len(raw)
    doc = json.loads(chunks[b'JSON'])
    assert len(doc['buffers']) == 1
    return doc, chunks[b'BIN\0']


def accessor_bytes(doc, blob, index):
    acc = doc['accessors'][index]
    assert 'sparse' not in acc
    view = doc['bufferViews'][acc['bufferView']]
    assert view.get('buffer', 0) == 0
    width = WIDTHS[acc['type']] * COMPONENTS[acc['componentType']][1]
    stride = view.get('byteStride', width)
    offset = view.get('byteOffset', 0) + acc.get('byteOffset', 0)
    end = offset + (acc['count'] - 1) * stride + width
    assert end <= view.get('byteOffset', 0) + view['byteLength'] <= len(blob)
    return b''.join(blob[offset + i * stride:offset + i * stride + width]
                    for i in range(acc['count']))


def accessor_values(doc, blob, index):
    acc = doc['accessors'][index]
    fmt = '<' + COMPONENTS[acc['componentType']][0] * WIDTHS[acc['type']]
    return list(struct.iter_unpack(fmt, accessor_bytes(doc, blob, index)))


def save(path, doc, blob):
    encoded = json.dumps(doc, separators=(',', ':'), ensure_ascii=True).encode()
    encoded += b' ' * (-len(encoded) % 4)
    blob = bytes(blob) + b'\0' * (-len(blob) % 4)
    raw = (struct.pack('<4sII', b'glTF', 2, 28 + len(encoded) + len(blob))
           + struct.pack('<I4s', len(encoded), b'JSON') + encoded
           + struct.pack('<I4s', len(blob), b'BIN\0') + blob)
    Path(path).write_bytes(raw)


def append_clips(base_path, source_path, out_path, names):
    assert Path(base_path).resolve() != Path(out_path).resolve()
    base, base_bin = parse(base_path)
    src, src_bin = parse(source_path)
    out = copy.deepcopy(base)
    blob = bytearray(base_bin)
    nodes = {n['name']: i for i, n in enumerate(base['nodes']) if 'name' in n}
    old_names = {a['name'] for a in base['animations']}
    assert len(names) == len(set(names)) and not old_names.intersection(names)
    source_anims = {a['name']: a for a in src['animations']}
    accessor_map = {}
    for name in names:
        anim = copy.deepcopy(source_anims[name])
        for channel in anim['channels']:
            old_node = src['nodes'][channel['target']['node']]
            new_index = nodes[old_node['name']]
            new_node = base['nodes'][new_index]
            # Imported/exported bone local frames must match the base skeleton.
            for field, default in [('translation', [0, 0, 0]),
                                   ('rotation', [0, 0, 0, 1]), ('scale', [1, 1, 1])]:
                left, right = old_node.get(field, default), new_node.get(field, default)
                delta = max(abs(x-y) for x,y in zip(left, right))
                if field == 'rotation':
                    delta = min(delta, max(abs(x+y) for x,y in zip(left,right)))
                assert delta < 1e-5, (old_node['name'], field, delta)
            channel['target']['node'] = new_index
        for sampler in anim['samplers']:
            for field in ('input', 'output'):
                idx = sampler[field]
                if idx not in accessor_map:
                    acc = copy.deepcopy(src['accessors'][idx])
                    payload = accessor_bytes(src, src_bin, idx)
                    blob.extend(b'\0' * (-len(blob) % 4))
                    view_id = len(out['bufferViews'])
                    out['bufferViews'].append({'buffer': 0, 'byteOffset': len(blob),
                                               'byteLength': len(payload)})
                    blob.extend(payload)
                    acc['bufferView'] = view_id
                    acc.pop('byteOffset', None)
                    accessor_map[idx] = len(out['accessors'])
                    out['accessors'].append(acc)
                sampler[field] = accessor_map[idx]
        out['animations'].append(anim)
    out['buffers'][0]['byteLength'] = len(blob)
    save(out_path, out, blob)
    check, check_bin = parse(out_path)
    assert check_bin[:len(base_bin)] == base_bin
    for key, value in base.items():
        if key == 'buffers':
            continue
        assert (check[key][:len(value)] == value if key in
                ('animations', 'accessors', 'bufferViews') else check[key] == value), key
    return out
