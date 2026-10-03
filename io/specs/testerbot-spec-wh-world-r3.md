# TESTERBOT SPEC — Witch Hunter World R3: Internal-Res Pixelation Validation (gate step 2)

Author: Testerbot (independent validator-author). Date: 2026-10-02.
Devbot spec of record: io/specs/devbot-spec-wh-world-r3.md (read-only; mismatches are
amendment notes below, never patched in the spec by me). Spec commit 35644fd; CODE base
= 0406e64 (R2 marker; `git diff 0406e64 HEAD -- prototype tests` is empty at e6efd7e, so
all R3 diffs are measured against 0406e64). Authority for ACs: devbot spec :55-98 (AC-P1..P6
+ retune). Upstream (devbot spec only): doc 61 P0-4 (:301-310), M-08 (:570). HANDOFF.md
harness laws 1-8 + floor waiver classes are inherited verbatim.

## Harness + invocation contract
- File: tests/wh_world_r3_validation.py = build artifact `cat tests/r3parts/part01..10.py`
  (law 8: edit parts, re-cat, grep for shadowed duplicate defs before every run).
  Playwright sync, headless chromium `--enable-unsafe-swiftshader`, context viewport
  1920x1080, device_scale_factor=1 (explicit; P1 runs a separate dpr-2 context).
- Env: `WH_BASE_ROOT` (reuse candidate), `WH_W3_PORT` (default 0 = ephemeral self-spawn),
  `WH_SMOKE=1` (P2 reps 1 instead of 3, P3/P4 subprocesses still run), `WH_W3_FLOOR=0`
  (skip P3+P4 subprocesses, recorded as SKIP-NOTED, never silent), `WH_W3_DIVS`
  (default `1,2,4`). R1/R2 subprocesses get `WH_BASE_ROOT=<our root>` + `WH_R2_FLOOR=0`.
- Server identity (law 5 + R3 signature): reuse WH_BASE_ROOT only if served
  `js/CONFIG.js` contains `lightPool` AND `ambientIntensity: 0` AND `internalResDiv`
  AND its bytes equal the worktree's prototype/js/CONFIG.js (amendment A1). Else
  self-spawn prototype/server.py from REPO_ROOT on an ephemeral port (bind 127.0.0.1:0,
  close, spawn, poll); kill on exit. Never touch port 8791 (landed-work server).
- Laws: forced render + toDataURL in ONE evaluate; camera-settle wait (vz<1 retry) before
  screen probes; NaN guards on enemy pos; per-AC try/except -> recorded FAIL; exit 0
  ALWAYS; final stdout line = one JSON verdict; no key-shaped literals in parts.
- Sanctioned writes (measurement-only, renderer config, not gameplay state):
  `WH_CONFIG.renderer.internalResDiv = d; window.dispatchEvent(new Event('resize'))`
  for the P2 div sweep, ALWAYS restored to the dispatch value and re-verified (buffer
  back to 960x540) before any later AC; page.set_viewport_size for the P1 resize probe.
  Existing R2 sanctioned hooks (teleportPlayer etc.) unchanged.

## Pre-Devbot smoke — EXPECTED (current tree = R2 tip; captured run is authoritative)
| AC | Expected pre-Devbot | Evidence to capture |
|----|---------------------|---------------------|
| BOOT | PASS; reuse refused (no internalResDiv) -> self-spawn | identity check result, port |
| P1 | FAIL: buffer 1920x1080 (dpr1 x maxPixelRatio), imageRendering 'auto', aligned-pair ratio ~= misaligned | dims, computed style, pair metrics |
| P2 | FAIL: div writes are no-ops -> all rows same dims, eliminated 0 vs expected 0.75; triangles equal | full-res frame-time = baseline RECORD |
| P3 | PASS via inherited waivers (as at 0406e64); A8 waiver adds this untracked valspec | R1 JSON line |
| P4 | PASS; SCOPE flags this untracked valspec -> R3-artifact waived; L10 = full-res baseline | R2 JSON line, L10 rows |
| P5 | PASS (dirty set = this valspec only) | porcelain set |
| P6 | FAIL (key absent) | CONFIG.renderer dump |

