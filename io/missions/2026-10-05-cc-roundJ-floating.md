# ROUND J CONTRACT (FIX RUN): reach-trees floating above the ground (IO -> Claude Code)

SHORT RUN. Diagnose + fix ONE bug. No Meshy. No harness/game loops. Blender +
static loaders only. Commit early, both branches, push NO (IO pushes).

## Problem (Nicko, in-game)

Some reach-trees float above the ground (base not sunk); "not realistic".
Cone trees (yews) sit correctly. GLB-side y-extents are stable across every
bake pass (reach-a/b/c ymin -0.8592 / -0.6586 / -0.9430, accessor min/max
correct, node transforms none) - so the float is NOT asset geometry. Find the
real mechanism and fix it.

## Facts already verified by IO (do not re-derive, but DO verify the two flagged)

1. Game loader path: assets.js preloadAll -> prepTemplate(root, isPixelated)
   -> groundAlign(root): Box3.setFromObject(root); root.position.y -= minY;
   GROUND_META[name] = { height, width, groundMinY: minY }. Prop placement
   (region-manager buildRegion): obj = WH_ASSETS.instance(asset);
   obj.position.set(p.x, p.y || 0, p.z); rotation.y; scale.setScalar(p.scale);
   group.add(obj). The HOLDER (template clone) carries the compensated inner
   offset, so base should land at y=0 for EVERY prop identically.
2. SUSPECT A (highest): THREE.Box3.setFromObject on the reach GLBs measures
   the mesh node's WORLD bounds AFTER prepare/template - but groundAlign runs
   BEFORE the mesh's boundingSphere/geometry bounds are computed IF the
   geometry is lazily-computed... In r185 Box3.setFromObject(callers with
   precise=false) USES precomputed geometry.boundingBox WHEN AVAILABLE and
   EXPANDS by node transforms; if geometry.boundingBox is STALE/ABSENT it
   computes from positions. trimesh writes accessor min/max; GLTFLoader
   (r185) reads accessor min/max into geometry.boundingBox - correct here.
   VERIFY: with a headless three.js load of each of the 3 reach GLBs + 1 yew
   GLB (playwright chromium via about:blank + import of
   /tmp/wh-worldfeat/prototype/vendor/three.classic.js + GLTFLoader, load the
   GLB bytes as ArrayBuffer via file fetch from the live server), print
   new THREE.Box3().setFromObject(scene) per file. THIS IS A STATIC LOADER
   PROBE (3 files, no game loop) - allowed under the no-harness law
   (asset/GLB work: static geometry probes stay allowed). If chromium is
   unavailable, fall back to a manual BufferGeometry-clone simulation in
   node-free python using the same accessor math: read accessor min/max +
   node transforms per level and compute the SAME Box3 world bounds the
   loader would.
3. SUSPECT B: instance() = tmpl.clone(true). THREEM r185 .clone on a Group
   whose child's geometry is SHARED: fine. BUT GROUND_META is keyed by
   tmpl.uuid; region-manager's placement math does NOT use GROUND_META for
   props (it uses the holder's inner offset - fine).
4. SUSPECT C (second-highest): the I6 rows insert props with EXPLICIT "y:
   0.00" - region-manager does p.y || 0 = 0. Same as yews. NOT the bug.
5. SUSPECT D: the SNARE-style piece-snapping in my earlier passes moved PIECES
   in a/b (I2 runs had no snap for reach-a; Round I's --snap DID - median
   move 0.06-0.09, max 0.17-0.23 units, ~1-2m at tree scale: SOME SNAPPED TIP
   PIECES COULD SIT ON THE GROUND WHILE THE TRUNK BASE SANK - visually the
   BULK of the tree reads fine, but root flares could hover). The in-game
   look "floating off the ground" reads as WHOLE-TREE float though.
6. Nicko sees SOME trees floating (not all): per-placement variance points at
   the scatter path (whBuildInstanced / InstancedMesh undergrowth?) NO - he
   says TREES. Prop trees: the 6 I6 + 4 swaps. Per-instance float variance
   from a COMMON template = impossible for templates (identical transform)...
   unless the float is in the INSTANCE path: tmpl.clone(true) with
   SkinnedMesh? Not skinned. UNLESS groundAlign's Box3 was measured while the
   model's TEXTURES didn't affect geometry - no.
7. CHECK THE OBVIOUS: maybe only reachTreeB/C float (whose piece-snapping was
   bigger: I4 snapped 23/29 far pieces with moves up to 0.23) while A is
   grounded. ASK the geometry: compare the trunk-base neighborhood (lowest
   5% verts) between reach-a (intact) and b/c (snapped): if b/c lost their
   BASE pieces in snapping (moved UP), the visual base no longer touches
   ground level: THE WHOLE TREE then reads as floating (base flare at
   +0.3m). QUANTIFY: for each variant, lowest-1% verts z vs the z of the
   99th-percentile area-weighted mass center of the trunk region; and render
   a BASE CLOSE-UP of each variant at ground level (Blender, camera 2m from
   base at 0.5m height) -> 3 PNGs in scratch/roundJ-proof/. Vision-check
   each yourself.
8. If (7) shows b/c bases lifted: fix = re-run bake WITHOUT deleting base
   pieces: restore from raw/wh-reachtree-<v>.glb + decimate_roundI.py --snap
   with a BASE-PRESERVING snap rule (snap pieces DOWNWARD only if they are
   BELOW the trunk's 20% height; never lift base-level pieces), then re-run
   the I2/I2d/I2e weld+normal passes in order, then update:
   wh-reachtree-<v>-pixelated.glb (+ .glb mid + raw stays).
   ALSO fix reach-a if its base has ANY floating flare (it may already be
   fine).
9. If (2/3/4/5) show the loader/instance math is at fault instead: implement
   the MINIMAL engine-side fix (e.g. groundAlign for these assets: after
   Box3, ALSO ensure mesh-node-level base compensation) WITHOUT touching
   global loader semantics for other assets (gate the fix to reachTree*
   assets by name).

## Constraints

- No Meshy credits. No harness/game/browser-loop runs (the one loader probe
  in (2) is an allowed static asset probe; anything beyond loading + bounds
  print is a violation).
- Do not touch: light.js, player.js, enemy.js, moveset.js, region-defs.js,
  wall code, scatter plan code (unless (9) forces an assets.js-level fix),
  any rigged/combat GLB, wall GLBs.
- DO NOT delete visible canopy mass while fixing bases.
- Deterministic; esprima any JS edits; GLB writes verified by reload + ortho
  after EACH pass (backup each GLB to /tmp/roundJ-backup/ before overwriting).

## Commits (CaptainPickard <pickard.nicko@gmail.com>, both branches, same
messages):
- fix(assets): reach-tree bases grounded (Round J) [if GLB route]
- fix(world): reach-tree ground align fix (Round J) [if loader route]
- build: v7 bundle (worktree only, if pixelated GLBs moved)
Also commit scratch/roundJ-proof/ + io/roundJ-provenance.md (mechanism
found: one paragraph) + any fix scripts. No push.

## Report (<= 60 lines)

Mechanism (the one-line answer to WHY floating), evidence per step, fix
applied + files, before/after base-close-up stills list, determinism, GLB
bounds table, commits table, watch items.