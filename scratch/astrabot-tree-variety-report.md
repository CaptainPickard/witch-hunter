# Astrabot report: tree variety pass (2026-10-03)

Brief: io/missions/2026-10-03-astrabot-tree-variety-brief.md. Branch feat/world-visuals.
Result: **3/3 required trees + the bonus landed**. Every one passes the component
gate. One caveat on m16: its base flare has holes (details below).
Meshy spend: **156 of 160 credits** (balance 1600 -> 1444), including 6 rejected attempts.

| asset | commit | Meshy job (image-to-3d) | tris | welded largest comp | tinyFar | ext X / Y / Z | ymin | gate a | gate b | gate c |
|---|---|---|---|---|---|---|---|---|---|---|
| m16-living-oak-pixelated.glb | 60d8d36 | 01a10047-4905-70e0-a125-ac5536a9026a | 35590 | 32830 (92.2%) | 0 | 1.845 / 1.627 / 1.848 | -0.823 | PASS | PASS w/ defect (base flare) | PASS |
| m17-witchwood-pixelated.glb | e3ee46d | 01a1004d-7fc8-76e4-9925-45a542023bff | 28084 | 26516 (94.4%), 2 comps total | 0 | 0.642 / 1.889 / 0.714 | -0.951 | PASS | PASS | PASS |
| m18-dead-tree-pixelated.glb | c22f459 | 01a10051-0759-716c-95d1-7240d51f7c0d | 30174 | 30174 (100%), 1 comp | 0 | 1.380 / 1.896 / 0.736 | -0.952 | PASS | PASS | PASS |
| m19-birch-pixelated.glb (bonus) | 4dc038d | 01a10053-3888-7022-b473-504a6017fed0 | 30484 | 29467 (96.7%) | 0 | 1.022 / 1.897 / 1.005 | -0.951 | PASS | PASS (minor slit) | PASS |
| *m5 reference* | - | - | 28243 | 27487 (97.3%) | 0 | 1.011 / 1.894 / 1.022 | -0.950 | PASS | - | - |
| *m4 (purged)* | - | - | 27380 | 15111 (55.2%) | 46 | 1.843 / 1.755 / 1.881 | -0.879 | FAIL | - | - |
| *m6 (purged)* | - | - | 27672 | 18701 (67.6%) | 45 | | | FAIL | - | - |
| *church-kit dead-tree (purged)* | - | - | 2000 | 35 (1.8%) | 35 | | | FAIL | - | - |

All four are centered like m5: XZ center within 0.016 of the origin, and ymin is about -height/2.
Bake law check (scratch/tex_check.py): every pixelated texture is 512x512 with all channels 5-bit.
The GLB attributes are POSITION/TEXCOORD_0/NORMAL with a PNG image, the same layout as m5-pixelated.

Mean texture RGB: m5 51/52/44, m16 59/62/50, m17 57/56/52, m18 78/75/71, m19 60/62/49.
These are dark bark and muted olive/ash tones with no accent colors.
The m17 canopy averages about 92 grey-green, which is "pale-ish" next to its bark at about 62.

Files per asset: `biome_library/<id>-pixelated.glb`, `biome_library/<id>.glb` (raw re-export, the same
treatment as m5.glb), `biome_library/raw/<id>.glb` (Meshy original, byte copy), and
`biome_library/refs/M1x-*-ref.png` (the exact image sent to Meshy).
QA renders: `scratch/treeqa/m16|m17|m18|m19-front.png` and `-side.png`. The m5/m4 baselines are in
`scratch/treeqa/m5-full-*.png` and `m4-full-*.png`. Legacy ortho_preview.py output is in `scratch/treeqa/legacy/`.

## Gate methodology: two deviations from the brief's literal wording (please read)

