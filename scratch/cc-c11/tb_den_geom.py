# Testerbot valspec helper (CC-C11): regionD row geometry at base 935db87. Read-only.
import re, math, sys
src = open(sys.argv[1] if len(sys.argv) > 1 else 'prototype/js/CONFIG.js').read().split('\n')
start = next(i for i, l in enumerate(src) if l.startswith('  regionD: {'))
end = next(i for i in range(start, len(src)) if src[i].startswith('  },'))
rows = []
for i in range(start, end):
    l = src[i]
    m = re.search(r"asset: '(\w+)'", l)
    if not m or 'x:' not in l:
        continue
    x = float(re.search(r"\bx: (-?[\d.]+)", l).group(1)); z = float(re.search(r"\bz: (-?[\d.]+)", l).group(1))
    rows.append((i + 1, m.group(1), x, z))
C = (-186.0, -180.0)
ring = [r for r in rows if r[1].startswith('whWall')]
cx = sum(r[2] for r in ring) / len(ring); cz = sum(r[3] for r in ring) / len(ring)
print('regionD lines %d-%d rows %d' % (start + 1, end + 1, len(rows)))
print('ring centroid (%.1f, %.1f) seg r %s' % (cx, cz, [round(math.hypot(r[2] - cx, r[3] - cz), 1) for r in ring]))
for p in [('center', -186, -180), ('lairRow', -185.8, -180.2), ('spawn', -156, -190), ('landD', -185.8, -180.2),
          ('enemyLair c+(0,6)', -186, -174), ('nestComment', -175, -265)]:
    print('%-18s (%.1f,%.1f) dCenter %.1f dRing %.1f' % (p[0], p[1], p[2], math.hypot(p[1] - C[0], p[2] - C[1]), math.hypot(p[1] - cx, p[2] - cz)))
for ln, a, x, z in rows:
    print(':%d %-12s (%.1f,%.1f) dCenter %.1f dRing %.1f' % (ln, a, x, z, math.hypot(x - C[0], z - C[1]), math.hypot(x - cx, z - cz)))
