# Round F boundary wall + gate arch: provenance and determinism (2026-10-05)

Contract: io/missions/2026-10-05-cc-roundF-wall.md. Asset pipeline = Round E's
(io/roundE-veg-provenance.md): nano-banana t2i ref (white bg) -> `scratch/ref_matte.py`
-> `scratch/tree_meshy.py i23d` (meshy-5, quad, remesh) -> `scratch/tree_gate.py` +
`scratch/tree_ortho.py` QA -> `scratch/tree_bake.py` (raw mesh as-is, NORMAL, 512 NEAREST
+ 5-bit). Files per asset in `art-direction/3d/assets/biome_library/`: `<id>.glb`,
`<id>-pixelated.glb`, `raw/<id>.glb`, `refs/<id>-ref.png` (the matte sent to i23d).

## Assets

| asset | i23d task (shipped) | t2i ref task | target | tris | welded largest | tinyFar | ext X / Y / Z | ymin | ortho |
|---|---|---|---|---|---|---|---|---|---|
| wh-wall-vinestone-a | 01a10904-f03b-7066-9f77-4e1262959677 | 01a10903-4b16-74ca-99fe-de6e700adbd9 | 2000 | 4118 | 99.6% | 0 | 1.899 / 0.770 / 0.486 | -0.387 | PASS |
| wh-wall-vinestone-b | 01a10906-3616-76a5-b39f-a5622d568b44 | 01a10903-798e-7689-b234-2ca5863acdf4 | 2000 | 4375 | 81.1% | 0 | 1.899 / 0.779 / 0.513 | -0.404 | PASS |
| wh-lantern-hang | 01a10907-a486-7077-ab05-57d4c2c7bff7 | 01a10903-f808-7658-af4e-3ce75ed29e0e | 1500 | 3090 | 100.0% | 0 | 1.370 / 1.895 / 1.227 | -0.952 | PASS |

All three are centered like the proven pipeline (XZ center within 0.015 of the origin,
ymin ~ -height/2, identity node matrix). Pixelated textures: 512x512, every channel 5-bit
(`scratch/tex_check.py`). Mean RGB: wall-a 49/52/50, wall-b 38/42/38, lantern 51/40/32.

- **wh-wall-vinestone-a**: straight dark block wall, uneven cap-stone row, flat chunky ivy
  clumps fused to the front face. The 7 welded comps are ivy-leaf slivers on the face.
- **wh-wall-vinestone-b**: crumbled stepped top-right corner, dense ivy draping over the top
  onto BOTH faces (side ortho). 69 welded comps / 81.1% = ivy-drape edge slivers; tinyFar 0.
- **wh-lantern-hang**: square iron cage, pyramid roof, closed thick ring hook, amber glass.
  Single watertight component. **Emissive pass** (`scratch/lantern_emissive.py`, after
  tree_bake): emissiveTexture = the baked 512 5-bit base map masked to its amber texels
  (glass, 11.4% of texels), others black; emissiveFactor [1, 1, 1]. Only the -pixelated GLB
  carries it (the runtime file); region-manager gives the emissive map NearestFilter.

Refs: all three first-roll refs were accepted (closed silhouettes, ivy and glow painted on,
thick ring hook). Wall refs were shot three-quarter-from-above so i23d sees the depth.

QA renders: `scratch/treeqa/roundF/<id>-front.png` / `-side.png`; gate JSON
`scratch/treeqa/roundF/gate.jsonl`.

## Credits (scratch/tree_meshy_log.jsonl)

Balance went from 1309 to 1255, so **54 credits** were spent (cap 60):
3 t2i refs x 3 = 9, and 3 i23d meshes x 15 = 45. All submits were serial and blocking, and none returned 400 or 402. The guard was
updated first: `START_BALANCE 1309`, `CAP 60`, `MAX_TARGET 2000`. Refs were made before
any mesh on purpose: the t2i guard reserves 10 cr, so a ref re-roll after the meshes
would have been refused. The remaining 6 cr cannot buy a mesh, so a failed mesh could not have
been re-meshed. None failed.

