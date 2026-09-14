# 23 - Expedition Followers (The Party System)

Drafted 2026-09-12, world GDD session. Nicko directive: as you
leave camp for an expedition, choose a few friends/followers to
accompany you. A support bard that buffs you, an inventory
squire/slave type, a guard, and a magic user type. Up to 4 come
with you; the total that CAN accompany depends on player level,
up to 4 in endgame. Each type has its own behavior and
characteristics. Status: PROPOSED, awaiting Nicko rulings
(questions at bottom; recommendations marked REC).

## Core Principle

The warp camp (doc 11) is where followers LIVE; the expedition
party is who you CHOOSE to walk out with. Two distinct layers:
- RETINUE (doc 11, locked): everyone kept at your camp. They run
  the camp, greet you, staff stations. They do not travel.
- FOLLOWERS (this doc): the subset you deploy on an expedition,
  up to 4, level-gated. Retinue members you have saved, bought,
  hired, or rescued can be designated as expedition followers.

### Party size (locked from directive: up to 4, level-gated)
- Level 1-9: 1 follower slot.
- Level 10-19: 2 slots.
- Level 20-29: 3 slots.
- Level 30+ (endgame): 4 slots.
- REC working numbers; exact thresholds at GDD tuning. Design
  intent: the party grows with the character, so endgame
  expedition play is a real squad command fantasy without
  breaking doc 04's fixed-difficulty world (followers scale with
  THEIR OWN gear/skill, never the region).

## The Four Follower Types (each its own behavior + characteristics)

### 1. THE BARD (support)
- Role: buffs the party. Does not front-line.
- Behavior: stays mid-rear, behind the front line, moves with
  the player. Never initiates.
- Buff kit (doc 10/12 synergies made mobile): performance aura
  while out of combat (stamina regen up, morale: fear resistance
  vs Wails/Howls per doc 04 grammar), and 1-2 activated songs
  per encounter (a march speed verse, a resolve hymn that
  resists stagger, a luck lay that nudges rare drops, doc 07
  Luck).
- Scales: buff magnitude by their own skill growth (use-based,
  doc 18).
- Weak: low poise, no block. If engaged, they flee behind the
  guard line.

### 2. THE SQUIRE (inventory manager / slave type)
- Role: logistics, NOT combat.
- Behavior (Nicko locked intent): knows to stay OUT of danger.
  Pathfinding keeps them behind you and the whole team, at max
  follow distance; takes no aggro unless absolutely necessary
  (only self-defense if directly attacked, never engages).
- Camp functions on the road: carries the OVERFLOW inventory
  (a mobile second carry pool, feeding doc 07 Carry Weight and
  doc 06 weight economy), tends camp chores on stops, holds
  the torch in dark hours (doc 12 clock).
- Slave variant (doc 11 retinue-slave rules): enslaved squires
  obey identically but never leave on low affinity (doc 11
  slave exception), and their presence upsets anti-slavery
  retinue NPCs (doc 11 affinity consequences).
- Weak: flees combat entirely; if caught, they are a liability
  you must rescue (a capture risk, below).

### 3. THE GUARD (front-line protector)
- Role: tank and bodyguard. The front of the formation.
- Behavior: engages FIRST, holds aggro (taunt-tier attention
  pulling), uses the player verb grammar (doc 04: light/heavy,
  block; soldiers can parry, telegraphed), fights in the light-
  court shield-and-spear pair discipline if light-aligned (doc
  04).
- Kit: shield wall stance (interposes: bodies between enemies
  and you, blocks projectiles aimed at the bard/squire), a
  formation rally (party stagger-resist for seconds).
- Gear-gated like the player (doc 18): you can craft and equip
  your guard with better gear (Workbench supplies, doc 05), a
  real gold-and-attention sink.

### 4. THE ARCANIST (magic user)
- Role: ranged damage and control from the back line.
- Behavior: maintains max casting range (doc 04 stationary
  charge-up grammar: they stop to cast big spells, the party
  protects the cast), rotates elemental damage per their
  school (doc 17's five schools, doc 17 enemy caster model:
  rank-and-file transparent lists).
