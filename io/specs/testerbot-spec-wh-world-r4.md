# TESTERBOT SPEC — Witch Hunter World R4: Pixelated Character Bodies Validation (gate step 2)

Author: Testerbot (independent validator-author). Date: 2026-10-02.
Devbot spec of record: io/specs/devbot-spec-wh-world-r4.md (read-only; mismatches are amendment
notes B1..Bn below, never patched in the spec by me). Tree at authoring: 8bd137a. CODE base =
cce06eb (R3 marker); `git diff --stat cce06eb 8bd137a` = 3 PNGs + the spec rename only, so all
R4 code diffs are measured against cce06eb. HANDOFF.md harness laws 1-8 + floor waiver classes
inherited verbatim; R3 valspec amendments A1/A5/A8/A10 carried where cited.
Live anchors (verified at 8bd137a): MANIFEST prototype/js/assets.js:15-54 (rigged bodies :47-49),
CHARACTERS :87, prepTemplate :127-152 (filters only when isPixelated, :139-144), loadOne :154-189,
preloadAll isPixelated = url has '-pixelated' :197, WH_ASSETS.getTemplate :223; CONFIG assets
block prototype/js/CONFIG.js:478-481 (timeoutMs, standInColor only); window.WH_GAME.renderer
(R3 harness :196,:332). PNGs committed at art-direction/3d/assets/races_regen/rigged/
{human-hunter-male,orc-male-warrior,undead-ghoul-male}.rigged.pixelated.png (204349 / 243700 /
206150 B). index.html sha256 9ad39b809bc4... (blob 9af31e83) == cce06eb.

## Harness + invocation contract
1. File: tests/wh_world_r4_validation.py = build artifact `cat tests/r4parts/part01..NN.py`
   (law 8: edit parts, re-cat, grep shadowed duplicate defs before every run). Playwright sync,
   headless chromium `--enable-unsafe-swiftshader`, viewport 1920x1080, dsf=1.
2. Env: `WH_BASE_ROOT` (reuse candidate), `WH_W4_PORT` (default 0 = ephemeral self-spawn),
   `WH_SMOKE=1` (1 settle-rep, subprocesses still run), `WH_W4_FLOOR=0` (skip R4-4 + R4-5
   subprocesses, recorded SKIP-NOTED, never silent; a SKIP-NOTED run can never be PASS),
   `WH_W4_PRE_A2` (optional JSON of pre-R4 A2 minY numbers; else the smoke capture file
   tests/artifacts/r4-pre-a2.json is read). Subprocesses inherit `WH_BASE_ROOT=<our root>`.
3. Server identity (law 5 + R4 signature): reuse WH_BASE_ROOT only if served js/CONFIG.js
   contains `lightPool` AND `ambientIntensity: 0` AND `internalResDiv` AND `pixelatedBodies`
   AND its bytes equal the worktree prototype/js/CONFIG.js (A1). Else self-spawn
   prototype/server.py from REPO_ROOT on an ephemeral port (bind 127.0.0.1:0, close, spawn,
   poll); kill on exit. NEVER port 8791 (landed dev server = different tree) — any URL
   containing ':8791' anywhere in a request log of this run = BLOCK (see R4-4, B3).
4. Laws: forced render + toDataURL in ONE evaluate; camera-settle (vz<1 retry) before screen
   probes; NaN guards on enemy pos; per-AC try/except -> recorded FAIL; exit 0 ALWAYS; final
   stdout line = one JSON verdict; no key-shaped literals in parts.
5. Sanctioned measurement-only intervention (kill-switch OFF probe, B2): a page.route on
   `**/js/CONFIG.js` that serves the worktree bytes with `pixelatedBodies: true` rewritten to
   `pixelatedBodies: false`; the rewrite MUST match exactly once (count recorded; 0 or >1 =
   FAIL R4-1). No worktree file is ever modified. The OFF context is a separate browser
   context; route is never active in the ON context (asserted: ON served bytes == worktree).

