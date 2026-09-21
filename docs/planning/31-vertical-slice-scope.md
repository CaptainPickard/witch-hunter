# 31 - Vertical Slice Scope and UE 5.8 Engine/Pipeline Plan

Status: PROPOSED (Astrabot hard-numbers pass, 2026-09-13); engine UE 5.8
LOCKED and Rot-Mother boss IN at slice 1 (M4 checkpoint may cut), both by
Nicko, 2026-09-13. Remaining numbers PROPOSED.
Engine: Unreal Engine 5.8 (locked by Nicko, 2026-09-13).

SUPERSEDED NOTE (2026-09-21, Nicko, index entry 94): the UE5 buildout is
SHELVED, not cancelled. The game concept develops in the Three.js browser
prototype (prototype/); engine choice revisited later. This doc's engine
plan remains the reference if UE5 is revived; do not continue the 52-58
spec-set buildout without a new ruling.
Engine: Unreal Engine 5.8 (locked by Nicko, 2026-09-13).

Closes 30-prototype-gap-analysis.md G1 (slice scope) and G2 (engine version
and pipeline completion), and answers 01-vision-high-concept.md's standing
open question "Rough target scope for the first vertical slice". Resolves
the two remaining unvalidated pipeline stages recorded in
29-art-style-bake-off-spike.md (auto-rig + animation timing, UE5 scene
parity) with hour estimates. Every number below is PROPOSED.

## 1. Slice Definition

Slice 1 is a COMBAT-LOOP VERTICAL SLICE. One arena pocket, the player body,
two enemy types in it, one optional boss remix. It proves the feel contract
in 04-combat-system.md ("deliberate, weighty, readable") on the locked UE
5.8 3D carrier of 29-art-style-bake-off-spike.md. It is not a world demo,
not a survival demo, not a quest demo.

### IN (exactly this, nothing more)

- ARENA: one hand-authored Darkwood-edge pocket, 200 x 200 m playable,
  terrain + 1 ruined structure + 20-30 trees + graveyard clutter. Biome
  choice grounds it in 03-world-design.md's signature biome. Night + fog
  law per 24-art-bible.md, one diegetic key (lantern) + moon fill + fog
  density 0.018 (29-art-style-bake-off-spike.md scene-readability PASS).
- PLAYER: one human body (03-world-design.md human-lock), one weapon class
  (Long Blade), one shield. No class presets, no skill ranks simulated
  beyond flat numbers.
