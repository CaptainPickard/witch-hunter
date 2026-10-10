# TESTERBOT SPEC — EPR1 "ER-Parity Combat Values" validation

Repo: /workspace/witch-hunter, harness: `scratch/erparity/wh_erparity_validation.py`
(authored by this spec, validator-owned). Target under test: Devbot's EPR1 build
worktree (`../wh-erparity`, origin/dev + task spec). Pre-build smoke baseline was
captured against origin/dev `b94a35c` via a temporary worktree
(`/workspace/wh-erparity-test`, removed after smoke).

## 0. Authority and scope

- Contract of record: `io/specs/devbot-spec-wh-erparity-combat.md` (EPR1, 19 ACs:
  A1-A4, B1-B5, C1-C3, D1, E1-E3, F1-F3). This file is the VALIDATION contract:
  per-AC probe mapping, organic input sequence, sim-frame window math, pass
  criteria, and live-tree anchors verified by Testerbot.
- This spec does NOT amend the impl spec. Ambiguities Testerbot hit are listed
  in §9 with the operative reading used; real conflicts are escalated via the
  impl spec's §0 amendment protocol (not improvised).
- Git gate: Testerbot does not commit, push, or dispatch. Validator outputs
  are whitelisted in §10 Baseline Manifest (sha256 frozen).

## 1. Sim-frame currency (binding; reconciles spec "30 Hz" language)

