# QJR-2 SPEC — journal dialogue capture + keyword search (Morrowind-order part 2)

Issued by IO, 2026-11-06. Branch feat/world-visuals, worktree /tmp/wh-worldfeat.
Anchor art: concept-04-tavern + concept-01-darkwood (darkwood frame, stained
parchment, one amber accent, iron fittings). Builds directly on QJR-1
(2147054 + ef97f4c): entries model `{id,title,body,day,source}` newest-first,
dedupe by id, unlock gate, additive save block 'journal', HUD button/panel.

## Scope (Nicko's Morrowind order, GOALS.md QJR-2 line)

1. DIALOGUE CAPTURE: quest events append dated journal entries — the
   Morrowind flow "new topic" -> a journal line with who said it + location:
   - RESCUE event (npc.js tryRescue): entry id 'rescue-findDaughter'.
   - COMPLETION event (npc.js openDialog, the active->complete transition):
     entry id 'quest-findDaughter-complete'.
   - ACCEPTANCE already covered by the QJR-1 unlock-edge seed
     ('quest-findDaughter') — do NOT add a second acceptance entry.
2. BODY DISPLAY: journal rows render the entry body text (a body line was
   stored since QJR-1 but never shown; search without visible text is hollow).
3. SEARCH: keyword input filters entries client-side (title + body + source,
   case-insensitive). Query state is client-only: reset when the panel opens;
   never saved.

Non-goals (QJR-3): backfill of camp folk / findDaughter lore topics / board
clerk; no new NPCs; no new assets; no game.js logic changes.

## Design decisions (IO rulings)

- Strings live in CONFIG (A9 law): CONFIG.journal.text gains
  `searchPlaceholder` + `searchNoMatch`; CONFIG.journal gains a `topics`
  block (`rescue`, `complete`, each `{id,title,body,source}`). npc.js reads
  CONFIG and calls window.WH_JOURNAL.append — it never hardcodes journal copy.
- Day stamping: append(..., undefined, source) — journal.js already defaults
  to the live game day (QJR-1 normalizeDay). Entries are automatically dated.
- Dedupe: QJR-1 dedupe-by-id already makes repeat completion/rescue talks
  silent. The rescue + completion code paths each run once by state.
- KeyJ guard: the panel's document keydown listener must ignore KeyJ when the
  event target is the search box (typing 'j' must not close the journal).
  Escape still closes the panel from inside the box. Branches otherwise
  unchanged.
- Toast: rescue fires both the existing rescuedToast (quest copy) and the
  journal 'Journal: ' toast. Single toast slot; second write wins. Accepted.
- Save: capture/restore already roundtrip body (QJR-1) — NO save.js/game.js
  changes. Malformed-row drop law holds. Restore never seeds (old-save law).

## Files

- prototype/js/journal.js  — search input, query state, body rows, nomatch,
  KeyJ guard, openPanel reset (mod).
- prototype/js/CONFIG.js   — journal.text + journal.topics additions (mod).
- prototype/js/npc.js      — top: read CONFIG.journal; tryRescue + openDialog:
  two guarded append call sites (mod). NOTHING else in npc.js moves.
- prototype/style.css      — append #wh-journal-search / .journal-row-body /
  .journal-nomatch (mod, EOF only).
- ALL other prototype files are ZERO-TOUCH (game.js, index.html, player.js,
  save.js, wareffort.js, camp.js, chest.js, cooking.js, inventory.js, etc).
  Testerbot verifies via git diff that only these 4 files change.

## Acceptance criteria

A1. Rescue -> exactly one appended entry, id 'rescue-findDaughter', day =
    live game day, source = CONFIG topics.rescue.source; toast fires once.
A2. Rescue-complete talk -> exactly one entry 'quest-findDaughter-complete';
    repeat complete-talk appends nothing (dedupe + state).
A3. Rows show a third line: div.journal-row-body with e.body; title + day
    lines unchanged (dayStamp template intact).
A4. Search input (id 'wh-journal-search', class 'journal-search', type text,
    placeholder from CONFIG) sits in the panel above the page. Typing filters
    title+body+source case-insensitively. Zero matches (with entries present)
    -> div.journal-nomatch with CONFIG.text.searchNoMatch. openPanel clears
    the query and the input value.
A5. KeyJ while focus is in the search box does NOT toggle/close the panel and
    does NOT preventDefault; J outside the box toggles as in QJR-1; Escape
    closes the panel even from inside the box.
A6. A9 law: no new player-facing string hardcoded in npc.js/journal.js; all
    new copy reads CONFIG.journal.
A7. Save regression group: QJR-1 V5/V6 behaviors still pass (roundtrip,
    no-alias, malformed drop, seed/no-seed law, old-save law).
A8. Zero-touch: git diff shows ONLY journal.js, CONFIG.js, npc.js, style.css.
A9. Palette law: #d8b24a/#c9a94a amber accents only; no red, no gradients.
A10. Build: python3 tools/build_v8.py exit 0; grep counts in
     prototype/builds/v8-playable.html: 'QJR-2' >= 4, 'wh-journal-search' >= 2.
A11. No harness runs, no headless browser smoke tests. Node one-shot
     self-checks only. Nicko's playtest stays the acceptance bar.

Gate: IO spec (this) -> Testerbot valspec (BEFORE Devbot) -> Devbot build
card qjr-2-buildcard.md -> Testerbot independent verdict (PASS/FAIL report in
io/reports/) -> IO commit+push -> build_v8 -> release flip -> serve verify.
