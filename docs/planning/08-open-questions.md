# 08 - Open Questions Tracker

Running list of every open decision across the planning docs. This version
is the POST-CONSISTENCY-PASS state (2026-09-11): all resolved items are
grouped and compressed; remaining opens are explicitly assigned to a
future pass (dedicated session or GDD stage). This tracker is the master
checklist for "no holes or gaps."

## RESOLVED (decisions with specs in their docs - summary list)
1. Continent scale/authoring: hand-shaped landmass, hand-authored
   overworld, procedural persistent interiors only; 20-30 holds, each a
   real place (03, 13).
2. Dungeon persistence: saved once generated (03).
3. Death penalty: souls-drop recoverable at corpse (04).
4. Healing: potions + mid/late healing spells; tavern saves; camp saves
   (04, 09).
5. Stats: NINE (Health, Stamina, Focus, Carry Weight, Precision, Ward,
   Speed, Luck, Wisdom); 5 points/level (07).
6. Skill lines: 29 core (9 combat, 5 magic, 5 crafting, 6 gathering, 3
    utility/social, 1 salvage) + specialty expansion upward (15).
7. Skill mechanics: ranks 1-100 by use, 5 tiers, permanent technique
   choices (2-3 options), diminishing curve after 50, no decay, no
   respec, gear gates by tier (18).
8. Art: 512-1024px hand-drawn sprites, 4-8 frames/anim, Souls-style UI,
   portrait dialogue, all-2D props, sprite mounts travel-only (02, 08).
9. Camping: tiered gear, overworld only, sleep = day restart, gear
   breakable in ambushes, warp camp = default forward respawn (09, 11).
10. Cooking: 5 grades, campfire=3 ingredients/kitchen unlocks grading, no
    spoilage, knowledge-gates-attempt + skill-gates-magnitude (10).
11. No item repair; items permanent (05, 08).
12. Day/night: affinity-relative clock; good fears night, evil fears
    daylight sleep, neutral plays the good clock (03, 12).
13. Warp camp: 4-day summon cooldown, relocatable after cooldown,
    one-time hire cost, no fast travel, defenses actively fight,
    one camp per character, default forward respawn (11).
14. Conquest: trigger-driven, off-screen resolution, background slow-burn
    war tipped by player, regicide-with-heirs rule, alternate routes
    (defense destabilization, famine), comeback events (demon summon /
    divine prayer), reconquest + procedural nobility + land grants
    (13, 14).
15. Two Thrones + Three Courts: light/dark/neutral courts, Two Thrones
    crowns, Allegiance Gambit (3 denials each), Third Path true ending,
    NG+ rules incl. tilt (12).
16. Moral axis: single visible axis on character screen, emote/pose
    unlocks, affinity-relative presentation (11, 12, 02).
17. Specialties: combination-unlock titles, 2-4 stack, lapsable rules
    (standing-conditioned lapse, historical/skill permanent, apex
    titles permanent), condition-transparency UI requirement, apex
    specialty content gates (16, 17).
18. Magic: five schools, spell lists locked (48 spells + 6 hybrids + 2
    corruption kits), acquisition Option B, taint meter, corruption
    kits, Aegis rule, apex magic titles (17 - parallel session).
19. Nodes respawn 2-3 days; fishing full skill line; Hunting/Skinning
    sixth gathering line; grave-looting costs light reputation (06).
20. Marriage race-shift, player house = character name, lore rights to
    banner creation on first conquest grant (14).

## REMAINING OPEN - assigned to future passes
### Dedicated sessions (next)
- COMBAT/CRAFTING/LOOT deep-dive (next session, Nicko-directed): combat
  move-set/technique menus in full, crafting station quality tiers,
  utility-crafting mapping (fletching/lockpicks), loot table design,
  rarity-vs-tier item economy, vendor economy depth. Docs 04-06 are
  consistency-passed; this session designs the depth.
- MAGIC SESSION (running in parallel): doc 17 open questions (spell
  tuning details, enemy caster kits, summon caps) - owned by that
  session.

### Quests/Factions GDD
- Alignment thresholds (tier ladder tuning), multiple alignments within
  a court, alignment ceremony/rewards, axis drift vs deed-lock,
  double-agent playstyle integration with the Gambit (12).
- Hold defense mechanics (defend quests, garrisons, retinue deployment);
  neutral-court war profiteering arc (13).
- Specialty catalog completion + apex chains for good/bad/neutral (16).

### World GDD
- Biome safety by alignment: RESOLVED 2026-09-12 (Nicko, doc 03):
  per-biome clock weight + home affinity frame; blight = passive
  attrition for good/neutral, wolves immune to ambient penalty;
  daylight-sleep grounds for evil players = blight + dark-flipped
  farmland only.
- Blighted zone count and map placement (relative to the pre-Fall
  ruins): RESOLVED 2026-09-12 (Nicko, doc 03): THREE SCARS (Core
  ~10 km2 at the Spire + Moor March scar + Darkwood-Eaves scar,
  ~20 km2 total); HYBRID dynamics (fixed hearts, war-breathing
  edges read on the map); cleansing = Red Vigil temporary +
  ONE cleansable satellite scar via light-court spine questline;
  Core + Darkwood scar permanent until total domination.
- Witness-tier NPC list (who alive remembers the Fall): RESOLVED
  2026-09-12 (Nicko, doc 03): THE TIGHT NINE roster (8 named
  witnesses + the Debt's Echo place-NPC + 2 texture anchors:
  War-Father Ghash, Half-Face). Grudge rule REFINED: grudges take
  only if the murder was witnessed. NEW LOCKED SYSTEM: THE PURGE
  OF MEMORY (both courts' witness-assassination questlines;
  assassinations close personal quest keys, feed purge standing,
  and harden the survivors).
- Per-biome ingredient category member lists (doc 05 sub-item):
  RESOLVED 2026-09-12 (Nicko, doc 03): full per-biome lists written
  (commons + signatures per biome, reagent spawn densities,
  blight-spawn rules incl. no Holy spawns + Red Vigil Holy window,
  wolf blight-harvest note). Remaining sub-items stay GDD tuning
  (reagent step-count, refining bonus scope).
- Race-origin deep detail (dwarven altar-masons, coven
  Veil-Altar-tender prehistory): RESOLVED 2026-09-12 (Nicko,
  doc 03): doc 22 sketch locked + map grounding (massif = old
  quarries, Darkwood glades = old altar-gardens) + DEEP ALTAR
  DEDICATION locked: built down-deep to the world's own deeps,
  never a throne instrument; true ending = returning the world
  to itself. Werewolf wild-strain dens pool at all three altar
  ruins' edges (broken wards).
- Named-storm authoring + Veil-Tide front cadence numbers: STORMS
  AUTHORED 2026-09-12 (Nicko, doc 03): Red Vigil (sun-storm,
  burns scar edges, required rite for the Moor March cleanse),
  Pale Tide (moon-fog, lifts blight drain, wakes wild strains,
  stacks full moons), Storm-Calls (dark siege-prep ritual,
  pins Veil fronts, counterplay = anchor sniping). CADENCE
  LOCKED 2026-09-12 (world GDD tuning): season = 21 in-game
  days, fronts change every 2-4 days, Vigil 6 days / Tide 5
  days, once per season each.
