# 04 - Combat System

## Decisions (locked with Nicko)
- Difficulty is FIXED per region: no level scaling. Specialization pressure
  stays sharp; early zones stay deadly to low-level characters. One seamless
  fixed-difficulty world: NO region tier gating at all, endgame zones are
  simply far/dangerous places you can walk into whenever you dare.
- Death penalty: drop XP/currency on death, recoverable at your corpse
  (classic souls loop). LOCKED 2026-09-11.
- Healing: potions AND spells. Healing spells exist but are found later
  (mid-to-late game) and gate on magic skill, so the early game leans on
  crafted potions. LOCKED.
- Save/respawn is TAVERN-BASED: you save your next respawn point at a tavern
  local to the area you are exploring. Taverns are the souls-bonfire analog,
  themed into the world fiction. Intermediate saves come from CAMPING
  (09-expedition-camping): camps save progress; once unlocked, the warp camp
  becomes the DEFAULT forward respawn (taverns remain usable). LOCKED.
- AIMING (locked + revised 2026-09-11): dual-mode. Stationary (standing or
  crouched) = manual reticle aim for bows/crossbows/aimed spells; moving =
  lock-on fire/cast; charge-up spells require standing still.
- NO ITEM REPAIR (locked 2026-09-11): items are permanent; crafting
  relevance lives in tiers, enchants, and grades instead. LOCKED.
- MOUNTS (locked): travel speed only, no mounted combat. LOCKED.
- PARRY: yes, and not shield-only (Shield/Defense skill line holds the
  parry techniques; some weapon techniques include parry-adjacent options -
  Riposte Master in Shield, Guard-counter stance in Long Blade). Full
  move-set rules are GDD-stage.

## Combat Feel
Combat should feel like Dark Souls: deliberate, weighty, readable. Lock-on,
dodge roll, camera follow are the feel-defining verbs. Sprite animation frames
must sell weight (big wind-ups, committed recovery) because there is no 3D
skeleton to lean on for anticipation. Skill techniques (doc 18) are the
expressive layer: each weapon line's tier choices (Riptide, Skullringer,
Skewer, Bulwark...) expand the moveset permanently as you specialize.

## Core Verbs
- Light attack, heavy attack (weapon-class dependent)
- Dodge roll (i-frames, stamina cost, roll direction = camera or lock-on
  relative)
- Block / parry (shield and some weapons; parry window is a skill test)
- Lock-on toggle with soft-target switching
- Stamina governs attacks, rolls, blocks. Health and stamina regenerate
  slowly out of combat; stamina regen slows while blocking. (Exact regen
  rules TBD in GDD.)
- Dual-mode aiming (see locked decisions above).
- TECHNIQUES: permanent tier-unlocked moves per skill line (doc 18) -
  offensive, utility, and specialist options shape each build's moveset.

## Weapon Classes (9 combat skill lines - aligned with 15-skill-lines.md)
- Short Blade (daggers, shortswords) - fast, crit-flavored
- Long Blade (longswords, claymores) - balanced arcs
- Blunt (maces, hammers) - armor-crushing, stagger
- Axes - bleed, heavy chops
- Polearms - reach, spacing control
- Archery (bows, crossbows)
- Dual Wielding - off-hand attacks, combo finishers; levels all THREE of
  its contributing skills (e.g. dagger + longsword levels Short Blade,
  Long Blade, AND Dual Wielding)
- Shield / Defense - block stability, parry windows; levels while a shield
  is equipped and used
- Unarmed - fallback and roleplay option

The weapon-skill web is the combat-to-progression pipeline. Each line has a
primary passive curve (doc 18) plus five tier-up technique choices that
permanently shape the moveset.

