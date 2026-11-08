// QJR-4 bestiary codex (io/specs/qjr-4-bestiary-spec.md, 2026-11-07).
// Kill-log + first-sight witness module: rides the journal panel (journal.js
// owns the panel DOM and hands this module its page mount). No THREE, no
// scene roots, no new assets, no texture, no GLB, no audio. Sight arrives as
// two guarded hand-offs from the enemy.js idle->aggro / idle->chase
// transition sites; kills arrive as one guarded hand-off from the takeDamage
// hp<=0 acknowledgement branch, after the onKilled loot hand-off (the same
// attribution law corpse loot already uses). Every player-facing string
// lives in window.WH_CONFIG.journal.bestiary (A9 law); zero literals here.
(function () {
  'use strict';

  // QJR-4: a double boot would stomp a live codex; only the first load binds.
  if (window.WH_BESTIARY) return;

  var CFG = window.WH_CONFIG.journal.bestiary;

  var game = null, born = false, tabActive = false;
  var witnessed = {};        // typeKey -> true (per-TYPE codex rows)
  var kills = {};            // typeKey -> int tally
  var days = {};             // typeKey -> first-seen day
  var seen = [];             // per-INSTANCE set (enemy object refs), Set semantics

  // Same shape as the journal.js / camp.js buildMenu helper.
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined && text !== null) n.textContent = text;
    return n;
  }

  function toast(t) {
    if (game && game.inventoryUI && typeof game.inventoryUI.toast === 'function') {
      game.inventoryUI.toast(t);
    }
  }

  function entryFor(typeKey) {
    if (!CFG || !CFG.entries) return null;
    return CFG.entries[typeKey] || null;
  }

  // Clean int day (journal normalizeDay shape), never negative.
  function currentDay() {
    var d = (game && game.dayNight) ? Number(game.dayNight.day) : 0;
    if (!isFinite(d)) return 0;
    d = Math.round(d);
    return d < 0 ? 0 : d;
  }

  // Per-TYPE witness: row unlock + first-seen day recorded once per save.
  function witness(typeKey, day) {
    if (!witnessed[typeKey]) {
      witnessed[typeKey] = true;
      if (days[typeKey] === undefined) days[typeKey] = day;
    }
  }

  // appendSight(enemy): hand-off from the enemy.js canPull transition sites
  // (idle->aggro / idle->chase). Idempotent per INSTANCE (the seen[] ref
  // set): re-aggroing the same live mob adds nothing. The row set is
  // per-TYPE, so a second instance of an already-witnessed type collapses
  // into the row it already has (fresh instances still register in seen[]
  // independently). Unknown / entryless types are silently ignored.
  function appendSight(enemy) {
    if (!enemy || typeof enemy !== 'object') return;
    if (enemy.type === undefined || enemy.type === null) return;
    var t = String(enemy.type);
    if (!entryFor(t)) return;
    for (var i = 0; i < seen.length; i++) {
      if (seen[i] === enemy) return;      // this instance is already on file
    }
    seen.push(enemy);
    var wasNewType = !witnessed[t];
    witness(t, currentDay());
    born = true;                          // the codex is born on first sight
    if (wasNewType && CFG.text) {
      toast(CFG.text.seenToast.replace('{title}', CFG.entries[t].title));
    }
  }

  // appendKill(enemy): hand-off from takeDamage's hp<=0 acknowledgement
  // branch, AFTER the onKilled loot hand-off - so withered minion deaths and
  // save-restored dead corpses (which bypass takeDamage) never tally. Kill
  // of an unseen type unlocks witnessed AND kills=1 in one event. Toast
  // cadence (spec 2.9): kill #1 uses the first-kill shape (whether the type
  // was previously only witnessed or unlocked by this very kill - the
  // killToastTitleUnseen shape governs, no duplicate toasts); later kills
  // toast only on every CONFIG killToastEvery-th (5, 10, 15...). Kill of a
  // type with no codex entry: totally silent, no born flip.
  function appendKill(enemy) {
    if (!enemy || typeof enemy !== 'object') return;
    if (enemy.type === undefined || enemy.type === null) return;
    var t = String(enemy.type);
    var entry = entryFor(t);
    if (!entry) return;
    witness(t, currentDay());
    kills[t] = (kills[t] || 0) + 1;
    born = true;
    var n = kills[t];
    var every = (CFG.killToastEvery && CFG.killToastEvery > 0) ? CFG.killToastEvery : 5;
    if (n === 1) {
      toast(CFG.text.killToastTitleUnseen.replace('{title}', entry.title));
    } else if (n > 1 && n % every === 0) {
      toast(CFG.text.killEveryLabel.replace('{title}', entry.title)
        .replace('{n}', String(n)));
    }
  }

  // update(dt): NOTHING is scanned per frame (spec 2.5). The map of
  // witnessed instances lives in appendSight's seen[] set and is touched
  // only by those event hand-offs; dt is ignored. The unlock edge and the
  // save roundtrip carry born; journal.js re-renders its tab row when the
  // isBorn() boolean changes (journal owns the DOM).
  function update(dt) { /* QJR-4: no per-frame scans */ }

  function sightOf(typeKey) {
    return !!witnessed[String(typeKey)];
  }

  function killsOf(typeKey) {
    var n = kills[String(typeKey)];
    return (typeof n === 'number' && n > 0) ? n : 0;
  }

  function capture() {
    var w = [], k = {}, d = {};
    Object.keys(witnessed).forEach(function (t) {
      if (witnessed[t] && entryFor(t)) w.push(t);
    });
    Object.keys(kills).forEach(function (t) {
      var n = kills[t];
      if (typeof n === 'number' && isFinite(n) && n > 0 && entryFor(t)) k[t] = n;
    });
    Object.keys(days).forEach(function (t) {
      var dv = days[t];
      if (typeof dv === 'number' && isFinite(dv) && entryFor(t)) d[t] = dv;
    });
    return { born: born, witnessed: w, kills: k, days: d };
  }

  // restore(block): additive-safe roundtrip (spec 2.6). Missing / malformed
  // block = fresh empty codex; malformed rows dropped (negative kill counts,
  // non-array witnessed, unknown types); the journal module receives its own
  // data.journal key untouched (independent blocks, A-7). Never seeds, never
  // toasts. A codex block with content counts as born even if the born flag
  // itself was lost.
  function restore(block) {
    witnessed = {}; kills = {}; days = {}; seen = [];
    var wasBorn = false;
    if (block && typeof block === 'object' && !Array.isArray(block)) {
      if (block.born === true) wasBorn = true;
      var w = block.witnessed;
      if (Array.isArray(w)) {
        w.forEach(function (t) {
          var k = (t === undefined || t === null) ? '' : String(t);
          if (k && entryFor(k)) witnessed[k] = true;
        });
      }
      var kn = block.kills;
      if (kn && typeof kn === 'object' && !Array.isArray(kn)) {
        Object.keys(kn).forEach(function (t) {
          var n = Number(kn[t]);
          if (!isFinite(n)) return;
          n = Math.floor(n);
          if (n < 0) return;
          if (n === 0) return;
          if (!entryFor(t)) return;
          kills[t] = n;
        });
      }
      var dy = block.days;
      if (dy && typeof dy === 'object' && !Array.isArray(dy)) {
        Object.keys(dy).forEach(function (t) {
          var d = Number(dy[t]);
          if (!isFinite(d)) return;
          d = Math.round(d);
          if (d < 0) return;
          if (!entryFor(t)) return;
          days[t] = d;
        });
      }
    }
    if (Object.keys(witnessed).length > 0) wasBorn = true;
    born = wasBorn;
  }

  // init(g): holds the game ref only. born is NOT set here (V-1: the codex
  // is born only through appendKill / appendSight / restore).
  function init(g) {
    game = g;
    tabActive = false;
  }

  function isBorn() { return born; }
  function isOpen() { return tabActive; }
  // setOpen(v): journal-owned tab state (the BESTIARY tab drives the page).
  function setOpen(v) { tabActive = !!v; }
  function closeForTest() { setOpen(false); }

  // One codex row (journal-row family): [sigil] [title] on a head line,
  // then the seen stamp ('Day N' / 'Day N - slain: m') and, when discovered,
  // the hunter's field note. Undiscovered rows render as locked rows: the
  // locked sigil placeholder and the locked title only - no day, no count,
  // no note. Accent = ONE per row, on the sigil span only.
  function rowFor(typeKey, entry, isSeen) {
    var row = el('div', 'bestiary-row' + (isSeen ? '' : ' bestiary-row-locked'));
    var head = el('div', 'bestiary-head');
    head.appendChild(el('span', 'bestiary-row-sigil codex-accent-' + (entry.accent || 'ash'),
      isSeen ? entry.sigil : CFG.text.lockedSigil));
    head.appendChild(el('div', 'bestiary-row-title', isSeen ? entry.title : CFG.text.lockedTitle));
    row.appendChild(head);
    if (isSeen) {
      var day = (typeof days[typeKey] === 'number' && isFinite(days[typeKey]))
        ? days[typeKey] : 0;
      day = Math.max(0, Math.round(day));
      var n = (typeof kills[typeKey] === 'number' && kills[typeKey] > 0) ? kills[typeKey] : 0;
      var stamp = CFG.text.seenStamp.replace('{day}', String(day));
      if (n > 0) stamp += ' - ' + CFG.text.killsLabel + ' ' + String(n);
      row.appendChild(el('div', 'bestiary-row-stamp', stamp));
      if (entry.page) row.appendChild(el('div', 'bestiary-row-page', entry.page));
    }
    return row;
  }

  // renderPage(container, query): journal-owned mount (the page div), query
  // already lowercased by journal.js. Discovered rows filter on title + page
  // text (the nomatch grammar covers an empty result). Locked rows stay
  // behind the sigil-only placeholder with a single footer count line.
  function renderPage(container, query) {
    if (!container || !CFG || !CFG.text || !CFG.entries) return;
    var q = (typeof query === 'string' && query.length > 0) ? query : '';
    var keys = Object.keys(CFG.entries);
    var hidden = 0, shown = 0;
    keys.forEach(function (t) {
      var entry = CFG.entries[t];
      if (!entry) return;
      var isSeen = !!witnessed[t];
      if (q) {
        if (!isSeen) return;            // locked rows carry no searchable text
        var hay = (entry.title + ' ' + (entry.page || '') + ' ' + (entry.sigil || ''))
          .toLowerCase();
        if (hay.indexOf(q) < 0) return;
        shown++;
        container.appendChild(rowFor(t, entry, true));
        return;
      }
      if (isSeen) {
        shown++;
        container.appendChild(rowFor(t, entry, true));
      } else {
        hidden++;
        container.appendChild(rowFor(t, entry, false));
      }
    });
    if (q) {
      if (!shown) container.appendChild(el('div', 'journal-nomatch', CFG.text.nomatch));
    } else if (hidden > 0) {
      container.appendChild(el('div', 'bestiary-footer',
        CFG.text.hiddenFooter.replace('{n}', String(hidden))));
    }
  }

  window.WH_BESTIARY = {
    init: init,
    update: update,
    capture: capture,
    restore: restore,
    appendKill: appendKill,
    appendSight: appendSight,
    sightOf: sightOf,
    killsOf: killsOf,
    isBorn: isBorn,
    isOpen: isOpen,
    setOpen: setOpen,          // QJR-4: journal-owned tab state (small additive API)
    closeForTest: closeForTest,
    renderPage: renderPage     // journal hands the page mount; DOM never touches body
  };
})();
