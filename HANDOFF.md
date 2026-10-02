# WITCH HUNTER WORLD — R3-R6 HANDOFF (2026-10-02, IO)

State at handoff: R2 LANDED. feat/world-visuals tip = be1561d (origin-verified).
This file + the committed specs make R3-R6 executable WITHOUT chat context.

## REPO STATE (all on origin, verified via ls-remote)
- dev = integration branch: eacff4a (R1), f881dac (whanim1), 02ca0ac+d7e0b41
  (combat), dc697ce (whanim2), 33d0d80 (combat integrity) — all validated.
- feat/world-visuals (world rounds): c37a9f7 pre-R2 chain, then:
  - 46454c5 R2 gate specs (IO devbot spec + Testerbot valspec)
  - 0406e64 R2 VALIDATED MARKER — full9 verdict PASS flakes=0
    (io/reports/2026-10-01-world-r2-implementation.md)
  - 35644fd R3 gate spec (io/specs/devbot-spec-wh-world-r3.md, ACs P1-P6)
  - be1561d R4/R5/R6 draft specs + R4 bake tool + A3 settle matrix + lane log
- MAIN CHECKOUT /workspace/witch-hunter = dev @ 33d0d80 (DO NOT WORK IN IT;
  its server on port 8791 belongs to landed work — leave running).
- WORKTREE LAW: world-branch work ONLY in /tmp/wh-worldfeat (branch
  feat/world-visuals). If /tmp wiped: cd /workspace/witch-hunter && git
  worktree prune && git worktree add /tmp/wh-worldfeat feat/world-visuals.

## WHAT R2 DELIVERED (the foundation you inherit)
- Lighting: Neutral tonemap + exposure 1.15, hemi-only fill (region-scaled
  1.35/0.7425), moon directional (0xa8bce6, 0.45, -z, 30deg), player
  hip-lantern (parented yawFrame, dist 12, decay 2), fixed 4-PointLight pool
  with nearest-socket handoff + flame cards, campfire + waymarker props in B.
- Harness (THE pattern to reuse): tests/wh_world_r2_validation.py assembled
  from tests/r2parts/part01-10.py (cat). HARNESS LAWS (each paid for):
  1. SwiftShader ~1-3fps; game dt clamp 0.05 => game time ~15x slower than
     wall; poll with wall-generous bounds, never fixed game-time sleeps.
  2. NO preserveDrawingBuffer: forced render + toDataURL in SAME evaluate.
  3. Camera lerps to teleports: wait for settle before screen-space probes
     (vz > 1 = behind camera = retry).
  4. Enemy pos can NaN transiently: guard x !== x, reload-retry.
  5. Server identity check before reuse: served CONFIG must contain
     lightPool AND ambientIntensity: 0; else self-spawn on EPHEMERAL port.
  6. Per-AC try/except (exceptions become recorded FAIL data); exit code
     ALWAYS 0; final stdout line = one JSON verdict object.
  7. NEVER write example key-shaped literals in harness files (the scope
     self-scan greps the diff and will hit its own examples).
  8. Assembled file = build artifact: edit PARTS then re-cat; watch for
     shadowed duplicate defs across parts (they caused the L7 bug).
- Floor machinery: part10 ac_floor runs R1 harness as subprocess (WH_BASE_ROOT
  shared); 5 evidence-backed waiver classes with in-run re-verification
  (A2-dev-baseline, A3-settle-subprobe, A4-nightrig-chain, A6/A7-drift,
  A8-surface-FP). Full rationale in the R2 report.

## THE GATE (Nicko standing order — non-negotiable structure)
1. IO agent writes round spec io/specs/devbot-spec-wh-world-Rn.md with
   LIVE-TREE-VERIFIED anchors (line numbers).
2. Testerbot valspec BEFORE Devbot: io/specs/testerbot-spec-wh-world-Rn.md.
3. Devbot implements (dispatch by PROFILE ONLY — never bare model names;
   glm bare names resolve dead credentials; profile carries its own).
4. Independent validation (PASS/FAIL with evidence, verdict JSON).
5. IO agent ONLY commits + pushes. One marker commit per round:
   "feat: world-rN - one-line + gate trail | carrier-req: Testerbot
   revalidates harness on lane recovery".
- LANE STATUS: the glm-5.3 Testerbot child lane died 10x total (finalize:
  "API call failed after 3 retries: Non-streaming API call timed out") —
  valspec+amend runs succeed, LONG SINGLE-GENERATION files die. If
  dispatching testerbot profile: lean contracts, chunked writes, steer
  early. If the lane is unusable: IO-authored valspec+harness is
  PRE-AUTHORIZED (Nicko carrier-req ruling) WITH the loud
  "Testerbot revalidates on lane recovery" note in EVERY commit + report.
  Never silently fallback; never switch models mid-round.

