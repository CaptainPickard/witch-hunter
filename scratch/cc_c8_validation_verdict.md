# CC-C8 validation verdict (Testerbot): the Rot Mother's den instance (re-run 3, TRIM 2)

**VERDICT: PASS** (a-h and T2 all pass. The region-C worst 170 m circle is 1,914,268 tris, 95.7% of 2M. The real m9
boulder is kept everywhere and no tree stump remains. Two sec-8 numbers are superseded by IO's trim briefs: watch-items
9 and 11.)

- Builder commit: `eae8cbe` feat(cc-c8), author CaptainPickard, parent `a631fa6`. Earlier verdicts: `f34e430` (FAIL h,
  tris) and `7ea710d` (FAIL b/T, trim 1 swapped in the M8 tree stump).
- What I validated: eae8cbe plus the **uncommitted** TRIM 1 + TRIM 2 working tree (io/missions/2026-10-12-cc-c8-trim.md,
  io/missions/2026-10-12-cc-c8-trim2.md; scratch/cc_c8_trim2_log.txt). Against eae8cbe only CONFIG.js and the bundle
  differ (assets.js is byte-identical again). File hashes (sha256/16): CONFIG.js `7be4c899481c4f19`, assets.js
  `4a50b788dbb5a238`, v8-playable.html `d7af162d3598c825`. The trim diff is NOT in this commit; IO commits it.
- Spec: scratch/cc_c8_valspec.md (sec 8 a-i, plus row T2 for the trim-2 brief).
- Method: HEADLESS. `node scratch/cc_c8_check.js a631fa6 WT2` (node v22.23.3) exits 0 with PASS.
  `node scratch/cc_c8_ledger_probe.js . -84 -309 170`. No harness, browser, game run or network.
- Line numbers are from the worktree.

