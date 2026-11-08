# P1-9 — Retro Post Pass — VALIDATION SPEC (Testerbot, wake 41)

Independent validation spec for `/tmp/wh-worldfeat/io/specs/p1-9-post-pass-spec.md`
(IO spec, wake 41). Worktree `/tmp/wh-worldfeat`, branch `feat/world-visuals`,
spec-time HEAD `7697dd9`.

This spec is executable by a validator who has NOT seen any prior conversation.
Every check below is self-contained: it names the file, the command to run, and
the exact pass condition.

## Read-only rules for this round

- Validator NEVER edits `prototype/js/*`, `prototype/vendor/*`, `index.html`,
  or runs `git commit/push/stash/checkout`. Read-only git (`status/log/diff/
  grep`) is fine.
- Validator may run `grep`, `sha256sum`, `node --check`, `git diff --stat`,
  `python3 tools/build_v8.py` (build gate), and the repo's own
  `tools/final_boot.js` boot-check harness (V-K, code QA, not a playtest).
- NO harness/headless-browser page loads beyond `final_boot.js` run ONCE by
  Testerbot for the verdict (repo law; Nicko's playtest is the acceptance bar).
- Validation output lands in `io/reports/2026-11-08-p1-9-post-pass-validation.md`
  (created by the validating Testerbot, not this file).

## House law: content anchors, not line numbers

Line numbers below are spec-time references only (lines drift as Devbot
edits). Every PASS criterion keys on a grep needle plus an expected
neighborhood, never on a bare line number.

## File abbreviations

- GJS    = `prototype/js/game.js`
- CFGJS  = `prototype/js/CONFIG.js`
- VENDOR = `prototype/vendor/three.classic.js`
- BUILD  = `prototype/builds/v8-playable.html` (produced by `tools/build_v8.py`)
- FROM   = run all greps from `/tmp/wh-worldfeat` unless stated otherwise

## Pre-flight anchor facts (Testerbot verified this wake, spec-time tree 7697dd9)

- `WH_POSTPASS` marker: 0 hits in GJS, 0 hits in CFGJS (absent today, as spec says).
- `toneMappingExposure` write sites in GJS: line 126 (`setupRenderer`) and
  line 1959 (`applyDayNight` day/night chain) — exactly 2; spec's "1959"
  anchor verified verbatim:
  `game.renderer.toneMappingExposure = CFG.renderer.toneMappingExposure * S.exposureMult;`
- `CFG.renderer.toneMappingExposure` row: CFGJS:11, value 1.15 (R2 P0-3 law).
- `internalSize()` sites in GJS: defined at 43; consumed at 64 (applyResDiv),
  112 (setupRenderer), 3611 (window resize). `internalResDiv` reads at 44, 62,
  72, 85. Spec's "~46/65/113/3612" = off-by-one from comments; content anchors
  verified instead (house law).
- Loop render call: `game.renderer.render(game.scene, game.camera);` at GJS:3604,
  inside `loop()`, after `updateInteractPrompt();` and before the closing `}`.
- `renderer.setSize` sites: 65 (applyResDiv), 114 (setupRenderer), 3612 (resize).
  Spec's "BOTH setSize sites" for resize wires = **65 and 3612** (65 is the F1/F2
  res-tuner path; 3612 is the window resize path). 114 is boot-time initial
  sizing — the RT does not exist yet, so it is NOT a resize-wire target
  (initPostPass sizes the RT at create time).
- Vendor sha256: `9a14fed2d1a8413edf623cae96008e3433964ab421340f89a0316716ec8e5a1a`
  — recomputed this wake, MATCHES spec O2.
- Vendor r185 confirmed (`const REVISION = '185';` line 11).
- `ShaderChunk` exported at 60595; `NeutralToneMapping` has 10 hits in vendor
  (chunk body + export block + prelude references).
- Vendor sRGB OETF chunk (colorspace_pars_fragment at 60373) carries the exact
  constants `0.41666`, `1.055`, `0.055`, `0.0031308`, `12.92` in the
  `mix(pow(...) * 1.055 - vec3(0.055), ... * 12.92, vec3(lessThanEqual(..., vec3(0.0031308))))` form. Verified.
- `currentRenderTarget === null` tone-map/outputColorSpace gates verified at
  vendor 37706 / 67567 / 67599 (V1/V2 anchors).
- `WH_ATMO` markers: 11 hits in GJS (P1-7 installer intact).
- `atmosphereTick(dt);` call at GJS:3589, before the render line at 3604 —
  the postPassTick slot (V-F) sits between them.
- Day/night dormant `exposureMult: 0.75` row at CFGJS:4753 — the chain the
  uniform live-read must preserve.
- Region ids `hold_outskirts` / `darkwood_edge` / `forest_of_the_old_king`
  verified in CFGJS (170/382/557); mistPlane regionId row at 154.
