# CC-WB1 — War-Effort Contract Board (doc 42 Part 3, doc 37-C11 lifecycle)

Spec author: IO (Autopilot wake 9, 2026-11-06). Repo: /tmp/wh-worldfeat worktree,
branch feat/world-visuals. Build: python3 tools/build_v8.py from repo root.
No harness runs, no headless browser smoke tests — node one-shots only; Nicko's
playtest is the acceptance bar.

## Scope

Turn the landed CC-WM1 Redseam mine site into a CONTRACT LOOP anchored at the
hold: a war-effort requisition board near the south road in region A
(hold_outskirts) hands out ONE Requisition paper per in-game day; filling it
means mining ironOre at Redseam (already live: 8 veins, E-gather) and turning
6 ore in at the board for a coin reward. This is the minimal doc 42 Part 3
board + doc 37-C11 lifecycle: stable board, posted/active/filled/await-states,
single reward authority, save-persisted. No NPC, no economy overhaul, no
smelting, no second contract type.

## Art anchor (law 1)

concept-04-tavern.png (approved set): weathered dark-oak board, parchment
papers, iron brackets; palette law = parchment/oak base, ONE amber accent
(lantern) per frame; amber = human fire. The board mesh follows the vision-
noted materials: desaturated browns/greys, parchment cream papers, oxidized
iron, single amber lantern = the one warm note. No red (red = pact/danger).

## B-1. CONFIG data (js/CONFIG.js)

Add block CONFIG.warEffort (new top-level key, after CONFIG.camp):

    warEffort: {
      lsKey: 'wh_wareffort_v1',            // unused this round; state rides the save-wrap (B-5)
      boardSeat: { regionId: 'hold_outskirts', x: 5.9, z: -15.5, rotY: 3.14 },
        // PROPOSED, Nicko tunes. Pre-spec lock BY DATA: scratch/cc-wb1/site_scan.js —
        // (6.7,-14.5) chosen then shifted to (5.9,-15.5): > 4.6 m from every
        // regionA static prop (nearest originally 3.34 m bandit row = enemy, 8.09 m
        // statics; clearance re-verified at final seat: nearest static
        // mossBoulder (10.5,-14.5) = 5.36 m), 88.6 m from spawn, on the south
        // road sight-line (churchArchway x=8 z=-58), 566.8 m from the Redseam
        // seam center. Region A is FLAT (WH_GROUND.has = false by design; board
        // sits y=0).
      rotYFacesRoadNorth: true,            // PROPOSED: papers face the incoming traveler
      requisition: {
        itemId: 'warOrder',                // B-2
        oreItemId: 'ironOre',              // CC-WM1 item, already live
        oreRequired: 6,                    // PROPOSED, Nicko tunes (8 veins, ~1 E-dig each)
        reward: { id: 'stolenCoin', count: 3 },  // PROPOSED, Nicko tunes; reward authority = THIS table only (37-C11)
        title: 'War Requisition',
        offerText: 'The garrison wants iron for the war. Bring 6 iron ore to this board.',
        doneText: 'Requisition filled. The quartermaster marks the board.'
      }
    }

All gameplay values PROPOSED for Nicko tuning, marked in comments.

## B-2. New item (CONFIG.items)

    warOrder: { id: 'warOrder', name: 'War Requisition', glyph: 'WO',
                category: 'document', desc: 'Garrison order: 6 iron ore for the war effort.' }

No icon PNG (glyph fallback law, ironOre precedent WH1-W2). Category 'document'
matches the stolenCoin category slot usage pattern (plain string).

## B-3. js/wareffort.js (NEW file, window.WH_WarEffort)

Module shape copies js/chest.js conventions (IIFE, WH_CONFIG, el() helper for
DOM, buildBody -> THREE.Group, game.scene.add). Public surface:

    init(game)            stash game ref; build the board body; restore state
    tryOpen()             proximity-gated E interaction (mirror chest tryOpen:
                          active region + distance <= C.rangeM 2.6 PROPOSED)
    interactPrompt()      prompt text or falsy, same contract as chest (game.js 2229)
    capture()/restore()   save-wrap payload (B-5)
    boardPos()            {x,z} for tests

Board body (buildBody): dark-oak two-post board per art anchor — posts (2 boxes
0.18x2.2x0.18 rough brown 0x4a3a2a), frame box 1.6x1.1x0.12 at y~1.5 tinted
0x3d2b1f, 3 parchment planes (0xd2b48c, MeshStandard, slight rotY jitter)
nailed on the frame face, iron bracket strip (0x6e6a63) + ONE amber lantern
emissive plane/disc on an arm (emissive 0xffb347 — the single accent) mounted
above the frame. Root name 'cc-wb1-war-effort-board'. Board does NOT collide
with walk (chest precedent: no physics body; interact is proximity, not LOS).