## Skill Progression in Combat (doc 18 rules)
Ranks 1-100 by use; tiers at Novice/Apprentice/Adept/Expert/Grandmaster
(25/50/75/100); each tier-up offers 2-3 technique options (one offensive,
one utility, one specialist); choices are permanent. GEAR GATES read TIERS:
Tier-2 gear needs Apprentice, Tier-3 Adept, Tier-4 Expert, Tier-5/named
Grandmaster. Rank curve: diminishing after 50 (2x by 75, 3x by 95). No
decay. No respec.

## Enemy Design Direction
- Humanoids (bandits, cultists, soldiers) - telegraphed, gear-based movesets.
- Beasts (wolves, bears, wendigo-type things) - fast, spacing tests.
- Undead (skeletons, ghouls, revenants) - night-anchored (dangerous half of
  the day is affinity-relative: see 03/12), grave-robbing economy.
- Witch-fauna and horrors - the signature tier: covens' bound creatures,
  cursed things, boss-scale abominations.
- Faction soldiers - they fight like the player does (lock-on, rolls), which
  makes faction combat dangerous and honest.
- (New) COURT FORCES: light-court paladins and dark-court creatures are each
  other's mirror. An evil player's daylight-sleep ambush comes from paladins
  who fight with wards and formation; a good player's night ambush comes
  from vampire/undude raiders with dark pacts. Both courts' kits are the
  magic schools (doc 17) made hostile.
- (New) CORRUPTION KITS: vampire and undead forces use their race kits
  (Blood Tithe, The Embrace, Grave Rot...) whose conversion mechanics make
  Aegis-blessed weapons the light court's counterplay (doc 17, decision 38).

## Ranged and Spell Aiming (locked with Nicko, revised 2026-09-11)
DUAL-MODE aiming system:
- STATIONARY (standing or crouched): manual aiming with an over-shoulder
  reticle for bows, crossbows, and aimed spells. Precision mode.
- MOVING: lock-on fire/cast against targets. The full souls-like combat
  experience: you can fight while moving, or commit to precision.
- EXCEPTION: charge-up spells cannot be cast while moving - stationary
  commitment is the standard souls caster trade-off (big spell = big
  vulnerability window).

## COMBAT FEEL RULES (LOCKED 2026-09-12, Nicko, combat/crafting/loot session)

### Poise and stagger (the universal stagger resource)
- Every combatant (player and enemy) has a POISE pool that regenerates
  after a few seconds without taking a poise hit.
- Every attack deals poise damage alongside health damage. Light attacks
  chip poise; heavies and Blunt weapons melt it. Poise broken = STAGGER:
  a committed recovery animation, the souls punish-window. Downed
  states (from Bonecracker etc.) are an upgraded stagger.
- Poise pools scale with armor weight class and enemy size, NOT player
  level (fixed difficulty: a knight has knight poise in every region).
- Stagger interactions with the LOCKED technique menus: Concussive
  Force extends staggers, Momentum of Ruin stacks from staggers,
  Pressure Strike extends them, staggers feed Blunt's whole identity.
- BLOCKED hits still transfer a fraction of poise damage (chip poise),
  which is what makes Blunt's Crushing Blow and shield-play matter.

### Parry windows (by source, one grammar)
- PARRY = a short active window at the start of block input. Success
  negates the hit and opens a punish window on the attacker.
- Window sizes by source (widest to narrowest): shield parry >
  Riposte Master (extends it further) > Twin-Parry (dual wield, two
  weapons overlapping = bigger window than any single weapon) >
  weapon shaft-parries (Lever Guard) > bare blade parries.
- Trade rule: narrow windows get BIGGER punishers (Lever Guard opens a
  heavy counter; shield parry opens a normal riposte). Risk and reward
  scale together.
- Enemy parries: only faction soldiers (the player-grammar enemies)
  can parry, at a readable, smaller window, telegraphed by stance.
  Beasts/undead never parry.

### Stamina discipline
- Attacks, rolls, blocks, parries all cost stamina; sprinting drains
  it. At zero stamina the player is STAMINA-BREAKED: brief vulnerable
  state, no actions (souls standard).
