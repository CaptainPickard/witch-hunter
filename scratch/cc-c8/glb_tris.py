#!/usr/bin/env python3
"""Count triangles + bbox per GLB (CC-C8 tri ledger). Usage: glb_tris.py file.glb ..."""
import json, struct, sys
for path in sys.argv[1:]:
    b = open(path, 'rb').read()
    n = struct.unpack_from('<I', b, 12)[0]
    j = json.loads(b[20:20 + n])
    tris = 0
    for m in j.get('meshes', []):
        for p in m['primitives']:
            if p.get('mode', 4) != 4: continue
            if 'indices' in p: tris += j['accessors'][p['indices']]['count'] // 3
            else: tris += j['accessors'][p['attributes']['POSITION']]['count'] // 3
    mins = [1e9] * 3; maxs = [-1e9] * 3
    for m in j.get('meshes', []):
        for p in m['primitives']:
            a = j['accessors'][p['attributes']['POSITION']]
            if 'min' in a:
                mins = [min(x, y) for x, y in zip(mins, a['min'])]
                maxs = [max(x, y) for x, y in zip(maxs, a['max'])]
    ext = [round(maxs[i] - mins[i], 3) for i in range(3)]
    print(f"{path.split('/')[-1]:40s} tris {tris:7d}  ext {ext}")
