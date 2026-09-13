# 24 - ART BIBLE

Status: canonical catalog + generation grammar for Witch Hunter concept art.
Created 2026-09-12. Owner: IO. Mood register authority: doc 02 (LOCKED
section). Any new concept art MUST follow this document.

## 1. Purpose and Canonical Surfaces

- 02-art-style.md: the locked design law (mood register + sprite doctrine).
  This art bible operationalizes it: catalog, prompt grammar, workflow.
- 00-art-direction.html (art-direction/): the visual presentation page,
  self-contained (embedded fonts + data-URI images). Rebuilt after any
  catalog addition; sections: Character, Theme, Setting, Settlements,
  Situations, Day and Night, The Warp Camp, Presentation System.
- art-direction/concepts/: master frames (1024-1536px PNG). The masters.
- art-direction/concepts-web/: 960px q80 JPEG derivatives for the page.
- art-direction/reference/: Nicko's 9 external reference images (the
  approved register's DNA). Do not delete.
- art-direction/fonts/: UnifrakturCook-Bold (blackletter display), Cinzel
  (engraved capitals), EBGaramond (body). Subset woff2, OFL licensed.

## 2. The Locked Mood Register (mirror of doc 02, LOCKED 2026-09-12)

Nicko on the frame set: "These are exactly what im going for. You got the
concept right 100%."

- STYLE: painterly pixel-art hybrid illustration. Chunky visible brushwork,
  faceted shapes, never photoreal. Checkerboard dithering in gradients,
  film grain over everything. 16-bit/VGA soul.
- COMPOSITION: massive negative space, 60-80 percent of frame near-black
  or fog. Figure TINY (lower third or lower), dwarfed by colossal
  architecture or wilderness. Deep one-point perspective or natural
  framing (trees, arches, cliffs as vignette). Layered z-depth.
- LIGHT: low-key chiaroscuro. Backlit rim light on silhouettes. Small
  diegetic sources only (lanterns, torches, beacons, moon, hearths).
  Thick volumetric fog, atmospheric perspective. Light is scarce; every
  light is a location.
- PALETTE LAW: monochromatic cool base (deep indigo, Prussian blue,
  slate, charcoal, obsidian) with EXACTLY ONE accent per frame. No
  warm/cool salad. One warm note per panel.
- MOOD: quiet dread, solitude, awe. The frame is a held breath, not a
  shout. Not grimdark misery, not poster energy.
- DAY/NIGHT LAW: every place exists twice (24:1 clock, even halves).
  Day frames keep the same composition/camera as their night master.
  Day is NOT cheerful: honest gray-gold light at best, and the blight
  gets "wrong day" (ash haze, burned sun disc, red accent persists).
- CAMERA: third person, behind the subject. Never first person.
- HARD NEGATIVES: no text, no UI, no watermark, no cheerful pastel, no
  busy poster energy, no multiple warm accents.

## 3. Per-Biome Palette Table (the accent law, per place)

| Place | Base | Single accent |
|---|---|---|
| Darkwood | indigo/slate fog | amber lantern |
| Moors | midnight, violet heather | silver beacon (or small campfire ember) |
| Swamplands | teal/olive murk | drowned-dead green glow |
| Mountains | white/blue snow | torch gold |
| Farmland | warm dusk, olive-gold | hearth amber |
| Blight | ash gray / violet-black | blood-red (the danger itself) |
| Taverns | parchment, oak | amber windows/hearth |
| Warp camp (good) | white/gold canvas, dawn slate | hearth amber |
| Warp camp (neutral) | iron gray, moss | teal glass lanterns |
| Warp camp (dark) | obsidian, ash | blood-red + forge ember |
| Magic/VFX (reserved) | n/a | electric cyan |

Accent ownership rule (open ruling, from page NOTES): cyan belongs to
magic; amber to human fire; red to the pact/danger; teal to the neutral
court. Combat VFX must not steal a biome's accent.

## 4. Generation Grammar (the reusable prompt template)

Model used for the blessed set: gpt-image-2-high (image_generate tool),
quality high. Establishing shots: portrait 1024x1536. Scene/action/
camps: landscape 1536x1024. Character feature: portrait.

Slot template - fill every slot, never drop a block:

  [STYLE] "Retro 1980s-1990s dark fantasy video game concept art,
  painterly pixel-art hybrid illustration with checkerboard dithering
  and film grain, [VGA-era | 16-bit era] palette."
  [SUBJECT+CAMERA] "Third-person view from behind a lone [who], [tiny
  scale | small | mid-scale], [position in frame], [facing what]."
  [SCALE] "Dwarfed by [colossal thing]. Massive negative space, [60-80]
  percent of the frame in near-black or fog."
  [LIGHT] "Low-key chiaroscuro, backlit rim light on the silhouette,
  small diegetic light sources only, thick volumetric fog, atmospheric
  perspective."
  [PALETTE] "Palette: [per-biome base] with [one accent] as the single
  warm/accent note."
  [MOOD] "Quiet dread, solitude, awe. The frame is a held breath."
  [NEGATIVES] "No text, no UI, no watermark."

