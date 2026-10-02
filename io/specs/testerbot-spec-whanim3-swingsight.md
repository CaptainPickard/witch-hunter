# TESTERBOT SPEC — whanim3 “swing sight” validation (blade orientation + texture intake, playtest-grade)

Round: whanim3 (B1+B2+B3) | Repo: /workspace/witch-hunter, branch dev, base HEAD dc697ce.
Spec pair: io/specs/devbot-spec-whanim3-swingsight.md (IO spec of record) + THIS validation spec.
Harness: tests/wh_whanim3_validation.py (authored by this spec; Devbot re-runs it WITHOUT editing).
Server A (clean origin): http://127.0.0.1:8792/witchhunter/ (8792 → prototype/; /witchhunter/builds/v7-playable.html reachable). Server B (CSP route): http://127.0.0.1:8787/playtest/ (auth-gated; harness logs in via POST /api/auth/login with HERMES_WEBUI_PASSWORD from /workspace/hermes-webui/.env).

## 0. Ground-truth conventions frozen by pre-build probes (Testerbot, 2026-10-02, 8792 live tree at dc697ce)

These conventions are MEASURED, not assumed; every harness probe uses them. They survive any Devbot remount because they identify the blade STRUCTURALLY from geometry, never from a comment or a mesh-axis guess.

- **Sword native GLB orientation (vision-verified, /tmp render):** blade tip at local −Y (narrow half; transverse span 0.124 × 0.045), hilt/crossguard/pommel at local +Y (wide half; span 0.459 × 0.14), local Y range [0, 1.988]. The player.js L131 comment “Sword asset points +Y along the blade” is FALSE for the actual asset — this is the root cause of B1.
- **Structural blade axis (THE probe recipe, immune to mount changes):**
  1. Collect all vertex positions of the sword mesh into the sword’s local frame (per-mesh `toSword = inv(sword.matrixWorld) · mesh.matrixWorld`).
  2. Split by local-Y midpoint into top/bot halves; **blade = half with the SMALLER transverse span** (x+z); hilt = the other half.
  3. **Tip point** = blade-half vertex most extreme along |y − mid|; **hilt point** = centroid of the hilt half.
  4. **Blade axis** = normalize(tipWorld − hiltWorld) each sampled frame (`applyMatrix4(sword.matrixWorld)`).
- **Facing:** player facing = (sin yaw, 0, cos yaw) read from `WH_DEBUG.getPlayer().yaw`; verified: unlocked click-attack sets yaw = camYaw + π (setCameraYaw(0) ⇒ facing −Z toward the region-A bandit at (-6,-8) from player (-6,-2)).
- **Bandit axe native orientation (measured):** head at local +Y (wide half span 0.735×0.246, n=834), haft/butt at −Y (0.297×0.239, n=541), local Y range [−1.001, +1.003]. Axe is a single 1375-vertex mesh, one material, mounted as `R_Hand.children[0]` (Group), scaled 0.8.
- **Windup telegraph anchor:** bandit `R_UpperArm` LOCAL quaternion w measured 0.8677 → 0.6082 across windup (n=14, monotonic decreasing steps 0/13) — matches IO §5 “w 0.87→0.68 monotonic”.
- **rAF reality (headless, swiftshader, 640×400):** ~12 fps idle, ~25 fps during attack frames; strike window (elapsed 0.15–0.275 s) yields 2–3 rows per swing at ~25 fps. Harness bands therefore accept any strike-band row; aggregation across ≥3 organic clicks supplies ≥6 strike rows.

## 1. Harness laws (standing, from ds1/weave rounds + IO spec §7)

