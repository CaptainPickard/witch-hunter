# Astrabot report - Stage 2: enemy drops + gather nodes + torch hand wiring

Date: 2026-10-05. Brief: `io/missions/2026-10-05-astrabot-stage2-drops-gather-brief.md`, including the playtestGlow amendment (9073ca1).
Branch: `feat/world-visuals`. No harness or headless runs. No assets generated.
Syntax was checked with a Python JS parser (`esprima`, because there is no node on this box). Every placement and grip number comes from static Python scripts in `scratch/`.

## Commits

| Sub-block | sha | What |
|---|---|---|
| S1 drops | b0a2876 | `CONFIG.drops`, `items.stolenCoin`, `Enemy.onKilled`, weighted pick, delayed spawn |
| S2 gather | ee30437 | new `js/gather.js`, `CONFIG.gather`, 5 ingredient items, region node lists |
| S3 torch | 1916775 | `torchMount`, `items.torch.mesh`, a second torch mesh so both hands can hold one, hand light at the flame |
| report | (this commit) | this file + gather marker now fogged |

## Flows and anchors

### S1 - enemy drops
- **Kill entry point:** `enemy.js` `Enemy.prototype.takeDamage`, in the death branch. Both the melee sweep (`game.js` loop) and firebolt (`spells.js:69`) end there. It calls the static hook `Enemy.onKilled(enemy)`.
- **Scheduling:** `game.js` `scheduleDrops` rolls the loot when the enemy dies:
  - guaranteed `stolenCoin x1`
  - then a `Math.random() < bonusChance` roll, and if it hits, `weightedPick(bonusPool)`
  - the result is queued on `game.pendingDrops` with the corpse x/z and `enemy.homeRegionId`
- **Spawning:** `tickDrops(dt)` runs in the loop before `worldItems.update`. Once `spawnDelaySec` runs out it calls the existing `game.worldItems.spawn`, so drops get the same boxes, E pickup and region gating as anything else. The coin lands on the corpse; a bonus item lands `bonusOffset` (0.45 m) away so the two boxes don't overlap.
- **Drop odds:** torch 50/88 = 56.8%, bandage 34.1%, glove 9.1%. Per kill: torch 11.4%, bandage 6.8%, glove 1.8%.
- **New categories:** `valuable` (pale cyan 0x9ff0f0) and `ingredient` (moss 0x7cb860) get entity colors. The inventory tooltip now names the category instead of saying "Consumable" for every non-gear item.

### S2 - gather nodes
- **Load order:** `index.html` loads `js/gather.js` after `light.js` and before `player.js`. It exposes `window.WH_GATHER = { NodeManager, defs }`.
- **Construction:** `NodeManager(scene, WH_REGION_DEFS.regions)` builds every region's `cfg.nodes`. Each node is `{ type, regionId, x, z, state 'ready'|'dormant', readyAt, fade }`.
- **E key** (`game.js`): a ground item in pickupRadius is picked up first (`tryPickup` now returns bool); otherwise `tryGather` runs:
  - it finds the nearest READY node in the active region within `interactRadius`
  - `harvest` takes the whole yield or nothing. If `addItem` only fits part of it, that part is removed again, the "Inventory full" toast shows, and the node stays ready.
  - on success the node goes dormant, its timer comes from the economy clock, and the toast reads `Gathered {item name} x{n}`
- **Prompt:** `#wh-gather-prompt` (HUD) shows `E - Gather {node name}` while a ready node is in reach and no ground item would take the E press.
- **`update(dt, activeRegionId)`:**
  - ticks respawn
  - fades (scale to 0 plus a 0.15 m sink over `fadeSec` 0.5) when harvested, and fades back in on respawn
  - only the active region's nodes are visible
  - bobs and pulses the marker
- **Respawn economy model:**
  - `economy.mode 'playtest'` uses per-type `respawnSec` on the game clock (accumulated dt, so it pauses while the tab is hidden)
  - `'real'` uses `realSec[rarity]` (86400 for common, 604800 for rare) on `Date.now()`
  - each respawn is jittered ±`respawnJitterPct` (15%), so node timers drift apart (AC S4)
  - `reshuffleOnRespawn` (default false in playtest) moves a returning node to a random free spot in its region+type placement pool
- **Visual:**
  - a placeholder clump at every node: dodecahedron, Lambert, glowColor×0.45, flat-shaded. This is the stand-in for later bush/grass art.
  - only while `playtestGlow` is true: an unlit (MeshBasic) octahedron marker floating 0.95 m up, with bob and pulse
  - **no PointLights**
  - geometry and materials are shared per type
