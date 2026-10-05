#!/usr/bin/env python3
"""Round K: land the Meshy lantern-post-v2 in church-kit via the texture path.

  1. position weld of the raw Meshy mesh (its UV-seam split is not geometry) + XZ recenter so
     the PILLAR axis (vertex band 20-60% H) sits on the glTF origin: assets.js groundAlign only
     shifts Y, so the prop row's x/z, the collider circle and the socket offset all hang off
     this origin;
  2. quadric decimate on the WELDED mesh, target <= 2500 (scratch/decimate_roundH.py loop);
  3. per-face UV transfer, the decimate_roundH.py method (4 closest-point probes on the raw
     mesh, texel medoid wins): one texel per face, which matches the 512 posterize;
  4. weld positions -> UV-seam copies (one vertex per distinct UV at a welded position), so the
     faces share exact corner positions (no cracks) and are NOT the unshared per-face layout;
  5. smooth normals accumulated per welded POSITION (not per copy) + zero-normal repair from the
     nearest good position;
  6. posterize512 imported directly (biome_pixelate.export()'s injector is NOT used, its BIN
     header offset bug is filed) -> trimesh GLB export -> verify NORMAL attr, b'JSON' chunk,
     reload counts.
Outputs (church-kit flat layout + raw/ + refs/):
  church-kit/raw/lantern-post-v2.glb          Meshy original, byte copy
  church-kit/refs/lantern-post-v2-ref.png     t2i ref (unmatted), byte copy
  church-kit/lantern-post-v2-ref.png          matted ref (sits with the other kit refs)
  church-kit/lantern-post-v2.glb              decimated geometry + raw texture
  church-kit/lantern-post-v2-pixelated.glb    decimated geometry + posterized 512 texture
Appends a signed row to scratch/treeqa/roundK/decimate.jsonl.
Signed: Claude Code (Round K), 2026-10-05.
"""
import json, shutil, struct, sys
from pathlib import Path
import numpy as np
import trimesh
import fast_simplification as fs
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'art-direction/3d'))
from biome_pixelate import posterize512

RAW = ROOT / 'scratch/treegen/roundK/lantern-post-v2-meshy.glb'
REF = ROOT / 'scratch/treegen/roundK/lantern-post-v2-ref.png'
MATTE = ROOT / 'scratch/treegen/roundK/lantern-post-v2-ref-matte.png'
KIT = ROOT / 'art-direction/3d/assets/church-kit'
TARGET = 2500

(KIT / 'raw').mkdir(exist_ok=True)
(KIT / 'refs').mkdir(exist_ok=True)
shutil.copyfile(RAW, KIT / 'raw/lantern-post-v2.glb')
shutil.copyfile(REF, KIT / 'refs/lantern-post-v2-ref.png')
shutil.copyfile(MATTE, KIT / 'lantern-post-v2-ref.png')

scene = trimesh.load(RAW)
assert len(scene.geometry) == 1, f'expected 1 geometry, got {len(scene.geometry)}'
m = list(scene.geometry.values())[0]
img = m.visual.material.baseColorTexture
mat = m.visual.material
uv = np.asarray(m.visual.uv, dtype=np.float64)
before = dict(faces=len(m.faces), verts=len(m.vertices), tex=list(img.size))

# 1. weld + recenter on the pillar axis
V0 = np.asarray(m.vertices, dtype=np.float64)
y0, y1 = V0[:, 1].min(), V0[:, 1].max()
band = (V0[:, 1] > y0 + 0.2 * (y1 - y0)) & (V0[:, 1] < y0 + 0.6 * (y1 - y0))
shift = np.array([-(V0[band, 0].min() + V0[band, 0].max()) / 2, 0.0,
                  -(V0[band, 2].min() + V0[band, 2].max()) / 2])
V0 = V0 + shift
w = trimesh.Trimesh(V0, np.asarray(m.faces), process=False)
w.merge_vertices()
welded = dict(faces=len(w.faces), verts=len(w.vertices))

# 2. decimate on welded positions
req = TARGET
for _ in range(8):
    vn, fn = fs.simplify(np.asarray(w.vertices, dtype=np.float32),
                         np.asarray(w.faces, dtype=np.int32), target_count=req)
    if len(fn) <= TARGET:
        break
    req = int(req * TARGET / len(fn)) - 1
d = trimesh.Trimesh(vn, fn, process=False)
d.remove_unreferenced_vertices()
DV = np.asarray(d.vertices, dtype=np.float64)
DF = np.asarray(d.faces)
F = len(DF)

