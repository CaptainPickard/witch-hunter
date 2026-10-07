# CC-C1 · Heightfield Spike — Forest of the Old King (Region C)

Change-order brief, written 2026-10-07 by IO from docs/planning/62 §4 and
docs/planning/63 (CC-C1). Playtest approval for the previous order chain:
HP2 98393f2 (serving verified releases/98393f2). Ruling set R-62.1: REAL
heightfield now — spike first (raycast height sampler + smooth displaced
ground mesh), then gameplay walks on sampled heights (CC-C4).

## MISSION

Build a THROWAWAY spike in scratch/ ONLY — no game files touched:

1. A standalone Three.js demo page: displaced terrain mesh at Region C
   scale with smooth multi-octave hills.
2. A playable stand-in: WASD-walked actor whose y follows the ground, with
   slope blocking (max-step guard) and a camera that never goes underground.
3. An on-screen measurements panel: tri counts, fps, and a sampler
   comparison with a verdict row. These numbers gate CC-C2/CC-C3/CC-C4.

Artifacts live in scratch/region-c-spike/ (new dir):
- scratch/region-c-spike/index.html (demo page, inline CSS fine)
- scratch/region-c-spike/region-c-spike.js (all demo code, plain js)
- scratch/region-c-spike/SPIKE-LOG.md (findings + numbers, filled as you go)
- builder log: append your summary to scratch/cc_c1_builder_log.txt

## HARD LAWS (binding)

- NO harness runs, NO headless browser, NO playwright, NO screenshot loops —
  Nicko opens the demo himself and plays. Your verification = node --check
  on region-c-spike.js plus your own reading of the code.
