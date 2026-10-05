"""Round L: measure the lantern-post-v3 (arm-hook) light socket: the HANGING cage, off the pillar axis.

scratch/lantern_head_probe_roundK.py reader (POSITION accessor straight from the chunks; +8 for
the BIN chunk header). v3's pillar sits on the glTF origin (bake recenter), the arm curves out
to -X and the cage hangs below its hook, so the cage is split from the pillar by X: vertices
with x < CAGE_X are cage + hook + arm tip. Fine 2.5% bands over the top 40% H, cage-side only,
locate the glass band (widest section between the cage floor and the cap overhang) and its
X/Z centre. heightFraction is up the ground-aligned height (assets.js groundAlign: minY -> 0),
the frame game.js computeSockets() uses: y = groundHeight * scale * heightFraction.
Signed: Claude Code (Round L), 2026-10-05.
"""
import json
import sys
sys.path.insert(0, '/workspace/witch-hunter/scratch')
from lantern_head_probe_roundK import positions, analyze

WH = '/workspace/witch-hunter'
KIT = f'{WH}/art-direction/3d/assets/church-kit'
CAGE_X = -0.12


def cage(path, lo=0.6, step=0.025):
    P, _ = positions(path)
    ys = [p[1] for p in P]
    y0, y1 = min(ys), max(ys)
    H = y1 - y0
    pil = [p for p in P if (p[1] - y0) / H < 0.6]
    print(f'== cage bands {path.split("/")[-1]}  H={H:.4f}  pillar(<60%H) x[{min(p[0] for p in pil):+.3f},'
          f'{max(p[0] for p in pil):+.3f}] z[{min(p[2] for p in pil):+.3f},{max(p[2] for p in pil):+.3f}]')
    rows = []
    f = lo
    while f < 1.0 - 1e-9:
        b = [p for p in P if f <= (p[1] - y0) / H < f + step and p[0] < CAGE_X]
        if b:
            bx = [v[0] for v in b]; bz = [v[2] for v in b]
            r = dict(lo=round(f, 3), hi=round(f + step, 3), n=len(b),
                     xmin=min(bx), xmax=max(bx), zmin=min(bz), zmax=max(bz),
                     xc=(min(bx) + max(bx)) / 2, zc=(min(bz) + max(bz)) / 2)
            rows.append(r)
            print(f"  {r['lo']:.1%}-{r['hi']:.1%}: n={r['n']:4d} x[{r['xmin']:+.3f},{r['xmax']:+.3f}] "
                  f"z[{r['zmin']:+.3f},{r['zmax']:+.3f}] ctr=({r['xc']:+.3f},{r['zc']:+.3f}) "
                  f"w={r['xmax'] - r['xmin']:.3f}")
        f += step
    return dict(H=H, rows=rows)


if __name__ == '__main__':
    v3 = analyze(f'{KIT}/lantern-post-v3-pixelated.glb')
    cage(f'{KIT}/lantern-post-v3-pixelated.glb')
    v2 = analyze(f'{KIT}/lantern-post-v2-pixelated.glb')
    old = analyze(f'{KIT}/lantern-post-pixelated.glb', nb=10)
    print(json.dumps({'old_H': round(old['H'], 4), 'v2_H': round(v2['H'], 4), 'v3_H': round(v3['H'], 4),
                      'scale_factor_v2_over_v3': round(v2['H'] / v3['H'], 4),
                      'scale_factor_old_over_v3': round(old['H'] / v3['H'], 4)}))
