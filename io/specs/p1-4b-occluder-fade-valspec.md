# P1-4b — Occluder proximity FADE validation spec (Testerbot)

Authority: io/specs/p1-4b-occluder-fade-spec.md (IO spec, wake 48, read in
full this authoring wake). Status: PRE-BUILD — written before Devbot starts;
every check runs against the Devbot diff on feat/world-visuals in
/tmp/wh-worldfeat after the build. Gate: code/diff/JSON review + tiny node -e
/ probe scripts ONLY — NO playtest harness, NO headless browser, NO game
loop, NO npm installs, NO network (Nicko is the playtest). Runtime feel
(A9 cycle counts, shader compile on GPU, disabled-branch feel) is Nicko's bar.

## Rules for the validator

- Git is READ-ONLY: `git status --porcelain`, `git diff`, `git log` allowed.
  NEVER `git add/commit/push/stash/checkout/clean` (no-git gate).
- All code reads against /tmp/wh-worldfeat, branch feat/world-visuals.
- Anchors are TEXT: never match by line number after Devbot's edit; the line
  numbers below are authoring-time landmarks only.
- Convention law stands (IIFE + window globals, var style, NO ES modules /
  import / const / let / arrow functions in prototype/js; zero per-frame
  allocation in the player pull and the fade driver).
- A FAIL quotes the offending line(s); a SKIP states the reason and needs
  the gate's consent.

## Testerbot artifacts (created PRE-BUILD this authoring wake; read-only for Devbot)

1. io/specs/p1-4b-fade-probe.js — node loader of CONFIG.js + region-defs.js +
   region-manager.js with a PINNED stub meta (getMeta always
   {height:6,width:2,groundMinY:0}) and a static THREE stub; dumps every
   WH_REGION_DEFS region's propColliders table (rows projected onto
   index,name,x,z,r,h,fy exactly as today) + scatter stats + wall plan
   counts as ONE JSON doc. sha256 prefix c108d5288f190e77. Runs clean on the
   pre-change tree (exit 0); writes nothing in the repo.
2. io/specs/p1-4b-fade-baseline.json — probe 1 output pre-change. sha256
   prefix f15c6913e6e84801. 3409 circle rows, 0 exempt rows, wall plan
   colliders 596 (A region hold_outskirts 586, B darkwood_edge 426,
   C forest_of_the_old_king 272; full per-region table in V-11).
3. io/specs/p1-4b-fade-probe2.js — same harness, adding per-row columns
   veg (the COLLIDER name-law regex verbatim: /tree|oak|birch|sapling|bush|
   bramble|fern|shrub|stump/i) and fadeSeed (hash over `index|name`: FNV-1a
   bytes h1 = 2166136261; per code unit h ^= code; h = Math.imul(h,
   16777619) >>> 0; then h >>>= 15; h = Math.imul(h, 2246822519) >>> 0;
   h = Math.imul(h, 3266489917) >>> 0; h ^= h >>> 13; seed = (h >>> 0) /
   4294967295). sha256 prefix ecaf486916991b62. This is the A3 veg/fadeSeed
   oracle AND the A4 classifier oracle (node-side, pre- and post-build).
4. io/specs/p1-4b-fade-baseline2.json — probe 2 output pre-change. sha256
   prefix 6841b71af5cc76a3. 3409 rows; veg rows: hold_outskirts 109 (95
   prop + 14 scatter), darkwood_edge 47 (37 + 10), forest_of_the_old_king
   106 (A/B/C), all other regions 0; veg seed range 0.0120..0.9963.
   The baselines are deterministic (only the pinned stub is consulted): if
   a re-run ever disagrees, STOP and hand the discrepancy to IO.

Devbot must NOT modify, move, or delete these four files; IO commits them
with the round. No git stash is allowed, so post-build these artifacts ARE
the only record of the pre-change tree (no rebuild-the-baseline fallback).

## Pre-change landmarks (authoring-time; TEXT anchors govern)

- CONFIG.js: `player` block holds the P1-4a cameraPull subtree (enabled
  true, camRadiusM 0.45, skinM 0.30, samples 6, trunkTopFrac 0.45, minFloor
  0.0). NO occluderFade key anywhere (grep = 0 across js/). CONFIG counts
  today: 'transparent' 0; 'prototype:' 0; '=>' 7 (string literals);
  'Math.random' 2.
