#!/usr/bin/env python3
"""CC-C16b loop re-jitter: push each loop-point >= 14 m from every prop while
keeping the 8-pt loop convex-ish and >= 60 m from old loops. Deterministic."""
import math, json, re

src = open('/tmp/wh-worldfeat/prototype/js/CONFIG.js').read()
S = json.load(open('/tmp/wh-worldfeat/scratch/cc-c16/sites.json'))
iC = src.index('  regionC: {'); iD = src.index('  regionD: {')
crows = [(float(m[0]), float(m[1])) for m in re.findall(r"x: ([-\d.]+), z: ([-\d.]+)", src[iC:iD])]
def dist(a, b): return math.hypot(a[0] - b[0], a[1] - b[1])

def clear(pt, extra_r=0):
    return all(dist(pt, p) >= 14 + extra_r for p in crows)

fixed = []
for loop in S['loops']:
    cx = sum(p[0] for p in loop) / 8; cz = sum(p[1] for p in loop) / 8
    new = []
    for k, pt in enumerate(loop):
        if clear(pt):
            new.append(pt); continue
        # push outward/inward along the bearing from the loop centre to the point
        b = math.atan2(pt[0] - cx, pt[1] - cz)
        done = False
        for rmod in (6, -6, 10, -10, 14, -14, 18, -18, 22, -22):
            for tang in (0, 0.35, -0.35, 0.7, -0.7):
                rad = math.hypot(pt[0] - cx, pt[1] - cz) + rmod
                ang = b + tang
                cand = (round(cx + rad * math.sin(ang), 1), round(cz + rad * math.cos(ang), 1))
                if clear(cand):
                    new.append(list(cand)); done = True; break
            if done: break
        if not done:
            # rotate the point's angle around the loop until clear
            base_rad = math.hypot(pt[0] - cx, pt[1] - cz)
            for da in [0.2 * s * (1 if k % 2 else -1) for s in range(1, 13)]:
                cand = (round(cx + base_rad * math.sin(b + da), 1), round(cz + base_rad * math.cos(b + da), 1))
                if clear(cand):
                    new.append(list(cand)); done = True; break
        if not done:
            new.append(pt)   # unresolved - probe re-fails and we widen globally
    fixed.append(new)
S['loops'] = fixed
json.dump(S, open('/tmp/wh-worldfeat/scratch/cc-c16/sites.json', 'w'), indent=1)
print('loops re-jittered')

# quick local recheck (14 m props)
bad = [(pt, min((dist(pt, p) for p in crows), default=999))
       for loop in fixed for pt in loop]
bad = [(p, round(d, 1)) for p, d in bad if d < 14]
print('remaining prop-violating loop pts:', bad if bad else 'NONE')