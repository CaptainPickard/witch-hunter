#!/usr/bin/env python3
"""Position-weld test: are the single-tri components spatially separated?
Union-find over quantized vertex POSITIONS (not indices). If pieces >> position
components, vertices match exactly (crack-free) -> defect is normals/shading.
If position components ~= piece count, geometry is spatially cracked."""
import json, struct
import numpy as np
from pathlib import Path

ROOT = Path('/workspace/witch-hunter')

def load_glb(path):
    d = path.read_bytes()
    ln = struct.unpack('<I', d[12:16])[0]
    j = json.loads(d[20:20+ln])
    bino = 20 + ln + 8
    binlen = struct.unpack('<I', d[20+ln:20+ln+4])[0]
    buf = d[bino:bino+binlen]
    return j, buf

def pos_components(j, buf, q=4):
    # gather all POSITION accessors of all prims, build position-index graph
    pos_of_vert = []  # per (mesh,prim) arrays of quantized pos tuples
    quants = []
    for prim_idx, mesh in enumerate(j['meshes']):
        for prim in mesh['primitives']:
            ai = prim['attributes']['POSITION']
            acc = j['accessors'][ai]
            bv = j['bufferViews'][acc['bufferView']]
            off = bv.get('byteOffset', 0) + acc.get('byteOffset', 0)
            n = acc['count']
            arr = np.frombuffer(buf, dtype='<f4', count=n*3, offset=off)
            quants.append(np.round(arr.reshape(n, 3) / 10.0**-q).astype(np.int64) if False else np.round(arr.reshape(n, 3), 4))
    # global unique positions
    allpos = np.vstack(quants)
    upos, inv = np.unique(allpos, axis=0, return_inverse=True)
    # union-find on unique positions joined by triangles (face verts share position)
    parent = np.arange(len(upos))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    # faces: consecutive 3 indices per accessor mode 4 (TRIANGLES); assume triangles
    idx_cur = 0
    for mesh in j['meshes']:
        for prim in mesh['primitives']:
            ai = prim['attributes']['POSITION']
            acc = j['accessors'][ai]
            n = acc['count']
            slice_inv = inv[idx_cur:idx_cur+n]
            idx_cur += n
            if acc.get('componentType') == 5125 or 'indices' in prim:
                pass
            for t in range(0, n - 2, 3):
                a, b, c = int(slice_inv[t]), int(slice_inv[t+1]), int(slice_inv[t+2])
                ra, rb, rc = find(a), find(b), find(c)
                if ra != rb: parent[ra] = rb
                if ra != rc: parent[ra] = rc
    # count unique roots
    roots = set()
    idx_cur = 0
    for mesh in j['meshes']:
        for prim in mesh['primitives']:
            ai = prim['attributes']['POSITION']
            acc = j['accessors'][ai]
            n = acc['count']
            s = inv[idx_cur:idx_cur+n]
            idx_cur += n
            for t in range(0, n - 2, 3):
                roots.add(find(int(s[t])))
    return len(upos), len(roots)

for rel in ['art-direction/3d/assets/biome_library/wh-bramble-pixelated.glb',
            'art-direction/3d/assets/biome_library/wh-reachtree-a-pixelated.glb',
            'art-direction/3d/assets/biome_library/wh-bush-snare-pixelated.glb']:
    j, buf = load_glb(ROOT / rel)
    npos, ncomp = pos_components(j, buf)
    print(rel.split('/')[-1], ': unique positions', npos, '| position-connected components', ncomp)