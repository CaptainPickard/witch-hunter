# QJR-1 — Journal Core (Nicko MorROWIND order 2026-11-06, part 1 of 3)

Spec author: IO (Autopilot wake 11, 2026-11-06). Repo worktree: /tmp/wh-worldfeat,
branch feat/world-visuals. Build: python3 tools/build_v8.py (repo root).
No harness runs, no headless browser smoke tests — node one-shots only;
Nicko's playtest is the acceptance bar.

Lane family: QJR = the player-facing quest JOURNAL. This round is CORE ONLY:
entries model, unlock gate, save roundtrip, HUD button + panel skeleton
(entry LIST view). QJR-2 adds dialogue capture + keyword search; QJR-3 adds
content backfill + panel polish.

## Scope

New module prototype/js/journal.js (window.WH_JOURNAL, DOM-only IIFE, no
THREE/vendor deps): an entries array of { id, title, body, day, source }
(newest-first), a born flag, and a DOM panel. The journal is BORN when the
findDaughter quest state first leaves 'available' (the transition edge to
'active' — states are CONFIG.regionC.quest.states['available','active',
'complete']; the first acceptance is the only door in). At birth the journal
writes ONE seed entry (the quest-accepted line, source Farmer Aldric) and
reveals the HUD JOURNAL button. Before birth the button does not exist on
screen and the panel cannot open.

Save: additive block 'journal' rides the landed game.js setupSaveHooks wrap
(same pattern as lairs/questState/chest/warEffort) — capture payload
{ born, entries }. An older profile without the journal block restores as:
born = (quest active or complete), entries = [] — the button shows for an
old in-flight quest, the journal page starts empty (QJR-3 backfills).

Panel: #wh-journal modal (camp-menu pattern) with a darkwood .inv-panel
frame, a parchment insert page listing entries (title + Day stamp per row),
an empty-state line, Esc close, input suspension while open
(inventoryUI.blocked + player.setInputSuspended, npc.js:178 law), close on
player death (npc.js:252 law).

## Art anchor (law 1)

