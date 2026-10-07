#!/usr/bin/env python3
"""Ground profile + component vertical placement probe for the campkit meshy output."""
import numpy as np, trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
src = 'scratch/campkitgen/wh-campkit-meshy.glb'
sc = trimesh.load(src, process=False)
mesh = list(sc.geometry.values())[0]
V = np.asarray(mesh.vertices); F = np.asarray(mesh.faces)
w = trimesh.Trimesh(V, F, process=False); w.merge_vertices(merge_tex=False, merge_norm=False)
fn = w.face_normals; fc = w.triangles_center
hz = (np.abs(fn[:, 1]) > 0.9)
print('per-x-bin: horizontal-face y histogram (ground profile)')
for x0 in np.arange(-1.0, 1.0, 0.2):
    sel = hz & (fc[:, 0] >= x0) & (fc[:, 0] < x0 + 0.2)
    if sel.sum() < 20:
        continue
    ys = fc[sel, 1]
    u, c = np.unique(np.round(ys, 2), return_counts=True)
    top = sorted(zip(c, u), reverse=True)[:6]
    print(f'x[{x0:+.1f},{x0+0.2:+.1f}] n={int(sel.sum()):5d}  ' +
          '  '.join(f'y={y:+.2f}(n={ci})' for ci, y in top))
print()
n = len(w.faces); adj = w.face_adjacency
g = coo_matrix((np.ones(len(adj)), (adj[:, 0], adj[:, 1])), shape=(n, n))
k, lab = connected_components(g, directed=False)
counts = np.bincount(lab, minlength=k)
print('large comps vertical placement:')
for ci in np.argsort(-counts):
    if counts[ci] < 80:
        break
    sel = lab == ci; fcs = fc[sel]
    print(f'comp {ci:4d} n={int(counts[ci]):5d} ymin {fcs[:,1].min():+.3f} ymax {fcs[:,1].max():+.3f} '
          f'x[{fcs[:,0].min():+.3f},{fcs[:,0].max():+.3f}] z[{fcs[:,2].min():+.3f},{fcs[:,2].max():+.3f}] '
          f'ycent {fcs[:,1].mean():+.3f}')