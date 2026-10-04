#!/usr/bin/env python3
"""Round G: decimate the Meshy snare bush to the ring-instance budget.

Same decimator as art-direction/3d/regen_pipeline_v2.py (fast_simplification
quadric simplify, target_count). The raw Meshy GLB is geometry only (POSITION +
indices, no material / UV / texture), so there is no UV to carry across; the
mesh is welded by position first so the simplifier sees one connected surface
per component instead of seam-split islands.

  decimate_roundG.py <in.glb> <out.glb> [target_tris=3000]

Prints (and appends to scratch/treeqa/roundG/decimate.jsonl) the signed
before/after counts. Signed: Claude Code (Round G), 2026-10-05.
"""
import json, sys
from pathlib import Path
import numpy as np
import trimesh
import fast_simplification as fs

src, dst = sys.argv[1], sys.argv[2]
target = int(sys.argv[3]) if len(sys.argv) > 3 else 3000

m = trimesh.load(src, force='mesh')
before = dict(faces=len(m.faces), verts=len(m.vertices))
w = trimesh.Trimesh(np.asarray(m.vertices), np.asarray(m.faces), process=False)
w.merge_vertices()
welded = dict(faces=len(w.faces), verts=len(w.vertices))

# fast_simplification overshoots/undershoots slightly; step the request down
# until the result is within budget.
req = target
for _ in range(8):
    vn, fn = fs.simplify(np.asarray(w.vertices, dtype=np.float32),
                         np.asarray(w.faces, dtype=np.int32), target_count=req)
    if len(fn) <= target:
        break
    req = int(req * target / len(fn)) - 1
out = trimesh.Trimesh(vn, fn, process=False)
out.remove_unreferenced_vertices()
out.export(dst, file_type='glb')
after = dict(faces=len(out.faces), verts=len(out.vertices), requested=req)
b0, b1 = m.bounds, out.bounds
row = dict(signed='Claude Code (Round G) 2026-10-05', src=src, dst=dst, target=target,
           before=before, welded=welded, after=after,
           ext_before=[round(float(v), 3) for v in b0[1] - b0[0]],
           ext_after=[round(float(v), 3) for v in b1[1] - b1[0]])
print(json.dumps(row))
log = Path(__file__).parent / 'treeqa' / 'roundG' / 'decimate.jsonl'
log.parent.mkdir(parents=True, exist_ok=True)
with open(log, 'a') as f:
    f.write(json.dumps(row) + '\n')
