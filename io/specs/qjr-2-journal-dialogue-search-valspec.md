# QJR-2 Journal Dialogue Capture + Search Validation Spec (v1, Testerbot-owned; written BEFORE the Devbot build)

Round: qjr-2 (journal dialogue capture + keyword search: npc.js rescue/complete
append hooks, CONFIG.journal.text + topics, body-row third line, client-side
query state, KeyJ-in-box guard). Worktree /tmp/wh-worldfeat @ feat/world-visuals,
HEAD recorded at dispatch (V-0). Spec: io/specs/qjr-2-journal-dialogue-search-spec.md;
this file binds its A1-A11. Format + harness law continue
io/specs/qjr-1-journal-core-valspec.md and the STAGE 6 fake game/window stub
pattern of io/specs/qjr-1-buildcard.md. Test style: node one-shots ONLY (fake-DOM
recorder harness, see Harness law). NO harness runs, NO headless-browser smoke
tests, NO browser automation (standing order; spec A11). NO git writes (NO-GIT
law): validate the tree as found; IO commits after the verdict. Read-only git
(rev-parse/status/diff/log) allowed, REQUIRED for the census groups (A8). NO
harness-run playtests and NO serving checks: build_v8 runs are allowed (A10),
but Nicko's playtest stays the acceptance bar — Testerbot never stands in for it.

## File law for the round

TOUCHED — `git diff`/`git status --porcelain` at verdict time must show EXACTLY
these five paths and NOTHING else (A8 census, V-1):
  prototype/js/journal.js    (mod: search input, query state, body rows,
                              nomatch, KeyJ guard, openPanel reset)
  prototype/js/CONFIG.js     (mod: journal.text +{searchPlaceholder,searchNoMatch};
                              NEW journal.topics {rescue,complete})
  prototype/js/npc.js        (mod: top CONFIG.journal read + two guarded
                              window.WH_JOURNAL.append call sites — tryRescue,
                              openDialog active->complete transition; NOTHING
                              else in npc.js moves)
  prototype/style.css        (EOF append ONLY: #wh-journal-search /
                              .journal-row-body / .journal-nomatch)
  prototype/builds/v8-playable.html (rebuilt artifact, tools/build_v8.py)
ZERO-TOUCH (sha256 UNCHANGED through the whole validation):
  prototype/js/game.js, prototype/index.html — QJR-1 landed these; QJR-2 must
  not move them (save hooks, script tag list already in place);
  prototype/js/save.js, player.js, camp.js, chest.js, cooking.js, inventory.js,
  touch-controls.js, wareffort.js, region-defs.js.
Any ZERO-TOUCH sha change at ANY point = immediate FAIL (no grace). Journal
remains read-only over the quest machinery (journal.js may read WH_NPC.
questState(), never writes it); npc.js owns quest state, journal.js owns
entries. No new assets, no index.html edit, NO new script tag (all three js
files load already), no game.js logic change (spec Non-goals).

## Pre-checks (sha the files BEFORE reading any landed code)

