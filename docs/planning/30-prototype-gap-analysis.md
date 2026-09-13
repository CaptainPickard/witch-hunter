# 30 - Prototype Gap Analysis

Status: PROPOSED (Astrabot gap analysis, 2026-09-13, pending Nicko lock).

## Method

This audit read every doc in docs/planning/ (00 through 29, including the
26-A audit 26-astrabot-analysis.md) and skimmed the art-direction/ tree
structure for context. The lens: "what does a prototype need that no doc
defines or owns." A gap is recorded only where a system is referenced,
assumed, or required by locked decisions but no doc defines, owns, or
resolves it. Tuning numbers explicitly deferred to GDD are not gaps when a
doc owns the decision; they are gaps when no doc owns the decision at all.
This audit extends 26-A Part 3 (which found the presentation/controls and
art-cost holes) into the systems layer, and reflects the current carrier
state: doc 29 resolved the art carrier to TRUE 3D (low-poly pixelated
models), demoting the sprite production docs (25, 26, 27) to REFERENCE.
Nothing here is LOCKED or RESOLVED. Per repo convention this doc is
PROPOSED and append-only at the audit layer; lock-ins are Nicko's.

## Gap List

### BLOCKER severity (a combat-loop vertical slice cannot start without these)

G1. VERTICAL SLICE SCOPE
The first playable target is undefined. 01-vision-high-concept.md carries
the open question ("Rough target scope for the first vertical slice") and
08-open-questions.md lists it as unassigned. Every other gap below is
scoped by this one.
- How many biome tiles, enemy types, weapons, and spells does slice 1 contain?
- Is slice 1 a combat loop only, or does it include camp/save/tavern?
- What is the acceptance test that proves or kills the slice?
- Which locked systems are explicitly OUT of slice 1?

G2. ENGINE VERSION AND PIPELINE COMPLETION
Unreal is the target (00-README-index.md) but the version is TBD and the
3D pipeline validation is incomplete: 29-art-style-bake-off-spike.md
records image-to-3D, re-texture, and equipment-slot stages as PASS, with
auto-rig + animation and UE5 scene parity explicitly "remaining
unvalidated stages". Engine access (a machine with UE5) is a listed
blocker owned by Nicko.
- Which UE5 version is the target, and does the spike machine match it?
- Auto-rig output quality and hours per body: what is the measured number?
- Does the Three.js spike scene actually predict UE5 register parity?
- Who owns the rigging/retopology skill (doc 29 judging criterion 5)?

G3. INPUT BINDING AND CONTROL MAP
28-controls-camera-gdd.md lists "Input mapping" as an open item and no
other doc owns it. 04-combat-system.md locks the verb set (light/heavy,
roll, block/parry, lock-on, dual-mode aim) but never binds a single key or
button, and defines no crouch, interact, sprint, mount, spell-select, or
item-use verbs even though those verbs are used by locked docs (09, 10,
17, 23).
- Full verb-to-input map for controller and keyboard/mouse?
- Which verbs exist in slice 1 vs deferred (crouch, mount, party commands)?
- Keyboard/mouse scheme for dual-mode aiming (reticle vs lock-on)?
- Rebinding, modifiers, and press-vs-hold conventions?

G4. CAMERA COMPLETION
28-controls-camera-gdd.md locks three registers and lock-on behavior, but
its own open items remain: camera collision, sensitivity, and boss-scale
camera behavior. A playable slice needs all three.
- Camera collision rules vs walls/interiors (procedural dungeons included)?
- Sensitivity defaults and the exploration-to-combat zoom transition rate?
- Does the aim register add a zoom step, and how does it blend?
- Auto-center / recenter rules outside lock-on?

