# 28 - Controls & Camera GDD (PROPOSED)

Status: PROPOSED (Astrabot bake-in from 26-A analysis, 2026-09-13, pending
Nicko lock). LOCKED 2026-09-13 (Nicko): the 16-view ruling below is
LOCKED for the player and hero-tier enemies. LOCKED 2026-09-13 (Nicko):
the art-style question itself (billboard sprites vs low-poly pixelated
3D models) goes to a BAKE-OFF SPIKE, see doc 29. Until that verdict,
every billboard-specific rule in this doc stays PROPOSED; sections
"Lock-On Camera Behavior" and "Logical Facing Rule" are contingent on
the billboard branch winning. Closes 26-A Part 3 HIGH gaps 1 and 7,
partially gap 10. Sources: 26-astrabot-analysis.md Part 2 (Tensions 1, 2,
4, 5) and Part 3.

## Three Camera Registers (PROPOSED)

From 26-A Part 2 Tension 4. Action framing in this game is allowed to
break the tiny-figure composition; scene-03's side camera is the
precedent, written here as a rule instead of an exception.

- EXPLORATION: the concept-frame framing. Tiny figure, colossal world.
  Matches the locked composition grammar in doc 02 / doc 24.
- COMBAT: tightened lock-on framing. The player sprite reads at 15-25
  percent of frame height, with 1-3 enemy sprites simultaneously legible.
- AIM: over-shoulder reticle per doc 04's stationary aiming mode.

Sprite resolution (512-1024px, doc 02) is sized to the COMBAT register,
the tightest read, not the exploration register.

## Lock-On Camera Behavior (PROPOSED)

From 26-A Part 2 Tension 1. Cap camera angular velocity during lock-on so
sprite directional-view changes land on attack-beat boundaries. Hide view
reselection inside hit-stop, which doc 04's poise system already
generates. This keeps the no-visible-popping pillar (doc 02 tech pillar
7) honest under combat-rate camera motion.

## Logical Facing Rule (PROPOSED)

From 26-A Part 2 Tension 5. The standard retro-3D reconciliation:

- Logical facing = last input/attack direction. World-space and
  continuous. Combat logic uses this, never the rendered view.
- Rendered view = nearest directional view of that logical facing
  (camera-relative selection per doc 02).
- Block, parry, Wall of Steel, and Firm Stance arcs resolve against
  LOGICAL facing.
- Defensive poses snap their directional view to the logical facing even
  mid-camera-swing. A 45-degree snap reads as intent in a block; the
  same snap in an idle reads as a glitch. Only defensive poses snap.

## Roll Direction (LOCKED 2026-09-13, Nicko)

From 26-A Part 2 Tension 5. Two options:

- LOCKED: 16 directional views for the player and hero-tier enemies.
  The player is hero-tier by doc 02's own escalation, and 16 views
  un-quantize the dodge roll, which Slip the Blade's direction-precise
  i-frame contract leans on. Nicko: "16 makes more sense than 8."
- 8 views remain available for ambient props and distant NPCs only.

## Open Items

- Camera collision.
- Sensitivity.
- Input mapping.
- Boss-scale camera behavior vs a 10-meter billboard (26-A Part 3 gap 10).
- Exact readability-floor numbers, to be set by the UE5 spike (see the
  doc 24 bake-in section).