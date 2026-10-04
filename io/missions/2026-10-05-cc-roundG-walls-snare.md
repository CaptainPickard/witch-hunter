# ROUND G CONTRACT: tall walls + snare-bush tree rings (IO -> Claude Code)

You are implementing IO-approved Round G in /workspace/witch-hunter. Two
changes, one dispatch. Follow EXACTLY. No harness runs, no browser/game runs,
Nicko playtests. Static probes + renders only.

## Change 1: boundary walls 3x taller

CONFIG.boundaryWall (prototype/js/CONFIG.js, landed Round F) drives the wall
segment scale; today segments read ~2.4 m tall (sy factor in
prototype/js/region-manager.js whWallPlan / scratch/wall_mirror.py).
Nicko order: "3x their current height should suffice" so the camera cannot see
around/over them.

- Multiply the wall segment HEIGHT (Y) by 3 in the ONE CONFIG knob that
  controls it (target height or equivalent; find it, do not hardcode in
  region-manager). X/Z (length, thickness) stay UNCHANGED - the wall must not
  get thicker or longer.
- The wall plan geometry (segment positions, count, colliders r .45, arch,
  plugs) must remain byte-identical: after your change,
  `python3 scratch/wall_mirror.py <root>` must output the SAME numbers as
  before except the segment scale sy values (3x). Verify mirror determinism
  (two runs byte-identical) as in Round F.
- The gate arch (10.5 m tall, apex 6.8 m) stays as-is; walls just meet it
  taller now.
- Proof still (1): closeup of two wall segments + the ring line receding,
  showing the new towering height, plus the wide ring view. If the Y-only
  stretch of the vinestone GLB looks unacceptable (eg vine banding), report
  it as a watch item with the exact artifact you saw - do NOT deviate to a
  different scaling scheme on your own.

## Change 2: tree rings use Nicko's snare bush (already downloaded)

Nicko generated a bush on Meshy and ordered it to REPLACE the bulbous bush
models surrounding trees (the atTreeRing rings, currently wh-bush-a/b).

Already done by IO (do NOT re-download, do NOT spend Meshy credits):
- Raw GLB:      scratch/treegen/roundE/wh-bush-snare-meshy-raw.glb
- Thumbnail:    scratch/treegen/roundE/wh-bush-snare-thumb.png
- Meshy task:   01a1092f-3bdf-7461-86ad-9eaa081187cc (SUCCEEDED, account task)

Your pipeline (reuse the tree-variety toolchain, read each script's header
before use):
1. Tri-count + QA the raw: scratch/tree_gate.py checks (read the header for
   invocation) + scratch/tree_ortho.py renders front/side into
   scratch/treeqa/roundG/.
2. CRITICAL: the raw may be ~15-30k tris (user-generated, no poly target).
   The rings instance it ~430x across regions (~305 in A, ~128 in B).
   Decimate the snare bush to <= 3000 tris (use the repo's decimate path from
   the 3D pipeline - search tools/ and scratch/ for the proven decimation
   script; if none exists, a minimal trimesh decimation script in
   scratch/decimate_roundG.py, SIGNED with before/after counts, is acceptable).
3. Pixelate per the register law (512 NEAREST + 5-bit): use the same pipeline
   the E bushes used (tree_bake.py / scratch helpers - read headers; the
   NORMAL-map inject + texture treatment must match wh-bush-a exactly).
4. Land: art-direction/3d/assets/biome_library/wh-bush-snare-pixelated.glb
   (+ raw copy in raw/ and refs/ per the biome_library layout, keep the
   original Meshy GLB also under refs/ per prior rounds).
   KEEP wh-bush-a/b-pixelated.glb files in the repo (rollback = CONFIG edit).
5. CONFIG.scatter.atTreeRing.assets -> ['whBushSnare'] ONLY (rings swap to
   the snare bush; free bushes keep whBushA/whBushB; grass unchanged). The
   ring code must pick up any newly-needed MANIFEST entry in assets.js.
   Ring placement numbers may differ from Round E's (different footprint) -
   document the new counts in the report table. keepOut/corridor/spawn
   clearances and no-collider law (rings have r=0) all unchanged.
6. Determinism: the scatter mirror must produce identical counts on two runs.
   Report the new per-region ring counts explicitly.

## Commits (identity CaptainPickard <pickard.nicko@gmail.com>)

Same shape as prior rounds; per branch in this order:
- feat(assets): snare bush pixelated + QA (dev + feat)
- feat(world): 3x wall height + snare-bush tree rings (dev + feat)
- build: v7 bundle (worktree only)
Also commit: scratch/treeqa/roundG/, the decimation script (if written),
scratch/roundG-proof/, updated provenance docs (io/roundG-provenance.md),
and the wall_mirror.json + scatter mirror outputs if changed.
Do NOT push. Do NOT touch main, light.js, player.js, enemy.js, moveset.js,
or any .rigged.glb/.combat-*.glb, and never read/commit
scratch/.mixamo-credentials.txt or scratch/.mixamo-storage.json.

## Proof stills (exactly 3, into scratch/roundG-proof/)

Use the Round F renderer pattern (grounded placement, shadows off):
1. wall-height closeup (two segments + receding line, new 3x height)
2. wide ring view (the wall circle from inside, showing no sightline over)
3. snare-bush ring closeup: snare bushes ringing a young tree base, grass
   tufts near - the trunk-to-bush blend must read.

Vision-check each still yourself in the render loop (do NOT ping-pong through
IO). If a still looks wrong, fix the underlying placement/lighting and
re-render (this is within scope; re-renders are free).

## Hard laws

- NO Meshy submits of ANY kind (asset already downloaded; zero credits).
- NO harness, headless browser, or game-loop runs. Blender headless renders
  + esprima syntax-checks only.
- NO game-code edits beyond: the ONE CONFIG wall-height knob,
  CONFIG.scatter.atTreeRing (assets), assets.js MANIFEST entry, region-
  manager/roundF-pattern manifest reads if the code requires the new asset
  id plumbed (minimal edits, keep the Round E architecture intact).
- If a step fails twice on real errors: mark FAILED with the exact error,
  continue the rest, never fabricate.
- Budget: commit early and often; land work as it completes.

## Report format

End with: commits table (both branches), the new ring counts (per region,
before/after), wall mirror determinism result (must be byte-identical),
tri-counts of the snare bush (raw -> decimated), deviations list, watch
items for Nicko's playtest, and FAILED steps (or none).