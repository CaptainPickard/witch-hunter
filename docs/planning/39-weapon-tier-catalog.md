# 39 - Weapon Tier Catalog and Material Sourcing

Status: PROPOSED, IO bake from Nicko session directives 2026-09-14, pending
Nicko lock. Rulings 1-4 below are LOCKED in session. Every weapon name,
sourcing weight, gem name, and anchor percentage in the parts below is
PROPOSED unless marked otherwise.

## SESSION RULINGS (locked by Nicko, 2026-09-14)

1. FULL CATALOG: all 9 combat classes x 5 tiers authored now, with names,
   primary materials, and sourcing paths. Damage derives from doc 33
   formulas, no new math. Multi-pass authoring expected.
2. DROP FORMAT: named sources and weighted rarity bands per area,
   dungeon type, and vendor family for every tier. A few anchor
   percentages get locked where exact odds are wanted; everything else
   stays weight-based for GDD tuning.
3. GEM SYSTEM: gem drop chance from mining veins scales with mining
   rank; the Luck stat adds on top; gem TIER is gated by vein depth and
   region band (mountains richest). Cut gems socket into gear via Gem
   Crafting.
4. SEQUENCE: doc 38 locked first (commit ea263fe, 2026-09-14), doc 39
   authored on the locked base.

## CONVENTIONS

- Tiers T1-T5 per the doc 18 gear gate (T2 Apprentice, T3 Adept, T4
  Expert, T5 Grandmaster). Grade ladder C/B/A/S per doc 33.
- Tier multipliers and class baselines: doc 33 section 3 and 5. This doc
  carries NO damage numbers; every weapon derives from its class row x
  tier x grade x skill.
- Crossing rule (doc 06, locked): T1-T2 gear spans all rarities, T3 is
  mostly Uncommon/Rare, T4 is Rare/Named only, T5 is Named only.
- Rarity bands used here: ABUNDANT / COMMON / RARE / STORY (Named).
  Rows marked ANCHOR carry a locked percentage proposal for Nicko.
- Ingredient system (doc 05, locked): the primary material sets the
  tier; category secondaries shift the grade roll. Doc 38's 10
  representative gear recipes stay; this doc extends to the full
  weapon spread.
- Biome sourcing follows doc 03's locked per-biome lists. Dungeon
  sourcing follows doc 06's dungeon-type keys and doc 37's Descent
  Gates (rarity escalates within the regional tier band per stratum).

## PART 1 - PRIMARY MATERIAL LADDER (weapons)

### Metals (doc 05 master list, tier mapping PROPOSED for T2)

| Tier | Primary metal | Source (doc 03 locked) | Refine (doc 38) |
|---|---|---|---|
| T1 | iron ingot | mountain common veins, dungeon mine walls, all vendors | S1 |
| T2 | silver ingot | moor barrows + mountain seams, light vendors | S1 |
| T3 | steel ingot | mountain deep seams, war camps (faction gear), town vendors | S2 |
| T4 | cold iron ingot | mountains + blight scars ONLY, Rare/Named finds | S4 |
| T5 | blacksteel ingot | blight ore-scars + strata 3-4, dark vendors (raw only), Named | S5 |

Silver at T2 is PROPOSED: doc 05 lists five metals for five tiers and
doc 38 already maps iron T1, steel T3, cold iron T4, blacksteel T5,
leaving silver for T2. Silvered weapons read as the church-adjacent
mid tier (light vendors stock them, doc 06).

### Woods (bows, crossbow stocks, polearm shafts, handles)

| Tier | Primary wood | Source (doc 03 locked) |
|---|---|---|
| T1 | oak | common, every biome |
| T2 | yew | darkwood, moors |
| T3 | bog-oak (fine-grade bonus) / drift-oak | swamplands / moors |
| T4 | thorn-yew (watchtower-grade) / blackwood | moors / swamplands |
| T5 | witchwood (tainted) / blightwood (taint on harvest) | coven groves / blight |

## PART 2 - THE 9 x 5 WEAPON CATALOG

