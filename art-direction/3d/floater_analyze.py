#!/usr/bin/env python3
"""Stronger floater analysis: for every component, min distance from its
vertices to the nearest vertex of ANY OTHER component. Islands whose whole
boundary sits > gap_thresh from everything else are true floaters."""
import sys, json
import numpy as np, trimesh
from scipy.spatial import cKDTree
import networkx as nx
from collections import defaultdict

def welded_comps(m, tol=1e-4):
    parent = list(range(len(m.vertices)))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    t = cKDTree(m.vertices)
    for a, b in t.query_pairs(tol, output_type="ndarray"):
        ra, rb = find(a), find(b)
        if ra != rb: parent[ra] = rb
    fids = np.array([find(v) for v in range(len(m.vertices))])
    f = fids[m.faces]
    good = (f[:,0]!=f[:,1]) & (f[:,1]!=f[:,2]) & (f[:,2]!=f[:,0])
    keep = np.nonzero(good)[0]
    f = f[good]
    ef = defaultdict(list)
    for i in range(3):
        e = np.sort(f[:, [i, (i+1)%3]], axis=1)
        for j, p in enumerate(map(tuple, e)):
            ef[p].append(j)
    g = nx.Graph(); g.add_nodes_from(range(len(f)))
    for p, fl in ef.items():
        if len(fl) > 1:
            for a, b in zip(fl, fl[1:]): g.add_edge(a, b)
    comps = sorted(nx.connected_components(g), key=len, reverse=True)
    return [keep[np.array(sorted(c))] for c in comps], m

def analyze(path):
    m = trimesh.load(path, force="mesh")
    comps, m = welded_comps(m)
    allv = m.vertices
    n = len(comps)
    if n == 1:
        return {"path": path, "comps": 1}
    # per-comp vertex arrays
    cv = [np.unique(m.faces[c].reshape(-1)) for c in comps]
    gaps = []
    for i in range(n):
        others = np.concatenate([cv[j] for j in range(n) if j != i]) if n > 2 else cv[1-i]
        tree = cKDTree(allv[others])
        d, _ = tree.query(allv[cv[i]], k=1)
        gaps.append({"faces": len(comps[i]), "gap": float(d.min()),
                     "gap_mean": float(d.mean())})
    return {"path": path, "comps": n, "faces": len(m.faces),
            "top": sorted(gaps, key=lambda g: -g["faces"])[:25]}

if __name__ == "__main__":
    path = sys.argv[1]
    r = analyze(path)
    print(json.dumps(r, indent=1))