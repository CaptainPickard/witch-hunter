# Testerbot valspec: Round D audit (IO -> Testerbot, READ-ONLY)

You are Testerbot for Witch Hunter Round D. Audit ONLY. You have Read and Bash
but NO Edit/Write. Do not modify any repo file. Do not run the game, a
browser, playwright, or any game loop: code/diff/JSON review and cheap static
verifiers only (Nicko is the tester; his playtest is the acceptance bar).

Repo: /workspace/witch-hunter (dev checked out in the main dir;
feat/world-visuals in the git worktree /tmp/wh-worldfeat). Nothing is pushed
yet: local dev @ 8da1aa1, local feat @ f3d8300; origin still has Round C
heads. Push is IO's job after your PASS - do NOT push, do NOT commit.

## Background (what to audit)

Round D replaced the longsword combo's self-authored attack clips
(WH_SlashR2L, WH_SlashL2R, WH_Thrust) with 3 Mixamo sword-pack clips, baked
per branch into art-direction/3d/assets/races_regen/rigged/human-hunter-male.
combat-sword.glb:
- WH_SS_SlashR2L from scratch/mixamo-fbx/swordpack/"sword and shield slash.fbx"
  (1.500s clip, impact frame at t=0.567s)
- WH_SS_SlashL2R from scratch/mixamo-fbx/swordpack/"sword and shield slash (3).fbx"
  (1.667s clip, impact frame at t=0.800s)
- WH_SS_Overhead from scratch/mixamo-fbx/swordpack/"sword and shield attack (4).fbx"
  (1.000s clip, impact frame at t=0.400s)
The thrust slot plays an overhead chop: the pack has no true stab. This
substitution was decided by IO per Nicko's 10-05 order and is documented.

Round D commits (audit every one: git show --stat + read the diffs):
- dev: 4391181 (bake), 8da1aa1 (wiring)
- feat/world-visuals: 9491894 (bake), d45401e (wiring), f3d8300 (build)

Bake history note: each branch's combat-sword.glb was baked from that
branch's PRE-ROUND-D combat-sword.glb snapshot (kept at scratch/mixamo-fbx/
rt_roundD/<dev|feat>-base-combat-sword.glb, untracked), not from
combat-chain.glb. The snapshots are byte-identical to the pre-bake HEAD blobs
(dev = 21 clips = 9 chain/shield + 12 sword-locomotion; feat = 25 clips =
13 + 12). verify_retarget.py ran with --original-count 21 (dev) / 25 (feat).

## Required checks, in order

### 1. Commit scope audit (git show --stat every SHA)

For each of the five SHAs, confirm the stat matches the message:
bake commits touch ONLY the GLB + bake/verify/probe JSONs + manifest JSONs +
scratch/test_mixamo_retarget.py; wiring commits touch ONLY prototype/js/
anim.js + CONFIG.js + assets.js (+ the contract file io/missions/
2026-10-05-cc-roundD-mixamo-attacks.md and scratch/swordpack_probe2/3/4.py on
dev); the build commit touches ONLY prototype/builds/v7-playable.html.
Flag ANY file outside this scope. Confirm none of these entered git: any
.fbx, any .mixamo.glb temp, scratch/.mixamo-credentials.txt,
scratch/.mixamo-storage.json.

### 2. Phase-durations adjudication review (the IO ruling)

Trace the timing pipeline in the code yourself, then judge:
- CONFIG.js window.WH_CONFIG.moveset.weapons.longsword.moves holds per-move
  windup/strike/recover seconds.
- player.js getAttackPhase (~line 660) reads this.attackMove - the move-def
  snapshot taken in startAttack - and slices elapsed time into windup /
  strike / recover by those CONFIG numbers. player.js needed no changes.
- anim.js playerAttack -> seekAttack: for per-move clips it slices the CLIP
  by the duration RATIO (a = dur * windup/total, b = dur * (windup+strike)/
  total) and warp-matches action.timeScale = span/duration every frame.
