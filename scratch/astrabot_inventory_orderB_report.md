# Astrabot report - Inventory Order B (free per-hand equip, CHARACTER tab, INV button, magic-canon kit)

Brief: `io/missions/2026-10-05-astrabot-inventory-orderB-brief.md`
Branch: `feat/world-visuals` (worktree `/tmp/wh-worldfeat`). Nothing beyond Order B was started.

## Commits (all pushed)

| sha | step |
|---|---|
| 9caa786 | B1 + B4: two-hand equip model, RMB/LMB/Q/belt rewiring, either-hand mounts, kit retrofit |
| 00fed73 | B10: per-character expected clip counts (boot warning silenced) |
| 8b3dd20 | B2: CHARACTER tab (hand slots, inventory gear list, learned spells) |
| 1f34391 | B3: INV HUD button |
| (final) | review fixes + glow anchor cache + this report |

B1 and B4 share one commit because they depend on each other: the boot hands
need `magicGlove`, and the kit only makes sense with the hand model in place.

## Verification

- **No harness or browser runs** (per LAWS). Nicko's playtest is the only acceptance test.
- **Syntax:** `node` is not installed here. I ran `esprima.parseScript` (Python,
  parse-only, never executes) on every `prototype/js/*.js`. All files parse.
- **Offline measurements** (Python on the GLB JSON/bin, no Blender/Meshy):
  - `scratch/measure_hand_mirror.py`: the L_Hand and R_Hand bind-pose local frames
    map onto each other by diag(-1, 1, 1) within 0.01. That is the basis for
    mirroring a mount into the other hand.
  - Clip counts: the combat-chain player GLB has 9 clips (6 whanim1 + WH_SlashR2L,
    WH_SlashL2R, WH_Thrust). Bandit and ghoul have 6 each.
- **Static review** of the full diff (read-only, nothing executed). No stale
  references to the removed fields and no item duplication or loss in any
  equip, move, unequip or Q path. Fixed in the final commit:
  - The INV button no longer swallows `mouseup`. Before, releasing RMB or LMB
    over it left a guard or camera drag stuck on.
  - `tryBlock` now refuses during the Q toggle window. The shield stays in hand
    until the swap lands, so blocking could open a parry mid-swap.
  - `prepShield` has a once-per-mesh guard.
  - A debug `equipWeapon` moveset is no longer reset by unrelated hand changes.
  - The glow mirror reads `equip.nativeHand.magicGlove`.
- **Known and left as is:** a cast already winding up when Q is pressed can still
  fire during the window (it is dropped only when the glove actually leaves).
  This is the same as before Order B.

## JUDGMENT CALL 1 - which mouse button runs the attack chain (please confirm)

