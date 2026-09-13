# 17 - The Magic System

Drafted 2026-09-11, restructured 2026-09-12 with Nicko. The magic deep-dive:
five schools are named in doc 15 (Pyromancy, Cryomancy, Storm Magic, Holy
Wards, Dark Pacts); this doc gives them their spell structure, acquisition,
casting rules, and mastery rewards. Wisdom is the primary magic stat
(damage + mana pool, locked).

## Decisions Locked with Nicko

- SPELL ACQUISITION MODEL, Option B (locked with Nicko, 2026-09-12): "you
  find and learn spells, and as you master them you can specialize them
  with advanced techniques." Spells are KNOWLEDGE found in the world
  (tomes, faction teachers, world-drop discovery), each spell gated by the
  caster's skill tier (Novice/Apprentice/Adept/Expert/Grandmaster, doc 18).
  Tier-up menus (doc 18) offer ADVANCED TECHNIQUES: permanent choices that
  specialize how the spells you already know behave. The spell pool is
  collected from the world; techniques are the forks that make two casters
  of the same tier play differently. This resolves the doc-18 conflict:
  tomes/teachers are real acquisition, techniques are real identity.
- STRUCTURE (2026-09-12): every school's spell list below is TIER-MAPPED,
  each spell naming the tier that gates learning it. Lists are proposals
  for review unless marked locked.

## Casting Rules (carrying locked decisions)

- DUAL-MODE aiming: stationary (standing/crouched) = manual reticle aim;
  moving = lock-on cast (locked, doc 04/08).
- CHARGE-UP spells: cannot cast while moving, stationary commitment is
  the caster trade-off (locked).
- Resource: FOCUS/mana pool scales with Wisdom. Cast costs scale with
  spell tier.
- Skill-by-use: each school levels by casting it (use-based, locked).

## The Five Schools

Spell tier mapping: T1 = Novice (rank 1+), T2 = Apprentice (25+),
T3 = Adept (50+), T4 = Expert (75+), T5 = Grandmaster (100). Each spell
is found/learned per the acquisition rules below.

### PYROMANCY (elemental damage)

Identity: direct aggression. Fire bolts, burning ground zones, immolation.

