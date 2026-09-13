# 06 - Loot and Resources

## Decisions (locked with Nicko)
- Inventory is Daggerfall-style weight-based. Carry Weight is a real stat
  (one of the nine) and progression pressure, not slot Tetris. LOCKED.
- NODE RESPAWN (locked 2026-09-11, second sweep): 2-3 in-game days per
  resource node. Gathering routes are repeatable without exhausting the
  world.
- GRAVE-LOOTING (locked 2026-09-11): cemetery looting costs light-court
  reputation (Church/Guild disapprove; dark factions approve); feeds the
  moral axis. LOCKED.
- FISHING (locked 2026-09-11, second sweep): a FULL skill line with its own
  techniques (Stillwater, Deep-Line, Trophy Angler). It feeds cooking and
  is thematically load-bearing (swamp/river biomes).
- ALL PROPS ARE 2D (locked, art pass): ground loot renders as sprites.

## Design Intent
The world is full of loot AND full of resources. Loot answers "what do I get
for fighting," resources answer "what do I get for exploring and working the
land," and both feed crafting, selling, and XP. Loot and resources are also
affinity-political: where you fight and gather depends on which courts will
tolerate you there (doc 12).

## Loot Sources
- Enemy drops (monster parts are crafting reagents, not trash)
- Chests and stashes in dungeons, cemeteries, and wilderness caches
- Grave goods (cemetery looting is a mechanic with a light-court reputation
  cost - LOCKED; a Graverobber specialty exists for players who live here,
  doc 16)
- Quest rewards and faction requisition payouts
- Purchased from vendors (courts stock different gear; neutral court sells
  to anyone - doc 12)
- Rare world drops (named weapons with lore, "hunter's relics")
- SPELL TOMES (doc 17): spells are world knowledge; tome drops are a loot
  category, and axis-burning tomes are a special case - the wrong player
  picks up a book that combusts.

## Gathering Skills (6 gathering skill lines - aligned with 15-skill-lines.md)
1. Herbalism - pick herbs across biomes; higher skill reveals rarer
   specimens, higher yields, and unlocks stronger potion bases.
2. Woodcutting - fell trees and harvest deadwood; special trees (blackwood,
   witchwood) in dark forests are rare spawns.
3. Mining - ore veins in mountains, caves, and dungeon walls; deeper = rarer.
4. Gem Crafting (acquisition side) - raw gems from veins and monster drops;
   refined in crafting (see 05).
5. Hunting / Skinning - monster parts, pelts, bones, ichors. LOCKED as the
   sixth gathering line; feeds cooking (meals) and crafting (reagents).
6. Fishing - rivers, swamp, sea. LOCKED as a full skill line with its own
   techniques; feeds cooking.

## Resource Philosophy
- Every resource node type maps to at least one crafting discipline, so
  nothing you gather is dead weight.
- Regional specialization: swamps grow the best alchemy herbs, mountains
  hold the best ore - this makes travel and court territory meaningful.
- Resources respawn on a 2-3 day timer (LOCKED) so gathering routes become
  a repeatable loop without exhausting the world.
- Node density defaults (how many veins/herb patches per region) remain
  GDD-stage tuning.

## XP Integration
Gathering a node levels its specific skill line (Herbalism, Mining, etc.)
under the doc 18 mechanics: ranks 1-100 by use, tier-up technique choices.
Higher skill = faster harvest, rarer finds, better crafted outputs from
those materials. LUCK (stat, locked) raises drop odds and rare-resource
rolls - the Luck stat and the tier-up techniques (Rare Sight, Seam Sense)
stack as the two sources of gathering fortune.

## Loot Rules
- GEAR RARITY (first pass): Common / Uncommon / Rare / Named (named items
  are unique, lore-bearing). Rarity is a LOOT dimension and is separate
  from the crafted GRADE systems (cooking's Common-to-Masterwork grades
  are a food system, not a gear system) and from gear TIER (the doc 18
  gate dimension: Tier-2 needs Apprentice, etc.).
  CLARIFIED 2026-09-11: three orthogonal item dimensions -
  (1) RARITY: how rarely it drops (loot system)
  (2) TIER: what skill tier it requires to use (gear-gate system)
  (3) ENCHANTS/GRADES: what it does (enchanting sockets, cooking grades).
- Loot tables are biome- and dungeon-type-keyed, not global, so where you
  fight determines what you can find. Court territory shapes tables
  further (vampire holds drop dark reagents).
- Monster-part-first mentality: kills should feel like they feed your
  crafting chain, not just your coin purse.

## Storage
- Player storage: the VALET system (doc 11) - the warp camp's valet gives
  instant access to all built storage chests; primary external storage
  lives at the summoned camp. Weight binds you in the field, not at home.
- Stash upgrade path = building more/better storage structures in the warp
  camp (crafting-driven, doc 11).

## LOOT ECONOMY (LOCKED 2026-09-12, Nicko, combat/crafting/loot session)

Built to integrate with the LOCKED ingredient system (doc 05): loot feeds
the primary/secondary/reagent/component ingredient slots directly.

