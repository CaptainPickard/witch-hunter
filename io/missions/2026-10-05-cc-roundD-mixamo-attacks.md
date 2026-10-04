# ROUND D CONTRACT: Mixamo attack clips into the longsword chain combo (IO -> Claude Code)

You are implementing IO-approved Round D in /workspace/witch-hunter. Follow this
contract EXACTLY. No harness runs, no headless browser game sessions, no
contact-sheet QA loops - Nicko playtests the build himself. Static probes and
Static probes and syntax checks only. Commit early and often: land the bake +
verify work as it completes rather than holding everything for one big finish.
All measurements you need are IN THIS CONTRACT. ZERO research beyond the
listed steps: the clip choices, names, timings, bake flags, wire pattern,
commit order, and serve steps are all decided below.

## Round D (binding)

Replace the SELF-AUTHORED Blender chain-combo attack clips in the longsword
combo with 3 Mixamo sword-pack attack clips. Keep the authored clips as
rollback. Rhythm stays: R2L slash -> L2R slash -> third distinct move.

## Chosen clips + names + timings (decided by IO from probes, DO NOT re-pick)

| config move | new clip name   | source FBX (scratch/mixamo-fbx/swordpack/) | clip dur | impact (windup) | strike window |
|-------------|-----------------|--------------------------------------------|----------|-----------------|---------------|
| slashR2L    | WH_SS_SlashR2L  | sword and shield slash.fbx                 | 1.500s (46f) | 0.567s (18f, 15.6 m/s peak) | 0.20s |
| slashL2R    | WH_SS_SlashL2R  | sword and shield slash (3).fbx             | 1.667s (51f) | 0.800s (25f, 11.7 m/s peak) | 0.27s |
| thrust      | WH_SS_Overhead  | sword and shield attack (4).fbx            | 1.000s (31f) | 0.400s (13f, 9.8 m/s peak)  | 0.43s |

Direction proof (roundD probe3, hand offset from spine, char faces -Y so Y- =
forward; start is [-0.37,+0.2,0.94] = right-hand guard for all three):
- slash.fbx: guard -> [p50 +0.49,-0.72,0.69] ( crosses LEFT while sweeping
  forward) -> returns to guard start. In-place, zero roots, zero spin. R2L.
- slash (3).fbx: guard -> [p25 +0.17,-0.71,1.28] ( already crosses RIGHT deep
  forward) -> [p50 -0.35,-1.09,1.44] -> returns. L2R.
- attack (4).fbx: guard -> [p25 -0.43,+0.32,1.41] raised high -> [p50
  -0.05,-0.70,1.44] down-forward through center. Compact overhead chop,
  distinct silhouette, reads as a third move. Thrust-slot substitute per
  Nicko's 10-05 order (pack has no true stab; documented substitution).

Rejected (do not use): slash (5) crouched (hips z 0.43 of stance), slash (4)
full 360 spin, attack (2)/(3) ~400deg spins, attack.fbx overhead with 3.6m
root travel + 44deg yaw drift.

Substitutions documented for Nicko: third move = overhead instead of stabbing
thrust (pack lacks one).

## Phase-duration adjudication (IO RULE - Testerbot audits this)

Phase durations are CONFIG-FIXED, NOT clip-duration-derived. Proof: player.js
getAttackPhase (line ~662) reads this.attackMove = CONFIG.moveset.weapons.
longsword.moves[move] (hardcoded windup/strike/recover seconds); anim.js
seekAttack (lines ~237-255) then slices the CLIP by those ratios and warp-
matches timeScale to the FSM clock every frame. Mixamo timing therefore does
NOT flow through automatically: the contract updates CONFIG per-move durations
to the measured values above so the clip plays near-naturally (timeScale ~1)
and damage lands on each clip's fastest-wrist impact frame.

Exact CONFIG edits (CONFIG.js, window.WH_CONFIG.moveset.weapons.longsword.moves):

    slashR2L: windup: 0.57, strike: 0.20, recover: 0.73   (total 1.50 = clip dur)
    slashL2R: windup: 0.80, strike: 0.26, recover: 0.61   (total 1.67 = clip dur)
    thrust:   windup: 0.40, strike: 0.43, recover: 0.17   (total 1.00 = clip dur)

