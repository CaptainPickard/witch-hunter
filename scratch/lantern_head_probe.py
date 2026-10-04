"""Round D2 pre-contract: measure lantern head offsets from GLB vertex data.

For each fire prop GLB: load POSITION accessor, bucket vertices by height
into 10 bands, print per-band lateral centroid + count, so the hanging
head's offset from the prop column is MEASURED, not guessed.
"""
import struct, json

WH = '/workspace/witch-hunter'  # raw vertex data, same in both branches

def analyze(path):
    d = open(path, 'rb').read()
    ln = struct.unpack('<I', d[12:16])[0]
    j = json.loads(d[20:20+ln])
    prim = j['meshes'][0]['primitives'][0]
    ai = prim['attributes']['POSITION']
    acc = j['accessors'][ai]
    bv = j['bufferViews'][acc['bufferView']]
    off = 20 + ln + 8 + bv.get('byteOffset', 0) + acc.get('byteOffset', 0)  # +8: BIN chunk header
    stride = bv.get('byteStride', 12)
    n = acc['count']
    mn, mx = acc['min'], acc['max']
    H = mx[1] - mn[1]
    bands = [[] for _ in range(10)]
    for i in range(n):
        x, y, z = struct.unpack_from('<fff', d, off + i * stride)
        b = min(9, int((y - mn[1]) / H * 10))
        bands[b].append((x, y, z))
    name = path.split('/')[-1]
    print(f'== {name}  H={H:.3f}')
    for bi, band in enumerate(bands):
        if not band: continue
        cx = sum(v[0] for v in band) / len(band)
        cz = sum(v[2] for v in band) / len(band)
        ym = (bi + 0.5) / 10
        print(f'  band {bi} ({ym:.0%}): n={len(band):6d} cx={cx:+.3f} cz={cz:+.3f}')

analyze(f'{WH}/art-direction/3d/assets/church-kit/lantern-post-pixelated.glb')
analyze(f'{WH}/art-direction/3d/assets/biome_library/b3-waymarker-pixelated.glb')
analyze(f'{WH}/art-direction/3d/assets/biome_library/m15-bandit-campfire-pixelated.glb')