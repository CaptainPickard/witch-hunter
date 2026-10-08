# 62 - Forest of the Old King (Region C Design Doc)

Status: PROPOSED, IO spec session 2026-10-07 (census @ 98393f2, tip verified
equal to origin/feat/world-visuals). Rulings from Nicko's clarify form of
2026-10-07 are LOCKED for this region. The region name "Forest of the Old
King" is Nicko's own words and is canon from this order; any lore beyond
his order text is PROPOSED and flagged. This doc changes no mechanic, no
ruling in docs 00-61; conflicts with locked rulings are open questions.

## LOCKED RULINGS (clarify 2026-10-07, binding for Region C)

- R-62.1 ELEVATION: real heightfield, not fake hills. Spike first (raycast
  height sampler + smooth displaced ground mesh), then gameplay walks on
  sampled heights. Heavier, but true rolling hills. (The engine has zero
  heightfield tech today: ground = flat `CircleGeometry(whVisualGroundRadius,
  48)` + procedural texture, region-manager.js:1213 - verified 98393f2.)
- R-62.2 SCALE: radius 250-300, true open-world feel. Fog/LOD discipline is
  mandatory from day one (Nicko accepted the risk knowingly). This doc pins
  the spec number at 280 (middle of the ruled band), tunable by one CONFIG
  row without re-ruling.
- R-62.3 DUNGEONS: scene-swap regions. Each dungeon is its own region def in
  the existing region-manager (streaming/dispose/respawn machinery reused);
  fade teleports at doorways; per-region persistence keeps kills/pickups;
  the save records the region so load puts the player back in-world.
- R-62.4 ROT MOTHER: repeatable nest boss. Respawns after some in-game days
  so her materials stay farmable; minion cadence same as any cadence ruling;
  economy trivialization risk is accepted and tuned via respawn days.
- R-62.5 CAMP CHEST: spawns at the player's camp beside the campkit pegs,
  24-slot grid (6x4), panel styled like the tent menu, opens only while at
  camp, save schema gains an additive `chest` block.
- R-62.6 ANCIENT FOREST (Nicko playtest feedback on CC-C2, 2026-10-07):
  trees are scaled MUCH larger and spaced MUCH farther apart - we have lots
  of room and we use it. The Old King's forest must feel ancient. Tree
  scale band ~16-26 (rare specimens larger), stumps 2.4-3.4, minimum
  tree-to-tree spacing ~55m; the forest reads as sparse + massive, not
  dense + small. The tri-budget ledger (doc 61, 2M) still governs: scale is
  free (scale does not change tri count), so the ancient look buys
  atmosphere without buying tris.

## BINDING SOURCE ORDER (Nicko, 2026-10-07, condensed - full text in session log)

