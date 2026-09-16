# 55 - UE5.8 World and Streaming Architecture Spec

Drafted 2026-09-16, UE5.8 world and streaming architecture spec (doc 31 engine plan governs; GDDs 46-51 + planning corpus are the content source). PROPOSED for Nicko review. Subordinate to locked rulings; conflicts are open questions, not edits.

Scope: the WORLD module only (doc 52 spec set row 55). Level streaming for the continent, hold-overlay integration, procedural dungeon generation, delve layouts as levels, seat/city level maps. This doc authors engine structure and contracts. Gameplay content stays in the GDDs: delve content is doc 47's, conquest sim internals are doc 13's, combat internals are doc 54's, ledger tables are doc 57's.

Sources: doc 52 (plan of record), doc 03 (continent, biomes, structure principle), doc 49 (placements: underworld capital, Deep Altar, altar sites), doc 47 (three delve GDDs), doc 13 (conquest meta), doc 37 Part 5 + doc 08 (descent gates, generation grammar, exit-trigger ruling), doc 12 (faction seats context), doc 53 section 1.4 (naming conventions; inherited, not restated).

## 1. CONTINENT STREAMING ARCHITECTURE

### 1.1 World composition approach

PROPOSED: UE 5.8 One File Per Actor (OFPA) world partition over world composition semantics, structured as a persistent level plus manually assigned streaming levels. Rationale: doc 03 locks a hand-authored overworld (~10 x 13 km, ~130 km2, locked 2026-09-12), which is one continuous authored terrain body; per-hold political state (doc 13) needs per-region runtime swap, which level streaming gives and pure OFPA tiling does not.

- Persistent level: `WH_Continent_Persistent` (PROPOSED name, doc 53 section 1.4 asset pattern). Holds: terrain, world partition grid, the streaming manager, global lighting/sky (doc 03 Veil-Tide fronts read from the sky), the hold subsystem (section 2).
- Streaming levels: one per biome-region bucket, one per city, one per delve (sections below).
- The doc 31 slice pocket (`WH_Arena_Darkwood`, doc 53 section 1.3) lives inside the Darkwood-region streaming level as an authored clearing; doc 49 section 6 continuity: the pocket's law does not change when the full Darkwood lands.

### 1.2 Level bucketing

