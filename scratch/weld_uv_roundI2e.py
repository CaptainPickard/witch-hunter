#!/usr/bin/env python3
"""Round I2e: zero-normal repair on reach a/b/c (degenerate-face verts got
zero normals from I2d's accumulation): recompute from their good faces."""
import struct, json
from pathlib import Path
import numpy as np
import trimesh

ROOT = Path('/workspace/witch-hunter')
base = ROOT / 'art-direction/3d/assets/biome_library'

for rel in ['wh-reachtree-a-pixelated.glb', 'wh-reachtree-b-pixelated.glb',
            'wh-reachtree-c-pixelated.glb']:
    p = base / rel
    d = bytearray(p.read_bytes())
    jslen, = struct.unpack_from('<I', d, 12)
    g = json.loads(d[20:20+jslen].decode())
    json_end = 20 + jslen
    blen, = struct.unpack_from('<I', d, json_end)
    bin_data = bytearray(d[json_end+8:])
    prim = g['meshes'][0]['primitives'][0]

    acc = g['accessors'][prim['attributes']['NORMAL']]
    bv = g['bufferViews'][acc['bufferView']]
    noff, n = bv['byteOffset'], acc['count']
    N = np.frombuffer(bytes(bin_data), dtype='<f4', count=n*3, offset=noff).reshape(n, 3).copy()

    accP = g['accessors'][prim['attributes']['POSITION']]
    bvP = g['bufferViews'][accP['bufferView']]
    P = np.frombuffer(bytes(bin_data), dtype='<f4', count=accP['count']*3,
                      offset=bvP['byteOffset']).reshape(accP['count'], 3)
    accI = g['accessors'][prim['indices']]
    bvI = g['bufferViews'][accI['bufferView']]
    IDX = np.frombuffer(bytes(bin_data), dtype='<u4', count=accI['count'],
                        offset=bvI['byteOffset'])
    F = IDX.reshape(-1, 3)
    tri = P[F]
    fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    ln = np.linalg.norm(fn, axis=1)
    fn_ok = fn / np.maximum(ln, 1e-12)[:, None]
    good = ln > 1e-9

    zeros = np.abs(np.linalg.norm(N, axis=1) - 1) > 0.5
    fixed = 0
    for vi in np.where(zeros)[0]:
        fs = np.where((F == vi).any(axis=1) & good)[0]
        if len(fs):
            nv = fn_ok[fs].mean(axis=0)
            lg = np.linalg.norm(nv)
            if lg > 1e-9:
                N[vi] = nv / lg
                fixed += 1
    bin_data[noff:noff + n*12] = N.astype('<f4').tobytes()

    js = json.dumps(g, separators=(',', ':')).encode()
    js = js + b' ' * ((-len(js)) % 4)
    jchunk = struct.pack('<I', len(js)) + b'JSON' + js
    bchunk = struct.pack('<I', len(bin_data)) + b'BIN\x00' + bytes(bin_data)
    total = 12 + len(jchunk) + len(bchunk)
    head = b'glTF' + struct.pack('<II', 2, total)
    p.write_bytes(head + jchunk + bchunk)

    d3 = p.read_bytes()
    jl3, = struct.unpack_from('<I', d3, 12)
    g3 = json.loads(d3[20:20+jl3].decode())
    prim3 = g3['meshes'][0]['primitives'][0]
    acc3 = g3['accessors'][prim3['attributes']['NORMAL']]
    bv3 = g3['bufferViews'][acc3['bufferView']]
    N3 = np.frombuffer(d3, dtype='<f4', count=acc3['count']*3,
                       offset=20+jl3+8+bv3['byteOffset']).reshape(acc3['count'], 3)
    print(rel, 'zero-fixed', fixed, 'unit err', round(float(np.abs(np.linalg.norm(N3, axis=1) - 1).max()), 6))
print('I2E DONE')