## AC-P1 — Pixel-locked upscale
- (a) Buffer: one evaluate: force render, return {cw:canvas.width, ch:canvas.height,
  dw:clientWidth, dh:clientHeight, ir:getComputedStyle(canvas).imageRendering,
  url:toDataURL}; decode PNG. PASS: cw,ch == decoded == 960x540 exactly; dw,dh ==
  1920x1080; ir in {'pixelated','crisp-edges'}; renderer.getPixelRatio() === 1.
- (b) Block structure (amendment A2): toDataURL returns the LOW-RES buffer, which has no
  2x2 blocks; blocks exist only in the composited display. Capture page.screenshot
  (full 1920x1080, png) after settle, decode (PIL ok). Region = R1/R2-validated ground
  band rows [0.72h,0.95h] x cols [0.30w,0.70w] (textured; sky is flat and proves
  nothing). Pixel equal = max channel |diff| <= 2.
  - aligned_h = P(px(2i,y)==px(2i+1,y)), aligned_v = P(px(x,2j)==px(x,2j+1)) over the
    band; bar BOTH >= 0.90 (IO bar).
  - misaligned control: P(px(2i+1,y)==px(2i+2,y)); bar aligned_h - misaligned >= 0.15
    (proves block grid, not flat colour; a bilinear upscale fails this).
  - run-length: horizontal runs of identical colour over 20 sampled rows; bar >= 0.90 of
    runs have even length AND modal run length >= 2. Block phase offset (0 or 1) is
    auto-detected once and reused for all metrics.
- (c) Resize path: set_viewport_size(1280,720) -> settle 2 frames -> buffer 640x360;
  restore 1920x1080 -> 960x540. (d) DPR law: second context dsf=2 at 1920x1080 ->
  buffer still 960x540 (setPixelRatio(1)). (c)+(d) PASS/FAIL (spec design 2-3).
- Evidence: all dims, ir, aligned_h/v, misaligned, run histogram top-5, phase.
- Verdict: PASS iff a+b+c+d. Numeric miss on (b) = FAIL-RETUNE-PENDING (spec :94-98).

## AC-P2 — Fragment cost drop (SwiftShader translation of M-08)
- One evaluate per rep, divs from WH_W3_DIVS in interleaved order (1,2,4)x3 reps: set
  div + dispatch resize; 3 warm renders; 20 timed renders each followed by a 1-px
  gl.readPixels sync (amendment A3: without a sync SwiftShader timing measures command
  submission only); record mean ms, canvas w/h, renderer.info.render.triangles + calls
  read directly after the last render (info.autoReset per frame). Camera fixed: no
  input during the evaluate; pose = A spawn after settle. Restore div 2, verify 960x540.
- Bars: (a) triangles IDENTICAL (exact int) across all div rows of the same rep, and
  equal to the smoke-captured pre-implementation count at the same pose (pre value
  RECORD; mismatch vs pre = FAIL only if > 0 diff persists across reps); (b) eliminated
  = 1 - (w_d*h_d)/(w_1*h_1) within ±0.01 of 1-1/d^2 (d=2: 0.75, d=4: 0.9375);
  (c) median-over-reps ms(div2) <= median ms(div1). RECORD table: div, w x h, px,
  eliminated, ms per rep, median, ratio vs div1, triangles, calls.
- Verdict: PASS iff a+b+c with the table captured; (c) miss = FAIL-RETUNE-PENDING.
  The hardware p99 <= 16.6 ms bar is GPU-only (M-08) -> RECORD "ENV-LIMIT GPU".

## AC-P3 — R1 floor re-proof (subprocess)
- `python3 tests/wh_world_r1_validation.py` with WH_BASE_ROOT shared, unchanged file,
  parse final JSON. R1's own protocol: A1-A4,A6,A7,A8 PASS, A5 RECORD. R1 viewport is
  960x600 -> buffer 480x300 at div 2; its readbacks are fraction-sampled.
- Inherited waiver classes, each re-verified in-run exactly as R2 part10 ac_floor:
  A2-dev-baseline, A3-settle-subprobe, A4-nightrig-chain, A6/A7-hash-drift, A8-surface-FP.
