# 57 - UE5.8 Data and World Ledger Architecture Spec

Drafted 2026-09-16, UE5.8 data and World Ledger architecture spec (doc 31 engine plan governs; GDDs 46-51 + planning corpus are the content source). PROPOSED for Nicko review. Subordinate to locked rulings; conflicts are open questions, not edits.

## Scope and reading rules

Module: DATA AND THE WORLD LEDGER (doc 52 spec-set row 57). This doc
authors engine structure only: the save-serializable ledger schema, the
deed log, faction and sect meters, quest frame templates, and the
knowledge-ledger reveal gates as runtime data structures. It authors no
gameplay content. Beats, lore, and the ledger tables' CONTENT belong to
docs 44 and 46; this doc mirrors their structure into UE5.8 data
containers and cites cell-by-cell.

Doc 53 stubs the container classes (UWHWorldLedgerSubsystem, section
2.2) and the naming conventions (section 1.4: FWH structs, DT_WH tables,
EWH enums, /Game/WH/Data/ registry). This doc fills the stubs' schema;
it does not restate doc 53's class bodies or serialization contract.

Source map (every tracked fact cites its owning doc):

| Ledger family | Owning doc | Cited content |
|---|---|---|
| Knowledge cells (knows/suspects/misses) | 44 Part 2 | the 11-fact table, verbatim states |
| Deed log grammar | 20 (World Ledger list) | kill, purge, sparing, cleansing, escort, protection, betrayal |
| Faction and sect meters | 12 | axis scale, siege-ladder thresholds, parish flip rules |
| Quest frames | 20 grammar + 46 Sections 1-4 | spine chains A-H, six doors, four tissue frames |
| Sentence sequences | 48 Sections 1-5 | four sentences, kill-or-break, Last Dance stubs |
| Save rules | 09 (locked) | camps save, taverns respawn, warp camp forward respawn |

Hard rule inherited from doc 52 gate rule 4: no architecture beat may
encode a fact a character's doc 44 Part 2 cell forbids. Section 2's
enforcement contract makes a forbidden grant impossible BY DATA, not by
convention (see 2.4).

GAS stays deferred (doc 31); nothing here adopts it.

---

## SECTION 1: WORLD LEDGER SCHEMA

Doc 53 owns UWHWorldLedgerSubsystem (the container interface and
serialization contract, section 2.2 stub: SetCell, FindCell,
OnCellChanged, ExportCells, ImportCells). This section owns WHAT the
cells contain: the cell families, the row structs at header-signature
level, and the per-cell source citations.

### 1.1 Cell grammar

One cell = one serializable world-state slot, keyed by CellId (FName),
per doc 53's stub. Doc 53's FWHLedgerCell carries CellId, CellFamily,
IntValue, FloatValue, StringValue, VersionTag (all SaveGame). This doc
fixes the taxonomy those fields carry.

CellId grammar (PROPOSED, dot-separated, stable FNames):

```
<family>.<subject>.<key>
```

| Family (EWHLedgerCellFamily, EWH enum) | Subject slot | Key slot | Int/Float/String payload | Source doc |
|---|---|---|---|---|
| Warmomentum | hold id | none | int: owner court side | 13, 20 |
| Debttension | court side (dark only reads nonzero) | none | int: 0..100 band index | 19, 20 (hidden until discovery arc) |
| Axisposition | player | none | int: -100..100 | 12 |
| Courtstanding | court side | none | int: -100..100 ladder points | 12 (locked thresholds) |
| Sectmeter | parish id | none | int: -100..100 (Militant<->Mercy) | 20 Parish-Flip, 19 Schism |
| Standingmeter | door id (doc 46 six doors) | none | int: 0..100 | 46 Section 2 (PROPOSED bands) |
| Deedlog | entry index | none | string: serialized FWHDeedLogEntry | 20, 13 |
| Worldflag | flag id | none | int: 0/1 set + string: tag payload | 20 unresolved consequences |
| Knowledgecell | character id | fact id | int: EWHKnowledgeState | 44 Part 2 |
| Questframe | frame instance id | none | string: template id + state tags | 20, 46 Section 4 |
| Sentencestate | ending fork id | none | string: doc 48 stub id | 48, 36 ruling 5 |

Rules:
- Every cell's row in its owning DataTable carries a SourceDoc column
  (FName, e.g. "44-P2", "12", "46-S2"). A cell written without a
  registered family (CellFamily not in EWHLedgerCellFamily) is rejected
  at SetCell with a fatal log, mirroring doc 53's registry fail-fast.
- Procedural systems write ONLY into the Tissue-payload families
  (Deedlog, Worldflag, Questframe, Sectmeter, Standingmeter); spine
  families (Sentencestate, Knowledgecell) are hand-authored data only
  (doc 20 locked two-tier rule, made mechanical here).
- Ledger mutations flush in tick group 3 only (doc 53 section 2.4
  contract); callers outside group 3 enqueue through the subsystem's
  internal queue (doc 53 states the queue; this doc consumes it).

### 1.2 Deed log entries

Doc 20's World Ledger list owns the deed log as a structured record.
Row struct (header-signature level, FWH prefix per doc 53 section 1.4):

```cpp
USTRUCT(BlueprintType)
struct FWHDeedLogEntry {
    UPROPERTY(SaveGame) FName DeedId;        // stable per-entry id
    UPROPERTY(SaveGame) EWHDeedCategory Category;
    UPROPERTY(SaveGame) FName SubjectId;     // NPC/faction/hold acted on
    UPROPERTY(SaveGame) FName HoldId;        // where it happened
    UPROPERTY(SaveGame) int32 DayStamp;      // in-game day
    UPROPERTY(SaveGame) bool bWitnessed;     // doc 03/19 grudge rule input
};
```