- In-game day length ratio (24:1 vs 48:1, even halves locked):
  RESOLVED 2026-09-12 (Nicko, world GDD tuning, doc 03): 24:1
  LOCKED (1 in-game day = 60 real minutes, even halves: day
  30 real min, night 30 real min).
- Neutral court across both throne territories: RESOLVED 2026-09-12
  (Nicko, doc 03): THE SHADOW COURT, outlawed in both realms,
  secret dens, purge questlines, city battles on provocation;
  elders prefer stalemate (deep spine reveal).
- Name pool depth, heraldry generation, clan lifecycle depth
  (13, 14): RESOLVED 2026-09-12 (Nicko, doc 03): stem-assembly
  names (vampire decay by age tier, player names propagate),
  charged-shields procedural heraldry grammar (player banners
  same grammar), six-state house lifecycle (Rising/Established/
  Ascendant/Declining/Exiled/Extinct).
- Weather gameplay: RESOLVED 2026-09-12 (Nicko, doc 03): the
  VEIL-TIDE front system locked (three charge states, bite on clock
  edges/patrols/school flavor only, no new resources). Named storms
  (Red Vigil, Pale Tide, Storm-Calls) = design intent, authoring +
  front cadence numbers at GDD stage.
- Continent physical size: RESOLVED 2026-09-12 (Nicko, doc 03):
  ~10 x 13 km playable (~130 km2), ~25 holds, ~2.3 km settlement
  gaps. New dependent opens: exact in-game day length (24:1 vs
  48:1, even day/night halves locked); fast-travel removal
  downstream checks (doc 09 camping balance, doc 11 warp camp
  role, retinue errand ranges).

### Retinue/Base GDD
- Retinue cap by tier (11): retinue GDD item.
- Faction reaction to fortified camps (11): quests/world GDD item.
- EXPEDITION FOLLOWERS (doc 23, 2026-09-12, FULLY RESOLVED by
  Nicko except UI/tuning): 4 types (BARD / SQUIRE / GUARD /
  ARCANIST, own behaviors); slots LOCKED 1/2/3/4 at levels
  1/10/20/30; command grammar; FOLLOWER XP (own levels, shared
  party stream) + FOLLOWER MENU; PERMADEATH + CAMP MOURNING
  (pairwise affinity grief, blame mechanics, memorials;
  MOURNING PERIOD = 14 IN-GAME DAYS); BARD POOL AFFINITY-KEYED
  (good = protection buffs, evil = damage + elemental weapon
  coatings, neutral = travel kit; bards befriended/recruited
  from taverns + world locations; type list = GDD tuning);
  NO MEAL UPKEEP. Open: bard type list + per-song numbers
  (tuning), follower UI (art/tech), romance buffs (retinue
  GDD), XP share (tuning).

### Cooking GDD
- RESOLVED 2026-09-12 (Nicko, doc 10 GDD session): WARD-DISH
  GRAMMAR locked (biome signature dishes counter that biome's
  threats; attack = monster parts vs enemy grammar, defense =
  herb signatures vs ambient threat); ~43 per-biome dishes
  authored incl. enemy lists per biome; RARE BONUS POOL locked
  (10 first-pass effects); TAVERN MEALS locked (cheap WELL-FED
  convenience tier). Veil-Tide meal interaction (+1 grade roll
  on Veil-charged fronts).

