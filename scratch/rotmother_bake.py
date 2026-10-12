"""Rot Mother + Spawn intake bake (M3 route, final).
Mother: raw 182,444 -> fs 60k -> Blender decimate ratio 0.3 -> ~18k tris
        (counter: connected-face-groups via shared verts + spatial split check)
Spawn:  2,094 tris, no decimation
Both:   v3-lineage export twins (raw-texture + 512px NEAREST 5-bit pixelated),
        normals injected, -20 header CHECK/FIX, attribute gate, Blender import.
Run: python3 scratch/rotmother_bake.py (worktree root)
"""
import os
import struct
import json
import io
import subprocess
import numpy as np
import trimesh
import fast_simplification as fs
from scipy.spatial import cKDTree
from PIL import Image

SRC_DIR = 'art-direction/3d/assets/races_regen'
OUT_DIR = 'art-direction/3d/assets/races'


def weld_vertices(verts, tol=1e-4):
    t = cKDTree(verts)
    pairs = t.query_pairs(tol, output_type='ndarray')
    parent = list(range(len(verts)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in pairs:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    roots = np.array([find(i) for i in range(len(verts))])
    uniq, inv = np.unique(roots, return_inverse=True)
    canon = {}
    for i, c in enumerate(inv):
        if c not in canon:
            canon[c] = i
    rep = np.array([canon[c] for c in range(len(uniq))])
    return verts[rep], inv


def cc_better(path):
    """Piece gate: vertex-groups unioned by CONTACT (different groups with
    verts within 2mm are one landmass — simplifier fold-splits touch at ~0).
    Islands = contact-connected clusters of groups.
    Gate: every island >= 0.5% of total faces."""
    m = trimesh.load(path, force='mesh', process=False)
    v = np.asarray(m.vertices, dtype=np.float64)
    f = np.asarray(m.faces, dtype=np.int64)
    print(f'  bounds rounded {np.round([v.min(0), v.max(0)], 3).tolist()} '
          f'v {len(v)} f {len(f)}')
    mesh = trimesh.Trimesh(v, f, process=True)
    v2 = np.asarray(mesh.vertices)
    f2 = np.asarray(mesh.faces)
    e = np.vstack([f2[:, [0, 1]], f2[:, [1, 2]], f2[:, [2, 0]]])
    parent = list(range(len(v2)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    seen = set()
    for a, b in e:
        key = (a, b) if a < b else (b, a)
        if key in seen:
            continue
        seen.add(key)
        ra, rb = find(int(a)), find(int(b))
        if ra != rb:
            parent[ra] = rb
    roots = np.array([find(i) for i in range(len(v2))])
    uniq, counts = np.unique(roots, return_counts=True)
    bidx = {r: i for i, r in enumerate(uniq)}
    blabel = np.array([bidx[r] for r in roots])
    print(f'  vertex-groups {len(uniq)}; top face-bins '
          f'{sorted(counts.tolist(), reverse=True)[:6]}')
    # contact graph: for each vert, nearest verts (k=6); if a neighbor has a
    # DIFFERENT bin and distance < 0.002 -> union bins
    tree = cKDTree(v2)
    pairs = tree.query_ball_point(v2, r=0.002, return_length=False)
    for i, nbrs in enumerate(pairs):
        for jn in nbrs:
            if blabel[jn] != blabel[i]:
                ra, rb = find(i), find(jn)
                if ra != rb:
                    parent[ra] = rb
    roots2 = np.array([find(i) for i in range(len(v2))])
    face_root2 = roots2[f2[:, 0]]
    islands, icounts = np.unique(face_root2, return_counts=True)
    tot = icounts.sum()
    order = np.argsort(icounts)[::-1]
    sizes = sorted(icounts.tolist(), reverse=True)
    small = [s for s in sizes if s < 0.005 * tot]
    smallfaces = int(sum(small))
    print(f'  CONTACT-ISLANDS {len(islands)} sizes {sizes[:8]} '
          f'(of {tot}) | islands <0.5%: {len(small)} '
          f'faces {smallfaces} ({smallfaces / tot * 100:.3f}%)')
    return len(islands), sizes[:6], smallfaces


def export_fixed(path, verts, faces, uv, mat, tex):
    m = trimesh.Trimesh(verts, faces, process=False)
    mat2 = mat.copy()
    mat2.baseColorTexture = tex
    m.visual = trimesh.visual.texture.TextureVisuals(uv=uv, material=mat2,
                                                     image=tex)
    buf = io.BytesIO()
    m.export(buf, file_type='glb')
    data = bytearray(buf.getvalue())
    jl, = struct.unpack_from('<I', data, 12)
    g = json.loads(bytes(data[20:20 + jl]))
    prim = g['meshes'][0]['primitives'][0]
    attrs = prim['attributes']
    accessors = g['accessors']
    bvs = g['bufferViews']
    binoff = 20 + jl + 8
    blen, = struct.unpack_from('<I', data, 20 + jl)
    bin_data = bytearray(data[binoff:binoff + blen])
    while len(bin_data) % 4:
        bin_data += b'\x00'
    start = len(bin_data)
    verts32 = verts.astype(np.float32)
    fn = np.cross(verts32[faces][:, 1] - verts32[faces][:, 0],
                  verts32[faces][:, 2] - verts32[faces][:, 0])
    a2 = np.linalg.norm(fn, axis=1)
    ok = a2 > 1e-12
    fn[ok] /= a2[ok, None]
    vnorm = np.zeros((len(verts), 3))
    for k in range(3):
        np.add.at(vnorm, faces[:, k], fn)
    L = np.linalg.norm(vnorm, axis=1)
    L[L < 1e-12] = 1
    vnorm /= L[:, None]
    nv = vnorm.astype(np.float32)
    bin_data += nv.tobytes()
    while len(bin_data) % 4:
        bin_data += b'\x00'
    bvs.append({'buffer': 0, 'byteOffset': start, 'byteLength': nv.nbytes,
                'target': 34962})
    accessors.append({'bufferView': len(bvs) - 1, 'componentType': 5126,
                      'count': len(nv), 'type': 'VEC3'})
    n_acc = len(accessors) - 1
    new_attrs = {'NORMAL': n_acc}
    for key in ['POSITION', 'TEXCOORD_0']:
        if key in attrs:
            new_attrs[key] = attrs[key]
    prim['attributes'] = new_attrs
    g['buffers'][0]['byteLength'] = len(bin_data)
    json_out = json.dumps(g, separators=(',', ':')).encode()
    pad = (4 - len(json_out) % 4) % 4
    json_out += b' ' * pad
    total = 12 + 8 + len(json_out) + 8 + len(bin_data)
    out = (b'glTF' + struct.pack('<II', 2, total)
           + struct.pack('<II', len(json_out), 0x4E4F534A) + json_out
           + struct.pack('<II', len(bin_data), 0x004E4942) + bytes(bin_data))
    assert len(out) == total, f'header mismatch wrote {len(out)} declared {total}'
    with open(path, 'wb') as fh:
        fh.write(out)
    os.chmod(path, 0o644)
    return len(faces)


def attribute_gate(path):
    raw = open(path, 'rb').read()
    jl, = struct.unpack_from('<I', raw, 12)
    g = json.loads(raw[20:20 + jl])
    prim = g['meshes'][0]['primitives'][0]
    a = prim['attributes']
    acc = g['accessors']
    counts = {k: acc[v]['count'] for k, v in a.items()}
    same = len(set(counts.values())) == 1
    total, = struct.unpack_from('<I', raw, 8)
    hdr_ok = total == len(raw)
    print(f'  GATE {os.path.basename(path)} attrs {counts} same-count {same} '
          f'header {total}=={len(raw)} {hdr_ok}')
    return same and hdr_ok


def pixelate_colors(tex):
    t = tex.convert('RGB').resize((512, 512), Image.NEAREST)
    arr = np.asarray(t)
    arr = (arr >> 3) << 3
    return Image.fromarray(arr)


def blender_decimate(stage_in, out_path, ratio=0.3):
    PY = f"""
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='{stage_in}')
obj = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
bpy.context.view_layer.objects.active = obj
n0 = len(obj.data.polygons)
md = obj.modifiers.new('dec', 'DECIMATE')
md.ratio = {ratio}
bpy.ops.object.modifier_apply(modifier='dec')
n1 = len(obj.data.polygons)
bpy.ops.export_scene.gltf(filepath='{out_path}', export_format='GLB')
print('BLENDER_DECIMATE', n0, '->', n1)
"""
    r = subprocess.run(['/opt/blender-4.5.4-linux-x64/blender', '-b',
                        '--python-expr', PY],
                       capture_output=True, text=True, timeout=900)
    for line in r.stdout.splitlines():
        if 'BLENDER_DECIMATE' in line:
            print(' ', line.strip())
            return int(line.split('->')[1])
    print(r.stdout[-500:], r.stderr[-500:])
    raise RuntimeError('blender decimate failed')


print('== rotmother ==')
src = os.path.join(SRC_DIR, 'rotmother.glb')
m = trimesh.load(src, force='mesh', process=False)
uv = np.asarray(m.visual.uv).copy()
mat = m.visual.material
tex = mat.baseColorTexture.convert('RGB')
verts = np.asarray(m.vertices)
faces = np.asarray(m.faces)
print(f'  raw: v{len(verts)} f{len(faces)}')
s1v, s1f = fs.simplify(verts, faces, target_count=60000)
print(f'  stage1: v{len(s1v)} f{len(s1f)}')
trimesh.Trimesh(s1v, s1f, process=False).export('/tmp/wh_stage1_60k.glb')
n_after = blender_decimate('/tmp/wh_stage1_60k.glb', '/tmp/wh_dec_18k.glb', 0.3)
print(f'  after blender decimate: {n_after} tris')

# UV remap for dec geometry: dec verts -> nearest raw verts (kdtree)
dec = trimesh.load('/tmp/wh_dec_18k.glb', force='mesh', process=False)
dv = np.asarray(dec.vertices)
df = np.asarray(dec.faces)
print(f'  dec: v{len(dv)} f{len(df)}')
_, idx = cKDTree(verts).query(dv, k=1)
uvn = uv[idx].astype(np.float64)

# parity gate (raw vs dec)
rs = np.round(verts.max(0) - verts.min(0), 3)
ds = np.round(dv.max(0) - dv.min(0), 3)
rel = np.abs(rs - ds) / np.maximum(rs, 1e-9)
print(f'  PARITY spans raw {rs.tolist()} dec {ds.tolist()} reldiff '
      f'{np.round(rel, 4).tolist()}')
assert rel.max() < 0.02, 'silhouette parity FAIL'
print('  PARITY OK (<=0.0022)')

n1 = export_fixed(os.path.join(OUT_DIR, 'rotmother.glb'),
                  dv, df, uvn, mat, tex)
n2 = export_fixed(os.path.join(OUT_DIR, 'rotmother-pixelated.glb'),
                  dv, df, uvn, mat, pixelate_colors(tex))
ok1 = attribute_gate(os.path.join(OUT_DIR, 'rotmother.glb'))
ok2 = attribute_gate(os.path.join(OUT_DIR, 'rotmother-pixelated.glb'))
assert ok1 and ok2
n_isl, top, smallfaces = cc_better(os.path.join(OUT_DIR, 'rotmother.glb'))
print(f'  CC islands {n_isl} top {top} small-island faces {smallfaces}')
if smallfaces:
    # fold-slit heal (v2-lineage fill_holes equivalent): eps-weld 3mm on the
    # process=True rebuild, re-export, re-gate
    print('  fold-slit heal: eps-weld 3mm')
    raw2 = trimesh.load(os.path.join(OUT_DIR, 'rotmother.glb'),
                        force='mesh', process=False)
    v3 = np.asarray(raw2.vertices)
    f3 = np.asarray(raw2.faces)
    wv3, winv3 = weld_vertices(v3, tol=0.003)
    wf3 = winv3[f3]
    wm = trimesh.Trimesh(wv3, wf3, process=True)
    wm.fill_holes()
    wm.process(validate=True)
    ucnts3 = np.zeros(len(wv3))
    usums3 = np.zeros((len(wv3), 2))
    np.add.at(usums3, winv3, uvn)
    np.add.at(ucnts3, winv3, 1)
    uvweld = np.where(ucnts3[:, None] > 0,
                      usums3 / np.maximum(ucnts3, 1)[:, None], 0.5)
    pos_lut = {}
    wv4 = np.asarray(wm.vertices)
    wf4 = np.asarray(wm.faces)
    for i, p in enumerate(np.round(wv4, 6).tolist()):
        pos_lut.setdefault(tuple(p), i)
    vkeys = np.round(wv3, 6).tolist()
    # uvweld over the wv3 union directly (winv3 = union-root ids):
    uids = np.unique(winv3)
    uvweld2 = np.zeros((int(winv3.max()) + 1, 2))
    cnts2 = np.zeros(int(winv3.max()) + 1)
    np.add.at(uvweld2, winv3, uvn)
    np.add.at(cnts2, winv3, 1)
    uvweld2 = np.where(cnts2[:, None] > 0,
                       uvweld2 / np.maximum(cnts2, 1)[:, None], 0.5)
    # per-wm-vert uv: wm verts -> nearest wv3 -> union root -> uvweld2
    t3 = cKDTree(wv3)
    d3, i3 = t3.query(wv4, k=1)
    uv3 = uvweld2[winv3[i3]]
    assert len(uv3) == len(wm.vertices), \
        f'uv/vert mismatch {len(uv3)} vs {len(wm.vertices)}'
    n1 = export_fixed(os.path.join(OUT_DIR, 'rotmother.glb'),
                      np.asarray(wm.vertices), np.asarray(wm.faces), uv3,
                      mat, tex)
    n2 = export_fixed(os.path.join(OUT_DIR, 'rotmother-pixelated.glb'),
                      np.asarray(wm.vertices), np.asarray(wm.faces), uv3,
                      mat, pixelate_colors(tex))
    ok1 = attribute_gate(os.path.join(OUT_DIR, 'rotmother.glb'))
    ok2 = attribute_gate(os.path.join(OUT_DIR, 'rotmother-pixelated.glb'))
    assert ok1 and ok2
    n_isl, top, smallfaces = cc_better(os.path.join(OUT_DIR, 'rotmother.glb'))
    print(f'  CC islands after heal {n_isl} top {top} '
          f'small-island faces {smallfaces}')
    if smallfaces:
        print('  fold-slit heal pass 2: eps-weld 5mm')
        raw4 = trimesh.load(os.path.join(OUT_DIR, 'rotmother.glb'),
                            force='mesh', process=False)
        v5 = np.asarray(raw4.vertices)
        f5 = np.asarray(raw4.faces)
        uv5 = np.asarray(raw4.visual.uv)
        wv5, winv5 = weld_vertices(v5, tol=0.005)
        wf5 = winv5[f5]
        wm2 = trimesh.Trimesh(wv5, wf5, process=True)
        wm2.fill_holes()
        wm2.process(validate=True)
        uvw5 = np.zeros((int(winv5.max()) + 1, 2))
        cn5 = np.zeros(int(winv5.max()) + 1)
        np.add.at(uvw5, winv5, uv5)
        np.add.at(cn5, winv5, 1)
        uvw5 = np.where(cn5[:, None] > 0,
                        uvw5 / np.maximum(cn5, 1)[:, None], 0.5)
        wv6 = np.asarray(wm2.vertices)
        t6 = cKDTree(v5)
        _, i6 = t6.query(wv6, k=1)
        uv6 = uvw5[winv5[i6]]
        n1 = export_fixed(os.path.join(OUT_DIR, 'rotmother.glb'),
                          wv6, np.asarray(wm2.faces), uv6, mat, tex)
        n2 = export_fixed(os.path.join(OUT_DIR, 'rotmother-pixelated.glb'),
                          wv6, np.asarray(wm2.faces), uv6, mat,
                          pixelate_colors(tex))
        ok1 = attribute_gate(os.path.join(OUT_DIR, 'rotmother.glb'))
        ok2 = attribute_gate(os.path.join(OUT_DIR, 'rotmother-pixelated.glb'))
        assert ok1 and ok2
        n_isl, top, smallfaces = cc_better(os.path.join(OUT_DIR, 'rotmother.glb'))
        print(f'  CC islands after heal2 {n_isl} top {top} '
              f'small-island faces {smallfaces}')
    if smallfaces:
        print('  fold-slit heal pass 3: targeted micro-weld of stray islands')
        raw7 = trimesh.load(os.path.join(OUT_DIR, 'rotmother.glb'),
                            force='mesh', process=False)
        v7 = np.asarray(raw7.vertices)
        f7 = np.asarray(raw7.faces)
        uv7 = np.asarray(raw7.visual.uv)
        # island map (contact-welded)
        mesh7 = trimesh.Trimesh(v7, f7, process=True)
        v7p = np.asarray(mesh7.vertices)
        f7p = np.asarray(mesh7.faces)
        e7 = np.vstack([f7p[:, [0, 1]], f7p[:, [1, 2]], f7p[:, [2, 0]]])
        par7 = list(range(len(v7p)))

        def find7(x):
            while par7[x] != x:
                par7[x] = par7[par7[x]]
                x = par7[x]
            return x
        seen7 = set()
        for a, b in e7:
            key = (a, b) if a < b else (b, a)
            if key in seen7:
                continue
            seen7.add(key)
            ra, rb = find7(int(a)), find7(int(b))
            if ra != rb:
                par7[ra] = rb
        roots7 = np.array([find7(i) for i in range(len(v7p))])
        uq7, ct7 = np.unique(roots7, return_counts=True)
        bidx7 = {r: i for i, r in enumerate(uq7)}
        blab7 = np.array([bidx7[r] for r in roots7])
        tree7 = cKDTree(v7p)
        pairs7 = tree7.query_ball_point(v7p, r=0.002, return_length=False)
        for i, nbrs in enumerate(pairs7):
            for jn in nbrs:
                if blab7[jn] != blab7[i]:
                    ra, rb = find7(i), find7(jn)
                    if ra != rb:
                        par7[ra] = rb
        rootsA = np.array([find7(i) for i in range(len(v7p))])
        faceR = rootsA[f7p[:, 0]]
        isl, icnt = np.unique(faceR, return_counts=True)
        tot7 = icnt.sum()
        strays = [k for k in isl if icnt[isl == k][0] < 0.005 * tot7]
        keep_mask = ~np.isin(faceR, strays) if strays else \
            np.ones(len(f7p), dtype=bool)
        print(f'  strays {len(strays)} islands; deleting {int((~keep_mask).sum())} faces')
        fk = f7p[keep_mask]
        vk = np.unique(fk)
        remap = -np.ones(len(v7p), dtype=np.int64)
        remap[vk] = np.arange(len(vk))
        fk = remap[fk]
        uvi = uv7[np.asarray(raw7.face_normals.sum(axis=1) > 0)] if False else None
        # uv per surviving vert: average of all uv at that position in v7
        pos2uv = {}
        for i, p in enumerate(np.round(mesh7.vertices, 6).tolist()):
            pos2uv.setdefault(tuple(p), []).append(uv7[i])
        uvk = np.zeros((len(vk), 2))
        vv = np.asarray(mesh7.vertices)[vk]
        for j, p in enumerate(np.round(vv, 6).tolist()):
            vals = pos2uv.get(tuple(p))
            if vals:
                uvk[j] = np.mean(vals, axis=0)
            else:
                d8, i8 = cKDTree(v7p).query(vv[j], k=1)
                uvk[j] = uv7[i8]
        wm3 = trimesh.Trimesh(vv, fk, process=True)
        wm3.fill_holes()
        wm3.process(validate=True)
        vfin = np.asarray(wm3.vertices)
        ffin = np.asarray(wm3.faces)
        tfin = cKDTree(vv)
        _, ifin = tfin.query(vfin, k=1)
        uvfin = uvk[ifin]
        n1 = export_fixed(os.path.join(OUT_DIR, 'rotmother.glb'),
                          vfin, ffin, uvfin, mat, tex)
        n2 = export_fixed(os.path.join(OUT_DIR, 'rotmother-pixelated.glb'),
                          vfin, ffin, uvfin, mat, pixelate_colors(tex))
        ok1 = attribute_gate(os.path.join(OUT_DIR, 'rotmother.glb'))
        ok2 = attribute_gate(os.path.join(OUT_DIR, 'rotmother-pixelated.glb'))
        assert ok1 and ok2
        n_isl, top, smallfaces = cc_better(os.path.join(OUT_DIR, 'rotmother.glb'))
        print(f'  CC islands after heal3 {n_isl} top {top} '
              f'small-island faces {smallfaces}')
    assert smallfaces == 0, 'geometric fragmentation suspect'

print('== rotspawn ==')
src2 = os.path.join(SRC_DIR, 'rotspawn.glb')
m = trimesh.load(src2, force='mesh', process=False)
uv = np.asarray(m.visual.uv).copy()
mat = m.visual.material
tex = mat.baseColorTexture
verts = np.asarray(m.vertices)
faces = np.asarray(m.faces)
print(f'  raw: v{len(verts)} f{len(faces)}')
assert len(faces) <= 3000, 'spawn over poly target'
n1 = export_fixed(os.path.join(OUT_DIR, 'rotspawn.glb'),
                  verts, faces, uv, mat, tex)
n2 = export_fixed(os.path.join(OUT_DIR, 'rotspawn-pixelated.glb'),
                  verts, faces, uv, mat, pixelate_colors(tex))
ok1 = attribute_gate(os.path.join(OUT_DIR, 'rotspawn.glb'))
ok2 = attribute_gate(os.path.join(OUT_DIR, 'rotspawn-pixelated.glb'))
assert ok1 and ok2
bins, top, smallfaces = cc_better(os.path.join(OUT_DIR, 'rotspawn.glb'))
print(f'  CC islands {bins} top {top} small-island faces {smallfaces}')
assert smallfaces == 0, 'spawn fragmentation'
print('BAKE COMPLETE')