LOCKED with Nicko (2026-09-12): spell list below confirmed as the working
Pyromancy lineup; Flame Cloak stays as a T3 spell (Nicko's ruling); Detonate
stays OUT of the spell list (Nicko's ruling). Advanced techniques listed
are IO proposals pending review.

- T1: Firebolt (fast, cheap single-target bolt; the spell that levels the
  school). Cinder Spray (short point-blank cone, hits crowds, pricier).
- T2: Flame Wave (fan burst, staggers light enemies and shoves them back;
  the get-off-me tool). Fire Zone (burning ground patch, DoT + area
  denial; locked design carried from 2026-09-11).
- T3: Ember Lance (short held charge, piercing line that carries burn
  through a file of enemies; the early stationary charge-up lesson).
  Flame Cloak (self-buff: fire resist up, melee attackers take burn;
  LOCKED as a spell 2026-09-12).
- T4: Immolate (full charge-up, stationary, massive single-target burn).
- T5: Meteor Call (charge-up, big AoE, long telegraph).
- Detonate: REJECTED by Nicko 2026-09-12, stays out of the spell list.

Proposed ADVANCED TECHNIQUES (IO, for review; tier-up menus per doc 18):
- Apprentice: Firebolt leaves a small burn patch on impact / one cast per
  fight is un-staggerable / 20 percent faster fire casts.
- Adept: Fire Zones tick 25 percent faster / Flame Wave knocks down
  instead of stagger / charge-ups can be held 50 percent longer.
- Expert: Fire Zone radius grows with rank / Immolate's burn spreads to
  enemies touching the victim / Flame Cloak reflects burn as damage.
- Grandmaster: zones stack damage instead of refreshing / casting while a
  zone burns under you grants cast speed / Meteor Call's telegraph pulls
  enemies in with a heat vortex (risk-reward positioning).

APEX HOOK (for open question 8): Grandmaster Pyromancy is the natural
trigger for a fire-court apex specialty chain (working name THE ASHEN
THRONE). Formal proposal comes with question 8.

Mastery identity: fire scales raw damage and zone control; Grandmaster
techniques push zone stacking, faster charges, cheaper spam.

### CRYOMANCY (control)

Identity: battlefield control. Chill buildup, freeze, terrain denial.

LOCKED with Nicko (2026-09-12): 9-spell list adopted as the working
Cryomancy lineup; Rime Armor stays as a T3 spell (Nicko's ruling).
Advanced techniques are IO proposals pending review.

- T1: Frostbolt (slow bolt, applies chill buildup on hit). Ice Shard
  (fast, cheap shard, minimal chill; the low-tier spammer).
- T2: Chill Ground (frost patch, slows enemies crossing it). Ice Lance
  (punctures chilled enemies for bonus damage; shatters frozen ones).
  Frost Wall (blocking terrain, melts over time).
- T3: Ice Prison (entomb a single target in ice; frozen solid until
  allies break them out or duration ends). Rime Armor (self-buff: melee
  attackers are chilled on hit, frost resist up; LOCKED as a spell
  2026-09-12).
- T4: Absolute Zero (charge-up AoE freeze, stationary; freezes everything
  in a radius).
- T5: Avalanche (charge-up; ice spikes erupt across a huge radius, frozen
  enemies caught in it shatter instantly). Winter's Crown (persistent
  Grandmaster aura: enemies near the caster accumulate chill passively
  while the caster fights).

Proposed ADVANCED TECHNIQUES (IO, for review):
- Apprentice: Frostbolt chill applies through block / Ice Shard refunds a
  sliver of Focus on hit / chill builds twice as fast in Chill Ground.
- Adept: Ice Prison holds two enemies within a meter / frozen enemies
  give a bonus backstab window (frozen = staggered for Stealth builds) /
  Frost Wall lasts longer and grants brief frost resist behind it.
- Expert: shattering a frozen enemy restores Focus / Absolute Zero radius
  grows with rank / Rime Armor chills attackers' movement speed.
- Grandmaster: every third freeze is instant / Winter's Crown leaves
  permanent cold trails where you walk / Avalanche frozen-shatter bonus
  doubles.

APEX HOOK (for open question 8): Grandmaster Cryomancy as a possible
neutral elemental apex trigger (working name THE GLACIER WARDEN);
formal options at question 8.

Mastery identity: chill-to-freeze chains get faster and cheaper to
trigger; frozen enemies shatter for bonus damage; ice structures persist
longer.

### STORM MAGIC (burst/crit)

Identity: burst damage and crit synergy; the crit school, pairs with
Precision. LOCKED with Nicko (2026-09-12): 9-spell list adopted as the
working Storm Magic lineup; Tempest Aura is MOBILE but rents its mobility
with Focus upkeep per second while active (Nicko's ruling). Advanced
techniques are IO proposals pending review.

- T1: Spark (cheap poke bolt, high crit flavor). Static Touch
  (melee-range zap, interrupts casters).
- T2: Chain Lightning (arcs between multiple targets). Storm Brand
  (mark a target, detonate later; the setup-payoff spell).
- T3: Ball Lightning (slow drifting orb that zaps anything it passes;
  zone control with mobility). Gale Step (self-buff: move speed and
  cast speed up; completes the school self-buff trio with Flame Cloak
  and Rime Armor).
- T4: Thunderfall (charge-up strike from above, huge single-spot burst).
- T5: Tempest Aura (a mobile storm field around the caster; the only
  moving high-tier spell; costs Focus upkeep per second while active,
  locked 2026-09-12). Eye of the Storm (while stationary, crits generate
  supercharge windows: next cast is instant).

Proposed ADVANCED TECHNIQUES (IO, for review):
- Apprentice: Spark crits arc a mini-chain to one nearby enemy / Static
  Touch stagger window doubles / 15 percent faster storm casts.
- Adept: Storm Brand marks spread to one extra enemy / Chain Lightning
  jumps +1 / Ball Lightning follows your movement on recast.
- Expert: Gale Step grants brief immunity frames on cast / Storm Brand
  detonation staggers / crits during Tempest Aura extend it 1 second.
- Grandmaster: supercharge windows also make the next cast free / Chain
  Lightning forks (each jump can split in two) / Thunderfall re-cast
  instantly at half power within seconds.

Mastery identity: chain jumps +1 per mastery tier; crit-fishing builds
get supercharge procs; the school rewards aggressive positioning.

### HOLY WARDS (light court; axis-keyed deep-good)

Identity: protection, healing, anti-undead, cleansing. Three lanes:
heal (Minor Mend, Group Mend), ward (Light Ward, Sanctuary), anti-undead
(Blessed Bolts, Consecrate, Radiance). Gated to deep-good attunement;
tomes burn in evil hands. LOCKED with Nicko (2026-09-12): 10-spell list
adopted as the working Holy Wards lineup, and the AEGIS RULE locked:
Aegis-blessed weapons prevent corruption conversion on kill (blessed
weapon kills of rotted or Embraced-doomed victims do not rise as undead
or vampires). The Aegis rule is the light court's counterplay against
the corruption kits. Advanced techniques are IO proposals pending review.

- T1: Minor Mend (healing; mid-game find per doc 04). Light Ward
  (personal shield, absorbs damage).
- T2: Blessed Bolts (radiant projectiles, bonus damage vs undead/evil).
  Consecrate (anti-undead zone: undead inside are weakened and burn).
- T3: Group Mend (heal allies in radius). Purify (cleanse ailments and
  curses; also burns away necromantic taint, taint interaction ruled at
  open question 4). Aegis of Dawn (bless a weapon: bonus vs undead and
  evil for a duration; triggers the locked Aegis rule).
- T4: Sanctuary (charge-up; massive ward dome, blocks enemy casts and
  projectiles inside).
- T5: Radiance (burst of holy light, massive undead/evil damage, blinds
  the living). Resurrection-lite (revive a fallen retinue NPC, once per
  long rest).

Proposed ADVANCED TECHNIQUES (IO, for review):
- Apprentice: Minor Mend casts faster when standing in Consecrate / Light
  Ward recharges out of combat / Blessed Bolts pierce one extra target.
- Adept: Consecrate's burn ticks heal the caster for a fraction / Group
  Mend also cleanses one ailment / Aegis of Dawn duration doubles.
- Expert: Sanctuary's dome deals holy damage to evil things that touch
  it / healing granted while at low Health is stronger / Consecrate
  suppresses undead summons (raised minions inside crumble faster).
- Grandmaster: lesser undead flee the caster's presence / Light Ward
  reflects a percent of absorbed damage / Resurrection-lite can also
  restore a slain WARhorse or retinue beast once per rest.

Mastery identity: wards reflect a percent of damage; at max mastery
lesser undead flee the caster's presence; healing scales with Wisdom.

### DARK PACTS (dark court; axis-keyed deep-evil)

Identity: curses, hexes, necromancy, and BARGAINS. The witch-hunter's
dark mirror. Gated to deep-evil attunement. LOCKED with Nicko
(2026-09-12): 11-spell list adopted as the working Dark Pacts lineup;
Rot Field and Dominion both stay. Advanced techniques are IO proposals
pending review.

- T1: Hex (weaken target). Siphon (steal health). Grave Whispers (speak
  with the dead; the Graverobber's intel tool).
- T2: Raise Skeleton (combat summon). Wither (DoT + slow). Pact of the
  Leech (lifesteal window).
- T3: Bound Wraith (powerful summon requiring ongoing Focus upkeep, a
  real cost). Rot Field (corruption zone, DoT; feeds taint gain, see
  the taint ruling below).
- T4: Mass Grave (charge-up; raises everything that died nearby as
  undead).
- T5: Dominion (turn enemy undead to your side; permanent at high
  taint). Dark Bargain (pay PERMANENT stat costs for one-time miracle
  effects; the pact fantasy made mechanical).

Proposed ADVANCED TECHNIQUES (IO, for review):
- Apprentice: Hex also slows / Siphon refunds a sliver of Focus on steal
  / hexes last 25 percent longer.
- Adept: Raise Skeleton costs less / Wither spreads to one adjacent
  enemy on death / hexed enemies deal less damage.
- Expert: Bound Wraith upkeep halves / Mass Grave raised undead inherit
  the hexes on the corpses / Pact of the Leech grants brief damage
  reduction during the window.
- Grandmaster: summons reflect taint tier (higher taint = stronger
  summons, the taint-as-resource payoff) / Dominion turns a second
  undead target / Dark Bargain refunds half its stat cost if the
  bargain's condition is met within a day.

## NECROMANTIC TAINT (locked with Nicko, 2026-09-12)

The taint meter is GOOD design and STAYS, structured as a 3-BAND system
(Nicko's ruling: ride it, never scrub it):

- LOW band (0-33): minor dark blessings, no attention.
- MID band (34-66): real blessings, undead start noticing the caster,
  neutral NPCs grow wary.
- HIGH band (67-100): major blessings, undead actively seek the caster
  out, good-court NPCs react to visible taint on sight.

Design contract: taint is a risk-reward DIAL, not a cleanup meter. Dark
casters RIDE taint (push it up for power, eat the attention costs), they
do not manage it tick by tick. Rot Field feeding taint gain is confirmed
as part of this: zones you fight from push the band up.

PURIFY INTERACTION (locked with Nicko, 2026-09-12): taint CAN be
cleansed, but only by a Holy Wards caster purifying ANOTHER. A player
can never cleanse their own taint (Nicko's ruling). Cleansing another's
taint is light-court gameplay; a dark caster who wants their taint
cleansed must find a purifier who will tolerate them, which is exactly
the friction this design wants.

## Corruption Race Spell Kits (NEW, 2026-09-12)

Nicko directive: add magic spells for the corruption races, Vampire and
Undead, the two races that CORRUPT OTHER LIVING BEINGS to fill their
ranks. At least three spells each, thematically grounded. IO proposal,
not locked. OPEN QUESTION 7 covers where these live in the system.

### VAMPIRE SPELL KIT

Theme: blood, mist, and the Embrace. Vampires do not breed; they
convert. The kit is built around feeding, escape, and taking the living
as thralls.

1. Blood Tithe - drain blood from a living target at range; heals the
   vampire and progressively weakens the victim. The feeding spell.
2. Veil of Mist - become mist briefly: untargetable, drifts through
   cracks and grates, cannot attack while in mist.
3. The Embrace - corrupt a DYING living humanoid into a permanent
   vampire thrall under the caster. The rank-filling spell: every kill
   with the Embrace is a new vampire servant.
4. Domination Gaze - lock eyes with a weak-willed living target and
   command it briefly (fight for me, open the gate, stand down).
   Short duration, broken by damage.

### UNDEAD SPELL KIT

Theme: rot, despair, and undeath as infection. The undead do not
recruit; the living JOIN THEM by dying corrupted.

1. Grave Rot - necrotic bolt/touch that applies a rotting curse; any
   living humanoid that dies while rotted rises as a zombie bound to
   the caster. The rank-filling spell.
2. Miasma of Decay - a drifting disease cloud; living beings infected
   inside it weaken over time, and those who die of the miasma rise as
   undead (slower, area-wide conversion).
3. Wail of Despair - a wave of grave-cold despair: fear, broken morale,
   weakened will. Sets up conversion (despaired targets rot faster)
   and routs mortal armies.
4. Corpse Bloom (optional fourth) - explode a nearby corpse into
   spores and grasping roots: burst damage plus a temporary undead
   growth that fights for the caster.

Note: both kits encode Nicko's rank-filling fantasy mechanically: the
Embrace and Grave Rot/Miasma literally convert living enemies into
permanent faction soldiers.

## Cross-School Hybrid Spells (locked with Nicko, 2026-09-12)

LOCKED with Nicko (2026-09-12): cross-school hybrids are FORMALIZED as
dedicated named spells with two-school tier gates. Full cross-product, 6
hybrids, including the axis-keyed pairs (Holy and Dark hybridize with the
elementals; Holy and Dark never hybridize with each other, the axis line
holds between them).

STRUCTURE (locked):
- Gate: BOTH schools at ADEPT (rank 50+) to learn a hybrid.
- Acquisition: learned like any other spell (tome, faction teacher, rare
  world-drop) AND gated by the two-school tier gate. No auto-unlock.
- Tier: hybrids sit at T5-equivalent capstone power.

THE SIX HYBRIDS (IO proposals, for Nicko review):
1. THERMAL SHOCK (Pyro + Cryo): freeze an enemy, then strike with fire
   to shatter it violently. AoE shatter burst scaled to the frozen
   target's max Health. The physical-physics fantasy.
2. CRYO-STORM (Cryo + Storm): lightning that arcing through frozen
   enemies chain-shatters them, arcs +2 through frozen foes.
3. SUNFIRE (Pyro + Holy): burning light, damages and DoTs the living,
   catastrophically damages undead and dark creatures; the crusader's
   fire.
4. STORM-LIGHT (Storm + Holy): judgment bolts that stun evil targets
   and chain between evil-aligned enemies. The lightning of inquisition.
5. WITHERBOLT (Dark + Pyro): necrotic fire, damage over time that
   cannot be healed while burning (heal-block burn).
6. GRAVE-STORM (Dark + Storm): lightning fed by the dead, each corpse
   within the strike area empowers the bolt.

AXIS INTERACTION (locked): axis-keyed hybrids (3-6) require deep-good
(Sunfire, Storm-Light) or deep-evil (Witherbolt, Grave-Storm) attunement
to learn, consistent with their parent schools' axis gating; the tome
burns rule applies. Hybrids 1-2 are neutral-safe.

OPEN (parked): hybrid spell costs, exact magnitudes, and whether
hybrids can appear as rare world-drops in enemy courts' territories
(dark drops teaching Witherbolt to evil players, holy drops teaching
Sunfire in Church vaults). Tuning detail, GDD stage.

- TOMES: found in dungeons, purchased from faction vendors, stolen
  (Stealth + Lockpicking gameplay). Each tome teaches one spell; the
  tome's tier gate must be met to learn it.
- TEACHERS: faction casters teach spells at standing thresholds
  (Church for Holy Wards, covens/undead/vampire courts for Dark Pacts
  and the corruption kits, Colleges for the three elemental schools).
- DISCOVERY: rare spells exist only as world-drops in named locations
  (the best Dark Pacts spells are gifts from undead patrons).
- AXIS-GATED: Holy Wards and Dark Pacts spells physically cannot be
  learned outside their axis band; the tome burns in the wrong hands.
- ADVANCED TECHNIQUES: earned at tier-ups (doc 18), permanent, no
  respec; they specialize known spells rather than adding new ones.

## Open Questions

1. Spell count per school: RESOLVED 2026-09-12 by adopting the locked
   lists: Pyromancy 9, Cryomancy 9, Storm Magic 9, Holy Wards 10,
   Dark Pacts 11 (48 school spells), plus 6 hybrids and two corruption
   kits (4 spells each), ~62 spells total in the system.
2. Cross-school combos: RESOLVED 2026-09-12 (Nicko). FORMALIZED as 6
   dedicated hybrid spells (full cross-product including axis pairs;
   Holy and Dark never hybridize with each other). Gate: both schools
   Adept 50+, learned like spells, T5-equivalent capstones. The six:
   Thermal Shock, Cryo-Storm, Sunfire, Storm-Light, Witherbolt,
   Grave-Storm. Names/effects are IO proposals pending Nicko review.
3. Neutral players learn the three elemental schools freely; ONLY Holy
   Wards / Dark Pacts are axis-gated. RESOLVED 2026-09-12 (Nicko):
   CONFIRMED, elementals open to every affinity with no friction, and
   Holy/Dark are STRICTLY axis-gated, no exceptions. The doc-16
   undead-patron exception for neutral Dark Pacts learning is REJECTED;
   tomes burn for neutrals too. Cross-reference note for the main
   session: 16-specialties.md Graverobber bonus line "Dark Pacts spells
   learnable at neutral (undead patrons teach them)" is VOID per this
   ruling.
4. Taint meter: RESOLVED 2026-09-12 (Nicko). GOOD design, STAYS as a
   3-band system (Low 0-33, Mid 34-66, High 67-100): ride it, never
   scrub it. Rot Field feeds taint gain. Thresholds/effects detail
   parked to GDD tuning within the band structure.
5. Enemy casters: RESOLVED 2026-09-12 (Nicko). HYBRID model: rank-and-
   file enemy casters (coven witches, hedge wizards, undead acolytes)
   cast from the SAME transparent school lists (players can counterplay
   them and loot their tomes); boss casters (hierophants, liches,
   vampire lords) add 1-3 bespoke NPC-only signature spells each, drawn
   from the same elemental grammar so they read consistently. The
   corruption kits (Embrace, Grave Rot, Miasma) are cast BY enemy
   casters under the transparent rule, and the locked Aegis rule is the
   player's counterplay.
6. Summon cap: RESOLVED 2026-09-12 (Nicko). Tier ladder: Novice 1,
   Apprentice 2, Adept 3, Expert 4, Grandmaster 5 active summons, PLUS
   taint bonus for dark casters (+1 at Mid taint, +2 at High taint,
   max 7 at Grandmaster + High taint). Corruption kit summons (Embrace
   thralls, Grave Rot zombies) SHARE the same cap pool. Cap applies to
   combat summons under the caster's control; the earlier note about
   Dark Bargain negotiating the cap is superseded, no bargain bypass.
7. Corruption race spell kits: RESOLVED 2026-09-12 (Nicko). FACTION
   PATRONAGE KITS: the Vampire and Undead kits are a separate reward
   pool from Dark Pacts, learnable only through undead/vampire faction
   patronage (questlines, standing thresholds, patron gifts), gated to
   deep-evil attunement. Any deep-evil player can earn patronage, no
   race/fiction gate. Each kit levels by its OWN use (casting Blood
   Tithe levels the vampire kit, not Dark Pacts), under doc-18
   mechanics. Summon cap and taint bands apply to kit casting.
8. Flame Cloak: RESOLVED 2026-09-12 (Nicko), stays a T3 Pyromancy spell.
   Parallel school self-buffs also confirmed: Rime Armor (Cryomancy T3,
   locked with the Cryomancy list) and Gale Step (Storm Magic T3, locked
   with the Storm list).
9. Detonate: RESOLVED 2026-09-12 (Nicko), stays OUT of the spell list,
   rejected.
10. Purify vs taint: RESOLVED 2026-09-12 (Nicko). Purify CAN cleanse
    taint, but only ANOTHER's, never your own.
11. Apex specialty triggers (from the main session's second sweep):
    RESOLVED 2026-09-12 (Nicko). Three magic apex chains adopted, one
    per stance:
    - THE LICH KING (dark): Dark Pacts Grandmaster + HIGH taint band
      sustained. The lichdom questline; super-powerful magic user and
      summoner.
    - THE SANCTIFIED (light, working name): Holy Wards Grandmaster +
      no/low taint + deep-good axis held. The Church's inner circle,
      sainthood-tier power.
    - THE PARAGON OF BALANCE (neutral, working name): two elemental
      schools at Grandmaster + survived the Allegiance Gambit (six
      refusals). The underworld's balance-keeper.
    APEX LAPABILITY RULE (Nicko, 2026-09-12, verbatim): "once earned,
    apex titles are permanent, and cannot be changed. they are the
    pinnacle lock-in Apex of each affinity. they represent the
    culmination of commitment, and cannot be altered once achieved."
    Apex titles are a deliberate EXCEPTION to doc 16's lapsable-title
    rule: lapsable conditions gate EARNING an apex, but the earned
    title never lapses afterwards.
    Lapsable-title interactions noted for doc 16 (cross-reference for
    the main session): Witchbane lapses on axis drift from deep-good;
    Corpse-Smith lapses on dark-court betrayal; Graverobber lapses on
    swearing allegiance AND its undead-patron Dark Pacts bonus is VOID
    per question 3's strict-gating ruling.