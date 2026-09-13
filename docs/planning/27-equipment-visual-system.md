# 27 - EQUIPMENT VISUAL SYSTEM: THE SPRITE FASHION PIPELINE
# (LOCKED 2026-09-13, Nicko: "All three decisions are approved. Move
# forward with that." D1 layered paper-doll approved; D2 doc-26 race
# cards produce bodies in neutral under-layers; D3 layer pilot approved
# as third prove-or-kill artifact.)

Status: LOCKED 2026-09-13 (D1/D2/D3 all approved by Nicko). AMENDED
2026-09-13 (Nicko ruling after the transition pass): the transition
pieces (gorget, faulds, full leg harness) are NOT equipment slots.
They are CANON LAYERS: permanently part of the body harness look, on
for aesthetics and lore, never toggleable. The paper-doll system has
two layer classes:
- CANON LAYERS (always on, baked into the body canon render): linen
  base, leg harness, faulds, gorget. Race cards produce these with the
  body canon per D2.
- EQUIPMENT SLOTS (swappable at runtime): cloak/back, gloves, chest
  (cuirass variants), helm/head, weapon, plus future variants. These
  are the fashion-expression surface.
eventually make it so that each piece of equipped armor changes the
actual player model, creating unique player expressions via fashion
and unlocked equipment. How do we achieve that?"

## 1. The Answer in One Paragraph

Layered sprite compositing, the "paper doll" pattern proven from Daggerfall
itself through modern pixel RPGs: the character body is a base sprite set,
and every equipment piece is its OWN sprite set rendered as a stack of
layers over the body at runtime. Equipping a helm swaps the helm layer's
atlas; nothing about the body changes. Unique player expression comes from
the combinatorics: N equipment pieces with M variants each yield enormous
outfit space from a small art budget. This is THE standard solution for
2D sprite characters and it maps perfectly onto our locked 360-degree
billboard system.

## 2. How It Works (the runtime model)

- The player actor renders a stack of layers, bottom to top:
  1. BODY: race/sex base sprite set (the 10 production-queue cards:
     orc/undead/vampire/elf/dwarf, male+female).
  2. LEGS: pants/greaves layer.
  3. TORSO: chest armor/surcoat layer.
  4. ARMS: gloves/vambraces (optional layer).
  5. HEAD: helm/hood/circlet layer.
  6. BACK: cloak/cape/quiver layer (renders behind body for most
     views, in front for some angles - a z-order rule per piece).
  7. WEAPON: held item layer (right/left hand anchors).
  8. FX: enchant glow / aura overlay (optional, top).
- Each layer is an atlas with the SAME frame grid as the body: 8
  directions x N animation frames, same canvas size, same anchor points.
  A layer atlas only exists for poses where the piece is visible.
- Runtime equip = swap which atlas each layer slot reads. No regeneration,
  no pipeline run, instant. The 3D engine composites the stack as
  transparent quads at the same billboard anchor (trivially cheap:
  3-8 quads per character instead of 1).

## 3. The Art Production Rules (what the pipeline must add)

The current pipeline produces MONOLITHIC characters (body + gear baked
in). For the fashion system, characters split into canonical pieces:

- R1 ANATOMY CANON: each race/sex card (doc 26) produces the body
  sprite set in a NEUTRAL UNDER-LAYER outfit (simple linen underclothes,
  no gear). This body canon is fixed forever; every equipment piece
  fits over it.
- R2 ANCHOR CONTRACT: every equipment piece is drawn to align with the
  body canon: same canvas, same ground line, same shoulder/hip/wrist
  anchor pixels per direction. A QA script must verify piece-to-body
  alignment (silhouette union looks like one character, not a collage).
- R3 PIECE GRAMMAR: equipment items are generated per piece-type with
  the body turnarounds as the image-to-image reference. One helm atlas
  = 8 directions x N frames where the helm occludes the body (idle
  first; walk later). A chest piece needs torso-visible frames; a
  cloak needs behind/front z-views.
- R4 PALETTE VARIANTS: fashion tier system via palette swaps, NOT new
  art: each piece gets variant atlases recolored by the doc 24 palette
  law (steel/iron/blacksteel/cold iron for armors; cloth dyes per
  biome signature). Scripted palette-swap tooling, near-zero cost.
