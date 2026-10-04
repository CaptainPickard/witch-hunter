# Round G: tall walls + snare-bush tree rings, provenance (2026-10-05)

Contract: io/missions/2026-10-05-cc-roundG-walls-snare.md. No Meshy submits and no downloads (zero credits). No
harness, browser or game-loop runs: only static mirrors, esprima syntax checks and Blender headless renders.

## Change 1: boundary walls 3x taller

- The one knob is `CONFIG.boundaryWall.heightM`: **2.4 -> 7.2**. `whWallPlan.scaleFor` already derives
  `sy = heightM / measured height`. X (`segmentLengthUnits`) and Z (`depthScale`) are untouched, and so is region-manager.
- `scratch/wall_mirror.py` output vs Round F (`scratch/roundF-proof/wall_mirror.json`) differs in **exactly two
  numbers**:
  - whWallA sy 3.1179 -> **9.3537**.
  - whWallB sy 3.0821 -> **9.2464**.
  - Both are exactly x3.000. Segment positions, the 145 ring + 22 + 22 chord count, 603 colliders (r 0.45), arch,
    legs, plugs, lantern and socket are all byte-identical.
- Determinism: two consecutive runs gave byte-identical JSON and stdout on dev, and on feat/world-visuals. The dev
  and feat outputs are also byte-identical to each other. Output: `scratch/roundG-proof/wall_mirror.json`.
- The gate arch (10.53 m tall, apex 6.80 m) is unchanged. The 7.2 m chord walls now meet it above the opening apex.

## Change 2: snare bush on the tree rings

### Asset: wh-bush-snare

- Source: Nicko's Meshy model, task `01a1092f-3bdf-7461-86ad-9eaa081187cc`. IO downloaded it to
  `scratch/treegen/roundE/wh-bush-snare-meshy-raw.glb`, with the thumbnail at `wh-bush-snare-thumb.png`.
- **The raw GLB is geometry only.** Its glTF has a single primitive with `POSITION` + indices. It has no `materials`,
  `textures`, `images` or `TEXCOORD_0`. The thumbnail is the grey untextured preview: a thorned briar with roses.
- Gate (`scratch/tree_gate.py`, `scratch/treeqa/roundG/gate.jsonl`):

| mesh | tris | welded comps | largest | tinyFar | ext X / Y / Z | ymin | gate(a) |
|---|---|---|---|---|---|---|---|
| raw | **820,996** | 9 | 77.5% | 0 | 1.899 / 1.644 / 1.645 | -0.821 | PASS |
| decimated (shipped) | **3,000** | 247 | 22.3% | 6 | 1.896 / 1.621 / 1.602 | -0.815 | FAIL (see note) |

- Decimation: `scratch/decimate_roundG.py`, signed, log in `scratch/treeqa/roundG/decimate.jsonl`.
  - It uses `fast_simplification.simplify` (the art-direction/3d/regen_pipeline_v2.py decimator) on the
    position-welded mesh.
  - Before: 820,996 faces / 410,398 verts. After: 3,000 faces / 1,525 verts.
  - Output is deterministic: two runs gave identical geometry.
- Gate note: thin thorn branches split into separate ribbons at 3k tris, so the welded-largest test (>= 60%) fails.
  This is not the shard-storm failure. The ortho renders (`scratch/treeqa/roundG/wh-bush-snare-{front,side}.png` vs
  `-raw-{front,side}.png`) keep the same silhouette: trunk, arching thorned canes and ~20 rose heads. Roses become
  chunky low-poly knots and canes become flat ribbons. Rendering is DoubleSide, so the ribbons do not vanish edge-on.
- Bake: `scratch/snare_bake_roundG.py`. **The bake-law texture half could not run** (FAILED, see below). What
  shipped:
  - `wh-bush-snare-pixelated.glb` holds the decimated mesh, smooth vertex NORMALs (injected, like the E siblings) and
    one untextured PBR material.
    - Metallic 0 and roughness 0.8 match wh-bush-a.
    - `baseColorFactor` is wh-tree-dead-young's mean bark texel (62/55/50 sRGB), 5-bit crushed to 56/48/48 and
      stored linear (0.0395 / 0.0296 / 0.0296).
  - `wh-bush-snare.glb` is the decimated geometry with no material.
  - `raw/wh-bush-snare.glb` and `refs/wh-bush-snare-meshy-raw.glb` are byte copies of the Meshy original (one git blob).
  - `refs/wh-bush-snare-ref.png` is the Meshy thumbnail.