### Craft depth: Workbench + Camp customization (LOCKED 2026-09-12,
### Nicko, spec in doc 05)
- THE WORKBENCH: sixth station, the REFINING HUB (supplies:
  leather/lumber/ingots/cloth/fittings/pigments/purified
  reagents; line-stations stop refining); ALL-CRAFTABLE
  PRINCIPLE (everything except Hunter's Relics + spine items);
  8 decoration categories (rugs/trophies/furniture/lighting/
  banners/shrines/defenses/structures); DECORATION PRESTIGE
  ladder resolves doc 11 Q8 (rest quality +morning buff hour,
  greeting scale, safe-zone deterrence, +1 grade roll on
  camp-brewed meals/potions at Masterwork decor, retinue
  tolerance). TROPHY BUFFS LOCKED: apex-beast trophies grant a
  small permanent camp-wide buff vs that beast family while
  displayed. HERALDRY on camp items = OPTIONAL display (Nicko
  "if chosen to").
- NO ESTUS FLASK: health/mana potions are crafted STOCK
  (carry-weight-limited), intensity = Alchemy skill tier (floor)
  x station tier (ceiling); stamina potion CUT (food/rest owns
  stamina). THE MORNING RITUAL: one daily prep potion taken with
  the morning meal (the doc 10 drink slot): offense bane
  draughts (monster parts, enemy-grammar keyed) or defense ward
  draughts (herb signatures, biome-threat keyed). BANE GRAMMAR
  locked (mirrors ward-dish). Four families: Healing+Mana stock /
  Daily Prep / Coatings+payloads / Throwables. Alchemy station
  ladder = doc 05's 5 tiers at the bench; legendary station
  brews the two T5 potions. Same doc 03 ingredient pool as food.
  Open: T5 recipe discovery routes (quests GDD), numbers
  (tuning).

### Art/Tech Plan
- Sound and music direction (no doc yet).
- Rare-node UI hint (glint vs observation); cutscene format (02).
- Unreal: sprite pipeline validation, base-building placement system,
  player-authored banner/heraldry UI (02, 11).

### Tuning (GDD-stage, not design holes)
- XP budget per level; stat-point caps; stamina/regen rules; parry
  windows; raid/thief encounter rates; axis
  threshold numbers; summon-cap numbers for summons (04, 06, 12, 17).
  RESOLVED 2026-09-12 (world GDD tuning, doc 03): node density
  (moderate, doc 06), in-game day ratio (24:1), Veil-Tide cadence
  (doc 03), reagent ratio + refining bonus scope (doc 05).

### COMBAT/CRAFTING/LOOT SESSION ADDITIONS (2026-09-12)
- Combat technique menus: COMPLETE AND LOCKED (see decision 40, doc 04).
- Crafting depth: COMPLETE AND LOCKED 2026-09-12 (doc 05): craft quality
  FLOOR/CEILING model (skill tier = floor, station = ceiling); 5 station
  tiers (Field Kit/Village/Town/City/Grandmaster); crafted GRADE ladder
  (Crude/Standard/Fine/Superior/Masterwork, Masterwork = +1 socket);
  utility mapping (arrows/fletching/torches/lockpicks = Weaponsmithing,
  payloads/throwables = Alchemy); recipe economy (biome-keyed loot,
  tier-gated attempts, reverse-engineering with named items excluded,
  materials set tier, axis-gated recipes burn); Aegis gear EXCLUSIVE
  faction asset (deep-good craftable only, no NPC service); ONE legendary
  Grandmaster dungeon station, never mapped, found only via cumulative
  redundant clue chains (Grave Whispers on dead smiths, tavern rumor/
  purchased intel, dungeon journal finds) - no quest marker.
- New open question: legendary station clue-chain content (fragment
  lists, which graves/NPCs/dungeons carry clues): quests/world GDD.
  OWNERSHIP: world GDD (doc 03 session) carries the biome-side of
  clue content; quests GDD carries the chain structure.
- New World ingredient-system adaptation (doc 05, LOCKED 2026-09-12,
  Nicko "for now"): recipes = 1 tier-locked primary + 2-3 category-filled
  secondary slots (rarer secondaries shift the grade roll); refining
  layer with catalysts and station-tier caps; five arcane reagent ladders
  (Mote/Wisp/Essence/Quintessence, Fire/Frost/Storm/Holy/Dark, Holy and
  Dark axis-gated); Hunter's Components (rare finds that guarantee one
  specific enchant, the player's hand on the enchant dimension);
  explicitly NOT adopted: Trading Post, Azoth, town-project stations.
  Sub-items assigned: per-biome category member lists = world GDD;
  reagent combining ratio and refining bonus scope = GDD tuning.
- LOOT ECONOMY (doc 06, LOCKED 2026-09-12, Nicko): four-layer
  tables (monster parts / materials / gear / special slot with court
  overlay and dungeon-type keys); Rarity-vs-Tier CROSSING RULE (low-tier
  gear spans all rarities, T4 = Rare+Named only, T5 = Named only,
  always story-attached); three vendor families (light/dark/neutral
  brokers) + requisition contracts paying standing; Hunter's Relics
  (hand-authored Tier-5 named items, ~9 weapon + ~6 armor/charm,
  fixed acquisition stories, Reforge-only). Sub-questions: table
  weights = GDD tuning; relic authoring = GDD content; broker intel
  delivery = quests GDD; reverse-engineering rates = GDD tuning
  (doc 05).
- COMBAT FEEL RULES (doc 04, LOCKED 2026-09-12, Nicko):
  poise/stagger as universal resource (pools by armor/size not level,
  chip poise through blocks); parry windows by source (shield widest >
  Riposte Master > Twin-Parry > shaft > bare blade, narrow windows =
  bigger punishers, only soldiers parry); stamina rules (1s regen
  pause after actions, reduced regen while blocking, stamina-break at
  zero, EQUIP LOAD roll-speed bands light/medium/heavy); enemy grammar
  (same verbs as player; beasts no block, undead no dodge/parry;
  light-court soldiers fight in shield-spear PAIRS, dark-court as
  bleed PACKS; paladins cast Holy Wards grammar, vampire/undead
  raiders use corruption kits incl. The Embrace on player retinue;
  court ambushes teach the Aegis counterplay). Sub-questions: exact
  numbers = GDD tuning; equip-load bands = GDD tuning.
- LORE SPINE: THE FALL OF THE VEIL THRONE (NEW doc 19, 2026-09-12):
  LOCKED: Solar Throne core myth, the debt/Undertow (dark court out of
  credits, reunification as sacrifice supply), demon invasion = debt
  default, the Undersovran as contracts-and-sigils-only specter, the
  Long Agency (living-memory witnesses), the Third Altar (Deep Altar =
  true ending mechanism, six refusals = qualification). ALSO LOCKED
  (second round, doc 19): SCHISM SECTS (sub-alignments, resolves doc
  12's multiple-alignments question: Militant/Mercy light, Old Blood/
  Veil Faithful dark, parish-flip world state); RELIQUARY WARDENS
  (underworld questline faction, relic authentication, leader THE
  SIGNER); THE HIDDEN COURT (underworld's secret werewolf sect, the
  Signer's ace, player lycanthropy questline proposed). HIDDEN COURT
  LORE REVISITED (Nicko ruling, 2026-09-12): werewolves ARE a
  corruption race/class, third alongside Vampire and Undead (doc 17
  kit model): the bite converts the living to fill the Court's
  ranks; the difference is ALLEGIANCE, the wolf strain is NEUTRAL,
  beholden to neither throne, the corruption race of the
  neutral/Third Faction; the Undersovran holds no claim on it,
  neither court can command it; the Court converts rarely,
  deliberately, by its own law, wild strains spread carelessly (the
  world's feral wolves); Holy Wards hurt wolves only when they hunt
  you, not on sight. New opens
  assigned: debt's visible payment schedule (quests/factions GDD),
  demon invasion scope (doc 13 GDD), Third Altar locations (quests
  GDD), witness NPC list (world GDD), werewolf questline mechanics
  (locked in doc 20), the Signer's ace triggers: RESOLVED 2026-09-12
  (doc 19/21: debt default or Third Path crisis, not player-earned).
- QUESTS/FACIONS GDD PART 1 (NEW doc 20, 2026-09-12, LOCKED
  structure): two-tier architecture (spine vs tissue), the World
  Ledger (quests react to simulation state, never random), frame
  grammar with PERSONAL AXES (princess/dragon texture: willingness
  keyed off HOW the need was resolved, 2-3+ endings per tissue quest
  that differ in personal/retinue/standing reward, not necessarily
  world state), expiry fails-forward, parish-flip rules (locked,
  weights tuning), wolf trial six stages, WOLF LADDER (full second
  form with its own doc 18 ladder, Nicko locked), debt hidden until
  discovery arc, progression safety rules (spine immunity, debt fuse,
  threshold triggers, NPC promotions). RESOLVED 2026-09-12 (Nicko):
  frame library first pass = 8 templates (hunt, escort, clear-site,
  defense, supply, curse-lift, relic-hunt, parish-work), expanded
  later; wolf kit = four-ability kit (doc 21); wolf axis tension +
  wolf clock resolved (doc 19); Signer's ace triggers resolved (doc
  19/21).
- QUESTS/FACIONS GDD PART 2 (NEW doc 21, 2026-09-12): wolf kit
  RESOLVED (four-ability kit per Nicko, doc 17 corruption-kit model,
  SUPERSEDES the 36-menu ladder; Hunter's Sprint / Pounce /
  Terrifying Howl / Elder's Shape; doc 21 wolf-kit section now
  carries the RESOLVED ruling); spine outlines PROPOSED (allegiance
  chains, the Gambit six-denial line, Third Altar path incl. the
  Signer crossover, debt discovery arc, wolf post-transform, the
  Signer's Unsigning chain, demon invasion event chain);
  progression-safety addendum (spine unlocks by threshold,
  spine-only endgame gates, all spine chains have continue-the-game
  failure states). Resolved this session: wolf axis tension
  (hunt-any-during-moon), wolf player clock (inverted, night safe),
  Unsigning costs (the Signer herself; the realm pact is
  un-unsignable), Signer's ace triggers (debt default or Third Path
  crisis, not player-earned).
- QUESTS/FACIONS GDD PART 3 (NEW doc 22, 2026-09-12, PROPOSED
  awaiting Nicko): transformation lines for VAMPIRE (The Suitor's
  Season, six stages: Noticing/Season/Ledger of Gifts/Embrace/First
  Tithe/Court's Welcome) and UNDEAD (The Necro-Arrangement, six
  stages: Rot's Bargain/Arrangements/Dose/Death/Rising/First Deed,
  the paperwork-and-grave-planning texture); Human Center Principle
  (one human can become every strain; one strain at a time;
  switching via death-shaped exits, Mercy as the only backward path
  to human, IO proposal); PRE-FALL WORLD sketch (Age of the Sun:
  death was final; race origins: elven split, human backbone,
  dwarven altar-masons, orc legion-breed, undead nonexistent before
  the Fall, werewolf origin options a/b/c with IO lean b (Deep
  Altar's wardens), covens as Veil Altar's first tenders). Open:
  stage-by-stage detail (quests GDD authoring), rot-window tuning.
  RESOLVED 2026-09-12 (Nicko, second pass, doc 22): switching =

  death-shaped exits only, no stacking; backward path = NONE, no
  cure exists, Mercy-switchboard proposal superseded; wolf origin =
  option B (Deep Altar's wardens, wolf den = altar threshold); wolf
  player clock = INVERTED (night safe, day dangerous); strain
  re-take = allowed but costs the exit event each time; orc origin
  = REVISED to the Devil's early creation per the Great Cities
  ruling. Remaining open (authoring/tuning): vampire/undead
  stage-by-stage detail (quests GDD); race-origin deep detail
  (world GDD); rot-window tuning (GDD tuning).

    - WOLF LADDER (doc 21, 2026-09-12, first-pass anchors PROPOSED):
      12 of 36 menus drafted (Pounce/Hunter's Sprint/Bloodhound, Terrifying
      Howl/Wilds' Silence/Shepherd's Nose, Ravening/Moon-Fed/Long-Legged
      Night, Elder's Shape/The Den's Door/Grandfather's Voice); menu
      differentiator = HUNTING DOCTRINE (pack-hunter vs lone-terror vs
      moon-cultist); Hidden-Court-trust gating remains IO proposal for
      review; remaining 27 techniques to next technique session.
      REVISITED 2026-09-12 (Nicko): wolf = FOUR-ABILITY KIT (doc 17
      corruption-kit model, Hunter's Sprint / Pounce / Terrifying Howl /
      Elder's Shape), not a 36-menu ladder; see doc 21.
- SPINE QUESTLINES OUTLINED (doc 21, PROPOSED): allegiance chains
  (3-5 beats each; short because standing unlocks the real content),
  the Gambit line (six escalating denials, then the underworld
  opens), Third Altar path (five beats incl. the Signer's Confession
  crossover), Debt Discovery arc (five beats ending at the
  bankruptcy the player uncovers), wolf post-transform content, the
  Signer's Unsigning chain (IO proposal parked: it costs the player
  the Signer), demon invasion event chain (portents/breach/choice/
  aftermath).
- PROGRESSION-SAFETY ADDENDUM (doc 21, PROPOSED): spine chains unlock
  by threshold; spine is the only content that may hard-gate endgame
  power (apexes, Lich King); every spine chain has a failure state
  that continues the game (a failed court line closes that court's
  unique rewards, never the game; failed wolf trials retried after a
  season).
- New open items: RESOLVED 2026-09-12 (Nicko): wolf kit = four-
  ability kit (doc 21); wolf axis tension = hunt-any-during-moon
  (doc 19); wolf player clock = INVERTED (doc 19); Unsigning
  costs = the Signer herself, realm pact un-unsignable; Signer's
  ace triggers = debt default or Third Path crisis; frame library
  first pass = 8 templates (hunt, escort, clear-site, defense,
  supply, curse-lift, relic-hunt, parish-work), expanded later;
  invasion scope = N days of war, ends when a Great City falls OR
  the ritual site is destroyed; light comeback = the Blessed Host
  (paladin army for N days, monarch stays mortal); Hidden Court
  internal factions (parked, doc 21).

## RULES OF THIS TRACKER
- Nothing here is unresolved DESIGN; everything open is assigned.
- A new open question must be added here AND in its doc's open-questions
  section, with an assignment, at the moment it surfaces.
- The parallel magic session owns doc 17 and its questions; this tracker
  records only its conclusions.
- Engine note: Unreal target; the Unreal MCP integration is a tooling
  phase idea - validate actual capabilities before committing any
  workflow to it.

## ASTRABOT BAKE-IN (2026-09-13, from 26-astrabot-analysis.md)

### PROPOSED rulings (baked into docs 02, 04, 24, 25, 26, 27, 28 — pending Nicko lock)

Each is PROPOSED (Astrabot bake-in from 26-A analysis, 2026-09-13,
pending Nicko lock). One line per proposal:

- 16 directional views for the player and hero-tier enemies, 8 for
  ambient props/distant NPCs (doc 02).
- Per-pose frame budgets: 8 for attack wind-ups/staggers, 4 for
  idle/walk (docs 02, 04).
- Mandatory telegraph frame in every enemy attack stack, flashing the
  threat accent (docs 02, 04).
- Three camera registers: exploration/combat/aim, sprite resolution
  sized to combat (doc 28).
- Lock-on camera behavior: angular-velocity cap, view reselection hidden
  in hit-stop (doc 28).
- Logical facing rule for billboard combat arcs, defensive-pose view
  snapping (docs 04, 28).
- Roll direction: 16-view player recommendation, 8-view quantization as
  the stated alternative (docs 04, 28).
- Combat readability floor proposal: silhouette contrast target under
  night + Pale Tide, numbers at the UE5 spike (doc 24).
- Hostile rim-light boost, still diegetic (doc 24).
- Fog keyed to encounter state: recedes in locked-on combat (doc 24).
- Accent collision ranking: red > cyan > ambient (doc 24).
- Dithering ruling recommendation: painted first, shader only where
  painted cannot reach; final call pending (doc 24).
- Equipment silhouette QA as a qa_gate.py check (docs 24, 27).
- Combat animation cost model + prove-or-kill artifact gate (doc 25).
- Cloth flicker mitigation extended to combat poses (doc 25).
- Named-character LoRA costing/tooling/fallback carried open (doc 25).
- Human approval gate throughput model carried open (doc 25).
- New HIGH-priority human male/female body cards (doc 26).
- Human body canon dependency blocking the paper-doll player body
  (doc 27).
- RESOLVED 2026-09-13 (Nicko): carrier = TRUE 3D world, low-poly
  pixelated models. Billboard-specific items above stay in the docs as
  REFERENCE (palette law, QA methodology, lessons); the camera
  registers, readability floor, rim-light boost, fog-by-encounter, and
  accent ranking carry over to the 3D carrier unchanged. Pipeline
  validation plan: doc 29.

### NEW opens surfaced by the audit

All OPEN, none resolved:

- Vertical-slice scope definition (doc 01 open question, unassigned).
- UE5 spike priority + Unreal version (docs 00, 08, 26).
- Combat animation cost prove-or-kill (doc 25).
- Audio direction doc (no doc).
- UI/UX art direction doc (docs 02, 11, 13, 20).
- Mount visual system (docs 02, 03, 04).
- Transformation-strain sprite plan incl. gear transfer (docs 22, 26, 27).
- Boss/colossal sprite treatment (docs 04, 24).
- Runtime perf budget for hundreds of billboard sprites (doc 02 pillar 5).
- Cutscene format beyond portraits (docs 02, 08).
- Hold defense + specialty catalog sessions (already listed above,
  confirm cross-ref).
- Rembg replacement (tools).
- Title IP check (doc 01).

## ART-STYLE FORK (2026-09-13, Nicko)

Nicko opened the carrier question: 2D billboard sprites vs low-poly
pixelated 3D models (PSX-style retro 3D) under the same locked
painterly-pixel register. RESOLVED 2026-09-13 (Nicko): TRUE 3D world,
low-poly pixelated 3D models are the carrier, register unchanged, all
concept art and sprite cards remain canon REFERENCE for world and
character creation. Decision record + converted 3D pipeline validation
plan: doc 29. The 16-view ruling below remains locked for spirit but is
superseded by the 3D carrier (a mesh has continuous facing); doc 28's
billboard-facing sections are demoted to reference. Carrier-agnostic
locks (camera registers, readability floor, fog-by-encounter, accent
ranking) carry forward. Spike blockers needing Nicko: a Meshy/Tripo
API key and engine access (a machine with UE5).
## HARD-NUMBERS PASS RULINGS (2026-09-13)

Seventeen live rulings by Nicko, 2026-09-13, on the hard-numbers pass
(docs 31-35). All LOCKED. Rulings 2-12 are doc 35 rulings and the
corresponding doc 35 open-question blocks are updated in place.

1. Roll i-frames: the docs 33/34 version wins. Equip-load bands (fast
   30f / 11 i-frames f12-f23 / 22 stamina; standard 37f / 6 i-frames
   f12-f18 / 26 stamina; slow 48f / 3 i-frames f12-f15 / 32 stamina;
   roll disabled above 30.0 load). Doc 32 section 4.2 rewritten to
   match (docs 32, 33, 34).
2. Damage numbers ON for player hits, OFF for incoming (doc 35 G11).
3. Focus bar hidden for non-casters, renders when Focus first becomes
   relevant (doc 35 G11).
4. Follower menu camp/tavern only at slice 1 (doc 35 G11).
5. Inventory capacity = 100 + Carry Weight x 2.5 (doc 35 G12).
6. Quest items in a zero-weight quest pocket (doc 35 G12).
7. Squire overflow scales with squire level: base +150 at level 1; the
   per-level increment is PROPOSED tuning at +15/level (doc 35 G12).
8. Dungeon-clear delta written only at the dungeon EXIT trigger, not at
   camp saves (doc 35 G13).
9. Currency: Silver Marks, single neutral currency (doc 35 G14).
10. Camp construction is the primary late-game money sink, no new sink
    doc (doc 35 G14).
11. One corpse on the field; the newest drop replaces the older
    permanently (doc 35 G15).
12. Death penalty: currency plus 25 percent of current-level XP (doc 35
    G15).
13. Two talisman slots: YES (doc 33 section 5).
14. Armor model: flat ladder plus percent cap as proposed (doc 33
    section 6).
15. Crit cap: 30 percent (doc 33).
16. Rot-Mother boss IN at slice 1; the M4 checkpoint can still cut it
    for scope (docs 31, 34).
17. Bestiary scope confirmed: Bandit 180 / Rot Wolf 140 / Grave Ghoul
    220 plus Rot-Mother 900 (doc 34).

Engine note in the same pass: Unreal Engine 5.8 LOCKED by Nicko,
2026-09-13 (doc 31 section 2; resolves the UE-version open item in docs
00, 08, and 30-remote-ue5-pipeline.md). Still open from these docs: doc
31 M4 live decisions, NG+ preserve-list (doc 35 G13), squire-overflow
save location (doc 35 G13), dark-vendor currency question (doc 35 G14),
camp-raid corpse edge (doc 35 G15), trigger-curve validation (doc 32),
GAS adoption gate and perf revisions (doc 31), bandit rout flavor and
Darkbread cue timing (doc 34), stamina-break window tuning (doc 33),
doc 30's unowned gaps G16+ (audio, dialogue, stealth, mounts, day-night
content, ammo, localization, accessibility).

## PALE QUEEN OPENS (2026-09-13, doc 36 lore session)

New open questions from the doc 36 lock session, all tracked in doc
36's Open Questions section with assignments:
1. What does the dark queen know about the creditor's identity
   (doc 36, lore GDD pass).
2. The Pale Queen's comeback-equivalent event (her desperate move,
   parallel to the dark court's bankruptcy ritual, doc 36, lore
   GDD pass).
3. The king's rescue path: breaking the dark magic early and its
   war-trajectory effects (doc 36, quests GDD item, doc 20 line).
4. What happens when the Signer learns her penance was for a
   framed crime (doc 36, quests GDD item).
5. The two queens' fates in the neutral real ending (doc 36,
   endgame GDD item).
6. Harvest mechanic depth: Mercy-harvest taint flow as world
   simulation meter vs fixed narrative resource (doc 36, quests
   GDD + lore pass together).
7. Whether the creditor's peasant name is ever learnable (doc 36,
   lore GDD pass).
Still open carried from docs 30-35: doc 31 M4 live decisions, NG+
preserve-list (doc 35 G13), squire-overflow save location (doc 35
G13), dark-vendor currency question (doc 35 G14), camp-raid corpse
edge (doc 35 G15), trigger-curve validation (doc 32), GAS adoption
gate and perf revisions (doc 31), bandit rout flavor and Darkbread
cue timing (doc 34), stamina-break window tuning (doc 33), doc 30's
unowned gaps G16+ (audio, dialogue, stealth, mounts, day-night
content, ammo, localization, accessibility).

## PALE QUEEN RULING PASS (2026-09-13, second session, doc 36)

All 7 original doc 36 opens RESOLVED by Nicko (rulings in doc 36's
RULING PASS section, verbatim): dark queen learns mid-ritual only
(her reaction is a live player-choice beat); comeback event = THE
LAST DANCE (pour 400 years of harvested taint through the Sun altar
to un-sin the world, a world where the elf king loved her); the
king's compulsion is permanent by design, no rescue, the choice is
which kingdom you leave him to; THE SIGNER IS THE PALE QUEEN (THE
PENITENT IS THE PEN: a 400-year alteration-magic mask inside the
Wardens, the penitent chancellor was invented, the unmasking is the
neutral ending's climax and the Wardens fragment is the trap she
built; doc 19 Signer section carries a supersession note; doc 19's
framed-chancellor premise is superseded); the neutral ending's fate
of the Pale Queen = THE HUNTER BECOMES THE LEDGER (mortal and
powerless after the engine breaks; the player's final choice is her
sentence: execution, exile, wardenship, or freedom); harvest depth
= FIXED NARRATIVE RESOURCE (story beats, no simulation meter);
peasant name = THE NAME IN THE GRAVE (learnable on an unmarked
grave she made for herself; speaking it aloud in the finale is the
one line that breaks her composure).

New opens from the rulings, tracked in doc 36's Open Questions
section with assignments: the Wardens after the unmasking (underworld
GDD pass), the Signer mask's operations needing re-derivation (doc 19
reconciliation pass), the neutral ending's sentence mechanics
(endgame GDD), the dark queen's mid-ritual consequence table (endgame
GDD), the Last Dance failure state (endgame GDD), and the grave site
(world GDD item).

