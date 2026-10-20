# CC-C10 · Wolves walk rear-first fix; lair is in the den (by design); legs watch item

## 1. RULING (Nicko, 2026-10-20)
"the wolves walk backwards, leading with their rear end moving forward first.
Also, the legs of the wolves don't move." Plus: "there is no rot mother lair".

## 2. EVIDENCE (IO, offline probes on the shipped GLB + real loader)
- wolf.rigged.pixelated.glb (1a4e13c): 6 WH_Wolf_* clips, all with real leg
  actuation (Walk FL 42-52 deg; Run 70-84; Idle intentionally flat); skin +
  SkeletonUtils clone healthy (mesh verts move 5.09 m/cycle in three.js with
  skeleton.update); no root-motion, no baked yaw in the walk keys.
- FACING: bone space head world z = +0.65; visible bind mesh ear/skull
  vertex cluster z mean = +0.68 in BOTH raw and pixelated bakes -> the rig
  faces +Z. CONFIG wolf row said "the rig's nose points model -Z" and baked
  bodyYawDeg: 180 (region-manager applies it at build). Authored assumption
  is wrong for the shipped bake -> the 180 doubles the correction -> rear
  leads. FIX: remove bodyYawDeg from the wolf row (region-manager: no row =
  no override); correct the comment.
- LEGS: cannot reproduce frozen legs on any game-faithful path offline.
  Watch item: after the yaw fix, if legs still freeze in play, instrument
  the live served page (CDP) next round. Primary suspect if it persists:
  an in-session wolfBody stand-in/late-swap corner (asset.js lateSwap notes
  rigged bodies get the mesh, not the clips).
- LAIR: CC-C8 (eae8cbe, Nicko-approved trim) re-homed the rot mother from
  the Region C glade into the DEN behind the boulder-outcrop doorway NE of
  the glade (E-to-enter, 0.8 s dip, always-dark, lair den-local (0,+6),
  save key unchanged). Testerbot PASS a-h+T2. Not a defect.

## 3. CHANGE
- CONFIG.js wolf row: delete bodyYawDeg: 180; rewrite the body comment
  (nose points +Z in the shipped bake; C5's -Z read was wrong).
- No other files. banditFire/campfire work ships separately (CC-C9 c83d616).

## 4. ACCEPTANCE
- A1: wolf row has no bodyYawDeg; comment states +Z facing.
- A2: node --check clean; bundle rebuilt and contains the change.
- A3: served on 8787 (worktree commit) + 8793 (flip) - marker grep + md5.
- A4: NO harness, NO headless smoke runs - Nicko's playtests are the test
  for both the facing and the legs verdict.

## 5. SCOPE CONTRACT
TOUCH: prototype/js/CONFIG.js (wolf row + comment), prototype/builds/
v8-playable.html (rebuild), this brief. Nothing else.