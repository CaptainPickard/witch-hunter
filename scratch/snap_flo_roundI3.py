#!/usr/bin/env python3
"""Round I3: bramble floaters - SNAP them (rigid translate to touch the main
mass, same rule as decimate_roundI --snap) + normals smooth, in ONE pass."""
import struct, json
from collections import defaultdict
from pathlib import Path
import numpy as np
import trimesh

ROOT = Path('/workspace/witch-hunter')
p = ROOT / 'art-direction/3d/assets/biome_library/wh-bramble-pixelated.glb'

m = trimesh.load(p, force='mesh', process=False)
F = np.asarray(m.faces)
V = np.asarray(m.vertices)
UV = np.asarray(m.visual.uv)[:len(V)]
img = m.visual.material.baseColorTexture
mat = m.visual.material

# components by WELDED position (quantized)
q = np.round(V, 4)
uniq, inv = np.unique(q, axis=0, return_inverse=True)
parent = list(range(len(uniq)))
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]; x = parent[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb: parent[ra] = rb
for f in F:
    union(int(inv[f[0]]), int(inv[f[1]]))
    union(int(inv[f[1]]), int(inv[f[2]]))
comp_of = {i: find(i) for i in range(len(uniq))}
comp_faces = defaultdict(list)
for fi, f in enumerate(F):
    comp_faces[comp_of[int(inv[f[0]])]].append(fi)
# largest = main mass
sizes = {c: sum(1 for _ in v) for c, v in
         [(c, comp_faces[c]) for c in comp_faces]}
main = max(comp_faces, key=lambda c: np.sum(np.linalg.norm(
    np.cross(V[F[comp_faces[c]][:, 1]] - V[F[comp_faces[c]][:, 0]],
             V[F[comp_faces[c]][:, 2]] - V[F[comp_faces[c]][:, 0]]), axis=1)))
main_area = 0.0
for c in comp_faces:
    tri = V[F[comp_faces[c]]]
    main_area += np.sum(np.linalg.norm(np.cross(tri[:,1]-tri[:,0], tri[:,2]-tri[:,0]), axis=1)) if c == main else 0.0
areas = {}
for c, fl in comp_faces.items():
    tri = V[F[fl]]
    areas[c] = float(np.sum(np.linalg.norm(np.cross(tri[:,1]-tri[:,0], tri[:,2]-tri[:,0]), axis=1)))
main = max(areas, key=lambda c: areas[c])

# main mass points (KD tree)
main_tris = V[F[comp_faces[main]]]
main_pts = main_tris.reshape(-1, 3)
from scipy.spatial import cKDTree
t = cKDTree(main_tris_center := tri.mean(axis=1) if False else np.asarray(trimesh.triangles.closest_point(
    main_tris, main_pts.mean(axis=0)[None, :].repeat(1, axis=0)))) if False else None
# use the RAW verts + centers
centers = main_tris.mean(axis=1)
t = cKDTree(centers)

SNAP_MAX = 0.25
n_snapped = 0
offsets = {}
for c in sorted(areas.keys()):
    if c == main: continue
    # if piece within SNAP_MAX of main mass: snap (rigid) else: DELETE? no - snap only
    fl = comp_faces[c]
    pts = V[F[fl]].reshape(-1, 3)
    cdist, ci = t.query(pts.mean(axis=0)[None, :], k=1)
    if cdist[0] <= SNAP_MAX:
        # translate piece so its closest center-line lands on the main triangle center
        target = centers[ci[0]]
        offsets[c] = target - pts.mean(axis=0)
        n_snapped += 1

print('pieces', len(areas), 'main', main, 'area main', round(areas[main], 4),
      '| snapped', n_snapped, 'of', len(areas) - 1)
# apply: move all verts of snapped comps (welded positions)
for c, offv in offsets.items():
    for vi in np.where(np.isin(inv, [v for v in range(len(uniq)) if find(v) == c]))[0]:
        pass
# simpler: per-vertex apply
uniq2 = uniq.copy()
for c, offv in offsets.items():
    members = [v for v in range(len(uniq)) if comp_of.get(v) == c or find(v) == c]
    uniq2[members] += offv
# rebuild V from uniq2 via inv
V2 = uniq2[inv]
# rebuild faces as before (they index V originally per-face; but faces index V (len==3F?))
# current file is INDEXED (V 6817, F 2273): F indexes uniq-space? No: F indexes V.
# We welded in uniq space: V2 = uniq2[inv] gives per-ORIGINAL-VERT positions.
# faces reference original verts; new mesh: weld again by uniq2 quantization:
qq, inv2 = np.unique(np.round(V2, 4), axis=0, return_inverse=True)
F2 = inv2[F].astype(np.int64)
degen = int((F2[:,0]==F2[:,1]).sum() + (F2[:,1]==F2[:,2]).sum() + (F2[:,0]==F2[:,2]).sum())
assert degen == 0, degen
# UV: per original vert (kept)
mesh = trimesh.Trimesh(qq.astype(np.float64), F2, process=False)
# smooth normals
tri2 = mesh.vertices[F2]
fn = np.cross(tri2[:,1]-tri2[:,0], tri2[:,2]-tri2[:,0])
fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12)
NV = np.zeros_like(mesh.vertices)
for k in range(3):
    np.add.at(NV, F2[:, k], fn)