- Hold-region streaming levels: one streaming level per doc 03 biome region (6 biomes: Darkwood forests, moors/highlands, swamplands, mountains/passes, farmland/river valleys, blighted zones). Sublevel per hold: doc 03/13 locked 20-30 holds, target ~25 (doc 03 scale target); PROPOSED 25 hold sublevels, `WH_Region_<Biome>` parent + `WH_Hold_<HoldName>` sublevels (PROPOSED names).
- City streaming levels: separate streaming levels, one per seat, with their own sublevels, per doc 49's locked seat geography (doc 44 Part 4):
  - `WH_City_NewCapital` (light seat; Sun altar delve entry beneath it, doc 49 section 3.1)
  - `WH_City_VeilSpire` (dark seat; Veil altar ruin at its root, doc 49 section 3.2)
  - `WH_City_OrcCity` (dark minor seat, doc 44 Part 4)
  - `WH_City_DwarfCity` (dwarf seat; Tither's Hole access east of its workings, doc 49 section 1.2)
  - `WH_Capital_Underworld` (the Pale Queen's seat; its own level structure is section 4.4)
  - Each carries sublevels per district/wall tier (PROPOSED: 3 sublevels per city; doc 03: cities are walled, multi-district).
- Blight scars (doc 08 lines 83-89: three scars, Core ~10 km2 at the Spire) are terrain bodies inside their parent region levels, not separate streaming levels; the Spire scar is part of `WH_City_VeilSpire`'s surroundings sublevel.

### 1.3 Loading distance bands (PROPOSED)

Three bands, tuned at implementation (open question CW-1):

| Band | Radius (PROPOSED) | Behavior |
|---|---|---|
| Active | 0-600 m | Full load, actors ticked, encounters live (doc 41 grammar) |
| Near | 600-1500 m | Streaming level loaded, AI/sim tick at reduced rate; holds resolve off-screen triggers here (doc 13: triggers fire unseen) |
| Dormant | beyond 1500 m | Unloaded; state lives in the hold subsystem, consequences read on arrival (doc 13: off-screen resolution) |

- No fast travel (locked, doc 03), so every transition is a walked/ridden approach: band edges must clear by mount speed at doc 03's travel times (full crossing ~39 min mounted). Bands are therefore PROPOSED against the ~2.3 km average settlement gap.
- Blocking vs non-blocking load: overworld region transitions are NON-BLOCKING (visible pop-in is managed by doc 31's draw-call/triangle budgets; fog and biome density cover seams). City and delve transitions are BLOCKING on the boundary volume (a physical gate or stair, matching doc 37 Part 5's legible-door grammar: doors are in-world and physical).
- Blighted-zone weather wrongness (doc 03) is a post/layer state keyed per region level, not a global toggle.

### 1.4 Paths

Per doc 31's locked folder list via doc 53 section 1.3 (not restated, extended only under the World folder, which doc 53 reserves for this doc):

- `/Game/WH/World/Continent/` persistent level + streaming manager config
- `/Game/WH/World/Regions/` six region levels + hold sublevels
- `/Game/WH/World/Cities/` five seat levels + district sublevels
- `/Game/WH/World/Delves/` section 4's authored delve levels and strata sublevels
- `/Game/WH/World/Dungeons/` procedural dungeon shells (section 3)
- `/Game/WH/World/Overlays/` hold overlay data assets (section 2)

All names follow doc 53 section 1.4 (`WH` + descriptor in PascalCase segments, underscores, no spaces). C++ classes in this doc take the doc 53 prefixes (`UWH`, `AWH`, `FWH`, `EWH`).

### 1.5 Level tiling conventions (PROPOSED)

- Terrain is one authored body in the persistent level's world partition grid; region levels own only their placed actors (holds, roads' set dressing, biome gameplay volumes).
- Sublevel origin: each hold/city/district sublevel uses a shared continental origin; no per-level re-basing.
- One streaming level boundary per biome border per doc 03's biome map; boundary volumes sit on natural seams (ridgelines, tree walls, scar edges) so doc 03's biome-law transitions read diegetically.
## 2. HOLD OVERLAY INTEGRATION

Doc 13's hold system as engine structure. Interface level only: conquest sim internals (trigger evaluation, war engine, escalation ladder) are doc 13's; this section is the binding contracts.

### 2.1 Engine classes (C++, header-level signatures)

- `UWHHoldSubsystem` (doc 53 section 1.4 subsystem pattern): world subsystem, owns hold registry, conquest state machine, overlay data asset lookup. Tick group: pre-physics, low rate (PROPOSED: 1 Hz at Near band, per doc 13's background slow-burn pace).
- `AWHHoldActor` (PROPOSED): per-hold actor placed in each hold sublevel. Holds `FWHHoldHandle`, spawns/destroys region gameplay on doc 13 flip states (banner actor, patrol spawner sets, war-camp sprite dressing per doc 13 proposal A).
- `FWHHoldState` (struct): hold id, owning faction, stability model fields (doc 13's four vulnerability triggers read as inputs: succession, decimation, legitimacy, siege event), current doc 13 state (stable / invasion window / flipped / contested).
- `FWHHoldDefinition` (data row): one per hold, doc 03's real-place contract (noble family, tavern anchor, dungeon cluster).

### 2.2 Overlay data assets

`/Game/WH/World/Overlays/` (PROPOSED):

- `DA_WHOverlay_<HoldName>` per hold: banner set, patrol composition, spawn tables overrides, safe-road flags, price modifiers. Content tables are doc 13's; this doc fixes the container.
- Class `UWHHoldOverlayAsset` (UDataAsset subclass): rows keyed by doc 13 state so a flip re-keys (a) patrol ranges, (b) spawn tables, (c) settlement behavior, matching doc 03's "territory control affects" list.
- Doc 13's escalation ladder (rumors -> patrols thin -> border skirmishes -> siege -> conquest) maps to PROPOSED visual-dressing rows per rung (smoke columns, refugee sprites, war camps): the map reads like weather (doc 13 proposal A), delivered as streaming-level state swaps, not a politics UI.

### 2.3 Binding conquest state to streamed level instances

- `AWHHoldActor` implements `IFWHHoldLevelBinding` (PROPOSED interface): `GetOverlayAsset()`, `OnHoldFlipped(const FWHHoldState&)`, `OnRegionLoadStarted()`, `OnRegionLoadComplete()`.
- Because doc 13's triggers fire whether or not the player knows (locked), trigger evaluation runs in `UWHHoldSubsystem` at all times, including when the hold's level is Dormant/unloaded. A flip applied to an unloaded level: subsystem records the new state; on next load, the region level's `OnRegionLoadStarted` applies the overlay asset before actors tick. Consequences are witnessed on arrival (doc 13 resolved item 3).
- Inversion case: a dark-flipped river valley runs doc 03's inverted rule in mirror (night markets, day requisitions); the overlay asset carries clock-weight overrides the day/night system reads (doc 03 alignment safety; ownership of the clock itself stays with the doc 03/12 systems).
- The underworld capital and the three hidden seats are OUTSIDE conquest territory (doc 49 section 1.4: no hold overlay shows anything there): no `AWHHoldActor` in those levels; the hold overlay map reads nothing at their positions.
- Doc 13's player-held holds and land grants: a granted hold keeps the same streaming level and sublevel; the overlay asset row is regenerated (doc 13: procedural nobility per doc 14 naming). No new level is minted at runtime.

## 3. PROCEDURAL DUNGEON GENERATION

Doc 22/doc 03 grammar (procedural interiors persist once generated; named/special dungeons stay hand-authored) plus the doc 08/doc 37 ruling chain: one descent gate per dungeon, four escalating strata keyed to level 10/20/30/40 (doc 37 Part 5 rulings 9-12), and fresh generation per stratum (doc 37 open 19 resolution, 2026-09-14: each stratum generates its own layout; strata are separate dungeons below the one gate, not re-used floors).

### 3.1 Generator design

- `UWHDungeonGenerationSubsystem` (PROPOSED): world subsystem, generation-time only (editor-time for authored shells, game-time for procedural interiors).
- `AWHDungeonSeedActor` (PROPOSED): placed at each doc 03 dungeon-cluster anchor in hold sublevels. Carries dungeon type (doc 37 Deep Table types: crypt, mine, coven hollow, warren, etc.), region tier band (doc 06 crossing rule: tier band stays regional), and the playthrough seed binding.
- Generation grammar per doc 03/doc 31 G24: archetype seeding per stratum (doc 37 resolved item 19). Layout archetypes, monster pools, loot tables, hazard density come from doc 22's authored-rules-per-type contract; this doc wires the generator that consumes them.

### 3.2 Module kit shapes (PROPOSED)

- Module = an instanced set piece with doc 53 naming: `SM_WH_DungMod_<Archetype>_<Shape>` (e.g. `SM_WH_DungMod_Crypt_CorridorL`).
- Kit shapes (PROPOSED minimum set): corridor straight/L/T, chamber small/medium/large, stair shaft, antechamber, gate antechamber (descent gate socket), exit antechamber, chamber-with-side-rooms.
- Each module carries socket metadata (`FWHDungeonSocket`: position, facing, stratum tag, open/closed) consumed by the assembler.
- Module kits are per dungeon type per biome; kit content authoring is an art/GDD pass (open question CW-3): this doc authors the socket contract only.

### 3.3 Seed handling

- One playthrough master seed (PROPOSED: 64-bit, saved per doc 53's save/load system); per-dungeon seed = hash(master seed, dungeon id, stratum index).
- Determinism: same seed, same layout. Persistence rule (locked doc 03): the generated layout is saved for the playthrough on first generation; regeneration produces the saved layout, not a new one.
- Fresh generation per stratum (doc 37 resolved item 19) means each stratum's seed input differs by stratum index; doc 03's archetype seeding per layer applies per stratum.
- Seeds are content-addressed by dungeon id, never by world position, so doc 13's map movement (a hold flipping) does not disturb existing generated layouts.

### 3.4 Per-stratum generation flow (PROPOSED)

1. Player meets a stratum's threshold (doc 37: each stratum still checks its own level/lock threshold when entered; re-opening a door does not expose deeper strata).
2. Subsystem resolves archetype + pool tables for that stratum (fixed content per dungeon, locked doc 37: no visitor-level scaling).
3. Layout generated from module kit sockets; exits placed; descent gate socket placed at the dungeon end chamber (one gate per dungeon, doc 37 ruling 10).
4. Layout committed to the save (doc 03 persistence) when the stratum is CLEARED: per the doc 08 reconciliation pass ruling, destruction commits at the EXIT TRIGGER (doc 37 audit ruling 18: exit-only dungeon-clear writes preserved), not per-kill.
5. Strata beyond the first generate below the gate, reached by descending within the opened gate (doc 37 ruling 10: layers are reached by descending further within the same opened gate).

### 3.5 Exit-trigger commit rule

Doc 08 reconciliation ruling (destruction commits at the exit trigger, superseding inhabitants-respawn-on-rest for doc 37 dungeons): the generator serializes the stratum's post-clear state when the player crosses the stratum's exit trigger; killed inhabitants, opened containers, and destroyed set dressing commit at that point. Rest/recolonization interplay and partial-kill edges are doc 35 G13's serialized records (doc 37-C line 69 assignment), not this doc's.

### 3.6 Descent gates as level boundaries

- A descent gate is an in-world physical door at a dungeon's end chamber (doc 37 ruling 9): engine-wise (PROPOSED) an `AWHDescentGateActor` at the boundary between the dungeon shell level and the stratum streaming levels beneath it.
- One gate per dungeon; four strata behind it keyed to 10/20/30/40 or lock-tier (doc 37 ruling 10; stratum thresholds re-checked at each stratum entry, locked reconciliation).
- Opened gates persist (doc 37: the door remembers being picked; doc 03 persistence): gate-open state is a save flag consumed by the streaming manager; strata levels stay loaded only while descended into, then unload to Dormant with state kept.
- Deep strata (gate IV, layer 5) carry doc 37's Deep Table content by dungeon type; spine exclusion (doc 37: procedural deep layers never carry apex powers or mandatory-ending unlocks) is enforced by keeping deep-layer reward rows out of spine-gated tables (ledger-compliance note, section 5).

## 4. DELVE LAYOUTS AS LEVELS

Doc 47's three altar delves are named endgame dungeons, so per doc 03/doc 47 they are hand-AUTHORED layouts, not procedurally generated; doc 37's fresh-generation-per-stratum ruling does not apply to them (doc 47, Sun section hand-authored note). This section wires their level shells; strata content (themes, perils, encounters, warden concepts) stays in doc 47.

### 4.1 Naming (per doc 53 section 1.4)

| Delve | Level (PROPOSED names) | Strata sublevels |
|---|---|---|
| Sun Altar Delve | `WH_Delve_SunAltar` | `WH_Delve_SunAltar_S1` ... `_S5` |
| Veil Altar Delve | `WH_Delve_VeilAltar` | `WH_Delve_VeilAltar_V1` ... `_V5` |
| Deep Altar Delve | `WH_Delve_DeepAltar` | `WH_Delve_DeepAltar_P1` ... `_P6` |

### 4.2 Per-strata sublevel structure

- Doc 47 strata counts (PROPOSED counts in doc 47, wired here): Sun five (S1 Underbelly, S2 Harvest Lines, S3 Taint Cisterns, S4 The Works, S5 The Humming Chamber), Veil five (V1 Old Throne's Crypt, V2 Erased Galleries, V3 Pact-Scar, V4 Tithe Vaults, V5 The Remains), Deep six (P1 Den's Stairs, P2 Old Foundations, P3 Wild Strains, P4 Dark Beneath the Dark, P5 Congregation's Porch, P6 The Final Chamber). Total 16 strata.
- Each stratum is one sublevel; stratum N's exit trigger is stratum N+1's load boundary. Doc 47 checkpoint bands (one checkpoint per strata boundary, PROPOSED there, doc 47 shared grammar): the checkpoint volume lives at the strata boundary in the persistent shell logic of the delve level; camp-grammar saves per doc 09/11 via doc 47's checkpoint rule.
- Strata sublevels stream BLOCKING at boundaries (a descent is a commitment; doc 47's attrition economy assumes no mid-stratum world pivot).
- Doc 47 checkpoint-band open question (doc 47 AD-7) is tuning, not structure: sublevel boundaries are fixed by strata count regardless of checkpoint cadence.

### 4.3 Final-chamber encounter level hooks

- Each delve's final stratum sublevel (S5/V5/P6) contains a final-chamber actor shell: `AWHEncounterStage` (PROPOSED) with trigger volume, boss-warden spawn point, and lever-fire relay.
- Doc 54 owns combat internals (doc 52 spec set row 54: state machine, frame data, boss remix math); this doc authors the level shell only: one spawn socket, one arena volume, one exit/return volume, sized PROPOSED at doc 34 boss scale clearance (open question CW-4).
- Boss-warden identity and encounter content are doc 47's (three concepts per delve, PROPOSED there); the level shell references them by soft class pointer, filled by doc 34's bestiary pass (doc 47 AD-2).
- Lever rule (doc 44 Part 8, locked; restated doc 47 section 4, not re-ruled): the delve's final act (destroy Sun altar / destroy Veil remains / re-kindling) fires the quest-side consequence chain. Engine shape: the final act is an interactable in the final chamber sublevel whose activation raises a `FWHOnDelveLeverPulled` delegate (PROPOSED signature, doc 53 naming) consumed by the quest system (doc 46/21 chains own the beats).
- Doc 47's two-stage trigger (audit N11: altar lighting starts the working; the dark king's death commits her) is quest-state logic (doc 44 Part 5C); the level shell exposes only the two state flags as save-backed booleans on the final-chamber actor.

### 4.4 Re-kindling chamber as scripted sequence stage

- The Deep delve's P6 re-kindling (doc 47 section 3: the re-kindling IS the final chamber) is staged as a Level Sequence stage (PROPOSED): `LS_WH_DeepAltar_Rekindling` under `/Game/WH/World/Delves/Sequences/`.
- Sequence scope: altar lighting, congregation muster arrival (doc 49 section 2: banners travel the wolf-road), the Rival Engine moment (doc 46 beat DA-4). Beat CONTENT is doc 46's; the sequence asset and its camera register are this doc's (camera blends per doc 28/doc 53 plugin list: LevelSequence + TemplateSequence).
- The sequence is skippable-none (PROPOSED): it is the underworld's counter-engine founding, doc 44 Part 8 neutral path; no doc grants a skip. Open question CW-5 if a skip is wanted.

### 4.5 Underworld capital cavern-city level structure (doc 49)

- Level `WH_Capital_Underworld` (PROPOSED, section 1.2) with sublevels per doc 49's tier grammar (each tier is an old waterline, PROPOSED there):
  - `WH_Capital_Underworld_T1Market` (lowest tier, arrival tier: doc 49 section 1.4, arrival is into the market tier, never the court tier)
  - `WH_Capital_Underworld_T2Walls` (middle tiers)
  - `WH_Capital_Underworld_T3Court` (court tier: met only after vouching grammar, doc 49)
  - `WH_Capital_Underworld_DrownedFloor` (muster ground, doc 49 section 1.5)
- The three surface mouths (Drowned Stair, Tither's Hole, Wolf-Road Mouth, doc 49 section 1.2) are door actors in their parent surface region levels, each rumor-tier gated per doc 44 Part 4 hidden-seat grammar; no map marker is ever granted (doc 49 section 1.4: the hold overlay shows nothing here).
- The Wolf-Road (doc 49 section 2.2) is a PROPOSED corridor streaming level `WH_Road_WolfRoad` connecting the capital's court tier to the Deep delve's P1 entry, loadable independently so the congregation's walk and the siege version (doc 49 section 2.3) run in the same level shell.
- The Smuggler Road (doc 49 section 3.1) and North Trunk (doc 49 section 3.2) are PROPOSED tunnel-corridor streaming levels `WH_Road_SmugglerRoad`, `WH_Road_NorthTrunk`, same pattern, each terminating at its altar delve's entry sublevel.
- The Neutral Brokers' seat sits ON the North Trunk route (doc 49 section 1.3): a small authored sublevel `WH_Capital_BrokersSeat` streamed as part of the trunk's corridor level, not the capital's.

## 5. TEST PLAN

Testerbot validates (grep-able checks named exactly; all run against this file and the cited docs):

1. T1 streaming level naming vs doc 53 section 1.4: every level name in this file matches `WH` + PascalCase segments, underscores, no spaces, no em dashes.
   - grep: `grep -E 'WH_[A-Za-z]+(_[A-Za-z0-9]+)*' 55-ue5-world-streaming-architecture.md` returns only convention-conforming names.
2. T2 strata counts vs doc 47: Sun 5 + Veil 5 + Deep 6 = 16.
   - grep: `grep -c 'STRATA\|strata sublevel\|_S[1-5]\|_V[1-5]\|_P[1-6]' 55-ue5-world-streaming-architecture.md` and manual count of section 4.2 table rows equals 16.
3. T3 seat geography vs doc 49/doc 44 Part 4: the five seats named in section 1.2 match doc 49's seat list (New Capital, Veil Spire, Orc City, Dwarf City, underworld capital) and doc 49's three hidden seats (Hidden Court den, Reliquary Wardens' vault-seat, Neutral Brokers' true seat) appear as non-conquest (no hold actor).
   - grep: `grep -c 'WH_City_\|WH_Capital_' 55-ue5-world-streaming-architecture.md` equals 6 level names; `grep 'OUTSIDE conquest territory' 55-ue5-world-streaming-architecture.md` matches section 2.3.
4. T4 no gameplay beats authored: no stratum theme, peril, encounter description, boss concept, or lore sentence appears; only structural wiring with citations.
   - grep: `grep -iE 'warden encounter [SVP][0-9]|theme:|peril:' 55-ue5-world-streaming-architecture.md` returns no content rows (citations to doc 47 only).
5. T5 generation doc citations present: doc 37 Part 5 rulings 9-12, doc 37 open 19 resolution (fresh generation per stratum), doc 08 exit-trigger ruling, doc 03 persistence rule each cited in section 3.
   - grep: `grep -c 'doc 37\|doc 08\|doc 03' 55-ue5-world-streaming-architecture.md` counts at or above the citations present in sections 3 and 1.
6. T6 overlay integration vs doc 13: the four doc 13 vulnerability triggers, the escalation ladder rungs, and the off-screen-resolution rule are each cited in section 2.
   - grep: `grep -c 'doc 13' 55-ue5-world-streaming-architecture.md` in section 2 at or above 5.
7. T7 ledger compliance: no element in this doc grants any character knowledge a doc 44 Part 2 cell forbids (the delves are content-quiet by construction per T4; no NPC, no beat, no text added). Runtime ledger table ownership is doc 57's (doc 52 spec row 57); this doc's `FWHOnDelveLeverPulled` consumer reads doc 57's ledger, never writes it.
   - grep: `grep -c 'KNOWS\|SUSPECTS' 55-ue5-world-streaming-architecture.md` returns only citation-context matches, no new ledger rows authored.

## OPEN QUESTIONS (doc 08 format)

- CW-1: Loading distance band radii (section 1.3, PROPOSED 600 m / 1500 m): tune against streaming hitch budget and doc 31 perf budget (60 fps locked, under 1,500 draw calls) on target hardware. Assignment: implementation tuning pass, M2, Testerbot measurement.
- CW-2: Blocking-load mask for delve and city transitions: pure volume-based blocking load vs a doc 37-style physical door with a load accept interaction. Doc 37 ruling 9 legibility suggests physical doors; UE loading UX suggests volumes. Assignment: Nicko ruling at spec review.
- CW-3: Module kit shape catalog per dungeon type per biome (section 3.2 minimum set is PROPOSED): which doc authors the full kit list and its art pass. Assignment: world GDD pass (doc 22 owner) + doc 25 art pipeline.
- CW-4: Final-chamber arena dimensions per delve (section 4.3, PROPOSED to doc 34 boss scale): three delves, three chamber shells, one clearance number. Assignment: doc 34 bestiary pass (with boss-warden chassis sizes, doc 47 AD-2 dependency).
- CW-5: Re-kindling sequence skip grant (section 4.4, PROPOSED no-skip): whether NG+ replays may skip the muster sequence. Assignment: Nicko ruling; doc 46 owns beat content.
- CW-6: Corridor streaming level count for the three doc 49 roads (Wolf-Road, Smuggler Road, North Trunk, section 4.5 PROPOSED): one corridor level per road vs corridor sublevels inside neighboring region levels. Bandwidth impact at doc 31 budgets. Assignment: implementation pass M2+ measurement, Testerbot.

## COMPLETION REPORT

Sections delivered: 5 of 5 (1 continent streaming architecture, 2 hold overlay integration, 3 procedural dungeon generation, 4 delve layouts as levels, 5 test plan) plus open questions CW-1..CW-6.

Level/sublevel counts (PROPOSED): 1 persistent level; 6 region levels + 25 hold sublevels; 5 city/capital levels (4 surface seats + underworld capital) + 15 city district sublevels + 4 underworld capital sublevels + 1 brokers' seat sublevel; 3 delve levels + 16 strata sublevels; 3 corridor levels (roads); procedural dungeon shells generated at runtime per doc 03 persistence (not pre-authored levels). Total authored streaming levels: 19; total authored sublevels: 61.

Spec conflicts: none against locked rulings found. Tension noted, not a conflict: doc 47 proposes 16 strata across three delves while doc 37 locks four strata per PROCEDURAL dungeon; doc 47 explicitly excepts the altar delves from procedural generation rules (hand-authored named dungeons, doc 03), so both hold. Doc 49's underworld capital is outside conquest territory while doc 13's overlay covers all holds: resolved by section 2.3 (no hold actor in seat levels), consistent with doc 44 Part 4.