- REGEN RULES (proposed exacts): regen pauses ~1 second after ANY
  stamina action; then regenerates fast while idle/walking, reduced
  ~50 percent while blocking, near-zero while attacking or charging.
  Out of combat, health and stamina regen slowly (locked doc 04).
- Equipment weight (Carry Weight stat is inventory; EQUIP LOAD is the
  combat-side weight of worn/wielded gear) gates roll speed: light =
  fast roll, medium = standard, heavy = slow roll. Souls rule,
  consistent with Armorsmithing weight classes.

### Enemy grammar: everyone fights with the player's verbs
ENEMIES USE THE SAME VERB SET: light attack, heavy attack, dodge-roll,
block, (soldiers only) parry. Nothing enemies do is something the
player cannot do; readability is the fairness contract.
- HUMANOIDS (bandits, cultists, soldiers): full grammar. Bandits are
  sloppy versions (slow reads, panic rolls); soldiers are disciplined
  versions (formation, spacing, block-and-punish loops).
- BEASTS: no block/parry, but real dodge-equivalents (leaps, sidesteps)
  and high poise; the spacing test.
- UNDEAD: no dodge, no parry; relentless pressure walkers with heavy
  poise, some with corruption-kit casters among them. Their answer to
  player spacing is numbers and Wail/Grave Rot zone denial.
- FACTION SOLDIERS fight like the player does (locked doc 04):
  lock-on, rolls, blocks, punishes. Light-court soldiers fight in
  PAIRS with shield-and-spear discipline (one blocks, one stabs);
  dark-court soldiers fight as PACKS with bleed-and-retreat rhythm.
- COURT FORCES are the schools made hostile (locked doc 04):
  - PALADINS (light): fight with Holy Wards grammar. Light Ward on
    approach, Blessed Bolts at range, Consecrate zones to deny the
    player's ground, Sanctuary at officer tier. They are the day-sleep
    ambush for evil players. Killing them with Aegis weapons matters
    (locked doc 17 rule).
  - VAMPIRE/UNDEAD RAIDERS (dark): the night ambush for good players.
    Vampire raiders use the corruption kit grammar (Blood Tithe
    self-heal loops, Veil of Mist escape resets, The Embrace on the
    downed player's RETINUE, Domination Gaze to turn a retinue member
    mid-fight). Undead raiders use Grave Rot/Miasma zone denial and
    Wail of Despair morale breaks. Their bespoke boss casters add the
    1-3 signature spells per doc 17's enemy-caster rule.
  - COUNTERPLAY TEACHING: encountering paladins teaches undead
    players the Aegis rule viscerally (their Embraced converts stop
    rising when paladins with blessed steel show up); encountering
    vampire raiders teaches good players the same system from the
    other side. The war's mechanics teach themselves through its
    ambushes.

### Open questions added by this section (also in 08):
1. Exact poise/stamina numbers, regen curves, window sizes in
   seconds/frames: GDD tuning (structure locked here, numbers later).
2. Equip load: confirm the three roll-speed bands and their exact
   weight thresholds vs armor weight class: tuning, GDD.

## Encounter Philosophy
- Density over quantity: fewer encounters, each with a plan.
- Dungeons teach a monster pool; the boss remixes it.
- Open-world encounters scale to region danger, NOT to player level (locked:
  fixed difficulty everywhere), so specialization keeps mattering.
- Affinity-relative threat (doc 12): the world's danger schedule inverts by
  alignment. The same night road is a gauntlet for a good player and home
  ground for an evil one.

## TECHNIQUE MENUS, ALL 9 COMBAT LINES (LOCKED 2026-09-12, Nicko, combat/crafting/loot session)

Structural rules locked with Nicko 2026-09-12:
- Every menu has EXACTLY 3 options: one OFFENSIVE, one UTILITY, one SPECIALIST.
  9 lines x 4 tier-ups = 36 menus, 108 techniques.
