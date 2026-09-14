# 37 - Pop-Up Quests: Rumor Engine, Bounty Boards, the Quiet Parish

Drafted 2026-09-13, quest content pass. Built on docs 20 (two-tier
architecture, frame grammar, World Ledger, fails-forward), 21 (spine
outlines, frame library), 19 (lore spine, Long Agency, debt), 12
(courts, Shadow Court), 03 (world structure, taverns, cemeteries), 06
(grave-looting rep cost), 16 (specialties), 14 (procedural NPC pools).
Everything here is TISSUE-layer work: procedural systems writing into
the tissue only, per doc 20's locked rule.

## Session rulings (locked by Nicko, 2026-09-13, verbatim)

1. DOC SCOPE: full concept doc now, all four parts, slice scoping
   inside it. ("Full concept doc now (doc 37, all four parts, slice
   scoping inside it)")
2. DEAD-SPEECH GATE: no one can speak to the dead except an actual
   undead graverobber. A hidden mechanic for the specific class. More
   of these hidden specializations will be added for other classes.
   This is the pinnacle example of hidden mechanics through class
   gates. ("No one can speak to the dead except an actual undead
   graverobber. A hidden mechanic for the specific class.")
3. CONSENT RULE: digging always costs light rep; consent only affects
   what the dead give you. ("Digging always costs light rep, consent
   only affects what the dead give you")
4. THE UNKNOWABLE WEIGHT: the vendetta cascade stays unknowable in
   advance, just like real life: we all know not the gravity of our
   actions until it is too late. Heirlessness is learnable only
   through the Overheard Word (Part 3b), never a UI surface.
5. THE PRIVATE-CONVERSATION RULE: NPCs with important things to say
   only say them when they think no one else is hearing, besides the
   person they are talking to. Stealth becomes an
   information-gathering verb, not just theft. (Part 3b, the
   Overheard Word.)
6. INTEL TIERS (locked 2026-09-13, fourth pass): any fact or piece of
   information that can result in a hold toppling or being captured
   is PARANOID-SPEAKER memory: it is only spoken under the
   private-conversation rule. THE EXCEPTION: heirlessness is PUBLIC
   knowledge, common knowledge for the common folk of a territory,
   overheard anywhere in the territory. Treasure locations and
   monster locations are also GUARDED (paranoid-tier). The full tier
   table is in Part 3b.
7. MONSTERS HOLD GRUDGES AS FACTIONS (RULING 7, locked 2026-09-13,
   fifth pass): killing the toll goblin triggers the Warren chain
   (Part 3c); goblin kidnappers take the player ASLEEP, and capture
   REPLACES the death penalty for that ambush only (gear stripped
   into the hoard, recoverable, no currency or XP loss). The capture
   is a NON-DEATH DEFEAT STATE, the first in the game. The general
   rule (which monster societies hold grudges, which do not, what
   other courts get capture mechanics): open question 15.
8. THE PETTY LEGALIST (RULING 8, locked 2026-09-13): the Goblin
   King's personality is toll-law bureaucracy played straight: the
   trial itemizes the debt, the remedy is working it off, dark
   comedy. The Warren chain baked as archetype 26 (Part 3c) with
   all four endings (cleared ledger, escape, dead king, the
   volunteer).
9. LEGIBLE DOORS (sixth pass): descent gates are IN-WORLD, visible
   and physical at dungeon ends, labeled with tier number and
   lock-tier by Warden inspection. Diegetic, discoverable, no menu.
10. ONE DOOR PER DUNGEON, FOUR STRATA (Part 5): one descent gate
    per dungeon, four escalating layers keyed to level
    10/20/30/40, descended within the one opened gate.
11. THE CROSSING RULE HOLDS: escalated layers drop better RARITY
    within the region's fixed tier band (doc 06 crossing rule
    respected, tier band stays regional).
12. Part 5 bake scope: full section with details as working ideas,
    opens 19-23 logged.
13. FACTION KEYS (seventh pass, Nicko idea): buy a faction's key
    from its vendor, use it on a descent gate, and the layers CHANGE:
    different enemies, traps, and unique loot per affinity. One key
    per court family: Warden key (neutral, excavation), Guild seal
    (light, sanctified purge), Coven key (dark, coven nest),
    Smuggler's tally (neutral, economics only). Affinity gating per
    doc 12 vendor rules. Keys re-weight flavor and rarity within the
    regional band (ruling 11 still holds). Claim rule proposed:
    keyed layers persist as faction claims until a different key is
    used.
14. KEY TIERS (eighth pass, Nicko idea): each court family sells
    THREE key tiers at deepening affinity thresholds (friendly /
    honored / sworn, exact thresholds GDD tuning). Each tier
    escalates differently, not just harder: T1 baseline operations
    (excavation, purge, nest, cache), T2 faction projects (the
    Warden survey-hunt, the Militant crusade floor, the coven's
    ritual choir, the underworld auction house), T3 FACTION WARS
    INSIDE DUNGEONS: close-quarters battles between major factions,
    the player fighting for a side, looting the crossfire, playing
    double agent, or (neutral tier 3 only) taking the dungeon for
    themselves. Tier 3 availability seeded by the war state (doc
    13): the war leaks underground.
15. REPLAYABILITY RULES (ninth pass, Nicko locks): 15A THE
    CLEARED-WOUND RULE, what the player destroys stays destroyed
    (burnt rooms, cut bridges, boss corpses persist), and THE
    VACUUM RULE, cleared space does not stay empty: bandits,
    spiders, necromancers, wizards, squatters, refugees, scavengers
    move in to colonize the ruins the player made. 15B THE
    SITUATION SYSTEM, every dungeon carries one of six situations
    (OCCUPIED / INFESTED / ABANDONED-RECENTLY / CONTESTED /
    CONSECRATED-DESECRATED / COLLAPSING), re-rolled on long timers,
    readable from outside, reported by the rumor engine. Design
    contract: four layers, four clocks, the same dungeon is never
    the same dungeon. Six working ideas parked (ghost corpses,
    adapted denizens, dungeon economy, Veil-Tide interiors,
    expedition format, type specials).

## Part 1: The Rumor Engine (taverns speak of dungeons)

Every hold's tavern is the discovery engine for its dungeon cluster
(doc 03: every hold has a tavern, the save/respawn anchor and rumor
hub). Three rumor tiers:

- HEARSAY. Free, ambient tavern chatter. Vague, often wrong. Points at
  a dungeon, tells nothing reliable. Feeds curiosity, costs nothing.
- THE VETERAN'S ACCOUNT. Bought for a round of drinks or earned by a
  standing check. A procedural patron (doc 14 pools) recounts a real
  visit: what the entry looks like, what killed his friends, what the
  thing down there is. Accurate but incomplete.
- THE LEDGER PAGE. Expensive. Cartographers, smugglers, and the
  Wardens sell structured dungeon dossiers: known enemy type, hazard
  notes, partial map. INTEL TIER INTERFACE (locked with the tier
  table, 2026-09-13): paid sources SELL only PUBLIC facts and vague
  leads. GUARDED facts (precise treasure and monster locations) are
  never sold: they come only from private conversation (the
  private-conversation rule) or from the dead. A dossier says what
  kind of thing lairs in a dungeon and how it is entered; it does
  not say where the strongbox sits. The Wardens' pre-Split ruin
  keys (doc 19, locked) slot in as the endgame tier of rumor:
  dungeon keys to sites nobody alive has walked.

Mechanics, locked structure:

- RUMORS ARE REACTIONS: fed by the World Ledger (doc 20's rule). War
  near a hold, taverns gossip about it. A ghoul nest cleared nearby,
  the next rumor names a deeper site. A player who abandons contracts
  starts hearing the desperate-patron pool instead (doc 20
  fails-forward).
- RUMOR TRUTH TABLE: some rumors true, some stale, a few planted traps
  (covens, the Shadow Court). Verifying a rumor and returning alive
  improves the source's standing, feeding doc 20's promotion rule
  (procedural NPCs promoted to recurring named NPCs).
- SOURCE MEMORY: a promoted rumor source remembers what you verified.
  Their next rumor is better. Their grudge (if you abandoned their
  lead) is remembered too.
- FACT VERSIONING (assigned, open 37): dungeon facts carry version
  stamps tied to the site's situation epoch. When a named target's
  situation changes after a rumor or accepted contract, resolution
  is deterministic FAILS-FORWARD per objective type (migrate,
  expire, or convert), and a source is never grudge-punished for a
  war-caused change. Owner: doc 20 fact lifecycle + doc 35 G13.

## Part 2: The Bounty Board (monster contracts)

Contract surface at tavern notice boards, chapels, guild posts, and
dark-court requisition stones. Witcher-grammar contracts on the
tissue layer.

- CONTRACT TIERS: VERMIN (wolves, ghouls, a single haunt, low silver)
  / NAMED (a specific beast with a name and a body count) / HEADHUNT
  (people: outlaws, deserters, inquisitorial witch-bounties). Tier
  maps to dungeon depth and enemy tier.
- PROOF OF KILL: the bounty names the proof: a ghoul's jaw, the hag's
  charm-bundle, the wight's crown. Monster parts double as crafting
  reagents (doc 06), so proof is never trash: the sell-it-or-craft-it
  tension is built in.
- WHO POSTED IT CHANGES THE TEXTURE: a Guild bounty pays clean silver
  and feeds light standing. A village bounty pays in food, beds, and
  gratitude but little coin. A Militant requisition demands the taint
  burn. A coven's bounty asks you to leave something alive. Same
  monster, different resolutions: doc 20's frame grammar (2-3
  legitimate endings) applies to every contract.
- BOUNTIES ON THE PLAYER: doc 12's locked rule inverted. A deep-evil
  player finds their own name on light-court boards. An inquisitorial
  hunt you must survive or buy off. Written from the deed log.
- THE MISPRICED CONTRACT: a recurring tissue archetype. A bounty that
  pays too well. Sometimes a trap, sometimes a desperate patron,
  sometimes the "monster" is the victim. The world lies only when
  someone in it profits.
- BOARD LIFECYCLE (assigned, open 36): each board and contract gets
  a stable ID with a posted / accepted / resolved / expired
  lifecycle and ONE reward-authority record across every surface:
  the same hunt cannot pay twice at different boards, and resolved
  postings do not stay advertised. Owner: doc 20 contract
  lifecycle + doc 35 G13 persistence.
- PROOF RULES (assigned, open 38): proof provenance is tracked (a
  trophy harvested before accepting counts; one trophy satisfies
  one contract; proof is consumed on turn-in; spared and bargained
  outcomes name their own evidence). Crafting the only proof
  forfeits the contract. Owner: doc 20 objective attribution.

## Part 3: The Quiet Parish (the cemetery mechanic)

The new system this pass adds. Working name: the Quiet Parish. Built
on locked pieces: grave-looting rep cost (doc 06), the Graverobber
specialty (doc 16), cemetery keepers and revenant spawns (doc 03),
the Long Agency (doc 19).

### The loop

1. DIG. A shovel, time, and noise. Every dig risks waking the grave's
   resident (ghoul or revenant spawn weighted by cemetery age and
   region) and risks the cemetery keeper noticing. Keeper catch =
   standing loss with a mini-faction that also sells shovels, maps,
   and rite services: keepers are a resource to preserve, not just an
   enemy.
2. SPEAK. THE CLASS GATE (RULING 2, locked): no one can speak to the
   dead except an actual undead graverobber. To every other build the
   graveyard is loot, risk, and revenants. To the undead graverobber
   it is also a conversation. The dead open only to one of their own
   kind: a dead thing digging up dead things. This is the pinnacle
   example of HIDDEN SPECIALIZATIONS: mechanics invisible to every
   other class, discoverable only by playing the class deep. More
   hidden specializations for other classes are planned as a family
   (see Hidden Specialization Family below).
3. WHAT THE DEAD GIVE (consent affects this, not the rep cost; RULING
   3, locked):
   - DUNGEON LEADS. "They buried my ring with me, but my brother took
     the rest to the mill cave." The dead point at local dungeons for
     treasure. The tavern-rumor engine's dark twin: the living rumor
     loosely, the dead testify precisely.
   - KIN MESSAGES. Deliver a word to a living descendant in the same
     hold. Small quests with big texture. The family remembers (deed
     log, standing, a bed to sleep in).
   - UNFINISHED BUSINESS. The dead name what keeps them walking: the
     killer unpunished, the bones in the wrong soil, the spouse
     buried elsewhere, the sin unconfessed. Resolving it is the
     quest. Leave it, and that grave's revenant is on the night-spawn
     table later. Fails-forward (doc 20).
   - WITNESS TESTIMONY. Fall-era graves hold Long Agency witnesses
     (doc 19). A 400-year dead veteran of the Split is lore-gated
     content feeding the Wardens' contradictory-truths assembly.
     Deepest graves, oldest voices, highest risk.
   - THE VENDETTA GRAVE (new archetype, Nicko idea 2026-09-13): some
     dead are BOUND to their killer. They cannot lie, so when they
     name who killed them, the name is true. Their unfinished
     business is an assassination quest: kill the person they are
     bound to. The target is drawn like any other patron (doc 20
     pools): a random procedural NPC in the local area, OR a person
     of importance, a noble without an heir. THE CASCADE PREDICATE
     (locked reconciliation, 2026-09-13): the hold cascade fires
     ONLY when the bound dead targets the CURRENT RULER of a hold
     and no suitable heir exists (doc 13's exact
     regicide-with-heirs condition, invasion window included).
     Heirless minor nobles do NOT cascade: their deaths are tissue
     consequences only. All vendetta targets and cascade victims
     are filtered against SPINE IMMUNITY (doc 20: no procedural
     event may kill a spine NPC; audit B10 resolved, open 9
     closed). THE UNINTENDED CONSEQUENCE:
     the dead man's justice is a pebble the player drops into the
     war's machinery. A grave-side whisper can topple a hold. The
     player often cannot know in advance which graves hide a vendetta
     that scales that high: the dead ask for justice, the world
     decides what that justice costs. Resolution texture: the player
     can refuse the vendetta (the grave stays restless, the revenant
     keeps returning on night spawns), complete it quietly (the
     target dies, the deed log
     records an unknown-hand kill), or complete it loudly (witnesses,
     faction consequence, the noble's court remembers). All three are
     legitimate endings per the frame grammar; only the world's
     cascade is not optional.
   - THE MISDIRECTED VENDETTA (RULING 19, locked 2026-09-13): killer
     testimony CAN be wrong. Misdirected vendettas are a FEATURE.
     The comedy vendetta: the dead asks for revenge, the named
     killer is wrong (up to three times), and the quest turns
     comedic. Return to the corpse to collect and the dead is still
     there, still talking. By the second frustrated return the
     player is arguing with a corpse. Fallible testimony made
     playable.
   - THE UNKNOWABLE WEIGHT (RULING 4, locked 2026-09-13): the
     unknowable cascade is CONFIRMED as the design intent. The player
     does not and cannot reliably know the gravity of their actions
     in advance, just like real life: we all know not the gravity of
     our actions until it is too late. Heirlessness is learnable
     only through the Overheard Word system below, never from a
     UI panel, a bestiary-style entry, or a quest marker: the
     knowledge lives in the world's conversations or nowhere.
   - CONSENT TEXTURE. Digging always costs light rep (RULING 3).
     What changes with consent: the dead of an aided grave GIVE (testimony,
     treasure leads, kin words, sometimes grave-goods freely handed
     over as a gift). The dead of an unconsented looted grave give
     NOTHING: silence, or a revenant. Consent is the difference
     between a witness and a haunting. The dead of a robbed-and-
     abandoned grave remember the shovel.
4. ACCESS TEXTURE. Only the undead graverobber hears the dead at all
   (RULING 2). The Graverobber specialty's existing identity (doc 16:
   different rumors per specialty) is preserved and deepened: the
   specialty that already read graves differently now owns the only
   conversation the graveyard offers.

### The hidden specialization family (design intent, RULING 2)

The dead-speech gate is the PINNACLE EXAMPLE of a new content family:
HIDDEN SPECIALIZATIONS. Mechanics through class gates, invisible
until the class is played deep. Working idea, one per specialty, to
be designed incrementally (not part of this doc's scope beyond the
graverobber example):

- GRAVEROBBER (undead-aligned): speaks with the exhumed dead. THE
  PINNACLE EXAMPLE, fully specified in this doc.
- Family principle: a hidden mechanic should change how the CLASS
  reads a place everyone else visits (the graveyard, the tavern, the
  road), not just add stats. Discovery is diegetic: the mechanic
  reveals itself in play, not in a menu.

## Part 3b: The Overheard Word (conversations as a stealth-reward system)

New system from the 2026-09-13 second pass (Nicko idea). Two rules,
locked in session:

- HEIRLESSNESS AND OTHER WORLD FACTS ARE OVERHEARD. One way to know
  a hold's noble is heirless is tavern chatter or conversation heard
  out in the open. It can be as simple as being in the right place at
  the right time. Heirless nobles, succession anxiety, feuds,
  illegitimate children, debts: the facts that make the world's
  cascades readable are seeded into ambient conversation and tavern
  rumor, catchable by anyone who happens to be present. No interface
  surfaces them.
- THE PRIVATE-CONVERSATION RULE (RULING 5, locked): NPCs that have
  important things to say will only do so if they think no one else
  is hearing, besides the person they are talking to. Important
  conversations trigger an audience check: if the player (or a
  follower) is detectable to the speakers, the important line is
  withheld or the conversation defers (moves elsewhere, drops to
  small talk). This creates a real need to sneak undetected apart
  from theft: stealth becomes an INFORMATION-GATHERING verb. The
  player who wants the heirless-noble fact, the debt gossip, the
  coven's meeting time, or the keeper's secret must stand in the
  dark, behind a wall, up on the gallery, unseen.

Mechanics notes (PROPOSED, for GDD tuning):

- The Overheard Word is the stealth system's reward economy: doc 30's
  G19 gap (stealth specifications, unowned) now has a REASON to
  exist beyond thief intrusions (doc 11) and the Graverobber (doc
  16). Wire this section into the eventual stealth GDD as a
  requirement on the detection model: sight cones and noise radii
  are what decide whether the important line is spoken.
- LISTENING POSITIONS: the game reads the same detection model
  inversely: the player hidden from the speakers and in earshot
  collects the line. Darkness, crowd, elevation, and distance are
  the tools. A detected listener does not just miss the line: the
  speakers may stop, move, or remember the eavesdropper (deed log,
  a grudge from the paranoid). SCOPE CORRECTION (RULING 20, locked
  2026-09-13): audience checks, withheld lines, and follower
  liability apply to GUARDED facts only. PUBLIC facts (heirlessness,
  open feuds, road safety, war talk) ride ordinary chatter with no
  audience check and no risk.
- SCHEDULES MAKE IT POSSIBLE: private conversations key off doc 30's
  G17 open (NPC schedules/routines): a noble and his steward argue
  in the study at a certain hour, the miller's widow meets a
  smuggler by the river at dusk. Time-of-day knowledge becomes
  intel knowledge.
- FOLLOWER LIABILITY: a hidden player with a loud follower loses
  the line. The retinue is a stealth liability here (doc 23
  behavior intents), which makes solo listening a real build
  choice.
- TIE-IN: this is also how the Vendetta Grave's grave-side whisper
  can be pre-read. The heirless-noble fact is in the world's
  conversations: a player who never eavesdrops takes the kill
  unknowing (the unknowable weight, RULING 4); a player who
  eavesdrops for weeks holds a map of succession crises. Knowledge
  is earned, never given.
- DELIVERY (assigned, open 40): overheard lines are delivered as
  perception-gated subtitles and audio using the SAME earshot and
  audience predicate (no ungated captions, no auto-populated quest
  panel, no post-hoc readout of missed facts); replay of heard
  lines allowed, replay of unheard lines never. Owner: G16 audio
  + G17 dialogue + doc 35 G11 accessibility.
- AUDIENCE PREDICATE (assigned, open 33): a suspected-presence
  threshold DISTINCT from combat aggro decides whether GUARDED
  speech happens (speaker-belief owner, follower handling,
  bystander noise, walls and crowds, interruption and retry
  state). Owner: the G19 stealth specification using doc 34's
  perception primitives.
- RUMOR MVP (audit C3 resolved): the slice quest proof uses FIXED
  tavern patrons with event-triggered lines; G17 daily schedules
  are explicitly DEFERRED to the post-slice quest integration
  milestone.

### The intel tier table (RULING 6, locked 2026-09-13)

The Overheard Word has three tiers. The tier decides WHERE a fact can
be learned, and how dangerous learning it is:

- PUBLIC (common knowledge, overheard anywhere in the territory):
  heirlessness (THE EXCEPTION per Nicko: common folk know who has no
  heir), open feuds, famine scares, which hold is at war, which roads
  are unsafe, the shape of local resentment. PUBLIC facts ride
  ordinary ambient chatter and tavern rumor: no audience check, no
  risk.
- GUARDED (paranoid-speaker memory, private-conversation rule
  applies): any fact that can result in a HOLD TOPPLING or being
  CAPTURED (the ruling's own words): illegitimate heirs, forged
  wills, a steward skimming the garrison's pay, a captain who can be
  bought, where the granary's rot is hidden, which gate's guard is
  understrength, a cult under the chapel floor. ALSO GUARDED:
  TREASURE LOCATIONS and MONSTER LOCATIONS (Nicko, locked): where
  the merchant's real strongbox sits, the mine the family sealed,
  what lairs under the mill. GUARDED facts are spoken only when the
  speakers believe they are alone: stealth is the price of entry.
- DEAD-SPOKEN (the Quiet Parish's own tier): facts the dead hold that
  the living never say: the vendetta's true binding, the unconfessed
  sin, the grave's real name. Undead graverobber only (RULING 2).

Rule: TIER FOLLOWS CONSEQUENCE, not secrecy. A fact is GUARDED
because of what it can topple, not because someone whispered it. The
same fact can sit in different tiers by territory: heirlessness is
PUBLIC in its own hold and GUARDED in the rival hold that wants to
exploit it (their illegitimate-children talk happens in the dark).

### The overheard quest-seed catalog (working ideas, fourth pass)

Facts the player can overhear, by what quest they become. Working
names, nothing locked beyond the tier table above:

- THE PAID GATE. Two guards arguing: one is being paid to look away
  on a certain night. Overheard GUARDED: becomes a heist-ally
  opportunity (slip in on the pay-night), or a loyalty test to
  expose, or the player takes the smugglers' side of the deal
  themselves.
- THE ROT IN THE GRANARY. A steward and a factor whisper: the
  lord's grain is spoiled and the ledger hides it. GUARDED. Becomes
  THE SALT SCARE (catalog 13) from the inside: expose it, join the
  skim, or use the famine to break the hold's loyalty for a court.
- THE BASTARD IN THE WOODS. An old nurse and a priest: the lord
  fathered a child on a woodcutter's daughter; the child lives near
  the mill. GUARDED (succession fact, toppling-grade). Becomes an
  heir-hunting quest with three buyers: the lord (silence it), a
  rival house (crown it), the child's mother (protect it). Every
  buyer changes a hold's fate; the player picks the border's next
  owner without ever reading a war map.
- WHERE THE WATCH DOES NOT RIDE. A poacher and a fence: the moor
  road is unpatrolled between two stones after the bell. PUBLIC
  (roads are common talk) but the REASON it is unpatrolled is
  GUARDED: the captain sold the route. Follow it far enough and the
  why becomes a quest: corrupt captain, wolf-bought patrol, or
  something worse walking the gap.
- THE MINE THE FAMILY SEALED. Two cousins at a funeral: grandfather
  sealed the mine after what the diggers found; the deed and the
  key are still in the hall. GUARDED (treasure tier). Becomes a
  delve with a mystery cap: what was sealed in, and is the family's
  fear still alive down there.
- THE KEEPER'S SECRET LANE. A sexton, drunk, to the verger: there is
  a second entrance to the crypt under the yew, and the keeper does
  not know the gravediggers use it. GUARDED (treasure tier).
  Becomes the back-door version of any cemetery quest: smuggling
  route, older graves, or the Quiet Parish meta-quest's missing
  coffin went in through the yew.
- THE MEETING AT THE STONE. A veiled woman and a farmhand,
  whispered: the coven meets at the split stone on the dark of the
  moon, and the farmhand's brother is one of them now. GUARDED
  (monster/cult tier). Becomes a coven infiltration, a rescue from
  conversion, or the player's own dark-court introduction (the
  Overheard Word is affinity-blind: it feeds evil players the same
  way).
- THE TITHE THAT LEAVES AT NIGHT. A carter and his wife: the
  manor's grain tithe does not go to the granary; it goes into the
  marsh by torchlight once a month. GUARDED. Becomes a shadow
  operation with three reads: the lord feeds something in the
  marsh, the steward is smuggling, or the marsh's drowned dead are
  being paid their due. All three reads are playable.
- THE SICK LADY OF THE TOWER. Two maids: the lady has not been seen
  since winter, the physician visits with a black bag, and the lord
  has doubled the tower guard. GUARDED (toppling-grade: a captive
  heir is a succession crisis). Becomes THE LOST CHILD's adult twin:
  the rescue quest where the captive might be ill, pregnant,
  imprisoned, or already something else.
- THE WARDEN'S DOUBLE LEDGER. Two Wardens, low voices, in the
  reliquary stacks: the authentication ledger has a second book, and
  some relics are signed twice. GUARDED (toppling-grade for the
  Wardens themselves). A rare dark-tier intel that touches doc 36's
  mask: players who dig into it brush the Pale Queen's machinery
  without ever being told so.
- THE GOBLIN TOLL. Smugglers, laughing: the bridge between the
  holds now charges a toll to the things that live under it, and
  business is good since nobody patrols. PUBLIC (roads) with a
  GUARDED underbelly (what the toll actually buys). Becomes a
  monster-bounty quest (Part 2, CONTRACT TIERS, VERMIN tier) or a
  smuggler alliance quest: kill the toll, or become the toll's new
  collector. Expands into Part 3c, THE WARREN UNDER THE BRIDGE.
- THE COLD WIDOWS OF THE PASS. Mountain guides, quietly: three
  widows of the pass walk at night and bury travelers who freeze.
  Respect them or do not, but never dig what they bury. GUARDED
  (monster tier). Becomes a grave-site delve, an undead mercy
  quest, or the discovery that the widows are feeding the pass's
  wight something worse than corpses.

Design rule for all seeds: the overheard FACT is cheap to learn
(being present, unseen); the QUEST is what the fact grows into. The
tier table decides who speaks; the frame grammar decides what
listening earns.

## Part 3c: The Warren Under the Bridge (archetype 26: the hidden chain)

Added 2026-09-13, fifth pass (Nicko idea). Builds directly on THE
GOBLIN TOLL seed above. The full hidden chain, baked from session
rulings 7 and 8.

### The trigger (RULING 7, locked): monsters hold grudges as factions

Killing the toll goblin writes a HIDDEN GRUDGE into the World Ledger:
the bridge warren is the first MONSTER FACTION WITH A GRIEVANCE, the
Vendetta Grave's mechanic turned around, a living monster society
instead of a dead man holding the grudge. The toll goblin was the
king's licensed collector, probably kin. Consequence: GOBLIN
KIDNAPPERS COME FOR YOU. They do not attack on the road and they do
not fight awake players: they take you ASLEEP (at camp, in the
tavern's stable, anywhere you sleep). Goblins are cowards by
reputation and pragmatists by culture:
they jump you at your worst hour. If they defeat you, you do not die:
you wake bound in a cave.

CAPTURE TRANSACTION (assigned, open 39): capture/escrow/release is
an ATOMIC save transaction (audit C15 resolved as a spec): gear
escrow persists with the capture state, a pre-existing corpse drop
is preserved untouched, and at least one no-tool release path is
provable per warren before faction capture generalizes. Owner:
doc 35 G13/G15 + doc 04 defeat transitions.

CAPTURE REPLACES THE DEATH PENALTY (RULING 7, locked): for this one
ambush only, the goblin capture REPLACES the normal death penalty
(doc 04: currency plus 25 percent XP). No currency drop, no XP loss:
the capture IS the penalty. What the goblins take is your GEAR:
stripped and stacked in the king's hoard, fully recoverable. Goblins
do not want you dead; they want you ANSWERABLE. This is a
NON-DEATH DEFEAT STATE, the first in the game, and a template for
faction captures generally (see the grudges-as-factions open
question).

### The trial: the Petty Legalist (RULING 8, locked)

The Goblin King's personality is THE PETTY LEGALIST (Nicko lock):
the warren runs on TOLL-LAW. The king is not outraged that you killed
a goblin; he is outraged that you killed a LICENSED OFFICER and
DEFRAUDED THE TOLL. The trial is a bureaucratic farce played
straight: he reads the toll schedule aloud, itemizes what you owe
(one collector, plus interest, plus court costs), and offers the
ancient remedy: THE DEBT CAN BE WORKED OFF. THE CHOICE: work for him
or die. Dark comedy, goblin bureaucracy as the mirror of doc 22's
necro-court paperwork, the same absurdity scaled down to a bridge.

### Working for the king: the goblin bullshit job menu

Each completed job pays down the debt in installments. The chain ends
when the ledger clears. Working jobs:

1. THE NEW COLLECTOR. Stand at the bridge with the king's badge and
   collect from travelers, humans included, until the debt is paid.
   The loop closes: you become the toll of Part 3b, THE GOBLIN
   TOLL, the quest target for the next mercenary who hears kill
   the toll. This job is a STATE of catalog archetype 26.
2. THE SNUFF-BOX WAR. A rival warren under the mill claims the
   bridge's territory. Steal their tribute-hoard or their
   champion's ears. Goblins hire outsiders because they will not
   fight their own kin cleanly.
3. THE DWARF CARAVAN. Shake down a contract clan's freight on the
   mountain road (doc 14: dwarves are contract clans). The king
   wants the clan's seal-stamp as a trophy either way.
4. THE FEAST OF THE DEBT. Hunt the marsh beast for the
   debt-forgiveness feast. Ties into THE TITHE THAT LEAVES AT
   NIGHT: if that seed is live in the region, the thing being fed
   in the marsh is now on the menu, and the player learns what the
   lord has been paying.
5. THE CROWN OF TIN. The king's crown is pawned to a smuggler
   fence. Steal it back. Robbing the underworld for goblins makes
   you a debtor in two worlds.
6. THE TONGUE-TAX. Bring the king something overheard (Overheard
   Word tie-in). Goblins pay for gossip like currency; the warren
   is the region's best intel bazaar because goblins hear
   everything that crosses the bridge.
7. THE PALE LADY'S GIFT. Escort the king's courting gift to a coven
   matron in the Darkwood. The gift is alive, or must be fed
   nightly, or is a child's tooth collection. The dark texture
   under the comedy.

Cleared-ledger reward: freed with a ceremony, a badge, and the
standing to collect the toll (the king's real goal: the warren wants
a living human officer on the bridge, someone the other courts will
not shoot on sight).

### The escape routes (choose death, or fight, or just leave)

The lair is an escape dungeon where the stealth system's pieces pay
off. Working routes:

- THE BONDS. Escape begins bound: pick the pins (doc 15's Feel for
  the Pins), gnaw through (time and Strength), or talk a goblin into
  untying you (Speech, or bribery with grave-goods trinkets: goblins
  love grave loot).
- THE LAIR IS A LISTENING LEVEL. The Overheard Word applies: goblin
  guards gossip constantly because nobody taught them better.
  Listening positions reveal trapped corridors, the gear-hoard's
  location, which guard is drunk, and the king's schedule. Treasure
  locations are GUARDED per the tier table, but goblins are the
  world's worst secret-keepers: the tier is easier and the noise
  discipline is brutal (goblins hear better than men).
- THE OTHER CAGES. The warren holds other captives: a merchant
  whose ransom is late, a Militant friar preaching at his jailers,
  a Warden archivist cataloguing goblin grave-goods, maybe a
  smuggler who recognizes you. Freeing them pays standing elsewhere
  (the friar is a Mercy deed; the merchant becomes a promoted
  recurring patron, doc 20's promotion rule).
- THE PIT GAMBLE. Goblin culture's one sacred thing: games. Wager
  your freedom and gear on the pit: bone dice, riddle-duel, or the
  warren champion. High variance, in character, and the king loves
  it because the house always wins. Unless it does not.
- THE FLOOD DOOR. The warren's one weakness, learnable only from
  overheard goblin grumbling: the river still reaches the old
  flood-gallery. Open it and the warren drowns: the chain resolves
  in chaos, everything in the hoard washes into the river shallows,
  lootable for days. The nuclear option: the toll is dead, the
  warren is dead, the bridge is free, and the smugglers' ledger
  notes who broke their profitable arrangement.

### The four endings (RULING 8 bake, all four locked in concept)

- THE CLEARED LEDGER (work the debt off): free with a badge; the
  toll line in the catalog flips to the collector is a human in
  goblin service; smugglers respect you, the light court does not.
- THE ESCAPE (flee with or without your gear): the warren hunts you
  for N days (blood-feud ambush events on that bridge's road); the
  toll post stays empty, the toll collapses, the smugglers profit.
- THE DEAD KING. Kill the king instead: the warren splinters into
  rival claimants (doc 13's procedural churn), the bridge becomes
  contested, and every goblin warren within a region's ride knows
  the face of the toll-killer. Crossing any bridge near that warren
  reads your face.
- THE VOLUNTEER (the ending you cannot take back). Take the badge
  voluntarily without ever being captured: a player who
  investigates the toll before killing it can find the king's court
  and apply for the collector's job. The whole chain, offered
  freely. Hidden content that respects the player who talks first
  and kills later.

### GRUDGES AS FACTIONS (proposed rule, open question 15)

This chain is the proof-of-concept for a general rule: MONSTERS HOLD
GRUDGES AS FACTIONS, the Vendetta Grave's mechanic extended from the
dead to the living. Not every monster, only the ones with a court:
the goblin warrens, the Cold Widows of the pass, the coven, the
marsh thing the tithe feeds. Disrespect a monster SOCIETY and it
remembers in kind: captures, ambushes, grudges with faction memory.
Beasts do not hold grudges. Peoples do.

## Part 4: The quest catalog, by court

Tissue archetypes, each a doc 20 frame-grammar application with 2-3
resolutions. Difficulty reads as dungeon depth, enemy tier, night-
lock, time pressure, moral weight. Working names. All are frame-
grammar applications (patron + need + site + resolution axes +
personal axes, doc 20): no new systems required beyond the rumor
engine and the Quiet Parish.

### NEUTRAL COURT (any affinity, underworld, Wardens)

1. THE DEAD MAN'S LEDGER. A corpse's testimony (dead-speech tie-in)
   names where a smuggler crew hid their take before the ghouls got
   them. Thieves' guild wants it, Wardens want the pre-Fall seals on
   the strongbox. Competing buyers, one dive.
2. GRAVE-LEASE SALVAGE. Warden-sanctioned recovery of grave goods
   from a collapsing crypt. Legal looting, paid by the artifact,
   authenticated on return. The Graverobber's respectable cousin.
3. THE SILENT FERRYMAN. Night escort of a neutral fence through wolf
   country. Pays well, no questions, both courts tolerate it, both
   courts might intercept it.
4. THE CARTOGRAPHER'S LAST MAP. A dead map-maker's notes (from his
   grave, or his widow) lead to an uncharted dungeon. The reward is
   the map itself: it stays useful.
5. PURGE THE DEN. Shadow Court double-sided work (doc 12 open 8):
   clear a rival den for the underworld, paid by people who
   officially do not exist.
6. THE HANGED MAN'S DEBT. The underworld pays to move an executed
   man's grave before his ghost rises at the gallows tree. Underworld
   superstition with a real mechanic behind it.
7. THE QUIET COMMISSION. The Wardens ask you to recover a specific
   pre-Fall piece from a site that also wants it. The light court
   learns you took it: graverobbing rep even though you worked for
   archivists. Warden politics have teeth.

### LIGHT COURT (Militant and Mercy flavors)

8. THE LOST CHILD. The well, the cave, the abandoned monastery.
   Resolutions: rescue alive (family standing, deed log), recover the
   body (colder pay, honest grief), or discover what took the child
   and follow it down (converts into a deeper dungeon crawl).
9. THE NIGHT HAUNTER. A ghost or wight terrorizes a village after
   dark. Destroy it, lay it to rest (find what it wants: its name,
   its bones, its killer), or bargain with it. The lay-to-rest path
   is the good player's answer to the dead who cannot speak to them.
10. THE MONASTERY MEAL. Abandoned monastery, ghouls in the refectory.
    Clear it for the parish. Deeper read: the monks did not die of
    plague. What they did is down there too, and the Church would pay
    to never hear of it.
11. THE ACCUSED. Mercy-side inverse bounty: get to the charged woman
    before the Militant pyre does. Hide her, prove innocence, or
    expose the real taint in the accuser. The parish flips on this
    one (doc 20's sect meter, literally).
12. THE BLEEDING FIELD. Blight creeping into farmland (doc 03).
    Militant wants the field burned, an alchemist wants a sample
    gathered from the thing underneath. Both paid. The field
    remembers.
13. THE SALT SCARE. Famine rumor, granary thefts, a village ready to
    hang the miller's son. Rats, thieves, or the tax collector: the
    truth is one of three, and two of the three want you to leave it
    buried.
14. RELIC RECOVERY. Guild contract: a named hunter's relic (doc 06)
    lost in a known dungeon. The Guild wants it back, the Wardens
    want to see it first, the family of the dead hunter wants it at
    any price.

### DARK COURT (Old Blood and Veil Faithful flavors)

15. THE UGLY REQUISITION. The debt-discovery arc's tissue echo (doc
    21): dark-court contracts that visibly cost too much, seeded by
    debt tension. The dark player learns the throne's arithmetic one
    job at a time.
16. THE BLOOD TITHE. Veil Faithful work: collect the covenant's due
    from a village that signed. Collect in full, take only the coin
    and take the village's hate, or tip off the victims and lose the
    court's favor. Dark standing has its own moral texture.
17. THE DESECRATION. The coven's claim on a chapel: carry the Veil's
    mark into a Militant hold's crypt. Night work, sun-clock danger,
    and the light court's bounty on you doubles if you are seen.
18. THE UNMAKING. Old Blood work: a house's pre-Fall banner locked in
    a light-vault or a ruin. Steal it back and the Old Blood elders
    remember you are the kind of dark player they are hunting for
    (doc 19: they court players resisting the Undertow).
19. THE PALE PILGRIM. A veiled figure asks night escort to a ruin.
    Never ask what it carries. Pay is absurd, and it is a dark-court
    courier test: refusal is remembered, betrayal is hunted.
20. GRAVE-GOODS RETRIEVAL. Necro-court paperwork made quest (doc 22's
    necro-aristocracy): a dead house's arrangement was botched and
    its grave-goods scattered. The house pays, politely, to have them
    returned. Rob the living for the dead.

### CROSS-CUTTING (any court, seeded by world state)

21. THE LEANING CROSS. The keeper's quiet ask: graves collapsing into
    something hollow under the cemetery. Opens the
    crypt-beneath-the-church dungeon class.
22. THE DROWNED BELL. A moor or river bell that rings at night,
    drawing wights. Silence it, ring it for your own purpose, or
    learn who drowned with it.
23. THE QUIET PARISH (meta-quest, shares the system's name). A
    cemetery whose dead all speak of the same missing coffin (undead
    graverobber only, RULING 2). The chain of testimony is the quest,
    and the answer is a dungeon.
24. REFUGEE ROADS (war-state spawn, doc 20's why-now). A hold flips
    and the neighboring tavern fills with refugees: escort contracts,
    camp-defense contracts, and a dark-court version where the
    "refugees" are inventory.
25. THE DEAD MAN'S JUSTICE (catalog twin of the Part 3 VENDETTA
    GRAVE). The full quest-shaped version: dig, hear the vendetta,
    find the bound target (procedural NPC or an heirless noble),
    deliver the killing. The kill's cascade through doc 13's
    regicide-with-heirs rule is the archetype's signature: the
    player's smallest employer is a corpse, and the corpse's contract
    can redraw a border. Can surface from any court's territory; the
    dead are not loyal to the living's factions.

26. THE WARREN UNDER THE BRIDGE (full quest-shaped version of the
    Part 3c hidden chain, see Part 3c for the complete specification).
    Trigger, capture, four endings, and the catalog's only
    multi-frame archetype (hunt + supply + escort + relic-hunt +
    clear-site per the 37-C audit matrix).

Count: 26 working archetypes on top of the 8 locked frame templates
(doc 21: hunt, escort, clear-site, defense, supply, curse-lift,
relic-hunt, parish-work). Every archetype is frame-grammar
expressible.

## Part 5: The Descent Gates (dungeon layers behind doors)

Added 2026-09-13, sixth pass (Nicko idea). How dungeons work at
different levels: every dungeon ends at a DOOR, and behind the door
is an escalated version of the same dungeon: more dangerous monsters,
different traps, better loot and mob drops. The gates let early
dungeons be explored again once the gate unlocks, by level or by
lockpicking skill.

### Session rulings (locked by Nicko, 2026-09-13, sixth pass)

9. LEGIBLE DOORS: descent gates are IN-WORLD, visible and physical at
   dungeon ends, labeled with their tier number and lock-tier by
   Warden inspection. Diegetic and discoverable. (No menu.)
10. ONE DOOR PER DUNGEON, FOUR STRATA: each dungeon has ONE descent
    gate; behind it are four escalating strata keyed to character
    level 10 / 20 / 30 / 40. The gate opens on the layer matching
    your level; the layers are reached by descending further within
    the same opened gate.
11. THE CROSSING RULE HOLDS (ruling 11, locked): escalated layers
    drop better RARITY within the region's fixed tier band (doc 06's
    crossing rule is respected: tier band stays regional, escalation
    improves rarity and named-item odds within the band).
12. BAKE SCOPE: full concept section in doc 37 (Part 5), details as
    working ideas, opens logged.

### The gate rule

Every procedural dungeon (doc 03: generated interiors, persistent
layouts) ends at a sealed DESCENT GATE: a visible, physical door in
the dungeon's end chamber. The gate is labeled by Warden inspection
(standing-neutral, any player can pay for or earn the read): its
tier number (10/20/30/40) and its lock-tier. Two keys open it:

- LEVEL KEY: character level meets or exceeds the gate's tier. The
  door reads your level (it is not a moral gate, it is a weight and
  craft gate: the door's makers did not trust the unproven with
  what they kept).
- LOCKPICK KEY: Lockpicking skill at the gate's lock-tier (doc 15's
  Feel for the Pins ladder). The sneaky bypass: a lockpick character
  descends early. The tradeoff is honest: you bypass the level gate
  but the layer's danger does not negotiate.

ACCESS SEMANTICS (locked reconciliation, 2026-09-13): ONE physical
door per dungeon. Opening the door (by level or by pick) opens it
PERMANENTLY. Behind the door, EACH stratum still checks its own
threshold when entered (level 10/20/30/40 or its lock tier):
reaching layer 2 does not expose layer 3. Faction keys change a
stratum's CONTENT, never its thresholds. Stratum encounter tables
are FIXED content per dungeon: level is an access check only, no
visitor-level scaling, no relocking (audit B9 resolved).

Gate tiers and their layers, one gate per dungeon, four strata:

- GATE I (level 10 / lock Novice-Adept): layer 2 of the dungeon.
  Harder variants of the base pool, first trap escalation, rarity
  bump within the band.
- GATE II (level 20 / lock Adept-Expert): layer 3. New enemy types
  enter the pool (doc 34's bestiary widens), different trap grammar
  (environmental, not just spike-and-pit), rare-material veins.
- GATE III (level 30 / lock Expert): layer 4. The layer's own
  guardian (a named elite, not the base boss remixed: a new
  encounter), named-item chance opens. NAMED vs RELIC (audit B3
  resolved): named-item odds refer to ordinary Named-band loot;
  Hunter's Relics (doc 06) remain hand-authored T5 story items
  and are NEVER procedural drops in strata or key overlays.
- GATE IV (level 40 / lock Grandmaster): layer 5, the deep. The
  dungeon's true content: the reason the place was built. Each
  dungeon TYPE has a different deep (see The Deep Table below).

Re-locking: a gate you opened stays open for the playthrough (doc
03's persistence rule). The door remembers being picked: a
Lockpicking-opened gate stays unlocked once picked, so the sneaky
path does not need repeating.

### The Deep Table (what waits at gate IV, by dungeon type)

SPINE EXCLUSION (audit B15 resolved): procedural deep layers NEVER
carry apex powers or mandatory-ending unlocks (doc 21's spine-only
endgame-power rule stands). Authored spine hooks may use deep sites
without making tissue completion a prerequisite.

Doc 06's dungeon-type keys become the deep-layer identity. Working
ideas for what each type's layer 5 holds:

- CRYPT/Cemetery deep: the founder's vault. The cemetery's oldest
  resident (Long Agency witness territory, doc 19): the coffin
  chains, the unconfessed sin, the grave-goods the family never
  dared sell. The Quiet Parish's deepest dead-speech content lives
  here.
- MINE: the vein that was sealed. Why the diggers stopped, what the
  ore was for, and the sealed gallery's resident (doc 22's
  orc-prehistory hooks: some mines seal warren doors, some seal
  worse).
- COVEN DEN: the true altar room. The den's surface level is the
  coven's work; the deep is the coven's faith. Dark Pacts tier
  content, Veil Faithful hooks (doc 19 sects).
- WAR CAMP: the command vault. The general's map table, the
  requisition chest, the siege plans. Court-territory overlay
  (doc 06 layer 4) reads darkest here: the deep vault knows who the
  war is really for.
- MONASTERY/CHAPEL: the reliquary under the reliquary. What the
  parish buried twice.
- WARREN (goblin): the king's hall is not the bottom. The toll
  schedule's fine print lists what the crown owes DOWN there.
- BLIGHTED DEEP (blighted zones only, late-game): the pact's
  scar tissue has architecture. The blight's inner dungeons (doc 03
  opportunity texture) are gate-IV-exclusive content.

### Faction keys (added seventh pass, Nicko idea, 2026-09-13)

Buy a faction's key from its vendor, use it on a descent gate, and
the gate's layers CHANGE: different enemies, different traps, unique
loot per affinity. A second way past the doors, and a way to make the
same dungeon three different operations.

- THE FACTION KEY TABLE (working idea, one key per court family):
  - THE WARDEN KEY (neutral, Reliquary Wardens vendor): the layer
    becomes a WARDEN EXCAVATION. Their dig crews, their survey
    stakes, their hazards (tame, meticulous, trapped by archivists
    not sadists). Loot: authenticated artifacts, pre-Fall relics,
    relic-signing services discounted by how deep you went. The
    Warden key is the standing-cheapest: the Wardens want sites
    opened, not looted.
  - THE GUILD SEAL (light, Guild/Church vendor): the layer becomes a
    SANCTIFIED PURGE SITE: blessed braziers, paladin escorts on the
    upper strata, the undead pool weighted up and the loot table
    weighted holy (consecrated silver, Aegis-adjacent components at
    the deep, holy reagents). The Church pays per purge, not per
    visit: light keys come with a requisition attached.
  - THE COVEN KEY (dark, coven or necro-court vendor): the layer
    becomes a COVEN NEST. The pool inverts: the living are the
    intruders, the dark creatures are tenants. Loot: Dark Pacts
    tomes, taint reagents, the coven's own ritual components. The
    coven key's fine print: the nest expects tithes on the way out.
  - THE SMUGGLER'S TALLY (neutral court, underworld vendor): no
    faction flavor, pure economics: the layer's loot converts to
    broker-managed caches (higher rarity variance, no court
    reagents, fence access on return). The neutral key does not
    change the enemies; it changes what the enemies are GUARDING.
- AFFINITY GATING (doc 12 vendor rules carry): keys are sold to
  axis-compatible buyers the way tomes are. A deep-evil player
  cannot buy the Guild Seal at the counter; a light player buys the
  Coven Key only through fences at a markup. Neutral players can
  buy Warden and Smuggler keys freely, the neutral court's
  advantage.
- WHAT THE KEY CHANGES: enemy pool re-weight, trap grammar
  re-themed, loot table overlay (doc 06's court-territory overlay
  applied to the strata), and the layer's fiction: whose operation
  the dungeon reads as. THE CROSSING RULE STILL HOLDS (ruling 11):
  keys shift flavor and rarity odds within the regional tier band;
  no key crosses the band.
- CLAIM RULE (locked reconciliation, 2026-09-13): a keyed layer
  keeps the faction's content until a DIFFERENT faction's key is
  used. CLAIM vs OCCUPATION are separate states: the CLAIM decides
  which faction's content runs the layers (changes only on a new
  key); OCCUPATION is who is physically inside now (changes on
  clears, tenant moves, battle outcomes). WARDEN BOUNDARY (audit
  B14 resolved): Warden keys are NON-SOVEREIGN excavation licenses:
  defensive presence only, no conquest ownership, no land grants,
  no hold-momentum writes (doc 19's non-conquering Wardens stand).
  Light/dark court keys are the conquest system's smallest unit
  (doc 13 texture): you are not taking a hold, you are taking a
  floor.

### Key tiers (added eighth pass, Nicko idea, 2026-09-13)

Each court family sells THREE key tiers, gated by deepening affinity
thresholds (doc 12's tier ladder, exact thresholds GDD tuning: tier
1 keys at friendly standing, tier 2 at honored tier, tier 3 at
sworn/deep). Each tier escalates DIFFERENTLY, not just harder: the
faction's operation inside the dungeon changes character.

NEUTRAL / WARDEN KEYS (Reliquary Wardens vendor):
- T1, THE EXCAVATION (friendly): the working dig site as baked in
  the seventh pass. Meticulous traps, authenticated loot.
- T2, THE SURVEY (honored): the Wardens are not excavating, they
  are HUNTING something in the layers (a misfiled pre-Fall
  artifact, a rogue signer's cache). The dungeon's inhabitants
  were moved aside: something else is down there now. Loot adds
  Warden-quest hooks and the standing ladder accelerates.
- T3, THE CONTESTED SITE (sworn): the Wardens' dig has been
  ATTACKED. The layers become a live three-way: Warden holdout
  positions, raiders (scavenger guilds, the Shadow Court, or
  graverobber crews, drawn from the region's powers), and the
  dungeon's own residents. Close quarters, all three sides hostile
  to each other, the player the fourth. Loot: whatever both
  factions came for, contested at the deep.

LIGHT / GUILD SEALS (Guild/Church vendor):
- T1, THE SANCTIFIED PURGE (friendly): the purge site as baked.
- T2, THE CRUSADE FLOOR (honored): a full Militant operation: the
  layers are a siege in miniature, the faction is TAKING the
  dungeon, and the player fights alongside paladin squads against
  the incumbent pool. Loot adds Militant requisition claims.
- T3, THE WAR BELOW (sworn): the light court and the dark court
  are fighting OVER the dungeon. The strata are the front line:
  paladin vanguards vs coven/necro warbands, corridors changing
  hands between visits, the player free to fight for a side, loot
  the crossfire, or play double agent (doc 12 proposal C's
  gameplay). Close-quarters faction battle: the tier-3 signature.

DARK / COVEN KEYS (coven or necro-court vendor):
- T1, THE COVEN NEST (friendly): the nest as baked, tithe fine
  print included.
- T2, THE CHOIR (honored): the coven's layers host a RITUAL
  IN PROGRESS: processions, altar chambers, the incubation of
  something (doc 19's sect hooks: Old Blood restoration work or
  Veil Faithful devotion, seeded by the player's own sect
  standing). Loot adds ritual components and one-time pact
  opportunities.
- T3, THE COURT BELOW (sworn): the necro-court and the coven are
  at war over the deep (doc 14's necro-aristocracy politics made
  playable): the layers are contested ground between undead
  houses and coven cells, the player fights for a side or sells
  intelligence to both. The dark court's civil war, diveable.

NEUTRAL / SMUGGLER TALLIES (underworld vendor):
- T1, THE CACHE (friendly): economics as baked.
- T2, THE AUCTION HOUSE (honored): the layers host the underworld's
  black auction: buyer encampments, auction lots in the vaults,
  bidding as gameplay. Everything is for sale, including intel
  the Overheard Word would charge for.
- T3, THE HOSTILE TAKEOVER (sworn): the underworld's syndicates
  are fighting over the site (thieves guild vs smuggler rings vs
  mercenary companies, the neutral court's own politics): the
  player backs a syndicate, arbitrages between them, or takes the
  floor for themselves. The neutral court's tier 3 is the only one
  where the player can end up owning the dungeon.

TIER RULES (working ideas): tier-2 keys require the tier-1 key's
content to have been cleared at least once under that faction (the
faction escalates its investment only after you have proven the
floor); tier-3 keys are FACTION EVENTS, purchasable but seeded by
the war state (doc 13): a tier-3 faction battle inside a dungeon is
the war leaking underground, so its availability tracks the Two
Thrones' momentum. The crossing rule holds at every tier: band
respected, rarity odds deepen.

### The Cleared-Wound Rule and the Situation system (added ninth
pass, 2026-09-13, Nicko locks for replayability)

The goal: dungeons stay FRESH again and again. The same place takes
longer and gets more dangerous with each revisit, but under a
DIFFERENT context each time, and the player learns to read the
escalation pattern. Two locked rules deliver this:

15A. THE CLEARED-WOUND RULE (locked): what the player destroys stays
destroyed. The barracks you burned is still a burnt room three dives
later, the bridge you cut is still down, the boss's corpse is still
there. Persistence (doc 03) makes the player's history visible in
the geometry. THE VACUUM RULE (locked with it): cleared space does
not stay empty. Other things MOVE IN to fill the vacuum the player
created: bandits, spiders, necromancers, wizards, squatters,
refugees, scavengers, whatever the region can produce. Fresh context
is what colonizes the ruins you made. The dungeon does not respawn
its old self; it grows a new tenant on your wound.

15B. THE SITUATION SYSTEM (locked): every dungeon carries one of six
SITUATIONS, re-rolled on long timers and readable from outside (the
rumor engine, Part 1, reports situation changes; the entrance shows
it: cart tracks, war banners, quarantine sigils):
- OCCUPIED (default): who holds it now.
- INFESTED: something bred up in the deep (vermin, spiders, worse).
- ABANDONED-RECENTLY: loot-rich, with the tension of WHY it was
  left.
- CONTESTED: two powers inside, the tier-3 key state. AUTHORITY
  RULE (audit B8 resolved): situation rerolls run only through the
  World Ledger (doc 20's authoritative state, doc 13 war state);
  a CONTESTED roll happens only when the war makes it credible,
  and the situation is an outside SIGNAL: entering a tier-3 faction
  battle still requires the sworn key. No roll or purchase flips
  hold ownership.
- CONSECRATED / DESECRATED: court work was done here (light or
  dark), leaving standing effects and faction interest.
- COLLAPSING: time-limited, dive before it closes for a season.
The situation decides what moves in after a clearing, which quests
attach, which keys make sense, and what the entrance reads as.
Situation changes are reported by the rumor engine and the Overheard
Word: the world knows a dungeon changed hands before the player
walks in.

Design contract: the situation system is the CONTEXT layer, the
descent gates are the DEPTH layer, the faction keys are the
FACTION layer, and the cleared-wound rule is the MEMORY layer.
Four clocks, never all ticking the same way twice: the same
dungeon is never the same dungeon.

IMPLEMENTATION CONTRACT (assigned, opens 34-35): situations are
overlays on stable dungeon/layer/room IDs, never topology erasure;
permanent wounds persist as a bounded sparse-delta record (per-room
flags, not arbitrary geometry) whose budget is specified in the
open-32 slice-systems pass (owner: doc 35 G13, audit C8 corrected);
situation overlays must pass a reachability check against committed
wounds so no quest actor is stranded. Faction-key state is ONE
versioned dungeon-state record per gate: key family and tier,
claim owner, situation epoch, loot state, and faction-clear
history (audit C10 resolved as an assigned spec).

PARKED WORKING IDEAS from the ninth-pass menu (not baked, for future
sessions):
- The ghosts of your last dive: previous corpses as permanent set
  pieces; the Graverobber can dead-speak their own old corpse.
- The adapted denizens: residents adapt to HOW you killed them
  (capped at 3-5 beats, learning not rubber-banding).
- The dungeon economy: claimed floors as player assets, toll
  rights, the exhausted-vein endgame (the dungeon that goes COLD).
- Veil-Tide interior calendar: sun-charged fronts dry flooded
  galleries, Veil-charged fronts raise dead pools, blizzards close
  mountain dungeons (doc 03 weather, interiors edition).
- The expedition format: forward camps for deep strata, squire
  resupply, corpse runs as heists.
- Dungeon-type specials: one signature mechanic per type (crypts
  re-bury, mines settle, dens redirect, camps entrench, warrens
  multiply).
- GHOST-CORPSE GUARD (audit B6 note): ghost corpses, if ever
  adopted, are NON-LOOT memory actors, never recovery corpses;
  doc 35 G15's one-corpse rule stands and player drops never gain
  grave-rep costs.

### What I would add (working ideas, for review)

- THE WARDEN SEAL as the label grammar: the Warden inspection read
  is also a Warden SERVICE (doc 19: they authenticate relics; they
  authenticate doors). A Warden-touched gate can also carry their
  warning: sealed by the Wardens, or sealed by someone who was NOT
  the Wardens. The second kind is a quest seed, not just a door.
- ESCALATION CHANGES THE ROOMS, NOT JUST THE NUMBERS: per doc 03's
  layout archetypes, each layer's generation seeds shift (new
  layout archetypes, hazard density up, water rising, the crypt's
  lower galleries flooded, the mine's timber rotted). The layer
  should feel like the same place with the lid taken off, not a
  reskin. Traps follow dungeon-type keys (doc 06): mines gas and
  collapse, crypts flood and lock behind you, dens ward and
  redirect.
- THE LAYER BOSS RULE: doc 35's rule (dungeon inhabitants respawn
  on rest, bosses do not) applies per LAYER: each strata keeps a
  resident boss that stays dead once killed. The deep's resident
  is the dungeon's real boss; the base layer's boss is its
  doorman. PRECEDENCE CORRECTION (RULING 18, locked 2026-09-13):
  inhabitants-respawn-on-rest is SUPERSEDED for doc 37 dungeons.
  Cleared inhabitants never return as themselves; recolonization
  comes only from the Vacuum Rule on long timers. Destruction
  commits at the dungeon EXIT trigger (doc 35's locked exit-only
  rule); before that commit, reload reverts wounds.
- SCAVENGER SPOILS: gates mean old cleared dungeons have content
  again, but the base layer should not become trivial trash: base
  layers keep their own respawn economy per RULING 18's
  correction (old tenants never return; vacuum tenants and
  recolonization are the only refresh), and the deep's
  pull is the rarity bump, not the base layer's leftovers.
- THE UNDOORABLE: a small set of descent gates that neither level
  nor Lockpicking opens (working name: the Unopenable). Keyed to
  spine progress, court standing, or a specific quest's key item
  (doc 20's threshold rule). Every dungeon cluster should have one
  door the player cannot open yet: the world should always be
  bigger than your keys.
- THE MISLABELED DOOR: rare tissue event: a Warden read that turns
  out wrong (the dead cannot lie but the living misread, doc 37's
  dead-truth rule applies to documents too). The door said 10. It
  was lying, or its label was moved. Feeds the rumor-trap grammar
  (open question 2).

### Open Questions (assigned per tracker rules)

19. Layer generation grammar: how strata reuse the base layout
    (doc 03 archetype seeding per layer, doc 30 G24 dungeon
    interior gap cross-check): world GDD pass.
20. Descent-gate density: which dungeon types carry gates, how many
    gates per dungeon cluster, whether named/special dungeons
    (doc 03 hand-authored) get gates or their own rules: world GDD
    pass.
21. The Unopenable door list: which keys (spine chains, court
    standing, quest items) open which Unopenables: doc 20/21 spine
    cross-check.
22. Warden door-inspection service standing cost and availability
    (any player or standing-gated): doc 19 Warden GDD pass.
23. Whether layer-5 deep bosses carry named-item guaranteed drops
    (doc 06 named-item economy cross-check): GDD tuning.

## Slice scoping (first-pass subset for the vertical slice)

The slice carries three systems, not all four parts:

- IN SLICE: (a) the Rumor Engine at HEARSAY + VETERAN'S ACCOUNT tier
  only (Ledger Page later); (b) the Bounty Board at VERMIN tier only
  (one contract type, one proof grammar); (c) the Quiet Parish's DIG
  loop only (grave-looting with keeper risk and disturbed-grave
  Grave Ghoul wake risk, the doc 34 locked spawn; the dead do not
  speak in the slice, per RULING 2 the class does not exist at slice
  scale; the separate revenant is deferred per RULING 17 until core
  mechanics are established).
- SCOPE LABEL (RULING 16, locked 2026-09-13): slice 1 is a COMBAT
  demo only (doc 31). This slice subset is a PROPOSED post-combat
  QUEST INTEGRATION SLICE for the UE5 buildout, not a slice-1 claim.
- OUT OF SLICE: dead-speech, the 26-archetype catalog (this slice
  uses 2-3 archetypes as proof of frame grammar: THE LOST CHILD and
  THE MONASTERY MEAL proposed, with a VERMIN wolf contract from
  Part 2), bounties on the player, the
  Ledger Page tier, kin messages, witness testimony, the Warren
  chain, descent gates, faction keys, key tiers, and situations.
- Slice proof target: the rumor-to-dungeon loop (hear in tavern, find
  the dungeon, delve, return, bounty paid, next rumor reacts) must
  close end to end with World Ledger writes.

## Open Questions (assigned per tracker rules)

1. Which hidden specializations beyond the graverobber enter the
   family first, and their mechanics (doc 16 follow-up, next
   specialties session).
2. Rumor-trap frequency and detection grammar (how often planted
   rumors appear, what telegraphs them): GDD tuning.
3. Bounty proof grammar details (trophy-specific vs generic part
   proofs, per enemy tier): GDD tuning.
4. Whether the dead can lie: RESOLVED 2026-09-13 (Nicko): THE DEAD
   CANNOT LIE, BUT CAN BE WRONG. Their testimony about their own life
   (their name, their killer, their treasure, their unfinished
   business) is always truthful but may be mistaken, and a bound dead
   can be compelled by whoever holds the binding (see THE VENDETTA
   GRAVE, Part 3).
5. Keeper mini-faction standing ladder and rite-service prices: GDD
   tuning.
6. Which 2-3 archetypes prove the frame grammar in the slice beyond
   THE LOST CHILD and THE NIGHT HAUNTER: slice scoping pass.
7. Quiet Parish keeper-catch consequences beyond standing loss (does
   the keeper remember across holds): world GDD pass.
8. Vendetta Grave spawn weights: what share of graves carry a
   vendetta, and the noble-without-heir draw rate (GDD tuning).
9. Whether the killer of a bound dead can be a spine NPC (spine
   immunity says NO for spine NPCs as targets; confirm the guard) :
   doc 20 progression-safety cross-check, IO to verify against doc 20
   SPINE IMMUNITY.
10. Overheard Word audience-check tuning: detection radius vs speech
    volume bands, line-withheld vs conversation-defers behavior
    weights (stealth GDD, G19 owner).
11. Which world facts are Overheard-Word seeded vs rumor-tier only
    (heirlessness confirmed in-world; feuds, debts, illegitimate
    children proposed): world GDD pass.
12. Paranoid-speaker behavior: which NPC dispositions remember an
    eavesdropper and at what severity (deed log entry, grudge,
    hostile): G17 dialogue GDD.
13. PUBLIC-vs-GUARDED boundary cases beyond heirlessness (which other
    facts are territory-common vs guarded, e.g. famine scares,
    coven memberships): world GDD pass, per-territory tier table.
14. Overheard-seed spawn density: how many seeds per hold, per
    schedule slot, and their respawn rules (G17 schedules GDD).
15. GRUDGES AS FACTIONS scope (Part 3c): which monster societies
    hold faction grudges and get capture mechanics (goblin warrens
    confirmed by RULING 7; the Cold Widows, the coven, the marsh
    thing proposed), which are beasts that do not; capture-ambush
    grammar per faction; whether faction captures share the one
    non-death defeat state: doc 34 bestiary + doc 04 cross-check,
    IO reconciliation pass.
16. Goblin warren map: how many warrens per region, which bridges
    have them, whether the toll seed can spawn in holds without a
    bridge territory (doc 03 world GDD pass).
17. The pit-gamble ruleset (bone dice, riddle-duel, champion fight,
    wager ladder, house edge): GDD tuning.
18. Goblin King procedural or fixed: one Petty Legalist king per
    warren with procedural name and toll-schedule, or fully
    procedural (doc 14 pools GDD pass).
33. The audience predicate for GUARDED speech (suspected-presence
    threshold vs combat aggro, speaker-belief owner, follower and
    bystander handling, interruption/retry): G19 stealth spec
    (audit C6 assigned).
34. Situation overlay contract: stable dungeon/layer/room IDs,
    overlay rules, reachability checks against committed wounds:
    doc 30 G24 dungeon-generation spec.
35. Versioned dungeon-state record schema (key family/tier, claim
    owner, situation epoch, loot state, faction-clear history) and
    atomic re-key transitions: doc 35 G13 + doc 30 G24.
27. Faction-key pricing and vendor availability per court family
    (doc 06 vendor economy + doc 12 axis-gating): GDD tuning.
28. Whether keyed layers stack with level strata (does a key used
    at gate II change only its strata or the whole descent): GDD.
29. Faction-claim consequences beyond the claim rule (rival faction
    reactions, World Ledger territory texture): doc 13 cross-check.
30. Situation re-roll timers and transition triggers (clears, war
    events, blight creep beyond timers): GDD tuning.
31. Vacuum-tenant draw tables per region and dungeon type (doc 14
    pools + doc 34 bestiary): world GDD pass.
32. Cleared-wound persistence budget (per-room destruction state
    the save blob carries): doc 35 G13 slice-systems pass.
36. Bounty board and contract lifecycle (stable IDs, posted/
    accepted/resolved/expired, single reward-authority record):
    doc 20 contract lifecycle + doc 35 G13.
37. Dungeon-fact version stamps and deterministic fails-forward
    resolution when a target's situation changes: doc 20 fact
    lifecycle + doc 35 G13.
38. Proof provenance, consumption, and alternative-outcome evidence
    rules: doc 20 objective attribution + doc 06 item identity.
39. The capture transaction (atomic capture/escrow/release, prior
    corpse preservation, provable no-tool release path): doc 35
    G13/G15 + doc 04 defeat transitions.
40. Perception-gated subtitle/audio delivery for overheard lines
    (same earshot predicate, replay policy, accessibility): G16 +
    G17 + doc 35 G11.
## RULING PASS (2026-09-13, third session: audit reconciliation)

Nicko ruled on the audit findings (docs 37-A/37-B/37-C) and locked the
following. Rulings verbatim, then IO reconciliation entries applied
below.

R16. SLICE SCOPE (Nicko): slice 1 is meant to be just a demo of the
combat. Doc 31's combat-only boundary stands; do not worry about
everything else in it. The other PCG elements (quests, the World
Ledger loop, faction systems) are built out during UE5 development.
Resolution applied: doc 37's Slice scoping section relabeled as a
PROPOSED post-combat quest integration slice, not a slice-1 claim.
R17. REVENANT DEFERRAL (Nicko): the roster hole is a good catch, but
revenants and the other new enemy types are deliberately deferred
until other core mechanics are established. They WILL be built out.
Resolution applied: slice dig risk uses the locked disturbed-grave
Grave Ghoul spawn; a separate revenant is future roster work.
R18. RESPAWN PRECEDENCE (Nicko): the Cleared-Wound Rule ("the
dungeon never respawns its old self") is TRUE and current. Doc 35's
inhabitants-respawn-on-rest line is now WRONG and STALE for doc 37's
systems. DESTRUCTION COMMITS AT THE EXIT TRIGGER: that is the rule.
R19. MISDIRECTED VENDETTAS (Nicko): killer testimony CAN be wrong.
Misdirected vendettas are a FEATURE. New archetype: the comedy
vendetta. The dead asking for revenge can be wrong three times, and
the quest turns comedic: when the player returns to the corpse to
collect, the dead is still there, still talking. By the second
frustrated return the player is arguing with a corpse. Resolution
applied: vendetta killer identity marked fallible in Part 3, comedy
vendetta added as a working archetype.
R20. PUBLIC HEIRLESSNESS (Nicko): heirlessness is PUBLIC. Audience
checks apply to GUARDED facts only. Resolution applied to Part 3b
mechanics notes.

## IO RECONCILIATION PASS (2026-09-13, third session)

Editorial fixes applied per the audit docs (37-A, 37-B, 37-C). No
locked text rewritten; stale text marked superseded where required.

- A1/C2 resolved by R20: audience checks and follower liability are
  GUARDED-fact mechanics only. PUBLIC facts ride ordinary chatter.
- A2 resolved: the dusk bridge-crossing example removed from the
  capture trigger; captures occur while ASLEEP (camp, tavern stable,
  anywhere the player sleeps). No awake captures.
- A3 resolved by R19: vendetta killer identification is FALLIBLE
  testimony (can be wrong about who); the comedy vendetta is the
  designed use of that fallibility. Misdirection is a feature.
- A8/C9/B5 resolved by R18: inhabitants-respawn-on-rest marked
  SUPERSEDED for doc 37 dungeons; destruction commits at the exit
  trigger (doc 35's locked exit-only rule preserved); rest does NOT
  restore old tenants, recolonization runs on long timers only.
- B11/C4/C5 resolved by R17: slice dig uses the locked Grave Ghoul
  disturbed-grave spawn; Night Haunter deferred as a proof archetype
  in favor of THE MONASTERY MEAL (ghoul clear-site) and a VERMIN
  wolf contract from Part 2.
- A10/A12 fixed: catalog entry 26 added pointing to Part 3c; the
  slice count corrected to 26; toll seed references now cite Part
  3b by name; collector service identified as a state of archetype
  26.
- A11 fixed: the goblin toll bounty reference now cites Part 2,
  CONTRACT TIERS.
- A14 fixed: the vendetta refusal sentence completed.
- A4 (paid intel): the Veteran's Account, Ledger Page, and auction
  intel obey the intel tier table; paid sources may not sell
  GUARDED facts (treasure and monster locations) except as vague
  leads; precise guarded facts come only from private conversation
  or the dead. The AUCTION HOUSE sells PUBLIC and stale facts, and
  rumor-true leads, never GUARDED precision.
- A5 resolved: ONE physical door per dungeon; each stratum behind
  it carries its own level and lock threshold; opening the gate
  (level or pick) permanently opens the DOOR, but each stratum
  still checks its own level or lock when entered; faction keys
  change content, never thresholds.
- A6/B8 resolved: CONTESTED as a situation requires war-state
  authorization through the World Ledger (doc 20's authoritative
  state); situation rerolls never bypass key requirements or flip
  hold ownership; the situation is an outside signal, the key
  purchase is the permission.
- A7 resolved: CLAIM (which faction's content runs the layers) is
  separate from OCCUPATION (who is physically inside now). Clears
  change occupation; claims change only on a new key; battle
  outcomes in tier-3 write both.
- B2/B3 fixed: named-item odds refer to ordinary Named-band loot;
  Hunter's Relics (doc 06) remain hand-authored T5 story items and
  are NEVER procedural drops in strata or key overlays.
- B4 fixed: key access uses three separate predicates (axis
  compatibility, faction standing, allegiance); neutral vendors
  stay open to every affinity per doc 12; fenced Coven Key resale
  to light players is coven-knowledgeable smuggler markup, tracked
  by deed log.
- B6 fixed (parked idea note): ghost corpses, if ever adopted, are
  non-loot memory actors, never recovery corpses (doc 35 G15's
  one-corpse rule stands).
- B7 resolved: the Vendetta cascade fires only when the bound dead
  targets the CURRENT RULER of a hold and no suitable heir exists
  (doc 13's exact regicide-with-heirs condition, invasion window
  included); heirless minor nobles do NOT cascade.
- B10 resolved: spine immunity is the binding rule; bound-dead
  targets and all cascade victims are filtered against spine NPCs;
  open question 9 CLOSED (answered by doc 20's existing lock).
- B13/C12 resolved: the Warren chain, descent gates, faction keys,
  key tiers, and situations are explicitly POST-SLICE systems;
  goblin society gets its own bestiary and faction-behavior spec
  in a future doc 34 follow-up; doc 37's "no new systems" claim
  is replaced by an explicit dependency note (frame labels hold
  per the 37-C matrix; chain runners and objective verbs are
  G26 work).
- B14 resolved: Warden keys are NON-SOVEREIGN excavation licenses
  (defensive presence, no conquest ownership, no land grants, no
  hold-momentum writes), consistent with doc 19's non-conquering
  Wardens.
- B15 resolved: procedural deep layers NEVER carry apex or
  mandatory-ending unlocks (doc 21's spine-only endgame-power
  rule); authored spine hooks may use deep sites without making
  tissue completion a prerequisite.
- B9 fixed: stratum encounter tables are FIXED content per
  dungeon; level is an access check only; no visitor-level
  scaling, no relocking.
- C3 resolved: the slice quest proof uses FIXED tavern patrons with
  event-triggered lines; G17 daily schedules explicitly deferred.
- C6 assigned: the audience predicate (suspected-presence threshold
  distinct from combat aggro, speaker-belief owner, follower and
  bystander handling, interruption/retry state) is a G19 stealth
  specification requirement, tracked as open 33.
- C7/C10 assigned: stable dungeon/layer/room IDs, situation overlay
  contracts, bounded wound budgets, and the versioned dungeon-state
  record (key family/tier, claim, situation epoch, loot state) are
  G24/G13 prerequisites, tracked as opens 34-35.
- C8 fixed: open 32's persistence-budget assignment confirmed as
  the wound-budget home; doc 35 G13 (not G11) is the owner.
- C11 assigned: bounty boards get stable IDs, a posted/accepted/
  resolved/expired lifecycle, and a single reward-authority record;
  tracked as open 36 (doc 20 contract lifecycle owner).
- C13 assigned: site facts carry version stamps; accepted quests
  resolve fails-forward when their target's situation changes;
  tracked as open 37.
- C14 assigned: proof provenance (harvested-before-accept, one
  trophy one contract, consume-on-turn-in, alternative-outcome
  evidence) is doc 20 objective-attribution work, open 38.
- C15 assigned: the capture transaction (atomic capture/escrow/
  release, prior corpse preserved, no-tool release path proven) is
  a doc 35 G13/G15 + doc 04 transition spec, open 39.
- C16 assigned: overheard lines delivered as perception-gated
  subtitles and audio (same earshot predicate, no ungated captions,
  no auto-quest-panel); replay policy at G16, open 40.
- C17 fixed: doc 37's open list now carries the full 1-40 sequence;
  doc 31 G24 reference corrected to doc 30 G24.