NV /= np.maximum(np.linalg.norm(NV, axis=1, keepdims=True), 1e-12)
mesh.visual = trimesh.visual.texture.TextureVisuals(uv=UV, material=mat, image=img)
mesh.export(p, file_type='glb')

# rewrite header (JSON type) + inject normals manually
d = bytearray(p.read_bytes())
jslen, = struct.unpack_from('<I', d, 12)
g = json.loads(d[20:20+jslen].decode())
je = 20 + jslen
blen, = struct.unpack_from('<I', d, je)
bin_data = bytearray(d[je+8:])
prim = g['meshes'][0]['primitives'][0]
if 'NORMAL' not in prim['attributes']:
    accP = g['accessors'][prim['attributes']['POSITION']]; bvP = g['bufferViews'][accP['bufferView']]
    P = np.frombuffer(bytes(bin_data), dtype='<f4', count=accP['count']*3, offset=bvP['byteOffset']).reshape(accP['count'],3)
    accI = g['accessors'][prim['indices']]; bvI = g['bufferViews'][accI['bufferView']]
    IDX = np.frombuffer(bytes(bin_data), dtype='<u4', count=accI['count'], offset=bvI['byteOffset'])
    FF = IDX.reshape(-1,3)
    tri3 = P[FF]
    fn = np.cross(tri3[:,1]-tri3[:,0], tri3[:,2]-tri3[:,0])
    fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12)
    NV2 = np.zeros_like(P)
    for k in range(3):
        np.add.at(NV2, FF[:, k], fn)
    NV2 /= np.maximum(np.linalg.norm(NV2, axis=1, keepdims=True), 1e-12)
    payload = NV2.astype('<f4').tobytes()
    bv_off = len(bin_data)
    pad = (-bv_off) % 4
    bin_data = bytearray(bytes(bin_data) + b'\x00' * pad + payload)
    bvidx = len(g['bufferViews'])
    g['bufferViews'].append({'buffer': 0, 'byteOffset': bv_off + pad, 'byteLength': len(payload)})
    aid = len(g['accessors'])
    g['accessors'].append({'bufferView': bvidx, 'componentType': 5126, 'count': len(NV2), 'type': 'VEC3'})
    prim['attributes']['NORMAL'] = aid
    g['buffers'][0]['byteLength'] = len(bin_data)
    js = json.dumps(g, separators=(',',':')).encode()
    js = js + b' ' * ((-len(js)) % 4)
    jchunk = struct.pack('<I', len(js)) + b'JSON' + js
    bchunk = struct.pack('<I', len(bin_data)) + b'BIN\x00' + bytes(bin_data)
    total = 12 + len(jchunk) + len(bchunk)
    p.write_bytes(b'glTF' + struct.pack('<II', 2, total) + jchunk + bchunk)
# verify
m3 = trimesh.load(p, force='mesh', process=False)
d3 = p.read_bytes()
jl3, = struct.unpack_from('<I', d3, 12)
g3 = json.loads(d3[20:20+jl3].decode())
N3acc = g3['accessors'][g3['meshes'][0]['primitives'][0]['attributes'].get('NORMAL', 0)] if 'NORMAL' in g3['meshes'][0]['primitives'][0]['attributes'] else None
import subprocess
r = subprocess.run(['python3', 'art-direction/3d/ortho_preview.py', str(p),
                    'scratch/treeqa/roundI-triage/bramble-I3-front.png',
                    'scratch/treeqa/roundI-triage/bramble-I3-side.png'],
                   cwd=str(ROOT), capture_output=True, text=True)
print('bramble I3:', json.dumps({'verts': len(m3.vertices), 'faces': len(m3.faces),
    'snapped': n_snapped, 'ortho': bool(r.stdout.strip())}))