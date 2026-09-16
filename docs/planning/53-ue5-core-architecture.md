# 53 - UE5.8 Core and Project Structure Architecture Spec

Drafted 2026-09-16, UE5.8 core architecture spec (doc 31 engine plan governs; GDDs 46-51 + planning corpus are the content source). PROPOSED for Nicko review. Subordinate to locked rulings; conflicts are open questions, not edits.

Scope: the CORE module only. Project structure, C++ module map, subsystems, DataTable registry, input mapping, save/load architecture, and the naming/folder conventions every other module spec inherits. This doc authors engine structure and contracts. Gameplay content lives in the GDDs; combat component internals are doc 54; ledger tables are doc 57; UI is doc 58; world streaming is doc 55.

## 1. PROJECT STRUCTURE

### 1.1 Repo: witch-hunter-ue

Locked (doc 31, doc 30 open item resolved): a separate repo named
`witch-hunter-ue`, distinct from this planning repo. Planning docs never
enter it. Repo root layout (PROPOSED, standard UE 5.8 project shape):

```
witch-hunter-ue/
  WHGame.uproject            descriptor: name WHGame, modules list below
  Config/                    DefaultEngine.ini, DefaultGame.ini,
                             DefaultInput.ini, DefaultScalability.ini,
                             DefaultRemoteControl.ini
  Source/WHGame/             primary game module (C++)
  Source/WHGame.Target.cs
  Source/WHGameEditor.Target.cs
  Content/                   mirrors /Game/; the /Game/WH tree below
  ue/                        IO-authored Python scripts (import_asset.py,
                             build_scene.py) per doc 30's loop
  manifests/                 scene manifests (JSON) per doc 30 Phase 3
  .gitattributes             LFS rules below
```

C++ module name: `WHGame` (PROPOSED, one primary module; a second
`WHGameEditor` editor-only module is added only when editor utilities
need it). Build configuration: engine references via the standard
`UnrealGame`/`UnrealEditor` targets; no engine source build assumed.

### 1.2 Plugin list (PROPOSED)

Enabled in WHGame.uproject, all PROPOSED pending M0 validation:

| Plugin | Purpose | Source |
|---|---|---|
| EnhancedInput | doc 32 input grammar | stock |
| PythonEditorScriptPlugin | doc 30 control plane | stock |
| RemoteControlAPI | doc 30 control plane, :30010 | stock |
| PythonScriptPlugin | doc 30 remote execution | stock |
| GameplayTasks | AI module base (doc 56 consumer) | stock |
| AISupport | doc 56 | stock |
| Paper2D | HUD sprite consumers, doc 58 | stock |
| UMG + HUD | doc 58 | stock |
| LevelSequence + TemplateSequence | camera register blends, doc 28 | stock |
| EnhancedSceneInterfaces | n/a, omitted | - |
| ModelingToolsEditorMode | blockout authoring, M2 | stock |
| first-party Unreal MCP | audited before FFZackFair92 adoption (doc 30, doc 52) | 5.8 stock |

Deferred: GAS plugins (Adoption gate at slice exit, doc 31). No
third-party plugins in the base list; the FFZackFair92 MCP server is a
VPS-side tool, not a project plugin (doc 30).

### 1.3 /Game/WH tree at file level

Locked folder list (doc 31), expanded to expected file level. Paths are
/Game/WH/...; C++ sources live under Source/WHGame/ with matching
subfolders.

- /Game/WH/Core/
  - Blueprints: BP_WHGameMode, BP_WHPlayerController,
    BP_WHPlayerCharacter (shells subclassing the C++ classes in
    section 2), BP_WHGameInstance.
  - Input: IMC_Exploration, IMC_Combat, IMC_Delve (mapping contexts,
    section 3), IA_* action assets per section 3 table.
  - Config mirrors: none; engine config lives in /Config.
- /Game/WH/Combat/ (doc 54's to fill; Core only reserves the folder and
  the DataTable registry paths)
  - /Game/WH/Data/DT_WHFrameData (uasset DataTable, FWHFrameDataRow
    rows, doc 54 schema).
  - /Game/WH/Data/DT_WHStaminaCosts, DT_WHPoiseValues,
    DT_WHDamageTable (doc 54 columns).
