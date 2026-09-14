# 40 - Armor Tier Catalog and Material Sourcing

Status: PROPOSED, IO bake from Nicko session directives 2026-09-14, pending
Nicko lock. Rulings 1-4 below are LOCKED in session. Every armor piece
name, sourcing weight, ingredient mapping, and anchor percentage in the
parts below is PROPOSED unless marked otherwise.

## SESSION RULINGS (locked by Nicko, 2026-09-14)

1. FULL CATALOG: all 3 weight classes x 5 tiers x 4 armor slots authored
   now (60 per-piece names), with primary materials, secondaries, and
   sourcing paths. Armor values derive from doc 33 formulas, no new math.
   Multi-pass authoring expected.
2. HEAVY LADDER: heavy armor primary is the METAL PLATE ladder (iron,
   silvered scale, steel, cold iron, blacksteel), matching the weapons
   metals ladder. Doc 38's T4 heavy row (wyrm-leather primary with cold
   iron reinforcement) is superseded; wyrm-leather moves to a PROPOSED
   T4-T5 light/medium alternative primary (open question 4).
3. NAMING: 60 per-piece names (New World style), not 15 set names.
4. DROP FORMAT: named sources and weighted rarity bands per area,
   dungeon type, and vendor family for every tier, mirroring doc 39's
   structure. A few anchor percentages get locked where exact odds are
   wanted; everything else stays weight-based for GDD tuning.
5. ALL-CRAFTABLE CHECK (canon, doc 05 locked): all armor is craftable at
   the camp EXCEPT the Hunter's Relic armor pieces (Named T5, Reforge-
   only, doc 06) and spine-story items. Craftable armor therefore spans
   T1-T5 via the materials-set-tier rule (doc 38's craftable T5
   blacksteel blade is the precedent), while the ~6 relic armor/charm
   pieces are story-authored finds.
6. UPGRADE PATH (locked by Nicko, 2026-09-14): craft-new-only. There is
   NO in-place armor upgrade; the material-tier ladder IS the upgrade
   path (Part 5). Doc 05's Armorsmithing "upgrade paths" phrase is
   resolved as this ladder. Reforge stays Named-item-only (doc 18).
7. DISASSEMBLY (locked by Nicko, 2026-09-14): ALL items disassemble
   into raw materials. Disassembly is its own SKILL LINE (core line 29,
   doc 15) that levels by use: higher rank yields more raw materials
   and raises the chance of rare-material recovery. Full mechanic spec
   lives in doc 05 (DISASSEMBLY section); doc 15 carries the roster
   entry.

## CONVENTIONS

- Tiers T1-T5 per the doc 18 gear gate (T2 Apprentice, T3 Adept, T4
  Expert, T5 Grandmaster). Grade ladder C/B/A/S per doc 33.
- Armor numbers: doc 33 section 2 flat ladder per slot and weight class
  (grade B light set 5 armor / 5.5 weight, medium 9 / 10.5, heavy 15 /
  19.0), multiplied by the doc 33 tier ladder (T1 1.00, T2 1.35, T3
  1.75, T4 2.20, T5 2.70) and the grade multiplier. This doc carries NO
  armor numbers; every piece derives from its slot row x tier x grade.
- Slots: HEAD, CHEST, HANDS, BACK only (doc 33 section 1). BACK carries
  cloak armor (light only per slot table) and quiver if archer. The doc
  27 CANON LAYERS are visual, never slots.
- Weight class choice is a real build choice via doc 33 equip load bands
  (LIGHT 0-10.0 fast roll, MEDIUM 10.1-20.0 standard, HEAVY 20.1-30.0
  slow roll, above 30 disabled) and poise factors (light 1.0, medium
  1.5, heavy 2.2).
- Crossing rule (doc 06, locked): T1-T2 gear spans all rarities, T3 is
  mostly Uncommon/Rare, T4 is Rare/Named only, T5 is Named only. Craft
  exception: craftable T5 armor exists per ruling 5 (Grandmaster,
  doc 38 precedent); random T5 DROPS do not.
- Rarity bands used here: ABUNDANT / COMMON / RARE / STORY (Named).
  Rows marked ANCHOR carry a locked percentage proposal for Nicko.