Day-variant conversion block (applied to an existing night master via
image-to-image, keeps composition exact):

  "Convert this night scene to daytime while keeping the exact same
  composition, camera, poses, and painterly pixel-art hybrid style with
  checkerboard dithering and film grain. [Day description per biome].
  The figure/campfire/lantern stays [same position, lantern now dark /
  fire now smoke thread]. Palette shifts from [night base] to [day
  base], keeping painterly texture, atmospheric depth, and the mood.
  No text, no UI, no watermark."

Day rules: day is honest but never cheery in the wilds (gray-gold,
overcast, hard shadows); the blight's day is WRONG day (ashen sky,
burned sun disc, red accent persists); candles become smoke threads;
lanterns go dark. Night is the default register; day frames are always
derived from an approved night master, never invented fresh.

Camp grammar: fixed skeleton (full station set: forge, alchemy,
enchanting, workbench, kitchen; defenses; merchant+cook; retinue tents;
decoration track) + affinity modifiers: good = banners displayed,
warm hearth, chapel shrine, neat rows; neutral = no banners displayed
(standard furled/cased), teal glass lanterns, hidden den entrance,
low-profile defenses, trophies as warnings; dark = banners flying
(broken sun), blood-red altar light, undead watch, chain-topped stakes,
trophies as threats.

## 5. Frame Catalog (23 frames, all Nicko-approved)

NIGHT MASTERS (concepts/concept-*.png):
1. concept-01-darkwood.png - Darkwood clearing at night; colossal
   twisted trees; amber lantern. APPROVED.
2. concept-02-moors.png - moors night; ruined watchtower; huge moon;
   cold beacon window; campfire ember. APPROVED (near-perfect register
   match; strongest dithering).
3. concept-03-blight.png - blighted wastes; spire in ash fog; eclipsed
   sun monoliths; red glow at base. APPROVED.
4. concept-04-tavern.png - timber-and-thatch tavern at dusk; stag skull
   above door. APPROVED with noted deviation (reads warmer/denser than
   target; candidate for one cooling pass).
5. concept-05-night-ambush.png - moor-road night ambush; hunter mid
   dodge-roll vs two dire wolves. APPROVED.
6. concept-06-siege-council.png - torch-lit war council in a ruined
   gothic courtyard; hunter apart from the circle. APPROVED
   (near-perfect).
7. concept-07-camp-mourning.png - mourning ring; fourteen cairns;
   kneeling hunter; candle glow. APPROVED (candles read as one diffuse
   warm mass rather than many points).
8. concept-08-veil-spire.png - colossal establishing shot; Debt's Echo
   statue rows; crimson rim. APPROVED with noted deviation (palette
   skews warm charcoal-red; candidate for a cooler pass).
9. concept-09-tavern-hearth.png - tavern hearth interior; save-point;
   patrons as silhouettes. APPROVED.
10. concept-10-hunter-figure.png - character presentation; hunter from
    behind on a fog-wrapped pass; lantern lit. APPROVED.

DAY PAIRS (concepts/day-*.png, generated FROM each night master,
composition-locked):
11. day-01-darkwood.png - day as the Darkwood allows: pale shafts,
    moss-light, lantern dark.
12. day-02-moors.png - honest daylight; tower in weathered stone;
    fire now smoke thread.
13. day-03-blight.png - WRONG day: burned sun disc; red persists.
14. day-04-tavern.png - visible safety; the only truly warm daylight.
15. day-05-ambush.png - same poses; wolves hunt at noon too.
16. day-06-council.png - cressets unlit; banners vivid.
17. day-07-mourning.png - smoke threads replace flames.
18. day-08-veil-spire.png - gray noon; scale reads sharper.
19. day-09-hearth.png - embers banking; dust in window light.
20. day-10-hunter.png - resolve in honest light; lantern dark.

WARP CAMPS (concepts/camp-*.png):
21. camp-good-affinity.png - farmland ridge dawn; white-and-gold; sun
    stag banner; chapel shrine; warmth earned.
22. camp-neutral-affinity.png - dusk hollow; iron/teal; NO banners;
    teal glass lanterns; toll-ring den entrance; deniability.
23. camp-dark-affinity.png - night deadwood; spired black pavilions;
    broken-sun banners; blood-red altar; undead watch.

CHARACTER FRAMES (concepts/char-*.png), generated 2026-09-13, all
third-person behind-figure, register checked via gemma4:31b QA:
24. char-01-handmaiden.png - light-court princess's servant, candle in
    a night corridor. APPROVED (two warm sources noted: candle + sconce;
    acceptable as diegetic, candidate for tightening).
25. char-02-thrall.png - orc-work-camp slave, iron collar, ore basket.
    APPROVED (runs warmer/denser than tiny-figure frames).
26. char-03-bannerman-good.png - light bannerman, gold stag banner,
    castle wall, enemy campfires below. APPROVED (multiple warm points:
    lantern + torches + city lights; candidate pass).
27. char-04-bannerman-dark.png - dark bannerman, broken-sun banner,
    red brazier. APPROVED (dither subtle).