Interaction logic (dayNumber = game.dayNight.day, day 0 before the first rest —
dormant tutorial night; dayNight integration verified wake-pre-spec:
js/daynight.js .day +1 per dawn via camp.js rests):

  state model (single object this.logic):
    { postedDay: null, active: bool, resolvedDay: null }
  - idle (no paper out and not resolved today): tryOpen awards
    WH_Config items warOrder x1 via game.inventory.model.addItem (verify exact
    accessor against inventory.js public surface at build time: game.inventory
    addItem path used by gather.js pickup — mirror it), sets active=true,
    postedDay=dayNumber, toasts CFG.warEffort.requisition title given.
  - active (paper out): interactPrompt shows fill state 'E - War Board (n/6
    iron ore)'. tryOpen: if countOf(oreItemId) >= oreRequired: remove that many,
    active=false, resolvedDay=dayNumber, award reward, toast doneText.
    else: toast short insufficient text ('Not enough iron ore. (n/6)').
  - resolved today: papers look emptied (parchment meshes hidden), prompt
    'The board is spent until dawn.'; tryOpen does nothing.
  - NEW DAY LAW (doc 42 cadence): on any interact when resolvedDay != null and
    dayNumber > resolvedDay: state resets to idle (a fresh requisition posts at
    dawn — one contract per day). No timers, no tick hook; the check runs on
    interaction only (cheap, deterministic).
  37-C11 single reward authority: the ONLY coin payout table is
  CFG.warEffort.requisition.reward. No other code path may grant stolenCoin
  from the board.

## B-4. game.js + index.html wiring (established patterns only)

  - index.html: <script src="js/wareffort.js"></script> immediately after the
    chest.js script line.
  - Interact chain (game.js 1890): tryRescue() || tryChest() || tryGather()  →
    tryRescue() || tryChest() || tryWareffort() || tryGather()  (board checks
    before gather nodes; board seat is 15 m from any node row, no collision in
    practice).
  - Prompt block (game.js ~2229): after the chest prompt branch add the
    wareffort prompt branch (same shape: if (window.WH_WarEffort &&
    window.WH_WarEffort.interactPrompt()) text = ...).
  - Save wrap (game.js 2637/2649/2658 mirror, three sites exactly like chest):
    data.warEffort = window.WH_WarEffort.capture();  (capture)
    stored.warEffort = window.WH_WarEffort.capture(); (explicit storage write)
    window.WH_WarEffort.restore(data.warEffort);     (restore, missing = no-op)
  - Manager init (game.js 2594 chest init site): if (window.WH_WarEffort)
    window.WH_WarEffort.init(game);

## B-5. Persistence (37-C13/G13 spirit)

Capture payload: { active, postedDay, resolvedDay } (plain JSON). restore()
merges known-shape only; missing/null = fresh idle state. Death (which writes
nothing per schema law) leaves the board where the last SAVE left it —
same semantics as the chest. NO new localStorage key this round (state rides
the save-wrap like lairs/questState); lsKey field exists in CONFIG for a
future world-hopping board network, unused.

## B-6. Out of scope (explicit)

No NPC quartermaster, no second contract, no dynamic contract generation, no
board mesh GLB (module-built boxes like chest), no regionA CONFIG prop row
(board is code-built, NOT a CONFIG prop — no clearance law edits), no
economy mode, no smelting, no Redseam changes at all, no new assets/icons, no
UI/HUD changes beyond toasts + prompt text, no new sounds, no regionB/C edits,
no save schema version bump (additive field only).

## B-7. Acceptance criteria (bind into valspec)

  1. node one-shot census: CONFIG.warEffort exists with exactly B-1 fields;
     CONFIG.items.warOrder exists (glyph 'WO', category 'document');
     CONFIG.regionA byte-diff shows ONLY zero prop/node/enemy changes.
  2. Board boot: node one-shot builds the module (THREE shim), root present,
     name 'cc-wb1-war-effort-board', position (5.9, 0, -15.5) ± 0.01, 3
     parchment planes, 1 amber emissive lantern mesh.
  3. Simulated loop (node one-shot with a fake game/inventory harness OR
     module-level unit calling the public surface): idle → award warOrder x1 +
     active=true + postedDay=d; active with 3 ore → insufficient toast path, no
     removal; active with 6 ore → ore 6 removed, reward +3 stolenCoin added,
     resolvedDay=d; interact same day → spent prompt, no double reward (37-C11
     one authority), interact next day (dayNumber d+1) → idle reset, new award
     works, ore counting independent of stack layout (2 stacks of 3 accepted).
  4. Save wrap: capture() round-trips through restore() exactly; restore(null)
     = fresh idle; payload keys exactly {active, postedDay, resolvedDay}.
  5. game.js diff law: ONLY the four wiring sites (B-4) added lines; git diff
     shows no other game.js hunks; index.html diff = one script line.
  6. No .js files modified besides CONFIG.js / game.js / index.html /
     js/wareffort.js (git status law).
  7. Build: python3 tools/build_v8.py exit 0; 'CC-WB1' marker count in built
     html >= 8 (grep -o | wc -l); byte size reported.
  8. Runtime smoke (node one-shot, no browser): CONFIG loads clean after
     additions; WH_WarEffort defined with the 6 public functions (B-3).
  9. Playtest law: NO harness runs, NO headless smoke beyond node one-shots.