- Ingredient system (doc 05, LOCKED New World adaptation): the primary
  material sets the tier; category secondaries shift the grade roll;
  the same item cannot fill two slots in one recipe; station tier caps
  refine ceilings. Doc 38's refining tables and ceilings carry
  unchanged (S1 hides T1-T2, S2 steel, S4 cold iron/wyrm, S5
  blacksteel).
- Biome sourcing follows doc 03's locked biome roster and doc 06's
  layer-2 regional specialization. Dungeon sourcing follows doc 06's
  dungeon-type keys and doc 37's Descent Gates (rarity escalates within
  the regional tier band per stratum).

## PART 1 - PRIMARY MATERIAL LADDERS (armor)

### Hides (light class primary; medium class primary)

| Tier | Primary hide | Source (doc 03/06 locked) | Refine (doc 38) |
|---|---|---|---|
| T1 | doe leather | farmland and river valleys hunting, all vendors | S1 |
| T2 | wolf hide | darkwood dens, moor packs, town vendors | S1 |
| T3 | boar-tusk leather / eel-leather | darkwood signature beasts / swamplands | S2 |
| T4 | ibex hide / snow-cat hide | mountain strata 2+ / mountain snow strata | S4 |
| T5 | ghoul-hide | moor barrows, mountain crypts, blight; dark vendors (raw) | S4 (S5 wyrm T5) |

Wyrm-scale to wyrm-leather stays the doc 38 special case: T4 at S4, T5
at S5, PROPOSED here as an ALTERNATIVE T4-T5 light/medium primary (open
question 4), not the heavy ladder.

### Metals (heavy class primary; medium fittings secondary)

Same ladder as doc 39 Part 1, one table for both uses:

| Tier | Primary metal | Source (doc 03 locked) | Refine (doc 38) |
|---|---|---|---|
| T1 | iron ingot | mountain common veins, dungeon mine walls, all vendors | S1 |
| T2 | silver ingot | moor barrows + mountain seams, light vendors | S1 |
| T3 | steel ingot | mountain deep seams, war camps (faction gear), town vendors | S2 |
| T4 | cold iron ingot | mountains + blight scars ONLY, Rare/Named finds | S4 |
| T5 | blacksteel ingot | blight ore-scars + strata 3-4, dark vendors (raw only) | S5 |

Medium-class metal fittings use the same ladder one step down as
CATEGORY secondaries: iron bosses (T1), silver fittings (T2), steel
ribs (T3), cold iron clasps (T4), blacksteel ribs (T5).

### Cloth and bindings (all classes)

| Tier | Material | Source | Refine |
|---|---|---|---|
| T1-T2 | comfrey fiber to cloth (PROPOSED processing, doc 38) | farmland, river valleys | S1 |
| T1-T2 | common bones (binding) | any hunting loop | none (raw) |
| T2 | barrow-bone (binding, grave-wrought flavor) | moor barrows, crypts | none (raw) |
| T3 | troll sinew, hardened chitin | mountain beasts | none (raw) |
| T4-T5 | wyrm-sinew | wyrm hoards, mountain strata 3+ | none (raw) |
| T5 | tainted lining (tallow-hide) | blight zones, dark vendors | none (raw) |

## PART 2 - THE 60-PIECE ARMOR CATALOG

All names are PROPOSED working names. Secondaries follow doc 05
categories: lining hide, binding sinew, metal fittings, cloth lining.
Rarity band per the crossing rule. Sources name the locked biome,
dungeon type, vendor family, or relic story slot. Per ruling 1: every
piece derives its numbers from doc 33, no new math.

### LIGHT (leather; doc 33 grade-B set: 5 armor / 5.5 weight, poise 1.0, fast roll)