EWHDeedCategory (EWH enum), one enumerator per doc 20's deed list, each
citing its feeding doc: Kill (doc 20), Purge (doc 20, Militant-weighted
per doc 19), Sparing (doc 20, Mercy feed), Cleansing (doc 17 Purify
economy via doc 20), Escort (doc 20), Protection (doc 20; also Mercy's
deed category per doc 45 L8 via doc 46 beat H-A3), Betrayal (doc 20),
PurgeContract (doc 46 Section 4 purge-contract frame: deed log quietly
records the purge), FeudMediation (doc 46 beat D6-2 citing doc 13),
GraveRobbing (doc 46 beat D2-1 citing doc 06 reputation cost).

Consumer rules (cited, not invented):
- Deeds feed sect meters with weights (doc 20: weights at GDD tuning,
  open; this doc carries no weight numbers).
- The World Ledger remembers unresolved threads; abandoned chains build
  a reputation that gates the trustworthy-patron tier and unlocks the
  desperate-patron pool (doc 20 Expiry section). Mechanically: an
  UnresolvedConsequences worldflag family row per abandoned chain.
- Patron death mid-quest resolves as betrayal, never a stuck state
  (doc 20); the frame writer emits a Betrayal deed + consequence tag.

### 1.3 Faction and sect meters (doc 12, locked values cited)

Doc 53's UWHFactionSubsystem carries gate STATE; this doc owns the
meter schema those reads consume.

```cpp
USTRUCT(BlueprintType)
struct FWHCourtMeter {
    UPROPERTY(SaveGame) int32 AxisValue;          // -100..100 (doc 12)
    UPROPERTY(SaveGame) int32 DenialCountLight;   // Gambit memory, 0..3
    UPROPERTY(SaveGame) int32 DenialCountDark;    // Gambit memory, 0..3
    UPROPERTY(SaveGame) bool bHostilityOpenLight; // post-third-denial state
    UPROPERTY(SaveGame) bool bHostilityOpenDark;
};

USTRUCT(BlueprintType)
struct FWHParishSectMeter {
    UPROPERTY(SaveGame) FName ParishId;
    UPROPERTY(SaveGame) int32 SectValue;      // -100 Militant .. +100 Mercy? doc 20 sign convention at tuning
    UPROPERTY(SaveGame) bool bFlipped;        // crossed +/-50
};
```

Locked values carried by citation (doc 12 RULING PASS 2026-09-14):
deep-good/deep-evil alignment thresholds at +80/-80 points; courts'
favor tiers at +50/-50; neutral band between. Numbers are the doc's
PROPOSED working values pending GDD tuning, cited here as doc 12's
values, not re-tuned.

Locked mechanics this schema must serialize (doc 20 Parish-Flip):
- Flip at crossing +/-50; preacher NPC swap, quest pool swap, dialogue
  tone change follow the meter (doc 20), all reads off SectValue.
- HYSTERESIS: once flipped, crossing back past +/-25 flips again
  (buffer band); the schema stores bFlipped plus last-crossing band so
  the buffer is data, not recomputation.
- RIPPLE: three or more parishes in a region tipping the same way
  converts the region's bishop (doc 20); computed from the parish
  table at read time, no extra state.
- Sect meter is independent of the moral axis (doc 20 locked).
- Debt tension: hidden until the discovery arc, never a visible meter
  (doc 20 Debt Visibility, doc 19); the schema stores the int, the
  UI/HUD spec (doc 58) owns its never-showing it.

### 1.4 Territory keys

Territory identity for hold states, seats, and spawn-context reads:

| Key family | Grammar | Example | Source |
|---|---|---|---|
| Hold | `Hold_<Id>` | Hold_DarkwoodEaves | doc 03 holds, doc 13 conquest |
| City seat | `Seat_City_<n>` | Seat_City_1 (New Capital, mercenaries) | doc 44 Part 4 seats 1-4 |
| Hidden seat | `Seat_Hidden_<n>` | Seat_Hidden_5 (Hidden Court den) | doc 44 Part 4 seats 5-7 |
| Underworld capital | `Seat_Underworld` | single key | doc 44 Part 4 (eighth SEAT, not a faction) |
| Parish | `Parish_<HoldId>_<n>` | Parish_NewCapital_2 | doc 20 parish flip scope |
| Altar site | `Altar_Sun/Veil/Deep` | Altar_Deep | doc 44 Part 8, doc 19 |

Seat assignments (city 1-4 = New Capital mercenaries, Veil Spire
smugglers, Underground Dwarf City thieves, Orc City bandit camps;
hidden 5-7 = Hidden Court den, Wardens vault-seat, brokers' cavern
market; Pale Queen's seat = underworld capital) are doc 44 Part 4
locked/assigned content, cited as keys only (doc 44 Part 4; brokers
fold into the Pale Queen per audit ruling 4, doc 45 N-branch).

### 1.5 Per-cell source citations

Every ledger DataTable row carries: SourceDoc (FName), SourceSection
(FName, e.g. "44-P2", "12-RULING-PASS"), and LockState (enum:
LOCKED_RULING, PROPOSED_VALUE, OPEN_QUESTION). Testerbot check T57-02
(section 5) greps for missing citations. No cell exists whose owning
GDD/ruling is uncited.
---

## SECTION 2: KNOWLEDGE-LEDGER REVEAL GATES

Doc 44 Part 2's table is THE source of truth for reveal design (its own
words: doc 36's reveal arcs and the doc 20 debt discovery arc must not
contradict it). This section makes that table a RUNTIME DATA STRUCTURE
and the gate other modules call. Docs 54 and 56 cite this doc as the
gate owner (doc 52 spec-set rows 54/56); the enforcement contract here
is what they consume.