The brief says "RMB attack chain fires ONLY when a melee weapon is in the RIGHT
hand" and lists RMB precedence as `1) melee-right -> chain, 2) caster -> cast,
3) shield -> block`. In the code the chain has always been on **LMB**
(`player.js` mousedown button 0 -> `tryAttack`). Every earlier spec agrees:
"LMB attack, RMB cast/block".

Taken literally, the brief would break things. With the boot loadout (sword
right, glove left), RMB would always swing and **casting would be unreachable**.
AC B6 would also fail: with the glove unequipped and the sword in the right hand,
RMB would swing instead of "does nothing".

So I treated "RMB attack chain" as a mislabel for the attack button:
- **LMB** (and the touch attack button) runs the chain only when `hasMeleeRight()`.
  With the sword in the left hand, or no sword, LMB does nothing except drag the camera.
- **RMB** (and the touch block button) uses `secondaryAction()`, the first entry of
  `CONFIG.equip.rmbOrder` that the hands can do. The default `['caster', 'shield']`:
  1. a caster in either hand casts the active learned spell
  2. otherwise a shield in either hand gives hold-to-block
  3. otherwise nothing happens

  Cast wins over block, as the brief ruled. `rmbOrder: ['shield', 'caster']` flips it.

Read with "the attack button" = LMB, every AC row passes. If Nicko really wants the
chain on RMB, it is a small change in `secondaryAction()`.

## Flows

**Hands model** (`player.js`, section "Order B: hands")
- `player.hands = { right, left }` holds item ids or null.
- Every gear item is a single instance: it is either in a hand or in the inventory
  grid, never both. Equipped items are not in the grid.
- Capability flags, derived only from `CONFIG.items[id].kind`:
  `hasCaster()` / `casterHand()`, `hasShield()`, `hasMeleeRight()`.
  Every combat gate reads these:
  - `tryAttack`: melee in the right hand
  - `canCast`: a caster in either hand
  - `tryBlock`: a shield in either hand
  - `update()` drops a held guard when no shield is left
- `equipItem(id, hand, inventoryOnly)`:
  - Refuses when the item is not gear, or the hand is not in `def.hands`.
  - Source is the other hand (a move) or the inventory (`removeItem`).
  - Any item already in the target hand goes back to the inventory. Drawing from
    the inventory frees a slot (gear stacks to 1), so that always fits.
  - A hand-to-hand move with something already in the target hand needs a free
    slot. Otherwise it is refused with "Inventory full".
  - Every refusal shows a toast and the block flash.
- `unequipHand(hand)`: hand -> inventory. When the inventory is full the item
  stays in the hand and the "Inventory full" toast shows.
- `handsChanged()`:
  - cancels a swing when no melee is left in the right hand
  - sets the moveset from `def.moveset`
  - ends a block when no shield is left
  - drops a pending cast when no caster is left
  - restarts the 0.3s regrip when the caster changes hands
  - derives `activeLoadout` for the HUD I/II pips (1 = glove left, 2 = shield left, 0 = other)
  - remounts meshes and redraws the screen
- Boot: the kit fills the grid, then `equipDefaultHands()` moves
  `CONFIG.equip.defaultHands` into the hands (glove left, longsword right).
  The grid then shows only Round Shield and Bandage.
- Death and respawn keep the hands, the same as the inventory.

**Belt keys 1-5**
- Each key picks the active learned spell: `pressBeltKey` -> `selectBeltSlot`.
- An empty slot gives the refusal flash, as before.
- Pressing the key of the spell that is already active does nothing. The old
  "press again to stow to the shield" behavior is gone, because hands are now
  set from the equip screen.
- Switching spells drops a cast still in windup.
- The 0.3s regrip only starts when a caster is in hand.
- The HUD belt always tints the active slot in the spell's school color, so 1/2
  give visible feedback even without a caster. With no caster, the spell slots
  dim (`#wh-belt.stowed`).

**Q (`toggleLoadout`)**
- Q swaps the left hand between `CONFIG.equip.qSwap[0]` (magicGlove) and `[1]`
  (roundShield). If the left hand holds the glove, the shield goes in. If it holds
  anything else (the shield, nothing, or a moved sword), the glove goes in.
- The incoming item must be in the INVENTORY. Otherwise "Round Shield not in
  inventory" (or "Magic Glove ...") shows and nothing changes: no window, no
  chain reset.
- The 0.8s window and the chain reset work exactly as before. The swap lands when
  the window completes, and the source is checked again then.
- The outgoing item goes back to the inventory.

**Meshes**
- Each gear item with `CONFIG.items[id].mesh` gets one GLB instance at boot
  (`game.js setupHandMeshes`). That means the longsword and the shield. The glove
  has no mesh.
- `applyHandVisuals()` mounts each instance on the bone of the hand holding it
  (`mountWeapon` / `mountShield`). When the item is unequipped, the instance is
  detached and hidden.
- Mounts are measured for each item's native hand (`CONFIG.equip.nativeHand`:
  sword right, shield left). In the other hand, the rotation is mirrored as S·R·S
  and the offset as S·p, with S = `CONFIG.equip.mirrorScale` (measured
  diag(-1, 1, 1)).
- One-time prep (sword grip slide, shield disc centring) now runs once per mesh,
  so a remount never applies those offsets twice.

## JUDGMENT CALL 2 - glove placeholder visual

The brief asks for "the existing spellGlow orb on THAT hand, same idle-pose offset
mirrored for right hand". The old anchor was a fixed point on yawFrame at
`(-idlePose.x, ...)`. In the skinned rig, +X is body-left (radiance
`anchorOffset` note; L_Hand measures at +X). So that point does not reliably sit
on a hand, and it does not follow animation.

Default `CONFIG.equip.casterGlow.anchor: 'hand'`:
- The orb is parented to the caster hand bone, at `handOffset` (the measured
  L_Hand fist centroid, mirrored for R_Hand). It rides the animation and is
  colored by the active spell's school.

`anchor: 'idlePose'` restores the old yawFrame anchor, mirrored per hand, as the
brief literally describes. The rigid stand-in body (no bones) always uses that path.