## Gate arch: measured opening (b3-gate)

`scratch/gate_opening.py` rasterizes the front silhouette (projection along Z, so geometry at
any depth blocks) and finds, per row, the clear run containing the center column. The scan is limited to the walkable
band, above the floor sill and below 60% of the opening apex.

| GLB | clear opening (narrowest) | median | / ext X | apex above floor | / ext Y |
|---|---|---|---|---|---|
| b3-gate-pixelated.glb (as shipped) | 0.215 | 0.261 | **0.131** | 0.737 | 0.645 |
| b3-gate-open-pixelated.glb (leaves cut) | 0.5637 | 0.6075 | **0.3428** | 0.737 | 0.645 |

The brief's ~60-70% opening was a misread. The shipped mesh has two **door leaves standing
nearly closed** inside the doorway. The leaves are fused into the main welded component (132
comps, main = 6887 faces), so they cannot be dropped by component.
`scratch/gate_open_cut.py` derives `b3-gate-open-pixelated.glb`:
- It cuts 2074 faces inside each leaf's measured x/z slab, between the sill and the leaf tops (y < 0.06).
- It drops 56 faces of small crumb components left inside the doorway box.
- Masonry and the sill are untouched, and the source GLB is unchanged (`scratch/treeqa/roundF/b3-gate-open-front.png`).

The MANIFEST key `b3Gate` points at the derived file. Fitting 5.2 m to the as-shipped
0.215 opening would have made the gate ~40 m wide.

**Chosen scale**: s = fitOpening / (openingFrac x width) = 5.2 / (0.3428 x 1.6447) = **9.223**
(XY). Gate = 15.17 m wide x 10.53 m tall, and the opening apex is at 6.80 m. At uniform scale the depth would be
9.6 m, so Z is squashed by `arch.depthScale 0.45` (scaleZ 4.150) to 4.33 m. The opening center
(+0.0097 GLB units) is shifted onto x = 0 (offsetX -0.0895 m).

## Runtime integration

- `assets.js` MANIFEST: whWallA, whWallB, whLanternHang, b3Gate (-> b3-gate-open-pixelated).
- `CONFIG.js`: `boundaryWall` holds parameters only, plus the measured gate fractions with their source.
  `lightSockets.b3Gate` = { heightFraction 0.45 of the hung lantern, intensity 5.0, offset [0, 0] }.
- `region-manager.js`:
  - `whWallPlan(meta)` is THREE-free and pure, with a single plan for the shared disc.
  - `RegionManager.wallPlan()` caches the plan once every footprint is known and logs `[WH wall] {stats}` once.
  - `buildWorld()` instances the segments as one InstancedMesh per wall asset, so the wall is **2 draw calls**.
    Per-axis scale comes from `whBuildInstanced`'s new optional sx/sy/sz/y fields.
  - The arch is an unscaled group whose origin is the opening center. It holds the gate clone
    (scale 9.223, 9.223, 4.150) and the lantern child (hook top 5 cm into the apex stone).
  - `worldSockets()` feeds the light socket.
- `game.js` (one 3-line hook, not on the frozen list): world sockets are appended to the socket list.
  - dev: `computeSockets` (pool + flame cards).
  - feat/world-visuals: `computeFireSockets`, which feeds the pool + flame cards **and** the
    lock-light registry (`collectLockLights`).
- **World-level lifetime**: `buildRegion` calls `buildWorld()`, which builds once into a
  `world-boundary-wall` group added straight to the scene and guarded by `this.worldGroup`. It
  returns early and builds nothing until the plan is complete, so a partial group is never added.
  `disposeRegion` only walks region groups, so region swaps, pre-warms and hysteresis disposes never
  touch or re-add the wall.
