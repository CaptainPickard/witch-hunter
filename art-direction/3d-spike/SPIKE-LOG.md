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