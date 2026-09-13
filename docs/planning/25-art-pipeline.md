# 25 - ART PRODUCTION PIPELINE (PROPOSED, 2026-09-13)

Status: PROPOSED for Nicko review. Nothing here is locked. This doc
answers one question: can we turn the approved concept-art register
(doc 02 + 24-art-bible) into a REPEATABLE PRODUCTION PIPELINE that
generates game-ready scene and character art? Short answer: YES, with
two honest caveats (section 6).

## 1. The Distinction That Drives Everything

The 36 cataloged concept frames are MARKETING/DIRECTIONAL art: huge
negative space, atmosphere, dithering, tiny figures. They are the
art bible made visible. IN-GAME ASSETS ARE A DIFFERENT PRODUCT:

- CONCEPT FRAMES: for key art, the art-direction page, store pages,
  loading screens, dialogue backdrops. Already production-grade (done).
- SPRITE ASSETS: the 512-1024px painted characters/props that live
  in-engine as 360-degree billboards. These need: clean full-body
  silhouettes, transparent backgrounds, neutral painted lighting (the
  3D engine applies dynamic light/rim/fog per doc 02 tech pillar 3),
  directional view sets, and per-pose frame stacks.

The pipeline below produces the SECOND product; concept frames remain
the quality bar every sprite must match.

## 2. Pipeline Stages (the factory)

S1 DESIGN SOURCE: per character, a one-page sheet from the art bible
   grammar: identity, kit items, palette (biome law + one accent),
   silhouette intent, personality pose. No generation without it.
S2 TURNAROUND SHEET: generate the character in 3-5 canonical views
   (front/side/back, neutral dark-gray studio background) using
   image-to-image with the approved reference set for consistency.
   Nicko approves ONE view as the canonical look (HUMAN GATE 1).
S3 DIRECTIONAL BAKE: derive the 8 directional views (16 for hero-tier,
   pending doc 02 ruling) from the canonical view: reference-guided
   regeneration per direction + a redraw pass. Consistency technique
   per section 5.
S4 FRAME STACKS: per pose (idle/walk/attack/hit/death), 4-6 animation
   frames per direction, pose-driven generation. Budget math in doc 02.
S5 CLEANUP (scripted, no AI): background removal to alpha (rembg-class
   model), silhouette integrity check, palette quantization toward the
   character's law-set colors, optional subtle baked dither (or leave
   to the engine shader - open ruling, doc 02).
S6 QA GATE (scripted + vision): silhouette readability at 25 percent
   and at gameplay distance, one-accent audit, frame-to-frame flicker
   check (adjacent frame diff), 512-1024px resize with crisp filtering.
   gemma4:31b vision QA + PIL metrics, same tooling as the bible QA.
   HUMAN GATE 2: Nicko thumbs the batch or it loops.
S7 ATLAS + ENGINE: pack frames into a directional atlas (Python +
   TexturePacker-class tool), import to Unreal as billboard material:
   camera-angle-to-directional-frame selection, light-tint + rim-glow
   material (doc 02 tech pillar 3), contact shadow grounding (pillar 1).

SCENE GENERATORS run the same factory minus S3/S4: concept-frame
quality scenes generated per biome/location from the bible grammar, QA
gated, then used as key art, tavern/dialogue backdrops, and worldbuilding
plates. Runtime world rendering stays TRUE 3D (locked): generated
scenes never replace the engine.

## 3. What We Already Have (proven this session)

- The register grammar: prompt template in art bible section 4
  (23+13 frames generated through it).
- Vision QA tooling: gemma4:31b against the checklist (bible section 7),
  already scripted in-session.
- Derivative tooling: PIL resize/palette/derivative pipeline
  (concepts-web build is a live S5 prototype).
- Human gate workflow: PROPOSED -> Nicko review -> lock.

## 4. What Needs Building (the actual work)

1. SPRITE PROMPT GRAMMAR: extend the bible template with a
   neutral-background studio variant (no fog/negative space in sprites;
   the engine owns atmosphere). Half a day.
