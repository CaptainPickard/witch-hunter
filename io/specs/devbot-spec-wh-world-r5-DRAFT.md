# DEVBOT SPEC (DRAFT v0 — NOT DISPATCHED until prior round lands; finalize then)

# DEVBOT SPEC — Witch Hunter World R5: collision + world bounds (P0-5 + P1-4 camera half)
Branch: feat/world-visuals. Authority: doc 61 P0-5 (audit :312-321), M-13/M-15/M-16;
P1-4 (:382-405) camera occlusion HALF only (M-14) — the post pass / camera occlusion
raycast may defer per dispatch-time audit re-read; P0-5's camera ground clamp is in.

## Live-tree anchors (verified 2026-10-02 @ R2 worktree)
- CFG.world.groundRadius = 90 (CONFIG.js:58); CFG.boundary.z = -25 (:216-218);
  regionA.spawn (0,45) / regionB.spawn (0,-45) (:76,:137).
- RegionManagerLogic.clampPlayer (region-manager.js:99-113): boundary-plane-only;
  chokepoint corridor free passage; active-home-side pushback. THE R5 EXTENSION
  SURFACE: add radial disc clamp (r = groundRadius - CFG.world.playerMargin) here
  or in game.js clampPlayerToBounds (game.js:455-465) — pin ONE place.
- Prop footprint basis: WH_ASSETS GROUND_META (assets.js:90,119-123:
  height/width/groundMinY per holder uuid); CONFIG props arrays carry x,z,scale.
- Camera: player.js:92-93 camYaw/camPitch init; :229-231 pitch clamp
  (camPitchMinDeg -15 / Max 65 CONFIG.js:271-272); game.js:372-373 reticle uses
  window pixels. Camera ground clamp: min camera y >= 0.4 over ground (audit) —
  wire into the camera follow math; M-13 bar: camera y >= 0.3 organic max zoom.
- Spawn validator (boot-time): every prop+enemy home-side + inside playable radius;
  A's ghoul spawn z >= -23.5 fix or deliberate gate-guard config flag.

## Design (per audit verbatim)
1. Radial clamp: player AND enemies to groundRadius - margin (new CONFIG key
   world.playerMargin; enemies keep their boundary-hold logic, add the radial
   clamp in enemy movement or region-manager's enemy path — pin file).
2. Visual ground 1.1x fog-opaque: B is the shortfall candidate (fogFarFactor
   1.5 * radius 90 = 135 > disc 90). If region builds use a fixed ground disc,
   extend B's visual disc to ~1.1x its fog-opaque distance with texture repeat
   scaled to keep texel density (groundTexture.repeat recalc per region).
3. Prop colliders: per-prop cylinder/circle from GROUND_META.width x scale
   (footprint), pushed out in clampPlayerToBounds AFTER the boundary clamp;
   radial pushout against prop circle (player radius CFG.player.radius).
   Chokepoint-corridor props exempt from collision (the gate path itself).
4. Camera clamp (anchors: player.js:896-948 updateCamera — orbit offset
   = sin(yaw)cos(pitch),sin(pitch),cos(yaw)cos(pitch) * camDist, lerp into
   camera.position, lookAt(target); pitch clamped at mousemove :229-231;
   CFG.camHeight/camMaxDistance/camMinDistance exist): (a) add min-pitch
   ground clamp AFTER orbit-want computation: camera.position.y = max(want.y,
   groundY + 0.4) per audit P0-5; (b) max distance by pitch law: camDist
   effective = clamp(camDist, camMinDistance, camMaxDistance_by_pitch) where
   the by-pitch cap shrinks as pitch rises (steep-down = closer); document
   the formula (e.g. maxDist = camMaxDistance * cos(pitch) shaped) and pin
   it in the spec amendment at dispatch. M-13 bar: camera y >= 0.3 organic.

## ACs (shape; finalize with numbers at dispatch)
- AC-R5-1 (M-15): walk-toward-edge probe: radial clamp holds player within
  groundRadius - margin in EVERY direction (8-heading teleport+walk sweep);
  no visible luminance step at the rim in the readback at the clamped pos.
- AC-R5-2 (M-16): boot validator: 0 violations (both regions, 104+ props);
  A ghoul inside its home side with a pinned spawn (z >= -23.5 or configured).
- AC-R5-3 (M-13): organic camera zoom-in + mouse pitch rise: camera y >= 0.3
  at all times; distance shrinks as pitch rises (max distance by pitch law).
- AC-R5-4: prop collision: walk into lanternPost A1 (-2,30) from +x: player
  pushed out, |pos - socket| >= prop radius + player radius - 0.02; no push
  through the chokepoint corridor centerline from colliders.
- AC-R5-5: crossings still work (L1 crossing re-proof via R2 harness floor).
- AC-PRES: R2 harness floor re-run (part10 pattern); scope set-diff within
  region-manager.js/CONFIG.js/game.js/R5 specs+reports/harness surfaces;
  combat/anim hunks byte-identical; secrets clean.

## Retune: exactly-once retune for bars (margin, collider radii); second
## identical numeric failure = STOP. Harness: tests/wh_world_r5_validation.py
## from r5parts/ (same laws).