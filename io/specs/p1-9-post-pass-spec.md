# P1-9 — Retro Post Pass (doc 61: tone map, sRGB, per-region lift/gamma/gain, 4×4 Bayer ordered dither, animated grain, vignette)

IO spec, wake 41 (2026-11-08). Worktree /tmp/wh-worldfeat, branch feat/world-visuals.
Build tool: tools/build_v8.py from repo root (do NOT create build_v9).
Art anchor (IO viewed + analyzed this wake): art-direction/concepts/concept-01-darkwood.png
(cold blue-black dominant palette, ONLY warm accent = lantern amber; "shadows crushed";
fine organic film-grain across the whole frame, not structured checkerboard dither;
strong vignette) + day-08-veil-spire.png (moderate grain, subtle stipple at fog edges,
moderate vignette, achromatic-midtone grade with crushed blacks).

## Acceptance metric (doc 61): M-21 look QA + the M-10 fog readability floor must survive.

Doc 61 P1-9 text of record: "Render into a WebGLRenderTarget at internal resolution
(HalfFloat, Nearest). One full-screen pass: tone map, sRGB, per-region lift/gamma/gain,
4×4 Bayer ordered dither, animated grain and vignette (58:103 single-pass fusion).
With a render target bound, three.js does not tone-map (three.classic.js:37702-37713),
so tone mapping must move into this pass."

## VERIFIED VENDOR FACTS (IO verified all in the worktree's prototype/vendor/three.classic.js, r185, REVISION='185'):
- V1: fragment prelude injects tone mapping ONLY when `parameters.toneMapping !== NoToneMapping`
  (defines build, ~line 1759345). parameters.toneMapping comes from getParameters (~line 4598):
  `let toneMapping = NoToneMapping; if (material.toneMapped) { if (currentRenderTarget === null
  || currentRenderTarget.isXRRenderTarget === true) { toneMapping = renderer.toneMapping; } }`.
  => Rendering the SCENE into a WebGLRenderTarget leaves every scene material in linear
  HDR (no tone map applied there) — exactly the doc's premise.
- V2: outputColorSpace for materials with an RT bound = ColorManagement.workingColorSpace
  (linear), so the scene pass stays linear — the post pass must do its own tone map + sRGB.
