# whanim3 — swing sight: blade orientation + texture intake, playtest-grade

Round: whanim3 (B1+B2+B3 from the 2026-10-01 playtest assessment). Gate:
IO spec (this file) -> Testerbot validation spec + harness -> Devbot build
-> Testerbot independent validation -> IO commit + push.

## 0. Background + problem (from the live assessment, evidence on file)

io/reports/2026-10-01-playtest-why-no-anim-assessment.md proved on the live
tree (real probes, real screenshots):

- **B1 (game defect):** the sword's blade leads BACKWARD through the swing.
  Player.setWeapon (player.js L128-138) parents the longsword to the
  skinned R_Hand socket and applies `mesh.rotation.set(0, 0, Math.PI)`
  claiming "At the strike pose the animated hand's +Y aims +Z, so the tip
  leads -Z". Live probe of the vendored loader's actual hand basis during
  the strike contradicts the comment: hand yAxis at strike t=0.20 world =
  (-0.29, +0.28, +0.91) -> mesh +Y (blade axis) points +Z-ish (AWAY from
  the enemy across facing (0,0,-1)), and the measured tipDotFacing during
  a real click-attack was negative in 5 of 6 samples. Also Nicko
  observed hilt-first contact in play. The PI Z-rotation flips blade
  +Y -> -Y in hand space; with the clip's hand orientation this leaves
  the TIP pointing behind the swing arc. Result: hilt-first swings.
- **B2 (route presentation):** on the WebUI playtest route (8787
  /playtest/), the enforced CSP (api/helpers.py template,
  `connect-src` WITHOUT blob:) blocks the FETCH of embedded-GLB texture
  blob: URLs (208 console errors). Characters load as skinned meshes
  (mixer live, 6 clips, 0 stand-ins) but ALL textures are stripped -> the
  white/grey mannequins Nicko reports. data: URIs in img-src ARE allowed;
  THREE.TextureLoader(data:) proven OK under the enforced CSP in-page.
- **B3 (hygiene):** rail-button route serves no-store (verified), but the
  single-file build artifact is stale (pre-anim2). Rebuild + verify.

## 1. Scope: combat/presentation intake only

IN: prototype/js/player.js (setWeapon rotation), prototype/js/enemy.js
(bandit axe mount = same class of defect; verify orientation before
touching), prototype/js/assets.js (texture intake hook), rebuild of
prototype/builds/v7-playable.html, README playtest-routes note if
trivially stale, io/reports/.
OUT (hard): combat FSM math (attackPhase windows/timings stay EXACTLY as
committed at dc697ce), world-visual items (lighting/bounds/LOD, doc-61
P0-3..7/P1), anim clip data (GLBs are frozen assets), CONFIG timings,
the WebUI repo (Option A blob:/connect-src is EXPLICITLY OUT — game-side
fix only), sui/, docs/planning (read-only reference).

## 2. B1 — blade orientation fix (player longsword)

Files: prototype/js/player.js (setWeapon L128-138 only).

Design: replace the single sign-flip guess with a MEASURED orientation
that is proven at the strike instant, keep it as ONE rotation composed
ONCE at set-up (no per-frame writes — the rig owns the hand):

- At setWeapon, after hand.add(mesh): compute hand's bind/current
  orientation ONCE. The invariant the fix must satisfy at strike
  (clip time = CFG attackClipStrikeFraction of WH_Attack1, measured
  t=0.20 in probes): the blade's world axis (mesh +Y after the fix's
  rotation) must have positive dot product with the player's facing
  direction AND point forward-downward through the arc (dot < -0.5
  against facing... measured goal: tip crosses to dot >= +0.5 by the
  strike sample).
- Deterministic method (no trial-and-error in gameplay code): at
  setWeapon, read hand world quaternion at REST (mixer idle), compute
  the rotation R such that R * Y_hand maps the blade onto the desired
  local axis, cache it as a local const; apply as
  `mesh.quaternion.copy(R)` (not rotation.set on Euler) so no
  euler-order drift. Verify by probing WH_Attack1 at t=0.2: blade
  worldDot(facing) >= +0.5, and at t=0.45 (recover) the pose returns to
  an idle-carry that matches the current screenshot's vertical back
  carry within 30 deg.
- The bandit axe MUST be verified with its own probe; if the measured
  axe orientation is correct at strike (NOT backwards), DO NOT touch
  enemy.js (the defect may be player-only); if backwards, apply the same
  measured-rotation method on the axe mount (enemy.js L58-64) and log
  the numbers.

## 3. B2 — texture intake: blob->data at the loader edge (CSP-immune)

Files: prototype/js/assets.js ONLY (loader hook), never the vendored
loader files (gltf-loader.classic.js / three.classic.js stay untouched).

Design: intercept the embedded-image fetch BEFORE the
ImageBitmapLoader's fetch() runs, by installing a LoadingManager
URL-modifier on the GLTFLoader used by loadOne (L153):

- `var mgr = new THREE.LoadingManager();` + `mgr.setURLModifier(fn)`;
  construct `new window.WHGLTFLoader(mgr)`.
