# TESTERBOT SPEC — Witch Hunter World R5: Collision + World Bounds Validation (gate step 2)

Author: Testerbot (independent validator-author; Claude Code opus). Date: 2026-10-02.
Devbot spec of record: io/specs/devbot-spec-wh-world-r5.md (read-only; mismatches = amendment notes
C1..Cn, never patched in the spec by me). Tree at authoring 0e51bd7 (R5 spec commit); `git diff
818d8bc 0e51bd7 -- prototype tests` is EMPTY, so all R5 code diffs are measured against 818d8bc (R4
marker). Authority: doc 61 P0-5, M-13/M-15/M-16, P1-4 camera half. HANDOFF laws 1-8, R2 part10 /
R4 part06 floor waiver classes, R3 A5/A6, R4 B7/B11 (A2 bar = pre + 0.05, 3x same-build noise
0.0145) inherited verbatim except where C-notes re-scope them.
Live anchors (verified at 0e51bd7; spec lines drifted, C2): CONFIG.js world.groundRadius 90 :60,
regionA.spawn (0,45) :78, A ghoul (2,-30) :86, regionB.spawn (0,-45) :139, boundary.z -25 :218-220,
chokepoint x0 w8 :225-228, player.radius 0.7 :269, camDistance 7/Min 3/Max 14 :270-272, camPitch
-15/65 :273-274, camHeight 2.6 :275, holdAtBoundaryMargin 1.5 :391; props 106 (A 44 + B 62), enemies
3+3. region-manager.js clampPlayer :99-113, clampEnemyToHomeSide :116-133 (enemy.js:289), ground
CircleGeometry :297 + repeat :253. game.js clampPlayerToBounds :467-477 (early return :472), scene.fog
FogExp2 :69/:511, WH_DEBUG teleportPlayer :561 / setCameraYaw :575 / getAssetMeta :545. player.js
pitch clamp :231, wheel :233-236, updateCamera :896-947 (lock-on :907-930, follow :931-945).
assets.js GROUND_META :98/:127-131, getMeta :279-284, blob @818d8bc 4d27e6f9 (R4-frozen).

## Harness + invocation contract
1. File: tests/wh_world_r5_validation.py = `cat tests/r5parts/part01..NN.py` via r5parts/build.py
   (law 8: re-cat, py_compile, dup-def check). Playwright sync, headless chromium
   `--enable-unsafe-swiftshader`, viewport 1920x1080, dsf=1.
2. Env: `WH_BASE_ROOT`, `WH_W5_PORT` (0 = ephemeral self-spawn), `WH_SMOKE=1` (headings 0/90/180/270
   only; subprocesses still run), `WH_W5_FLOOR=0` (skip R2+R1 subprocesses = SKIP-NOTED, never PASS),
   `WH_W5_HEADINGS` (default 0,45,...,315). Subprocesses: WH_BASE_ROOT=<our root>, WH_R1_PORT /
   WH_R2_PORT = our port (R4 B7), WH_R2_FLOOR=0 (R3 A5).
3. Server identity (law 5): reuse only if served js/CONFIG.js contains `lightPool`, `ambientIntensity:
   0`, `internalResDiv`, `pixelatedBodies`, `playerMargin` AND bytes == worktree CONFIG.js; else
   self-spawn prototype/server.py on an ephemeral port, kill on exit. NEVER 8791; ':8791' anywhere in
   this run's request log or subprocess output = BLOCK.
4. Laws: render + toDataURL in ONE evaluate; settle (|dcam| < 0.01 over 2 polls, vz<1) before reads;
   NaN guards on player+enemy pos; per-AC try/except; exit 0; final line = JSON verdict; no
   key-shaped literals; wall-generous polls. Sanctioned writes: teleportPlayer, setCameraYaw, enemy.pos
   (R5-1e), R5-2 CONFIG route (each rewrite exactly once). Walking = real 'w' keydown with
   setCameraYaw(h+180) (W = (sin(yaw+PI), cos(yaw+PI)), player.js:753); camera = real wheel + LMB drag.

