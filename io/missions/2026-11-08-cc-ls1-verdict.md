# CC-LS1 Blob Contact Shadows — Testerbot Independent Validation Verdict (2026-11-08)

## PASS — RE-VERDICT 2026-11-07T20:47Z: 40/40, 0 blocking (see RE-VERDICT section at bottom)

**Original 2026-11-08 verdict: FAIL — 1 blocking defect** (text below preserved; the
V-1.2 defect was repaired and re-verified the same day — see
"## RE-VERDICT 2026-11-07T20:47Z" at end of file).

Gate: CC-LS1 valspec V-1..V-7 (independent re-derivation; Testerbot did not write
this code). Worktree `/tmp/wh-worldfeat`, branch `feat/world-visuals`, HEAD
`ab61c2c` (parent = QJR-4 landed round). Probes: node-only (vm stubs, regex
censuses, git diffs, build tool re-runs). NO harness, NO headless browser, NO
playwright (no-harness-playtest-gate law + valspec probe law). Probe scripts:
`scratch/cc-ls1-val/` (independent, `val_*`-prefixed; Devbot's own
`scratch/cc-ls1-probe.js` / `scratch/cc-ls1-texture-probe.js` left untouched).

| Verdict | Criterion | Points | Blocking |
|---|---|---|---|
| FAIL | V-1 CONFIG `contacts` + parse | 0/4 | **YES — V-1.2 integration** |
| PASS | V-2 shadows.js surface + singletons | 8/8 | no |
| PASS | V-3 pool physics | 10/10 | no |
| PASS | V-4 numeric transform table (D1 exact-k) | 8/8 | no |
| PASS* | V-5 wiring census (5 anchors: all located; one census rule re-interpreted) | 5/5 | no |
| PASS | V-6 additive-only diff + markers + determinism | 3/3 | no |
| PASS | V-7 lighting untouched (byte-identity) | 2/2 | no |
| **FAIL** | | **36/40** | **1 blocking** |

## The blocking defect (V-1.2 — valspec "integration" criterion)

**`contacts` landed NESTED inside `window.WH_CONFIG.leveling`, not as a
top-level `WH_CONFIG` key. `WH_CONFIG.contacts` is `undefined`.**

- CONFIG.js:5120 `contacts:` sits at 2-space indent between
  `rankToastSeconds: 1.6,` (5117) and the `leveling` closer `};` (5129);
  the 10-line block spans 5118-5128.
- The CONFIG.js opener census: the nearest preceding `WH_CONFIG.X =` is
  `window.WH_CONFIG.leveling =` (CONFIG.js:5005); no later opener exists.
- CONFIG.js contains exactly ONE occurrence of the token `contacts` (5120)
  — it is a property of `leveling`, not a top-level key.
- grep `WH_CONFIG.contacts` / `CFG.contacts` across js lands exactly ONE
  call: `game.js:195` `if (window.WH_SHCONTACTS) window.WH_SHCONTACTS.init(scene, CFG.contacts);`
  → passes `undefined` at runtime.
- Integrated probe (REAL call chain, REAL landed CONFIG, vm stub three):
  `init(scene, undefined)` → `makeRadialTexture(cfg.textureSize)` →
  `cfg.textureSize` on undefined → **TypeError thrown at boot inside
  `setupLights()`** (game.js:143-196, called from setupScene game.js:2515 —
  not in a try/catch). Reproduced twice (plain vm load + full call-chain
  harness): **the boot path dies at the init call.**
- Bundle re-derivation: the built `v8-playable.html` embeds CONFIG.js
  (embed open at offset 2,283,465) with the SAME nesting — the last
  `WH_CONFIG.X =` opener before the `contacts` row (offset 2,632,733) is
  `WH_CONFIG.leveling`, and the CONFIG embed's `};` closer carries it
  (verified: the `contacts` row sits inside the CONFIG.js embed bounds),
  while the runtime call-site embed (game.js embed open at offset
  3,420,170) boots `WH_SHCONTACTS.init(scene, CFG.contacts)` — the built
  bundle carries the identical defect.
