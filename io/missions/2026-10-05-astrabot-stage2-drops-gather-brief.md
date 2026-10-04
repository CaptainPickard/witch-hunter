# ASTRABOT MISSION BRIEF - Stage 2 order: enemy drops + world gathering (+ torch hand wiring)
2026-10-05, from IO. Nicko's rulings (10-05 design round, form-confirmed):
1. Drops: SHARED pool, both enemy types, exactly the same things. GUARANTEED
   1x Stolen Coin per kill + 20% bonus roll: torch (most common), bandage,
   RARE second magic glove. Cooking ingredients NEVER come from enemies.
2. Cooking items: ONLY from herbalism gathering nodes + wild animals (wild
   animals are a LATER stage; the item types exist now for when they land).
3. Gathering: STATIC interactable nodes in region CONFIG with a faint glow
   marker. Forest (A): herb bundles, deadwood, mushrooms. Graveyard (B):
   grave moss, bone piles. E harvests in radius; node dormants; respawns.
4. Respawn economy (REAL-GAME spec, build the MODEL now with seconds-scale
   override): common items respawn EVERY REAL DAY at RANDOM locations drawn
   from per-node-type placement pools (reshuffled); rares respawn every REAL
   WEEK regardless of in-game time. For playtest NOW, timers run in seconds
   (CONFIG per type; see 5-rates). Persist the design intent comments in
   CONFIG - the day/week economy arrives with the real game.
5. Torch: gear item, either hand, item light stat (asset mission lands the
   GLB + CONFIG.items.torch - build on it, manifest is torch-ready when its
   commit lands; if it has not landed yet, wire the mount for the manifest
   path anyway and it activates when the file exists).

You are Astrabot, Claude Code print-mode agent, worktree /tmp/wh-worldfeat
(branch feat/world-visuals). Laws as always: NO harness/headless runs, one
order at a time, CONFIG-driven everything, commit+push per sub-block.

## A. WORK ORDER S1 - enemy drops (game.js/enemy.js/CONFIG)
- CONFIG.drops = {
    bonusChance: 0.20,                        // per kill
    bonusPool: [                              // weighted
      { id: 'torch', weight: 50 },
      { id: 'bandage', weight: 30 },
      { id: 'magicGlove', weight: 8 }
    ],
    guaranteed: { id: 'stolenCoin', count: 1 },
    spawnDelaySec: 0.6                        // drop pops shortly after corpse settles
  }
- CONFIG.items.stolenCoin: { id, name 'Stolen Coin', glyph 'SC', category
  'valuable', stackCap: 999 } (new 'valuable' category - cyan box color OK
  for now; vendor/currency systems NOT built).
- At enemy death (the existing death entry point), schedule the drop: spawn
  1x stolenCoin at the corpse x/z (+ the 20% bonus roll). Drops use the
  EXISTING worldItems.spawn - same boxes, same E pickup, same region gating.
- Bonus-weight table resolver = tiny weighted pick helper, CONFIG-driven.
- magicGlove bonus respects stackCap/hands data automatically (it is a normal
  item).

