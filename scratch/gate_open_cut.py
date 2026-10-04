#!/usr/bin/env python3
"""Round F: derive b3-gate-open-pixelated.glb from b3-gate-pixelated.glb.

The legacy b3 gate mesh has two door leaves standing almost closed inside the
doorway (front-silhouette clear gap 0.14-0.21 GLB units = ~13% of ext X).
The leaves are fused into the main welded component, so this cuts them by
box: faces whose centroid lies in each leaf's measured x/z slab between the
floor sill and the leaf tops (y < 0.06), then drops any welded component of
< 60 faces left inside the doorway box (leaf hinge crumbs / floaters).
Masonry (pillars, arch, sill) is untouched. The source GLB is not modified.
Texture is the source's already-posterized 512 map (posterize is idempotent).

  gate_open_cut.py [--force]
"""
import os, sys
import numpy as np
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
sys.path.insert(0, 'art-direction/3d')
from biome_pixelate import posterize512, export, OUT

SRC = os.path.join(OUT, 'b3-gate-pixelated.glb')
DST = os.path.join(OUT, 'b3-gate-open-pixelated.glb')
if os.path.exists(DST) and '--force' not in sys.argv:
    sys.exit(f'refusing to overwrite existing {DST}')
m = trimesh.load(SRC, force='mesh')
ymin = m.bounds[0][1]
c = m.triangles_center
Y0, Y1 = ymin + 0.012, 0.06
LEAVES = [((-0.335, -0.13), (0.24, 0.43)),    # left leaf slab (x, z)
          ((0.05, 0.305), (0.11, 0.28))]      # right leaf slab
cut = np.zeros(len(m.faces), bool)
for (x0, x1), (z0, z1) in LEAVES:
    cut |= (c[:, 0] > x0) & (c[:, 0] < x1) & (c[:, 2] > z0) & (c[:, 2] < z1) & \
           (c[:, 1] > Y0) & (c[:, 1] < Y1)
n_leaf = int(cut.sum())
m.update_faces(~cut)
m.remove_unreferenced_vertices()
# crumbs: small welded components entirely inside the doorway box
w = trimesh.Trimesh(np.asarray(m.vertices), np.asarray(m.faces), process=False)
w.merge_vertices(merge_tex=True, merge_norm=True)
n = len(w.faces); adj = w.face_adjacency
k, lab = connected_components(coo_matrix((np.ones(len(adj)), (adj[:, 0], adj[:, 1])), shape=(n, n)), directed=False)
cnt = np.bincount(lab, minlength=k)
cw = w.triangles_center
drop = np.zeros(n, bool)
for comp in np.where(cnt < 60)[0]:
    f = lab == comp
    p = cw[f]
    if p[:, 0].min() > -0.345 and p[:, 0].max() < 0.315 and p[:, 1].max() < 0.2:
        drop |= f
n_crumb = int(drop.sum())
m.update_faces(~drop)          # face order is shared with w (process=False)
m.remove_unreferenced_vertices()
# biome_pixelate.export's NORMAL injection assumes uint32 indices; this mesh
# exports uint16, so cache the normals first and trimesh writes NORMAL itself.
m.vertex_normals
export(DST, m, posterize512(m.visual.material.baseColorTexture))
print('cut leaf faces', n_leaf, 'crumb faces', n_crumb, 'faces left', len(m.faces), '->', DST)
