# ASTRABOT MISSION BRIEF - Chain-attack animation clips (Blender headless)
2026-10-04, from IO (Nicko change order: pose variety for the chain attacks;
"Blender should still be installed locally" - it is NOW: /opt/blender-4.5.4-linux-x64/)

You are Astrabot, running as a Claude Code print-mode run (Opus) inside the
Witch Hunter worktree /tmp/wh-worldfeat on branch feat/world-visuals.
Read this whole brief, confirm in one line you read it, then work autonomously.

## Mission

The longsword 3-chain (slashR2L -> slashL2R -> thrust, landed last order) plays
on ONE shared WH_Attack1 clip: every swing looks the same. Author THREE distinct
animation clips for the player skeleton and wire them per chain move.

## Ground truth (pre-measured, do not renormalize)

- Player rig: art-direction/3d/assets/races_regen/rigged/human-hunter-male.rigged.glb
  - 20 bones: Root, Hips, Spine, Chest, Neck, Head, L_Shoulder, L_UpperArm,
    L_Forearm, L_Hand, R_Shoulder, R_UpperArm, R_Forearm, R_Hand, L_Thigh,
    L_Shin, L_Foot, R_Thigh, R_Shin, R_Foot. Mesh node WH_Body.
  - Existing clips: WH_Attack1, WH_Death, WH_Hit, WH_Idle, WH_Run, WH_Walk.
- anim.js maps state -> clip (find the attack mapping; the syncPlayer flow
  samples game FSM -> mixer). CONFIG.animations may hold names - check.
- moveset CONFIG chain rows carry pose: 'm2'/'m1'/'m4' (fallback pivot-pose
  keyframes used when the rigged body has no per-move clip).
- IMPORTANT mount note: attacks face this.yaw; the sword sits in R_Hand via
  weaponMount. Any clip you author must keep R_Hand posed so an attached
  weapon reads correctly (weapon tip along the swing arc, not floating away).

## Work order

1. Copy the rigged GLB to human-hunter-male.combat-chain.glb (work on the copy;
   the original file must remain byte-identical - verify with sha256sum before
   and after all Blender work).
2. Headless Blender (NO display, use --background --python) via a script you
   write to scratch/blender_chain_clips.py:
   - Import the copy (Blender 4.5 glTF importer).
   - Author three actions, 24fps baked, each ~0.62-0.70s total:
     a) WH_SlashR2L - right-to-left horizontal swipe: windup R arm raised
        back-right (sword trail up/right), strike sweeps across to the left
        with torso twist (Spine/Chest y-rotation), recover settles.
     b) WH_SlashL2R - left-to-right swipe: windup low-left, strike rises
        diagonally to the right, recover settles. Must read clearly DIFFERENT
        from WH_Attack1 and from WH_SlashR2L.
     c) WH_Thrust - lunge thrust: windup pulls sword back at hip (elbow bent),
        strike extends R arm forward (+ lunge step with R leg), recover pulls
        back to guard. Fast strike window (matches strike: 0.14 in CONFIG).
   - Key the 10 upper-body bones at minimum (Hips/Spine/Chest/both Shoulders/
     UpperArms/Forearms/Hands), plus one forward weight-shift on the legs for
     the thrust. Keep Root at origin (no root motion - the game drives
     position; lunge is a game-side mechanic).
   - Each action: 3-phase pose keys (windup/strike/recover) with ease-in-out
     interpolation between keyframes, matching the CONFIG stage proportions
     (0.14/0.20/0.30 for slashes, 0.16/0.14/0.40 for thrust -> scale your
     0.62-0.70s clip accordingly; strike should occupy ~30% of slashes, ~22%
     of thrust).
   - Push each action as an NLA track, all three stashed in the same armature.
3. Export the copy back to GLB (Blender glTF exporter, animations included).
4. Round-trip verify with plain python (struct/json parse of the GLB, see
   scratch/rig_probe-style code): animations list must contain the 3 new names
   PLUS the original 6 (WH_Attack1, WH_Death, WH_Hit, WH_Idle, WH_Run,
   WH_Walk) - the game still needs all of them. Bone count must stay 20.
   Report sampled positions of R_Hand at first/last keyframe of each new
   action in your report (sanity: thrust extends forward, slashes sweep wide).
5. Wire it in (game code, minimal diff):
   - assets.js manifest: move the playerBody entry to the NEW glb (keep the
     old path in a comment for one-line rollback). The atlas postload (R4)
     must still find it - the copy keeps the same texture references, verify
     BODY_PNG still matches (it keys by logical name, path-independent).
   - anim.js: map the chain moves to clips - slashR2L: WH_SlashR2L,
     slashL2R: WH_SlashL2R, thrust: WH_Thrust; other states unchanged
     (WH_Attack1 stays for the handaxe + any unmapped attack).
   - CONFIG: no new knobs needed beyond what exists (clip names may live in
     anim.js mapping table or CONFIG.animations if that pattern exists -
     follow the file's existing convention).
6. Static verification: esprima parse every touched js file (python esprima
   is installed). NO BROWSER RUNS of any kind - no chromium, no puppeteer,
   no headless smoke test. Nicko's playtest is the only acceptance.

## Hard laws

- Do NOT modify: the original rigged GLB (byte-verified), CONFIG.assets
  weaponMount numbers, or any enemy/combat logic outside the anim mapping.
- Never echo or write anywhere: MESHY_KEY if present in env (not needed here).
- Commit incrementally to feat/world-visuals and push after each landed step:
  (a) blender script + raw copy step, (b) authored clips + evidence,
  (c) game wiring. The worktree is truth: uncommitted work does not exist.
- Provenance: scratch/blender_chain_clips.py committed (it IS the asset source
  of truth), QA evidence (sampled R_Hand keys per clip) ->
  scratch/astrabot-chain-clips-report.md. Report: commits + shas, per-clip
  key summaries, round-trip animation/bone counts, wiring diff summary.
- Blender availability check: if /opt/blender-4.5.4-linux-x64/blender --version
  fails at start, STOP after diagnosing and report - do not substitute a
  different animation approach without IO approval (write findings to
  scratch and stop).