# ASTRABOT MISSION BRIEF: Mixamo->WH retarget bake (3 GLBs)
Issued: 2026-10-05 by IO. NO CHAT CONTEXT PROVIDED - this brief is the complete contract.

## Mission
Headless-Blender retarget Nicko's uploaded Mixamo FBX packs onto the Witch Hunter
20-bone rigs and export 3 new GLBs:
  1. bandit: orc-male-warrior.rigged.glb + Pro Melee Axe pack clips
  2. ghoul: undead-ghoul-male.rigged.glb + Not So Scary Zombie pack clips (+ Zombie_Attack.fbx)
  3. player (OPTIONAL phase, only if time; Marko confirms clips separately):
     human-hunter-male.combat-chain.glb + Pro Sword and Shield pack clips
Output naming: <original-stem>.mixamo.glb NEXT TO the original in
art-direction/3d/assets/races_regen/rigged/. DO NOT overwrite originals.
DO NOT modify prototype/ JS or assets.js - wiring is a later brief.

## Inputs (all verified present)
- Blender 4.5.4: /opt/blender-4.5.4-linux-x64/blender (invoke --background --factory-startup)
- Staged FBX per pack: /workspace/witch-hunter/scratch/mixamo-fbx/{axepack=47,
  swordpack=51, zombienotscary=24, singles=1(Zombie_Attack.fbx)}
- Clip selection + counts per body: io/mixamo-clip-selection.md (READ IT FIRST)
- Proven verification scripts: scratch/verify_retarget.py (GLB clip/shape/identity),
  scratch/rt_render_qa.py (Workbench pose render; needs Xvfb+libEGL1 already installed)
- Working retarget base script: scratch/mixamo_retarget.py (constraint+bake route)

## Verified facts (trust these, do not re-derive)
- WH rig: 20 bones, names exactly: Root,Spine,Chest,Neck,Head,L_Shoulder,R_Shoulder,
  L_UpperArm,R_UpperArm,L_Forearm,R_Forearm,L_Hand,R_Hand,L_Thigh,R_Thigh,L_Shin,
  R_Shin,L_Foot,R_Foot. GLB clips: WH_Idle,WH_Walk,WH_Run,WH_Attack1,WH_Hit,WH_Death
  (+ WH_SlashL2R/SlashR2L/Thrust on player combat-chain GLB only).
- House channel shape: EVERY clip = 60 channels = all 20 bones x {translation,
  rotation,scale}, dense ~30fps keys, translation+rotation BOTH (even leaf bones).
- Mixamo FBX: FBX 7.7 (7700), 65-bone mixamorig: prefix, 30fps per file already.
- Bone map (WH <- mixamorig): Root<-Hips(loc+rot), Spine<-Spine1, Chest<-Spine2,
  Neck<-Neck, Head<-Head, L_Shoulder<-LeftShoulder, R_Shoulder<-RightShoulder,
  L_UpperArm<-LeftArm, R_UpperArm<-RightArm, L_Forearm<-LeftForeArm,
  R_Forearm<-RightForeArm, L_Hand<-LeftHand, R_Hand<-RightHand, L_Thigh<-LeftUpLeg,
  R_Thigh<-RightUpLeg, L_Shin<-LeftLeg, R_Shin<-RightLeg, L_Foot<-LeftFoot,
  R_Foot<-RightFoot. Drop fingers/toes/ends.
- Direct quaternion copy is WRONG (rest-orientation differences). Use COPY_ROTATION
  (target_space=POSE, owner_space=POSE on BOTH rigs) + COPY_LOCATION on Root only,
  then bake VISUALLY so the constraint RESULT is keyed into matrix_basis.
  NOTE: pb.matrix_basis is NOT constraint output - key the evaluated pose matrix
  result (nla.bake visual_keying=True does this), never raw basis values.

## GOTCHAS hit in live probes (avoid or solve)
1. bpy.ops.nla.bake(..., bakematerials=...) kwarg DOES NOT EXIST in 4.5.4 -> TypeError.
2. nla.bake(use_current_action=False) pushes the strip onto the FIRST NLA track ->
   after several clips the original WH_Walk/WH_Run strips get displaced and the
   glTF exporter then DROPS them (proved: export lost WH_Walk).
3. nla.bake(use_current_action=True) into an empty hand-made action bakes
   ZERO fcurves (proved twice). Only bakes reliably into actions it creates itself.
4. Hand-built NLA strips REQUIRE strip.action_slot assignment or the 4.5 exporter
   dies: AttributeError NoneType target_id_type in io_scene_gltf2 (proved).
5. glTF export flags that WORK (from scratch/blender_chain_clips.py):
   export_animation_mode="ACTIONS", export_skins=True, export_def_bones=False,
   export_apply=False, export_yup=True, export_force_sampling=False,
   export_optimize_animation_size=False, export_anim_slide_to_zero=True,
   export_reset_pose_bones=True. Actions need use_fake_user=True.
