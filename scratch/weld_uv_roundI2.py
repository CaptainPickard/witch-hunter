#!/usr/bin/env python3
"""Round I2: weld the per-face-shattered pixelated GLBs (bramble + reach a/b/c)
into indexed meshes with UV-seam-preserving vertex copies, then export through
the repo's biome_pixelate.export (posterized texture + NORMAL injection).

Deterministic (sorted iteration, no RNG). UVs preserved per corner copy.
Backups were already copied to /tmp by the caller.
"""
import json, os, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
import trimesh

ROOT = Path('/workspace/witch-hunter')
sys.path.insert(0, str(ROOT / 'art-direction/3d'))
from biome_pixelate import export

UV_EPS = 1e-4

JOBS = [
    'art-direction/3d/assets/biome_library/wh-bramble-pixelated.glb',
    'art-direction/3d/assets/biome_library/wh-reachtree-a-pixelated.glb',
    'art-direction/3d/assets/biome_library/wh-reachtree-b-pixelated.glb',
    'art-direction/3d/assets/biome_library/wh-reachtree-c-pixelated.glb',
]

def weld_uv(path):
    obj = trimesh.load(path, force='mesh', process=False)
    F = np.asarray(obj.faces)
    V = np.asarray(obj.vertices)
    if len(V) != 3 * len(F):
        print(path.name, 'already indexed, skipping', len(V))
        return
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
    comp_of = {i: find(i) for i in range(nU)}
    verts_of_comp = defaultdict(set)
    for v, c in comp_of.items():
        verts_of_comp[c].add(v)
    corners_of_comp = defaultdict(lambda: defaultdict(list))
    for fi, f in enumerate(F):
        for k in range(3):
            g = int(inv[f[k]])
            for c, vs in verts_of_comp.items():
                if g in vs:
                    corners_of_comp[c][g].append((fi, k))
                    break

    new_V, new_VT = [], []
    copy_of_corner = {}
    nid = 0
    for c in sorted(verts_of_comp.keys()):
        vmap = corners_of_comp[c]
        for g in sorted(vmap.keys()):
            cl = vmap[g]
            base_pos = uniq[g]
            copies = []
            for fi, k in sorted(cl):
                uv = UV[F[fi][k]]
                hit = None
                for uv0, idx0 in copies:
                    if np.linalg.norm(uv0 - uv) < UV_EPS:
                        hit = idx0
                        break
                if hit is None:
                    hit = nid; nid += 1
                    copies.append((uv, hit))
                    new_V.append(base_pos)
                    new_VT.append(uv)
                copy_of_corner[(g, fi, k)] = hit

    new_V = np.asarray(new_V)
    new_VT = np.asarray(new_VT)
    newF = np.zeros((len(F), 3), dtype=np.int64)
    for fi, f in enumerate(F):
        for k in range(3):
            g = int(inv[f[k]])
            newF[fi, k] = copy_of_corner[(g, fi, k)]
    degen = int((newF[:, 0] == newF[:, 1]).sum() + (newF[:, 1] == newF[:, 2]).sum() + (newF[:, 0] == newF[:, 2]).sum())
    assert degen == 0, f'degenerate faces {degen}'

    mesh = trimesh.Trimesh(new_V, newF, process=False)
    mesh.visual = trimesh.visual.texture.TextureVisuals(uv=new_VT, material=mat, image=img)
    export(str(path), mesh, img)
    print(path.name, json.dumps({'verts_old': len(V), 'verts_new': len(new_V),
        'faces': len(newF), 'degenerate': degen,
        'bytes': os.path.getsize(str(path))}))

for rel in JOBS:
    weld_uv(ROOT / rel)
print('I2 BAKE-FIX DONE')