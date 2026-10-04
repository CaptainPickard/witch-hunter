# ROUND E CONTRACT: world vegetation pass (IO -> Claude Code)

You are implementing IO-approved Round E in /workspace/witch-hunter: fill the
empty parts of both regions with trees, and add bushes + grass with NO
collision, bushes ringing tree bases so the fauna reads as one organic layer.
Worktree discipline, no-harness law, and the commit model are below. The
Meshy key arrives in your shell env as MESHY_KEY - never echo it, never write
it to any file, never log it.

## Ground truth (IO-verified 2026-10-05)

- Branch layout: main checkout /workspace/witch-hunter is on `dev`
  (@ 70bc19f); playtest worktree /tmp/wh-worldfeat is on
  `feat/world-visuals` (@ 96e7010). Make every change IN BOTH CHECKOUTS
  (identical edits + commit messages), then ONE build in the worktree ONLY.
- Meshy budget: 1426 credits. Driver scratch/tree_meshy.py (balance / t2i /
  i23d), SERIAL-ONLY submissions (one submit -> poll SUCCEEDED -> next),
  meshy-5 ~15cr/asset, TARGET_TRI cap 2000 per submit (provider cap), MISSION
  CAP: 130 credits this round incl bounded retries. Balance-check before
  EVERY submit (the script guards: floor logic inside). If a submit 402s or
  400s twice: mark FAILED, continue, never fabricate.