- GJS line count at spec time: **3619** (spec says 3620 — see AMB-3, cosmetic).
- CFGJS line count 5290 (matches spec). BUILD size 3,622,907 bytes (matches spec).
- `git status --porcelain` at spec time: `M prototype/builds/v8-playable.html`
  (pre-existing, from the P1-8 flip) + this spec untracked. Validator's V-3
  file-census must treat this pre-existing BUILD modification as part of the
  baseline, not as a Devbot change signal — see V-3 wording.

---

## 1. Config law (V-A family)

**V-1 (CFG.post row field census):** `grep -n "post: {" CFGJS` returns exactly
1 hit (the new row, added near the other post-P0 renderer/look rows). Inside the
`post: { ... }` block the following keys MUST each appear exactly once:
`enabled`, `regions`, `dither`, `grain`, `vignette`. Inside `regions:` exactly
the THREE keys `hold_outskirts`, `darkwood_edge`, `forest_of_the_old_king`,
each carrying `lift`, `gamma`, `gain`. Inside `dither:` keys `enabled`,
`strength`. Inside `grain:` keys `enabled`, `strength`, `speedSeconds`,
`sizePx`. Inside `vignette:` keys `enabled`, `radius`, `softness`, `strength`.
The `msaa` key is OPTIONAL: either absent entirely, or present with a comment
marking it reserved/inert AND zero code references (`grep -n "post.msaa\|post\.msaa\|\.msaa" prototype/js/game.js` = 0 hits; if the key exists in CFGJS it must
be data-only). PASS iff all mandatory keys present exactly once, region rows
exactly 3, and the msaa law held (absent OR inert-with-no-code-path).

