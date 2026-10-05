#!/usr/bin/env python3
"""Triage shatter: per-asset connected pieces WITHOUT the OOM-heavy path."""
import sys, json, subprocess
from pathlib import Path
import trimesh, numpy as np

ROOT = Path('/workspace/witch-hunter')

def piece_stats(path):
    # load ONE geometry at a time; use adjacency split on a merged COPIES dict
    obj = trimesh.load(path, force='scene', process=False)
    geos = []
    for name, g in obj.geometry.items():
        m = g.copy()
        try:
            T = obj.graph.get(name)[0]
            m.apply_transform(T)
        except Exception:
            pass
        geos.append((name, m))
    # merge vertices+faces manually to avoid submesh repair blowups
    vs, fs, off = [], [], 0
    for name, m in geos:
        vs.append(np.asarray(m.vertices))
        fs.append(np.asarray(m.faces) + off)
        off += len(m.vertices)
    V = np.vstack(vs)
    F = np.vstack(fs)
    import scipy.sparse
    from scipy.sparse import coo_matrix
    n = len(V)
    # face adjacency graph via shared edges
    edges = np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
    # union-find on vertices joined by edges
    parent = np.arange(n)
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    roots = np.array([find(i) for i in range(n)])
    uniq, counts = np.unique(roots, return_counts=True)
    # per-component face counts: dominant root per face
    face_root = np.array([find(f[0]) for f in F], dtype=np.int64)
    fu, fc = np.unique(face_root, return_counts=True)
    order = np.sort(fc)[::-1]
    return {
        'pieces': int(len(fu)),
        'top_face_frac': np.round(order[:5] / len(F), 3).tolist(),
        'verts_largest': int(counts.max()) if len(counts) else 0,
    }

for name, rel in [
    ('lamp-post', 'art-direction/3d/assets/church-kit/lantern-post-pixelated.glb'),
    ('lamp-post-RAW', 'art-direction/3d/assets/church-kit/lantern-post.glb'),
    ('grave-mound', 'art-direction/3d/assets/graveyard/grave-mound-pixelated.glb'),
    ('grave-mound-RAW', 'art-direction/3d/assets/graveyard/grave-mound.glb'),
    ('bramble', 'art-direction/3d/assets/biome_library/wh-bramble-pixelated.glb'),
    ('bramble-RAW', 'art-direction/3d/assets/biome_library/raw/wh-bramble.glb'),
    ('reach-a', 'art-direction/3d/assets/biome_library/wh-reachtree-a-pixelated.glb'),
    ('reach-a-RAW', 'art-direction/3d/assets/biome_library/raw/wh-reachtree-a.glb'),
    ('reach-b', 'art-direction/3d/assets/biome_library/wh-reachtree-b-pixelated.glb'),
    ('reach-c', 'art-direction/3d/assets/biome_library/wh-reachtree-c-pixelated.glb'),
    ('rose-snare', 'art-direction/3d/assets/biome_library/wh-bush-snare-pixelated.glb'),
]:
    p = ROOT / rel
    if not p.exists():
        print(name, 'MISSING', rel)
        continue
    r = piece_stats(p)
    print(name, json.dumps(r))

if __name__ == '__main__':
    pass