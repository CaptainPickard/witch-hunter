# QJR-1 BUILD CARD — journal core (Devbot lean dispatch; consolidated contract)

Worktree: /tmp/wh-worldfeat (branch feat/world-visuals, HEAD dd93ad8). Repo root
/tmp/wh-worldfeat. DO NOT read the big spec files — this card is complete; on
conflict the card wins and you disclose it. Code FIRST, no narration. Budget:
max ~30 tool calls total, then stop.

## Laws (hard)
- NO-GIT: never git add/commit/push/stage/branch. Read-only status/diff ok.
- Touch ONLY: prototype/js/journal.js (NEW), prototype/js/CONFIG.js, prototype/js/game.js,
  prototype/index.html, prototype/style.css. ZERO-TOUCH everything else
  (npc.js/wareffort.js/save.js/camp.js/chest.js/cooking.js/player.js sha-pinned).
- No harness runs, no headless browser, no browser automation. Node one-shots only.
- Every player-facing string lives in CONFIG.journal.text (A9 law: journal.js
  contains no quoted string that is not a CONFIG key read, an id/class/event
  name listed here, or code). id/class/event allowlist: 'wh-journal-btn',
  'wh-journal', 'open', 'journal-panel', 'journal-rule', 'journal-page',
  'journal-row', 'journal-row-title', 'journal-row-day', 'journal-empty',
  'inv-title', 'inv-hint', 'pointerdown', 'mousedown', 'click', 'contextmenu',
  'keydown', 'KeyJ', 'Escape', 'use strict', 'none', '', 'click' etc.
