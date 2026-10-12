# CC-C8 validation verdict (Testerbot) - the Rot Mother's den instance (re-run 2: the TRIM)

**VERDICT: FAIL** (b + T: the trim's replacement "boulder" is the tree stump. `mossBoulderSmall` points at
`biome_library/m8-pixelated.glb`, which is the M8 **tree stump**, the same GLB as the existing `treeStump` key. It is
not a cheaper moss boulder. So 7 outcrop rows (one of them the lintel, now a stump floating 7 m up) and 6 den
shoulders render as stumps, which breaks the trim brief's own law: "WITHOUT changing any silhouette ... same shapes,
cheaper rock mesh". Everything else passes. **The tri budget (h) now passes:** the region-C worst circle is 1,949,432,
97.5% of 2M.)

- Builder commit: `eae8cbe` feat(cc-c8), author CaptainPickard, parent `a631fa6`. The first verdict was `f34e430`
  (FAIL h, tris).
- What I validated: eae8cbe plus the **uncommitted** CC-C8 TRIM working-tree diff (io/missions/2026-10-12-cc-c8-trim.md;
  scratch/cc_c8_trim_log.txt). That is 3 files, +54/-40: CONFIG.js sha256 `fee6ffdf80432237`, assets.js `8bec9f9f01ef1842`,
  v8-playable.html `86d0a017bb200e85`. The trim diff is NOT in this commit; IO commits it.
- Spec: scratch/cc_c8_valspec.md (sec 8 a-i, plus row T for the trim brief).
- Method: HEADLESS. `node scratch/cc_c8_check.js a631fa6 WT` (node v22.23.3) exits 1 with FAIL (b,T).
  `node scratch/cc_c8_ledger_probe.js . -84 -309 170`. No harness, browser, game run or network.
- Line numbers are from the worktree.

| id | check | result | evidence (line numbers @ worktree) |
|----|-------|--------|------------------------------------|
| a | regionD + C<->D door + C row gone + rotLair reshaped | PASS | CONFIG regionD L1054: id rot_den L1055, groundRadius 34 L1058, fog 0x05070a / 0.12 L1069-1070, ambient 0.06 L1071. region-defs registers it at L46; the door connection is pushed at L93, sides C -1 / D +1 at L111-112. vm: 1 connection, door, planeZ -295.6. C enemies 23 -> 22, rotmother rows 1 -> 0 (removal note L602). C rotLair L1029: stains L1030, void L1038, no light, fog or pool.radius. Outcrop rows (cullM 120): 26 (25 - 1 gate + 2 bramble). keepOut at L501 |
| b | den build rows | **FAIL** | regionD.props from L1113. 10 ring segments at r 24.0, wall 8 each. 9 boulder rows = 3 mossBoulder + **6 mossBoulderSmall, and those 6 are the tree stump** (assets.js L75 -> m8-pixelated.glb, the same file as treeStump at L63; docs/planning/59-biome-object-library.md L129 "M8, Tree stump", L130 "M9, Moss boulder"). Everything else passes: 4 stoneSteps, 2 skullPile, 6 blightcap, 8 graveMound (5 nest ring r 7.5 + 3 brood); pool r 10 L1164; light 1.6 / h 1.2 L1166; exit gap 7.01 m collider edge-to-edge, centred (-175.00,-295.57); lane +-2.81 inside the door window +-3; widest other hole 1.01 m < 1.4 m body; seat region-manager L1833; flat disc |
| c | lair re-home + params byte-equal C7 | PASS | rotmother.lair L1754 -> rot_den, world (-175,-265). regionD.lairs row L1103. enemy.js lairNest letter=flag L1106, lairFlag L1093. vm deep-equal against bef33f1: rotmother minus lair = true, rotspawn = true. Lair rows are instanced after the enemy rows at region-manager L1909 |
| d | E-to-enter 3.5 m + 0.8 s fade + walk-back, no pause/menu | PASS | door L1080: interactM 3.5 L1086, fadeIn 0.3 + fadeOut 0.5, exitFadeOut 0.8 L1094, prompt L1095. game.js: interact chain L1863, tryDenDoor L1876, forceCross L1882, prompt L2172, fade L1891 / L1916, tick L2953, walk-out dip L2960. region-manager: portalNear L128, forceCross L144 / L2047, planeIn filter L49. vm logic sim: all 10 cases true (no crossing in C, portal at 3.4 m yes / 3.6 m no, forceCross land, no portal in D, no crossing inside, walk-out, no bounce-back, window-only, hysteresis) |
| e | always-dark phase + light rules | PASS | constantPhases.rot_den L2853: moon 0, exposure 0.75 L2856, stars 0.15, disc 0.2 L2860. Hemi = base x 0.06 (game.js L1358). daynight.js: constantRow L225, setArea skip L391, SkyPool.tick L444, copyRow L500 after an untouched coreTick L494. Nest light: cleared-skip enemy.js L1568, polled per frame (game.js L2720 -> L2769). Death flag L1163, re-arm L1132, fog cards L1418. No region light on her or the spawns |
| f | save round-trip + pre-C8 compat | PASS | Flag key rotmother_cleared_C is byte-equal to C7 (lairNest L1106). captureLairs L1538 / restoreLairs L1546; a missing block means all armed (L1548). game.js WH_SAVE capture L2567 / restore L2581. Den roster is index 0; the prune boundary counts lair rows (enemy.js L1278). save.js validRegion L40. save.js diff: none |
| g | scope audit a631fa6..worktree | PASS (1 flag) | eae8cbe files as before, plus the trim, which touches only CONFIG.js, assets.js and v8-playable.html (all allowed). FORBIDDEN touched: none. The daynight.js flag (+30/-0, sec 6 sanctioned) carries over from f34e430, non-blocking. The untracked docs/planning/64-*.md predates C8 and isn't in any C8 diff |
| h | node --check + bundle + tris ledger | PASS (trim gate) | node --check OK on CONFIG, assets, daynight, enemy, game, region-defs, region-manager and both scratch scripts. Bundle is 3,252,430 B (matches the trim log) and inlines every edited js verbatim. **Probe: C8 LAYOUT worst 170 m circle = 1,949,432 (97.5% of 2M) at (-84,-309)**, 1,854,909 without the outcrop, missing tri rows: none. Raw new tris: outcrop 26 rows = 146,355, den 39 rows = 235,470, pools/stains ~1.2k, total 383,051. That is still well over sec 7's <= 40k target, which the trim brief replaces with the < 2M probe gate (W9) |
| T | TRIM brief conformance | **FAIL** (silhouette) | vm row diff against eae8cbe. C: gone = [cemeteryGate @ -134.4,-228.9]; added = bramble (-135.2,-227 s2.0) + (-133.6,-226.2 s1.6); 7 swaps. D: 0 gone, 0 added, 6 swaps. Every kept row's x/z/rotY/scale/y/wall/sy/sz/tint/cullM/noCollide is identical, and the non-prop blocks of C and D are equal. Manifest row assets.js L75; bootCritical L2010. **Silhouette: FAIL.** m8 is the tree stump (8,109 tris, raw ext 1.898 x 1.827 x 0.342) against m9's boulder (1.897 x 1.402 x 0.327). The brief's "boulder family, 1.9 x 1.8 x 0.34 slab" description is wrong; the error is in the brief, and the builder followed it as written |

