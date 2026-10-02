# DEVBOT SPEC — Witch Hunter World R4: pixelated character bodies (P0-7 RE-SCOPED)
Branch: feat/world-visuals. Base: R3 validated marker cce06eb. Authority: doc 61
P0-7 + THIS RE-SCOPE (evidence
2026-10-02): the audit's premise "pixelated race variants exist" is STALE for
RIGGED bodies — races_regen contains ZERO *pixelated* GLBs (verified: only
10 raw rigged GLBs); every rigged body = 1 material + ONE 2048x2048 JPEG
atlas, smooth PBR painterly (vision QA on extracted atlases: no texelation,
no quantization, full 8-bit gradients), ~28-33k tris, 1 skin each. The
manifest (prototype/js/assets.js:46-49) wires 3 rigged bodies as
playerBody/banditBody/ghoulBody. whanim2 owns rig + AnimationMixer state
machine + skinned instancing.

## Re-scoped design (art law: raw mesh as-is + color pixelation only)
1. PIXELATE THE ATLAS TEXTURES of the 3 in-manifest rigged bodies at
   POSTLOAD: after loadOne/prepTemplate, replace m.map with a processed
   texture: draw texture.image to a 512px canvas (NEAREST downscale),
   5-bit posterize per channel (pattern: art-direction/3d/biome_pixelate.py
   v3 color law), THREE.CanvasTexture + NearestFilter mag + keep min as
   prepTemplate set (LinearMipmapLinear) + needsUpdate. GPU memory law:
   2048^2 RGBA ~16.7MB -> 512^2 RGBA ~1MB per body via renderer.info.memory.
   NO geometry post-processing, NO rigging changes, NO bone/skin edits.
   Offline alternative (if canvas/ImageBitmap path fails on SwiftShader):
   pre-committed pixelated PNG atlases beside the rigged GLBs + manifest
   map override — DECISION EVIDENCE REQUIRED at dispatch (bake test via
   the biome_pixelate runner bound to the WORKTREE).
2. Anim compatibility gate: every anim2 state-machine AC re-runs
   (whanim2 harness subprocess) + R1 A2 body grounding re-check (the A2
   drift stays parked per R2 ruling; texture swap must not worsen it —
   same minY bars as the pre-R4 capture, recorded).
3. CONFIG: new key assets.pixelatedBodies: true (kill-switch documented).

## MECHANISM RULING (bake evidence 2026-10-02): OFFLINE BAKE chosen. PIL
## present; 2048 JPEG atlas -> 512 NEAREST + 5-bit posterize PNG: hunter
## 204349B, orc 243700B, ghoul 206150B (from ~2.7-3.2MB each). Vision QA on
## ALL THREE: texelation visible, banding visible (ghoul: source already
## dithered, banding N/A), shapes/armor readable, no unusable artifacts.
## The 3 pixelated PNGs are BAKED AND READY at /tmp/wh_r4_atlas/
## (*-pixelated.png): COPY them into
## art-direction/3d/assets/races_regen/rigged/ (committed surface) and
## wire assets.js postload: m.map -> TextureLoader PNG (Nearest mag per
## prepTemplate law, min LinearMipmapLinear unchanged), driven by the new
## CONFIG kill-switch (off = original atlas path unchanged). Baking in-repo
## at dev-time is FORBIDDEN for Devbot (no PIL at game runtime; the PNGs
## ship as data). The runtime canvas/ImageBitmap alternative is the
## documented fallback; decision evidence recorded.

## ACs (shape)
- AC-R4-1 per body (player/bandit/ghoul, kill-switch ON): texture image is
  the pixelated PNG at 512x512, magFilter Nearest, minFilter
  LinearMipmapLinear; renderer.info.memory.textures count unchanged
  (swap, not add); kill-switch OFF = original atlas texture loads (both
  states probed).
- AC-R4-2: GPU memory drop measured via renderer.info.memory readback:
  per-body atlas 2048^2 -> 512^2 (~64x per-texture byte drop); RECORD
  table per body (textures count + bytes before/after if exposed).
- AC-R4-3: visual block structure: forced render + toDataURL in ONE
  evaluate; character-region pixels form posterized blocks (5-bit
  distinct-color histogram: <=8 shades per channel bucket on body px).
- AC-R4-4: anim2 harness subprocess PASS (state machine unaffected).
- AC-R4-5: R1 subprocess floor (part10 ac_floor pattern, inherited waiver
  classes): A1 ground-align PASS; A2 numbers not worse than the R2-era
  baseline (record).
- AC-PRES: scope set-diff within assets.js/CONFIG.js/rigged PNG assets/
  R4 specs+reports/harness surfaces; combat/anim hunks byte-identical;
  index.html byte-identity vs cce06eb; secrets clean; no "free" literals.

## Retune: exactly-once (512->256 or posterize tweak), evidence recorded;
## second identical numeric failure = STOP.
# Harness: tests/wh_world_r4_validation.py assembled from r4parts/ (pattern
# preserved); same harness laws as R2/R3.