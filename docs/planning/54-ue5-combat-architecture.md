# 54 - UE5.8 Combat Architecture Spec

Drafted 2026-09-16, UE5.8 combat architecture spec (doc 31 engine plan governs: custom action stack, GAS deferred). PROPOSED for Nicko review. Subordinate to locked rulings; conflicts are open questions, not edits.

Module owner: the COMBAT module of the doc 52 spec set. Sources: doc 04 (verb grammar, locked), doc 32 (frame data, schema source), doc 34 (enemy side of the shared pipeline), doc 33 (formulas, equipment), doc 31 (engine plan, folder layout, budgets), doc 44 Part 8 (lever rule) and Part 2 (ledger gates), doc 52 (boundaries). Doc 53 owns the input side of the input buffer; this doc owns the interface. Doc 56 owns enemy AI internals; this doc owns the shared damage interface they call. Doc 57 owns the ledger runtime; this doc cites its gates, never encodes them. Changes no mechanic.

## Section 1: UCombatComponent STATE MACHINE

### 1.1 Class signature (header level)

Doc 31 lock: one C++ component owns the action stack. GAS deferred; the migration appendix (Section 7) records the shape only.

```cpp
// /WH/Combat/UCombatComponent.h
UCLASS(ClassGroup=(WHCombat), meta=(BlueprintSpawnableComponent))
class WHCOMBAT_API UCombatComponent : public UActorComponent
{
    // Owning the action stack: one active action + a one-slot input buffer.
    // States are data-driven from DT_FrameData (Section 2); no per-verb
    // branching in C++ beyond the verb enum dispatch.
    void      PushAction(FWHActionHandle Handle);      // stack push
    void      CancelActive(EWHCancelReason Reason);     // cancel rules, 1.4
    void      BufferInput(EWHVerb Verb, FWHInputStamp Stamp); // 1.5 contract
    FWHActionHandle PeekActive() const;

    // Calculator entry points (Section 3), called by hit events on both
    // sides. Same interface serves player and AI pawns (doc 34 grammar).
    void      ApplyHit(const FWHHitEvent& Event);
    void      OnPoiseBroken(const FWHHitEvent& Event);
    void      OnStaminaBreak();
    void      OnDeath(const FWHDeathContext& Ctx);

    // DataTable registry reads (doc 53 owns the registry; we consume).
    const FWHFrameDataRow* FindRow(FName RowId) const;

private:
    EWHCombatState   State;            // Idle/Startup/Active/Recovery/Block/Stagger/Downed/Dead
    float            StateElapsed;     // frames at 60 fps fixed-step combat tick
    TArray<FWHActionHandle> ActionStack;  // depth 1 at slice 1 (PROPOSED)
    FWHInputBuffer   Buffer;           // 1.5
    FTimerHandle     RegenDelayHandle; // stamina/poise regen, doc 33 rates
};
```

- Tick group: `TG_PrePhysics`, fixed-step combat clock at 60 fps decoupled from render (doc 31's 2 ms game-thread combat budget, G23). Frame counters in all DataTables are 60 fps frames; the component converts to seconds once.
- The component is class-agnostic: the same UCombatComponent runs on the player pawn and every AI pawn. Doc 34's agents consume identical frame rows; only their decision layer (doc 56) differs.
- Facing per doc 04 bake-in: logical facing = last input; defensive poses (block, parry, Wall of Steel, Firm Stance) snap their directional view to logical facing. Arcs in DT_FrameData resolve against logical facing, per doc 28 (PROPOSED there, carried).

### 1.2 States

States are data-driven: each DT_FrameData row names its startup/active/recovery frame counts; the state machine is a small interpreter over those numbers. No Blueprint per-state logic at slice 1.

| State | Entered by | Exits to | Source |
|---|---|---|---|
| Idle | default, recovery end | Startup (any verb), Block, Roll | doc 04 verbs |
| Startup | action push | Active at row's startup frames | doc 32 4.1 |
| Active | startup end | Recovery at row's active frames; hit events fire here | doc 32 4.1 |
| Recovery | active end | Idle; cancel window rules 1.4 | doc 32 4.1 |
| Block (hold) | block input held | BlockHit on hit; Parry on tap-window hit; Idle on release | doc 32 4.3-4.4 |
| Roll | roll input, band row | Idle at band total; i-frame window inside | doc 32 4.2, LOCKED bands |
| Stagger | poise break (Section 3) | Idle at stagger duration | doc 04 locked, doc 33: 1.20 s |
| StaminaBreak | 0 stamina from any action | Idle at break duration | doc 33: 1.50 s (PROPOSED tuning) |
| Downed | Bonecracker-class effects | Idle at downed duration | doc 04: upgraded stagger |
| Dead | health 0 | Death clip, then corpse/respawn flow (Section 3.6) | doc 04 death penalty locked |
| Aim (mode flag, not stack state) | aim-mode input | overlays Idle/Block; stationary gate for charge-up casts | doc 04 dual-mode lock |

Aim is a mode flag rather than a stack state so the player can hold aim while blocked or idle exactly as doc 04's dual-mode lock describes; charge-up casts refuse while moving by input gating (doc 53's side), not by state machine rule.

