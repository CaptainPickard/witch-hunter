# CC-C4a · Flora Pass + The King's Roads — full-disc flora, boulders, dead trees, unlit winding path + 3 branch roads

Change-order brief, written 2026-10-08 by IO from Nicko's playtest ruling
(R-62.7 ANCIENT FLORA + CROSSROADS, session 2026-10-08), docs/planning/62
§1/§5.1, docs/planning/63 CC-C3, and the landed Round-E/dirt-path machinery.
Base 23f2e3c (CC-C4 heightfield landed + mtime fix). Branch
feat/world-visuals, worktree /tmp/wh-worldfeat. ONE order at a time.
CC-C4b (rim mountains) follows AFTER this order's playtest. Merge to
dev/main = Nicko's call only. Always English.

## 0. WHY THIS ORDER (R-62.7, binding)

Nicko on CC-C4: "add more flora to this region — the roses, around trees,
bushes, etc. Even random boulder assets of different scales to fill the
area between the old king trees, even some dead trees from the other area
at their normal size. This area is a crossroads: a winding dirt path, NOT
lit by lanterns, leads to the Old King's Stone in the middle, then branches
in three directions (north, east, west) — these will eventually lead to 3
new areas built later."

Locked interpretations (clarify recommendations accepted 2026-10-08):
- Flora uses EXISTING assets now; a true rose bush GLB stays open as a
  later small Astrabot asset (NOT dispatched in this order).
- The 3 branch roads VISIBLE-but-soft-blocked at the rim (toast convention,
  reason-naming) until the future regions exist; C4b carves the rim
  notches they point into.
- "Roses" v1 = the floral layer that exists (moonbell colonies + bracken +
  bushB + bramble + grass) — moonbell bell-flowers are the pale-flower
  accent.

## 1. LANDED MACHINERY THIS ORDER REUSES (verified @ 23f2e3c)

- SCATTER ENGINE (Round E): CONFIG.scatter (CONFIG.js:716-772: seed, clear
  radii, keepOut, treesExtra, bushes{ring,free}, grass) + whScatterPlan
  (region-manager.js:711, pure function, seeded rng streams per layer) +
  whBuildInstanced (:1147, one InstancedMesh per asset, matrices written
  once; reads it.y || 0 — THE HEIGHTFIELD HOOK, see 3.1) + the gate:
  whScatterPlan returns empty when cfg.scatter === false
  (region-manager.js:719) — C currently has scatter:false (CONFIG.js:477).
  Existing scatter params are A/B-tuned: ringHosts list, atTreeRing
  (whBushSnare), freeBushes 20, grass 220, bushSway etc.
