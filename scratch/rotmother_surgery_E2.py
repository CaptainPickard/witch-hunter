"""Refit E+G: feathered leg/talon push from stage D, then smoothing + export.
python3 scratch/rotmother_surgery_E2.py /tmp/wh_stage_D_v.npy /tmp/wh_stage_D_f.npy OUT.glb
"""
import sys
import numpy as np
import trimesh
import scipy.sparse as sp
sys.path.insert(0, 'scratch')
from rotmother_fill_lib import fill_loops

vs, fs = sys.argv[1], sys.argv[2]
OUT = sys.argv[3]
v = np.load(vs)
f = np.load(fs)
print(f'LOAD D-stage V{len(v)} F{len(f)}')


def bf(v):
    return v[:, 0], -v[:, 2], v[:, 1]


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


# ---- E2: feathered leg push ----
bX, bY, bZ = bf(v)
# z-feather: 0 at -0.24 (belly floor) -> 1 at -0.38, hold to -0.92
tz = np.clip((-bZ - 0.24) / 0.14, 0, 1)
# x-window: 0 at 0.06 (centerline) -> 1 at 0.17 -> 1 at 0.32 -> 0 at 0.40
tx = np.clip((np.abs(bX) - 0.06) / 0.11, 0, 1) * \
     np.clip((0.40 - np.abs(bX)) / 0.08, 0, 1)
w = (tz * tx)
# foot emphasis: keep talons strong
foot = (bZ <= -0.75)
w = np.where(foot, w * 1.15, w)
w = np.clip(w, 0, 1)
print('E2 verts active', int((w > 0.01).sum()), 'max w', round(float(w.max()), 2))
push = 0.09 * w
nv = v.copy()
nv[:, 0] = bX + np.sign(bX + 1e-12) * push
print(f'  leg max|x| before {np.abs(bX[bZ <= -0.30]).max():.3f} '
      f'after {np.abs(nv[:, 0][bZ <= -0.30]).max():.3f}')
v = nv
stats('E2', v, f)

# ---- F: local smoothing + final fill ----
bX, bY, bZ = bf(v)
mouthz = (bZ >= 0.50) & (bZ <= 0.78) & (np.abs(bX) < 0.17) & (bY <= -0.06)
v = smooth_region(v, f, mouthz, iters=3, lam=0.40, ring=1)
drippz = (bZ >= -0.60) & (bZ <= -0.20) & (np.abs(bX) < 0.20) & (bY >= -0.25) & (bY <= 0.10)
v = smooth_region(v, f, drippz, iters=3, lam=0.40, ring=1)
legz = (bZ <= -0.20) & (bZ > -0.95)
v = smooth_region(v, f, legz, iters=2, lam=0.45, ring=1)
v, f, tot, resid = fill_loops(v, f, max_loop=1500, rounds=2)


def drop_tiny_comps(v, f, min_faces=12):
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


v, f = drop_tiny_comps(v, f, 12)
stats('F', v, f)
bX, bY, bZ = bf(v)
print('CHECK head max|x|', round(float(np.abs(v[bZ >= 0.82, 0]).max()), 3))
print('CHECK legs max|x|', round(float(np.abs(bX[bZ <= -0.30]).max()), 3))
print('CHECK feet max|x|', round(float(np.abs(bX[bZ <= -0.75]).max()), 3))
trimesh.Trimesh(v, f, process=False).export(OUT)
print('WROTE', OUT, 'V', len(v), 'F', len(f))