# 18 - Skill Progression Mechanics

Drafted 2026-09-11. The deep-dive Nicko requested: what leveling up in each
skill MEANS, how each skill changes as it grows, and how points are spent
vs. unlocked. Magic deep-dive deferred to a separate session (doc 17 stays
as parked first-pass).

## The Core Model (framework proposal)
Every skill line uses a TWO-LAYER structure:

LAYER 1 - RANKS (passive, use-based):
- Skills rank 1-100 by USING them (locked philosophy). No manual points
  flow into ranks.
- Every rank gives a small passive improvement on that skill's PRIMARY
  CURVE (see per-line meanings below). This is the Morrowind feel: you
  never "spend" anything, you simply get better at what you do.

LAYER 2 - TIERS + TECHNIQUE CHOICES (the agency layer):
- Five named tiers bracket the ranks: NOVICE (1-24), APPRENTICE (25-49),
  ADEPT (50-74), EXPERT (75-99), GRANDMASTER (100).
- TIER-UP is the meaningful event. On each tier-up the player CHOOSES ONE
  TECHNIQUE from that skill's tier menu (2-3 options per tier).
- Techniques are unlocks (choose, not buy): no skill-point currency. The
  "cost" is the play that earned the tier. This answers "points spent vs
  unlock": RANKS are passive growth; TIER-UPS are choice moments where you
  spend nothing and pick a technique.
- Each tier menu contains at least one OFFENSIVE, one UTILITY, and one
  SPECIALIST option, so two players at Adept Short Blade can diverge.
- Technique choices are PERMANENT for that character (respec question
  parked).