Region C is a new area accessed from Region B through a doorway directly
opposite the Region B entry door/archway (Region B's far north edge). The
doorway is ONLY accessible AFTER the player acquires the camp and sleeps
for the first time. Content: (1) massive open-world area for practicing
camping/cooking/fighting/leveling - much larger than A/B; (2) large trees -
SAME tree assets as A/B (yewTree / witchwoodTree / treeStump) - and rolling
hills; (3) multiple bandit camps reusing existing bandit + campkit prop
styles; (4) WOLVES hunting in packs, patrolling in loops (loop patrol
routes, pack cohesion, pack aggro - pack pulls pack); (5) the ROT MOTHER
and her minion spawns; (6) first DUNGEONS for finding crafting materials;
(7) first QUEST and first NPC - a farm area with a FARMER whose quest is to
rescue his daughter from the dungeon; on rescue the player is awarded the
first CAMP CHEST (a storage item that spawns at the player's camp).

## 1. REGION IDENTITY AND LOCATION

| Aspect | Value |
|---|---|
| Name | Forest of the Old King |
| id | `forest_of_old_king` |
| Access | Doorway on Region B's far north edge (the rim opposite B's south entry) |
| Gate | `!game.dayNight.dormant` (TUTORIAL LAW predicate, the same one the HP2 clock reads - daynight.js:126 dormant boot, camp.js:13 law header; verified 98393f2) |
| Geometry | C's playable circle center `(0, -366)`, radius 280 (playable 278.5 after margin 1.5, CONFIG.js:124) |
| Ground | Displaced heightfield mesh (R-62.1) after CC-C4; flat stub disc at y = -0.05 before it (avoids coplanar z-fight with B's disc, doc 61 latent risk) |
| Adjacency | B <-> C only, one connection initially (A and B stay untouched) |

Doorway placement arithmetic (verified against live clamps): Region B's
playable rim is `groundRadius 90 - playerMargin 1.5` (CONFIG.js:120,124)
under `whPlayRadius()` (region-manager.js:142-143); the deepest reachable
point on B's north edge is z = -88.5 at x = 0. The B/C boundary plane sits
at **z = -86** (2.5 units inside B's rim so the doorway arch props stand on
ground within B's own clamp). Crossing teleports 2 units past the plane per
the existing crossing convention (region-manager.js:57-72 family). C's
ground disc centered (0, -366) r=280 spans z ∈ [-646, -86], i.e. C is the
z <= -86 side of its plane.

Today this single boundary is one global boundary (`connections[0]`,
`clampPlayerPlane` region-manager.js:99-121; boundary plane z=+25 south).
Region C introduces a SECOND plane for the B player, so the boundary
machinery generalizes from one connection to a per-region connection table
(region-defs.js already carries a region-adjacency structure at :33+, the
generalization lands in CC-C2). A/B must keep working exactly as now: A's
side and the A/B plane stay byte-identical; the B/C plane only activates
when the B/C region pair is the active pair.

## 2. GATING - THE TUTORIAL LAW

- The B/C doorway is locked while `dayNight.dormant` is true. A live read of
  the DayNight instance owned by game.js (game.js:2070) is the gate; NO new
  state is added (HP2 already established `!dn.dormant` as the first-gate
  predicate).
- Locked feedback: interact range shows the arch; interacting before the
  gate opens gives a toast in the existing toast convention (camp ghost
  refusal style: name the REASON, e.g. "Rest at a camp first - the forest
  beyond still sleeps").
- Save/load interplay: a save taken while day > 0 keeps the gate open on
  load (dormant is false after the first Save-and-Heal for the whole
  profile; save.js persists `world.day`, save.js:97, so `day > 0` is the
  restored marker). No schema change needed for the gate.
- Enemies never cross (D2 law): bandits/wolves/the Rot Mother clamp to C's
  side of the B/C plane exactly as B's enemies do today
  (`clampEnemyToHomeSide`, region-manager.js:124-143).

## 3. WORLD LAYOUT AND LANDMARKS

Design intent (Nicko's order): a huge forest where the practiced verbs of
A/B - camping, cooking, fighting, leveling - are the whole playstyle. C
gives each verb room: camps to found, packs to hunt, a nest to farm, a
barrow to delve, a farm to help.

Proposed layout (C-local grid, origin = C's center (0, -366); placements
are PROPOSED rows for CC-C2/CC-C3, tuned in play - no ruling locked here):

| # | Landmark | C-local pos (x, z) | Contents |
|---|---|---|---|
| L0 | Entry glade | (0, +273) i.e. world (0, -93) | Doorway arch (gateM/arch family reuse) facing B; safe spawn/return plaza; one lantern post |
| L1 | The Old King's Stone | (0, 0) = world (0, -366) | REGION CENTERPIECE: a crown-shaped ruin - m3 statue + m1 gate pair + boulders ring on a heightfield rise; visible silhouette from most of the region (doc 61's landmark/skyline gap) |
| L2 | Barrow entrance (dungeon door) | (+170, -60) | Sunken mound with stone steps (crypt kit pieces exist on disk: chandelier, pillars, steps, sarcophagus, skulls, candelabra - doc 61:52-54) |
| L3 | Rot Mother lair | (-175, +95) | Marsh glade, nest mound (heightfield dip + egg sacs placeholder props) |
| L4 | Bandit camp Alpha | (-60, +180) | 2-3 bandits, firepit, bandit props |
| L5 | Bandit camp Bravo | (+95, +130) | 3-4 bandits, firepit, bandit props |
| L6 | Bandit camp Charlie | (-140, -140) | 4 bandits (deepest, best loot tier) |
| L7 | Wolf den East | (+210, +40) | Pack 1: 3 wolves, loop patrol |
| L8 | Wolf den West | (-215, -30) | Pack 2: 4 wolves, loop patrol |
| L9 | Wolf den North | (-30, -200) | Pack 3: 3 wolves, loop patrol |
| L10 | Farmstead | (+150, +205) | Fences (m2 picket reuse), farmhouse (placeholder kit assembly; Astrabot model flagged), farmer NPC |

Traversal grammar: door (L0) -> practice strip (L4/L5 visible early) ->
center landmark (L1) anchors orientation -> outer ring (dens, lair, barrow,
farm) rewards long trips -> camping everywhere (the C4 camp system is the
lifeline at r=280). Nothing blocks the direct walk from door to barrow;
wolves' loops cross the paths (tension without gating).

## 4. ELEVATION - THE HEIGHTFIELD PROGRAM (R-62.1)

Phased, spike-gated:

1. **CC-C1 SPIKE (scratch-only, no game files)**: displaced PlaneGeometry at
   C scale with smooth multi-octave noise; raycast height sampler; segment
   density vs fps probe; sampler API shape (`WH_GROUND.heightAt(x, z)`)
   validated on slopes and hilltops. Output: spike log + demo html + the
   CONFIG rows CC-C4 will consume. No game js touched.
2. **CC-C4 LANDS IT**: C's ground becomes the displaced mesh; the sampler
   feeds actor y. Rules:
   - `heightAt(x,z)` is the single source of truth (player, enemies, props,
     corpses, camp placement ghost all sample it). No per-actor shortcuts.
   - Props ground-align on slopes via the sampler (P0-1 holder pattern from
     doc 61 keeps the base on ground).
   - Actors get a max-step guard (walkable slope clamp) so hills read as
     hills, not walls or ramps; numbers come from the spike, tuned in play.
   - Camera min-height respects sampled ground (doc 61 camera-under-ground
     finding).
   - A/B stay flat y=0; the sampler returns 0 outside C (and inside any
     flat region) so one code path serves all regions.
   - Save schema: no change - y is derived from (regionId, x, z) on load.
3. Deferred if the spike shows a real perf wall: tree-scatter density rides
   the same displacement; impostor stage is CC-C3's fallback lever.

## 5. ENEMY ROSTER AND PLACEMENT PHILOSOPHY

Roster for C: bandit (existing), wolf (new), rot spawn minion (new), Rot
Mother (new boss). Ghouls DO NOT spawn in C's overworld (they stay A/B/zombie
by ruling) EXCEPT inside the barrow dungeon, where they fit.

Philosophy: C is the practice ground - every encounter teaches or feeds a
verb. Bandit camps teach the landed AI1 guard posture and give cookable
fires. Wolf packs teach spacing and retreat (pack pulls pack). The nest
teaches boss patterns with a farmable reward. The barrow teaches delving.
Placement is literal CONFIG rows (no procedural spawning - same as A/B).

### 5.1 Wolves (packs, loops, cohesion)

- Pack = 3-4 wolves on a closed loop patrol route (literal waypoint list in
  CONFIG; loops cross paths deliberately).
- Pack cohesion: stragglers beyond a leash radius of the pack centroid
  regroup (state hook in the pack FSM); nobody solo-pulls.
- Pack aggro: aggroing one member aggros the whole pack (the "pack pulls
  pack" law, binding).
- Hunt pattern v1: reuse AI1's landed strafe band + decision loop shapes for
  the pack orbit; wolves lunge in relay (one commits, others circle).
- Night boldness: aggro radius multiplies when `dn.phase` reads night
  (uses the landed clock; darkcourt law respected - night is simply more
  dangerous).
- Model: Astrabot lane (wolf GLB + run/attack/howl/death). CC-C5 ships a
  placeholder body so the behavior is playtestable before the model.

### 5.2 Rot Mother (R-62.4 repeatable nest boss)

- Lair L3: nest mound (heightfield dip), egg-sac placeholder props.
- Boss loop: slow heavy slams + poison-lite (v1 = damage + slow debuff, NOT
  a new status system; full poison economy is a later ruling).
- Minion cadence (binding cadence number, tunable): while she lives, spawn 1
  rot spawn every 7s, cap 3 live; all die/despawn when she dies.
- Respawn: lair re-arms 3 fully-camped in-game days after her last death
  (day counter read; `dayLastKilled` rides the chest/quest additive save
  block family). Re-arming happens on player proximity, not while away.
- Reward: rot-silk + rotgland crafting materials per kill (the farmable
  loop in R-62.4).
- Model: Astrabot lane; CC-C7 ships a placeholder body first.

### 5.3 Bandit camps

- 3 camps (L4/L5/L6) reusing bandit props + campkit firepit/bedroll/pegs
  (CK1 pattern: player camp kit vs bandit props already both exist
  f6a05bc). Firepits are USABLE cook stations (existing cook station
  surface) - travelers can cook at enemy fires: camping practice reward.
- Guards use AI1 landed posture (lock-on awareness, strafe band, 0.5x
  front-arc guard - e325005/6aaf339).
- Loot: corpse/gather nodes at camp (NO containers until CC-C12; chests
  stay the quest reward).

## 6. DUNGEON - THE OLD KING'S BARROW (R-62.3 scene-swap)

- The barrow is its own region def (id `old_king_barrow`) inside the SAME
  region-manager: streaming, disposal, per-region persistence (dead stay
  dead), and the spawn/respawn machinery all reuse. Fade teleport at its
  door (L2) mirrors the existing region crossing.
- Interior: crypt-kit corridors and the sarcophagus chamber (assets on
  disk, doc 61:52-54); dark fog + low ambient + candelabra light pools
  (doc 61's light-pool gap) - no Astrabot dependency for the shell.
- Save/death: `world.regionId` joins the save additively (C4 law, additive
  blocks only). Load restores active region at its entry side of the door;
  death in the barrow respawns at the camp respawn point (existing respawn
  machinery) and does NOT roll region persistence.
- Exit: the entrance chamber's door teleports back to C at the barrow
  threshold.
- Purpose v1: dungeon traversal + crafting materials (CC-C9) + the quest's
  rescue chamber (CC-C10/CC-C11).

## 7. FARM, FARMER, QUEST CHAIN (first NPC, first quest)

- Farmstead (L10): picket fence runs (m2 reuse), tilled-plot texture rows on
  the heightfield (ground-canvas variant), farmhouse (placeholder kit
  assembly first; Astrabot farmhouse flagged).
- The FARMER: first NPC. Body: reuse an existing races GLB standing v1
  (placeholder), Astrabot model flagged. Dialog: DOM panel in the tent-menu
  style (camp.js convention) - first dialog UI.
- Quest chain (first QUEST):
  1. Talk to the farmer -> dialog gives the quest: his daughter was taken
     into the Old King's Barrow.
  2. Objective HUD line (tent-menu style readout) tracks the rescue.
  3. Enter the barrow; the daughter is held in the sarcophagus chamber
     (guarded); interact to free her -> escorted v1 = instant "rescued"
     state (no escort mechanic; walk-out together is visual only).
  4. Return talk completes the quest -> reward: the CAMP CHEST spawns at
     the player's camp (R-62.5).
- State machine v1: `available -> active -> complete`, persisted additively
  in the save (`questState` block). This is the seed of the quest system;
  doc 46's beat grammar stays the long-form reference, no contradiction.

## 8. CAMP CHEST (R-62.5 reward)

- Spawns beside the campkit pegs at the player's camp (all current and
  future camp placements) once the quest completes; persists across camp
  re-placements (rides the camp site list).
- Interact opens the chest panel ONLY while at camp (R-62.5).
- 24-slot grid (6x4), tent-menu styling; deposit/withdraw with the existing
  inventory item model (cooking inventory block is the pattern).
- Save: additive `chest` block (wh-save-v1 schema v1 stays; save.js:283
  WH_SAVE surface), storing slot arrays, never shipped item lists.

## 9. ASTRABOT ASSET LANE (flagged, NO dispatch without Nicko's word)

| Asset | Needed by | Placeholder until then |
|---|---|---|
| Wolf GLB + anims (run/attack/howl/death) | CC-C5 behavior order | recolored/box body |
| Rot Mother GLB + egg sacs | CC-C7 | placeholder body |
| Rot spawn minion GLB | CC-C7 | scaled ghoul-looking placeholder (NOT the ghoul enemy wiring) |
| Farmer GLB | CC-C10 | standing races GLB |
| Daughter GLB | CC-C11 | standing races GLB |
| Farmhouse set | CC-C10 | church-kit assembly |
| Chest GLB | CC-C12 | procedural chest box |

## 10. PERFORMANCE AND BUDGET DISCIPLINE (R-62.2)

- r=280 tri budget: tree tri count is THE risk (doc 61: B hits 72% of the
  2M budget with 43 biome props). C's scatter discipline: fog-dense palette
  (C's fog tuned deep-forest), scatter placement with distance-culling
  (beyond fog-opaque range = not placed), and CC-C3 ships a tri-budget
  ledger in the order brief. LOD/impostors are the explicit fallback lever
  (doc 61 P1-5) if Nicko's fps counter or the spike ledger demands it.
- Ground mesh density for the heightfield: from the spike (target: one
  draw-call displaced mesh, < 40k tris).
- The barrow renders as its own region (single-active law keeps GPU honest);
  crossing spike discipline rides the existing prewarm.

## 11. NON-GOALS (explicitly out of scope for this region)

- No new player verbs (no climbing, no swimming, no mounts).
- No new damage types beyond the v1 poison-lite note (design only).
- No multi-dungeon support beyond the ONE barrow (more dungeons are future
  orders riding the same CC-C8 machinery).
- No weather. No mini-map. No horse. No new UI frameworks beyond the tent-
  menu and dialog panels.
- A/B stay byte-compatible: their regions, enemies, props, camp law, and
  tutorial law are untouched except where CC-C2 generalizes the connection
  table (A's rows land unchanged).

## 12. OPEN QUESTS

- OQ-62.1 Walkable slope clamp numbers (from CC-C1 spike, tuned in play).
- OQ-62.2 Tree scatter density + impostor threshold after the first C
  playtest fps read.
- OQ-62.3 Poison-lite v1: damage+slow only - confirm with Nicko at CC-C7
  clarify (do not silently grow it).
- OQ-62.4 Daughter "rescue" feel: instant-rescue v1 vs a walk-out beat -
  Nicko's call at CC-C11 clarify.
- OQ-62.5 Farmer voice/name - new-canon name needed at CC-C10; proposed as
  an open question there, not invented silently here.

## 13. PROCESS LAW REMINDERS (binding, unchanged)

One change order at a time; brief files in io/missions/ with crg impact
baked in; builder = Claude Code print mode with the standing flags; commit
+ rebuild bundle before each commit; push after every commit; 8793 atomic
flip with relative releases/<sha> after landing; NO harness runs (Nicko
playtests, syntax checks only); nothing merges to dev/main without
Nicko's explicit call; Astrabot lane is flagged, not dispatched.