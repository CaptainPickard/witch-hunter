# Astrabot report: Order D, shield animation + block/parry presentation

Brief: `io/missions/2026-10-05-astrabot-shield-block-orderD-brief.md`. Branch `feat/world-visuals`, worktree `/tmp/wh-worldfeat`.

**What was not run:** no browser, harness or headless game run. Acceptance is Nicko's playtest.

**What was run:** Blender (authoring, plus Cycles stills for QA), the Python GLB append/proof script, and an `esprima` parse of every touched JS file.

**Mechanics:** none of the numbers changed. parryWindow 0.25, absorb 0.8, arc 90, moveMult 0.5, guard-break rules, riposteMult 1.75 and riposteStaggerDur 1.25 are all untouched.

| sub-block | commit |
|---|---|
| D1 Blender clips + GLB + expected count | `b196771` |
| D2 block state presentation (anim.js / player.js / CONFIG) | `a5cb4c0` |
| D3 enemy deflect, parry hit-react, riposte marker (enemy.js / game.js / CONFIG) | `1a97e2f` |

## D1: Blender run log

Tools:
- `scratch/blender_shield_clips.py` authors the clips (Blender 4.5.4, `--background --factory-startup`).
- `scratch/glb_append_clips.py` appends them to the GLB with plain Python.

Rebuild (deterministic):

```sh
R=art-direction/3d/assets/races_regen/rigged
git show 0ffa64e:$R/human-hunter-male.combat-chain.glb > /tmp/base9.glb   # the 9-clip base
/opt/blender-4.5.4-linux-x64/blender --background --factory-startup \
  --python scratch/blender_shield_clips.py -- /tmp/base9.glb /tmp/shield_clips.glb \
  --log /tmp/solve.json [--preview /tmp/prev]
python3 scratch/glb_append_clips.py /tmp/base9.glb /tmp/shield_clips.glb $R/human-hunter-male.combat-chain.glb \
  WH_ShieldRaise WH_ShieldImpact WH_ParrySwipe WH_GuardBreakStagger
```

### Bone verification

The script asserts the imported skeleton is exactly the 20 bones Root, Hips, Spine, Chest, Neck, Head, L/R Shoulder, UpperArm, Forearm, Hand, L/R Thigh, Shin, Foot. It also asserts the input holds exactly the 9 base clips. Both passed.

### Clips authored

All clips are 24 fps, 60 channels each (T/R/S x 20 bones), LINEAR, with Root static (no root motion).

| clip | frames | s | keys | read |
|---|---|---|---|---|
| WH_ShieldRaise | 6 | 0.250 | bind, guard | shield comes from the side up to chest-height guard, ease-in-out |
| WH_ShieldImpact | 8 | 0.333 | guard, recoil @0.22, settle @0.62 (pass-through), guard | shield driven back toward the chest, top tipped back, shoulder compressed, torso rocks back, small forward overshoot, then guard |
| WH_ParrySwipe | 10 | 0.417 | guard, coil @0.18, shove @0.42, guard | shield pulled in with the torso wound right, then a hard angled shove out front-left with the boss turned outward (the deflect), then guard |
| WH_GuardBreakStagger | 19 | 0.792 | guard, reel @0.2, slump @0.55 (pass-through), crouch | reel back (head back, arms flung), head drops, ends in a low crouch with the shield hanging (matches guardBreakStun 0.8) |

### Method

The rig convention is copied from `blender_chain_clips.py`.

**Left (shield) arm.** It is solved by Nelder-Mead over L_UpperArm, L_Forearm and L_Hand to three targets: a hand position, a boss direction and a disc-up direction. The bounds are the right arm's, mirrored. Three elbow guesses are tried and the best one kept.

**Shield axes.** These are `CONFIG.assets.shieldMount` faceAxis/upAxis taken into armature space at bind. Measured from the GLB with numpy, they are FACE (0.940, -0.340, -0.035) and UP (0, -0.105, 0.995). Bind and WH_Idle frame 0 agree within 0.03.

**Right (sword) arm.** It is solved the same way to a tucked guard by the right hip, blade forward-up.

**Feet.** Each key re-plants the lower foot at its bind height through Hips lz, before the arms are solved.

**Solver residuals** (full log in `scratch/shield-clips-qa/shield_solve.json`):
- Guard, recoil, settle, coil and shove: under 0.6 cm, boss within 3.2 deg, disc-up within 7.4 deg.
- Stagger keys use deliberately loose orientation weights (the shield just hangs): position under 0.4 cm, disc-up 12-27 deg.

**Checks inside the script:**
- An FK cross-check against Blender's own pose evaluation is asserted at every integer key.
- Raise, Impact and Swipe end frames are asserted identical: L_Hand (0.131, -0.301, 0.437), boss (0.253, -0.966, 0.055).
- The stagger is asserted to start at guard.

QA renders: `scratch/shield-clips-qa/sheet_*.png` (Cycles CPU, amber disc = shield proxy on the posed L_Hand). I looked at the sheets and made two adjustments:
- The crouch shield was clipping the thigh, so I moved it out by 0.07.
- The impact recoil got more amplitude.