- Free mix rule: techniques may be new moves, stances, behaviors, OR passive
  perks, wherever the fantasy is right. The rank curve still owns flat stat
  growth; techniques add identity on top.
- Doc 18's example techniques are KEPT as anchor picks inside their menus
  (marked "carried"). Names and effects preserved.
- APPROVED BY NICKO 2026-09-12: "This all looks good for weapons." All 36
  menus and 108 techniques below are LOCKED as written.

### 1. SHORT BLADE (fast, crit-flavored)
- APPRENTICE (25):
  - OFFENSIVE: Riptide (carried): fast double-slash; if the second hit crits,
    a third free slash follows.
  - UTILITY: Quickstep Thrust: attacking out of a dodge roll has no recovery
    penalty; the roll-to-poke chain becomes fluid.
  - SPECIALIST: Venom Carrier: weapon poisons and alchemical oils apply at
    full potency without needing Alchemy ranks.
- ADEPT (50):
  - OFFENSIVE: Fang Flurry: three-hit chain finisher; the finisher always
    crits staggered foes.
  - UTILITY: Shadow Kill: kills from stealth are silent and do not alert
    nearby enemies.
  - SPECIALIST: Backstab Mastery (carried): stealth openers and rear strikes
    gain bonus crit damage, scaling with rank.
- EXPERT (75):
  - OFFENSIVE: Hemorrhage: critical hits open bleeding wounds that stack
    with weapon bleed.
  - UTILITY: Slip the Blade: a perfectly timed dodge (attack passing through
    your i-frames) grants 2 seconds of bonus attack speed.
  - SPECIALIST: Duelist's Reading: against a single locked-on humanoid, your
    crit chance grows the longer the duel lasts.
- GRANDMASTER (100):
  - OFFENSIVE: Thousand Cuts: the full light-attack chain ends in a 6-hit
    barrage.
  - UTILITY: Vanish and Strike: dodge through an enemy attack while
    breaking lock-on to leave a decoy afterimage; re-engage from any angle.
  - SPECIALIST: Assassin's Doctrine: all your crits ignore a portion of
    armor, and poisons applied by you tick 50 percent longer.

### 2. LONG BLADE (balanced arcs)
- APPRENTICE (25):
  - OFFENSIVE: Rising Cleave (carried): upward arcing cut that pops light
    enemies off their feet briefly.
  - UTILITY: Guard-counter Stance (carried): block, then immediately counter;
    the counter carries bonus poise damage.
  - SPECIALIST: Long Guard: heavy attacks gain hyper armor; chip hits do not
    interrupt the swing.
- ADEPT (50):
  - OFFENSIVE: Bleeding Edge (carried): heavy attacks apply bleed buildup.
  - UTILITY: Momentum Arc: sweeping attacks hit a wider arc at no extra
    stamina cost.
  - SPECIALIST: Knight's Poise: your own swings cannot be flinched by chip
    damage; only real staggers interrupt you.
- EXPERT (75):
  - OFFENSIVE: Crescent Storm: spinning slash hitting everything around you;
    heavy stamina commitment.
  - UTILITY: Riposte Line: after a successful blade-parry, a guaranteed
    critical follow-up window opens.
  - SPECIALIST: Battlefield Reach: light-attack chains extend by one extra
    step (4-hit chains).
- GRANDMASTER (100):
  - OFFENSIVE: Judgment Cut: hold heavy to charge an unblockable overhead
    arc.
  - UTILITY: Blade Dance: dodge rolls no longer reset your combo; attacks
    flow seamlessly through rolls.
  - SPECIALIST: Perfect Edge: heavy attacks partially pierce block and
    shield stability.

### 3. BLUNT (armor-crushing, stagger)
- APPRENTICE (25):
  - OFFENSIVE: Skullringer (carried): fully charged heavy guarantees a
    stagger.
  - UTILITY: Crushing Blow: your hits damage through block and drain
    defender stamina faster.
  - SPECIALIST: Mauler: stagger damage scales with the target's armor
    weight; plate is your favorite food.
