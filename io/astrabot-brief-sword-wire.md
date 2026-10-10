# ASTRABOT MISSION BRIEF: Player sword-pack wiring (Round C of A->B->C ladder)
Issued: 2026-10-05 by IO. NO CHAT CONTEXT - this brief is the complete contract.
ROUNDS A (ghoul wiring) AND B (orc cape fix) MUST LAND + VALIDATE BEFORE this
round starts. Do not start early. Do not touch their scope.

## Current state (verified)
Repo /workspace/witch-hunter, branch dev (A+B landed). Git identity
CaptainPickard <pickard.nicko@gmail.com>. Push via HTTPS credential store.
- Player body: art-direction/3d/assets/races_regen/rigged/human-hunter-male.
  combat-chain.glb - 9 clips: WH_Idle, WH_Walk, WH_Run, WH_Attack1, WH_Hit,
  WH_Death + chain attacks WH_SlashR2L/WH_SlashL2R/WH_Thrust (wired via
  anim.js MOVE_NAMES, chain-attack system landed in commits 1632097..a890f41).
  This is the canonical player asset: byte-identity protection applies.
- Wiring map: prototype/js/anim.js NAMES + MOVE_NAMES; CharacterAnim used by
  player.js:130 with getClips('playerBody'); assets.js playerBody entry -> the
  combat-chain.glb.
- Nicko's staged Mixamo sword pack: scratch/mixamo-fbx/swordpack/ (51 FBX,
  sword-and-shield set: idle/walk/run/strafe variants, block states, slashes,
  crouch etc). Zombie pack singles also staged but ghoul scope already landed
  (do not double-touch ghoul).

## Round C task
1. CURATE from scratch/mixamo-fbx/swordpack/ the best 8-12 clips that map onto
   the player's existing state/chain system without breaking the landed chain
   attack work: candidates = sword-and-shield idle, walk, run, strafe,
   crouch block, standing block react, attack variants that could serve as
   alternate chain moves. Write scratch/mixamo_player.json mapping WH_ names.
   NAMING: new player clips MUST use the WH_* namespace with suffixes that do
   not collide with existing player clip names (e.g. WH_SwordIdle, WH_SwordWalk,
   WH_SwordRun, WH_ShieldBlockIdle, WH_ShieldHit_L...). Do NOT rename or replace
   existing WH_SlashR2L/WH_SlashL2R/WH_Thrust/WH_Attack1 - chain moves stay.
2. BAKE via the proven pipeline (scratch/mixamo_retarget.py, per-clip RT_ tracks
   + action_slot; keep bone_heuristic='BLENDER'; exporter slot rules documented
   in scratch/mixamo-retarget-report.md). Base GLB = the CURRENT committed
   human-hunter-male.combat-chain.glb; output =
   human-hunter-male.combat-sword.glb (NEW FILE - the combat-chain.glb bytes
   MUST remain untouched on disk and in git).
   Player clip-name variant: SWORD map (like Round A's ZOMBIE pattern): idle/
   walk/run swap to sword variants IF the bake passes QA; hit/death stay
   canonical; MOVE_NAMES unchanged.
3. If wiring the sword locomotion would change player speed feel: do NOT touch
   game speed constants; pure clip swap only (movement code already drives the
   anim speed; if clip duration differs the existing crossfade handles it).
4. QA loop: render mid+end for EVERY new player clip (full-size, one vision
   call per frame), save under scratch/mixamo-fbx/qa/player/. PASS = no mesh
   collapse, natural pose, sword grip sane (proxy sword rules from prior round
   docs apply if needed for judging).
5. VERIFY: run scratch/verify_retarget.py adapted for this pair (original
   combat-chain.glb vs new combat-sword.glb): all 9 existing clips BIN-prefix +
   append-only-JSON identical; new clips 60-channel/20-node/30fps. Regression
   tests (scratch/test_mixamo_retarget.py pattern) extended for the player GLB.
6. WIRE: assets.js gains playerBodySword (or playerBody path swap ONLY IF
   variant map lands - prefer explicit name to avoid preloading ambiguity);
   player.js uses the SWORD map (same fallback-per-slot safety as Round A).
   Chain attack flow MUST behave identically (MOVE_NAMES resolution untouched).
7. Bandit + ghoul paths: DO NOT TOUCH.

## Gate discipline
Commit EARLY/OFTEN (feat:). Behavioral evidence (headless playtest load: player
uses sword idle/walk, chain attacks still fire correct clips, no console errors,
no bandit/ghoul regression) BEFORE push. Update io/mixamo-anim-campaign-plan.md
Round C section.

## Report back
Curated clip list + WH names, bake report path, QA verdicts per frame, verifier
results, wiring diffs, evidence JSON + screenshots paths, commit SHAs, push
confirmation, deviations + why.