### Proof that the originals are identical

Blender only authors. Its export is a temp file. `glb_append_clips.py` copies the 4 new animations' accessors onto the end of the base BIN chunk, appends new JSON entries, and remaps channel nodes by name. It then asserts all of the following, and every one passed:

```
PROOF: base BIN (4415448 B, sha256 8b248c03487627cf) is a byte prefix of OUT BIN (4458060 B);
all 1150 pre-existing JSON entries identical; animations 9 -> 13
```

Every pre-existing accessor, bufferView, node, skin, mesh, material and image entry is unchanged and points at unchanged bytes. That makes the 9 original clips, the skin, the mesh and the texture byte-identical by construction. An independent numpy re-parse also passed: every key array of all 9 original clips is `array_equal` to base.

| file | sha256 |
|---|---|
| combat-chain.glb before (9 clips) | `9ca71111937cf8bfeb1e167d7f17ff42fe07c26a578d95844ad76aaed13f9d3f` |
| combat-chain.glb after (13 clips) | `48a342d0d7929ca7694850bdda69b513e10f9b69ac31321d9593ed2ff9c8da01` |
| human-hunter-male.rigged.glb (never opened for writing) | `9658044ff5961ffe9d171597016edb3df9a2ea12f7d8d5b1a9c9513076b41401` (unchanged) |

`assets.js`: `CHARACTERS.playerBody` changed from 9 to 13, so the boot count check expects 13. The comment records the new clips and the scripts.

## D2: block state presentation

### Anchors changed

**`prototype/js/anim.js`:**
- New `CLIP_NAMES` (shieldRaise, shieldImpact, parrySwipe, guardBreak). It is separate from `MOVE_NAMES`. All four actions are LoopOnce + clampWhenFinished, built only if the body has the clip.
- New `shieldImpact()` and `shieldParry()`.
- New `syncBlock(player)`. It is called from `syncPlayer` in the non-attacking branch, before `setLocomotion`.
- `getState()` now reports the shield clips.

**`prototype/js/player.js` `resolveIncomingHit`:**
- The parry branch calls `anim.shieldParry()`.
- The non-break block branch calls `anim.shieldImpact()` after the chip `takeDamage`, unless the chip killed the player.

**`CONFIG.block.blockAnim`:** see the knobs section.

### Judgment call: how the hold works

There is no separate hold state. All three of Raise, Impact and Swipe end on the same guard frame (asserted in D1). So the hold is whichever of them ran last, clamped on its final frame. While `player.blocking` is true, `syncBlock` keeps any of those three as the current clip. If something else is current, it transitions to `shieldRaise`.

Each blocked hit is one `resolveIncomingHit` call. That gives one `shieldImpact` restart per new hit, and nothing replays per frame.

### syncBlock priority, read fresh every frame (no flags)

1. dead (existing)
2. attacking (existing)
3. `guardBroken`: transition to `guardBreak` once. It clamps on the crouch for the stun.
4. rolling: hand over to locomotion. Roll wins, and it ends the block.
5. blocking: hold. A real unblocked hit (from behind) finishes its WH_Hit first.
6. a parry swipe still running finishes its 0.42 s.
7. otherwise `setLocomotion`.

### Exit paths

Release RMB, shield loss, Q-swap, roll, guard-break end and the parry swipe ending all leave through `setLocomotion`. That is `transition()` with the existing `animRt.crossfadeSeconds` 0.18. A one-shot that finished and clamped is still `this.clip`, so `setLocomotion`'s `clip !== state` check always transitions out of it.

Death goes through the existing death branch. Respawn uses `revive()`, which stops every action.

### Locomotion starvation (D9)

No new latched flag was added. `syncBlock` returns true only while one of these live conditions holds:
- `guardBroken`: a timer
- `blocking`: input
- a parry swipe that `isRunning()`: false once it finishes

Blocked chip hits used to fire WH_Hit, and they still call `anim.hit()`. The `shieldImpact` that immediately follows goes through `transition()`, which clears `hitActive` (cf1f458 discipline). The guard-break transition clears it the same way.

### Parry follows the mechanics

The existing parry branch calls `endBlock()`, which also clears `blockButton`. That means "swipe then back to hold" happens only if RMB is pressed again. Otherwise it is swipe then locomotion. I did not change this, because it is mechanics. A re-press during the swipe keeps the swipe as the hold clip, and it ends on guard.

### Stage-2 polish (not this order)

The hold clip owns the whole body, including the legs in a soft split stance. Walking while blocking (walk pace) therefore slides with static legs. Fixing that needs an upper-body mask (shield clips on spine and arms, walk on the legs), and the brief excluded blend masks. The same applies to the parry swipe if the player walks during its 0.42 s.

## D3: enemy feedback and indicators

### Anchors changed

**`prototype/js/enemy.js`:**
- New `deflect(fromPos)` and `applyDeflectPose(baseX, baseY, pivotFresh)`.
- New fields `deflectTimer` and `deflectDir`. Also new: `bodyBaseRotX/Y` (rigged body base), `heldAxe` and `heldAxeBaseQuat`.
- The pushback tick runs at the top of `update`, before the parry-stagger freeze.
- The overlay is applied in all three visual paths: rigged, stand-in, and the frozen riposte branch.

