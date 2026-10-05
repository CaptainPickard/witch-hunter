#!/usr/bin/env python3
"""Round J: trunk-underside gap of a tree GLB as the game grounds it.
Grounds like assets.js groundAlign (lowest vertex -> y=0), then casts rays
straight up from a grid inside the trunk footprint (r < rtrunk) and reports
the first-hit height. Gap = sky visible under the trunk = 'floating'.
usage: roundJ_underside.py <glb> [scale=10] [sink=0 (GLB units)]"""
import sys
import numpy as np
import trimesh

f = sys.argv[1]
scale = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
sink = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
m = trimesh.load(f, force='scene').to_geometry()
v = m.vertices
ymin, ymax = v[:, 1].min(), v[:, 1].max()
H = ymax - ymin
band = (v[:, 1] > ymin + 0.10 * H) & (v[:, 1] < ymin + 0.25 * H)
ax = np.median(v[band][:, [0, 2]], 0)
low = v[v[:, 1] < ymin + 3.0 / scale]
r = np.sort(np.linalg.norm(low[:, [0, 2]] - ax, axis=1))
rt = r[len(r) // 10]                        # trunk radius (same rule as render)
g = np.linspace(-rt, rt, 41)
gx, gz = np.meshgrid(g, g)
keep = gx**2 + gz**2 < rt**2
O = np.stack([gx[keep] + ax[0], np.full(keep.sum(), ymin - 1.0), gz[keep] + ax[1]], 1)
# vertical rays: 2D barycentric in xz over triangles near the base (no rtree)
T = m.triangles
T = T[T[:, :, 1].min(1) < ymin + 0.5 * H]
a, b, c = T[:, 0], T[:, 1], T[:, 2]
first = np.full(len(O), np.nan)
for i, o in enumerate(O):
    px, pz = o[0], o[2]
    d = (b[:, 2] - c[:, 2]) * (a[:, 0] - c[:, 0]) + (c[:, 0] - b[:, 0]) * (a[:, 2] - c[:, 2])
    ok = np.abs(d) > 1e-14
    d = np.where(ok, d, 1.0)
    l1 = ((b[:, 2] - c[:, 2]) * (px - c[:, 0]) + (c[:, 0] - b[:, 0]) * (pz - c[:, 2])) / d
    l2 = ((c[:, 2] - a[:, 2]) * (px - c[:, 0]) + (a[:, 0] - c[:, 0]) * (pz - c[:, 2])) / d
    l3 = 1 - l1 - l2
    ins = ok & (l1 >= 0) & (l2 >= 0) & (l3 >= 0)
    if ins.any():
        y = l1[ins] * a[ins, 1] + l2[ins] * b[ins, 1] + l3[ins] * c[ins, 1]
        first[i] = y.min() - ymin
hit = first[~np.isnan(first)]
gap_m = (hit - sink) * scale                 # ground at ymin+sink
print(f"{f.split('/')[-1]}: H={H:.4f} rtrunk={rt:.3f} rays={len(O)} hit={len(hit)} "
      f"scale={scale} sink={sink:.4f}")
print("  underside gap m  p10/p50/p90/max: " +
      " / ".join(f"{np.percentile(gap_m, q):.2f}" for q in (10, 50, 90, 100)))
print(f"  footprint >0.15m above ground: {np.mean(gap_m > 0.15) * 100:.0f}%  "
      f"(>0.30m: {np.mean(gap_m > 0.30) * 100:.0f}%)")
print("  underside GLB units p50/p75/p90: " + " / ".join(f"{np.percentile(hit, q):.4f}" for q in (50, 75, 90)))
