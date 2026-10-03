# Astrabot report - weapon moveset framework + longsword 3-chain
2026-10-03, branch feat/world-visuals. Brief: io/missions/2026-10-04-astrabot-moveset-framework-brief.md

Static checks only (esprima parse + grep). No browser, harness or smoke test was run.
How it feels is for Nicko to judge in a playtest.

## Commits
- 85cdcbd feat: per-weapon moveset framework in CONFIG (longsword 3-chain, handAxe 2-chain)
- e694726 feat: chain gating + per-move timings/sweeps (longsword r2l/l2r/thrust, handAxe hack/chop)
- (this report) docs commit

## Design
- `CONFIG.moveset.weapons[id]` = `{ chainCap, chain[], moveMultWhileAttacking{windup,strike,recover}, bladeAxisY, moves{} }`.
  Each move has `{ pose, windup, strike, recover, chainOpenSec, damage, range, halfAngleDeg, lunge, staminaCost, damageGhoulMult }`.
  `pose` is a key into `window.WH_MOVESET` (moveset.js now holds pose shapes only; its dead `lunge`/`chainCap` numbers were removed).
- `CONFIG.moveset.playerWeapon` picks the weapon at boot (`'longsword'`). Set it to `'handAxe'` to play the axe chain,
  or call `WH_DEBUG.equipWeapon('handAxe')` at runtime. The axe mount reuses the bandit axe's measured +Y blade axis.
  The longsword mount is unchanged: -Y, and `gripHolderY` is now looked up by weapon id.
- Player state: `attackMove`/`attackMoveId` are frozen when a swing starts, so a loadout toggle mid-swing can't change the swing's timing.
  `getAttackPhase()` returns `{stage, t, dur, p, durations}`. `getAttackStage()` is built on top of it.
- **Chain gating (`tryAttack` + `update`)**:
  - idle press -> `startAttack(0)`, so the chain always starts at `chain[0]`;
  - press in **windup** -> ignored;
  - press in **strike/recover** -> `comboQueued = true` and `comboBufferTimer = inputBufferSec`. The buffer drains in `update` and a stale press is dropped;
  - non-last move: a fresh buffered press fires `startAttack(comboIndex+1)` only once `stage === 'recover'` and `t >= move.chainOpenSec`.
    The new swing starts at its own windup, so no stage is skipped;
  - last move: there is no early window. At `attackTimer <= 0` the chain resets (`comboIndex = 0`, `chainHits = 0`). A press that is still fresh then starts `chain[0]`.
- **Sweep**: `consumeAttackSweep()` returns `{origin, dir, range, halfAngle, damage, ghoulMult, moveId}`, all taken from the current move.
  game.js' loop is unchanged except that it uses `sweep.ghoulMult` (it used to read `CFG.player.attackDamageGhoulBonus`).
- **Animation**:
  - anim.js `playerAttack(stage, t, durations)` is now phase-mapped like enemies: clip segments windup/strike/recover play over the move's own durations.
    The seek code is shared with `enemyAttack` through `seekAttack`. Chained swings re-seek without crossfading into themselves.
  - Stand-in pivot path: uses `WH_MOVESET[move.pose]` with per-pose `crouch` (windup dip) and `bodyLean` (recover settle).
  - Lunge: one FSM block for both paths, `velocity = move.lunge / move.strike`. It now runs **before** the bounds clamp, so the larger lunges can't leave the bounds for a frame.

## Acceptance criteria
- **AC1 (no spam) - PASS (computed).** The fastest cadence is a chain window: swing start -> windup + strike + chainOpenSec.
  - Longsword (mashing continuously, so the buffer is always fresh): starts at t = 0, 0.46, 0.92, 1.62, 2.08, 2.54 -> **6 swings in 3 s**.
    - Chain period: 0.46 + 0.46 + 0.70 = 1.62 s for 3 swings.
    - Stamina: 6 swings cost 100, exactly the stamina max.
    - The old build re-fired every windup + strike = 0.275 s, about 11 swings in 3 s.
  - handAxe: starts at 0, 0.32, 0.88, 1.20, 1.76, 2.08, 2.64, 2.96 -> **8 swings in 3 s** (period 0.88 s per 2 swings, 88 stamina).
  - Windup presses never queue. Strike presses wait for the chainOpenSec gate. A new swing always begins at windup, so no stage is skipped.
- **AC2 (order) - PASS.**
  - `weapons.longsword.chain = ['slashR2L', 'slashL2R', 'thrust']`, with poses m2 (slash-r2l), m1 (slash-l2r), m4 (thrust).
  - Progression: idle press -> `startAttack(0)`; buffered press -> `startAttack(comboIndex + 1)`, gated by `!lastMove`.
  - After the last move resolves: `comboIndex = 0`, and a fresh press runs `startAttack(0)`.
  - `startAttack` also wraps `idx >= chainCap` to 0.
