#!/usr/bin/env python3
"""Weld vertices with spatial tolerance and count true connected components."""
import sys
import numpy as np, trimesh
import networkx as nx
from collections import defaultdict

def weld_comps(path, tol):
    m = trimesh.load(path, force="mesh")
    v = np.round(m.vertices / tol).astype(np.int64)
    uq, inv = np.unique(v, axis=0, return_inverse=True)
    faces_q = inv[m.faces]
    good = (faces_q[:,0]!=faces_q[:,1]) & (faces_q[:,1]!=faces_q[:,2]) & (faces_q[:,0]!=faces_q[:,2])
    faces_q = faces_q[good]
    edge_faces = defaultdict(list)
    f = faces_q
    for i in range(3):
        e = np.sort(f[:, [i, (i+1)%3]], axis=1)
        pairs = list(map(tuple, e))
        for j, pair in enumerate(pairs):
            edge_faces[pair].append(j)
    g = nx.Graph(); g.add_nodes_from(range(len(f)))
    for pair, fl in edge_faces.items():
        if len(fl) > 1:
            for a, b in zip(fl, fl[1:]):
                g.add_edge(a, b)
    comps = sorted(nx.connected_components(g), key=len, reverse=True)
    return len(f), len(comps), [len(c) for c in comps], faces_q, m

if __name__ == "__main__":
    names = sys.argv[1:] or ["human-hunter-male", "human-hunter-female", "dwarf-female"]
    for name in names:
        for label, path in (("RAW", f"art-direction/3d/assets/races/{name}.glb"),
                            ("PIX", f"art-direction/3d/assets/races/{name}-pixelated.glb")):
            for tol in (1e-5, 1e-4, 1e-3):
                nf, ncomp, sizes, fq, m = weld_comps(path, tol)
                print(f"{name} {label} tol={tol:g} faces_kept={nf}/{len(m.faces)} ncomp={ncomp} top6={sizes[:6]}")
            print()