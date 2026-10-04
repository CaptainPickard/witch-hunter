# Astrabot report - Light radius order (earned light)
2026-10-05. Branch feat/world-visuals. Brief:
io/missions/2026-10-05-astrabot-light-radius-order-brief.md

No harness / headless runs (law 0). The only check run was an esprima syntax
parse of the edited JS files. Nicko's playtest is the acceptance test.

## Commits
- 53e991f L1 - delete the R2 player lantern; WH_PlayerLight manager (js/light.js)
- bed48fe L2 - firebolt binding light + in-flight projectile light (CONFIG)
- (this commit) L3 - item light stat precedence + dormant torch example + this report

## Flows
- **Boot**: `setupLights()` (game.js) builds hemi + moon + the world light pool
  as before, and now `game.playerLight = new WH_PlayerLight.PlayerLight(scene)`.
  That creates 2 hand PointLights + `CONFIG.playerLight.projectilePoolSize` (2)
  projectile PointLights, all at intensity 0, before the first render. The
  scene light count never changes after that (M-19: a light-count change
  recompiles every lit material). It's the same reasoning as RadianceEffect.park().
- **Per frame** (`loop`, where `lanternTick()` used to be):
  `game.playerLight.update(game.player, game.firebolts)`.
  - For each hand: `handLightDef(player, hand)` =
    1. `CONFIG.items[heldId].light` if present (item wins, L3)
    2. else, if the held item is `kind: 'caster'`, `CONFIG.spell[boundSpell].light`
       (the binding comes from `player.getBoundSpellId(hand)`, live)
    3. else null, and the light goes to intensity 0.
  - If the hand has a light, the light gets anchored to the hand, then color /
    distance / decay come from the block, plus flickered intensity.
  - Projectile lights: the n-th live bolt whose `config.projectileLight` is
    set gets pool light n, positioned at `bolt.pos`. Unused pool lights go to 0.
    A bolt that dies drops out of `game.firebolts`, so its light goes out
    in the same frame.
- **Binding / equip changes**: these need no event hooks. pressBeltKey, the
  CHARACTER tab rebind, equip/unequip and the Q swap all mutate
  `player.bindings` / `player.hands`. The next `update()` runs before that
  frame's render and reads both. That is the same per-frame read that
  `updateCasterGlows` uses to recolor the orbs.
- **Radiance**: untouched. `game.radiances` and RadianceEffect still own their
  own light. `spell.radiance.light = null` only means "no per-hand binding light".

## Anchors
- Hand light = **the same anchor as the per-hand glow orb**: the hand bone
  (`L_Hand` / `R_Hand`) at `CONFIG.equip.casterGlow.handOffset`, mirrored for
  the non-native hand. If the body has no bones (rigid stand-in), it falls
  back to the yawFrame idle pose.
- I moved the anchor code from game.js `anchorGlow()` into
  `WH_PlayerLight.anchorToHand()`. `updateCasterGlows` now calls it, so the
  orb and the light cannot drift apart. The orb's behavior is unchanged
  (same math, same re-anchor-on-body-change cache).
- The lights stay parented at the hand while off (intensity 0). They are never
  hidden or removed, so the light count stays fixed.

## Judgment calls
1. **Where PlayerLight lives**: a new file, `prototype/js/light.js`.
   index.html loads it after inventory.js and before player.js. player.js
   stays combat/state only, and light.js only reads player state
   (`hands`, `getBoundSpellId`, `body`, `yawFrame`).
2. **How flicker attaches**: it uses the old lantern's two-sine formula
   unchanged, `base * (1 + (0.6 sin 7.3t + 0.4 sin(3.1t+1.7)) * pct/100)`.
   It runs per light with a per-light phase offset
   (`CONFIG.playerLight.flickerPhaseStep`), so two gloves don't pulse in
   lockstep. The pct comes from each light block's `flickerPct`.
3. **Projectile light = a pool, not a new PointLight per bolt.** A literal
   per-bolt light would recompile shaders on every cast and again on every
   bolt death, which hitches badly on SwiftShader. The pool has 2 lights
   (CONFIG). Bolts beyond 2 in flight go unlit, but they still feed the
   existing world-pool firebolt socket, which is unchanged.
   Light budget: before = lantern (1). Now = 2 hand + 2 projectile (4),
   so +3 point lights. Watch FPS. If it costs too much, set
   `projectilePoolSize` to 1 (or 0).
