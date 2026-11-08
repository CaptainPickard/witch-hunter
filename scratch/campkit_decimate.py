#!/usr/bin/env python3
"""Campkit decimate (IO QA gate 2026-10-07): the raw Meshy campsite is 39,860 faces,
over the brief's ~35k hard ceiling. Clone of scratch/decimate_roundH.py flow:
position weld -> fast_simplification quadric simplify (target stepped until it fits)
-> per-face UV transfer (medoid of 4 closest-point probes) -> unshared verts
(one UV per face) -> export with the RAW unposterized texture.
The raw Meshy GLB is kept byte-intact in scratch/campkitgen/; the decimated mesh
feeds campkit_bake.py.

  campkit_decimate.py <in.glb> <out.glb> [target_tris=30000]
Signed: Astrabot (campkit dispatch), 2026-10-07.
"""
import json, sys, os
from pathlib import Path
import numpy as np
import trimesh
import fast_simplification as fs
from scipy.spatial import cKDTree

src, dst = sys.argv[1], sys.argv[2]
target = int(sys.argv[3]) if len(sys.argv) > 3 else 30000

scene = trimesh.load(src, process=False)
assert len(scene.geometry) == 1, f'expected 1 geometry, got {len(scene.geometry)}'
m = list(scene.geometry.values())[0]
img = m.visual.material.baseColorTexture
uv = np.asarray(m.visual.uv, dtype=np.float64)
before = dict(faces=len(m.faces), verts=len(m.vertices), tex=list(img.size))
w = trimesh.Trimesh(np.asarray(m.vertices), np.asarray(m.faces), process=False)
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

# per-face UV transfer (medoid of 4 probes: centroid + 3 corner midpoints)
raw = trimesh.Trimesh(np.asarray(m.vertices), np.asarray(m.faces), process=False)
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
dist = np.linalg.norm(col[:, :, None] - col[:, None, :], axis=3).sum(axis=2)   # (F,4)
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
row = dict(signed='Astrabot (campkit) 2026-10-07', src=src, dst=dst, target=target,
           before=before, welded=welded, after=after,
           uv_transfer='per-face medoid of 4 closest-point probes',
           ext_before=[round(float(v), 4) for v in b0[1] - b0[0]],
           ext_after=[round(float(v), 4) for v in b1[1] - b1[0]])
print(json.dumps(row))
log = Path(__file__).parent / 'campkitgen' / 'decimate.jsonl'
log.parent.mkdir(parents=True, exist_ok=True)
with open(log, 'a') as f:
    f.write(json.dumps(row) + '\n')