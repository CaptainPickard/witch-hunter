#!/usr/bin/env python3
"""Campkit bake v4 (2026-10-07): partition the decimated (30k, IO QA gate) Meshy
campsite into the four element meshes (tent, bedroll, firepit, pegs), uniform
scale so the tent ridge = 2.2 m, origin ground-centered between tent and pit,
bake the pixelated twin (512 NEAREST + 5-bit posterize, NORMAL injected).

Classification SPATIAL+color (rules verified against isolated textured renders
in scratch/campkitgen/probe/):
  canvas   = lum>=88, x<-0.20                      -> tent (+all leftovers:
             patch, poles, ropes - Meshy fuses them; raw mesh kept as-is)
  bedroll  = lum<95, 0.14<x<0.42, y>-0.405
  stoneish = lum>=85, ring r<0.28 @ (0.68,0)       -> firepit (stones)
  char     = lum<50,  ring r<0.28, x>0.48          -> firepit (charred stubs)
  pegs     = lum<62, non-horizontal, -0.43<y<-0.20, |z|>0.60 or |x|>0.84
  is_ground= y<=-0.405 (slab top+underside; faces excluded from all groups,
             ride tent node)

Scale: ONE uniform factor S = 2.2 / 1.199 where 1.199 m = canvas z-extent
measured incl. wall bottoms (scratch/campkit_measure.py). Tent lands
2.2 (ridge) x 1.34 (width) x ~1.46 (peak) - peak overshoots the brief's ~1.1
because the generator's proportions differ; uniform-only scale law noted in
report (CONFIG row can add engine-side tweak if Nicko wants).

Accent: amber tint ONLY on the pit stones' inner faces (horizontal, normal
pointing at ring center, low). Tint covers the exact 5-bit texels those faces
render through 512-NEAREST (4x4 blocks in the 2048 atlas).

Exports: art-direction/3d/assets/camp/wh-campkit.glb (raw tex) +
wh-campkit-pixelated.glb (posterized tex). Node names exactly
tent/bedroll/firepit/pegs; ground y=0; origin centered tent<->pit.
"""
import os, sys
import numpy as np
import trimesh
from PIL import Image
sys.path.insert(0, 'art-direction/3d')
from biome_pixelate import posterize512

BASE = 'art-direction/3d/assets/camp'
SRC = 'scratch/campkitgen/wh-campkit-meshy-dec30k.glb'
os.makedirs(BASE, exist_ok=True)

sc = trimesh.load(SRC, force='mesh')
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
fn = np.asarray(sc.face_normals)
x, y, z = fc[:, 0], fc[:, 1], fc[:, 2]

# ---------- classification ----------
is_ground = y <= -0.405
canvas = (~is_ground) & (lum >= 88) & (x < -0.20)
bedroll = (~is_ground) & (lum < 95) & (x > 0.14) & (x < 0.42) & (y > -0.405)
ring = ((x - 0.68) ** 2 + z ** 2) < 0.28 ** 2
stoneish = (~is_ground) & ring & (lum >= 85)
char = (~is_ground) & ring & (x > 0.48) & (lum < 50)
firepit = stoneish | char
pegs = (~is_ground) & (lum < 62) & (np.abs(fn[:, 1]) < 0.5) & (y > -0.43) & (y < -0.20) & (
    (np.abs(z) > 0.60) | (np.abs(x) > 0.84))

pit = firepit & ~bedroll
taken = np.zeros(len(fc), bool)
groups = {}
for nm, sel in (('bedroll', bedroll & ~pit), ('firepit', pit),
                ('pegs', pegs & ~pit & ~bedroll), ('tent', canvas)):
    groups[nm] = np.where(sel & ~taken)[0]
    taken |= sel
left = np.where(~taken)[0]
print('leftovers (ride tent node: patch/poles/ropes):', len(left))
groups['tent'] = np.concatenate([groups['tent'], left])
for nm in ('tent', 'bedroll', 'firepit', 'pegs'):
    print(f'  {nm:8s} faces {len(groups[nm]):6d}')

# ---------- uniform scale: tent ridge (= canvas z-extent incl wall bottoms) ----------
CM = np.where(canvas | ((lum >= 88) & (x < -0.20) & (y > -0.43)))[0]
ridge = z[CM].max() - z[CM].min()
S = 2.2 / ridge
print(f'canvas ridge (z, incl wall bottoms) {ridge:.3f} m -> uniform scale {S:.4f}')

meshes = {}
for nm in ('tent', 'bedroll', 'firepit', 'pegs'):
    sel = groups[nm]
    Fi = sc.faces[sel]
    meshes[nm] = [np.asarray(sc.vertices)[Fi.reshape(-1)] * S,
                  uvc[sel].reshape(-1, 2), len(Fi)]

