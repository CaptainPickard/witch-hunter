# ASTRABOT MISSION BRIEF - Inventory Order B (character screen + free per-hand equip + open button + magic-canon kit retrofit)
2026-10-05, from IO. Nicko's orders (10-04 clarifications + 10-05 magic canon + "Proceed with B now"):

1. Inventory screen CHARACTER tab is now REAL: shows currently equipped items,
   and you can equip/unequip items from inventory there.
2. FREE PER-HAND equip: the shield AND the longsword each equip to EITHER hand,
   one item per hand. RMB attack chain fires ONLY when a melee weapon (longsword)
   is in the RIGHT hand - shield in the right hand is just carried, no bash move.
3. On-screen open button: "I key, and UI button that can be pressed" - a clickable
   HUD button opens/closes the inventory screen (same as the I key).
4. MAGIC CANON (binding, 10-05): spells are KNOWLEDGE learned from books/scrolls;
   there are NO consumable spell charges; casting requires an equipped casting
   implement - magic glove < wand < staff (power tiers, wands/staffs come later).
   Belt keys 1-5 select WHICH learned spell is active (unchanged). Boot: knows
   firebolt + radiance, magic glove equipped in the LEFT hand (magic canon answer
   supersedes the older "shield at left boot" line - shield starts in INVENTORY).
   Books/scrolls (learn-on-read, destroyed on read) are a stage-2 item category -
   NOT this order; just don't build anything that contradicts them.

You are Astrabot, running as a Claude Code print-mode agent in the witch-hunter
repo worktree /tmp/wh-worldfeat (branch feat/world-visuals).
Report file, commits, and pushes as in previous missions (Order A precedent:
prototype/js/inventory.js, CONFIG.js, game.js, player.js, style.css all exist
and are live; Order A = commits 4bbb210..dbaf37a).

## 0. LAWS (hard)
- NO automated harness or headless-browser smoke runs of any kind - not even a
  quick chromium pass. Nicko's playtest is the ONLY acceptance test.
- One order at a time: this order only. Commit to feat/world-visuals and push
  after each sub-block (Astrabot commits, IO is the merge gate).
- Every tunable from CONFIG. No hardcoded gameplay numbers in code.
- NO new 3D assets, NO Meshy, NO Blender in this order (see 4c for the glove visual).
- Magic canon above is binding: do not re-introduce spell charges.
- Silence the assets.js once-per-boot warning "expected 6 clips, got 9"
  (combat-chain.glb legitimately holds 9) in this order's commits.

## 1. Current mechanics (from Order A + equip/radiance missions - verify exact
   line numbers as you go, they may have drifted a few lines)
- player.js: leftHand = { mode: 'spell'|'shield', spellId } state machine
  (10-04 mission); offhand derived property = leftHand.mode is read by game.js
  (cast path requires offhand==='spell', block path requires offhand==='shield');
  selectBeltSlot(i) on Digit1-5 (equip/stow + regrip 0.3s); Q loadout toggle
  (0.8s window, chain reset) at activeLoadout 1<->2; setInputSuspended(open)
  gates all input while the screen is open (Order A).
- game.js: setupInventory() boots WH_INVENTORY (Inventory + InventoryUI +
  WorldItems), dropFromSlot / tryPickup, WH_DEBUG hooks (getInventory, addItem,
  getWorldItems, isInventoryOpen); equipPlayerWeapon('longsword') + 
  equipPlayerShield() at boot: longsword R_Hand, roundShield L_Hand via
  CONFIG.assets mounts (weaponMount, shieldMount + weaponTargetHeight).
- inventory.js: WH_INVENTORY module (Inventory slots/stacks; InventoryUI modal
  with INVENTORY/CHARACTER tabs - character tab currently a "Coming soon"
  placeholder div; WorldItems ground entities; toast system).
- CONFIG.js: CFG.inventory (slots 24, defaultStackCap 60, startingItems, drop,
  entity), CFG.items registry (fireboltCharge, radianceCharge, bandage,
  longsword, roundShield with useHint/equipHint data), CFG.inventoryUI keys.
- spells.js / game.js cast path: WH_SPELLS.spawn on castWindup completion;
  spellGlow = left-hand emissive orb shown while offhand==='spell'.

## 2. B1 - HAND EQUIP MODEL (player.js core)
Replace the leftHand spell/shield state machine with a generic two-hand model:
- player.hands = { right: null, left: null }  // item id or null
- Items are single instances: equipping an item that is already in the other
  hand MOVES it (never duplicates). Equipping FROM the character screen pulls
  the item out of inventory (removeItem) and into the hand; unequipping puts
  it back into inventory (addItem; if inventory is FULL the unequip is
  REFUSED with a toast "Inventory full" and the item stays equipped).
- Derived capability flags (single source for all combat code):
  hasCaster()   = hand holds a casting implement (magicGlove now)
  hasShield()   = a hand holds roundShield
  hasMeleeRight() = right hand holds longsword
- RMB precedence (one handler, decided by Nicko's rulings):
  1) hasMeleeRight() -> attack chain (unchanged moveset)
  2) else hasCaster() -> cast active learned spell (works EITHER hand)
  3) else hasShield() -> hold-to-block (unchanged block path)
  4) else nothing. Note: cast wins over block when both equipped - if that
     feels wrong in playtest it becomes a CONFIG knob, default cast-first.
- Belt keys 1-5 (Digit1..5): select the active learned spell ONLY
  (belt = learned-spell quick slots, default ['firebolt','radiance',null,null,null];
  no learned spell in a slot = refusal flash as today). NO hand-state changes
  from belt keys anymore (the stow-to-shield behavior is SUPERSEDED - hands
  are equip-screen-driven now). Keeping selectedBeltSlot + regrip visuals is
  optional; if kept, regrip applies to nothing when no caster changes hands.
