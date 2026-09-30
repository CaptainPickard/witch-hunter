# DEVBOT SPEC — Witch Hunter World R1: ground-align correctness + ground material
Repo: /workspace/witch-hunter, branch dev. Base commit: 8e8a015 (docs world-audit).
Authority for this round: docs/planning/61-world-audit.md (Claude Opus 5.5 world audit,
verbatim copy, committed) items **P0-1** and **P0-2** ONLY. The audit's design and
numbers are the contract; do not substitute re-derived designs. When the audit text and
this spec disagree, THIS SPEC wins (it is the spec of record); report the divergence in
implementation notes instead of improvising.

## TREE-STATE CONTRACT (read first)
You build on the LIVE DIRTY working tree (weave + combat-ds1 workstreams are
implemented but unvalidated/uncommitted; that is intentional and frozen):
- Freeze file: /tmp/wh-world-r1-freeze-20260930.txt (HEAD 8e8a015 + sha256 of every
  dirty/untracked artifact as of 2026-09-30T16:04Z).
- Your allowed edit surface is EXACTLY 5 files:
    prototype/js/assets.js
    prototype/js/region-manager.js
    prototype/js/game.js
    prototype/js/CONFIG.js
    prototype/js/enemy.js
- Files you may RUN but must NEVER EDIT: tests/wh_v7_weave.py,
  tests/wh_combat_ds1_validation.py, tools/build_v7.py, prototype/js/spells.js,
  prototype/js/player.js, prototype/vendor/*, prototype/index.html.
- NO git commands that mutate state (no commit/push/checkout/restore/stash).
  NO edits under sui/, docs/, art-direction/, io/. NO new files anywhere except the
  deliverable notes named in DELIVERABLES.
- If a needed edit falls outside the 5 files, STOP and file an amendment request in
  your scoped README (name the file, the reason, the exact spec line) instead of
  improvising. That is a healthy gate signal, not a failure.

## SCOPE
Two fixes, both S-sized, both code-only:
1. P0-1: props and characters ground-align correctly at any scale (holder structure).
2. P0-2: ground material renders correctly (color/mipmaps).
Explicitly OUT of scope: P0-3..P0-7 and all P1/P2 (lighting rig, internal-res,
bounds, region lifetime, pixelated bodies, LOD, etc). Lighting values, region
boundaries, spawns, asset load lists stay byte-identical.

## PRECISION MAP (verified against the freeze tree 2026-09-30; re-read target
lines +/-3 before each edit — lines drift as you edit)
- prototype/js/assets.js
  - :85 `var GROUND_META = {}` (template uuid -> {height, width}).
  - :110-120 `groundAlign(group)` — current implementation shifts
    `group.position.y -= minY` ON THE TEMPLATE ROOT and measures
    {height, width}. Keep measured values; the SHIFT moves into the new structure.
  - :161 the single call site `groundAlign(root)` inside the loader.
  - :191-195 `instance(name)` -> `tmpl.clone(true)`.
  - :196-215 `window.WH_ASSETS` export block; `groundHeight(name)` (:206-211)
    reads GROUND_META[tmpl.uuid].height (fallback 1.8). Its semantics (measured
    template height) MUST NOT change — consumers: game.js:625, region-manager.js:342.
- prototype/js/region-manager.js
  - :241-251 `makeGroundTexture(regionId)`: CanvasTexture; :246-248
    `magFilter=NearestFilter; minFilter=NearestFilter; generateMipmaps=false`.
  - :250 `tex.repeat.set(gtc.repeat, gtc.repeat)` (CONFIG.world.groundTexture.repeat=12).
  - :286-299 ground mesh: `MeshStandardMaterial({ color:
    CFG.world.groundColorA|groundColorB, map: makeGroundTexture(...), roughness:1,
    metalness:0, side:DoubleSide })` on `CircleGeometry(CFG.world.groundRadius, 48)`.
  - :323-329 prop placement loop: `obj = WH_ASSETS.instance(p.asset);
    obj.position.set(p.x, 0, z); obj.rotation.y; obj.scale.setScalar(p.scale)`.
    THE BUG: y is overwritten to 0 AFTER the template's baked offset, and scale
    is applied after, rescaling the baked offset wrongly.
  - :335-346 enemy body load: instance -> eScale = characterHeight / groundHeight
    -> scale.setScalar -> enemy.setBody(eBody).
- prototype/js/game.js
  - :619-637 player/boot asset load: pBody instance (:623), pScale from
    groundHeight (:624-625), `pBody.scale.setScalar(pScale)` (:626),
    `game.player.setBody(pBody)` (:627). Sword: :628-631 (DO NOT TOUCH — combat
    audit owns weapon grip; only add the one-line guard described in D1.5).
  - :202-216 the v7 armed emissive block reads `p.sword.material` on a Group.
    Keep-alive: this block MUST keep working exactly as today.
- prototype/js/player.js (READ-ONLY, you make NO edits here)
  - :113-122 `setBody`: bodyBaseY = meshRoot.position.y || 0; bodyBaseX likewise;
    adds body to yawFrame. setBodyBob (:146-149) writes
    `body.position.y = bodyBaseY + bobY`. Direct write-sites: :807, :823, :852
    (absolutes off bodyBaseY). CONSEQUENCE: your player-side fix is to set
    meshRoot.position.y (scaled) BEFORE game.js calls setBody — bodyBaseY then
    picks it up with zero player.js changes.
- prototype/js/enemy.js
  - :48-53 `setBody` (same pattern; bodyBaseY at :51).
  - :283-285 stagger/恢复 write body.position.y absolutes off bodyBaseY — keep working.
  - :240-252 death drop: `root.position.y = -deadFall*0.3` and the settled
    `-0.3 + bounce` (ANIM.death.settleDuration/overshoot from CONFIG at :44-47 —
    leave ANIM keys untouched; the -0.3 constant is what you replace).

## DESIGN
### D1 — P0-1 ground-align (audit P0-1 change items 1,2,4; item 3 DEFERRED)
1.1 assets.js loader: for EVERY loaded GLB template (and makeStandIn results),
    replace the in-place shift with a holder structure:
    - `holder = new THREE.Group(); holder.add(root)`;
      inner `root.position.y = -minY` (measured once via Box3.setFromObject(root)
      BEFORE any caller transforms); `holder.updateMatrixWorld(true)`.
    - Cache the HOLDER as the template. GROUND_META stays keyed by the holder uuid
      with {height, width} measured on the inner root, PLUS a new field
      `groundMinY` = the raw (unscaled) minY you compensated (<=0, or 0 if none).
    - Rotation note: measure minY at identity orientation (as today). rotY
      placement must not break grounding because prop meshes are y-symmetric
      enough at audit tolerance; the harness AC (A1) is the arbiter. If any
      CONFIG prop fails |minY|<=0.02 after rotY, record it in notes as a data fix
      (per-prop groundMinY override) rather than changing the measurement plan.
1.2 region-manager.js prop loop: stop writing y. `obj.position.set(p.x, p.y || 0, p.z)` —
    add optional `p.y` support (default 0) so future placement data can lift props.
    scale.setScalar stays AFTER position (order irrelevant now — grounding lives
    inside the holder, scale-invariant).
1.3 game.js player body: after `pBody.scale.setScalar(pScale)` and BEFORE
    `game.player.setBody(pBody)`: `pBody.position.y = -(WH_ASSETS.groundMinY('playerBody') * pScale)`.
    Expose `groundMinY(name)` in the WH_ASSETS export (raw template minY; 0 when
    unknown/stand-in-fallback). bodyBaseY (player.js:119) then holds the scaled
    offset — bob/crouch/recover absolutes (:148, :807, :823, :852) keep working
    unchanged. This fixes the latent scale-mismatch float (bodyBaseY captured
    unscaled today).
1.4 enemy bodies: same pattern inside region-manager.js:341-345
    (set eBody.position.y = -(groundMinY(bodyName) * eScale) before enemy.setBody),
    AND enemy.setBody keeps bodyBaseY semantics unchanged (no enemy.js edits for this).
1.5 weapons: NO grounding changes (longsword/handAxe keep their current pivot
    handling; the combat audit owns grip pivots; doc 60). Only guard: do not wrap
    weapon templates differently from other templates — if the shared loader wraps
    everything, verify sword attach sites (game.js:628-631, enemy.js:56-58) still
    frame correctly by reading their setWeapon/attach offsets in notes; adjust
    NOTHING unless the harness shows a weapon regression, then stop + amendment.
1.6 corpse drop (enemy.js:240-252): replace the hardcoded -0.3 with a measured
    value computed once at death start: after `body.rotation.x = -PI/2` is applied,
    sample `new THREE.Box3().setFromObject(this.body).min.y` (world), set
    `this.corpseFinalY = min.y + smallMargin` (target: settled |minY| <= 0.05),
    deadFall interpolates root.position.y from 0 to corpseFinalY, the settle
    bounce uses corpseFinalY + bounce. Keep ANIM keys and timing untouched.
    Compute lazily ONCE (guard flag), never per-frame.
1.7 CONFIG.js: add nothing for P0-1 EXCEPT if a per-prop groundMinY override table
    becomes necessary per 1.1's note (then `world.propGroundMinY: { name: value }`,
    consumed in the loader before holder math). Prefer zero new keys.

### D2 — P0-2 ground material (audit P0-2)
2.1 region-manager.js ground material (:286-293): `color: 0xffffff` for BOTH
    regions. The canvas already carries region-biased blotch palette
    (buildGroundCanvas regionId branch). Delete the groundColorA/B USAGE here;
    leave the CONFIG keys in place untouched (cleanup is doc-61 P2-8, not ours).
    Keep-alive: overall palette impression must stay region-biased (A olive,
    B charcoal) — if the white-light material visibly neutralizes the palette,
    fold the old tint into buildGroundCanvas blotch colors (bounded change,
    note it) rather than reintroducing a material color multiply.
2.2 makeGroundTexture (:246-248): keep `magFilter = NearestFilter`;
    `minFilter = THREE.NearestMipmapLinearFilter`; `generateMipmaps = true`;
    add `tex.anisotropy = Math.min(4, renderer max aniso)` (read from
    game.renderer capabilities if reachable; else hardcode 4 — note which).
2.3 Do not touch repeat=12, canvas resolution, or the mist plane.

### D3 — debug hook (one addition, harness-facing)
game.js WH_DEBUG (+435 block): add
`getAssetMeta: function (name) { ... }` returning
{height, width, groundMinY} from WH_ASSETS meta (null for unknown). Nothing else.

## TEST-QUALITY LAW (from the standing gate rules)
Validation is organic-path only: real key/mouse/frame events through the live page
(window.WH_GAME reads are fine; direct state mutation as a TEST act is banned).
The existing harnesses (wh_v7_weave.py 18-test profile; wh_combat_ds1_validation.py
18-test pre-fix profile 2 PASS / 16 FAIL) are PRESERVATION FLOORS: their PASS/FAIL
sets must remain exactly as documented at your start state (weave suite: its current
known profile; ds1 harness: exactly its frozen 2 PASS / 16 FAIL pre-fix profile —
these are ds1-round expectations, do NOT try to fix their failures, they belong to
the combat round). A R1-caused NEW failure in either suite blocks this round.

## ACCEPTANCE CRITERIA (validator will drive these; sim-frame or luminance evidence)
- A1 (M-01): every CONFIG prop instance in both regions post-build:
  |worldBBox.min.y| <= 0.02 AND |max.y - expectedTopFromScale| consistent with
  scale; assert per-prop via region manager groups traversal.
- A2 (M-02): player + bandit + ghoul standing on flat ground:
  |feet minY| <= 0.02 at idle; record max deviation over a 2s sprint + ghoul hop;
  no float > 0.05.
- A3 (M-03): kill an enemy (organic inputs), wait settle: corpse |minY| <= 0.05.
- A4 (M-09 proxy): ground visible-luminance check via canvas readback in a ring
  around the player: mean > 20/255 and pixel stddev > 4 (proves the black-ground
  fix; recorded headless-safe).
- A5 (M-12 proxy, record-only watch-item): temporal stddev across a slow pan on
  far ground pixels recorded, non-blocking (minification shimmer evidence for a
  later pass).
- A6: no new failure in wh_v7_weave.py or wh_combat_ds1_validation.py vs the
  DISPATCH-TIME captured profiles (both suites' sha256 + PASS/FAIL profile are
  recorded at dispatch and in the Testerbot smoke evidence; the ds1 harness is
  concurrently maintained by another workstream, so freeze-time hashes are
  informational only — the floor is: your diff introduces zero new failing test
  ids in either suite vs the dispatch-time capture).
- A7: tools/build_v7.py regenerated build loads clean (zero console errors,
  zero pageerrors, AC13-style load assert), index.html + style.css byte-identical
  to freeze.
- A8 (scope): git status set-difference vs freeze = exactly the 5 allowed files
  modified (+ your own io/ notes dir if you keep one), zero new repo files
  outside deliverables, secrets grep clean.

## PIPELINE NOTES
- No rigging, no skeleton work, no art regeneration. This round touches code only.
- Standing copy/secret rules apply (no keys or tokens in any file you touch).
- Vanilla JS only: IIFE style, window globals, no ES modules, no class syntax,
  CONFIG-driven tunables (no magic literals in logic — use CFG keys when a value
  is gameplay-tuning-shaped; rendering constants like filter enums may be literals).

## DELIVERABLES
1. The 5 edited files (only).
2. prototype/builds/v7-playable.html rebuilt via tools/build_v7.py.
3. Implementation notes at io/reports/2026-09-30-world-r1-implementation.md:
   per-AC self-check results, deviations, amendment requests (if any), and the
   exact final line numbers of every site listed in the precision map.

## VERDICT PROTOCOL (for Testerbot)
JSON verdict, per-AC PASS/FAIL/PARTIAL with file:line evidence verified at verdict
time; suite counts vs frozen profiles; freeze set-difference output included;
honest-PARTIAL allowed only for A5 (record-only) or pre-authorized environment
limits (SwiftShader) — anything else blocks. Pre-round harness run signature:
same as ds1/weave frozen profiles (harness already wired; do not re-author).