## JUDGMENT CALL 3 - small rules the brief left open

- **Moving into an occupied hand:** the occupant goes back to the inventory. It
  does not swap into the other hand. This matches unequip, and the result is
  predictable.
- **Grid order:** the boot auto-equip leaves slots 0-1 empty, so the shield and
  bandage sit at slots 2-3. I did not add compaction (Order A has none).
- **Learned spells:** `getKnownSpells()` returns the filled belt slots. There is
  no separate spellbook store yet. Books and scrolls (stage 2) will add to the belt.
- **Spell names on the CHARACTER tab:** the id with its first letter capitalized
  (CONFIG.spell has no `name` field).

## CHARACTER tab (`inventory.js InventoryUI.renderCharacter`)

- **EQUIPPED:** a RIGHT HAND row and a LEFT HAND row. Each shows the item's glyph
  tile and name, or "Empty".
  - Click a row to unequip.
  - A held item that may enter the other hand gets a `[L]` or `[R]` button that
    moves it across. This is what AC B4 tests.
- **SPELLS:** the learned spells (key number + name). The active one shows ACTIVE.
  Click one to select it, the same as its belt key.
- **INVENTORY GEAR:** a scrollable list of the gear in the grid.
  - Each row shows the glyph, the name, and `hands: R / L*`, where `*` marks the
    default hand.
  - Click the row to equip to the `equipHint` hand. `[L]` / `[R]` equip to that hand.
- The UI only calls `opts.equip` (`hands / equip / unequip / spells /
  selectSpell`). `game.js` backs those with player methods, so the rules live in
  `player.js`.
- It reuses the darkwood `.inv-panel` / `.inv-slot` look. Hover borders use amber.

## INV button (`inventory.js` InventoryUI ctor, `style.css #wh-inv-btn`)

- A body-level `<button>` in the bottom-left corner. Position and label come from
  `CONFIG.inventoryUI.openButton`.
- It toggles the screen with `setOpen(!open)`, the same path as the I key.
- It reacts on `pointerdown`, so it works with both mouse and touch (the
  touch-toggle pattern). It swallows mousedown, mouseup, click and contextmenu,
  so a click never starts a swing or a camera drag.
- `tabIndex -1`, so Space never presses it.
- z-index 46 keeps it above the modal (20) and the touch toggles (45), so it
  closes the screen as well. It is lit amber while the screen is open.

## Code anchors changed

- `prototype/js/player.js`:
  - constructor: `hands`, `inventory`, `itemMeshes`, `pendingQSwap`; removed
    `offhand` and `leftHand`
  - mount helpers: `isMirrored`, `mirrorQuat`, `mirrorVec`, `boneFor`
  - `mountWeapon` replaces `setWeapon`; `equipWeapon` (debug moveset swap)
  - `toggleLoadout`, `selectBeltSlot`, `pressBeltKey`, `getKnownSpells`
  - the new "Order B: hands" section: flags, `secondaryAction` / `secondaryDown` /
    `secondaryUp`, `equipItem`, `unequipHand`, `equipDefaultHands`, `handsChanged`,
    `setItemMesh`, `prepShield`, `applyHandVisuals`, `mountShield`
  - gates in `tryBlock`, `canCast`, `tryAttack`; the Q completion and guard drop in `update()`
  - mouse RMB down/up handlers; `respawnAt`
  - removed: `equipBeltSpell`, `stowToShield`, `setLeftHand`,
    `applyLeftHandVisual`, `setShield`, `setWeapon`
- `prototype/js/game.js`:
  - new `updateCasterGlow()`; `instanceHandMesh`, `equipPlayerWeapon` (debug),
    `setupHandMeshes`
  - `setupInventory()`: default hands, `opts.equip`, `onEquipRefusal`, `onHandsChanged`
  - HUD belt `stowed` = no caster
  - debug hooks: `getHands`, `equipItem`, `unequipHand` replace `getLeftHand` / `getOffhand`
  - boot calls `setupHandMeshes()` in place of `equipPlayerWeapon` + `equipPlayerShield`
- `prototype/js/inventory.js`: `kindOf`, `defaultHandOf`,
  `Inventory.hasRoomFor`, `InventoryUI` (`opts.equip`, INV button,
  `renderCharacter`, tooltip text), and the module exports.
