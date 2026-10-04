# Round E vegetation: provenance and determinism (2026-10-05)

Contract: io/missions/2026-10-05-cc-roundE-veg.md. Pipeline: the M16-M19 round
(scratch/astrabot-tree-variety-report.md). Each asset went through these steps:

1. t2i ref (nano-banana, white background).
2. `scratch/ref_matte.py` alpha matte. Some refs were also muted in the ref, never regraded afterwards.
3. `scratch/tree_meshy.py i23d` (meshy-5, quad, remesh, data-URI ref).
4. `scratch/tree_gate.py` (welded component gate) and `scratch/tree_ortho.py` front+side QA, done before accepting the mesh.
5. `scratch/tree_bake.py` (raw mesh as-is, NORMAL injected, 512 NEAREST + 5-bit posterize).

Files per asset are the same as the siblings in `art-direction/3d/assets/biome_library/`:
`<id>.glb`, `<id>-pixelated.glb`, `raw/<id>.glb` (Meshy original) and `refs/<id>-ref.png` (the exact image sent to i23d).

## Assets

| asset | i23d task (shipped) | t2i ref task (shipped) | target | tris | welded largest | tinyFar | ext X / Y / Z | ymin | ortho |
|---|---|---|---|---|---|---|---|---|---|
| wh-bush-a | 01a108dc-ad5b-7175-ad45-ba8ea751cb42 | 01a108dc-0a79-7609-95e0-d624d337baa6 (r3) | 1200 | 2321 | 97.0% | 0 | 1.775 / 0.962 / 1.743 | -0.502 | PASS (2nd mesh) |
| wh-bush-b | 01a108e1-7da2-74a9-81e6-05bd4de76ddc | 01a108e0-4fef-75e6-b33b-a8d184e88c1d (r2, muted) | 1200 | 2836 | 77.9% | 3 | 1.813 / 1.488 / 1.110 | -0.754 | PASS w/ note |
| wh-grass-tuft | 01a108e3-cd8c-71ad-9aee-d6537fe0af85 | 01a108e3-24d0-70f7-8c8a-e81512be8bbd (muted) | 500 | 848 | 100.0% | 0 | 1.463 / 1.859 / 1.363 | -0.951 | PASS |
| wh-tree-birch-young | 01a108e7-ed30-7259-b690-1a6cdc28852b | 01a108e6-b52c-7202-961a-f2181f90921f (r2) | 2000 | 4410 | 77.0% | 0 | 0.656 / 1.852 / 0.698 | -0.929 | PASS |
| wh-tree-dead-young | 01a108ea-0d56-76c5-b2dc-b529deacf3a5 | 01a108e9-6c1d-7076-b0b7-aab68c1e185c | 2000 | 3630 | 99.9% | 0 | 0.690 / 1.895 / 0.509 | -0.951 | PASS |

All five assets are centered like m5: XZ center is within 0.021 of the origin and ymin is about -height/2. Every
pixelated texture is 512x512 with all channels 5-bit (`scratch/tex_check.py`).

Mean texture RGB: bush-a 50/62/46, bush-b 70/72/46, grass 95/106/80, birch 74/84/65, dead 62/55/50.

Ortho renders:
- Primary: `scratch/treeqa/roundE/<id>-front.png` and `-side.png` (tree_ortho.py).
- Legacy: `scratch/treeqa/roundE/legacy/<id>-{front,side}-ortho_preview.png`. These assets are under 8000 faces, so the
  decimation bug doesn't trigger, but the legacy "side" view is still the front view rolled 90°.
- Gate JSON: `scratch/treeqa/roundE/gate.jsonl`.

### Per-asset notes
- **wh-bush-a**:
  - Mesh 1 (01a108d9-9c87-74ad-ae96-be208554b71b, from fuzzy-leaf ref 01a108d8-...) **failed ortho QA**. It came
    back as a shard storm: 239 welded components, largest only 31.9%, holes throughout. This is the same failure mode as thin fronds.
  - Ref r2 (01a108db-...) was a clean but toy-like clay mound, so it was rejected before meshing.
  - Ref r3 (solid clumps with the leaf pattern only *painted* on, firm silhouette) meshed clean.
  - Lesson: bush refs need closed silhouettes, with no leaf tips breaking the outline.
- **wh-bush-b**:
  - Ref 1 (01a108de-...) read as a conical topiary tree with a trunk and blue-grey tone, so it was rejected before meshing.
  - The shipped mesh has a small dark notch high on the tall lump, plus 3 tiny far faces. It reads as a foliage gap. Accepted.
- **wh-grass-tuft**: chunky faceted blades fused at one base. Single watertight component.
- **wh-tree-birch-young**:
  - Ref 1 (01a108e5-...) had pencil-thin side branches, a breakage hazard, so it was rejected before meshing.
  - r2 was matted at tol 22 so the near-white bark survives the white-background matte. The trunk measured 24-42 px wide all the way down.
  - The 77% welded figure comes from thin branchlets at the canopy base. tinyFar is 0.
- **wh-tree-dead-young**: one trunk with three chunky blunt limbs. It is more upright than "lean". It was the last
  asset and there was no credit room for a second mesh, so the mesh-safe ref was chosen.

