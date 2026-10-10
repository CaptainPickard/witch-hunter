# ROUND I6 CONTRACT (FIX RUN): make the reach-trees visible on the walked path (IO -> Claude Code)

SHORT RUN. One change + build + commits. No Meshy calls (all assets exist).
No harness/browser/game runs. Read this whole brief first: everything is
already measured for you.

## Problem (Nicko, with screenshot)

Round I landed 3 reach-tree variants (reachTreeA/B/C). Swaps + scatter put
reach trees at: region A props - (21.93,-10.21), (-24.57,-3.33),
(22.57,-5.39), (-21.84,41.43); region B - (-31.2,-50.3), (-10.9,-55.8),
(-29.1,-72.5), (29.8,-76.9); scatter landed 2-3 further per region. TOTAL 8
placements, ALL 41-88m from the new spawn (2.5, 74) and NONE within 12m of
the walked dirt path corridor (path centerline x(z) = 1.6*sin(2pi(z-86)/34),
z 32..86). The path view is walled by yewTrees (~59 of them in A) on both
sides 7-11m off centerline. Result: Nicko sees zero change - "still the same
old ones" - because every cone-shaped silhouette in his view is a yew.

## THE FIX (exact, deterministic, no code changes)

Edit prototype/js/CONFIG.js ONLY on regionA props (identical edit on both
branches; region B keeps its swaps as-is):

INSERT exactly 6 prop rows after the existing line
  { asset: 'reachTreeA', x: -21.84, y: 0.00, z: 41.43, rotY: 3.70, scale: 8.53 },
with a 4-line comment "Round I6: 6 reach-trees deliberately placed along the
path corridor (Nicko: 'still no different trees' - none stood near the walked
path). Deterministic spots: even z-steps, alternating sides, 8-11m off the
centerline, clash-checked vs every prop collider."

The 6 rows (pre-computed by IO, clash-checked vs every region-A prop collider
- nearest existing prop is 3.3m+ away from each; trunk colliders auto-register;
snare rings auto-ring them via the existing ringHosts machinery):
  { asset: 'reachTreeA', x: 7.16,  y: 0.00, z: 38.00, rotY: 0.60, scale: 8.90 },
  { asset: 'reachTreeB', x: -12.57, y: 0.00, z: 42.50, rotY: 1.07, scale: 9.40 },
  { asset: 'reachTreeC', x: 7.29,  y: 0.00, z: 49.50, rotY: 1.54, scale: 9.10 },
  { asset: 'reachTreeA', x: -6.82, y: 0.00, z: 56.50, rotY: 2.01, scale: 8.90 },
  { asset: 'reachTreeB', x: 8.44,  y: 0.00, z: 67.50, rotY: 2.48, scale: 9.40 },
  { asset: 'reachTreeC', x: -7.29, y: 0.00, z: 66.50, rotY: 2.95, scale: 9.10 },

AFTER the insert, RE-RUN the clash check YOURSELF (script below) and if any
row sits < 3.0 m from an existing prop collider edge, nudge that row 1m
farther from the path centerline and re-check (report final positions):
- nearest-prop check: for each new row, min over ALL other region A props of
  hypot(dx, dz) must be >= 3.0.

## Verification (required, in order)

1. esprima parse CONFIG.js both branches.
2. python3 scratch/wall_mirror.py <root> - MUST be unchanged vs HEAD
   (145 ring / 603 colliders / same sy) and byte-identical over two runs.
3. python3 scratch/scatter_mirror.py <root> two runs byte-identical; counts
   may gain ring bushes (the new 6 trees get rings: expect +18-24 ring bushes
   in A); report the new counts per region.
4. Blender proof stills (scratch/roundI6-proof/, use the Round I renderer
   pattern): ONE still: camera at the NEW spawn (2.5, 74) at the game's
   camera height/pitch looking north down the path showing AT LEAST 3 of the
   new reach-trees visible as jagged horizontal-spread silhouettes among the
   yews. Vision-check it yourself; if fewer than 3 visible, adjust camera
   position slightly along the path (not the placements) and re-render.
5. Commit BOTH branches (CaptainPickard <pickard.nicko@gmail.com>):
   - feat(world): 6 reach-trees along the walked path corridor (Round I6)
   - build: v7 bundle (worktree only)
   Also commit scratch/roundI6-proof/ + updated io/roundI-provenance.md
   (add an "I6 addendum" section: why the first mix read as nothing - the
   path-corridor density fact from above).
   Do NOT push (IO pushes). Do NOT touch any other file. No main. No
   light.js/player.js/enemy.js/moveset.js/region-defs.js/no GLB changes.
   Never read/commit scratch/.mixamo-credentials.txt or .mixamo-storage.json.

## Report (<= 40 lines)

The inserted row list (final, post-nudge-if-any), clash-check results,
mirror verdicts, ring-count deltas, commits table, watch items (or none).
Commit early: land the CONFIG edit first, then stills, then build.