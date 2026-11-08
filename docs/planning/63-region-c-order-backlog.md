# 63 - Region C Order Backlog (Forest of the Old King)

Status: PROPOSED, IO spec session 2026-10-07 (census @ 98393f2). Companion
to doc 62 (design). ONE change order at a time, each small enough to land
and playtest in one builder run. Build order below is the dependency order;
a later order never opens before the earlier one is PLAYTEST-APPROVED by
Nicko. Briefs land in io/missions/YYYY-MM-DD-cc-<slug>.md with crg impact
baked in before dispatch. Process law = doc 62 §13.

## PHASE 0 - INTEL (no game code)

### CC-C0 · crg + tree-tri baseline (pure code-reading, no dispatch needed)
- Scope: register /tmp/wh-worldfeat with code-review-graph if the alias is
  stale (crg register /tmp/wh-worldfeat + crg build, binary
  /app/venv/bin/code-review-graph, alias wh-worldfeat); record the tree tri
  ledger baseline (current A/B tree scatter counts: yewTree 72,
  witchwoodTree 11, treeStump 9 CONFIG rows, verified at 98393f2) plus the
  C tri budget plan for the ledger CC-C3 uses.
- Dependencies: none. Assets: none.
- Output: numbers in the CC-C1/CC-C3 briefs.

## PHASE 1 - THE REGION SHELL

### CC-C1 · Heightfield spike (scratch-only)
- Scope: scratch/ spike, NO game js touched: displaced PlaneGeometry at C
  scale (smooth multi-octave noise, ~40k tri target for one draw-call
  mesh), raycast height sampler (WH_GROUND.heightAt(x,z) API shape),
  segment density vs fps probe, slope/step numbers, camera-under-ground
  check. Demo html for eyeballs only.
- Dependencies: CC-C0. Assets: none (procedural).
- Gates CC-C2/CC-C3/CC-C4: the spike log + demo carry the numbers (the
  OQ-62.1 slope clamp numbers come from here).
- Playtest: Nicko opens the demo html (not a game build; no harness).

### CC-C2 · Region C shell: doorway, gate, boundary, flat stub ground, tree scatter
- Scope: the walkable shell so Nicko can traverse and playtest an empty-ish
  forest BEFORE the heightfield lands. Includes:
  - B/C connection as the boundary-table generalization: A's rows
    byte-identical, B/C plane z=-86, C center (0,-366) r=280 (doc 62 §1
    arithmetic).
  - Second-plane clamp generalization + doorway (arch/gateM props, existing
    assets) at B's north rim.
  - Gate on the TUTORIAL LAW predicate (!dayNight.dormant, no new state)
    with a reason-naming locked toast (camp ghost refusal style).
  - C stub ground: flat disc at y=-0.05 (avoids coplanar z-fight with B's
    disc), C-local ground canvas variant, C fog/ambient rows, deep-forest
    fog palette.
  - First tree-scatter pass with distance-culling (beyond fog-opaque = not
    placed), reusing yewTree/witchwoodTree/treeStump; density per CC-C0
    ledger (typo law: the asset ids are yewTree / witchwoodTree /
    treeStump exactly).
  - L0 entry glade furniture (lantern post).
  - save.js "world.regionId" additive block (C4 law).
  - CONFIG rows: regionC block, boundary table, doorway, gate, stub ground.
  - NOT TOUCH: enemy.js (no wolves yet), camp.js/daynight.js (tutorial law
    untouched), player.js, A/B region rows (byte-identical), camp system.
- Dependencies: CC-C0 + CC-C1 spike numbers (density); the stub ground
  needs no heightfield. Assets: none (arch/gateM/lantern/tree GLBs on
  disk).
- Acceptance: A1 walk from B through the doorway into C's stub forest -
  gated while dormant (locked toast + blocked passage), opens after the
  first Save-and-Heal, same profile. A2 tree scatter visible to fog depth,
  no z-fighting against B's disc. A3 A/B traversal unchanged.