**`prototype/js/game.js`:**
- `onParry(attacker)` / `onBlock(attacker)` call `attacker.deflect(player.pos)`.
- A parry also calls `attacker.anim.hit()` (gated by CONFIG).
- New `updateRiposteMarkers()`, called after the anim sync.

### Enemy deflect (block and parry)

The attack FSM timing is not touched. For `deflectEnemyRecoilSec` (0.15 s):
- the body twists toward its weapon side (yaw 18) and leans back 10;
- the hand-held axe is knocked 40 deg about hand-local X;
- the root slides 0.25 away from the player, clamped to the home side.

The envelope is a smoothstep that snaps on at contact and eases out. The rotations are written as base + offset, so they never accumulate. On a parry, the existing `enterStagger` still fires, and the recoil plays inside the freeze.

### Unverified axis

I could not see the hand-local X knock direction without a run. If the axe flicks the wrong way, negate `deflect.weaponKnockDeg`.

### Parry stagger read

Rigged enemies had no visible parry-stagger pose: the frozen branch returned with a stale `animMoveSpeed`, so a chasing bandit walked in place. The frozen branch now sets `animMoveSpeed = 0`, which gives an idle stance. A parry also plays the enemy's WH_Hit once. That is a LoopOnce clip whose finish clears `hitActive`, so it cannot latch.

### Riposte marker

An amber `0xd8b24a` ring under the enemy. That is the canon human/fire amber already used for consumables, and it is the only accent in the frame. It has 12 segments for a chunky read.
- **When shown:** while `isStaggered() && riposteArmed`. That is the existing riposteStaggerDur 1.25 s, and it disappears as soon as the riposte hit consumes `riposteArmed`.
- **Animation:** it pulses at 3 Hz and shrinks from 1.0 to 0.6 as the window closes.
- **Lifetime:** it is parented to the enemy root, so it goes away with the enemy. It counter-offsets the root's hop/bob y so it stays on the ground.

### Shield knock cue

The existing blockFlash (0.12 s gray) already fires at the moment of the blocked hit. That is the same frame `shieldImpact` starts, so the flash tick lines up with the start of the recoil. No change was needed and none was made.

### Guard break

The stagger clip (0.79 s) plays during guardBreakStun (0.8 s). The existing GUARD BROKEN text (1.4 s), red flash (0.5 s) and shake are kept. `guardBreakFlashSeconds` was not retimed: the flash already starts on the same frame as the clip, and it fades before the crouch settles. If Nicko wants the flash to last the whole stagger, set it to 0.8.

## Tuning knobs (all `CONFIG.block`)

- `blockAnim.raiseCrossfadeSec` 0.06
- `blockAnim.impactCrossfadeSec` 0.03
- `blockAnim.parryCrossfadeSec` 0.03
- `blockAnim.guardBreakCrossfadeSec` 0.06
- Release/exit reuses `animRt.crossfadeSeconds` 0.18.
- `deflectEnemyRecoilSec` 0.15
- `deflect` { yawDeg 18, leanBackDeg 10, weaponKnockDeg 40, pushback 0.25 }
- `parryEnemyHitReact` true
- `riposteMarker` { color 0xd8b24a, radius 0.85, width 0.14, segments 12, opacity 0.9, pulseMin 0.45, pulseHz 3, endScale 0.6, yOffset 0.04 }
- Pose shapes live in `scratch/blender_shield_clips.py` (GUARD_* / IMPACT_* / COIL_* / SHOVE_* / REEL_* / SLUMP_* / CROUCH_*). Rerun the rebuild block above to apply changes.

## Acceptance criteria: what each one rests on

None of these has been playtested yet.

| AC | status |
|---|---|
| D1 raise + hold | ready: WH_ShieldRaise, then clamped guard while `blocking` |
| D2 recoil per blocked hit | ready: `shieldImpact` restart per resolved blocked hit, ends on guard |
| D3 parry swipe + stagger + amber marker | ready: swipe, enemy recoil + WH_Hit + frozen idle, amber ring for the window |
| D4 riposte 1.75x | unchanged code path (game.js sweep, `riposteMult`). The marker only reads the existing flags. The 0.25 parry pushback is small next to sword reach, but it is worth watching. |
| D5 guard-break stagger + text, then walk | ready: clip during the stun, existing text/flash, `setLocomotion` after |
| D6 release, smooth drop | ready: 0.18 s locomotion crossfade |
| D7 roll while blocking | ready: roll ends the block (existing) and `syncBlock` yields to locomotion |
| D8 touch | unchanged path: the touch block button calls the same `handButton` dispatch as RMB, so it gets the same states |
| D9 no locomotion starvation | no new latches. See the D2 section above. |
| D10 boot log 13 clips, originals unchanged | expected count 13. Byte-prefix proof above. |

## Left undone

- Upper-body mask for walk-while-blocking (stage 2, see above).
- The direction of the axe knock axis is unverified (one-knob flip).
