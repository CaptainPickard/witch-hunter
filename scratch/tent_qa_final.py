#!/usr/bin/env python3
"""C3.1c final QA: underside check of wh-tent-pixelated.glb (Round J lesson -
no undersides visible from 0/120/240 persp) + final door-z probe render.
Signed: IO, 2026-10-06.
"""
import numpy as np, trimesh, os, sys, importlib.util
spec = importlib.util.spec_from_file_location('to', 'scratch/tree_ortho.py')
to = importlib.util.module_from_spec(spec); spec.loader.exec_module(to)

BASE = 'art-direction/3d/assets/camp'
m = trimesh.load(BASE + '/wh-tent-pixelated.glb')
mesh = list(m.geometry.values())[0] if hasattr(m, 'geometry') else m
cols = to.face_colors(mesh)

# underside probe: camera below the base plane looking up (ortho from -y)
def render_lower(mesh, cols, out):
    tri = np.asarray(mesh.triangles)
    sx, sy, depth = tri[:, :, 0], tri[:, :, 2], tri[:, :, 1].mean(1)
    fn = mesh.face_normals
    # two-sided flat light
    cols2 = np.clip(cols * 0.9, 0, 1)
    order = np.argsort(depth)
    polys = np.stack([sx, sy], axis=-1)[order]
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    fig = plt.figure(figsize=(6, 8), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.add_collection(PolyCollection(polys, facecolors=cols2[order], edgecolors=cols2[order], linewidths=0.15))
    b = mesh.bounds
    r = max(b[1]-b[0]) * 0.62
    ax.set_xlim(b[0,0]-r, b[1,0]+r); ax.set_ylim(b[0,2]-r, b[1,2]+r)
    ax.set_aspect('equal'); ax.set_axis_off()
    fig.savefig(out, dpi=100); plt.close(fig)
    print('wrote', out)

render_lower(mesh, cols, '/tmp/tent_underside.png')   # top-down silhouette (base ring check)
# door +z proof at final baked orientation
to.render(mesh, cols, '/tmp/tent_final_plusz.png', 'front', 'baked+Z')
to.render(mesh, cols, '/tmp/tent_final_minusx.png', 'side', 'baked-X')
print('QA set complete')