The spec authored timing values as design-time 30 fps frames (rollIFrameWindow
0.433 = ER's 13 frames @30 Hz = 13/30 ≈ 0.4333 s). The game's rAF loop clamps
`dt = min(dtMs/1000, CFG.loop.maxDt)` at **maxDt = 1/20 = 0.05 s per frame**
(origin/dev `prototype/js/CONFIG.js:777`; game.js:1176 — Law 2). Therefore:

- **Seconds are the number of record** (config values are seconds).
- **In-harness frame counts are GAME frames at 0.05 s/frame**, with ±2 frames
  tolerance per spec section 3.5.
- Conversion: `frames = seconds / 0.05`.

Canonical anchors for this round (verified at origin/dev b94a35c):

| Value | seconds | game frames |
|---|---|---|
| hold→sprint threshold | 0.35 | 7.00 |
| roll i-frames (A4) | 0.433 | 8.66 → gate [7,11] |
| roll duration (kept) | 0.45 | 9.00 |
| backstep duration (A2) | 0.30 | 6.00 → gate [4,8] |
| backstep i-frames (A2) | 0.20 | 4.00 → gate [2,6] |
| guard-raise delay (B3) | 0.13 | 2.60 → gate ≈ 3 frames |
| slashR2L total | 1.50 | 30.00 |
| slashR2L dodge threshold 0.90 | 1.35 | 27.00 → gate [25,29]+ |
| slashR2L guard threshold 0.95 | 1.425 | 28.50 → gate [27,31]+ |
| slashR2L move threshold 0.65 | 0.975 | 19.50 → gate [18,22]+ |
| slashR2L bufferFrom 0.5×windup (0.285) | 0.285 | 5.70 → gate [4,8] |
| slashR2L chainOpen onset (0.97 s from start = 0.20 into recover) | 0.97 | 19.40 ±2 |
| slashL2R total | 1.67 | 33.40 |
| slashL2R dodge/guard/move | 1.503 / 1.5865 / 1.0855 | 30.1 / 31.7 / 21.7 |
| slashL2R bufferFrom (0.40) | 0.40 | 8.00 |
| slashL2R chainOpen onset (1.32 s) | 1.32 | 26.40 ±2 |
| thrust total | 1.00 | 20.00 |
| thrust dodge/guard/move | 0.90 / 0.95 / 0.80 | 18.0 / 19.0 / 16.0 |
| thrust bufferFrom (0.20) | 0.20 | 4.00 |

Provenance table (design frames @30 Hz → seconds → game frames): kept in the
impl notes (F1); this spec gates against the seconds and game frames columns
only.

## 2. Harness conventions (Frame-Clock Laws, binding)

- Sampler = `window.__IO_SAMPLERS[<name>]`, `{rows:[...], frame:i, stop()}`,
  rows pushed per rAF BEFORE the tick's re-arm; `install_sampler` returns
  synchronously (Law 1). Every organic act has its sampler installed FIRST
  (Law 3). Drain via short `page.evaluate` (never a pending evaluate_handle).
- Each row: `{f, attacking, rolling, blocking, blockActive, backstep, iframes,
  stamina, hp, comboIndex, comboQueued, moveId, phase{stage,t,dur}, elapsed,
  pos{x,z}, moveDir{x,z}}`. Frame index `f` is the harness's game-frame clock.
- Organic inputs only: `page.keyboard` / `page.mouse` real events. WH_DEBUG
  reads are READS; the only writes are setup acts (teleportPlayer,
  setCameraYaw, setStamina, breakLockOn, killPlayer/respawnAt for cleanup) —
  Law "organic-path inputs only; direct state mutation never as a test act".
- Poll loops: short evaluates against live `attackTotal - attackTimer`
  (seconds) to hit threshold targets; each observed effect is then gated in
  GAME FRAMES via sampler rows. Tolerance ±2 frames everywhere unless a
  narrower gate is listed in §3.

## 3. Per-AC validation mapping

### A1 — release-of-key dodge with direction rolls

- Probe: fn `ac_a1`, sampler name `a1`.
- Setup: teleport to (2.5, 74), camYaw 180°, stamina 100, breakLockOn.
- Organic sequence: `keyboard.down('KeyW')`; poll until `moveDirWorld` live
  (|x|+|z|>0.05); `keyboard.down('Space')`; record `f_dn`; `keyboard.up('Space')`
  inside the same wall burst (<7 sim frames); wait 2500 ms; release W.
- Sim-frame window math: tap = Space-held <7 frames; effect = roll begins on
  the frame AFTER Space-up at latest.
- PASS criteria:
  1. Some row with `rolling=true` exists.
  2. No row with `f <= f_up` (frame recorded at the key-up) has `rolling=true`
     (release-gate: pre-build rolls on keyDOWN → this gate is the wiring
     discriminator).
- Anchor: `player.js:247-249` (Space keydown → tryRoll) at b94a35c;
  post-build this site must move the firing decision to keyUP.
- Pre-build expected: **FAIL** (roll fires on keydown; early-roll row present
  at `f <= f_up`).

### A2 — tap dodge with no direction = backstep

- Probe: fn `ac_a2`, sampler `a2`.
- Setup: teleport; no move keys held.
- Organic: `page.keyboard.press('Space')` (fast down/up, <7 frames).
- Window math: backstep duration 0.30 s = 6 frames (gate [4,8]); backstep
  i-frames 0.20 s = 4 frames (gate [2,6]); stamina cost 20; distance 2.5 m.
- PASS:
  1. `backstep=true` observed and `rolling=true` never observed.
  2. max `iframes` observed in [0.15, 0.25] (0.20 ±1 frame @0.05).
  3. stamina spent ≈ 20 ±4.
- Anchors: `player.js:329-348` (tryRoll) at b94a35c — the whole block has no
  backstep branch today (A2's anchor *is the absence*; post-build inserts the
  no-direction branch here or a sibling).
- Pre-build expected: **FAIL** (no `backstep` symbol, roll behavior instead).

### A3 — hold ≥ 0.35 s = sprint, release does not roll

- Probe: fn `ac_a3`, sampler `a 3`.
- Setup: teleport; W held.
- Organic: W down → Space down → hold until sampler `frame - f_dn >= 9`
  (0.45 s ≥ 0.35 s) → Space up → observe 2500 ms.
- Window math: hold threshold 0.35 s = 7 frames; we hold 9+.
- PASS:
  1. `sprinting=true` at some row while Space held.
  2. No `rolling=true` row in the FULL window.
  3. `rolling=false` at sample end.
- Anchors: Space keydown at `player.js:247-249`; sprint flag consumed at
  `player.js:876` (`sprintingNow = self.sprinting && !blocking && stamina>0`).
- Pre-build expected: **FAIL** (Space never raises `sprinting`; roll fires).

### A4 — rollIFrameWindow = 0.433

- Probe: fn `ac_a4`, sampler `a4` + direct CONFIG read.
- Organic: same as A1 (W held, Space tap).
- PASS:
  1. `WH_CONFIG.player.rollIFrameWindow == 0.433` (exact).
  2. `WH_CONFIG.player.rollDuration == 0.45` (kept).
  3. Effect: count of frames with `iframes > 0.001` in [7, 11] (8.66 ±2).
- Anchors: `CONFIG.js:558-559` rollDuration/rollIFrameWindow at b94a35c;
  tryRoll sets `iframes = CFG.rollIFrameWindow` at `player.js:339`.
- Pre-build expected: **FAIL** (iw=0.35; iframe row count ~7).

### B1 — per-move cancel matrix (dodge 0.90, guard 0.95, move fractions)

- Probes: `ac_b1_dodge` (dodge column via `b1d`), `ac_b1_early_guard`
  (1-frame-early guard acceptance via `b1e`), `ac_b4_move_cancel` (`b4`).
  B1's light column is exercised by B2 (chain onset at light threshold) and
  B5 (buffer at bufferFrom fires at the light cancel point) — the light column
  gate is "chain move begins within ±2 frames of `chainOpenSec` after recover
  start" = B2's gate.
- Matrix rows driven per move (seconds → game frames; gates ±2 frames):

  | move | total | dodge@0.90 | guard@0.95 | move@0.65/0.80 |
  |---|---|---|---|---|
  | slashR2L | 1.50 / 30f | 1.35 / 27f | 1.425 / 28.5f | 0.975 / 19.5f |
  | slashL2R | 1.67 / 33.4f | 1.503 / 30.1f | 1.5865 / 31.7f | 1.0855 / 21.7f |
  | thrust | 1.00 / 20f | 0.90 / 18f | 0.95 / 19f | 0.80 / 16f |

- Organic dodge flow (slashR2L first): LMB → poll `getMoveDef().phase.stage
  == 'strike'` (post bufferFrom, pre dodge fraction) → organic Space tap →
  keep sampler on through swing end and roll end.
- PASS dodge: `rolling=true` first appears at `elapsed ∈ [dodge·total - 2f,
  dodge·total + 2f]`; no `rolling` row before `elapsed` reaches that window.
- Organic guard flow: LMB → wait stage recover → press RMB (mouse.down
  right) at `elapsed = T - 1 frame` (0.95·total - 1f = 1.375 s) → hold through
  swing end → mouse.up.
- PASS guard-acceptance: a `blocking=true` row appears and its `elapsed` (for
  rows still showing the old attack) lies within [T - 2f, T + 3f]; a press at
  `T - 1f` is accepted (buffered) not dropped. The full ACTIVE-vs-raised
  distinction is B3's gate.
- Organic move flow (B4 probe but gated here): hold A (strafe) during the
  whole slashR2L swing with camYaw=0 (attack yaw = -Z; strafe displacement is
  +X lateral, isolated from root motion which is -Z only post-build).
- PASS move: across sampler rows with `elapsed ≥ 0.65·total`, |Δx| in
  [0.4·want, 1.2·want] where `want = 3 m/s × 0.05 × frames` (0.5× of
  walkSpeed 6.0 anchored at `CONFIG.js:554`).
- Anchors: cancel sites `player.js:329-348` (tryRoll), `353-359` (tryBlock),
  `594-605` (tryAttack), consumption `818-841`, moveMult gate `883`
  (`speed *= moveMultWhileAttacking[stage]`) at b94a35c.
- Pre-build expected: **B1dodge FAIL** (strike-stage roll request dropped →
  roll never fires), **B1e FAIL** (tryBlock refuses while attacking →
  `blocking` never true), **B4 FAIL** (recover moveMult=0 → Δx ≈ 0).

### B2 — chainOpenSec preserved verbatim (regression)

- Probe: `ac_b2_chain`, sampler `b2`.
- Organic: LMB → poll `stage == 'strike'` → LMB (buffered) → wait for
  `slashL2R` windup → stop.
- PASS: swing-1 `elapsed` at the row before the first `moveId == 'slashL2R'`
  row ∈ [0.97 s - 2f, 0.97 s + 3.5f] (0.97 = windup+strike+chainOpen
  = 0.57+0.20+0.20).
- Anchors: `CONFIG.js:851` (chainOpenSec 0.20) and consumption site
  `player.js:828-830` (`ph.stage === 'recover' && ph.t >= chainOpenSec`) at
  b94a35c.
- Pre-build expected: **PASS** (regression canary: must stay true post-build).

### B3 — guard-raise delay 0.13 s

- Probe: `ac_b3_guard_delay`, sampler `b3`, enemy-assisted.
- Setup: teleport to (-6, -4) directly south of bandit at (-6, -8); camYaw
  180° faces the bandit.
- Organic: hold RMB into guard; bandit winds up and hits; sampler rows capture
  `blocking`, `blockActive` (post-build flag), `hp`.
- Window math: raise 0.13 s = 2.6 frames → gate ≈ 3.
- PASS (two sub-gates, both must hold):
  1. `blockActive` symbol OBSERVED (row field non-null) — the contract
     surface for the raise delay.
  2. First enemy hit arrives ≥ 2.6 frames after first `blocking=true` — if the
     hit lands when `blockActive=false`, hp must drop by FULL damage
     (bandit 12); if dropped by chip (12 × (1-absorb)) the flag was active.
     The hp delta read discriminates: pre-gate hit = 12±1 vs post-gate chip
     ≤ 2.5 (v6 absorb 0.8 of 12 → chip 2.4; CONFIG.js:636). Bandit damage at
     CONFIG.js:657 (`attackDamage: 12.0`), spawn roster CONFIG.js:166.
- Anchors: `player.js:353-359` tryBlock, `540-585` resolveIncomingHit,
  game.js `586-588` damagePlayerFromEnemy at b94a35c; bandit enemy slot 0
  spawn `CONFIG.js:166`.
- Pre-build expected: **FAIL** (no `blockActive` field on player → gate 1
  fails). If Devbot implements without a public `blockActive` field but with
  an equivalent signal (e.g., `blockRaiseTimer`), the valspec amendment must
  name it; the probe accepts either symbol once the impl note (F1) declares it.

### B5 — input buffer listens from 0.5 of windup

- Probe: `ac_b5_buffer_from`, sampler `b5b`.
- Organic: LMB (slashR2L starts) → poll `elapsed >= 0.285 - 0.025` → LMB.
- PASS: (i) `comboQueued=true` observed while phase.stage == 'windup' (the
  second LMB fell inside the buffer window during late windup); (ii) chain
  move `slashL2R` begins at swing-1 `elapsed ∈ [0.97-2f, 0.97+3.5f]`.
- 1-frame-early sub-gate (amendment risk noted §9): fire LMB at
  `elapsed = 0.285 - 1f (0.235)` → `comboQueued` must NEVER be true in the
  sampler. Pre-build note: this also fails today (windup presses dropped
  wholesale) so it is not a discriminator, only a post-build correctness gate.
- Anchors: `player.js:594-605` `tryAttack` windup-drop at b94a35c;
  `CONFIG.js:839` inputBufferSec.
- Pre-build expected: **FAIL** (windup press ignored; never `comboQueued` in
  windup).

### C1 — root motion slashR2L 0→0.9→1.0 forward

- Probe: `ac_c1_c2_root_motion`, sampler `c1` (C1 and C2 share the run).
- Setup: teleport open ground (2.5, 74); camYaw 0 → attack yaw = -Z so
  forward gain measured as `-(z-z0)`.
- Organic: LMB single swing; the same sampler continues into C2's chain.
- PASS: per-phase gain: windup |Δz| ≤ 0.08; strike Δz ∈ [0.82, 1.0]
  (0.90 ± 0.08); end-of-swing total Δz ∈ [0.82, 1.18] (1.0 ± recover
  tolerance); lateral |Δx| < 0.1 over the strike segment.
- Anchors: current lunge sink at `player.js:946-956` (`lungeStep` along
  `sin(yaw), cos(yaw)`, dt-scaled `lunge/strike` rate) — EPR1's rootMotion
  table drives the same slot; spec allows replacing the constant-rate lunge
  with the staged profile.
- Pre-build expected: **FAIL** (lunge 0.8 total ≠ 1.0, spread evenly across
  the whole strike = 1.50 m/… actually lunge 0.8 over strike only; windup
  gain 0; measured totals will mismatch: end total ≈ 0.8 → outside [0.82,
  1.18] lower bound? 0.8 IS below 0.82 → boundary FAIL. Windup gain ≈ 0
  passes; strike ≈ 0.8 < 0.82 fails).

### C2 — root motion thrust 0→1.5→1.7

- Same probe continues: during slashR2L strike press LMB (chain buffer),
  during slashL2R strike press LMB again → swing 3 = thrust (chain order
  `CONFIG.js:844`).
- PASS: thrust strike Δz ∈ [1.42, 1.62] (1.5 ± 0.08); total ∈ [1.42, 1.88]
  (1.7); lateral |Δx| < 0.1.
- Pre-build expected: **FAIL** (thrust lunge 1.4 evenly over 0.43 s strike;
  gate wants 1.5 in strike alone plus 0.2 in recover).

Pre-land deviation note accepted by this spec: if the GLB clip's authored
forward sweep differs by a per-move delta ≤ 0.2 m at strike end, Devbot
compensates via the rootMotion table so MEASUREMENT lands on the table (the
spec's explicit ruling: "the table — not the clip sweep — is the contract");
the probe gates the measurement only.

### C3 — root motion respects the level clamp

- Probe: `ac_c3_clamp`, sampler `c3`.
- Setup: walk S(+z) until `clampPlayer` blocks (position stops advancing two
  polls in a row); teleport to `z = blocked - 0.6`; camYaw 180° (facing +z,
  into the rim).
- Organic: LMB then chain-press through slashL2R and into thrust.
- PASS: max `pos.z` over the sampler window ≤ blocked + 0.05.
- Anchors: `game.js:548-557` clampPlayerToBounds + prop colliders at b94a35c.
- Pre-build expected: FAIL or PASS depending on whether the thrust's
  additional root motion crosses the rim (lunge 1.4 already exists, but it is
  smaller; both pre- and post- must HOLD — this is a preservation canary; a
  pre-build FAIL here is a wiring-caveat documented in §8, not a new rule).

### D1 — v6/v7 block/parry/loadout semantics preserved (regression)

- Probe: `ac_d1_preserve`, sampler none (transient checks).
- Organic: Q toggle to shield offhand → RMB → read `isBlocking()` and
  `getParryWindowRemaining()`.
- PASS: after RMB with shield offhand, `blocking=true` and `parry > 0`.
- Anchors: tryBlock `player.js:353-359`, parry consume `559-567`, RMB route
  `279-289`, loadout toggle `437-441` at b94a35c; WH_DEBUG hooks
  `game.js:915-919`.
- Pre-build expected: **PASS** (preservation canary; a post-build FAIL is a
  hard regression).

### E1 — player combat GLB untouched

- Probe: `ac_e1_glb`, page-side asserts.
- PASS: `WH_ASSETS.getClips('playerBody').length == 24` AND
  `['WH_SS_SlashR2L','WH_SS_SlashL2R','WH_SS_Overhead']` all present. Repo-side
  (E3 sweep covers) art-direction/model/player-combat-sword.blend(.glb) and
  texture paths unmodified.
- Anchors: asset registry `game.js:520` (WH_ASSETS def), debug hook
  `getAssetMeta` `game.js:854`, MOVE_NAMES `anim.js:16-19` at b94a35c.
- Pre-build expected: **PASS**.

### E2 — suite floor (no new FAIL ids vs frozen floor)

- Probe: `ac_e2_suite_floor` (repo-side subprocess runner).
- Floor file: `scratch/erparity/e2_floor.json` — Testerbot-owned, frozen at
  pre-build origin/dev b94a35c; maps `{suite-tag: {AC-id: "PASS"|"FAIL"}}`.
- Suites run (whanim3-AC4 pattern, each from the EPR1 worktree):
  `tests/wh_combat_ds1_validation.py` (tag `combat-ds1-A`),
  `tests/wh_v7_weave.py` (`weave`), `tests/wh_v2_verify.py` (`v2-assets`),
  `tests/wh_v3_anim_probes.py` (`v3-anim`),
  `tests/wh_mousebind_validation.py` (`mousebind`) — EXCLUDED by IO recovery
  edit 2026-10-06: this suite exists only on feat/mouse-bind-cam (unmerged),
  not on origin/dev b94a35c; including it would hard-flag `mousebind:missing`
  at post-build E2. The E2 floor + suite gate therefore covers the other four
  suites. (Re-add to the gate when mouse-bind-cam lands on dev.)
- PASS: every suite runs to completion (exit-code convention: 1 iff crashes)
  AND no per-AC id regresses from PASS→FAIL vs floor. Pre-existing floor
  FAILs are whitelisted by id; any PASS→PASS or FAIL→FAIL is clean. A suite
  exiting non-zero (crashes) is a FAIL.
- Anchors: none (runner only).
- Pre-build smoke: skipped (floor file missing at authoring time is the
  trigger; smoke run validated the runner logic offline).

### E3 — tree hygiene against the frozen base file set

- Probe: `ac_e3_hygiene` (repo-side git census of WH_ERPARITY_REPO).
- Base set: every tracked file at origin/dev b94a35c MINUS the contract-mod
  set (`prototype/js/CONFIG.js`, `prototype/js/player.js`) MINUS validator
  whitelist (§10) MINUS EPR1 declared artifacts (`io/erparity-impl-notes.md`,
  `scratch/erparity-amendments.md` if produced).
- PASS: `git status --porcelain` delta after removal of the carve-outs is
  empty.
- Pre-build smoke: passes as wiring proof only after the harness itself is
  in `scratch/erparity/` (whitelisted).

### F1 — io/erparity-impl-notes.md present and substantive

- Probe: `ac_f1_f3` (file presence + size ≥ 200 bytes).
- Pre-build expected: **FAIL** (file is a Devbot artifact; absent pre-build).

### F2 — amendments file iff requested (informational)

- Probe: informational; the amendment verdict is owned by IO's §0 protocol,
  not by the harness. Always passes at the harness layer; any present
  `scratch/erparity-amendments.md` is reported for IO review.
- Pre-build expected: PASS (informational).

### F3 — handAxe cancel columns present or explicit defer note

- Probe: `ac_f3` — repo-side: either new cancel keys exist inside the
  `handAxe` moves block (`CONFIG.js:866-881` at b94a35c) OR F1 carries a
  "handAxe defer" sentence. Pre-build: FAIL expected (neither exists).

## 4. Anchor verification (origin/dev b94a35c, re-derived)

| File | Symbol | Verified line(s) | Impl-spec claim | Drift? |
|---|---|---|---|---|
| CONFIG.js | `window.WH_CONFIG.moveset = {` | 834 | ~828-889 | +6 (block opens 834, inputBufferSec 839; spec said 845) |
| CONFIG.js | rollDuration / rollIFrameWindow | 558-559 | — | — |
| CONFIG.js | inputBufferSec | 839 | ~845 | +6 |
| CONFIG.js | moves.slashR2L/slashL2R/thrust | 850-862 | ~855-886 | −5 |
| CONFIG.js | moves.handAxe block | 866-881 | — | — |
| CONFIG.js | chainOpenSec rows | 851, 855, 860, 873, 877 | — | — |
| player.js | Space keydown → tryRoll | 247-249 | — | — |
| player.js | tryRoll def | 329-348 | — | — |
| player.js | tryBlock def | 353-359 | — | — |
| player.js | tryAttack def (windup-drop) | 594-605 | — | — |
| player.js | getAttackPhase | 662-675 | — | — |
| player.js | getAttackStage | 678-681 | — | — |
| player.js | chain consume (chainOpenSec) | 826-831 | — | — |
| player.js | lunge site (attackMove.lunge) | 946-956 | — | legacy stub also at 751-756 (attack-window path, `AW.strikeLunge`; dead under clip path) |
| player.js | resolveIncomingHit def | 540-588 | — | — |
| anim.js | `var MOVE_NAMES = {` | 16-19 (3 names) | — | — |
| game.js | `window.WH_DEBUG = {` | 831 | — | — |
| game.js | getMoveDef hook | 900-904 | — | — |
| game.js | clampPlayerToBounds | 548-557 | — | — |
| game.js | maxDt clamp in loop | 1176 | — | — |

Re-run this table against the EPR1 worktree HEAD at final validation; any
drift >0 in the *existing* files is an E3 flag.

## 5. Pre-build smoke result (origin/dev b94a35c)

Harness: `scratch/erparity/wh_erparity_validation.py`, run:
`WH_BASE_ROOT=http://127.0.0.1:8793/ python3 wh_erparity_validation.py`
against worktree `/workspace/wh-erparity-test` (removed after smoke).

See §8 for the captured per-probe matrix. Summary: wiring clean (zero
pageerrors, zero console errors, all samplers returned rows, all organic
inputs reached the page). FAILs are expected FAILs (feature absent), not
crash FAILs.

## 6. E2 suite floor (frozen at pre-build)

`scratch/erparity/e2_floor.json` maps suite-tag → AC-id → PASS|FAIL. Frozen
against origin/dev b94a35c. Floor FAIL ids (whitelisted regressions):

_See §8 for the captured floor._ Pre-existing FAILs in the floor are
whitelisted; new PASS→FAIL transitions on these suites post-build are the
E2 gate. Suites exited 0 unless crashes occurred.

## 7. PASS verdict requirements (all must hold)

1. All 19 ACs print `PASS` from the harness (F2/F3 informational paths count
   when their conditions are met).
2. Zero pageerrors / zero crashes across the full run (runner exits 0).
3. E2: no new FAIL ids vs floor; all five suites exit 0.
4. E3: tree census delta empty after carve-outs.
5. Impl notes present and substantive (F1).

## 8. Captured matrices (populated at smoke time)

- Pre-build per-probe verdict: `_SMOKE_LOG_SNAPSHOT_` (see section inserted
  by the validator run summary; source of record =
  `/tmp/erparity_smoke.log` mirrored into the result file).
- Frozen floor: `_FLOOR_SNAPSHOT_` (mirrored from `e2_floor.json`).

## 9. Ambiguities / conflicts found / amendment recommendations to IO

1. **Frame-rate basis**: spec section 3.5 asks harness to convert seconds at
   30 Hz while the game clamps at 0.05 s/frame (20 Hz; Law 2 + CONFIG.js:777).
   Seconds are the number of record; this spec gates in game frames
   (§1). Recommend IO amend spec text to say "harness converts the seconds
   above at the game's rAF frame clock (1/maxDt)" or add a sentence making
   the 30 Hz provenance explicit (the 13i@30Hz → 0.433 mapping). NOT a
   blocker: the seconds columns are self-consistent with the reference
   sim (tests.rs asserts 26 ticks @60 Hz = 13 frames @30 Hz = 0.433 s).
2. **Roll onset release-vs-down**: A1's discriminating gate is "no rolling
   row at f ≤ Space-up frame". This is the release contract. A clean
   devbot-side implementation detail is whether Space held ≥0.35s ALSO
   suppresses the roll on release (A3 forbids; A1 tolerates it). Current
   reading: tap <0.35s must roll on release; hold ≥0.35s must not (A3);
   exactly 0.35s is unspecified — gate at the inclusive boundary favors
   sprint (hold). Flag for impl notes (F1) to state which side won.
3. **B5 "1 sim-frame early ignored"**: the windup-drop at `player.js:597-603`
   means windup presses never queue today, so the pre/post discriminator for
   sub-(i) is null. The harness still runs the sub-probe as a post-build
   correctness gate, but a pre-build FAIL does not isolate the bug. Low risk.
4. **B3 blockActive symbol**: pre-build there is no flag; the valspec probe
   checks for its presence. If Devbot uses a different name (e.g.
   `blockRaiseTimer`, `guardArmT`), F1 must declare it and the probe accepts
   either. Minor contract-surface recommendation: expose `blockActive` (or a
   `getBlockActive()` debug hook) so validators remain implementation-agnostic.
5. **C1/C2 pre-land deltas**: GLB clip sweep compensation up to 0.2 m at
   strike end is allowed by the spec; the probe's ±0.08 strike-end gate is
   tighter than the 0.2 compensation budget (any absorbed delta lands in the
   table, not the measurement). No conflict; noted for Devbot awareness.
6. **E2 floor contains pre-existing FAIL ids** (ds1 A1-3, A2-1, A2-2, A2-4
   among others — full list in `e2_floor.json`). These are whitelisted
   regressions from earlier rounds (mouse-bind-cam branch churn; see io/mb-
   smoke-baseline.md). E2's gate is "no NEW FAIL", not "floor must be green".

## 10. Baseline Manifest (validator-owned, tree-hygiene whitelist)

| Path | sha256 |
|---|---|
| `io/specs/testerbot-spec-wh-erparity-combat.md` | TBD (this file; recomputed at ship) |
| `scratch/erparity/wh_erparity_validation.py` | TBD |
| `scratch/erparity/probe_boot.py` | TBD |
| `scratch/erparity/e2_floor.json` | TBD |
| `scratch/erparity/floor/ds1_floor.log` | TBD (evidence; not a gate) |

Allowed contract-mod set (E3): `prototype/js/CONFIG.js`,
`prototype/js/player.js` (both from impl spec §4 modified files). Any other
delta outside this manifest + carve-outs is an E3 FAIL.
