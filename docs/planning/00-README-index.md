# WITCH HUNTER - Planning Index

Project: Witch Hunter
Stage: Concept / Pre-production planning
Target engine: Unreal Engine (version TBD, see open-questions.md)

## High Concept
A single-player, third-person, open-world action RPG set on a dark fantasy
continent. The world renders in true 3D (dynamic lighting, fog, volumetrics)
while all characters, creatures, and props are presented as 2D sprites in a
retro 1980s/1990s dark fantasy and pulp illustration style, echoing Daggerfall's
structural ambition with a modern atmospheric layer on top.

## Pillars
1. Old-meets-new presentation: sprite-based retro fantasy art inside a modern
   3D engine with dynamic lighting, fog, and atmosphere.
2. Souls-like action combat: lock-on, dodge roll, camera follow, deliberate
   pacing.
3. Specialize or fall behind: Morrowind-style skill-by-use progression where
   the tools you use make you better at using them, and everything you do
   feeds some XP system.
4. A living dark continent: biomes, factions vying for control, procedural
   dungeons, cemeteries, towns, and cities.

## Document Index
- 00-README-index.md         - this file
- 01-vision-high-concept.md  - pitch, pillars, tone, references
- 02-art-style.md            - visual direction, sprite pipeline, lighting
- 03-world-design.md         - continent, biomes, settlements, taverns, dungeons
- 04-combat-system.md        - action combat, lock-on, dodge, weapon classes
- 05-crafting-system.md      - weapons, armor, magic crafting
- 06-loot-and-resources.md   - loot tables, gathering skills, economy hooks
- 07-leveling-progression.md - XP model, skill-by-use, builds, stat points
  (9 stats, 5 points/level)
- 08-open-questions.md       - running list of decisions still needed
- 09-expedition-camping.md   - partial survival, expedition prep loop, camping
- 10-cooking-meals-drinks.md - cooking system, daily meals, utility drinks
- 11-warp-camp.md            - mid-game warp camp home base, tiers, retinue
- 12-moral-axis-factions.md  - moral axis as faction-alignment gate, two courts
- 13-territory-conquest.md   - dynamic conquest triggers, the moving map
- 14-races-houses-naming.md  - race-flavored house generation, chain of command
- 15-skill-lines.md          - the skill lines (28 core + specialties)
- 16-specialties.md          - titled specialty combos, bonuses, identities
- 17-magic-system.md         - magic system: five schools, spells, hybrids,
                               taint, corruption kits (LOCKED 2026-09-12)
- 18-skill-progression.md    - ranks/tiers/techniques, per-line meanings
- 19-fall-of-the-veil-throne.md - continental lore spine: the Fall, the
                               debt, the Undersovran, the Third Altar
- 20-quests-factions-gdd-part1.md - quests/factions GDD: two-tier quest
                               architecture, World Ledger, frames, parish
                               rules, wolf trial + ladder, safety rules
- 21-quests-factions-gdd-part2.md - quests/factions GDD: spine outlines,
                               wolf ladder menus, safety addendum
- 22-quests-factions-gdd-part3.md - quests/factions GDD: transformation
                               lines (vampire/undead), pre-Fall races
- 23-expedition-followers.md  - the party system: 4 follower types,
                               level-gated slots, follower XP +
                               menu, command grammar
- 24-art-bible.md             - canonical concept-art catalog: locked
                               mood register mirror, per-biome palette
                               law, generation grammar, frame catalog
                               (23 frames), QA checklist
- 25-art-pipeline.md          - PROPOSED: art production pipeline for
                               in-game sprite assets (turnaround ->
                               directional bake -> frame stacks ->
                               cleanup -> atlas -> billboard), feasibility
                               verdict + pilot milestone
- 26-sprite-production-queue.md - living to-do queue for the race sprite
                               production run (10 cards: orc/undead/
                               vampire/elf/dwarf, male+female each),
                               standing pilot lessons incl. hand-pose
                               drift rule
- 27-equipment-visual-system.md - PROPOSED: layered paper-doll equipment
                               system (body + per-piece sprite layers,
                               palette variants, anchor contract) for
                               player fashion expression

## Decisions Locked So Far (2026-09-11)
1. Procedural dungeons persist once generated (Daggerfall-style).
40. Combat technique menus COMPLETE (2026-09-12, combat/crafting/loot
    session): all 36 tier-up menus for the 9 combat lines written and
    LOCKED with Nicko ("This all looks good for weapons"): exactly 3
    techniques per menu (one offensive, one utility, one specialist),
    free mix of moves/passives, doc-18 anchors carried. Full text in
    04-combat-system.md.
41. Crafting depth LOCKED (2026-09-12, combat/crafting/loot session):
    - Craft quality FLOOR/CEILING model: skill tier sets the quality
      floor, station quality sets the ceiling; grade ladder Crude/
      Standard/Fine/Superior/Masterwork; Masterwork = +1 enchant socket.
    - 5 station tiers (Field Kit/Village/Town/City/Grandmaster); a
      Grandmaster forge beats a village forge by two grade-steps of
      ceiling; the maxed warp camp's Grandmaster stations exceed every
      world station except the ONE legendary dungeon station.
    - Utility crafting mapping: arrows/fletching/torches/LOCKPICKS under
      Weaponsmithing (Enchanting stays purely magical); payloads and
      throwables under Alchemy.
    - Recipe economy: recipes as biome-keyed loot, tier-gated attempts,
      reverse-engineering (named items can never be reverse-engineered,
      only Reforged), materials set the output tier, Holy/Dark recipes
      burn in wrong hands.
    - AEGIS EXCLUSIVE (Nicko): permanent Aegis gear is an exclusive
      faction asset, deep-good craftable only, no NPC service at any
      price.
    - LEGENDARY STATION (Nicko directive): the single legendary dungeon
      station sits in an obscure, difficult place, never mapped, no quest
      marker; found only by assembling cumulative redundant clue chains
      (Grave Whispers on dead smiths / graverobbing, tavern rumors and
      purchased intel via Speechcraft + neutral-court brokers, chance
      dungeon finds). Spec in 05-crafting-system.md.
42. Ingredient system LOCKED (2026-09-12, combat/crafting/loot session,
    Nicko "I like the ingredients system, lock it in for now"): New
    World adaptation - recipes have 1 tier-locked primary slot plus
    2-3 CATEGORY secondary slots (any category member fills them,
    rarer/higher-tier picks shift the grade roll, no duplicate
    ingredients per recipe); refining layer (raw to refined at
    stations, catalyst reagents, station tier caps refine tier, bonus
    yield rolls); five arcane reagent ladders (Fire/Frost/Storm free,
    Holy/Dark axis-gated, Mote > Wisp > Essence > Quintessence);
    Hunter's Components (rare world finds guaranteeing one specific
    enchant). NOT adopted: Trading Post, Azoth, town-project station
    leveling. Sub-items: per-biome category lists = world GDD;
    reagent ratio + refining bonus scope = GDD tuning. Spec in
    05-crafting-system.md.
