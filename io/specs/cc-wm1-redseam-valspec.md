# CC-WM1 Testerbot Validation Spec — Redseam (region C)

Round: CC-WM1 (doc 65 Rich Iron Seam site 'Redseam', world-feature round,
IO spec `io/specs/cc-wm1-redseam-spec.md`). This is the independent
validation contract. Devbot builds; Testerbot executes the anchors below
verbatim and reports PASS/FAIL per anchor. No anchor may be weakened or
skipped without IO sign-off.

Branch: `feat/world-visuals` (worktree root `/tmp/wh-worldfeat`).
All commands below assume `cd /tmp/wh-worldfeat` first.

## INDEPENDENT CENSUS (Testerbot-verified, this build, 2026-11-06)

Re-grepped from `prototype/js/CONFIG.js` (3799 lines) — not copied from the
IO spec. Note: **two** earlier `nodes:` arrays (lines 345, 449) and an
earlier `props:` array exist before regionC; every census below that
touches "the nodes block" anchors off `east_hollow_den larder cache S`
(a comment string that lives *inside* the target block at line 1202), and
"the props block" anchors off `west_hollow_den` (in the props block at
1145). This lands all probes in the **region C** `nodes` block at
1192–1206, never in the region A arrays.

- `CONFIG.gather.nodeTypes` (opens line 3559, closes 3570): **5 types**,
  order: herbBundle, deadwoodPile, mushroomCluster, graveMoss, bonePile.
  Last row closes line 3569 with `scale: 1.0 }` (bonePile, no trailing
  comma).
- `CONFIG.items` (opens line 3049, `window.WH_CONFIG.items = {`):
  ingredient block = forestHerb (3111), deadwood (3112), wildMushroom
  (3113), graveMoss (3114), boneShard (3115, **trailing comma present**).
  Next key after 3115 is `graveSoup` (3119, category food). No `ironOre`
  anywhere in the file.
- `CONFIG.regionC.nodes` (opens 1192, closes 1206): **exactly 8 rows, all
  `bonePile`** — 4 west_hollow_den (1193–1196) + 4 east_hollow_den
  (1202–1205). No `ironVein` anywhere in the file.
- `CONFIG.regionC.props` (opens ~810 by context, closes line 1187):
  **31 `{ asset:` rows** (IO-verified census 2026-11-06; the child's 243 figure
  was phantom). Last prop row = line 1186
  `{ asset: 'rubblePile', x: 202, z: -440, rotY: 0.90, scale: 1.00 },`
  (east_hollow_den chewed earth NW, trailing comma present).
- `CONFIG.regionC.enemies` (opens line 575, closes 646): **52 rows** =
  28 wolf + 22 bandit + 2 coven (census `grep -oE "type: '[a-z]+'"` over
  575–646, `sort | uniq -c`). File-wide there are 7 more bandit rows at
  other locations (177–186 region A-ish block, 379) — those are
  untouched-by-this-round but must not be counted in the regionC census.
  Last row = line 645 `{ type: 'coven', x: -99.2, z: -249.1 }`
  (no trailing comma). The nw2 wolf pack sits at lines 614–617.
- `grep -c "CC-WM1\|redseam\|ironVein\|ironOre" prototype/js/CONFIG.js` =
  **0** (round has not landed; clean baseline).
- `prototype/builds/v8-playable.html` exists; baseline
  `grep -c "west_hollow_den\|east_hollow_den"` = **34** (den markers
  already in the built bundle from CC-WD1/ED1; CC-WM1 markers are 0).
- `tools/build_v8.py` exists.
- `prototype/vendor/three.classic.js` and `prototype/js/wh-ground.js`
  both exist for the runtime smoke chain.
- `git status -sb` clean apart from this spec's untracked docs.

## SEVERITY LEGEND

- **BLOCKER** — build is rejected, Devbot must fix and re-stage.
- **MAJOR** — build is rejected unless IO grants a written waiver.
- **MINOR** — reported in the validation report; does not block commit.

Every anchor below is BLOCKER unless stated otherwise.

---

## SECTION A — `CONFIG.gather.nodeTypes.ironVein` exact fields

Spec W-1. Insertion point: in the `nodeTypes` block (3559–3570), after the
`bonePile` row currently ending line 3569, so `ironVein` becomes type #6
and `bonePile` gains a trailing comma (that comma diff is covered by
anchor I-1's byte law: it appears as an added line only if Devbot uses the
comma-first continuation style already used at line 644; if Devbot instead
touches line 3569 in place, anchor I-1 catches it).

### A-1 — ironVein row exists, exact fields, exact order of checks

Command:

    grep -n "ironVein" prototype/js/CONFIG.js

Expected: exactly **3** hits —
1. one row inside `CONFIG.gather.nodeTypes` (between lines 3559 and 3571
   post-edit),
