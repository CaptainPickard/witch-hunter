# CC-H5 VALSPEC — The Tithe Vaults (regionK, delve strata V4 off the Spire Approach) — write BEFORE build

Round: 2026-11-07 wake. Validates the FROZEN spec
`io/specs/cc-h5-tithe-vaults-spec.md` against a Devbot build on
`feat/world-visuals` in `/tmp/wh-worldfeat`. Closest sibling: CC-H3 (wake
21's regionJ spire approach — same one-sided conn grammar, same clearance
law set, same probe lineage). Testerbot is INDEPENDENT: do not read
Devbot's dispatch transcript. Work ONLY in `/tmp/wh-worldfeat`; REPORT
FIRST to `io/reports/2026-11-07-cc-h5-tithe-vaults-validation.md`, then
verdict in your summary (RUNBOOK report-first law).

Item numbering here maps 1:1 to spec sec 6's V-0..V-12, wrapped by the
standard pre-state (BV-0), build-validation (BV-6) and verdict scaffolding
carried from the H3 valspec. Adversarial checks N-1..N-5 fold INTO V-items
(cited in the verdict per item) — a FAIL on an N-check fails its parent
V-item.

## BV-0 PRE-STATE (record raw, before touching anything)

- HEAD must be `1f7f904`. `git -C /tmp/wh-worldfeat log --oneline -1`
  recorded; `git status --porcelain` recorded: at spec time the dirty set
  is `io/specs/cc-h5-tithe-vaults-spec.md` + `scratch/cc-h5/` only;
  post-build additionally `io/specs/cc-h5-tithe-vaults-valspec.md`,
  `scratch/cc-h5/*`, `io/reports/*`. Any OTHER dirty path before the
  build = report + do not touch.
- `grep -c zealot prototype/js/CONFIG.js` == 0 and
  `grep -c tithe prototype/js/CONFIG.js` == 0 pre-build (recorded at
  HEAD `1f7f904`); both go non-zero only after Devbot's build lands.
- `grep -c zealot prototype/js/region-defs.js` == 0 pre-build; post-build
  region-defs.js may carry `tithe_vaults` strings (registration + conn[9])
  but NO `zealot` (the zealot is a CONFIG-only row).

## V-0 CONFIG PARSES + regionK/zealot/tithecaptain ROWS COMPLETE

- Pre AND post build: `node --check prototype/js/CONFIG.js` AND
  `node --check prototype/js/region-defs.js`: record PASS at HEAD
  `1f7f904` (expected) and post-build (required).
- CONFIG.js gains exactly ONE new top-level block `  regionK: {`:
  `grep -n "^  regionK: {" prototype/js/CONFIG.js` returns exactly one
  line; and exactly one `id: 'tithe_vaults'` line in the file.