- ADEPT (50):
  - OFFENSIVE: Armor-Breaker (carried): strikes reduce the target's armor
    for the remainder of the fight.
  - UTILITY: Shockwave: attacking immediately after a dodge roll sends a
    small poise ripple.
  - SPECIALIST: Concussive Force: staggered enemies stay staggered longer
    (extended recovery animations).
- EXPERT (75):
  - OFFENSIVE: Earthquake Slam (carried): AoE poise damage in a ring around
    the player.
  - UTILITY: Iron Stance: while charging a heavy, incoming hits do not
    interrupt the charge and deal half damage.
  - SPECIALIST: Bonecracker: staggered humanoids are knocked down; downed
    enemies take bonus damage.
- GRANDMASTER (100):
  - OFFENSIVE: Ruinfall: capstone ground slam with an expanding
    ring-shaped shockwave.
  - UTILITY: Momentum of Ruin: each stagger you land grants a short stacking
    damage buff; staggers snowball.
  - SPECIALIST: Dread Impact: your staggers cause fear in nearby lesser
    enemies (they hesitate or flee).

### 4. AXES (bleed, heavy chops)
- APPRENTICE (25):
  - OFFENSIVE: Deep Gash (carried): heavy chops apply a deep, long bleed.
  - UTILITY: Cleave: light attacks arc wide and catch two enemies in front.
  - SPECIALIST: Butchery: axes harvest monster parts and pelts faster and
    one grade higher (direct Hunting/Skinning synergy).
- ADEPT (50):
  - OFFENSIVE: Reaving Swing (carried): heavy swings hit through blocks for
    partial damage.
  - UTILITY: Berserk Momentum: consecutive hits without being hit build
    attack speed; taking a hit resets it.
  - SPECIALIST: Blood Frenzy: killing a bleeding enemy restores stamina.
- EXPERT (75):
  - OFFENSIVE: Execute (carried): bonus damage against bleeding foes, plus
    an instant-kill threshold on low-health targets.
  - UTILITY: Wide Reap: the dodge-roll attack sweeps behind you; the
    anti-surround tool.
  - SPECIALIST: Ravager: bleeding enemies take a percent more damage from
    all your attacks.
- GRANDMASTER (100):
  - OFFENSIVE: Headsman's Arc: enormous overhead chop, bonus damage vs
    staggered targets, refunds stamina on kill.
  - UTILITY: Warpath: kills grant brief movement speed and make your next
    heavy free.
  - SPECIALIST: Executioner's Code: the Execute threshold widens and
    executions restore a sliver of health.

### 5. POLEARMS (reach, spacing control)
- APPRENTICE (25):
  - OFFENSIVE: Skewer (carried): long forward lunge; the reach gap-closer.
  - UTILITY: Counter-Thrust: a perfect dodge rewards an immediate
    extended-reach poke.
  - SPECIALIST: Reach Master: attack range extends further; poke enemies
    from outside their own ranges.
- ADEPT (50):
  - OFFENSIVE: Sweeping Halberd: wide horizontal sweep hitting a whole arc.
  - UTILITY: Wall of Steel (carried): anti-approach stance; enemies trying
    to close distance are poked and pushed back, costing you stamina per poke.
  - SPECIALIST: Phalanx Footwork: you can walk backward at full attack
    speed; the kiting fantasy.
- EXPERT (75):
  - OFFENSIVE: Dismount (carried): hook and pull riders down; also yanks
    shields and works as bonus damage vs large enemies.
  - UTILITY: Lever Guard: parry with the shaft; a shorter window than a
    shield parry but it opens a heavy counter.
  - SPECIALIST: Distance Discipline: hits landing at maximum reach deal
    bonus damage.
