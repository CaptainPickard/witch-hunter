# CC-H5 THE TITHE VAULTS — Devbot build note (2026-11-07 wake)

Round: delve strata V4 off the Spire Approach, per
`io/specs/cc-h5-tithe-vaults-spec.md` + its valspec. Two-file law held:
`prototype/js/CONFIG.js` + `prototype/js/region-defs.js` ONLY. No engine
files, no assets, no css/html touched. NO commit, NO push (build law sec 8).
Probe: `scratch/cc-h5/solve_geometry.py` (node-evals the live CONFIG +
region-defs; run from worktree root).

## Markers landed

- CONFIG.js: `regionK: {` (tithe_vaults) — the J-mirror pocket (center
  (0,-880), radius 34, seed 448271909, plane-0 one-sided door, 5 enemies,
  1 lair, rotLair, 25 props incl. the closed 10-row r34 vault ring).
- CONFIG.js: `CONFIG.enemy.zealot` (bandit chassis, verbatim bandit
  attackPhase + ai1, no pattern key) and `CONFIG.enemy.tithecaptain`
  (boss-slam, soldier-disciplined slam, lair K / flagPrefix tithecaptain,
  stolenCoin loot, zealot minions, ai1 guardArcDeg 45).
- CONFIG.js: bodyByType + animVariantByType gains zealot AND tithecaptain
  (banditBody / 'bandit' — the spec 2.3 symmetry law).
- region-defs.js: `makeRegion(CFG.regionK, -1)` registration + conn[9]
  (J->K, AMENDMENT A door row re-pointed from conn[8]'s shape; sides
  J=+1 / K=-1 per sideOfPlane geometry). conn count 9 -> 10.

## Probe totals (final run, exit 0)

**161 checks, 0 failures** (deterministic: consecutive fresh runs byte-identical).
LABEL: PASS/FAIL per line, V-0..V-12 mapped;
disclosure lines carry the footprint map and the K-vs-J seat minima:
nearest K enemy to any J seat 123.91 m (V-12 tol trivially clean);
footprint map: blightcap 1.6921 / lanternPost 0.5854 / mossBoulder 1.8974 /
mourningStatue 1.8620 / okRuinColumn 0.9571 / skullPile 2.0000 /
stoneSteps 1.9483 / whWallA|B 1.8990 (collider radii = width*scale/2 via
the region-manager law; walls r 0.45 x 100 circles).

