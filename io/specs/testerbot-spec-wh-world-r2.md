# TESTERBOT SPEC — Witch Hunter World R2: Lighting Rig Overhaul Validation (gate step 2)

Author: Testerbot (independent validator-author). Date: 2026-10-01.
Devbot spec of record: io/specs/devbot-spec-wh-world-r2.md (read-only; do not fix —
mismatches are reported as amendment notes, never patched in the spec by me).
Authority for ACs: devbot-spec-wh-world-r2.md lines 186-241 (R1 floor + L1-L10) +
retune protocol lines 243-248. Audit doc 61 §5.3/P1-8 is upstream authority for the
devbot spec only; I derive tests from the SPEC, not the audit.

## Harness
- File: tests/wh_world_r2_validation.py (NEW file; Playwright sync API, headless
  chromium, `--enable-unsafe-swiftshader`). The R1 file tests/wh_world_r1_validation.py
  stays untouched and keeps passing as shipped (floor step re-runs it unchanged).
- Boot: spawn prototype/server.py on WH_R2_PORT (default 8792) or reuse an external
  server via `WH_BASE_ROOT` env (default http://localhost:8792/; v2 pattern from
  wh_v7_weave.py, R1 start_server pattern verbatim). Load `prototype/index.html`
  (source tree, not the build). Watch console errors + pageerrors from boot; BOOT
  gate = 0 console errors, 0 pageerrors, WH_DEBUG ready. Viewport is set to
  1920x1080 for every run (L4 samples "1080p center-top" — fixed size is part of
  the method, not incidental).
- Harness discipline (mirrors R1): `check(ac,name,ok,detail)` records and prints one
  AC-line per check; per-AC functions `ac_l1..ac_l10` + `ac_floor` + `ac_scope`; every
  AC body wrapped in try/except so a runner exception becomes recorded FAIL data, not
  a harness crash; runtime budget guard (failures past budget recorded as
  BUDGET-SKIP, exit still 0); exit 0 ALWAYS (failures are data; final stdout line is
  one JSON object).
- Organic-path law: real keyboard/mouse events (page.keyboard.down/up/press,
  page.mouse) reach the game via document listeners (player.js:170-213). WH_DEBUG /
  WH_GAME / WH_ASSETS READS are always fine (page.evaluate that only reads). Direct
  gameplay-state mutation as a TEST act is banned. Sanctioned writes: exactly the
  ones R1 sanctioned plus R2's own shipped hooks — WH_DEBUG.teleportPlayer (position
  before organic play), WH_DEBUG.setFocus / setStamina (pre-existing), and the NEW
  R2 hooks WH_DEBUG.getLightPool() / WH_DEBUG.getLightSockets() which are
  measurement-only per devbot spec R2-3 (:166-169). Harness-created scene geometry is
  allowed ONLY for the L2 probe plane (see method note there) and only after all
  other geometry-sensitive ACs are done.
- Env overrides: `WH_BASE_ROOT`, `WH_R2_PORT` (8792), `WH_SMOKE=1` (short mode:
  skips the 10 s L5 walk-segment and 4-distance L10 sweep, runs 1 cast + 1
  distance), `WH_R2_FLOOR=0` to skip the R1 subprocess re-run (default on).
- Headless-safe luminance: R1 toDataURL pattern unchanged — WebGLRenderer has no
  preserveDrawingBuffer (game.js:34), so the harness calls
  `WH_GAME.renderer.render(WH_GAME.scene, WH_GAME.camera)` synchronously inside
  page.evaluate immediately before canvas.toDataURL, decodes PNG in Python (stdlib
  struct/zlib, no PIL) and samples luminance per pixel. Page-clock only: waits via
  page.wait_for_timeout and rAF-chained in-page samplers (a JS function that records
  on consecutive requestAnimationFrame callbacks), never wall-clock assumptions.
- rAF-chained sampler (new primitive, read-only): install via add_init_script BEFORE
  page load — wrap window.requestAnimationFrame passively; on tick N record
  {poolLen, lanternOk, ambientCount, hemiCount, dirCount, programs} from WH_GAME into
  window.__R2_BOOT_PROBE (first tick) and window.__R2_TICKS (sliding last 120 ticks).
  This proves "pool lights exist before the first render" deterministicly instead of
  racing WH_DEBUG-ready. Reads only; writes nothing into game state.

