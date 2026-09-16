# 51 - Bestiary Encounters GDD

Status: Drafted 2026-09-16, bestiary/encounter GDD pass (doc 04 grammar and doc 34 pools govern; content authored). PROPOSED for Nicko review. Subordinate to locked rulings; conflicts are open questions.

Scope note: this doc authors enemy pools and encounter tables. It invents no
combat mechanics, no corruption kits, and no verb grammar. Doc 04 and doc 32's
frame data govern; doc 17's three kits are locked; doc 34's pools and doc 41's
families govern. Identity and ledger rules apply to every lore-flavored line
below (constraint 4).

## IDENTITY AND LEDGER COMPLIANCE (whole-doc rule)

- Signer = the witch's mask (spec constraint 4). See open question 1 vs doc
  19's superseded ruling; this doc does not resolve it.
- Pale Queen = a separate neutral vampire leading the brokers.
- Light queen = Queen Maren of the Dawn.
- Ledger compliance: NO entry in this doc states or implies the creditor's
  identity. No enemy dialogue, flavor line, or bestiary note names the
  creditor, quotes the debt's terms, or dates the pact from the debtor's side.
  Enemy text may reference "the pact," "the Veil," "the tithe" as witnessed
  facts only. Doc 44 Part 2 governs.

## Section 1: FACTION ENEMY POOLS

Every entry: name, race corruption kit (doc 17 model where applicable), verb
grammar subset of doc 04, spawn context, tier band, taint or debt texture.
All stats PROPOSED. All stats reuse doc 33/34 conventions (health 300-1500
player scale for elites, poise = 30 x weight class x size factor x boss
factor where boss, fixed difficulty: no level scaling).

### 1.1 Light court forces (paladins, human and light-elf houses)

Race: humans (doc 14) and light-aligned elves (houses: Silvermoon, Dawnmere,
Elderbough). Kit: NONE. Their "kit" is the Holy Wards school made hostile
(doc 04 lock), not a corruption kit.

| Entry | Kit | Verb grammar (doc 04) | Spawn context | Tier band | Texture |
|---|---|---|---|---|---|
| Dawnward Shield-Guard | none (Holy Wards grammar) | light, heavy, roll, block, parry (soldier) | light-held land patrols, purge parties | T2-T3 | shield-and-spear pair front half |
| Dawnward Spear-Guard | none | same, polearm-flavored | paired with Shield-Guard, exactly 2 | T2-T3 | one blocks, one stabs (doc 34 pair grammar) |
| Dawnward Officer (Paladin) | none | full grammar + Light Ward on approach, Blessed Bolts at range, Consecrate, Sanctuary at officer tier | leads pairs in conquered-light holds | T3-T4 | day-sleep ambush for evil players (doc 04) |

Pair discipline per doc 34: shield holds front (block, bash on approach),
spear holds a 2.5m offset at 90 degrees, attacks only while the shield
partner holds aggro. Lone survivor switches to pack-retreat logic. Officer
tier adds the doc 17 Holy Wards kit verbs. PROPOSED that officer spawns are
1 per 3 pairs, never solo-led. All numbers PROPOSED.

Ledger texture: purge-party flavor lines reference the Militant's writ and
Queen Maren of the Dawn's banner. No entry references the debt or the
creditor.

### 1.2 Dark court forces

Race: elf-vampire houses (doc 14 dark houses: Duskmantle, Veylthorn,
Nightshroud, Ashveil) plus raised undead soldiery. Kits: doc 17's vampire and
undead kits ONLY. No new kit verbs invented; kit verbs re-used at enemy-caster
costs per doc 04's enemy-caster rule (1-3 signature spells for bespoke boss
casters).

