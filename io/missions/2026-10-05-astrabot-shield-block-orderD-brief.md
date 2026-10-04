# ASTRABOT MISSION BRIEF - Order D: shield animation + block/parry presentation (Blender clips + full feedback set)
2026-10-05, from IO. Nicko's orders (10-05 session + clarification round):
- "Next I want to work on an actual shield animation and the actual block and
  parry mechanic."
- Clarifications: Blender-authored clips (same pipeline as the sword chain);
  block/parry stays on RMB (press timing = parry, hold = block; mechanics
  UNCHANGED); FULL feedback set (deflect, shield knock, player guard-break
  stagger pose, riposte window indicator).

You are Astrabot, running as a Claude Code print-mode agent in the witch-hunter
repo worktree /tmp/wh-worldfeat (branch feat/world-visuals).
Commits + pushes per sub-block as usual. Report file as usual.

## 0. LAWS (hard)
- NO automated harness or headless-browser runs of any kind. Nicko's playtest
  is the ONLY acceptance test.
- One order at a time: this order only. Commit+push per sub-block.
- Blender 4.5.4 is installed at /opt/blender-4.5.4-linux-x64 (used 10-04 for the
  chain clips; script precedent scratch/blender_chain_clips.py). THIS order owns
  real Blender work - see D2.
- Art law: pixelated everything, darkwood palette, ONE accent per frame (amber
  human fire / cyan magic / red pact). VFX additions follow the existing HUD
  flash language (parryFlash/blockFlash/guardBreakFlash already exist).
- Every tunable from CONFIG.
- This order MUST NOT change block/parry MECHANICS numbers (parryWindow 0.25,
  absorb 0.8, arc 90deg, moveMult 0.5 + guard-break rules + riposte 1.75 stay).
  Presentation only, plus the state plumbing the visuals need.

## 1. NICKO'S RULINGS (10-05, binding)
1. Blender-authored clips into human-hunter-male.combat-chain.glb (the same
   GLB the per-move sword clips live in - currently 9 clips; expected-count
   check in assets.js CHARACTERS dict updates accordingly).
2. Input model unchanged: RMB with shield in the LEFT hand. Press = parry
   timing window (first 0.25s), hold = block. Touch block button same path.
3. Full feedback set: blocked attacks show enemy weapon deflection + shield
   knock reaction; guard break staggers the PLAYER (stagger pose + flash +
   text); a successful parry shows a riposte window indicator on the ENEMY
   (existing riposteMult/riposteStaggerDur mechanics unchanged).

## 2. Current mechanics (verified by IO this session - do not re-research)
- CONFIG.block (CONFIG.js:525-541): all numbers above live there.
- player.js: tryBlock() on RMB-down (shield LEFT only, Order C routing),
  endBlock() on release; parryTimer set on block start; resolveIncomingHit()
  (~1023): roll i-frames > parry (attacker.enterStagger(riposteStaggerDur),
  spendStamina(parryStaminaCost)) > block (chip damage, stamina drain,
  guardBroken when stamina empties, guardBreakMinStamina gate) > full damage.
  blocking forces walk pace, blocks sprint. Guard break: guardBreakStun 0.8s.
- anim.js (cf1f458, walk fix): CharacterAnim transition() clears hitActive
  when leaving hit; hit/attack/death are LoopOnce+clamp; per-move sword clips
  via MOVE_NAMES; setLocomotion gate = !hitActive. walk fix JUST landed -
  re-verify your changes do not reintroduce any locomotion starvation
  (AC D9 below).
- Player body: human-hunter-male.combat-chain.glb, 9 clips, 20 bones. Meshes
  attach to R_Hand/L_Hand bones via Order B/C mount system (nativeHand +
  mirrorScale). Shield = round-shield-pixelated.glb on L_Hand.
- HUD: parryFlash/blockFlash/guardBreakFlash + GUARD BROKEN text exist in
  game.js/hud layer (search blockFlash / guardBreak in game.js).

## 3. WORK ORDER D1 - Blender clip authoring (the real animation)
Author and add to combat-chain.glb (script under scratch/, re-runnable like
blender_chain_clips.py):
1. WH_ShieldRaise (~0.25s): shield arm rises to the guard pose from idle.
   Designed to play ONCE on block start (LoopOnce, no clamp-into-hold - the
   HOLD pose is frozen at the raised frame via the existing pose system, see
   D3).
2. WH_ShieldImpact (~0.35s): short recoil on the shield arm when a hit is
   BLOCKED (chip path) - arm+shoulder compress then settle back to guard.
3. WH_ParrySwipe (~0.4s): quick angled shield shove when a PARRY lands -
   reads as a deflect, ends back in guard.
4. WH_GuardBreakStagger (~0.8s): full-body stagger matching guardBreakStun
   (reel back, head drop, recover start). Plays on guard break; player takes
   the stun sitting in this pose.
