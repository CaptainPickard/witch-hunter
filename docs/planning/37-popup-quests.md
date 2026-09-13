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
  notes, partial map. The Wardens' pre-Split ruin keys (doc 19,
  locked) slot in as the endgame tier of rumor: dungeon keys to sites
  nobody alive has walked.

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
     of importance, a noble without an heir. Killing a noble with no
     heir feeds doc 13's regicide-with-heirs rule: an heirless
     succession triggers, the hold's Sundering and capture can be set
     into motion, and the war map moves. THE UNINTENDED CONSEQUENCE:
     the dead man's justice is a pebble the player drops into the
     war's machinery. A grave-side whisper can topple a hold. The
     player often cannot know in advance which graves hide a vendetta
     that scales that high: the dead ask for justice, the world
     decides what that justice costs. Resolution texture: the player
     can refuse the vendetta (the grave stays restless, the revenant
     returns), complete it quietly (the target dies, the deed log
     records an unknown-hand kill), or complete it loudly (witnesses,
     faction consequence, the noble's court remembers). All three are
     legitimate endings per the frame grammar; only the world's
     cascade is not optional.
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

Count: 25 working archetypes on top of the 8 locked frame templates
(doc 21: hunt, escort, clear-site, defense, supply, curse-lift,
relic-hunt, parish-work). Every archetype is frame-grammar
expressible.

## Slice scoping (first-pass subset for the vertical slice)

The slice carries three systems, not all four parts:

- IN SLICE: (a) the Rumor Engine at HEARSAY + VETERAN'S ACCOUNT tier
  only (Ledger Page later); (b) the Bounty Board at VERMIN tier only
  (one contract type, one proof grammar); (c) the Quiet Parish's DIG
  loop only (grave-looting with keeper risk and revenant wake risk;
  the dead do not speak in the slice, per RULING 2 the class does not
  exist at slice scale).
- OUT OF SLICE: dead-speech, the 24-archetype catalog (slice uses 2-3
  archetypes from the catalog as proof of frame grammar: THE LOST
  CHILD and THE NIGHT HAUNTER proposed), bounties on the player, the
  Ledger Page tier, kin messages, witness testimony.
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