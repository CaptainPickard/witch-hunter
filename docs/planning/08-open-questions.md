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
6. Skill lines: 28 core (9 combat, 5 magic, 5 crafting, 6 gathering, 3
   utility/social) + specialty expansion upward (15).
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