- **Debug:** `WH_DEBUG.getGatherNodes()`.

### S3 - torch hand wiring
- **Hand mesh:** `CONFIG.items.torch.mesh = 'torch'` (MANIFEST.torch from c317a13). `setupHandMeshes` creates a second torch mesh, and `player.setItemMesh(id, mesh, twin)` stores torch meshes per hand in `player.handMeshes[id] = { left, right }`. Torch + torch therefore shows two meshes.
- **Mount:** `prepTorch` slides the inner mesh down by `gripHolderY` so the fist sits on the grip, and hangs a light anchor at `lightHolderY`. `mountTorch` turns raw +Y (butt to flame) toward hand-local `headAxis` and places it at `offset` (the fist centroid). It is measured for `nativeHand.torch = 'left'` and mirrored for the right hand, the same way as the shield. The stand-in body falls back to the idle anchor.
- **Light** (`light.js`):
  - `handLightDef` already returned `items[id].light` before the spell binding, so the item's stat wins on that hand (unchanged)
  - new: while a torch mesh is mounted, that hand's PointLight hangs at the torch's flame anchor instead of the fist. The asset report noted the hand would otherwise hide the light.
  - when the torch leaves the hand, the light goes back to the hand bone, so it never leaves the scene graph and the light count stays fixed
- **Combat:** `handAction` returns null for kind 'torch'. RMB/LMB with a torch-only hand do nothing, and the torch is not counted as a caster, shield or melee weapon. `CONFIG.equip.qSwap` is untouched (glove <-> shield).

## Torch measure (`scratch/measure_torch_grip.py`, static GLB parse)

The torch's XZ radius per 5% Y slice (raw units, butt at holder y 0, H 1.8988):
- the shaft is narrowest at 0.061-0.062, at holder y 0.38-0.57. That is the grip, so `gripHolderY` = 0.50.
- the head flares from 1.14 to 1.80 (r 0.17)
- the amber cap starts at 1.54 (from the asset report). The light goes at `lightHolderY` 1.70.

At a scale of 0.3265, the fist sits about 0.16 m from the butt and the light about 0.39 m above the fist.

## Node placements (`scratch/gen_gather_nodes.py`, seed 20261005)

Region A (hold_outskirts) clearances:
- open forest floor only
- dirt path corridor (half width 2.7 + 2.5 m)
- the cemetery and its tree ring (ellipse centred (0, 10), semi-axes 36 x 33)
- props: trees 4 m, others 3 m
- enemy spawns 5 m, player spawn 6 m
- z > -17 (gate corridor)
- at least 9 m between nodes

| type | x | z | nearest prop |
|---|---|---|---|
| herbBundle | 59.8 | 23.1 | 8.0 |
| herbBundle | 13.5 | 58.4 | 5.2 |
| herbBundle | -54.7 | -15.4 | 12.5 |
| herbBundle | -54.5 | 44.3 | 13.9 |
| herbBundle | 21.3 | 71.0 | 5.5 |
| herbBundle | 39.8 | 43.1 | 7.0 |
| deadwoodPile | 69.4 | 16.4 | 6.5 |
| deadwoodPile | 70.8 | -3.8 | 6.1 |
| deadwoodPile | -34.3 | 42.0 | 5.8 |
| deadwoodPile | -40.0 | 4.6 | 7.0 |
| mushroomCluster | 38.0 | -6.3 | 9.3 |
| mushroomCluster | 59.2 | -0.5 | 8.3 |
| mushroomCluster | 68.5 | -12.6 | 6.3 |
| mushroomCluster | -60.0 | 23.2 | 7.4 |

Region B (darkwood_edge) uses the band |x| < 42, z -82 to -31, at least 6 m between nodes:

| type | x | z | nearest prop |
|---|---|---|---|
| graveMoss | -32.9 | -39.1 | 4.5 |
| graveMoss | 38.3 | -57.4 | 6.0 |
| graveMoss | -33.7 | -62.2 | 5.3 |
| graveMoss | -14.4 | -66.6 | 4.6 |
| graveMoss | -12.7 | -48.1 | 4.3 |
| bonePile | 31.7 | -63.2 | 5.5 |
| bonePile | -41.7 | -54.4 | 8.2 |
| bonePile | -17.0 | -53.1 | 6.2 |
| bonePile | -2.7 | -52.4 | 5.2 |

## Judgment calls