Keep every OTHER field per move (pose, chainOpenSec, damage, range,
halfAngleDeg, lunge, staminaCost, damageGhoulMult) UNCHANGED except:
- slashR2L.chainOpenSec: 0.12 -> 0.20
- slashL2R.chainOpenSec: 0.12 -> 0.26
- thrust.chainOpenSec stays 0.40 (full recover anyway)
Rationale: chainOpenSec must sit inside the new strike windows so buffered
combos still open. Add a one-line comment in CONFIG.js at the moves block:
"Round D: durations derived from Mixamo impact frames (scratch/
swordpack_probe4_rD.json); totals equal clip durations."

## Bake (per branch, from that branch's own combat-chain.glb)

Tool: scratch/mixamo_retarget.py (proven). Write TWO manifest JSONs:

scratch/roundD-clips-dev.json:
    {"WH_SS_SlashR2L": "<abs path> sword and shield slash.fbx",
     "WH_SS_SlashL2R": "<abs path> sword and shield slash (3).fbx",
     "WH_SS_Overhead": "<abs path> sword and shield attack (4).fbx"}

scratch/roundD-clips-feat.json: same three entries (same sources). Both
manifests use the ABSOLUTE source path
/workspace/witch-hunter/scratch/mixamo-fbx/swordpack/<file>.fbx (the repo's
scratch/ is shared with the worktree, so this works from both checkouts).

Commands (from repo root; blender at /opt/blender-4.5.4-linux-x64/blender):

dev branch (main checkout /workspace/witch-hunter stays on dev):
    mkdir -p scratch/mixamo-fbx/rt_roundD
    <blender> -b --factory-startup --python-exit-code 1 --python scratch/mixamo_retarget.py -- \
      art-direction/3d/assets/races_regen/rigged/human-hunter-male.combat-chain.glb \
      scratch/mixamo-fbx/rt_roundD/dev-human-hunter-male.mixamo.glb \
      --clips scratch/roundD-clips-dev.json --log scratch/mixamo-fbx/reports/roundD-bake-dev.json
    then copy the output over art-direction/3d/assets/races_regen/rigged/human-hunter-male.combat-sword.glb
    (The .mixamo.glb temp files stay OUT of git. Round C used exactly this
    copy-over pattern - see the feat bake log's output path in
    scratch/mixamo-fbx/reports/player-sword-bake-feat.json.)

