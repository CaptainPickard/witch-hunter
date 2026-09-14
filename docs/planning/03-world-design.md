# 03 - World Design

## Decisions (locked with Nicko)
- Procedural dungeons PERSIST: once a dungeon layout is generated, it is saved
  for the playthrough. Named/special dungeons stay hand-authored. Feels
  Daggerfall-like and persistent.
- Character creation is human-centric dark fantasy: no fantasy race selection.
  Factions and covens carry the exotic roles.
- SCALE (locked 2026-09-11): a deliberate, hand-shaped landmass where every
  town and road is curated; hand-authored overworld + procedural INTERIORS
  only (dungeons/crypts/cemeteries, persistent). 20-30 holds, each a real
  place: noble family, tavern, dungeon cluster.
- SCALE TARGET (locked 2026-09-12, Nicko, world GDD session): playable
  footprint ~10 x 13 km, ~130 km2. Target ~25 holds (mid of the 20-30
  band), ~5.2 km2 per hold, average settlement-to-settlement gap ~2.3 km
  (a 5-min mounted hop, a ~15-min walk). Full diagonal crossing ~16.4 km:
  ~3.3 h walk, ~1.4 h run, ~39 min mounted. Design intent: dense enough
  that every hold is curated and hostile biomes read as real expanses
  (moor night, blight crossing), while a mounted crossing still reads as
  ~16 in-game days at the 24:1-class clock.
- MOUNTS (locked 2026-09-11): travel speed only, no mounted combat.
- DAY/NIGHT (locked + revised 2026-09-11): night is dangerous for GOOD
  players (undead, evil ambushes; sleep at night). EVIL players live the
  INVERTED clock: out at night, sleep by day, with DAYLIGHT sleep risking
  paladin/good-force attacks. The dangerous half of the day depends on the
  player's affinity. Neutral players play the good-side clock by default.
- PLAYER HOUSING (locked via doc 11): superseded by the warp camp system -
  a placeable, customizable home base earned as the mid-game milestone.

## The Continent
One large landmass ("the continent") spanning multiple biomes, with towns,
cities, cemeteries, dark forests, and procedurally generated interiors. A
full-continental map is a core promise: hand-authored density where it
matters, fast travel between discovered settlements to preserve scale.

## Structure Principle
- Overworld: hand-authored (heavily curated) - terrain, biome placement,
  major roads, towns, cities, named dungeons, and all 20-30 holds. This is
  where worldbuilding and faction storytelling live.
- Dungeons, crypts, cemeteries interiors: procedurally generated layouts with
  authored rules per type (monster pools, loot tables, hazard density, layout
  archetypes). Every descent should be different but every descent should feel
  on-brand. Layouts persist once generated.

## Biomes (first pass, unchanged)
1. Darkwood forests - the signature biome. Dense, fog-choked, old-growth forest.
   Witch covens, bandits, beasts.
2. Moors and highlands - open, windy, dangerous at night. Wolves, wights,
   ruined watchtowers.
3. Swamplands - disease, alchemy ingredients, hidden shrines. Hags, drowned
   dead.
4. Mountains and passes - mining, dwarven or old-imperial ruins, snow biome
   variant.
5. Farmland and river valleys - the safe-ish core. Villages, trade, faction
   HQs.
6. Blighted zone(s) - late-game corrupted regions where the "witch" threat is
   concentrated. (Now also holding dark-court holdings: see the Two Thrones.)

## Settlements
- Cities: walled, multi-district, faction seats, vendors, trainers, quest hubs.
- Towns: smaller hubs with blacksmith, alchemist, inn, chapel.
- Villages / hamlets: flavor, side quests, resource-gathering anchors.
- Cemeteries: semi-procedural surface sites attached to most settlements.
  Revenant spawns, grave goods, cemetery-keeper NPCs and mini-factions
  possible.
- (New) Every hold has a tavern: the save/respawn anchor (see Taverns below)
  and rumor hub.

## Factions - SUPERSEDED BY THE COURTS (see 12-moral-axis-factions.md)
The original six-faction roster has been reorganized under the Three Courts
and the Two Thrones. The full political structure now lives in doc 12; this
section records the mapping:
- LIGHT COURT: the human throne (king and queen), the Witch Hunter's Guild,
  the Church/Order, free cities of men/elves/dwarfs.
- DARK COURT: the elf-vampire throne (ruler court), the Old Faith/covens,
  orcs, undead, demonic pacts, vampires.
- NEUTRAL COURT: mercenaries, smugglers, thieves, the underworld - a mix of
  all races, unaligned, accepting any affinity.
- The Two Thrones (main struggle): both courts have mirrored nobility -
  crown, mapped holds, minor noble families - and the player aids one court
  toward total domination. Territory flips through the conquest system
  (doc 13); the nobility is procedurally generated as clans rise and fall
  (docs 13-14).
Territory control affects prices, patrols, quest availability, safe roads, and
which dungeons spawn hostile or allied NPCs. Mechanics live in docs 12-13.

## WEATHER: THE VEIL-TIDE (locked 2026-09-12, Nicko)

Weather is a continental FRONT system where weather carries the Veil's
charge: the pact's breathing made visible. Fronts move over the map
across in-game DAYS, read from the sky itself (watchtowers,
ridgelines), forecastable through tavern rumors and Storm-caster
senses. No UI meter: reading weather is survival knowledge.