43. Loot economy LOCKED (2026-09-12, combat/crafting/loot session):
    four-layer loot tables (monster parts guaranteed-weighted /
    biome-keyed materials / gear Rarity roll / special slot with COURT
    TERRITORY OVERLAY and dungeon-type keys); Rarity-vs-Tier CROSSING
    RULE (T1-T2 span all rarities, T3 mostly Uncommon/Rare, T4 = Rare
    and Named only, T5 = Named only always story-attached; fixed
    region difficulty sets each region's tier band); three vendor
    families (light/dark/neutral brokers; court contracts pay
    standing; Aegis components never sold to non-deep-good); Hunter's
    RELICS (hand-authored Tier-5 named items, fixed acquisition
    stories, ~9 weapon + ~6 armor/charm at GDD, Reforge-only). Spec
    in 06-loot-and-resources.md.
44. Combat feel rules LOCKED (2026-09-12, combat/crafting/loot
    session): POISE/STAGGER as the universal stagger resource (pools
    scale with armor weight class and enemy size, never player level;
    chip poise through blocks; stagger = committed recovery
    animation); PARRY windows by source (shield > Riposte Master >
    Twin-Parry > shaft-parries > bare blade; narrow windows earn
    bigger punishers; only faction soldiers can parry, telegraphed);
    STAMINA rules (regen pauses ~1s after any stamina action, fast
    regen idle/walking, ~50 percent reduced while blocking, near-zero
    while attacking; stamina-break at zero); EQUIP LOAD (worn-gear
    weight, separate from Carry Weight inventory stat) gates roll
    speed into light/medium/heavy bands; ENEMY GRAMMAR: enemies use
    the player's verb set (humanoids full grammar, beasts no
    block/parry, undead no dodge/parry); faction soldiers fight with
    player grammar (light-court pairs shield-and-spear, dark-court
    packs bleed-and-retreat); court forces are the schools made
    hostile (paladins = Holy Wards grammar, vampire/undead raiders =
    corruption kits incl. The Embrace on downed retinue); court
    ambushes teach the Aegis counterplay viscerally. Exact numbers =
    GDD tuning. Spec in 04-combat-system.md.
45. THE FALL OF THE VEIL THRONE (2026-09-12, Nicko, lore spine for the
    quests/factions + world GDD work; spec in NEW doc
    19-fall-of-the-veil-throne.md):
    - CORE (Nicko): the elf-vampire court was once the SOLAR THRONE,
      sole ruler of the continent. The pursuit of power led them to
      dark magic that invited evil into the world; a pact with the
      Devil cost them their mortality and corrupted them into
      vampires. The corruption split the continent: the political
      struggle of the present day is the scar.
    - THE UNDERTOW / THE DEBT (Nicko): the pact is a LEASE that still
      collects, escalating by generation (memory, names, the sun,
      their future). The dark court's secret motive: they are OUT OF
      CREDITS. They must reunite the realm to have more to sacrifice.
      Public face is restoration; the debt is the hidden truth.
    - COMEBACK EVENT TIE-IN: the doc-13 evil comeback event (mass
      demon summon) is the DEBT DEFAULT: when losing the war, the dark
      court opens the nether and demons pour into the waking world as
      an invasion. Bankruptcy option, not preferred weapon.
    - THE UNDERSOVRAN (Nicko): the Devil is NOT a waking walking
      entity; a specter of evil with a grip on the mortal world since
      the Fall. Presence is CONTRACTS and SIGILS only; never a spawn,
      boss, or body.
    - THE LONG AGENCY (approved): the Split is living memory; the Fall
      generation still walks. Killing a long-lived witness creates
      permanent grudges (doc 14 hook made mechanical); shared-past
      quest keys; witness-tier dialogue; ancient-witness retinue
      possibility.
    - THE THIRD ALTAR (approved): the old realm's balance was
      ceremonial, three altars (Sun, Veil, Deep). The Fall broke the
      Veil altar. The true ending is re-kindling the DEEP ALTAR, held
      unknowing by the neutral underworld; the six refusals are the
      ceremonial qualification (fed neither altar may light the
      third).
    - PARKED, NOT APPROVED: Schism Sects (sub-alignments: Church
      Militant vs Church of Mercy; Old Blood vs Veil Faithful) and the
      Reliquary Wardens (third-force lore keepers, neutral player
      faction).
46. SCHISM SECTS, RELIQUARY WARDENS, THE HIDDEN COURT (2026-09-12,
    Nicko rulings, spec in doc 19):
    - SCHISM SECTS LOCKED: sub-alignments within each court
      (resolves doc 12's multiple-alignments open question). Light:
      Church Militant (purge doctrine) vs Church of Mercy (redemption
      doctrine). Dark: the Old Blood (debt-despising pureblood
      restorationists) vs the Veil Faithful (creditor-worshippers).
      Sect standing is a second meter; local parishes flip by the
      player's deed pattern; sect choice shapes dark endgames (Old
      Blood = restoration/Lich King line, Veil Faithful = the
      bankruptcy default).
    - RELIQUARY WARDENS LOCKED, placed under the UNDERWORLD
      questlines: the neutral court's innermost scholarly circle;
      the neutral player's faction; hold contradictory Fall accounts,
      pre-Split ruin keys, and AUTHENTICATE hunter's relics. Leader
      working name THE SIGNER: the pact's royal-chancellor signer,
      self-starving for centuries, trying to undo her signature.
    - SCHISM SECT STANDING: sub-meter inside each court (Militant<->
      Mercy, Old Blood<->Veil Faithful), gates quest appearance,
      stacks with alignment. RESOLVED 2026-09-12 (Nicko).
    - SECT ACCESS: court-gated (Militant/Mercy light-only, Old
      Blood/Veil Faithful dark-only, no cross-play). RESOLVED
      2026-09-12 (Nicko).