- **AC3 (thrust sweep) - PASS.** Thrust is range 3.8 / halfAngleDeg 22 / damage 40. Slashes are range 3.2 / halfAngleDeg 70 / damage 34.
  `consumeAttackSweep` returns `M.range`, `deg2rad(M.halfAngleDeg)` and `M.damage * pendingDamageMult`.
- **AC4 (CONFIG-only numbers) - PASS.**
  - `git grep` over prototype/js finds zero hits for: `attackDuration`, `attackStaminaCost`, `attackArcHalfAngleDeg`, `attackDamageGhoulBonus`, `windupFrac`, `strikeFrac`, `strikeLunge`, `comboChainCap`, `windupCrouch`, `recoverLean`, `CFG.attackRange`, `CFG.attackDamage`, `[MS.m1, MS.m2`.
  - The legacy keys were deleted from CONFIG; nothing falls back to them.
  - Remaining non-moveset numbers on the attack path are visual feel only: `anim.attack.windupLean` and `strikeYawSweepDeg` (stand-in body sway), and the walk lean `0.5` while attacking.
- **AC5 (handAxe) - PASS (code path).**
  - `weapons.handAxe.chain = ['hack' (pose claw), 'chop' (pose m3)]` with chainCap 2.
  - It runs through the same `startAttack` / `getAttackPhase` / `consumeAttackSweep` code with no axe-specific branches.
  - Turn it on with `playerWeapon: 'handAxe'` or `WH_DEBUG.equipWeapon('handAxe')`.
- **AC6 - PASS (walkthrough).**
  - **Armed finisher**: game.js still increments `chainHits` per landed hit. It arms when `chainHits >= player.getChainCap()`, which is 3 for the longsword (same as before).
    `startAttack` still consumes armed/cross the same way. The `chainHits` sync line is unchanged. Roll-cancel and natural chain end clear `chainHits` but leave `armedTimer` alone.
    For the handAxe the arm threshold is its chainCap of 2.
  - **Toggle**: `toggleLoadout` still zeroes `comboIndex`/`comboQueued`, and `tryAttack` is refused while toggling. Because the move is frozen per swing, the active swing finishes with its own timings and the next press starts `chain[0]`.
  - **Roll**: `tryRoll` checks stamina first, then allows the roll only if the stage is `'recover'`, and calls `cancelAttack()` (chain reset, armed kept).
    Windup and strike rolls are refused.
    - **Behavior change**: the old build allowed a roll to cancel *windup* only. The brief asked for recover-only, so that is what this build does.
  - Block and lock-on are untouched: `tryBlock` is refused while attacking, and `updateLockTracking` still hard-tracks.
- **AC7 - PASS.** esprima `parseScript` succeeds on CONFIG.js, moveset.js, player.js, anim.js, game.js and touch-controls.js.

## Tuning knobs (all in prototype/js/CONFIG.js, `window.WH_CONFIG.moveset`)
- `playerWeapon` - `'longsword'` | `'handAxe'`
- `inputBufferSec` (0.35) - how long a strike/recover press stays buffered
- Per weapon:
  - `chainCap` - moves per chain and the landed-hit count that arms the finisher
  - `chain[]` - move order
  - `moveMultWhileAttacking.{windup,strike,recover}` - movement speed multiplier per stage
- Per move:
  - `windup` / `strike` / `recover` - seconds per stage
  - `chainOpenSec` - seconds into recover before the next chain move may fire. Lower is snappier, higher is heavier. Has no effect on the last move.
  - `damage` / `range` / `halfAngleDeg` - hit sweep
  - `lunge` - units of forward drift during strike
  - `staminaCost`
  - `damageGhoulMult`
- Pose shapes and their `bodyLean`/`crouch`: prototype/js/moveset.js

## Left undone / notes for the playtest
- No runtime verification, per the brief. All feel calls are Nicko's.
- Lunge numbers come straight from the brief (0.8 slash / 1.4 thrust), up from the old 0.25. Expect a much more forward-driving swing; the per-move `lunge` knob tunes it.
- Thrust staminaCost 20 and all handAxe numbers are my picks; the brief left them as "...".
- The rigged player has a single attack clip (WH_Attack1). Slash vs thrust only reads differently through timing, lunge and sweep.
  Per-pose weapon keyframes only drive the stand-in pivot path. Distinct per-move clips need new animation assets.
- tests/wh_combat_ds1_validation.py still reads the removed `player.attackDuration` / `strikeLunge` keys. It was not run or edited (there is no harness on this project).
- The handAxe in the player's hand reuses the bandit's measured axe mapping (+Y blade). Grip offset is 0, same as the bandit. Untested visually.
