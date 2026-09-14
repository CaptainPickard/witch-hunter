#!/usr/bin/env python3
"""v3: EXACTLY what the user asked for. No geometry post-processing at all.

"Get rid of your post processing completely... Remove any post-processing
unless it's purely pixelation of the colors on the skin."

v3 per body:
  - raw Meshy mesh used AS-IS (no decimation, no UV changes, no hole-fill)
  - normals injected (required for the viewer's lighting to work; invisible)
  - texture: color pixelation ONLY (512px nearest + 5-bit posterize, no
    smoothing, no regrade, no palette quantize beyond the bit crush)

Input:  art-direction/3d/assets/races_regen/<name>.glb  (raw Meshy, untouched)
Output: art-direction/3d/assets/races/<name>.glb (2048px tex)
        art-direction/3d/assets/races/<name>-pixelated.glb (512px, 5-bit)
"""
import os, io, struct, json
import numpy as np
import trimesh
from PIL import Image

SRC = 'art-direction/3d/assets/races_regen'
OUT = 'art-direction/3d/assets/races'
NAMES = ['dwarf-female','dwarf-male-smith','elf-dawn-refuser-male',
         'human-hunter-female','human-hunter-male','orc-female',
         'orc-male-warrior','undead-ghoul-male','vampire-female','vampire-male-noble']


def export(path, verts, faces, uv, mat, tex):
    """Export raw mesh + inject NORMAL. uv MUST be len==len(verts)."""
    m = trimesh.Trimesh(verts, faces, process=False)
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
    # smooth normals (lighting requirement; no visual change on unlit texels)
    verts32 = verts.astype(np.float32)
    fn = np.cross(verts32[faces[:,1]]-verts32[faces[:,0]], verts32[faces[:,2]]-verts32[faces[:,0]])
    a2 = np.linalg.norm(fn, axis=1); ok = a2 > 1e-12
    fn[ok] /= a2[ok,None]
    vnorm = np.zeros((len(verts), 3))
    for k in range(3):
        np.add.at(vnorm, faces[:,k], fn)
    L = np.linalg.norm(vnorm, axis=1); L[L<1e-12]=1
    vnorm /= L[:,None]
    nv = vnorm.astype(np.float32)
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
    outb = (b'glTF' + struct.pack('<II',2,len(json_out)+8+len(bin_data))
            + struct.pack('<II',len(json_out),0x4E4F534A) + json_out
            + struct.pack('<II',len(bin_data),0x004E4942) + bytes(bin_data))
    with open(path,'wb') as fh: fh.write(outb)
    os.chmod(path, 0o644)


def pixelate_colors(tex):
    """Pure color pixelation: NEAREST downscale + 5-bit posterize. No blur,
    no smoothing, no palette remap - just crush texel density and color depth."""
    t = tex.convert('RGB').resize((512,512), Image.NEAREST)
    arr = np.asarray(t)
    arr = (arr >> 3) << 3
    return Image.fromarray(arr)


if __name__ == '__main__':
    for name in NAMES:
        src = os.path.join(SRC, name + '.glb')
        raw = open(src,'rb').read()
        jl, = struct.unpack_from('<I', raw, 12)
        g = json.loads(raw[20:20+jl])
        prim = g['meshes'][0]['primitives'][0]
        img = g['images'][0]; bv = g['bufferViews'][img['bufferView']]
        binoff = 20 + jl + 8
        tex = Image.open(io.BytesIO(raw[binoff+bv['byteOffset']:binoff+bv['byteOffset']+bv['byteLength']])).convert('RGB')
        m = trimesh.load(src, force='mesh')
        uv = np.asarray(m.visual.uv)
        assert uv is not None and len(uv) == len(m.vertices), name
        mat = m.visual.material
        # raw export: original texture, original mesh, + normals
        export(os.path.join(OUT, name + '.glb'), np.asarray(m.vertices), np.asarray(m.faces), uv, mat, tex)
        # pixelated: color-pixelated texture only
        export(os.path.join(OUT, name + '-pixelated.glb'), np.asarray(m.vertices), np.asarray(m.faces), uv, mat, pixelate_colors(tex))
        print(f'{name}: raw mesh as-is ({len(m.faces)} faces), color-pixelated tex, normals')
    print('V3 COMPLETE')