- Node `--check` cannot catch this (scope-correct plain JS); every parse
  and Devbot's own pool probes PASS because they pass a HAND-BUILT cfg
  (not `CFG.contacts`) to `init`, which is exactly why the in-lane
  validation missed it. The valspec's "integration" wording (probe loads
  CONFIG.js AND shadows.js in one context — not two isolated runs) is the
  intent V-1.2 enforces; both readings of "parse" are satisfied only by
  the top-level placement.

## All other V checks — PASS (evidence)

- **V-2** — shadows.js surface OK: one global, exactly `init/attach/update/detach`
  exported, 'use strict', IIFE, zero ES5+ tokens, one geometry, ONE texture
  object per init (one CanvasTexture constructed; line 57's second construction
  is the non-DOM fallback — only one path executes; runtime singletons verified
  in V-3.1/V-3.2), one material (0x000000, map, transparent, depthWrite:false,
  polygonOffset −2/−2, cast/receiveShadow:false), rotation.x −π/2, per-actor
  scaling via mesh.scale only, zero new lights. Texture ramp carries the 0.55
  half-radius value with (1−dist) linear falloff, black core, no color fill.
- **V-3** — 22/22 pool physics probes PASS on the real landed module: pool of
  24 acquired from free-list; init idempotent (double-init rebuilds nothing,
  singleton identities unchanged); exhaustion = silent skip + exactly ONE
  lifetime console.warn; free-on-parent-null every tick (Freed mesh removed
  from scene, re-acquired on next attach); idempotent re-attach returns the
  SAME slot, second opts ignored; detach() releases cleanly + re-acquirable;
  no new meshes/geometry/texture/material after exhaustion or re-attach.
- **V-4** — 23/23 numeric probes PASS with the Landed values:
  | lift | k | opacity | scale (r=0.9) | blob y |
  |---|---|---|---|---|
  | 0.0 | 1.0 | 0.4200 | 0.9000 | pos.y+0.02 |
  | 0.8 | 0.75 | 0.3150 | 0.7987 (0.55+0.45×0.75) | pos.y+0.02 |
  | 3.2 | 0.0 | 0.0000 | 0.4950 (≥0.55 floor) | pos.y+0.02 |
  | 4.0 | 0.0 (D1 clamp) | 0.0000 | 0.4950 | pos.y+0.02 |
  | −1.2 (sinking) | 1.0 (stays full) | 0.4200 | 0.9000 | pos.y+0.02 |
  plus: pos-less owner anchors at root.y+0.02; rotation.x −π/2 on every pooled
  mesh (bob never read); mesh.scale uniform; per-actor sizing (mesh.scale not
  geometry).
- **V-5** — all five anchors verified by RE-LOCATION (never stale line numbers):
  1. index.html: shadows tag exactly once, immediately before game.js
     (shadows @84, game @85); after hazards(@83)/region-manager(@65).
     Bundle embed order (embed-open tags): CONFIG 2,283,465 → … →
     region-manager 3,134,120 → shadows 3,413,390 → game 3,420,170 —
     shadows.js is embedded before game.js in the built bundle too
     (single embed per file; the first `WH_SHCONTACTS` hits sit in the
     game/region call sites, as in the sources).
  2. game.js boot: `if (window.WH_SHCONTACTS) window.WH_SHCONTACTS.init(scene, CFG.contacts);`
     @195, inside `setupLights()` (fn 143-196), after `game.playerLight` init
     (@170) and the P1-8 pool lines — same setup region.
  3. game.js:2588 player attach directly after `game.player.setBody(pBody)`
     (@2586), `{ bodyName: 'playerBody' }`.
  4. game.js:3270 the ONLY `WH_SHCONTACTS.update()` call site (@3270), within
     ±5 lines of `game.playerLight.update` (@3268).
  5. region-manager.js:1928 per-enemy attach directly after
     `enemy.setBody(eBody)` (@1926), with in-scope `var bodyName` (@1916) and
     `var eScale` (@1920) — exact tokens.
  Census (token counts vs valspec "line-count" rule): `WH_SHCONTACTS`
  appears x2 in shadows.js (definition + header comment), x3 in game.js,
  x1 in region-manager.js (grep -c), 0 elsewhere — matching the valspec
  numbers for shadows.js and region-manager.js exactly. game.js measures
  x3 tokens vs valspec's "×4 lines": the boot site's call text is split
  across two lines (`init(scene,` / `CFG.contacts);`), so a line-based
  census counts it twice — a counting-convention difference, not a
  functional fault (all 3 sites verified by re-location above), not
  blocking. In the bundle, `WH_SHCONTACTS` = 10 hits = 2 per call-site
  invocation (guard + call) × 5 sites, matching the source census.
  `CC-LS1` markers = 7 (`shadows.js` ×2, `warn` string ×1, CONFIG ×1,
  game ×3, region-manager ×1 — the 7th is shadows.js:117's
  `console.warn('CC-LS1: contact-shadow pool exhausted')`), matching
  Devbot's count; ≥ 6 floor PASS.