concept-04-tavern.png + concept-01-darkwood.png (both viewed this wake): the
inn under a bruised-indigo dusk, amber window-glow as the single warm accent;
the hunter's world of mud, mist and moonlight on the road. Palette law
inherits the house scheme exactly — darkwood frame = existing .inv-panel
(#1a1510 bg / #4a4034 border), parchment page insert = #e3dcc4 background
with #221c15 text (the ONE inversion this round; day stamps #6a6350),
single amber accent = 2px #d8b24a rule under the title + existing button
hover amber. NO red, no second accent, no new image assets, no gradients.
The journal is the hunter's own vellum by lantern light: cream page, dark
ink, iron-and-oak frame around it.

## S-1. CONFIG.js — CONFIG.journal (new top-level key; all PROPOSED, Nicko tunes)

    journal: {                            // QJR-1 (MorROWIND order 2026-11-06)
      button: { glyph: '☰', label: 'JOURNAL', left: 152, bottom: 20 },
      openKey: 'KeyJ',
      text: {
        title: 'JOURNAL',
        empty: 'No entries yet. The road will give you words.',
        seedTitle: "The farmer's daughter",
        seedBody: 'Farmer Aldric: the Old King\'s Barrow, west past the dead trees. Bring her home.',
        seedSource: 'Farmer Aldric',
        toastNew: 'Journal: ',
        hint: 'Esc close'
      }
    }

Placement law: INV at left 16, CAMP at left 76 ('▲ CAMP' ends ~left 136);
journal at left 152 stays clear (2px gap). CONFIG-tunable, not final.
The block is a SIBLING of CONFIG.inventoryUI / CONFIG.camp — not inside them.
Every existing CONFIG.warEffort / regionC / inventoryUI key byte-identical.

## S-2. js/journal.js — module (the whole file is new)

House shape: 'use strict' IIFE, local el() copy (npc.js:36 pattern), game
ref captured by init(g). DOM appended to #wh-root (camp.js:260 pattern);
the button to document.body (cooking.js:662 pattern). Exports:

    window.WH_JOURNAL = { init, update, capture, restore, append, isBorn,
                          isOpen, closeForTest }   // closeForTest = panel close, test seam

State:

    var game = null;
    var born = false;           // journal exists (quest was accepted once)
    var entries = [];           // { id, title, body, day, source } newest-FIRST
    var open = false;           // panel open flag
    var btn = null;             // HUD button (created in init, display 'none')
    var rootEl = null;          // #wh-journal overlay

init(g):
- capture game; build both DOM pieces; button hidden.
- keydown listener: openKey toggles open when born; Escape closes when open
  (input chain law: the panel must not react before born — the key handler
  returns early if !born).
- button: id 'wh-journal-btn', tabIndex -1, title 'Journal (J)', CONFIG
  position; pointerdown opens (preventDefault + stopPropagation), then the
  mouse-events swallow row ['mousedown','click','contextmenu'] exactly as
  cooking.js buildKitButton:649-657.

update(dt) — called every frame from game.js:
1. UNLOCK EDGE: if (!born && WH_NPC && WH_NPC.questState() !== 'available')
   -> born = true; seed the findDaughter entry (below); reveal the button;
   open nothing. This fires on live play (dialog line 3) AND after restore
   of an old profile whose quest restored active (restore order puts
   journal.restore AFTER WH_NPC.restoreQuest, so the edge sees it).
2. DEATH LAW: if open && game.player.dead -> close (input never stays
   suspended behind a dead player; npc.js:252 law).

Seed entry (written exactly once, at the edge):

    append('quest-findDaughter', CFG.journal.text.seedTitle,
           CFG.journal.text.seedBody, undefined, CFG.journal.text.seedSource)

append(id, title, body, day, source):
- day default = (game && game.dayNight ? game.dayNight.day : 0).
- DEDUPE: an entry whose id already exists is a no-op (no toast, no write).
- valid append: entries.unshift({ id, title, body, day, source }); if the
  panel DOM exists, prepend a row; if journal was already born (any append
  AFTER the seed) -> game.inventoryUI.toast(CFG.journal.text.toastNew +
  title). The seed itself stays silent (no toast at birth moment — the
  dialog panel is closing; QJR-2 revises entry toasts).

capture():
    return { born: born, entries: entries.map(clone5) }   // newest-first order preserved

clone5 = shallow clone of exactly the five keys. capture() must not leak
live references (valspec one-shot proves mutate-after-capture independence).

restore(block):
- block falsy/non-object -> entries = []; then born = (WH_NPC &&
  WH_NPC.questState() !== 'available'); rebuild panel rows; return.
  (Old-save law; NEW GAME mid-session also passes through here → fresh journal.)
- valid shape: born = block.born === true; entries = block.entries filtered:
  row must be an object with string-able id/title/body/source and a finite
  day (round to integer, clamp >= 0; malformed rows DROPPED, not crashed).
  Rebuild rows from CONFIG text.
- after restore, if !born the button is hidden again; if born it shows.

open()/close law (internal): open = inventoryUI.blocked = true +
game.player.setInputSuspended(true); close reverses BOTH (npc.js:178-179
pair). Panel display via #wh-journal.open class toggle ONLY.

isBorn()/isOpen() = getters for the no-DOM node one-shots.

## S-3. js/game.js — wiring (FIVE added lines + trailing comments, nothing else)

All in landed anchors; each line carries a '// QJR-1' tag:
1. init tier, immediately after the WH_AMBUSH init line (game.js:2610):
       if (window.WH_JOURNAL) window.WH_JOURNAL.init(game);
2. save wrap capture, after the warEffort line (game.js:2655 area):
       if (window.WH_JOURNAL) data.journal = window.WH_JOURNAL.capture();
3. save wrap explicit storage write, after the warEffort stored line:
       if (window.WH_JOURNAL) stored.journal = window.WH_JOURNAL.capture();
4. save wrap restore, after the warEffort restore line (BEFORE
   baseRestore — journal.restore must read the already-restored quest):
       if (window.WH_JOURNAL) window.WH_JOURNAL.restore(data && data.journal);
5. frame update, on the line after WH_NPC.update(dt) (game.js:3199):
       if (window.WH_JOURNAL) window.WH_JOURNAL.update(dt);
The 5th line is the last. Zero lines removed. The unlock edge reads
   WH_NPC.questState() — it NEVER writes quest state (journal is read-only
   over the quest machinery; npc.js stays the one holder).

## S-4. index.html — one script tag

Insert <script src="js/journal.js"></script> on the line directly after
<script src="js/wareffort.js"></script> (line 68 area, the manager tier,
before save.js/touch-controls). No other tag, no comment, no attribute.

## S-5. style.css — append ONE section at end of file

Append (do not reorder or edit anything above):

    /* QJR-1 journal (js/journal.js): darkwood frame + parchment page insert;
       single amber rule accent. Button mirrors the camp button body. */
    #wh-journal-btn { ... }            // same block as #wh-camp-btn (fixed, z-index 46,
                                       // min-width 44, height 30, monospace 12px, colors
                                       // #c9bf9f/#1a1510/#4a4034, shadows per house), + display block
    #wh-journal-btn:hover { border-color: #c9a94a; }
    #wh-journal { position:absolute; inset:0; display:none; align-items:center;
                  justify-content:center; background: rgba(5,4,3,0.55);
                  z-index:20; font-family:monospace; image-rendering:pixelated;
                  user-select:none; }
    #wh-journal.open { display:flex; }
    .journal-panel { width:320px; max-height:70vh; display:flex; flex-direction:column; }
    .journal-rule { height:2px; background:#d8b24a; margin:6px 0 10px; }  // THE amber accent
    .journal-page { background:#e3dcc4; color:#221c15; border:2px solid #4a4034;
                    box-shadow: inset 0 0 0 2px #d3c8a8; padding:10px 12px;
                    overflow-y:auto; flex:1 1 auto; min-height:0; }
    .journal-row { padding:6px 2px; border-bottom:1px solid #b7ac8f; }
    .journal-row:last-child { border-bottom:none; }
    .journal-row-title { font-size:12px; letter-spacing:1px; color:#2a231b; }
    .journal-row-day { font-size:10px; color:#6a6350; font-style:italic; margin-top:2px; }
    .journal-empty { color:#6a6350; font-style:italic; font-size:11px; padding:6px 2px; }

Panel skeleton rows: title row = .inv-title CONFIG.journal.text.title, then
the rule, then .journal-page with the entries (or .journal-empty), then
.inv-hint Esc close. No search box, no tabs, no detail view (QJR-2/3).

## S-6. Out of scope (explicit)

No dialogue wiring (QJR-2), no search, no quest-transition entries beyond
the seed, no panel detail/pagination, no icons/glyph PNGs, no new art
assets, no npc.js/camp.js/chest.js/wareffort.js/cooking.js/save.js edits
(sha law), no region/enemy changes, no CONFIG schema bump (save stays v1
additive), no second accent color anywhere, no new scene roots or THREE
objects (journal is pure DOM), no harness/browser playtests.

## S-7. Acceptance criteria (Testerbot binds ALL)

A1 (file census): new file js/journal.js; index.html + exactly one tag per
S-4; CONFIG.js gains only the journal block; style.css diff = additions at
EOF only; game.js diff = exactly the 5 added lines of S-3 (plus their
comments). npc/camp/chest/wareffort/cooking/save shas UNCHANGED.
A2 (unlock edge): node one-shot — fresh: isBorn() false, button hidden;
fake WH_NPC questState -> 'active', update() once: born true, entries
length 1, id 'quest-findDaughter', day = fake day, button visible.
A3 (edge single-fire): update() x 50 more while active: entries still 1.
A4 (dedupe + add): append('quest-findDaughter', ...) again -> 1 entry, no
toast; append('topic-wolf', ...) -> 2 entries, toast fired once, newest first.
A5 (save roundtrip): capture -> restore of the same block -> born/entries
identical (order included). Mutating the captured payload must not change
live entries (no aliasing).
A6 (old-save + clamp): restore(undefined) with quest active -> born true,
entries []; with 'available' -> born false. restore({born:true, entries:
[{id:1,day:-5},null,'garbage',{id:'ok',day:2.7,...valid}]}) -> 1 valid row,
day 3 (2.7 rounds up), crash-free.
A7 (panel law): open via button pointer -> game.inventoryUI.blocked true,
fake player.setInputSuspended recorded true; Esc/close reverses both;
update() with dead player closes. Panel toggles only via .open class.
A8 (build): python3 tools/build_v8.py exit 0 from repo root; built
builds/v8-playable.html contains 'QJR-1' >= 6 times and 'wh-journal-btn'
>= 2; index.html marker 'js/journal.js' present in built html inline.
A9 (CONFIG isolation): every journal string lives in CONFIG.journal.text
(module reads only CFG.journal.*) — one-shot greps journal.js for no
hard-coded player-facing strings beyond CONFIG reads.
A10 (zero-regression): CONFIG.warEffort.ladder keys, regionC.quest keys,
inventoryUI.openButton present and byte-identical; builds/ v8 title-stamp
still deterministic.
