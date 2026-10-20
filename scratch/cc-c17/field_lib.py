#!/usr/bin/env python3
"""CC-C17v2 placement aid: the ledger2 per-grid-point field (WH_FIELD dump of
ledger2_probe.js at (0,-366) R 280 = the whole disc) + candidate rows -> the new
worst. Scatter re-plans slightly when props move (rows are scatter obstacles), so
every pick is RE-VERIFIED by the real ledger2_probe.js before paste."""
import json, math
import numpy as np
class Field:
    def __init__(self, path):
        a = np.array(json.load(open(path)), dtype=float)
        self.x, self.z, self.t = a[:, 0], a[:, 1], a[:, 2]
    def add(self, rows, T):
        t = self.t.copy()
        for r in rows:
            m = (self.x - r['x']) ** 2 + (self.z - r['z']) ** 2 <= r.get('cullM', 170) ** 2
            t[m] += T[r['asset']]
        return t
    def worst(self, rows, T):
        t = self.add(rows, T); i = int(t.argmax()); return t[i], (self.x[i], self.z[i])
    def exposure(self, x, z, cull):
        m = (self.x - x) ** 2 + (self.z - z) ** 2 <= cull ** 2
        return self.t[m].max() if m.any() else 0
T = {'deadTree': 30174, 'blightcap': 5786, 'skullPile': 4733, 'mossBoulder': 21599}
