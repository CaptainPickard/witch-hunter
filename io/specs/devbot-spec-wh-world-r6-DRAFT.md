# DEVBOT SPEC (DRAFT v0 — NOT DISPATCHED until prior round lands; finalize then)

# DEVBOT SPEC — Witch Hunter World R6: region-crossing spike (P0-6)
Branch: feat/world-visuals. Authority: doc 61 P0-6 (audit :323-329) + M-05/M-06
(+ M-22 row re-read at dispatch). Last of the P0 world rounds; enables more
regions/assets (ordering constraint satisfied: P0-4 landed R3, P0-6 after R2).

## Live-tree anchors (verified 2026-10-02 @ R2 worktree)
- RegionManager.prototype.disposeRegion (region-manager.js:371-390): traverse
  disposes EVERY mesh geometry + material + maps unconditionally — no
  userData.whShared exemption. THE SPIKE: template resources re-upload on the
  next buildRegion (boot GLB re-upload of ~MBs per prop + ground canvas).
- Prewarm path: logic.tickTransition 'prewarm' -> buildRegion(hidden=true)
  (region-manager.js:75-78,396-397); 'cross' -> reveal + disposeRegion(old)
  (:405-417). No renderer.compile / initTexture ANYWHERE (R6's missing half).
- Cache: assets.js cache[name] template reuse (loadOne/cache hit path) —
  template materials ARE shared references today; disposal destroys them for
  the surviving/returning region.

## Design (per audit)
1. Tag: every template geometry/material/texture gains userData.whShared=true
   at load (assets.js loadOne/prepTemplate + region-manager ground/mist
   canvas excluded where per-region).
2. Dispose: disposeRegion skips any geometry/material/texture carrying
   userData.whShared (dispose only per-region overlays: ground canvas tex,
   mist, per-clone materials). Record BEFORE/AFTER info.memory across
   crossing cycles.
3. Prewarm GPU ready: during buildRegion(hidden) call renderer.compile(group,
   camera) + renderer.initTexture(map) spread over 2-3 frames (rAF-chunked;
   vanilla function shapes only).
4. M-06 spike proof: SwiftShader rAF timestamps around organic crossing —
   relative frame-time table RECORD (GPU bar 0 frames > 33ms translates:
   no crossing frame slower than 1.25x the pre-crossing p95; measured
   relative, not absolute — hardware delta documented).

## ACs
- AC-R6-1 (M-05): 5 round-trip crossings: info.memory.geometries/textures
  growth <= +2 total; programs growth <= +2 (L5's boot-identity law holds).
- AC-R6-2 (M-06): crossing frame-time table: max crossing-cycle frame time
  <= 1.25x pre-crossing p95 (SwiftShader-relative translation of the GPU
  bar; hardware bar recorded as N/A-on-SwiftShader).
- AC-R6-3: crossing continuity: L1/L2-class checks + R2 harness floor PASS
  (crossing still flips regions, hemi rescale, moon unscaled).
- AC-R6-4: whShared tags audit: every template resource tagged; dispose
  skips them; SECOND return-crossing build reuses the SAME geometry uuid
  set (readback proof of no re-upload).
- AC-PRES: scope set-diff within region-manager.js/assets.js/R6 specs+
  reports+harness; combat/anim hunks byte-identical; secrets clean.

## Retune: exactly-once (tag-set or compile-chunk count); second identical
## numeric failure = STOP. Harness: tests/wh_world_r6_validation.py from
## r6parts/ part pattern; same harness laws (SwiftShader, no
## preserveDrawingBuffer, camera settle, identity-guarded server reuse).