- Kit: one school's spells at a tier 2-3 below the player's
  cap; zone control (Chill Ground/Fire Zone analogs), a single
  heal or hex depending on axis (Holy/Dark strictly axis-gated,
  doc 17).
- Weak: if closed on, they panic-roll (full player grammar,
  doc 04 humanoids) and need the guard.

## Party Command Grammar (the player's verbs)
- FOLLOW/HOLD: toggle the party between following and holding
  position (hold = guard front, squires to rear cover).
- FOCUS: everyone targets your lock-on.
- WITHDRAW: bard/arcanist/squire fall back to max range; guard
  holds the line.
- HEEL (downed allies): command a downed follower to crawl to
  cover instead of bleeding where they fell.
- No follower micromanagement beyond these: doc 04's fairness
  contract, they fight with the player's grammar, readable.

## FOLLOWER LIFE AND DEATH (LOCKED 2026-09-12, Nicko)

- DOWNED, not automatically killed: followers reach a downed
  state (doc 04 downed grammar) the player can revive with a
  focus channel (vulnerable window). Reviving is the player's
  mercy window; failure to reach them in time has consequences.
- FOLLOWERS CAN DIE (LOCKED, Nicko): a downed follower left
  unrevived, executed by an enemy, or killed by world rules is
  DEAD. Permadeath for the playthrough. The world kills
  followers for real: vampire raiders' The Embrace on the
  downed, undead Miasma, slavers, camp raids, executions by a
  court that caught them, demon invasions (docs 04/11/19).
  The player's mistakes can kill them too: friendly fire, a
  botched rescue, leaving them behind (the Ledger records the
  cause and the deed, doc 20 World Ledger).
