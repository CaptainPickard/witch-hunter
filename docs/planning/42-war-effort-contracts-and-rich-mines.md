# 42 - War Effort Contracts and Rich Mines

Status: PROPOSED, IO bake from Nicko session directives 2026-09-14,
pending Nicko review. Rulings 1-2 below are LOCKED in session; every
number, name, and percentage in the parts below is PROPOSED unless
marked otherwise.

## SESSION RULINGS (locked by Nicko, 2026-09-14)

1. WAR EFFORT CONTRACTS: hold-level supply contracts where the player
   is tasked with delivering a number of FINISHED armors or weapons to
   a local hold for a substantial sum. Contracts name item class,
   quantity N, and a quality/tier bar. The more you make and bring,
   the higher the reward: over-delivery pays escalating per-item
   rates (Part 2). This is the hold-scale extension of doc 05's
   requisition contracts (which stay the small repeatable tier).
2. DEDICATED RICH MINES (locked as direction): dedicated mine sites
   across the map carrying LARGE quantities of minerals and ores,
   mineable at volume. Authored as a doc 41 Family 6 (Riches Sites)
   extension (Part 5); doc 41 carries the site grammar, this doc the
   economy. Rich mines are the natural supply chain into war effort
   contracts.

## CONVENTIONS

- Requisition lineage (doc 05, locked): faction crafting requisitions
  are repeatable contract quests paying standing + coin; standing
  gates requisition tiers; requisitions are also a recipe source.
  War effort contracts INHERIT: same standing economy, hold-scale
  quantities, war-keyed why-now.
- Why-now grammar (doc 20, locked): quests are reactions, not rolls.
  A war effort contract exists because a hold is preparing for a
  siege (doc 13), replenishing after one, or feeding a court's
  campaign (doc 12). Never ambient.
- Gear derives from docs 33/39/40: item class per doc 33 section 3,
  tier per the material ladders, grade per the doc 05 craft ladder.
  Contracts pay for GRADE, which makes secondaries and station
  ceiling matter: the quality bar is where crafting skill cashes out.
- Currency: Silver Marks (doc 35, locked). All coin figures PROPOSED
  tuning.
- Region tier bands (docs 06/39/40): a hold's contract tier band
  matches its region (farmland holds ask T1-T2, mountains T3-T4,
  blight-adjacent T4-T5). Never a T5 ask of a T2 hold.
- The quest frame grammar (doc 20): patron + need + site + resolution.
  War effort contracts are frames with a QUANTITY axis added.

## PART 1 - CONTRACT ANATOMY

Every war effort contract names:

| Field | Source of truth |
|---|---|
| HOLD | doc 13's holds; the local quartermaster or castellan is the patron |
| COURT | the holding court flavors the ask (doc 12): light asks warded gear, dark asks tainted, neutral pays pure coin |
| ITEM CLASS | one weapon class (doc 33 section 3) or one armor class (doc 40 weight class); armor contracts name class, not slot (any of the 4 slots qualifies) |
| TIER BAR | minimum tier per the hold's region band; higher-tier deliveries count double toward N |
| GRADE BAR | minimum grade (default STANDARD/Fine band; premium contracts demand Superior+) |
| QUOTA N | base quantity (PROPOSED 5-20 by tier) |
| DEADLINE | in-game days (PROPOSED 7-15); expiry refunds nothing, the why-now passed |
| REWARD | coin ladder + standing + court perks (Part 3) |

Quality rule: a delivery item must MEET the tier and grade bars.
Items above the bar (higher tier, higher grade) are accepted and pay
more per item (Part 3 ladder). Masterwork deliveries always qualify
and always pay premium: Masterwork's +1 enchant socket (doc 05) makes
war-effort Masterwork pieces the court's preferred issue.

## PART 2 - THE REWARD LADDER (more made and brought = higher reward)

Per ruling 1: over-delivery escalates. Three payout bands, all
PROPOSED numbers for GDD tuning:

| Band | Delivery | Payout rule |
|---|---|---|
| Quota | exactly N at bar | base coin per item (PROPOSED: ~120-160% of the item's vendor value) + contract standing |
| Over-delivery | N+x (same contract window) | each item beyond N pays an ESCALATING per-item bonus (+10 percent per item over quota, PROPOSED, cap +100 percent) |
| Ladder repeat | after resolution, the contract re-posts at N+50 percent quota (cap 3x base) and +15 percent base pay per repeat (PROPOSED), standing gates the repeat tiers (doc 05 inheritance) |

Standing effects (doc 05/06 inheritance): completing a war effort
contract grants court standing scaled to quota tier; three resolved
contracts at a hold unlock that hold's REQUISITION STONE tier-up
(doc 37's boards), which posts bigger contracts. Court requisition
contracts (doc 05's small tier) stay available alongside: war effort
is the big brother, not a replacement.

WAR-STATE MULTIPLIER (doc 13 coupling): a hold under SIEGE PREP
multiplies demand: quota N doubles, pay x1.5, and the contract window
shortens. A hold that RESOLVED a siege recently posts REARMAMENT
contracts (replacement gear, standard pay, longer window). War scars
(doc 41 family 8) are the visible evidence of why the contract
exists.

## PART 3 - SOURCING SYNERGY (the mines-to-muster loop)

The intended loop per ruling 2: rich mine trips feed the smelting
stock, the smelting feeds contract batches, the batches feed the
hold's war, the war generates new contracts and opens new territory.

- Mountains rich mines (Part 5) supply steel/cold iron volume for
  T3-T4 weapon contracts; moor barrow silver feeds T2 silvered armor
  contracts; blight ore-scars feed the T5 Grandmaster endgame
  contracts (dark-court only, doc 06 dark vendors' raw-only rule
  still gates purchase vs mining).
- Court flavors shape demand: light courts order warded/holy-adjacent
  gear (accepts only axis-clean pieces), dark courts accept tainted
  pieces, neutral brokers pay slightly less coin but buy ANY piece
  and never ask about the axis (PROPOSED: neutral quartermasters at
  bandit-friendly holds).
- Contract volume makes Disassembly (doc 05, line 29) a quality
  engine: batch-craft, disassemble the below-bar rolls, re-refine the
  raws into the next attempt. The anti-exploit rule (raw-only
  returns) keeps this a cost, not a profit loop; its value is grade
  rerolling.

## PART 4 - OPEN QUESTIONS

1. [08 TRACKER] RESOLVED 2026-09-14 (Nicko): pay bands and escalation
   caps handed to GDD tuning per the doc 39/40 anchor precedent.
2. [08 TRACKER] RESOLVED 2026-09-14 (Nicko): surplus CARRIES AT HALF
   VALUE into the re-posted contract's quota (each stockpiled
   above-bar item counts as half an item toward the next posting).
3. [08 TRACKER] RESOLVED 2026-09-14 (Nicko): neutral quartermasters
   CONFIRMED: neutral/bandit holds run war effort contracts at
   slightly lower pay, buy ANY piece regardless of axis, and never
   run an axis check. Their contracts pay coin only, no standing.
4. [08 TRACKER] Contract boards physical persistence: war effort
   postings inherit doc 37-C11's stable-ID board rules; confirm
   no separate treatment needed.

## PART 5 - DEDICATED RICH MINES (ruling 2)

Authored as doc 41 Family 6 extension; the ruling and site list below
are the spec, doc 41 carries the site-state/discovery grammar.

- WHAT: dedicated mine SITES (not ambient veins) with LARGE ore
  quantities: dense vein clusters worth many mining trips, the
  destination-tier version of doc 06's ambient nodes (same grammar as
  riches sites: DENSE, not different-mechanic; deplete and recover on
  doc 06's 2-3 day node timers, with the site's DENSITY making the
  trip worthwhile).
- WHERE (per-biome, PROPOSED placements at GDD): mountains carries
  the deepest (steel, cold iron strata, gem seams per doc 39's
  depth-gated tiers); moors barrow-adjacent silver seams; blight
  ore-scars (blacksteel, Rare/Named territory rules apply); darkwood
  and swamplands carry small iron/seam sites (T1-T2 volume); farmland
  carries one worked quarry (iron + stone, the safe starter mine).
- WHO: rich mines are WORKED sites with light state (doc 41 Part 2):
  some INHABITED by garrisons or dwarf clans (safe, court-keyed),
  some HAUNTED or CONTESTED (the ore is why the fight is there).
  Clearing a contested mine is itself war-effort-adjacent work (doc
  13).
- GEM SYNERGY: mountain rich mines carry the doc 39 gem system's
  richest vein tiers (ruling 3 of doc 39: depth and region band gate
  gem tier; mountains richest).
- DISCOVERY: tier 1 rumor-revealable (doc 41 Part 4: miners talk).