V-0. Record sha256 FIRST: prototype/js/journal.js, prototype/js/CONFIG.js,
     prototype/js/npc.js, prototype/style.css, prototype/js/game.js,
     prototype/index.html + the byte size of style.css (V-1 append-only check
     needs it) + prototype/builds/v8-playable.html (pre-build sha AND byte
     size) + `git -C /tmp/wh-worldfeat rev-parse HEAD`. Also write the
     validator-authored one-shot /tmp/qjr2_pre_config.js output to
     /tmp/qjr2_pre_config.json: JSON of {journal: WH_CONFIG.journal,
     quest: WH_CONFIG.regionC.quest} (post groups byte-compare against it; V-14).
     After validation re-run ALL (V-15); the report carries the pre/post sha
     table. IO-logged pre-dispatch baselines (must MATCH before Devbot lands):
     HEAD           ef97f4cd8b4dae7d00b5dd784caf014b9397a9d6
     journal.js     e4bfa37cfb9a48c3f5739b5b077a535b2842e47b5dd943fc2fba38d7ea04927c
     CONFIG.js      fd3434b876bafc6e890d97a57ea50d730b5e8bc15497b2b98416a0349020469e
     npc.js         cf9137db41d76d8cc80fa37460a6b23d7beb84315850477f7b56862ac8ca3f31
     style.css      1cbde19b346212b5e0b54f8577d07f7e47404fa2d5a2c5c4535e8bfca837b13c  (30898 bytes)
     game.js        9d0468c3c7fe17f67fb3186a83f71cce55e8be882d6f3e535a2ddc9fa4a185a3
     index.html     b2f83043c433700246c77eb29c55263ce2db4bc02c023d2fe809744b537fc256
     builds/v8-playable.html  12dab405be41ea749d6524b10438c55ca1f35b4de765a4ecc67ffc605eb42c19  (3399828 bytes)
     A mismatch between the validator's own sha256sum readings and ANY of
     these lines before Devbot lands = the tree changed under dispatch; STOP
     and re-derive before designing checks.
V-0b. Pre-sha the remaining ZERO-TOUCH set (save/player/camp/chest/cooking/
     inventory/touch-controls/wareeffort/region-defs; the QJR-1 landed state
     is the baseline). HEAD must still equal the V-0 sha at every verdict
     moment (V-15 re-proves at the end).

## Landing gate (poll discipline)

Devbot lands journal.js + CONFIG.js + npc.js + style.css edits + a rebuilt
artifact (build card io/specs/qjr-2-buildcard.md, authored after this valspec).
Poll with `sha256sum` (>= 30 s interval) until ALL of: (i) journal.js,
CONFIG.js, npc.js, style.css pre-shas EACH changed, (ii) `grep -c 'QJR-2'`
prototype/builds/v8-playable.html >= 1, (iii) `grep -c 'wh-journal-search'`
same file >= 1. Poll cap: poll >= 15 minutes before ANY "landing never
happened" FAIL conclusion. A landing detected mid-poll re-pins V-0's
post-baselines; before treating the tree as validatable, re-check EVERY
zero-touch sha is still at its V-0 value (mid-landing drift = FAIL).

## V-groups (each a numbered node check; bind spec A1-A11)

