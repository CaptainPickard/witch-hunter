# CC-C8 validation verdict (Testerbot) - the Rot Mother's den instance

**VERDICT: FAIL** (h only: the tri budget. The change order targets <= 40k new tris and the build adds ~574k.
In region C that pushes the worst 170 m circle to ~2.06M, over the 2M ledger. Every other blocking check
(a-g) passes, and so do the node --check and bundle parts of h.)

- Builder commit: `eae8cbe` feat(cc-c8), author CaptainPickard, parent `a631fa6` (the change-order commit).
- Spec: scratch/cc_c8_valspec.md (from io/missions/2026-10-12-cc-c8-rotmother-den.md sec 8, Nicko rulings sec 0).
- Method: HEADLESS. `node scratch/cc_c8_check.js` (node v22.23.3) runs a vm eval of CONFIG.js, region-defs.js
  and region-manager.js with a `window` stub, scans GLB headers for tris and x-extent, line-greps the sources,
  runs `node --check` and audits the diff. `node scratch/cc_c8_ledger_probe.js . -136 -219 170` is an offline
  region-C tri upper bound (the CC-C7 probe re-pointed). No harness, browser, game run or network.
- The checker exits 1 (h). Line numbers are @ eae8cbe.

| id | check | result | evidence (line numbers @ eae8cbe) |
|----|-------|--------|-----------------------------------|
| a | regionD + C<->D door + C row gone + rotLair reshaped | PASS | CONFIG.js regionD L1052: id rot_den L1053, groundRadius 34 L1056, fogColor 0x05070a / fogDensity 0.12 L1067-1068, ambientLightLevel 0.06 L1069. region-defs.js registers it at L46; the door connection is pushed at L93 (axis z, planeZ -295.6, `door` object), sides C -1 / D +1 at L111-112. vm finds exactly 1 C<->D connection. regionC.enemies 23 -> 22, rotmother rows 1 -> 0 (removal note L602). C rotLair L1027 now has stains L1028 (mouth r 5 + trail 1.8/1.4/1.0) + void card L1036, and no light, fog or pool.radius (vm). 25 outcrop rows (cullM 120). keepOut (-136,-219) rx 22 rz 18 at L501 |
| b | den build rows | PASS | regionD.props from L1111. 10 whWall ring segments at r 24.0 (wall 8 colliders each). 9 mossBoulder. 4 stoneSteps, 2 skullPile, 6 blightcap, 8 graveMound (5 = nest ring r 7.5 + 3 brood). rotLair pool r 10 L1161, light 1.6 / h 1.2 / 0x7fbf4f L1163. Exit gap centred (-175.00,-295.57) = den-local z -24.57. Widest other ring hole is 1.01 m, under the 1.4 m player body, so the den is closed. Seat: region-manager L1833 `whGroundFeed(...) + (p.y\|\|0)` on every row; flat disc (no terrain row, groundY 0). The gap width is a deviation, see D1 |
| c | lair re-home + params byte-equal C7 | PASS | rotmother.lair `{x 0, y 6, region 'D', flag 'C'}` L1751 -> rot_den, world (-175,-265). regionD.lairs row L1101. vm deep-equal against bef33f1: `enemy.rotmother` minus `lair` = true (minions 7 s / 6 m / cap 3 / dieOnMasterDeath, rearm 3 d / proximity / 14 m, loot, poison, slam), `enemy.rotspawn` = true. Lair rows are instanced after the enemy rows at region-manager L1909 |
| d | E-to-enter 3.5 m + 0.8 s fade + walk-back exit, no pause/menu | PASS | door L1078: interactM 3.5 L1084, fadeIn 0.3 + fadeOut 0.5 = 0.8 s, exitFadeOut 0.8 L1092, prompt 'E - Enter the den' L1093. game.js: interact chain L1863, tryDenDoor L1876 (forceCross at the dip peak L1882), prompt L2172, dip on #wh-death-overlay startDenFade L1891 / denFadeTick L1916, tick L2953, walk-out dip L2960. region-manager: portalNear L128, logic forceCross L144, live forceCross L2047, planeIn filter L49. No pause/menu token in the block. **vm sim of RegionManagerLogic, all true:** no crossing on the C side of the line; portal at 3.4 m yes / 3.6 m no; forceCross -> rot_den at land (-175,-292.6); no portal while in D; no crossing inside the mouth; walk-out at z -296 -> C at land (-142.6,-227.8); no bounce-back; no crossing outside the window (x -180); C's pre-warm survives anywhere inside the ring (47.4 m < 30 + 20) |
| e | always-dark phase + light rules | PASS | dayNight.constantPhases.rot_den L2849: lightIntensity 0 (moon 0), exposureMult 0.75 L2852, stars 0.15, discOpacity 0.2 L2856, fog rot_den 0x05070a / 0.12. Hemi = hemiBaseIntensity x 0.06 (game.js L1358) x hemiFillMult 1.0. daynight.js: constantRow L225, setArea skip L391, SkyPool.tick underlay-only L444, DayNight.tick copyRow L500 after an untouched coreTick L494 (no clock math). No region light targets her or the spawns: the only den light is the nest socket. Nest light: lairSockets skips while cleared (L1568) and computeSockets polls it every frame (game.js L2720 -> L2769). Death sets the flag (L1163), re-arm clears it (L1132), and the fog cards follow (L1418) |
| f | save round-trip + pre-C8 compat | PASS | The flag letter stays 'C' (lairNest L1106), so the key `rotmother_cleared_C` is byte-equal to C7. captureLairs L1538 / restoreLairs L1546; a missing block means all armed (L1548). game.js WH_SAVE wrap: capture L2567, restore L2581. Den roster: enemies [] + lairs[0], so she is index 0; the spawn-prune boundary counts lair rows (enemy.js L1278). Per-index dead state is session-only as in C7 (save.js L8). save.js validRegion accepts rot_den (L40). save.js diff: none |
| g | scope audit a631fa6..eae8cbe | PASS (1 flag) | 10 files: v8-playable.html, CONFIG.js, assets.js, **daynight.js (flagged)**, enemy.js, game.js, region-defs.js, region-manager.js, scratch/cc-c8/gen_den.py, scratch/cc-c8/glb_tris.py. FORBIDDEN touched: none |
| h | node --check + bundle + tris ledger | **FAIL** (tris) | node --check OK on all 7 edited js. Bundle v8-playable.html is 3,251,738 B (matches the commit) and inlines every edited js verbatim. Tri delta was reported by the builder (log + commit). **Measured new tris = 574,430 against the <= 40,000 target.** Outcrop 25 rows = 256,794 (8 mossBoulder x 21,599 + 2 gates x 20,585 + walls/bramble/sacs), den 39 rows = 316,410, pools/stains ~1.2k. Region C net = +192k (+168k with her and the spawn bodies moved out). **C ledger probe: the worst 170 m circle around the outcrop is 2,059,871 (103.0% of 2M) at (-84,-309), 1,802,291 without the outcrop.** The den (~340k with bodies) never draws with C |