- Proven pipeline pattern (READ IT FIRST): scratch/astrabot-tree-variety-
  report.md = the M16-M19 round. t2i ref (1 ref per asset, darkwood
  painterly pixel-art register, NO trigger-word hazards: no thin curling
  fronds, no multi-object subjects, one Meshy task = ONE object) -> i23d ->
  ortho QA art-direction/3d/ortho_preview.py front+side -> pixelation +
  NORMAL injection exactly as that round did (see its scripts: scratch/
  tree_bake.py / tools/*) -> commit pixelated + raw glb like biome_library
  siblings (both files per asset, <name>.glb + <name>-pixelated.glb).
- Regions: A hold_outskirts (playable radius ~88.5, 127 existing props),
  B (62 props). Props + colliders live in prototype/js/CONFIG.js
  (WH_CONFIG.regionX.props) and prototype/js/region-manager.js
  (colliderRadius + TRUNK_ASSETS + TRUNK_RATIO 0.25, corridor exemptions).
  Existing tree assets: livingOak, witchwoodTree, birchTree, deadTree,
  deadTree2, ancientOak, hangingTree, twistedSapling (+ m19-birch-pixelated
  etc in biome_library). Existing undergrowth: thornbush, bramble,
  largeFern, deadShrub (m* and b6-bracken/leaves/mushrooms). USE these
  first - generation is ONLY for the gaps listed in "Generate".
- Player clamp + wall/doorway: OUT OF SCOPE this round (separate pass).
  Do not build boundary rings or arches.

## Generate (Meshy, exactly these 5, serial, ortho-QA each before i23d accept)

1. wh-bush-a: low dense darkwood bush, olive-sage, painterly pixel-art
   texture (512px NEAREST + 5-bit posterize after), single object, broad
   rounded silhouette, under-1m height feel.
2. wh-bush-b: second bush variant, slightly taller, sparser, paler moss
   tint. Distinct silhouette from bush-a.
3. wh-grass-tuft: small pale sage grass clump, gentle lean, single object,
   NO thin curling fronds (blades chunky, low-poly - thin fronds fail in
   i23d: they come back as shard storms).
4. wh-tree-birch-young: young slender birch (m19 is big/mature; this fills
   sparse mid-ground), pale bark, sparse canopy.
5. wh-tree-dead-young: small dead tree variant (m18/m7 are large), lean,
   bare twigs chunky.
All: centered origin like m5 (ymin ~= -height/2 handled by the pixelation/
bake step of the proven pipeline - region-manager ground-aligns at runtime),
report measured ext X/Z/Y in the provenance doc.

## Runtime integration (both branches, identical)

1. CONFIG.js: add the 5 new assets to the manifest mapping (assets.js
   biome_library entries: 'art-direction/3d/assets/biome_library/
   wh-bush-a-pixelated.glb' etc).
2. prototype/js/region-manager.js + CONFIG.js - new INSTANCED scatter layer:
   - CONFIG: WH_CONFIG.scatter = { seed: 20261005, per-region placement
     tables NOT enumerated by hand - parameters only }:
     { treesExtra: { minSpacingM: 7, targetCount: { hold_outskirts: 14,
       region B id: 10 } }, bushes: { atTreeRing: { count: [2,4],
       radiusFrac: [1.1, 1.6] (x trunk/canopy scale), avoidFront: true },
       freeBushes: 20, grass: 220 } } (tune numbers to taste, keep within
       these magnitudes).
   - Placement: deterministic seeded PRNG (mulberry32-style, seed from
     CONFIG). Trees-in-empty: sample positions inside playable disc,
     REJECT if: within 4m of any existing prop, within 5m of the spawn
     point, within 6m of the dirt-path centerline (compute the path sway
     x like region-manager buildDirtPath does - reuse its math), within
     8m of region connection chokepoint/gate, or collider-corridor zone.
     Trees get standard trunk colliders (join TRUNK_ASSETS behavior via
     the existing regex: young birch/dead trees match /tree|birch|sapling/).
   - Bushes ring tree bases: for EVERY tree (existing CONFIG tree props
     AND scatter trees), place [2,4] bushes around its base at radius
     [1.1,1.6]x the tree's collider scale, seeded angles, skipping the
     camera-front arc ONLY for hand-placed hero props is NOT needed -
     keep all rings; skip a ring slot if it would land inside another
     prop's collider radius + own radius.
   - Grass + free bushes: uniform random across the disc, same rejection
     rules (grass skips only path + spawn + gates + other colliders).
   - RENDERING (perf cap M-19): bushes and grass go through
     THREE.InstancedMesh (one InstancedMesh per asset per region, frustum
     NOT per-instance - set whole-mesh frustumCulled true; count = placed
     instances). New trees are normal cloned props like existing ones +
     their colliders registered in whPropColliders (scatter trees must be
     IN the collider table so enemies/pathing respect them - add scatter
     collider entries at placement time via a deterministic call, NOT
     hand-listed).
   - InstancedMesh pixelation: reuse the pixelated materials (the
     instanced mesh shares the pixelated GLB's material).
   - NO per-instance matrix updates per frame; build once at region build.
3. region-defs (WH_REGION_DEFS.regions[].cfg): add the new manifest assets
   to any preload lists if such per-region lists exist (check assets.js
   MANIFEST structure - biome_library assets are globally manifest-loaded;
   no per-region list change needed if so - verify, do not assume).

## Commit + build (git identity CaptainPickard <pickard.nicko@gmail.com>)

Per branch, TWO commits:
- feat(assets): generate wh-bush-a/b, grass tuft, young birch + dead tree
  (Round E)  -> new GLBs + provenance doc io/roundE-veg-provenance.md
  (per-asset: task id, credits, ortho paths, ext XYZ) + log jsonl update +
  treeqa renders.
- feat(world): instanced scatter layer - trees, bush rings, grass (Round E)
  -> CONFIG.js + region-manager.js + assets.js (+ any region-def edit).
Then worktree only: python3 tools/build_v7.py; git add
prototype/builds/v7-playable.html; git commit -m "build: v7 bundle with
instanced vegetation scatter (Round E)".
Also git add this contract file (io/missions/2026-10-05-cc-roundE-veg.md)
into the world commit, and scratch treeqa/ renders into the asset commit.
Do NOT push (IO pushes). NEVER commit scratch/raw-meshy intermediates or
.env/.meshy credential files (they do not exist in this repo; keep it that
way). NEVER echo MESHY_KEY into logs/reports/commits.

## Verification (static only; NO harness, NO headless game, NO browser loops)

- esprima parse: region-manager.js + CONFIG.js + assets.js after edits,
  both branches.
- Determinism proof: run the placement function twice (extract it into a
  small node-free self-test: python3 -c calling nothing - instead write a
  tiny JS snippet runnable by python esprima? NO - prove determinism by
  construction: document the seeded PRNG + why placement is a pure
  function of CONFIG; cite the code lines in the provenance doc. NO node
  on this box).
- Ortho renders committed for all 5 assets (front+side each).
- grep -c proof in the built bundle: 'wh-bush-a-pixelated' >= 1,
  'scatter' (the CONFIG key) >= 1.
- 2 scene stills (Blender, like Round D2's renderer pattern): one region-A
  ground patch with scatter trees + bush rings visible around trunks, one
  close-up bush-ring at a tree base with grass tufts - commit to
  scratch/roundE-proof/ (MAX 3 stills; IO vision-checks them).
- tree_meshy.py log ends with all 5 i23d-done SUCCEEDED entries; report
  total credits consumed (sum of consumed_credits if present, else
  balance delta).

## Report (final message, markdown)

Table: asset | task id | credits | ortho PASS | ext XYZ. Runtime: exact
counts placed per region (trees extra, bush rings, free bushes, grass),
InstancedMesh count per region, any placement rejections worth knowing,
deviations with reasons, FAILED steps with exact errors (or none), and the
two still paths.

## Hard laws

- NO harness/browser/game-loop runs. Nicko playtests.
- Serial Meshy only. CAP 130cr. Never echo the key.
- Zero edits to light.js, enemy.js, player.js, anim.js, spell files.
- Keep parked items parked (9 unhooked clips, bandit cape, etc).
- If a Meshy asset fails ortho QA twice: pick a different prompt angle
  once, then mark FAILED and continue with the rest - never fabricate.