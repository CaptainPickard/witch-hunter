# ROUND B CONTRACT: Orc cape-fix pipe-through + bandit Mixamo wiring (Claude Code)
Issued 2026-10-05 by IO. This file + ROLE ADDENDUM at the bottom = your complete
contract. Sequential after Round A (ghoul wiring, LANDED: 5b5d444 on both
feat/world-visuals and pushed origin). You may NOT start Round C (sword pack) -
a separate run handles it after this round validates.

## State (verified, do not re-derive)
- Repo: /workspace/witch-hunter on branch dev @ e460fc2 (checkout); playtest
  worktree /tmp/wh-worldfeat on feat/world-visuals @ 5b5d444 (Round A cherry-
  picks + ghoul wiring + fresh build, pushed to origin by IO).
- Git identity configured: CaptainPickard <pickard.nicko@gmail.com>. Push via
  HTTPS (deploy key read-only). Commits to BOTH dev (main checkout) and
  feat/world-visuals (worktree /tmp/wh-worldfeat) are REQUIRED this round.
- Blender headless: /opt/blender-4.5.4-linux-x64/blender. No node on box.
- The retarget pipeline (Round A era, landed): scratch/mixamo_retarget.py
  (constraint+bake, per-clip RT_ NLA tracks + action_slot; 25deg Spine/Chest
  clamp landed in b599cc1), append route scratch/glb_append_clips.py,
  verifier scratch/verify_retarget.py, bandit clip map scratch/mixamo_bandit.json
  (7 clips), bake/QA reports in scratch/mixamo-fbx/reports/.
- THE DEFECT (diagnosed 10-05, do not re-derive): orc cape/lat/hand vertices
  were auto-rig_weighted to anatomically distant bones. At rest the bones
  overlap in space so the ORIGINAL authored WH_* clips render fine; Mixamo clips
  move the arms away -> stuck verts extrude into rigid slab fans. Evidence
  renders: scratch/mixamo-fbx/qa/bandit/{WH_Idle_Melee,WH_Attack_Horiz,
  WH_Hit_Large_L}{,_end}.png (slabs visible at/near rest).
- THE FIX (built, byte-surgical, VERIFIED by prior run, killed before pipe):
  scratch/orc_weight_fix.py + scratch/orc_stretch_probe.py +
  scratch/mixamo-fbx/reports/orc-weight-fix.json (4025/23109 verts changed:
  per-bone capsule regions, keep-threshold 0.5, far_ratio 1.5, rigid
  reassignment only where no hierarchy neighbor holds 50%+).
  OUTPUT ALREADY ON DISK: scratch/mixamo-fbx/capefix/orc-male-warrior.rigged.glb
  (5,289,560 bytes; canonical BIN stays byte-identical prefix - report header
  documents the append-only JOINTS_0/WEIGHTS_0 accessor swap).

## Round B tasks
1. PIPE THE FIX: rebuild orc-male-warrior.mixamo.glb FROM THE FIXED MESH:
   run the proven pipeline with the cape-fixed mesh GLB as the retarget base,
   same 7-clip bandit map (scratch/mixamo_bandit.json), 25deg clamp preserved.
   IMPORTANT: retarget.py imports the base GLB and re-appends clips; verify it
   accepts the capefix mesh (JOINTS_0 accessor indices changed - the append
   script remaps by bone NAME, confirm before running; if the fixed mesh breaks
   the append route, extend the script minimally and DOCUMENT the change).
   Output: art-direction/3d/assets/races_regen/rigged/orc-male-warrior.mixamo.glb
   (overwrite in the FEAT WORKTREE first; then mirror to dev checkout - both
   branches must carry the same bytes; commit identically on both).
2. RENDER PROOF (for NICKO - he is the only tester, law of 10-04): render
   EXACTLY 3 stills, full-size, into scratch/capefix-proof/: rest pose, walk
   mid-stride, attack mid-swing. ONE render script, NO contact sheets, NO
   per-clip QA mill. Vision-analyze each once to confirm slab-free and note
   anything Nicko should look for; he makes the final call by PLAYING.