- ENEMIES, 2 types + 1 optional:
  1. BANDIT (humanoid): full doc 04 verb grammar, sloppy reads, panic
     rolls. Quantity 4-6 per encounter.
  2. WOLF (beast): no block/parry, leap/sidestep dodge-equivalents, high
     poise (04-combat-system.md). Quantity 2-3 per encounter.
  3. OPTIONAL BOSS REMIX: gravedigger-undead body from the spike, boss
     grammar = bandit verbs at 1.6x scale + one poise-slam. Teaches the
     doc 04 remix rule ("dungeons teach a monster pool; the boss remixes
     it") at minimum cost. Cut without ceremony if schedule slips.
- SYSTEMS IN: the full verb set (light/heavy, roll, block/parry, lock-on,
  sprint), stamina/poise/stagger, parry windows by source, i-frames,
  health-potion drink (no estus, see 32), death/respawn at one tavern
  door in the arena, and the HUD minimum (health, stamina, poise, boss
  bar, target reticle).
- ACCEPTANCE TEST (the prove-or-kill gate): 5 external viewers, 60 fps,
  night conditions. (a) Each viewer names the enemy verb type
  (wind-up/stagger/block) within 250 ms, per 29-art-style-bake-off-spike.md
  criterion 1. (b) A viewer dies twice and reaches the boss without
  instruction. (c) A viewer calls the combat "weighty" unprompted on a
  one-word form. Kill criteria: any (a) failure rate above 20 percent, or
  the frame-data table in 32-controls-frame-data.md needing structural
  (not numeric) revision.

### OUT (explicitly deferred, with owning gap)

- Survival/camping/cooking loops (09-expedition-camping.md,
  10-cooking-meals-drinks.md; G13/G14 territory). One tavern door
  stub only.
- Quests, factions, moral axis, World Ledger (20-22; G25/G26).
- Followers and party AI (23-expedition-followers.md; G20).
- Magic system and spell cast bar (17-magic-system.md; G7 formulas).
- Procedural dungeon interiors (03-world-design.md; G24). Arena is
  hand-authored.
- Equipment mechanics beyond one sword + one shield visual (G6).
- Stealth, mounts, transformation bodies, warp camp building
  (G19, G21, G22, G27).
- Second weapon class, spell wheel, crouch-lock interplay depth.

## 2. Engine and Project Plan (UE 5.8)

- VERSION: Unreal Engine 5.8, locked by Nicko 2026-09-13. This resolves
  the open version item in 00-README-index.md, 08-open-questions.md, and
  30-remote-ue5-pipeline.md ("UE version decision").
- WORKFLOW: the 30-remote-ue5-pipeline.md manual applies unchanged
  (VPS asset prep, GitHub data plane, Remote Control API :30010 control
  plane, renders/ verification plane). 5.8's first-party Unreal MCP is
  audited first before adopting the recommended FFZackFair92 server;
  30-remote-ue5-pipeline.md names this audit as the 5.8+ condition.
- REPO: separate witch-hunter-ue repo, LFS for binaries, per
  30-remote-ue5-pipeline.md open item. Planning docs stay here.
- FOLDER LAYOUT (PROPOSED, under /Game/WH/):
  - /WH/Core (game mode, player controller, camera, input mapping).
  - /WH/Combat (verb state machine, frame data tables as DataTables,
    damage/poise/stamina calculators).
  - /WH/World (arena map WH_Arena_Darkwood, lighting, fog, post-process).
  - /WH/Characters/Player, /WH/Characters/Bandit, /WH/Characters/Wolf,
    /WH/Characters/Boss (meshes, skeletons, anim monitors, sockets).
  - /WH/Art/Materials (pixel register material function),
    /WH/Art/PostProcess (low-res render, point sample, ordered dither,
    grain, per 29-art-style-bake-off-spike.md register stack).
  - /WH/UI (HUD minimum), /WH/Data (Tables: FrameData, StaminaCosts,
    PoiseValues, DamageTable).
  - /WH/Audio (reserved, G16; empty is acceptable for slice 1).

### Ability system: GAS vs custom (PROPOSED)

Slice 1 uses a CUSTOM lightweight verb/action state machine: one C++
UCombatComponent owning an action stack (startup/active/recovery states),
reading frame data from DataTables. Rationale: the slice needs exact
frame-data iteration (32-controls-frame-data.md), hit-stop, and i-frame
windows; a custom stack is 2-3 days of work and iterates in seconds.
GAS is deliberately deferred. Adoption gate at slice exit: adopt GAS when
the first technique menu (04-combat-system.md, 108 locked techniques)
needs gameplay-tag-driven effects, predicted input, or replicated
abilities. Estimate: GAS migration 5-8 days; recorded so the cost is
known before the techniques pass.

### Animation pipeline (resolves doc 29 remaining stages)

The proven stages (image-to-3D, re-texture, equipment slots) are PASS in
29-art-style-bake-off-spike.md with timed numbers. The two remaining
stages, now estimated (all PROPOSED, first run must time them against
these):

- AUTO-RIG + SKELETON QC: Meshy auto-rig ~5 min machine time per body,
  plus 2-3 h manual QC per body (joint placement, root motion, socket
  check against 29's anchor rule, sub-mesh split per KNOWN ISSUES 1).
- RETOPOLOGY FOR HERO CLOSEUPS: 4-8 h per hero body (player + boss
  only; enemies ship spike-mesh at gameplay distance per KNOWN ISSUES 2).
- CLIP AUTHORING: UE 5.8 Control Rig + sequencer for loops, or Blender
  export for attacks. Estimates per clip: idle/walk loops 0.5-1.0 h,
  combat-quality attack/hit clips 1.5-2.0 h. First body (player, 26
  clips in 32-controls-frame-data.md) = 35-45 h including rig learning
  curve; later bodies on a proven rig = 15-20 h (4-8 clips each).
- UE5 SCENE PARITY: closed by the spike scene being rebuilt in-engine
  (milestone M2 below). The Three.js demos are representative only,
  per 29-art-style-bake-off-spike.md.
- SKILL OWNERSHIP (doc 29 criterion 4): rigging/retopology owned by
  Devbot with Nicko as art QA; retop overflow is a named-hire decision
  if any hero body exceeds 12 h. PROPOSED for Nicko's confirmation.

### Performance budget (G23 first pass, PROPOSED)

- TARGET: 60 fps locked at 1080p output, 720p internal point-sampled
  upscale per 02-art-style.md scaling law, on a GTX 1660 / Steam Deck
  class GPU. 30 fps hard floor.
- CPU: 2 ms game thread for combat logic, 4 ms total game+render thread
  budget headroom.
- GPU: full post chain (low-res + dither + grain + fog) under 2.5 ms;
  total GPU under 14 ms.
- SCENE: under 1,500 draw calls, under 2 M triangles, under 20 skinned
  meshes visible (1 player + 6 enemies + boss worst case = 8; headroom
  for foliage).
- VFX: doc 04's hit-feedback rule (hit-stop, contact flash, camera
  shake) costs zero particle budget for slice 1; light-tint materials
  per 02-art-style.md pillar 3 only.
- TEST: a scripted 8-enemy orbit fight in the arena at night fog;
  pass bar is 60 fps with 0 hitches above 33 ms over 5 minutes.

## 3. Milestones to Playable Loop (PROPOSED, hour estimates)

- M0, PC PIPELINE LIVE (4-6 h): 30-remote-ue5-pipeline.md Phase 0-1 on
  UE 5.8. The one curl over Tailscale is the gate.
- M1, REGISTER IN-ENGINE (6-10 h): Phase 2. Pixel material function,
  post-process stack, mood-lighting blueprint, gravedigger import.
  Vision QA vs concept frames.
- M2, GREYBOX ARENA + CONTROLLER (20-30 h): terrain + blockout, player
  pawn with the custom combat component, camera registers wired,
  input map loaded from 32-controls-frame-data.md.
- M3, FRAME DATA FEEL PASS (20-30 h): full player clip set authored
  (35-45 h overlaps here), frame table live in DataTables, hit-stop
  and i-frames functional. Iteration-only milestone.
- M4, ENEMIES (25-35 h): bandit + wolf bodies through the pipeline
  (15-20 h each with 4-8 clips), AI = approach/attack/roll state
  machine on the player grammar, telegraph accent frames per doc 04
  bake-in. Rot-Mother boss IN at slice 1 (locked by Nicko,
  2026-09-13); the M4 checkpoint can still cut it for scope, decided
  at the checkpoint by Nicko.
- M5, LOOP CLOSE (10-15 h): death, tavern respawn, potion drink, boss
  remix, HUD minimum.
- M6, ACCEPTANCE RUN (5-10 h): perf test, 5-viewer acceptance test,
  findings back into 32-controls-frame-data.md as revision proposals.
- TOTAL: roughly 90-125 h of agent/human time to a playable slice,
  excluding concept-art work already done.

## 4. Open Items

- Rot-Mother boss IN at slice 1, locked by Nicko, 2026-09-13; the M4
  checkpoint can still cut it for scope (decision at M4 by Nicko).
  RECONFIRMED 2026-09-14 (Nicko): keep unless the UE5 spike proves
  the rig budget heavy; the spike can kill it before M4.
- Arena placement inside the future full Darkwood: world-GDD concern,
  not a slice blocker.
- GAS adoption gate: DECIDED AT THE UE5 SPIKE (Nicko, 2026-09-14):
  the spike runs real GAS test code alongside plain C++ gameplay code
  and the result is recorded at slice exit.
- UE5 SPIKE PREREQUISITES (Nicko, 2026-09-14): Nicko provisions the
  Meshy/Tripo API key and machine access with UE5; doc 29's remaining
  validation stages then run. This is the critical-path blocker for
  the slice's 3D pipeline work.
- Perf budget revision after M6 numbers land; the budget itself is a
  spike deliverable (Nicko, 2026-09-14).