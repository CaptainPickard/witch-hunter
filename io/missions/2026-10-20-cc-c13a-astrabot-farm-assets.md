# CC-C13a · ASTRABOT ASSET BRIEF - Old King's Forest area dressing (farm, ruins, trees, fences/gates)

Nicko ruling 2026-10-20: design new assets for the Forest of the Old King
(region C) area: (1) a SMALL FARM where the first quest giver will live,
(2) replace the random upscaled wood fences and the random gates of
different sizes with authored pieces, (3) MORE STONE-RUIN-LIKE STRUCTURES,
(4) TREES per the game concept art. You DESIGN + GENERATE + BAKE assets.
You do NOT wire the game (CC-C13b / Claude Code lane does that).

## 0. LAWS (binding, from the playtest-era laws + 3D pipeline)
- PIXELATED EVERYTHING: 512px NEAREST + 5-bit posterize bake; raw meshes as-is
  (no geometry post-processing beyond the bake pipeline's standard decimate/
  normalize used by the shipped 46-asset production run).
- PALETTE: darkwood canon (deep moss-green loam, charcoal mud, bone-pale
  stone); ONE accent per frame (amber human fire / cyan magic / red pact).
  Farm = human amber touches ONLY.
- NO HUD/game wiring, NO prototype/js edits, NO bundle rebuild. Deliver GLBs
  + PNGs + a manifest addendum under art-direction/3d/assets/.
- NO harness runs, NO headless browser passes (repo stays clean).
- Commit NOTHING: work on the feat/world-visuals worktree at
  /tmp/wh-worldfeat but leave files UNTRACKED for IO review (IO is the
  gatekeeper); report paths + tri counts + QA grids at the end.

## 1. SOURCE OF TRUTH = CONCEPT ART (reference these files)
- art-direction/concepts/concept-01-darkwood.png + day-01-darkwood.png
  (the forest mood), concept-06-siege-council.png (stone architecture
  scale/shape language), concept-04-tavern.png + concept-09-tavern-hearth.png
  (human structural language for the farm), day-03-blight.png (rot-adjacent
  weathering). The 00-art-direction.html hub documents the palette rules.

## 2. DELIVERABLES (targets, each = ref renders -> pixelated bake + QA grid)
A) small_farm + barn + silo + hay bales + stone well (Meshy text-to-3d,
   serial credits, <= 3 attempts per asset, STOP + evidence on fail).
   Scale language: barn ~6-8 m, cottage 4-5 m, well ~1.6 m. Farm site = the
   open ground near the Stone ring (region C, world coords near the
   ring's NE, keep 40+ m off the denTrail).
B) stone_ruin pieces x 4-6: broken wall lengths (straight/L), an arch stand
   (NOT a b3Gate copy), column stumps, a rubble heap. Weathered, moss-sunk
   bases (sitting IN the loam, not floating).
C) trees x 2-3 per concept art: an old-king oak variant (broader crown,
   heavier trunk, hanging lichen hints) + a tall bare king-pine variant.
   These must read at BOTH scales (road-side young + ancient landmark
   versions bake from the same mesh at different scales).
D) fence kit set: one stone-wall section (1.2 m), one wooden RANCH/POST fence
   section with a coherent post spacing (2.0 m, single authored design - NOT
   upscaled picketFence), one matching farm GATE (single design + single
   scale). Pieces must tile: flat posts + rails that butt-join across
   rotations (design a straight + a corner piece).
E) per asset: ref renders (3 angles), pixelated 512 NEAREST + 5-bit bake,
   tri-count report, a QA verdict per the 3D pipeline gates (fragmentation/
   frayed-rim/fragmentation checks like the rotmother bake ledger).

## 3. BUDGET
Tris per prop: farm structures <= 40k assembled per building, ruins <= 10k
per piece, trees <= 30k, fence pieces <= 3k. Region C currently spends
1,914,268 / 2,000,000 worst-case 170 m circle - the budget for the new
props is ~40k tris TOPS until Nicko approves a trim trade (record every
count; the C13b wiring pass decides what actually ships).

## 4. OUTPUT
- Files under art-direction/3d/assets/old_king/ (new folder) + ref renders
  under art-direction/concepts/old_king/.
- One MANIFEST-DRAFT.md listing every GLB (name, tris, bytes, QA verdict,
  bake seed) for IO's review.
- Final report: what shipped, what failed, credit ledger.

Skill ladder applies (image gen -> mesh -> bake). Astrabot: use the
concept-art-first workflow; do not invent palette drift.