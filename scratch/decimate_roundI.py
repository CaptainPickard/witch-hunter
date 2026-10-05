#!/usr/bin/env python3
"""Round I: decimate a Meshy reach-tree to <= 3500 tris, keeping its texture.

Same decimator and per-face UV transfer as scratch/decimate_roundH.py (position weld,
fast_simplification stepped to fit, each face takes the medoid texel of 4 closest-point
probes on the raw mesh). See that file's docstring for the why.

Round I addition, --snap (tip reattach): Meshy-5 returns these trees with their tertiary
twig tips as separate shells, parked a small gap (~0.08-0.13 of a ~1.6-unit tree, i.e.
~1 m in-world) off the limb ends. That is what drops tree_gate's largest-piece share to
38-56%. With --snap, every non-largest position-welded piece within SNAP_MAX of the
attached set is translated (rigidly, never rotated or scaled) so its closest vertex lands on
the closest vertex of the attached set. Pieces are processed greedily, nearest first, and
each one joins the attached set once moved, so a tip can chain onto a tip. It is deterministic
(no RNG; ties break on piece index). The UV probes then run against the snapped raw mesh,
which has the same faces and UVs with only moved vertices, so the texture follows the moved tips.

  decimate_roundI.py <in.glb> <out.glb> [target_tris=3500] [--snap]

Writes <out.glb> as decimated geometry + the RAW (unposterized) texture. Prints the signed
before/after row and appends it to scratch/treeqa/roundI/decimate.jsonl.
Signed: Claude Code (Round I), 2026-10-05.
"""
import json, sys
from pathlib import Path
import numpy as np
import trimesh
import fast_simplification as fs
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

snap = '--snap' in sys.argv
argv = [a for a in sys.argv if a != '--snap']
src, dst = argv[1], argv[2]
target = int(argv[3]) if len(argv) > 3 else 3500
SNAP_MAX = 0.25   # in raw mesh units (tree ext ~1.6); farther pieces are left where they are

scene = trimesh.load(src)
assert len(scene.geometry) == 1, f'expected 1 geometry, got {len(scene.geometry)}'
m = list(scene.geometry.values())[0]
img = m.visual.material.baseColorTexture
uv = np.asarray(m.visual.uv, dtype=np.float64)
mv = np.asarray(m.vertices, dtype=np.float64).copy()
before = dict(faces=len(m.faces), verts=len(m.vertices), tex=list(img.size))

snap_rec = None
if snap:
    # position weld (exact) -> pieces on the welded face graph
    wv, inv = np.unique(mv, axis=0, return_inverse=True)
    inv = inv.ravel()
    wf = inv[np.asarray(m.faces)]
    nf = len(wf)
    ed = np.concatenate([wf[:, [0, 1]], wf[:, [1, 2]], wf[:, [2, 0]]])
    k, vlab = connected_components(coo_matrix((np.ones(len(ed)), (ed[:, 0], ed[:, 1])),
                                              shape=(len(wv), len(wv))), directed=False)
    flab = vlab[wf[:, 0]]
    fcount = np.bincount(flab, minlength=k)
    big = int(np.argmax(fcount))
    attached = vlab == big
    pend = set(int(c) for c in np.unique(flab) if c != big)
    moves = []
    while pend:
        tree = cKDTree(wv[attached])
        best = None
        for c in sorted(pend):
            pv = np.where(vlab == c)[0]
            d, j = tree.query(wv[pv])
            i = int(np.argmin(d))
            if best is None or d[i] < best[0]:
                best = (float(d[i]), c, pv, pv[i], int(j[i]))
        dist, c, pv, vi, aj = best
        pend.discard(c)
        if dist > SNAP_MAX:
            break   # every remaining piece is farther still
        off = wv[attached][aj] - wv[vi]
        wv[pv] += off
        attached[pv] = True
        moves.append(dist)
    mv = wv[inv]
    mvs = np.array(moves) if moves else np.zeros(1)
    snap_rec = dict(pieces=int(k), moved=len(moves), left=int(k - 1 - len(moves)),
                    move_median=round(float(np.median(mvs)), 4), move_max=round(float(mvs.max()), 4),
                    faces_attached=int(fcount[np.unique(vlab[attached])].sum()), faces=nf)

w = trimesh.Trimesh(mv, np.asarray(m.faces), process=False)
w.merge_vertices()
welded = dict(faces=len(w.faces), verts=len(w.vertices))

req = target
for _ in range(8):
    vn, fn = fs.simplify(np.asarray(w.vertices, dtype=np.float32),
                         np.asarray(w.faces, dtype=np.int32), target_count=req)
    if len(fn) <= target:
        break
    req = int(req * target / len(fn)) - 1
d = trimesh.Trimesh(vn, fn, process=False)
d.remove_unreferenced_vertices()

# per-face UV transfer (decimate_roundH.py), probing the (snapped) raw mesh
raw = trimesh.Trimesh(mv, np.asarray(m.faces), process=False)
tri = d.triangles
cen = tri.mean(axis=1)
probes = np.concatenate([cen[:, None]] + [((cen + tri[:, k]) / 2)[:, None] for k in range(3)], axis=1)
P = probes.reshape(-1, 3)
KC = 24
_, cand = cKDTree(raw.triangles_center).query(P, k=KC)
cpts = trimesh.triangles.closest_point(raw.triangles[cand.ravel()], np.repeat(P, KC, axis=0)).reshape(-1, KC, 3)
best = np.linalg.norm(cpts - P[:, None], axis=2).argmin(axis=1)
fid = cand[np.arange(len(P)), best]
cp = cpts[np.arange(len(P)), best]
bary = trimesh.triangles.points_to_barycentric(raw.triangles[fid], cp)
puv = np.einsum('nk,nkj->nj', bary, uv[raw.faces[fid]])
tex = np.asarray(img.convert('RGB')).astype(float)
H, W = tex.shape[:2]
px = np.clip((puv[:, 0] % 1.0) * (W - 1), 0, W - 1).round().astype(int)
py = np.clip((1 - puv[:, 1] % 1.0) * (H - 1), 0, H - 1).round().astype(int)
col = tex[py, px].reshape(-1, 4, 3)
puv = puv.reshape(-1, 4, 2)
dist = np.linalg.norm(col[:, :, None] - col[:, None, :], axis=3).sum(axis=2)
pick = dist.argmin(axis=1)
fuv = puv[np.arange(len(fn)), pick]

F = len(d.faces)
V = d.vertices[d.faces].reshape(-1, 3)
Fi = np.arange(F * 3).reshape(F, 3)
U = np.repeat(fuv, 3, axis=0)
out = trimesh.Trimesh(V, Fi, process=False)
mat = m.visual.material.copy()
out.visual = trimesh.visual.texture.TextureVisuals(uv=U, material=mat, image=img)
out.export(dst, file_type='glb')

after = dict(faces=F, verts=len(V), welded_verts=len(d.vertices), requested=req)
b0, b1 = m.bounds, out.bounds
row = dict(signed='Claude Code (Round I) 2026-10-05', src=src, dst=dst, target=target,
           before=before, welded=welded, after=after, snap=snap_rec,
           uv_transfer='per-face medoid of 4 closest-point probes',
           ext_before=[round(float(v), 3) for v in b0[1] - b0[0]],
           ext_after=[round(float(v), 3) for v in b1[1] - b1[0]])
print(json.dumps(row))
log = Path(__file__).parent / 'treeqa' / 'roundI' / 'decimate.jsonl'
log.parent.mkdir(parents=True, exist_ok=True)
with open(log, 'a') as f:
    f.write(json.dumps(row) + '\n')