- **Colliders**: `whPropColliders(regionId, meta, plan, wall)` appends wall circles on the
  region's side of the plane (pad 3 m). The chord and arch circles land in both regions. They are never
  `whMeetsCorridor`-exempt.

## Placement results (scratch/wall_mirror.py; byte-identical on dev and feat/world-visuals)

- Ring: N = ceil(2 pi 87.5 / (4.0 - 0.2)) = **145** segments, all placed. Chord between centers is 3.791 m and the
  instance is 4.0 m, so neighbours overlap 0.21 m. Radius range is 86.87-88.06 (circular 1-2-1-smoothed jitter of
  +-0.7, floor 86.5).
- Chords: **22 per side** (east and west), step 3.630 m from x = +-4.0 to the ring intercept at +-83.85.
- Exclusion sweep: **0 nudges, 0 drops**. The closest CONFIG prop is darkwood_edge#31 witchwood
  (-28.4, -79.9), 1.32 m edge to edge from ring segment 101.
- Instances: whWallA 95, whWallB 94. Scale (sx, sy, sz): A 2.106 / 3.118 / 1.474, B 2.106 / 3.082 / 1.474.
  That makes each segment 4.0 m long, 2.4 m tall and ~0.72 m thick; Y is stretched 1.48x over uniform.
- Colliders: **603** in total:
  - 567 wall circles: 189 segments x 3, r 0.45.
  - 32 arch leg circles, r 0.6, ringing two pillar blocks of x 2.6-7.58 by z -27.16 to -22.84.
  - 4 corner plugs, r 0.5, at (+-3.1, -22.84) and (+-3.1, -27.16), just outside the opening.
  - Per region after the side filter: hold_outskirts gets 431, darkwood_edge gets 350.
- The passable lane between the leg/plug inner edges is **5.20 m** (= arch opening).
- Ring continuity: the largest edge-to-edge gap between consecutive ring circles is 0.433 m, under the
  player's 1.4 m diameter.
- Lantern: base y 5.949, height 0.9 m (0.75 x 1.2), scale 0.4748. Socket at (0, 6.354, -25), intensity 5.0.

Mirror output: `scratch/roundF-proof/wall_mirror.json`. Two consecutive runs on each branch gave identical output.

## Determinism

`whWallPlan` reads only the following:
- CONFIG: boundaryWall, lightSockets, and both regions' props.
- `meta(name)`: Box3 footprints.

It reads no time, `Math.random`, player or frame state. It uses two mulberry32 streams seeded by
`seed ^ FNV1a('wall:ring'|'wall:chord')`, with a fixed draw count per segment drawn before the exclusion
test. Only `Math.sin`/`Math.cos` ulp differences could matter, and only at a knife-edge exclusion test. The
closest one is 1.32 m clear, so there are none.

## Performance note

The two wall InstancedMeshes draw 95 x 4118 + 94 x 4375 = **~802k triangles**. Whole-mesh frustum culling
never culls the ring, because it spans the disc. The contract's 2-draw-call layout costs this; if mobile frame time suffers, the lever
is decimating the two wall GLBs, which are ~4.1-4.4k tris each against the 2000 target.

## Proof stills (scratch/roundF-proof/, Blender 4.5 EEVEE)

The shots were built from the mirror plan with dev CONFIG props (`scratch/roundF_proof_scene.py`) and rendered with `roundF_proof_render.py`:
- `01-wall-pair-closeup.png`: ring segments 0 (A) + 1 (B).
- `02-wall-ring-wide-canopy.png`: the ring receding behind the region-B far witchwood / oaks.
- `03-gate-arch-lantern.png`: night, front view from region A. A 900 W Blender point light
  stands in for the pool light at the socket, so the brightness is illustrative, not the game's.

Render-script note: `roundE_proof_render.py` sets `.location.z -= zmin` and then reads
`.matrix_world` in the same tick, which is stale. Every object came out centered on the ground (half-buried). The Round F
renderer folds the lift into the matrix chain. The Round E stills likely carry the same offset.
