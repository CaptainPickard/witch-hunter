# 41 - Wilderness Encounter Layer (working title: THE LIVING GAPS)

Status: PROPOSED (IO, 2026-09-14, pending Nicko lock). Authored from the
2026-09-14 session's concept-space pass; three structural rulings locked
in that session (see SESSION RULINGS). All eight families and all
working names are PROPOSED until reviewed line by line.

Design sentence: a ~2.3 km gap between holds is a journey, and every
journey should carry at least one thing worth remembering. No fast
travel (doc 03, locked) made the gaps real; this layer makes them alive.
This doc owns the overworld's NOTABLE encounter sites: dens, hidden
places, wayfinding, road life, landmarks, riches, set pieces, and the
war's litter. Dungeons remain doc 37's; ambient gather nodes remain
doc 03/06's; settlements remain doc 03's. Nothing here re-authors those.

## SESSION RULINGS (locked 2026-09-14, Nicko)
1. PATH: author the full concept doc now with all eight families,
   marked PROPOSED, review line by line (the doc 37 pattern).
2. SITE STATE: inherit doc 37's Cleared-Wound and Vacuum rules
   wholesale. What you clear stays cleared, colonizers move in, sites
   carry a light state readable from outside.
3. DENSITY: 8-12 notable sites per hold region (~5.2 km2). A memorable
   thing on most travel gaps, but the land still breathes with empty
   miles.

## CONVENTIONS (carried from the locked set)
- Overworld placement is HAND-AUTHORED (doc 03 structure principle):
  every site in this doc is a curated placement per hold region.
- No markers for hidden sites (doc 03/37 map-reads-like-weather
  principle): discovery is gameplay, through the rumor engine (doc 37
  Part 1), observation, and the cumulative-redundant clue-chain
  pattern (design bank) for the deepest secrets.
- Biome safety by alignment (doc 03) and the Veil-Tide (doc 03) recolor
  every site; war state (doc 13) rekeys patrols, spawns, and refugee
  flow. Sites themselves carry no new alignment math.
- Site state inherits doc 37 Part 5's locked rules (ruling 2 above):
  CLEARED-WOUND (destruction persists, committed at exit triggers for
  interiors; for open-air sites, committed when the site's resistance
  breaks), VACUUM (cleared space is colonized: bandits, spiders,
  necromancers, wizards, refugees, per the situation tables), and a
  LIGHT STATE readable from outside (smoke, banners, gnawed bones,
  silence) reported by the rumor engine and Overheard Word when it
  changes.
- Bestiary grammar is doc 34's: beasts (no block, no parry), undead
  (no dodge, no parry), light pairs, dark packs, sloppy bandits,
  disciplined soldiers. Encounter sites stage these grammars; they do
  not add new combat rules.
- No em dashes; terse declarative sentences.

