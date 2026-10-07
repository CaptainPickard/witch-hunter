// Witch Hunter prototype - save profile (C4, io/missions/2026-10-06-cc-c4-save-profile.md).
// ONE rolling profile in localStorage (CONFIG.save.lsKey 'wh-save-v1'),
// JSON schema v1 = { v, ts, player, inventory, cooking, camp, world }.
// Every save overwrites; load = last save wins. Fresh world spawns (trees,
// gather nodes, enemies) are never saved. Buffs are derived state: only the
// dayMeal slot (buff id + day) is stored, applyBuffStats recomputes hpMax.
// MAGIC CANON: spells are learned knowledge - the belt + per-hand bindings
// restore exactly as saved (AB1.1 select semantics untouched).
// All reads / writes go through the existing managers on the game object;
// game.js hands over the few local helpers it owns as game.c4 =
// { applyBuffStats, switchRegion, breakLockOn, reloadActionMap }.
// Exposes window.WH_SAVE:
//   capture(game, opts) -> plain profile object (opts.respawnCamp: the camp
//                          the menu Save runs on - its respawn is stored)
//   restore(game, data)  apply a profile (scene ready, after boot)
//   save(game, opts)     write { v, ts, ...capture } -> true on success
//   load(game)           stored profile | null (missing / corrupt / other v)
//   has()                a loadable profile exists