- DIRT PATH (Round: Nicko's A-order): buildDirtPathCanvas
  (region-manager.js:544-595: 128px canvas, packed-dirt umber 0x5a4a33,
  mud 0x463a27, pebbles; seeded whRng(78002024)); whPathCenterX +
  whDistToPath (1m-step polyline distance, region-manager.js:598-610);
  the ribbon mesh + DP.pathBand keep-out in the scatter clear radii
  (CONFIG.clear.pathM 6). DP = CFG.world.dirtPath, gated
  DP.regionId === regionId (region-manager.js:724) — A-only today.
- HEIGHTFIELD FEED (CC-C4): WH_GROUND.has/.heightAt/.footY (wh-ground.js);
  game.groundYAt; prop feed pattern whGroundFeed(regionId, x, z,
  propFootR) = min ground under footprint center+4 pts
  (region-manager.js:1326 area). The Stone assembly y-feed landed CC-C4.
- CULL (CC-C3): cullLists + cullProps(regionId, x, z) per-frame on
  regionC props (cullDistanceM 170 / cullShowFrac 0.92, CONFIG.js:536-537).
  SCATTER INSTANCED MESHES ARE NOT IN THE CULL LIST (they pre-date it;
  whole-mesh frustum culling only, region-manager.js:1142-1146) — the
  flora pass must join the same visibility discipline (see 3.3).
- B3 WAYMARKER: art-direction/3d/assets/biome_library/b3-waymarker.glb
  (kit prop; manifest id family 'b3-waymarker' — CHECK the manifest's
  logical id (assets.js map) before writing rows; typo law: use the
  manifest key EXACTLY, grep first, the builder MUST re-grep).

## 2. VERIFIED ASSET INVENTORY (all on disk, byte sizes checked @ 23f2e3c)

| manifest id (typo law — verify each in assets.js) | file | size | role in C |
|---|---|---|---|
| moonbell | biome_library/m11-moonbell-pixelated.glb | 366K | pale bell-flower colonies (the floral accent) |
| bracken | biome_library/b6-bracken-pixelated.glb | 588K | fern patches in clearings |
| bushA | biome_library/wh-bush-a-pixelated.glb | 258K | bush body 1 |
| bushB | biome_library/wh-bush-b-pixelated.glb | 252K | bush body 2 |
| bramble | biome_library/wh-bramble-pixelated.glb | 4.0MB | thorny thickets (sparse, landmarks of thorn) |
| bushSnare | (Round G) wh-bush-snare-pixelated.glb | small | ring bushes at giant trunks |
| grassTuft | wh-grass-tuft-pixelated.glb | small | ground layer |
| leaves | biome_library/b6-leaves-pixelated.glb | 384K | leaf-litter clusters |
| pebbles | biome_library/b6-pebbles-pixelated.glb | 294K | gravel spreads |
| stonefrags | biome_library/b6-stonefrags-pixelated.glb | 306K | stone debris |
| mossBoulder | biome_library/m9-pixelated.glb | 1.2M | BOULDER FIELDS (varied scales) |
| stoneSingle | biome_library/b3-stone-single-pixelated.glb | 375K | standing stones |
| deadTree | biome_library/m18-dead-tree.glb | ~2k tris | NORMAL-SIZE dead trees (A/B size 8-9.85; age contrast) |
| waymarker | biome_library/b3-waymarker-pixelated.glb | small | road fork marker |

Builder re-greps assets.js for each manifest key BEFORE writing rows
(typo law; grey-stand-in on a typo'd id = the Oct-8 bug class). Any
missing key = report + skip that layer, never guess an id.

## 3. IMPLEMENTATION CONTRACT

3.1 SCATTER ON FOR C (CONFIG.js + region-manager.js):
- Set CFG.regionC.scatter to a C-TUNED params block (per-region scatter
  overrides: keep the block's SHAPE but resolve per-region — the cleanest
  path: CFG.scatter gains per-region override rows read by whScatterPlan
  via cfg.scatterOverrides || CFG.scatter; DO NOT fork the engine).
  Ancient-tuned PROPOSED values (all 'Nicko tunes'):
  - treesExtra.targetCount: forest_of_the_old_king: 0 (giant rows are
    hand-placed CC-C3; NO extra auto trees — the 55m spacing law holds;
    DO NOT add auto trees without the spacing assert on THOSE too).
  - bushes: ring at EVERY C giant (ringHosts += yewTree/witchwoodTree —
    already listed; verify the ring reads scale-aware: rings use the
    TRUNK radius = width*scale/2*TRUNK_RATIO — at scale 16-26 the ring
    radius must scale with the giant; check the trunk math accounts the
    giant scale, report the computed ring radii for a scale-26 giant),
    atTreeRing count [3,6] for C overrides, assets for C rings: [bushA,
    bushB, bushSnare] weighted.
  - freeBushes: forest_of_the_old_king: 40 (bramble 1, bushB 2, bracken 3
    weighted — clearings get bracken patches).
  - GROUND LAYERS (new small engine bit, declared): leaves + pebbles +
    moonbell as instanced layers the same way grass is (per-region counts:
    PROPOSED leaves 160, pebbles 120, moonbell 90 clustered near tree
    rings + clearings; cluster = groups of 3-8 within ~5m — moonbell reads
    as COLONIES, not singles). Keep the per-region override shape.
- HEIGHTFIELD SEAT (the load-bearing seam): whBuildInstanced already
  writes pos.set(it.x, it.y || 0, it.z) — the scatter plan must CARRY a
  y per instance: extend whScatterPlan to include y = the terrain height
  under (x,z) for C (WH_GROUND.heightAt — the exact seat, not footY:
  ground-cover instances are tiny, the exact seat is correct and cheap)
  when the region has a heightfield, else undefined (A/B unchanged).
  whScatterPlan is PURE (CONFIG-in, plan-out) — pass the height function
  in as part of meta (add meta.heightAt or a per-region height fn) —
  the plan stays testable/pure.
- CULL JOIN (3.3 discipline): instanced scatter layers for C get a
  per-layer visibility treatment: either (a) join cullProps per instance
  (IMPOSSIBLE cheaply — one InstancedMesh = one object; per-instance
  hide = instanceMatrix edits) — SO: (b) whole-LAYER culling: each
  scatter layer stores its instances' centroid + radius; the layer's
  InstancedMesh joins the per-frame cull as ONE object (hide when the
  PLAYER is beyond layerRadius + cullDistanceM — i.e. the layer is
  fully beyond fog-cull coherence), PROPOSED per C's geometry (C's
  layers span the whole disc: one layer = always partially visible →
  whole-layer cull never fires → acceptable v1: the layers ARE the
  draw-call-cheap form: ~5-7 InstancedMeshes total = ~5-7 draw calls).
  Builder decides + documents with the draw-call math; NO per-instance
  culling machinery this order.

3.2 BOULDER FIELDS + DEAD TREES (CONFIG.js props rows + region-manager.js
feed reuse — NO new code paths; props/footY/cull all landed):
- ~40 PROPOSED boulder rows: mossBoulder scales 1.5-6.0 (a couple of 8-10
  'king boulders'), stoneSingle scales 2-4 (~8 rows), stonefrags +
  pebbles as PROPS (scale 1.5-3) where clusters read (some rows), placed
  in the gaps between giants (55m spacing law is TREE-TO-TREE: boulders
  respect prop clearances + the tree trunk radius, not the 55m).
- ~24 PROPOSED normal deadTree rows: scale 8-9.85 (A/B size, the age
  contrast between giants), min spacing 30m to any tree/boulder (the
  dead trees are SUBLIMINAL, not another giant layer), same exclusion
  zones as CC-C3 (glade, lane, Stone breathing room 20m, rim 4m).
- ALL new prop rows: y lands via the CC-C4 prop feed automatically (rows
  carry x/z only; the feed seats them). Distance-cull: new rows join
  cullLists automatically (regionC props all in the list — verify).
- The typo law check on every asset id before writing.

3.3 THE KING'S ROADS (CONFIG.js + region-manager.js):
- GENERALIZE the A-path machinery to a per-region road list: CFG.roads = [
  { regionId: 'hold_outskirts', ...today's dirtPath fields unchanged
  (byte-identical rendering; keep CFG.world.dirtPath working or migrate
  it to CFG.roads[0] with the same fields — builder picks the smaller
  diff, documents) }, { regionId: 'forest_of_the_old_king', ... } ].
  The C road block (PROPOSED):
  - ROAD SPINE (glade -> Stone): polyline through the flat pocket then
    rolling to the Stone ring: waypoints PROPOSED: (0,-96) glade ->
 (2,-130) -> (-6,-170) -> (4,-215) -> (-3,-255) -> (0,-300) -> (0,-340)
 -> Stone south rim (0,-352). Sway: per-waypoint lateral sine jitter
 (amplitude ~6-9, period ~90) — WINDING, not a straight ruler line; the
 ribbon
    texture reuses buildDirtPathCanvas (new seed for C: 20261008).
  - THREE BRANCH ROADS at the Stone fork (the crossroads is AT the Stone,
    R-62.7: the Stone IS the crossroads centerpiece): ring road around
    the Stone pad (radius ~16 arc) then:
    - NORTH: (0,-382) -> (3,-420) -> (-4,-460) -> (5,-500) -> (2,-540) ->
      notch mouth at the rim (0,-596) PROPOSED heading true north.
    - EAST: (16,-366)-ish ring exit -> (60,-362) -> (100,-370) -> (150,
      -358) -> (200,-368) -> notch mouth (240,-366) PROPOSED heading east.
    - WEST: (-16,-366)-ish ring exit -> (-60,-360) -> (-100,-370) ->
      (-150,-357) -> (-200,-370) -> notch mouth (-240,-366) PROPOSED
      heading west.
    (All waypoints PROPOSED, Nicko tunes; the builder nudge-adjusts to
    the terrain: print heightAt along each road — a road that climbs a
    30° slope reads wrong; nudge waypoints to the gentler saddles,
    document the nudges. The NOTCH MOUTHS are the C4b carve points —
    mark them in comments for CC-C4b.)
  - UNLIT LAW: NO lanterns on roads (rows absent by construction); the
    road fork gets ONE b3-waymarker stone (scale ~2.4) at the south
    approach to the Stone ring (the ancient waymarker, PROPOSED) — a
    dead-reckoning aid, NOT a light.
  - WIDTH: road half-width ~2.2 (A's path reads DP.halfWidth — check its
    value; C roads at 2.2 half-width = 4.4m wide PROPOSED, a proper cart
    road vs A's footpath).
  - KEEP-OUTS: roads join the scatter rejection (pathM 6) + tree rows
    keep 8m from road centerlines (the C2 generation comment block
    pattern) + the camp edge path logic reads DP per region — CHECK
    camp.js's DP usage (camp.js:482-483 uses CFG.world.dirtPath +
    GEO.distToPath for A) — generalize to the region's road list so
    camp placement in C keeps the path band free (SMALL declared
    camp.js touch, exactly the DP read).
  - SCATTER + ROADS: the ground-cover layers (grass/leaves) keep
    pathPadM off the road ribbons (grass.rs:766-771 pattern per road).
- SOFT BLOCKERS at the 3 notch mouths: the roads END at the rim line
  (still inside the playable disc for C4a — C4b carves the notches);
  in C4a NOTHING blocks the road ends yet (the rim clamp already holds
  the player; the road just visibly stops at the rim). NO blocker toast
  in C4a (the rim is the blocker; C4b adds the notch + blocker when the
  road can actually exit). Document the C4b follow-up in the CONFIG
  comment block.

3.4 BUDGET + DRAW CALLS (self-check math, report):
- New InstancedMesh layers: ~6-8 (bushA, bushB, snare, bramble+bracken
  free bushes maybe one layer per asset, grass, leaves, pebbles, moonbell,
  bracken) + boulder/deadTree/waymarker are NORMAL props (draw call each,
  but they join cullProps: ~72 new props + the existing 153).
- Assert: C worst-case visible tris still under 2M (the CC-C3 worst case
  was 1.12M; add the new layers' worst circles + print the math).
- Instanced layers' matrices written once (no per-frame cost beyond the
  cull loop's ~225 items — still trivial).

3.5 BUNDLE + SERVING (standing law):
- node --check every edited JS (via the playwright driver node);
  python3 tools/build_v8.py from repo root; bundle in the SAME commit.
- Commit (author CaptainPickard <pickard.nicko@gmail.com>):
  'feat(cc-c4a): flora pass + king'\''s roads - C scatter ON (rings at
  giants, bracken/moonbell colonies, leaves/pebbles layers, free bushes),
  boulder fields + normal dead trees between ancients, winding unlit
  dirt roads glade->Stone + N/E/W branches (A-path machinery generalized
  to CFG.roads), waymarker at the fork, heightfield-seated instances,
  A/B byte-identical'
  + push origin feat/world-visuals immediately.
- Do NOT flip 8793 (IO-side). Report FLIP-HOST-SIDE-PENDING + sha.
- NO harness, NO headless browser, NO game run: syntax checks only.

## 4. SELF-CHECKS THE BUILDER RUNS (report contents)

1. node --check every edited JS.
2. Manifest-id grep table: every new asset id vs assets.js (typo law
   evidence).
3. Road-height table: heightAt along each road's waypoints (glade->Stone
   + 3 branches) — max slope along each road printed (should be gentle;
   nudges documented).
4. Ring-radius audit for the giants: computed trunk radius + ring radius
   for a scale-16 and a scale-26 giant (rings must read at the base of
   the giants, not at their ankles).
5. Worst-case visible tri assert vs 2M (print the math).
6. Road-exclusion sweep: zero scatter trees/bushes within pathM of any
   road centerline (assert + count).
7. A/B invariance argument (which paths changed for A/B and why
   byte-identical: the scatter gate + DP migration risk).
8. Bundle byte size.

## 5. ACCEPTANCE CRITERIA (Nicko playtests; A1-A7)

- A1 FLORA RICHNESS: bushes cluster at giant trunks (rings read at the
  base, scale-aware), bracken/moonbell colonies in clearings, leaf+pebble
  ground layers visible; the forest floor is no longer bare.
- A2 BOULDER FIELDS: varied-scale boulders + standing stones + stone
  debris fill the gaps between giants; normal-size dead trees visible
  (age contrast reads).
- A3 THE ROADS: a winding dirt road leads from the glade to the Stone;
  at the Stone it forks N/E/W; roads are UNLIT; the waymarker stands at
  the fork; roads follow gentle terrain (no road climbing a cliff); the
  north road visibly ends toward the rim (the future notch).
- A4 ROADS + FLORA COEXIST: no bushes/trees on the road; grass/leaves
  keep off the ribbon; camp placement respects the road band (path
  keep-out works in C).
- A5 HEIGHTFIELD SEAT: all flora/boulders/dead trees sit ON the terrain
  (no floaters on slopes, no buried rings).
- A6 PERFORMANCE: draw calls/framerate still fine (the instanced layers
  are cheap; Nicko's eyes + the builder's math).
- A7 A/B UNCHANGED: A and B look/behave exactly as today (A's dirt path
  + scatter + wall ring all byte-identical); the C door still gates
  (CC-C2 A1 quick re-test).

## 6. SCOPE CONTRACT

TOUCH: prototype/js/CONFIG.js, prototype/js/region-manager.js,
prototype/js/camp.js (ONLY the DP read generalization, ~2-4 lines),
prototype/builds/v8-playable.html (rebundle).
NOT TOUCH: js/wh-ground.js (read-only: the height feed),
js/region-defs.js, js/game.js (roads are region-manager + CONFIG; if a
toast/interact hook seems needed, STOP — none is in C4a), js/daynight.js,
js/save.js, js/player.js, js/enemy.js, js/corpse-loot.js, js/assets.js
(manifest unchanged — all assets already in the library; if a NEW
manifest row seems needed, STOP and report), index.html, style.css,
tools/*, docs/*, io/*, scratch/*, art-direction/*.
CRG IMPACT (baked per law, run 2026-10-08 @ 23f2e3c): impact --files
CONFIG.js region-manager.js wh-ground.js --depth 2 --max-results 12 →
**41 nodes directly changed, 0 nodes impacted within 2 hops, 0 additional
files**. camp.js adds ≤4 lines (DP read) — outside the run's file set,
flagged here per law.

## 7. IF THE SPEC MEETS REALITY AND DISAGREES

Obey the code's actual shape, land the INTENT, log deviations. Scope
violations to avoid: no new manifest rows (typo law: report, don't
guess), no per-instance culling machinery, no blocker toasts (C4b), no
game.js touch, no wh-ground.js touch. The scatter engine generalization
(per-region overrides) must NOT fork the engine: A/B keep their params
byte-identical.