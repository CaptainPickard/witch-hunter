# Astrabot report - left-hand shield equip + Radiance (2026-10-04)

Brief: io/missions/2026-10-04-astrabot-equip-radiance-brief.md
Branch: feat/world-visuals (worktree /tmp/wh-worldfeat)

| Order | Commit | Summary |
|---|---|---|
| A | 17933b0 | feat(equip): left-hand implement system - Digit1-5 equip/stow, round shield on L_Hand |
| B | 1ecaf05 | feat(spell): Radiance follow-light on belt slot 2 (60s, survives stow/swap/death) |

Both pushed to origin/feat/world-visuals. Checks were static only: esprima parse
plus grep. Per the hard laws, no harness or browser was run.
Nicko's playtest is the acceptance test.

## AC evidence

| AC | Status | Evidence |
|---|---|---|
| AC1 boot fireball, 1 stows, 1 re-equips | PASS (static trace) | Constructor: `leftHand = {spell, belt[0]='firebolt'}`, offhand 'spell'. `setShield` -> `applyLeftHandVisual` hides the shield. Press 1: `pressBeltKey(0)`, mode spell and spellId === belt[0], so `stowToShield()` -> `setLeftHand('shield')` -> offhand 'shield', shield visible, regrip 0.3s. Press 1 again: mode shield, so `equipBeltSpell(0)` -> endBlock, `selectBeltSlot(0)`, `setLeftHand('spell','firebolt')`, shield hidden. |
| AC2 fireball held, press 2 = direct switch to radiance | PASS (static trace) | `pressBeltKey(1)`: spellId 'radiance' !== 'firebolt', so `equipBeltSpell(1)` -> one `setLeftHand('spell','radiance')`. No shield state in between. |
| AC3 shield: RMB blocks / spell: RMB casts | PASS | RMB routing is unchanged (`offhand==='spell'` -> tryCast, else tryBlock). `canCast` still needs offhand 'spell'. `tryBlock` now also refuses unless offhand === 'shield' and regrip has ended, so spells never block. |
| AC4 radiance follows, survives stow, expires with fade, recast refreshes, never stacks | PASS (static trace) | `castRadiance`: `game.radiances[0]` exists -> `refresh()` (timer = durationSeconds), else spawn + push. That is the only push, so the array holds at most 1. The effect group is a child of `player.yawFrame`. Nothing on the left-hand path (`setLeftHand`, stow, equip, Q) touches `game.radiances`. `update()` fades over the last fadeOutSeconds, then `park()`s. |
| AC5 persists through death/respawn | PASS (static trace) | The radiance tick in `loop()` is not gated on player state. `respawnAt` only moves `pos`, and yawFrame/root are never rebuilt, so the light rides along. |
| AC6 chain/armed untouched by 1-5 | PASS (code path) | `pressBeltKey` -> `equipBeltSpell`/`stowToShield` -> `endBlock`, `dropPendingCast`, `selectBeltSlot`, `setLeftHand`. None of these write comboIndex/comboQueued/chainHits/armedTimer/crossArmed or call cancelAttack, so a swing in progress plays out. |
| AC7 numbers in CONFIG | PASS | New engine lines contain only 0/1/2 identities, loadout ids 1/2 and deg/rad conversions. Every tunable is in CONFIG: `spell.radiance.*`, `belt.defaultSpells`, `assets.shieldMount`, `assets.weaponTargetHeight.roundShield`. |
| AC8 parse + no dangling refs | PASS | esprima parses all 11 `prototype/js/*.js`. No CONFIG keys were removed. The only removed code is the per-frame offhand derive, and offhand is now written by `setLeftHand`. |
| AC9 prepTemplate normal fallback | PASS | assets.js prepTemplate: if a mesh has `position` but no `normal`, it calls `computeVertexNormals()` before the material normalize. |
| AC10 shield measured scale | PASS | Measured disc height (GROUND_META Y extent) 2.0017. `weaponTargetHeight.roundShield = 1.0`, so `weaponScale` gives 0.4996. Recorded in a CONFIG comment and here. |

## Shield measurement (scratch/measure_shield.py)

- Raw extents: 1.995 x 2.0017 x 0.393. The front (boss) side is raw **+Z**:
  the centre-core mean z is +0.075 and the rim mean z is -0.063. Raw +Y is the disc "up".