## Pre-Devbot smoke — EXPECTED (tree = 8bd137a; captured run is authoritative)
| AC | Expected pre-Devbot | Evidence to capture |
|----|---------------------|---------------------|
| BOOT | PASS; reuse refused (no pixelatedBodies) -> self-spawn | identity result, port |
| R4-1 | FAIL: key absent (WH_CONFIG.assets.pixelatedBodies === undefined); OFF-route rewrite count 0 | per-body map dims 2048x2048, magFilter Linear(1006), image src not .png |
| R4-2 | FAIL (no swap); memory.textures baseline = RECORD | textures/geometries count A-spawn |
| R4-3 | FAIL: body-px per-channel distinct levels > 32 (smooth atlas) | level counts = baseline RECORD |
| R4-4 | PASS (anim regressions green on unchanged tree) | per-suite exit + summary line |
| R4-5 | PASS via inherited waivers; A2 minY numbers written to tests/artifacts/r4-pre-a2.json | R1 JSON line |
| PNG | PASS: 3 PNGs HTTP 200 from our root, image/png, decode 512x512 | status, content-type, dims |
| PRES | PASS (dirty set = this valspec only; 3 PNGs already committed since base) | porcelain + diff set |

## AC-R4-1 — Texture source + filters, both kill-switch states
- Probe (one evaluate per context, after WH_ASSETS.loadedCount settles): for each of
  playerBody/banditBody/ghoulBody, traverse WH_ASSETS.getTemplate(name), first mesh with
  material.map -> {w:image.width, h:image.height, src:image.currentSrc||image.src||'',
  ctor:image.constructor.name, mag, min, flipY, colorSpace, wrapS, wrapT, uuid}, plus
  WH_ASSETS.isFailed(name) and getClips(name).length. Live player body mesh map uuid (and
  any live bandit/ghoul instance) must equal its template map uuid (shared, not per-clone).
- ON bars (served CONFIG, no route): (1) WH_CONFIG.assets.pixelatedBodies === true;
  (2) w===h===512; (3) src ends with `races_regen/rigged/<stem>.rigged.pixelated.png` for the
  matching body (stem from MANIFEST :47-49); (4) mag===THREE.NearestFilter, min===
  THREE.LinearMipmapLinearFilter; (5) flipY===false and colorSpace/wrapS/wrapT === the OFF
  values (B4: a TextureLoader PNG defaults flipY=true -> UV-flipped garbage on glTF UVs);
  (6) isFailed false, clips === 6; (7) request log: exactly 3 *.pixelated.png requests, all
  200, from our root.
- OFF bars (route rewrite count === 1): w===h===2048; src has no 'pixelated'; mag/min/
  flipY/colorSpace == pre-Devbot smoke capture per body (exact); 0 *.pixelated.png requests;
  isFailed false, clips 6. Evidence: both 3-row tables + rewrite count + request log.
- PNG byte proof: served bytes of each PNG sha256 == worktree file == 8bd137a blob.

## AC-R4-2 — GPU memory (renderer.info.memory)
- Both contexts, A spawn after settle: one evaluate calls WH_GAME.renderer.initTexture(map)
  for all 3 template maps (symmetric upload in ON and OFF), forced render, then reads
  renderer.info.memory {textures, geometries}. Bars: textures_ON === textures_OFF and
  geometries_ON === geometries_OFF (exact ints = swap, not add; a retained uploaded original
  shows as +1..+3). three.js exposes no byte counter (B5): bytes = w*h*4*4/3 (RGBA8 + mip
  chain) from the R4-1 dims. Bar: per-body OFF/ON byte ratio === 16.0 (2048^2/512^2;
  22,369,621 -> 1,398,101 B); RECORD table body, dims ON/OFF, bytes ON/OFF, counts, total drop.