| Tier | HEAD | CHEST | HANDS | BACK | Primary | Secondaries | Sources | Band |
|---|---|---|---|---|---|---|---|---|
| T1 | Doe-Skin Cowl | Farmhand's Jerkin | Poacher's Gloves | Traveler's Shawl | doe leather | common bones (binding), cattle-hide (lining) | farmland hunting, all T1 vendors | ABUNDANT |
| T2 | Wolfsblood Hood | Moor-Ranger Jerkin | Ranger's Wraps | Yew-Watcher's Mantle | wolf hide | common bones, doe trim | darkwood/moors hunting, town vendors, T2 dungeon gear layer | COMMON |
| T3 | Bog-Stalker's Hood | Bog-Stalker's Jerkin | Eel-Skin Grips | Reed-Warden Cloak | boar-tusk leather / eel-leather | troll sinew, cattle-hide lining | darkwood signature beasts, swamplands, coven dens | COMMON/RARE |
| T4 | Frostwatch Hood | Frostwatch Jerkin | Snow-Cat Paw Grips | Pass-Watcher's Cloak | ibex hide / snow-cat hide | troll sinew, ibex trim | mountain strata 2+, blight scars | RARE |
| T5 | Ghoul-Weave Cowl | Ghoul-Weave Jerkin | Grave-Silent Grips | Veil-Dampened Cloak | ghoul-hide | wyrm-sinew (binding), tallow-hide lining | moor barrows, mountain crypts, blight; Grandmaster craft | STORY territory + Grandmaster craft |

### MEDIUM (layered hide + metal fittings; doc 33 set: 9 / 10.5, poise 1.5, standard roll)

| Tier | HEAD | CHEST | HANDS | BACK | Primary | Secondaries | Sources | Band |
|---|---|---|---|---|---|---|---|---|
| T1 | Boiled-Leather Cap | Brigandine Vest | Layered Gloves | Scout's Cape | doe leather | iron bosses (fittings), common bones | farmland, all T1 vendors, bandit war camps | ABUNDANT |
| T2 | Silver-Bossed Coif | Silver-Bossed Brigandine | Silver-Knuckled Gloves | Watch-Guard Cloak | wolf hide | silver fittings, doe lining | town vendors, crypt gear layer, war camps | COMMON |
| T3 | Steel-Ribbed Coif | Steel-Ribbed Brigandine | Steel-Plate Gloves | Siege-Runner's Cape | boar-tusk leather / eel-leather | steel ribs, troll sinew | war camps, hold sieges, moor/mountain dungeons | COMMON/RARE |
| T4 | Cold-Iron Clasped Coif | Cold Iron Brigandine | Cold-Iron Clasped Gauntlets | Warden's Ward-Cloak | ibex hide | cold iron clasps, wyrm-sinew | mountain strata 2+, blight scars | RARE |
| T5 | Blacksteel-Ribbed Coif | Blacksteel Brigandine | Blacksteel Gauntlets | Night-Warden's Cloak | ghoul-hide | blacksteel ribs, tallow-hide lining | blight, strata 3-4; Grandmaster craft | STORY territory + Grandmaster craft |

### HEAVY (metal plate; doc 33 set: 15 / 19.0, poise 2.2, slow roll)

| Tier | HEAD | CHEST | HANDS | BACK | Primary | Secondaries | Sources | Band |
|---|---|---|---|---|---|---|---|---|
| T1 | Iron Kettle Helm | Iron Cuirass | Iron Vambraces | Soldier's Half-Cloak | iron plate | doe lining, common bones (strap binding) | all T1 vendors, bandit war camps, mine walls | ABUNDANT |
| T2 | Silvered Sallet | Silvered Scale Cuirass | Silvered Gauntlets | Herald's Mantle | silvered scale | wolf lining, barrow-bone binding | town vendors, war camps, crypt gear layer | COMMON |
| T3 | Steel Great-Helm | Steel Plate Cuirass | Steel Rerebraces | Siege-Banner Cloak | steel plate | cattle-hide lining, troll sinew | war camps, hold sieges, mountain dungeons | COMMON/RARE |
| T4 | Cold Iron Visor Helm | Cold Iron Cuirass | Cold Iron Gauntlets | Witch-Warden's Mantle | cold iron plate | ibex lining, wyrm-sinew | mountain strata 2+, blight scars | RARE |
| T5 | Blacksteel Dread-Helm | Blacksteel Bulwark Cuirass | Blacksteel Talon Gauntlets | Dread-Warden's Cloak | blacksteel plate | ghoul-hide lining, wyrm-sinew | blight, strata 3-4; Grandmaster craft | STORY territory + Grandmaster craft |

BACK-slot note: doc 33 gives BACK armor 0 (light) / 1 (medium) / 1
(heavy) at grade B, so cloaks are mostly flavor + quiver carrier at low
tiers; tier multipliers keep them marginal by design. No rebalance here.

## PART 3 - SOURCING MATRIX (bands + anchors)