All names are PROPOSED working names. Secondaries follow doc 05
categories: handle wood, grip leather, binding sinew. Rarity band per
the crossing rule. Sources name the locked biome, dungeon type, vendor
family, or relic story slot.

### Short Blade (doc 33: 12 dmg, fast, crit identity)

| Tier | Name | Primary | Secondaries | Sources | Band |
|---|---|---|---|---|---|
| T1 | Hunter's Dirk | iron | oak, doe | farmland/darkwood vendors, T1 kills | ABUNDANT |
| T2 | Silvered Poniard | silver | yew, wolf | town vendors, T2 dungeon gear layer | COMMON |
| T3 | Steel Fang | steel | yew, boar-tusk | moors/mountains dungeons, coven dens | COMMON/RARE |
| T4 | Cold Iron Stiletto | cold iron | thorn-yew, ibex | mountain strata 2+, blight scars | RARE |
| T5 | The Veilneedle | blacksteel | witchwood, ghoul-hide | relic story slot (Named) | STORY |
### Long Blade (doc 33: 20 dmg, balanced arcs)

| Tier | Name | Primary | Secondaries | Sources | Band |
|---|---|---|---|---|---|
| T1 | Militia Longsword | iron | oak, doe | all T1 vendors, bandit war camps | ABUNDANT |
| T2 | Huntsman's Saber | silver | yew, wolf | town vendors, crypt gear layer | COMMON |
| T3 | Warbrand | steel | yew, boar-tusk | war camps, hold sieges, moor dungeons | COMMON/RARE |
| T4 | Cold Iron Falchion | cold iron | thorn-yew, ibex | mountain strata 2+, blight scars | RARE |
| T5 | The Pale Verdict | blacksteel | blackwood, ghoul-hide | relic story slot (Named, Pale Queen arc: the neutral underworld unifier, doc 44) | STORY |

### Blunt (doc 33: 22 dmg, stagger identity)

| Tier | Name | Primary | Secondaries | Sources | Band |
|---|---|---|---|---|---|
| T1 | Iron Maul | iron | oak, doe | all T1 vendors, T1 kills | ABUNDANT |
| T2 | Silver-Socketed Cudgel | silver | yew, wolf | town vendors, war camps | COMMON |
| T3 | Steel-Head Bevel | steel | bog-oak, boar-tusk | hold sieges, war camps | COMMON/RARE |
| T4 | Cold Iron Sledge | cold iron | thorn-yew, ibex | mountain strata 2+, blight scars | RARE |
| T5 | The Gravewright | blacksteel | blackwood, ghoul-hide | relic story slot (Named) | STORY |

### Axes (doc 33: 24 dmg, bleed identity)

| Tier | Name | Primary | Secondaries | Sources | Band |
|---|---|---|---|---|---|
| T1 | Woodcutter's Axe | iron | oak, doe | all T1 vendors, farmland tool-turn-weapon | ABUNDANT |
| T2 | Silver-Rimed Cleaver | silver | yew, wolf | town vendors, crypt gear layer | COMMON |
| T3 | Steel Splitter | steel | yew, boar-tusk | war camps, mountain dungeons | COMMON/RARE |
| T4 | Cold Iron Reaver | cold iron | thorn-yew, ibex | mountain strata 2+, blight scars | RARE |
| T5 | The Hollow Hewer | blacksteel | blightwood, ghoul-hide | relic story slot (Named) | STORY |

### Polearms (doc 33: 18 dmg, reach identity)

| Tier | Name | Primary | Secondaries | Sources | Band |
|---|---|---|---|---|---|
| T1 | Boar Spear | iron | oak, doe | all T1 vendors, farmland/moors hunting loop | ABUNDANT |
| T2 | Silver-Butted Glaive | silver | yew, wolf | town vendors, war camps | COMMON |
| T3 | Steel Pike | steel | drift-oak, boar-tusk | war camps, hold sieges | COMMON/RARE |
| T4 | Cold Iron Halberd | cold iron | thorn-yew, ibex | mountain strata 2+, blight scars | RARE |
| T5 | The Warden's Reach | blacksteel | witchwood, ghoul-hide | relic story slot (Named, Warden arc) | STORY |

