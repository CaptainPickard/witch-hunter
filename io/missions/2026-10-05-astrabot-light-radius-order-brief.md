# ASTRABOT MISSION BRIEF - Light radius order (earned light: spell light follows bindings, item light stat, player lantern deleted)
2026-10-05, from IO. Nicko's orders (10-05 post-Order-C session):
- "the light coming from the player was because of the equipped fireball. But only
  after unequipping the magic glove did I realize that the light was on the player
  themselves. Lets change this so that some spells have a light radius, which
  fireball absolutely should. The player should have no natural light radius
  unless there is a reason for it, equipped torch, magic spells that would give
  off light, or magic items that have a light radius stat."
- Order C (dual-wield) is LIVE (384aa97..fcd5b06) and playtested OK on the
  off-hand visuals. This order builds directly on the per-hand bindings.

You are Astrabot, running as a Claude Code print-mode agent in the witch-hunter
repo worktree /tmp/wh-worldfeat (branch feat/world-visuals).
Report file, commits, pushes as in Orders A/B/C.

## 0. LAWS (hard)
- NO automated harness or headless-browser runs of any kind. Nicko's playtest is
  the ONLY acceptance test.
- One order at a time: this order only. Commit+push per sub-block.
- Every tunable from CONFIG.
- NO new 3D assets, NO Meshy, NO Blender.
- Shield animation + block/parry is the NEXT order - touch nothing in block
  mechanics.
- Magic canon unchanged: spells are learned knowledge, no charges.

## 1. NICKO'S RULINGS (10-05, binding)
1. Light is EARNED - the player has NO intrinsic light. Sources: a gloved hand's
   CURRENT BINDING (firebolt emits; radiance binding emits nothing per-hand but
   keeps its own follow-light when cast), an equipped item's light stat
   (mechanism this order, torch ITEM in stage 2), and Radiance cast lights
   (unchanged, separate system).