# 3. per-face UV transfer (decimate_roundH.py)
raw = trimesh.Trimesh(V0, np.asarray(m.faces), process=False)
tri = DV[DF]
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
fuv = puv[np.arange(F), dist.argmin(axis=1)]          # (F,2): one UV per face

# 4. weld positions (DV is already welded) -> one copy per (position, uv)
key = {}
NVpos, NUV, posof = [], [], []
OF = np.zeros((F, 3), dtype=np.int64)
for fi in range(F):
    u = tuple(np.round(fuv[fi], 6))
    for k in range(3):
        g = int(DF[fi, k])
        kk = (g, u)
        if kk not in key:
            key[kk] = len(NUV)
            NUV.append(fuv[fi]); posof.append(g)
        OF[fi, k] = key[kk]
posof = np.asarray(posof)
OV = DV[posof]
OUV = np.asarray(NUV)
assert not (OF[:, 0] == OF[:, 1]).any() and not (OF[:, 1] == OF[:, 2]).any()

# 5. smooth normals per welded position + zero-normal repair
fnrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
fnrm /= np.maximum(np.linalg.norm(fnrm, axis=1, keepdims=True), 1e-12)
NP = np.zeros_like(DV)
for k in range(3):
    np.add.at(NP, DF[:, k], fnrm)
ln = np.linalg.norm(NP, axis=1)
bad = ln < 1e-6
NP[~bad] /= ln[~bad, None]
zero_repaired = int(bad.sum())
if zero_repaired:
    good = np.where(~bad)[0]
    _, j = cKDTree(DV[good]).query(DV[bad], k=1)
    NP[bad] = NP[good[j]]
ON = NP[posof]


def build(image):
    mesh = trimesh.Trimesh(OV, OF, vertex_normals=ON, process=False)
    mt = mat.copy()
    mt.baseColorTexture = image
    mesh.visual = trimesh.visual.texture.TextureVisuals(uv=OUV, material=mt, image=image)
    return mesh


def verify(path):
    b = path.read_bytes()
    jl, = struct.unpack_from('<I', b, 12)
    assert b[16:20] == b'JSON', 'chunk 0 is not JSON'
    assert b[20 + jl + 4:20 + jl + 8] == b'BIN\x00', 'chunk 1 is not BIN'
    g = json.loads(b[20:20 + jl])
    prim = g['meshes'][0]['primitives'][0]
    assert 'NORMAL' in prim['attributes'], 'NORMAL missing'
    na = g['accessors'][prim['attributes']['NORMAL']]
    bv = g['bufferViews'][na['bufferView']]
    off = 20 + jl + 8 + bv.get('byteOffset', 0) + na.get('byteOffset', 0)
    N = np.frombuffer(b, '<f4', na['count'] * 3, off).reshape(-1, 3)
    nl = np.linalg.norm(N, axis=1)
    r = trimesh.load(path, force='mesh', process=False)
    return dict(bytes=len(b), json_chunk=True, normal_attr=True, normals=int(na['count']),
                normal_len_min=round(float(nl.min()), 4), normal_len_max=round(float(nl.max()), 4),
                reload_verts=len(r.vertices), reload_faces=len(r.faces),
                tex=list(r.visual.material.baseColorTexture.size))


mid = KIT / 'lantern-post-v2.glb'
pix = KIT / 'lantern-post-v2-pixelated.glb'
build(img).export(mid, file_type='glb')
build(posterize512(img)).export(pix, file_type='glb')
vm, vp = verify(mid), verify(pix)
assert vp['reload_faces'] == F and vp['reload_verts'] == len(OV)

bb = OV.min(axis=0), OV.max(axis=0)
row = dict(signed='Claude Code (Round K) 2026-10-05', src=str(RAW.relative_to(ROOT)),
           dst=str(pix.relative_to(ROOT)), target=TARGET, before=before, welded=welded,
           after=dict(faces=F, welded_verts=len(DV), verts_with_uv_copies=len(OV), requested=req),
           recenter_xz=[round(float(shift[0]), 4), round(float(shift[2]), 4)],
           uv_transfer='per-face medoid of 4 closest-point probes',
           normals='smooth per welded position', zero_normals_repaired=zero_repaired,
           ext_before=[round(float(v), 3) for v in m.bounds[1] - m.bounds[0]],
           ext_after=[round(float(v), 3) for v in bb[1] - bb[0]],
           verify_mid=vm, verify_pixelated=vp)
print(json.dumps(row, indent=1))
log = ROOT / 'scratch/treeqa/roundK/decimate.jsonl'
log.parent.mkdir(parents=True, exist_ok=True)
with open(log, 'a') as f:
    f.write(json.dumps(row) + '\n')
