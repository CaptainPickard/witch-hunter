"""Rot Mother delta surgery v2 (final) — uses rotmother_fill_lib.
Masks in Blender space; region paint vision-verified.
Run: python3 scratch/rotmother_surgery_full2.py IN.glb OUT.glb [DRY]
"""
import sys
import numpy as np
import trimesh
import scipy.sparse as sp
sys.path.insert(0, 'scratch')
from rotmother_fill_lib import boundary_edges, fill_loops

IN, OUT = sys.argv[1], sys.argv[2]
DRY = len(sys.argv) > 3 and 'DRY' in sys.argv[3].upper()

m = trimesh.load(IN, force='mesh', process=False)
v = np.asarray(m.vertices, dtype=np.float64)
f = np.asarray(m.faces, dtype=np.int64)
print(f'LOAD V{len(v)} F{len(f)}')
spans = v.max(0) - v.min(0)
assert abs(spans[1] - 1.906) < 0.03, f'unexpected spans {spans}'


def bf(v):
    return v[:, 0], -v[:, 2], v[:, 1]


def cent_bl(v, f):
    c = v[f].mean(axis=1)
    return c[:, 0], -c[:, 2], c[:, 1]


def drop_tiny_comps(v, f, min_faces=6):
    mesh = trimesh.Trimesh(v, f, process=True)
    lab = trimesh.graph.connected_component_labels(mesh.face_adjacency,
                                                   node_count=len(f))
    n = np.bincount(lab)
    small = np.where(n < min_faces)[0]
    if len(small) == 0:
        print('  no tiny comps')
        return v, f
    keepm = ~np.isin(lab, small)
    f2 = f[keepm]
    verts = np.unique(f2)
    remap = -np.ones(len(v), dtype=np.int64)
    remap[verts] = np.arange(len(verts))
    print(f'  dropped {len(small)} comps ({int(n[small].sum())} faces)')
    return v[verts], remap[f2]


def v_adj(v, f):
    e = np.vstack([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]])
    A = sp.csr_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])),
                      shape=(len(v), len(v)))
    A = A + A.T
    A.data[:] = 1.0
    return A


def smooth_region(v, f, vmask, iters, lam, ring):
    A = v_adj(v, f)
    deg = np.maximum(np.asarray(A.sum(axis=1)).ravel(), 1.0)
    D = sp.diags(1.0 / deg)
    L = D @ A
    nv = v.copy()
    active = vmask.copy()
    for it in range(iters):
        delta = (L @ nv) - nv
        w = lam * np.where(active, 1.0, 0.0)
        nv = nv + (w[:, None] * delta)
        if ring and it < iters - 1:
            grow = np.asarray(A @ active.astype(float)).ravel() > 0
            active = active | grow
    return nv


def stats(tag, v, f):
    mesh = trimesh.Trimesh(v, f, process=True)
    lab = trimesh.graph.connected_component_labels(mesh.face_adjacency,
                                                   node_count=len(f))
    n = np.bincount(lab)
    print(f'[{tag}] V{len(v)} F{len(f)} comps {len(n)} '
          f'outside-largest {int(n.sum() - n.max())} '
          f'({(n.sum() - n.max()) / n.sum() * 100:.3f}%)')


def save(stage, v, f):
    np.save(f'/tmp/wh_stage_{stage}_v.npy', v)
    np.save(f'/tmp/wh_stage_{stage}_f.npy', f)


# ---------- STEP 0 ----------
print('== STEP 0 tiny comps ==')
v, f = drop_tiny_comps(v, f, 6)
stats('0', v, f)
if not DRY:
    save('0', v, f)

cX, cY, cZ = cent_bl(v, f)

