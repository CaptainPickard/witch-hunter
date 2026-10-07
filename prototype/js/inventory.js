// Witch Hunter prototype - inventory (2026-10-05, Order A + B).
// Possession system, separate from the belt: the belt picks the active
// learned spell (keys 1-5, player.js), the inventory only holds items.
// Order B: equipped gear lives in player.hands, NOT in the grid (an item is
// in exactly one place); the CHARACTER tab moves gear between the two.
// Generic on purpose - stage 2 enemy drops + gatherables route through the
// same item registry (CONFIG.items) and pickup flow.
// Exposes window.WH_INVENTORY:
//   Inventory          constructor (one per player; game.js owns the instance)
//   active             the player's Inventory once game.js boots it
//   addItem / removeItem / countOf / slotAt / forEachSlot -> delegate to active
//   itemDef(id), stackCapOf(id), kindOf(id) ('caster' | 'melee' | 'shield' | 'torch' | null)
//   InventoryUI        the I-key grid screen (DOM modal) + HUD toast
//   WorldItems         dropped item entities in the scene (E pickup)

(function () {
  'use strict';

  var CFG = window.WH_CONFIG;

  function itemDef(id) {
    return CFG.items[id] || null;
  }

  // Order B gear capability, purely from CONFIG.items (category + kind).
  function kindOf(id) {
    var d = itemDef(id);
    return d && d.category === 'gear' ? d.kind || null : null;
  }

  // equipHint 'rightHand' / 'leftHand' -> 'right' / 'left' (default hand)
  function defaultHandOf(id) {
    var d = itemDef(id);
    if (!d || !d.hands || !d.hands.length) return null;
    var h = d.equipHint === 'rightHand' ? 'right' : d.equipHint === 'leftHand' ? 'left' : null;
    return h && d.hands.indexOf(h) >= 0 ? h : d.hands[0];
  }

  // Gear carries stackCap 1; consumables fall back to the inventory default.
  // L1 Carry Weight: the default cap scales by WH_LEVEL statTotal('carry')
  // (1 with no points = 60); items with their own stackCap (gear 1, coin
  // 999) keep it. Read live at pickup / join, so points apply at once.
  function stackCapOf(id) {
    var d = itemDef(id);
    if (!d) return 0;
    if (d.stackCap) return d.stackCap;
    var carry = window.WH_LEVEL ? window.WH_LEVEL.statTotal('carry') : 1;
    return Math.round(CFG.inventory.defaultStackCap * carry);
  }

  // ---- data model ---------------------------------------------------------------
  // slots[i] = null | { id, count } with 1 <= count <= stackCapOf(id).

  function Inventory(slotCount) {
    this.slots = [];
    var n = slotCount || CFG.inventory.slots;
    for (var i = 0; i < n; i++) this.slots.push(null);
    this.onChange = null;             // UI redraw hook
  }

  // Spill order: existing partial stacks first, then empty slots, then
  // refuse. Returns the count actually added (0..count).
  Inventory.prototype.addItem = function (id, count) {
    var cap = stackCapOf(id);
    var left = count === undefined ? 1 : count;
    if (!cap || left <= 0) return 0;
    var i, s, room;
    for (i = 0; i < this.slots.length && left > 0; i++) {
      s = this.slots[i];
      if (!s || s.id !== id || s.count >= cap) continue;
      room = Math.min(cap - s.count, left);
      s.count += room;
      left -= room;
    }
    for (i = 0; i < this.slots.length && left > 0; i++) {
      if (this.slots[i]) continue;
      room = Math.min(cap, left);
      this.slots[i] = { id: id, count: room };
      left -= room;
    }
    var added = (count === undefined ? 1 : count) - left;
    if (added > 0) this.changed();
    return added;
  };

  // Removes up to count of id, draining the LAST stacks first so the
  // earliest slot keeps its position. Returns the count actually removed.
  Inventory.prototype.removeItem = function (id, count) {
    var left = count === undefined ? 1 : count;
    for (var i = this.slots.length - 1; i >= 0 && left > 0; i--) {
      var s = this.slots[i];
      if (!s || s.id !== id) continue;
      var take = Math.min(s.count, left);
      s.count -= take;
      left -= take;
      if (s.count <= 0) this.slots[i] = null;
    }
    var removed = (count === undefined ? 1 : count) - left;
    if (removed > 0) this.changed();
    return removed;
  };

  // Slot-addressed removal (the UI drop path acts on the selected stack).
  Inventory.prototype.removeFromSlot = function (i, count) {
    var s = this.slots[i];
    if (!s) return null;
    var take = Math.min(s.count, count === undefined ? 1 : count);
    s.count -= take;
    if (s.count <= 0) this.slots[i] = null;
    this.changed();
    return { id: s.id, count: take };
  };

  // True when addItem(id, 1) would land (a partial stack or an empty slot).
  Inventory.prototype.hasRoomFor = function (id) {
    var cap = stackCapOf(id);
    for (var i = 0; i < this.slots.length; i++) {
      var s = this.slots[i];
      if (!s || (s.id === id && s.count < cap)) return true;
    }
    return false;
  };

  Inventory.prototype.countOf = function (id) {
    var n = 0;
    for (var i = 0; i < this.slots.length; i++) {
      if (this.slots[i] && this.slots[i].id === id) n += this.slots[i].count;
    }
    return n;
  };

  // Copy of slot i (null when empty) so callers cannot mutate the stack.
  Inventory.prototype.slotAt = function (i) {
    var s = this.slots[i];
    return s ? { id: s.id, count: s.count } : null;
  };

  Inventory.prototype.forEachSlot = function (fn) {
    for (var i = 0; i < this.slots.length; i++) fn(this.slotAt(i), i);
  };

  // Fresh-spawn kit from CONFIG.inventory.startingItems.
  Inventory.prototype.fillStartingItems = function () {
    var kit = CFG.inventory.startingItems || [];
    for (var i = 0; i < kit.length; i++) this.addItem(kit[i].id, kit[i].count);
  };

  Inventory.prototype.changed = function () {
    if (this.onChange) this.onChange();
  };

  // ---- inventory screen (DOM modal, I key / INV button) ----------------------------
  // opts: { inventory, onOpenChange(open), onDrop(slotIndex, wholeStack),
  //         equip: { hands(), equip(id, hand, fromInventory), unequip(hand),
  //                  spells(), bindSpell(slot, role) } }.
  // Order C: spells() rows are { slot, id, main, off }; bindSpell binds a
  // belt slot to 'main' (right) or 'off' (left). fromInventory = draw the
  // item from the grid, never move it from the other hand (second glove).
  // The UI never touches player state itself: game.js suspends input on
  // onOpenChange, routes onDrop to the drop flow, and backs opts.equip with
  // the player's equip rules (refusals toast from there).

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  // AB1: pixel icon on a glyph span from the js/icons-data.js registry
  // (window.WH_ICONS, id -> data URI). Unknown id -> the fallback glyph text
  // (never blank); null id -> empty. Skips the write when unchanged, so
  // per-frame / per-render callers stay cheap.
  function setIcon(span, id, fallback) {
    var icons = window.WH_ICONS || {};
    var uri = id && Object.prototype.hasOwnProperty.call(icons, id) ? icons[id] : null;
    var key = uri ? id : '#' + (fallback || '');
    if (span._whIcon === key) return span;
    span._whIcon = key;
    span.classList.toggle('wh-icon', !!uri);
    span.style.backgroundImage = uri ? 'url("' + uri + '")' : '';
    span.textContent = uri ? '' : (fallback || '');
    return span;
  }

  // el() + setIcon in one: an icon span for item / spell id
  function iconEl(cls, id, fallback) {
    return setIcon(el('span', cls), id, fallback);
  }

  function InventoryUI(opts) {
    var UI = CFG.inventoryUI;
    var self = this;
    this.inv = opts.inventory;
    this.onOpenChange = opts.onOpenChange || null;
    this.onDrop = opts.onDrop || null;
    this.onUse = opts.onUse || null;  // C1: (slotIndex) eat a food stack
    this.canUse = opts.canUse || null;  // C1: (itemId) -> usable from the grid?
    this.equip = opts.equip || null;
    this.leveling = opts.leveling || null;   // L1: WH_LEVEL (CHARACTER tab column)
    this.open = false;
    this.tab = 'inventory';
    this.selected = -1;
    this.tipSlot = -1;

    var root = el('div');
    root.id = 'wh-inv';
    var panel = el('div', 'inv-panel');
    root.appendChild(panel);
    panel.appendChild(el('div', 'inv-title', 'INVENTORY'));

    var tabs = el('div', 'inv-tabs');
    this.tabEls = {
      inventory: el('div', 'inv-tab', 'INVENTORY'),
      character: el('div', 'inv-tab', 'CHARACTER')
    };
    Object.keys(this.tabEls).forEach(function (k) {
      tabs.appendChild(self.tabEls[k]);
      self.tabEls[k].addEventListener('click', function () { self.setTab(k); });
    });
    panel.appendChild(tabs);

    // inventory tab: fixed grid, CONFIG.inventoryUI.gridCols wide
    this.invBody = el('div', 'inv-body');
    var grid = el('div', 'inv-grid');
    grid.style.gridTemplateColumns = 'repeat(' + UI.gridCols + ', auto)';
    this.slotEls = [];
    this.inv.slots.forEach(function (_, i) {
      var s = el('div', 'inv-slot');
      var glyph = el('span', 'inv-glyph');
      var count = el('span', 'inv-count');
      s.appendChild(glyph);
      s.appendChild(count);
      s.addEventListener('click', function () { self.select(i); });
      s.addEventListener('mouseenter', function (e) { self.showTip(i, e); });
      s.addEventListener('mousemove', function (e) { self.moveTip(e); });
      s.addEventListener('mouseleave', function () { self.hideTip(); });
      grid.appendChild(s);
      self.slotEls.push({ root: s, glyph: glyph, count: count });
    });
    this.invBody.appendChild(grid);
    // C1: EAT button, shown while the selected stack is usable (food)
    this.useBtn = el('button', 'inv-use-btn', UI.useLabel + ' [' + keyLabel(UI.useKey) + ']');
    this.useBtn.type = 'button';
    this.useBtn.addEventListener('click', function () { self.useSelected(); });
    this.invBody.appendChild(this.useBtn);
    this.invBody.appendChild(el('div', 'inv-hint',
      keyLabel(UI.dropKey) + ' drop 1  -  Shift+' + keyLabel(UI.dropKey) +
      ' drop stack  -  ' + UI.closeKeys.map(keyLabel).join(' / ') + ' close'));
    panel.appendChild(this.invBody);

    // character tab (Order B): hands + learned spells | inventory gear list.
    // Rebuilt by renderCharacter() - a handful of rows, no diffing needed.
    this.charBody = el('div', 'inv-body inv-char');
    panel.appendChild(this.charBody);

    this.tip = el('div', 'inv-tip');
    this.tipName = el('div', 'inv-tip-name');
    this.tipCat = el('div', 'inv-tip-cat');
    this.tipFlavor = el('div', 'inv-tip-cat inv-tip-flavor');
    this.tip.appendChild(this.tipName);
    this.tip.appendChild(this.tipCat);
    this.tip.appendChild(this.tipFlavor);
    root.appendChild(this.tip);

    document.getElementById('wh-root').appendChild(root);
    this.root = root;

    // toast lives in the HUD layer so it shows with the screen closed too
    this.toastEl = el('div');
    this.toastEl.id = 'wh-toast';
    document.getElementById('wh-hud').appendChild(this.toastEl);

    // Order B: clickable open/close button (same toggle as the I key).
    // Body-level + above the modal so it also closes the screen. Activates
    // on pointerdown (mouse AND touch, the touch-toggle pattern) and
    // swallows the mouse events so the player's document listeners never
    // see a swing / camera drag from it.
    var OB = UI.openButton;
    if (OB && OB.enabled) {
      var btn = el('button', '', OB.label);
      btn.id = 'wh-inv-btn';
      btn.type = 'button';
      btn.tabIndex = -1;               // never keyboard-focused (Space = roll)
      btn.title = 'Inventory (' + keyLabel(UI.openKey) + ')';
      btn.style.left = OB.left + 'px';
      btn.style.bottom = OB.bottom + 'px';
      btn.addEventListener('pointerdown', function (e) {
        e.preventDefault();
        e.stopPropagation();
        self.setOpen(!self.open);
      });
      // mouseup is NOT swallowed: the player's document mouseup must still
      // end a guard / camera drag released over the button
      ['mousedown', 'click', 'contextmenu'].forEach(function (t) {
        btn.addEventListener(t, function (e) {
          e.preventDefault();
          e.stopPropagation();
        });
      });
      document.body.appendChild(btn);
      this.openBtn = btn;
    }

    this.inv.onChange = function () { self.render(); };
    document.addEventListener('keydown', function (e) { self.onKey(e); });
    this.setTab('inventory');
    this.render();
  }

  // 'KeyG' -> 'G', 'Escape' -> 'Esc'
  function keyLabel(code) {
    if (code === 'Escape') return 'Esc';
    return code.indexOf('Key') === 0 ? code.slice(3) : code;
  }

  InventoryUI.prototype.onKey = function (e) {
    var UI = CFG.inventoryUI;
    if (e.repeat) return;
    if (!this.open) {
      if (e.code === UI.openKey) { e.preventDefault(); this.setOpen(true); }
      return;
    }
    if (UI.closeKeys.indexOf(e.code) >= 0) {
      e.preventDefault();
      this.setOpen(false);
    } else if (e.code === UI.dropKey) {
      e.preventDefault();
      if (this.tab === 'inventory' && this.selected >= 0 &&
          this.inv.slots[this.selected] && this.onDrop) {
        this.onDrop(this.selected, e.shiftKey);
      }
    } else if (e.code === UI.useKey) {
      e.preventDefault();
      if (this.tab === 'inventory') this.useSelected();
    }
  };

  // C1: the selected stack is usable (food) -> onUse (game.js -> cooking.eat)
  InventoryUI.prototype.selectedUsable = function () {
    var s = this.selected >= 0 ? this.inv.slots[this.selected] : null;
    return !!(s && this.onUse && this.canUse && this.canUse(s.id));
  };

  InventoryUI.prototype.useSelected = function () {
    if (!this.selectedUsable()) return;
    this.onUse(this.selected);
    if (!this.inv.slots[this.selected]) this.selected = -1;
    this.render();
  };

  // blocked: another modal owns the screen (C1 cook panel) - I / INV ignored
  InventoryUI.prototype.setOpen = function (open) {
    if (this.open === open || (open && this.blocked)) return;
    this.open = open;
    this.root.classList.toggle('open', open);
    if (this.openBtn) this.openBtn.classList.toggle('active', open);
    if (!open) this.hideTip();
    this.render();
    if (this.onOpenChange) this.onOpenChange(open);
  };

  InventoryUI.prototype.setTab = function (tab) {
    this.tab = tab;
    var self = this;
    Object.keys(this.tabEls).forEach(function (k) {
      self.tabEls[k].classList.toggle('active', k === tab);
    });
    this.invBody.style.display = tab === 'inventory' ? '' : 'none';
    this.charBody.style.display = tab === 'character' ? '' : 'none';
    if (tab !== 'inventory') this.hideTip();
    if (tab === 'character') this.renderCharacter();
  };

  // Click = select (highlight). Clicking the selected slot again clears it.
  InventoryUI.prototype.select = function (i) {
    this.selected = (this.selected === i || !this.inv.slots[i]) ? -1 : i;
    this.render();
  };

  InventoryUI.prototype.render = function () {
    for (var i = 0; i < this.slotEls.length; i++) {
      var s = this.inv.slots[i];
      var v = this.slotEls[i];
      var d = s ? itemDef(s.id) : null;
      v.root.classList.toggle('filled', !!s);
      v.root.classList.toggle('selected', i === this.selected && !!s);
      setIcon(v.glyph, d ? s.id : null, d ? d.glyph : '');
      // count on every stackable item (x1 included); gear (cap 1) shows none
      v.count.textContent = s && stackCapOf(s.id) > 1 ? String(s.count) : '';
    }
    this.useBtn.style.display = this.selectedUsable() ? '' : 'none';
    if (this.tipSlot >= 0) this.fillTip(this.tipSlot);
    if (this.tab === 'character') this.renderCharacter();
  };

  var HAND_LABEL = { right: 'RIGHT HAND', left: 'LEFT HAND' };
  var HAND_KEY = { right: 'R', left: 'L' };

  // Order C binding columns (role = player.bindings key)
  var BIND_COLS = [
    { role: 'main', hand: 'right', label: 'MAIN (R)' },
    { role: 'off', hand: 'left', label: 'OFF (L)' }
  ];

  function spellDef(id) {
    return (window.WH_CONFIG.spell && window.WH_CONFIG.spell[id]) || {};
  }

  function spellName(id) {
    return spellDef(id).name || id.charAt(0).toUpperCase() + id.slice(1);
  }

  function spellGlyph(id) {
    return spellDef(id).glyph || id.slice(0, 2).toUpperCase();
  }

  // Left column: RIGHT / LEFT HAND slots (click = unequip to inventory) and
  // the MAIN (R) / OFF (L) spell bindings (click a spell = bind it to that
  // hand, same as Digit / Shift+Digit). Right column: gear rows from the
  // inventory (click = equip to the default hand - or the other hand when
  // the default already holds the same item, e.g. glove #2 - [L] / [R] =
  // that hand; moving across hands is allowed).
  InventoryUI.prototype.renderCharacter = function () {
    var self = this, E = this.equip, body = this.charBody;
    body.textContent = '';
    if (!E) return;
    var hands = E.hands();

    var left = el('div', 'inv-char-col');
    left.appendChild(el('div', 'inv-sec', 'EQUIPPED'));
    ['right', 'left'].forEach(function (h) {
      var d = itemDef(hands[h]);
      var row = el('div', 'inv-hand' + (d ? ' filled' : ''));
      row.appendChild(el('span', 'inv-hand-label', HAND_LABEL[h]));
      var slot = el('div', 'inv-slot inv-hand-slot' + (d ? ' filled' : ''));
      slot.appendChild(iconEl('inv-glyph', d ? hands[h] : null, d ? d.glyph : ''));
      row.appendChild(slot);
      row.appendChild(el('span', 'inv-hand-name', d ? d.name : 'Empty'));
      if (d) {
        // [L] / [R] move the held item across hands (one instance rule)
        var other = h === 'right' ? 'left' : 'right';
        if (d.hands && d.hands.indexOf(other) >= 0) {
          var id = hands[h];
          var mv = el('button', 'inv-hand-btn', '[' + HAND_KEY[other] + ']');
          mv.title = 'Move to ' + HAND_LABEL[other].toLowerCase();
          mv.addEventListener('click', function (e) {
            e.stopPropagation();
            E.equip(id, other);
          });
          row.appendChild(mv);
        }
        row.title = 'Click to unequip';
        row.addEventListener('click', function () { E.unequip(h); });
      }
      left.appendChild(row);
    });
    // Order C: SPELLS = two binding columns over the one learned list.
    // Click a spell under a column = bind it to that hand (same rules as
    // Digit / Shift+Digit).
    left.appendChild(el('div', 'inv-sec', 'SPELLS'));
    var spells = E.spells();
    var cols = el('div', 'inv-bind');
    BIND_COLS.forEach(function (c) {
      var col = el('div', 'inv-bind-col');
      col.appendChild(el('div', 'inv-hand-label', c.label));
      var bound = null;
      spells.forEach(function (sp) { if (sp[c.role]) bound = sp; });
      var cur = el('div', 'inv-bind-cur');
      var tile = el('div', 'inv-slot inv-hand-slot' + (bound ? ' filled' : ''));
      tile.appendChild(iconEl('inv-glyph', bound ? bound.id : null, bound ? spellGlyph(bound.id) : ''));
      cur.appendChild(tile);
      var txt = el('div', 'inv-gear-text');
      txt.appendChild(el('div', 'inv-hand-name', bound ? spellName(bound.id) : 'None'));
      txt.appendChild(el('div', 'inv-gear-hands', bound ? 'slot ' + (bound.slot + 1) : ''));
      if (kindOf(hands[c.hand]) !== 'caster') {
        txt.appendChild(el('div', 'inv-bind-note', 'no implement'));
      }
      cur.appendChild(txt);
      col.appendChild(cur);
      spells.forEach(function (sp) {
        var row = el('div', 'inv-spell' + (sp[c.role] ? ' active' : ''));
        row.appendChild(el('span', 'inv-spell-key', (c.role === 'off' ? 'S' : '') + (sp.slot + 1)));
        row.appendChild(el('span', 'inv-spell-name', spellName(sp.id)));
        row.title = 'Bind to the ' + c.hand + ' hand';
        row.addEventListener('click', function () {
          E.bindSpell(sp.slot, c.role);
          self.render();
        });
        col.appendChild(row);
      });
      cols.appendChild(col);
    });
    left.appendChild(cols);
    body.appendChild(left);

    var right = el('div', 'inv-char-col');
    right.appendChild(el('div', 'inv-sec', 'INVENTORY GEAR'));
    var list = el('div', 'inv-gear-list');
    var any = false;
    this.inv.slots.forEach(function (s) {
      var d = s ? itemDef(s.id) : null;
      if (!d || d.category !== 'gear' || !d.hands) return;
      any = true;
      var id = s.id, def = defaultHandOf(id);
      var alt = def === 'right' ? 'left' : 'right';
      if (hands[def] === id && d.hands.indexOf(alt) >= 0) def = alt;
      var row = el('div', 'inv-gear');
      var g = el('div', 'inv-slot filled');
      g.appendChild(iconEl('inv-glyph', id, d.glyph));
      row.appendChild(g);
      var txt = el('div', 'inv-gear-text');
      txt.appendChild(el('div', 'inv-gear-name', d.name));
      txt.appendChild(el('div', 'inv-gear-hands', 'hands: ' + d.hands.map(function (h) {
        return HAND_KEY[h] + (h === def ? '*' : '');
      }).join(' / ')));
      row.appendChild(txt);
      ['left', 'right'].forEach(function (h) {
        if (d.hands.indexOf(h) < 0) return;
        var b = el('button', 'inv-hand-btn', '[' + HAND_KEY[h] + ']');
        b.title = 'Equip to ' + HAND_LABEL[h].toLowerCase();
        b.addEventListener('click', function (e) {
          e.stopPropagation();
          E.equip(id, h, true);
        });
        row.appendChild(b);
      });
      row.title = 'Click: equip to ' + HAND_LABEL[def].toLowerCase();
      row.addEventListener('click', function () { E.equip(id, def, true); });
      list.appendChild(row);
    });
    if (!any) list.appendChild(el('div', 'inv-soon', 'No gear in inventory'));
    right.appendChild(list);
    body.appendChild(right);
    if (this.leveling) body.appendChild(this.renderLeveling());
  };

  // ---- L1 leveling column (opts.leveling = WH_LEVEL) ---------------------------------
  // LEVEL (xp bar + pending points badge), the nine stats (+ spends a
  // pending point, - takes back one spent since the screen opened), the
  // three skill lines (rank + progress bar + passive caption). Plain DOM
  // buttons, no sounds; every change re-renders through WH_LEVEL.onChange.

  // 0.004 -> '0.4', 0.25 -> '25' (percent, one decimal, trailing .0 trimmed)
  function pct(v) {
    return String(Math.round(Math.abs(v) * 1000) / 10);
  }

  function lvlBar(frac) {
    var outer = el('div', 'lvl-bar');
    var fill = el('div', 'lvl-bar-fill');
    fill.style.width = Math.round(Math.max(0, Math.min(1, frac)) * 100) + '%';
    outer.appendChild(fill);
    return outer;
  }

  function statCaption(LV, key) {
    var c = CFG.leveling.statCurves[key];
    var b = LV.statBonus(key);
    return c.caption.replace('{v}', String(Math.round(b * 10) / 10)).replace('{pct}', pct(b))
      .replace('{focus}', String(LV.statPoints(key) * (c.focusPerPoint || 0)));
    // L1.1: the {focus} placeholder is dead (no curve uses it) - harmless
    // replace; captions are pure CONFIG rows.
  }

  function skillCaption(LV, line) {
    var def = CFG.leveling.skillLines[line];
    var txt = def.caption;
    Object.keys(def.passives).forEach(function (k) {
      var v = LV.skillPassive(line, k);
      txt = txt.replace('{' + k + 'Ms}', String(Math.round(v * 10000) / 10))
        .replace('{' + k + '}', pct(v));
    });
    return txt;
  }

  InventoryUI.prototype.renderLeveling = function () {
    var LV = this.leveling, LC = CFG.leveling, T = LC.text;
    var col = el('div', 'inv-char-col inv-lvl-col');
    col.appendChild(el('div', 'inv-sec', 'LEVEL'));
    var head = el('div', 'lvl-head');
    head.appendChild(el('span', 'lvl-num', 'Level ' + LV.level()));
    var pend = LV.pendingPts();
    if (pend > 0) head.appendChild(el('span', 'lvl-badge', '+' + pend + ' ' + T.allocateHint));
    col.appendChild(head);
    col.appendChild(lvlBar(LV.xpFrac()));
    col.appendChild(el('div', 'lvl-cap', LV.level() >= LC.maxLevel ? 'MAX' :
      Math.floor(LV.xp()) + ' / ' + LV.xpForNext(LV.level()) + ' XP'));

    col.appendChild(el('div', 'inv-sec', 'STATS'));
    LC.stats.forEach(function (key) {
      var row = el('div', 'lvl-stat');
      var top = el('div', 'lvl-stat-top');
      top.appendChild(el('span', 'lvl-stat-name', LC.statCurves[key].label));
      top.appendChild(el('span', 'lvl-stat-pts', String(LV.statPoints(key))));
      var minus = el('button', 'inv-hand-btn lvl-btn', '-');
      minus.type = 'button';
      minus.disabled = !LV.canRecoup(key);
      minus.addEventListener('click', function (e) { e.stopPropagation(); LV.recoup(key); });
      var plus = el('button', 'inv-hand-btn lvl-btn', '+');
      plus.type = 'button';
      plus.disabled = pend <= 0;
      plus.addEventListener('click', function (e) { e.stopPropagation(); LV.spend(key); });
      top.appendChild(minus);
      top.appendChild(plus);
      row.appendChild(top);
      row.appendChild(el('div', 'lvl-cap', statCaption(LV, key)));
      col.appendChild(row);
    });

    col.appendChild(el('div', 'inv-sec', 'SKILLS'));
    Object.keys(LC.skillLines).forEach(function (line) {
      var row = el('div', 'lvl-skill');
      var top = el('div', 'lvl-stat-top');
      top.appendChild(el('span', 'lvl-stat-name', LC.skillLines[line].name));
      top.appendChild(el('span', 'lvl-stat-pts', 'Rank ' + LV.skillRank(line)));
      row.appendChild(top);
      row.appendChild(lvlBar(LV.skillProgress(line)));
      row.appendChild(el('div', 'lvl-cap', skillCaption(LV, line)));
      col.appendChild(row);
    });
    return col;
  };

  var CATEGORY_TIP = {
    gear: 'Gear - equip on the CHARACTER tab',
    consumable: 'Consumable',
    valuable: 'Valuable',
    ingredient: 'Ingredient',
    food: 'Food - select + ' + keyLabel(CFG.inventoryUI.useKey) + ' to eat'
  };

  InventoryUI.prototype.fillTip = function (i) {
    var s = this.inv.slots[i];
    var d = s ? itemDef(s.id) : null;
    if (!d) { this.tip.style.display = 'none'; return false; }
    this.tipName.textContent = d.name;
    this.tipCat.textContent = CATEGORY_TIP[d.category] || d.category;
    this.tipFlavor.textContent = d.flavor || '';
    this.tipFlavor.style.display = d.flavor ? '' : 'none';
    this.tip.style.display = 'block';
    return true;
  };

  InventoryUI.prototype.showTip = function (i, e) {
    this.tipSlot = i;
    if (this.fillTip(i)) this.moveTip(e);
  };

  InventoryUI.prototype.moveTip = function (e) {
    this.tip.style.left = (e.clientX + 14) + 'px';
    this.tip.style.top = (e.clientY + 14) + 'px';
  };

  InventoryUI.prototype.hideTip = function () {
    this.tipSlot = -1;
    this.tip.style.display = 'none';
  };

  // Brief HUD line ("Dropped Bandage x1", "Inventory full").
  // seconds: optional lifetime override (default CONFIG.inventoryUI.toastSeconds).
  InventoryUI.prototype.toast = function (text, seconds) {
    var t = this.toastEl;
    t.textContent = text;
    t.classList.add('visible');
    clearTimeout(this.toastTimer);
    this.toastTimer = setTimeout(function () {
      t.classList.remove('visible');
    }, (seconds || CFG.inventoryUI.toastSeconds) * 1000);
  };

  // ---- world item entities (drops; stage 2 enemy drops / gatherables) -------------
  // One entity = one stack on the ground: { id, count, x, z, regionId, mesh }.
  // Placeholder visual: unlit box colored by item category (CONFIG.inventory
  // .entity), resting on the ground plane (y = 0, the prop convention). The
  // list persists across region swaps; entities show only while their region
  // is active (both regions share one world space). No save wiring.

  function WorldItems(scene) {
    var E = CFG.inventory.entity;
    this.scene = scene;
    this.list = [];
    this.geo = new THREE.BoxGeometry(E.size, E.size, E.size);
    this.mats = {};
    for (var cat in E.colors) {
      this.mats[cat] = new THREE.MeshBasicMaterial({ color: E.colors[cat] });
    }
  }

  WorldItems.prototype.spawn = function (id, count, x, z, regionId) {
    var d = itemDef(id);
    if (!d || count <= 0) return null;
    var E = CFG.inventory.entity;
    var holder = new THREE.Group();
    holder.position.set(x, 0, z);
    var box = new THREE.Mesh(this.geo, this.mats[d.category] || this.mats.consumable);
    box.position.y = E.size / 2;      // bottom face on the ground
    holder.add(box);
    holder.rotation.y = Math.random() * Math.PI * 2;
    this.scene.add(holder);
    var ent = { id: id, count: count, x: x, z: z, regionId: regionId, mesh: holder };
    this.list.push(ent);
    return ent;
  };

  WorldItems.prototype.remove = function (ent) {
    var i = this.list.indexOf(ent);
    if (i < 0) return;
    this.list.splice(i, 1);
    this.scene.remove(ent.mesh);    // shared geometry/materials stay alive
  };

  // Nearest entity of regionId within radius of (x, z) on the ground plane.
  WorldItems.prototype.nearest = function (x, z, radius, regionId) {
    var best = null, bestD2 = radius * radius;
    for (var i = 0; i < this.list.length; i++) {
      var e = this.list[i];
      if (e.regionId !== regionId) continue;
      var dx = e.x - x, dz = e.z - z;
      var d2 = dx * dx + dz * dz;
      if (d2 <= bestD2) { bestD2 = d2; best = e; }
    }
    return best;
  };

  WorldItems.prototype.update = function (dt, activeRegionId) {
    var spin = CFG.inventory.entity.spinDegPerSec * Math.PI / 180 * dt;
    for (var i = 0; i < this.list.length; i++) {
      var e = this.list[i];
      e.mesh.visible = e.regionId === activeRegionId;
      e.mesh.rotation.y += spin;
    }
  };

  // ---- module ---------------------------------------------------------------------

  var M = {
    InventoryUI: InventoryUI,
    WorldItems: WorldItems,
    Inventory: Inventory,
    active: null,
    itemDef: itemDef,
    stackCapOf: stackCapOf,
    kindOf: kindOf,
    defaultHandOf: defaultHandOf,
    setIcon: setIcon,                 // AB1: icon registry consumer (belt, buffs, picker)
    iconEl: iconEl,
    addItem: function (id, count) { return M.active ? M.active.addItem(id, count) : 0; },
    removeItem: function (id, count) { return M.active ? M.active.removeItem(id, count) : 0; },
    countOf: function (id) { return M.active ? M.active.countOf(id) : 0; },
    slotAt: function (i) { return M.active ? M.active.slotAt(i) : null; },
    forEachSlot: function (fn) { if (M.active) M.active.forEachSlot(fn); }
  };
  window.WH_INVENTORY = M;
})();
