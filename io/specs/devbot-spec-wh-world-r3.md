# DEVBOT SPEC — Witch Hunter World R3: internal-resolution pixelation (P0-4)

Branch: feat/world-visuals (stacked after R2). Base: the validated R2 marker
commit 0406e64. Authority: docs/planning/61-world-audit.md
item P0-4 (lines 301-310) + M-08 (line 570) + P1-9 ordering gate (P0-4 must
land before P1-9). Dispatch law: IO spec -> Testerbot valspec -> Devbot ->
Testerbot validates -> IO commits/pushes. Worktree: /tmp/wh-worldfeat
(recreate from feat/world-visuals if /tmp wiped; branch refs survive).

## Problem (audit, verbatim anchor)
"The render pipeline renders full-res then CSS-scales; only the prop-texture
half of the retro look is implemented. Low internal res is the other half;
audit sizes fragment-cost at 4-10x on SwiftShader."

## Live-tree anchors (verified 2026-10-02 against feat/world-visuals R2 tip)
- prototype/js/game.js:32-40  setupRenderer: THREE.WebGLRenderer({canvas,
  antialias:false}); setPixelRatio(min(dpr, CFG.renderer.maxPixelRatio));
  setSize(window.innerWidth, window.innerHeight)  <- THE resize surface.
- prototype/js/game.js:941-946  window resize handler: aspect update +
  renderer.setSize(window.innerWidth, window.innerHeight).
- prototype/js/CONFIG.js:7-14  renderer block: outputColorSpaceSRGB,
  toneMappingName 'Neutral', toneMappingExposure 1.15, maxPixelRatio 2,
  shadowMapEnabled false.
- prototype/style.css:18-22  #wh-canvas { display:block; width:100%;
  height:100%; }  <- CSS drives DISPLAY size; canvas ATTR size is what
  three.js setSize writes.
- prototype/index.html:11  <canvas id="wh-canvas"></canvas>  (NOT in scope:
  setSize(..., false) keeps the CSS sizing; index.html must stay
  byte-identical).