- The modifier: for `blob:` URLs ONLY, fetch the blob ONCE at preload
  time when NOT under a CSP-blocked origin (feature-detect: try
  fetch(url); on failure convert via FileReader.readAsDataURL =>
  data: URI (img-src includes data:). The modifier returns the data:
  URI for the texture-loader path. Buffer/blob GLBs ALSO flow through
  bufferUri (gltf-loader L3136 FileLoader path) — limit the modifier
  to sourceDef.mimeType image/* blobs: distinguish by url
  `blob:...` + a Set the loader populates? No: the loader creates
  blob URLs ONLY for embedded images (sourceDef.bufferView +
  mimetype image/*); the .glb file itself is fetched directly (not
  a blob URL) — so mapping EVERY blob: URL through data:-rewrite is
  safe and simple. Use try-fetch fallback with a module-level
  in-memory Map<url, dataUri> so each blob converts once.
- Keep the existing timeout/stand-in machinery untouched: this hook
  only changes HOW embedded images are fetched inside the loader.
- prepTemplate (L124-148) already force-updates map filters — no
  change; the hook must produce textures whose image is a decodable
  bitmap exactly like before (TextureLoader(data:) proven).
- Acceptance: on the 8787 /playtest/ route (enforced CSP): ZERO
  "violates CSP" console errors during a full asset load + 10s
  gameplay; player body material.map.image.width >= 512; the
  screenshot is visibly textured (cloak colors present). On the 8792
  clean origin: byte-identical behavior to today (regression must
  pass v2 asset audit 26/26).

## 4. B3 — build freshness

- Rebuild prototype/builds/v7-playable.html via tools/build_v7.py
  AFTER B1+B2 verify clean; confirm the build now contains
  CharacterAnim + the data: intake hook (grep checks), and that its
  gameplay smoke (page load + one attack, WH_DEBUG present) passes
  via file:// or the local origin — the artifact is not the primary
  playtest surface but must not stay misleading.

## 5. Preservation floor (measured at dc697ce, real runs this session)

- ds1 validation: 18/18 PASS, 0 crashes (3x verified + Testerbot).
- weave v7: 18/18 checks, v2 + v3 regressions PASS.
- Enemy windup telegraph numbers (bandit raise-back w 0.87->0.68
  monotonic across 0.55s) = MUST remain in probes post-build.
- Weapon probe values measured today become the baseline for the
  orientation ACs: strike-frame hand yAxis = (-0.29,+0.28,+0.91),
  tipDotFacing must FLIP from the current negative-dominant signature
  to positive-dominant after B1.
- No CONFIG timing values change; no clip data changes (GLBs
  bit-frozen at the whanim2 hashes; Testerbot re-verifies A2-style).

## 6. ACs (Devbot accepts; Testerbot validates independently)

- AC1 (B1-player): on 8792 + built locally: during a REAL click-attack
  (organic mouse events), sampled blade axis worldDot(facing) is
  POSITIVE at strike-window samples (t=0.20 and t=0.30; >= +0.4 both)
  and the idle carry pose is visually within 30 deg of today's
  vertical back-carry. Evidence: page probes + screenshot at freeze
  frame.
- AC2 (B1-bandit or verified-skip): probe the bandit axe at windup +
  strike (enemy attack fsm). EITHER measured-correct orientation is
  proven unchanged (no enemy.js edit; log evidence) OR the axe gets
  the measured-rotation fix and blade/edge leads the swing at strike
  with arm-travel telegraph retained (w-monotonic windup intact).
- AC3 (B2): on 8787 /playtest/: zero CSP violations during full load
  + 10s gameplay; player material map width >= 512; screenshot
  visibly textured (cloak dark + silver sword). Zero stand-ins.
- AC4 (regression): ds1 18/18 + weave 18/18 + v2 26/26 asset audit +
  v3 PASS on the fixed tree (both origins where the suite defines
  them); enemy telegraph numbers preserved (section 5 baseline).
- AC5 (B3): rebuilt single-file build contains CharacterAnim + the
  intake hook; its smoke load (page boots, WH_DEBUG present, one
  attack fires) passes on the clean origin; grep shows the build's
  sources == dev sources at build time (shas recorded in the report).
- AC6 (no-scope-drift): git diff at verdict time touches ONLY
  player.js, enemy.js (if AC2 needed it), assets.js, the rebuilt
  v7-playable.html, harness files under tests/ (harness authored by
  Testerbot), io/reports/. ZERO edits to CONFIG.js, game.js,
  moveset.js, anim.js, spec GLBs, vendor/*.

## 7. Environment + harness laws (standing, from ds1/weave rounds)

- Playwright sync API, headless chromium --enable-unsafe-swiftshader;
  page-time (performance.now()) bands only; sim-frame counting per
  references/playwright-headless-frame-clock-gotchas-2026-09-30.md
  (pending-promise samplers are FORBIDDEN; window-buffer rows +
  instant returns).
- Organic-path law: inputs via real key/mouse events; state-reads
  via WH_DEBUG fine; state-mutations only as setup acts, never as
  assertion basis.
- No node on the box; no ESM/class in game JS; vendored loader files
  are read-only.
- No commit/push by children. IO is the git gatekeeper, commits ONLY
  after the Testerbot PASS verdict.

## 8. Dispatch notes

- Testerbot FIRST: authors its validation spec (framing ACs 1-6 into
  per-AC checks with the probe recipes), SMOKE-RUNS the harness on
  the PRE-build tree: AC1/AC2 expected FAIL (sword defect present),
  AC3 expected FAIL (CSP kill), AC4/AC5/AC6 PASS/neutral — proving
  the harness is wired and honest. Then freeze that profile as the
  baseline.
- Devbot: implements B1/B2(/enemy if measured), re-runs Testerbot's
  harness WITHOUT editing it, records per-AC numbers in
  /tmp/delegation_result_whanim3-dev.md.
- Testerbot re-validate: fresh harness run, verdict JSON per-AC,
  regression floor re-run, freeze-table of post-build shas.
- Amendment law: mid-flight changes -> both specs amended with
  AMENDMENT A1 markers + re-frozen anchors (wh-econ-spike1 lesson 1).

## 9. Amendment log

(none yet)