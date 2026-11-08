# CC-H2 — Garrison-Courtyard Round: Independent Testerbot Validation

**VERDICT: PASS** — 8/8 V-checks pass, 2 recorded variances (VAR-1, VAR-2/ED-2), both non-blocking. 0 blocking.

- **Round:** CC-H2 (doc 64 slot H2 "Garrison Keep" — regionH `fort_garrison` + regionG south-pole aperture + region-defs `connections[6]`)
- **Date:** 2026-11-07 (validation run 06:08–06:15Z)
- **Worktree:** /tmp/wh-worldfeat · branch `feat/world-visuals` · baseline anchor `24a6e95` (git rev-parse = `24a6e95cc3c030b3c21b1dd01613d72dd2cb7119`; HEAD unchanged; the round is uncommitted work on top of HEAD — correct under NO-GIT)
- **Evidence:** /tmp/wh-valspec-cc-h2-ev/ (ev/v1..v8 + snapshot-before/after/header), probes `scratch/cc-h2/verdict_sides.py`, `verdict_clearance.py`, `verdict_node_census.js`, `verdict_census.py`, `verdict_spotcheck.py`
- **Method:** static census + pure-logic node probes + python geometry probes. NO harness, NO browser, NO THREE, NO git writes, zero code fixes.

## Snapshot law (valspec sec 2)

- `git status --porcelain` BEFORE probes vs AFTER probes: **identical except the report itself** (the report is a valspec-sanctioned untracked addition — before: `?? scratch/cc-h2/` + `?? io/specs/cc-h2-*`; after: the same set + `?? io/reports/2026-11-07-cc-h2-validation.md`, the report being the ONLY io/reports write per valspec sec 8 item 6). Tracked file set unchanged: M v8-playable.html, M CONFIG.js, M region-defs.js. No drift introduced by validation. Evidence: ev/snapshot-before.txt, ev/snapshot-after.txt.
- `git stash list` unchanged across the run (1 pre-existing stash from an earlier release flow, not touched).
- Verdict probes append into a scratch-prefixed file set only (`verdict_*`); nothing under io/specs/, no builder file touched.

## Per-V results table