- CHARGE STATES (per front): SUN-CHARGED (high pressure, bright
  post-clear nights: paladin patrols ride farther, evil players'
  daylight sleep is riskier, Holy Wards +1 tier flavor) /
  VEIL-CHARGED (low ceiling, fog and moon-haze: undead/wolf action
  extends into the dusk and dawn EDGES of the clock, Dark Pacts +1
  tier flavor, blighted zones exhale) / EVEN (ordinary weather).
- MECHANICAL BITE (locked, ruling): charge affects ONLY (a) clock
  edges (dusk/dawn extension or contraction), (b) faction patrol
  ranges, and (c) school power as +1-tier flavor. No new resource,
  no new numbers to balance; weather leans on locked systems.
- FORECASTING: read-the-sky gameplay plus rumor economy (doc 13)
  and Storm Magic senses. Wolves get a STORM-SENSE (locked): the
  front is forecastable to wolf players natively, extending the
  doc-19 moon-rule; the Hidden Court reads as weather-edge couriers.
- PER-BIOME PERSONALITIES: Darkwood (fog default, rain = sound-cover
  stealth bonus); moors (wind and visibility, storms arrive fast,
  beacons gutter); swamplands (mist thickness IS the misted clock
  weight, Task 1; VEIL fronts briefly make swamps the most neutral
  place in the world); mountains (blizzards dominate, cold exposure
  over the clock, passes CLOSE, garrison control reopens, doc 13);
  farmland (gentle weather, storms damage crops and economy holds,
  famine hooks doc 13); blighted zones (weather is WRONG: ash-gray,
  no clean weather ever, VEIL fronts pool there).
- NAMED STORMS (locked as DESIGN INTENT, authored at GDD stage): the
  RED VIGIL (sun-storm burning blight edges back for N days, light
  opportunity), the PALE TIDE (moon-fog lifting blight's ambient
  drain entirely, waking the wild wolf strains; full-moon stacking),
  STORM-CALLS (dark-court weather rituals dragging a VEIL front over
  an enemy hold as siege prep, doc 13 hook).

