# 02 - Art Style and Presentation

## Core Look
3D world, 2D inhabitants. Terrain, buildings, dungeon geometry, water, weather,
and light are real-time 3D in Unreal. All characters (player, NPCs, enemies,
creatures) plus key interactive props (chests, doors, shrines, resource nodes)
are billboarded 2D sprites in a retro dark fantasy illustration style.

## Sprite Direction
- Style: 1980s/1990s dark fantasy and pulp illustration. Heavy inks, dramatic
  anatomy, grim palettes, painterly shading. Think Frazetta / Bisley / early
  Warhammer covers redrawn as game sprites.
- Consistency rule: sprites are illustrations first. They should look like
  cover art cropped and pasted into a 3D world, not pixel-art cutouts.
- Resolution (locked 2026-09-11): hand-drawn high-res illustrations, 512-1024px
  per sprite, scaled down with crisp filtering (not nearest-neighbor
  pixelation) so the painted feel survives.
- Animation (locked 2026-09-11): 4-8 frames per animation. Flipbook-style
  frame animation for movement, attacks, hits, deaths. Fewer frames, high
  impact, each frame is a full illustration.
- Budget framing (locked 2026-09-11): this resolution/frame target was
  chosen specifically because it is feasible for a small team while
  preserving the pulp-illustration feel. It is the production bet of the
  whole art pipeline.

## Why This Works in a Modern Engine
The retro sprite cast against volumetric fog, dynamic torchlight, real shadows
on the ground beneath them, and weather creates deliberate contrast: the cast
is timeless, the world is alive. The lighting sells depth and mood that the
2D art cannot, and the 2D art sells character that modern realism cannot.

## Presentation Decisions Locked Since First Draft (2026-09-11)
- UI: modern Souls-style - clean menus, diegetic touches where cheap (doc 08
  resolved). The character menu carries the moral axis, specialty titles with
  their retention conditions, and pose/emote unlocks.
- Dialogue: in-world sprite conversations, with illustrated portrait panels
  for key story NPCs (courts, throne figures, retinue majors). The portrait
  panels are where the pulp-illustration style gets to shine close-up.
- ALL props are 2D: loot on the ground is sprite-based, not 3D rigid props.
  Fully committed style.
- Mounts exist as sprite mounts (travel speed only).
- The warp camp (doc 11) makes sprite-based structures a major art category:
  tents, structures, defenses, and decorations are all authored sprite assets,
  and player-created banners/heraldry (doc 14 lore rights) will need a
  player-facing banner creation UI. Flagged early for the tech plan.

## Affinity-Relative Art Direction (new, from doc 12)
The moral axis now shapes presentation, not just mechanics:
- Good and evil players get different pose/emote unlocks on the character
  screen (honorable/stoic vs. powerful/dominating).
- The dangerous half of the day differs by affinity (good fears night, evil
  fears daylight sleep), which means lighting design must read BOTH modes
  as intentional: the same scene at midnight is threat for one player and
  home ground for another.
- Court-keyed spells (Holy Wards vs. Dark Pacts) and the necromantic taint
  meter need visual language that keeps the 2D-cast style: sprite-scale
  effects, not modern particle realism.

## Technical Pillars (to validate in Unreal)
1. Billboard sprite rendering with correct world-space grounding (contact
   shadows, foot placement, occlusion handling).
2. Sprite frame animation system with animation states driven by the combat
   controller.
3. Lighting integration: sprites receive light direction info for tinting /
   rim glow so they react to the scene's dynamic lights.
4. Fog and depth integration: sprites fade / tint with distance fog like 3D
   geometry.
5. Performance: hundreds of animated billboard sprites in towns without frame
   drops (instancing / flipbook texture atlases).
6. (New) Player-authored heraldry/banners flowing onto flags, map markers,
   and tabards - flagged for the tech plan with the warp camp building system.

## Precedents to Study
- Doom / Doom II and Blood for sprite-in-3D heritage.
- Daggerfall for UI, map, and world structure in this style family.
- Octopath Traveler (HD-2D) as proof the hybrid reads, with our direction
  going grittier and darker, not pastel.

