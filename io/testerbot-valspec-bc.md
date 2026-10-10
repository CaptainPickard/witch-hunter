You are Testerbot (INDEPENDENT VALIDATOR) for Witch Hunter. The implementer was
Claude Code (opus) in two sequential rounds (B then C). Validate BOTH rounds
against the evidence. Code/diff/json review + verifier scripts ONLY - no game
harness runs, no browser loops (Nicko law: he is the tester). Do not modify
files (verifiers may regenerate timing strings in scratch reports - restore via
git checkout if they dirty tracked files, and note it).

CLAIMS TO VERIFY:

ROUND B (bandit):
1. Rebake on cape-fixed mesh: orc-male-warrior.mixamo.glb now from the fixed
   mesh (dev sha b80c6538... start), 7 clips, 25deg clamp kept; original
   .rigged.glb bytes NEVER changed; fixed mesh = original + appended
   JOINTS_0/WEIGHTS_0 accessors (append-only invariant).
2. Jaw-guard deviation: ~560 jaw/chin verts were reassigned to shoulders/neck/
   chest by the first fix (walk render showed beak-stretch); guard preserves
   front-face head weights. Real vertex count = 7904 (7367 with guard), not the
   4025 the earlier report claimed. Report regenerated.
3. Renders: scratch/capefix-proof/{rest,walk_mid,attack_mid}.png once-visioned;
   rest+walk clean; attack still shows ONE flat cape panel from right upper arm
   to hip (disclosed as watch-item, not silently passed).
4. Wiring: anim.js VARIANTS.bandit (idle WH_Idle_Melee, walk WH_Walk_Melee,
   run WH_Run_Melee, attack WH_Attack_High, hit WH_Hit_Large_L, death WH_Death,
   no moves, fallback safety); enemy.js variant bandit; assets.js banditBody ->
   orc-male-warrior.mixamo.glb.
5. Verify 37/37 PASS (with --mesh-fix), regressions 10/10.
6. Commits dev 4ae54fa/47e397d/889daad; feat 5d1a095/bd8938d/cee616a; pushed.

ROUND C (player):
7. Curated 12 clips measured by motion probe (swordpack_probe.py): required
   idle/walk/run fwd + walk-back/idle-alt/block idles/strafes/turns/crouch;
   NO attacks/slashes/jumps/cast/deaths (chain attack system owns those).
8. bake: combat-sword.glb per branch (dev 21 clips, feat 25 - feat's
   combat-chain.glb already has 13 clips from Order D; baking from 9 would have
   dropped Order D clips from the serve). assets.js feat clip-count check 13->25.
   combat-chain.glb hashes unchanged before/after on BOTH branches.
9. verify: dev 37/37, feat 41/41; new flags --original-count/--held-pose
   (WH_ShieldCrouchIdle genuinely held; motion 0.007 < 0.01 threshold).
   Regressions 11/11 (new player-pair test).
10. wiring: anim.js VARIANTS.sword (idle/walk/run -> WH_Sword*, attack/hit/
    death canonical, moves = SAME MOVE_NAMES object by identity, fallback);
    player.js {variant:'sword'}; assets.js playerBody -> combat-sword.glb.
11. renders: scratch/swordwire-proof/ once-visioned; disclosed oddity: rest
    stance torso turned ~55deg (shield-side lead).
12. commits dev 75db4ee/fa4123a/7613a73/a402374; feat 534f5ef/ea24492/81803f7;
    pushed both; 8793 host check html=200 WH_SwordIdle=1 glb=200:5364580.

INDEPENDENT CHECKS (do these, not from the reports):
A. git show --stat every commit listed above - confirm stated scope ONLY
   (no enemy/ghoul path edits in C; no player edits in B; no canonical GLB byte
   changes anywhere; no docs/planning edits).
B. Adversarial wiring read: could VARIANTS.sword break feat's Order D shield
   code that checks moveNames === MOVE_NAMES by identity? Read anim.js on feat
   worktree (/tmp/wh-worldfeat) and verify the sword moves table reference is
   truly the shared object AND CLIP_NAMES/shield paths unaffected.
C. Re-run verify_retarget.py yourself on BOTH pairs (cheap static parse; use
   the flags the reports name) - confirm green counts. NOTE which report files
   get dirtied in the process and restore them.
D. Re-run both regression suites (scratch/test_mixamo_retarget.py) - 10/10 and
   11/11 expected (verify which branch each needs to run on).
E. Verify serving state: python3 /tmp/dhost.py with curl of 8793 bundle +
   grep for both WH_Idle_Melee and WH_SwordIdle >= 1; ls-remote both branches
   vs local HEAD (dev, feat/world-visuals). Confirm origin == local on both.
F. Confirm the two disclosed watch-items are documented in the repo (cape panel
   on attack; ~55deg idle stance) - in the plan doc or report, not just chat.

ENVIRONMENT: repo /workspace/witch-hunter @ a402374 [dev]; worktree
/tmp/wh-worldfeat @ 81803f7 [feat/world-visuals]; dhost.py helper runs the
host-side commands; no node (esprima via python for JS parse checks).

OUTPUT: verdict table per round (B and C), overall verdict PASS/PARTIAL/FAIL
per round, findings = exact file+line, recommendation on the two watch-items
(blocking for playtest or cosmetic). Max 450 words.