## Traversal
- Walk / run / sprint with stamina.
- NO FAST TRAVEL (locked 2026-09-12, Nicko, world GDD session): every
  journey is walked or ridden. SUPERSEDES the previous Daggerfall-style
  fast-travel line and the doc-00 fast-travel promise; doc 11's
  no-fast-travel-through-camps rule now reads as the whole rule. Scale
  is preserved by the ~2.3 km settlement gap (short hops, real
  journeys), not by teleporting past the world. Consequences: the
  affinity-relative clock governs EVERY arrival (departure time is a
  survival decision per doc 03's biome safety), tavern density and the
  camping system (doc 09) carry all long-haul logistics, and the rumor
  economy (doc 13) becomes the strategic map's only shortcut: you plan
  at the bar, then you ride.
- Mounts: travel speed only (locked). (Visuals: SUPERSEDED by the
  2026-09-14 mount ruling below; living 3D mounts per doc 29's
  carrier, "sprite mounts" was pre-pivot text.)
- The warp camp provides a region anchor but NOT fast travel (locked in
  doc 11: no fast travel through camps).

## Taverns (locked with Nicko, 2026-09-11)
Taverns are the save/respawn points of the world - the souls-bonfire analog,
themed into the fiction: you rent a room, rest, and set your respawn point at
the tavern local to whatever region you are exploring. This has world-design
consequences:
- Every explorable region needs at least one tavern within reasonable reach.
- Taverns double as rumor hubs, quest hooks, and faction-neutral ground (a
  good fiction anchor: hunters of every allegiance drink somewhere).
- Intermediate saves on roads: handled by the camping system (doc 09). Camps
  save progress; once unlocked, the warp camp becomes the DEFAULT forward
  respawn (taverns remain usable).
- The rumor economy is conquest-intel (doc 13): tavern rumors reveal hold
  vulnerability states - the strategic map is read at the bar.

## BIOME SAFETY BY ALIGNMENT (locked 2026-09-12, Nicko)

Frame: every biome has a CLOCK WEIGHT (how hard the affinity-relative
day/night clock bites there, per doc 12) and a HOME AFFINITY (who the
biome itself belongs to). Doc 13's conquest overlay rekeys patrols and
spawns when holds flip. A player's safety in a biome = their clock half,
weighted by the biome, colored by who holds it.

1. DARKWOOD FORESTS: the contested buffer.
   - Clock weight LOW: the canopy keeps the veil thin, night arrives
     early, day stays dim. Both alignments operate here at all hours;
     neither is ever fully safe.
   - Safety keys off TERRITORY, not the hour: coven-held glades are safe
     ground for dark players; Guild-ranger waystations and lit roads are
     the good player's thin safe threads; bandit camps sell passage to
     anyone (neutral court).
   - Wild wolf-strain dens live here (doc 04). Full-moon nights spike
     danger for everyone, any affinity.
2. MOORS AND HIGHLANDS: the exposed hourglass.
   - Clock weight MAXIMUM: open sky, no shade, the purest expression of
     the treaty of night (doc 19). Moor night is the most dangerous
     travel time for a good player (wights, evil packs). The mirror
     holds for evil players: paladin patrols ride far and you are
     visible for kilometers.
   - Ruined watchtowers are the mechanic: day shelters for evil players,
     night beacons for good ones. Knowing which tower is lit is survival
     intel.
3. SWAMPLANDS: the standing neutral.
   - Clock weight MISTED: fog diffuses sun and moon, the danger windows
     shrink both ways. But the swamp is never safe: its dangers (hags,
     drowned dead, disease) key off STANDING AND BARGAINS, not the clock.
   - Hag bargains and coven shrines admit the tainted and the bartered.
     A clean deep-good player is the swamp's favorite prey.
   - Highest alchemy ingredient density (doc 06 hook), paid for in risk
     instead of alignment.
4. MOUNTAINS AND PASSES: the garrison biome.
   - Clock weight MODERATE, WEATHER-DOMINATED: altitude and cold, not
     the clock, are the main threat (weather gameplay, this doc below).
     Night is deadlier for everyone; the wolf's inverted clock does not
     save you from a blizzard.
   - Home affinity: light by population (the dwarf city, mining holds
     feed the light court's war industry), but the high passes and
     old-imperial ruins are pre-Fall neutral ground, and the Deep
     Altar's underworld approaches sit beneath them (doc 19/22).
   - Safety rule: in the mountains, safety equals GARRISON CONTROL
     (doc 13), not the clock. A pass your court holds is safe at all
     hours; a contested pass is deadly at all hours.
5. FARMLAND AND RIVER VALLEYS: the clock's heartland.
   - Clock weight FULL: day towns, night raids, the doc 12 clock at
     full strength. Home affinity light by default (villages, faction
     HQs).
   - This is where doc 13's flips bite hardest: a dark-flipped river
     valley runs the INVERTED rule in mirror (night markets, day
     requisitions, thrall-taking). Farmholds are the conquest system's
     densest prizes.
   - This is the parish belt (doc 20): the Militant/Mercy meters live
     here and recolor safety village by village.
6. BLIGHTED ZONES: the pact's scars, the one true dark-keyed biome.
   - Clock INVERTED AND BROKEN: day is dim (the sun-motifs burned
     through, doc 19), night is calm for dark players, and (per ruling
     2 below) the blight is one of the two places an evil player can
     daylight-sleep without court-held cover.
   - For good and neutral players the blight is AMBIENT HOSTILITY
     (locked, ruling 1): constant low Ward-drain / taint-creep the whole
     time inside. The blight is an attrition biome you provision for.
     Aegis gear and Holy Wards are the counterplay (locked Aegis rule,
     doc 17). On top of attrition: the concentrated witch threat.
   - WOLF IMMUNITY (locked, ruling 3): the wolf strain belongs to no
     pact and no ledger (doc 19), so the pact's scar does not grip it:
     wolves cross blight without the ambient penalty. The Hidden Court
     is load-bearing for Third Path logistics through blighted zones.

### Strain overlay (cross-cutting)
- Vampire/undead players: the doc 12 inverted clock everywhere, scaled
  by each biome's clock weight.
- Wolf players: inverted clock, plus Darkwood and moors read them as
  kin by the wild strains (less hostile); the hunt-any-during-moon law
  still holds (doc 19).
- Strains change your clock and how locals read you; they never change
  a biome's home affinity.

### Locked rulings (2026-09-12, Nicko)
1. BLIGHT AMBIENT MODEL: passive attrition. Constant low Ward-drain /
   taint-creep the whole time inside blighted zones for good/neutral
   players, not just spawn pressure.
2. DAYLIGHT SLEEP GROUNDS FOR EVIL PLAYERS: the blighted zones AND
   dark-FLIPPED farmland are the only places an evil player can sleep
   by day without court-held cover (coven glades, garrison control) or
   defended camps. Conquest is logistically valuable for evil players,
   mirroring light-held farmland safety.
3. WOLF BLIGHT-CROSSING: locked, full immunity to the ambient penalty
   (lore-mechanical: no-ledger strain, doc 19).

## THE FOUR GREAT CITIES: MAP PLACEMENT (locked 2026-09-12, Nicko)

MACRO-GEOGRAPHY (locked FOR NOW, revisitable): a NORTH/SOUTH split of
the continent. The dark court holds the NORTH (the old realm's
heartland, the Fall's ground zero); the light court holds the SOUTH
(the seceded mortal provinces: coasts, river valleys, the parish
belt). Doc 19's fiction reads spatially: the light realm is the
secession, holding the rim of the south against the old capital's
heart. (Nicko: north/south for now, may play with it later.)

1. THE VEIL SPIRE (dark capital): NORTH-CENTER, on the old capital's
   site where the Veil Altar stood. The blighted zones RADIATE
   outward from it: the Fall's burn pattern (see the Altars below).
   Darkwood wraps its west, moors stretch south and north of it.
2. THE ORC CITY (dark minor): DEEP in the northern heartland, on the
   old pre-Fall borderlands where the scourge fought the realm for
   centuries. It is the scourge's first true city, now their proof of
   becoming. DEEP PLACEMENT (Nicko ruling): capturing it is a
   mid-to-LATE game event; reaching and exploring it is mid-to-late
   game activity. A light player's siege quest penetrates deep dark
   territory to reach it (doc 22's debt-default trigger).
3. THE UNDERGROUND DWARF CITY (light minor): DEEP in the south, under
   the great eastern massif's southern reaches. The forge-city
   anchoring the light court's war industry (doc 22). DEEP PLACEMENT
   (Nicko ruling, mirrors the orc city): a dark player's siege runs
   deep light-held ground; attackable from below per doc 22.
4. THE NEW CAPITAL (light capital): SOUTH-CENTER at the wrist's river
   delta on the southern coast, built after the Sunder (doc 22).
   Farmland and river valleys wrap it (the parish belt, the clock's
   heartland). The young city: new walls, human scale, the light
   court's urgency in stone.

- THE CONTESTED MARCH: the mid-continent border between north and
  south (moors, blight edges, Darkwood's southern eaves) is the war's
  front line and where doc 13's conquest metas churn. The two minor
  cities sit BEHIND their courts' territory: sieges are deep raids,
  not border hops.
- DISTANCES (on the ~130 km2 footprint): the four cities form a long
  diamond, ~10-14 km city-to-city: a half-day mounted ride, a full
  dangerous day-plus on foot, with NO fast travel (locked above).
  Every diamond crossing passes hostile biome; cities depend on the
  holds between them (doc 13's domino rule).
- BLIGHTED ZONES (count still open): radiate from the Veil Spire
  across the northern heartland; the south stays clean except where
  doc 13's events put scars.

## THE ALTARS: MAP PLACEMENT (locked 2026-09-12, Nicko)

All three altars sit in dark-held ground: every altar is a dangerous
destination for a Third Path player.

- THE VEIL ALTAR'S RUIN: inside the Veil Spire itself, its broken
  stones in the old throne's crypt. The dark court squats on its own
  crime.
- THE SUN ALTAR'S RUIN: deep in the NORTHERN moors, north of the Veil
  Spire: the old realm's holiest mount, desecrated but never toppled.
  A light or neutral pilgrimage runs the length of enemy land (doc
  20 relic-hunt frames); the Reliquary Wardens authenticate what is
  found there (doc 19).
- THE DEEP ALTAR: far beneath the great eastern massif, in the
  underworld's deeps, behind the HIDDEN COURT'S DEN: the wolf den IS
  the altar's threshold (locked doc 19/22). The massif's southern
  reaches hold the dwarf city above; dwarven masonry outlived its
  kingdoms and the underworld kept the foundation warm unknowing
  (doc 22). The Third Path must pass the Court to reach the altar
  (locked doc 19: the Signer's ace is load-bearing for the true
  ending).

## BLIGHTED ZONES: COUNT AND DYNAMICS (locked 2026-09-12, Nicko)

THREE SCARS (locked): the blight is three hand-authored scars,
~20 km2 total on the ~130 km2 map:
- THE CORE (~10 km2): the Fall's ground zero around the Veil
  Spire. Full attrition, densest witch threat, the Spire at its
  heart.
- THE MOOR MARCH SCAR (~5-6 km2): ancient satellite scar on the
  western moor march, from an age's demon breach. Designated THE
  CLEANSABLE SCAR (below).
- THE DARKWOOD-EAVES SCAR (~5-6 km2): where the burn licked the
  great forest's southern edge; blighted trees, coven deep-glades.

DYNAMICS (locked, HYBRID): scar hearts are FIXED ancient wounds;
their EDGES breathe with the war (doc 13 momentum). Dark winning =
blight creeps into adjacent border holds (those holds take the
ambient attrition rule at reduced intensity). Light winning = the
edges recede and crept holds clean up. The breathing edge is read
on the map itself (doc 13's map-reads-like-weather: withered
crops, gray grass, ash runoff), never a UI gauge: the blight is
the war's barometer. DEMON INVASION INTERACTION (IO note, for
review): doc 22's "scar tissue remains" reads as MINOR temporary
blight-lite patches fading over a season, not new full scars; the
three great scars are the Fall's alone.

CLEANSING (locked):
- RED VIGIL (doc 03 weather): TEMPORARY, burns back a scar's edge
  for N days, a window into cleansed land.
- THE CLEANSABLE SCAR (locked, Nicko): a major light-court spine
  questline (doc 20 spine-tier) can PERMANENTLY cleanse the Moor
  March scar mid-game. The cleansed scar becomes new light-held
  march land (doc 13 land-grant hooks); its dungeon cluster
  converts. The Core and the Darkwood-Eaves scar stay blighted
  until total domination (doc 13's cleansed-world ending).

## THE NEUTRAL COURT ACROSS THE THRONES (locked 2026-09-12, Nicko)

LEGAL MODEL (locked): THE SHADOW COURT. The neutral court is OUTLAWED
in both realms. The light and dark courts agree on exactly one thing:
the underworld dies. It persists IN SECRET alongside both: safehouse
dens, passwords, bribed gate guards, smugglers' docks, tavern back
rooms that do not ask names. There is no legal protection anywhere;
neutrality is survived, not granted. (Doc 12's free-trade neutral
fantasy stands: trade happens through fences, docks, and back-room
brokers, tolerated by low-level officials on the take, never by
charter.)

- DENS: roughly one neutral den per hold (the tavern's back room, a
  smuggler's dock, a borrowed cellar, a graveyard gatehouse), each a
  SECRET. Finding a den is gameplay (doc 20 rumor economy, Wardens'
  introductions, smuggling errands). Dens are hidden by default and
  unmarked; discovery by a court's inquisitors starts a PURGE clock.
- PURGE QUESTLINES (locked, Nicko): BOTH courts offer affinity
  questlines to root out and purge the neutral holds from their
  territory (light: Guild inquisitors and Church Militant cells;
  dark: orc enforcers and the houses' thrall-catchers). A player of
  either affinity can essentially TURN IN a den: identifies it to the
  holding court, triggering raid events. Purged dens close that
  hold's neutral services and feed the purging player's court/sect
  standing.
- CITY BATTLES (locked, Nicko): provoking a den inside a city
  (attacking its keeper, exposing it loudly, botching a purge
  stealthily) creates BATTLES WITHIN CITIES: good vs neutral or bad
  vs neutral street wars, doc 13 stability consequences attached
  (the hold's legitimacy meter takes the damage).
- DOUBLE-SIDED WORK (locked, Nicko): underworld operatives may take
  work from BOTH courts' patrons, EXCEPT direct sabotage of the court
  they last served. The deed log tracks it (doc 20's World Ledger);
  betrayal closes that court's tissue flow and opens its hunt lists.
- THE WAR'S STAKE (locked, Nicko): the war is good for business, BUT
  the underworld's elders know a TOTAL victory ends their niche. The
  neutral court quietly prefers stalemate, and its deep spine
  questline (doc 20 tier) reveals the elders SELLING INTEL to keep
  the war going: the neutral player's moral edge, tied into the
  Ledger. This seeds the Third Path congregation arc (doc 19: the
  Third Altar's faction IS the underworld united).
- THE WARDENS' EXCEPTION (doc 19 stands): the Reliquary Wardens'
  neutrality is inviolable and unprosecuted in practice (both courts
  fear the memory they keep); they are the shadow court's one
  protected circle, and the reason a purged den's people can flee
  somewhere.

## WITNESS-TIER NPC ROSTER: THE TIGHT NINE (locked 2026-09-12, Nicko)

Nine hand-authored witnesses of the Fall (doc 19's Long Agency),
one per court/sect/faction seat plus the wilds, plus three
named texture anchors. Locations follow the locked map (this doc).

TRUE WITNESSES (first-person memory of the Fall):
1. THE SIGNER (locked, doc 19): the Wardens' leader, under the
   eastern massif. The pact's signatory; the oldest witness alive.
2. VESNA OF THE DAWN-REFUSERS (light, sylvan high elven matriarch):
   the New Capital's elven quarter. Remembered the throne's court
   as a child; her line broke away before the pact. Keys light-court
   courtly quests and the elven civil war's wound.
3. MOTHER ROT, NECRO-ARISTOCRAT PRIMARCH (dark, necro-court): died
   in the first century after the Fall; the oldest undead, remembers
   dying. Her court politics are the Undertow's ledger in person.
4. THE LAST TENDER (dark sect, Old Blood root): ancient coven crone
   in a Darkwood deep-glade, last of the Veil Altar's original
   tenders (doc 22 Old Faith). Remembers what the altar was FOR.
5. BROTHER ANCIL, MILITANT CONFESSOR (light sect, Church Militant):
   holds a parish in the contested march. A mortal: he is the
   confessor OF a witness he executed, carrying a confession he
   cannot absolve. Human memory, second-hand but living. Grudge-
   bearing through his dead charge's house.
6. THE GRAVE-WARDEN OF THE MOOR MARCH (neutral, Wardens-adjacent):
   cemetery-keeper at the cleansable scar's edge; ties the blight
   purge questline to the Wardens.
7. THE MOOR'S WIGHT-BARD (wilds, undead court's edge): a wight that
   predates the Split, a corpse-memory that does not speak in
   words but REPLAYS the Fall's battles where it fell (doc 04
   undead grammar: no dodge/parry). Grudge: the dead remember.
8. THE ELDER'S SHAPE ELDER (neutral, Hidden Court): under the
   eastern massif, the oldest wolf, born the year the Veil altar
   broke. Remembers through the pack's blood-memory, not eyes.
9. THE DEBT'S ECHO (special place-NPC, locked, Nicko): not a person:
   the erased statue field outside the Veil Spire (doc 19's
   diegetic debt reading). A witness as landmark.

TEXTURE ANCHORS (named, not witnesses, confirmed by Nicko):
- WAR-FATHER GHASH (the orc city): impossibly old orc who remembers
  the pre-Fall holy war FROM THE OTHER SIDE (the Devil's early
  creation's own memory). Not a Fall witness; the war's.
- HALF-FACE (the smugglers' den under the New Capital's docks):
  a dawn-refuser elf who burned his own face off escaping the
  throne's service; knows the old realm's roads, which is why his
  routes survive.

GRUDGE RULE, REFINED (locked, Nicko, sharpens doc 14): grudges take
hold only if the murder was WITNESSED. Killing a roster witness in
secret is clean; killing one before eyes (their retainers, their
court, their den) brands the killer across that faction web
permanently. The roster above marks WHO is grudge-bearing and to
whom. Design intent: assassination becomes a stealth problem, not
a murder problem; the world remembers what it SEES.

THE PURGE OF MEMORY (locked, Nicko): BOTH courts offer
assassination questlines against the roster: kill the witnesses,
purge the old world from living memory. Light motive: erase the
shame, end the Long Agency's testimony (the Militant's version:
end the heresies; the Mercy heresy-adjacent question: some want a
witness's story preserved, not the witness). Dark motive: erase
the debt's witnesses before the default. A witness's death closes
their personal quest keys permanently (the shared-past quests,
doc 19) and advances the killing court's purge standing. THE
WORLD'S COUNTERWEIGHT: every assassination makes the remaining
witnesses harder to find (they go to ground; the Wardens hide
them, the Hidden Court shelters some); a player hunting memory
feeds the underworld's relevance.

## PER-BIOME INGREDIENT CATEGORY LISTS (locked 2026-09-12, Nicko)

The member lists for doc 05's category secondaries. Rules: every
biome's list carries the COMMON member (any biome) plus BIOME
SIGNATURES (rarer, higher-tier, shift the grade roll). Biome-keyed
recipe drops (doc 05/06) correspond: hunting a biome for its
signatures is the gather loop's travel engine. NO fast travel makes
these choices real logistics.

1. DARKWOOD FORESTS
   - Woods: oak (common), yew, WITCHWOOD (signature: coven-tended
     groves only, axis-tainted, dark-biased enchants).
   - Hides: wolf, bear; BOAR-TUSK LEATHER signature.
   - Bone/sinew: common bones; COVEN-BLESSING SINEW signature
     (ritual components, Warden-authenticated only).
   - Herbs: moonbell, grave-moss, hemlock; BLIGHTCAP signature
     (grows only at blight edges, alchemy grade-shifter).
   - Reagent spawns: Ember and Frost Motes in glade-clearings;
     DARK reagents (Grave Motes) densest here; Storm at the
     ridgelines.
2. MOORS AND HIGHLANDS
   - Woods: heath-wood (common, poor), drift-oak; THORN-YEW
     signature (watchtower-grade).
   - Hides: moor-pony, wight-touched wolf; GHOUL-HIDE signature.
   - Bone/sinew: barrow-bone signature (undead ossuary parts).
   - Herbs: bog-myrtle, crow-garlic; STORM-THISTLE signature
     (Storm reagents' plant source).
   - Reagent spawns: STORM chain densest (Spark Motes in
     thunder-weather, Veil-Tide fronts pool them); Holy Motes
     rare on old chapel mounds.
3. SWAMPLANDS
   - Woods: bog-oak (waterlogged, FINE-grade bonus), BLACKWOOD
     signature (the dark-enchants wood).
   - Hides: drowned-dead hide (undead loot table), eel-leather;
     HAG-HIDE signature (barter-gated, hag bargains only).
   - Herbs: densest herb biome: feverfew, bloodroot, marsh
     heliotrope; CRYPT-BLOOM signature (Dark reagents bloom).
   - Reagent spawns: DARK chain densest in the world; Grave/Crypt
     Wisps at drowned shrines. Alchemy's richest biome (doc 06).
4. MOUNTAINS AND PASSES
   - Metals: iron (common), steel; COLD IRON signature (blight-
     burn quenched, Aegis-adjacent recipes) and the DEEP STEEL
     seams nearest the underworld (Gate to blacksteel refining).
   - Woods: pine, high-altitude birch.
   - Hides: ibex, snow-cat; WYRM-SCALE signature (the deep
     wyverns' sheds, T4-5).
   - Bone/sinew: hardened chitin (cave clatterers); TROLL SINEW
     signature.
   - Gems: richest gem biome (Mining/Gem Crafting anchor).
   - Reagent spawns: Frost chain densest (Rime/Glacial); the
     DEEP ALTAR's approaches carry mixed Motes (doc 19: the altar
     kept balance).
5. FARMLAND AND RIVER VALLEYS
   - Woods: willow, river-ash; APPLE-WOOD signature (grade-bonus
     for utility crafts, cooking-smoke ties).
   - Hides: cattle-hide, doe (common leathers' source biome).
   - Bone/sinew: common bones (bulk supply).
   - Herbs: kitchen herbs + the healing staples (comfrey,
     yarrow); CHAPEL-GARDEN HOLY HERBS signature (light-held
     parishes only, parish-meter gated, doc 20).
   - Metals: no ores; river-panned silver FLAKES minor.
   - Reagent spawns: even mix, low density; the war's scar tissue
     (doc 03 dynamics) can temporarily seed Grave Motes.
6. BLIGHTED ZONES
   - Metals: CORRUPTED IRON signature (blight-steeped, dark
     enchants' catalyst), blacksteel ORE-SCARS (the Fall burned
     rich veins open; the deep-war metal's wildest source).
   - Woods: BLIGHTWOOD signature (witchwood's ruined sibling,
     strongest dark-socket wood, harvest = taint exposure even
     for dark players, doc 17 taint bands).
   - Hides: blight-wolf, witch-hag; TALLOW-HIDE signature (rendered
     undead fat, poisons base).
   - Herbs: BLIGHTCAP densest; NOTHING CLEAN grows; alchemy here
     is dark or dangerous.
   - Reagent spawns: DARK chain absolute densest (the pact's
     scar breathes, doc 03 dynamics); Holy reagents CANNOT SPAWN
     (locked consistent with doc 17's axis-gate; the Red Vigil's
     cleansed ground briefly spawns Holy Motes, weather hook).
   - WOLF-NOTE (doc 03 wolf immunity): wolf players harvest here
     WITHOUT ambient exposure, making Hidden Court crafters the
     blight's natural harvesters.
- METALS master list (doc 05 stands): iron, steel, silver,
  cold iron, blacksteel. Silver spawns in moor barrows + mountain
  seams; cold iron only in mountains + blight scars (the Fall's
  burn exposed it: why Aegis-adjacent smithing is war-central).

## PROCEDURAL NOBILITY: NAMES, HERALDRY, LIFECYCLE (locked 2026-09-12, Nicko)

### Name pools: STEM ASSEMBLY (locked)
Each race gets curated stem lists (prefixes, suffixes, hold-
modifiers) assembled by seed into house and hold names. ~40 stems
per race, effectively infinite assembly, all hand-curated in
flavor.
- DWARF: stone-word + deed-word (Karak-Zhorn, the Under-Forge).
- HUMAN: virtue/object + suffix (House Ambrose, House Fellgate).
- ELF/VAMPIRE: fallen-solar stems, and VAMPIRE NAMES DECAY BY AGE
  TIER (doc 14's name distortion made procedural: Vesperline >
  Vesperlyn > Vsp'lyn, the Undertow's receipts readable in names).
- ORC: earned-titles as names (doc 14's earned-leadership
  culture): First-Forge, Deep-Breacher, names are RESUMES.
- PLAYER NAMES PROPAGATE: land grants enter the pool (locked doc
  14), marriage carries them into future generations' pools.
- THE WITNESS ECHO (doc 03 roster tie): some stems are pre-Fall
  words that only the Tight Nine use in dialogue.

### Heraldry: CHARGED SHIELDS (locked)
Procedural heraldry from a curated GRAMMAR, not name-agnostic art:
- FIELDS per court palette: light = sun-gold/white/blue; dark =
  veil-black/blood-red; neutral = iron-gray/teal.
- CHARGES per race: light human = stags, towers, rivers; sylvan =
  stars and bows; dwarven = anvils and mountain-hall marks; dark
  elf-vampire = moons, bats, BROKEN SUNS (the Veil Spire's fallen
  motifs); orc = tusks, chains, NEW FORGES (the First Forge mark
  as the becoming-a-people story on a shield, doc 22).
- DIVISION patterns by rank: crown holds = complex; minor houses
  = simple.
- Player-authored banners (locked doc 02 flag) use the SAME
  grammar in the player's UI: the player speaks heraldry fluently.
- Design payoff: every hold banner, retinue tabard, and siege camp
  reads instantly. You learn to read the war's map from heraldry
  alone: doc 13's map-reads-like-weather principle, extended to
  politics. No politics UI needed.

### Clan lifecycle: THE SIX-STATE HOUSE (locked)
Doc 13's living nobility made an explicit state machine. Houses
move between states via conquest, marriage, debt, and land grants
(doc 13/14 hooks):
1. RISING (new grant): hungry, cheap contracts, unproven.
2. ESTABLISHED: holds, marriages, rivals, the normal state.
3. ASCENDANT (post-victory): new banner flourishes, land grants,
   marriage offers TO the player, doc 20 personal-axes richest.
4. DECLINING: lost holds, succession crises, doc 13's triggers
   fire more easily; desperate patrons pool (doc 20).
5. FALLEN-IN-EXILE: lost the last hold; the house survives as a
   retinue-in-exile, questable for restoration (doc 20's
   personal axes: a Declining patron's daughter questing to
   restore the house's banner).
6. EXTINCT: the name dies; deeds pass to the Ledger's history
   (doc 20's World Ledger remembers, erased statues join the
   Debt's Echo field, doc 03 roster).
- Regicide-with-heirs (locked doc 13) is the EXTINCTION engine;
  debt (dark court, doc 19) is the dark houses' Declining pull;
  land grants (doc 13) are the player-adjacent RISING engine.
- The war's churn (doc 13) reads through these states: a map of
  banners in motion, states legible through heraldry + names.

## RACE ORIGINS: DEEP DETAIL (locked 2026-09-12, Nicko)

Doc 22's pre-Fall sketch LOCKED with three map-grounding additions
and one cosmology completion:

- DWARVEN ALTAR-MASONS (locked): the dwarves built the three
  altars' stones in the age before elves held the throne (doc 22).
  MAP GROUNDING: the Deep Altar stands in dwarven-masoned deeps
  under the eastern massif where the dwarf city now sits: the
  forge-city is built on its ancestors' greatest work, unknowing
  (doc 22). The massif's mines are the OLD QUARRIES: why mountain
  gems and cold iron run richest there (doc 03 ingredient lists
  consistent).
- COVENS AS THE VEIL ALTAR'S FIRST TENDERS (locked, doc 19/22):
  the Old Faith predates the throne; the pact perverted their
  altar; their oldest doctrine is anger at the pact, the Old
  Blood sect's root. MAP ADDITION: the Darkwood's coven glades
  are the OLD ALTAR-GARDENS, tended since the Age of the Sun
  (why the Darkwood reads coven-held in doc 03's biome safety);
  the Last Tight-NINE Tender is the surviving link.
- ELVEN SPLIT, HUMAN BACKBONE, ORC SCOURGE, UNDEAD POST-FALL:
  locked as doc 22 wrote (no changes).
- THE DEEP ALTAR'S DEDICATION (locked, Nicko, the cosmology
  completion): the Deep Altar was NEVER a throne instrument. The
  masons built it DOWN-DEEP: not to the sun or the veil but to
  the world's own deeps, the one altar the sky-powers never
  claimed. Its re-kindling (doc 19's true ending) is literally
  returning the world to ITSELF rather than to either court. It
  belongs to neither throne because it belongs to the GROUND;
  the neutral underworld being its unknowing congregation is the
  cosmology in one image.
- WEREWOLF WILD STRAINS, MAP GROUNDING (locked, Nicko): the wild
  strains are the undisciplined bite-spread (doc 19 locked), the
  Hidden Court the re-disciplined remnant. FERAL PACK DENS sit
  at the edges of ALL THREE ALTAR RUINS: the broken wards
  explain where wild strains pool (the Sun altar's moor ring,
  the Spire's blight ring, the Deep Altar's underworld
  approaches, the Hidden Court's territory).

## NAMED STORMS: THE THREE (authored 2026-09-12, Nicko)

Rare hand-authored storms on the Veil-Tide front system (locked
above), spine-adjacent set pieces. Cadence: each fires AT MOST
once per in-game season, never twice back-to-back; a Red Vigil
never coexists with a Pale Tide.

1. THE RED VIGIL (sun-storm)
   - What it is: a standing high-pressure wall of harsh gold
     light, a blight-burning dry spell that rolls off the
     southern realms northward (light court's weather, read as
     divine favor: doc 13's divine-prayer event's small cousin).
   - Duration: N in-game days (GDD tuning, working number 5-7).
   - Effects: burns back ONE scar's edge for the duration (doc 03
     blight dynamics: a window into cleansed land); blight ambient
     attrition suspended inside the burned-back band; paladin
     patrol range at maximum; Dark Pacts cast at -1 tier flavor;
     evil players' daylight sleep NEVER safe inside a Vigil.
   - Opportunity texture: the blight's inner dungeons open to
     light/neutral raiding (their monster tables exposed without
     attrition); the cleansable Moor March scar's purge questline
     (locked above) REQUIRES one Red Vigil as its rite's crown.
   - Counterplay: dark courts shelter in dens and deep woods;
     wild wolf strains (immune to blight but not to fire) push
     OUT of the Vigil's radius into border holds.
2. THE PALE TIDE (moon-fog)
   - What it is: a low silver fog-bank that flows up from the
     swamps and coast at dusk, lasting N days (working 4-6).
   - Effects: lifts blight's ambient drain ENTIRELY while it
     lies (locked design intent); the world reads VEIL-CHARGED
     at maximum; undead and wolf action extends deep into the
     clock's edges (doc 03 charge rules, maxed); wild wolf
     strains WAKE and pool (stacking with full moons: the
     Pale-Tide-full-moon night is the game's most dangerous
     night, and the Hidden Court's busiest).
   - Opportunity texture: blight crossing without attrition (the
     wolf couriers' superhighway); Dark Pacts +1 (maxed); the
     Deep Altar's approaches open widest; holy wards gutter.
   - Counterplay: light players bunker; Aegis gear carries.
3. STORM-CALLS (dark-court weather ritual)
   - What it is: a doc 13 siege-prep ACTION: dark-court casters
     (Storm Magic rank-and-file, doc 17 enemy casters) drag and
     PIN a VEIL-CHARGED front over an enemy hold before a siege.
   - Effects: the target hold's garrison fights under lowered
     ceilings and Veil charge (dark kits at +1, undead/wolf
     edges extended); doc 13's siege window lengthens by the
     pinned front's stay.
   - Counterplay: Storm-caster sniping (kill the anchor casters,
     the front drifts free); Holy Wards' garrison-ward rite
     (light counter-ritual, doc 17's school) burns the pin.
   - Design intent: the war's weather is WEAPONIZED late, but
     never invisibly: a Storm-Call's arrival is read in the sky
     days ahead (Veil-Tide forecasting rules, locked above).
- CADENCE NUMBERS: GDD tuning (front cadence, N values, season
  definition), consistent with the tracker's tuning block.

### IN-GAME CLOCK: TUNING LOCKED (2026-09-12, Nicko)
- RATIO: 24:1. One in-game day = 60 real minutes; even halves
  (day = 30 real min, night = 30 real min). The affinity clock's
  danger half is always a real gameplay half.
- VEIL-TIDE CADENCE (locked): a SEASON = 21 in-game days; fronts
  change every 2-4 in-game days; named storms fire at most once
  per season each (locked rule), working durations: RED VIGIL 6
  days, PALE TIDE 5 days. A named storm lands roughly once per
  3-4 real hours of play: rare but seeable. Vigil and Tide never
  coexist (locked).

### TUNING PASS (locked 2026-09-12, Nicko, world GDD tuning session)
- NODE DENSITY (doc 06 open item): MODERATE. ~6-10 gatherable
  nodes per hold region per type; denser in farmland and
  swamps; sparse in blighted zones. Gathering routes repeat
  across the ~2.3 km settlement-gap world without feeling
  farmed.
- Named-storm N values and season length: see Veil-Tide cadence
  above (locked).

## RULING PASS (open-questions sweep, 2026-09-14, Nicko)
MOUNT VISUALS: LIVING MOUNTS. After the 3D pivot (doc 29), mounts are
true 3D models like everything else (the 46-asset Meshy pipeline,
low-poly pixelated, own atlas, riding pose), with doc 03's mount lock
intact: travel speed only, no mounted combat. The pre-pivot
"sprite mounts" line above is SUPERSEDED by this ruling (carrier
change, not a design change). Exact mount asset spec authors with the
first mount asset run.
## Open Questions (current state)
- Continent size: RESOLVED 2026-09-12 (see SCALE TARGET above). Open
  dependent: exact in-game day length (even day/night halves locked,
  24:1 vs 48:1 ratio) - GDD tuning.
- Weather: RESOLVED 2026-09-12 (VEIL-TIDE above); named-storm authoring
  and front cadence numbers at GDD stage.
- Biome-safety-by-alignment: RESOLVED 2026-09-12 (section above).
- Blighted zone count and map placement (how many scars, where they
  sit relative to the pre-Fall ruins): world GDD, this session's
  ruins/cities pass.
- Four Great Cities map placement + the Sun/Veil altar ruins + the
  Deep Altar threshold: RESOLVED 2026-09-12 (Nicko, doc 03):
  north/south split (locked for now, revisitable), cities deep in
  home territory (sieges = mid-late game deep raids), Veil Altar
  ruin in the Spire's crypt, Sun Altar ruin in the northern moors,
  Deep Altar under the eastern massif behind the Hidden Court's
  den.
- Witness-tier NPC list (who alive remembers the Fall): world GDD
  authoring (doc 19 assignment, now owned here alongside the map
  passes).