# 29 - Art-Style Bake-Off Spike: 2D Billboard Sprites vs Low-Poly Pixelated 3D Models

Status: RESOLVED 2026-09-13 (Nicko). DECISION: the game is a TRUE 3D
world. Low-poly 3D models with pixelated/posterized textures
(PSX-style retro 3D) are the character/prop carrier. The locked
painterly-pixel REGISTER is unchanged and now applies to textures,
lighting, and post-processing instead of painted sprites. All 36
concept frames and the 10 finished race-card sprite bodies remain
CANON as reference material for world building and character creation
(silhouette, palette, mood, lighting keys). This spike doc stays as
the record of the decision and converts below into the 3D PIPELINE
VALIDATION plan. The doc 02 sprite-carrier pillars and docs 25/26/27
production specs are demoted to REFERENCE (superseded for production,
kept for palette law, QA methodology, and lessons L0-L8).

## The decision (2026-09-13, Nicko)

"We're pivoting to an actual 3D design world while keeping the art
style. We can still use all the concept art that's already been
created as reference material for the world and character creation."

Grounding: 26-astrabot-analysis.md Part 2 found six of seven art-style
x controls tensions exist BECAUSE of billboards. A 3D carrier dissolves
Tensions 1, 5, and most of 2 and 6, and the register is carrier-agnostic.
The bake-off was chartered to decide on evidence; the decision is made
on design intent instead, so the spike's remaining job is de-risking,
not deciding (see converted plan below).
multiplication). A true-3D carrier dissolves Tensions 1, 5, and most of 2
and 6. The register (near-black negative space, rim light, diegetic
light, one accent, dithering, fog) is carrier-agnostic and survives
either branch. The 36 concept frames stay canon either way: they become
lighting/keys references instead of sprite sources.

## The two artifacts

Same character (gravedigger undead, char-07 / the proven pilot), same
scene, same lighting law, same locked COMBAT camera register (doc 28).

### Artifact A - Billboard (the control)

Already exists in repo: art-direction/sprites/gravedigger/ (8 directional
views, 5-frame idle, atlases, pilot-billboard.html). Spike work: mount
the existing atlas in the spike scene at gameplay camera distance under
night + fog + rim-light law. Optionally extend to 16 views (LOCKED
2026-09-13 for player/hero-tier, doc 28) for one camera-orbit stress
test to price view-popping under combat-rate motion.

### Artifact B - Low-poly pixelated 3D (the challenger)

Production chain (all staged, no keys needed to prepare):

1. SOURCE: concept-10-hunter / char-07-gravedigger-undead frame as the
   image-to-3D input.
2. IMAGE-TO-3D: Meshy (api.meshy.ai) or Tripo (api.tripo3d.ai).
   Image-to-3D mode, character preset, PBR OFF (we replace textures).
   Both auto-rig humanoid output. Cost: free trial tiers exist; paid
   ~USD 20/mo. NEEDS: an API key (not yet provisioned).
3. RE-TEXTURE (the register pass, this is where the style is won):
   - Posterize albedo to 15-16 bit color depth, or hand-pixel a
     64-128px texture per material zone.
   - Palette-limit to the gravedigger's frame palette (doc 24
     per-character palette law).
   - Nearest-neighbor filtering, mipmaps OFF.
4. MATERIAL/LIGHTING: rim-light via fresnel term (register-legal,
   diegetic keyed to lantern/moon), light-tint materials per doc 02
   pillar 3.
5. SCENE: see scene spec below.

## Spike scene spec (both artifacts, one scene)

- Engine: UE5 (version still TBD, docs 00/08; recommend whatever the
  dev machine has, the spike tests style not engine version).
- Post-process: render at 480p-720p internal, point-sampled upscale
  (crisp pixels, doc 02 scaling law); ordered dithering post-process;
  film grain.
- Lighting: single diegetic key (lantern at player), moon fill, fog
  with density keyed to two states: EXPLORATION (thick) and LOCKED-ON
  COMBAT (receded, doc 24 bake-in proposal).
- Camera: doc 28 COMBAT register (player reads 15-25% frame height),
  plus one EXPLORATION-register beauty shot for the mood comparison.

## Judging criteria (decide A vs B)

1. COMBAT READ: at locked combat camera, night + fog, can a viewer
   identify enemy verb type (wind-up/stagger/block) within 250ms?
   Formal check: 5-viewer panel, forced choice, or the qa_gate.py
   silhouette-contrast metric adapted for meshes.
2. FEEL: does dodging/locking-on feel right against each carrier
   (billboard view-popping vs mesh smoothness).
3. MOOD FIDELITY: does each artifact hold the register (near-black
   ratio, rim light, one accent) at exploration framing.
4. PRODUCTION COST PER BODY (the decider if 1-3 tie):
   - Billboard branch: known. ~1 card day per body at idle; combat
     stacks 300-700 illos per key character (doc 25 bake-in).
   - 3D branch: measure actual hours: generation minutes + retopology
     fixes + re-texture per body + rig/animation per combat pose set.
     Unknown until run. THE SPIKE MUST TIME THIS.
5. RISK: 3D branch needs retopology/rigging skills the repo does not
   yet have. Name the person/agent who owns that skill before
   mass-production is contemplated.

## CONVERTED: 3D PIPELINE VALIDATION PLAN (the spike's remaining job)

The decision is made; the spike now validates and prices the chosen 3D
pipeline before mass production. Success criteria, not A-vs-B judging:

1. REGISTER SURVIVAL: can the retro-3D stack (posterized textures,
   nearest-neighbor, point-sampled low-res render, ordered dithering,
   film grain, diegetic rim light, fog) reproduce the locked register
   at both camera registers? Compare directly against the concept
   frames; the frames are the bar.
2. CHARACTER PIPELINE PROOF: one body (gravedigger) end to end:
   concept frame -> image-to-3D (Meshy/Tripo) -> retopology fixes ->
   pixelated re-texture pass -> auto-rig -> one idle + one attack
   animation -> in-engine at the doc 28 COMBAT camera. Time every
   stage. This is the hours-per-body number that prices the project.
3. READABILITY FLOOR: numeric silhouette/contrast targets under night +
   Pale Tide fog (doc 24 bake-in proposal), now measured on meshes.
4. SKILL OWNERSHIP: name who owns retopology/rigging/texturing before
   mass production (agents, Nicko, or a hire).

## Execution blockers (what's needed to run)

- [ ] Meshy or Tripo API key (Nicko to provision, free trial OK).
- [ ] Engine access: a machine with UE5 (this VPS container has no
      Docker/UE5; options: Nicko's PC, or a hosted build runner).
- [ ] Concept frame selected and exported for image-to-3D input.

## Deliverable

A one-page pipeline validation memo appended to this doc: in-engine
screenshots vs concept frames, hours-per-body measured stage by stage,
readability numbers, and the skill-ownership call. If register survival
or cost fails, the bake-off reopens with evidence.