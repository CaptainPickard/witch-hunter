#!/usr/bin/env python3
import warnings; warnings.simplefilter("ignore")
import numpy as np, trimesh
from scipy.spatial import cKDTree
for name in ["human-hunter-male", "orc-male-warrior", "vampire-male-noble"]:
    m = trimesh.load(f"assets/races/{name}-pixelated.glb", force='scene')
    g = list(m.geometry.values())[0]
    rgb = np.asarray(g.visual.material.baseColorTexture)[...,:3]
    L = rgb.mean(axis=2)
    d = np.concatenate([np.abs(np.diff(L,axis=1)).ravel(), np.abs(np.diff(L,axis=0)).ravel()])
    print(name, "atlas jump p50/p90/p99/max:", np.percentile(d,[50,90,99]).round(1), d.max().round(0),
          " frac>30:", (d>30).mean().round(4), " frac>50:", (d>50).mean().round(4))
    v = g.vertices
    t = cKDTree(v)
    pairs = t.query_pairs(5e-3, output_type='ndarray')
    d01 = np.linalg.norm(v[pairs[:,0]]-v[pairs[:,1]], axis=1)
    tight = (d01 > 1e-4) & (d01 < 2e-3)
    print("  near-dup verts (1e-4..2e-3):", int(tight.sum()), "of", len(v))