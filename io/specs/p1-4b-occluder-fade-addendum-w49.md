# P1-4b IO ADDENDUM — wake 49 finish pass (binding; amends fixspec F1–F7)

IO addendum, 2026-11-08 ~17:05Z. Authority: IO is the spec author (P1-4b
spec + fixspec + this addendum are one contract). The fix child
(deleg_50db966c) exhausted its budget mid-rewrite; IO completed the pass
inline (HUSK law, wake-44 precedent). Testerbot re-verdicts against THIS
file + fixspec + spec together. Allowlist unchanged (CONFIG.js,
player.js, region-manager.js ONLY).

The data-verified findings below supersede any narrower wording in the
fixspec where they conflict (both agree everywhere F1–F7 already spoke;
this file pins what F1–F7 left unspoken or what the fix child broke).

## P1. whFadeApply VALUE law (fixspec F4 completion; the seed-mix contract)

- `dv` arriving in whFadeApply is T-SPACE (the raw eased dissolve 0..1).
  The GPU-facing value v = mix(sv, 1, dv) for dv > 0; v = EXACT 0 for
  dv <= 0 (restore/disengage-landed byte-solid law; NO seed residual at
  rest — a tree at rest must render 100% solid, V-2's rest-state law).
- The DRIVER (player.js fdApply) passes the RAW eased dv — no seed
  pre-mix anywhere player-side. Exactly ONE mix exists, in whFadeApply.
- Decay runs on the record's eased t (rec.t -= decayPerSec * dt,
  clamped at 0, never jumps) and passes the decayed t through the same
  single-mix value law. Release at rec.t === 0.
- fdDrop (rollback + stale-guard) passes dv = 0 → v = 0 exactly (A8).
- Dirty gate is V-SPACE: |e.t - v| > 1e-3, where e.t stores the last
  written v. No attribute/uniform churn on no-change frames (V-22).
- fade/unfade counter semantics (v-space): fades++ when dv > 0 and the
  old e.t <= 1e-3; unfades++ when new v <= 1e-3 and old e.t > 1e-3.

## P2. Path selection by KIND, not instIdx (fixspec F3/F4 completion)

whFadeApply selects its write path by e.kind ONLY:
- kind 'instanced' (whBuildInstanced opts.fadeable clones): e.mesh set,
  e.instIdx >= 0; write e.mesh.geometry.attributes.whDissolve.
  A missing mesh/attribute is a guarded no-op (return 0).
- kinds 'clone' (CONFIG prop clones) and 'single' (whBuildSingle
  scatter trees): NON-instanced meshes — e.mesh is null by design;
  the write walks e.tObj.traverse for meshes flagged
  userData.whFadeMaterial and sets material.uniforms.whFadeUniform.value.
- NEVER index e.mesh.geometry for a 'clone'/'single' row (the fix
  child's `e.mesh.geometry` dereference on mesh:null rows is a
  guaranteed TypeError on the first camera-tree contact — REMOVE).
- The traverse walker is a MODULE-LEVEL function reading module-scope
  scratch (WALK_V) — zero per-call closure allocation (V-23 law).

## P3. Patchers — which variant attaches where (fixspec F2/F5 completion)

- whFadePatchMaterial (attribute variant, whDissolve) is used ONLY by
  the whBuildInstanced fadeable clone path (real InstancedMesh).
- whFadePatchMaterialSingle (uniform variant, whFadeUniform) is used by
  BOTH non-instanced paths: the CONFIG prop clones (buildRegion ~2440)
  and whBuildSingle (scatter trees). The fix child attached the
  ATTRIBUTE variant to non-instanced meshes (undeclared attribute →
  vWhDissolve always 0 → the uniform write is dead): REMOVE.
- whBuildSingle returns THE tree object that gets group.add'ed — the
  scatter span must build via whBuildSingle ONCE (no double instance,
  no stock-material tree left visible while the patched clone sits
  unparented). Order: tObj = whBuildSingle(asset); group.add/cull push;
  register (mesh + tObj = the SAME object).

## P4. Shader reality (three r185 classic build, prototype/vendor)

The bundled three.classic.js (REVISION 185) ShaderChunk inventory:
- MISSING: alphahash_pars_vertex, alphahash_vertex, batching_pars_fragment,
  batching_fragment, worldpos_pars_fragment, worldpos_vertex.
- PRESENT: alphahash_pars_fragment, alphahash_fragment,
  batching_pars_vertex, batching_vertex, dithering_fragment, common,
  begin_vertex, project_vertex.
Therefore (fixspec F5 completion):
- DROP every `#include <alphahash_pars_vertex>` and
  `#include <batching_pars_fragment>` (compile throw on the classic
  build — undefined chunk references do NOT silently no-op).
- The self-contained inline world-hash arm stays (spec 4.8's sanctioned
  "either" arm; V-27 law holds without the alphahash chunks).
