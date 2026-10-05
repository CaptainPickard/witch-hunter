#!/usr/bin/env python3
"""Round J2: count sky pixels seen THROUGH the tree base in a roundJ2 render.
Sky = exact world colour; 'holes' = sky components NOT connected to the open
sky (image top/sides), within the bottom band (rows >= y0, default 200 = below
mid-trunk in the 900x600 persp frame). usage: roundJ2_skyholes.py <png>... """
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
for p in sys.argv[1:]:
    a = np.asarray(Image.open(p).convert('RGB')).astype(int)
    sky = np.all(np.abs(a - a[2, 2]) <= 2, axis=2)
    lab, nl = ndimage.label(sky)
    border = set(np.unique(np.concatenate([lab[0], lab[:, 0], lab[:, -1]]))) - {0}
    hole = (lab > 0) & ~np.isin(lab, list(border))
    hole[:200] = False
    l2, n2 = ndimage.label(hole)
    sizes = sorted(ndimage.sum(hole, l2, range(1, n2 + 1)).astype(int), reverse=True) if n2 else []
    print(f"{p.split('/')[-1]}: sky-hole px={int(hole.sum())} comps={n2} largest={sizes[:4]}")
