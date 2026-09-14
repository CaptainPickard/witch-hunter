# 33 - Equipment Mechanics and Combat Formulas

Status: PROPOSED (Astrabot hard-numbers pass, 2026-09-13). LOCKED by
Nicko, 2026-09-13: two talisman slots (section 5), flat-ladder plus
percent-cap armor model (section 6), crit cap 30 percent (section 7).
Remaining tuning PROPOSED.

Extends 27-equipment-visual-system.md into the mechanical layer and answers
G6 and G7 from 30-prototype-gap-analysis.md. Every number is PROPOSED
tuning. Shared conventions: frame data at 60 fps, durations in seconds to
2 decimals plus frame count, player health 300-1500 across progression,
stamina 80-160, damage integers 1-999 per hit, stats 1-99, tiers T1-T5,
grades C/B/A/S.

## 1. Canonical Mechanical Slot List

The mechanical slot list is the doc 27 equipment slot list plus three
combat-only slots. Doc 27's CANON LAYERS (linen base, leg harness, faulds,
gorget) are never slots and never carry stats, per the doc 27 amendment.

| Mechanical slot | Carries | Doc 27 visual mapping |
|---|---|---|
| HEAD | helm/hood armor value | HEAD layer |
| CHEST | cuirass armor value, poise bonus | TORSO layer |
| HANDS | glove armor value | ARMS layer (optional visual, mandatory slot) |
| BACK | cloak armor value (light only), quiver if archer | BACK layer |
| MAIN HAND | weapon | WEAPON layer, right anchor |
| OFF HAND | weapon or shield or empty | WEAPON layer, left anchor |
| BELT | potions/consumables, no stats | new slot, no doc 27 layer (hidden) |
| TALISMAN x2 | charms/trinkets | new slots, no doc 27 layer (see 6) |

The HANDS slot always exists mechanically even though doc 27 marks the ARM
layer optional visually; ungloved hands are armor 0. BELT and TALISMAN are
mechanical-only, no sprite layer, zero art cost under the doc 27 pipeline.
Total: 9 mechanical slots, 2 of them talisman.

## 2. Armor and Weight Per Slot

Armor is a flat damage reduction. Weight feeds EQUIP LOAD (section 8).
Values are for grade B; grade multiplies armor the same way it multiplies
damage (section 5). Light/medium/heavy per 05-crafting-system.md
Armorsmithing weight classes.

| Slot | Light armor (armor/weight) | Medium | Heavy |
|---|---|---|---|
| HEAD | 1 / 1.0 | 2 / 2.0 | 4 / 4.0 |
| CHEST | 3 / 3.0 | 5 / 6.0 | 8 / 10.0 |
| HANDS | 1 / 1.0 | 1 / 1.5 | 2 / 3.0 |
| BACK | 0 / 0.5 | 1 / 1.0 | 1 / 2.0 |
| Full set | 5 / 5.5 | 9 / 10.5 | 15 / 19.0 |

Flat armor never exceeds 15; percentage reduction lives on Ward and
enchant wards (doc 17), keeping armor a small constant and scaling pressure
on tiers. Tier multiplies armor by the same ladder as damage (section 5):
a T4 heavy chest is 8 x 2.2 = 17.6 -> 17 armor alone.

## 3. Weapon Class Table

Nine classes per 04-combat-system.md. Baselines are T1, grade B, skill
rank 1. Damage is the light-attack base; heavy = 1.5x damage and 2.0x poise
damage. Stamina is the light-attack cost; heavy costs 1.7x. Poise damage
per light hit. Speed is light-attack total time (wind-up + active +
recovery) at 60 fps. Reach is a range band, meters.

| Class | Damage | Stamina | Poise dmg | Speed | Reach | Identity (04) |
|---|---|---|---|---|---|---|
| Short Blade | 12 | 8 | 10 | 0.42s (25f) | 1.5 | fast, crit |
| Long Blade | 20 | 12 | 16 | 0.55s (33f) | 2.5 | balanced arcs |
| Blunt | 22 | 15 | 26 | 0.70s (42f) | 2.0 | stagger |
| Axes | 24 | 14 | 20 | 0.68s (41f) | 2.0 | bleed |
| Polearms | 18 | 12 | 16 | 0.62s (37f) | 3.5 | reach |
| Archery | 16 | 10 | 8 | 0.80s draw (48f) | ranged | dual-mode aim |
| Dual Wield | 9 + 9 | 16 | 12 | 0.50s (30f) | 1.8 | combos |
| Shield (bash) | 8 | 10 | 30 | 0.60s (36f) | 1.2 | block/parry |
| Unarmed | 7 | 5 | 8 | 0.38s (23f) | 1.0 | cheapest |

Bleed (Axes) is 3 damage per second for 5.00s (300f) per stack, max 3
stacks. Blunt poise numbers are deliberately double Short Blade's; doc 04
locks "heavies and Blunt weapons melt" poise.

## 4. Two-Hand and Off-Hand Rules