- regionK key set EXACTLY spec sec 3's var-shape list: `id, name, center,
  groundRadius, groundY, groundColor, groundColor2, groundSeed, scatter,
  spawn, gravityY, fogColor, fogDensity, ambientLightLevel, door, enemies,
  lairs, rotLair, props`.
- Parse check (not eyeball), run from the worktree root; the probe's own
  shape, adapted into `scratch/cc-h5/solve_geometry.py`:

      node -e "global.window={};eval(require('fs').readFileSync('prototype/js/CONFIG.js','utf8'));var C=window.WH_CONFIG;var K=C.regionK;console.log(JSON.stringify({keys:Object.keys(K),K:K,zealot:C.enemy.zealot,cap:C.enemy.tithecaptain}))"

  Assert: every spec-sec-3 key exists and NO extra top-level keys beyond
  the set above.
- The zealot row carries every key of spec sec 2.1: `hpMax, moveSpeed,
  chaseSpeed, attackDamage, attackRange, attackCooldown, sightRadius,
  leashRadius, staggerTime, radius, aggroPingInterval, attackPhase, ai1`;
  the tithecaptain row carries every key of spec sec 2.2: `name, hp, dmg,
  speed, aggro, pattern, slamRadius, slamArcDeg, slamWindup, slamActive,
  slamRecover, slamCooldown, slamTrackDegPerSec, engageRange, cueDark,
  cueHot, scale, lair, lairRadius, rearm, loot, minions, radius,
  corpseLingerSec, maxCorpses, riseSec, barLiftM, ai1`. Value-level spot
  asserts from the parsed rows: zealot `hpMax === 60.0`,
  `sightRadius === 16.0`, `ai1.guardArcDeg === 50`; captain `pattern ===
  'boss-slam'`, `slamArcDeg === 100`, `slamTrackDegPerSec === 110`,
  `scale === 2.1`, `ai1.guardArcDeg === 45`, `cueHot === 0xd84a4a`.
- CONFIG.enemy body map additions (spec sec 2.3) asserted from the parsed
  object: `C.enemy.bodyByType.zealot === 'banditBody'`,
  `C.enemy.animVariantByType.zealot === 'bandit'`,
  `C.enemy.bodyByType.tithecaptain === 'banditBody'`,
  `C.enemy.animVariantByType.tithecaptain === 'bandit'`.

## V-1 conn[9] SHAPE (region-defs.js)

Mirror of conn[8]'s AMENDMENT A row, re-pointed J->K. Assert on the
EVALED object (probe adapted from `scratch/cc-h3/solve_geometry.py`'s
node-eval wrapper into `scratch/cc-h5/solve_geometry.py`; JS body):

    const fs = require('fs');
    global.window = {};
    eval(fs.readFileSync('prototype/js/CONFIG.js', 'utf8'));
    eval(fs.readFileSync('prototype/js/region-defs.js', 'utf8'));
    const C = window.WH_CONFIG, D = window.WH_REGION_DEFS;
    const conn = D.connections[9];
    console.log(JSON.stringify({K: C.regionK, c: conn, count: D.connections.length,
      J: C.regionJ, wall: C.boundaryWall ? C.boundaryWall.collider : null,
      forward: D.connectionBetween(C.regionJ.id, C.regionK.id) === conn,
      reverse: D.connectionBetween(C.regionK.id, C.regionJ.id) === conn,
      sideInK: D.sideIn(conn, C.regionK.id),
      sideOfPlaneK: D.sideOfPlane(conn, C.regionK.spawn.z),
      sideInJ: D.sideIn(conn, C.regionJ.id),
      planeInJ: D.planeIn(conn, C.regionJ.id),
      planeInK: D.planeIn(conn, C.regionK.id)}));

- `D.connections.length` === 10 post-build (was 9 at HEAD 1f7f904).
- `conn.from === CFG.regionJ.id ('veil_spire_approach')`,
  `conn.to === CFG.regionK.id ('tithe_vaults')`, `conn.axis === 'z'`,
  `conn.planeCoord === CFG.regionK.door.planeZ === -844`.
- `conn.door.doorX === 0`, `conn.door.doorHalfWidth === 2.2`,
  `conn.door.suspendDepthM === 0`, `conn.door.wallGapPadM === 0`,
  `conn.door.arch === null`, `conn.door.gatedTo === null`.
- `conn.door.walkFrom === 'tithe_vaults'` (ONE-SIDED: the walk-back plane
  exists ONLY from K; J keeps no walkFrom).
- `conn.door.interact.from === 'veil_spire_approach'`,
  `conn.door.interact.x === 7.5`, `conn.door.interact.z === -678`,
  `conn.door.interact.radius === 3.5`.
- `conn.door.land.veil_spire_approach` deep-equals
  `{ x: 2, z: -682, faceX: 2, faceZ: -700 }`;
  `conn.door.land.tithe_vaults` deep-equals
  `{ x: 0, z: -856, faceX: 0, faceZ: -880 }`.
- AMENDMENT A carries: `conn.door.fadeIn === 0.3`,
  `conn.door.fadeOut === 0.5`, `conn.door.exitFadeOut === 0.8`.
- Prompt VERBATIM: `conn.door.text.prompt ===
  'E - Descend into the tithe vaults'` (exact string, case and spacing;
  DISTINCT from conn[8]'s 'E - Descend toward the spire' — assert the
  two differ in the same probe).
- Registration line present in region-defs.js source:
  `grep -n "makeRegion(CFG.regionK, -1)" prototype/js/region-defs.js`
  returns exactly one hit.

## V-2 SIDES TABLE (the round's engine-law call, NOT adjudicable)

From the SAME probe object (sideInK / sideOfPlaneK / sideInJ / planeInJ /
planeInK fields above), asserting the SPEC sec 4 probe-law verbatim:

- `sideIn(connections[9], CFG.regionK.id) === sideOfPlane(connections[9],
  CFG.regionK.spawn.z) === -1` — K's interior (-880/-856) is SOUTH of the
  plane -844.
- `sides[J] === +1` — assert BOTH the evaluated table
  `conn.sides['veil_spire_approach'] === 1` AND the helper agreement
  `sideIn(conn, 'veil_spire_approach') === 1`.
- `connections[9].sides[CFG.regionJ.id] = +1;` and
  `connections[9].sides[CFG.regionK.id] = -1;` present in region-defs.js
  SOURCE:
  `grep -n "connections\[9\]\.sides\[CFG.regionJ.id\] = +1;" prototype/js/region-defs.js`
  and
  `grep -n "connections\[9\]\.sides\[CFG.regionK.id\] = -1;" prototype/js/region-defs.js`
  each return exactly one hit — quote these two lines in the report next
  to conn[8]'s precedent pair (`connections[8].sides[CFG.regionF.id] = -1;`
  / `connections[8].sides[CFG.regionJ.id] = +1;`, region-defs.js:306-307
  at HEAD 1f7f904).
- planeIn asymmetry (the one-sided law): `planeIn(conn,
  'veil_spire_approach') === false` (J carries no walkFrom) and
  `planeIn(conn, 'tithe_vaults') === true`.
- `forward === reverse === true` (connectionBetween resolves conn[9] in
  both directions).
- If `sideIn(9, K) !== sideOfPlane(9, K spawn -856)` or the J side is not
  +1: FAIL and quote region-defs sideOfPlane/sideIn definitions — this is
  spec sec 4's central decision, NOT a non-blocking adjudication.

## V-3 CLEARANCE PROBE (fresh run, CONFIG-PARSED — zero hard-coded spec numbers)

Devbot writes `scratch/cc-h5/solve_geometry.py` (adapted from
`scratch/cc-h3/solve_geometry.py` — the newest landed lineage: node-evals
the LIVE regionK/regionJ blocks + conn[9], rebuilds ring colliders per
the region-manager whPropColliders law: circles of radius
`CONFIG.boundaryWall.collider.r` (0.45) along each whWall row's local X,
`wall`-count per row, axis length 1.899 (WIDTH map 'whWallA': 1.899,
'whWallB': 1.899), at `y: -0.2`). Testerbot RE-RUNS it fresh; every check
reads LANDED values. Run from the worktree root:
`python3 scratch/cc-h5/solve_geometry.py`. Law set (thresholds from spec
sec 5/6; expected values in parens are the IO pre-audit's arithmetic, the
probe is the truth; a probe computing them hard-coded fails this item):

- Ring integrity: exactly 10 whWall rows (whWallA/B alternating starting
  whWallA), each `wall: 10`, `scale 11.067`, `sy` 11.69 (A) / 11.55 (B),
  `sz 2.40`, `y: -0.2` — ring colliders = 10 x 10 = 100 circles of
  r 0.45. Closed ring: centers on the r34 circle at k*36 deg from north,
  x = 34*sin(k*36deg), z = -880 - 34*cos(k*36deg), rounded 2dp (recompute
  from LANDED rows; rho tolerance 0.05 — north row (0,-846) exact, south
  row (0,-914) exact).
- Ring closure against the SPEC's table only as CONTEXT: the landed rows
  are authoritative. NOTE for the report: sec 3's z-literals carry
  +-0.29..2.01 rounding drift vs a strict 2dp re-derivation (e.g. row 2
  literal -867.48 vs re-derived -869.49; adjacent-chord targets 21.0132,
  re-derived 21.008..21.020). This drift is a SPEC-annotation arithmetic
  quirk, NOT a build blocker: the assert is rho == 34.0 +- 0.05 for all
  10 landed rows + inter-row chord uniformity within 0.02, not literal
  equality with sec 3's table. If the probe instead asserts literal
  sec-3 equality, that probe design is the bug — flag it.
- Door lane: walk-back lane `|x| <= 2.2` at z-plane -844 (K's planeZ):
  nearest ring collider edge >= 1.0 m (the north-point row (0,-846)
  expected nearest, spec quote 1.55 m); ZERO colliders overlapping the
  lane window within 0.5 m (lane window = |x| <= 2.7, z within 0.5 of
  -844). Also assert the lane is on the walk-EXIT side: the plane -844
  sits 12 m inside the north rim -846 and the spawn (0,-856) is 12 m
  south of the plane (ADJ-E geometry, probe-derived).
- K enemies (5 rows: 3 zealot + 2 ghoul, from the LANDED regionK.enemies):
  each >= 8.0 m from spawn (0,-856) AND from `land.tithe_vaults`
  (0,-856) (same seat by coordinate); mutual >= 12.5 (spec quote min
  14.2); >= 4.45 ring walk-clear (`34 - rho`); >= 5.0 from EVERY non-ring
  prop row center. Note the spec's sec-5 'every K prop >= 32' line is a
  pre-audit summary of the spawn-vs-PROP floor (the nearest prop to
  spawn/land is the okRuinColumn colossus at (0,-876): 20.0 m), while
  the >= 32 m figure describes the whole-ring minimum — the V-3 law
  floor is >= 5.0 per spec sec 6; record the computed minima for both
  (spawn-to-prop-min and whole-prop-min-to-nearest-enemy) and FAIL only
  the sec-6 floors.
- Boss seat: largest collider-edge clear circle at (0,-872) >= 6.0 m
  (the gate trio + statues are intended blockers; the captain reads
  around them) — the H3 AMEND-1 threshold, applied at K's dais
  (spec quote: binding obstacle is zealot (0,-865) at 7.0 m). Exclude
  NO category: blockers = all prop colliders (non-ring rows with the
  ASSET footprint radii per the measured-footprint table the cc-h2/h3
  lineage uses: mourningStatue 0.9, stoneSteps 1.1, okRuinColumn 1.15,
  lanternPost 0.5, blightcap 0.8, skullPile 0.9, mossBoulder 1.5;
  DISCLOSE the map used) + ring colliders (r 0.45) + ALL enemy seats
  (zealot/ghoul seats at their CONFIG rows). Report the computed radius
  AND the binding obstacle row.
- J-side hook (7.5,-678) r 3.5, parsed from LANDED
  regionK.door.interact: verify clear of J's LANDED rows (recompute from
  the LIVE regionJ block — never from the spec's sec-5 quotes):
  >= 4.5 from every J prop (spec quote nearest: mossBoulder (0,-672)
  9.60), >= 5.0 from every J enemy (sec quotes 30.92/37.50 plus zealot
  rows if any), >= 5.0 from J's tithecaptain/scarreader seats and lair
  rows (spec quote scar-reader seat 31.89), >= 4.5 from J's land rows
  (spec quote land-in (0,-730) 52.54), and the hook does NOT sit in J's
  own conn[8] walk-out lane: `abs(hook.x) > J.door.doorHalfWidth` at J's
  planeZ -738 (spec quote: hook x 7.5 outside |x| <= 2.2 — verify
  against J's LANDED door block, not the quoted numbers).
- J-side land row (2,-682) parsed from LANDED
  regionK.door.land.veil_spire_approach: >= 6.0 from every J prop (spec
  quote nearest: mossBoulder 6.32 — a 0.32 margin, so the probe must
  re-derive from live rows; a 2dp round-off in a copied J table would
  flip this check), >= 5.0 from every J enemy; sits inside J's disc
  (rho from J center (0,-700) with margin) and 20 m south of J's own
  walk-out plane -662 wait — check the plane-vs-land geometry: land
  z -682 vs J plane -662... 

  CORRECTION during drafting: J's landed walk-out plane is -662 (the
  F/J tomb-mouth, CONFIG.js:1614), NOT -738 (that is J's conn[8] far-wall
  plane). Spec sec 6's '20 m north of J's own walk-out plane (-662)' —
  land-in (2,-682) is 20 m SOUTH of -662 in z terms; assert |(-682) -
  (-662)| === 20 exactly, and that the land row is on J's INTERIOR side
  of that plane per J's landed door grammar. (The sec-5 line 'J-side land
  (0,-730) 52.54' refers to the conn[8] far-wall land row (0,-730);
  both J land rows are checked, each against the corresponding plane's
  lane if in its window — neither sits in a |x| <= 2.2 lane window
  (x 7.5 and x 2 are both OUTSIDE except x=2... ) 

  FINAL LAW: for each of J's two planes (-738 conn[8] far-wall and
  -662 conn[7] F/J mouth), assert the K-originated hook/land rows are
  NOT inside that plane's lane window (|x| <= 2.2 + 0.5, |z - planeZ|
  <= 0.5). Hook (7.5,-678): |x| 7.5 > 2.7 BOTH planes. Land (2,-682):
  |x| 2 < 2.7 for both lanes BUT |z - (-662)| = 20 > 0.5 and
  |z - (-738)| = 56 > 0.5, so it is out of both lane WINDOWS — the
  lane-window assert (not a bare |x| test) is what keeps this correct;
  assert it per-plane exactly as computed here.
- Walk-out land INTO K (0,-856): every K non-ring prop >= 32 by center
  distance? NO — law floor is the sec-6 set: nearest prop >= 5.0 (spec
  sec 6 'vs props >= 5'), and the >= 32 m reading is the sec-5 summary
  line. Record both readings; FAIL only on >= 5.0 (nearest expected:
  okRuinColumn (0,-876) at 20.0 — passes both readings, so the 32-figure
  is informational and any probe FAILING the 32 reading is over-strict:
  flag, don't block).
- K-tol band: K's north rim -846 vs J's ring south point row (0,-740):
  106 m gap (sec 5 last item, sec 3 comment) — probe-derived:
  `abs(-846 - (-740)) === 106` within 0.5 (the one-active-region
  tolerance band swallows it; non-blocking).

CORRECTION LEDGER (spec-author arithmetic quirks the validator must NOT
inherit as law): (a) sec 3/5's ring z-literals drift up to ~2.0 m from a
strict re-derivation — rho-matching to the r34 circle is the law, not the
literals; (b) 'every K prop >= 32' (sec 5, walk-out land INTO K) cannot
hold as stated (nearest prop 20.0 m) — the governing floor is sec 6's
>= 5.0; (c) sec 5's 'land-into-J (2,-682) ... 20 m north of J's own
walk-out plane (-662)' reads 20 m SOUTH in z — the assert is the
arithmetic distance |dz| === 20, not the direction word 'north'; (d) the
sec 5 line 'land->ring colliders >= 9' computes 34 - rho(land) - 0.45 =
9.55 only for the NORTH row from (0,-856): assert >= 9 as the nearest
ring-collider-edge distance from the land row, north row expected
binding. Where a spec sec-5 quote and a sec-6 V-item disagree, the V-item
floor governs; record both numbers in the report.

## V-4 regionJ BLOCK BYTE-IDENTICAL to HEAD@1f7f904

- Extract the regionJ block from HEAD and post-build, cmp:

      git show 1f7f904:prototype/js/CONFIG.js | awk '/^  regionJ: \{/,/^  \},$/' > /tmp/j_head.txt
      awk '/^  regionJ: \{/,/^  \},$/' prototype/js/CONFIG.js > /tmp/j_new.txt
      cmp /tmp/j_head.txt /tmp/j_new.txt

  Must be byte-identical (block close anchor is the FIRST `^  \},$` after
  the block open; regionJ opens at line 2115 and closes at line 2221 at
  HEAD 1f7f904 — pin by CONTENT ANCHOR `  regionJ: {`, not line number).
- No J rows added/removed/moved: J's props count (26 rows: 15 non-ring +
  10 ring+1? — record the exact landed count from the parse: non-ring
  asset tally from V-6's method applied to J), enemies count (8 rows
  incl. the scar-reader), door block, and rotLair unchanged. J-side
  clearances in V-3 are checked against these LANDED rows.
- `grep -n "makeRegion(CFG.regionJ" prototype/js/region-defs.js`
  returns exactly one hit, unchanged shape.

## V-5 FRESH SEED + REGION CONSTANTS

- `regionK.groundSeed === 448271909` and differs from every
  groundSeed/textureSeed in CONFIG. Assert against the parsed CONFIG,
  not a hard-coded list — collect ALL of them generically and assert
  448271909 is absent from the collected set:

      node -e "global.window={};eval(require('fs').readFileSync('prototype/js/CONFIG.js','utf8'));var C=window.WH_CONFIG;var seen=[];var walk=(o,path)=>{for(var k in o){var v=o[k];if(typeof v==='object'&&v!==null)walk(v,path.concat(k));else if(/groundSeed|textureSeed/.test(k))seen.push(path.concat(k).join('.')+'='+v)}};walk(C,[]);console.log(seen.join('\n'))"

  Every printed line's value !== 448271909, and regionK's own line reads
  regionK.groundSeed=448271909. (Landed inventory at HEAD 1f7f904, for
  the record: C 1662061217, D 1662061218, E 1662061219, F 1662061329,
  G 1662061440, H 1662061651, I 1662061654, J 1662061763 — plus
  textureSeeds 20261012, 20261013, 20261208?, rotLair pools' textureSeed
  448271910 (J's) — J's rotLair textureSeed is 448271910 at HEAD: the
  +1 sister of K's groundSeed 448271909. This is NOT a collision with
  the K groundSeed (different keys), but the probe asserts K's
  rotLair.pool.textureSeed === 448271910 too and that it differs from
  J's IF J's equals it... — record the collected list; the LAW is: K's
  groundSeed 448271909 unique among ALL ground/texture seeds, AND K's
  rotLair textureSeed NOT equal to J's rotLair textureSeed 448271910
  ... FINAL LAW: assert K.groundSeed unique among all groundSeed and
  textureSeed values; assert K.rotLair.pool.textureSeed !==
  J.rotLair.pool.textureSeed. (If the build reuses 448271910 for K's
  pool, that IS the J-mirror convention; the uniqueness law binds ONLY
  the groundSeed.)

Hmm, wait — resolve this properly. The sec-3 spec row:
`textureSeed: 448271910` for K's rotLair pool vs J's landed rotLair
`textureSeed: 448271910` (CONFIG.js:2174 at HEAD). THE SPEC SPECIFIES
the SAME textureSeed as J's landed pool. J's landed pool textureSeed
reads 448271910 at line 2174. So K's pool reuses J's pool textureSeed
deliberately? The spec sec 6 V-5 law says 'groundSeed 448271909 differs
from every other groundSeed/textureSeed in CONFIG' — it constrains ONLY
the groundSeed. So:

  FINAL LAW (V-5, clean form): (1) `regionK.groundSeed === 448271909`;
  (2) the generic walk shows no OTHER key (groundSeed or textureSeed,
  anywhere in CONFIG) carrying 448271909; (3) `regionK.groundY === 0`,
  `regionK.scatter === false`, `regionK.gravityY === -22` from the
  parsed regionK. No assertion on rotLair textureSeed beyond recording
  it (spec sec 3 fixes it at 448271910, same value as J's landed pool
  seed 448271910 — record the J/K pool-seed pair for IO's interest; the
  V-5 law constrains only groundSeed).

## V-6 ONE CRIMSON ACCENT FAMILY (lanternPost x1 + blightcap x2 + the lair dressing)

- From the parsed regionK props rows (excluding whWall ring rows):
  `lanternPost` count === 1 (the ONE crimson lamp, row (-13,-882));
  `blightcap` count === 2 (rows (-13,-868), (13,-868)). Assert by asset
  tally from the parsed rows:

      node -e "global.window={};eval(require('fs').readFileSync('prototype/js/CONFIG.js','utf8'));var p=window.WH_CONFIG.regionK.props;var t={};p.forEach(r=>t[r.asset]=(t[r.asset]||0)+1);console.log(JSON.stringify(t))"

- No other colored-light/colored-cap rows in regionK: the remaining
  non-ring prop assets are exactly { mourningStatue x4, stoneSteps x2,
  okRuinColumn x3, skullPile x2, mossBoulder x1 }. Total non-ring prop
  rows === 13 (4+2+3+1+2+1); total props incl. ring === 23 (13 + 10
  whWall rows). NOTE vs sec 3's props list: sec 3 lists 16 non-ring rows
  (4 statues + 2 steps + 3 columns + 1 lantern + 2 caps + 2 skulls +
  1 boulder = 15) — recount from the SPEC literally: 4+2+3+1+2+2+1 =
  15 non-ring rows, +10 ring = 25 total. The tally line above is the
  truth source; the spec's prose count is annotation. FINAL: non-ring
  = 15 rows { mourningStatue x4, stoneSteps x2, okRuinColumn x3,
  lanternPost x1, blightcap x2, skullPile x2, mossBoulder x1 }, total
  25.
- Crimson-family completeness: the tithecaptain's LAIR dressing rides
  regionK.rotLair (the H4 scar-pool pattern): `regionK.rotLair.light.color
  === 0xd85050` (the ONE crimson family's engine half), `pool.color ===
  0x1a0f12`, `pool.color2 === 0x2a1116`, `pool.speck === 0x5a2028`,
  `pool.radius === 8`, `pool.rings === 5`, `fog.showWithinM === 70`,
  `cullM === 170`. Assert from the parsed regionK.rotLair.
- Pin by content anchor (the asset keys), not line numbers.

## V-7 regionI + connections[7]/[8] BYTE-IDENTICAL to HEAD@1f7f904

- regionI block byte-identity (same extract recipe as V-4):

      git show 1f7f904:prototype/js/CONFIG.js | awk '/^  regionI: \{/,/^  \},$/' > /tmp/i_head.txt
      awk '/^  regionI: \{/,/^  \},$/' prototype/js/CONFIG.js > /tmp/i_new.txt
      cmp /tmp/i_head.txt /tmp/i_new.txt

  (regionI opens at line 2036 and closes at line 2113 at HEAD
  1f7f904 — anchor `  regionI: {`.)
- conn rows 0..8 in region-defs.js byte-identical to HEAD: extract the
  source span from the file's first `connections.push` through the
  `connections[8].sides[CFG.regionJ.id] = +1;` line in both HEAD and
  worktree, cmp:

      git show 1f7f904:prototype/js/region-defs.js | awk '/connections\.push\(/,0' ...

  — the simplest robust form: find the byte offset of the first
  `connections.push` and the line number of
  `connections[8].sides[CFG.regionJ.id] = +1;` in both versions, then
  head -c/line-window cmp. Exact commands:

      head=$(git show 1f7f904:prototype/js/region-defs.js)
      ln_head=$(printf '%s' "$head" | grep -n 'connections\[8\]\.sides\[CFG.regionJ.id\] = +1;' | cut -d: -f1)
      ln_new=$(grep -n 'connections\[8\]\.sides\[CFG.regionJ.id\] = +1;' prototype/js/region-defs.js | cut -d: -f1)
      # span = from the LAST 'makeRegion(CFG.regionI, -1)' line? No — from the first
      # conn push to the conn[8] J-side line, INCLUSIVE, in both files:
      printf '%s' "$head" | sed -n "$(printf '%s' "$head" | grep -n 'connections\.push' | head -1 | cut -d: -f1),${ln_head}p" > /tmp/conn_head.txt
      sed -n "$(grep -n 'connections\.push' prototype/js/region-defs.js | head -1 | cut -d: -f1),${ln_new}p" prototype/js/region-defs.js > /tmp/conn_new.txt
      cmp /tmp/conn_head.txt /tmp/conn_new.txt

  The new round's text (regionK registration, conn[9] push + sides)
  must appear only AFTER the conn[8] J-sides line.
- `grep -c "connections\[9\]" prototype/js/region-defs.js` counts BOTH
  new source rows (push body reference + 2 sides lines appear inside the
  block; the sides lines are the only `connections[9].` accesses) —
  record the count and its composition (registration line covered in
  V-1; the sides lines covered in V-2).
- `grep -n "makeRegion(CFG.regionI, -1)" prototype/js/region-defs.js`
  unchanged and still exactly one hit; same for
  `makeRegion(CFG.regionJ, -1)` (V-4).

## V-8 SURFACE DISCIPLINE (the round touches CONFIG.js + region-defs.js ONLY)

- `git status --porcelain` at verdict: ONLY
  `prototype/js/CONFIG.js`, `prototype/js/region-defs.js`,
  `scratch/cc-h5/*`, `io/reports/*`, `io/specs/*` (spec + valspec).
  ANY other touched path = FAIL. Explicitly: no
  prototype/js/{enemy,game,save,region-manager,daynight}.js, no CSS/HTML,
  no assets/, no prototype/builds/* changes.
- Explicit byte-identity asserts on the named no-touch files:

      git diff 1f7f904 -- prototype/js/enemy.js prototype/js/game.js prototype/js/save.js prototype/js/region-manager.js prototype/js/daynight.js prototype/index.html

  must be EMPTY.
- Traps hazard primitive NOT landed (spec sec 1: out of this round):
  `grep -c "hazard" prototype/js/CONFIG.js` unchanged from HEAD value
  (record the HEAD value; the delta must be zero).

## V-9 ZEALOT WIRED ENGINE-SIDE WITHOUT ENGINE EDITS

- `C.enemy.zealot` exists and is truthy (from the V-0 probe object).
- Body map asserted in V-0 (banditBody / bandit for zealot AND
  tithecaptain).
- cfgFor fall-through: a node eval of the cfgFor-logic EQUIVALENT (the
  spec's framing: the row has NO `pattern` key -> the row is returned
  as-is, no slam key rewrite, ai1 survives intact):

      node -e "global.window={};eval(require('fs').readFileSync('prototype/js/CONFIG.js','utf8'));var z=window.WH_CONFIG.enemy.zealot;console.log(JSON.stringify({truthy:!!z,hasPattern:('pattern' in z),hasSlamKeys:Object.keys(z).filter(k=>/^slam/.test(k)),ai1Survives:!!(z.ai1&&z.ai1.guardArcDeg===50)}))"

  Assert truthy === true, hasPattern === false, hasSlamKeys empty list,
  ai1Survives === true.
- Enemy.js consumption is GENERIC (no engine edits — V-8's diff is
  empty proves it); quote the consumption lines for the record from
  HEAD enemy.js:152 (`this.lair = this.cfg.pattern === 'boss-slam' &&
  this.cfg.lair ? newLair(this.cfg) : null;`) — the zealot (no pattern
  key) gets `this.lair === null` and `ai1For` reads `cfg.ai1`
  independent of pattern. NO build-side engine change is needed or
  allowed.

## V-10 TITHECAPTAIN WIRED (boss-slam + lair + minions + loot + ai1)

- `C.enemy.tithecaptain` exists; `pattern === 'boss-slam'` (V-0 spot
  assert covers it; record here too).
- lairNest derivation — the ENGINE's own formula (enemy.js:1243-1247 at
  HEAD 1f7f904): nest = region.center + lair offset. Assert from a
  dedicated probe (the sign law: lair.x adds to center.x, lair.y adds to
  center.z):

      node -e "global.window={};eval(require('fs').readFileSync('prototype/js/CONFIG.js','utf8'));var C=window.WH_CONFIG,L=C.enemy.tithecaptain.lair,R=C['region'+L.region];var nest={x:R.center.x+L.x,z:R.center.z+L.y};var row=C.regionK.lairs.find(l=>l.type==='tithecaptain');console.log(JSON.stringify({lair:L,nest:nest,lairsRow:row,match:nest.x===row.x&&nest.z===row.z}))"

  Assert: `L.region === 'K'`, resolve path `C['regionK']` exists, nest
  === { x: 0, z: -872 }, the lairs row { type: 'tithecaptain', x: 0,
  z: -872 } exists in regionK.lairs, and match === true. The save-letter
  law: `L.flagPrefix === 'tithecaptain'` and the letter law
  (`lairFlagPrefixed` at enemy.js:1691 emits
  `(prefix || 'rotmother') + '_cleared_' + region-letter`) — assert the
  composition law holds by the regionK letters: the K row's letter comes
  from the lair region 'K', so key === 'tithecaptain_cleared_K'; quote
  enemy.js:1691 and the scarreader precedent (CONFIG.js:2947-2950: the
  scarreader_cleared_J shape) for the record. The lars/letter check is
  a STATIC composition assert (prefix + '_cleared_' + 'K'), not an eval
  of enemy.js internals.
- minions: `L.minions.asset === 'zealot'`, `cap === 2`,
  `interval === 7.0`, `range === 5.0`, `dieOnMasterDeath === true`.
- loot: `L.loot` deep-includes `[{ mat: 'stolenCoin', n: [1, 3] }]`;
  AND CFG.items.stolenCoin exists: `!!C.items.stolenCoin === true`
  (IO's node eval precedent; item id, name 'Stolen Coin', glyph 'SC').
- ai1 present (the guard machine rides): `L.ai1` truthy with
  `guardArcDeg === 45` (smaller readable window than the zealot's 50 —
  the spec sec 2.2 comment law).
- rearm: `L.rearm.days === 3`, `trigger === 'proximity'`,
  `radius === 14`; `lairRadius === 16` (record; consumption is engine
  law per HEAD enemy.js, no edits).

## V-11 FOG/DARKNESS MATH

- Dense-fog d95 law: `d95 = sqrt(-ln 0.05) / fogDensity`. Probe
  computes from the PARSED regionK (no hard-coding):

      node -e "global.window={};eval(require('fs').readFileSync('prototype/js/CONFIG.js','utf8'));var K=window.WH_CONFIG.regionK;var d=Math.sqrt(-Math.log(0.05))/K.fogDensity;console.log(JSON.stringify({density:K.fogDensity,d95:d}))"

  Assert: density === 0.16, d95 within [10.77, 10.87] (10.8176 +- 0.05
  rounding tolerance, spec sec 3 comment: 'one stratum quieter than J's
  11.61'; J's landed fogDensity 0.15 -> 11.6179 — record the J value
  from the parse for the chain comparison).
- Chain monotonicity from the parse: `regionK.ambientLightLevel (0.045)
  < regionJ.ambientLightLevel (0.05) < regionF.ambientLightLevel
  (0.055)` as STRICT inequalities on the parsed values; J/F values
  byte-protected by V-4/V-7 block identity.
- `regionK.fogColor === 0x0a0810` (the veil fog family, same constant
  as J's landed fogColor).

## V-12 ZEALOT SEATS LIVE ONLY IN K; NO K/J ROW COLLISION

- K's enemies/hooks live only in regionK: from the V-0 probe, count
  `zealot` rows across ALL regions' enemies arrays —

      node -e "global.window={};eval(require('fs').readFileSync('prototype/js/CONFIG.js','utf8'));var C=window.WH_CONFIG;var out={};Object.keys(C).filter(k=>/^region/.test(k)).forEach(k=>{var r=C[k];var z=(r.enemies||[]).filter(e=>e.type==='zealot').length;tally...});"

  — assert regionK carries exactly 3 zealot rows and every other region
  carries 0; `grep -c zealot prototype/js/CONFIG.js` counts ONLY the
  enemy-row keys + body-map rows (record composition; BV-0's pre-count
  was 0). region-defs.js carries NO zealot string (grep -c === 0).
- No K row collides with J's rows: the V-3 probe computes min distances
  from every K-originated seat (hook 7.5,-678; land-in 2,-682) to
  J's props/enemies/lairs — all >= their V-3 floors; the tol band
  (K north rim -846 vs J south ring row (0,-740), 106 m) is
  probe-derived and recorded (the one-active-region tolerance band
  swallows it; non-blocking per spec sec 5).
- Cross-region z-order sanity from the parse: all K rows' z <= -846 and
  all J rows' z >= -740 (the 106 m tol band holds as a STRUCTURAL gap,
  not just the north-rim pair: record min-K-z and max-J-z from the full
  row sets).
- Cross-region z-order sanity from the parse (second form, the ring
  extremes): max z of K's non-ring rows <= -846 (K interior is south of
  its rim) and min z of J's non-ring rows >= -740 (J interior is north
  of its south ring point); record both extremes.
- Probe adaptation deltas from the cc-h3 lineage and footprint-map
  disclosure are NON-BLOCKING adjudication classes (H3 verdict
  precedent).

## N-1..N-5 ADVERSARIAL CHECKS (fail-closed against the round type's likely build mistakes)

Each N-item names the mistake and the SPECIFIC check that catches it;
a FAIL on an N-check fails its parent V-item (the parent is named) and
shows in the verdict's adjudications as blocking.

- N-1 CONFIG row-key drift vs engine consumption. The build renames or
  omits a key the ENGINE reads generically (hpMax vs hp-style naming in
  the zealot row: engine cfgFor maps hp/dmg/speed/aggro for pattern rows
  but the TRASH rows use hpMax/moveSpeed; bodyByType/animVariantByType
  misspellings — 'banditBody' vs 'banditbody', or the captain's
  animVariant omitted on the symmetry-law assumption that the fallback
  covers it). CATCH: the V-0 parse asserts EVERY sec-2 key by name and
  the four body-map rows by exact value (`bodyByType.zealot ===
  'banditBody'`, `bodyByType.tithecaptain === 'banditBody'`,
  `animVariantByType.zealot === 'bandit'`,
  `animVariantByType.tithecaptain === 'bandit'`) — a missing/spelled
  row fails V-0 and V-9; the zealot's hpMax key shape is asserted
  against the sec-2.1 list, and a build that renames hpMax to hp on
  the zealot ALSO fails V-9's hasPattern/hasSlamKeys probe (a hp-key
  rename does not trip it, but the V-0 key-list check does). Spot
  values (guardArcDeg 50 vs 45 distinguishing the rows) catch cross-
  row copy-drift.
- N-2 Ring-row arithmetic drift from the spec literals vs probe
  re-derivation. Two ways to build this wrong: (a) hard-code sec 3's
  table into the probe instead of re-deriving (then a spec-literal
  drift becomes a false PASS), or (b) build ring rows whose CENTERS
  match sec 3's drifted literals rather than the r34 circle (then the
  probe's rho check fails). CATCH: the V-3 probe MUST re-derive all
  ten rows from the LANDED CONFIG rows (rho == 34.0 +- 0.05 for all 10
  landed rows + inter-row chord uniformity within 0.02) — asserted
  against the r34 circle law, NEVER against sec 3's literals; and the
  VALIDATOR re-runs the probe twice (once fresh, once after
  `git stash` of nothing — just twice for determinism) and diffs the
  two outputs. Ring rotation-direction drift (clockwise vs counter-
  clockwise: x = +sin vs -sin) is caught by the rotY law
  (rotY = 3.14 + k*0.6283 with row order N->E->S->W; assert rotY
  increases monotonically with row index AND x-sign follows
  north->east positive). The spec-literal z-drift ledger note (V-3
  correction ledger items (a)-(c)) explains why the literals are not
  the truth source.
- N-3 J-region contamination. The build adds rows to J, moves J rows,
  or (subtler) adds the hook/land seats INTO J's props/enemies rather
  than leaving them on the K block/conn[9]. CATCH: (a) V-4's cmp of
  the extracted regionJ block is byte-identical; (b) V-8's empty diff
  range covers region-defs above the conn[9] span (V-7's span cmp);
  (c) the V-12 region-census probe asserts 3 zealot rows in K and 0
  zealot rows in every other region; (d) J's asset tally from the
  parsed regionJ (V-6's method applied to J) matches HEAD's tally
  exactly (record HEAD's J tally at BV-0: mourningStatue x4,
  stoneSteps x2, okRuinColumn x3, blightcap x2, lanternPost x1,
  skullPile x2, tally check
  `node -e "...;var p=HEAD-regionJ.props..."` — the probe extracts
  HEAD's regionJ from a `git show 1f7f904:...` eval for the tally +
  the live one, and cmp of the two tallies is the catch).
- N-4 lair.lairNest offset sign errors. The classic: `lair: { x: 0,
  y: 8 }` interpreted as world-or-negated (nest at (0,-888) if y is
  treated as world-z, or (0,-884)?? no — center +8 => -872; the mistake
  shapes: nest at (0, -888) [y treated as a southward offset] or
  (0,-880) [y ignored]). CATCH: the V-10 probe computes the nest by
  the ENGINE's OWN formula (`R.center + {x: lair.x, z: lair.y}` =
  (0,-872)) and requires `nest.x === row.x && nest.z === row.z` where
  row is regionK.lairs' tithecaptain row (0,-872); plus the V-3
  boss-seat clear-circle check runs at the lair row seat (0,-872) — a
  misplaced nest (0,-888) would ALSO fail V-3's boss-seat check
  ((0,-888) is 2 m inside the statue line at z -896/-888: the clear
  circle there would collapse... record the probe's binding obstacle
  at the ROW seat (0,-872) — the zealot (0,-865) at 7.0 m — and note
  that a nest at (0,-888) would bind at mourningStatue (6,-888) at
  6.0 m, which still passes >= 6.0 trivially... the REAL catch is the
  nest==row equality plus the lairRadius 16 ring: the rearm/proximity
  radius 14 + lairRadius 16 at nest (0,-888) would swallow the spawn
  (0,-856): the probe asserts nest-vs-spawn = 16.0 ± tolerance and
  rearm.proximity radius 14 < 16 = spawn-to-nest... no — FINAL: the
  N-4 catch is exactly (i) the lairNest FORMULA probe
  (nest === (0,-872), matching the lairs row) with the sign law quoted
  (enemy.js:1245 `x: R.center.x + cfg.lair.x, z: R.center.z +
  cfg.lair.y`), (ii) nest-vs-spawn distance asserted === 16.0 within
  0.5 (the intended 12 m inside-north-rim + 4 m dais depth: spec sec 6
  V-10's derivation (0,-880)+(0,+8)), and (iii) the boss-seat clear
  circle computed AT the nest seat.
- N-5 sideIn sign errors. The classic conn[9] mistake: sides[K] = +1
  (copying conn[8]'s J-side +1 without the geometry), or sides[J] = -1,
  or the connect helper agreement broken
  (sideIn(9,K) !== sideOfPlane(9,-856)). CATCH: V-2's full law —
  sides[J] === +1, sides[K] === -1, sideIn(K) === sideOfPlane(K spawn
  -856) === -1, sideIn(J) === +1, planeIn(J) === false, planeIn(K)
  === true, plus the SOURCE-line grep pair (the +1/-1 assignment lines)
  and the conn[8] precedent pair quoted line-adjacent in the report.
  The geometry rationale in the report: K's interior (-880/-856) is
  SOUTH of the plane -844 (sideOfPlane: z > planeCoord ? 1 : -1 →
  -856 < -844 → -1), J's interior (-640..-740) is NORTH of it (+1) —
  and J is the POCKET PARENT (conn[7]/conn[8] convention: the
  parent-of-a-pocket convention gives the parent side +1 when the
  child's plane is a walk-back-only plane... quote sec 4's own
  rationale: 'J's plane is underground/inactive for this conn'). If any
  of the V-2 asserts fails, quote region-defs.js's sideOfPlane/sideIn
  definitions in the verdict — the round's central decision, NOT
  adjudicable.

## BV-6 BUILD VALIDATION — build is IO's; children NEVER build/push

- Children do NOT run `tools/build_v8.py` and do NOT commit. Validate
  whatever the worktree carries at verdict time:
  - If a pre-built v8 bundle with tithe markers exists:
    `grep -c 'tithe_vaults' prototype/builds/v8-playable.html` >= 8;
    record sha256.
  - If not present: record "no pre-built bundle at verdict time — IO
    builds at close-out" and the verdict rests on BV-0, V-0..V-12 and
    N-1..N-5.

## Verdict format

`io/reports/2026-11-07-cc-h5-tithe-vaults-validation.md` — BV-0,
V-0..V-12, N-1..N-5, BV-6 one line each (PASS/FAIL + raw numbers:
distances, rho margins, tallies, counts, cmp results, d95, seed list).
Adjudications section: deviations with blocking/non-blocking + reason.
PASS = all checks PASS, zero blocking. Expected NON-BLOCKING
adjudication classes: probe adaptation deltas from the cc-h3 lineage,
footprint-map disclosure for the boss-seat computation, the spec
sec-3/5 annotation quirks recorded in V-3's correction ledger
((a)-(d)), and the J/K rotLair textureSeed reuse (448271910) recorded
in V-5.

## Verdict PASS -> IO close-out (not the child's job)

IO: commit 1 = code + spec/valspec/report + doc 64 H5 ledger line +
GOALS tick; then `tools/build_v8.py` IN THE WORKTREE, marker check
(`tithe_vaults` >= 8), commit 2 (stamp), push both, release flip,
serve-verify (200 + marker grep on served bytes + cmp
served==worktree), journal, GOALS change-log.

---
READY FOR BUILD

Devbot build scope (exact): Build touches prototype/js/CONFIG.js and
prototype/js/region-defs.js ONLY (spec sec 1 two-file law: CONFIG.js +
region-defs.js) — no engine files, no assets, no CSS/html; the probe
goes to scratch/cc-h5/solve_geometry.py and the build note to
io/reports/2026-11-07-cc-h5-tithe-vaults-build.md per spec sec 8.

SUMMARY
File: /tmp/wh-worldfeat/io/specs/cc-h5-tithe-vaults-valspec.md
Items: 13 V-items (BV-0 + V-0..V-12 is 14 scaffolding items; V-0..V-12
= 13) + N-1..N-5 adversarial items = 18 total numbered items, 1:1 with
spec sec 6's V-0..V-12.
Ambiguities for IO to adjudicate BEFORE Devbot builds (do not silently
interpret): (1) sec 3's ring z-literals drift +-0.29..2.01 m from a
strict 2dp re-derivation of x = 34 sin(k*36deg), z = -880 - 34
cos(k*36deg) (e.g. row-2 z -867.48 vs re-derived -869.49) — is the
drift table a deliberate J-table transcription convention or spec
author arithmetic error? The valspec treats rho-on-r34 as the law. (2)
sec 5's 'Walk-out land INTO K (0,-856): every K prop >= 32' cannot
hold (nearest prop colossus (0,-876) is 20.0 m); the sec-6 V-3 floor
'vs props >= 5' governs; confirm the 32 figure is summary-only. (3)
sec 3's rotLair.pool textureSeed 448271910 equals J's LANDED pool
textureSeed 448271910 (CONFIG.js:2174) — intentional J-mirror reuse
or should K's pool seed be fresh? V-5's law constrains only the
groundSeed per spec sec 6; the pool seed is recorded, not asserted.
