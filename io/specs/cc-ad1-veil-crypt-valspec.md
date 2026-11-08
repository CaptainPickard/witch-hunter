# CC-AD1 VALSPEC — Veil Spire Crypt Mini-Delve (independent Testerbot validation spec)

Round: CC-AD1 · 2026-11-06 · Author: Testerbot (gate step 2 — written BEFORE Devbot builds)
Source of truth: `io/specs/cc-ad1-veil-crypt-spec.md` (section 6 acceptance criteria, verbatim anchors)
Round contract: IO spec → Testerbot valspec → Devbot build → Testerbot validation → IO commit
Style parent: `io/specs/cc-ec1-coven-acolyte-valspec.md` (V-anchors, deviation classes, sanctions)
Build note (style reference, behavior contract for the coven): `io/reports/cc-ec1-build-note.md`

## V-0 Ground state (Testerbot's own census, taken 2026-11-06 before any build; Devbot must keep true)

- Baseline `grep -c veil_crypt prototype/builds/v8-playable.html` = **0** (the marker is NEW in this round — any count ≥ 1 is this round's work, and the bundle exists, ~3.3 MB).
- **CONFIG.js comments ARE preserved in the served bundle** (verified: the CC-C16a planeZ comment and "den-local z -24.6" both grep inside the current bundle) — so per-row comments like `// crypt-local (0, -8) landing` are valid marker material, not stripped by build_v8.
- `grep -rn "CFG.regionD" prototype/js/game.js` = **3 baseline reads** (lines 1907 tryDenDoor, 2219 E-prompt, 3071 exitFade read). After the genericization, at most one such read may remain — inside the ternary/conn resolution in tryDenDoor (V-10), and only where the IO spec's own snippet still names regionD.
- `grep -rn "regionE" prototype/js/ | wc -l` = **0** today; the new-marker census stays meaningful.
- Files and line anchors (today's HEAD 264c703, branch `feat/world-visuals`): CONFIG.js 3481 lines; region-defs.js 224 (makeRegion at 17, regionD registration at 46, connections[2] push at ~96–110, `connectionBetween` at 117); region-manager.js 2140 (logic.forceCross 144, buildRegion 1747, manager.forceCross 2047); game.js 3197 (denDoorNear 1899, tryDenDoor 1903/1907, denFade family 1918–1951, E-prompt chain else-if at 2218–2219, tickTransition cross block 3068–3073 with exitFade read at 3071); save.js 301 (`validRegion` at 39, restore's region gates at 253/264/273; exports WH_SAVE = {capture, restore, save, load, has}).
- All five syntax-checkable files pass `node --check` at baseline (V-12).
- `scratch/cc-ad1/` does not exist yet — Devbot creates it (Testerbot's V-14 runs after).
- The build tool is `python3 tools/build_v8.py` — run IN the worktree, never via absolute path out of it; the served bundle is what gets greped, never the repo copy.

## V-1 Build and marker count (IO §6.1)

**Command.** Run in `/tmp/wh-worldfeat`:
```bash
python3 tools/build_v8.py && echo "BUILD_EXIT=$?"
```
`$?` must be 0 and the tool must complete without a Python traceback. The build is run in the worktree, not the repo copy (IO §7: children work only in the worktree).

**Command (marker).**
```bash
grep -c veil_crypt prototype/builds/v8-playable.html
```

**Pass threshold.** Count **≥ 8** and the build exited 0. **BLOCKING** if below.

**Where the count must come from (additionality, not a single bloat row).** With CONFIG comments preserved in the bundle (V-0), the expected contributors are: regionE block header (`id: 'veil_crypt'`), name string, the region-defs makeRegion line, connections[3] from/to keys, land key `veil_crypt: { x: 0, z: -604 ... }`, both coven enemy rows' comments, props sub-comments, and the constantPhase row IF Devbot appends one (IO §5 allows the append, flags it in the build note). A single 8-hit comment row technically clears the byte count but fails this sub-check: the ledger must identify ≥ 5 distinct source contributors; each must map to a real build surface. A bloat-row pass is **BLOCKING-LEVEL-2** (see V-16 class B2).

**Ledger.** Testerbot keeps a per-hit ledger (`grep -n veil_crypt prototype/builds ≥ 8` lines with their source attribution); the validation report reproduces it.

## V-2 CONFIG.js additionality (IO §6.2)

**Command.**
```bash
git diff prototype/js/CONFIG.js
```
(testerbot runs it against HEAD; Devbot leaves the change unstaged per the NO-GIT clause.)

**Pass thresholds (all required, BLOCKING on any failure).**
1. **Pure-add diff:** zero `-` lines excluding the `+++`/`---` header lines; zero `/^changed|modified/` claims needed — the diff shows only `+` lines. (EC1 precedent: the 50 added rows were verified by "append-only row purity" — same shape here at whole-file scope.)
2. **Block placement:** `grep -n "  regionE: {" prototype/js/CONFIG.js` — the block opens AFTER the regionD block's close brace (line ~1348 today) and BEFORE the `// Round E (io/missions/2026-10-05-cc-roundE-veg.md)` scatter comment at ~1349. No line inside the pre-existing regionD row moved or was rewritten: `git diff | grep "^-[^-]"` empty AND the block's own diff hunk spans only the insertion point.
3. **Enemy rows:** `grep -n "type: 'coven'" prototype/js/CONFIG.js` — regionE's enemy rows carry `type: 'coven'`, position values matching the spec's crypt-local (5, 4) and (-6, 6) → world (5, −592) / (−6, −590) (the z math: crypt-local z = world z + 596; IO spec's illustration z −594 is internally inconsistent — see V-15 note N-2; the clearance table uses crypt-local coordinates, V-14 governs).
4. **Key-set shape:** every regionE key (id, name, center, groundRadius, groundY, groundColor, groundColor2, groundSeed, scatter, spawn, gravityY, fogColor, fogDensity, ambientLightLevel, door, enemies, props) mirrors the regionD key set with new values. A missing key = **BLOCKING**; `veil_crypt` id string appears in-region.
5. **Door sub-row shape:** planeZ (crypt-local −16 → world −612), doorX 0, doorHalfWidth 2.4, suspendDepthM 0, wallGapPadM 0, interactM 3.5, interactAt {0, −596} (world); land rows: `land.forest_of_the_old_king { x: 0, z: -596, faceX: 0, faceZ: -366 }`, `land.veil_crypt { x: 0, z: -604, faceX: 0, faceZ: -604 }`; fadeIn 0.3, fadeOut 0.5, exitFadeOut 0.8, and text: { prompt: 'E - Descend into the crypt' } — the fade triple mirrors regionD.door rows 1271–1274 (fadeIn 0.3 / fadeOut 0.5 / exitFadeOut 0.8 / text 'E - Enter the den'), new prompt string per IO §2 (exact-string law → V-8).
6. **Wall/prop row shape:** ring rows carry the SAME per-row shape as regionD's whWall rows (asset, x, z, rotY, scale, sy, sz, y: -0.2, wall: 8 — CONFIG 1295–1304 is the model), 8 segments at r ~17–18; prop rows carry `asset:` from the verified manifest only (V-11) plus x/z/rotY/scale. The ring's only collider-free arc is the door window at crypt-local (0, −16) — asserted executable in V-14 row 8.

## V-3 region-defs.js registration + connections[3] additionality (IO §6.3)

**Command.**
```bash
git diff prototype/js/region-defs.js
```

**Pass thresholds (all required, BLOCKING on any failure).**
1. **Pure-add diff:** only `+` lines; the sanctioned additions are exactly three, in order:
   - (a) `regions[CFG.regionE.id] = makeRegion(CFG.regionE, -1);` appended directly after the regionD registration (line 46 baseline; the -1 side argument is the plane-0 convention only — connections[3].sides carries the truth, per the CC-C8 comment block above the registration);
   - (b) a `var DD2 = CFG.regionE.door;` alias + one `connections.push({ ... })` block appended after the connections[2] sides lines (111–112), shaped EXACTLY on connections[2]: `from: CFG.regionC.id, to: CFG.regionE.id, axis: 'z', planeCoord: DD2.planeZ, sides: {}`, and `door: { doorX: DD2.doorX, doorHalfWidth: DD2.doorHalfWidth, suspendDepthM: DD2.suspendDepthM, wallGapPadM: DD2.wallGapPadM, arch: null, gatedTo: null, walkFrom: CFG.regionE.id, interact: { from: CFG.regionC.id, x: DD2.interactAt.x, z: DD2.interactAt.z, radius: DD2.interactM }, land: DD2.land }`;
   - (c) exactly two sides lines after the push: `connections[3].sides[CFG.regionC.id] = -1;` and `connections[3].sides[CFG.regionE.id] = 1;` (the sides TABLE governs — IO §3's "regionE occupies z <= planeZ" prose is contradicted by the spec's own land rows; see V-7 and N-3).
2. **Door-key law:** `arch: null` and `gatedTo: null` present as EXPLICIT keys on the connections[3] door row (mirroring connections[2], C0 law). Absent or non-null = **BLOCKING** — the wall-gap arithmetic reads `conn.door.arch` and the dormant-clock gate lookup reads `conn.door.gatedTo` off the row (N-3).
3. **walkFrom semantics:** `walkFrom: CFG.regionE.id` — the plane exists ONLY for the crypt side (the walk-back-out); while in regionC no plane crossing fires anywhere along planeZ −612. Verified executable in V-6/V-7.
4. **Helpers untouched:** connectionBetween (117), planeIn, sideIn, insideDoorWindow, mapPositionAcross, sideOfPlane, neighborOf, and the `window.WH_REGION_DEFS` export block keep their exact line ranges; zero `−` lines touching them. `WH_REGION_DEFS.connections.length` must become 4 (V-6 asserts).
5. **No other region-defs edit.** Any hunk beyond (a)+(b)+(c) = **BLOCKING**.

## V-4 game.js genericization — the three reads (IO §6.4)

**Command.**
```bash
git diff prototype/js/game.js
```

The three regionD-keyed reads (baseline 1907 / 2219 / 3071, V-0) become per-conn reads. Pass shape — one substitution hunk each, surrounding context byte-identical:

1. **tryDenDoor (~1907):** `var D = CFG.regionD.door;` → conn-based: the function already holds `var conn = denDoorNear();` (1905) — `var D = conn.door;` (or the IO-spec variant `var D = conn && conn.door;`). Every `D.*` use in the block is unchanged: `startDenFade(D.fadeIn, D.fadeOut, function () { applyCross(game.regionManager.forceCross(conn)); })` keeps its exact shape.
2. **E-prompt (~2219):** `text = CFG.regionD.door.text.prompt;` → `text = conn.door.text.prompt;` (denDoorNear() captured first, per IO §4.2). The chain SLOT is untouched: the den/crypt doorway keeps its exact priority position between cook/camp and lockedDoor/notch/npc — chain REORDER = **BLOCKING** (V-8.3).
3. **exitFade (~3071):** `startDenFade(0, CFG.regionD.door.exitFadeOut, null)` → `startDenFade(0, tr.conn.door.exitFadeOut, null)`; the guard line above (`tr.conn && tr.conn.door && tr.conn.door.land && !game.denFade`) stays byte-identical — it already proves tr.conn non-null (the reuse IO §4.3 mandates).

**Hunk census.** Exactly 3 substitution hunks (or 2 if the E-prompt and tryDenDoor hunks merge mechanically); NO other game.js edit. IO §4's never-silently-default law: if any of the three reads hits a CONFIG row not carrying the needed key, Devbot fails the build and reports — never silently defaults. Syntax gate: V-12. Post-build regionD residual census: V-10.

## V-5 veil_crypt / regionE census (V-1 cross-check — additionality, not bloat)

**Command.**
```bash
grep -rc veil_crypt prototype/js/CONFIG.js prototype/js/region-defs.js prototype/js/game.js
grep -rln "regionE\|veil_crypt" prototype/js/
```

**Pass thresholds.**
1. **Per-file floors:** CONFIG.js ≥ 5 (id, door text prompt, land key veil_crypt, both coven rows, props comments); region-defs.js ≥ 2 (makeRegion/conn block); game.js ≥ 0 (the genericized reads need not contain the string — the prompt text lives in CONFIG). The three-file sum must be ≥ 8 to corroborate V-1's bundle count with real sources.
2. **Leak law:** zero `regionE`/`veil_crypt` occurrences in save.js, player.js, region-manager.js, light.js, enemy.js, spells.js, assets.js, camp.js, npc.js, touch-controls.js, icons-data.js. Any hit outside CONFIG.js / region-defs.js / game.js = **BLOCKING** (surfaces beyond the three sanctioned files).
3. **Anti-bloat:** no single source row carries more than 3 of its file's hits — a padded comment row inflating the count is the B2 signature (**BLOCKING-LEVEL-2**, same class V-1 cites).

## V-6 connections[3] probe — THREE-free node smoke (IO §6.3)

**Command.** Devbot delivers `scratch/cc-ad1/connection_probe.js` (new file, untracked, NO-GIT). Testerbot runs it in `/tmp/wh-worldfeat`:
```bash
node scratch/cc-ad1/connection_probe.js
```

**Harness shape (verified live 2026-11-06):** stub `global.window = {}` + a localStorage no-op, then eval `prototype/js/CONFIG.js` → `prototype/js/region-defs.js`. region-defs evaluates THREE-free at module scope; pre-build it exposes the 4 baseline regions and `connections.length = 3`.

**Required assertions (ALL print PASS; exit 0):**
1. `WH_REGION_DEFS.connections.length === 4`; `conn = WH_REGION_DEFS.connections[3]` exists.
2. `conn.from === CFG.regionC.id` and `conn.to === 'veil_crypt'` (CFG.regionE.id).
3. `WH_REGION_DEFS.connectionBetween('forest_of_the_old_king', 'veil_crypt')` resolves to that conn (IO §6.3 verbatim).
4. `conn.door.arch === null && conn.door.gatedTo === null` (door-key law, N-3).
5. `conn.sides[CFG.regionC.id] === -1 && conn.sides[CFG.regionE.id] === 1`.
6. Door window at planeCoord −612, doorX 0, doorHalfWidth 2.4: `insideDoorWindow(conn, 0)` true; `insideDoorWindow(conn, 2.5)` and `insideDoorWindow(conn, -3.5)` false.
7. `WH_REGION_DEFS.regions['veil_crypt']` registered; `.spawn` equals the IO §2 row; `.groundRadius === 20`; `.center` = { x: 0, z: -596 }.
8. RegionManagerLogic forceCross from the C side lands `newActiveId === 'veil_crypt'` with mappedPos overridden by the land row (0, −604) — and from the land row, no re-cross (V-7's executable proof).

Any assertion failure = **BLOCKING**.

## V-7 crossing semantics (code-read + probe)

- **E-to-enter = interact-radius cross:** forceCross via `rm.forceCross(conn)` inside the startDenFade peak callback (game.js 1903–1916 law unchanged); the black-dip mechanic, no-pause/no-menu law, and death-mid-dip-cancels (denFadeTick 1943–1946) are UNTOUCHED — hunks exist only at the three V-4 sites.
- **Walk-back-out = plane crossing at the crypt mouth:** tickTransition (region-manager 44; game.js 3068–3073) fires only when `sideOfPlane(pos) !== conn.sides[activeId]`.
- **No re-cross at the land row:** the crypt land row (0, −604) sits at world z −604 > planeZ −612, i.e. the +1 side — matching `connections[3].sides['veil_crypt'] = 1`. Landing does NOT re-cross; V-6.8 asserts it executable. If Devbot writes sides[regionE] = −1 (the IO §3 prose misreading), the land row re-crosses INSTANTLY — a teleport loop = **BLOCKING**.
- **Plane exists only walkFrom the crypt:** V-6's probe also asserts a C-side position far outside the door window (x ±10, beyond halfWidth 2.4) crosses NOTHING on planeZ −612, and inside the window on the C side the ENTER path is the interact radius, not the plane — three position cases total.
- **The ring is CLOSED except the door gap:** geometric duty of V-14 (row 8); here the code-read confirms the door window is the only walkable mouth (suspendDepthM 0, wallGapPadM 0).

## V-8 E-prompt and door-text law (IO §6.4 prompt half)

**Commands.**
```bash
grep -n "Descend into the crypt" prototype/js/CONFIG.js
grep -n "conn.door.text.prompt" prototype/js/game.js
git diff prototype/js/game.js
```

**Pass thresholds.**
1. The regionE door row carries `text: { prompt: 'E - Descend into the crypt' }` — EXACT string (IO §2/§5), exactly once in CONFIG.js. Misspelled/absent = **BLOCKING**.
2. The 2219 slot reads `conn.door.text.prompt` (per-conn) — one slot now serves both doors by whichever conn is near; regionD's `'E - Enter the den'` (CONFIG 1274) still resolves the same way with ZERO edit to its row (`grep -c "Enter the den" prototype/js/CONFIG.js` stays 1).
3. Chain ORDER unchanged (CC-C11 priority): cook → camp → den/crypt doorway → lockedDoor → notch → npc, byte-identical around the slot (else-if neighbors untouched).

## V-9 denFade family law (in/out symmetric dip)

- **In:** `startDenFade(D.fadeIn, D.fadeOut, cb)` = (0.3, 0.5) read off regionE.door via the conn; **walk-out:** `startDenFade(0, tr.conn.door.exitFadeOut, null)` = (0, 0.8). Same #wh-death-overlay element, same opacity 0→1→0 mechanic, same onPeak cross.
- **No hardcoded fade constants** introduced in game.js hunks (no stray 0.8/0.5 literals where a conn read belongs) — grep the three hunks.
- The 3070 guard prefix `tr.conn && tr.conn.door && tr.conn.door.land && !game.denFade` is byte-identical (V-4.3).
- startDenFade's inline-style ownership swap, denFadeTick's death-cancel, and endDenFade's restore (1918–1951) carry NO diff hunks.

## V-10 CFG.regionD residual census in game.js (V-0's law, executable)

**Command.**
```bash
grep -n "CFG.regionD" prototype/js/game.js
```

**Pass law.** Baseline 3 (1907/2219/3071) → post-build EITHER 0 (all three fully genericized) OR exactly 1 — a single `CFG.regionD.id`-style read inside tryDenDoor's region-resolution ternary of the IO-spec shape (`activeId === CFG.regionD.id ? ... : CFG.regionE.id`), and ONLY there (the one spot where the IO spec's own §4 snippet still names regionD). Two or more residuals, or a residual anywhere but tryDenDoor = **BLOCKING**. A remaining ternary read is sanctioned-but-noted: Devbot records it in the build note (V-16 expected-class) — never silent.

## V-11 art law (grep-assert)

**Commands.**
```bash
git diff --stat -- prototype/js/assets.js
grep -n "asset: '" prototype/js/CONFIG.js
```

**Pass thresholds.**
1. **assets.js diff EMPTY this round** — no new GLB rows, no pngs rows, no CHARACTERS additions. Any change = **BLOCKING**.
2. Every regionE prop `asset:` is one of the 8 verified manifest keys: whWallA, whWallB, mossBoulder, blightcap, stoneSteps, skullPile, stoneSarcophagus, rubblePile (assets.js 58/59/64/70/71/72/74/99). Any other key = **BLOCKING**.
3. **Palette law:** groundColor/groundColor2 in the basalt-charcoal family (IO §2: 0x121418 / 0x171a20), fogColor the bruised-purple near-black (0x0a0810), ambientLightLevel present; NO new red/orange accent beyond the altar-side ember language (the blightcap pair's faint red caps + the altar stones; asset-only v1, no light code — IO §5). `grep -nE "0xff|0xf[0-9a-f][0-9a-f]"` over the regionE block = no red/orange hex rows.
4. `fogDensity` present (~0.13, PROPOSED); `groundRadius: 20`; `scatter: false`; `gravityY: -22`.

## V-12 syntax gate — node --check, 5/5

**Command (run in `/tmp/wh-worldfeat`).**
```bash
for f in game.js CONFIG.js region-defs.js region-manager.js assets.js; do node --check prototype/js/$f && echo "$f OK"; done
```

**Pass.** All five print OK, exit 0. Any syntax error = **BLOCKING** — the v8 inliner happily bundles broken JS; a build pass is NOT a syntax pass. Baseline verified 2026-11-06: all five pass pre-build. save.js is outside this gate by the file-set law (the round only READS it; V-16/B10 pins the touched-file set).

## V-13 save round-trip logic test (THREE-free, no browser — IO §6.6)

Devbot delivers `scratch/cc-ad1/save_roundtrip.js` (new file, untracked, NO-GIT). Testerbot runs:
```bash
node scratch/cc-ad1/save_roundtrip.js
grep -cn "require('three')\|THREE\.\|puppeteer\|playwright\|browser" scratch/cc-ad1/save_roundtrip.js
```
(second command must print 0).

**Harness shape (verified live 2026-11-06: CONFIG → region-defs → save.js evaluates THREE-free under stubs; WH_SAVE exports {capture, restore, save, load, has}; validRegion at save.js:39 is the region gate).** Stubs: `global.window = {}`; `global.localStorage` {getItem/setItem/removeItem no-ops}; `global.WH_LEVEL` {capture/restore/discover no-ops}; then eval CONFIG.js → region-defs.js → save.js. The game stub must carry the FULL save.js surface — player {hp, focus, stamina, pos, yaw, state, regionId, hands, belt, bindings, consumables, respawnAt, yawFrame, cast, isCasterHand}, inventory {slots}, cooking {buffs with clear()/list()/add() methods — capture reads ck.buffs.list(); a plain-object or plain-array stub throws, verified}, recipes, kitAcquired, mealDay; camp {sites, respawn, place, packUp, siteSeq}, dayNight {day, phase, timeOfDay}, regionManager {logic.activeId}, classId.

**Required assertions (ALL print PASS; exit 0):**
1. `validRegion('veil_crypt') === true` post-build (the save.js:39 lookup through WH_REGION_DEFS.regions).
2. **Negative control:** `validRegion('veil_crypt_gone') === false`.
3. capture(game with regionManager.logic.activeId = 'veil_crypt') → `JSON.stringify` → parse → restore onto a fresh stubbed game: the teleport path lands player pos on the saved crypt row (0, −604 world) and rid resolves 'veil_crypt' (save.js 273 path).
4. A profile with regionId 'veil_crypt_gone' restores WITHOUT throw, falling back to `game.regionManager.logic.activeId` — asserted EQUAL to the stub's activeId.
5. The three gates fire: camp.sites rows with regionId 'veil_crypt' restore (253); camp.respawn with regionId 'veil_crypt' restores (264); player.regionId 'veil_crypt' restores (273).
6. No THREE require, no browser/puppeteer import, no DOM beyond the stubs.

Any assertion failure or exit ≠ 0 = **BLOCKING**.

## V-14 clearance geometry table (RUNNABLE — the governing geometry law, crypt-local)

Devbot delivers `scratch/cc-ad1/clearance.py` (new file, untracked, NO-GIT), shaped on `scratch/cc-ec1/clearance.py` (regex rows out of the CONFIG regionE block, pure-math `math.hypot` distances, one printed line per check: label, value, minimum, ok/FAIL). Testerbot re-runs:
```bash
python3 scratch/cc-ad1/clearance.py
```

All coordinates CRYPT-LOCAL relative to center (0, −596) — crypt-local (x, z) = world − (0, −596) (the governing convention: V-2 row 3, N-2). Reference points (IO §2): spawn/land veil_crypt (0, −8) [world (0, −604)]; coven 1 (5, 4); coven 2 (−6, 6); altar feature (0, 6); door window center (0, −16); wall ring r ~17–18, 8 segments, sy ~9, sz 2.4, colliders ≤ every 2 m — inner walking edge ≈ 16 m from center.

**Required checks (every row must print ok):**

| # | check | minimum | Testerbot reference (2026-11-06) |
|---|---|---|---|
| 1 | spawn/land rows inside r 20 of center | ≤ 20 | ρ = 8.0 ✓ |
| 2 | coven 1 → spawn/land | ≥ 8.0 m | 13.00 ✓ |
| 3 | coven 2 → spawn/land | ≥ 8.0 m | 15.23 ✓ |
| 4 | coven 1 ↔ coven 2 (independent casters, no stacking) | ≥ 8.0 m | 11.18 ✓ |
| 5 | each coven → every wall collider | ≥ 4.0 m | (16 − ρ) interior law: coven 1 ρ 6.40 → 9.60 ✓; coven 2 ρ 8.49 → 7.51 ✓ |
| 6 | each prop → every wall collider | ≥ 4.0 m | same law per prop row |
| 7 | each prop → spawn/land | ≥ 6.0 m | altar (0, 6) → (0, −8) = 14.0 ✓ |
| 8 | each prop → each coven | ≥ 5.0 m | altar → coven 1 = 5.39, → coven 2 = 6.00 ✓ |
| 9 | **wall ring CLOSED except the door gap**: the script reconstructs the ring from the regionE whWall rows' (x, z, wall) colliders and asserts the only collider-free arc at the ring radius is the door window at crypt-local (0, −16) ± 2.4 m (arc gap ≈ 8.10° at r 17 / 7.65° at r 18); every other angular sector covered | binary | ✓ shape law |
| 10 | `validRegion('veil_crypt') === true` re-derived from the built registers (cross-check of V-13.1) | binary | ✓ |

**Pass.** Exit 0, every row ok, and the four IO §6 numbers (8.0 spawn/each-other, 4.0 walls, 6.0 spawn, 5.0 covens) appear verbatim in the script's threshold table. Devbot PASTES the full table into the build note; Testerbot re-runs and compares — margins within 0.05 m (float rounding). Any FAIL row, unlocked ring, or exit ≠ 0 = **BLOCKING**.

## V-15 notes / deviation register

**N-1 (preserve law).** Rows 1–50 of this valspec and V-2's threshold rows 1–4 are the first Testerbot draft, preserved byte-identical: the first attempt was killed by a transport timeout mid-write, leaving the dangling fragment `fadeOut 0.JS` at the file's end (a wrapped `fadeOut 0.5,` whose tail was lost). This completion strips the fragment and completes the sentence (`fadeOut 0.5, exitFadeOut 0.8, …`), then APPENDS from V-2 row 6 onward — nothing above the fragment was rewritten, reflowed, or renumbered. Any future edit to the preserved bytes invalidates the valspec and re-opens the round. A separate full-rewrite recovery file surfaced at io/reports/2026-11-06-cc-ad1-valspec.md during the outage window; this file (copied over that path at completion) is the authoritative version.

**N-2 (IO-spec world-z slip).** IO §2's enemy illustration `(−6, −594)` contradicts the spec's own conversion law (crypt-local z = world z + 596, so crypt-local (−6, 6) → world z 6 − 596 = **−590**). Normative: the crypt-local table — (5, 4) and (−6, 6) → world (5, −592) / (−6, −590). Center-relative geometry makes the two readings differ only in coven 2's spawn distance (15.23 vs 11.66 — BOTH clear the 8.0 floor), so the slip never breaks a real constraint; clearance.py reads crypt-local rows (V-14 governs, per V-2 row 3). A world row written at −594 is the expected-class deviation (V-16 ED-1), never silent.

**N-3 (door-key law).** connections[3]'s door row must EXPLICITLY carry `arch: null` and `gatedTo: null` — shape proven on connections[2]: the wall-gap arithmetic reads `conn.door.arch` and the dormant-clock gate lookup reads `conn.door.gatedTo` off the row. Omitting the keys silently changes that math (BLOCKING per V-3.2).

**N-4 (bundle comment survival).** CONFIG.js comments survive build_v8 (verified: the CC-C16a planeZ comment and "den-local z -24.6" grep inside the current bundle) — per-row comments like `// crypt-local (0, -8) landing` are legitimate V-1 ledger material.

**N-5 (bases at writing).** HEAD 264c703, branch feat/world-visuals; bundle marker count 0; CFG.regionD reads in game.js = 3 (1907/2219/3071); regionE/veil_crypt anywhere in prototype/js = 0; node --check 5/5 OK (game.js, CONFIG.js, region-defs.js, region-manager.js, assets.js); the THREE-free harness proof for V-6/V-13 executed live on 2026-11-06.

## V-16 deviation classes + sanctions

**Expected-class deviations (Devbot MAY adopt; the build note records each as a numbered ED-n entry; Testerbot PASSES a recorded expected-class deviation).**

| class | deviation | verification hook |
|---|---|---|
| ED-1 | coven-2 world row written (−6, −594) per the IO §2 illustration slip instead of (−6, −590); crypt-local rows correct and all clearance minimums still clear (11.66 ≥ 8.0) | V-2.3 + N-2 |
| ED-2 | marker count in the 8–11 advisory band with per-file distribution skew, provided the ≥ 5-contributor ledger holds | V-1 / V-5 |
| ED-3 | genericization shape variance within the IO-§4-sanctioned set: `var D = conn.door` vs `var D = conn && conn.door`; prompt conn captured to a local vs inline; exitFade via `tr.conn.door` vs a hoisted local | V-4 |
| ED-4 | exactly one residual CFG.regionD read inside tryDenDoor's region-resolution ternary (the IO-spec-named shape) | V-10 |
| ED-5 | clearance margins differ from Testerbot's reference table by ≤ 0.05 m (float rounding), all minimums still exceeded | V-14 |
| ED-6 | blank-line/comment drift at the regionE insertion edges (the whWall comment block shifts with the append); append-only law intact | V-2.2 |
| ED-7 | prop positions differ from any illustrative IO §2 row, provided every V-14 minimum clears (the illustration is non-normative; the table is law) | V-14 |
| ED-8 | the optional rubblePile row omitted (IO §2 marks it optional), and/or the optional `veil_crypt` constantPhase row appended (IO §5 allows; build note flags; the rot_den row untouched) | V-5 / V-16 |

**Blocking classes (any one → round FAILED; Testerbot issues the remediation card; re-gate required).**

| class | violation | verified by |
|---|---|---|
| B1 | **byte-purity:** any `−` line (excluding pure-whitespace) in the CONFIG.js or region-defs.js diffs, any pre-existing line rewritten or moved, or a non-add hunk shape anywhere in those two files | V-2.1, V-3.1 |
| B2 | **bloat-row:** bundle count ≥ 8 but < 5 distinct source contributors in the ledger, or any single source row carrying > 3 hits — a padded pass is a failed pass | V-1, V-5.3 |
| B3 | regionE block placed anywhere but after regionD's close brace and before the Round E scatter comment; a missing regionE key; a wrong land/door sub-row value class | V-2 |
| B4 | region-defs shape: connections[3] key drift, sides not exactly (−1, +1), walkFrom ≠ CFG.regionE.id, arch/gatedTo absent or non-null, helper/export block touched, connections.length ≠ 4 | V-3, V-6 |
| B5 | game.js: hunks beyond the three substitutions, E-prompt chain ORDER changed, any new CFG.regionD read beyond the V-10 residual law, prompt string not exact | V-4, V-8, V-10 |
| B6 | art law: asset outside the 8-key manifest, any assets.js diff, a second accent in the red/orange family, missing fogColor/ambientLightLevel rows | V-11 |
| B7 | geometry: any V-14 row below its minimum, ring not closed except the door gap, margin mismatch > 0.05 m, or clearance.py missing/unrunnable | V-14 |
| B8 | save-safety: any V-13 assertion failing including the negative control, or a non-THREE-free harness (THREE require, browser/puppeteer, unstubbable surface) | V-13 |
| B9 | syntax: any of the five files failing node --check | V-12 |
| B10 | file-set law: any file in the working diff outside { prototype/js/CONFIG.js, prototype/js/region-defs.js, prototype/js/game.js, prototype/builds/v8-playable.html, scratch/cc-ad1/*, io/reports/* } — save.js / player.js / enemy.js / light.js / spells.js / assets.js / region-manager.js modified | V-16 (this table) |
| B11 | process: ANY git commit/push by Devbot (NO-GIT clause), or the build note missing its required pastes (contributor ledger, clearance table, probe output, roundtrip output) so Testerbot cannot re-verify | V-1, V-6, V-13, V-14 |
| B12 | build: tools/build_v8.py exit ≠ 0, or post-rebuild bundle marker < 8 | V-1 |

**Adjudication (EC1 §6 law).** Every recorded deviation is adjudicated against this table: expected-class → PASS with note; blocking → FAIL regardless of everything else green. Zero-vs-list rule: a blocking item Testerbot discovers UNRECORDED fails the round even if all checks green.

## Post-gate slice — IO serve-flip verification (IO §6.7; not a Devbot surface)

After gate PASS and IO's commit, the release flip lands (IO post-gate step). Verification is curl-only, no browser:

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://172.16.5.1:8793/current/prototype/builds/v8-playable.html
curl -s http://172.16.5.1:8793/current/prototype/builds/v8-playable.html | grep -c veil_crypt
```

**Pass.** HTTP 200 AND served-bytes veil_crypt count ≥ 8 — SERVED bytes, never the repo copy. Testerbot's role ends at handing these two steps to IO in the verdict text (Testerbot does not own the flip). A 200-with-0-count means the flip is stale: IO re-runs the flip and re-verifies. Nicko's playtest remains the final acceptance bar — this valspec NEVER substitutes for it.