## Why it fails, and the fix
The trim brief picked m8 by tri count (8,109), and m8 is the stump. The builder did exactly what the brief asked, so the
error is upstream, in the brief. Options for a ruling:
1. **Bake a real low-poly moss boulder.** Decimate m9 to <= ~8k tris (the same pipeline that took rotmother from 182k
   to 17.6k) and point `mossBoulderSmall` at it. Nothing else changes and the probe stays at ~1.95M. Recommended.
2. Swap fewer rows. Cutting the gate alone leaves C at ~2.039M, still over. The outcrop needs about 40k more trimmed,
   for example by dropping 2 horseshoe boulders or switching 3 of them to a <= 8k boulder. The den swaps don't affect
   C's ledger at all: D never draws with C.
3. Nicko accepts stumps as outcrop and den dressing. Even then, the lintel row (y 7.0, a stump floating over the
   doorway) needs a different asset.

## Testerbot deviations (my own)
- T1-T4 are as in f34e430: wall-collider x-extent from the GLB accessor, the h ledger is a header upper bound, d uses a
  vm logic simulation, and f checks the den roster as session state.
- T5: This run validates an uncommitted working tree. The checker gained a `WT` mode (diffs against the worktree;
  bundle bytes 3,252,430; outcrop 26; h gated on the probe < 2M), plus the boulder-identity sub-check in b and row T.
- T6: I added `"mossBoulderSmall": 8109` to the probe's tri table, as the trim builder flagged. Without it the probe
  reads low (1,892,669, with a NaN outcrop total).
- T7: The silhouette verdict comes from asset identity (manifest path equality + the doc 59 asset table), not from a
  render. Seeing it would need a runtime or render pass, which is out of scope for a headless run.

## Builder deviations (trim; non-blocking on their own)
- DT1: For the den's third m9 row the builder kept the 2.30 row, because the largest (2.40) is already a gap flanker.
  That reading is sound.
- DT2: The 2 new brambles got rotY 3.67 (the cut gate's angle) and 5.30. The brief gave none.
- D1-D7 from f34e430 still stand: mouth ~6.2 m visual / 7.0 m collider, hemi mult 1.0, per-axis wall scale, 3 manifest
  rows, door helper rows, enemy.js refactor, fog d95 14.4 m.

## Watch-items (i, runtime only, not verified)
1. Fade timings: 0.3 s to black, the cross, 0.5 s up. Walk-out starts black and lifts over 0.8 s. A death mid-dip
   cancels the dip. Check that the camera carry-over hides the ~60 m jump.
2. Doorway sightline: check that the 4.6 x 9 m void card in the recess reads as depth. The wall ends poke ~0.35 m
   past the mouth plane. With one gate leaf the east jamb is bramble only, so check the doorway still frames.
3. Torch radius 10.5 m vs the 24 m cavern under a 14.4 m fog d95. The nest light at 1.6 is the only landmark.
4. Her 4.2 m body vs the ~9 m walls, and the 6 m minion ring vs the egg-sac ring at r 7.5.
5. Wolves and bandits outside: outcrop colliders and keepOut near the patrol line. The plane-hold skip is at
   region-manager L253ff.
6. Camps can be pitched inside the den, and a quit-save in the den makes CONTINUE build regionD at boot.
7. forceCross keeps C resident while D is active.
8. Outcrop cullM 120 pop-in. C is at 97.5% of the ledger, so ~50k of headroom remains for anything else in that circle.
9. **Sec 7's <= 40k raw new-tris target is replaced only by the trim brief's < 2M probe gate.** 383k raw new tris ship
   (the den's 235k never draws with C). Nicko should confirm the gate change explicitly.
10. `mossBoulderSmall` and `treeStump` share one GLB path. The loader caches by logical name (assets.js L186
    `cache = {}  // logical name -> ...`), so the same file is probably loaded and parsed twice. Option 1 fixes this
    too.
