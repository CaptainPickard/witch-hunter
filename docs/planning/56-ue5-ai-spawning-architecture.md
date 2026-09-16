# 56 - UE5.8 AI and Spawning Architecture Spec

Drafted 2026-09-16, UE5.8 AI and spawning architecture spec (doc 31 engine plan governs; GDDs 46-51 + planning corpus are the content source). PROPOSED for Nicko review. Subordinate to locked rulings; conflicts are open questions, not edits.

Scope note: this doc authors engine structure for the AI and SPAWNING module: enemy AI state machines, pair/pack grammars, spawn rules, World Ledger read hooks, and encounter table wiring. It invents no gameplay content, no new enemies, no lore, no new verbs, no new mechanics. Doc 54 owns the shared damage interface this doc consumes; doc 57 owns the World Ledger schema this doc reads. Content sources: doc 34 (pools, state rules), doc 51 (pools, 48 compositions, camp threats, remix grammar), doc 41 (families, site states), doc 11 (camp threats, territory keys). Zero new enemies (doc 51 section 1 pools are the content source).

## CONVENTIONS (cited, not restated)

- Naming: doc 53 section 1.4 governs every class, struct, enum, DataTable, and asset name in this doc (WH/FWH/UWH/EWH prefixes, DT_WH tables, /Game/WH/Data registry for cross-module tables). Cited per doc 52 gate rule 2.
- Folder root: /Game/WH/ per doc 31 (Core, Combat, World, Data, UI). This doc adds /Game/WH/AI/ (PROPOSED path) for AI classes and /Game/WH/Data/ for every table two or more modules read (doc 53 section 1.4 rule).
- Custom combat stack: doc 31 locked the custom lightweight action stack with GAS deferred to the slice-exit gate (doc 52 locked engineering ground). This spec adopts NO GAS types anywhere. Where a kit verb payload needs a representation, doc 54 CB-4 is open and carries (see CA-4).
- Header-level signatures only; implementations at M2+ per doc 31 milestones (doc 53 section 2 rule).

## Section 1: ENEMY AI STATE MACHINE

### 1.1 Stance

Custom finite state machine, no Behavior Tree assets, no GAS (doc 31 locked custom stack, GAS deferred; doc 52 row 56). Rationale: doc 34's AI is data-driven (perception meters, stat-block tables, family grammars), which a compact FSM plus DataTables carries without Behavior Tree authoring overhead. PROPOSED as the module stance; see CA-1.

Every humanoid, beast, and undead agent runs the SAME verb set as the player (doc 04 lock: "enemies use the same verb set"). The AI never owns combat math: it dispatches verb intents into the agent's UWHCombatComponent (doc 54 section 2, the shared player/enemy component), and all hit resolution routes into doc 54's UWHDamagePipeline (section 3). Stagger and death are not AI states to author: they are states doc 54's pipeline already owns (doc 54 sections 3.3-3.5). This doc wires the routing, nothing else.

### 1.2 Class list (header-level signatures)

```cpp
// /WH/AI/WHEnemyAIController.h
UCLASS()
class AWHEnemyAIController : public AAIController
{
    GENERATED_BODY()
public:
    void OnPerceptionEvent(const FWHAIPerceptionEvent& E);  // doc 34 section 1 channels
    void EnterState(EWHAIState Next);                        // 1.3 routing
    void ReceiveTaunt(const FWHTauntEvent& E);               // doc 34 section 2
private:
    TWeakObjectPtr<UWHCombatComponent> OwnedCombat;          // doc 54 section 2 (player grammar)
    TWeakObjectPtr<UWHGroupCoordinatorComponent> Group;      // section 2 of this doc
    EWHAIState CurrentState;
};

// /WH/AI/WHEnemyBrainComponent.h : one blackboard per agent (doc 34 section 1)
UCLASS()
class UWHEnemyBrainComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    void TickPerception();          // every 0.10s (6f), doc 34 section 1
    float DetectionMeter;           // 0-100, doc 34 section 1
    FName FamilyRowId;              // DT_WHAIPerception row (doc 34 section 5 stat blocks)
};
```

Enum and event structs (header level):

```cpp
UENUM()
enum class EWHAIState : uint8 { Idle, Patrol, Engage, Stagger, Dead };

struct FWHAIPerceptionEvent
{
    EWHPerceptionChannel Channel;  // Sight, Sound, Damage (doc 34 section 1)
    TWeakObjectPtr<AActor> Source;
    float NoiseRadius_m;           // doc 34 section 1 sound table
};

struct FWHTauntEvent
{
    TWeakObjectPtr<AActor> Taunter;
    float ThreatWeight;            // damage last 5.00s + 50 per taunt event (doc 34 section 2)
};
```

