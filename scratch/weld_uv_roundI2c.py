#!/usr/bin/env python3
"""Round I2c: compute SMOOTH-BY-POSITION vertex normals myself and inject them
into the welded GLBs with CORRECT buffer math (single source of truth: find the
BIN chunk header via the JSON chunk length; append the NORMAL buffer view +
accessor; rewrite both chunk lengths + total length; re-serialize JSON padded
to 4 bytes). Deterministic. Verify by re-loading."""
import json, struct
from collections import defaultdict
from pathlib import Path
import numpy as np
import trimesh

ROOT = Path('/workspace/witch-hunter')

JOBS = [
    'art-direction/3d/assets/biome_library/wh-bramble-pixelated.glb',
    'art-direction/3d/assets/biome_library/wh-reachtree-a-pixelated.glb',
    'art-direction/3d/assets/biome_library/wh-reachtree-b-pixelated.glb',
    'art-direction/3d/assets/biome_library/wh-reachtree-c-pixelated.glb',
]

for rel in JOBS:
    p = ROOT / rel
    trimesh_mesh = trimesh.load(p, force='mesh', process=False)
    F = np.asarray(trimesh_mesh.faces)
    V = np.asarray(trimesh_mesh.vertices)
    tri = V[F]
    fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12)
    NV = np.zeros_like(V)
    for k in range(3):
        np.add.at(NV, F[:, k], fn)
    NV /= np.maximum(np.linalg.norm(NV, axis=1, keepdims=True), 1e-12)

    d = bytearray(p.read_bytes())
    jl, = struct.unpack_from('<I', d, 12)          # JSON chunk length
    bin_head = 20 + jl                              # 8-byte BIN chunk header addr
    bin_len, = struct.unpack_from('<I', d, bin_head)
    bin_start = bin_head + 8
    jl_chunk = d[20:20+jl]
    g = json.loads(bytes(jl_chunk))

    payload = NV.astype('<f4').tobytes()
    # bufferView offset must be 4-aligned within the buffer
    pad = (-len(d)) % 4
    d.extend(b'\x00' * pad)
    bv_off = len(d) - bin_start
    d.extend(payload)

    bvidx = len(g['bufferViews'])
    g['bufferViews'].append({'buffer': 0, 'byteOffset': bv_off, 'byteLength': len(payload)})
    aid = len(g['accessors'])
    g['accessors'].append({'bufferView': bvidx, 'componentType': 5126,
                           'count': len(NV), 'type': 'VEC3'})
    g['meshes'][0]['primitives'][0]['attributes']['NORMAL'] = aid

    new_bin_len = len(d) - bin_start
    g['buffers'][0]['byteLength'] = new_bin_len

    js = json.dumps(g, separators=(',', ':')).encode()
    js_pad = (-len(js)) % 4
    js += b' ' * js_pad
    jchunk = struct.pack('<I', len(js)) + b'UTF8' + js
    bchunk = struct.pack('<I', new_bin_len) + b'BIN\x00' + bytes(d[bin_start:])
    total = 12 + len(jchunk) + len(bchunk)
    head = b'glTF' + struct.pack('<III', 2, total, len(jchunk))
    p.write_bytes(head + jchunk + bchunk)

    # verify: reload
    m2 = trimesh.load(p, force='mesh', process=False)
    d2 = p.read_bytes()
    jl2, = struct.unpack_from('<I', d2, 12)
    g2 = json.loads(d2[20:20+jl2])
    ok = 'NORMAL' in g2['meshes'][0]['primitives'][0]['attributes']
    print(rel.split('/')[-1], json.dumps({'verts': len(m2.vertices), 'faces': len(m2.faces),
        'normal_attr': ok, 'bytes': len(d2), 'verts_match': len(m2.vertices) == len(NV)}))
print('I2C DONE')