2. one comment or row reference in `CONFIG.regionC.nodes` block header
   comment (the W-3 site comment names ironVein),
3. eight node rows in `regionC.nodes` — see C-1 for those; count code lines
   that mention ironVein, excluding comment-ONLY lines (node rows carry
   trailing `// CC-WM1` comments BY DESIGN — G demands them — so a plain
   `grep -v "//"` would wrongly exclude them; IO repair 2026-11-06):
   the count must be 1 (nodeTypes row) + 8 (node rows) = **9**. Enforce with:

    grep -nE "ironVein" prototype/js/CONFIG.js | grep -vE "^[0-9]+:\s*//" | wc -l

   Expected: **9** (1 nodeTypes row + 8 node seat rows).

### A-2 — nodeTypes.ironVein field-by-field

Command:

    python3 - <<'PY'
    import re
    src = open('prototype/js/CONFIG.js').read()
    m = re.search(r"ironVein:\s*\{(.*?)\},?\s*\n\s*\};", src, re.S)
    # fallback: ironVein not last
    if not m:
        m = re.search(r"ironVein:\s*\{(.*?)\},", src, re.S)
    assert m, "ironVein row missing"
    body = m.group(1)
    checks = {
        "name":     re.search(r"name:\s*'Iron Vein'", body),
        "rarity":   re.search(r"rarity:\s*'common'", body),
        "yield":    re.search(r"yield:\s*\{\s*id:\s*'ironOre',\s*count:\s*3\s*\}", body),
        "respawn":  re.search(r"respawnSec:\s*240\b", body),
        "glow":     re.search(r"glowColor:\s*0x8f5a33\b", body),
        "scale":    re.search(r"scale:\s*1\.15\b", body),
    }
    for k, v in checks.items():
        print(f"{k}: {'OK' if v else 'FAIL'}")
    assert all(checks.values()), "ironVein fields mismatch"
    print("A-2 PASS")
    PY

Expected output: six `OK` lines then `A-2 PASS`, exit 0.

### A-3 — glowColor decimal cross-check

Command:

    python3 -c "print(0x8f5a33)"

Expected: `9394739`. (If the source ever carried the decimal instead of the
hex literal, A-2's `0x8f5a33` regex still catches the hex form; the decimal
cross-check here is a documentation anchor only — informational, MINOR.)

### A-4 — nodeTypes census after edit

Command:

    awk 'NR>=3559 && /^  \};/{print NR; exit} NR>=3559' prototype/js/CONFIG.js \
      | tail -1

    # then count type keys inside the block:
    python3 - <<'PY'
    src = open('prototype/js/CONFIG.js').read()
    start = src.index('nodeTypes: {')
    end = src.index('\n  }\n};', start)
    import re
    keys = re.findall(r"^    ([a-zA-Z]+):\s+\{", src[start:end], re.M)
    print(sorted(keys))
    assert len(keys) == 6, f"expected 6 nodeTypes, got {len(keys)}"
    assert keys[-1] == 'ironVein' or 'ironVein' in keys
    print("A-4 PASS")
    PY

Expected: the 5 pre-existing keys (bonePile, deadwoodPile, graveMoss,
herbBundle, mushroomCluster) plus `ironVein`; sorted list is alphabetical,
so assertion is on count=6 and membership of `ironVein`. Prints `A-4 PASS`.

---

## SECTION B — `CONFIG.items.ironOre` exact fields

Spec W-2. Insertion point: items ingredient block, after `boneShard`
(line 3115), before the `// C1 cooked food` comment at 3116. `boneShard`
already has a trailing comma, so the new row is pure-append.

### B-1 — ironOre row exists with exact fields

Command:

    grep -n "ironOre" prototype/js/CONFIG.js

Expected: **≥ 2** hits — the items row AND the gather nodeTypes yield
reference (`id: 'ironOre'` in the bonePile-adjacent ironVein row from
A-2). No other pre-existing hits (census showed 0).

### B-2 — ironOre field-by-field (name, glyph, category; no weight/stackCap/flavor)

Command:

    python3 - <<'PY'
    import re
    src = open('prototype/js/CONFIG.js').read()
    m = re.search(r"^  ironOre:\s*\{(.*?)\},?\s*$", src, re.M | re.S)
    # tighter: stop at next top-level key in items
    m = re.search(r"ironOre:\s*\{([^}]*)\}", src)
    assert m, "ironOre row missing"
    body = m.group(1)
    ok = {
        "id":       re.search(r"id:\s*'ironOre'", body),
        "name":     re.search(r"name:\s*'Iron Ore'", body),
        "glyph":    re.search(r"glyph:\s*'IO'", body),
        "category": re.search(r"category:\s*'ingredient'", body),
    }
    forbidden = {
        "weight":   re.search(r"\bweight:", body),
        "stackCap": re.search(r"\bstackCap:", body),
        "flavor":   re.search(r"\bflavor:", body),
        "useHint":  re.search(r"\buseHint:", body),
    }
    for k, v in ok.items():
        print(f"required {k}: {'OK' if v else 'FAIL'}")
    for k, v in forbidden.items():
        print(f"forbidden {k}: {'OK' if not v else 'FAIL'}")
    assert all(ok.values()) and not any(forbidden.values())
    print("B-2 PASS")
    PY