### 1.3 State diagram per verb

Windows are from DT_FrameData rows (doc 32 4.1-4.3, values carried verbatim; all PROPOSED except the locked roll bands and block arcs):

```
LIGHT ATTACK (Long Blade LA1 reference)
  [0-6  Startup] [7-10 Active] [11-22 Recovery]
  chain cancel: LA1 f14-20 into LA2 (doc 32 4.1)
HEAVY ATTACK   [0-13 Startup] [14-19 Active] [20-39 Recovery]
CHARGED HEAVY  hold 0.60 s (36 f) gate, then [0-19/20-27/28-47]
ROLL           fast 30 f / std 37 f / slow 48 f; i-frames late window from f12
               (fast f12-23 = 11 f, std f12-18 = 6 f, slow f12-15 = 3 f)
BLOCK          raise 8 f to full 120 deg arc; hold consumes on BlockHit
PARRY (tap)    active window opens at f4 after input; per-source windows (1.4)
LOCK-ON        toggle/soft-switch: acquire 18 m, break 24 m, blend 12 f (doc 32 4.6)
SPRINT         hold, 8 stamina/s at 6.0 m/s; drains, no state machine state
```

Sprite-side contract (doc 32 section 3 clips): startup+active+recovery sums equal the authored clip lengths (LA1 6+4+12 = 22 f; heavy 14+6+20 = 40 f; charged 20+8+20 = 48 f). The state machine reads the same row the animator authored against; there is one source of truth.

### 1.4 Cancel rules

| From | Into | Rule | Source |
|---|---|---|---|
| LA1 recovery (f14-20) | LA2 | chain cancel window | doc 32 4.1 |
| Any attack recovery | Roll | roll-cancel at recovery start +0 f (PROPOSED: whole recovery is roll-cancel legal; souls standard) | doc 04 roll verb |
| Any attack recovery | Block raise | cancel into block allowed (PROPOSED: at f4 into recovery) | doc 04 block verb |
| Block hold | Parry tap | same input key, tap vs hold discrimination per doc 32 0.30 s tap threshold | doc 32 section 1 |
| Stagger | nothing | committed; no cancel (the punish window is the point) | doc 04 locked |
| StaminaBreak | nothing | no actions for the full 1.50 s | doc 33 |
| Potion drink | walk-cancel after f30 | cancel-locked f1-f29 | doc 32 4.5 |
| Attack recovery | Technique moves | technique rows carry their own cancel entries in DT_FrameData (Section 2; doc 04 menus govern which exist; no new verbs here) | doc 04 locked menus |

### 1.5 Input-buffer contract

- Interface in: `BufferInput(EWHVerb Verb, FWHInputStamp Stamp)` where the stamp carries press frame and hold duration so tap/hold discrimination (0.30 s threshold, doc 32 section 1) resolves inside combat, not input.
- Buffer depth: 1 slot (PROPOSED). A buffered verb executes at the first frame the state machine accepts it: recovery end for attacks, block release for parry-tap, idle for anything.
- Buffer lifetime: 0.25 s (15 f, PROPOSED) then dropped. Souls-standard forgiveness without combo autocorrect.
- Doc 53 owns the input mapping side (the doc 32 tables are its source); the contract here is only the FWHInputStamp struct and the consume order: buffered verb > new verb > nothing.

### 1.6 Hit-stop and i-frames wiring

Doc 04 bake-in rule, doc 31 zero-particle VFX budget: hit feedback is engine-side, not particle-side.

- HIT-STOP: on a landed hit, both attacker and victim enter a global time dilation of the combat clock: N frames of stop where N = the row's HitStopFrames column (Section 2; PROPOSED values carried from doc 34 5.x light hits: 3 f, PROPOSED). Implemented as combat-clock freeze (the fixed-step accumulator stops), never as global time dilation: the doc 32 rule that view reselection hides inside hit-stop requires the camera to keep ticking.
- CONTACT FLASH: material-parameter flash on the impact accent per the pixel register material (doc 31 VFX line; doc 02 pillar 3 diegetic light, no particle realism). One material param set call, zero particles.
- CAMERA SHAKE: doc 32 numbers, 0.25 m amplitude, 0.30 s decay, max 2 simultaneous sources.
- I-FRAMES: the roll rows carry the window (f12-f23 / f12-f18 / f12-f15 by band, doc 32 4.2 LOCKED bands). Implementation: the combat clock checks an IFrameActive flag on the defender before the hit resolves; i-frame hits produce the Slip the Blade event hook (doc 04 Expert menu) but no damage, no poise, no hit-stop.

