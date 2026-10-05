#!/usr/bin/env python3
"""Round H continuation: decimate the Meshy bramble to the free-bush budget, keeping its texture.

The decimator is the same one Round G used (scratch/decimate_roundG.py): position weld, then
fast_simplification quadric simplify with the target stepped down until the result fits.
Unlike the snare, the raw bramble carries a baseColor texture + TEXCOORD_0. Its UV atlas has
about 6k islands for 28k faces, so averaging UVs per decimated vertex (the regen_pipeline_v2
approach) would smear across seams on almost every face. UVs are transferred PER FACE instead:
  - each decimated face gets its own 3 vertices (unshared), and
  - all 3 take one UV. Four probe points (centroid + 3 points halfway to the corners) are
    projected to the closest point on the raw mesh, and their UVs are interpolated
    barycentrically on the raw face they hit. The probe whose texel is the medoid of the 4
    texel colours wins. This is deterministic and drops speckle.
So each face samples a single texel, and with 512 NEAREST posterize on top that matches the pixel register.

  decimate_roundH.py <in.glb> <out.glb> [target_tris=2500]

Writes <out.glb> as decimated geometry + the RAW (unposterized) texture. Prints the signed
before/after row and appends it to scratch/treeqa/roundH/decimate.jsonl.
Signed: Claude Code (Round H continuation), 2026-10-05.
"""
import json, sys
from pathlib import Path
import numpy as np
import trimesh
import fast_simplification as fs

src, dst = sys.argv[1], sys.argv[2]
target = int(sys.argv[3]) if len(sys.argv) > 3 else 2500

scene = trimesh.load(src)
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

# per-face UV transfer
raw = trimesh.Trimesh(np.asarray(m.vertices), np.asarray(m.faces), process=False)
tri = d.triangles                                       # (F,3,3)
cen = tri.mean(axis=1)
probes = np.concatenate([cen[:, None]] + [((cen + tri[:, k]) / 2)[:, None] for k in range(3)], axis=1)
P = probes.reshape(-1, 3)
# closest point without rtree: the K nearest raw face centroids are candidates, and
# trimesh.triangles.closest_point gives the exact point on each; nearest wins (ties -> lower k)
from scipy.spatial import cKDTree
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
pick = dist.argmin(axis=1)                              # argmin ties -> lowest probe index
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
row = dict(signed='Claude Code (Round H continuation) 2026-10-05', src=src, dst=dst, target=target,
           before=before, welded=welded, after=after, uv_transfer='per-face medoid of 4 closest-point probes',
           ext_before=[round(float(v), 3) for v in b0[1] - b0[0]],
           ext_after=[round(float(v), 3) for v in b1[1] - b1[0]])
print(json.dumps(row))
log = Path(__file__).parent / 'treeqa' / 'roundH' / 'decimate.jsonl'
log.parent.mkdir(parents=True, exist_ok=True)
with open(log, 'a') as f:
    f.write(json.dumps(row) + '\n')
