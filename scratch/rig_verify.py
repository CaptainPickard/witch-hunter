#!/usr/bin/env python3
"""Round-trip verify BOTH player GLBs: original (6 anims) + combat-chain (9)."""
import struct, json

def probe(path):
    data = open(path, 'rb').read()
    jl, = struct.unpack_from('<I', data, 12)
    j = json.loads(data[20:20 + jl])
    anims = [a.get('name', '<noname>') for a in j.get('animations', [])]
    nb = 0
    if j.get('skins'):
        nb = len(j['skins'][0].get('joints', []))
    print(path.split('/')[-1], '| anims:', len(anims), '| bones:', nb)
    print('  ', anims)
    return anims

a = probe('/tmp/wh-worldfeat/art-direction/3d/assets/races_regen/rigged/human-hunter-male.rigged.glb')
b = probe('/tmp/wh-worldfeat/art-direction/3d/assets/races_regen/rigged/human-hunter-male.combat-chain.glb')
need = {'WH_Attack1', 'WH_Death', 'WH_Hit', 'WH_Idle', 'WH_Run', 'WH_Walk'}
new = {'WH_SlashR2L', 'WH_SlashL2R', 'WH_Thrust'}
print('original has all 6:', need.issubset(set(a)))
print('chain copy has 6 + 3:', need.issubset(set(b)) and new.issubset(set(b)))