- wh-bush-a/b(-pixelated).glb stay in the repo.

### Wiring

- `CONFIG.scatter.bushes.atTreeRing.assets = [['whBushSnare', 1, 1.0, 1.4]]` (rows: [asset, weight, hMin, hMax], the
  `bushes.assets` row format).
  - The 1.0-1.4 m height range sits inside the old ring band (0.7-1.3 m).
  - That gives a ~1.2-1.6 m wide briar.
- Free bushes still draw `bushes.assets` (bushA/bushB), and grass is unchanged.
- Rollback: delete the `assets` key (or set it to the bushA/bushB rows). The code then falls back to `B.assets`.
- `region-manager.js`: `bushPick(rand, rows)`. Rings pass `R.assets || B.assets` and free bushes pass `B.assets`. The
  draw count per bush is unchanged (pick, height, rotY), so no stream shifts.
- `assets.js`: MANIFEST `whBushSnare`. `preloadAll()` iterates every MANIFEST key, so no other plumbing was needed.
  The generic per-asset InstancedMesh build picks it up.
- Rings keep r = 0 (no collider). keepOut, corridor, spawn and path clearances are untouched.
- `scratch/scatter_mirror.py` mirrors the same `bush_pick(rand, rows)` change.

### Ring counts (scratch/scatter_mirror.py; two runs byte-identical on each branch)

| region | Round E (bushA/B) | Round G (whBushSnare) | ring slots skipped |
|---|---|---|---|
| hold_outskirts (A) | 305 | **305** | 3 -> 3 |
| darkwood_edge (B) | 128 | **130** | 4 -> 2 |

- dev and feat/world-visuals give the same counts.
- Every Round E ring position is kept (305/305 and 128/128 common). The 2 added B rings are slots that used to be
  skipped: the snare's smaller own-radius now clears the neighbour circle.
- Free bushes (20 + 20), grass (220 + 220) and scatter trees are identical to Round E.
- Instances: A has whBushSnare 305, bushA 12, bushB 8. B has whBushSnare 130, bushA 13, bushB 7.
- Mirror output: `scratch/roundG-proof/scatter_mirror.json` (dev).
- Triangles in bush instances, approximate:
  - A: ~819k -> ~966k.
  - B: ~374k -> ~440k.

## Proof stills (scratch/roundG-proof/, Blender 4.5 EEVEE, shadows off)

`scratch/roundG_proof_scene.py` builds the shots from the two mirrors. `scratch/roundG_proof_render.py` is the
Round F renderer (matrix-chain ground lift) with shadows off.
1. `01-wall-height-closeup.png`: ring segments 10/11 seen along the arc, with the line receding past a yew.
2. `02-wall-ring-wide.png`: from inside region A at game eye height 4.99 m. The camera spot was searched clear of
   props/trees, because the first framing sat inside a yew canopy. The 7.2 m wall top stays above the eye line along
   the whole arc, so no horizon shows over it.
3. `03-snare-ring-closeup.png`: young birch (48.7, 32.6) with 4 snare bushes knotted around its base, and grass
   tufts in the mid-ground. The first framing used a young dead tree, but there the briars sat inside the flared
   trunk (see watch items), so the host is now restricted to youngBirch.

## FAILED

- **Step 3, texture treatment matching wh-bush-a.** `tree_bake.py`'s `mesh.visual.material.baseColorTexture` fails
  on this input: trimesh loads `ColorVisuals` with no `.material` (`AttributeError: 'ColorVisuals' object has no
  attribute 'material'`), because the GLB has no material, UV or image. There is no texture to pixelate. The untextured
  bark-factor material above is the fallback. A real fix needs a Meshy texture pass on the model, which costs credits
  (IO/Nicko call).