- Casting capability: castWindup only starts when hasCaster(); RMB with no
  caster and no shield does nothing. Blocking unchanged (requires shield and
  reaches the block path only under precedence rule 3).
- Q (loadout toggle): repurpose as LEFT-HAND SWAP between magicGlove and
  roundShield: left currently glove -> equip shield to left (must be in
  inventory, else refusal toast), left currently shield -> equip glove (same
  rule). Preserves the 0.8s toggle window + chain reset exactly. If the target
  item is not in inventory: refusal toast, nothing changes.
- Boot state (fresh spawn): longsword RIGHT, magicGlove LEFT, roundShield +
  bandage in INVENTORY (kit per B4). Firebolt learned + selected.
- Visuals: longsword + shield meshes mount via the EXISTING mount system but
  must now attach to EITHER hand (mount item -> hand bone R_Hand/L_Hand with
  per-item scale/targetHeight from CONFIG.assets). Unequip = detach + hide.
- Glove visual placeholder (NO new mesh this order): while a caster implement
  is equipped, show the existing spellGlow orb on THAT hand (school-colored,
  same idle-pose offset mirrored for right hand); hide when unequipped. The
  real glove/wand/staff meshes come in a later Astrabot asset mission.

## 3. B2 - CHARACTER TAB (character screen)
- Left panel: two equipment slots, RIGHT HAND and LEFT HAND, each showing the
  equipped item glyph+name (or "Empty"). Click an equipped slot = unequip to
  inventory (refused if full). 
- Right panel: INVENTORY GEAR list - scrollable list of gear items currently
  in the inventory (longsword, roundShield, magicGlove...), each row shows
  glyph + name + which hands it may enter (equipHint). Click a row = equip to
  the DEFAULT hand from its equipHint; small [L]/[R] buttons on the row equip
  to that specific hand (one instance rule applies: moving from the other
  hand is allowed).
- Also show SPELLS: learned spells list (firebolt, radiance) with the active
  one marked; click = set active spell (same as belt keys). Pure display +
  selection - no new spell logic.
- Screen styling = existing darkwood modal look (reuse .inv-panel classes).

## 4. B3 - OPEN BUTTON + B4 - KIT RETROFIT
- B3: small HUD button (bottom-left corner near the touch-button area or next
  to the hint bar - your call, darkwood style) labeled "INV" that toggles the
  inventory screen (same path as the I key: setOpen(!open)). Must work with
  mouse AND be a real button (the touch-controls path also uses it fine).
- B4 (kit retrofit per magic canon):
  * CONFIG.items: DELETE fireboltCharge + radianceCharge. ADD:
    magicGlove: { id:'magicGlove', name:'Magic Glove', glyph:'MG',
                  category:'gear', stackCap:1, equipHint:'leftHand',
                  cast: { powerTier: 1 } }   // glove=1 < wand=2 < staff=3
  * Add to longsword/roundShield defs: hands: ['right','left'] capability data
    (longsword: melee weapon; roundShield: block item; neither casts).
  * Starting kit: { magicGlove x1, longsword x1, roundShield x1, bandage x1 }
    - glove + longsword AUTO-EQUIP at boot (glove left, longsword right), so
    the inventory shows shield + bandage only.
  * WH_INVENTORY knows caster vs melee vs shield purely from CONFIG.items
    flags (category:'gear' + a kind field: 'caster' | 'melee' | 'shield').

## 5. ACCEPTANCE CRITERIA (Nicko playtests all of these)
| AC | Test |
|---|---|
| B1 | CHARACTER tab: RIGHT HAND = Longsword, LEFT HAND = Magic Glove; shield + bandage in the INVENTORY tab |
| B2 | Unequip longsword (click right-hand slot): hand empty, sword back in inventory grid; equip it to LEFT: carried, RMB does NOT chain; equip back to RIGHT: chain fires |
| B3 | Shield to RIGHT hand, glove unequipped: RMB hold blocks. Glove re-equipped (either hand): RMB casts firebolt; shield in other hand still carried |
| B4 | Same item never in both hands; the equip row's [L]/[R] moves it across hands |
| B5 | INV button toggles the screen (mouse click works; I key unchanged) |
| B6 | Belt keys: 1/2 switch active spell (HUD/tooltip confirms); with glove unequipped, RMB does nothing; re-equip glove -> cast works |
| B7 | Q swaps left-hand glove<->shield (0.8s window, chain reset); if shield was dropped it refuses with a toast |
| B8 | No fireboltCharge/radianceCharge anywhere; no spell charges canon visible |
| B9 | Drop a gear item while equipped = impossible (only unequipped items drop) |
| B10 | assets.js boot warning "expected 6 clips, got 9" no longer logs |

## 6. Tunables to expose in CONFIG
- CONFIG.inventoryUI.openButton = { enabled:true, label:'INV' } (+ css placement)
- CONFIG.equip = { defaultHands: { right:'longsword', left:'magicGlove' } }
- CONFIG.items[*].kind ('caster'|'melee'|'shield') + cast.powerTier
- Keep Order A keys untouched otherwise.

## 7. Report
Write scratch/astrabot_inventory_orderB_report.md (committed) with:
flows, exact code anchors changed, judgment calls (esp. RMB precedence + Q
semantics + glove visual), tunables list, AC notes. Final chat message: short
summary - commits with shas, AC table state, knobs, anything left undone.