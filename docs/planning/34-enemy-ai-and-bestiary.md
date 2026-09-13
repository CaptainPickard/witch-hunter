# 34 - Enemy AI Architecture and Slice-1 Bestiary

Status: PROPOSED (Astrabot hard-numbers pass, 2026-09-13). LOCKED by
Nicko, 2026-09-13: slice-1 bestiary scope (Bandit 180 / Rot Wolf 140 /
Grave Ghoul 220 + Rot-Mother 900) and Rot-Mother IN at slice 1 (M4
checkpoint may cut). Remaining numbers PROPOSED.

Answers G8 and G9 from 30-prototype-gap-analysis.md. Honors 04-combat-system.md's
locked grammar: enemies use the player's verbs, light-court pairs, dark-court
packs. All numbers sit on the same shared conventions as doc 33 (60 fps,
health 300-1500 player scale, damage 1-999, poise pools by weight class and
size, never by player level). Every number is PROPOSED.

## 1. Perception Model

Enemy agents read the world through three channels, one blackboard per agent,
evaluated every 0.10s (6 frames):

- SIGHT: cone 120 degrees, range per family (section 4). Detection is a
  meter, not a switch: 0-100, gain rate = 40 per second in the open at
  close range (under 5m), 20 at mid, 8 at the cone's edge. Crouched
  player, doc 04's stationary-aim stance, halves gain. Darkness is real
  (doc 02 light register): night halves all sight ranges. full line of
  sight at 100 = AGGRO.
- SOUND: actions emit noise events with a radius in meters: light attack
  4, heavy 8, roll 6, sprint footsteps 10, walk 3, doc 10's cooking and
  camp noise 12 (audio-cue meals: cooking at night invites the night
  spawn table). Sound sets detection gain to 50 minimum against agents
  inside the radius.
- DAMAGE: any hit taken sets detection to 100 on the hit source
  instantly, aggro without a roll.

## 2. Aggro, Taunt, and Target Selection

- AGGRO: at detection 100 the agent locks its first target = the source
  of the trigger (sight, loudest recent noise, or last hitter).
