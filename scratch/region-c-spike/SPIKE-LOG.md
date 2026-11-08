# CC-C1 · Heightfield spike — SPIKE LOG

Region C (Forest of the Old King) · brief `io/missions/2026-10-07-cc-c1-heightfield-spike.md`
· built 2026-10-07 on `feat/world-visuals` @ 562442d · scratch-only, nothing committed.

## Files

| file | role |
|---|---|
| `index.html` | demo page; loads `../../prototype/vendor/three.classic.js` (r185) then `region-c-spike.js` |
| `region-c-spike.js` | all demo code. CORE (terrain, samplers, stats) is DOM-free and also `module.exports` for node; DEMO boots only when `document` exists |
| `measure-node.js` | CPU-side numbers in this log (node, no browser/renderer/game) |
| `SPIKE-LOG.md` | this file |

Path note: the brief says `../../vendor/three.classic.js`; from `scratch/region-c-spike/` that
resolves to a non-existent `/tmp/wh-worldfeat/vendor/`. The page uses
`../../prototype/vendor/three.classic.js` (the absolute file the brief names). Works over
file:// or any static server rooted at the repo (classic scripts, no modules).

## Terrain (deterministic, A4)

- Seed `1337`. Value noise: 32-bit integer lattice hash (`Math.imul` mix) → [0,1),
  smoothstep-interpolated. fBm 4 octaves, base wavelength 45 u, lacunarity 2.0, gain 0.45,
  per-octave salt `SEED + o·1013` and offset `(o·17.13, −o·9.71)`, normalised to [0,1].
- Remap: `h = 5 · clamp((n − 0.22) / (0.79 − 0.22))`; 0.22 / 0.79 are the p1 / p99 of fbm01 over
  the plane (measured: p1 0.222, p50 0.518, p99 0.785, min 0.132, max 0.917).
- Spawn pocket: `h = 0.4` inside r 25, smoothstep blend to the raw height at r 45.
- Resulting heights (2 u grid): p50 2.61, p90 4.03, p99 4.96, max 5.00; spawn h(0,0) = 0.400.
- Only `+ − × ÷ floor sqrt imul` in the height path → IEEE-exact, identical in every engine.
  Verified: two builds per S hash to the same grid (FNV over Float32 bits):
  S100 `55f82d9c`, S140 `c5a19f53`, S180 `f2237fff` (run1 = run2).
- Mesh: `PlaneGeometry(560, 560, S, S)`, `rotateX(−π/2)`, vertex y = heightA(x, z). r185 layout:
  vertex (ix, iy) at world (ix·seg − 280, iy·seg − 280); each quad split on the
  (ix, iy+1)–(ix+1, iy) diagonal. MeshStandardMaterial flatShading + vertex colours (moss
  `#2c4424` → stone `#8c7b5e` by height). Hemisphere + 1 directional. Fog `#b9c6c4` 50→190.

## Measurement table

CPU side (node 24, this box, `measure-node.js`; build ms = 2nd build after a warm-up build):

| S | seg (u) | verts | terrain tris | build ms (node) |
|---|---|---|---|---|
| 100 | 5.60 | 10,201 | 20,000 | 10.4 |
| 140 | 4.00 | 19,881 | 39,200 | 26.7 |
| 180 | 3.11 | 32,761 | 64,800 | 55.4 |

GPU / fps side — **PENDING Nicko's browser load.** No browser was run (hard law). The page runs a
~63 s scripted cross-hill waypoint walk once at load (S 100 → 140 → 180, 1 s warm-up + 20 s
measured each, run speed 9 u/s, guard off for the scripted path), then shows per S: avg fps,
1%-low fps (from p99 frame time), JS cpu ms/frame p50/p99, `renderer.info.render.triangles`,
draw calls, build ms (browser), verts. Press **M** for the same table as markdown to paste here.
Expected renderer tris = terrain tris + actor (capsule 4/10 + box ≈ 0.2k), 1 terrain draw call.
fps is capped at the display refresh (vsync) — read the 1%-low and cpu ms for headroom.

| S | renderer tris | calls | build ms (browser) | avg fps | 1% low | cpu ms p50/p99 |
|---|---|---|---|---|---|---|
| 100 | _pending_ | | | | | |
| 140 | _pending_ | | | | | |
| 180 | _pending_ | | | | | |

## Sampler comparison (1000 seeded points, reference = C raycast)

Points: mulberry32(1337), uniform in ±279.5. Per-call µs = node, 50 reps × 1000 (A/B/B-TRI),
single pass for C. Browser µs appear in the HUD after the bench.

| S | strategy | max \|diff\| (u) | mean \|diff\| (u) | µs/call |
|---|---|---|---|---|
| 100 | A analytic fBm | 0.3496 | 0.0545 | 0.139 |
| 100 | B grid bilinear | 0.1599 | 0.0148 | 0.066 |
| 100 | **B-TRI grid triangle** | 0.0000 | 0.0000 | 0.079 |
| 100 | C raycast | ref | ref | 1262.9 |
| 140 | A analytic fBm | 0.1843 | 0.0312 | 0.123 |
| 140 | B grid bilinear | 0.0898 | 0.0090 | 0.060 |
| 140 | **B-TRI grid triangle** | 0.0000 (7.1e-15) | 0.0000 | 0.076 |
| 140 | C raycast | ref | ref | 1983.8 |
| 180 | A analytic fBm | 0.1472 | 0.0203 | 0.134 |
| 180 | B grid bilinear | 0.0696 | 0.0063 | 0.032 |
| 180 | **B-TRI grid triangle** | 0.0000 | 0.0000 | 0.037 |
| 180 | C raycast | ref | ref | 3227.5 |