# ---------- STEP A: drips ----------
print('== STEP A drips ==')
zone = (cZ < -0.24) & (cZ > -0.60) & (np.abs(cX) < 0.18) & (cY >= -0.25) & (cY <= 0.10)
zidx = np.where(zone)[0]
cells = {}
for t in zidx:
    key = (int(np.floor((cX[t] + 0.6) / 0.02)),
           int(np.floor((cY[t] + 0.6) / 0.02)),
           int(np.floor((cZ[t] + 0.6) / 0.02)))
    cells.setdefault(key, []).append(t)
keys = list(cells)
kset = set(keys)
parent = {k: k for k in keys}


def find(a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]
        a = parent[a]
    return a


for (i, j, k) in keys:
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                nb = (i + dx, j + dy, k + dz)
                if nb in kset:
                    ra, rc = find((i, j, k)), find(nb)
                    if ra != rc:
                        parent[ra] = rc
groups = {}
for k in keys:
    groups.setdefault(find(k), []).extend(cells[k])
drop = []
for r, fl in sorted(groups.items(), key=lambda g: -len(g[1])):
    fx = cX[fl]
    fz = cZ[fl]
    if (fx.max() - fx.min()) < 0.07 and fz.min() < -0.30:
        drop.append(fl)
        print(f'  DROP f{len(fl)} x[{fx.min():+.3f}..{fx.max():+.3f}] z[{fz.min():+.3f}..{fz.max():+.3f}]')
    else:
        print(f'  KEEP f{len(fl)} x[{fx.min():+.3f}..{fx.max():+.3f}] z[{fz.min():+.3f}..{fz.max():+.3f}]')
if drop and not DRY:
    drop_faces = np.concatenate(drop)
    print('drip delete faces', len(drop_faces))
    keep = np.ones(len(f), dtype=bool)
    keep[drop_faces] = False
    f = f[keep]
    v, f, tot, resid = fill_loops(v, f, max_loop=140, rounds=3)
    v, f = drop_tiny_comps(v, f, 12)
    stats('A', v, f)
    save('A', v, f)
    cX, cY, cZ = cent_bl(v, f)
elif DRY:
    for r, fl in drop:
        pass
    print('DRY: would delete', sum(len(x) for x in drop), 'faces')

# ---------- STEP B: mouth ----------
print('== STEP B mouth ==')
nn = np.cross(v[f][:, 1] - v[f][:, 0], v[f][:, 2] - v[f][:, 0])
nl = np.linalg.norm(nn, axis=1, keepdims=True)
nl[nl == 0] = 1
nny = -(nn / nl)[:, 2]
rec = (cZ >= 0.53) & (cZ <= 0.74) & (np.abs(cX) < 0.16) & (cY <= -0.10) & (nny > 0.30)
print('recess faces', int(rec.sum()))
if not DRY and rec.sum():
    keep = np.ones(len(f), dtype=bool)
    keep[rec] = False
    f = f[keep]
    v, f, tot, resid = fill_loops(v, f, max_loop=1200, rounds=6)
    v, f = drop_tiny_comps(v, f, 12)
    bX, bY, bZ = bf(v)
    vmz = (bZ >= 0.50) & (bZ <= 0.78)
    vmx = np.abs(bX) < 0.17
    vmy = (bY <= -0.06) & (bY >= -0.46)
    vmask = vmz & vmx & vmy
    print('mouth smooth verts', int(vmask.sum()))
    v = smooth_region(v, f, vmask, iters=7, lam=0.55, ring=2)
    stats('B', v, f)
    save('B', v, f)
elif DRY:
    print('DRY: would delete', int(rec.sum()), 'mouth recess faces')