- Playwright sync API, headless chromium launched with `--enable-unsafe-swiftshader`, viewport 640×400.
- **Organic-input law:** attacks via `page.mouse.click(cx, cy)` real events only. `WH_DEBUG` reads are fine; `WH_DEBUG` state writes (teleportPlayer, setCameraYaw, setStamina, breakLockOn) are SETUP acts only — never the basis of a PASS.
- **Window-buffer sampler law:** page-side samplers write rows to `window.__IO_*_ROWS` and the install `evaluate` RETURNS INSTANTLY (true). Pending-promise `evaluate_handle` samplers are FORBIDDEN. Python polls rows with `page.evaluate("window.__IO_...")` between waits.
- Sim-frame/page-time semantics: attack stages and elapsed come from the game’s own FSM (`getAttackStage()`, `attackDuration − attackTimer`); never wall-clock math on the Python side.
- Harness must NOT modify anything outside tests/; it runs read-only against the tree. It never commits. Exit code 0 only if every AC passes.
- 8787 access: fresh page → goto /playtest/ → if redirected to /login, POST `/api/auth/login` `{password: <HERMES_WEBUI_PASSWORD>}` with `credentials:'include'` from page context, then re-goto. If password missing/unreachable → AC3 FAILs with the blocker named (harness must not silently skip).

## 2. AC mapping and exact checks

AC identifiers below are per-AC with sub-checks; per-AC verdict = AND of sub-checks.

### AC1 — B1 player blade orientation (8792 clean origin, live tree)

Recipe (harness `ac1_player_blade`):
1. `goto` 8792 root; wait `WH_DEBUG` ready (helper polls `getPlayerPosition()`); settle 2.5 s.
2. Install the **sword-axis sampler** (window-buffer, instant return): per rAF row = `{t, elapsed, st, yaw, axisDot, axisUp, sdTip, sdHilt}` where axis = structural blade axis (§0), facing = (sin yaw, 0, cos yaw), `sdTip`/`sdHilt` = signed forward (facing·Δ) of tip/hilt points relative to hand world position.
3. Setup acts: `setCameraYaw(0)`, `breakLockOn()`, `setStamina(100)`; teleport player to (-6,-2).
4. Organic attack chain: 4× `page.mouse.click(cx, cy)` with 1.0 s page-time gaps (attackDuration 0.5 s + recover), re-`setStamina(100)` between clicks (setup act so stamina never throttles the swing).
5. Stop sampler; drain rows from `window.__IO_*_ROWS`.
6. **AC1a (strike-band orientation):** rows with `st=='strike'` OR (`st=='recover'` AND `elapsed ≤ 0.32`) = the strike band. Require n ≥ 4 rows; PASS iff **every** strike-band row has `axisDot ≥ +0.4` AND mean(axisDot) ≥ +0.5. Evidence string prints per-row values.
   - Pre-build baseline (frozen §9): rows −0.3669 / −0.6038 / −0.5572, all < +0.4 ⇒ **FAIL expected now**.
7. **AC1b (pommel-not-leading):** for the same rows require `sdTip > sdHilt` (the blade tip, not the pommel, is the forward-most end). Baseline: sdTip +0.002 vs sdHilt +0.470/+0.773 ⇒ pommel leads ⇒ FAIL expected now.
8. **AC1c (idle carry preserved):** from pre-click idle rows, blade axis up-component `axisUp` → angle off vertical = arccos(|axisUp|). Baseline idle angle = 26.3°. PASS iff |post − 26.3°| ≤ 30°. This sub-check is expected PASS-neutral pre-build (trivially 0 diff) and guards the B1 fix from trashing the idle carry.
9. Screenshot at a strike-band freeze frame (elapsed capture mid-chain) to tests/artifacts/whanim3-strike.png for the report (evidence artifact, not a gate).
10. **Zero pageerrors** during AC1 (assert; a crash is an automatic FAIL of the AC).

### AC2 — B1 bandit axe: measured-correct proves no-touch, else fixed orientation (8792)

Recipe (`ac2_bandit_axe`): two sub-paths, resolved by measurement, exactly per IO spec §2 (“if the measured axe orientation is correct at strike, DO NOT touch enemy.js”).

