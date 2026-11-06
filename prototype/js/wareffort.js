// CC-WB1 war-effort requisition board (doc 42 Part 3 entry tier; doc 37-C11
// lifecycle). IO spec io/specs/cc-wb1-warboard-spec.md; module per chest.js
// conventions (IIFE, game couplings, proximity gate, save-wrap payload).
// 2026-11-06 note: the first Devbot build of this file was overwritten by an
// orphaned dispatch; this version is the IO-inline rebuild against the same
// spec + the surviving turn-in smoke (/tmp/wb1_smoke2.js, 34 checks).
;(function () {
  'use strict';
  var CFG = window.WH_CONFIG;
  var W = CFG.warEffort || {};
  var RQ = W.requisition || {};
  var game = null, body = null, papers = null;

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  // B-3 state model: the whole payload is these three keys (B-5).
  var logic = { postedDay: null, active: false, resolvedDay: null };

  function dayNumber() {
    return (game && game.dayNight && typeof game.dayNight.day === 'number') ? game.dayNight.day : 0;
  }

  function inv() {
    var gi = game && game.inventory;
    if (gi && typeof gi.addItem === 'function' && typeof gi.countOf === 'function') return gi;
    return window.WH_INVENTORY || null;
  }
  function oreCount() {
    var bag = inv();
    return bag && typeof bag.countOf === 'function' ? (bag.countOf(RQ.oreItemId) || 0) : 0;
  }
  function toast(t) {
    if (game && game.inventoryUI && typeof game.inventoryUI.toast === 'function') {
      game.inventoryUI.toast(t);
    }
  }

  // Board body: the ONLY scene object this round (engine untouched, art law).
  // Dark-oak two-post board per the concept-04-tavern anchor: desaturated
  // oak/parchment, ONE amber emissive lantern = the single warm accent.
  function setPapersVisible(v) {
    if (!papers) return;
    for (var i = 0; i < papers.length; i++) papers[i].visible = !!v;
  }

  function buildBody() {
    var root = new THREE.Group();
    root.name = 'cc-wb1-war-effort-board';
    var oak = new THREE.MeshStandardMaterial({ color: 0x4a3a2a, roughness: 1 });
    var dark = new THREE.MeshStandardMaterial({ color: 0x3d2b1f, roughness: 0.95 });
    var parch = new THREE.MeshStandardMaterial({ color: 0xd2b48c, roughness: 1,
      side: THREE.DoubleSide });
    var iron = new THREE.MeshStandardMaterial({ color: 0x6e6a63, roughness: 0.8, metalness: 0.4 });
    var pl = new THREE.Mesh(new THREE.BoxGeometry(0.18, 2.2, 0.18), oak);
    pl.position.set(-0.8, 1.1, 0); root.add(pl);                     // left post
    var pr = pl.clone(); pr.position.x = 0.8; root.add(pr);          // right post
    var frame = new THREE.Mesh(new THREE.BoxGeometry(1.6, 1.1, 0.12), dark);
    frame.position.y = 1.5; root.add(frame);                         // board face
    papers = [];
    for (var i = 0; i < 3; i++) {                                    // parchment papers
      var p = new THREE.Mesh(new THREE.PlaneGeometry(0.48, 0.62), parch);
      p.position.set(-0.5 + i * 0.5, 1.5 + (i - 1) * 0.06, 0.08);
      p.rotation.y = (i - 1) * 0.06;                                 // nail slouch jitter
      root.add(p); papers.push(p);
    }
    var strip = new THREE.Mesh(new THREE.BoxGeometry(1.7, 0.09, 0.05), iron);
    strip.position.set(0, 2.0, 0.08); root.add(strip);               // iron bracket strip
    var arm = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.05, 0.05), iron);
    arm.position.set(0.68, 2.34, 0.1); root.add(arm);                // lantern arm
    var lamp = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.22, 0.16),
      new THREE.MeshStandardMaterial({ color: 0x332a1a, roughness: 0.6,
        emissive: 0xffb347, emissiveIntensity: 0.9 }));              // THE one amber accent
    lamp.name = 'cc-wb1-lantern';
    lamp.position.set(0.85, 2.26, 0.1); root.add(lamp);
    root.position.set(SEAT.x, 0, SEAT.z);                            // region A FLAT: y = 0
    root.rotation.y = SEAT.rotY;
    game.scene.add(root);
    return root;
  }

  var SEAT = (W.boardSeat && typeof W.boardSeat.x === 'number')
    ? W.boardSeat : { x: 5.9, z: -15.5, rotY: 3.14 };

  // Proximity gate (chest.js law): region-gated, CONFIG radius, alive + not
  // suspended. Radius PROPOSED 2.6 (chest feel).
  function near() {
    if (!game || !game.player || !game.player.pos) return false;
    if (game.regionManager) {
      var activeId = game.regionManager.logic.activeId;
      if (activeId !== SEAT.regionId) return false;
    }
    var p = game.player.pos;
    var r = 2.6;                       // PROPOSED, chest-feel
    return game.player.state === 'alive' && !game.player.inputSuspended &&
      Math.hypot(p.x - SEAT.x, p.z - SEAT.z) <= r;
  }

  // NEW DAY LAW (doc 42 cadence): one contract per day. Interaction-time roll
  // only - no timers, no tick hook. A resolved board resets at the NEXT dawn.
  function rollNewDay() {
    var d = dayNumber();
    if (logic.resolvedDay !== null && d > logic.resolvedDay) {
      logic.active = false; logic.postedDay = null; logic.resolvedDay = null;
      setPapersVisible(true);
    }
  }

  function spentToday() {
    return logic.resolvedDay !== null && logic.resolvedDay === dayNumber();
  }

  function tryOpen() {
    if (!near() || open()) return false;
    rollNewDay();
    if (spentToday()) return true;                 // press consumed, board does nothing
    var bag = inv();
    if (!logic.active) {                            // idle: award the requisition paper
      var added = bag ? (bag.addItem(RQ.itemId, 1) || 0) : 0;
      if (added < 1) { toast('Your satchel is full.'); return true; }
      logic.active = true;
      logic.postedDay = dayNumber();
      toast(RQ.offerText || 'The garrison wants iron for the war.');
      return true;
    }
    // active: fill the requisition (37-C11 single reward authority = RQ.reward)
    var have = oreCount();
    if (have < RQ.oreRequired) {
      toast('Not enough iron ore. (' + have + '/' + RQ.oreRequired + ')');
      return true;
    }
    var removed = bag.removeItem(RQ.oreItemId, RQ.oreRequired);
    if (removed < RQ.oreRequired) {                 // never partially charge (defensive)
      if (removed > 0) bag.addItem(RQ.oreItemId, removed);
      toast('Not enough iron ore. (' + have + '/' + RQ.oreRequired + ')');
      return true;
    }
    var granted = bag.addItem(RQ.reward.id, RQ.reward.count) || 0;
    logic.active = false;
    logic.resolvedDay = dayNumber();
    setPapersVisible(false);
    toast(RQ.doneText || 'Requisition filled.');
    return granted > 0 || true;
  }

  function open() { return false; }   // this round the board never holds a modal

  function interactPrompt() {
    if (!near()) return '';
    rollNewDay();
    if (spentToday()) return 'The board is spent until dawn.';
    if (logic.active) return 'E - War Board (' + oreCount() + '/' + RQ.oreRequired + ' iron ore)';
    return 'E - War Board (Take a requisition)';
  }

  // B-5 persistence: exactly the payload keys; restore merges known shape,
  // missing/foreign block = no-op (fresh idle board keeps default state).
  function capture() {
    return { active: logic.active, postedDay: logic.postedDay, resolvedDay: logic.resolvedDay };
  }
  function restore(data) {
    if (!data || typeof data !== 'object') return;
    var known = 'active' in data || 'postedDay' in data || 'resolvedDay' in data;
    if (!known) return;
    logic.active = data.active === true;
    logic.postedDay = typeof data.postedDay === 'number' ? data.postedDay : null;
    logic.resolvedDay = typeof data.resolvedDay === 'number' ? data.resolvedDay : null;
    setPapersVisible(!spentToday());
  }

  function boardPos() { return { x: SEAT.x, z: SEAT.z }; }

  function init(g) {
    game = g;
    if (game && game.scene && window.THREE) body = buildBody();
  }

  window.WH_WarEffort = { init: init, tryOpen: tryOpen, interactPrompt: interactPrompt,
    capture: capture, restore: restore, boardPos: boardPos };
})();