- TAUNT (23-expedition-followers.md Guard's "taunt-tier attention
  pulling"): a taunt is a noise-plus-threat event that forces a target
  re-evaluation roll every 1.00s (60f): an agent whose current target is
  not the taunter rolls against the taunter's threat weight. Threat
  weight = damage dealt in the last 5.00s + 50 per taunt event. Guard's
  shield-wall interpose (23) adds +100 weight. Bandits (sloppy family)
  re-roll on every taunt; disciplined soldiers resist with a stability
  stability score of 60 percent (roll fails 40 percent of the time); bosses
  do not re-roll at all: their aggro is taunt-resistant by design.
- TARGET SELECTION after aggro: lowest re-evaluation cost = nearest
  visible hostile, weighting distance 60 percent, damage-dealt threat 30
  percent, current-target stickiness 10 percent. Squires' "takes no
  aggro unless absolutely necessary" (23) is implemented as threat
  weight 0 while un-armed and fleeing.
- DE-AGGRO: target invisible and silent for 8.00s (480f) and beyond
  leash range (30m from spawn, 15m in interiors) -> return to patrol at
  walk speed, heal to full over 10.00s off-screen. No health leash
  against the player inside the leash range (souls rule).

## 3. Shared Verb Grammar (how AI uses the player's verbs)

Per 04-combat-system.md lock, every humanoid agent runs the same verb
set as the player, same costs, same frame data from doc 33:

- ROLL: identical i-frames (f12-f23 light band). AI rolls on an incoming
  attack read: probability per family (section 4), gated by a stamina
  check. Bandits panic-roll in the WRONG direction 20 percent of the
  time (doc 04's "slow reads, panic rolls"); soldiers never do.
- BLOCK: identical stamina drain and chip-poise transfer. AI blocks when
  facing the attacker and its read roll succeeds; block has the same
  120-degree facing arc as the player's.
- PARRY: soldiers only (doc 04 lock: "beasts/undead never parry"),
  smaller readable window than the player's shield parry: 0.15s (9f)
  vs the player's 0.20s (12f), telegraphed by a stance change per the
  doc 04 bake-in telegraph frame contract.
- HEAVY ATTACK and STAGGER: agents use doc 33 poise math identically;
  a staggered bandit eats the same 1.20s punish window the player does.
- STAMINA: agents carry stamina pools and can stamina-break; the player
  can pressure an enemy into break exactly as doc 33 defines it.

Difficulty knob inside fixed difficulty (doc 04's lock is on region
danger, not on per-agent sloppiness): the sloppy-to-disciplined axis is
a per-FAMILY property, never a region scaling. Bandits are sloppy,
cultists midline, faction soldiers disciplined. This is the answer to
G8's "sloppiness tiers" question and it does not violate the
fixed-difficulty lock because it is authored per spawn table, not per
player.

## 4. Pair vs Pack Tactics (the court grammar)

- LIGHT-COURT PAIRS (doc 04: "shield-and-spear discipline, one blocks,
  one stabs"): spawn in exactly 2. The shield agent holds front (blocks,
  bash on approach), the spear agent holds a 2.5m offset at 90 degrees,
  attacks only when the shield partner has aggro (guarding behavior).
  If one dies the survivor switches to pack-retreat logic (section 5)
  unless officer-tier. Paladin officers add doc 17 kit: Light Ward on
  approach, Blessed Bolts at range (doc 04 lock).
- DARK-COURT PACKS (doc 04: "bleed-and-retreat rhythm"): spawn in 3-5.
  Ring behavior: agents keep a 4m spacing ring, exactly one commits per
  1.5s window while the rest strafe (the bleed rhythm), attack from the
  target's rear arc when the ring arc is over 50 percent rear-facing.
  After a pack member dies the pack's rhythm tightens (commit windows
  1.0s). Vampire raiders run the doc 04 corruption kit: Blood Tithe
  self-heal, Veil of Mist escape reset when pack drops below 50 percent.
- BEASTS: no block, no parry, dodge-equivalents (leaps, sidesteps) at
  high probability, high poise (doc 04 lock). They fight solo or in
  wild packs with no ring discipline: pure spacing test.
- UNDEAD: no dodge, no parry (doc 04 lock): relentless walkers, heavy
  poise, zone denial via Wail/Grave Rot for their "answer" to spacing.
- RETREAT LOGIC: pack agents retreat when pack strength falls below 40
  percent and agent health below 30 percent: flee to max sight range,
  de-aggro, return with the pack at full re-grouped strength after
  30.00s. Light pairs never retreat while the pair stands; a lone
  survivor does. Bandits rout at 50 percent pack loss regardless of
  health (panic, doc 04's sloppy family). Beasts flee at 25 percent
  health. Undead never retreat: they are the relentless pressure tier.

## 5. Slice-1 Bestiary

Scope answer to G9's "which enemies at slice-1 scope": three stat blocks
plus one optional boss remix. All numbers follow doc 33 conventions. Poise
pools use doc 33 factors (weight class x size). Stamina pools follow the
player formula scale. Speed column = light-attack total time. Damage is
per light hit after nothing (raw; armor applies on the defender side per
doc 33).

### 5.1 Bandit (humanoid, sloppy, Darkwood/farmland)

The tutorial enemy. Full verb grammar, sloppy reads.

| Stat | Value |
|---|---|
| Health | 180 |
| Stamina | 80 |
| Poise | 45 (medium class, medium size: 30 x 1.5 x 1.0) |
| Light damage | 18 |
| Heavy damage | 30 |
| Poise damage per light | 12 |
| Light speed | 0.65s (39f), readable slow wind-up |
| Roll chance vs player attacks | 15 percent, 20 percent wrong-direction |
| Block chance | 30 percent |
| Parry | never (not soldiers) |
| Sight range | 25m day, 12m night |
| Aggro de-aggro leash | 30m |
| Rout threshold | pack at 50 percent loss |

Drops per doc 06 layer 1: bandit parts (tier 1 materials, coin).

### 5.2 Rot Wolf (beast, Darkwood/moors)

The spacing test. No block, no parry, dodge-equivalent leap.

| Stat | Value |
|---|---|
| Health | 140 |
| Stamina | 120 |
| Poise | 40 (light class 1.0 x wild factor 1.33: 30 x 1.33) |
| Light damage (bite) | 14, applies bleed 3/s for 5.00s (doc 33 bleed) |
| Heavy damage (pounce, 1.5x) | 21 + knockdown on hit |
| Poise damage per bite | 8 |
| Bite speed | 0.45s (27f) |
| Leap dodge probability | 45 percent vs melee, 20 percent vs arrows |
| Block / parry | never (doc 04 beast lock) |
| Sight range | 30m day, 18m night (scent: sound radius x2 vs player) |
| Pack size | 2-4, no ring discipline |
| Flee threshold | 25 percent health |

### 5.3 Grave Ghoul (undead, cemetery/moors night)

The relentless tier. No dodge, no parry, heavy poise, night-anchored.

| Stat | Value |
|---|---|
| Health | 220 |
| Stamina | 60 (never flees, rarely breaks) |
| Poise | 56 (medium class 1.5, large-ish 1.25: 30 x 1.5 x 1.25) |
| Light damage (claw) | 16 |
| Heavy damage (lunge) | 26 |
| Poise damage per claw | 10 |
| Claw speed | 0.75s (45f) |
| Roll / block / parry | never, never, never (doc 04 undead lock) |
| Zone denial | Grave Rot patch on 20 percent of heavies (doc 04 kit) |
| Sight range | 15m (blind, sound-driven: hearing radius 18m) |
| Night rule | day: buried, spawns only from disturbance (section 6) |
| Retreat | never |

### 5.4 Optional Boss Remix: the Rot-Mother (ghoul remix)

Doc 04 lock: "dungeons teach a monster pool; the boss remixes it." The
Rot-Mother is the slice-1 cemetery crypt boss: a large ghoul chassis plus
two remixed pool verbs.

| Stat | Value |
|---|---|
| Health | 900 (fixed, no scaling; doc 04) |
| Poise | 30 x 1.5 x 3.0 (boss factor) = 135 |
| Light claw | 30, poise 20 |
| Heavy (Grave Rot burst, remixed ghoul heavy) | 45 + Rot zone 6/s for 4.00s |
| Remixed pool verb 1 | Wail of Despair (doc 04 kit): 8m fear check, staggers un-blocked players 1.00s |
| Remixed pool verb 2 | summons 2 Grave Ghouls at 60 percent health (teaches the pool it came from) |
| Claw speed | 0.90s (54f) |
| Parry / roll | never |
| Phase rule | below 40 percent health, commit windows shorten to 0.9s |

Teaching goal: the fight drills poise-breaking (135 pool rewards Blunt),
zone management (Rot patches), and adds discipline (ghoul summons), all
with the pool's own verbs. This is the G9 boss-remix grammar in data
terms: remix = same pool stats, size factor 3.0, two kit verbs re-costed.

## 6. Spawn Table for the Slice Biome (Darkwood edge + cemetery crypt)

Per-biome encounter composition, doc 03's Darkwood forest and its
cemetery sites. Day/night per doc 03's affinity-relative clock (good
player's night = dangerous half).

| Site | Day composition | Night composition |
|---|---|---|
| Darkwood road patrol | 1-2 Bandits | 2-3 Bandits + 1 Rot Wolf |
| Darkwood deep woods | 1 Rot Wolf + 1 Bandit | wolf pack 3-4 |
| Cemetery surface | 0-1 Grave Ghoul (disturbed graves only) | 2-3 Grave Ghouls |
| Cemetery crypt (dungeon) | ghoul pool per room, 1-2 each | +1 ghoul per room, Rot-Mother at depth |
| Camp ambush check | doc 09 night events: 1-2 wolves or bandits, roll on camp site risk | same, +1 strength |

Night/ambush rules:
- Night spawn multiplier: night tables add +1 agent per encounter and
  sight ranges halve (section 1), which is the ambush enabler: you see
  them at 12m, they see you at 25m against your torch (torch radius
  light override: 20m both ways inside torch light, doc 02's scarce
  light register).
- Ambush spawn: night agents spawning within 18m of an unaware player
  enter with detection pre-set to 60 and attack from the player's rear
  arc when the rear arc is not facing them. Doc 10's HUNTER'S DARKBREAD
  "+early audio cue on night ambushes" reads as: the audio cue fires
  2.00s before the ambush spawn resolves.
- Doc 03's Veil-Tide VEIL-CHARGED fronts extend undead/wolf clock edges
  into dusk/dawn (locked doc 03): mechanically, night tables run from
  19:00 to 07:00 instead of 21:00 to 05:00 during VEIL fronts.
- Fixed difficulty: none of these tables scale with player level (doc 04
  lock). Deep-woods and crypt tables are simply deadlier places.

## 7. Open Items for Nicko

1. Three-block slice bestiary + one optional boss remix (section 5):
   scope LOCKED by Nicko, 2026-09-13: Bandit 180 / Rot Wolf 140 /
   Grave Ghoul 220 health + Rot-Mother 900.
2. Bandit rout at 50 percent pack loss: PROPOSED, flavor for the sloppy family.
3. Rot-Mother as the slice-1 boss: IN at slice 1, LOCKED by Nicko,
   2026-09-13 (docs 31/34); the M4 checkpoint can still cut it for
   scope.
4. Darkbread audio cue timing 2.00s: PROPOSED, cross-doc 10 dependency.