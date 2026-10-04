# Astrabot report - Inventory Order C (dual-wield casting: two gloves, two bindings, two-button combat)

Brief: `io/missions/2026-10-05-astrabot-inventory-orderC-brief.md`
Branch: `feat/world-visuals` (worktree `/tmp/wh-worldfeat`). Nothing beyond Order C was started.

## Commits (all pushed)

| sha | step |
|---|---|
| 384aa97 | C1: per-hand cast state + two spell bindings (+ HUD belt off-binding marker) |
| 5c91f9e | C2: two-button combat (LMB main / RMB off), per-hand glow orbs, hand-anchored cast origin, touch routing |
| e07594c | C3: CHARACTER tab MAIN/OFF columns, glove #2 in the kit, equip-from-inventory fix |
| (final) | this report |

## Verification

- **No harness or browser runs** (per LAWS). Nicko's playtest is the only acceptance test.
- **Syntax:** every `prototype/js/*.js` parses with `esprima.parseScript` (Python, parse only).
- **Static review** of the full diff. A grep finds no remaining references to the removed
  fields: `castWindup`/`castCooldown` on the player, `regripTimer`, `pendingSpellId`,
  `selectedBeltSlot`, `getSelectedSpellId`, `secondaryAction`/`Down`/`Up`, `rmbOrder`,
  `offhandGlow` and `spellGlow`.

## FLAGGED CONSEQUENCES (please confirm in playtest)

1. **Blocking now works only with the shield in the LEFT hand.** A shield in the right hand
   is just carried: LMB does nothing with it, and there is no block until it goes back to
   the left hand. `tryBlock`, `handsChanged` and `update()` all check `hasShieldLeft()`.
   Moving the shield out of the left hand ends any held block on the same frame.
2. **There are no per-hand cast ANIMATION clips yet.** The only cast cue for each hand is
   its glow orb swelling over the windup (`casterGlow.windupScale`). Cast clips are
   deferred to a later Blender mission. No clips, assets, Meshy or Blender were used in
   this order.

## Flows

**Per-hand cast state** (`player.js`, section "Order C: per-hand cast state + bindings")
- `player.cast = { main, off }`. Each is `{ windup, spellId, cooldown, regrip }`.
  `main` is the right hand and `off` is the left hand.
- Every cast API takes a role (`'main'`/`'off'`) or a hand (`'right'`/`'left'`); `roleOf()` maps
  between the two. These are `canCast`, `tryCast`, `completeCast`, `castProgress`,
  `dropPendingCast` and `getBoundSpellId`.
- `canCast(role)` needs all of the following:
  - the player is alive, not rolling, not toggling and not guard-broken
  - the attack is in windup stage or there is no attack (weave rule unchanged)
  - **this** hand holds a caster
  - **this** hand's regrip, windup and cooldown are all at 0
  - `focus - focusReserved(role) >= cost`
- `tickCasts(dt)` (called from the game loop) runs both windups and returns 0-2 completed
  requests each frame. `completeCast(role)` spends focus and starts **that** hand's
  cooldown (`spell.castCooldown`).
- Fizzle: damage during a windup cancels every hand that is mid-windup. There is one
  fizzle flash and no focus is spent.
- Respawn resets both hands' cast state. The bindings persist, like the hands.

**Bindings**
- `player.bindings = { main: 0, off: 0 }` holds two pointers into the one `belt` list.
  At boot both point at slot 1 (firebolt).
- Digit1-5 calls `pressBeltKey(i, 'main')`. Shift+Digit1-5 calls `pressBeltKey(i, 'off')`.
- An empty slot gives the refusal flash, as before.
- Pressing the hand's current slot does nothing.
- A rebind drops only **that** hand's pending windup. If the hand holds a caster, it also
  starts that hand's 0.3s regrip.
- Shift is also sprint. Shift+Digit while running binds the off hand, which is intended.