## Section 2: FRAME-DATA DataTable SCHEMA

Path: `/WH/Data/FrameData` (doc 31 folder layout: /WH/Data holds Tables: FrameData, StaminaCosts, PoiseValues, DamageTable). Four DataTables. Every numeric value is PROPOSED and GDD-tunable; the schema is the deliverable.

### 2.1 DT_FrameData (one row per attack/verb instance)

Columns follow doc 32's tables exactly; row IDs name verb + step (e.g. `LongBlade_LA1`).

| Column | Type | Notes |
|---|---|---|
| RowName | FName | `WeaponClass_Verb[_Step]` |
| AttackName | FName | display/debug name |
| VerbClass | EWHVerb (uint8) | Light, Heavy, ChargedHeavy, Roll, Block, Parry, Riposte, Backstab, LockOn, Sprint, Technique |
| WeaponClass | EWHWeaponClass (uint8) | 9 classes, doc 33 section 3 |
| StartupFrames | int32 | f at 60 fps |
| ActiveFrames | int32 | |
| RecoveryFrames | int32 | startup+active+recovery must equal clip length (doc 32 check) |
| StaminaCost | int32 | cross-checked against DT_StaminaCosts |
| PoiseDamage | int32 | pre-multiplier base |
| StaggerThreshold | int32 | 0 = uses defender's poise pool (normal path); nonzero = guaranteed-stagger overrides (Skullringer class effects; PROPOSED encoding) |
| DamageBase | int32 | pre-multiplier base; final damage always derives via Section 3, never from this column alone (doc 39: catalog carries no damage numbers, they derive) |
| HitStopFrames | int32 | PROPOSED: light 3, heavy 5, charged 7 |
| IFrameFlag | bool | roll rows only |
| IFrameWindowStart | int32 | f12 every band (doc 32 4.2) |
| IFrameWindowEnd | int32 | f23 / f18 / f15 by band |
| RangeMeters | float | reach band per doc 33 section 3 |
| ArcDegrees | float | attack arc vs logical facing (doc 28 facing rule) |
| CancelWindowStart | int32 | -1 = none |
| CancelWindowEnd | int32 | |
| CancelTargetVerb | EWHVerb | LA1 -> Light |
| ClipID | FName | doc 32 section 3 clip reference |

Seed rows: exactly the doc 32 4.1 Long Blade table (LA1 6/4/12, LA2 5/4/13, LA3 6/5/19, Heavy 14/6/20, Charged 20/8/20), the doc 32 4.2 roll bands, and the doc 32 4.3 parry windows as Parry rows (shield 10 f, Riposte Master 14 f, Twin-Parry 12 f, Lever Guard 8 f, bare blade 6 f, enemy soldier 5 f; riposte 45 f active f10-f24). No new rows invented; technique rows arrive when doc 04's 108 locked techniques enter implementation (their menus are locked; their frame data is a tuning pass, CB-3).

### 2.2 DT_StaminaCosts

| Column | Type | Seed (doc 32; PROPOSED except where locked) |
|---|---|---|
| RowName | FName | |
| EWHVerb | uint8 | |
| StaminaCost | int32 | light 12, heavy 25, charged heavy 40, block-hit absorb 10 + 2x incoming poise damage, parry attempt 8, roll 22/26/32 by band, sprint drain 8/s |
| RegenPauseFrames | int32 | 60 f (1.00 s) after any stamina action |
| RegenRateIdle | float | 25 stamina/s |
| RegenRateBlocking | float | 12.5 stamina/s (50 percent cut) |
| RegenRateAttacking | float | 2 stamina/s |
| StaminaBreakFrames | int32 | 90 f / 1.50 s (PROPOSED tuning) |

Pool formula stays in C++ (stamina = 80 + Stamina stat x 0.8, doc 33 section 8); the table stores costs and rates only, so GDD tuning never recompiles.

### 2.3 DT_PoiseValues

