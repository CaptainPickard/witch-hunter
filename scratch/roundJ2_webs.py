"""Round J2: 'web' fill for see-through slits between root flares and trunk.
Voxelises the tree base (vertical-ray parity, odd columns dropped), applies a
3D morphological closing, and keeps only the NEW voxels (closed & ~inside)
connected to the base: those are the slits/crotches narrower than ~2*RC.
Surface = naive surface nets over (web | inside-mesh voxels next to the web),
so the web's seam with the original mesh is buried inside the original
shell. Then Taubin smoothing. Adds mass only; never removes flare geometry.
Used by roundJ2_rootpad.py; webs(P, F, ymin, ax) -> (V, faces, stats)."""
import numpy as np
from scipy import ndimage

VOX = float(__import__("os").environ.get("J2_VOX", 0.008))   # GLB units (8 cm at scale 10)
RC = int(__import__("os").environ.get("J2_RC", 6))   # closing radius in voxels (0.048: gaps up to ~0.1 wide)
DECIM = float(__import__("os").environ.get("J2_DECIM", 0.90))  # fast_simplification target_reduction
LEAK = bool(int(__import__("os").environ.get("J2_LEAK", 1)))   # keep only see-through webs
SHEET = bool(int(__import__("os").environ.get("J2_SHEET", 0)))
PIN = bool(int(__import__("os").environ.get("J2_PIN", 0)))  # pin sheet borders during smoothing
HTOP = 0.30       # base band height above ymin (3 m)


def ball(r):
    g = np.mgrid[-r:r + 1, -r:r + 1, -r:r + 1]
    return (g ** 2).sum(0) <= r * r


def occupancy(P, F, ymin, lo, hi):
    nx, nz = int((hi[0] - lo[0]) / VOX), int((hi[1] - lo[1]) / VOX)
    ny = int(HTOP / VOX)
    occ = np.zeros((nx, ny, nz), bool)
    hits = [[[] for _ in range(nz)] for _ in range(nx)]
    T = P[F]
    T = T[(T[:, :, 1].min(1) < ymin + HTOP + 0.05)]
    jit = np.array([1.37e-5, 2.11e-5])          # avoid rays through edges
    for t in T:
        xs, zs = t[:, 0], t[:, 2]
        i0 = max(int(np.floor((xs.min() - lo[0]) / VOX - 0.5)), 0)
        i1 = min(int(np.ceil((xs.max() - lo[0]) / VOX - 0.5)), nx - 1)
        k0 = max(int(np.floor((zs.min() - lo[1]) / VOX - 0.5)), 0)
        k1 = min(int(np.ceil((zs.max() - lo[1]) / VOX - 0.5)), nz - 1)
        if i1 < i0 or k1 < k0: continue
        ii, kk = np.meshgrid(np.arange(i0, i1 + 1), np.arange(k0, k1 + 1), indexing='ij')
        X = lo[0] + (ii + 0.5) * VOX + jit[0]; Z = lo[1] + (kk + 0.5) * VOX + jit[1]
        a, b, c = t
        den = (b[2] - c[2]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[2] - c[2])
        if abs(den) < 1e-14: continue
        l1 = ((b[2] - c[2]) * (X - c[0]) + (c[0] - b[0]) * (Z - c[2])) / den
        l2 = ((c[2] - a[2]) * (X - c[0]) + (a[0] - c[0]) * (Z - c[2])) / den
        l3 = 1 - l1 - l2
        m = (l1 >= 0) & (l2 >= 0) & (l3 >= 0)
        Y = l1 * a[1] + l2 * b[1] + l3 * c[1]
        for i, k, yy in zip(ii[m], kk[m], Y[m]):
            hits[i][k].append(yy)
    odd = 0
    for i in range(nx):
        for k in range(nz):
            h = sorted(hits[i][k])
            if len(h) % 2: odd += 1; continue
            for y0, y1 in zip(h[0::2], h[1::2]):
                j0 = max(int(np.ceil((y0 - ymin) / VOX - 0.5)), 0)
                j1 = min(int(np.floor((y1 - ymin) / VOX - 0.5)), ny - 1)
                if j1 >= j0: occ[i, j0:j1 + 1, k] = True
    return occ, odd


def surface_nets(G, lo3, solid=None):
    """naive surface nets: one vertex per mixed 2x2x2 cell (cell centre), quads
    across every in/out voxel face. Returns V (world), faces (tri)."""
    Gp = np.pad(G, 1)
    Sp = np.pad(solid, 1) if solid is not None else np.zeros_like(Gp)
    nx, ny, nz = Gp.shape
    cell = np.zeros((nx - 1, ny - 1, nz - 1), np.int64) - 1
    s = (Gp[:-1, :-1, :-1].astype(int) + Gp[1:, :-1, :-1] + Gp[:-1, 1:, :-1] + Gp[:-1, :-1, 1:] +
         Gp[1:, 1:, :-1] + Gp[1:, :-1, 1:] + Gp[:-1, 1:, 1:] + Gp[1:, 1:, 1:])
    mixed = (s > 0) & (s < 8)
    idx = np.argwhere(mixed)
    cell[mixed] = np.arange(len(idx))
    V = lo3 + idx * VOX                           # padded cell c = centre of voxels c-1..c
    quads, outd = [], []
    for ax in range(3):
        o = [d for d in range(3) if d != ax]
        a = np.moveaxis(Gp, ax, 0)
        diff = a[1:] != a[:-1]                   # face between voxel i and i+1 along ax
        sa = np.moveaxis(Sp, ax, 0)
        # outside voxel of the face must be air (not the original solid)
        diff = diff & ~np.where(a[:-1], sa[1:], sa[:-1])
        pos = np.argwhere(diff)
        sign = np.where(a[:-1][diff], 1.0, -1.0)  # outward = +ax if voxel i is inside
        ids = []
        for dj, dk in ((-1, -1), (0, -1), (0, 0), (-1, 0)):
            cc = np.zeros((len(pos), 3), int)
            cc[:, ax] = pos[:, 0]; cc[:, o[0]] = pos[:, 1] + dj; cc[:, o[1]] = pos[:, 2] + dk
            ids.append(cell[cc[:, 0], cc[:, 1], cc[:, 2]])
        ids = np.stack(ids, 1)
        good = ids.min(1) >= 0
        quads.append(ids[good])
        d = np.zeros((good.sum(), 3)); d[:, ax] = sign[good]; outd.append(d)
    Q = np.vstack(quads); D = np.vstack(outd)
    tris = np.vstack([Q[:, [0, 1, 2]], Q[:, [0, 2, 3]]]); D = np.vstack([D, D])
    fn = np.cross(V[tris[:, 1]] - V[tris[:, 0]], V[tris[:, 2]] - V[tris[:, 0]])
    flip = (fn * D).sum(1) < 0
    tris[flip] = tris[flip][:, ::-1]
    return V, tris