- GRANDMASTER (100):
  - OFFENSIVE: Dragon Piercer: chargeable thrust that penetrates a whole
    line of enemies.
  - UTILITY: Impaling Pivot: instantly reposition 180 degrees mid-combo;
    face any direction at will.
  - SPECIALIST: Master of the Line: locked-on enemies cannot circle behind
    you without triggering a free poke; the space around you is yours.

### 6. ARCHERY (dual-mode aiming line)
- APPRENTICE (25):
  - OFFENSIVE: Quick-Nock (carried): faster draw; follow-up shots come
    quicker.
  - UTILITY: Steady Hands: stationary manual-aim reticle sway shrinks the
    longer you hold aim.
  - SPECIALIST: Deadeye: precision hits (headshots on humanoids) crit.
- ADEPT (50):
  - OFFENSIVE: Piercing Shot (carried): the arrow passes through multiple
    foes in a line.
  - UTILITY: Snapshot: moving lock-on shots fire faster with a reduced
    accuracy penalty.
  - SPECIALIST: Fletcher's Eye: arrows accept alchemical payloads (fire,
    frost, poison tips) without Alchemy ranks.
- EXPERT (75):
  - OFFENSIVE: Arced Volley (carried): loose a fan of arrows over an area.
  - UTILITY: Cover Fire: a hit to an enemy interrupts and staggers its
    attack animation.
  - SPECIALIST: Sharpshooter's Calm: your first shot at an unaware target
    from out of combat is a guaranteed crit.
- GRANDMASTER (100):
  - OFFENSIVE: Rain of Death: chargeable sky-shot; an arrow barrage falls on
    an area.
  - UTILITY: Storm of Steel: while stationary, each consecutive shot draws
    faster than the last.
  - SPECIALIST: Grandmaster's Ballistics: arrows partially pierce armor, and
    crossbows reload on the move.

### 7. DUAL WIELDING (off-hand, combos)
- APPRENTICE (25):
  - OFFENSIVE: Cross-Strike (carried): crossing X-slash using both weapons;
    damage partially stacks.
  - UTILITY: Off-Hand Riposte: parry with the off-hand weapon and counter.
  - SPECIALIST: Twinned Practice: dual-wielding grants +10 percent rank gain
    to the two equipped weapon lines (deepens the "levels all three" rule).
- ADEPT (50):
  - OFFENSIVE: Flurry Rush: rapid alternating strike chain.
  - UTILITY: Weapon Swap Flow: swapping weapons mid-combo continues the
    combo instead of resetting it.
  - SPECIALIST: Twin-Parry (carried): parry with both weapons for a larger
    window than any single-weapon parry.
- EXPERT (75):
  - OFFENSIVE: Tempest Flurry (carried): a long alternating flurry ending
    in a spin.
  - UTILITY: Blur Step: micro-dash between combo chains; attack-dodge-attack
    as one motion.
  - SPECIALIST: Cross-Bleed: a full combo finisher applies bleed if either
    equipped weapon is an axe or short blade.
- GRANDMASTER (100):
  - OFFENSIVE: Whirling Death: capstone spin hitting everything around you
    with both weapons.
  - UTILITY: Phantom Second: dodge through an enemy attack to trigger an
    instant off-hand counter.
  - SPECIALIST: Grandmaster's Rhythm: combo chains never reset from
    dodging; your offense flows through rolls indefinitely.

### 8. SHIELD / DEFENSE (block stability, parry windows)
- APPRENTICE (25):
  - OFFENSIVE: Shield Bash (carried): cheap stagger strike with the shield.
  - UTILITY: Firm Stance: your block covers a wider facing arc; harder to
    hit through the block.
  - SPECIALIST: Second Skin: shield weight penalty reduced; light shields
    gain stability.
- ADEPT (50):
  - OFFENSIVE: Riposte Master (carried): the parry window extends and the
    riposte deals poise-breaking damage.
  - UTILITY: Battering Advance: shove forward behind the shield, pushing
    enemies while walking.
  - SPECIALIST: Guardian's Read: while blocking, enemy attack telegraphs
    stay visible longer (readability perk that fits sprite combat).