## POP-UP QUEST OPENS (2026-09-13, doc 37 quest content pass)

New open questions from the doc 37 concept pass, all tracked in doc
37's Open Questions section with assignments:
1. Which hidden specializations beyond the undead graverobber enter
   the family first, and their mechanics (doc 16 follow-up, next
   specialties session).
2. Rumor-trap frequency and detection grammar (how often planted
   rumors appear, what telegraphs them): GDD tuning.
3. Bounty proof grammar details (trophy-specific vs generic part
   proofs, per enemy tier): GDD tuning.
4. Whether the dead can lie (working idea in doc 37: the dead cannot
   lie about their own life but can be wrong, and can be bound by
   whoever killed them): Nicko ruling.
5. Keeper mini-faction standing ladder and rite-service prices: GDD
   tuning.
6. Which 2-3 archetypes prove the frame grammar in the slice beyond
   THE LOST CHILD and THE NIGHT HAUNTER: slice scoping pass.
7. Quiet Parish keeper-catch consequences beyond standing loss (does
   the keeper remember across holds): world GDD pass.
Still open carried from docs 30-36: doc 31 M4 live decisions, NG+
preserve-list (doc 35 G13), squire-overflow save location (doc 35
G13), dark-vendor currency question (doc 35 G14), camp-raid corpse
edge (doc 35 G15), trigger-curve validation (doc 32), GAS adoption
gate and perf revisions (doc 31), bandit rout flavor and Darkbread
cue timing (doc 34), stamina-break window tuning (doc 33), doc 30's
unowned gaps G16+ (audio, dialogue, stealth, mounts, day-night
content, ammo, localization, accessibility), doc 36's six opens
(Wardens after the unmasking, Signer mask re-derivation, neutral
sentence mechanics, dark queen mid-ritual table, Last Dance failure
state, grave site).