2. Firebolt light follows the BINDING: light exists while a gloved hand's current
   binding is firebolt; switch that hand's binding to radiance and the per-hand
   firebolt light goes away (Radiance's follow-light is a different mechanism).
3. The built-in player lantern (R2 night rig, game.js) is DELETED - intensity
   0, not a faint ember. No glove + no firebolt binding + no torch = genuinely
   dark, moonlight only.
4. Build the item light-stat mechanism NOW: CONFIG.items[*].light =
   { color, intensity, distance, decay, flickerPct }. The torch item itself lands
   with stage 2 (drops/gatherables), NOT this order.

## 2. Current mechanics (verified live end of Order C; re-check line numbers)
- game.js setupLights (~132-170): game.lantern = PointLight(0xffb060, 6.5,
  12, decay 2) created at boot, attachPlayerLantern() re-parents it into
  player.yawFrame (left-hip anchor CONFIG.playerLantern.lanternAnchorOffset),
  lantern flicker (~1297) wobbles ±lanternFlickerPct each frame. CONFIG keys:
  playerLantern.lanternColor/Intensity/Distance/Decay/FlickerPct.
- Order C per-hand cast state (player.js): cast.main/cast.off with windup
  timers, bindings.main/off = belt slot indexes (pressBeltKey(i, role)), per-hand
  cooldowns, focus reserved at cast start. spellGlow: per-hand orbs
  (CONFIG.equip.casterGlow.perHand = true) anchored to each gloved hand's bone,
  school-colored by that hand's binding.
- spells.js: WH_SPELLS registry; Firebolt class (CONFIG.spell.firebolt =
  focusCost 8, damage 12, speed 40...). Radiance cast in game.js manages
  game.radiances[] follow-lights (60s, fade-off, recast resets, never stacks).
- CONFIG.items: magicGlove (kind 'caster', cast.powerTier 1), longsword
  (melee), roundShield (shield), bandage (consumable). CONFIG.spell.firebolt /
  .radiance definitions.

## 3. WORK ORDER L1 - delete the player lantern
- Remove: lantern creation in setupLights, attachPlayerLantern() + its call,
  the lantern flicker update, CONFIG.playerLantern keys (delete the block).
- REPLACE WITH: a small PlayerLight manager (player.js or a new light.js file
  included before player.js in index.html - your call, report it) that maintains
  AT MOST TWO follow PointLights (one per hand) + does not touch game.radiances.
- Moon rig, region lights (graveyard braziers etc), fireplace/flame-card pool
  (R2 P1-8) are ALL untouched - they are world lights, not player light.

## 4. WORK ORDER L2 - spell light (per-hand, binding-following)
- CONFIG.spell.firebolt gains: light = { color 0xff7722, intensity 5.5,
  distance 10, decay 2, flickerPct 5 } (defaults tuned to approximate today's
  look when one glove is out - your job to eyeball-match the old lantern
  brightness from the code values; keep them CONFIG).
- CONFIG.spell.radiance gains light = null (radiance emits NO per-hand light;
  its cast follow-light already exists and is unchanged).
- Behavior: for each hand with a gloved implement equipped AND that hand's
  binding pointed at a spell with light != null -> that hand's follow PointLight
  is on (color/intensity/distance/decay/flicker from the SPELL's light block),
  parented to that hand's bone (same anchor as the per-hand spellGlow orbs).
- Light follows binding changes live: pressBeltKey / CHARACTER tab rebind
  updates the hand's light in the same frame the binding changes (same code
  path that recolors/relabels the orbs).
- Unequip a glove -> that hand's light dies instantly. Equip glove -> light
  returns if the binding is a light spell.
- Two gloves both bound to firebolt = two lights (one per hand). If both are
  on, brightness adds naturally (two PointLights) - no special dedup.
- Cast projectile: give the Firebolt PROJECTILE its own small light so the
  shot glows in flight (CONFIG.spell.firebolt.projectileLight, small - e.g.
  intensity 2.5, distance 6; killed with the projectile). Radiance projectile
  already glows via its cast system - leave it.
- No player shadow-casting changes (shadowMapEnabled stays false).

## 5. WORK ORDER L3 - item light stat (mechanism only)
- CONFIG.items[*] may carry light = { color, intensity, distance, decay,
  flickerPct }. PlayerLight also polls EQUIPPED items: any equipped item with
  a light stat spawns/updates that hand's light with the ITEM's values instead
  of spell-derived values. Precedence when both could apply: item light wins
  over spell binding light on the SAME hand (an item that literally emits light
  is doing so regardless of spell choice); different hands are independent.
- The mechanism must be data-driven and inert until stage 2 ships a torch item
  (no CONFIG.entries with light today except via spells). Add ONE harmless
  dormant example entry (a commented-out torch item in CONFIG.items with its
  light block) so the shape is documented in-file.
- Flicker: same flicker math as the old lantern (±pct of intensity), applied
  per-light.

## 6. ACCEPTANCE CRITERIA (Nicko playtests all of these)
| AC | Test |
|---|---|
| L1 | Boot (sword right, glove left, firebolt bound): night forest looks CLOSE to before - warm light around the player |
| L2 | Unequip the glove: player area goes MOONLIGHT-ONLY dark - no warm glow at the player, braziers/flame props still light the world |
| L3 | Re-equip glove with firebolt bound: light back, tinted fire-orange |
| L4 | Rebind the gloved hand to radiance (Shift+2 or CHARACTER tab): per-hand warm light goes away; glow orb recolors; casting radiance STILL spawns its 60s follow-light normally |
| L5 | Two gloves both bound to firebolt: two warm lights, brightness adds |
| L6 | Cast firebolt: the projectile visibly glows along its flight path |
| L7 | Q swap glove<->shield in the left hand: light dies with the glove, returns on swap back |
| L8 | No boot errors; the old lantern CONFIG keys are gone from CONFIG.js |
| L9 | Firebolt windup: no NEW light beyond the orb swell (light is binding-persistent, not cast-only) |

## 7. Report
scratch/astrabot_light_radius_order_report.md (committed): flows, anchors,
judgment calls (esp. where PlayerLight lives + how flicker attaches),
tunables list, AC notes, brightness-match notes (old lantern vs new firebolt
light). Final chat message: commits with shas, AC table, knobs, anything left
undone.