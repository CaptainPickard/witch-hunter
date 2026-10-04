# ROUND F CONTRACT: boundary wall ring + gate arch (IO -> Claude Code)

You are implementing IO-approved Round F in /workspace/witch-hunter: surround
BOTH explorable regions with a believable boundary (vine-on-stone), and place
a gate doorway on the A<->B path with a lantern hanging at its top so the
"entrance to the next area" reads at a glance. Same worktree/commit discipline
as Round E. The Meshy key is in your env as MESHY_KEY - never echo it, never
write it anywhere.

## Ground truth (IO-verified 2026-10-05)

- Branch layout: main checkout /workspace/witch-hunter on `dev` (@ 9cfc393);
  playtest worktree /tmp/wh-worldfeat on `feat/world-visuals` (@ a5f83d9).
  Identical edits + commit messages on BOTH; ONE build in the worktree only.
- World geometry (prototype/js/CONFIG.js + region-defs.js + region-manager.js):
  ONE disc centered at origin: CFG.world.groundRadius 90, playable rim
  groundRadius - playerMargin = 88.5. Region A = z > boundary.z (-25),
  region B = z < -25. Chokepoint: corridor x in [centerX -4, +4] through the
  boundary plane (CFG.chokepoint.width 8); the plane clamp allows crossing
  ONLY inside that corridor (region-manager clampPlayerPlane + insideChokepoint).
- Prop collision: region-manager.js whPropColliders + colliderRadius
  (TRUNK ratio 0.25 for trees/bushes); whMeetsCorridor exempts corridor
  props. Player push-out reads the circles each frame. Scatter trees (Round
  E) join via the plan param. Max hand-placed prop radial distances:
  regionA 62.2, regionB 84.8 (witchwoodTree at x -28.4, z -79.9, scale 9.8).
- b3-gate-pixelated.glb EXISTS in biome_library but is NOT in the assets.js
  MANIFEST (verify with grep -n "b3-gate" prototype/js/assets.js; if 0, add
  it). Rendered silhouette (IO vision-checked): gabled arch, thick outer
  frame, two side pillars, central passable opening ~60-70% of width; raw
  bounds X 1.65 / Y 1.14 / Z ~1.0.
- Meshy budget: balance at dispatch ~1309. Driver scratch/tree_meshy.py -
  ROUND F UPDATE THE GUARD FIRST: START_BALANCE 1309, CAP 60, MAX_TARGET
  2000 (same pattern as the Round E edit in commit 7edfaa4). Serial-only
  submits. ~15cr/mesh + ~3cr/ref. If 400/402 twice on a submit: mark
  FAILED, continue, never fabricate.

## Generate (Meshy, exactly 3, serial, ortho-QA each; pipeline = Round E's)

1. wh-wall-vinestone-a: a straight weathered dark-stone wall SEGMENT, one
   solid object, ~4m long x ~2.5-3m tall x ~0.6m thick feel, slightly uneven
   cap stones, chunky dark-green ivy/vine strands growing over the face (NO
   thin curling fronds - they i23d-fail; make vines thick/chunky), painterly
   pixel-art texture register like m5/m16.
2. wh-wall-vinestone-b: second wall segment variant - visibly different
   silhouette: one broken/crumbled top corner and denser vine coverage.
3. wh-lantern-hang: a small iron hanging lantern - compact cage body with
   glass panels and a top hook loop, single object, ~0.4-0.5m tall feel,
   dark iron (+ warm amber emissive glass in the pixelation pass like the
   round-D2 lanterns; you will attach it under the arch).
All: centered origin like the proven pipeline, ext XYZ reported.
QA: art-direction/3d/tree_gate.py + tree_ortho.py path used in Round E
(scratch/treeqa/roundF/ for renders). Iterate the ref once if a mesh fails
ortho QA; then mark FAILED and continue.

## Runtime integration (both branches, identical edits)

1. assets.js MANIFEST: add wh-wall-vinestone-a/b + wh-lantern-hang
   (-pixelated paths), and b3-gate-pixelated.glb if not present.