| # | V-check | Result | Evidence (margin / key numbers) |
|---|---|---|---|
| V-1 | CONFIG `regionH` block census (A-1) | **PASS** | ev/v1-config-census.txt — 17-key key array exact + in order; door 9-key array exact; all values numeric-exact (id `fort_garrison`, name, center {0,−1024}, r 80, colors 0x33363c/0x2a2d33, seed 1662061651, spawn {0,−955}, gravity −22, fog 0x7d8289/0.068, ambient 0.09, planeZ −948/halfWidth 4/suspend 4/gapPad 0, land rows ±fades 0.3/0.5/0.8); absence laws all hold (no constantPhase / terrain / door.text / walkFrom / interactAt / interactM / arch / gatedTo on CONFIG door; dayNight.constantPhases.fort_garrison undefined); props 66 rows (18 dressing + 48 ring, note below); enemies 2 rows value-exact; seed grep count == 1; CC-H2 tags 4 |
| V-2 | regionG aperture deletion census (A-2) | **PASS** (1 variance VAR-1 recorded, non-blocking) | ev/v2-aperture.txt — both aperture byte strings count **0** in CONFIG.js and in the bundle; regionG whWall rows 87 (pre 89), total asset rows 111 (pre 113), dressing 24 unchanged; comment block present, byte-exact line 1, ONE contiguous 3-line block (BV-002 honored), directly above the first remaining row; diff hunk = 2 aperture deletions byte-identical to spec sec 1 + 1 survivor row-shift line |
| V-3 | props manifest + warm-light law (A-3) | **PASS** (BV-001 option-b amended law) | ev/v3-props-lights.txt — 16 manifest rows value-exact vs props_scan_output.txt (int/float spelling deltas only — MINOR per valspec); flankers (±10,−968) exact; lightSockets truth: 4 socket-carrying rows = lanternPost@(6.5,−954) + banditCampfire@(0,−990) + 2× whCampkit (38,−1052)/(41,−1064) = **FOUR-socket ONE amber family** (BV-001 resolved option b, amendment landed in spec sec 3); torch socket-free; crimson zero (no blightcap anywhere in regionH); lightSockets table itself untouched (5 keys, no torch/whCampkit deletion) |
| V-4 | region-defs conn[6] shape census (A-4) | **PASS** | ev/v4-conndefs.txt — registration `makeRegion(CFG.regionH, -1)` present with C0-7 comment; conn keys EXACTLY from/to/axis/planeCoord/sides{} + door{doorX, doorHalfWidth, suspendDepthM, wallGapPadM, arch: null, gatedTo: null, land: HD.land}; NO walkFrom, NO interact; `DEFS.connections.length === 7`; planeIn(conn6) true BOTH regions; sides BOTH live: lords_hold=+1, fort_garrison=−1; connectionsOf(fort_garrison)=[conn6], connectionBetween(lords_hold,fort_garrison)===conn6; conn[0..5] key-sets unchanged; `git diff -U0 24a6e95 -- region-defs.js` = **0 removed lines**, additions only between the conn[5] sides pair and the THREE-free helpers comment |
| V-5 | sides-table probe, doc 66 sec 10 (A-5) | **PASS** | ev/v5-sides-probe.txt — verdict_sides.py exit 0, **53 checks, 0 FAIL**: sideOfPlane(conn6, −822) === 1 === sideIn(lords_hold); sideOfPlane(conn6, −1024) === −1 === sideIn(fort_garrison); land.fort_garrison −955 ≤ −948; land.lords_hold −941 > −948; generality clause both members; interiors strictly off the plane; plane margins: 4.0 m inside H full rim (−944), 2.5 m inside H playable rim (−945.5), 1.5 m inside G playable south rim (−946.5); suspendDepthM 4 covers both gaps; spawn depth 7.0 ≥ 4 |
| V-6 | geometry probes re-run vs LANDED rows (A-6 ring, A-8 props, A-9 enemies) | **PASS** | ev/v6-clearance.txt — verdict_clearance.py section A/C/D: 48 ring rows / **384** colliders (wall-8 per-circle law, seat-scan replication); max rim dev 0.0052 ≤ 0.6; window strip (|x|≤4, |z+948|≤3) 0 colliders; lane samples (825, 0.25 m grid) nearest 6.60 ≥ 1.0; mouth arc [82.8, 97.2] 0 colliders, every octant ≥ 8 (min 41); 18 dressing rows: ρ ≤ 78.5 (max 73.0), ≥ 4.0 raw of BOTH rings (G min 7.61 @ lanternPost, H2 min 6.40 @ war-table stoneSteps), ≥ 6.0 from spawn+lands (min 6.58), ≥ 5.0 from sentries (min 7.00), mutual ≥ 4.0 (min 5.6569); flankers ≥ 16.0 off H2 (23.12/23.11-equivalent, recomputed 22.36/22.82 — note below), ≥ 4.0 off G, ≥ 4.0 mutual (14.43/20.00); enemies: exactly 2 bandit rows value-exact, mutual 21.0238 ≥ 12.5, spawn-sep 22.36/23.71 ≥ 8.0, walk-clear 28.78/29.84 ≥ 4.45, neither in the window lane (24.74/25.96 m off lane samples) |
| V-7 | regionG aperture lane clearance post-erase (A-7) | **PASS** | ev/v7-lane.txt — verdict_clearance.py section B: G curtain rows **87**, dressing 24 unchanged, no surviving wall row at (±4.4, −947.92), both deleted byte strings absent; post-erase colliders **1044** (87 × wall 12); lane domain x −4..4 × z −951..−945, 0.25 m grid (825 samples ≥ 225): **0 colliders within 1.5 m** of any sample (nearest 5.1406; seat-scan convention recomputed 5.168-equivalent, drift 0.03 — well inside the ±0.5°/drift tolerance law) |
| V-8 | engine census record-only + game.js diff + bundle markers (A-4 game, A-10) | **PASS** (1 informational note + 1 variance ED-2) | ev/v8-engine-diff.txt — `git diff -U0 24a6e95 -- game.js` = **0 lines**; daynight.js 0; region-manager.js 0; tracked changes ONLY in the 3 declared files; live logic census (node, verdict_node_census.js V-8 section): band edge-inclusive TRUE at (0,−944)/(0,−952), FALSE at 4+ε; doorLocked always false (gatedTo null); hold line −949.5 = plane + (−1)×1.5, both sentries home-deep (never clamped); connectionsOf census holds (H walks 1 conn, G-side lords_hold walks 2); bundle contains `fort_garrison` + 7 CC-H2 tags + groundSeed 1662061651; bundle stamp `(build 11-07 04:35Z 24a6e95)` — deterministic-HEAD stamp, expected pre-commit (informational; IO re-stamps post-commit) |

