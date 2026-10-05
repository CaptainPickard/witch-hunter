"""Round K: measure the lantern-post-v2 light socket from GLB vertex data, and old vs new height.

scratch/lantern_head_probe.py pattern (POSITION accessor read straight from the chunks; +8 for
the BIN chunk header) with 20 bands and per-band XZ extents, so the glass box (widest section
between the scroll brackets and the cap overhang) and its lateral centre are MEASURED.
heightFraction is up the ground-aligned height (assets.js groundAlign: minY -> 0), the same
frame game.js computeSockets() uses: y = groundHeight * scale * heightFraction.
Signed: Claude Code (Round K), 2026-10-05.
"""
import struct, json, sys

WH = '/workspace/witch-hunter'


def positions(path):
    d = open(path, 'rb').read()
    ln = struct.unpack('<I', d[12:16])[0]
    j = json.loads(d[20:20 + ln])
    prim = j['meshes'][0]['primitives'][0]
    acc = j['accessors'][prim['attributes']['POSITION']]
    bv = j['bufferViews'][acc['bufferView']]
    off = 20 + ln + 8 + bv.get('byteOffset', 0) + acc.get('byteOffset', 0)  # +8: BIN chunk header
    stride = bv.get('byteStride', 12)
    return [struct.unpack_from('<fff', d, off + i * stride) for i in range(acc['count'])], acc


def analyze(path, nb=20):
    P, acc = positions(path)
    ys = [p[1] for p in P]
    y0, y1 = min(ys), max(ys)
    H = y1 - y0
    xs = [p[0] for p in P]; zs = [p[2] for p in P]
    print(f'== {path.split("/")[-1]}  H={H:.4f}  W(x)={max(xs) - min(xs):.4f}  D(z)={max(zs) - min(zs):.4f}')
    bands = [[] for _ in range(nb)]
    for p in P:
        bands[min(nb - 1, int((p[1] - y0) / H * nb))].append(p)
    rows = []
    for bi, b in enumerate(bands):
        if not b:
            continue
        bx = [v[0] for v in b]; bz = [v[2] for v in b]
        r = dict(band=bi, lo=bi / nb, hi=(bi + 1) / nb, n=len(b),
                 cx=sum(bx) / len(b), cz=sum(bz) / len(b),
                 xmin=min(bx), xmax=max(bx), zmin=min(bz), zmax=max(bz))
        rows.append(r)
        print(f"  band {bi:2d} ({r['lo']:.0%}-{r['hi']:.0%}): n={r['n']:5d} cx={r['cx']:+.3f} cz={r['cz']:+.3f} "
              f"x[{r['xmin']:+.3f},{r['xmax']:+.3f}] z[{r['zmin']:+.3f},{r['zmax']:+.3f}]")
    return dict(H=H, y0=y0, rows=rows)


if __name__ == '__main__':
    new = analyze(f'{WH}/art-direction/3d/assets/church-kit/lantern-post-v2-pixelated.glb')
    old = analyze(f'{WH}/art-direction/3d/assets/church-kit/lantern-post-pixelated.glb', nb=10)
    print(json.dumps({'old_H': round(old['H'], 4), 'new_H': round(new['H'], 4),
                      'scale_factor_old_over_new': round(old['H'] / new['H'], 4)}))
