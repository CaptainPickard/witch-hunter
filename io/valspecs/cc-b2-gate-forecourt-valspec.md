# CC-B2 Validation Spec — Gate Forecourt (Testerbot)
Owner: Testerbot. Date: 2026-11-07. Worktree /tmp/wh-worldfeat (feat/world-visuals).
Validates IO spec io/specs/cc-b2-gate-forecourt-spec.md. Code QA only; pure-plan probe.
Run everything from the repo root: /tmp/wh-worldfeat.

## 1. Probe procedure (pure WH_WallPlan, stubbed meta)
Precedent: scratch/cc13b_probe.cjs (plain node, no three) — but CC-B2 calls the REAL
pure function, not a numeric mirror. Pattern (new file scratch/cc-b2-valspec-probe.cjs,
run `node scratch/cc-b2-valspec-probe.cjs`, exit 1 = any fail):

    global.window = global;                       // CONFIG/defs/mgr are window.* IIFEs
    require('../prototype/js/CONFIG.js');         // sets window.WH_CONFIG
    require('../prototype/js/region-defs.js');    // sets window.WH_REGION_DEFS
    require('../prototype/js/region-manager.js'); // sets window.WH_WallPlan + WH_RegionGeom
    var plan = window.WH_WallPlan(metaStub);

Stub minimalism: `metaStub(name)` returns `{ width, height }` per asset — that is all
whWallPlan reads. Values should mirror the measured manifests
(ironFenceSection ~1.8w, ironFenceCorner ~0.589w, lanternPost ~0.585w, b3Gate/whWallA/
whWallB/whLanternHang their manifest ext) so arch halfWidth matches production; copy
the width/height table from scratch/cc-b1_probe.cjs (WIDTH) + the b3Gate row as the
baseline and extend as needed. MANDATORY: the props-exclusion loop calls meta() for
EVERY regionA/regionB prop asset — any name not in the stub makes plan.complete=false;
therefore iterate window.WH_REGION_DEFS.regions[*].cfg.props asset keys, fail loudly on
a missing stub entry, and assert plan.complete === true at the end. No THREE, no
buildWorld, no canvas: if the require chain touches THREE/document at load, stub
`global.THREE = {}` (defined functions only at load time) and report it.

## 2. Assertions (A1–A3 → concrete checks)
A1 — structure (from post-patch plan, exactly ONE new stats block):
  a. stats gains fenceE, fenceW, fenceCorners, posts, forecourtSkips; fenceE === fenceW
     >= 1, fenceCorners === 2, posts === 2.
  b. fromX: fence runs start at x >= plan.arch.halfWidth + 1.2 (hard floor); with the
     spec formula it must equal max(CFG.boundaryWall.chordFromX, halfWidth+1.2+0.7)
     = max(4.0, hw+1.9) within 1e-6. No fence/corner/post collider center with
     |x| < halfWidth (never inside the arch pillar face).
  c. geometry: EVERY fence+corner segment has z === -22.9 (±1e-6); E-side segment
     centers span [fromX, 20.0 ± step] and the run's last piece on each side is the
     corner asset (ironFenceCorner); step = span/nc, nc = ceil(span/(len-overlapM)),
     len = metaWidth(ironFenceSection)*1.35; per-axis scales sx/sy/sz present (y 0),
     rotY = 0 or PI (+rotJitter-free) such that the section runs along X.
  d. posts: exactly two segments (asset lanternPost) at (-6.2, -20.5) and (6.2, -20.5),
     rotY 0, sx===sy===sz===2.535; one corner/terminus pair NOT at post coords
     (corners stay with the fence runs).
  e. colliders: every fence piece, corner, and post contributes plan.colliders entries
     via colliderRadius (NOT trunk-class: r = width*scale/2, no 0.25 factor for
     ironFence*/lanternPost); collider counts: new entries == fenceE+fenceW+corners
     (perSegment 3 does NOT apply to forecourt — full footprint per piece, per spec)
     post colliders == 2 (collider count only posts==2 rows). Verify count matches the
     index prefix the patch uses ('forecourt*' or equivalents — assert consistency).
  f. corridor law: for EVERY new collider, window.WH_RegionGeom.meetsCorridor(x, z, r)
     === false (corridor rect x [-4,4], z [-31..-19] minus circle r). stats
     .forecourtSkips == number of placements skipped by that rule (>= 0, consistent
     with a re-derivation: recount skipped placements from CONFIG geometry).
  g. sockets: plan.sockets contains exactly 2 NEW entries with ids
     'lanternPost@forecourtE'/'lanternPost@forecourtW' at x = ±6.2, z = -20.5
     (offset [0,0] per spec), intensity === CFG.lightSockets.lanternPost.intensity
     (9.0), weight 1, y === stubHeight*2.535*0.76 ± 1e-6 (heightFraction 0.76).
     Pre-existing socket (b3Gate@lantern) coordinates unchanged.