- /Game/WH/World/ (doc 55): WH_Arena_Darkwood level, lighting, fog,
  post-process volumes.
- /Game/WH/Characters/Player, .../Bandit, .../Wolf, .../Boss:
  skeletal meshes, physics assets, anim monitors, sockets. Subfolders
  per body: Meshes/, Animations/, Blueprints/.
- /Game/WH/Art/Materials/: M_WHPixelRegister master material and the
  MFunction_WHPixelRegister material function (doc 29 Phase 2, doc 58).
- /Game/WH/Art/PostProcess/: post-process volumes and blends (low-res
  render, point sample, ordered dither, grain; doc 31).
- /Game/WH/UI/ (doc 58): WBP_WH_HUD minimum set.
- /Game/WH/Data/: the DataTable registry (section 2.5). Tables:
  FrameData, StaminaCosts, PoiseValues, DamageTable named at doc 31;
  registry pattern in section 2.5.
- /Game/WH/Audio/: reserved (G16), empty acceptable for slice 1 (doc
  31).

### 1.4 Naming conventions (inherited by every module spec)

| Kind | Rule | Example |
|---|---|---|
| C++ class | `WH` prefix, PascalCase | AWHGameMode, AWHPlayerController, UWHCombatComponent (doc 31's UCombatComponent takes the WH prefix as UWHCombatComponent, PROPOSED spelling) |
| Struct | `FWH` prefix | FWHFrameDataRow |
| Subsystem | `UWH` + role + `Subsystem` | UWHWorldLedgerSubsystem |
| Enum | `EWH` prefix | EWHInputContext |
| Delegate | `FWH` + verb + `Signature`-less | FWHOnLedgerCellChanged |
| Asset | `WH` + descriptor, underscores | WH_Arena_Darkwood (doc 31) |
| Blueprint | `BP_WH` + name | BP_WHPlayerCharacter |
| Widget Blueprint | `WBP_WH` + name | WBP_WH_HUD |
| Material | `M_WH` + name; functions `MFunction_WH` + name | M_WHPixelRegister |
| DataTable | `DT_WH` + table name | DT_WHFrameData |
| Input Action | `IA_WH` + verb | IA_WHLightAttack |
| Input Mapping Context | `IMC_WH` + context | IMC_WHCombat |
| Curve/float assets | `Curve_WH` + name | Curve_WHHpRegen |

Rule: the doc 31 asset pattern (WH_Arena_Darkwood) is
`WH_<Descriptor>_<Biome|Role>` in PascalCase segments. No spaces in any
asset path. DataTable row struct names always FWH-prefixed even when the
table is owned by another module's doc.

The /WH/Data registry: every cross-module DataTable lives in
/Game/WH/Data/ and is registered in a C++ registry (section 2.5).
Module-local tables may live in the module's folder; anything read by
two or more modules belongs in /WH/Data.

### 1.5 Git/LFS wiring (serves doc 30's three planes)

- Repo: `witch-hunter-ue`, remote GitHub, default branches `main`
  (stable, tagged) and `dev` (integration). Branch model matches the
  planning repo's convention: work happens on dev; main moves only at
  verified gates. PROPOSED: feature branches `ue/<topic>` merge to dev.
- LFS-tracked (binary): *.glb, *.fbx, *.png, *.tga, *.exr, *.wav,
  *.mp3, *.ogg, *.uasset, *.umap, *.bnk (reserved, G16).
- Text (never LFS): *.ini, *.cpp, *.h, *.cs, *.py, *.json, *.md,
  *.uplugin, *.uproject, *.build.cs. Uassets are binary by format, so
  all data that must be diff-reviewed lives in DataTable-backed CSV or
  JSON sources under /WH/Data/Source/ (PROPOSED) imported to uassets by
  a repo script; the reviewable source is text, the uasset is LFS.
- renders/ artifacts go to the `renders/` branch, never dev or main
  (doc 30 verification plane).
- Commit cadence: IO commits asset batches to dev, pushes; the PC pulls
  (doc 30 data plane). No direct PC-to-VPS transfer of repo data.
- Doc 30 control-plane prerequisites the project must ship with:
  - Config/DefaultRemoteControl.ini: bAutoStartWebServer=True, port
    30010, bEnableRemotePythonExecution=True, function-call gates per
    doc 30 security notes (CustomAllowedRemoteFunctionCalls gated to
    PythonScriptLibrary, bAllowAnyRemoteFunctionCall=False, console
    gate OFF).
  - Python Editor Script Plugin + Remote Control API enabled by
    default in the uproject (Plugins list in 1.2).
  - ue/ scripts repo-side so `run_python_file` targets repo paths only
    (doc 30 loop steps 2-3).
  - Web server bound to the Tailscale interface (doc 30 checklist 5).

### 1.6 Prerequisites this doc does not solve

The doc 31 M0 blocker (Nicko provisions the UE 5.8 Windows machine,
Meshy/Tripo keys) gates all implementation. This doc only defines the
structure the machine must receive.

## 2. C++ MODULE MAP

All classes in the `WHGame` module under Source/WHGame/. Header-level
signatures only; implementations are authored at M2+ per doc 31
milestones. Every class carries the WH prefix (section 1.4).

### 2.1 Game framework

```cpp
// Game mode: rules shell only. Slice-1 rules: no respawn teleport
// beyond tavern anchor (doc 09 locked rules, section 4).
class AWHGameMode : public AGameModeBase {
    virtual void StartPlay() override;          // boot order, 2.4
protected:
    UPROPERTY(EditDefaultsOnly) TSubclassOf<APawn> PlayerPawnBP;  // BP_WHPlayerCharacter
    UPROPERTY(EditDefaultsOnly) FString DefaultSaveSlot;          // section 4.3
};

class AWHPlayerController : public APlayerController {
    // Owns input contexts (section 3), camera registers (doc 28/32
    // inherited, implementation detail of the controller).
    void PushInputContext(EWHInputContext Context);   // stack push
    void PopInputContext(EWHInputContext Context);    // stack pop
    EWHInputContext GetActiveContext() const;
    virtual void SetupInputComponent() override;      // binds IA_WH*
};

class AWHPlayerCharacter : public ACharacter {
    // Pawn shell ONLY. Owns the combat component by composition;
    // component internals (state machine, frame data reads, poise
    // math) are doc 54's. This doc fixes the ownership seam only.
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Combat")
    TObjectPtr<UWHCombatComponent> CombatComponent;   // composed, doc 54
    void BindCombatInput();                            // IA_* -> component
};
```

Composition contract (locked per doc 31 custom-stack ruling):
AWHPlayerCharacter owns UWHCombatComponent as a composed component. The
character forwards Enhanced Input events to the component through a
single C++ interface `UWHCombatInputBridge` (static, pure forwarding);
no combat logic reads input directly. Doc 54 authors the component's
action state machine, frame-data reads, and calculators. This doc does
not.

Camera: doc 28's three registers (EXPLORATION/COMBAT/AIM) and doc 32's
numbers are consumed by AWHPlayerController through a camera component
configuration; the register blend contract is data (curves + sequence
actors under /WH/Core/), not per-frame C++.

### 2.2 Subsystems

```cpp
// WorldLedgerSubsystem: the save-serializable world-state container.
// SCHEMA STUB ONLY: full ledger tables, deed log, faction meters, and
// the knowledge-ledger reveal gates are doc 57's runtime schema. Core
// authors the container interface and serialization contract.
UCLASS()
class UWHWorldLedgerSubsystem : public UWorldSubsystem {
public:
    // Cell access: cell = one serializable world-state slot keyed by
    // CellId (FName). Values are save-serializable structs only
    // (section 4.1 serialization rule).
    void SetCell(FName CellId, const FWHLedgerCell& Value);
    const FWHLedgerCell* FindCell(FName CellId) const;
    // Change broadcast (doc 56 AI read hooks, doc 57 consumers).
    FWHOnLedgerCellChanged OnCellChanged;
    // Serialization contract: the subsystem exports a flat cell map
    // into the save payload (section 4.1). Doc 57 owns the cell
    // families (hold states, faction meters, deed log, reveal gates).
    void ExportCells(FWHSaveLedgerBlob& OutBlob) const;
    void ImportCells(const FWHSaveLedgerBlob& Blob);
};

// FactionSubsystem: runtime read-side of alignment gates. Thresholds
// and the two-courts ladder are doc 12's (locked 2026-09-14 ruling:
// deep-good/deep-evil at +80/-80, favor tiers at +50/-50). The
// subsystem carries the gate STATE; how deeds move the axis is doc
// 57's ledger schema.
UCLASS()
class UWHFactionSubsystem : public UWorldSubsystem {
public:
    float GetAxisValue() const;                     // -100..100 scale (doc 12)
    EWHCourtStanding GetStanding(EWHCourtSide Side) const;
    bool IsGateOpen(EWHFactionGate Gate) const;     // progression gate reads
    FWHOnAxisChanged OnAxisChanged;                 // HUD + AI consumers
};

// SaveSubsystem: owns slot IO per section 4. Camps save (doc 09
// resolved 1), taverns anchor respawn, warp camp = forward respawn.
UCLASS()
class UWHSaveSubsystem : public UGameInstanceSubsystem {
public:
    bool WriteSlot(const FString& SlotName, const FWHSaveBlob& Blob);
    bool ReadSlot(const FString& SlotName, FWHSaveBlob& OutBlob) const;
    TArray<FString> ListSlots() const;
    void SetRespawnAnchor(const FWHRespawnAnchor& Anchor); // tavern/warp
    FWHRespawnAnchor GetRespawnAnchor() const;
};
```

### 2.3 Core data structures

```cpp
// Frame data row: STUB. Doc 54 owns the full column schema; this stub
// fixes the row key and the registry contract so combat tables can be
// imported before doc 54 lands.
USTRUCT(BlueprintType)
struct FWHFrameDataRow : public FTableRowBase {
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FName ActionId;   // e.g. LA1
    UPROPERTY(EditAnywhere, BlueprintReadOnly) int32 StartupFrames;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) int32 ActiveFrames;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) int32 RecoveryFrames;
    // doc 54 adds: stamina cost links, poise damage, i-frame windows,
    // cancel windows, clip references.
};

// Ledger cell value: one save-serializable state unit. Doc 57 owns
// the cell families (hold state, faction meter, deed log entry).
USTRUCT()
struct FWHLedgerCell {
    UPROPERTY(SaveGame) FName CellId;
    UPROPERTY(SaveGame) FName CellFamily;    // doc 57 taxonomy
    UPROPERTY(SaveGame) int32 IntValue;
    UPROPERTY(SaveGame) float FloatValue;
    UPROPERTY(SaveGame) FString StringValue;
    UPROPERTY(SaveGame) FGuid VersionTag;
};

// Save blob containers (payload shapes in section 4.1).
USTRUCT() struct FWHSaveLedgerBlob { UPROPERTY(SaveGame) TArray<FWHLedgerCell> Cells; };
USTRUCT() struct FWHSaveBlob { /* section 4.1 */ };
```

### 2.4 Tick groups and update order

Combat logic budget: 2 ms game thread (doc 31 G23, PROPOSED budget
carried). Update order locks the frame contract so doc 54 can assume
fresh inputs and doc 56 fresh ledger reads:

| Order | Group | What runs | Budget share |
|---|---|---|---|
| 1 | PrePhysics: input sampling | AWHPlayerController samples IA_* into the combat input bridge | within 2 ms |
| 2 | DuringPhysics: combat logic | UWHCombatComponent action state machine advance (doc 54) | majority of 2 ms |
| 3 | DuringPhysics: world tick | UWHFactionSubsystem, UWHWorldLedgerSubsystem change flush | minor |
| 4 | PostPhysics: frame-data commit | timers, doc 54 window opens/closes | minor |
| 5 | PostUpdateWork: save/UI reads | HUD pull (doc 58), autosave triggers (section 4.4) | outside 2 ms |

Rule: combat reads inputs in group 1 only; save writes occur in group
5 only; ledger mutations outside group 3 are deferred to group 3 by
the subsystem's internal queue. Tick groups are engine-structural, so
this table is a contract other specs cite, not a tuning value.

### 2.5 DataTable registry pattern

```cpp
// Registry: single lookup for cross-module tables. Tables live in
// /Game/WH/Data/ (section 1.3); the registry resolves row structs by
// FName so docs 54/56/57 reference tables, not file paths.
UCLASS()
class UWHDataRegistry : public UGameInstanceSubsystem {
public:
    // Registered at startup from a static list (PROPOSED names below).
    const UDataTable* GetTable(FName TableId) const;
    const FWHFrameDataRow* FindFrameRow(FName ActionId) const;
private:
    // DT_WHFrameData, DT_WHStaminaCosts, DT_WHPoiseValues,
    // DT_WHDamageTable (doc 31 names) + doc 57's ledger tables later.
    TMap<FName, TObjectPtr<UDataTable>> Tables;
};
```

Registry invariants: table ids are stable FNames; a missing table is a
fatal log at startup (fail fast, per Testerbot check T53-04); row
structs are FWH-prefixed; no gameplay code loads DataTables directly
by path, only through the registry.

### 2.6 Config: ini and debug cvars

- Config/DefaultGame.ini: game-side constants (tick budgets above,
  save slot limits, input context stack sizes). All values PROPOSED.
- Config/DefaultInput.ini: Enhanced Input defaults, doc 32 tables.
- Config/DefaultEngine.ini: scalability + the doc 31 render settings
  (low-res point-sample chain), doc 30's RemoteControl ini per 1.5.
- Debug cvars (PROPOSED list, all `wh.Core.*`, clamped to dev/test
  builds):
  - `wh.Core.DumpLedger` (log all ledger cells)
  - `wh.Core.SaveSlots.Max` (default 20, PROPOSED)
  - `wh.Core.CombatTickBudgetMs` (default 2.0, read-only alarm hook)
  - `wh.Core.TraceFrameData` (log registry lookups, doc 54 debug)
  - `wh.Core.DisableAutosave` (test builds only)

Perf-budget hooks: section 2.4's budget share is surfaced as a stat
group (`WHCoreTick`) so Testerbot can assert the hook exists (T53-09).

## 3. INPUT MAPPING (per doc 32)

Doc 32's control grammar is the source; this section makes it engine
structure. Enhanced Input only (plugin in 1.2). Rebinding is free-form
in options (doc 32); these are defaults.

### 3.1 Action names (IA_ assets under /Game/WH/Core/Input/)

| IA_WH action (PROPOSED names, doc 32 verbs) | Kbm default | Gamepad default | Doc 32 row |
|---|---|---|---|
| IA_WHMove | WASD | Left stick | Move |
| IA_WHLightAttack | LMB | X / Square | Light attack |
| IA_WHHeavyAttack | RMB (tap) | Y / Triangle | Heavy attack |
| IA_WHChargedHeavy | RMB hold 0.60 s (36 f) | Y hold 0.60 s | Charged heavy |
| IA_WHBlockParry | Shift (hold=block, tap=parry) | LB / L1 | Block/Parry |
| IA_WHOffhandBlock | n/a (slice 1: no off-hand weapon) | RB / R1 | Off-hand block/bash (techniques pass) |
| IA_WHDodgeRoll | Space | B / Circle | Dodge roll |
| IA_WHSprint | Shift + moving, no block | L3 or LB while moving | Sprint |
| IA_WHInteract | E | A / Cross | Interact / loot |
| IA_WHLockOn | MMB tap; MMB flick or Q soft-switch | R3 click / RS flick | Lock-on toggle / soft-switch |
| IA_WHAimMode | Alt hold or C | LT / L2 | Aim mode |
| IA_WHPotion | R | D-pad Up | Use health potion |
| IA_WHPotionBelt | R hold | D-pad Up hold | Belt selection (doc 32: +12 f) |
| IA_WHSpellSlot1..5 | 1-5 | D-pad L/R | Direct slots |
| IA_WHSpellWheel | Tab | D-pad Down | Wheel |
| IA_WHCrouch | Ctrl hold | D-pad Right | Crouch |
| IA_WHInventory | I | Menu/Options | Inventory |
| IA_WHCharacterMenu | K | View/Share | Character/menu |
| IA_WHCamRecenter | MMB double-tap | (stick flick recenter) | Camera recenter |

Tap/hold grammar is engine-structural: TAP = press/release under
0.30 s (18 f), HOLD = 0.30 s or longer (doc 32 conventions). Charged
heavy threshold 0.60 s (36 f) is doc 32 data, validated at M2 (doc 32
open item), not re-decided here.

### 3.2 Context stack

EWHInputContext: `Exploration`, `Combat`, `Delve` (PROPOSED enum
spelling; doc 32 names the three play surfaces exploration/combat and
the delve surfaces are doc 47's, entering as a third context).

Stack rules (PROPOSED structure):

- One active context resolves actions; contexts stack LIFO in
  AWHPlayerController (section 2.1).
- IMC_WHExploration is the base (always on in slice 1: move,
  interact, camera, menus).
- IMC_WHCombat overlays on combat-state entry and pops on exit; it
  consumes attack/block/roll/lock-on/aim actions.
- IMC_WHDelve overlays inside delve levels (doc 47); it owns any
  delve-specific verbs and inherits combat actions when combat is
  active within a delve.
- Precedence: top of stack wins on conflicting bindings; the doc 32
  Shift ambiguity (block vs sprint while moving) resolves by context
  priority: combat context maps sprint only when block is not held,
  exactly the doc 32 keyboard rule ("Shift while moving + no block").
- Context switches are the only input-driven stack mutations; combat
  state entry/exit is doc 54's state machine signaling the controller
  through the bridge (3.3).

### 3.3 Frame-data hookup contract (interface level)

The contract between input (this doc) and the combat state machine
(doc 54):

1. AWHPlayerController samples Enhanced Input actions in tick group 1
   (section 2.4) into an input frame snapshot:
   `FWHCombatInputFrame { FWHInputVerb Verb; float HoldTime;
   FWHVector2 MoveAxis; FGuid ActionInstance; }` (PROPOSED struct).
2. The snapshot crosses to UWHCombatComponent only through
   UWHCombatInputBridge::SubmitFrame(const FWHCombatInputFrame&)
   (section 2.1 composition contract). Doc 54 owns what the state
   machine does with the frame.
3. The bridge stamps each frame with the current frame index (60 fps
   fixed step, doc 32: one frame = 0.02 s / 16.67 ms). Frame indices
   are the contract key: doc 54's windows (i-frames, cancel windows,
   parry windows) index against the same counter.
4. Hold detection: the controller reports HoldTime on release or at
   threshold crossing (charged heavy at 0.60 s); the state machine
   never polls input state.
5. Context transitions (3.2) are edge events, not polled: combat
   entry/exit and delve enter/exit enqueue one bridge event each.

Contract test surface: Testerbot asserts the bridge is the only
combat-input path (T53-05) and that frame indices advance at the 60
fps fixed step (T53-06).

## 4. SAVE/LOAD ARCHITECTURE

Locked rules carried (doc 09 open questions 1-2, RESOLVED
2026-09-11, Nicko): camps save (autosave on completing camp),
taverns remain respawn points (rent a room), the unlocked warp camp
becomes the default forward respawn, taverns still usable. This
section turns those rules into engine structure.

### 4.1 What serializes into saves

FWHSaveBlob payload (PROPOSED shape; every member UPROPERTY(SaveGame)):

| Member | Type | Contents | Owner |
|---|---|---|---|
| Ledger | FWHSaveLedgerBlob (cell array) | World Ledger cells: hold states, faction meters, deed log, quest frame flags, reveal-gate states | doc 57 owns cell families; this doc owns the container |
| PlayerState | FWHSavePlayer | stats (doc 08 resolved 5: nine stats), current stamina/poise, position, equipment instance ids | doc 33 formulas |
| WorldFlags | FWHSaveWorldFlags | boss/encounter liveness flags, dungeon-generated-and-saved flag (doc 08 resolved 2), warp camp anchor + build snapshot pointer | docs 55/57 |
| RespawnAnchor | FWHRespawnAnchor | tavern anchor (level, point) or warp-camp forward respawn | this doc (SaveSubsystem) |
| Meta | FWHSaveMeta | slot timestamp, NG+ flags (doc 12 locked: NG+ after any ending), engine version tag | this doc |

What does NOT serialize: transient combat state (the action state
machine's runtime phase, doc 54), input stack state (section 3.2
rebuilds to base context on load), AI runtime state (doc 56 rebuilds
from ledger reads), renders and screenshots, procedural dungeon
interiors' geometry (regenerated deterministically from the saved
generation seed; the seed cell serializes, doc 55 owns the
generation contract).

