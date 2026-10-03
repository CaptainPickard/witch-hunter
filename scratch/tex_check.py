#!/usr/bin/env python3
"""Verify bake law on a -pixelated.glb: texture <=512px and every RGB channel 5-bit (low 3 bits zero)."""
import sys, numpy as np, trimesh
for p in sys.argv[1:]:
    m = trimesh.load(p, force='mesh')
    t = m.visual.material.baseColorTexture
    a = np.asarray(t.convert('RGB'))
    print(p, 'tex', t.size, '5bit', bool(((a & 7) == 0).all()), 'meanRGB', a.reshape(-1, 3).mean(0).round(1))