3. VERIFY: adapt/run scratch/verify_retarget.py (or its capefix variant) so the
   green checks prove: mesh fixed accessor present, all 6 original clips
   byte-identical (BIN-prefix + append-only JSON relative to the ORIGINAL
   .rigged.glb), all 7 bandit clips 60ch/20node/30fps, quaternion norms 1.0.
   Also run scratch/test_mixamo_retarget.py regression suite.
4. WIRE THE BANDIT: enemy.js already passes {variant:'zombie'} only for ghouls.
   Add a BANDIT map to anim.js VARIANTS: idle WH_Idle_Melee, walk WH_Walk_Melee,
   run WH_Run_Melee, attack WH_Attack_High, hit WH_Hit_Large_L, death WH_Death
   (canonical), no move clips, same per-slot fallback safety. enemy.js passes
   {variant:'bandit'} for bandits. assets.js banditBody -> orc-male-warrior.
   mixamo.glb (texture path unchanged).
5. SYNTAX + SMOKE: compile-check the 3 edited JS files headless (parse OK +
   CharacterAnim.VARIANTS now has zombie+bandit keys). NO game harness runs
   (Nicko law: he is the tester; automated game-loop evidence BANNED).
6. COMMIT + PUSH + SERVE (the round is NOT done until ALL done):
   a. Commit everything on BOTH branches (dev: main checkout; feat/world-visuals:
      /tmp/wh-worldfeat). Same messages on both.
   b. Rebuild the bundle IN the worktree AFTER the wiring commit:
      python3 tools/build_v7.py (run from /tmp/wh-worldfeat) + build commit.
   c. Push both branches: dev:dev and feat/world-visuals:feat/world-visuals.
   d. Refresh the -clean detach for the 8793 host container:
      git -C /tmp/wh-worldfeat-clean checkout --detach <feat-build-sha>
      (if /tmp/wh-worldfeat-clean is missing, recreate:
      cd /workspace/witch-hunter && git worktree prune && git worktree add
      --detach /tmp/wh-worldfeat-clean <feat-build-sha>).
   e. Host-verify (via python3 /tmp/dhost.py, which execs on the HOST):
      curl 8793 /prototype/builds/v7-playable.html => 200 AND
      grep -c WH_Idle_Melee => >=1 (i.e. NOT 0). If the 8793 container 404s
      or serves empty, recreate it:
      docker rm -f wh-playtest-8793 && docker run -d --name wh-playtest-8793
      --network host --restart unless-stopped -v /tmp/wh-worldfeat-clean:/srv:ro
      python:3-alpine python -m http.server 8793 --directory /srv
      then re-verify. ONLY after this verification do you report done -
      Nicko reloads and plays.
7. Update io/mixamo-anim-campaign-plan.md Round B section (wiring summary +
   proof paths) and commit it with the round.

## HARD LAWS
- NO automated game/harness/smoke-loop runs (Nicko 10-04 law; he playtests).
  Static checks + still renders only.
- ZERO Mixamo-site work. NO ghoul path changes. NO player.js/anim wiring changes
  beyond the bandit variant table + enemy.js variant arg. Do NOT touch
  prototype/builds by hand - always via tools/build_v7.py.
- .rigged.glb canonical originals: READ ONLY (bytes never change).
- If any step fails twice on real errors, stop that step, mark FAILED with the
  exact error and continue the rest. NEVER fabricate verification output.

## ROLE ADDENDUM
You are the implementer (Devbot lane) for this brief. The context above is the
complete contract. Work autonomously, commit early/often, and as your FINAL
message report: pipe-through result/accessor-note, 3 render paths + vision
verdicts, verifier + regression results, wiring diffs, commit SHAs on both
branches, push confirmations, 8793 host-verification output, and any FAILED
steps. Keep the report under 400 words except the lists.