| Entry | Kit (doc 17) | Verb grammar (doc 04) | Spawn context | Tier band | Texture |
|---|---|---|---|---|---|
| Duskmantle Vampire Raider | vampire (Blood Tithe, Veil of Mist, The Embrace, Domination Gaze) | pack grammar: light, heavy, roll, block | night ambush on good-aligned players, dark-held roads | T2-T3 | Blood Tithe self-heal, Veil of Mist reset below 50 percent pack strength (doc 34) |
| House Elder-Caster | vampire | pack grammar + 1-3 signature dark pacts (doc 17 enemy-caster rule) | anchors raider packs at territory keys | T3-T4 | Domination Gaze on retinue members mid-fight (doc 04) |
| Gravebound Raider | undead (Grave Rot, Miasma, Wail of Despair) | undead lock: no dodge, no parry | night raids, Veil-Tide fronts | T2-T3 | zone denial: Rot and Miasma patches (doc 04) |
| Wail-Caster (raider priest) | undead | undead lock + Wail of Despair morale breaks | 1 per pack on dark land | T3 | morale-break support, PROPOSED 1 per pack cap |
| Enforcer Pack-hound | none | beast grammar: no block/parry, leap dodges, high poise | dark land enforcer packs' flanker | T2-T3 | the spacing test, doc 34 beast line |

Dark-court packs per doc 34: spawn 3-5, 4m spacing ring, one commit per 1.5s
window, rear-arc bias when the ring is over 50 percent rear-facing. Pack
death tightens commit windows to 1.0s. Retreat at pack under 40 percent and
agent health under 30 percent. All PROPOSED where not already doc 34 numbers.

Debt texture: raider flavor treats the tithe as house law, never names the
creditor. House names per doc 14 only.

### 1.3 Hidden Court strains (neutral, doc 19)

Wolf kit (doc 19): Pounce, Terrifying Howl, Elder's Shape, on the doc 17
kit model applied a third time. Grammar: beast lock (no block, no parry,
leap sidesteps, high poise). The bite converts (rank-filling mechanic, doc
19); wild strains spread carelessly, the Court converts rarely and by law.

