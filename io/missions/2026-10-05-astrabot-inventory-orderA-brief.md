# ASTRABOT MISSION BRIEF - Inventory system, Order A (data model + grid UI + pickup/drop)
2026-10-05, from IO. Nicko's orders (10-04 evening session + clarification round):

1. "This inventory screen should include a tab for a character screen where
   you see the currently equipped items, and can equip and unequip items
   from inventory." (character tab = Order B, NOT this order)
2. "Inventory holds only a shield that can be equipped and unequipped from
   either hand. This also included and should make the longsword equipable
   and unequipable." (per-hand equip = Order B, NOT this order)
3. Capacity model: slots + per-item stack caps, fixed N-slot grid.
4. Stacks: yes - same item type joins an existing stack when picked up.
5. Starting inventory: small preloaded kit: 3 fire-bolt charges, 1 radiance
   charge, 1 bandage.
6. Drop: physical drop spawns a pickupable item entity at my feet; CONFIG
   toggle for void-drop instead.
7. Belt spells stay OUT of the inventory. Keys 1-5 / Q behave exactly as
   they do today. This order must not change their semantics.

You are Astrabot, running as a Claude Code print-mode agent in the
witch-hunter repo worktree /tmp/wh-worldfeat (branch feat/world-visuals).
Report file, commits, and pushes as in previous missions.

## 0. LAWS (hard, no exceptions)
- NO automated harness runs, NO headless browser smoke runs of any kind.
  Nicko's playtest is the ONLY acceptance test. JS syntax check
  (node --check) is the only verification you may run.
- One change order at a time. This brief = Order A. Do not start Order B.
- Commit each completed sub-step to feat/world-visuals and push
  immediately. Push route: deploy key is read-only; use the HTTPS
  credential store (push to feat/world-visuals, same as previous missions).
- All tunables in CONFIG. No magic numbers in game code.
- Art law: pixelated UI (NEAREST), darkwood palette, one accent per frame.
  NO new GLB/model work in this order. No Meshy, no asset generation.
- Never the word "free" in player copy. No hardcoded agent names.
- assets.js warns 'expected 6 clips, got 9' once per boot. Harmless. Do
  not touch anim/clip logic in this order; IO silences it later.

## 1. Current mechanics (verified by IO - do not re-research)

