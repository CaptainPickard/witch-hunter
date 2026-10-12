"""Contact-island census for m8-boulder-small (reuse the bake counter logic).
python3 scratch/cc-c8/island_check.py
"""
import sys
import numpy as np
import trimesh
import scipy.sparse as sp
sys.path.insert(0, 'scratch')

PATH = 'art-direction/3d/assets/biome_library/m8-boulder-small.glb'
m = trimesh.load(PATH, force='mesh', process=False)
v = np.asarray(m.vertices, dtype=np.float64)
f = np.asarray(m.faces, dtype=np.int64)
mesh = trimesh.Trimesh(v, f, process=True)
v2 = np.asarray(mesh.vertices)
f2 = np.asarray(mesh.faces)
e = np.vstack([f2[:, [0, 1]], f2[:, [1, 2]], f2[:, [2, 0]]])
parent = list(range(len(v2)))
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]; x = parent[x]
    return x
seen = set()
for a, b in e:
    key = (a, b) if a < b else (b, a)
    if key in seen: continue
    seen.add(key)
    ra, rb = find(int(a)), find(int(b))
    if ra != rb: parent[ra] = rb
roots = np.array([find(i) for i in range(len(v2))])
uq, ct = np.unique(roots, return_counts=True)
bidx = {r: i for i, r in enumerate(uq)}
blab = np.array([bidx[r] for r in roots])
from scipy.spatial import cKDTree
tree = cKDTree(v2)
pairs = tree.query_ball_point(v2, r=0.002, return_length=False)
for i, nbrs in enumerate(pairs):
    for jn in nbrs:
        if blab[jn] != blab[i]:
            ra, rb = find(i), find(jn)
            if ra != rb: parent[ra] = rb
rootsA = np.array([find(i) for i in range(len(v2))])
faceR = rootsA[f2[:, 0]]
isl, icnt = np.unique(faceR, return_counts=True)
tot = icnt.sum()
sizes = sorted(icnt.tolist(), reverse=True)
small = [s for s in sizes if s < 0.005 * tot]
print(f'CONTACT-ISLANDS {len(isl)} sizes {sizes[:6]} (of {tot}) | islands <0.5%: '
      f'{len(small)} faces {int(sum(small))} ({sum(small)/tot*100:.3f}%)')