Named sources per area/dungeon type/vendor family, per ruling 4. Bands
are weight-based; this is the doc 06 layer-3 (gear) resolution for
ARMOR, parallel to doc 39's weapon resolution.

### Region tier bands (fixed difficulty, doc 06 locked)

| Region | Armor tier band | Notes |
|---|---|---|
| Farmland + river valleys | T1-T2 | starting meadow caps at T2 (doc 06); doe/cattle hide home |
| Darkwood forests | T1-T3 | wolf/boar-tusk home, coven dens carry tainted pieces |
| Moors + highlands | T2-T3 | barrow-bone and silver fittings home |
| Swamplands | T2-T4 | eel-leather home, hag-country mid band |
| Mountains + passes | T3-T4 | steel, cold iron, ibex, snow-cat, wyrm home |
| Blight zones | T4-T5 | blacksteel and ghoul-hide home, Named territory |
| Descent Gate strata 1-4 | +rarity within band per stratum | doc 37 ruling: strata at 10/20/30/40 |

### Dungeon-type armor weighting (doc 06 layer-3 keys)

| Dungeon type | Armor profile |
|---|---|
| Crypts/cemeteries | grave-wrought mid tier, barrow-bone and ghoul-hide pieces, holy wards |
| Mines | metals and plate tier up, smithing materials, gem-bearing strata |
| Coven dens | tainted leathers, witch-ward armor, dark charms |
| War camps | heavy plate share, steel-tier faction gear of every class (doc 12 court skins) |
| Hold sieges | T3-T4 heavy and medium, siege-quality plate |
| Descent strata | rarity escalation within the region band (doc 37) |

### VENDOR SOURCING (doc 06 three families)

| Vendor family | Armor stock |
|---|---|
| Light (Guild/Church) | T1-T3 doe/wolf/boar leathers, silvered mid tier (T2 silver-bossed and silvered scale), mid-tier cloth, consecrated components (axis-gated) |
| Dark (covens/undead courts) | blacksteel RAW materials, ghoul-hide raw, tainted/tallow gear, dark-court plate |
| Neutral brokers | mid-tier everything (T2-T3 all classes), recipe trade, alchemical supplies |

### ANCHOR PERCENTAGES (PROPOSED anchors, Nicko locks exact numbers)

1. ANCHOR AR1, dungeon gear-layer Named chance: mirrors doc 39 A1. A
   T1-T2 Named relic find in its story location is guaranteed by the
   story (doc 06 hand-authored rule); random Named drops do NOT exist
   at any tier. Anchor: 0 percent random Named everywhere.
2. ANCHOR AR2, T4 armor drop weight inside a T4-band dungeon gear
   layer: 5 percent of layer-3 gear rolls (mirrors doc 39 A2). Anchor
   for Nicko.
3. ANCHOR AR3, war-camp heavy-armor share: 20 percent of layer-3 gear
   rolls in war camps are heavy-class armor of any tier in band (armor
   analog of doc 39 A3's 40 percent steel-weapon share; armor is one
   axis across 3 classes vs weapons across 9, so the share is set
   lower). Anchor for Nicko.
4. Vendor armor stock refresh: 2-3 in-game days, matching the node
   respawn timer (doc 06 locked). No percentage; cadence only.

## PART 4 - INGREDIENT MAP (extends doc 38 Part 2/3 to full armor)

Doc 38 covered 3 representative armor recipes. The full 60-piece
spread uses the SAME chains and adds no new chains. Per-tier sourcing
map for every armor ingredient:

| Ingredient | Sets/feed | Tier | Source biome/location | Refine chain | Min station |
|---|---|---|---|---|---|
| doe leather | light/medium primary (T1) | T1 | farmland, river valleys | tanning liquor | S1 |
| cattle-hide | lining trim (T1-T3) | T1 | farmland ranches | tanning liquor | S1 |
| wolf hide | light/medium primary (T2) | T2 | darkwood dens, moor packs | tanning liquor | S1 |
| boar-tusk leather | light/medium primary (T3) | T3 | darkwood signature beasts | tanning liquor | S2 |
| eel-leather | light/medium primary (T3 alt) | T3 | swamplands rivers | tanning liquor | S2 |
| ibex hide | light/medium primary (T4) | T4 | mountain strata 2+ | tanning liquor | S4 |
| snow-cat hide | light primary (T4 alt) | T4 | mountain snow strata | tanning liquor | S4 |
| ghoul-hide | T5 light/medium primary; heavy lining | T5 | moor barrows, mountain crypts, blight | tanning liquor | S4 |
| wyrm-scale | wyrm-leather, PROPOSED T4-T5 light/medium alt | T4-T5 | wyrm hoards, mountain strata 3+ | tanning liquor | S4 (T5 at S5, doc 38) |
| iron ingot | heavy primary (T1); bosses (T1) | T1 | mountain common veins, mine walls, all vendors | quench salts | S1 |
| silver ingot | heavy primary (T2, silvered scale); fittings (T2) | T2 | moor barrows, mountain seams, light vendors | quench salts | S1 |
| steel ingot | heavy primary (T3); ribs (T3) | T3 | mountain deep seams, war camps | quench salts | S2 |
| cold iron ingot | heavy primary (T4); clasps (T4) | T4 | mountains + blight scars ONLY | quench salts + arcane ash | S4 |
| blacksteel ingot | heavy primary (T5); ribs (T5) | T5 | blight ore-scars, strata 3-4, dark vendors raw | quench salts + arcane ash | S5 |
| common bones | binding (T1-T2) | T1-T2 | any hunting loop | none | raw |
| barrow-bone | binding (T2 grave-wrought) | T2 | moor barrows, crypts | none | raw |
| hardened chitin | binding (T3) | T3 | mountain clatterers | none | raw |
| troll sinew | binding (T3-T4) | T3 | mountain trolls | none | raw |
| wyrm-sinew | binding (T4-T5) | T4-T5 | wyrm hoards, strata 3+ | none | raw |
| tallow-hide | tainted lining (T5) | T5 | blight zones, dark vendors | none | raw |
| comfrey cloth | cloak/clothing lining (T1-T2) | T1-T2 | farmland, river valleys | comfrey fiber processing (PROPOSED, doc 38) | S1 |
| tanning liquor | catalyst, all hide refines | - | Alchemy craft or vendors | - | - |
| quench salts | catalyst, all metal refines | - | Alchemy craft or vendors | - | - |
| arcane ash | catalyst, cold iron + blacksteel refines | - | Alchemy craft or vendors | - | - |

Tier-at-which-craftable gate: a piece is gated by BOTH the crafting
skill tier (doc 18: T2 Apprentice, T3 Adept, T4 Expert, T5 Grandmaster)
and the refine ceiling above. Station ceilings carry from doc 38
unchanged. Hunter's Components (doc 05, locked) guarantee armor wards:
the Cracked Ward Stone example guarantees a stamina-regen armor ward;
the armor-side component catalog is authored with doc 38's deferred
Hunter's Components doc.

## PART 5 - THE NEW WORLD QUALITY PATH (how higher-quality armor is made)

This is the locked doc 05 system applied to armor, restated as the
player-facing upgrade loop. No new mechanics.

1. TIER UP: craft a new set from higher-tier primaries. Doe set to wolf
   set to boar-tusk/eel set to ibex set to ghoul-hide set (light);
   iron to silvered to steel to cold iron to blacksteel (heavy). The
   MATERIAL LADDER is the upgrade path: doc 05's Armorsmithing blurb
   mentions "upgrade paths"; this doc resolves that phrase as the
   material-tier ladder itself (open question 1 for confirmation).
   There is NO in-place armor upgrade: Reforge stays Named-item-only
   (doc 18).
2. QUALITY UP within a tier: better SECONDARIES feed the grade roll
   (Crude/Standard/Fine/Superior/Masterwork). Cheap secondaries craft
   fine; higher-tier or rarer category members shift odds toward
   Masterwork. Masterwork grants +1 enchant socket (the armor ward
   payoff).
3. STATION UP: grade ceiling is set by the station (doc 05 floor/
   ceiling model): Field Kit caps Standard, Village caps Fine, Town
   caps Superior, City caps Masterwork (Expert+ crafters), the maxed
   warp-camp Grandmaster station has best odds, and the one unmarked
   legendary dungeon station is the single best in the world (doc 05
   clue-trail rule).
4. WARD UP: enchant sockets on higher-grade armor take armor wards
   (resistance, thorns, stamina regen, doc 17); Hunter's Components
   guarantee specific wards; the arcane reagent ladder (doc 05, 3:1)
   supplies the enchanting costs; axis gates apply to Holy/Dark wards.