## Design (audit-ordered, exact numbers pinned)
1. CONFIG.renderer.internalResDiv = 2  (new key; internal 960x540 at the
   1920x1080 validation viewport = the audit's 540 internalHeight at 16:9;
   audit P1-9's render-target pass lands LATER, out of R3 scope).
2. setupRenderer: replace the pixel-ratio+size pair with the internal-pixel
   law: setPixelRatio(1); w = round(window.innerWidth / internalResDiv);
   h = round(window.innerHeight / internalResDiv);
   setSize(w, h, false)  (updateStyle=false: style.css keeps driving the
   displayed size = pixel-locked upscale; buffer is the low-res one).
   DPR law: internal pixelation REQUIRES dpr 1 (a dpr-2 canvas would render
   1920x1080 physical px again); maxPixelRatio stays in CONFIG as a
   preserved legacy key (documented superseded) - do not delete it.
3. resize handler: same internal-pixel law (reuse one internalSize() helper
   so boot and resize share the single formula).
4. prototype/style.css #wh-canvas: add
     image-rendering: pixelated;
     image-rendering: crisp-edges;   (fallback line, AFTER pixelated)
   This + the index.html-freeze = the only style.css delta of the round.
5. Do NOT touch: tone mapping/exposure/lighting keys (R2 owns), L10 probe,
   region-manager.js, HUD DOM/HUD scale (DOM HUD is above the canvas and
   unaffected), reticle math (game.js:372-373 uses window px - unaffected).
6. NO dither/grain/post pass (P1-9 owns that; audit's dither/grain wording
   is texture/post-side, later round).

## ACs ( Testerbot-independent validation, each with evidence)
- AC-P1 pixel-locked upscale (canvas readback): forced render + toDataURL
  in ONE page.evaluate (no-preserveDrawingBuffer law). At div=2 with a
  1920x1080 viewport, decoded buffer must be 960x540 AND its pixels
  structured as 2x2 uniform blocks: sample columns of adjacent-pixel
  equality runs - for sampled rows, P(row x, row x+1 identical) high
  (>=0.9 of paired pixels in the road/sky region), and distinct-color
  horizontal run lengths quantized around the 2px block. Evidence: buffer
  dims + block-structure metrics.
- AC-P2 fragment cost drop (M-08 translated to SwiftShader, hardware bar is
  a RECORD): (a) renderer.info.render.triangles IDENTICAL pre/post (same
  geometry, only fill resolution changed); (b) forced-render wall-clock
  per frame (mean of ~20 forced renders in one evaluate loop, warmed) at
  div=1 vs div=2 vs div=4, RECORD table; (c) internal pixel count math:
  (1 - 1/div^2) fraction of fragments eliminated (div=2: 75% fewer).
  PASS = triangles identical AND pixel math reported AND div=2 measured
  faster-or-equal with the RECORD table captured. (Retune knob = div.)
- AC-P3 R1 floor re-proof: tests/wh_world_r1_validation.py as subprocess on
  the shared server (pattern: part10 ac_floor). Its canvas-readback ACs
  fraction-sample, so they absorb the buffer change; IF it fails with a
  fail set citing ONLY R3-round artifacts (buffer-size sampling constants),
  apply the FLOOR-WAIVER treatment (record, don't edit R1's file) - same
  structure as R2's floor of R1. A NEW non-artifact failure = STOP.
- AC-P4 R2 floor re-proof (same subprocess pattern on
  tests/wh_world_r2_validation.py with WH_HARNESS_R2_FLOOR=0 to avoid
  nesting R1 twice; L10's fixed-px annulus 120-180 becomes visually 2x
  under div=2 - declared pre-dispatch as a sanctioned R3-artifact drift:
  if L10 alone drifts, record its numbers + treat as WAIVED R3 artifact;
  any other L-drift = normal verdict logic).
- AC-P5 preservation: git set-diff at validation time shows dirty surface
  EXACTLY within: prototype/js/game.js (setupRenderer + resize hunks only),
  prototype/js/CONFIG.js (renderer block only), prototype/style.css (#wh-
  canvas rule only), io/specs/*-r3*, io/reports/*r3*,
  tests/wh_world_r3_validation.py, tests/r3parts*, tests/r3parts/* .
  index.html byte-identical; v7 build rebuild clean; combat/anim hunks in
  shared files byte-identical (surgical-commit law); secrets grep clean.
- AC-P6 (record): CONFIG.renderer.internalResDiv exists, = 2 at dispatch;
  the CONFIG comment documents the maxPixelRatio supersession.

## Retune protocol
Exactly-once: if AC-P1 block structure or AC-P2 fails numerically, ONE
retune of internalResDiv (2 -> 3 or 2 -> 1 with justification) is allowed,
evidence recorded; a SECOND identical numeric failure = STOP + surface
(same rule as R2 L10).

## Harness laws (inherit R2 verbatim)
SwiftShader wall-vs-game-time, same-evaluate render+readback, forced renders
for temporal sampling, camera settle waits, NaN guards, server identity
check (lightPool + ambientIntensity 0 signature, ephemeral port self-spawn),
per-AC try/except, exit 0, final line one JSON verdict. Assembly: parts
part01-part10 <=130 lines each? NO - R2's real parts exceed it; law =
part files <=130 lines for NEW files where practical, assembly pattern
identical (cat into tests/wh_world_r3_validation.py, it is a build
artifact). IO-authored banner under Nicko's 09-25 lane ruling + 'Testerbot
authored valspec of record + revalidates harness on lane recovery'.

## Deliverables
- Prototype changes per Design; harness tests/wh_world_r3_validation.py +
  tests/r3parts/part01-10.py; implementation report draft noted in commit
  message; NO spec/valspec edits by Devbot (mismatch -> comment in report,
  IO amends).