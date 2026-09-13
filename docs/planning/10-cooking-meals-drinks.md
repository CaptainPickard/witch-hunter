# 10 - Cooking, Meals, and Drinks

Proposed 2026-09-11 by Nicko. Cooking expands from a campfire flourish into a
full system: daily meals and drinks as loadout decisions that shape the day.

## Design Intent
Food is buff-only, never a survival tax: starving is not a mechanic, but
eating WELL is. Certain camp gear is still required to camp (see
09-expedition-camping), but food exists to make tomorrow's plan stronger.
Recipe knowledge becomes a mechanic in itself: knowing what to cook for what
you intend to do is a real player skill.

## Daily Consumption Rules
- Per in-game day the player can consume exactly ONE meal and ONE drink.
- Buffs from each last the day. Plan the night before; eat for the day you
  intend to have.

## Synergy Rules (locked with Nicko, 2026-09-11)
"Ingredients that go together" is defined by TWO axes:
1. FLAVOR FAMILIES - ingredients belong to families (vegetable, meat, grain,
   fungal, arcane, etc.). Dishes are identified by the family composition:
   e.g. three vegetable-family ingredients form a vegetable dish.
2. REGIONAL PAIRINGS - which regions the ingredients come from. A vegetable
   dish built from 3 ingredients sharing a regional pairing becomes a
   RATATOUILLE (a named dish). Region identity + flavor family = dish recipe
   discovered through play, not a menu list.

## Meal Grading (locked with Nicko, 2026-09-11)
Dishes have GRADES:
- The base dish (e.g. ratatouille) is formed by the 3-ingredient synergy
  match.
- A 4th ingredient, chosen by flavor family and spice compatibility, can
  UPGRADE the dish to a higher grade.
- Higher grades do more than lower grades: stronger buff magnitudes, longer
  duration, or better bonus-effect rolls.
- Practical reading: 3 ingredients = base dish; 4th complementary ingredient
  = upgraded dish; wrong 4th ingredient = base dish (or worse). Cooking skill
  and recipe knowledge determine whether the player can identify which 4th
  ingredient upgrades vs. ruins the dish.
- Grading gives cooking a completionist layer: every dish has a grade ladder
  to climb, and tavern cooks/NPCs can teach higher-grade variants.
- Ingredient archetypes map to stats:
  - Hearty ingredients -> Health
  - Lean/grain ingredients -> Stamina
  - Arcane/rare ingredients -> Focus
  - Exotic/rare ingredients -> derived stats: Luck, Charisma, Precision,
    Ward, Speed, etc.
- Recipes are discovered (found, bought, learned from tavern cooks and
  faction contacts), not menu-gated. A cooked meal's effects are visible
  after cooking; mastery is knowing what to combine BEFORE you commit.

## Meals as Daily Strategy
The meal is the player's "loadout for the day":
- Wilderness expedition tomorrow -> combat-stat meals (Strength/Stamina/
  resistances) are vitally important.
- Town/social day tomorrow -> Charisma- and Luck-based foods become the
  strategy (better prices, faction disposition, gambling/rumor outcomes).
- Dungeon dive -> Ward and Focus foods for trap and spell pressure.
This is optional content that greatly benefits players who engage with it -
a knowledge check that rewards planning, consistent with the project's
specialization philosophy.

## Drinks
- One drink per day. A drink is ANY consumable potion (found or crafted)
  that is NOT a health, magic (focus), or stamina potion.
- Drinks are utility consumables, e.g. a Potion of Frost Protection granting
  immunity to cold/frost traps and attacks for the day.
- This creates a clean economy split:
  - Health/Focus/Stamina potions = combat resources (spam during an
    expedition, limited by carry weight).
  - Drinks = strategic daily buffs (protection, luck, social, movement),
    limited to one per day.
- Healing spells/potions remain the healing channel (04-combat); drinks never
  heal.

## Sourcing
- Ingredients come from gathering (Herbalism, Hunting/Skinning), monster
  parts, loot, and vendors.