- No new scene roots / THREE objects. Pure DOM module. No red, no gradients,
  no second accent (amber #d8b24a only), no new assets.

## STAGE 1 — write prototype/js/journal.js (NEW file)

House IIFE: `(function () { 'use strict';` ... `})();` with local
`var CFG = window.WH_CONFIG.journal;` and an `el(tag, cls, text)` helper
(same as js/camp.js buildMenu). State vars: game=null, born=false,
entries=[], open=false, seedDone=false, btn=null, rootEl=null, pageEl=null.
Entries rows: `{ id:String, title:String, body:String, day:int, source:String }`
newest-FIRST (unshift). Exports exactly:

    window.WH_JOURNAL = { init: init, update: update, capture: capture,
      restore: restore, append: append, isBorn: isBorn, isOpen: isOpen,
      closeForTest: closePanel };

init(g):
- game = g. Build btn: el('button', '', CFG.button.glyph + ' ' + CFG.button.label);
  btn.id='wh-journal-btn'; btn.type='button'; btn.tabIndex=-1;
  btn.title='Journal (J)'; btn.style.left=CFG.button.left+'px';
  btn.style.bottom=CFG.button.bottom+'px'; btn.style.display='none';
  pointerdown -> e.preventDefault + stopPropagation + openPanel();
  swallow ['mousedown','click','contextmenu'] (preventDefault+stopPropagation).
  document.body.appendChild(btn).
- Build rootEl: el('div'); rootEl.id='wh-journal'; panel el('div','journal-panel');
  panel children in order: el('div','inv-title',CFG.text.title),
  row el('div','journal-rule'), page el('div','journal-page') (keep pageEl ref),
  el('div','inv-hint',CFG.text.hint). document.getElementById('wh-root').appendChild(rootEl).
  (If #wh-root missing in a test harness, appendChild must still not throw:
  guard `var r=document.getElementById('wh-root'); (r||document.body).appendChild(rootEl);`)
- One document 'keydown' listener: if e.repeat return; if e.code===CFG.openKey
  and born -> toggle panel (openPanel/closePanel), e.preventDefault; else if
  e.code==='Escape' and open -> closePanel, e.preventDefault. When !born the
  KeyJ branch must do NOTHING (no preventDefault).

update(dt): called every frame.
- UNLOCK EDGE: `if (!born && window.WH_NPC && window.WH_NPC.questState() !== 'available')`
  -> born=true; seedDone=false; append(CFG.text.seedTitle, CFG.text.seedBody,
  undefined, CFG.text.seedSource) with id 'quest-findDaughter' (see append
  signature below); reveal button (btn.style.display=''). Do NOT open the panel.
- DEATH LAW (IO amendment AM-1): player death is `game.player.state === 'dead'`
  (player.js:45 — 'alive' | 'dying' | 'dead'; there is NO .dead flag).
  `if (open && game && game.player && game.player.state === 'dead') closePanel();`

append(id, title, body, day, source):
- DEDUPE first: if entries has a row with the same id -> return (no toast).
- Normalize day: d = (day===undefined||day===null) ? ((game&&game.dayNight)?game.dayNight.day:0) : Number(day);
  if (!isFinite(d)) return (silently DROP); d=Math.round(d); if (d<0) return (DROP).
- entries.unshift({id:String(id),title:String(title),body:String(body),day:d,source:String(source)});
- rebuildRows() if pageEl exists.
- Toast law: if (seedDone) toast(CFG.text.toastNew + title); then seedDone=true.
  (The seed stays silent: at the seed call seedDone is still false. Every later
  append toasts once. restore() never toasts and never appends.)

capture():
    return { born: born, entries: entries.map(function (e) {
      return { id: e.id, title: e.title, body: e.body, day: e.day, source: e.source }; }) };
NO aliasing (fresh objects; valspec mutates the payload and re-checks live).

restore(block):
- entries=[]; var wasBorn=false;
- if (block && typeof block==='object'): if (block.born===true) wasBorn=true;
  if (Array.isArray(block.entries)) block.entries.forEach(function(r){
    if (!r || typeof r!=='object') return;                       // null/'garbage' dropped
    var d=Number(r.day); if (!isFinite(d)) return; d=Math.round(d); if (d<0) return;
    entries.push({id:String(r.id),title:String(r.title),body:String(r.body),day:d,source:String(r.source)}); });
- OLD-SAVE LAW: if (!wasBorn && window.WH_NPC && window.WH_NPC.questState() !== 'available')
  wasBorn=true.  born=wasBorn;
- rebuildRows() if pageEl exists; btn visibility mirrors born ('' or 'none').
- NEVER seeds the entry and NEVER toasts.

openPanel(): if (!born || open) return; open=true; rootEl.classList.add('open');
  rebuildRows(); if (game) { if (game.inventoryUI) game.inventoryUI.blocked=true;
  if (game.player && game.player.setInputSuspended) game.player.setInputSuspended(true); }
closePanel(): if (!open) return; open=false; rootEl.classList.remove('open');
  if (game && game.inventoryUI) game.inventoryUI.blocked=false;
  if (game && game.player && game.player.setInputSuspended) game.player.setInputSuspended(false);
isBorn(): return born;   isOpen(): return open;

rebuildRows(): pageEl.textContent=''; if (!entries.length) pageEl.appendChild(
  el('div','journal-empty',CFG.text.empty)); else entries.forEach(function(e){
  var row=el('div','journal-row'); row.appendChild(el('div','journal-row-title',e.title));
  row.appendChild(el('div','journal-row-day',CFG.text.dayStamp
    .replace('{day}', String(e.day)).replace('{source}', e.source||'')));
  pageEl.appendChild(row); });
(CONFIG amendment AM-2: CFG.journal.text.dayStamp = 'Day {day} - {source}' —
keeps A9 clean; row day line = that template.)

toast(t): if (game && game.inventoryUI && typeof game.inventoryUI.toast==='function')
  game.inventoryUI.toast(t);

## STAGE 2 — CONFIG.js: add ONLY this block

Insert immediately AFTER the `window.WH_CONFIG.inventoryUI = { ... };` block
closes (anchor: the line `  openButton: { enabled: true, label: 'INV', left: 16, bottom: 20 }`
then `};` ; insert after that `};`, before the `// L1 (2026-10-07` comment):

    // QJR-1 journal core (Nicko MorROWIND order 2026-11-06; all PROPOSED,
    // Nicko tunes). Sits in the HUD row right of INV (16) and CAMP (76).
    window.WH_CONFIG.journal = {
      button: { glyph: '☰', label: 'JOURNAL', left: 152, bottom: 20 },
      openKey: 'KeyJ',
      text: {
        title: 'JOURNAL',
        empty: 'No entries yet. The road will give you words.',
        dayStamp: 'Day {day} - {source}',
        seedTitle: "The farmer's daughter",
        seedBody: "Farmer Aldric: the Old King's Barrow, west past the dead trees. Bring her home.",
        seedSource: 'Farmer Aldric',
        toastNew: 'Journal: ',
        hint: 'Esc close'
      }
    };

Zero changes anywhere else in CONFIG.js (warEffort.ladder / regionC.quest /
inventoryUI byte-identical).

## STAGE 3 — game.js: exactly FIVE added lines, zero removals

Each line verbatim (indentation matches neighbors at each anchor):
1. Directly after the line `      if (window.WH_AMBUSH) window.WH_AMBUSH.init(game);`:
       `      if (window.WH_JOURNAL) window.WH_JOURNAL.init(game);   // QJR-1: journal core`
2. Directly after `      if (window.WH_WarEffort) data.warEffort = window.WH_WarEffort.capture();`:
       `      if (window.WH_JOURNAL) data.journal = window.WH_JOURNAL.capture();   // QJR-1`
3. Directly after `        if (window.WH_WarEffort) stored.warEffort = window.WH_WarEffort.capture();`:
       `        if (window.WH_JOURNAL) stored.journal = window.WH_JOURNAL.capture();   // QJR-1`
4. Directly after `      if (window.WH_WarEffort) window.WH_WarEffort.restore(data.warEffort);` (BEFORE baseRestore — questState is restored earlier in the chain):
       `      if (window.WH_JOURNAL) window.WH_JOURNAL.restore(data && data.journal);   // QJR-1`
5. Directly after `    if (window.WH_NPC) window.WH_NPC.update(dt);`:
       `    if (window.WH_JOURNAL) window.WH_JOURNAL.update(dt);   // QJR-1`

## STAGE 4 — index.html: one line

After `<script src="js/wareffort.js"></script>` add:
    `<script src="js/journal.js"></script>`

## STAGE 5 — style.css: append ONLY at EOF

    /* QJR-1 journal (js/journal.js): darkwood frame + parchment page insert;
       single amber rule accent. Button mirrors the camp button body. */
    #wh-journal-btn {
      position: fixed;
      z-index: 46;
      min-width: 44px;
      height: 30px;
      padding: 0 8px;
      font-family: monospace;
      font-size: 12px;
      letter-spacing: 2px;
      color: #c9bf9f;
      background: #1a1510;
      border: 2px solid #4a4034;
      box-shadow: 0 0 0 2px #14110e, inset 0 0 0 1px #2a231b;
      cursor: pointer;
      display: block;
      user-select: none;
      touch-action: manipulation;
    }
    #wh-journal-btn:hover { border-color: #c9a94a; }
    #wh-journal { position:absolute; inset:0; display:none; align-items:center;
      justify-content:center; background: rgba(5,4,3,0.55); z-index:20;
      font-family:monospace; color:#d8d2c0; image-rendering:pixelated;
      user-select:none; }
    #wh-journal.open { display:flex; }
    .journal-panel { width:320px; max-height:70vh; display:flex; flex-direction:column; }
    .journal-rule { height:2px; background:#d8b24a; margin:6px 0 10px; }
    .journal-page { background:#e3dcc4; color:#221c15; border:2px solid #4a4034;
      box-shadow: inset 0 0 0 2px #d3c8a8; padding:10px 12px; overflow-y:auto;
      flex:1 1 auto; min-height:0; }
    .journal-row { padding:6px 2px; border-bottom:1px solid #b7ac8f; }
    .journal-row:last-child { border-bottom:none; }
    .journal-row-title { font-size:12px; letter-spacing:1px; color:#2a231b; }
    .journal-row-day { font-size:10px; color:#6a6350; font-style:italic; margin-top:2px; }
    .journal-empty { color:#6a6350; font-style:italic; font-size:11px; padding:6px 2px; }

## STAGE 6 — node self-checks (authored fresh under /tmp, <= 6 files)

Harness: `global.window = global;` + minimal recorder document
(createElement returns {tagName,className,children[],style:{},classList:
{add,remove,contains},appendChild,addEventListener,calls log,textContent}),
document.getElementById returns recorders ('wh-root'), document.body recorder;
fake game = { inventoryUI:{blocked:false,toastLog:[]}, player:{state:'alive',
suspendLog:[], setInputSuspended:function(v){this.suspendLog.push(v);} },
dayNight:{day:3} }; fake window.WH_NPC = { questState: function(){return qs;} }.
Load journal.js AFTER CONFIG stub: set `window.WH_CONFIG={journal:{...copy of the
STAGE 2 block...}}` inline in the harness. Assertions:
- V2 edge: init; update() while qs='available' -> isBorn()=false; qs='active';
  update() -> isBorn()=true, capture().entries.length=1, entries[0].id==='quest-findDaughter', day 3.
- V3 single-fire: 50 more update() -> still 1.
- V4 dedupe/toast: append('quest-findDaughter','t','b',undefined,'s') -> still 1
  and NO new toast; append('topic-wolf','Wolves','Big ones...',undefined,'Road')
  -> 2, capture().entries[0].id==='topic-wolf', toastLog has 1 new item prefixed 'Journal: '.
- V5 roundtrip+no-alias: c=capture(); restore(JSON.parse(JSON.stringify(c)));
  isBorn() still true; entries equal; mutate c.entries[0].title then capture()
  again -> live title unchanged (no aliasing).
- V6 malform: restore({born:true,entries:[null,'garbage',{id:'ok',title:'T',
  body:'B',day:2.7,source:'S'},{id:'n',title:'N',body:'B',day:-5,source:'S'},
  {id:'nan',title:'N',body:'B',day:NaN,source:'S'}]}) -> 1 row, day===3,
  crash-free; qs='active' + restore(undefined) -> born true, entries [];
  qs='available' + restore(undefined) -> born false.
- V7 panel: born state; fire btn pointerdown handler -> inventoryUI.blocked
  true, suspendLog last true; keydown Escape -> both reversed; open again,
  player.state='dead', update() -> closed, blocked false.
All must pass exit 0 with zero console errors.

## STAGE 7 — build

    cd /tmp/wh-worldfeat && python3 tools/build_v8.py        # exit 0 required
    grep -c 'QJR-1' prototype/builds/v8-playable.html         # >= 6
    grep -c 'wh-journal-btn' prototype/builds/v8-playable.html  # >= 2

## Report (final message)

Files changed + sha256sum each, node self-check PASS lines, build exit code,
marker counts, any card-deviation disclosure. NO git writes. Never claim
V-group PASS (Testerbot's job) — self-checks only.
