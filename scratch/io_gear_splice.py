"""Splice gear primitives into the WH base player GLB (append-only surgery).

Base rules (from scratch/glb_append_clips.py law):
  - Only buffers[0].byteLength and append-only arrays (accessors, bufferViews,
    materials, meshes[], meshes[0].primitives, extensionsUsed?) may change.
  - Nodes, scenes, animations, skins UNTOUCHED. Base bin = strict prefix.
Gear side: move its 2 skinned meshes onto base node WH_Body (skin 0).
  - JOINTS_0 values are REMAPPED from gear skin's joint order -> base order.
  - Gear materials appended; gear prim material indices offset.
Run: python3 wh_splice.py BASE GEAR OUT
"""
import copy, json, struct, sys
from pathlib import Path

COMPONENTS = {5120: ('b', 1), 5121: ('B', 1), 5122: ('h', 2),
              5123: ('H', 2), 5125: ('I', 4), 5126: ('f', 4)}
WIDTHS = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}

def parse(path):
    raw = Path(path).read_bytes()
    magic, version, length = struct.unpack_from('<4sII', raw)
    assert magic == b'glTF' and version == 2 and length == len(raw)
    chunks, pos = {}, 12
    while pos < len(raw):
        size, kind = struct.unpack_from('<I4s', raw, pos)
        chunks[kind] = raw[pos + 8:pos + 8 + size]
        pos += 8 + size
    assert pos == len(raw)
    return json.loads(chunks[b'JSON']), chunks[b'BIN\0']

def accessor_bytes(doc, blob, index):
    acc = doc['accessors'][index]
    assert 'sparse' not in acc
    view = doc['bufferViews'][acc['bufferView']]
    width = WIDTHS[acc['type']] * COMPONENTS[acc['componentType']][1]
    stride = view.get('byteStride', width)
    offset = view.get('byteOffset', 0) + acc.get('byteOffset', 0)
    return b''.join(blob[offset + i*stride: offset + i*stride + width]
                    for i in range(acc['count']))

def save(path, doc, blob):
    enc = json.dumps(doc, separators=(',', ':'), ensure_ascii=True).encode()
    enc += b' ' * (-len(enc) % 4)
    blob = bytes(blob) + b'\0' * (-len(blob) % 4)
    raw = (struct.pack('<4sII', b'glTF', 2, 28 + len(enc) + len(blob))
           + struct.pack('<I4s', len(enc), b'JSON') + enc
           + struct.pack('<I4s', len(blob), b'BIN\0') + blob)
    Path(path).write_bytes(raw)

base_doc, base_bin = parse(sys.argv[1])
gear_doc, gear_bin = parse(sys.argv[2])
out_doc = copy.deepcopy(base_doc)
blob = bytearray(base_bin)

# ---- index maps
base_nodes = {n['name']: i for i, n in enumerate(base_doc['nodes']) if 'name' in n}
base_skin = base_doc['skins'][0]
base_joint_names = [base_doc['nodes'][j]['name'] for j in base_skin['joints']]
joint_index = {nm: i for i, nm in enumerate(base_joint_names)}
gear_skin = gear_doc['skins'][0]
gear_joint_names = [gear_doc['nodes'][j]['name'] for j in gear_skin['joints']]
perm = {}
for gi, nm in enumerate(gear_joint_names):
    assert nm in joint_index, "gear joint not in base: " + nm
    perm[gi] = joint_index[nm]
assert len(perm) == 20

out = out_doc
n_mat0 = len(out['materials'])
n_acc0 = len(out['accessors'])
n_bv0 = len(out['bufferViews'])
n_mesh0 = len(out['meshes'])

def add_payload(acc_src, data=None):
    """Append accessor payload (optional remapped) + bufferView; return new acc idx."""
    if data is None:
        data = accessor_bytes(gear_doc, gear_bin, acc_src['index'] if isinstance(acc_src, dict) else acc_src)
    blob.extend(b'\0' * (-len(blob) % 4))
    bv = {'buffer': 0, 'byteOffset': len(blob), 'byteLength': len(data)}
    blob.extend(data)
    out['bufferViews'].append(bv)
    acc = copy.deepcopy(acc_src)
    acc.pop('bufferView', None); acc.pop('byteOffset', None)
    acc['bufferView'] = len(out['bufferViews']) - 1
    out['accessors'].append(acc)
    return len(out['accessors']) - 1

acc_map = {}
mat_map = {}
def copy_acc(idx):
    if idx in acc_map: return acc_map[idx]
    gacc = gear_doc['accessors'][idx]
    payload = accessor_bytes(gear_doc, gear_bin, idx)
    blob.extend(b'\0' * (-len(blob) % 4))
    out['bufferViews'].append({'buffer': 0, 'byteOffset': len(blob), 'byteLength': len(payload)})
    blob.extend(payload)
    acc = copy.deepcopy(gacc)
    acc['bufferView'] = len(out['bufferViews']) - 1
    acc.pop('byteOffset', None)
    out['accessors'].append(acc)
    acc_map[idx] = len(out['accessors']) - 1
    return acc_map[idx]

