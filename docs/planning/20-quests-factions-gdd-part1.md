# 20 - Quests and Factions GDD (Part 1: Spawning, Frames, Parish, Wolf)

Drafted 2026-09-12, combat/crafting/loot session continuation into the
quests/factions GDD. Built on docs 12, 13, 16, 19 and the Locked
rulings from this session.

## The Two-Tier Quest Architecture (locked with Nicko 2026-09-12)

All quests separate into two strata with different rules:
- THE SPINE (hand-authored, ~15-20 chains): alignment ceremonies, the
  apex chains (Lich King, Sanctified, Paragon of Balance), the
  Signer/wolf/Hidden Court line, the Third Altar path, the debt
  discovery arc, the comeback events. Spine quests use FIXED named
  NPCs (the two thrones, the Signer, sect founders, Hidden Court
  elders). These are the only NPCs that can never die to proc-gen
  chaos.
- THE TISSUE (procedural, ~90 percent of quest volume): generated at
  runtime from templates reacting to world and character state. Every
  tissue quest is disposable; the story never depends on any single
  one.

Rule: procedural systems may only ever write into the TISSUE layer.
The spine is load-bearing hand-work. This is what makes procedural
quests safe: nothing generated can break the story.

## The World Ledger (the simulation state quests read)

One authoritative simulation state the quest spawner queries; quest
logic of its own does not exist:
- War momentum and hold ownership (doc 13 conquest state).
- Each court's DEBT TENSION (doc 19: hidden until the discovery arc,
  Nicko ruling).
- Per-parish sect meters (below).
- Faction standings, axis position, active titles, retinue roster.
- The player's DEED LOG: structured record of kills, purges, sparings,
  cleansings, escorts, protections, betrayals.
- Unresolved consequences awaiting follow-up.

QUESTS ARE REACTIONS, NOT ROLLS. A quest spawning is always the answer
to a why-now: a hold flipped so refugee contracts appear in the
neighboring tavern; a parish tipped Militant so an inquisition
requisition posts; debt tension crossed a band so the dark court's
requisitions get uglier; the player's deed log shows three spared
witches so a Mercy parish offers protection work.

## The Quest Frame Grammar

Tissue quests are assembled from FRAMES: patron + need + site +
resolution axes + consequence tags + (NEW, locked) PERSONAL AXES.
- PATRON: cast from the hold's procedural NPC roster (doc 14 pools:
  the noble, the priest, the tavern-keeper, the cemetery warden, the
  guild agent; each with race, house, sect, disposition, one secret).
- SITE: pulled from the persistent dungeon pool and world locations.
- RESOLUTION AXES: the moral texture. Most frames carry 2-3 legitimate
  resolutions (kill it, cure it, pay it, expose it, enslave it).
