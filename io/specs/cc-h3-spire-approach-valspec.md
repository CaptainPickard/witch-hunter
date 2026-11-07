# CC-H3 VALSPEC — The Spire Approach (regionJ pocket off the Erased Galleries) — write BEFORE build

Round: 2026-11-07 wake 21. Validates the FROZEN spec
`io/specs/cc-h3-spire-approach-spec.md` against a Devbot build on
`feat/world-visuals` in `/tmp/wh-worldfeat`. Closest sibling: CC-H2bV2
(wake 20's regionI armory_deep — same one-sided conn grammar, same
clearance law set). Testerbot is INDEPENDENT: do not read Devbot's dispatch
transcript. Work ONLY in `/tmp/wh-worldfeat`; REPORT FIRST to
`io/reports/2026-11-07-cc-h3-spire-approach-validation.md`, then verdict in
your summary (RUNBOOK report-first law).

Item numbering here maps 1:1 to spec sec 7's V-0..V-9, wrapped by the
standard pre-state (BV-0) and surface/build/verdict scaffolding carried
from the H2bV2 valspec.

## BV-0 PRE-STATE (record raw, before touching anything)

- HEAD must be `42ba377`. `git -C /tmp/wh-worldfeat log --oneline -1`
  recorded; `git status --porcelain` recorded: only `scratch/…` and
  `io/…` paths may be dirty; anything else = report + do not touch.
- `grep -c veil_spire_approach prototype/js/CONFIG.js` == 0 and
  `grep -c "regionJ" prototype/js/CONFIG.js` == 0 (pre-build state; both go
  non-zero only after Devbot's build lands).
- `grep -c veil_spire_approach prototype/js/region-defs.js` == 0 pre-build.

## V-0 CONFIG PARSES + regionJ ROW COMPLETE

- Pre AND post build: `node --check prototype/js/CONFIG.js` AND
  `node --check prototype/js/region-defs.js`: record PASS at HEAD
  `42ba377` (expected) and post-build (required).
- CONFIG.js gains exactly ONE new top-level block `  regionJ: {` with
  `id: 'veil_spire_approach'`. No second `veil_spire_approach` id anywhere:
  `grep -c "veil_spire_approach" prototype/js/CONFIG.js` returns exactly
  the regionJ block's own rows (id + walkFrom + land key + spawn comment
  references allowed; the assert is: exactly one `regionJ: {` block open,
  exactly one `id: 'veil_spire_approach'` line).
- regionJ key set EXACTLY spec sec 3: `id`, `name` ("The Spire Approach"),
  `center { x: 0, z: -700 }`, `groundRadius 40`, `groundY 0`,
  `groundColor 0x0d0f15`, `groundColor2 0x111318`, `groundSeed 1662061763`,
  `scatter: false`, `spawn { x: 0, z: -730 }`, `gravityY -22`,
  `fogColor 0x0a0810`, `fogDensity 0.15`, `ambientLightLevel 0.05`,
  `door { planeZ -738, doorX 0, doorHalfWidth 2.2, suspendDepthM 0,
  wallGapPadM 0, walkFrom 'veil_spire_approach', interact { from
  'veil_galleries', x 7.5, z -654, radius 3.5 }, land { veil_galleries:
  (2,-652 face 2,-644), veil_spire_approach: (0,-730 face 0,-700) },
  fadeIn 0.3, fadeOut 0.5, exitFadeOut 0.8, text prompt
  'E - Descend toward the spire' }`, then `enemies` and `props`.
