# 26 - SPRITE PRODUCTION QUEUE (PROPOSED, 2026-09-13)

Status: living document. The ordered to-do list for the race/character
sprite production run. Works from the proven pipeline
(25-art-pipeline.md) and the pilot learnings (gravedigger, noble
knight). Work one card at a time: S1-S7 per character, human gates at
turnaround and batch QA. Tick checkboxes as stages complete.

## Standing Lessons (from pilots 1-2, apply to every card)

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

### CARD 04: UNDEAD, FEMALE
- [ ] S1 sheet
- [ ] S2-S7 (same stages)

### CARD 05: VAMPIRE, MALE
- [ ] S1 sheet (elf-vampire court: tall gaunt, veil-black/blood-red
      wardrobe, broken-sun motifs, red accent law)
- [ ] S2-S7 (same stages)

### CARD 06: VAMPIRE, FEMALE
- [ ] S1 sheet
- [ ] S2-S7 (same stages)

### CARD 07: ELF (DAWN-REFUSER), MALE
- [ ] S1 sheet (light-court sylvan lines, stars-and-bows charges,
      white/blue palette law)
- [ ] S2-S7 (same stages)

### CARD 08: ELF (DAWN-REFUSER), FEMALE
- [ ] S1 sheet
- [ ] S2-S7 (same stages)

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