Expected: four required `OK`s, four forbidden `OK`s, then `B-2 PASS`,
exit 0.

### B-3 — items ingredient census after edit

Command:

    python3 - <<'PY'
    import re
    src = open('prototype/js/CONFIG.js').read()
    ings = re.findall(r"^  ([a-zA-Z]+):\s*\{[^}]*category:\s*'ingredient'", src, re.M)
    print(sorted(ings))
    assert len(ings) == 6, f"expected 6 ingredient items, got {len(ings)}"
    assert 'ironOre' in ings
    print("B-3 PASS")
    PY

Expected: 6 ingredient entries — the 5 pre-existing (boneShard, deadwood,
forestHerb, graveMoss, wildMushroom) plus `ironOre`. Prints `B-3 PASS`.

---

## SECTION C — regionC.nodes: exactly 8 new ironVein rows + 8 bonePile rows unchanged

Spec W-3 + W-6. `nodes` block opens line 1192, closes line 1206
(pre-edit). After the edit the block must contain exactly **16 rows**
(8 bonePile + 8 ironVein).

### C-1 — the 8 new ironVein rows at the spec's EXACT coordinates

Command:

    python3 - <<'PY'
    import re
    src = open('prototype/js/CONFIG.js').read()
    # self-anchor: the east-den cache comment sits inside regionC.nodes itself
    cmt = src.index('east_hollow_den larder cache S')
    start = src.rindex('    nodes: [', 0, cmt)
    end = src.index('    ],', start)
    block = src[start:end]
    iron = re.findall(r"\{ type: 'ironVein', x: ([-\d.]+), z: ([-\d.]+) \}", block)
    print(f"ironVein rows found: {len(iron)}")
    assert len(iron) == 8, f"expected 8 ironVein rows, got {len(iron)}"
    expected = [
        ('53', '-577'), ('55.5', '-573.5'), ('61', '-572'), ('64', '-575.5'),
        ('63.5', '-582'), ('57', '-584'), ('51.5', '-581.5'), ('50', '-574'),
    ]
    # order-insensitive compare on the (x,z) PAIRS (floats, exact text)
    assert sorted(iron) == sorted(expected), f"coord mismatch:\n got {sorted(iron)}\n want {sorted(expected)}"
    print("C-1 PASS")
    PY

Expected: `ironVein rows found: 8` then `C-1 PASS`, exit 0. Any drift in
any single coordinate is a BLOCKER.

### C-2 — the 8 pre-existing bonePile rows are unchanged

Command:

    python3 - <<'PY'
    import re
    src = open('prototype/js/CONFIG.js').read()
    cmt = src.index('east_hollow_den larder cache S')
    start = src.rindex('    nodes: [', 0, cmt)
    end = src.index('    ],', start)
    block = src[start:end]
    bone = re.findall(r"\{ type: 'bonePile', x: ([-\d.]+), z: ([-\d.]+) \}", block)
    print(f"bonePile rows found: {len(bone)}")
    assert len(bone) == 8, f"expected 8 bonePile rows, got {len(bone)}"
    expected = [
        ('-192.5', '-461'), ('-184', '-450'), ('-204', '-453.5'), ('-198.5', '-441'),
        ('208.5', '-455'), ('199.5', '-446'), ('220', '-447.5'), ('214.5', '-435'),
    ]
    assert sorted(bone) == sorted(expected), f"bonePile drift:\n got {sorted(bone)}\n want {sorted(expected)}"
    print("C-2 PASS")
    PY

Expected: `bonePile rows found: 8` then `C-2 PASS`. This is the byte-sacred
CC-WD1/ED1 invariant.

### C-3 — total nodes census

Command:

    awk '/^    nodes: \[/{s=1; next} s && /^    \],/{print c; exit} s && /\{ type:/{c++}' \
      prototype/js/CONFIG.js