def taubin(V, tris, it=int(__import__("os").environ.get("J2_SMOOTH", 120)), lam=0.5, mu=-0.53, pin=None):
    n = len(V)
    E = np.vstack([tris[:, [0, 1]], tris[:, [1, 2]], tris[:, [2, 0]]])
    E = np.vstack([E, E[:, ::-1]])
    deg = np.bincount(E[:, 0], minlength=n).astype(float)
    for _ in range(it):
        for f in (lam, mu):
            acc = np.zeros_like(V); np.add.at(acc, E[:, 0], V[E[:, 1]])
            dV = f * (acc / np.maximum(deg, 1)[:, None] - V)
            if pin is not None: dV[pin] = 0
            V = V + dV
    return V


def _crop(a, shape):
    o = [(a.shape[i] - shape[i]) // 2 for i in range(3)]
    return a[o[0]:o[0] + shape[0], o[1]:o[1] + shape[1], o[2]:o[2] + shape[2]]


def leak_marks(occ, W):
    """rotate the volumes so each view direction is axis 0, then a column with
    web voxels and no solid voxels is a see-through ray; rotate its web voxels
    back. 18 axis directions (= 36 azimuths) x 4 elevations (eye-level views)."""
    marked = np.zeros_like(W)
    for az in range(0, 180, 10):                 # +-axis 0 covers az and az+180
        o1 = ndimage.rotate(occ, az, axes=(0, 2), order=0)
        w1 = ndimage.rotate(W, az, axes=(0, 2), order=0)
        for el in (-15, -5, 5, 15):
            o2 = ndimage.rotate(o1, el, axes=(0, 1), order=0)
            w2 = ndimage.rotate(w1, el, axes=(0, 1), order=0)
            leak = ~o2.any(0) & w2.any(0)
            if not leak.any(): continue
            m2 = w2 & leak[None]
            m1 = _crop(ndimage.rotate(m2, -el, axes=(0, 1), order=0), o1.shape)
            m0 = _crop(ndimage.rotate(m1, -az, axes=(0, 2), order=0), occ.shape)
            marked |= m0
    return ndimage.binary_dilation(marked, structure=ball(2))


def webs(P, F, ymin, ax, rmax):
    lo = ax - rmax; hi = ax + rmax
    occ, odd = occupancy(P, F, ymin, lo, hi)
    pad = RC + 1
    O = np.pad(occ, pad)
    C = ndimage.binary_closing(O, structure=ball(RC))
    W = (C & ~O)[pad:-pad, pad:-pad, pad:-pad]
    W[:, :2, :] = False                            # ground contact is the pad's job
    # keep only the web voxels that sit on a see-through line of sight: march
    # parallel rays (36 azimuths x 4 elevations, the low eye-level views) through
    # the grid; a ray that crosses web voxels but never hits the original solid
    # is a sky window. Crotch fillets off those paths are dropped (no clutter).
    W = W & leak_marks(occ, W) if LEAK else W
    lab, nl = ndimage.label(W)
    sizes = ndimage.sum(W, lab, range(1, nl + 1)) if nl else np.array([])
    W = np.isin(lab, 1 + np.where(sizes >= 8)[0])
    if not W.any():
        return np.zeros((0, 3)), np.zeros((0, 3), int), dict(odd=odd, webvox=0)
    # closed web volumes (SHEET=1: web/air faces only, open borders - cracks
    # after smoothing/decimation). Web/solid faces face INTO the original solid
    # so they're occluded by it; a closed volume survives smoothing watertight.
    V, T = surface_nets(W, np.array([lo[0], ymin, lo[1]]), solid=occ if SHEET else None)
    used = np.unique(T); remap = -np.ones(len(V), int); remap[used] = np.arange(len(used))
    V, T = V[used], remap[T]
    E = np.sort(np.vstack([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]), 1)
    ue, cnt = np.unique(E, axis=0, return_counts=True)
    pin = np.unique(ue[cnt == 1])
    V = taubin(V, T, pin=pin if PIN else None)
    V[:, 1] = np.maximum(V[:, 1], ymin + 0.0005)  # never below the grounding vertex
    nraw = len(T)
    import fast_simplification
    V2, T2 = fast_simplification.simplify(V.astype(np.float32), T.astype(np.int32), target_reduction=DECIM)
    V2 = np.asarray(V2, float); T2 = np.asarray(T2, int)
    V2[:, 1] = np.maximum(V2[:, 1], ymin + 0.0005)
    return V2, T2, dict(odd=odd, webvox=int(W.sum()), comps=int((sizes >= 8).sum()),
                        raw_faces=nraw, pinned=len(pin))
