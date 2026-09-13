# SESSION PROMPT - WITCH HUNTER CARD 02-10 + EQUIPMENT LAYERS

Copy everything inside the code block into a fresh IO session.

```
Continue the Witch Hunter sprite production run. The project repo is
/workspace/witch-hunter (also on GitHub as CaptainPickard/witch-hunter,
branch dev). Read these docs FIRST, they contain everything you need:

1. /workspace/witch-hunter/docs/planning/26-sprite-production-queue.md
   - the card queue. Card 01 (orc male) is COMPLETE. Your job is cards
   02 through 10: orc female, undead male/female, vampire male/female,
   elf (dawn-refuser) male/female, dwarf male/female.

2. /workspace/witch-hunter/docs/planning/24-art-bible.md
   - the locked art register, palette law, prompt grammar (section 4),
   frame catalog, and QA checklist (section 7). Follow it exactly.

3. /workspace/witch-hunter/docs/planning/25-art-pipeline.md and
   /workspace/witch-hunter/docs/planning/27-equipment-visual-system.md
   - the pipeline stages (S1-S7) and the canon-layer vs equipment-slot
   distinction (transition pieces like gorget/faulds/leg harness are
   CANON, baked into the body, never slots; slots are cloak, gloves,
   chest, helm, weapon).

4. The witch-hunter-art-generation skill (load it with skill_view).

CARD PIPELINE per character (proven on card 01, follow it exactly):
- S1 CONCEPT: generate a third-person behind-figure concept frame
  (portrait 1024x1536) per the register: painterly pixel-art hybrid,
  dithering+grain, 60-80% near-black negative space, tiny-to-lone
  figure, mono cool base + ONE accent (per-biome/race palette in bible
  section 3), backlit rim light, diegetic light sources only, mood =
  quiet dread. Race flavor per the queue doc (orcs = Mordor-register
  creatures of evil per Nicko's explicit instruction; undead = gray-green
  flesh + corpse-green accent; vampires = tall gaunt elf-vampires,
  veil-black/blood-red; elves = sylvan light-court, white/blue + silver;
  dwarves = stocky, forge-gold accent). These characters generate dense
  first, then RECOMPOSE to register (v1 archived in _qa/). Vision QA
  with gemma4:31b via ollama cloud (the vision model in profile config).
- S2 TURNAROUND: image-to-image from the concept, 4 views (back, 3/4
  rear L, side L, 3/4 front L) on flat #1A1D24 studio background, even
  scale, same ground line. Weapons REMOVED (per L1 lesson: weapons and
  heraldry are consistency killers; weapons are separate layers).
  Vision QA; expect 2-3 rounds; archive failures in _qa/. Cut the 4
  views into views/ folder.
- S3 DIRECTIONS: generate the missing 4 views (front, side-right,
  3/4 front-right, 3/4 rear-right) each image-to-image from the nearest
  existing view. 8 total.
- S4 IDLE: 5-frame breathing idle, all frames derived image-to-image
  from the view-back master, one small change per frame (rise/settle/
  rest/inhale-start/peak). Never generate idle frames independently.
- S5 CLEANUP (use /workspace/witch-hunter/tools/): alpha_extract.py,
  defringe.py, atlas_pack.py (512px canvas, feet anchored). See the
  orc-male card for exact usage patterns.
- S6 QA: qa_gate.py metrics (flicker, coverage) + vision check.
- S7 SHIP: build a card billboard page (copy the pattern from
  sprites/orc-male/card01-billboard.html: orbit drag, idle toggle,
  atlases, findings), catalog entries in bible section 5, tick the
  card's checkboxes in doc 26, commit to the repo (git add the card
  folder + docs, imperative commit message, push origin dev).

EQUIPMENT LAYERS (after each race's body canon exists, or batched at
the end): use the in-place + diff-extraction technique proven in
sprites/noble-knight/layers/ (flatten the body canon to a gen input,
ask the model to ADD ONLY one piece keeping everything else identical,
diff-extract the added pixels with scipy label + largest components).
The orc cleaver weapon layer is the first one to do (card 01 deferred
it). Transition pieces (gorget, faulds, leg harness) are CANON layers,
baked into the body, never slots (Nicko ruling, doc 27).

THE HUB: /workspace/witch-hunter/art-direction/index.html is the
navigable proof-of-concept site. It is BUILT from hub-template.html +
build_hub.py. NEVER hand-edit index.html: add a web-weight derivative
(720px q72 JPEG into art-direction/web/, use the webify pattern in
build_hub.py), add a fig()/pair() line to the builder, re-run
python3 /workspace/witch-hunter/art-direction/build_hub.py. The Layer
Lab section uses full-canvas PNG data URIs. After each card completes,
add its concept frame + atlases to the hub so the site stays the
browsable master proof-of-concept.

COMMIT after each card (single card commit), push origin dev. Never
commit to main. Never modify docs 00-25 except the bible catalog and
the queue checkboxes. No external image URLs anywhere; all art is
generated via the image_generate tool with the bible grammar. All page
text pure ASCII.

Work through cards 02-10 sequentially. After all 10: build a roster
proof-sheet section in the hub showing all races' concept frames and
atlases, then commit. Report progress per card.
```