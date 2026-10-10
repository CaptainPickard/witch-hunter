# ASTRABOT MISSION BRIEF: Ghoul Mixamo wiring (Round A of A->B->C ladder)
Issued: 2026-10-05 by IO. NO CHAT CONTEXT - this brief is the complete contract.
Round B (orc cape skin-weight fix) and Round C (player sword-pack) follow AFTER
this round lands + is validated. Do not start them. Do not touch their scope.

## Current state (verified)
Repo /workspace/witch-hunter, branch dev @ c2ae186 (pushed). Git identity
CaptainPickard <pickard.nicko@gmail.com>. Push via HTTPS credential store.
- undead-ghoul-male.mixamo.glb exists (13 clips: 6 originals UNTOUCHED bytes +
  7 new: WH_Idle_Zombie, WH_Walk_Zombie, WH_Run_Zombie, WH_Attack_Zombie,
  WH_Hit_Zombie, WH_Death_Zombie, WH_StandUp_Zombie). Ghoul set validated clean
  by Testerbot (opus). Reports: scratch/mixamo-fbx/reports/ghoul-verification.json.
- Game wiring today:
  - prototype/js/assets.js:53 ghoulBody -> art-direction/3d/assets/races_regen/
    rigged/undead-ghoul-male.rigged.glb (texture path line 65 unchanged)
  - prototype/js/enemy.js:60 bodyName = ghoulBody for type 'ghoul'; line 62
    this.anim = new window.WH_CharacterAnim(meshRoot, getClips(bodyName))
  - prototype/js/anim.js: NAMES = {idle WH_Idle, walk WH_Walk, run WH_Run,
    attack WH_Attack1, hit WH_Hit, death WH_Death} + MOVE_NAMES (chain slashes,
    player-only). CharacterAnim handles missing clips gracefully (warns).
  - WH_Death present in ghoul GLB => animated death; enemy.js rigid-fall is only
    a fallback.
- Nicko BINDING decisions: Death_Zombie UNWIRED (agony clip ends standing, reads
  wounded not dead). StandUp_Zombie parked (no spawn-from-ground mechanic yet).
  Bandit clip set PARKED (cape skin-weight defect) - DO NOT touch bandit path,
  bandit rendering, or bandit anim in this round.

## Round A task: wire the ghoul's new zombie clips
1. assets.js: switch ghoulBody GLB path to undead-ghoul-male.mixamo.glb. Texture
   path (ghoulBody pixelated png) unchanged. CHARACTERS preload dict (line 99)
   already lists ghoulBody - keep.
2. anim.js: CharacterAnim constructor gains an OPTIONAL per-body clip-name map
   (2nd arg options or a static variant table - match codebase ES5 style: var,
   prototype, window globals). ZOMBIE variant map: idle WH_Idle_Zombie, walk
   WH_Walk_Zombie, run WH_Run_Zombie, attack WH_Attack_Zombie, hit WH_Hit_Zombie,
   death WH_Death (death stays canonical clip), NO move clips (MOVE_NAMES empty
   for ghoul). SAFETY: every override name must resolve in the loaded clip list;
   on any missing name fall back to the legacy default map for that slot (and the
   existing warn path), so an unexpected GLB regen can never strand a state.
3. enemy.js: ghoul enemies construct their CharacterAnim with the ZOMBIE map
   (bandit path untouched - default map).
4. player.js path UNTOUCHED (default map, chain moves). HUD/blood/corpse logic in
   enemy.js must keep working (corpse uses a separate mechanism; do not alter).
5. No data.js/enemy stat changes. No new config knobs beyond what the variant map
   needs.

## Validation (headless, no node on box - use the playwright driver pattern)
- JS syntax check: python3 driver launching playwright chromium loads each edited
  JS file via a file:// harness page OR uses node --check through the established
  prototype testing flow used by prior rounds (see tests/ and scratch/ for the
  pattern; tests/ has prior harness profiles).
- Behavioral check: headless load of the game (prototype playtest html), force-
  spawn a ghoul, then assert: clips array length === 13; active actions include
  WH_Idle_Zombie at rest; walking state transitions to WH_Walk_Zombie; running to
  WH_Run_Zombie; forced damage triggers WH_Hit_Zombie; attack fires
  WH_Attack_Zombie; death plays WH_Death (not Death_Zombie). Save evidence JSON +
  a screenshot to scratch/ghoul-wire-evidence/. Keep the game URL/entrypoint the
  one prior harness rounds used.
- Also spawn a bandit and assert it STILL uses legacy clips (WH_Idle etc) -
  confirms no leakage of the zombie map to bandit.
- Player smoke: spawn/load player, assert chain clips still resolve (WH_SlashR2L
  etc present) and no console errors.

## Gate discipline
- Commit EARLY and OFTEN (feat: prefix). Do NOT push mid-round without green
  syntax checks; push is allowed once behavioral evidence is recorded.
- Do NOT modify: bandit wiring, canonical .rigged.glb files, .mixamo.glb files
  (bytes must stay identical), data.js, docs/planning.
- Update io/mixamo-anim-campaign-plan.md at the end: Round A landed section
  (wiring diffs summary + evidence paths).

## Report back
Changed files + per-file summary, evidence JSON absolute path, screenshot paths,
clip length assertions results, test/syntax results, commit SHAs, push
confirmation (git rev-list origin/dev..dev --count === 0), any deviations from
this brief and why.