## Pre-Devbot smoke — EXPECTED (tree = 0e51bd7; captured run is authoritative)
| AC | Expected pre-Devbot | Evidence to capture |
|----|---------------------|---------------------|
| BOOT | PASS; reuse refused (no playerMargin) -> self-spawn | identity result, port |
| R5-1 | FAIL: world.playerMargin undefined; walk r > 90 (no radial clamp); snapback stays at r+5 | per-heading r_max, S_rim vs S_ref baseline |
| R5-2 | FAIL: spawnReport undefined; recompute = 1 violation (A ghoul (2,-30): z < -23.5, B side) | recompute table, injection result |
| R5-3 | FAIL: settled cam y = 2.6 - 14*sin15 = -1.02 at pitch -15 / dist 14; d flat 14 over pitch | camera table (pitch x dist) |
| R5-4 | FAIL: lanternPost A1 walk tunnels (x < -2); radii table RECORD | min dist, radii |
| R5-5 | PASS: organic corridor walk A->B->A; R2 floor L1 PASS (other L per inherited waivers) | activeId trace, R2 JSON |
| PRES | PASS: dirty = this valspec + pre-existing untracked tests/artifacts/r4-screen-*.png (C9); R1 floor PASS-via-waivers | porcelain, R1 JSON |

## AC-R5-1 (M-15) — Radial clamp, 8-heading sweep, rim seam
- (a) Key: WH_CONFIG.world.playerMargin is a number with player.radius (0.7) <= m <= 3.0;
  world.groundRadius === 90 (playable != visual; R1/R2 anchors key on 90). r_play = 90 - m.
- (b) Sweep: for h in WH_W5_HEADINGS, rim point T = r_play*(sin h, cos h); region = A if
  T.z > -23 else B (A: 0,45,90,270,315; B: 135,180,225). B entered via the R2 L1 stepped
  teleport at x=-2 (activeId asserted). Teleport to (r_play-6)*(sin h, cos h) (if inside an R5-4
  collider: h += 5deg until clear, recorded); setCameraYaw(h+180); hold W until r stationary
  (|dr| < 0.01 over 3 polls) or 180 s wall; r = hypot(x,z) sampled every poll. Bars per heading:
  max r <= r_play + 0.02; final r >= r_play - 0.30 (reached the rim, not stalled); final pos on
  the home side; no NaN.
- (c) Snapback: per heading, teleport to (r_play+5)*(sin h, cos h): within 2 polls r <= r_play+0.02.
- (d) Corner (C5 early-return trap): A active, teleport (95,-30) -> z >= -25 AND r <= r_play+0.02;
  B active, teleport (95,-20) -> z <= -25 AND r <= r_play+0.02 (both clamps in one frame).
- (e) Enemies: per region, live enemy[0] (NaN-guarded) pos written to (r_play+5) radially on its
  home side: within 2 polls r <= r_enemy + 0.02 (r_enemy = 90 - enemy margin key if Devbot adds
  one, else r_play; key recorded) AND home-side hold kept (A z >= -23.5, B z <= -26.5).
- (f) Rim seam (M-15 -> SwiftShader truth): at each heading's final clamped pose, settled
  (auto-follow holds camYaw = h+180 = looking outward, pitch 22 default), ONE evaluate forced
  render + toDataURL (960x540). Strips cols [0.10w,0.30w] U [0.70w,0.90w] (player body
  excluded), rows [0.05h,0.70h]; per-row mean luma L(y) = 0.2126R+0.7152G+0.0722B; S = max_y
  |L(y+2) - L(y)|. S_ref(region) = same probe at region spawn, default yaw/pitch, settled.
  Bar: S_rim(h) <= S_ref(region) + 10 for every heading. Geometry (C4): ground mesh radius R_vis
  and map.repeat RECORD; texel density GATE: repeat/R_vis == 12/90 +-2%; expectation (RECORD)
  R_vis >= r_play + 1.1*d95, d95 = sqrt(ln 20)/fogDensity (A 144.2, B 72.1). First numeric miss
  on (f) with (a)-(e) PASS = FAIL-RETUNE-PENDING.