A2 — determinism: run the whole probe twice in one process (fresh CFG deepcopy not
  needed — whWallPlan is pure); JSON.stringify(plan) is byte-identical across runs.
  Additionally hash the string: sha256 of plan JSON identical for two separate node
  invocations (catches Math.random/env leakage).
A3 — additivity: checkout PRE-patch CONFIG.js + region-manager.js + region-defs.js
  (git show HEAD:... > scratch/cc-b2-prepatch/, git read-only is allowed, NO commit)
  and run the identical probe there. Diff post vs pre plan:
    - stats ring, chordE, chordW, nudged, drops, dropReasons, doorGap, archLegs,
      archPlugs, colliders-from-ring/chord/arch: IDENTICAL (new forecourt stats keys
      excluded from the comparison).
    - segments with kind in {ring, chordE, chordW, doorArch}: asset,x,z,rotY,sx,sy,sz
      arrays byte-identical (JSON diff).
    - arch object + arch-leg/arch-plug colliders: identical.
    - ONLY allowed additions: fence/post segments, their colliders, 2 sockets.

## 3. Static checks
  a. `git status --porcelain` / `git diff --name-only` on the worktree: changed/added
     files ⊆ {prototype/js/CONFIG.js, prototype/js/region-manager.js,
     prototype/builds/v8-playable.html, io/specs/*, io/valspecs/*, docs/*, scratch/*}.
     Anything else inside prototype/ (game.js, styles, assets, GLB/JSON) = FAIL.
  b. `python3 tools/build_v8.py` exits 0 and new build succeeds (A4/IO spec).
  c. grep -c 'CC-B2' prototype/builds/v8-playable.html >= 1 (marker present).
  d. grep CONFIG.js boundaryWall.forecourt block: fence.z 22.9, toX 20.0, post
     coords -6.2/6.2, -20.5, scale 2.535, clearM 0.7 — all present as CONFIG keys,
     no magic numbers for these in region-manager.js (grep region-manager.js for
     '-22.9', '20.0', '-6.2', '2.535' must return no bare literals outside comments).

## 4. Verdict format (final report)
First line MUST be exactly one of:
  PASS: CC-B2 gate-forecourt
  FAIL: CC-B2 gate-forecourt
Then evidence lines, one per check id (A1.a..A3, 3.a..3.d), each:
  <id>: PASS|FAIL — <observed value / expected> (e.g. "A1.c fence z: all 14 == -22.9").
Any single FAIL line forces the FAIL verdict. Attach probe stdout + sha256 of both
plan runs + git-diff file list verbatim. No partial PASS without evidence lines.

## 5. No-playability clause
This validation is CODE QA only: pure-plan geometry, determinism, additivity, and
static/diff hygiene. It makes NO claim about visual quality, feel, or playability.
Nicko's playtest is the ONLY acceptance bar for gameplay/appearance (IO spec A6).
Do NOT write "playable", "fun", "reads well", or "gate feels right" anywhere in the
report — geometry facts only.