### 1. Loot table structure (biome- and dungeon-type-keyed)
Every table rolls FOUR layers in order:
- LAYER 1, MONSTER PARTS (monster-part-first, locked): guaranteed-weighted
  drops keyed to the kill. Parts feed the SINEW/BONE/HIDE categories and
  Alchemy. The kill should always be able to answer "what did this feed?"
- LAYER 2, MATERIALS: biome-keyed raw materials feeding the doc 05
  categories (metals ore, woods, herbs, hides). Regional specialization
  is enforced HERE: swamps carry the alchemy herbs, mountains the ore,
  dark forests the witchwood.
- LAYER 3, GEAR: the Rarity roll (structure below).
- LAYER 4, SPECIAL SLOT: tomes (doc 17 rules, axis-burning tomes
  included), recipes (doc 05 recipe economy), reagent rare-spawn
  equivalents (the Shockbulb analogs), Hunter's Components, and
  named-item chances. COURT TERRITORY OVERLAY: which court holds the
  region shifts layer 4 (vampire holds weight dark reagents and Dark
  Pacts tomes; church vaults the holy side; neutral dens carry
  recipes and broker intel).
- DUNGEON-TYPE KEYS: crypt/cemetery tables weight bones, grave goods,
  undead parts, holy reagents; mines weight ores and gems; coven dens
  weight reagents and tomes; war camps weight faction gear and
  requisition loot.

### 2. Rarity-vs-Tier distribution (the crossing rule)
LOW-TIER GEAR SPANS ALL RARITIES; HIGH-TIER GEAR LIVES ONLY AT HIGH
RARITY:
- T1-T2 gear: Common through Named (a Common T2 sword exists; Named T2
  relics exist as starter-region stories).
- T3 gear: mostly Uncommon/Rare, some Named.
- T4 gear: Rare and Named only.
- T5 gear: Named ONLY (and always story-attached, see relics below).
Rarity is the DROP-FREQUENCY axis (Common common, Named near-unique);
Tier is the skill gate. Fixed region difficulty decides the TIER BAND
per region: the blacksteel canyons hold T4 swords, the starting meadow
caps at T2, no matter how often you farm either. The crossing rule
keeps low-level named finds exciting without polluting endgame tables
with common junk.

### 3. Vendor economy (three court families)
- LIGHT VENDORS (Guild/Church, towns and holds): blessed components,
  consecrated silver, Holy reagents (axis-attuned, burn in evil hands
  at the counter), Holy Wards tomes (axis-gated purchase), mid-tier
  weapons/armor, T1-T2 recipes. Aegis-adjacent goods NEVER sold to
  non-deep-good (locked: Aegis is craft-exclusive; vendors sell the
  components only to crafters who can use them).
- DARK VENDORS (covens, undead/vampire courts, dark holds): corruption
  reagents, blacksteel, Dark Pacts tomes (axis-gated), dark-court gear,
  catalyst supplies.
- NEUTRAL BROKERS (mercenaries/smugglers/underworld, accept any
  affinity): sell to anyone, stock the recipe trade, alchemical
  throwables, mid-tier everything, AND are one of the three
  legendary-station clue sources (purchased intel, doc 05). Standing
  with the neutral court lowers prices and deepens stock.
- REQUISITION CONTRACTS (locked in doc 05 economy hooks, expanded):
  anyone sells materials to anyone for coin, but COURT contracts pay
  standing + coin, and standing gates each court's better stock. A
  hunter's selling pattern therefore visibly feeds their political
  position.

### 4. Hunter's Relics (named items)
- HAND-AUTHORED, one per item, lore-bearing, never random drops. Each
  has a FIXED acquisition story: a specific boss, a specific grave, a
  specific hidden vault, or a court questline reward.
- All relics are Tier-5 (Grandmaster gear gate), which makes Grandmaster
  weapon skill the relic-readiness gate and gives the diminishing-curve
  grind a treasure at the end.
- Reforgeable (doc 18 Reforge technique re-rolls stats in place);
  never reverse-engineered, never duplicated (doc 05).
- WORKING TARGET: one relic per combat line (9) plus a small set of
  armor/charm relics (~6), authored during the GDD with their
  acquisition stories.

### Open questions added by this section (also in 08):
1. Exact per-biome table weights and drop-rate numbers: tuning, GDD.
2. Relic list authoring (9 weapons + ~6 armor/charms + stories):
   GDD content.
3. Whether neutral brokers' legendary-station intel is a fixed
   inventory item per broker or a Speechcraft-gated reveal: quests GDD.

## Open Questions (current state - first-draft questions resolved)
- Node respawn: RESOLVED (2-3 days). Inventory system: RESOLVED (weight).
- Grave-looting consequences: RESOLVED (light-court reputation cost).
- Fishing: RESOLVED (full skill line).
- Node density per region: RESOLVED 2026-09-12 (Nicko, world GDD
  tuning, doc 03): MODERATE, ~6-10 gatherable nodes per hold
  region per type; denser farmland/swamps, sparse blight.
- Rare-node UI hint (glint vs pure observation): GDD-stage art decision,
  leaning glint for readability of 512-1024px sprites at distance.
- Loot economy (section above): LOCKED 2026-09-12 (four-layer tables,
  Rarity-vs-Tier crossing rule, three vendor families, Hunter's Relics
  spec).