Class count, section 1: 2 classes, 1 enum, 2 structs. All names WH-convention per doc 53 section 1.4.

### 1.3 State routing

States at header-signature level. Routing table (all transitions derive from doc 34 sections 1-2; no new behaviors):

- Idle/Patrol to Engage: DetectionMeter reaches 100 (AGGRO, doc 34 section 2). First target = trigger source (sight, loudest recent noise, last hitter).
- Engage to Stagger: poise break. Doc 54's pipeline calls OnPoiseBroken on the defender's UWHCombatComponent (doc 54 section 3.4); the AI controller listens as an event, never a pipeline branch. Stagger duration, extensions, and hit-stop are doc 54's (1.20 s committed, +15 f Concussive Force-class).
- Any to Dead: health 0. Doc 54 section 3.5 owns the death clip and drop context (FWHDeathContext); this doc's UWHSpawnPersistenceSubsystem (section 2.4) receives the death notification to update site persistence state. No respawn logic lives in the AI.
- Engage to Patrol (de-aggro): target invisible and silent 8.00s (480f) AND beyond leash (30m from spawn, 15m interiors); heal to full over 10.00s off-screen (doc 34 section 2).

### 1.4 Perception model as data

Doc 34 section 1's three channels become data rows, not code constants:

DT_WHAIPerception (one row per family; values carry doc 34 sections 1 and 5 verbatim, PROPOSED where doc 34 is PROPOSED):

| Column | Type | Notes |
|---|---|---|
| FamilyRowId | FName | bandit, rot wolf, grave ghoul, plus doc 51 section 1 roster rows |
| SightRangeDay_m | float | doc 34 section 5 blocks (25 bandit, 30 wolf, 15 ghoul) |
| SightRangeNight_m | float | night halves sight ranges (doc 34 section 1) |
| DetectionGainOpen/GainMid/GainEdge | float | 40/20/8 per second (doc 34 section 1) |
| CrouchMultiplier | float | 0.5 (doc 34 section 1: crouched halves gain) |
| TorchOverrideRadius_m | float | 20 both ways inside torch light (doc 34 section 6, doc 02 light register) |
| RollChancePct / WrongDirectionPct | float | per family (doc 34 section 5: bandit 15/20, wolf 45 leap, ghoul 0) |
| BlockChancePct / ParryFlag | float/bool | doc 04 locks: soldiers parry only (0.15s AI window, doc 34 section 3); beasts never; undead never |
| HearingRadius_m | float | ghoul 18m sound-driven (doc 34 section 5.3) |

Tick budget: 0.10s (6f) per agent (doc 34 section 1). With doc 31's under-20-skinned-mesh budget and 2 ms game thread combat slice (doc 31 G23), a synchronized tick of 20+ agents risks a spike. PROPOSED: staggered per-agent phases so at most a quarter of active agents evaluate per tick frame. See CA-3.

### 1.5 Aggro, taunt, target selection (doc 34 section 2 as engine structure)

- AGGRO lock, TAUNT re-evaluation roll every 1.00s (60f), threat weight = damage dealt last 5.00s + 50 per taunt event, Guard interpose +100 (doc 34 section 2).
- Family responses: bandits re-roll on every taunt; disciplined soldiers resist at 60 percent stability; bosses never re-roll (doc 34 section 2).
- Target selection weights: distance 60 percent, damage-dealt threat 30 percent, target stickiness 10 percent (doc 34 section 2). Squire threat weight 0 while unarmed and fleeing (doc 34 section 2, doc 23).
- Fixed difficulty: no table or code path reads player level or region progress (doc 04 lock; doc 54 section 3.6 fairness floor carries). Sloppiness is a per-family authored property on the spawn table row, never a scaling input (doc 34 section 3).

### 1.6 Shared verb grammar wiring

Doc 04's locked grammar (doc 34 section 3) as engine wiring: the AI dispatches intents (light, heavy, roll, block, parry where soldier) into UWHCombatComponent, which resolves them with the identical doc 32/33 frame data the player reads. AI-specific values that already exist as locked data: AI roll chance per family, AI parry window 0.15s (9f) vs player 0.20s (doc 34 section 3), panic-roll wrong direction 20 percent bandits (doc 34 section 3), stamina pools and stamina-break (doc 34 section 3). Nothing here adds a verb. Stagger and death feed doc 54's pipeline (sections 3.3-3.5); no AI-side duplicate math.

## Section 2: PAIR/PACK GRAMMARS AND SPAWN RULES

### 2.1 Group coordinator component

