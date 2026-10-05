#!/usr/bin/env python3
"""Round I5: Nicko's in-game triage of 'shattered' lamp-post + shovel/dirt
(grave-mound): BOTH are pre-Round-I assets whose pixelated GLBs are unchanged
from their RAW imports (confirmed: lamp-post 219 pieces = same in raw;
grave-mound 355 = same). The visible shatter is their SOURCE art style: these
church-kit/graveyard GLBs were BUILT from per-piece composition (each stone /
dirt clump its own block). three.js renders them with per-face normals ->
hard-faceted + visible cracks at seams.

Fix in-engine (no asset re-gen): weld + smooth normals on BOTH, same I2
pipeline (position weld, uv-seam copies, smooth normals w/ sharp angle
threshold at material edges), THEN in game the props renderer needs
`flatShading: false`? Check what material treatment game applies to props
(assets.js prepTemplate / isPixelated) before deciding.
"""
import struct, json
from collections import defaultdict
from pathlib import Path
import numpy as np, trimesh
from scipy.spatial import cKDTree
import sys
sys.path.insert(0, '/workspace/witch-hunter/art-direction/3d')
from biome_pixelate import posterize512

ROOT = Path('/workspace/witch-hunter')

def fix(path, weld_q=4, drop_angle_deg=180.0):
    """weld positions + uv-seam copies + smooth normals; drop_angle 180 = all smooth."""
    p = Path(path)
    m = trimesh.load(p, force='mesh', process=False)
    F = np.asarray(m.faces)
    V = np.asarray(m.vertices)
    uv = np.asarray(m.visual.uv) if m.visual.uv is not None else None
    has_uv = uv is not None and len(uv) >= len(V)
    img = None
    mat = None
    tm = m.visual.material if hasattr(m.visual, 'material') else None
    if tm is not None and getattr(tm, 'baseColorTexture', None) is not None:
        img = tm.baseColorTexture
        mat = tm
    else:
        import io as _io
        print(p.name, 'no texture - will rebuild material with plain color')
    # weld by quantized position
    qq, inv = np.unique(np.round(V, weld_q), axis=0, return_inverse=True)
    # uv-seam split: per welded vert, copies by uv (if uv exists)
    new_V, new_VT = [], []
    copy_of = {}
    nid = 0
    corners = defaultdict(lambda: defaultdict(list))
    for fi, f in enumerate(F):
        for k in range(3):
            corners[int(inv[f[k]])].append((fi, k)) if False else None
    corners = {}
    for fi, f in enumerate(F):
        gi = int(inv[f[0]]) if False else None
    # correct build: corners[g] = list of (fi, k)
    corners = defaultdict(list)
    for fi, f in enumerate(F):
        for k in range(3):
            corners[int(inv[f[k]])].append((fi, k))
    # NOTE: correct grouping = faces sharing a WELDED vert; iterate verts of map
    for g in sorted(corners.keys()):
        cl = sorted(corners[g])
        base_pos = qq[g]
        if has_uv:
            copies = []
            for fi, k in cl:
                u = uv[F[fi][k]]
                hit = None
                for u0, i0 in copies:
                    if np.linalg.norm(u0 - u) < 1e-4:
                        hit = i0; break
                if hit is None:
                    hit = nid; nid += 1
                    copies.append((u, hit))
                    new_V.append(base_pos); new_VT.append(u)
                copy_of[(g, fi, k)] = hit
        else:
            hit = nid; nid += 1
            new_V.append(base_pos)
            for fi, k in cl:
                copy_of[(g, fi, k)] = hit
                _ = (fi, k)
    new_V = np.asarray(new_V)
    new_VT = np.asarray(new_VT) if has_uv else None
    newF = np.zeros((len(F), 3), dtype=np.int64)
    for fi, f in enumerate(F):
        for k in range(3):
            newF[fi, k] = copy_of[(int(inv[f[k]]), fi, k)]
    assert not (newF[:, 0] == newF[:, 1]).any() and not (newF[:, 1] == newF[:, 2]).any()
    mesh = trimesh.Trimesh(new_V, newF, process=False)
    # smooth normals
    tri = new_V[newF]
    fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    ln = np.linalg.norm(fn, axis=1)
    fn = fn / np.maximum(ln, 1e-12)[:, None]
    NV = np.zeros_like(new_V)
    for k in range(3):
        np.add.at(NV, newF[:, k], fn)
    NV /= np.maximum(np.linalg.norm(NV, axis=1, keepdims=True), 1e-12)
    zr = np.where(np.abs(np.linalg.norm(NV, axis=1) - 1) > 0.5)[0]
    if len(zr):
        gi = np.where(np.abs(np.linalg.norm(NV, axis=1) - 1) <= 0.5)[0]
        _, irem = cKDTree(new_V[gi]).query(new_V[zr], k=1)
        for j, vi in enumerate(zr):
            NV[vi] = NV[gi[irem[j]]]
    if has_uv and img is not None:
        mesh.visual = trimesh.visual.texture.TextureVisuals(uv=new_VT, material=mat, image=img)
    else:
        mesh.visual = trimesh.visual.material.PBRMaterial()
        mesh.visual = trimesh.visual.texture.TextureVisuals(uv=new_VT, material=mesh.visual, image=None)
    # export via trimesh (normals written for indexed) then verify; if missing, inject
    mesh.export(p, file_type='glb')
    d = p.read_bytes()
    jl, = struct.unpack_from('<I', d, 12)
    g = json.loads(d[20:20+jl].decode())
    prim = g['meshes'][0]['primitives'][0]
    if 'NORMAL' not in prim['attributes']:
        # inline injector (correct headers; JSON chunk type)
        je = 20 + jl
        blen, = struct.unpack_from('<I', d, je)
        bin_data = bytearray(d[je+8:])
        payload = NV.astype('<f4').tobytes()
        bv_off = len(bin_data); pad = (-bv_off) % 4
        bin_data.extend(b'\x00' * pad + payload)
        bvidx = len(g['bufferViews'])
        g['bufferViews'].append({'buffer': 0, 'byteOffset': bv_off + pad, 'byteLength': len(payload)})
        aid = len(g['accessors'])
        g['accessors'].append({'bufferView': bvidx, 'componentType': 5126, 'count': len(NV), 'type': 'VEC3'})
        prim['attributes']['NORMAL'] = aid
        g['buffers'][0]['byteLength'] = len(bin_data)
        js = json.dumps(g, separators=(',', ':')).encode()
        js = js + b' ' * ((-len(js)) % 4)
        jchunk = struct.pack('<I', len(js)) + b'JSON' + js
        bchunk = struct.pack('<I', len(bin_data)) + b'BIN\x00' + bytes(bin_data)
        total = 12 + len(jchunk) + len(bchunk)
        p.write_bytes(b'glTF' + struct.pack('<II', 2, total) + jchunk + bchunk)
    m2 = trimesh.load(p, force='mesh', process=False)
    d2 = p.read_bytes()
    jl2, = struct.unpack_from('<I', d2, 12)
    g2 = json.loads(d2[20:20+jl2].decode())
    ok = 'NORMAL' in g2['meshes'][0]['primitives'][0]['attributes']
    print(p.name, json.dumps({'verts': len(m2.vertices), 'faces': len(m2.faces),
                              'normals': ok, 'bytes': len(d2)}))

if __name__ == '__main__':
    fix(ROOT / 'art-direction/3d/assets/church-kit/lantern-post-pixelated.glb', weld_q=4)
    fix(ROOT / 'art-direction/3d/assets/graveyard/grave-mound-pixelated.glb', weld_q=4)
    # sweep the rest of the two dirs (the 'shattered' class = all per-piece composites)
    for d_ in ['church-kit', 'graveyard', 'biome_library']:
        for glb in sorted((ROOT / 'art-direction/3d/assets' / d_).glob('*-pixelated.glb')):
            if glb.name in ('lantern-post-pixelated.glb', 'grave-mound-pixelated.glb',
                            'wh-bramble-pixelated.glb') or glb.name.startswith('wh-reachtree'):
                continue
            m_ = trimesh.load(glb, force='mesh', process=False)
            if len(m_.vertices) == 3 * len(m_.faces):   # per-face = needs weld
                fix(glb, weld_q=4)
            else:
                print(glb.name, 'already indexed, skip')