# 38 - Ingredient Recipe Matrix

Status: LOCKED by Nicko, 2026-09-14 (recipe-matrix scope confirmed in
session; item-level PROPOSED markers below stay per-item).

Exact ingredient lists and minimum stations for alchemical consumables and representative gear. World names follow [03's locked lists](03-world-design.md); exceptions are PROPOSED monster parts and 05's supplies/reagents. All combinations and unspecified minima are PROPOSED. Consumables use exact names, gear uses category secondaries. Meals stay in 10; Hunter's Components are deferred.

## STATION GATE REMINDER

Source: [05](05-crafting-system.md). Its global five-tier ladder is locked; its alchemy-specific heading remains PROPOSED. S = station tier; T = material/output tier.

| Minimum station tier | Capability carried from 05 | Grade ceiling |
|---|---|---|
| S1 Field Alchemy Kit | Three-ingredient potions only; T1-T2 supply cap; no rare-component handling | Standard |
| S2 Village Alchemy Table | T3 supply cap; standard potions; coatings T1-T3 | Fine |
| S3 Town Apothecary Lab | T3 supply cap; full coatings and throwables; improved bonus-yield odds | Superior |
| S4 City Laboratory | T4 supply cap; one rare-component socket per brew | Masterwork |
| S5 Grandmaster Lab; legendary dungeon station | All supply tiers; best odds. Only the legendary dungeon station brews the two T5 legendary potions | Masterwork, best odds |

05's later locked WORKBENCH ruling moves all refining there. Supply caps require matching Workbench access; alchemy stations only brew.

## PART 1 - CONSUMABLE RECIPES

Inputs are Workbench-prepared supplies retaining named identities. Quantities are GDD tuning. No substitution or optional fourth ingredient. Signature herbs are not Hunter's Components.

### A. HEALTH + MANA STOCK POTIONS

| Recipe | Exact ingredients, PROPOSED combination | Minimum station tier | Axis/taint gate |
|---|---|---|---|
| Healing potion | comfrey + yarrow + moonbell | S1 Field Kit+ | None specified |
| Mana/Focus potion | marsh heliotrope + moonbell + comfrey | S1 Field Kit+ | None specified |

Locked in 05: carry-weight-limited stock, no Estus or stamina potion. Grade scales with skill tier x station tier, skill floor and station ceiling. Crude/Standard/Fine/Superior/Masterwork scale magnitude and duration. Prep uses 10's single daily drink slot with the meal.

### B. THE 18 DAILY PREP DRAUGHTS

05's working names. Defense includes utility/social prep. Two-input proposals need Village; Field permits three-ingredient potions only. PROPOSED parts are not Hunter's Components.

| Recipe | Biome | Role | Exact ingredients, PROPOSED combination | Minimum station tier | Axis/taint gate |
|---|---|---|---|---|---|
| Green Veil-Steep | Darkwood | Defense | moonbell + blightcap | S2 Village+ | None specified |
| Tender's Draught | Darkwood | Defense | moonbell + hemlock + blightcap | S1 Field Kit+ | Taint resistance is not cleansing |
| Witch-Bane Philter | Darkwood | Offense | witch-fauna heart (PROPOSED part) + moonbell + hemlock | S1 Field Kit+ | None specified |
| Watcher's Tonic | Moors | Defense | bog-myrtle + crow-garlic | S2 Village+ | None specified |
| Unwailed Draught | Moors | Defense | storm-thistle + bog-myrtle + crow-garlic | S1 Field Kit+ | None specified |
| Wight-Marrow Draught | Moors | Offense | wight-marrow (PROPOSED part) + barrow-bone + bog-myrtle | S1 Field Kit+ | None specified |
| Feverfew Tonic | Swamplands | Defense | feverfew + bloodroot + marsh heliotrope | S1 Field Kit+ | None specified |
| Still-Water Draught | Swamplands | Defense | marsh heliotrope + feverfew | S2 Village+ | None specified |
| Hag-Bane Draught | Swamplands | Offense | hag-bile (PROPOSED part) + bloodroot + feverfew | S1 Field Kit+ | None specified |
| Hearth-Toddy | Mountains | Defense | Frost Wisp + pine + high-altitude birch | S1 Field Kit+ | Elemental, no axis gate |
| Deep-Breath | Mountains | Defense | pine + high-altitude birch | S2 Village+ | None specified |
| Clatterer-Dissolving Draught | Mountains | Offense | clatterer chitin (PROPOSED part) + troll sinew | S2 Village+ | None specified |
| Farmwife's Cider | Farmland | Defense | comfrey + yarrow | S2 Village+ | None specified |
| Chapel-Garden Tea | Farmland | Defense | chapel-garden holy herbs + comfrey + yarrow | S1 Field Kit+ | Deep-good; light-held parish supply/benefit |
| Thrall-Breaker Draught | Farmland | Offense | thrall marrow (PROPOSED part) + common bones + yarrow | S1 Field Kit+ | None specified |
| Undertow-Nausea Draught | Blight | Defense | blightcap + tallow-hide + Grave Mote | S1 Field Kit+ | Dark reagent: deep-evil; taint on drinking |
| The Visioner's Draught | Blight | Defense | blightcap + tallow-hide | S2 Village+ | No additional axis gate specified |
| Demon-Bait Draught | Blight | Offense | demon ichor (PROPOSED part) + blightcap + tallow-hide | S1 Field Kit+ | Taint on drinking; no new axis threshold assigned |

Recipe-fit gaps, PROPOSED: 03 lists no mountain herbs, so local woods/Frost reagent replace that grammar. Frost Wisp is 05's refinement of 03's Frost chain. Blight lists only blightcap, so its defenses add local fat/reagents. Chapel-garden holy herbs is 03's collective name, not a substitution slot. Farmwife's herb pairing lacks 10's orchard press because 03 names no fruit. Undertow-Nausea differs from 10's imported bloodroot pairing. Nicko review required.

PROPOSED parts follow 03/05/10's local witch-fauna, wights, hags, clatterers, thralls and demons. Undead parts alone do not imply Dark attunement.

### C. COATINGS + PAYLOADS AND THROWABLES

PROPOSED pairings. Exact wax/tallow bases, no fat/wax slot. Cross-biome sourcing allowed here. 05 lists three basic throwables and two vials, not four basics; both vials require Grandmaster.

| Recipe | Biome | Role | Exact ingredients | Minimum station tier | Axis/taint gate |
|---|---|---|---|---|---|
| Wight-Marrow Oil | Moors | Offense coating | wight-marrow (PROPOSED part) + bog-myrtle + wax | S2 Village+ | None specified |
| Witch-Bane Oil | Darkwood | Offense coating | witch-fauna heart (PROPOSED part) + hemlock + wax | S2 Village+ | None specified |
| Hag-Bile Tip | Swamplands | Offense payload | hag-bile (PROPOSED part) + bloodroot + wax | S2 Village+ | None specified |
| Troll-Blood Coating | Mountains | Offense coating | troll blood (PROPOSED part) + troll sinew + wax | S2 Village+ | None specified |
| Thrall-Breaker Oil | Farmland | Offense coating | thrall marrow (PROPOSED part) + yarrow + wax | S2 Village+ | None specified |
| Corrupted-Iron Slurry | Blight | Offense coating | corrupted iron + tallow-hide + blightcap | S2 Village+ | Dark, deep-evil; taint on crafting |
| Firebomb | Darkwood/Blight | Offense throwable | Ember Mote + tallow-hide | S3 Town+ | None specified |
| Acid Flask | Mountains/Swamplands | Offense throwable | hardened chitin + bloodroot + wax | S3 Town+ | None specified |
| Frost Flask | Mountains | Offense throwable | Frost Wisp + wax | S3 Town+ | None specified |
| Holy Water Vial | Moors/Farmland | Offense throwable | Dawn Wisp + chapel-garden holy herbs | S5 Grandmaster | Deep-good; burns in evil hands |
| Grave-Rot Vial | Swamplands | Offense throwable | Crypt Wisp + crypt-bloom | S5 Grandmaster | Deep-evil; taint on use |
| Fire tip | Darkwood | Offense payload | Ember Mote + wax | S2 Village+ | None specified |
| Frost tip | Mountains | Offense payload | Rime Mote + wax | S2 Village+ | None specified |
| Storm tip | Moors | Offense payload | Spark Mote + wax | S2 Village+ | None specified |
| Poison tip | Darkwood | Offense payload | hemlock + wax | S2 Village+ | None specified |
| Holy-blessed tip | Farmland | Offense payload | Grace Mote + wax | S2 Village+ | Deep-good; burns in evil hands |
| Dark tip | Darkwood | Offense payload | Grave Mote + wax | S2 Village+ | Deep-evil; taint on use |
| The Cleansing Draught | Farmland | Defense/cleansing | chapel-garden holy herbs + consecrated salt | S2 Village+ | Deep-good brew; cleanses another, never self |
| The Undertow's Draft | Blight | Utility legendary | Abyssal Quintessence + blightcap + tallow-hide | S5 legendary dungeon station ONLY | Deep-evil; dark-potion taint on use |
| The Dawn-Draught | Farmland/Moors | Defense legendary | Aegis Quintessence + consecrated silver + chapel-garden holy herbs | S5 legendary dungeon station ONLY | Deep-good brew |

Additional rows cover 05's generic tips, cleansing and PROPOSED legendaries. Reagent identities follow 05. Consecrated supplies are 05/06 vendor/relic goods. 05/17 axis gates apply; taint bands are Low 0-33, Mid 34-66, High 67-100. No taint amounts assigned.

## PART 2 - REPRESENTATIVE GEAR RECIPES

PROPOSED model, not a catalog: primary sets tier, two category secondaries use distinct items from 03. Exact-name ruling applies only to consumables. Material-tier mappings/minima are PROPOSED; T5 blacksteel differs from 05's old T4 example. Matching crafting skill required. Catalysts are upstream costs, not charged twice.

| Recipe | Primary, sets tier | Category secondaries, examples | Catalysts needed | Minimum station tier | Axis/taint gates |
|---|---|---|---|---|---|
| T1 iron sword | Iron ingot | Handle wood: oak; grip leather: doe | Quench salts, sealant, tanning liquor | S1 forge+ | None |
| T3 steel sword | Steel ingot | Handle wood: yew; grip leather: wolf | Quench salts, sealant, tanning liquor | S2 forge+ | None |
| T4 cold iron blade | Cold iron ingot | Handle wood: thorn-yew; grip leather: ibex | Quench salts, arcane ash, sealant, tanning liquor | S4 forge+ | Metal alone grants no Holy effect |
| T5 blacksteel blade | Blacksteel ingot | Handle wood: blackwood; grip leather: ghoul-hide | Quench salts, arcane ash, sealant, tanning liquor | S5 forge | No automatic Dark enchant |
| T1 light armor set | Doe leather | Binding: common bones; trim hide: wolf | Tanning liquor | S1 armory+ | None |
| T3 medium armor set | Boar-tusk leather | Binding: troll sinew; lining hide: cattle-hide | Tanning liquor | S2 armory+ | None |
| T4 heavy armor set | Steel plate | Reinforcement metal: cold iron; lining hide: ibex | Tanning liquor, quench salts, arcane ash | S4 armory+ | None |
| T2 bow | Yew lumber | Binding sinew: troll sinew; grip leather: doe | Sealant, tanning liquor | S1 weapons bench+ | None |
| T4 holy charm | Consecrated silver | Holy reagent: Sanctified Essence; mounting wood: river-ash | Sealant; silver supplied consecrated | S4 enchanting altar+ | Deep-good, recipe burns outside axis |
| T3 dark charm | Blackwood lumber | Dark reagent: Crypt Wisp; bone: barrow-bone | Sealant | S2 enchanting altar+ | Deep-evil; taint on activation PROPOSED |

Holy charm uses the Grace chain. Permanent Aegis weapons retain 05's Expert/deep-good craft exclusivity, consecrated silver and Aegis Quintessence. Armor pairings are PROPOSED; wyrm-scale is T4-T5. No Named Relic duplication.

## PART 3 - REFINING CHAINS

Workbench replaces line-station refining; target line owns XP. Caps: S1 Field T1-T2, S2 Village T3, S3 Town T3, S4 City T4, S5 Grandmaster all. PROPOSED reagent tiers: Mote T1, Wisp T2, Essence T3, Quintessence T4.

### Hides to leather
| Raw -> supply | Catalyst | Station / line | Minimum station tier | Yield |
|---|---|---|---|---|
| Doe -> cured leather; wyrm-scale -> wyrm-leather | Tanning liquor | Workbench, Armorsmithing | S1 T1-T2; wyrm T4 at S4, T5 at S5 | Refine-only roll |

### Woods to lumber
| Raw -> supply | Catalyst | Station / line | Minimum station tier | Yield |
|---|---|---|---|---|
| Oak -> lumber; witchwood -> treated witchwood | Sealant | Workbench, Weaponsmithing | S1 oak; S2 witchwood, PROPOSED | Refine-only roll |

Witchwood working causes taint. Its T3/S2 supply mapping is PROPOSED.

### Ores to ingots
| Raw -> supply | Catalyst | Station / line | Minimum station tier | Yield |
|---|---|---|---|---|
| Iron, silver, steel, cold iron, blacksteel -> ingots | Quench salts; cold iron/blacksteel also arcane ash | Workbench, Weaponsmithing; formerly forge | S1 iron/silver; S2 steel; S4 cold iron; S5 blacksteel, PROPOSED | Refine-only roll |

### Fiber to cloth/rope
| Raw -> supply | Catalyst | Station / line | Minimum station tier | Yield |
|---|---|---|---|---|
| Comfrey fiber -> cloth/rope, PROPOSED processing | None specified | Workbench, Armorsmithing cloth; rope line TBD | S1 T1-T2, PROPOSED | Refine-only roll |

03 names no fiber species; comfrey processing is PROPOSED, not new crop canon.

### Purified reagents
| Raw -> supply | Catalyst | Station / line | Minimum station tier | Yield |
|---|---|---|---|---|
| 3 Motes -> 1 Wisp; 3 Wisps -> 1 Essence; 3 Essences -> 1 Quintessence | None specified | Workbench, Enchanting; formerly altar | S1 Wisp; S2 Essence; S4 Quintessence, PROPOSED tier mapping | Refine-only roll |

The 3:1 ratio is locked. Named chains from 05:
- Ember Mote > Flame Wisp > Cinder Essence > Pyre Quintessence.
- Rime Mote > Frost Wisp > Glacial Essence > Absolute Quintessence.
- Spark Mote > Storm Wisp > Tempest Essence > Maelstrom Quintessence.
- Grace Mote > Dawn Wisp > Sanctified Essence > Aegis Quintessence.
- Grave Mote > Crypt Wisp > Haunt Essence > Abyssal Quintessence.

Holy/Dark axis attunement persists. Rare nodes respawn in 2-3 days; no ordinary Holy blight spawns. 06 gathering/loot and court vendors supply chains. Catalysts: Alchemy or vendors. Locked bonus yield: refine/consumable ONLY, never gear; rank-weighted, Luck-adjusted, negative high-tier base.

## PART 4 - OPEN QUESTIONS

Flagged for 08 tracker, not written to 08 here.

1. [08 TRACKER] RESOLVED 2026-09-14 (Nicko): all seven monster-part
   names CONFIRMED as locked working names (witch-fauna heart,
   wight-marrow, hag-bile, clatterer chitin, troll blood, thrall
   marrow, demon ichor). Doc 38's recipe-fit exceptions stand as
   written.
2. [08 TRACKER] Quantities per craft, including moonbells per flask, are GDD tuning; validate PROPOSED minima and fiber processing.
3. [08 TRACKER] RESOLVED 2026-09-14 (Nicko): consumable substitution
   is ALLOWED WITH DEGRADATION COST. A category-appropriate substitute
   may fill a consumable slot when the exact named ingredient is
   missing, but the output takes a grade/magnitude degradation (exact
   recipe = full grade odds; substitute = shifted odds and/or reduced
   magnitude, numbers GDD tuning). Gear keeps the category-slot model
   unchanged.
4. [08 TRACKER] RESOLVED 2026-09-14 (Nicko): Hunter's Components
   catalog becomes doc 43, authored next crafting pass, full catalog
   (12-16 components) with biome/monster sources.

## PART 5 - GATHERING FORTUNES (slot/spread/grammar LOCKED 2026-09-14, Nicko; recipes PROPOSED)

Six daily-prep fortunes, one per gathering skill line (doc 06). Node-keyed grammar: each key ingredient is a small byproduct of the resource it boosts (byproducts are PROPOSED additions to 06's gather tables). Secondary herbs from 03's lists. Grade scales magnitude, duration stays the day. Stack rule: separate source from Luck stat and techniques, stacks with both. Discovery: normal recipe economy (05, locked), recipes are loot, not default-known.

| Fortune | Line boosted | Exact ingredients, PROPOSED | Minimum station tier | Effect (PROPOSED) |
|---|---|---|---|---|
| Prospector's Draught | Mining | ore-dust (byproduct) + bog-myrtle + quench salts | S1 Field Kit+ | more ore per vein, more gem-bearing veins flagged |
| Faceter's Eye | Gem Crafting | raw-gem chips (byproduct) + blightcap | S2 Village+ | better raw-gem yields from veins and monster drops |
| Tiller's Green | Herbalism | herb-tallow (byproduct) + comfrey + yarrow | S1 Field Kit+ | rarer specimens, higher herb yields |
| Sawyer's Tonic | Woodcutting | sawdust paste (byproduct) + sealant | S1 Field Kit+ | better wood cuts, more special-tree finds |
| Tracker's Draught | Hunting/Skinning | render-fat (byproduct) + bog-myrtle + crow-garlic | S1 Field Kit+ | richer pelts, parts, ichors per kill |
| Stillwater Chum | Fishing | fish-oil (byproduct) + marsh heliotrope | S2 Village+ | better catches, more rare fish |

Recipe-fit notes, PROPOSED: ore-dust, raw-gem chips, herb-tallow, sawdust paste, render-fat, fish-oil are new byproduct items (06 table additions). Quench salts and sealant double as catalysts here, bought or Workbench-made. Faceter's Eye uses blightcap, the locked grade-shifter herb. Stillwater Chum echoes the Still-Water Draught's marsh-heliotrope pairing.
