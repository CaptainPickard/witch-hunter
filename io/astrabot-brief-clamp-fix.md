# ASTRABOT MISSION BRIEF: Bandit clip clamp-rebake fix round (Testerbot follow-up)
Issued: 2026-10-05 by IO. NO CHAT CONTEXT - this brief is the complete contract.
Context: The Mixamo retarget bake round landed on dev (commits e20d68d, 1fa07f2,
41935dc, 7cb7a33 range; GLBs orc-male-warrior.mixamo.glb + undead-ghoul-male.mixamo.glb).
Testerbot (opus, independent PASS/FAIL audit) validated: 5 criteria PASS, criterion E
(pose QA) PARTIAL. This fix round addresses exactly that.

## Nicko's decisions (BINDING, 2026-10-05)
1. WH_Hit_Large_L + WH_Attack_Horiz (bandit): torso/cape mesh collapse at mid-frame
   -> CLAMP Spine/Chest bend via rebake. Keep Mixamo motion otherwise.
2. WH_Death_Zombie: ends standing (agony clip), NOT dead-on-ground -> LEAVE UNWIRED.
   Ghoul keeps the existing rigid-fall death in enemy.js. Keep the baked clip in the
   GLB (harmless), document "unwired by decision" in reports. Do NOT delete it.
3. Doc drift: io/mixamo-clip-selection.md names WH_Hit_Reaction/WH_StandUp but the
   baked clips are WH_Hit_Zombie/WH_StandUp_Zombie -> patch the doc names to match
   reality (clip names in GLB win; do not rename clips).

## Task
1. Read scratch/mixamo_retarget.py (stabilized by your predecessor run) and
   scratch/mixamo-fbx/reports/{bandit,ghoul}-verification.json + bandit-bake.json.
2. Add a clamp post-process to the bake flow: after baking WH_Hit_Large_L and
   WH_Attack_Horiz for the bandit, clamp the Spine (and Spine1/Chest if needed)
   world-bend so no single frame exceeds the deformation the mesh tolerates.
   Testerbot measured: Spine max bend 47deg (Hit_Large_L) and 31deg (Attack_Horiz)
   collapses the cape/pauldron region. Try clamps from ~25deg downward until the
   two QA renders show no slab-collapse: pick the LARGEST bend clamp that renders
   clean (preserve as much motion as possible). Clamp in world/local-bend terms on
   the rotation FCurves of those 3 bones only; do not touch other bones or clips.
   NOTE: re-baking just those 2 clips into the EXISTING .mixamo.glb must preserve
   the bin-prefix + append-only-JSON invariant. If in-place replacement of 2 clip
   ranges breaks the invariant validator, acceptable alternative: re-run the full
   7-clip bandit bake with the clamp applied (the pipeline is proven and fast).
3. Re-run scratch/verify_retarget.py + regression tests (test_mixamo_retarget.py).
   Update scratch/mixamo-fbx/reports/bandit-verification.json so the pose entries
   for these 2 clips reflect the clamped rebake (pass criteria: no mesh collapse,
   not "bend unchanged").
4. QA renders: new WH_Hit_Large_L.png + WH_Attack_Horiz.png (+ _end variants) in
   scratch/mixamo-fbx/qa/bandit/ overwriting stale ones. Vision-analyze both and
   record the verdicts in the report.
5. Patch io/mixamo-clip-selection.md: WH_Hit_Reaction -> WH_Hit_Zombie,
   WH_StandUp -> WH_StandUp_Zombie; add line: WH_Death_Zombie unwired by Nicko
   decision 2026-10-05 (agony clip ends standing; ghoul keeps rigid-fall death).
6. Update scratch/mixamo-retarget-report.md: correct the two pose-review entries,
   add the clamp parameters used, add Death_Zombie decision note.
7. Commit (feat/anim prefix, CaptainPickard identity) + push to origin dev via
   HTTPS credential store. Commit EARLY. Do NOT touch prototype/ or .rigged.glb
   originals. Do NOT remove or rewire anything in enemy.js/assets.js (wiring is a
   later round, not this brief).

## Known gotchas (from the landed round - do not rediscover)
- nla.bake pushes strips onto the FIRST NLA track: clobbers WH_Walk/WH_Run. Use the
  proven pattern already in scratch/mixamo_retarget.py (per-clip RT_ tracks +
  action_slot assignment). Blender 4.5.4 at /opt/blender-4.5.4-linux-x64/blender.
- glTF import: bone_heuristic='BLENDER'.
- Exporter throws on hand-made NLA strips without action_slot (target_id_type None).
- FBX import prints "FBX version: 7700" noise: harmless.
- verify scripts may REWRITE reports they load (test-timing strings) - restore with
  git checkout if a verifier run dirties a tracked report (Testerbot hit this).
- Renders need libegl1 (installed) and BLENDER_WORKBENCH; purge default Cube/
  Icosphere before rendering; camera ~4.6m back, 35mm lens frames the ~2m character.

## Definition of done
- Both bandit clips clamped + rebaked, invariant validator green, regression tests
  green, new QA renders clean per vision check, docs/reports corrected, committed
  and pushed to origin/dev with the verification JSONs updated.
- Report back: clamp angle used per clip, before/after max Spine bend, render QA
  verdicts, commit SHAs, push confirmation, absolute paths of every changed file.