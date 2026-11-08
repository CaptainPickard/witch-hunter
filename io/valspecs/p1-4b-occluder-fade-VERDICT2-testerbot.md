# P1-4b occluder fade — Testerbot RE-VERDICT round 2 (post-RV-4 repair)

- Round under review: P1-4b finish pass (fixspec F1–F7; RV gates in F7).
- Tree: /tmp/wh-worldfeat branch feat/world-visuals, HEAD `ae4d66e` at verdict time.
- Working tree at verdict: modified `prototype/js/CONFIG.js`, `prototype/js/player.js`,
  `prototype/js/region-manager.js`, `prototype/builds/v8-playable.html` (IO's rebuild),
  plus the three IO spec documents and this verdict file (Testerbot wrote nothing
  else in the repo; scratch probes stayed under /tmp/).
- Authority chain (read in order, all four):
  1. `io/specs/p1-4b-occluder-fade-spec.md` (original: 4.1–4.10 + A1–A8)
  2. `io/specs/p1-4b-occluder-fade-fixspec.md` (F1–F7; acceptance gates in F7)
  3. `io/specs/p1-4b-occluder-fade-addendum-w49.md` (IO addendum P1–P9, binding)
  4. Round-1 re-verdict context: its ONLY blocker was RV-4 (registration lookup
     read `fadeTable.circleByIdx`, a nonexistent field → prop rows 0 registered).
- Prior verdict file for mapping: `io/valspecs/p1-4b-occluder-fade-VERDICT-testerbot.md`.

# Artifact state checks

| Check | Result |
|---|---|
| git HEAD | `ae4d66e` (docs commit; the build is uncommitted working-tree state, per round framing) |
| `node --check` ×3 (CONFIG.js / player.js / region-manager.js) | OK ×3 |
| sha256 of `prototype/builds/v8-playable.html` | `e162ae8855e4c1c0e9d28894463239e929086b2ba41fd990aa41bc93fab172e9` — matches the IO-stated value byte-exact |
| probe1 (`/tmp/p14b-test/probe1.js`, run from /tmp/wh-worldfeat) | byte-identical to IO's `/tmp/wh49_probe1b.json` (`cmp` = 0) |
| probe2 (`/tmp/p14b-test/probe2.js`) | byte-identical to IO's `/tmp/wh49_probe2c.json` (`cmp` = 0) |
| Round-1 validator scratch (`/tmp/p14b-test-rv/`) | reused as-is: `rv4trace.js`, `rv5sim.js` re-run against the current tree; two new scratch files added by this round: `rv4trace_c.js` (C-region per-prop clone trace), `check_laws.sh` (residual greps) |

# Gate-by-gate (fixspec F7)

## RV-1 — CONFIG block (V-5 as worded): **PASS**
- `git diff prototype/js/CONFIG.js` = +12/−0: ONE `occluderFade` block inside
  `world:`, exactly 5 keys (`enabled: true, dissolveM: 1.2, hashMin: 0.02,
  pullFadeSlack: 0.25, decayPerSec: 2.0`), each with its one-line comment, block
  head comment cites `io/specs/p1-4b-occluder-fade-spec.md 4.5/4.7` (addendum P8:
  acceptance is the value/spine law, not comment text).
- The diff's added-line census grep: `player.occluderFade` hits in js sources = 0
  (no `player.*` residue of the round-1 V-24 build shape anywhere).

## RV-2 — FD var chain + diff scope (V-13/V-24): **PASS**
- FD chain byte-exact: `player.js:61` comment + `player.js:65`
  `var FD = window.WH_CONFIG.world.occluderFade;`; region-manager reads the same
  chain at `rm:2471` (`CFG.world.occluderFade && CFG.world.occluderFade.enabled`)
  and injects `hashMin` from `window.WH_CONFIG.world.occluderFade.hashMin`
  (rm:701, rm:733) — addendum P4's `WH_CONFIG.world.occluderFade.hashMin` law.
- `git diff CONFIG.js` added `cameraPull` hits = 0 (the P1-4a block is untouched;
  grep inside `git diff` returns nothing; block values byte-unchanged from HEAD).

## RV-3 — clone ownership (V-16 as worded): **PASS**
- `whBuildInstanced` (rm:1931–1981): `opts.fadeable` gate; fadeable path builds
  `geo = o.geometry.clone()`, `fAttr = new THREE.InstancedBufferAttribute(new
  Float32Array(list.length), 1)`, `geo.setAttribute('whDissolve', fAttr)`,
  `fMat = whFadePatchMaterial(o.material.clone())`, and stashes
  `im.userData.whFadeClone = { geo, mat, attr }` (rm:1948–1962) — template
  geometry/material receive nothing on the non-fadeable shared path.
- `WH_FADE_ATTRS = ['whDissolve']` (rm:650); grep `whFadeT` / `whFadeSeed` as
  ATTRIBUTES = 0 hits (both names exist only as the seed-hash FUNCTION
  `whFadeSeed(index, name)` per spec 4.4 — required, distinct).
- Amended F2 honored: zero `fadeable:` opt-in callers in the tree (all veg renders
  per-prop today); the machinery is dormant but owned (registry + disposal cover
  the clone, rm:2684–2720).
- F3 per-prop clones verified live: the prop table's `wall-`/`arch-leg`/
  `arch-plug`/`forecourt-`/`forecourt-post` rows (rm:1647/1771/1780/1869/1899)
  all carry `veg` + seed columns and ride `whBuildSingle`'s per-prop clone path.

## RV-4 — registration trace (V-19 as amended; the round-1 blocker): **PASS**
- **The P9 repair is in the tree**: `buildRegion` now builds a LOCAL
  `circleByIdx` map from `fadeTable.circles` —
  `rm:2475` (comment names the removed stale field), `rm:2479–2484`
  (`circleByIdx = {}` … `circleByIdx[String(ftC[fci].index)] = ftC[fci]`),
  reader at `rm:2504` (`var frow = circleByIdx && circleByIdx[fk];`). The stale
  `fadeTable.circleByIdx` reader is gone (grep: the identifier survives only in
  the explanatory comment + the local map).
- Predecessor trace `rv4trace.js` re-run on the current tree, output:
  - `hold_outskirts`: circles 586, veg rows 109, buildRegion group ok,
    **registered: 147**, `fadeHas(propVeg.index)` = true (prop row 8, yewTree,
    seed 0.2528…), `fadeHas(scatter0)` = true (youngBirch, seed 0.3551…);
    `apply(scatter0, 0.5)` → `{calls 1 → 2, fades 1}`; `apply(scatter0, 0)` →
    `{unfades 1}`; counters stable after.
  - This round's added C-region trace `rv4trace_c.js` on `forest_of_the_old_king`
    (WH_GROUND stubbed for the terrain read; a scratch-only deviation, not a repo
    change): circles 272, veg rows 106, **registered: 222**,
    `fadeHas(int 13)` = true (yewTree, seed 0.8360…), `apply(int 13, 0.5)` →
    counted a fade, `apply(int 13, 0)` → counted an unfade, and the counter's
    `writes: 2` shows the traverse write path executed on the clone-kind row.
- All three pinned rows of the F3 amendment traced: int prop row (registered +
  apply law), scatter single (registered + apply/unfade law), C per-prop clone
  (registered + write-through verified). Registration hygiene (P6): counts never
  exceed A5 floors, entries ride `whFadeBuckets[region|rowIndex]`, disposal
  deletes bucket + prop entry + decrements `registered` (rm:2684–2720).

## RV-5 — law sim (V-20 as worded): **PASS**
- Predecessor's `rv5sim.js` re-run: `RV5SIM-ALLPASS` (exit 0). It quotes the
  driver law byte-for-byte from source and reads ONLY
  `window.WH_CONFIG.world.occluderFade`:
  - pen 0.25 → raw t 0 → eased 0 (exact); pen 1.45 → raw t 1.0 → eased 1 (exact);
    pen 0.85 → raw t 0.5 → eased 0.5 (exact; smoothstep t²(3−2t))
  - law monotone across the 0.00–1.45 sweep; decay bounded at decayPerSec·dt,
    clamps at 0, overshoot lands exactly 0, never jumps; no negative
  - whFadeApply value law: dv 0 → v EXACTLY 0 (rest, no seed residual); dv 0.5 →
    v = mix(seed,1,0.5) exact; no-change frame → no write (1e-3 gate); sub-1e-3
    v-space change → no write; 20-step engage sweep bounded; disengaged decay →
    final v exactly 0 (A8 byte-solid); fdDrop dv 0 → v exactly 0
  - CONFIG keys consumed in the pinned order; nothing hardcoded.

## RV-6 — material clones + whFadeUniform + dirty gate (V-17/V-22): **PASS**
- Patcher variants (P3): instanced → `whFadePatchMaterial` (+attr chunk +
  `whSeedMin` uniform at rm:705/708), non-instanced →
  `whFadePatchMaterialSingle` (+uniform chunk, rm:727–739). Uniform injection
  rides the SAME object across all three surfaces:
  `m.userData.whFadeUniform`, `m.uniforms.whFadeUniform`,
  `sh.uniforms.whFadeUniform` (rm:727–734, P5) — writes flow through any surface.
- whBuildSingle clones material + injects uniform patch on every child mesh
  (rm:1997–1998, addendum P3).
- **Dirty gate is the addendum's 1e-3, as-built**: `rm:810`
  `if (Math.abs(e.t - v) <= 1e-3) return 0;` (v-space, V-22's exact-equality
  caveat from round 1 is superseded); fades/unfades counter thresholds at
  rm:811/812 use the same 1e-3 scale.
- The write walker reads module-scope `WALK_V` through the zero-closure
  `whFadeWalk` (rm:794–801, V-23); instanced path writes
  `attr.setX(e.instIdx, v); attr.needsUpdate = true;` (rm:819–823); a missing
  mesh/attr or a target whose clone objects are gone is a guarded no-op that
  keeps the registry consistent (P2).
- Guard flags: `whFadePatched` on material CLONES only (rm:695/723 early-return;
  the template never gets flagged or patched).

## RV-7 — byte-identity reruns (V-8/V-9): **PASS**
- probe1 rerun stdout byte-identical to IO's round capture
  (`cmp /tmp/p14b-test-rv/rvp1.json /tmp/wh49_probe1b.json` → 0): row identity,
  order, and values diff-clean across the refactor.
- probe2 rerun byte-identical to `/tmp/wh49_probe2c.json` (cmp = 0): the
  veg-classification + fadeSeed columns derived by the pinned laws diff clean
  (seed law byte-exact across all regions).

## RV-8 — regression families (V-6/12/14/18/26/27/29/30/31/33): **PASS**
- V-6/C14 classifier: predecessor `census.js` re-run — `VEG1 (14) misclassified:
  []`, `VEG0 (32) misclassified: []`, census PASS; post2 rows checked 3409,
  seed out-of-range 0, veg-vs-law mismatch 0, row-agreement PASS. `v35.js`
  re-run: valspec VEGLIST all 14 = 1, VEG0LIST all 32 = 0 (A4 names ABSENT, INFO).
- V-12/V-30 (pull-gate law): `fdPullBlock` (player.js:238–244) byte-equal to the
  round-1 quoted law: `if (!FD.enabled) return true; if (c.veg !== 1) return
  true; if (FD_ACT && … rid === activeId && idx === c.index) return false;
  return true;`; predecessor `v32sim.js` re-run — fade OFF → first blocked
  sample = the veg row (2), fade ON → first blocked sample = the mass row (4):
  the split is exact.
- V-14 (cameraPull untouched): diff added-line grep = 0 (see RV-2).
- V-18 (material reuse / template untouched): the patcher guard early-returns on
  an already-flagged material (rm:695/723); clone paths clone before patching;
  the shared template receives neither attribute nor patch; disposal disposes
  ONLY clone materials (`whFadeDisposeMaterial` on `whFadeMaterial` meshes +
  `whFadeClone.mat`, rm:2695–2714).
- V-26 (transparency law): patch functions set no `transparent` (grep; flags set
  are `whFadePatched` + customProgramCacheKey per P5); added-line
  `transparent` hits = 0; depthWrite stays true in the added lines (patch
  functions only), per round-1 finding still current.
- V-27 (shader reality): injected chunks are the self-contained hash arms
  (attribute chunk at rm:705–708; uniform chunk at rm:737–739); r185
  `alphahash_fragment|getAlphaHashThreshold` reuse in region-manager = 0 (grep);
  the REBUILT `builds/v8-playable.html` carries the engine alphahash chunks (14
  hits) — the rebuild was IO's, not Devbot's, per fixspec F6.
- V-29/V-31 (A8 rollback + P7 residue): `fdTick`'s first line is
  `if (!FD.enabled) { fdDrop(); return; }` (player.js:204) — disabled = one flag
  check, `fdDrop` restores any lingering t to 0 exactly
  (player.js:195–201: sets FD_ACT.t = 0 and calls
  `whFadeApply(rid, idx, 0, seed)` with the row's OWN seed — the restore is
  exact-0, no seed residual); registry invariants verified live across an
  enabled OFF→ON toggle (this round's `rv_dyn_all.js` run: registered stays 147,
  fadeHas persistent, no unregister storm).
- V-33 (P7 driver residue): player fade-scratch declarations are FD_*
  module-scope ONLY (player.js:54–85: FD_AFTER, FD_DF, FD_PEN, FD_FD2, FD_RGM,
  FD_ACT, FD_C, FD_J, FD_TT, FD_X/Y/Z, FD_TX/TY/TZ, FD_DX/DY/DZ, FD_H/FY,
  FD_LIM, FD_D, FD_D2, FD_DV, FD_HIT, FD_STALE, FD_FM, FD_CIRCLES) — grep
  `player.occluderFade` = 0; fdClaim mutates the ONE FD_ACT record in place.
- P6 (console budget): added `console.` hits in the player diff = 0; in the
  region-manager diff the only added-line `console.log` is inside a comment
  ("No new console.log in steady state"); rm console count 4 → 5 is comment
  accounting, zero new runtime logs.
- P1/P2 spine (static): single mix site `v = dv > 0 ? sv + (1 - sv) * dv : 0`
  (rm:806–807); `sv` from the row's OWN seed with a defined fallback chain; raw
  eased t rides the call as dv (player.js:114 `rec.t` → fdApply's dv, no remap);
  decay writes only via whFadeApply (bounded, never jumps); `fadeHas` fallback
  in the driver is gated on the registry bucket
  (player.js:229 `if (fdClaim(FD_C))` = fdClaim consults `fadeHas`; the claim
  branch handles unregistered rows by leaving them with the pull).

# Deviations disclosed (non-blocking)

1. Scratch-only: the C-region trace (`rv4trace_c.js`) stubs `WH_GROUND`
   (`footY/heightAt/sample/mesh`) because regionC is terrain-enabled and node has
   no terrain grid. This is a test-harness stub, not a repo change; the row it
   traces is the real registration path.
2. The prior round-1 verdict file (`VERDICT-testerbot.md`) documents V-24 as the
   old `player.*` FAIL; the round-2 tree is the repaired `world.*` shape (verified
   at RV-1/RV-2). The stale V-24 text is superseded by this file.
3. P9's pinned floor is "≥ 100 per tree-full region"; hold_outskirts registered
   147 and forest_of_the_old_king registered 222 — both comfortably above; the
   A5 floor of 586 counts CIRCLES not registrations (registration covers veg rows
   only, by design), so no contradiction.

# Verdict

ALL RV-1 … RV-8 gates PASS on the current tree (8/8, 0 blocking). The RV-4
repair (local `circleByIdx` from `fadeTable.circles`) is verified live: prop rows
and scatter rows on hold_outskirts AND per-prop clone rows on the terrain region
register, apply, and unfade with exact counters. Round-2 verdict = **PASS**.

Testerbot: no edits to /tmp/wh-worldfeat except this verdict file; no git
operations (NO-GIT honored); scratch under /tmp/p14b-test-rv/ only.
