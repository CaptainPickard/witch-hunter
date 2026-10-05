# ROUND L CONTRACT: gothic arm-hook lantern post v3 (IO -> Claude Code)

SHORT RUN. ONE asset + wire, replaces lantern-post-v2 (Nicko liked the OLD
arm-hook silhouette; v3 = arm-hook design, gothic styling, SOLID geometry).
No harness/game loops. No main. Commit early, both branches, NO push.

## Asset pipeline (proven path; serial Meshy only)

tree_meshy.py guard: Round K (start 1213, cap 40); balance now ~1195.
Update header: Round L = start <measured>, cap 40 (room for 1 re-roll).

1. REF (t2i ~3cr), single object, matte, NO trigger words (no 'thin curling
   fronds', 'dew', no multi-object phrasing):
   "a tall gothic wrought iron lamp post, single object, slender weathered
   dark iron pillar on a flared stepped base, ONE elegant curved arm
   reaching up and out from the pillar top, a hexagonal lantern cage hanging
   from the arm's hook by a small ring, peaked cap and finial on the
   lantern, grim dark fantasy matte render, plain near-black background,
   centered, ground level"
2. MESH (i23d meshy-5, 15cr): target_polycount 2000.
3. QA gates HARDER than prior rounds (the arm is the classic shatter point):
   scratch/tree_gate.py: largest-piece >= 90% AND tinyFar <= 5; PLUS a
   CONNECTIVITY check vs the OLD asset: count position-welded pieces of the
   pixelated result (scratch/piece_stats.py pattern) - must be <= 3 pieces,
   every piece within 2mm of shared vert (no floaters, same standard as K).
   If gate fails: ONE re-roll (-3cr ref -15cr mesh). Second failure = FAILED
   step: keep v2 in place, report, stop.
4. Bake + land (exactly the Round K recipe which produced a correct file):
   weld positions -> UV-seam copies -> smooth normals by position +
   zero-normal repair -> posterize512 -> trimesh GLB export (verify NORMAL
   attr + b'JSON' chunk type + reload + ortho front/side). DO NOT use
   biome_pixelate.export() inject path (+8 header bug filed).
   Land: art-direction/3d/assets/church-kit/lantern-post-v3-pixelated.glb
   (+ .glb + raw/ + refs/ per the flat+subfolder layout K used).
   KEEP v2 + old on disk (rollback = MANIFEST pointer).
5. ALSO measure: the ORTHO silhouette must visibly show the curved arm +
   hanging cage (vision-check yourself); if the mesh came back as
   pillar-with-crowned-lantern AGAIN (no arm), that's a FAILED design match
   even if gates pass - treat as gate failure (re-roll once with a stronger
   arm-emphasis prompt: "the arm clearly hooks sideways beyond the pillar
   edge").

## WIRE (CONFIG + code, minimal; identical on both branches)

- MANIFEST lanternPost -> v3 (v2 retired to comment).
- Row scale: measure v3 ext Y vs v2's 1.8894 (old-old 1.9991); correct ALL
  lanternPost rows' scale in both regions to keep ~4.8m in-world height.
  Report factor.
- lightSockets.lanternPost: REMEASURE (lantern_head_probe.py pattern - +8
  BIN header gotcha): head = the HANGING cage (OFF-AXIS this time):
  heightFraction of the cage glass band + offset [x,z] glTF-local of the
  cage center from the pillar axis. Intensity 9.0 stays. Verify with the
  Round-K-style lit still: flame INSIDE the cage, pool on the ground,
  warm on the arm underside.
- Collider: v3 pillar on origin (verify; if v3's pillar is off-origin like
  the OLD asset, note the offset - the K-era collider math expects origin).

## VERIFY (all required)

- treeqa orthos + lit socket still -> scratch/roundL-proof/01-v3-lit.png
  (+ ortho front/side in treeqa/roundL/). Vision-check.
- esprima CONFIG.js + assets.js both branches.
- wall_mirror unchanged; scatter mirror unchanged counts; ringHosts
  without lanternPost.
- SHA guard: reach a/b/c, bramble, v2, old post GLBs byte-identical
  before/after (20/20 + v2 = 22 checks).

## Commits (CaptainPickard <pickard.nicko@gmail.com>, both branches, same
messages):
- feat(assets): lantern-post-v3 arm-hook generated + QA (Round L)
- feat(world): MANIFEST swap to v3 + arm-hook socket remeasure (Round L)
- build: v7 bundle (worktree only)
Plus scratch/treeqa/roundL/, scratch/roundL-proof/, io/roundL-provenance.md
(ledger + measurements), tree_meshy.py header, this brief file. No push. No
light.js/player.js/enemy.js/moveset.js/region-defs.js. Never read/commit
scratch/.mixamo-credentials.txt or .mixamo-storage.json.

## Report (<= 50 lines)

Ledger (start/ids/spend/end), gate + piece-count results, arm-silhouette
vision verdict, old-vs-v3 heights + scale factor, socket measured values,
mirror verdicts, sha-guard verdict, proof list, deviations, watch items,
FAILED (or none).