#!/usr/bin/env python3
"""Post-pipeline for the regenerated race bodies: decimate to 15k, pixel
register re-texture, hole-fill, normals, vertex-color bake.

Steps per body:
  1. UV-preserving decimation to ~15k tris (fast_simplification)
  2. Pixelate the atlas (256px / 48-color mediancut / 5-bit posterize)
  3. Export pixelated GLB (TextureVisuals, uv preserved)
  4. fill_holes (small open-shell defects)
  5. add_normals.py-style in-place NORMAL inject
  6. bake_vertex_colors.py-style COLOR_0 bake (from regraded atlas)
  7. regrade_atlas.py-style in-place atlas regrade (gamma/saturation/denoise)

Input:  art-direction/3d/assets/races_regen/<name>.glb   (raw Meshy)
Output: art-direction/3d/assets/races/<name>.glb + <name>-pixelated.glb
(replaces the old bodies; old ones are backed up in /tmp first)
"""
import os, sys, io, struct, json
import numpy as np
import trimesh
import fast_simplification as fs
from scipy.spatial import cKDTree
from PIL import Image, ImageEnhance, ImageFilter

SRC = 'art-direction/3d/assets/races_regen'
DST = 'art-direction/3d/assets/races'
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


def pixelate(img):
    img = img.convert('RGB')
    w, h = img.size
    scale = 256.0 / max(w, h)
    if scale < 1.0:
        img = img.resize((max(1, int(w*scale)), max(1, int(h*scale))), Image.LANCZOS)
    # regrade baked into the pixel pass (concept midtones restored)
    a = np.asarray(img).astype(np.float32) / 255.0
    a = np.clip(a ** 0.55, 0, 1)
    img = Image.fromarray((a*255).astype(np.uint8))
    img = ImageEnhance.Color(img).enhance(1.4)
    img = img.filter(ImageFilter.MedianFilter(3))
    rgb = img.quantize(colors=48, method=Image.MEDIANCUT, dither=Image.Dither.NONE)
    arr = np.array(rgb.convert('RGB'))
    arr[...,0] = (arr[...,0] >> 3) << 3
    arr[...,1] = (arr[...,1] >> 3) << 3
    arr[...,2] = (arr[...,2] >> 3) << 3
    return Image.fromarray(arr)


def decimate_and_pixelate(name):
    src = os.path.join(SRC, name + '.glb')
    dst_raw = os.path.join(DST, name + '.glb')
    dst_pix = os.path.join(DST, name + '-pixelated.glb')
    m = trimesh.load(src, force='mesh')
    uv = np.asarray(m.visual.uv).copy()
    mat = m.visual.material
    tex = mat.baseColorTexture.copy()
    faces = np.asarray(m.faces)
    verts = np.asarray(m.vertices)
    # UV-preserving decimation
    vn, fn = fs.simplify(verts, faces, target_count=15000)
    # map UVs: nearest surviving vertex keeps its uv
    _, idx = cKDTree(vn).query(verts, k=1)
    uvn = uv[idx]
    nm = trimesh.Trimesh(vn, fn, process=False)
    nm.visual = trimesh.visual.texture.TextureVisuals(uv=uvn, material=mat, image=tex)
    nm.export(dst_raw, file_type='glb')
    # pixelated: same mesh, quantized texture
    newtex = pixelate(tex)
    nm.visual = trimesh.visual.texture.TextureVisuals(uv=uvn, material=mat, image=newtex)
    nm.export(dst_pix, file_type='glb')
    return len(fn)