### 4.2 Slot grammar

Slot name grammar (PROPOSED): `WH_<ProfileId>_S<NN>` where NN is the
zero-padded slot index, plus reserved auto slots
`WH_<ProfileId>_AUTO_CAMP` (camp autosave) and
`WH_<ProfileId>_AUTO_TAVEN` (tavern autosave). One profile's slots
share the Ledger version tag; loading a save whose VersionTag misses
the current schema runs the migration hook, and an unmigratable save
fails loudly (no silent corruption). Slot cap: 20 manual slots
(`wh.Core.SaveSlots.Max`, PROPOSED).

Respawn anchor semantics (locked rules as engine structure):

- Tavern anchor: set only by the tavern-rent-room interact (doc 09
  town tier: "sets your respawn point"). Serialized as
  FWHRespawnAnchor { AnchorType=Tavern, LevelPath, PointId }.
- Warp-camp forward respawn: when the warp camp is unlocked, the
  anchor type is WarpCamp and death respawns there by default; the
  tavern anchor stays valid and selectable (doc 09 resolved 2).
- Camp autosaves never move the anchor (doc 09 resolved 1: "camps
  save, taverns remain respawn points").

### 4.3 Save hooks (stubs; endgame schema is doc 57's)

Doc 46/48 sentence-sequence save hooks, as engine stubs only. Doc 48
authors the endgame consequence tables; Core only reserves the hook
points so the sentence sequence can write save state later:

```cpp
// On SaveSubsystem (stubs, PROPOSED signatures):
void HookOnEndingReached(FName EndingId);      // doc 48 sentence fork id
void HookOnSentenceCommitted(FName SentenceId); // doc 48 section 2 verbs
// Both enqueue one ledger cell write (section 2.2) executed in tick
// group 5 (section 2.4). The ending/sentence payload schema is doc
// 57's; until it lands the hooks write only the Id + timestamp cell.
```

Rule: no sentence, ending, or reveal content may be inferred from
these hooks' shapes (identity/ledger rule, doc 44 Part 2 governs
reveal gates; doc 57 owns the runtime table). This doc encodes no
knowledge a character's ledger cell forbids; the subsystem interface
carries opaque cells only.

