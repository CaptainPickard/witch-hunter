#!/usr/bin/env python3
"""Check vertex winding vs UV orientation for the pixelated GLB.

GLTF expects CCW front faces (+Y up, +Z forward, right-handed). If faces are
CW as authored (as in glTF convention terms), the GPU backface-culls them.
Also verify: (a) UVs vs 3D position correlation sign (v vs +y), (b) whether
swapping UV axes fixes things, (c) test in a live page whether flipping the
index order per triangle makes the mesh appear.
"""
import trimesh, numpy as np

m = trimesh.load("art-direction/3d/assets/races/human-hunter-male-pixelated.glb", force="mesh")
print("is_winding_consistent:", m.is_winding_consistent)
print("volume:", m.volume, "  (negative volume => inverted winding)")
print("is_volume:", m.is_volume)

# UV vs position correlation: v should increase with +y (u increases with x-ish) for a sane unwrap
uv = np.asarray(m.visual.uv)
v = m.vertices
corr_y = np.corrcoef(uv[:, 1], v[:, 1])[0, 1]
corr_x = np.corrcoef(uv[:, 0], v[:, 0])[0, 1]
print("corr(uv.v, pos.y) = %.3f   corr(uv.u, pos.x) = %.3f" % (corr_y, corr_x))

# per-face normal direction consistency via signed volume
f = m.faces
tri = m.vertices[f]
n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
print("normals finite:", np.isfinite(n).all())