- player.js: `var CP = window.WH_CONFIG.player.cameraPull;` (grep = 1);
  CP_* scratch block grep -cE '^  var CP_' = 24; `lastCameraPull` hits = 5
  (decl comment, init null ~179, lazy-object record ~2383-2395).
  updateCamera anchors: gate line `if (CP.enabled && this.state === 'alive'
  &&`; sample walk with conservative defaults `(CP_C.h === undefined ||
  CP_C.h === null) ? 12 : CP_C.h` and `... CP_C.fy ... ? -6 : CP_C.fy`
  (2 sites each); `CP_REC.sampleCount = CP_N;`; then `if (want.y < floorY)
  want.y = floorY;` + lerp2/lerp/lookAt. `new ` inside the updateCamera
  span = exactly 1. Whole file: const/let = 0, '=>' = 0. The walk reads
  ONLY table.circles (`propColliders(...).circles`).
- region-manager.js: TRUNK_RATIO 0.25; TRUNK_ASSETS 14 names; colliderRadius
  + whOccluderH EACH carry the veg-name regex inline (2 copies today; 4.2
  collapses them onto vegClass — post-build grep for the regex body = 1).
  whPropColliders: p.noCollide skip; p.wall per-segment rows (index `i.k`,
  r = CFG.boundaryWall.collider.r, h = CFG.boundaryWall.heightM); normal
  rows (r/h/fy attach, corridor routing to exempt vs circles, r>0 filter);
  scatter rows (index 'scatter<j>', h fallback 12); world-wall side rows
  from wall.colliders (WALL_SIDE_PAD_M 3). Returns {circles, exempt,
  complete}. proto.propColliders caches per region (stores table.complete).
  whBuildInstanced(name, list) 2-arg; buildWorld; buildRegion (prop rows
  .instance(); scatter trees .instance() + whGroundFeed; CC-C4a cell
  buckets); disposeRegion (traverse dispose: materials/maps/geometry/
  isInstancedMesh, scene.remove(group)). 'transparent' count rm = 2.
  CFG.player.cameraPull hits in rm = 1 (whOccluderH).