(function () {
  'use strict';

  var CFG = window.WH_CONFIG;
  var S = CFG.save;

  function num(v, fallback) {
    return typeof v === 'number' && isFinite(v) ? v : fallback;
  }

  function copyRespawn(r) {
    if (!r) return null;
    return { regionId: r.regionId, x: r.x, z: r.z,
      face: r.face ? { x: r.face.x, z: r.face.z } : null, campId: r.campId };
  }

  function validRegion(rid) {
    return !!(rid && window.WH_REGION_DEFS.regions[rid]);
  }

  // Gear item id that may sit in hand (same rules as Player.equipItem,
  // minus the inventory source check - the profile is the source).
  function validHandItem(id, hand) {
    var d = id && CFG.items[id];
    if (!d || d.category !== 'gear' || !d.hands || d.hands.indexOf(hand) < 0) return false;
    return !(!d.mesh && (d.kind === 'shield' || d.kind === 'melee'));
  }

  function isSpell(id) {
    var s = id && CFG.spell[id];
    return !!(s && typeof s === 'object' && s.kind);
  }

  // ---- capture ---------------------------------------------------------------------

  function capture(game, opts) {
    opts = opts || {};
    var p = game.player, dn = game.dayNight, ck = game.cooking, camp = game.camp;
    var rm = game.regionManager;
    var actionMap = null;
    try { actionMap = window.localStorage.getItem(CFG.actionbar.lsKey); } catch (e) { actionMap = null; }
    var mealBuff = null;
    ck.buffs.list().forEach(function (b) {
      var def = CFG.cooking.buffs[b.id];
      if (def && def.dayMeal) mealBuff = b.id;
    });
    var respawn = opts.respawnCamp ? opts.respawnCamp.respawn : camp.respawn;
    return {
      player: {
        hp: p.hp, focus: p.focus, stamina: p.stamina,
        regionId: rm.logic.activeId,
        pos: [p.pos.x, p.pos.z],
        yaw: p.yaw,
        hands: { right: p.hands.right, left: p.hands.left },
        belt: p.belt.slice(),
        bindings: { main: p.bindings.main, off: p.bindings.off },
        actionMap: actionMap,       // raw CONFIG.actionbar.lsKey JSON (string | null)
        consumables: p.getConsumables()
      },
      inventory: {
        items: game.inventory.slots.map(function (s) { return s ? { id: s.id, count: s.count } : null; })
      },
      cooking: {
        recipes: CFG.cooking.recipes.filter(function (r) { return r.known; })
          .map(function (r) { return r.id; }),
        kitAcquired: !!ck.kitAcquired,
        dayMeal: { buffId: mealBuff, savedDay: ck.mealDay }
      },
      camp: {
        sites: camp.sites.map(function (s) {
          return { id: s.id, regionId: s.regionId, x: s.x, z: s.z, face: { x: s.f.x, z: s.f.z } };
        }),
        respawn: copyRespawn(respawn)
      },
      world: { day: dn.day, phase: dn.phase, timeOfDay: dn.timeOfDay }
    };
  }

  // ---- storage ---------------------------------------------------------------------

  function save(game, opts) {
    var data = capture(game, opts);
    data.v = S.version;
    data.ts = Date.now();
    try {
      window.localStorage.setItem(S.lsKey, JSON.stringify(data));
      return true;
    } catch (e) {
      return false;                 // private mode / quota: nothing persists
    }
  }

  // version guard: only v === CONFIG.save.version loads (future migrations
  // slot in here, keyed by data.v)
  function load() {
    var data = null;
    try { data = JSON.parse(window.localStorage.getItem(S.lsKey) || 'null'); } catch (e) { data = null; }
    if (!data || typeof data !== 'object' || data.v !== S.version) return null;
    if (!data.player || !data.inventory || !data.cooking || !data.camp || !data.world) return null;
    return data;
  }

  function has() {
    return !!load();
  }

  // internal only (no wipe surface this round, C4 ruling 5)
  function wipe() {
    try { window.localStorage.removeItem(S.lsKey); } catch (e) { /* nothing to wipe */ }
  }

  // ---- restore ---------------------------------------------------------------------

  // Clock: the look is recomputed by one zero-dt tick at the saved time of
  // day; TUTORIAL LAW - a profile still on the dormant boot night (day 0 on
  // startPhase) restores dormant, so the first Save and Heal stays the only
  // beginCycle() caller.
  function restoreClock(dn, w) {
    var D = CFG.dayNight, len = D.dayLengthSec;
    var day = Math.max(0, Math.floor(num(w.day, 0)));
    var dormant = !(w.phase !== D.startPhase || day > 0);
    dn.day = day;
    dn.dormant = false;
    dn.fresh = false;
    dn.clock = dormant ? D.bounds[D.startPhase] * len + D.blendSec :
      Math.min(Math.max(num(w.timeOfDay, 0), 0), 0.999999) * len;
    dn.tick(0);                      // phase / timeOfDay / blended look at the saved time
    if (dormant) {
      dn.dormant = true;
      dn.clock = 0;
      dn.phase = D.startPhase;
      dn.timeOfDay = D.bounds[D.startPhase];
    }
    if (dn.sky) dn.sky.retarget('time');   // this day's pano variant
  }

  function restore(game, data) {
    if (!data) return;
    var p = game.player, ck = game.cooking, camp = game.camp, inv = game.inventory;
    var hooks = game.c4 || {};
    var P = data.player, I = data.inventory, C = data.cooking, K = data.camp;

    // modal / in-flight state the profile replaces (no refunds: the
    // inventory is overwritten below)
    if (camp.placing) camp.stopPlacing();
    if (ck.channel) { ck.channel.station.cooking = false; ck.channel = null; }
    if (ck.open) ck.setOpen(false);
    if (hooks.breakLockOn) hooks.breakLockOn();

    // 1) inventory first (slot layout as saved)
    var items = Array.isArray(I.items) ? I.items : [];
    for (var i = 0; i < inv.slots.length; i++) {
      var s = items[i];
      inv.slots[i] = s && CFG.items[s.id] && num(s.count, 0) > 0 ?
        { id: s.id, count: Math.floor(s.count) } : null;
    }

    // 2) hands: the saved ids overwrite; a hand MISSING from the profile
    // takes its CONFIG.equip.defaultHands item (equipItem path). Re-applied
    // through handsChanged -> applyHandVisuals with a regrip reset.
    var H = P.hands || {};
    p.toggling = false;
    p.toggleTimer = 0;
    p.pendingQSwap = null;
    p.dropPendingCast('main');
    p.dropPendingCast('off');
    p.hands = { right: null, left: null };
    p.lastHandItems = { right: null, left: null };
    ['right', 'left'].forEach(function (h) {
      if (H[h] !== undefined && H[h] !== null && validHandItem(H[h], h)) p.hands[h] = H[h];
    });
    p.handsChanged();
    var dh = CFG.equip.defaultHands;
    ['right', 'left'].forEach(function (h) {
      if (H[h] === undefined && dh[h]) p.equipItem(dh[h], h);
    });
    inv.changed();

    // 3) belt + per-hand bindings exactly as saved (AB1.1 semantics LOCKED)
    var slots = CFG.belt.slots;
    if (Array.isArray(P.belt)) {
      p.belt = [];
      for (var b = 0; b < slots; b++) p.belt.push(isSpell(P.belt[b]) ? P.belt[b] : null);
    }
    var bd = P.bindings || {};
    ['main', 'off'].forEach(function (role) {
      var v = Math.floor(num(bd[role], 0));
      p.bindings[role] = v >= 0 && v < slots ? v : 0;
    });
    if (Array.isArray(P.consumables)) {
      p.consumables = P.consumables.map(function (c) {
        return c && typeof c.id === 'string' ? { id: c.id, charges: Math.max(0, Math.floor(num(c.charges, 0))) } : null;
      });
    }
    // the action-bar map rides inside the profile; its own key stays the
    // live store (bar edits persist independently of wh-save-v1)
    if (typeof P.actionMap === 'string') {
      try { window.localStorage.setItem(CFG.actionbar.lsKey, P.actionMap); } catch (e) { /* no storage */ }
      if (hooks.reloadActionMap) hooks.reloadActionMap();
    }

    // 4) cooking knowledge + the campsite kit
    var known = Array.isArray(C.recipes) ? C.recipes : [];
    CFG.cooking.recipes.forEach(function (r) { r.known = known.indexOf(r.id) >= 0; });
    ck.kitAcquired = !!C.kitAcquired;
    if (ck.kitBtn) ck.kitBtn.style.display = ck.kitAcquired ? '' : 'none';

    // 5) clock (before the meal slot: savedDay compares against it)
    restoreClock(game.dayNight, data.world);

    // 6) camp sites through the manager's own builder (place(); groups are
    // built lazily by camp.update in their region), then the respawn point
    camp.sites.slice().forEach(function (site) { camp.packUp(site); });
    (Array.isArray(K.sites) ? K.sites : []).forEach(function (st) {
      if (!st || !validRegion(st.regionId)) return;
      var f = st.face || { x: 0, z: 1 };
      var fl = Math.sqrt(num(f.x, 0) * num(f.x, 0) + num(f.z, 0) * num(f.z, 0));
      f = fl > 1e-6 ? { x: f.x / fl, z: f.z / fl } : { x: 0, z: 1 };
      var seq = parseInt(String(st.id || '').replace(/^camp/, ''), 10);
      if (seq > 0) camp.siteSeq = seq - 1;           // same site id as saved
      camp.place(st.regionId, num(st.x, 0), num(st.z, 0), f);
    });
    camp.siteSeq = camp.sites.reduce(function (m, s) {
      return Math.max(m, parseInt(s.id.replace(/^camp/, ''), 10) || 0);
    }, camp.siteSeq);
    camp.respawn = K.respawn && validRegion(K.respawn.regionId) ? copyRespawn(K.respawn) : null;

    // 7) dayMeal slot (meal day + its buff), then the derived stats
    ck.buffs.clear();
    ck.mealDay = Math.floor(num(C.dayMeal && C.dayMeal.savedDay, -1));
    var mb = C.dayMeal && C.dayMeal.buffId;
    if (mb && CFG.cooking.buffs[mb] && ck.mealDay === game.dayNight.day) ck.buffs.add(mb);

    // 8) teleport (region first), then pools clamped to the maxes
    var rid = validRegion(P.regionId) ? P.regionId : game.regionManager.logic.activeId;
    if (rid !== game.regionManager.logic.activeId && hooks.switchRegion) hooks.switchRegion(rid);
    var pos = Array.isArray(P.pos) ? P.pos : [p.pos.x, p.pos.z];
    p.respawnAt(num(pos[0], p.pos.x), num(pos[1], p.pos.z));   // alive, combat state cleared
    var yaw = num(P.yaw, p.yaw);
    p.yaw = yaw;
    p.camYaw = yaw + Math.PI;
    if (p.yawFrame) p.yawFrame.rotation.y = yaw;
    // respawnAt reset both hands' cast state: the restored implements re-grip
    if (p.isCasterHand('right')) p.cast.main.regrip = CFG.belt.regripSeconds;
    if (p.isCasterHand('left')) p.cast.off.regrip = CFG.belt.regripSeconds;
    if (hooks.applyBuffStats) hooks.applyBuffStats();
    p.hp = Math.min(p.hpMax, Math.max(1, num(P.hp, p.hpMax)));
    p.focus = Math.min(p.focusMax, Math.max(0, num(P.focus, p.focusMax)));
    p.stamina = Math.min(p.staminaMax, Math.max(0, num(P.stamina, p.staminaMax)));
    ck.lastHp = p.hp;                // no phantom cook-interrupt hit
    if (game.inventoryUI) game.inventoryUI.render();
  }

  window.WH_SAVE = {
    capture: capture,
    restore: restore,
    save: save,
    load: load,
    has: has
  };
  void wipe;                        // wipe() stays internal: no UI / key / export reaches it
})();