- Pre-declared R3-artifact waivers (amendment A4): A7 prototype/style.css sha mismatch
  vs R1 FREEZE (R3 is REQUIRED to edit it) — waived only if index.html sha still ==
  R1 FREEZE value AND the style.css diff is exactly the P5 hunk; A8 residual paths all
  inside the P5 R3 surface.
- Any other new fail: R3-artifact only if its detail cites buffer-size-dependent
  sampling AND its numbers sit in an inherited class band; else STOP (spec :77).
  Record, never edit R1. Evidence: R1 JSON line, fails, classes applied.

## AC-P4 — R2 floor re-proof (subprocess)
- `python3 tests/wh_world_r2_validation.py` with WH_BASE_ROOT shared + `WH_R2_FLOOR=0`
  (amendment A5: the spec's WH_HARNESS_R2_FLOOR does not exist; R2 reads WH_R2_FLOOR,
  wh_world_r2_validation.py:33 — the spec's name would nest R1 again). R2 identity check
  passes on the R3 tree (signature unchanged). Verdict per R2's own protocol.
- L10 pre-declaration STANDS: R2 L10 maps projected coords into buffer px (:1078-1079)
  then uses a fixed ±10 box + r120-180 annulus in BUFFER px (:1080-1081) = 2x footprint
  on screen at div 2. If L10 alone drifts: record all rows (d, t, b, c) + WAIVED
  R3-artifact; R3 also RECORDs a scaled re-measure (box ±5, annulus r60-90 at div 2,
  same projection, same forced frame) as judgment evidence, not a gate.
- R2 SCOPE residual consisting only of P5 R3-surface paths (+ prototype/style.css) =
  R3-artifact waived (amendment A6: SCOPE is not an "L"; spec silent). Any other L or
  SCOPE drift = normal R2 verdict logic. Evidence: R2 JSON line, per_ac, waivers.

## AC-P5 — Preservation surface (git set-diff at validation time, vs 0406e64)
- Allowed dirty/committed-since-base set EXACTLY: prototype/js/game.js,
  prototype/js/CONFIG.js, prototype/style.css, io/specs/*-r3*, io/reports/*r3*,
  tests/wh_world_r3_validation.py, tests/r3parts, tests/r3parts/*. Porcelain parsing
  with the R1 A8 leading-3-char strip. Residual non-empty = FAIL (4th prototype file =
  BLOCK).
- Hunk law: game.js hunks only inside setupRenderer (anchor :32-40), the resize handler
  (:941-946), and ONE internalSize helper adjacent to either (spec design 3, amendment
  A7); CONFIG.js hunks only inside renderer {} (:7-14), with outputColorSpaceSRGB,
  toneMappingName 'Neutral', toneMappingExposure 1.15, maxPixelRatio 2,
  shadowMapEnabled false unchanged; style.css diff = exactly +2 lines inside
  #wh-canvas (`pixelated` then `crisp-edges`, that order). Any other hunk = FAIL.
- index.html sha256 == worktree 0406e64 (9ad39b809bc4...) AND == 0406e64's
  blob. IO AMENDMENT A10 (2026-10-02, granted on Devbot's smoke evidence):
  the valspec's R1-FREEZE index.html sha pin (cec75217eb37...) is STALE --
  pre-dates anim/combat rounds; the file at 0406e64 is already the pinned
  content (diff empty, sha 9ad39b809bc4...). New bar: index.html byte-
  identity vs CODE BASE 0406e64 (full stop). The A4 style.css waiver reads
  "index.html identical to 0406e64 AND the exact P5 hunk" in place of the
  frozen-sha read. v7 rebuild clean (amendment
  A8): run tools/build_v7.py against a temp copy of prototype/+tools/, load result,
  0 console/page errors; prototype/builds/ must NOT appear in the dirty set.
- Secrets: `git diff 0406e64` grep msy_[A-Za-z0-9]{8} + key/token/secret/password
  assignment patterns = 0 hits; player-facing "free" over the 3 prototype diffs = 0.
- Untouched-surface spot checks: region-manager.js, player.js, hud files absent from diff.

## AC-P6 — CONFIG record
- evaluate WH_CONFIG.renderer: internalResDiv === 2 (integer) and maxPixelRatio
  still present; source text of the renderer block (worktree CONFIG.js) contains a
  comment matching /supersed/i on/adjacent to the maxPixelRatio line.
- Verdict (amendment A9): key presence + value = PASS/FAIL (P1/P2 depend on it);
  comment = RECORD (quoted line as evidence). After a sanctioned retune the bar
  becomes the retuned value (2 -> 3 or 1) with justification recorded.

## Flake rule (same as R1/R2)
- Retries up to 2 (fresh reload) for infra-shaped failures only: runner exception,
  timeout, server 500, WH_DEBUG not ready, SwiftShader degenerate frame (all-zero),
  screenshot blank. Deterministic number misses (dims, pair ratios, triangles, timing
  medians, subprocess verdicts) are NEVER retried. Verdict per AC = LAST attempt;
  >= 3 flakes in the run = BLOCK ("harness unstable, do not gate on this run").

## Verdict protocol
`{"round":"world-r3","verdict":"PASS|FAIL|BLOCK|FAIL-RETUNE-PENDING","div":2,
 "per_ac":[{"id":"P1","verdict":"...","evidence":"..."}],
 "floor":{"r1":{...,"waivers":[]},"r2":{...,"waivers":[]}},"p2_table":[...],
 "flakes":0,"notes":"..."}` — exit 0 ALWAYS.
- PASS iff P1, P2, P5, P6 PASS and P3, P4 PASS (waivers only from enumerated classes).
- First numeric miss on P1(b)/P2(c) with correct plumbing = FAIL-RETUNE-PENDING (one
  retune); SECOND identical miss = STOP. Independent BLOCKs: scope violation, secrets
  hit, index.html drift, non-artifact R1/R2 floor fail, >= 3 flakes.

## Amendment notes (spec-of-record vs live tree e6efd7e; I own the bars)
A1. Identity: signature grep alone can pass a stale server carrying the same strings;
    added byte-equality of served CONFIG.js vs worktree. Pre-impl, reuse is refused
    (no internalResDiv) and self-spawn from the worktree is trusted by construction.
A2. P1 "2x2 blocks" cannot exist in a toDataURL readback (it IS the 960x540 buffer);
    block metrics run on page.screenshot (composited display). Region moved from
    road/sky to the textured ground band + misaligned control; flat sky passes any
    upscale. Bars 0.90 kept; control (>= 0.15 gap) and even-run (>= 0.90) are mine.
A3. P2 timing adds a 1-px readPixels sync per render and 3 interleaved reps with
    medians; "pre/post triangles" = div sweep within one pose + smoke pre-count.
A4. R1 A7 FREEZE pins prototype/style.css sha (r1:45) — R3 must change it; pre-declared
    R3-artifact waiver, gated on index.html still matching and the exact P5 hunk.
A5. WH_HARNESS_R2_FLOOR -> WH_R2_FLOOR (r2:33). Using the spec's name = R1 runs twice.
A6. R2 SCOPE (r2:1113 allowlist lacks style.css/r3 paths) will fail on R3 surface;
    waived only when residual is wholly inside the P5 surface.
A7. Spec design 3 mandates an internalSize() helper, which P5's "setupRenderer +
    resize hunks only" would forbid; one adjacent helper hunk allowed.
A8. "v7 build rebuild clean" would dirty prototype/builds/ (outside P5's surface);
    rebuild runs on a temp copy, builds/ must stay clean.
A9. P6 "(record)" hardened: key presence/value gates; comment stays RECORD.
A10 (IO ruling 2026-10-02): P5's index.html bar changed from the stale R1
    FREEZE sha to byte-identity vs CODE BASE 0406e64 (sha 9ad39b809bc4...).
    Evidence: diff 0406e64..HEAD index.html = empty; the frozen pin
    pre-dated the anim/combat rounds. A4's waiver gate reads the same new
    bar. P1(b) control-gap bar REPLACED per IO ruling 2: primary bar =
    edge_on_grid >= 0.80 (Devbot's record-only field, grid-adjacency of
    colour edges; scene-flat misaligned control is unreliable here);
    aligned bars unchanged. No retune of div occurred or was needed.
