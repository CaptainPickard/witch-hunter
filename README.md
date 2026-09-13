# Witch Hunter

A single-player, third-person open-world dark fantasy action RPG.
"A more stylized, but pixelated version of Elden Ring": a Daggerfall-like
retro 3D world (dynamic lighting, fog, volumetrics) with modern
Souls-style action combat, rendered in a painterly pixel-art register.
PIVOT 2026-09-13 (Nicko): characters, creatures, and props are low-poly
3D models with pixelated/posterized textures (PSX-style retro 3D); the
locked painterly-pixel register now lives in textures, lighting, and
post-processing. All concept art and sprite cards remain canon
reference for world and character creation.

## Repo Contents

- docs/planning/ - the full planning set (25 docs: vision, world design,
  combat, crafting, quests, factions, transformation lines, followers,
  art style, art bible, art pipeline).
- docs/planning/24-art-bible.md - canonical concept-art catalog (36
  frames), locked mood register, per-biome palette law, generation
  grammar, QA checklist.
- docs/planning/25-art-pipeline.md - the art production pipeline (S1-S7
  sprite factory) and feasibility verdict.
- docs/planning/26-astrabot-analysis.md - Astrabot project digest, art-style x third-person-controls analysis, and gap audit (2026-09-13).
- docs/planning/28-controls-camera-gdd.md - PROPOSED controls and camera GDD (camera registers, billboard facing rules, roll direction, readability floor).
- docs/planning/29-art-style-bake-off-spike.md - RESOLVED: pivot to a true 3D world (low-poly pixelated models, PSX-style), locked painterly-pixel register unchanged, all concept art retained as canon reference. Contains the 3D pipeline validation plan.
- art-direction/ - concept art masters (concepts/), web derivatives
  (concepts-web/), reference images, the canonical art-direction page
  (00-art-direction.html, self-contained), gothic fonts.
- art-direction/sprites/gravedigger/ - the PILOT: first character taken
  through the full sprite pipeline (turnaround, 8 directional views,
  5-frame idle stack, alpha/defringe cleanup, atlases, live billboard
  test page pilot-billboard.html). Retained as canon reference and QA
  methodology after the 3D pivot (doc 29).
- tools/ - the pipeline's scripted tooling (see tools/README.md).

## The Art Register (locked)

Painterly pixel-art hybrid illustration. Dithered gradients and film
grain. 60-80 percent near-black negative space. Tiny lone figures
dwarfed by colossal scale. Low-key chiaroscuro, backlit rim light,
diegetic light sources only. Monochromatic cool base with exactly one
accent per frame. Third-person camera. The frame is a held breath.

## Status

Pre-production. Design locked through world GDD, combat, crafting,
quests, and followers. Art register locked with concept frames approved.
Sprite production pipeline piloted and proven end-to-end on one
character (the gravedigger undead).

## Note

All AI-generated art in this repo was produced for the Witch Hunter
project by CaptainPickard with IO (Hermes Agent) as the production
tooling. Planning docs are internal design material.