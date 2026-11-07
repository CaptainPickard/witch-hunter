# CC-H2 VALSPEC — Testerbot validation specification, garrison-courtyard round
# (doc 64 slot H2 "Garrison Keep"; doc 66 instanced-region recipe secs 5-7 + sec 10 sides law)

Round CC-H2 · written by the Testerbot seat 2026-11-07, BEFORE the Devbot build starts.
Validates IO spec `/tmp/wh-worldfeat/io/specs/cc-h2-garrison-spec.md` against the LANDED tree at
worktree `/tmp/wh-worldfeat`, branch `feat/world-visuals`, baseline `24a6e95`. Shaped on the
landed valspec convention (cc-ad2-veil-galleries-valspec.md / cc-h1-lords-hold-valspec.md).

## 0. Scope and authority

- One deliverable: Testerbot validates the landed CC-H2 round (regionH `fort_garrison` + the
  regionG south-pole aperture + region-defs `connections[6]`), issues a PASS/FAIL verdict, and
  files `io/reports/2026-11-07-cc-h2-validation.md`. Testerbot NEVER fixes code and NEVER runs
  git (NO-GIT clause: no commit/push/checkout/worktree/branch, nothing git-touching).
- NO harness runs, NO headless browser smoke tests, NO automated playability runs (spec A-law
  closing note). Every V below is a static census, a pure-logic node probe, or a python probe —
  no THREE, no browser. Nicko's playtest is the acceptance bar; this verdict is the code-QA gate.
- Independent census DONE before this build (Testerbot-verified against the tree, 2026-11-07,
  NOT copied — recorded as the pre-build baseline at HEAD 24a6e95):
  - regionG CONFIG block (line 1684): **89** `{ asset: 'whWall…' }` rows + **24** non-wall
    dressing rows; exact landed rows to be deleted at lines 1776-1777 match the spec sec 1
    strings BYTE-EXACT (6-space indent, `wall: 12`, values `4.4/-947.92/6.25/4.63/11.69/2.40/-0.2`
    and `-4.4/-947.92/0.03/4.63/11.55/2.40/-0.2`).
  - Landed groundSeeds: regionC 1662061217 (line 478), D 1662061218 (1338), E 1662061219 (1464),
    F 1662061329 (1589), G 1662061440 (1692). String `1662061651` occurs **0** times today.
  - `CONFIG.lightSockets` keys (lines 98-117): lanternPost, banditCampfire, **whCampkit (line
    107, `// PROPOSED`, intensity 3.2 — LIVE property, not commented)**, lanternWaymarker,
    b3Gate. NO `torch` key (confirms spec line 143). NO crimson-family key (blightcap rows exist
    elsewhere at 1147-1148 but `lightSockets.blightcap` does not exist).
  - region-defs.js (330 lines): regionG registration line 187; conn[5] push + `var GD` block
    lines 197-215; conn[5] sides pair lines 217-218; the THREE-free transition helpers comment
    line 220 = the insert ceiling for the new block; `sideOfPlane` helper line 277
    (`z > conn.planeCoord ? 1 : -1`); `sideIn` line 255; connections length **6** today.
  - region-manager.js (engine truth, censused — record-only baselines for V-8): tickTransition
    line 44; inOpenDoorBand line 169 (band edge `d > suspendDepthM || -d > suspendDepthM`
    → |z−plane| == suspendDepthM is INSIDE the band, edge-inclusive); clampEnemyToHomeSide
    line 248 (per-conn hold line = `planeCoord + hs * margin`, margin =
    `CFG.enemy.holdAtBoundaryMargin` = **1.5**, CONFIG line 2622).
  - game.js: computeFireSockets ~line 2838 — a prop carries a light socket iff
    `CFG.lightSockets[p.asset]` exists (the V-3 light-law truth); exitFade consumer ~line 3097.

## 1. Gate law (applies to every check)

