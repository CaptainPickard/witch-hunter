# Astrabot report - Inventory Order A (data model + grid UI + pickup/drop)

Brief: `io/missions/2026-10-05-astrabot-inventory-orderA-brief.md`
Branch: `feat/world-visuals` (worktree `/tmp/wh-worldfeat`). Order B was not started.

## Commits (all pushed)

| sha | step |
|---|---|
| 4bbb210 | A1 data model: CONFIG.inventory / items / inventoryUI + `WH_INVENTORY` API |
| 7fb993a | A2 grid screen (I), tabs, select + tooltip, input suspension |
| 99e028a | A3 starting kit at boot |
| f1734f2 | A4 drop (G / Shift+G) + pickup (E), void-mode toggle, debug hooks |
| (this) | A5 report |

## Verification

- **No harness or browser runs** (per LAWS). Nicko's playtest is the acceptance test.
- **Syntax check:** `node` is not installed on this host, so `node --check` could
  not run. I used the closest equivalent, a parse-only check with Python
  `esprima.parseScript`, on every `prototype/js/*.js`. All 12 files parse cleanly.
  It never executes code, same as `node --check`.

## Files touched

- `prototype/js/inventory.js` (new, loaded after spells.js and before player.js/game.js)
  - `Inventory`: slots model, `addItem`, `removeItem`, `removeFromSlot`, `countOf`,
    `slotAt`, `forEachSlot`, `fillStartingItems`
  - `InventoryUI`: the DOM modal and the HUD toast
  - `WorldItems`: ground item entities
  - module helpers: `active`, `itemDef`, `stackCapOf`, and module-level
    `addItem/removeItem/countOf/slotAt/forEachSlot` that act on `active`
- `prototype/js/CONFIG.js`: three appended sections (below).
- `prototype/js/game.js`: `setupInventory()` (boot), `dropFromSlot()`, `tryPickup()`,
  the E listener, the `worldItems.update` tick in the loop, and WH_DEBUG hooks.
- `prototype/js/player.js`: `inputSuspended` flag + `setInputSuspended()`, plus gates
  on keydown, mousedown, wheel and `collectMoveInput`.
- `prototype/js/touch-controls.js`: same gate on the camera pad and action buttons.
- `prototype/index.html`: script tag. `prototype/style.css`: `#wh-inv` modal and `#wh-toast`.

## CONFIG keys added

```
CONFIG.inventory = {
  slots: 24, defaultStackCap: 60,
  startingItems: [fireboltCharge x3, radianceCharge x1, bandage x1],
  drop: { mode: 'physical' | 'void', scatterRadius: 1.75, pickupRadius: 1.6 },
  entity: { size: 0.28, spinDegPerSec: 70,
            colors: { consumable: 0xd8b24a (amber), gear: 0x4ac8d8 (cyan) } }
}
CONFIG.items = { fireboltCharge, radianceCharge, bandage, longsword, roundShield }
  each: id, name, glyph (2-letter slot label), category;
  gear: stackCap 1 + equipHint 'mainHand' | 'offHand';
  consumables: no stackCap (-> defaultStackCap 60) + useHint (data only, nothing reads it yet)
CONFIG.inventoryUI = { openKey: 'KeyI', closeKeys: ['KeyI', 'Escape'], dropKey: 'KeyG',
                       pickupKey: 'KeyE', gridCols: 6, toastSeconds: 1.8 }
```

## How the flows route

- **Open/close:** `InventoryUI` listens for `keydown`. I opens the screen; I or Esc closes
  it. It then calls `onOpenChange(open)`, which game.js turns into
  `player.setInputSuspended(open)`.
- **Suspension:** while `player.inputSuspended` is set:
  - The keydown handler still records key states but returns before any action:
    Space roll, F lock-on, Q, 1-5, R/T.
  - mousedown is ignored (LMB attack and drag start, RMB cast/block).
  - wheel zoom is ignored.
  - `collectMoveInput` reads no keys, so WASD and the touch stick do nothing.
  - The touch camera pad and touch buttons are ignored.

  Opening the screen also stops any camera drag and drops a held block. A swing,
  roll or cast windup that is already running plays out. Closing just clears the
  flag. Keys held through the close resume immediately, because their state was
  still being tracked. The world keeps running (enemies move). The cursor needed no
  change because the game never used pointer lock.