Rules:
- Author on the existing skeleton (20 bones, same names). Verify bone names
  from the GLB first (precedent: blender_chain_clips.py reads them).
- Clips LOOP-SAFE: raise/impact/swipe end AT the guard pose so a hold after
  them looks continuous; stagger ends near a crouch (the stun holds last pose
  via clampWhenFinished, respawn cleans up).
- The originals must stay byte-identical when re-saved (10-04 precedent: the
  9 existing clips + skin carried through unmodified). Verify count = 13 after
  the run; update assets.js CHARACTERS.playerBody expected count 9 -> 13.
- MOVE_NAMES-style mapping: new CLIP_NAMES entries for shield states (do NOT
  route them through MOVE_NAMES - that dict is for sword chain moves).

## 4. WORK ORDER D2 - block state presentation (player.js/anim.js)
- Block START (tryBlock success): crossfade to WH_ShieldRaise, then HOLD the
  raised pose for as long as blocking (freeze at end via a 'blockHold' pose
  state or clampWhenFinished + transition guard - your call, report it).
- BLOCKED hit (chip path): interrupt hold with WH_ShieldImpact, then back to
  hold. Each blocked hit replays impact (no restart-storm: only on a NEW hit).
- PARRY (parry branch): WH_ParrySwipe once, then back to hold (the parry
  branch does not extend the block state itself).
- GUARD BREAK: WH_GuardBreakStagger plays during guardBroken (stun); on stun
  end, back to idle/locomotion (existing setLocomotion path). MUST NOT starve
  locomotion afterward (the walking bug: any new latch clears within the
  same transition() discipline - state leaves one-shot clips cleanly).
- Release RMB / lose shield / roll / death: exit hold to locomotion
  crossfade (existing seconds), NO latched flags.
- While blocking, movement stays walk-pace (mechanics unchanged) and the
  walk-under-block feel should read as holding guard while stepping - if the
  hold fightss the walk cycle visually, note it in the report as a stage-2
  polish item (blend masks are NOT this order).

## 5. WORK ORDER D3 - enemy feedback + indicators (game.js)
- ENEMY DEFLECT on block/parry: the ATTACKING enemy's swing visibly deflects -
  reuse the enemy attack FSM: knock the enemy's weapon yaw outward +
  small pushback stagger-lite (0.15s, CONFIG.block.deflectEnemyRecoilSec) on
  block/parry contact; on parry the full enterStagger already fires (keep).
- SHIELD KNOCK cue at impact: reuse/extend the shield recoil clip timing +
  a small HUD flash tick (blockFlash exists).
- RIPOSTE INDICATOR on the staggered enemy (after a successful parry): a
  visible marker for riposteStaggerDur (existing duration) - amber ring/marker
  under the enemy or a brief highlight - CONFIG-driven color/size; ONE accent
  color (amber = human opportunity). Removed when stagger ends.
- GUARD BREAK: player stagger clip plays + existing GUARD BROKEN text/flash
  (keep, maybe retime to the clip: CONFIG.block.guardBreakFlashSeconds
  alignment - note any change in the report).

## 6. ACCEPTANCE CRITERIA (Nicko playtests all of these)
| AC | Test |
|---|---|
| D1 | Press RMB (shield left): shield rises smoothly to a guard pose and HOLDS while held |
| D2 | Blocked hit: shield recoils on impact each blocked hit, returns to guard hold |
| D3 | Parry (timed press): quick deflect swipe plays; enemy staggers + amber riposte marker shows |
| D4 | Riposte hit on the staggered enemy deals the 1.75x (existing - confirm no drift) |
| D5 | Guard break (stamina out while blocking): player staggers with the stagger clip + GUARD BROKEN text; walks normally after |
| D6 | Release RMB: guard drops smoothly to idle/walk |
| D7 | Roll while blocking: roll wins (existing), shield raise exits cleanly |
| D8 | Touch: block button holds block + parries on tap timing (same as RMB) |
| D9 | No locomotion starvation: after any of the above, walking plays the walk cycle immediately |
| D10 | Boot log: expected 13 clips, no warning; the 9 originals unchanged |

## 7. Tunables (all CONFIG)
- CONFIG.block additions: deflectEnemyRecoilSec (0.15), riposteMarker
  {color, radius}, blockAnim {raiseCrossfadeSec, holdPoseFreeze...} whatever
  D2 needs. Mechanics numbers NOT changed.
- CONFIG.animRt crossfades reused where possible.

## 8. Report
scratch/astrabot_orderD_shield_block_report.md (committed): Blender run log
(clips authored, bone verification, originals-identical proof), anchors
changed, judgment calls (hold mechanics, exit paths), tunables, AC notes.
Final chat message: commits with shas, AC table state, knobs, anything left
undone.