- Parse check (not eyeball): a three-free node probe evaluates CONFIG.js
  and asserts every key above by value:
  `node -e "global.window={};eval(require('fs').readFileSync('prototype/js/CONFIG.js','utf8'));var J=window.WH_CONFIG.regionJ;console.log(JSON.stringify(J,null,1))"` — assert the full key list exists and no extra
  top-level keys beyond spec sec 3's set (`id, name, center, groundRadius,
  groundY, groundColor, groundColor2, groundSeed, scatter, spawn, gravityY,
  fogColor, fogDensity, ambientLightLevel, door, enemies, props`).

## V-1 conn[8] SHAPE (region-defs.js)

Mirror of conn[7]'s AMENDMENT A row, re-pointed F->J. Assert on the EVALED
object (three-free node probe per `scratch/cc-h2bv2/connection_probe.js`
lineage, adapted into `scratch/cc-h3/connection_probe.js`):

- `DEFS.connections.length` === 9 post-build (was 8 at HEAD).
- `conn = DEFS.connections[8]`; `conn.from === CFG.regionF.id
  ('veil_galleries')`, `conn.to === CFG.regionJ.id
  ('veil_spire_approach')`, `conn.axis === 'z'`,
  `conn.planeCoord === CFG.regionJ.door.planeZ === -738`.
- `conn.door.doorX === 0`, `conn.door.doorHalfWidth === 2.2`,
  `conn.door.suspendDepthM === 0`, `conn.door.wallGapPadM === 0`,
  `conn.door.arch === null`, `conn.door.gatedTo === null`.
- `conn.door.walkFrom === 'veil_spire_approach'` (ONE-SIDED: the
  walk-back plane exists ONLY from J; F keeps no walkFrom).
- `conn.door.interact.from === 'veil_galleries'`,
  `conn.door.interact.x === 7.5`, `conn.door.interact.z === -654`,
  `conn.door.interact.radius === 3.5`.
- `conn.door.land.veil_galleries` deep-equals
  `{ x: 2, z: -652, faceX: 2, faceZ: -644 }`;
  `conn.door.land.veil_spire_approach` deep-equals
  `{ x: 0, z: -730, faceX: 0, faceZ: -700 }`.
- AMENDMENT A carries: `conn.door.fadeIn === 0.3`,
  `conn.door.fadeOut === 0.5`, `conn.door.exitFadeOut === 0.8`.
- Prompt VERBATIM: `conn.door.text.prompt ===
  'E - Descend toward the spire'` (exact string, case and spacing).
- Registration line present in region-defs.js source:
  `grep -n "makeRegion(CFG.regionJ, -1)" prototype/js/region-defs.js`
  returns exactly one hit.
- `DEFS.connectionBetween('veil_galleries','veil_spire_approach') === conn`
  and the reverse lookup `connectionBetween('veil_spire_approach',
  'veil_galleries') === conn`.

## V-2 SIDES TABLE (the round's engine-law call, NOT adjudicable)

- `conn.sides['veil_galleries'] === -1` (the parent-of-a-pocket
  convention per conn[7]'s H-side row).
- `conn.sides['veil_spire_approach'] === +1`.
- Engine-consistency assertion (quote
  `prototype/js/region-defs.js` `sideOfPlane` — `z > planeCoord ? 1 : -1`,
  line ~340): `Logic.sideOfPlane(conn, -730) === +1` (J interior
  spawn/land z=-730 vs plane -738: -730 > -738 = +1) AND
  `Logic.sideIn(conn, 'veil_spire_approach') === +1` — the two must AGREE.
- F-side exception documented like conn[7]: F's interior (-640) is
  arithmetically +1 vs plane -738, but the table carries -1 by the
  pocket-parent law (the plane exists only from J: `planeIn(conn,
  'veil_galleries') === false`, `planeIn(conn,
  'veil_spire_approach') === true`). Assert BOTH the table value (-1) AND
  the planeIn asymmetry; quote conn[7]'s precedent lines
  (`connections[7].sides[CFG.regionH.id] = -1;` /
  `connections[7].sides[CFG.regionI.id] = +1;`) for the record.
- If `sideIn(8, J) !== sideOfPlane(8, J interior)`: FAIL and quote
  region-manager/region-defs lines — this is the spec sec 2/5 central
  decision, NOT a non-blocking adjudication.

## V-3 CLEARANCE PROBE (fresh run, CONFIG-PARSED — zero hard-coded spec numbers)

Devbot writes `scratch/cc-h3/solve_geometry.py` (adapted from
`scratch/cc-h2bv2/clearance.py` — the newest landed lineage: regex-parses
the LIVE regionJ/regionF blocks and region-defs conn[8], rebuilds ring
colliders per the region-manager whPropColliders law: circles of radius
`CONFIG.boundaryWall.collider.r` (0.45) along each whWall row's local X,
`wall`-count per row, axis length 1.899, at `y: -0.2`). Testerbot RE-RUNS
it fresh; every check reads LANDED values. Run from the worktree root:
`python3 scratch/cc-h3/solve_geometry.py`. Law set:

- Ring integrity: exactly 10 whWall rows (whWallA/B), each `wall: 9`,
  `scale 13.019`, `sy` 11.69 (A) / 11.55 (B), `sz 2.40`, `y: -0.2` — ring
  colliders = 10 x 9 = 90 circles of r 0.45. Closed ring: centers on the
  r40 circle at k*36 deg from north (recompute from landed rows).
- Door lane: walk-back lane `|x| <= 2.2` at z -738 (planeZ): nearest ring
  collider edge >= 1.0 m (the south-point row (0,-740) is expected
  nearest, spec quote 1.55 m); ZERO colliders overlapping the lane window
  within 0.5 m. (lane window = |x| <= 2.2 + 0.5, z within 0.5 of -738.)
- Ghouls (2, from the landed regionJ enemies rows): each >= 8.0 m from
  spawn (0,-730) AND from `land.veil_spire_approach` (0,-730) (same seat
  by coordinate); mutual >= 12.5 (spec quote 30.0); >= 4.45 ring
  walk-clear (`40 - rho`); >= 4.0 from EVERY ring collider edge. Also >=
  5.0 from every non-ring prop row (spec sec 3 comment: "NOT near the
  ghouls" for the lamp).
- Props-in-J (non-ring rows, all hand-placed): every row >= 4.0 raw of
  EVERY ring collider AND >= 4.0 ring walk-clear (`40 - rho`); >= 6.0 from
  spawn/land (0,-730); >= 5.0 from BOTH ghouls; >= 4.0 mutual between
  every prop pair (spec sec 4 law "every row >= 4.0 m mutual" — NOTE: this
  round HAS a prop-mutual law, unlike H2b's E-precedent exemption; no
  tableaux group is declared in spec sec 4, so NO exemption applies).
- F-side hook (7.5,-654) r 3.5, parsed from landed regionJ.door.interact:
  verify clear of F's landed rows (recompute from the LIVE regionF block):
  >= 4.0 from nearest F prop (spec quote mossBoulder (9,-650) 4.27);
  >= 4.0 from F ring colliders (spec quote 6.39); >= 5.0 from F ghouls
  (spec quote 18.1); >= 6.0 from F's own land rows (spec quote nearest
  (0,-650) 8.5). Assert the hook does NOT sit in F's own conn[5] walk-out
  lane: |7.5| > F's doorHalfWidth at F's plane (spec quote: hook x 7.5
  cannot cross the |x| <= 2.2 lane at z -662 — verify against F's landed
  door block, not the quoted numbers).
- F-side land row (2,-652): inside F's disc (rho from F center (0,-640)
  with margin), every F prop >= 6.0 (spec quotes: mossBoulder 7.3, statue
  12.1, blightcap 10.4), F ring colliders >= 4.0 (spec quote 10.5).
- conn sanity: from/to/axis/planeCoord/walkFrom/interact/land per V-1;
  sideIn(J) == sideOfPlane(J interior -730) == +1 asserted from the parsed
  conn object, not from constants.

## V-4 regionF BLOCK BYTE-IDENTICAL to HEAD@42ba377

- Extract the regionF block from HEAD and from the worktree post-build and
  cmp:
  `git show 42ba377:prototype/js/CONFIG.js | awk '/^  regionF: \{/,/^  \},$/' > /tmp/f_head.txt`
  `awk '/^  regionF: \{/,/^  \},$/' prototype/js/CONFIG.js > /tmp/f_new.txt`
  `cmp /tmp/f_head.txt /tmp/f_new.txt` — must be byte-identical (the block
  close anchor is the FIRST `^  \},$` after the block open; regionF opens
  at line ~1584 and closes at line ~1675 at HEAD — pin by CONTENT ANCHOR
  `  regionF: {`, not line number).
- No F rows added/removed/moved: F's props count, enemies count, door
  block, and conn[5] row all unchanged (conn[5] byte-identity is covered
  by V-7's conn[0..7] check).

## V-5 FRESH SEED + REGION CONSTANTS

- `J.groundSeed === 1662061763` and differs from every landed seed.
  Assert against the parsed CONFIG, not a hard-coded list:
  `node -e "...;var C=window.WH_CONFIG;['regionC','regionD','regionE','regionF','regionG','regionH','regionI'].forEach(k=>console.log(k,C[k]&&C[k].groundSeed))"` — every printed value !== 1662061763. (HEAD
  values for the record: C 1662061217, D ...218, E ...219, F ...1329,
  G ...1440, H ...1651, I 1662061654.)
- `J.groundY === 0`, `J.scatter === false`, `J.gravityY === -22`.

## V-6 ONE CRIMSON ACCENT FAMILY (lanternPost x1 + blightcap x2 ONLY)

- From the parsed regionJ props rows (excluding whWall ring rows):
  `lanternPost` count === 1 (the ONE crimson lamp, at spec row (-6,-724));
  `blightcap` count === 2 (spec rows (-12,-692), (12,-692)).
- No other colored-light/colored-cap rows in regionJ: the remaining prop
  assets are exactly { mourningStatue x4, stoneSteps x2, okRuinColumn x3,
  skullPile x2, mossBoulder x1 }. Total non-ring prop rows === 15
  (4+2+3+2+1+1+2). Assert by asset tally from the parsed rows:
  `node -e "...;var p=window.WH_CONFIG.regionJ.props;var t={};p.forEach(r=>t[r.asset]=(t[r.asset]||0)+1);console.log(JSON.stringify(t))"`.
- Pin by content anchor (the asset keys), not line numbers (V-6 lesson:
  sha windows rot when the file shifts).

## V-7 regionI + connections[7] BYTE-IDENTICAL to HEAD@42ba377

- regionI block byte-identity (same extract recipe as V-4):
  `git show 42ba377:prototype/js/CONFIG.js | awk '/^  regionI: \{/,/^  \},$/' > /tmp/i_head.txt`
  `awk '/^  regionI: \{/,/^  \},$/' prototype/js/CONFIG.js > /tmp/i_new.txt`
  `cmp /tmp/i_head.txt /tmp/i_new.txt` (regionI opens ~line 2036, closes
  ~line 2113 at HEAD — anchor `  regionI: {`).
- conn rows 0..7 in region-defs.js byte-identical to HEAD: extract the
  source span from the file's first `connections.push` through the
  `connections[7].sides[CFG.regionI.id] = +1;` line in both HEAD and
  worktree, cmp. The new round's text (regionJ registration + conn[8]
  push + conn[8] sides) must appear only AFTER the conn[7] sides lines.
- `grep -n "makeRegion(CFG.regionI, -1)" prototype/js/region-defs.js`
  unchanged and still exactly one hit for regionI.

## V-8 SURFACE DISCIPLINE (the round touches CONFIG.js + region-defs.js ONLY)

- `git status --porcelain` at verdict: ONLY
  `prototype/js/CONFIG.js`, `prototype/js/region-defs.js`,
  `prototype/builds/v8-playable.html` (ONLY if IO pre-built — see BV-6),
  `scratch/cc-h3/*`, `io/reports/*` (+ `io/specs/*` for spec/valspec).
  ANY other touched path = FAIL.
- Explicit byte-identity asserts on the named no-touch files:
  `git diff 42ba377 -- prototype/js/game.js prototype/js/region-manager.js prototype/js/save.js prototype/js/daynight.js` must be EMPTY.

## V-9 BOSS-TIER OPEN SPACE (largest clear circle at (0,-702) >= 12 m)

- In `scratch/cc-h3/solve_geometry.py` (same CONFIG-parsed run as V-3):
  compute the largest circle centered at (0,-702) whose boundary touches
  the nearest obstacle, excluding ALL prop colliders — non-ring props
  (15 rows, per-row collider radius per the region-manager footprint
  table the cc-h2 lineage already uses), ring colliders (90 circles of
  r 0.45), and BOTH ghoul seats. Report the computed radius AND the
  binding obstacle row.
- PASS = largest clear radius >= 12.0 m. (Spec sec 7 target: "open
  center-north band from the statues to the root monolith >= 12 m clear
  radius". NOTE: prop/prop-mutual laws in V-3 use raw center distances;
  this check uses COLLIDER-EDGE distances — disclose which footprint
  radii the probe assigns, same disclosure law as H2bV2's footprint-map
  reuse adjudication.)
- Ring diameter sanity: parsed ring centers' rho from center (0,-700) ===
  40.0 for all 10 rows (tolerance 0.05) — the r40 closure.

## BV-6 BUILD VALIDATION — build is IO's; children NEVER build/push

- Children do NOT run `tools/build_v8.py` and do NOT commit. Validate
  whatever the worktree carries at verdict time:
  - If a pre-built v8 bundle with spire markers exists:
    `grep -c 'veil_spire_approach' prototype/builds/v8-playable.html` >= 8;
    record sha256.
  - If not present: record "no pre-built bundle at verdict time — IO
    builds at close-out" and the verdict rests on BV-0, V-0..V-9.

## Verdict format

`io/reports/2026-11-07-cc-h3-spire-approach-validation.md` — BV-0,
V-0..V-9, BV-6 one line each (PASS/FAIL + raw numbers: distances, rho
margins, tallies, marker counts, cmp results). Adjudications section:
deviations with blocking/non-blocking + reason. PASS = all checks PASS,
zero blocking. Expected adjudication classes (non-blocking): probe
adaptation deltas from the cc-h2bv2 lineage, footprint-radii disclosure
for the V-9 collider-edge computation.

## Verdict PASS -> IO close-out (not the child's job)

IO: commit 1 = code + spec/valspec/report + doc 64 H3 ledger line + GOALS
tick; then `tools/build_v8.py` IN THE WORKTREE, marker check
(`veil_spire_approach` >= 8), commit 2 (stamp), push both, release flip,
serve-verify (200 + marker grep on served bytes + cmp served==worktree),
journal, GOALS change-log.

---

SUMMARY
File: /tmp/wh-worldfeat/io/specs/cc-h3-spire-approach-valspec.md
Items: 13 (BV-0 + V-0..V-9 + BV-6), 1:1 with spec sec 7.
Ambiguities for IO to adjudicate BEFORE Devbot builds (do not silently interpret): (1) Spec sec 4 declares ">= 4.0 m mutual" for J props with NO tableaux exemption, unlike H2b's E-precedent exempt bier group — V-3 enforces mutual on ALL 15 non-ring rows including the stoneSteps pair near the statues; confirm no exemption was intended. (2) Spec sec 7 V-9 says "excluding prop colliders" but never numbers the collider radius per asset; the probe must reuse the cc-h2 footprint map — confirm that's the intended source. (3) Spec sec 3's J-side spawn/land seat (0,-730) sits 16.2 m from the ghouls per sec 6, but sec 4's law says props >= 6.0 from spawn — the skullPile at (-5,-668) is 62.2 m from the seat yet the mossBoulder (0,-672) is 58.0 m; both pass trivially, but the F-side land row (2,-652) prop law (">= 6", spec sec 6) is a QUOTED pre-verification, not a numbered law sec — V-3 enforces it anyway; confirm.
