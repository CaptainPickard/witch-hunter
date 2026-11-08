# P1-7 — Layered Atmosphere — VALIDATION SPEC (Testerbot, wake 40)

Independent validation spec for `/tmp/wh-worldfeat/io/specs/p1-7-atmosphere-spec.md`
(IO spec, wake 40). Worktree `/tmp/wh-worldfeat`, branch `feat/world-visuals`.

This spec is executable by a validator who has NOT seen any prior conversation.
Every check below is self-contained: it names the file, the command or the
greps to run, and the exact pass condition. Read-only rules for this round:

- Validator NEVER edits `prototype/js/*`, `prototype/vendor/*`, `index.html`,
  or runs `git commit/push`. Validator may run `node --check`, `grep`, `python3`
  numeric recompute, `git diff --stat`, and the repo's own `tools/final_boot.js`
  boot-check harness (A13 only, code QA, not a playtest).
- NO harness/headless-browser page loads beyond the repo's existing
  `final_boot.js` script (which is the repo-law boot check, already used in
  wake-39 P1-4a). Nicko's playtest is the acceptance bar.
- Validation output lands in `io/specs/p1-7-atmosphere-verdict.md` (created
  by the validating Testerbot, not this file).

File abbreviations used below:
- GJS   = `prototype/js/game.js`
- RMJS  = `prototype/js/region-manager.js`
- CFGJS = `prototype/js/CONFIG.js`
- VENDOR = `prototype/vendor/three.classic.js`
- BUILD = the built v8 output produced by `tools/build_v8.py`

The spec maps V-numbers to the IO spec's acceptance rows A1..A18.

---

## 1. Chunk-splice presence + verbatim structure (static grep on GJS and the BUILD bundle)

V1 (build artifact): Run `cd /tmp/wh-worldfeat && python3 tools/build_v8.py`. PASS iff exit 0
and the build summary reports success. If the build fails at any step, FAIL here and stop.
(Maps to A13, first half.)

V2 (marker presence): `grep -c "WH_ATMO_V1" GJS` must be >= 1. Then grep the
BUILD bundle produced by `build_v8.py` (path printed in build output) for `WH_ATMO_V1`
— count >= 2 (must appear in both the patched `fog_fragment` and `fog_pars_fragment`
splice strings). Note: the spec names the marker `WH_ATMO_V1`; the spec's own wording
"version 'WH_ATMO_V1'" is the canonical marker. (Maps to A1, A14 partially.)

V3 (fused install call + ordering): In GJS, `WH_installAtmoChunks()` must be
defined AND invoked at the top of `setupScene()` BEFORE `scene.fog = new THREE.FogExp2(...)`
(which lives at GJS:136 today). `grep -n "WH_installAtmoChunks" GJS` must show both a
`function WH_installAtmoChunks` and a call site; the call site's line number must be
smaller than the `setupScene` line containing `scene.fog = new THREE.FogExp2`.
(Maps to §1 "At the TOP of setupScene()".)

V4 (boot-time marker truth): GJS should declare `window.WH_ATMO = { installed: false,
version: 'WH_ATMO_V1', recedeState: 1.0, cardsBuilt: 0, originals: {...} }` at
module scope near setupScene. `grep -n "WH_ATMO" GJS` must show a module-scope
initializer. PASS iff present. (Maps to A14.)

V5 (six atmo consts in fog_pars_fragment splice): In the spliced
`fog_pars_fragment` string in GJS (the JS string assigned to
`THREE.ShaderChunk.fog_pars_fragment`), all six const names must appear exactly once:
`atmoYBase`, `atmoYScaleInv`, `atmoYMinFrac`, `atmoMoonTint`, `atmoMoonCol`,
`atmoMoonDir`. Verify with six greps (each count = 1) inside the patch block only —
these names must NOT appear anywhere else in the file. Cross-check: `grep -rn
"atmoYBase\|atmoYScaleInv\|atmoYMinFrac\|atmoMoonTint\|atmoMoonCol\|atmoMoonDir"
prototype/` returns hits ONLY inside GJS's atmos splice function. (Maps to A4+A5.)