# ---------- STEP C: head shrink ----------
print('== STEP C head shrink ==')
bX, bY, bZ = bf(v)
ZPIV = 0.79
skull = (bZ >= 0.79) & (bZ <= 0.95) & (np.abs(bX) < 0.30)
crest = (bZ >= 0.79) & (bZ <= 0.95) & (np.abs(bX) >= 0.30)
hold = crest & (bZ > 0.845)
w = np.zeros(len(v))
w[skull] = 0.90
w[crest] = 0.65
w[hold] = 0.0
taper = np.clip((bZ - 0.76) / 0.06, 0, 1)
w = w * taper
print('w: active', int((w > 0).sum()), 'max', round(float(w.max()), 2))
if not DRY:
    nv = v.copy()
    nv[:, 0] = bX * (1.0 - 0.30 * w)
    nv[:, 1] = ZPIV + (bZ - ZPIV) * (1.0 - 0.20 * w)
    v = nv
    stats('C', v, f)
    save('C', v, f)

# ---------- STEP D: hips ----------
print('== STEP D hips ==')
bX, bY, bZ = bf(v)
hip = (bY <= 0.10) & (bY >= -0.24) & (bZ >= -0.58) & (bZ <= -0.24) & (np.abs(bX) >= 0.12)
print('hip verts', int(hip.sum()))
if not DRY:
    push = 0.055 * np.clip(1.0 - (np.abs(bX) - 0.12) / 0.18, 0.30, 1.0)
    nv = v.copy()
    nv[:, 0] = bX + np.sign(bX + 1e-12) * push * hip
    print(f'  hip max|x| {np.abs(bX[hip]).max():.3f} -> {np.abs(nv[:, 0][hip]).max():.3f}')
    v = nv
    mask_h = (bY <= 0.10) & (bY >= -0.24) & (bZ >= -0.58) & (bZ <= -0.24)
    v = smooth_region(v, f, mask_h, iters=2, lam=0.5, ring=1)
    stats('D', v, f)
    save('D', v, f)

# ---------- STEP E: legs + talons ----------
print('== STEP E legs ==')
bX, bY, bZ = bf(v)
legs = (bZ <= -0.20) & (np.abs(bX) >= 0.09) & (np.abs(bX) < 0.30)
print('leg verts', int(legs.sum()))
if not DRY:
    push = 0.085 * np.clip((0.30 - np.abs(bX)) / 0.16, 0.25, 1.0)
    nv = v.copy()
    nv[:, 0] = bX + np.sign(bX + 1e-12) * push * legs
    print(f'  leg max|x| {np.abs(bX[legs]).max():.3f} -> {np.abs(nv[:, 0][legs]).max():.3f}')
    v = nv
    mask_l = (bZ <= -0.20) & (np.abs(bX) < 0.34)
    v = smooth_region(v, f, mask_l, iters=2, lam=0.5, ring=1)
    stats('E', v, f)
    save('E', v, f)

# ---------- STEP F ----------
print('== STEP F smoothing ==')
if not DRY:
    bX, bY, bZ = bf(v)
    mouthz = (bZ >= 0.50) & (bZ <= 0.78) & (np.abs(bX) < 0.17) & (bY <= -0.06)
    v = smooth_region(v, f, mouthz, iters=3, lam=0.4, ring=1)
    drippz = (bZ >= -0.60) & (bZ <= -0.20) & (np.abs(bX) < 0.20) & (bY >= -0.25) & (bY <= 0.10)
    v = smooth_region(v, f, drippz, iters=3, lam=0.4, ring=1)
    v, f, tot, resid = fill_loops(v, f, max_loop=1500, rounds=2)
    v, f = drop_tiny_comps(v, f, 12)
    stats('F', v, f)
    save('F', v, f)
    bX, bY, bZ = bf(v)
    print('CHECK head max|x|', round(float(np.abs(v[bZ >= 0.82, 0]).max()), 3))
    print('CHECK legs max|x|', round(float(np.abs(bX[bZ <= -0.30]).max()), 3))
    print('CHECK feet max|x|', round(float(np.abs(bX[bZ <= -0.75]).max()), 3))
    trimesh.Trimesh(v, f, process=False).export(OUT)
    print('WROTE', OUT, 'V', len(v), 'F', len(f))
print('DONE DRY' if DRY else 'DONE')