**V-2 (identity-at-defaults law):** In the same CFGJS block: master
`enabled: true`; every region row's `lift` array literal equals `[0.0, 0.0,
0.0]` (any whitespace), `gamma: 1.0`, `gain: [1.0, 1.0, 1.0]`;
`dither.enabled: false`; `grain.enabled: false`; `vignette.enabled: false`.
Verify by reading the block (`sed -n` around the V-1 hit) — all seven
creative channels provably OFF/identity at ship state. PASS iff every value
above holds to the literal. (Numeric tolerance: `0` vs `0.0` acceptable.)
*Maps to IO spec §CONFIG row + "IDENTITY AT DEFAULTS" + §3.*

## 2. Scope / byte-identity (part of O-family gates)

**V-3 (changed-file census — the ONLY-files gate):** `git status --porcelain`
plus `git diff --stat HEAD` FROM the worktree. The set of prototype code files
changed across the round MUST be exactly: `prototype/js/game.js`,
`prototype/js/CONFIG.js`, `prototype/builds/v8-playable.html` (the build re-flip).
Spec/verdict files under `io/` are allowed additions. NO other path under
`prototype/` may appear modified or newly added: specifically zero hits for
`prototype/vendor/`, `prototype/index.html`, `prototype/css/`, `prototype/js/region-manager.js`,
`prototype/js/player.js`, `prototype/js/enemy.js`, and no new `??` files under
`prototype/js/`. Note for the validator: the worktree carried a pre-existing
`M prototype/builds/v8-playable.html` at spec time (P1-8 flip remnant); the
round's own build re-writes the same file — that single path is expected and
allowed. Any OTHER prototype path = FAIL. *Maps to O1.*

**V-4 (vendor byte-identity):** `sha256sum prototype/vendor/three.classic.js`
FROM the worktree must print EXACTLY
`9a14fed2d1a8413edf623cae96008e3433964ab421340f89a0316716ec8e5a1a`.
Also `git diff --stat HEAD -- prototype/vendor/three.classic.js` must print
NOTHING. FAIL on any mismatch. *Maps to O2.*

## 3. Module block + marker (V-B presence half)

**V-5 (marker placement law):** `grep -rn "WH_POSTPASS_V1" prototype/`
(after build) returns hits ONLY in GJS (module block + log line) and in the
BUILD bundle's embedded game.js copy. `grep -c "WH_POSTPASS_V1" CFGJS` = 0,
`grep -c "WH_POSTPASS_V1" prototype/vendor/three.classic.js` = 0, and zero hits
in any other prototype file. FAIL on any hit outside GJS+BUILD. *Maps to
spec §Implementation "Marker" law: (a) module block, (b) build copy, (c)
nowhere else.*

**V-6 (module block position):** The `WH_POSTPASS_V1` module-scope block must
sit between `applyDayNight` and the loop helpers: the first
`WH_POSTPASS_V1` hit line number must be GREATER than the
`function applyDayNight` definition line and LESS than the
`function loop(` line. Verify by `grep -n "function applyDayNight\|WH_POSTPASS_V1\|function loop(" GJS` and comparing the hit positions.
PASS iff the block lives strictly between. (Content anchors, not numbers.)

**V-7 (install slot — setupScene, before first render):** `initPostPass`
must be DEFINED at module scope and CALLED from inside `setupScene()`
after the scene exists (i.e. textually after `scene.fog = new THREE.FogExp2`
or after the WH_ATMO install call — the P1-7 slot pattern) and before
`setupScene` returns. `grep -n "initPostPass\|function setupScene\|return scene" GJS`;
PASS iff a `function initPostPass` definition exists at module scope AND a
call `initPostPass(...)` line number sits between the `function setupScene(`
line and that function's `return scene;`. (Maps to spec §1.)

**V-8 (idempotence + state object):** Inside `initPostPass`'s body, an
early-return guard must exist so a second call no-ops: grep the body for a
check on the exposed state object, e.g. `if (window.WH_POSTPASS && window.WH_POSTPASS.installed) return;` or an equivalent guard on a
module-scope created flag. `window.WH_POSTPASS` must be assigned exactly once
(grep -c on `window.WH_POSTPASS =` in GJS = 1). PASS iff both hold.
(Maps to spec §2a "idempotent ... expose the state object window.WH_POSTPASS".)

## 4. RT construction law (V-D family)

**V-9 (HalfFloat feature-test + fallback):** Inside `initPostPass`, grep for
`EXT_color_buffer` — at least one hit covering `EXT_color_buffer_half_float`
and/or `EXT_color_buffer_float`, feeding a `gl.getExtension(...)` call, and
the type choice between `THREE.HalfFloatType` and `THREE.UnsignedByteType`.
Both type names must appear in the block. There must be NO `throw` in
`initPostPass` (grep the function body: `throw` = 0 hits). PASS iff the
feature-test and both types are present and no throw exists. *Maps to V6
vendor law.*

**V-10 (single log line):** `grep -n "WH_POSTPASS_V1: RT type" GJS` — exactly
1 hit in the module block, a `console.log(...)` line that logs the chosen
path (halffloat or ubyteldr wording per spec §2a; accept any two-branch
string that names the chosen type; the constant prefix `WH_POSTPASS_V1` is
mandatory). PASS iff exactly one such log call exists, on ONE line, executed
once at init (not inside any per-frame path — confirm it is inside
`initPostPass`, not `postPassTick`). *Maps to spec §2a "console.log one
line" + O7 "ONE extra line".*

**V-11 (RT construction parameters):** The `new THREE.WebGLRenderTarget(`
call in the block must carry `THREE.NearestFilter` for BOTH `minFilter` and
`magFilter`, `depthBuffer: true`, `stencilBuffer: false`, and a `type:`
field set from the V-9 feature-test variable (not a hard-coded type).
Grep the constructor's argument object; PASS iff all four named props+
the dynamic type are present and NO `THREE.LinearFilter` appears in the
constructor args, and no `generateMipmaps` key appears (default false law).
Also: the RT dimensions must come from `internalSize()` — grep the block
for an `internalSize()` call feeding the `w, h` args. *Maps to spec §2c +
O5's "RT never window-sized".*

**V-12 (blit material flags — hard gate):** The `new THREE.ShaderMaterial(`
call for the blit must carry ALL THREE of `toneMapped: false`,
`depthTest: false`, `depthWrite: false` in its options object. Grep the
constructor call's options object. PASS iff all three literals present
exactly once in that constructor. (The `toneMapped: false` is the V4
double-tone-map defense.) *Maps to spec §2d + vendor V4.*

**V-13 (fullscreen quad + camera):** The block must create
`new THREE.PlaneGeometry(2, 2)` (or `(2,2)` with either spacing) AND an
`new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1)` with the exact
argument values `(-1, 1, 1, -1, 0, 1)`. The vertex shader must contain
`gl_Position = vec4(position.xy, 0.0, 1.0)` (full-clip quad, no matrices —
the substring `position.xy` inside the vertex shader source, and the
absence of `projectionMatrix`/`modelViewMatrix` in the vertex shader).
PASS iff all three sub-checks hold. *Maps to spec §2d + postQuad spec.*

## 5. Fragment shader content law (V-B content half — hard gates)

For V-14..V-22: the "fragment" under test is the fragment shader SOURCE as
built inside the module block (JS string pieces + any spliced chunk). Grep
GJS around the `fragmentShader` assembly; where the source is assembled
from a JS splice of a vendor chunk, verify the SPLICE EXPRESSION (not the
GLSL text, which lives in the vendor file).

**V-14 (Neutral splice via JS, not hand-copy — hard gate):** The fragment
source must incorporate the vendor tone-mapping chunk by JS string splice:
grep GJS for `ShaderChunk['tonemapping_pars_fragment']` or
`ShaderChunk.tonemapping_pars_fragment` — at least 1 hit inside the module
block, used in a concatenation that builds `fragmentShader`. Additionally,
the literal GLSL text `vec3 NeutralToneMapping(` must NOT be hand-written
inside a quoted string in GJS: grep GJS for lines containing the literal
string `vec3 NeutralToneMapping(` — every hit must be either the call site
`col = NeutralToneMapping(col);` (no `vec3` return type) or a comment;
there must be ZERO hits of the full vendor function-definition line embedded
as a string literal. PASS iff the splice reference exists AND no hand-copied
function body is embedded. (Maps to spec §2e(ii) "NOT copied by hand".)

**V-15 (Neutral call + uniform name contract):** The fragment must contain
the call `NeutralToneMapping(col);` (or `= NeutralToneMapping(` with the
scene-sampled variable as the argument). The uniforms object literal in the
ShaderMaterial constructor must carry a key EXACTLY named
`toneMappingExposure` (matching the vendor chunk's declared uniform) —
grep the uniforms literal for `toneMappingExposure:`. A comment near the
uniform or the call must name the contract (accept any comment containing
`toneMappingExposure` in the module block). PASS iff all three hold.
*Maps to spec §2e(ii) uniform-name contract + vendor V3.*

**V-16 (exact vendor sRGB branch constants — hard gate):** The fragment must
contain the sRGB encode using the exact vendor constants. Grep GJS for each
of the five constants as fragment-source content: `0.41666`, `1.055`,
`0.055`, `0.0031308`, `12.92` — each must appear at least once inside the
fragment shader source string(s) in the module block (not merely in
comments). The shape must be the branch form: `mix(` present AND
`lessThanEqual(` present in the same source, both inside the module block.
PASS iff all five constants and both function tokens appear in the fragment
source. (The vendor chunk's exact form per spec V5/§2e(iv):
`mix(pow(col.rgb, vec3(0.41666)) * 1.055 - vec3(0.055), col.rgb * 12.92, vec3(lessThanEqual(col.rgb, vec3(0.0031308))))` —
validator confirms the constants; whitespace/vec3-wrapping may differ.)
Additionally: grep the module block for `linearToOutputTexel` — must be 0
hits (no colorspace chunk splice; spec V5 "simpler LAW" — do our own encode,
splice nothing from colorspace chunks). PASS iff that grep is empty too.

**V-17 (Bayer function + cited table — hard gate):** The fragment/module
block must define a 4×4 Bayer function (any name containing `bayer`,
case-insensitive: `grep -in "bayer" GJS` inside the block, at least 1 hit as
a GLSL function definition). A COMMENT in the block must cite the row-major
table of record: the comment must contain the sequence `0,8,2,10` AND
`12,4,14,6` AND `3,11,1,9` AND `15,7,13,5` (all four rows, comma-separated
as above; whitespace tolerated). Hard gate: **NO GLSL array-literal syntax**
— grep the fragment source for `float[16]` and the pattern `float [0-9]+\[` —
must be 0 hits inside the module block (GLSL ES 1.0 law; r185 classic shaders
are GLSL ES 1.0). PASS iff the function exists, the comment cites all four
rows, and array-literal greps are empty. *Maps to spec §2e(v).*

**V-18 (grade chain order — lift→gain→gamma):** The fragment must apply the
per-region grade in the order of record: gain multiply, lift add, gamma pow —
with a comment marking the order. Form of record per spec §2e(iii):
`col = col * gain + lift;` then `pow(max(col, 0.0), ...)`. Grep the fragment
for `pow(max(` (guard against negative base) and for the uniforms
`uLift`, `uGain`, `uGamma` (or whatever the dev names them — MUST be one
vec3 uniform for lift, one vec3 for gain, one float for gamma: confirm by
reading the uniforms literal — exactly one `uGamma`-class float and two
vec3-class entries). PASS iff the order comment exists, `pow(max(` present,
and the uniform arity (vec3/vec3/float) matches. *Maps to spec §2e(iii).*

**V-19 (grain law):** If/as written: grain GLSL function is a pure
deterministic hash (accept the classic `fract(sin(dot(` family or
equivalent); grep for `fract(` in the module block). The grain must be
gated on an enabled flag (grep for the CFG row path or a uniform enable in
the grain code neighborhood). The time base must be a uniform advanced from
sim dt (see V-25) — NOT from `performance.now()`/`Date.now()`: grep the
WHOLE module block for `performance.now` and `Date.now` — must be 0 hits.
The speedSeconds phase law: grep for `speedSeconds` in the grain code
neighborhood (uniform or config read feeding the phase). PASS iff all four
sub-checks hold. *Maps to spec §2e(vi).*

**V-20 (vignette identity guard):** The vignette must be the LAST operation
before output and must carry a documented identity case: a comment in the
vignette code neighborhood documenting that at `radius>=1.0` with
`softness>=0.5` (or the dev's equivalent boundary) the vignette is a NO-OP
(or that the shipped default row leaves it disabled-and-identity). Grep for
`vignette` (case-insensitive) in the module block: at least one comment hit
stating the identity/no-op condition, and the GLSL must be an enabled-gated
multiply on `col`. Confirm the vignette statement appears AFTER the grain
statement and BEFORE `gl_FragColor =` by hit-position order in the fragment
assembly. PASS iff all three sub-checks hold. *Maps to spec §2e(vii).*

**V-21 (output write + alpha law):** The fragment's final assignment must be
of the form `gl_FragColor = vec4(<col-var>, 1.0);` — grep for
`gl_FragColor = vec4(` in the module block, exactly 1 hit in the fragment,
with the literal alpha `1.0`. PASS iff exactly one output write ending in
`, 1.0)`. *Maps to spec §2e(viii).*

**V-22 (no toneMapping writes / no colorSpace splice — regression wall):**
Within the module block: `grep -n "toneMapping =" GJS` restricted to lines
between the `WH_POSTPASS_V1` block start and its end — must be 0 hits (the
block NEVER writes `renderer.toneMapping`; vendor V7 law). Also
`sRGBTransferOETF` must NOT be hand-embedded: the block must not contain
that function's definition text (the constants law in V-16 is satisfied by
the explicit encode, not by splicing `colorspace_pars_fragment`): grep the
block for `sRGBTransferOETF` — 0 hits in GJS (it lives only in vendor and
must stay only there; `grep -c "sRGBTransferOETF" GJS` = 0 for the whole
file). PASS iff both greps are clean. *Maps to vendor V5/V7 + V-E's
"NEVER written".*

## 6. Render-path swap (V-E family)

**V-23 (gated branch, BOTH branches present — hard gate):** In `loop()`, the
render site must now be branched. Grep GJS for
`renderer.setRenderTarget(` — at least 2 hits in the module/loop area:
one `setRenderTarget(game.sceneRT)` and one `setRenderTarget(null)`,
plus a second `renderer.render(` call for `game.postQuad.scene`.
The gate must test the module state (e.g. `window.WH_POSTPASS && window.WH_POSTPASS.active`). Verify by reading the render
site (`grep -n "setRenderTarget\|WH_POSTPASS.active\|renderer.render" GJS`
and `sed -n` around the hits). PASS iff: (a) the `.active` gate exists,
(b) inside the active branch the four-statement pattern
(setRT(sceneRT) → render(scene,camera) → setRT(null) → render(postQuad))
appears in that order, (c) a fallback/else path exists. *Maps to spec §2f.*

**V-24 (off-path byte law — CFG.post.enabled=false keeps the literal
original render line — hard gate):** With `CFG.post.enabled` false, the
executed loop render line must be the literal original
`game.renderer.render(game.scene, game.camera);`. Verify statically: in
GJS the token `game.renderer.render(game.scene, game.camera);` must appear
in BOTH branches of the render gate — inside the active branch (scene pass)
AND on the fallback path (else-branch or unguarded fallback), byte-identical
to the original (modulo leading whitespace). `grep -c "game.renderer.render(game.scene, game.camera);" GJS` >= 2 after the build, and
`sed -n` around the render site must show the inactive path executing that
exact line with no other post-processing. Additional sub-check: when
`CFG.post.enabled` is false, `initPostPass` must no-op BEFORE creating the
RT: grep the top of `initPostPass` for the `CFG.post` + `.enabled` guard
preceding any `new THREE.WebGLRenderTarget` (position compare). PASS iff
both sub-checks hold. *Maps to O3 + spec §"Off-laws" + CRITICAL DESIGN
BINDS #2.*

## 7. Tick / uniform refresh law (V-F family)

**V-25 (postPassTick position + sim-time law):** `postPassTick` must be
DEFINED at module scope and CALLED from `loop()` exactly once per frame,
positioned AFTER `atmosphereTick(dt);` and BEFORE the render call. Verify:
`grep -n "atmosphereTick(dt);\|postPassTick\|renderer.render(game.scene, game.camera)\|renderer.render(game.postQuad" GJS` —
the `postPassTick` call line must sit between the atmosphereTick hit (today
3589) and the render block (today 3604-neighborhood). dt must be passed in
from the loop's dt variable (the call passes the loop's `dt`); grep the
call for `(dt)`. Inside `postPassTick`, time accumulation must add the
passed dt to a module-scope accumulator. `performance.now`/`Date.now` = 0
hits in the whole module block (also asserted in V-19). PASS iff position,
dt plumbing, and no-wall-clock all hold. *Maps to spec §2 "Refresh law" +
2e(vi) time base.*

**V-26 (exposure live-read law):** Inside `postPassTick`, the
`toneMappingExposure` uniform's `.value` must be refreshed per frame from
`game.renderer.toneMappingExposure` (live read — an ASSIGNMENT reading the
renderer property, NOT a cached numeric). Grep the body for an assignment
of form `...toneMappingExposure... .value = game.renderer.toneMappingExposure` (variable names may differ; the RHS MUST be
`game.renderer.toneMappingExposure` or `renderer.toneMappingExposure`
with the live object reference). A comment naming the day/night chain
contract should exist near it (accept any comment with `exposureMult` or
`applyDayNight` in the module block — soft requirement; record absence in
the verdict as a NOTE, not a FAIL). PASS iff the live-read assignment
exists on the per-frame path. *Maps to CRITICAL DESIGN BINDS #1.*

**V-27 (region-row refresh only on id change):** The region grade uniforms
must refresh ONLY when the active region id changes from the last upload:
grep `postPassTick` (or a helper it calls) for an equality/inequality check
comparing the current id (from `game.regionManager`/rm logic active id or
the CFG fallback per spec §"Region grade resolution law") against a stored
last-id variable, with the uniform writes textually inside that conditional
branch. Verify there is no unconditional per-frame upload of the
lift/gamma/gain triple. PASS iff the change-gated pattern exists. *Maps to
spec §"Region grade resolution law" + §2 "region-row equality check".*

**V-28 (no per-frame allocation — hard gate):** Inside `postPassTick`'s
body (and any per-frame helper), grep for `new THREE.Vector`, `new THREE.Color`,
`new Color(`, `new Vector`, `THREE.PlaneGeometry`, `new PlaneGeometry`,
`object allocation literals passed to .set(` — the patterns `new THREE.` and
`= new ` must produce 0 hits on the per-frame path (init-time allocations
inside `initPostPass` are legal and expected: grep each function body
separately by line range). Uniform updates must be `.value` writes or
`.set(...)` on pre-allocated uniform value objects. PASS iff zero
allocation patterns in `postPassTick`. *Maps to O6 + spec §2 "NO
allocation".*

## 8. Resize wires (V-G family)

**V-29 (BOTH setSize sites wired — hard gate):** The two internal-res
resize sites must each carry a sceneRT resize, null-guarded: (a) inside
`applyResDiv` (anchor: the function containing `CFG.renderer.internalResDiv = div;` and the `game.renderer.setSize(isz.w, isz.h, false);` line —
today 60-66); (b) inside the window `resize` listener (anchor:
`window.addEventListener('resize'` and the second
`game.renderer.setSize(isz.w, isz.h, false);` — today 3606-3613). At BOTH
sites there must appear, immediately after or adjacent to the renderer
setSize line, a guarded resize of form `if (game.sceneRT) { ... game.sceneRT.setSize(...) }` (the guard
`if (game.sceneRT)` or `game.sceneRT &&` is mandatory). The RT size arg
must come from `internalSize()` (the site's `isz` variable or a fresh
`internalSize()` call — either acceptable per spec O5's wire text). Verify
with `grep -n "sceneRT" GJS` — expect hits in initPostPass (create), both
resize sites, and the loop (render). Confirm by `sed -n` around both
setSize anchors that the null guard is present in each. PASS iff both
sites wired with null guards. Note: the setupRenderer setSize (today 114)
is NOT a required wire site — the RT does not exist at boot before
setupScene; initPostPass sizes the RT from `internalSize()` at creation
(V-11). *Maps to O5 + spec §2 "F1/F2 applyResDiv path AND the window
resize handler".*

## 9. Preservation / regression wall (V-I family + spec non-goals)

**V-30 (WH_ATMO markers intact):** `grep -c "WH_ATMO" GJS` must remain >= 11
(the P1-7 baseline count this wake; accept >= 11). The chunk-splice install
function must be untouched: `git diff HEAD -- prototype/js/game.js` hunks
must NOT touch the body of the WH_ATMO install function (anchor: the
function around GJS:134-216 today) nor `atmosphereTick` (anchor ~1544),
nor the splice call site region in setupScene. PASS iff marker count holds
and the diff hunks fall outside those function bodies. *Maps to O4 +
spec "P1-7 chunk installer needs NO change".*

**V-31 (fog-writer sites unchanged):** The legal fog writers are unchanged:
`git diff HEAD -- prototype/js/game.js` hunks must NOT touch the bodies of
`applyRegionLighting`, `cemeteryFogTick`, `regionFadeTick`, the
`applyDayNight` denFade block, or `atmosphereTick`. Verify via
`git diff -U0 -- prototype/js/game.js` and confirm no hunk's content range
falls inside any of those five bodies (identify bodies by their
`function <name>` anchors, not line numbers). PASS iff zero diff lines land
inside. *Maps to spec "fog writers need NO change".*

**V-32 (exposure chain line unchanged):** The applyDayNight exposure write
must remain byte-identical: `grep -n "game.renderer.toneMappingExposure = CFG.renderer.toneMappingExposure \* S.exposureMult" GJS` — exactly 1 hit
(with any single-space normalization), unchanged from HEAD (confirm via
`git diff` that line 1959-neighborhood is untouched). PASS iff the exact
assignment survives verbatim. *Maps to spec "applyDayNight 1959 needs NO
change" + CRITICAL DESIGN BINDS preamble.*

**V-33 (HUD / DOM untouched):** `git diff --stat HEAD` shows zero changes to
`prototype/index.html` and zero changes to any HUD-adjacent JS functions:
confirm no diff hunks touch `updateHud`, `updateEnemyBars`, `updateDayClock`,
`updateInteractPrompt`, or the reticle/bars/dial DOM code (grep the diff
for those function names — 0 hits). PASS iff both hold. *Maps to spec
"HUD is DOM and rides ABOVE the canvas — untouched" non-goal.*

**V-34 (CFG diff purity):** `git diff HEAD -- prototype/js/CONFIG.js` shows
ONLY added lines (the `post:` block + its comments). No `-` line deletes or
modifies a pre-existing row — specifically the `toneMappingExposure: 1.15`
row (CFGJS:11 today), the day/night `exposureMult` rows (4673-4753 region),
and the three region blocks must appear in the diff only as unchanged
context. PASS iff zero deletions/edits of prior rows. *Maps to spec
"No OTHER config keys" + preservation binds.*

## 10. Build + boot gates

**V-35 (syntax + build):** `node --check prototype/js/game.js` and
`node --check prototype/js/CONFIG.js` both exit 0. Then
`cd /tmp/wh-worldfeat && python3 tools/build_v8.py` exits 0 (build law:
`build_v8.py`, NOT a new build tool). After build, `grep -c "WH_POSTPASS_V1" prototype/builds/v8-playable.html` >= the GJS module-block marker count
(the build's embedded copy must carry the markers). PASS iff all three
sub-checks hold. *Maps to close-out §2 + spec §1 marker law (b).*

**V-36 (boot check — repo-law final_boot.js, ONCE by Testerbot):** After
the build flips locally, Testerbot serves the worktree copy on port 8794
the way the P1-7 valspec did
(`cd /tmp/wh-worldfeat/prototype && python3 server.py 8794 &`, then run
`node tools/final_boot.js` pointed at
`http://127.0.0.1:8794/builds/v8-playable.html` per the repo's harness
usage, then kill the server). PASS iff the harness reports: 0 pageerrors,
boot barrier 51 critical assets settled with 0 stand-ins, 80 assets total
with 0 stand-ins, 0 GLB 4xx, AND the captured console contains exactly ONE
line matching `WH_POSTPASS_V1: RT type` (either halffloat or ubyteldr
wording per V-10 — both are PASS; record which path the local GL took).
This is the ONLY harness execution this round (also re-run by Devbot once
after its own build per spec close-out — Testerbot's run is the verdict of
record). If `server.py`/8794 is unavailable or the harness shape changed,
record the exact command + output and mark FAIL-with-blocker, NOT pass.
*Maps to V-K + spec close-out §2-3. NOTE: IO spec body says "8793 surface"
in the V-K bullet but close-out §2 says serve on 8794 — the P1-7 precedent
and §2 win; 8794 of the worktree copy is the binding surface (see AMB-1).*

**V-37 (no other harness runs — Nicko law):** The verdict file must record
that NO other headless/browser/smoke execution was performed by Testerbot
beyond V-36, and that the build lane ran only its own single boot check +
`node --check` + `build_v8.py`. PASS by attestation recorded in the verdict.
*Maps to V-L.*

## 11. Identity look (V-J, static)

**V-38 (identity-at-defaults static proof):** With ship-state config
(V-2: all creative channels off/identity), prove statically that the pass
output reduces to the old look: (a) the grade chain's uniforms at defaults
are lift=[0,0,0], gain=[1,1,1], gamma=1.0 — with those values
`col*gain+lift` = col and `pow(max(col,0),1.0)` = col (record this algebra
line in the verdict); (b) dither/grain/vignette enabled-guards skip their
adds/multiplies at enabled:false (grep each guard — confirmed in V-17/V-19/
V-20 neighborhoods); (c) Neutral + sRGB-encode = the old default-framebuffer
path per vendor V1/V5 facts (cite the vendor line numbers 67567/67599 and
the constants from V-16 in the verdict). A numeric pixel-diff harness is
explicitly OPTIONAL and NOT required (spec V-J). PASS iff the verdict file
carries this three-part reduction argument with the grep evidence from
V-16..V-20. *Maps to V-J + CRITICAL DESIGN BINDS #2.*

---

## Verdict rule

Verdict = **PASS** iff every check V-1..V-38 is PASS, or is explicitly
recorded SKIPPED-under-amendment with the amendment logged in the
amendment-log section below (amendments may only come from IO, in writing,
mid-flight; Testerbot does not self-amend). Otherwise verdict = **FAIL**
with the failing V-numbers listed at the top of
`io/reports/2026-11-08-p1-9-post-pass-validation.md`.

Recording: one row per V-number: `| V-n | PASS/FAIL/SKIP | <command> | <observed output / 1-line excerpt> |`, then a summary block with counts,
then the failing list (if any), then STRESS answers (below), then the
amendment log.

## STRESS questions for the validator (record answers in the verdict file)

S1. Double tone-map audit: with the RT bound, scene materials skip tone
mapping (vendor V1). With the blit's `toneMapped:false`, the blit skips the
built-in map (vendor V4). Trace by reading: is there ANY path where
NeutralToneMapping could execute twice on the same pixel (e.g. if
`.active` gate mis-evaluates while sceneRT exists, or if a scene material
has toneMapped:false AND the module block also ran)? State the proof or
flag the gap.

S2. LDR fallback look delta: if `EXT_color_buffer_*` is absent, the RT is
UnsignedByte — the scene HDR range clamps at 1.0 before Neutral runs.
Under day exposure 1.15, what scene values exceed 1.0 in practice (fog is
the brightest area by P0-3 law)? Record whether the LDR path would visibly
differ, and whether the single log line (V-10) is sufficient disclosure.
Do not "fix" — flag numbers if they contradict the spec's "still runs"
claim.

S3. Uniform-name binding proof: the spliced vendor chunk declares
`uniform float toneMappingExposure`. Confirm by reading the vendor chunk
text (`grep -n "uniform float toneMappingExposure" prototype/vendor/three.classic.js`) that the name matches the uniforms literal key EXACTLY
(V-15). If the chunk's saturate #define block could collide with any other
spliced chunk in the same fragment (e.g. if the builder also splices
common chunks), flag the double-#define risk.

S4. Region unknown-id fallback: spec §3 requires an identity fallback row
in CODE for a fourth region id (rot_den, veil_crypt). Verify the code path:
when `post.regions[activeId]` is undefined, the code must use identity
values, not crash and not upload garbage. Grep for the fallback expression
(e.g. `|| identityRow`, a `.hasOwnProperty` check, or an `Object.assign`
default). If the build indexes blindly, FAIL V-27 with the S4 note.

S5. First-frame flash: initPostPass installs in setupScene before first
render (V-7). If the RT creation failed silently (V-9's no-throw law), does
`.active` stay false so loop() falls back to the original line (V-24)?
Trace the failure path and record whether a half-installed state (RT null
but .active true) is possible.

---

## AMENDMENT LOG (mid-flight IO amendments; Testerbot appends verbatim, each entry = id, date, IO wording, superseded V-rows)

- AA-1 (2026-11-08, IO wake 41): AMB-1 ruled. V-36 binds 8794-of-the-worktree
  as the verdict-of-record surface (P1-7 precedent; close-out §2 wins). The
  V-K phrase "0 GLB 4xx on the live 8793 surface" is satisfied by a POST-FLIP
  IO-serving-health check (IO boots the FLIPPED 8793 release + the WebUI 8787
  route after the verdict and before declaring the round served) — it is NOT
  part of Testerbot's verdict run and does not block the verdict. No V-row
  superseded; V-36 stands as written.
- AA-2 (2026-11-08, IO wake 41): AMB-2 ruled. V-29 stands exactly as written:
  resize wires at the two sites only (applyResDiv ~65 + window resize ~3612);
  the boot-time setSize at ~114 is excused (RT does not exist pre-setupScene)
  and NO comment or wire is required there. AMB-2 closed.
- AA-3 (2026-11-08, IO wake 41): AMB-3 noted, closed with no action. The
  spec's GJS line-count is off-by-one cosmetic drift; every V-row remains
  keyed on content anchors (house law), so no ruling changes any check.

## AMBIGUITIES FLAGGED FOR IO RULING (AMB-1..n, pre-dispatch)

- **AMB-1 (boot-check surface port):** spec V-K bullet says "0 GLB 4xx on
  the live **8793** surface" while close-out §2 says serve the worktree copy
  on **8794** (the P1-7 precedent). This valspec binds 8794-of-the-worktree
  (V-36). If IO intends 8793-after-flip instead, amend V-36; the two surfaces
  serve different code (8793 = old release until IO flips), so this choice
  changes what the boot check proves. **Awaiting IO ruling.**
- **AMB-2 (resize-wire site count):** spec O5 says "both, exactly where the
  two setSize calls exist today (line ~65 + ~3612)" — but the tree carries
  THREE setSize calls (65 applyResDiv, 114 setupRenderer, 3612 resize).
  This valspec binds 65+3612 per O5's explicit pair (V-29) and excuses the
  boot-time 114 (RT does not exist pre-setupScene). If IO additionally wants
  a wire or a comment at 114, amend. **Awaiting IO ruling.**
- **AMB-3 (game.js line count drift):** spec "Numbers" section says game.js
  is 3620 lines at spec time; measured 3619 at HEAD 7697dd9 this wake.
  Cosmetic (all content anchors verified). Assumed off-by-one via trailing
  newline counting. No ruling needed unless IO's build-size math depends on
  it. **Noted, no block.**

---
*Valspec authors: Testerbot, wake 41. Anchors verified against worktree
HEAD 7697dd9 on 2026-11-08 (see "Pre-flight anchor facts").*
