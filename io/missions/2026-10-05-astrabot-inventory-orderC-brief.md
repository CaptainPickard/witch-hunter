# ASTRABOT MISSION BRIEF - Inventory Order C (dual-wield casting: two gloves, two bindings, two-button combat)
2026-10-05, from IO. Nicko's orders (10-05 post-Order-B playtest report):
- "magic glove should be both [hands], dual wielding magic gloves should be possible,
  allowing you to have two spells active at once. Turning the 'block/cast' button
  into the off hand attack button."
- OFF-HAND LOOK CONFIRMED GOOD in playtest (sword left / shield right mounts pass).

You are Astrabot, running as a Claude Code print-mode agent in the witch-hunter
repo worktree /tmp/wh-worldfeat (branch feat/world-visuals).
Report file, commits, pushes as in Orders A/B. Order B = commits 9caa786..a8b1a0d
(hands model, CHARACTER tab, INV button, glove kit are LIVE and work).

## 0. LAWS (hard)
- NO automated harness or headless-browser runs of any kind. Nicko's playtest is
  the ONLY acceptance test.
- One order at a time: this order only. Commit+push per sub-block.
- Every tunable from CONFIG. Magic canon binding: spells = learned knowledge, no
  consumable charges; a hand casts only if it holds a casting implement
  (glove tier 1 now).
- NO new 3D assets, NO Meshy, NO Blender. No new animation clips this order
  (per-hand cast animation polish comes later - see report note).
- shield animation + block/parry = the NEXT order, NOT this one. Do not touch
  block mechanics beyond what C requires (RMB routing below).

## 1. NICKO'S RULINGS (10-05, binding)
1. Belt: TWO bindings over ONE belt list. Digit1-5 selects the MAIN (right) hand's
   spell (unchanged behavior). Shift+Digit1-5 selects the OFF (left) hand's spell.
   CHARACTER tab shows both bindings.
2. Buttons: LMB = MAIN-hand action (longsword chain if longsword is in the RIGHT
   hand; else cast MAIN binding if an implement is in the RIGHT hand; else nothing).
   RMB = OFF-hand action (cast OFF binding if an implement in the LEFT hand; else
   hold-to-block if roundShield in the LEFT hand; else nothing).
   CONSEQUENCE to note in report: blocking now ONLY works with shield in the LEFT
   hand. Shield in the right hand = carried only (consistent with Nicko's earlier
   "shield in right hand is just carried").
3. Casts fully independent: per-hand windup/cooldown state, both hands can be
   mid-cast at once. Focus pool is shared - each cast costs its spell's focus and
   both can fire in the same frame if focus allows. Future combined-cast spells
   may layer on later; do not pre-build.
4. Kit: TWO magicGloves at boot - ONE auto-equips LEFT (defaultHands unchanged:
   longsword RIGHT, magicGlove LEFT), the SECOND sits in the inventory. Dual-cast
   is demoable by storing the sword and equipping glove#2 to the right hand.

## 2. Current mechanics (verified live end of Order B; re-check line numbers)
- player.js: this.hands = { right, left } (item ids), single-instance equip via
  CHARACTER tab + Q swap (equip.qSwap = ['magicGlove','roundShield'],
  0.8s window, chain reset). Capability helpers: hasCaster()/hasShield()/
  hasMeleeRight()/handOf(id). RMB today = single precedence chain melee>cast>block
  (equip.rmbOrder array) with ONE shared castWindup state + castCooldown.
- player.js keys: selectBeltSlot(i) on Digit1-5 sets selectedBeltSlot (the ONE
  active spell). offhand glow = spellGlow orb anchored to the hand bone via
  CONFIG.equip.casterGlow (anchor:'bone' default).
- game.js: RMB mouse handler routes press/release to player (tryAttack/tryBlock/
  tryCast via action map); castWindup ticked in game loop, completes ->
  WH_SPELLS.spawn(scene, spellId, origin, dirX, dirZ). LMB handler = tryAttack +
  camera drag start. touch-controls.js: attack button + block button route the
  same player methods; cam joystick separate.
- CONFIG.equip = { defaultHands, rmbOrder, qSwap, nativeHand, mirrorScale,
  casterGlow }; CONFIG.inventoryUI.openButton live; CONFIG.items[*].kind
  ('caster'|'melee'|'shield'), hands array, equipmentHint, cast.powerTier.

## 3. WORK ORDER C1 - two-hand cast state
- Replace the single castWindup/castCooldown with per-hand cast state:
  player.cast = { main: {spellId, t, phase}, off: {spellId, t, phase} } or a
  small per-hand structure of your choosing - but BOTH hands must be able to be
  mid-windup simultaneously and complete independently.
- Bindings: player.bindings = { main: <beltSlotIndex>, off: <beltSlotIndex> };
  boot defaults both 0 (firebolt). Digit1-5 sets bindings.main;
  Shift+Digit1-5 sets bindings.off (new key paths; keep refusal flash for empty
  belt slots - a learned spell must sit in that belt slot; CONFIG.belt defaults
  ['firebolt','radiance',null,null,null] unchanged).
- The belt slot LIST stays the single source of which spells exist; bindings are
  just two pointers into it. Spell->binding is data, not a new selection system.
