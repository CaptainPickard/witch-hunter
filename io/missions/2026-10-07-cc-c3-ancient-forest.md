# CC-C3 · Ancient Forest Full Pass — trees (R-62.6), per-frame cull, fog discipline, Old King's Stone, camp-edge fix

Change-order brief, written 2026-10-07 by IO from docs/planning/62 §5.1
(scatter + fog + landmark), docs/planning/63 CC-C3 (+ the R-62.6 rider),
and Nicko's playtest ruling R-62.6 ANCIENT FOREST. Base a26e5ca (CC-C2
shell landed, serving verified). Branch feat/world-visuals, worktree
/tmp/wh-worldfeat. ONE order at a time. Merge to dev/main = Nicko's call
only. Always English.

## 0. WHY THIS ORDER

Nicko played CC-C2's shell: the forest works, but the trees must feel
ANCIENT — much bigger, much farther apart, room used. R-62.6 (binding):
tree scale band ~16-26 (rare specimens larger), stumps 2.4-3.4, minimum
tree-to-tree spacing ~55m. Sparse + massive, not dense + small.

Second problem this order solves for real: the scatter must cover the r280
disc WITHOUT blowing the tri budget. Each biome tree is ~30k tris (doc
61:147), no LOD, no instancing (doc 61:45) — so ~160 placed trees are
~4.8M placed tris. The 2M budget (doc 61:44) governs DRAWN (per-frame)
tris: the pass must place trees across the whole disc but DRAW only what
can be seen through fog (per-frame visibility cull by distance to camera).
This makes the ancient look cheap: scale is free, big spacing REDUCES the
count per visible area.

## 1. LOCKED RULINGS THIS ORDER RIDES

- R-62.6 ANCIENT FOREST (binding, supersedes CC-C2's first-pass look):
  scale band ~16-26 trees (rare up to ~30), stumps 2.4-3.4, min spacing
  ~55m between trees. All C tree rows regenerated to this band; CC-C2's
  8-ish-scale rows are replaced, not incrementally tuned.
- R-62.2 scale: r280 disc, center (0,-366) — already landed CC-C2.
- doc 61 laws that govern: 2M drawn-tri budget (44); props ~30k tris each
  (43), no LOD / no instancing (45); world-edge finding: fog hides the
  plane edge from spawn but not within ~60 units (CC-C1 finding) — the
  full pass must keep the disc edge invisible.
- No new tech beyond a distance-based visibility cull (draw-only-nearby for
  scatter props). No LOD system, no impostors, no instancing this order
  (CC-C3 scope per doc 63: scatter + ledger + fog; those are later orders
  if needed).
- A/B untouched (byte-identical behavior; the cull is a C-scatter feature,
  NOT a rewrite of A/B prop paths).
- Tutorial law / camp law files: camp.js is touched ONLY for the edge
  check (rider, below) — the menu / beginCycle wiring is NOT TOUCH.

## 2. VERIFIED STATE BLOCK (census @ a26e5ca; line anchors drift — RE-GREP)

- C rows: CFG.regionC CONFIG.js:468+ (center {0,-366}, groundRadius 280,
  groundY -0.05, scatter false, propCullM 150, props ~141 rows hand-placed
  scale ~8-10). CC-C2's comment block above props documents its generation;
  this order REWRITES that block + rows for the ancient band.
- A/B: regionA CONFIG.js:157 area, regionB CONFIG.js:368 area; per-region
  scatter only lands via C paths; A/B prop render path unchanged.
- Prop build: props built per region by region-manager.js (GLB instances;
  the C build path landed CC-C2 with per-region disc build at
  CircleGeometry(whVisualGroundRadius(regionId), 48)
  region-manager.js:1213 family + the regionC branch).
- Cull surface: props are static per region today (no per-frame prop
  visibility pass has existed before CC-C3). Region manager has a per-frame
  update; player position available. FPS counter exists (index.html:19,
  always on) — ledger numbers read off it.
- Camp edge check: camp.js measures distance from the ORIGIN (verified
  builder finding, CC-C2 report): deploying a camp in C is refused as
  'edge'. camp.js owns placement edge logic; the ACTIVE region's center +
  groundRadius are on WH_REGION_DEFS.regions[activeId] (CC-C2 landed
  center/groundRadius fields makeRegion region-defs.js:25-40) — fix reads
  the region def instead of the origin. A/B: center null → falls back to
  today's origin behavior exactly.
- Old King's Stone furniture (CC-C3 scope, doc 63:68-74): m3 statue + m1
  gate pair + boulders ring at region center. Assets exist (doc 61:147
  biome library; regionB already places m3/m1 rows — CONFIG.js:380+ block,
  churchArchway/churchCornerButtress rows are the mirror pattern).
- Ground canvas: C-local painter (CONFIG.groundColor 0x1e2319 loam /
  groundColor2 0x2c2a1d umber / groundSeed 1662061217) landed CC-C2;
  ancient palette tweaks are PROPOSED rows in this order's CONFIG only.
- Bundle/build: tools/build_v8.py; node syntax checks via the playwright
  driver node. Serving: IO-side flip after gate review (builder does not
  flip).

## 3. SCOPE CONTRACT

TOUCH (the ONLY files this order may modify):
- prototype/js/CONFIG.js          — regionC props rewrite (ancient band),
                                    propCullM + cullDistanceM + fog rows
                                    tweaks + Old King's Stone assembly rows
                                    + camp edge rows (PROPOSED, Nicko tunes)
- prototype/js/region-manager.js  — per-frame scatter visibility cull for
                                    C's props (distance-to-camera, hysteresis
                                    low-cost) + Old King's Stone build path
                                    (kit assembly on the stub ground, rises
                                    with CC-C4 heightfield) + any C-scatter
                                    build-path adjustments (no A/B changes)
