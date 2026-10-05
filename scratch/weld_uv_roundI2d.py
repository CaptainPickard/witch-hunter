#!/usr/bin/env python3
"""Round I2d: inject NORMAL (smooth-by-position) into reach a/b/c GLBs with the
CORRECT chunk types + alignment, and flip chunk type to b'JSON' on all outputs.
One clean writer, verified by reload after each write."""
import json, struct
from pathlib import Path
import numpy as np
import trimesh

ROOT = Path('/workspace/witch-hunter')
base = ROOT / 'art-direction/3d/assets/biome_library'

def rewrite(path, g, js_pad_align=True):
    js = json.dumps(g, separators=(',', ':')).encode()
    js = js + b' ' * ((-len(js)) % 4)
    jchunk = struct.pack('<I', len(js)) + b'JSON' + js
    bchunk = struct.pack('<I', g['buffers'][0]['byteLength']) + b'BIN\x00' + BIN_DATA[1]
    raise SystemExit('placeholder')

def inject(path):
    d = bytearray(path.read_bytes())
    jslen, = struct.unpack_from('<I', d, 12)
    g = json.loads(bytes(d[20:20+jslen]).decode())
    json_end = 20 + jslen
    blen, = struct.unpack_from('<I', d, json_end)
    bin_data = bytes(d[json_end+8:])
    prim = g['meshes'][0]['primitives'][0]
    if 'NORMAL' in prim['attributes']:
        print(path.name, 'already has NORMAL'); return
    # read positions + indices
    def vals(acc_i, expect_w):
        acc = g['accessors'][acc_i]
        bv = g['bufferViews'][acc['bufferView']]
        off = bv['byteOffset'] + acc.get('byteOffset', 0)
        comp = {5126: '<f4', 5125: '<u4', 5123: '<u2'}[acc['componentType']]
        w = {'VEC3': 3, 'SCALAR': 1, 'VEC2': 2}[acc['type']]
        assert w == expect_w
        return np.frombuffer(bin_data, dtype=comp, count=acc['count']*w, offset=off).reshape(acc['count'], w)
    P = vals(prim['attributes']['POSITION'], 3).astype(np.float64)
    IDX = vals(prim['indices'], 1).ravel().astype(np.int64) if 'indices' in prim else np.arange(len(P))
    tri = P[IDX].reshape(-1, 3, 3)
    fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12)
    NV = np.zeros_like(P)
    idxm = IDX.reshape(-1, 3)
    for k in range(3):
        np.add.at(NV, idxm[:, k], fn)
    NV /= np.maximum(np.linalg.norm(NV, axis=1, keepdims=True), 1e-12)
    payload = NV.astype('<f4').tobytes()
    bv_off = len(bin_data)
    pad = (-bv_off) % 4
    bin_data = bin_data + b'\x00' * pad + payload
    bv_off_padded = bv_off + pad
    bvidx = len(g['bufferViews'])
    g['bufferViews'].append({'buffer': 0, 'byteOffset': bv_off_padded, 'byteLength': len(payload)})
    aid = len(g['accessors'])
    g['accessors'].append({'bufferView': bvidx, 'componentType': 5126, 'count': len(NV), 'type': 'VEC3'})
    prim['attributes']['NORMAL'] = aid
    g['buffers'][0]['byteLength'] = len(bin_data)
    js = json.dumps(g, separators=(',', ':')).encode()
    js = js + b' ' * ((-len(js)) % 4)
    jchunk = struct.pack('<I', len(js)) + b'JSON' + js
    bchunk = struct.pack('<I', len(bin_data)) + b'BIN\x00' + bin_data
    total = 12 + len(jchunk) + len(bchunk)
    head = b'glTF' + struct.pack('<II', 2, total)
    path.write_bytes(head + jchunk + bchunk)
    # verify
    m2 = trimesh.load(path, force='mesh', process=False)
    d3 = path.read_bytes()
    jl3, = struct.unpack_from('<I', d3, 12)
    g3 = json.loads(d3[20:20+jl3].decode())
    print(path.name, json.dumps({'verts': len(m2.vertices), 'faces': len(m2.faces),
        'normal': 'NORMAL' in g3['meshes'][0]['primitives'][0]['attributes'],
        'bytes': len(d3)}))

for rel in ['wh-reachtree-a-pixelated.glb', 'wh-reachtree-b-pixelated.glb',
            'wh-reachtree-c-pixelated.glb', 'wh-bramble-pixelated.glb']:
    inject(base / rel)
print('I2D DONE')