Expected: **5** if run file-wide (the first `nodes:` block in the file is
region A, 31+ rows — do NOT use that one). Use the C-block-scoped census
instead:

    python3 -c "
    import re
    src = open('prototype/js/CONFIG.js').read()
    cmt = src.index('east_hollow_den larder cache S')
    s = src.rindex('    nodes: [', 0, cmt)
    e = src.index('    ],', s)
    rows = re.findall(r\"\{ type: '[a-zA-Z]+', x:\", src[s:e])
    print(len(rows))
    assert len(rows) == 16, f'expected 16 regionC node rows post-edit, got {len(rows)}'
    print('C-3 PASS')
    "

Expected: prints `16` then `C-3 PASS`.

### C-4 — site clearance envelope for the 8 vein seats (spec W-6)

Command:

    python3 - <<'PY'
    import re, math
    src = open('prototype/js/CONFIG.js').read()
    veins = [
        (53, -577), (55.5, -573.5), (61, -572), (64, -575.5),
        (63.5, -582), (57, -584), (51.5, -581.5), (50, -574),
    ]
    props_start = src.index('    props: [')
    # region C props block is the one that CONTAINS the west_hollow_den comment
    cmt = src.index('west_hollow_den', props_start)
    # find the props: [ that precedes cmt
    ps = src.rindex('    props: [', 0, cmt)
    pe = src.index('    ],', ps)
    props_block = src[ps:pe]
    props = re.findall(r"\{ asset: '([a-zA-Z]+)', x: ([\d.\-]+), z: ([\d.\-]+)", props_block)
    cmt = src.index('east_hollow_den larder cache S')
    nodes_start = src.rindex('    nodes: [', 0, cmt)
    nodes_end = src.index('    ],', nodes_start)
    nodes_block = src[nodes_start:nodes_end]
    bones = re.findall(r"\{ type: 'bonePile', x: ([-\d.]+), z: ([-\d.]+) \}", nodes_block)
    enemies_start = src.rindex('    enemies: [', 0, cmt)
    enemies_end = src.index('    ],', enemies_start)
    enemies_block = src[enemies_start:enemies_end]
    enemies = re.findall(r"\{ type: '[a-z]+', x: ([-\d.]+), z: ([-\d.]+)", enemies_block)

    def dist(a, b): return math.hypot(a[0]-b[0], a[1]-b[1])

    for vein in veins:
        for asset, x, z in props:
            d = dist(vein, (float(x), float(z)))
            assert d > 1.5, f"vein {vein} within 1.5m of prop {asset} ({x},{z}) d={d:.2f}"
        for x, z in bones:
            d = dist(vein, (float(x), float(z)))
            assert d > 4.0, f"vein {vein} within 4m of bonePile ({x},{z}) d={d:.2f}"
        for x, z in enemies:
            d = dist(vein, (float(x), float(z)))
            # CONTESTED-site law (IO repair 2026-11-06): the 3 redseam bandit
            # squatters ARE the fight at the veins (W-5, E-4 governs them at
            # 2.8m). The 12m no-enemy bar applies to every OTHER regionC enemy.
            if (x, z) in [(56.5, -580.5), (61.5, -580), (59, -574.5)]:
                continue
            assert d > 12.0, f"vein {vein} within 12m of non-squatter enemy ({x},{z}) d={d:.2f}"
    print("C-4 PASS — all 8 veins clear props>1.5m, nodes>4m, non-squatter enemies>12m")
    PY

Expected: `C-4 PASS — all 8 veins clear props>1.5m, nodes>4m, non-squatter
enemies>12m` (the CONTESTED-site squatter exception per IO repair 2026-11-06).

---

## SECTION D — the 14 redseam prop rows (spec W-4) + no other regionC prop drift

### D-1 — the 14 new prop rows exist with exact asset/x/z/rotY/scale

Command:

    python3 - <<'PY'
    import re
    src = open('prototype/js/CONFIG.js').read()
    # locate regionC props block (contains west_hollow_den comment)
    cmt = src.index('west_hollow_den')
    ps = src.rindex('    props: [', 0, cmt)
    pe = src.index('    ],', ps)
    block = src[ps:pe]

    expected = [
        ('mossBoulder', '54',   '-586',  '4.2', '1.90'),
        ('mossBoulder', '59',   '-587',  '5.3', '2.10'),
        ('mossBoulder', '64',   '-585',  '0.6', '1.80'),
        ('mossBoulder', '67',   '-581',  '1.4', '1.60'),
        ('mossBoulder', '67.5', '-575',  '2.7', '2.00'),
        ('mossBoulder', '65',   '-570',  '3.5', '1.70'),
        ('mossBoulder', '60',   '-567',  '4.9', '1.50'),
        ('rubblePile',  '57.5', '-588',  '2.1', '1.20'),   // WM1-A4 supersedes (55,-584.5); Testerbot verdict D-1 2026-11-06
        ('rubblePile',  '60.5', '-578.5', '5.0', '1.00'),
        ('rubblePile',  '51.5', '-570',  '3.3', '1.10'),   // WM1-A4 supersedes (52,-572.5); Testerbot verdict D-1 2026-11-06
        ('treeStump',   '49.5', '-578',  '1.1', '1.30'),
        ('treeStump',   '66.5', '-573',  '5.8', '1.20'),
        ('deadTree',    '47',   '-585',  '2.4', '1.60'),
        ('deadTree',    '68',   '-578',  '5.9', '1.40'),
    ]
    rows = re.findall(
        r"\{ asset: '([a-zA-Z]+)', x: ([\d.\-]+), z: ([\d.\-]+), rotY: ([\d.]+), scale: ([\d.]+) \}",
        block)
    # Strict: every expected row must appear EXACTLY once
    for e in expected:
        n = rows.count(e)
        assert n == 1, f"expected row {e} appears {n} times (want exactly 1)"
    # Strict: total regionC prop rows went from 31 -> 45 (IO-verified census
    # 2026-11-06 with this exact extraction: 31 pre-edit; 243/257 earlier was
    # the Testerbot child's phantom number, never reproducible)
    print(f"props rows total: {len(rows)}")
    assert len(rows) == 45, f"expected 45 regionC props rows post-edit, got {len(rows)}"
    print("D-1 PASS — all 14 redseam rows present, regionC props census 31->45")
    PY

Expected: `props rows total: 45` then `D-1 PASS — ...`, exit 0.

### D-2 — the last pre-existing redseam-row insertion point

Command:

    grep -n "rubblePile', x: 202, z: -440" prototype/js/CONFIG.js

Expected: **1 hit**, still in the props block (line 1186 pre-edit; may be
higher post-edit if insertion happens above, but I-law forbids that — see
I-4). Then:

    awk 'NR>=1186 && /redseam/{print NR": "$0}' \
      prototype/js/CONFIG.js | head -3

Expected: the first `redseam` mention sits AFTER the `rubblePile', x: 202, z: -440`
line (i.e. Devbot appended below the east-den rubble row, per the spec's
insertion-point W-4).

### D-3 — no other regionC prop touched

Command:

    git diff prototype/js/CONFIG.js | grep -E "^[-].*asset:" | wc -l

Expected: **0** — zero removed prop lines anywhere in the file.

    git diff prototype/js/CONFIG.js | grep -cE "^\+.*asset: '"

Expected: **14** (exactly the W-4 rows). MAJOR if any other prop line
appears as `+` (i.e. a pre-existing row was re-typed elsewhere).

---

## SECTION E — exactly 3 new bandit rows at W-5 coordinates + all pre-existing enemies untouched

`regionC.enemies` opens line 575, closes line 646 pre-edit; last row 645
(`{ type: 'coven', x: -99.2, z: -249.1 }` no trailing comma). Devbot must
use the comma-first continuation style at line 644 already established by
CC-AE1 (see note at 642–644) so the byte-diff law stays intact.

### E-1 — the 3 new bandit rows at exact W-5 coordinates

Command:

    python3 - <<'PY'
    import re
    src = open('prototype/js/CONFIG.js').read()
    # regionC enemies block = the one containing the wolf-pack loop point comment at line ~640
    cmt = src.index('wolf-pack loop point')
    es = src.rindex('    enemies: [', 0, cmt)
    ee = src.index('    ],', es)
    block = src[es:ee]
    expected = [
        ('56.5', '-580.5'),
        ('61.5', '-580'),
        ('59',   '-574.5'),
    ]
    rows = re.findall(r"\{ type: 'bandit', x: ([-\d.]+), z: ([-\d.]+) \},?\s*// redseam", block)
    print(f"CC-WM1 bandit rows: {len(rows)}")
    assert len(rows) == 3, f"expected 3 CC-WM1 bandit rows, got {len(rows)}"
    assert sorted(rows) == sorted(expected), f"W-5 coords mismatch: got {sorted(rows)} want {sorted(expected)}"
    # file-wide bandit census: 29 pre-edit (22 regionC + 7 other blocks) + 3 new = 32 post-edit
    all_bandits = re.findall(r"\{ type: 'bandit', x:", src)
    print(f"file-wide bandit rows: {len(all_bandits)}")
    assert len(all_bandits) == 32, f"expected 32 bandit rows file-wide post-edit, got {len(all_bandits)}"
    print("E-1 PASS")
    PY

Expected: `CC-WM1 bandit rows: 3`, `file-wide bandit rows: 32`, then
`E-1 PASS`, exit 0.

### E-2 — regionC enemies census after edit

Command:

    python3 - <<'PY'
    import re
    src = open('prototype/js/CONFIG.js').read()
    # regionC enemies block anchored on the wolf-pack loop point comment
    cmt = src.index('wolf-pack loop point')
    es = src.rindex('    enemies: [', 0, cmt)
    ee = src.index('    ],', es)
    block = src[es:ee]
    from collections import Counter
    types = Counter(re.findall(r"type: '([a-z]+)'", block))
    print(dict(types))
    assert types['wolf'] == 28
    assert types['bandit'] == 25
    assert types['coven'] == 2
    assert sum(types.values()) == 55
    print("E-2 PASS")
    PY

Expected: `{'wolf': 28, 'bandit': 25, 'coven': 2}` then `E-2 PASS`.

### E-3 — no pre-existing enemy row touched

Command:

    git diff prototype/js/CONFIG.js | grep -E "^[-].*type: '(wolf|bandit|coven)'" | wc -l

Expected: **0** removed enemy rows.

    git diff prototype/js/CONFIG.js | grep -cE "^\+.*type: '(wolf|coven)'"

Expected: **0** added wolf/coven rows (only bandit adds this round).

    git diff prototype/js/CONFIG.js | grep -cE "^\+.*\{ type: 'bandit'"

Expected: **3**.

### E-4 — interior spacing of the 3 squatters vs veins/props (spec W-5, post-WM1-A3 numbers)

Command:

    python3 - <<'PY'
    import math
    squatters = [(56.5, -580.5), (61.5, -580), (59, -574.5)]
    veins  = [
        (53, -577), (55.5, -573.5), (61, -572), (64, -575.5),
        (63.5, -582), (57, -584), (51.5, -581.5), (50, -574),
    ]
    props = [
        (54, -586), (59, -587), (64, -585), (67, -581), (67.5, -575),
        (65, -570), (60, -567),                       # bank boulders
        (57.5, -588), (60.5, -578.5), (51.5, -570),   # talus rubblePiles (WM1-A4 final; Testerbot D-1 2026-11-06)
        (49.5, -578), (66.5, -573),                   # treeStumps
        (47, -585), (68, -578),                       # deadTree leaners
    ]
    # squatters >= 2.8 m from every vein
    for s in squatters:
        for v in veins:
            d = math.hypot(s[0]-v[0], s[1]-v[1])
            assert d > 2.8, f"squatter {s} within 2.8m of vein {v} (d={d:.2f})"
    # squatters >= 1.8 m from every NEW prop
    for s in squatters:
        for p in props:
            d = math.hypot(s[0]-p[0], s[1]-p[1])
            assert d > 1.8, f"squatter {s} within 1.8m of prop {p} (d={d:.2f})"
    # squatters >= 4.3 m apart
    for i in range(len(squatters)):
        for j in range(i+1, len(squatters)):
            d = math.hypot(squatters[i][0]-squatters[j][0], squatters[i][1]-squatters[j][1])
            assert d > 4.3, f"squatters {i},{j} within 4.3m (d={d:.2f})"
    # veins >= 2.5 m from every NEW prop
    for v in veins:
        for p in props:
            d = math.hypot(v[0]-p[0], v[1]-p[1])
            assert d > 2.5, f"vein {v} within 2.5m of prop {p} (d={d:.2f})"
    # veins >= 4.2 m apart
    for i in range(len(veins)):
        for j in range(i+1, len(veins)):
            d = math.hypot(veins[i][0]-veins[j][0], veins[i][1]-veins[j][1])
            assert d > 4.2, f"veins {i},{j} within 4.2m (d={d:.2f})"
    print("E-4 PASS — squatter/vein/prop interior spacing per WM1-A3")
    PY

Expected: `E-4 PASS — squatter/vein/prop interior spacing per WM1-A3`.

---

## SECTION F — git-status law (only `prototype/js/CONFIG.js` modified among `.js`)

Command:

    git status --porcelain | awk '{print $2}' | grep '\.js$'

Expected: the only `.js` line printed is `prototype/js/CONFIG.js`.
Exactly one line total; any other `.js` path is a BLOCKER.
(Markdown/docs/io-scratch untracked files are fine and ignored by the
`\.js$` filter.)

---

## SECTION G — build law (`tools/build_v8.py` + `CC-WM1` marker count)

Command:

    python3 tools/build_v8.py

Expected: exit code **0**. Non-zero is a BLOCKER.

then:

    grep -c "CC-WM1" prototype/builds/v8-playable.html

Expected: **>= 26** (the sanctioned amendment: `// CC-WM1` on every new row
= 8 node-row comments + 3 bandit-row comments + 14 prop-row comments
+ 1 site banner comment; the amended floor). Counts 16–25 = MINOR violation
(traceability gap), <16 = MAJOR.

If the floor is missed but exit is 0, severity MAJOR (the build passed but
the spec's own traceability markers are weak — Devbot must add the
`// CC-WM1` tag to the missing rows; see I-law for what's allowed to
change).

---

## SECTION H — node one-shot runtime smoke

Spec W-7. Runs in the sandbox with Node; no browser required. Validates
that `window.WH_CONFIG` loads through the real require chain and that all 8
vein seats sit on sane terrain.

Command:

    node - <<'JS'
    // Minimal window shim
    globalThis.window = globalThis;
    require('/tmp/wh-worldfeat/prototype/vendor/three.classic.js');
    require('/tmp/wh-worldfeat/prototype/js/CONFIG.js');
    require('/tmp/wh-worldfeat/prototype/js/wh-ground.js');

    const C = window.WH_CONFIG;
    const G = window.WH_GROUND;
    if (!C) { console.error('FAIL: WH_CONFIG missing'); process.exit(1); }
    if (!G || typeof G.heightAt !== 'function') {
      console.error('FAIL: WH_GROUND.heightAt missing'); process.exit(1);
    }

    const veins = [
      [53, -577], [55.5, -573.5], [61, -572], [64, -575.5],
      [63.5, -582], [57, -584], [51.5, -581.5], [50, -574],
    ];
    const RX = 0, RZ = -366;         // region C centre per census/spec
    let bad = 0;
    for (const [x, z] of veins) {
      const y = G.heightAt('forest_of_the_old_king', x, z);
      const d = Math.hypot(x - RX, z - RZ);
      const ok = Number.isFinite(y) && Math.abs(y) <= 26 && d <= 280;
      console.log(`vein (${x}, ${z})  y=${y.toFixed(2)}  d=${d.toFixed(1)}  ${ok ? 'OK' : 'FAIL'}`);
      if (!ok) bad++;
    }
    // Bonus assertions: node type & item wired up
    const nt = C.gather.nodeTypes.ironVein;
    const it = C.items.ironOre;
    console.log('nodeTypes.ironVein:', nt ? 'OK' : 'MISSING');
    console.log('items.ironOre:     ', it ? 'OK' : 'MISSING');
    if (!nt || !it) bad++;

    if (bad) { console.error(`H FAIL: ${bad} checks failed`); process.exit(1); }
    console.log('H PASS — 8 vein seats on-terrain, |y|<=26, d<=280 from (0,-366), ironVein+ironOre wired');
    JS

Expected: eight `OK` vein lines, `nodeTypes.ironVein: OK`,
`items.ironOre: OK`, then
`H PASS — 8 vein seats on-terrain, |y|<=26, d<=280 from (0,-366),
ironVein+ironOre wired`, exit **0**.

Any vein outside the envelope or a missing key is a BLOCKER.

---

## SECTION I — byte-diff law (append-only inside the five blocks)

The five protected blocks:

1. `nodeTypes` (3559–3570 pre-edit)
2. `items` (3049 onward, specifically the ingredient sub-block; new row
   after boneShard 3115)
3. `regionC.nodes` (1192–1206 pre-edit)
4. `regionC.props` (opens ~810, closes 1187 pre-edit)
5. `regionC.enemies` (575–646 pre-edit)

Byte law: inside these blocks the diff may contain ONLY added lines
(`+`); zero removed lines (`-`) of content. Comments above/below the
blocks may also be added, but pre-existing lines must remain byte-equal.

### I-1 — nodeTypes block append-only

Command:

    git diff -U0 prototype/js/CONFIG.js \
      | awk '/^@@/{ if ($0 ~ /-355[0-9]|\+355[0-9]|-356[0-9]|\+356[0-9]/||/-357[0-9]|\+357[0-9]/) show=1; else show=0 } show'

Expected: shows only `+` additions (the ironVein row + optionally a
trailing-comma comma-first continuation on a NEW line if Devbot follows
the line-644 style). No line starting with `-` that isn't `---` header.

Simpler equivalent (preferred):

    git diff prototype/js/CONFIG.js | grep -cE "^-[[:space:]]+(bonePile|deadwoodPile|herbBundle|graveMoss|mushroomCluster):"

Expected: **0**.

### I-2 — items ingredient block append-only

Command:

    git diff prototype/js/CONFIG.js | grep -cE "^-[[:space:]]+[a-zA-Z]+:.*category: 'ingredient'"

Expected: **0** removed ingredient lines.

    git diff prototype/js/CONFIG.js | grep -cE "^\+[[:space:]]+[a-zA-Z]+:.*category: 'ingredient'"

Expected: **1** (only the new `ironOre` row).

### I-3 — regionC.nodes block append-only

Command:

    git diff prototype/js/CONFIG.js | grep -cE "^-[[:space:]]+\{ type: 'bonePile'"

Expected: **0**.

    git diff prototype/js/CONFIG.js | grep -cE "^\+[[:space:]]+\{ type: 'bonePile'"

Expected: **0** (no bonePile re-typed).

    git diff prototype/js/CONFIG.js | grep -cE "^\+[[:space:]]+\{ type: 'ironVein'"

Expected: **8**.

### I-4 — regionC.props block append-only

Command:

    git diff prototype/js/CONFIG.js | grep -cE "^-[[:space:]]+\{ asset:"

Expected: **0**.

    git diff prototype/js/CONFIG.js | grep -cE "^\+[[:space:]]+\{ asset:"

Expected: **14**.

### I-5 — regionC.enemies block append-only

Command:

    git diff prototype/js/CONFIG.js | grep -cE "^-[[:space:]]+\{ type: '(wolf|bandit|coven)'"

Expected: **0**.

    git diff prototype/js/CONFIG.js | grep -cE "^\+[[:space:]]+,?\{ type: 'bandit'"

Expected: **3** (the comma-first form `,{ type: 'bandit', ...` used at
line 644 also matches the leading `,?`).

### I-6 — file-wide append-only summary

Command:

    git diff --stat prototype/js/CONFIG.js

Expected: `1 file changed, N insertions(+), 0 deletions(-)` for some N
(roughly 30–80 depending on comment line count). **Zero deletions overall**
is the hard invariant. Any `(-)` count > 0 = BLOCKER.

---

## REPAIR BANNER (IO, 2026-11-06, sanctioned WD1 mechanical-recovery pattern)

Testerbot child drift: the valspec this child authored carried a PHANTOM
 truths set in C-1/C-4/D-1/D-2/E-1/E-4/H (assets `rockSharpRusset`/`oreCart`/
`rubbleSmall` = 0 manifest keys, coordinates near (0,-350) far from the frozen
Redseam seat, a nonexistent fire row) mixed with correct censuses. IO
repaired the valspec mechanically BEFORE dispatching Devbot: every truth
table now carries the IO spec's amended-final values (WM1-A3), re-verified
against CONFIG.js on this worktree by IO directly. Anchors whose STRUCTURE
was sound and whose censuses matched reality were kept; only truth values
and stale references were replaced. Amendment WM1-A3 (see IO spec W-6)
supersedes: vein 5 = (63.5,-582), rubblePile S = (55,-584.5), rubblePile W =
(52,-572.5), leaner SW = (47,-585), A-3 decimal = 9394739, G floor = 26.
Amendment WM1-A4 (post-valspec, in-force; Testerbot verdict D-1/E-4
2026-11-06) supersedes: rubblePile S = (57.5,-588), rubblePile W = (51.5,-570)
— the D-1 and E-4 truth tables above carry the A4 seats.

## SPEC-CONFLICTS

Two conflicts/imprecisions found while census-verifying the IO spec:

1. **Bandit census is not pinned in the IO spec (W-5).** The spec names
   "exactly 3 new bandit rows" but does not give the regionC or file-wide
   totals. The ground truth from the independent census is: **file-wide
   bandit rows pre-edit = 29** (22 in regionC + 7 outside: 6 at lines
   177–186 + 1 at line 379). Post-edit file-wide = **32**; post-edit
   regionC-only = **25**.
   *Recommended amendment to the IO spec:* pin both numbers explicitly —
   W-5 should read "regionC.enemies goes from 52 to **55 rows** (28 wolf
   unchanged, 22+3=**25 bandit**, 2 coven unchanged); file-wide bandit
   rows go from 29 to **32**". This is now baked into anchors E-1 and
   E-2, so no runtime impact; the note exists so the IO spec text
   matches what the validator enforces.