Therefore phase durations are CONFIG-FIXED, not clip-duration-derived, and
the fix was to update CONFIG to the measured clip values so timeScale ~= 1
and the strike stage aligns with each clip's fastest-wrist impact frame.
- Confirm the commit-diffed values: slashR2L 0.57/0.20/0.73 (total 1.50),
  slashL2R 0.80/0.26/0.61 (total 1.67), thrust 0.40/0.43/0.17 (total 1.00),
  and that the totals equal the baked clip durations 1.50/1.67/1.00 (check
  the durations in scratch/mixamo-fbx/reports/roundD-bake-*.json).
- Cross-check each windup against the measured impact time in scratch/
  swordpack_probe4_rD.json (0.567 / 0.8 / 0.4 -> rounded 0.57 / 0.80 / 0.40).
- Judge chainOpenSec: old 0.12 -> new 0.20 (R2L) and 0.26 (L2R), thrust kept
  0.40. Consistency question: chain window must sit inside the strike stage
  for buffered chaining to fire without skipping stages. PASS or FAIL this
  adjudication explicitly.

### 3. Invariant re-run (both branches)

Run both verbatim (from /workspace/witch-hunter):
    python3 scratch/verify_retarget.py scratch/mixamo-fbx/rt_roundD/dev-base-combat-sword.glb art-direction/3d/assets/races_regen/rigged/human-hunter-male.combat-sword.glb --clips scratch/roundD-clips-dev.json --bake-log scratch/mixamo-fbx/reports/roundD-bake-dev.json --out /tmp/tb-verify-rD-dev.json --original-count 21
    python3 scratch/verify_retarget.py scratch/mixamo-fbx/rt_roundD/feat-base-combat-sword.glb /tmp/wh-worldfeat/art-direction/3d/assets/races_regen/rigged/human-hunter-male.combat-sword.glb --clips /tmp/wh-worldfeat/scratch/roundD-clips-feat.json --bake-log /tmp/wh-worldfeat/scratch/mixamo-fbx/reports/roundD-bake-feat.json --out /tmp/tb-verify-rD-feat.json --original-count 25
Requirements: each run ends with zero failed_assertions; dev has 40 passing
assertions, feat 44; new_clips lists exactly WH_SS_SlashR2L, WH_SS_SlashL2R,
WH_SS_Overhead; every previously baked clip is byte-identical.
Also run from BOTH checkouts:
    python3 scratch/test_mixamo_retarget.py
Requirement: 11 tests, OK, on both.
Also parse-check the six edited JS files (no node on this box - use python
esprima): prototype/js/anim.js, CONFIG.js, assets.js on both branches.

### 4. Identity check + fallback review (feat anim.js @ d45401e)

Confirm on the feat worktree:
- anim.js still contains the exact expression
  (this.moveNames === MOVE_NAMES ? CLIP_NAMES[this.clip] : null) - the
  identity check intact.
- MOVE_NAMES values are exactly WH_SS_SlashR2L / WH_SS_SlashL2R /
  WH_SS_Overhead, and VARIANTS.sword.moves is the SAME MOVE_NAMES object
  (assigned by reference, declared before VARIANTS).
- MOVE_FALLBACK_NAMES keeps the authored names (WH_SlashR2L / WH_SlashL2R /
  WH_Thrust) and the constructor's move loop falls back to them when a
  WH_SS_* clip is missing, registering actions[move] from the authored clip
  and console.warn-ing.
- Fallback degrade analysis: the fallback fires only when a WH_SS_* clip is
  absent; then seekAttack slices the OLD authored clip by the NEW CONFIG
  ratios. The old clips were authored on the old proportions
  (0.14/0.20/0.30, 0.16/0.14/0.40), so a fallback on the new CONFIG would
  mis-slice the old clip (a 0.57s windup slice = 38% of the old clip). This
  is a degraded-but-playable safety net with a loud warning. Confirm it
  cannot strand a state (actions[move] always gets an action if either clip
  exists; if BOTH clips are missing the move silently skips the loop entry -
  check whether playerAttack then falls to the shared 'attack' key, making
  the net complete).
- Rollback coherence: reverting MOVE_NAMES values to the authored names (+
  CONFIG timings) restores Round C behavior exactly. Confirm the commit
  message and the contract (io/missions/2026-10-05-cc-roundD-mixamo-attacks.md)
  document this.

### 5. Serving verification (static part; the live curl is IO's post-audit)

