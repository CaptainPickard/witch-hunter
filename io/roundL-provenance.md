# Round L provenance: lantern-post-v3, gothic arm-hook (Claude Code, 2026-10-05)

Brief: io/missions/2026-10-05-cc-roundL-lamppost-v3.md. Replaces lantern-post-v2 (post-top
lantern, no arm) with the OLD post's arm-hook silhouette in solid geometry. v2 + old kept on disk.

## Meshy ledger (serial, scratch/tree_meshy.py guard: Round L start 1155, cap 40, floor 1115)

| step | task id | credits | balance after |
|---|---|---|---|
| measured start | - | - | 1155 |
| t2i ref (nano-banana) | 01a10b39-15ed-732b-9380-3ec9e8a88d29 | 3 | 1152 |
| i23d meshy-5, target 2000 | 01a10b3a-0771-75c1-bbda-fd24e20c64ed | 15 | 1137 |

Total spend: 18 of 40. No re-roll (gate + design match passed on the first mesh).
Start deviation: the brief expected ~1195 (Round K end). The helper log has no call after Round K
(last row bal_after 1195), so 40 cr were spent outside scratch/tree_meshy.py between rounds.

Ref prompt (brief verbatim): "a tall gothic wrought iron lamp post, single object, slender weathered
dark iron pillar on a flared stepped base, ONE elegant curved arm reaching up and out from the
pillar top, a hexagonal lantern cage hanging from the arm's hook by a small ring, peaked cap and
finial on the lantern, grim dark fantasy matte render, plain near-black background, centered,
ground level". The model drew the arm-hook design on the first try: arm curling out to one side,
hook + ring, hex cage hanging free of the pillar.

## Matte

scratch/ref_matte.py --dark (tol 34/40/45) kept only the base (10-17k px; shadow side = bg tone),
and Round K's rowspan matte mirrors rows about the pillar axis (would erase the arm). New
scratch/ref_matte_diff_roundL.py: 2nd-order bg fit on the border, |px - bg| > 7 OR 3x3 texture
std > 3, closing, enclosed holes < 4000 px filled (the arm/pillar gap is open, stays bg), largest
blob. 66.2k px, one blob, arm + hook + ring + cage intact (vision-checked on magenta).

## Gate (scratch/tree_gate.py welded mode + piece check; scratch/treeqa/roundL/)

| file | faces | welded pieces | largest | tinyFar | gate |
|---|---|---|---|---|---|
| raw Meshy | 4344 | 1 | 100.0% | 0 | PASS |
| v3 pixelated | 2500 | 2 | 99.92% | 0 | PASS (>=90%, <=5, <=3 pieces) |
| v2 pixelated | 2500 | 3 | 99.84% | 0 | PASS |
| old lantern-post-pixelated | 2000 | 202 | 10.7% | 4 | FAIL |

The extra v3 piece (pieces.txt) is a 2-face decimation sliver at y 0.584 that shares all 3 of its
vertices with the body (0.0 mm gap): edge-nonmanifold attached, not a floater.
Orthos (raw + pixelated, front + side): pillar on the axis, arm curving out past the pillar edge,
hook + ring carrying the hanging cage, one continuous piece. DESIGN MATCH: PASS.

## Bake (scratch/lanternpost_bake_roundL.py = the Round K script with v3 paths; decimate.jsonl)

Position weld 4111 -> 2170 verts, XZ recenter on the pillar axis (20-60% H band, pure pillar):
shift x -0.1113, z +0.0016. Quadric decimate to 2500, per-face UV transfer, UV-seam copies
(1248 positions -> 7497 verts), smooth normals per position (0 zero normals), posterize512 imported
directly, trimesh export. Verified: chunk 0 JSON, chunk 1 BIN, NORMAL present (unit length),
reload 2500 / 7497, tex 512. biome_pixelate.export() NOT used.

Landed (church-kit): lantern-post-v3-pixelated.glb (403,600 B), lantern-post-v3.glb (mid, 590,376 B,
raw 2048 tex), lantern-post-v3-ref.png (matte), raw/lantern-post-v3.glb, refs/lantern-post-v3-ref.png.
v2 and old lantern-post GLBs byte-identical (rollback = MANIFEST line flip in assets.js).

## Wire (both branches, identical edits)

- assets.js MANIFEST lanternPost -> lantern-post-v3-pixelated.glb (v2 line kept as comment).
- Heights (GLB units): old 1.9991, v2 1.8894, v3 1.8934. Factor v2/v3 = 0.9979 -> scale
  2.54 -> 2.535 on all 5 lanternPost rows (all in regionA hold_outskirts; regionB has none).
  In-world height 4.799 m -> 4.800 m (old 4.798 m).
- lightSockets.lanternPost (scratch/lantern_head_probe_roundL.py, socket_probe.txt): cage-side
  (x < -0.12) 2.5% bands: cage floor 70% H, glass 70-82.5% (x -0.388..-0.211 at its widest,
  z +-0.086), cap brim 82.5-85% (w 0.209), finial/ring 87.5-92.5%, hook/arm 92.5-100%. Cage
  centre x -0.298..-0.300, z 0.000 on every cage band -> heightFraction 0.76, offset [-0.30, 0.0]
  (v2: 0.81, [0.0, 0.0]). Intensity 9.0 unchanged. World socket at rotY 0: x -0.761,
  y 1.8934 * 2.535 * 0.76 = 3.648, z 0.
- Collider: pillar on the glTF origin (bands 2-13 centres within 8 mm). Math unchanged (full
  footprint r = width * scale / 2), but width = bbox X now includes the arm + cage reach:
  0.585 * 2.535 / 2 = 0.742 m (v2: 0.502 m), circle centred on the pillar; base radius is ~0.46 m.

## Verify

- esprima: CONFIG.js + assets.js parse on dev and feat/world-visuals.
- wall_mirror: byte-identical JSON before/after on both branches. scatter_mirror: stdout (counts +
  tree placements) identical; JSON diffs = only the 5 lanternPost rows' scale (2.54 -> 2.535) and
  r (0.502 -> 0.742). ringHosts has no lanternPost (both branches).
- sha256 guard: 3 reach-tree + bramble (mid + pixelated), old lantern-post (2), v2 (2), both
  trees: 24/24 identical before/after (scratch/treeqa/roundL/sha_before.txt, sha_after.txt).
- Proof (roundF_proof_render.py, night, 900 W point at the socket, shadow off, flame r 0.06):
  scratch/roundL-proof/01-v3-lit.png (full post: warm ground pool offset under the cage, arm
  underside + cage-facing pillar side warm, cage frame lit from inside), 02-v3-lit-cage-close.png.
  The flame marker is hidden because the baked glass panes are opaque/dark; the socket lies
  inside the measured cage box.
