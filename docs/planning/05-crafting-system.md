# 05 - Crafting System

## Design Intent
An extensive crafting system for weapons, armor, and magic. Crafting is a
primary progression path, not a side minigame: a hunter who never forges can
plateau hard, while a hunter who invests in smithing can out-equip their
level. Crafting follows the SAME progression mechanics as every other skill
(doc 18): ranks 1-100 by use, five tiers, permanent tier-up technique
choices.

## Crafting Disciplines (5 crafting skill lines - aligned with 15-skill-lines.md)
1. Weaponsmithing - melee weapons. Quality tiers, material gates (iron,
   steel, silver, cold iron, blacksteel...), enchantment sockets.
2. Armorsmithing - armor sets across weight classes (light / medium /
   heavy), material gates, upgrade paths.
3. Alchemy - potions, poisons, oils, tinctures. Scales with Herbalism (see
   06-loot-and-resources.md) and its own Alchemy skill. Feeds the daily
   DRINK slot (doc 10: any non-health/magic/stamina potion counts as the
   day's drink).
4. Enchanting - imbue weapons and armor with effects; scribe scrolls; bind
   warded charms. Consumes reagents from mining, gem crafting, and monster
   parts.
5. Gem Crafting - cut raw gems (from mining) into enchant-grade components
   and jewelry.
Plus UTILITY crafting (not a separate skill line): fletching, arrows,
throwables, torches, lockpicks, tools - folded under the relevant lines
(Archery supplies under Weaponsmithing/Alchemy, lockpicks under Enchanting
or vendor goods; exact mapping is GDD-stage).

COOKING is also a crafting skill line but lives in its own doc (10-cooking-
meals-drinks) with its own grade/kitchen-station system - do not duplicate
it here.

## Core Rules
- Materials come from the world: gathering skills (mining, woodcutting,
  herbalism, hunting/skinning), loot (monster parts, grave goods, dungeon
  chests), and purchases.
- Quality system: every crafted item has a quality outcome influenced by
  the crafter's relevant skill TIER, materials used, and station quality.
  Crafted gear then obeys the global GEAR-GATE rule (doc 18): its own tier
  requires the matching skill tier to use.
- Enchantment sockets on high-tier crafted gear are the magic-crafting hook.
- Crafting stations: forge, alchemy table, enchanting altar, workbench.
  Stations live in towns AND in the warp camp (doc 11: a maxed warp camp
  duplicates the town crafting experience in the field).
- Recipe discovery: recipes are found, bought, or reverse-engineered from
  disassembling gear. (Roguelite-ish discovery, not menu-gated from level 1.)
- Techniques (doc 18): each crafting line's tier-ups add permanent
  techniques - Masterwork Edges, Signature Series, Reforge,
  Philosopher's Shortcut, etc. These are what make a Grandmaster smith
  categorically better than an Adept one, beyond quality odds.

## Magic Crafting Direction
- Weapon runes (elemental / holy / witch-ward damage types)
- Armor wards (resistance, thorns, stamina regen)
- Charms and trinkets (passive bonuses, active-use abilities with cooldowns)
- Spell scribing: learn spells from tomes found in the world (doc 17
  acquisition model), then scribe stronger variants as Enchanting levels
  up. AXIS NOTE: enchanting cannot forge Holy or Dark effects the player's
  axis cannot hold - the axis gate applies to crafted magic the same as
  learned magic (consistent with doc 12/17).
- AEGIS interaction (doc 17): Aegis-blessed weapons are the light court's
  counterplay to corruption conversion - enchanting is where blessed gear
  comes from, making Enchanting strategically central to the war.

## Economy Hooks
- Crafted goods are sellable; NPCs want specific goods (blacksmiths buy
  ores and ingots, alchemists buy herbs and potions) - this creates the
  gathering-to-gold loop.
- Faction crafting requisitions as repeatable contract quests (Guild wants
  10 silver swords, pays in standing + coin). Standing with courts gates
  requisition tiers - a light-court smith gets light-court contracts.

## CRAFTING DEPTH (LOCKED 2026-09-12, Nicko, combat/crafting/loot session)

Approved with rulings: lockpicks = Weaponsmithing (counter-proposal
adopted, Enchanting stays purely magical); permanent Aegis gear is an
EXCLUSIVE faction asset (deep-good craftable only, no NPC service);
grade ladder and legendary station approved as written.

### Craft Quality: the FLOOR and CEILING model
Crafted gear quality is decided by TWO independent inputs, and good output
needs BOTH:
- SKILL TIER sets the quality FLOOR (a Grandmaster never produces junk).
- STATION QUALITY sets the quality CEILING (a village forge caps what even
  a Grandmaster can express through it).
- Material grade adds a modifier inside that range; techniques (doc 18
  anchors like Masterwork Edges) raise the floor further.

Gear-grade ladder (the crafting analog of loot Rarity, separate from both
Rarity and Tier): CRUDE / STANDARD / FINE / SUPERIOR / MASTERWORK.
- Grade scales the item's numbers WITHIN its tier (a Fine T3 sword beats a
  Crude T3 sword; neither touches a T4 sword).