## Why h fails (root cause = the change order's ledger)
Sec 7 priced a mossBoulder at ~1k tris and the gate pair at ~4k. The shipped GLBs are 21,599 and 20,585 tris
each (header scan; the CC-C7 probe table agrees). The kit counts sec 1/3 mandate (8 + 9 boulders, 2 gates)
can't fit 40k on their own, so the builder built to spec and reported the overrun honestly. The cullM 120
band limits it but doesn't fix it: C's worst circle goes over 2M. **A Nicko ruling is needed:** (1) accept the
budget, or (2) trim or swap the kit, e.g. fewer or lower-poly outcrop boulders and gates (the outcrop's 8
boulders + 2 gates = 214k of the 257k), and/or a tighter outcrop cullM. Then re-run h.

## Scope flag (g) ruling
`prototype/js/daynight.js` (+30 / -0) isn't on sec 8g's allowed list, and it isn't on the forbidden list
either. Sec 6 sanctions it in so many words ("daynight gains ONE always-dark branch read, no clock changes"),
as does sec 9. The builder used one helper and three read sites (SkyPool.setArea, SkyPool.tick, a
DayNight.tick post-step) instead of literally one. No clock code changed: coreTick runs untouched first and
no lines were removed. **Non-blocking**; Nicko can overrule.

