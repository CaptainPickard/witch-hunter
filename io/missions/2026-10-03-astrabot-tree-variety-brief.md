# ASTRABOT MISSION BRIEF - Tree variety assets for Witch Hunter
2026-10-03, from IO (change order: Nicko, "lets get astrabot on a variety pass")

You are Astrabot, running as a Claude Code print-mode builder session. This
brief is your complete contract. Repo: /workspace/witch-hunter, branch
feat/world-visuals (checked out here at /tmp/wh-worldfeat - ALL work happens
in this worktree, commit and push to feat/world-visuals).

## 1. Situation (measured 2026-10-03)

The playtest forest purged three shattered tree GLBs (committed cf82f1f):
- livingOak    was m4-pixelated.glb (biome_library) - DESTROYED: fragment cloud
- witchwoodTree was m6-pixelated.glb (biome_library) - DESTROYED: fragment cloud
- deadTree     was church-kit/dead-tree-pixelated.glb - DESTROYED: slivers + specks

Every playable tree in both regions is now the single healthy asset:
- yewTree = m5-pixelated.glb - GOLD STANDARD, intact (conical evergreen,
  ~28k tris, centered origin ymin=-0.95, ext X=1.01 Z=1.02 Y=1.89)

Visual proof of FAIL vs PASS (look at these first):
- scratch/treeqa/m4-front.png, m6-front.png, dead-tree-front.png = BROKEN look
- scratch/treeqa/m5-front.png = the quality bar
- (side views alongside each)

The forest reads monotonous. Mission: regenerate the three purged tree types
as NEW healthy assets so world dressing can use real variety again.

## 2. Deliverables (exactly 3 new tree assets, plus optional 1 bonus)

New files under art-direction/3d/assets/biome_library/ following the existing
naming convention (see m15-bandit-campfire-pixelated.glb, b3-waymarker...):

1. m16-living-oak-pixelated.glb   (+ raw m16-living-oak.glb)
   Broad deciduous oak: thick trunk, wide round canopy. This re-homes the
   purged livingOak role.
2. m17-witchwood-pixelated.glb    (+ raw m17-witchwood.glb)
   Witchwood: gnarled, tall, sparse pale-ish canopy, slightly wrong/organic.
   Re-homes witchwoodTree (region B Darkwood Edge).
3. m18-dead-tree-pixelated.glb    (+ raw m18-dead-tree.glb)
   Bare gnarled dead tree, no canopy, 2-3 crooked bare branches.
4. BONUS ONLY IF queue time allows: m19-birch-pixelated.glb (+ raw)
   Young birch/ash, slim trunk, light small canopy (understory variety).

Generation pipeline: it already lives in this repo at art-direction/3d/ -
meshy_driver.py + queue.json (Meshy API), regen_pipeline_v3.py,
biome_pixelate.py, bake_vertex_colors.py, verify_vcolors.py, glb_json.py.
Follow the SAME bake law that produced m5: raw mesh as-is, color pixelation
only (512px atlas NEAREST + 5-bit posterize), no geometry post-processing.
Darkwood canon palette: dark bark, muted olive/ash canopy tones. No accent
colors on trees (accents are reserved: cyan magic, amber human fire, red pact).

## 3. QA gate you must pass per asset (self-QA, offline, no browser)

For EVERY produced -pixelated.glb:
a) Component analysis (tools: python3 + trimesh, pattern = scratch has
   tree_diag.py from IO - reuse or rewrite): largest connected component
   must hold >= 60% of total faces AND tiny-far shard count (components
   <10 faces with centroid dist > 1.0 from origin) must be <= 20.
   The shattered predecessors were: m4 largest comp 281/27380 faces,
   537 tiny-far shards. Those numbers are the failure signature you MUST be
   far from.
b) Ortho render QA: art-direction/3d/ortho_preview.py <glb> front.png
   side.png (matplotlib installed). Iterate until front+side views read as a
   coherent tree silhouette comparable to m5 - no floating debris, no holes.
   Save renders to scratch/treeqa/m16-front.png, m16-side.png etc. (commit them).
c) Origin convention: centered like m5 (ymin ~= -height/2). Report measured
   ext X/Z/Y + ymin per asset in the provenance doc.
- Budget discipline: bounded retry; if the Meshy queue stalls, log the job id
  in the provenance doc and continue with the next asset; do not burn the run
  blocked on one job.
- Meshy provider laws (from the 10-01 R7 run, do not rediscover the hard way):
  submits are SERIAL-ONLY - never two task submissions back-to-back; submit,
  confirm the task_id, then the next submit only after the previous returned.
  MESHY_KEY is provided by IO in your shell environment at dispatch (key
  rotated 10-01; never echo it, never write the key value into any file,
  report, manifest, or commit). meshy-5 costs ~15
  credits/asset; TOTAL MISSION CAP 160 credits (4 assets x ~15 + bounded
  retries); if you exceed the cap, stop generating and report.
  If a submit rejects on polycount, cap target_tri at 2000 per submit (the
  R7-observed provider cap) and let the local pipeline reach the detail goal.

## 4. Hard laws

- NO HARNESS. Absolutely no headless browser runs, no Playwright/chromium
  smoke tests, no automated gameplay validation of any kind. Nicko's manual
  playtest is the ONLY acceptance test. Your QA = the offline mesh + ortho
  render gates above, nothing else.
- ZERO game-code edits. Do not touch prototype/js/* or prototype/* at all.
  IO owns manifest/CONFIG integration. If you believe a code change is needed,
  write the recommendation in your report instead.
- Do not overwrite or delete ANY existing asset files (m5 stays untouched,
  m1-m9/m15/b3 stay untouched). New filenames only, per section 2.
- Nothing outside: art-direction/3d/assets/biome_library/,
  art-direction/3d/docs/asset-manifest.md (append rows only),
  scratch/ (your working+QA files). 
- Worktree discipline: work ONLY in /tmp/wh-worldfeat on feat/world-visuals.
  Commit incrementally (raw+QA per asset is a good cadence) and push to
  origin feat/world-visuals after each. The worktree is truth: uncommitted
  work does not exist.
- Provenance: append one row per asset to art-direction/3d/asset-manifest.md
  (it lives at the 3d/ root - read its existing rows and match the format)
  with Meshy job id, tri counts, QA metrics.
- Write your final report to scratch/astrabot-tree-variety-report.md and
  keep your last chat message a short summary of assets landed + QA numbers.

## 5. REPORT format (in the report file)

Per asset: filename, Meshy job id, tri count, component stats (largest comp
faces %, tiny-far count), ext/ymin measurements, QA render paths, PASS/FAIL
per gate. End with: integration recommendations (manifest logical names you
suggest: e.g. livingOak -> m16-living-oak-pixelated.glb), any pipeline
friction, anything left undone and why.