| Column | Type | Seed (doc 33 section 8 / doc 32 4.4; all PROPOSED) |
|---|---|---|
| RowName | FName | armor class x size key |
| WeightClassFactor | float | light 1.0, medium 1.5, heavy 2.2 |
| SizeFactor | float | small 0.8, medium 1.0, large 1.6, boss 3.0 |
| PoisePool | int32 | = 30 x weight x size (medium human 45; bandit 45; wolf 40; boss remix 135; doc 34 blocks) |
| PoiseRegenDelaySeconds | float | 4.00 s to full (doc 33); doc 04's "a few seconds" governs |
| ChipPoiseThroughBlock | float | 30 percent of listed poise damage |
| StaggerFrames | int32 | 72 f / 1.20 s committed; +15 f under Concussive Force-class effects |
| DownedBonusDamageMultiplier | float | doc 04 Bonecracker: downed take bonus damage (value PROPOSED 1.25) |

### 2.4 DT_DamageTable

| Column | Type | Seed (doc 33 sections 5-7) |
|---|---|---|
| RowName | FName | source id (weapon row, spell id, creature verb) |
| DamageBase | int32 | doc 33 section 3 class baseline at T1 grade B rank 1 |
| DamageType | EWHDamageType (uint8) | Physical, plus the three damage-carrying schools (Pyromancy, Storm, Cryomancy) per doc 41's note; Holy Wards / Dark Pacts ride spell ids |
| TierMultiplier | float | T1 1.00, T2 1.35, T3 1.75, T4 2.20, T5 2.70 |
| GradeMultiplier | float | C 0.90, B 1.00, A 1.10, S 1.20 |
| BleedPerSecond | int32 | Axes: 3/s for 5.00 s, max 3 stacks (doc 33) |
| MagicTagged | bool | true rows resolve Ward percent step (Section 3.3) |

The formulas that consume these tables live in C++ (Section 3), never as derived columns; DT_DamageTable stores inputs, the calculator owns the math (doc 33 section 6 is the cited authority).

## Section 3: DAMAGE/POISE/STAGGER PIPELINE

