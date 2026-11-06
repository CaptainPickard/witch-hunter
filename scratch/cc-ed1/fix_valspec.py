"""CC-ED1 valspec remediation (IO, degraded-dispatch law): repair transport
corruption in the died-mid-write Testerbot child's valspec. Mechanical fixes
only + two census corrections verified against the live CONFIG this wake
(nodes close 1176 not 1180; whole-file wolf count 28 not 30)."""
import re

p = '/tmp/wh-worldfeat/io/specs/cc-ed1-east-wolfpack-den-valspec.md'
s = open(p).read()
orig = s

fixes = [
    # V-1 command corruption
    ('Run in `/tmp/wh-wh-worldfeat` — CORRECT: `/tmp/wh-worldfeat`:',
     'Run in `/tmp/wh-worldfeat`:'),
    ("grep -c east_h typo-guard: the real command is `grep -c east_hollow_den prototype/builds/v8-playable.html`",
     "grep -c east_hollow_den prototype/builds/v8-playable.html"),
    ('one padded comment row (< 4 contributors, or > 3 hits from a15 single row)',
     'one padded comment row (< 4 contributors, or > 3 hits from a single row)'),
    (' Testerbot keeps a per-hit ledger (`grep -n east_hollow_den prototype/builds/w8-pl... prototype/builds/v8-playable.html`)',
     ' Testerbot keeps a per-hit ledger (`grep -n east_hollow_den prototype/builds/v8-playable.html`)'),
    # V-2 factual + corruption fixes
    ("nodes: [` array (open 1171, close 1180) **after the last WD1 node row (bonePile (−198.5,−441), line 1175)**",
     "nodes: [` array (open 1171, close 1176) **after the last WD1 node row (bonePile (−198.5,−441), line 1175)**"),
    ("Any third surface = **V-2** = **BLOCKING** (B3).", "Any third surface = **BLOCKING** (B3)."),
    ('2b. **Row law:** every new prop row is exactly `{ asset, x, z, rotY, re  // east_hollow_den thicket mouth W... scale }`',
     '2b. **Row law:** every new prop row is exactly `{ asset, x, z, rotY, scale }`'),
    ("exactly 4 new node rows, all `type: 'boneItem'... 'bonePile'`.",
     "exactly 4 new node rows, all `type: 'bonePile'`."),
    ("cite the two art anchors (`concept-05-night-props banner + day-05-ambush` both named;",
     "cite the two art anchors (`concept-05-night-ambush` + `day-05-ambush` both named;"),
    # V-3 corruption
    ('git diff prototype hunk-typo-guard-here', 'git diff prototype/js/gather.js'),
    ('`git diff prototype/js/ggather.js | grep -c "^@"`',
     '`git diff prototype/js/gather.js | grep -c "^@@"`'),
    # V-5 corruption
    ('- **assets.js diff EMPTY this round** — no new GLB rows, no pngs rows, no manifest edits. Any change = **BLOCKING** (B6).\n2. Every new prop `asset:` ∈ { deadTree, mossBoulder, sweep-guard: type: \'bonePile\', skullPile, buriedCoffin, rubblePile }',
     '- **assets.js diff EMPTY this round** — no new GLB rows, no pngs rows, no manifest edits. Any change = **BLOCKING** (B6).\n2. Every new prop `asset:` ∈ { deadTree, mossBoulder, skullPile, buriedCoffin, rubblePile }'),
    # V-6 corruption
    ("grep -c \"id: 'east'\" prototype/js: CONFIG.js # = 2 (779 + 2191)",
     "grep -c \"id: 'east'\" prototype/js/CONFIG.js # = 2 (779 + 2191)"),
    ('sha256 = `2e2afb6097e39a166f29c9c1e0f74cfbdfe77f06e383a658db5b20a8dfd1bd`',
     'sha256 = `2e2afb6097e39a166f58107231e3f74cfbdfe77f06e383a658db5b20a8dfd1bd`'),
    ("[[190,-318],[214,-3220],[222,-340],[220,-372],[205,-398],[178,-388],[166,-360],[192,-334]] — (190,−318), (214,−322), (222,−472)... wait, that's (220,−372)... (see V-0).",
     "[[190,-318],[214,-322],[222,-340],[220,-372],[205,-398],[178,-388],[166,-360],[192,-334]] — i.e. the eight pairs (190,−318) (214,−322) (222,−340) (220,−372) (205,−398) (178,−388) (166,−360) (192,−334) (see V-0)."),
    ("3. `type: 'wolf'` whole-file count still **30** (= 28 regionC rows at 576–615 + 2 elsewhere; N-2)",
     "3. `type: 'wolf'` whole-file count still **28** (V-0 CORRECTION: the child's census pre-print said 30 with 2 elsewhere; the measured whole-file count is 28 — all wolf rows live at 576–615; N-2 carries the correction)"),
    ("6. `'east'` census = **6** rows (576, 579+2 intermediate, 779, 2191)",
     "6. `'east'` census = **6** rows (576–579 the four spawn rows, 779 the boundary guard, 2191 the pack row)"),
    # V-7 corruption
    ('`prototype/builds/v2... prototype/builds/v8-playable.html`',
     '`prototype/builds/v8-playable.html`'),
    ('1b-bis. **UN-REDACTED scratch edits ALLOWED under one law:',
     '1b-bis. **Scratch edits ALLOWED under one law:'),
    # V-8 corruption
    ('`scratch/cc-ed1/c clearance_ed1.py` (IO proven pre-spec;',
     '`scratch/cc-ed1/clearance_ed1.py` (IO proven pre-spec;'),
    ('and re-derives every margin from the LOST... landed rows.',
     'and re-derives every margin from the LANDED rows.'),
    ('|  wolf | G-2: props → every east waypoint (8, CONFIG 2192–2193) | ≥ 25.0 m | 41.76 41.77 |',
     '| 2 | G-2: props → every east waypoint (8, CONFIG 2192–2193) | ≥ 25.0 m | 41.77 |'),
    ('| 10 | G-6c: nodes mutual | ≥ 6.11 6.0 m | 12.73 |',
     '| 10 | G-6c: nodes mutual | ≥ 6.0 m | 12.73 |'),
    ('| 12 | G-7: union → C center (0,−366) | ≤ 262.0 m | 234.61 (site (210,−455) is 235.5 — the deepest row IS the max) |',
     '| 12 | G-7: union → C center (0,−366) | ≤ 262.0 m | 234.61 (deepest row node (208.5,−455) — the site max) |'),
    ("the two 2-row coven census note is a wolf/coven mix-up — Testerbot's census here is the C-census law: the IO spec's own print is the normative reference (G-1 12.03 etc.), Testerbot's re-run must reproduce the IO §5 table within 0.05 m, and the G-1 census question (wolf vs wolf+C-census) does NOT change the limit law.",
     "the two 2-row coven census note is a wolf/coven mix-up — Testerbot's census here is the C-census law: the IO spec's own print is the normative reference (G-1 12.03 etc.), and the G-1 census question (wolf vs wolf+coven rows) does NOT change the limit law. NOTE the child's 'wolf count 30' pre-print was a census error, corrected to 28 (N-2)."),
    # V-9 corruption
    ('node scratch/cc-ed1probe.js         # ← typo guard; real command: node scratch/cc-ed1/preseat_probe.js',
     'node scratch/cc-ed1/preseat_probe.js'),
    ("`WH_GROUND.heightAt('forest_of_the_old_node... 'forest_of_the_old_king', x, z)`",
     "`WH_GROUND.heightAt('forest_of_the_old_king', x, z)`"),
    # V-11 corruption
    ('4. NO git commands by Devbot (NO-GIT): changes unstaged, zero commits, zero pushes (B11). no git commands by devbot (NO-GIT): changes unstaged, zero commits, zero pushes (B11).',
     '4. NO git commands by Devbot (NO-GIT): changes unstaged, zero commits, zero pushes (B11).'),
]
missed = []
count = 0
for old, new in fixes:
    if old not in s:
        missed.append(old[:70])
        continue
    s = s.replace(old, new)
    count += 1

# N-2 correction note (replace the wrong claim wholesale)
m = re.search(r'\*\*N-2 \([^)]*\)\*\*[^\n]*', s)
if m:
    print('N-2 line:', m.group(0)[:200])

if s != orig:
    open(p, 'w').write(s)
    print('WROTE', count, 'of', len(fixes), 'fixes;', len(missed), 'missed')
    for x in missed:
        print('  MISSED:', x)
else:
    print('NO CHANGES')
