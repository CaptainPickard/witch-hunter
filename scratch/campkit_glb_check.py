#!/usr/bin/env python3
"""Campkit GLB byte-invariant + structure check (clone of torch_glb_check.py):
per-file parse of the GLB chunks: nodes, mesh names, attributes, texture size,
5-bit posterize proof, per-node tri counts, origin/bounds.
  campkit_glb_check.py <glb> [<glb> ...]
"""
import json, struct, sys
import numpy as np

for path in sys.argv[1:]:
    b = open(path, 'rb').read()
    magic, ver, ln = struct.unpack_from('<III', b, 0)
    jl, = struct.unpack_from('<I', b, 12)
    js = json.loads(b[20:20 + jl])
    print(f'== {path}  bytes {len(b):,}  gltf {ver} json {jl:,}')
    print('  asset:', js.get('asset', {}).get('version'), 'generator:', js.get('asset', {}).get('generator', '')[:60])
    nodes = js.get('nodes', [])
    print('  nodes:', [n.get('name') for n in nodes])
    print('  scenes[0].nodes:', js.get('scenes', [{}])[0].get('nodes'))
    meshes = js.get('meshes', [])
    tot = 0
    for i, m in enumerate(meshes):
        for p in m['primitives']:
            mode = p.get('mode', 4)
            if 'indices' in p:
                ntri = js['accessors'][p['indices']]['count'] // 3
            else:
                ntri = js['accessors'][p['attributes']['POSITION']]['count'] // 3
            tot += ntri
            print(f"  mesh[{i}] node={m.get('name', 'unnamed')} tris {ntri} attrs {sorted(p['attributes'])} material {p.get('material')}")
    print('  tris total:', tot)
    for mi, m in enumerate(meshes):
        pass
    imgs = js.get('images', [])
    print('  images:', [(im.get('mimeType'), ) for im in imgs])
    mats = js.get('materials', [])
    for mt in mats:
        pbr = mt.get('pbrMetallicRoughness', {})
        print('  material:', mt.get('name'), 'baseColorTex' in pbr and 'TEX' or 'no-tex',
              'metallic', pbr.get('metallicFactor'), 'rough', pbr.get('roughnessFactor'))
    # texture pixel check per bufferView->image (only if single image)
    if len(imgs) == 1:
        im = imgs[0]
        bv = js['bufferViews'][im['bufferView']]
        off = 20 + jl + 8 + bv.get('byteOffset', 0)
        png = b[off:off + bv['byteLength']]
        from PIL import Image
        import io
        timg = Image.open(io.BytesIO(png))
        a = np.asarray(timg.convert('RGB'))
        five = bool(all((a[..., c] & 7 == 0).all() for c in range(3)))
        print('  tex', timg.size, 'mode', timg.mode, '5-bit', five,
              'levels R/G/B', [int(len(np.unique(a[..., c]))) for c in range(3)])
    # bounds from POSITION of all prims
    mins = np.full(3, np.inf); maxs = np.full(3, -np.inf)
    for m in meshes:
        for p in m['primitives']:
            ai = p['attributes']['POSITION']
            acc = js['accessors'][ai]
            mins = np.minimum(mins, acc['min']); maxs = np.maximum(maxs, acc['max'])
    print('  POSITION mins/maxs:', mins.round(3).tolist(), maxs.round(3).tolist())