**Two-button combat**: `player.handButton(button, down)` is THE single dispatch
- Mouse LMB/RMB down/up and the touch attack/block buttons all call it.
- `buttonHand(button)` reads `CONFIG.equip.twoHand`: `lmb` -> `mainHand` = right, `rmb` -> `offHand` = left.
- `handAction(hand)` decides what the button does from that hand's item `kind`:
  - right hand melee -> `tryAttack()` (input buffer, chain and roll-cancel are unchanged)
  - caster in that hand -> `tryCast(hand)`
  - left hand shield -> `tryBlock()`, hold to keep blocking
  - anything else -> nothing (a sword in the left hand, a shield in the right hand, or an empty hand)
- Release ends a block only if **that button** started it (`blockButton`). `endBlock()`
  clears it.
- LMB still starts the camera drag, as before.

**Glow orbs and cast origin** (`game.js`)
- `game.casterGlows = { right, left }`: one orb per hand. Order B's single orb was
  extended into a per-hand pair, not forked.
- `updateCasterGlows(p)`: with `casterGlow.perHand`, every hand holding a caster shows its
  own orb. Each orb is colored by that hand's binding's `schoolColor`, so firebolt is
  orange and radiance is amber.
- The orb is scaled by `1 + (windupScale - 1) * castProgress(hand)`.
- `anchorGlow` keeps the Order B bone mount: `handOffset`, mirrored for the hand that is
  not native. Each orb re-anchors only when the anchor mode or the body changes.
- `castOrigin(req)`: a bolt spawns at the **casting hand's orb** world position, so a
  right-glove cast leaves the right hand. Before the orb is anchored, it falls back to the
  old chest-height origin.
- Radiance ignores the origin, the same as before. It refreshes the single follow-light
  whichever hand cast it.

**Kit and CHARACTER tab**
- `CONFIG.inventory.startingItems` has a second `magicGlove`. Boot then fills the grid:
  glove, glove, longsword, shield, bandage.
- `equipDefaultHands` then removes the sword and one glove, taking from the end of the
  grid. The grid is left with **glove #2, Round Shield and Bandage**. `defaultHands` is
  unchanged: longsword in the right hand, glove in the left.
- The SPELLS section has two columns, **MAIN (R)** and **OFF (L)**. Each column shows:
  - the bound spell: glyph tile, name and "slot N"
  - a red "no implement" note when that hand holds no caster
  - the learned spells, keyed `1`/`2` for main and `S1`/`S2` for off. Clicking one calls
    `bindSpell(slot, role)`, the same path as the keys. The bound spell is highlighted.
- HUD belt: the main binding keeps the solid school-color border. The off binding gets a
  dashed outline in its school color and an `L` badge.

## JUDGMENT CALLS

1. **Shape of the per-hand state:** `cast.{main,off} = { windup, spellId, cooldown, regrip }`.
   Regrip is per hand too. Rebinding the off hand never locks out the main hand, which
   matches "fully independent".
2. **Shared focus is reserved at the press.** The old code checked focus at the press and
   spent it on completion. With two hands, both windups could pass the check on one cast's
   worth of focus. A second press now has to fit beside what the other hand has already
   promised. The starved hand refuses with the flash while the other cast completes (C6).
   Both hands can still fire in the same frame when there is enough focus.
3. **The duplicate-glove equip bug, fixed.** Order B's `equipItem(id, hand)` moves the item
   out of the other hand when that hand holds the same id. So "equip glove #2 to the right
   hand" would have **moved the left glove** to the right, and glove #2 would have stayed
   in the grid. CHARACTER-tab gear rows now pass `fromInventory = true`. The hand-row `[L]`/`[R]` move
   buttons still move the held item. A plain click on a glove row goes to the free hand
   when the default hand already holds a glove, so the click is not a no-op swap.
4. **Touch:** the attack button calls `handButton('lmb')` and the block button calls
   `handButton('rmb')`, both on press and on release. The block button label is now
   "Off Hand", because it casts with a left glove and blocks with a left shield.
5. **Casting while blocking** (right glove plus left shield) is allowed, because nothing
   in the brief forbids it. This is the same weave rule as before: casting never checks
   `blocking`. Block and parry are the next order, so this can be revisited there.
