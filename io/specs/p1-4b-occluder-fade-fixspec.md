# P1-4b FIXSPEC — occluder-fade contract alignment (wake 49)

IO fix spec, 2026-11-08 wake 49. Amends the build perTesterbot verdict
(io/valspecs/p1-4b-occluder-fade-VERDICT-testerbot.md, VERDICT: FAIL,
blockers V-5/V-13/V-16/V-17/V-19/V-20). The as-built law base (V-8 seed
hash, V-9/V-10 row identity, V-6 classifier, V-12/V-14 pull-block wrap,
V-29 disposal, V-26/V-27 shader form) SURVIVES. This spec changes the
CONFIG surface, the geometry ownership, the registry, and the driver law.

Allowlist UNCHANGED: prototype/js/CONFIG.js, region-manager.js, player.js
ONLY. Everything below is binding. Where this spec and the original spec
(p1-4b-occluder-fade-spec.md) both speak, BOTH agree; the valspec greps
are the mechanical truth.

## F1. CONFIG (CONFIG.js) — fixes V-5, V-13, V-24, V-37

DELETE the as-built block at CONFIG.js:3080 (under `player:`) and ADD
under `world:` (near cameraPull, same `world: {` object, line ~300):

```js
occluderFade: {
  enabled: true,       // false = the P1-4a law exactly (veg rows pull again, no fade writes)
  dissolveM: 1.2,      // penetration (m past pullFadeSlack) at which a tree is fully dissolved
  hashMin: 0.02,       // shader dissolve-threshold floor (no full-alpha single-pixel shimmer)
  pullFadeSlack: 0.25, // m of pull allowed BEFORE fade engages
  decayPerSec: 2.0     // dissolve values decay toward 0 at this rate when not engaged
},
```

- The cameraPull block and every other CONFIG subtree stay byte-identical.
- git diff on CONFIG.js = the moved block + cameraPull comment addendum ONLY.
- player.js:61 FD var reads `window.WH_CONFIG.player.occluderFade` —
  change to `window.WH_CONFIG.world.occluderFade` (V-13: exactly the
  world.* chain; grep 'occluderFade' player.js = every hit on world.*).
- region-manager.js fadeTable read (rm:2413) likewise world.*.

## F2. Geometry ownership — fixes V-16 (inverted), removes the template hazard

The as-built attaches whFadeT/whFadeSeed InstancedBufferAttributes onto
the SHARED template geometry in whBuildInstanced (rm:1893-1900, guarded
by `if (!o.geometry.attributes.whFadeT)`) — with region A and region B
both instancing the same template, the second region's build is skipped
and the first region's per-index values serve both meshes; a fade write
into one region's mesh corrupts the other region's trees at equal
instance indices. This is the KEY HAZARD spec 4.6 froze. REMOVE it:

- whBuildInstanced(name, list, opts): opts OPTIONAL third param. When
  `opts && opts.fadeable` (ONLY the fadeable call sites opt in):
  - CLONE the geometry first: `var geo = o.geometry.clone();` and build
    the InstancedMesh on the CLONE.
  - Add ONE InstancedBufferAttribute on the CLONE: 'whDissolve'
    (Float32, length = list.length, all zeros). NO whFadeT, NO
    whFadeSeed attributes anywhere (per-instance seeds ride the driver,
    F4; the shader needs exactly one attribute).
  - The patch (whFadePatchMaterial clone) happens on the mesh's material
    CLONE before the mesh is added to the scene (R2 order preserved).
  - Track the clone for disposal: registry entry carries the clone;
    disposeRegion disposes cloned GEOMETRY + clone material (V-29
    pattern; the SHARED template geometry and template materials are
    NEVER disposed).
- The attribute-add happens per built mesh (per region), so both regions
  carry independent whDissolve arrays. Non-fadeable callers keep the
  2-arg signature byte-identical.
- The fadeable call sites: NONE this round. No whBuildInstanced caller
  opts in (all C-region veg render per-prop; the wall/arch/forecourt
  rows are mass (veg 0); the C buckets carry r 0 decor). The opts
  {fadeable:true} clone path EXISTS and is wired (attribute + registry +
  disposal ready) but stays dormant — the next round that adds a
  fadeable instanced asset opts in at one call site (F2 machinery is
  Testerbot-verified without a live caller by reading the guard).

## F3. Registry — fixes V-19 (inverted), V-17

Resolution becomes explicit per-row obj+instIdx:

- A per-region map `whFadeByProp[regionId]` (plain object) keyed by the
  same row-index strings used today ('prop<k>', 'scatter<j>',
  'wall-…', 'arch-…', 'forecourt-…'), each value
  `{ obj: <instanced mesh or single object>, instIdx: <int, -1 for
  singles>, kind: 'instanced'|'single' }`.
- AMENDMENT (wake 49, data-verified): the C-region veg collider rows are
  ALL int-index CONFIG.props rows rendered per-prop; the C cell buckets
  hold only r=0 decor (ring/free bushes, grass) with NO collider rows —
  valspec V-19's '#.#' C-bucket premise does not exist in the data. The
  C-region registration therefore rides the SAME per-prop clone path as
  A/B (whFadeRegister at build for every r>0 row, kind 'clone',
  instIdx = i), and the C cell buckets stay OUT of the registry (no
  fadeable rows address them). Testerbot's re-verdict traces V-19's
  three pinned rows as: a prop row (int index), a scatter row
  ('scatter<j>' single), and for the C-region row the per-prop clone
  path (the '#.#' form asserted no rows exist, grep 0).