feat branch (worktree /tmp/wh-worldfeat, which shares the repo's scratch/):
    cd /tmp/wh-worldfeat
    mkdir -p /workspace/witch-hunter/scratch/mixamo-fbx/rt_roundD
    <blender> -b --factory-startup --python-exit-code 1 --python scratch/mixamo_retarget.py -- \
      art-direction/3d/assets/races_regen/rigged/human-hunter-male.combat-chain.glb \
      /workspace/witch-hunter/scratch/mixamo-fbx/rt_roundD/feat-human-hunter-male.mixamo.glb \
      --clips scratch/roundD-clips-feat.json --log scratch/mixamo-fbx/reports/roundD-bake-feat.json
      (note the ABSOLUTE output path: relative output resolution breaks under
      the worktree; this also prevents the worktree's cwd from changing the
      log's input path. Then:)
    cp /workspace/witch-hunter/scratch/mixamo-fbx/rt_roundD/feat-human-hunter-male.mixamo.glb \
      /tmp/wh-worldfeat/art-direction/3d/assets/races_regen/rigged/human-hunter-male.combat-sword.glb

Expected: dev 9 base + 3 = 24 clips; feat 13 base + 3 = 27 clips. The
retarget script's flags are all proven in scratch/mixamo-retarget-report.md -
it needs action_slot assignment; use exactly the invocation pattern of the
Round C commits (git show 534f5ef --stat for context).

## Verify (both branches; PASS required before wiring)

    python3 scratch/verify_retarget.py <branch combat-chain.glb> <branch combat-sword.glb> \
      --clips scratch/roundD-clips-<branch>.json \
      --bake-log scratch/mixamo-fbx/reports/roundD-bake-<branch>.json \
      --out scratch/mixamo-fbx/reports/roundD-verify-<branch>.json \
      --original-count <9 dev | 13 feat>
Do NOT pass --held-pose for the three attack clips (they are dynamic; the
frozen-threshold check must stay active for them).
Also: python3 scratch/test_mixamo_retarget.py (keep 11/11).

## Wire (same edits on BOTH branches)

1. anim.js: change MOVE_NAMES values only (object identity with VARIANTS.
   sword.moves MUST survive - feat anim.js line ~340 checks
   this.moveNames === MOVE_NAMES):
       var MOVE_NAMES = {
         slashR2L: 'WH_SS_SlashR2L',
         slashL2R: 'WH_SS_SlashL2R',
         thrust: 'WH_SS_Overhead'
       };
   Fallback: in the CharacterAnim constructor's move-actions loop (the
   Object.keys(this.moveNames) forEach, line ~96), when a move's clip is
   missing from the GLB, fall back to the authored clip name per move with a
   console.warn('[WH anim] move ' + move + ' missing ' + this.moveNames[move]
   + ', falling back'):
       var MOVE_FALLBACK_NAMES = { slashR2L: 'WH_SlashR2L', slashL2R:
       'WH_SlashL2R', thrust: 'WH_Thrust' };
   (module-level const next to MOVE_NAMES; fallback must resolve the
   authored clip and register the SAME actions[move] slot so playerAttack's
   per-move seek still drives it.)
2. Update the comment block above MOVE_NAMES (Round D note + rollback:
   one-line MOVE_NAMES revert to authored names).
3. assets.js clip-count check: dev branch "if (clips[name].length !== 6)"
   -> 24; feat branch "!== 25" -> 27 (update the adjacent comment counts:
   dev 9+... +12 Sword +3 SS; feat 13+12+3).
4. player.js: NO changes. moveset.js: NO changes. Enemy or ghoul/bandit
   paths: NO changes.

## Commits (git identity CaptainPickard <pickard.nicko@gmail.com>)

Per branch, in the branch's checkout, in this order (also `git add` the four
scratch/swordpack_probe*_rD.json measurement files into the bake commit, and
the contract file io/missions/2026-10-05-cc-roundD-mixamo-attacks.md plus
scratch/swordpack_probe2.py/3.py/4.py into the dev wiring commit):
    git add <combat-sword.glb> scratch/roundD-clips-<branch>.json \
      scratch/mixamo-fbx/reports/roundD-bake-<branch>.json \
      scratch/mixamo-fbx/reports/roundD-verify-<branch>.json
    git commit -m "feat(anim): bake 3 Mixamo attack clips into combat-sword.glb (Round D)" 
    git add prototype/js/anim.js prototype/js/CONFIG.js prototype/js/assets.js
    git commit -m "feat(anim): rewire MOVE_NAMES to WH_SS_* Mixamo attacks + CONFIG timings (Round D)"
    # feat only, then build:
    python3 tools/build_v7.py
    git add prototype/builds/v7-playable.html
    git commit -m "build: v7 bundle with WH_SS_* Mixamo chain attacks (Round D)"
Do NOT push (IO pushes after its own verification). Do NOT touch main. Do NOT
modify art/.../human-hunter-male.rigged.glb or combat-chain.glb or the authored
WH_SlashR2L/WH_SlashL2R/WH_Thrust clip data inside combat-sword.glb
(append-only GLBs on both branches).
NEVER commit scratch/mixamo-fbx/*.fbx and NEVER read, move, or commit
scratch/.mixamo-credentials.txt or scratch/.mixamo-storage.json.
Never use them (ZERO Mixamo-site work).

## Proof stills (exactly 3, after wiring, into <repo>/scratch/roundD-proof/)

Use blender headless + Xvfb DISPLAY=:99 (as Round A/B did; if :99 is down,
start one: Xvfb :99 -screen 0 1024x768x24 &). Full size (1024px), NO contact
sheets:
    01-rest.png           - player GLB rest, no clip, f0
    02-ss-slashr2l-mid.png - WH_SS_SlashR2L at impact frame f18 of its clip
    03-ss-overhead-mid.png - WH_SS_Overhead at impact frame f13 of its clip
(That is 3 stills total. Stop there. Name and label them via filenames only.)

## Stop / escalation rules

- If any step fails twice on real errors: mark FAILED with the exact error in
  your final report, continue the remaining steps that do not depend on it.
- Do NOT touch ghoul/bandit assets, region-manager, or spell/casting code.
- Do NOT run the game, a browser, playwright, the harness, or any game loop.
- Your FINAL REPORT must list: every git sha created (per branch), verify
  JSON pass counts, the exact grep -c result of WH_SS_SlashR2L in
  prototype/builds/v7-playable.html, the 3 still paths, any FAILED step with
  its error text, and any deviation from this contract.