## Credits (scratch/tree_meshy_log.jsonl)

Balance went from 1426 to 1309, so **117 credits** were spent (cap 130):
- 9 t2i refs x 3 credits = 27
- 6 i23d meshes x 15 credits = 90 (one mesh rejected: bush-a mesh 1)

No submit returned 402 or 400. All submits were serial: each command blocks until its task returns. The log ends with
the five shipped `i23d-done SUCCEEDED` entries. The driver guard was updated for this mission:
`START_BALANCE 1426`, `CAP 130`, and a hard `MAX_TARGET 2000` on target_polycount.

## Runtime integration

- `prototype/js/assets.js` MANIFEST adds youngBirch, youngDeadTree, bushA, bushB and grassTuft.
  - Region-def check: `preloadAll()` iterates every MANIFEST key. region-defs.js has no per-region preload list (it
    only derives region records from CONFIG), so no region-def edit is needed.
- `prototype/js/CONFIG.js` has a new `scatter` block. It holds parameters only (seed 20261005).
- `prototype/js/region-manager.js` adds the following:
  - `whScatterPlan` (THREE-free, pure).
  - `whBuildInstanced`: one InstancedMesh per asset per region. It shares the pixelated template's geometry and
    material, writes matrices once, and uses whole-mesh frustum culling over `computeBoundingSphere()`.
  - Scatter trees are built as ordinary cloned props.
  - Scatter tree colliders are appended to `whPropColliders` at plan time as `index: 'scatter<i>'`.
  - The dirt-path sway is shared via `whPathCenterX`.
  - `disposeRegion` frees the instance buffers.

## Determinism by construction (no JS engine on this box)

Line numbers below refer to `prototype/js/region-manager.js`, which is byte-identical on dev and feat/world-visuals.

1. **PRNG**: `whRng` (line 267) is mulberry32. It is a pure 32-bit integer recurrence over its seed, using only
   `|0`, `Math.imul`, `^` and `>>>`. These are exact in every JS engine (no floating point until the final divide by 2^32).
2. **Seeds**: `stream(layer)` (line 575) seeds each layer from `CFG.scatter.seed ^ whHashStr(regionId + ':' + layer)`.
   `whHashStr` (line 532) is FNV-1a 32-bit, also pure integer math. The layers are trees (646), rings (694),
   freeBushes (712) and grass (725). The streams are independent, so changing one layer's parameters can't move another layer.
3. **Fixed draw order**:
   - Each tree draws exactly `candidates` × 2 samples (line 650 loop), then pick, rotY and height. It draws these even
     when no candidate was valid, so a miss can't shift later trees.
   - Each ring slot draws angle-jitter, radius, pick, height and rotY in fixed order.
   - Each free-bush and grass attempt draws a fixed count before its rejection test.
4. **Inputs**: `whScatterPlan` (line 552) reads only the following:
   - CONFIG: the scatter block, region props/spawn/enemies/nodes, world dirtPath, boundary, chokepoint, groundRadius
     and playerMargin.
   - `meta(name)`: footprints measured once from the loaded GLBs (Box3 at identity, assets.js groundAlign).
   - It reads no time, no `Math.random`, no player state and no frame data.
   It returns a fresh object and mutates nothing outside it, so the same inputs always give the same plan.
5. **Caching**: `RegionManager.prototype.scatterPlan` (line 811) caches the plan once every footprint is known. That is
   the same rule as the collider table. `buildRegion` (line 952) and `propColliders` both read that one cached plan,
   so the visual trees and the collider rows can't disagree. Rebuilding after dispose reuses the cached plan.
6. **Independent check**: `scratch/scatter_mirror.py` is a line-by-line Python port with JS int32 semantics. Its
   mulberry32(1) output matches the published sequence (0.6270739405881613, ...). Running it twice gives identical
   output, and it produced the counts below. In game, the authoritative counts are logged once per region as
   `[WH scatter] <regionId> {...}`. Only `Math.sin`/`Math.cos` ulp differences between V8 and libm could flip a
   knife-edge rejection.

## Placement results (mirror; feat/world-visuals = the built branch)

| region | trees extra | ring bushes (skipped) | free bushes | grass | InstancedMesh (instances) |
|---|---|---|---|---|---|
| hold_outskirts | 14/14 | 305 (3) | 20 | 220 | 3: bushA 199, bushB 126, grassTuft 220 |
| darkwood_edge | 10/10 | 128 (4) | 20 | 220 | 3: bushA 88, bushB 60, grassTuft 220 |

dev gives identical numbers for region A. For region B, dev has the same counts (10 / 128 / 20 / 220), but 2 tree
positions differ. Only feat has CONFIG gather `nodes`, and trees keep 2.5 m from them. The plan is a pure function of
each branch's CONFIG, as intended.

Proof stills: `scratch/roundE-proof/01-regionA-patch.png` and `02-bush-ring-closeup.png`
(`scratch/roundE_proof_scene.py` + `roundE_proof_render.py`, Blender 4.5 EEVEE, positions taken from the feat plan).