- vWorldPosition is NOT guaranteed on these materials: declare the
  patch's own `varying vec3 whVWorldPos;` in BOTH stages and compute it
  by extending project_vertex:
    vec4 whW4 = vec4(transformed, 1.0);
    #ifdef USE_INSTANCING
      whW4 = instanceMatrix * whW4;
    #endif
    whVWorldPos = (modelMatrix * whW4).xyz;
  (modelMatrix is a program built-in; USE_INSTANCING is defined by
  three for InstancedMesh and absent for the single clones.)
- Threshold arm (both variants), dithering_fragment position:
    float whHashX = fract(sin(dot(floor(whVWorldPos),
      vec3(127.1, 311.7, 74.7))) * 43758.5453);
    float whHashD = (vWhDissolve <= 0.0) ? 0.0
                  : max(whSeedMin, vWhDissolve);
    if (whHashX < whHashD) discard;
  The dv<=0 → threshold EXACTLY 0 arm is binding: trees at rest are
  byte-solid (the hashMin floor applies only WHILE dissolving — its
  CONFIG comment's stated purpose).

## P5. Uniform injection (fixspec F5's "VALUE must derive from CONFIG")

Both patchers, inside onBeforeCompile:
- sh.uniforms.whSeedMin = { value: window.WH_CONFIG.world.occluderFade
  .hashMin } (compile-time read; a hashMin change is a recompile event —
  CONFIG is a const table, acceptable and pinned).
- Single variant ONLY: create-or-reuse m.userData.whFadeUniform = { value: 0 }
  ONE object per material clone; expose the SAME object on
  m.uniforms.whFadeUniform (registry surface) AND bind it into
  sh.uniforms.whFadeUniform (same reference; value updates flow without
  re-binding). Declared in VS as `uniform float whFadeUniform;` and
  consumed in begin_vertex: `vWhDissolve = whFadeUniform;`.
- m.customProgramCacheKey = function () { return 'whfade:' + m.uuid; }
  on EVERY patched clone — without it three's program cache shares one
  program across clones with identical onBeforeCompile text and the
  second clone's uniform writes bind to the first clone's object.

## P6. Registration hygiene (fixspec F3)

- whFadeRegister: the intermediate `whFadeBuckets[bucket] =
  whFadeList.length;` line is DEAD (overwritten by the entry assignment)
  — remove; buckets map bucket → ENTRY.
- Kinds in the live registry: 'clone' (CONFIG props), 'single' (scatter),
  'instanced' (dormant whBuildInstanced path, no caller this round —
  F2 unchanged). The debug registrar passes every kind through.

## P7. Player.js residue

- Duplicate `var FD_PEN = 0;` declaration in the FD scratch block
  (fix child artifact) — one declaration only.
- fdApply engaged branch: delete the player-side seed pre-mix
  (FD_SEED/FD_V fold) — see P1. FD_SEED/FD_V scratch removed.
- No other law in the fd* chain changes (fdRowHit/fdClaim/fdDrop/
  fdPullBlock/fdTick verdict-passed forms stand).

## P8. Acceptance framing for the re-verdict

- RV gates = fixspec F7 (RV-1..RV-8) re-run against the FINISHED worktree,
  adjudicating P1..P7 as binding law alongside fixspec + spec.
- P-regressions watch: V-2 (var law), V-12/V-14 (pull law byte-form),
  V-20 (law sim: pen 0.25→t 0; 1.45→t 1 eased 1; 0.85→t ~0.5 eased 0.5;
  decay bounded), V-22 (1e-3 v-space gate), V-23 (zero steady-state
  alloc: WALK_V scratch, no per-frame closures), V-25/V-26 (patch flag +
  opaque/depthWrite), V-27 (self-contained hash + CONFIG-derived
  whSeedMin + the P4 conditional arm), V-29 (dispose), V-33 (RNG law).
- A re-verdict gate that quotes pre-refactor strings (e.g. the exact
  alphahash include line) adjudicates against P4's reality — the
  missing-chunk pins REPLACE the old wording, not violate it.

## P9. circleByIdx reality — buildRegion's registration lookup (RV-4)

The re-verdict (wake 49 IO re-dispatch, deleg re-run 1) found the fix
child's registration gate reading `fadeTable.circleByIdx` — a field
whPropColliders NEVER produced ({circles, exempt, complete} only). The
reader existed from the FIRST Devbot build; Testerbot's round-1 gates
passed because they exercised whFadeApply/fadeHas directly (V-8/V-9/
V-19 as worded) and never traced registration through buildRegion.

- buildRegion constructs its own lookup IN PLACE: a local
  `circleByIdx` object keyed by `String(row.index)` over
  fadeTable.circles (exempt rows stay out — V-30). The prop loop
  resolves its row via that map; the stale `fadeTable.circleByIdx`
  reader is removed.
- RV-4's pinned-row trace must now run on the repaired branch: an int
  prop row (e.g. hold_outskirts row 8), a scatter single, and the
  C-region per-prop clone path all register.
- No other consumer of the nonexistent field exists (grep 1 hit was the
  reader; now 0).
