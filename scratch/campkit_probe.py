#!/usr/bin/env python3
"""Component-inspection helper for the campkit meshy output (pre-classification).
Prints connected components (welded by POSITION) with face counts, bbox and
centroid, so the bake's node-assignment rules can be coded from real data.
  campkit_probe.py <meshy.glb>
"""
import sys
import numpy as np
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

src = sys.argv[1]
sc = trimesh.load(src, process=False)
mesh = list(sc.geometry.values())[0] if hasattr(sc, 'geometry') else sc
print('faces', len(mesh.faces), 'verts', len(mesh.vertices))
print('extents', np.asarray(mesh.extents).round(3).tolist())
print('bounds min', np.asarray(mesh.bounds[0]).round(3).tolist(), 'max', np.asarray(mesh.bounds[1]).round(3).tolist())
w = trimesh.Trimesh(np.asarray(mesh.vertices), np.asarray(mesh.faces), process=False)
w.merge_vertices(merge_tex=True, merge_norm=True)
n = len(w.faces)
adj = w.face_adjacency
g = coo_matrix((np.ones(len(adj)), (adj[:, 0], adj[:, 1])), shape=(n, n))
k, lab = connected_components(g, directed=False)
counts = np.bincount(lab, minlength=k)
print('welded components:', k)
order = np.argsort(-counts)
for ci in order[:14]:
    sel = lab == ci
    fc = w.triangles_center[sel]
    lo, hi = fc.min(0), fc.max(0)
    cen = fc.mean(0)
    print(f'  comp {ci}: faces {int(counts[ci]):5d}  bbox {np.round(lo,2).tolist()}..{np.round(hi,2).tolist()}'
          f'  centroid {np.round(cen,2).tolist()}')
if k > 14:
    print(f'  ... {k-14} more comps, faces {int(counts[order[14:]].sum())}')