| id | check | result | evidence (line numbers @ worktree) |
|----|-------|--------|------------------------------------|
| a | regionD + C<->D door + C row gone + rotLair reshaped | PASS | CONFIG regionD L1049: id rot_den L1050, groundRadius 34 L1053, fog 0x05070a / 0.12 L1064-1065, ambient 0.06 L1066. region-defs registers it at L46; the door connection is pushed at L93, sides C -1 / D +1 at L111-112. vm: 1 connection, door, planeZ -295.6. C enemies 23 -> 22, rotmother rows 1 -> 0 (removal note L602). C rotLair L1024: stains L1025, void L1033, no light, fog or pool.radius. Outcrop rows (cullM 120): **20** (25 - 1 gate - 6 horseshoe + 2 bramble). keepOut at L501 |
| b | den build rows | PASS (count per trim 2) | regionD.props from L1108. 10 ring segments at r 24.0, wall 8 each. **4 boulder rows, all mossBoulder = m9** (assets.js L64 m9-pixelated.glb, 21,599 tris). 0 mossBoulderSmall. 4 stoneSteps, 2 skullPile, 6 blightcap, 8 graveMound (5 nest ring r 7.5 + 3 brood). Pool r 10 L1154; light 1.6 / h 1.2 L1156. Exit gap 7.01 m collider edge-to-edge, centred (-175.00,-295.57); lane +-2.81 inside the door window +-3. Widest other ring hole 1.01 m < 1.4 m body; ring closure comes from the wall colliders only, so the cut shoulders don't open it. Seat region-manager L1833. Flat disc |
| c | lair re-home + params byte-equal C7 | PASS | rotmother.lair L1744 -> rot_den, world (-175,-265). regionD.lairs row L1098. enemy.js lairNest letter=flag L1106, lairFlag L1093. vm deep-equal against bef33f1: rotmother minus lair = true, rotspawn = true. Lair rows are instanced after the enemy rows at region-manager L1909 |
| d | E-to-enter 3.5 m + 0.8 s fade + walk-back, no pause/menu | PASS | door L1075: interactM 3.5 L1081, fadeIn 0.3 + fadeOut 0.5, exitFadeOut 0.8 L1089, prompt L1090. game.js: interact chain L1863, tryDenDoor L1876, forceCross L1882, prompt L2172, fade L1891 / L1916, tick L2953, walk-out dip L2960. region-manager: portalNear L128, forceCross L144 / L2047, planeIn filter L49. vm logic sim: all 10 cases true (no crossing in C, portal at 3.4 m yes / 3.6 m no, forceCross land, no portal in D, no crossing inside, walk-out, no bounce-back, window-only, hysteresis). No pause/menu token in the den-door block |
| e | always-dark phase + light rules | PASS | constantPhases.rot_den L2842: moon 0, exposure 0.75 L2845, stars 0.15, disc 0.2 L2849. Hemi = base x 0.06 (game.js L1358). daynight.js: constantRow L225, setArea skip L391, SkyPool.tick L444, copyRow L500 after an untouched coreTick L494. Nest light: cleared-skip enemy.js L1568, polled per frame (game.js L2720 -> L2769). Death flag L1163, re-arm L1132, fog cards L1418. No region light on her or the spawns |
| f | save round-trip + pre-C8 compat | PASS | Flag key rotmother_cleared_C is byte-equal to C7 (lairNest L1106). captureLairs L1538 / restoreLairs L1546; a missing block means all armed (L1548). game.js WH_SAVE capture L2567 / restore L2581. Den roster: regionD.enemies [] + lairs[0] = index 0; the prune boundary counts lair rows (enemy.js L1278). save.js validRegion L40. save.js diff: none |
| g | scope audit a631fa6..worktree | PASS (1 flag) | Code files: CONFIG, assets, daynight, enemy, game, region-defs, region-manager, the bundle, plus scratch. FORBIDDEN touched: none. Trim 2 itself touches only CONFIG.js, the bundle and the scratch probe; assets.js is back to eae8cbe byte-for-byte. The daynight.js flag (+30/-0, sec 6 sanctioned) carries over from f34e430, non-blocking. Untracked and not in any C8 diff: `biome_library/m8-boulder-small.glb` (unreferenced: grep of prototype/js finds no mossBoulderSmall or m8-boulder-small) and docs/planning/64-*.md (predates C8) |
| h | node --check + bundle + tris ledger | PASS (trim gate) | node --check OK on CONFIG, assets, daynight, enemy, game, region-defs, region-manager and both scratch scripts. Bundle is **3,251,156 B** (matches the trim-2 log) and inlines every edited js verbatim. **Probe: C8 LAYOUT worst 170 m circle = 1,914,268 (95.7% of 2M) at (-84,-309)**. Without the outcrop it is 1,854,909 (92.7%) at (32,-427); missing tri rows: none. The outcrop's 111,191 tris agree between the probe table and the checker's GLB scan. Raw new tris: outcrop 20 rows = 111,191, den 34 rows = 208,415, pools/stains ~1.2k, total 320,832. That is still above sec 7's <= 40k target, which the trim briefs replace with the < 2M probe gate (watch-item 9) |
| T2 | TRIM 2 brief conformance | PASS | vm row diff against eae8cbe. **C gone**: cemeteryGate (-134.4,-228.9) + mossBoulder (-148.2,-213.6), (-144.1,-209.8), (-138.5,-211.5), (-128.1,-219.3), (-124.9,-224.2), (-127.4,-229.2), exactly the 6 the brief lists. Added: bramble (-135.2,-227 s2.0) + (-133.6,-226.2 s1.6). 0 swaps. **D gone**: (-154.6,-277.8), (-162.3,-253.6), (-175,-250.5), (-187.7,-253.6), (-194.5,-264.7), exactly the 5 listed; 0 added/swapped. Every kept row is byte-identical, asset key included. Kept boulders: C lintel (-139.8,-224.1 s1.6 y7) + mouth (-133.0,-215.0 s1.4); D -163.1 s1.6, -155.5 s1.8, -195.4 s2.3, -186.9 s2.4. 8 bramble, 1 gate leaf. Non-prop blocks of C/D equal. assets.js byte-identical to eae8cbe; bootCritical equal. Comments: L998 (outcrop), L1105 / L1119 (den) |

