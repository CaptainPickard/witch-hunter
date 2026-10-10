# ROUND C CONTRACT: Player sword-pack wiring (Claude Code)
Issued 2026-10-05 by IO. This file = your complete contract. Round B LANDED
(bandit cape-fixed + wired, serving on 8793). Your scope is the PLAYER only.

## State (verified)
- Repos/branches as Round B left them: dev @ 889daad (checkout), worktree
  /tmp/wh-worldfeat @ cee616a [feat/world-visuals]. Push both.
- Player today: human-hunter-male.combat-chain.glb - 9 clips (WH_Idle, WH_Walk,
  WH_Run, WH_Attack1, WH_Hit, WH_Death + chain moves WH_SlashR2L/WH_SlashL2R/
  WH_Thrust). anim.js: NAMES + MOVE_NAMES (+ VARIANTS zombie/bandit tables +
  CLIP_NAMES shield tables). player.js:130 new WH_CharacterAnim(meshRoot,
  getClips('playerBody')) - NO options arg (default map). assets.js playerBody
  -> combat-chain.glb (KEEP THIS FILE AS-IS).
- Staged Mixamo sword pack: /workspace/witch-hunter/scratch/mixamo-fbx/swordpack/
  = 51 FBX @30fps (sword-and-shield: 4 idles + looking variants, walk fwd/back,
  run fwd, turn 90s, crouching, block idles + reacts, slashes S/S-P, attacks
  high/low/jump/hilt, combo packs. FULL LIST: run ls).
- Blender headless + pipeline: scratch/mixamo_retarget.py (constraint+bake route,
  per-clip RT_ tracks + action_slot, bone_heuristic BLENDER, exporter action-slot
  rules in scratch/mixamo-retarget-report.md), append route scratch/glb_append_
  clips.py (matches by bone NAME), verifier scratch/verify_retarget.py,
  regression scratch/test_mixamo_retarget.py (10/10 green).

## Round C tasks
1. CURATE 8-12 clips from swordpack/ by INSPECTING NAMES + DESCRIPTIONS (ls the
   dir; each FBX has a mixamorig armature; NO browser work). Pick the set that
   upgrades locomotion + adds shield/block flavor WITHOUT breaking the chain
   attack system:
   REQUIRED: sword-and-shield idle (standing), sword-and-shield walk forward,
   sword-and-shield run forward.
   RECOMMENDED ADDS (judge by name, prefer variety): sword-and-shield idle
   looking ver. 1, crouch block idle, sword-and-shield strafe, turn 90 L+R,
   sword-and-shield crouching.
   AVOID: jump attacks, hilt melee, unarmed/equip/disarm/taunt (out of scope).
   Write scratch/mixamo_player.json: {WH_SwordIdle: <fbx>, WH_SwordWalk: <fbx>,
   WH_SwordRun: <fbx>, WH_SwordIdleLook: <fbx>, WH_ShieldCrouchIdle: <fbx>,
   WH_SwordStrafe: <fbx>, WH_SwordTurnL: <fbx>, WH_SwordTurnR: <fbx>,
   WH_SwordCrouch: <fbx>} (key set = your curated picks; naming stays in the
   WH_ namespace, no collisions with existing player clip names).
2. BAKE: output art-direction/3d/assets/races_regen/rigged/human-hunter-male.
   combat-sword.glb (NEW file; original combat-chain.glb bytes NEVER change).
   Base = the CURRENT combat-chain.glb (9 clips) -> retarget appends the new
   clips (expected: 9+9=18). Keep exporter/pipeline flags EXACTLY as the bandit
   round used them.
3. VERIFY: run/extend scratch/verify_retarget.py for this pair: all 9 original
   clips byte-identical (BIN-prefix + append-only JSON), new clips 60ch/20node/
   30fps, quat norms 1.0. Regression suite still 10/10 (add a player-pair test
   if the pattern supports it cheaply - optional).
4. RENDER PROOF FOR NICKO (3 stills ONLY, full-size, into
   scratch/swordwire-proof/): rest pose on WH_SwordIdle, mid-stride on
   WH_SwordWalk, mid-block on WH_ShieldCrouchIdle (if curated) or best
   alternative. Vision-analyze each ONCE. NO contact sheets, NO per-clip mill.
5. WIRE:
   - anim.js: add a SWORD variant to VARIANTS: names override idle/walk/run to
     the WH_Sword* clips, attack/hit/death STAY canonical, moves = MOVE_NAMES
     UNCHANGED (chain moves must keep working identically), same per-slot
     fallback safety.
   - player.js: pass {variant:'sword'} at the CharacterAnim construction.
   - assets.js: playerBody GLB path -> human-hunter-male.combat-sword.glb
     (texture path unchanged; CHARACTERS preload: playerBody entry stays).
   - enemy.js/ghoul/bandit paths: DO NOT TOUCH.
6. SYNTAX + STATIC: compile-check edited JS (parse OK; VARIANTS has 3 keys;
   every sword clip resolvable by name in the new GLB). No game runs (Nicko law).
7. COMMIT + PUSH + SERVE (not done until all done):
   a. Commits on BOTH branches (same messages): rebake, wiring, build, plan doc.
   b. python3 tools/build_v7.py IN /tmp/wh-worldfeat AFTER wiring commit + build
      commit.
   c. Push dev:dev and feat/world-visuals:feat/world-visuals.
   d. Refresh serving: git -C /tmp/wh-worldfeat-clean reset --hard <feat build
      sha> (that folder lives on the HOST; container /tmp is different - reset
      --hard is the reliable refresh; verify with a host-side check).
   e. Host-verify via python3 /tmp/dhost.py: curl 8793
      /prototype/builds/v7-playable.html => 200 AND grep -c WH_SwordIdle >= 1.
      Recreate the container ONLY if it serves empty/404:
      docker rm -f wh-playtest-8793 && docker run -d --name wh-playtest-8793
      --network host --restart unless-stopped -v /tmp/wh-worldfeat-clean:/srv:ro
      python:3-alpine python -m http.server 8793 --directory /srv
8. Update io/mixamo-anim-campaign-plan.md Round C section + commit on dev.

## HARD LAWS
- NO automated game/harness runs (Nicko plays; static + stills only).
- ZERO Mixamo-site work. NO ghoul/bandit changes. NO prototype/builds hand
  edits (always build_v7.py). Canonical GLB bytes never change. If a step
  fails twice on real errors, mark FAILED with exact error, continue.
- NEVER fabricate verification output.

## ROLE ADDENDUM
You are the implementer (Devbot lane). Work autonomously, commit early/often.
FINAL message report: curated list + why, bake/verify results, 3 render paths +
vision verdicts, wiring diffs, commit SHAs both branches, push confirmations,
8793 host verification output, FAILED steps. Max 400 words except lists.