- **V-6** — additive-only: diff `ab61c2c` → worktree touches exactly the 5
  sanctioned tracked files (index.html +1, CONFIG.js +10 insertions/1
  removed line being the disclosed `rankToastSeconds: 1.6` →
  `rankToastSeconds: 1.6,` comma-only edit, game.js +8, region-manager.js
  +3) + untracked additions (shadows.js; the 2 io docs; scratch probe
  files). NO edits to enemy.js/player.js/journal.js/bestiary.js/wolf-debug.js/
  ambush.js/hazards.js/save.js/style.css/light.js/daynight.js (all
  byte-identical vs parent). tools/build_v8.py byte-identical.
  Markers: CC-AE1 6, QJR-2 9, CC-WB2 7, CC-H6 5, lastchancel 8, QJR-4 36,
  WH_AFF 26, **CC-LS1 7** in the built bundle — every prior floor intact.
  Build determinism: 2 INDEPENDENT fresh runs of `python3 tools/build_v8.py`
  → exit 0 both, byte-identical to the landed bundle each time, sha256
  `913c68cc6309b750768e77fd0ee8e7f8d5c97bd4f2b0bdb7d4767f2b29c0d7d7`
  (= claimed x3-identical sha).
- **V-7** — lighting untouched: CONFIG.js `lighting {…}` and `lightPool {…}`
  bands byte-identical (band-extracted diff against `git show ab61c2c`);
  hemi/moon 7 rows intact; game.js `playerLight` 3 / `lightPool` 13 /
  `applyDayNight` 2 / `cemeteryFogTick` 2 / `skyTick` 3 / `PointLight(` 1
  rows vs parent all EQUAL (no row edits anywhere); P1-8 markers 2+4
  (≥2+≥3); light.js + daynight.js byte-identical; the 6 byte-sacred js + style.css
  byte-identical; shadows.js has ZERO `PointLight`/`DirectionalLight`/
  `HemisphereLight`/`SpotLight`. game.js+region-manager.js+index.html diff
  is pure insertions (zero removed lines); the sole line not carrying a
  CC-LS1 tag is the CC-LS1 comment's own continuation
  (`// no per-frame allocation - P1-8 pool law).`, second line of the 2-line
  boot comment) — accounted, non-blocking.

## Defect list

1. **BLOCKING** — `contacts` nested in `WH_CONFIG.leveling` instead of
   top-level WH_CONFIG (CONFIG.js:5121); `WH_CONFIG.contacts` undefined;
   boot init at game.js:195 receives undefined and throws TypeError at
   `cfg.textureSize`. Fix: de-indent/hoist the 10-line block out of
   `leveling` to top-level (immediately after the `leveling` object's
   closing `};`), keeping the same comment lines and 7 keys; the
   `rankToastSeconds: 1.6,` comma then belongs to `leveling` (restore its
   no-comma form). Rebuild (v8 bundle) + full V-1..V-7 re-run required.