- Focus gate per cast: casting hand H fails with the existing refusal flash when
  focus < spell.focusCost. No focus changes.
- Cooldown per hand: after a hand completes a cast, THAT hand's next cast waits
  spell.castCooldown (per-spell value unchanged). Two hands can cast the same
  spell simultaneously and then both independently cool down.

## 4. WORK ORDER C2 - two-button combat (LMB main / RMB off)
- LMB (press): main-hand action in priority order:
  1) hands.right is longsword (kind 'melee') -> existing attack chain path
     (input buffer, chain, roll-cancel rules ALL unchanged)
  2) else hands.right kind 'caster' -> start MAIN-hand cast (C1 state) using
     bindings.main
  3) else nothing (shield in right / empty = inert)
- RMB (press): off-hand action in priority order:
  1) hands.left kind 'caster' -> start OFF-hand cast using bindings.off
  2) else hands.left kind 'shield' -> hold-to-block (existing block path,
     press/hold/release semantics unchanged; block still requires the shield)
  3) else nothing (sword in left / empty = inert)
- Delete/replace the old single-rmbOrder precedence logic; keep the ability to
  endBlock() on any state transition that takes the shield out of the left hand.
- Cast origin and visual: spawn from the CASTING hand's glow anchor (the bone
  mount from Order B). Right-glove casts fire right-hand-side, left-glove casts
  left-hand-side. spellGlow: BOTH hands may glow at once when two implements are
  equipped - give each hand its own orb instance keyed by hand + schoolColor of
  that hand's binding. (Order B has a single orb: extend, don't fork.)
- Cast windup feedback: reuse the existing windup visuals per hand as far as the
  current rig allows (glow pulse/scale); note in report that per-hand cast
  ANIMATION clips are deferred to a later Blender mission.
- Touch: route the touch attack button -> LMB action path, touch block button ->
  RMB action path (block button behaves as block when shield left, cast when
  caster left). One shared dispatch function both mouse and touch call.

## 5. WORK ORDER C3 - CHARACTER tab + kit + CONFIG
- CHARACTER tab spells section: two columns MAIN(R) and OFF(L), showing the
  bound spell per hand (glyph + name), click a spell under a column to bind it
  to that hand (same rules as belt keys). Show the belt slot index (1-5) each
  binding points at.
- Kit: CONFIG.inventory.startingItems gains a second { id:'magicGlove', count:1 }
  entry (gear, separate slot). defaultHands UNCHANGED (longsword right, glove
  left). Inventory at boot shows: magicGlove#2, roundShield, bandage.
- CONFIG additions:
  * CONFIG.equip.twoHand = { lmb: 'mainHand', rmb: 'offHand' } (documented;
    the value IS the behavior, knob exists for later remapping)
  * CONFIG.equip.casterGlow.perHand = true
  * Keep rmbOrder key REMOVED (superseded) - report notes the deletion.
- WH_DEBUG: add getHands(), getBindings(), and extend the existing hooks so
  playtest support stays possible without new harness runs.

## 6. ACCEPTANCE CRITERIA (Nicko playtests all of these)
| AC | Test |
|---|---|
| C1 | Boot: sword RIGHT, glove LEFT; inventory grid holds glove#2 + shield + bandage (3 items) |
| C2 | LMB swings the sword chain (unchanged). Store sword, LMB now casts firebolt from the RIGHT glove position |
| C3 | RMB casts the OFF binding from the LEFT glove; with sword back in right hand: LMB sword + RMB left-glove cast both work (battle-mage loadout) |
| C4 | Equip glove#2 into RIGHT hand: LMB casts main binding (right glove), RMB casts off binding (left glove) - both firebolt = two orbs; main+off firebolt+radiance shows a firebolt orb AND an amber radiance orb glow on respective hands |
| C5 | Digit1/2 changes ONLY the right-hand binding; Shift+Digit1/2 changes ONLY the left. CHARACTER tab MAIN(OFF) columns update and clicking a spell under a column rebinds that hand |
| C6 | Fire both hands back-to-back: both windups run simultaneously; each finishes on its own; focus drains by both spells' costs; focus-starved hand refuses (flash) while the other still casts |
| C7 | Shield to LEFT hand (glove stored): RMB holds block. Glove RIGHT: LMB casts. Shield RIGHT: inert on LMB, and NO block exists until it returns to the left hand |
| C8 | Q still swaps LEFT hand glove<->shield with the 0.8s window + refusal toast when the shield was dropped. Right hand never changes from Q |
| C9 | Radiance from either hand: orb + follow-light behaves as before (60s, recast resets, never stacks) regardless of which glove cast it |
| C10 | Cooldowns: after casting firebolt from BOTH hands, each gloved hand re-casts independently (staggered casts do not share a cooldown) |

## 7. Report
scratch/astrabot_inventory_orderC_report.md (committed): flows, anchors changed,
judgment calls (per-hand state shape, glow per hand, touch routing), tunables,
AC notes, and the two flagged consequences (shield-in-left-only blocking;
per-hand cast anim clips deferred). Final chat message: commits with shas, AC
table state, knobs, anything left undone.