### 4.4 Autosave triggers (structural)

- Camp completed: one autosave (doc 09 locked rule).
- Tavern anchor set: one autosave.
- Manual save: menu-driven through SaveSubsystem::WriteSlot.
- Autosaves run in tick group 5 (section 2.4) and are skippable in
  test builds (`wh.Core.DisableAutosave`, 2.6).

## 5. TEST PLAN (Testerbot)

All checks are grep-able against the witch-hunter-ue repo and this
doc. Named exactly:

| Check | Validates | Grep-able command |
|---|---|---|
| T53-01 | Class list matches section 2 | `grep -E "class (AWHGameMode|AWHPlayerController|AWHPlayerCharacter|UWHWorldLedgerSubsystem|UWHFactionSubsystem|UWHSaveSubsystem|UWHDataRegistry|UWHCombatComponent)" -r Source/WHGame --include=*.h` yields exactly the 8 doc-listed classes |
| T53-02 | Naming convention: C++ prefixes | `grep -rE "class (A|U|F)?[^WH]" Source/WHGame --include=*.h` returns no gameplay class lacking the WH/FWH/EWH prefix |
| T53-03 | Folder tree matches section 1.3 | `grep -E "/WH/(Core|Combat|World|Characters|Art|UI|Data|Audio)" -r Source Config` resolves; no gameplay asset outside /Game/WH/ |
| T53-04 | Registry fail-fast | `grep -E "UE_LOG.*(Fatal|Error)" Source/WHGame/WHDataRegistry.cpp` finds the missing-table fatal at startup |
| T53-05 | Bridge-only combat input | `grep -E "IA_WH" Source/WHGame/WHCombatComponent.cpp` returns nothing; IA_ bindings appear only in WHPlayerController + bridge |
| T53-06 | Fixed 60 fps frame index | `grep -E "FrameIndex|0\.02" Source/WHGame/WHCombatInputBridge.cpp` finds the fixed-step stamp |
| T53-07 | Save round-trip contract | a headless test writes FWHSaveBlob, reads it back, asserts cell-for-cell equality incl. FWHSaveLedgerBlob.Cells |
| T53-08 | Save rules encoded | `grep -E "AUTO_CAMP|AUTO_TAVEN|RespawnAnchor" Source/WHGame` finds camp-autosave + tavern-anchor + warp-forward-respawn wiring per doc 09 |
| T53-09 | Perf-budget hooks present | `grep -E "WHCoreTick" -r Source/WHGame` finds the stat group; `wh.Core.CombatTickBudgetMs` cvar registered |
| T53-10 | No gameplay content leaked | this doc contains no doc 46/47/48 beat names, no lore strings: `grep -E "sentence|beat " docs/planning/53-ue5-core-architecture.md` shows only structural hook references |
| T53-11 | LFS rules cover binaries | `grep -E "\.(glb|uasset|umap|png|wav)" .gitattributes` at repo root |
| T53-12 | Remote-control prerequisites | `grep -E "bAutoStartWebServer|30010|bEnableRemotePythonExecution" Config/DefaultRemoteControl.ini` per doc 30 checklist 4 |

