# World R3 — internal-res pixelation (P0-4) — implementation report (DRAFT)

Gate step 3 (Devbot). Spec of record: io/specs/devbot-spec-wh-world-r3.md
(35644fd). Valspec of record: io/specs/testerbot-spec-wh-world-r3.md
(d8eb538; amendments A1-A9 applied as binding). Code base 0406e64.
carrier-req: Testerbot revalidates the harness on lane recovery.
Nothing committed or pushed by Devbot (IO owns step 5).

## Prototype diff (3 files, +21 / -3)
- prototype/js/CONFIG.js (renderer block only): `internalResDiv: 2` added
  after `maxPixelRatio: 2`; a comment line directly above maxPixelRatio says
  it is superseded by internalResDiv (setPixelRatio(1)) and kept as a legacy
  key. maxPixelRatio, outputColorSpaceSRGB, toneMappingName,
  toneMappingExposure and shadowMapEnabled lines are byte-unchanged.
- prototype/js/game.js:
  - new `internalSize()` helper directly above setupRenderer:
    `{w: max(1, round(innerWidth/div)), h: max(1, round(innerHeight/div))}`
    with `div = CFG.renderer.internalResDiv || 1`. CFG is the live
    `window.WH_CONFIG`, so the P2 sanctioned div write followed by a resize
    event takes effect.
  - setupRenderer: `setPixelRatio(1)` + `setSize(isz.w, isz.h, false)`
    replaces the min(dpr, maxPixelRatio) pair.
  - resize handler: the same helper + `setSize(isz.w, isz.h, false)`
    (aspect/projection lines unchanged).
- prototype/style.css `#wh-canvas`: `image-rendering: pixelated;` then
  `image-rendering: crisp-edges;` (exactly +2 lines, in that order).
- index.html, player.js, region-manager.js, HUD, lighting/tonemap keys,
  combat/anim files: untouched.

## Harness
- tests/r3parts/part01..10.py = source. tests/wh_world_r3_validation.py =
  build artifact, byte-identical to
  `cat tests/r3parts/part01.py ... part10.py` (final sha256 9389b24f...e455,
  checked against the cat pipe). py_compile OK; no duplicate defs.
  Assembly: `sh tests/r3parts/build.sh` or `python3 tests/r3parts/build.py`
  (both: cat + py_compile + duplicate-def check).
- Plumbing taken from tests/r2parts part01/02 (identity-checked reuse,
  ephemeral self-spawn, never port 8791, READY poll) and part10 (floor
  subprocess plus waiver re-verification).

### Per-AC notes
- P1 (a) one evaluate: force render, then canvas w/h, client w/h, computed
  imageRendering, getPixelRatio, toDataURL (decoded with PIL).
  (b) A2: block metrics run on `page.screenshot` over the ground band
  [0.72h,0.95h]x[0.30w,0.70w]. Equality = max channel diff <= 2. Phase is
  auto-detected once from the horizontal aligned-minus-misaligned gap and
  reused. Bars: aligned_h/v >= 0.90, gap >= 0.15, even runs >= 0.90,
  modal run >= 2. The screenshot is saved to /tmp/whr3_p1_shot.png as
  evidence. (c) viewport 1280x720 -> 640x360, then back to 960x540.
  (d) a dsf=2 context still gives a 960x540 buffer with pr 1 and dpr 2.
  A (b)-only miss = FAIL-RETUNE-PENDING.
- P2: one evaluate per rep. Divs from WH_W3_DIVS go through set +
  resize, then 3 warm renders and 20 timed renders, each followed by a
  1-px readPixels sync (A3). Each rep records ms, w/h, triangles and calls.
  Div is restored and the buffer is re-verified at 960x540. The
  pre-implementation triangle count is measured live on a `git archive
  0406e64 prototype` copy at the same pose (or WH_W3_PRE_TRIS). The table
  is in the verdict JSON as `p2_table`. A (c)-only miss =
  FAIL-RETUNE-PENDING. The hardware bar is recorded as ENV-LIMIT GPU.
- P3: the R1 harness runs unchanged with WH_BASE_ROOT + WH_R1_PORT on the
  shared server. Waivers A2/A3/A6/A8 are re-verified as in R2 part10. The
  A3 subprobe text is read verbatim from the R2 harness at run time. A7
  uses the A4 amendment (index freeze-ok + exact style hunk).
- P4: the R2 harness runs with WH_R2_FLOOR=0 (A5) and also WH_R2_PORT =
  our port (see deviations). L10-alone drift is waived as the
  pre-declared R3 artifact, with the scaled re-measure (box +-5, annulus
  r60-90, buffer px) recorded. A SCOPE residual wholly inside the P5
  surface is waived (A6). Any other fail = BLOCK.
- P5: porcelain (`--untracked-files=all`, 3-char strip) plus committed
  paths since 0406e64 under prototype/ and tests/ must sit inside the P5
  surface. Hunk windows: game.js old lines 29-41 / 940-947; CONFIG.js 7-14
  with protected lines intact; style.css exactly the 2 added lines inside
  #wh-canvas. index.html sha must equal the R1 FREEZE pin. v7 rebuild runs
  on a temp copy (A8) and is served and loaded with 0 console/page
  errors; prototype/builds must stay clean. Secrets: msy_ pattern plus the
  R2 real-assignment regex over `git diff 0406e64` and the untracked file
  contents. There is also a "free" check over added prototype lines.
