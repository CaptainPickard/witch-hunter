# CC-H6 VALSPEC — The Remains (regionL, delve strata V5 off the Tithe Vaults) — written BEFORE build

Validates `io/specs/cc-h6-remains-spec.md` against a future Devbot build on
`feat/world-visuals` in `/tmp/wh-worldfeat`. Closest siblings: CC-H5
(regionK, the same one-sided conn grammar one stratum up), CC-H3/H4
(probe + lair lineage). Testerbot validates INDEPENDENTLY (fresh probe
run + own greps); report FIRST to
`io/reports/2026-11-07-cc-h6-remains-validation.md`, then verdict (RUNBOOK
report-first law). No harness runs, no headless smoke: the verdict is
code QA only (acceptance bar stays Nicko's playtest). Sha windows ARE
PINNED BY CONTENT ANCHOR (V-6 law), never line numbers.

## 1. BASELINE (pre-build state at HEAD e20f61d)

- `git log --oneline -1` = `e20f61d build: v8 bundle (worktree) - CC-H5b
  hazards stamp`; branch `feat/world-visuals`. `git status --porcelain`
  at valspec time: untracked `io/specs/cc-h6-remains-spec.md` + this
  valspec ONLY. Any OTHER dirty path at verdict time is adjudicated
  against this ledger (unregistered = FAIL).
- File shas (both `git show HEAD:<p> | sha1sum` AND worktree `sha1sum`
  recorded, identical):
  - `prototype/js/CONFIG.js`       `dfcef3bea4e080baa2a7670e407ce7163833842d`
  - `prototype/js/region-defs.js`  `2193a5a53c46d2183c8e065d24da1bd74a72ba6c`
  (post-build exactly these two MUST change; every other prototype/js /
  prototype/index.html file keeps its HEAD sha — see CH-6.)
- `node --check prototype/js/CONFIG.js` + `region-defs.js`: PASS at HEAD
  (recorded), required PASS post-build.
- Content anchors (pre-build counts; go non-zero ONLY via the build):
  - CONFIG.js: `^  regionK: {` == 1; `regionL` == 0; `the_remains` == 0;
    `lastchancel` == 0.
  - region-defs.js: `regionL|the_remains|lastchancel` == 0;
    `regions[CFG.regionK.id] = makeRegion(CFG.regionK, -1);` == 1; the
    conn[9] sides pair `connections[9].sides[CFG.regionJ.id] = +1;` /
    `connections[9].sides[CFG.regionK.id] = -1;` == 1 each (predecessor
    the new conn[10] mirrors).
  - Node eval (THREE-free: `global.window={}; eval CONFIG; eval
    region-defs`): `WH_REGION_DEFS.connections.length === 10`; `conn[9]
    .from === 'veil_spire_approach' && conn[9].to === 'tithe_vaults'`.
  - K seats the new layer reads against (each asserted from the PARSED
    object, not an eyeball): `regionK.id === 'tithe_vaults'`,
    `regionK.spawn` = (0,-856), `regionK.door.planeZ === -848`,
    `regionK.door.doorHalfWidth === 2.2`, tithecaptain lairNest =
    (0,-872) (enemy.js:1245 law), `lairRadius === 16`.

## 2. VALSPEC CHECKS (CH-1..CH-6, one per IO-spec section; ALL read LANDED rows)

**CH-1 — IO-spec sec 2: regionL row (CONFIG.js).** Anchors: `  regionL: {`
== 1; `  id: 'the_remains'` == 1. PARSED asserts:
- Key-set LAW: `Object.keys(regionL)` == `Object.keys(regionK)` minus
  `traps` minus `rotLair` (sorted cmp on the eval; `traps`/`rotLair` NOT
  in L's keys — doc 47 S5 clean-chamber citations).
- Spot equals (sec's PROPOSED initial values): id `'the_remains'`; name
  `'The Remains'`; center {x:0, z:-1064}; groundRadius 30; groundY 0;
  groundColor 0x090b10; groundColor2 0x0c0e11; groundSeed 559043117;
  scatter === false; spawn {x:0, z:-1044}; gravityY -22; fogColor
  0x090710; fogDensity 0.17; ambientLightLevel 0.04; enemies deep-= [];
  lairs deep-= `[{type:'lastchancel', x:0, z:-1060}]` (length 1). A
  Nicko-tuned delta passes ONLY with a build-note adjudication entry.
- Seed freshness: L's groundSeed differs from EVERY other region's
  landed groundSeed (probe tallies from the parse: landed set
  1662061217/1218/1219/1329/1440/1662061763/448271909).
- Darkness math (parsed, no hard-coding): d95_L = sqrt(-ln 0.05)/0.17 in
  [10.13, 10.23] and STRICTLY < d95_K (K fogDensity 0.16 -> ~10.82,
  parsed) < d95_J; ambient 0.04 < K 0.045 < J 0.05 as strict
  inequalities.

**CH-2 — IO-spec sec 2b: ring + identity/dressing props.**
- Ring: exactly 10 whWall rows in regionL.props, alternating
  whWallA/whWallB starting A; each `wall: 10`, `y -0.2`, `sz 2.40`, `sy
  11.69` (A) / `11.55` (B); rotY monotonic increasing ~ `3.14 +
  0.6283*k` (row order N->E->S->W; x-sign follows north->east positive).
  NO omission (K law: the ring is closed behind the plane).
- Ring is RE-DERIVED, not literal-copied (CC-H5 SPEC-FIG-FIX law): rho ==
  30.0 +- 0.05 for all 10 rows; adjacent-chord uniformity <= 0.02;
  scale = landed chord / 1.899 (sec initial 9.763). The sec-2b row
  literals are CONTEXT; a probe asserting literal sec equality instead
  of the rho/chord law fails this check by design.
- Lane LAW: plane -1036 (`door.planeZ`), halfWidth 2.2: zero ring
  colliders inside the window |x| <= 2.2 at z = -1036 within 1.0 m;
  north-point row edge clearance >= 1.0 m (sec quote 1.55 = 2.00 -
  0.45); NO mouth gap (plane crosses INSIDE the closed ring).
- Props: exactly 13 non-ring rows, asset tally ==
  {stoneSarcophagus:1, okRuinColumn:2, mourningStatue:2, stoneSteps:2,
  skullPile:2, mossBoulder:1, lanternPost:1, blightcap:2}; every asset
  id already landed elsewhere at HEAD (CONFIG-only add: no new asset
  strings outside regionL vs HEAD tally).

**CH-3 — IO-spec sec 4: registration + conn[10] (region-defs.js).**
Greps, each exactly 1 hit:
`regions[CFG.regionL.id] = makeRegion(CFG.regionL, -1);`,
`connections[10].sides[CFG.regionK.id] = +1;`,
`connections[10].sides[CFG.regionL.id] = -1;`. Node-eval on
`WH_REGION_DEFS.connections[10]`:
- `connections.length === 11`; from === `'tithe_vaults'`; to ===
  `'the_remains'`; axis 'z'; planeCoord === -1036; door.doorX 0,
  doorHalfWidth 2.2, suspendDepthM 0, wallGapPadM 0, arch null, gatedTo
  null, walkFrom === `'the_remains'` (ONE-SIDED), interact deep-=
  `{from:'tithe_vaults', x:7.5, z:-854, radius:3.5}`, land.tithe_vaults
  deep-= `{x:2, z:-858, faceX:0, faceZ:-880}`, land.the_remains deep-=
  `{x:0, z:-1044, faceX:0, faceZ:-1060}` AND equals parsed
  `regionL.spawn` (landing row = spawn row), fadeIn 0.3 / fadeOut 0.5 /
  exitFadeOut 0.8, `text.prompt === 'E - Descend into the remains'`
  (verbatim; assert in the same eval that it differs from conn[9]'s
  prompt).
- Sides LAW (the central engine decision, NOT adjudicable): parsed
  sides[K] === +1 and sides[L] === -1; helper agreement
  `sideIn(conn,'the_remains') === sideOfPlane(conn, regionL.spawn.z)
  === -1` (L interior south of -1036), `sideIn(conn,'tithe_vaults')
  === +1` (K interior north of -1036), `planeIn(conn,'tithe_vaults')
  === false`, `planeIn(conn,'the_remains') === true`,
  connectionBetween resolves it in BOTH directions. If any sides assert
  fails, quote region-defs sideIn/sideOfPlane definitions in the verdict.
- conn[9] span UNTOUCHED (block cmp HEAD vs post-build, CH-6).

**CH-4 — IO-spec sec 5: lastchancel row + body maps (CONFIG.js).**
PARSED `C.enemy.lastchancel`:
- Key set == spec list (name, hp, dmg, speed, aggro, pattern, slamRadius,
  slamArcDeg, slamWindup, slamActive, slamRecover, slamCooldown,
  slamTrackDegPerSec, engageRange, cueDark, cueHot, scale, lair,
  lairRadius, rearm, loot, minions, radius, corpseLingerSec, maxCorpses,
  riseSec, barLiftM, ai1). Spot equals: hp 400, dmg 24, speed 4.2,
  aggro 18, pattern `'boss-slam'`, slamRadius 4.6, slamArcDeg 100,
  slamTrackDegPerSec 120, scale 2.3, cueHot 0xd84a4a, lairRadius 16,
  rearm {days 3, trigger 'proximity', radius 14}, loot
  `[{mat:'stolenCoin', n:[2,5]}]`, ai1.guardArcDeg 42.
- Lair self-consistency (ENGINE truth = enemy.js:1245 lairNest): nest =
  `regionL.center + {x: lair.x, z: lair.y}` EQUALS regionL.lairs[0]
  {x,z}; `lair.region === 'L'`; `lair.flagPrefix === 'lastchancel'` ->
  key `'lastchancel_cleared_L'` (composition assert: prefix +
  `'_cleared_'` + region letter); K-mirror spacing `|seat.z -
  land.the_remains.z| === 16.0 +- 0.5` (landing 16 == aggro 16).
- Minions crash-guard row (THE safety item): `minions` KEY EXISTS,
  deep-= `{asset:'zealot', cap:0, interval:999.0, range:5.0}`; cap === 0
  AND interval is a finite number — enemy.js lairTick (~1285-1290,
  verified: `var M = cfg.minions;` then `M.interval` / `M.cap` read
  UNGUARDED every tick) crashes on a boss row with no minions block;
  cap 0 keeps the spawner permanently dead (alive < cap false). Engine
  edit REJECTED (all-config law) — CH-6's empty engine diff is the proof.
  `lairOnDeath`'s `cfg.minions.dieOnMasterDeath` read is falsy-safe on
  its absence (spec-as-written): recorded, not asserted.
- Body maps (symmetry law): `bodyByType.lastchancel === 'banditBody'`,
  `animVariantByType.lastchancel === 'bandit'`.
- Engine census record-only (sec 7): no constantPhases.the_remains, no
  scatter gate change, wh-ground reads the flat disc, save.js additive
  path unedited, `grep -c lastchancel prototype/js/enemy.js` stays 0.

**CH-5 — IO-spec sec 6: clearance laws.** Enforced by the probe's
G-01..G-12 lines (output contract = sec 4 below): ring rho/chord · lane
window · north-row edge >= 1.0 · props->ring raw >= 4.0 · prop mutual
edges >= 2.0 · boss-seat clear circle >= 6.0 AT the parsed lairs seat
(sec figure (0,-1060); blockers = all 13 prop footprint edges + ring
r0.45 colliders; footprint map DISCLOSED) · L land/spawn >= 8.0 south of
plane -1036 on the home side · K land row (2,-858) >= 8.0 south of K's
plane -848, inside K's disc (r34 parsed), on K's home side · hook
(7.5,-854) >= 4.0 from EVERY K collider (ring + props + enemy seats)
AND >= 2.0 outside the captain lairRadius-16 circle about the PARSED K
seat (0,-872) AND outside K's own mouth lane (|hook.x| >
K.door.doorHalfWidth at -848) · disc containment for L landing row +
every L prop (raw + footprint radius vs r30, jitter margin per the
cc-h2/h3 lineage, disclosed) · x=0 chain axis (K center, L center, L
spawn/land rows, doorX all x == 0) · lair-tick safety re-asserted from
the parse (minions.cap === 0, interval defined).

**CH-6 — IO-spec secs 3 + 7 + 8: parent NONE, census, surface discipline.**
- `git diff e20f61d -- prototype/js/enemy.js prototype/js/game.js
  prototype/js/save.js prototype/js/region-manager.js prototype/js/
  daynight.js prototype/index.html` EMPTY; `git diff e20f61d --
  prototype/js/region-defs.js` confined to the appended regionL conn
  block (conn[9] span + K registration byte-identical); `git diff
  e20f61d -- prototype/js/CONFIG.js` confined to regionL + lastchancel +
  body-map rows (regionK block byte-identical by block-cmp, sec 3 law).
- No `traps`/`rotLair` strings added anywhere outside nothing (L has
  none); no new asset ids; no constantPhases row (grep).

## 3. LETTER-vs-LANDED TABLE (pre-empts disputes: spec letter vs landed law)

| IO-spec figure | Landed MUST satisfy | Class |
|---|---|---|
| regionL row shape "on regionK's key set" | keys == regionK minus traps/rotLair | LAW |
| enemies [], lairs [lastchancel (0,-1060)], props sec 2b | parsed deep-equals; lairs row == lairNest derive | LAW (shape) / INITIAL (coords) |
| center (0,-1064), groundRadius 30, seeds/colors/fog 0.17/ambient 0.04, spawn (0,-1044) | exactly as spec = initial values; Nicko deltas via build-note adjudication only | INITIAL |
| rho == 30.0 +- 0.05, chord uniformity <= 0.02 | re-derived from the 10 LANDED rows, never literal sec copy | FLOOR (law) |
| sec-2b ring z-literals (H5-style drift) | context only; rho/chord law governs | context |
| lane figure 1.55 m | floor is >= 1.0 m edge clearance; 1.55 is the quote | FLOOR 1.0 (1.55 quote) |
| prop-edge floors 4.0 (to ring) / 2.0 (mutual) | computed raw/edge distances on landed rows | FLOOR |
| boss-seat clear 6.0 at (0,-1060) | >= 6.0 at the ENGINE-derived seat (== lairs row), blockers disclosed | FLOOR; (0,-1060) initial |
| land/spawn >= 8.0 south of plane, home side; K land >= 8.0 + in r34 disc + home side | measured from landed planeZ + land rows | FLOOR |
| hook >= 4.0 from K colliders; >= 2.0 outside lairRadius 16 | measured vs ALL K colliders + parsed K lair circle | FLOOR; lairRadius 16 initial |
| disc containment (raw + map radius vs r30) | every prop + land row; jitter margin disclosed | FLOOR |
| conn[10] sides K +1 / L -1, walkFrom 'the_remains', one-sided | parsed + helper agreement (sec 2 CH-3) | LAW |
| connections.length 10 -> 11 | parsed count | LAW |
| prompt 'E - Descend into the remains', fades 0.3/0.5/0.8 | verbatim parsed | INITIAL (verbatim) |
| lastchancel numerics (hp 400, dmg 24, ..., ai1 42, scale 2.3) | as spec; build-note adjudication for tuned deltas | INITIAL |
| minions {cap 0, interval 999.0} present | key EXISTS + cap === 0 + finite interval | LAW (crash guard); 999.0 initial |
| lair { y: 8 } with center (0,-1064) | self-consistency LAW governs (see ambiguity A1): trio must agree + 16.0 m spacing | LAW wins over letter |

## 4. PROBE OUTPUT CONTRACT (Devbot writes; Testerbot re-runs fresh)

Files: `scratch/cc-h6/solve_geometry.py` + `scratch/cc-h6/save_roundtrip.js`
(deviation precedents: scratch/cc-h3/h5). CONFIG-ROW-PARSED LAW: every
NEW-row value comes from eval(CONFIG.js) + eval(region-defs.js) at run
time; hard-coding spec constants for the new rows = FAIL. Floors may be
constants; landed values may not.

`solve_geometry.py` stdout, EXACT shapes (fail-closed: prints FAIL lines
and exits non-zero rather than throwing; a stack trace where an assert
should be = the probe is the bug):

```
CONFIG-ROW-PARSED: regionL wallRows=<n> props=<m> conn10=<true|false> lairSeat=(<x>,<z>) planes=(L -1036, K -848) (values from live CONFIG.js/region-defs.js)
PASS G-01 rho: max |rho-30.0| = <d> | FAIL G-01 rho <rho> outside 30.0 +- 0.05
PASS G-02 chord: spread = <d> <= 0.02
PASS G-03 lane: <count> colliders in window |x|<=2.2 @ -1036 (need 0)
PASS G-04 north-row edge clearance = <d> >= 1.0
PASS G-05 prop->ring min raw = <d> >= 4.0
PASS G-06 prop mutual edge min = <d> >= 2.0
PASS G-07 boss-seat clear circle = <d> >= 6.0 at (<x>,<z>)
PASS G-08 L land/spawn: plane offset = <d> >= 8.0, side = <sign>, spawn==land
PASS G-09 K land (2,-858): plane offset = <d> >= 8.0, in-disc dist = <d> <= 34, side = <sign>
PASS G-10 hook->K colliders min = <d> >= 4.0
PASS G-11 hook->captain-lair-circle clearance = <d> >= 2.0, lane-clear = <d>
PASS G-12 disc: land row + <m> props max overfill = <d>; chain x-axis = <max|x|>; lair-tick: minions.cap = 0 interval = <v>
H6-GEOMETRY-SUMMARY: <passed>/12 PASS (scratch/cc-h6/solve_geometry.py)
```

Every G-line starts `PASS G-<nn> ` or `FAIL G-<nn> ` with measured
numbers vs floors. G-12 folds the lair-tick safety check (lastchancel
row HAS the cap-0 minions block, parsed). Banner prints once, first
line, quoting the parse.

`save_roundtrip.js` stdout (THREE-free node eval CONFIG.js ->
region-defs.js -> save.js with a stubbed game surface, cc-ad1 pattern):

```
SAVE-ROUNDTRIP: THREE-free eval CONFIG.js -> region-defs.js -> save.js (stubbed game surface)
PASS SR-1 capture: regionId 'the_remains' rides validRegion + save block
PASS SR-2 restore: gate crossing honored + teleport back to land rows
PASS SR-3 negative: unknown region id falls back, no false gate
PASS SR-4 lair key: 'lastchancel_cleared_L' matches enemy.js:1702 regex /^([a-z][a-z0-9]*)_cleared_([A-Z])$/ groups lastchancel/L, day round-trips
H6-SAVE-SUMMARY: <passed>/4 PASS (scratch/cc-h6/save_roundtrip.js)
```

Both probe file paths are printed on the SUMMARY lines (locatable
artifacts). SR-4 verifies the key SHAPE (the enemy.js regex), not a
THREE-backed enemy eval; composition asserted in CH-4. Testerbot runs
each probe twice and diffs outputs (determinism), like the H5 card.

## 5. VERDICT RULES

PASS requires ALL of:
1. Every G-01..G-12 + SR-1..SR-4 line PASS on the LANDED rows, run fresh
   twice with byte-identical output; both probes carry the CONFIG-ROW-PARSED
   banner and CONFIG-ROW-PARSED discipline (no hard-coded spec constants).
2. CH-1..CH-6 all PASS (each cited in the verdict with raw numbers:
   shas, greps, parsed values, distances).
3. Build succeeds via the NEWEST `tools/build_vX.py` present at build
   close (build_v8.py at valspec time; do NOT regress to an older vX),
   with the served-title stamp line and the probe-output digest verbatim
   in `scratch/cc-h6/build-note.md` (sec 8).
4. Worktree `git status --porcelain` build-delta == EXACTLY:
   `prototype/js/CONFIG.js`, `prototype/js/region-defs.js`,
   `scratch/cc-h6/*`, `prototype/builds/<newest vX bundle>` — plus the
   pre-registered `io/specs/*` + `io/reports/*` files from sec 1's
   ledger. ANY other touched path = FAIL (engine files, assets/, CSS,
   daynight, index.html above all).
5. NO-GIT: child stages/commits/pushes NOTHING (`git diff --cached`
   empty at verdict; IO is the sole git gatekeeper).

Anything else — any FAIL line, probe missing/refusing, banner missing,
probe computing from hard-coded spec constants, node --check failure,
build error, unregistered dirty path, engine-file diff — is FAIL, with
per-item reasons: every failed item ID + measured value vs floor, cited
in `io/reports/2026-11-07-cc-h6-remains-validation.md` (one line per
CH/G/SR item; adjudications split blocking/non-blocking).

## AMBIGUITIES for IO to adjudicate BEFORE Devbot builds (do not silently interpret)

- A1: spec sec 5's `lair: { x: 0, y: 8 }` with sec 2's center
  (0,-1064) derives nest (0,-1056) — but the lairs row, the world
  comment, the K-mirror 16.0 m landing spacing, and sec 6's seat
  (0,-1060) all pin (0,-1060): the letters disagree by 4 m. Likely fix
  is `lair.y: 4`. The valspec enforces the SELF-CONSISTENCY law (CH-4:
  lairNest trio agrees, spacing 16.0 +- 0.5) over either letter; landing
  y:8 verbatim with center -1064 FAILS CH-4.
- A2: sec 2b's ring z-literals may carry H5-style +-drift vs a strict
  2dp re-derivation of `x = 30 sin((180-36k)deg), z = -1064 - 30
  cos((180-36k)deg)`; the rho == 30.0 +- 0.05 + chord <= 0.02 law
  governs (literals are context, per the CC-H5 SPEC-FIG-FIX).
- A3: lastchancel.minions carries NO `dieOnMasterDeath` (K's landed
  captain has true). Engine-safe (lairOnDeath reads it falsy-safe);
  recorded, not asserted — confirm intent.

VALSPEC LEAN BY DESIGN: probes + greps only, no harness/screen QA; the
G/SR ID lists double as the verdict checklist. Total items: 6 CH + 12 G
+ 4 SR = 22.
