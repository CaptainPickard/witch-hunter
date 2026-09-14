#!/usr/bin/env python3
"""Regen post-pipeline v2: MINIMAL intervention.

2026-09-14: v1 ruined the approved raw look (regrade washed colors to plastic,
vcolor bake smoothed the authored grain, 256px crushed detail). v2 keeps the
authored Meshy output as intact as possible:

  1. UV-preserving decimation to 15k (per-decimated-vertex UV averaging)
  2. Texture kept at AUTHORED look, downscaled 2048 -> 512 (keeps grain and
     material detail; 4x crisper than the old 256px pixel pass)
  3. fill_holes (small open-shell defects only)
  4. welded smooth normals injected (lighting needs them)
  5. NO regrade, NO posterize, NO denoise, NO vertex colors - the texture
     renders as authored with LinearMipmapLinear + anisotropy

Input:  art-direction/3d/assets/races_regen/<name>.glb
Output: art-direction/3d/assets/races/<name>.glb (raw, 2048px tex)
        art-direction/3d/assets/races/<name>-pixelated.glb (512px tex)
"""
import os, sys, io, struct, json
import numpy as np
import trimesh
import fast_simplification as fs
from scipy.spatial import cKDTree
from PIL import Image

SRC = 'art-direction/3d/assets/races_regen'
DST_OUT = 'art-direction/3d/assets/races'
NAMES = ['dwarf-female','dwarf-male-smith','elf-dawn-refuser-male',
         'human-hunter-female','human-hunter-male','orc-female',
         'orc-male-warrior','undead-ghoul-male','vampire-female','vampire-male-noble']


def weld_vertices(verts, tol=1e-4):
    t = cKDTree(verts)
    pairs = t.query_pairs(tol, output_type="ndarray")
    parent = list(range(len(verts)))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for a, b in pairs:
        ra, rb = find(a), find(b)
        if ra != rb: parent[ra] = rb
    roots = np.array([find(i) for i in range(len(verts))])
    uniq, inv = np.unique(roots, return_inverse=True)
    canon = {}
    for i, c in enumerate(inv):
        if c not in canon:
            canon[c] = i
    rep = np.array([canon[c] for c in range(len(uniq))])
    return verts[rep], inv


def export_with_tex(path, verts, faces, uv, mat, tex):
    """Trimesh export then inject NORMAL. trimesh gotchas:
    - len(uv) MUST equal len(verts) or TEXCOORD_0 is silently dropped
    - GLB export embeds material.baseColorTexture, not TextureVisuals image
    """
    m = trimesh.Trimesh(verts, faces, process=False)
    m.fill_holes()
    faces = np.asarray(m.faces)
    mat2 = mat.copy()
    mat2.baseColorTexture = tex
    m.visual = trimesh.visual.texture.TextureVisuals(uv=uv, material=mat2, image=tex)
    buf = io.BytesIO(); m.export(buf, file_type='glb')
    data = bytearray(buf.getvalue())
    jl, = struct.unpack_from('<I', data, 12)
    g = json.loads(bytes(data[20:20+jl]))
    prim = g['meshes'][0]['primitives'][0]
    attrs = prim['attributes']
    accessors = g['accessors']; bvs = g['bufferViews']
    binoff = 20 + jl + 8
    blen, = struct.unpack_from('<I', data, 20+jl)
    bin_data = bytearray(data[binoff:binoff+blen])
    while len(bin_data)%4: bin_data += b'\x00'
    start = len(bin_data)
    # weld + area-weighted smooth normals
    wverts, inv = weld_vertices(verts)
    wfaces = inv[faces]
    wnorm = np.zeros((len(wverts), 3))
    fverts = wverts[wfaces]
    n = np.cross(fverts[:,1]-fverts[:,0], fverts[:,2]-fverts[:,0])
    a2 = np.linalg.norm(n, axis=1)
    valid = a2 > 1e-12
    n[valid] /= a2[valid,None]
    for k in range(3):
        np.add.at(wnorm, wfaces[:,k], n)
    L = np.linalg.norm(wnorm, axis=1); L[L<1e-12]=1
    wnorm /= L[:,None]
    nv = wnorm[inv].astype(np.float32)
    bin_data += nv.tobytes()
    while len(bin_data)%4: bin_data += b'\x00'
    bvs.append({'buffer':0,'byteOffset':start,'byteLength':nv.nbytes,'target':34962})
    accessors.append({'bufferView':len(bvs)-1,'componentType':5126,'count':len(nv),'type':'VEC3'})
    n_acc = len(accessors)-1
    new_attrs = {'NORMAL': n_acc}
    for key in ['POSITION','TEXCOORD_0']:
        if key in attrs: new_attrs[key] = attrs[key]
    prim['attributes'] = new_attrs
    g['buffers'][0]['byteLength'] = len(bin_data)
    json_out = json.dumps(g, separators=(',',':')).encode()
    pad = (4-len(json_out)%4)%4; json_out += b' '*pad
    out = (b'glTF' + struct.pack('<II',2,len(json_out)+8+len(bin_data))
           + struct.pack('<II',len(json_out),0x4E4F534A) + json_out
           + struct.pack('<II',len(bin_data),0x004E4942) + bytes(bin_data))
    with open(path,'wb') as fh: fh.write(out)
    os.chmod(path, 0o644)
    return len(verts)


if __name__ == '__main__':
    os.system('cp -r ' + SRC + ' /tmp/races_regen_backup_v2 2>/dev/null')
    for name in NAMES:
        src = os.path.join(SRC, name + '.glb')
        m = trimesh.load(src, force='mesh')
        uv = np.asarray(m.visual.uv).copy()
        mat = m.visual.material
        tex = mat.baseColorTexture
        faces = np.asarray(m.faces)
        verts = np.asarray(m.vertices)
        vn, fn = fs.simplify(verts, faces, target_count=15000)
        # per-decimated-vertex UV: average uv of original verts mapping to it
        _, idx = cKDTree(vn).query(verts, k=1)
        usums = np.zeros((len(vn), 2)); ucnts = np.zeros(len(vn))
        np.add.at(usums, idx, uv); np.add.at(ucnts, idx, 1)
        uvn = np.where(ucnts[:,None] > 0, usums/np.maximum(ucnts,1)[:,None], 0.5)
        uvn = uvn.astype(np.float64)
        # raw export: original 2048px texture
        export_with_tex(os.path.join(DST_OUT, name + '.glb'),
                        vn, fn, uvn, mat, tex)
        # pixelated-slot export: same authored texture at 512px
        tex512 = tex.resize((512,512), Image.LANCZOS)
        export_with_tex(os.path.join(DST_OUT, name + '-pixelated.glb'),
                        vn, fn, uvn, mat, tex512)
        print(f'{name}: {len(fn)} tris, 512px authored texture, normals in place')
    print('V2 PIPELINE COMPLETE')