## AC-R5-2 (M-16) — Boot spawn validator
- Readable surface (C7): WH_DEBUG.getRegionManager().spawnReport = {props:int, enemies:int,
  violations:[{kind:'prop'|'enemy'|'spawn', region, index, name, x, z, why}], exempt:[...]},
  written once at boot for BOTH regions from WH_CONFIG (independent of build state) + one console
  line prefixed "[WH spawn-validator]". Validator logs; it never throws.
- Checks (validator performs; harness recomputes independently from WH_CONFIG + getAssetMeta):
  (i) home side: A props z > -25, B props z < -25; A enemies z >= -23.5, B enemies z <= -26.5
  (boundary.z +- holdAtBoundaryMargin); (ii) hypot(x,z) <= r_play for every prop + enemy;
  (iii) each region spawn outside every collider: |spawn - c_i| >= R_i + 0.7 (R_i per R5-4).
- Bars: report present; props === 106 and enemies === 6 (live CONFIG counts); violations === [];
  harness recompute === []; A ghoul: CONFIG z >= -23.5, OR a gate-guard flag on that entry listed
  in exempt[] with runtime ghoul z >= -23.5 after 5 s wall; regionA/B props arrays byte-identical
  to 818d8bc (no prop moved to dodge the validator).
- Negative control (separate context, sanctioned route): rewrite served CONFIG.js A
  `{ asset: 'gravestoneObelisk', x: -10, z: 20,` -> `z: -40` and B `{ type: 'bandit', x: 0,
  z: -60 }` -> `z: -95`; each match count === 1 (else FAIL). Bars: boot completes (WH_DEBUG ready,
  0 pageerror); violations >= 2 and name exactly those two entries (side; radius).

## AC-R5-3 (M-13) — Camera ground clamp + distance-by-pitch (organic input only)
- A spawn, no lock (LMB mousedown also fires tryAttack :196 — harmless at spawn, recorded). Wheel
  x10 down/up sets camDist 14 / 3 (player.camDist readback); LMB drag sets pitch; matrix dist
  {3,7,14} x pitch {-15,0,22,45,65} (ends via the clamp). Per cell: camera.position.y polled through
  the transition (min kept); settled y and d = |cam - (player.pos + (0,camHeight,0))|.
- Bars: (a) EVERY sampled y >= 0.3 (M-13); (b) settled y >= 0.395 in all 15 cells (audit 0.4
  clamp; shake 0.05*0.6 = 0.03 fits inside the 0.3 bar); (c) lock-on branch (C8): engageLockOn on
  A bandit[0] from 6 units, pitch -15, dist 14: min y over 10 s wall >= 0.3, settled >= 0.395.
- By-pitch law (spec: shrinks as pitch rises): at camDist 14, settled d over pitch {0,22,45,65}
  non-increasing (step <= +0.05), d(65) <= 0.85*d(0), d >= camMinDistance - 0.05; player.camDist
  still 14 after the sweep (effective cap, not a wheel-state mutation). Default framing preserved:
  pitch 22 / camDist 7 -> d = 7 +- 0.10, y = 2.6 + 7*sin22 = 5.22 +- 0.10. Pitch < 0 d = RECORD.
  Devbot's report pins the formula; harness RECORDs measured d vs formula per cell.

## AC-R5-4 — Prop colliders
- R_i = getMeta(asset).width * scale / 2 (spec design 3); table RECORD for all 106 props. Corridor
  exempt set E = props whose circle meets x in [-4,4], z in [-31,-19]: expected [] (RECORD, C6).