- git status --porcelain at authoring: M prototype/builds/v8-playable.html;
  M prototype/js/CONFIG.js; M prototype/js/wareffort.js; ?? cc-wb4-*
  standing-stone spec+valspec, p1-4b-fade-baseline(.2).json,
  p1-4b-fade-probe(.2).js, p1-4b-occluder-fade-spec.md, this valspec.
  git diff --numstat on player.js + region-manager.js = EMPTY; CONFIG.js
  diff = +25/-0 (CC-WB4 repeatStanding/stone rows — PRE-EXISTING, NOT
  P1-4b's). index.html <script> count = 37; prototype/builds/ = v1, v2,
  v8 (builds are IO's job). No node_modules, no package.json.

## Checks (V-1..V-38)

Map (A = acceptance, R = risk): V-1..V-4 syntax/convention/diff
confinement (A1, A12). V-5..V-8 CONFIG block, classifier, row annotation,
seeds (A4, A3 fields, spec 4.1/4.2/4.4). V-9..V-11 row identity + counts
byte-stable (A3, A5 floor, 4.3). V-12..V-14 camera split + disabled law
(A2, A8, 4.5). V-15..V-19 registry build, geometry clone, singles, wall
weld, resolution (A5, 4.6, R1). V-20..V-23 driver math, decay, dirty
writes, zero-alloc (4.7, A10). V-24..V-28 nesting/ownership/shader/
transparency/bounds (A11, 4.8/4.9, R2/R3). V-29 disposal (A9 code-level).
V-30/V-31 exemption + collision (A6). V-32..V-34 pull-law sim, RNG,
priority (A7). V-35 classifier census (A4). V-36 allowlist (A12). V-37
CONFIG safety. V-38 = A9 runtime skip statement.

- V-1 [BLOCKING] A1 syntax. `node --check prototype/js/CONFIG.js`,
  `node --check prototype/js/player.js`,
  `node --check prototype/js/region-manager.js` — all exit 0.
- V-2 [BLOCKING] Convention sweep, three files: grep -cE
  '(^|[^a-zA-Z.])(const|let) ' = 0/0/0; grep -c '=>' player.js + rm = 0/0,
  CONFIG.js = 7 (pre-existing); grep -rn 'prototype:' CONFIG.js = 0 (4.1 is
  data-only); grep -c 'Math.random' = 2/0/0 (pre-existing; see V-33).
- V-3 [BLOCKING] A12 diff confinement. git status --porcelain shows ONLY
  the 3 allowlist js files modified (plus the authoring-time pre-existing
  M builds/v8-playable.html, M CONFIG.js [CC-WB4], M wareffort.js and the
  untracked io/ paperwork incl. io/devbot-p14b-notes.md);
  `git diff --numstat -- prototype/js/player.js
  prototype/js/region-manager.js` non-zero for those two ONLY; CONFIG.js
  diff = occluderFade block + cameraPull comment addendum ONLY;
  prototype/builds/ still v1/v2/v8; no new prototype/js files.
- V-4 [BLOCKING] Anti-harness. grep -rniE 'puppeteer|playwright|headless'
  prototype/js/ = 0; no node_modules / package.json under prototype/ or
  repo root; no added require(/fetch/XMLHttpRequest in the 3 diffs.
- V-5 [BLOCKING] 4.1 CONFIG block. node -e
  `global.window=global;require('<abs>/prototype/js/CONFIG.js');
  var F=window.WH_CONFIG.world.occluderFade;` — F exists;
  enabled === true (strict boolean); dissolveM === 1.2; hashMin === 0.02;
  pullFadeSlack === 0.25; AND the block carries decayPerSec === 2.0
  (4.7 names CONFIG occluderFade.decayPerSec); block cites the IO spec
  path in a comment; cameraPull VALUES untouched (diff hunk: comment-only
  or nothing). occluderFade lives under CFG.world.occluderFade exactly as
  4.5 reads it (V-24 cross-confirms both nesting points).
- V-6 [BLOCKING] 4.2 classifier. typeof window.WH_RegionManager.vegClass
  === 'function' OR same on the prototype (post-build node -e; quote
  which form). The veg regex body appears EXACTLY ONCE in rm
  (grep -c 'tree|oak|birch|sapling|bush|bramble|fern|shrub|stump'
  region-manager.js = 1) — colliderRadius AND whOccluderH delegate to
  vegClass (no duplicate OR-list anywhere); TRUNK_RATIO 0.25 and
  TRUNK_ASSETS unchanged (diff context-only).
- V-7 [BLOCKING] 4.3 row annotation. Post-build probe2 run: every row in
  every region carries veg === 1 on veg-name rows, 0 on the rest (probe2
  computes the law itself; the check is that Devbot's rows AGREE with
  probe2's veg column — a `diff` of the veg columns = clean). Wall rows
  (index 'wall-*'/'arch-*'/'forecourt-*', asset whWallA/whWallB/b3Gate)
  carry veg 0 (A4 census confirms those classify 0).
- V-8 [BLOCKING] 4.4 seeds. Post-build probe2: every row's fadeSeed in
  0..1 AND equal to probe2's own seed for that row. Binding law: Devbot
  MUST match probe2's exact hash (they may not edit Testerbot-owned
  probe2, and 4.4's "any deterministic mapping" is pinned by the probe;
  a different hash = FAIL here — no ambiguity).
- V-9 [BLOCKING] A3 row identity (THE probe). `mkdir -p /tmp/p14b &&
  cp io/specs/p1-4b-fade-probe.js /tmp/p14b/probe1.js &&
  node /tmp/p14b/probe1.js > /tmp/p14b/post.json &&
  diff -q io/specs/p1-4b-fade-baseline.json /tmp/p14b/post.json` —
  IDENTICAL (exit 0): every (index,name,x,z,r,h,fy) tuple byte-stable in
  row order (A3: "row ... values match pre-change build to the byte").
  Pre-conditions quoted: baseline hash f15c6913e6e84801; the P1-4b
  diff footprint present. Any drift = A3 FAIL.
- V-10 [BLOCKING] A3 projected probe2 diff. `node
  io/specs/p1-4b-fade-probe2.js > /tmp/p14b/post2.json` then compare the
  (index,name,x,z,r,h,fy) projection of post2 against baseline2 with ALL
  veg/fadeSeed fields dropped (tiny compare script at /tmp/p14b/cmp2.js:
  JSON-parse both, strip the 2 new keys per row, JSON.stringify per
  region, diff) — byte-identical. New fields must NOT collide with any
  pre-change field name (the projection proves none moved).
- V-11 [BLOCKING] A1 + A5 registry floor. From post.json (V-9 run):
  hold_outskirts 586, darkwood_edge 426, forest_of_the_old_king 272,
  rot_den 105, veil_crypt 63, veil_galleries 57, lords_hold 1068,
  fort_garrison 406, armory_deep 93, veil_spire_approach 105,
  tithe_vaults 115, the_remains 113 circle rows; wall plan colliderCount
  596; total 3409; exempt 0 (every region) — UNCHANGED. From post2 (V-10
  run): veg circle rows: hold_outskirts 109 (95 property-row + 14
  scatter), darkwood_edge 47 (37 + 10), forest_of_the_old_king 106, every
  other region 0; 13 distinct veg names across A/B/C (yewTree, treeStump,
  witchwoodTree, livingOak, reachTreeA, reachTreeB, reachTreeC, deadTree,
  youngBirch, youngDeadTree, bramble, okTreeOak, okTreePine). These 262
  veg rows are the A5 registry FLOOR: the registry may add MORE targets
  (scatter singles, wall rows, C bucket indices) but never fewer per
  region. A4 spec names (thornbush, stoneMarker, campfireRing,
  gravestone) not present in CONFIG's actual asset rows — A4's
  parenthetical delegates to CONFIG-derived names; see V-35.
- V-12 [BLOCKING] 4.5 camera split. player.js diff: ONLY the fade-request
  bookkeeping (veg-row hit records {row, penetration} on the fixed
  preallocated list, does NOT set CP_I) + the driver call; the PULL MATH
  (sample walk, Y-band, circle test, first-blocked index, verification
  shrink, CP_FIN floor, want construction) takes ZERO ± lines (span from
  the gate line to the want.set(...) line + the floor clamp). Quote both
  branches: veg hit -> fade path ONLY when CFG.world.occluderFade is
  enabled AND the region's fade registry exists; otherwise exact
  pre-change CP_I pull. Mass rows pull as today in BOTH modes (V-34).
- V-13 [BLOCKING] A2 disabled law. grep -n 'occluderFade' player.js: every
  hit sits in a short-circuit chain that resolves BEFORE any registry
  read or fade write; updateCamera must not touch this.fadeMeshes /
  call updateOccluderFade when disabled (code-read + quote the guard
  chain). Re-greps unchanged: CP scratch = 24, lastCameraPull hits = 5,
  `new ` in updateCamera span = 1, `var CP = ...cameraPull;` = 1,
  conservative defaults 2x each.
- V-14 [BLOCKING] A8 full-off equivalence. The disabled branch executes
  ONLY pre-change statements: the fade-request array is allocated at
  init/module scope (never inside the disabled path — grep the decl);
  the record write, pull math, floor are the pre-change lines (V-12's
  zero-delta + this code-read = A8 evidence; quote 3 decisive lines).
- V-15 [BLOCKING] 4.6 registry. In buildRegion (rm): registry fill at
  BUILD time: scatter trees push 'single' entries keyed 'scatter<j>'
  (per 4.6); instanced prop meshes (incl. CC-C4a cell buckets) register
  byProp keys per row (obj + instIdx); shape per 4.6's
  `fadeMeshes[regionId] = { byProp ..., count }` or equivalent (quote
  it). grep the driver span for 'buildRegion' = 0 (registration is not
  per-frame).
- V-16 [BLOCKING] R1 geometry clone. The fadeable InstancedMesh path
  CLONES the geometry (grep '.clone()' on geometry in the fadeable
  branch): carries the InstancedBufferAttribute 'whDissolve' (grep
  'whDissolve' >= 1 hit in rm), added BEFORE the clone's first render
  (R2); the SHARED template geometry receives NO attribute (quote the
  ownership). Non-fadeable callers keep the 2-arg signature; the opts
  param ({fadeable:true}) is additive.
- V-17 [BLOCKING] 4.6 singles. Scatter-tree registry entries own a
  per-tree MATERIAL CLONE (mesh.material = material.clone() in the
  scatter span) carrying the fade uniform (whFadeUniform {value:0} or
  equivalent, grep 'whFadeUniform' >= 1); the clone is tracked for
  disposal (V-29); the template material is never mutated.
- V-18 [BLOCKING] 4.6 wall weld. Registry keys for wall rows use the row
  index strings ('wall-ring<i>.<k>', 'wall-chordE<i>.<k>',
  'wall-chordW<i>.<k>', 'arch-legE/W<i>', 'arch-plug<i>',
  'forecourt-<kind>-<i>') so driver resolution matches the build plan
  1:1 (quote the key construction); the region-side wall filter
  (WALL_SIDE_PAD_M 3) untouched.
- V-19 [BLOCKING] A5 resolution. ByProp resolves rows to {obj, instIdx}
  (grep 'instIdx' or the byProp push); C cell buckets resolve through
  bucket-instance indices (CC-C4a path). Verdict traces 3 rows from
  post2: a prop row (hold_outskirts index 8: yewTree x 29.4 z 1.3 r
  1.625), a scatter row ('scatter7' hold_outskirts: 'single'),
  a C cell-bucket row (index '#.#' form) — each resolves to its
  registered target(s).
- V-20 [BLOCKING] 4.7 driver math (simulator). `node -e` sim (quoted
  constants; no file needed): t = clamp((penetration - pullFadeSlack) /
  dissolveM, 0, 1); ease t*t*(3-2t); instanced write = mix(seed, 1,
  easedT); single uniform = same mix law; decay bounded by decayPerSec
  2.0 (values decay toward 0, never jump). The verdict quotes PASS
  values: penetration 0.25 -> t 0; 1.45 -> t = (1.45-0.25)/1.2 = 1.0
  (full dissolve); 0.85 -> t = 0.5 -> eased 0.5 (smoothstep midpoint
  symmetric). Devbot's driver must read these constants from CONFIG
  (grep CONFIG.world.occluderFade in the driver = hit), not hardcode
  (V-21/V-24 confirm).
- V-21 [BLOCKING] 4.7 decay. grep the driver for the decayPerSec read +
  the flat loop over the previous-frame active list; NO full-mesh reseed
  per frame (grep for a setScalar/forEach-all-instances in the decay
  path = 0 hits); decay applies every pass to ALL registered targets
  (quote the loop bounds).
- V-22 [BLOCKING] 4.7 dirty writes. attribute.needsUpdate set ONLY when
  the instance's value changed by > 1e-3 (quote the threshold line); no
  unconditional needsUpdate inside the driver loop.
- V-23 [BLOCKING] A10 zero-alloc. In the diff-ADDED per-frame spans
  (player bookkeeping + rm driver): grep 'new ' = 0; object/array
  literals only at module/constructor scope (fixed arrays fine there);
  frame-scoped fade list = fixed-capacity preallocated array + count Int
  (quote the decl + reset); NO closures in the per-frame walk (grep
  'function(' inside the driver loop body = 0 hits).
- V-24 [BLOCKING] Nesting + CONFIG-only. node -e (CONFIG.js alone) walks
  window.WH_CONFIG.player.cameraPull (still the P1-4a subtree, values
  byte-equal to the Landmarks list) AND window.WH_CONFIG.world.occluderFade
  (V-5's keys); git diff on CONFIG.js = occluderFade block + cameraPull
  comment lines ONLY; verdict prints the JSON.
- V-25 [BLOCKING] R2/R3 patch-once. In the injected material path: the
  onBeforeCompile injection is guarded by a per-material-CLONE flag
  (whFadePatched keyed by material uuid — grep 'whFadePatched' >= 1 hit,
  grep 'uuid' in the guard >= 1); the flag NEVER lives on the template
  material; the injection/attribute-add precedes the region group's
  scene add in buildRegion order (quote the order).
- V-26 [BLOCKING] A11 transparency. grep -c 'transparent' CONFIG.js = 0,
  region-manager.js = 2 (pre-existing; added code adds none — grep the
  ADDED diff lines for 'transparent' = 0 hits); no .transparent = true
  anywhere in the diff; depthWrite stays true (added 'depthWrite' lines,
  if any, set true; absent = pass).
- V-27 [BLOCKING] A11 GLSL paths. In rm's injected GLSL: attribute path
  present (grep -c 'attribute float whDissolve' >= 1 or the declared
  equivalent, quoted); uniform path present (grep 'whFadeAmount' >= 1);
  varying declared (grep 'varying' >= 1 in the injection); hash source:
  either the r185 chunk reuse (grep 'alphahash_fragment|getAlphaHashThreshold'
  >= 1 — chunks verified present TODAY: 12 alphahash/hash_PCG hits in
  builds/v8-playable.html) OR an inline self-contained hash — both
  allowed (4.8); the valspec requires ONLY both paths present + node
  --check clean (A11's runtime half is Nicko's bar).
- V-28 [BLOCKING] Bounds untouched. Fade never moves geometry: no new
  computeBoundingSphere/position-writes in the driver (grep = 0 new
  hits; the pre-existing im.computeBoundingSphere in whBuildInstanced
  unchanged); no boundingSphere recompute in the added spans.
- V-29 [BLOCKING] 4.9 disposal (A9 code half). disposeRegion: added lines
  dispose (a) fadeable geometry CLONES (quote the ownership test — never
  tmpl.geometry), (b) 'single' material clones, (c) the region's
  fadeMeshes entries (delete/empty); the SHARED template geometry and
  template materials receive NO new dispose calls (quote); registry
  cleanup is ordered before the group is gone (R4 half 1). grep count:
  .dispose( hits in the disposeRegion span >= 9 (8 pre-existing + clone
  disposal).
- V-30 [BLOCKING] A6 exemption. WhMeetsCorridor/WALL_SIDE_PAD_M untouched
  (grep -c 'whMeetsCorridor' rm unchanged; wall filter untouched);
  exempt arrays stay EMPTY in probe dumps (V-9); the registration reads
  table.circles ONLY (grep '.exempt' in the registration/driver = 0 new
  hits) — exempt rows never fade.
- V-31 [BLOCKING] A6 collision. pushOutCircles (TEXT anchor
  'RegionManagerLogic.prototype.pushOutCircles') + the CP_CIRCLES
  consumer receive ZERO diff lines (quote the absence from git diff);
  every circle (veg and mass) still pushes the player out — only the
  CAMERA test splits (4.3 advisory-metadata law).
- V-32 [BLOCKING] A7 pull-law simulation. `node -e` (Testerbot-run;
  constants inlined — camRadius 0.45, skin 0.30, samples 6, target
  (0,0,0), want (10,0,0), veg trunk x=5 r=0.35 h=3.4 fy=0, mass boulder
  x=9 r=1.0 h=9 fy=0, Y-band law [fy-0.25, fy+h]): (i) fade OFF -> first
  blocked sample I = 2 (the veg row at x=5 blocks first: sample k=3,
  t=0.5, x=5.0 inside the 1.10 limit; legacy treats it as an occluder);
  (ii) fade ON -> the veg row produces a fade REQUEST (k=3, penetration
  1.1) and does NOT pull; the first blocked MASS sample I = 4 (the
  mass row fires the pull exactly as today). Re-run post-build against
  the REAL walk by stubbing CP_CIRCLES with these rows (the walk is a
  pure function of circles + CONFIG; Vector3-like {x,y,z} floats
  suffice) — if not extractable, the simulator result stands with
  V-12's code-read as A7 evidence.
- V-33 [BLOCKING] A7 no new RNG. git diff | grep -E '^\+.*(random|Date.now)'
  = no hits; grep -c 'Math.random' = pre-change counts (2/0/0); seeds are
  pure string hashes (V-8/probe2 — deterministic across rebuilds: same
  index+name -> same seed; probe2 re-run byte-matches itself).
- V-34 [BLOCKING] 4.5 priority. Code-read (quote): the veg-hit branch
  never sets CP_I and keeps scanning; the mass-hit branch sets CP_I
  exactly as pre-change; a fade request can never cancel a fired pull;
  a mass row at ANY sample pulls at the FIRST mass sample even if fade
  requests were recorded earlier (fade does not screen mass).
- V-35 [BLOCKING] A4 census. node io/specs/p1-4b-fade-probe2.js post-build
  + V-6's vegClass: assert veg 1 for livingOak, treeStump,
  witchwoodTree, bramble, mossyStump (TRUNK_ASSETS), reachTreeA/B/C,
  yewTree, deadTree, youngBirch, youngDeadTree, okTreeOak, okTreePine;
  veg 0 for whWallA, whWallB, b3Gate, gravestoneObelisk, graveMound,
  mossBoulder, fallenLog, lanternPost, picketFence, ironFenceSection,
  mourningStatue, skullPile, stoneSteps, banditCampfire, blightcap,
  grassTuft, rubblePile, pegs, tent, whTent, whCampkit, bedroll,
  banditBedroll, churchPewBroken, churchPulpit, stoneSarcophagus,
  buriedCoffin, candelabra, farmerBody, zealot, ghoul, rotspawn. A4's
  literal spec names (thornbush, stoneMarker, campfireRing, gravestone)
  do not exist as CONFIG asset names — report as INFO per A4's
  parenthetical (CONFIG-derived actuals govern), quoting any mismatch;
  NOT a FAIL unless a CONFIG-real name classifies against the law.
- V-36 [BLOCKING] A12 build/surface. index.html grep -c '<script' = 37;
  builds/ = v1/v2/v8 only; no new prototype/js files; no tools/ or
  art-direction/ changes; no new .html. Any file outside §5's allowlist
  in the Devbot diff = FAIL.
- V-37 [BLOCKING] CONFIG safety. node -e loads CONFIG.js alone without
  throwing (the `},` + insertion whitespace is clean;
  JSON.stringify(window.WH_CONFIG.world.occluderFade) round-trips V-5's
  values; cameraPull round-trips P1-4a's). CONFIG.js is a JS object
  literal (not JSON) — this is a JS-eval + stringify check, quoted as
  such.
- V-38 [SKIP — pre-consented by A9's own wording] A9 runtime half (build
  + dispose region x3, registry empty after, no cloned-geometry leaks,
  DeveloperTools memory): needs a browser — out of Testerbot scope under
  the no-harness gate ("DeveloperTools memory count NOT checked;
  code-level audit of dispose paths only"; playtest is Nicko's). The
  disposal LAW is verified by V-29 (geometry clones + material clones +
  registry cleanup + template survival both halves).

## HOW TO REPORT

Final answer, structured exactly:

VERDICT: PASS | FAIL (with exact failed check numbers)

Then one line per check, in order, in the form:

V-<n> <short name>: PASS | FAIL | SKIP — <one-clause evidence>

Evidence rules:
- PASS: quote the command + decisive output ("diff -q exit 0",
  "circles total 3409", "post2 projection identical").
- FAIL: QUOTE the offending line(s) from the file or the diff.
- SKIP: expected ONLY for V-38 (quote the no-harness reason + the V-29
  stand-in).
- Anything unexpected (extra diff hunks, a second `new` in updateCamera,
  an exempt row appearing, a seed outside 0..1, probe drift, a CONFIG key
  drift): list under "Deviations / unexpected" after the per-check lines,
  even when the verdict is PASS.
- List any check that FAILED twice (stop; hand the exact error to IO).

End with the four acceptance calls:
(a) A1..A12 status table — one line each, naming the covering checks
    (A1: V-1; A2: V-13/V-14; A3: V-9/V-10; A4: V-35/V-6; A5: V-11/V-15/
    V-16/V-19; A6: V-30/V-31; A7: V-32/V-33/V-34; A8: V-14; A9: V-29 +
    V-38 SKIP; A10: V-23; A11: V-26/V-27; A12: V-3/V-36).
(b) Diff readiness for IO's rebuild (prototype/builds/v8-playable.html is
    IO's job; V-36 expects it untouched by Devbot).
(c) R6 tuning caveat: the constants (pullFadeSlack 0.25, dissolveM 1.2,
    hashMin 0.02, decayPerSec 2.0) are Nicko's playtest-tuning surface,
    not acceptance constants — the law is that they live in CONFIG (V-5)
    and are read from CONFIG in code (V-20/V-21).
(d) A9 runtime acceptance = Nicko playtest (V-38 SKIP).