## AC-R4-3 — Visual posterization
- (a) Texture-space (gate): in-page draw each ON map.image to a 512 canvas, getImageData;
  per channel distinct levels <= 32 (5-bit), all 3 bodies; RECORD whether every value is
  congruent mod 8 and the top-8 level histogram per channel. OFF same probe = RECORD
  (expected > 32, proves the probe discriminates).
- (b) Screen-space (gate, IO bars B6): ONE evaluate: force render -> toDataURL; set player
  body holder visible=false; force render -> toDataURL; restore visible=true (sanctioned,
  restored in-evaluate). Body mask = pixels with max channel |diff| > 8; mask >= 400 px at
  960x540 else settle-retry (infra). Over mask: distinct RGB count D and 4-neighbour equality
  E (max channel diff <= 2). Bars: D_ON <= 0.60 * D_OFF AND E_ON - E_OFF >= 0.10, same pose
  both contexts (camera settled, player at A spawn, no input). First numeric miss with (a)
  PASS = FAIL-RETUNE-PENDING. Evidence: D, E, mask px, both PNG artifacts.

## AC-R4-4 — Anim compatibility (whanim2 regression set)
- FINDING (B3): no committed whanim2 harness exists; whanim2 was validated by /tmp probe
  scripts (io/reports/2026-10-01-whanim2-validation.md, evidence /tmp/tb_*.json, not in repo).
  Its A12 committed regression set is the gate here, as subprocesses, timeout 3600s each:
  (1) tests/wh_v3_anim_probes.py — ORIGINS hardcoded [8791, 8792] (:12) with fallback to
  8791 (:300) and an UNGUARDED main() at :311, so importing it runs it. Invoke as
  `python3 -c` that reads the file, replaces the :12 ORIGINS line in memory with
  [<our root>] (replace count must === 1, else FAIL), and exec()s it; file untouched.
  Bars: exit 0, line "V3 ANIM PROBES: PASS", summary keys === [our root] only.
  (2) tests/wh_combat_ds1_validation.py with WH_BASE_ROOT: verdict PASS, failed === 0.
  (3) tests/wh_v2_verify.py with WH_BASE_ROOT=<root>, WH_BASE_PROXY=http://127.0.0.1:9/
  (unreachable -> root only, :163-172): exit 0; asset-audit non-200 count === 0 (total RECORD).
  wh_v7_weave.py = SKIP-NOTED (writes builds/; v7 load covered by PRES).
- In-harness (both contexts): clips === 6 per body; skeleton.bones.length per body ON ===
  OFF; 3 manifest GLBs sha256 === cce06eb blobs (whanim2 A2 frozen-GLB law).

## AC-R4-5 — R1 floor (subprocess, A2 non-worsening)
- `python3 tests/wh_world_r1_validation.py` env WH_BASE_ROOT=<our root>, WH_R1_PORT=<our
  port> (B7: R1 defaults both to 8791, :26-27), WH_R2_FLOOR=0 (inert for R1, set for uniform
  nesting), unchanged file; parse final JSON. R1 protocol: A1-A4,A6,A7,A8 PASS, A5 RECORD.
- Inherited waiver classes, each re-verified in-run as R2 part10 ac_floor: A2-dev-baseline,
  A3-settle-subprobe, A4-nightrig-chain, A6/A7-hash-drift (incl. R3 A4/A10: style.css ==
  cce06eb blob, index.html == cce06eb), A8-surface-FP (residual wholly inside PRES surface).
- Bars: A1 PASS un-waived. A2: per actor (player/bandit/ghoul) idle |minY|_R4 <= |minY|_pre
  + 0.005 and walk maxdev_R4 <= maxdev_pre + 0.005 (pre = smoke capture; a texture swap
  cannot move geometry, so expected delta is 0). Any other new fail = STOP. Record, never edit R1.

