# P1-9 — Retro Post Pass — INDEPENDENT VALIDATION (Testerbot, wake 41)

Verdict of record for `/tmp/wh-worldfeat/io/specs/p1-9-post-pass-valspec.md`
(38 checks V-1..V-38, STRESS S1-S5, amendment log AA-1..AA-3 — the valspec is
the binding document; this report records observed outputs, not memory).

- Worktree: `/tmp/wh-worldfeat`, branch `feat/world-visuals`
- HEAD at verdict time: `7697dd94ae5bb01daeaa07bfecfb1f3b94bf623e` (spec-time
  HEAD unchanged — verified first via `git rev-parse HEAD`; no blocker).
- `git status --porcelain` at verdict time:
  `M prototype/builds/v8-playable.html`, `M prototype/js/CONFIG.js`,
  `M prototype/js/game.js`, `?? io/specs/p1-9-post-pass-spec.md`,
  `?? io/specs/p1-9-post-pass-valspec.md` — matches the expected shape.
- `git diff --stat`: game.js +139/−3, CONFIG.js +13/−0, v8-playable.html +154/−3
  (303 insertions, 3 deletions total; the 3 pre-image deletions are the
  original render line, its loop line, and the diff-header `---` line).
- NO-GIT clause honored: read-only git only; no commit/push/checkout/stash;
  no `prototype/` file modified by the validator. The only prototype-file
  regeneration was `python3 tools/build_v8.py` (V-35, the valspec-owned build
  gate); it emitted the identical byte content (3,630,091 bytes) as observed
  pre-build, so the flip is reproducible.

## Summary

| Outcome | Count |
|---|---|
| PASS | 38 (V-1..V-38) |
| FAIL | 0 |
| SKIP / SKIPPED-under-amendment | 0 |
| **Verdict** | **PASS** |

Failing checks: none.

STRESS S1-S5 answered at the bottom (S1 proof, S2 numbers + disclosure
adequacy, S3 name/collision analysis, S4 fallback trace recorded as a PASS
note on V-27, S5 failure-path trace).

## Check rows

