# TESTERBOT SPEC — Witch Hunter World R1: Validation Plan (gate step 2)

Author: Testerbot (independent validator-author). Date: 2026-09-30.
Devbot spec of record: io/specs/devbot-spec-wh-world-r1.md (read-only; do not fix —
mismatches are reported as amendment notes, never patched in the spec by me).
Authority for ACs: devbot-spec-wh-world-r1.md lines 160-185 (A1-A8) + verdict
protocol lines 201-205. Audit doc 61 is upstream authority for the devbot spec only.
I derive tests from the SPEC, not the audit, so spec-audit divergence does not
change my method.

## Harness
- File: tests/wh_world_r1_validation.py (Playwright sync API, headless chromium,
  `--enable-unsafe-swiftshader`). Boot: spawn prototype/server.py (port 8791) or
  reuse an external server via `WH_BASE_ROOT` env (v2 pattern from
  wh_v7_weave.py:10-11), load `index.html` (NOT the build — this is a source-tree
  validation; the build is only touched by A7), watch console errors + pageerrors.
- Harness discipline (mirrors wh_combat_ds1_validation.py): `check(ac,name,ok,detail)`
  records and prints one AC-line per check; per-AC functions `ac_a1..ac_a8`; every
  AC body wrapped in try/except so a runner exception becomes recorded FAIL data,
  not a harness crash; runtime budget guard; exit 0 ALWAYS (failures are data).
- Organic-path law (devbot spec :150-152): real keyboard events via
  `page.keyboard.down/up` (page listens on document, player.js:158-181, so
  keyboard events on the page reach the game). window.WH_GAME / WH_DEBUG reads
  are fine; direct state mutation as a TEST act is banned. The ONLY sanctioned
  debug writes are teleport (WH_DEBUG.teleportPlayer, a shipped debug API) for
  positioning before organic play, and the WH_DEBUG damage hook for A3 fallback
  if organic kill is unreachable. `page.evaluate` that only READS is always fine.
