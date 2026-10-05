#!/usr/bin/env python3
"""Round I2b: weld per-face shards -> indexed + UV-seam copies + SMOOTH-BY-
POSITION normals; export via plain trimesh (glTF exporter writes NORMALS for
indexed meshes itself - verify after). NO biome_pixelate.export (its inject
reads buffers without the BIN-chunk header offset and corrupts files whose
normals are missing - that corruption broke exactly the meshes this script
touches; noted for a later fix of biome_pixelate itself)."""
import json, os, shutil, struct, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
import trimesh

ROOT = Path('/workspace/witch-hunter')
UV_EPS = 1e-4

JOBS = [
    ('bramble', 'art-direction/3d/assets/biome_library/wh-bramble-pixelated.glb'),
    ('reach-a', 'art-direction/3d/assets/biome_library/wh-reachtree-a-pixelated.glb'),
    ('reach-b', 'art-direction/3d/assets/biome_library/wh-reachtree-b-pixelated.glb'),
    ('reach-c', 'art-direction/3d/assets/biome_library/wh-reachtree-c-pixelated.glb'),
]
BK = {'bramble': '/tmp/backup2-bramble.glb', 'reach-a': '/tmp/backup2-reach-a.glb',
      'reach-b': '/tmp/backup2-reach-b.glb', 'reach-c': '/tmp/backup2-reach-c.glb'}

for name, rel in JOBS:
    p = ROOT / rel
    shutil.copyfile(BK[name], p)  # always start from the clean per-face backup
    obj = trimesh.load(p, force='mesh', process=False)
    F = np.asarray(obj.faces)
    V = np.asarray(obj.vertices)
    if len(V) != 3 * len(F):
        print(name, 'unexpected layout, SKIP'); continue
    UV = np.asarray(obj.visual.uv)[:len(V)]
    img = obj.visual.material.baseColorTexture
    mat = obj.visual.material

    q = np.round(V, 5)
    uniq, inv = np.unique(q, axis=0, return_inverse=True)
    nU = len(uniq)
    parent = list(range(nU))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    for f in F:
        union(int(inv[f[0]]), int(inv[f[1]]))
        union(int(inv[f[1]]), int(inv[f[2]]))
    verts_of_comp = defaultdict(set)
    for i in range(nU):
        verts_of_comp[find(i)].add(i)
    corners_of_comp = defaultdict(lambda: defaultdict(list))
    for fi, f in enumerate(F):
        for k in range(3):
            g = int(inv[f[k]])
            for c, vs in verts_of_comp.items():
                if g in vs:
                    corners_of_comp[c][g].append((fi, k))
                    break

    new_V, new_VT = [], []
    copy_of = {}
    nid = 0
    for c in sorted(verts_of_comp.keys()):
        for g in sorted(corners_of_comp[c].keys()):
            cl = corners_of_comp[c][g]
            base_pos = uniq[g]
            copies = []
            for fi, k in sorted(cl):
                uv = UV[F[fi][k]]
                hit = None
                for uv0, idx0 in copies:
                    if np.linalg.norm(uv0 - uv) < UV_EPS:
                        hit = idx0; break
                if hit is None:
                    hit = nid; nid += 1
                    copies.append((uv, hit))
                    new_V.append(base_pos)
                    new_VT.append(uv)
                copy_of[(g, fi, k)] = hit
    new_V = np.asarray(new_V); new_VT = np.asarray(new_VT)
    newF = np.zeros((len(F), 3), dtype=np.int64)
    for fi, f in enumerate(F):
        for k in range(3):
            newF[fi, k] = copy_of[(int(inv[f[k]]), fi, k)]
    assert not (newF[:, 0] == newF[:, 1]).any(), 'degenerate'
    mesh = trimesh.Trimesh(new_V, newF, process=False)
    # smooth normals over each position-component (average face normals):
    tri = new_V[newF]
    fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12)
    NV = np.zeros_like(new_V)
    for k in range(3):
        np.add.at(NV, newF[:, k], fn)
    NV /= np.maximum(np.linalg.norm(NV, axis=1, keepdims=True), 1e-12)
    mesh.visual = trimesh.visual.texture.TextureVisuals(uv=new_VT, material=mat, image=img)
    mesh.export(p, file_type='glb')
    # verify NORMAL made it into the file
    d = p.read_bytes()
    jl, = struct.unpack_from('<I', d[12:16])
    g = json.loads(d[20:20+jl])
    prim = g['meshes'][0]['primitives'][0]
    has_n = 'NORMAL' in prim['attributes']
    print(name, json.dumps({'verts_old': len(V), 'verts_new': len(new_V), 'faces': len(F),
                            'pos_comps': len(verts_of_comp), 'normal_attr': has_n,
                            'bytes': os.path.getsize(str(p))}))
print('I2B DONE')