## 6. OPEN QUESTIONS (doc 08 format, assigned)

- CO-1: DataTable CSV/JSON source-of-truth layout under
  /WH/Data/Source/ (1.5) and its import script: adopt a generic
  UDataTable import path or a custom factory? Assignment: doc 54
  authoring pass + M2 validation (Devbot, then Nicko confirms).
- CO-2: Context stack details for delve + combat overlap: does
  IMC_WHDelve own a unique verb set at slice 1, or is Delve a
  re-theme of Exploration until doc 47's delve grammar lands?
  Assignment: doc 55/56 architecture passes (Nicko, delve GDD is doc
  47).
- CO-3: Save slot cap 20 and the AUTO slot pair are invented numbers
  (PROPOSED): confirm slot budget and whether warp-camp snapshot
  data lives in the save blob or as a level-state reference.
  Assignment: Nicko, at the 50-expedition-survival GDD review (doc
  50 is the survival GDD).
- CO-4: First-party 5.8 Unreal MCP vs FFZackFair92 server: doc 30/52
  order the audit before adoption; this doc's plugin list (1.2)
  carries the stock-only stance. Assignment: doc 30 Phase 0 run
  (Devbot), record result in the doc 30 open items.
- CO-5: UWHFactionSubsystem reads axis thresholds as data; doc 12's
  ruling pass names +80/-80 and +50/-50 as PROPOSED working values
  with exact point values at GDD tuning (doc 07 XP block). If tuning
  moves them, only the ini/DataTable value changes, not this
  interface. Assignment: GDD tuning pass (Nicko), no doc edit here.