0 raycast misses at every S.

**Verdict (all three S): CC-C4 `heightAt` = B-TRI** — the cached vertex-height grid,
interpolated over the same two triangles per quad the mesh draws. Fallback order:
B bilinear → A analytic → C raycast (debug/validation only).

- The brief's "A or B < ~0.05 at S=140" did **not** hold: A max 0.184, B max 0.090. A misses
  because octave 4 (wavelength 5.6 u) is below the S=140 mesh Nyquist (2·seg = 8 u), so the mesh
  cannot represent it; B misses because bilinear ≠ the triangle split. B-TRI is exact (float
  noise only), so "mesh and sampler share one function" holds in the form: **one Float32 grid,
  produced once by heightA, feeds both the mesh vertices and heightAt.**
- B-TRI costs ~0.04–0.08 µs, ~25,000× cheaper than raycast; raycast is brute force over every
  triangle (no BVH in vendored three) and scales with S: 1.3 / 2.0 / 3.2 ms per call.

## Slopes + climbFactor

Analytic (central differences on heightA, 2 u grid, n = 78,400) and rendered facets (degrees):

| source | p50 | p90 | p99 | max |
|---|---|---|---|---|
| analytic heightA | 4.7 | 9.0 | 12.9 | 19.5 |
| facets S=100 | 4.3 | 8.3 | 12.1 | 16.9 |
| facets S=140 | 4.5 | 8.6 | 12.5 | 18.2 |
| facets S=180 | 4.6 | 8.8 | 12.7 | 19.0 |

Guard as specified: reject the move when `|Δh| > maxStepPerFrame = runSpeed · dt · climbFactor`.
Per-frame horizontal step is `speed · dt`, so this is a dt-independent slope cap
`tan(cap) = climbFactor · runSpeed / speed` (dt clamped to 50 ms).

| climbFactor | run cap | facets blocked running (S140) | walk cap | blocked walking |
|---|---|---|---|---|
| 0.15 | 8.5° | 10.51% | 12.7° | 0.82% |
| **0.20 (demo default)** | 11.3° | 2.24% | 16.7° | 0.02% |
| 0.25 | 14.0° | 0.26% | 20.6° | 0.00% |
| 0.30 | 16.7° | 0.02% | 24.2° | 0.00% |
| 0.60 | 31.0° | 0.00% | 42.0° | 0.00% |

**climbFactor used in the demo: 0.20**, picked only so the guard is observable on these gentle
hills (Shift-run up the steeper faces blocks; walking barely ever does). `[` / `]` tune it live
(±0.05); the HUD shows both caps, the last |Δh| vs max, and a blocked counter. The actor flashes red
on each reject.

## Recommendation

**Production S = 140** (39,200 tris, about 2% of the 2M slice budget, one draw call, 4 u cells).
S=180 adds 65% tris for little visible gain under flat shading. S=100's 5.6 u facets look
noticeably coarser. **Pending:** Nicko's bench fps must confirm there's no cliff at 140; the CPU
side gives no reason to expect one.

**Sampler = B-TRI as the single source of truth for CC-C4.** Player, enemies, props, corpses and
the camp ghost all read the same Float32 grid that built the mesh, so the error against the
rendered surface is zero at ~0.08 µs per call. Fallbacks: B bilinear (≤0.09 u at 140, only if
the mesh triangulation ever stops matching), then A analytic (off-mesh queries, ≤0.18 u), then C
raycast (validation/debug only, never per-entity per-frame).

**climbFactor:** at this amplitude (height 0..5, p99 facet 12.5°, max 18.2°) natural terrain never
needs blocking. Ship 0.6 (31° run / 42° walk) as a safety net for authored steps such as rocks,
roots and camp edges. Better still, replace the formula with a speed-independent slope-angle cap
(`|Δh| / |Δxz| > tan(maxSlope)`). The brief's formula lets a walking actor climb steeper slopes
than a running one, which feels inverted.

**Warnings:**
1. **Raycast is 1.3–3.2 ms per call.** Any per-frame, per-entity raycast heightAt would blow
   the frame budget. Keep C out of gameplay.
2. **The build stall is synchronous** (node: 27 ms at 140, 55 ms at 180; see the HUD for browser
   numbers). Build once at region load and never rebuild on the fly or on a tab return. The demo's
   1/2/3 toggle rebuilds on purpose so the stall shows. rAF pauses on hidden tabs, so the bench
   flags itself invalid if the tab is hidden.
3. **Fog only hides the edge from the middle.** Fog far is 190, so the edge is invisible from
   spawn (280 u away), but the bench path reaches 220 u from centre, 60 u from the edge, and the
   edge shows there. CC-C3 needs fog far < (mesh edge − walkable boundary), or a skirt/ring past
   the walkable disc. With the production disc r=280, play must stop well inside it, or the mesh
   must extend past it.
4. **Any future LOD, decimation or re-triangulation breaks B-TRI exactness.** The grid must
   always be derived from the final mesh vertices and its diagonal convention.
5. **Octave 4 is sub-Nyquist at S≤140.** Harmless with B-TRI, which makes A irrelevant at
   runtime, but don't trust A for gameplay.
6. **The heightfield mesh is not the budget risk** (doc 61): the tree scatter on top of it (CC-C3)
   is.

## Controls (demo)

WASD move (camera-relative) · Shift run · drag orbit · wheel zoom 8..24 · 1/2/3 S = 100/140/180 ·
H cycle sampler (B-TRI → C → A → B) · [ ] climbFactor · R respawn · B rerun bench · X skip bench ·
M results markdown. Camera y ≥ ground(camera xz) + 1.5 every frame.