- MASTERWORK grants +1 enchant socket (crafted gear's rarity-equivalent
  payoff).
- Grades are rolled per craft, weighted by rank, station, materials.

### Station Quality Tiers (5 tiers, mirroring gear tiers)
1. FIELD KIT (portable forge kit; warp camp basic build): ceiling STANDARD,
   slower crafts, extra material waste. Enough for T1-T2 expedition work.
2. VILLAGE STATION (village smithy, camp alchemy table): ceiling FINE.
3. TOWN STATION (town guild forge, proper alchemy lab): ceiling SUPERIOR.
4. CITY STATION (city master forge, castle armory, college labs): ceiling
   MASTERWORK, but only crafters at EXPERT+ reliably reach it.
5. GRANDMASTER STATION (guild masterwork forge; buildable ONLY at a maxed
   warp camp, or found as a single legendary dungeon station): ceiling
   MASTERWORK with the best odds in the game, plus grade-bonus rolls.
   LEGENDARY STATION PLACEMENT (Nicko, 2026-09-12, LOCKED): the single
   legendary dungeon station sits in a very obscure and difficult place in
   the world, and is NEVER marked on any map. The only route to it is a
   clue trail the player assembles from the world, with no quest marker:
   - Talking to the dead: Grave Whispers (Dark Pacts T1, doc 17) and
     graverobber play can pull the location fragment-wise from old smiths'
     graves and the dead who knew the forge.
   - Tavern intelligence: rumors, drunk stories, and informant chatter
     surface fragments; purchased info from the right brokers is the fast
     but expensive route (Speechcraft and neutral-court brokers matter).
   - Chance discovery: dungeon finds (a smith's journal page, a marked
     tool, a half-map) can start or complete the trail.
   Fragments are cumulative and redundant (several overlapping clue
   chains, any combination of which can triangulate the site), so the
   discovery is deterministic in outcome but personal in route. This
   makes the station itself a hunter's-relic-grade world secret.
Consequences: the maxed warp camp (doc 11) does not just duplicate town
crafting - its Grandmaster stations EXCEED everything in the world except
the one legendary dungeon station. Answer to the standing question: yes,
a Grandmaster forge beats a village forge by TWO grade-steps of ceiling.

### Utility Crafting Mapping (resolves the doc 05 open question)
- ARROWS + BOLTS + FLETCHING: Weaponsmithing (heads, shafts, fletching
  jigs). Mundane arrows are cheap batch crafts.
- ELEMENTAL/POISON ARROW PAYLOADS: Alchemy (coatings and tips). Fletcher's
  Eye (Archery technique, doc 04) lets the ARCHER apply payloads without
  Alchemy ranks; making them still needs Alchemy.
- LOCKPICKS: IO counter-proposal, challenges doc 05's lean: Weaponsmithing
  (precision forging at a bench), NOT Enchanting - Enchanting should stay
  purely magical, and lockpicks are mundane metalwork. Vendor goods remain
  the fallback for non-smiths. (Nicko ruling needed.)
- TORCHES + TOOLS: Weaponsmithing (mundane metalwork).
- ALCHEMICAL THROWABLES (firebombs, acid flasks, frost flasks): Alchemy.
- CAMPING GEAR and WARP CAMP STRUCTURES: not a skill line's product; built
  through the warp camp system itself (doc 11), using materials from any
  gathering line.

### Recipe Economy
- RECIPES ARE LOOT: found in dungeons, bought from faction-stocked vendors,
  rewarded by requisition contracts. Recipe drops are keyed by biome and
  dungeon type (doc 06 tables) like everything else.
- TIER GATE ON ATTEMPT: a recipe for Tier-N gear requires the crafting
  skill tier that gates Tier-N gear (Apprentice/T2, Adept/T3, Expert/T4,
  Grandmaster/T5). Knowing a recipe too early does nothing; recipes you
  cannot use yet sit in your book as visible future goals.
