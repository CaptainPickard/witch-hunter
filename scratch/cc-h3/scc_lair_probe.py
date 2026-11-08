#!/usr/bin/env python3
"""CC-H4 static probe: the Scar-Reader's lair at the Spire Approach.

Pure-text audit of the WORKTREE CONFIG.js - no THREE, no node, no browser,
no harness, no build_vX. Parse = regex over the source text, evaluated from
the source, never copied from the spec. Colliders follow the cc-h3
solve_geometry.py footprint table (measured GLB X widths; width*scale/2).

Prints labeled blocks (a)-(f). Exit 0 = all structural checks pass;
exit 1 = the first structural violation (nest parse, socket census, seed
collision), printed as a FAIL line. Props inside the slam reach are REPORTED
as violators, not failures (spec sec 5c).
"""
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = (ROOT / 'prototype' / 'js' / 'CONFIG.js').read_text()


def strip_comments(text):
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    return re.sub(r'//[^\n]*', '', text)


def brace_block(text, start):
    """Return the balanced {...} block at `start`, string/comment aware.

    The naive brace count breaks on CONFIG rows whose strings or comments
    contain braces (the boss rows carry quoted copy + brace-heavy comments),
    so quotes and // or slash-star runs are skipped.
    """
    depth = 0
    i = start
    n = len(text)
    while i < n:
        c = text[i]
        if c == '{':
            depth += 1
            i += 1
        elif c == '}':
            depth -= 1
            i += 1
            if depth == 0:
                return text[start:i]
        elif c in '"\'':
            q = c
            i += 1
            while i < n and text[i] != q:
                if text[i] == '\\':
                    i += 1
                i += 1
            i += 1
        elif text.startswith('//', i):
            j = text.find('\n', i)
            i = n if j < 0 else j + 1
        elif text.startswith('/*', i):
            j = text.find('*/', i)
            i = n if j < 0 else j + 2
        else:
            i += 1
    raise ValueError('unbalanced braces from offset %d' % start)


def obj_keys(block):
    return set(re.findall(r'(\w+)\s*:', strip_comments(block))) - JS_RESERVED


def js_num(expr):
    """Evaluate a JS numeric literal expression (hex / decimal / +/-)."""
    return eval(expr, {'__builtins__': {}}, {})


JS_RESERVED = {'if', 'for', 'while', 'switch', 'catch', 'return', 'function'}
FAILURES = []


def check(label, passed, detail=''):
    print('%s: %s%s' % (label, 'PASS' if passed else 'FAIL', (' ' + detail) if detail else ''))
    if not passed:
        FAILURES.append(label)


# ---- parse the live CONFIG text -----------------------------------------
m = re.search(r'scarreader:\s*\{', SRC)
if not m:
    sys.exit('FAIL: CONFIG.enemy.scarreader row not found')
boss = brace_block(SRC, m.end() - 1)

ml = re.search(r'lair:\s*\{', boss)
if not ml:
    sys.exit('FAIL: scarreader.lair missing - would silently default a lair seat')
lair = brace_block(boss, ml.end() - 1)


def lair_key(pat, cast=str):
    lm = re.search(pat + r'\s*:\s*([^,\n}]+)', lair)
    return cast(strip_comments(lm.group(1))) if lm else None


lair_x, lair_y = lair_key(r'\bx\b', js_num), lair_key(r'\by\b', js_num)
LAIR_REGION = (re.search(r"region:\s*'([A-Z])'", lair) or [None, None])[1]
FLAG_PREFIX = (re.search(r"flagPrefix:\s*'(\w+)'", boss) or [None, None])[1]

mj = re.search(r'regionJ:\s*\{', SRC)
if not mj:
    sys.exit('FAIL: regionJ block not found')
REGION_J = brace_block(SRC, mj.end() - 1)
CJ = re.search(r'center:\s*\{\s*x:\s*([^,]+),\s*z:\s*([^}]+)\}', strip_comments(REGION_J))
JX, JZ = js_num(CJ.group(1)), js_num(CJ.group(2))
NEST_X, NEST_Z = JX + lair_x, JZ + lair_y

