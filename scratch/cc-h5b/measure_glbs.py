#!/usr/bin/env python3
import struct, json

def glb_json(path):
    with open(path, 'rb') as f:
        magic, ver, length = struct.unpack('<III', f.read(12))
        clen, ctype = struct.unpack('<II', f.read(8))
        assert ctype == 0x4E4F534A, hex(ctype)  # 'JSON'
        data = f.read(clen)
        return json.loads(data.decode('utf-8', errors='replace'))

def measure(path):
    g = glb_json(path)
    acc = g['accessors']
    xs = []
    for m in g.get('meshes', []):
        for p in m.get('primitives', []):
            pa = p.get('attributes', {}).get('POSITION')
            if pa is not None:
                a = acc[pa]
                if a.get('min') and a.get('max'):
                    xs.append((a['min'][0], a['max'][0]))
    return max(x[1] for x in xs) - min(x[0] for x in xs) if xs else 0

for name, p in [('mourningStatue',
                 '/tmp/wh-worldfeat/art-direction/3d/assets/biome_library/m3-pixelated.glb'),
                ('okRuinColumn',
                 '/tmp/wh-worldfeat/art-direction/3d/assets/old_king/ok-ruin-column-pixelated.glb'),
                ('stoneSteps',
                 '/tmp/wh-worldfeat/art-direction/3d/assets/crypt/stone-steps-pixelated.glb'),
                ('skullPile',
                 '/tmp/wh-worldfeat/art-direction/3d/assets/crypt/skull-pile-pixelated.glb')]:
    try:
        w = measure(p)
        print(name, 'raw X width', round(w, 3), 'foot radius scale1', round(w / 2, 3))
    except Exception as e:
        print(name, 'ERR', e)
