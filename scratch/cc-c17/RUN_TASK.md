# CC-C17v2 IMPLEMENTATION RUN - THE BINDING TASK

You are the CC-C17v2 implementation agent for the Witch Hunter repo,
worktree /tmp/wh-worldfeat (branch feat/world-visuals). MAX long-horizon run
(~200 turns; use them). Your task document is:

    io/missions/2026-10-20-cc-c17b-integration-v2.md

Read it COMPLETELY first, then execute THE WORK (v2 ORDER, steps 0-8) exactly.
The v2 brief SUPERSEDES io/missions/2026-10-20-cc-c17-integration-brief.md
(the v1 brief) everywhere they differ - including the fence-corner ruling:
ok-fence-corner-v2 IS usable (2 rows in the farm yard fence kit). The v1
brief's farm layout (barn/silo/haybales), ruins-replacement plan, tree
scatter-table plan and spooky-dressing full set are REPLACED by the v2 brief's
trimmed set. Do not import v1-only requirements.

## RUN-SPECIFIC FACTS + SANCTIONS (IO, binding)

1. MANIFEST LOCATION: the manifest is the `var MANIFEST = {` object at the top
   of prototype/js/assets.js (L16.., existing keys like gravestoneObelisk,
   blightcap, b6Bones). Add the manifest rows THERE (comment // CC-C17),
   relative paths 'art-direction/3d/assets/old_king/ok-...-pixelated.glb',
   NOT bootCritical. (window.WH_CONFIG.assets is a SETTINGS object - retry
   counts etc - not the manifest; do not add asset rows to it.)
2. MANIFEST KEYS (10, camelCase like existing keys) - the v2 brief lists 9
   + this sanction adds the 10th:
   okFarmCottage, okFarmWell, okTreeOak, okTreePine, okFencePost,
   okFenceGate, okFenceStonewall, okFenceCornerV2, okRuinArch,
   okRuinColumn  <- SANCTIONED 10th row (the v2 brief orders 2
   ok-ruin-column rows in the ruin accent but omits the manifest row; props
   rows cannot resolve without it). Use these exact key spellings in rows.
3. SCALE LAW (props rows carry RAW scale; ok-* GLBs are ~1.9 height-units):
   scale = desiredHeight / 1.9. cottage 7.0 m -> 3.68; well 2.4 -> 1.26;
   fencePost 1.2 -> 0.63; gate 2.5 -> 1.32; okRuinArch 7.2 -> 3.79;
   okRuinColumn 7.5 -> 3.95. WHERE THE V2 BRIEF NAMES THE SCALE DIRECTLY the
   brief wins: ok-fence-corner-v2 scale 1.5; sentinel oaks scale 12-14;
   N road bend pine scale 12. Stonewall rows carry scale = len/1.9.
   Nominal widths at scale 1 (collider ESTIMATES): okFarmCottage 6.5,
   okFarmWell 2.0, okTreeOak 6.0, okTreePine 6.0, okFencePost 0.4,
   okFenceGate 2.5, okFenceStonewall 2.5, okFenceCornerV2 1.5,
   okRuinArch 4.0, okRuinColumn 1.5. TRUNK regex catches okTreeOak/
   okTreePine (/tree|oak/ -> x 0.25 colliders).
4. TRI TABLE for your ledger (GLB-header tris, measured): okFarmCottage ~9800,
   okFarmWell ~2600, okTreeOak ~28700, okTreePine ~22600, okFencePost ~2100,
   okFenceGate ~6700, okFenceStonewall ~9000, okFenceCornerV2 ~2500,
   okRuinArch ~7900, okRuinColumn ~5200. Plus the four unlisted C13b kit
   assets the v2 brief says to count: churchArchway 4000,
   churchCornerButtress 2000, stoneSteps 5000, stoneCrossTilted 4000.
5. OUTPUT DISCIPLINE: after each of the v2 steps (2..6) print one line
   `STEP <n> DONE rows <N> ledger <PASS/FAIL>`; never stop mid-run to ask.
   Finish with the v2 brief's summary block + exact final line
   `CC-C17 INTEGRATION-V2 DONE rows-added <N> ledger PASS build <bytes>`
   (substitute real values; PARTIAL/FAIL if any step could not complete).