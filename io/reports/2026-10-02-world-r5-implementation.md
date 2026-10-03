# World R5 — implementation report (DRAFT, Devbot gate step 3)

Round: world-r5 — collision + world bounds (P0-5 + P1-4 camera half).
Spec: io/specs/devbot-spec-wh-world-r5.md. Valspec of record:
io/specs/testerbot-spec-wh-world-r5.md (AC-R5-1..5 + PRES, C1-C13).
Base: 818d8bc (R4 marker). Tree at implementation: 923a659.
Carrier-req: Testerbot revalidates harness on lane recovery.

STATUS: code + harness parts written. **NOT smoke-run.** The Devbot session
was sandboxed: `python3`, `git diff -U0 <rev>`, `git hash-object` and shell
output redirection were all denied. No harness assembly, no py_compile, no
browser run, no verdict JSON from this session. IO runs build + smoke +
verdict outside it (see "IO next steps").

## Files

| File | Change |
|------|--------|
| prototype/js/CONFIG.js | world{}: `playerMargin 1.5`, `visualGroundFogMult 1.1`, `fogOpaqueFrac 0.95`, `colliderCorridorHalfDepth 6`; regionA ghoul z -30 -> -23.5; player{}: `camGroundClearance 0.4`, `camPitchDistShrink 0.35` |
| prototype/js/region-manager.js | clampPlayer split (plane body renamed `clampPlayerPlane`, byte-identical; new `clampPlayer` = plane + radial); enemy radial clamp in clampEnemyToHomeSide; adjacent THREE-free helpers (radial / visual radius / corridor / collider table / push-out); ground disc radius + repeat + mist size; live `propColliders` / `pushOutOfProps` / `validateSpawns` next to the live clampEnemyToHomeSide wrapper |
| prototype/js/game.js | clampPlayerToBounds: prop push-out + one re-clamp, BEFORE the `if (blocked) return` |
| prototype/js/player.js | updateCamera only: by-pitch distance cap + ground y floor (want.y in both branches + post-lerp) |
| tests/r5parts/part01..part10.py + build.py | harness parts (assembled artifact NOT yet built — sandbox) |
| io/reports/2026-10-02-world-r5-implementation.md | this draft |

Not touched: assets.js, enemy.js, anim.js, region-defs.js, style.css,
index.html, every GLB/PNG. `git status --short` shows only the 4 allowed
prototype files as modified. assets.js and index.html are absent from
status, so they are byte-identical to HEAD (= 818d8bc for prototype/):
assets.js blob 4d27e6f9 and index.html 9ad39b809bc4...dc32 are unchanged.
`git diff --stat`: 205 insertions, 6 deletions over the 4 files.

## Pinned numbers

### Margin
`world.playerMargin = 1.5` (inside [0.7, 3.0]; = holdAtBoundaryMargin, so
player and enemy hold lines share one number). r_play = 90 - 1.5 = **88.5**.
`world.groundRadius` stays 90 (R1/R2 anchors).

### Effective camera distance (C13 pin)
```
cap(pitch) = max(camMinDistance, camMaxDistance * (1 - camPitchDistShrink * max(0, sin(pitch))))
dEff       = max(camMinDistance, min(cap(pitch), camDist))           // camDist (wheel state) never written
want.y     = max(want.y, groundY + camGroundClearance)  (groundY = 0; both branches)
camera.y   = max(camera.y, camGroundClearance) after the lerp, before lookAt
```
camMax 14, camMin 3, k = 0.35, clearance 0.4. Predicted d at camDist 14:
pitch 0 -> 14.000; 22 -> 12.165; 45 -> 10.535; 65 -> 9.559 (ratio 0.683 <=
0.85 bar; monotone). Pitch < 0: cap = 14 and the y floor lifts the camera
(pitch -15 / dist 14: want.y -1.02 -> 0.40). Default framing (pitch 22 /
camDist 7): cap 12.165 > 7 -> dEff = 7 exactly, y = 5.222, so the default
camera is bit-identical to 818d8bc. Lock-on: framing distance bytes unchanged
(C13); only the y floor is added (C8). Shake (+-0.03) is applied after
updateCamera, so the minimum is 0.37, which clears the 0.3 bar.