- (a) lanternPost A1 (-2,30) s2.4: start (-2 + R + 0.7 + 4, 30), setCameraYaw(90) (W = -x), hold W
  until stationary / 120 s wall. Bars: every sample |p - c| >= R + 0.7 - 0.02; x never < -2;
  final |p - c| <= R + 0.7 + 0.30 (contact made, not stalled).
- (b) Inside pushout, every prop (B after crossing; smoke 10/region): teleport c_i + (0.1,0)
  (avoids the d=0 NaN), 2 polls: no NaN; isolated props (no other collider within R_i+R_j+1.4, not
  within R_i+0.7 of plane or rim) -> |p - c_i| >= R_i + 0.7 - 0.02; clustered/edge props RECORD.
- (c) Corridor = R5-5(a) walk: |x| <= 0.10 throughout (no lateral collider push on the gate path).

## AC-R5-5 — Crossings re-proof
- (a) Organic: teleport (0,-15), setCameraYaw(0), hold W: activeId -> regionB.id within 240 s
  wall, z < -25 after flip; then setCameraYaw(180), hold W: back to A within 240 s. Trace RECORD.
- (b) R2 floor subprocess (unchanged file, env per contract 2). Bars: L1 PASS un-waived (stepped
  path x=-2 passes mossBoulder (-2.5,-6.5) / graveMound (-4.5,-12.5): pushout allowed, crossing
  must complete). L3/L5/L6/L9/BOOT PASS or WAIVED only by: L10-alone R3-artifact (scaled
  re-measure), SCOPE residual inside R5 PRES surface (R3 A6), NEW class R5-collider-teleport (C10).
  Any other fail = BLOCK. L4 + L10 feed the R1 A4 re-verify (C3).

