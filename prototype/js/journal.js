// QJR-1 journal core (build card: io/specs/qjr-1-buildcard.md, 2026-11-06).
// Pure DOM module: HUD journal button + quest journal panel. No THREE, no
// scene roots, no new assets. Every player-facing string lives in
// window.WH_CONFIG.journal.text (A9 law); ids/classes/events are card-allowlisted.
(function () {
  'use strict';

  var CFG = window.WH_CONFIG.journal;

  // Same shape as the camp.js buildMenu helper.
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined && text !== null) n.textContent = text;
    return n;
  }

  var game = null, born = false, entries = [], open = false;
  var seedDone = false, btn = null, rootEl = null, pageEl = null;

  function toast(t) {
    if (game && game.inventoryUI && typeof game.inventoryUI.toast === 'function') {
      game.inventoryUI.toast(t);
    }
  }

  function rebuildRows() {
    if (!pageEl) return;
    pageEl.textContent = '';
    if (!entries.length) {
      pageEl.appendChild(el('div', 'journal-empty', CFG.text.empty));
      return;
    }
    entries.forEach(function (e) {
      var row = el('div', 'journal-row');
      row.appendChild(el('div', 'journal-row-title', e.title));
      row.appendChild(el('div', 'journal-row-day', CFG.text.dayStamp
        .replace('{day}', String(e.day))
        .replace('{source}', e.source || '')));
      pageEl.appendChild(row);
    });
  }

  function openPanel() {
    if (!born || open) return;
    open = true;
    rootEl.classList.add('open');
    rebuildRows();
    if (game) {
      if (game.inventoryUI) game.inventoryUI.blocked = true;
      if (game.player && game.player.setInputSuspended) game.player.setInputSuspended(true);
    }
  }

  function closePanel() {
    if (!open) return;
    open = false;
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
    if (open && game && game.player && game.player.state === 'dead') closePanel();
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
    pageEl = el('div', 'journal-page');
    panel.appendChild(pageEl);
    panel.appendChild(el('div', 'inv-hint', CFG.text.hint));
    rootEl.appendChild(panel);
    var r = document.getElementById('wh-root');
    (r || document.body).appendChild(rootEl);

    document.addEventListener('keydown', function (e) {
      if (e.repeat) return;
      if (e.code === CFG.openKey && born) {
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