- PERSONAL AXES (Nicko, locked 2026-09-12): the old-princess fantasy
  made systematic. Frames can carry a SECONDARY CHARACTER (the
  princess, the heir, the accused, the rival knight, the widow) whose
  fate is decided by HOW the primary resolution was achieved:
  - Save the princess by defeating the dragon in honorable combat and
    she may join the player's retinue WILLINGLY (retinue romance/
    harem fiction, doc 11).
  - Slay the dragon while it still holds her in terror and she will
    not come willingly; she can still be ENSLAVED (doc 11's slave
    retinue type, with the neck-chain inventory requirement and doc
    11's NPC slavery stances applied).
  - Kill the dragon, free her, escort her home: no retinue gain, but
    the house remembers the honor (standing + deed log).
  - The rule: willingness is gated by HOW you resolved the need, and
    both paths are viable for different builds. This is the
    multiple-endings texture for MOST tissue quests: 2-3+ endings per
    quest that differ in personal, retinue, standing, and material
    reward but do NOT necessarily shift world state. Fun and
    interesting play first, world consequences where earned.
- CONSEQUENCE TAGS: whichever ending the player takes writes tags
  back to the World Ledger (deed log, sect meters, standing, grudges,
  retinue availability), which changes what spawns next.
- Patron death mid-quest resolves as BETRAYAL (standing hit, grudge,
  frame expires into a consequence), never a stuck state.

## Expiry: Fails-Forward (locked with Nicko 2026-09-12)

Nicko ruling: tissue quests expire into consequences, never dead ends:
- Patron dies before resolution: the quest resolves as betrayal or
  inheritance (the patron's heir inherits the need, at a markup).
- Timer passes: escort targets become corpse scenes and standing
  losses; defense quests become occupied holds; rescue targets
  reappear later as harder versions (moved deeper, more guards,
  colder).
- The World Ledger remembers unresolved threads: a player who abandons
  a chain of them builds a reputation for it, which gates the
  trustworthy-patron quest tier and unlocks the desperate-patron pool
  (worse pay, darker jobs).

## Parish-Flip Rules (locked structure, weights at GDD tuning)

Each hold with a chapel carries one sect meter, MILITANT <-> MERCY,
spanning -100 to +100, seeded by region temperament. Doc 19's schism
sect mechanics made concrete:
- Deed categories feed it with weights (GDD tuning): purges,
  witch-hunt completions, taint-bearing kills push Militant; sparing
  resolutions, Purify services rendered to others (doc 17 economy),
  protecting the accused, tithes push Mercy.
- Crossing +/-50 flips the parish: the preacher NPC swaps sect, the
  quest pool swaps, dialogue tone changes.
- HYSTERESIS RULE: once flipped, crossing back past +/-25 flips it
  again (a buffer band, so villages do not yo-yo between services
  week to week).
- RIPPLE RULE: three or more parishes in a region tipping the same
  way converts the region's BISHOP, unlocking that sect's regional
  questline and shifting prices/standing.
- The sect meter is independent of the moral axis (a deep-evil player
  can feed the Militant as an attack dog; sect play is available to
  every affinity).

## The Wolf Trial (locked with Nicko 2026-09-12; doc 19's six stages)

1. THE SCENT: discovery through underworld haunts; a Warden must
   vouch for you (Warden standing gate).
2. THE LAW: brought before the Hidden Court; the wolf's law is
   spoken: hunt alone, speak of the den to no one, keep the human
   face by day, the hunt must be honest. Refusing here leaves
   cleanly; they wipe your knowledge of the den and standing holds.
3. THE FAST: N in-game days wearing the wolf-scent charm while living
   your normal life. Harm no innocents. The charm draws wild wolves
   to test you at night; the trial is restraint, not slaughter.
4. THE VIGIL: one night unarmed and alone in the deep wilds. Survive
   what comes. Kill only what attacks you.
5. THE BITE: the Court's elder bites you. Having passed the Fast, you
   receive the disciplined strain, not the curse.
6. THE FIRST HUNT: your first full-moon hunt under the Court's watch;
   the tutorial for the second form.

## THE WOLF KIT (RESOLVED 2026-09-12, Nicko: "the werewolf only
needs 4, just like the vampire and undead. Not super expansive.")
REVISION from any 36-menu ladder: the wolf form is a TRANSFORMATION
KIT of exactly FOUR abilities, modeled on doc 17's corruption kits
(Vampire: 4 spells; Undead: 4 spells). Full spec in doc 21:
1. HUNTER'S SPRINT - quadruped travel form; you are the mount.
2. POUNCE - leap-and-pin; pinned targets take bonus follow-up damage.
3. TERRIFYING HOWL - fear/stagger radius; lesser enemies flee or freeze.
4. THE ELDER'S SHAPE - the near-human battle form (capstone at kit
   maturity).
Kit levels by its own use under doc 18; the four abilities are
FIXED. Gating by Hidden Court trust (IO proposal, for review).

## THE WOLF LADDER (locked with Nicko 2026-09-12)

Nicko ruling: "I want a ladder of abilities that can be earned for
werewolf form, just like vampire and undead." The wolf form is a FULL
SECOND FORM with its own technique ladder under doc 18 mechanics:
- Ranks 1-100 by use of the wolf form (the wolf levels by hunting as
  a wolf, locked philosophy: use-based).
- Tiers at the standard five; tier-up menus of exactly 3 options
  (offensive/utility/specialist), permanent, no respec: identical
  grammar to every other line (36-menu rule applies to the wolf as
  the 10th combat-adjacent line; its menus to be drafted like doc
  04's, GDD work).
- GEAR-GATE EXCEPTION (IO proposal, for review): the wolf form
  carries no humanoid gear (fangs and claws are the weapons), so the
  wolf ladder is gated by the HIDDEN COURT'S TRUST instead of gear:
  Court standing gates the transformation's availability tiers (the
  wolf does not grow; your welcome deepens). Consistent with the
  game's everything-gates-by-trust philosophy.
- The WOLF LADDER (first pass, doc-18 style, one per tier shown):
  - Novice: Hunter's Sprint (fast quadruped travel, the wolf's mount
    analog within the no-mounted-combat rule).
  - Apprentice: Pounce (leap-and-pin, doc 04 beast grammar made
    player-side).
  - Adept: Terrifying Howl (fear/stagger-radius AoE).
  - Expert: Moon-Fed (heal from kills during the full moon).
  - Grandmaster: Elder's Shape (the near-human battle form: fight
    standing with claws, still a wolf).
