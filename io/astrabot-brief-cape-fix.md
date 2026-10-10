# ASTRABOT MISSION BRIEF: Orc cape skin-weight fix (Round B of A->B->C ladder)
Issued: 2026-10-05 by IO. NO CHAT CONTEXT - this brief is the complete contract.
ROUND A (ghoul wiring) MUST LAND AND PASS VALIDATION BEFORE this round starts.
Round C (player sword pack) follows After B. Do not start C.

## Defect (fully diagnosed, do not re-derive)
The orc bandit's cape renders as rigid SLABS fanned from the back at/near REST
pose, and worsens under spine bend (was misdiagnosed first as bend-angle issue).
Affected: ALL 8 bandit clips renders, including Idle (rest). Root cause: cape
skin weights in art-direction/3d/assets/races_regen/rigged/orc-male-warrior.
rigged.glb (the .mixamo.glb inherits the same mesh + weights). Evidence:
- scratch/mixamo-fbx/qa/bandit/WH_Idle_Melee.png (slabs at hip/back at rest)
- scratch/mixamo-fbx/qa/bandit/WH_Hit_Large_L.png + _end.png
- scratch/mixamo-fbx/qa/bandit/WH_Attack_Horiz.png + _end.png
- scratch/mixamo-fbx/reports/bandit-clamp-verification.json (bends now sane)
- Retracted false pass + full story: scratch/mixamo-retarget-report.md
  "Pose review" section + io/mixamo-anim-campaign-plan.md fix-round note.

## Source of truth for mesh bytes
- Canonical ORIGINAL (do not modify in place, but it is the visual reference):
  art-direction/3d/assets/races_regen/rigged/orc-male-warrior.rigged.glb
- Deliverable GLB that must be fixed END-STAGE:
  art-direction/3d/assets/races_regen/rigged/orc-male-warrior.mixamo.glb
- The cape/cloth geometry is part of WH_Body skinned mesh. Weight data lives in
  the skin joint weights (Joints accessor) + joints lists. Approach: headless
  Blender import of the .mixamo.glb, find cape vertices (by material/geometry
  group/mesh island - identify by inspection: the fanning cloth geometry on the
  back), re-weight them to sensible spine/chest influence (dominant Spine1/
  Chest with small Spine blend, NO weight on arms/head; keep 1.0 total), do NOT
  touch the rest of the mesh, export preserving the glb structure that
  scratch/glb_append_clips.py expects (this pipeline re-appends animation from
  the untouched original - bone rest compatibility already handled there).
- Alternative acceptable fix if vertex re-weighting proves too risky: REMOVE
  cape vertices from the skinned mesh (delete the cloth geometry island), keep
  the armor torso intact, and record that the orc now has no cape. Choose ONLY
  if re-weight after 2 solid attempts still renders slabbed. A cape-missing orc
  is acceptable; a slabbed cape is not (Nicko preference: playable > pretty).

## Constraints (hard)
- Byte-invariant protection: the .mixamo.glb's EXISTING 6 original clips must
  remain BIN-prefix + append-only-JSON identical relative to the original
  .rigged.glb (verifier scratch/verify_retarget.py must stay green after the
  final rebuild). Vertex weights are MESH data, NOT animation data - fixing
  weights does not conflict with the invariant if you rebuild via the proven
  pipeline: fix weights in Blender export of a MESH-ONLY glb, then re-run
  scratch/mixamo_retarget.py with the fixed mesh glb as the base (it appends
  clips by name exactly like the round did).
- Do not modify: prototype/ JS (wiring was Round A's job), bandit clip JSON
  mappings (scratch/mixamo_bandit.json stays as landed), assets/enemy wiring,
  the canonical .rigged.glb files, ghoul files.
- Keep the 25deg Spine/Chest clamp behavior from b599cc1 in the retarget script
  (it stays; verify it applies).
- renders/QA loop is mandatory: after final rebuild, re-render ALL 16 bandit QA
  frames (8 clips x mid+end) into scratch/mixamo-fbx/qa/bandit/ and
  vision_analyze EACH before declaring done (contact-sheet thumbnails HID this
  defect twice - full-size renders only, one vision call per frame minimum).
- PASS criterion ( Testerbot will audit same): no cape slab geometry in ANY
  frame; cape (if kept)deforms smoothly with torso; rest pose clean.

## Gate discipline
Commit EARLY/OFTEN (feat:/fix: prefix). Push only with green verifier + green
renders. Update io/mixamo-anim-campaign-plan.md Round B section at the end.

## Report back
Weight-fix approach taken (reweight vs removal), vertices changed count,
render QA verdicts per frame (16), verifier results, commit SHAs, push
confirmation, absolute paths. If you chose cape removal, add a note for the
next art pass.