- Env overrides: `WH_BASE_ROOT` (default http://localhost:8791/), `WH_SMOKE=1`
  (short mode: skip long-duration ACs A2-sprint/A3-organic-kill where noted),
  `WH_R1_PORT` (server port, default 8791).
- Headless-safe luminance: read pixels via `canvas.toDataURL()` after a forced
  `renderer.render` — the WebGLRenderer is created without
  preserveDrawingBuffer (game.js:34), so toDataURL after a rAF may be blank.
  The harness calls `renderer.render(scene,camera)` synchronously inside
  `page.evaluate` immediately before toDataURL, which guarantees buffer content
  (buffer clear happens on compositing, not on render). SwiftShader records
  honestly at 1x1 sample steps.

## Per-AC validation method (A1-A8)

### A1 — prop ground-align (M-01), tolerance |minY| <= 0.02
Method: post-boot, `WH_DEBUG.getRegionManager().groups` traversal. For BOTH
built regions (groups[regionA.id], groups[regionB.id]): walk each group's
children; skip ground mesh, mist plane, and enemy roots (identifiable as
enemies via WH_DEBUG.getEnemies / enemy.root). Every remaining child is a prop
instance. For each prop instance compute `new THREE.Box3().setFromObject(obj)`
(WORLD space — Box3.setFromObject applies updateMatrixWorld), read
`box.min.y` = world minY of the placed prop.
- PASS: every prop in both regions has |min.y| <= 0.02. Detail records per-asset
  worst offenders (asset, scale, minY) for the top 5 worst.
- Secondary spec clause ("|max.y - expectedTopFromScale| consistent with scale"):
  record `max.y` and `WH_ASSETS.groundHeight(asset)*scale` per prop; assert
  |max.y - height*scale| <= 0.05*scale. This catches "sunk but tall" fakes. The
  0.05*scale tolerance absorbs rotY-induced height wobble for tilted props
  (stoneCrossTilted, fallenLog) where the world bbox differs from identity.
- Note: region B builds only after travel/prewarm. VALIDATED METHOD (smoke run
  4-5): the harness walks the player toward the boundary (teleportPlayer to
  boundary.z + 22 — inside CFG.preWarm.distance=30) and waits 2.5s; the
  manager's own logic then prewarm-builds region B organically. Direct
  `buildRegion(id)` calls FAILED in smoke (it dereferences DEFS differently
  than expected and throws) — do not use. Props are joined to CONFIG entries
  by (x,z) match within 1e-6 (all 104 props joined in the live run).
- Pre-fix expectation: FAIL (props sink ~half their height when the baked
  template offset is overwritten by the `y=0` write at region-manager.js:327).

### A2 — actor ground-align (M-02), idle |minY| <= 0.02, sprint max dev <= 0.05
Subjects: player body (WH_DEBUG.getPlayer() -> .root/.body chain), bandit,
ghoul (WH_DEBUG.getEnemy(i).ref). All standing on flat ground (y=0 plane).
- Idle: after a 1s settle, Box3.setFromObject(body-root).min.y for each of the
  three; PASS if all |minY| <= 0.02.
- Sprint: hold `page.keyboard.down('w')` + `down('ShiftLeft')` for 2s
  (collectMoveInput reads k['KeyW'] at player.js:230 and ShiftLeft at :236 —
  Playwright 'w' sends code KeyW; verify via WH_DEBUG position delta > 2m).
  Sample player body minY every ~150ms; PASS if max |deviation from 0| <= 0.05.
- Ghoul hop: ghouls hop while chasing (enemy.js:266-271 hop arc raises root
  ABOVE baseline). The AC's idle sample is taken while enemies are at spawn
  (fsm 'idle'); the sprint window samples the player only. If a ghoul is
  mid-hop during an idle sample, minY > 0 is animation, not a grounding bug —
  the harness records it but treats sustained idle float as the signal.
  Pre-fix smoke: idle floats of ~0.09-0.14 for all actor types (a real
  grounding defect, NOT hop artifacts).
- Keys released in finally (`keyboard.up` for both) so later ACs are clean.
- Pre-fix expectation: FAIL (bodies float or sink by scale-mismatch because the
  template shift rescales wrongly at :327/:342 and bodyBaseY captures unscaled
  offsets — spec D1.3's latent-scale bug).

### A3 — corpse ground-align (M-03), |minY| <= 0.05 after settle
Primary path (organic): teleport near a bandit in region A, engage lock-on
('f') or face it, then click (mousedown fires tryAttack, player.js:182-184;
organic mouse events via `page.mouse.click` at canvas center). Loop clicks
until enemy fsm === 'dead' (bandit hpMax 70, player attack damage CFG-driven
~12/hit so ~6+ hits; loop max 20 attempts with 400ms spacing, stamina permitting).
After fsm === 'dead', wait settleDuration + overshoot window (ANIM.death.settle
CONFIG values; harness waits a fixed 3.5s to cover settle + bounce decay), then
Box3.setFromObject(enemy.root).min.y; PASS if |minY| <= 0.05.
- Organic path may fail for reasons unrelated to grounding (kiting, leash,
  attack whiff at spawn offset). Fallback (sanctioned, still organic-adjacent):
  WH_DEBUG damage hook — if no WH_DEBUG damage API exists (current tree has
  none; getEnemy(i).ref.takeDamage is a JS-object method, not a test-only
  mutation — calling e.takeDamage(hpMax) via evaluate is a direct state write
  and BANNED as a TEST act under the organic law, UNLESS the organic path is
  unreachable, in which case it is recorded as the fallback used + note). The
  spec of record says "kill an enemy (organic inputs)" — so the harness tries
  organic first, records attempts, and only if zero dead enemies after the
  click-budget uses `WH_DEBUG.getEnemy(0).ref.takeDamage(9999)` marked
  `detail="fallback: damage-hook (organic kill unreachable in N clicks)"`.
  Verdict under fallback is reported but flagged `partial-organic` in notes.
- Pre-fix expectation: FAIL (death drop writes root.position.y = -0.3 hardcoded
  regardless of body pivot — corpse rests either sunk or floating by the
  baked-offset mismatch; spec D1.6).

### A4 — ground luminance ring readback (M-09 proxy)
After settling, run `page.evaluate`: force one `renderer.render(scene, camera)`,
then `canvas.toDataURL('image/png')`, decode base64 PNG in Python (stdlib
struct/zlib — no PIL). SAMPLE VALIDATED IN SMOKE: a screen-space ring at 35%
of min(w,h) is dominated by the uniform fog band (luminance ~158 flat) and
passed for the WRONG reason; the actual visible ground occupies the lower
~35% of the frame behind the player (verified via an 8x8 luminance grid
probe). Method: sample the GROUND BAND — rows y in [0.72h, 0.95h] x cols
x in [0.30w, 0.70w] (the near-field ground behind the player). PASS: band
mean luminance (0-255) > 20 AND band pixel stddev > 4. This proves the
ground is not rendering near-black (currentColorA 0x3d3a2c *
NearestFilter-no-mipmap renders ~8/255 flat under SwiftShader pre-fix) and
has visible texture variance (blotches). Pre-fix evidence: mean=7.91 sd=1.67
(52992 px) — correctly RED.
- Headless-safe: recorded, evidence numbers in detail (mean, stddev, n).
- Pre-fix expectation: FAIL (black ground — mean luminance < 20 expected).

### A5 — temporal shimmer (M-12 proxy), RECORD-ONLY
Same readback machinery: slowly pan camera (repeated small setCameraYaw
increments via WH_DEBUG.setCameraYaw — a debug API, reading only camera state)
across ~4s, sample the same far-ground band coordinates (rows y in
[0.66h, 0.78h], cols x in [0.25w, 0.75w], strided) each 500ms, compute
per-pixel temporal stddev across frames. Report mean temporal stddev + max.
NOTE from smoke: SwiftShader rendered 0.000 temporal stddev pre-fix (fog
dominates the far band and minification shimmer is suppressed at these
distances); the record is the evidence either way. NO PASS/FAIL impact: verdict is
RECORD with values. (SwiftShader minification shimmer is the doc-61 P2 watch
item; this is the evidence record for a later pass.)
- Note: setCameraYaw writes camYaw (game.js:473-475) — camera is presentation,
  not gameplay state; sanctioned as the pan mechanism.

### A6 — suite preservation floors
Floors are DISPATCH-TIME captures (not freeze-time, per spec A6 :174-179 —
ds1 is concurrently maintained):
- weave (tests/wh_v7_weave.py): sha256 d2893c23b834337936fdc9440f9f3cf99736cede2bbc28e647bcf9f9566b4c9b,
  expected profile "10/8" (10 PASS / 8 FAIL) as captured at dispatch.
- ds1 (tests/wh_combat_ds1_validation.py): sha256 9093216de6a3da6dd3d392fae86a701c623dafe7b2fafe485a00cafddfdf49fb
  — capture-at-smoke: its PASS/FAIL profile is captured by MY smoke run
  (expected pre-fix 2 PASS / 16 FAIL per devbot spec :154-156) and THAT capture
  becomes the floor for Devbot's round.
Floor rule: Devbot's diff introduces ZERO new failing test IDs vs the
dispatch-time capture (a test that was PASS before must not flip to FAIL;
pre-existing FAILs staying FAIL is fine and expected).
Harness role: A6 records both suite sha256 at run start + (when run with
`WH_R1_SUITES=1`) invokes both suites as subprocesses, parses their JSON
summary lines, and set-diffs failing IDs vs the captured profiles embedded in
this harness. Default smoke runs A6 in capture mode only (hash + embedded
profile assertion) to bound runtime; full suite invocation happens at
Devbot-validation time.

### A7 — rebuild load-assert
Only meaningful post-Devbot (build must be regenerated). Harness: runs
`python3 tools/build_v7.py`, then loads `builds/v7-playable.html` in a FRESH
page with console/pageerror watch, waits WH_DEBUG ready (wh_combat_ds1
wait_ready pattern :64-85), asserts zero console errors, zero pageerrors, and
WH_DEBUG ready within 20s (AC13-style). Plus index.html + style.css
sha256 vs freeze values (freeze: cec75217eb376395cea4642a7640c3d1d9314567f0e3b8c3222c72f7dec2b637,
d31fe8487155bbfdb734e233c2973f85204e12a13ff4a5836520ec3db83c1fb7) — byte-identical.
At SMOKE time (pre-fix, no rebuild performed): PASS is "existing
builds/v7-playable.html loads clean" (it is the frozen weave build a5b5cfdd0e95ab8575f88a76d8073844c208e61f55b6ac8c552af10af19e2a32).
Pre-fix expectation: PASS.

### A8 — scope set-diff via git status
Harness shells `git status --porcelain` and set-diffs against the ALLOWED
mutation surface from the devbot tree-state contract: exactly 5 editable files
(prototype/js/assets.js, region-manager.js, game.js, CONFIG.js, enemy.js) plus
Devbot's own deliverable notes (io/reports/2026-09-30-world-r1-implementation.md)
plus pre-existing dirty files that were already dirty at freeze (docs/planning
04/08/17/27/33, prototype/index.html, style.css, player.js, spells.js,
tools/build_v7.py, tests/*, io/* probe/rebuild/compare/dbg files from the
concurrent workstream, prototype/builds/v7-playable.html). PASS: the set
difference (current status MINUS freeze status MINUS the 5 allowed MINUS
devbot deliverable) is empty. VALIDATED IMPLEMENTATION: the allowlist is
seeded from the freeze manifest itself (/tmp/wh-world-r1-freeze-20260930.txt
- every hashed path + dir entries like io/reports/) UNION the 5 allowed R1
files UNION R1 deliverables UNION concurrent-workstream io/ artifacts
(rebuild_part*/probe_*/compare_*/dbg_*/fix_*/check_*/run_*/dump_*/assemble_*
patterns). Parsing gotcha found in smoke: `git status --porcelain` prints a
LEADING SPACE for unstaged modifications - strip exactly 3 chars, never
`.strip()` the whole line (it ate "docs/" -> "ocs/"). Secrets grep over
`git diff` output for key/secret/token/password assignments must be clean.
Smoke result: PASS (70 dirty paths, 0 outside allowed surface, 0 secrets).
## Pre-Devbot smoke - EXPECTED vs AS-CAPTURED (WH_SMOKE=1, 2026-09-30, run 5)
| AC | Expected | Captured | Evidence |
|----|----------|----------|----------|
| BOOT | PASS | PASS | consoleErr=0 pageErr=0 |
| A1 | FAIL | FAIL | 104 props, minYViol=104 heightViol=104; worst yewTree minY=-9.88 (region-manager.js y=0 overwrite + scale-after-offset) |
| A2 | FAIL | FAIL | idle: player minY=0.117, bandit 0.143/0.117, ghoul 0.107 (all > 0.02; scale-mismatch float) |
| A3 | FAIL | FAIL | damage-hook fallback path, corpse minY=0.08 > 0.05 after settle |
| A4 | FAIL | FAIL | ground band mean=7.91 sd=1.67 (52992 px) - near-black flat |
| A5 | RECORD | RECORD | 8 pan frames, temporal stddev 0.000 (record-only) |
| A6 | PASS | PASS | weave d2893c23b834... (match), ds1 9093216de6a3... (match) |
| A7 | PASS | PASS | v7 build loads clean (0 err, 0 pageerror); buildHash a5b5cfdd0e95; index/style freeze-identity recorded as informational DRIFT (pre-existing weave-round edits, expected) |
| A8 | PASS | PASS | 70 dirty paths, 0 outside allowed surface, secrets clean |
Expected profile MATCHED exactly on the final harness revision. Deviations
found in EARLIER harness drafts (fog-band ring passing A4 for the wrong
reason; NaN-poisoned teleports) were fixed before the recorded run - they
were harness bugs, not tree state. A2 sprint segment is skipped under
WH_SMOKE=1 (full sprint runs in the Devbot validation pass).

## Flake rule
- Any AC that fails with a runner exception, a timeout, or evidence that looks
  environmental (server 500, browser crash, WH_DEBUG not ready) is retried up
  to 2 times (fresh page reload between attempts). If all 3 attempts fail the
  same way with a real assertion miss, it is a true FAIL (no retry credit).
- If an AC fails on attempt 1 and passes on attempt 2, record "flake-retry
  passed" in detail; the AC verdict is the LAST attempt, and the flake is
  counted in the verdict notes. 3 or more flakes across the run = BLOCK: report
  "harness unstable, do not gate on this run" instead of a verdict.
- Deterministic assertion failures (tolerance exceeded with numbers) are NEVER
  retried (retrying only wastes budget); retries are for infra-shaped failures.

## Verdict protocol
Final line of harness stdout is a single JSON object:
```
{"round": "world-r1", "verdict": "PASS|FAIL|RECORD-ONLY",
 "per_ac": [{"id": "A1", "verdict": "PASS|FAIL|RECORD", "evidence": "..."}],
 "suites": {"wh_v7_weave.py": {"sha256": "...", "profile": "10/8"},
            "wh_combat_ds1_validation.py": {"sha256": "...", "profile": "captured-at-smoke"}},
 "flakes": 0, "notes": "..."}
```
- Harness exit code is ALWAYS 0 (failures are data).
- Round verdict (Testerbot-authored, from the harness JSON + my judgment):
  PASS only when A1-A4, A6, A7, A8 all PASS and A5 recorded. A6 new-failing-ID,
  A7 load-error, A8 out-of-scope-file each independently BLOCK.
- honest-PARTIAL allowed only for A5 (record-only) or pre-authorized
  environment limits (SwiftShader render variance) — anything else blocks.

## Amendment notes (spec-of-record mismatches found while authoring)
1. Devbot spec D3 (:145-148) adds `WH_DEBUG.getAssetMeta(name)` — the CURRENT
   tree has no such hook (game.js WH_DEBUG block :435-563 verified). My A1/A2
   read geometry directly via Box3 traversal instead, so validation does NOT
   depend on the hook. If Devbot ships the hook, harness prefers it (reads
   groundMinY) but does not require it.
2. Devbot spec A1 says "expectedTopFromScale" without defining expectedTop; I
   implement it as `WH_ASSETS.groundHeight(asset) * scale` (height is the
   measured template height, groundHeight is its accessor, assets.js:203-208).
3. Devbot spec A2 mentions "ghoul hop" while asserting no float > 0.05 — ghouls
   hop ABOVE ground mid-chase (enemy.js:266-271), so a naive minY sample during
   a hop reads > 0.05 without being a bug. I sample the window MINIMUM (feet
   must touch 0) to keep the AC meaningful. Flagging for amendment awareness.
4. Devbot spec A6 cites weave profile "10/8" — that is 10 PASS / 8 FAIL of 18
   tests. My harness embeds that as the dispatch-time floor and will set-diff
   failing IDs at Devbot-validation time.
5. Devbot spec :163 says "post-build" for A1 — pre-Devbot, region B group may
   not exist without travel; harness builds it via the manager's own
   buildRegion (see A1 note) or reports PARTIAL.
