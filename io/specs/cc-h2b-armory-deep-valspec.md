# CC-H2bV2 VALSPEC — The Armory Deep (regionI chamber) — write BEFORE build

Round: 2026-11-07 wake 20. Validates the FROZEN spec
io/specs/cc-h2b-armory-deep-spec.md (committed 3779049, wake 18's untracked
orphan) against a Devbot build on feat/world-visuals in /tmp/wh-worldfeat.
Testerbot is INDEPENDENT: do not read Devbot's dispatch transcript. Work
ONLY in /tmp/w h-worldfeat; REPORT FIRST to
io/reports/2026-11-07-cc-h2b-armory-deep-validation.md, then verdict in
your summary (RUNBOOK report-first law).

## BV-0 PRE-STATE (record raw, before touching anything)
- HEAD must be 2a61dd5. git status --porcelain recorded: only scratch/…
  and io/… paths may be dirty; anything else = report + do not touch.
- grep -c armory_deep prototype/js/CONFIG.js == 0 (pre-build state; it goes
  non-zero only after Devbot's build lands).

## BV-1 SYNTAX (pre AND post build)
- node --check prototype/js/CONFIG.js AND region-defs.js: record PASS at
  HEAD (expected) and post-build (required).

## BV-2 SPEC SHAPE (A-1..A-4)
- V2.1 CONFIG.js gains exactly ONE new top-level block `  regionI: {` with
  id 'armory_deep'. No second armory_deep id anywhere.
- V2.2 CONFIG.regionI key set EXACTLY spec sec 2: id, name, center
  (0,-1120), groundRadius 18, groundY 0, groundColor 0x101218,
  groundColor2 0x14161c, groundSeed 1662061654, scatter:false, spawn
  (0,-1128), gravityY -22, fogColor 0x0a0810, fogDensity 0.13,
  ambientLightLevel 0.07, door{ planeZ -1136, doorX 0, doorHalfWidth 3.0,
  suspendDepthM 0, wallGapPadM 0, walkFrom 'armory_deep', interact{from
  'fort_garrison', x -7.5, z -1088.5, radius 3.5}, land{
  fort_garrison:(0,-1084,face -1097), armory_deep:(0,-1128,face -1120)},
  fadeIn 0.3, fadeOut 0.5, exitFadeOut 0.8, text prompt
  'E - Descend into the armory' }.
- V2.3 enemies = 2 ghouls at spec sec 3 rows (+-6.3,-1117). No other
  enemies.
- V2.4 props = EXACTLY spec sec 4's 23 rows: 3 bier tableaux
  (stoneSarcophagus + 2 stoneSteps, ONE tableaux group), 9 hall rows
  (lanternPost 6.4/-1127.2 = the ONE crimson lamp + skullPile + whCampkit
  x2 + whTent x2 + blightcap x2 + okRuinColumn x2), 10 ring whWallA/B
  rows (scale 5.8581, wall: 8). lanternPost is the ONLY crimson-family
  socket — every other socket-bearing row in regionI must be
  amber-family or socket-free (one-accent-per-frame law).
- V2.5 groundSeed 1662061654 fresh vs every landed seed
  (1217/1218/1219/1329/1440/1651).

## BV-3 PARENT-PURITY + REGISTRATION (A-2, A-3)
- V3.1 regionH block byte-identical to HEAD (blob-extract between
  `  regionH: {` and its closing `  },`, cmp vs
  `git show HEAD:prototype/js/CONFIG.js` same extract).
- V3.2 game.js byte-identical to HEAD; daynight.js byte-identical to HEAD.
- V3.3 region-defs.js: connections 6 -> 7 (conn[6] was last). conn[0..6]
  row-text byte-identical to HEAD (row-wise extract + cmp against
  git show HEAD:…). conn[7]: from fort_garrison, to armory_deep, axis z,
  planeCoord -1136, walkFrom armory_deep, interact
  {from fort_garrison, (-7.5,-1088.5), r 3.5}, land both rows, text+fadeIn
  0.3/fadeOut 0.5/exitFadeOut 0.8 riding the door object (AMENDMENT A).
  regions registration line present (makeRegion(CFG.regionI, -1)).
- V3.4 sides table EXACTLY spec sec 6: sides[fort_garrison] = -1,
  sides[armory_deep] = +1. Record the landed values verbatim; if the
  engine's sideIn/sideOfPlane semantics disagree with the spec's E-mirror
  reading, FAIL and quote region-manager.js lines — this is the round's
  central engine-law decision (spec sec 2b), NOT adjudicable to
  non-blocking.

## BV-4 CLEARANCE PROBE (A-5)

Adapt scratch/cc-h2/clearance.py (the newest landed probe lineage: parses
LIVE CONFIG rows, no hard-coded spec numbers) into
scratch/cc-h2bv2/clearance.py. Every check reads LANDED values. Law set:

- I-side seats: spawn (0,-1128) and land.armory_deep (0,-1128) — the SAME
  seat by coordinate; both inside groundRadius 18 with margin.
- Ghouls (2): each >= 8.0 from the seat, mutual >= 12.5, >= 4.45 ring
  walk-clear (ring walk-clear = 18 - rho).
- Ring (10 whWall rows, wall: 8, scale 5.8581): colliders rebuilt per
  region-manager whPropColliders law (circle r CFG.boundaryWall.collider.r
  along local X at y -0.2). Door lane |x| <= 3 at z -1136: nearest ring
  collider >= 1.0 m (the south-point row (0,-1138) is expected nearest,
  ~1.55-1.60); ZERO colliders inside the lane window within 0.5 m.
- Props: NON-group rows >= 4.0 raw from EVERY ring collider AND >= 4.0 ring
  walk-clear (18 - rho) AND >= 6.0 from the seat (0,-1128). Bier trio =
  ONE tableaux group: internal mutual EXEMPT (E precedent 2.06 m);
  group-vs-non-group and group-vs-ring use the same laws as non-group
  props. NO other prop-mutual law (E/F landed precedent, spec sec 5).
- H-side seats: land fort_garrison (0,-1084) inside H r80 with margin
  (rho 60.0, limit 78.5), on H's home side (land.z -1084 > plane -1136).
  landH clear of: H2 dais trio (recompute from LANDED regionH rows),
  both H2 torches (raw + margin per cc-h2 verdict numbers: 8.85 spec
  target), H2's landed dressing/nodes rows per the cc-h2/clearance.py
  H-side law set (adapt which rows it checks: the landed H rows are the
  ground truth), plus 14.7 m from the G pole flank pair per spec (the
  erased-pole rows are NON-colliders — G's banner pole pair still stands
  in regionG; recompute raw from regionG rows if present, else disclose).
- H-side interact hook (-7.5,-1088.5) r 3.5: >= 5.7 clear of torchL,
  >= 9.3 of the dais, rho 64.9 (limit 78.5). Landed rows ground truth.
- conn sanity: from/to/axis/planeCoord/walkFrom/interact/land per V3.3;
  sideIn(R) == sideOfPlane(R interior) asserted BOTH ways for I;
  for H the spec's underground-law reading stands (-1 with H interior
  arithmetically +1) — assert the table carries -1 and quote the
  E-precedent lines from region-defs.js connections[2] for the record.