1. **Drop region = `enemy.homeRegionId`**, not the active region. The corpse lies in its home region, and enemies only tick in the active one.
2. **Bonus item offset by 0.45 m** from the coin (`drops.bonusOffset`) so two boxes never overlap.
3. **Gather is all-or-nothing.** A partial fit is rolled back, which matches the brief's "if added < yield.count, refuse ... node stays ready".
4. **One key for both actions.** E picks up a ground item first and gathers only if there is none, so a drop lying next to a node never blocks either action for long. The prompt hides while a ground item is in reach.
5. **Prompt vs toast names.** The prompt uses the node name ("E - Gather Herb Bundle"); the toast uses the item name ("Gathered Forest Herb x2"), as AC S2 specifies.
6. **"Fades out" is a scale shrink plus sink**, not opacity. That keeps the per-type shared materials and avoids per-node transparent sorting.
7. **Staggered timers:** ±15% jitter per respawn. The first harvest is staggered anyway because the player harvests nodes at different times.
8. **Reshuffle model is built but off** (`reshuffleOnRespawn: false`), so AC S4 ("herbs return ~90s later") is testable in place. With today's pools (pool = the live node list) a reshuffle would have no free spot anyway. The real game needs pools bigger than the live count; see Undone.
9. **Marker uses fog.** It is unlit but fogged, so it reads as a faint marker close up and doesn't shine through the mist from across the map.
10. **Torch mesh per hand (twin)** instead of `itemMeshes[id]`, which is one mesh per id. The second instance shares geometry and materials (`clone(true)`).
11. **Torch light at the flame**, following the asset report's note. The item light stat is unchanged.
12. **No despawn on drops** (AC S8: same discipline as G drops). Boxes stay until picked up. Stolen Coin stacks to 999 in one slot.

## Tunables (all CONFIG)

- **`CONFIG.drops`:** bonusChance 0.20, bonusPool weights 50/30/8, guaranteed, spawnDelaySec 0.6, bonusOffset 0.45
- **`CONFIG.items`:**
  - stolenCoin (stackCap 999)
  - forestHerb / deadwood / wildMushroom / graveMoss / boneShard (default stackCap 60)
  - torch.mesh
- **`CONFIG.inventory.entity.colors`:** valuable, ingredient
- **`CONFIG.gather`:**
  - interactRadius 1.6, prompt/toast/full text
  - respawnJitterPct 15, fadeSec 0.5
  - economy: mode, realSec, reshuffleOnRespawn
  - **playtestGlow true** (real game: false)
  - marker: size, height, bob, pulse
  - base: radius, height, colorMult
  - nodeTypes: name, rarity, yield, respawnSec, glowColor, scale
- **`regionA.nodes` / `regionB.nodes`:** placements, which are also the per-type placement pools
- **`CONFIG.assets.torchMount`:** headAxis [0,0,1], rollDeg, offset, gripHolderY 0.5, lightHolderY 1.7. `equip.nativeHand.torch` is 'left'.

## AC notes (Nicko playtests - none of these were run in a browser)

| AC | Expected | Note |
|---|---|---|
| S1 | coin box at corpse 0.6 s after the kill; ~1 in 5 kills add a bonus box | melee and firebolt kills both route through takeDamage |
| S2 | E at an herb bundle: "Gathered Forest Herb x2", node shrinks away | prompt "E - Gather Herb Bundle" |
| S3 | full grid: "Inventory full", node stays | a partial fit is rolled back |
| S4 | herb ~90 s ±15%, deadwood 180, mushroom 120, moss/bone 150 | jitter per respawn |
| S5 | A nodes only in A, B nodes only in B; none on the path or in the cemetery | see the placement tables |
| S6 | torch in either hand: 0xffa040 @10.5 / 15 m light with 7% flicker at the flame; RMB with a torch-only left hand does nothing | **mount orientation is not verified in-engine.** If the torch points wrong, tune `torchMount.headAxis` / `rollDeg` |
| S7 | torch + glove: both lights; CHARACTER tab [L]/[R]/unequip/drop work like other gear | torch + torch shows two meshes and two lights |
| S8 | coin stacks to 999 in one slot; no despawn added | |
| S9 | no new lights (still 4 pool + 2 hand + 2 projectile, flame cards unchanged); new boot paths: gather nodes (unknown type, console.warn only), twin torch | the torch GLB was already preloaded since c317a13 |

## Undone / follow-ups

- **Torch mount is unverified in-engine.** `headAxis` [0,0,1] assumes the torch is carried like the longsword blade. It is one CONFIG edit if it looks wrong. The flame anchor and grip are measured.
- **Real-game economy:**
  - placement pools need extra spare spots per type (e.g. `pool: true` entries that hold no live node) before `reshuffleOnRespawn` does anything useful
  - wall-clock respawn state is not persisted (there is no save system)
