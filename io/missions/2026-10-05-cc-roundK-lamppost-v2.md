# ROUND K CONTRACT: replace the shattered lamp post (IO -> Claude Code)

SHORT RUN, ONE ASSET + WIRE. No harness/game loops. Nicko's screenshot shows
the current lantern-post GLB is visibly shattered up close (per-piece blocks,
floating shard pixels, jagged unstable lantern head, arm appearing broken at
the scrolls). The weld pass cannot fix a bad source asset. REPLACE IT.

## Budget + pipeline (proven path; serial Meshy only)

tree_meshy.py guard currently: START_BALANCE 1213 (Round I), CAP 60. Update
header: Round K = start <measured balance>, cap 40.

1. REF (t2i, ~3 cr) - prompt distilled from the vision read of Nicko's
   screenshot + the darkwood register (single object, matte, no trigger
   words - no 'thin curling fronds', 'dew', no multi-object phrasing):
   "a tall gothic wrought iron lamp post, single object, slender dark metal
   pillar with flared stepped base, elegant curved arm holding a hexagonal
   lantern with peaked cap and finial, weathered rusted iron, grim dark
   fantasy matte render, plain near-black background, centered, ground level"
   Matte it (scratch/ref_matte.py - check its current flags; --dark pocket
   mode after Round I's fix).
2. MESH (i23d meshy-5, 15 cr): target_polycount 2000 (MAX_TARGET guard).
3. QA gates (scratch/tree_gate.py + tree_ortho.py into
   scratch/treeqa/roundK/): largest-piece >= 60% AND tinyFar <= 20 AND
   vision-check the orthos YOURSELF: must read as ONE continuous post+arm+
   lantern, NO floaters. On gate failure: ONE re-roll from a corrected ref
   (2nd ref -3cr + mesh -15cr). Second failure = FAILED step: report, keep
   old asset in place this round, stop (do not ship a known-bad mesh).
4. Decimate <= 2500 (scratch/decimate_roundH.py pattern - welded positions,
   NOT the per-face path) + bake texture path via the SAME pattern as the
   snare/biome exports that produced CORRECT files: weld positions -> UV
   seam copies -> smooth normals by position + zero-normal repair ->
   posterize512 -> trimesh GLB export -> verify NORMAL attr + b'JSON' chunk
   + reload + ortho. (Do NOT use biome_pixelate.export()'s injector path -
   its +8 BIN-header bug is already filed; if you need its posterize only,
   import posterize512 directly like fix_bramble_roundI3.py does.)
5. Land: art-direction/3d/assets/church-kit/lantern-post-v2-pixelated.glb
   (+ .glb + raw/ + refs/ per the layout). KEEP the old lantern-post
   pixelated GLB files on disk (rollback = MANIFEST pointer flip).

## WIRE (CONFIG + code, minimal)

- assets.js MANIFEST: lanternPost -> the NEW -v2 path (one line edit; old
  entry retired to a comment).
- CONFIG.lightSockets.lanternPost: REMEASURE the socket for the NEW asset:
  glass/luminous head position from the GLB vertex bands (use
  scratch/lantern_head_probe.py header pattern - it documents the +8 BIN
  header gotcha) + offset [x,z] in glTF-local coords + heightFraction of
  the NEW measured height. Intensity stays 9.0. Report the measured values.
- CONFIG regionA/regionB prop rows keep asset id 'lanternPost' UNCHANGED
  (x/z/rotY/scale stay) - only the MANIFEST path changes what loads.
  scale may need +-10% adjustment to match the OLD post's in-world height
  (measure old vs new ext Y; report both, apply the correction factor to
  ALL lanternPost rows' scale in both regions).
- Collider: the regex treats it trunk-like already (r*0.25 of FOOTPRINT -
  verify the new asset's measured width feeds the same math unchanged).
- lightSockets offset: verify the head position against vertex bands (the
  Round D2 recipe); pool light must sit INSIDE the new lantern head.

## VERIFY (all required)

- treeqa orthos + closeup render of the NEW post with a test point light in
  the socket position: flame reads inside the head, light pool on the
  ground (the Round D2 recipe with the new asset), 1 still into
  scratch/roundK-proof/01-new-post-lit.png. Vision-check.
- esprima CONFIG.js + assets.js both branches.
- wall_mirror unchanged (should be untouched by these files); scatter mirror
  unchanged counts (ringHosts does NOT include lanternPost - verify).
- No GLB regressions: sha256 the 4 reach GLBs + bramble GLB before/after
  this run - MUST be identical (do not let the pipeline touch them).

## Commits (CaptainPickard <pickard.nicko@gmail.com>, both branches, same
messages):
- feat(assets): lantern-post-v2 generated + QA (Round K)
- feat(world): MANIFEST swap to lantern-post-v2 + socket remeasure (Round K)
- build: v7 bundle (worktree only)
Also commit scratch/treeqa/roundK/, scratch/roundK-proof/,
io/roundK-provenance.md, updated tree_meshy.py header, the original brief
io/missions/2026-10-05-cc-roundK-lamppost-v2.md. No push. No main. No
light.js/player.js/enemy.js/moveset.js/region-defs.js. Never read/commit
scratch/.mixamo-credentials.txt / .mixamo-storage.json. Do not modify the
reach/bramble GLBs (sha-check guard).

## Report (<= 50 lines)

Meshy ledger (measured start, ids, spend, end balance), ortho + gate results,
old-vs-new measured heights + scale factor applied, socket measured values,
mirror verdicts, sha-guard verdict, proof stills list, deviations, watch
items, FAILED (or none).