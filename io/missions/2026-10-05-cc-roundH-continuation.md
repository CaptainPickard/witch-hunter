# ROUND H CONTINUATION (IO -> Claude Code): finish the dead run, ZERO research

The previous Round H agent DIED mid-run. His completed work is ON DISK in
/workspace/witch-hunter, UNCOMMITTED. Harvest it: do NOT redo, do NOT
re-run Meshy (ALL Meshy submits FORBIDDEN this run - ledger already spent
18 of 30 credits; balance 1267; any further Meshy call = contract violation).
Do not re-read the mission file for context; the facts you need are HERE.

## Already done by the dead run (verify ONLY, then commit AS IS)

- CONFIG.js: regionA.spawn = { x: 2.5, z: 74.0 } (computed, safety-checked by
  scratch/roundH-proof/spawn_probe.json: prop edge gap 4.88m, outside keepOut
  (1.941), nearest enemy 25.75m, 0 nudges) + cemeteryFog block
  (zone keepOut hold_outskirts, density 0.030, color 0x7f8ea6,
  rampStart 1.35, rampEnd 0.55). DO NOT RETUNE.
- game.js: cemeteryFogTick() O(1) smoothstep ramp + its call in the frame
  loop. DO NOT RETOUCH except syntax check (esprima).
- Snare recolor LANDED: art-direction/3d/assets/biome_library/wh-bush-snare-
  pixelated.glb now carries the two-tone COLOR_0 paint (scratch/treeqa/
  roundH/snare_color.jsonl last row = the signed landing record: canes
  srgb [40,40,32], roses srgb [136,104,104], rose_pct 45.9). Do not regenerate.
- Bramble raw: scratch/treegen/roundH/wh-bramble-meshy.glb (Meshy mesh,
  SUCCEEDED, task in tree_meshy_log; QA renders
  scratch/treeqa/roundH/wh-bramble-raw-front/side.png + gate.jsonl).
- Still 01-spawn-view.png rendered (scratch/roundH-proof/).

## YOUR remaining work, in order

1. DECIMATE the bramble: scratch/treegen/roundH/wh-bramble-meshy.glb ->
   <= 2500 tris, deterministic. Reuse/extend scratch/decimate_roundG.py
   (signed jsonl with before/after counts into scratch/treeqa/roundH/).
2. BAKE it: check if the raw bramble has a material/texture (the snare was
   geometry-only; brambles from the same account run normally carry one - if
   tree_bake.py works on it, run the standard register treatment; if it is
   ALSO geometry-only, use the flat-colour fallback path
   (scratch/snare_color_roundG.py pattern) with a dark tangled-briar palette
   (cane ~ #2e2a26, sparse dead-rose accents ~ #8d6d6a by local density) and
   REPORT which path ran. 5-bit posterize + 512 NEAREST either way.
3. LAND it: art-direction/3d/assets/biome_library/wh-bramble-pixelated.glb
   (+ raw copy under raw/, ref under refs/, per the biome_library layout).
4. WIRE it: assets.js MANIFEST 'bramble' entry (pattern: existing biome
   entries); CONFIG.scatter.bushes.free assets -> [['bramble', 1, 1.4, 2.0]]
   (keep the existing row format; free bushes swap wholesale; atTreeRing
   stays whBushSnare). KEEP wh-bush-a/b pixelated GLBs in the repo.
5. MIRRORS: run scratch/wall_mirror.py (expect UNCHANGED vs Round G) and
   scratch/scatter_mirror.py (free-bush footprint changed -> counts may
   shift; report per-region trees/ freeBushes/ grass and ring counts).
   Both determinism checks: two runs byte-identical each.
6. STILLS: 02-cemetery-fog-approach.png (camera on the path at the graveyard
   fence mouth, denser cooler fog pool visible over the cemetery) and
   03-bramble-snare-closeup.png (free brambles + a snare ring at a young
   tree base; two-tone roses vs dark canes must read). Use the Round H
   renderer already in scratch/ (roundH_proof_render.py / roundH_proof_
   scene.py - read their headers). Re-render 01 only if it is broken.
   Vision-check each still yourself.
7. SPARSE-EDGE NOTE for the still: the dead run's spawn_probe flagged
   spawn 3.78m off the path centerline (path halfWidth 2.7). That is the
   faithful midpoint of the wall-point and the lantern (which sits
   off-path) - Nicko's order. Keep it; put it in watch items.
8. PROVENANCE: io/roundH-provenance.md summarizing BOTH runs (dead run's
   ledger: measured start 1285, t2i -3, i23d -15, balance 1267, spent 18/30;
   your run: 0 Meshy credits).
9. COMMITS (identity CaptainPickard <pickard.nicko@gmail.com>), per branch,
   identical messages, dev checkout /workspace/witch-hunter first, then the
   worktree /tmp/wh-worldfeat (feat/world-visuals):
   - feat(assets): wh-bramble baked + integrated (Round H continuation)
     [assets GLB(s) + manifests + CONFIG swap + scripts + treeqa]
   - feat(world): south spawn + cemetery fog ramp + snare recolor (Round H)
     [CONFIG spawn/fog + game.js + the modified snare GLB + spawn probe +
     mirror JSONs + stills]
   - build: v7 bundle (WORKTREE only; verify grep counts for
     'wh-bramble-pixelated' >= 1 before committing it)
   Also git add io/missions/2026-10-05-cc-roundH-tone.md (the original
   brief) into the first assets commit. Do NOT push (IO pushes).
   NOTE: the worktree edits NOTHING yet - you are ferrying dev's landed
   state into feat: apply the SAME diffs there (file copy for assets + GLBs;
   re-edit CONFIG/game.js identically, or cherry-pick the dev commits if
   cleaner - your call, identical content required).
10. SYNTAX: esprima every edited JS file on both branches before committing.

## Hard laws

NO Meshy calls. NO harness/browser/game runs. No main. No light.js,
player.js, enemy.js, moveset.js, region-defs.js, no rigged/combat GLB.
Never read/commit scratch/.mixamo-credentials.txt or .mixamo-storage.json.
If a step fails twice: FAILED with exact error, continue, never fabricate.
Commit early; the run dying again must leave commits, not disk state.

## Report (<= 100 lines)

Commits table (both branches), bramble bake path (texture vs flat fallback),
tri counts raw->decimated, scatter mirror counts per region (+diffs vs
Round G), wall mirror verdict, determinism verdicts, deviations, watch
items, FAILED steps (or none).