### Visual ground (C4)
`R_vis = max(90, r_play + 1.1 * d95)`, `d95 = sqrt(-ln(1 - 0.95)) / fogDensity`:
- A (0.012): d95 144.24 -> R_vis **247.17**, repeat 32.96
- B (0.024): d95 72.12 -> R_vis **167.83**, repeat 22.38
- repeat = 12 * R_vis / 90 -> repeat / R_vis = 12/90 exactly (texel gate).
- Mist plane (B) is sized 2 * R_vis, so its 180-unit square edge no longer
  sits 1.5 units past the rim (it would have been a rim-seam luma step).

### Prop colliders
R_i = GROUND_META.width * scale / 2 (valspec formula, verbatim). Push-out
runs in clampPlayerToBounds after the plane + rim clamp, every frame
(including frames where the plane clamp fired; C5), then one re-clamp.
Corridor exempt = circle meets x in [chokepoint +- width/2], z in
[boundary.z +- 6] (= the valspec [-4,4] x [-31,-19]). Collider count:
106 props evaluated; circles = 106 - |E|. Predicted |E| = 1, so **105 live
colliders** (A 44, B 61). Final table = harness RECORD (colliders.radii).

Native widths I read from the GLB JSON headers (trimesh exports, single
node, no transform, so setFromObject X-extent = accessor max-min):

| asset | width | example R |
|-------|-------|-----------|
| lanternPost | 0.5897 | A1 (-2,30) s2.4 -> **0.708** |
| mossBoulder | 1.8974 | (-2.5,-6.5) s1.05 -> 0.996 |
| graveMound | 1.9345 | (-4.5,-12.5) s1.6 -> 1.548 |
| deadTree | 1.7598 | s6.5 -> 5.72; s9.85 -> 8.67 |
| livingOak | 1.8430 | s7.25 -> 6.68 |
| yewTree | 1.0109 | s10.4 -> 5.26 |
| witchwoodTree | 1.8594 | s10.43 -> 9.70 |

### A ghoul disposition
CONFIG regionA ghoul (2,-30) -> **(2,-23.5)**: the exact hold line
(boundary.z + holdAtBoundaryMargin). clampEnemyToHomeSide already snapped
it to z -23.5 on its first frame, so its runtime position is unchanged. Only
the leash/spawn anchor moves 6.5 units. No gate-guard flag used.

## PREDICTED GATE ISSUE — IO ruling needed (C6/C12)

**AC-R5-2 (iii) will fail at the B spawn under the valspec's own radius
formula.** Canopy-wide tree footprints put B spawn (0,-45) inside two
colliders:
- B#0 livingOak (6.2,-46.4) s7.25: R 6.681, d 6.356 < R+0.7 = 7.381
- B#23 witchwoodTree (-7.4,-41.5) s10.02: R 9.316, d 8.185 < 10.016

Props and spawns are byte-frozen by PRES, so no in-surface code change can
clear this. The validator honestly reports both as `kind:'spawn'`
violations. The harness classifies "mechanics PASS, only spawn-in-collider
misses" as **FAIL-RETUNE-PENDING**, the collider-radii retune C12 already
budgets, not FAIL. Gameplay effect: a B respawn lands in the overlap of
both circles. Alternating push-out converges to a circle intersection
point (no NaN, no lock), but B's canopy circles act as large invisible
walls. Suggested single retune (IO to rule; not implemented): a per-asset
trunk fraction for tree-class footprints (deadTree / livingOak / yewTree /
witchwoodTree), e.g. collider R = 0.25 * width * scale / 2. The valspec
R_i formula for R5-2 (iii) and R5-4 (b) would need the same amendment.

Second prediction (RECORD only, C6): corridor exempt set E = {B#9 deadTree
(-9.1,-35.8) s8, R 7.039}. Its distance to the corridor corner (-4,-31) is
7.003, so it touches by 0.036 and is exempt from collision. The valspec
expected []; it is RECORD, not a gate.