47. QUESTS/FATIONS GDD PART 1 (2026-09-12, spec in NEW doc
    20-quests-factions-gdd-part1.md):
    - TWO-TIER ARCHITECTURE: hand-authored SPINE chains (alignment
      ceremonies, apexes, wolf line, Third Altar, debt arc, comeback
      events; fixed NPCs immune to proc-gen chaos) vs procedural
      TISSUE quests (~90 percent; proc systems may only write
      tissue).
    - THE WORLD LEDGER: one simulation state quests read (war
      momentum, holds, hidden debt tension, parish meters,
      standings, deed log, unresolved consequences); quests are
      REACTIONS to ledger state, never random rolls. Every spawn
      answers a why-now.
    - FRAME GRAMMAR: patron (cast from doc 14 procedural NPC pools)
      + need + site + resolution axes + consequence tags + PERSONAL
      AXES. Nicko ruling locked: old-princess texture made
      systematic, secondary characters whose fate keys off HOW the
      need was resolved (save-by-honor may join the retinue
      willingly; slay-while-terrorized allows enslavement per doc
      11; free-and-escorted = honor only). 2-3+ endings per tissue
      quest, differing in personal/retinue/standing/material
      reward, not necessarily world state. Fun and interesting play
      first.
    - EXPIRY FAILS-FORWARD (Nicko): tissue quests expire into
      consequences (patron death = betrayal/inheritance; timers =
      corpse scenes, occupied holds, harder return versions); the
      Ledger remembers abandonment into a trustworthy-patron vs
      desperate-patron pool split.
    - PARISH-FLIP RULES: Militant<->Mercy meter per chapel hold,
      +/-50 flip with +/-25 hysteresis band, three-plus parishes
      tip the region's bishop, sect meter independent of moral
      axis.
    - WOLF TRIAL LOCKED: six stages (Scent/Law/Fast/Vigil/Bite/
      First Hunt).
    - WOLF KIT RESOLVED 2026-09-12 (Nicko: "the werewolf only needs
      4, just like the vampire and undead. Not super expansive"):
      transformation kit of exactly FOUR abilities (doc 17
      corruption-kit model, supersedes any 36-menu ladder):
      Hunter's Sprint (travel form, you are the mount) / Pounce
      (leap-and-pin) / Terrifying Howl (fear/stagger radius) /
      Elder's Shape (near-human battle form, capstone). Kit levels
      by its own use under doc 18; abilities FIXED. Hidden-Court-
      trust gating remains IO proposal for review.
    - DEBT VISIBILITY LOCKED + REAFFIRMED (Nicko): diegetic only,
      before AND after the discovery arc; never a visible meter;
      post-arc reading through the Signer's ledgers, erased
      statues, sermons, requisitions.
    - SAFETY RULES: spine NPC immunity; debt fuse independent of
      quest completion (comeback event always fires on war state);
      threshold triggers not NPC triggers for major lines; surviving
      cast NPCs promotable to recurring named status.
    - FRAME LIBRARY FIRST PASS RESOLVED 2026-09-12 (Nicko): 8
      templates (hunt, escort, clear-site, defense, supply,
      curse-lift, relic-hunt, parish-work), expanded later.
48. QUESTS/FACIONS GDD PART 2 (2026-09-12, spec in NEW doc
    21-quests-factions-gdd-part2.md):
    - WOLF KIT REVISION (Nicko 2026-09-12: "the werewolf only needs
      4, just like the vampire and undead. Not super expansive"):
      REVISITED from the 36-menu ladder to a TRANSFORMATION KIT of
      exactly FOUR abilities (modeled on doc 17 corruption kits):
      Hunter's Sprint (travel form, you are the mount), Pounce
      (leap-and-pin), Terrifying Howl (fear/stagger radius), and
      Elder's Shape (near-human battle form, the capstone). Kit
      levels by its own use under doc 18, but the four abilities
      are FIXED. Hidden-Court-trust gating remains IO proposal for
      review.
    - SPINE OUTLINES (PROPOSED, hand-authored): allegiance chains
      (3-5 beats), the Gambit line (six escalating denials), the
      Third Altar path (five beats, Signer's Confession crossover),
      the Debt Discovery arc (five beats ending at the bankruptcy
      the player uncovers), wolf post-transform content, the
      Signer's Unsigning chain (IO proposal parked: it costs the
      player the Signer), the demon invasion event chain
      (portents/breach/choice/aftermath).
    - PROGRESSION-SAFETY ADDENDUM: spine chains unlock by threshold;
      spine is the only content that may hard-gate endgame power
      (apexes, Lich King chain); every spine chain has a failure
      state that continues the game (failed court lines close that
      court's unique rewards, never the game; failed wolf trials
      retried after a season).
49. QUESTS/FACIONS GDD PART 3: TRANSFORMATION LINES + PRE-FALL RACES
    (2026-09-12, spec in NEW doc 22-quests-factions-gdd-part3.md):
    - HUMAN CENTER PRINCIPLE (Nicko): creation stays human; ONE human
      can become every strain across a playthrough. One strain at a
      time; switching requires resolving the old via a death-shaped
      exit. Vampire/undead entries deep-evil gated (doc 12/17); wolf
      neutral-keyed (doc 19); deep-good has no corruption entry (its
      transformation is the Sanctified apex).
    - THE VAMPIRE LINE, THE SUITOR'S SEASON (PROPOSED): six stages
      (The Noticing / The Suitor's Season / The Ledger of Gifts /
      The Embrace / The First Tithe / The Court's Welcome); texture:
      seduction and patronage, the house courts a champion before
      spending the Embrace; endings: willing turn / refused turn
      (ledger page leverage, grudge) / forced turn (rise as thrall,
      escapable per doc 19).
    - THE UNDEAD LINE, THE NECRO-ARRANGEMENT (PROPOSED): six stages
      (The Rot's Bargain / The Arrangements / The Dose / The Death /
      The Rising / The First Deed); texture: formal, contractual,
      bureaucratic; the player files their own WILL (death-drop
      heir), GRAVE (site choice), GRAVE-GOODS (you rise with what
      you are buried with, doc 06 made personal), and drafts their
      own death-title (doc 14). Death penalty still applies (locked:
      undeath changes the body, not the souls rules), recoverable at
      the corpse you rose from.
    - TRANSFORMATION SWITCHING (PROPOSED, awaiting Nicko ruling):
      exits route through death-shaped events (Mercy cure for
      vampires, laying-to-rest for undead, Court unbinding or
      silver for wolves); only the Church of Mercy can move a
      player backward to human, making Mercy the switchboard of the
      transformation web (IO proposal).
    - THE GREAT CITIES + SIEGE TRIGGERS (LOCKED, Nicko): orc origin
      REVISED (supersedes the legion-breed proposal): pre-Fall main
      conflict was the realm of men/elves/dwarfs vs the ORC SCOURGE;
      orcs were nearly mindless brutes, an EARLY CREATION OF THE
      DEVIL HIMSELF to conquer the mortal world. Post-Fall they
      sided with the dark court, now ruled under the elf-vampire
      court, and have become MORE SOPHISTICATED (their own towns,
      trade, cities). FOUR GREAT CITIES: dark minor = THE ORC CITY;
      dark capital = THE VEIL SPIRE (working name: the PREVIOUS
      SOLAR THRONE, old capital of the whole world, elf-vampire
      seat); light minor = THE UNDERGROUND DWARF CITY; light
      capital = THE NEW CAPITAL (human king and queen, built after
      the Sunder). SIEGE QUESTS (locked): a major spine quest per
      side is the SIEGE OF THE ENEMY'S MINOR CITY; its conquest
      TRIGGERS THE COMEBACK EVENT (doc 13) for the losing side,
      mid-late game: light takes the orc city = the dark court's
      debt default begins (demon invasion); dark takes the dwarf
      city = the light court's divine prayer event fires. The debt
      fuse stays the dark court's lore truth; the siege is the
      mechanical trigger for both courts.
    - THE WORLD BEFORE THE FALL (PROPOSED sketch, for discussion):
      Age of the Sun: death was final, no undead or vampires
      existed. Race origins: elves split into Veil lines (vampires)
      and dawn-refuser lines (light sylvan); humans as the mortal
      backbone (short lives = light court's urgency); dwarves
      PROPOSAL: masons who built the three altars' stones (why the
      Deep Altar still stands); orcs REVISED per Nicko ruling (see
      Great Cities above); undead did not exist before the Fall
      (the Split's dead stopped resting; necro-aristocracy = their
      institution); werewolf origin options (a: pact overspill, b:
      Deep Altar's wardens gone feral when the altar broke, c:
      older than everything; IO lean b, ties the wolf den to the
      Third Altar's threshold); covens PROPOSAL: the Old Faith
      predates the throne as the Veil Altar's first tenders; the
      pact perverted their altar; their oldest doctrine is anger at
      the pact (the Old Blood sect's root).
50. BIOME SAFETY BY ALIGNMENT (2026-09-12, world GDD session, spec in
    doc 03): per-biome CLOCK WEIGHT + HOME AFFINITY frame over doc
    12's clock and doc 13's conquest overlay. Blighted zones = the
    pact's scars, attrition biomes (passive Ward-drain/taint-creep
    for good/neutral players, locked), wolves immune (no-ledger
    strain); evil daylight-sleep grounds = blight + dark-flipped
    farmland only. Blighted zone count/placement opened as world GDD
    map item (tied to the ruins pass).
51. CONTINENT SCALE + TRAVERSAL (2026-09-12, world GDD session, spec in
    doc 03): playable footprint ~10 x 13 km (~130 km2), ~25 holds at
    ~5.2 km2 each, ~2.3 km average settlement gap. IN-GAME CLOCK: day
    and night are EVEN halves (Nicko: "night shouldnt be shorter than
    day"; exact 24:1 vs 48:1 ratio still open, GDD tuning). NO FAST
    TRAVEL AT ALL (Nicko): everything walked or ridden; supersedes
    Daggerfall-style fast travel everywhere; departure time is a
    survival decision; taverns + camping carry logistics.
52. WEATHER: THE VEIL-TIDE (2026-09-12, world GDD session, spec in
    doc 03): continental front system, weather carries the Veil's
    charge. Three charge states (SUN-CHARGED/VEIL-CHARGED/EVEN);
    bite locked to clock edges + patrol ranges + school power
    (+1-tier flavor only, no new resources); read-the-sky
    forecasting, no UI meter; wolves get storm-sense; named storms
    (Red Vigil / Pale Tide / Storm-Calls) locked as design intent,
    authored at GDD stage.
53. FOUR GREAT CITIES + THE THREE ALTARS: MAP PLACEMENT (2026-09-12,
    world GDD session, spec in doc 03): macro-geography = NORTH/SOUTH
    split (dark heartland north incl. the Veil Spire at the old
    capital, light realm south; locked FOR NOW, revisitable). Cities
    DEEP in home territory per Nicko (siege captures = mid-to-late
    game events): orc city deep north, dwarf city deep south under
    the eastern massif, New Capital at the wrist delta, Veil Spire
    north-center with blight radiating from it. ALL THREE ALTARS IN
    DARK-HELD GROUND (Nicko): Veil Altar ruin in the Spire's crypt,
    Sun Altar ruin deep in the northern moors, Deep Altar under the
    eastern massif behind the Hidden Court's den.
54. BLIGHTED ZONES: COUNT + DYNAMICS (2026-09-12, world GDD, spec in
    doc 03): THREE SCARS (Core ~10 km2 at the Veil Spire + Moor
    March + Darkwood-Eaves satellites, ~20 km2 total, each
    hand-authored with own identity/dungeon cluster). HYBRID
    dynamics: fixed ancient hearts, edges breathe with doc-13 war
    momentum, read on the map never a UI gauge. Cleansing: Red
    Vigil = temporary edge burns; the Moor March scar is THE
    CLEANSABLE SCAR via major light-court spine questline
    (mid-game, becomes light-held march land); other two scars
    permanent until total-domination ending.
55. NEUTRAL COURT ACROSS THE THRONES (2026-09-12, world GDD, spec in
    doc 03): THE SHADOW COURT (Nicko): outlawed in both realms,
    persists in secret alongside both (secret dens ~1 per hold);
    BOTH courts offer purge questlines against neutral holds and
    players can turn dens in, creating city battles on provocation
    (good vs neutral, bad vs neutral); double-sided work allowed
    except sabotaging the court last served (Ledger-tracked);
    underworld elders quietly prefer stalemate and sell intel to
    keep the war going (deep spine reveal, seeds the Third Path
    congregation); Wardens' neutrality inviolable (doc 19).
56. WITNESS-TIER NPC ROSTER (2026-09-12, world GDD, spec in doc 03):
    THE TIGHT NINE (Nicko): 8 named true witnesses + the Debt's
    Echo place-NPC + 2 texture anchors (War-Father Ghash,
    Half-Face). GRUDGE RULE REFINED (Nicko): grudges take hold
    only if the murder was WITNESSED. THE PURGE OF MEMORY (Nicko):
    both courts offer witness-assassination questlines (purge the
    old world from living memory); assassinations close personal
    quest keys permanently, feed purge standing, harden survivors.
57. PER-BIOME INGREDIENT CATEGORY LISTS (2026-09-12, world GDD,
    spec in doc 03): full member lists for doc 05's category
    secondaries authored per biome (commons + biome signatures:
    witchwood, blacksteel ore-scars, blightwood, hag-hide,
    storm-thistle, chapel-garden Holy herbs, etc.); reagent spawn
    density keys (Dark densest in blight, no Holy spawns there,
    Red Vigil opens a temporary Holy window); wolf players harvest
    blight without exposure (Hidden Court harvesters).
58. PROCEDURAL NOBILITY DEPTH (2026-09-12, world GDD, spec in doc
    03): NAME POOLS = stem assembly per race (vampire names decay
    by age tier, player names propagate via land grants/marriage);
    HERALDRY = charged-shields procedural grammar (court palettes,
    race charges incl. orc First Forge + broken suns, rank
    patterns; player banners same grammar); CLAN LIFECYCLE =
    six-state house (Rising/Established/Ascendant/Declining/
    Exiled/Extinct) moved by conquest, marriage, debt, land
    grants; regicide-with-heirs = extinction engine.
59. RACE ORIGINS: DEEP DETAIL (2026-09-12, world GDD, spec in doc
    03): doc 22's sketch LOCKED with map grounding (dwarven old
    quarries under the massif, Darkwood glades = the Old Faith's
    altar-gardens) + THE DEEP ALTAR'S DEDICATION (Nicko): built
    down-deep to the world's own deeps, never a throne
    instrument; re-kindling = returning the world to itself.
    Werewolf wild-strain dens pool at all three altar ruins'
    edges (broken wards).
60. NAMED STORMS AUTHORED (2026-09-12, world GDD, spec in doc 03):
    THE RED VIGIL (sun-storm: burns back a scar's edge for N days,
    suspends blight attrition in the band, Dark Pacts -1, required
    rite-crown for the Moor March cleanse), THE PALE TIDE
    (moon-fog: lifts blight drain entirely, max Veil charge, wakes
    wild strains, full-moon stacking = most dangerous night,
    Deep Altar approaches open widest), STORM-CALLS (dark siege-
    prep ritual: pins a Veil-charged front over an enemy hold,
    counterplay = anchor-caster sniping + Holy garrison rite).
    Each fires at most once per season; never coexisting. Cadence
    numbers = GDD tuning.
61. WORLD GDD TUNING PASS (2026-09-12, Nicko, spec in doc 03):
    IN-GAME CLOCK = 24:1 LOCKED (1 in-game day = 60 real min,
    even halves: day 30 real min, night 30 real min). VEIL-TIDE
    CADENCE: season = 21 in-game days, fronts change every
    2-4 days, Red Vigil 6 days / Pale Tide 5 days, once per
    season each. NODE DENSITY (doc 06): moderate, ~6-10 nodes
    per hold region per type, denser farmland/swamps, sparse
    blight. REAGENT COMBINING (doc 05): 3:1 per step; refining
    bonus yield stays refine/consumable only, never gear-craft
    extra-item rolls.
62. COOKING GDD: WARD-DISH GRAMMAR (2026-09-12, Nicko, spec in
    doc 10): biome signature dishes counter that biome's
    threats (attack dishes = monster parts keyed to doc 04
    enemy grammar; defense dishes = herb signatures vs ambient
    threats); ~43 dishes authored across the six biomes with
    per-biome enemy lists; RARE BONUS POOL locked (10 effects:
    corpse-recovery insurance, calm-night, second-meal grace,
    warm-blood, hunter's eye, salt-tongue, den-key, moon-haze,
    tithe-sate, ledger-page); TAVERN MEALS locked (cheap
    WELL-FED convenience tier); Veil-Tide fronts shift meal
    grade rolls.
63. POTIONS GDD: THE ALCHEMY STATION (2026-09-12, Nicko, spec in
    doc 05): NO ESTUS FLASK (Nicko): health/mana potions are
    crafted stock, carry-weight-limited, intensity scales by
    Alchemy skill tier x station tier; stamina potion cut (food/
    rest owns stamina). THE MORNING RITUAL (Nicko): one daily
    prep potion taken with the morning meal for the day's plan;
    offense = bane draughts from monster parts (doc 04 enemy
    grammar), defense = ward draughts from herb signatures
    (biome ambient threats); the daily trio = meal + potion +
    coatings. Bane grammar locked (mirrors doc 10 ward-dish).
    Four families: Healing+Mana stock / Daily Prep / Coatings+
    payloads / Throwables. Alchemy station ladder (5 tiers) +
    legendary station T5 brews (Undertow's Draft, Dawn-Draught).
    Open: T5 recipe discovery routes = quests GDD; numbers =
    tuning.
64. CRAFTING DEPTH: WORKBENCH + CAMP CUSTOMIZATION (2026-09-12,
    Nicko, spec in doc 05): THE WORKBENCH = sixth station, the
    REFINING HUB (supplies: leather/lumber/ingots/cloth/
    fittings/pigments+biome dyes/purified reagents; line-
    stations stop refining). ALL-CRAFTABLE PRINCIPLE: every
    item craftable except Hunter's Relics (doc 06) + spine-
    story items (doc 20). EIGHT DECORATION CATEGORIES (rugs/
    trophies/furniture/lighting/banners/shrines/defenses/
    structures); DECORATION PRESTIGE ladder (rest quality +
    morning buff hour, greeting scale, safe-zone deterrence,
    +1 grade roll on camp-brewed meals/potions at Masterwork
    decor, retinue affinity tolerance; resolves doc 11 Q8).
    TROPHY BUFFS (Nicko "I love this camp wide effect"):
    apex-beast trophies = small permanent camp-wide buff vs
    that beast family while displayed. HERALDRY on camp items =
    optional display (Nicko: "if chosen to").
65. EXPEDITION FOLLOWERS: OPEN QUESTIONS RESOLVED (2026-09-12,
    Nicko, spec in doc 23): slot thresholds LOCKED (1/2/3/4 at
    levels 1/10/20/30); BARD POOL AFFINITY-KEYED (good bards =
    protection buffs, evil bards = damage + elemental weapon
    coatings/ignition, neutral = travel kit; bards befriended
    and recruited from taverns and world locations; their
    affinity IS their kit); NO MEAL UPKEEP (hire + gear only);
    MOURNING PERIOD = 14 in-game days (band ceiling). Remaining
    opens: bard type list + song numbers (tuning), follower UI
    (art/tech), romance buffs (retinue GDD), XP share (tuning).
2. Human-centric character creation, class presets only.
3. Fixed region danger, no level scaling, no endgame tier gating.
4. Souls-style death penalty (XP/currency drop, recoverable at corpse).
5. Healing: crafted potions plus healing spells (mid-to-late game finds).
6. Save/respawn is tavern-based, themed as renting a room.
7. Inventory: weight-based, Daggerfall-style.
8. Stats: NINE total - Health, Stamina, Focus, Carry Weight, Precision,
   Ward, Speed, Luck (item drops/rng rolls), Wisdom (magic damage/mana).
   5 stat points per level.
9. ~28 core skill lines (9 combat, 5 magic, 5 crafting, 6 gathering, 3
   utility/social), expandable upward via unlockable specialties like
   Fry Cook. Luck is a stat (drop chance), Speechcraft is the social
   skill. Spec in 15-skill-lines.md.
33. Specialties with titles (2026-09-11): specialties are COMBINATION
    UNLOCKS - skill thresholds (2-3 lines) + optional affinity/court
    standing conditions - awarding TITLES with bonuses. Every specialty
    is a build identity; multiple stack. Nicko's example build: undead-
    aligned neutral GRAVEROBBER (Stealth+Lockpicking+Hunting, undead
    standing, robbed graves with the dead's own permission). 16-title
    first-pass catalog in 16-specialties.md, incl. The Pallbearer,
    Witchbane, Corpse-Smith, Black-Marketeer, and the automatic
    Six-Times-Refuser title for surviving the Allegiance Gambit.
36. Second-sweep resolutions (2026-09-11):
 - Third Path NG+ world state LOCKED: even, no court tilt, BUT both
   courts stronger than a first run (even amplification) - fair field,
   higher difficulty. Aligned endings keep the asymmetric tilt.
 - Specialty stacking: 2-4 max at endgame.
 - Content gates: mostly bonuses + APEX SPECIALTIES that gate exclusive
   questlines (Lich King chain for deep necromancy; apex chains to be
   designed for good/bad/neutral).
 - Warp camp summon cooldown: 4 in-game days.
 - Node respawn: 2-3 in-game days per resource node.
 - Fishing: full skill line (Stillwater/Deep-Line/Trophy Angler).
 - Specialty lapsability: LOCKED - lapsable (standing-conditioned titles
   lapse; historical/skill-only titles permanent); character menu must
   show retention conditions per title (condition transparency for
   planning specialty transitions).
 - APEX SPECIALTIES: new content-gate tier confirmed (Lich King chain =
   deep necromancy example); apex chains to design for good/bad/neutral.
37b. First-docs revision pass (2026-09-11, main session): docs 01-03
    revised to reflect everything learned since they were written. 01:
    new pitch paragraph (Two Thrones war, Third Path, moral axis as the
    spine; base building reclassified from non-goal to purpose-built warp
    camp scope). 02: locked art decisions folded in (512-1024px, 4-8
    frames, Souls UI, portrait dialogue, all-2D props), affinity-relative
    presentation section added, banner/heraldry tech flag added. 03:
    scale/holds decision folded in, faction roster section SUPERSEDED by
    the Three Courts + Two Thrones (mapping recorded, mechanics pointed
    at docs 12-13), day/night affinity-relative rule, mounts, tavern
    rumor economy, housing superseded; open questions list refreshed.
    (Numbered 37b to avoid colliding with the parallel magic session's
    37-39 entries.)
37c. Full consistency pass (2026-09-11, main session): docs 04-07 revised
    and docs 08-18 swept. 04: locked decisions consolidated (aiming,
    no-repair, mounts, parry-yes), skill-tier/technique layer added to
    combat, court-forces + corruption-kit enemies added, stale open
    questions resolved/closed. 05: crafting disciplines aligned with doc
    15 (5 lines + utility crafting), doc-18 tier/technique mechanics
    wired in, axis-gate on crafted magic, Aegis interaction, no-repair
    and warp-camp-station resolutions recorded. 06: node respawn (2-3
    days), grave-looting, fishing, and 2D-props locks folded in; item
    dimensions CLARIFIED (Rarity = drop frequency, Tier = skill gate,
    Enchants/Grades = function - three orthogonal axes); valet storage
    cross-referenced. 07: nine stats + 5 points/level, 28 lines,
    doc-18 mechanics summarized, NG+ spec linked, level-is-a-point-budget
    clarified, character creation tied to house naming. 08 tracker
    REWRITTEN as the master no-holes checklist: 20 resolved blocks +
    every remaining open item ASSIGNED to a future pass (combat/crafting/
    loot session, magic session, quests/factions GDD, world GDD,
    retinue/base GDD, cooking GDD, art/tech plan, tuning). Rule added:
    new open questions must be recorded with an assignment at the moment
    they surface. Foundation is consistent; no unassigned holes remain.
37. Magic acquisition model (2026-09-12, magic session): Option B locked
    with Nicko, verbatim: "you find and learn spells, and as you master
    them you can specialize them with advanced techniques." Spells are
    world knowledge (tomes, faction teachers, rare world-drops), each
    gated by the school's skill tier; doc-18 tier-up menus offer ADVANCED
    TECHNIQUES that specialize known spells (permanent, no respec).
38. Magic session resolutions (2026-09-12, all locked with Nicko, spec in
    17-magic-system.md):
    - School spell lists LOCKED, tier-mapped: Pyromancy 9, Cryomancy 9,
      Storm Magic 9, Holy Wards 10, Dark Pacts 11 (48 spells), plus 6
      cross-school hybrids and 2 corruption kits (4 each), ~62 total.
    - Hybrids FORMALIZED: 6 dedicated spells (Thermal Shock, Cryo-Storm,
      Sunfire, Storm-Light, Witherbolt, Grave-Storm), both schools Adept
      50+ to learn, world-learned, T5 power; Holy and Dark never
      hybridize with each other (the axis line holds).
    - Access: three elemental schools open to every affinity; Holy
      Wards/Dark Pacts STRICTLY axis-gated, no exceptions, tomes burn for
      neutrals too (doc 16's undead-patron Graverobber bonus is VOID).
    - Necromantic taint: 3-BAND system (Low 0-33 / Mid 34-66 / High
      67-100), ride it never scrub it; Purify cleanses only ANOTHER's
      taint, never your own.
    - Summon cap: 1-5 by school tier, +1/+2 at Mid/High taint for dark
      casters; corruption-kit converts share the pool.
    - Enemy casters: hybrid model, rank-and-file use transparent school
      lists (lootable tomes), bosses add 1-3 bespoke signature spells.
    - Corruption kits (Vampire: Blood Tithe, Veil of Mist, The Embrace,
      Domination Gaze; Undead: Grave Rot, Miasma of Decay, Wail of
      Despair, Corpse Bloom): faction patronage pool separate from Dark
      Pacts, deep-evil gated, level by their own use; kits encode the
      conversion fantasy (The Embrace, Grave Rot/Miasma fill ranks by
      converting the living).
    - AEGIS RULE: Aegis-blessed weapons prevent corruption conversion on
      kill; the light court's counterplay to the kits.
39. APEX TITLES ARE PERMANENT (2026-09-12, Nicko, verbatim): "once
    earned, apex titles are permanent, and cannot be changed. they are
    the pinnacle lock-in Apex of each affinity. they represent the
    culmination of commitment, and cannot be altered once achieved."
    Deliberate EXCEPTION to decision 36's lapsable rule: conditions gate
    EARNING an apex, the earned title never lapses. Magic apex triggers:
    THE LICH KING (dark: Dark Pacts Grandmaster + High taint), THE
    SANCTIFIED (light: Holy Wards Grandmaster + clean hands + deep-good,
    working name), THE PARAGON OF BALANCE (neutral: two elemental
    Grandmasters + survived the Allegiance Gambit, working name).
34. Magic system first pass (2026-09-11): five schools fully specified in
    17-magic-system.md - Pyromancy (damage), Cryomancy (control), Storm
    Magic (burst/crit), Holy Wards (axis-keyed deep-good: healing/wards/
    anti-undead), Dark Pacts (axis-keyed deep-evil: curses/hexes/
    necromancy + necromantic taint as a visible second resource with
    blessings and attention costs). Casting carries the dual-mode aim +
    stationary charge-up rules; Wisdom scales damage + mana. Acquisition:
    tomes, faction teachers, world-drop discovery; axis-gated tomes burn
    in the wrong hands. Spell lists reworked and LOCKED 2026-09-12 in the
    magic session (see decisions 37-39); first-pass tier/proposal note
    superseded.
35. Skill progression mechanics (2026-09-11, doc 18): two-layer model.
    Ranks 1-100 by use (passive primary-curve growth per rank); five
    tiers (Novice/Apprentice/Adept/Expert/Grandmaster at 25/50/75/100);
    tier-up = pick ONE technique from a 2-3 option menu (permanent, no
    respec). Gear gates read TIERS. Rank curve LOCKED: diminishing
    after 50 (2x slower by 75, 3x by 95) - Grandmaster earned, grinding
    blunted. No rank decay. Stat points (5/level) remain the only
    manual allocation; skills are earned, stats spent, techniques chosen.
10. Hand-shaped curated landmass; procedural interiors only (dungeons/
    crypts/cemeteries, persistent layouts).
11. Mounts: travel speed only, no mounted combat.
12. Hunting/Skinning is the sixth gathering skill (feeds cooking/crafting).
10. Partial survival / expedition loop (2026-09-11): two-tier rest system.
    Taverns = full service hub + only respawn point. Camps (bedroll/tent)
    = field saves, heal health/stamina, cure short ailments. Camping makes
    deep-wilderness exploration a preparation loop; carry weight becomes
    the expedition constraint.
11. Food is buff-only, never a survival tax; certain camp gear required to
    camp (2026-09-11).
12. Full cooking system (2026-09-11): one meal + one drink per day. Meals
    need 3+ ingredients, each buffing stats; synergistic combos get full
    effect + one bonus effect; salt amplifies potency. Ingredient choice
    encodes tomorrow's plan (combat stats for wilderness days, Luck/
    Charisma for town days). Cooking is its own skill line. Drinks = any
    non-health/magic/stamina potion, one daily (e.g. frost protection
    immunizes vs cold traps/attacks).
13. Cooking synergy rules (2026-09-11): synergies defined by flavor families
    + regional pairings. Family composition + region match yields named
    dishes (3 vegetables + regional pairing = ratatouille). A 4th compatible
    ingredient (flavor family + spice) upgrades the dish to a higher grade
    that does more than lower grades. Grade ladder per dish = completionist
    layer.
14. Cooking gating combo (2026-09-11): recipe knowledge gates the ABILITY
    to attempt a dish; Cooking skill gates success odds and buff magnitude.
15. Warp camp (2026-09-11): utility-magic camp class, early-midgame unlock,
    the mid-game opening moment. 3 tiers (Camp/Outpost/Hold). Warps in at
    any site meeting the open-space rule; becomes fully customized home
    base (structures, NPC merchants/cooks, defenses, decorations). Crafting
    drives building every piece. Warp camp kitchen = top-tier cooking
    station; Fry Cook specialty unlocks complex dishes. Player quarters
    include a retinue/harem fiction (saved or captured NPCs).
16. Retinue mechanics (2026-09-11): collected NPCs serve any mixture of
    staff roles (butler/slave; run to greet the player on camp summon),
    item handling, romance buffs, quest-specialist rewards (save the
    princess + kill the castle dragon = princess servant with a buff), and
    trade. Retinue variety IS part of the build playstyle, a progression
    axis like weapon skills or cooking.
17. Retinue valet + affinity (2026-09-11): the valet serves the summoned
    warp camp only (primary external storage lives there), never leaves
    camp, dies only to camp raids, and grants INSTANT access to all built
    storage chests on interaction (master-chest interface, no remote
    fetching). NPCs who like you stay and perform the camp greeting,
    ceremony scaled to relationship level. Affinity driven by the player's
    deeds: evil NPCs warm to evil acts, good NPCs to good ones. Below an
    affinity threshold, NPCs leave the camp freely; SLAVE type stays
    indefinitely until killed. Moral playstyle therefore shapes which
    retinue pool is stable.
18. Moral reputation axis (2026-09-11): single VISIBLE good<->evil axis on
    the character inventory screen; drives retinue affinity and faction
    reactions. Pose/emote unlocks per direction: powerful/dominating for
    evil, honorable/stoic for good. Special emotes unlock from quests and
    completed activities - emotes/poses are a standing reward category.
19. Summon cooldown (2026-09-11): warp camps summonable once every few
    days. Committing to a location is meaningful; the cooldown binds the
    player to a region and makes defending the camp in place a real
    commitment.
20. Camp threat model (2026-09-11): placement is a threat-profile choice.
    Near enemy bases/factions = attacked more often. Near friendly
    towns/cities = raids incredibly low, but thief intrusions instead.
    Caught thieves are brought to the player for judgment: kill (evil),
    turn in (good), enslave (neutral; option only visible with an unused
    neck chain in inventory), befriend (neutral; bluff risk, they may
    steal again and flee). Retinue NPCs hold slavery stances (against/
    favoring/neutral) that modulate affinity from the enslave choice.
    Dynamic interaction gating by inventory/progress/world state is a
    general design principle for all interaction menus.
21. Moral axis = faction gate (2026-09-11): the axis has WORLD WEIGHT and is
    the guiding mechanic for faction alliances. Neutral: can enter/trade
    with free cities of men, elves, dwarfs but cannot align. Good/noble:
    full alignment with noble factions (gear, standing, protection). Evil
    past a threshold: orc/undead/demonic/vampire factions stop attacking
    unless provoked; dialogue, quests, and alignment unlock with them for
    the same benefits. Details in 12-moral-axis-factions.md.
22. The Neutral Court (2026-09-11): confirmed third political family -
    mercenaries, smugglers, thieves, the underworld; a mix of all races,
    unaligned to any good or bad faction in the topworld political arena.
    Accepts any affinity; the political home of neutral players and the
    fallback web between courts. Faction mapping: Guild/Church = light,
    covens = dark, mercenaries/smugglers/thieves/underworld = neutral,
    crown TBD.
23. The Two Thrones (2026-09-11): crown/nobility exists on BOTH sides as
    the aristocratic spine of the light and dark courts. Light throne =
    human king and queen with mapped realm holds and good minor noble
    families. Dark throne = similarly powerful elf-vampire king and queen
    (ruler court) with their own holds and bad minor nobility. THIS IS THE
    MAIN STRUGGLE OF THE GAME: aiding either side to completely dominate
    the other, changing the world as each conquers the other (a
    territory-conquest meta where political boundaries move over the
    playthrough).
24. Territory conquest meta (2026-09-11): dynamic, trigger-driven, emergent.
    Every hold has vulnerability triggers (ruler killed - even
    accidentally, garrison decimation, legitimacy loss, siege events).
    Triggers fire whether the player knows them or not: deliberate quest
    completion and accidental king-kill produce the same conquest. The
    player discovers the system through exploration (rumors, refugees,
    map/banner changes). Details in 13-territory-conquest.md.
25. Reconquest + procedural nobility (2026-09-11): holds CAN flip back;
    the map is contested ground for the whole playthrough - a real,
    ongoing power struggle. Flipped holds can be granted to the leaders of
    the victorious conquest, making the nobility layer procedurally
    generated: different Sirs, names, and clans rise and fall with their
    political faction's fortunes. A living, breathing world that can be
    lived in; the player can rise from nobody to hold-holder to
    clan-founder (or watch their patron's house collapse).
26. Conquest chain of command + race-flavored houses (2026-09-11): clan
    lifecycles live ONLY in the conquest layer. Before each conquest the
    faction leader (king/queen) CHOOSES certain houses/families to lead
    it; when the battle is won or lost, the victor chosen by the king
    assumes control of the territory. The king's favor is a resource
    houses compete for. Procedural nobility is RACE-FLAVORED: each race
    (human, elf, elf-vampire, dwarf, orc, undead, vampire, demonic, neutral
    race-mix) has its own naming grammar, house/clan name style, title
    ladder, heraldry motifs, and tradition hooks. Details in
    14-races-houses-naming.md.
27. Marriage race-shift + player house + lore rights (2026-09-11): houses
    change race procedurally over generations via the marriage system
    (inter-race marriage drifts the line's identity). The player's founded
    house bears the player's character-creation first and last name. The
    player gains LORE-CHANGING RIGHTS as political standing rises, up to
    BANNER CREATION, unlocked on winning the FIRST conquest territory
    capture and being granted a hold (the moment the player designs their
    house banner and heraldry).
28. Batch resolutions (2026-09-11, open-question sweep):
    - World: hand-shaped curated landmass, procedural interiors only.
    - 20-30 holds, each a real place (noble family, tavern, dungeons).
    - Stats: nine total (added Luck, Wisdom); 5 points/level.
    - Mounts: travel only. Hunting/Skinning: sixth gathering skill.
    - Camping: tiered gear; overworld only; sleep = day restart; gear
      breakable in ambushes (sleeping tent safe); warp camp = default
      forward respawn once unlocked.
    - Cooking: 5 grades (Common/Fine/Remarkable/Exquisite/Masterwork);
      kitchen unlocks grading (campfire = 3 ingredients); no spoilage.
    - No item repair system; items permanent.
    - Night is dangerous (more undead, ambushes, night-only content).
    - Warp camp: relocatable after days-long cooldown; one-time hire
      cost (no upkeep); NO fast travel via camps; defenses actively
      fight in raids.
    - Combat: manual aim (reticle) for ranged/spells; lock-on for melee.
    - Conquest: triggers resolve off-screen; background slow-burn war
      tipped by player; regicide cascades only with no suitable heirs;
      alternate routes (defense destabilization, famine); comeback
      events (evil = mass demon summon, good = divine prayer event).
    - Art: high-res hand-drawn sprites 512-1024px, 4-8 frames/anim;
      Souls-style UI; portrait dialogue; all-2D props; grave-looting
      costs light-court reputation.
29. Day/night is affinity-relative (2026-09-11, revision): the dangerous
    half of the day depends on the player's alignment. Good players: night
    is for danger, day for towns/trade, sleep at night (risk: evil
    ambushes). Evil players: INVERTED - out at night, sleep by day, and
    DAYLIGHT sleep risks paladin/good-force attacks. Each affinity owns
    one half of the clock. REVISION: neutrality is NOT protected - the
    world forces a choice. True neutrals play the good-side day/night
    cycle by default; BOTH courts approach them demanding allegiance; the
    ONLY way to stay neutral is denying each side THREE times, after which
    BOTH courts attack. The Allegiance Gambit (doc 12): neutrality is the
    hardest path; the neutral court is its only home.
30. The Third Path / true ending (2026-09-11): after the six refusals a
    hidden quest path opens - unite the entire underworld into a THIRD
    FACTION and win the game by defeating BOTH courts, bringing absolute
    balance to the world. The hardest path in the game; its ending is
    regarded as the TRUE ENDING. NG+ from the true ending: keep your camp
    (warp camp + everything built), world resets to an even good/evil
    match with different procedural outcomes (new nobility, new war).
31. NG+ across all endings (2026-09-11): NG+ is available after ANY
    ending. All NG+ runs keep the camp (warp camp and everything built)
    while the world resets to an even good/evil match with fresh
    procedural outcomes. ONLY the neutral/Third Path NG+ lets the player
    choose their next playstyle (good, bad, or neutral); light/dark
    ending NG+ locks the next run to that court's side. Path freedom is
    the true ending's unique privilege.
32. NG+ world tilt (2026-09-11): in aligned-ending NG+ runs, the ENEMY
    court is much stronger and the player's aligned court slightly
    weaker; difficulty scales up with each NG+. The enemy faction
    captures holds easily through sheer power from early in the run -
    the world's favor tips toward the enemy naturally. Third Path NG+
    starts with the world truly even (no tilt): balance is what its
    ending bought (IO reading - confirm).

## Path to GDDs
Each planning doc is a raw idea capture. The promotion path is:
planning doc -> reviewed with Nicko -> formal GDD (one per major system) ->
feature-by-feature implementation against the GDD.
66. HARD-NUMBERS PASS RULINGS (2026-09-13, Nicko, spec in docs 31-35):
    seventeen live rulings locked in one session. (1) Roll i-frames =
    the docs 33/34 equip-load band version: fast 30f / 11 i-frames
    f12-f23 / 22 stamina, standard 37f / 6 i-frames f12-f18 / 26
    stamina, slow 48f / 3 i-frames f12-f15 / 32 stamina, roll disabled
    above 30.0 load; doc 32's roll section rewritten to match. (2)
    Damage numbers ON for player hits, OFF for incoming. (3) Focus bar
    hidden for non-casters. (4) Follower menu camp/tavern only at
    slice 1. (5) Inventory capacity = 100 + Carry Weight x 2.5. (6)
    Quest items in a zero-weight quest pocket. (7) Squire overflow
    scales with squire level, base +150 at level 1, per-level
    increment PROPOSED (+15/level tuning). (8) Dungeon-clear delta
    written only at the dungeon EXIT trigger. (9) Currency = Silver
    Marks, single neutral. (10) Camp construction is the primary
    late-game money sink, no new sink doc. (11) One corpse on the
    field, newest drop replaces the older permanently. (12) Death
    penalty = currency + 25 percent of current-level XP. (13) Two
    talisman slots: YES. (14) Armor model = flat ladder + percent cap
    as proposed. (15) Crit cap 30 percent. (16) Rot-Mother boss IN at
    slice 1 (M4 checkpoint may cut). (17) Bestiary scope confirmed:
    Bandit 180 / Rot Wolf 140 / Grave Ghoul 220 + Rot-Mother 900.
    RULING LOG: 08-open-questions.md section HARD-NUMBERS PASS
    RULINGS (2026-09-13).

67. UE 5.8 ENGINE LOCK (2026-09-13, Nicko, spec in doc 31): Unreal
    Engine 5.8 is the target version for the slice and beyond;
    resolves the UE-version open item in docs 00, 08, and
    30-remote-ue5-pipeline.md. Pipeline workflow, repo split
    (witch-hunter-ue, LFS), and folder layout per doc 31 section 2.

## New docs 30-35 (2026-09-13, hard-numbers pass)
- 30-prototype-gap-analysis.md - gap audit across docs 00-29: G1-G15
  blockers and needed-soon items, G16-G33 deferable items; prototype
  readiness verdict.
- 31-vertical-slice-scope.md - vertical slice scope and UE 5.8
  engine/pipeline plan (G1, G2): arena pocket, milestones M0-M6,
  GAS-vs-custom gate, perf budget, acceptance test.
- 32-controls-frame-data.md - controls, camera completion, player
  animation set (26 clips), combat frame data (G3, G4, G5, G10); roll
  bands locked by Nicko 2026-09-13.
- 33-equipment-and-formulas.md - mechanical equipment slots, weapon
  class table, damage/crit/poise/stamina formulas, equip-load bands
  (G6, G7); talisman, armor model, crit cap locked 2026-09-13.
- 34-enemy-ai-and-bestiary.md - enemy AI (perception, aggro/taunt,
  court grammar) and slice-1 bestiary with spawn tables (G8, G9);
  bestiary scope and Rot-Mother locked 2026-09-13.
- 35-slice-systems.md - HUD/UI, inventory mechanics, save and
  persistence, currency and economy, death and respawn edge rules
  (G11-G15); G11-G15 rulings locked 2026-09-13.

68. THE PALE QUEEN LOCK SESSION (2026-09-13, Nicko, spec in doc
    36): the light court's hidden spine. Locked rulings: the truth
    of the Fall (peasant girl spurned by the elf king, her failed
    working cursed him and his queen to vampiric immortality and
    split the continent); the dark court's vampire queen is the
    elven queen from the Fall, the two queens mirror each other;
    the "Devil"/Undersovran is the witch herself, there is no
    devil, she engineered the pact and collects the debt; she
    siphons the altars (the Sun altar is her tap, not a ruin); she
    controls the human king with dark magic; she has played both
    sides for centuries and can be the true final antagonist;
    working name THE PALE QUEEN; the Signer signed the pact
    unwittingly, her penance is for a framed crime; the
    grey-morality doctrine for all major players; three
    allegiance-keyed reveal storylines with the NEUTRAL line as
    the only path to the whole truth, and the neutral ending is
    the game's actual official real ending. New doc:
    36-pale-queen.md - the Pale Queen lore spine, grey-morality
    doctrine, three reveals, 7 open questions (dark queen's
    knowledge, comeback event, king rescue, Signer truth, mirror
    ending, harvest depth, peasant name).

69. PALE QUEEN RULING PASS (2026-09-13, second session, Nicko,
    rulings verbatim in doc 36 RULING PASS): all 7 doc 36 opens
    resolved. Headline rulings: the dark queen does not know,
    learns mid-ritual in the neutral ending, her reaction is a
    player-choice beat; comeback event THE LAST DANCE (one
    working of 400 years of harvested taint to un-sin the world);
    the king's compulsion is permanent, no rescue; THE SIGNER IS
    THE PALE QUEEN (THE PENITENT IS THE PEN: 400-year alteration-
    magic mask inside the Wardens, the penitent chancellor was
    invented, unmasking is the neutral ending's climax, the
    Wardens fragment is her trap; doc 19 carries a supersession
    note); the neutral ending leaves her mortal and powerless,
    the player chooses her sentence (THE HUNTER BECOMES THE
    LEDGER); harvest is a fixed narrative resource, no
    simulation meter; her peasant name is learnable on an
    unmarked grave (THE NAME IN THE GRAVE), and speaking it
    aloud in the finale breaks her composure. Six new opens
    tracked in doc 36 with assignments.

70. THE THREE VERSIONS COHERENCE PASS (2026-09-13, Nicko, spec
    in doc 36 THE THREE VERSIONS): the three affinity storylines
    written out as complete narratives. Light = THE SANCTIFIED
    WAR (learns the witch and the compulsion, never the
    creditor; ending is a victory that serves her). Dark = THE
    DEBTOR'S REVOLT (learns the lie, never the liar; the sigil
    wall at deepest standing; a revolt that misses). Neutral =
    THE TRUE ENDING (the only line assembling all three
    fragments; the unmasking is the big reveal and the neutral
    finale's climax: the witch is behind everything). NG+
    availability LOCKED: NG+ opens at the credits of any
    completed run; only the player (not the character) carries
    the reveal knowledge into NG+, fragments without the
    keystone.

71. POP-UP QUEST CONCEPT PASS (2026-09-13, Nicko, spec in doc 37):
    tavern rumor engine, bounty boards, the Quiet Parish cemetery
    mechanic, and a 24-archetype quest catalog (neutral, light, dark,
    cross-cutting) for the procedural tissue layer. Three rulings
    locked in session: (1) full concept doc now with slice scoping
    inside it; (2) DEAD-SPEECH GATE: no one can speak to the dead
    except an actual undead graverobber, a hidden mechanic for the
    specific class, the pinnacle example of hidden mechanics through
    class gates, more hidden specializations for other classes
    planned; (3) digging always costs light rep, consent only affects
    what the dead give you. New doc: 37-popup-quests.md. 7 open
    questions tracked in doc 37 and 08.

72. VENDETTA GRAVE + DEAD-TRUTH RULING (2026-09-13, Nicko, baked
    into doc 37): the dead CANNOT LIE, BUT CAN BE WRONG (resolves doc
    37 open question 4). New archetype THE VENDETTA GRAVE: some dead
    are bound to their killer; their unfinished business is an
    assassination quest on the person they are bound to. Target is a
    random procedural NPC or a person of importance, a noble without
    an heir; killing the heirless noble feeds doc 13's
    regicide-with-heirs rule and can set the hold's Sundering and
    capture into motion, the unintended consequence: a grave-side
    whisper can topple a hold. Catalog twin THE DEAD MAN'S JUSTICE
    added (archetype 25, doc 37 now 25 archetypes).

73. THE OVERHEARD WORD (2026-09-13, Nicko, baked into doc 37 Part
    3b): two rulings. (1) THE UNKNOWABLE WEIGHT: the vendetta cascade
    stays unknowable in advance, like real life, we all know not the
    gravity of our actions until it is too late; heirlessness is
    learnable only from tavern chatter and overheard conversation,
    never a UI surface. (2) THE PRIVATE-CONVERSATION RULE: NPCs with
    important things to say only say them when they think no one else
    is hearing besides the person they talk to; important
    conversations run an audience check; stealth becomes an
    information-gathering verb apart from theft. Gives doc 30's
    unowned G19 stealth gap its reward economy and keys off G17
    schedules.

74. INTEL TIERS + QUEST-SEED CATALOG (2026-09-13, Nicko, baked into
    doc 37 Part 3b): ruling 6, any fact that can result in a hold
    toppling or being captured is paranoid-speaker memory
    (private-conversation rule); THE EXCEPTION is heirlessness,
    common knowledge for common folk of a territory, overheard
    anywhere; treasure and monster locations are also GUARDED.
    Three-tier intel table locked: PUBLIC / GUARDED / DEAD-SPOKEN
    (tier follows consequence, not secrecy). 12-entry overheard
    quest-seed catalog added (working ideas): paid gate, rot in the
    granary, bastard in the woods, unpatrolled road, sealed mine,
    keeper's secret lane, coven meeting at the stone, night tithe,
    sick lady of the tower, Warden double ledger, goblin toll, cold
    widows of the pass.
