# CC-C17v2 INTEGRATION REPORT (Claude Code lane, 2026-10-20)

Brief: io/missions/2026-10-20-cc-c17b-integration-v2.md (supersedes v1), run task
scratch/cc-c17/RUN_TASK.md. No git, no harness/browser/server. Edits UNTRACKED:
prototype/js/assets.js (MANIFEST object only), prototype/js/CONFIG.js (regionC.props
data rows), prototype/builds/v8-playable.html (rebuilt), scratch/cc-c17/*.

## Result
- Manifest: 10 rows (9 from the brief + the sanctioned okRuinColumn), NOT bootCritical.
- regionC.props: **28 rows appended** (farm 14, ruin accent 3, trees 3, spooky 8).
- 54 existing giant rows got `cullM: 140` (row-shape law; see Decision D6). x/z/rotY/scale unchanged.
- Ledger: **PASS**. Worst 1,895,571 (94.78%) at centre (0,-366); 1,876,200 (93.81%) at (-175,-266).
- Build: prototype/builds/v8-playable.html **3,273,645 bytes**. `node --check` OK for CONFIG.js and assets.js. All 5 block markers and 10 manifest keys are in the bundle.

## Steps
| step | rows | ledger after step (centre 1 / centre 2) |
|---|---|---|
| 1 manifest | 10 manifest keys | 1,883,576 / 1,858,603 (pre-C17 baseline incl. the 17k C13b kit) |
| 2 farm | 14 | 1,927,185 (96.36%) / 1,855,949 PASS |
| 3 ruin accent | 3 | 1,927,185 / 1,855,949 PASS |
| 4 trees | 3 | 1,927,185 / 1,905,304 (95.27%) PASS |
| 5 spooky | 8 (+54 giant cullM) | 1,895,571 (94.78%) / 1,876,200 (93.81%) PASS |
| 6 ledger2.py | - | PASS (whole-disc R 280 scan: 1,895,571 at (-102,-282)) |

## Rows (world x, z; nearest NON-C17 prop / road / fire / loop / den opening, from final_probe.txt)
FARM. Cottage (150.5,-256.7); yard centre (150.4,-263.7) is at bearing 124, r 182 from the Stone.
Cluster centre distances: props 30.0, roads 104.3, fires 62.0 (Bravo), loop segments 67.2, all zones clear. Ground span 1.4 m.
- okFarmCottage (150.5,-256.7) rotY 3.15, scale 3.68 (7.0 m). Door +Z faces the nearest road (eastRoad, N).
- okFarmWell (154.9,-264.7) scale 1.26.
- Front line z -269.7: okFenceGate (150.4) `wall:2` scale 1.32; 4 okFencePost rail sections (147.4 / 143.9 / 153.4 / 156.9) `wall:3` scale 1.85; okFenceCornerV2 brackets at (141.7) and (159.1), scale 1.5.
- Side lines x 141.7 and 159.1: okFenceStonewall at z -266.5 `wall:4` scale 2.5; okFencePost at z -262.2 `wall:3`.
- lanternPost (148.2,-271.3) scale 2.535: the amber gate beacon.
- Every farm row: props ≥ 23.3, roads ≥ 96.7, loops ≥ 57.3 (segments).

RUIN ACCENT. Added to the C13b C1 cluster; no church-kit rows removed.
- okRuinArch (-111.2,-201.7) rotY 2.10, scale 3.79. Its opening faces the cluster.
- okRuinColumn (-114.2,-206.9) and (-108.2,-196.5), scale 3.95. Each sits 6 m off the arch along its X axis, so nothing interpenetrates.
- Cluster envelope: 8 rows, centre (-105.3,-205.1), r 9.1. Nearest non-cluster prop is 14.7 m: the C4a boulder field, which the brief sanctions as a tight cluster. Each new row is ≥ 20.6 m from every non-cluster prop.

TREES (cullM 140).
- okTreeOak (-110.3,-158.5) scale 13: bearing 208, r 235.
- okTreeOak (-200.3,-272.6) scale 12.5: bearing 245, r 221.
- okTreePine (-13.0,-567.0) scale 12: road 10.4, props 26.1.

SPOOKY.
- deadTree (-144.7,-180.8) scale 8.6, cullM 140.
- deadTree (-176.5,-233.0) scale 9.2, cullM 140.
- skullPile (-148.7,-206.6) scale 1.2: 15.2 m from the doorway.
- blightcap (-149.8,-233.5) scale 1.4 and (-123.1,-199.6) scale 1.6.
- Ring fragment: 3 mossBoulder (-76.3,-140.4) 2.8 / (-80.7,-144.2) 2.2 / (-86.6,-144.1) 2.5, each with y = -0.3 × height (half-swallowed). Centre bearing 200, r 244. Slopes ≤ 5.8°.
- The corridor rows are spaced at least 26.1 m from each other.

## Decisions / deviations (each one was probe-driven and is recorded in the generator scripts)
- **D1 Stonewall count.** The fence-kit summary says x4, but THE WORK step 2 says "2 stonewall". RUN_TASK binds THE WORK, so I placed 2.
- **D2 Fence-post scale is 1.85, not 0.63.** The scale law assumes the GLBs are ~1.9 units tall. ok-fence-post is a 2-post, 2-rail SECTION: 1.90 long × 0.65 tall (GLB header and concept ref). I followed the law's intent (desiredHeight 1.2 m / measured 0.65). Scale 0.63 would have made a 0.4 m-tall, 1.2 m-long toy.
  - The stonewall is the same shape (0.65 tall), so scale = len/1.9 = 2.5 gives 4.75 m long, 1.6 m tall.
  - Fences, stonewalls and the gate use the existing `wall: N` row field. It gives segment colliders along the row's local X (the CC-C8 outcrop tech, region-manager whPropColliders), not one fat circle.
- **D3 Measured tris differ from the IO table.** okFarmCottage is 28,632 (table ~9,800) and okFarmWell is 11,481 (table ~2,600). The ledger uses max(IO table, GLB header) per asset (scratch/cc-c17/glb_measure.py).
- **D4 The brief's nominal slots failed the 26 m gate.** Each one took the nearest clear slot (deterministic scans):
  - Oak at bearing 210: a boulder was 17.8 m away. Moved 8.7 m.
  - Oak at bearing 240: the camp-3 fire was 8.0 m away. Moved 22.6 m, to bearing 245.
  - Pine at (-15,-570): a scree boulder was 22.7 m away. Moved 3.6 m.
  - Ring fragment: r 238 failed the gates, so it sits at r 244. The fragment's arc still bows in to r ~237.
- **D5 Den-corridor prop gate.** A 26 m gate against every prop is infeasible in the bearing-225 band at r 200-235 (3 of 3,321 grid points, all one spot). I used 26 m as the mutual spacing (brief) and ≥ 10 m to every prop row as the dressing gate. Extra keep-outs: doorway ≥ 12, stains ≥ 4 + radius, the walking line on the bearing-225 axis kept clear (lateral 6-32 m), camp-3 guards ≥ 12. Seed random.Random(20261020).
- **D6 Giant rows got cullM 140.** The v2 ROW SHAPE LAW describes the C4b giants as `{..., cullM: 140}`, but the live rows had NO cullM (they hide at 170). With the brief's full set the ledger measured 2,071,776 (103.6%) on the west plateau (-70,-252). It still failed after:
  - swapping deadTree for youngDeadTree: 2,018,688;
  - also giving both oaks cullM 120: 1,998,039;
  - keeping deadTree and dropping the whole ring fragment: 2,006,979.
  - Fix: the 54 live yew/witchwood giant rows got `cullM: 140` (a 128.8 m show band). By CONFIG's own FOG-CULL COHERENCE rule that is past the 94.2 m fog-visible reach at the thinnest C fog, so there is no visible pop. CC-C8 set the precedent with cullM 120 on its outcrop.
  - This kept every brief row as specified (deadTree x2, 3 mossBoulder at bearing 200).
  - Rollback: strip `, cullM: 140 },   // CC-C17 shape` back to ` },`. Without it the C17 set does not fit 1.98M.
  - **IO: please ratify or revert this.**
- **D7 The farm is far from any road.** The east-of-spine pocket with r 150-200, props ≥ 26, fires ≥ 45 and loops ≥ 60 has only 27 clear 2 m slots, and all of them are ~100 m from a road. So the cottage faces the nearest road (eastRoad) from a remote homestead. The glade-to-Stone spine side was full: se/ss packs and Bravo.
- **D8 Deferred, as the brief says:** barn, silo, haybales, ok-ruin-rubble, ok-ruin-wall-*, ok-fence-corner v1/v3. They have no manifest rows.

## Ledger output (python3 scratch/cc-c17/ledger2.py)
```
CC-C17 rows appended to regionC.props: 28  (blightcap x2, deadTree x2, lanternPost x1, mossBoulder x3, okFarmCottage x1, okFarmWell x1, okFenceCornerV2 x2, okFenceGate x1, okFencePost x6, okFenceStonewall x2, okRuinArch x1, okRuinColumn x2, okTreeOak x2, okTreePine x1, skullPile x1)
CC-C17 added tris (sum, before cull): 330700
giant rows with cullM 140 (CC-C17 shape): 54
C13b kit rows counted: churchArchway 4000 churchCornerButtress 2000 stoneSteps 5000 stoneCrossTilted 4000
LEDGER centre (0,-366) R 170: worst 1895571 = 94.78% of 2M at (-102,-282)  missing none  -> PASS
LEDGER centre (-175,-266) R 170: worst 1876200 = 93.81% of 2M at (-103,-278)  missing none  -> PASS
whole disc (0,-366) R 280 (info): worst 1895571 = 94.78% at (-102,-282)
LEDGER PASS (cap 1980000)
```

## Tools (scratch/cc-c17/)
- dump_cfg.js, heights.js: node CONFIG / heightfield readers.
- probe_lib.py: gates.
- glb_measure.py: GLB header tris and bbox.
- gen_farm.py, gen_ruin.py, gen_trees.py, gen_spooky.py: placement generators.
- apply_rows.py: appends rows at the END of regionC.props.
- apply_giant_cull.py: the D6 edit.
- ledger2_probe.js + ledger2.py: the step-6 ledger.
- field_lib.py, opt_west.py: budget search aids.
- final_probe.py → final_probe.txt.

Build: `python3 tools/build_v8.py` produced 3,273,645 bytes.