5. RELIC CEILING: the ~6 Named armor/charm relics (doc 06) sit above
   the whole craftable ladder, are never craftable, and are Reforge-
   only (doc 18).

## PART 6 - RELIC ARMOR (Named, never crafted)

Working target from doc 06: ~6 armor/charm relics, T5, hand-authored,
fixed acquisition stories. Four armor pieces + two charms PROPOSED to
fill the family; stories are GDD content per doc 06 open question 2.
All are STORY band, all obey ruling 5 (not craftable).

| Relic | Slot/class | Acquisition story hook (PROPOSED) |
|---|---|---|
| The Warden's Aegis Cuirass | CHEST, heavy | Warden arc questline terminal reward; cold iron plate faced in Aegis Quintessence |
| The Pale Queen's Shroud | BACK, light | Pale Queen arc (doc 44: the neutral underworld unifier): taken from her faction's vault |
| Gravedigger's Iron Hands | HANDS, heavy | the gravedigger's grave (doc 19 grave-whisper trail); the one T1-LOOKING Named piece, doc 06's "Named T2 relics exist as starter-region stories" made real at T5 |
| The Moor-King's Antlered Helm | HEAD, medium | the moor's wight-bard (doc 03): replayed Fall battles, the king's last stand |
| The Hexbreaker Charm | TALISMAN | light-court requisition line terminal; burns in evil hands |
| The Veil-Eye Talisman | TALISMAN | Hidden Court trust line; reads weather-edge and scouted intel |

## PART 7 - OPEN QUESTIONS

1. [08 TRACKER] Upgrade path ruling: RESOLVED 2026-09-14 (Nicko):
   craft-new-only confirmed. No in-place armor upgrade mechanic; the
   material ladder is the upgrade path.
2. [08 TRACKER] Anchor percentages AR2, AR3: RESOLVED 2026-09-14
   (Nicko): handed to GDD tuning per the doc 39 anchor precedent (no
   numbers lock without a playable build).
3. [08 TRACKER] Relic armor list (Part 6): RESOLVED 2026-09-14
   (Nicko): the 4 armor + 2 talisman split is CONFIRMED (Warden's
   Aegis Cuirass, Pale Queen's Shroud, Gravedigger's Iron Hands,
   Moor-King's Antlered Helm, Hexbreaker Charm, Veil-Eye Talisman).
   Stories are GDD content (doc 06 open question 2).
4. [08 TRACKER] Wyrm-leather role after the metal-plate heavy ruling:
   RESOLVED 2026-09-14 (Nicko): doc 38's T4 heavy recipe row amended to
   steel-plate primary; wyrm-leather stays the PROPOSED T4-T5
   light/medium alternative primary.
5. [08 TRACKER] Piece names (all 60 + 6 relic names): working names
   pending Nicko pass.
6. [08 TRACKER] T5 craftable-vs-crossing-rule tension: RESOLVED
   2026-09-14 (Nicko, doc 40 ruling 5): craftable armor spans T1-T5
   per the All-Craftable Principle; the crossing rule reads "random T5
   DROPS are Named only" with craft as the Grandmaster route.
7. [08 TRACKER] Disassembly skill line (ruling 7): RESOLVED 2026-09-14
   (Nicko): IO drafts a concrete first-pass curve (yield percentages,
   rank curve, technique names) next session for Nicko approval;
   numbers stay PROPOSED until then.

## RULING PASS (open-questions sweep, 2026-09-14, Nicko)
1. SILVER AT T2: CONFIRMED. Doc 05's five-metal ladder maps 1:1 to
   gear tiers T1-T5 (iron/silver/steel/cold iron/blacksteel);
   silver is the T2 primary, doc 40's heavy plate ladder stands.
2. DUAL-WIELD RELIC SLOTS: CONFIRMED (one slot). Named dual-wield
   pairs count as ONE relic slot against doc 06's 9-relic target.
3. AEGIS BULWARK: CONFIRMED crafted-not-dropped (deep-good
   exclusivity carries; never purchasable at any price).
4. GEM NAMES: CONFIRMED as locked working names (Chip/Deep/
   Vein-heart/Veil Star), gated by vein depth + region band.