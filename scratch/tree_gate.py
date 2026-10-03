#!/usr/bin/env python3
"""Tree QA gate (a) + (c): component analysis + extents/origin.

Reports two connectivity modes:
  uv    = trimesh default load (UV-seam vertices stay split -> counts UV islands;
          this is the brief's literal tree_diag.py method)
  weld  = vertices merged by POSITION only (geometric connectivity; what
          "shattered vs intact" actually means)
Gate: largest comp >= 60% faces AND tinyFar (<10 faces, centroid > 1.0) <= 20,
evaluated on the weld mode (see report for why).
Usage: tree_gate.py a.glb [b.glb ...]   (add --json for machine output)
"""
import sys, json
import numpy as np
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components


def comp_stats(m):
    n = len(m.faces)
    adj = m.face_adjacency
    g = coo_matrix((np.ones(len(adj)), (adj[:, 0], adj[:, 1])), shape=(n, n))
    k, lab = connected_components(g, directed=False)
    counts = np.bincount(lab, minlength=k)
    fc = m.triangles_center
    sums = np.zeros((k, 3))
    np.add.at(sums, lab, fc)
    cen = sums / counts[:, None]
    tiny_far = int(((counts < 10) & (np.linalg.norm(cen, axis=1) > 1.0)).sum())
    return dict(faces=n, comps=int(k), largest=int(counts.max()),
                largest_pct=round(100.0 * counts.max() / n, 1), tiny_far=tiny_far)


def analyze(path):
    m = trimesh.load(path, force='mesh')
    uv = comp_stats(m)
    w = trimesh.Trimesh(np.asarray(m.vertices), np.asarray(m.faces), process=False)
    w.merge_vertices(merge_tex=True, merge_norm=True)
    weld = comp_stats(w)
    b = m.bounds; ext = b[1] - b[0]
    ok = weld['largest_pct'] >= 60.0 and weld['tiny_far'] <= 20
    return dict(path=path, uv=uv, weld=weld,
                ext=dict(X=round(float(ext[0]), 3), Y=round(float(ext[1]), 3), Z=round(float(ext[2]), 3)),
                ymin=round(float(b[0][1]), 3), ymax=round(float(b[1][1]), 3),
                center_xz=[round(float((b[0][0]+b[1][0])/2), 3), round(float((b[0][2]+b[1][2])/2), 3)],
                gate_a='PASS' if ok else 'FAIL')


if __name__ == '__main__':
    as_json = '--json' in sys.argv
    for p in [a for a in sys.argv[1:] if a != '--json']:
        r = analyze(p)
        if as_json:
            print(json.dumps(r)); continue
        u, w = r['uv'], r['weld']
        print(f"{p}\n  uv-split: faces={u['faces']} comps={u['comps']} largest={u['largest']} ({u['largest_pct']}%) tinyFar={u['tiny_far']}"
              f"\n  welded  : comps={w['comps']} largest={w['largest']} ({w['largest_pct']}%) tinyFar={w['tiny_far']}"
              f"\n  ext X={r['ext']['X']} Y={r['ext']['Y']} Z={r['ext']['Z']} ymin={r['ymin']} centerXZ={r['center_xz']}  gate(a)={r['gate_a']}")
