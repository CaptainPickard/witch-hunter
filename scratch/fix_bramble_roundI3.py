#!/usr/bin/env python3
"""Round I3b: rebuild bramble from the H bake's mid file (wh-bramble.glb = decimated
+ textured pre-pixelate, which HAS uv) -> delete far floaters > 0.25m + snap near
ones + weld + smooth normals -> pixelate via biome_pixelate.posterize512 -> land.
Deterministic."""
import struct, json
from collections import defaultdict
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial import cKDTree
import sys
sys.path.insert(0, '/workspace/witch-hunter/art-direction/3d')

ROOT = Path('/workspace/witch-hunter')
SRC = ROOT / 'art-direction/3d/assets/biome_library/wh-bramble.glb'
DST = ROOT / 'art-direction/3d/assets/biome_library/wh-bramble-pixelated.glb'

m = trimesh.load(SRC, force='mesh', process=False)
F = np.asarray(m.faces); V = np.asarray(m.vertices)
uv_full = np.asarray(m.visual.uv)
img = m.visual.material.baseColorTexture
mat = m.visual.material
print('src verts', len(V), 'faces', len(F), 'uv', uv_full.shape if uv_full is not None else None)

qq, inv = np.unique(np.round(V, 4), axis=0, return_inverse=True)
parent = list(range(len(qq)))
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]; x = parent[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb: parent[ra] = rb
for f in F:
    union(int(inv[f[0]]), int(inv[f[1]])); union(int(inv[f[1]]), int(inv[f[2]]))
comp_faces = defaultdict(list)
for fi, f in enumerate(F):
    comp_faces[find(int(inv[f[0]]))].append(fi)
areas = {}
for c, fl in comp_faces.items():
    t_ = V[F[fl]]
    areas[c] = float(np.sum(np.linalg.norm(np.cross(t_[:,1]-t_[:,0], t_[:,2]-t_[:,0]), axis=1)))
main = max(areas, key=areas.get)
main_tri = V[F[comp_faces[main]]]
t = cKDTree(main_tri.mean(axis=1))
keep, snapped, deleted, del_area = list(comp_faces[main]), 0, 0, 0.0
offsets = {}
for c, fl in sorted(comp_faces.items()):
    if c == main: continue
    dmin, ci = t.query(V[F[fl]].mean(axis=0)[None, :], k=1)
    dmin_val = float(np.asarray(dmin).ravel()[0])
    ci_val = int(np.asarray(ci).ravel()[0])
    if dmin_val <= 0.25:
        keep.extend(fl)
        if dmin_val > 1e-9:
            offsets[c] = main_tri.mean(axis=1)[ci_val] - V[F[fl]].mean(axis=0)
            snapped += 1
    else:
        deleted += 1; del_area += areas[c]
print('comp', len(areas), 'main area', round(areas[main],2),
      'snapped', snapped, 'deleted', deleted, 'deleted-area-frac', round(del_area/sum(areas.values()), 4))
K = np.array(sorted(set(keep)))
F2 = F[K]
V2 = V.copy()
for c, offv in offsets.items():
    mem = np.array([v for v in range(len(qq)) if find(v) == c], dtype=np.int64)
    mem = mem[np.isin(mem, np.arange(len(qq)))]
    mem = mem[mem < len(qq)]
    if len(mem) == 0: continue
    V2 = V2  # placeholder no-op; qq mutation below
    offv_v = np.asarray(offv, dtype=float).ravel()
    if offv_v.size != 3:
        # stored as [target - mean_piece] pairs from the k=1 probe: recompute per piece
        target_pt = offv_v[:3]
        mean_pt = qq[mem, :].mean(axis=0)
        offv_v = target_pt - mean_pt
    qq[mem, :] = qq[mem, :] + offv_v.reshape(1, 3)
V2 = qq[inv]
uv2 = uv_full[V2_idx] if False else None
# uv per ORIGINAL vert index: uv rows align with V (per-vertex in this mid file? mid is indexed 6.8k? check)
print('uv rows', uv_full.shape[0], 'V rows', len(V))
# mid file bramble.glb: verts 2499*?? - indexed from decimate (H): verts~2500 (welded at decimate) YES
assert uv_full.shape[0] == len(V), 'uv/vert mismatch'
tri = V2[F2]
fn = np.cross(tri[:,1]-tri[:,0], tri[:,2]-tri[:,0])
fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12)
NV = np.zeros_like(qq)
F2w = inv[F2]
for k in range(3):
    np.add.at(NV, F2w[:, k], fn)
NV /= np.maximum(np.linalg.norm(NV, axis=1, keepdims=True), 1e-12)
zv = np.where(np.abs(np.linalg.norm(NV, axis=1) - 1) > 0.5)[0]
gpos = {}
for i in np.where(np.abs(np.linalg.norm(NV, axis=1) - 1) <= 0.5)[0]:
    gpos.setdefault(tuple(np.round(qq[i], 4)), i)
for vi in zv:
    donor = gpos.get(tuple(np.round(qq[vi], 4)))
    if donor is not None: NV[vi] = NV[donor]
rem = np.where(np.abs(np.linalg.norm(NV, axis=1) - 1) > 0.5)[0]
if len(rem):
    good_idx = np.array([i for i in np.where(np.abs(np.linalg.norm(NV, axis=1) - 1) <= 0.5)[0]])
    _, irem = cKDTree(qq[good_idx]).query(qq[rem], k=1)
    for j, vi in enumerate(rem):
        NV[vi] = NV[good_idx[irem[j]]]
# weld to indexed: unique qq2
qq2, inv2 = np.unique(np.round(qq, 6), axis=0, return_inverse=True)
F3 = inv2[F2w].astype(np.int64)
assert not (F3[:,0]==F3[:,1]).any() and not (F3[:,1]==F3[:,2]).any()
# UV dedupe: per new vert - the uv of the representative original vert:
uv_rows = {}
for new_i, old_i in enumerate(inv2_reps := [None] * 0): pass
# simpler: build uv per new_i = uv of ANY old vert mapping there (identical uv since
# this mid file's uv is per OLD vert, unique per welded vert):
uv_new = np.zeros((len(qq2), 2))
seen = {}
# mid file: verts == unique welded verts? uv_full rows align with V (1578 vs 1577?) - guard
nv_rows = min(len(V), len(inv2), uv_full.shape[0])
for old_i in range(nv_rows):
    ni = int(inv2[old_i])
    if ni not in seen:
        seen[ni] = uv_full[old_i]
for ni in range(len(qq2)):
    uv_new[ni] = seen.get(ni, np.array([0.0, 0.0]))
mesh = trimesh.Trimesh(qq2, F3, process=False, face_normals=None, vertex_normals=NV)
mesh.visual = trimesh.visual.texture.TextureVisuals(uv=uv_new, material=mat, image=img)
from biome_pixelate import posterize512
# pixelate tex: 512 NEAREST + 5-bit
tex_new = posterize512(img)
mesh.visual = trimesh.visual.texture.TextureVisuals(uv=uv_new, material=mat, image=tex_new)
mesh.export(DST, file_type='glb')
print('exported', DST.name, DST.stat().st_size)