- REVERSE-ENGINEERING: disassembling gear at a station has a
  rank-weighted chance to learn its recipe (or a variant). NAMED items
  (hunter's relics, doc 06) can never be reverse-engineered - their
  uniqueness is protected; they can only be REFORGED via the doc 18
  Reforge technique.
- AXIS-GATED RECIPES: Holy/Dark enchant recipes burn in the wrong hands,
  same rule as tomes (doc 17).
- MATERIALS set the tier: the recipe defines the form; the material grade
  (iron, steel, silver, cold iron, blacksteel) defines the output tier.
  One sword recipe + blacksteel = a higher-tier sword than the same
  recipe in iron, IF the crafter's skill tier supports it.

### DISASSEMBLY (LOCKED 2026-09-14, Nicko: all items break down; own skill line)
- ALL ITEMS disassemble into raw materials at the Workbench: gear,
  charms, decorations, camp goods, vendor junk. Nothing is
  unsalvageable except the two All-Craftable exceptions (Hunter's
  Relics Reforge-only, spine-story items) and axis-gated gear in the
  wrong hands (it burns, same rule as recipes/tomes).
- DISASSEMBLY IS CORE SKILL LINE 29 (doc 15 SALVAGE): ranks 1-100 by
  use, five tiers, technique choices at tier-ups (doc 18 mechanics),
  same as every other line. Levels ONLY by disassembling.
- YIELD MODEL: base yield = a fraction of the item's own recipe
  inputs (the primaries and secondaries the item was made from, raw
  form: hides, bones, wood, ore-not-ingots). Higher rank yields MORE
  raw materials per item.
- RARE RECOVERY: rank-scaled chance to recover RARE materials beyond
  the base yield: higher-tier category members than the item's own
  tier, refined supplies, catalysts (tanning liquor, quench salts,
  arcane ash), and at high ranks Hunter's Components (doc 05). Luck
  adds on top (same stack rule as the fortune/Luck pairing).
- RELIC EXCEPTION: disassembling a Hunter's Relic is NEVER possible;
  its salvage path is Reforge only (doc 18), per the locked relic
  protection. Attempting it is refused by the station.
- RECIPE DISCOVERY (relocated from reverse-engineering, doc 05 locked
  economy): disassembling gear has a rank-weighted chance to learn its
  recipe (or a variant), now rolled as THIS line's skill check instead
  of the crafting line's. NAMED items can still never be reverse-
  engineered. Success rates and failed-disassembly outcomes stay GDD
  tuning (open question 3 above unchanged).
- ANTI-EXPLOIT: disassembly returns RAW materials, never a net gain of
  refined supplies, so buy-refine-disassemble loops lose money against
  vendor prices. T5 craftables disassemble at a reduced yield
  (negative base bonus, same grammar as refining's anti-stockpile
  rule).

### INGREDIENT SYSTEM: New World adaptation (LOCKED 2026-09-12, Nicko: "I like the ingredients system, lock it in for now")

Research basis: New World (Amazon) crafting splits every recipe into a
PRIMARY material (tier-locked, determines the item's tier) plus SECONDARY
slots filled by CATEGORY (any item of the right category works, and
using rarer/higher-tier members of the category raises outcome odds),
with refining chains (raw to refined, station tier caps refine tier),
elemental reagent ladders (Mote/Wisp/Essence/Quintessence), rare "craft
mod" resources that GUARANTEE a specific perk, and a resource (Azoth)
that improves perk/socket odds. Adapted below for a single-player souls-
like with fixed difficulty, no repair, and the three item dimensions.

#### 1. Ingredient slots: 1 primary + category secondaries
Every gear recipe = ONE PRIMARY SLOT + TWO OR THREE SECONDARY SLOTS.
- PRIMARY: the exact refined material class, tier-locked (blacksteel
  ingots for a T4 blade). The primary sets the output TIER (already
  locked: materials set the tier). No substitution across tiers.
- SECONDARIES: recipe slots name a CATEGORY, not an item: "handle wood",
  "grip leather", "binding sinew", "focus crystal". ANY item of that
  category fills the slot. The same item cannot fill two slots in one
  recipe (New World's no-duplicate rule).
- QUALITY BONUS: secondaries of HIGHER tier or rarity than the minimum
  feed the grade roll (shifts odds toward Fine/Superior/Masterwork).
  Cheap secondaries craft fine; expensive secondaries craft BETTER.
- This is the world-sampling magic of New World: the recipe names the
  shape, the world's variety fills it, and every biome's special
  materials become relevant to every crafter.

#### 2. Material categories (world taxonomy for secondary slots)
- METALS (refined under Weaponsmithing): iron, steel, silver, cold iron,
  blacksteel.
- WOODS (Woodcutting): oak, yew, blackwood, witchwood.
- HIDES (Hunting/Skinning): doe leather, boar hide, wyrm-scale.
- BONE AND SINEW (Hunting/Skinning): common bones, hardened chitin,
  troll sinew, undead ossuary parts.
- HERBS (Herbalism): biome-keyed, feeds Alchemy and Cooking unchanged.
- GEMS (Mining/Gem Crafting): cut gems for sockets and jewelry.
- ARCANE REAGENTS: see the reagent ladder below.

#### 3. Refining layer (raw to refined, at stations)
- Raw gathered materials must be REFINED before crafting (ore to ingot,
  hide to leather, raw gem to cut stone). Refining happens at the
  station of the target crafting line and levels THAT line (no separate
  refining skills; keeps the 29-line structure intact, Disassembly
  included).
- REFINING REAGENTS: some refine steps need a catalyst (quench salts for
  ingots, tanning liquor for leather, arcane ash for cold iron and
  blacksteel). Catalysts are crafted (Alchemy) or bought. This makes
  refining a small recipe chain, not a click.
- STATION TIER CAPS REFINING (direct from New World): a Field Kit
  cannot refine above T2 materials; Grandmaster stations refine
  everything. The FLOOR/CEILING station ladder now ALSO gates what
  materials can even be processed, deepening station importance.
- BONUS YIELD: refining has a rank-weighted chance to yield extra
  output; high-tier recipes have negative base bonus (New World's anti-
  stockpile rule). Luck (stat) nudges the roll.

#### 4. Arcane reagent ladder (New World's Mote/Wisp/Essence/Quintessence)
Four-step reagent chains keyed to the five magic schools' elements,
refined at enchanting altars. COMBINING RATIO LOCKED 2026-09-12
(Nicko, world GDD tuning): 3:1 per step (3 Motes combine to 1 Wisp,
and so on up the ladder).
- FIRE: Ember Mote > Flame Wisp > Cinder Essence > Pyre Quintessence
- FROST: Rime Mote > Frost Wisp > Glacial Essence > Absolute
  Quintessence
- STORM: Spark Mote > Storm Wisp > Tempest Essence > Maelstrom
  Quintessence
- HOLY (axis-gated materials): Grace Mote > Dawn Wisp > Sanctified
  Essence > Aegis Quintessence
- DARK (axis-gated materials): Grave Mote > Crypt Wisp > Haunt Essence >
  Abyssal Quintessence
- Sources: rare resource spawns per biome (New World's Shockbulb
  analog: glowing blooms, charged ores, grave-cold moss), monster part
  byproducts, and dungeon caches. Rare spawns respawn on the standard
  2-3 day node timer. Holy/Dark reagents come from court territory and
  cannot be carried across the axis gate (they attune to the holder).
- CONSUMED BY: Enchanting (higher reagent steps = stronger enchant
  tiers), Alchemy (potions and coatings), and the Aegis recipe
  (Aegis Quintessence + consecrated silver).

#### 5. Hunter's Components (New World's craft mods, adapted)
- Rare special resources gathered from the world (a small chance from
  ANY harvest node, kill, or chest, weighted by Luck): each one
  GUARANTEES a specific enchant when used as an optional ingredient.
- Examples: Wolf-Fang Sigil guarantees lifesteal enchant; Cracked Ward
  Stone guarantees stamina-regen armor ward; Ember Gizzard guarantees
  fire weapon rune.
- This gives the player DIRECT CONTROL of the enchant dimension (the
  third item dimension): sockets are rolled (grade + techniques), but
  what goes in them can be dictated by rare finds. Chasing a specific
  component sends the hunter to specific biomes/monsters: the gather
  loop and the build fantasy connect.
- A craft can hold ONE guaranteed enchant (one component); other
  sockets roll randomly or take cut gems.

#### 6. What we deliberately do NOT take from New World
- The Trading Post economy (single-player game; our vendor economy in
  doc 06 covers trade).
- Azoth as a craft resource (our outcome-shifters are materials, Luck,
  station, and axis standing; no new global currency needed).
- Town-project station leveling (our stations are world-fixed +
  warp-camp built, doc 11).

### Open questions added by this section (also in 08):
1. Category member lists per biome (exact woods/hides/reagent spawns):
   world GDD content authoring.
2. Reagent step-count tuning (3:1 vs 4:1): RESOLVED 2026-09-12
   (Nicko, world GDD tuning): 3:1 per step, locked (doc 05).
3. Whether refining bonus-yield should also apply to gear crafting
   (extra item chance) or stay refine/consumable only: RESOLVED
   2026-09-12 (Nicko): REFINE/CONSUMABLE ONLY, never gear-craft
   extra-item rolls. Gear crafts stay deliberate.

### Interaction With the Three Item Dimensions (doc 06)
- TIER: set by recipe + materials, never by the quality roll. Deterministic.
- GRADE (quality): rolled per craft; the crafting analog of Rarity, but
  earned rather than dropped.
- ENCHANTS: socket count = base (by gear tier) + grade bonus (Masterwork
  +1) + techniques (Twin-Socket, Setting Mastery). Enchant effects are
  limited by the axis gate (no Holy/Dark enchants beyond your axis).
- AEGIS-BLESSED WEAPONS (strategically central, doc 17): permanent Aegis
  enchant is an EXPERT-tier Enchanting recipe requiring consecrated
  silver (light-court vendors and relic loot only) and deep-good axis.
  RULED 2026-09-12 (Nicko): Aegis gear is an EXCLUSIVE FACTION ASSET.
  Deep-good crafters only; no NPC enchanting service exists at any
  price. A non-deep-good player can never own permanent Aegis gear.
  This makes blessed gear a light-court strategic resource, not a
  purchasable commodity.

### New Open Questions (also recorded in 08-open-questions.md)
1. Lockpicks under Weaponsmithing: RESOLVED 2026-09-12 (Nicko adopted the
   counter-proposal; Enchanting stays purely magical).
2. Permanent Aegis access: RESOLVED 2026-09-12 (Nicko: exclusive faction
   asset, deep-good craftable only, no NPC service).
3. Reverse-engineering success rates and whether failed disassembly
   destroys the item with no learn: tuning, GDD stage.
4. Legendary station clue-chain content: exact fragment list, which
   graves/NPCs/dungeons carry which clues, fragment counts per chain:
   quests/world GDD stage.
5. New World ingredient-system adaptation: RESOLVED 2026-09-12 (Nicko
   approved and locked "for now"). Remaining sub-items stay assigned:
   category member lists per biome (world GDD content authoring),
   reagent step-count tuning (GDD tuning), refining bonus scope (GDD
   tuning, leaning refine/consumable only).
- NO item repair system: items are permanent (doc 08). Crafting relevance
  comes from tiers, enchants, grades.
- The player can fully skip crafting and still finish the game - yes, but
  worse: purchasable gear caps lower than Grandmaster-crafted gear, and
  the crafting-adjacent systems (enchanting for Aegis gear, cooking for
  daily buffs) confer advantages that buying cannot. CONFIRMED as design
  answer.
- Crafting XP is USE-based per line (doc 18) - there is no separate
  crafting XP currency; the line's ranks ARE its XP.
- Player-made crafting stations exist via the warp camp (doc 11), not a
  separate hideout system. Superseded.

## POTIONS GDD: THE ALCHEMY STATION (LOCKED 2026-09-12, Nicko)

Built on the SAME doc 03 per-biome ingredient lists as food (Nicko
directive): one gather loop feeds both stations. The alchemist
station is its own ladder, separate from cooking stations.

### USAGE MODEL (LOCKED, Nicko: "the estus flask is unnecessary")
- NO ESTUS FLASK. Health and Mana (Focus) potions are crafted
  STOCK items: brew them, carry them, drink when needed. Carry
  weight is the only brake (doc 10's literal reading, locked).
- INTENSITY SCALES TWO WAYS: player Alchemy skill tier (the
  floor) and alchemy station tier (the ceiling), per the locked
  doc 05 floor/ceiling model and the grade ladder. A Grandmaster
  at a City Lab brews a Superior healing potion; a Novice at a
  Field Kit brews Crude.
- COMBAT POTION SCOPE: strictly HEALING and MANA potions (Nicko).
  No stamina potion line (stamina is food/rest's domain, doc 10).

### THE MORNING RITUAL (LOCKED, Nicko): potions are made to be
### had WITH the morning meal, to prep for the day
- ONE daily prep potion, taken with the morning meal (this IS
  the doc 10 drink slot: one per day, non-health/mana). Chosen
  the night before or at dawn for the day's plan.
- OFFENSE prep potions (the BANE draughts): built from monster
  parts, keyed to the day's target grammar (doc 04): +damage,
  Ward-pierce, poise-shred, crit vs the chosen enemy family.
- DEFENSE prep potions (the WARD draughts): built from herb
  signatures, keyed to the day's biome ambient threat:
  resistances for blight, cold, disease, hexes, miasma, fear.
- The daily trio is thus MEAL + POTION + (coatings applied):
  food shapes the body, the potion shapes the day, coatings arm
  the blade. One gather loop, two stations, one morning ritual.

### THE ALCHEMY STATION LADDER (PROPOSED; instantiates doc 05's
### global 5-tier model at the alchemy bench)
1. FIELD ALCHEMY KIT (portable, warp-camp basic): refine T1-T2,
   3-ingredient potions only, no rare-component handling.
2. VILLAGE ALCHEMY TABLE (herbalist's shed): refine T3, standard
   potions, coatings T1-T3.
3. TOWN APOTHECARY LAB: refine T3, bonus-yield odds up, full
   coatings/throwables lines.
4. CITY LABORATORY: refine T4, rare-component socket (one
   Hunter's Component per brew, doc 05), grade ceiling
   Masterwork.
5. GRANDMASTER LAB (maxed warp camp) + THE ONE LEGENDARY DUNGEON
   STATION (doc 05's legendary station doubles for alchemy):
   refine everything, best odds; the legendary station alone
   brews the two T5 legendary potions (list below).
- FLOOR/CEILING carries (locked doc 05): Alchemy skill tier =
  floor, station = ceiling, grade ladder Crude/Standard/Fine/
  Superior/Masterwork scales magnitude + duration. Refine/
  consumable-only yield (locked this session's tuning).

### THE FOUR PRODUCT FAMILIES (LOCKED 2026-09-12, Nicko)
1. HEALING + MANA STOCK (health/focus): crafted stock, spammable,
   carry-weight-limited; intensity = skill tier x station tier.
   (The stamina potion is CUT, Nicko: food/rest owns stamina.)
2. THE DAILY PREP POTION (the morning ritual, drink slot): one
   per day with the morning meal; offense (bane draughts, monster
   parts) or defense (ward draughts, herb signatures).
3. WEAPON COATINGS + PAYLOADS: blade oils and arrow/bolt tips
   from monster parts; arm the blade for the day's fights.
4. THROWABLES: firebombs, acid flasks, frost flasks.

### THE BANE GRAMMAR (LOCKED 2026-09-12, Nicko)
Potions mirror the ward-dish grammar (doc 10): one learnable
system across food and alchemy.
- BIOME ATTACK potions = the biome's MONSTER PARTS (coatings +
  pre-fight draughts keyed to doc 04 enemy grammar, same as
  attack dishes): Wight-Marrow Oil (moors: your hits pierce
  undead Ward), Witch-Bane Philter (Darkwood: +crit vs
  witch-fauna), Clatterer-Dissolving Acid (mountains:
  corrosion vs chitin).
- BIOME DEFENSE potions = the biome's HERB SIGNATURES (draughts,
  drink slot): Blizzard-Pot's potion twin (cold immunity),
  Feverfew Tonic (swamp disease), the Visioner's Draught
  (blight attrition half).
- SAME HERBS, DIFFERENT STATION: the moonbell in Darkwood's
  Glade-Knot Porridge is the same moonbell in Darkwood's
  anti-hex draught. Doc 03's locked lists do double duty by
  design (Nicko directive).

### WORKING DRAUGHT LIST (one per biome, the daily prep potion;
### LOCKED list, names/durations at tuning)
- DARKWOOD: Green Veil-Steep (fog-sight), TENDER'S DRAUGHT
  (taint-creep resistance for witchwood harvest), WITCH-BANE
  PHILTER (offense: +crit vs witch-fauna, the bane draught).
- MOORS: Watcher's Tonic (cold-wind + Precision at range),
  UNWAILED DRAUGHT (Wail/Howl morale-break resistance),
  WIGHT-MARROW DRAUGHT (offense: Ward-pierce vs undead).
- SWAMPLANDS: Feverfew Tonic (disease), STILL-WATER DRAUGHT
  (fishing/swimming + Pale-Tide fog sight, doc 03 Veil-Tide),
  HAG-BANE DRAUGHT (offense: +poise vs hags/bound things).
- MOUNTAINS: HEARTH-TODDY (frost immunity, doc 10's example
  made canonical), DEEP-BREATH (altitude stamina),
  CLATTERER-DISSOLVING DRAUGHT (offense: corrosion vs chitin).
- FARMLAND: FARMWIFE'S CIDER (social/Charisma, doc 10),
  CHAPEL-GARDEN TEA (parish standing +25 percent, light-held
  parishes only, doc 20), THRALL-BREAKER DRAUGHT (offense:
  +damage vs thralls/raiders).
- BLIGHT: UNDERTOW-NAUSEA DRAUGHT (function in Pale Tide fog),
  THE VISIONER'S DRAUGHT (blight attrition half, lasts the
  day), DEMON-BAIT DRAUGHT (offense: +damage vs demons; taint
  on drinking, doc 17).

### COATINGS + PAYLOADS (PROPOSED, monster-part attack grammar)
- WIGHT-MARROW OIL: hits pierce undead Ward (moors).
- WITCH-BANE OIL: +crit vs witch-fauna and hags (Darkwood).
- HAG-BILE TIP: poisons bound things resist less (swamps).
- TROLL-BLOOD COATING: +poise damage vs high-poise (mountains).
- THRALL-BREAKER OIL: +damage vs thralls and undead raiders
  (farmland's grudge oil).
- CORRUPTED-IRON SLURRY (blight): dark coating, +damage vs
  demons and Ward-pierce (taint on crafting, doc 17 bands).
- PAYLOADS: elemental tips (Fire/Frost/Storm reagent ladder,
  doc 05: coating = reagent + fat/wax base), poison tips
  (hemlock base), HOLY-blessed tips (axis-gated, burn in evil
  hands), DARK tips (deep-evil, taint on use).
- Grade scales charges-per-coating and potency; Masterwork
  coating = +1 effect tier (mirrors Masterwork +1 socket).

### THROWABLES (locked doc 05, numbers PROPOSED)
- FIREBOMB (Pyro reagents + fat): fire zone on impact (doc 17
  Flame Zone grammar in a flask).
- ACID FLASK (armor/poise shred pool, doc 04 poise grammar).
- FROST FLASK (chill patch, Cryomancy grammar).
- HOLY WATER VIAL (axis-gated: anti-undead zone burst,
  Consecrate grammar; burns in evil hands).
- GRAVE-ROT VIAL (deep-evil: raises ONE corpse briefly; taint
  on use).
- Station gate: throwables need TOWN Apothecary+; the vial
  needs Grandmaster.

### COMBAT POTION USAGE MODEL (PROPOSED, REC for ruling)
- SOULS ESTUS MODEL (REC): the Healing Trio are limited-charge
  FLASKS refilled at taverns/camps/the warp camp; charges scale
  with station tier (Field Kit 3 charges, Grandmaster Lab 6) and
  Alchemy skill. Carry weight on top (locked). Rationale:
  classic souls potion tension, no inventory spam, the tavern
  network stays load-bearing (no fast travel made it so).
- Alternative carried for review: pure carry-weight stock (doc
  10's literal reading).

### AXIS AND TAINT (carried doc 17 gates)
- HOLY potions (consecrated salts, Aegis-adjacent): axis-gated
  deep-good, burn in evil hands (locked doc 17 tomes rule
  extended).
- DARK potions (grave-moss, crypt-bloom bases): gated deep-evil
  AND push necromantic taint on use (ride the 3-band dial,
  locked doc 17).
- THE CLEANSING DRAUGHT (chapel-garden herbs + consecrated
  salt): the PORTABLE version of Purify (cleanses ANOTHER's
  taint/ailments only, locked doc 17 rule; brewing is
  deep-good only). REC: makes the Church of Mercy's alchemists
  a light-court strategic resource like Aegis smiths.
- WOLVES (no-ledger strain, locked doc 19): drink either side's
  potions without axis burn; Hidden Court alchemists buy from
  neutral brokers (doc 03 shadow court).

### T5 LEGENDARY POTIONS (legendary-station-only; PROPOSED)
1. THE UNDERTOW'S DRAFT (dark, T5): one in-game day of the
   Undersovran's sight: sigils and contracts visible on the
   world (doc 19's contracts-and-sigils presence; aids the
   debt-arc discovery arc's diegetic reading, doc 20's
   diegetic-only rule untouched: it shows sigils, not a meter).
2. THE DAWN-DRAUGHT (light, T5): one Aegis-grade day: your gear
   reads as blessed steel vs undead for a day (the Aegis rule's
   temporary cousin; deep-good brew only, locked Aegis rule).

### Open Questions (potions; also recorded in 08)
1. Combat potion usage model: RESOLVED 2026-09-12 (Nicko): NO
   estus flask; health/mana potions are crafted stock,
   carry-weight-limited; intensity = skill tier x station tier;
   no stamina potion.
2. Four-family split: RESOLVED 2026-09-12 (Nicko): Healing+Mana
   stock / Daily Prep Potion (the morning ritual, drink slot) /
   Coatings+payloads / Throwables.
3. Potion grade ladder: RESOLVED 2026-09-12 (Nicko implicitly by
   the intensity ruling): the standard 5-name grade ladder,
   magnitude+duration scale with skill x station.
4. Bane grammar: RESOLVED 2026-09-12 (Nicko): locked, potions
   mirror the ward-dish grammar (offense = monster parts,
   defense = herb signatures).
5. REMAINING OPEN (potions): T5 legendary potion recipes (the
   Undertow's Draft, the Dawn-Draught) stay legendary-station
   exclusive (doc 05 legendary station); recipe discovery
   routes for them = quests GDD. Potion exact numbers = tuning.

## CRAFTING DEPTH: THE WORKBENCH + SUPPLIES (LOCKED 2026-09-12, Nicko)

Nicko directive: ALL items in the game craftable, including all
decorations; the warp camp as the defining customization hub, rugs
to trophies, decorations, stations, defenses, full expression of
player choice. Compensating station: a main CRAFT WORKSTATION
that refines and purifies world ingredients into usable supplies
(New World model).

### THE WORKBENCH (LOCKED)
A sixth dedicated REFINING station, the hub of every craft: raw
world materials in, USABLE SUPPLIES out. Gear/food/potions/
decorations/structures consume SUPPLIES, not raw pelts and logs.
Five tiers matching the locked doc 05 station ladder (Field Kit
refines T1-T2 ... Grandmaster refines everything). Line-stations
stop refining; the Workbench feeds them.

SUPPLY CHAINS (per category, doc 03/05 lists feed it):
- HIDES > LEATHER grades (pelt + tanning liquor): T1 cured
  leather up to wyrm-leather; grade scales armor outputs.
- WOODS > LUMBER grades (log + sealant); witchwood > TREATED
  witchwood (taint on working, doc 17).
- ORES > INGOTS (locked doc 05 chain moves here wholesale:
  quench salts, arcane ash for cold iron/blacksteel).
- FIBER > CLOTH + ROPE (herb/fiber staples, doc 03).
- FITTINGS: nails, clasps, hinges, wax, glue (bone/resin
  byproducts, doc 06 monster parts).
- PIGMENTS + DYES: herb-keyed (doc 03's herbs double as dyes:
  biomes decorate with the map's own colors).
- PURIFIED REAGENTS: the doc 05 arcane ladders (3:1 locked),
  refined here at enchant-grade.
- GRADE LADDER carries: workbench tier x skill = supply grade;
  supply grade feeds every downstream craft's grade roll
  (gear/food/potions/decorations: the doc 05 floor/ceiling
  grammar extended to buildings).

### THE ALL-CRAFTABLE PRINCIPLE (LOCKED)
Every item in the game is craftable at the camp EXCEPT two
locked categories: Hunter's Relics (Named T5, Reforge-only,
locked doc 06) and spine-story items (doc 20 spine immunity).
Gear, ammo, potions, food, decorations, structures, defenses,
tools, camp furniture: all craftable, all consuming supplies.

## CAMP CUSTOMIZATION: DECORATION CATALOG (LOCKED)
The warp camp as the customization hub (Nicko directive); the
doc 11 three-tier camp is the canvas. Eight categories, all
Workbench-crafted:
1. FLOORS + RUGS (hides, woven fiber; per-biome pattern sets
   from doc 03 pigments).
2. TROPHIES (monster-part-first, doc 06): every biome enemy has
   a craftable trophy (mounted heads, pelt racks, bone totems,
   the wight-bard's harp). TROPHY BUFFS (LOCKED, Nicko "I love
   this camp wide effect"): trophies of a biome's apex beast
   grant a small permanent camp-wide buff vs that beast family
   while displayed; the hunt-collector loop pays rent.
3. FURNITURE (beds, tables, benches, Tier 3 thrones).
4. LIGHTING (torch sconces, witchfire lanterns, consecrated
   lamps; light = safety radius at night, doc 12 clock).
5. BANNERS + HERALDRY (the charged-shields grammar, doc 03):
   your authored crest on walls and rugs. HERALDRY IS OPTIONAL
   DISPLAY (LOCKED, Nicko: "if chosen to"): crest/court colors
   show on camp items only when the player chooses to display
   them.
6. SHRINES (axis-gated: light shrine, dark altar, neutral
   hearth; feed rest quality per affinity, doc 12).
7. DEFENSES (already locked doc 11, now all Workbench-crafted:
   spikes, traps, walls, watchfires).
8. STRUCTURES (tents to halls, all doc 11 tiers).

### DECORATION PRESTIGE (LOCKED, resolves doc 11 Q8)
Comfort/Prestige value (fed by every decoration category, doc
11's track made mechanical) buffs:
1. REST QUALITY: full heal + the morning buff slot extends one
   extra hour per prestige band.
2. GREETING CEREMONY scale (locked doc 11 fantasy made
   mechanical).
3. Camp thief/raid DETERRENCE in safe zones (thieves pick
   shabbier camps; prestige camps in dangerous zones stay
   raided: wealth attracts, doc 11 threat model honest).
4. CAMP AS STATION: a Masterwork-decorated Tier 3 camp adds
   +1 grade roll to meals/potions brewed there (the camp
   itself is a station quality).
5. RETINUE MORALE (doc 11 NPC morale): prestige raises the
   affinity-threshold tolerance (doc 11's leave-on-dislike
   rule loosens one band).

### Open Questions (crafting depth; RESOLVED 2026-09-12, Nicko)
1. The four core locks: RESOLVED + LOCKED (section above).
2. Heraldry on decorations: RESOLVED + LOCKED (optional display
   per player choice, section above).
3. Trophy buffs: RESOLVED + LOCKED (camp-wide buffs, section
   above).

## Open Questions (current state - first-draft questions resolved)
- Repair system: RESOLVED (none). Hideout stations: RESOLVED (warp camp).
- Crafting XP model: RESOLVED (use-based ranks per doc 18).
- Station quality tiers: RESOLVED 2026-09-12 (FLOOR/CEILING model, 5
  station tiers, grade ladder Crude/Standard/Fine/Superior/Masterwork,
  legendary dungeon station with a no-marker clue trail). LOCKED.
- Utility-crafting mapping: RESOLVED 2026-09-12 (arrows/fletching/torches/
  lockpicks = Weaponsmithing; payloads/throwables = Alchemy). LOCKED.
- Permanent Aegis gear access: RESOLVED 2026-09-12 (exclusive faction
  asset, deep-good craftable only, no NPC service). LOCKED.
- Reverse-engineering rates: GDD-stage tuning (above); also recorded
  in 08-open-questions.md under this session's additions.
- New World ingredient-system adaptation (1 primary + category
  secondaries, refining with catalysts, arcane reagent ladders,
  Hunter's Components): LOCKED 2026-09-12 (Nicko, "for now").

## GATHERING FORTUNES (slot + spread + grammar rulings LOCKED 2026-09-14, Nicko; names and effects PROPOSED)

Nicko requested drop/gathering-increase potions. Ruled in session:
- SLOT: DAILY PREP ONLY. A gathering fortune replaces that day's bane/ward draught. The morning ritual is unchanged (one meal, one potion, one day). No new potion family; the daily prep's menu grows.
- SPREAD: ONE FORTUNE PER GATHERING SKILL LINE (doc 06's six lines): Herbalism, Woodcutting, Mining, Gem Crafting (acquisition side), Hunting/Skinning, Fishing.
- GRAMMAR: NODE-KEYED. Each fortune's key ingredient is a small byproduct of the very resource it boosts, so the loop is self-feeding: gather the byproduct, brew the fortune, the fortune helps gather more. Byproduct items are PROPOSED additions to doc 06's gather tables.
- EFFECT (PROPOSED): for the rest of the day, raises that line's drop odds and rare-resource rolls, the same rolls the Luck stat and the Rare Sight / Seam Sense techniques already move (doc 06/15). They stack with Luck and techniques because they are separate sources; exact percentages are GDD tuning.
- DISCOVERY: normal recipe economy (doc 05, locked): recipes are loot, found in dungeons, bought from faction vendors, or reverse-engineered. An undiscovered recipe is invisible, not craftable.

The six (working names PROPOSED):
1. PROSPECTOR'S DRAUGHT (Mining): more ore per vein, more gem-bearing veins flagged.
2. FACETER'S EYE (Gem Crafting): better raw-gem yields from veins and monster drops.
3. TILLER'S GREEN (Herbalism): rarer specimens, higher herb yields.
4. SAWYER'S TONIC (Woodcutting): better wood cuts, more special-tree finds.
5. TRACKER'S DRAUGHT (Hunting/Skinning): richer pelts, parts, and ichors per kill.
6. STILLWATER CHUM (Fishing): better catches, more rare fish.