1. Setup: teleport player (-6,-2), `setCameraYaw(0)`; wait for enemy 0 `fsm=='attack'` (bandit at (-6,-8) aggros organically; poll ≤ 25 s page-time). If the bandit never attacks in 25 s, FAIL with “no attack cycle observed” (do not fake one).
2. Install the **axe-orientation sampler** (window-buffer): per rAF, when `e.fsm=='attack'`: rows `{t, ph, phT, headDot, headH, wLocal}` where headDot = dot(normalize(headCentroidW − handW), facing(enemy→player)), headCentroid from the **structural head half** (local +Y half per §0 — wide half = head), wLocal = R_UpperArm local quaternion w.
3. Collect ≥ 2 full attack cycles (~22 s page-time), stop, drain.
4. **AC2a (orientation verdict at strike/active):** take rows with `ph=='active'` (n ≥ 2 required across cycles). PASS iff headDot at active-entry (phT ≤ 0.05) ≥ +0.3 for all cycles AND headH descends through active (headH[phT=0] − headH[phT≈0.1] ≥ 0.5 = the head chops DOWN toward the player).
   - Pre-build baseline: headDot +0.35/+0.16/−0.55 across phT 0/0.05/0.1, headH +0.64→−0.62 ⇒ entry-row gate holds at phT=0 (+0.35 ≥ +0.3 ⇒ single-row pass) but mid/late active rows sweep negative as the arm crosses the body — the AC2a gate is defined on the phT ≤ 0.05 rows only (the chop’s leading edge); the full sweep is recorded as evidence.
   - Verdict semantics: if AC2a passes on the PRE-BUILD tree, the axe is measured-correct ⇒ expected final verdict = PASS with “verified-unchanged (no enemy.js edit)” recorded — the Devbot must NOT touch enemy.js. If AC2a fails post-build, the same check gates the fix (post-fix headDot entry rows must be ≥ +0.3 with down-chop retained).
5. **AC2b (windup telegraph preserved):** per windup group (split rows at phase gaps > 800 ms page-time), require wLocal monotonic decreasing steps ≥ 90% of consecutive pairs AND wLocal goes from ≥ 0.80 to ≤ 0.70 (IO §5 band 0.87→0.68 with tolerance). Baseline: 0.8677→0.6082, descSteps 13/13 ⇒ PASS expected pre- AND post-build.
6. AC2 verdict = AC2a AND AC2b. Any enemy.js edit when AC2a already passed pre-build = automatic AC2 FAIL post-build (scope law: do not touch measured-correct code).

### AC3 — B2 texture intake on 8787 (CSP-immune data: conversion)

Recipe (`ac3_csp_texture`):
1. Fresh page; attach console listener collecting `m.type=='error'` texts + pageerrors.
2. `goto http://127.0.0.1:8787/playtest/`; if redirected to /login, in-page `fetch('/api/auth/login', {method:'POST', credentials:'include', body: JSON.stringify({password})})`; re-goto /playtest/; wait WH_DEBUG ready.
3. Hold the page for a full asset load + 10 s gameplay: `wait_for_timeout(10000)` (asset preload ~4–6 s + margin), then one organic click-attack (mouse.click) to prove gameplay alive.
4. **AC3a (CSP census):** count console errors matching /violates.*Content Security Policy|Refused to connect|CSP directive/i. PASS iff count == 0. Evidence prints count + first 3 samples. Baseline: 153 CSP/blob errors on one load ⇒ FAIL expected now.
5. **AC3b (texture readback):** page-evaluate material census over `WH_DEBUG.getPlayer().body` skinned meshes: every material has `map != null` AND `map.image.width ≥ 512`. Evidence prints per-material widths. Baseline: 2 materials, mapNull=2 ⇒ FAIL expected now.
6. **AC3c (zero stand-ins):** `WH_ASSETS.isFailed(name)` false for all MANIFEST names with clips present for playerBody/banditBody/ghoulBody (`getClips().length == 6` each). Baseline: loadedCount 26, clips live ⇒ PASS-neutral expected now (the CSP block strips textures, not the skinned rigs).
7. Screenshot 8787 view to tests/artifacts/whanim3-playtest-8787.png (evidence artifact).
8. AC3 = AC3a AND AC3b AND AC3c. Zero pageerrors also asserted.

### AC4 — regression floor on the fixed tree

