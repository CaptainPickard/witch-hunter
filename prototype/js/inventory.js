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

  // ---- module ---------------------------------------------------------------------

  var M = {
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