- Salt and other amplifier ingredients are vendor staples and rare deposits
  in certain biomes.
- Recipes: found in taverns (cooks sell hints), faction requisitions, and
  dungeon rewards. Tavern cooks can also cook FOR you if you bring
  ingredients (paid service) - early-game onramp before Cooking skill
  exists.

## Cooking Skill Line (proposed)
Cooking becomes its own skill line within the ~25-skill budget:
- Levels by cooking meals (use-based, like everything else).
- Higher skill: stronger buff magnitudes, more synergy effects recognized,
  access to rarer ingredient handling (monster parts, exotic herbs), better
  "bonus effect" pools.
- Synergizes with Herbalism (ingredient knowledge) and the gathering loops.

## COOKING GDD: WARD-DISH GRAMMAR (locked 2026-09-12, Nicko)

SYSTEM (locked): every biome's signature dishes counter that
biome's threats. Lore: eating the land's danger tames it (Old
Faith table-magic, predating the pact, doc 22; coven-territory
food is the best and slightly tainted).
- ATTACK dishes: built from the biome's MONSTER-PART ingredients
  (doc 06 monster-part-first). Eating what you hunt grants
  +1-tier flavor against that biome's common enemy grammar
  (poise damage vs beasts, Ward-pierce vs undead, stagger-resist
  vs packs). Attack buffs key to doc 04's universal grammar:
  poise damage, stagger windows, bleed, crit.