- Scale: 1.0 / 2.0017 = **0.4996**. This follows the same pattern as the
  longsword (the target ignores the inherited body scale). The rig is 2.0 raw,
  normalised to 1.8 m, so the hand inherits 0.9 and the **world diameter is about 0.90 m**.
  To hit exactly 1.0 m in the world, set `weaponTargetHeight.roundShield` to 1.11.
- L_Hand basis at WH_Idle frame 0, in body space: hand +Z points forward,
  +Y points down along the fingers, and -X points outward (body-left).
- Mount target: the boss faces body-left turned **20 deg toward forward**,
  with the disc level. Converted to hand-local axes, that gives:
  - `faceAxis: [-0.876, 0.4, 0.271]`, `upAxis: [-0.327, -0.903, 0.277]`, `rollDeg: 0`
  - `offset: [-0.028, 0.099, 0.035]`. This is the fist centroid
    [0.018, 0.078, 0.021] pushed out along faceAxis by the fist depth (0.042)
    plus a 0.01 gap. setShield centres the disc on X/Y and puts the shield's
    back-most point on this spot.
  - The L_Thigh clears the shield back plane by 0.027 at idle.
- Stand-in body (no bones): the shield goes on yawFrame at the mirrored
  weapon idle anchor, which is the same spot as the spell glow, facing outward.

## Radiance defaults

These keys were changed from the brief:

- `lightIntensity` is **8.0** (brief: 2.2). With decay 2 and the orb 1.9 m up,
  2.2 lights less than the 6.5 hip lantern. 8.0 gives a ~6 m ground pool.
- New keys: `kind`, `lightDecay` 2, `schoolColor` (the HUD/glow code reads it
  for every spell), `orbSegments`, `anchorOffset`, `bobHz` 0.5, `fadeInSeconds` 0.4.
- **`anchorOffset` is [+0.45, 1.9, 0.1], not -0.45.** I measured that body-left
  is +X in yawFrame: L_Hand sits at x=+0.42, and the soles reach z +0.25
  forward vs -0.07 back. So "upper-left" means +X. As a side effect, the
  lantern's "left-hip" anchor at x=-0.32 is actually on the RIGHT hip. I left it alone.

## Deviations / notes

- **Expiry parks the light, it is not disposed.** Removing a PointLight
  changes the scene light count, and three.js then recompiles every lit
  material, which is a visible hitch. So after fade-out the orb is hidden and
  the light sits at intensity 0, and the next cast reuses the same effect.
  This keeps one dedicated light and never stacks. The first cast still adds
  the light, so there is one recompile at that moment (watch item).
- **activeLoadout follows the left hand.** Stowing (shield) sets loadout 2;
  equipping a spell sets loadout 1. This way Q always flips spell <-> shield,
  and the I/II pips match what is in hand. Q keeps its 0.8s window, chain
  reset and cross-arm banking. When Q lands on loadout 1 and the selected belt slot is empty, it gives the shield.
- A cast still in windup is dropped when the implement changes: no focus
  spent, no fizzle flash. This stops a firebolt firing out of the shield hand.
- The shield's guard comes up after the 0.3s regrip (`belt.regripSeconds`),
  the same as spell regrip.
- The leftHand state survives respawn (it is not reset on death).
- HUD: in shield mode, `#wh-belt.stowed` dims spell slots to 45%, removes
  the school tint, and shows a small 'S' over the spell/consumable divider. No layout changes.
- Debug: `WH_DEBUG.pressBeltKey(i)`, `getLeftHand()`, `getRadianceState()`.

## Watch items for playtest

1. Shield pose in walk/run/attack clips. The mount is hand-local and was
   measured at idle, so arm swing moves the shield. Tune with
   `shieldMount.rollDeg` or `faceAxis` / `offset`.
2. Thigh clearance at idle is only 0.027, so the shield may clip in a stride.
   The fix is to push `offset` further along faceAxis.
3. Shield size: 0.90 m in the world (see above).
4. One-frame hitch on the first Radiance cast (light count +1).
5. Radiance brightness: 8.0, tune `spell.radiance.lightIntensity`.

Nothing left undone. No sub-order was impossible.