6. Original clips live ONLY as NLA strips on the target armature (no fake users):
   your pipeline MUST keep every original strip + its action intact.
7. Workbench render needs libEGL1 (installed) + Xvfb :99 for --background GPU-less ok:
   purge factory Cube/Icosphere junk, camera at ~(1.2,-4.6,1.05) rot (1.32,0,0.25)
   lens 35 to frame a ~1.95m character.

## PROVEN working pattern for clip #1 (single clip, WH_Idle_Melee):
import target GLB -> stash existing actions with use_fake_user -> import FBX ->
assign action -> constraints per map (COPY_ROTATION all, COPY_LOCATION Root,
target/owner spaces POSE) -> empty new action w/ slot + action_slot assigned ->
nla.bake(frame_start=0, frame_end=ceil(range), only_selected=False,
visual_keying=True, clear_constraints=True, use_current_action=False) ->
RECOVER baked action from bpy.data.actions[-1], name it, fake_user, strip-attach
WITH action_slot -> cleanup source FBX objects/actions/meshes/materials via
users==0 sweep -> next clip. FIRST clip in isolation bakes 200 fcurves and
verifies byte-identity-preserving on export (proved: prove_one.glb 4.80MB,
old clips shape-identical, WH_Walk survived because only ONE bake ran).
THE UNSOLVED PROBLEM: clip 2+ bakes come back 0 fcurves with
use_current_action=False (acted on stripped/cleared state?) - investigate:
prime suspects = (a) leftover target.animation_data.action from previous loop,
(b) t_act placeholder accumulating, (c) constraint objects not fully cleared by
clear_constraints=False path, (d) need scene frame range reset per clip (fbx
import overrides scene.frame_start/end!). HINT fyi: the probes set scene.frame
AFTER import each time; verify bake's actual frame_end. Use the debug-instrumented
script at /tmp/rt_probe3.py (reads ACTS/NLA per loop) as your starting point.

## Alternative route if bake route cannot be stabilized
Manual keyframe insertion works syntactically (proved: 133 fcurves) but MUST key
the CONSTRAINT RESULT, not matrix_basis. Compute per bone per frame:
  final = arm.matrix_world.inverted() @ pb.matrix   (armature space result)
Then express as local delta vs rest: convert armature-space result to bone-local
(rotation: (rest_in_arm_rot).inverted() @ final_rot; location: rest-space
translation of result - rest translation) and write fcurves with
keyframe_points.insert(frame, value) (SCALAR args, not tuple - proved).
Deterministic, no operators, but you own the math - verify with render QA.

## Acceptance criteria (ALL required)
A. 2 GLBs exported: orc-male-warrior.mixamo.glb, undead-ghoul-male.mixamo.glb
B. Each contains ALL 6 original clips byte-shape-identical (verify_retarget.py:
   shape old=new, channel paths preserved, source-data identity TRUE for the 6)
C. Each contains the selected new clips (io/mixamo-clip-selection.md sets):
   bandit: WH_Idle_Melee, WH_Walk_Melee, WH_Run_Melee, WH_Attack_High,
   WH_Attack_Horiz, WH_Hit_Large_L, WH_Taunt (7)
   ghoul: WH_Idle_Zombie, WH_Walk_Zombie, WH_Run_Zombie, WH_Attack_Zombie,
   WH_Hit_Zombie, WH_Death_Zombie, WH_StandUp_Zombie (7 incl Zombie_Attack.fbx)
   Exact FBX paths in io/mixamo-clip-selection.md - follow them, rename ONLY
   clip names listed there.
D. Every NEW clip: 60 channels (20 bones x T/R/S), >= 60 fcurves... (equal to
   channel shape), dense keys across full range.
E. Pose render QA passes: render 2 frames per new clip (mid + end) with
   rt_render_qa.py pattern; limbs natural, no T-pose/twist/ground-penetration.
   Save PNGs under scratch/mixamo-fbx/qa/<body>/<clip>.png and review each via
   your own judgment (you have vision? if not, attach paths in report).
F. Deliverables land as git COMMITS on dev (branch may be created
   feat/mixamo-retarget-bakes from current dev HEAD 30c815c): scripts + GLBs +
   verification JSON (per-clip channel counts, fcurve counts, identity booleans).
   COMMIT EARLY AND OFTEN (dispatch law; worktree = truth).
G. Final report: absolute paths of GLBs, verification JSON dump, render PNG list,
   plus any clip that FAILED bake and why (do not silently skip clips).

## Discipline
- ZERO re-research of Mixamo license/API - assets are already staged on disk.
- Do not modify anything under prototype/. Do not touch canonical .rigged.glb files.
- Do not push to origin? PUSH IS ALLOWED to origin/dev via existing HTTPS creds
  (witch-hunter deploy key is read-only; use credential-store HTTPS route as IO does).
- If a route definitively fails after 2 solid attempts, STOP and report; do not
  thrash. Partial result with verification > late perfection.