- 'single' kind entries (scatter trees) carry the mesh object (mesh:
  tObj — NOT null) and a per-tree MATERIAL CLONE that the registry
  tracks for disposal.
- The uniform key in the single path is `whFadeUniform`
  (`material.uniforms.whFadeUniform = { value: 0 }` — rename from
  whFadeAmt everywhere; grep 'whFadeUniform' >= 1) and the clone
  creation sets `material = material.clone()` inside the scatter span
  (V-17). Template materials never mutated.

## F4. Driver law — fixes V-20, V-22, V-21

Replace the growth-slack + bidirectional-speed ease + min(1, dv+seed)
write with the spec 4.5/4.7 law, keeping the as-built structure
(module-scope FD_* scratch, zero steady-state allocation, live
window.WH_GAME region read):

- Requests: the preallocated module-scope record stays the ONE active
  fade record; a veg row engages on segment hit AS TODAY (fdClaim).
  Per-frame the row's penetration P is measured (the fdRowHit law).
- t = clamp((P - CFG.world.occluderFade.pullFadeSlack) /
  CFG.world.occluderFade.dissolveM, 0, 1); eased = t*t*(3 - 2*t).
- Dissolve value written = mix(seed, 1, eased) where
  seed = whFadeSeed(row.index, row.name) (the SAME byte-exact hash, V-8).
  - instanced: whDissolve.setX(instIdx, value) + attribute.needsUpdate
    when |old - value| > 1e-3 (V-22 threshold; no unconditional write).
  - single: uniforms.whFadeUniform.value = mix(seed, 1, eased), same
    dirty threshold (uniform write only when changed).
- Disengage: when the row leaves the band, dissolved value DECAYS toward
  0 at CFG.world.occluderFade.decayPerSec (value -= decayPerSec * dt,
  clamped at 0, never jumps to 0), then the record releases. The mix
  seed floor rides hashMin only in the SHADER threshold
  (max(hashMin, whDissolve) — F5); no driver-side seedMin.
- Enabled-off rollback: instant restore of the recorded value (fdDrop
  semantics preserved; A8 law byte-preserving as today's V-12/V-14 form).
- The driver (fdTick + whFadeApply/rename) reads ONLY the five CONFIG
  keys via window.WH_CONFIG.world.occluderFade — no hardcoded constants.

## F5. Shader — fixes V-20's threshold side

- Instanced path: vertex `attribute float whDissolve; varying float
  vWhDissolve; vWhDissolve = whDissolve;`; fragment: threshold =
  max(hashMin, vWhDissolve) against the existing inline world-hash
  (the whHashX arm V-27 passed); discard when hash < threshold. HashMin
  rides as a `#define` or uniform from CONFIG (either fine, but the
  VALUE must derive from CFG.world.occluderFade.hashMin).
- Single path: uniform-fade variant stays, threshold = max(hashMin,
  mix(seed, 1, whFadeUniform.value)) — seed per-tree (already computed
  per registry entry).
- material.transparent stays FALSE; depthWrite stays TRUE (V-26 law).
- whFadePatched flag law unchanged (V-25 passed as-built; do not churn).

## F6. Non-goals (unchanged)

- CP_CIRCLES consumer, pushOutCircles, pull math, CP_* scratch counts,
  RNG law, wall weld keys (V-18 passed), TRUNK_ASSETS, vegClass (V-6):
  byte-untouched.
- No new concept art (anchors concept-01-darkwood + day-01-darkwood +
  concept-05-night-ambush serve; 37-piece set unchanged).
- builds/v8-playable.html is rebuilt by IO after the fix (Devbot never
  builds).

## F7. Acceptance (re-verdict gates, Testerbot re-runs)

- RV-1 = V-5 as worded (world.* block present, 5 keys exact, block
  cites the IO spec path in a comment).
- RV-2 = V-13/V-24 (FD var chain = world.*; git diff CONFIG.js = the 5
  keys + comments only; cameraPull values byte-equal).
- RV-3 = V-16 as worded (clone + 'whDissolve', no whFadeT/whFadeSeed
  setAttribute anywhere, template geometry attribute-free; quote the
  ownership lines).
- RV-4 = V-19 as amended (per-row {obj, instIdx} resolution map present
  and wired; the 3 pinned rows traced per the F3 amendment's mapping of
  V-19 onto the data-verified paths: int prop row, scatter single, C
  per-prop clone).
- RV-5 = V-20 as worded (node -e sim of the LAW with the CONFIG keys;
  quoted constants: pen 0.25 -> t 0, 1.45 -> t 1.0, 0.85 -> t 0.5 ->
  eased 0.5; decay bounded, never jumps; CONFIG-only reads, no
  hardcoded law constants).
- RV-6 = V-17/V-22 (per-tree material clones + whFadeUniform; dirty
  threshold 1e-3 quoted).
- RV-7 = V-8/V-9 re-run (probe1 byte-identity and seed-hash byte-exact
  MUST SURVIVE the refactor untouched).
- RV-8 = regressions: V-6/V-12/V-14/V-18/V-26/V-27/V-29/V-30/V-31/V-33
  re-run; any new FAIL = new blocking.
- Verdict: ALL RV gates PASS = round PASS; any FAIL = iterate.
