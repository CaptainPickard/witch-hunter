# 07 - Leveling and Progression

## Decisions (locked with Nicko)
- Human-centric world: no fantasy race selection at character creation. Class
  template presets remain the origin mechanism. LOCKED.
- Stat list: NINE stats (locked 2026-09-11): Health, Stamina, Focus (mana
  pool), Carry Weight, Precision (crit), Ward (resist), Speed, Luck (item
  drops/rng rolls), Wisdom (magic damage + mana). 5 STAT POINTS PER LEVEL.
  LOCKED.
- Skill scope (revised): 28 CORE skill lines - 9 combat, 5 magic schools,
  5 crafting, 6 gathering, 3 utility/social (Stealth, Lockpicking,
  Speechcraft). The old "~25 budget" was a FLOOR, not a ceiling: unlockable
  specialties (doc 16) expand upward. Luck and Charisma are stats; the
  trainable social skill is Speechcraft. LOCKED.
- Healing: potions plus healing spells (found mid-to-late game). Taverns are
  the save/respawn points (see 04-combat). LOCKED.
- NG+ (locked): available after ANY ending; all NG+ runs keep the warp camp
  while the world resets to an even good/evil match with fresh procedural
  outcomes; only the Third Path NG+ lets the player re-choose their stance;
  aligned-ending NG+ locks the run to that court and tilts the world toward
  the enemy court (much stronger enemy, slightly weaker aligned court); the
  Third Path NG+ amplifies BOTH courts evenly. Full spec in doc 12.

## Core Philosophy
Morrowind-style skill-by-use, generalized: you are good at what you
specialize in, and increasingly bad at what you neglect. A single playthrough
cannot master everything. Builds are declarations of intent - now formally
expressed as: stats (spent points), skill lines (earned by use), techniques
(permanent tier-up choices), and specialty titles (lapable identities, doc
16).

## Two-Layer Model
Layer 1: Character level (XP-based, "stat points")
- Everything earns XP: kills, quests, crafting, gathering, discovery.
- Character level grants 5 stat points to allocate across the nine stats
  (list locked above).
- Stat points are the "customize your build" knob; skill tiers are the
  "play into your skills" knob. Both matter and neither substitutes for
  the other.
- Character level does NOT directly scale combat power (Morrowind-style:
  stats and skills are the power sources; the level number is a point
  budget, not a damage stat). CONFIRMED as design lean - the anti-grind
  answer is the doc 18 rank curve, not level scaling.

Layer 2: Skill lines (use-based leveling - FULL MECHANICS IN DOC 18)
- 29 core lines (list in 15-skill-lines.md; Disassembly added as line
  29, 2026-09-14). Skills level by doing the
  thing, never by spending points.
- Ranks 1-100 by use; each line has a primary passive curve (per-rank
  improvements specific to that line - damage/speed for weapons, potency
  for alchemy, yield for gathering).
- Five tiers bracket the ranks: Novice/Apprentice/Adept/Expert/
  Grandmaster (25/50/75/100). TIER-UP is the meaningful event: pick ONE
  technique from a 2-3 option menu (offensive/utility/specialist per
  menu); choices are PERMANENT, no respec.
- Rank curve: diminishing after 50 (roughly 2x slower by 75, 3x by 95);
  Grandmaster is earned, grind-farming blunted, tier-ups still arrive at
  a good pace. No rank decay. LOCKED.
- GEAR GATES read TIERS: Tier-2 gear needs Apprentice, Tier-3 Adept,
  Tier-4 Expert, Tier-5/named Grandmaster. LOCKED.

## Skill Growth Effects
Higher skill = faster and stronger: attack speed, damage, stamina
efficiency, harvest yield, craft quality, cast power - line-specific
curves are defined per line in doc 18. The compounding loop: use the item,
level the skill, unlock better items and stronger outputs, push further.

## Specialization Pressure
- The doc 18 rank curve rewards focus (the slow zone above rank 50 punishes
  spread builds by math, not by penalty).
- Gear gates by tier (locked) mean a spread build physically cannot wear
  the specialist's kit.
- Magic: school tiers gate spell tiers (doc 17 acquisition model); Holy
  Wards and Dark Pacts are additionally axis-gated (tomes burn in the
  wrong hands).
- Specialty titles (doc 16) reward skill COMBINATIONS: 2-4 lapable titles
  at endgame, with apex specialties (deep specialization unlocks exclusive
  questlines like the Lich King chain). Titles show their retention
  conditions in the character menu.

## Progression Loops Summary
- Fight -> combat skill XP + loot + monster parts -> craft better -> fight
  deeper.
- Gather -> gathering skill XP + materials -> craft/potions -> sell or use
  -> afford better gear.
- Explore -> discovery XP + loot + recipes + tomes -> unlock regions,
  factions, and spells -> access rarer resources.
- Politick -> deeds move the moral axis and court standing -> unlock
  factions, titles, and specialties -> the world's map and courts respond.
- Everything you do earns XP somewhere and moves identity somewhere.
  Nothing is wasted time; everything is a build choice.

## Character Creation
- Human-centric world (LOCKED): no fantasy race selection. The player's
  first-and-last name IS their eventual house name (doc 14: founded clans
  bear the character-creation name).
- Class template presets (e.g. Witch Hunter, Duelist, Occultist, Ranger,
  Knight) set starting skill ranks - but pure playstyle-based growth means
  presets are suggestions, not prisons (Morrowind rule).

## RULING PASS (open-questions sweep, 2026-09-14, Nicko)
XP BUDGETS, STAT-POINT CAPS, STAMINA/REGEN, PARRY WINDOWS: HAND TO
GDD TUNING. All stay PROPOSED working numbers, tuned only against a
playable build. Doc 07's frame stands, numbers wait.
## Open Questions (current state - first-draft questions resolved)
- Stat list and budget: RESOLVED (9 stats, 5 points/level).
- Skill count: RESOLVED (29 core + specialties upward; Disassembly
  added 2026-09-14 as line 29).
- Level-power coupling: RESOLVED (stats only; level is a point budget).
- Skill anti-grind: RESOLVED via doc 18 rank curve (diminishing after 50),
  not XP decay.
- NG+ : RESOLVED (doc 12; all endings, camp persists, world resets, tilt
  rules by ending).
- XP budget per level (how much XP a character level costs): GDD-stage
  tuning.
- Stat-point cap / diminishing on stats themselves: GDD-stage tuning.