## VENDETTA GRAVE PASS (2026-09-13, doc 37 second pass)

Resolved in this pass: doc 37 open question 4, whether the dead can
lie. RESOLVED 2026-09-13 (Nicko): THE DEAD CANNOT LIE, BUT CAN BE
WRONG. Testimony about their own life is always truthful but may be
mistaken; a bound dead can be compelled by whoever holds the binding.

New content: THE VENDETTA GRAVE (doc 37 Part 3) and its catalog twin
THE DEAD MAN'S JUSTICE (doc 37 archetype 25), baked 2026-09-13 from
Nicko's idea: assassination quests given by the bound dead, targets
random procedural NPC or heirless noble, heirless-noble kills cascade
through doc 13's regicide-with-heirs rule into hold Sundering and
capture. Doc 37 archetype count now 25.

New opens from this pass, tracked in doc 37's Open Questions section
with assignments:
8. Vendetta Grave spawn weights: what share of graves carry a
   vendetta, and the noble-without-heir draw rate (GDD tuning).
9. Whether the killer of a bound dead can be a spine NPC (spine
   immunity says NO for spine NPCs as targets; confirm the guard) :
   doc 20 progression-safety cross-check, IO to verify against doc 20
   SPINE IMMUNITY.

## OVERHEARD WORD PASS (2026-09-13, doc 37 third pass)

