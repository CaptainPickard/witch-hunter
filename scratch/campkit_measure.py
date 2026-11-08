import numpy as np, trimesh, sys
sys.path.insert(0, 'art-direction/3d')
sc = trimesh.load('scratch/campkitgen/wh-campkit-meshy-dec30k.glb', force='mesh')
tex = sc.visual.material.baseColorTexture
arr = np.asarray(tex.convert('RGB')).astype(float)
H, W = arr.shape[:2]
uvc = np.asarray(sc.visual.uv)[sc.faces]
fuv = uvc.mean(axis=1)
px = np.clip((fuv[:, 0] % 1.0) * (W - 1), 0, W - 1).astype(int)
py = np.clip((1 - fuv[:, 1] % 1.0) * (H - 1), 0, H - 1).astype(int)
col = arr[py, px]
lum = col @ np.array([0.299, 0.587, 0.114])
fc = np.asarray(sc.triangles_center)
x, y, z = fc[:, 0], fc[:, 1], fc[:, 2]

canvas = (lum >= 88) & (x < -0.20) & (y > -0.43)
C = np.where(canvas)[0]
print('canvas faces', len(C))
for lbl, ax in (('x', x), ('y', y), ('z', z)):
    print(f'  canvas {lbl}: {ax[C].min():+.3f} .. {ax[C].max():+.3f}  (ext {ax[C].max()-ax[C].min():.3f})')

bed = (x > 0.14) & (x < 0.42) & (y > -0.43)
print('bedroll-region faces', int(bed.sum()))
for lbl, ax, s in (('x', x[:, None], None), ):
    pass
print('  bed x: %+.3f..%+.3f  y: %+.3f..%+.3f  z: %+.3f..%+.3f' % (
    x[bed].min(), x[bed].max(), y[bed].min(), y[bed].max(), z[bed].min(), z[bed].max()))
bestr = np.where(bed)[0]
above = bestr[y[bestr] > -0.38]
print('  bedroll above-floor subset:', len(above), 'y-ext %.3f' % (y[above].max() - y[above].min()))

pit = (x > 0.42) & (np.abs(z) < 0.42) & (y > -0.40)
print('pit-region faces', int(pit.sum()))
print('  pit x: %+.3f..%+.3f  y: %+.3f..%+.3f  z: %+.3f..%+.3f' % (
    x[pit].min(), x[pit].max(), y[pit].min(), y[pit].max(), z[pit].min(), z[pit].max()))

pegs = (y < -0.15) & (y > -0.43) & (lum < 70) & ((np.abs(z) > 0.55) | (np.abs(x) > 0.84))
print('peg faces', int(pegs.sum()))
if pegs.sum():
    p = np.where(pegs)[0]
    print('  peg x: %+.3f..%+.3f  z: %+.3f..%+.3f' % (x[p].min(), x[p].max(), z[p].max(), z[p].max()))
    # cluster pegs by rounding
    key = np.round(np.stack([x[p], z[p]], 1) / 0.15).astype(int)
    uniq = np.unique(key, axis=0)
    print('  peg clusters (0.15 grid):', len(uniq), uniq.tolist())

floor = y <= -0.40
print('floor faces (y<=-0.40):', int(floor.sum()))
print('  floor x: %+.3f..%+.3f  z: %+.3f..%+.3f' % (x[floor].min(), x[floor].max(), z[floor].min(), z[floor].max()))
print('  floor y histogram:', np.unique(y[floor].round(3), return_counts=True))