# 26 - SPRITE PRODUCTION QUEUE (PROPOSED, 2026-09-13)

Status: living document. The ordered to-do list for the race/character
sprite production run. Works from the proven pipeline
(25-art-pipeline.md) and the pilot learnings (gravedigger, noble
knight). Work one card at a time: S1-S7 per character, human gates at
turnaround and batch QA. Tick checkboxes as stages complete.

## Standing Lessons (from pilots 1-2, apply to every card)

- L0 (Nicko standing rule, 2026-09-13): EVERY FINISHED IMAGE GOES ON THE
  HUB. A card is not done until its concept frame + atlases appear on
  art-direction/index.html (Race Cards section + Roster Proof Sheet).
  Mechanics: web derivative into art-direction/web/, one CARDS list
  line in build_hub.py, rebuild with /app/venv/bin/python, commit with
  the card. See the witch-hunter-art-generation skill section 9.

- L1: held weapons and heraldic charges are the consistency killers in
  turnarounds; expect 2-3 QA rounds. QA MUST check weapon presence in
  EVERY view, explicitly.
- L2 (Nicko, knight pilot): HAND POSE DRIFT across views. The knight's
  back view showed hands clasped behind the back while every other view
  had hands in front on the pommel. New rule: the turnaround prompt
  MUST specify the exact hand position per view, and QA checks hand
  position matches the canonical pose in all views.
- L3: idle animation frames must derive image-to-image from ONE source
  view; never generate idle frames independently.
- L4: symmetric rigid subjects (armor) animate cleaner than cloth;
  expect higher flicker on cloth/tatter-heavy characters.
- L5: separate generations drift (cloak folds, tatter patterns). Fine
  for rank-and-file; named characters need per-character adapter
  training (LoRA) before final production bakes.
- L6: chroma-key + defringe is the proven cleanup path (rembg's model
  download kills the pilot host; revisit only with pre-cached model).
- L7 (vampire female, card 06): floor-length garments will pool on the
  floor and hide the feet in turnaround sheets, which breaks atlas
  ground-line anchoring. Turnaround prompts for gowned characters MUST
  pin the hem at ankle height and demand visible feet/shoes in every
  view; QA checks it explicitly.

## Card Format

Each card: [race x sex]. Every card runs the full S1-S7 pipeline:
design sheet -> turnaround (Nicko gate) -> 8 directions -> 5-frame idle
-> cleanup -> QA -> atlas -> billboard page -> catalog + commit.

- [ ] prefix = not started; [x] = done; (QA r2) notes = QA rounds used.

## Queue

### CARD 01: ORC, MALE  [COMPLETE 2026-09-13]
- [x] S1 concept frame (Mordor register; 1 recompose pass; v1 archived)
- [x] S2 turnaround (first-round PASS)
- [x] S3 8 directional views
- [x] S4 5-frame idle (flicker 18.6-26.7, best of 3 characters)
- [x] S5 cleanup (alpha, defringe, normalize)
- [x] S6 QA (scripted metrics + vision gates)
- [x] S7 atlas + billboard page (sprites/orc-male/card01-billboard.html)
- [x] catalog in 24-art-bible.md + commit to repo

### CARD 02: ORC, FEMALE  [COMPLETE 2026-09-13]
- [x] S1 sheet (same grammar, leaner silhouette, rank-gender variants
      per doc 14 earned-title culture; v1 archived - weapon removed)
- [x] S2 through S7 (same stages as card 01; turnaround first-round
      PASS; idle flicker 8.3-19.0, best of the run)

### CARD 03: UNDEAD, MALE  [COMPLETE 2026-09-13]
- [x] S1 sheet (corpse tone law: gray-green flesh, grave-green lantern
      accent; v1 archived - landscape/small-figure, recomposed portrait)
- [x] S2 turnaround (first-round PASS; lantern stripped per body-canon)
- [x] S3 8 directional views (derived sheet PASS)
- [x] S4 5-frame idle (flicker 18.1-30.2, cloth coat per L4; vision PASS)
- [x] S5 cleanup (alpha, defringe, normalize)
- [x] S6 QA (scripted metrics + vision gates)
- [x] S7 atlas + billboard page (sprites/undead-male/card03-billboard.html)
- [x] catalog in 24-art-bible.md + commit to repo
- Note: split across the openai-codex credential outage (S1-S3 before,
  S4-S7 after Nicko re-authed 2026-09-13 13:41 UTC).

### CARD 04: UNDEAD, FEMALE  [COMPLETE 2026-09-13]
- [x] S1 sheet (drowned-crypt marsh; grave-green lantern accent;
      first-round register PASS)
- [x] S2 turnaround (first-round PASS; lantern stripped per body-canon)
- [x] S3 8 directional views (derived sheet PASS)
- [x] S4 5-frame idle (flicker 23.7-28.5, layered cloth per L4; vision PASS)
- [x] S5 cleanup (alpha, defringe, normalize)
- [x] S6 QA (scripted metrics + vision gates)
- [x] S7 atlas + billboard page (sprites/undead-female/card04-billboard.html)
- [x] catalog in 24-art-bible.md + commit to repo