- EXPERT (75):
  - OFFENSIVE: Bulwark (carried): block without stamina cost for N hits per
    fight.
  - UTILITY: Shield Charge: running shield rush that tackles enemies down.
  - SPECIALIST: Bodyguard: nearby retinue and allied NPCs take reduced
    damage while you hold block close to them.
- GRANDMASTER (100):
  - OFFENSIVE: Unyielding Verdict: after absorbing 5 hits while blocking,
    your next bash deals massive poise damage.
  - UTILITY: Last Wall: below 25 percent health, block stability and parry
    window grow.
  - SPECIALIST: Wall of the People: allies near your block share your block
    stability; the formation-tank fantasy.

### 9. UNARMED (fallback and roleplay line)
- APPRENTICE (25):
  - OFFENSIVE: Jab Rush: fast jab chain, the cheapest stamina attack in the
    game.
  - UTILITY: Throat Jab (carried): a hit that silences and interrupts
    casters.
  - SPECIALIST: Rough Hands: grapple and throw any humanoid smaller than a
    troll.
- ADEPT (50):
  - OFFENSIVE: Bear-Hug Slam (carried): grapple, lift, and slam; AoE damage
    on landing.
  - UTILITY: Rolling Tackle: dodging into an enemy turns the roll into a
    tackle.
  - SPECIALIST: Iron Palm (carried): fists break doors, barrels, and weak
    locks; the brute-force alternative to Lockpicking.
- EXPERT (75):
  - OFFENSIVE: Pressure Strike: hits against staggered enemies extend the
    stagger (stun-lock play).
  - UTILITY: Grapple Master: grapples work on larger enemies and can disarm
    weapons from hands.
  - SPECIALIST: Open Palm Stance: after dodging through an attack, your
    next punch crits.
- GRANDMASTER (100):
  - OFFENSIVE: Fist of the Mountain: chargeable megapunch that launches
    enemies.
  - UTILITY: Iron Body: while fighting unarmed-only, incoming damage is
    reduced; the monk tank.
  - SPECIALIST: Grandmaster's Grip: grappled enemies can be used as human
    shields or hurled into other enemies.

## Open Questions (current state - all first-draft questions resolved)
- Souls death penalty, healing economy, aiming mode, level scaling, mounted
  combat: ALL RESOLVED (see Decisions).
- Parry move-set specifics (window sizes, weapon-parry rules): GDD-stage
  balance work.
- Stamina/health regen exact rules: GDD-stage.

## Bake-in from 26-A analysis (2026-09-13, PROPOSED)

Status line per item: PROPOSED (Astrabot bake-in from 26-A analysis,
2026-09-13, pending Nicko lock). Source: 26-astrabot-analysis.md.

- Facing rules for billboard combat: logical facing = last input;
  rendered view = nearest directional view of that facing; combat arcs
  (block, parry, Wall of Steel, Firm Stance) resolve against logical
  facing; defensive poses snap their directional view to logical facing.
  Full spec in doc 28 (PROPOSED). PROPOSED.
- Telegraph frame contract: every enemy attack animation carries a
  mandatory telegraph frame flashing the danger accent. Parry-window
  readability depends on it. PROPOSED.
- Per-pose frame budgets: 8 frames for wind-ups and staggers, 4 for
  idle/walk. PROPOSED.
- Hit feedback rule: because every flipbook hit-react costs frames x 8
  directions, lean hit feedback on the engine: hit-stop, contact flash
  on the impact accent, camera shake, light-tint per doc 02 pillars 3-4.
  Impacts stay inside doc 24's no-modern-particle-realism law (diegetic
  light, not particle realism). PROPOSED.
- Roll direction: 16-view player recommendation (spec and the 8-view
  alternative in doc 28, PROPOSED). PROPOSED.