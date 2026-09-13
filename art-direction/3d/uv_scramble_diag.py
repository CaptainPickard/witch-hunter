#!/usr/bin/env python3
"""Per-triangle texel-brightness coherence diagnostic for pixelated GLBs.
If adjacent triangles alternate wildly between dark and bright texels, UVs are scrambled."""
import trimesh, numpy as np, os

D = "art-direction/3d/assets/races"

for fn in sorted(os.listdir(D)):
    if not fn.endswith("-pixelated.glb"):
        continue
    m = trimesh.load(os.path.join(D, fn), force="mesh")
    uv = np.asarray(m.visual.uv)
    tex = m.visual.material.baseColorTexture
    arr = np.asarray(tex.convert("RGB"))
    h, w = arr.shape[:2]
    uq = np.round(uv, 6)
    px = np.clip((uq[:, 0] * w).astype(int), 0, w - 1)
    py = np.clip(((1 - uq[:, 1]) * h).astype(int), 0, h - 1)
    vcol = arr[py, px]                      # (V,3) sampled texel per vertex
    fc = vcol[m.faces].mean(axis=1)         # (F,3) per-corner RGB
    fb = fc.mean(axis=1)                    # (F,) face mean brightness
    # 1) adjacent-face brightness jump
    adj = m.face_adjacency
    jumps = np.abs(fb[adj[:, 0]] - fb[adj[:, 1]])
    # 2) within-face corner spread (UV corners of one tri sampling far-apart texels)
    spread = fc.max(axis=1) - fc.min(axis=1)
    # 3) same-position vertices with different UVs? (unwelded UV seams - normal)
    # 4) UV-to-position spatial coherence: nearest 3D neighbor should have nearby UV
    from scipy.spatial import cKDTree
    vt = cKDTree(m.vertices)
    sample = np.arange(len(m.vertices))
    d3, i3 = vt.query(m.vertices[sample], k=2)
    nn = i3[:, 1]
    uv_dist_nn = np.linalg.norm(uv - uv[nn], axis=1)
    # control: shuffled UV pairing
    rng = np.random.default_rng(0)
    sh = rng.permutation(len(m.vertices))
    uv_dist_shuf = np.linalg.norm(uv - uv[sh], axis=1)
    print("%-32s V=%d F=%d | adj-delta mean %4.1f p95 %4.1f frac>80 %.3f | corner-spread mean %4.1f p95 %4.1f frac>120 %.3f | NN-uv-dist mean %.3f (shuffled %.3f)" % (
        fn[:-14], len(m.vertices), len(m.faces), jumps.mean(), np.percentile(jumps, 95),
        (jumps > 80).mean(), spread.mean(), np.percentile(spread, 95), (spread > 120).mean(),
        uv_dist_nn.mean(), uv_dist_shuf.mean()))