### Archery (doc 33: 16 dmg, dual-mode aim)

| Tier | Name | Primary | Secondaries | Sources | Band |
|---|---|---|---|---|---|
| T1 | Hunter's Shortbow | oak | doe binding, common sinew | all T1 vendors, hunting loop | ABUNDANT |
| T2 | Yew Warbow | yew | wolf binding, common sinew | town vendors, moor dungeons | COMMON |
| T3 | Bog-Oak Longbow | bog-oak | boar-tusk binding, troll sinew | swamplands/moors dungeons, coven dens | COMMON/RARE |
| T4 | Blackwood Composite | blackwood | ibex binding, troll sinew | mountain strata 2+, swamplands strata | RARE |
| T5 | The Moonlit Draw | witchwood | ghoul-hide binding, wyrm-sinew | relic story slot (Named) | STORY |

### Dual Wield (doc 33: 9+9, combos; uses one-hand classes' tiers)

Dual Wield has no own primary-material row: a dual pair inherits the
tier of its two weapons (both must be one-hand classes, doc 33 section
4). The T1-T5 ladder is the Short/Long/Blunt/Axes 1H rows above. Doc 39
supplies only the named-pair framing:
- Named pairs follow the same STORY rule as single relics: one named
  pair per the relic working target (doc 06: 9 weapon relics), the
  pair counts as ONE relic slot.
- PROPOSED anchor pair: The Sundered Twins (T5 blacksteel short blade
  + cold iron parrying blade, relic story: a smith's two sons, one
  light one dark, split by the war).

### Shield (doc 33: bash 8, block/parry identity)

| Tier | Name | Primary | Secondaries | Sources | Band |
|---|---|---|---|---|---|
| T1 | Oak Field Shield | oak | iron boss, doe | all T1 vendors | ABUNDANT |
| T2 | Silvered Kite | yew | silver boss, wolf | town vendors, war camps | COMMON |
| T3 | Steel-Faced Tower | steel | bog-oak frame, boar-tusk | war camps, hold sieges | COMMON/RARE |
| T4 | Cold Iron Ward-Screen | cold iron | thorn-yew frame, ibex | mountain strata 2+, blight scars | RARE |
| T5 | The Aegis Bulwark | blacksteel frame + Aegis Quintessence facing | ghoul-hide rim | deep-good Expert Enchanting only (doc 05 Aegis exclusivity) | STORY |

The Aegis Bulwark is a CRAFTED legendary, not a drop: it obeys the
locked Aegis faction-exclusivity (deep-good crafters only, no vendor,
doc 05). Listed here because it is the shield line's T5 terminal item.

### Unarmed (doc 33: 7, cheapest; knuckles/talons as tier carriers)

| Tier | Name | Primary | Secondaries | Sources | Band |
|---|---|---|---|---|---|
| T1 | Weighted Knaps | iron band | leather wrap, doe | all T1 vendors | ABUNDANT |
| T2 | Silver-Bound Wraps | silver band | wolf wrap | town vendors | COMMON |
| T3 | Steel Knuckle-Cage | steel | boar-tusk studs, troll sinew | war camps, coven dens | COMMON/RARE |
| T4 | Cold Iron Talons | cold iron | ibex binding | mountain strata 2+ | RARE |
| T5 | The Veilgauntlet | blacksteel | witchwood inlay | relic story slot (Named) | STORY |

## PART 3 - SOURCING MATRIX (bands + anchors)

Named sources per area/dungeon type/vendor family, per ruling 2. Bands
are weight-based (ABUNDANT/COMMON/RARE/STORY); the named-source grid
below is the doc 06 layer-3 (gear) resolution for weapons.

### Region tier bands (fixed difficulty, doc 06 locked)

