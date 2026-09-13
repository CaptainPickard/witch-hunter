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
