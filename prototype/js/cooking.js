// Witch Hunter prototype - cooking (C1, io/missions/2026-10-05-cc-c1-cooking.md).
// A fire STATION (data row in CONFIG.cooking.stations) burns fuel; E near a
// lit station opens the COOK panel (3 ingredient slots, no dish preview),
// Cook runs a channel (CONFIG.cooking.channelSeconds) and turns the trio
// into a recipe result or the fallback (Bland Mush). CAMP GROWTH LAW: the
// station list is a registry (Cooking.addStation) - C3's deployed campfire
// adds a row of the same shape; nothing keys off the bandit fire itself.
// Exposes window.WH_COOKING:
//   Cooking   constructor (game.js owns the one instance)
//   Station   one fire station { id, kind, regionId, asset, x, z, fuel }
//   matchRecipe(ids) -> recipe row | null (order-free)
//   BuffSet   the first buff system (food buffs; game.js applies the stats)
// C2: day buffs count down on the day clock (js/daynight.js, opts.dayNight),
// dayMeal buffs obey the one-meal-per-day cap, 'hot' buffs heal over time.

(function () {
  'use strict';

  var CFG = window.WH_CONFIG;
  var C = CFG.cooking;
  var INV = window.WH_INVENTORY;

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  // ---- recipes ----------------------------------------------------------------------
  // Order-free multiset match of exactly 3 ingredient ids.
  function matchRecipe(ids) {
    var key = ids.slice().sort().join('|');
    for (var i = 0; i < C.recipes.length; i++) {
      if (C.recipes[i].ingredients.slice().sort().join('|') === key) return C.recipes[i];
    }
    return null;
  }

  // { id: count } for a list of ids (duplicates allowed)
  function tally(ids) {
    var t = {};
    for (var i = 0; i < ids.length; i++) if (ids[i]) t[ids[i]] = (t[ids[i]] || 0) + 1;
    return t;
  }

  // ---- stations ---------------------------------------------------------------------
  // fuel = seconds of burn left. Lit while fuel > 0, or while a cook channel
  // holds the station (that cook's fuel was deducted at start and is what
  // burns during the channel, so the passive burn pauses).
  function Station(row) {
    this.id = row.id;
    this.kind = row.kind || 'cookFire';
    this.regionId = row.regionId;
    this.asset = row.asset;
    this.x = row.x;
    this.z = row.z;
    this.fuel = row.startLit ? C.fire.startFuelSec : 0;
    this.burnAcc = 0;
    this.cooking = false;
  }

  Station.prototype.isLit = function () {
    return this.fuel > 0 || this.cooking;
  };

  // enough fuel to start a cook (>= one channel)
  Station.prototype.canCook = function () {
    return this.fuel >= C.channelSeconds;
  };

  // passive burn: burnTickSec of fuel every burnTickSec seconds
  Station.prototype.update = function (dt) {
    if (this.cooking || this.fuel <= 0) { this.burnAcc = 0; return; }
    var tick = C.fire.burnTickSec;
    this.burnAcc += dt;
    while (this.burnAcc >= tick && this.fuel > 0) {
      this.burnAcc -= tick;
      this.fuel = Math.max(0, this.fuel - tick);
    }
  };

  // ---- buffs (C1: the first buff system) --------------------------------------------
  // One instance per buff id (CONFIG.cooking.buffs); add() on an active id
  // refreshes its duration, never stacks; different ids coexist. C2: stat
  // buffs last def.days in-game DAYS, counted down by the day clock
  // (dayNight.dayDelta; frozen while the clock is dormant); without a
  // dayNight, 1 day = buffDurationFallbackSec real seconds. 'hot' buffs
  // run on REAL seconds (def.durationSec). remaining = seconds left (HUD).
  function BuffSet(dayNight) {
    this.dayNight = dayNight || null;
    this.active = {};                 // id -> { id, kind, unit, remaining, days?, acc? }
  }

  BuffSet.prototype.add = function (id) {
    var def = C.buffs[id] || {};
    var old = this.active[id];
    var b = { id: id, kind: def.kind || 'stat' };
    if (b.kind === 'hot') {
      b.unit = 'sec';
      b.remaining = b.duration = def.durationSec;
      b.acc = old ? old.acc : 0;      // refresh keeps the tick phase (no double tick)
    } else if (this.dayNight) {
      b.unit = 'day';
      b.days = def.days || 1;
      b.remaining = b.duration = b.days * CFG.dayNight.dayLengthSec;
    } else {
      b.unit = 'sec';
      b.remaining = b.duration = (def.days || 1) * C.buffDurationFallbackSec;
    }
    this.active[id] = b;
  };

  // Counts every buff down; returns the HP that 'hot' buffs heal this frame
  // (Cooking.update applies it AFTER the cook-interrupt hit test, so regen
  // never masks or fakes a hit).
  BuffSet.prototype.update = function (dt, dayDelta) {
    var heal = 0;
    for (var id in this.active) {
      var b = this.active[id];
      if (b.kind === 'hot') {
        var def = C.buffs[id];
        b.acc += Math.min(dt, b.remaining);
        // eps: 30s of summed dt still lands all 30 ticks
        while (b.acc >= def.tickSec - 1e-6) { b.acc -= def.tickSec; heal += def.rate; }
      }
      if (b.unit === 'day') {
        b.days -= dayDelta || 0;
        b.remaining = b.days * CFG.dayNight.dayLengthSec;
      } else {
        b.remaining -= dt;
      }
      if (b.remaining <= 1e-6) delete this.active[id];
    }
    return heal;
  };

  // summed amount of every active buff on stat ('hpMax')
  BuffSet.prototype.statBonus = function (stat) {
    var n = 0;
    for (var id in this.active) {
      var def = C.buffs[id];
      if (def && def.stat === stat) n += def.amount;
    }
    return n;
  };

  // C3 Save and Heal: every buff ends (game.js recomputes hpMax after)
  BuffSet.prototype.clear = function () {
    this.active = {};
  };

  BuffSet.prototype.list = function () {
    var self = this;
    return Object.keys(this.active).map(function (id) { return self.active[id]; });
  };

  // ---- Cooking (registry + panel + channel) -----------------------------------------
  // opts: { inventory, player, toast(text), onOpenChange(open),
  //         dropAtFeet(id, count), dayNight }.
  // onKitButton: set by the camp manager (C3, js/camp.js) - the CAMP press.
  function Cooking(opts) {
    var self = this;
    this.inv = opts.inventory;
    this.player = opts.player;
    this.toastFn = opts.toast;
    this.onOpenChange = opts.onOpenChange || null;
    this.dropAtFeet = opts.dropAtFeet || null;
    this.onCooked = opts.onCooked || null;   // L1: fn(resultId, learnedRecipe)
    this.onKitButton = null;
    this.stations = [];
    for (var i = 0; i < C.stations.length; i++) this.addStation(C.stations[i]);
    this.open = false;
    this.station = null;              // station the panel is open on
    this.slots = [null, null, null];  // reserved ingredient ids (not yet taken)
    this.channel = null;              // { station, ids, t, fuelSpent }
    this.hintShown = false;           // C1: cryptic hint once per session
    this.showHint = false;
    this.lastHp = this.player.hp;
    this.toastTimers = [];
    this.dayNight = opts.dayNight || null;   // C2: js/daynight.js clock
    this.buffs = new BuffSet(this.dayNight);
    this.mealDay = -1;                // C2: dayNight.day the day's dayMeal was eaten
    this.kitAcquired = false;         // C1 campsite-kit moment (C3: the camp deploy gate)
    this.buildPanel();
    this.buildKitButton();
    document.addEventListener('keydown', function (e) { self.onKey(e); });
  }

  // CAMP GROWTH LAW: any module (C3 deployed campfire) registers here.
  Cooking.prototype.addStation = function (row) {
    var st = new Station(row);
    this.stations.push(st);
    return st;
  };

  // C3: a packed-up camp takes its fire out of the registry
  Cooking.prototype.removeStation = function (st) {
    var i = this.stations.indexOf(st);
    if (i < 0) return;
    if (this.channel && this.channel.station === st) this.interrupt();
    if (this.station === st) this.setOpen(false);
    this.stations.splice(i, 1);
  };

  // C3 Save and Heal: the day's meal slot is empty again (the new day's
  // first dayMeal applies)
  Cooking.prototype.clearMealSlot = function () {
    this.mealDay = -1;
  };

  Cooking.prototype.nearestStation = function (x, z, regionId) {
    var best = null, bestD2 = C.interactRadius * C.interactRadius;
    for (var i = 0; i < this.stations.length; i++) {
      var s = this.stations[i];
      if (s.regionId !== regionId) continue;
      var dx = s.x - x, dz = s.z - z;
      var d2 = dx * dx + dz * dz;
      if (d2 <= bestD2) { bestD2 = d2; best = s; }
    }
    return best;
  };

  // Light-pool socket intensity for a fire prop (game.js computeFireSockets):
  // a burnt-out station goes dark, anything else keeps its CONFIG value.
  Cooking.prototype.socketIntensity = function (regionId, prop, base) {
    for (var i = 0; i < this.stations.length; i++) {
      var s = this.stations[i];
      if (s.regionId === regionId && s.asset === prop.asset &&
          Math.abs(s.x - prop.x) < 0.01 && Math.abs(s.z - prop.z) < 0.01) {
        return s.isLit() ? base : C.fire.burntLightIntensity;
      }
    }
    return base;
  };

  Cooking.prototype.promptFor = function (st) {
    var T = C.text;
    if (!st.isLit()) return T.promptBurnt;
    return st.canCook() ? T.promptCook : T.promptLow;
  };

  // E on a station: lit with enough fuel = open the panel, else feed it.
  Cooking.prototype.interactStation = function (st) {
    if (st.canCook()) {
      this.setOpen(true, st);
    } else {
      this.refuel(st);
    }
  };

  // 1 fuel item -> burnPerCookSec * refuelCooks seconds on top of what is left.
  Cooking.prototype.refuel = function (st) {
    var F = C.fire;
    if (this.inv.countOf(F.fuelItem) < 1) {
      this.toast(C.text.noFuelToast);
      return false;
    }
    this.inv.removeItem(F.fuelItem, 1);
    st.fuel = Math.max(0, st.fuel) + F.burnPerCookSec * F.refuelCooks;
    st.burnAcc = 0;
    this.toast(C.text.refuelToast);
    return true;
  };

  // Chained toasts (cooked -> learned -> kit), toastChainSec apart.
  Cooking.prototype.toast = function (text) {
    this.toastChain([text]);
  };

  Cooking.prototype.toastChain = function (lines) {
    var self = this;
    this.toastTimers.forEach(clearTimeout);
    this.toastTimers = [];
    lines.forEach(function (line, i) {
      if (i === 0) { self.toastFn(line); return; }
      self.toastTimers.push(setTimeout(function () { self.toastFn(line); },
        i * C.toastChainSec * 1000));
    });
  };

  // ---- panel (DOM modal, inventory-screen patterns) ---------------------------------

  Cooking.prototype.buildPanel = function () {
    var self = this;
    var root = el('div');
    root.id = 'wh-cook';
    var panel = el('div', 'inv-panel cook-panel');
    root.appendChild(panel);
    panel.appendChild(el('div', 'inv-title', 'COOKING'));
    this.fuelEl = el('div', 'cook-fuel');
    panel.appendChild(this.fuelEl);
    // fuel top-up: the fire lasts as long as the player keeps feeding it
    // (1 deadwood per click, same math as the ground refuel prompt)
    this.fuelBtnRow = el('div', 'cook-btns cook-fuel-row');
    this.fuelBtn = el('button', 'cook-btn cook-fuel-btn', C.text.addWoodBtn);
    this.fuelBtn.type = 'button';
    this.fuelBtn.tabIndex = -1;
    this.fuelBtn.addEventListener('click', function () {
      if (self.channel) return;
      self.refuel(self.station);
      self.render();
    });
    this.fuelBtnRow.appendChild(this.fuelBtn);
    panel.appendChild(this.fuelBtnRow);
    this.hintEl = el('div', 'cook-hint', C.hint.noMushroomText);
    panel.appendChild(this.hintEl);

    var pot = el('div', 'cook-pot');
    this.slotEls = [];
    for (var i = 0; i < 3; i++) {
      (function (i) {
        var s = el('div', 'inv-slot cook-slot');
        var g = el('span', 'inv-glyph cook-icon');   // C4: pixel icon (WH_ICONS)
        s.appendChild(g);
        s.title = 'Click to clear';
        s.addEventListener('click', function () { self.clearSlot(i); });
        pot.appendChild(s);
        self.slotEls.push({ root: s, glyph: g });
      })(i);
    }
    panel.appendChild(pot);
    this.potNameEl = el('div', 'cook-pot-names');
    panel.appendChild(this.potNameEl);

    var prog = el('div', 'cook-progress');
    this.progFill = el('div', 'cook-progress-fill');
    prog.appendChild(this.progFill);
    panel.appendChild(prog);

    var btns = el('div', 'cook-btns');
    this.cookBtn = el('button', 'cook-btn', 'COOK');
    this.cookBtn.type = 'button';
    this.cookBtn.addEventListener('click', function () { self.startCook(); });
    this.cancelBtn = el('button', 'cook-btn', 'CANCEL');
    this.cancelBtn.type = 'button';
    this.cancelBtn.addEventListener('click', function () { self.cancel(); });
    btns.appendChild(this.cookBtn);
    btns.appendChild(this.cancelBtn);
    panel.appendChild(btns);

    panel.appendChild(el('div', 'inv-sec', 'INGREDIENTS'));
    this.ingEl = el('div', 'cook-ings');
    panel.appendChild(this.ingEl);
    panel.appendChild(el('div', 'inv-sec', 'RECIPES'));
    this.recEl = el('div', 'cook-recipes');
    panel.appendChild(this.recEl);
    panel.appendChild(el('div', 'inv-hint', 'Click an ingredient to add it - click a slot to clear - Esc cancel'));

    document.getElementById('wh-root').appendChild(root);
    this.root = root;
  };

  Cooking.prototype.setOpen = function (open, st) {
    if (this.open === open) return;
    if (!open && this.channel) this.interrupt();
    this.open = open;
    this.station = open ? st : null;
    if (open) {
      this.slots = [null, null, null];
      // cryptic hint: first open with no mushroom in the bag, once per session
      this.showHint = !this.hintShown && this.inv.countOf(C.hint.hintItem) === 0;
      if (this.showHint) this.hintShown = true;
    }
    this.root.classList.toggle('open', open);
    this.render();
    if (this.onOpenChange) this.onOpenChange(open);
  };

  Cooking.prototype.onKey = function (e) {
    if (!this.open || e.repeat) return;
    if (e.code === 'Escape') {
      e.preventDefault();
      this.cancel();
    } else if (this.channel && C.interruptKeys.indexOf(e.code) >= 0) {
      this.interrupt();             // movement input breaks the channel
    }
  };

  // Cancel button / Esc: a running channel is interrupted (refund), then close.
  Cooking.prototype.cancel = function () {
    if (this.channel) this.interrupt();
    this.setOpen(false);
  };

  // count of id still free to reserve (bag minus the pot's reservations)
  Cooking.prototype.freeCount = function (id) {
    var n = this.inv.countOf(id);
    for (var i = 0; i < this.slots.length; i++) if (this.slots[i] === id) n--;
    return n;
  };

  Cooking.prototype.addToPot = function (id) {
    if (this.channel || this.freeCount(id) <= 0) return;
    var i = this.slots.indexOf(null);
    if (i < 0) return;
    this.slots[i] = id;
    this.render();
  };

  Cooking.prototype.clearSlot = function (i) {
    if (this.channel) return;
    this.slots[i] = null;
    this.render();
  };

  // Known recipe row: fill the pot from the bag and start the channel.
  Cooking.prototype.cookRecipe = function (r) {
    if (this.channel) return;
    var need = tally(r.ingredients);
    for (var id in need) {
      if (this.inv.countOf(id) < need[id]) { this.toast(C.text.missingToast); return; }
    }
    this.slots = r.ingredients.slice();
    this.startCook();
  };

  // Ingredients leave the bag and the cook's fuel leaves the fire at START;
  // an interrupt gives both back in full.
  Cooking.prototype.startCook = function () {
    var st = this.station;
    if (this.channel || !st) return;
    if (this.slots.indexOf(null) >= 0) { this.toast(C.text.needThreeToast); this.render(); return; }
    if (!st.canCook()) { this.toast(C.text.tooLowToast); this.render(); return; }
    var need = tally(this.slots);
    for (var id in need) {
      if (this.inv.countOf(id) < need[id]) { this.toast(C.text.missingToast); return; }
    }
    for (id in need) this.inv.removeItem(id, need[id]);
    var spent = Math.min(C.fire.burnPerCookSec, st.fuel);
    st.fuel -= spent;
    st.cooking = true;
    this.channel = { station: st, ids: this.slots.slice(), t: 0, fuelSpent: spent };
    this.lastHp = this.player.hp;
    this.render();
  };

  Cooking.prototype.interrupt = function () {
    var ch = this.channel;
    if (!ch) return;
    this.channel = null;
    ch.station.cooking = false;
    ch.station.fuel += ch.fuelSpent;
    var back = tally(ch.ids);
    for (var id in back) {
      var added = this.inv.addItem(id, back[id]);
      if (added < back[id] && this.dropAtFeet) this.dropAtFeet(id, back[id] - added);
    }
    this.toast(C.text.interruptToast);
    this.render();
  };

  Cooking.prototype.finishCook = function () {
    var ch = this.channel;
    this.channel = null;
    ch.station.cooking = false;
    var recipe = matchRecipe(ch.ids);
    var resultId = recipe ? recipe.result : C.fallbackResult;
    var added = this.inv.addItem(resultId, 1);
    if (added < 1 && this.dropAtFeet) this.dropAtFeet(resultId, 1);
    var name = INV.itemDef(resultId).name;
    var lines = [C.text.cookedToast.replace('{name}', name)];
    var learned = !!(recipe && !recipe.known);
    if (recipe && !recipe.known) {
      recipe.known = true;
      lines.push(C.text.learnedToast.replace('{name}', recipe.name));
      // campsite-kit moment: same beat as the first recipe learned
      if (!this.kitAcquired) {
        this.kitAcquired = true;
        lines.push(C.text.kitToast);
        this.kitBtn.style.display = '';
      }
    }
    this.toastChain(lines);
    this.slots = [null, null, null];
    this.render();
    // L1: cook / recipe-learn XP (game.js -> WH_LEVEL)
    if (this.onCooked) this.onCooked(resultId, learned);
  };

  // Per frame: station burn, channel progress + interrupts (hit / death /
  // fire out), panel auto-close on death.
  Cooking.prototype.update = function (dt) {
    for (var i = 0; i < this.stations.length; i++) this.stations[i].update(dt);
    var heal = this.buffs.update(dt, this.dayNight ? this.dayNight.dayDelta : 0);
    var p = this.player;
    if (this.channel) {
      // a hit = hp dropped below last frame (a buff-expiry clamp lands
      // exactly ON hpMax, so it is not a hit)
      var hit = p.hp < this.lastHp && p.hp < p.hpMax;
      if (p.state !== 'alive' || hit || !this.channel.station.isLit()) {
        this.interrupt();
      } else {
        this.channel.t += dt;
        if (this.channel.t >= C.channelSeconds) this.finishCook();
      }
    }
    // C2 heal over time (Bland Mush) lands after the hit test; lastHp takes
    // the healed value so the next frame only compares real drops
    if (heal > 0 && p.state === 'alive') p.hp = Math.min(p.hpMax, p.hp + heal);
    this.lastHp = p.hp;
    if (this.open && p.state !== 'alive') this.setOpen(false);
    if (this.open) this.renderLive();
  };

  // per-frame bits only (fuel readout, progress bar)
  Cooking.prototype.renderLive = function () {
    var st = this.station;
    if (!st) return;
    var secs = Math.ceil(st.fuel);
    var mm = Math.floor(secs / 60), ss = secs % 60;
    var txt = st.isLit() ? 'Fire: ' + mm + ':' + (ss < 10 ? '0' : '') + ss : 'Fire: burnt out';
    if (this.fuelEl.textContent !== txt) this.fuelEl.textContent = txt;
    var frac = this.channel ? Math.min(1, this.channel.t / C.channelSeconds) : 0;
    this.progFill.style.width = (frac * 100) + '%';
    if (this.fuelBtn) {
      this.fuelBtn.disabled = !!this.channel ||
        this.inv.countOf(C.fire.fuelItem) < 1;
    }
  };

  Cooking.prototype.render = function () {
    var self = this;
    var busy = !!this.channel;
    var ids = busy ? this.channel.ids : this.slots;
    for (var i = 0; i < 3; i++) {
      var d = ids[i] ? INV.itemDef(ids[i]) : null;
      this.slotEls[i].root.classList.toggle('filled', !!d);
      INV.setIcon(this.slotEls[i].glyph, d ? ids[i] : null, d ? d.glyph : '');
    }
    this.potNameEl.textContent = ids.map(function (id) {
      return id ? INV.itemDef(id).name : '-';
    }).join('  +  ');
    this.hintEl.style.display = this.showHint ? '' : 'none';
    this.cookBtn.disabled = busy || ids.indexOf(null) >= 0;
    this.root.classList.toggle('channel', busy);

    // ingredient stacks in the bag (the fuel item is fuel, never a cook slot).
    // C4: rows show the WH_ICONS pixel icon (AB1 belt pattern, glyph fallback)
    this.ingEl.textContent = '';
    var seen = {};
    this.inv.forEachSlot(function (s) {
      if (!s || seen[s.id]) return;
      var d = INV.itemDef(s.id);
      if (!d || d.category !== 'ingredient' || s.id === C.fire.fuelItem) return;
      seen[s.id] = true;
      var free = self.freeCount(s.id);
      var b = el('div', 'inv-slot' + (free > 0 ? ' filled' : ' cook-spent'));
      b.appendChild(INV.iconEl('inv-glyph cook-icon', s.id, d.glyph));
      b.appendChild(el('span', 'inv-count', String(Math.max(0, free))));
      b.title = d.name;
      b.addEventListener('click', function () { self.addToPot(s.id); });
      self.ingEl.appendChild(b);
    });
    if (!this.ingEl.children.length) this.ingEl.appendChild(el('div', 'inv-soon', 'No ingredients'));

    // learned recipes (one-click cook). C4: result icon before the name,
    // ingredient icons in place of the glyph text
    this.recEl.textContent = '';
    C.recipes.forEach(function (r) {
      if (!r.known) return;
      var row = el('div', 'inv-spell cook-recipe');
      var rd = INV.itemDef(r.result);
      row.appendChild(INV.iconEl('cook-icon', r.result, rd ? rd.glyph : ''));
      row.appendChild(el('span', 'inv-spell-name', r.name));
      var ings = el('span', 'inv-gear-hands cook-rec-ings');
      r.ingredients.forEach(function (id, k) {
        if (k) ings.appendChild(el('span', 'cook-rec-plus', '+'));
        ings.appendChild(INV.iconEl('cook-icon', id, INV.itemDef(id).glyph));
      });
      row.appendChild(ings);
      row.title = 'Cook ' + r.name;
      row.addEventListener('click', function () { self.cookRecipe(r); });
      self.recEl.appendChild(row);
    });
    if (!this.recEl.children.length) this.recEl.appendChild(el('div', 'inv-soon', 'None known'));
    this.renderLive();
  };

  // ---- food use (inventory screen EAT / E on a selected food stack) ---------------

  Cooking.prototype.canEat = function (id) {
    var d = INV.itemDef(id);
    return !!(d && d.category === 'food' && d.useHint && d.useHint.kind === 'eat');
  };

  // Eat 1 from slot i: its buff (if any) starts / refreshes. Returns true when eaten.
  // C2 meal cap: a dayMeal buff fills the day's one meal slot; a further
  // dayMeal meal that day is eaten (consumed) but grants no buff. Refresh
  // counts as the day's meal. Non-dayMeal food (Bland Mush) is never capped.
  Cooking.prototype.eat = function (slotIndex) {
    var s = this.inv.slotAt(slotIndex);
    if (!s || !this.canEat(s.id) || this.player.state !== 'alive') return false;
    var d = INV.itemDef(s.id);
    var bid = d.useHint.buff, bdef = bid ? C.buffs[bid] : null;
    this.inv.removeFromSlot(slotIndex, 1);
    if (bdef && bdef.dayMeal && this.dayNight) {
      if (this.mealDay === this.dayNight.day) {
        this.toast(C.text.alreadyAteToast);
        return true;
      }
      this.mealDay = this.dayNight.day;
    }
    if (bdef) this.buffs.add(bid);
    this.toast(C.text.eatToast.replace('{name}', d.name) +
      (bdef && bdef.stat ? '' : ' - ' + d.flavor));
    return true;
  };

  // ---- campsite kit HUD button (C1 reveal; C3 js/camp.js owns deploy) -----------
  // Same body-level button pattern as the INV button: pointerdown acts,
  // the mouse events are swallowed so no swing / camera drag leaks through.
  Cooking.prototype.buildKitButton = function () {
    var self = this, K = C.kitButton;
    var btn = el('button', '', K.glyph + ' ' + K.label);
    btn.id = 'wh-camp-btn';
    btn.type = 'button';
    btn.tabIndex = -1;
    btn.title = 'Set up camp';
    btn.style.left = K.left + 'px';
    btn.style.bottom = K.bottom + 'px';
    btn.style.display = 'none';       // revealed on the first recipe learned
    btn.addEventListener('pointerdown', function (e) {
      e.preventDefault();
      e.stopPropagation();
      if (self.onKitButton) self.onKitButton();
    });
    ['mousedown', 'click', 'contextmenu'].forEach(function (t) {
      btn.addEventListener(t, function (e) {
        e.preventDefault();
        e.stopPropagation();
      });
    });
    document.body.appendChild(btn);
    this.kitBtn = btn;
  };

  window.WH_COOKING = {
    BuffSet: BuffSet,
    Cooking: Cooking,
    Station: Station,
    matchRecipe: matchRecipe
  };
})();