| Region | Weapon tier band | Notes |
|---|---|---|
| Farmland + river valleys | T1-T2 | starting meadow caps at T2 (doc 06) |
| Darkwood forests | T1-T3 | |
| Moors + highlands | T2-T3 | |
| Swamplands | T2-T4 | richest alchemy biome, mid combat band |
| Mountains + passes | T3-T4 | cold iron home |
| Blight zones | T4-T5 | blacksteel home, Named territory |
| Descent Gate strata 1-4 | +rarity within band per stratum | doc 37 ruling: strata at 10/20/30/40 |

### Dungeon-type weapon weighting (doc 06 layer-3 keys)

| Dungeon type | Weapon profile |
|---|---|
| Crypts/cemeteries | silvered mid-tier, holy charms, bone/binding secondaries |
| Mines | steel tier up, smithing materials, gem-bearing strata |
| Coven dens | witchwood, tainted weapons, dark charms |
| War camps | steel weapons of every class, faction gear (doc 12 court skins) |
| Hold sieges | T3-T4 arms, siege-quality polearms/axes |
| Descent strata | rarity escalation within the region band (doc 37) |

### VENDOR SOURCING (doc 06 three families)

| Vendor family | Weapon stock |
|---|---|
| Light (Guild/Church) | T1-T3 iron/silver/steel melee, silvered mid tier, mid-tier bows |
| Dark (covens/undead courts) | blacksteel RAW materials, dark-court gear, tainted weapons |
| Neutral brokers | mid-tier everything, alchemical throwables, recipe trade |

### ANCHOR PERCENTAGES (PROPOSED anchors, Nicko locks exact numbers)

1. ANCHOR A1, dungeon gear-layer Named chance: a T1-T2 Named relic
   find in its story location is guaranteed by the story (doc 06
   hand-authored rule); random Named drops do NOT exist at any tier.
   Anchor: 0 percent random Named everywhere.
2. ANCHOR A2, T4 weapon drop weight inside a T4-band dungeon gear
   layer: 5 percent of layer-3 gear rolls. Anchor for Nicko.
3. ANCHOR A3, war-camp steel weapon share: 40 percent of layer-3 gear
   rolls in war camps are steel-tier weapons of any class. Anchor for
   Nicko.
4. Vendor weapon stock refresh: 2-3 in-game days, matching the node
   respawn timer (doc 06 locked). No percentage; cadence only.

## PART 4 - THE GEM SYSTEM (ruling 3)

Gems are the third sourcing axis beyond metals and woods: socket
payloads via Gem Crafting (doc 05 category), richest in the mountains
(doc 03 locked).

### Gem drop model (ruling 3, locked)

- Gem drop chance from mining vein harvests SCALES WITH MINING RANK:
  base chance at rank 1, rising with rank, per the doc 18 Mining curve
  (+yield, +vein sense, +crit-ore chance, techniques Deep Scan /
  Precision Strike / Seam Sense).
- The LUCK stat adds on top of the rank-scaled chance (doc 06: Luck
  raises drop odds and rare-resource rolls; the two fortune sources
  stack).
- GEM TIER is gated by vein depth and region band: surface veins cap
  at the region's base gem tier; strata veins roll higher tiers;
  mountains is the richest gem biome (doc 03 locked).
- Monster-drop and chest gem paths stay OPEN as doc 06 layer-1/4
  weightings (mines dungeon type already weights ores and gems) but
  the vein-mining scaling chance is the primary acquisition path per
  ruling 3.

### Anchor percentages (PROPOSED)

1. ANCHOR G1, base gem-on-harvest chance at Mining rank 1: 2 percent.
   Anchor for Nicko.
2. ANCHOR G2, rank scaling: +0.3 percent per rank, so rank 100 reads
   roughly 32 percent before Luck and technique bonuses. Anchor for
   Nicko.
3. ANCHOR G3, Luck contribution: +1 percent per 10 Luck stat points.
   Anchor for Nicko.
4. ANCHOR G4, gem-tier gate: gem tier ceiling = vein stratum + region
   band (surface mountains T1-T2 gems, strata 2 mountains up to T4,
   strata 3+ T5 star-gems via the Star-Cutting technique, doc 18).