## Testerbot deviations (my own)
- T1-T4 are as in f34e430: wall-collider x-extent from the GLB accessor, the h ledger is a header upper bound, d uses a
  vm logic simulation, and f checks the den roster as session state.
- T5: This run validates an uncommitted working tree again. The checker gains a `WT2` mode: outcrop 20, 4 den
  boulders, bundle 3,251,156 B, h gated on the probe < 2M, and row T2 replaces T. The `WT` (trim-1) expectations stay in
  the script so 7ea710d still reproduces against its own tree.
- T6: b's "9 boulders" (sec 8b / sec 3) is graded at **4** because IO's trim-2 brief ordered the cut. That is a spec
  change from the brief, not a builder deviation, and Nicko should know about it (watch-item 11).
- T7: I'm committing scratch/cc_c8_ledger_probe.js again. Its only change is the builder dropping the dead
  `"mossBoulderSmall": 8109` entry, which has no effect on the result.

## Builder deviations (trim 2; non-blocking)
- DT3: The probe comes in about 48k under the brief's 1,962,768. The brief's ledger counted 8 brambles + 4 sacs + walls
  + 1 gate + 2 boulders as 107,859, and the checker's GLB scan gives 111,191 for the same 20 rows. The difference is in
  the brief's arithmetic for the rest of the circle, not in the rows. The probe line is the gate either way.
- DT1, DT2 (the den's 2.30 row choice; rotY on the two new brambles) and D1-D7 from f34e430 still stand.

## Watch-items (i, runtime only, not verified)
1. Fade timings: 0.3 s to black, the cross, 0.5 s up. Walk-out starts black and lifts over 0.8 s. A death mid-dip
   cancels the dip. Check that the camera carry-over hides the ~60 m jump.
2. Doorway sightline: check that the 4.6 x 9 m void card reads as depth. With one gate leaf, the east jamb is bramble
   only.
3. Torch radius 10.5 m vs the 24 m cavern under a 14.4 m fog d95. The nest light at 1.6 is the only landmark. With 4
   shoulders left, the whole north half of the wall foot is bare: there are no rocks on the arc from the east shoulder
   (-155.5,-264.7) round through north to the west one (-195.4,-277.8). Check the walls don't read as a flat cylinder in
   torchlight.
4. Her 4.2 m body vs the ~9 m walls, and the 6 m minion ring vs the egg-sac ring at r 7.5.
5. Wolves and bandits outside: outcrop colliders and keepOut near the patrol line. With 6 horseshoe boulders gone, the
   outcrop's collision mass is the 5 vinestone wall cores + 1 gate leaf. Check that nothing paths behind or through the
   outcrop sides that the horseshoe used to plug. The plane-hold skip is at region-manager L253ff.
6. Camps can be pitched inside the den, and a quit-save in the den makes CONTINUE build regionD at boot.
7. forceCross keeps C resident while D is active.
8. Outcrop cullM 120 pop-in. C is at 95.7% of the ledger, so ~86k of headroom remains in that circle.
9. **Sec 7's <= 40k raw new-tris target is replaced by the trim briefs' < 2M probe gate.** 321k raw new tris ship
   (the den's 208k never draws with C). Nicko should confirm the gate change explicitly.
10. **Outcrop silhouette (sec 1, "boulder outcrop").** Only 2 m9 boulders remain: the 7 m lintel and the s1.4 mouth
   rock. The mass is now mostly the vinestone wall cores. A render or playtest should confirm it still reads as a
   moss-boulder outcrop and not a wall stub.
11. Sec 3 / 8b specified 9 den shoulders; 4 ship (trim 2). Needs Nicko's sign-off along with item 9.
12. `art-direction/3d/assets/biome_library/m8-boulder-small.glb` (IO's decimated m9, rejected on visuals) is untracked
   and unreferenced. Delete it or keep it out of the trim commit.