def post_fix(path, uv, mat, tex, verts, faces):
    """fill_holes + normals + vcolors. Works in memory; single trimesh export,
    then GLB surgery injects NORMAL + COLOR_0 (trimesh drops those attrs)."""
    m = trimesh.Trimesh(verts, faces, process=False)
    m.fill_holes()
    faces = np.asarray(m.faces)
    # normals: weld + area-weighted smooth
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
    # vertex colors: bilinear atlas sample + 4-round smoothing
    arr = np.asarray(tex.convert('RGB'), dtype=np.float64)
    h, w = arr.shape[:2]
    wcount = len(wverts)
    wuv = np.zeros((wcount,2)); seen = np.zeros(wcount, bool)
    for i, c in enumerate(inv):
        if not seen[c]:
            seen[c] = True; wuv[c] = uv[i]
    px = np.clip(wuv[:,0]*w-0.5, 0, w-1); py = np.clip((1.0-wuv[:,1])*h, 0, h-1)
    x0=np.floor(px).astype(int); x1=np.clip(x0+1,0,w-1); y0=np.floor(py).astype(int); y1=np.clip(y0+1,0,h-1)
    fx=(px-x0)[:,None]; fy=(py-y0)[:,None]
    col = (arr[y0,x0]*(1-fx)*(1-fy) + arr[y0,x1]*fx*(1-fy) + arr[y1,x0]*(1-fx)*fy + arr[y1,x1]*fx*fy)
    sm = col.copy()
    for _ in range(4):
        ns = np.zeros_like(col); nc = np.zeros(wcount)
        for k in range(3):
            a,b,c2 = wfaces[:,k], wfaces[:,(k+1)%3], wfaces[:,(k+2)%3]
            for src,dst in ((a,b),(a,c2),(b,a),(b,c2),(c2,a),(c2,b)):
                np.add.at(ns,dst,sm[src]); np.add.at(nc,dst,1.0)
        mk = nc>0
        sm[mk] = 0.6*sm[mk] + 0.4*(ns[mk]/nc[mk,None])
    vcol = np.clip(sm**0.85, 0, 1)
    # single export with uv+material (trimesh drops NORMAL/COLOR_0 -> inject)
    m.visual = trimesh.visual.texture.TextureVisuals(uv=uv, material=mat, image=tex)
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
    def append(arrf, target=34962):
        nonlocal bin_data
        while len(bin_data)%4: bin_data += b'\x00'
        start = len(bin_data); bin_data += arrf.tobytes()
        while len(bin_data)%4: bin_data += b'\x00'
        bvs.append({'buffer':0,'byteOffset':start,'byteLength':arrf.nbytes,'target':target})
        return len(bvs)-1
    nv = wnorm[inv].astype(np.float32)
    nview = append(nv)
    accessors.append({'bufferView':nview,'componentType':5126,'count':len(nv),'type':'VEC3'})
    n_acc = len(accessors)-1
    colf = np.concatenate([vcol[inv], np.ones((len(inv),1))], axis=1).astype(np.float32)
    cview = append(colf)
    accessors.append({'bufferView':cview,'componentType':5126,'count':len(colf),'type':'VEC4'})
    c_acc = len(accessors)-1
    new_attrs = {}
    for key in ['POSITION','NORMAL','TEXCOORD_0','COLOR_0']:
        if key == 'NORMAL': new_attrs[key] = n_acc
        if key == 'COLOR_0': new_attrs[key] = c_acc
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
    return len(vcol)


if __name__ == '__main__':
    # backup old bodies once
    os.system('cp -r ' + DST + ' /tmp/races_backup_regen_final 2>/dev/null')
    for name in NAMES:
        src = os.path.join(SRC, name + '.glb')
        dst_raw = os.path.join(DST, name + '.glb')
        dst_pix = os.path.join(DST, name + '-pixelated.glb')
        m = trimesh.load(src, force='mesh')
        uv = np.asarray(m.visual.uv).copy()
        mat = m.visual.material
        tex = mat.baseColorTexture.copy()
        faces = np.asarray(m.faces)
        verts = np.asarray(m.vertices)
        vn, fn = fs.simplify(verts, faces, target_count=15000)
        # per-vn-vertex UV: average uv of original vertices mapping to each
        # decimated vertex. TextureVisuals requires len(uv)==len(verts) or
        # trimesh silently drops TEXCOORD_0 on export.
        _, idx = cKDTree(vn).query(verts, k=1)
        usums = np.zeros((len(vn), 2)); ucnts = np.zeros(len(vn))
        np.add.at(usums, idx, uv); np.add.at(ucnts, idx, 1)
        uvn = np.where(ucnts[:,None] > 0, usums/np.maximum(ucnts,1)[:,None], 0.5)
        uvn = uvn.astype(np.float64)
        nm = trimesh.Trimesh(vn, fn, process=False)
        nm.visual = trimesh.visual.texture.TextureVisuals(uv=uvn, material=mat, image=tex)
        nm.export(dst_raw, file_type='glb')
        os.chmod(dst_raw, 0o644)
        newtex = pixelate(tex)
        # post_fix does: fill_holes + normals + vcolors + pixelated-texture export
        wv = post_fix(dst_pix, uvn, mat, newtex, vn, fn)
        print(f'{name}: decimated to {len(fn)} tris, vcolors baked ({wv} welded verts)')
    print('PIPELINE COMPLETE')