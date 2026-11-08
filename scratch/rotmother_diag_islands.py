"""List every contact-island < 0.5% of the 18k mother bake: size + position.
python3 scratch/rotmother_diag_islands.py
"""
import numpy as np
import trimesh
import scipy.sparse as sp
import sys
sys.path.insert(0, 'scratch')
from scipy.spatial import cKDTree

path = 'art-direction/3d/assets/races/rotmother.glb'
m = trimesh.load(path, force='mesh', process=False)
v = np.asarray(m.vertices, dtype=np.float64)
f = np.asarray(m.faces, dtype=np.int64)
mesh = trimesh.Trimesh(v, f, process=True)
v2 = np.asarray(mesh.vertices)
f2 = np.asarray(mesh.faces)
e = np.vstack([f2[:, [0, 1]], f2[:, [1, 2]], f2[:, [2, 0]]])
parent = list(range(len(v2)))
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
seen = set()
for a, b in e:
    key = (a, b) if a < b else (b, a)
    if key in seen:
        continue
    seen.add(key)
    ra, rb = find(int(a)), find(int(b))
    if ra != rb:
        parent[ra] = rb
roots = np.array([find(i) for i in range(len(v2))])
uniq, counts = np.unique(roots, return_counts=True)
bidx = {r: i for i, r in enumerate(uniq)}
blabel = np.array([bidx[r] for r in roots])
tree = cKDTree(v2)
pairs = tree.query_ball_point(v2, r=0.002, return_length=False)
for i, nbrs in enumerate(pairs):
    for jn in nbrs:
        if blabel[jn] != blabel[i]:
            ra, rb = find(i), find(jn)
            if ra != rb:
                parent[ra] = rb
roots2 = np.array([find(i) for i in range(len(v2))])
face_root2 = roots2[f2[:, 0]]
islands, icounts = np.unique(face_root2, return_counts=True)
tot = icounts.sum()
order = np.argsort(icounts)[::-1]
print('islands:', len(islands), 'total faces', tot)
for k in order:
    n = int(icounts[k])
    if n < 0.005 * tot:
        sel = face_root2 == islands[k]
        mv = v2[f2[sel].ravel()]
        lo, hi = mv.min(0), mv.max(0)
        print(f'ISLAND f{n:5d} x[{lo[0]:+.3f}..{hi[0]:+.3f}] '
              f'y[{lo[1]:+.3f}..{hi[1]:+.3f}] z[{lo[2]:+.3f}..{hi[2]:+.3f}] '
              f'center ({mv.mean(0).round(2).tolist()})')