- DEFENSE dishes: built from the biome's HERB SIGNATURES
  (doc 03's locked lists) and resist that biome's ambient threat.
- GRADES scale magnitude and duration (doc 10's locked ladder);
  salt amplifies (locked); the 4th ingredient upgrades (locked).
- RARE BONUS POOL (locked, doc 10 open item): rare 4th
  ingredients can roll special effects. First-pass pool of 10:
  corpse-recovery insurance (next death drops at the tavern, not
  the corpse), calm-night (one guaranteed ambush-free night),
  second-meal grace (yesterday's buff carries one extra hour),
  warm-blood (no cold-shiver stagger on first blizzard hit),
  hunter's eye (rare-node glint range doubled), salt-tongue
  (identify a dish's upgrade ingredient on sight), den-key
  (one neutral den revealed on the map, doc 03 shadow court),
  moon-haze (wolf-strain Howl fear reduced), tithe-sate (hunger
  of the strains: wild wolves ignore you one night), ledger-
  page (one free rumor purchase at any tavern).

### TAVERN MEALS (locked, doc 10 open item)
Cheap convenience tier at every tavern (the innkeeper's simple
fare): fixed minor buff WELL-FED (small stamina-regen bonus),
no customization, no recipe knowledge needed. Taverns stay the
save/rumor hub with a light food hook; no inventory bypass.

## PER-BIOME DISH SETS (authored 2026-09-12, Nicko)

Each biome: the enemy list it must answer (doc 04 grammar, doc
03/19 spawns), then its dish kit. ~7 dishes per biome, ~43 total.

### 1. DARKWOOD FORESTS
ENEMIES: coven-bound witch-fauna, wild wolf strains (altar-edge
dens, doc 03), bandits, boar-tusk and bear beasts, cursed things.
- ATTACK: WOLF-HEART STEW (wolf part + moonbell + onion): +poise
  damage vs beasts (their high poise is the test). 4th: boar-tusk
  leather is WRONG (fatty, downgrades); coven sinew UPGRADES.
- ATTACK: TUSK-RAGOUT (boar-tusk meat + root veg + crow-garlic):
  bleed stacks vs beasts and bandits (Axes grammar on a plate).
- ATTACK: WITCH-FLEW BROTH (witch-fauna part + hemlock-honey +
  grain, Warden-authenticated): crit vs witch-fauna (their
  bound-creature poise is low but their Ward is high).
- DEFENSE: GLADE-KNOT PORRIDGE (oak-crafted grain + moonbell +
  grave-moss): resist witch curses (coven hex duration -50
  percent). 4th: witchwood smoke-salt UPGRADES to full hex-
  immunity for one fight.
- DEFENSE: THE TENDER'S STEW (3 Darkwood herbs + coven glade
  honey): taint-creep resistance (doc 17 bands), for harvesting
  witchwood safely.
- DEFENSE: HUNTER'S DARKBREAD (darkwood grain + bear fat + salt):
  night-ambush notice (+early audio cue on night ambushes, the
  doc 04 ambush grammar, one warning per ambush).
- DRINK: GREEN VEIL-STEEP (moonbell + blightcap edge-pick): see
  through Darkwood fog as if it were clear (fog = Darkwood's
  default weather, doc 03).

### 2. MOORS AND HIGHLANDS
ENEMIES: wights and ghouls (night-anchored undead), the Moor's
wight-bard, ghouls from barrows, evil packs, storm-front beasts.
- ATTACK: WIGHT-MARROW BROTH (wight bone-ash + barley + bog-
  myrtle): Ward-pierce vs undead (their relentless pressure
  answers nothing to Ward: this answers them). 4th: barrow-bone
  UPGRADES (sympathetic eating, doc 06 grave economy).
- ATTACK: GHOUL-STEW (ghoul flesh + crow-garlic + hemlock-
  bitters): poise-shred vs undead walkers (their heavy poise).
- ATTACK: PACK-RAGOUT (wolf + pony + thorn-yew shoots): stagger-
  resist vs pack rhythm (dark-court packs bleed-and-retreat,
  doc 04: their rhythm is the weapon).
- DEFENSE: WATCHER'S PORRIDGE (thorn-yew grain + bog-myrtle +
  salt): cold-wind resistance (moor gales, doc 03 weather) and
  watchtower watchfulness ( +1 Precision at range).
- DEFENSE: THE UNWAILED POTTAGE (storm-thistle + bog-myrtle +
  heath herb): morale-break resistance (Wail of Despair and
  Terrifying Howl fear, doc 04/17 grammar) for the whole night.
- DEFENSE: BEACON-Keeper's HASH (drift-oak smoke-dried meat +
  grain + salt): beacon-warding (tower beacons gutter less in
  gales, doc 03; your camp's ambush risk drops one band).
- DRINK: STORM-CALLER'S DRAUGHT (storm-thistle steep): counts as
  Storm-caster sense-lite: feel the next Veil-Tide front 1 day
  earlier (doc 03 forecasting).

### 3. SWAMPLANDS
ENEMIES: hags and their bargains, drowned dead, swamp beasts,
disease vectors, miasma zones.
- ATTACK: DROWNED-MAN CHOWDER (drowned-dead flesh + eel + marsh
  heliotrope): Ward-pierce vs drowned dead (their grave-rot
  zones, doc 04 undead grammar). 4th: crypt-bloom UPGRADES
  (Dark-flavored).
- ATTACK: HAG-BANE FRICASSEE (hag-hide renderings + bloodroot +
  feverfew): +poise vs hags and their bound things (bargain-
  breakers' dish; eating it, hags will not bargain: they HUNT).
- ATTACK: EEL-SMOKE POTTAGE (eel-leather meat + bloodroot +
  grain): crit vs swamp beasts (leaping strikes on the
  mud-drunk).
- DEFENSE: FEVERFEW CURE-BOWL (feverfew + comfrey + marsh herb):
  disease resistance (the swamp's ambient threat, doc 10's
  drink-slot immune overlap is fine: this is the meal version).
- DEFENSE: HAG'S-REBUKE STEW (3 swamp herbs + salt): hag-bargain
  resistance (swamp dangers key off standing and bargains, doc
  03: this dish auto-refuses one bargain's fine print per day).
- DEFENSE: MIASMA-BREAD (blackwood-smoked grain + crypt-bloom +
  salt): Miasma of Decay zone resistance (doc 17 corruption
  kit, undead raiders' denial grammar).
- DRINK: STILL-WATER DRAUGHT (marsh heliotrope tonic): fishing
  and swimming stamina (Stillwater skill line, doc 06) plus
  Veil-Tide: Pale-Tide fog does not blind you.

### 4. MOUNTAINS AND PASSES
ENEMIES: cave clatterers (chitin), trolls, wyverns, blizzard
exposure, pass-raiders, garrison wars.
- ATTACK: CLATTERER-CRACK CHOWDER (chitin + mountain grain +
  high birch sap): +poise damage vs chitin armor (their shells
  ARE poise: doc 04 beast grammar).
- ATTACK: TROLL-BLOOD POT (troll sinew + ibex meat + frost
  herbs): stagger-resist vs trolls (their heavy poise swings)
  and +poise vs their regen-panic.
- ATTACK: WYRM-HEART STEAK (wyrm-scale shed meat + river-ash
  salt + thorn-yew): crit vs wyverns (T4-5 signature dish,
  Grandmaster-ingredient grade-shifter, doc 03 lists).
- DEFENSE: BLIZZARD-POT (frost herbs + ibex fat + salt): cold
  exposure immunity (mountains' main threat, weather-dominated,
  doc 03; passes stay open for you).
- DEFENSE: MASON'S PROVISION (mountain grain + hard cheese +
  salt): garrison-biome logistics (+Carry Weight effective for
  the day, doc 05/06 weight economy; the pass-carrier's meal).
- DEFENSE: DEEP-BREATH BROTH (glacial-herb + pine needle +
  snowmelt base): altitude stamina (stamina regen unpenalized
  at pass heights).
- DRINK: HEARTH-TODDY (frost-wisp distilled): frost immunity
  drink (doc 10's drink example made canonical here).

### 5. FARMLAND AND RIVER VALLEYS
ENEMIES: bandits, court soldiers (pairs: shield-and-spear),
night raiders, thrall-takers in dark-flipped holds, the
parish war's refugees-turned-desperate.
- ATTACK: SOLDIER-BREAKER HASH (raider-bandit part + kitchen
  veg + apple-wood smoke): +poise vs humanoid blocks (chip
  poise through blocks, doc 04: the shield-and-spear pair's
  answer). 4th: chapel-garden herb UPGRADES (the parish blesses
  the plate).
- ATTACK: RIVER-Pike PIE (pike + willow-smoked + grain): crit
  vs humanoids in duels (Duelist's Reading synergy, doc 04:
  the duel grows your crit, this starts it higher).
- ATTACK: SCARECROW'S DUE (bandit offal + root mash + salt):
  +damage vs thralls and undead raiders (the farmhold's grudge
  meal, doc 03's dark-flipped valleys).
- DEFENSE: THE PARISH PLATE (chapel-garden herbs + grain +
  honey): Militant/Mercy parish standing gain +25 percent for
  the day (doc 20 parish meters; the church supper).
- DEFENSE: GOOD-NEIGHBOR POTTAGE (farm veg + doe + salt):
  civilian trust (villagers treat you +1 disposition; rumor
  prices cheaper, doc 13 rumor economy).
- DEFENSE: WAKEFUL-WATCH WAFER (apple-wood grain + comfrey +
  salt): night-watch buff (sleep at night WITHOUT the full
  sleep risk once: a light player's one guarded night, doc 12
  clock; neutral players' bridge to the wolf law).
- DRINK: FARMWIFE'S CIDER (orchard press): social drink (doc 10
  drink slot: Charisma-flavored, +Speechcraft attempts).

### 6. BLIGHTED ZONES
ENEMIES: the concentrated witch threat, blight-wolves,
witch-hags, corrupted beasts, demons (invasion windows, doc
19/22), the blight itself (attrition, doc 03).
- ATTACK: DEMON-BAIT STEW (corrupted iron-ore-marinated meat +
  blightcap + salt): +damage vs demons (invasion windows:
  their flesh is the pact's, and the scar's food knows it).
  Eating = taint exposure even for dark players (doc 17
  bands), the cost on the plate.
- ATTACK: WITCH-BANE BLACK-POT (witch-hag part + blightcap +
  blightwood smoke): +Ward-pierce and +crit vs witch-fauna and
  hags (the concentrated threat's counter-dish; the doc 03
  witch-threat answer in a bowl).
- ATTACK: BLIGHT-WOLF CARRIER (blight-wolf part + grave-moss +
  feverfew): stamina-regen during hunts (the wolf-player's
  road food; wolves harvest ingredients unexposed, doc 03).
- DEFENSE: THE PROVISIONER'S FAST (3 preserved staples + salt,
  no blight ingredients): blight attrition HALF for the day
  (the counter to Ward-drain/taint-creep, doc 03 locked
  ambient model: you provision for the blight, literally).
- DEFENSE: AEGIS-ADJACENT POTTAGE (cold iron filings +
  chapel-garden herb + consecrated salt, deep-good craft
  only): full attrition immunity for one expedition, the
  Aegis rule's kitchen cousin (locked Aegis rule, doc 17).
- DEFENSE: THE PALE FASTING (crypt-bloom + blightcap + hag
  honey): undead-court tolerance (undead spawns read you
  neutral ONE night; doc 12's affinity visibility bent one
  night, the infiltration meal).
- DRINK: UNDERTOW-NAUSEA DRAUGHT (blightcap + bloodroot):
  Veil-Tide interaction (doc 03): function inside a Pale
  Tide's fog without the Veil-charged pressure.

### SALT AND AMPLIFIERS (doc 10 sourcing, grounded)
- SALT: vendor staple everywhere; RARE DEPOSITS: the moor
  march's old salt-pans (the cleansable scar's post-cleanse
  industry, doc 03) and the southern coast.
- Veil-Tide note: VEIL-CHARGED fronts make ALL meals +1 grade
  roll (doc 03 charge rules' flavor-tier reach), Sun-charged
  fronts make Holy-adjacent meals (chapel-garden, Aegis-
  adjacent) +1 grade roll.

## Open Questions (current state)
1. Synergy rules: RESOLVED - flavor families + regional pairings; dish
   identity emerges from family composition + region match (e.g.
   ratatouille). Salt/spice acts as amplifier and grade-up ingredient.
2. Bonus-effect pool rare/unique effects (corpse recovery, calm
   night): RESOLVED 2026-09-12 (Nicko, doc 10 GDD section): RARE
   BONUS POOL LOCKED with 10 first-pass effects (corpse-recovery
   insurance, calm-night, second-meal grace, warm-blood,
   hunter's eye, salt-tongue, den-key, moon-haze, tithe-sate,
   ledger-page).
3. Station gating: RESOLVED - campfire cooks 3-ingredient meals only; a
   KITCHEN unlocks 4th-ingredient grading (warp-camp kitchen = mid-game
   power spike). Station ladder: campfire < tavern kitchen < warp camp
   kitchen.
4. Ingredient spoilage: RESOLVED - raw ingredients NEVER spoil; weight is
   the only inventory pressure.
5. Drink slot: RESOLVED - one drink per day, any non-health/magic/stamina
   potion; combat potions unaffected.
6. Pre-made tavern meals (innkeeper convenience): RESOLVED
   2026-09-12 (Nicko, doc 10 GDD section): cheap convenience
   tier, fixed WELL-FED minor buff, no customization.
7. Grade scale: RESOLVED - FIVE grades (Common/Fine/Remarkable/Exquisite/
   Masterwork); recipe knowledge gates attempt, Cooking skill gates
   success odds and magnitude (locked combo).
8. Gating combo: LOCKED (see 7).
9. Fry Cook specialty: confirmed in the specialties system (doc 16); full
   specialty mechanics in the specialties pass.