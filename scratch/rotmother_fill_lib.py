"""Rot Mother surgery: earcut hole-filling module (PCA projection + cycle walk).
python3 -c  # library file — imported by rotmother_surgery_full2.py
"""
import numpy as np
import mapbox_earcut as ec


def boundary_edges(f):
    e = np.vstack([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]])
    e = np.sort(e, axis=1)
    uk, cnt = np.unique(e, axis=0, return_counts=True)
    return uk[cnt == 1]


def kept_rim_dirs(f, rim_nodes):
    """Direction of rim edges as traversed in kept faces: set of (a,b)."""
    ke = np.vstack([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]])
    sel = np.isin(ke[:, 0], rim_nodes) & np.isin(ke[:, 1], rim_nodes)
    return set(map(tuple, ke[sel].tolist()))


def fill_loops(v, f, max_loop=400, rounds=5, verbose=True):
    """Cycle-walk boundary edges, PCA-plane earcut each cycle, repair orient."""
    total = 0
    residual = 0
    for rnd in range(rounds):
        bnd = boundary_edges(f)
        if len(bnd) == 0:
            break
        adj = {}
        for a, c in bnd:
            adj.setdefault(int(a), []).append(int(c))
            adj.setdefault(int(c), []).append(int(a))
        used = set()
        cycles = []
        for a0, c0 in bnd:
            key = (int(a0), int(c0))
            if key in used:
                continue
            used.add(key)
            cyc = [int(a0), int(c0)]
            guard = 0
            while cyc[-1] != cyc[0] and guard < 8000:
                guard += 1
                cur = cyc[-1]
                cand = [w for w in adj.get(cur, [])
                        if (min(cur, w), max(cur, w)) not in used]
                if not cand:
                    break
                w = cand[0]
                used.add((min(cur, w), max(cur, w)))
                cyc.append(w)
            if cyc[-1] == cyc[0] and len(cyc) >= 4:
                cycles.append(cyc[:-1])
        if verbose:
            print(f'  fill round {rnd}: bnd {len(bnd)} cycles {len(cycles)}')
        if not cycles:
            break
        added = 0
        for cyc in cycles:
            if len(cyc) > max_loop:
                if verbose:
                    print(f'  SKIP cycle len {len(cyc)} > {max_loop}')
                continue
            pts = v[np.asarray(cyc)]
            ctr = pts.mean(axis=0)
            P = pts - ctr
            _, _, Vt = np.linalg.svd(P, full_matrices=False)
            u = P @ Vt[0]
            wv = P @ Vt[1]
            p2 = np.stack([u, wv], axis=1).astype(np.float32)
            L = len(cyc)
            try:
                tri = np.asarray(ec.triangulate_float32(
                    p2, np.array([L], dtype=np.uint32)), dtype=np.int64)
                tri = tri.reshape(-1, 3)
            except Exception as ex:
                if verbose:
                    print('  earcut fail', ex)
                tri = None
            lnodes = np.asarray(cyc, dtype=np.int64)
            ked = kept_rim_dirs(f, lnodes)
            if tri is None or len(tri) < L - 3:
                cv = len(v)
                v = np.vstack([v, ctr[None, :]])
                T = np.array([[lnodes[i], lnodes[(i + 1) % L], cv]
                              for i in range(L)], dtype=np.int64)
            else:
                T = lnodes[tri]
            # orientation repair: each new tri's rim edges must run OPPOSITE
            # to the kept faces' rim-edge direction
            T2 = T
            flips = 0
            for t in range(len(T2)):
                edges = ((T2[t][0], T2[t][1]), (T2[t][1], T2[t][2]),
                         (T2[t][2], T2[t][0]))
                hits = sum(1 for e2 in edges if e2 in ked)
                if hits >= 2:
                    T2[t] = T2[t][::-1]
                    flips += 1
            f = np.vstack([f, T2])
            added += 1
        total += added
        resid = len(boundary_edges(f))
        if verbose:
            print(f'  fill round {rnd}: filled {added} residual-bnd {resid}')
        if added == 0:
            residual = resid
            break
    return v, f, total, len(boundary_edges(f))