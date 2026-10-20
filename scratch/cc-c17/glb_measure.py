#!/usr/bin/env python3
"""CC-C17v2: GLB header measure (POSITION accessor min/max + tri count) for the old_king bakes."""
import json, struct, sys, glob, os
for f in sorted(glob.glob(sys.argv[1] + '/*-pixelated.glb')):
    b = open(f, 'rb').read()
    ln = struct.unpack('<I', b[12:16])[0]
    j = json.loads(b[20:20 + ln])
    mn = [1e9] * 3; mx = [-1e9] * 3; tris = 0
    for m in j['meshes']:
        for p in m['primitives']:
            a = j['accessors'][p['attributes']['POSITION']]
            mn = [min(u, v) for u, v in zip(mn, a['min'])]; mx = [max(u, v) for u, v in zip(mx, a['max'])]
            tris += (j['accessors'][p['indices']]['count'] if 'indices' in p else a['count']) // 3
    ns = [n for n in j.get('nodes', []) if 'scale' in n or 'matrix' in n or 'rotation' in n]
    print('%-34s tris %6d  x %.2f  y %.2f  z %.2f  (ymin %.2f) nodeXf %d' % (os.path.basename(f), tris, mx[0]-mn[0], mx[1]-mn[1], mx[2]-mn[2], mn[1], len(ns)))
