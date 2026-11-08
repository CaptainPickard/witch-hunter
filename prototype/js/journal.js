// QJR-1 journal core (build card: io/specs/qjr-1-buildcard.md, 2026-11-06).
// Pure DOM module: HUD journal button + quest journal panel. No THREE, no
// scene roots, no new assets. Every player-facing string lives in
// window.WH_CONFIG.journal.text (A9 law); ids/classes/events are card-allowlisted.
// QJR-4 (io/specs/qjr-4-bestiary-spec.md): a second text tab (JOURNAL |
// BESTIARY) inside the same panel - journal.js still owns the panel DOM and
// hands the codex module its page mount only; codex labels ride
// CONFIG.journal.bestiary.text (A9). J / Esc / death law unchanged.
(function () {
  'use strict';

  var CFG = window.WH_CONFIG.journal;

  // QJR-4: the codex tab's labels live in the new CONFIG.journal.bestiary
  // block (A9); a missing module / block simply means the panel stays a
  // single-tab journal (pre-QJR-4 shape byte-equal).
  var BC = window.WH_CONFIG.journal.bestiary;

  // Same shape as the camp.js buildMenu helper.
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined && text !== null) n.textContent = text;
    return n;
  }

  var game = null, born = false, entries = [], open = false;
  var seedDone = false, btn = null, rootEl = null, pageEl = null;
  var searchEl = null, query = '';   // QJR-2: client-only filter state, reset on open
  // QJR-4: the active page tab; 'journal' until the BESTIARY tab is picked.
  var tab = 'journal', tabJournalEl = null, tabBestiaryEl = null, bestPageEl = null;

  function toast(t) {
    if (game && game.inventoryUI && typeof game.inventoryUI.toast === 'function') {
      game.inventoryUI.toast(t);
    }
  }

  // QJR-4: the ORIGINAL buildJournalRows body, renamed under the dispatcher
  // (same loop as QJR-2 search; callers unchanged below).
  function buildJournalRows() {
    if (!pageEl) return;
    pageEl.textContent = '';
    var q = query.toLowerCase();   // QJR-2 client-only search
    var shown = 0;
    if (!entries.length) {
      pageEl.appendChild(el('div', 'journal-empty', CFG.text.empty));
      return;
    }
    entries.forEach(function (e) {
      if (q && (e.title + ' ' + e.body + ' ' + e.source)
        .toLowerCase().indexOf(q) < 0) return;
      shown++;
      var row = el('div', 'journal-row');
      row.appendChild(el('div', 'journal-row-title', e.title));
      row.appendChild(el('div', 'journal-row-day', CFG.text.dayStamp
        .replace('{day}', String(e.day))
        .replace('{source}', e.source || '')));
      row.appendChild(el('div', 'journal-row-body', e.body));   // QJR-2: body line now visible
      pageEl.appendChild(row);
    });
    if (!shown) pageEl.appendChild(el('div', 'journal-nomatch', CFG.text.searchNoMatch));
  }

  // QJR-4: the codex page render - the module hands back filled rows for the
  // page mount journal.js provides (bestiary.js never touches document.body).
  function renderBestPage() {
    if (!bestPageEl) return;
    bestPageEl.textContent = '';
    if (window.WH_BESTIARY && typeof window.WH_BESTIARY.renderPage === 'function') {
      window.WH_BESTIARY.renderPage(bestPageEl, query.toLowerCase());
    }
  }

  function renderCurrentPage() {
    if (tab === 'bestiary') renderBestPage();
    else buildJournalRows();
  }

  // QJR-4: the tab + shared-page dispatcher every existing caller
  // (search input, openPanel, append, restore, unlock edge) already hits;
  // one shared filter feeds both pages (spec 2.7: search applies to the
  // codex tab too, nomatch grammar per page).
  function rebuildRows() {
    if (tab !== 'journal' && tab !== 'bestiary') tab = 'journal';
    if (pageEl) pageEl.style.display = (tab === 'journal') ? '' : 'none';
    if (bestPageEl) bestPageEl.style.display = (tab === 'bestiary') ? '' : 'none';
    renderCurrentPage();
    refreshTabs();
  }

  function openPanel() {
    if (!born || open) return;
    open = true;
    if (tab === 'bestiary' && !(window.WH_BESTIARY && window.WH_BESTIARY.isBorn())) {
      tab = 'journal';              // spec 2.7: codex tab hides until born
    }
    rootEl.classList.add('open');
    query = '';
    if (searchEl) searchEl.value = '';
    rebuildRows();
    if (game) {
      if (game.inventoryUI) game.inventoryUI.blocked = true;
      if (game.player && game.player.setInputSuspended) game.player.setInputSuspended(true);
    }
  }

  function closePanel() {
    if (!open) return;
    open = false;
    // QJR-4: the codex tab is never left armed while the panel is down.
    if (window.WH_BESTIARY && typeof window.WH_BESTIARY.setOpen === 'function') {
      window.WH_BESTIARY.setOpen(false);
    }
    rootEl.classList.remove('open');
    if (game && game.inventoryUI) game.inventoryUI.blocked = false;
    if (game && game.player && game.player.setInputSuspended) game.player.setInputSuspended(false);
  }

  // Returns a clean int day or null when the value must be dropped.
  function normalizeDay(day) {
    var d = (day === undefined || day === null)
      ? ((game && game.dayNight) ? game.dayNight.day : 0)
      : Number(day);
    if (!isFinite(d)) return null;
    d = Math.round(d);
    if (d < 0) return null;
    return d;
  }

  // append(id, title, body, day, source): newest-FIRST; dedupe by id; seed stays silent.
  function append(id, title, body, day, source) {
    var i, sid = String(id);
    for (i = 0; i < entries.length; i++) {
      if (entries[i].id === sid) return;
    }
    var d = normalizeDay(day);
    if (d === null) return;
    entries.unshift({
      id: sid, title: String(title), body: String(body),
      day: d, source: String(source)
    });
    rebuildRows();
    if (seedDone) toast(CFG.text.toastNew + title);
    seedDone = true;
  }

  function capture() {
    return {
      born: born,
      entries: entries.map(function (e) {
        return { id: e.id, title: e.title, body: e.body, day: e.day, source: e.source };
      })
    };
  }

  // restore(block): never seeds, never toasts. Malformed rows are dropped.
  function restore(block) {
    entries = [];
    var wasBorn = false;
    if (block && typeof block === 'object') {
      if (block.born === true) wasBorn = true;
      if (Array.isArray(block.entries)) {
        block.entries.forEach(function (r) {
          if (!r || typeof r !== 'object') return;
          var d = Number(r.day);
          if (!isFinite(d)) return;
          d = Math.round(d);
          if (d < 0) return;
          entries.push({
            id: String(r.id), title: String(r.title), body: String(r.body),
            day: d, source: String(r.source)
          });
        });
      }
    }
    // OLD-SAVE LAW: a save predating the journal still unlocks if the quest is underway.
    if (!wasBorn && window.WH_NPC && window.WH_NPC.questState() !== 'available') wasBorn = true;
    born = wasBorn;
    rebuildRows();
    if (btn) btn.style.display = born ? '' : 'none';
  }

  // Called every frame: unlock edge + death law (AM-1: player.state === 'dead').
  function update(dt) {
    if (!born && window.WH_NPC && window.WH_NPC.questState() !== 'available') {
      born = true;
      seedDone = false;
      append('quest-findDaughter', CFG.text.seedTitle, CFG.text.seedBody, undefined, CFG.text.seedSource);
      if (btn) btn.style.display = '';
    }
    // QJR-4: birth-edge re-render - once the codex is born, the BESTIARY tab
    // may appear in the (open) tab row; the visibility check itself guards
    // this branch (refreshTabs hides or shows it; page render only on the
    // bestiary tab).
    if (open && tabBestiaryEl && tabBestiaryEl.style.display === 'none' &&
      window.WH_BESTIARY && window.WH_BESTIARY.isBorn()) {
      refreshTabs();
      if (tab === 'bestiary') renderCurrentPage();
    }
    if (open && game && game.player && game.player.state === 'dead') closePanel();
  }

  // QJR-4: sync the two tab buttons with DOM state (no per-frame work:
  // called only from rebuildRows, which itself is event- and edge-driven).
  function refreshTabs() {
    if (!tabJournalEl || !tabBestiaryEl) return;
    var b = BC || { text: {} };
    tabJournalEl.textContent = (BC && BC.text && BC.text.tabJournal) ? BC.text.tabJournal : CFG.text.tabJournal;
    tabBestiaryEl.textContent = (BC && BC.text && BC.text.tabBestiary) ? BC.text.tabBestiary : CFG.text.tabJournal;
    var showBest = !!(window.WH_BESTIARY && window.WH_BESTIARY.isBorn() &&
      BC && BC.text && BC.text.tabBestiary);
    tabBestiaryEl.style.display = showBest ? '' : 'none';
    tabJournalEl.classList.toggle('active', tab !== 'bestiary');
    tabBestiaryEl.classList.toggle('active', tab === 'bestiary');
  }

  // QJR-4: build the two text tabs (inv-tab grammar, pointerdown TC-FIX1
  // pattern: focus/activation, preventDefault, stopPropagation, tabIndex -1).
  function buildTabs(panel) {
    if (!BC || !window.WH_BESTIARY) return;   // no module -> single-tab journal
    var row = el('div', 'wh-journal-tabs');
    function pick(name) {
      if (name === 'bestiary' && !window.WH_BESTIARY.isBorn()) return;
      tab = name;
      rebuildRows();
      // keep the module's isOpen() in step with the tab the journal shows
      window.WH_BESTIARY.setOpen(tab === 'bestiary');
    }
    tabJournalEl = el('button', 'wh-journal-tab', '');
    tabJournalEl.type = 'button';
    tabJournalEl.tabIndex = -1;
    tabJournalEl.textContent = BC.text.tabJournal;
    tabJournalEl.addEventListener('pointerdown', function (e) {
      e.preventDefault();
      e.stopPropagation();
      pick('journal');
    });
    ['mousedown', 'click', 'contextmenu'].forEach(function (t) {
      tabJournalEl.addEventListener(t, function (e) {
        e.preventDefault();
        e.stopPropagation();
      });
    });
    tabBestiaryEl = el('button', 'wh-journal-tab', '');
    tabBestiaryEl.type = 'button';
    tabBestiaryEl.tabIndex = -1;
    tabBestiaryEl.style.display = 'none';
    tabBestiaryEl.textContent = BC.text.tabBestiary;
    tabBestiaryEl.addEventListener('pointerdown', function (e) {
      e.preventDefault();
      e.stopPropagation();
      pick('bestiary');
    });
    ['mousedown', 'click', 'contextmenu'].forEach(function (t) {
      tabBestiaryEl.addEventListener(t, function (e) {
        e.preventDefault();
        e.stopPropagation();
      });
    });
    row.appendChild(tabJournalEl);
    row.appendChild(tabBestiaryEl);
    panel.appendChild(row);
    refreshTabs();   // QJR-4: settle the labels/active states at build time
  }

  function init(g) {
    game = g;

    btn = el('button', '', CFG.button.glyph + ' ' + CFG.button.label);
    btn.id = 'wh-journal-btn';
    btn.type = 'button';
    btn.tabIndex = -1;
    btn.title = 'Journal (J)';
    btn.style.left = CFG.button.left + 'px';
    btn.style.bottom = CFG.button.bottom + 'px';
    btn.style.display = 'none';
    btn.addEventListener('pointerdown', function (e) {
      e.preventDefault();
      e.stopPropagation();
      openPanel();
    });
    ['mousedown', 'click', 'contextmenu'].forEach(function (t) {
      btn.addEventListener(t, function (e) {
        e.preventDefault();
        e.stopPropagation();
      });
    });
    document.body.appendChild(btn);

    rootEl = el('div');
    rootEl.id = 'wh-journal';
    var panel = el('div', 'journal-panel');
    panel.appendChild(el('div', 'inv-title', CFG.text.title));
    panel.appendChild(el('div', 'journal-rule'));
    buildTabs(panel);   // QJR-4: JOURNAL | BESTIARY tab row (no module = skipped)
    var searchWrap = el('div', 'journal-search');
    searchEl = el('input');
    searchEl.type = 'text';
    searchEl.id = 'wh-journal-search';
    searchEl.placeholder = CFG.text.searchPlaceholder;
    searchEl.tabIndex = -1;
    searchEl.addEventListener('input', function () {
      query = searchEl.value;
      renderCurrentPage();   // QJR-4: the shared filter feeds both pages
    });
    // TC-FIX1 (F4): pointerdown focus so the virtual keyboard opens reliably
    // on touch devices (the layer's global stopPropagation noise can starve
    // the default focus path). Deliberately NOT preventDefault'ed; keydown
    // guard + Escape behavior below are byte-identical to the QJR-1 build.
    searchEl.addEventListener('pointerdown', function () {
      searchEl.focus({ preventScroll: true });
    });
    searchWrap.appendChild(searchEl);
    panel.appendChild(searchWrap);
    pageEl = el('div', 'journal-page');
    panel.appendChild(pageEl);
    // QJR-4: the codex page mount - same .journal-page grammar, a
    // .bestiary-page modifier; the module fills it via renderPage.
    bestPageEl = el('div', 'journal-page bestiary-page');
    bestPageEl.style.display = 'none';
    panel.appendChild(bestPageEl);
    panel.appendChild(el('div', 'inv-hint', CFG.text.hint));
    if (BC && BC.text && BC.text.hint) {
      panel.appendChild(el('div', 'inv-hint bestiary-hint', BC.text.hint));
    }
    refreshTabs();   // QJR-4: initial tab labels + visibility
    rootEl.appendChild(panel);
    var r = document.getElementById('wh-root');
    (r || document.body).appendChild(rootEl);

    document.addEventListener('keydown', function (e) {
      if (e.repeat) return;
      var inSearch = !!(open && searchEl && document.activeElement === searchEl);   // QJR-2
      if (e.code === CFG.openKey && born && !inSearch) {
        if (open) closePanel();
        else openPanel();
        e.preventDefault();
      } else if (e.code === 'Escape' && open) {
        closePanel();
        e.preventDefault();
      }
    });
  }

  function isBorn() { return born; }
  function isOpen() { return open; }

  window.WH_JOURNAL = {
    init: init,
    update: update,
    capture: capture,
    restore: restore,
    append: append,
    isBorn: isBorn,
    isOpen: isOpen,
    closeForTest: closePanel
  };
})();