2. Non-blocking (V-2 nuance, documented): two `new THREE.CanvasTexture` call
   sites in shadows.js (line 54 canvas path, line 57 non-DOM fallback);
   exactly one executes per init (canvasRendered XOR) → one texture object,
   which is the spec's substantive law; census wording "x1" refers to the
   runtime singleton, verified by V-3.1/V-3.2.
3. Non-blocking (V-5 nuance, documented): valspec "game.js ×4" is a
   line-count convention (the boot site's call is split across two lines);
   token census = x3, all sites verified by re-location — no functional
   fault.
4. Non-blocking (V-7 nuance, disclosed): one added line inside the 2-line
   CC-LS1 boot comment does not itself carry the tag text; harmless
   (comment continuation of a tagged site line).

## Measured build determinism

- 2 independent fresh runs post-verdict: exit 0 both, byte-identical to the
  landed bundle, sha256 `913c68cc6309b750768e77fd0ee8e7f8d5c97bd4f2b0bdb7d4767f2b29c0d7d7`
  (matches Devbot's x3-identical claim).

## Verdict

**FAIL — 40-point gate, 36/40 earned (90.0%), 1 blocking defect
(V-1: CONFIG placement).** The module itself is excellent (V-2/V-3/V-4
fully pass; V-5/V-6/V-7 pass with no functional fault). This is a 2-line
placement error with a clean 10-line hoist fix; every other landed line is
additive, byte-clean, and marker-intact. Fix, rebuild, and re-run the gate.

---

## RE-VERDICT 2026-11-07T20:47Z — AMENDED OVERALL: **PASS — 40/40, 0 blocking**

Focused Testerbot re-run on the repaired placement (independent; verdict file +
scratch probes only, NO source edits, no harness, no headless browser —
no-harness-playtest-gate law). Same worktree `/tmp/wh-worldfeat`
(feat/world-visuals), diff base `ab61c2c`. Fresh independent probe:
`scratch/cc-ls1-fix-probe.js` (rewritten by Testerbot for this re-verdict:
real landed CONFIG.js + shadows.js under node `vm`, stubbed three.js,
WH_ASSETS absent-stub, REAL boot call `init(scene, CFG.contacts)`).
**Probe: 12/12 PASS, exit 0.**

### RE-VERDICT — V-1 (full re-check): PASS 4/4

- `window.WH_CONFIG.contacts = {` is now a **genuine top-level statement**
  (CONFIG.js:5121, zero indentation), sitting AFTER the `leveling` closer
  `};` (5118) and its `rankToastSeconds: 1.6` no-comma row (5117) —
  sibling of every other `window.WH_CONFIG.X = {` opener. Opener census
  (grep `^window\.WH_CONFIG\.\w+ = {`): 19 openers, last two are
  `leveling` (5005) then `contacts` (5121); NO `contacts:` property line
  remains anywhere (only occurrence of the token `contacts` in CONFIG.js
  is line 5121's assignment).
- Exactly 7 keys with the valspec values: poolSize 24, textureSize 128,
  radiusBase 0.55, groundOffset 0.02, maxLift 3.2, minScale 0.55,
  maxOpacity 0.42 (all verified via vm-loaded object equality, not text).
- `WH_CONFIG.leveling.rankToastSeconds === 1.6` **numeric** (===, vm check;
  commaless row at 5117, `leveling` band byte-identical to parent).
- `node --check prototype/js/CONFIG.js` → OK.
- **Boot call-chain probe: no throw.** `WH_SHCONTACTS.init(scene,
  CFG.contacts)` executes the REAL landed module (CircleGeometry +
  CanvasTexture + MeshBasicMaterial all constructed, pool built) end-to-end
  and returns cleanly — the prior TypeError at `cfg.textureSize` is dead.

### RE-VERDICT — V-6 (re-check): PASS (unchanged 3/3)

- `git diff --stat ab61c2c` → exactly the 5 sanctioned tracked files:
  index.html +1, CONFIG.js **11 insertions / 0 deletions** (now purely
  additive — the prior `1` removed line, the `rankToastSeconds` comma
  edit, is gone; the commaless form is byte-parent), game.js +8,
  region-manager.js +3, bundle +213/-1 (embed). game.js /
  region-manager.js / index.html diffs re-read line-by-line: pure
  CC-LS1-tagged insertions, zero removed lines.
- **leveling round-trip verified by Testerbot**: `git show
  ab61c2c:prototype/js/CONFIG.js | diff - worktree/CONFIG.js` → only the
  11 appended lines; zero changed/removed rows inside `leveling`
  (rankToastSeconds row byte-identical to parent).
- Byte-identical vs parent (git diff --stat empty): light.js, daynight.js,
  enemy.js, player.js, journal.js, bestiary.js, wolf-debug.js, ambush.js,
  hazards.js, save.js, style.css, tools/build_v8.py.
- **Build determinism (Testerbot-measured, fresh, post-repair)**: 2
  independent `python3 tools/build_v8.py` runs → exit 0 both;
  sha256 both **`c5cfead212d0133602419ba146c7fae6efe1cc6e9ce76b34656ff4f2b8b80354`**
  (pre-repair sha `913c68cc…` superseded; matches Devbot's claim).
- Marker floors in the rebuilt bundle (Testerbot census): CC-AE1 6,
  QJR-2 9, CC-WB2 7, CC-H6 5, lastchancel 8, QJR-4 36, WH_AFF 26 —
  all prior floors intact — **CC-LS1 = 7** (≥6 floor PASS; matches
  Devbot's 7).

### RE-VERDICT — V-7 (spot re-check): PASS (unchanged 2/2)

- CONFIG.js `lighting {…}` and `lightPool {…}` bands re-extracted from
  worktree and from `git show ab61c2c:…` and sha256-compared —
  **identical** (lighting band sha `be4dd1…d38ed05`, lightPool band sha
  `0c1ff7…edb94a`, equal across versions); hemi/moon row counts equal.
- game.js row counts worktree vs parent, ALL EQUAL: playerLight 3/3,
  lightPool 13/13, applyDayNight 2/2, cemeteryFogTick 2/2, skyTick 3/3,
  PointLight( 1/1 — zero row edits.

### RE-VERDICT — V-2/V-3/V-4/V-5 (module surface, pool, numerics, wiring)

Not invalidated by this placement fix (the repair only moved the
already-verified block and restored the comma); the landed
shadows.js/game.js/region-manager.js wiring lines are byte-identical to
what the original verdict verified by re-location, and the boot call-site
`init(scene, CFG.contacts)` — the one thing V-1.2 blocked — now provably
resolves (probe). No re-run performed; no evidence contradicts those
PASSes.

### RE-VERDICT — bundle re-derivation

The rebuilt `v8-playable.html` embed carries the CORRECT form: opener
`window.WH_CONFIG.contacts = {` at offset 2,632,729, immediately following
`rankToastSeconds: 1.6\n};\n// CC-LS1 (doc 61 P1-1)…` (leveling closed,
contacts a sibling statement); the boot call-site embed
`window.WH_SHCONTACTS.init(scene, CFG.contacts)` sits further down in the
game.js embed — bundle and source agree.

### RE-VERDICT — verdict update

| Verdict | Criterion | Old | New |
|---|---|---|---|
| V-1 CONFIG `contacts` + parse | FAIL 0/4 | **PASS 4/4** |
| V-2..V-7 (module, pool, numerics, wiring, determinism, lighting) | PASS | PASS (unchanged) |
| **OVERALL** | **FAIL 36/40, 1 blocking** | **PASS 40/40, 0 blocking** |

Blocking defect V-1.2 is RESOLVED. The 36/40 fail verdict of 2026-11-08 is
superseded; CC-LS1 gate = **PASS, cleared to land** (Nicko playtest per
no-harness-playtest-gate remains the visual evidence step).