# ---- (a) nest world position -------------------------------------------
print('(a) nest parse: regionJ center (%g,%g) + lair x %g y %g -> world (%g,%g)'
      % (JX, JZ, lair_x, lair_y, NEST_X, NEST_Z))
check('(a) nest parses to world (0,-709)', (NEST_X, NEST_Z) == (0.0, -709.0),
      'computed (%g,%g)' % (NEST_X, NEST_Z))

# ---- colliders (the cc-h3 footprint table) ------------------------------
WIDTH = {'whWallA': 1.899, 'whWallB': 1.899, 'mourningStatue': 1.862,
         'stoneSteps': 1.94825, 'okRuinColumn': 0.957085, 'blightcap': 1.692074,
         'lanternPost': 0.585384, 'skullPile': 2.0, 'mossBoulder': 1.897361}
WALL_R = 0.45

mp = re.search(r'\n  props:\s*\[', REGION_J)
if not mp:
    sys.exit('FAIL: regionJ props block not found')
PROPS_START = REGION_J.index('[', mp.end() - 1)
props_depth = 0
PROPS_END = None
for i in range(PROPS_START, len(REGION_J)):
    if REGION_J[i] == '[':
        props_depth += 1
    elif REGION_J[i] == ']':
        props_depth -= 1
        if props_depth == 0:
            PROPS_END = i + 1
            break
PROPS_BLOCK = REGION_J[PROPS_START:PROPS_END]

rows, ring_rows = [], []
for raw in re.findall(r'\{[^{}]*\}', strip_comments(PROPS_BLOCK)):
    # value = the quoted or bare group that actually matched (findall returns
    # '' - not None - for non-participating groups, so test truthiness)
    row = {g[0]: (g[1] or g[2] or g[3])
           for g in re.findall(r'(\w+)\s*:\s*(?:"([^"]*)"|\'([^\']*)\'|([^,\n}]+))', raw)}
    a = row.get('asset')
    if not a:
        continue
    r = {'asset': a.split("'")[0] if "'" in a else a,
         'x': js_num(row['x']), 'z': js_num(row['z']),
         'scale': js_num(row.get('scale', '1')), 'row': raw}
    if 'rotY' in row:
        r['rotY'] = js_num(row['rotY'])
    if 'wall' in row:
        r['wall'] = int(row['wall'].strip() or '0')
        ring_rows.append(r)
    else:
        r['radius'] = WIDTH.get(a, 0) * r['scale'] / 2.0
        rows.append(r)

ring_circles = []
for w in ring_rows:
    length = WIDTH[w['asset']] * w['scale']
    ax, az = math.cos(w['rotY']), -math.sin(w['rotY'])
    for k in range(w['wall']):
        t = ((k + 0.5) / w['wall'] - 0.5) * length
        ring_circles.append((w['x'] + ax * t, w['z'] + az * t, WALL_R, w))

# ---- (b) largest clear circle centered AT the nest ----------------------
def edge_dist(px, pz, x, z, r):
    return math.hypot(px - x, pz - z) - r


obstacles = []          # (clear edge distance, label, pos) vs the nest point
for r in rows:
    obstacles.append((edge_dist(NEST_X, NEST_Z, r['x'], r['z'], r['radius']),
                      '%s at (%g,%g)' % (r['asset'], r['x'], r['z']),
                      (r['x'], r['z'])))
for x, z, rr, w in ring_circles:
    obstacles.append((edge_dist(NEST_X, NEST_Z, x, z, rr),
                      'ring %s segment at (%.2f,%.2f)' % (w['asset'], x, z), (x, z)))

print('(b) regionJ prop parse: %d non-ring rows, %d ring rows (%d ring colliders)'
      % (len(rows), len(ring_rows), len(ring_circles)))
