# Mixamo Clip Selection — per body (Nicko packs, staged 2026-10-05)

Raw FBX staged under scratch/mixamo-fbx/{axepack,swordpack,zombienotscary,singles}/.
All FBX 7.7, 65-bone mixamorig rigs, 30fps. WH rig 20 bones, mapping verified 1:1.

## Bandit — orc-male-warrior.rigged.glb (Pro Melee Axe Pack)
Clip-naming pattern: WH_<Name>. Curated 14:
- WH_Idle_Melee     <- standing idle.fbx                      (melee stance idle)
- WH_Walk_Melee     <- standing walk forward.fbx
- WH_Run_Melee      <- standing run forward.fbx
- WH_WalkBack_Melee <- standing walk back.fbx
- WH_Attack_High    <- standing melee attack 360 high.fbx
- WH_Attack_Low     <- standing melee attack 360 low.fbx
- WH_Attack_Horiz   <- standing melee attack horizontal.fbx
- WH_Attack_Down    <- standing melee attack downward.fbx
- WH_Attack_Back    <- standing melee attack backhand.fbx
- WH_Combo1         <- standing melee combo attack ver. 1.fbx
- WH_Combo2         <- standing melee combo attack ver. 2.fbx
- WH_Hit_Large_L    <- standing react large from left.fbx
- WH_Hit_Large_R    <- standing react large from right.fbx
- WH_Hit_Gut        <- standing react large gut.fbx
- WH_Taunt          <- standing taunt battlecry.fbx
RESERVE (phase 2): turns, jumps, disarms, taunt chest thump, unarmed set.

## Ghoul — undead-ghoul-male.rigged.glb (Not So Scary Zombie Pack + Zombie_Attack)
Curated 12:
- WH_Idle_Zombie    <- zombie idle.fbx
- WH_Idle_Scratch   <- zombie scratch idle.fbx               (idle variety, 2nd idle)
- WH_Idle_Grope     <- zombie idle (2).fbx                   (3rd idle variant)
- WH_Walk_Zombie    <- walking.fbx
- WH_Run_Zombie     <- zombie running.fbx
- WH_Attack_Swipe   <- zombie attack.fbx                     (pack swipe)
- WH_Attack_Over    <- singles/Zombie_Attack.fbx             (overhead two-hand)
- WH_Attack_Punch   <- zombie punching.fbx
- WH_Attack_Kick    <- zombie kicking.fbx
- WH_Attack_Head    <- zombie headbutt.fbx
- WH_Hit_Zombie     <- zombie reaction hit.fbx
- WH_Death_Zombie   <- zombie agonizing.fbx                  (baked agony; unwired)
- WH_StandUp_Zombie <- zombie stand up.fbx                   (recovery/rise)
- WH_Stumble        <- zombie stumbling.fbx
RESERVE: idle (3)(4), punching (2), kicking (2), reaction hit (2), stand up (2)(3),
transitions, turn, walking (2).

WH_Death_Zombie unwired by Nicko decision 2026-10-05 (agony clip ends standing; ghoul keeps rigid-fall death).

## Player — human-hunter-male.combat-chain.glb (Pro Sword and Shield Pack)
Curated (APPEND ONLY; existing 9 clips byte-locked):
- WH_ShieldIdle    <- sword and shield idle.fbx
- WH_ShieldWalk    <- sword and shield walking.fbx (verify name)
- WH_ShieldRun     <- sword and shield running.fbx (verify name)
- WH_ShieldStrafeL <- sword and shield strafe left.fbx (verify)
- WH_ShieldStrafeR <- sword and shield strafe right.fbx (verify)
- SHIELD BLOCK SET + attack variants -> wired to shield/combat ds1 phases after anim.js
  mapping update. Exact singles list finalized at retarget time from swordpack/ ls.

## Retarget pipeline (probe verified)
1. Import target GLB (WH_Armature, 20 bones).
2. Import Mixamo FBX (65 bones, Armature|mixamo.com|Layer0).
3. Constrain each WH bone:
   Root<-Hips, Spine<-Spine1, Chest<-Spine2, Neck<-Neck, Head<-Head,
   L/R_Shoulder<-Left/RightShoulder, L/R_UpperArm<-Arm, L/R_Forearm<-ForeArm,
   L/R_Hand<-Hand, L/R_Thigh<-UpLeg, L/R_Shin<-Leg, L/R_Foot<-Foot.
   Copy rotation LOCAL space; Hips also copy location (scaled).
4. Bake (visual keying) onto WH bones at 30fps, delete constraints,
   delete Mixamo import entirely (mesh + armature + action).
5. Append action into target GLB (the glb_append_clips.py flow),
   rename to WH_<name>, export GLB, byte-identity proof: existing 9 clips'
   channel counts + track data hashes UNCHANGED vs pre-patch baseline.