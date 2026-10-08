# CC-C4 · Heightfield Landing — Region C walks on the hills (R-62.1)

Change-order brief, written 2026-10-08 by IO from docs/planning/62 §4
(heightfield program), docs/planning/63 CC-C4, the CC-C1 spike verdicts
(scratch/region-c-spike/SPIKE-LOG.md), and the R-62.6 ancient-forest
context. Base 1ef42b6 (CC-C3 landed), branch feat/world-visuals, worktree
/tmp/wh-worldfeat. ONE order at a time. C1 spike was playtest-approved by
Nicko (verdicts banked below). Merge to dev/main = Nicko's call only.
Always English.

## 0. WHY THIS ORDER

C's ground is a flat stub disc at y=-0.05 (CC-C2). This order replaces it
in C with the spike's displaced deterministic heightfield mesh (S=140,
~39.2k tris ≈ 2% of budget) and feeds its height grid to everything that
stands on the ground: player, enemies, props, corpses, camp deploy ghost +
built camp, mist plane anchor, camera floor. A/B stay EXACTLY as they are
(flat, y=0) — the whole program is per-region gated.

## 1. SPIKE-APPROVED NUMBERS (banked, spike log + Nicko playtest approval)

- Sampler: **B-TRI** — exact, ~0.08µs; reads the SAME cached height grid
  the mesh was built from, follows the same per-cell triangle split.
  Fallbacks: B bilinear (7e-15 max err), A analytic (0.147 max err — mesh
  can't represent the 5.6u finest wavelength). Raycast = DEBUG ONLY
  (1.3-3.2ms/call, never per-frame).
- Mesh: PlaneGeometry(560,560,S=140,S) rotateX(-π/2), vertex y =
  heightA(x,z), flatShading + vertex colors (moss 2c4424 → stone 8c7b5e by
  height), hemisphere + 1 directional, build ~27ms synchronous AT REGION
  LOAD, never on the fly. Mesh tris 39,200 (S=140; S=180 64,800 rejected —
  +65% tris for little gain).
- Terrain constants (carry EXACTLY into the game CONFIG, seed 1337):
  PLANE 560 (HALF 280), BASE_WAVELENGTH 45, OCTAVES 4, LACUNARITY 2.0,
  GAIN 0.45, H_MAX 5.0, N_LO 0.22, N_HI 0.79 (p1/p99), spawn pocket
  FLAT_R 25 / FLAT_BLEND 20 / FLAT_H 0.4 (flat around C spawn (0,-96);
  heights: p50 2.61 p90 4.03 p99 4.96 max 5.00).
- Slopes: p50 4.7° / p90 9.0° / p99 12.9° / max ~18-19.5° (faces).
- climbFactor: ship 0.6 (~31° run / ~42° walk cap — mostly unbinding
  safety net; spike demo's 0.2 was just for visibly testing blocking).
  KNOWN QUIRK (spike finding, do not fix blind): with the speed-scaled
  formula a WALKING actor can climb steeper than a RUNNER. Acceptable
  v1; a slope-angle cap is a possible later refinement, NOT this order.

## 2. LOCKED RULINGS THIS ORDER RIDES (unchanged)

- R-62.1 real heightfield: gameplay walks on SAMPLED heights (this order).
- R-62.6 ancient forest: 153 props on the full disc — now they SIT ON the
  heights (y = heightAt(row) + their ground offset; the Stone assembly's
  pieces rise with the terrain — doc 63's "rises with the heightfield in
  CC-C4" closes here).
- R-62.2 r280 disc at (0,-366) — the 560x560 plane fully covers it
  (spans z -646..-86).
- Tutorial law NO-TOUCH: daynight.js, camp.js menu/beginCycle wiring are
  not touched (camp.js: ONLY the y-feed for the deploy ghost + built
  pieces + a y-transport on re-load if needed — declared below).
- A/B byte-identical behavior: every heightfield touch is behind a
  per-region gate; regions without a heightfield run exactly today's code.
- Enemies never cross (D2): unchanged this order (C has no enemies).
- The C2 door machinery (window, gate at the line, suspension) is NOT
  touched: the door approach on B is flat B ground; C's door-side glade
  sits in the FLAT POCKET (see 4.2) so the crossing stays on flat ground
  at every phase of this order.

## 3. VERIFIED STATE BLOCK (census @ 1ef42b6; line anchors drift — RE-GREP)

- C ground build: region-manager.js:1413 area — ground.position.set(
  region.center.x, region.cfg.groundY || 0, region.center.z); disc build
  CircleGeometry(whVisualGroundRadius, 48) ~:1213 family; CC-C3 added
  visualGroundMinRadius floor (cfg row, region-manager.js:1491 area) and
  cullProps (region-manager.js:1544, called :1597 from the frame path).
- Player: game.js:1146-1157 clamp path (clampPlayer → pushOutOfProps →
  holdAtLockedDoor); player root at y=0 today (game.js:2184 area: pBody
  y offset = -(groundMinY*scale) — the GLB floor pin, P0-1 pattern).
- Enemies: enemy.js root.position.y = 0 (enemy.js:163) + the
  groundMinY pin (region-manager.js:1490-1492, eBody build); corpseFinalY
  measured at death end (enemy.js:161-169, -finalMinY + 0.01) and read by
  corpse-loot.js:144.
- Props: obj.position.set(p.x, p.y || 0, p.z) region-manager.js:1453;
  stumps tObj.position.set(sTree.x, 0, sTree.z) ~:1466; Stone pieces
  arch.position.set(A.x, 0, A.z) ~:1270 (y=0 hard-coded family).
- Camp: camp.js y surfaces — pieces at .y tweaks (:58), ghost rotation
  only (:409), obj.rotation on build (:120, :570) — today flat y=0
  implicit. Camp edge check region-aware (CC-C3, camp.js:480-483).
- Mist plane: mistCfg.y row (region-manager.js ~:1435); C2's y=-0.05
  groundY row must be SUPERSEDED by the mesh (delete or repurpose the
  row; the build for C uses the heightfield path — see 4.2).
- Save: player x/z only (+regionId); y is derived — NO schema change
  (doc 63:87). Load re-derives y from the sampler (camp restore /
  player restore use the same feed).

## 4. IMPLEMENTATION CONTRACT

4.1 TERRAIN CORE — NEW FILE prototype/js/wh-ground.js (the only new file):
- The C1 spike CORE, productionized: hash lattice (SEED 1337), fBm 4
  octaves (base wavelength 45, lacunarity 2.0, gain 0.45), remap
  clamp((n-0.22)/0.57)*5, spawn pocket flattening (r25 / blend 20 /
  h 0.4), grid build at S=140 (Float32Array), the THREE mesh builder
  (PlaneGeometry displaced, vertex colors, flatShading), and the
  B-TRI sampler (exact per-cell triangle split, no raycast in any
  gameplay path; C raycast exists only behind a debug flag).
- API shape (all on window.WH_GROUND): .has(regionId) → true only for a
  CONFIG-listed heightfield region (regionC only, see 4.2);
  .build(regionId, center) → builds grid+mesh once (synchronous ~27ms at
  region load, cached; repeated calls return the cache);
  .heightAt(regionId, x, z) → B-TRI y in WORLD coords (subtract center:
  C-local (x, z-(-366)) before the grid lookup — document the mapping);
  outside the region's disc → 0; .mesh(regionId) → the mesh (added to
  the region group by the caller);
  .debugRaycast(regionId, x, z) → dev only.
- Grid hash determinism assert: build regionC twice, identical Float32
  grid (the spike's c5a19f53 hash at S=140, seed 1337) — assert at DEBUG
  level, log once.
- NO modules: classic script, load order AFTER CONFIG.js BEFORE
  region-defs.js (index.html script order). The BUNDLE (build_v8.py)
  must include wh-ground.js in the concatenation (verify the build tool
  reads the script order from index.html — check tools/build_v8.py and
  add the file to whatever manifest it uses if it has its own list; this
  is a TOOLS change ONLY IF build_v8.py hard-codes the file list —
  permitted, declared).

4.2 C GROUND SWAP (region-manager.js):
- The C ground build: if WH_GROUND.has(regionId) → build mesh + add to
  the region group at (center.x, 0, center.z); ELSE today's flat disc
  path (A/B, untouched). The flat-disc groundY -0.05 row for C becomes
  DEAD on this path (keep the row for A/B semantics; comment it).
- visualGroundMinRadius still caps the VISUAL disc for fog/edge (it stays
  exactly as landed CC-C3 — the heightfield mesh at 560x560 covers beyond
  the visual radius; if the spike mesh's edge could show through fog
  before visualGroundMinRadius, keep the flat skirt ring OUTSIDE the
  mesh edge at the rim color, PROPOSED — builder decides from geometry,
  documents the decision).
- MIST plane for C: anchor at heightAt spawn (0.4 + mistCfg height offset
  if the mist rides the ground — PROPOSED rows; A/B unchanged).

4.3 THE Y-FEED (game.js — the load-bearing seam):
- Add ONE helper used by every grounded system:
  groundYAt(x, z) = WH_GROUND.has(activeId) ? WH_GROUND.heightAt(activeId,
  x, z) : 0. Expose on game + on WH_DEBUG.
- PLAYER: after the existing clamp/push/door sequence (game.js:1146-1157,
  order preserved): player.root.position.y = groundYAt(player.pos.x,
  player.pos.z) + player body offset (the existing P0-1
  -(groundMinY*scale) pin rides on top). SLOPE GUARD (the movement
  contract): before applying, if the heightAt delta along the movement
  direction exceeds climbableSlope(=tan(cap°) * moveDist) then BLOCK the
  move component (reuse the existing blocked flag pattern; roll still
  allowed — falls are not a cc-c4 mechanic). climb cap: CONFIG rows from
  the spike (climbFactor 0.6; capDeg rows PROPOSED — walk 42 / run 31
  equivalents per the spike's curve). Player STAYS on the flat pocket
  spawn: the pocket makes the spawn area trivially flat.
- CAMERA: game.js camera floor — camY = max(camY, groundYAt(player) +
  camMinAboveGround PROPOSED 0.8) so the camera never goes under terrain
  (verify the actual camera code shape first; apply minimally).
- ENEMIES: C has none in CC-C4, BUT the eBody build pin
  (region-manager.js:1490) + root.position.y (enemy.js:163) and corpse
  placement (corpse-loot.js:144 + enemy.js:161-169 corpseFinalY: add the
  ground-y into the corpse final placement) must READ the feed with the
  A/B=0 fallback so C's future enemies are correct-by-construction:
  root.position.y = groundYAt(e.pos) (guarded per-region; enemy.js body
  pin math unchanged).
- PROPS: region-manager.js prop placement rows take y from the feed:
  obj.position.set(p.x, groundFeed + (p.y || 0), p.z) — where groundFeed
  = the per-region height (A/B: 0) — SAME for stumps, Stone pieces
  (~:1270 arch y), lantern. The camp kit pieces: same feed (camp.js
  build path; ghost + pieces).
- MIST: 4.2.

4.4 CAMP IN C (camp.js, rider-scoped):
- Deploy ghost y = groundYAt(ghost x,z) per frame (the ghost already
  repositions; ADD the y). Built pieces: y from feed at placement time
  (bake into the site? NO — sites store x/z only (save.js camp rows);
  pieces re-derive y every build from the feed — C4 additive law: no
  schema change).
- Camp edge check unchanged (region-aware CC-C3); the FLAT POCKET also
  mostly guarantees camp placement stays in gentle terrain near the
  glade (the builder re-reads edgeM vs the pocket and documents).

4.5 SPAWNS + TRANSPORTS (game.js, small):
- C spawn row already z=-96 INSIDE the flat pocket (r25 → z -71..-121
  flat band around (0,-96)? CAREFUL: the pocket is LOCAL to the CENTER
  (0,-366) in the spike (FLAT_R around the grid center). In the GAME
  the "spawn" that must be flat is the ARRIVAL GLADE (0,-96) — the door
  deposit (cross at z=-88) is 2m past the plane at C-local... the pocket
  must sit at the ARRIVAL side: CONFIG row terrain.pocket = { x: 0,
  z: -96, r: 25, blend: 20, h: spawnPocketH } PROPOSED where
  spawnPocketH = heightAt-free constant 0.4 EXACTLY as spike FLAT_H
  (the glade is a pocket of calm); the Stone center (0,-366) gets NO
  pocket (it sits on hills PROPOSED — its ring pieces take heights from
  the feed; a FLAT RING pad under the Stone assembly PROPOSED: pad radius
  ~14, height = the unflattened heightAt(0,-366) — decided by builder
  from the terrain values, documented).
- The door->glade lane is inside/near the pocket: the C arrival walk is
  flat; hills start beyond the blend ring. (Verify against the real
  noise: the builder prints heightAt along the lane z -88..-121 — the
  pocket assert.)
- Region-cross transports: cross into C deposits at z=-88 (existing
  mapPositionAcross) — y derives from the feed automatically (no
  transport code needed; the door window sits inside the pocket band).

4.6 CONFIG ROWS (CONFIG.js, PROPOSED commented):
- CFG.regionC.terrain = { enabled: true, S: 140, hMax: 5, baseWavelength
  45, octaves 4, lacunarity 2, gain 0.45, nLo 0.22, nHi 0.79, seed 1337,
  climbFactor 0.6, stepSlopeCapDeg PROPOSED 45 (walk) — see 4.3,
  pocket {...}, stonePad {...}, meshColorMoss 0x2c4424,
  meshColorStone 0x8c7b5e }.
- Save schema: NO change (y derived; doc 63:87 stays).

4.7 BUNDLE + SERVING (standing law):
- wh-ground.js must pass node --check; CONFIG/region-manager/game/camp
  + any build_v8.py manifest change too.
- Rebuild: python3 tools/build_v8.py from repo root; bundle in the SAME
  commit as source.
- Commit (author CaptainPickard <pickard.nicko@gmail.com>):
  'feat(cc-c4): heightfield landing - C walks on the seeded terrain mesh
  (S=140 B-TRI exact sampler), y-feed to player/camera/enemies/props/
  corpses/camp, slope guard + camera floor, flat spawn pocket + Stone
  pad, A/B byte-identical'
  + push origin feat/world-visuals immediately.
- Do NOT flip 8793 (IO-side). Report FLIP-HOST-SIDE-PENDING + sha.
- NO harness, NO headless browser, NO game run: syntax checks only.

## 5. SELF-CHECKS THE BUILDER RUNS (report contents)

1. node --check every edited/created JS.
2. Determinism: build the C grid twice in node (measure via wh-ground's
   CORE export), print both hashes (must equal c5a19f53).
3. heightAt vs the MESH truth on 200 seeded points (B-TRI exactness
   assert, zero error) + the pocket assert (heightAt along the lane
   z -88..-121 at x=0 = flat 0.4 inside r25, blend zone smooth, hills
   beyond — print a short table).
4. Camera-floor clamp sanity (one synthetic frame: camY < ground+0.8
   raises to ground+0.8).
5. Worst-case slope walk: print max terrain slope along a seeded walk
   path vs the climb cap (the cap should almost never bind per the
   spike's slope table - print how often it WOULD bind in the walk).
6. A/B invariance argument (which code paths run for A/B and why they
   are byte-identical: the has() gate list).
7. Bundle byte size.

## 6. ACCEPTANCE CRITERIA (Nicko playtests; A1-A6)

- A1 HILLS VISIBLE + REAL: cross into C, the forest now ROLLS — walking
  up/down slopes works, the view rises and dips. The arrival glade and
  the door approach stay flat; hills begin past the pocket.
- A2 PROPS ON SLOPES: trees, stumps, Stone assembly all sit ON the
  terrain through the full walk (no floating trunks, no buried rings);
  the Stone ring reads ON its pad.
- A3 CAMP ON A SLOPE: deploy camp in C: ghost follows terrain height,
  firepit/bedroll/pegs sit on the ground, camp works (save/load keeps
  x/z and re-derives y — reload after camp deploy, camp still sits on
  the slope).
- A4 CAMERA + SLOPE GUARD: the camera never clips under terrain;
  walking a slope at run speed never lets you climb an impossible wall
  (and the cap almost never binds on natural hills).
- A5 A/B UNCHANGED: A/B still flat (y=0), all A/B systems identical
  (quick CC-C2 A1 re-test: fresh door still locked; CC-C3 A5: camp near
  B edge still refused today-style).
- A6 SAVE/LOAD: save in C on a slope, CONTINUE → still on the slope
  (y re-derived); death in C respawns through the camp machinery
  correctly (cross-region respawn + y).

## 7. SCOPE CONTRACT

TOUCH: prototype/js/wh-ground.js (NEW), CONFIG.js, region-manager.js,
game.js, camp.js, prototype/builds/v8-playable.html (rebundle),
tools/build_v8.py (ONLY IF its file list is hard-coded — declared change).
NOT TOUCH (read-only): js/region-defs.js, js/daynight.js, js/save.js,
js/player.js, index.html (unless script-order insertion is needed —
declared), style.css, docs/*, io/*, scratch/*, art-direction/*.
CONDITIONAL TOUCH, DECLARED: js/enemy.js — ONLY the y-feed seam
(corpseFinalY area enemy.js:161-169 + the root.position.y guard at :163
must read the feed with A/B=0 fallback). NO FSM/AI/combat edits — the
combat surface (phase FSM, stagger, hyperarmor) is not touched.
js/corpse-loot.js — the y-read seam only (corpse-loot.js:144 area).
CRG IMPACT (baked per law, run 2026-10-08 @ 1ef42b6): impact --files
CONFIG.js region-manager.js game.js camp.js corpse-loot.js --depth 2
--max-results 12 → **153 nodes directly changed, 0 nodes impacted within
2 hops, 0 additional files**. (wh-ground.js + enemy.js seams are new-file
/ pin-line edits; the graph result bounds the 5-file set.)

## 8. IF THE SPEC MEETS REALITY AND DISAGREES

Obey the code's actual shape, land the INTENT, log deviations in the
report. Scope violations to avoid: no A/B flat-path changes, no FSM/combat
edits in enemy.js, no camp menu/beginCycle changes, no save schema
change. If the index.html script order must change, the diff must insert
ONE line (wh-ground.js) and nothing else.