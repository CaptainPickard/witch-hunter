#!/usr/bin/env python3
"""verdict_spotcheck.py — Testerbot spot-checks recomputed from CONFIG rows
(valspec sec 8 item 4: >= 3 independent recomputations, never copied).
Read-only."""
import math
import re

cfg = open('/tmp/wh-worldfeat/prototype/js/CONFIG.js').read()
h = cfg[cfg.find('\n  regionH: {'):]
H = {
    'spawn': (0.0, -955.0),
    'enemy0': (-10.0, -975.0),
    'enemy1': (11.0, -976.0),
    'flank_pos': (10.0, -968.0),
    'center': (0.0, -1024.0),
    'plane': -948.0,
}
# re-parse the values so nothing is hand-copied
m = re.search(r'spawn: \{ x: (-?[\d.]+), z: (-?[\d.]+) \}', h)
H['spawn'] = (float(m.group(1)), float(m.group(2)))
me = re.search(r'enemies: \[(.*?)\]', h, re.S).group(1)
en = re.findall(r"\{ type: 'bandit', x: (-?[\d.]+), z: (-?[\d.]+) \}", me)
H['enemy0'], H['enemy1'] = [(float(x), float(z)) for (x, z) in en]
m = re.search(r'planeZ: (-?[\d.]+)', h)
H['plane'] = float(m.group(1))
m = re.search(r'center: \{ x: (-?[\d.]+), z: (-?[\d.]+) \}', h)
H['center'] = (float(m.group(1)), float(m.group(2)))
m = re.search(r"okFenceStonewall', x: (-?[\d.]+), z: (-?[\d.]+)", h)
H['flank_pos'] = (float(m.group(1)), float(m.group(2)))

out = []
d_plane = abs(H['spawn'][1] - H['plane'])
out.append(('spot-1 spawn depth past the plane |%.1f + %.1f|' % (H['spawn'][1], H['plane']),
            d_plane, '== 7.0', abs(d_plane - 7.0) < 1e-9,
            'in-band margin %.1f (suspend 4.0)' % (d_plane - 4.0)))
mut = math.hypot(H['enemy0'][0] - H['enemy1'][0], H['enemy0'][1] - H['enemy1'][1])
out.append(('spot-2 enemy mutual sqrt(21^2 + 1)', mut, '~= 21.02 (floor 12.5)',
            abs(mut - 21.02379604162864) < 1e-6 and mut >= 12.5, 'exact %.10f' % mut))
# flanker H2-ring margin: ring r 80 circles at row scale 5.29 (ext 1.899*5.29);
# nearest ring collider center is the nearest ROW center distance - 0 (center law):
# margin law uses the ring row circle centers; the nearest ring ROW to (10,-968)
ring_rows = re.findall(r"\{ asset: 'whWall[AB]', x: (-?[\d.]+), z: (-?[\d.]+), rotY: (-?[\d.]+), scale: 5\.29[^}]*wall: 8 \}", h)
nearest = min(math.hypot(H['flank_pos'][0] - float(x), H['flank_pos'][1] - float(z))
              for (x, z, ry) in ring_rows)
raw_margin = nearest - (1.899 * 5.29 / 2) - 0.45  # half-ext + collider r toward the flanker
out.append(('spot-3 flanker H2-ring raw clearance (nearest row center %.4f)' % nearest,
            nearest, '>= 16.0 m margin law (raw ~23.12: center-nearest minus half-ext minus r)',
            nearest >= 16.0 + (1.899 * 5.29 / 2) + 0.45,
            'raw center dist %.4f; minus half-ext %.4f minus r 0.45 -> %.4f'
            % (nearest, 1.899 * 5.29 / 2, raw_margin)))
# spot-4: sentry walk-clear = 80 - rho
for i, key in enumerate(['enemy0', 'enemy1']):
    rho = math.hypot(H[key][0] - H['center'][0], H[key][1] - H['center'][1])
    out.append(('spot-4%d sentry %d walk-clear = 80 - rho' % (i, i), 80 - rho,
                '>= 4.45 (pre-freeze ~30.0/30.8)', 80 - rho >= 4.45, 'rho %.4f -> margin %.4f' % (rho, 80 - rho)))
ok_all = True
for name, val, expect, ok, detail in out:
    ok_all = ok_all and ok
    print('%-4s %-58s %s  [expected %s | %s]' % ('ok' if ok else 'FAIL', name, val, expect, detail))
print('---')
print('SPOT-CHECKS: %s (%d checks)' % ('PASS' if ok_all else 'FAIL', len(out)))
raise SystemExit(0 if ok_all else 1)