- Axis tension (doc 19, still pending Nicko ruling): the hunt feeds
  the axis; cold-blooded full-moon kills drift evil, defense-of-the-
  underworld kills hold neutral.

## Debt Visibility (locked with Nicko 2026-09-12)

Debt tension stays HIDDEN until the discovery arc (doc 19). It is
never a visible meter. The player reads it only diegetically after
the arc opens: the Signer's ledgers, erased statues, preacher sermons
about lean winters, the increasing urgency of dark-court
requisitions. Before discovery it exists only as subtle world
texture (the GDD may plant one or two unknowing clues, see open
questions).

## Progression Safety Rules (locked structure)

- SPINE IMMUNITY: no procedural event can kill, displace, or de-spawn
  a spine NPC. Thrones, Signer, sect founders, Hidden Court elders
  are off-limits to conquest consequences.
- THE DEBT HAS ITS OWN FUSE: debt tension escalates from war state
  and elapsed time, never from any quest the player must complete.
  The comeback event (doc 13/19) always fires if the dark court
  loses enough ground, regardless of player quest participation. No
  soft-lock on the biggest world event.
- THRESHOLD TRIGGERS, NOT NPC TRIGGERS: the Gambit, sect unlocks, the
  wolf line, Third Altar access all key off standing/axis/title
  thresholds, so they surface wherever the player is, from whichever
  compatible surface (tavern, camp visit, envoy), never from one
  fragile questgiver in one fragile town.
- FACTION NPC PROMOTIONS: procedural cast NPCs who survive notable
  quests may be PROMOTED to recurring status (named, persistent,
  retinue candidates or rivals). The world grows familiar faces
  through play.

## Open Questions (assigned per tracker rules)

1. Debt payment schedule made concrete (visible collections): quests/
   factions GDD (post-discovery-arc).
2. Demon invasion scope (duration, spawns, territory effects, ending
   conditions): doc 13 conquest GDD.
3. Third Altar locations and re-kindling questline structure: quests
   GDD.
4. Witness-tier NPC list: world GDD.
5. The Signer's ace triggers (debt default only, Third Path crisis,
   player-earned): quests GDD.
6. Wolf technique menus in full (36-menu style for the ladder):
   doc 04/18 follow-up, next session's technique work.
7. Parish flip weights and hysteresis thresholds: GDD tuning.
8. Axis-tension rule for the wolf (doc 19, still pending): Nicko
   ruling.
9. Frame library size for first pass (how many tissue templates):
   quests GDD scoping.