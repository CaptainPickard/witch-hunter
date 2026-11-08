# P1-4b OCCLUDER FADE spec (doc 61 P1-4, second half)

IO spec, 2026-11-08, wake 48. Worktree /tmp/wh-worldfeat, branch
feat/world-visuals. Author: IO. Validator: Testerbot (valspec separate).
Devbot implements ONLY from this file + the Testerbot valspec.

## 0. Problem statement

The camera orbits the player through a forest of instanced trees. Wake 39
landed P1-4a (camera pull-in: the camera samples the target->want segment
against prop collider circles and pulls IN to the first blocked sample).
That treatment is correct for MASS occluders (stone walls, boulders,
architecture: you cannot see through them anyway, so moving the camera
closer is right). For VEGETATION (trees, bushes, stumps — the C14
trunk-class rows) yanking the camera every time a trunk crosses the orbit
is jittery and unnecessary, because foliage CAN break up visually. Doc 61
P1-4 says: "Fade occluding trees with material.alphaHash (r185) on
per-instance material clones." Wake 39's change log fixed the split:
"low stone walls = the future alphaHash round" — this round.

## 1. Art law anchor (Nicko standing order)

Palette/mood reference: /tmp/wh-worldfeat/art-direction/concepts/
concept-01-darkwood.png and day-01-darkwood.png (IO viewed both this wake):
cold blue-grey mist (#2C3545..#3E4B61), near-black trunks, amber lantern
accent, fog swallowing the mid ground. The fade must NOT punch holes in
that mood: fading is dissolve-to-nothing (hash noise threshold), never a
transparent ghost overlay; trunks stay solid at > camera-block distance.
concept-05-night-ambush.png governs the pull/fade SPLIT (mass stays pull).

## 2. Desired behavior (acceptance in one line)

When the target->want camera segment crosses a VEGETATION-class circle
row, the tree(s) whose instances own that row DISSOLVE via alphaHash noise
(threshold-driven, per-instance) instead of triggering a camera pull. Mass
rows keep today's pull. A vegetation row blocks PULL only if fade is
disabled/off or its instance cannot be addressed for fading — the camera
falls back to pull exactly as today in that case.

Player-side behavior is UNCHANGED: player collision still uses every
circle (vegetation circles still push the player out — the player still
cannot walk through a trunk). Only the CAMERA segment test splits.

## 3. Terminology and coupling facts (verified this wake)

- player.js updateCamera ~2291-2330: segment sampling loop over
  CP_CIRCLES = regionManager.propColliders(activeId).circles. Circle rows
  carry { index, name, x, z, r, h, fy }.
- Row provenance (region-manager whPropColliders ~485-547):
  (a) CONFIG props rows: index = numeric i -> CONFIG.props[i]; wall rows
      (p.wall) index = `i.k` string -> wall instance segment k of prop i.
  (b) scatter rows: index = `scatter<j>` -> plan.trees[j], ALSO placed as
      individual WH_ASSETS.instance objects (NOT instanced meshes) at
      region-manager ~2180-2188.
  (c) wall-plan rows: index = `wall-<kind><i>.<k>` / `arch-leg...` /
      `arch-plug...` / `forecourt-...` -> plan.colliders matching the
      whBuildInstanced(name, byAsset[name]) lists 1:1 in build order
      (name -> list order, per-instance index j = list position).
  (d) world-wall membership rows (side-filtered plan.colliders entries)
      join (c).
- Vegetation classification ALREADY EXISTS: TRUNK_ASSETS map +
  /tree|oak|birch|sapling|bush|bramble|fern|shrub|stump/i test in
  colliderRadius and whOccluderH (region-manager ~439-462). Reuse ONE
  shared classifier (export it, do not duplicate the regex).
- Instanced meshes are built ONLY by whBuildInstanced(name, list)
  (each instance list item = { x, y, z, rotY, scale | sx/sy/sz });
  A/B: one InstancedMesh per asset, list order = instance index.
  C: buckets per (asset, cell) — instance index is the position WITHIN
  the bucket list. The collider-table build and the mesh build both
  iterate the SAME underlying CONFIG props / plan.trees arrays in the
  same order, so mapping via ROW SOURCE (prop index i / tree index j)
  is deterministic; mapping via global instance counter is FORBIDDEN.
- Wall InstancedMeshes (buildWorld ~1789-1798) follow plan.segments
  order via byAsset[name] — segment list position = instance index.
- Material sharing: templates share one material across ALL instances
  and regions (window.WH_ASSETS template). alphaHash threshold reads
  MATERIAL alpha, so a GLOBAL threshold constant can ride the shared
  material; the PER-INSTANCE dissolve seed must come from a per-instance
  attribute injected via material.onBeforeCompile (custom attribute
  `whDissolve` float on the InstancedMesh geometry or an
  InstancedBufferAttribute added to the SHARED geometry — see design).

## 4. Design (binding)

### 4.1 New CONFIG block (CONFIG.js, near cameraPull)

```js
occluderFade: {
  enabled: true,          // false = exact pre-change behavior (single early-out)
  dissolveM: 1.2,         // segment penetration depth (m into r + camRadius + skin) at which a tree is FULLY dissolved
  hashMin: 0.02,          // dissolve threshold floor (avoid full-alpha single pixels shimmer)
  pullFadeSlack: 0.25     // m of additional pull allowed BEFORE fade engages (a trunk the camera barely touches should not dissolve the whole tree)
}
```

Wake-39 cameraPull block stays byte-identical except comments if the
spec requires (it does not).

### 4.2 Shared vegetation classifier (region-manager.js)

Rename/extract nothing public; add `RegionManager.vegClass = function(name)`
(or module-level function exported on the prototype) that returns true iff
`TRUNK_ASSETS[name] || /tree|oak|birch|sapling|bush|bramble|fern|shrub|stump/i.test(name)`.
colliderRadius and whOccluderH call THIS function instead of their own
inline test (byte-identical behavior, single source of truth).
Devbot must NOT duplicate the regex.

### 4.3 Row annotation (whPropColliders)

Every circle row gains `veg: 0|1`:
- (a) props rows: veg = vegClass(p.asset) ? 1 : 0 (wall rows veg = same rule
  from the wall asset name — boundary wall assets whWallA/whWallB are NOT
  vegetation: veg 0).
- (b) scatter rows: veg = vegClass(t.asset) (always 1 in practice).
- (c) wall-plan rows: veg = vegClass(asset).
- (d) world-wall membership rows (plan.colliders entries): veg = vegClass(name).

Existing consumers (player pull, enemy pathing if any reads circles)
keep working: `veg` is advisory metadata. Player push-out code (player.js
CP_CIRCLES consumer ~2292) MUST NOT change its circle usage (see 4.5).

### 4.4 Per-instance dissolve seed (deterministic)

At the point a circle row is CREATED, also compute
`seed = whFadeSeed(row.index)` — a stable float 0..1 = a hash of the row
index string (e.g. FNV-1a over bytes / 2^32; any deterministic mapping;
MUST be stable across region rebuilds within one page load AND across
page loads — string-hash of index is inherently stable). Rows store it as
`row.fadeSeed`.

### 4.5 Camera-side split (player.js updateCamera)

Inside the segment loop, for a circle hit:
- if `CFG.world.occluderFade && CFG.world.occluderFade.enabled` AND the
  row has veg 1 AND a fadeable instance can be addressed -> record a fade
  request { row, penetration } on a frame-scoped list; DO NOT set CP_I
  (do not pull). Continue scanning for a MASS row (veg 0) behind it: if
  any mass row is hit at any sample, normal pull fires at the first mass
  sample (mass occludes as today; fade does not screen it).
- if fade disabled or row not fadeable -> exact pre-change behavior
  (CP_I = hit index -> pull).
- pull math, floor, retreat, samples, allocation law: byte-untouched.
- zero per-frame allocation is preserved: iterate WITHOUT closures; the
  fade request list is a fixed-capacity preallocated array + a count Int.

Camera pull vs vegetation rows STILL fires as fallback when:
`CFG.world.occluderFade.enabled === false` (whole feature off) or when
the region has NO fade mesh registry (see 4.6 — legacy regions), with
identical geometry to today. This is the single-flag-off law.

### 4.6 Fade mesh registry (region-manager.js, the real welding)

RegionManager gains a per-region fade registry:
`this.fadeMeshes[regionId] = { byProp: Map(propKey -> array of {obj, mesh, instIdx, kind}), count }`
built at region build time:
- scatter trees (individual WH_ASSETS.instance at ~2180): key
  `scatter<j>` -> ONE entry {obj: tObj, kind: 'single'}: the whole tree
  Object3D simply fades via a per-clone material? NO — see design note:
  (i) alphaHash works on the SHADER level; for a single mesh we can set
  a per-object fade by injecting onBeforeCompile that reads a
  per-instance attribute ONLY if instanced; for a single Object3D the
  cheap equivalent: clone the template material ONCE per tree, set
  uniform fadeAmount, onBeforeCompile threshold = mix(hashMin, 1,
  fadeAmount) against a world-position hash; dispose on region dispose.

Devbot decision (allowed, binding either way, Testerbot re-derives):
- For INSTANCED meshes (A/B props + wall-plan assets + C cell buckets):
  add ONE InstancedBufferAttribute `whDissolve` (float per instance,
  init 0) to the geometry BEFORE first render… but geometry is SHARED
  across instances of the same template across regions — the attribute
  is a property OF THE GEOMETRY, and different regions share geometry.
  => therefore the attribute must live on the Geometry and instance
  index mapping must be GLOBAL to that geometry. whBuildInstanced uses
  tmpl.geometry shared across regions — the same geometry bytes. If two
  regions both instance the same asset, their instance indices would
  collide on one shared attribute. THIS IS THE KEY HAZARD.
  Resolution (binding): whBuildInstanced clones the geometry when the
  caller opts in (`whBuildInstanced(name, list, {fadeable: true})`),
  sets whDissolve InstancedBufferAttribute (length = list.length, all
  0), adds it, registers the mesh in the region fade registry under its
  row keys, and disposes the CLONE (not the shared template geometry!)
  in disposeRegion. Non-fade callers (none today besides enemies which
  do not use whBuildInstanced) keep sharing geometry as before.
- For SINGLE (non-instanced) scatter trees: per-tree material clone with
  onBeforeCompile hash threshold (same shader math, uniform-driven),
  registered kind 'single'; material clones tracked for dispose.

### 4.7 Per-frame driver (region-manager.js, called from player.js or game loop)

`RegionManager.updateOccluderFade(frameFadeRequests, camTarget, camWant)`:
- input: the frame's fade requests (rows + penetration depth), camera
  segment endpoints.
- for each requested row, resolve its registered fade target(s):
  instanced mesh instance index (from byProp map: propKey -> {obj (the
  InstancedMesh), instIdx}) or single-tree material.
- compute fade amount t in 0..1: t = clamp((penetration - pullFadeSlack)
  / dissolveM, 0, 1); ease t = t * t * (3 - 2 * t) (smoothstep).
- write per-instance dissolve value = mix(seed, 1, t) — the seed makes
  the noise threshold non-uniform per tree so a 50% fade looks like
  noise-eaten holes, not a 50% alpha overlay. hashMin is enforced by
  the shader-side floor.
- single-tree: uniform fadeAmount = mix(seed, t, ...) same law.
- decay: dissolve values DECAY toward 0 at a bounded rate when the row
  is not requested this frame (decayM per second, CONFIG
  occluderFade.decayPerSec = 2.0) so trees grow back smoothly and a
  camera swing doesn't strobe trees in/out. decay is applied to ALL
  registered fadeable instances each pass in a single flat loop over
  the previous-frame active list — NO full-mesh reseed per frame.
- writes are dirty-checked: only instances whose value changed by >
  1e-3 get attribute.needsUpdate (per-frame cost bounded by active
  fade count, not instance count). InstancedMesh bounding spheres:
  fade never moves geometry — bounds untouched.

### 4.8 Shader (whBuildInstanced onBeforeCompile or a shared helper)

Inject into any fadeable material ONCE (cache the patched material by
template material uuid + a `whFadePatched` flag on the material clone):
- vertex: `attribute float whDissolve; varying float vWhDissolve;
  vWhDissolve = whDissolve;` (guard `#ifdef USE_INSTANCING`? — NO:
  whDissolve is an InstancedBufferAttribute so it exists only when
  instancing is on; for the 'single' kind use a uniform instead: the
  material clone carries `whFadeUniform = { value: 0 }`, and the
  injected code reads `whFadeAmount` uniform, no attribute).
- fragment: hash3D/getAlphaHashThreshold reuse: threshold =
  max(hashMin, mix(seed_or_0, 1.0, t)) vs hash of vPosition-based
  world-ish noise. Devbot may reuse three's alphahash chunk functions
  (they are already in common chunks in r185 — verify by grep
  alphahash_fragment) OR write a self-contained 8-line hash. Either is
  fine; the valspec will check visual-noise determinism, not impl style.
- material.transparent stays FALSE; depthWrite stays TRUE (alphaHash is
  a discard-based dissolve, no sorting hazard, no ghost overlay).

### 4.9 Disposal law

- disposeRegion: cloned geometries (fadeable instanced) + material
  clones ('single' kind) are disposed. The SHARED template geometry and
  template materials are NEVER disposed by this round's code.
- buildWorld wall meshes: they are worldGroup, disposed only on full
  world rebuild today; fadeable wall clones follow the same registry +
  dispose pattern keyed by row index mapping (wall rows in (c)).

### 4.10 Explicit non-goals

- No changes to player collision push-out (CP player-side path).
- No changes to pull math for mass rows, no new camera modes, no UI.
- No changes to enemy meshes, camp fires, gather nodes, chest.
- No texture or GLB changes; no new assets; no build script changes
  (build_v8.py output unchanged by this feature: pure js/ round).
- No new concept art generation required this round (art anchors exist:
  concept-01-darkwood, day-01-darkwood, concept-05-night-ambush).
- Do NOT touch CONFIG.js beyond the new block + cameraPull comment addendum.

## 5. Files (allowed edits)

- /tmp/wh-worldfeat/prototype/js/CONFIG.js — +occluderFade block.
- /tmp/wh-worldfeat/prototype/js/region-manager.js — classifier, row
  annotations, fadeable instancing, registry, per-frame driver, disposal.
- /tmp/wh-worldfeat/prototype/js/player.js — updateCamera split + driver
  call. NOTHING else in player.js.

## 6. Acceptance criteria (Testerbot re-derives each)

A1. `node --check` on CONFIG.js, region-manager.js, player.js passes.
A2. With occluderFade.enabled = false: updateCamera behavior byte-equal
    to pre-change (single early-out path, no fade writes; grep-verified
    the disabled branch cannot reach registry lookups).
A3. Every circle row in propColliders output for regions A, B, C carries
    veg 0|1 and fadeSeed 0..1; row index/r/x/z/r/h/fy values match
    pre-change build to the byte (run the cached-table builder twice,
    diff JSON).
A4. vegClass: 'livingOak' 1, 'thornbush' 1, 'mossyStump' 1, 'whWallA' 0,
    'b3Gate' 0, 'campfireRing' 0 (or whatever the actual non-veg CONFIG
    prop names are — Testerbot derives from CONFIG), 'stoneMarker' 0,
    'gravestone' 0.
A5. fade registry: region A/B counts == counts of veg rows with r > 0 in
    propColliders (scatter rows count as 1 target each (single), prop
    instanced rows resolve to their mesh+index); C region: cell buckets
    resolve via within-bucket instance index, verified by spot-checking
    3 rows (position match: registered instance matrix at instIdx puts
    the tree at the row's x/z within 0.5 m).
A6. Player collision unchanged: with fade enabled, a player walking into
    a trunk is still pushed out (circle used in the push-out path is
    untouched — code-level check + one scripted... NO: playtest is
    Nicko's; Testerbot verifies code-level only, no browser).
A7. Mass-row fallback: a mass row (veg 0) crossed by the segment still
    triggers pull at the first mass sample; a veg row + mass row both
    present = pull at the mass sample (fade does not pre-empt mass).
A8. Disabled flag = zero fade writes (A2) AND full pull behavior for
    veg rows (legacy fallback), matching today's build byte-for-byte in
    the disabled branch.
A9. Dispose: build + dispose region A x3 cycles -> no cloned geometry
    or material leaks (registry empty, cloned geometries disposed,
    template geometry refcount untouched — DeveloperTools memory count
    NOT checked; code-level audit of dispose paths only).
A10. Zero per-frame allocation in the fade driver steady state (no `new`
    / literal object allocation inside the per-frame path; fixed arrays).
A11. Shader: patched material compiles under the existing renderer setup
    (node --check only; runtime compile is Nicko playtest territory).
    Testerbot greps injected GLSL for both attribute path (instanced)
    and uniform path (single) + confirms material.transparent stays false.
A12. No files outside section 5's allowlist touched (git status clean
    except those three).

## 7. Devbot working rules

- Work ONLY in /tmp/wh-worldfeat on feat/world-visuals. NEVER git add,
  commit, push, or stash. NEVER build (tools/build_v*.py is IO's job).
- No harness runs, no headless browser smoke tests (Nicko's bar).
- No new npm installs; no network calls.
- Journal file: /tmp/wh-worldfeat/io/devbot-p14b-notes.md (append build
  notes; do not modify specs or reports).
- Keep per-frame budget law: zero allocation in updateCamera and
  updateOccluderFade steady state; dirty-checked attribute writes only.

## 8. Risk register (Testerbot probes)

R1. Shared-geometry instance collision (section 4.6 hazard) — verify the
    clone-per-fadeable-mesh resolution is actually implemented, not a
    comment.
R2. InstancedBufferAttribute added AFTER first compile -> material
    recompile; acceptable (one-time per material), but registration must
    happen before add-to-scene so it compiles once, not per frame.
R3. onBeforeCompile double-patch on shared material clones across
    regions — the whFadePatched flag must be per material CLONE uuid,
    not per template.
R4. Dispose ordering: region dispose while fade active list still holds
    its entries -> next frame must not write into a disposed attribute
    (the driver must drop dead-region entries in the same pass).
R5. Scatter trees on region C walk the heightfield: tObj.position.y =
    whGroundFeed(...): fade must be position-agnostic (attribute lives
    on the mesh, not world position), so terrain offset cannot break it.
R6. The pull/fade split changes camera feel on B forest walks: penetration
    thresholds (pullFadeSlack 0.25 m, dissolveM 1.2 m) are the tuning
    surface; Testerbot verifies the constants are CONFIG-driven, not
    magic numbers in code.