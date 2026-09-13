#!/usr/bin/env python3
"""UV island + texel brightness stats for race pixelated glbs."""
import trimesh, numpy as np, networkx as nx

for name in ["human-hunter-male", "human-hunter-female", "dwarf-female", "orc-female"]:
    m = trimesh.load(f"art-direction/3d/assets/races/{name}-pixelated.glb", force="mesh")
    uv = np.asarray(m.visual.uv)
    uq = np.round(uv, 5)
    uniq_u, inv_u = np.unique(uq.reshape(-1, 2), axis=0, return_inverse=True)
    fu = inv_u[m.faces]
    g = nx.Graph(); g.add_nodes_from(range(len(m.faces)))
    for a, b in m.face_adjacency:
        if len(set(fu[a]) & set(fu[b])):
            g.add_edge(a, b)
    comps = list(nx.connected_components(g))
    sizes = sorted((len(c) for c in comps), reverse=True)
    print(name, "uv islands:", len(comps), "top10:", sizes[:10])
    arr = np.asarray(m.visual.material.baseColorTexture.convert("RGB"))
    h, w = arr.shape[:2]
    px = np.clip((uq[:, 0] * w).astype(int), 0, w - 1)
    py = np.clip(((1 - uq[:, 1]) * h).astype(int), 0, h - 1)
    vcol = arr[py, px][m.faces].mean(axis=1)
    fb = vcol.mean(axis=1)
    print("  face brightness: mean %.1f std %.1f p95 %.1f max %.1f" % (fb.mean(), fb.std(), np.percentile(fb, 95), fb.max()))
    # island brightness variance: do tiny islands get wildly different colors?
    import statistics
    island_means = [fb[sorted(c)].mean() for c in comps if len(c) >= 5]
    print("  island mean-brightness: spread min %.0f max %.0f stddev %.1f" % (min(island_means), max(island_means), statistics.pstdev(island_means)))