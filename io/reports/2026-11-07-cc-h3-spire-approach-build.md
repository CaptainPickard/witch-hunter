# CC-H3 Spire Approach — Devbot build note (2026-11-07)

Source-only handoff. CONFIG regionJ sec 3+4 copied byte-for-byte; conn[8] mirrors conn[7]. `node --check` passes for both JS files. `python3 scratch/cc-h3/solve_geometry.py` runs 231 live-CONFIG/region-defs checks: **230 PASS, 1 FAIL**. No bundle build, harness, browser, commit, or push.

| Item | Self-check |
|---|---|
| V-0 | PASS — syntax; single regionJ id; complete exact top-level key set and values. |
| V-1 | PASS — evaluated conn[8] F→J, one-sided J plane, F interact, exact lands/prompt/fades, bidirectional lookup. |
| V-2 | PASS — F=-1, J=+1; J `sideIn=sideOfPlane=+1`; F plane inactive. |
| V-3 | PASS — 10 ring rows/90 colliders, lane edge 1.5500 m, zero lane-window overlap; ghoul spacing 30 m; F hook nearest prop 4.2720 m; F land nearest prop 7.2801 m, ring edge 9.7313 m. All 230 other probe assertions passed. |
| V-4 | PASS — regionF byte-identical to `42ba377`. |
| V-5 | PASS — fresh seed 1662061763, groundY 0, scatter false, gravityY -22. |
| V-6 | PASS — one lanternPost, two blightcap, 12 other non-ring props; 15 non-ring props total. |
| V-7 | PASS — regionI and conn[0..7] byte-identical to `42ba377`. |
| V-8 | PASS — only CONFIG.js and region-defs.js production changes; this probe and report are the only new deliverables. No named no-touch file diff. |
| V-9 | **FAIL — spec conflict requiring IO adjudication.** At required center `(0,-702)`, largest collider-edge clear circle is **0.8515 m**, bound by the mandated root `okRuinColumn` at `(0,-700)` (measured width 0.957085 m × scale 2.40 / 2 = 1.1485 m collider radius). Requirement is ≥12 m. The frozen prop layout cannot satisfy it; moving the monolith or changing the V-9 center would violate the verbatim-row law. Ring diameter itself passes at 80 m. |

Footprints in probe: measured GLB X widths are disclosed in its output; walls use lineage 1.899 m local X and live `boundaryWall.collider.r=0.45`. F-side ring-edge numbers are collider-edge rather than raw center distance. **Do not treat this as a PASS verdict until IO resolves V-9.**

## IO post-verdict ruling (wake 21)

AMEND-1 applied to the frozen spec (V-9 re-ruled: >= 6.0 m at (0,-709); the
original 12 m @(0,-702) placed the circle inside the root column's own
collider — spec-author error). Devbot's probe scratch/cc-h3/solve_geometry.py
re-aligned to the adjudicated law by IO (kept CONFIG-parsed; comment carries
the ruling). Full re-run: 231/231 checks PASS, V-9 clear radius 6.6848 m —
convergent with Testerbot's independent model (6.6848 m, verdict PASS
against the amended spec).
