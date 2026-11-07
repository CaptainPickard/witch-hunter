# CC-AF2 SPEC — Affinity-reactive camp-NPC dialogue (v1)

Round: CC-AF2 (continues CC-AF1 landed f1cefd0; docs 12 + 44/45 story-web.
Backlog lane "affinity-gated camp dialogue (world reactions to Sworn/Feared)").
Worktree: /tmp/wh-worldfeat, branch feat/world-visuals. NO-GIT: children edit
files only; IO is the sole committer.

## GOAL

The world reacts to the player's standing tier in dialogue. Farmer Aldric (the
one talk-to NPC, js/npc.js, CONFIG.regionC.npc.dialog) chooses his REPEAT line
by Standing tier on every dialog OPEN, after quest state.

## RULES (order matters)

1. Quest state FIRST, byte-identical behavior to v8 (CC-C10/C11) for quest
   flow: 'available' -> line1..line3; 'complete' -> lineComplete. The CC-C11
   sentinel lines (-2 lineRescued, -3 lineComplete, -4 lineRescue) are NOT
   tier-reactive — they are story beats, untouched.
2. ONLY the 'active' quest repeat line becomes tier-reactive. At openDialog
   time, after quest-state selection sets lineIdx = -1 (repeat), the module
   resolves the repeat text:
   - tier = window.WH_AFF.tier().id — gated on PRESENCE of WH_AFF (if absent
     or tier() falsy -> D.repeat, no throw). Decision by tier ID, never by
     reading score directly in npc.js.
   - 'honored' OR 'sworn-light' -> D.lineAffinityGood
   - 'feared' OR 'sworn-dark' -> D.lineAffinityDark
   - otherwise (neutral) -> D.repeat (BYTE-IDENTICAL to v8's repeat line)
   Re-open after tier change picks the new line (decision is per-open, no
   caching of the choice).
3. Copy lives ONLY in CONFIG.regionC.npc.dialog (two appended keys,
   single-line strings, APPEND ONLY — do not reorder or edit sibling keys):

   lineAffinityGood: "Aldric: 'You are welcome at any fire in the camp,
   hunter. Word of the daughter travels further than you think.'"

   lineAffinityDark: "Aldric: 'The camp watches its fires when you pass,
   hunter. I have my daughter thanks to you — I will not watch too closely.'"

   (Style anchor: camp-good concept = welcome/hearth gold; camp-dark = red low
   fire, watched. Voice = doc 44 camp folk, plain address "hunter".)
4. No journal topic in v1, no deed changes, no ladder changes, no save schema
   change: the quest save block stays v1 ({state, rescued}); tier is live
   state and is NOT saved.
5. npc.js change surface: minimal. A small helper (e.g. repeatLine()) +
   call in showLine() for lineIdx === -1 only. Header comment line "CC-AF2:"
   at the choice site, matching file style. No literals in npc.js beyond the
   tier-id strings ("honored", "sworn-light", "feared", "sworn-dark") or a
   small CONFIG constant set; prefer a CONFIG.affinity.dialogMap append
   (PROPOSED, single source of truth) — either is acceptable; valspec
   decides which is verified.
6. Files touched: ONLY prototype/js/CONFIG.js (+2 keys) and
   prototype/js/npc.js (helper + call + comment). affinity.js, camp.js,
   journal CONFIG topics: untouched. No build run by children; no other
   modules reflowed.

## ACCEPTANCE (Testerbot validates code, not play; letters reused by valspec)

- A: quest 'available' -> line1 shown on open; tier-agnostic (also with
  score -80 or +80 forced).
- B: quest 'active', standing neutral (score 0) -> repeat line BYTE-IDENTICAL
  to CONFIG.regionC.npc.dialog.repeat.
- C: quest 'active', honored (e.g. score 50 via deeds) -> lineAffinityGood.
- D: quest 'active', feared (score -50) -> lineAffinityDark.
- E: quest 'complete' -> lineComplete shown, regardless of tier (incl +80).
- F: WH_AFF absent (delete stub in a probe) -> 'active' open falls back to
  D.repeat, no exception.
- G: CC-C11 sentinels preserved: rescue (-4) shows lineRescue; complete path
  (-2/-3) unchanged; negative sentinels never tier-swapped.
- H: save schema unchanged; restoreQuest of an old v1 block still works
  (grep: no new fields in questStateDetail).
- I: CONFIG diff is exactly the 2 added dialog keys (append, single-line);
  npc.js diff bounded to the repeat-path helper + call + header comment.
