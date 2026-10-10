# Mixamo Candidate List — Phase 1 (scout sweep 2026-10-05)

Account: io-6075@agentmail.to (login verified, session persisted).
All counts verified live: walk 391, run 365, idle 507, death 46, sword slash 19,
sword attack 29, hit reaction 52, dodge 17 hits.

## PRIMARY: Pro Sword And Shield Pack (51 animations) — bulk download
Covers (verified in grid): Power/Downward/Cross/Crouch/Combo slashes, High/Low/
Jump/Hilt-Melee attacks, Sword And Shield Death (falling forward), plus block/
idle/locomotion with shield. This is the Witch Hunter's exact weapon kit.
Alternatives if needed: Sword And Shield Pack (49), Great Sword Pack (51).

## SINGLES (per-body variety)
LOCOMOTION
- Walking (standard male walk)            -> replaces WH_Walk
- Fast Run                                -> replaces WH_Run; "Injured Run"/
  "Male Injured Walk" for ghoul/zombie bodies
IDLE
- Idle (Standing Idle)                    -> replaces WH_Idle
- Fight Idle To Standing Idle transitions -> combat stance layering later
DEATH (4-directional variety per body)
- Standing React Death Backward (falls backwards)
- Standing React Death Forward
- Standing React Death Left / Right
- Two Handed Sword Death (sword-relevant flavor)
HIT REACTION
- Hit Reaction (unarmed variant)
DODGE (reference for procedural roll polish)
- Dodging Right / Dodging Backward (In Place)

## Download settings (applied to every export)
Format FBX Binary, Skin: Without Skin, Frame Rate: 30, Keyframe Reduction: none,
"In Place" checked where offered (locomotion; attacks keep root motion OFF in
retarget), no T-pose correction needed (retarget onto our 20-bone rig).

## Pipeline reminder
FBX -> Blender 4.5.4 headless retarget onto human-hunter rig -> append to
canonical GLB through the byte-identity proof gate (existing 9 clips UNTOUCHED).
New clip names: WH_WalkMixamo, WH_RunFast, WH_DeathBack, WH_DeathFwd,
WH_DeathL, WH_DeathR, WH_Pack_* (51 from the pack), WH_HitMixamo, WH_DodgeR.