V6 (guarded varyings): the `fog_pars_vertex` splice in GJS must contain the
substring `varying vec3 vWhFogPos;` inside its own `#ifdef USE_FOG ... #endif`
guard. The `fog_pars_fragment` splice must also contain `varying vec3 vWhFogPos;`
likewise guarded. Verify the guard opens and closes within the appended block:
in each splice string the appended text must begin after the original chunk
text and open a NEW `#ifdef USE_FOG`. (Maps to A4.)

V7 (`WH_ATMO_POS` define placement): In the begin_vertex splice the exact tokens
`#define WH_ATMO_POS` and `vWhFogPos = whWorldPos;` must be present. `#define
WH_ATMO_POS` must appear BEFORE the assignment in the same string, and both must
sit between `#ifdef USE_FOG` and the matching `#endif`. (Maps to §1 "This is the
ONLY place vWhFogPos is written".)

V8 (begin_vertex compose order): in the splice GLSL the lines must be ordered:
`#ifdef USE_INSTANCING` transforms `whW4` FIRST, then `modelMatrix * whW4`.
The exact two statements (whitespace may differ):
`whW4 = instanceMatrix * whW4;` and `vec3 whWorldPos = ( modelMatrix * whW4 ).xyz;`.
Verify order by line position in the string. (Maps to A3.)

V9 (vendor non-exp2 branch byte preservation): The ORIGINAL vendor fog_fragment
non-exp2 branch is:
`#else\\n\\t\\tfloat fogFactor = smoothstep( fogNear, fogFar, vFogDepth );\\n\\t#endif\\n\\tgl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );`.
In the patched `fog_fragment` string in GJS, the smoothstep line and the non-exp2
`mix` line must BOTH be present verbatim (they may be moved/rewrapped, but the
smoothstep formula and the mix call's argument names/order must be unchanged).
PASS iff both substrings `smoothstep( fogNear, fogFar, vFogDepth )` and
`mix( gl_FragColor.rgb, fogColor, fogFactor )` appear. (Maps to A2.)

V10 (vendor exp2 fallback preserved for sprite-class): in the patched
`fog_fragment` the `#else` branch of `#ifdef WH_ATMO_POS` must contain the
un-modified exp2 mix:
`float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );`
followed by `gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );`
(without `atmoC`). Grep for both substrings. (Maps to §1 sprite-class fallback.)

V11 (fog_vertex untouched): the GJS atmos-install function must NOT write
`THREE.ShaderChunk.fog_vertex` at all. `grep -n "ShaderChunk.fog_vertex" GJS`
must return ZERO hits. (Spec law: fog_vertex is untouched.)

V12 (no other ShaderChunk patch anywhere): search the entire prototype tree.
`grep -rn "ShaderChunk\\." prototype/js prototype/*.html | grep -v "WH_installAtmoChunks\|atmos\|WH_ATMO"`
must return ZERO hits outside the atmos function body, and
`grep -rn "ShaderChunk\\." prototype/js` may only show hits for the four names
`begin_vertex`, `fog_pars_vertex`, `fog_fragment`, `fog_pars_fragment` (the
patched set). PASS iff no other chunk name is written. (Maps to §1 zero per-material cost
law, §12 "no ShaderChunk patch anywhere else".)

V13 (vendor byte-identical): `cd /tmp/wh-worldfeat && git diff --stat prototype/vendor/three.classic.js`
must print NOTHING (empty diff). Also `git hash-object prototype/vendor/three.classic.js`
must equal the committed blob hash from `git ls-tree HEAD prototype/vendor/three.classic.js`.
(Maps to A12.)

V14 (no new script file; index.html unchanged):
`git diff --stat -- index.html prototype/index.html` (whichever exists) must be empty.
`git status --porcelain prototype/js prototype/index.html` must NOT list any `??`
(untracked) new `.js` file under `prototype/js`. (Maps to A12.)

V15 (edit scope — A18 hard gate): `cd /tmp/wh-worldfeat && git diff --stat HEAD`
lists ONLY: `prototype/js/game.js`, `prototype/js/region-manager.js`,
`prototype/js/CONFIG.js`, plus spec/doc files under `io/specs/` (and the build
summary). If ANY other `prototype/` path appears in git diff or git status
(except untracked spec/markdown files), FAIL.

## 2. CFG.atmos row (b — field presence)

V16: In CFGJS, the row `atmos: {` exists. `grep -n "atmos: {" CFGJS` returns
exactly 1 hit. The block must contain ALL of these keys exactly once each:
- `heightFog:`
- inside heightFog: `enabled`, `yBase`, `yScale`, `minFrac`, `moonTint`,
  `moonColorHex`
- `mistCards:`
- inside mistCards: `enabled`, `regionId`, `count`, `yMin`, `yMax`,
  `sizeMin`, `sizeMax`, `opacityMin`, `opacityMax`, `colorHex`, `radiusFrac`,
  `seed`
- `recede:` with `enabled`, `mult`, `lerpRate`
The tick-budget field: spec lists an atmos tick budget row; verify the atmos
block carries a numeric per-frame budget field (spec calls it "tick budget";
accept the name `tickMs`, `perFrameMs`, `tickBudgetMs` — any ONE of these
must be present as a numeric row inside `atmos:`). If none of those keys
exist under atmos, FAIL with a note "tick budget row missing".

V17: `CFG.mistPlane` row still exists and remains `enabled: true` (rollback
path preserved). `grep -n "mistPlane" CFGJS | head` returns the row block with
`enabled: true` unchanged. (Maps to §5 note "mistPlane row stays").

V18: Existing CFG keys unchanged: `git diff HEAD -- prototype/js/CONFIG.js`
shows ONLY added lines (`+`) inside the atmos block plus comment lines; no
`-` line deletes a pre-existing CFG row. PASS iff zero deletions of prior
rows. (Maps to A18.)

## 3. Static JS checks (c)

V19 (tick order law): In GJS the loop section near line 3445-3455 must call
`applyDayNight();`, then `regionFadeTick(dt);`, then `cemeteryFogTick();`,
then `skyTick();`, then `atmosphereTick(dt);`. `grep -n "skyTick();\|atmosphereTick(dt);\|cemeteryFogTick();\|regionFadeTick(dt);\|applyDayNight();" GJS`
must show those five lines in that relative order, all within the same enclosing
tick block (contiguous, no unrelated fog writer between them).

V20 (install call before first render): In GJS the function body of
`setupScene()` (starts around line 132) must contain the
`WH_installAtmoChunks()` call TEXTUALLY BEFORE the line `return scene;` and
before `scene.fog = new THREE.FogExp2(...)` at line 136. Confirm by
reading `sed -n '130,150p' GJS` — the call line number must be < 136 and inside
setupScene. (The scene does not exist before setupScene, so "before first
scene render" is enforced by code position inside setupScene.)

V21 (mist-plane block ending state — spec §6/§3): The pre-P1-7 mist-plane
block (RMJS 2066-2086 today, building `name='mist-plane'`, `cfg=CFG.mistPlane`,
region-gated `darkwood_edge`, PlaneGeometry of `whVisualGroundRadius*2`,
`transparent: true`, `depthWrite: false`, `DoubleSide`,
`opacity = opacityX100/100`) must be REPLACED BY a branched block that:
- reads `CFG.atmos.mistCards` FIRST;
- when `mistCards.enabled && regionId === mistCards.regionId`, calls
  `buildMistCards(regionId)` (new function) and does NOT create the plane;
- otherwise (flag-off or non-matching region) executes the ORIGINAL plane
  construction code unchanged (byte-preserved inner statements).
EXACT ENDING STATE the spec mandates: `grep -c "buildMistCards" RMJS` >= 2
(call + definition); `grep -n "name = 'mist-plane'" RMJS` returns exactly 1
hit inside the flag-off branch only; the `if (mistCfg && mistCfg.enabled && regionId === mistCfg.regionId)`
plane-build block remains present and reachable (not deleted) so the rollback
path still builds the legacy plane when cards are off. (Maps to A8 + A16.)

V22 (card build law conformance): In the new `buildMistCards` function body
(grep its definition and read the full block):
- exactly `CFG.atmos.mistCards.count` entries are built;
- one shared `THREE.CanvasTexture` created ONCE per build call (no texture
  per card);
- each card uses `new THREE.SpriteMaterial({ color: mistCards.colorHex,
  transparent: true, opacity: <row-driven>, depthWrite: false, fog: false })`;
- `fog: false` and `depthWrite: false` appear verbatim in the material options;
- `blending: THREE.AdditiveBlending` (spec law: additive blending) appears;
- NO `uniforms:` key, NO `THREE.ShaderMaterial` for cards (cards are plain
  sprites);
- NO allocation inside any per-frame/tick callback (the builder runs only on
  region build; grep the build function for `setInterval`, `requestAnimationFrame`,
  must return 0 hits);
- placement is seeded: the function calls `whRng(seed ^ whHashStr('mist-cards'
  + ':' + regionId))` or an equivalent seeded stream mirroring the
  stream() pattern at RMJS:1101 (verify either the seed XOR pattern or the
  `stream(...)` helper use with a mist layer key).
(Maps to A9.)

V23 (deterministic placement literals): inside `buildMistCards`, per-card y must
be drawn from `[mistCards.yMin, mistCards.yMax]` and size from `[mistCards.sizeMin,
mistCards.sizeMax]` and opacity from `[mistCards.opacityMin, mistCards.opacityMax]`,
with x,z inside a disc of `mistCards.radiusFrac * whVisualGroundRadius(regionId)`
centered on the region center (same anchor the plane used). Grep each row name
inside the function body. (Maps to A9.)

V24 (group ownership): `buildMistCards` must call `group.add(sprite)` for each
card on the SAME `group` node the legacy plane block used. Grep inside the
function for `group.add(`; count equals count row (or the loop is explicit).
(Maps to §3 "Group ownership ... auto disposal".)

V25 (lock-recede state ownership): `atmosphereTick(dt)` (GJS, defined near
cemeteryFogTick, ~1415-1450 zone) must satisfy:
- NEVER assigns an absolute value to `game.scene.fog.density` —
  grep inside the function body; the only assignment to density is of the form
  `game.scene.fog.density = game.scene.fog.density * atmoRecede;`
  (multiplier-only law: RHS reads current density, multiplies by the eased
  state).
- reads `game.player.lockTarget` (grep for `lockTarget` inside the function);
- module-scoped state variable (e.g. `var atmoRecedeState = 1.0`) declared
  OUTSIDE the function body; NOT allocated per call (no `new` inside the tick);
- eased step: `state += (target - state) * Math.min(1, dt * CFG.atmos.recede.lerpRate)`
  with `target = (game.player.lockTarget ? CFG.atmos.recede.mult : 1.0)`;
  clamped to `[CFG.atmos.recede.mult, 1.0]`;
- on unlock (lockTarget falsy) target returns to `1.0` and the multiplier
  restores density by multiplying by a state that eases back to exactly 1.0;
- `enabled: false` early-out: the function returns (or skips the multiply)
  after a single comparison when `CFG.atmos.recede.enabled === false` OR
  `CFG.atmos.recede` is missing; the zero-allocation law holds on that path.
(Maps to A10, §4.)

V26 (no new writer of scene.fog color/density — regression wall):
`grep -rn "scene.fog.color\s*=\|scene.fog.density\s*=" prototype/js prototype/*.html`
must return hits ONLY at these 5 legal sites (line numbers recorded at wake-40
baseline, may drift slightly but function names must match):
1. `game.js` `applyRegionLighting` (~1398-1399)
2. `game.js` `cemeteryFogTick` (~1444-1445)
3. `game.js` `regionFadeTick` (~1583-1584)
4. `game.js` `applyDayNight` denFade block (~1827-1828, the `S.fog[rid]`
   day-phase writes)
5. `game.js` `atmosphereTick` — and ONLY the multiplier line from V25.
If ANY other file or function contains a `scene.fog.color =` or
`scene.fog.density =` assignment, FAIL with the file:line. (Maps to §7 +
regression wall.)

V27 (flag-off equivalence path): In `WH_installAtmoChunks` (GJS):
- the function MUST capture the FOUR original chunk strings
  (`begin_vertex`, `fog_vertex` is untouched so originals =
  `{begin_vertex, fog_pars_vertex, fog_fragment, fog_pars_fragment}`)
  at module scope BEFORE any patch (grep the function body for a capture of
  `THREE.ShaderChunk.<name>` into `WH_ATMO.originals` or an equivalent
  module-scope holder BEFORE the assignment `THREE.ShaderChunk.<name> =`);
- when `CFG.atmos.heightFog.enabled === false` the function returns WITHOUT
  writing any of the four chunks (grep the body: the guarded return happens
  before all assignments);
- flag-off path performs ZERO allocation beyond the early return
  (no `+`, no `.concat`, no `new` before the enabled check).
- When `enabled === false`, `WH_ATMO.installed` is set to `false`
  and `window.WH_ATMO.recedeState` is forced to `1.0`.
(Maps to A7.)

V28 (atmosphereTick observability): grep GJS for `WH_ATMO.recedeState`. The
tick must write `WH_ATMO.recedeState = atmoRecedeState;` (or equivalent) once
per call WITHOUT new object allocation. `WH_ATMO.cardsBuilt` must be set by
`buildMistCards` (grep RMJS) to the count actually built. (Maps to A14.)

## 4. Numeric / bake-formula checks (d)

V29: Recompute each GLSL literal that the splice bakes and verify the JS-side
bake matches the spec formula to 1e-6:
- `atmoYBase` literal equals `CFG.atmos.heightFog.yBase` (= 0.0);
- `atmoYScaleInv` literal equals `1.0 / CFG.atmos.heightFog.yScale` —
  with `yScale = 6.0`, expected literal `0.166667` (6-decimal toFixed)
  i.e. recomputed 0.16666666... rounded to 6 dp; PASS iff |literal - 1/yScale|
  <= 1e-6;
- `atmoYMinFrac` equals `CFG.atmos.heightFog.minFrac` (0.35);
- `atmoMoonTint` equals `CFG.atmos.heightFog.moonTint` (0.45);
- `atmoMoonCol` equals `new THREE.Color(0x778da9)` components:
  r=0.466667, g=0.552941, b=0.662745 — each component of the GLSL vec3 literal
  must be within 1e-6 of `((hex >> shift) & 0xff) / 255`;
- `atmoMoonDir` is the normalized moon-light direction composed EXACTLY as the
  game.js moon-light position formula at GJS:152-158 (az from
  `CFG.lighting.moonAzimuthDeg` = 0, el from `moonElevationDeg` = 30, dir
  from `moonDirectionDistance` = 60); the rounded moon position is
  (0.0, 30.0, -52.0); normalize to (0.0, 0.499722, -0.866186). The GLSL
  `atmoMoonDir` literal must equal those components to 1e-6, and the
  validator MUST document handedness: verify against the vendor
  right-handed camera convention (x=east, y=up, z toward viewer, -z forward)
  by confirming `pz = -cos(az)*cos(el)*dir` (negative-z forward at az=0,
  matching GJS:158's negation of the z term). Record the handedness note in
  the verdict; if the sign of any axis differs from the recompute, FAIL.
(Maps to A5 + A6.)

V30 (dot-product sanity): independently recompute in a scratch script
(`python3`) the normalized moonDir and dot it against
`normalize(moonLight.position)`. Expected |dot - 1.0| <= 1e-6. Include the
recompute numbers in the verdict. (Maps to A6.)

V31 (MIST-LAWN guard for yScale): `atmoYScaleInv` must NEVER be zero or
negative infinity; with `yScale > 0` asserted at config-load time (or guard
in `WH_installAtmoChunks`: `if (!yScale || yScale <= 0) yScale = 1e-3` or
spec-mandated "ground-variant half-range" baked in). The spec requires the
bake to use a yScale that includes the ground-variant half-range so a
perfectly flat world cannot bake yScale=0. Grep GJS for the guard or the
half-range term in the yScale bake expression; PASS iff the baked yScale is
provably non-zero for the current region rows. (Maps to §3 MIST-LAWN law.)

V32 (literals decimal-safe): every float literal embedded in the spliced GLSL
strings must come through `.toFixed(6)` or equivalent decimal rendering (no
scientific notation, no `e-` forms). Grep the splice block for `/\de[+-]\d+`
patterns; PASS iff 0 hits. (Maps to §1 "All literals decimal-safe via toFixed(6)".)

## 5. Regression wall (e)

V33 (4 fog-writer bodies byte-identical): extract the function bodies of
`applyRegionLighting`, `cemeteryFogTick`, `regionFadeTick`'s fog block, and
the `applyDayNight` denFade block from HEAD (`git show HEAD:prototype/js/game.js`)
and from the working tree. Each function body must be byte-identical between
HEAD and the working tree (use `git diff -U0 -- prototype/js/game.js` and
confirm the diff hunks do NOT touch the body of any of those four functions).
PASS iff zero diff lines fall inside their bodies. (Maps to A11.)

V34 (skyTick & setupScene rest untouched): the rest of `setupScene()` after
the atmos install call, `scene.background` assignment, `boot()`, and
`skyTick()` body must be unchanged from HEAD. Same diff-scope check as V33.
(Maps to §7.)

V35 (no edits to player.js/enemy.js/vendor/etc.): enforced by V15 file-list
gate; additionally `git diff --stat HEAD -- prototype/js/player.js prototype/js/enemy.js prototype/vendor/`
must be empty. (Maps to A12 + §7.)

V36 (index.html script order unchanged): `git diff HEAD -- prototype/index.html`
(or the actual entry HTML path) must be empty. (Maps to A12.)

V37 (boot check — repo-law A13, second half): after a successful build (V1),
run the repo's existing boot QA harness `node tools/final_boot.js` (or the
equivalent harness named in tools/README) against the built file. PASS iff
the harness reports 0 pageerrors, the "51 critical assets" boot barrier
passes with 0 stand-ins, and 0 GLB 4xx entries. Record the raw stdout tail in
the verdict. This is the ONLY harness execution allowed this round; NO other
headless-browser smoke test is permitted — Nicko's playtest is the acceptance
bar and Testerbot does not replicate it.

V38 (M-17 binding — structural): with cards enabled, verify by greps that
no single mesh named `'mist-plane'` is built for `darkwood_edge` when
`mistCards.enabled === true` (the branch in V21 ensures the plane mesh is
skipped in the cards path). This is a static code-path proof, not a runtime
render check. (Maps to A16.)

V39 (M-10 binding — static): the CFG recede row exists with `mult: 0.55` and
`lerpRate: 3.0`; the height-fog chunk reads `fogDensity` (the SAME uniform
the 4 legal writers own); the splice's `atmoD` computation uses `fogDensity`
on the right-hand side. Grep the fog_fragment splice for `fogDensity` — it
must appear on the RHS of the `atmoD` assignment, so the recede multiplier
affects BOTH the flat and the layered path. (Maps to A17.)

---

## EXECUTION NOTE — how the validating Testerbot runs this file

Check classes
- **Static-grep only (allowed, no execution needed):** V2-V18, V21-V29,
  V31-V36, V38-V39. Each verdict = PASS/FAIL + the grep command run + the
  exact output (or a 1-line excerpt). Grep from `/tmp/wh-worldfeat`. NEVER
  edit files to "fix" a failed check — FAIL and report.
- **JS parse check (node --check only):** After V1 build, run
  `node --check <built bundle path>` to prove the bundle parses. PASS iff exit
  0. This is the ONLY node execution allowed besides final_boot.
- **Harness check (exactly one, A13):** V1 (`build_v8.py`) and V37
  (`final_boot.js`) only. NO additional page loads, NO headless browser, NO
  puppeteer-style smoke. Primary law: Nicko's playtest is the acceptance bar.
- **Numeric recompute (python3 stdlib only, no npm):** V29, V30. Emit the
  recomputed values into the verdict file so a later validator can re-verify.

Recording each verdict
- One row per V-number in `io/specs/p1-7-atmosphere-verdict.md`:
  `| V1 | PASS | <cmd> | <observed output / excerpt> |`.
- End with a summary block: how many PASS / FAIL / SKIP (SKIP only allowed
  when a check's prerequisite — e.g. the build — already FAILED; record the
  blocking V-number).
- Verdict = PASS iff every V1..V39 is PASS or explicitly SKIPPED-under-a-
  failed-parent. Otherwise verdict = FAIL with the list of failing V-numbers
  at the top of the file.

## STRESS questions for the validator (record answers in the verdict file)

S1. M-10 readability at full lock-on recede: with `mult: 0.55` and base
`fogDensity` 0.012 (regionA row), eased-in density is 0.0066. Recompute the
exp2 fogFactor at distances 5 / 10 / 15 / 20 / 30 units for both the locked
and unlocked densities. Does the 25%-contrast threshold really move past 30
units while locked, and does it stay below the threshold at 15 units unlocked
(spec's M-10 floor)? If the recomputed numbers contradict the spec's claim,
flag the numbers — do not "fix" them.

S2. Additive-blend blow-out near the camera: the cards use AdditiveBlending
with `opacity` up to 0.10 and `sizeMax` 14 world units. If several cards
overlap the same screen region close to the camera, the additive sum can
exceed 1.0 on a dark navy background. From the seeded stream law, how many
cards can plausibly stack within a 1-viewport cone at minimum card-to-camera
distance? Is there any per-card attenuation (e.g. distance falloff) in the
material to keep sum <= 1? If none, record the worst-case additive sum over
the 9 cards and the spec's answer (or absence of one).

S3. lockRecede vs regionFadeTick race: `regionFadeTick` absolutely writes
`scene.fog.density` every crossfade frame, and `atmosphereTick` multiplies
"after" it in the same frame. During a 1.5 s crossfade initiated while the
player is locked on, the fade moves the base value while the recede eases
the multiplier. Does the composition (multiply on top of a moving base) ever
cause the visible density to OVERSHOOT the unlocked target mid-fade, or to
undershoot the locked target when the fade also lowers density? Trace one
frame numerically with both mid-fade (w=0.5) and locked states to see if
clamping or ordering is needed. Spec asserts "no interplay"; validate that
assertion with numbers, not wording.

S4. Sprite-material audit coverage: spec §8 requires every `SpriteMaterial(`
use in `prototype/js` to be audited. Grep the whole file set. How many call
sites default `fog: true` and would have hit the uninitialized-
`vWhFogPos` path before the fix? For sites that remain `fog: true` (i.e.
the spec's intended flat-exp2 fallback), confirm by reading the
corresponding shader (`sprite_vert` + `sprite_frag`) that `begin_vertex`
is NOT included so the WH_ATMO_POS define is absent — i.e. the fallback
branch is the compiled one. List any site where this cannot be proven
statically.

S5. WH_ATMO.originals as a rollback oracle: `WH_ATMO.originals` exposes the 4
captured pre-patch chunk strings. If a future round patches ANY of the same
four chunks, the equality check in V27 breaks silently (originals get
overwritten at install time). Is the capture idempotent — i.e. does the
install function refuse to overwrite already-captured originals on a second
invocation (`if (originals.begin_vertex) return` or equivalent)? If not,
document the failure mode for the IO wake to address.

---

## WAKE-40 AMENDMENT APPENDIX (IO, binding; supersedes conflicting rows above)

AA1 (replaces V29 numeric basis): atmoMoonCol is baked from
new THREE.Color(0x778da9).r/.g/.b — recompute against THREE.Color's actual
built semantics, NOT raw hex/255. atmoYScaleInv = 1/(yScale + hMax/2) =
1/8.5 = 0.117647 (V29's 0.166667 void; MIST-LAWN law).
AA2 (replaces V16 tick-budget clause): the CFG.atmos key set is FINAL as
built — no tick-budget row exists by design (Amend 4). V16 passes on key
presence of heightFog/mistCards/recede blocks with the exact keys listed in
Amend 4; its tickMs alternatives are void.
AA3 (replaces V17 + parts of V21): CFG.mistPlane's ending state = present
as the DATA ROW of the flag-off branch; its `enabled` value is
irrelevant to the verdict (Amend 5). The plane-build statements must remain
byte-preserved inside the else-branch; 'mist-plane' name string expected
exactly 1 hit in RMJS inside that branch.
AA4 (voids V37): NO boot harness this round. A13 = build exit 0 + bundle
markers + node --check on the three sources (Devbot already ran all three:
exit 0). Record in the verdict that V37 is SKIPPED-under-amendment, not
under a failed parent.
AA5 (V22 clarifications): the implementation signature buildMistCards
(regionId, group) is accepted (Amend 6). AdditiveBlending is NOT required
— Devbot used standard transparent alpha per the IO spec's SpriteMaterial
row; V22's additive clause is void. Per-card opacity drift is EXCLUDED
polish (static per-card opacity from the seeded stream is the round's
intent); V22's drift expectations are void. fog:false + depthWrite:false
verbatim requirements STAND. V28's WH_ATMO.cardsBuilt law stands.
AA6 (V25 clarifications): early-out may use the CFG.atmos master row OR the
recede row (function must be inert when EITHER is false — grep both
guards); multiplier-only law on the density assignment STANDS.
AA7 (V27 idempotence, from S5): the capture guard
`if (!whAtmoOriginals)` satisfies the refuse-to-overwrite law; verdict
notes confirm it wraps the ORIGINALS capture only, while chunk restoration
to originals re-runs on every install (correct: restore-then-patch).
AA8 (S2 answer, numbers for verdict): cards are transparent-alpha, opacity
<= 0.10 each, 9 cards worst-case full stack = 0.90 alpha cap — below 1.0,
no blow-out; record this computation.
AA9 (S3 answer): multiplier composition is commutative-safe: regionFade
moves the BASE while the recede multiplies; eased mult in [0.55,1] cannot
overshoot base (product <= base) nor undershoot below base*0.55; verdict
records one numeric trace (w=0.5 frame).
AA10 (S4 answer): wake-40 audit per Amend 2 — 4 fog-true sprite/point
sites all in the USE_SIZEATTENUATION class -> vendor fallback; stars/dome
custom ShaderMaterials outside fog; sizeAttenuation:false+fog:true = 0
instances. Residual risk configuration-dependent; S4 law stands.
AA11 (S5 recording): note the capture-guard idempotence in the verdict
(AA7 form).
AA12 (verdict rule): overall verdict = PASS iff every V1..V39 is PASS or
explicitly SKIPPED-under-amendment (AA4) or voided-by-amendment (V17,
V29's 0.166667, V37, V22-additive/drift clauses, V16 tick-budget clause).