- Repo worktree /tmp/wh-worldfeat, branch feat/world-visuals at 30d035b.
- Game entry: prototype/index.html; core files prototype/js/*.js.
  Key modules: game.js (main loop, input), player.js, spells.js,
  assets.js (MANIFEST logical->path, prepTemplate), hud.js, CONFIG.js.
- CONFIG.belt.slots = 5, regripSeconds 0.3; belt = ['firebolt', null, ...];
  Q loadout toggle (CONFIG.loadout.toggleSeconds = 0.8).
- Keys 1-5: quick equip/stow left-hand spell (shield on stow) - DO NOT
  TOUCH. RMB = cast when spell equipped, block when shield equipped -
  DO NOT TOUCH.
- Player lantern lives on yawFrame. Camera fully decoupled (mouse drag /
  camera joystick only).
- The in-game HUD is DOM-based (hud.js) - the inventory screen should be
  DOM/HTML+CSS in the same style (pixelated, darkwood), not canvas.
- There is currently NO item entity system, NO pickup system, NO
  inventory data structure anywhere in the codebase. You are adding the
  first one; make it generic (stage 2 will wire enemy drops + gatherables
  through the same pickup flow and item registry).

## 2. ORDER A - scope

### A1. Inventory data model (CONFIG + core module)
- New file prototype/js/inventory.js, loaded by index.html AFTER spells.js
  and BEFORE game.js (match the script tag order style). Global:
  window.WH_INVENTORY.
- CONFIG.inventory = {
    slots: 24,                    // fixed grid size, growable later
    startingItems: [
      { id: 'fireboltCharge', count: 3 },
      { id: 'radianceCharge', count: 1 },
      { id: 'bandage', count: 1 },
    ],
    drop: {
      mode: 'physical',           // 'physical' | 'void'
      scatterRadius: 1.75,        // meters, where dropped items land
      pickupRadius: 1.6,          // meters, auto-pickup on E / walk-over per A4
    },
  }
- CONFIG.items = {} registry entries for: fireboltCharge, radianceCharge,
  bandage, longsword, roundShield. Each entry: {
    id, name (player-facing), stackCap (ingredients/consumables 60 default
    via CONFIG.inventory.defaultStackCap; gear = 1), category
    ('consumable' | 'gear'), // gear items carry gear-only fields
    // for gear: equipHint ('mainHand' | 'offHand'), used by Order B
    // for consumables: useHint (Order B+ reads these; e.g. bandage heals)
  }
  Keep item ids EXACTLY: 'fireboltCharge', 'radianceCharge', 'bandage',
  'longsword', 'roundShield'. Do not invent extra items.
- Data structure (per-player, on player object or module state your
  design keeps): slots = array of CONFIG.inventory.slots entries; each
  slot = null | { id, count } (count <= stackCap of that item). Stacks
  join when picking up the same id; full stacks open a new slot.
- API (module exports, exercised by A3/A4): addItem(id, count) ->
  returns actually-added count (respects stack caps + free slots),
  removeItem(id, count), countOf(id), slotAt(i), forEachSlot(fn),
  and internal spill logic order: existing partial stacks first, then
  empty slots, then refuse (no satchel pouch in Order A - Populate stage
  decides if we add it).

### A2. Inventory UI - grid screen (I key)
- CONFIG.inventoryUI = { openKey: 'KeyI', closeKeys: ['KeyI', 'Escape'] }.
- Pressing I opens a centered modal: darkwood-styled DOM panel, pixelated
  borders, title "INVENTORY", 24-slot grid (6x4), tab strip with two tabs:
  "INVENTORY" (active this order) and "CHARACTER" (tab exists but renders
  a locked/empty placeholder line "Coming soon" - Order B fills it; do
  NOT build equip/unequire logic here).
- Each occupied slot: item name glyph + stack count (bottom-right),
  hover tooltip (name + category line). Empty slot: subtle frame.
- While the inventory is open: movement input and combat input (WASD,
  LMB/RMB, roll, spell keys 1-5, Q) are SUSPENDED - mouse cursor free,
  camera drag disabled. Closing restores all input instantly. Pausing the
  world is NOT required (enemies keep moving; this is a survival game) -
  player actions pause instead. If that feels wrong we tune later.
- Clicking an occupied inventory slot this order: selects it (highlight).
  No drag, no context menu yet - drop uses the keyboard path (A4).
- Slot index / layout constant lives in CONFIG (gridCols: 6).

### A3. Starting items + boot wiring
- On player spawn (fresh state), inventory starts with exactly
  CONFIG.inventory.startingItems (3 fireboltCharge, 1 radianceCharge,
  1 bandage). These are INVENTORY items, NOT belt charges - belt spells
  stay untouched and key 1/2 keep casting as today (belt is a casting
  system, inventory is a possession system; consuming inventory charges
  to fuel belt spells is a later-order decision, NOT this order).
- If a later load/save system exists by the time you build, do not wire
  persistence - persistence lands with camp savepoints in a later stage.

### A4. Drop + pickup (physical entity flow)
- Drop action this order: with inventory open, selected slot + a visible
  key hint ("DROP" keybind = 'KeyG' via CONFIG.inventoryUI.dropKey)
  drops 1 of that stack (or whole stack with Shift held - your call, but
  document it in the report). Void mode instead deletes count and shows a
  brief toast "Dropped Bandage x1".
- Physical drop: spawn an item entity at my feet + scatter (random angle,
  radius up to CONFIG.inventory.drop.scatterRadius), ground-aligned (reuse
  prop ground-y conventions; y must sit on terrain like props do).
  Entity render: billboarded pixel-style quad OR tiny box placeholder
  colored per item category (consumable = amber accent, gear = cyan
  accent) - placeholder visuals acceptable, art pass later. NO new GLBs.
- Pickup: walking within pickupRadius + pressing E auto-collects nearest
  item entity into inventory (stack-join first). If inventory full ->
  toast "Inventory full" and the entity stays. E when nothing nearby
  does nothing (interact prompt integration is a later stage).
- Item entities persist in the world list like other dynamic entities;
  no save wiring this order.
- 'KeyX' alternative NOT needed; keep one drop key only (G).

### A5. Report
- Write scratch/astrabot_inventory_orderA_report.md: what landed, files
  touched, CONFIG keys added, how pickup/drop/open flows route, any
  judgment calls. Commit + push with the code commits.

## 3. Acceptance criteria (Nicko plays, then verdicts)
- A: I opens/closes inventory; grid 6x4; tab strip visible with
  CHARACTER placeholder.
- B: Boot state shows the 3 starting items with correct counts.
- C: With G on a selected stack, one unit drops, spawns at my feet with
  scatter, walk back + E picks it up, count updates (stack-join works).
- D: Movement/combat input suspended while inventory open; restored
  instantly on close. Belt keys 1-5 and Q unaffected by the whole order.
- E: Filling inventory then dropping nothing -> pickup refusal toast,
  entity remains on ground.
- F: Void-mode toggle in CONFIG flips drop behavior (testable by IO after
  landing by flipping the CONFIG flag).

Order B (separate brief, later): character tab - equipped-items view,
free per-hand equip/unequip for longsword + roundShield (either item to
either hand, one item per hand), RMB chain gated to melee-in-right-hand.
Do NOT implement any part of B in this order.