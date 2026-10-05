#!/usr/bin/env python3
"""Shield asset integrity v2 (count accessor fixed)."""
import struct, json

def glb_report(path):
    data = open(path, 'rb').read()
    jl, = struct.unpack_from('<I', data, 12)
    d = json.loads(data[20:20 + jl])
    mesh = d['meshes'][0]
    out = []
    for prim in mesh['primitives']:
        out.append((sorted(prim['attributes'].keys()), prim.get('indices')))
    return d['meshes'][0].get('name'), out

def trimesh_info(path):
    import trimesh
    m = trimesh.load(path, force='mesh')
    e = m.extents
    return len(m.faces), tuple(round(float(x), 2) for x in e)

candidates = {
    'round-shield (weapons)': '/workspace/witch-hunter/art-direction/3d/assets/weapons/round-shield-pixelated.glb',
    'tower-shield (armor)':   '/workspace/witch-hunter/art-direction/3d/assets/armor/tower-shield-pixelated.glb',
    'buckler (armor)':        '/workspace/witch-hunter/art-direction/3d/assets/armor/buckler-pixelated.glb',
}
for label, path in candidates.items():
    try:
        mname, prims = glb_report(path)
        faces, ext = trimesh_info(path)
        print('%-24s mesh=%r prims=%d faces=%d ext=%s' % (label, mname, len(prims), faces, ext))
        for attrs, icount in prims:
            print('   attrs=%s indices=%s' % (attrs, icount if isinstance(icount, int) else '?'))
    except Exception as e:
        print(label, 'FAIL', str(e)[:90])