// Witch Hunter prototype - inventory (2026-10-05, Order A).
// Possession system, separate from the belt: the belt is the casting system
// (keys 1-5 / Q, player.js), the inventory only holds items. Generic on
// purpose - stage 2 enemy drops + gatherables route through the same item
// registry (CONFIG.items) and pickup flow.
// Exposes window.WH_INVENTORY:
//   Inventory          constructor (one per player; game.js owns the instance)
//   active             the player's Inventory once game.js boots it
//   addItem / removeItem / countOf / slotAt / forEachSlot -> delegate to active
//   itemDef(id), stackCapOf(id)

(function () {
  'use strict';

  var CFG = window.WH_CONFIG;

  function itemDef(id) {
    return CFG.items[id] || null;
  }

  // Gear carries stackCap 1; consumables fall back to the inventory default.
  function stackCapOf(id) {
    var d = itemDef(id);
    if (!d) return 0;
    return d.stackCap || CFG.inventory.defaultStackCap;
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

  // ---- inventory screen (DOM modal, I key) ---------------------------------------
  // opts: { inventory, onOpenChange(open), onDrop(slotIndex, wholeStack) }.
  // The UI never touches player state itself: game.js suspends input on
  // onOpenChange and routes onDrop to the drop flow.

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  function InventoryUI(opts) {
    var UI = CFG.inventoryUI;
    var self = this;
    this.inv = opts.inventory;
    this.onOpenChange = opts.onOpenChange || null;
    this.onDrop = opts.onDrop || null;
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
    this.invBody.appendChild(el('div', 'inv-hint',
      keyLabel(UI.dropKey) + ' drop 1  -  Shift+' + keyLabel(UI.dropKey) +
      ' drop stack  -  ' + UI.closeKeys.map(keyLabel).join(' / ') + ' close'));
    panel.appendChild(this.invBody);

    // character tab: placeholder until Order B
    this.charBody = el('div', 'inv-body inv-char');
    this.charBody.appendChild(el('div', 'inv-soon', 'Coming soon'));
    panel.appendChild(this.charBody);

    this.tip = el('div', 'inv-tip');
    this.tipName = el('div', 'inv-tip-name');
    this.tipCat = el('div', 'inv-tip-cat');
    this.tip.appendChild(this.tipName);
    this.tip.appendChild(this.tipCat);
    root.appendChild(this.tip);

    document.getElementById('wh-root').appendChild(root);
    this.root = root;

    // toast lives in the HUD layer so it shows with the screen closed too
    this.toastEl = el('div');
    this.toastEl.id = 'wh-toast';
    document.getElementById('wh-hud').appendChild(this.toastEl);

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
    }
  };

  InventoryUI.prototype.setOpen = function (open) {
    if (this.open === open) return;
    this.open = open;
    this.root.classList.toggle('open', open);
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
      v.glyph.textContent = d ? d.glyph : '';
      v.count.textContent = s && s.count > 1 ? String(s.count) : '';
    }
    if (this.tipSlot >= 0) this.fillTip(this.tipSlot);
  };

  InventoryUI.prototype.fillTip = function (i) {
    var s = this.inv.slots[i];
    var d = s ? itemDef(s.id) : null;
    if (!d) { this.tip.style.display = 'none'; return false; }
    this.tipName.textContent = d.name;
    this.tipCat.textContent = d.category === 'gear' ? 'Gear' : 'Consumable';
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
  InventoryUI.prototype.toast = function (text) {
    var t = this.toastEl;
    t.textContent = text;
    t.classList.add('visible');
    clearTimeout(this.toastTimer);
    this.toastTimer = setTimeout(function () {
      t.classList.remove('visible');
    }, CFG.inventoryUI.toastSeconds * 1000);
  };

  // ---- module ---------------------------------------------------------------------

  var M = {
    InventoryUI: InventoryUI,
    Inventory: Inventory,
    active: null,
    itemDef: itemDef,
    stackCapOf: stackCapOf,
    addItem: function (id, count) { return M.active ? M.active.addItem(id, count) : 0; },
    removeItem: function (id, count) { return M.active ? M.active.removeItem(id, count) : 0; },
    countOf: function (id) { return M.active ? M.active.countOf(id) : 0; },
    slotAt: function (i) { return M.active ? M.active.slotAt(i) : null; },
    forEachSlot: function (fn) { if (M.active) M.active.forEachSlot(fn); }
  };
  window.WH_INVENTORY = M;
})();
