#!/usr/bin/env python3
"""CC-C10: GLB header measure (read-only) for the two new manifest keys -
POSITION min/max, tri count, skins / animations, embedded image dims.
usage: python3 scratch/cc-c10/glb_header.py <file.glb> [...]"""
import json, struct, sys, os, hashlib

def png_dims(buf):
    if buf[:8] == b'\x89PNG\r\n\x1a\n':
        return struct.unpack('>II', buf[16:24])
    if buf[:2] == b'\xff\xd8':                 # JPEG: walk to the SOF0/SOF2 marker
        i = 2
        while i + 9 < len(buf):
            m = buf[i + 1]; L = struct.unpack('>H', buf[i + 2:i + 4])[0]
            if m in (0xC0, 0xC2): return struct.unpack('>HH', buf[i + 5:i + 9])[::-1]
            i += 2 + L
    return None

for f in sys.argv[1:]:
    b = open(f, 'rb').read()
    ln = struct.unpack('<I', b[12:16])[0]
    j = json.loads(b[20:20 + ln])
    bin_off = 20 + ln + 8
    mn = [1e9] * 3; mx = [-1e9] * 3; tris = 0
    for m in j['meshes']:
        for p in m['primitives']:
            a = j['accessors'][p['attributes']['POSITION']]
            mn = [min(u, v) for u, v in zip(mn, a['min'])]; mx = [max(u, v) for u, v in zip(mx, a['max'])]
            tris += (j['accessors'][p['indices']]['count'] if 'indices' in p else a['count']) // 3
    imgs = []
    for im in j.get('images', []):
        if 'bufferView' in im:
            bv = j['bufferViews'][im['bufferView']]
            s = bin_off + bv.get('byteOffset', 0)
            imgs.append((im.get('mimeType'), png_dims(b[s:s + bv['byteLength']])))
    samp = [(s.get('magFilter'), s.get('minFilter')) for s in j.get('samplers', [])]
    print(json.dumps({
        'file': os.path.basename(f), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest(),
        'tris': tris, 'size': [round(mx[i] - mn[i], 3) for i in range(3)], 'ymin': round(mn[1], 3),
        'skins': len(j.get('skins', [])), 'animations': [a.get('name') for a in j.get('animations', [])],
        'images': imgs, 'samplers': samp}))
