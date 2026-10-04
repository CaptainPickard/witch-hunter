# Mixamo Animation Integration Campaign (Nicko order, 2026-10-04/05)

Source: https://www.mixamo.com/#/ — Nicko provides login; MFA code to his email.
Goal: replace our one-gait-fits-all authored clips with Mixamo's free library
(retargeted onto the shared 20-bone rig), priority = walk/run/idle variety,
then any other gaps found in the sweep.

## Nicko's pack assignments (2026-10-05, BINDING)
- Bandit (orc-male-warrior.rigged.glb, enemy.js 'bandit' type): Pro Melee Axe Pack
- Undead (undead-ghoul-male.rigged.glb, enemy.js 'ghoul' type): Not So Scary Zombie
  Pack (24 anims, Nicko-uploaded 10-05; supersedes Scary Zombie Pack which was
  bot-blocked) + Zombie_Attack.fbx single
- Player (human-hunter-male.combat-chain.glb): Pro Sword And Shield Pack (51, uploaded)
  + locomotion/idle/death singles — NOT YET ASSIGNED; wiring brief later

## Status 2026-10-05 (after Nicko hand-delivered the packs)
- All 123 FBX staged: scratch/mixamo-fbx/{axepack 47, swordpack 51, zombienotscary 24, singles 1}
- FBX inventory: FBX 7.7 (7700), 65-bone mixamorig rigs, 30fps. Bone map proven 1:1
  onto WH 20-bone rig (fingers/toes dropped, Spine1->Spine, Spine2->Chest).
- SINGLE-CLIP PROOF PASSED on bandit: constraint+bake retarget of standing idle
  (WH_Idle_Melee, 200 fcurves), old 6 clips byte-shape-identical + WH_Walk intact on
  single bake, pose render QA PASS (natural orc idle, no twist).
- Multi-clip loop bug hit (clips 2+ bake 0 fcurves; nla.bake strip-push clobbers
  original tracks; hand-strips need action_slot). Full diagnosis + hints in
  io/astrabot-brief-mixamo-retarget.md.
- ASTRABOT DISPATCHED (deleg_8b6720d5, prof astrabot) to stabilize the loop, bake
  bandit+ghoul (7 clips each), verify, QA-render, commit dev, report.
- ASTrabot LANDED (30m cap hit at the summary step; worktree truth verified): 4
  commits on dev e20d68d/1fa07f2/41935dc/7cbca33, both .mixamo.glb baked (7 clips
  each, 13/body total), pushed. verify reports pass:true both bodies; strongest
  invariant proof = BIN-chunk prefix byte-identical + append-only JSON.
- TESTERBOT (opus-5.5 via claude-code, independent) VERDICT: PARTIAL.
  A/B/D/F/G PASS with independent GLB parser re-derivation. E PARTIAL:
  WH_Hit_Large_L + WH_Attack_Horiz bandit mid-frames show torso/cape mesh collapse
  (Spine bends 47/31deg; skin weights, not keys). Also: WH_Death_Zombie (agony
  source) ends standing not dead; clip-name doc drift (WH_Hit_Reaction ->
  WH_Hit_Zombie, WH_StandUp -> WH_StandUp_Zombie); my 'full-file sha identity'
  wording wrong -> use BIN-prefix + append-only JSON. Nicko decisions 10-05:
  CLAMP-REBAKE the 2 bandit clips; zombie death LEAVE UNWIRED (rigid-fall stays).
- FIX ROUND LANDED (partially; 429 truncated it): 9d09af3 doc fixes + b599cc1
  clamp commit (25deg Spine/Chest, scope verified: 4 channels changed, 776
  identical). TESTERBOT E RE-AUDIT: FAIL (correctly).
  ESCALATION: cape slabs appear in IDLE too => orc cape skin-weight defect at
  rest pose affects ALL 8 bandit clips; clamps cannot fix. b599cc1's commit msg
  (Attack_Horiz "fixed") falsified; report retracted+corrected in c2ae186.
  STATUS: bandit Mixamo set PARKED from wiring; ghoul set READY.
- NEXT OPTIONS (Nicko decides): (a) ghoul wiring brief now (ghoul set is clean,
  Testerbotted); (b) orc cape skin-weight fix round (Astrabot, mesh edit + vision
  loop, then re-render 16 frames + re-QA); (c) jump to player sword-pack round.
  After cape fix: re-render, re-run Testerbot E, then wire bandit set.

## Current state (verified 2026-10-05, dev 30c815c)

- Canonical body: art-direction/3d/assets/races_regen/rigged/human-hunter-male.combat-chain.glb
  9 clips: WH_Attack1, WH_Death, WH_Hit, WH_Idle, WH_Run, WH_SlashL2R,
  WH_SlashR2L, WH_Thrust, WH_Walk. 20 bones.
- 11 rigged bodies total; 10 still carry the bare 6 (no chain attacks).
- Consumers: prototype/js/anim.js (CharacterAnim: NAMES map idle/walk/run/
  attack/hit/death + MOVE_NAMES slashR2L/slashL2R/thrust), player.js + enemy.js
  both mount it; enemies without WH_Death take a procedural rigid fall.
- Roll is procedural (player.js rollTimer/rollDir), no WH_Roll clip.
- Runtime contract (binding): NO root motion (gameplay owns translation);
  clips start/end in idle/guard pose; one-shot clips end in hold pose for
  state chains; no resampling at export (preserve Mixamo fps? -> see Risks).

## Mixamo facts (to verify live)