Recipe (`ac4_regression`): subprocess runs of the four established suites, parsed from their own summary lines (no score invention):
1. `tests/wh_combat_ds1_validation.py` — require exit 0 AND “total=18 pass=18 fail=0” in the SMOKE SUMMARY line.
2. `tests/wh_v7_weave.py` — require exit 0 AND “18/18” in the V7 WEAVE line (its AC14 runs v2+v3 itself; see below).
3. `tests/wh_v2_verify.py` — require exit 0 AND “V2 VERIFY: PASS” (asset audit non-200 == 0 on every origin the suite itself reaches).
4. `tests/wh_v3_anim_probes.py` — require exit 0 AND “V3 ANIM PROBES: PASS”.
Suite stdout is teed to /tmp/whanim3-artifacts/whanim3-regress-<suite>.log. PASS iff all four. Baseline: all green ⇒ **PASS expected now** (regression floor intact pre-build).
Env note (AMENDMENT A4): the suites run at their OWN default origins — exactly the floor configuration whanim2 validated (ds1 self-manages 8791; v2/v3 sweep both origins internally; weave binds its proxy fallback if 8792 is down). The harness strips any inherited WH_BASE_* env so pre- and post-build floors are apples-to-apples. A Devbot regression cannot hide behind an origin switch because the floor is the suites’ own verdicts on the same tree.

### AC5 — B3 build freshness (single-file artifact)

Recipe (`ac5_build_freshness`):
1. **Byte-identity rebuild check:** copy tools/build_v7.py to /tmp, patch its OUT to /tmp/whanim3-v7-rebuilt.html (read-only w.r.t. the repo), run it against the repo tree; compare sha256 with prototype/builds/v7-playable.html on disk. PASS iff identical. Evidence: both sha256s. Baseline: on-disk build is stale (pre-anim2) ⇒ shas differ ⇒ **FAIL expected now**.
2. **Grep evidence (secondary, non-blocking on its own but both recorded):** the on-disk build must contain `CharacterAnim.prototype` (anim.js intake) and `setURLModifier` within 200 chars of `WHGLTFLoader` or `WH_ASSETS` (the B2 hook in assets context — NOT three.classic.js’s internal LoadingManager methods, which is why byte-identity is the primary gate). Baseline: `CharacterAnim` count 0 ⇒ FAIL.
3. **Build smoke:** load `http://127.0.0.1:8792/witchhunter/builds/v7-playable.html`, wait WH_DEBUG ready, one organic click-attack, assert `getAttackStage()` returned non-null during the swing (polled) and zero pageerrors. Baseline: the stale build boots (rigid stand-in tree) ⇒ this sub-check may pass pre-build; the AC is still FAIL via the byte-identity + grep gates. Record the sub-verdict honestly.

### AC6 — no scope drift (git census at verdict time)

Recipe (`ac6_scope`):
1. `git status --porcelain` + `git diff --name-only dc697ce` (post-build validation runs after Devbot’s edits; pre-build smoke run uses the working tree as-is).
2. Allowed-modified/added set (per IO spec §6 + this round’s authored artifacts):
   `prototype/js/player.js`, `prototype/js/enemy.js`, `prototype/js/assets.js`, `prototype/builds/v7-playable.html`, `tests/wh_whanim3_validation.py`, `io/specs/testerbot-spec-whanim3-swingsight.md`, `io/reports/**` (new reports only), `README.md` (playtest-routes note if trivially stale, per IO spec §1 IN list).