clear, bind_label, bind_pos = min(obstacles)
print('(b) clear circle centered AT nest (%g,%g): %.4f m  (binding: %s at (%.2f,%.2f))'
      % (NEST_X, NEST_Z, clear, bind_label, bind_pos[0], bind_pos[1]))
check('(b) clear circle >= 6.0 m', clear >= 6.0, '%.4f m' % clear)

# ---- (c) REPORT only: props inside the slam reach circle r 7.5 ----------
SLAM_R = 7.5
violators = [(d, lab, pos) for d, lab, pos in obstacles if d < SLAM_R]
print('(c) REPORT: props inside slam reach r %.1f (%d, reported not failed):'
      % (SLAM_R, len(violators)))
for d, lab, pos in sorted(violators):
    print('      VIOLATOR %s at (%.2f,%.2f): edge %.2f m inside reach %.1f'
          % (lab, pos[0], pos[1], d, SLAM_R))
if not violators:
    print('      none')

# ---- (d) ghouls vs the nest ---------------------------------------------
me = re.search(r'\n\s*enemies:\s*\[', REGION_J)
if not me:
    sys.exit('FAIL: regionJ enemies block not found')
enemies_block = REGION_J[me.end():REGION_J.index(']', me.end())]
ghouls = [(js_num(dict(re.findall(r'(\w+)\s*:\s*([^,}\n]+)', g))['x']),
           js_num(dict(re.findall(r'(\w+)\s*:\s*([^,}\n]+)', g))['z']))
          for g in re.findall(r'\{[^{}]*\}', strip_comments(enemies_block))]
gd = [math.hypot(gx - NEST_X, gz - NEST_Z) for gx, gz in ghouls]
print('(d) ghouls at %s vs nest (%g,%g): %s'
      % (ghouls, NEST_X, NEST_Z, ', '.join('%.4f m' % d for d in gd)))
check('(d) both ghouls >= 8.0 m from nest', all(d >= 8.0 for d in gd) and len(gd) == 2,
      'distances %.3f / %.3f m' % tuple(gd) if len(gd) == 2 else 'count %d' % len(gd))

# ---- (e) lairSockets census ---------------------------------------------
# enemy.js Enemy.lairSockets: for every CONFIG.enemy row with pattern
# 'boss-slam' + a lair key -> lairNest (region center + lair.x/y; region =
# CONFIG['region'+lair.region]) -> socket when rotLair.light exists and the
# nest's LAIR_STATE is not cleared (no save block = armed). id = rotLair@x,z.
EB = re.search(r'\n  enemy:\s*\{', SRC)
if not EB:
    sys.exit('FAIL: CONFIG.enemy block not found')
ENEMY_BASE = EB.end()          # offsets inside the finditer substring
SLAM_LAIRS = {}
for tm in re.finditer(r'\n    (\w+):\s*\{', SRC[ENEMY_BASE:]):
    name = tm.group(1)
    if name in JS_RESERVED:
        continue
    # tm.end() is an offset within the SUBSTRING - map it onto SRC before
    # brace_block (the boss rows sit far from the enemy block head), and scan
    # forward from THIS row's opening brace only (SRC.index from 0 would leap
    # back into an earlier row when a later row lacks '{' handling).
    row = brace_block(SRC, ENEMY_BASE + tm.end() - 1)
    if re.search(r"pattern:\s*'boss-slam'", row) and re.search(r'\blair:\s*\{', row):
        SLAM_LAIRS[name] = row

sockets = {}
for name, row in SLAM_LAIRS.items():
    lb = brace_block(row, re.search(r'lair:\s*\{', row).end() - 1)
    lx = js_num(strip_comments(re.search(r'\bx\s*:\s*([^,\n}]+)', lb).group(1)))
    ly = js_num(strip_comments(re.search(r'\by\s*:\s*([^,\n}]+)', lb).group(1)))
    reg = re.search(r"region:\s*'([A-Z])'", lb).group(1)
    rb = brace_block(SRC, re.search(r'region%s:\s*\{' % reg, SRC).end() - 1)
    crb = re.search(r'center:\s*\{\s*x:\s*([^,]+),\s*z:\s*([^}]+)\}', strip_comments(rb))
    rx, rz = js_num(crb.group(1)), js_num(crb.group(2))
    has_light = bool(re.search(r'light:\s*\{[^}]*\}', strip_comments(rb)) and
                     re.search(r'\brotLair:\s*\{', rb))
    sid = 'rotLair@%g,%g' % (rx + lx, rz + ly)
    sockets.setdefault(reg, []).append((name, sid, has_light))
