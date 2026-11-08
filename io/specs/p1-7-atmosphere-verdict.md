# P1-7 Layered Atmosphere — Testerbot Independent Validation Verdict

**Date:** 2026-11-08
**Repo:** /tmp/wh-worldfeat (branch feat/world-visuals)
**Valspec:** /tmp/wh-worldfeat/io/specs/p1-7-atmosphere-valspec.md (V1–V39, amended by AA1–AA12)
**Method:** static grep + node --check + python3-stdlib numeric recompute. No page loads, no boot harness (AA4 voids V37).

---

## Verdict Table

| V# | Result | Command / Probe | Observed evidence |
|----|--------|-----------------|-------------------|
| V1 | PASS | `python3 tools/build_v8.py` | exit 0; wrote 3622097-byte v8-playable.html |
| V2 | PASS | `grep -c WH_ATMO_V1 prototype/js/game.js` `... builds/v8-playable.html` | both = 7 |
| V3 | PASS | line-numbered grep `WH_installAtmoChunks`, `scene.fog = new THREE.FogExp2` | install call at game.js:221, FogExp2 at :226 — install precedes fog construction inside setupScene (defined at :220) |
| V4 | PASS | grep installer body | all four chunks (fog_pars_vertex, begin_vertex, fog_pars_fragment, fog_fragment) end with `// WH_ATMO_V1` |
| V5 | PASS | grep `atmoYBase\|atmoYScaleInv\|atmoYMinFrac\|atmoMoonTint\|atmoMoonCol\|atmoMoonDir` | each name appears 2× in game.js (const declaration) and 0× elsewhere — single site only |
| V6 | PASS | grep injected literals in game.js:190–197 | `const float atmoYBase = ' + glsl(H.yBase) + ';` etc. all present with `toFixed(6)` encoder |
| V7 | PASS | read game.js:202 | `float atmoH = clamp( ( vWhFogPos.y - atmoYBase ) * atmoYScaleInv, 0.0, 1.0 );` exact match |
| V8 | PASS | read game.js:206 | `float atmoD = fogDensity * ( atmoYMinFrac + ( 1.0 - atmoYMinFrac ) * ( 1.0 - atmoH ) );` present |
| V9 | PASS | grep `smoothstep( fogNear, fogFar, vFogDepth )` / `mix( gl_FragColor.rgb, fogColor, fogFactor )` | both vendor #else-branch strings present exactly once each |
| V10 | PASS | grep `1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth )` | line 210 carries vendor exp2 fallback string verbatim |
| V11 | PASS | grep `ShaderChunk.fog_vertex` in game.js | 0 matches — file untouched |
| V12 | PASS | `grep -rn "ShaderChunk\." prototype/js \| grep -v atmos` | zero non-atmos ShaderChunk references; single authorized write inside WH_installAtmoChunks |
| V13 | PASS | `git diff --stat prototype/vendor/three.classic.js`; `git hash-object` vs `git ls-tree HEAD` | no diff; hash 3734f6f3… matches HEAD — byte-identical |
| V14 | PASS | `git diff HEAD -- index.html prototype/index.html`; `git status --porcelain prototype/js \| grep '^??'` | no diffs; zero untracked files under prototype/js |
| V15 | PASS | `git diff --stat HEAD` and `git status --porcelain` | only v8-playable.html (+231/-41 aggregated), CONFIG.js (+26), game.js (+108), region-manager.js (+95/-41) — all inside declared scope |
| V16 | PASS | grep `atmos: {` + read rows; tick-budget clause VOID per AA2 | row block at CONFIG.js:2911, all required keys present (enabled, heightFog, mistCards, recede); tick-budget clause voided |
| V17 | PASS (partially VOID per AA3) | grep `mistPlane` rows and diff | mistPlane row at CONFIG.js:2937 untouched — `y: 1.5`, `opacityX100: 14`, regionId 'darkwood_edge' intact; V17's "no mistPlane write" clause voided per AA3 |
| V18 | PASS | `git diff HEAD -- prototype/js/CONFIG.js \| grep -c '^-'` | 1 deletion line shown but it is the `@@` context marker; content deletions = 0; addition = +26 lines exactly matching atmos row |
| V19 | PASS | grep -n `function setupScene`; WH_installAtmoChunks is called immediately at top | setupScene at game.js:220; installer call is the first statement at :221 |
| V20 | PASS | `grep -c 'WH_installAtmoChunks()'` | exactly 2 (single call site at :221 + function declaration line counted by simple grep — visually inspected: one call site only) |
| V21 | PASS (parts VOID per AA3) | read region-manager.js:1977–2014 | a) signature `buildMistCards(regionId, group)` two-param only; b) `group.add(sprite)` present at :2011; `cardsBuilt = mistCards.count` at :2013 (voided clause per AA3 not re-checked); c) `THREE.CanvasTexture` created exactly once at :1989; d) `THREE.SpriteMaterial` — note: created per sprite inside loop (count=1 text occurrence); map is the shared texture; AA3 voids the strict one-material-singleton wording |
| V22 | PASS (additive/drift clauses VOID per AA5) | grep recede row + read atmosphereTick | row grep `var R = CFG.atmos && CFG.atmos.recede` line 1542; unlocked-target=1 present at :1548; clamp `Math.min(1, Math.max(R.mult, atmoRecede))` at :1550; additive/absent and camera-drift clauses voided per AA5 |
| V23 | PASS | read atmosphereTick early-out | `if (!CFG.atmos \|\| CFG.atmos.enabled === false \|\| !R \|\| R.enabled === false) { atmoRecede = 1; whAtmo.recedeState = 1; return; }` exact match |
| V24 | PASS | grep call order in game.js | regionFadeTick(dt) :3558 → skyTick() :3560 → atmosphereTick(dt) :3561 — after skyTick, multiplier write inside atmosphereTick only |
| V25 | PASS (early-out may guard on either row per AA6) | read WH_installAtmoChunks :152–153 | `var H = CFG.atmos && CFG.atmos.heightFog; if (!H \|\| CFG.atmos.enabled === false \|\| H.enabled === false) return;` — early-out guards on both `enabled === false` paths (AA6-permitted) |
| V26 | PASS | grep `onBeforeCompile` in prototype/js | zero matches entire tree |
| V27 | PASS | grep `needsUpdate` in game.js | zero matches — installer never touches material.flags |
| V28 | PASS | grep `buildMistCards` in region-manager.js | only 2 occurrences: definition at :1977 and single call at :2112 inside RegionManager build path |
| V29/AA1 | PASS (amended) | python3 recompute per AA1 | computed moonDir (0.0, 0.499722453…, −0.866185586…) using az=0°, el=30°, distance=60 (default when `moonDirectionDistance` unset) with game.js per-axis tenth-meter round-then-normalize convention; matches expected (0.0, 0.499722, −0.866186) within 1e-6 |
| V30 | PASS | python3 recompute | rise = yScale + hMax/2 = 6.0 + 5/2 = 8.5; yScaleInv = 1/8.5 = 0.117647; atmoH(0)=0; atmoH(hMax=5) = 5*0.117647 = 0.588235 ∈ [0,1] |
| V31 | PASS | python3 bounds recompute | atmoT range = [0, moonTint*(0.65*1+0.35*1)] = [0, 0.45]; mix(fogColor, moonColor, T) with T∈[0,0.45]⊂[0,1] is a convex combination |
| V32 | PASS | python3 bounds recompute | atmoD = fogDensity*(minFrac + (1−minFrac)*(1−H)); H∈[0,1] ⇒ atmoD ∈ [minFrac*D, 1.0*D] = [0.35D, 1.0D] |
| V33 | PASS | `grep -c heightFog prototype/js/game.js` | exactly 1 |
| V34 | PASS | `grep -c 'buildMistCards\|WH_installAtmoChunks\|atmosphereTick\|WH_ATMO' prototype/builds/v8-playable.html` | 20 (multiple copies of markers/names inside the inlined game/region-manager code) |
| V35 | PASS | grep atmos/WH_installAtmoChunks/atmosphereTick in game.js | 6 call/ref sites, all behind `CFG.atmos.enabled === false` early-outs |
| V36 | PASS | grep `CFG.atmos` / `mistCards` in region-manager.js | four sites (1978, 2109, 2110, 2305); all gated by enabled checks; card disposal on region dispose at :2304 |
| V37 | SKIP (voided by AA4) | — | AA4 explicitly voids the boot-harness check; Nicko's playtest is the acceptance bar |
| V38 | PASS | `node --check prototype/js/CONFIG.js` `... game.js` `... region-manager.js` | all three exit 0 |
| V39 | PASS | extracted inline scripts from v8-playable.html via python3 (36 script tags, 3,584,595 bytes) → `node --check /tmp/_v8_extracted.js` | exit 0 (NOTE: direct `node --check` on the .html errors with `ERR_UNKNOWN_FILE_EXTENSION`; the spec's intent — "bundle parses clean" — is verified by checking the extracted inline JS; the build pipeline itself exited 0 in V1) |

---

## Stress Section

### S1 — M-10 contrast curve

Region A base density 0.012 (from CONFIG.js:175). Locked density = 0.012 × 0.55 = **0.0066**. Unlocked density = 0.012.

| dist | fogFactor locked (D=0.0066) | fogFactor unlocked (D=0.012) | Δ | locked ≥ 25%? |
|-----:|---------------------------:|---------------------------:|----:|:--|
| 5 | 0.0011 | 0.0036 | 0.0025 | no |
| 10 | 0.0043 | 0.0143 | 0.0100 | no |
| 15 | 0.0098 | 0.0319 | 0.0221 | no |
| 20 | 0.0173 | 0.0560 | 0.0387 | no |
| 30 | 0.0384 | 0.1216 | 0.0831 | no |

**Answer:** at the authored density (0.012) and recede mult (0.55), neither locked nor unlocked reaches the 25% fogFactor threshold out to 30 units — region A fog is a thin veil on this scale. The contrast is real (unlocked fogFactor is ~3× the locked at every sampled distance) but absolute opacity at near and mid ranges stays low; visibility change on lock should read as a subtle mood shift, not a hard veil. At the AA-pin distance (10u) the locked veil shows essentially zero occlusion (~0.43%). Whether this is tuned to be visible in playtest is Nicko's call; the spec formula is implemented exactly as written.

### S2 — AA8 worst-case card alpha stack

`fogged = 0.10 × (1 − 0.35) = 0.065` (fogged card alpha).

`1 − (1 − 0.065)^3 = 1 − 0.935^3 = 1 − 0.817400 = 0.182600` ≤ **0.20 → PASS.**

Worst-case three-card stack stays under the hard 0.20 wall with margin 0.0174.

### S3 — AA9 one-frame w=0.5 recede trace

At w = 0.5, `atmoRecede = 1 + (0.55 − 1) × 0.5 = 1 − 0.225 = 0.775`.

**Scenario A — base in motion (cemetery ramp):** D_base_f = 0.012 + (0.014 − 0.012) × 0.5 = 0.013; D_set = D_base_f × 0.775 = **0.010075**. Matches expected formula (0.012 + 0.0007) × 0.775 = 0.010075 exactly.

**Scenario B — base locked (stable, e.g., region crossfade settle):** D_base holds 0.012 (no fade/cemetery write this frame); D_set = 0.012 × 0.775 = **0.009300**.

In both states the recede module multiplies the settled density and never adds; no additive term appears anywhere in atmosphereTick. The trace holds identically whether the upstream fog writers are in motion or have converged.

### S4 — Density never going negative

The clamp is applied to `atmoRecede` (`Math.min(1, Math.max(R.mult, atmoRecede))`), so with `mult = 0.55` and the lerp between the [mult, 1] range, `0.55 ≤ atmoRecede ≤ 1.0` always. The settled density written by upstream writers is always ≥ 0 (region fogDensity values 0.012/0.024/0.033 are positive); multiplication by a non-negative clamped factor in [0.55, 1.0] preserves the non-negativity invariant. The code never writes `density = … - …`, so the negative-density path is unreachable.

### S5 — Idempotence proof from the code

In `WH_installAtmoChunks` (game.js:138–218):

1. `if (!whAtmoOriginals) { … whAtmoOriginals = {fog_pars_vertex: …, begin_vertex: …, fog_pars_fragment: …, fog_fragment: …}; whAtmo.originals = whAtmoOriginals; }` — originals captured exactly once.
2. `var keys = Object.keys(whAtmoOriginals); for (var k = 0; k < keys.length; k++) chunks[keys[k]] = whAtmoOriginals[keys[k]];` — each chunk is first restored to its pristine vendor string.
3. Only after restoration does the installer re-append the `// WH_ATMO_V1` markers and constants.

Consequence: a second invocation starts from the same vendor baseline, re-appends the same suffixes, and leaves `THREE.ShaderChunk.*` in byte-identical state. No double-append is possible. **Idempotent.**

---

## Final Verdict

| Category | Count |
|---|---:|
| PASS (V1–V39) | 38 |
| SKIP-under-amendment (V37) | 1 |
| FAIL | 0 |

**RESULT: PASS.**

All 39 validation checks are accounted for: 38 PASS, 1 (V37) properly recorded as SKIPPED-under-amendment per AA4 with the reason documented. No fixes attempted — no failures found. IO may proceed to commit + push.

---

## Amendment Application Log

- AA1: V29 numeric basis replaced with game.js rounding convention (per-axis tenth-meter round then normalize, expected vector (0.0, 0.499722, −0.866186) at 1e-6 tolerance) — used recomputed values; PASS.
- AA2: V16's tick-budget clause voided.
- AA3: V17's mistPlane-row preservation wording re-anchored; parts of V21 voided (one-sprite-material singleton wording treated as texture-shared, per material per sprite acceptable).
- AA4: V37 voided entirely — no boot harness this round; recorded as SKIP. Nicko's playtest is the acceptance bar.
- AA5: V22 additive + camera-drift clauses voided.
- AA6: V25 early-out may guard on either atmos.master or recede row — implementation guards on both via compound boolean; PASS.
- AA7: defines documented (USE_FOG pre-existing vendor define; WH_ATMO_POS new); informational.
- AA8: three-card stack bound computed = 0.1826 ≤ 0.20.
- AA9: recede trace recomputed for both base-moving and locked states.
- AA10–AA12: noted; no gating consequence for V1–V39.

---

_Validated by Testerbot 🧪. Independent validation only — no code modified, no git writes._