- prototype/js/camp.js            — ONLY the edge-check fix (rider):
                                    region-aware center/radius, A/B fallback
                                    to today's origin behavior byte-identical
- prototype/builds/v8-playable.html — rebuilt bundle (same commit)
NOT TOUCH (read-only): js/region-defs.js (no conn changes this order),
js/game.js (door/gate/interact landed CC-C2; the cull lives in the region
manager), js/daynight.js, js/player.js, js/enemy.js, js/save.js,
js/leveling.js, js/icons-data.js, js/assets.js (assets manifest unchanged —
tree GLBs are loaded), index.html, style.css, tools/*, docs/*,
art-direction/*, io/*, scratch/*.

## 4. CRG IMPACT (run 2026-10-07 @ a26e5ca, baked per law)

impact --files CONFIG.js region-manager.js camp.js --depth 2 --max-results
12 → status ok: **50 nodes directly changed, 0 nodes impacted within 2
hops, 0 additional files affected**. If the builder needs any file outside
Section 3's TOUCH list, that is a spec violation (Section 8).

## 5. IMPLEMENTATION CONTRACT

5.1 ANCIENT SCATTER (CONFIG.js + region-manager.js):
- Replace ALL CFG.regionC.props tree rows with the ancient band:
  ~70 trees PROPOSED (yewTree ~55% / witchwoodTree ~45% EXACT ids, typo
  law), scale 16-26 (a handful of ~28-30 'king specimen' giants PROPOSED
  ≤6 rows), ~20 stumps scale 2.4-3.4. Keep rows hand-placed style
  (generated once offline, seed documented in the comment block, then
  pasted — same pattern as CC-C2's comment, new seed documented).
- MIN SPACING ~55m tree-to-tree (builder self-checks the generated rows
  with a quick node script before pasting: assert no pair < 55 apart;
  print the actual min). Keep the existing exclusion zones: glade 10m
  (scale up: glade clear 18m PROPOSED — the lantern must not be under a
  giant), door->glade lane |x| < 6 && z > -110, lantern 6m, 4m inside the
  playable rim.
- propCullM: retune for the ancient look (PROPOSED ~260) — BUT its CC-C2
  semantic (generation bubble around spawn) is REPLACED this order: rows
  now cover the FULL playable disc (4m inside the rim; CC-C2's rows were
  a 150m bubble near the spawn glade — the center/Stone area was empty).
  The runtime cull (5.2) is the frame-budget mechanism; propCullM stays
  only as the generation contract (rows exist everywhere on the disc).
- Draw-tri budget row: with ~90 props placed and a per-frame cull at
  cullDistanceM (PROPOSED ~170 from camera), typical visible-tree count
  at any spot is small; the region-manager cull is per-frame distance
  check on instance objects (hide/show, no geometry rebuild). Ledger
  comment in CONFIG + one line in the builder's report: worst-case visible
  tris vs 2M (assert the worst case stays under budget, e.g. full circle
  of neighbors at cull radius count).

5.2 PER-FRAME VISIBILITY CULL (region-manager.js):
- For C's props (ALL of them — scatter trees, stumps, lantern, Stone
  assembly; regionC rows; do not touch A/B paths): each frame, props
  beyond cullDistanceM (PROPOSED 170) from the PLAYER position (stable
  anchor; camera trails the player at camDistance ~7) are .visible =
  false; inside → visible. Hysteresis: two bands (hide at R, show at
  R*0.92) to avoid pop-flicker at the boundary. Implementation must be
  cheap: precomputed prop list, per-frame distance check over ~90-100
  items is trivial; no allocation.
- FOG-CULL COHERENCE LAW: visible pop must be impossible — cullDistanceM
  must be >= the distance at which fog makes an object invisible (at
  density 0.033, ~120m; 170 > 120 gives margin) so a prop is fully fogged
  out before the cull could ever hide it visibly. Assert with numbers in
  the report.
- The cull applies to regionC props ONLY (A/B prop rendering untouched
  byte-identical).

5.3 STONE COHERENCE with the cull: the Stone sits at region center
  (0,-366) — 280m from the arrival glade, so it is BEYOND cullDistanceM
  on arrival and pops in as you walk the lane. That is FINE (fog hides
  it until ~120m; the cull is invisible inside fog) — REQUIRED behavior:
  the Stone must be no different from trees here; it fades in through
  fog before any visible pop (same coherence law). The approach-lane
  tree exclusion (|x| < 12, z > -300) keeps the silhouette clean.

5.4 OLD KING'S STONE (region-manager.js build path + CONFIG rows):
- Assembly at region center (0,-366): m3 statue (scale ~10-12 PROPOSED) +
  m1 gate pair (two gates flanking, rotY mirrored) + boulders ring
  (mossBoulder ~8-10, varied scale 1.5-2.5) on the stub ground. Existing
  kit assembly pattern (doc 61:147 m1/m3/m9 rows exist in regionB).
- It is PROP ROWS + placement math only; no new collision (props are
  walk-through; the ring is furniture). Rises with the heightfield in
  CC-C4 (a comment marks the y-anchor for the CC-C4 reader).
- Exclusion: glade lane + 20m clear of the assembly for trees (it must
  BREATH as a landmark; nothing within 20m of it, and it must be visible
  from the arrival glade lane: keep the lane z > -110 .. -300 |x| < 12
  PROPOSED free of trees so the silhouette reads on approach).

5.5 ANCIENT DRESSING + FOG (CONFIG.js rows PROPOSED, region-manager.js):
- Ground canvas palette tweak PROPOSED (deeper loam/Umber; the old-king
  floor is darker and more mossy than CC-C2's greens) — adjust
  groundColor/groundColor2 rows.
- Fog discipline (doc 61 world-edge finding): C fog density stays 0.033
  (d95 ~52m, edge-hidden from spawn); the disc edge (z=-646) must NEVER be
  visible: verify by geometry — from the C rim z=-86+1 walking north, the
  FIRST reachable fog-opaque depth at 0.033 is ~120m; the far disc edge is
  560m away → invisible. Assert in the builder report (numbers, not
  vibes). Optionally add far-fog second-row density PROPOSED if the
  builder finds the stub edge visible in the geometry math.
- King specimen giants: 3-6 rows near lanes/landmark approaches at scale
  28-30 — silhouette anchors (doc 61 landmark gap; the Stone is the local
  landmark, giants are the skyline rhythm).

5.6 CAMP EDGE RIDER (camp.js):
- ONLY the edge check: the check today computes the camp position's
  distance from the WORLD ORIGIN vs groundRadius - margin. Fix: read the
  ACTIVE region's center + groundRadius (WH_REGION_DEFS.regions[activeId]
  carries center/groundRadius after CC-C2; null center = origin, A/B
  fallback byte-identical). No other camp.js behavior changes: menu,
  beginCycle wiring, save/load, ghost preview all NOT TOUCH.
- Test surface: camp placement in C near the glade must pass (green
  ghost, allowed placement ~30m from the door lane); A/B placements
  unchanged (same refusals as today near A's rim, B's edge).

5.7 BUNDLE + SERVING (standing law):
- Rebuild: python3 tools/build_v8.py from repo root; bundle ships in the
  SAME commit as the source.
- Commit (git commit --author='CaptainPickard <pickard.nicko@gmail.com>'):
  'feat(cc-c3): ancient forest full pass - R-62.6 tree scale 16-26 (giants
  to 30) + ~55m spacing, per-frame visibility cull for C scatter, Old
  King'\''s Stone centerpiece assembly, camp edge check region-aware,
  fog/edge discipline verified'
  + push origin feat/world-visuals immediately.
- Do NOT flip 8793 and do NOT run tools/wh_release_flip.py (IO-side after
  gate review). Report 'FLIP-HOST-SIDE-PENDING' with the sha.
- NO harness, NO headless browser, NO game run. Syntax checks only:
  node --check on every edited JS (CONFIG.js, region-manager.js,
  camp.js) via /usr/local/lib/python3.12/site-packages/playwright/driver/node.

## 6. ACCEPTANCE CRITERIA (Nicko playtests; A1-A6)

- A1 ANCIENT FEEL: entering C from the door, the forest reads SPARSE +
  MASSIVE — giants on the approach lane, spacing feels park-like between
  trunks, stumps are big enough to matter. No CC-C2-scale trees remain
  (spot any tree that looks small: report it).
- A2 OLD KING'S STONE: walking the door->center lane, the Statue + gate
  pair + boulder ring is visible FROM THE APPROACH (silhouette through
  fog by ~100m out), stands clear of trees (20m breathing room), lantern +
  glade lane stay clear.
- A3 CULL INVISIBILITY: no tree pop in/out anywhere during normal walking
  (hysteresis works); the disc edge NEVER shows from any reachable ground
  (the builder's geometry assert backs this; your eyes confirm on a
  rim walk).
- A4 BUDGET: fps reads fine standing in the Stone ring (worst-case visible
  cluster), and in the densest point of the scatter the counter shows it
  (Nicko eyeballs + the ledger assert in the builder's report).
- A5 CAMP IN C: place a camp near the C glade — ghost GREEN, deploys,
  firepit/bedroll/pegs/camp save/load all work in C (C4 law intact).
  A/B placements unchanged (same refusals as today near A's rim, B's edge).
- A6 A/B UNCHANGED: A->B->A crossing identical; A/B prop rendering has no
  new cull behavior, no visual change; door gate still works (quick
  re-test of CC-C2's A1: with a fresh profile the door is still locked).

## 7. SELF-CHECKS THE BUILDER RUNS (report contents)

1. node --check on the 3 edited JS files.
2. The spacing assert (min pairwise distance >= 55 in the pasted rows) -
   print the actual min.
3. The cull-budget assert (worst-case visible tris vs 2M) - print the
   math.
4. The fog/edge geometry assert (edge visibility distance vs fog depth) -
   print the numbers.
5. Bundle byte size in the report.

## 8. IF THE SPEC MEETS REALITY AND DISAGREES

Any conflict between this contract and the real code (a line anchor that
moved, machinery that differs from the description): obey the code's
actual shape, land the INTENT, log the deviation in the final report. Do
NOT expand scope to fix unrelated things. camp.js changes beyond the edge
check are a violation; region-defs.js changes are a violation.

## 9. ASTRABOT LANE

None this order (existing kit assets only). The Old King's Stone is kit
assembly. Flag: if the statue reads wrong at scale 10-12 on playtest, a
dedicated centerpiece model is an Astrabot candidate LATER (Nicko's call).