## AC-PRES — Preservation surface (git set-diff vs cce06eb, committed + porcelain)
- Allowed set EXACTLY: prototype/js/assets.js, prototype/js/CONFIG.js, the 3 rigged
  *.pixelated.png (bytes === 8bd137a blobs; any re-bake = FAIL, B8), io/specs/*-r4*,
  io/reports/*r4*, tests/wh_world_r4_validation.py, tests/r4parts/*, tests/artifacts/r4-*.
  Porcelain with the R1 A8 leading-3-char strip. Residual non-empty = FAIL; any other
  prototype/ file (game.js, player.js, enemy.js, anim.js, region-manager.js, style.css) = BLOCK.
- Hunk law: CONFIG.js hunks only inside assets {} (:478-481), adding pixelatedBodies: true
  with a kill-switch comment; timeoutMs/standInColor unchanged. assets.js hunks only in: the
  header comment :6-7, a body->PNG table adjacent to MANIFEST, loadOne's success path
  (:165-179) and ONE adjacent swap helper; groundAlign, prepTemplate, instance, makeStandIn,
  resolveUrl, preloadAll, CHARACTERS, WH_ASSETS API byte-identical. Rigged GLBs unchanged.
- index.html sha256 === cce06eb blob (9ad39b809bc4...). v7 rebuild on a temp copy (R3 A8):
  0 console/page errors; prototype/builds/ absent from dirty set.
- Secrets: `git diff cce06eb` grep msy_[A-Za-z0-9]{8} + key/token/secret/password assignment
  patterns = 0; player-facing "free" over prototype diffs = 0.

## Flake rule (same as R1/R2)
- Retries up to 2 (fresh reload) for infra-shaped failures only: runner exception,
  timeout, server 500, WH_DEBUG not ready, SwiftShader degenerate frame (all-zero),
  screenshot blank. Deterministic number misses (dims, pair ratios, triangles, timing
  medians, subprocess verdicts) are NEVER retried. Verdict per AC = LAST attempt;
  >= 3 flakes in the run = BLOCK ("harness unstable, do not gate on this run").

## Verdict protocol
`{"round":"world-r4","verdict":"PASS|FAIL|BLOCK|FAIL-RETUNE-PENDING","atlas":512,
 "kill_switch":{"on":[...3 rows],"off":[...3 rows],"rewrite_count":1},
 "per_ac":[{"id":"R4-1","verdict":"...","evidence":"..."}],"mem_table":[...],
 "floor":{"r1":{...,"waivers":[],"a2_pre":{},"a2_post":{}},"anim":{"v3":{},"ds1":{},"v2":{}}},
 "flakes":0,"notes":"..."}` — exit 0 ALWAYS.
- PASS iff R4-1, R4-2, R4-3, R4-4, PRES PASS and R4-5 PASS (waivers only from enumerated
  classes); any SKIP-NOTED gating AC => verdict cannot be PASS.
- First numeric miss on R4-3(b) with R4-1/R4-3(a) PASS = FAIL-RETUNE-PENDING (one retune);
  SECOND identical miss = STOP. Independent BLOCKs: scope violation, secrets hit, index.html
  drift, any :8791 request, non-artifact R1 fail, anim regression fail, >= 3 flakes.

## Amendment notes (spec-of-record vs live tree 8bd137a; I own the bars)
B6-IO (ruling 2026-10-02, Nicko-approved "amend the probe"): R4-3(b)'s
    ON-vs-OFF screen-space bars (D_on <= 0.60*D_off, dE >= 0.10) are
    UNMEASURABLE at the A-spawn pose — the night rig leaves the body a
    near-black silhouette (smoke evidence: D 475 vs 467, dE 0.0008, mask
    3392 px of near-identical dark pixels; texture-space (a) PROVES the
    atlas is 5-bit posterized with OFF discriminating at 196-230
    levels/channel). REPLACED BY: (1) the texture-space gates (a) remain
    the PRIMARY PASS basis; (2) a SCALED SCREEN RE-MEASURE (RECORD, not
    gate): same probe at a lit pose (player at the lanternPost A1 (-2,30),
    lantern light on the body, camera settled), numbers recorded either
    way; a lit-pose miss does NOT fail the round (it informs tuning only).
    Rationale: the swap demonstrably ships posterized atlases; the dark
    pose cannot express the difference to either the probe or a viewer.
B1. Anchors: the spec cites the manifest at assets.js:46-49; live MANIFEST is :15-54 with
    bodies at :47-49; loadOne :154-189, prepTemplate :127-152. Spec design 1 (runtime canvas
    bake) is superseded by its own MECHANISM RULING (offline PNG); I validate the ruling.
B2. Spec says "both states probed" without a mechanism; CONFIG is a static script, so OFF is
    probed via an in-flight route rewrite of served CONFIG.js (exactly-once), never a tree edit.
    Key ABSENT is recorded as pre-Devbot state only; post-Devbot the key must exist.
B3. "anim2 harness subprocess" does not exist in tests/; replaced by whanim2's committed A12
    regression set. wh_v3_anim_probes.py would silently test the 8791 dev tree (hardcoded
    ORIGINS + fallback + unguarded main) — hence the in-memory ORIGINS rewrite and the
    8791-request BLOCK. Recommend a committed whanim2 harness in a later anim round (parked).
B4. Live-tree trap: preloadAll's isPixelated keys on '-pixelated' (:197) but the PNGs are
    named '.rigged.pixelated.png' and loaded separately, so prepTemplate never sets Nearest
    for them; Devbot must set filters explicitly. TextureLoader defaults flipY=true and
    colorSpace=NoColorSpace, both wrong for glTF maps -> bars R4-1 (5).
B5. Spec "~64x per-texture byte drop" is arithmetically wrong: 2048^2/512^2 = 16x (its own
    16.7MB -> 1MB figures agree with 16x). renderer.info.memory exposes counts only; bytes
    are dims-derived. Bar = 16.0 exact plus count equality.
B6. Spec bar "<=8 shades per channel bucket on body px" is unmeasurable post-lighting
    (tonemap + hemi/moon/lantern shading reintroduce gradients). Split into texture-space
    5-bit gate (<= 32 levels) + screen-space ON-vs-OFF relative bars (0.60 / +0.10, mine).
B7. R1 floor must pass WH_R1_PORT as well as WH_BASE_ROOT (R1 :26-27 default 8791).
    WH_R2_FLOOR=0 is passed for uniformity but only R2 reads it (r2:33).
B8. Retune conflict: spec allows 512->256 or a posterize tweak but forbids Devbot in-repo
    baking. A retune therefore requires an IO re-bake with io/specs/wh-r4-bake-all3-tool.py
    and re-pinning PRES PNG blob bars + R4-1 dims (256) + R4-2 ratio (64.0) before re-run.
B9. Server identity adds `pixelatedBodies` to the R3 signature (and CONFIG byte equality, A1);
    PNG files are mode 600 root-owned like the GLBs — self-spawn as the same user (root).
B10 (IO, 2026-10-02): P4's pre-Devbot smoke on an unchanged tree expects R1
    floor PASS-via-waivers (smoke table row R4-5) — as at R2/R3.
B11 (IO ruling 2026-10-02, Nicko-approved): R4-5's A2 non-worsening bar
    (|minY| <= pre + 0.005) was UNMEASURABLY tight across runs: the
    same-build idle minY sampling spread on the IDENTICAL R4 tree is
    0.0145 (3 fresh boots: -0.4911/-0.4766/-0.4850; probe
    /tmp/whr4_a2_variance.py). New bar: post <= pre + 0.05 (3x noise).
    The swap's mechanical integrity stays hard-gated by R4-1 (map
    dims/filters/flipY/sRGB) and R4-4 (clips==6, bones equal). The
    observed 0.523-vs-0.488 delta is idle-pose phase sampling, not a
    geometry change (texture swap cannot move geometry).
