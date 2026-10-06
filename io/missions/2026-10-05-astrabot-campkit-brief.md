# ASTRABOT ORDER B BRIEF - WITCH HUNTER CAMP KIT GLB (stage 3 arc, rides C2/C3)

Asset lane: Astrabot (meshy gen + blender bake). Brief committed to
io/missions/ per standing law. NO dispatch until Nicko says so.

## Goal
One new GLB: the WITCH HUNTER CAMP KIT - a small deployable campsite the
player sets from the CAMP button (C3). Not a loose pair of props: a composed
site, readable at DS-bonfire distance.

## Composition (one GLB, origin at ground center, Y-up, meters)
- RIDGE TENT: A-frame canvas, worn and weather-stained; ~2.2m long, 1.4m
  wide, 1.1m tall. Slightly askew (hand-pitched, not factory).
- BEDROLL: rolled blanket + strap, lying at the tent mouth, offset so the
  interact point faces outward.
- FIRE PIT: ring of 5-7 fire-blackened stones with charred stubs inside and
  a soot decal feel at center - deliberately modest, NOT the bandit
  campfire's iron tripod look (this is the PLAYER's camp).
- Staked corners: 4-6 small pegs + taut line hints on the tent.

## Canon laws (binding, from the art bible)
- Pixelated everything: 512px NEAREST + 5-bit posterize, raw mesh as-is
  (28-32k tris target, hard ceiling ~35k), no geometry post-processing.
- PALETTE: darkwood - desaturated canvas (warm grey-green), aged leather
  straps, charcoal stones. ONE ACCENT per frame: the amber fire-glow tint on
  the pit stones' inner faces ONLY (human fire = amber, no cyan, no red).
- Tone: gothic, moonlit-world, lived-in melancholy. Nothing cheery.
- Deliver BOTH: raw .glb + -pixelated.glb (the pipeline pair, same as other
  families). Name: wh-campkit (+ wh-campkit-pixelated).
- Path: art-direction/3d/assets/camp/ (new family).

## Tech requirements
- ONE mesh per element (tent, bedroll, pit, pegs) so C-day can toggle/hide
  pieces; node names: tent, bedroll, firepit, pegs.
- Ground-contact base: no undersides visible from any of 0/120/240 persp
  angles (the Round J lesson); flat shading OK, weld rims.
- Origin centered between tent and pit; scale 1:1 to meters (props scale in
  engine: CONFIG row will place at scale 1.0).
- No rig, no animation, no embedded textures beyond the atlas.

## Verification (cheap, allowed by the no-harness law)
- Headless Blender: byte invariants + node names present + tri count report.
- Static geometry probes + 3-angle ortho renders for the underside check.
- NO game run, NO chromium, NO harness.

## Land
- Commits on feat/world-visuals: assets commit + docs proof stills; build
  commit only if CONFIG wiring is in scope for this order (it is NOT -
  C3 wires placement; stop at the asset commits).
- Report: tri counts per node, palette check, proof-still list, commit shas.