- **Belt keys:** 1-5, Q and RMB routing are unchanged when the screen is closed.
  The only new rule is that they are ignored while it is open.
- **Select:** clicking a filled slot highlights it with the amber border. Clicking it again
  clears it. Clicking an empty slot clears the selection.
- **Drop:** with the screen open and a slot selected, G calls
  `game.js dropFromSlot(i, shiftHeld)`.
  - G drops 1. **Shift+G drops the whole stack** (my call).
  - `void` mode deletes the items and toasts "Dropped Bandage x1".
  - `physical` mode spawns ONE entity carrying the dropped count, at a uniform random
    point in the scatter disc around the player. It then goes through the player's own
    `clampPlayer` and `pushOutOfProps`, so it can never land out of bounds or inside a prop.
- **Pickup:** with the screen closed and the player alive, E calls `tryPickup()`.
  - It finds the nearest entity of the active region within `pickupRadius` on the
    ground plane and runs `addItem` (partial stacks first, then empty slots).
  - Everything fits: the entity is removed and a "Picked up X xN" toast shows.
  - Nothing fits: "Inventory full", and the entity stays.
  - Part fits: the entity keeps the remainder, with an "Inventory full" toast.
  - If nothing is in range, nothing happens.
- **Entities:** placeholder unlit box (`MeshBasicMaterial`, so it reads at night) with its
  bottom face at y = 0, the same ground convention props use (`p.y || 0`; terrain is flat).
  It spins slowly. Each entity is tagged with the region it was dropped in. Both regions
  share one world space, so an entity shows (and can be picked up) only while its region
  is active. The list lives on `game.worldItems` and survives region swaps. Nothing is saved.

## Judgment calls

1. Shift+G = whole stack. G = 1.
2. A physical drop of N items = one entity with count N, not N boxes. Pickup joins stacks.
3. The starting kit is filled at **boot only**. Death and respawn keep the inventory.
   Death-loss rules land with camp savepoints.
4. Added a **"Picked up X xN" toast** on a successful pickup. The brief only asked for the
   void-drop and inventory-full toasts, but with the screen closed this is the only
   pickup feedback. Physical drops show no toast (the box is the feedback).
5. E pickup is ignored while the inventory is open, since all player actions are paused.
6. Drop points are clamped to the player's walkable area (bounds and prop push-out).
7. Tooltip category line reads "Consumable" or "Gear". Slot labels are 2-letter glyphs from
   CONFIG (`glyph`): FB, RA, BD, LS, SH. Placeholder until icon art.
8. Toast z-order sits above the modal backdrop, so drop toasts are visible with the screen open.
9. `node` is not on this host, so the syntax check used esprima (see Verification).

## AC test notes (for Nicko / IO)

- **A:** I opens; I or Esc closes. 6x4 grid. INVENTORY and CHARACTER tabs; CHARACTER
  shows "Coming soon".
- **B:** FB 3, RA 1, BD 1 in the first three slots. Every stackable item shows its count,
  including 1. Gear (stack cap 1) shows none. Hover shows name and category.
- **C:** Click FB, press G, and an amber box lands at your feet; FB shows 2. Close, walk
  to the box, press E: "Picked up Firebolt Charge x1", and FB is back to 3 in the same stack.
- **D:** With the screen open, WASD, mouse buttons, Space, F, 1-5, Q, R/T and camera drag/zoom
  do nothing. Close it and everything responds at once.
- **E:** In the console, `WH_DEBUG.addItem('longsword', 24)` fills every empty slot
  (gear stacks to 1). With a box on the ground, E gives "Inventory full" and the box stays.
  Alternative: drop an item first, then fill.
- **F:** Set `WH_CONFIG.inventory.drop.mode = 'void'` (works live in the console, or edit
  CONFIG.js). G then deletes the item and toasts "Dropped Bandage x1".

## Debug hooks added

`WH_DEBUG.getInventory()`, `addItem(id, count)`, `getWorldItems()`, `isInventoryOpen()`.

## Left undone / out of scope

- All of Order B: character tab contents, per-hand equip of longsword / roundShield,
  RMB gating.
- Consuming inventory charges to fuel belt spells, and using the bandage (`useHint` is
  data only).
- Persistence, an interact prompt for E, drag and drop, context menus, icon art.
- The assets.js "expected 6 clips" warning was left alone, as ordered.