## BV-5 SAVE + CHAIN PROBES (A-7, A-8)
- Adapt scratch/cc-ad1/save_roundtrip.js into
  scratch/cc-h2bv2/save_roundtrip.js: capture/restore with regionId
  'armory_deep' rides through C4 + questState untouched; unknown-id
  fallback returns the old activeId. THREE-free node probe (plain node,
  no modules).
- Adapt scratch/cc-ad1/connection_probe.js into
  scratch/cc-h2bv2/connection_probe.js: connectionBetween('fort_garrison',
  'armory_deep') finds conn[7]; walkFrom-semantics fields present;
  conn[6] (H2 two-sided) MUST read byte-identical to HEAD (row extract).

## BV-6 BUILD VALIDATION (A-6) — build is IO's; children NEVER build/push
- children do NOT run build_v8 and do NOT commit. Validate whatever the
  worktree carries at verdict time:
  - If a pre-built v8 bundle with armory_deep markers exists: grep -c
    'armory_deep' prototype/builds/v8-playable.html >= 8; record sha256.
  - If not present: record 'no pre-built bundle at verdict time — IO
    builds at close-out' and PASS/FAIL rests on BV-0..BV-5.

## BV-7 SURFACE DISCIPLINE (A-9)
- git status --porcelain at verdict: ONLY prototype/js/CONFIG.js,
  prototype/js/region-defs.js, prototype/builds/v8-playable.html (if
  pre-built), scratch/cc-h2bv2/*, io/reports/* (+ io/specs/* for the
  valspec+report). ANY other touched path = FAIL.

## Verdict format
io/reports/2026-11-07-cc-h2b-armory-deep-validation.md — V-0..V-7 one line
each (PASS/FAIL + raw numbers: rho margins, distances, marker counts, sha
pairs). Adjudications section: deviations with blocking/non-blocking +
reason. PASS = all checks PASS, zero blocking. Expected adjudication
classes (non-blocking): probe adaptation deltas, footprint-map reuse from
the cc-h2 lineage, G-pole-flank handling if the pair is absent from
regionG rows (disclose raw numbers either way).

## Verdict PASS -> IO close-out (not the child's job)
IO: commit 1 = code + spec/valspec/report + doc 64 H2b ledger line
(H2b row already reads LIVE H2b? — IO checks and appends the chamber line)
+ GOALS tick; then tools/build_v8.py IN THE WORKTREE, marker check
(armory_deep >= 8), commit 2 (stamp), push both, release flip
(wh_release_flip.py, background >= 900s), serve-verify (200 + marker grep
on served bytes + cmp served==worktree), journal, GOALS change-log.