## Floor step (before L1-L10)
- Re-run tests/wh_world_r1_validation.py UNCHANGED as a subprocess, sharing the R2
  server via WH_BASE_ROOT (R1's own start_server polls BASE_ROOT first and reuses an
  up server; no port collision). Parse its final stdout JSON line.
- PASS: R1 verdict PASS per R1's own protocol (A1-A4,A6,A7,A8 PASS, A5 RECORD;
  A3 partial-organic flag allowed). R2 note applies: R1 A1 must now also cover the
  two new region-B props (banditCampfire, lanternWaymarker) with |minY| <= 0.02
  because they join the CONFIG arrays the R1 harness walks — same tolerance, no R1
  edit needed.
- Floor-WAIVER rule: if R1 A8 (git-status scope) fails only because of known R2-round
  artifacts (io/specs/*-r2*.md, io/reports/*r2*, tests/wh_world_r2_validation.py),
  record FLOOR-WAIVER with the explicit path list and continue; any other
  out-of-surface file blocks. R1 A6/A7 hash floors are R1-frozen and must match
  exactly (their subject files did not change this round).
- WH_SMOKE=1 still runs the floor step (R1 smoke profile is cheap); WH_R2_FLOOR=0
  skips with a recorded note (never silently).

## Per-AC validation method (L1-L10; devbot spec :195-241 verbatim bars)

### L1 — AmbientLight removal + hemisphere fill scaling
- Scene traversal via page.evaluate: count lights by constructor name over
  WH_GAME.scene (recursive children walk).
- PASS bars: AmbientLight count == 0 (whole scene, both before and after a region
  crossing); HemisphereLight count == 1; hemi.color.getHex() == CFG.lighting
  .hemiSkyColor (0x4a5a80) and hemi.groundColor.getHex() == 0x16181e; hemi.intensity
  == hemiBaseIntensity (1.35) while in region A and == hemiBaseIntensity *
  regionB.ambientLightLevel (0.55 -> 0.7425) while in region B (tolerance ±0.03);
  CFG.lighting.ambientIntensity === 0 (kept key, kept zero).
- Region B sample: reuse the R1-VALIDATED prewarm entry — teleportPlayer to
  regionA boundary z (-25) + 22 inside CFG.preWarm distance 30, wait 2.5 s, then walk
  across (page.keyboard.down('w')) until
  WH_DEBUG.getRegionManager().logic.activeId flips; sample hemi.intensity again.
  Direct buildRegion() calls remain banned (R1 smoke showed they throw).
- Evidence: both regions' hemi intensities recorded numerically; also record
  moonLight.intensity in both regions to prove it does NOT scale.

### L2 — Moon direction + backlight proof
- Primary numeric (PASS basis): exactly 1 DirectionalLight in scene; color ===
  CFG.lighting.moonColor (0xa8bce6, THREE.Color.getHex()); world position z < 0;
  elevation = asin(|y| / len(position)) in degrees within 25-35; azimuth ≈ 0 (x
  component |x|/len <= 0.08); target is scene-fixed at origin (0,0,0).
  Direction is validated from light.position alone — no gameplay write.
- Backlight probe (RECORD + secondary PASS input, run LAST): create ONE measurement
  plane (2x2, MeshBasicMaterial white lambert-free) at world center offset (+40, 0,
  0), facing +z; force render; toDataURL; sample plane pixels; repeat with a second
  identical plane at (-40, 0, 0) facing -z; ratio = lum(moon-facing)/lum(opposite).
  Instrumentation geometry (not gameplay state): allowed as the one sanctioned
  test-scene write, added AFTER L5's program sweep and L8 sprite checks to avoid
  contaminating their counts, cleaned by a page reload immediately after. PASS input:
  ratio >= 2.0 (moon:fill on vertical faces 3-5:1 per audit, bar 2.0 per spec).
  If ratio is degenerate (plane unlit, SwiftShader artifact), record numbers and
  flag ENV-LIMIT rather than silently passing on position math alone.
- Fog difference between regions does not gate L2 (probe taken in region A after
  returning from the L1 crossing).

### L3 — Player lantern (warm, parented, flicker, follow)
- Existence/config: exactly 1 PointLight whose parent chain (walk .parent up) reaches
  WH_GAME.player.root or its yawFrame; color.getHex() == 0xffb060; light.distance ==
  CFG.lighting.lanternDistance (12) && light.decay == 2.
- Flicker band: rAF-chained sampler records lantern.intensity on 60 consecutive
  frames at idle; PASS if every sample within ±5% of lanternIntensity (6.5 -> band
  [6.175, 6.825]) AND max |step| between consecutive samples <= 0.5 AND no sample
  exactly equals 6.5 for the whole window unless flicker is present elsewhere
  (a dead-flat trace means flicker code absent — cross-check by computing the
  expected wobble envelope: intensity should differ from base at some sampled t
  since 0.6*sin(7.3t)+0.4*sin(3.1t+1.7) has no 60-frame dead zone; flat trace =
  FAIL with the trace range as evidence). No Math.random is verified by
  re-sampling a second 60-frame window and checking the first window's trace
  repeats shape on similar t-offsets within tolerance — too weak to gate alone, so
  it is RECORD-only evidence.
- Follow: read lantern.getWorldPosition() and player pos; teleportPlayer(+15, +15);
  forced render, re-read; PASS if lantern world delta == player world delta within
  0.01 on both x and z.

### L4 — Tone mapping + exposure + fog-brightness floor
- PASS bars: WH_GAME.renderer.toneMapping === THREE.NeutralToneMapping (also verify
  CFG.renderer.toneMappingName === 'Neutral'); renderer.toneMappingExposure ===
  CFG.renderer.toneMappingExposure (1.15) (identity of plumbing, not a re-derivation);
  pixel test at the 1920x1080 viewport: forced render + toDataURL, sky band =
  rows [0.02h, 0.18h] x cols [0.4w, 0.6w] mean luminance, ground band = rows
  [0.72h, 0.95h] x cols [0.30w, 0.70w] (R1-validated near-field ground placement);
  PASS if sky mean >= ground mean (fog stays the brightest large area) AND sky mean
  is nonzero at 1080p (recording both). Numbers recorded with n pixels each.
- SwiftShader note: compare means, not per-pixel exactness; both samples come from
  the SAME forced frame so exposure variance cancels in the inequality.

### L5 — Fixed pool exists at boot; program growth <= +2 (M-19)
- Boot bar: window.__R2_BOOT_PROBE from the pre-load init script shows pool point
  lights == 4 (lightPool length via scene traversal count of pool-tagged
  PointLights: identify pool lights by checking WH_GAME.lightPool identity —
  pool[i] uuid set vs scene PointLights; player lantern excluded from the count)
  AND player lantern already present AND zero AmbientLight AND all 4 pool
  intensities == 0 before any socket assignment — all captured on the FIRST rAF
  tick, i.e. before first renderer.render. Confirmation read post-ready:
  WH_DEBUG.getLightPool().length === 4.
- Program sweep: capture WH_GAME.renderer.info.programs.length at (a) boot probe,
  (b) after 10 s organic walk in region A (page.keyboard.down('w') held with
  periodic direction changes via 'a'/'d' taps every 2 s — organic input only),
  (c) after A->B->A crossing (the L1 travel), (d) after 5 firebolt casts (L7 cast
  path, castCooldown waits from CFG read), (e) after teleport near lanternPost
  (-2,30) dwell 2 s and teleport to (4,-2) dwell 2 s. PASS if max - min <= +2
  across the whole run. Also record shader-light-count proxy: pool+lantern light
  objects present in scene must be EXACTLY 5 PointLights+1 Hemi+1 Dir at every
  sweep point (never 6 pool lights, never a 6th added post-boot).
- New/removed lights check: every sweep point re-counts scene PointLights by uuid
  identity vs boot; any uuid not in the boot set (or a missing one) = FAIL
  directly (M-05/M-19), independent of program growth.

### L6 — Socket handoff between lantern posts
- Method: WH_DEBUG.getLightPool() returns per-slot {intensity, socketId, x/y/z}
  (R2-3 sanctioned hook). Teleport to (-2,30) (post A1 area); read pool; PASS if
  slot whose socketId matches 'lanternPost@-2,30' (accept '<asset>@<-2>,<30>'
  coordinate form; ids are Devbot's — harness matches by parsed x,z within 0.1) has
  intensity > 0.5.
- Handoff: teleport to (4,-2) (post A2 area) and rAF-chain sample pool slot
  intensities every frame for 1.5 s. PASS if within 1.5 s the A1-targeted slot's
  intensity strictly decreases (toward 0 or its fade path) and the A2-targeted
  slot's increases; fade duration consistent with handoffFadeSec 0.35 (recorded
  from tick deltas; accept 0.2-0.75 s observed window); curves monotonic or
  single-dip. Evidence: tick trace ranges for both slots.

### L7 — Firebolt dynamic socket
- Cast path (organic, weave-proven): page.keyboard.press("1") selects belt slot 0
  (firebolt), confirm offhand via WH_DEBUG.getPlayer().getOffhand() == 'spell',
  then page.mouse.down(button="right") fires tryCast (player.js:205-208); wait
  castWindup + 0.3 s; windup completion spawns the bolt into game.firebolts
  (game.js:680-688).
- PASS bars: WH_DEBUG.getLightSockets().filter(id startsWith 'firebolt#') >= 1 while
  bolt alive (bolt liveness via WH_DEBUG.getFirebolts()); the pool slot whose
  socketId matches that bolt's id has intensity > 1.0 while alive; after bolt death
  (alive false, maxRange expiry per CFG spell.firebolt.maxRange), the socket list
  drops the firebolt id within 2 page frames — measured by a pre-armed rAF-chained
  recorder snapshotting socket ids every frame; frames_between(alive-last, id-gone)
  <= 2 (rAF-true frame count, no polling guesswork). Record the drop delta.
- Bolt world position including y: socket entries carry x/y/z (spec); if only x/z
  appear, cross-read WH_GAME.firebolts[i].pos.y (READ via WH_GAME — game.js:28) and
  record per amendment note 4.

### L8 — Flame cards (one-time sprites, additive, positioned)
- Passage (organic): walk/teleport near lanternPost (-2,30), dwell until that slot's
  intensity > 0.5 (L6 precondition).
- Scene traversal: count THREE.Sprite objects; PASS bars: exactly 4 created at boot
  (assert 4 exist post-boot and uuid set equals boot-probe sprite set — no
  creation/destruction after boot, cross-checked by the tick recorder's sprite-count
  column staying 4 for the entire run); material.blending === THREE.AdditiveBlending;
  material.map resolves to the ember texture (image src contains
  'particle-ember.png' — resolved through WH_ASSETS.MANIFEST.particleEmber);
  material.depthWrite === false && material.transparent === true; while near the
  post: the matching slot's sprite worldPosition within 0.3 of that slot's socket
  position (socket x/y/z from getLightPool, sprite pos from scene traversal), and
  every slot whose intensity <= 0.06 has sprite.visible === false; bob present:
  sprite y varies (>= 2 distinct y values across 30 frames, amplitude ~0.06,
  RECORD evidence).
- Sprite scale: record size ~0.55 with scale.y *1.4 as RECORD (spec says
  approximately; not a hard bar).

### L9 — New props wired (region B sockets)
- Load check: WH_ASSETS.isLoaded('banditCampfire') && isLoaded('lanternWaymarker')
  both true, isFailed both false, and WH_ASSETS.getMeta(...) non-null with plausible
  height (0.5 - 6). Stand-in avoidance: getMeta non-null implies a real template
  (cache-hit) per assets.js:228-231 — see amendment note 1 regarding the spec's
  nonexistent `standIn` field. Network 404 check: page.on('response') collector
  asserts no response in the session had status >= 400 for
  *bandit-campfire*/*b3-waymarker*/*particle-ember* URLs.
- Grounding: R1 A1 machinery (they are inside region B props; the floor re-run
  covers them) plus direct: Box3.setFromObject on each new instance (joined to
  CONFIG entries by x,z match within 1e-6) |min.y| <= 0.02.
- Socket proximity: teleport within 6 units of campfire entry (2.5,-52): PASS if
  getLightSockets() contains id matching 'banditCampfire@2.5,-52' (parsed coords
  within ±0.1); repeat for waymarker (-6.5,-47). Socket height sanity: socket y ==
  holder world y + groundHeight(asset) * heightFraction * scale within 0.15
  (computed against WH_ASSETS.groundHeight, not hardcoded).

### L10 — Readability floor (Weber contrast, ghoul @ 10 units)
- Subject: a region-A ghoul (regionA.enemies has one at (2,-30)). Ghoul chases when
  close, so the harness measures against the ghoul's LIVE position: for each target
  distance d in [5, 10, 20, 30] (WH_SMOKE: [10] only): read ghoul pos (WH_DEBUG
  .getEnemies()), teleport player to a point exactly d units from it with line of
  sight along -z bias toward camera-forward, forced render, canvas.toDataURL.
- Contrast method (primary, write-free): project ghoul root world pos to screen
  space via THREE camera projection inside evaluate; sample a target box (±10 px)
  at the projected torso (y + 0.9*characterHeight projected) and an annulus ring
  (radius 18-30 px, excluding target box) around it; luminance means L_g, L_b from
  the SAME forced frame; Weber contrast = |L_g - L_b| / max(L_b, 1).
- PASS bar (spec :237-241): contrast at 10 units >= 1.15; record all four distances
  numerically. If 10-unit bar fails but 5-unit passes -> FAIL-L10 recorded with
  numbers and the retune-protocol note attached (exactly-once CONFIG retune; never
  hacked by loosening the bar in the harness).
- The devbot spec's fog-toggle mask ("render with and without fog via two
  toDataURL frames") requires mutating scene.fog — a banned test-state write with no
  sanctioned hook (see amendment note 2). Harness records the annulus method as the
  implementation of the mask intent (local contrast against the local background
  the fog actually renders) and marks the deviation explicitly in the AC detail.

## Pre-Devbot smoke - EXPECTED (WH_SMOKE=1, filled at capture time)
| AC | Expected pre-Devbot | Evidence to capture |
|----|---------------------|---------------------|
| BOOT | current tree = R1 lighting: L1/L2/L4 FAIL (ACES, ambient 4.0, key light), L5 boot FAIL (0 pool lights), L8 FAIL (0 sprites), L6/L7 FAIL (no hooks -> hook-absent recorded) | consoleErr/pageErr counts |
| L1 | FAIL | ambient count 1 (current), hemi mismatch |
| L2 | position part FAIL (key light at +x/+z, not -z) | elevation calc numbers |
| L3 | FAIL (no lantern PointLight) | parent walk result |
| L4 | FAIL (ACESFilmic, exposure 1.6) | toneMapping enum print |
| L5 | FAIL (pool empty; programs baseline captured as floor reference) | program sweep |
| L6 | FAIL-hook-absent | WH_DEBUG key grep |
| L7 | FAIL-hook-absent + cast still viable (organic cast proof is a bonus check) | cast state trace |
| L8 | FAIL (0 additive sprites) | sprite count |
| L9 | FAIL (assets not in manifest pre-round; 404/no meta) | response collector |
| L10 | RECORD baseline (contrast numbers of the OLD rig become the improvement reference) | 4-distance table |
| FLOOR | PASS (R1 verdict PASS on shared server) | R1 JSON line |
Smoke profile expectations are my own pre-fix model, not Devbot's promise; the captured run is authoritative.

## Flake rule (same as R1)
- Retries up to 2 (fresh page reload between attempts) for infra-shaped failures
  only: runner exception, timeout, server 500, WH_DEBUG not ready, SwiftShader
  degenerate frame (all-zero sample). Deterministic assertion misses (numbers
  recorded, tolerance exceeded) are NEVER retried.
- Verdict per AC = LAST attempt; flake noted in detail; >= 3 flakes across the run
  = report "harness unstable, do not gate on this run" (BLOCK) instead of verdict.

## Scope + secrets check (AC-SCOPE)
- git status --porcelain set-diff: allowed mutation surface = exactly
  prototype/js/CONFIG.js, prototype/js/game.js, prototype/js/assets.js (devbot spec
  standing law :25-27) + tests/wh_world_r2_validation.py (my deliverable) +
  io/specs/* and io/reports/* R2-round docs + the R1 freeze-dirty inheritance list
  (reuse the R1 FREEZE_DIRTY + io/-pattern allowlist; apply the documented
  leading-3-char strip for porcelain unstaged lines, R1 A8 gotcha). PASS when the
  residual set is empty. Any 4th prototype/js file = BLOCK (devbot was told to STOP
  if it needs one — my job is to catch it, not forgive it).
- Secrets grep over `git diff` (key/secret/token/password assignment patterns) must
  be clean; greping the 3 allowed files' diffs for 'free' catches the player-facing
  "free" ban. Failures recorded as SCOPE FAIL / SECRETS FAIL evidence lines.

## Verdict protocol
Final stdout line of tests/wh_world_r2_validation.py is a single JSON object:
```
{"round": "world-r2", "verdict": "PASS|FAIL|BLOCK",
 "per_ac": [{"id": "L1", "verdict": "PASS|FAIL|RECORD|FAIL-HOOK-ABSENT",
             "evidence": "..."}],
 "floor": {"r1": {"verdict": "PASS", "per_ac": {...}, "waivers": []}},
 "flakes": 0, "notes": "..."}
```
- Exit code ALWAYS 0.
- Round verdict (from harness JSON + Testerbot judgment): PASS only when L1-L9 and
  L4 bars all PASS, L10 10-unit bar PASS (or FAIL-L10 within retune protocol on a
  first failure — verdict FAIL-RETUNE-PENDING, not PASS), L2 position+probe both
  PASS, FLOOR PASS (waivers allowed only for the enumerated R2-round artifacts), and
  SCOPE+SECRETS clean.
- Independent BLOCKs: new light/sprite objects after boot (L5 identity check),
  program growth > +2, any WH_DEBUG hook-absent on getLightPool/getLightSockets
  (they are R2 deliverables, not optional reads — absence is a Devbot miss, recorded
  FAIL-HOOK-ABSENT on the dependent ACs and verdict BLOCK), scope violation, secrets
  hit, R1 floor hard FAIL.
- Retune loop (pre-authorized once, spec :243-248): first-time numeric floor misses
  on L4/L5/L10/L9 with otherwise-correct logic -> verdict FAIL-RETUNE-PENDING with
  the exact numbers Devbot needs; a SECOND identical failure = STOP and report.

## Amendment notes (spec-of-record mismatches found while authoring against 26e7a60)
1. Devbot spec L9 (:225-226) validates stand-in absence via
   `WH_ASSETS.getMeta(...).standIn !== true` — getMeta returns
   {height,width,groundMinY} only (assets.js:228-231); there is no standIn field
   anywhere. Harness uses isLoaded && !isFailed && getMeta non-null (cache-hit
   implies real template; makeStandIn only fires on cache miss, assets.js:206-208).
   Spec's standIn reads are satisfied vacuously; flagged for amendment awareness.
2. Devbot spec L10 prescribes "render with and without fog via two toDataURL
   frames" — mutating scene.fog is a direct scene-state write and no sanctioned
   hook exposes fog; this contradicts the organic-path law the same spec restates
   (:190-193). Harness implements the write-free annulus-mask variant of the same
   mask intent (see L10 method); if IO/Devbot prefer the literal method, ship a
   WH_DEBUG measurement hook for fog and I re-run both ways.
3. Devbot spec L2 "plane at world center facing -z" — a test-created plane is scene
   instrumentation; harness treats it as the single sanctioned test-geometry write,
   sequences it strictly after the L5 program sweep and L8 sprite identity checks,
   and reloads the page immediately after, so it cannot contaminate
   program/light/sprite counts.
4. WH_DEBUG.getFirebolts (game.js:560-564) returns {x,z,alive} — no y, though the
   spec (:147-148) says bolts carry world position with y for socket height. Harness
   reads bolt y via WH_GAME.firebolts[i].pos.y (READ-only, WH_GAME exposed at
   game.js:28) and via the new getLightSockets y field; flagged so Devbot knows
   either source is fine but the hook spec's "y included" only holds through
   getLightSockets.
5. Devbot spec R2-3 (:167) example socket id prints 'langernPost@x,z' (typo) and
   :140 lists the same map — harness matches socket ids by PARSED coordinates
   ('<asset>@<x>,<z>' with ±0.1 numeric compare), never by literal string equality,
   so id-spelling drift cannot false-fail an AC.
6. Devbot spec R2-3 pool paragraph says color "0xffd9a0-class comes from CONFIG"
   while the CONFIG block it mandates (:125-132) sets 0xffc27a — harness reads
   CFG.lightPool.color and validates sprite/light tint derivation against THAT value
   only; the 0xffd9a0 mention is treated as prose, not a bar.
7. Devbot spec L5 (:213-218) says "verify via getLightPool() len == 4 on the first
   rAF tick" — a post-ready evaluate may miss the literal first tick; harness adds
   the pre-load add_init_script rAF probe (see Harness) which snapshots scene light
   identity on the true first tick, then confirms with getLightPool(). Not a spec
   mismatch — a determinism upgrade for the same bar, noted for transparency.
8. Spec :128 "store game.lantern" vs :106-110 "PointLight ... parent it under
   yawFrame" vs L3's "parented within the player root/yawFrame chain" — harness
   accepts any depth in the root/yawFrame subtree (walk .parent to exhaustion);
   exact attach depth is Devbot's choice, the AC only needs world-delta parity with
   the player (tested directly).