```cpp
// /WH/AI/WHGroupCoordinatorComponent.h
UCLASS()
class UWHGroupCoordinatorComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    void RegisterMember(AWHEnemyAIController* Member);
    void OnMemberDeath(AWHEnemyAIController* Member);   // retighten rhythm, retreat checks
    bool CanCommit(const FWHPackConfig& Config);          // 2.2 pack rhythm gate
private:
    TArray<TWeakObjectPtr<AWHEnemyAIController>> Members;
    EWHPawnGrammar Grammar;   // Pair, Pack, BeastWild, UndeadRelentless (doc 34 section 4)
};
```

Group composition is authored on the SPAWN TABLE row (section 2.3), never on the agent class: the same doc 51 pool entry can stage as a pair, a pack, or a solo depending on which DT_WHEncounterComposition row spawned it. Grammar per doc 34 section 4 and doc 04's locked court forces:

### 2.2 Grammars as spawn-composition patterns

- LIGHT-COURT PAIRS (doc 04: shield-and-spear discipline; doc 34 section 4): spawn exactly 2. Shield agent holds front (block, bash on approach), spear holds 2.5m offset at 90 degrees, attacks only while the shield partner holds aggro. Lone survivor switches to pack-retreat logic unless officer tier (doc 34 section 4; doc 51 section 1.1 carries the same pattern).
- DARK-COURT PACKS (doc 04: bleed-and-retreat rhythm; doc 34 section 4): spawn 3-5, 4m spacing ring, exactly one commit per 1.5s window, rear-arc attack bias when the ring is over 50 percent rear-facing. Pack member death tightens commit windows to 1.0s (doc 34 section 4). Vampire raiders run doc 04's corruption kit verbs (Blood Tithe, Veil of Mist below 50 percent pack strength); kit verbs per doc 17, no new kit (doc 51 section 1.2).
- BEASTS: no block, no parry; dodge-equivalent leaps/sidesteps; wild packs with NO ring discipline (doc 34 section 4): pure spacing test.
- UNDEAD: no dodge, no parry; relentless walkers, heavy poise; zone denial via Wail of Despair / Grave Rot patches as their spacing answer (doc 04, doc 34 section 4).
- RETREAT LOGIC (doc 34 section 4): pack retreat below 40 percent pack strength AND agent health below 30 percent (flee to max sight range, return after 30.00s re-grouped). Light pairs never retreat while the pair stands; a lone survivor does. Bandits rout at 50 percent pack loss. Beasts flee at 25 percent health. Undead never retreat.

All pattern parameters are DataTable columns on DT_WHEncounterComposition (2.3), not code branches. No new grammar; doc 34's numbers carry verbatim, PROPOSED where doc 34 is PROPOSED.

### 2.3 Composition DataTables

Schema only; values are PROPOSED until reviewed (constraint 3).

DT_WHEncounterRowStruct (row struct FWHEncounterRow):

| Column | Type | Notes |
|---|---|---|
| RowId | FName | stable id, e.g. Darkwood_Road_Day |
| Biome | EWHBiome | Darkwood, Moors, Swamplands, Mountains, Farmland, Blight (doc 03 biomes; doc 51 section 2 tables) |
| Family | EWHEncounterFamily | 8 values = doc 41 Part 1 families (DensAndLairs, HiddenHolyTainted, WayfindingThreads, RoadLife, RuinsLandmarks, RichesSites, OneOffWanderers, WarScars) |
| DayComposition / NightComposition | FWHSpawnSlot arrays | ordered spawn slots (2.4) |
| TierBand | uint8 | T0-T4 (doc 51 section 2 tier columns) |
| Grammar | EWHPawnGrammar | Pair, Pack, BeastWild, UndeadRelentless, None |
| SiteStateRead | EWHSiteState | doc 41 Part 2 five light states gate whether the row is live |

Wiring rules:

- Doc 41's 8 encounter families are ENUM VALUES plus per-biome mix rows (doc 41 Part 3 mixes), not eight code paths. One spawner, family-keyed rows.
- Doc 51's 48 wilderness compositions (section 2, six biome tables x 8 family rows) are DT_WHEncounterComposition ROWS. Each row references doc 51 roster entries by FName; the spawner resolves rows to doc 51 section 1 stat blocks. Family 7 (One-Off Wanderers) stays OUT of random tables: hand-authored placement only (doc 41; doc 51 open question 4), so tables cover 7 of 8 families with authored zero-enemy rows where the mix says none. See CA-2 for the wanderer-table membership fork already logged in doc 51.
- Spawner config asset: BP or DataAsset DT_WHEncounterConfig per hold region, listing which DT rows are live per site state and per war-state key (doc 13 war state rekeys patrols, doc 41 conventions).