- THE CAMP MOURNING SYSTEM (LOCKED, Nicko: the camp remembers
  those it lost): when a follower (or camp retinue member) dies,
  the camp grieves DYNAMICALLY by pairwise affinity:
  - MOURNING PERIOD: for N in-game days after a death (working
    7-14, tuning), the dead are spoken of: retinue NPCs raise
    them in camp dialogue, retell how they died, and the
    greeting ceremony has an empty place where they stood.
  - ATTACHMENT SCALES BY BOND: each mourner's reaction keys off
    THEIR affinity to the dead (member-to-member bonds, the
    doc 11 affinity system extended pairwise):
    - CLOSE BOND: deep grief. The mourner may refuse duties
      briefly, work at reduced pace, keep the dead's bunk
      untouched, or display their trophy/grave marker.
    - FRIEND: speaks of them often during the mourning period.
    - NEUTRAL: mentions them once, then moves on.
    - RIVAL/RESENTMENT: says nothing, or quietly approves
      (evil retinue NPCs may openly approve a death they
      enjoyed; doc 11's evil-affinity rules).
  - BLAME MECHANICS (dynamic): if the camp reads the death as
    the PLAYER'S fault (you left them behind, friendly fire,
    a reckless orders pattern), the attached mourners' affinity
    toward the PLAYER drops; enough collapse and a close friend
    may leave the camp (doc 11 leave-threshold rule). The
    Ledger's deed log is the evidence they judge by.
  - REMEMBRANCE HOOKS (Workbench tie, doc 05): a GRAVE MARKER
    or MEMORIAL decoration is craftable for the dead (the
    trophies category's somber sibling); displaying it feeds
    camp prestige and keeps the mourning dialogue alive past
    the mourning period. A dark camp may mount the skull
    instead (axis-flavored mourning, doc 12).
- DESIGN INTENT: the camp is a LIVING community with memory,
  not a menu (doc 11's living-world principle). Death is
  expensive precisely because the camp is alive.
- Affinity: followers are doc 11 NPCs; they like or dislike
  your deeds, can leave if past threshold (except slaves), and
  the greeting ceremony greets the party you bring home.

## Acquisition (feeds from locked systems)
- Hired at taverns/cities (coin, doc 05/06 economy), rescued
  (doc 20 frame library: rescue/capture personal axes), bought
  from slavers (dark territory), granted by courts at standing
  thresholds (doc 12), redeemed bandits (doc 11 thief
  judgment BEFRIEND route), promoted camp staff (doc 11).
- Follower gear: craftable at the warp camp (locked all-craft
  principle, doc 05) and equipable per their archetype.

## Interaction With Locked Systems
- doc 04: followers use the player verb grammar; beasts/undead
  grammar rules hold for what they fight.
- doc 12: affinity-relative danger applies to them (a bard
  follower sleeps on the good clock).
- doc 13: followers can man camp defenses (doc 11) during your
  absence; holds your followers hold can be lost (doc 13).
- doc 17: arcanist schools strictly axis-gated; corruption kits
  can target YOUR followers (The Embrace on downed, doc 04).
- doc 19: wolf players' pack instinct: a Hidden Court wolf
  player's followers suffer no Howl fear (pack-bonded, doc 03
  strain overlay).
- doc 20: personal axes key off follower fates (the saved
  princess IS a follower archetype, doc 11).

## FOLLOWER PROGRESSION + THE FOLLOWER MENU (LOCKED 2026-09-12, Nicko)

- FOLLOWERS HAVE AN XP SYSTEM (Nicko ruling, supersedes the REC
  gear-scaled proposal): followers LEVEL UP as they fight by your
  side. Follower XP accrues from kills/encounters they accompany
  (shared party XP stream alongside the player's doc 07 XP; exact
  share = GDD tuning). Their own follower level scales their
  combat competence (health, damage, their kit's effectiveness)
  independent of gear.
- Follower level does NOT change the world's fixed difficulty
  (locked doc 04); it grows them toward THEIR archetypes' caps.
- GEAR still matters and stacks with levels: the player equips
  followers with Workbench-crafted gear (locked all-craft), tier
  gates read their follower level (doc 18 gate grammar).
- THE FOLLOWER MENU (Nicko, visible UI): a dedicated menu at the
  camp (and usable at taverns) where you VIEW each follower's
  stats (follower level, XP bar, archetype, affinity, kit
  readout) and EQUIP them (gear slots per archetype: weapon/
  armor/trinket). The party screen from doc 23's open question
  4 is CONFIRMED as this menu.

## OPEN QUESTION RESOLUTIONS (locked 2026-09-12, Nicko)

1. SLOT THRESHOLDS: LOCKED as authored (1/2/3/4 at levels
   1/10/20/30; GDD tuning may adjust after playtest).
2. BARD SONG POOL: structure LOCKED; the pool is AFFINITY-KEYED
   (Nicko): different bards with different affinities sing
   different songs and buff different things.
   - GOOD-affinity bards grant PROTECTION buffs: wards, fear
     resistance, heal-chants (Holy-adjacent, doc 17 grammar).
   - EVIL-affinity bards buff DAMAGE and can coat/ignite weapons
     with elemental damage types (the war-singer: Fire/Frost/
     Storm coatings channeled through song).
   - NEUTRAL bards carry the travel kit: march speed, luck lay,
     morale.
   - Bards are BEFRIENDED AND RECRUITED from taverns and across
     world locations (doc 20 rumor economy + doc 03 shadow court
     dens as sources). Their affinity is their kit: the bard you
     befriend determines the songs you get. Bard type list and
     per-song numbers: GDD tuning.
3. FOLLOWER MEAL UPKEEP: NONE (Nicko). Followers' cost is the
   hire price + gear only; food stays the player's strategy lane
   (doc 10).
4. MOURNING PERIOD: 14 IN-GAME DAYS (Nicko, the locked band's
   ceiling: grief lingers, the camp remembers long).

## Open Questions (remaining, assigned per tracker rules)
1. Bard type list (the named bard archetypes per affinity) and
   per-song numbers: GDD tuning + authoring. RESOLVED 2026-09-14
   (Nicko): ONE FOLLOWERS GDD PASS owns this (quintet ruling: opens
   1-4 all ride the followers GDD pass; UI details route through it
   to the UI art doc when authored).
2. Follower UI details (party screen layout, field command
   prompts): art/tech plan. RESOLVED 2026-09-14 (Nicko): rides the
   followers GDD pass, which hands UI specs to the UI art doc.
3. Romance buffs for expedition followers (doc 11 romance
   role): retinue GDD item, carried. RESOLVED 2026-09-14 (Nicko):
   rides the followers GDD pass.
4. Follower XP share of the party stream: GDD tuning. RESOLVED
   2026-09-14 (Nicko): rides the followers GDD pass.