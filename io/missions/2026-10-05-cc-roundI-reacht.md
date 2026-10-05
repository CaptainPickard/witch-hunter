# ROUND I CONTRACT: gothic reach-tree - replaces half the witchwoods (IO -> Claude Code)

You are implementing IO-approved Round I in /workspace/witch-hunter: ONE new
tree asset, generated on Meshy from IO's reference render and integrated to
replace half of the witchwoodTree placements. Goal (Nicko): many VERY HIGH,
SHARP, JAGGED branches reaching out through the skyline in ALL directions, so
spaces under these trees feel NEARLY ENCLOSED by their branches. Dark fantasy /
gothic horror register, matte, desaturated.

## Assets (Meshy budget 60 credits; measured balance at dispatch: 1267)

NICKO ORDER (mid-dispatch): 3 VARIANTS for variety - reachTreeA, reachTreeB,
reachTreeC. Serial-only submits. tree_meshy.py guard is set to Round H
(start 1285, cap 30) - UPDATE ITS HEADER: Round I = start <balance you
measure>, cap 60.

1. 3 REF IMAGES (plain t2i, ~3 cr each): one per variant, each distilled
   from the vision brief (do NOT re-analyze JPEGs), DIFFERING in silhouette
   character for variety:
   - refA (the reference match): "a massive ancient gnarled tree, single
     object, huge flared trunk with root wave buttresses, proud twisting
     limbs starting a quarter up, sharp elbows, needle-thin jagged tertiary
     branches reaching out in ALL directions through the sky, sparse bare
     fractal canopy of skeletal twigs, dark fantasy matte grey render,
     plain black background, centered, ground level camera"
   - refB (wider/lower, horizontal claw-spread): same base but "broader
     than tall, limbs reaching far sideways, wide sprawling reach, slightly
     drooping tips"
   - refC (taller/horizontal lean, sparser): same base but "towering narrow
     profile, sparse canopy, fewer but longer limbs, dramatic lean"
   Matte each like prior rounds (scratch/ref_matte.py). NO trigger words
   (no 'thin curling fronds', no 'dew', no multi-object phrasing).
2. 3 MESHES (i23d, meshy-5, 15 cr each): target_polycount 2000
   (MAX_TARGET guard). EACH ref -> its own mesh, serial.
   Per-mesh failure rule: if tree_gate fails (shard storm, largest piece
   < 60%) or vision-QA reads a blob/lollipop against its ref, ONE re-roll
   for that variant (<= 60 cr total). A second failure on the same variant
   = FAILED step for THAT variant: keep the better render, wire only the
   variants that passed (the 8 swapped rows then cycle among the passing
   variants), report.
3. QA: scratch/tree_gate.py + tree_ortho.py -> scratch/treeqa/roundI/
   (front/side, raw + decimated + pixelated). Vision-check YOURSELF: the
   skyline reading (limb reach in all directions) must be visible in the
   front ortho; the trunk must ground.

## Pipeline (proven path)

- Decimate to <= 3500 tris each (larger budget: this tree's silhouette IS
  the point; keep limb tips. Reuse scratch/decimate_roundH.py pattern,
  deterministic, signed before/after into a treeqa jsonl).
- Bake per register (512 NEAREST + 5-bit posterize; the bramble-style
  texel-per-face UV pickup is PREFERRED if the raw UV layout is fragmented -
  reuse scratch/bramble_bake_roundH.py as the base, adapt paths). The refs
  are grey matte renders: keep monochrome grey-brown bark; the 5-bit pass
  may add the faintest cold tint.
- EXACT ASSET NAMES: ids 'reachTreeA', 'reachTreeB', 'reachTreeC'. Per
  variant land: art-direction/3d/assets/biome_library/wh-reachtree-<a|b|c>-
  pixelated.glb, wh-reachtree-<a|b|c>.glb (decimated, textured),
  raw/wh-reachtree-<a|b|c>.glb (byte copy of the Meshy output),
  refs/wh-reachtree-<a|b|c>-ref.png.
- MANIFEST entries for all three (assets.js), biome_library layout per
  prior rounds.

## Placement: replace EXACTLY HALF the witchwood placements (deterministic)

- CONFIG props: 17 witchwoodTree rows. Swap ODD-indexed rows (0-based even =
  keep witchwood, odd = reachTree variant) -> 8 reachTree + 9 witchwood,
  rotY/scale/x/z UNCHANGED on swapped rows. Variant assignment on the 8
  swapped rows: cycle A, B, C, A, B, C, A, B in row order (deterministic,
  no RNG). Implement by editing the asset id on those 8 rows only (one
  list, no code changes).
- Scatter: CONFIG scatter treesExtra assets weights - ADD all three
  variants at equal weight next to witchwood:
  ['witchwoodTree', 1, 15.5, 18.5] stays, plus ['reachTreeA', 1, 15.5, 18.5],
  ['reachTreeB', 1, 15.5, 18.5], ['reachTreeC', 1, 15.5, 18.5]. MEASURED
  height: report each variant's raw ext Y and pick min/max around it
  (target 15.5-18.5 m in-world).
- Rings + no-collider law: every reachTree variant joins the RING-hosting
  assets (region-manager's colliderRadius regex 'tree|oak|...' treats them
  trunk-like (r*0.25) - VERIFY, and the ring code rings them like other
  trees). Ring asset stays whBushSnare.
- Mirrors: scatter_mirror + wall_mirror two runs byte-identical each; wall
  mirror expect UNCHANGED from Round H; scatter counts may shift (new mix);
  report per-region counts.
- Clearances (spawn/enemy/node/corridor/path/keepOut) all automatic via
  existing machinery - do not touch it.

## Commits (identity CaptainPickard <pickard.nicko@gmail.com>)

Per branch (dev checkout /workspace/witch-hunter, worktree
/tmp/wh-worldfeat), identical messages:
- feat(assets): wh-reachtree generated + QA (Round I)
- feat(world): reach-tree replaces half the witchwoods (Round I)
- build: v7 bundle (worktree only)
Also commit: scratch/treeqa/roundI/, scratch/treegen/roundI/ refs,
scratch scripts if new, io/roundI-provenance.md, the updated
tree_meshy.py guard header, io/missions/2026-10-05-cc-roundI-reacht.md
(the original brief). Do NOT push. Do NOT touch main, light.js,
player.js, enemy.js, moveset.js, region-defs.js, any rigged/combat GLB,
never read/commit scratch/.mixamo-credentials.txt or .mixamo-storage.json.

## Proof stills (exactly 3, scratch/roundI-proof/, Round H renderer pattern)

1. 01-variants-lineup.png: the three variants side by side, grounded, mist
   behind - the jagged skyline reach reading clearly on each, variety
   visible between A/B/C.
2. 02-reacht-enclosure.png: camera UNDER/NEAR one variant's canopy looking
   out/at - the 'nearly enclosed by branches' feel Nicko ordered.
3. 03-world-mix.png: a spot where a reachTree stands near a witchwood: the
   mix reading naturally (scale parity in-world).
Vision-check each; re-render on mistakes (free).

## Report (<= 100 lines)

Commits table (both branches), Meshy ledger (per-variant ref+mesh ids,
credits, before/after balance; measured start), tri counts per variant
(raw/decimated), the 8 swapped CONFIG rows (asset A/B/C + x,z list),
scatter weights, mirror determinism verdicts + per-region counts,
deviations, watch items, FAILED (or none; a failed variant notes which
variants shipped).