2. CONSISTENCY HARNESS: reference-image conditioning workflow
   (image-to-image with approved canonical view as input) + per-character
   reference folders. Days, not weeks.
3. CLEANUP SCRIPTS: rembg alpha extraction, palette quantizer, flicker
   differ, readability resizer. A few days scripted, tested on existing
   frames.
4. ATLAS PACKER + UNREAL BILLBOARD MATERIAL: directional frame selection
   by camera angle; light-tint material. Depends on engine decision
   (doc 00 open question: Unreal version TBD). The web/prototype
   equivalent (billboard renderer in JS) can validate first.
5. THE FACTORY RUNNER: a script that walks a character sheet through
   S2-S7 and emits a pass/fail QA report per batch.

## 5. The Hard Problem: Character Consistency (honest section)

Current image models do NOT reliably hold one character across 8
directional views x multiple frames out of the box. Mitigations, in
rising cost order:
a. Reference-guided image-to-image (feed the canonical view back in).
   Works for style; drifts on identity over many generations.
b. Character turnaround sheets as fixed input + tight pose instructions
   (ControlNet-class pose control where available).
c. Per-character adapter training (LoRA/character training) for
   protagonists and retinue majors: one-time cost per character, then
   unlimited consistent frames. This is the production answer for
   named characters; rank-and-file NPCs can use (a)+(b) since slight
   drift is acceptable in procedural crowds.

## 6. Feasibility Verdict

- POSSIBLE: yes. A working pipeline PROTOTYPE (one character taken
  through S2-S7, sprite rendered in a billboard test scene) is buildable
  in days from existing tooling; a production-grade factory with adapter
  training is a weeks-scale effort once the engine target is decided.
- CAVEAT 1: fully RUNTIME generation (art generated while playing) is
  the wrong shape: it kills consistency, costs per-frame, and adds
  legal exposure. The pipeline is a BUILD-TIME factory; the game ships
  baked atlases. Recommendation: never runtime-generate.
- CAVEAT 2: human gates are load-bearing. AI generates, vision QA
  filters, NICKO approves. The approved-frame catalog is the quality
  bar; the pipeline multiplies approved quality, it cannot define it.
- CAVEAT 3: the 24:1 sprite bet (doc 02 budget framing) was chosen for
  small-team feasibility; this pipeline is how the bet is won, but the
  S4 frame math still needs the 8-vs-16 ruling to finalize budgets.

## 7. Suggested First Milestone (for approval)

PILOT: take ONE existing approved character (the gravedigger undead,
char-07) through S2-S7: turnaround sheet -> 8 directions -> one 5-frame
idle stack -> cleanup -> atlas -> billboard test render in a browser
prototype. Deliverable: a page showing the approved concept frame
beside the generated sprite rotating in-engine. That single artifact
proves or kills the pipeline before any deeper investment.

## Bake-in from 26-A analysis (2026-09-13, PROPOSED)

Status line per item: PROPOSED (Astrabot bake-in from 26-A analysis,
2026-09-13, pending Nicko lock). Source: 26-astrabot-analysis.md Part 2
Tension 6, Part 3 gaps 3/15/16.

- Combat animation cost model: a full combat pose set (idle, walk, run,
  light/heavy attacks, block, parry, hit-react, stagger, death, roll x 8
  directions) is roughly 10-15 poses, i.e. 300-700 illustrations per key
  character at doc 02's 32-48-per-animation pricing. Doc 26's queue
  prices bodies at turnaround + idle only. This is the project's largest
  unproven art bet; a prove-or-kill artifact (ONE full combat animation
  stack for the player body, in-engine) must precede any mass
  production. PROPOSED.
- Cloth flicker extended to combat: combat frames derive image-to-image
  from one source view; cloth-heavy bodies get silhouette-stabilized
  combat poses. Extends lessons L3/L4, which flagged flicker at IDLE.
  PROPOSED.
- Named-character LoRA (section 5): costing + tooling + fallback still
  open. PROPOSED (carried open).
- Human approval gates (caveat 2): throughput model needed before
  production scales to hundreds of NPCs + thousands of equipment pieces
  (doc 27 section 4). PROPOSED (carried open).