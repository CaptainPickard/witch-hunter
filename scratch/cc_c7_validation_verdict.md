# CC-C7 validation verdict (Testerbot) - rot mother + rot spawn wiring

**VERDICT: PASS** (all blocking checks a/b/c/d/g/h pass; one scope flag on g, non-forbidden, ruled below)

- Builder commit: `bef33f1` feat(cc-c7), author CaptainPickard, parent `a948290` (the brief commit).
- Spec: scratch/cc_c7_valspec.md (from io/missions/2026-10-12-cc-c7-rotmother-behavior.md sec 7).
- Method: HEADLESS. `node scratch/cc_c7_check.js` (playwright-driver node): vm-eval of CONFIG.js / anim.js
  with a `window` stub + line grep of enemy.js / game.js / CONFIG.js. No harness, browser or network.
- File-name mapping: the brief's `data.js` = `prototype/js/CONFIG.js` (no data.js in the repo);
  the clip wiring file = `prototype/js/anim.js`.

| id | check | result | evidence (line numbers @ bef33f1) |
|----|-------|--------|-----------------------------------|
| a | CONFIG.enemy.rotmother + rotspawn exact fields | PASS | CONFIG.js rotmother L1579, rotspawn L1606; every value vm-evaluated equal (hp 460, speed 1.6, lair -175/95/C, slamCooldown 3.4, slamWindup 1.15, poison 3.5/4.0/0.45, rearm 3d/proximity/14, loot rot-silk [2,4] + rot-gland [1,2], minions cap 3 / 7.0 / range 6.0 / dieOnMasterDeath; spawn 26/5/2.4/14/0.8). regionC row L605 at world (-175,-271) = center + lair |
| b | slam AoE 180 deg / 3.2 + knockback + poison | PASS | CONFIG slamRadius 3.2 L1595, slamArcDeg 180 L1596; enemy.js deriveCfg attackRange=slamRadius L35, hitArcDeg=slamArcDeg/2 (half-angle 90) L37; arc test L411-412; slamImpact call L418, def L1486 (only on a LANDED hit: L1490), poison L1491, knockback L1493; game.js applyPlayerPoison L2753 (refresh-not-stack L2756), slow L2771, knockbackPlayer L2760, DOT tick L2785 |
| c | minion spawner 7 s / 6 m / cap 3 / die on mother death | PASS | enemy.js alive count L1144, gate (alive + player within lairRadius 14) L1145, interval + cap L1147, 6 m ring L1231, wither loop L1163-1172 called from death L831; CONFIG lairRadius 14 L1593 |
| d | re-arm flag / +3 days / 14 m proximity / persisted | PASS | enemy.js lairFlag `rotmother_cleared_<letter>` L1092, death day stamp L1160, +3-day test L1123, 14 m proximity (or first entry) L1124, clear-once L1129; captureLairs L1520, restoreLairs L1528; game.js additive WH_SAVE wrap L2478 / L2486 / L2492 (save.js untouched) |
| e | rot-silk + rot-gland registry + drop-log | PASS | CONFIG.js items L2352 / L2356 (flavor + dropLog L2355 / L2359); game.js drop-log consumer L2007, typed loot roll L1968 / L1980 |
| f | placeholder clip set + clip scale | PASS | anim.js RIGID_CLIPS L667; mother idle/walk/attack/hit/death/spare L670, clipScale 1.0 L669; spawn idle/walk/attack/death (+spare, hit null) L682, clipScale 1.3 L681; CONFIG rigidAnimByType L1628 |
| g | scope audit a948290..bef33f1 | PASS (1 flag) | 6 files: v8-playable.html, CONFIG.js, anim.js, enemy.js, game.js, **assets.js (flagged)**. FORBIDDEN touched: none |
| h | node --check on every edited .js | PASS | CONFIG.js, anim.js, assets.js, enemy.js, game.js all OK |

## Scope flag (g) ruling
`prototype/js/assets.js` (+9 lines) isn't on the allowed list, and it isn't on the forbidden list either. The
change only adds asset-manifest rows: `b6Bones` (an existing biome-library GLB), `rotmotherBody`, and `rotspawnBody`
(the shipped `-pixelated` bakes the brief requires, not the raw twins). The GLBs can't load without these rows.
The brief allows "game.js registration", and these rows are the same kind of registration. I rule it
**non-blocking**. Nicko can overrule if the scope rule is meant literally.

Other scope notes: no separate lair scatter JSON was committed. The 6 bone rows are inlined in CONFIG.js
(regionC.props), and the generator output lives in untracked scratch/cc-c7/lair.json. No io/missions doc
is in the diff. The bundle `prototype/builds/v8-playable.html` was rebuilt and contains the new code: 24 hits for
RIGID_CLIPS / rotmother_cleared_ / slamArcDeg.

## Watch-items (runtime, outside headless reach; not judged)
1. Save/load round-trip of the `lairs` block. game.js does a second localStorage write after `baseSave` (L2486). Check that this
   doesn't race save.js's quit-persist path, and that a pre-CC-C7 profile loads with the nest armed.
2. Poison-lite includes a DOT (dps 3.5 x 4 ticks), not only a slow. That matches the CONFIG row (`dps`), and a
   re-apply refreshes rather than stacks. Confirm that "damage + slow ONLY" in brief sec 3 means this.
3. Poison and knockback apply only on a landed slam (hp dropped, no block: enemy.js L1490). A blocked slam does no
   poison and no shove. Confirm this is the intended design.
4. Minions spawn exactly at 6.0 m (a ring, not a disc) and can spawn even if the player is closer. Check in play
   that a spawn never lands inside a prop or on a slope.
5. Re-arm "exactly once per cycle", loot re-roll, cap never > 3 under play, arc edge cases at ±90 deg, and perf
   (17.5k + 3x2k tris, ledger ≤ 1,889k): all need a harness run.
6. Withered spawn give no loot and no XP (by design). `kill_rotmother` 240 XP pays again on every re-arm, which makes
   the boss farmable. That needs an economy check.
7. `rotspawnBody` is deferred (not boot-critical). The first spawn late-swaps the mesh. Look for a visible pop.