V-1 Zero-touch census (A8) — exact assertions, from repo root:
  - `git -C /tmp/wh-worldfeat status --porcelain`: NO untracked path under
    prototype/ (validator scratch lives in /tmp ONLY); the changed-set =
    exactly the five TOUCHED paths.
  - `git diff --numstat` per path: game.js and index.html have 0 added and
    0 removed lines (their shas already equal V-0/V-0b — this is the formal
    re-proof); every other prototype path is untouched.
  - `node --check prototype/js/journal.js` exit 0; `node --check
    prototype/js/npc.js` exit 0; `node -e
    "global.window={};require('/tmp/wh-worldfeat/prototype/js/CONFIG.js')"`
    exit 0; `grep -c THREE prototype/js/journal.js` === 0 (pure DOM, no new
    assets).
  - npc.js census: `git diff -U0 -- prototype/js/npc.js` removed lines are
    ALL comment-only (after trimming, each starts '//' or '/*' or '*') —
    zero removed CODE lines; every ADDED code line carries '// QJR-2'; the
    added lines anchor at exactly three places (grep -B2/-A2 context): (1) a
    top-of-module read of CONFIG.journal (near the var CFG/N/Q/D head), (2)
    inside openDialog's active->complete transition branch, (3) inside
    tryRescue; total added lines <= 16.
  - journal.js census: removed lines ALL comment-only (zero removed code
    lines — provable title/day law; A3's dayStamp intactness rides on this);
    additions confined to: the state head (query var), rebuildRows (body row
    line), openPanel (query reset), init (search input node), the keydown
    handler (KeyJ guard branch); post file contains 'wh-journal-search',
    'journal-row-body', 'journal-nomatch' each >= 1 and 'QJR-2' >= 1; the
    exact QJR-1 line
    `          row.appendChild(el('div', 'journal-row-day', CFG.text.dayStamp`
    still exists with `.replace('{day}', String(e.day))` and
    `.replace('{source}', e.source || ''))` on its continuation lines.
  - CONFIG.js census: zero removed CODE lines (comment-only allowed); added
    lines confined to the existing `window.WH_CONFIG.journal` block (between
    the `journal = {` line and its closing `};`) — no other CONFIG region
    grows (V-14 byte-proves pre-block regions untouched).
  - style.css census: APPEND-ONLY — sha256 of the FIRST 30898 bytes of the
    post style.css === the V-0 style.css sha (pre content is a byte-prefix;
    zero edits/reorders above EOF).

V-2 CONFIG journal additions census (foundation of A6; reads REAL CONFIG) —
  /tmp/qjr2_v2.js loads CONFIG.js with global.window={}; asserts:
  - journal.text pre keys survive BYTE-IDENTICAL (compare against
    /tmp/qjr2_pre_config.json: title, empty, dayStamp, seedTitle, seedBody,
    seedSource, toastNew, hint — every value unchanged; button object
    unchanged and openKey === 'KeyJ').
  - journal.text gains EXACTLY {searchPlaceholder, searchNoMatch} (set
    equality: pre keys + exactly those two, both non-empty strings).
  - journal gains a `topics` block, EXACTLY {rescue, complete} as keys; each
    row EXACTLY the 4-key set {id,title,body,source} (set equality; all four
    non-empty strings);
    topics.rescue.id === 'rescue-findDaughter';
    topics.complete.id === 'quest-findDaughter-complete'.
  - NO second acceptance entry anywhere: 'quest-findDaughter' appears in
    CONFIG only as the pre-existing journal.text seed (seedTitle/Body/Source
    trio) — the topics block carries NO 'quest-findDaughter' bare entry and
    the acceptance-id count in journal.toString() is 4 or fewer total
    occurrences (seed + the two topic ids + none else) — the concrete bar:
    `grep -c "id: 'quest-findDaughter'" CONFIG.js` === 0 (the seed is text,
    not a topic row).
  - NO new CONFIG top-level key; regionC.quest keys/values byte-identical to
    the pre snapshot (rescuedToast untouched at 'The daughter is safe.
    Return to Farmer Aldric.').

V-3 Palette law (A9) — grep-level, no node needed:
  - The APPENDED style.css region (bytes after offset 30898) declares the
    pinned selectors: '#wh-journal-search', '.journal-row-body',
    '.journal-nomatch' each present >= 1.
  - Amber accents ONLY: every hex literal whose value is NEW (not already in
    the pre-EOF file) must be in the allowed QJR-1 family set
    {'#d8b24a','#c9a94a','#4a4034','#1a1510','#14110e','#2a231b','#e3dcc4',
     '#d3c8a8','#b7ac8f','#c9bf9f','#6a6350','#221c15','#d8d2c0'}
    (darkwood #1a1510 body, iron #4a4034 borders, stained parchment
    #e3dcc4/#d3c8a8/#d3c8a8 family, ink #221c15, amber rule #d8b24a, hover
    amber #c9a94a; concept-04-tavern + concept-01-darkwood anchors, no new
    assets). The appended region carries '#d8b24a' >= 1 (the single amber
    accent law).
  - Forbidden in the appended region (case-insensitive grep): 'gradient'
    (no gradients), 'red', 'crimson', 'maroon' (no red, no second accent).
    Any rgba() in the appended region must have its red channel <=
    max(green, blue) (ink/shadow family only).
  - Cross-file: npc.js/journal.js diffs contain NO style hex strings and NO
    inline cssText additions (DOM styling stays in style.css this round; the
    QJR-1 inline-csstext npc dialog is untouched — its shas/diff prove it).

V-4 Rescue capture one-shot (A1) — /tmp/qjr2_v4.js, REAL npc.js + REAL
  journal.js + REAL CONFIG.js on the fake game/window stub (Harness law):
  - Setup: window.WH_NPC = real npc.js module; fake game:
    regionManager.logic.activeId = CFG.regionD.id, player {state:'alive',
    inputSuspended:false, pos within rescueInteractM (3) of the
    stoneSarcophagus prop (CONFIG.regionD.props, x=-201, z=-185 at
    dispatch), setInputSuspended spy}, inventoryUI {blocked, toast->toastLog},
    dayNight {day: 7}; npc.init(game); journal.init(same game object).
  - restoreQuest({findDaughter:{state:'active',rescued:false}});
    window.WH_JOURNAL.update() once (unlock edge -> seed born, seedDone
    true); entries.length === 1 (seed still exactly once — no second
    acceptance entry, spec Scope 1).
  - rescuePrompt() returns true; WH_JOURNAL.closeForTest() first (panel not
    open); tryRescue() returns true; asserts:
    entries.length === 2 newest-FIRST with entries[0].id ===
    'rescue-findDaughter'; entries[0].day === 7 (live fake game day — the
    append(...,undefined,source) day-stamping law); entries[0].title/body/
    source === CONFIG.journal.topics.rescue.title/body/source (npc.js read
    CONFIG — the A6 law in behavior).
    rescue entry is 'exactly one': a SECOND tryRescue() cannot fire
    (rescued flips rescuePrompt() false; tryRescue() returns false;
    entries.length STILL 2; no new toast).
  - Toast law: toastLog contains the quest copy (CONFIG.regionC.quest.
    rescuedToast) EXACTLY once and a 'Journal: ' prefixed fire (CFG.text.
    toastNew + topics.rescue.title) EXACTLY once; entries model unchanged by
    toasting. Single-slot ordering is NOT pinned either way (spec Toast
    ruling: both fire, second write wins — accept either order); assert
    toastLog.length === seedToast + 2 exactly (seed stays silent; V-3 of
    qjr-1 valspec law still holds).
  - npc.js wrote NO journal entry id outside CONFIG (the id literal check is
    V-9); journal wrote NO quest state: WH_NPC.questState() === 'active'
    after tryRescue (journal is read-only).

V-5 Completion capture one-shot (A2) — /tmp/qjr2_v5.js, fresh harness as V-4:
  - restoreQuest({findDaughter:{state:'active',rescued:true}});
    WH_JOURNAL.update() (seed edges in); openDialog() -> the transition:
    questState() === 'complete' after this call and ONLY after it.
    asserts: entries.length === 2; entries[0].id ===
    'quest-findDaughter-complete'; title/body/source === CONFIG.journal.
    topics.complete.*; day === fake day; 'Journal: ' toast fired for the
    completion entry (toastNew + topics.complete.title).
  - REPEAT complete-talk: closeDialog(); openDialog() again (quest already
    'complete', lineIdx -3 branch): entries.length STILL 2; no entry id
    duplicated (dedupe + state BOTH — grep the toastLog: no second
    'Journal: ' completion fire; entries map has exactly one row per id);
    toastLog gains ZERO 'Journal: ' rows on the repeat.
  - Acceptance not duplicated: every id in entries is unique; the id
    'quest-findDaughter' appears EXACTLY once across entries (the QJR-1
    seed), proving no second acceptance entry was appended anywhere in the
    flow.

V-6 Body-row rendering (A3) — /tmp/qjr2_v6.js, journal-only harness (real
  CONFIG.js + journal.js + WH_NPC stub, fake game, day 4):
  - Edge fire + append('topic-smith','The smith','He spoke of the barrow.',
    undefined,'Road') (2 entries with non-empty bodies).
  - Open the panel via the button pointerdown handler (QJR-1 V-7 dispatch
    pattern). On pageEl (recorder #journal-page child of .journal-panel of
    #wh-journal): for EACH entry EXACTLY one .journal-row exists containing
    IN ORDER: div.journal-row-title with textContent === e.title; a
    div.journal-row-body with textContent === e.body (the NEW third line);
    div.journal-row-day with textContent === 'Day 4 - Road'
    (CFG.text.dayStamp 'Day {day} - {source}' template rendered VERBATIM —
    the template is unchanged). Row order newest-first. NO other classes
    appear in a row and the day line is NOT doubled (exactly one
    journal-row-day per row).
  - The empty-entry state still legal: a harness where every body is ''
    renders journal-row-body nodes with textContent === '' (body row exists
    even when the stored line is empty — QJR-1 old saves carry empty
    bodies; the row law is unconditional).

V-7 Search filter + nomatch + openPanel reset (A4) — /tmp/qjr2_v7.js,
  journal-only harness, panel open, entries seeded so each of title / body /
  source carries one DISTINCT keyword (e.g. title 'Wolves', body 'barrow',
  source 'Aldric'):
  - The panel DOM, in child order, contains the input BEFORE the
    .journal-page node: the input node has id 'wh-journal-search', className
    containing 'journal-search', type === 'text', placeholder ===
    CFG.text.searchPlaceholder (CONFIG read, A6).
  - FILTER: set input.value through each probe query and dispatch the
    registered 'input'/'keyup'-style handler (recorder event with target =
    the input): 'wolves' (title hit) -> the Wolves row visible, others
    gone/hidden; 'BARROW' (body hit, case-insensitive UP) -> the barrow row;
    'aldric' (source hit) -> that row; a query matching NOTHING (with
    entries present) -> ZERO visible rows and EXACTLY ONE div.journal-nomatch
    under the page whose textContent === CFG.text.searchNoMatch (a CONFIG
    read, no hardcoded copy); nomatch appears ONLY in the zero-hit state.
    Matching is case-insensitive in BOTH directions (lower query vs Mixed
    data AND upper query vs lower data — assert both). Fields joined: a
    query of two keywords from DIFFERENT fields of one entry (e.g. 'wolves
    aldr') matches that entry (title+body+source searched as one haystack).
  - Visible-set law is implementation-neutral: each .journal-row is either
    ABSENT from pageEl children at inspection time or carries a journaled
    style.display write of 'none'; the attached-and-visible row set equals
    the match set.
  - RESET: with a query active (list filtered), close then reopen via the
    button pointer — query state is cleared: input.value === '' and the
    FULL list is visible again (openPanel clears the query AND the input
    value). Reopening does NOT re-run the old query (no stale nomatch).
  - CLIENT-ONLY STATE: capture() still returns EXACTLY {born, entries} (set
    equality) — NO query key ever enters the save block (never saved); a
    capture/restore roundtrip with a query active loses the query silently
    (assert restore then shows the full list after the next open).

V-8 KeyJ guard in the search box + escape-from-box (A5) — /tmp/qjr2_v8.js,
  journal-only harness, panel OPEN via button pointer (suspension ON; spy
  history [true] at this point):
  - Dispatch the document keydown handler with {code:'KeyJ', repeat:false,
    target:<the search input recorder>}: isOpen() STAYS true (no toggle,
    no close), the preventDefault spy is NOT called (typing 'j' keeps its
    native meaning in the box), inventoryUI.blocked stays true, suspend spy
    history unchanged ([true]); the input still RECEIVES its own handlers
    (the guard must not swallow anything but the toggle).
  - Dispatch KeyJ with target = the panel/body recorder (NOT the box):
    toggles CLOSED exactly as QJR-1 (blocked false, spy [true,false]) — the
    outside-box law unchanged.
  - ESCAPE from the box: reopen (spy [true,false,true]); dispatch
    {code:'Escape', target:<input recorder>}: panel closes (blocked false,
    spy [true,false,true,false], 'open' class gone, isOpen() false) —
    Escape closes from INSIDE the box (A5 escape-from-box close).
  - e.repeat guard unchanged: a KeyJ (target outside box) with repeat:true
    is a no-op (QJR-1 branch law intact). Panel closed + KeyJ outside box ->
    opens; the guard branch must not fire when the panel is closed with
    target = input (isOpen() still false — no crash, no toggle).

V-9 A9-law strings-via-CONFIG audit (A6) — /tmp/qjr2_v9.js, static scan of
  the LANDED npc.js + journal.js:
  - Strip ALL '//' line comments and '/* */' blocks FIRST (comments exempt).
    Extract every single-/double-quoted literal from the REMAINING code.
    A literal is ALLOWED only if: (a) a CONFIG path/key member used for
    reads (e.g. 'journal', 'topics', or its row keys 'rescue'/'complete'
    when read as members); (b) an id/class string from the spec: the QJR-1
    allowlist (wh-journal-btn, wh-journal, journal-panel, journal-rule,
    journal-page, journal-row, journal-row-title, journal-row-day,
    journal-empty, inv-panel, inv-title, inv-hint, wh-root, wh-hud,
    wh-npc-label, wh-npc-dialog, npc-dialog-line, cook-btn, cook-btns,
    npc-dialog-panel, npc-dialog-btns, inv-*) PLUS the QJR-2 pins
    'wh-journal-search', 'journal-search', 'journal-row-body',
    'journal-nomatch'; (c) structural/boilerplate: 'use strict',
    instantiated DOM tag names ('div','input','button'), event names
    (keydown, Escape, pointerdown, mousedown, click, contextmenu, input),
    attribute/property strings (id, class, style, display, type, text,
    value, placeholder, tabIndex), 'none'/'flex'/'block' style values, the
    spec-pinned tooltip 'Journal (J)'; (d) npc.js PRE-EXISTING literals
    only for lines NOT touched by the QJR-2 diff (quest-state literals
    'available'/'active'/'complete', 'Escape', asset names, the inline
    Dialog cssText) — for ADDED lines the (a)-(c) classes apply strictly.
  - HARD second bar: NO string literal EQUALS any CONFIG.journal.text VALUE
    (searchPlaceholder and searchNoMatch included) or any
    CONFIG.journal.topics.{rescue,complete} id/title/body/source value, and
    the quoted literals 'rescue-findDaughter' and
    'quest-findDaughter-complete' occur ZERO times in npc.js and ZERO times
    in journal.js (grep both post files: every occurrence in the repo's
    touched js lives ONLY in CONFIG.js). The one-shot FAILS on any literal
    outside these classes — every new player-facing string lives in
    CONFIG.journal (A6).

V-10 Zero-regression: QJR-1 V5 roundtrip + no-alias (A7) — /tmp/qjr2_v10.js,
  journal-only harness (LANDED QJR-2 journal.js), edge + one appended entry:
  - capture() returns EXACTLY the keys {born, entries} (set equality — the
    query state did NOT leak into the save model); every row EXACTLY
    {id,title,body,day,source}; order newest-first; born true.
  - restore(JSON.parse(JSON.stringify(captured))) -> isBorn() true; entries
    deep-equal the captured rows (JSON equality, ORDER INCLUDED); capture()
    after restore identical to the input block.
  - NO ALIASING: mutate the captured payload hard (payload.entries.push({});
    payload.entries[0].title='MUTATED'; per-row field writes) -> live
    entries unchanged (QJR-1 V-5 clone law).

V-11 Zero-regression: QJR-1 V6 malformed drop + seed law (A7) —
  /tmp/qjr2_v11.js; EVERY sub-case crash-free (one-shot asserts each):
  - restore(undefined) with questState 'active': born true, entries [],
    button visible; a following update() keeps entries [] (restore never
    seeds — old-save law).
  - restore(undefined) with questState 'available': born false, entries [],
    button hidden; KeyJ press does NOT open the panel (isOpen() stays
    false — the !born early return).
  - restore({born:true,entries:[{id:1,title:'t',body:'b',source:'s',day:-5},
    null,'garbage',{id:'ok',title:'T',body:'B',source:'S',day:2.7},
    {id:'nan',title:'N',body:'B',day:NaN,source:'S'},
    {id:'inf',title:'N',body:'B',day:Infinity,source:'S'}]}): EXACTLY 1
    valid row — id 'ok', day === 3 (2.7 rounds-to-integer), title/body/
    source preserved; negative / non-object / non-array / NaN / Infinity
    rows each DROPPED, crash-free. born true -> button shown.
  - THE UNLOCK EDGE STILL FIRES under the QJR-2 file: after the malformed
    restore above, set questState 'active', born false via
    restore(undefined) on the available stub, then update() -> isBorn()
    true, entries[0].id 'quest-findDaughter', day === fake day, button
    visible (the QJR-1 seed path is intact, un-broken by the search/rows
    edit), and the search rows render the seeded entry with its body line
    (V-6 law holds for the seed row too).

V-12 Zero-regression: QJR-1 V7 panel input law (A7) — /tmp/qjr2_v12.js,
  journal-only harness, edge fired, player alive, blocked false:
  - OPEN via button pointerdown (preventDefault AND stopPropagation both
    called): blocked === true, suspend spy [true], 'open' class present,
    isOpen() true.
  - KeyJ outside box while closed -> opens (blocked true, spy [true,false,
    true]) — unchanged toggle.
  - Escape while open (target body) -> blocked false, spy history
    [true,false,true,false], 'open' class gone, isOpen() false. CLASS-ONLY
    law: no journaled write to rootEl style.display anywhere; the panel
    toggles exclusively via the .open class.
  - DEATH: reopen, player.state = 'dead', update() -> panel closed, blocked
    === false, spy history === [true,false,true,true,false] (suspension
    released on death, QJR-1 AM-1 law). The new KeyJ guard must not alter
    any of these (V-8 cross-bound).

V-13 Build + markers (A10) — `cd /tmp/wh-worldfeat && python3
  tools/build_v8.py` exit 0 from the repo root; on
  prototype/builds/v8-playable.html:
  - `grep -o 'QJR-2' | wc -l` >= 4; `grep -o 'wh-journal-search' | wc -l`
    >= 2 (the input id surfaces from both js and css). Log the counts.
  - QJR-1 markers persist (zero-regression of the build): 'QJR-1' >= 6 and
    'wh-journal-btn' >= 2; the 'WH_JOURNAL' sentinel still present >= 1
    (journal.js still inlined).
  - Byte-size sanity: post-build size >= the V-0 pre-build size (3399828).
  - DETERMINISM: run the build a SECOND time (exit 0); artifact sha after
    run 2 IDENTICAL to run 1. NO serving checks, no server start, no URL
    fetch (the flip is IO's).

V-14 CONFIG zero-regression isolation (A7/A8 support) — /tmp/qjr2_v14.js:
  - CONFIG top-level key set POST === the pre snapshot EXACTLY (QJR-2 adds
    NOTHING new at top level — journal exists since QJR-1; the QJR-1 V-10
    law, minus its '+journal' delta which already landed).
  - Byte-identical vs /tmp/qjr2_pre_config.json: regionC.quest (ALL keys
    incl. rescuedToast/rescuePrompt/hudText), and journal.button +
    journal.openKey; journal.text = pre values + EXACTLY the two new keys.
  - warEffort.ladder keys AND values byte-identical; inventoryUI keys AND
    values byte-identical (the QJR-1 V-10 probe set re-proven against this
    round's baseline).

V-15 NO-GIT audit (final) — `git -C /tmp/wh-worldfeat rev-parse HEAD` equals
  the V-0 sha; `git log -1 --format=%H` equals it; `git status --porcelain`
  shows NO NEW staged rows vs the V-0-time recording; `git diff --cached`
  EMPTY; no commit/push/stage/branch by this validator (read-only git only).
  THEN re-sha ALL V-0 files + the whole zero-touch set; the report carries
  the pre/post sha table; any unexpected drift = FAIL with the sha pair
  quoted. A11 is bound HERE and in the Header: this validation used node
  one-shots only, no harness runs, no headless browser, no browser
  automation; the acceptance bar remains Nicko's playtest.

## Harness law (all V-groups; journal.js AND npc.js are DOM/quest modules)

- FAKE STUBS, same pattern as qjr-1-buildcard STAGE 6: `global.window =
  global;` + a minimal recorder document. document.createElement(tag)
  returns recorders: tagName, className, classList {add/remove/contains,
  journaled}, style object (every write journaled, 'display' readable),
  children[] + appendChild/removeChild/insertBefore recorders,
  addEventListener REGISTRY (the test dispatches stored fns with spy events
  carrying preventDefault/stopPropagation spies AND an explicit target
  field), type/value/placeholder/tabIndex plain fields, textContent.
  document.getElementById returns dedicated recorders for 'wh-root',
  'wh-hud' (npc.js needs both) and a default recorder otherwise;
  document.body is a recorder root. The recorder must ALSO accept an
  <input> node (tagName 'input') whose value/placeholder/type are set by
  journal.js — no DOM globals, no THREE shim: if journal.js or npc.js
  touches THREE on the tested paths, the absent global FAILS visibility.
- LOAD ORDER: window stub -> REAL prototype/js/CONFIG.js (require;
  global.window={} -> window.WH_CONFIG present) -> the module under test
  (journal.js and/or npc.js). Journal-only groups set a STUB
  window.WH_NPC = {questState: fn returning a settable var} BEFORE journal
  calls; npc.js groups use the REAL WH_NPC module and let journal.js read
  IT (restore quest via WH_NPC.restoreQuest FIRST, then journal.update()).
  fake game object (single instance shared by both inits for the V-4/V-5
  groups): {regionManager:{logic:{activeId: <settable, WH_CONFIG.regionC
  .id or .regionD.id>}}, player:{state:'alive', inputSuspended:false,
  pos:{x: sarc.x, z: sarc.z + 1}, setInputSuspended spy}, inventoryUI:
  {blocked:false, toastLog:[], toast(t){this.toastLog.push(t);}},
  dayNight:{day:<settable int 7 for npc groups, 4 for journal groups>},
  scene NOT needed on the tested paths (npc.update/build are never called;
  no THREE is constructed)}. The one-shot re-derives the sarcophagus
  coords from CONFIG.regionD.props (asset === 'stoneSarcophagus'), never
  hardcodes (-201,-185 beyond the cross-check).
- One-shot files authored FRESH by the validator at validation time as
  /tmp/qjr2_<group>.js, run via `node /tmp/qjr2_<group>.js` with cwd =
  /tmp/wh-worldfeat; each prints PASS/FAIL per assertion, exits non-zero on
  any FAIL. This valspec prescribes the ASSERTIONS; the validator authors
  the code fresh. NOTHING is written inside the worktree except the verdict
  report; scratch scripts, the pre-snapshot, and pre/post probes live in
  /tmp. NO harness runs, NO headless browser, NO server, NO fetch (A11).

## Verdict file

Write io/reports/2026-11-06-qjr-2-journal-dialogue-search-validation.md
(worktree; the ONLY worktree write): FIRST line is the one-line
`VERDICT: PASS` or `VERDICT: FAIL` banner, then per-group PASS/FAIL (V-0,
V-0b, V-1..V-15) with the actual node one-shot output lines, the pre/post
sha tables (V-0 + V-0b), the marker counts (V-13), the landing-gate timings
(poll start, first-change minute), and — on any FAIL — every failed check
with observed vs expected. No partial PASS: any FAILing group = FAIL
verdict. Cross-bind: V-0 sha recording is mandatory FIRST (before reading
any landed code); if two readings of the same file happen at different
times, both go in the report and the SECOND is the validated one, explicitly
labeled. A1-A11 bind map: A1=V-4, A2=V-5, A3=V-6, A4=V-7, A5=V-8, A6=V-9
(with V-2 as its CONFIG foundation), A7=V-10+V-11+V-12+V-14, A8=V-1, A9=V-3
(with the V-9 no-second-accent-in-code cross-read), A10=V-13, A11=Header +
Harness law + V-15; the landing gate feeds every group; V-15 closes the
round.