- `prototype/js/touch-controls.js`: the block button routes through
  `secondaryDown` / `secondaryUp`.
- `prototype/js/assets.js`: `CHARACTERS` holds the expected clip counts
  (`playerBody: 9`, `banditBody: 6`, `ghoulBody: 6`).
- `prototype/js/CONFIG.js`: `inventory.startingItems`, `items`, the new `equip`
  section, `inventoryUI.openButton`, and the belt comment.
- `prototype/style.css`: CHARACTER tab classes (`.inv-char*`, `.inv-sec`,
  `.inv-hand*`, `.inv-gear*`, `.inv-spell*`) and `#wh-inv-btn`.

## Tunables (all CONFIG)

| key | default | what |
|---|---|---|
| `equip.defaultHands` | `{ right: 'longsword', left: 'magicGlove' }` | boot auto-equip from the kit |
| `equip.rmbOrder` | `['caster', 'shield']` | RMB precedence (cast-first) |
| `equip.qSwap` | `['magicGlove', 'roundShield']` | the Q left-hand pair |
| `equip.nativeHand` | `{ longsword: 'right', roundShield: 'left', magicGlove: 'left' }` | which hand each mount was measured for |
| `equip.mirrorScale` | `[-1, 1, 1]` | other-hand mount mirror (measured) |
| `equip.casterGlow` | `{ anchor: 'hand', handOffset: [0.018, 0.078, 0.021] }` | glove placeholder orb |
| `items[*].kind` | `caster` / `melee` / `shield` | capability source |
| `items[*].hands`, `equipHint` | see CONFIG | allowed and default hands |
| `items.magicGlove.cast.powerTier` | 1 | glove 1 < wand 2 < staff 3 (not read yet) |
| `items[*].moveset`, `mesh` | `longsword` | melee chain + hand GLB |
| `inventory.startingItems` | glove, longsword, shield, bandage (x1) | boot kit |
| `inventoryUI.openButton` | `{ enabled: true, label: 'INV', left: 16, bottom: 20 }` | HUD button |

The Order A keys are unchanged, apart from the item registry and kit entries
this order explicitly replaced.

## AC notes (Nicko playtest)

| AC | expected behaviour / note |
|---|---|
| B1 | At boot, CHARACTER shows RIGHT = Longsword, LEFT = Magic Glove. The INVENTORY grid shows SH + BD (slots 3-4). |
| B2 | Clicking the RIGHT HAND row empties it and puts LS back in the grid. `[L]` on the Longsword row puts it in the left hand. Because the glove sits there, the glove goes back to the inventory. LMB (the attack button, see judgment call 1) does not chain. `[R]` puts it back in the right hand, and the chain fires again. |
| B3 | Shield `[R]` (the sword goes to the inventory), then unequip the glove: RMB hold blocks. Re-equip the glove with `[L]` or `[R]`: RMB casts firebolt (cast-first). The shield stays visibly carried. |
| B4 | One instance per item, enforced in `equipItem` (it moves, it never copies). `[L]` / `[R]` on a held item moves it across hands. |
| B5 | Click or tap INV to toggle. The I key is unchanged. The button also closes an open screen. |
| B6 | 1/2 change the belt tint and the CHARACTER "ACTIVE" marker. With the glove unequipped and no shield in hand, RMB does nothing. Re-equip the glove and casting works (after the 0.3s regrip). |
| B7 | Q swaps glove <-> shield in the left hand (0.8s window, chain reset). After the shield is dropped (G in the grid), Q shows "Round Shield not in inventory" and changes nothing. |
| B8 | `fireboltCharge` / `radianceCharge` no longer appear anywhere in `prototype/`. The kit has no charges and spells have no counts. |
| B9 | Equipped items are not in the grid, so G cannot reach them. Only unequipped items drop. |
| B10 | The "expected 6 clips ... got 9" warning no longer logs. A real clip-count mismatch still warns. |

## Left undone / for later

- **Off-hand mount accuracy is untested in-game.** The sword in L_Hand and the
  shield in R_Hand use the measured mirror, but nobody has seen them. If either
  looks wrong, tune `equip.mirrorScale` or the item mount `rollDeg`. Both are
  CONFIG data.
- **No block or cast animation per hand.** The existing block and cast visuals
  play whichever hand holds the item.
- `cast.powerTier` is data only. Nothing scales from it until wands and staffs exist.
- Grid compaction after the boot auto-equip was not added.