## DENSITY AND DISTRIBUTION (ruling 3)
Target 8-12 notable sites per hold region, ~25 regions, so roughly
200-300 notable sites continent-wide, PLUS the ambient node layer
(doc 03's 6-10 nodes per type per region) and the settlements
themselves. Distribution guidance (PROPOSED):
- Every travel gap between neighboring holds carries at least one
  notable site within sight-or-rumor of the road (the "worth
  remembering" floor).
- Each biome's family mix differs (per-biome tables below). A hold
  region's 8-12 is a MIX, not eight dens: typical mix reads as 2-3
  wayfinding threads, 1-2 dens, 1-2 hidden places, 1-2 road-life
  anchors, 1 landmark or riches site, and the rare one-off wanders
  NOT counted in the 8-12 (they are continent-rare, hand-authored,
  and never region-guaranteed).
- One-off wanders (family 7) are the memory tier: maybe 15-20 on the
  whole continent, encountered once in a long playthrough.

## PART 1 - THE EIGHT FAMILIES

### Family 1: DENS AND LAIRS
Beast habitat sites. Wolf dens, bear caves, boar wallows, spider
hives, later goblin nests and hag pools. Keyed to doc 34's beast
grammar (spacing tests, no block/parry) and doc 03's ingredient
lists: the den IS the source of its biome's signature hide (boar-tusk
leather from Darkwood wallows, ghoul-hide from moor barrow-adjacent
packs, wyrm-scale from the deep mountain caves).
- Structure: an entrance (cave mouth, hollow, thicket), a den body
  (usually a small interior per doc 03's procedural interior rule,
  persistent once generated), a brood (the pack), and the LARDER
  (cached kills, bones, sometimes a past victim's gear: the den's
  loot identity is what the beast ate).
- FERAL PACK DENS at the three altar ruins are already locked (doc
  03); this family generalizes them as a type.
- Repopulation tension (OPEN 1): doc 37's Cleared-Wound rule says
  cleared stays cleared and colonizers move in. Ruling 2 applies it
  wholesale, so a cleared wolf den gets colonized (by bandits,
  spiders, refugees) rather than repopulating with wolves. Beast
  dens do NOT respawn their old species. New dens can appear
  elsewhere (habitat pressure), but the map's wounds stay wounds.
  This touches doc 37 open 15 (which societies hold grudges); beast
  dens hold none (beasts are not factions), goblin nests DO (locked
  Warren chain, doc 37).
- Den danger scales by region band and den depth, not player level
  (fixed difficulty lock, doc 04).

### Family 2: HIDDEN HOLY AND TAINTED PLACES
The grove family. Coven glades (locked lore: the Old Faith's original
altar-gardens, doc 03), drowned shrines (locked reagent sites), old
chapel mounds (locked Holy-reagent sites), witch-huts, hilltop
chapels, a blighted shrine that still works. Affinity-keyed safe
grounds per doc 03's biome safety: coven glades are safe ground for
dark players, chapel mounds for good ones, drowned shrines admit the
bartered (hag-bargain holders).
- Structure: a place, a keeper or presence (coven tender, chapel
  hermit, a wisp chorus), an offering economy (what the place takes
  and gives), and the discovery layer (no markers; found via rumor,
  observation, or being led there by a quest or a wanderer).
- The blighted shrine that still works is the family's signature
  rarity: a working altar-piece inside a scar, exactly the kind of
  wrongness the blight produces. PROPOSED as a Red-Vigil-anchored
  discovery (the Vigil's burned-back edge briefly exposes it).
- The Last Tender (doc 03 roster) is the family's named ceiling: her
  deep-glade is THE grove of Darkwood. Named roster sites are
  hand-authored once, never procedurally repeated.

### Family 3: WAYFINDING THREADS
The survival infrastructure family. Answers the locked no-fast-travel
question: "it is dusk, the gap is 2 km, where do I sleep?" Per-biome
grammar (PROPOSED working set):
- Darkwood: Guild-ranger waystations (locked name), lit roads,
  hunter lean-tos with old fire-scars. Night = climb or barricade.
- Moors: ruined watchtowers (locked mechanic: day shelter for evil,
  night beacon for good; knowing which tower is lit is survival
  intel), beacon pyres, shepherd cots.
- Swamplands: stilt-huts, causeway shrines, hag-marked paths (safe
  to whom?).
- Mountains: garrison blockhouses (doc 13 key: a pass your court
  holds is safe at all hours), mine-adit shelters, hot springs.
- Farmland: roadside shrine-waystones, barn lofts, mill overhangs;
  the parish belt's Militant/Mercy meters (doc 20) recolor who
  welcomes you.
- Blight: almost nothing. That is the point. The blight's wayfinding
  layer is dens and ruins; provisioning is the counterplay (locked
  attrition model).
- Wayfinding sites are camp-eligible per doc 09's site rules; some
  carry pre-built advantages (a tower's walls) and pre-built risks
  (a tower is a beacon: things see it too).

### Family 4: ROAD LIFE
The dynamic layer: things that MOVE on roads, keyed to war state and
the clock. Each is a deniable encounter and an information source
(the rumor economy's mobile tier):
- Refugee columns (locked in docs 20/37 as rumor sources; here given
  their travel reality: routes, guards, what they carry).
- Pilgrim trains to the Sun Altar's moor ring (light pilgrimage
  traffic through enemy land, doc 03).
- Corpse carts, tax wagons, dwarf caravans from the forge-city (doc
  22 war industry), smuggler couriers (doc 12's dens and docks),
  bounty targets on the move, a Warden escorting a relic (doc 19
  authentication traffic).
- Raiding parties at clock edges (doc 03/34 night ambush rules).
- Road life spawns from ROUTES, not random points: each hold pair's
  road has a traffic profile keyed to war state (a contested road
  runs raiders and refugees; a held road runs wagons and pilgrims).
  PROPOSED: the tavern rumor engine (doc 37 Part 1) reports traffic
  changes on named roads as a rumor type ("the coast road runs
  dark").

### Family 5: RUINS AND PRE-FALL LANDMARKS
Old-imperial ruins (locked name), moor barrows (locked, silver
source), standing stones, gallows fields, the erased-statue texture
(the Debt's Echo field's type, doc 03). The battlefield hook: the
moor's wight-bard REPLAYS the Fall's battles where it fell (locked
roster entry), which implies BATTLEFIELD SITES where the dead
re-fight old wars on Veil-charged nights (PROPOSED: the replay is
spectacle first, threat only when approached).
- Ruins are the family's dungeon-adjacent tier: some are surface
  sites, some open into small interiors (still doc 03 procedural
  interiors).
- Barrows carry doc 03's silver spawns and doc 34's undead grammar.

### Family 6: RICHES SITES
The notable gather destinations (ambient nodes stay doc 03/06's; this
is the destination tier you plan a day around):
- A rich gem seam worth a mining trip (doc 39's depth-gated tiers;
  mountains richest, locked).
- A blightcap grove at a scar edge (the locked grade-shifter herb's
  densest find, doc 03/38).
- A hag's herb pool (barter-gated, doc 03's hag-hide economy).
- A drowned cache (swamp salvage, doc 03's drowned-dead table).
- A seed orchard or chapel garden (light-held parish-gated Holy
  herbs, doc 20's parish meters).
- Riches sites deplete on harvest and recover on long timers (doc
  06's node rules govern; the notable site is the DENSE version,
  not a different mechanic).

### Family 7: ONE-OFF WANDERS
The memory tier. Hand-authored, rare, no markers, each carrying a
rumor, a clue, or a piece of the Ledger:
- A white stag that leads somewhere (working name: THE PALE STAG).
- An ancient bear with an old heraldry tag on its collar (a Fallen
  house's beast, doc 14 lifecycle hook).
- A hermit with one fragment of the world's memory (Ledger-adjacent,
  doc 20).
- A wandering Warden far from any cemetery (why?).
- The still-talking corpse archetype already exists in doc 37's
  vendetta comedy; wanders can carry it into the wilds.
- 15-20 continent-wide, never region-guaranteed, never respawned
  the same way twice. Discovery is the reward; their loot is
  usually information.

### Family 8: WAR SCARS
Event sites the conquest system (doc 13) leaves on the land:
- Siege camps after sieges resolve (earthworks, burnt supply).
- Battlefields after doc 13 battles (loot, dead, grudge evidence
  per doc 03's witnessed-murder rule).
- Blight-edge refugee camps (doc 03's breathing edges displace
  people).
- A purged den's aftermath (doc 12's purge quests leave a physical
  site: the burned safehouse, the wanted notices).
- War scars decay: loot rots, earthworks fade, and the site returns
  to family 3/5 state over time (PROPOSED: one in-game season). The
  war's litter is temporary by design; the war moves on.

## PART 2 - SITE STATE (ruling 2's inheritance, specified)
Every notable site carries a LIGHT STATE readable from outside and
reported by rumor/Overheard Word when it changes:
- INHABITED (smoke, movement, banners)
- ABANDONED-RECENTLY (cold ashes, scattered goods)
- HAUNTED (unnatural signs, doc 34 undead grammar)
- CONTESTED (signs of a fight that has not finished)
- OVERGROWN/FALLEN (long-empty, nature reclaiming)
These five are the overworld mirror of doc 37's dungeon situations,
deliberately simplified (no occupancy factions per site; occupancy
FOLLOWS from war state and the Vacuum tables). Cleared-wound
commitment for open-air sites: when the site's resistance breaks
(its defenders dead or fled), the wound commits and the Vacuum rule
schedules colonizers on the situation tables' timers. Interiors
inside sites follow doc 37's exit-trigger commitment exactly.

## PART 3 - PER-BIOME FAMILY MIXES (PROPOSED)
- DARKWOOD: dens 2-3, hidden places 2-3 (glades), wayfinding 2,
  road life 1-2 (smuggler routes), ruins 1, riches 1 (witchwood,
  blightcap edges). The contested buffer: everything is keyed to
  territory, not hour.
- MOORS: wayfinding 2-3 (towers), dens 2 (wolf country), ruins 2-3
  (barrows, battlefields), hidden places 1 (chapel mounds), road
  life 1-2 (pilgrims, corpse carts). The exposed hourglass.
- SWAMPLANDS: hidden places 2-3 (drowned shrines), riches 2-3 (the
  alchemy biome), dens 1-2 (hag pools, spider hives), road life 1
  (smugglers), wayfinding 1-2 (stilt-huts). Standing neutral.
- MOUNTAINS: dens 2 (bear caves, cave clatterers), riches 2-3 (gem
  seams, the deepest), wayfinding 2-3 (blockhouses), ruins 1-2
  (old-imperial), road life 1 (dwarf caravans). Garrison biome.
- FARMLAND: road life 2-3 (the traffic heartland), war scars 1-2,
  hidden places 1-2 (parish gardens), wayfinding 2, riches 1, dens
  0-1 (wolf pressure at full-moon). The clock's heartland.
- BLIGHT: dens 2-3, ruins 2-3, hidden places 1-2 (the working
  shrine rarity), riches 1-2 (blacksteel ore-scars, blightcap),
  wayfinding 0-1. The attrition biome: fewer sites, worse company.

## PART 4 - DISCOVERY ECONOMY
Tiers per the design bank's cumulative-redundant clue chain and doc
37's rumor tiers:
- Tier 0 (ambient, no info needed): wayfinding sites, road life,
  ruins on roads. You find them by walking.
- Tier 1 (rumor-revealable): dens (hunters talk), riches sites
  (miners and herbalists talk), most hidden places.
- Tier 2 (guarded: multiple clues or an NPC's trust): the deep
  glades, the blighted working shrine, one-off wanders' purposes.
- Tier 3 (story-authored only): roster sites (the Last Tender's
  glade), anything spine-keyed.
Rumor types added to doc 37's engine (PROPOSED): site-state changes,
road traffic reports, den sightings (a bounty board tie: a den with
a price on its beast), pilgrim road warnings.

## Open Questions
1. Beast den repopulation vs habitat drift: ruling 2 commits cleared
   dens to Vacuum colonization. Where do NEW dens come from (habitat
   pressure at region edges?), and can a den's species ever return?
   Owning doc: 41 with doc 37 open 15.
2. Wayfinding site ownership: are towers/waystations faction-
   claimable (doc 13 conquest rekeys them?) or terrain-fixed
   neutral? Owning doc: 41 with doc 13.
3. Road-life spawn budgets: how many concurrent road parties per
   region, and their collision rules with doc 34's night ambush
   spawn caps. Owning doc: 41 with doc 34.
4. Wanderer authoring: the 15-20 continent set pieces need a
   hand-authoring pass at GDD stage. Owning doc: 41.
5. Blight wayfinding exception: does the blight's near-empty
   wayfinding layer need ONE special shelter type (a Warden waybone?
   a camp that holds?), or is provisioning the whole answer? Owning
   doc: 41 with doc 03.