Two rulings locked (doc 37 Part 3b): THE UNKNOWABLE WEIGHT (vendetta
cascade unknowable in advance; heirlessness learnable only through
overheard conversation, never UI) and THE PRIVATE-CONVERSATION RULE
(NPCs withhold important lines when they detect an audience; stealth
becomes an information-gathering verb). New system: THE OVERHEARD
WORD, conversations as a stealth-reward economy. Wires into doc 30's
G19 stealth gap (reward economy requirement on the detection model)
and G17 schedules open (private conversations key off NPC routines).

New opens from this pass, tracked in doc 37's Open Questions section
with assignments:
10. Overheard Word audience-check tuning: detection radius vs speech
    volume bands, line-withheld vs conversation-defers behavior
    weights (stealth GDD, G19 owner).
11. Which world facts are Overheard-Word seeded vs rumor-tier only
    (heirlessness confirmed in-world; feuds, debts, illegitimate
    children proposed): world GDD pass.
12. Paranoid-speaker behavior: which NPC dispositions remember an
    eavesdropper and at what severity (deed log entry, grudge,
    hostile): G17 dialogue GDD.

## INTEL TIER PASS (2026-09-13, doc 37 fourth pass)

Ruling 6 locked (doc 37 Part 3b intel tier table): hold-toppling
facts are GUARDED (paranoid-speaker memory); heirlessness is PUBLIC
(common knowledge for common folk of a territory, Nicko's exception);
treasure and monster locations are GUARDED. DEAD-SPOKEN is the third
tier (undead graverobber only). 12 overheard quest seeds added as
working ideas in doc 37's quest-seed catalog.

New opens from this pass, tracked in doc 37's Open Questions section
with assignments:
13. PUBLIC-vs-GUARDED boundary cases beyond heirlessness (which other
    facts are territory-common vs guarded, e.g. famine scares,
    coven memberships): world GDD pass, per-territory tier table.
14. Overheard-seed spawn density: how many seeds per hold, per
    schedule slot, and their respawn rules (G17 schedules GDD).

## WARREN UNDER THE BRIDGE PASS (2026-09-13, doc 37 fifth pass)

Rulings 7 and 8 locked (doc 37 Part 3c, archetype 26 THE WARREN UNDER
THE BRIDGE): (7) MONSTERS HOLD GRUDGES AS FACTIONS trigger, goblin
kidnappers take the player ASLEEP, capture REPLACES the death penalty
for that ambush only (gear stripped to the hoard, recoverable, no
currency or XP loss; the game's first NON-DEATH DEFEAT STATE), (8)
the Goblin King is THE PETTY LEGALIST, toll-law trial, itemized debt,
work it off, dark comedy played straight. Job menu (7 jobs), escape
routes (5), and four endings (cleared ledger, escape, dead king, the
volunteer) baked as working content. Doc 37 archetype count now 26.

New opens from this pass, tracked in doc 37's Open Questions section
with assignments:
15. GRUDGES AS FACTIONS scope (Part 3c): which monster societies hold
    faction grudges and get capture mechanics (goblin warrens
    confirmed by RULING 7; Cold Widows, coven, marsh thing proposed),
    which are beasts that do not; capture-ambush grammar per
    faction: doc 34 bestiary + doc 04 cross-check.
16. Goblin warren map: warrens per region, which bridges have them,
    toll seed spawn rules (doc 03 world GDD pass).
17. The pit-gamble ruleset: GDD tuning.
18. Goblin King procedural or fixed per warren (doc 14 pools GDD
    pass).

## DESCENT GATES PASS (2026-09-13, doc 37 sixth pass, Part 5)

Four rulings locked: (9) descent gates are in-world physical doors at
dungeon ends, labeled with tier number and lock-tier by Warden
inspection; (10) one gate per dungeon, four escalating strata keyed
to character level 10/20/30/40, descended within the one opened
gate; (11) escalated layers drop better RARITY within the region's
fixed tier band (doc 06 crossing rule respected, tier band stays
regional); (12) full Part 5 baked with working ideas, opens logged.
Two keys per gate: LEVEL key or LOCKPICK key (Feel for the Pins
ladder); opened gates stay open for the playthrough. Deep Table
added (per dungeon type, layer 5 content: crypt founder's vault,
sealed mine vein, coven true altar, war camp command vault,
monastery reliquary-under-reliquary, warren below the king's hall,
blighted deep). Six working-idea additions in Part 5: Warden seal
grammar, rooms-not-numbers escalation, per-layer boss rule,
scavenger-spoils note, THE UNOPENABLE doors, the mislabeled door.

New opens from this pass, tracked in doc 37's Open Questions section
with assignments:
19. Layer generation grammar: strata reuse of base layout, per-layer
    archetype seeding (doc 03 + doc 31 G24 cross-check): world GDD.
20. Descent-gate density: which dungeon types carry gates, gates per
    cluster, named/special dungeon gate rules: world GDD pass.
21. The Unopenable door list: which spine/standing/quest keys open
    which Unopenables: doc 20/21 spine cross-check.
22. Warden door-inspection service: standing cost, availability: doc
    19 Warden GDD pass.
23. Layer-5 deep boss named-item guaranteed drops: GDD tuning.

## FACTION KEYS PASS (2026-09-13, doc 37 seventh pass)

Ruling 13 locked (doc 37 Part 5): faction keys. Buy a faction's key
from its vendor, use it on a descent gate, and the layers CHANGE
(different enemies, traps, unique loot per affinity). Key table
(working idea): Warden key (neutral, excavation, relic-signing
perks), Guild seal (light, sanctified purge, requisition attached),
Coven key (dark, coven nest, tithe fine print), Smuggler's tally
(neutral, economics only, changes what enemies GUARD). Affinity
gating per doc 12 vendor rules; crossing rule holds (ruling 11).
Claim rule proposed: keyed layers persist as faction claims until a
different key is used (the conquest system's smallest unit, doc 13
texture).

New opens from this pass, tracked in doc 37's Open Questions section
with assignments:
24. Faction key pricing and vendor availability per court family
    (doc 06 vendor economy + doc 12 axis-gating cross-check): GDD
    tuning.
25. Whether keyed layers stack with level strata (does a Warden key
    used at gate II change only layer 2-3, or the whole descent): GDD
    pass.
26. Faction-claim consequences beyond the claim rule (do rival
    factions react to your keyed floors, does the World Ledger track
    keyed dungeons as territory texture): doc 13 conquest
    cross-check.

## KEY TIER PASS (2026-09-13, doc 37 eighth pass)

Ruling 14 locked (doc 37 Part 5): three key tiers per court family,
gated at deepening affinity thresholds (friendly/honored/sworn, GDD
tuning). Each tier escalates differently: T1 baseline (excavation /
purge / nest / cache), T2 faction projects (Warden survey-hunt /
Militant crusade floor / coven ritual choir / underworld auction
house), T3 faction wars inside dungeons (contested site / war below
/ the court below / hostile takeover): close-quarters major-faction
battles, player fights for a side, loots the crossfire, plays double
agent, or (neutral only) owns the dungeon. Tier-2 gate proposal:
tier-1 floor cleared first under that faction. Tier-3 availability
seeded by war state (doc 13): the war leaks underground.

New opens from this pass, tracked in doc 37's Open Questions section
with assignments:
27. Exact affinity thresholds per key tier (friendly/honored/sworn
    bands, doc 12 tier ladder numbers): GDD tuning.
28. Tier-3 faction-war scaling: side strength vs war momentum,
    corridor-capture persistence between visits, respawn grammar
    (doc 13 + doc 34 cross-check): GDD pass.
29. Does clearing a tier-3 faction war dungeon write conquest state
    (does the winning faction's dungeon claim affect the hold above,
    doc 13 texture): doc 13 cross-check, IO reconciliation.

## REPLAYABILITY PASS (2026-09-13, doc 37 ninth pass)

Ruling 15 locked (doc 37 Part 5): 15A THE CLEARED-WOUND RULE plus
THE VACUUM RULE (destruction persists; new tenants colonize the
player's ruins: bandits, spiders, necromancers, wizards, squatters,
refugees, scavengers). 15B THE SITUATION SYSTEM (six dungeon
situations: OCCUPIED / INFESTED / ABANDONED-RECENTLY / CONTESTED /
CONSECRATED-DESECRATED / COLLAPSING; re-rolled on long timers,
readable from outside, rumor-reported). Design contract baked: four
layers (context / depth / faction / memory), four clocks, the same
dungeon is never the same dungeon. Six working ideas parked in doc
37 (ghost corpses, adapted denizens, dungeon economy, Veil-Tide
interiors, expedition format, dungeon-type specials).

New opens from this pass, tracked in doc 37's Open Questions section
with assignments:
30. Situation re-roll timers and transition rules (how often a
    dungeon changes situation, what triggers a change beyond timers:
    clears, war events, blight creep): GDD tuning.
31. Vacuum-tenant draw tables per region and dungeon type (which
    colonizers can appear where, doc 14 pools + doc 34 bestiary
    cross-check): world GDD pass.
32. Cleared-wound persistence budget (how much per-room destruction
    state the save blob carries, doc 35 G11 persistence
    cross-check): slice-systems pass.

## AUDIT RECONCILIATION PASS (2026-09-13, doc 37 third session)

Astrabot audits landed as docs 37-A (internal, 14 findings), 37-B
(cross-doc, 15 findings), 37-C (feasibility/slice-fit, 17 findings):
46 total. Nicko ruled on the five HIGH forks (RULINGS 16-20, verbatim
in doc 37 RULING PASS): slice 1 is combat-only (doc 37's slice subset
is a PROPOSED post-combat quest integration slice); revenants
deliberately deferred (slice dig uses the locked Grave Ghoul);
inhabitants-respawn-on-rest SUPERSEDED for doc 37 dungeons and
destruction commits at the exit trigger; misdirected vendettas are a
FEATURE (the comedy vendetta archetype: wrong killer up to three
times, arguing with a corpse by the second return); heirlessness is
PUBLIC, audience checks apply to GUARDED facts only.

IO reconciliation applied all 46 findings: HIGHs fixed inline, all
MEDIUMs resolved or assigned to owners (paid-intel tier interface,
door strata semantics, CONTESTED authority through the World Ledger,
claim-vs-occupation split, Named-vs-Relic exclusion, Warden
non-sovereign licenses, Vendetta cascade ruler predicate, spine
immunity filter, post-slice labeling, rumor MVP fixed patrons,
situation overlays on stable IDs, bounded wound budget, versioned
dungeon-state record, board lifecycle, fact versioning, capture
transaction, perception-gated subtitles), all LOWs fixed (catalog
entry 26 added, references corrected, broken sentence completed).
Doc 37's open list extended to 1-40. Full fix map in doc 37's
RECONCILIATION PASS section.

RESOLVED: doc 37 open 9 (spine immunity answers the vendetta target
question; doc 20's lock stands). Doc 37's open 12 and open 29 remain
open as spec assignments. New opens 33-40 logged above and in doc 37.

## INGREDIENT RECIPE MATRIX PASS (2026-09-14, doc 38)

Doc 38-ingredient-recipe-matrix.md baked (Astrabot, IO verified):
exact named ingredients + minimum station tier for every consumable
(2 stock potions, all 18 daily prep draughts, 6 coatings + 3 generic
payload tips, 5 throwables, the Cleansing Draught, the two T5
legendaries), 10 representative gear recipes with category
secondaries, and the 5 refining chains. Nicko's rulings this pass:
doc 38 = recipe matrix only, Hunter's Components catalog DEFERRED to
a separate later doc; consumables use EXACT named ingredients (not
category slots), the category-slot model stays gear-only; component
catalog size 12-16 agreed for when that later pass happens.

New opens from this pass (logged in doc 38 Part 4):
33. Monster-part names for the bane draughts and coatings
    (witch-fauna heart, wight-marrow, hag-bile, clatterer chitin,
    troll blood, thrall marrow, demon ichor) are PROPOSED pending
    Nicko; also review doc 38's recipe-fit exceptions (mountain
    herbs, blight defense bases, Farmwife's Cider): doc 38 pass.
34. Quantities per craft (how many moonbells per flask) and every
    PROPOSED minimum station tier: GDD tuning.
35. Whether consumables may later accept category-slot substitution
    (current ruling: exact names only, gear keeps category slots):
    GDD fork.
36. Hunter's Components catalog (12-16 guaranteed-enchant
    components with biome/monster sources): separate later doc,
    next crafting pass.

## GATHERING FORTUNES PASS (2026-09-14, doc 05 + 38)

Nicko requested drop/gathering-increase potions. Rulings locked in
session: gathering fortunes are DAILY PREP ONLY (a gathering draught
replaces that day's bane/ward, morning ritual unchanged), ONE PER
GATHERING SKILL LINE (six, doc 06), NODE-KEYED GRAMMAR (each key
ingredient is a byproduct of the resource it boosts, self-feeding
loop). No new potion family; the daily prep menu grows. Recipes are
loot per the locked recipe economy (undiscovered = not craftable).
Six working names + recipes PROPOSED in doc 38 Part 5. Byproduct
items (ore-dust, raw-gem chips, herb-tallow, sawdust paste,
render-fat, fish-oil) are PROPOSED additions to doc 06's gather
tables.

New opens from this pass:
37. Fortune percentages (drop-odds boost per grade, duration edge
    cases, byproduct drop rates themselves): GDD tuning.
38. Byproduct items' placement in doc 06's four-layer loot tables
    (which layer, which weights, do Luck techniques affect them):
    doc 06 pass, next loot touch.

## WEAPON TIER CATALOG PASS (2026-09-14, doc 39)

Doc 39-weapon-tier-catalog.md baked (IO, in-session): the full weapon
tier catalog and material sourcing stage. Nicko's four rulings locked
in session 2026-09-14 (verbatim intent in doc 39 SESSION RULINGS):
full 9x5 catalog now; named sources + weighted bands + anchor
percentages; gem drops scale with mining rank + Luck, gem tier gated
by vein depth and region band; doc 38 locked first.

New opens from this pass (logged in doc 39 Part 6):
37. Anchor percentages (A2 T4 dungeon drop weight, A3 war-camp steel
    share, G1-G4 gem base chance/rank curve/Luck/stratum gate): lock
    exact numbers or hand to GDD tuning: doc 39 pass.
38. Silver-as-T2 metal (doc 05's five-metal ladder maps 1:1 to
    T1-T5, silver at T2): confirm: doc 39 pass.
39. Named dual-wield pairs count as ONE relic slot against doc 06's
    9-relic working target: confirm: doc 39 pass.
40. The Aegis Bulwark as a CRAFTED (not dropped) T5 shield terminal
    item, deep-good exclusivity carries: confirm: doc 39 pass.
41. Gem names (Chip/Deep/Vein-heart/Veil Star families): working
    names pending Nicko: doc 39 pass.
42. Crossbow subclass existence (doc 33 Archery row assumes bows):
    unaddressed: doc 39 pass.

## WILDERNESS ENCOUNTER PASS (2026-09-14, doc 41)

Doc 41-wilderness-encounters.md authored (IO, in-session): the overworld's
notable encounter layer, the living gaps between holds. Nicko's three
rulings locked in session 2026-09-14: full concept doc authored now with
all eight families PROPOSED (doc 37 pattern, line-by-line review); site
state inherits doc 37's Cleared-Wound and Vacuum rules wholesale with a
light state readable from outside; density 8-12 notable sites per hold
region.

Parts: session rulings, conventions, density and distribution, Part 1
eight families (dens and lairs, hidden holy and tainted places,
wayfinding threads, road life, ruins and pre-Fall landmarks, riches
sites, one-off wanders, war scars), Part 2 site state (five overworld
light states), Part 3 per-biome family mixes, Part 4 discovery economy
(tier 0-3). Status: PROPOSED pending Nicko line-by-line review.

New opens from this pass (logged in doc 41):
43. Beast den repopulation vs habitat drift under the Cleared-Wound
    rule: where new dens come from, whether a species ever returns:
    doc 41 with doc 37 open 15.
44. Wayfinding site ownership (faction-claimable via conquest vs
    terrain-fixed neutral): doc 41 with doc 13.
45. Road-life spawn budgets and collision rules with doc 34 night
    ambush caps: doc 41 with doc 34.
46. Wanderer authoring pass (the 15-20 continent set pieces) at GDD
    stage: doc 41.
47. Blight wayfinding exception (one special shelter type vs
    provisioning as the whole answer): doc 41 with doc 03.
48. Witch hut pass additions (doc 41 Part 5, second pass 2026-09-14):
    the witch's name and exact discovery keys: doc 41.
49. The witch hut questline spine (what "played correctly" means,
    Old Blood storyline shape, failure states, resident-offer beat):
    parked for the quest GDD: doc 41 Part 5 with doc 20/22.
50. Resident-witch camp services scope (which vendor/teaching menus
    move into the warp camp when she joins): parked with the
    questline: doc 41 with doc 23/11.
51. Skeleton bard pass additions (doc 41 Part 6, third pass
    2026-09-14): bard tome count and rarity per playthrough, and
    whether a third hex-song tome ever exists: doc 41 with doc 06.
52. Bard spawn odds and check rules (any signal for which cemetery,
    or pure seed lottery; can he be missed entirely): doc 41.
53. Bard party slot (occupies one of doc 23's four level-gated
    slots vs free sixth member): doc 41 with doc 23.
54. Hex-song axis-bypass check (doc 41 fourth pass, ruling 6): the
    Dark Pacts hex-song tome lets a non-caster party carry a Dark
    Pacts payload through weapon coatings; playtest reads whether
    this bypasses doc 17's axis gates too far, revisit at GDD:
    doc 41 with doc 17.

RESOLVED by ruling 6 (2026-09-14, Nicko): doc 41 opens 9-10
(tracker 51-52). Tome count: one lightning + one frost per
playthrough, plus the optional hex-song tome in later-tier
dungeons only. Spawn signal: NONE, pure seed lottery, he can be
missed entirely, that is the design.