- **No rare node types yet.** Every node type is `rarity: 'common'`; the rare path (real week) is only reachable from CONFIG.
- **Node meshes are placeholders**, waiting on the bush/grass art mission.
- **Drops never despawn.** If coins pile up in playtest, a `drops.despawnSec` would be the knob to add.
- **Vendor/currency for Stolen Coin and cooking for ingredients are not built**, as the brief says.

---

## INTERACT BUTTON (Order S3b, 2026-10-05)

A touch USE button that does exactly what the E key does, so pickup and gather work on a phone.

**One entry point.** `game.js` now has a single `interact()` function: it does nothing if input is suspended (inventory open) or the player is dead; otherwise it tries `tryPickup()`, then `tryGather()`, and returns whether anything happened. Three callers use it:
- the E keydown handler (`CONFIG.inventoryUI.pickupKey`, same `e.repeat` guard as before)
- `WH_DEBUG.interact()`, which sits next to `handButton` and is what the touch layer calls
- future chests and doors: add their `tryX()` to the `||` chain inside `interact()`. Nothing else needs to change.

Pickup and gather rules are not touched. The guard and the item-before-node order are the same as the old E path. They were moved, not rewritten.

**Button.** `CONFIG.touch.layout.interact = { x: 0.74, y: 0.38 }`, glyph ◈, label `Use`. It uses the same `.wh-touch-ctl` style, the same `touched` press feedback, and the same size and scale as the other buttons. It is always visible when the touch layer is showing, it can be dragged in LAYOUT mode, and it is included in the saved layout and in Reset. If a saved layout from before this change has no `interact` entry, the button sits at the CONFIG default.

**Placement reasoning.** The suggested (0.72, 0.52) is about 50 px from sprint (0.68, 0.62) on a landscape phone (~800x380). That is less than the 64 px button, so they would overlap. (0.74, 0.38) sits above-left of attack (0.90, 0.45) and above sprint:
- landscape ~800x380: ~130 px from attack, ~100 px from sprint, well above the camera pad (r 70 at y 0.72)
- portrait ~390x844: ~85 px from attack

It can be moved with the LAYOUT drag if a thumb disagrees.

**No double-fire.** The touch layer never sends a synthetic `KeyE`. It calls the hook directly, and the button already swallows mouse/touch compatibility events, as attack does. Desktop E goes through the keydown handler only.

| AC | Expected |
|---|---|
| I1 | Use ◈ appears above-left of Attack, clear of Sprint, Dodge, Off Hand, Lock-On and the camera pad |
| I2 | Near an item box: picks it up, with the same toast as E |
| I3 | Near a ready node (no item in reach): gathers it, with the same toast as E |
| I4 | Nothing in range: no-op, no console error (`interact()` returns false) |
| I5 | Desktop E behaves as before, one action per press |

Not tested in a browser (no headless browser, by order). The syntax was checked by reading the code only, because node is not installed in this environment.

---

## CORPSE LOOT (Order S4, 2026-10-05)

Enemy drops now stay on the corpse. Kills no longer spawn boxes. Boxes are only for player G-drops.

### Flow
1. `Enemy.takeDamage` → `Enemy.onKilled` → `game.js storeCorpseLoot(enemy)`. The S1 roll (`rollDrops()`: guaranteed 1x stolenCoin + 20% weighted bonus, `CONFIG.drops` unchanged) goes to `WH_CORPSE_LOOT.Manager.attach`, which sets `enemy.corpseLoot = [{id, count}, ...]` and builds that corpse's effect.
2. The effect waits for `appearDelaySec` (0.6, the old box delay) and for the death settle (`corpseFinalY` set). It then measures the body centre once with a Box3, because the fall direction moves the torso away from root. After that it fades in over `fadeInSec`.
3. `interact()` = `tryPickup() || lootCorpseNearest(x, z, lootRadius) || tryGather()`. E and touch USE both route through it, as before.
4. `lootCorpseNearest` finds the nearest corpse in the active region that still has loot, measured from the body centre. Every entry goes through `inventory.addItem` (stack-join), and what does not fit stays in `corpseLoot`:
   - Something was taken: toast `Looted: Stolen Coin x1, Torch x1`, plus ` - Inventory full` if anything was left on the body.
   - Nothing fit: toast `Inventory full`, and the corpse keeps glowing.
   - The list is empty: the effect fades out over `fadeOutSec`, then its materials and geometry are disposed. `nearest()` skips the corpse from then on.