28. char-05-bard-good.png - light-affinity bard, tavern bench, lute,
    warm hearth pool. APPROVED.
29. char-06-bard-dark.png - dark-affinity bard, black lute, veiled
    courtiers, red cresset. APPROVED.
30. char-07-gravedigger-undead.png - PC undead gravedigger, empty open
    grave, corpse-green lantern. APPROVED.
31. char-08-noble-knight.png - PC good knight kneeling in chapel
    vigil, votives, moon shaft. APPROVED.
32. char-09-coven-wizard.png - PC neutral hedge-witch at standing
    stones, cyan staff-wisp. APPROVED (strongest hybrid dither of the
    set).

SCENE FRAMES (concepts/scene-*.png), 2026-09-13:
33. scene-01-bard-skeleton.png - skeleton bard in ossuary, spectral
    green candles. APPROVED (denser than register target).
34. scene-02-swamp-ghouls.png - drowned-dead rising from black marsh,
    hunter on tussock, grave-green accent. APPROVED.
35. scene-03-dragon-windup.png - knight carrying princess down a
    causeway, colossal dragon winding up furnace breath against the
    full moon. APPROVED (action register; side camera).
36. scene-04-toll-bridge.png - Shadow Court toll-keeper collecting
    passage on a moonlit gorge bridge, red brazier. APPROVED
    (near-perfect register match).

PRODUCTION CARDS (docs/planning/26 queue; sprite assets in
art-direction/sprites/<card>/):
37. sprites/orc-male/concept.png - CARD 01 S1: Mordor-register orc male
    at a smoldering war-camp; recomposed once to register (v1 archived
    in _qa/). APPROVED.
38. sprites/orc-male/turnaround.png - CARD 01 S2: 4-view turnaround,
    first-round PASS (weapon-removal instruction per L1). APPROVED.
    8 directions + 5-frame idle built (S3/S4); flicker 18.6-26.7
    (best of three characters; rigid mass animates clean). Weapon
    deliberately not baked: separate layer per doc 27.
39. sprites/orc-female/concept.png - CARD 02 S1: Mordor-register orc
    female, war-earned trophy rank, ember war-camp horizon; v1 archived
    in _qa/ (held a sword; regenerated with explicit empty hands).
    APPROVED.
40. sprites/orc-female/turnaround.png - CARD 02 S2: 4-view turnaround,
    first-round PASS (empty-hand instruction per L1+L2 held). APPROVED.
    8 directions + 5-frame idle built (S3/S4); flicker 8.3-19.0, best
    of the run so far. Weapon not baked: separate layer per doc 27.

Page captions for every frame live in 00-art-direction.html and are the
canonical short descriptions; the pair descriptions there tie each pair
to the clock mechanics.

## 6. Rebuild Procedures

- Web derivatives: concepts/*.png -> 960px wide, q80 JPEG, into
  concepts-web/ (PIL LANCZOS).
- Page build: single self-contained HTML; ALL images embedded as data
  URIs (WebUI serves single files; sibling-folder img src WILL break);
  fonts embedded as subset woff2 data URIs (subset to ASCII 0x20-0x7E
  via fonttools); gothic chrome: UnifrakturCook display + Cinzel
  headers/labels + EBGaramond body; engraved dark-iron "cathedral"
  panels (double rule lines, gold #C9A227 on #08090D, film-grain
  overlay). Pure ASCII text only, no unicode punctuation.
- Adding a frame: generate per grammar (section 4) -> vision QA
  (section 7) -> save master to concepts/ (name: concept-NN-slug or
  day-NN-slug or camp-slug) -> web derivative -> add panel + caption to
  the matching page section -> catalog entry here (append number).
- Vision QA tooling: auxiliary.vision = gemma4:31b via ollama cloud
  (config patched 2026-09-12; minicpm-v is dead there). Ask the model
  to check the frame against the register and list deviations.

## 7. New-Frame QA Checklist

1. Negative space 60-80 percent near-black/fog (day frames may run
   lighter but must stay low-key).
2. Figure tiny, lower third, dwarfed.
3. Exactly one accent; check no second warm source crept in.
4. Dither/grain visibly present (zoom to verify).
5. Rim light on the silhouette; diegetic sources only.
6. No text/UI/watermark; no photorealism; no pastel.
7. Mood reads as held breath, not poster.
8. Blight/spire frames: red accent present even in day variants.
9. Register deviation verdict recorded with the catalog entry.

## 8. Open Rulings Carried (from page NOTES + doc 02 PROPOSED)

- 360-rotation doctrine PROPOSED: 8 directional views standard, 16 for
  hero-tier/bosses? Frame budget ruling needed.
- Dithering: post-process shader over the 3D world, painted into
  sprites, or both.
- One-accent law vs combat VFX color collisions.
- Fog depth vs sprite silhouette readability floor (test at gameplay
  distance, 512-1024px frames).
- Portrait frames for dialogue: sprite-scale or illustration crops.
- Mourning ring: set dressing or mechanically keyed camp mood.
- concept-04 and concept-08 cooling passes (section 5 notes) - pending
  Nicko's "keep going" call.