1. **Gate (a) has to weld vertices by position.** The brief's tree_diag.py method loads the mesh
   with trimesh defaults, and that keeps UV-seam vertices split. So it counts UV islands, not
   geometric pieces. Under that method even the gold-standard **m5 scores 1.7%** for its largest
   component (7643 "components"). That fails the 60% rule, so the rule can't be met as literally
   written. `scratch/tree_gate.py` reports both modes and gates on the position-welded one.
   Welded mode separates the cases cleanly: m5 97.3% / m8 99.3% PASS, m4 55.2% / m6 67.6% /
   dead-tree 1.8% FAIL (each with 35-46 far shards).
   For the record, the uv-split numbers for the new assets are: largest component 1.9% / 6.1% / 14.2% / 4.7%;
   tinyFar 46 / 0 / 0 / 0.
   m16's 46 uv-split tinyFar are UV islands on its canopy surface, not loose debris (welded tinyFar is 0).
2. **Gate (b) used `scratch/tree_ortho.py`, not `art-direction/3d/ortho_preview.py`.** The legacy tool has two bugs:
   (i) it runs fast_simplification down to 8000 faces on the unwelded mesh, which shreds every
   silhouette, so intact m5 also renders as confetti (see scratch/treeqa/m5-front.png).
   (ii) its "side" view rotates about the camera's depth axis, so it is the front view rolled 90°.
   The replacement draws every face, uses the texture colors and a real side elevation, and adds a ground line at ymin.
   I left ortho_preview.py untouched because it is outside this mission's edit scope. Its outputs for each new
   asset are still in scratch/treeqa/legacy/. Suggested fix for IO: drop the decimation, or weld before
   simplifying, and rotate about the vertical axis for the side view.

## Per-asset notes

- **m16-living-oak**: the canopy is broad, solid and dome-shaped, with a thick dark trunk.
  **Defect:** the root-flare skirt in the bottom ~10% of height (0.163 local units) is holed and fragmented.
  725 of the 731 stray trunk faces sit below that line; m5 has 14 such faces. In game terms this means:
  **sink the oak 0.16 local units (× instance scale) into the terrain** and the defect is fully buried.
  Five mesh attempts were made:
  - r1: see-through canopy and 56k tris (target 30000 in quad mode doubles the triangles).
  - r2: dark trunk on a dark background; most of the trunk was lost to background removal.
  - r4: background shadow included.
  - r5: matted ref. **This one was shipped.**
  - r6: base reshaped into a column in the ref. It came out worse (88.1%), so it was rejected.
- **m17-witchwood**: a tall, spiral-twisted black trunk with five round ash clumps on crooked limbs.
  It reads a little organic and wrong.
  The first pass (01a1004b-a54e-740f-9d35-6b5451dc5114) baked a near-white canopy (RGB about 186), so
  I rejected it. The canopy was muted in the reference image instead (no asset regrade).
- **m18-dead-tree**: three thick crooked limbs plus broken stubs, with no twigs. It is a single
  watertight component, done on the first attempt.
- **m19-birch**: brief option "young birch/ash"; I built it as a young ash, because white birch
  bark would break the darkwood palette and the white-background matte. It has a slim trunk and a small olive crown, with a footprint
  identical to m5. Minor issues: a thin vertical slit in the lower trunk on the side view, and 42 stray
  faces at the base. A 0.1-unit sink covers them.

## Integration recommendations (for IO; no game code was touched)

| manifest logical name | asset | notes |
|---|---|---|
| livingOak | m16-living-oak-pixelated.glb | sink 0.16 local × scale; wide (1.85) and shorter (1.63) than m5, so space it wider |
| witchwoodTree | m17-witchwood-pixelated.glb | region B Darkwood Edge; narrow footprint (0.64 × 0.71), can be packed tight |
| deadTree | m18-dead-tree-pixelated.glb | replaces church-kit/dead-tree; 1.38 wide on X, so random Y-rotation reads well |
| birchTree / youngAsh (new) | m19-birch-pixelated.glb | understory filler; optionally sink 0.1 |

- Triangle budget: the new trees are 28-36k tris each (m5 is 28k). A forest mixing them costs about the same per
  instance as today's all-m5 forest, with m16 about 26% heavier.
- **Naming clash:** biome_library already has m16-bandit-bedroll, m17-witch-totem, m18-mote-shrine and
  m19.glb (hanging moss). I used the brief's filenames as given; nothing was overwritten. The numeric prefixes now
  repeat, though, so refer to these by full filename in the manifest.
