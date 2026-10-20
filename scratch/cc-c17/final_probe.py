#!/usr/bin/env python3
"""CC-C17v2 final verification: every appended C17 row vs the live CONFIG (C17 rows
excluded from their own obstacle set): nearest non-C17 prop, road, fire, loop, zones."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe_lib as P
W = P.World()
props = W.cfg['props']; i0 = max(i for i, p in enumerate(props) if p['asset'] == 'banditCampfire') + 1
skip = set(range(i0, len(props)))
print('%-17s %8s %8s  %6s %-22s %6s %6s %6s %6s %6s' % ('asset', 'x', 'z', 'prop', 'nearest', 'road', 'fire', 'loop', 'spawn', 'den'))
for p in props[i0:]:
    x, z = p['x'], p['z']; d, w = W.d_props(x, z, skip=skip); zs = W.zones(x, z)
    print('%-17s %8.1f %8.1f  %6.1f %-22s %6.1f %6.1f %6.1f %6.1f %6.1f' % (p['asset'], x, z, d, w[0], W.d_road(x, z)[0], W.d_fire(x, z)[0], W.d_loop(x, z)[0], zs['spawn'], zs['den']))