- Branch = `feat/world-visuals`; pinned content anchor = the baseline commit print
  `24a6e95` (record `git rev-parse HEAD` + `git status --porcelain` into header.txt; diff basis
  law §2). A drifted HEAD or foreign branch = BLOCKER on every V (H1 V-12b shape).
- Testerbot runs ONLY: grep/awk/git-diff reads, the python probes named below, and the node
  census scripts named below. Any file the round is not allowed to touch that shows a diff = the
  owning V fails by construction.
- Every FAIL is blocking unless §5 adjudicates it; Testerbot never silently tolerates.

## 2. Diff-basis law (governs all V-checks)

- All diff counts run `git diff -U0 24a6e95 -- <file>` and count `^-` / `^+` lines (never a
  context-bearing grep on `-`/`+`).
- Declared tracked-change set (the whole round): `prototype/js/CONFIG.js`,
  `prototype/js/region-defs.js`, `prototype/builds/v8-playable.html`. NOTHING else tracked may
  differ. `daynight.js` MUST be untouched (no constantPhase row is spec'd — A-9 surface law).
- Declared CONFIG.js envelope, inside CONFIG.js: additions ONLY inside the new `regionH: { … }`
  block + the regionG aperture edit (2 deletions + the CC-H2 comment block). Any other CONFIG.js
  content line changed = BLOCKER under V-1's scope law — EXCEPT the single pre-licensed
  resolution of BV-001 (§5), if IO grants it, which is exactly the deletion of the
  `whCampkit: { … }` lightSockets row (2 lines).
- Position anchors are content-anchored, never line-pinned (recipe lesson): "after the
  `regionG: {` block", "after the conn[5] sides pair and before the THREE-free transition
  helpers comment".

## 3. Check matrix — A-1..A-10 → V-checks

| # | V-check | IO-spec criterion | Blocking rule |
|---|---|---|---|
| 1 | V-1 | A-1 CONFIG regionH block | wrong key/value/order, groundSeed collision, stray constantPhase/terrain row = blocker |
| 2 | V-2 | A-2 G-aperture deletion | deleted-string survivors, wrong row counts, missing comment, extra edits = blocker |
| 3 | V-3 | A-3 props manifest + light law | row-value drift, socket-family violation, crimson row = blocker (BV-001 pre-registered) |
| 4 | V-4 | A-4 region-defs shape | wrong conn keys, walkFrom/interact present, sides sign/membership wrong = blocker |
| 5 | V-5 | A-5 sides-table law (doc 66 sec 10) | sideOfPlane ≠ sideIn either direction, land off home side = blocker (H1a P0 class) |
| 6 | V-6 | A-6 ring + A-8 props + A-9 enemies (probe re-run) | any single constraint FAIL = blocker |
| 7 | V-7 | A-7 aperture lane clearance | any post-erase G collider within 1.5 m of a lane sample = blocker |
| 8 | V-8 | A-4(game) + A-10 build + spec sec 5 engine census | game.js diff line, band/clamp/tick misbehavior, blast-radius leak, marker floor miss = blocker |

## 4. V-checks — exact commands + expected PASS evidence

### V-1 — CONFIG `regionH` block census (A-1) — BLOCKER

HOW — node census `scratch/cc-h2/config_census.js` (Specified here; Devbot/Testerbot writes it
in the cc-h1a sides_law_probe.js loader shape: `window` shim, `eval(fs.readFileSync(
prototype/js/CONFIG.js))`, NO THREE, no browser). Assertions, ALL required, exit 0:

1. Position: the `regionH: {` anchor sits AFTER the regionG block (`grep -n "regionG: {"` vs
   `"regionH: {"`) and before the next top-level key following regionG.
2. Key array EXACTLY, in order: `[id, name, center, groundRadius, groundY, groundColor,
   groundColor2, groundSeed, scatter, spawn, gravityY, fogColor, fogDensity, ambientLightLevel,
   door, enemies, props]` (17 keys; door keys in order `[planeZ, doorX, doorHalfWidth,
   suspendDepthM, wallGapPadM, land, fadeIn, fadeOut, exitFadeOut]`; land keys
   `[fort_garrison, lords_hold]`). Reorder/extra/missing key = BLOCKER; formatting-only = MINOR.
3. Values (numeric-exact): id `'fort_garrison'`; name `'Garrison Keep'` (byte-apostrophe);
   center `{0,-1024}`; groundRadius 80; groundY 0; groundColor 0x33363c; groundColor2 0x2a2d33;
   groundSeed 1662061651; scatter `false`; spawn `{0,-955}`; gravityY -22; fogColor 0x7d8289;
   fogDensity 0.068; ambientLightLevel 0.09; door planeZ -948, doorX 0, doorHalfWidth 4,
   suspendDepthM 4, wallGapPadM 0, land.fort_garrison `{0,-955,face 0,-1100}`,
   land.lords_hold `{0,-941,face 0,-822}`, fadeIn 0.3, fadeOut 0.5, exitFadeOut 0.8.
4. Absence laws: `regionH.constantPhase` undefined; `regionH.terrain` undefined;
   `regionH.door.text` undefined; `regionH.door` has NO `walkFrom`, NO `interactAt`/`interactM`,
   NO `arch` row (arch lives in the conn as `null`), `gatedTo` absent from the CONFIG door — the
   seat scan's PROPOSED `interactAt (0,-934) / interactM 3.5` (seat_scan_output line 45) are
   intentionally NOT landed under the TWO-SIDED-door law; absence is asserted so nobody
   "restores" them. `CONFIG.dayNight.constantPhases.fort_garrison` undefined.
5. Censuses: `regionH.props.length === 18`; `regionH.enemies.length === 2`;
   `grep -c "1662061651" prototype/js/CONFIG.js` → **1** (the regionH row only); printed landed
   seed set {1662061217, 1662061218, 1662061219, 1662061329, 1662061440} contains no
   1662061651 (freshness law).
6. Enemies value-exact: `{ type: 'bandit', x: -10, z: -975 }` and `{ type: 'bandit', x: 11,
   z: -976 }` (numeric equality; type string exact).
7. Traceability: `grep -c "CC-H2" prototype/js/CONFIG.js` → >= 1 (comment-banner law).

PASS bar: script exits 0, every assert line PASS. Any numeric drift beyond formatting spelling
= BLOCKER.

### V-2 — regionG aperture deletion census (A-2) — BLOCKER

HOW — byte-search + block census, run from the worktree root:

1. `grep -F -n "{ asset: 'whWallA', x: 4.4, z: -947.92, rotY: 6.25, scale: 4.63, sy: 11.69, sz: 2.40, y: -0.2, wall: 12 }" prototype/js/CONFIG.js`
   and the whWallB twin with `x: -4.4 … rotY: 0.03 … sy: 11.55` → both counts **0** post-build
   (A-7 cross-law: the erased pair's byte strings appear NOWHERE).
2. regionG block census (awk between the `regionG: {` anchor and its closing `},`):
   wall rows `{ asset: 'whWall…'` count = **87** (pre: 89); non-wall asset rows = **24**
   (unchanged); total asset rows = 111 (pre: 113).
3. Deletion comment present, contiguous, ABOVE the first remaining curtain row: all 3 lines of
   the spec sec 1 block, first line byte-exact
   `// CC-H2 (doc 64 slot H2): the two south-pole flank rows ERASED 2026-11-07` (see §5 BV-002
   on the "ONE comment line" wording).
4. Everything else in regionG byte-identical: `git diff -U0 24a6e95 -- prototype/js/CONFIG.js`
   restricted to the regionG window shows EXACTLY 2 `^-` lines (the aperture rows) and the
   comment `^+` lines INSIDE regionG — zero other regionG content changes (door row, spawn,
   land rows, all 87 survivors, all 24 dressings untouched).

PASS bar: (1) both 0; (2) 87/24; (3) comment present; (4) no third edit. Any survivor of either
byte string (same asset, differing whitespace still counts — search both the full line and the
row body) = BLOCKER.

### V-3 — regionH props census + warm-light law (A-3) — BLOCKER (with §5 BV-001)

HOW — node census (`config_census.js` props section) + grep cross-checks:

1. **18 rows**, order exactly per spec sec 3 (4 armory + 4 dungeon-mouth + 3 war-table +
   2 warm-light + 3 yard-scatter + 2 flankers), no extras, no missing rows.
2. Every row's `(asset, x, z, rotY, scale)` NUMERICALLY EQUAL to the manifest block printed by
   `scratch/cc-h2/props_scan_output.txt` (16 rows) plus the flanker pair
   `(okFenceStonewall, 10, -968, rotY 0, scale 1.2)` and `(okFenceStonewall, -10, -968,
   rotY 0, scale 1.2)`. "Byte-shaped" is enforced as value-exactness: the spec prints ints
   (`44`), the probe printed floats (`44.0`) — int/float SPELLING delta = MINOR (recorded,
   non-blocking) because the probes re-parse the landed rows; any VALUE delta = BLOCKER.
3. Light-socket law (game.js computeFireSockets truth): for every landed regionH prop row,
   `CFG.lightSockets[asset]` must exist ONLY for `banditCampfire` (1 row) and `lanternPost`
   (1 row). Assert NO lightSockets key exists for whTent, okRuinColumn, stoneSteps, skullPile,
   b6Bones, rubblePile, torch, mossBoulder, okFenceStonewall (torch explicitly socket-free —
   spec line 143 — the one deliberate NON-light warm dressing family).
4. Crimson zero: no `blightcap` (or any other crimson-family asset) row anywhere in the 18;
   `regionH.fogColor/groundColor` are the spec's slate values (already pinned in V-1), so the
   art law resolves to: crimson appears NOWHERE in regionH.
5. **BV-001 (pre-registered, §5) interacts here**: `CONFIG.lightSockets.whCampkit` is LIVE
   (line 107, `// PROPOSED`, intensity 3.2), and the landed manifest carries 2 whCampkit
   dressing rows — under the computeFireSockets truth those rows ARE socket-carrying, so as the
   spec stands this census observes **4** socket-carrying prop rows vs the declared "banditCampfire
   + lanternPost ONLY (2 sockets)". Testerbot records the observed count verbatim and
   adjudicates per §5; it never edits the lightSockets table itself.

PASS bar (as-written): count of socket-carrying assets among the 18 == 2
{banditCampfire, lanternPost} — anything else = BLOCKER pending §5 BV-001 adjudication.

### V-4 — region-defs registration + `connections[6]` shape census (A-4) — BLOCKER

HOW — grep + node census (region-defs eval'd after CONFIG under the window shim):

1. Registration line present, appended after the regionG registration line (anchor: line 187 at
   HEAD), exactly `regions[CFG.regionH.id] = makeRegion(CFG.regionH, -1);` (the -1 is the
   plane-0 convention only — C0-7 law note required in the adjoining comment).
2. `var HD = CFG.regionH.door;` + `connections.push({ … })` block whose keys are EXACTLY:
   `from: CFG.regionG.id, to: CFG.regionH.id, axis: 'z', planeCoord: HD.planeZ, sides: {}`,
   door `{ doorX: HD.doorX, doorHalfWidth: HD.doorHalfWidth, suspendDepthM: HD.suspendDepthM,
   wallGapPadM: HD.wallGapPadM, arch: null, gatedTo: null, land: HD.land }`.
   **NO `walkFrom` row, NO `interact` row** (two-sided B/C grammar), `gatedTo: null`,
   `arch: null`.
3. SIDES TABLE — BOTH entries LIVE, adjacent literal rows:
   `connections[6].sides[CFG.regionG.id] = 1;` and `connections[6].sides[CFG.regionH.id] = -1;`
   with the sec 10 comment banner (`// SIDES TABLE (CC-H2 …)`); both sideIn values are OWN
   numbers on the conn (missing table = the fallback-to-region-side bug class, H1a).
4. Live helper census: `DEFS.connections.length === 7`;
   `connectionsOf('fort_garrison')` length 1 and `[0] === DEFS.connections[6]`;
   `connectionBetween('lords_hold','fort_garrison') === DEFS.connections[6]`;
   `planeIn(conn6,'fort_garrison') === true` AND `planeIn(conn6,'lords_hold') === true`;
   `conn6.planeCoord === -948 === CFG.regionH.door.planeZ`; conn[0..5] objects unchanged
   (compare the pre-build snapshot of the six push blocks' key sets).
5. Append-only diff: `git diff -U0 24a6e95 -- prototype/js/region-defs.js` → **0 removed
   lines**; additions only after the conn[5] sides pair and before the THREE-free transition
   helpers comment.

PASS bar: all five groups hold. Wrong from/to/axis, a stray walkFrom/interact, a missing or
inverted sides entry = BLOCKER.

### V-5 — sides-table probe, the doc 66 sec 10 interior law, BOTH entries (A-5) — BLOCKER

HOW — primary: node probe `scratch/cc-h2/sides_probe.js` (Specified here; cc-h1a
sides_law_probe.js pattern: window shim → eval CONFIG.js + region-defs.js; NO region-manager
needed for this V, no browser, no harness). Fallback (if node is unavailable): python — parse
the conn[6] block's `planeCoord` and both `sides` lines from region-defs.js with regex,
replicate `sideOfPlane(z) = z > planeCoord ? 1 : -1` from the PARSED value, assert the same
equalities. Required assertions, ALL four equalities + both land comparisons:

```
sideOfPlane(conn6, -822)  === 1  === sideIn(conn6, 'lords_hold')     // G interior reads +1
sideOfPlane(conn6, -1024) === -1 === sideIn(conn6, 'fort_garrison')   // H interior reads -1
conn6.door.land.fort_garrison.z (-955) <= conn6.planeCoord (-948)     // H land on H home side
conn6.door.land.lords_hold.z   (-941) >  conn6.planeCoord (-948)      // G land on G home side
```

Plus the law's generality clause (sec 10 item 1): `sideIn(R) == sideOfPlane(R's interior)` for
EVERY member — assert the two above and additionally that neither region lies ON the plane
(interior z values strictly off −948). Plane-on-edge sanity per sec 10 item 2: the plane
(−948) sits 4 m inside H's rim (−944) and 1.5 m inside G's playable south rim (−946.5, playRadius
124.5 of r 126) — record the two margins; a plane at the disc CENTER would be an instant blocker
reclass.

PASS bar: probe exit 0, every line PASS. ANY sign inversion = the H1a P0 class = BLOCKER.

### V-6 — geometry probes RE-RUN against LANDED rows (A-6 ring, A-8 props, A-9 enemies) — BLOCKER

HOW — ONE python probe, `scratch/cc-h2/clearance.py` (Specified here; Devbot ADAPTS
`scratch/cc-h2/seat_scan.py` + `scratch/cc-h2/props_scan.py` into it — Testerbot does not write
it, Testerbot RE-RUNS it against the LANDED files and checks NO hard-coded spec constants feed
the assertions: every constraint computes from CONFIG.js-parsed regionH + regionG rows and the
region-defs-parsed conn[6]). Structure: sections A (H2 ring), B (G aperture lane → V-7), C
(props), D (enemies). Commands: `python3 scratch/cc-h2/clearance.py` from the worktree root;
PASS = exit 0 + every printed line `ok` + final `ALL CONSTRAINTS: PASS`; any FAIL line = blocker.

Section A — H2 ring (from LANDED regionH whWall rows, wall column = ring index n, r 0.45
collider circles along local X, ext 1.899 · scale — the recipe sec 6 collider math):
- 48 wall rows; **384** colliders; every row `|hypot(x, z + 1024) − 80| <= 0.6` (r-80 rim).
- Window strip EMPTY: 0 colliders with `|x| <= 4` and `|z + 948| <= 3`.
- Lane samples (x −4..4, z −951..−945, 0.5 m grid or finer): nearest H2-collider distance
  >= **1.0** (pre-freeze probe printed 7.49).
- Mouth bearing arc: 0 colliders with bearing inside the recomputed aperture arc (seat_scan.py's
  bearing convention; pre-freeze arc ≈ [82.8, 97.2] — recomputed-vs-frozen drift beyond ±0.5° is
  recorded as a MINOR variance, not a blocker, since the arc is re-derived from landed rows);
  **every bearing octant holds >= 8 colliders** (pre-freeze minimum 34).

Section C — props (the props_scan.py law re-run against LANDED regionH rows):
- Every prop >= 4.0 m raw of BOTH rings (G post-erase collider set + H2 full 384);
  every prop >= 6.0 m from spawn (0,−955) AND both land rows (0,−955)/(0,−941);
  >= 4.0 m mutual across all 18; >= 5.0 m from both sentries (−10,−975)/(11,−976);
  rho <= 78.5 from center (0,−1024).
- Flankers (10,−968)/(−10,−968): >= **16.0** m raw off the H2 ring (margin law), >= 4.0 off the
  G post-erase ring, >= 4.0 mutual from the manifest (pre-freeze: 23.12 / 20.29 / ≥14.43).

Section D — enemies:
- Exactly the 2 bandit rows (−10,−975)/(11,−976) parsed from CONFIG; mutual 21.0 >= **12.5**
  (doc 66 tolerance ±0.15 — the floor accepted at 12.4); each >= **8.0** m from spawn (0,−955)
  and both land rows; each >= **4.45** m walk-clear of the H2 ring (pre-freeze ≈ 30.0/30.8);
  neither sentry inside the G↔H window lane band (cross-check with V-7's lane domain).

### V-7 — regionG aperture lane clearance, post-erase (A-7) — BLOCKER

HOW — clearance.py **section B**: rebuild the G ring from LANDED regionG whWall rows (must be
87 rows), erase-audit (the 2 aperture rows' coordinates absent from the landed row set), build
the post-erase collider list (**1044** expected = 1068 full-ring minus the pair's 24), then:
- Lane sample domain x −4..4 × z −951..−945 (0.5 m grid or finer, >= 225 samples): count of
  post-erase G colliders within **1.5 m** of ANY sample must be **0** (pre-freeze nearest-collider
  distance 5.168).
- Cross-check: the two deleted byte strings (V-2 strings) appear nowhere in CONFIG.js.

PASS bar: count == 0 and G landed wall rows == 87. Any collider-in-lane = the lane is blocked =
BLOCKER.

### V-8 — engine census (record-only) + game.js diff + bundle marker floor (A-4 game part, A-10, spec sec 5) — BLOCKER (diff + markers parts)

HOW — three parts; ALL commands are reads (no code changes anywhere in this V):

1. **game.js diff empty** (A-4): `git diff -U0 24a6e95 -- prototype/js/game.js` → **0 lines**.
   The prompt/forceCross/land/fade machinery is conn-carried; a single diff line = BLOCKER.
2. **Live logic census** (record-only; node, sides_probe.js extended with the region-manager
   shim defaults — `cfg.boundary/chokepoint/preWarm` per cc-h1a; still no browser):
   - `connectionsOf('fort_garrison')` walks ONE connection (conn[6], planeIn true);
     `connectionsOf('lords_hold')` walks TWO (conn[5] planeIn-true in G via `walkFrom === G.id`,
     conn[6] planeIn-true both).
   - `inOpenDoorBand`: TRUE at (x 0, z −946) and (x 0, z −950) and at the edge
     (x 0, z −944 → |z−plane| = 4, edge-inclusive) for BOTH activeIds; FALSE at 4+ε (z −952.1 /
     −943.9); window-lane-only (FALSE at x 4.5, z −948); `doorLocked(conn6, ·) === false`
     everywhere (gatedTo null).
   - `clampEnemyToHomeSide`: home side of fort_garrison on conn[6] = **−1**; both landed
     sentries NEVER clamped (positions unchanged — z −975/−976 are home-deep below the hold
     line −949.5 = plane + hs·margin); a synthetic enemy at z −940 clamps to exactly **−949.5**.
   - First-tick no-cross (doc 66 sec 10 item 3 law): `tickTransition` at H2 spawn (0,−955) and
     G land (0,−941) fires NOTHING (no plane cross on a stationary first tick).
   - Walk-back / walk-in cross census (record-only): a tick z −949.2 → −946.8 inside the window
     while activeId fort_garrison transitions to lords_hold; the reverse −946.8 → −949.2 while
     activeId lords_hold transitions to fort_garrison (the two-sided cross, planeIn both).
3. **Blast radius + build marker floor** (A-9 surface discipline + A-10):
   - `git status --porcelain` + `git diff -U0 24a6e95 --stat`: tracked changes ONLY in
     {CONFIG.js, region-defs.js, v8-playable.html}; `prototype/js/daynight.js` diff EMPTY;
     untracked additions only under io/specs/cc-h2-\*, scratch/cc-h2/\*, and the report itself.
   - Bundle marker floor: `grep -c fort_garrison prototype/builds/v8-playable.html` → **>= 8**
     on the LANDED bundle (IO's `python3 tools/build_v8.py` is the build; Testerbot greps and
     NEVER rebuilds — the H1 V-1 division of labor). Build-tool drift law: record which
     build_vX was newest at build time from the build note.

## 5. Blocking-variance adjudication (AD2 §5 format) — PRE-REGISTERED BEFORE the build

```
BV-ID | UTC timestamp | V-check | criterion | observed | declared | classification | reasoning | owner
```

Pre-registered rows (declared NOW so post-build adjudication is mechanical):

- **BV-001 — the whCampkit socket conflict (potentially BLOCKING, owner IO, resolve BEFORE the
  Devbot build).** `CONFIG.lightSockets.whCampkit` (line ~107, marked `// PROPOSED`, intensity
  3.2) is a LIVE key, and the spec's landed 18-row manifest includes 2 `whCampkit` dressing
  rows; game.js computeFireSockets lights every prop whose asset has a lightSockets row. Observed
  truth if built as-is: 4 socket-carrying prop rows in regionH vs the spec's declared
  "banditCampfire + lanternPost ONLY (2 sockets, ONE warm amber family)" (A-3) and the art law
  "ONE amber family (2 sockets)". Resolution paths, IO's call ONLY:
  (a) license the deletion of the whCampkit lightSockets row this round (2-line CONFIG.js edit;
    V-1's envelope grows by exactly that deletion; V-3 then passes at 2 sockets), or
  (b) amend spec A-3's light law to admit the campkit family (V-3 then passes at 4 sockets;
    observed-vs-declared recorded, art-law tension noted for Nicko's playtest).
  Testerbot default as-written: observed 4 vs declared 2 = spec-as-written FAIL (blocking) until
  IO resolves. This row EXISTS because the valspec is written pre-build — it is a spec defect,
  not a build defect.
- **BV-002 — spec sec 1 wording, NON-BLOCKING.** The spec says "insert ONE comment line" and
  then prints a 3-line `//` comment block. Census definition (used in V-2): the insertion is
  ONE comment BLOCK of exactly the 3 printed lines, contiguous, first line byte-exact. No
  variance expected; recorded so a literal "1 physical line" reading never fails a correct
  build, and a 3-line-correct build never fails a literal reading.
- **BV-003 — frozen interact rows dropped by design, NON-BLOCKING.** seat_scan_output line 45
  froze `interactAt (0.0, -934.0) interactM 3.5`; the spec (two-sided B/C grammar, first
  H-chain walk-through) lands NEITHER. V-1 asserts their APPROPRIATE absence. Any landed
  interactAt/interactM row = spec deviation = BLOCKER under V-1.

Rules: non-blocking ONLY if formatting-only AND IO-licensed (H1 §5 + amendment discipline);
Devbot fixes route back through IO; verdicts FAIL pending re-run; Testerbot never fixes code.
BV-IDs sequential.

## 6. Verdict PASS/FAIL table (AD2 §6 shape, H1 precedent)

One row per V-check in §4; round verdict = PASS iff every row is PASS + zero blocking variances
+ restore law clean + blast-radius sweep clean. A criterion with no evidence, or a V skipped
without a recorded BLOCKED-PENDING-BUILD classification, fails by construction.

## 7. Evidence bundle

`/tmp/wh-valspec-cc-h2-evidence/` (OUTSIDE the worktree, D-4 law): one file per check
`ev/v1-config-census.txt`, `ev/v2-aperture.txt`, `ev/v3-props-lights.txt`, `ev/v4-conndefs.txt`,
`ev/v5-sides-probe.txt`, `ev/v6-clearance.txt`, `ev/v7-lane.txt`, `ev/v8-engine-diff.txt`,
plus `snapshot-before.txt`, `snapshot-after.txt`, `variances.csv`, `verdict.md`, and
`header.txt` carrying the pinned baseline (`git rev-parse HEAD` → 24a6e95-family, branch,
porcelain at validation time). Every evidence file carries the raw command line + raw output;
no hand-written summaries in place of output (H1 §7 law).

## 8. Verdict-report requirements (the post-build Testerbot's deliverable)

File: `io/reports/2026-11-07-cc-h2-validation.md`. Contract:

1. The report OPENS with the ALL-CAPS verdict line: `**VERDICT: PASS**` or `**VERDICT: FAIL**`
   (first bold line, H1 precedent), followed by the one-paragraph scope line (round, date,
   worktree/branch/baseline, evidence path).
2. Per-V results table — one row per V-check: `| # | V-check | Result | Evidence |` covering
   V-1..V-8 exactly as §4 titles them, every row PASS / FAIL / BLOCKED-PENDING-BUILD + the
   evidence filename.
3. BV adjudication rows verbatim from §5's format, sequential BV-IDs, with the pre-registered
   BV-001 resolution recorded (IO's licensed path a or b, or the observed-vs-declared fail).
4. An independent spot-checks section: >= 3 recomputed-from-CONFIG-rows numbers (e.g. spawn
   depth past the plane |−955 + 948| = 7.0 with in-band margin 3.0; enemy mutual
   sqrt(21² + 1) ≈ 21.02; flanker H2-ring margin 23.12) — recomputed, never copied (H1 §law).
5. The disclosure ledger: any Devbot build-note deviations (ED-ids) restated, with Testerbot's
   classification of each.
6. NOTHING else changes in the tree: the report is the ONLY io/reports write; Testerbot commits
   NOTHING; IO is the sole git gatekeeper (NO-GIT clause).

## 9. HOW TO RUN (Testerbot execution order, deterministic)

1. Snapshot: `git rev-parse HEAD`, `git status --porcelain`, `git stash list` → header.txt.
2. Confirm branch = `feat/world-visuals`, baseline anchor 24a6e95 (§1 gate).
3. Static censuses first (no build dependence): V-2, V-3 (minus adjudication), V-4
   (grep part), V-1 (grep part), V-8 diff part.
4. Node probes next (worktree LANDED source): V-5 sides probe, then V-1/V-4 live census
   (config_census.js), then V-8 logic census (sides_probe.js extended).
5. Python probes (LANDED rows, no spec constants): V-6 sections A/C/D, then V-7 section B —
   `python3 scratch/cc-h2/clearance.py` exits 0 ONCE with both sections green (V-6 + V-7).
6. Bundle greps: V-8 marker floor on the landed v8-playable.html (IO's build is the artifact;
   Testerbot does NOT rebuild unless the verdict needs identity — then D-2/D-3 restore law).
7. Adjudicate §5 BVs (BV-001 resolution check against whatever IO licensed), package the
   evidence bundle, emit `verdict.md`, write `io/reports/2026-11-07-cc-h2-validation.md` per §8.
8. Report to IO: verdict table + variances + restore proof + this valspec's own pass note.
   NOTHING ELSE. IO is the sole committer.
