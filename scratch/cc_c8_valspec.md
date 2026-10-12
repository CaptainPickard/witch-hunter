# CC-C8 validation spec (Testerbot) - the Rot Mother's den instance

Source: io/missions/2026-10-12-cc-c8-rotmother-den.md sec 8 (+ the sec 0-7 numbers it validates; Nicko rulings in sec 0).
Target: builder commit eae8cbe `feat(cc-c8)` (CaptainPickard), parent a631fa6 (the change-order commit).
Mode: HEADLESS only. Node `vm` eval of CONFIG.js + region-defs.js + region-manager.js (the THREE-free
RegionManagerLogic half) with a `window` stub, GLB-header tri/extent scan, regex/line grep of
enemy.js / game.js / daynight.js / assets.js / save.js, and `node --check`. No harness, no browser, no game run, no network.
Checker: scratch/cc_c8_check.js. Region-C ledger probe: scratch/cc_c8_ledger_probe.js (supports h).

| id | check | method | blocking |
|----|-------|--------|----------|
| a | `CONFIG.regionD` exists (id rot_den, groundRadius 34, ambient 0.06, fog 0x05070a / 0.12); the C<->D connection is registered door-type; the regionC rotmother row is GONE; regionC.rotLair gains outcrop/doorway/trail and LOSES pool radius/light/fog; outcrop keepOut row | vm-eval CONFIG + region-defs; diff vs a631fa6 enemy list | YES |
| b | den build: 10 ring segments (r ~24) + 9 mossBoulder + furniture (4 stoneSteps, 2 skullPile, 3+5 egg sacs, 6 blightcap) + nest pool r 10 + light 1.6 + an exit gap in the ring at den-local (0,-24); every row seated by the standard seat; ring closed elsewhere | vm-eval; ring collider circles rebuilt from the GLB x-extent (region-manager wall tech) to measure the gap + the widest other hole vs the 1.4 m player body | YES |
| c | lair: home region rot_den; nest den-local (0,+6) = world (-175,-265); spawner / re-arm / flag / loot params byte-equal to C7 (bef33f1) | vm deep-equal of `enemy.rotmother` minus `lair` + `enemy.rotspawn` against bef33f1 | YES |
| d | E-to-enter: prompt within 3.5 m of the doorway; E triggers the cross + a 0.8 s fade; a walk-back exit crossing exists; no pause/menu | grep game.js / region-manager.js; vm simulation of RegionManagerLogic (portalNear radius, forceCross land row, no plane in C, walk-out cross inside the window only, no bounce-back, hysteresis inside the ring) | YES |
| e | always-dark phase (moon 0, hemi 0.06, exposure 0.75), stars 0.15 underlay; no region light on her/spawns; nest light dies on death and relights on re-arm | vm CONFIG.dayNight.constantPhases; grep daynight.js / enemy.js / game.js socket path | YES |
| f | save: rotmother_cleared flag + per-index den roster round-trip; a pre-C8 profile loads armed (default) or cleared (flag honored) | grep enemy.js capture/restore + flag letter; game.js WH_SAVE wrap; save.js untouched | YES |
| g | scope: only CONFIG.js, region-defs.js, region-manager.js, assets.js, enemy.js, game.js, the bundle, io/missions, scratch. FORBIDDEN: save.js, player.js, camp.js, cooking.js, style.css, index.html, docs/planning | `git diff --name-only a631fa6 eae8cbe` | YES |
| h | node --check on every edited js; bundle rebuilt; tris ledger delta reported, target <= 40k new tris | node --check; edited sources inlined verbatim in v8-playable.html; GLB-header tris x rows; region-C 2M worst-circle probe | YES |
| i | runtime watch-items: fade timings, doorway sightline, torch radius vs the 24 m cavern, her 4.2 m body vs the cavern, wolf/bandit approaches outside | listed only (no runtime) | no |
