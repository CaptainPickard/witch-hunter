# 52 - UE5.8 Architecture Spec Set: Plan of Record

Status: Drafted 2026-09-16, architecture-spec phase opening (Nicko directive:
turn the GDDs into architecture specs for UE5.8, preparing for
implementation). PROPOSED for Nicko review. This doc defines the spec set,
module boundaries, authoring order, and gate rules. Subordinate to doc 31's
locked engine plan (UE 5.8, /WH folder layout, custom combat component,
GAS deferred, perf budgets).

## What "architecture spec" means here

A GDD says WHAT the game does (beats, meters, doors, sentences). An
architecture spec says HOW UE5.8 carries it: C++ classes, DataTables,
Blueprints, assets, subsystems, file paths, tick groups, replication
stance, and the test plan per module. Every architecture spec cites its
GDD/planning source and changes no ruling.

## Locked engineering ground (carried from doc 31, not re-decided)

- Engine: UE 5.8 (locked, doc 31).
- Repo: separate witch-hunter-ue repo, LFS for binaries (doc 31).
- Folder layout under /Game/WH/: Core, Combat, World, Characters/*,
  Art/Materials, Art/PostProcess, UI, Data, Audio (reserved).
- Combat: CUSTOM lightweight action stack, one C++ UCombatComponent
  owning an action state machine (startup/active/recovery), reading
  frame data from DataTables. GAS adoption gate at slice exit (decided
  at the UE5 spike per doc 31 open items).
- Perf budget (doc 31 G23): 60 fps locked at 1080p output / 720p
  internal point-sampled upscale; 2 ms game thread for combat logic;
  under 1,500 draw calls; under 2 M triangles; under 20 skinned meshes.
- Pipeline: doc 30 remote manual (VPS asset prep, editor on Nicko's PC,
  Remote Control API :30010 control plane). UE 5.8 first-party Unreal MCP
  audited before adopting the FFZackFair92 server.

## The architecture spec set (docs 53-58, one per module)

| Doc | Module | Source GDDs/planning | Contents |
|---|---|---|---|
| 53 | Core & project structure | 31, 03, 12 | Game mode, player controller, camera, input mapping (doc 32), save/load, subsystems, DataTable registry, folder/file naming |
| 54 | Combat | 04, 32, 34, 33, 33-equipment | UCombatComponent state machine, frame-data schema, hit/hit-stop/i-frames, poise/stagger calculators, weapon classes, damage pipeline |
| 55 | World & streaming | 03, 13, 49, 22, 12 | Level streaming for the continent, hold-overlay integration, procedural dungeon gen, delve layouts as levels, seat/city maps |
| 56 | AI & spawning | 34, 04, 41, 19 | Enemy AI state machines, pair/pack grammars, spawn rules, World Ledger read hooks, encounter tables wiring |
| 57 | Data & the World Ledger | 20, 12, 19, 44-P2, 46 | Ledger schema (save-serializable), deed log, faction/sect meters, quest frame templates, knowledge-ledger reveal gates |
| 58 | UI/HUD & presentation | 27, 31, 24, 29, 30, 25 | UMG HUD minimum, sprite/billboard stack, layered paper-doll equipment, pixel register material + post chain, GLB import pipeline |

Authoring order: 53 and 54 first (they unblock the doc 31 M2/M3
milestones), then 55, 56, 57, 58. Docs 47-51 GDDs are additional sources
per module (delves feed 55; sentences feed 57's save schema; doors feed
55/56; bestiary feeds 56).

## Gate rules for this phase

1. IO authors the master plan and per-module spec briefs (this doc +
   spec files). Devbot authors each architecture doc from its spec.
   Testerbot validates consistency against GDDs + planning corpus.
2. Every architecture doc carries: module class list (C++ header-level
   signatures), DataTable schemas with column types, asset lists with
   /Game/WH paths, and OPEN QUESTIONS where a GDD leaves engine choices
   open. No GDD/ruling edits.
3. GAS stays deferred: combat spec authors the custom stack; a GAS
   migration appendix records the shape for the slice-exit gate.
4. Ledger compliance carries over: no architecture beat may encode a
   fact a character's doc 44 Part 2 cell forbids (the knowledge ledger
   is a runtime data structure in doc 57, and its gates are enforced).
5. No em dashes. PROPOSED markers on invented numbers. Doc 08 format
   open questions with assignments.

## Blocked-on-Nicko register (does not block spec authoring; blocks implementation milestones)

- UE5 spike prerequisites (doc 29/31): Meshy/Tripo API key + a Windows
  machine with UE 5.8 provisioned. M0 pipeline-live and the GAS/perf
  validations gate on this.
- Doc 46 OQ-8/OQ-9 (Gambit hostility interpretation, ambush hours) and
  the open-question queues in docs 47-51: tuning/rulings, assignable to
  a session pass; the architecture specs reference them as open and do
  not derive from them.

## Status line convention

Each architecture doc opens: "Drafted 2026-09-16, UE5.8 architecture spec
(doc 31 engine plan governs; GDDs 46-51 + planning corpus are the content
source). PROPOSED for Nicko review. Subordinate to locked rulings;
conflicts are open questions, not edits."