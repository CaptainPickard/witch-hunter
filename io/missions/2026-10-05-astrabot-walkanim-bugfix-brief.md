# ASTRABOT MISSION BRIEF - BUGHUNT: player walk animation stuck (Order C regression)
2026-10-05, from IO. Nicko's report (10-05, playing at ded9664):
- "the walk animation is stuck, no actual animation plays when walking."
- Context: he noticed it AFTER the light order, but reports it fresh - treat the
  onset as unknown; the character MOVES (position updates work) but the walk
  clip does not visibly play.

You are Astrabot, running as a Claude Code print-mode agent in the witch-hunter
repo worktree /tmp/wh-worldfeat (branch feat/world-visuals).
Commit + push the fix to feat/world-visuals. Report file as usual.

## 0. LAWS (hard)
- NO automated harness or headless-browser runs of any kind (no chromium/Node
  DOM passes). Nicko's playtest is the ONLY acceptance test. Static reasoning +
  code instrumentation reading is your toolset.
- One order at a time: this bughunt only.
- Every tunable from CONFIG.

## 1. IO'S BUGHUNT WINDOW (verified facts - do not re-research)
- Walking WORKED at a8b1a0d (Order B end): Nicko playtested it and praised the
  off-hand visuals while walking around.
- Regression window = ORDER C ONLY: 384aa97 (C1 per-hand cast state +
  bindings), 5c91f9e (C2 two-button combat), e07594c (C3 tab + second glove).
- EXONERATED BY IO (verified, do not re-check):
  * ded9664 light order touched NO player.js lines (diff fcd5b06..ded9664
    player.js is EMPTY) and did not touch anim.js.
  * anim.js untouched since 17933b0 (diff vs HEAD is EMPTY).
  * assets.js Order B change = sanity-check counts only (CHARACTERS dict); diff
    verified benign, WH_Walk clip lookup chain unchanged.
  * CONFIG.animRt.walkMetersPerCycle / runMetersPerCycle present (607/608/610-611).
  * game.js:1396 still calls player.anim.syncPlayer(player, dt) every frame.
  * player.anim is created in setBody() from WH_ASSETS.getClips('playerBody')
    inside preloadAll().then - boot chain unchanged.
  * player.update() movement block sets animMoveSpeed correctly (1336-1370);
    attacking/blocking multiplicities unchanged.
  * tryAttack/startAttack/getAttackPhase/attack-timer resolution read correct
    in HEAD; handButton dispatch reads correct.

## 2. IO'S OPEN SUSPECTS (ranked - work these first, add your own)
1. syncPlayer branch starvation: if player.attacking gets STUCK true (or
   getAttackPhase returns a degenerate phase like stage always windup / always
   strike with t frozen), the mixer never reaches setLocomotion and the walk
   clip never plays while positions still update (matches the symptom exactly:
   the character walks, the body holds an attack-ish frame).
2. Per-hand cast windup path: Order C moved windup ticking for BOTH hands
   (cast.main/cast.off). If a windup completes WITHOUT clearing c.windup
   (e.g. spellId null vs spawn path skipping the clear), and cast windup > 0
   feeds canCast/attacking interplay... look for any state where a cast windup
   never resolves to 0 (fizzled, refused at completion, spell deleted from
   belt, radiance cast path, focus starved at completion time).
3. attackMoveId/weaponId drift: Order B/C kept this.weaponId static
   (MV.playerWeapon) while hands hold items; getWeaponDef() in startAttack and
   getChainCap() - if any path makes attackMove undefined or a move id with
   windup/strike/recover = 0, getAttackPhase can divide/segment weirdly and
   the FSM timer can stall (attackTimer -= dt still runs though - check
   whether some NEW guard skips the decrement).
4. transition() restart storm: if something (regrip? offhand orb? blockButton
   cleanup?) calls anim.transition(..., restart) or hitActive flickers each
   frame, walk restarts at t=0 every frame = visually frozen at frame 0.
5. Anything in Order C's game.js diff (151 lines) that changed WHEN/WHETHER
   syncPlayer is reached per frame.

## 3. DELIVERABLES
1. ROOT CAUSE: name the exact mechanism (file:line before/after).
2. FIX: minimal, CONFIG-driven, committed to feat/world-visuals + pushed.
   - Commit message: fix(anim): walk animation regression from Order C - <one line>.
3. Report scratch/astrabot_walkanim_bugfix_report.md (committed): symptom,
   root cause chain, why each suspect above was/was not it, the fix, regressions
   you re-verified by READING (attack chain, roll cancel, cast windup both
   hands, Q swap, radiance light).
4. Final chat message: commits with shas, root cause one-liner, what to
   playtest.

## 4. PLAYTEST AC (Nicko)
| AC | Test |
|---|---|
| W1 | Walking plays the walk cycle (legs/arms visible motion), body advances |
| W2 | Sprint plays run faster than walk |
| W3 | Attack chain still plays swing clips + transitions back to walk cleanly |
| W4 | Cast windup + projectile unchanged; walk resumes while bolts fly |
| W5 | Roll still tumbles and returns to walk |
| W6 | Block (shield left) still holds; blocking slows to walk pace as before |