6. **Spell names and glyphs** are CONFIG data (`spell.*.name` / `glyph`: Firebolt FB,
   Radiance RD). Order B capitalized the id instead.
7. **Removed:** `CONFIG.equip.rmbOrder` (replaced by `twoHand`),
   `secondaryAction`/`secondaryDown`/`secondaryUp`, `getSelectedSpellId`, `selectedBeltSlot`,
   the `onSpellSelected` glow-color handler (the orbs are recolored every frame) and
   `player.offhandGlow` (replaced by `player.casterGlows`).

## Tunables (all CONFIG)

| key | default | what |
|---|---|---|
| `equip.twoHand` | `{ lmb: 'mainHand', rmb: 'offHand' }` | button -> hand. The value IS the behavior; swap it to remap |
| `equip.casterGlow.perHand` | `true` | one orb on each caster hand (false = one orb, left first) |
| `equip.casterGlow.windupScale` | `1.8` | orb size at the end of a windup (per-hand cast cue) |
| `equip.casterGlow.anchor` / `handOffset` | `'hand'` / measured | unchanged from Order B |
| `inventory.startingItems` | glove x2, longsword, shield, bandage | glove #2 = dual-cast kit |
| `spell.*.castCooldown` / `castWindup` / `focusCost` | unchanged | now per hand |
| `spell.*.name` / `glyph` | Firebolt FB / Radiance RD | CHARACTER tab columns |
| `belt.regripSeconds` | 0.3 | now per hand |
| `player.castFocusTaxMult` | 1.25 | unchanged, applies to each hand's cast |

## WH_DEBUG (playtest support, no harness)

- `getHands()` adds `shieldLeft`, plus `lmb` / `rmb` = what each button does now (`'attack'|'cast'|'block'|null`).
- `getBindings()` returns `{ main: { slot, spell }, off: { slot, spell } }`.
- `getCastState()` returns `{ main: {windup, spellId, cooldown, regrip}, off: {...}, focus, toggling }`.
- `bindSpell(slot, role)`, `tryCast(role)` and `handButton('lmb'|'rmb', down)` are new.
- `selectBeltSlot(i, role)` and `pressBeltKey(i, role)` now take a role.
- `equipItem(id, hand, fromInventory)`.

## AC notes (static reading; Nicko's playtest decides)

| AC | expected by the code |
|---|---|
| C1 | Boot: sword in the right hand, glove in the left; the grid shows glove #2, shield and bandage |
| C2 | LMB swings the chain. With the sword stored, the right hand is empty, so LMB does nothing. Equip glove #2 in the right hand and LMB casts from the right orb. Storing the sword alone does not put a glove in the right hand: a right-hand implement is required by ruling 2 |
| C3 | RMB casts the off binding from the left orb. Sword right + glove left: LMB swings and RMB casts |
| C4 | Two gloves give two orbs. Main firebolt + off radiance gives an orange right orb and an amber left orb |
| C5 | Digit changes only the main binding and Shift+Digit only the off binding. The tab columns and the belt markers follow, and clicking under a column rebinds that hand |
| C6 | The windups are independent. Focus is reserved at the press, so a starved hand flashes while the other casts |
| C7 | Shield in the left hand: RMB blocks. Glove in the right hand: LMB casts. Shield in the right hand: LMB does nothing and there is no block anywhere |
| C8 | Q is unchanged and touches only the left hand (`equipItem(..., 'left', true)`). It still shows the refusal toast when the incoming item is not in the grid |
| C9 | Radiance from either hand goes through `castRadiance`, which keeps a single follow-light; a recast resets it |
| C10 | Each hand has its own cooldown, so staggered casts do not share one |

## Left undone / for later

- Per-hand cast animation clips (Blender mission).
- Shield animation and block/parry rework (next order).
- Combined two-hand spells: not pre-built, per ruling 3.
- Known, unchanged from Order B: a windup already running when Q is pressed can still fire
  during the 0.8s window. It is dropped only when the glove actually leaves the hand.