2. **`CC-WM1` marker count floor (>=16) is spec-loose.** The spec does not
   name where the 16 markers must live. My census-derived expectation is
   8 node-row comments + 3 bandit-row comments + 14 prop-row comments +
   1 site banner comment = **26** if Devbot tags every row, **12** if
   Devbot tags only rows the spec explicitly demanded. Since the spec's
   floor is 16, the validator should accept any count >=16 without
   checking placement, but flag any count <26 in the report as MINOR so
   IO can see which rows Devbot left untagged.
   *Recommended amendment to the IO spec:* name the comment style —
   require `// CC-WM1` (or `// redseam CC-WM1`) on every new row, making
   the floor exact (26) rather than a range.

---

## HOW TO RUN

1. `cd /tmp/wh-worldfeat`. NO-GIT clause: Testerbot never runs git mutations;
   Devbot never commits/stages — IO is the sole git gatekeeper. The byte-diff
   law reads `git diff` (unstaged) directly — no `git add` anywhere.
2. **F** (git-status law) — fastest sanity check; abort if other .js
   files dirty.
3. **I-1 … I-6** (byte-diff law) — abort on any deletion.
4. **A-1 … A-4**, **B-1 … B-3** — field anchors on nodeTypes + items.
5. **C-1, C-2, C-3, C-4** — nodes census + exact coords + site clearance.
6. **D-1, D-2, D-3** — props census + exact rows + insertion point.
7. **E-1, E-2, E-3, E-4** — enemy census + exact coords + clearance.
8. **G** (build law) — run `tools/build_v8.py` then marker count.
9. **H** (runtime smoke) — final integration proof.

Report result per anchor as PASS / FAIL / WAIVED with one line of
evidence each. Block commit until every BLOCKER passes and IO has signed
off any MAJOR waivers.