# ---------- ground + origin (tent canvas center <-> pit ring center) ----------
ally = min(v[:, 1].min() for v, _, f in meshes.values() if f)
for nm in meshes:
    meshes[nm][0][:, 1] -= ally
tcx = 0.5 * (x[CM].min() + x[CM].max()) * S
pcx = 0.68 * S
midx = 0.5 * (tcx + pcx)
allv = np.vstack([v[0] for v in meshes.values()]) if all(meshes[nm][2] for nm in meshes) else None
zs = np.concatenate([v.reshape(-1, 3)[:, 2] for v, _, f in meshes.values() if f])
zmid = 0.5 * (zs.min() + zs.max())
for nm in meshes:
    meshes[nm][0][:, 0] -= midx
    meshes[nm][0][:, 2] -= zmid
kitx = np.concatenate([v.reshape(-1, 3)[:, 0] for v, _, f in meshes.values() if f])
kity = np.concatenate([v.reshape(-1, 3)[:, 1] for v, _, f in meshes.values() if f])
print(f'origin shift x {midx:.4f} z {zmid:.4f}; tent cx {tcx - midx:+.2f}, pit cx {pcx - midx:+.2f}')
print(f'kit bounds x {kitx.min():+.2f}..{kitx.max():+.2f}  y {kity.min():.3f}..{kity.max():.2f}  z {zs.min() - zmid:+.2f}..{zs.max() - zmid:+.2f}')

# ---------- amber accent: inner faces of the pit stones ----------
stone_faces = np.intersect1d(groups['firepit'], np.where(stoneish)[0])
sfc, sfn = fc[stone_faces], fn[stone_faces]
d = np.array([0.68, 0.0])[None, :] - sfc[:, [0, 2]]
d /= np.linalg.norm(d, axis=1, keepdims=True) + 1e-9
horiz = sfn[:, 1] < 0.8                      # not straight-up top faces
inward = (sfn[:, [0, 2]] * d).sum(1) > 0.45  # normals point at ring center
inner = stone_faces[horiz & inward & (sfc[:, 1] < -0.30)]
print('pit stone inner faces tinted:', len(inner), 'of', len(stone_faces))

tpx = np.asarray(tex.convert('RGB')).astype(np.uint8)
own = np.zeros((H, W), bool)
BLOCK = W // 512
for i in inner:
    fu = (uvc[i][:, 0] % 1.0).mean()
    fv = (1 - (uvc[i][:, 1] % 1.0)).mean()
    bx = int(min(W - 1, fu * (W - 1))) // BLOCK * BLOCK
    by = int(min(H - 1, fv * (H - 1))) // BLOCK * BLOCK
    own[by:by + BLOCK, bx:bx + BLOCK] = True
print('atlas 4x4 blocks tinted:', int(own.sum()), f'-> {int(own.sum()) // (BLOCK * BLOCK)} texels at 512 ({100.0 * own.sum() / (H * W):.3f}% atlas)')

tint = tpx.astype(float)
tint[..., 0] = np.where(own, tpx[..., 0] * 1.55 + 30, tpx[..., 0])
tint[..., 1] = np.where(own, tpx[..., 1] * 1.30 + 4, tpx[..., 1])
tint[..., 2] = np.where(own, tpx[..., 2] * 0.72 - 18, tpx[..., 2])
tinted = Image.fromarray(np.clip(tint, 0, 255).astype(np.uint8))

# ---------- export ----------
mat0 = sc.visual.material

def emit(path, texture):
    sc2 = trimesh.Scene()
    for nm in ('tent', 'bedroll', 'firepit', 'pegs'):
        V3, U3, F = meshes[nm]
        if F == 0:
            print('EMPTY NODE', nm); continue
        tm = trimesh.Trimesh(V3, np.arange(F * 3, dtype=np.int64).reshape(-1, 3), process=False)
        tm.vertex_normals      # force vertex NORMAL attribute into the GLB export
        mat = mat0.copy()
        mat.baseColorTexture = texture
        tm.visual = trimesh.visual.texture.TextureVisuals(uv=U3, material=mat, image=texture)
        sc2.add_geometry(tm, node_name=nm, geom_name=nm)
    sc2.export(path, file_type='glb')

emit(BASE + '/wh-campkit.glb', tinted)
emit(BASE + '/wh-campkit-pixelated.glb', posterize512(tinted))
print('wrote', BASE + '/wh-campkit.glb', os.path.getsize(BASE + '/wh-campkit.glb') // 1024, 'KB')
print('wrote', BASE + '/wh-campkit-pixelated.glb', os.path.getsize(BASE + '/wh-campkit-pixelated.glb') // 1024, 'KB')
tot = 0
for nm in ('tent', 'bedroll', 'firepit', 'pegs'):
    f = meshes[nm][2]; tot += f
    print(f'tris {nm}: {f}')
print('tris total:', tot)