No new reveals are authored. The table's content mirrors doc 44 Part 2
exactly; every row below cites its cells.

### 2.1 The knowledge DataTable

Table: DT_WHKnowledgeLedger, asset path /Game/WH/Data/DT_WHKnowledgeLedger
(naming per doc 53 section 1.4). One row PER FACT PER CHARACTER (the
long format of doc 44 Part 2's matrix; the matrix's 8 character columns
x 11 fact rows flatten to 80 runtime rows, PROPOSED flattening
mechanics, the CELL CONTENTS are doc 44's, not invented).

```cpp
USTRUCT(BlueprintType)
struct FWHKnowledgeCellRow : public FTableRowBase {
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FName CharacterId;
    // Witch, LightKing, DarkKing, DarkQueen, PaleQueen,
    // HiddenCourt, Wardens (doc 44 Part 2 columns; player is not a
    // matrix column: the player's own knowledge is player-state,
    // section 4)
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FName FactId;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) EWHKnowledgeState State;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FName StateQualifier;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FName GateEventId;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FName SourceDoc;   // e.g. 44-P2
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FName LockTag;     // e.g. locked-2026-09-14
};
```

EWHKnowledgeState enumerators (mirror the doc 44 Part 2 cell values,
no others): KNOWS, NO, SUSPECTS, LEARNS_MIDRITUAL (the locked
conditional), UNAVAILABLE (the one dash cell), UNCERTAIN (the witch's
"no (uncertain)" Pale-Queen-lives cell).

FactIds (FName forms of doc 44 Part 2's fact column, one per row of
the table, cited cell-by-cell):

| FactId | Doc 44 Part 2 row | Cells as doc 44 states them |
|---|---|---|
| Fact_WitchCausedFall | "The witch caused the Fall" | Witch KNOWS; all six others no |
| Fact_CreditorIsLightQueen | "The creditor is the light queen" | Witch KNOWS; DarkQueen no (learns mid-ritual, locked); rest no |
| Fact_DebtRealEscalating | "The debt is real and escalating" | Witch KNOWS; DarkKing KNOWS; DarkQueen KNOWS; PaleQueen SUSPECTS (the war's economics); Wardens SUSPECTS (contradictory versions); LightKing/HiddenCourt no |
| Fact_UndersovranFiction | "The Undersovran is a fiction" | Witch KNOWS; all others no |
| Fact_KingCompelled | "The king is compelled" | Witch KNOWS; LightKing no (victim); rest no |
| Fact_AltarsSiphoned | "The altars are siphoned" | Witch KNOWS; all others no |
| Fact_HarvestFeedsHer | "The Mercy/Militant harvest feeds her" | Witch KNOWS; all others no |
| Fact_SignerIsMask | "The Signer is a mask" | Witch KNOWS; PaleQueen KNOWS (locked 2026-09-14: she was at the signing, she smelled the plot); HiddenCourt no (the leash is real to them); rest no |
| Fact_WitchSurvivedAsLightQueen | "The witch survived as the light queen" | Witch KNOWS; all others no |
| Fact_PaleQueenUnites | "The Pale Queen lives in the underworld and unites the rings" | Witch no (uncertain); HiddenCourt SUSPECTS (an unifier moves pieces); PaleQueen cell is "-" (self-fact); rest no |
| Fact_DeepAltarExists | "The Deep Altar exists and what it is" | Witch KNOWS (she drains the other two; the Deep one she forgot, doc 19); PaleQueen SUSPECTS (the underworld sits on it); Wardens SUSPECTS (in their archives); rest no |

CharacterIds map doc 44 Part 2's columns 1:1: Char_Witch,
Char_LightKing, Char_DarkKing, Char_DarkQueen, Char_PaleQueen,
Char_HiddenCourt, Char_Wardens (names PROPOSED as FNames; the
characters and their states are doc 44's).

StateQualifier carries the doc 44 cell parentheticals as data
("learns-midritual-locked", "the-wars-economics",
"contradictory-versions", "at-the-signing", "leash-real",
"uncertain", "she-drains-other-two", "underworld-sits-on-it",
"archives", "unifier-moves-pieces", "victim"). These strings mirror
doc 44 Part 2's cell text; they authorize nothing by themselves, the
gate predicate (2.3) reads them.

### 2.2 Gate predicates (doc 37 G19 audience predicate assignment)

Doc 37-A resolution (line-level): audience checks and follower
liability apply only to GUARDED facts, explicitly exempting PUBLIC
facts; doc 37-C assigns G19 audience detection and dig risk as the
stealth/lockpick-side owner of the audience predicate. Doc 37-popup
ruling (2026-09-13): guarded speech runs an audience predicate (no
ungated captions, no auto-populated quest text); ambient chatter and
tavern rumor carry no audience check.

This doc adapts that predicate assignment to knowledge cells:

```cpp
USTRUCT(BlueprintType)
struct FWHRevealGatePredicate {
    UPROPERTY(EditAnywhere) FName GateId;
    UPROPERTY(EditAnywhere) FName FactId;         // 2.1 table key
    UPROPERTY(EditAnywhere) EWHGateKind GateKind; // Audience / Standing / Questflag / Saveflag
    UPROPERTY(EditAnywhere) int32 AudienceTier;   // G19 guarded-fact tier (0 = ambient, no check)
    UPROPERTY(EditAnywhere) FName RequiredDeed;   // deed log key or NONE
    UPROPERTY(EditAnywhere) FName RequiredQuestFlag;
    UPROPERTY(EditAnywhere) FName OwningDoc;      // cite: the ruling/doc that owns the gate
};
```

Predicate bindings (each cites its owning doc):

| GateId | Predicate | Owning doc |
|---|---|---|
| Gate_AudienceGuarded | G19 audience check applies (suspected-presence + earshot) | 37-A resolution, 37-C G19 assignment, 37-popup ruling 33 |
| Gate_AmbientFact | no audience check, no risk | 37-A (public-fact exemption) |
| Gate_StandingDoor1 | WOLF TRUST ladder read (PROPOSED bands doc 46 S2) | 46 Section 2 door 1 |
| Gate_LeashTruth | player-side leash-truth flag set (doc 46 beat D1-4) | 46 Section 2 door 1, doc 45 N3 |
| Gate_SixRefusals | Gambit denial counters == 3+3 | 12 Allegiance Gambit (locked) |
| Gate_Midritual | fires only inside beat DA-6's window | 36 ruling 1 (locked), 46 beat DA-6 |
| Gate_GiftBeat | player CHOSE to tell (doc 44 Part 5 beat 6) | 44 Part 5 beat 6, 46 beat DA-7 |

### 2.3 The enforcement contract (what other modules call)

The gate API other modules call (doc 56 AI read hooks and doc 54's
dialogue/barks read through this; docs 54/56 cite this doc as gate
owner per doc 52 spec table):

```cpp
UENUM(BlueprintType)
enum class EWHGrantCheck : uint8 { Granted, DeniedByGate, DeniedByLedger };

UINTERFACE(MinimalAPI)
class UWHRevealGateInterface : public UInterface {
    GENERATED_BODY()
};

class IWHPredicateBearer {
    GENERATED_BODY()
public:
    // Does this speaker reveal this fact to this audience right now?
    virtual EWHGrantCheck EvaluateGrant(FName SpeakerId, FName FactId,
        const FWHAudienceContext& Audience) const = 0;
};
```

UWHWorldLedgerSubsystem (doc 53 stub, extended by this doc's contract,
not its class body):

```cpp
// OWNED BY DOC 57 SCHEMA (this doc). Doc 53 owns the class shell.
EWHGrantCheck EvaluateReveal(FName SpeakerId, FName FactId,
    const FWHAudienceContext& Audience) const;

// Mutations. ONLY these three entry points exist; a direct
// SetCell on a Knowledgecell family cell from outside the gate
// module is a fatal-logged rejected write (see 2.4).
EWHGrantCheck TryMutateKnowledgeCell(FName CharacterId, FName FactId,
    EWHKnowledgeState NewState, FName GateEventId, bool bIsPlayerDrivenGift);
FWhOnLedgerCellChanged& OnKnowledgeCellMutated();  // doc 53 delegate reused
```

Callers (cited): doc 56's AI and encounter systems READ cells through
FindCell/EvaluateReveal (doc 52 row 56 "World Ledger read hooks"); doc
54's dialogue layer calls EvaluateReveal per line before any guarded
line is eligible (doc 37-popup audience predicate; doc 37-A line-level
resolution); doc 58 HUD reads nothing from knowledge cells (debt never
a visible meter, doc 20/19).

### 2.4 Enforcement by data, not by convention

The point of this doc (brief constraint 4): a forbidden grant must be
IMPOSSIBLE by data shape.

- EWHGrantCheck returns DeniedByLedger whenever the would-be listener's
  row for FactId is in a state the mutation would contradict (doc 44
  Part 2 cell), and DeniedByGate when an owning predicate fails.
- There is no API that writes a knowledge cell without passing through
  TryMutateKnowledgeCell; the subsystem's SetCell (doc 53 stub) is
  route-guarded: family Knowledgecell writes from any caller other than
  the gate path are fatal-logged and rejected. This is the mechanism
  that makes "a beat lets a character learn a fact their cell forbids"
  unrepresentable at the data layer, not merely prohibited by style.
- No gameplay beat may flip a cell whose GateEventId predicate is not
  registered in the gate table; a mutation attempt against an
  unregistered gate is a fatal log (fail-fast per doc 53 registry
  invariant).
- Spine-only writes: procedural/proc-gen code paths may call only the
  Tissue-payload families (1.1 rule, doc 20 two-tier lock). A proc-gen
  write attempt against Knowledgecell or Sentencestate is rejected.

### 2.5 Reveal beat hooks and the mid-ritual rule

Where a quest event checks and mutates a cell (all beat ids cited from
doc 46, not restated):

| Hook (FName) | Fires at doc 46 beat | Cell mutated | Cite |
|---|---|---|---|
| Hook_TwoStageReveal | D1-4 | PLAYER knowledge only (mask's falsity); Court cell stays no | 46 D1-4, doc 45 N3, doc 44 Part 4 door 1 |
| Hook_CourtExpose | D1-5 EXPOSE route | Court's SignerIsMask cell -> learns-mask-is-false; witch's hunted-state flag | 46 D1-5, doc 44 open 3 resolution |
| Hook_RekeyQuiet | D1-5 RE-KEY route | none (Court cell stays no) | 46 D1-5 |
| Hook_WardenFragmentWalked | D2-5 / C4 | player cells only (Warden fragment) | 46 D2-5, C4 |
| Hook_MidRitualCreditorFace | DA-6 | DarkQueen CreditorIsLightQueen: NO -> LEARNS_MIDRITUAL; no other cell changes, no other character gains it | 46 DA-6, doc 36 ruling 1 (LOCKED), doc 48 Section 3 |
| Hook_GiftBeat | DA-7 aftermath | PaleQueen learns ONLY what the player tells her | 46 DA-7, doc 44 Part 5 beat 6 |

THE MID-RITUAL-ONLY CREDITOR-FACE RULE (doc 36 ruling 1, LOCKED,
cited; restated as data constraint): the dark queen's
Fact_CreditorIsLightQueen cell may leave NO only through
Hook_MidRitualCreditorFace, whose GateEventId predicate
(Gate_Midritual) is bound to the beat DA-6 window (doc 48 Section 3:
mid-ritual only, neutral ending only; the player sees the face with
her; no faction, companion, or broker inherits it). The gate table
carries no other binding for this fact, so no other code path can
legally grant it. Doc 48 Section 3 authors the choice's consequences;
this doc owns only the cell mutation.

The Pale Queen's Fact_SignerIsMask KNOWS cell (locked 2026-09-14) is
seed data, not a mutation target: she learns nothing new from the
two-stage reveal (doc 46 beat D1-4 LEDGER line), so her row's
GateEventId is NONE and no hook binds it.

### 2.6 What the gates do NOT do

- No new reveals (brief): 2.1's table mirrors doc 44 Part 2 exactly;
  any mismatch is a Testerbot failure (section 5), not a design space.
- No dialogue content authored here; doc 58 and the GDDs own lines.
- No AI behavior authored here; doc 56 consumes reads.

---

## SECTION 3: QUEST FRAME TEMPLATES

Doc 20 owns the quest frame grammar (patron + need + site + resolution
axes + consequence tags + personal axes, locked 2026-09-12). Doc 46
owns the authored beats: spine chains A-H, the six doors, the Deep
Altar approach, and four new tissue frames. This section authors the
DATA-DRIVEN TEMPLATE STRUCT: how a frame or chain becomes rows in
registry DataTables consumed by the quest spawner (doc 20: quest logic
of its own does not exist; the spawner queries the World Ledger).

NO new beats. Doc 46's beats are cited by id, not restated. Frame
struct fields mirror doc 20's grammar fields 1:1.

### 3.1 Frame struct

```cpp
USTRUCT(BlueprintType)
struct FWHQuestFrameDef : public FTableRowBase {
    UPROPERTY(EditAnywhere) FName FrameId;            // e.g. Frame_PurgeContract
    UPROPERTY(EditAnywhere) EWHFrameTier Tier;        // Spine / Tissue (doc 20 two-tier lock)
    UPROPERTY(EditAnywhere) FName PatronPool;         // doc 14 pools / spine fixed-NPC table
    UPROPERTY(EditAnywhere) FName NeedTag;
    UPROPERTY(EditAnywhere) TArray<FName> SitePool;   // doc 20 persistent dungeon pool
    UPROPERTY(EditAnywhere) TArray<FName> ResolutionAxes; // kill/cure/pay/expose/enslave (doc 20)
    UPROPERTY(EditAnywhere) FWHPersonalAxes PersonalAxes; // secondary character + fate-by-resolution (doc 20 locked)
    UPROPERTY(EditAnywhere) TArray<FName> ConsequenceTags; // writes back to ledger (doc 20)
    UPROPERTY(EditAnywhere) TArray<FWHBeatHook> BeatHooks; // 3.2
    UPROPERTY(EditAnywhere) FName SourceDoc;          // 46-S1..S4 / 20
    UPROPERTY(EditAnywhere) FName LockTag;
};
```

EWHFrameTier mirrors doc 20's locked two-tier architecture. Tier rule
made mechanical (doc 20: procedural systems may only ever write into
the TISSUE layer): the spawner refuses to instantiate Spine-tier
frames procedurally; spine instances exist only as authored data rows.

### 3.2 Beat list and ledger-check hooks per beat

```cpp
USTRUCT(BlueprintType)
struct FWHBeatHook {
    UPROPERTY(EditAnywhere) FName BeatId;      // cited doc 46 beat id, e.g. A1, D1-4, DA-6, G2
    UPROPERTY(EditAnywhere) TArray<FName> LedgerChecks;   // EvaluateReveal / FindCell reads
    UPROPERTY(EditAnywhere) TArray<FName> LedgerMutations; // permitted cell writes (gate-routed)
    UPROPERTY(EditAnywhere) FName CiteDoc;     // owning doc + section
};
```

Hooks are data: a beat may check a cell (FindCell read) or mutate
through the section 2 gate path only. Spine chains map by citation,
one row per chain, no beats restated:

| Chain (FrameId) | Beats cited | Ledger hooks | Cite |
|---|---|---|---|
| ChainA_Allegiance_Light / _Dark | A1-A5 (mirrored 5x2) | Gambit denial counters; standing tiers | 46 S1 chain A, 12 Gambit |
| ChainB_Gambit | B1-B6 (six refusals) | DenialCount counters; sixth refusal opens underworld flag + Six-Times-Refuser title (doc 16) | 46 chain B, 12 |
| ChainC_ThirdAltar | C1-C5 (C2 defers to six doors, C5 to delve) | Fact reads (C3 LEDGER: no NPC states transfer or purpose); fragment walk (C4) | 46 S1 chain C, 44 P4/P8 |
| ChainD_DebtDiscovery | D1-D5 + Foreclosure F-D1..F-D3 | debt tension bands (hidden, doc 20); F-D2 throne-does-not-know read | 46 chain D, 44 P5B |
| ChainE_WolfTrial | E1-E6 + post-transformation block | wolf trust gating (doc 20 gear-gate exception) | 46 chain E, 20 Wolf Trial |
| ChainF_Signer | F1, F2 (+ RETIRED Unsigning status note, doc 45 N9) | Warden standing; grave beat deed | 46 chain F, 45 N9 |
| ChainG_DemonInvasion | G1-G4 | world event flags; G4 LEDGER: no character learns creditor's face; dark queen reads default as CONFIRMED (doc 45 D9) | 46 chain G, 44 P5C |
| ChainH_SanctifiedDoubt | H1-H5 + Heresy H-A1..A4 + delve entry hook | light-line rule: Sun-altar evidence PHENOMENOLOGICAL ONLY (audit L12) | 46 chain H, 45 L12 |
| Doors 1-6 | D1-1..D6-3 (per doc 46 S2) | standing meters (WOLF TRUST, ARCHIVE STANDING, PAYMASTER REGARD, ROAD SILENCE, FENCE REGARD, CAMP TRUSS; all PROPOSED bands doc 46 S2) | 46 S2, 44 P4 |
| Destination congregation | DA-1..DA-7 | rival-engine flag; sentence-state write (doc 48) | 46 S3, 44 P8, 48 |

Sentence-sequence hooks (doc 48's four sentences) as save-schema stubs:

| Stub (FName) | Doc 48 section | Payload this doc owns | Cite |
|---|---|---|---|
| Sent_Execution | 2.1 | Sentencestate cell: altars disposition stub, spawn-table shift flag | 48 S2.1, 36 ruling 2/5 |
| Sent_Exile | 2.2 | Sentencestate cell: exile world-seed stub | 48 S2.2 |
| Sent_Wardenship | 2.3 | Sentencestate cell: Warden-held mortal NPC stub + retired-Unsigning image tag | 48 S2.3, 45 N9 |
| Sent_Freedom | 2.4 | Sentencestate cell: population-seed stub, no faction flag | 48 S2.4 |

Stub rule: doc 53 stubs the hooks' engine side (save payload shape,
section 4.1); doc 48 owns the tables' content; this doc owns only the
stub ids and the cell family they write into. Consequence-table VALUES
are doc 48's; here they are FName references, never numbers.

### 3.3 The four tissue frames (doc 46 Section 4, mirrored as templates)

Doc 46 Section 4 authors exactly four new tissue frames (bounded,
small). This doc registers them as template rows; their patron/need/
site/axes/personal-axes/consequence-tags are doc 46 Section 4's
verbatim field set, cited per row:

| FrameId (DT_WHQuestFrames row) | Doc 46 frame | Ledger consequence tags (as doc 46 writes them) |
|---|---|---|
| Frame_PurgeContract | purge-contract (the witch's disguised underworld purges) | deed log records purge; underworld standing drops silently; Militant parish meters rise; on neutral read: her strategy executed (doc 46 cites doc 20 deed log) |
| Frame_HeresyShelter | heresy-shelter (Mercy parish protection work) | Mercy standing up, Militant grudge, parish meters, deed log; feeds the Mercy Mirror pivot (doc 45 L8) |
| Frame_BrokerIntel | broker-intel (the underworld-economics shadow route) | dark fragment progress (player-knowledge), underworld standing, Pale Queen economics read; LEDGER: no broker ever learns the creditor's face (doc 46 cites doc 44 P2) |
| Frame_WolfRoadLogistics | wolf-road logistics (Hidden Court aligned supply line) | wolf trust, underworld standing, final-battle logistics tier (feeds beat DA-2), deed log |

Personal-axes characters in these frames (the den's inhabitants, the
accused, the collector, the passenger) are doc 46 Section 4's authored
texture, carried as data fields; this doc invents no NPC names.

### 3.4 Frame runtime rules (cited locks)

- Threshold triggers, not NPC triggers: frame unlocks key off
  standing/axis/title thresholds so they surface from any compatible
  surface (doc 20 locked).
- Fails-forward: expiry resolves into consequences, never dead ends
  (doc 20; the schema's Questframe cell carries state tags for
  betrayal/inheritance/harder-version re-appearance, doc 20's list).
- Spine immunity: no procedural event can kill, displace, or de-spawn
  a spine NPC (doc 20 locked); mechanically, spine NPC ids live in a
  protected FName list the spawner and the conquest meta both read
  (doc 13 consequences route through the same list).
- The debt has its own fuse: debt tension escalates from war state
  and elapsed time, never from player quest completion (doc 20
  locked); the Debttension family tick reads war momentum + day
  stamp, nothing else.


---

## SECTION 4: SAVE SCHEMA

Doc 53 owns the save subsystem class (UWHSaveSubsystem, section 2.2
stub: WriteSlot/ReadSlot/ListSlots/SetRespawnAnchor) and the
serialization contract (section 4.1: save-serializable structs only,
flat cell map export). This doc owns WHAT goes in the blob.

### 4.1 What serializes (doc 09 locked save rules honored)

Doc 09's resolved save/respawn rules the schema must carry (locked
2026-09-11, cited): CAMPS SAVE (autosave on completing camp);
TAVERNS ANCHOR RESPAWN (renting a room sets the point); UNLOCKED WARP
CAMP IS THE DEFAULT FORWARD RESPAWN (taverns still usable); camping
does not move respawn; camp gear destructible in night ambushes (the
tent slept in is safe); night skips only on sleeping.

| Payload block | Cell families serialized | Cite |
|---|---|---|
| Ledger cells | all families in 1.1 (Warmomentum, Debttension, Axisposition, Courtstanding, Sectmeter, Standingmeter, Deedlog, Worldflag, Knowledgecell, Questframe, Sentencestate) | this doc S1, doc 53 4.1 contract |
| Player state | axis position, denial counters, allegiance state, retinue roster refs, titles (doc 16), skill/kit states by reference (docs 15-18 own those schemas; this doc stores ids + version tags only) | 12, 16, 20 |
| World flags | Worldflag family (hold states, unresolved-consequence threads, underworld-opened, chain event flags) | 20, 13 |
| Faction meters | Courtstanding per side, Sectmeter per parish, Standingmeter per door (PROPOSED bands doc 46 S2) | 12, 20, 46 S2 |
| Sentence-sequence stubs | Sentencestate family + kill-or-break asset-or-enemy live state (doc 48 S3: live by beat order between the dark king's fall and the light-capital stand) | 48 S3/S5, 44 P5C |
| Respawn anchor | FWHRespawnAnchor (doc 53 stub): AnchorType (tavern/warp-camp), SiteId | 09 resolved 1-2, doc 53 S2.2 |

NOT serialized into this blob (cited): dungeon interiors generated
once then saved as persistent (doc 03/08 resolution 2, doc 53 owns the
dungeon save path); conquest meta (doc 13 state rides
Warmomentum/Worldflag families); NG+ world seeds (doc 12 NG+ locks:
aligned endings lock the side, Third Path NG+ keeps the camp while
the world resets; the seed block is a doc 53 save-subsystem concern,
this doc stores only the flag set it passes).

### 4.2 Slot grammar and version field

```cpp
USTRUCT(BlueprintType)
struct FWHSaveLedgerBlob_V1 {
    UPROPERTY(SaveGame) int32 SchemaVersion;      // starts at 1 (PROPOSED)
    UPROPERTY(SaveGame) TArray<FWHLedgerCell> Cells;   // doc 53 struct
    UPROPERTY(SaveGame) TArray<FWHDeedLogEntry> Deeds;
    UPROPERTY(SaveGame) TArray<FWHCourtMeter> CourtMeters;
    UPROPERTY(SaveGame) TArray<FWHParishSectMeter> ParishMeters;
    UPROPERTY(SaveGame) TArray<FWHDoorStandingRow> DoorStandings;
    UPROPERTY(SaveGame) FWHRespawnAnchor Respawn;      // doc 53 struct
    UPROPERTY(SaveGame) TArray<FWHSentenceStub> Sentences;
    UPROPERTY(SaveGame) FGuid BuildTag;
};
```

- SlotName grammar (PROPOSED): `WH_<SlotLabel>_<NN>` (auto slots
  `WH_Auto_NN`), matching doc 53's WriteSlot(FString SlotName) key.
  Slot count cap: doc 53's wh.Core.SaveSlots.Max (default 20,
  PROPOSED there, cited not re-numbered).
- Version field: int32 SchemaVersion + FGuid BuildTag per blob.
  Mismatch = migration path.
- Migration note (PROPOSED): version N-1 -> N runs a registered
  FWHSaveMigrationStep chain (ordered, per-family; unknown family =
  drop-with-log for tissue families, refuse-to-load for spine
  families: Knowledgecell/Sentencestate rows never silently dropped).
  Doc 53 owns the save class; this doc owns the migration policy
  declaration. PROPOSED pending doc 53 section 4 review.
- Sentence-state secret rule carried into the schema: the sentence
  fork's secret stays player-side; NG+ world seeds read the stub,
  never the secret (doc 48 S2 NG+ rows, locked asymmetry doc 36).

---

## SECTION 5: TEST PLAN (Testerbot)

No gameplay beats validated here; every check is schema/gate/contract
shaped. Grep-able checks, named exactly:

| Check | What Testerbot validates | Method (grep/parse) |
|---|---|---|
| T57-01 | Every knowledge row in DT_WHKnowledgeLedger matches a doc 44 Part 2 cell (state + qualifier) | parse DT_WHKnowledgeLedger export CSV; diff against the 80 expected (char,fact,state) triples; zero diff required |
| T57-01a | Per-fact spot-checks, named: Fact_CreditorIsLightQueen row set == Witch KNOWS + DarkQueen "no (learns mid-ritual, locked)" + six no; Fact_SignerIsMask row set == Witch KNOWS + PaleQueen KNOWS (locked 2026-09-14) + HiddenCourt "no (leash real)" + four no; Fact_KingCompelled == Witch KNOWS + LightKing "no (victim)" + five no | exact-triple assertions per named fact |
| T57-02 | Every ledger DataTable row carries SourceDoc + SourceSection + LockState; none empty | grep export CSV for empty citation columns; count == 0 |
| T57-03 | No gate predicate lacks OwningDoc cite; every doc-36-ruling-derived element carries LockTag | grep GateId rows lacking OwningDoc |
| T57-04 | Save round-trip: ExportCells -> ImportCells -> ExportCells is byte-identical for all families | engine-side diff of two exported blobs |
| T57-05 | No proc-gen write path reaches Knowledgecell or Sentencestate (2.4 route guard fires) | attempt rejected writes in test harness; assert fatal log + unchanged cells |
| T57-06 | Mid-ritual gate: TryMutateKnowledgeCell(DarkQueen, Fact_CreditorIsLightQueen) returns DeniedByGate unless Gate_Midritual window active; no other speaker/audience pair ever Granted | predicate fuzz run |
| T57-07 | Doc 46 tissue frames instantiate only as Tissue tier; spine chain rows refuse procedural instantiation | spawner harness asserts rejection |
| T57-08 | Frame beat hooks cite existing doc 46 beat ids; no invented beat ids | parse BeatHooks; diff against doc 46 id list |
| T57-09 | No em dashes anywhere in this doc; line count under 700 | grep for the character; wc -l |
| T57-10 | Every PROPOSED-marked value in this doc is either schema mechanics or carries a doc-cite; no new gameplay numbers | grep PROPOSED lines lacking a "doc " cite |

Testerbot scope note: consistency validation runs against docs 44 P2,
46, 48, 12, 20, 09 (doc 52 gate rule 1); this doc's data rows are the
assertion targets, not the GDD text.

---

## OPEN QUESTIONS (doc 08 format, numbered, with assignments)

- CD-1. Knowledge matrix flattening mechanics (80 runtime rows vs
  in-place matrix reads; row count is a PROPOSED flattening artifact,
  cell contents are doc 44's). Assignment: Nicko review of this spec
  (schema shape), then doc 53 DataTable registry list update.
- CD-2. FWHSaveLedgerBlob version/migration policy (4.2 PROPOSED:
  refuse-to-load for spine families vs drop-with-log for tissue
  families). Assignment: doc 53 section 4 owner (save/load pass) with
  Nicko sign-off.
- CD-3. Parish sect-meter sign convention (doc 20 states
  Militant<->Mercy with +/-50 flip; the doc 12 axis uses
  light-positive; one shared signed-int convention must be locked for
  UI reads). Assignment: doc 58 HUD spec + GDD tuning pass.
- CD-4. Gate predicate AudienceTier values (G19 guarded-fact tiers
  referenced by id only; the tier table's numbers are doc 37-A/37-C's
  to fix and this doc cites rather than copies). Assignment: G19
  stealth/dialogue GDD pass owner (doc 08 tracker item 32/33 thread).
- CD-5. FWHDeedLogEntry weight plumbing: deed categories feed sect
  meters with weights explicitly deferred to GDD tuning (doc 20 open
  question 7). Assignment: GDD tuning pass (docs 12/20 thresholds
  with doc 07's XP block).
- CD-6. Door standing band values (doc 46 S2's PROPOSED 25/60/90
  bands are consumed by Standingmeter gates here, owned there).
  Assignment: already doc 46 OQ-1; this doc adds no new numbers.

## SPEC CONFLICTS FOUND

None blocking. Two citations-of-record noted, both following existing
supersessions rather than new rulings:
1. The brief's "doc 37 G19 audience predicate assignment" resolves to
   doc 37-A's line-level resolution (audience checks apply only to
   GUARDED facts) plus doc 37-C's G19 assignment plus doc 37-popup
   ruling 33; the three docs' division of labor is cited in 2.2 and
   no conflict with doc 44 P2 arises (audience gating governs
   delivery of guarded speech, ledger cells govern what may be
   known).
2. File-name variants vs the brief's citation list: doc 20 lives as
   20-quests-factions-gdd-part1.md and doc 19 as
   19-fall-of-the-veil-throne.md, doc 09 as 09-expedition-camping.md;
   cited content verified in those files. No content conflict.

## COMPLETION REPORT

- Sections delivered: 1 (World Ledger Schema: cell grammar, deed log,
  faction/sect meters, territory keys, per-cell citations), 2
  (Knowledge-Ledger Reveal Gates: DT_WHKnowledgeLedger per-fact rows,
  gate predicates, enforcement contract, mid-ritual rule), 3 (Quest
  Frame Templates: FWHQuestFrameDef, beat hooks for chains A-H, doors
  1-6, DA-1..7, four sentence stubs, four tissue frames), 4 (Save
  Schema: serialized families per doc 09 locked rules, slot grammar,
  version field, migration note PROPOSED), 5 (Test Plan: T57-01..
  T57-10 named checks).
- Struct/DataTable counts: 6 C++ structs declared at header-signature
  level (FWHDeedLogEntry, FWHCourtMeter, FWHParishSectMeter,
  FWHKnowledgeCellRow, FWHRevealGatePredicate, FWHQuestFrameDef) plus
  2 helper structs (FWHBeatHook, FWHSaveLedgerBlob_V1) plus 1
  interface (IWHPredicateBearer, with UWHRevealGateInterface shell) =
  9 total. DataTables owned: DT_WHKnowledgeLedger, DT_WHQuestFrames,
  DT_WHRevealGates, plus row families inside the doc 53 registry
  (DT_WHLedgerCells per family). Enums declared: EWHLedgerCellFamily,
  EWHKnowledgeState, EWHGrantCheck, EWHFrameTier, EWHGateKind,
  EWHDeedCategory (6).
- Open questions: CD-1 through CD-6, each with an assignment (see
  section above). No locked ruling is contradicted anywhere in this
  doc; where a value was needed, the owning doc's value is cited or
  the slot is marked PROPOSED with an assignment.
- Spec conflicts: none blocking (two citation reconciliations
  recorded above). Ledger compliance is structural: knowledge cells
  are writable only through the section 2.3 gate path, so a beat
  cannot grant a fact a doc 44 Part 2 cell forbids; the mid-ritual
  creditor-face rule (doc 36 ruling 1) is enforced by the gate table
  carrying exactly one binding for that fact (2.5).
- File status: single new file
  docs/planning/57-ue5-data-ledger-architecture.md, untracked, no git
  commands run.