| Entry | Kit | Verb grammar | Spawn context | Tier band | Texture |
|---|---|---|---|---|---|
| Wild Wolf-Strain (feral) | wolf kit, undisciplined | beast lock | wild packs anywhere, doc 04's roaming beasts | T1-T3 | unconverted bites, no ring discipline |
| Hidden Court Hunt-Pair | wolf kit, disciplined | beast lock + Terrifying Howl opener | moon hunts, wolf-line trial adjacency | T3-T4 | hunt-any-during-moon rule (doc 19); den law: hunt alone, speak to no one of the den |
| Warden War-Party (hostile, rare) | wolf kit, disciplined | beast lock, coordinated pounces | only where the Court commits force in extremis (doc 19's ace) | T4 | PROPOSED: never a random spawn; quest-keyed or debt-default adjacency only |

Warden hostility ruling: the Court is neutral and hidden (doc 19). PROPOSED
that hostile Warden encounters outside wolf-line trials exist only at debt
default or Third Path adjacency. See open question 2.

### 1.4 Bandit camps (sloppy humanoid)

Bandit per doc 34 slice-1 block (health 180, rout at 50 percent pack loss).
Full verb grammar, sloppy reads, 15 percent roll chance, 20 percent
wrong-direction. Spawn context: Darkwood, farmland edges, road ambushes.
Tier band T1. Texture: coin and parts (doc 06 layer 1). Camps field 3-6 with
1-2 bows at PROPOSED composition: 2 melee ring + 1 archer per 3.

### 1.5 Mercenary turncoats (disciplined humanoid)

Full verb grammar INCLUDING parry (they are soldiers, doc 04 lock). Spawn
context: war scars (doc 41 family 8), pay-lapsed garrisons, conquest
aftermath. Tier band T2-T3. Discipline axis: midline-to-disciplined, resist
taunts at the doc 34 soldier stability band. PROPOSED stats: reuse soldier
frame from doc 34's disciplined read (no panic rolls), health 220 PROPOSED
band. Texture: banner-less, contract-ledgers on the body; no taint, no kit.

### 1.6 Orc companies (dark court subject race, doc 22)

Race: orcs (doc 22: post-Fall, sophisticated, own towns and cities under the
elf-vampire court). Kit: NONE (doc 17 lock admits only three kits). Verb
grammar: full humanoid set, soldier-discipline, parry YES (PROPOSED: orc
line-infantry count as soldiers for the parry lock; see open question 3).
Spawn context: orc city approaches, cavern market guards, siege-adjacent
roads. Tier band T2-T4. Texture: the scourge that became a people; war-band
mottos reference their own becoming, never the debt's authorship. Orc
war-bands run dark-court PACK grammar (3-5, ring) PROPOSED as their adopted
court grammar.

### 1.7 Pool summary counts

Light court: 3 entries. Dark court: 5 entries. Hidden Court: 3 entries.
Bandits: 1. Mercenary turncoats: 1. Orcs: 1. Total 14 roster entries, every
one mapped to doc 04's verb grammar and (where applicable) a locked doc 17
kit. Zero new kits, zero new verbs.

## Section 2: WILDERNESS ENCOUNTER TABLES PER BIOME

Per doc 03's biomes and doc 41's eight families. Columns: family,
composition, tier band, day/night variant. Day/night per doc 12's
affinity-relative clock (a good player's night is the dangerous half; doc 03
biome safety by alignment governs). Wolf-adjacent encounters obey doc 19's
hunt-any-during-moon rule: during the full moon, wolf-strain encounters run
day tables as night tables. All compositions PROPOSED.

### 2.1 Darkwood forests (the contested buffer)

| Family (doc 41) | Day composition | Night composition | Tier |
|---|---|---|---|
| Family 1 (dens and lairs) | Rot Wolf pair at den mouth | wolf pack 3-4 | T1-T2 |
| Family 2 (hidden holy/tainted) | coven glade: 2 Bound Thralls (humanoid, full grammar, PROPOSED health 160) | +1 thrall, 1 Wail-Caster at tainted glades | T2 |
| Family 3 (wayfinding) | 0-1 bandit scavenger pair | 2-3 bandits | T1 |
| Family 4 (road life) | smuggler pair (bandit frame, flee at 50 percent) | +1, plus 1 Rot Wolf escort | T1-T2 |
| Family 5 (ruins) | 0-1 Grave Ghoul (disturbance-spawned only, doc 34 day rule) | 2-3 ghouls | T2 |
| Family 6 (riches) | 1-2 bandit claim-jumpers | +1 | T1 |
| Family 7 (one-off wanderers) | see open question 4: hand-authored, likely OUTSIDE tables | same | n/a |
| Family 8 (war scars) | 2-3 mercenary turncoats looting | +1 | T2-T3 |

### 2.2 Moors and highlands (the exposed hourglass)

| Family | Day | Night | Tier |
|---|---|---|---|
| Family 1 | wolf pack 2-4 (doc 34: no ring discipline) | pack 3-5, full-moon: packs hunt any hour (doc 19) | T1-T2 |
| Family 2 | chapel mounds: 0-1 ghoul (disturbed only) | 2-3 ghouls | T2 |
| Family 3 | wayfinding: no enemies | no enemies | T0 |
| Family 4 | pilgrim road traffic (neutral, doc 41) | corpse-cart pair + 1-2 ghouls drawn to the cart | T1-T2 |
| Family 5 | barrow wights (undead kit, PROPOSED health 260, undead lock) | +1 per barrow, wight-lord at named barrows (T4) | T2-T3 |
| Family 6 | none (mine sites per doc 41 ruling 9; garrison-held sites use 1.5 turncoats) | haunted mines: ghoul pool | T2 |
| Family 7 | open question 4 | | n |
| Family 8 | battlefield scavenger bandits 2-4 | +1 | T1-T2 |

### 2.3 Swamplands (standing neutral)

| Family | Day | Night | Tier |
|---|---|---|---|
| Family 1 | hag-pool beast (beast grammar, PROPOSED health 200, Miasma-adjacent spit reuses undead-kit Wail/Grave Rot costs per doc 34's undead zone-denial line; see open question 5) | +1 | T2 |
| Family 2 | drowned shrine: drowned dead (undead lock, PROPOSED health 180) | 2-3 drowned dead | T2 |
| Family 3 | stilt-hut wayfinding: no enemies | no enemies | T0 |
| Family 4 | smuggler skiff pair | +1, night smuggling runs | T1 |
| Family 5 | old-imperial ruin: ghoul pool | +1 | T2 |
| Family 6 | alchemist-gatherer rival (bandit frame) | +1 | T1 |
| Family 7 | open question 4 | | n |
| Family 8 | none (swamp war scars rare) | | T2 |

### 2.4 Mountains and passes (the garrison biome)

Weather, not the clock, is the main threat (doc 03). Encounter density low.

| Family | Day | Night | Tier |
|---|---|---|---|
| Family 1 | bear cave (beast grammar, PROPOSED health 320, high poise) | +1 cub at seasons PROPOSED | T2-T3 |
| Family 2 | none | none | T0 |
| Family 3 | blockhouses: garrison pair (soldier grammar, parry) | +1 | T2 |
| Family 4 | dwarf caravans (neutral escort) | +1 guard | T1 |
| Family 5 | old-imperial ruin: undead kit wights | +1 | T2-T3 |
| Family 6 | gem-seam claim bandits 2-3 | +1 | T1-T2 |
| Family 7 | open question 4 | | n |
| Family 8 | skirmish scar: turncoat patrol 3-4 | +1 | T2-T3 |

### 2.5 Farmland and river valleys (the safe-ish core)

| Family | Day | Night | Tier |
|---|---|---|---|
| Family 1 | 0-1 wolf (full-moon pressure only, doc 41 mix) | wolf pack 2-3 (full moon: any hour) | T1 |
| Family 2 | parish garden: no enemies | 0-1 ghoul at desecrated gardens | T0-T1 |
| Family 3 | wayfinding: no enemies | no enemies | T0 |
| Family 4 | the traffic heartland: neutral carts, bandit toll attempt 2-3 | +1 | T1 |
| Family 5 | 0-1 ghoul (old barrow-under) | +1 | T1-T2 |
| Family 6 | none beyond doc 03/06 ambient | | T1 |
| Family 7 | open question 4 | | n |
| Family 8 | harvest-burn scar: bandit looters 2-4 | +1 | T1 |

### 2.6 Blighted zones (the attrition biome)

Clock inverted and broken (doc 03/19: day dim, night calm for dark players).
Fewer sites, worse company.

| Family | Day (dim) | Night | Tier |
|---|---|---|---|
| Family 1 | blight-hound pack 2-3 (beast grammar, PROPOSED health 160, taint texture) | pack 3-4 | T2-T3 |
| Family 2 | the working shrine rarity: 1 Veil-Touched Zealot (humanoid, full grammar, PROPOSED health 200; texture: tends the scar, never names the creditor) | +1 | T3 |
| Family 3 | wayfinding 0-1: no enemies | no enemies | T0 |
| Family 4 | dark-court supply pack (undead raider line, section 1.2) | +1 | T2-T3 |
| Family 5 | pact-scar ruins: Veil-scar revenants (undead lock, PROPOSED health 240; kit: Grave Rot + Wail only, doc 17 model, no new kit) | +1 | T3 |
| Family 6 | blacksteel ore-scar: contested, ghoul pool | +1 | T2-T3 |
| Family 7 | open question 4 | | n |
| Family 8 | fresh war scar: dark-court dead, 2-3 ghouls | +1 | T2 |

### 2.7 Doc 41 family coverage check

- Family 1 Dens and Lairs: covered (every biome table).
- Family 2 Hidden Holy and Tainted Places: covered (Darkwood, Swamplands,
  Farmland, Blight). Moors chapel mounds covered.
- Family 3 Wayfinding Threads: covered (non-hostile family; zero-enemy rows
  are the coverage, not an omission).
- Family 4 Road Life: covered.
- Family 5 Ruins and Pre-Fall Landmarks: covered.
- Family 6 Riches Sites: covered.
- Family 7 One-Off Wanderers: NOT tabled. They are hand-authored,
  continent-rare, never region-guaranteed (doc 41). Flagged open question 4
  rather than force-fed into random tables.
- Family 8 War Scars: covered.

Eight of eight families covered; one coverage flag raised, not silently
dropped.

## Section 3: CAMP THREAT BESTIARY (the raid and ambush sets)

Doc 11's camp threat model: raids hit camps in dangerous zones; thieves hit
camps in safe zones; the Knock at the Door investigators run the
2026-09-14 ruling pass. All numbers PROPOSED.

### 3.1 Raiding parties per territory key

- LIGHT-HELD LAND: Militant purge parties. Doc 34 pair grammar at scale:
  2 Shield-Guards + 2 Spear-Guards, 1 Dawnward Officer at T3 keys (Light
  Ward on approach, Blessed Bolts at range, Sanctuary if the camp holds).
  Raid trigger: evil-affinity player camping in light-held land (doc 04's
  day-sleep ambush mirrored). PROPOSED party size 4-5.
- DARK-HELD LAND: enforcer packs. Doc 34 pack grammar: 3-5, 4m ring, one
  commit per 1.5s; composition 2-3 Gravebound Raiders + 1-2 Duskmantle
  raiders + 1 Wail-Caster. Night raids only in practice (doc 04: the night
  ambush for good players). PROPOSED.
- CONTESTED LAND (Darkwood): mixed. 1 pair + 1 pack PROPOSED, the buffer's
  both-masters texture.
- Raid timing: camps emit noise 12m (doc 34 sound table, doc 10 cooking);
  a raiding party inside that radius on a night table begins its approach.
  Raid party sight uses section 1 doc 34 ranges; torch light override 20m
  both ways (doc 02 scarce light register, doc 34 reuse).

### 3.2 Thief encounters (safe zones)

Humanoid, sloppy-to-midline, full grammar minus parry (not soldiers).
PROPOSED block: health 120, stamina 70, poise 35, light 14, heavy 24, light
speed 0.55s (33f), roll 25 percent, block 20 percent, parry never. Spawn
context: safe-zone camps at night, lone or pair. Behavior: steal-then-flee
(rout logic at 50 percent health, no pack loyalty). Texture: unaffiliated;
thieves carry no taint and no kit. PROPOSED.

### 3.3 Knock at the Door investigators (the 2026-09-14 ruling pattern)

Composition per territory key (PROPOSED):
- Light-keyed knock: 1 Shield-Guard + 1 Spear-Guard + 1 Investigator
  (full grammar, block-heavy, PROPOSED health 200; carries the writ texture,
  never the debt's contents).
- Dark-keyed knock: 2 Gravebound Raiders + 1 Wail-Caster.
- Neutral-keyed knock: 2 mercenary turncoats + 1 thief-guide (stealth opener,
  doc 34's Shadow Kill grammar reference).

Ambush ring setup the Knock pattern requires: investigators spawn outside
sight range at the camp's perimeter, ring spacing 4m (doc 34 pack spacing
reuse), approach from the player's rear arc when the rear arc is not facing
them (doc 34 ambush-spawn reuse), detection pre-set to 60, audio cue fires
2.00s before the spawn resolves (doc 34's night-ambush audio contract).
On knock etiquette: they announce (the Knock), then force if refused.
Refusal triggers the ring. All PROPOSED; the etiquette texture is doc 11's
to own if it conflicts.

## Section 4: DELVE WARDEN CONCEPTS (non-authoring note)

Doc 47 (altar delves GDD) owns warden concepts and delve layouts. This doc
supplies ONLY the enemy pool delves draw from: 2-3 warden-adjacent enemy
concepts per altar, each mapped to doc 04's verb grammar and doc 17's kit
model, cross-referenced to doc 47. No layouts here. All PROPOSED.

Per-altar pool (the three delve mouths, doc 47's altar set):

- SUN SIPHON CONSTRUCT (light-keyed altar): construct (not undead, not
  beast): full grammar minus parry (PROPOSED: construct tier reads as
  soldier-lite; see open question 6). Doc 04 mapping: heavy attack =
  siphon draw (remixed heavy, doc 34 remix grammar reference), zone
  signature = Consecrate-flavored ground denial using the doc 17 Holy
  Wards grammar made hostile, no new spell. Tier T3. Doc 47 cross-ref:
  altar interior pool.
- VEIL PACT-SCAR REVENANT (scar-keyed altar): undead lock (no dodge, no
  parry, heavy poise, relentless). Kit model: Grave Rot + Wail of Despair
  only (doc 17 undead kit subset, no new kit verbs). Tier T3. Texture:
  pact-scarred remnant; flavor text references the scar, never the
  creditor. Doc 47 cross-ref: scar chambers.
- DEEP CONGREGATION GUARDIAN (deep altar): humanoid cultist line, full
  grammar, midline discipline, PROPOSED health 240, 1 caster per 3 with
  1-3 signature dark pacts (doc 17 enemy-caster rule). Tier T3-T4. Doc 47
  cross-ref: congregation hall. Guardia texture: they serve the altar's
  silence, not the pact's ledger; no entry names the signer or the
  creditor.

Pool count: 3 concepts, reusable across the three altars with composition
swaps (PROPOSED: each altar leads with its keyed concept and mixes in one
other). Doc 47 owns which pool lands in which layout.

## Section 5: BOSS REMIX GRAMMAR APPLICATION

Doc 04's rule: dungeons teach a monster pool; the boss remixes it. Remix
recipe per doc 34's Rot-Mother pattern: same pool stats, size/boss factor
3.0, two kit verbs re-costed, one signature twist, health fixed (no
scaling). All PROPOSED.

- DEN (beast pool, doc 41 family 1): pool taught = the biome's beast line
  (Rot Wolf Darkwood, bear mountains, blight-hound blight). Remix: boss =
  pack-mother chassis, pool stats x boss factor 3.0 poise, health PROPOSED
  1000 band; remixed verb 1 = Terrifying Howl re-costed as a fear-check
  opener on the doc 19 wolf kit model (no new verb: kit verb re-costed);
  remixed verb 2 = summons 2 pool beasts at 60 percent health. Signature
  twist: the ring-less pack discipline inverts (beasts commit in
  overlapping pairs rather than solo spacing).
- VAULT-SEAT (undead/necro line, doc 14 necro-aristocracy texture):
  pool taught = Gravebound Raider + ghoul line (doc 34's ghoul grammar).
  Remix: Dread Lord-tier boss (doc 14 title reuse), undead lock, heavy
  poise; remixed verb 1 = Grave Rot burst (ghoul heavy re-costed, doc 34
  Rot-Mother pattern); remixed verb 2 = Mass Grave summon (doc 17 T4
  re-costed as a once-per-fight boss cast; kit verb, not new). Signature
  twist: the vault's sealed doors open on phase 2, the pool floods in.
  PROPOSED.
- CAVERN MARKET APPROACHES (orc line, doc 22): pool taught = orc
  companies (1.6) + mercenary turncoats. Remix: orc war-chief chassis,
  full grammar including parry (soldier-tier boss), PROPOSED health 1100;
  remixed verb 1 = Wall of Steel-adjacent approach denial is a PLAYER
  technique: NOT usable. Boss remix uses only enemy-legal verbs: heavy =
  shield-shatter charge (remixed heavy), remixed verb 2 = rally (pack
  commit windows tighten, doc 34 rhythm at officer scale). Signature
  twist: the market crowd joins the boss's ring at phase 2. PROPOSED.
- THE THREE DELVE MOUTHS: pool taught = section 4's warden-adjacent pool.
  Remix per altar key: Sun siphon construct boss (poise factor 3.0,
  remixed siphon heavy + Light Ward re-costed as a self-ward), Veil-scar
  revenant matriarch (Grave Rot + Wail re-costed, undead lock), Deep
  congregation hierophant (1-3 signature dark pacts per doc 17
  enemy-caster rule, midline grammar). Signature twist per mouth PROPOSED:
  light altar boss denies its own Consecrate ground to the player;
  scar-keyed boss's Rot patches linger after death; congregation boss
  re-casts a fallen guardian once. Doc 47 owns placement; this doc owns
  the pool mapping. All PROPOSED.

Remix count: 4 dungeon types, 4 pool-to-boss recipes, 8 remixed verbs total,
all re-costed existing kit/pool verbs. Zero new mechanics.

## Open questions (doc 08 format, numbered, assigned)

1. RESOLVED, reclassified from "spec conflict" to provenance note:
   spec constraint 4 states "Signer = witch's mask"; doc 19's own
   supersession chain (doc 19 lines 156-177) resolves it: the
   2026-09-13 ruling (no separate Signer, role performed by the Pale
   Queen, doc 36 ruling pass entry 4) was superseded, then superseded
   AGAIN 2026-09-14 by the Nicko identity correction (doc 36 RULING
   PASS 2026-09-14): THE SIGNER WAS ALWAYS THE WITCH, posing as the
   good court's queen. Doc 44 reconciles the cast. The spec's Signer
   framing stands; no live competing authority, so this is not an
   open question. Resolved by citation; no ruling pass needed.
   Assigned: Nicko (closed by citation).
2. Hostile Warden war-parties outside wolf-line trials: doc 19's ace rule
   implies the Court deploys only in extremis. Confirm hostile Warden
   spawns are debt-default or Deep-Altar adjacency only. Assigned: Nicko.
3. Orc line-infantry parry: doc 04's lock says soldiers only. Are orc
   war-bands "soldiers" for the parry lock (this doc assumes YES,
   PROPOSED) or beasts-adjacent? Assigned: Nicko.
4. Family 7 (One-Off Wanderers) table membership: doc 41 makes them
   hand-authored and continent-rare. Confirm they stay OUT of random
   encounter tables and appear only via authored placement. Assigned:
   Nicko.
5. Hag-pool beast zone-denial: this doc proposes reusing the undead kit's
   Wail/Grave Rot as the hag-pool beast's spacing answer per doc 34's
   undead line, but a beast with cast verbs may strain the doc 04 beast
   lock. Confirm or cut to pure leap/spacing grammar. Assigned: Nicko.
6. Construct grammar tier: sun siphon constructs are neither undead nor
   beast. Doc 04's grammar offers humanoid, beast, undead. Confirm
   constructs read as soldier-tier (parry allowed) or beast-tier (no
   parry); this doc default proposes soldier-lite with no parry. Assigned:
   Nicko.
7. Thief stat block (3.2) has no governing doc number for health/stamina
   bands outside doc 34 conventions. Confirm the PROPOSED block or hand it
   to doc 34's next number pass. Assigned: Nicko.

Note: doc 46's OQ-8 and OQ-9 are pending Nicko rulings. Nothing in this doc
derives from them; no dependency raised.

## Completion report

- Sections delivered: 1 FACTION ENEMY POOLS, 2 WILDERNESS ENCOUNTER TABLES
  PER BIOME, 3 CAMP THREAT BESTIARY, 4 DELVE WARDEN CONCEPTS
  (non-authoring), 5 BOSS REMIX GRAMMAR APPLICATION.
- Entry counts: Section 1: 13 roster entries across 3 courts/factions
  (light 3, dark 5, Hidden Court 3, bandits 1, turncoats 1, orcs 1). Section 2: 6 biome tables, 8 rows each = 48
  compositions, 8/8 doc 41 families covered (family 7 via open question
  flag, per the spec's coverage-check alternative). Section 3: 4 territory
  raid sets, 1 thief block, 3 Knock compositions, 1 ring setup. Section 4:
  3 warden-adjacent concepts. Section 5: 4 remix recipes, 8 remixed verbs.
- Open questions raised: 7 (numbered above, all assigned to Nicko), plus
  the doc 46 OQ-8/OQ-9 non-derivation note. Open question 1 is
  RESOLVED by citation and reclassified from "spec conflict" to
  provenance note (doc 19's supersession chain, lines 156-177: the
  09-13 ruling was superseded 2026-09-14; the Signer was always the
  witch), so 6 remain open for ruling.
- Spec conflicts: 0 live. The flagged constraint 4 Signer-identity
  conflict was reclassified to provenance note after verification
  against doc 19's supersession chain; the spec framing stands.
- Hard constraints honored: no new combat mechanics, no new corruption
  kits (doc 17's three used only), no new verb grammar (doc 04/32 verbs
  only), no em dashes, PROPOSED on all invented numbers, under 900 lines,
  identity/ledger compliance throughout (no entry discloses the
  creditor's identity), doc 46 OQ-8/OQ-9 untouched.
- Files created: this doc only. No git commands run. No other files
  touched.