Other floor interactions (expected, covered):
- R2 L6 teleports onto lanternPost centres (-2,30) / (4,-2). The player is
  pushed about 1.41 units along +x. If L6 fails, that is waiver class
  R5-collider-teleport (C10), recomputed in-run from the literal targets in
  R2's ac_l6.
- R2 L1 stepped x=-2 path: mossBoulder (-2.5,-6.5) pushes the player to
  x ~ -0.8 (still inside the corridor). graveMound (-4.5,-12.5) clears
  (2.5 > 2.248). The crossing must still complete (L1 un-waived).
- R1 :394 (bandit + 2 = (-4,-8)) clears mossBoulder (2.12 > 1.70).

## Hunk classification (vs 818d8bc; from `git diff`)

| file | base hunk | class |
|------|-----------|-------|
| CONFIG.js | +7 after :60 | world{} keys |
| CONFIG.js | :86 | regionA ghoul z |
| CONFIG.js | +2 after :275 | player camera keys (C1 window :270-279) |
| region-manager.js | :99 | clampPlayer -> clampPlayerPlane rename (body byte-identical; the existing corridor comment line is untouched) |
| region-manager.js | +4 after :131 | clampEnemyToHomeSide radial (C11) |
| region-manager.js | +~95 after :133/134 | adjacent helpers (radial / collider / visual radius) + new clampPlayer |
| region-manager.js | :253 | ground repeat |
| region-manager.js | +~71 after :274/275 | live collider + validator methods, adjacent to the clampEnemyToHomeSide wrapper |
| region-manager.js | :297 | ground disc radius |
| region-manager.js | :316 | mist size |
| game.js | +6 after :472 | clampPlayerToBounds |
| player.js | :899-:946 (5 hunks) | updateCamera only; wheel / mousemove / lock-on framing (:907-929) bytes unchanged |

Added prototype lines contain no "free" and no key-shaped literals.

## Deviations / interpretation notes
1. Validator trigger: `spawnReport` is written on the first
   `pushOutOfProps` call, i.e. the first clampPlayerToBounds frame (boot
   frame 1), not in the RegionManager constructor. This keeps the
   constructor out of the diff, since it is not a sanctioned window. It
   still runs once, at boot, from CONFIG for both regions.
2. `exempt[]` carries the corridor-exempt colliders
   (`kind:'collider-corridor'`). No gate-guard entry, because the ghoul was
   moved.
3. Negative control is judged on violations NEW vs the same-build baseline
   report, because the baseline already carries the 2 predicted spawn
   violations. Expected new = {A prop#0 side, B enemy#2 radius}.
4. The R1 floor is reported as its own gating id `PRES-R1` (WAIVED
   allowed); `PRES` = scope / hunk / frozen / secrets. R5-5 = organic +
   R2 floor (WAIVED allowed).
5. The R5-2 FAIL-RETUNE-PENDING class (see above) is a harness
   interpretation of C12. Testerbot to confirm on lane recovery.
6. The lunge step in Player.update (player.js:884-890) runs after
   clampToBounds, so an attack lunge can move the player up to 0.25 units
   past a collider or rim for one frame (re-clamped next frame). This is
   outside the sanctioned player.js window, so it was left. The W-walk
   probes never attack.
7. A2 pre: `tests/artifacts/r5-pre-a2.json` does not exist (no
   pre-Devbot R5 smoke ran). The harness measures it on a git-archive copy
   of 818d8bc and writes the artifact (R4 archive-baseline pattern).

## IO next steps
1. `python3 tests/r5parts/build.py` (assembles
   tests/wh_world_r5_validation.py; py_compile + dup-def check — the parts
   were checked for duplicate defs by hand only).
2. Smoke: `WH_SMOKE=1 WH_W5_FLOOR=0 python3 tests/wh_world_r5_validation.py`,
   then the full run. Expected: R5-2 = FAIL-RETUNE-PENDING (B spawn), the
   rest PASS / WAIVED, unless the smoke shows otherwise.
3. Rule the tree-footprint retune (above) before the full verdict run.
