# QJR-2 BUILD CARD — journal dialogue capture + search (Devbot lean dispatch)

Worktree: /tmp/wh-worldfeat (branch feat/world-visuals, HEAD ef97f4c). Repo
root IS /tmp/wh-worldfeat. DO NOT read the big spec files — this card is
complete; on conflict the card wins and you disclose it. Code FIRST, no
narration. Budget: max ~30 tool calls total, then stop.

## Laws (hard)
- NO-GIT: never git add/commit/push/stage/branch. Read-only status/diff ok.
- Touch ONLY: prototype/js/journal.js, prototype/js/CONFIG.js,
  prototype/js/npc.js, prototype/style.css. ZERO-TOUCH everything else —
  esp. game.js, index.html, save.js, player.js, wareffort.js, camp.js,
  chest.js, cooking.js, inventory.js, region-manager.js, touch-controls.js,
  vendor/* (Testerbot byte-pins them against HEAD ef97f4c).
- No harness runs, no headless browser, no browser automation. Node one-shots
  only, authored fresh under /tmp, <= 5 files.
- Every new player-facing string lives in CONFIG.journal (A9 law). journal.js
  keeps QJR-1 laws: no new scene roots, no THREE, pure DOM.
- Palette law: appended CSS hex literals ONLY from the QJR-1 family set
  {'#d8b24a','#c9a94a','#4a4034','#1a1510','#14110e','#2a231b','#e3dcc4',
  '#d3c8a8','#b7ac8f','#c9bf9f','#6a6350','#221c15','#d8d2c0'}. Amber
  #d8b24a single accent. NO gradients, NO red, no new assets.
- Anchors: concept-04-tavern + concept-01-darkwood (darkwood/parchment/amber).
- Use the patch tool (targeted replaces) for journal.js / npc.js / CONFIG.js;
  style.css appends at EOF ONLY (bytes above EOF must stay byte-identical).
- Zero removed code lines in journal.js and CONFIG.js (removed lines, if any,
  comment-only). npc.js adds ~5 lines, removes none.

## STAGE 1 — CONFIG.js: extend window.WH_CONFIG.journal

Patch A — extend journal.text. The block currently ends:
    hint: 'Esc close'
  }
};
Replace with:
    hint: 'Esc close',
    searchPlaceholder: 'Search the journal...',
    searchNoMatch: 'Nothing in the journal matches.'
  },
  topics: {
    rescue: {
      id: 'rescue-findDaughter',
      title: "The farmer's daughter",
      body: 'Rescue: I found Aldric\'s daughter by the stone sarcophagus in the Old King\'s Barrow. She is safe and walking to her father\'s farm.',
      source: "Aldric's daughter"
    },
    complete: {
      id: 'quest-findDaughter-complete',
      title: "The farmer's daughter",
      body: "Aldric: 'She is home, hunter. You have given me back my world.' The road is quiet again.",
      source: 'Farmer Aldric'
    }
  }
};
The `hint: 'Esc close'` fragment appears in several CONFIG blocks — include
enough surrounding context in the patch old_string that the match is unique
(surrounding `dayStamp`/`seedSource`/`toastNew` lines above). NO other CONFIG
change of any kind: pre keys (title/empty/dayStamp/seedTitle/seedBody/
seedSource/toastNew/hint, button, openKey 'KeyJ') stay BYTE-IDENTICAL;
regionC (incl. quest.rescuedToast) untouched.

## STAGE 2 — npc.js: exactly 3 added anchors, 0 removed lines

Anchor 1 — top-of-module, directly after:
    var D = N.dialog;
add:
    var JT = window.WH_CONFIG.journal && window.WH_CONFIG.journal.topics;   // QJR-2

Anchor 2 — in openDialog, replace:
    if (quest === 'active' && rescued) { quest = 'complete'; lineIdx = -2; }
with:
    if (quest === 'active' && rescued) { quest = 'complete'; lineIdx = -2;
      if (JT && window.WH_JOURNAL) window.WH_JOURNAL.append(JT.complete.id, JT.complete.title, JT.complete.body, undefined, JT.complete.source);   // QJR-2
    }

Anchor 3 — in tryRescue, directly after:
    game.inventoryUI.toast(Q.rescuedToast);
add:
    if (JT && window.WH_JOURNAL) window.WH_JOURNAL.append(JT.rescue.id, JT.rescue.title, JT.rescue.body, undefined, JT.rescue.source);   // QJR-2

Exactly these three anchors; NO helper function, NO other npc.js line
(comment lines allowed nowhere). Total added lines <= 6.

## STAGE 3 — journal.js: five targeted patches, 0 removed code lines

Patch 1 — state head. Replace:
  var game = null, born = false, entries = [], open = false;
  var seedDone = false, btn = null, rootEl = null, pageEl = null;
with:
  var game = null, born = false, entries = [], open = false;
  var seedDone = false, btn = null, rootEl = null, pageEl = null;
  var searchEl = null, query = '';   // QJR-2: client-only filter state, reset on open

Patch 2 — openPanel. Replace:
    open = true;
    rootEl.classList.add('open');
    rebuildRows();
with:
    open = true;
    rootEl.classList.add('open');
    query = '';
    if (searchEl) searchEl.value = '';
    rebuildRows();

Patch 3 — rebuildRows. The EXACT original lines from
  function rebuildRows() {
down through
      row.appendChild(el('div', 'journal-row-day', CFG.text.dayStamp
must survive byte-identical. The only change INSIDE the forEach body is
appending one line after the .replace('{source}', e.source || '')); line:
      row.appendChild(el('div', 'journal-row-body', e.body));   // QJR-2: body line now visible
PLUS two additions to the function shell:
(a) directly after `pageEl.textContent = '';` insert:
    var q = query.toLowerCase();   // QJR-2 client-only search
    var shown = 0;
(b) at the very END of the forEach callback, before its closing `});`,
    wrap the row build with the filter: insert directly after
    `entries.forEach(function (e) {`:
      if (q && (e.title + ' ' + e.body + ' ' + e.source)
        .toLowerCase().indexOf(q) < 0) return;
      shown++;
and directly after the forEach closes (before the closing brace of
rebuildRows) insert:
    if (!shown) pageEl.appendChild(el('div', 'journal-nomatch', CFG.text.searchNoMatch));
(The QJR-1 `if (!entries.length)` empty-law block stays untouched — an empty
journal keeps the 'empty' wording; searchNoMatch shows only when entries
exist and none match.)

Patch 4 — init panel build. Replace:
    panel.appendChild(el('div', 'journal-rule'));
    pageEl = el('div', 'journal-page');
with:
    panel.appendChild(el('div', 'journal-rule'));
    var searchWrap = el('div', 'journal-search');
    searchEl = el('input');
    searchEl.type = 'text';
    searchEl.id = 'wh-journal-search';
    searchEl.placeholder = CFG.text.searchPlaceholder;
    searchEl.tabIndex = -1;
    searchEl.addEventListener('input', function () {
      query = searchEl.value;
      rebuildRows();
    });
    searchWrap.appendChild(searchEl);
    panel.appendChild(searchWrap);
    pageEl = el('div', 'journal-page');

Patch 5 — keydown guard. Replace:
    document.addEventListener('keydown', function (e) {
      if (e.repeat) return;
      if (e.code === CFG.openKey && born) {
with:
    document.addEventListener('keydown', function (e) {
      if (e.repeat) return;
      var inSearch = !!(open && searchEl && document.activeElement === searchEl);   // QJR-2
      if (e.code === CFG.openKey && born && !inSearch) {
(Escape branch untouched: Esc closes the panel even from inside the box.)

## STAGE 4 — style.css: APPEND ONLY at EOF

    /* QJR-2 journal dialogue capture + search (js/journal.js, js/npc.js):
       parchment scrap search pinned above the page, body lines, amber accents.
       Anchors: concept-04-tavern + concept-01-darkwood. */
    #wh-journal-search { width: 100%; box-sizing: border-box; margin: 8px 0;
      padding: 5px 8px; font-family: monospace; font-size: 11px;
      letter-spacing: 1px; color: #221c15; background: #d3c8a8;
      border: 2px solid #4a4034; box-shadow: inset 0 0 0 1px #e3dcc4;
      outline: none; }
    #wh-journal-search:focus { border-color: #d8b24a; }
    .journal-row-body { font-size: 11px; color: #3a3226; line-height: 1.45; }
    .journal-nomatch { color: #6a6350; font-style: italic; font-size: 11px;
      padding: 6px 2px; }
NOTE: '#3a3226' is NOT in the family set — replace it with '#2a231b' from the
set (body text ink). Final CSS uses ONLY family-set hexes.

## STAGE 5 — node self-checks (fresh under /tmp, <= 5 files)

Harness (QJR-1 STAGE-6 pattern): global.window = global; recorder document
(createElement -> {tagName,className,id,children[],style:{},classList,
appendChild,addEventListener,placeholder,type,value,textContent});
document.getElementById returns recorders; document.body recorder;
document.activeElement -> your harness sets it to the focused recorder.
Fake game: { inventoryUI:{blocked:false,toastLog:[],toast:function(t){this.
toastLog.push(t);}}, player:{state:'alive',inputSuspended:false,pos:{x:0,z:0},
suspendLog:[], setInputSuspended:function(v){this.suspendLog.push(v);}},
dayNight:{day:7}, regionManager:{logic:{activeId:'regionD'}} }.
Load REAL CONFIG.js with window stub BEFORE journal.js and npc.js. Stub
window.WH_ASSETS/WHSkeletonUtils/THREE minimally only if npc.js build-path
throws (do not stub beyond load safety; npc.update() is NOT driven — drive
the event seams directly). For npc.js rescue: restoreQuest requires
game.regionManager; rescuePrompt requires player pos within
CONFIG.regionC.quest.rescueInteractM of the stoneSarcophagus prop in
CONFIG.regionD.props (read the values from the real CONFIG — do not hardcode).

Checks (print PASS/FAIL lines, nonzero exit on any FAIL):
- S1 rescue: npc.init(game); journal.init(game);
  window.WH_NPC.restoreQuest({findDaughter:{state:'active',rescued:false}});
  window.WH_JOURNAL.update(); entries===1 (seed). Set player.pos to the
  sarcophagus coords; rescuePrompt()===true; tryRescue()===true;
  entries===2; entries[0].id==='rescue-findDaughter'; entries[0].day===7;
  entries[0].source===CONFIG.journal.topics.rescue.source; toastLog gained
  the rescuedToast AND one 'Journal: ' prefixed toast; tryRescue() again
  ===false (state gate), entries stay 2.
- S2 complete: reset entries via restore({born:true,entries:[]}) then
  restoreQuest({findDaughter:{state:'active',rescued:true}});
  window.WH_NPC.openDialog(); entries===1;
  entries[0].id==='quest-findDaughter-complete';
  window.WH_NPC.questState()==='complete'. openDialog() again (now
  lineIdx=-3 path) -> entries still 1.
- S3 search: journal with 3 entries (seed + two topics); open panel
  (fire the btn pointerdown handler); type: set activeElement=searchEl and
  fire searchEl 'input' handler with a title-matching token -> filtered
  rows; token matching only a body word -> row count == matches; a
  case-insensitive check (upper vs lower token same result); garbage token
  -> row 0 + a 'journal-nomatch' child on the page; re-open panel
  (closePanel then pointerdown) -> query reset: searchEl.value==='' and
  all rows visible again.
- S4 KeyJ guard + Esc: with panel open and activeElement===searchEl, fire
  document keydown {code:'KeyJ'} -> panel STILL open, no close; with
  activeElement moved away, KeyJ -> panel closed. Escape from inside the
  box -> panel closes; inventoryUI blocked=false; suspend ends.
- S5 regression: QJR-1 group — malformed restore drops (null/'garbage'/
  NaN/negative days), capture roundtrip no-alias, restore(undefined) with
  qs='active' -> born + no seed, qs='available' -> born false; dayStamp
  template string present in a rendered day row.

## STAGE 6 — build

    cd /tmp/wh-worldfeat && python3 tools/build_v8.py   # exit 0 required
    grep -c 'QJR-2' prototype/builds/v8-playable.html          # >= 4
    grep -c 'wh-journal-search' prototype/builds/v8-playable.html  # >= 2
    grep -c 'QJR-1' prototype/builds/v8-playable.html          # >= 6 (persists)
    git -C /tmp/wh-worldfeat status --porcelain        # ONLY the 4 files (+io/)

## Report (final message)

Files changed + sha256sum each, S1-S5 PASS lines, build exit code, marker
counts, any card-deviation disclosure. NO git writes. Never claim final
verdict (Testerbot's job) — self-checks only.