- License: free for commercial use inside games/video; raw FBX files must not
  be redistributed as assets. We store RETARGETED GLB clips inside our repo.
- Mixamo rig: 65-bone standard humanoid, T/A-pose skeleton, root motion
  embedded in "In Place" off variants -> must select In Place checkbox (or
  strip root motion on retarget), then bake to our 20-bone topology.
- Login: Adobe ID + MFA code to Nicko's email (mfa-portal-crawl discipline:
  one continuous session, paste code fast, never resend-spam; session dies
  with the browser process -> plan ALL downloads per session).

## Pipeline (per this repo's proven pattern)

1. SCOUT (logged-in browser session): list candidate Mixamo animations per
   category with names, IDs, URLs. Bring side-by-side preview list to Nicko
   BEFORE any download-heavy work.
2. DOWNLOAD: FBX (skin=none, without-skin so only the animation), In Place.
3. RETARGET (headless Blender 4.5.4, /opt/blender-4.5.4-linux-x64):
   import FBX, constrain/bake Mixamo skeleton -> our 20-bone names
   (exact contract names), verify channel counts = bone count x 3.
4. APPEND to canonical GLB via scratch/glb_append_clips.py pattern with the
   byte-identity proof gate (base BIN sha256 prefix; every pre-existing JSON
   entry unchanged; expected clip total; numpy re-parse array_equal).
5. QA contact sheets per clip into scratch/<feature>-clips-qa/.
6. Runtime: extend anim.js NAMES map (and MOVE_NAMES if any new attack
   variants); no MOVE_NAMES collisions with state clips.
7. IO gate: Testerbot validation spec -> Devbot -> Testerbot PASS -> commit.

## Clip naming contract (new)

- Locomotion variants: WH_Walk_<name>, WH_Run_<name>, WH_Idle_<name> etc.
- CharacterAnim picks a variant per body (e.g. enemy class) or random index;
  never rename existing 9 clips (consumers depend on exact names).

## Per-body variant matrix (from code sweep)

- Player (human-hunter-male): 9 clips + variants (walk variety, sprint, idle).
- Enemies: ghoul + orc-male-warrior (walk/run variety = biggest visual win).
- NPCs: dwarf-male-smith (idle variety), elf-dawn-refuser-male, etc.
- Females (orc-female, vampire-female, human-hunter-female, dwarf-female):
  currently share male-authored gaits; Mixamo adds proper variants.

## Risks / gotchas

- Mixamo MFA session dies with browser process: download ALL candidates in
  the one session or re-login later (space days per mfa-portal-crawl).
- Root motion in FBX must be stripped or "In Place" checked.
- Bone-name mapping: Mixamo mixamorig:* vs our 20-bone names; ONE mapping
  table, verified against the real GLB, reused for every body.
- NO root motion and clean in/out (start/end in idle pose) may need Blender
  trim/cleanup after retarget.
- 30fps Mixamo source -> do not resample; carry source fps.
- License: keep a download log (name, date, category) for attribution
  hygiene; do not commit raw Mixamo FBX (store retargeted GLB only).

## Open items (fill during scout)

- [ ] Candidate list per category (Nicko picks)
- [ ] Bone mapping table verified vs canonical GLB
- [ ] FPS / timeline normalization check
- [ ] Which bodies get which variants
## Round A landed (2026-10-05): ghoul Mixamo wiring

Brief: io/astrabot-brief-ghoul-wire.md. Commits c8f0b44 (wiring), cebf636
(harness + evidence) on dev.

Wiring diffs:
- prototype/js/assets.js: ghoulBody -> races_regen/rigged/
  undead-ghoul-male.mixamo.glb (13 clips). Texture path unchanged. Rollback:
  undead-ghoul-male.rigged.glb.
- prototype/js/anim.js: `CharacterAnim(body, clips, options)`; with
  `options.variant` set, the clip names come from the static
  `CharacterAnim.VARIANTS` table. `zombie` = idle/walk/run/attack/hit ->
  WH_*_Zombie, death = WH_Death (canonical), moves = {} (no chain clips).
  Each instance keeps its own `names`/`moveNames`, and getState reports
  through them. If an override clip is missing from the GLB, that slot
  falls back to the default NAMES clip and logs a warning.
- prototype/js/enemy.js setBody: ghoul -> `{variant: 'zombie'}`, bandit ->
  default map (no change). Player unchanged.
- WH_Death_Zombie stays unwired and WH_StandUp_Zombie stays parked (Nicko's
  decisions). The bandit Mixamo set is still parked (cape defect, Round B).

Evidence: scratch/verify_ghoul_wire.py ->
scratch/ghoul-wire-evidence/ghoul-wire-evidence.json (21/21 PASS) plus
ghoul-{idle,run,attack,hit,death}.png and player-bandit-smoke.png.
Assertions passed: 13 clips; rest/walk/chase/attack/damage play the matching
WH_*_Zombie clip; death plays WH_Death (WH_Death_Zombie never active) and the
corpse settles; dropping WH_Walk_Zombie falls back to WH_Walk with a warning;
bandit uses only the legacy map; player chain clips resolve and an attack
plays WH_SlashR2L; no console errors or pageerrors (only the browser's own
favicon.ico 404).
Harness notes: entry is prototype/index.html via prototype/server.py on a
free port. Headless swiftshader runs at about 1-2 fps (same on the baseline),
so each phase waits until its sampled clip shows up instead of using a fixed
sleep. builds/v7-playable.html was not rebuilt; it was already stale before
this round (it has no combat-chain clips either).