4. **Firebolt hand light values differ from the brief's example
   (5.5 / d10)**. The brief asked me to match the old lantern's brightness.
   See the brightness section.
5. The windup creates no new light (L9). The hand light depends only on the
   binding. Cast state is never read, so only the orb swells.

## Brightness match (old lantern vs firebolt hand light)
| | color | linear luminance of color | intensity | luminous product | distance | decay | anchor |
|---|---|---|---|---|---|---|---|
| R2 lantern (deleted) | 0xffb060 | 0.531 | 6.5 | 3.45 | 12 | 2 | left hip, y 0.95 |
| firebolt light (new) | 0xff7722 | 0.345 | **10.0** | 3.45 | 12 | 2 | glove hand bone (hand height, rides the animation) |
| brief example | 0xff7722 | 0.345 | 5.5 | 1.90 (55%) | 10 | 2 | |

(Luminance = Rec.709 weights on the sRGB->linear converted color. three
r152+ treats hex colors as sRGB.) At 5.5 / d10 the forest would read about
half as bright as before and the pool would end 2 m sooner. That fails
"CLOSE to before", so I picked 10.0 / d12. It has the same total output,
but the color is more saturated orange, so the ground looks redder than the
old amber. If it reads too hot or too red, lower
`spell.firebolt.light.intensity`, or move `color` toward 0xff9040.
Two firebolt gloves = 2 x 10.0, which adds up as the brief allows (L5).

## Tunables (all CONFIG)
- `CONFIG.playerLight.flickerPhaseStep` (2.3 rad), `.projectilePoolSize` (2)
- `CONFIG.spell.firebolt.light` = { color 0xff7722, intensity 10.0, distance 12, decay 2, flickerPct 5 }
- `CONFIG.spell.firebolt.projectileLight` = { color 0xff7722, intensity 2.5, distance 6, decay 2, flickerPct 8 }
- `CONFIG.spell.radiance.light` = null
- `CONFIG.items[id].light`: the item light-stat shape. There's a dormant,
  commented-out `torch` example in CONFIG.items.
- Anchor: `CONFIG.equip.casterGlow.handOffset` / `.anchor` (shared with the orbs)
- Removed: `CONFIG.lighting.lanternColor/Intensity/Distance/Decay/FlickerPct/Anchor/AnchorOffset`

## AC notes (for Nicko's playtest)
| AC | Expectation / note |
|---|---|
| L1 | Boot, sword right, glove left, firebolt bound: warm orange pool from the left hand. Same output as the old lantern but more orange, and it moves with the hand rather than the hip |
| L2 | Unequip the glove: both hand lights at 0, moonlight only. Braziers / lantern posts / flame cards are untouched (world pool) |
| L3 | Re-equip the glove: the next frame reads the hand + binding, light back |
| L4 | Shift+2 / CHARACTER tab radiance on the glove hand: light 0 and the orb recolors in the same frame. The Radiance cast path is unchanged |
| L5 | Both gloves on firebolt: two lights, phase-offset flicker, brightness adds |
| L6 | The bolt carries pooled light #1 (2.5, d6) along its path. With 2 hands firing quickly, a 3rd bolt in flight would be unlit (pool 2) |
| L7 | Q swaps glove <-> shield. The shield has no light and isn't a caster, so the light goes out, and comes back on swap back |
| L8 | No lantern keys left in CONFIG.js (`grep lantern[A-Z]` = only the world assets lanternPost/lanternWaymarker). `game.lantern`, `attachPlayerLantern` and `lanternTick` are gone |
| L9 | The windup never touches the lights. Only the orb swells |

## Left undone / notes
- The torch item itself is stage 2, as ordered. To activate the example
  you'd need a hand `kind` plus a source (kit / drop).
- The stale old R2 validation tests (`tests/wh_world_r2_validation.py`,
  `tests/r2parts/part06.py`) still reference the `lantern*` CONFIG keys.
  I didn't touch or run them (law 0). They will report the lantern
  as missing if anyone runs them again.
- Block mechanics untouched. No assets, no Meshy, no Blender.
