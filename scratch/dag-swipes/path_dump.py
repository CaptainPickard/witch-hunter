#!/usr/bin/env python3
"""Per-frame R_Hand world path + speed + Hips height for the probe GLB (numpy FK)."""
import sys
import numpy as np
sys.path.insert(0, 'scratch')
from verify_dagger_clips import Rig
R = Rig(sys.argv[1])
for clip in [c for c in R.anims if c.startswith('CAND_')]:
    an = R.anims[clip]
    ts = sorted(set(np.round(np.concatenate([v[0] for v in an.values()]), 5)))
    hp = np.array([R.world('R_Hand', clip, t)[:3, 3] for t in ts])
    hy = [R.world('Hips', clip, t)[1, 3] for t in ts]
    sp = np.r_[0, np.linalg.norm(np.diff(hp, axis=0), axis=1) * 30]
    print(clip)
    for k, t in enumerate(ts):
        print(f'  f{k:2d} x{hp[k,0]:+.3f} y{hp[k,1]:+.3f} z{hp[k,2]:+.3f} v{sp[k]:5.2f} hipsY{hy[k]:+.3f}')