## AC-PRES — Preservation (vs 818d8bc: committed prototype/+tests/ paths + porcelain -uall, 3-char strip)
- Allowed EXACTLY: prototype/js/{region-manager,CONFIG,game}.js, [prototype/js/player.js pending C1],
  io/specs/*-r5*, io/reports/*r5*, tests/wh_world_r5_validation.py, tests/r5parts/*,
  tests/artifacts/r5-*, tests/artifacts/r4-* (C9). Any other prototype/ file (assets.js, enemy.js,
  anim.js, region-defs.js, style.css, index.html, GLB/PNG) = BLOCK.
- Hunks: game.js only inside clampPlayerToBounds :467-477; region-manager.js only clampPlayer,
  clampEnemyToHomeSide, adjacent new helpers (radial/collider/validator), ground disc + repeat
  (:253,:297) + mist size; CONFIG.js only world{} (playerMargin, visual-ground keys), player{} camera
  keys adjacent :270-279 (C1), regionA.enemies ghoul :86; props arrays, lighting, renderer, assets{}
  byte-identical. player.js (if C1 allows) only inside updateCamera; wheel/mousemove byte-identical.
- assets.js blob === 4d27e6f9 (R4-frozen body->PNG table + swap); rigged PNGs + GLBs === 818d8bc
  blobs; index.html sha256 === 9ad39b809bc4...dc32; v7 temp-copy rebuild (R3 A8) 0 errors, builds/ clean.
- R1 floor (R4-5 method verbatim): A1 PASS un-waived; waivers only A2-dev-baseline (B11: post <= pre
  + 0.05; pre = smoke capture tests/artifacts/r5-pre-a2.json), A3-settle-subprobe, A4-nightrig (C3),
  A6/A7-hash-drift, A8-surface (residual inside this surface). Any other fail = BLOCK.
- Secrets: `git diff 818d8bc` + untracked contents: msy_[A-Za-z0-9]{8} + key/token/secret/password
  assignment patterns = 0; player-facing "free" in added prototype lines = 0.

## Flake rule (same as R1/R2)
- Retries up to 2 (fresh reload) for infra-shaped failures only: runner exception,
  timeout, server 500, WH_DEBUG not ready, SwiftShader degenerate frame (all-zero),
  screenshot blank. Deterministic number misses (dims, pair ratios, triangles, timing
  medians, subprocess verdicts) are NEVER retried. Verdict per AC = LAST attempt;
  >= 3 flakes in the run = BLOCK ("harness unstable, do not gate on this run").

## Verdict protocol
`{"round":"world-r5","verdict":"PASS|FAIL|BLOCK|FAIL-RETUNE-PENDING","r_play":0,"margin":0,
 "sweep":[{"h","region","r_max","r_final","snap","S_rim","S_ref"}],"validator":{"report","recompute",
 "neg"},"camera":[15 cells],"colliders":{"radii":[],"exempt":[],"a1":{}},"crossing":{"organic":{},
 "r2":{}},"per_ac":[{"id","verdict","evidence"}],"floor":{"r1":{"waivers":[],"a2_pre":{},"a2_post":{}},
 "r2":{}},"flakes":0,"notes":""}` — exit 0 ALWAYS. PASS iff R5-1..5 + PRES PASS (enumerated waivers
only; SKIP-NOTED gating AC => never PASS). First numeric miss on margin/radii/R5-1(f) with mechanics
PASS = FAIL-RETUNE-PENDING (exactly-once retune, C12); SECOND identical miss = STOP. BLOCKs: scope,
secrets, index.html drift, any :8791, non-artifact floor fail, >= 3 flakes.

## Amendment notes (spec-of-record vs live tree 0e51bd7; I own the bars)
C1 (NEEDS IO RULING): camera clamp lives in player.js updateCamera, spec PRES omits player.js.
   Provisional: player.js hunks ONLY inside updateCamera :896-947, else BLOCK.
C2. Anchor drift: CONFIG +2 lines (:60, :218-220, :78/:139, :273-274); clampPlayerToBounds :467-477
   not :455-465; GROUND_META :98/:127-131 not :90/:119-123.
C3. R4 A4-nightrig needed region-manager/game/player unchanged; R5 edits them -> A4 re-verifies via
   this run's R2 floor L4 PASS + L10 PASS or scaled c10 >= 0.25 (R3 deviation 3).
C4. Fog is FogExp2; fogNear/FarFactor (:70-71) are dead keys, so "B shortfall 135 > 90" is void:
   d95 A 144.2 > B 72.1 (A is the larger shortfall). Gate = seam luma + texel density.
C5. clampPlayerToBounds returns early when the boundary clamp fires (:472): radial + collider must
   still run that frame (R5-1d).
C6. GROUND_META.width = identity X-extent pre-rotY: canopy-wide for trees (s 6.5-10.4), length for
   fences/logs; circles may over-block. Gates = invariants + contact; radii RECORD.
C7. Validator output surface unspecified -> pinned RegionManager.spawnReport (no game.js hunk).
C8. Lock-on branch builds its own want (:907-930): clamp covers both. The by-pitch cap cannot fix
   clearance (danger is pitch < 0: -1.02); clearance = clamp. 0.85 ratio is my bar.
C9. Untracked tests/artifacts/r4-screen-*.png pre-exist at 0e51bd7: inherited, allowed.
C10. NEW waiver R5-collider-teleport: R2 L fail (not L1) whose teleport target (r2 :618/:631/:871 or
   computed) recomputes in-run inside a collider (|t-c| < R+0.7); evidence = displacement only.
C11. Enemy radial clamp pinned inside clampEnemyToHomeSide (enemy.js = BLOCK). C12. Exactly-once
   retune spans margin, collider radii AND R5-1(f) ground extent; 2nd identical miss = STOP.
C13 (IO RULING granted 2026-10-02): C1 accepted — player.js enters the AC-PRES
   allowed surface with hunk law "only inside updateCamera :896-947"; wheel/
   mousemove/lock-on-framing bytes unchanged. The camera ground clamp + by-pitch
   cap cannot live anywhere else (the clamp math IS updateCamera). Devbot's
   report must pin the effective-dist formula; the harness RECORDs d vs formula.