## NEXT ROUND: R3 — INTERNAL-RES PIXELATION (P0-4)
- Spec READY to execute: io/specs/devbot-spec-wh-world-r3.md (base pin
  0406e64; read it fully). Summary: CONFIG.renderer.internalResDiv=2;
  setupRenderer + resize use setPixelRatio(1) + setSize(round(w/div),
  round(h/div), false); style.css #wh-canvas += image-rendering: pixelated
  (+ crisp-edges fallback). ACs P1-P6 in the spec. Retune = exactly-once.
- Testerbot valspec for R3: NOT WRITTEN (lane died #10 mid-authoring).
  Either retry the lane with a hard 130-line cap, or IO-author it under
  the pre-authorization (with the note).
- Do NOT touch: tone mapping/exposure/lighting keys, L10 probe, HUD DOM,
  reticle math, region-manager.js, index.html (frozen).

## THEN: R4 (re-scoped), R5, R6 — DRAFT SPECS COMMITTED
- R4 (P0-7 re-scope): io/specs/devbot-spec-wh-world-r4-DRAFT.md. The audit's
  premise is stale: races_regen has ZERO pixelated variants; rigged bodies =
  1x 2048x2048 smooth JPEG atlas each (28-33k tris, 1 material, 1 skin).
  Mechanism ruled by bake evidence (io/specs/wh-r4-bake-all3-tool.py, all 3
  atlas PNGs vision-QA PASS): OFFLINE BAKE = commit the 3 pixelated PNGs
  (512 NEAREST + 5-bit posterize), assets.js postload swaps m.map. rig/anim
  untouched; anim2 harness + R1 A2 re-check ride the round. CONFIG kill
  switch assets.pixelatedBodies.
- R5 (P0-5 + P1-4 camera half): io/specs/devbot-spec-wh-world-r5-DRAFT.md.
  Radial clamp + prop colliders (GROUND_META footprints) + camera ground
  clamp; anchors verified (clampPlayer region-manager.js:99-113,
  clampPlayerToBounds game.js:455-465, updateCamera player.js:896-948).
- R6 (P0-6): io/specs/devbot-spec-wh-world-r6-DRAFT.md. Tag template
  geometry/materials/textures userData.whShared; disposeRegion skips tagged;
  renderer.compile + initTexture during prewarm spread over 2-3 frames.
  disposeRegion (region-manager.js:371-390) currently disposes EVERYTHING.
- Doc 61 section 7 has the M-bar tables (M-05/06/08/13/14/15/16/22).

## ROUNDS AFTER R6 (parked, do not start without Nicko)
- B0 runtime wire-in: 17 owned assets (crypt kit, church kit, weapons incl
  gravedigger-lantern as visible player lantern, race bodies) — after R2,
  0 meshy credits, rides later rounds.
- B4 camp decor (240cr) + B5 gear (90cr): BLOCKED on (a) P1-10 rest-space
  round landing AND (b) Nicko's explicit session-window ruling. ASK.
- MESHY LAWS if any asset work: 2610 credits left; key in
  /home/hermeswebui/.hermes/profiles/io/secrets/meshy_key (chmod 600, env
  only); image-to-3d 15cr flat; polycount target CAPS AT 2000 (HTTP 400
  above); NEVER back-to-back submits (400 wall ~19 tasks); thumbnail from
  top-level thumbnail_url; 1 retry max then skip-and-log.

## GROUND RULES (all rounds)
- Vanilla JS only: IIFE, window globals, no ES modules, no class syntax.
- NO rigging/skeleton work (anim round owns it). Art pipeline = raw mesh
  as-is + color pixelation only.
- No node on the box: Playwright sync API, headless chromium
  --enable-unsafe-swiftshader, page-clock timing only. PIL 12.3.0 available.
- Secrets: env-only; grep patterns are self-referential - grep for
  msy_[A-Za-z0-9]{8} not the bare prefix. No key-shaped example literals.
- Copy rule: "at no cost to you", never "free"; no hardcoded agent names.
- docs/ + sui/ READ-ONLY (doc 59 run-log appends belong to asset batches).
- Surgical-commit law: classify every hunk before staging; combat/anim
  hunks in shared files stay byte-identical.
- Push: cd /tmp/wh-worldfeat && git push
  https://github.com/CaptainPickard/witch-hunter.git
  feat/world-visuals:feat/world-visuals ; verify with
  GIT_CONFIG_GLOBAL=/dev/null git ls-remote ... refs/heads/feat/world-visuals
- FINAL REPORT per round: io/reports/YYYY-MM-DD-world-Rn-implementation.md
  (per-AC evidence, deviations, drift notes) + closing summary to Nicko
  (hashes, push verification, what he SEEES at /witchhunter/, parked items).