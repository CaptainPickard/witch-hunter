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

## The Pitch

You arrive on the continent with nothing. No name, no coin, no title,
no sword worth the leather that holds it. What you do with the next
hundred hours is the game. There are no fixed routes, no quest compass
walking you through a plot. The continent is ~130 km2 of hand-authored
wilds and ~25 holds, every one a real place with a noble family, a
tavern, and a dungeon cluster waiting under it. You hunt. You level.
You collect companions. And the world, quietly at first, starts to
learn your name.

That learning is mechanical, not cosmetic. The world keeps a deed log:
every kill, purge, sparing, escort, and betrayal. Rumors in taverns
change because of what you did. Patrols shift. Factions that once sent
killers now send envoys. Titles you can hold, quest lines that open,
which half of the day belongs to you, all of it reads from the life
you have actually lived. The build is the playthrough, and the world
reacts to the build.

## The Larger Struggle

Two courts rule the war underneath your story, and both want you.

The LIGHT THRONE: the human king and queen, the Church, the Guild, the
free cities of men, elves, dwarfs. The DARK THRONE: the elf-vampire
king and queen, orcs, undead, demons, vampires. Centuries ago the
dark court was the SOLAR THRONE, sole ruler of the realm, until its
pursuit of power invited something in. The pact they made cost them
their mortality, split the continent, and left the blighted zones as
the scars of the Fall. The history is there to be uncovered, and it
changes what the war means: the dark court's public creed is
restoration, its hidden motive is a Debt that keeps escalating, and
aligned players can discover the lie and choose to serve it or expose
it.

You can swear to either court. You can refuse both six times and walk
the neutral road, a mercenary fantasy with no protection and no
masters, until both courts decide a wildcard is a problem. Alignment
is not a dialogue option. It decides when you sleep, which roads are
safe, which courts will speak to you, and how the world ends.

## The War Plays Out Whether You Join or Not

The map is a live simulation, not a backdrop. 20-30 holds sit behind
vulnerability triggers that fire with or without you: a succession
crisis when a ruler dies, decimation when a garrison falls below
strength, legitimacy loss when a populace turns, and the siege event
when an army finally masses. Trigger a condition deliberately or
stumble into it by accident, and the same war moves either way. The
world does not care whether you meant it. You discover the rules
through play, in rumors, refugee columns, patrol shifts, and banners
changing on the horizon. No conquest is permanent: holds flip, flip
back, and flip again, and a procedurally generated nobility rises and
falls with every swing.

## Sieges and the Many Roads Into a Hold

Large-scale battles happen, and the siege is the loud end of a long
game. War camps appear on the roads, councils gather in taverns, and
you can join the assault on either side, break one, or lead it. But
open battle is only one tool. A hold can be turned in your court's
favor without a single ram touching the gate:

- Kill the ruler and open a succession crisis, on purpose or by
  accident.
- Bleed the garrison: destroy patrols, clear forts, drain the hold's
  strength quest by quest.
- Poison its legitimacy: smear the family, divert the famine relief,
  break the heir.
- Buy and sell the intel: tavern rumors are the war's currency, and
  a neutral player can sell to both sides.
- Intervene early instead of late: deliver supplies, warn the lord,
  destabilize cheaply before the escalation ladder ever reaches a
  siege.

Early-rung moves are cheap and deniable. Late-rung moves are dramatic
and loud. All of them move the same map. Aid a conquest decisively
and a grateful throne may grant you the hold: from nobody, to
landholder, to founder of a noble house that carries your name.

## The Promise

One character, one save, one continent that ends in a changed world,
not a credits roll. If one throne takes every hold, the game
continues under a vampiric sun or a cleansed sky, and you live in
whatever you helped build, or failed to stop. The world gives active
feedback at every step, remembers everything you do, and moves
whether you are watching or not. It does not judge you. It just
answers.

## Reference DNA

- Elder Scrolls II: Daggerfall - continent-scale map, factions, deep
  simulation of a lived-in world.
- Elder Scrolls III: Morrowind - skill-by-use leveling, you are bad
  at what you do not practice.
- Dark Souls (series) - lock-on, dodge roll, stamina discipline,
  deliberate combat pacing, weight and consequence.
- Mount & Blade-style living map energy - a war between thrones that
  moves borders while you play, experienced at street level.
- 1980s/1990s dark fantasy illustration - Frazetta, Bisley, early
  Warhammer, heavy inks and pulp energy.
- Modern atmospheric render tech - fog banks, god rays, volumetric
  night skies, weather that changes how the world reads.

## Repo Contents

- docs/planning/ - the full planning set (35 docs: vision, world
  design, combat, crafting, quests, factions, moral axis, territory
  conquest, lore spine, followers, controls, art style, art bible,
  art pipeline, vertical slice).
- docs/planning/24-art-bible.md - canonical concept-art catalog (36
  frames), locked mood register, per-biome palette law, generation
  grammar, QA checklist.
- docs/planning/25-art-pipeline.md - the art production pipeline (S1-S7
  sprite factory) and feasibility verdict.
- docs/planning/26-astrabot-analysis.md - Astrabot project digest, art-style x third-person-controls analysis, and gap audit (2026-09-13).
- docs/planning/28-controls-camera-gdd.md - PROPOSED controls and camera GDD (camera registers, billboard facing rules, roll direction, readability floor).
- docs/planning/29-art-style-bake-off-spike.md - RESOLVED: pivot to a true 3D world (low-poly pixelated models, PSX-style), locked painterly-pixel register unchanged, all concept art retained as canon reference. Contains the 3D pipeline validation plan.
- docs/planning/30-remote-ue5-pipeline.md - PROPOSED: how IO (on the VPS) builds UE5 assets and scenes in the editor running on Nicko's PC over Tailscale (Remote Control API / MCP), with the asset-to-scene-to-review loop and phased adoption plan.
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
quests, followers, moral axis, and territory conquest. Art register
locked with concept frames approved. Sprite production pipeline
piloted and proven end-to-end on one character (the gravedigger
undead), retained as reference after the 3D pivot.

## Note

All AI-generated art in this repo was produced for the Witch Hunter
project by CaptainPickard with IO (Hermes Agent) as the production
tooling. Planning docs are internal design material.