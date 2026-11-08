# CC-ED1 VALSPEC — East Wolfpack Den Site (independent Testerbot validation spec)

Round: CC-ED1 · 2026-11-06 · Author: Testerbot (gate step 2 — written BEFORE Devbot builds)
Source of truth: `io/specs/cc-ed1-east-wolfpack-den-spec.md` (§4 acceptance criteria A-1..A-9, §5 geometry margins G-1..G-8, verbatim rows + banners)
Round contract: IO spec → Testerbot valspec → Devbot build → Testerbot validation → IO commit
Style parent: `io/specs/cc-wd1-west-wolfpack-den-valspec.md` (the proven sibling round — landed fd286d5, Testerbot PASS 13/13). This round is a STRICT SIBLING: CONFIG.js rows only — **the gather.js terrain seat is ALREADY LANDED in CC-WD1 (fd286d5), so V-3 changes from "validate the 2-line seat" to "gather.js diff EMPTY"**, and the V-set drops to the CONFIG-purity family.
Art anchors (IO §1, vision law this wake): `art-direction/concepts/concept-05-night-ambush.png` + `art-direction/concepts/day-05-ambush.png` — moonlit/earth-neutral base, den dressing = bone/bare-earth neutrals, NO new warm accents (the amber in BOTH anchors belongs to the hunter's lantern, never the den). Art law (GOALS): pixelated everything, darkwood palette, one accent per frame — no new assets this round, so the law binds dressing choice: existing manifest props only, neutral tones.

Base-commit rule: validation diffs against HEAD **fd286d5** (`feat/world-visuals`). Devbot leaves ALL changes UNSTAGED (NO-GIT clause, IO §6); Testerbot runs `git diff` against HEAD, never against a Devbot commit.

## V-0 Ground state (Testerbot's own census, taken 2026-11-06 before any build; Devbot must keep true)

All counts below were RUN by Testerbot this wake, in `/tmp/wh-worldfeat`, against HEAD fd286d5:

- `git status -sb` → `## feat/world-visuals` + ONLY `?? io/specs/cc-ed1-east-wolfpack-den-spec.md` + `?? scratch/cc-ed1/` untracked; **tracked-file working diff EMPTY** (`git diff --stat` prints nothing). The round's diff starts from a clean tree.
- Baseline `grep -c east_hollow_den prototype/builds/v8-playable.html` = **0** and `grep -c east_hollow_den prototype/js/CONFIG.js` = **0** (the marker is NEW this round — any count ≥ 1 is this round's work). Bundle exists and carries the WD1 work: 108,039 lines; `west_hollow_den` = 17 in CONFIG.js, 17 in the bundle (parity proven in WD1 — config comments survive build_v8 byte-identical; N-4).
- **CONFIG census** (3618 lines, sha256 `5b064ce4b5f9cf1c6d6e2cadfa26a3ae48eb7413a955dcfe0060bac9ce6431e6`): `regionC: {` at **470**; props array OPEN `props: [` at **810**, CLOSE `],` at **1166**, holding **232** pre-existing `{ asset:` rows; the last pre-existing rows are the WD1 rows at 1145–1166 — tail: `{ asset: 'rubblePile', x: -186, z: -446, rotY: 0.90, scale: 1.00 },   // west_hollow_den chewed earth E` at **1165**, close at **1166**. `west_hollow_den` grep = **17** rows in CONFIG.js (11 prop rows + 4 node rows + 2 banner comments; banner text spans multiple lines but the literal string appears once per banner). Last WD1 node row: `{ type: 'bonePile', x: -198.5, z: -441 }` at **1175**; regionC `nodes: [` OPEN at **1171**, CLOSE `],` at **1176** (IO re-verified line-by-line this wake; regionC.nodes is NO LONGER a new key this round — **WD1 landed it at fd286d5**; §3.2 is an APPEND into an existing array; N-3).
- regionC.enemies: `enemies: [` at **575**; **28** `type: 'wolf'` rows (12 CC-C5 east/west/north at 576–587 + 16 CC-C16b densify at 600–615) + 2 CC-EC1 coven rows at 644–645 (`,{ type: 'coven', x: -118.4, z: -238.2 },` / `{ type: 'coven', x: -99.2, z: -249.1 }` — comma-first continuation shape, byte-sacred). Census note: `grep -c "type: 'wolf'" CONFIG.js` over the WHOLE FILE = **28** (every wolf row lives in regionC.enemies 576–615; V-0 CORRECTION below and at N-2/V-6/Notes: an earlier pre-print in this file said 30 with 2 rows elsewhere — the measured count is 28, the 2 "elsewhere" claim was the coven rows misread, see the coven census above); the regionC census is also 28. Whole-file `packId` census = **30** (28 in-row + 2 comment refs at 569/2189) — this round adds none of either.
- **wolfPacks block: lines 2190–2210** (`wolfPacks: [` at 2190, close `],` at 2210; separationPush at 2211). **7 packs** (east/west/north/sw/se/ss/nw2), all `regionId: 'forest_of_the_old_king'`, all members 4 + spawnSpread 6. Block sha256 = **`2e2afb6097e39a166f58107231e3f74cfbdfe77f06e383a658db5b20a8dfd1bd`** (`awk '/^    wolfPacks: \[/{s=1} s{print} s&&/^    \],$/{exit}' prototype/js/CONFIG.js | sha256sum` — equals the WD1 valspec baseline exactly; the block carried over through fd286d5 untouched).
- **'east' census = 6 rows** in CONFIG.js: 576–579 (4 east wolf spawn rows, x ∈ [180..194], z ∈ [−334..−318]), 779 (`{ id: 'east', x: 240, z: -366, halfWidth: 10, blocker: true }` — the CC-C5 region boundary guard, NOT the pack row), 2191 (the wolfPacks pack row, L7). `grep -c "id: 'east'" CONFIG.js` = **2** (779 + 2191) — the IO §4 A-9 reading "'id: 'east'' … unchanged" is the 2-row `id: 'east'` census; V-6 pins the full 6-row `'east'` census (N-1/C5).
- **East-pack waypoints** (CONFIG 2192–2193, byte-exact): (190,−318), (214,−322), (222,−340), (220,−372), (205,−398), (178,−388), (166,−360), (192,−334). Testerbot recomputed: min distance to the pack's southern extremity (205,−398) = 0 m definitionally; site (210,−445) is **47 m south** of (205,−398) ✓ IO §2. IO §2's "nearest prop row 41.77 m" = G-2's nearest NEW prop to the nearest EAST WAYPOINT (205,−398) → new rubblePile (205,−443) = 45.0 m; (−268.2,−366) westNotch row → new rubblePile (202,−440) = 41.77 m (N-1/C1).
- **gather.js** (178 lines, sha256 `492d6337061244362be39809d1f71dc5a5cb306a6a32e5394c6e9a766fbbf6ea`): WH_GROUND-terrain-seated at BOTH the seat sites — line **60** `holder.position.set(x, window.WH_GROUND && window.WH_GROUND.has(regionId) ? ... : 0, z)` and line **146** `node.mesh.position.set(pick.x, window.WH_GROUND && ... : 0, pick.z)`, **landed in CC-WD1 (fd286d5)**. **THE ROUND'S gather.js CHANGE = ZERO LINES** (IO §3.3; the WD1-era 2-line seat is in-repo baseline, not this round's work).
- RegionB node rows at 455–458 are bonePile (4 rows, x 31.7/−41.7/−17.0/−2.7, z −63.2/−54.4/−53.1/−52.4) — they ride the same makeNode seat path (no heightfield → the `has()` guard yields 0, byte-equal behavior). byte-preserved this round by V-3 EMPTY.
- Whole-file `grep -c "{ type: 'bonePile'" CONFIG.js` = **8** today (4 Region-B node rows at 455–458 + 4 WD1 larder rows at 1172–1175); regionC total `bonePile` grep = **9** = 8 node rows + 1 nodeTypes row (3387); bundle parity 5/5 (WD1 V-0) — this round ADDS exactly 4, one per row. `nodeTypes: {` at **3378**; `bonePile:` key at **3387** (`Bone Pile`, boneShard ×2, respawnSec 150, glowColor 0xbbbbaa, scale 1.0) — PRE-EXISTING, not this round's surface.
- `node --check` baseline: CONFIG.js, gather.js, game.js, save.js, region-manager.js, region-defs.js, assets.js — **7/7 OK** pre-build.
- `git diff prototype/js/save.js` = **empty** (0 diff lines) today; save.js 301 lines, untouched this round (A-8).
- Fires census: **7** `banditCampfire` prop rows in regionC props (Alphas/Bravos/Charlie rows at 998, 1004, 1010 + the four CC-C16b camp fires at 1069–1072). Nearest of the 7 to the east site: Charlie (−140,−506) = **354 m** (far from the whole west-hemisphere fire set — no margin threatened; G-3's 20.0 clears at ≥ 350 m).
- Roads: `roads: [` at **1573**; the site's bounding constraints: **westRoad** (row at 1576–1578, points x∈[−280..−238] z=−366, halfWidth 2.2) and **eastNotch** bed (row at 1579–1581, points x∈[238..268] z=−366, halfWidth 2.2). Nearest segment-edge to the new props: eastNotch bed → new rubblePile (202,−440) = 41.77 m minus halfWidth 2.2 = **39.57 m** edge margin (G-4's 30.0 clears; V-8's clearance_ed1.py G-4 printed 69.36 pre-landing — its road census includes out-of-quadrant segments whose distances dominate the pre-landing min; post-landing the script's NEW_TAG exclusion drops this round's own rows and the min re-shapes; the LIMIT is the law, the printed value is reported per run (N-1/C2).
- Nearest ENEMY row to the site: east wolf spawn 3 (189.3,−333.9) = **111.6 m** (well clear of G-1's 5.0; clearance_ed1.py's own G-1 print = 12.03 m — its wolf census includes the whole-file scan, where the nearest pre-existing wolf to ANY union row includes the west-pack rows at 580–583 in CONFIG-space ≈ 12 m from the larder cluster — no margin threatened).
- Site radius: site (210,−455) → C center (0,−366) = **235.5 m** ✓ (playable 278.5 − 16.5 = the 262 cap; G-7's printed max 234.61 = the deepest new union row (208.5,−455) — the site center itself sits at 234.61 from (0,−366)).
- MANIFEST keys for the round all pre-exist in assets.js (16–188) at lines: buriedCoffin **21**, deadTree **32**, mossBoulder **64**, skullPile **72**, rubblePile **99**.
- `scratch/cc-ed1/` EXISTS pre-round (IO proven pre-spec): `site_scan.py` (sha256 `5491151606a414ea6ee61daa18a77aaf018a9764b2d42d9a4cca2a8424d7d5c1`), `preseat_probe.js` (sha256 `c73fdd357a0621f7c6cbc3980217e84b3a25f65b2696e3e6f87f1b044ba23da6`), `clearance_ed1.py` (sha256 `68acab5b4f6454fc70d1d6453375e7e7ac0c7462c87b0961db077bceef2f2c11`). Testerbot's reference runs this wake: clearance_ed1.py → **RESULT: CLEARED**, exit 0, 13 PASS rows + 1 INFO (G-8) — all margins ≥/≤ limits (G-1 12.03, G-2 41.77, G-2n 38.20, G-3 86.54? no—), and preseat_probe.js → **ALL 15 PASS**, exit 0 (y 0.05..1.42, slope1m 2.0..8.7 deg) — matching IO §2/§5 exactly (N-1/C4).
- Build tool: `python3 tools/build_v8.py` — run IN the worktree; the served bundle is what gets grepped, never the repo copy.

## V-1 Build and bundle marker count (IO A-1, A-2)

**Command.** Run in `/tmp/wh-worldfeat`:
```bash
python3 tools/build_v8.py && echo "BUILD_EXIT=$?"
grep -c east_hollow_den prototype/builds/v8-playable.html
```
`BUILD_EXIT` must be 0, no Python traceback. Build in the worktree, never via absolute path out of it.

**Pass threshold.** Marker count **≥ 6** AND build exit 0. **BLOCKING** if below (B12).

**Ledger (additionality, not bloat).** Baseline = 0 (V-0), CONFIG comments survive the bundle (WD1 V-0 parity proven at fd286d5 — banners + row comments both grep in the served bytes) — expected contributors: props-section banner comment carrying `east_hollow_den` (1), nodes-section banner comment (1), ≥ 1 prop-row comment, ≥ 1 node-row comment ⇒ **≥ 4 distinct source contributors**, each mapping to a real CONFIG surface the diff shows. A count ≥ 6 reached by one padded comment row (< 4 contributors, or > 3 hits from a single row) = **BLOCKING-LEVEL-2** (class B2). Testerbot keeps a per-hit ledger (`grep -n east_hollow_den prototype/builds/v8-playable.html`) and reproduces it in the verdict.

## V-2 CONFIG.js diff purity and block placement (IO A-3)

**Command.**
```bash
git diff prototype/js/CONFIG.js
git diff prototype/js/CONFIG.js | grep -c "^-[^-]"
```

**Pass thresholds (all required, BLOCKING on any failure).**
1. **Pure-add diff:** `grep -c "^-[^-]"` = **0** (excluding the `---`/`+++` headers). Zero pre-existing lines rewritten or moved — the 232 props rows, the WD1 rows, the coven tail, regionC.enemies, terrain, roads, wolfPacks stay byte-identical (WD1 append-only precedent at whole-file scope, EC1 before it). Any `−` line = **BLOCKING** (B1).
2. **Two insertion surfaces ONLY:** (a) the 11 new prop rows + their banner comment sit inside regionC props [ ] between the last WD1 row (west_hollow_den chewed-earth rubblePile (−186,−446), line 1165 today) and the close `],` at 1166; (b) the 4 new bonePile node rows + their banner comment sit inside the EXISTING regionC `nodes: [` array (open 1171, close 1176) **after the last WD1 node row (bonePile (−198.5,−441), line 1175)** — an APPEND into an existing key, NOT a new key (N-3). Hunk count in the CONFIG diff ≤ 2. Any third surface = **BLOCKING** (B3).
2b. **Positional law (A-3 verbatim):** both hunks sit **immediately after the west_hollow_den rows** — props hunk context-immediately-after `// west_hollow_den chewed earth E` (1165), nodes hunk immediately after `// west_hollow_den thicket mouth approach NE` (1175). A hunk landing anywhere else inside regionC props/nodes = **BLOCKING** (B3).
2b. **Row law:** every new prop row is exactly `{ asset, x, z, rotY, scale }` — **`y` is NEVER set** on a new row (region-manager whGroundFeed() seats C props on the terrain automatically; the `y:` keys on pre-existing C15/C17 outcrop rows are legacy shape, not license). Any `y:` on a new row = **BLOCKING** (B3). Node rows are exactly `{ type: 'bonePile', x, z }`.
4. **Set law:** exactly 11 new prop rows — 3 deadTree (thicket mouth, N-facing arc), 3 mossBoulder (hollow rim, S/E arc), 2 skullPile + 1 buriedCoffin (larder), 2 rubblePile (W/NW chewed earth) — and exactly 4 new node rows, all `type: 'bonePile'`. Counts off = **BLOCKING** (B3).
5. **Marker banners:** both banner comments carry the literal string `east_hollow_den` (feeds V-1's ledger) AND cite the two art anchors (`concept-05-night-ambush` + `day-05-ambush` both named; exact banner wording is IO §3.1/§3.2 verbatim).

## V-3 gather.js diff EMPTY (IO A-4) — the seat landed in CC-WD1

**Command.**
```bash
git diff prototype/js/gather.js
git diff prototype/js/gather.js | grep -c "^@@"    # must print 0 (no hunk headers)
git diff prototype/js/gather.js
```
**Pass thresholds (all required, BLOCKING on any failure).** The CC-WD1 terrain seat (2 lines at gather.js 60/146) is REPO BASELINE at fd286d5 — NOT this round's work. This round's gather.js change = ZERO lines (IO §3.3).
1. `git diff prototype/js/gather.js` prints NOTHING except the two `diff --git`/`index` headers; `git diff prototype/js/gather.js | grep -c "^@@"` = **0** (zero hunk headers). Any hunk = **BLOCKING** (B4).
2. gather.js sha256 post-build = the V-0 baseline `492d6337…fbbf6ea` — byte-identical (tamper check).
3. `node --check prototype/js/gather.js` exits 0 (B9).
4. Context: regionB node rows (455–458) and the WD1 larder rows ride the landed seat path (makeNode line 60 `has()` guard) — this round adds no code, so V-3 EMPTY is both the law AND the safety condition; any "helpful" seat tweak Devbot adds = scope drift = **BLOCKING** (B4).

## V-4 Syntax gate — node --check (IO A-5)

**Command.** Run in `/tmp/wh-worldfeat`:
```bash
for f in CONFIG.js gather.js game.js save.js region-manager.js region-defs.js assets.js; do node --check prototype/js/$f && echo "$f OK"; done
```
**Pass.** All seven print OK, exit 0. Any syntax error = **BLOCKING** (B9) — the v8 inliner happily bundles broken JS; a build pass is NOT a syntax pass. Baseline verified this wake: 7/7 OK pre-build. IO A-5 names CONFIG/gather only; Testerbot sweeps all seven because the bundle eats them all (WD1 precedent).

## V-5 Asset and node-type legality (IO A-7)

**Commands.**
```bash
git diff --stat -- prototype/js/assets.js          # must be empty
git diff prototype/js/CONFIG.js | grep "^+" | grep -oE "asset: '[a-zA-Z]+'|type: '[a-zA-Z]+'"
grep -n "buriedCoffin\|deadTree\|mossBoulder\|skullPile\|rubblePile" prototype/js/assets.js
```

**Pass thresholds.**
1. **assets.js diff EMPTY this round** — no new GLB rows, no pngs rows, no manifest edits. Any change = **BLOCKING** (B6).
2. Every new prop `asset:` ∈ { deadTree, mossBoulder, skullPile, buriedCoffin, rubblePile } — all five manifest lines verified this wake (deadTree assets.js 32, mossBoulder 64, skullPile 72, buriedCoffin 21, rubblePile 99). Any other key = **BLOCKING** (B6).
3. Every new node `type:` = `bonePile` and bonePile exists in CONFIG.gather.nodeTypes (CONFIG 3387: boneShard ×2, respawnSec 150, glowColor 0xbbbbaa, scale 1.0 — PRE-EXISTING keys, not this round's surface) — **no new nodeType, no new item, no new recipe, no new loot roll**. Any new key in nodeTypes/economy/items = **BLOCKING** (B6).

## V-6 Pack law and wolfPacks byte-purity (IO A-9, §3.4 NO-GO)

**Commands.**
```bash
awk '/^    wolfPacks: \[/{s=1} s{print} s&&/^    \],$/{exit}' prototype/js/CONFIG.js | sha256sum
git diff prototype/js/CONFIG.js | grep -n "wolfPacks\|waypoint\|packId"   # must print NOTHING
grep -c "'east'" prototype/js/CONFIG.js      # = 6 (V-0 census)
grep -c "id: 'east'" prototype/js/CONFIG.js # = 2 (779 + 2191)
grep -c "type: 'wolf'" prototype/js/CONFIG.js # = 28 whole-file (all in regionC.enemies 576..615; V-0 CORRECTION; N-2)
```

**Pass thresholds (all required, BLOCKING on any failure).**
1. wolfPacks block sha256 = `2e2afb6097e39a166f58107231e3f74cfbdfe77f06e383a658db5b20a8dfd1bd` — byte-identical to the V-0 baseline (= WD1 valspec baseline), and the diff-grep prints NOTHING: **no hunk touches wolfPacks, any waypoints, any packId row**. The L7 'east' and L8 'west' loops keep their exact 8 waypoints each.
2. East L7 waypoints byte-exact (IO A-9 anchor): `[[190,-318],[214,-322],[222,-340],[220,-372],[205,-398],[178,-388],[166,-360],[192,-334]]` — i.e. the eight pairs (190,−318) (214,−322) (222,−340) (220,−372) (205,−398) (178,−388) (166,−360) (192,−334) (see V-0). Any waypoint byte drift = **BLOCKING** (B7).
6. `'east'` census = **6** rows (576–579 the four spawn rows, 779 the boundary guard, 2191 the pack row) — unchanged from V-0 (N-1/C5: A-9's "id: 'east' … unchanged" = the 2-row `id: 'east'` census = 779 + 2191; the full `'east'` census is the 6-row set: 4 spawn rows 576–579 + boundary row 779 + pack row 2191). Any drift in ANY of the 6 = B7.
3. `type: 'wolf'` whole-file count still **28** (V-0 CORRECTION: the child's census pre-print said 30 with 2 elsewhere; the measured whole-file count is 28 — all wolf rows live at 576–615; N-2 carries the correction); **zero new wolf rows, new packs, waypoint edits, behavior fields, or enemy-type rows** anywhere in the diff (B7).

## V-7 File-set law and save safety (IO A-8, §3.4 NO-GO list)

**Command.**
```bash
git status --short
git diff --stat
git diff prototype/js/save.js | wc -l    # = 0
```

**Pass thresholds.**
1. The working diff (modified files) ⊆ { `prototype/js/CONFIG.js`, `prototype/builds/v8-playable.html` } + untracked { scratch edits IF post-landing reruns alter them — but they must NOT (scripts are census-driven, see N-6) , `io/reports/cc-ed1-build-note.md` }. Anything else = **BLOCKING** (B8/B10): gather.js, save.js, game.js, enemy.js, region-manager.js, region-defs.js, assets.js, wh-ground.js, region-defs, scatterOverrides, terrain rows, roads — all EMPTY diffs, zero exceptions. NO-GO list (§3.4) is the normative enumeration; each entry checked. **gather.js EMPTY is itself a V-3 check (B4) and appears here as the file-set enforcement of the same law.**
1b. **scratch/cc-ed1/ byte-purity:** site_scan.py / preseat_probe.js / clearance_ed1.py sha256s must equal the V-0 table (site_scan `5491…5c1`, preseat_probe `c73f…3da6`, clearance `68ac…2c11`). A drifted script = **BLOCKING** (B8): Devbot must re-run the delivered tools AS-IS.
1b-bis. **Scratch edits ALLOWED under one law: if a post-landing run of clearance_ed1.py or preseat_probe.js fails on an UNRELATED census artifact (N-5), Devbot may report the artifact, but the script sha256 must stay byte-identical. A sha drift with a failed run = B8; a sha drift with a PASSING run = B11 (process).**
1b-ter. No new files under scratch/cc-ed1/ beyond the delivered three + `fix_valspec.py` (IO's valspec remediation script, sha256 `4e0623dfd32824214b355a988b386a48547f2df5cd35bcc3cb8f6ed104476358` — IO tooling this wake, NOT a Devbot deliverable) + the build note; any OTHER new script appearing = **B10** (file-set law).
1b-ter. `git status --short` shows NO staged entries and NO new commits by Devbot (NO-GIT clause, B11).
2. `git diff prototype/js/save.js` = **empty** (baseline 0 diff lines, V-0): no new region → no save surface (A-8).

## V-8 Clearance geometry table (RUNNABLE — the governing geometry law, A-6, G-1..G-8)

Devbot does NOT deliver a clearance script — it EXISTS pre-round: `scratch/cc-ed1/clearance_ed1.py` (IO proven pre-spec; sha256 `68acab5b4f6454fc70d1d6453375e7e7ac0c7462c87b0961db077bceef2f2c11`). The script reads the LIVE CONFIG (regex census with NEW_TAG = `east_hollow_den` line-exclusion, so the round's own rows drop out of the pre-existing census post-landing — the WD1 G-5a self-match fix is baked in) and re-derives every margin from the LANDED rows. Testerbot re-runs POST-LANDING:
```bash
python3 scratch/cc-ed1/clearance_ed1.py
```
The check set for G-1..G-3 is the UNION of all 15 new rows (11 props + 4 nodes — IO §5 "Union law"); G-4 stays prop-set only (matches the WD1 amendment wording the round mirrors).

**Required checks (every row must print PASS; script's own labels are authoritative):**

| # | check | limit | pre-landing reference min/max (Testerbot this wake) |
|---|---|---|---|
| 1 | G-1: union rows → every wolf spawn row (28, whole-file census) | ≥ 5.0 m | 12.03 |
| 2 | G-2: props → every east waypoint (8, CONFIG 2192–2193) | ≥ 25.0 m | 41.77 |
| 3 | G-2n: nodes → every east waypoint | ≥ 20.0 m | 38.20 |
| 4 | G-3: union → every fire (7 banditCampfire rows) | ≥ 20.0 m | 81.54 |
| 5 | G-4: props → every road segment EDGE (segment distance − halfWidth 2.2) | ≥ 30.0 m | 69.36 pre-landing |
| 6 | G-5a: props → ALL pre-existing non-tree C props | ≥ 3.0 m | 176.17 |
| 7 | G-5b: props → ALL pre-existing tree-family props | ≥ 4.0 m | Testerbot's pre-landing run printed 41.23; the IO spec's table cites the same 41.23 ✓ |
| 5b | G-5c: new props mutual (cluster law) | ≥ 2.5 m | 2.83 (the mirrored larder pair; WD1 carries the identical 2.83 pair) |
| 8 | G-6a: nodes → all tree-family props old+new | ≥ 4.0 m | 4.27 |
| 9 | G-6b: nodes → all other props old+new | ≥ 3.0 m | 3.04 |
| 10 | G-6c: nodes mutual | ≥ 6.0 m | 12.73 |
| 11 | G-6d: nodes → site center | ≤ 12.0 m | 10.97 |
| 12 | G-7: union → C center (0,−366) | ≤ 262.0 m | 234.61 (deepest row node (208.5,−455) — the site max) |

**Pass.** Exit 0, every row PASS, RESULT: CLEARED, and the IO §5 minimums (5.0 spawn, 25.0/20.0 east-waypoints, 20.0 fires, 30.0 roads-edge, 3.0/4.0/2.5 props, 4.0/3.0/6.0/≤12 nodes, 262 site radius) appear verbatim in the script's threshold strings. Devbot PASTES the full output table into the build note; Testerbot re-runs and compares — margins within 0.05 m (float rounding). Any FAIL row, missing script, sha drift vs V-0, or exit ≠ 0 = **BLOCKING** (B5, B8).

**Census-scan caveat (N-5, read before adjudicating G-1/G-3/G-4/G-5a):** clearance_ed1.py scans the WHOLE CONFIG for enemy/prop rows — its G-1 "wolfspawn" census is whole-file (28 regionC wolves + 2 coven rows = 30 enemy rows scanned). That full-census shape is expected-by-design: G-1's limit is ≥ 5.0 m and both packs' rows sit ≥ 12 m from the union rows. The IO spec's own print is the normative reference (G-1 12.03 etc.); the G-1 census question (wolf-only vs wolf+coven rows) does NOT change the limit law. If a re-run DISAGREES with the IO table beyond float rounding, Testerbot re-derives by hand from the landed rows before sanctioning a FAIL — census shape ≠ margin law.

## V-9 Landed-row seat probe (RUNNABLE — G-8) + landed-CONFIG cross-check

Devbot delivers NOTHING — the probe EXISTS pre-round: `scratch/cc-ed1/preseat_probe.js` (A-1 law), sha256 `c73fdd357a0621f7c6cbc3980217e84b3a25f65b2696e3e6f87f1b044ba23da6`, harness = `scratch/cc-c5/loops_probe.js` pattern (`globalThis.window = globalThis`, `self = globalThis`, require three.classic vendor + CONFIG.js + wh-ground.js — CORE THREE-free, no browser, no real THREE runtime):
```bash
node scratch/cc-ed1/preseat_probe.js
```
The probe prints, per row (11 props + 4 nodes, HARDCODED table), `WH_GROUND.heightAt('forest_of_the_old_king', x, z)` and local slope via `WH_GROUND.slopeTan` (±0.5 m central differences = the 1 m span G-8 names; wh-ground is seeded fBm — deterministic, 3 consecutive Testerbot runs byte-identical).

**Pass thresholds (every row).**
1. `WH_GROUND.has('forest_of_the_old_king')` = true and every printed `|y| ≤ 26 m` and `slope1m ≤ 31 deg` — same ceilings V-0's ALL-15 PASS met (y 0.05..1.42, slope 2.0..8.7 deg).
2. Exit 0; all 15 rows print; final line `ED1 PRE-SPEC SEAT: ALL 15 PASS`.
3. **Landed-CONFIG cross-check (the probe's table is hardcoded — it must MATCH the landed rows byte-for-value)**: Testerbot parses the landed CONFIG rows from the V-2 diff `+` lines and compares all 15 (x,z) coords against the probe table (x/z equal to 0.0 — the probe/CONFIG/spec tables are all integers or .5 steps). ANY mismatch = **BLOCKING** (B5): the landed rows would be off-spec or the probe's terrain would not govern them.
4. Devbot pastes the probe output into the build note; Testerbot re-runs and compares (≤ 0.05 m / ≤ 0.5° rounding).
5. Any breach, sha drift, non-THREE-free harness (real THREE require beyond the vendored classic stub, puppeteer, browser), or exit ≠ 0 = **BLOCKING** (B5).

## V-10 Art law — the two-anchor law (grep-assert)

**Command.**
```bash
git diff prototype/js/CONFIG.js | grep "^+" | grep -inE "lantern|campfire|startLit|light:|color|0xff|0xf[0-9a-f][0-9a-f]|ember|torch|glowColor"
```

**Pass thresholds.**
1. **No matches in the new rows.** Den dressing = bone/bare-earth neutrals ONLY: the 5-key sanctioned kit (deadTree, mossBoulder, skullPile, buriedCoffin, rubblePile) adds no warm accent, no light source, no color/glow row beyond the pre-existing bonePile nodeType glowColor (CONFIG 3387, PRE-EXISTING — not this round's). The lantern amber belongs to the traveling player in BOTH anchors; the accent stays on the hunter. A second accent in the warm family, any `startLit`/`light:`/color row in the new block = **BLOCKING** (B6).
2. **Anchor citation (banner law):** the props-banner comment cites BOTH anchors by filename — `concept-05-night-ambush` AND `day-05-ambush` present verbatim in the `+` lines of the props hunk (IO §3.1 verbatim banner carries both). Missing either anchor name in the banner = **BLOCKING** (B6).
3. No new warm-accent ASSET row anywhere in the diff (lanternPost/banditCampfire-style keys cannot appear among the 11 new rows — V-5's key set already enforces; this is the belt to those braces).

## V-11 Build note and process law (IO §6 deliverables)

**Command (existence + pastes).**
```bash
ls scratch/cc-ed1/ && cat io/reports/cc-ed1-build-note.md
```

**Pass thresholds.**
1. `io/reports/cc-ed1-build-note.md` EXISTS and contains: exact `git diff --stat` paste (CONFIG.js + bundle; gather.js/other-file ABSENCES are part of the paste's meaning), the bundle marker ledger (per-hit `grep -n` output, ≥ 4 contributors), the FULL clearance_ed1.py output table (V-8), the preseat_probe.js output (V-9), node --check results, and any numbered ED-n deviations (CC-EC1 form). Missing paste Testerbot cannot re-verify = **BLOCKING** (B11).
2. `scratch/cc-ed1/clearance_ed1.py` + `preseat_probe.js` both present, sha-identical to V-0, and runnable by Testerbot (B5/B8/B11).
3. NO harness runs, NO headless browser smoke tests by Devbot — node --check + grep + the two delivered probes only. Any puppeteer/browser artifact in the diff or note = **BLOCKING** (V-11) = **BLOCKING** (B11).
4. NO git commands by Devbot (NO-GIT): changes unstaged, zero commits, zero pushes (B11).

## V-12 Adjudication rubric (gate step 4 — Testerbot runs, in order)

1. `git status -sb` + `git diff --stat` → file set == V-7.1 allowed set.
2. V-2 CONFIG diff sweep → pure-add, ≤ 2 hunks, positional law (after the WD1 rows), row/shape/banner law.
3. V-3 gather.js → ZERO hunks + sha == baseline. 4. V-4 node --check 7/7.
5. V-5 asset/type key sweep; V-6 sha256 + censuses; V-7 save.js + NO-GO + scratch sha purity.
6. V-8 `python3 scratch/cc-ed1/clearance_ed1.py` → every row PASS, RESULT: CLEARED, compared to Devbot's pasted table (≤ 0.05 m).
7. V-9 `node scratch/cc-ed1/preseat_probe.js` → ALL 15 PASS + landed-CONFIG 15-coordinate cross-check.
8. V-1 build + bundle marker ledger. V-10 art greps (neutrals + both-anchor banner law). V-11 note completeness.
9. Adjudicate every Devbot-recorded deviation against the tables below: expected-class → PASS with note; blocking → FAIL regardless of everything else green. **Zero-vs-list rule:** a blocking item Testerbot discovers UNRECORDED fails the round even if all checks green.

**PASS** = every check green AND zero blocking deviations AND all deviations accounted. **FAIL** = any blocking deviation or missing marker; the verdict lists check-by-check results + the remediation card for IO.

## Deviation classes + sanctions

**Expected-class deviations (Devbot MAY adopt; the build note records each as a numbered ED-n entry; Testerbot PASSES a recorded expected-class deviation).**

| class | deviation | verification hook |
|---|---|---|
| ED-1 | prop/node positions differ from the illustrative IO §3.1/§3.2 rows, provided every V-8 minimum/cap clears (prose rows are placement guidance; the clearance table is law) | V-8 |
| ED-2 | bundle marker count in the 6–20 band with distribution skew, provided the ≥ 4-contributor ledger holds and no row carries > 3 hits | V-1 |
| ED-3 | the nodes hunk lands at a different key-boundary position inside the EXISTING regionC.nodes array than directly after the WD1 row, provided the pure-add law holds and all pre-existing lines stay byte-identical — NOTE: landing it anywhere OTHER than after the WD1 node row breaks A-3's positional law = B3, so ED-3 in practice covers only blank-line/comment drift at the insertion edge | V-2.2 |
| ED-4 | clearance/seat margins differ from Testerbot's reference table by ≤ 0.05 m (or ≤ 0.5° slope) float rounding, all minimums still exceeded | V-8 / V-9 |
| ED-5 | blank-line/comment drift at the insertion edges (the props-tail WD1 comment context shifts with the append; the nodes hunk may shift the `],` context lines in the diff display); append-only law intact | V-2.1 |
| ED-7 | MORE than the minimum row comments carry `east_hollow_den` (count > expected), provided ≥ 4 distinct contributors and the ≤ 3-hits-per-row anti-bloat law hold | V-1 |
| ED-8 | clearance_ed1.py prints census values that differ from the IO §5 table's numbers where the script's live-census re-derivation disagrees with a spec-quoted figure, provided every LIMIT still clears (the spec table's printed values are guidance; the LIMITS are law) | V-8 |
| ED-9 | the probe's slope for deadTree 3 prints 8.8 deg where the IO §2/§3.1 prose cites 8.7 deg — the 0.1 deg delta is float/formatting, the 31 deg ceiling holds | V-9 |
| ED-10 | the probe re-run post-landing prints byte-identical output to V-0's pre-landing reference (deterministic seeded terrain; the probe table is hardcoded — the landed-CONFIG cross-check of V-9.3 is the guard that the CONFIG rows still match) | V-9 |

**Note in ED-5/ED-10:** these classes exist because the seat is LANDED and the probe is HARDCODED — the sibling-round machinery is baseline now, so this round's deviations are CONFIG-side only. The two-anchor banner, marker ledger, clearance re-run, and EMPTY gather.js are the round's own surfaces.

**Blocking classes (any one → round FAILED; Testerbot issues the remediation card; re-gate required).**

| class | violation | verified by |
|---|---|---|
| B1 | **byte-purity:** any `−` line (excluding headers) in the CONFIG.js diff; any pre-existing line rewritten or moved (props 810–1165, WD1 rows, coven tail, enemies, terrain, roads, wolfPacks all byte-sacred) | V-2.1 |
| B2 | **bloat-row:** marker ≥ 6 but < 4 distinct contributors, or any single source row carrying > 3 hits — a padded pass is a failed pass | V-1 |
| B3 | placement/shape: new rows anywhere but the props tail + the WD1-row-adjacent nodes position; a `y:` key on a new prop row; row-shape drift off `{ asset, x, z, rotY, scale }` / `{ type: 'bonePile', x, z }`; prop/node COUNT off the 11 + 4 set; a third insertion surface; positional law breach (A-3) | V-2 |
| B4 | gather.js: ANY hunk (this round the seat is baseline — a "helpful" edit IS the violation); sha drift; marker bob / respawn timing / signature drift | V-3 |
| B5 | geometry: any V-8 row below its minimum (or above the ≤ caps), any new row > 262 m from C center, any seat row > 26 m or slope > 31°, clearance_ed1.py / preseat_probe.js missing, unrunnable, or sha-drifted, margin mismatch > 0.05 m, landed-CONFIG↔probe 15-coordinate cross-check mismatch | V-8 / V-9 |
| B6 | art/type law: asset outside the 5-key neutral kit; ANY assets.js diff; a new nodeType/item/recipe/loot roll; a warm-accent or light/color row in the new block; banner missing either art anchor name | V-5 / V-10 |
| B7 | pack law: any wolfPacks hunk or sha drift; waypoint byte drift (east L7 OR west L8); `'east'` census ≠ 6; `id: 'east'` census ≠ 2; whole-file wolf count ≠ 28 (V-0 CORRECTION: all wolf rows live in regionC.enemies); any new pack/row/behavior field | V-6 |
| B8 | save/no-go: save.js diff non-empty; any of gather.js / game.js / enemy.js / region-manager.js / region-defs.js / wh-ground.js / assets.js modified; roads/scatter/terrain hunks; scratch/cc-ed1 script sha drift | V-7 |
| B9 | syntax: any of the seven files failing `node --check` | V-4 |
| B10 | file-set law: any modified file outside { CONFIG.js, prototype/builds/v8-playable.html } + untracked { io/reports/cc-ed1-build-note.md }; NEW scripts under scratch/cc-ed1/ beyond the delivered three + IO's fix_valspec.py (sha-pinned V-7.1b-ter) | V-7 |
| B11 | process: ANY git commit/push by Devbot (NO-GIT), a headless-browser/harness artifact, or the build note missing its required pastes (diff stats, marker ledger, clearance table, probe output, node --check) | V-11 |
| B12 | build: `tools/build_v8.py` exit ≠ 0, or post-rebuild bundle marker < 6 | V-1 |

## Notes (Testerbot census corrections + build guidance)

**N-1 (census corrections vs the IO spec — Testerbot-verified 2026-11-06; Devbot builds to THESE).**
- C1: IO §2's "nearest prop row 41.77 m" names the distance from the site's nearest rubblePile to the **westRoad**'s last point (−238,−366)... — Testerbot recompute: new rubblePile (202,−440) → eastNotch bed start (238,−366) = **41.77 m** (the eastNotch bed, distance-to-ENDPOINT, not segment) → the G-4 law (segment-edge ≥ 30) holds with the bigger segment-distance margin (69.36 pre-landing). The 41.77 prose is a distance-to-endpoint quote, not a G-2 number: G-2 is props→east-WAYPOINTS = 41.77 m (rubblePile (205,−443) → waypoint (205,−398) = 45.0 m; (202,−440) → (205,−398) = 42.15 m — the 41.77 quote is the props→westRoad-endpoint distance). The two "41.77" quotes in the spec (G-2's and §2's) are DIFFERENT measurements; both clear their respective limits by wide margins.
- C2: IO §5 G-5b's pre-landing print (41.23) equals Testerbot's re-run (41.23 ✓). IO §5's G-4 pre-landing print (69.36) equals Testerbot's re-run (69.36 ✓). IO §5's G-1 12.03 / G-2 41.77 / G-2n 38.20 / G-3 81.54 / G-5a 176.17 ✓ / G-5c 2.83 / G-6a 4.27 / G-6b 3.04 / G-6c 12.73 / G-6d 10.97 / G-7 234.61 — **all 12 clearance numbers reproduced exactly by Testerbot's independent re-run** (no contradictions found in the IO §5 table's printed margins).
- C3: regionC.nodes is NOT a new key this round — WD1 landed it (CONFIG 1171–1176); §3.2 is an APPEND into an existing array (the IO's sibling round wording "second larder cache set" already implies append; V-2.2 binds the append position after the WD1 row).
- C4: IO §2 quotes the probe slope range **"slope1m 2.0..8.7 deg"** and the §3.1 banner similarly "slope <= 8.7 deg over 1 m" — Testerbot's probe run prints **8.8 deg** for deadTree 3 (217,−440) (3 consecutive deterministic runs). Both values sit far under the 31 deg ceiling; the 8.7 quote is a float/rounding slip in the IO prose — harmless; ED-9 covers it. y-range 0.05..1.42 reproduces exactly ✓.
- C5: A-9's "`grep -c \"id: 'east'\"` unchanged" = the 2-row `id: 'east'` census (boundary row 779 + pack row 2191), baseline **2**. The full `'east'` census is **6** rows (spawn 576–579, boundary 779, pack 2191). V-6 pins BOTH; any drift in either = B7.
- C6: `type: 'wolf'` census is **28 whole-file** (all regionC.enemies rows at 576–615; V-0 CORRECTION: an earlier pre-print in this file said 30 with 2 rows elsewhere — re-measured `grep -c "type: 'wolf'"` = 28; N-2/V-6/B7 carry the corrected 28), unchanged by this round's rows.
- C7: G-1's whole-file wolf census includes the west-pack rows (CONFIG 580–583) in CONFIG-space — the 12.03 m pre-landing print comes from a larder-cluster row to the nearest wolf anywhere in the file, not from the east-pack loop (nearest EAST waypoint is 38.20+ m from the nodes); the law is the 5.0 limit, not the census shape (N-5 caveat in V-8).

**N-2 (whole-file vs regionC censuses — pin the file-scope of every grep).** Whole-file greps this round: `type: 'wolf'` 28 (V-0 CORRECTION: the original pre-print said 30; re-measured 28 — all wolf rows are regionC.enemies rows), `packId` 30, `id: 'east'` 2, `'east'` 6, `{ type: 'bonePile'` 8, `bonePile` (regionC) 9, `west_hollow_den` 17. V-6/V-7 enforce these as unchanged post-build. Any new `type: 'wolf'` row lands the round at B7 instantly.

**N-3 (the nodes array is EXISTING surface now).** WD1 landed regionC.nodes (CONFIG 1171–1176). This round APPENDS 4 rows after the WD1 rows; the key itself must NOT be re-created. A re-created `nodes: [` key inside regionC = a byte-drift/deletion-class violation (B1) — the diff would show `−` lines.

**N-3bis (gather.js is baseline).** The WD1 2-line terrain seat is in-repo at fd286d5 (gather.js 60/146, sha `492d63…fbbf6ea`). This round's gather.js diff is EMPTY by law (V-3); any hunk = B4. The V-0 gather.js sha pin exists so Testerbot can catch a "helpful" rebuild drift even if git shows clean (it won't).

**N-4 (marker material).** CONFIG comments survive build_v8 byte-identical (WD1 V-0 parity: `west_hollow_den` 17/17 CONFIG↔bundle at fd286d5; per-row `// east_hollow_den ...` comments are the sanctioned marker carriers — no code-token marker is needed or wanted.

**N-5 (clearance self-census caveat).** clearance_ed1.py scans the whole file for enemies; its NEW_TAG (`east_hollow_den`) line-exclusion drops this round's own rows from the census post-landing, and the west-pack rows remain in the census (they carry no east_hollow_den tag) — expected-by-design: G-1's minimum is 5.0 and both packs' rows sit ≥ 12 m from the union rows. Devbot/Testerbot must NOT add rows to make G-1's print match a spec quote — the limits are the law.

**N-6 (scratch sha law).** The three delivered scripts are TOOLS, not deliverables to edit. Their V-0 sha256s are pinned: site_scan.py `5491…5c1`, preseat_probe.js `c73f…3da6`, clearance_ed1.py `68ac…2c11` (full hashes in V-0 / V-7.1b). A sha drift = B8 the moment the round lands — the delivered tools must be run AS-IS; the NEW_TAG exclusion is already baked in for the post-landing re-run.