- Any Main Hand weapon can be gripped two-handed: +25 percent damage,
  +25 percent poise damage, x1.3 stamina cost, and the Off Hand slot
  must be empty. Two-handing a Long Blade T1 B: 20 -> 25 damage.
- Shields cannot be two-handed. Bows and crossbows are inherently
  two-handed (their table row already assumes it).
- Dual Wield requires both hand slots filled with one-hand weapons
  (Short Blade, Long Blade, Blunt 1H, Axes 1H). Off-hand attacks deal
  60 percent of the off-hand weapon's damage and use the Dual Wield row
  timing. Class damage baselines above are Main Hand values.
- Off Hand occupied (shield or weapon) while not dual-wield skilled:
  the off-hand adds only its block/parry function, no attacks.
- Doc 04 rule holds: dual-wielding levels Short Blade, Long Blade, AND
  Dual Wielding when the pair is dagger + longsword.

## 5. Jewelry, Charms, Trinkets

LOCKED by Nicko, 2026-09-13: two TALISMAN slots, no rings/amulets
beyond them.
Rationale: doc 05 Enchanting already binds "warded charms" and Gem
Crafting cuts jewelry; two slots give builds a home without a full RPG
jewelry grid, and both slots are mechanical-only (no art layers). A
talisman carries ONE passive (doc 05 charm grammar: stat bonus, resist,
or an active with a cooldown). Charms are Enchanting products; plain
jewelry is vendor loot. Cap: 2 talismans, belt slots are consumables
only, no stat-bearing rings.

## 6. The Damage Formula

Attacker side:
- W = weapon base damage (section 3) x tier multiplier x grade multiplier
  x skill multiplier.
- Tier multiplier: T1 1.00, T2 1.35, T3 1.75, T4 2.20, T5 2.70.
- Grade multiplier: C 0.90, B 1.00, A 1.10, S 1.20 (grade ladder from
  05-crafting-system.md Crude/Standard/Fine/Superior/Masterwork mapped to
  C/B/A/S for combat math).
- Skill multiplier = 1 + 0.003 x weapon-line rank (rank 1-100, doc 18
  rank curve governs how fast rank rises, not the multiplier).
- Two-hand: x1.25 on the total. Heavy attack: x1.50 on the total.

Defender side, then flat, then percent:
1. Percent reduction: Ward. Damage x (1 - ward fraction) where ward
   fraction = min(0.60, Ward stat x 0.005) vs spells and magic-tagged
   hits; physical hits use enchant wards only (doc 17 armor wards).
2. Flat reduction: armor. Damage x 0.15 floor keeps chip damage alive:
   final = max(floor(raw x 0.15), raw - flat armor).
3. Round to integer, minimum 1. Single hits cap at 999.

