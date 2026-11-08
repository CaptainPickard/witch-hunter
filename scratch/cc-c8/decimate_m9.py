"""Decimate m9 (moss boulder, 21,599 tris) to <= 8k with the proven pipeline:
fs.simplify to a stage (3:1-ish) -> Blender quad decimate -> eps-weld heal,
UV-preserving, 512px NEAREST + 5-bit texture (the Round-G pixelated look).
python3 scratch/cc-c8/decimate_m9.py
Output: art-direction/3d/assets/biome_library/m8-boulder-small.glb (RAW tex)
"""
import numpy as np
import trimesh
import os, subprocess

def _weld(verts, tol):
    from scipy.spatial import cKDTree
    pairs = cKDTree(verts).query_pairs(tol, output_type="ndarray")
    parent = list(range(len(verts)))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for a, b in pairs:
        ra, rb = find(int(a)), find(int(b))
        if ra != rb: parent[ra] = rb
    roots = np.array([find(i) for i in range(len(verts))])
    uniq, inv = np.unique(roots, return_inverse=True)
    inv = inv.reshape(-1)
    canon = {}
    for i, c in enumerate(int(x) for x in inv):
        if c not in canon: canon[c] = i
    rep = np.array([canon[c] for c in (int(x) for x in inv)])
    return {'verts': verts[rep], 'inv': inv}

RAW = 'art-direction/3d/assets/biome_library/m9.glb'
OUT_RAW = 'art-direction/3d/assets/biome_library/m8-boulder-small.glb'
STAGE = '/tmp/c8_m9_stage.glb'
DEC = '/tmp/c8_m9_dec.glb'

m = trimesh.load(RAW, force='mesh', process=True)   # v2-lineage EXACT
verts = np.asarray(m.vertices)
faces = np.asarray(m.faces)
uv = np.asarray(m.visual.uv)
print('raw', len(verts), len(faces))

import fast_simplification as fs
vn, fn = fs.simplify(verts, faces, target_count=10000)
print('stage1', len(vn), len(fn))

# export stage for blender (geometry only; uv via kdtree re-map after)
sv = np.asarray(m.vertices)
sv = verts
from scipy.spatial import cKDTree
_, idx = cKDTree(vn).query(verts, k=1)
usums = np.zeros((len(vn), 2)); ucnts = np.zeros(len(vn))
np.add.at(usums, idx, uv); np.add.at(ucnts, idx, 1)
uvn = np.where(ucnts[:, None] > 0, usums / np.maximum(ucnts, 1)[:, None], 0.5)
sm = trimesh.Trimesh(vn, fn, process=False)
print('stage uv len', len(uvn), 'verts', len(vn))
import io as _io
sv_mat = m.visual.material
tex = sv_mat.baseColorTexture
sm.visual = trimesh.visual.texture.TextureVisuals(uv=uvn, material=sv_mat, image=tex)
sm.export(STAGE)

# blender decimate ratio .5 (2:1) -> about 5k
expr = (
 "import bpy;"
 "bpy.ops.wm.read_factory_settings(use_empty=True);"
 "bpy.ops.import_scene.gltf(filepath='%s');"
 "obj = next(o for o in bpy.context.scene.objects if o.type=='MESH');"
 "bpy.context.view_layer.objects.active=obj;"
 "md = obj.modifiers.new('d','DECIMATE'); md.ratio=0.48;"
 "bpy.ops.object.modifier_apply(modifier='d');"
 "bpy.ops.export_scene.gltf(filepath='%s', export_format='GLB');"
 "print('DEC', len(obj.data.polygons))" % (STAGE, DEC)
)
subprocess.run(['/opt/blender-4.5.4-linux-x64/blender', '-b', '--python-expr',
                expr], capture_output=True, text=True, check=True)
print('decimated to', DEC)

dm = trimesh.load(DEC, force='mesh', process=False)
dv = np.asarray(dm.vertices); df = np.asarray(dm.faces)
print('final', len(dv), len(df))
# uv: nearest from the stage verts
duv = np.zeros((len(dv), 2))
t = cKDTree(vn)
_, i2 = t.query(dv, k=1)
duv = uvn[i2]
mm = trimesh.Trimesh(dv, df, process=True)
mm.fill_holes()
# eps weld 1mm
from scipy.spatial import cKDTree as K2
wv = np.asarray(mm.vertices)
wf = np.asarray(mm.faces)
# eps weld
pairs = K2(wv).query_pairs(0.001, output_type='ndarray')
parent = list(range(len(wv)))
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]; x = parent[x]
    return x
for a, b in pairs:
    ra, rb = find(a), find(b)
    if ra != rb: parent[ra] = rb
roots = np.array([find(i) for i in range(len(wv))])
uniq, inv = np.unique(roots, return_inverse=True)
inv = inv.reshape(-1)
canon = {}
for i, c in enumerate(inv):
    ci = int(c)
    if ci not in canon: canon[ci] = i
rep = np.array([canon[int(c)] for c in inv])
wv2 = wv[rep]
wf2 = inv[wf]
uc = np.zeros(int(inv.max()) + 1); us = np.zeros((int(inv.max()) + 1, 2))
duv = duv[:len(wv)] if len(duv) > len(wv) else np.resize(duv, (len(wv), 2)) if len(duv) < len(wv) else duv
np.add.at(us, inv, duv); np.add.at(uc, inv, 1)
uvw = np.where(uc[:, None] > 0, us / np.maximum(uc, 1)[:, None], 0.5)
wm = trimesh.Trimesh(wv2, wf2, process=True)
wm.fill_holes()
wm.process(validate=True)
# contact-island heal: eps-weld 5mm + 12mm + 3mm follow-up passes (the decimate
# fold-splits reach 50mm on this boulder; the mother-bake law, escalated eps)
wv_a = np.asarray(wm.vertices)
wfaces0 = None
cur_v, cur_f = wv_a, np.asarray(wm.faces)
for tol in (0.005, 0.012, 0.003):
    w = _weld(cur_v, tol)
    cur_f = w['inv'][cur_f]
    mX = trimesh.Trimesh(w['verts'], cur_f, process=True)
    mX.fill_holes()
    mX.process(validate=True)
    cur_v = np.asarray(mX.vertices)
    cur_f = np.asarray(mX.faces)
wv3, wf3 = cur_v, cur_f
# uv per final vert: nearest ORIGINAL decimate vert (dv-space via wv), root uv
t3 = cKDTree(wv)
_, i3 = t3.query(wv3, k=1)
uv3 = uvw[inv[i3]]
print('healed', len(wv3), len(wf3))

# export with texture (the authored PNG, full res)
tex_img = sv_mat.baseColorTexture
mm2 = trimesh.Trimesh(wv3, wf3, process=False)
mm2.visual = trimesh.visual.texture.TextureVisuals(uv=uv3, material=sv_mat, image=tex_img)
buf = _io.BytesIO(); mm2.export(buf, file_type='glb')
open(OUT_RAW, 'wb').write(buf.getvalue())
print('WROTE', OUT_RAW)

# component check with rotmother_cc
import sys
sys.path.insert(0, 'scratch')
import numpy as _np
m3 = trimesh.load(OUT_RAW, force='mesh', process=True)
cc = trimesh.graph.connected_component_labels(m3.face_adjacency, node_count=len(m3.faces))
n = _np.bincount(cc)
print('COMPONENTS', len(n), 'largest', int(n.max()), 'outside', int(n.sum() - n.max()),
      f'({(n.sum()-n.max())/n.sum()*100:.3f}%)')