#!/usr/bin/env python3
"""List animation clip names + bone names in the player rigged GLB."""
import struct, json

p = '/tmp/wh-worldfeat/art-direction/3d/assets/races_regen/rigged/human-hunter-male.rigged.glb'
data = open(p, 'rb').read()
# GLB: 12-byte header, chunks
jl, = struct.unpack_from('<I', data, 12)
j = json.loads(data[20:20 + jl])
anims = j.get('animations', [])
print('animations:', [a.get('name', '<noname>') for a in anims])
skins = j.get('skins', [])
if skins:
    bones = [j['nodes'][n].get('name', '?') for n in skins[0].get('joints', [])]
    print('bone count:', len(bones))
    print('bones:', bones[:40])
print('mesh nodes:', [n.get('name', '?') for n in j.get('nodes', []) if 'mesh' in n][:10])