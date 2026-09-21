#!/usr/bin/env python3
"""Biome library pixelation pass (v3 discipline: raw mesh AS-IS, normals
injected, color pixelation only: 512px NEAREST + 5-bit posterize).

Input:  art-direction/3d/assets/biome_library/raw/<id>.glb
Output: art-direction/3d/assets/biome_library/<id>.glb (raw copy)
        art-direction/3d/assets/biome_library/<id>-pixelated.glb
"""
import os, io, struct, json
import numpy as np
import trimesh
from PIL import Image

SRC = 'art-direction/3d/assets/biome_library/raw'
OUT = 'art-direction/3d/assets/biome_library'
IDS = ['m1', 'm2', 'm3', 'm4']


def posterize512(img):
    img = img.convert('RGBA')
    w, h = img.size
    scale = 512.0 / max(w, h)
    if scale < 1.0:
        img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.NEAREST)
    arr = np.array(img)
    for c in (0, 1, 2):
        arr[..., c] = (arr[..., c] >> 3) << 3
    return Image.fromarray(arr)


def export(path, mesh, tex):
    mat = mesh.visual.material.copy() if hasattr(mesh.visual, 'material') else trimesh.visual.material.PBRMaterial()
    mat.baseColorTexture = tex
    mesh.visual = trimesh.visual.texture.TextureVisuals(
        uv=mesh.visual.uv, material=mat, image=tex)
    mesh.export(path, file_type='glb')
    # inject NORMAL attribute if missing (required for lighting)
    data = bytearray(open(path, 'rb').read())
    jl, = struct.unpack_from('<I', data, 12)
    g = json.loads(bytes(data[20:20 + jl]))
    prim = g['meshes'][0]['primitives'][0]
    if 'NORMAL' not in prim.get('attributes', {}):
        verts_i = prim['attributes']['POSITION']
        import numpy as _np
        # find POSITION accessor values
        acc = g['accessors'][verts_i]
        bv = g['bufferViews'][acc['bufferView']]
        off = 20 + jl + bv.get('byteOffset', 0)
        n = acc['count']
        pos = _np.frombuffer(bytes(data[off:off + n * 12]), dtype='<f4').reshape(n, 3)
        faces = None
        idx_i = prim.get('indices')
        acci = g['accessors'][idx_i] if idx_i is not None else None
        if acci is not None:
            bvi = g['bufferViews'][acci['bufferView']]
            offi = 20 + jl + bvi.get('byteOffset', 0)
            idx = _np.frombuffer(bytes(data[offi:offi + acci['count'] * 4]), dtype='<u4')
            faces = idx.reshape(-1, 3)
        tm = trimesh.Trimesh(pos, faces, process=False)
        tm.vertex_normals
        norm = tm.vertex_normals.astype('<f4')
        payload = norm.tobytes()
        # append a new bufferView + accessor + attribute
        blen = len(payload)
        buf = g['buffers'][0]
        buf['byteLength'] = (buf['byteLength'] + 3) // 4 * 4
        pad = buf['byteLength']
        data.extend(b'\x00' * (pad - (len(data) - 20 - jl - 8)))
        data.extend(payload)
        g['bufferViews'].append({'buffer': 0, 'byteOffset': pad, 'byteLength': blen})
        g['accessors'].append({'bufferView': len(g['bufferViews']) - 1,
                               'componentType': 5126, 'count': n, 'type': 'VEC3'})
        prim['attributes']['NORMAL'] = len(g['accessors']) - 1
        buf['byteLength'] = pad + blen
        jnew = json.dumps(g, separators=(',', ':')).encode()
        padj = (4 - (len(jnew) % 4)) % 4
        jnew += b' ' * padj if False else b' ' * ((4 - (len(jnew) % 4)) % 4)
        struct.pack_into('<I', data, 12, len(jnew))
        out = bytearray(b'glTF')
        struct.pack_into('<I', out, 4, 2)
        jl2 = len(jnew)
        blen2 = len(data) - 20 - 8
        out += struct.pack('<I', jl2) + jnew
        bin_data = bytes(data[20 + jl + 8:])
        out += struct.pack('<I', len(bin_data)) + bin_data
        open(path, 'wb').write(bytes(out))
        print('  injected normals')


def main():
    os.chdir('/workspace/witch-hunter')
    for mid in IDS:
        src = os.path.join(SRC, mid + '.glb')
        scene = trimesh.load(src)
        mesh = list(scene.geometry.values())[0]
        img = mesh.visual.material.baseColorTexture
        # raw copy (untouched mesh)
        raw_out = os.path.join(OUT, mid + '.glb')
        mesh.export(raw_out, file_type='glb')
        # pixelated
        tex = posterize512(img)
        pix_out = os.path.join(OUT, mid + '-pixelated.glb')
        export(pix_out, mesh, tex)
        print(mid, 'raw', os.path.getsize(raw_out) // 1024, 'KB, pixelated', os.path.getsize(pix_out) // 1024, 'KB')


if __name__ == '__main__':
    main()