One C++ calculator chain, one shared interface for player and AI (doc 34 grammar lock: enemies use the player's verbs and the same math). Structure:

```cpp
// /WH/Combat/WHDamagePipeline.h
struct FWHHitEvent
{
    TWeakObjectPtr<AActor> Attacker, Defender;
    FName  AttackRowId;        // DT_FrameData row
    bool   bDefenderBlocking;
    bool   bDeframerIFrames;   // roll i-frame flag resolved before entry
    bool   bAttackerTwoHanded; // x1.25, doc 33 section 4
    EWHVerb Verb;              // heavy resolves x1.50 / x2.0 poise here
    float  BlockFacingDot;     // arc test vs logical facing
};

UCLASS()
class UWHDamagePipeline : public UBlueprintFunctionLibrary
{
    static void ResolveHit(const FWHHitEvent& E);        // 3.1-3.4
    static float CalcRawDamage(const FWHHitEvent& E);    // doc 33 sec 5-6
    static void  ApplyPoise(const FWHHitEvent& E, float Raw);
    static void  TriggerHitStop(const FWHHitEvent& E);   // 1.6
};
```

### 3.1 Hit event

A hit resolves when an Active-window overlap fires (attack sphere vs defender capsule) and the defender's IFrameActive is false. Order of tests, cheapest first: i-frame flag -> facing/arc test (block validity, 120 deg base arc, doc 32 4.4; Firm Stance 160 deg) -> parry window test -> block -> clean hit. Every test reads DT_FrameData / DT_PoiseValues; nothing is hard-coded.

### 3.2 Damage calc (doc 33 section 6, cited, unchanged)

1. Attacker: W = DT_DamageTable DamageBase x tier x grade x skill (1 + 0.003 x rank). Two-hand x1.25; heavy x1.50. Crit roll: chance = 5 + Precision x 0.25 capped 30 percent; multiplier 1.5 + Precision x 0.005; guaranteed-crit rows skip the roll (doc 04: Deadeye, Sharpshooter's Calm, Fang Flurry on staggered foes).
2. Defender percent: Ward fraction = min(0.60, Ward x 0.005) vs spells and magic-tagged hits; physical uses enchant wards only (doc 17 armor wards).
3. Flat: armor, with the floor: final = max(floor(raw x 0.15), raw - flat armor). Round to integer, minimum 1, single hits cap 999.

### 3.3 Poise damage vs threshold

- Poise damage = row's PoiseDamage x tier x grade x skill x heavy-multiplier (2.0x heavies, doc 33 section 3 note) x class modifier (Blunt +50 percent, doc 33: deliberately double Short Blade's).
- Blocked hits transfer 30 percent chip poise (doc 04 lock; DT_PoiseValues ChipPoiseThroughBlock). Block-hit stamina cost on the defender: 10 + 2x incoming poise damage (doc 33 section 8).
- Pool: DT_PoiseValues row by the defender's armor weight class x size. Poise broken = STAGGER: 1.20 s (72 f) committed recovery, extended +15 f by Concussive Force-class effects; doc 04's technique interactions (Momentum of Ruin stacking, Pressure Strike extending) read the same stagger event, no new state.

### 3.4 Stagger state and hit-stop trigger

- On poise break the pipeline calls `OnPoiseBroken` on the defender's UCombatComponent (Stagger state, 1.2) and the attacker's Momentum-of-Ruin-style buff hooks listen as an event, not a pipeline branch.
- Hit-stop fires on every resolved hit (clean, blocked, or parried) at the row's HitStopFrames; parry success adds the attacker's punish-window grant per the doc 32 4.3 reward column (normal riposte 18 f window vs heavy counter 30 f window by source).

### 3.5 Death/respawn hookup

On health 0: Dead state, doc 32's 30 f death clip, then the drop context fires: XP/currency dropped at corpse, recoverable (doc 04 LOCKED). Respawn reads the save/respawn layer owned by doc 53: the tavern door respawn is doc 53's save-point implementation per doc 09 (tavern rooms set respawn; warp camp is the default forward respawn once unlocked). This doc only declares the interface: `FWHDeathContext` carries killer id, region id, and whether a camp or tavern owns the next respawn; doc 53/doc 09 own which.

### 3.6 Fairness floor

Doc 46 audit language pattern (base stats never touched by presentation-layer multipliers is the Kaiju pattern): Witch Hunter's analog is the doc 44 Part 2 ledger gate. Concretely in this pipeline:

- Enemy stats never read player level or region progress: DT_DamageTable / DT_PoiseValues rows are authored per stat block (doc 34's Bandit 180 / Rot Wolf 140 / Grave Ghoul 220 / Rot-Mother 900, locked). Difficulty is FIXED per region (doc 04 lock); the pipeline has no scaling multiplier input at all.
- The player-side fairness floor: no combat-path multiplier may alter the doc 33 formulas' inputs except the declared ones (tier, grade, skill, two-hand, heavy, crit). There is no "difficulty multiplier" hook anywhere in the chain; story-mode easing, if ever wanted, is a doc 08 open question, not a silent knob (CB-5).
- Ledger gate (doc 44 Part 2, enforced by doc 57's runtime structure): the pipeline is content-blind. No damage calc, stagger beat, or death beat may encode a forbidden-knowledge grant; what a defeated boss-warden's defeat event reveals is a doc 57 reveal-gate lookup, never a combat-side fact. See Section 5.3.

## Section 4: WEAPON CLASSES

Doc 04's nine combat skill lines are the class enum; slice 1 builds Long Blade fully (doc 32 reference weapon). The doc 33/39/40 catalog schema becomes DataTables; this doc authors the schema and the verb-set wiring, no new math (doc 39 ruling 1: damage derives from class row x tier x grade x skill, no new numbers here).

### 4.1 DT_WeaponClass verbs

| Column | Type | Notes |
|---|---|---|
| RowName | EWHWeaponClass (uint8) | 9 rows: ShortBlade, LongBlade, Blunt, Axes, Polearms, Archery, DualWield, Shield, Unarmed |
| VerbSet | bit mask of EWHVerb | which verbs the class's DT_FrameData rows exist for |
| DamageBase | int32 | doc 33 section 3 baseline |
| StaminaCost | int32 | light-attack cost; heavy = 1.7x (doc 33) |
| PoiseDamage | int32 | per light hit |
| SpeedFrames | int32 | light-attack total time (doc 33 table: LongBlade 33 f / 0.55 s) |
| ReachMeters | float | range band |
| HeavyDamageMult | float | 1.50 (doc 33 section 5) |
| HeavyPoiseMult | float | 2.00 (doc 33 section 3) |
| ParrySource | EWHParrySource (uint8) | Shield, RiposteMaster, TwinParry, LeverGuard, BareBlade, None; window sizes read doc 32 4.3 ordering (shield 10 f > Riposte Master 14 f > Twin-Parry 12 f > Lever Guard 8 f > bare blade 6 f; enemy soldiers 5 f, telegraphed) |

### 4.2 DT_Weapon catalog rows (per doc 39)

| Column | Type | Notes |
|---|---|---|
| RowName | FName | doc 39's named rows (Hunter's Dirk, Silvered Poniard...) |
| WeaponClass | uint8 | |
| Tier | int32 | T1-T5 |
| Grade | uint8 | C/B/A/S |
| PrimaryMaterial | FName | doc 39 part 1 ladders |
| FrameOverrides | FName | optional DT_FrameData row override (per-weapon reach/frame deltas; PROPOSED encoding: empty = class rows) |
| ShieldBlockGrammar | uint8 | for shields: block-stability class, bash row id; shields never two-hand (doc 33 section 4) |

Reach/frame overrides exist because doc 39's per-tier named weapons are the natural place GDD tuning will want per-weapon flavor without new classes (PROPOSED: overrides are stat-only, never new verbs).

### 4.3 Shield block grammar

Block is a verb, not a passive: raise 8 f to full arc, 120 deg base (160 with Firm Stance, doc 32 4.4), block-hit absorb 10 + 2x incoming poise stamina, chip poise 30 percent through (doc 04 lock). Shield parry is the widest window (10 f) with the normal riposte reward; Riposte Master extends to 14 f and makes the riposte poise-breaking (doc 04 menu, carried). Bulwark's N-free-blocks is a DT_FrameData flag on the technique row (N PROPOSED 3), not a new state.

### 4.4 Remix rule wiring (doc 04: dungeons teach a pool, boss remixes it)

Composition pattern, no new mechanic: a boss chassis is an enemy stat-block row (doc 34 5.4 pattern: pool chassis, size factor 3.0) plus two-to-three remixed pool verbs, each a DT_FrameData row whose RowName points at the pool verb's row with a re-costed damage/poise entry (doc 34's Rot-Mother is the reference: ghoul chassis, Wail of Despair and a summon re-costed from the pool). UCombatComponent cannot tell a boss row from a bandit row; the remix lives entirely in data. Doc 56 owns which pool verbs a given boss remixes; this doc owns the row shape that makes remixing a data edit.

## Section 5: DELVE/LEVER COMBAT HOOKS (doc 44 Part 8)

Doc 44 Part 8 lock: the three altars are the endgame dungeons, one per affinity; each altar = a unique long dungeon = the chain's lever; lever pulled = witch's hand forced. Doc 55 owns delve layouts; doc 47 owns delve content. This section wires the combat encounters and the forced-hand consequence, interface only.

### 5.1 Final chambers as combat encounters

Each delve's final chamber holds the altar as a destructible-or-activatable objective with a boss-warden guard (doc 47's warden concepts; stat blocks defer to doc 34's bestiary pass, AD-2 there). Combat encoding per affinity:

| Delve | Chain | Final-chamber combat act | Source |
|---|---|---|---|
| Sun Altar (beneath the New Capital) | light | destroy-or-sever the living altar; objective entity with a poise/health pool like any stat block; destroying (or severing) is a damage-pipeline completion event, no new verb | doc 44 Part 8, doc 47 |
| Veil Altar (beneath the Veil Spire) | dark | destroy what remains of the Veil working; same completion event | doc 44 Part 8 |
| Deep Altar (behind the Hidden Court's den) | neutral | re-kindling: activate objective guarded by the chamber's warden; the re-kindling IS the rival-engine event | doc 44 Part 8 |

The altar objective is a UCombatComponent-bearing actor with a DT_FrameData row (it can be hit, staggered, destroyed) so the existing pipeline destroys it with zero new code. "Sever" vs "destroy" on the Sun altar is a completion-event payload flag, resolved at quest GDD (doc 47's open item), not a second verb.

### 5.2 Lever rule: forced-hand consequence wiring

Doc 44 Part 8 lever lock: striking the heart of the machine FORCES HER HAND; per path the forced response differs (light: machine retaliation, chaos escalation, regicide push; dark: creditor's mask drops patience, brutal tithe escalation, early-hot bankruptcy fork; neutral: the Pale Queen uses the re-kindled altar as a rival engine, which forces the Last Dance, doc 36 ruling 2).

Interface only (delve layouts and escalation content are docs 47/55/quest GDD):

```cpp
// /WH/Combat/WHDelveCombatHooks.h  (interface; quest system subscribes)
DECLARE_MULTICAST_DELEGATE_OneParam(FOnAltarLeverPulled, EWHAltarId /*Sun, Veil, Deep*/);
// Fired by the altar objective's completion event (5.1). The quest layer,
// not combat, decides what "hand forced" means per chain (doc 44 Part 8).
```

The combat module's whole obligation is: the altar is hittable through the standard pipeline, and its destruction/re-kindling emits exactly one lever event. No combat beat may author the consequence.

### 5.3 Ledger gate (doc 44 Part 2; runtime structure owned by doc 57)

HARD GATE: no combat beat encodes a doc 44 Part 2 forbidden-knowledge grant.

- The creditor's face is ledger-locked to the mid-ritual reveal in the neutral ending (doc 36 ruling 1; doc 44 Part 2 Dark Queen and Pale Queen cells: neither knows who the creditor is until she learns mid-ritual, and her reaction is a live player-choice beat). No combat encounter anywhere in any delve, arena, or ambush may expose the creditor's face, voice-as-identification, or any reveal-equivalent, because no combat beat can carry a knowledge grant.
- Runtime shape: reveal gates are a doc 57 World-Ledger data structure (knowledge-ledger reveal gates, doc 52's doc 57 row). Combat exposes a query interface only:

```cpp
// /WH/Combat/WHKnowledgeGateQuery.h (interface only; doc 57 owns the ledger)
bool WH_CanVisualPresent(FName PresentationId);
// The altar-chamber presentation set, boss-warden intro cinematics, and any
// creditor-adjacent visual query this gate before rendering. Default-denies.
```

- Identity rules carried unchanged (doc 44 / doc 36): the Signer is the witch's mask; the Pale Queen is the separate neutral vampire leading the brokers (Part 7 ruling 4); the light queen is Queen Maren of the Dawn. No combat presentation may contradict the mask ruling: the witch's true face is old and twisted and never appears at court, no face recognition is possible (doc 36 locked), so no sprite, portrait, or hit-flash visual may depict the creditor's face outside the mid-ritual beat's ownership (quest GDD, doc 36).

## Section 6: TEST PLAN

Testerbot validates against the doc 32 frame-data tables and the doc 31 budgets. Automated first, editor-validated second.

### 6.1 Schema presence (automated)

- Asset scan: `/Game/WH/Data/` contains DT_FrameData, DT_StaminaCosts, DT_PoiseValues, DT_DamageTable, DT_WeaponClass, DT_Weapon. Failure = named missing table.
- Column check: each table's columns match Section 2/4 schemas exactly (name + type). Failure names the column.
- Row-presence check: every doc 32 4.1-4.6 entry resolves to a row: LongBlade_LA1/LA2/LA3, Heavy, ChargedHeavy, Roll_Fast/Standard/Slow, Parry_Shield/RiposteMaster/TwinParry/LeverGuard/BareBlade/EnemySoldier, plus DT_PoiseValues rows for LightArmor/MediumArmor/HeavyArmor/Bandit/Wolf/BossRemix and DT_DamageTable rows for the 9 class baselines (doc 33 section 3).

### 6.2 Value-range and consistency checks (automated)

- Startup+active+recovery equals clip length for every DT_FrameData row whose ClipID is non-empty (doc 32's own check: LA1 6+4+12 = 22 f; heavy 40 f; charged 48 f). This check runs in-editor on save and in CI.
- Parry-window ordering matches doc 04 exactly: shield (10 f) > Riposte Master (14 f) > Twin-Parry (12 f) > Lever Guard (8 f) > bare blade (6 f); enemy soldier 5 f. Grep: `Parry.*f/0\.[0-9]+ s` against the doc 32 4.3 table.
- Roll bands match the LOCKED doc 32 4.2 values: fast 30 f / 11 i-frames / 22 stamina, standard 37 f / 6 / 26, slow 48 f / 3 / 32, late window at f12 in every band, roll disabled above 30.0 load.
- Poise math spot-check: medium human = 45 (30 x 1.5 x 1.0); boss remix factor 3.0; chip poise 30 percent. The doc 33 section 11 worked example (bandit sequence, ~6.2 s, 98/100 stamina) is a scripted integration assert.
- Stamina regen rates: 25 idle / 12.5 blocking / 2 attacking; 1.00 s pause after any stamina action.
- Grep checks (exact, run over DT_* CSV/JSON exports and the doc itself): `HitStopFrames` present and 3 f on light rows; `IFrameWindowStart.*12` on all roll rows; `ChipPoise.*30`; `StaggerFrames.*72`; no row carries a damage number outside the 1-999 cap.

### 6.3 Doc 32 acceptance hooks

The acceptance hooks doc 32 names are the tests above verbatim: sum-matching (its section 5 checks one through five), the no-estus drink check (40 f drink, effect at f30, cancel-locked f1-f29), the 16-view rule applying to every directional clip except idle/walk 4-frame ambient, and lock-on parameters (18 m acquire, 24 m break, 180 deg/s camera cap).

### 6.4 The 8-enemy orbit perf test (doc 31 G23)

Wiring: a scripted arena map (WH_Arena_Darkwood, doc 31) runs 8 Bandit agents orbiting the player at night fog settings, all agents on the shared pipeline and doc 34 stat blocks. Pass bar: 60 fps at 1080p output / 720p internal point-sampled upscale, 2 ms game-thread combat logic, 0 hitches above 33 ms over 5 minutes, under 1,500 draw calls, under 2 M triangles, under 20 skinned meshes. The combat module's obligation: UCombatComponent and the pipeline stay allocation-free during the run (no per-hit spawning; hit-stop is clock arithmetic; feedback is material params and camera shake only, zero particles per doc 31).

### 6.5 Manual validation gates

- M3 feel pass (doc 31): frame table live in DataTables, hit-stop and i-frames functional; iteration-only.
- Parry-window feel: all five player-facing windows played in order of width; punish rewards match doc 32 4.3.
- Charged-heavy hold 0.60 s trigger-curve validation on controller (doc 32 open item, M2).

## Section 7: GAS MIGRATION APPENDIX (shape only, deferred per doc 31)

GAS stays deferred; adoption gate at slice exit when the first technique menu lands (doc 31). The migration shape, recorded not built:

- UCombatComponent's action stack maps to GAS Abilities; the startup/active/recovery states map to Ability tasks (WaitDelay/WaitTargetData equivalents); DT_FrameData rows map to Attribute Sets plus Gameplay Effect durations in frames.
- Damage pipeline maps to an ExecCalc (doc 33 section 6 formulas as the calculation graph); poise/stagger map to a secondary attribute set with its own tags; hit-stop maps to a global Gameplay Effect on the ability system.
- No AttributeSets, no GameplayEffects, no tags ship at slice 1. This appendix exists so the slice-exit gate decision is a mapping exercise, not a redesign.

## Open Questions (doc 08 format, numbered CB-1..n)

1. CB-1: Hit-stop frame values per verb class (Section 2.1 HitStopFrames seed 3/5/7 light/heavy/charged). Owner: GDD combat pass with Nicko; doc 32 has no hit-stop numbers, this doc invented the seed (PROPOSED).
2. CB-2: Guaranteed-stagger encoding (Section 2.1 StaggerThreshold override flag) vs a separate DT_EffectFlags table if techniques need richer flags. Owner: Devbot at implementation, flagged for Nicko at M3.
3. CB-3: Frame data for the 108 locked techniques (doc 04 menus): which techniques ship with slice-1-relevant rows vs the techniques pass. Owner: Nicko scoping session; doc 32 already deferred shield-bash and off-hand timings.
4. CB-4: Boss-warden stat blocks for the three delve final chambers (Section 5.1). Owner: doc 34's bestiary pass (its own AD-2), referenced not derived here.
5. CB-5: Difficulty-accessibility knob inside fixed difficulty (Section 3.6): whether any player-side damage taken multiplier may ever exist without violating the doc 04 fixed-difficulty lock. Owner: Nicko ruling needed; nothing in this spec assumes a yes.
6. CB-6: Charged-heavy trigger curve on controller (0.60 s hold, doc 32 open item) affects DT_FrameData ChargedHeavy row gating. Owner: M2 controller validation, doc 32's open item carried.

## Spec conflicts

None. Every mechanic above traces to doc 04 (verbs, poise/stagger locks), doc 32 (frame data, the schema source), doc 33 (formulas, pools, armor), doc 34 (enemy stat blocks and grammar), doc 31 (custom stack, GAS deferral, budgets, folder layout), doc 44 Parts 2 and 8 (ledger gate, lever rule), doc 36 ruling 1 (creditor reveal timing), and doc 36/44 identity rulings. Where docs gave ranges this doc picked seeds and marked PROPOSED; where docs were silent (hit-stop frames, altar-objective encoding) this doc invented structure and marked PROPOSED or opened a CB question.

## Completion report

- Sections delivered: 1 (UCombatComponent state machine), 2 (frame-data DataTable schema: DT_FrameData, DT_StaminaCosts, DT_PoiseValues, DT_DamageTable), 3 (damage/poise/stagger pipeline), 4 (weapon classes: DT_WeaponClass verbs + DT_Weapon catalog + shield grammar + remix wiring), 5 (delve/lever combat hooks + ledger gate), 6 (test plan), plus the GAS migration appendix (shape only).
- Counts: 1 C++ component class + 1 pipeline class + 2 interface headers declared; 6 DataTable schemas (4 named by doc 31's Data list + 2 weapon-side); 9 weapon classes; 3 altar final-chamber combat encodings.
- Open questions: CB-1 through CB-6, each assigned (Section "Open Questions").
- Hard constraints honored: no new mechanics, no new verbs, no GAS adoption (appendix is shape-only); no em dashes; under 900 lines; PROPOSED markers on invented numbers; ledger compliance: no combat beat encodes a doc 44 Part 2 grant, the creditor's face is mid-ritual-only (doc 36 ruling 1), the Pale Queen never learns who the witch is, identity rules carried (Signer = witch's mask; Pale Queen = separate neutral vampire leading the brokers; light queen = Queen Maren of the Dawn).
- File status: single new file, untracked, no commits, no git write commands run.