## What Tier Means Globally
- GEAR GATES: weapon/armor tiers require skill tiers (locked principle:
  the specialist's kit). Proposal: Tier-2 gear needs APPRENTICE, Tier-3
  needs ADEPT, Tier-4 needs EXPERT, Tier-5 (named/legendary) needs
  GRANDMASTER.
- SPECIALTIES read tiers: specialty combos (doc 16) reference tiers
  ("Adept Stealth + Apprentice Lockpicking"), not raw ranks.
- NPC world reaction: at GRANDMASTER, an NPC can comment on your skill
  (the blacksmith hears you forge Grandmaster-grade blades).

## Per-Line Meaning (what growing each skill does)
Format: PRIMARY CURVE (passive per-rank) + example TIER TECHNIQUES (one
per tier shown; FULL MENUS NOW WRITTEN: all 36 menus live in
04-combat-system.md, LOCKED with Nicko 2026-09-12 - the examples below
are the carried anchors inside those menus).

COMBAT:
1. Short Blade - Curve: +damage, +attack speed, -stamina cost. Techniques:
   Riptide (fast double-slash) / Backstab bonus / Poison-applied strikes.
2. Long Blade - Curve: +damage, +sweep arc, +poise damage. Techniques:
   Rising Cleave / Guard-counter stance / Bleeding Edge (bleed buildup).
3. Blunt - Curve: +stagger damage, +armor penetration. Techniques:
   Skullringer (guaranteed stagger) / Armor-Breaker strike / Earthquake
   slam (AoE poise).
4. Axes - Curve: +bleed buildup, +heavy-attack damage. Techniques:
   Deep Gash / Execute (bonus vs. bleeding foes) / Reaving Swing (hits
   through blocks).
5. Polearms - Curve: +reach, +spacing control (pushback). Techniques:
   Skewer (lunge) / Wall of Steel (anti-approach stance) / Dismount
   (pull riders down).
6. Archery - Curve: +draw speed, +aim stability, +damage. Techniques:
   Quick-Nock / Piercing Shot (through multiple foes) / Arced Volley
   (loose a fan).
7. Dual Wielding - Curve: +combo finisher damage, +flurry speed.
   Techniques: Cross-Strike / Tempest Flurry / Twin-Parry.
8. Shield/Defense - Curve: +block stability, +parry window size, -block
   stamina cost. Techniques: Shield Bash / Riposte Master / Bulwark
   (block without stamina for N hits).
9. Unarmed - Curve: +damage, +grapple power. Techniques: Throat Jab
   (silence casters) / Bear-Hug Slam / Iron Palm (breaks doors/locks
   with fists).

MAGIC (schools detailed in doc 17; skill mechanics identical):
10-14. Curve per school: -Focus cost, +cast speed, +effect magnitude.
   Techniques = school spells unlocked at tiers (tier 3+ spells require
   the tier). Dark Pacts adds taint management techniques; Holy Wards
   adds ward-reflection techniques.

CRAFTING:
15. Weaponsmithing - Curve: +craft quality odds, +craft speed, -material
    waste. Techniques: Masterwork Edges (quality tier floor) / Signature
    Series (craft named-line weapons) / Reforge (re-roll one stat).
16. Armorsmithing - Curve: +quality, +weight efficiency. Techniques:
    Fitted Armor (-weight, same protection) / Composite Plating / Seal of
    the Maker (armors carry your house mark - links to lore rights).
17. Alchemy - Curve: +potion potency, +batch size, +rare-extraction.
    Techniques: Double-Brew / Poisoner's Hand (oils last longer) /
    Philosopher's Shortcut (1 bonus rare extract per day).
18. Enchanting - Curve: +enchant capacity, +scroll scribe quality.
    Techniques: Twin-Socket / Scroll Mastery / Soul-Binding (charms with
    active abilities).
19. Cooking - Curve: +buff magnitude, +grade success odds (per locked
    gating: knowledge gates attempt, skill gates success/magnitude).
    Techniques: Salt-Blessing (salt cheaper/better) / Feast Prep (cook
    for the retinue, group buffs) / Masterwork Palate (5-ingredient
    dishes without Fry Cook).

GATHERING:
20. Herbalism - Curve: +yield, +rare-spawn visibility, +harvest speed.
    Techniques: Green Thumb (double common herbs) / Rare Sight (rare
    herbs glow for you) / Grafting (replant a rare node once/day).
21. Mining - Curve: +yield, +vein sense, +crit-ore chance. Techniques:
    Deep Scan / Precision Strike (extract without shattering gems) /
    Seam Sense (bonus rare veins in new dungeons).
22. Woodcutting - Curve: +yield, +special-wood identification. Techniques:
    Clean Felling / Witchwood Whisper (sense rare trees) / living-wood
    crafting technique.
23. Hunting/Skinning - Curve: +part quality, +pelt integrity, +track
    reading. Techniques: Trophy-Taker (double rare parts) / Tracker's
    Eye (see beast trails) / Butcher's Speed.
24. Gem Crafting - Curve: +cut quality, +facet bonus odds. Techniques:
    Flawless Cut / Star-Cutting (star-gems) / Setting Mastery (jewelry
    enchant slots).
25. Fishing - Curve: +bite rate, +rare-catch odds, +reel speed.
    Techniques: Stillwater / Deep-Line (rare swamp/sea catches) /
    Trophy Angler.

UTILITY/SOCIAL:
26. Stealth - Curve: +move-silently speed, +detection radius shrink,
    +backstab damage. Techniques: Shadow Meld (stand-still near-invisible)
    / Ghost Step (one silent dash) / Silent Takedown.
27. Lockpicking - Curve: +pin forgiveness, +speed, -noise. Techniques:
    Feel for the Pins (auto-open common locks) / Trap-Sense / Master's
    Hand (open one hard lock per day).
28. Speechcraft - Curve: +price favor, +intimidation odds, +persuasion
    depth. Techniques: Silver Tongue (better sell prices) / Iron Word
    (intimidate unlocks new dialog options) / Rumor Broker (extra tavern
    rumors per day).

## The Spend-vs-Unlock Answer (framework)
- NOTHING is bought with points; everything is EARNED by use.
- Character-level STAT points (5/level, locked) remain the only manual
  allocation in the game - they go to the nine stats, never to skills.
- Choices at tier-ups are the skill system's only decisions: pick
  techniques (permanent), shaping a build through play, not menus.
- This keeps the Morrowind promise ("you are what you do") while giving
  players meaningful forks at 5 moments per skill (tiers 2-5).

## Locked Mechanics (2026-09-11, Nicko's rulings)
1. RESPEC: NEVER. Technique choices are permanent for the character.
2. GEAR GATES: by TIER, not raw rank (proposal adopted).
3. TECHNIQUE MENUS: 2-3 options per tier (proposal adopted).
4. RANK DECAY: NONE. Skills never decay from disuse (Morrowind rule).
   Decay would also silently break specialty titles that read tiers.
5. RANK CURVE: LOCKED - diminishing after 50 (see below).

## The Rank Curve (locked with Nicko, 2026-09-11)
DIMINISHING AFTER 50, adopted:
- Ranks 1-50 rise at full speed.
- Above 50 the effort-per-rank grows progressively: roughly 2x slower by
  rank 75, roughly 3x slower by rank 95.
- Grandmaster feels genuinely earned; degenerate grind-farming of one
  skill is blunted; tier-ups (25/50/75) still arrive at a good pace.
- Tuning target: a focused player reaches Grandmaster in their main line
  within one normal playthrough.