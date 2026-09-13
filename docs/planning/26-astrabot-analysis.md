# 26-A (file 28) - ASTRABOT ANALYSIS: Project Digest, Art-Style x Controls, Gap Audit

Date: 2026-09-13. Author: Astrabot subagent (read-only pass over the full repo).
Scope: every doc in docs/planning/ (00-27), README.md, tools/README.md,
art-direction/00-art-direction.html (structure), art-direction/sprites/
(pilot + 9 race cards). Grounded citations use doc filenames throughout.

---

# PART 1 - PROJECT DIGEST

## What the game is

Witch Hunter is a single-player, third-person, open-world dark fantasy action
RPG: "a more stylized, but pixelated version of Elden Ring" (README.md,
01-vision-high-concept.md). The presentation bet is the identity: a true-3D
world (dynamic lighting, fog, volumetrics, weather in Unreal) inhabited
entirely by 2D painted billboard sprites with 360-degree directional rotation
(02-art-style.md). The DNA stack is explicit: Daggerfall's scope and
structure, Dark Souls' combat feel (lock-on, dodge roll, stamina, camera
follow), Morrowind's skill-by-use progression, wrapped in a modern mood
engine (01).

The frame narrative: one hunter on a continent locked in a war between two
supernatural courts - a human light court (king and queen) and an
elf-vampire dark court - plus an outlawed neutral Shadow Court. The player
aids one court to total domination, or refuses both six times (the
Allegiance Gambit) and forges the Third Path by re-kindling the Deep Altar
(01, 12-moral-axis-factions.md, 19-fall-of-the-veil-throne.md).

## Core systems (all specced in docs/planning/)

- **World** (03-world-design.md): hand-authored overworld ~10 x 13 km
  (~130 km2), ~25 holds, 6 biomes, procedural persistent dungeon interiors,
  4 Great Cities (Veil Spire, Orc City, Underground Dwarf City, New
  Capital), 3 blight scars, 3 altars all in dark-held ground, NO fast
  travel at all, 24:1 clock with even day/night halves, Veil-Tide weather
  front system with named storms (Red Vigil / Pale Tide / Storm-Calls).
- **Combat** (04-combat-system.md): Souls grammar - lock-on, dodge roll,
  block/parry, stamina, plus a locked poise/stagger universal resource,
  parry windows by source, equip-load roll bands, dual-mode aiming
  (stationary reticle vs moving lock-on), 9 weapon lines with all 36
  tier-up technique menus LOCKED (108 techniques), enemy grammar rule
  ("enemies use the player's verbs"), court forces as magic schools made
  hostile.
- **Progression** (07, 15, 16, 18): 9 stats, 5 points/level; 28 core skill
  lines ranked 1-100 by use, 5 tiers, permanent technique choices, no
  decay, no respec; lapable specialty titles; level number is a point
  budget, not a damage stat.
- **Magic** (17-magic-system.md): 5 schools, 48 spells + 6 hybrids + 2
  corruption kits, tome-based acquisition, taint meter, axis-gated
  Holy/Dark, Aegis rule. LOCKED.
- **Economy/survival** (05, 06, 09, 10, 11): floor/ceiling crafting quality
  model, 5 station tiers + 1 legendary dungeon station found only via clue
  chains, New World-style ingredient slots, four-layer loot tables with a
  Rarity-vs-Tier crossing rule, weight-based inventory, tavern saves +
  camping + warp camp home base (3 tiers), no estus flask, one meal + one
  prep potion per day.
- **Politics/simulation** (12, 13, 14, 20-22): moral axis as faction gate,
  trigger-driven conquest with regicide-with-heirs, procedural nobility
  with six-state house lifecycles, two-tier quest architecture
  (hand-authored spine vs ~90% procedural tissue reacting to a World
  Ledger), 8 tissue frame templates, transformation lines (vampire /
  undead / werewolf four-ability kits), siege triggers tied to comeback
  events (demon invasion = debt default).
- **Followers** (23-expedition-followers.md): 4 types (Bard / Squire /
  Guard / Arcanist), level-gated slots 1-4, follower XP and permadeath
  with camp mourning.
- **Lore spine** (19-fall-of-the-veil-throne.md): the Fall of the Solar
  Throne, the debt/Undertow (dark court "out of credits"), the
  Undersovran (contracts and sigils only, never a body), the Third Altar
  true ending, Schism Sects, Reliquary Wardens, the Tight Nine witnesses.