### CC-C3 · Tree scatter full pass + budget ledger + forest fog discipline
- Rider (R-62.6 session, 2026-10-07): camp.js edge check becomes
  region-aware (reads the active region's center + groundRadius) so camps
  deploy inside C; A/B placement unchanged. Small, declared in the brief.
- Scope: full tree scatter for r=280 with distance-culling, density per
  CC-C0 ledger + CC-C1 spike numbers; fog depth tuned so the disc edge
  never shows (doc 61 world-edge finding); tri-budget ledger row per 100
  trees (ledger lives in the order brief; doc 61's 2M budget governs); L1
  Old King's Stone centerpiece assembly on the stub ground (statue/gate/
  boulders; rises with the heightfield in CC-C4).
- Dependencies: CC-C2 (shell + stub). Assets: none (existing tree GLBs;
  centerpiece = existing kit assembly).
- Playtest: traversal + fps counter read by Nicko.

### CC-C4 · Heightfield landing (R-62.1)
- Numbering note: doc 62 §4's phase list describes the same program
  (spike -> land). The backlog numbering is authoritative: shell before
  hills, so Nicko playtests traversal in CC-C2 first.
- Scope: C's ground becomes the displaced mesh (one draw-call, ~40k tris);
  WH_GROUND.heightAt(x,z) sampler feeding player / enemies / props /
  corpses / camp ghost (P0-1 holder pattern, doc 61); max-step slope
  guard; camera min-height respects sampled ground; sampler returns 0
  outside C. Save: no schema change (y derived from regionId + x + z).
- Dependencies: CC-C1 spike numbers + CC-C3 (tree scatter re-tuned on the
  mesh). Assets: none.
- Playtest: walk the hills - hills visible, slope clamps feel right,
  camera never underground, props sit ON slopes.

## PHASE 2 - INHABITANTS

### CC-C5 · Wolves: packs, loops, cohesion, pack aggro
- Scope: new js/enemy-wolf.js (loads after enemy.js; index.html script
  order) + CONFIG.enemy.wolf rows + pack machinery hooking the landed AI1
  shapes (strafe band, decision loop): closed-loop patrol waypoints in
  CONFIG, pack cohesion (leash radius to the pack centroid), pack aggro
  (one pulled = pack pulled, binding), relay lunge, night-boldness aggro
  multiplier read from the landed clock. Spawn rows L7/L8/L9. Placeholder
  body until the Astrabot wolf GLB (flagged, not dispatched).
- Dependencies: CC-C4 (packs belong with the hills). Soft fallback: if the
  heightfield hits a wall, wolves can land on the stub - IO surfaces the
  option at the time. AI1 shapes are landed (e325005 / 6aaf339).
- Ruling note: night-boldness = aggro radius multiplier when dn.phase
  reads night (darkcourt law respected - night is their playable day, so
  night is simply more dangerous). If a phase-read proves flaky, the
  fallback is a day-counter read; the ruling is "night is bolder", not the
  mechanism.
- Playtest: packs patrol loops, cohesion holds, pack-pulls-pack, night is
  bolder. Placeholder body acknowledged.

### CC-C6 · Bandit camps x3 (L4/L5/L6)
- Scope: camp Alpha/Bravo/Charlie rows + bandit props + campkit
  firepit/bedroll/pegs (CK1 pattern) + usable cook station at each firepit
  + AI1 guard posture + loot/gather nodes at camps (no containers; chests
  stay the quest reward). Deepest camp (L6) = best loot tier.
- Dependencies: CC-C4. Assets: none (all props on disk).
- Playtest: camps read as camps; guards use AI1 posture; cook at enemy
  fires works.

### CC-C7 · Rot Mother (R-62.4) + minions
- Scope: boss + minions in a new js/enemy-rot.js: nest at L3, repeatable
  respawn (lair re-arms 3 in-game days after her last death, re-arm on
  player proximity), minion cadence while she lives (1 spawn every 7s, cap
  3 live, all despawn on her death), poison-lite v1 = damage + slow debuff
  ONLY (OQ-62.3 confirmed with Nicko at this order's clarify - do not grow
  it silently), reward = rot-silk + rotgland materials per kill.
  Placeholder body (Astrabot flagged).
- Dependencies: CC-C4. Assets: Astrabot Rot Mother + egg sacs + minion GLB
  flagged; placeholder bodies first.
- Playtest: boss loop readable, cadence readable, materials drop, respawn
  discipline (dead landmark for 3 days, re-arms on approach).

## PHASE 3 - THE BARROW (first dungeon)

### CC-C8 · Barrow region shell + fade teleport
- Scope: barrow as its own region def (id old_king_barrow) inside the same
  region-manager: streaming/dispose/persistence reused; fade teleport at
  L2's door and back; dark fog + low ambient + candelabra light pools;
  crypt-kit corridors + sarcophagus chamber (assets on disk, doc 61
  light-pool gap closed here).
- Doorway note: CC-C2's doorway is a WALK-ACROSS plane (clamp-style); the
  barrow door is the TELEPORT-style variant (cross plane in corridor ->
  fade teleport). Both live in the connection model from CC-C2's
  generalization.
- Dependencies: CC-C4 (doorway L2 on the heightfield) + CC-C2's connection
  machinery. Assets: none (crypt kit on disk).
- Acceptance: enter, corridors navigable, exit back to C at the barrow
  threshold; death in the barrow respawns at the camp respawn point; load
  restores the active region at the door (world.regionId block).

### CC-C9 · Crafting materials: barrow + C-wide gather nodes
- Scope: gather nodes inside the barrow + C overworld node rows; materials
  flow into the crafting inventory and BANK (doc 05 governs crafting; NO
  recipes consume them yet - recipes are later orders).
- Dependencies: CC-C8 (barrow exists) + CC-C7 (mat ids exist). Assets:
  none (node props = on-disk kit pieces; prettier models flagged Astrabot
  if wanted).
- Playtest: gather in the dark with candelabra pools; mats bank correctly.

## PHASE 4 - FARM, NPC, QUEST, REWARD

### CC-C10 · Farmstead + farmer NPC + first dialog UI
- Scope: L10 farm rows (fences m2, tilled rows on the ground canvas,
  farmhouse placeholder kit assembly; Astrabot farmhouse flagged), farmer
  NPC (new js/npc.js surface; placeholder standing races GLB; Astrabot
  flagged), dialog panel (tent-menu style DOM panel, camp.js convention),
  quest seed: talk -> "my daughter was taken into the Old King's Barrow";
  quest state stored additively (questState block; v1 states available ->
  active -> complete).
- Dependencies: CC-C8 (the barrow door exists as the quest's target).
- Assets: Astrabot farmer + daughter + farmhouse flagged; placeholders
  first. No dispatch without Nicko's word.
- Playtest: farmer speaks, quest activates, HUD line tracks.

### CC-C11 · Rescue + reward: quest completion + CAMP CHEST (R-62.5)
- Scope: daughter held in the sarcophagus chamber (guarded), rescue
  interaction, quest completes on return talk; the CAMP CHEST spawns at
  the player's camp beside the campkit pegs; chest panel (24-slot 6x4
  grid, tent-menu style, openable only while at camp); save additive
  "chest" block (WH_SAVE surface). Rescue feel (instant rescue vs
  walk-out) is Nicko's call at this order's clarify (OQ-62.4).
- Dependencies: CC-C10 (quest active + dialog UI) + CC-C8 (barrow chamber)
  + CK1 (campkit pegs anchor). Assets: chest GLB flagged Astrabot;
  procedural chest box placeholder.
- Playtest: full chain - talk, delve, rescue, return, chest at camp, panel
  opens only at camp, contents persist across save/load and camp
  re-placements.

## APPENDIX: RULINGS TRACEABILITY

| Ruling | Source | Lands in |
|---|---|---|
| R-62.1 heightfield | clarify 2026-10-07 | CC-C1 spike, CC-C4 landing |
| R-62.2 scale (band 250-300, pinned 280) | clarify 2026-10-07 | CC-C2 stub, CC-C4 mesh |
| R-62.3 scene-swap dungeons | clarify 2026-10-07 | CC-C8 |
| R-62.4 repeatable nest boss (3 in-game day re-arm) | clarify 2026-10-07 | CC-C7 |
| R-62.5 24-slot camp chest at pegs | clarify 2026-10-07 | CC-C11 |
| R-62.6 ANCIENT FOREST (big trees scale ~16-26, spacing ~55m) | Nicko playtest 2026-10-07 | CC-C2 first pass superseded, CC-C3 full pass |
| TUTORIAL LAW gate | game state, verified | CC-C2 |
| Save additive blocks (C4 law) | game state, verified | CC-C2, CC-C10, CC-C11 |
| Wolves/AI on landed AI1 shapes | e325005 / 6aaf339 | CC-C5, CC-C6 |
| Greenfield: no wolf/rot/NPC/quest/chest code exists | census 98393f2 | all new files |