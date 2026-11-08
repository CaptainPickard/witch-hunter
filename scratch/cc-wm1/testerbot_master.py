#!/usr/bin/env python3
"""CC-WM1 Testerbot master validation: valspec anchors F, I-1..I-6, A-1..A-4,
B-1..B-3, C-1..C-4, D-1..D-3, E-1..E-4 (E-4 dual variant: valspec-literal vs
landed-truth), independent WM1-A3 distance recomputation, node-road probe,
cross-wiring checks. NO-GIT: reads git diff only, never mutates."""
import re, math, subprocess, json, sys
from collections import Counter

ROOT = '/tmp/wh-worldfeat'
CFG = ROOT + '/prototype/js/CONFIG.js'
src = open(CFG).read()

RES = []  # (anchor, verdict, note)
def rec(aid, ok, note):
    RES.append((aid, 'PASS' if ok else 'FAIL', note))
    print(f"[{'PASS' if ok else 'FAIL'}] {aid}: {note}")
def chk(aid, cond, ok_note, fail_note):
    rec(aid, cond, ok_note if cond else fail_note)

def dist(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

# ---------------- block locators (valspec anchors) ----------------
def block_by_anchor(open_pat, anchor, close_pat='    ],'):
    a = src.index(anchor)
    s = src.rindex(open_pat, 0, a)
    e = src.index(close_pat, s)
    assert a > s and a < e, f'anchor {anchor!r} not inside block'
    return s, e, src[s:e]

def span(text, key):
    """Find `key: {` and brace-match to its close. Returns body-with-braces slice."""
    i = text.index(key)
    j = text.index('{', i)
    depth = 0
    for k in range(j, len(text)):
        if text[k] == '{':
            depth += 1
        elif text[k] == '}':
            depth -= 1
            if depth == 0:
                return j, k + 1, text[j:k+1]
    raise KeyError(key)

def obj_body(txt, key):
    s, e, _ = span(txt, key)
    return txt[s+1:e-1]

PS, PE, props_block = block_by_anchor('    props: [', 'west_hollow_den')
NS, NE, nodes_block = block_by_anchor('    nodes: [', 'east_hollow_den larder cache S')
ES, EE, enemies_block = block_by_anchor('    enemies: [', 'wolf-pack loop point')
NTS, NTE, nt_body = span(src, 'nodeTypes: {')
NTS_LINE = src[:NTS].count('\n') + 1
NTE_LINE = src[:NTE].count('\n') + 1
ITS, ITE, _ = span(src, 'items = {')

# regionC whole-span (for the 237 props ground truth)
rc_s = src.index('  regionC: {')
m = re.search(r'(?m)^  [A-Za-z_]+:', src[rc_s+20:])
rc_e = rc_s + 20 + (m.start() if m else 4000)
rc_span = src[rc_s:rc_e]
print(f'INFO regionC span: lines {rc_s+1}..{rc_e+1}')

# ---------------- git diff (read-only) ----------------
DIFF = subprocess.run(['git', '-C', ROOT, 'diff', '--', 'prototype/js/CONFIG.js'],
                      capture_output=True, text=True).stdout
DIFF_U0 = subprocess.run(['git', '-C', ROOT, 'diff', '-U0', '--', 'prototype/js/CONFIG.js'],
                         capture_output=True, text=True).stdout
STAT = subprocess.run(['git', '-C', ROOT, 'diff', '--stat', '--', 'prototype/js/CONFIG.js'],
                      capture_output=True, text=True).stdout.strip()
STATUS = subprocess.run(['git', '-C', ROOT, 'status', '--porcelain'],
                        capture_output=True, text=True).stdout

# ================= SECTION F =================
js_dirty = [re.search(r'\S+$', l).group(0) for l in STATUS.splitlines() if l.split()[-1].endswith('.js')]
chk('F', js_dirty == ['prototype/js/CONFIG.js'],
    f'only .js dirty: {js_dirty}', f'unexpected .js dirt: {js_dirty}')

# ================= SECTION I (byte-diff law) =================
minus_content = [l for l in DIFF.splitlines() if l.startswith('-') and not l.startswith('--- ')]
chk('I-6a', len(minus_content) == 0,
    f'file-wide zero "-" content lines ({STAT})',
    f'{len(minus_content)} "-" content lines, first: {minus_content[:3]}')
chk('I-6b', '0 deletions' in STAT or 'insertions(+), 0' in STAT or STAT.endswith('insertions(+)'),
    f'diffstat: {STAT}', f'deletions present: {STAT}')

i1 = len(re.findall(r"^-[ \t]+(bonePile|deadwoodPile|herbBundle|graveMoss|mushroomCluster):", DIFF, re.M))
chk('I-1', i1 == 0, 'nodeTypes: 0 removed type rows', f'{i1} removed nodeType rows')

i2m = len(re.findall(r"^-[ \t]+[a-zA-Z]+:.*category: 'ingredient'", DIFF, re.M))
i2p = len(re.findall(r"^\+[ \t]+[a-zA-Z]+:.*category: 'ingredient'", DIFF, re.M))
chk('I-2', i2m == 0 and i2p == 1, f'items: {i2m} removed / {i2p} added ingredient row', f'removed={i2m} added={i2p}')

i3m = len(re.findall(r"^-[ \t]+\{ type: 'bonePile'", DIFF, re.M))
i3b = len(re.findall(r"^\+[ \t]+\{ type: 'bonePile'", DIFF, re.M))
i3v = len(re.findall(r"^\+[ \t]+\{ type: 'ironVein'", DIFF, re.M))
chk('I-3', i3m == 0 and i3b == 0 and i3v == 8,
    f'nodes: bonePile -{i3m}/+{i3b}, ironVein +{i3v}', f'r={i3m} b={i3b} v={i3v}')

i4m = len(re.findall(r"^-[ \t]+\{ asset:", DIFF, re.M))
i4p = len(re.findall(r"^\+[ \t]+\{ asset:", DIFF, re.M))
chk('I-4', i4m == 0 and i4p == 14, f'props: -{i4m}/+{i4p}', f'r={i4m} a={i4p}')

i5m = len(re.findall(r"^-[ \t]+\{ type: '(wolf|bandit|coven)'", DIFF, re.M))
i5b = len(re.findall(r"^\+[ \t]+,?\{ type: 'bandit'", DIFF, re.M))
i5o = len(re.findall(r"^\+[ \t]+,?\{ type: '(wolf|coven)'", DIFF, re.M))
chk('I-5', i5m == 0 and i5b == 3 and i5o == 0,
    f'enemies: -{i5m}, +bandit {i5b}, +wolf/coven {i5o}', f'r={i5m} b={i5b} o={i5o}')

# ================= SECTION A =================
iv_lines = [(n, l) for n, l in enumerate(src.splitlines(), 1) if 'ironVein' in l]
code_iv = [n for n, l in iv_lines if not re.match(r'^\s*//', l)]
iv_lines_all = src.splitlines()
seat_ln = code_iv[:8]; nt_ln = code_iv[-1] if code_iv else -1
blocktxt = f'nodeTypes block lines {NTS_LINE}-{NTE_LINE}'
chk('A-1', len(code_iv) == 9 and nt_ln > NTS_LINE and seat_ln == list(range(1234, 1242)),
    f'ironVein code lines = 9: 8 seat rows at lines {seat_ln} (contiguous in nodes block) + nodeTypes row at line {nt_ln}, {blocktxt}',
    f'code hits {code_iv}')

iv_body = obj_body(src, 'ironVein:')
a2 = {
    'name':     re.search(r"name:\s*'Iron Vein'", iv_body),
    'rarity':   re.search(r"rarity:\s*'common'", iv_body),
    'yield':    re.search(r"yield:\s*\{\s*id:\s*'ironOre',\s*count:\s*3\s*\}", iv_body),
    'respawn':  re.search(r"respawnSec:\s*240\b", iv_body),
    'glow':     re.search(r"glowColor:\s*0x8f5a33\b", iv_body),
    'scale':    re.search(r"scale:\s*1\.15\b", iv_body),
}
extra = [f for f in re.findall(r"([a-zA-Z]+):", iv_body)
         if f not in ('name', 'rarity', 'yield', 'id', 'count', 'respawnSec', 'glowColor', 'scale')]
chk('A-2', all(a2.values()) and not extra,
    f"fields OK, no extras; extra-keys={extra}", f'mismatch: {[k for k,v in a2.items() if not v]} extra={extra}')

a3 = 0x8f5a33
chk('A-3', a3 == 9394739, f'0x8f5a33 = {a3} (documentation anchor)', f'decimal = {a3}')

nt_keys = re.findall(r"(?m)^[ \t]+,?([A-Za-z]+):[ \t]*\{", nt_body)
chk('A-4', len(nt_keys) == 6 and 'ironVein' in nt_keys,
    f'nodeTypes keys = {nt_keys} (count 6, ironVein after bonePile)',
    f'keys={nt_keys}')

# ================= SECTION B =================
io_hits = [(n, l.strip()) for n, l in enumerate(src.splitlines(), 1) if 'ironOre' in l]
chk('B-1', len(io_hits) == 2, f'ironOre hits = {len(io_hits)}: lines {[n for n,_ in io_hits]}', f'hits={io_hits}')

io_body = obj_body(src, 'ironOre:')
b2ok = {
    'id':       re.search(r"id:\s*'ironOre'", io_body),
    'name':     re.search(r"name:\s*'Iron Ore'", io_body),
    'glyph':    re.search(r"glyph:\s*'IO'", io_body),
    'category': re.search(r"category:\s*'ingredient'", io_body),
}
b2bad = [f for f in ('weight', 'stackCap', 'flavor', 'useHint') if re.search(rf"\b{f}:", io_body)]
chk('B-2', all(b2ok.values()) and not b2bad,
    'ironOre: 4 required fields OK, 4 forbidden fields absent',
    f'missing={[k for k,v in b2ok.items() if not v]} forbiddenPresent={b2bad}')

ings = re.findall(r"(?m)^  ([a-zA-Z]+):[ \t]*\{[^}]*category:\s*'ingredient'", src)
chk('B-3', sorted(ings) == sorted(['boneShard','deadwood','forestHerb','graveMoss','wildMushroom','ironOre']),
    f'6 ingredient items incl ironOre: {sorted(ings)}', f'ings={sorted(ings)}')
# order: ironOre after boneShard, before C1 comment
i_bs = src.index('boneShard:      {'); i_io = src.index('ironOre:'); i_c1 = src.index('// C1 cooked food')
chk('B-3b', i_bs < i_io < i_c1, 'ironOre sits after boneShard, before C1 cooked-food block', 'order wrong')

# cross-wiring: every nodeType yield id exists in CONFIG.items
items_keys = set(re.findall(r"(?m)^  ([a-zA-Z]+):", src[ITS:ITE]))
yields = re.findall(r"(?m)^[ \t]+,?([A-Za-z]+):[ \t]*\{[^}]*yield:[ \t]*\{[ \t]*id:[ \t]*'([a-zA-Z]+)'", nt_body)
missing = [(t, y) for t, y in yields if y not in items_keys]
chk('XW', not missing, f'nodeType->item cross-wiring OK: {dict(yields)}', f'broken yields: {missing}')

# ================= SECTION C =================
iron = re.findall(r"\{ type: 'ironVein', x: ([-\d.]+), z: ([-\d.]+) \}", nodes_block)
expected8 = [('53','-577'),('55.5','-573.5'),('61','-572'),('64','-575.5'),
             ('63.5','-582'),('57','-584'),('51.5','-581.5'),('50','-574')]
chk('C-1', sorted(iron) == sorted(expected8), f'8 ironVein rows at exact census coords', f'got {sorted(iron)}')

bone = re.findall(r"\{ type: 'bonePile', x: ([-\d.]+), z: ([-\d.]+) \}", nodes_block)
expected_bone = [('-192.5','-461'),('-184','-450'),('-204','-453.5'),('-198.5','-441'),
                 ('208.5','-455'),('199.5','-446'),('220','-447.5'),('214.5','-435')]
chk('C-2', sorted(bone) == sorted(expected_bone), '8 pre-existing bonePile rows byte-untouched (sacred)', f'drift: {sorted(bone)}')

rows_c = re.findall(r"\{ type: '[a-zA-Z]+', x:", nodes_block)
gap = re.search(r"\]\s*,\s*\[|\[,|,\s*\[\s*\]", nodes_block)
chk('C-3', len(rows_c) == 16 and not gap, f'regionC.nodes = 16 rows (8+8), dense, no holes', f'rows={len(rows_c)} holes={bool(gap)}')

# C-4 valspec-literal: clearance envelope from LANDED extraction
props_rows = re.findall(r"\{ asset: '([a-zA-Z]+)', x: ([\d.\-]+), z: ([\d.\-]+)", props_block)
bones_c4 = [(float(x), float(z)) for x, z in bone]
enem_c4 = re.findall(r"\{ type: '([a-z]+)', x: ([-\d.]+), z: ([-\d.]+)", enemies_block)
SQUAT = {(56.5,-580.5),(61.5,-580),(59,-574.5)}
veins = [(53,-577),(55.5,-573.5),(61,-572),(64,-575.5),(63.5,-582),(57,-584),(51.5,-581.5),(50,-574)]
c4_problems, c4_worst = [], {'prop': (9e9, None), 'bone': (9e9, None), 'enemy': (9e9, None)}
for v in veins:
    for a, x, z in props_rows:
        d = dist(v, (float(x), float(z)))
        if d < c4_worst['prop'][0]: c4_worst['prop'] = (d, (v, a, (x, z)))
        if d <= 1.5: c4_problems.append(f'vein{v}-prop{a}{(x,z)} d={d:.2f}')
    for b in bones_c4:
        d = dist(v, b)
        if d < c4_worst['bone'][0]: c4_worst['bone'] = (d, (v, b))
        if d <= 4.0: c4_problems.append(f'vein{v}-bone{b} d={d:.2f}')
    for t, x, z in enem_c4:
        pt = (float(x), float(z))
        if pt in SQUAT: continue
        d = dist(v, pt)
        if d < c4_worst['enemy'][0]: c4_worst['enemy'] = (d, (v, t, pt))
        if d <= 12.0: c4_problems.append(f'vein{v}-enemy{t}{pt} d={d:.2f}')
chk('C-4', not c4_problems,
    f"all 8 veins clear props>1.5/bones>4/non-squatter-enemies>12; mins: prop={c4_worst['prop'][0]:.2f} bone={c4_worst['bone'][0]:.2f} enemy={c4_worst['enemy'][0]:.2f}",
    f'violations: {c4_problems[:6]}')

# ================= SECTION D =================
rows14 = re.findall(r"\{ asset: '([a-zA-Z]+)', x: ([\d.\-]+), z: ([\d.\-]+), rotY: ([\d.]+), scale: ([\d.]+) \}", props_block)
landed14 = [
    ('mossBoulder','54','-586','4.2','1.90'),('mossBoulder','59','-587','5.3','2.10'),
    ('mossBoulder','64','-585','0.6','1.80'),('mossBoulder','67','-581','1.4','1.60'),
    ('mossBoulder','67.5','-575','2.7','2.00'),('mossBoulder','65','-570','3.5','1.70'),
    ('mossBoulder','60','-567','4.9','1.50'),
    ('rubblePile','57.5','-588','2.1','1.20'),('rubblePile','60.5','-578.5','5.0','1.00'),
    ('rubblePile','51.5','-570','3.3','1.10'),
    ('treeStump','49.5','-578','1.1','1.30'),('treeStump','66.5','-573','5.8','1.20'),
    ('deadTree','47','-585','2.4','1.60'),('deadTree','68','-578','5.9','1.40'),
]
vspec14 = list(landed14); vspec14[7] = ('rubblePile','55','-584.5','2.1','1.20'); vspec14[9] = ('rubblePile','52','-572.5','3.3','1.10')
n_land = sum(rows14.count(e) for e in landed14)
n_vspec = sum(rows14.count(e) for e in vspec14)
chk('D-1', n_land == 14 and n_vspec == 12,
    f'all 14 redseam rows present exactly once @ amended-spec W-4 final seats (valspec D-1 truth table stale on the 2 rubble rows: valspec pairs match only {n_vspec}/14)',
    f'landed-table matches only {n_land}/14')

rp202 = src.index("rubblePile', x: 202, z: -440")
first_red = src.index("mossBoulder', x: 54, z: -586")
last_red = src.index("deadTree', x: 68, z: -578")
arr_close = src.index('\n    ],', rp202)
rp_line = src[:rp202].count('\n') + 1
fc_line = src[:arr_close].count('\n') + 1
seg_start = src.rindex('{ asset: ', rp202, first_red)   # include row 1's own opening brace
red_rows = len(re.findall(r'\{ asset: ', src[seg_start:arr_close]))
rp_anchor = "rubblePile', x: 202, z: -440"
chk('D-2', src.count(rp_anchor) == 1
    and rp202 < first_red < last_red < arr_close and red_rows == 14,
    f"insertion point OK: anchor rubblePile 202/-440 unique (line {rp_line}); all 14 redseam asset rows contiguous after it, before the props-array close at line {fc_line}",
    f"anchor count {src.count(rp_anchor)}, red_rows={red_rows}")

d3m = len(re.findall(r"^[-].*asset:", DIFF, re.M))
d3p = len(re.findall(r"^\+.*asset: '", DIFF, re.M))
chk('D-3', d3m == 0 and d3p == 14, f'props diff: -{d3m} removed / +{d3p} added', f'r={d3m} a={d3p}')

# regionC props census: valspec block vs ground truth span
blk_asset_rows = len(re.findall(r"\{ asset:", props_block))
span_asset_rows = len(re.findall(r"\{ asset:", rc_span))
span_arrays = re.findall(r"(?m)^    ([a-zA-Z]+): \[", rc_span)
print(f"INFO props census: valspec-anchored block rows={blk_asset_rows}, whole-regionC span rows={span_asset_rows}, span arrays={span_arrays}")

# ================= SECTION E =================
e1rows = re.findall(r"\{ type: 'bandit', x: ([-\d.]+), z: ([-\d.]+) \},?\s*// redseam", enemies_block)
eband = re.findall(r"\{ type: 'bandit', x:", enemies_block)
fband = re.findall(r"\{ type: 'bandit', x:", src)
chk('E-1', sorted(e1rows) == sorted([('56.5','-580.5'),('61.5','-580'),('59','-574.5')]) and len(fband) == 32,
    f'3 squatter rows at W-5 coords; file-wide bandits 29->32; regionC bandits {len(eband)}',
    f'rows={sorted(e1rows)} filebandits={len(fband)}')

types = Counter(re.findall(r"type: '([a-z]+)'", enemies_block))
chk('E-2', dict(types) == {'wolf': 28, 'bandit': 25, 'coven': 2} and sum(types.values()) == 55,
    f'regionC.enemies = {dict(types)} (55 total) matches ground truth', f'got {dict(types)}')

e3m = len(re.findall(r"^[-].*type: '(wolf|bandit|coven)'", DIFF, re.M))
e3w = len(re.findall(r"^\+.*type: '(wolf|coven)'", DIFF, re.M))
e3b = len(re.findall(r"^\+.*\{ type: 'bandit'", DIFF, re.M))
chk('E-3', e3m == 0 and e3w == 0 and e3b == 3, f'enemies diff: -{e3m} / +bandit {e3b} / +wolf-coven {e3w}', f'r={e3m} w={e3w} b={e3b}')

# E-4 dual variant
squatters = [(56.5,-580.5),(61.5,-580),(59,-574.5)]
props_vspec = [(54,-586),(59,-587),(64,-585),(67,-581),(67.5,-575),(65,-570),(60,-567),
               (55,-584.5),(60.5,-578.5),(52,-572.5),(49.5,-578),(66.5,-573),(47,-585),(68,-578)]
props_landed = [(54,-586),(59,-587),(64,-585),(67,-581),(67.5,-575),(65,-570),(60,-567),
                (57.5,-588),(60.5,-578.5),(51.5,-570),(49.5,-578),(66.5,-573),(47,-585),(68,-578)]

def e4_run(name, props, veins_):
    p = []
    for s in squatters:
        for v in veins_:
            d = dist(s, v)
            if d <= 2.8: p.append(f'S{squatters.index(s)+1}--vein{d:.2f}')
    for s in squatters:
        for pr in props:
            d = dist(s, pr)
            if d <= 1.8: p.append(f'S{squatters.index(s)+1}--prop{pr} {d:.2f}')
    for i in range(3):
        for j in range(i+1, 3):
            d = dist(squatters[i], squatters[j])
            if d <= 4.3: p.append(f'S{i+1}-S{j+1} {d:.2f}')
    for v in veins_:
        for pr in props:
            d = dist(v, pr)
            if d <= 2.5: p.append(f'vein{v}--prop{pr} {d:.2f}')
    for i in range(len(veins_)):
        for j in range(i+1, len(veins_)):
            d = dist(veins_[i], veins_[j])
            if d <= 4.2: p.append(f'vein{veins_[i]}-vein{veins_[j]} {d:.2f}')
    rec('E-4-'+name, not p, 'interior spacing bars hold' if not p else f'violations: {p}')
    return p

e4_p1 = e4_run('valspec-literal', props_vspec, veins)   # valspec truth table (stale rubble seats)
e4_p2 = e4_run('landed', props_landed, veins)           # actual landed seat set (authoritative)

# ================= independent WM1-A3 distance report =================
print('\n===== WM1-A3 independent clearance numbers (Testerbot-recomputed) =====')
def min_pair(items, pairs, label):
    best = min((dist(a, b), a, b) for a in items for b in pairs)
    print(f'{label}: min={best[0]:.4f}  {best[1]} -- {best[2]}')
    return best

sv = min_pair(squatters, veins, 'squatter--vein (bar >=2.8)')
ss = [(dist(squatters[i], squatters[j]), i, j) for i in range(3) for j in range(i+1, 3)]
print(f'squatter--squatter: {", ".join(f"S{i+1}-S{j+1}={d:.3f}" for d,i,j in sorted(ss))}  (spec 4.3-6.5)')
nn = min((dist(veins[i], veins[j]), veins[i], veins[j]) for i in range(8) for j in range(i+1, 8))
print(f'vein-vein nearest-neighbor: min={nn[0]:.4f} {nn[1]}--{nn[2]} (bar >4.2; spec claims >=4.24)')
vp = min_pair(veins, props_landed, 'vein--prop(landed new 14)')
sp = min_pair(squatters, props_landed, 'squatter--prop(landed new 14) (bar >=1.8)')
ap = min_pair(veins, [(float(x), float(z)) for _, x, z in props_rows], 'vein--prop(ALL landed regionC block)')
rp_s = min_pair([v for v in veins], [(57.5,-588)], 'vein--rubblePile S (57.5,-588) [spec A4 claim 4.03]')
rp_w = min_pair(veins, [(51.5,-570)], 'vein--rubblePile W (51.5,-570) [spec A4 claim 4.27]')
rp_c = min_pair(squatters, [(60.5,-578.5)], 'squatter--rubblePile center (60.5,-578.5) [A4 claim 1.80]')
# spec A4 annotation check: rubble S comment claims min-squatter 1.80
rsq = min_pair(squatters, [(57.5,-588)], 'squatter--rubblePile S (57.5,-588) [A4 comment claims 1.80 for "S" row]')
rw8 = min_pair(veins, [(51.5,-570)], 'vein--rubblePile W already above')
# vein-road: northRoad polyline worst case
pts = [(0,-400),(-3,-420),(-12,-460),(5,-500),(-5,-540),(0,-596)]
def seg_d(p, a, b):
    px, pz = p; ax, az = a; bx, bz = b
    vx, vz = bx-ax, bz-az
    t = max(0, min(1, ((px-ax)*vx + (pz-az)*vz) / (vx*vx + vz*vz)))
    return math.hypot(px-(ax+t*vx), pz-(az+t*vz))
road = min(min(seg_d(v, pts[k], pts[k+1]) for k in range(len(pts)-1)) for v in veins)
print(f'vein--northRoad centerline: min={road:.1f} m (worst-case with swayAmp 6: >= {road-6:.1f} m; site law 54-60 m, halfWidth 2.2)')
sp_enem = min_pair(squatters, [(float(x), float(z)) for t, x, z in enem_c4 if (float(x), float(z)) not in SQUAT],
                   'squatter--non-squatter enemy (informational)')

# props census ground-truth reconciliation
print(f'INFO: regionC span total asset rows = {span_asset_rows} (ground truth 237?), valspec props block rows = {blk_asset_rows} (valspec says 45 post-edit)')
json.dump({'anchors': [(a, v) for a, v, _ in RES]}, open('/tmp/wh-worldfeat/scratch/cc-wm1/testerbot_results.json', 'w'), indent=1)
print('\nsummary:', Counter(v for _, v, _ in RES))