## Testerbot deviations (my own)
- T1: In the checker, ring collider circles use the GLB accessor x-extent (1.899, no node transforms) as the
  runtime `meta.width`. That is the same value the CC-C7 probe table uses for mossBoulder.
- T2: The h ledger is a GLB-header upper bound (prop counts x tris, no frustum culling), the same method as CC-C7.
- T3: d goes one step past grep: a vm simulation of the THREE-free RegionManagerLogic. This is pure logic,
  not a game run.
- T4: f's "per-index den roster round-trip" is checked as session state (stateFor) plus the persistent flag.
  save.js never persisted per-index enemy state (L8), in C7 or now.

## Builder deviations noted (non-blocking unless Nicko rules otherwise)
- D1: **The mouth is wider than the brief's 4.6 m.** The visual mesh gap is ~6.2 m and the collider gap
  7.0 m edge-to-edge. The player-centre lane is +-2.81 m, inside the door window of +-3.0, so every walk-out
  crosses. The builder's log quotes +-2.65.
- D2: Hemi fill mult is 1.0, not 0.06. Applying 0.06 twice would be pitch black. Effective fill = base x 0.06.
- D3: Wall rows are per-axis scaled (sy / sz) instead of "3 stacked rows at scale 2": den segments are 15 m x
  ~9 m, outcrop walls 13-15 m. Colliders: 6 per outcrop facade (3 recess sides, 4 back) and 8 per den segment.
- D4: Manifest gets 3 rows (blightcap + stoneSteps + skullPile), not 1. All three join bootCritical and
  b6Bones leaves it.
- D5: The door gained `walkFrom` / `interact` / `land` and a new `planeIn` helper. In C the line isn't a
  plane at all, and x is not preserved across the door (land rows).
- D6: enemy.js goes past "homeRegionId + coords": a rotPoolMesh refactor (shared with the stains), light + fog
  gating on cleared (required by sec 4 / e), and the prune row count includes lair rows. No combat logic changed.
- D7: fogDensity 0.12 (FogExp2) gives d95 = 14.4 m, not the brief's "~24 m". The values match the spec;
  the brief's arithmetic was off.

## Watch-items (i, runtime only, not verified)
1. Fade timings: E gives 0.3 s to black, the cross, then 0.5 s up. Walk-out starts black and lifts over 0.8 s.
   A death mid-dip cancels the dip. Check that the camera carry-over hides the ~60 m jump.
2. Doorway sightline: C shows a black void card (4.6 x 9 m) in the recess, not the den, so check that it reads
   as depth. The wall mesh ends poke ~0.35 m past the mouth plane.
3. Torch light radius 10.5 m vs a 24 m cavern under a 14.4 m fog d95: the far wall should be invisible, and the
   nest light at 1.6 is the only landmark.
4. Her 4.2 m body vs the ~9 m walls, and the 6 m minion ring vs the egg-sac ring at r 7.5.
5. Wolves and bandits outside: outcrop colliders and keepOut near the patrol line. region-manager skips the
   enemy plane-hold for a plane that doesn't exist in the home region (L253ff).
6. Builder-flagged: camps can be pitched inside the den, and a quit-save inside the den makes CONTINUE build
   regionD at boot (spawn (-175,-291)).
7. forceCross keeps C hidden but resident while D is active, so both groups sit in memory.
8. Perf: once the h ruling lands, re-check C's worst circle (scratch/cc_c8_ledger_probe.js) and the outcrop's
   cullM 120 pop-in.