G5. PLAYER BODY CANON AND ANIMATION DATA UNDER THE 3D CARRIER
The player is human-locked (03-world-design.md) and no human model exists.
26-sprite-production-queue.md's bake-in proposed human cards but the race
cards were sprite bodies, now demoted to reference by doc 29. No doc owns
the player's 3D model canon, and no doc owns the combat animation set
(moves, frames-as-time, hit-reacts, staggers, rolls, deaths) that
04-combat-system.md's whole feel contract depends on. 26-A flagged this
as HIGH gap 2/3; the 3D pivot changed the medium, not the hole.
- Who authors the player model and to which concept frame canon?
- What is the full pose/animation list for slice 1, and its hours-per-body cost?
- Does the equipment-slot sub-mesh rule (doc 29 KNOWN ISSUES 1) apply to the player rig from the start?
- Is one player body used for slice 1 (no sex variants yet), and is that a decision or an accident?

G6. EQUIPMENT RULES BEYOND VISUALS
27-equipment-visual-system.md defines the VISUAL layer (canon layers,
equipment slots for appearance). 04-combat-system.md defines EQUIP LOAD
bands from "worn-gear weight". 05-crafting-system.md defines gear TIER and
GRADE. No doc defines the mechanical equipment system itself: the slot
list (is it the visual slot list?), armor values per tier/grade, weapon
damage baselines per class, two-hand vs one-hand rules, off-hand rules,
charm/trinket slots, weight numbers per piece, or how the visual slot list
and the mechanical slot list relate.
- What is the canonical mechanical slot list, and does it equal doc 27's visual slots?
- What does a piece of armor DO (absorption? poise bonus? Ward?), per tier and grade?
- What is a weapon's damage/stamina/poise baseline per class per tier?
- Are there jewelry/charm body slots separate from doc 27's appearance layers?

G7. DAMAGE AND STAT FORMULAS
07-leveling-progression.md locks nine stats and "stats and skills are the
power sources", 04-combat-system.md locks poise/stamina structure, 17
locks spell tier gating. No doc defines how damage is actually computed:
weapon damage to health math, the Precision crit formula, Ward as damage
resistance, armor interaction, the skill primary-curve contribution to
damage, Focus cost scaling, or poise damage values. The docs say
"numbers are GDD tuning" but the FORMULA SHAPE has no owner.
- What is the damage formula (attacker variables vs defender variables)?
- How do Tier and Grade modify damage, and how does armor reduce it?
- What do Precision, Ward, and Speed actually compute?
- Are spell and weapon damage on one scale?

G8. ENEMY AI ARCHITECTURE
04-combat-system.md locks the enemy grammar (enemies use the player's
verbs; light-court pairs, dark-court packs) and 23-expedition-followers.md
requires taunt/aggro mechanics for the Guard. No doc owns enemy AI:
perception, aggro rules, target selection, formation/pair behavior, pack
retreat logic, caster positioning, or how "the player's verbs" map to
AI decisions. The fairness contract is undeliverable without this.
- Perception model (sight ranges, sound, doc 10's audio-cue meals)?
- What drives pair vs pack tactics, and what is the aggro/taunt rule the Guard uses?
- How do i-frames, rolls, and block decisions work for AI on the same rules as the player?
- Is there a difficulty knob inside fixed region danger (sloppiness tiers for bandits)?

G9. ENEMY ROSTER AND ENCOUNTER DATA
04-combat-system.md names enemy families and 10-cooking-meals-drinks.md
lists per-biome enemies for dishes, but no bestiary exists: no stat
blocks, no spawn tables, no per-biome encounter composition, no ambush
and night-spawn rules beyond intent sentences. 03-world-design.md's
dungeon "authored rules per type (monster pools, loot tables, hazard
density)" is named but never written.
- Which enemies exist at slice-1 scope, with what stat blocks?
- What are the spawn/ambush density and patrol rules per biome and clock half?
- What are the dungeon-type monster pools (crypt/mine/den/war camp)?
- What is the boss remix grammar (doc 04: "dungeons teach a monster pool; the boss remixes it") in data terms?

