# ASTRABOT MISSION BRIEF - Weapon moveset framework + longsword 3-chain
2026-10-03, from IO (Nicko change order: combo spam -> real chains, souls-style)

You are Astrabot, running as a Claude Code print-mode session in the Witch
Hunter playtest worktree /tmp/wh-worldfeat (branch feat/world-visuals). Your
bar: Nicko plays the build and judges feel. You do NOT run any browser, any
headless browser, any automated harness, or any smoke test of any kind - there
is NO automated validation on this project, period. Your own checks are static
only: esprima-style syntax parse (python3 -c with esprima is available) and
grep-level self-review of your diff.

## 1. Current mechanism map (verified today - trust this, re-read files anyway)

- prototype/js/moveset.js - window.WH_MOVESET: keyframed WEAPON-PIVOT poses:
  idle, m1 'slash-l2r', m2 'slash-r2l', m3 'overhead', m4 'thrust', claw.
  Each move = windup/strike/recover {pos,rot} + bodyLean/crouch/lunge.
  Also chainCap=3 and interpPose(a,b,t). There are NO timings here today.
- prototype/js/player.js - the attack machinery:
  - tryAttack() starts swings; state: attacking, attackStage (windup/strike/
    recover via getAttackStage()), attackTimer; comboIndex (which chain move
    next), comboQueued (input buffered during recover), recoverFullyElapsed,
    chainHits, armedTimer/crossArmed (v7 armed finisher - PRESERVE IT).
  - consumeAttackSweep() returns {origin, range, halfAngle, damage} consumed
    BY game.js' update loop, which applies damage to enemies in the cone.
  - Movement input -> moveDirWorld is CAMERA-relative (camYaw basis). Attack
    body yaw: free turn during windup (CFG.turnLerpDegPerSecAttackWindup),
    locked during strike/recover. Roll = Space/tryRoll with i-frames.
  - THE SPAM BUG: attacks today share one short duration
    (CFG.player.attackDuration = 0.5) and mashing LMB re-fires swings without
    completing a chain rhythm; there is no per-move timing and no enforced
    chain order.
- prototype/js/game.js - consumes the sweep, drives sword pose animation from
  WH_MOVESET poses + attack stages (see the sword pose integration in boot
  and the pose sampling in the anim/sword sync path). Do not break the weapon
  mount (CONFIG.assets.weaponMount.gripHolderY - GLB origin sits mid-blade).
- prototype/js/touch-controls.js - attack button calls the same tryAttack.
- CONFIG: CFG.moveset.comboChainCap exists (read where used), player.attack*
  keys, block.moveMult etc.

## 2. THE ORDER - build the framework, then make longsword use it

A. PER-WEAPON MOVESET FRAMEWORK in CONFIG.js (all tunables CONFIG-driven,
   ZERO hardcoded combat numbers in player.js/moveset.js):

   CONFIG.moveset = {
     inputBufferSec: 0.35,        // buffered input lifetime in a chain window
     weapons: {
       longsword: {
         chainCap: 3,             // matches WH_MOVESET.chainCap today
         chain: ['slashR2L', 'slashL2R', 'thrust'],   // Nicko's exact order:
             // 1st hit swipe right->left, 2nd left->right, 3rd THRUST,
             // then the chain resets (next attack starts at slashR2L again)
         moves: {
           slashR2L: { pose:'m2', windup: 0.14, strike: 0.20, recover: 0.30,
                       damage: 34, range: 3.2, halfAngleDeg: 70, lunge: 0.8,
                       staminaCost: 15, damageGhoulMult: 1.15 },
           slashL2R: { pose:'m1', ... },
           thrust:   { pose:'m4', windup: 0.16, strike: 0.14, recover: 0.40,
                       damage: 40, range: 3.8, halfAngleDeg: 22, lunge: 1.4,
                       ... }   // thrust = narrow, longer reach, more damage
         },
         moveMultWhileAttacking: keep current behavior (windup 0.3 speed)
       },
       handAxe: { ... }         // wire the axe to the SAME framework with fast
                                // 2-hit chain (reuse 'claw'/overhead poses),
                                // timings quicker, damage lower. A real
                                // moveset so the framework is proven generic.
     }
   }
   Pose shapes stay in moveset.js (keyframes); the framework references them
   by pose name. Timings/damage/sweeps live ONLY in CONFIG.

B. INPUT + CHAIN GATING in player.js (the actual spam fix):
   - A swing runs its OWN windup/strike/recover durations from its CONFIG move.
   - The NEXT chain input is only accepted during a strike/recover "chain
     window": inputs during windup are IGNORED (no skip), inputs during
     strike/recover are Buffered (comboQueued, now with inputBufferSec
     freshness) and fire as the next chain move the moment the window opens.
   - After the LAST move of the chain resolves its recover, the chain resets
     (comboIndex -> 0). Mashing through recover early must NOT skip stages.
   - chainHits/armedTimer v7 layer must keep working unchanged (3 landed
     hits -> armed finisher window; toggle still resets the chain).
   - Roll/roll input MAY cancel recover (souls behavior: roll out of
     recovery), but never windup/strike. Block toggle unchanged.
   - Lock-on: keep current hard-track behavior on strikes.

C. SWEEP PLUMBING: consumeAttackSweep must return per-move range/halfAngle/
   damage (from the CONFIG move of the CURRENT comboIndex), so thrust can be
   narrow+long and slashes wide+short. game.js' damage loop signature stays.

D. ANIMATION: the sword pose driver reads the same windup/strike/recover
   phase timings from the CONFIG move (pose keys unchanged in moveset.js).
   If the current driver assumes one uniform attackDuration, refactor it to
   take the per-phase durations. Keep bodyLean/crouch/lunge per move working.

## 3. Acceptance criteria (code-level, self-verify; FEEL is Nicko's playtest)

- AC1: mash LMB at any moment <= strike window start: NO skipped stages, no
  faster-than-designed swings; swing count over 3s of mashing <= design
  (compute: chains of windup+strike+recover sum, +buffer windows - state the
  number in your report).
- AC2: chain order for longsword is r2l, l2r, thrust, then resets (grep-level
  proof: the CONFIG chain array + comboIndex progression).
- AC3: thrust sweep is narrower and longer than slash sweeps (numbers from
  CONFIG, visible in consumeAttackSweep output).
- AC4: ALL combat numbers (durations, damage, range, angles, lunge, stamina,
  buffer) readable from CONFIG.moveset.weapons[weapon]; grep proves no
  hardcoded remnants drive the combo path (CFG.player.attackDuration may
  remain referenced ONLY as a fallback the framework ignores when the
  framework is active - preferred: remove its use on this path entirely).
- AC5: handAxe swings through the same framework (its own chain defined).
- AC6: armed finisher + toggle chain reset + roll cancel of recover all
  still hold (code-path walkthrough in the report; no runtime tests).
- AC7: syntax parse passes for every touched file.

## 4. Hard laws

- NO headless browser runs, NO Playwright, NO harness - static checks only.
- Do not touch art-direction/ assets or the weapon mount orientation.
- Commit to feat/world-visuals incrementally (framework commit, then
  longsword/handAxe wiring commit is a natural 2-3 commits) and PUSH to
  origin after each. The worktree is truth: uncommitted work does not exist.
- Do not commit scratch/dhost-style exploration files; keep diff clean.
- Write your final report to scratch/astrabot-moveset-report.md (design
  notes, AC evidence, tuning knob list). Your last chat message: short
  summary - commits, AC status, knobs Nicko can tune in CONFIG, anything
  left undone.