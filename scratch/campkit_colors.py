#!/usr/bin/env python3
"""Texel color statistics per region: find brightness/saturation separations
between dirt slab, canvas, charred stubs, stones, bedroll.
  campkit_colors.py <glb>
"""
import numpy as np, trimesh, sys
src = sys.argv[1]
m = trimesh.load(src, force='mesh')
tex = m.visual.material.baseColorTexture
arr = np.asarray(tex.convert('RGB')).astype(float)
H, W = arr.shape[:2]
uv = np.asarray(m.visual.uv)
fuv = uv[m.faces].mean(axis=1)
px = np.clip((fuv[:, 0] % 1.0) * (W - 1), 0, W - 1).astype(int)
py = np.clip((1 - fuv[:, 1] % 1.0) * (H - 1), 0, H - 1).astype(int)
col = arr[py, px]
lum = col @ np.array([0.299, 0.587, 0.114])
sat = col.max(1) - col.min(1)
fc = np.asarray(m.triangles_center)
r = (fc[:, 0] - fc[:, 0].mean())
# region x-bins
import collections
def stats(name, sel):
    c = col[sel]
    print(f'{name:14s} n={int(sel.sum()):6d} lum {lum[sel].mean():6.1f}±{lum[sel].std():5.1f} '
          f'sat {sat[sel].mean():5.1f} rgb {c.mean(0).round(0).tolist()}')
print('regions by x (luma distribution):')
for x0 in np.arange(-1.0, 1.0, 0.2):
    sel = (fc[:, 0] >= x0) & (fc[:, 0] < x0 + 0.2)
    if sel.sum() < 100:
        continue
    l = lum[sel]
    u, cnts = np.unique(l.round(0), return_counts=True)
    keep = cnts > cnts.max() * 0.05
    lst = list(zip(u[keep], cnts[keep]))[:14]
    peaks = ' '.join(f'{int(uu)}({int(cc)})' for uu, cc in lst)
    print(f'x[{x0:+.1f},{x0+0.2:+.1f}] n={int(sel.sum()):5d}: {peaks}')
print()
print('y levels (all faces):')
for y0, y1 in [(-0.45, -0.37), (-0.37, -0.25), (-0.25, -0.10), (-0.10, 0.05), (0.05, 0.20), (0.20, 0.45)]:
    sel = (fc[:, 1] >= y0) & (fc[:, 1] < y1)
    stats(f'y[{y0:+.2f},{y1:+.2f})', sel)
print()
print('color class shares per x-window:')
classes = {
    'dark<45': lum < 45,
    'dull45-90': (lum >= 45) & (lum < 90),
    'mid90-140': (lum >= 90) & (lum < 140),
    'light140+': lum >= 140,
    'sat>35': sat > 35,
}
for x0 in np.arange(-1.0, 1.0, 0.25):
    selx = (fc[:, 0] >= x0) & (fc[:, 0] < x0 + 0.25) & (np.abs(fc[:, 1] + 0.40) < 0.004)
    selo = (fc[:, 0] >= x0) & (fc[:, 0] < x0 + 0.25) & (fc[:, 1] > -0.37)
    if selx.sum() < 30:
        continue
    row = ' '.join(f'{k}={100*v[selx].sum()/max(selx.sum(),1):.0f}%' for k, v in classes.items())
    row2 = ' '.join(f'{k}={100*v[selo].sum()/max(selo.sum(),1):.0f}%' for k, v in classes.items())
    print(f'x[{x0:+.2f},{x0+0.25:+.2f}] FLOOR y≈-0.42: {row}')
    print(f'      {"":16s} ABOVE-floor  : {row2}')