## B. WORK ORDER S2 - gather nodes (NEW gather.js + region CONFIG)
- NEW file prototype/js/gather.js (index.html AFTER assets.js/light.js,
  BEFORE player.js like inventory.js's slot):
  WH_GATHER = { NodeManager, defs from CONFIG.gather }.
- CONFIG.gather = {
    interactRadius: 1.6,           // same as pickupRadius feel
    promptText: 'E - Gather {name}',
    gatherToast: 'Gathered {name} x{n}',
    fullText: 'Inventory full',    // reuse
    nodeTypes: {
      herbBundle:     { yield: { id:'forestHerb', count: 2 }, respawnSec: 90,  glowColor: 0x66aa55, scale: 1.0 },
      deadwoodPile:   { yield: { id:'deadwood',   count: 3 }, respawnSec: 180, glowColor: 0x998855, scale: 1.0 },
      mushroomCluster:{ yield: { id:'wildMushroom', count: 2 }, respawnSec: 120, glowColor: 0xaa99cc, scale: 0.85 },
      graveMoss:      { yield: { id:'graveMoss', count: 2 }, respawnSec: 150, glowColor: 0x77bbaa, scale: 1.0 },
      bonePile:       { yield: { id:'boneShard', count: 2 }, respawnSec: 150, glowColor: 0xbbbbaa, scale: 1.0 }
    }
  }
- Node VISUAL (placeholder, art pass later): small unlit marker mesh (cone or
  box per type from CONFIG shape) + a faint PointLight? NO - light budget
  discipline: the glow marker = an unlit emissive-look mesh + subtle bob/pulse
  via update; NO per-node PointLights (the light order's budget stays).
- Region CONFIG: add nodes arrays to regionA/regionB defs
  (e.g. regionA: 6x herbBundle, 4x deadwood, 4x mushroomCluster placed
  AWAY from the dirt path/lane and graveyard polygon - do not collide with
  the existing prop placements; scatter them in the remaining open forest
  floor; regionB: 4-5x graveMoss + 3-4x bonePile).
- NodeManager: holds nodes, tracks state (ready | dormant {t}), respawn
  tick in update(dt), region-visibility like WorldItems (only the active
  region's nodes visible).
- HARVEST: E near the nearest ready node within radius:
  inventory.addItem(yield.id, yield.count) - if added < yield.count (full),
  refuse: toast + node stays ready. Success: node -> dormant, respawn timer
  from CONFIG, toast 'Gathered X xN'.
- ITEMS to add in CONFIG.items (all category 'ingredient', default stackCap):
  forestHerb, deadwood, wildMushroom, graveMoss, boneShard. (Names/glyphs:
  FH, DW, WM, GM, BS - glyphs 2-letter per the Order A convention.)

## C. WORK ORDER S3 - torch hand wiring (player.js/game.js light hookup)
- Mount: torch GLB to hand bones via the Order B/C mount system (nativeHand
  torch: same as shield style - measure targetHeight; CONFIG.assets
  torchMount + weaponTargetHeight.torch).
- Light: when a torch is equipped in a hand, that hand's WH_PlayerLight slot
  uses CONFIG.items.torch.light (item stat wins on that hand - mechanism is
  LIVE already; ensure the hand light path reads the ITEM stat when the item
  has one, spell-binding light otherwise).
- Hand capability: kind 'torch' contributes NOTHING to combat flags (not a
  caster, not a shield, not melee) - carrying it just emits light. Both hands
  may be torch+glove, torch+shield, torch+torch (two lights, fine).
- Q swap pair (CONFIG.equip.qSwap) stays glove<->shield ONLY - do NOT sweep
  torch into Q. Torch swaps via the CHARACTER screen like other gear.

## D. AC (Nicko playtests)
| AC | Test |
|---|---|
| S1 | Kill any enemy: 1 Stolen Coin box pops at the corpse; ~1 in 5 kills also pops a torch/bandage/rare glove bonus |
| S2 | E near an herb bundle: 'Gathered Forest Herb x2', node fades out |
| S3 | Full inventory: gather refuses, node unharvested |
| S4 | Herbs return ~90s later (deadwood/mushroom at their rates); timers staggered per node, not global-sync |
| S5 | Nodes visible only in their region; forest nodes not on the path/graveyard |
| S6 | Torch equipped (either hand): warm light ~1.3x firebolt feel, gentle flicker; RMB with torch-only does nothing |
| S7 | Torch + glove: both hand lights live; CHARACTER screen can swap/drop the torch normally |
| S8 | Stolen Coin stacks (stackCap 999); coin boxes do not clutter (same despawn discipline as drops - no despawn yet, note if you add one) |
| S9 | No boot warnings; no light-budget regressions (still 4 player pool lights + flame cards) |

## E. Report
scratch/astrabot_stage2_drops_gather_report.md (committed): flows, anchors,
node placement list (coords), judgment calls, tunables, AC notes. Final
chat: commits with shas, AC table, knobs, undone items.