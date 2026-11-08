# CC-LS1 — Blob Contact Shadows — VALSPEC (Testerbot, doc 61 P1-1)

- PREFLIGHT: sha256(/tmp/wh-worldfeat/io/specs/cc-ls1-contact-shadows-spec.md) = f38909c1eb06a0b685b985fb6f46caf400dba9979b73ab9ad287295832c4c855 — if the spec changed after this valspec was written, abort and re-read it.
- Worktree /tmp/wh-worldfeat, branch feat/world-visuals, parent commit ab61c2c3("build: v8 bundle (worktree) - QJR-4 bestiary stamp") — baseline numbers below are measured against that parent at valspec write time; do not re-derive them, use them as embedded floors.
- Validation mode: static census + node scripts with STUBS only. NO headless browser, NO harness, NO per-frame runtime. Validator scratch scripts land in `scratch/cc-ls1-val/`. NO-GIT: no commit/push/config; read-only `git log/show/diff/rev-parse` allowed (the build tool's internal `git rev-parse/show` is the tool's, not a child commit).

## SPEC DEFECTS CAUGHT (marked; the spec file is NOT edited — resolved HERE)

- D1 (arithmetic): spec A-7 V-4 row says lift 3.2 → k "0.0(3)". Exact law (1 − lift/maxLift) gives k = 0.0 at lift 3.2; 0.0(3) would require lift ≈ 3.09. This valspec's table uses exact values.
- D2 (stale floors): spec V-6 "CC-WB2 x6" and "WH_AFF x14" do not match the landed tree — measured: CC-WB2 7, WH_AFF 25 (js-only; 26 incl. style.css). The spec numbers predate later marker landings. Valspec floors = measured baselines (no-loss rule), tabulated in V-6.
- D3 (ambiguity): spec V-6 "CC-H6 lastchancel" carries one unnumbered pair. Split: CC-H6 ≥ 5, lastchancel ≥ 8 (js-only), both measured today.
- D4 (A-5 token): spec writes `{ bodyName: bodyNameFor(<local var>), scale: enemy.scaleUsed ... }`. `bodyNameFor` is a WH_Enemy method already called on region-manager.js:1916 (`var bodyName = window.WH_Enemy.bodyNameFor(e.type)`), and `enemy.scaleUsed` does not exist — the applied scale is local `var eScale` (:1920). Valspec instructs census of the LANDED attach call, not these tokens (per the spec's own note).
- D5 (A-4 prose): spec site 2 contains a garbled transition line (`window.WH_SHCONTACTS && game.contacts attaches — CONCRETE:`) that is spec prose, not code. Validate only against the CONCRETE line that follows it.

None of D1–D5 blocks the build; each is resolved by the rules in this valspec.

## V-1 CONFIG `contacts` block — exact 7 keys, parses, additive-only

PASS requires all of:

1. `node --check prototype/js/CONFIG.js` exits 0.
2. Shim-load parse: node script running the CONFIG.js source in a fresh vm context with `window={}` (and a benign `THREE={}` stub if referenced), then asserting `window.WH_CONFIG.contacts` is a plain object.
3. Key census: the block has EXACTLY 7 keys with exactly these values/types: `poolSize:24`, `textureSize:128`, `radiusBase:0.55`, `groundOffset:0.02`, `maxLift:3.2`, `minScale:0.55`, `maxOpacity:0.42` (all finite numbers; no extra keys, no nested objects, comments allowed and ignored). The block carries the `CC-LS1` comment tag.
4. Additive-only diff vs parent for js/CONFIG.js: no deleted or modified pre-existing line; the only hunk(s) append the contacts block inside the `window.WH_CONFIG` object literal. Everything outside the appended block diffs empty.
5. No duplicate key: `contacts` appears as an object key exactly once in the file.

## V-2 shadows.js API surface (NEW file)

PASS requires all of:

1. `prototype/js/shadows.js` is new (absent in parent); `node --check` exits 0.
2. Namespace: defines `window.WH_SHCONTACTS` exactly once, exporting exactly the four keys `init, attach, update, detach` (spec: "exactly three functions + init"); `detach` is exported for tests only (no production caller outside the module — census of all call sites belongs to V-5).
3. ES5 + IIFE + `'use strict'`: zero regex hits in the file for `=>`, `\bconst\b`, `\blet\b`, `\bclass\b`, and template literals.
4. Pool singletons, created ONCE inside init: regex count over the whole file — `new THREE.CircleGeometry(` ×1; `new THREE.CanvasTexture(` ×1 (texture rendered from `cfg.textureSize`, no hardcoded second size); `new THREE.MeshBasicMaterial(` ×1. No geometry/texture/material creation anywhere in attach() or update().
5. Material census: `color:0x000000` (or `0x000000` bound to color), `map:` bound to the texture, `transparent:true`, `depthWrite:false`, `polygonOffset:true` with factor −2 and units −2; per pooled mesh `castShadow=false` and `receiveShadow=false`.
6. Blob orientation: `mesh.rotation.x = -Math.PI/2` (census).
7. Per-actor sizing via `mesh.scale` only (census `scale.set(`); texture routine is a radial alpha ramp: black core → transparent edge, with a linear falloff term (`1 - r/R` shape) carrying the 0.55 half-radius value; no colored fill (palette law: black blob only).
8. No per-frame allocation: update() body contains zero `new` operators and zero texture/canvas redraws; attach() allocates nothing but bookkeeping (it binds an existing pool mesh).

## V-3 Pool physics (node script `scratch/cc-ls1-val/val_v3_pool.js`)

Contract: load shadows.js via `vm.runInNewContext` with a stub env — `window={}`; `THREE` stub whose `CircleGeometry`, `CanvasTexture`, `MeshBasicMaterial`, `Mesh` are plain recordable classes (Mesh exposes `position`, `scale`, `rotation`, `material`, `parent`, `castShadow`, `receiveShadow`); `console` spied; pass a `fakeScene` whose `add`/`remove` are recorded. Then `init(fakeScene, cfg)` with cfg = the V-1 7-key object.

PASS requires all of:

1. acquire: init creates exactly `cfg.poolSize` mesh instances (stub constructor call count == 24); each of 24 `attach()`s binds a DISTINCT pool mesh and the blob is parented to the scene (added via fakeScene).
2. idempotent re-init: calling init() a second time does not rebuild the pool (mesh count stays 24; geometry/texture/material identities unchanged).
3. exhaustion = silent skip: the 25th attach() does not throw, binds nothing, and emits AT MOST ONE `console.warn` for the whole lifetime; a further attach after exhaustion must not warn again (no per-frame noise). Pool accounting unchanged.
4. free-on-parent-null: set `owner.root.parent = null`; a single `update()` releases that slot — the freed mesh is removed from the scene and a subsequent attach() re-acquires that specific mesh (free-list restored; stub add/remove balanced).
5. idempotent re-attach: `attach(owner, opts)` twice on the same live owner consumes a single slot; the second call's opts are ignored (no double-bind).
6. `detach(owner)` explicitly releases the slot (releasing the same mesh as rule 4's path); detaching an unbound owner is a quiet no-op.
7. No leak: after a free+re-acquire cycle the accounted meshes are again exactly 24 (bound 24, free 0); after freeing 1, bound 23 / free 1.

## V-4 Numeric transform table (node script reusing the V-3 harness)

From the 7-key CONFIG values: `k = clamp(1 - lift/3.2, 0, 1)`; `opacity = 0.42*k`; `scale = R*(0.55 + 0.45*k)`; blob y = ground of the tick (pos-anchored when `owner.pos` exists), x/z = root.

| lift (root.y − pos.y) | k | opacity | scale (·R) | blob y | blob x/z |
|---|---|---|---|---|---|
| 0.0 (standing) | 1.00 | 0.420 | 1.0000 | pos.y + 0.02 | root.x/z |
| 0.8 (hop / root ride) | 0.75 | 0.315 | 0.8875 | pos.y + 0.02 — NOT root.y + 0.02 | root.x/z |
| 3.2 (= maxLift) | 0.00 (exact, D1) | 0.0 | 0.5500 | pos.y + 0.02 | root.x/z |
| 4.0 (> maxLift) | 0.00 (clamped) | 0.0 | 0.5500 | pos.y + 0.02 | root.x/z |
| −1.2 (sinking; negative delta) | 1.00 (stays full) | 0.420 | 1.0000 | pos.y + 0.02 | root.x/z |

Script asserts, per row: drive a synthetic owner with `root.position = {x: 3.5, y: pos.y + lift, z: -2.0}` and `pos = {y: groundLevel}` (use ground 0.0), call `update()` ONCE per row, then check `material.opacity`, `mesh.scale.x` (uniform, i.e. equals scale.y), `mesh.position`. Two structural assertions ride along: (a) pos-less owner (pos undefined) anchors y at `root.position.y + 0.02`; (b) the blob is never bobbed/tilted — y is set from the lift-independent ground term on every row including 0.8 and 3.2/4.0.

## V-5 Wiring census (line anchors are today's, at valspec write; FINAL VALIDATOR CENSUSES THE LANDED FILES — if lines drifted, re-locate the named anchors, never hard-require stale line numbers)

Anchor map (parent): index.html:84 `<script src="js/game.js"></script>` (:83 hazards.js); game.js:8 `var CFG = window.WH_CONFIG`; :170 `game.playerLight = new window.WH_PlayerLight.PlayerLight(game.scene)`; :2583 `game.player.setBody(pBody)`; :3262 `game.playerLight.update(game.player, game.firebolts)`; region-manager.js:1916 `var bodyName = window.WH_Enemy.bodyNameFor(e.type)`; :1920 `var eScale`; :1926 `enemy.setBody(eBody)`.

PASS requires all of:

1. index.html: `<script src="js/shadows.js"></script>` present exactly once, in the last-before-game.js slot — immediately before the game.js tag (today line 84), i.e. after hazards.js/region-manager.js. Bundle consequence (build inlines by document order): shadows.js code must precede game.js code inside builds/v8-playable.html (census by byte offset).
2. game.js — 3 sites, ≤ 10 added lines total, each guarded `if (window.WH_SHCONTACTS)` and tagged `// CC-LS1:`:
   - boot: `WH_SHCONTACTS.init(game.scene, CFG.contacts)` inside the setup region after the playerLight init (:170); may sit before or after the P1-8 pool lines but within the same region; references the scene and the CONFIG alias, not `CONFIG`.
   - player attach: directly after `setBody(pBody)` (:2583): `attach(game.player, { bodyName: 'playerBody' })`.
   - per-frame: exactly ONE `update()` call site, within ±5 lines of the `playerLight.update` call (:3262), before/after both acceptable.
3. region-manager.js — 1 site: attach directly after `setBody(eBody)` (:1926), guarded + tagged. Extract the LANDED opts object and verify: (a) `bodyName` resolves to an in-scope body-name string (today: the local `var bodyName`; acceptable equivalents: a name string from the same expression), (b) a `scale` passthrough is present and is an in-scope number matching the scale the holder applied at this site (today: `var eScale`); c) the same guard/tag. D4 law applies: do not require the spec's speculative tokens.
4. Global call-site census: `WH_SHCONTACTS` appears in exactly — shadows.js (definition), game.js ×4 (init/attach/update + guards are part of those lines), region-manager.js ×1; plus at most 1 comment line in index.html. No site in enemy.js, player.js, or elsewhere.

## V-6 Zero regression (floors measured at valspec write vs parent ab61c2c3)

1. `git diff --stat <parent>..HEAD` (or working-tree diff at gate): changed files EXACTLY {prototype/js/shadows.js (new), prototype/js/CONFIG.js, prototype/index.html, prototype/js/game.js, prototype/js/region-manager.js} PLUS the generated `prototype/builds/v8-playable.html`. Nothing else: tools/build_v8.py diff empty; byte-sacred families diff empty — journal.js, bestiary.js, wolf-debug.js, ambush.js, hazards.js, save.js, style.css.
2. Scoped line budgets: CONFIG.js additive-only (V-1); index.html exactly 1 added line; game.js ≤ 10 added lines total across exactly 3 sites; region-manager.js ≤ 4 added lines in exactly 1 site; shadows.js free.
3. Deterministic build: final validator runs `python3 tools/build_v8.py` (newest tool law) — exit 0 on two consecutive runs, and sha256(prototype/builds/v8-playable.html) is byte-identical across the two runs. (Stamp law keys off HEAD author time; HEAD does not move because children never commit.)
4. Prior-marker no-loss census, js-only tokens (`grep -rho TOKEN prototype/js | wc -l`); prototype totals in parentheses (incl. style.css + index.html):

| token | floor js-only (total) | per-file ≥1 in |
|---|---|---|
| CC-AE1 | 5 (6) | CONFIG.js, ambush.js, game.js, region-manager.js |
| QJR-2 | 8 (9) | journal.js (5), npc.js (3) |
| CC-WB2 | 7 (7) — D2: spec's "x6" stale | CONFIG.js, wareffort.js (5), strataeffort.js |
| CC-H6 | 5 (5) — D3 | CONFIG.js (4), region-defs.js |
| lastchancel | 8 (8) — D3 | CONFIG.js |
| QJR-4 | 33 (36) | journal.js (16), game.js (8), bestiary.js (4), enemy.js (4), CONFIG.js |
| WH_AFF | 25 (26) — D2: spec's "x14" stale | game.js (9), npc.js (6), affinity.js (2), inventory.js (2), wareffort.js (2), strataeffort.js (2), camp.js, CONFIG.js |

GATE: every count after CC-LS1 ≥ its floor; no file in the per-file column drops below 1; CC-LS1 markers ≥ 6 in the built bundle (spec A-6 law).

## V-7 Lighting rows untouched (static)

1. CONFIG.js lighting band byte-identical vs parent — the hemi rows (`hemiSkyColor`/`hemiGroundColor`/`hemiBaseIntensity`), moon rows (`moonColor`/`moonIntensity`/`moonAzimuthDeg`/`moonElevationDeg`, today CONFIG.js:26–36), the moon-card block (today :60–70), and the `lightPool` block (:74): diff vs parent shows zero modifications; the only CONFIG.js content change is the V-1 append.
2. game.js rig unchanged except the single inserted update() site: playerLight init (:170), P1-8 pool construction block (~:172–200), light-socket registry (~:2866), nearest-socket handoff (~:2937), `applyDayNight`/`cemeteryFogTick`/`skyTick` clock lines after the 3262 row — all diff-clean.
3. P1-8 marker floor intact: js-only 5 (CONFIG.js ×2, game.js ×3); light.js and daynight.js diff empty (0 changed lines).
4. No new lights: shadows.js creates no THREE lights of any kind (census: zero `PointLight|DirectionalLight|HemisphereLight|SpotLight` in shadows.js) — light count law (M-19) preserved.

Final verdict: PASS only when every gate above is green; report per-V PASS/FAIL with the actual measured numbers (marker counts, sha256 pair, diff stats) in the Testerbot report — never a bare "passed".
