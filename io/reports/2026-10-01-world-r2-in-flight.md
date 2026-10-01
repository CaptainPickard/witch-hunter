# World R2 in-flight state — 2026-10-01 (for next auto-finisher tick)

Branch state (verified 08:30Z, worktree /tmp/wh-worldfeat):

  8765ded  WIP (LOCAL ONLY, NEVER PUSH): world-r2 chunks A+B unvalidated
  46454c5  docs: world-r2 gate specs (IO devbot spec + Testerbot valspec)
  26e7a60  merge: dev (whanim2 dc697ce) into feat/world-visuals
  dc697ce  feat: whanim2 (on dev, pushed)

Freeze table:
- prototype/... js code: R2 complete-but-UNVALIDATED in 8765ded. Do not
  stack new rounds on it. Do not push it. Treat as the R2 candidate.
- io/specs/devbot-spec-wh-world-r2.md: IO-authored authority, committed.
- io/specs/testerbot-spec-wh-world-r2.md: Testerbot-authored valspec,
  350 lines, committed. Its amendment notes 1-8 are binding context for
  the run stage.
- tests/wh_world_r2_validation.py: MISSING (3 authoring lane deaths).
  This is the next deliverable.
- tests/wh_world_r1_validation.py: unchanged, is the floor gate.

Diff summary in 8765ded vs 46454c5 (3 files, +208/-20):
- CONFIG.js: renderer.toneMappingName 'Neutral', exposure 1.15; lighting
  block rewritten (hemiBaseIntensity 1.35 fill, moon 0xa8bce6 @0.45 elev
  30 azimuth 0, lantern 0xffb060 @6.5 distance 12 decay 2 flicker 5%,
  left-hip anchor offset [-0.32,0.95,0.08]); NEW lightPool block (size 4,
  color 0xffc27a, distance 11, decay 2, handoffFadeSec 0.35); NEW
  lightSockets block (lanternPost 0.85/1.6, banditCampfire 0.55/2.4,
  lanternWaymarker 0.80/1.8); regionB props += banditCampfire (2.5,-52)
  + lanternWaymarker (-6.5,-47).
- game.js: setupLights = hemi + moon dir + player lantern (re-parented
  to yawFrame post-player via attachPlayerLantern) + pool creation at
  boot (4 PointLights + 4 flame-card Sprites, ember texture via
  WH_ASSETS.resolveUrl) BEFORE first render; computeSockets() from
  CONFIG tables for the ACTIVE region + firebolt dynamic sockets;
  poolTick(dt) nearest-socket handoff w/ exponential fade (0.12s on
  socket change, handoffFadeSec otherwise) + flame card visibility gate
  (intensity > 0.06) + bob; called in loop between applyCameraShake and
  updateHud; WH_DEBUG.getLightPool/getLightSockets hooks (per-slot
  intensity + socketId '<asset>@<x>,<z>' or 'firebolt#<i>' + xyz).
- assets.js: MANIFEST += banditCampfire (m15-bandit-campfire-pixelated),
  lanternWaymarker (b3-waymarker-pixelated). No particleEmber entry
  (amendment A1: texture loads via resolveUrl in game.js).

Devbot self-checks already run (chunk B): brace depth 0, scoped files
correct, no class/arrow/backtick introduced.

NOT DONE (blocked on Testerbot lane):
- tests/wh_world_r2_validation.py (authoring + run)
- R1 floor re-run on the R2 tree
- verdict JSON + IO PASS/FAIL ruling
- validated-commit + push feat/world-visuals
- R2 implementation report io/reports/2026-10-01-world-r2-implementation.md

Next tick: author harness (write-only dispatch, method table embedded in
testerbot-spec-wh-world-r2.md + lane-failure report), then run + verdict.
If Testerbot lane dies again: STOP, update lane-failure report, stay armed.

— IO, job 2c7556f7f609, 08:30Z