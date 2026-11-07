# CC-H3 Spire Approach — Testerbot independent validation report
2026-11-07 · feat/world-visuals · worktree `/tmp/wh-worldfeat` · HEAD `42ba377`

**Verdict: PASS (against the AMENDED spec, V-9 re-ruled to ≥ 6.0 m at (0,-709))**

Validated item-by-item, with my own fresh greps, `node -e` evaluations, and an independently-written clearance model (not a re-run of Devbot's code for the verdicts; Devbot's probe was run as *data* and cross-checked against ≥ 3 seats of my own arithmetic).

---

## Per-item results

| Item | Result | Evidence |
|---|---|---|
| **V-0** Syntax/J-block complete | **PASS** | `node --check` clean on both `prototype/js/CONFIG.js` and `prototype/js/region-defs.js`. Exactly **1** `regionJ: {` key in CONFIG.js (grep = 1; `veil_spire_approach` appears 3×: key + id + walkFrom/interact self-refs). Parsed regionJ top-level keys = id, name, center, groundRadius, groundY, groundColor, groundColor2, groundSeed, scatter, spawn, gravityY, fogColor, fogDensity, ambientLightLevel, door, enemies, props — complete superset, zero missing keys. regionJ registered via `makeRegion(CFG.regionJ, -1)` (line 285). Values match spec verbatim: center (0,-700), radius 40, spawn (0,-730), planeZ -738, doorX 0, doorHalfWidth 2.2, groundColor 855829 (= 0x0d0f15), groundColor2 1119000 (= 0x111318), fogColor 657424 (= 0x0a0810), fogDensity 0.15, ambientLightLevel 0.05. |
| **V-1** conn[8] shape/door/lands | **PASS** | My own evaluated probe (`scratch/cc-h3/validator/connection_probe.validator.js`): `connections.length` = 9; conn[8].from = `veil_galleries`, to = `veil_spire_approach`, axis 'z', planeCoord -738. Door one-sided to J (`walkFrom` J, J-side plane, F-side interact). F interact (7.5, -654, r 3.5); land keys exactly `veil_galleries` (2,-652, face 2,-644) and `veil_spire_approach` (0,-730, face 0,-700); fades 0.3/0.5/0.8; prompt `"E - Descend toward the spire"`. `connectionBetween` resolves the same conn both directions. |
| **V-2** side table | **PASS** | sides: F = -1, J = +1. `sideIn(conn, J)` = +1 == `sideOfPlane(conn, -730)` = +1. Plane asymmetry: `planeIn(F)` = false, `planeIn(J)` = true. My probe's own `sideOfPlane`/`planeIn` evaluations (not Devbot's) confirm. |
| **V-3** clearance + probe | **PASS** | Devbot's probe run as data: **231 checks, 230 PASS, 1 FAIL** — the sole FAIL is the superseded ORIGINAL V-9 (see Adj-1). Every V-3 clearance (door lane, ghouls, props, F-side hook/land) passes. My own independent clearance model (90 J wall circles, wall r 0.45) agrees: door-lane collider-edge minimum **1.5500 m** at lane depth 1–3 m (≥ 1.0 required), zero `±0.5`-window overlap; J ring 10 rows / 90 colliders / radius-40 / diameter 80. |
| **V-4** regionF byte-identical | **PASS** | `git show 42ba377:prototype/js/CONFIG.js` regionF block vs worktree: `cmp` clean — byte-identical. |
| **V-5** seed/groundY/scatter/gravityY | **PASS** | groundSeed **1662061763** — distinct from every landed seed (regionC…regionI = 1662061217, …218, …219, …329(F), …440, …651, …654). groundY 0, scatter false, gravityY -22. All confirmed from live CONFIG eval. |
| **V-6** single crimson accent family | **PASS** | Crimson family = lanternPost ×1 + blightcap ×2, and **only** those. Non-ring props total 15 (of 25 rows: 10 ring walls). Other non-ring assets: mourningStatue ×4, stoneSteps ×2, okRuinColumn ×3, skullPile ×2, mossBoulder ×1 (12 rows) + the 3 crimson = 15. No other assets from the cc-ad1/cc-h2 "crimson" families present. Single accent family = true. |
| **V-7** regionI + connections[0..7] byte-identical | **PASS** | regionI block `cmp` clean vs `42ba377`. connections[0..7] (lines 93–281 in both old & new) `cmp` clean — byte-identical; the CC-H3 block was appended at line 283 without shifting prior text. |
| **V-8** only-two-files-changed | **PASS** | `git diff 42ba377 --name-only` = CONFIG.js, region-defs.js + the two deliverables (build note, probe). Named no-touch files (game.js, region-manager.js, save.js, daynight.js) diff empty. Worktree cleanliness otherwise pre-existing spec/valspec untracked files only. |
| **V-9** AMENDED clear circle ≥ 6.0 m at (0,-709) | **PASS** | My own arithmetic (independent of Devbot's probe, which checked the *original* center): clear radius at **(0,-709) = 6.6848 m ≥ 6.0 m**, binding `mourningStatue` at (-7,-712) (collider r 0.931). Devbot's build note claimed ~7.1 m at this center; my stricter model yields 6.68 m — both satisfy the AMENDED requirement. Ring diameter itself = 80 m (per spec 6a). |

---

## Cross-check: ≥ 3 seats, my arithmetic vs Devbot probe

| Seat | Devbot probe | My arithmetic | Δ |
|---|---|---|---|
| Door-lane min collider-edge clearance | 1.5500 m | **1.5500 m** | 0 |
| J ghoul mutual distance | 30.0000 m | **30.0000 m** | 0 |
| F hook nearest prop | 4.2720 m | **4.2720 m** | 0 |
| F land (2,-652) ring-edge | 9.7313 m | **9.7313 m** | 0 |
| V-9 (0,-702) clear radius | 0.8515 m | **0.8515 m** | 0 |

All agree. (The V-9 (0,-702) agreement is on the *superseded original* target — it confirms the frozen prop layout truly could not meet 12 m, and that AMEND-1's new center is the correct governing target.)

## Non-blocking adjudications

- **ADJ-1 — V-9 amended target governs; Devbot probe still encodes the original 12 m / (0,-702).** Devbot's `solve_geometry.py` hard-codes the ORIGINAL V-9 (line 164: `center_north = (0,-702)`; line 173: `floor(..., 12.0)`), and it FAILs by design (0.8515 m). This is the expected, disclosed outcome — the frozen prop layout cannot yield 12 m at (0,-702) because the spec-mandated root `okRuinColumn` sits at (0,-700). Per AMEND-1, the governing criterion is **clear circle ≥ 6.0 m at (0,-709)**, which passes at 6.68 m (my math) / ~7.1 m (Devbot). Devbot's probe FAIL is therefore *non-blocking*; it does not signal a build defect. Future hygiene: the probe could be updated to assert the amended target so CI-style reruns go green.
- **ADJ-2 — V-9 measurement delta at the amended center (6.68 vs 7.1 m).** Devbot's "~7.1 m" vs my 6.68 m differ by ~0.4 m, likely from a differing collider model detail at the binding mourningStatue (rotY/orientation handling). Both clear the 6.0 m bar with margin; flagged as a non-blocking modeling disclosure, not a pass/fail factor.

## BV-0 / pre-build evidence (report-only)

Build already landed before validation dispatch. Recorded: HEAD = `42ba377` (unmodified, insertion-only diff); pre-build greps show exactly 1 `regionJ: {` key; no regionJ/veil_spire_approach references in `game.js` / `region-manager.js` / `save.js` / `daynight.js`; only CONFIG.js + region-defs.js carry production changes. Consistent with CC-H2b state at `42ba377`.

## Method note

All verdicts rest on my own fresh greps and an independently-written Node clearance model (`scratch/cc-h3/validator/`), with engine helpers (`sideOfPlane`/`planeIn`/`sideIn`/`connectionBetween`) evaluated live from `region-defs.js`. Devbot's `solve_geometry.py` was executed once *as data* to harvest its 231-check matrix and cross-compare seat arithmetic; its single FAIL is the superseded V-9 original target and is adjudicated non-blocking (ADJ-1). No harness run, no headless browser, no bundle build, no commit/push — report-only per task law.

**Action:** Validation complete. IO may commit & push.