- R5 QUALITY BAR: equipment layers must match the approved register
  (painterly pixel-art hybrid, dithering, one accent) and QA against
  the body: same style grain, same edge quality after defringe.

## 4. What This Enables (the design payoff)

- FASHION AS PROGRESSION: unlocked equipment = unlocked looks. The
  warp camp vanity wardrobe (doc 05 decoration system adjacent) becomes
  the player's expression surface: cosmetics stay unlocked once found.
- UNIQUE EXPRESSION: with ~20 equipment slots x ~10 visual variants
  each, outfit combinations number in the millions. Two players rarely
  match. Third-person camera makes the player's own sprite the most
  viewed asset in the game: worth every layer.
- LORE COMPATIBILITY (docs already support this): Aegis gear (doc 05)
  gets its own iconic layer set; Hunter's Relics (doc 06) get unique
  layer art as part of their fixed-acquisition stories; faction tabards
  and player heraldry (doc 14) render as the BACK/banner layer per the
  locked banner grammar.
- COMBAT READABILITY: equipment changes silhouette. Enemy grammar
  (doc 04: soldiers parry, beasts do not) stays readable because
  silhouette language (helms, shields, weapon shapes) is layered ON
  TOP of body language.

## 5. Build Order (slots into doc 26 queue)

1. NOW (before mass production): extend the doc 26 card spec: the 10
   race cards produce bodies in NEUTRAL UNDER-LAYER clothing per R1
   (re-run knight/gravedigger canon later as equipment-bearing NPCs or
   rebase them onto the body+layers system).
2. NEXT: define the ANCHOR CONTRACT precisely (per doc 26 card: anchor
   pixel map for shoulders, hips, wrists, head top) + the alignment QA
   script (tools/).
3. THEN: pilot the layer system on ONE body (the knight body):
   generate 3 equipment pieces (helm, chest plate variant, cloak) as
   layer atlases, composite them live in the billboard page with
   equip/unequip buttons. Same prove-or-kill pattern as pilots 1-2.
4. Production: equipment pieces generated per armor set doc (doc 05
   crafting tiers Crude -> Masterwork map to visual quality tiers),
   palette variants scripted per R4.
5. UE5: layer stack = multiple sprite components at identical anchor;
   material per layer; equip swap = material parameter swap.

## 6. Cost and Feasibility Verdict

- FEASIBLE: yes, and it is the industry-standard solution for exactly
  this ask. The runtime cost is near-zero (a few extra transparent
  quads). The art cost is bounded: each equipment piece is one atlas,
  and palette variants are scripted.
- HONEST COSTS: (a) the body canon must be REBASED: knight and
  gravedigger pilots baked gear into the body; those become NPC-specific
  looks or get re-derived onto the layer system. (b) every equipment
  piece is its own pipeline run (smaller than a full character: only
  the frames where it is visible). (c) z-order rules for cloaks/weapons
  need a small authored table per piece type.
- THE ALTERNATIVE, REJECTED: per-outfit full sprite sets (bake every
  equipment combination as complete characters). Combinatorially
  impossible, and it is what would force uniform player models. Layered
  compositing is the only scalable route to unique player expression.

## 7. Decision Needed from Nicko

- D1: approve the layered paper-doll direction (vs per-outfit baked
  sets). Recommended: YES.
- D2: approve R1 rebase: the 10 doc-26 race cards produce bodies in
  neutral under-layers, so equipment layers land on clean canon.
- D3: approve the layer pilot as the third prove-or-kill artifact
  (knight body + 3 equipment pieces, live composite in the billboard
  page) before the 10-card production run.

## Bake-in from 26-A analysis (2026-09-13, PROPOSED)

Status line per item: PROPOSED (Astrabot bake-in from 26-A analysis,
2026-09-13, pending Nicko lock). Source: 26-astrabot-analysis.md Part 2
Tension 3, Part 3 gap 2.

- Variant silhouette QA check: every equipment variant preserves the
  piece-type silhouette markers that enemy-grammar readability keys off
  (cross-ref doc 24 bake-in, PROPOSED). PROPOSED.
- Human body canon dependency: the paper-doll system currently lacks
  body canon for the human player body; blocked on doc 26's proposed
  human cards (doc 26 bake-in, PROPOSED). PROPOSED.