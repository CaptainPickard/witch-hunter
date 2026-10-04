#!/usr/bin/env python3
"""Round G: land the Meshy snare bush in biome_library (tree_bake.py layout).

The Meshy GLB IO downloaded (task 01a1092f-3bdf-7461-86ad-9eaa081187cc) is
GEOMETRY ONLY: POSITION + indices, no material, no TEXCOORD_0, no image. So
the bake law's texture half (512 NEAREST + 5-bit posterize of the base color
map) has nothing to act on. Fallback, flagged in io/roundG-provenance.md:
  - mesh = the decimated mesh (scratch/decimate_roundG.py), smooth vertex
    NORMALs (biome_pixelate.export's area-weighted vertex normals);
  - material = untextured PBR, metallic 0 / roughness 0.8 like the E siblings,
    baseColorFactor = wh-tree-dead-young's mean bark texel (62/55/50 sRGB)
    5-bit crushed (56/48/48) and converted to linear (glTF factors are linear).

  snare_bake_roundG.py <meshy-raw.glb> <decimated.glb> <thumb.png> [--force]
Writes biome_library/raw/wh-bush-snare.glb (Meshy original, byte copy),
       biome_library/refs/wh-bush-snare-meshy-raw.glb (same bytes, per brief),
       biome_library/refs/wh-bush-snare-ref.png (Meshy thumbnail),
       biome_library/wh-bush-snare.glb (decimated geometry, no material),
       biome_library/wh-bush-snare-pixelated.glb (runtime asset).
"""
import json, os, shutil, struct, sys
import numpy as np
import trimesh

OUT = 'art-direction/3d/assets/biome_library'
MID = 'wh-bush-snare'
raw, dec, thumb = sys.argv[1:4]
SRGB = (62, 55, 50)                                  # wh-tree-dead-young mean texel


def crush5(v): return (v >> 3) << 3
def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


targets = [os.path.join(OUT, 'raw', MID + '.glb'), os.path.join(OUT, 'refs', MID + '-meshy-raw.glb'),
           os.path.join(OUT, 'refs', MID + '-ref.png'), os.path.join(OUT, MID + '.glb'),
           os.path.join(OUT, MID + '-pixelated.glb')]
for p in targets:
    if os.path.exists(p) and '--force' not in sys.argv:
        sys.exit(f'refusing to overwrite existing {p}')
shutil.copyfile(raw, targets[0])
shutil.copyfile(raw, targets[1])
shutil.copyfile(thumb, targets[2])

m = trimesh.load(dec, force='mesh')
plain = trimesh.Trimesh(np.asarray(m.vertices), np.asarray(m.faces), process=False)
plain.export(targets[3], file_type='glb')

# runtime asset: POSITION + NORMAL + indices + one untextured material
v = np.asarray(m.vertices, dtype='<f4')
f = np.asarray(m.faces, dtype='<u4').reshape(-1)
n = np.asarray(trimesh.Trimesh(v, m.faces, process=False).vertex_normals, dtype='<f4')
crushed = [crush5(c) for c in SRGB]
factor = [round(lin(c), 6) for c in crushed] + [1.0]
blobs = [v.tobytes(), n.tobytes(), f.tobytes()]
views, off = [], 0
for b, tgt in zip(blobs, (34962, 34962, 34963)):
    views.append({'buffer': 0, 'byteOffset': off, 'byteLength': len(b), 'target': tgt})
    off += len(b)
gltf = {
    'asset': {'version': '2.0', 'generator': 'scratch/snare_bake_roundG.py'},
    'scene': 0, 'scenes': [{'nodes': [0]}], 'nodes': [{'mesh': 0, 'name': MID}],
    'meshes': [{'name': MID, 'primitives': [{'attributes': {'POSITION': 0, 'NORMAL': 1},
                                             'indices': 2, 'material': 0}]}],
    'materials': [{'name': MID + '-bark', 'pbrMetallicRoughness': {
        'baseColorFactor': factor, 'metallicFactor': 0.0, 'roughnessFactor': 0.8}}],
    'accessors': [
        {'bufferView': 0, 'componentType': 5126, 'count': len(v), 'type': 'VEC3',
         'min': v.min(0).tolist(), 'max': v.max(0).tolist()},
        {'bufferView': 1, 'componentType': 5126, 'count': len(n), 'type': 'VEC3'},
        {'bufferView': 2, 'componentType': 5125, 'count': len(f), 'type': 'SCALAR'}],
    'bufferViews': views, 'buffers': [{'byteLength': off}]}
js = json.dumps(gltf, separators=(',', ':')).encode()
js += b' ' * ((4 - len(js) % 4) % 4)
bin_ = b''.join(blobs)
bin_ += b'\x00' * ((4 - len(bin_) % 4) % 4)
total = 12 + 8 + len(js) + 8 + len(bin_)
with open(targets[4], 'wb') as fh:
    fh.write(struct.pack('<4sII', b'glTF', 2, total))
    fh.write(struct.pack('<I4s', len(js), b'JSON') + js)
    fh.write(struct.pack('<I4s', len(bin_), b'BIN\x00') + bin_)
print(MID, 'faces', len(m.faces), 'verts', len(v), 'baseColor sRGB', crushed, 'linear', factor[:3],
      'raw', os.path.getsize(targets[0]) // 1024, 'KB, pixelated', os.path.getsize(targets[4]) // 1024, 'KB')
