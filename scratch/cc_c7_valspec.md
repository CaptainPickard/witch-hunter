# CC-C7 validation spec (Testerbot) - rot mother + rot spawn wiring

Source: io/missions/2026-10-12-cc-c7-rotmother-behavior.md sec 7 (+ the sec 2-6 numbers it validates).
Target: builder commit bef33f1 `feat(cc-c7)` (CaptainPickard), parent a948290.
Mode: HEADLESS only - node `vm` eval of CONFIG.js with a `window` stub + regex/line grep of the JS
sources. No harness, no browser, no network. Checker: scratch/cc_c7_check.js.

Note on file names: the brief says `data.js`; this repo's data file is `prototype/js/CONFIG.js`
(no data.js exists). The "clip wiring file" = `prototype/js/anim.js` (RIGID_CLIPS).

| id | check | method | blocking |
|----|-------|--------|----------|
| a | `CONFIG.enemy.rotmother`: hp 460, speed 1.6, lair {x -175, y 95, region C}, slamCooldown 3.4, slamWindup 1.15, poison {dps 3.5, duration 4.0, slow 0.45}, rearm {days 3, radius 14}, loot rot-silk [2,4] + rot-gland [1,2], minions {cap 3, interval 7.0, dieOnMasterDeath true}. `rotspawn`: hp 26, dmg 5, speed 2.4, aggro 14, scale 0.8. | vm-eval CONFIG.js, deep-compare values; grep line numbers | YES |
| b | slam AoE = front arc 180 deg / radius 3.2 in enemy.js (grep-able), knockback + poison apply on a landed slam; poison = damage + slow only, refresh-not-stack | grep enemy.js (deriveCfg mapping, active-entry arc test, slamImpact) + game.js applyPlayerPoison | YES |
| c | minion spawner: interval 7 s, spawn at range 6 m around her, cap 3 alive, all die on mother death | grep enemy.js lairTick / spawnMinion / lairOnDeath + its takeDamage call site | YES |
| d | re-arm: save flag `rotmother_cleared_<region>`, +3 day counter, 14 m proximity trigger, persisted via save block | grep enemy.js lairFlag / lairTick / captureLairs / restoreLairs + game.js WH_SAVE wrap | YES |
| e | rot-silk + rot-gland registered in the item/mat registry + drop-log descriptors (and the drop-log consumer) | vm-eval CONFIG.items + grep game.js dropLog | no (notes) |
| f | placeholder clips: mother = bandit 6-clip pattern (idle/walk/attack/hit/death/spare), spawn = idle/walk/attack/death (+spare ok), clipScale 1.0 / 1.3 | grep anim.js RIGID_CLIPS | no (notes) |
| g | SCOPE AUDIT `git diff --stat a948290..bef33f1`: only data(CONFIG).js, enemy.js, game.js, clip wiring (anim.js), lair scatter JSON, prototype bundle html, io/missions docs. FORBIDDEN: docs/planning, art-direction, style.css, index.html, save.js, daynight.js, camp.js, player.js, cooking.js. Any other file = flagged. | git diff --name-only | YES (forbidden touch) |
| h | `node --check` on every edited .js | playwright-driver node | YES |

Out of headless reach (sec 7 runtime items, carried as watch-items, not judged): save/load round-trip,
in-game arc hit test, poison expiry timing, cap never > 3 under play, exactly-once re-arm in play,
loot re-roll, perf (no dropped frames).
