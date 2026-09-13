# Meshy 3D Pipeline Validation - Stage Log (doc 29)

Character: gravedigger undead (char-07 canon, doc 24).
Input prep: 2 image-gen rounds (round 1 produced a multi-view sheet,
rejected; round 2 clean single-figure A-pose, vision-QA'd PASS).
Input hosted: raw.githubusercontent.com/CaptainPickard/witch-hunter/dev/
art-direction/3d-spike/gravedigger-apose-front.png (committed dev).

| Stage | Task/Tool | Started | Done | Elapsed | Notes |
|---|---|---|---|---|---|
| S-A1 reference sheet | gpt-image-2-high, 2 rounds | 15:19 | 15:21 | ~2 min | round 1 rejected by vision QA (multi-view sheet) |
| S-A2 hosting/commit | git push + raw URL check | 15:22 | 15:22 | <1 min | HTTP 200 verified |
| S-B1 image-to-3d | Meshy meshy-5, quad, 15k tris, symmetry auto | 15:24 | pending | pending | task 01a09b5b-6f19-7611-b9f5-ada2d1fd78d2 |
| S-B2 download + inspect | GLB via curl + trimesh/manual | pending | | | poly count, texture res, rig presence |
| S-B3 re-texture recipe | posterize + nearest-neighbor pass | pending | | | recipe prototype due after mesh lands |
| S-C1 UE5 scene | BLOCKED: engine access | | | | scene spec in doc 29 |

Open blockers after B stage: engine access (Nicko machine or hosted
runner) for S-C; re-texture tooling (PIL recipe) runnable here.
## PRODUCTION RUN 2026-09-13 (Phase 1 at production scale, doc 29 validation plan)

46 assets generated end to end: 10 race bodies (15k tris), 9 weapons (2k),
8 armor pieces (helms 3k / chests 5k), 15 church-kit props (2k), 4
graveyard props (2k). Every asset: single-object or single-figure concept
ref from the closest canon frame (image_generate + vision_analyze gate),
hosted on dev raw URLs, Meshy image-to-3d (meshy-5, quad, symmetry auto,
15 credits each), UV-preserving decimation to tri target, pixelated
register re-texture pass. Full per-asset table with task ids:
art-direction/3d/asset-manifest.md. Viewable/equippable in
art-direction/3d/arsenal-viewer.html (self-contained three.js page with
head/chest/right-hand/left-hand equip slots, verified in headless Chromium).

| Stage | Result | Notes |
|---|---|---|
| S-A1 refs (46) | PASS | 46/46 first-round vision QA PASS, 0 regen rounds (spike round 1 body needed 1 retry; production refs needed 0) |
| S-A2 hosting | PASS | all raw refs + GLBs committed dev, HTTP 200 spot-verified |
| S-B1 image-to-3d | PASS | 46/46 SUCCEEDED, ~2-3 min each; Meshy burst rate limit ~1 submit/min after first 10, handled with backoff |
| S-B2 download+inspect | PASS | 690 credits total of 700 cap; tri targets hit via UV-preserving fast-simplification + nearest-neighbor UV resampling |
| S-B3 re-texture | PASS | retexture.py (256px, 48-color MEDIANCUT, 5-bit posterize) applied to all 46; UV retention fix added for trimesh GLB export |
| S-C1 UE5 scene | still BLOCKED | engine access unchanged; three.js viewer remains the representative viewer |
| S-C2 equip slots | PASS (new) | arsenal-viewer.html: 4 slots (head/chest/rh/lh), anchors measured from human-hunter-male mesh, headless-browser verified; per-body sockets still rig-stage |

Production-run economics: 46 assets in ~2.5 h wall clock, 690 credits
(~15/asset, 0.46 USD-equivalent each at Pro 1000/mo), zero failed tasks,
zero skips. The doc 29 pipeline is now validated at production scale for
characters, props, and modular kit pieces.

---

## DEFECT FIX 2026-09-13 (arsenal viewer render defect, post-production-run)

Defect: race bodies rendered wrong in the browser viewer: black silhouette,
white salt-and-pepper speckle, detached floating shards near arms and feet,
geometry reading as mangled. Python ortho previews of the same GLBs were
correct, so the browser render path was suspect.

Root causes (three, all verified by bisect + headless Chromium A/B):
1. Decimation debris: every race body ships with ~300-1000 disconnected face
islands from the Meshy source mesh; the 15k decimation orphaned tiny
components. Worst case human-hunter-male (its pixelated GLB was re-decimated
separately from raw): main body shattered 4855 to 1375 faces, 358
far-floating shard components. Measured with welded-vertex adjacency
(union-find at 1e-4 tolerance), not raw vertex adjacency (UV-seam duplicates
lie).
2. Backface culling: the fractured shells have real gaps; three.js FrontSide
culling turned every gap into a see-through hole (the white speckle read as
texture noise but was background showing through the body).
3. Color encoding: GLTFLoader assigns sRGBEncoding (3001) to base-color
textures, but the r147 renderer default outputEncoding is LinearEncoding
(3000). sRGB texels decoded to linear and never re-encoded: texel 35/255
rendered ~11/255. The black silhouette was a page bug, not an asset defect.

Fixes:
- art-direction/3d/drop_shards.py: drops face components that are BOTH tiny
(under 10 faces) AND farther than 0.01 from the main body surface (cKDTree to
the largest component's vertices). Applied to all 10 race pixelated GLBs:
4,299 components dropped, UVs + 256px atlases preserved. Backup of pre-fix
GLBs kept at /tmp/glb_backup_races (session-local, not committed).
- arsenal-viewer.template.html: material.side = THREE.DoubleSide in
pixelFilter; renderer.outputEncoding = THREE.sRGBEncoding; pixelated
minFilter = NearestMipmapLinearFilter with mipmaps on (was full Nearest with
generateMipmaps false, which made the dark atlas salt-and-pepper at
distance). Rebuilt arsenal-viewer.html with build_viewer.py.

Verified: headless Chromium screenshots before/after (shards gone, no
see-through holes, figure reads as upright cloaked hunter with visible dark
browns/greys). Deployed /art-3d-viewer route serves the file live from disk,
byte-identical, no WebUI restart needed.

Tooling committed alongside: drop_shards.py (shard-removal post-pass),
shard_diagnose.py + weld_comps.py (connectivity diagnostics), uv_stats.py
(atlas/UV island stats), shoot_viewer.py (playwright screenshot harness),
bisect.template.html + build_bisect.py (raw-vs-pix x nearest-vs-linear
bisect harness), check_encoding.py (r147 encoding constant check).