- The brief cited `art-direction/3d/docs/asset-manifest.md`. That file doesn't exist, so the rows were appended to
  `art-direction/3d/asset-manifest.md`, as the brief's provenance section says.

## Pipeline friction / lessons (for the next asset run)

- The ref image decides whether foliage survives Meshy. See-through leafy canopies (the old M4/M6 refs) come
  back as fragment clouds. Dense, opaque clump masses come back intact.
- The ref background must contrast with the trunk. On a dark grey background, the dark trunk is lost to Meshy's background removal.
  Put refs on white, then alpha-matte locally (`scratch/ref_matte.py`, which also clears floor shadows and
  enclosed sky pockets). Meshy accepts the RGBA PNG as a base64 data URI, so no hosting step is needed.
- Meshy's textures come out about 1.3× brighter than the ref. Control canopy tone in the ref.
- Meshy keeps generating broad root flares as thin, broken flange geometry (oak r2, r4, r5, r6). A slender or
  plain base (m17/m18) comes out clean.
- With `topology: quad`, `target_polycount` counts quads: 15000 gives about 28-38k triangles, matching m5.
- No polycount rejection from the provider at 15000/30000. The 2000 cap from R7 was not hit.
- Submits were serial throughout via `scratch/tree_meshy.py`, which blocks until each task returns and checks the
  balance against the cap floor before every submit. The key is never written anywhere; the log is
  `scratch/tree_meshy_log.jsonl` (task ids and balances only).

## Credit ledger (start 1600)

| task | kind | credits | outcome |
|---|---|---|---|
| 01a10036-73c4-7364-a868-f2e1e550ee24 | ref oak r1 | 3 | see-through canopy |
| 01a10036-e25e-7353-941d-d524d8b2be68 | mesh oak r1 (30000) | 15 | rejected: thin trunk, 56.6k tris |
| 01a1003e-2890-77e5-a2a4-5bca794465a6 | ref oak r2 | 3 | |
| 01a1003e-6ec3-7007-b372-ae56d7eed53d | mesh oak r2 | 15 | rejected: lower trunk lost (dark bg) |
| 01a10042-ef74-743a-bebe-8dc6f98f3e34 | ref oak r3 | 3 | unused (bark too light) |
| 01a10043-71c9-71bf-98e0-d9cdc09228c9 | ref oak r4 | 3 | |
| 01a10043-e052-74c7-a1d3-f34e1bfb9b29 | mesh oak r4 | 15 | rejected: base fragments (shadow in ref) |
| 01a10047-4905-70e0-a125-ac5536a9026a | mesh oak r5 (matte) | 15 | **SHIPPED m16** |
| 01a1004b-09db-706f-8595-6e45a74f8fc4 | ref witchwood | 3 | |
| 01a1004b-a54e-740f-9d35-6b5451dc5114 | mesh witchwood v1 | 15 | rejected: canopy near-white |
| 01a1004d-7fc8-76e4-9925-45a542023bff | mesh witchwood ash | 15 | **SHIPPED m17** |
| 01a1004f-543e-74f6-b392-b167aaf2edba | ref dead tree | 3 | |
| 01a10051-0759-716c-95d1-7240d51f7c0d | mesh dead tree | 15 | **SHIPPED m18** |
| 01a10052-9bf0-7268-80f7-2d71567f6315 | ref birch/ash | 3 | |
| 01a10053-3888-7022-b473-504a6017fed0 | mesh birch/ash | 15 | **SHIPPED m19** |
| 01a10056-d4da-7349-aa0c-8088bbcfe006 | mesh oak r6 (column base) | 15 | rejected: worse than r5 |
| | **total** | **156** | |

## Left undone

- The m16 base-flare holes are not fixed at the source. Fixing them needs another mesh attempt, and I had
  4 credits left. The terrain sink above is the workaround. Under the no-geometry-post-processing law,
  the only other fix is more Meshy attempts, perhaps a narrower oak with a plain base.
- No in-engine check, per the NO HARNESS law. Nicko's playtest is the acceptance test.
