# CAST1H2 report - cast shot 2.25x + upper-body cast overlay

Brief: io/missions/2026-10-10-cast1h2-overlay.md. Baseline 4c9512039a6f635578f15d6560c9f131ca2ef3fc.
Builder: Claude Code print mode, 2026-10-10. No harness, no game run, no browser.

## 1. Per-unit summary

- T1 SPEED (R8) - prototype/js/CONFIG.js `assets.caster.castShotSpeed` 1.5 -> 2.25
  (comment: Nicko 10-10 second order). fire1HFraction 0.46 and cast1HClipSeconds 2.3
  unchanged. player.js tryCast (round 1, :1479) already computes
  `fire1HFraction * cast1HClipSeconds / castShotSpeed` from the live row ->
  0.46 * 2.3 / 2.25 = 0.470 s. **player.js / game.js: zero change.**
- T2 PARTITION ROWS (R9) - CONFIG.js `castUpperBody: true`, `castUpperNodes` (12),
  `castLowerNodes` (8), exactly the R9 lists, comments cite the census.
- T2 OVERLAY MACHINERY - prototype/js/anim.js:
  - new module helpers `nodeTracks(clip, nodes)` (filter by track.name up to the
    first '.'), `legScale(action, speed, running)` (setLocomotion's walk/run rate law),
    `startLegs(legs, src, fade)` (phase-continuous start of a lower variant).
  - constructor: `castUpper / lowerActions / lowerActive` fields; MODE_NAMES loop
    builds `actions.Cast1H` from `new AnimationClip('WH_Mag_Cast1H__upper', duration,
    upper tracks)` when castUpperBody (R10). this.clips untouched; Cast2H full clip.
  - `transition()` - R14 lower-variant cleanup (see section 7).
  - `castShot()` - one added line: Cast1H + castUpper -> `castOverlay(action)`;
    refusal guards above it are round 1 verbatim; castUpperBody false skips the
    branch entirely (round-1 path, round-1 full clip).
  - new `lowerAction(key)` (R11): lazy cache `lowerActions['<clip>__lower']`,
    default loop, lower tracks only, keyed off the RESOLVED locomotion action key
    (caster magIdle/magWalk/... and warrior idle/walk/run -> WH_Sword* on the
    player body).
  - new `castOverlay(action)` (R12): no transition(); stops every action except
    the pose being left and the shot; legs onto the lower variant at the full
    action's phase (`time % duration`) and timeScale; shot reset/fadeIn 0.08/play,
    timeScale castShotSpeed, clip 'Cast1H', castShotKey 'Cast1H', hitActive false,
    `lowerActive = '<clip>__lower'`. Missing locomotion action -> castShotKey null,
    return (locomotion untouched).
  - new `syncCastLegs(player)` (R13) called from syncPlayer's hold branch when
    lowerActive: a resolved-locomotion change crossfades legs to the new lower
    variant (time = held.time % duration); leg timeScale follows the live speed.
- T3 FIRE-AT-PEAK - preserved through the row (T1); no timing code touched.
- T4 build/commit - node --check, build_v8, markers, host-tip check, one commit, push.
- Provenance: scratch/glb_bone_census2.py extended to emit
  scratch/mag_cast_track_partition.json; scratch/mag_cast_peak.py/.json committed
  as-is (round-1 provenance, previously untracked).

## 2. Partition proof

`python3 scratch/glb_bone_census2.py` (GLB art-direction/3d/assets/races_regen/rigged/
human-hunter-male.combat-sword.glb):

    R9 PARTITION: upper 12 lower 8 overlap [] orphans [] clips 42 neverAnimated ['WH_Body', 'WH_Armature']

- UPPER (code = CONFIG.castUpperNodes = R9): Spine, Chest, Neck, Head, L_Shoulder,
  L_UpperArm, L_Forearm, L_Hand, R_Shoulder, R_UpperArm, R_Forearm, R_Hand
- LOWER (code = CONFIG.castLowerNodes = R9): Hips, Root, L_Thigh, L_Shin, L_Foot,
  R_Thigh, R_Shin, R_Foot
- UPPER ∩ LOWER = [] ; every one of the 42 clips has exactly 12 upper + 8 lower
  animated nodes and 0 nodes outside both sets (per-clip table in the JSON), so
  the two filtered variants together re-cover each full clip exactly.
- The anim.js sets are not re-derived: both filters read the CONFIG rows.

## 3. Scope audit (git diff --stat 4c9512..HEAD)

    docs/planning/65-caster-body-variant.md |  29 ++++     TOUCH: doc 65 round-2 section
    prototype/builds/v8-playable.html       | 150 +++-     TOUCH: build_v8 output
    prototype/js/CONFIG.js                  |  16 +-      TOUCH: R8/R9 rows
    prototype/js/anim.js                    | 134 +++     TOUCH: R10-R14
    scratch/cast1h2_report.md               |  (this)     TOUCH: report
    scratch/glb_bone_census2.py             |  58 +++     TOUCH: provenance
    scratch/mag_cast_peak.json              |   1 +       TOUCH: provenance
    scratch/mag_cast_peak.py                | 132 +++     TOUCH: provenance
    scratch/mag_cast_track_partition.json   | 287 +++     TOUCH: provenance

player.js, game.js, spells.js, enemy.js, light.js, assets.js, save schema: 0 lines.

## 4. node --check

/usr/local/lib/python3.12/site-packages/playwright/driver/node --check:
- prototype/js/anim.js  OK
- prototype/js/CONFIG.js OK

## 5. Bundle markers (prototype/builds/v8-playable.html, 3130287 bytes)

    'castShotSpeed: 2.25' 1 | fire1HFraction 4 | cast1HClipSeconds 3 | castUpperBody 3
    castUpperNodes 2 | castLowerNodes 3 | "'__upper'" 1 | "'__lower'" 2
    castOverlay 3 | syncCastLegs 2 | lowerActive 9

## 6. Dodge-graze grep

`git diff 4c9512 -- prototype/js prototype/builds | grep -E '^[+-]' | grep -cE
'requestDodge|inputDirWorld|sampleDodgeInput|consumeQueuedDodge'` = **0**.

## 7. Cancel sites (R14 re-check)

VERIFY result: the brief's premise "transition() already stops the lower variant"
was FALSE as written - transition() only iterates `this.actions`, and R11 puts
the lower variants in `this.lowerActions`. So transition() (anim.js:213) now also
frees them: every lower variant except the live one stops; the live one fades
out with `prev` (anim.js:247, hard stop when seconds = 0) and, when the next
state is the locomotion it was the lower half of, hands its phase to it
(`next.time = legs.time`); `lowerActive = null`. No cancel site needed a branch:

- fizzle: player.js:1545 cancelCastFizzle -> anim.endCastShot (anim.js:341,
  unchanged) -> transition(locomotion, crossfadeSeconds) -> legs freed.
- hand change / belt rebind: player.js:1175 handsChanged -> endCastShot -> same.
- shot completes (clamped): castShotRunning false -> syncPlayer setLocomotion ->
  transition -> legs freed.
- hit: anim.hit -> transition(hitKey) -> legs fade out under the hit.
- death: anim.death (anim.js:304) -> transition(deathKey) -> legs freed.
- respawn: player.js:2314 -> anim.revive (anim.js:571): mixer.stopAllAction +
  transition(idle, 0) -> lowerActive cleared (legs.stop()).
- attack / block / guard break / parry: playerAttack / syncBlock -> transition.
- syncCastLegs only runs while lowerActive is set, i.e. only between castOverlay
  and the next transition() - no stale lower swap after any exit.

## 8. Commit + push + host tip

- Pre-commit host check (dhost, workdir /tmp): `git ls-remote https://github.com/
  CaptainPickard/witch-hunter.git refs/heads/feat/world-visuals` =
  4c9512039a6f635578f15d6560c9f131ca2ef3fc (container ls-remote identical) - EQUAL.
- One commit `fix(cast1h2): ...`, author CaptainPickard <pickard.nicko@gmail.com>,
  pushed via HTTPS to feat/world-visuals. This report ships inside that commit,
  so its own sha + the post-push ls-remote are in the builder's final reply.

## 9. Deviations + reasons

All inside anim.js, structure/lifecycle as briefed (filtered variant actions,
same Cast1H slot, castShotKey, clamp hold, exit via transition, no scheduler).
Each one is the brief's own stated intent ("legs never pop") where the literal
step would contradict it - three r185 PropertyMixer blends any shortfall under
weight 1 with the BIND pose (three.classic.js:52297), so a fade-in from 0 over a
hard-stopped action dips the bones toward the T-pose for the fade:

1. R12 step 2: the lower variant starts at FULL weight (no fadeIn(0.08)) and the
   full locomotion FADES OUT over 0.08 s instead of stop(). Legs: identical
   values at the same phase -> exact; arms/torso: walk arms 1->0 under the cast
   0->1 instead of a bind-pose dip. When the pose being left is not the
   locomotion (hit / shield / clamped shot), the legs do fadeIn(0.08) against it.
2. R12 step 1: the pose being left (this.clip) fades out like a transition() prev
   rather than a hard stop (a hit/shield hard stop pops the whole body; round 1
   faded it via transition()). All other actions stop as briefed.
3. R12: lower timeScale copies the full action's (walk/run rate is
   speed-scaled; default 1 would slide the feet); syncCastLegs keeps it current.
4. R13: the mid-cast lower swap crossfades over CFG.crossfadeSeconds (different
   leg clips, so a hard swap would pop); time continuity kept as briefed.
5. R14: transition() needed the lower-variant cleanup (section 7) - the
   "already stops it" premise did not hold. endCastShot itself unchanged.
6. Verification extra: a throwaway node script (outside the repo, not
   committed, /tmp/cast1h2_sanity) ran anim.js against the vendored three
   AnimationMixer on a 20-node mock skeleton (no game, no browser): walking cast
   kept L_Thigh stepping 0.0083/frame (walk rate) through entry, hold and exit
   (max step 0.0083), torso crossfaded to the cast, stop-mid-cast swapped legs to
   WH_SwordIdle__lower, completion/fizzle left clip 'walk', lowerActive null and
   no running lower action.