2. CONFIG.js new block CFG.boundaryWall = {
     radius: 87.5,
     segmentLengthUnits: 4.0,        // world meters per segment INSTANCE
     assets: ['whWallA', 'whWallB'], // MANIFEST keys
     jitter: { radial: 0.7, rotJitterDeg: 4 },   // seeded placement jitter
     chordZ: -25,                    // boundary-plane wall line
     chordFromX: 4.0,                // from corridor edge outward...
     chordToRim: true,               // ...to the ring intercept (x ~ +-83.8)
     arch: { asset: 'b3Gate', x: 0, z: -25, fitOpening: 5.2, rotY: 0,
         legs: { r: 0.6 }, plugCorners: true },
 lantern: { asset: 'whLanternHang', parent: arch apex underside,
            y: apex-0.15, scale: ~1.2 },
     lightSocket: { heightFraction: 'apex-based', intensity: 5.0,
                    offset: [0, 0] },
   // (registered in CONFIG.lightSockets under the arch asset key so the pool
   // light + flame card live at the arch apex, Round-D2 offset pattern).
   Tune exact numbers to read well; keep magnitudes. NO hand-listed
   segment tables - generation code only (seeded mulberry32, seed in
   CONFIG; deterministic = pure function of CONFIG).
3. region-manager.js wall builder: instances wh-wall-a/b around the FULL
   circle r 87.5 (step ~4m along the circumference so segments butt; alternate
   a/b; seeded radial jitter +-0.7 KEEPING >= 86.5) and along the chord line
   z=-25 from x=+-4.0 to the ring intercepts (same alternation). ALL segments
   via InstancedMesh (2 draw calls total, static, built once per region boot
   - actually WORLD-static: build once at boot, both regions' shared disc).
   Colliders: add per-segment circles (r ~0.45) to the collider table so the
   player cannot walk through the wall - use the existing scatter-plan join
   (plan.trees-style entries or a parallel wallColliders list; whichever
   keeps whPropColliders complete).
   EXCLUSION SWEEP (must): before placing each segment, reject/re-nudge if
   its circle intersects an existing hand-placed prop's collider radius +
   0.5m (the region-B far trees at r 78-85 are the known clash) - nudge the
   segment radius inward up to 1.0m, else drop that segment (max 2 drops,
   log counts). Canopy-over-wall overlap is FINE and desired visually; only
   trunk colliders matter here.
   Arch: instance b3Gate at (0,-25) scaled so its OPENING is >= 5.2m wide
   (measure the real opening fraction from the GLB, do not assume 65%). Two
   leg colliders at the arch's outer pillar feet + corner plugs (r ~0.5) at
   x ~ +-3.7 so the passable gap reads == the arch opening (the corridor
   x in [-4,4] - plugs must NOT sit inside the corridor's passing lane).
   Attach whLanternHang as a child of the arch group at the apex underside.
   The arch + lantern join the LOCK/socket + flame-card systems per
   CONFIG.lightSockets (round-D2 pattern: offset rotated+scaled).
   NOTE corridor exemption: legs/plugs must NOT be whMeetsCorridor-exempt -
   they physically bound the doorway.
4. Wall segments are WORLD-level (shared disc) - verify region-manager
   rebuild/dispose does not double-add them on region switches (build once,
   keep, or rebuild-safe deterministic - your call, document it).

## Commits (git identity CaptainPickard <pickard.nicko@gmail.com>)

Per branch, TWO commits:
- feat(assets): wh-wall-vinestone-a/b + wh-lantern-hang (Round F) - GLBs
  (pixelated + raw per Round E pattern), io/roundF-wall-provenance.md (task
  ids, credits, ext XYZ, arch opening measurement), treeqa/roundF renders,
  tree_meshy.py guard edit + log.
- feat(world): boundary wall ring + gate arch with lantern (Round F) -
  CONFIG.js + region-manager.js + assets.js + THIS CONTRACT FILE
  (io/missions/2026-10-05-cc-roundF-wall.md).
Then worktree only: python3 tools/build_v7.py; commit
"build: v7 bundle with boundary wall + gate arch (Round F)".
Do NOT push. NEVER echo the key; never commit .env/credential files.

## Verification (static only; NO harness, NO headless game, NO browser runs)

- esprima parse the 3 JS files on both branches after edits.
- Bundle greps (worktree build): 'wh-wall-vinestone-a' >= 1, 'b3Gate' >= 1,
  'wh-lantern-hang' >= 1, 'boundaryWall' >= 1.
- Placement determinism: extend scratch/scatter_mirror.py-style reporting -
  a small python mirror (scratch/wall_mirror.py) that recomputes segment
  count/placement from the same formulas and prints: ring segment count,
  chord count per side, drops+reasons, arch opening width, leg/plug
  positions. Run twice, identical output. Commit it.
- 3 stills max (Blender render, round-D2/E render pattern) into
  scratch/roundF-proof/: (1) wall segment pair closeup w/ vines, (2) wide
  shot: wall ring receding with a tree canopy overlapping it, (3) the gate
  arch front view with the hanging lantern + warm glow visible. renders.json
  alongside. Commit.

## Report (final message, markdown)

Assets table (asset | task id | credits | ortho QA | ext XYZ), arch opening
measured fraction + chosen scale, placement counts (ring, chords, drops),
collider totals added, determinism statement + mirror output counts,
deviations with reasons, FAILED steps with exact errors (or none), still
paths. No key values anywhere.

## Hard laws

- NO harness/browser/game-loop runs. Nicko playtests.
- Serial Meshy; CAP 60cr; never echo the key.
- Zero edits to light.js, enemy.js, player.js, anim.js, spells.js,
  gather.js, corpse-loot.js, touch-controls.js, moveset.js.
- Keep parked items parked (9 unhooked clips, bandit cape, idle stance,
  kick/cast/draw/sheath hooks, grass density, bush sizes - Round E knobs).
- If a step fails twice on real errors: mark FAILED with the exact error,
  continue, never fabricate.