G10. COMBAT FRAME DATA
04-combat-system.md defers poise numbers, stamina costs, parry window
sizes, regen curves, roll i-frame durations, and wind-up timings to "GDD
tuning". The structure is locked, but a prototype needs an owned frame-
data table: every verb's duration, cost, i-frames, and recovery.
- One table owning every verb's timing/cost numbers, even first-pass?
- Parry window sizes in seconds per source (shield to bare blade)?
- Roll i-frame window and stamina cost; stamina-break recovery timing?
- Poise pool and poise damage starting values per weight class and size?

### NEEDED-SOON severity (needed during or immediately after the first slice)

G11. UI AND HUD SPECIFICATION
02-art-style.md locks one line ("modern Souls-style, clean menus,
diegetic touches where cheap"). Multiple docs require specific UI that no
doc designs: health/stamina/poise/Focus HUD, the character menu carrying
the moral axis and titles (11-warp-camp.md, 16-specialties.md), the
follower menu (23-expedition-followers.md), the inventory screen, spell
and technique selection, the World Ledger readouts (20-quests-factions-
gdd-part1.md), the map-reads-like-weather map (13-territory-conquest.md),
and the banner creation UI (02, 14-races-houses-naming.md). 26-A flagged
UI art direction as MED gap 17; the interaction design layer is also
unowned, which is the bigger hole for a prototype.
- What is the HUD layout and which meters exist on screen at once?
- What are the menu flows: inventory, character, follower, crafting, map?
- How are spell/technique/item slots selected during play?
- Which UI is diegetic vs abstract, per doc 02's "where cheap" ruling?

G12. INVENTORY MECHANICS DETAIL
06-loot-and-resources.md locks weight-based inventory and the Carry Weight
stat; 11-warp-camp.md locks valet/storage; 23 adds a squire overflow
pool. No doc defines the interaction layer: item stacking, the pickup and
drop model, weight overflow behavior at max carry, container UI, what
happens to items on a downed follower, ammo/quiver handling, or item
context menus (use/equip/drop comparisons).
- Stacking rules per item class, and what happens at zero carry headroom?
- One inventory pool or separate equipment/consumable/materials tabs?
- How do container contents persist (valet chests, dungeon chests, corpse drops)?
- Drop/pickup model for ground loot given the all-props-are-2D-then-3D presentation?

G13. SAVE AND PERSISTENCE MODEL
Tavern saves, camp saves, and warp-camp forward respawn are locked
(04-combat-system.md, 09-expedition-camping.md, 11-warp-camp.md), and
dungeon persistence is locked (03). No doc owns the persistence model:
what state is saved when and where, autosave triggers, what survives
save/load vs death, whether enemy/NPC/vendor state is saved, how corpse
drops survive reloads, and how NG+ serializes the world reset
(12-moral-axis-factions.md) into this model.
- What is the save data model (single world blob vs per-system state)?
- What are the autosave triggers besides camps, and is death a save event?
- Do vendor stock, node timers, and NPC positions persist across save/load?
- How does the NG+ world reset preserve camp state mechanically?

G14. CURRENCY AND ECONOMY NUMBERS
00-README-index.md decision 4 locks a souls currency drop; 06 locks three
vendor families and requisition contracts; 05/11 lock hire costs and
"expensive" intel. No doc names the currency, defines denominations,
prices anything, or designs sinks and faucets (repair is gone by
decision, so what does late-game money buy?).
- Currency name and denominations?
- Who pays what: vendor price bands, tavern costs, rumor prices, hire costs?
- What are the money sinks in a no-repair economy?
- Does the debt fiction constrain what dark-court vendors will take?

G15. DEATH AND RESPAWN EDGE RULES
The core loop is locked (drop XP/currency at corpse, tavern respawn, warp
camp forward respawn). Unowned edges: dying inside your own camp raid,
dying with the squire holding overflow items, corpse-despawn rules, dying
during a dungeon run with persistence, death during transformation lines
(doc 22 says the death penalty still applies but the Rising reuses the
corpse), and repeated-death softlock protection.
- Where is the corpse marker after death, and does it ever despawn?
- What drops, what stays, and what happens to follower-carried items?
- Does death during a spine/transformation quest stage restart a stage or the chain?
- Any debuff or cost on repeated death (doc 10's corpse-recovery insurance implies one exists)?

G16. AUDIO DESIGN
No audio doc exists (08-open-questions.md Art/Tech Plan: "Sound and music
direction (no doc yet)"). Locked mechanics already depend on audio: doc
10's HUNTER'S DARKBREAD grants "+early audio cue on night ambushes", doc
04's readability contract is partly audio-delivered in Souls games, and
the register ("the frame is a held breath") is half sound design.
- Music direction per biome/register, and combat music state rules?
- Verb audio: swings, parries, staggers, spell accents under the one-accent law?
- Ambush/stealth audio cue grammar (the Darkbread mechanic needs it)?
- Volume of work: who composes/sources, and what is the slice-1 audio minimum?

G17. NPC AND DIALOGUE SYSTEMS
02 locks portrait dialogue for key NPCs; 20 casts tissue patrons from
procedural pools with "race, house, sect, disposition, one secret"; 16
requires NPCs to react to titles; 19 requires witness-tier dialogue; 03
requires den discovery and rumor gameplay. No doc owns the dialogue
system: conversation UI, dialogue tree format, the patron instantiation
rules, disposition and greeting models, NPC daily schedules, or how
titles/axis/sect standing inject lines.
- What is the dialogue data format and authoring pipeline?
- How is a tissue patron generated and voiced from pool parts?
- What is the disposition model (affinity vs axis vs standing vs sect)?
- Do NPCs have schedules/routines, or are they place-based?

G18. DAY-NIGHT BEHAVIORAL CONTENT
The 24:1 clock, affinity-relative danger halves, and Veil-Tide states are
locked (03, 12, 61). What the world actually DOES per half is not: town
open hours, NPC sleep/wake, shop availability, night-only spawns and
content lists, undead spawn anchors, and how the inverted clock changes
towns in dark-flipped holds (doc 03 sketches "night markets, day
requisitions" with no system).
- What closes and opens across the clock in towns (shop hours, tavern role)?
- What is the night spawn table per biome and per affinity?
- How do holds mechanically run the inverted clock when dark-flipped?
- What wakes and sleeps across the Veil-Tide charge states?

G19. STEALTH AND LOCKPICKING SPECIFICATIONS
15-skill-lines.md defines Stealth and Lockpicking as skill lines with
techniques (Shadow Meld, Ghost Step, Silent Takedown, Feel for the Pins,
Trap-Sense, Master's Hand); 11 uses Stealth for thief intrusions; 16
builds the Graverobber on them. No doc defines either minigame or system:
detection math, light/darkness interaction, backstab windows, lock
difficulty tiers, trap types, or noise propagation.
- Detection model (sight cones, light levels, noise radii)?
- Backstab/opening-strike rules vs doc 04 grammar?
- Lock tier ladder vs Lockpicking rank, and the trap grammar?
- Pickpocket rules (doc 15 names the verb; nothing specifies it)?

G20. FOLLOWER AND PARTY TECHNICAL BEHAVIOR
23-expedition-followers.md locks behavior INTENTS (mid-rear bard, rear
squire, front guard, max-range arcanist) and the four command verbs. The
implementation layer is unowned: pathfinding and formation, follow
distance numbers, downed/revive channel mechanics, follower aggro
interaction with G8's aggro model, party XP stream plumbing, and how
followers traverse the no-fast-travel world across camping nights.
- Formation/follow distance numbers and re-form rules after combat?
- The revive channel: duration, interrupt rules, failure consequence?
- How do followers interact with camp saves and the mourning system state?
- What is the follower AI budget (four actors on the enemy grammar)?

G21. TRANSFORMATION BODIES AND GEAR TRANSFER
22-quests-factions-gdd-part3.md locks three strains; doc 29's KNOWN
ISSUES notes bodies are region sub-meshes for equipment slots. No doc
owns the strain bodies' visual canon, the quadruped Hunter's Sprint form
(21-quests-factions-gdd-part2.md), whether and how gear transfers across
the strain states (26-A gap 13 carried), or strain-specific animation
sets (Pounce, The Elder's Shape).
- Strain body canon sources and who authors the wolf quadruped?
- Does gear hide, store, or transform per strain, and what of grave-goods rules?
- One rig per strain or overlay skeletons?
- Slice-deferrable, but the sub-mesh body build (G5) should not foreclose it.

G22. MOUNTS
02/03 lock sprite mounts (now 3D mounts), travel speed only, no mounted
combat. No doc owns mount acquisition, mount types per faction/biome,
speed numbers vs the locked travel-time math (doc 03 distances are priced
in "mounted" hours), mounting/dismount rules (doc 04 has a Dismount
technique), or mounted inventory/stash interaction.
- Mount roster and acquisition routes?
- Speed values that honor doc 03's traversal math?
- Dismount/Stable rules at towns, camps, and dungeons?
- What happens to a mount's body when the rider is a wolf (Hunter's Sprint, doc 21)?

G23. PERFORMANCE BUDGET
26-A gap 14 flagged the missing runtime budget for hundreds of billboard
sprites; the 3D pivot changes the load (skinned meshes, sub-mesh stacks,
fog/volumetrics per doc 02's pillars). No perf target exists to validate
the slice against.
- Target resolution, framerate, and hardware floor?
- Draw call/actor budgets for towns, sieges, and the demon invasion?
- Fog + dither + grain post-process cost envelope?
- What is the slice-1 perf test and its pass bar?

G24. PROCEDURAL DUNGEON GENERATION SPEC
03-world-design.md locks persistent procedural interiors with "authored
rules per type". No doc owns the generator: layout archetypes, room/curve
grammar, key-and-lock logic, hazard and shrine placement, boss room
placement, or the persistence data model for a generated layout.
- Layout archetype list per dungeon type?
- Generation constraints (guaranteed exits, Chest/boss density)?
- What is saved: full tile set, seed, or entity deltas?
- How do doc 06's dungeon-type loot keys wire into generation?

### CAN-DEFER severity (post-slice, but must be owned eventually)

G25. WORLD LEDGER DATA MODEL
20-quests-factions-gdd-part1.md defines the Ledger conceptually (war
momentum, debt tension, parish meters, deed log). No schema doc exists:
state fields, update triggers, and query surfaces. Needed before quests
GDD implementation, not before the combat slice.
- Field list and update owners per Ledger entry?
- What granularity of deed log is recorded (per kill or per category)?
- Save/load implications (overlaps G13)?
- Who arbitrates conflicting writes (conquest vs quest vs axis)?

G26. TISSUE QUEST GENERATOR AUTHORING
The frame grammar and 8 templates are locked (20, 21). The generator's
data needs are unowned: patron pool per hold, site pools per frame,
resolution axis wiring, personal-axes content, consequence tag
vocabulary, and expiry tuning. This is the quests GDD's own workload;
listed so it is not assumed to exist.
- Patron pool size and secret distribution per hold?
- Consequence tag vocabulary and its Ledger mapping?
- Per-template content lists (sites, needs, rewards)?
- Does the frame library expansion schedule exist?

G27. WARP CAMP PLACEMENT AND BUILDING TECH
11-warp-camp.md's engine note flags base-building placement as a
significant UI/render feature. Placement rules (open-space rule),
foundation/terraform behavior, structure snap or freeform, raid-time
defense AI wiring, and camp-in-world persistence are undesigned.
- Placement validation rules concretely (slope, overlap, biome gates)?
- Snap/grid vs freeform, and relocation teardown semantics?
- How camp defenses run without the player present?
- Defer past slice 1, but doc 09's camp system needs a simpler subset answered first (G13).

G28. LANTERN AND LIGHT MECHANIC
The register makes light scarce and diegetic (02, 24); torches are
craftable (05); the lantern is the player's key light in every frame. No
doc rules on whether light is a MECHANIC (fuel, burn timers, darkness
penalties, doc 03's cold/exposure texture) or purely presentation. This
silently changes stealth (G19), night danger, and camping balance.
- Is there a light/visibility mechanic at all, and does the lantern burn out?
- Do darkness stealth bonuses exist, and how do they read under G19's model?
- Cold/exposure: is "cold exposure over the clock" (doc 03 mountains) a mechanic or flavor?
- One ruling closes this; it must be Nicko's.

G29. AMMO ECONOMY
05-crafting-system.md makes arrows/bolts batch crafts and payloads
Alchemy products; Archery is one of nine combat lines. No doc defines
ammo: quiver capacity, retrieval of spent arrows, payload application
flow in and out of combat, or crossbow bolt distinctions.
- Quiver/ammo slot rules and stack sizes?
- Arrow recovery rates and payload application UX?
- Does ammo scarcity bind carry weight into ranged builds (intended?)?

G30. BOSS AND COLOSSAL TREATMENT
26-A gap 10 carried into doc 28's open items (boss-scale camera). Still
unowned: boss framing, multi-part or oversized model handling, arena
design grammar, boss-only telegraph conventions, and the boss remix rule
(G9). Needed before the first boss, which is plausibly in slice 1.
- Boss camera register rules vs a 10-meter body?
- Arena grammar (space, hazards, doc 04 zone denial kits)?
- Signature-spell authoring rules per doc 17's boss caster model?
- Is there a slice-1 boss, and which pool does it teach?

G31. NAMED-CHARACTER PRODUCTION UNDER THE 3D CARRIER
25-art-pipeline.md's LoRA consistency problem and 26's lesson L5 were
sprite-side. Doc 29 demoted the sprite pipeline; the named-character
path for MESHES (the Tight Nine, thrones, Signer) is unowned, as is the
human-gate throughput model (26-A gap 16).
- Consistency method for named characters as meshes?
- Human approval gate throughput for a full cast?
- Which named characters exist before the slice (possibly none)?

G32. TITLE IP CHECK
01-vision-high-concept.md's standing open question: "Witch Hunter"
collides with existing IP in the genre. Tracked in 08; unresolved. Cheap
to resolve, awkward to defer past any public artifact.
- Search/filing status?
- Decision point before any public-facing use of the title?

G33. OPTIONS, ACCESSIBILITY, AND LOCALIZATION
Nothing in the doc set addresses accessibility (colorblind support under
the one-accent law, subtitle/camera-shake options), difficulty modifiers
inside the fixed-difficulty lock, or language support. Not prototype
work, but the one-accent law and camera-shake combat feedback (doc 04
bake-in) make two accessibility decisions design-coupled.
- Colorblind strategy for accent-critical threat reads?
- Camera shake/hit-stop intensity options?
- Are difficulty modifiers non-goals (doc 04's fixed-difficulty lock suggests yes, but say so)?
- Any localization ambition at all?

## Prototype readiness verdict

The doc set is unusually deep on systems, world, lore, and art direction,
and it is now self-consistent about the carrier (doc 29). It is NOT
sufficient to start a combat-loop vertical slice. The moment-to-moment
loop has no owned specification: input binding (G3), camera completion
(G4), the player model and its animation set (G5), equipment mechanics
(G6), damage formulas (G7), enemy AI (G8), enemy data (G9), and combat
frame data (G10) are all referenced by locked decisions but owned by no
doc. G1 (slice scope) must come first because it sizes everything else.

Minimum path to prototype readiness, in order: lock G1 (slice scope),
then one session owning G3+G4+G10 (the controls/frame-data pass that
completes doc 28), one session owning G6+G7 (the equipment and formula
pass that extends 27-equipment-visual-system.md into a mechanical doc),
and one session owning G8+G9 (the enemy AI and bestiary pass that extends
04-combat-system.md), while doc 29's remaining pipeline stages (G2) and
the player body (G5) are proven in parallel. G11 through G15 are needed
during the slice; G16 onward can trail it. Nothing in this doc is LOCKED
or RESOLVED; all of it awaits Nicko's review.