- CO-6: NG+ save shape: doc 12 locks NG+ availability and world-tilt
  but no doc yet fixes what NG+ carries into the new run's save
  (world seed vs ledger carryover). Assignment: doc 57 (data/ledger
  spec) owns the NG+ cell families; this doc's FWHSaveMeta flags
  stay the stub.

## 7. COMPLETION REPORT

- Sections delivered: 1 PROJECT STRUCTURE, 2 C++ MODULE MAP, 3 INPUT
  MAPPING, 4 SAVE/LOAD ARCHITECTURE, 5 TEST PLAN, 6 OPEN QUESTIONS.
- Class count: 8 C++ classes authored (AWHGameMode,
  AWHPlayerController, AWHPlayerCharacter, UWHWorldLedgerSubsystem,
  UWHFactionSubsystem, UWHSaveSubsystem, UWHDataRegistry,
  UWHCombatComponent referenced-as-composed, doc 54-owned) plus 5
  struct stubs (FWHFrameDataRow, FWHLedgerCell, FWHSaveLedgerBlob,
  FWHSaveBlob, FWHCombatInputFrame) and 1 enum (EWHInputContext).
- DataTable count: 4 core tables registered (DT_WHFrameData,
  DT_WHStaminaCosts, DT_WHPoiseValues, DT_WHDamageTable, doc 31
  names); registry pattern accepts doc 57's ledger tables later.
- Open questions: CO-1..CO-6 with assignments above.
- Spec conflicts: none against locked rulings found. Doc 32's
  off-hand block/bash is techniques-pass territory and is carried as
  a deferred action name only. Doc 12's axis numbers are PROPOSED
  working values and are consumed as data (CO-5). The plugin list,
  cvars, slot cap, and IA_ asset names are invented here and carry
  PROPOSED throughout.