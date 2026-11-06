#!/usr/bin/env python3
"""CC-EC1 clearance check: 2 coven spawn rows vs check set (>25m required)."""
import re, math, sys

ROOT = '/tmp/wh-worldfeat'
cfg = open(ROOT + '/prototype/js/CONFIG.js').read()

coven = [(-118.4, -238.2), (-99.2, -249.1)]

checks = []  # (kind, label, x, z)

# 1. CC-C16b camp guards + CC-C6 rows (regionC.enemies, lines 575-634)
m = re.search(r'enemies: \[(.*?)\n    \]', cfg, re.S)
# take the regionC enemies block = the third 'enemies: [' (A, B, C, D order)
blocks = re.findall(r'enemies: \[(.*?)\n    \]', cfg, re.S)
c_enemies = blocks[2]
for ln in c_enemies.splitlines():
    mm = re.match(r"\s*\{ type: '(\w+)', x: (-?[\d.]+), z: (-?[\d.]+)", ln)
    if not mm:
        mm = re.match(r"\s*\{ type: '(\w+)', x: (-?[\d.]+), z: (-?[\d.]+)", ln + ' ')
    if mm:
        t, x, z = mm.group(1), float(mm.group(2)), float(mm.group(3))
        if t in ('bandit', 'wolf', 'ghoul'):
            checks.append((t, f'{t}', x, z))

# 2. banditCampfire props in regionC props
prop_block = cfg.split('regionC')[1] if 'regionC' in cfg else cfg
for ln in cfg.splitlines():
    if 'banditCampfire' in ln:
        mm = re.search(r'x: (-?[\d.]+),\s*z: (-?[\d.]+)', ln)
        if mm:
            checks.append(('campfire', 'banditCampfire', float(mm.group(1)), float(mm.group(2))))

# 3. wolfPacks waypoints (all 8 packs)
wp = re.search(r'wolfPacks: \[(.*?)\n    \]', cfg, re.S).group(1)
pid = None
for ln in wp.splitlines():
    idm = re.search(r"\{ id: '(\w+)'", ln)
    if idm:
        pid = idm.group(1)
    pts = re.findall(r'\[(-?[\d.]+),\s*(-?[\d.]+)\]', ln)
    for x, z in pts:
        checks.append(('wolfWP', f'wolfpack {pid}', float(x), float(z)))

# also wolf spawn rows already caught by enemies scan (type wolf)

# 4. den door interactAt
door = re.findall(r'interactAt: \{ x: (-?[\d.]+), z: (-?[\d.]+) \}', cfg)
doorx, doorz = float(door[0][0]), float(door[0][1])
checks.append(('denDoor', 'den door interactAt', doorx, doorz))

print(f'check-set size: {len(checks)} members')
print(f'den door at ({doorx},{doorz})')
ok = True
report = []
for ci, (cx, cz) in enumerate(coven, 1):
    best = None
    for kind, label, x, z in checks:
        d = math.hypot(cx - x, cz - z)
        if best is None or d < best[0]:
            best = (d, kind, label, x, z)
    report.append((ci, cx, cz, best))
    print(f"coven {ci} @ ({cx},{cz}): min {best[0]:.1f}m -> {best[1]} {best[4-3] if False else best[2]} @({best[3]},{best[4]})")
    if best[0] <= 25:
        ok = False

# per-kind minimums for the table
for ci, (cx, cz) in enumerate(coven, 1):
    by_kind = {}
    for kind, label, x, z in checks:
        d = math.hypot(cx - x, cz - z)
        if kind not in by_kind or d < by_kind[kind][0]:
            by_kind[kind] = (d, x, z, label)
    print(f'--- coven {ci} per-kind mins ---')
    for kind, (d, x, z, label) in sorted(by_kind.items()):
        print(f'  {kind}: {d:.1f}m @({x},{z}) {label}')

# full ranked list for coven 1 (top 8 nearest)
print('--- coven 1 top-8 nearest ---')
all_d = sorted(((math.hypot(cx - x, cz - z), kind, x, z) for kind, label, x, z in checks for cx, cz in coven[:1]), key=lambda t: t[0])
for d, kind, x, z in all_d[:8]:
    print(f'  {d:.1f}m {kind} @({x},{z})')
print('--- coven 2 top-8 nearest ---')
all_d = sorted(((math.hypot(cx - x, cz - z), kind, x, z) for kind, label, x, z in checks for cx, cz in coven[1:]), key=lambda t: t[0])
for d, kind, x, z in all_d[:8]:
    print(f'  {d:.1f}m {kind} @({x},{z})')
print('CLEARANCE:', 'PASS' if ok else 'FAIL')
sys.exit(0 if ok else 1)