### CARD 05: VAMPIRE, MALE  [COMPLETE 2026-09-13]
- [x] S1 sheet (veil-black/blood-red court; unlit lantern stripped for
      body canon; first-round register PASS)
- [x] S2 turnaround (first-round PASS)
- [x] S3 8 directional views (derived sheet PASS)
- [x] S4 5-frame idle (flicker 6.6-10.6, BEST of the run; vision PASS)
- [x] S5 cleanup (alpha, defringe, normalize)
- [x] S6 QA (scripted metrics + vision gates)
- [x] S7 atlas + billboard page (sprites/vampire-male/card05-billboard.html)
- [x] catalog in 24-art-bible.md + commit to repo

### CARD 06: VAMPIRE, FEMALE  [COMPLETE 2026-09-13]
- [x] S1 sheet (Veil Duchess register; fan stripped for body canon;
      first-round register PASS)
- [x] S2 turnaround (2 rounds: r1 pooled gown hid feet, archived;
      r2 ankle-hem PASS; new lesson L7 in QA notes)
- [x] S3 8 directional views (derived sheet PASS)
- [x] S4 5-frame idle (flicker 9.5-16.8; vision PASS)
- [x] S5 cleanup (alpha, defringe, normalize)
- [x] S6 QA (scripted metrics + vision gates)
- [x] S7 atlas + billboard page (sprites/vampire-female/card06-billboard.html)
- [x] catalog in 24-art-bible.md + commit to repo

### CARD 07: ELF (DAWN-REFUSER), MALE  [COMPLETE 2026-09-13]
- [x] S1 sheet (light-court sylvan lines, stars-and-bows identity pin,
      white/blue/silver palette, cold moon accent; first-round PASS)
- [x] S2 turnaround (first-round PASS; lantern stripped per body-canon)
- [x] S3 8 directional views (derived sheet PASS)
- [x] S4 5-frame idle (flicker 22.0-29.0, cloak edge per L4; vision PASS)
- [x] S5 cleanup (alpha, defringe, normalize)
- [x] S6 QA (scripted metrics + vision gates)
- [x] S7 atlas + billboard page (sprites/elf-male/card07-billboard.html)
- [x] catalog in 24-art-bible.md + commit to repo

### CARD 08: ELF (DAWN-REFUSER), FEMALE  [COMPLETE 2026-09-13]
- [x] S1 sheet (light-court watchtower; white/blue/silver; 2 rounds -
      v1 archived for smooth paint + baked bow/quiver)
- [x] S2 turnaround (first-round PASS; gear stripped per body-canon)
- [x] S3 8 directional views (derived sheet PASS)
- [x] S4 5-frame idle (flicker 23.1-46.5 metric-high but vision grade
      GOOD: subtle sway, no pose breaks; dither inflates metric)
- [x] S5 cleanup (alpha, defringe, normalize)
- [x] S6 QA (scripted metrics + vision gates)
- [x] S7 atlas + billboard page (sprites/elf-female/card08-billboard.html)
- [x] catalog in 24-art-bible.md + commit to repo

### CARD 09: DWARF, MALE
- [ ] S1 sheet (anvil/mountain-hall marks, stocky silhouette, forge
      gold accent)
- [ ] S2-S7 (same stages)

### CARD 10: DWARF, FEMALE
- [ ] S1 sheet
- [ ] S2-S7 (same stages)

## Batch Workflow (once 2+ cards are done)

- [ ] Race cards page: after each card completes, add its billboard to a
      growing race gallery page (or extend 00-art-direction.html with a
      CAST section per race) so the set is browsable.
- [ ] After all 10 cards: composite roster page (all races, all
      directions) as the NPC base-cast proof sheet.
- [ ] Then: the UE5 spike (atlas import, billboard material with
      camera-angle directional selection, Lumen night scene) per the
      engine-decision conversation on 2026-09-13.

## Reference Data for S1 Sheets

Race-flavored lore hooks live in docs/planning/14-races-houses-naming.md
(race stems, house flavor) and 22-quests-factions-gdd-part3.md (race
origins: orc = First Forge becoming-a-people story; elves split into
veil lines + dawn-refusers; dwarves = altar masons; undead = post-Fall
institution). Palette law per-biome/race in 24-art-bible.md section 3.

## Working Notes

- 2026-09-13: queue created after pilot II (knight) review. Nicko
  approved both pilots' output quality ("These look amazing"). Knight
  defect noted (L2 hand pose drift) and folded into the standing rules.
- Sex variants per race are SEPARATE cards (10 cards total), not palette
  swaps: each gets its own turnaround gate.
- Loop-later principle: cards produce canonical turnarounds + atlases;
  batch variation (outfit tiers, age tiers, damage states) loops on top
  of approved canon later.