### 2.4 Spawn persistence (doc 09/37 respawn-on-rest rules)

```cpp
// /WH/World/WHSpawnPersistenceSubsystem.h
UCLASS()
class UWHSpawnPersistenceSubsystem : public UWorldSubsystem
{
    GENERATED_BODY()
public:
    void OnSiteCleared(FName SiteId);         // Cleared-Wound commit
    void OnPlayerRest(FName CampOrTavernId);  // respawn-on-rest trigger
    void OnDungeonExitTrigger(FName DungeonId); // destruction commits (doc 37 ruling 18)
    bool IsSiteCleared(FName SiteId) const;   // read by spawner before rolling a row
};
```

Rules carried verbatim as structure (doc 09/37 per the brief; doc 37 R18 locked 2026-09-13; doc 41 conventions; doc 41 ruling pass 7 R1 habitat drift):

- OVERWORLD inhabitants respawn on rest: the player resting (tavern or warp camp, doc 04 save/respawn lock) re-rolls Inhabited-state site spawns on the site's DT rows. Cleared-Wound rule first: a CLEARED site stays cleared for its species and is colonized by Vacuum-rule colonizers (doc 37 ruling 15, doc 41 ruling 2). So respawn-on-rest re-rolls only sites whose light state is INHABITED or CONTESTED (doc 41 Part 2 states), and the colonizer set comes from the situation tables (doc 37 ruling 15's colonizer list: bandits, spiders, necromancers, wizards, refugees).
- DUNGEONS never respawn their old self: destruction commits at the EXIT trigger (doc 37 ruling 18). Engine shape: dungeon instance holds a pending-state buffer; crossing the exit trigger flushes it into the save-serializable world state (doc 57 owns the ledger and save schema; this doc only declares the flush call). No dungeon interior re-spawns its pre-clear population on rest.
- HABITAT DRIFT (doc 41 ruling pass 7 R1): cleared dens never re-form as their species; new dens of that species may appear at region edges over time. Engine shape: the persistence subsystem holds a per-species den registry; drift is authored as new site placements by the world GDD (doc 49 owns placements), not a runtime spawner behavior. This doc wires the registry only. See CA-5.
- One-off wanderers never respawn the same way twice (doc 41 family 7): the persistence subsystem marks a wanderer's payoff-consumed flag at their encounter's commit.

### 2.5 Night and ambush spawn modifiers (doc 34 section 6, carried)