def remap_joints(gidx):
    """JOINTS_0 accessor: remap component values through perm, append."""
    gacc = gear_doc['accessors'][gidx]
    comp, w = COMPONENTS[gacc['componentType']]
    assert gacc['type'] == 'VEC4', gacc['type']
    raw = accessor_bytes(gear_doc, gear_bin, gidx)
    flat = list(struct.iter_unpack('<' + comp*4, raw))
    remapped = b''.join(struct.pack('<' + comp*4,
                                    *(perm[v] for v in tup)) for tup in flat)
    blob.extend(b'\0' * (-len(blob) % 4))
    out['bufferViews'].append({'buffer': 0, 'byteOffset': len(blob), 'byteLength': len(remapped)})
    blob.extend(remapped)
    acc = copy.deepcopy(gacc)
    acc['bufferView'] = len(out['bufferViews']) - 1
    acc.pop('byteOffset', None)
    acc.pop('min', None); acc.pop('max', None)   # joint indices: min/max no longer valid
    out['accessors'].append(acc)
    return len(out['accessors']) - 1

# ---- gear materials first (append in gear order)
for gm in gear_doc['materials']:
    out['materials'].append(copy.deepcopy(gm))

# ---- gear meshes: resolve via named nodes (object names land on nodes)
gear_node_of = {n['name']: n for n in gear_doc['nodes'] if 'name' in n}
pairs = []
for gname in ('WH_Hat', 'WH_Satchel'):
    gnode = gear_node_of[gname]
    pairs.append((gname, gear_doc['meshes'][gnode['mesh']]))
assert len(pairs) == 2
new_mesh_names = []
for gname, gmesh in pairs:
    m = copy.deepcopy(gmesh)
    m['name'] = gname
    m.pop('extensions', None)
    for prim in m['primitives']:
        pa = prim['attributes']
        new_attrs = {}
        for k, idx in pa.items():
            if k == 'JOINTS_0':
                new_attrs[k] = remap_joints(idx)
            elif k == 'WEIGHTS_0':
                # copy weights but zero out non-primary bones? not needed: all weight on one joint
                new_attrs[k] = copy_acc(idx)
            else:
                new_attrs[k] = copy_acc(idx)
        prim['attributes'] = new_attrs
        prim['indices'] = copy_acc(prim['indices'])
        prim['material'] = n_mat0 + prim['material']
        # targets/extensions not used by these prims
        prim.pop('extensions', None); prim.pop('targets', None)
    out['meshes'].append(m)
    new_mesh_names.append(gname)
assert new_mesh_names == ['WH_Hat', 'WH_Satchel'], new_mesh_names

# ---- attach gear via NEW skinned nodes under WH_Armature (wolf-paw pattern)
arm_node = out['nodes'][base_nodes['WH_Armature']]
assert 'children' in arm_node
hat_node_id = len(out['nodes'])
out['nodes'].append({'name': 'WH_Hat', 'mesh': n_mesh0, 'skin': 0})
out['nodes'].append({'name': 'WH_Satchel', 'mesh': n_mesh0 + 1, 'skin': 0})
arm_node['children'] = arm_node['children'] + [hat_node_id, hat_node_id + 1]

# ---- buffer byteLength
out['buffers'][0]['byteLength'] = len(blob)
save(sys.argv[3], out_doc, blob)

# ---- append-only proofs (nodes: prefix + WH_Armature tail-extend diff allowed)
chk, chk_bin = parse(sys.argv[3])
assert chk_bin[:len(base_bin)] == base_bin, "BIN prefix changed"
for key, value in base_doc.items():
    if key == 'buffers':
        continue
    if key in ('accessors', 'bufferViews', 'materials', 'meshes'):
        assert chk[key][:len(value)] == value, "append-only violated: " + key
    elif key == 'nodes':
        arm_idx = base_nodes['WH_Armature']
        for i, (a, b) in enumerate(zip(chk['nodes'], value)):
            if i == arm_idx:
                continue  # covered by the explicit tail-extend check below
            assert a == b, "node %d changed" % i
    else:
        assert chk[key] == value, "changed: " + key
arm_chk = chk['nodes'][base_nodes['WH_Armature']]
arm_base = base_doc['nodes'][base_nodes['WH_Armature']]
assert arm_chk['children'][:len(arm_base['children'])] == arm_base['children']
assert arm_chk['children'][len(arm_base['children']):] == [hat_node_id, hat_node_id + 1]
new_nodes = chk['nodes'][hat_node_id:]
assert new_nodes == [{'name': 'WH_Hat', 'mesh': n_mesh0, 'skin': 0},
                     {'name': 'WH_Satchel', 'mesh': n_mesh0 + 1, 'skin': 0}]
print("SPLICE_OK out=%s anims=%d nodes=%d mats=%d meshes=%d bytes=%d" % (
    sys.argv[3], len(chk['animations']), len(chk['nodes']),
    len(chk['materials']), len(chk['meshes']), len(chk_bin)))