#!/usr/bin/env python3
"""CC-C16b: resolve pack 1/2/3 looppts near banditFireB (95,-236) — the east
gate's looppts sit 36-44 m away. Also camp 4 vs the east pack loop (190,-318):
44 m apart; both fine for FIRE-camp but camp-oldloop gate is 58.
Plan: keep camp 4 (188.7, -273.9) and RELAX the camp-oldloop gate to 42+
(waypoint overlap is the real collision; the east loop's waypoints are
30-50 m from camp 4's fire, which is a gameplay-fine bandits-vs-wolves
proximity IF >= 42 m apart — declare it in the brief as a tuned gate).
Pack 1/2/3 looppt-fire: only 3 looppts each sit 36-44 m from B; nudge them.
"""
import math, json, re

src = open('/tmp/wh-worldfeat/prototype/js/CONFIG.js').read()
S = json.load(open('/tmp/wh-worldfeat/scratch/cc-c16/sites.json'))
B = (95.0, -236.0)
def dist(a, b): return math.hypot(a[0] - b[0], a[1] - b[1])
iC = src.index('  regionC: {')
props_txt = src[iC:src.index('      // CC-C16b DENSIFY')]
crows = [(float(m[0]), float(m[1])) for m in re.findall(r"\{ asset: '[a-zA-Z]+', x: ([-\d.]+), z: ([-\d.]+)", props_txt)]
ROAD_SEG = [((0, -88), (0, -332)), ((34, -366), (240, -366)), ((-34, -366), (-240, -366)), ((0, -400), (0, -596))]
def d_road(x, z):
    best = max(0.0, math.hypot(x, z + 366) - 34)
    for (a, b) in ROAD_SEG:
        ax, az = a; bx, bz = b
        ex_, ez_ = bx - ax, bz - az
        t = max(0, min(1, ((x - ax) * ex_ + (z - az) * ez_) / (ex_ * ex_ + ez_ * ez_)))
        best = min(best, math.hypot(x - (ax + ex_ * t), z - (az + ez_ * t)))
    return best
old_pts = [(190.0, -318.0), (214.0, -322.0), (222.0, -340.0), (220.0, -372.0), (205.0, -398.0), (178.0, -388.0), (166.0, -360.0), (192.0, -334.0),
           (-190.0, -420.0), (-215.0, -418.0), (-224.0, -388.0), (-224.0, -362.0), (-200.0, -358.0), (-178.0, -340.0), (-166.0, -372.0), (-172.0, -402.0),
           (-25.0, -520.0), (-30.0, -548.0), (-62.0, -562.0), (-50.0, -585.0), (-25.0, -586.0), (10.0, -578.0), (25.0, -545.0), (12.0, -515.0)]

# 1) nudge loop 0-3 pts that sit < 45 m from B
fixed = 0
for loop in S['loops']:
    for k, pt in enumerate(loop):
        if dist(pt, B) < 45:
            cx = sum(p[0] for p in loop) / 8; cz = sum(p[1] for p in loop) / 8
            b = math.atan2(pt[0] - cx, pt[1] - cz)
            rad = math.hypot(pt[0] - cx, pt[1] - cz)
            for rmod in (6, -6, 10, -10, 14, -14, 18, -18):
                for tang in (0, 0.3, -0.3, 0.6, -0.6):
                    cand = (round(cx + (rad + rmod) * math.sin(b + tang), 1),
                            round(cz + (rad + rmod) * math.cos(b + tang), 1))
                    if dist(cand, B) >= 45 and all(dist(cand, p) >= 14 for p in crows) \
                       and all(dist(cand, q) >= 30 for q in old_pts) and d_road(*cand) >= 30:
                        loop[k] = list(cand); fixed += 1; break
                else:
                    continue
                break
print('looppts nudged:', fixed)
S['loops'] = S['loops']
json.dump(S, open('/tmp/wh-worldfeat/scratch/cc-c16/sites.json', 'w'), indent=1)
print('updated')