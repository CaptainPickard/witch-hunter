#!/usr/bin/env python3
"""Round J step 2 (static, no browser): the Box3.setFromObject(scene) the
r185 GLTFLoader path yields = accessor POSITION min/max through each node's
TRS chain (precise=false uses geometry.boundingBox = accessor min/max)."""
import json, struct, sys
import numpy as np

def trs(n):
    if 'matrix' in n:
        return np.array(n['matrix']).reshape(4, 4).T
    t = np.eye(4); t[:3, 3] = n.get('translation', [0, 0, 0])
    x, y, z, w = n.get('rotation', [0, 0, 0, 1])
    r = np.eye(4); r[:3, :3] = [[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                                [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                                [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]]
    s = np.diag(list(n.get('scale', [1, 1, 1])) + [1])
    return t @ r @ s

for f in sys.argv[1:]:
    d = open(f, 'rb').read()
    jl, = struct.unpack_from('<I', d, 12)
    g = json.loads(d[20:20 + jl])
    lo, hi = np.full(3, np.inf), np.full(3, -np.inf)
    def walk(i, M):
        global lo, hi
        n = g['nodes'][i]; M = M @ trs(n)
        if 'mesh' in n:
            for p in g['meshes'][n['mesh']]['primitives']:
                a = g['accessors'][p['attributes']['POSITION']]
                mn, mx = a['min'], a['max']
                for c in [(x, y, z) for x in (mn[0], mx[0]) for y in (mn[1], mx[1]) for z in (mn[2], mx[2])]:
                    w = (M @ np.array([*c, 1]))[:3]
                    lo = np.minimum(lo, w); hi = np.maximum(hi, w)
        for c in n.get('children', []):
            walk(c, M)
    for r in g['scenes'][g.get('scene', 0)]['nodes']:
        walk(r, np.eye(4))
    xf = [k for n in g['nodes'] for k in ('matrix', 'translation', 'rotation', 'scale') if k in n]
    print(f"{f.split('/')[-1]}: Box3 min={lo.round(4)} max={hi.round(4)} node-xforms={xf or 'none'}")
