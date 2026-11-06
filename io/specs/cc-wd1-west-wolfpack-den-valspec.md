# CC-WD1 VALSPEC — West Wolfpack Den Site (independent Testerbot validation spec)

Round: CC-WD1 · 2026-11-06 · Author: Testerbot (gate step 2 — written BEFORE Devbot builds)
Source of truth: `io/specs/cc-wd1-west-wolfpack-den-spec.md` (§4 acceptance criteria A-1..A-9, §5 geometry margins G-1..G-8, verbatim anchors)
Round contract: IO spec → Testerbot valspec → Devbot build → Testerbot validation → IO commit
Style parents: `io/specs/cc-ad1-veil-crypt-valspec.md` (V-anchors, ED/B classes, post-gate slice) + `io/specs/cc-ec1-coven-acolyte-valspec.md` (census corrections, verdict rubric)
Art anchor: `art-direction/concepts/concept-05-night-ambush.png` — indigo/charcoal base, NO new warm accents in den dressing (the lantern amber stays on the hunter); den dressing = bone/bare-earth neutrals only.

Base commit rule: validation diffs against HEAD **49106ea** (`feat/world-visuals`). Devbot leaves ALL changes UNSTAGED (NO-GIT clause, IO §6); Testerbot runs `git diff` against HEAD, never against a Devbot commit.

## V-0 Ground state (Testerbot's own census, taken 2026-11-06 before any build; Devbot must keep true)

All counts below were RUN by Testerbot this wake, in `/tmp/wh-worldfeat`, against HEAD 49106ea:

- `git status -sb` → `## feat/world-visuals` + ONLY `?? io/specs/cc-wd1-west-wolfpack-den-spec.md` untracked; **tracked-file working diff EMPTY** (`git diff --stat` prints nothing). The round's diff starts from a clean tree.
- Baseline `grep -c west_hollow_den prototype/builds/v8-playable.html` = **0** (the marker is NEW this round — any count ≥ 1 is this round's work). Bundle exists: 108,008 lines.
- `grep -c bonePile prototype/js/CONFIG.js` = **5** (4 Region-B node rows at 455–458 + the nodeTypes row at 3356) and `grep -c bonePile prototype/builds/v8-playable.html` = **5** — every CONFIG hit survives into the bundle.
- **CONFIG.js comments ARE preserved in the served bundle** (verified: `grep -c "den-local z -24.6"` = 1, `grep -c "CC-C17 ring fragment"` = 3 inside the current bundle) — so per-row `// west_hollow_den ...` comments are valid marker material, not stripped by build_v8.
- **CONFIG census** (3587 lines, sha256 `8197e89a95e0fc2c5847cf0d02825b4906538bd1e989d6b0582bb792bc435915`): `regionC: {` at **470** (id `forest_of_the_old_king`, center (0, −366), groundRadius 280 → playable r 278.5); props array OPEN at **810**, CLOSE `],` at **1145**, holding **221** pre-existing `{ asset:` rows; last pre-existing rows = the two CC-C17 ring-fragment mossBoulders at 1143–1144. **NO `nodes:` key anywhere in regionC** (470–1233) — only regionA (line 345) and regionB (line 449) carry nodes today. The regionC.nodes array is a NEW KEY, not an append into an existing array.
- regionC.enemies: OPEN 575, CLOSE 647-adjacent `],` at the coven tail; **28** `type: 'wolf'` rows (12 CC-C5 east/west/north at 576–587 + 16 CC-C16b densify at 600–615) + 2 CC-EC1 coven rows (`,{ type: 'coven', x: -118.4, z: -238.2 },` / `{ type: 'coven', x: -99.2, z: -249.1 }`) — comma-first continuation shape, byte-sacred.
- **wolfPacks block: lines 2159–2179** (`wolfPacks: [` at 2159, close `],` at 2179; separationPush 2180). **7 packs** (east/west/north/sw/se/ss/nw2), all `regionId: 'forest_of_the_old_king'`, all members 4 + spawnSpread 6. Block sha256 = **`2e2afb6097e39a166f58107231e3f74cfbdfe77f06e383a658db5b20a8dfd1bd`** (`sed -n '2159,2179p' prototype/js/CONFIG.js | sha256sum`).
- **'west' census = 6 rows** in CONFIG.js: 580–583 (4 west wolf spawn rows), 780 (westNotch rim row), 2163 (the wolfPacks pack row). The IO §4 A-9 reading "'west' … 1 pack row" is the wolfPacks-block SUBSET of this 6-row census (see N-1/C5) — V-6 pins the full census.
- **West-pack waypoints** (CONFIG 2165–2166, byte-exact): (−190,−420), (−215,−418), (−224,−388), (−224,−362), (−200,−358), (−178,−340), (−166,−372), (−172,−402). Testerbot recomputed: min distance hollow (−255, −410) → waypoint = **38.0 m** ((−224,−388)) ✓ IO §2.
- **gather.js** (178 lines, sha256 `9eb0479c79302d78cdcc9c6764bb563c906c51f142ada2ca5f1452eb12a5e390`): `    holder.position.set(x, 0, z);` at line **60** (inside makeNode — signature `function (regionId, type, x, z)` at line 55, so `regionId` is in scope); `    node.mesh.position.set(pick.x, 0, pick.z);` at line **146** (inside reshuffle — `node.regionId` in scope, used at line 131). **Zero WH_GROUND references in gather.js today.** The whole round's gather.js change = exactly these 2 lines.
- RegionB node rows at 455–458 are bonePile (4 rows) — they ride the SAME seat path; V-3's change must be a NO-OP for them (B has no heightfield → the `has()` guard yields 0, byte-equal behavior, N-3).
- `node --check` baseline: CONFIG.js, gather.js, game.js, save.js, region-manager.js, region-defs.js, assets.js — **7/7 OK** pre-build.
- `git diff prototype/js/save.js` = **empty** (0 diff lines) today; save.js 301 lines, untouched this round (A-8).
- Fires census: **7** `banditCampfire` prop rows in regionC props (998, 1004, 1010 Alphas/Bravos/Charlie + 1069–1072 the four CC-C16b camp fires), not 4 (IO §2's "all 4 C fires" = the CC-C16b subset — N-1/C1). Testerbot distances from the hollow: camp 1 (−106.1,−472.1) = **161.3 m** ✓ IO §2's quoted min; Charlie (−140,−506) = 149.8 m is the nearest of the full 7.
- Roads: CONFIG.roads at 1542; **9** C road rows (6 King's Roads incl. stoneRing + 3 notch beds). Nearest segment to the hollow: westNotch bed (y −366, x −240..−270) = **44.0 m** ✓ IO §2; westRoad mouth (−240,−366) = 46.5 m.
- Nearest ENEMY row to the hollow: west wolf spawn 0 (−190,−420) = **65.8 m** ✓ IO §2. Nearest pre-existing PROP: witchwoodTree (−178.2,−424.2) = **78.1 m** (Testerbot re-sweep of props 810–1145; IO §2's "nearest existing prop 65.8 m (wolf spawn row)" is a prop/enemy wording slip — N-1/C2).
- Site radius: hollow (−255,−410) → C center (0,−366) = **258.8 m** ✓ (playable 278.5; SW-quadrant rim-mountain foot per CC-C15).
- MANIFEST keys for the round all pre-exist in assets.js (16–188): buriedCoffin **21**, deadTree **32**, mossBoulder **64**, skullPile **72**, rubblePile **99**.
- `scratch/cc-wd1/` does **not** exist yet — Devbot creates it (clearance.py + seat probe; Testerbot's V-8/V-9 run after). Shape parent: `scratch/cc-c5/loops_probe.js` (globalThis.window = globalThis → require three.classic vendor → CONFIG.js → wh-ground.js).
- Build tool: `python3 tools/build_v8.py` — run IN the worktree; the served bundle is what gets grepped, never the repo copy.

## V-1 Build and bundle marker count (IO A-1, A-2)

**Command.** Run in `/tmp/wh-worldfeat`:
```bash
python3 tools/build_v8.py && echo "BUILD_EXIT=$?"
grep -c west_hollow_den prototype/builds/v8-playable.html
```
`BUILD_EXIT` must be 0, no Python traceback. Build in the worktree, never via absolute path out of it.

**Pass threshold.** Marker count **≥ 6** AND build exit 0. **BLOCKING** if below (B12).

**Ledger (additionality, not bloat).** Baseline = 0 (V-0), CONFIG comments survive the bundle (V-0) — expected contributors: props-section banner comment carrying `west_hollow_den` (1), nodes-section banner comment (1), ≥ 1 prop-row comment, ≥ 1 node-row comment ⇒ **≥ 4 distinct source contributors**, each mapping to a real CONFIG surface the diff shows. A count ≥ 6 reached by one padded comment row (< 4 contributors, or > 3 hits from a single row) = **BLOCKING-LEVEL-2** (class B2). Testerbot keeps a per-hit ledger (`grep -n west_hollow_den prototype/builds/v8-playable.html`) and reproduces it in the verdict.

## V-2 CONFIG.js diff purity and block placement (IO A-3)

**Command.**
```bash
git diff prototype/js/CONFIG.js
git diff prototype/js/CONFIG.js | grep -c "^-[^-]"
```

**Pass thresholds (all required, BLOCKING on any failure).**
1. **Pure-add diff:** `grep -c "^-[^-]"` = **0** (excluding the `---`/`+++` headers). Zero pre-existing lines rewritten or moved — the 221 props rows, the coven tail, regionC.enemies, terrain, roads stay byte-identical (EC1 append-only precedent at whole-file scope). Any `−` line = **BLOCKING** (B1).
2. **Two insertion surfaces ONLY:** (a) the 8 new prop rows + their banner comment sit inside regionC props [ ] between the last pre-existing row (CC-C17 mossBoulder fragment, line 1144 today) and the close `],` (1145); (b) the new `nodes: [` key + 4 bonePile rows + banner comment sit inside the regionC block as a NEW key (N-1/C3: no pre-existing nodes array exists there — nothing can be "appended into" it). Hunk count in the CONFIG diff ≤ 2. Any third surface = **BLOCKING** (B3).
3. **Row law:** every new prop row is exactly `{ asset, x, z, rotY, scale }` — **`y` is NEVER set** on a new row (region-manager whGroundFeed() seats C props on the terrain automatically; the `y:` keys on pre-existing C15/C17 outcrop rows are legacy shape, not license). Any `y:` on a new row = **BLOCKING** (B3). Node rows are `{ type: 'bonePile', x, z }`.
4. **Set law:** exactly 8 new prop rows — 3 deadTree (thicket mouth, NE arc), 3 mossBoulder (hollow rim, SW arc), 2 skullPile + 1 buriedCoffin (larder, NE, 4–7 m), 2 rubblePile (SE flank) — and exactly 4 new node rows, all `type: 'bonePile'` (3 larder-cluster + 1 thicket-mouth approach). Counts off = **BLOCKING** (B3).
5. **Marker banners:** both banner comments carry the literal string `west_hollow_den` (feeds V-1's ledger).

## V-3 gather.js terrain seat — the ONE non-CONFIG change (IO A-4, §3.3: EXACTLY 2 lines)

**Command.**
```bash
git diff prototype/js/gather.js
node --check prototype/js/gather.js && echo GATHER_OK
git diff prototype/js/gather.js | grep -c "^-[^-]"
git diff prototype/js/gather.js | grep -c "^+[^+]"
```

**Pass thresholds (all required, BLOCKING on any failure).** This 2-line change IS in-scope for validation (IO §3.3): Testerbot validates the WHOLE diff.
1. **Hunk shape: exactly 2 changed lines** — `grep -c "^-[^-]"` = **2** AND `grep -c "^+[^+]"` = **2** (plus headers). One hunk, spanning the makeNode seat line (~60) and the reshuffle respawn line (~146); no third line, no other hunk. Any drift = **BLOCKING** (B4).
2. **Pre-image verbatim:** the two deleted lines are EXACTLY the V-0 baseline strings — `    holder.position.set(x, 0, z);` and `    node.mesh.position.set(pick.x, 0, pick.z);` (any other line touched = the wrong line was edited = **BLOCKING**, B4).
3. **Seat semantics:** both added lines seat via the WH_GROUND guard of the IO §3.3 shape — `window.WH_GROUND && window.WH_GROUND.has(regionId) ? window.WH_GROUND.heightAt(regionId, x, z) : 0` at makeNode (regionId = the makeNode parameter), and the same treatment at reshuffle reading `node.regionId`. The `has()` guard is REQUIRED — without it the A/B flat-path nodes break (N-3: the change must be a no-op for regionA/regionB/hold_outskirts pools, which carry no heightfield). Missing guard or wrong regionId source = **BLOCKING** (B4).
4. **No logic drift:** marker bob untouched (CONFIG.gather.marker rows byte-identical — V-2's diff shows no gather.marker hunk), respawn timing, harvest, pools, and the makeNode signature untouched. Any change beyond the y-argument of the two position.set calls = **BLOCKING** (B4).
5. `node --check prototype/js/gather.js` exits 0 (B9). Baseline sha256 of gather.js pre-build is in V-0; the post-build file must differ from it in exactly these 2 lines.

## V-4 Syntax gate — node --check (IO A-5)

**Command.** Run in `/tmp/wh-worldfeat`:
```bash
for f in CONFIG.js gather.js game.js save.js region-manager.js region-defs.js assets.js; do node --check prototype/js/$f && echo "$f OK"; done
```

**Pass.** All seven print OK, exit 0. Any syntax error = **BLOCKING** (B9) — the v8 inliner happily bundles broken JS; a build pass is NOT a syntax pass. Baseline verified this wake: 7/7 OK pre-build. IO A-5 names CONFIG/gather/game; Testerbot sweeps all seven because the bundle eats them all.

## V-5 Asset and node-type legality (IO A-7)

**Commands.**
```bash
git diff --stat -- prototype/js/assets.js
grep -oE "asset: '[a-zA-Z]+'" prototype/js/CONFIG.js | sort -u   # after build: extract the new rows from the diff
git diff prototype/js/CONFIG.js | grep "^+" | grep -oE "asset: '[a-zA-Z]+'|type: '[a-zA-Z]+'"
```

**Pass thresholds.**
1. **assets.js diff EMPTY this round** — no new GLB rows, no pngs rows, no manifest edits. Any change = **BLOCKING** (B6).
2. Every new prop `asset:` ∈ { deadTree, mossBoulder, skullPile, buriedCoffin, rubblePile } — all five verified in the MANIFEST this wake (assets.js 32/64/72/21/99). Any other key = **BLOCKING** (B6).
3. Every new node `type:` = `bonePile` and bonePile exists in CONFIG.gather.nodeTypes (CONFIG 3356: boneShard ×2, respawnSec 150) — **no new nodeType, no new item, no new recipe, no new loot roll**. Any new key in nodeTypes/economy/items = **BLOCKING** (B6).

## V-6 Pack law and wolfPacks byte-purity (IO A-9, §3.4 NO-GO)

**Commands.**
```bash
sed -n '2159,2179p' prototype/js/CONFIG.js | sha256sum
git diff prototype/js/CONFIG.js | grep -n "wolfPacks\|waypoint\|packId"   # must print NOTHING
grep -c "'west'" prototype/js/CONFIG.js
grep -c "type: 'wolf'" prototype/js/CONFIG.js
```

**Pass thresholds (all required, BLOCKING on any failure).**
1. wolfPacks block sha256 = `2e2afb6097e39a166f58107231e3f74cfbdfe77f06e383a658db5b20a8dfd1bd` — byte-identical to the V-0 baseline, and the diff grep prints nothing: **no hunk touches wolfPacks, any waypoints, any packId row**. The L8 'west' loop keeps its exact 8 waypoints.
2. `'west'` census = **6** rows (580, 581, 582, 583, 780, 2163) — unchanged from V-0 (N-1/C5: the IO's "1 pack row" reading is the wolfPacks-block subset).
3. `type: 'wolf'` count still **28**; 7 wolfPacks rows; **zero new wolf rows, new packs, waypoint edits, behavior fields, or enemy-type rows** anywhere in the diff (B7).

## V-7 File-set law and save safety (IO A-8, §3.4 NO-GO list)

**Command.**
```bash
git status --short
git diff --stat
git diff prototype/js/save.js | wc -l
```

**Pass thresholds.**
1. The working diff (modified files) ⊆ { `prototype/js/CONFIG.js`, `prototype/js/gather.js`, `prototype/builds/v8-playable.html` } + untracked { `scratch/cc-wd1/*`, `io/reports/cc-wd1-build-note.md` }. Anything else = **BLOCKING** (B8/B10): save.js, game.js, enemy.js, region-manager.js, region-defs.js, assets.js, wh-ground.js, region-defs, scatterOverrides, terrain rows, roads — all EMPTY diffs, zero exceptions. NO-GO list (§3.4) is the normative enumeration; each entry checked.
2. `git diff prototype/js/save.js` = **empty** (baseline 0 diff lines, V-0): no new region → no save surface (A-8).
3. `git status --short` shows NO staged entries and NO new commits by Devbot (NO-GIT clause, B11).

## V-8 Clearance geometry table (RUNNABLE — the governing geometry law, A-6, G-1..G-7)

Devbot delivers `scratch/cc-wd1/clearance.py` (new file, untracked, NO-GIT), shaped on `scratch/cc-ec1/clearance.py` (regex rows out of the CONFIG regionC block, pure-math `math.hypot`, one printed line per check: label, value, minimum, ok/FAIL). Testerbot re-runs:
```bash
python3 scratch/cc-wd1/clearance.py
```

All distances measured from the verified hollow center **(−255, −410)** (site law center); the check set for G-1..G-5/G-7 is the UNION of all 12 new rows (8 props + 4 nodes — the IO §5 prose says "prop row"; Testerbot applies it to the union: strictly stronger, never weaker).

**Required checks (every row must print ok):**

| # | check | minimum | Testerbot baseline (2026-11-06, hollow-relative) |
|---|---|---|---|
| 1 | G-1: every new row → every one of the 28 wolf spawn rows (regionC.enemies) | ≥ 5.0 m | nearest pre-existing = west spawn 0 (−190,−420) at 65.8 m ⇒ worst-case new-row margin ≈ 53.8 ✓ |
| 2 | G-2: every new row → every west-pack waypoint (8, CONFIG 2165–2166) | ≥ 38.0 m | waypoint (−224,−388) → hollow = 38.0 m ⇒ worst-case ≈ 26.0 ✓ |
| 3 | G-3: every new row → every regionC fire (7 banditCampfire rows: 998, 1004, 1010, 1069–1072) | ≥ 20.0 m | nearest = Charlie (−140,−506) at 149.8 m ⇒ worst-case ≈ 137.8 ✓ |
| 4 | G-4: every new row → every C road SEGMENT (9 rows incl. westNotch bed; segment distance, not point) | ≥ 30.0 m | nearest = westNotch bed at 44.0 m ⇒ worst-case ≈ 32.0 ✓ |
| 5 | G-5a: every new prop row → all 221 pre-existing regionC props | ≥ 3.0 m | nearest pre-existing prop = witchwoodTree (−178.2,−424.2) at 78.1 m ✓ |
| 6 | G-5b: new row ↔ new row (cluster law, not a pile) | ≥ 2.5 m | pairwise, all 12 rows |
| 7 | G-6a: every node row → ALL props (new + old) | ≥ 5.0 m | hand law (N-1/C4: stricter than runtime propM 3) |
| 8 | G-6b: node row ↔ node row | ≥ 6.0 m | C band spacing |
| 9 | G-6c: every node row → hollow center | ≤ 12.0 m | site radius (3 larder cluster + 1 mouth approach) |
| 10 | G-7: every new row → C center (0, −366) | ≤ 262.0 m | hollow at 258.8; playable 278.5 − 16.5 margin. HARD — see N-2: SW-arc rim rows sit radially outward; any row > 262 = FAIL |

**Pass.** Exit 0, every row ok, and the IO §5 numbers (5.0 spawn, 38.0 west-waypoints, 20.0 fires, 30.0 roads, 3.0/2.5 props, 5.0/6.0/≤12 nodes, 262 site radius) appear verbatim in the script's threshold table. Devbot PASTES the full table into the build note; Testerbot re-runs and compares — margins within 0.05 m (float rounding). Any FAIL row, missing script, or exit ≠ 0 = **BLOCKING** (B5).

## V-9 Seat-law probe (RUNNABLE — G-8)

Devbot delivers `scratch/cc-wd1/seat_probe.js` (new file, untracked, NO-GIT) on the `scratch/cc-c5/loops_probe.js` pattern — `globalThis.window = globalThis`, `require` three.classic vendor, CONFIG.js, wh-ground.js (CORE THREE-free: no browser, no real THREE runtime):
```bash
node scratch/cc-wd1/seat_probe.js
```
The probe prints, per new row (8 props + 4 nodes), `WH_GROUND.heightAt('forest_of_the_old_king', x, z)` and the local slope via `WH_GROUND.slopeTan('forest_of_the_old_king', x, z)` (±0.5 m central differences = the 1 m span G-8 names; both APIs verified at wh-ground.js 294/320, exports at 373).

**Pass thresholds (every row).**
1. `WH_GROUND.has('forest_of_the_old_king')` true and every printed `|y| ≤ 26 m` (the heightfield hMax/rim-ridge ceiling convention; site sits on the C15 rim-mountain foot, so real heights here are non-trivial and must be printed, not asserted zero).
2. Slope over 1 m → `atan(slopeTan) ≤ 31 deg` (tan 31° = 0.6009) for every row — the C4b cliff-guard convention.
3. Exit 0; every row prints its numbers. Devbot pastes the probe output into the build note; Testerbot re-runs and compares (≤ 0.05 m / ≤ 0.5° rounding).

Any breach, missing probe, non-THREE-free harness (real THREE require beyond the vendored classic stub, puppeteer, browser), or exit ≠ 0 = **BLOCKING** (B5).

## V-10 Art law — concept-05 anchor (grep-assert)

**Command.**
```bash
git diff prototype/js/CONFIG.js | grep "^+" | grep -inE "lantern|campfire|startLit|light:|color|0xff|0xf[0-9a-f][0-9a-f]|ember|torch"
```

**Pass thresholds.**
1. **No matches in the new rows.** Den dressing = bone/bare-earth neutrals ONLY: the 5-key sanctioned kit (deadTree, mossBoulder, skullPile, buriedCoffin, rubblePile) adds no warm accent, no light source, no color/glow row beyond the pre-existing bonePile nodeType glowColor (CONFIG 3356, pre-existing — not this round's). The lantern amber belongs to the traveling player, never the den; the accent stays on the hunter. A second accent in the warm family, any `startLit`/`light:`/color row in the new block = **BLOCKING** (B6).
2. No new warm-accent ASSET row anywhere in the diff (lanternPost/banditCampfire-style keys cannot appear among the 8 new rows — V-5's key set already enforces; this is the belt to those braces).

## V-11 Build note and process law (IO §6 deliverables)

**Command (existence + pastes).**
```bash
ls scratch/cc-wd1/ && cat io/reports/cc-wd1-build-note.md
```

**Pass thresholds.**
1. `io/reports/cc-wd1-build-note.md` EXISTS and contains: exact `git diff --stat` pastes (CONFIG.js, gather.js), the bundle marker ledger (per-hit, ≥ 4 contributors), the FULL clearance table output (V-8), the seat-probe output (V-9), and any numbered ED-n deviations. Missing paste Testerbot cannot re-verify = **BLOCKING** (B11).
2. `scratch/cc-wd1/clearance.py` + `scratch/cc-wd1/seat_probe.js` both present and runnable (B5/B11).
3. NO harness runs, NO headless browser smoke tests by Devbot — node --check + grep + the two python/node probes only. Any puppeteer/browser artifact in the diff or note = **BLOCKING** (B11).
4. NO git commands by Devbot (NO-GIT): changes unstaged, zero commits, zero pushes (B11).

## V-12 Adjudication rubric (gate step 4 — Testerbot runs, in order)

1. `git status -sb` + `git diff --stat` → file set == V-7.1 allowed set.
2. V-2 CONFIG diff sweep → pure-add, 2 hunks, row/shape/banners.
3. V-3 gather.js diff → exactly 2 del + 2 add, verbatim pre-image, WH_GROUND guard.
4. V-4 node --check 7/7.
5. V-5 asset/type key sweep; V-6 sha256 + censuses; V-7 save.js + NO-GO.
6. V-8 `python3 scratch/cc-wd1/clearance.py` → every row ok, compared to Devbot's pasted table (≤ 0.05 m).
7. V-9 `node scratch/cc-wd1/seat_probe.js` → every row inside |y|/slope ceilings.
8. V-1 build + bundle marker ledger. V-10 art greps. V-11 note completeness.
9. Adjudicate every Devbot-recorded deviation against the tables below: expected-class → PASS with note; blocking → FAIL regardless of everything else green. **Zero-vs-list rule:** a blocking item Testerbot discovers UNRECORDED fails the round even if all checks green.

**PASS** = every check green AND zero blocking deviations AND all deviations accounted. **FAIL** = any blocking deviation or missing marker; the verdict lists check-by-check results + the remediation card for IO.

## Deviation classes + sanctions

**Expected-class deviations (Devbot MAY adopt; the build note records each as a numbered ED-n entry; Testerbot PASSES a recorded expected-class deviation).**

| class | deviation | verification hook |
|---|---|---|
| ED-1 | prop/node positions differ from any illustrative IO §3.1/§3.2 range wording, provided every V-8 minimum and the G-6c ≤ 12 m site radius clear (the prose is placement guidance; the clearance table is law) | V-8 |
| ED-2 | bundle marker count in the 6–8 band with distribution skew, provided the ≥ 4-contributor ledger holds and no row carries > 3 hits | V-1 |
| ED-3 | the regionC `nodes:` key inserted at a different key boundary inside regionC than directly after the props close, provided the pure-add law holds and all pre-existing lines stay byte-identical | V-2.2 |
| ED-4 | clearance/seat margins differ from Testerbot's reference table by ≤ 0.05 m (or ≤ 0.5° slope) float rounding, all minimums still exceeded | V-8 / V-9 |
| ED-5 | blank-line/comment drift at the insertion edges (the props-tail CC-C17 comment context shifts with the append); append-only law intact | V-2.1 |
| ED-6 | seat expression shape variance within the IO §3.3 sanctioned form — e.g. a hoisted `var G = window.WH_GROUND;` local vs the inline ternary — provided EXACTLY 2 changed lines hold and the `has()`-guard semantics are preserved at both call sites | V-3 |
| ED-7 | MORE than the minimum row comments carry `west_hollow_den` (count > 6), provided ≥ 4 distinct contributors and the ≤ 3-hits-per-row anti-bloat law hold | V-1 |
| ED-8 | the clearance script prints the Testerbot 7-fire census (V-0) where the IO §2 prose cites 4 fires — the STRICTER set governs and is what V-8 row 3 checks | V-8 |

**Blocking classes (any one → round FAILED; Testerbot issues the remediation card; re-gate required).**

| class | violation | verified by |
|---|---|---|
| B1 | **byte-purity:** any `−` line (excluding headers) in the CONFIG.js diff; any pre-existing line rewritten or moved (props 810–1144, coven tail, enemies, terrain, roads, wolfPacks all byte-sacred) | V-2.1 |
| B2 | **bloat-row:** marker ≥ 6 but < 4 distinct contributors, or any single source row carrying > 3 hits — a padded pass is a failed pass | V-1 |
| B3 | placement/shape: new rows anywhere but the props tail + the new regionC nodes key; a `y:` key on a new prop row; row-shape drift off `{ asset, x, z, rotY, scale }` / `{ type: 'bonePile', x, z }`; prop/node COUNT off the 8 + 4 set; a third insertion surface | V-2 |
| B4 | gather.js: any hunk beyond the 2 seat lines (3rd changed line = instant fail); missing/failed `has()` guard; wrong regionId source; marker bob / respawn timing / signature drift | V-3 |
| B5 | geometry: any V-8 row below its minimum, any new row > 262 m from C center, any seat row > 26 m or slope > 31°, clearance.py / seat_probe.js missing or unrunnable, margin mismatch > 0.05 m | V-8 / V-9 |
| B6 | art/type law: asset outside the 5-key neutral kit; ANY assets.js diff; a new nodeType/item/recipe/loot roll; a warm-accent or light/color row in the new block | V-5 / V-10 |
| B7 | pack law: any wolfPacks hunk or sha drift; waypoint byte drift; 'west' census ≠ 6; wolf count ≠ 28; any new pack/row/behavior field | V-6 |
| B8 | save/no-go: save.js diff non-empty; any of game.js / enemy.js / region-manager.js / region-defs.js / wh-ground.js modified; roads/scatter/terrain hunks | V-7 |
| B9 | syntax: any of the seven files failing `node --check` | V-4 |
| B10 | file-set law: any modified file outside { CONFIG.js, gather.js, prototype/builds/v8-playable.html } + untracked { scratch/cc-wd1/*, io/reports/cc-wd1-build-note.md } | V-7 |
| B11 | process: ANY git commit/push by Devbot (NO-GIT), a headless-browser/harness artifact, or the build note missing its required pastes (diff stats, marker ledger, clearance table, seat-probe output) | V-11 |
| B12 | build: `tools/build_v8.py` exit ≠ 0, or post-rebuild bundle marker < 6 | V-1 |

## Notes (Testerbot census corrections + build guidance)

**N-1 (census corrections vs the IO spec — Testerbot-verified 2026-11-06; Devbot builds to THESE).**
- C1: regionC carries **7** banditCampfire prop rows, not 4. IO §2's "all 4 C fires: min 161.3 m" is the CC-C16b camp-fire subset and holds exactly (camp 1 (−106.1,−472.1) = 161.3 m); G-3 checks all 7 (nearest overall: Charlie (−140,−506) at 149.8 m — no margin threatened).
- C2: IO §2's "nearest existing prop: 65.8 m (wolf spawn row)" conflates prop and enemy: 65.8 m is the nearest ENEMY row (west wolf spawn 0); the nearest pre-existing PROP is witchwoodTree (−178.2,−424.2) = 78.1 m. G-5 threshold unchanged.
- C3: regionC has **no nodes:** key today — the 4-row nodes array is a NEW key (only regionA/B have nodes arrays at CONFIG 345/449). "Additions" in IO §3.2 means create-the-key, not append-into-existing.
- C4: `CONFIG.gather.placement.propM` = **3** (the runtime auto-placer's bound); the round's HAND rows obey IO's stricter ≥ 5.0 law — V-8 row 7 checks 5.0. spacingM keys today = { hold_outskirts: 9, darkwood_edge: 6 }; no regionC key; the ≥ 6.0 node-to-node hand law governs (G-6).
- C5: A-9's "'west' … 1 pack row" is the wolfPacks-block subset of a 6-row `'west'` census (4 spawn rows 580–583, westNotch rim 780, pack row 2163). V-6 pins the full census; any drift in ANY of the 6 = B7.

**N-2 (G-7 radius tension — build guidance, hard cap).** The hollow sits at 258.8 m from C center; the SW rim-boulder arc points radially OUTWARD — a row merely ~3.2 m outward-radial breaches 262. Devbot must bias SW rim rows tangentially or slightly inward; V-8 row 10 is HARD (B5), no expected-class exemption exists for it.

**N-3 (seat no-op law).** WH_GROUND.has() is false for regionA/regionB (no terrain rows) and for any node pool outside heightfield regions; the guard reduces to 0 there, so the 2-line change must be behaviorally invisible outside C. The Region-B bonePile rows (CONFIG 455–458) ride the same makeNode path — V-3's guard requirement protects them.

**N-4 (marker material).** CONFIG comments survive build_v8 byte-identical (V-0: 'den-local z −24.6' and 'CC-C17 ring fragment' both grep in the served bundle) — banner + row comments are the sanctioned marker carriers; no code-token marker is needed or wanted.

## Post-verdict law — IO close-out (IO §7; not a Devbot surface)

Testerbot **PASS** → IO commits (identity CaptainPickard <pickard.nicko@gmail.com>) and pushes `feat/world-visuals` via the HTTPS credential route; build verified; release flip; journal + GOALS tick. Testerbot **FAIL** → ED loop or IO inline-landing per the 2-death law, disclosed in the round note.

Post-gate slice — serve-flip verification (after IO's commit + flip; curl-only, no browser):
```bash
curl -s -o /dev/null -w '%{http_code}\n' http://172.16.5.1:8793/current/prototype/builds/v8-playable.html
curl -s http://172.16.5.1:8793/current/prototype/builds/v8-playable.html | grep -c west_hollow_den
```
**Pass.** HTTP 200 AND served-bytes `west_hollow_den` count ≥ 6 — SERVED bytes, never the repo copy. Testerbot hands these two steps to IO in the verdict text (Testerbot does not own the flip). A 200-with-0-count means the flip is stale: IO re-runs the flip and re-verifies. Nicko's playtest remains the final acceptance bar — this valspec NEVER substitutes for it.
