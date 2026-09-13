#!/usr/bin/env python3
"""Shard removal post-pass: drop tiny (<10 faces) components far from the main body surface.

Distance = nearest-vertex distance from component to the main (largest) component's
vertex cloud via cKDTree. Bodies are single visual meshes; anything tiny AND far is
decimation debris. Weapons/kit are NOT touched by this script.
Writes <name>-pixelated.glb in place (backup to /tmp first), preserving material/uv.
"""
import sys, io, os
import numpy as np, trimesh
from scipy.spatial import cKDTree
import networkx as nx
from collections import defaultdict

def face_components_welded(m, tol=1e-4):
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
    deg = (f[:, 0] == f[:, 1]) | (f[:, 1] == f[:, 2]) | (f[:, 0] == f[:, 2])
    keep = ~deg
    f = f[keep]
    ef = defaultdict(list)
    for i in range(3):
        e = np.sort(f[:, [i, (i + 1) % 3]], axis=1)
        for j, p in enumerate(map(tuple, e)):
            ef[p].append(j)
    g = nx.Graph(); g.add_nodes_from(range(len(f)))
    for p, fl in ef.items():
        if len(fl) > 1:
            for a, b in zip(fl, fl[1:]):
                g.add_edge(a, b)
    comps = sorted(nx.connected_components(g), key=len, reverse=True)
    # map back to original face indices
    orig_idx = np.nonzero(keep)[0]
    return [orig_idx[np.array(sorted(c))] for c in comps]

def process(path, max_faces=10, min_dist=0.01, dry=False):
    m = trimesh.load(path, force="mesh")
    comps = face_components_welded(m)
    if len(comps) < 2:
        print(f"{os.path.basename(path)}: single component, nothing to do")
        return 0
    main = comps[0]
    main_v = m.vertices[np.unique(m.faces[main])]
    tree = cKDTree(main_v)
    drop = []
    for c in comps[1:]:
        if len(c) >= max_faces:
            continue
        cv = m.vertices[np.unique(m.faces[c])]
        d, _ = tree.query(cv, k=1)
        if d.min() > min_dist:
            drop.append(c)
    if not drop:
        print(f"{os.path.basename(path)}: {len(comps)} comps, no tiny-far shards, nothing to do")
        return 0
    drop_faces = np.concatenate([np.asarray(c) for c in drop])
    keep_mask = np.ones(len(m.faces), dtype=bool)
    keep_mask[drop_faces] = False
    faces = m.faces[keep_mask]
    print(f"{os.path.basename(path)}: dropping {len(drop)} comps / {len(drop_faces)} faces "
          f"({len(comps)} -> {len(comps) - len(drop)} comps, {len(m.faces)} -> {keep_mask.sum()} faces)")
    if dry:
        return len(drop)
    # rebuild mesh preserving visual (uv + material)
    vis = m.visual
    uv = np.asarray(vis.uv)
    nm = trimesh.Trimesh(vertices=m.vertices, faces=m.faces[keep_mask], process=False, visual=vis)
    if uv is not None and uv.shape[0] == len(m.vertices):
        # per-vertex uv: indexing survives the face drop automatically
        from trimesh.visual.texture import TextureVisuals
        nm.visual = TextureVisuals(uv=uv, material=vis.material, image=vis.material.baseColorTexture)
    elif uv is not None and uv.shape[0] == len(m.faces) * 3:
        # per-corner uv: keep corners of kept faces
        corner_keep = np.repeat(keep_mask, 3)
        from trimesh.visual.texture import TextureVisuals
        nm.visual = TextureVisuals(uv=uv[corner_keep].reshape(-1, 2),
                                   material=vis.material, image=vis.material.baseColorTexture)
    out = io.BytesIO()
    nm.export(out, file_type="glb")
    data = out.getvalue()
    with open(path, "wb") as fh:
        fh.write(data)
    os.chmod(path, 0o644)
    return len(drop)

if __name__ == "__main__":
    d = "/workspace/witch-hunter/art-direction/3d/assets/races"
    dry = "--dry" in sys.argv
    total = 0
    for fn in sorted(os.listdir(d)):
        if fn.endswith("-pixelated.glb"):
            total += process(os.path.join(d, fn), dry=dry)
    print("TOTAL dropped components:", total)