## MOOD REGISTER: THE BLESSED LOOK (LOCKED 2026-09-12, Nicko, on review
of the nine generated concept frames: "These are exactly what im going
for. You got the concept right 100%")

Reference family (9 reference images analyzed + 3 approved concept frames
in art-direction/concepts/): a retro dark fantasy ILLUSTRATION register,
not a graphic-design register. "A more stylized, but pixelated version of
Elden Ring": Daggerfall-like retro 3D world with modern Souls-style action
combat, presented in full-scene illustrated concept art.

- CORE REGISTER: painterly-pixel hybrid illustration. Chunky visible
  brushwork and faceted shapes that never resolve into photorealism,
  with dithered gradients and film grain layered on top (16-bit/VGA
  era flavor). Sprites are illustrations that read as cover art living
  inside a living 3D world.
- COMPOSITION GRAMMAR (per frame): massive negative space, 60-80 percent
  of the frame in near-black or fog; the lone figure TINY in the frame
  (lower third or lower), dwarfed by colossal architecture or wilderness
  scale; deep one-point perspective or natural framing (trees, arches,
  cliffs as a vignette); layered z-depth (foreground props, midground
  figure, background void).
- LIGHTING LANGUAGE: low-key chiaroscuro; backlit rim lighting on the
  figure's silhouette; small diegetic light sources only (lanterns,
  torches, beacons, bioluminescence, the moon); thick volumetric fog and
  atmospheric perspective; light is scarce and every light is a location.
- PALETTE LAW: monochromatic cool base (deep indigo, Prussian blue,
  slate, charcoal, obsidian) with EXACTLY ONE accent per frame: warm
  amber (lantern/torch), electric cyan (magic/bioluminescence), or
  blood-moon crimson (threat/supernatural). One warm note per panel,
  no warm/cool salad.
- PER-BIOME PALETTE VARIATION (locked intent, from the approved frames):
  Darkwood = indigo/slate + amber lantern; moors = midnight/violet heather
  + silver beacon; swamplands = teal/olive + drowned-dead green glow;
  mountains = white/blue + torch gold; farmland = warm dusk + hearth
  amber; blight = ash gray/violet-black + blood-red (the one biome whose
  accent IS the danger).
- MOOD TARGET: quiet dread, solitude, awe. Not grimdark misery, not
  poster energy. The frame is a held breath, not a shout.

## 360-DEGREE SPRITE ROTATION (PROPOSED 2026-09-12, Nicko: "all characters
and assets in the game can be sprites with 360 degrees of rotation")

The classic Wolfenstein/Daggerfall billboard system, upgraded: every
sprite character, creature, and prop renders from a full rotation set.
As the camera orbits, the sprite re-selects its directional view.

- DIRECTIONAL VIEWS: 8 or 16 directional views per pose (8 = the
  Daggerfall standard and the production baseline; 16 = hero-tier
  characters and bosses only, if budget allows). The camera-facing view
  is selected per frame render.
- FRAME MATH IMPACT: the locked 4-8 frames per animation now multiplies
  by directional views. Working budget: 8 directions x 4-6 animation
  frames per pose for key characters = 32-48 illustrations per
  animation; 8 directions x 1 view for ambient/set-dressing props.
  Production mitigation (from the locked budget framing): generate the
  master illustration once, derive directions by redrawing over a shared
  turnaround sheet, NOT by animating from scratch per direction.
- PAINTED FEED RULE: each directional frame is still a full illustration
  at the locked 512-1024px, scaled down with crisp filtering. Rotation
  must not degrade the painted feel into pixel-art cutouts.
- TECH PILLAR (new #7 for the validation list): directional sprite
  selection logic in-engine (angle from camera to sprite -> nearest
  directional view), with the flipbook atlas extended to a directional
  atlas. Validation: no visible "popping" between adjacent views at
  gameplay camera distances.
- PRECEDENT: Doom/Daggerfall directional billboards, modernized by the
  512-1024px painted resolution so close-ups still read as illustration.

## Open Questions (carried)
- Sound and music direction: no doc yet (tracked in 08-open-questions).
- Cutscene format beyond the dialogue/portrait system.