print('socket rows: %s' % ', '.join('%s(lair region %s)' % (name, reg)
      for reg, lst in sockets.items() for name, _, _ in lst))

print('(e) lairSockets census (per boss-slam row, no save block = armed):')
ALL_SOCKETS = {}
for reg in sorted(sockets):
    for name, sid, has_light in sockets[reg]:
        ALL_SOCKETS.setdefault(reg, []).append((name, sid))
        print('      %s -> boss %s socket id %s (rotLair.light present: %s)'
              % (reg, name, sid, has_light))
CHECKED = {'J': 1, 'D': 1}
for reg, lst in sorted(ALL_SOCKETS.items()):
    if reg not in CHECKED:
        print('      NOTE region %s carries %d socket(s) (not gated; no lairs key in baseline)'
              % (reg, len(lst)))

CENSUS = {reg: len(v) for reg, v in ALL_SOCKETS.items()}
check('(e) exactly one scarreader socket in regionJ', CENSUS.get('J', 0) == 1,
      'regionJ count %d' % CENSUS.get('J', 0))
jd = [s for _, s in ALL_SOCKETS.get('J', [])]
check('(e) regionJ socket id rotLair@0,-709', jd == ['rotLair@0,-709'], 'got %s' % jd)
dd = [s for _, s in ALL_SOCKETS.get('D', [])]
check('(e) exactly one rotmother socket in regionD', CENSUS.get('D', 0) == 1,
      'regionD count %d' % CENSUS.get('D', 0))
dupes = [s for s, c in
         (lambda flat: [(s, [x for _, x in flat].count(s)) for s in set([x for _, x in flat])])
         ([s for v in ALL_SOCKETS.values() for s in v]) if c > 1]
check('(e) zero duplicate rotLair@ ids', not dupes, 'duplicates %s' % dupes if dupes else '')

# region-manager gate (AMB-1): which regions carry lairs rows (the concat
# at region-manager ~1909 instantiates lair enemies only there)
lair_regions = []
for rm in re.finditer(r'\n  region([A-Z])\s*:\s*\{', SRC):
    letter = rm.group(1)
    if re.search(r'\n\s*lairs:\s*\[', brace_block(SRC, rm.end() - 1)):
        lair_regions.append(letter)
gate = {l: CENSUS.get(l, 0) for l in lair_regions}
check('(e) AMB-1 gate: no socket count changed outside regionJ(+D baseline 1)',
      gate == {'D': 1, 'J': 1}, 'lair-row regions census %s' % gate)
check('(e) every socket backed by rotLair.light',
      all(h for _, _, h in [t for v in sockets.values() for t in v]))

# ---- (f) textureSeed uniqueness ------------------------------------------
seeds = re.findall(r'textureSeed:\s*([^,\n}]+)', strip_comments(SRC))
c20261107 = sum(1 for s in seeds if js_num(s.strip()) == 20261107)
allseed = [js_num(s.strip()) for s in seeds]
families = {}
for s in allseed:
    families[s] = families.get(s, 0) + 1
print('(f) textureSeed 20261107 occurs %dx in CONFIG.js; seed families (count per value): %s'
      % (c20261107, dict(sorted(families.items()))))
check('(f) textureSeed 20261107 unique (exactly 1 occurrence)', c20261107 == 1)

print('--- failures: %d ---' % len(FAILURES))
if FAILURES:
    for f in FAILURES:
        print('FAIL: ' + f)
    sys.exit(1)
print('SUCCESS: all structural checks pass')
sys.exit(0)