- V3: ShaderChunk IS exported (line 60595: `const ShaderChunk = {`; export `__THREE__.ShaderChunk`).
  `tonemapping_pars_fragment` chunk (~1555573) contains the FULL NeutralToneMapping function
  body including `uniform float toneMappingExposure` and every named function
  (LinearToneMapping, ReinhardToneMapping, CineonToneMapping, ACESFilmicToneMapping,
  AgXToneMapping, NeutralToneMapping, RRTAndODTFit, agxDefaultContrastApprox, plus the
  LINEAR_REC2020_TO_LINEAR_SRGB / LINEAR_SRGB_TO_LINEAR_REC2020 const mats and
  CustomToneMapping). The chunk is a STRING; a non-raw ShaderMaterial may splice it into
  its own fragment source to reuse the identical Neutral math (`vec3 NeutralToneMapping(vec3 color)`
  needs `toneMappingExposure` uniform declared; it is not a #define).
- V4: for the blit material: ShaderMaterial defaults to toneMapped=true; when IT renders
  with NO RT bound it would ALSO tone-map (double). The blit ShaderMaterial MUST set
  `toneMapped: false` in its constructor (line 20937 `this.toneMapped = true;` is the
  Material default). Then the prelude skips both TONE_MAPPING and its functions, and
  our spliced Neutral call is the only tone map.
  NB getParameters also only defines TONE_MAPPING's chunk when renderer.toneMapping !==
  NoToneMapping — with toneMapped:false the define never appears regardless.
- V5: the blit pass's own outputColorSpace: renderer.outputColorSpace = SRGBColorSpace
  applies (parameters.outputColorSpace = renderer.outputColorSpace when NO RT bound, line
  ~5510) => the blit material's fragment prefix ALSO gets colorspace_pars + a
  `linearToOutputTexel` that... only appears as a function definition; it is CALLED only
  inside built-in chunk `colorspace_fragment` ("gl_FragColor = linearToOutputTexel(
  gl_FragColor );"), which a custom ShaderMaterial does NOT include by default. So a
  custom fragment that never calls linearToOutputTexel receives the sRGB OETF function
  but never auto-applies it. DO NOT let the pass double-apply sRGB: if we splice
  colorspace_pars_fragment for the sRGBTransferOETF function we may; but simpler LAW:
  our pass does its OWN explicit sRGB encode (mix(pow(c, 0.41666)*1.055-0.055, c*12.92,
  lessThanEqual(c, 0.0031308)) — the exact branch vendor uses) and splices NOTHING from
  colorspace chunks. State this in the shader source as a comment for the validator.
- V6: WebGLRenderTarget exists (class at 9502, export confirmed). Default options (line
  9308 _setTextureOptions): minFilter default LinearFilter, magFilter default LinearFilter
  (Texture ctor default at 7255), type default UnsignedByteType, colorSpace default
  NoColorSpace, generateMipmaps false. HalfFloatType is exported (1 hit in export block).
  HalfFloat renderability: textureTypeReadable (in WebGLTextures) treats HalfFloat as
  NOT universally color-renderable — requires `EXT_color_buffer_half_float` OR
  `EXT_color_buffer_float` (7 hits for EXT_color_buffer at ~62365 area). => the RT
  construction must fall back cleanly: feature-test ONCE (renderer.getContext().getExtension...),
  if the ext is absent use UnsignedByteType (LDR) and the pass still runs (grade+dither+grain
  on 8-bit values); NEVER throw, NEVER crash boot. Log one console line with the chosen path.
- V7: renderer.setRenderTarget(rt) exists (35 hits); passing null restores the default
  framebuffer (standard r185; the same API set used by EffectComposer internals at
  ~1712714: they flip renderer.toneMapping to NoToneMapping during the scene pass —
  our design does NOT need to do that because it renders to an RT, where tone mapping
  is already skipped by the material gate per V1; do NOT mutate renderer.toneMapping).
- V8: `dithering` (material flag) exists as a separate built-in mechanism (Bayer-8x8
  style dithering_fragment chunk injected into built-in materials only when
  parameters.dithering true) — UNRELATED to this round; our pass adds its own 4×4 Bayer
  (doc-ordered). Do not touch material.dithering on any scene material.

## CRITICAL DESIGN BINDS (why this must not change the approved look)
The whole P0 set (R2 P0-3) validated a LOOK: Neutral tonemap + exposure 1.15 so fog
stays brightest; day/night multiplies exposure via S.exposureMult (applyDayNight line
1959: `game.renderer.toneMappingExposure = CFG.renderer.toneMappingExposure * S.exposureMult`).
Night dormant config row carries exposureMult 0.75. So the post pass MUST:
1. Read the LIVE `renderer.toneMappingExposure` per frame (uniform) — never cache it —
   so the day/night exposureMult chain keeps working unmodified. The scene shader chain
   will NO LONGER see toneMappingExposure (no tone map happens in the scene pass).
   The exposure math moves wholesale into our NeutralToneMapping call via the uniform.
2. Reproduce the OLD visible result to ZERO per-pixel difference when the post pass is
   CONFIG-DISABLED (CFG.post.enabled false => never create RT, never install; boot
   byte-path identical; the only allowed difference is file additions). With
   enabled:true and grade/dither/grain/vignette all at their identity values, the
   pass must ALSO be pixel-equivalent to the old look (tone map + sRGB = the old
   renderer default-framebuffer path with Neutral + SRGBColorSpace). All creative
   deviation lives in the CONFIG rows (enabled rows for grade/dither/grain/vignette,
   each defaulting to identity or off, all PROPOSED for Nicko tuning). The pass law:
   IDENTITY AT DEFAULTS. Each creative channel starts OFF/identity; Nicko turns
   channels on and tunes; the round only ships the machinery + neutral machinery
   defaults. Doc-61-named default VALUES (dither + grain + vignette amounts) go as
   PROPOSED cfg rows with enabled:false so the ship state is provably look-neutral.

## CONFIG row (CFG.post), all PROPOSED except enabled:
```
post: {
  enabled: true,            // master switch; false => code inert, tree identical
  msaa: 0,                  // reserved, do not implement; must be ignored, zero paths today
  // Per-region lift/gamma/gain, from CFG.regionX.id keys onto hex numbers:
  liftR: 0.0, liftG: 0.0, liftB: 0.0,   // additive pre-gamma lift (linear)
  gamma: 1.0,               // per-channel gamma exponent applied as pow(c, vec3(gammaR/gammaG/gammaB)) etc.
  gainR: 1.0, gainG: 1.0, gainB: 1.0,
  // Per-region grade rows (WH_POSTPASS_V1): keys = region ids, values = same fields with region values.
  // ALL THREE rows start identical (identity). Rows are pure CFG; the shader reads uniforms
  // refreshed per region switch (applyRegionLighting pattern) and per phase.
  regions: {
    hold_outskirts: { liftR: 0.0, ... }, darkwood_edge: {...}, forest_of_the_old_king: {...}
  },
  dither: { enabled: false, strength: 0.5 },   // 4x4 Bayer ordered, strength in [0.0,1.0], applied AFTER sRGB (display domain) with pixel-quantization-friendly 1/255-scaled offset
  grain: { enabled: false, strength: 0.5, speedSeconds: 0.25, sizePx: 1 },  // animated: white noise, scale = sizePx in internal-buffer px, animates on cfg.speedSeconds period
  vignette: { enabled: false, radius: 0.72, softness: 0.35, strength: 0.35 } // display-domain multiply: color *= smoothstep-based radial falloff
}
```
NO OTHER config keys (valspec greps). msaa is a doc-61 word; keep the key as a
documented-inert reservation ONLY if trivially cheap; if it costs any code path today,
omit the key — the spec accepts EITHER (devbot picks one, states it).

Region grade resolution law: at any frame the pass reads row = post.regions[
game.regionManager ? rm.logic.activeId : CFG.regionA.id] — a live read, refreshed
into uniforms ONLY when the id CHANGES from the last upload (cheap equality check, no
per-frame upload of static values). Region switches + phase both ride this (phase
doesn't touch post — grade rows are static per region).

## Implementation (game.js; THE ONLY FILE; zero vendor edits)
Marker: `WH_POSTPASS_V1` must appear (a) in the module block, (b) in the v8 build's
game.js copy, (c) nowhere else.

1. At the END of setupRenderer() (returns renderer): nothing changes there — post
   installs inside setupScene() AFTER the scene exists but BEFORE first render, same
   slot as the P1-7 chunk installer, so the first frame already renders through the
   RT pipeline (no flash of unprocessed frames; boot shows the loading overlay until
   the game runs anyway, so even a 1-frame difference is invisible).
2. New module-scope block `WH_POSTPASS_V1` placed between applyDayNight and the
   loop helpers, containing:
   - `function initPostPass()` — idempotent (a second call with the same renderer must
     no-op entirely, not re-create; expose the state object `window.WH_POSTPASS`).
     Only runs if CFG.post && CFG.post.enabled true. Steps:
     a. feature-test HalfFloat: `var gl = renderer.getContext(); var hf = !!(gl.getExtension('EXT_color_buffer_half_float') || gl.getExtension('EXT_color_buffer_float'));`
        Pick texType = hf ? THREE.HalfFloatType : THREE.UnsignedByteType; console.log
        one line: 'WH_POSTPASS_V1: RT type ' + (hf ? 'halffloat' : 'ubyteldr').
     b. sizes from internalSize() (the R3 P0-4 law: EXACTLY the drawing buffer size,
        div-aware).
     c. `game.sceneRT = new THREE.WebGLRenderTarget(w, h, { minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter, depthBuffer: true, stencilBuffer: false, type: texType })` — Nearest is the doc's
        point-sampled rule (protects the P0-4 pixel-locked look; NO mipmap). Note the
        texture colorSpace stays NoColorSpace (the doc's data-only law, V5).
     d. blit material: `new THREE.ShaderMaterial({ uniforms: {...}, vertexShader, fragmentShader, toneMapped: false, depthTest: false, depthWrite: false })`
        with vertex shader:
        ```glsl
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = vec4(position.xy, 0.0, 1.0);   // full-clip quad, no matrices
        }
        ```
        And the scene-quad geometry: `new THREE.PlaneGeometry(2, 2)` — covers the clip
        volume exactly (PlaneGeometry centered; xy spans [-1,1]).
     e. the fragment shader: single-pass fused chain IN THIS ORDER (order of record):
        (i)   sample scene: `vec3 col = texture2D(tScene, vUv).rgb;` (linear HDR,
              scene's frame buffer content)
        (ii)  tone map: `col = NeutralToneMapping(col);` — vendored verbatim (V3
              splice of ShaderChunk['tonemapping_pars_fragment'] at material build
              time as a JS string, NOT copied by hand; the fragment must include the
              EXACT vendor text so the Neutral branch matches what the non-RT path
              had). The vendor chunk declares `uniform float toneMappingExposure`
              itself — OUR uniforms map therefore carries the uniform under that
              EXACT name `{ toneMappingExposure: { value: CFG.renderer.toneMappingExposure } }`
              (the chunk-declared name and the JS uniform name must match, or the
              upload binds nothing and the look breaks). Its .value is refreshed per
              frame from renderer.toneMappingExposure (V6.1 binds the day/night
              chain). State this uniform-name contract in a comment.
              ALSO handle the chunk's `#ifndef saturate / #define saturate(...) #endif`
              block — harmless, splices clean.
        (iii) per-region lift/gamma/gain: `col = col * gain + lift; col = pow(max(col, 0.0), vec3(gamma));`
              ORDER of record: lift ADDS first, then gain MULTIPLIES, then gamma
              (the chain lift→gain→gamma in that order; comment marks it). lift and
              gain are vec3 uniforms read from the CONFIG row's 3-arrays; gamma is a
              float uniform from the row's scalar. A UNIFORM PER CHANNEL GROUP (not
              per channel): uLift (vec3), uGain (vec3), uGamma (float). All read
              from the CONFIG row for the region (uniform refresh on region-id
              change only). NOTE: the spec's original prose said "col = col * gain
              + lift" — bind gain FIRST (multiply), THEN add lift, THEN gamma. The
              three steps may be one expression; keep the order.
        (iv)  sRGB encode: the EXACT vendor branch from the V5 census
              (`mix(pow(col.rgb, vec3(0.41666)) * 1.055 - vec3(0.055), col.rgb * 12.92, vec3(lessThanEqual(col.rgb, vec3(0.0031308))))`),
              applied to col directly (alpha stays 1).
        (v)   dither (after sRGB, display domain): if enabled: `float b = bayer4x4(vec2(gl_FragCoord.xy));` then
              `col += (b - 0.5) * (ditherStrength / 255.0);` — 4×4 Bayer matrix,
              generated IN JS as the literal 16-float array (not runtime GLSL
              computation); the JS assembles the GLSL literal `const float
              whBayer4x4[16] = float[...](...);` (GLSL ES 3.0? — NO: r185 classic
              shaders are GLSL ES 1.0 (WebGL1-compat syntax with WebGL2 upgrades
              handled by three internally); DO NOT use float[N] array literal
              syntax. Use bit-free arithmetic form: `float bayer4(vec2 p) { p = floor(mod(p, 4.0)); ...nested mixes/mat mult-free... }`
              Devbot may implement as any function mathematically equal to the 4×4
              Bayer index/16 table {0,8,2,10; 12,4,14,6; 3,11,1,9; 15,7,13,5}
              (normalized 0..1 by /16). A verbatim 16-entry nested-if or an arithmetic
              formula is fine, but the function must be PURE, deterministic, and
              depend ONLY on gl_FragCoord.xy integer part. Comment must cite the
              matrix-of-record row-major table above.)
        (vi)  grain (after dither): if enabled: `float g = whGrain(vUv, uTimeSec);`
              col += (g - 0.5) * grainStrength * 0.35; — whGrain = a GLSL
              deterministic hash (classic `fract(sin(dot(...)))` family OK; must be
              pure), sampled on a sizePx-scaled grid so the grain has integer-pixel
              chunkiness when sizePx > 1; uTimeSec is a uniform advancing with the
              sim's day/night time (NOT wall time — see 3; grain then animates on
              cfg.grain.speedSeconds period: `uTimeSec / speedSeconds` drives a
              floor() phase so grain changes only every speedSeconds (a strobe-free
              periodic update, matches the doc's "animated grain" while staying
              deterministic inside a sim-frame test).
        (vii) vignette (last): if enabled: compute `vec2 q = vUv - 0.5; float r2 = dot(q,q);`
              `float v = smoothstep(radius - softness, radius + softness, r2 * 4.0 + ...)` — ANY correct
              radial falloff is fine as long as (1) it's a multiply on col with a
              [0,1] weight smoothly falling to vignetteStrength*(some floor) at the
              corners, (2) at radius>=1.0 with softness>=0.5 it becomes a NO-OP
              (documented identity case). Pin the documented identity case in the
              comment and the valspec.
        (viii) output: `gl_FragColor = vec4(col, 1.0);` (alpha never sampled)
     f. render path change IN loop() (game.js line 3604 replacement, THE ONE CALL):
        OLD: `game.renderer.render(game.scene, game.camera);`
        NEW (inside `if (window.WH_POSTPASS && window.WH_POSTPASS.active)` gate — the
        module exposes .active = installed AND cfg.enabled; when inactive the line
        falls back to the ORIGINAL code UNCHANGED):
        ```game.js
        game.renderer.setRenderTarget(game.sceneRT);
        game.renderer.render(game.scene, game.camera);
        game.renderer.setRenderTarget(null);
        game.renderer.render(game.postQuad.scene, game.postQuad.camera);
        ```
        postQuad = { scene: new Scene with one Mesh(geo, blitMat), camera: an
        OrthographicCamera(-1, 1, 1, -1, 0, 1) }. autoClear stays default TRUE (both
        passes must clear; two render calls in a frame is the standard three.js pattern).
   - Refresh law for uniforms IN THE SAME BLOCK, ticked from a dedicated function
     `postPassTick()` called from loop() ONCE PER FRAME, right AFTER atmosphereTick
     and BEFORE the render line (so any same-frame exposure/phase change lands):
     - uExposure.copy from renderer.toneMappingExposure (live read, no caching).
     - uTimeSec += dt (sim time, dt from the loop's dt variable passed in; NOT
       performance.now()).
     - region-row equality check; on id change refresh lift/gamma/gain uniforms.
     - NO allocation (no new Vector3/Color per frame; numeric uniform .value writes
       only; the ONE-time allocation happens at initPostPass only).
3. CFG.post.regions rows keyed EXACTLY as the CONFIG day/night fog rows (region ids
   as keys — hold_outskirts / darkwood_edge / forest_of_the_old_king) — Devbot MAY
   ALSO read a fallback default row { identity } when a fourth region id (rot_den,
   veil_crypt, ...) is encountered at runtime; NO new CONFIG regions beyond the three
   (identity fallback is code-side, not a CONFIG row per unknown id — this keeps the
   CONFIG row-count frozen while every unknown id is safe). The valspec asserts:
   - the THREE rows exist under post.regions;
   - each carries all 7 fields (liftR liftG liftB gammaR gammaG gammaB gainR gainG gainB) =>
     WAIT: gamma per-channel? Doc 61 says "lift/gamma/gain" without channel granularity.
     DESIGN DECISION (spec of record): gamma is a SINGLE vec3-uniform but ONE scalar
     per row (gamma, not gammaR/G/B); lift is vec3 (liftR/liftG/liftB); gain is vec3
     (gainR/gainG/gainB). 4 scalars per row total... lift(3)+gamma(1)+gain(3) = 7
     numbers per region row. CONFIG row shape:
     `hold_outskirts: { lift: [0.0, 0.0, 0.0], gamma: 1.0, gain: [1.0, 1.0, 1.0] }`
     — array literals, THREE.Color-compatible reads.
   - dither/grain/vignette blocks all exist with their fields;
   - master post.enabled default TRUE (the pass runs; it's the doc's requirement that
     the pass EXIST in the pipeline), BUT every creative channel defaults to
     identity/ off/ disabled — so ship-state = identity look.
4. The doc's "per-region lift/gamma/gain" is the CREATIVE surface: Nicko tunes rows
   per region later (e.g. lift [0.02, 0.02, 0.04] for a cold hold). The THREE rows
   ship identity.

## Off-laws (validation gates, each independently greppable)
- O1. `git diff` shows the ONLY changed files: prototype/js/game.js, prototype/js/CONFIG.js,
      prototype/builds/v8-playable.html (build). NO style.css, NO index.html, NO vendor.
      (The CONFIG P0-4 law the RT size derives from is CFG.renderer.internalResDiv +
      game.js internalSize() — pre-existing, unchanged; the RT just CALLS internalSize().
- O2. prototype/vendor/three.classic.js sha256 EXACTLY
      9a14fed2d1a8413edf623cae96008e3433964ab421340f89a0316716ec8e5a1a (computed by
      IO this wake). (Devbot must recompute + compare in ITS report.)
- O3. CFG.post.enabled=false path: boot-check with the flag off shows the pre-round
      behavior + the ORIGINAL render line unguarded (`game.renderer.render(game.scene,
      game.camera);` still present verbatim in the else path).
- O4. All P1-7 behavior preserved: WH_ATMO markers still present + atmo chunk splice
      still runs (the scene content is untouched; fog math lives in scene shaders,
      unchanged by the RT indirection).
- O5. P0-4 internal-res law preserved: internalSize() drives the RT size (RT never
      window-sized); the F1/F2 res-tuner keys STILL resize the RT live (postResize
      handler: when internal buffer changes, `game.sceneRT.setSize(w, h)`).
      Devbot WIRE: in the F1/F2 applyResDiv path AND the window resize handler, add
      `if (game.sceneRT) { var s = internalSize(); game.sceneRT.setSize(s.w, s.h); }`
      — both, exactly where the two setSize calls exist today (line ~65 + ~3612).
- O6. NO runtime allocation in postPassTick (Devbot self-review + valspec grep).
- O7. Boot barrier + loading screen + asset pipeline + save/restore + day/night + all
      regions unchanged: no new console errors at boot; the pass logs ONE extra line.

## What a Testerbot valspec must cover (IO pre-declares; Testerbot expands + owns)
- V-A. CFG.post row exact field census (grep), regions 3 rows identity, no extra keys,
       msaa law honored (absent or inert).
- V-B. Shader source integrity: fragment contains 'WH_POSTPASS_V1', 'NeutralToneMapping',
       'toneMappingExposure', bayer comment row-major table line, sRGB branch matches the
       vendor mix/pow text (float-for-float), 'lessThanEqual(vec3' present, grain/vignette
       identity guards.
- V-C. ShaderMaterial flags: toneMapped:false, depthTest:false, depthWrite:false, NearestFilter.
- V-D. RT type law: HalfFloat feature-test + UnsignedByte fallback, no throw, one log line.
- V-E. render-path swap: RT-bound when active, null-RT fallback path exists when inactive
       (grep shows BOTH branches); renderer.toneMapping NEVER written by the post code
       (grep -c 'toneMapping =' in the new module == 0).
- V-F. postPassTick law: sim-time dt-driven; NO allocation; uniform writes only; called
       between atmosphereTick and the render line (grep order in loop).
- V-G. resize wires at BOTH existing setSize sites; sceneRT null-guarded.
- V-H. Off-path byte-law: with enabled false, the ONLY functional difference is zero.
       (Testerbot constructs a node-based parse of the module: when !active, the loop's
       render branch is the literal original.)
- V-I. M-10 preservation proxy: the scene material fragment chain is untouched (O2
       vendor sha + WH_ATMO markers intact + fog uniform writes untouched) — tone map
       happening later cannot change FOG VISIBILITY math, only the final color grade;
       assert the fog constants + moonDir splice sites unchanged.
- V-J. Identity look: with all channels off, pass output = old path pixel-for-pixel
       (Testerbot MAY verify via the repo-law final_boot.js boot check + reading the
       shader source; numeric pixel-diff harness is OPTIONAL, not required this round).
- V-K. Boot check (repo-law final_boot.js): 0 pageerrors, boot barrier 51 critical
       assets settled (0 stand-ins), 80 assets 0 stand-ins, 0 GLB 4xx on the live
       8793 surface. Plus ONE new console line grep: WH_POSTPASS_V1 RT type.
- V-L. No harness runs / no headless smoke tests BY THE BUILD lane (Nicko law); the
       ONLY node/browser execution allowed is the repo-law final_boot.js boot check
       (single run, Devbot runs it once after build; Testerbot runs its OWN copy once
       for the verdict). No interactive pointer-lock/play testing.

## Deliberate scope cuts (state in the report; NOT deviations)
- No depth buffer tricks, no MSAA, no FXAA, no bloom (doc 61 P1-9 names none of them
  except via "tone map" — bloom is NOT in this doc's text).
- No per-phase (day/night) grade rows — per-REGION only; the day/night state drives
  exposure only. If Nicko later wants phase grades, that's a follow-up round.
- No screenshot diff harness (P1-9's M-21 is Nicko's eye; the machinery is what ships).
- No changes to enemy/HUD/fog/atmosphere code paths.

## Known-verified non-goals for Devbot (grep these to save time)
- The day/night exposure chain (applyDayNight 1959) needs NO change — the uniform
  read happens live in postPassTick.
- P1-7 chunk installer (WH_ATMO) needs NO change.
- regionFade / denFade / cemetery fog writers need NO change (they write scene fog,
  which the scene pass keeps honoring; the post pass is downstream).
- The HUD (reticle, bars, dial) is DOM and rides ABOVE the canvas — untouched by an
  RT swap (the canvas element itself still exists; only its backbuffer content changed).
- The boot-time class picker + save rows + loading bar are DOM too — untouched.

## Numbers for the valspec's numeric checks (all measured by IO this wake)
- game.js is 3620 lines at spec time; CONFIG.js 5290; region-manager.js 2506.
- Current HEAD sha256s (worktree, frozen): game.js 3620 lines; CONFIG.js 5290.
- v8 build size at HEAD: 3,622,907 bytes.

## Build + close-out (Devbot hand-off)
1. Devbot lands code in the worktree (NO commit, NO push).
2. Devbot runs `node --check` on each touched prototype/js file? (game.js has an
   IIFE wrapper — node --check is syntactically valid for the file as a whole.)
   Then runs python3 tools/build_v8.py from repo root (build law: this is not a
   "playability claim", it's the build-tool gate; the build is REQUIRED to flip).
   Then runs the repo-law final_boot.js boot check ONCE against
   http://172.16.5.1:8793/current/prototype/builds/v8-playable.html (serving the
   OLD release until IO flips — the boot check on the OLD surface is pointless for
   THIS code; instead Devbot serves the worktree copy on 8794 the way the P1-7
   valspec did: `cd /tmp/wh-worldfeat/prototype && python3 server.py 8794 &` then
   final_boot.js pointed at 8794, then kill the server).
3. Testerbot re-runs its own boot check, greps the markers, and writes the verdict
   to io/reports/2026-11-08-p1-9-post-pass-validation.md.
4. IO commits (all files incl. spec + valspec + verdict), pushes, flips, journals.