- Night tables add +1 agent per encounter; sight ranges halve (doc 34 section 6).
- Ambush spawn: night agents spawning within 18m of an unaware player enter with detection pre-set to 60 and attack from the rear arc when not facing them (doc 34 section 6).
- Audio cue 2.00s before the ambush spawn resolves (doc 34 section 6, doc 10 Hunter's Darkbread). This is an event the spawner emits for the audio module (doc 58/audio doc owns the cue); the AI module only owns the timing contract.
- Veil-Tide fronts extend night-table hours to 19:00-07:00 (doc 03 lock, doc 34 section 6). PROPOSED engine shape: DT_WHEncounterConfig rows carry a front-override hour band; the clock subsystem (doc 53 owns time) publishes the current front state, the spawner reads it.
- Night raids draw FROM doc 34's ambush cap, not on top (doc 41 ruling pass 7 R3): the spawner never stacks a night-raid party beyond the cap's party sizes.

## Section 3: WORLD LEDGER READ HOOKS

### 3.1 Ownership boundary

The World Ledger runtime table and its schema are doc 57's (doc 52 row 57: ledger schema, deed log, faction/sect meters, knowledge-ledger reveal gates). This doc authors ONLY the read interface AI consumes. Every hook declared here is read-only. The spawner and AI controller hold no ledger write path (constraint: grep-able, section 5).

### 3.2 Read-only interface

```cpp
// /WH/World/WHWorldLedgerReadInterface.h
UINTERFACE()
class UWHWorldLedgerReadInterface : public UInterface { GENERATED_BODY() };

class IWHWorldLedgerReadInterface
{
    GENERATED_BODY()
public:
    // Faction meters (doc 12 alignment gates; doc 57 owns the meter schema)
    virtual float GetFactionMeter(EWHCourt Court, FName MeterId) const = 0;   // e.g. Militant/Mercy parish meters (doc 20), siege alignment (doc 12)
    // Territory and war-state reads (doc 13; feed spawner keys, doc 11)
    virtual EWHWarState GetTerritoryWarState(FName TerritoryId) const = 0;
    // Knowledge-ledger gate check (doc 44 Part 2 cells; doc 57 owns the table)
    virtual bool MayActorKnow(FName ActorLedgerId, EWHCoreFact FactId) const = 0;
    // Site state read (doc 41 Part 2 five states; persistence in section 2.4)
    virtual EWHSiteState GetSiteLightState(FName SiteId) const = 0;
};
```

Implementation lives on doc 57's UWHWorldLedgerSubsystem (doc 53 naming convention: UWH + role + Subsystem). This module depends on the interface, never on the ledger implementation. No AI-side cache of ledger rows: reads go through the interface at decision time so war-state and meter changes apply without stale copies.

### 3.3 Faction meters driving aggression tables

Doc 12's alignment gates (affinity-relative threat, doc 04: "the same night road is a gauntlet for a good player and home ground for an evil one") as engine structure:

- DT_WHAggressionProfile (PROPOSED schema): one row per (court, meter band). Columns: MeterBand (EWHMeterBand PROPOSED bands: hostile/neutral/friendly per doc 12's meters), AggressionMultiplier (float, PROPOSED, tuning block), AllowedBehaviors (bitmask: ambush, patrol, ignore), NightTableOverride (row id or None).
- Meter bands gate which composition rows the spawner may roll (2.3) and which engage behaviors the FSM may enter. The band lookup is a data check at spawn time and at engage entry, not a continuous script.
- Doc 46 OQ-8/OQ-9 (Gambit hostility symmetry, ambush hours) are pending Nicko rulings: nothing here derives from them (doc 52 blocked-on-Nicko register). The aggression table schema leaves a per-court override column available but unused until ruled. See CA-6.

### 3.4 Knowledge-ledger gates as data checks

Doc 44 Part 2's knowledge ledger (who knows / suspects / misses each core fact) is enforced at runtime as data checks, not authored dialogue:

- Before any AI beat that references a core fact (an enemy flavor line, a knock-investigator's writ line, a wight-bard battlefield replay, a Warden encounter), the presentation layer calls MayActorKnow(ActorLedgerId, FactId). FALSE: the beat's fact-bearing line is replaced by the beat's neutral variant authored in doc 51/20 content. This is a runtime data gate on doc 57's table, never a hard-coded branch per fact.
- No AI beat may act on knowledge its doc 44 Part 2 cell forbids: concretely, no enemy agent's behavior tree state, target selection, or aggro trigger reads a fact the actor's ledger row does not grant. The only AI-side fact consumers in this doc's scope are: (a) war state (public, doc 13), (b) site light states (physical observation, doc 41 Part 2), (c) faction meters (public court posture). The pact, the creditor, the Signer's identity: NO enemy AI reads these. Doc 51's identity section carries the same rule for content text; this doc carries it for runtime reads.
- Ledger compliance (constraint 6): the gate is a data check at the read hook; nothing in a DT_WHEncounterComposition row, an AI state table, or a spawn config encodes a forbidden knowledge grant. Testerbot greps for write-call absence (section 5).
- Doc 44 Part 2's who-knows table (the Pale Queen knows the Signer is false; everyone else's rows per Part 2) is doc 57's runtime table content. This doc consumes the gate function only.

### 3.5 What AI never exposes (doc 19 context)

Enemy actors never expose: the creditor's identity, the debt's terms, the pact's authorship, the Signer's true identity. Their text may reference the pact, the Veil, the tithe as witnessed facts only (doc 51 identity section carries the content-side rule; this doc's runtime gate is the enforcement point). The dark court's NEED for souls is playable through aggression tables (doc 19: they need souls to save themselves), never through exposition.

## Section 4: ENCOUNTER TABLES WIRING

### 4.1 Per-biome encounter tables as DataTables

Doc 51 section 2's six biome tables (Darkwood, Moors, Swamplands, Mountains, Farmland, Blight) become DT_WHEncounterComposition rows (section 2.3 schema). Wiring:

- Row resolution: spawner picks rows matching (Biome, Family, SiteStateRead, hour band day/night, TierBand). Night variant column carries the +1 agent modifier (doc 34 section 6).
- Full-moon override (doc 51 section 2 header, doc 19 hunt-any-during-moon): wolf-strain rows carry a FullMoonAsNight bool; the clock subsystem's moon phase (doc 53 owns the calendar) flips the row's band read. Data flag, not a code special case per family.
- Territory key: each hold region's DT_WHEncounterConfig lists live row ids per territory key (doc 11's territory-keyed camp tolerance; doc 13 war state rekeys). War-state flips swap the active row set; no code change.

### 4.2 Camp threat sets (doc 51 section 3, doc 11)

DT_WHCampThreat (row struct FWHCampThreatRow), schema only, values PROPOSED:

| Column | Type | Notes |
|---|---|---|
| ThreatSetId | FName | e.g. LightHeld_Purge |
| TerritoryKey | EWHCourt | LightHeld, DarkHeld, Contested (doc 51 section 3.1) |
| Composition | FWHSpawnSlot array | resolves to doc 51 section 1 entries |
| RaidTrigger | EWHRaidTrigger | NightNoiseRadius, EvilCampDaySleep, WarStateSiegePrep |
| KnockComposition | FWHSpawnSlot arrays | 4.3 |

- Territory-keyed raid sets (doc 11 camp threat model, doc 51 section 3.1): light-held = Militant purge parties running doc 34 PAIR grammar at scale (2 Shield-Guards + 2 Spear-Guards + officer at T3 keys); dark-held = enforcer packs running doc 34 PACK grammar (3-5, ring); contested Darkwood = 1 pair + 1 pack. All compositions are doc 51 section 3.1 rows.
- Raid trigger wiring: camps emit noise 12m (doc 34 sound table, doc 10 cooking); a raiding party inside that radius on a night table begins approach (doc 51 section 3.1). The camp system (doc 11 owns camp menu/structure) subscribes to the spawner's raid-event; this doc declares the event, doc 11/doc 53 own the camp actor.
- Thief encounters (doc 51 section 3.2): safe-zone camps at night, lone or pair, steal-then-flee at 50 percent health rout logic (doc 34 rout reuse). Same DT_WHCampThreat path with a SafeZone territory key.

### 4.3 Knock at the Door investigators (doc 51 section 3.3)

- Compositions per territory key carried as rows (light: 1 Shield-Guard + 1 Spear-Guard + 1 Investigator; dark: 2 Gravebound Raiders + 1 Wail-Caster; neutral: 2 mercenary turncoats + 1 thief-guide). All doc 51 section 1 entries, PROPOSED where doc 51 is PROPOSED.
- Ambush ring setup (doc 51 section 3.3, reusing doc 34 section 6 contracts): spawn outside sight range at camp perimeter, ring spacing 4m (doc 34 pack spacing reuse), rear-arc approach, detection pre-set 60, audio cue 2.00s before spawn resolves. Same contracts as 2.5; the Knock pattern is a composition row + ring config, not new AI code.
- Knock etiquette: announce then force if refused (doc 51 section 3.3). The refusal check is a camp-interaction beat (doc 11 owns camp interaction); the spawner receives a ForceEntry event. Etiquette texture ownership is doc 11's if it conflicts (doc 51 section 3.3 note).

### 4.4 Boss remix grammar (doc 51 section 5, doc 34 section 5.4 pattern)

- Remix recipe (doc 34 Rot-Mother pattern, doc 51 section 5 carries): same pool stats, size/boss factor 3.0, two kit/pool verbs re-costed, one signature twist, health fixed no scaling. Doc 51 section 5 authored 4 recipes (den beast, vault-seat undead, cavern market orc, three delve mouths) with 8 remixed verbs total, all re-costed existing kit verbs. Zero new verbs (doc 51 section 5 count).
- Engine wiring: DT_WHBossRemix (row per recipe): PoolRowIds (the pool it teaches), RemixedVerb1/2 (frame-data row ids into doc 54's DT_FrameData verb rows, re-costed values), SignatureTwist (a scripted-phase hook id), HealthFixed (int32, no scaling, doc 04 boss lock; doc 54 section 3.6 fairness floor carries).
- Reuse of doc 54's weapon class remix wiring: doc 54 section 4's weapon class rows own the verb/frame-data row model the remix consumes; the boss remix re-costs EXISTING pool verbs by referencing their existing rows with new cost columns. No new verb rows beyond what doc 54's schema already holds. Where a remixed verb needs a tag/payload representation that GAS deferral leaves open, doc 54 CB-4 is OPEN and carries (CA-4).
- Delve warden pool: doc 51 section 4 supplies 3 warden-adjacent concepts; doc 47 owns delve layouts and which pool lands in which layout. This doc wires only the pool-to-boss DataTable mapping.

### 4.5 Asset list

| Asset | Path | Notes |
|---|---|---|
| DT_WHAIPerception | /Game/WH/Data/ | cross-module (combat reads too), doc 53 section 1.4 registry rule |
| DT_WHEncounterComposition | /Game/WH/Data/ | cross-module (doc 55 reads site rows) |
| DT_WHEncounterConfig | /Game/WH/Data/ | per-region configs, one asset per hold region |
| DT_WHCampThreat | /Game/WH/Data/ | doc 11 camp threat wiring |
| DT_WHAggressionProfile | /Game/WH/Data/ | doc 12 meter bands |
| DT_WHBossRemix | /Game/WH/Data/ | doc 51 section 5 recipes |
| BP/AI classes | /Game/WH/AI/ (PROPOSED path) | section 1.2 classes |

DataTable count, this doc's schema ownership: 6 tables, 2 classes plus the coordinator, 1 subsystem, 1 interface (sections 1-4 count rollup in the completion report).

## Section 5: TEST PLAN

What Testerbot validates, grep-able checks named exactly. All greps run against docs/planning/56-ue5-ai-spawning-architecture.md and, where noted, against the spec corpus.

- T1 AI class list matches sections: every class in section 1.2 and 2.1 appears in exactly one section's deliverable. Check: `grep -cE "^(UCLASS|class) " 56-*.md` returns the count claimed in the completion report (3 classes: controller, brain, coordinator, plus 1 subsystem and 1 interface); `grep -nE "class (A|U)WH" 56-*.md` lists each exactly twice (header + mention) max.
- T2 No new verbs: every verb named in this doc appears in doc 04, doc 32/33 frame data, doc 34 sections 3/5, or doc 17 kits. Check: extract verbs from sections 1.6/2.2 and grep each against 04/34/17; expected zero verbs not found. Also `grep -nE "new verb|new mechanic|new kit|new grammar" 56-*.md` returns only negation lines ("no new", "zero new").
- T3 Spawn tables reference doc 51 entries: every composition name in sections 2.3/4.2/4.3 cites doc 51 section 1 or section 3. Check: `grep -nE "doc 51" 56-*.md` count matches citations in the completion report; spot-check 18-beat sample (Testerbot's doc 46 sample size) of table rows against doc 51's 48 compositions.
- T4 Ledger read hooks are read-only: check write-call absence on the interface and its consumers. `grep -nE "Set[A-Z]|Write|Commit|Mutate|Apply" 56-*.md` must return zero matches inside section 3 (allowed elsewhere only in non-ledger contexts, e.g. Set for AI state fields is NOT permitted to appear in section 3 at all). Positive control: `grep -c "const = 0" 56-*.md` returns 5: the 4 interface methods (section 3) plus this test line itself; scoped to section 3 the count is 4 (every interface method is const pure-virtual).
- T5 No GAS adoption: `grep -niE "\bGAS\b|GameplayAbility|GameplayEffect|AbilitySystem" 56-*.md` returns only negation/deferral lines (doc 31 deferral, CB-4 reference). Zero affirmative adoption statements.
- T6 No em dashes: `grep -n` for the em dash codepoint U+2014 returns zero. Byte check as backup: `grep -cP '\x{2014}'` returns 0.
- T7 PROPOSED markers on invented numbers: `grep -c PROPOSED 56-*.md` returns at least the count of value-bearing schema lines (Testerbot samples 10 schema cells against their source docs; any number without a PROPOSED marker or a doc 34/51 citation is a FAIL).
- T8 Citation coverage: every section cites its ruling-derived elements. `grep -cE "doc (04|34|41|51|11|12|13|44|57|53|54|31|37|09|19)" 56-*.md` must exceed 40 (density check); Testerbot spot-checks 10 citations against owning docs for misattribution (the doc 46 finding class (a)).
- T9 No gameplay content: `grep -nE "new enemy|new bestiary|lores? " 56-*.md` returns only scope-note negations. Roster names appearing in this doc must exist in doc 51 section 1 or doc 34 section 5 (sample 10).
- T10 Line budget: `wc -l 56-*.md` under 700.
- T11 Open questions registered in doc 08: CA-1..n appear in doc 08's tracker section. Check: `grep -n "CA-[0-9]" 08-open-questions.md` after IO logs them (IO owns the 08/00 sync; this doc only authors CA entries below).
- T12 CB-4 referenced as open: `grep -n "CB-4" 56-*.md` returns the section 4.4/CA-4 references, phrased as open, never resolved.

## OPEN QUESTIONS (doc 08 format, numbered CA-1..n, assigned)

1. CA-1: FSM vs Behavior Tree stance for the AI module. This doc proposes custom FSM + DataTables per doc 31's custom-stack lock (section 1.1). Confirm no BT assets for enemy AI through slice 1. Assigned: Nicko.
2. CA-2: Family 7 (One-Off Wanderers) spawner membership. Doc 41 makes them hand-authored and continent-rare; doc 51 open question 4 already flags their absence from random tables. Confirm they stay outside DT_WHEncounterComposition and ride authored placement only (section 2.3). Assigned: Nicko.
3. CA-3: Agent perception tick phasing (section 1.4). PROPOSED quarter-per-tick stagger; confirm or set the phase budget at the UE5 spike with real agent-count data (doc 31 perf budget context). Assigned: Devbot at M2 spike, flagged for Nicko.
4. CA-4: Doc 54 CB-4 (tag representation for kit-verb payloads without GAS) is OPEN and carries. This spec's remixed verbs and aggression-profile behavior masks consume that representation (sections 3.3/4.4). Referenced as open per the brief; not resolved here. Assigned: doc 54's CB-4 owner (Devbot at implementation, flagged for Nicko at M3 per doc 54 CB-4).
5. CA-5: Habitat-drift runtime shape (section 2.4). Doc 41 ruling pass 7 R1 rules the DESIGN (cleared dens never re-form; new dens drift at region edges). Whether drift is a world-GDD authored placement (this doc's read) or a spawner subsystem behavior is open. This doc assumes authored-at-world-GDD. Assigned: Nicko.
6. CA-6: Doc 46 OQ-8/OQ-9 (Gambit hostility symmetry, ambush hours) remain pending Nicko rulings. This doc's DT_WHAggressionProfile leaves a per-court override column available but unused (section 3.3); nothing derives from OQ-8/OQ-9 (doc 52 blocked-on-Nicko register carries). Assigned: Nicko (at the delve/endgame GDD sessions per doc 46).
7. CA-7: DT_WHAggressionProfile meter bands (section 3.3) are PROPOSED structure over doc 12's alignment gates. Doc 12 owns which meters exist and their gates; the BAND boundaries (hostile/neutral/friendly thresholds) are tuning for GDD. Confirm the band split or hand to doc 57's meter schema pass. Assigned: Nicko.
8. CA-8: War-state rekeying contract (section 4.1): doc 13 war state swaps active row sets via DT_WHEncounterConfig keys. Confirm doc 55 (world and streaming) consumes the same config asset rather than authoring its own spawn tables, so AI module and world module do not fork table ownership. Assigned: Devbot authoring doc 55 (cross-spec contract), flagged to IO.

## Spec conflicts (this doc vs sources)

- None live. One tension noted, not a conflict: doc 34 section 6's camp-ambush row and doc 51 section 3.1's raid sets both stage camp threats; this doc routes both through DT_WHCampThreat with distinct trigger columns (2.4/4.2), treating doc 51 as the content superset of doc 34's slice-biome table. If doc 34's slice table is meant to stay slice-canonical, that is a provenance note, not a ruling conflict (see CA-2 shape precedent).
- Doc 46 OQ-8/OQ-9: referenced as open, no derivation (constraint; doc 52 register).
- Doc 54 CB-4: referenced as open (CA-4), not resolved here.

## Completion report

- Sections delivered: 1 ENEMY AI STATE MACHINE, 2 PAIR/PACK GRAMMARS AND SPAWN RULES, 3 WORLD LEDGER READ HOOKS, 4 ENCOUNTER TABLES WIRING, 5 TEST PLAN. Plus cited CONVENTIONS header and this report.
- Counts: classes 3 (AWHEnemyAIController, UWHEnemyBrainComponent, UWHGroupCoordinatorComponent), subsystems 1 (UWHSpawnPersistenceSubsystem), interfaces 1 (UWHWorldLedgerReadInterface), enums 4 (EWHAIState, EWHPerceptionChannel in the event struct's type, EWHPawnGrammar, EWHEncounterFamily plus supporting enums EWHBiome/EWHSiteState/EWHCourt/EWHWarState/EWHMeterBand/EWHRaidTrigger reused-or-PROPOSED), structs 6 (FWHAIPerceptionEvent, FWHTauntEvent, FWHEncounterRow, FWHSpawnSlot referenced, FWHCampThreatRow, FWHRaidConfig referenced). DataTables: 6 (DT_WHAIPerception, DT_WHEncounterComposition, DT_WHEncounterConfig, DT_WHCampThreat, DT_WHAggressionProfile, DT_WHBossRemix).
- Open questions: CA-1..CA-8 (all assigned; CA-4 carries doc 54 CB-4 as open, not resolved).
- Spec conflicts: 0 live; 1 tension noted as provenance (camp-threat table consolidation, doc 34 slice table vs doc 51 superset).
- Hard constraints honored: no new mechanics, no new verbs, no GAS; no gameplay content (doc 51 pools are the content source, wired only); PROPOSED markers on invented numbers/names; no em dashes; under 700 lines; citations on every ruling-derived element; ledger gates as runtime data checks, no beat encodes a forbidden knowledge grant.
- Files created: this doc only. No git commands run; file left untracked.