- SCRATCH-ONLY: files outside scratch/region-c-spike/ and the scratch log
  are READ-ONLY. Especially: prototype/js/*, prototype/index.html,
  prototype/style.css, docs/, io/. Do NOT edit, do NOT run tools/build_v8.py
  (bundle must stay byte-identical for later verification).
- DO NOT git commit and DO NOT git push. IO reviews, then commits the spike
  record itself. Leave only working-tree artifacts.
- Vendor Three.js only: load ../../vendor/three.classic.js relative to the
  demo dir (absolute filesystem path /tmp/wh-worldfeat/prototype/vendor/
  three.classic.js). No CDN, no new npm/deps, no GLB assets, no textures.
- Identity for any accidental write ops: CaptainPickard
  <pickard.nicko@gmail.com>. cwd: /tmp/wh-worldfeat (your repo root).

## TECHNICAL CONTRACT (numbers baked)

Scene: square plane 560x560 world units (C-scale stub; the production C disc
is centered (0,-366) r=280 spanning z ∈ [-646, -86] — this spike does NOT
implement world placement, only terrain character + machinery).

Terrain generation (deterministic, seed constant 1337, documented):
- Value noise (hash-based, smoothstep interpolation), fBm 4 octaves,
  base wavelength ~45 units, lacunarity 2.0, gain 0.45.
- Height range target ~0..5 units. Zero-mean NOT required; the actor spawn
  point (center of plane) should be a LOW area (flatten radius ~25 units
  around origin so the stand-in spawns on near-flat ground).
- Build THREE.PlaneGeometry(560, 560, S, S), displace vertex z (before
  rotation) = height(x, y). Recommended S grid candidates to test: 100,
  140, 180. Target: ONE mesh, one draw call, ≤ ~40k tris at S=140 (tris ≈
  2·S² interior). Put the S value on a keyboard-toggleable cycle (1/2/3)
  so Nicko can compare densities live.
- Material: MeshStandardMaterial, flatShading true, vertex colors with a
  subtle height tint (low = dark moss green, high = lighter stone brown).
  Flat-shaded low-poly fits the game's stylization (raw mesh + color
  treatment per the v3 art pipeline ruling) — no post-processing needed.
- Lighting: hemisphere + one directional. Fog: scene fog matched to a clear
  background color so the plane edge fades out (this validates the
  fog-hides-the-edge discipline CC-C3 needs).

Machinery — height sampling, THREE strategies, ALL implemented, compared
on-screen (measure over >= 1000 random points inside the plane):
- Strategy A ANALYTIC: heightAt(x,z) = the fBm function itself (continuous).
  Cost: pure math. Error vs rendered mesh comes from tessellation +
  triangle interpolation.
- Strategy B GRID: bilinear lookup of a cached S+1 x S+1 height grid (the
  same vertex heights the mesh uses). Cost: array lookup + 4 lerps.
- Strategy C RAYCAST: THREE.Raycaster downward against the mesh. Exact vs
  the rendered surface; expensive per call.
- Table rows: max |diff vs raycast| (units), mean |diff| (units),
  per-call microseconds. Verdict row: which strategy CC-C4 should use as
  THE single source of truth (doc 62 §4: heightAt is the single source of
  truth for player, enemies, props, corpses, camp ghost), with the fallback
  order. Note: if A or B error vs C is under ~0.05 units at S=140, say so —
  that is the likely winner; the mesh vertices and the sampler can simply
  share one function.

Movement stand-in:
- Actor: capsule/box placeholder (no GLB), speed ~6 units/s (shift-run
  ~9). Each frame: y = sampler(x, z) with the chosen strategy.
- Max-step guard: block movement onto a cell whose |Δh| would exceed
  maxStepPerFrame = runSpeed * frameDt * climbFactor. Implement as a
  move-reject (slide along the blocked direction is NOT required — simple
  reject is fine) and log the chosen climbFactor + observed 50th/90th/99th
  percentile slopes of the terrain into SPIKE-LOG.md (compute the slope
  distribution analytically from the sampler over a grid of points, report
  in degrees).
- Camera: orbit behind the actor (drag to rotate, wheel to zoom 8..24),
  camera y >= groundHeight(cameraXZ) + 1.5 every frame.

Measurements (on-screen HUD panel + SPIKE-LOG.md):
- Per S in {100,140,180}: drawn triangles (renderer.info.render.triangles),
  rolling fps during a ~60s scripted walk pattern you run once at page
  load (a preset waypoint loop automating a cross-hill walk — this is a
  DEMO-internal scripted walk for fps sampling, not a harness run and not
  the game), build time (ms) and geometry vertex count.
- The sampler strategy table above.
- A recommendation paragraph: production S value, sampler strategy,
  climbFactor, any warning (fps cliffs, build stalls on tab-switch, etc).

## A - ACCEPTANCE CRITERIA (Nicko plays, no automation)

- A1 Walk the hills: WASD works, actor y follows terrain, steep slopes
  physically block (max-step guard), camera never cuts underground.
- A2 Readout: HUD panel shows S-density (toggleable), triangles drawn, fps
  — at the recommended S, motion stays smooth for a walk across hills.
- A3 Sampler table: all three strategies compared with error + cost + a
  verdict row naming the CC-C4 strategy.
- A4 Determinism: seed 1337 always produces the same terrain.
- A5 Scratch-only: clean report of every file you created (paths + sizes);
  confirm no file outside scratch/region-c-spike/ plus your log was touched
  (git status in your final reply must show ONLY those untracked paths).

## CODE-REVIEW-GRAPH IMPACT (baked, run pre-dispatch)

Command: code-review-graph impact --files scratch/region-c-spike/
region-c-spike.js scratch/region-c-spike/index.html --depth 2
--max-results 12 (repo /tmp/wh-worldfeat). Result JSON:
{"status":"ok","summary":"...2 changed file(s): 0 nodes directly changed,
0 nodes impacted (within 2 hops), 0 additional files affected",
"changed_nodes":[],"impacted_nodes":[],"impacted_files":[],
"resolution":"all","unresolved_call_sites":0,"confidence":"target not
indexed: no node matching 'region-c-spike.js', so this 0 is not evidence
that none exist"}.
Honest reading: new unmapped scratch files, so the 0 impact is NOT proof by
graph — the proof of no game-file contact is the SCOPE CONTRACT above
(scratch-only) plus A5's git-status check in your final reply.

## BUDGET CONTEXT (why the spike matters; cite, do not re-derive)

Doc 61: biome props ~30k tris each; Region B at 1.45M tris = 72% of the
2M slice budget BEFORE ground cover/decor/VFX; ground disc today is a
48-tri flat fan (region-manager.js:293-297). C adds a ~40k-tri ground mesh
(+2-3% of budget) — acceptable — but tree scatter on top of it (CC-C3)
needs the density discipline from CC-C0's ledger. The heightfield mesh is
NOT the budget risk; the tree scatter is.

## FINAL REPLY FORMAT (builder)

Files created (paths + sizes) · node --check result · git status output ·
the measurement table (S values, tris, fps, build ms) · sampler comparison
+ verdict · climbFactor + slope percentiles · the recommendation paragraph ·
anything you could not finish (exact remaining work).

Hand budget: --max-turns 80. If pressure appears, land a working demo at
S=140 with strategies A/B implemented and raycast C optional, and say
exactly what is missing.