## Art state (the most built-out area)

- Art register LOCKED (02 + 24-art-bible.md): painterly pixel-art hybrid,
  dithered gradients, film grain, 60-80% near-black negative space, tiny
  figures, low-key chiaroscuro, rim light, diegetic light only,
  monochromatic cool base with exactly one accent per frame, third-person
  camera. Per-biome palette table with accent-ownership rules.
- 36 approved concept frames (night masters + day pairs + camps + 9
  character frames + 4 scenes), QA'd via gemma4:31b vision checks
  (24-art-bible.md section 5).
- Production pipeline PROVEN end-to-end (25-art-pipeline.md): S1-S7
  factory (design sheet -> turnaround -> 8 directional views -> frame
  stacks -> chroma-key cleanup -> QA gate -> atlas + billboard). Pilot:
  gravedigger undead; then 9 of 10 race-card bodies complete
  (26-sprite-production-queue.md) with standing lessons L0-L8 (hand-pose
  drift, hem anchoring, weapon-consistency rules, cloth flicker).
- Equipment: layered paper-doll system LOCKED (27-equipment-visual-
  system.md) - body canon + per-piece layer atlases on the same frame
  grid, palette-swap variants, anchor contract, combat-silhouette
  readability rule.

## Current state of the design

Pre-production with an unusually deep design lock: decisions 1-62+ in
00-README-index.md record that world GDD, combat, crafting, loot, quests,
factions, transformations, followers, and the art pipeline have all had
dedicated lock sessions with the project owner (Nicko) between 2026-09-11
and 2026-09-13. The 08-open-questions.md tracker claims "no holes or gaps"
with every open item assigned to a future pass. The claims below in Part 3
identify what that tracker itself does not see.

What exists as artifacts: 36 concept frames, 10 character sprite bodies
(9 done + card 10 dwarf female pending), cleanup/QA/atlas tooling
(tools/), two live billboard test pages. What does not exist: any engine
validation, any combat animation, any playable prototype, any controls
spec, any audio direction, and any vertical-slice scope.

---

# PART 2 - ART STYLE x THIRD-PERSON CONTROLS ANALYSIS

**First, the stated fact: the docs propose combat controls only at the
verb level, and never specify the camera.** 04-combat-system.md locks
lock-on, dodge roll (i-frames, "roll direction = camera or lock-on
relative"), block/parry, dual-mode aiming (stationary over-shoulder
reticle vs moving lock-on), stamina/poise rules, and soft-target
switching. 00-README-index.md pillar 2 names "camera follow" as a
feel-defining verb. 24-art-bible.md locks "CAMERA: third person, behind
the subject. Never first person." That is the entire controls
specification. There is no doc for camera distance, camera collision,
lock-on camera behavior, aiming zoom, sensitivity, or input mapping. The
analysis below therefore checks the locked verb set and the locked art
register against standard modern third-person action conventions (Souls/
Elden Ring style), which is what the docs themselves invoke as the target
("Combat should feel like Dark Souls" - 04).

The art register is treated as LAW throughout: 02 and 24 state the mood
register is locked and "any new concept art MUST follow this document."
So the analysis asks: where does the locked look fight the locked verbs?

## Tension 1 - The orbiting camera vs the 8-view directional sprite

Modern third-person combat lives on a free-orbit camera that swings 180+
degrees during a single fight (lock-on reframes constantly, manual aim
sweeps, dodge rolls re-center). Every camera swing re-selects the sprite's
directional view. 02's tech pillar 7 requires "no visible popping between
adjacent views at gameplay camera distances" - but with 8 views, adjacent
views are 45 degrees apart, and a fast camera sweep will cross 2-3 view
boundaries inside one attack. The pilot (26 queue) proves idle-stacks at
slow orbit only; nothing tests view-popping under combat-rate camera
motion. 4-6 frame animations make it worse: frame N in view A is never
motion-matched to frame N in view B, so a mid-attack camera swing shows a
visual discontinuity in BOTH time and angle simultaneously.