### Gem tier ladder (PROPOSED names)

| Tier | Gem | Source gate | Cut use (Gem Crafting) |
|---|---|---|---|
| T1 | Chip gems (quartz, moss agate) | surface veins, any biome | basic socket fills |
| T2 | Cut-grade gems (garnet, moonstone) | moor/mountain surface | grade-shift sockets |
| T3 | Deep gems (sapphire, bloodstone) | strata 1-2 veins | enchant-grade components |
| T4 | Vein-hearts (empress stone, wyrm-glass) | strata 2-3, wyrm hoards | enchant-grade, +facet bonus |
| T5 | Star-gems (the Veil Star set) | strata 3-4, Star-Cutting only | named-tier sockets, relic-adjacent |

Gem names are working names. The Veil Star set is PROPOSED as the T5
star-gem family, tying the Star-Cutting technique to the descent-gate
deep strata.

## PART 5 - INGREDIENT CATALOG FOR WEAPONS (extends doc 38 Part 2)

Doc 38 covered 10 representative gear recipes. The full weapon spread
uses the SAME 5 refining chains and adds no new chains. What doc 39
adds is the per-tier sourcing map for each secondary CATEGORY member:

| Secondary category | Members by tier (doc 03 locked) | Refine | Source biome |
|---|---|---|---|
| Handle/frame wood | oak (T1), yew (T2), bog-oak/drift-oak (T3), thorn-yew/blackwood (T4), witchwood/blightwood (T5) | lumber at Workbench (doc 38 woods chain) | every biome per doc 03 |
| Grip/binding leather | doe (T1), wolf (T2), boar-tusk (T3), ibex (T4), ghoul-hide (T5) | tanning liquor, Armorsmithing | doc 03 hide lists |
| Binding sinew | common bones (T1-2), hardened chitin + troll sinew (T3), wyrm-sinew (T4-5) | none (raw) | hunting loop per biome |
| Silver bosses/fittings | silver ingot (T2+) | quench salts | moor barrows, mountain seams |
| Aegis facing | Aegis Quintessence (T5) | 27 Grace chain steps | light court only |

Station ceilings carry from doc 38's refining tables unchanged: S1
refines T1-T2, S2 steel, S4 cold iron, S5 blacksteel. A weapon recipe
is gated by BOTH the crafting-skill tier gate (doc 18) and the refine
ceiling.

## PART 6 - OPEN QUESTIONS

1. [08 TRACKER] Anchor percentages A2, A3, G1-G4: lock exact numbers or
   hand to GDD tuning.
2. [08 TRACKER] Silver-as-T2 metal: confirm the doc 05 five-metal
   ladder maps 1:1 to T1-T5 with silver at T2.
3. [08 TRACKER] Named-pair rule (Sundered Twins framing): confirm a
   dual-wield pair counts as one relic slot against the 9-relic target.
4. [08 TRACKER] The Aegis Bulwark as a crafted (not dropped) T5 shield:
   confirm the shield line's terminal item is craft-exclusive like the
   permanent Aegis weapon.
5. [08 TRACKER] Gem names (Chip/Deep/Vein-heart/Veil Star): working
   names pending Nicko pass.
6. [08 TRACKER] Crossbow: doc 33's Archery row assumes bows; whether a
   crossbow subclass exists (stocks, reload cadence) is unaddressed.

## RULING PASS (open-questions sweep, 2026-09-14, Nicko)
1. ANCHORS: CONFIRMED AS PROPOSED, HAND TO GDD TUNING. A2 (T4
   dungeon drop weight), A3 (war-camp steel share), G1-G4 (gem base
   chance/rank curve/Luck/stratum gates) stay PROPOSED working
   numbers, tuned against a playable build. Nothing locks a wrong
   number before a build exists to feel it.
2. CROSSBOW: ADDED. The Archery class gains a crossbow subclass
   (ruling on doc 33 above); doc 39's catalog gains crossbow rows
   across its 5 tiers at the next catalog touch (materials follow
   the bow ladder's sourcing; identity: slow reload, high poise
   damage).