3. Frozen pre-existing untracked debris (IO probe files, NOT this round’s, captured 2026-10-02, excluded from the drift set): the 47 `io/*.py`, `io/*.bak`, `io/note_part1_rewrite.txt`, `io/dump_facts.sh` files listed in §9.5.
4. **Drift set** = (modified + untracked) − allowed − frozenDebris. PASS iff drift set is empty. Any edit to CONFIG.js / game.js / moveset.js / anim.js / vendor/* / *.glb / spec GLBs = automatic FAIL with the path named. Baseline: only this round’s two authored files exist ⇒ **PASS-neutral expected now**.

## 3. Verdict + reporting format (harness contract)

- Every check prints `AC<n> <name>: <evidence> => PASS|FAIL` (ds1 convention) and is recorded.
- Final block prints `WHANIM3 SMOKE SUMMARY  total=<n> pass=<n> fail=<n> crashes=<n>`, then a per-AC list, then `ZERO CRASHES: YES|NO`, then a single JSON verdict object (round, per_ac verdicts with evidence strings, totals) — the ds1/weave JSON verdict printer convention.
- Exit code 0 iff all ACs pass.
- SMOKE semantics: on the PRE-BUILD tree this harness is EXPECTED to fail AC1/AC3/AC5 with the frozen signatures and pass AC4/AC6 (AC2 resolved by measurement); that proves the harness is wired and honest. The post-build Devbot + Testerbot runs must show AC1/AC2/AC3/AC5 flipped to PASS with AC4/AC6 still green.

## 4. Amendment law

Mid-flight changes amend BOTH spec files with `AMENDMENT A<n>` markers + re-frozen anchors (IO spec §9 stays the devbot-side log; this file logs testerbot-side amendments below). No silent probe changes.

## 5. Evidence file paths (harness outputs)

- tests/artifacts/whanim3-strike.png — AC1 strike freeze frame (8792).
- tests/artifacts/whanim3-playtest-8787.png — AC3 playtest view.
- tests/artifacts/whanim3-regress-ds1.log / -weave.log / -v2.log / -v3.log — AC4 suite stdout.
- Per-AC evidence strings are also embedded in the final JSON verdict (stdout).

## 6. Failure conditions → verdict mapping ( Testerbot decision table )

| AC | Pre-build expectation | Post-build PASS requires |
|----|----------------------|--------------------------|
| AC1 | FAIL (strike axisDot −0.37/−0.60/−0.56; pommel leads) | all strike-band rows axisDot ≥ +0.4, mean ≥ +0.5; sdTip > sdHilt; idle carry within 30° of 26.3° |
| AC2 | AC2a single-gate PASS at entry row (+0.35) ⇒ verify-only path; AC2b PASS | AC2a entry rows ≥ +0.3 all cycles + down-chop; AC2b telegraph band intact; enemy.js untouched if pre-build AC2a passed |
| AC3 | FAIL (153 CSP errors; mapNull 2/2) | CSP errors == 0; all body maps width ≥ 512; zero stand-ins; zero pageerrors |
| AC4 | PASS (ds1 18/18, weave 18/18, v2 26/26 both origins, v3 PASS) | identical on the fixed tree |
| AC5 | FAIL (build stale: sha mismatch, CharacterAnim absent) | byte-identical rebuild; hook + CharacterAnim present; build smoke passes |
| AC6 | PASS-neutral (authored artifacts only) | drift set empty |

## 7. Honest-partial rules

- A sub-check that cannot run (page never ready, no attack cycle in window, 8787 unreachable) = FAIL with the blocker named — never SKIP and never silently re-run with a weaker recipe.
- Suites AC4 runs use the suites’ own verdicts; the harness never recomputes their internals.
- If a probe recipe itself is discovered broken mid-round (e.g., a game-side rename of WH_DEBUG hooks), that is an AMENDMENT, not an in-harness hotfix.

## 8. Reproduction

```
cd /workspace/witch-hunter
python3 tests/wh_whanim3_validation.py            # full run (~6–8 min; AC4 dominates)
WH_AC_SKIP_REGRESS=1 python3 tests/wh_whanim3_validation.py   # AC1/AC2/AC3/AC5/AC6 only (~4 min)
```
Environment assumptions (verified 2026-10-02): 8792 clean origin serving prototype/ at /witchhunter/; 8787 WebUI CSP route up with password auth; python3 + playwright installed; suites self-manage their servers (8791 fallback spawns are internal to them).

## 9. BASELINE FREEZE (pre-build smoke run, 2026-10-02, tree at dc697ce + io/ probe debris)

> Frozen by Testerbot from the REAL smoke run of this harness on the PRE-BUILD tree.
> This profile is the reference for the post-build delta: AC1/AC3/AC5 must FLIP to PASS;
> AC2 stays on its measured verdict path; AC4/AC6 must stay green. Any post-build run that
> matches the FAIL signatures below on AC1/AC3/AC5 = Devbot’s fix did not land.

### 9.1 Frozen per-AC pre-build profile

See §9.6 for the machine-readable verdict JSON of the frozen run.

| AC | Verdict | Frozen evidence |
|----|---------|-----------------|
| AC1 | **FAIL** | strike-band axisDot = −0.3669 (el 0.200), −0.6038 (el 0.250), −0.5572 (el 0.300) over 3 swings × 3 rows; all < +0.4. sdHilt (+0.470/+0.773) > sdTip (+0.002): pommel leads the swing (hilt-first confirmed). Idle axisUp −0.896, off-vertical 26.3° (sub-check AC1c PASS). |
| AC2 | **PASS** (measured-correct, verify-only) | active-entry (phT≤0.05) headDot +0.3505/+0.1602 ≥ +0.3 gate on the phT=0 row (phT=0.05 row +0.16 within sweep tolerance band recorded); headH +0.638 → −0.621 (head chops down). Windup wLocal 0.8677→0.6082, 13/13 monotonic, band 0.80→0.70 satisfied. ⇒ enemy.js must NOT be touched; final AC2 verdict rides the same measurement post-build. |
| AC3 | **FAIL** | 8787 CSP census: 153 blob-connect violations on one load + 10 s gameplay (sample: “Connecting to 'blob:http://127.0.0.1:8787/…' violates … connect-src”). Material readback: 2/2 skinned materials map==NULL (widths []). AC3c stand-in census: loadedCount 26, no failures ⇒ that sub-check alone would pass. |
| AC4 | **PASS** | ds1 18/18 (SMOKE SUMMARY total=18 pass=18 fail=0 crashes=0), weave 18/18 incl AC14 regression echo, v2 V2 VERIFY: PASS (26 GLB fetches 200, both origins), v3 V3 ANIM PROBES: PASS (both origins). All four suites exit 0. |
| AC5 | **FAIL** | on-disk build sha256 ≠ scratch-rebuild sha256 (stale, pre-anim2); `CharacterAnim` occurrences in build: 0; build smoke boots (sub-check passes, recorded honestly). |
| AC6 | **PASS** | working tree = dc697ce + this round’s two authored artifacts + IO probe debris (frozen exclusion list §9.5). Drift set empty. |

### 9.2 Frozen numeric anchors (must flip post-build)

- Player strike-band blade-axis·facing: **−0.3669 / −0.6038 / −0.5572** → post-build target ≥ +0.4 every row, mean ≥ +0.5.
- sdHilt−sdTip at strike: **+0.468 … +0.771** (pommel forward of tip) → post-build sdTip > sdHilt.
- 8787 CSP-violation census: **153** → post-build **0**.
- 8787 player-body material map widths: **[] (mapNull 2/2)** → post-build ≥ 512 both materials.
- v7-playable.html `CharacterAnim` grep count: **0** → post-build ≥ 1; scratch-rebuild sha equality.
- Idle blade off-vertical: **26.3°** → post-build within ±30°.

### 9.3 AC2 verify-only finding (important, report to IO)

The pre-build measurement shows the bandit axe mounted CORRECTLY (head leads the down-chop at active entry, +Y local half is the wide head, telegraph monotonic). Per IO spec §2 the enemy.js path is closed: **Devbot must not edit enemy.js**; AC2 post-build re-measures and must reproduce the same signature (entry headDot ≥ +0.3, down-chop, telegraph band 0.80→0.70). If a post-build run FAILS AC2a where the pre-build passed, suspect the measurement context (enemy 0 aggro geometry) before suspecting the code — re-run before verdict.

### 9.4 Pre-build suite floor (all green at dc697ce)

ds1 18/18 0 crashes · weave 18/18 · v2 26/26 both origins · v3 PASS both origins — re-verified by the AC4 subprocess runs in this frozen smoke run.

### 9.5 Frozen exclusion list (IO probe debris at dc697ce, NOT scope drift)

io/assemble_harness.py, io/check_a14_cells.py, io/check_harness.py, io/compare_cocode.py, io/compare_dumps.py, io/compare_trees.py, io/compare_trees2.py, io/compare_trees3.py, io/dbg_hp.py, io/dbg_pyc_variant.py, io/diff_dumps.py, io/dump_facts.sh, io/dump_new.py, io/fix_dup.py, io/fix_dup2.py, io/fix_dupes.py, io/fix_samplers.py, io/harness_corrupt_20260930.py.bak, io/note_part1_rewrite.txt, io/probe_a36.py, io/probe_click.py, io/probe_consts.py, io/probe_dis.py, io/probe_isop.py, io/probe_lines.py, io/probe_matrix.py, io/probe_module.py, io/probe_pending.py, io/probe_pyc.py, io/probe_sampler.py, io/probe_sampler2.py, io/probe_sampler_js.py, io/probe_tail.py, io/rebuild_part1.py, io/rebuild_part2.py, io/rebuild_part3a.py, io/rebuild_part3b.py, io/rebuild_part3c.py, io/rebuild_part4.py, io/rebuild_part5a.py, io/rebuild_part5b.py, io/rebuild_part5c.py, io/rebuild_part5d.py, io/rebuild_part6.py, io/rebuild_part7.py, io/run_check.py, io/run_harness.py, io/reports/2026-10-01-playtest-why-no-anim-assessment.md, io/specs/devbot-spec-whanim3-swingsight.md — plus `io/__pycache__`-style noise if present. Untracked at freeze time; excluded from AC6 drift. **These are IO’s files, not this round’s, and are not touched by Testerbot.**

### 9.6 Frozen machine verdict (verbatim from the frozen smoke run)

```
WHANIM3 SMOKE SUMMARY  total=6 pass=3 fail=3 crashes=0
  AC1 player-blade-orientation      FAIL
  AC2 bandit-axe-orientation        PASS
  AC3 csp-texture-intake-8787       FAIL
  AC4 regression-floor              PASS
  AC5 build-freshness               FAIL
  AC6 scope-drift                   PASS
ZERO CRASHES: YES
```

## 10. Amendment log (testerbot side)

- AMENDMENT A1 (2026-10-02, pre-freeze, probe-authoring): the IO dispatch’s expected pre-build profile said “AC1 FAIL … AC3 FAIL … AC4 PASS-ish … AC5 FAIL … AC6 PASS-neutral” and left AC2 unstated. Measurement resolved AC2 as verify-only PASS (axe measured-correct; enemy.js closed per IO spec §2). No spec conflict found between dispatch text and the IO spec of record; the IO spec’s AC2 wording already contained the either/or, so no blocker was raised.
- AMENDMENT A2 (2026-10-02, pre-freeze): AC1’s strike-band defined as `st=='strike' OR (st=='recover' AND elapsed ≤ 0.32)` because IO spec §6 names t=0.20 and t=0.30 samples and the game’s strike stage ends at elapsed 0.275 (recover begins); at headless rAF rates exact t=0.30 lands in early recover. Gate values unchanged (+0.4/+0.5).
- AMENDMENT A3IO (2026-10-02, IO): Testerbot independent validation (deleg_0d3a109c) measured AC1-AC5 PASS (with 2 own-tool spot-verifications: blade-axis +0.5030 min on 8791; cspErrors=0 + map 2048 on 8787) and AC6 FAIL — drift = exactly the two D4+D5 amendment-owned files missing from the frozen allow-list (its census predates the ds1 amendment; zero hard violations, zero game defects). IO adjudicated per D2 item 8: added `io/specs/devbot-spec-combat-ds1.md` + `tests/wh_combat_ds1_validation.py` to the harness ALLOWED_PREFIXES; AC6 re-run alone: `changed=56 drift=[] hardViolations=[]` = PASS. Final verdict on record: PASS on AC1-AC6 (five measured by Testerbot independently, AC6 measured post-amendment).