Key live-derived numbers: ring rho == 34.0 +- tol on all 10 rows (2dp
circle re-derivation), lane edge clearance 1.5483 >= 1.0, fog d95 10.8176
(== 10.82 ± 0.05), ambient 0.045 < J 0.05, nest-vs-spawn 16.0 == the N-4
figure, hook nearest J prop 9.6047 >= 4.5, landJ out of both J lane windows
and |dz| == 20.0 south of J's -662 plane, K north rim -846 vs J south point
-740 = the 106 m tol gap. Boss-seat clear circle computed at the nest seat
(0,-872) under BOTH footprint maps (both >= the 6.0 AMEND-1 floor):
fixed-map (valspec radii) 6.8500 m, binding okRuinColumn (-8,-872); the
h3-lineage per-row map (width*scale/2) 6.8515 m, binding okRuinColumn
(0,-880) [the relocated root's own 1.15 map radius]. The spec's quoted
7.0 m zealot reading was the no-footprint map's number.

## SPEC-FIG FIXES (seats that violated stated engine/valspec laws — all
## re-seated, all disclosed here per the mandate)

1. **Walk-out plane -844 -> -848 (sec 3/5; engine law)**. -844 sits 2 m
   OUTSIDE K's north rim (-846): under the CC-C2 rim clamp door
   connections carry no plane clamp and suspendDepthM 0 gives no door-band
   extension, so a plane beyond the rim is unreachable from inside K.
   Every landed plane sits INSIDE its disc (J: -662 vs rim -660; J conn[8]:
   -738 vs rim -740). -848 = the J-mirror pair (2 m inside the rim) and
   restores the lane bookkeeping: north-point row (0,-846) colliders clear
   the |x| <= 2.2 lane by 2.00 - 0.45 = 1.55 m edge distance (the J/I
   landed figure; probe re-derives 1.5483 >= 1.0).
2. **N-5 enemy-seat rescue (sec 3 enemies; valspec V-3/N-5 law)**. The
   sec-3 flank zealot seats (+-9,-876) sat 4.12 m from the dais colonnade
   (+-8,-872) — below the >= 5.0 enemy-vs-prop floor. Moved to the
   north-wall pack line (-15,-863) / (+15,-863): props >= 5.39, mutuals
   >= 15.13, spawn 16.55, ring clear 11.33. North center zealot stays
   (0,-865) = the ADJ-E 9.0 m landing-row read.
3. **Colossus (0,-876) -> (0,-880) (sec 3/5; AMEND-1 law)**. At (0,-876)
   it sat 4 m from the boss seat: clear circle 2.85 m < the 6.0 AMEND-1
   floor (and N-4's own 16.0 nest-arithmetic would fail: 856-876 = 20). At
   (0,-880): clear circle 6.85 >= 6.0 (binding obstacle okRuinColumn,
   footprint 0.9571*2.40/2), nest-vs-spawn 16.0 exactly, and N-5's quoted
   binding "zealot (0,-865) at 7.0 m" still true.
4. **Ring rows re-derived to the strict 2dp circle (sec 3; N-2 law)**. The
   sec-3 z-literals carried up to 2.01 m drift (row 2 -867.48 vs true
   34*sin/cos re-derivation -869.49, rho 34.68) — the valspec's own N-2
   law is rho == 34.0 ± 0.05 on LANDED rows + chord uniformity within
   0.02 (literals = context, not law). All 10 rows now on the r34 circle
   (2dp: 0.00/-846.00, 19.98/-852.49, 32.34/-869.49, 32.34/-890.51,
   19.98/-907.51, 0.00/-914.00, mirror x<0), rotY = 3.14 + k*0.6283 kept.
   One skullPile nudged (6,-908) -> (8,-908) to hold the universal 4.0 m
   prop-mutual floor against the moved ring rows (now 8.51).
5. **spawn/ping-pong note (sec 3; crossing law)**. Sec 3's spawn (-856) on
   the -844 plane was ON the walk-back plane's line; the crossing cannot
   land the player on the plane. Spawn kept (0,-856), 8 m south of the
   -848 plane: walk-EXIT faces south into the vault, no re-trigger
   (ADJ-E's 12 m shortened to 8 m by fix 1 — the zealot (0,-865) still
   sits exactly 9.0 m from the landing row = ADJ-E's defended floor).

## Disclosures

- **ADJ-D ai1-vs-boss-slam check**: ai1 rides ALIVE under boss-slam —
  enemy.js `ai1For` (line 51) reads `cfg.ai1` with NO pattern branch, and
  the call at line 358 sits inside `Enemy.prototype.update` (line 250)
  before any slam/pattern-specific flow; the guard takeDamage hook (line
  948-951) keys on `this.cfg.ai1` similarly. No branch skips ai1For for
  slam patterns, so the captain's parry-capable soldier read (guardArcDeg
  45 alongside the boss-slam chassis) is wired as designed. No IO
  escalation needed; the ADJ-D dead-ai1 contingency did not fire.
- **Footprint/collider law**: prop collider radii = measured width*scale/2
  (region-manager whPropColliders); NO trunk-ratio asset appears in K, so
  every prop keeps its full footprint — disclosed numbers above; probe
  prints the map it used.
- **Stale valspec inventory**: the valspec's head-time seed list calls
  J's rotLair pool textureSeed "448271910"; the live landed value is
  20261107 (node-eval verified: 22 seeds total, K's groundSeed 448271909
  unique among ALL of them, K pool 448271910 = groundSeed + 1, distinct
  from every other seed). No effect on V-5 (the law binds only the
  groundSeed).
- **deriveCfg spot-check**: zealot carries NO pattern key (cfgFor returns
  the row as-is); captain's pattern 'boss-slam' derives attackRange/
  attackPhase from the slam keys, and cfg.ai1 survives the copy per
  enemy.js deriveCfg loop. Probe V-9 line asserts this from live rows.
- **V-5/V-8 hygiene**: node --check PASS on both files; connections
  length 10; conn[9] shape/values byte-checked against the valspec's
  asserted fields (walkFrom K, interact J (7.5,-678) r 3.5, land rows,
  fades 0.3/0.5/0.8, prompt verbatim 'E - Descend into the tithe vaults',
  distinct from conn[8]'s). J blocks regionJ/regionI + conn[7]/[8]
  byte-identical to HEAD@1f7f904 (cmp clean; the only two deleted lines
  in CONFIG.js are the two body-map rows this round extends).

## Left for Testerbot

Independent re-run of `scratch/cc-h5/solve_geometry.py` (expect 161/0,
twice for determinism),
its own valspec walk, verdict report to
`io/reports/2026-11-07-cc-h5-tithe-vaults-validation.md`.
