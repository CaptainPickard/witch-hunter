# Round K provenance: lantern-post-v2 (Claude Code, 2026-10-05)

Brief: io/missions/2026-10-05-cc-roundK-lamppost-v2.md. Replaces the shattered church-kit
lantern post (old pixelated GLB: 2000 faces, 202 welded pieces, largest 10.7%, gate(a) FAIL).

## Meshy ledger (serial, scratch/tree_meshy.py guard: Round K start 1213, cap 40, floor 1173)

| step | task id | credits | balance after |
|---|---|---|---|
| measured start | - | - | 1213 |
| t2i ref (nano-banana) | 01a10a92-f391-707d-b031-86b054c291ed | 3 | 1210 |
| i23d meshy-5, target 2000 | 01a10a94-5fb1-7543-8fb6-3de7e90467f7 | 15 | 1195 |

Total spend: 18 of 40. No re-roll (gate passed on the first mesh).

Ref prompt (brief verbatim): "a tall gothic wrought iron lamp post, single object, slender dark
metal pillar with flared stepped base, elegant curved arm holding a hexagonal lantern with peaked
cap and finial, weathered rusted iron, grim dark fantasy matte render, plain near-black background,
centered, ground level". The model drew a POST-TOP lantern (no side arm), on the pillar axis.

## Matte

scratch/ref_matte.py --dark could not separate the post: its shadow side is the bg tone
(24-28 vs bg 26-27), so the flood-fill split it (tol 45: only the base survived, 6.7k px; tol
31/34: only the head or base). New scratch/ref_matte_rowspan_roundK.py: bg-difference edges
(largest connected set), each row filled symmetrically about the pillar axis to its lit-left
half-width (the right side carries a faint bg halo), closing, largest blob. 54.7k px, one
continuous silhouette (diff=8).

## Gate (scratch/tree_gate.py, welded mode; scratch/treeqa/roundK/gate.jsonl)

| file | faces | welded comps | largest | tinyFar | gate(a) |
|---|---|---|---|---|---|
| raw Meshy | 4454 | 1 | 100.0% | 0 | PASS |
| v2 pixelated | 2500 | 3 | 99.8% | 0 | PASS |
| old lantern-post-pixelated | 2000 | 202 | 10.7% | 4 | FAIL |

The 2 extra pieces in v2 are 2-face decimation slivers at the finial tip (y=0.937), sharing
1-2 vertices with the body (max 1.6 mm off it): vertex-joined, not floaters. Orthos (raw +
pixelated, front + side) vision-checked: one continuous base + pillar + collar + scrolls + lantern
+ cap + finial, no floaters.

## Bake (scratch/lanternpost_bake_roundK.py; scratch/treeqa/roundK/decimate.jsonl)

Position weld (4010 -> 2229 verts) + XZ recenter on the pillar axis (shift +0.0020, +0.0017),
quadric decimate on the welded mesh to 2500, per-face UV transfer (decimate_roundH.py probes),
UV-seam copies over welded positions (1252 positions -> 7494 verts), smooth normals per
position (spread across copies = 0; 2 zero normals repaired), posterize512 imported directly,
trimesh export. Verified: chunk 0 JSON, chunk 1 BIN, NORMAL present (unit length), reload
2500 faces / 7494 verts, tex 512. biome_pixelate.export() NOT used.

Landed (church-kit): lantern-post-v2-pixelated.glb (427,040 B), lantern-post-v2.glb (mid, raw
2048 tex), lantern-post-v2-ref.png (matte), raw/lantern-post-v2.glb, refs/lantern-post-v2-ref.png.
Old lantern-post*.glb kept byte-identical (rollback = MANIFEST line flip in assets.js).

## Wire (both branches)

- assets.js MANIFEST lanternPost -> lantern-post-v2-pixelated.glb (old line kept as comment).
- Heights (GLB units): old 1.9991, new 1.8894; factor 1.0581 -> scale 2.4 -> 2.54 on all 5
  lanternPost rows (regionA 2, regionB 3). In-world height 4.798 m -> 4.799 m.
- lightSockets.lanternPost: glass x -0.123..+0.127, z -0.116..+0.112 at 75.5-87.5% H (floor ring
  72-75%, cap brim 88%), centre within 2 mm of the axis -> heightFraction 0.81, offset [0.0, 0.0]
  (was 0.72, [-0.18, 0.0]). Intensity 9.0 unchanged. World socket y = 1.8894 * 2.54 * 0.81 = 3.887.
- Collider: lanternPost does NOT match TRUNK_ASSETS or the trunk regex in region-manager.js, so it
  takes the FULL footprint r = width * scale / 2 (unchanged math): 0.708 m -> 0.502 m. The old
  pillar sat 0.36 m off its prop origin (old origin = bbox centre, pillar at x +0.15); v2 has the
  pillar ON the origin, so the circle now matches the post.

## Verify

- esprima: CONFIG.js + assets.js parse on dev and feat/world-visuals.
- wall_mirror: identical to HEAD on both branches. scatter_mirror: placements/counts identical;
  only the 5 lanternPost rows' echoed scale and collider r change. ringHosts has no lanternPost.
- sha256 guard: 3 reach-tree + bramble GLBs (mid + pixelated) and the old lantern-post GLBs,
  both trees: 20/20 identical before/after (scratch/treeqa/roundK/sha_before.txt, sha_after.txt).
- Proof: scratch/roundK-proof/01-new-post-lit.png (roundF_proof_render.py, night, 900 W point
  at the socket, shadow off = game props never cast shadows, flame marker r 0.06): warm ground
  pool around the base, cap-brim underside + scroll tops lit = light inside the head.