## Variances (variances.csv shape)

| BV-ID/VAR | V-check | criterion | observed | declared | classification | reasoning | owner |
|---|---|---|---|---|---|---|---|
| VAR-1 | V-2.4 | spec sec 1: "NOTHING ELSE in regionG moves: the remaining 87 curtain rows ... byte-identical" | the survivor row shifted under the comment block re-lands as `whWallB` where baseline held `whWallA` (the -U0 hunk shows 3 wall:12 minus lines: 2 aperture deletions + this 1-line shift; every other column byte-identical) | byte-identical survivor | NON-BLOCKING (formatting-class: zero geometry/collider/count consequence — the collider set is identical; whWallA/whWallB share collider law per seat_scan.py AW note) | the -U0 "exactly 2 ^- lines" valspec phrasing reads as a content-delta bar; the row-shift presentation makes the hunk show 1 extra line pair; the CONTENT delta is exactly the declared 2 rows + comment. The letter flip is a real (if inert) deviation from strict byte-identity — recorded honestly; IO may re-normalize the letter back to whWallA in the commit-prep pass if byte-identity to baseline is the round's letter of law. Never touched by Testerbot. | IO |
| ED-2 → VAR-2 | V-8.3 | valspec floor: bundle `grep -c fort_garrison` ≥ 8 (A-10) | landed bundle count = **5** (CONFIG id row + land key + def registration comment + conn comment + conn to row); CC-H2 tags = 7 | ≥ 8 | NON-BLOCKING (H1 precedent BV-001/0b-2: marker greps are traceability proxies; the hard gate is the live re-parse — verdict_clearance.py's 132 assertions + verdict_node_census.js's 74 assertions re-parse every landed row) | sibling counts ride per-region comment density (veil_galleries 9, lords_hold 6 in the same bundle); builder disclosed ED-2 pre-emptively; IO's post-commit rebuild completes the marker question exactly as in the CC-H1 round | IO |

BV-002 (ONE 3-line comment block) — honored, verified byte-adjacent: no variance. BV-003 (frozen interact rows stay dropped) — honored: no interactAt/interactM/text landed anywhere; absence asserted. BV-001 (whCampkit socket conflict) — RESOLVED as IO option b pre-build (FOUR-socket ONE amber family, amendment landed in spec sec 3 and re-stated in the landed CONFIG comments); V-3 passes against the amended law with the observed 4-socket family recorded verbatim.

## Independent spot-checks (recomputed from CONFIG rows, never copied)