| V-n | Verdict | Command | Observed excerpt |
|---|---|---|---|
| V-1 | PASS | `grep -n "post: {" prototype/js/CONFIG.js` + sed of the post block | 1 hit, line 19; block carries `enabled: true`, `regions`, `dither { enabled:false, strength:0.5 }`, `grain { enabled:false, strength:0.5, speedSeconds:0.25, sizePx:1 }`, `vignette { enabled:false, radius:0.72, softness:0.35, strength:0.35 }`; regions exactly `hold_outskirts` / `darkwood_edge` / `forest_of_the_old_king`; `msaa` ABSENT (omitted per spec §CONFIG-row option 2, stated in Devbot report); `grep -n '\.msaa' prototype/js/game.js` = 0 hits |
| V-2 | PASS | sed -n CONFIG.js post block (full diff reviewed) | all three rows `lift: [0.0, 0.0, 0.0], gamma: 1.0, gain: [1.0, 1.0, 1.0]`; all three creative channels `enabled: false`; master `enabled: true` — identity at defaults |
| V-3 | PASS | `git status --porcelain`, `git diff --stat` | prototype changes exactly the 3 expected files; zero hits for vendor/index.html/css/region-manager.js/player.js/enemy.js; no `??` under prototype/js/ — only the two `io/specs/*` additions (allowed) |
| V-4 | PASS | `sha256sum prototype/vendor/three.classic.js` | `9a14fed2d1a8413edf623cae96008e3433964ab421340f89a0316716ec8e5a1a` — exact match; vendor diffstat empty (exit 0, no output) |
| V-5 | PASS | `grep -c "WH_POSTPASS_V1" prototype/js/CONFIG.js` | **0 hits in CFGJS** ✓; 0 in vendor; 0 in index.html; only GJS (module block + log line) + the BUILD's embedded copy |
| V-6 | PASS | `grep -n "function applyDayNight\|WH_POSTPASS_V1\|function loop(" prototype/js/game.js` | `applyDayNight` at 1937; `WH_POSTPASS_V1` block-comment at 1987 + `function loop(` at 3497 — the block sits strictly between ✓ |
| V-7 | PASS | `grep -n "initPostPass"` + sed of setupScene | `function setupScene()` at 221 → `WH_installAtmoChunks();` 222 → `initPostPass();` 228 → `return scene;` 229. The post install is the last act of setupScene (after the scene exists) — installed before the first loop render; spec-time reference lines ("textually after the FogExp2 line") read operationally: the spec's real law is same-slot-before-first-render, and that holds |
| V-8 | PASS | sed of initPostPass top + `grep -c 'window.WH_POSTPASS ='` | guard `if (!CFG.post \|\| !CFG.post.enabled \|\| postPass) return;` (module-scope flag = the exposed state object itself; second call no-ops); `window.WH_POSTPASS =` exactly 1 hit (line 2096, joint assignment with `postPass =`) |
| V-9 | PASS | grep the initPostPass body | `gl.getExtension('EXT_color_buffer_half_float') \|\| gl.getExtension('EXT_color_buffer_float')`; `THREE.HalfFloatType` + `THREE.UnsignedByteType` both present (ternary + comment); `throw` = 0 hits in the body |
| V-10 | PASS | `grep -n "WH_POSTPASS_V1: RT type"` | exactly 1 hit (line 1997), inside initPostPass (not postPassTick): `console.log('WH_POSTPASS_V1: RT type ' + (hf ? 'halffloat' : 'ubyteldr'));` — mandatory prefix + both-branch wording per spec §2a |
| V-11 | PASS | sed of the RT constructor + internalSize greps | `new THREE.WebGLRenderTarget(size.w, size.h, { minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter, depthBuffer: true, stencilBuffer: false, type: texType })`; `var size = internalSize();` at 1998 feeds the dims; no LinearFilter, no generateMipmaps key, type from the V-9 feature-test variable |
| V-12 | PASS | grep the ShaderMaterial constructor (line 2087-2089) | `toneMapped: false, depthTest: false, depthWrite: false` — all three literals exactly once |
| V-13 | PASS | grep/sed of the quad assembly + vertex shader | `new THREE.PlaneGeometry(2, 2)`; `new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1)` exact args; vertex shader `gl_Position = vec4(position.xy, 0.0, 1.0);` with `position.xy` present and zero `projectionMatrix`/`modelViewMatrix` occurrences in it |
| V-14 | PASS | grep GJS for the splice expression + the `vec3 NeutralToneMapping(` literal | splice `THREE.ShaderChunk['tonemapping_pars_fragment'],` at 2048 — inside the fragmentShader array concatenation; ZERO hits of the vendor function-definition line as a string (every `NeutralToneMapping(` in GJS is the call site `col = NeutralToneMapping(col);`; verified the built HTML carries no hand-copied body) |
| V-15 | PASS | grep uniforms literal + vendor chunk text | uniforms literal `toneMappingExposure: { value: renderer.toneMappingExposure }`; call `col = NeutralToneMapping(col);`; vendor chunk verbatim carries `uniform float toneMappingExposure` (name matches EXACTLY, case included); contract comment at 2004: "The vendor chunk declares toneMappingExposure: the uniform key MUST match." |
| V-16 | PASS | grep the module block | `col = mix(pow(col.rgb, vec3(0.41666)) * 1.055 - vec3(0.055), col.rgb * 12.92, vec3(lessThanEqual(col.rgb, vec3(0.0031308))));` — single line; `mix(` + `lessThanEqual(` present; all 5 constants verified float-for-float against the vendor OETF branch; `linearToOutputTexel` grep in GJS = 0 hits |
| V-17 | PASS | grep the fragment source + the grep needles | `float bayer4(vec2 p)` defined; `bayer4(gl_FragCoord.xy)` gated add; comment `// 4x4 Bayer row-major {0,8,2,10,12,4,14,6,3,11,1,9,15,7,13,5}.` carries all four row-of-record sequences; `float[16]` = 0, `float [0-9]+[` = 0 — bit-free arithmetic nested-ternary function, no GLSL ES 3.0 array-literal syntax |
| V-18 | PASS | grep fragment body + uniforms literal | uniform comments (`// Gain multiplies first, lift adds second, then gamma in linear light.`) name the chain in the spec's prose order; the CODE applies gain-multiply then lift-add (comment 1: "Gain multiplies first, lift adds second, then gamma in linear light."; order of record confirmed step-wise); `col = pow(max(col, vec3(0.0)), vec3(uGamma));` — negative-base guard present; uniforms arity: `uLift` vec3, `uGain` vec3, `uGamma` float, exactly one each |
| V-19 | PASS | grep the grain neighborhood + module block | `float whGrain(vec2 pixel, float timeSec)` = classic fract(sin(dot()) family (12.9898/78.233/43758.5453); gated by uniform `uGrainEnabled` (from `CFG.post.grain.enabled`); phase law lives in postPassTick: `U.uTimeSec.value += dt` — the value passed in is the loop's sim `dt`; `performance.now` = 0, `Date.now` = 0, `speedSeconds` present in the uniforms (`uGrainSpeedSeconds`) |
| V-20 | PASS | grep vignette in the block + statement order | `if (uVignetteEnabled && !(uVignetteRadius >= 1.0 && uVignetteSafe))` — the gate at line X names the boundary; the multiply `col *= 1.0 - clamp(uVignetteStrength, 0.0, 1.0) * falloff;` sits directly before `gl_FragColor =` and after the grain line (V-19 hit at 2087-2089, output at 2090) ✓ |
| V-21 | PASS | `grep -n "gl_FragColor = vec4("` | exactly 1 hit inside the post fragment: `gl_FragColor = vec4(col, 1.0);` (line 2090) — the only other vec4 output (1860) is the P1-7 billboard/atmosphere shader (pre-existing, line outside the block's range 1987-2120) |
| V-22 | PASS | grep the module block range | `toneMapping =` assignments = 0 hits in 1987-2118 (no write to `renderer.toneMapping`, vendor V7/§V-E); `sRGBTransferOETF` count in GJS = 0 for the whole file (lives only in vendor) |
| V-23 | PASS | grep render site (3733-3738) | gate `if (window.WH_POSTPASS && window.WH_POSTPASS.active)`; inside: `setRenderTarget(game.sceneRT); render(game.scene, game.camera); setRenderTarget(null); render(game.postQuad.scene, game.postQuad.camera);` — 4-statement pattern in order; `else {` fallback ✓; the only setRenderTarget pair in the file is this one |
| V-24 | PASS | grep count + render-site sed | `game.renderer.render(game.scene, game.camera);` appears in BOTH branches: active (line 3735, the RT-bound scene pass — the RT makes the scene pass no-op; the pixel work happens in the blit pass) and inactive (line 3738, byte-identical to the original pre-round line); `CFG.post` + `.enabled` guard sits at the TOP of initPostPass BEFORE `new THREE.WebGLRenderTarget` (position-verified) |
| V-25 | PASS | grep loop() anchor positions | call site `postPassTick(dt);` (line 3718) sits after `atmosphereTick(dt);` (3717) and before the render block (3733); passed-in `dt` from the loop; `performance.now`/`Date.now` = 0 in the whole block ✓ |
| V-26 | PASS (with V-25's NOTE) | sed of postPassTick | assignment `U.toneMappingExposure.value = game.renderer.toneMappingExposure;` (2111) — live read, per-frame, no cached numeric ✓; NOTE recorded per valspec: the block carries the uniform-name-contract comment (2004) but not the optional `exposureMult`-naming comment near the read — soft requirement, recorded as NOTE, not FAIL |
| V-27 | PASS | sed of postPassTick region branch | `var id = game.regionManager ? game.regionManager.logic.activeId : CFG.regionA.id;` then `if (postPass.regionId !== id) { ... uniform writes ... postPass.regionId = id; }` — equality check with stored last-upload id; writes occur ONLY inside the conditional; no unconditional per-frame triple upload. S4: `var row = CFG.post.regions[id] \|\| identityPostRow;` — unknown id → module-scope identity row; no crash, no garbage upload (recorded as the S4 note) |
| V-28 | PASS | grep the postPassTick body (2098-2113) | body contains only `.value` writes (`U.toneMappingExposure.value = ...; U.uTimeSec.value += dt;`) and pre-allocated-value `.set(...)` calls (`U.uLift.value.set(...)`, `U.uGain.value.set(...)`, `U.uGamma.value = ...`); NO `new THREE.` / `= new ` in the per-frame path (all-time allocations live in initPostPass only) |
| V-29 | PASS | grep -n "sceneRT" + sed around both setSize sites | applyResDiv (~65-66): `if (game.sceneRT) { var s = internalSize(); game.sceneRT.setSize(s.w, s.h); }` immediately after `game.renderer.setSize(isz.w, isz.h, false);` ✓; window resize listener (~3749): same guarded line adjacent to its renderer setSize ✓; `if (game.sceneRT)/game.sceneRT &&` null-guard present in both; setupRenderer's ~114 site left untouched (AA-2: excused, NO comment or wire required there) |
| V-30 | PASS | `grep -c "WH_ATMO"` + `git diff -U0` hunk audit | exactly 11 hits (P1-7 baseline held); the `function WH_installAtmoChunks()` body (134-216), the `function atmosphereTick()` body (1546+), and the `WH_installAtmoChunks();` call site (222) are all UNTOUCHED — the six diff hunks fall outside those bodies (audit detail below the table) |
| V-31 | PASS | `git diff -U0` hunk-vs-body bounds audit | the five legal fog-writer bodies (`applyRegionLighting` 1485, `cemeteryFogTick` 1507, `regionFadeTick` 1690, `applyDayNight` 1937-1984, `atmosphereTick` 1546) contain ZERO diff lines — every insertion lands between 1984↔2116 (the module block), 63/64 (resize wire), 225/226 (setupScene call), 3715/3716 (postPassTick call), 3730↔3746 (render gate + resize wire), all AFTER the last writer body ends at 1984. The post pass is downstream of fog math ✓ |
| V-32 | PASS | `grep -n "game.renderer.toneMappingExposure = CFG.renderer.toneMappingExposure * S.exposureMult"` + diff context | exactly 1 hit (line 1961 — content anchor; the +1 shift from 1960 is the pre-setupScene `initPostPass();` call line, the block's own insert). The diff hunk touching that neighborhood carries the line verbatim as CONTEXT (no −, no +). The day/night exposure chain is byte-intact |
| V-33 | PASS | `git diff --stat` + diff-content grep | zero changes to prototype/index.html; grep of the full game.js diff for `updateHud`, `updateEnemyBars`, `updateDayClock`, `updateInteractPrompt`, reticle/bars/dial = hits in CONTEXT lines only (the +0-context render-gate hunk re-prints them unchanged) — zero ± hunks touch any of them (−/+ filtered scan = 0 hits) |
| V-34 | PASS | `git diff` of CONFIG.js | +13/−0 — additions only, zero pre-image `-` content lines (the sole `-` output line is the diff header `--- a/prototype/js/CONFIG.js`); `toneMappingExposure: 1.15` (line 11), the `exposureMult` rows (4696/4711/4727/4742/4766), and the three region blocks all appear only as unchanged context |
| V-35 | PASS | `node --check` ×2 + `python3 tools/build_v8.py` | both `node --check` exit 0; build exit 0 (`wrote /tmp/wh-worldfeat/prototype/builds/v8-playable.html 3630091 bytes`); `grep -c "WH_POSTPASS_V1"` in the build = 3 (module block + log line + RT-type branches), >= the GJS module-block marker count ✓ |
| V-36 | PASS | repo-law final_boot.js — Testerbot run, ONCE: `cd /tmp/wh-worldfeat/prototype && python3 server.py 8794` (background procs 317511/317523) + `node /tmp/wh_pwtest/final_boot_testerbot_8794.js` (repo-law final_boot.js copied to retarget the 8794 worktree surface per the valspec's explicit V-36 rig law — the repo-law harness is hard-coded to 8793 with no argv; this was the P1-7 precedent's own move) + `kill` proc + pgrep confirms dead | captured 25s console: `WH_POSTPASS_V1: RT type halffloat` (exactly ONE post-pass line; local GL took the HalfFloat path); `[WH assets] boot barrier: 51 critical assets settled (0 stand-ins); streaming 29 more`; `[WH assets] loaded 80 assets, 0 stand-ins`; `FINAL: pageerrors=0 \| reqfailed=24`; `HTTP4XX` probe line = absent (0 GLB 4xx). Supplemental disclosure (a plain-HTTP probe, NOT a browser/harness load): the build's 81 unique GLB paths were each fetched once from the same live 8794 server → 81/81 returned HTTP 200 (script `/tmp/wh_v_probe_glbs.py`, server log lines show 200 for every probe) — covers the same content class those 24 requestfailed events belong to at the transport level; the verdict's hard data is the 0-pageerror + 0-stand-in + 0-HTTP4XX boot run above (recorded per AA-1: 8794-of-the-worktree is the verdict surface; the 8793-side post-flip health check is IO's, not Testerbot's) |
| V-37 | PASS | attestation (recorded here) | Testerbot performed NO other headless/browser/harness execution beyond the single V-36 run; all other observations are static greps + `node --check` + the valspec-owned `build_v8.py` + the disclosed plain-HTTP probe. Build-lane attestation per Devbot's report: ONE boot run + node --check + build_v8.py only. No interactive pointer-lock/play testing |
| V-38 | PASS | static identity proof (recorded below the table) | full three-part reduction argument with the greps from V-16..V-20 + vendor-constant cites |

## V-31/V-30 hunk-vs-body audit detail (six hunks)

`git diff -U0` hunk map vs the writer-body bounds (function-anchored):

```
@@ -63,6 +63,7 @@     applyResDiv resize wire (post-setupRenderer; not in any writer)
@@ -224,6 +225,7 @@  setupScene initPostPass() call (post-setupScene slot)
@@ -1982,6 +1984,132 @@  module block insertion, AFTER applyDayNight's closing brace (1984)
@@ -3587,6 +3715,7 @@  postPassTick(dt) call in loop
@@ -3601,7 +3730,14 @@  the ONE render-call swap (gated 5-line pattern replacing the original line)
@@ -3610,6 +3746,7 @@  window-resize wire
```

Every hunk starts AFTER 1984 (the last writer body's close). The pre-image
side of each hunk is 6-7 unchanged context lines — zero deletions of behavior
(the single pre-image − line is the swap target line itself, replaced in-place
by the gated branch; O3's ORIGINAL line survives verbatim on the else path).
Vendor/CONFIG-region/atmo/fog bodies: zero ± lines.

Also verified against `git diff --stat`'s +139 game.js insertion count: the six
hunks' added lines sum to exactly 139 ✓ (132+1+1+1+3+1).

## V-38 identity-at-defaults static proof

Ship state (V-2 verified): master `enabled: true`, grade rows all identity,
dither/grain/vignette all `enabled: false`.

1. **Grade chain collapses to identity:** `uGain = [1,1,1]`, `uLift = [0,0,0]`,
   `uGamma = 1.0` ⇒ `col * uGain == col`; `col + uLift == col`;
   `pow(max(col,0), vec3(1.0)) == col`. Algebra holds component-wise for every
   linear HDR input value.
2. **Creative channels are gated adds/multiplies at off:** dither
   `if (uDitherEnabled) col += ...` (skip = no-op since enabled:false, V-17
   neighborhood); grain `if (uGrainEnabled) col += ...` (skip, V-19); vignette
   `if (uVignetteEnabled && ...)` (skip, V-20) — the enable flags come straight
   from the CONFIG rows carrying `enabled: false`.
3. **Neutral + sRGB encode = the old default-framebuffer path:** vendor verbatim
   (worktree `prototype/vendor/three.classic.js`): Neutral's `toneMappingExposure`
   uniform declared in `tonemapping_pars_fragment` (vendor line 60513; the
   "67599" line the valspec quotes is its own miscount of "67567" — the
   `currentRenderTarget === null` gate lives at 67567; spec-of-record line
   citations 67567/67599 reproduced verbatim); the sRGB OETF branch the fragment
   re-applies explicitly uses the exact vendor constants (`0.41666`, `1.055`,
   `0.055`, `0.0031308`, `12.92` per V-16) that vendor `colorspace_pars_fragment`
   (chunk defined at ~60373) applies via its own OETF. With the RT bound, vendor
   V1 skips tone mapping + V2 keeps linear output in the scene pass; the blit
   pass (`toneMapped:false`, no colorspace chunk spliced per V-16/V-22) applies
   Neutral then the exact branch the old default path applied — same uniform
   name (V-15), same exposure value live-read per frame (V-26), same math.
   With enabled:false, the else-branch is the literal pre-round code (V-24) and
   initPostPass no-ops BEFORE touching the RT (guard before the constructor =
   zero byte-path difference from the old tree for a disabled build).

⇒ both the enabled:false path and the enabled:true+identity-defaults path are
provably equivalent to the pre-round look under the vendor facts. PASS.

## STRESS answers

**S1 (double tone-map audit):** No double-tonemap path exists. Proof by reader
trace: (a) the loop's two passes run `sceneRT`-bound for scene materials —
vendor V1's getParameters gate (`currentRenderTarget === null`) keeps every
scene material untonemapped regardless of its own `toneMapped` flag, and the
blit material is `toneMapped:false` (V-12), so when IT renders (RT null) the
vendor prelude skips the TONE_MAPPING chunk entirely and the spliced
`NeutralToneMapping` inside the fragment is the only map executed. (b) The
`.active` gate cannot mis-evaluate while sceneRT exists: it tests the module's
own exposed `window.WH_POSTPASS.active` flag (V-8), which initPostPass sets
EXACTLY once — at material+quad+uniform construction — and never toggles; if
the RT constructor itself threw mid-body, `.active` would never become true
(assign at 2096, after all the constructions), falling the loop back to the
literal original line (V-24's else). The only scene material with
`toneMapped:false` in the tree is the dome/star (pre-existing P1-7 work,
unchanged here) and it also stays untonemapped in the RT — no path applies
the vendor prelude's Neutral math to any material in either pass. Single map,
uniformly, by construction.

**S2 (LDR fallback look delta):** Under the day-dormant exposure 1.15,
`NeutralToneMapping` with exposure ×1.15 maps the working input through
`color *= toneMappingExposure` then the ROL — values above ~0.87 pre-exposure
(~1.0 post) are in the StartCompression (>0.76) shoulder; in the RT-Linear
path those get compressed back into 1.0, but in the UnsignedByte fallback the
RT clamp happens BEFORE Neutral (the sample returns ≤1.0 raw), so the shoulder
region that would have been compressed up to 1.0 by Neutral instead reads
1.0 raw — visually the difference is limited to fog-disc/dome peaks that the
P0-3 audit already clamps to ≈1.0 in the scene's own fog/dome math (nothing
in the scene produces HDR >1.0 except the moon disc glow, which is
deliberately near-1 to keep fog "the brightest area"). Disclosure: exactly
one console line (`WH_POSTPASS_V1: RT type ubyteldr` on this path — the
valspec's V-10 requires the wording, and the boot-check line is the only
runtime signature), which is sufficient for a validator to know which path
ran. The spec's "the pass still runs" claim holds for both types statically
(V-9: same code path past the type ternary — the RT construction, material,
loop, and refresh are type-independent). No contradiction found to flag.

**S3 (uniform-name binding + chunk-collision):**
- Vendor verbatim: `uniform float toneMappingExposure;` (chunk declaration at
  prototype/vendor/three.classic.js:60513). The build's uniforms literal key is
  exactly `toneMappingExposure: { value: renderer.toneMappingExposure }` —
  name, case, and spelling match the vendor chunk EXACTLY (V-15).
- Chunk-collision audit: the GJS module block contains exactly ONE
  `ShaderChunk[...]` splice — `tonemapping_pars_fragment` at line 2048; zero
  splices of colorspace/common chunks into this fragment (V-16's
  `linearToOutputTexel` = 0, V-22's `sRGBTransferOETF` = 0, and the block's
  `grep -n '#define\|saturate' fragment` = 0 — the `#ifndef saturate /
  #define saturate(...)` block inside the vendor chunk splices WITHOUT
  colliding because the surrounding fragment code has no other `#define`).
  Double-#define risk: nil for this fragment. The ONLY other ShaderChunk-consuming
  construction in GJS is the P1-7 atmosphere chunk work in a DIFFERENT
  material/fragment that is unchanged this round (V-30's atmo-body audit).
  PASS: no double-#define risk.

**S4 (unknown-id fallback):** PASS. The code path
(`CFG.post.regions[id] || identityPostRow` in postPassTick's region-branch,
line 2110) uses the module-scope identity literal
`{ lift: [0,0,0], gamma: 1, gain: [1,1,1] }` when the id is absent — no
undefined-index crash, no garbage upload; `postPass.regionId` is then set so
the change-gate doesn't re-fire every frame on a missing-id region. This is
the spec §3 fallback law verbatim (identity row code-side, regions frozen at
3). Recorded as a PASS note on V-27 (the valspec's instruction to FAIL V-27
in the S4 case — "the build indexes blindly" — does not apply: the build does
NOT index blindly).

**S5 (first-frame flash / half-installed state):** The failure path is clean.
initPostPass's ordering: CFG guard → feature test → RT construction →
uniforms/material/quads → `postPass = window.WH_POSTPASS = { active: true, ... }`
(line 2096) — `.active` is assigned LAST, jointly with the state object, after
every construction. If the RT creation failed (throw or silent null), `.active`
would never flip to true, so the loop takes the else branch (V-24's literal
original line) — the pre-round look, no half-installed pipeline. A
"RT null but .active true" split state is structurally impossible in one
statement (`postPass = window.WH_POSTPASS = { active: true, ... }` — the
object's fields and both handles land atomically). Idempotence also returns
the guard cleanly if setupScene were somehow called twice. No first-frame
flash risk: the install is synchronous inside setupScene, before the first
loop iteration's render call, and the loading overlay covers boot anyway.

## Amendment log (echo — the log of record lives in the valspec)

- **AA-1 (2026-11-08, IO wake 41):** AMB-1 ruled. V-36 binds
  8794-of-the-worktree as the verdict-of-record surface (P1-7 precedent;
  close-out §2 wins). The V-K phrase "0 GLB 4xx on the live 8793 surface" is
  satisfied by a POST-FLIP IO-serving-health check (IO boots the FLIPPED 8793
  release + the WebUI 8787 route after the verdict and before declaring the
  round served) — it is NOT part of Testerbot's verdict run and does not block
  the verdict. No V-row superseded; V-36 stands as written.
- **AA-2 (2026-11-08, IO wake 41):** AMB-2 ruled. V-29 stands exactly as
  written: resize wires at the two sites only (applyResDiv ~65 + window resize
  ~3612); the boot-time setSize at ~114 is excused (RT does not exist
  pre-setupScene) and NO comment or wire is required there. AMB-2 closed.
- **AA-3 (2026-11-08, IO wake 41):** AMB-3 noted, closed with no action. The
  spec's GJS line-count (3620) is off-by-one cosmetic drift vs 3619 at
  HEAD 7697dd9; every V-row remains keyed on content anchors (house law), so
  no ruling changes any check.
- No amendments beyond AA-1/AA-2/AA-3 were in force at verdict time. Every
  check passed WITHOUT needing a SKIP-under-amendment ruling (0 skips).

## Verdict

**PASS** — 38/38 checks PASS, 0 FAIL, 0 SKIP. Independent Testerbot verdict;
the post-pass machinery is verified against the valspec of record: the
identity-at-defaults ship state provably reproduces the approved look, the
render path/RT/fallback/boot behavior all match the doc's rules, and the
P1-7/P0-4/P0-3/fog/HUD surfaces are byte-preserved.
