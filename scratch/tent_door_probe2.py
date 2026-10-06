#!/usr/bin/env python3
"""C3.1c door probe v2: use tree_ortho's proven render() at 4 azimuths by
rotating the MESH copy (not the camera). Door = the azimuth with the opening.
Signed: IO, 2026-10-06.
"""
import numpy as np, trimesh, os, sys
sys.path.insert(0, 'scratch')
import importlib.util
spec = importlib.util.spec_from_file_location('to', 'scratch/tree_ortho.py')
to = importlib.util.module_from_spec(spec)
spec.loader.exec_module.__self__ if False else spec.loader.exec_module(to)

BASE = 'art-direction/3d/assets/camp'
m = trimesh.load(BASE + '/wh-tent-pixelated.glb')
mesh = list(m.geometry.values())[0] if hasattr(m, 'geometry') else m
cols = to.face_colors(mesh)
os.makedirs('/tmp/tentdoor', exist_ok=True)
for deg, name in [(0, 'rot0'), (90, 'rot90'), (180, 'rot180'), (270, 'rot270')]:
    r = mesh.copy()
    r.apply_transform(trimesh.transformations.rotation_matrix(np.radians(deg), [0, 1, 0]))
    to.render(r, cols, f'/tmp/tentdoor/{name}_front.png', 'front', name)
    print('done', name)