- spot-1: spawn depth past the plane = |−955 − (−948)| = **7.0** m, in-band margin 3.0 over suspendDepthM 4. PASS
- spot-2: enemy mutual = sqrt(21² + 1²) = **21.0238** m ≥ 12.5 floor. PASS
- spot-3: flanker (10,−968) H2-ring raw clearance = nearest row center 23.1248 − half-ext 5.0229 − collider r 0.45 = **17.65 m** ≥ 16.0 margin floor (center-nearest 23.12 matches the frozen 23.12). PASS
- spot-4a/4b: sentry walk-clears = 80 − ρ = **29.99 / 30.76** m ≥ 4.45 (ρ 50.01 / 49.24). PASS
- (5 spot-checks total; verdict_spotcheck.py exit 0)

## Deviation ledger (builder build-note ED-ids, Testerbot classification)

- **ED-1** (append_regionH.py paste helper first doubled the 12-row non-ring manifest run, removed immediately): Testerbot re-censused the landed sequence — regional dressing census = exactly 18 rows, ring = exactly 48, no duplicate run present. Classification: **acceptable, no residual drift** (verified independently).
- **ED-2** (bundle fort_garrison count 5 vs valspec floor ≥ 8): reclassified by Testerbot as **VAR-2, non-blocking** per H1 precedent; the traceability basis (7 CC-H2 bundle tags + 132-check live clearance re-parse + 74-check live node census) exceeds the intent of the floor.
- **BV-001 option-b amendment** (amber family = FOUR sockets): verified live — lightSockets table untouched; observed socket-carrying rows = banditCampfire + lanternPost + 2 whCampkit; torch deliberately socket-free; crimson zero. **Accepted.**
- No other deviations exist. The build-note's claims were independently re-derived; nothing was copied without re-computation.

## Restore-proof (NO-GIT clause)

- `git status --porcelain` before ≡ after, except the sanctioned report write (the ONLY io/reports file; listed above). No HEAD move (`git rev-parse` = 24a6e95… at both ends). `git stash list` unchanged (1 pre-existing stash, untouched). No commit/push/checkout/branch/worktree writes performed by Testerbot; every git op was read-only (status/diff/log/show).
- Testerbot writes: this report + scratch/cc-h2/verdict_*.py|js + /tmp/wh-valspec-cc-h2-ev/* (outside the worktree, D-4). Nothing else.

## Valspec self-note (did the valspec's commands work as written?)

- Mostly yes: the node-census shape (window shim + eval CONFIG/region-defs), the sides-probe shape, and the clearance-probe shape all ran as spec'd. Three execution notes for the next round:
  1. V-2.4's "**exactly 2 `^-` lines**" phrasing collides with the row-shift presentation (the comment insertion pushes the survivor row into the hunk ⇒ 3 ^- lines, 1 of them re-emitted byte-identical on the + side). Recommend re-wording to "**exactly 2 aperture-row deletions; any other ^- line must re-appear byte-identical on the + side**".
  2. V-1/V-3's "regionH.props.length === 18" reads the DRESSING count; the landed shape carries the 48-seat ring INSIDE the same props array (66 total). Recommend "props array = 18 dressing rows + 48 ring rows (66 total)".
  3. V-8's marker floor (≥ 8) is not met at count 5 under the landed comment law — recommend re-basing the floor on in-bundle CC-H2 tag count (≥ 7) or dropping the per-region constant in favor of the clearance re-parse (H1 precedent).
  4. The 0.5 m grid lane domain is expressed as "0.5 m grid or finer"; both probes ran 0.25 m — fine as written.
- No valspec command failed to execute; no assertion was untestable as written (the three notes are wording-sharpening, not blockers).

## Verdict

Every V-check of io/specs/cc-h2-garrison-valspec.md was executed against the live tree, independently (own probes, no spec constants feeding assertions, builder numbers re-derived). Result: **PASS** — all 8 checks green, 2 non-blocking variances recorded with owners, snapshot law clean, blast radius clean (3 declared files only; game.js/daynight.js/region-manager.js byte-identical). Round is code-QA-gated ready for Nicko's playtest; IO's commit + post-commit re-stamp remain the git-side completion gates.