**Solution pattern (grounded):** take 02's own escalation seriously -
16 views for the PLAYER and hero-tier enemies as the baseline, not "if
budget allows"; reserve 8 views for ambient props and distant NPCs only.
Lock a camera-rate rule: during lock-on, cap camera angular velocity so
view changes land on attack-beat boundaries (hide reselection inside hit-
stop, which 04's poise system already generates). The atlas format
(02 pillar 7 directional atlas) supports this with zero engine change.

## Tension 2 - 4-6 frame animations vs Souls readability contracts

04 locks "big wind-ups, committed recovery" and admits the core problem:
"Sprite animation frames must sell weight... because there is no 3D
skeleton to lean on for anticipation." A Souls wind-up telegraph lives in
the pose change across 10-20 frames of a 3D rig; in 4-6 painted frames the
anticipation frame must be a deliberately exaggerated illustration. The
locked parry system sharpens this: parry windows are timed off attack
animations (04: "a short active window at the start of block input," only
readable if the attacker's wind-up is legible), and 04's own Guardian's
Read technique ("enemy attack telegraphs stay visible longer... a
readability perk that fits sprite combat") concedes the base readability
is marginal. Enemy grammar raises the stakes: "readability is the fairness
contract" (04) - every enemy verb must be readable in the same 4-6 frame
budget, multiplied by 8 directions.

**Solution pattern (grounded):** make the frame budget per-pose, not
global - 02 locks 4-8 frames/animation; spend 8 on attack wind-ups and
staggers (the fairness-critical poses) and 4 on idle/walk. Author a
TELEGRAPH FRAME as a mandatory named frame in every attack stack (the
one-accent law helps: 24 reserves electric cyan for magic and blood-red
for threat - a winding-up enemy can flash the threat accent at the
telegraph frame, which is diegetic and register-legal). QA gate it:
extend tools/qa_gate.py with a "telegraph frame distinctiveness" check
alongside the existing flicker and silhouette checks.

## Tension 3 - Tiny figures in 60-80% near-black vs combat target visibility

The register mandates 60-80% near-black or fog per frame (02, 24), tiny
figures in the lower third, diegetic light only, and thick volumetric fog.
24 section 8 already flags the collision as an open ruling: "Fog depth vs
sprite silhouette readability floor (test at gameplay distance)." Combat
makes it acute: 03 locks night as THE dangerous half for good players,
with undead and ambush packs; 03's Veil-Tide Pale Tide lifts fog and "wakes
wild strains." Fighting 4 ghouls in Pale Tide fog at night, at gameplay
camera distance, with 512-1024px sprites and monochromatic-cool palettes
is the worst case, and the enemy-grammar fairness contract assumes you can
see every verb. 27 section 4 adds a second collision: equipment layers
change silhouette by design (fashion), which can silently break enemy
readability ("is that soldier the parry-type?") that 04 keys off gear.

**Solution pattern (grounded):** promote 24's open ruling to a locked
COMBAT READABILITY FLOOR with numbers: silhouette contrast target at
fixed gameplay distances, tested with qa_gate.py's existing 25% silhouette
check, under night + Pale Tide lighting. Use the register's own tools as
the solution: rim light is already law (24) - make rim light on all
hostile sprites slightly stronger than on scenery (still diegetic: the
player's lantern, the moon); use accent-ownership (24 section 3: red = the
pact/danger) so hostile entities carry the frame's danger accent; keep
fog depth keyed off encounter density (fog recedes inside locked-on
combat, thickens in exploration - the fog is the mood, combat buys
clarity). 27's silhouette rule should add a QA check: each equipment
variant must preserve the piece-type silhouette markers (helm/shield/
weapon shape) that the enemy-grammar read depends on.

## Tension 4 - Camera framing: the concept register pulls the camera BACK, combat pushes it IN

Every approved concept frame composes the hunter tiny and distant
(24 section 5 catalog; scene-03-dragon is explicitly "action register;
side camera" and is the exception). But the locked verb set needs close
framing: stationary aiming is "an over-shoulder reticle" (04), lock-on
melee needs the player sprite and 1-3 enemy sprites simultaneously
legible, and stagger/punish windows are sub-second. A tiny-figure framing
at souls combat distance makes a 512px sprite occupy very few screen
pixels; 02's "crisp filtering, not nearest-neighbor" scaling decision was
made for this, but no doc specifies the actual combat camera distance,
and 24 section 8's "portrait frames for dialogue: sprite-scale or
illustration crops" shows the close-up question is unresolved even for
dialogue.

**Solution pattern (grounded):** define three camera registers as
explicit law (exploration = the concept-frame framing, tiny figure,
colossal world; combat = tightened lock-on framing where the player
sprite reads at 15-25% of frame height; aim mode = over-shoulder per
04) and make the 512-1024px locked resolution a function of the COMBAT
register (the tightest read), not the exploration register. The scene-03
side-camera note is the precedent: action framing in this game is
allowed to break the tiny-figure composition - write that down as a
combat-camera rule instead of an exception.

## Tension 5 - Roll directions, blocking arcs, and facing on a camera-relative billboard

04 locks "roll direction = camera or lock-on relative," Firm Stance covers
"a wider facing arc," Wall of Steel and Phalanx Footwork are facing-based,
Polearm's Master of the Line punishes enemies circling behind you, and
enemy soldiers use the same grammar. All of this needs a well-defined
WORLD-space facing for every billboard. But a billboard's rendered image
is chosen from the CAMERA's angle (02: "angle from camera to sprite ->
nearest directional view") - the rendered facing is camera-relative, while
the combat logic needs the character's world-facing (where they last
moved/attacked/blocked). The docs never reconcile these. A blocking arc
computed off the rendered view would be wrong the moment the camera
orbits; computed off an invisible world-facing, it can contradict what
the player sees (the sprite appears to block "backwards" after a camera
swing). Same issue for dodge i-frames: 4-frame rolls at 8 directions
quantize a 360-degree dodge input into 8 buckets, and Slip the Blade
("attack passing through your i-frames") demands precise timing and
direction readability.

**Solution pattern (grounded):** adopt the standard retro-3D rule
explicitly: logical facing = last input/attack direction (world-space,
continuous); rendered view = nearest directional view of that facing;
combat arcs (block, parry, Wall of Steel) resolve against logical facing,
and the game never renders a block animation in a view that contradicts
it (snap the directional view of defensive poses to the logical facing,
even mid-camera-swing - a 45-degree snap reads as intent in a block, as a
glitch in an idle). For rolls, either raise the player's directional
views to 16 (02 already contemplates this for hero-tier - the player IS
hero-tier) or quantize roll input to 8 directions deliberately (a
Daggerfall-honest choice that must be a stated design decision, not an
accident).

## Tension 6 - Hit feedback, hit-stop, and stagger on flipbook sprites

04's poise system is the feel core: chip poise, break, "stagger = a
committed recovery animation, the souls punish-window." In 3D games much
of hit feedback is procedural (skeletal hit-react blending, particle
impacts, camera shake). In a flipbook world, every hit reaction is
authored frames x 8 directions per body type, and 02's budget framing
(32-48 illustrations per animation for key characters) already prices ONE
animation; a full combat set (idle, walk, run, light, heavy x N, block,
parry, hit-react, stagger, death, roll x 8) is roughly 10-15 poses, i.e.
300-700 illustrations per key character. 26's queue prices bodies
(turnaround + idle only). The cost model for COMBAT animation stacks -
the thing the whole game rests on - is unbuilt, and cloth-heavy bodies
already flicker unacceptably at idle (26 lessons L4; elf-female flicker
23.1-46.5).

**Solution pattern (grounded):** (a) mirror 27's paper-doll economics:
hit reactions and staggers can share frames across the pose set with
palette/tint variation; (b) lean on the engine for feedback the sprites
can't carry - 02 pillars 3-4 (light-tint/rim-glow materials, fog
integration) plus hit-stop, contact-flash on the impact accent, and
camera shake are register-legal because they are diegetic light, not
particle realism (24 hard-negatives ban "modern particle realism" for
spell VFX - keep impacts in the same law); (c) solve cloth flicker with
26's own L3/L4 lessons extended to combat: combat frames derive
image-to-image from one source view, and cloth-heavy bodies get
silhouette-stabilized combat poses.

## Tension 7 - What the register gives combat for free (the positive case)

Grounded reasons the style can work WITH the controls rather than against
them: (1) silhouettes - the rim-light/black-negative-space law produces
exactly the high-contrast character silhouettes that 27 section 4 says
carry enemy-grammar readability; (2) the one-accent law gives combat a
built-in threat/color language (cyan magic, red danger, amber human fire
- 24 section 3) that modern games spend shaders on; (3) "fewer frames,
high impact, each frame is a full illustration" (02) is precisely the
weight-over-fluidity trade Souls combat makes anyway; (4) faction
soldiers "fight like the player does" (04) so a single sprite grammar
covers both sides; (5) the day/night law ("every place exists twice,"
24) already designed both lighting modes of every scene, which is the
hard part of affinity-relative ambush readability.

## Bottom line

The locked art style and the locked combat verbs are compatible, but only
if four unspecified things get specified: camera registers and rates
(Tension 1/4), facing rules for combat arcs on billboards (Tension 5),
per-pose frame budgets with mandatory telegraph frames (Tension 2/6), and
a numeric readability floor for night/fog combat (Tension 3). None of
these currently has a home in any doc.

---

# PART 3 - GAP AUDIT

Severity: HIGH = blocks the core promise or hides an unproven bet the
whole project rests on; MED = needed before vertical-slice/GDD lock;
LOW = polish or later-pass.

## HIGH severity

1. **No controls/camera specification exists anywhere.** What's missing:
   camera distance/registers, lock-on camera behavior, manual-aim zoom,
   input mapping, facing rules for billboard combat arcs (Part 2,
   Tensions 1, 4, 5), sprite view-selection vs combat logic. Why it
   matters: 04 locks a fairness contract ("readability is the fairness
   contract") that is undeliverable without these rules; every other GDD
   assumes them. 08-open-questions.md tracks it nowhere. (Docs: 04, 02,
   24, 08.)
2. **The player character has no body canon.** What's missing: doc 26's
   10-card queue covers orc/undead/vampire/elf/dwarf x male/female -
   there is no HUMAN male/female card, yet 03 locks a human-centric
   character creation ("no fantasy race selection") and the player's
   own sprite is "the most viewed asset in the game" (27 section 4).
   Why it matters: the equipment/paper-doll system (27) is built on
   body canon that doesn't exist for the one body every player sees.
3. **No combat animation exists or is costed.** What's missing: all S4
   frame stacks beyond idle (attacks, rolls, hit-reacts, staggers,
   deaths); a production cost model for the full combat pose set x 8
   directions x per-body; a flicker verdict on fast-motion frames (26's
   L4 flags cloth at IDLE). Why it matters: it is the project's largest
   unproven art bet - 02's "production bet of the whole art pipeline"
   was priced on idle stacks only. (Docs: 02, 25, 26.)
4. **Zero engine validation.** What's missing: the UE5 spike is queued
   but not run (26: "Then: the UE5 spike"); Unreal version still TBD
   (00, 08); tech pillars 1-7 (02) - contact shadows, animation-state
   driving, light-tint materials, fog integration, instancing for
   "hundreds of animated billboard sprites in towns," directional
   selection, heraldry-on-flag flow - are unvalidated. Layered
   paper-doll runtime (27) multiplies quads 3-8x per character and is
   likewise untested in-engine. Why it matters: every art decision so
   far was proven in a browser page, not the target engine; the
   billboard-in-Unreal risk is the project's largest technical unknown.
5. **8-vs-16 directional ruling still open.** What's missing: the frame
   budget ruling flagged in 02, 24 section 8, and 25 (caveat 3). Why it
   matters: it doubles or halves the entire sprite budget and is a
   prerequisite for gap 3's cost model; it has been open since 2026-09-12
   across three docs.
6. **No vertical-slice scope.** What's missing: 01's open question
   ("Rough target scope for the first vertical slice (one biome, one
   dungeon chain, one faction)?") is unresolved and unassigned in 08.
   Why it matters: the design surface (130 km2, 25 holds, 28 skill
   lines, 3 courts, conquest sim) is far beyond any team's first
   buildable proof; without a slice definition, nothing forces the
   prioritization the locked docs avoid making.

## MED severity

7. **Facing/parry/block arc spec for billboards** (Part 2, Tension 5) -
   logical-facing rule, defensive-pose view snapping, roll-direction
   quantization. Undeliverable fairness contract without it. (04, 02.)
8. **Combat readability floor unruled.** 24 section 8's "fog depth vs
   sprite silhouette readability floor" open ruling needs numbers and a
   night/fog test protocol; interacts with 03's Pale Tide and night-
   anchored undead. (24, 03, 04.)
9. **One-accent law vs combat VFX unresolved.** 24 section 8 flags it;
   04's combat is dense with concurrent effects (zones, wards, bleed,
   corruption kits, throwables - docs 04/17/05). Accent-ownership
   exists (24 section 3) but no rule ranks collisions mid-fight.
10. **Boss/colossal-sprite treatment unspecified.** The register's
    signature image is colossal scale (24), and 04's signature tier is
    "boss-scale abominations," but no doc covers giant-sprite framing,
    multi-part boss sprites, camera behavior vs a 10-meter billboard, or
    whether bosses get 16-view sets. scene-03 is a lone concept note.
11. **Sound and music direction: no doc at all** (02, 08). For a game
    whose mood law is "the frame is a held breath," audio is half the
    register and has zero coverage.
12. **Dithering ruling open** (post-process shader vs painted vs both -
    24 section 8): affects every sprite, the world shader budget, and
    the readability floor.
13. **Transformation-strain sprite plan missing.** 22 locks one human
    becoming vampire/undead/werewolf; the wolf's Hunter's Sprint is a
    quadruped travel form (21). Each strain needs its own directional
    body set + equipment-layer compatibility (does gear transfer?) -
    unaddressed in 22, 26, or 27.
14. **Runtime performance budget never quantified.** 02 pillar 5 says
    "hundreds of animated billboard sprites" without frame budget; add
    follower parties (23), retinue (11), siege events (13/22), and
    layer stacks (27). No perf target exists to validate against.
15. **Named-character consistency cost unproven.** 25 section 5 and 26
    L5 say named characters need per-character adapter training (LoRA):
    no costing, no tooling, no fallback if adapter training underperforms
    on this register. All 9 completed cards are rank-and-file bodies.
16. **Human approval throughput is a single-threaded bottleneck.** 25
    caveat 2 makes Nicko's human gates load-bearing at two points per
    character card; the production plan for hundreds of NPCs + thousands
    of equipment pieces (27 section 4: ~20 slots x ~10 variants) has no
    throughput model.
17. **UI art direction is one line.** 02 locks "modern Souls-style -
    clean menus, diegetic touches where cheap"; the banner-creation UI
    (02, 11), World Ledger readouts (20), map-reads-like-weather
    (13), and diegetic-only debt reading (20) all need a UI/UX doc that
    doesn't exist.
18. **Mount visual system unspecified.** 02/03 lock "sprite mounts,
    travel speed only" - mounted player sprite composition (rider +
    mount as stacked layers? baked pairs?), mounting/dis Mount frames,
    and 04's Dismount interaction have no spec.
19. **Hold defense mechanics and specialty catalog completion remain
    open with no session assigned** (08: "Hold defense mechanics...
    neutral-court war profiteering arc"; "Specialty catalog completion +
    apex chains"). Both feed locked systems (13 sieges, 16 apex gates).
20. **Cutscene format beyond dialogue/portraits unresolved** (02, 08) -
    the spine's big beats (the Embrace, the Rising, the Sixth Denial)
    will need more than portrait panels, per 20-22's own stage beats.

## LOW severity

21. **Rembg replacement** for alpha extraction (tools/README.md: the
    model download killed the pilot host; chroma-key works but is
    lighting-fragile for outdoor concept-derived sprites).
22. **concept-04 / concept-08 cooling passes** pending a keep-going call
    (24 section 8).
23. **Working-title IP collision** ("Witch Hunter" - 01 open question;
    genre crowd, likely trademark crowding).
24. **Romance buff mechanics, bard type list, follower XP share** -
    tracked as tuning (08, 23); fine to leave, listed for completeness.
25. **Mourning-ring ruling** (set dressing vs mechanical camp mood - 24
    section 8) and other small art-bible open rulings.
26. **Player-authored heraldry flowing to map markers/tabards** - flagged
    for tech plan (02 pillar 6) with no owner or tooling sketch.
27. **Fast-travel-removal downstream checks** (08 lists camping balance,
    retinue errand ranges as "new dependent opens") - assigned but
    worth watching: no-fast-travel is the kind of lock that quietly
    breaks quest-timer tuning done later.

## Pattern worth naming

08's tracker is disciplined ("nothing here is unresolved DESIGN;
everything open is assigned") and, within its own frame, true: the
SYSTEMS are nearly hole-free. Every HIGH gap above is either (a) the
presentation/controls layer, which no planning session has yet owned
(there is no "combat feel / camera" doc the way there is a crafting
doc), or (b) the production-cost layer of the art bet, which 25 priced
on a one-character pilot. The next three planning sessions that would
close the most risk per session: (1) a CONTROLS & CAMERA GDD (closes
gaps 1, 7, 8, partially 10), (2) the UE5 spike + one combat animation
stack prove-or-kill artifact, extending the pilot pattern (closes 3, 4,
5, 14), (3) a production-plan pass for the full cast cost (closes 15,
16, 2).