5. **Prompt:** I generalized the existing `wh-gather-prompt` element rather than adding a second one. `updateInteractPrompt()` follows the interact order:
   - a box is in reach: no prompt, same as before;
   - else an unlooted corpse: `USE - Loot`;
   - else a ready node: `E - Gather {name}`.
6. **Lifetime:** each effect lives in the scene, not the region group. Every frame the manager checks that its enemy is still in `regionManager.enemies[homeRegionId]`. When a region is unloaded or rebuilt, the effect is disposed and `corpseLoot` is cleared, so the loot vanishes with the corpse. Corpses rebuilt from the region's dead-state come back without loot. The CONFIG comment marks where real-game persistence will attach later (region state next to the 'dead' flag).

### Visual (no lights)
- **Glow:** an additive `THREE.Sprite` billboard, `glowScale` 1.5 m, centred `glowHeight` 0.45 m above the body. A flat additive ground disc (`groundGlow`) sits under the corpse so it reads at night. Both use the shared canvas radial texture, tinted `glowColor` 0xd8b24a, with an opacity breath every `glowPulseSec` and a slight scale breath. Fog stays on, so the glow is faint at range like the gather markers.
- **Sparks:** one `THREE.Points` per active corpse with a recycled pool of `sparks.count` (14). Positions are in world space. Each spark's brightness is written into its vertex colour (additive blending, so black is invisible): it fades in at the body and out at the top. Each spark drifts and sways sideways. Nothing is allocated per frame, only typed-array writes. During the fade-out no new sparks spawn.
- **Allocation:** each corpse gets 1 SpriteMaterial, 1 MeshBasicMaterial, 1 PointsMaterial and 1 BufferGeometry, created once at the kill and disposed when the effect ends. The textures and the disc geometry are shared.
- **PointLights: zero.** The light budget is unchanged.

### Knobs (`CONFIG.corpseLoot`)
| Group | Knobs |
|---|---|
| Interaction | `lootRadius` 1.6, `promptText`, `lootToast`, `partialSuffix`, `fullText` |
| Timing | `appearDelaySec` 0.6, `fadeInSec` 0.4, `fadeOutSec` 0.5 |
| Glow | `glowColor`, `glowOpacity` 0.55, `glowPulseSec` 2.4, `glowPulseMin` 0.6, `glowScale`, `glowHeight`, `groundGlow {radius, opacity}` (opacity 0 turns the pool off) |
| Sparks | `sparks {count, riseSpeed 0.45, drift 0.12, lifetimeSec 2.2, lifetimeJitter, spawnRadius 0.45, size 0.07, color 0xffd27a}` |

### Judgment calls
- **Removed `CONFIG.drops.spawnDelaySec` and `bonusOffset`.** They were box-only. The delay now lives on as `corpseLoot.appearDelaySec`.
- **The corpse can be looted during the 0.6 s appear delay.** The loot exists from the moment of the kill, and only the effect waits. Looting it before the effect shows just disposes the effect.
- **Added the ground pool disc** next to the billboard. A billboard alone gets cut by the ground plane under a downward camera, and the pool makes the glow read at night.
- **New debug hook:** `WH_DEBUG.getCorpseLoot()` returns `[{type, state, x, z, loot}]`.

### AC
| AC | Expected |
|---|---|
| C1 | Kill: no boxes. After about 0.6 s the corpse fades in a pulsing gold glow and pool, with sparks rising |
| C2 | USE/E near the corpse: `Looted: Stolen Coin x1` (bonus item listed when rolled); glow and sparks fade over 0.5 s |
| C3 | Inventory full (no coin stack with room): `Inventory full`, and the corpse keeps glowing |
| C4 | Partial: what fits is taken with ` - Inventory full` appended; looting again later takes the rest, then the effect ends |
| C5 | G-drop boxes unchanged; `tryPickup` runs first, so a box wins over a corpse |
| C6 | Node gathering unchanged; a corpse wins over a node, and the prompt follows the same order |
| C7 | No lights added (`getLightPool` and the scene light count are unchanged) |
| C8 | No new boot code paths besides creating the manager. Locomotion and latching are untouched |

### Not done / unverified
- **Not run in a browser** (no headless browser, by order). Node is not installed here, so I syntax-checked the edited files with python esprima. Nicko's playtest is the first real run.
- **Corpse loot does not persist across region rebuilds**, as the playtest rule says. Real-game persistence is marked in CONFIG.