On the feat worktree at f3d8300, verify prototype/builds/v7-playable.html:
    grep -c "WH_SS_SlashR2L" prototype/builds/v7-playable.html   -> 1
    grep -c "windup: 0.57" prototype/builds/v7-playable.html     -> 1
    grep -c "playerBody: 27" prototype/builds/v7-playable.html   -> 1
    grep -c "windup: 0.14" prototype/builds/v7-playable.html     -> 0
  (the old longsword move values 0.14/0.20/0.30 must be gone; the handAxe
  moves keep windup 0.10/0.12 and moveMultWhileAttacking keeps windup 0.3 -
  beware false positives, hence the exact-string checks above).
State explicitly: IO has NOT yet done the host refresh of /tmp/wh-worldfeat-
clean or the 8793 curl (that happens after your PASS), so live-serve checks
are out of scope for you.

### 6. Disclosed watch-items (verify all five are visible in artifacts)

1. Impact-still timing reading: the 02/03 proof stills show the arm raised
   at strike-START (the still frame is the hit-frame t where windup ends and
   strike begins; the cross-body sweep happens later IN the 0.20/0.43s
   strike windows - consumeAttackSweep applies damage across the whole
   strike stage, so hit registration is unaffected; this is a feel/look
   watch item for Nicko's playtest).
2. Still rendering artifacts: cloak clipping through the arm/leg, shoulder
   pinch (candy-wrapper) at the raised arm, slight ankle distortion at the
   planted foot in the impact stills.
3. Fallback-mode mis-slice degrade (old clip sliced by new ratios,
   loud console.warn, still playable).
4. Chain-open is the whole strike stage in consumeAttackSweep, so
   impact-frame alignment (per swing) is about damage-window FEEL
   (who hits first), not about hit registration.
5. Dev's prototype/builds/v7-playable.html is stale (feat-only build per
   contract; dev is served by the /playtest/ route straight from the dev
   checkout, so nothing serves the stale bundle).

## Output format

Final answer, structured:
VERDICT: PASS | FAIL (with exact failed check numbers)
Then: per-check summary (1-6), a judgment line for each deviation
1-6 (deviation list is below), the five watch-items quoted, anything
unexpected, and any step that FAILED twice (stop + exact error).

Deviations from the contract (Claude Code's report, for your judgment):
1. Bake input = pre-Round-D combat-sword.glb snapshot, not combat-chain.glb.
   Contract as written would have wiped the Round C sword-locomotion clips
   (the retarget script rebuilds all animation data from the input GLB), so
   the child adapted and verified byte-identity of ALL 21/25 prior clips
   instead of 9/13. Judge: is this strictly stronger, and were the
   contract's end state (24/27 clips, locomotion intact, authored chain
   clips intact) still achieved?
2. scratch/test_mixamo_retarget.py extended on both branches: the player-
   sword pair test now includes the Round D manifest (15 new clips instead
   of 12). Judge: reasonable scope or creep?
3. Dev assets.js: expected-count check split per body (playerBody 24,
   banditBody/ghoulBody 6) instead of contract's flat 24 - because dev
   shares the check across all three bodies while feat already has a
   per-body CHARACTERS table (playerBody 27). Judge: was flat 24 wrong on
   dev?
4. scratch/ is a SEPARATE checkout (not shared) between main dir and
   worktree - contract assumed shared. Child committed the probe JSONs and
   the feat manifest/bake log in each branch's own scratch/ and copied
   roundD-clips-feat.json to both. Judge: harmful or harmless?
5. The 3 proof stills + scratch/roundD_proof_render.py left UNTRACKED (not
   committed). Judge: consistent with Round C precedent (Round C stills
   also untracked)?
6. Dev's prototype/builds/v7-playable.html NOT rebuilt (build was feat-only
   per contract). Judge: does dev's stale bundle block anything, given dev
   is served from the dev checkout by the /playtest/ route?

If PASS: also confirm (a) both branches are ready for IO to push without
rebase, (b) IO should proceed to the host refresh of /tmp/wh-worldfeat-clean
+ 8793 curl verification, and (c) the acceptance bar is Nicko's playtest
verdict via the Playtest button, NOT your audit.