Worked: T2 grade B longsword, Long Blade rank 40:
raw = 20 x 1.35 x 1.00 x 1.12 = 30 (rounded). Vs a bandit with flat
armor 5: max(30 x 0.15, 30 - 5) = 25 health damage. The same hit vs a
T4 knight, flat armor 17: max(4, 13) = 13. Armor is why T2 gear feels
dead in endgame zones while never doing zero (04's fixed difficulty).

## 7. Critical Hits (Precision)

- Crit chance = 5 + Precision x 0.25, capped 30 (cap LOCKED by Nicko,
  2026-09-13). Precision 16 -> 9 percent. Precision 99 -> 29.75 -> 29
  percent.
- Crit multiplier = 1.5 + Precision x 0.005. Precision 16 -> 1.58.
- Crits apply to health damage after armor. Guaranteed crits (doc 04:
  Deadeye headshots, Sharpshooter's Calm openers, Fang Flurry on
  staggered foes) skip the chance roll, use the same multiplier.
- Short Blade's primary curve (+damage, +attack speed, doc 18) stacks
  with this; Assassin's Doctrine armor-pierce reads as ignoring the
  flat armor step.

## 8. Stamina, Poise, Equip Load

Stamina pool = 80 + Stamina stat x 0.8 (stat 25 -> 100, stat 99 -> 159).
Regen: 25 per second idle/walking, paused 1.00s (60f) after any stamina
action, 50 percent while blocking, near-zero while attacking, per doc
04's proposed exacts. Costs: table in section 3; roll = 22; block hit =
10 + 2x incoming poise damage. At 0 stamina the player is
STAMINA-BREAKED: 1.50s (90f) no-action window (04 lock).

Poise pool = 30 x armor weight class factor x size factor. Factors:
light 1.0, medium 1.5, heavy 2.2; size: small 0.8, medium 1.0, large
1.6, boss 3.0. Medium human = 45 poise. Poise regen: full pool after
4.00s (240f) without taking a poise hit (04: "a few seconds"). Poise
broken = stagger, 1.20s (72f) committed recovery. Blocked hits transfer
30 percent of poise damage (04 chip poise lock).

Equip load bands (04's three roll speeds), sum of section 2 weights:
- LIGHT: 0-10.0. Fast roll: 0.50s (30f), 22 stamina, i-frames 0.20-0.38s
  (f12-f23, 11 frames).
- MEDIUM: 10.1-20.0. Standard roll: 0.62s (37f), 26 stamina, i-frames
  0.20-0.30s (f12-f18, 6 frames).
- HEAVY: 20.1-30.0. Slow roll: 0.80s (48f), 32 stamina, i-frames
  0.20-0.25s (f12-f15, 3 frames). Above 30.0 the roll is disabled.
Carry Weight (inventory stat, doc 06) is separate and does not touch
these bands.

## 9. Focus Cost Scaling

Focus pool = 50 + Wisdom x 4 (Wisdom 20 -> 130). Spell cost = base x tier
factor x rank discount. Base costs: bolt-tier spells 8, control 12,
charge-up 20, ultimate 30. Tier factor: T1 1.00, T2 1.40, T3 1.80, T4
2.30, T5 2.90. Rank discount = 1 - 0.002 x school rank (max 20 percent
off at 100). Worked: Ember Lance (T3 charge-up, doc 17) = 20 x 1.80 x
0.94 = 33.8 -> 34 Focus at rank 30 Pyromancy. Firebolt stays 8 x 1.00 x
0.94 = 7.5 -> 7 (round half down: casters never pay odd cents). Spell damage uses section 6 with W = spell base
damage and the school rank multiplier replacing weapon skill; spells and
weapons share one health scale by construction.

## 10. Level-Up Stat Curve

Doc 07 locks 5 stat points per level, 9 stats, level number carries no
power. Proposed stat-point curve for the 300-1500 health span: points
per level = 5 flat (locked), XP to level = 100 x level^1.6 (GDD
tuning). A build spending 12 points in Health gets health = 300 + 12 x
12 = 444 at level 30; full Health investment (99) reaches 300 + 99 x 12
= 1488, inside the 300-1500 convention. Stamina stat 99 -> 159 (cap
160). All other stats buy linear per-point gains through the formulas
above; no stat has a hidden curve. Enemy numbers never read player
level (04 fixed difficulty).

## 11. Worked Combat Example, End to End

Player: level 30 Witch Hunter preset. Stats: Health 30, Stamina 25,
Focus 20, Precision 16, Ward 10, Wisdom 20, Carry Weight 30, Speed 10,
Luck 15. Health 660, stamina 100, Focus 130, crit 9 percent at x1.58.
Gear: T2 grade B longsword (Main Hand), medium chest+hands+head (flat
armor: medium CHEST 5 + HANDS 1 + HEAD 2 = 8), medium equip load 10.5
-> MEDIUM band. Long Blade
rank 40. T2 B longsword damage 27 (20 x 1.35 x 1.00), skill x1.12 ->
30 raw light.

Enemy: Darkwood bandit (doc 34 block): health 180, flat armor 5, poise
45, stamina 80.

Sequence at 60 fps:
1. Light attack, 0.55s. Raw 30, after armor 25 health, 18 poise.
   Bandit 155 health, 27 poise.
2. Light attack: 25 health, 18 poise. Bandit 130 health, 9 poise.
3. Bandit heavy (36 poise damage incoming): player rolls (26 stamina,
   6 i-frames) then blocks the follow-up light: 10 + 2x9 = 28 stamina,
   chip poise 30 percent of 18 = 5.
4. Heavy attack: raw 45, after armor 40 health, 36 poise. Poise breaks
   at 9 - 36: STAGGER, 1.20s punish window.
5. Punish heavy: raw 45, crit roll fails (9 percent), 40 health.
   Bandit 25 health. A crit here would deal 45 x 1.58 = 71 - 5 = 66,
   overkill.
6. Third light: 25 health, kill. Total time roughly 6.2 seconds,
   stamina spent 12+12+26+28+20 = 98 of 100, one near-break, doc 04's
   intended stamina discipline.

Kill feeds doc 06 layer 1 monster/humanoid parts, XP per doc 07.

## 12. Open Items for Nicko

1. Flat-armor ladder vs percent-ladder mix (section 6): the flat ladder
   plus percent cap armor model is LOCKED by Nicko, 2026-09-13
   (ruling 14: flat ladder + percent cap as proposed). Any mix-nuance
   tuning inside the model stays open as PROPOSED.
2. Two talisman slots (section 5): LOCKED yes by Nicko, 2026-09-13.
3. Crit cap 30 percent: LOCKED by Nicko, 2026-09-13.
4. Stamina-break window 1.50s: PROPOSED, tuning.

## RULING PASS (open-questions sweep, 2026-09-14, Nicko)
CROSSBOW SUBCLASS: EXISTS. Doc 33's Archery class gains a crossbow
subclass with its own identity: slower reload cadence, higher
per-shot poise damage than bows. Same locked hard-number conventions
(60 fps, doc 33 formulas apply unchanged). Catalog rows go to doc 39;
verb grammar (doc 04) unchanged.