- P6: the key must be an integer equal to 2 and maxPixelRatio must be
  present (gating, A9). The /supersed/i comment within ±1 line of
  maxPixelRatio is quoted as RECORD.

## Deviations / notes for IO
1. P5 committed-since-base set: `git diff 0406e64 HEAD` includes IO's own
   gate-doc commits (HANDOFF.md, R4-R6 drafts, R4 bake tool, lane log).
   These are outside the literal P5 list and would FAIL P5 by
   construction. The harness checks committed paths under prototype/ and
   tests/ only (as the valspec header does) and records the gate-doc count.
   IO to confirm or amend.
2. P4 also passes WH_R2_PORT. The R2 identity probe checks
   localhost:$WH_R2_PORT (default 8792), not WH_BASE_ROOT's port. Without
   it, R2 would refuse our server and self-spawn a second one. The result
   is still correct, just a different server instance. R1 likewise gets
   WH_R1_PORT.
3. P3 A4-nightrig re-verify: R3 has no in-suite L4/L10. The chain is read
   from THIS run's R2 floor instead: L4 PASS, plus L10 PASS or the scaled
   re-measure c10 >= 0.25. So P4 runs before P3.
4. Verdict `PASS-FLOOR-SKIPPED` (not in the valspec enum) is emitted only
   when WH_W3_FLOOR=0 and all core ACs pass. It is never a gate PASS.
5. Unexplained R1/R2 floor fails are emitted as BLOCK ("manual
   adjudication per spec :77"). The "buffer-size sampling artifact"
   judgment is not automated.

## Smoke run (Devbot-captured)
`WH_SMOKE=1 WH_W3_FLOOR=0 python3 tests/wh_world_r3_validation.py`
-> /tmp/whr3_smoke_devbot.log. Self-spawned on ephemeral port 45097,
flakes=0, exit 0. Verdict: **BLOCK**. Per AC:
- BOOT PASS. P6 PASS (comment quoted).
- P2 PASS. Triangles 120704 at every div, identical to the live pre-impl
  count on the 0406e64 archive. Eliminated fraction 0.75 / 0.9375 exactly.
  ms per forced+synced render: div1 572.7, div2 200.9 (0.351x), div4
  103.3 (0.18x). Smoke = 1 rep.
- P1 FAIL-RETUNE-PENDING. (a), (c) and (d) all PASS: buffer 960x540,
  display 1920x1080, ir = crisp-edges (Chromium honours the fallback
  line), pr 1, 720p -> 640x360 and back, dsf2 still 960x540. (b) misses
  ONLY the control-gap bar: aligned_h 0.9986, aligned_v 0.9926, even
  runs 0.961, modal run 8, BUT misaligned 0.905 -> gap 0.094 < 0.15.
- P5 BLOCK, solely on index.html sha != R1 FREEZE pin. Everything else
  in P5 is green: resid=[], hunks in their windows, exact css hunk, v7
  temp rebuild clean, builds/ clean, 0 secrets, 0 "free".
- P3/P4 SKIP-NOTED (WH_W3_FLOOR=0 as instructed). The full floor run is
  NOT yet done.

### Two valspec-bar findings for IO/Testerbot (Devbot does not amend)
F1. **index.html pin is stale, not drifted by R3.** prototype/index.html
    is byte-identical to 0406e64 (sha 9ad39b80...dc32; `git diff 0406e64
    -- prototype/index.html` is empty). The R1 FREEZE pin cec75217... was
    superseded by combat/anim commits 02ca0ac / dc697ce. This is the same
    root cause as R2's inherited A6/A7 HASH-DRIFT class. Proposed
    amendment: bar = "index.html byte-identical to BASE 0406e64" (now
    RECORDed in the P5 evidence as identToBase). This also affects the P3
    A7 waiver gate (A4 amendment), which keys on the same pin.
F2. **P1(b) control gap 0.15 is miscalibrated for this content.** The
    ground band at A spawn is mostly near-black, flat-shaded ground, and
    the prop textures are themselves NEAREST-pixelated (texels > 2 buffer
    px; modal run 8px). So even off-grid neighbours match 90% of the
    time. The grid itself is unambiguous: only 0.14% of on-grid pairs
    differ vs 9.5% off-grid. Put another way, 98.5% of colour edges fall
    on the 2px block grid (bilinear/no-grid would be ~50%). The harness
    now RECORDs this as `edge_on_grid` (added after the smoke run, not a
    bar). Visual check of /tmp/whr3_p1_shot.png confirms 2x2 blocks in
    the lantern pool. Proposed amendment: replace the gap bar with
    edge_on_grid >= 0.80, or a relative gap (1-mis)/(1-aligned) >= 5.
    **No internalResDiv retune applied**: div 3 would break the
    even-run metric by construction, and div 1 removes the feature. The
    miss is a bar-calibration issue, not a pixelation shortfall, so
    spending the exactly-once retune would be unjustified.

Post-smoke harness edits (both RECORD-only, no bar changed): P1
edge_on_grid field; P5 identToBase evidence. The artifact was re-verified
byte-identical to the cat of the parts (sha256 9389b24f...e455) and
py_compiles clean.
