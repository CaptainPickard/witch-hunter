// CC-WB1 war-effort requisition board (doc 42 Part 3 entry tier; doc 37-C11
// lifecycle). IO spec io/specs/cc-wb1-warboard-spec.md; module per chest.js
// conventions (IIFE, game couplings, proximity gate, save-wrap payload).
// 2026-11-06 note: the first Devbot build of this file was overwritten by an
// orphaned dispatch; this version is the IO-inline rebuild against the same
// spec + the surviving turn-in smoke (/tmp/wb1_smoke2.js, 34 checks).
;(function () {
  'use strict';
  var CFG = window.WH_CONFIG;
  var JT = CFG.journal && CFG.journal.topics;  // QJR-3
  var W = CFG.warEffort || {};
  var RQ = W.requisition || {};
  var game = null, body = null, papers = null, tallyGroup = null;

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  // B-3 state model: the payload is three keys (B-5) + CC-WB2 repeatIndex.
  var logic = { postedDay: null, active: false, resolvedDay: null, repeatIndex: 0 };

  // S-2: one resolution (fill) = one repeat: resolve() increments once.
  function resolve() { logic.repeatIndex = logic.repeatIndex + 1; }

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
    // CC-WB2 repeat tally (S-3): sub-group INSIDE the board root; pins reuse
    // the board's own iron material (0x6e6a63), NO red, no second emissive.
    var tally = new THREE.Group();       // sub-group INSIDE the board root (S-3)
    tally.name = 'cc-wb2-repeat-tally';
    tally.position.set(0.62, 1.5, 0.09); // board right side, parchment strip free spot
    root.add(tally);
    tallyGroup = tally;
    pinsMat = iron;
    rebuildTallyPins();
    root.position.set(SEAT.x, 0, SEAT.z);                            // region A FLAT: y = 0
    root.rotation.y = SEAT.rotY;
    game.scene.add(root);
    return root;
  }

  // S-3: one iron pin per repeat along the lower frame front lip,
  // LEFT to RIGHT, cap 8 (render min(repeatIndex, 8)).
  var pinsMat = null;

  function rebuildTallyPins() {
    var tally = tallyGroup;
    if (!tally || !window.THREE) return;   // headless one-shots skip visuals
    while (tally.children.length) tally.remove(tally.children[0]);
    var n = Math.min(logic.repeatIndex, 8);
    for (var k = 0; k < n; k++) {
      var pin = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.05, 0.12),
        pinsMat || undefined);
      pin.position.set(-0.42 + k * 0.12, 1.02, 0.08);
      tally.add(pin);
    }
  }

  var seatCfgW = W.boardSeat || {};
  var SEAT = (typeof seatCfgW.x === 'number') ? seatCfgW
    : { x: 5.9, z: -15.5, rotY: 3.14 };
  var LAD = W.ladder || null;          // CC-WB2 (doc 42 Part 2): null = WB1 economics

  // S-2 payout law: integer milli-unit (m4 = 1/10000 coin) money math, no
  // floats in state. baseM4(r) = 5000 + 750*r exact; quotaQ(r) =
  // min(round(6*1.5^r), 18) = round-half-up growth with the 3x cap; the
  // over-band bonus rate k climbs +10%/item (cap +100%), bonuses stack from k=1.
  function baseM4(r) {
    r = Math.max(0, Math.floor(r) || 0);
    return 5000 + 750 * r;
  }
  function quotaQ(r) {
    r = Math.max(0, Math.floor(r) || 0);
    var base = (typeof RQ.oreRequired === 'number') ? RQ.oreRequired : 6;
    var grows = 1 + (LAD ? LAD.repeatQuotaGrowthPct : 0) / 100;
    var q = Math.round(base * Math.pow(grows, r));
    var capQ = LAD ? LAD.repeatQuotaCapMult * base : base;
    return Math.min(q, capQ);
  }
  function ratePct(k) {
    var cap = LAD ? 100 + LAD.overBonusCapPct : 100;
    return Math.min(100 + (LAD ? LAD.overBonusStepPct : 0) * k, cap);
  }
  function bonusM4(k, r) { return Math.floor(baseM4(r) * ratePct(k) / 100); }
  function payM4(ore, r) {
    var q = quotaQ(r);
    var pay = baseM4(r) * q;
    var x = ore - q;
    for (var i = 1; i <= x; i++) pay += bonusM4(i, r);
    return pay;
  }
  function coinsFrom(pay) { return Math.floor((pay + 5000) / 10000); }

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
      var awardQuota = quotaQ(logic.repeatIndex);   // S-2: quota is set at award time
      toast(RQ.offerText || 'The garrison wants iron for the war.');
      if (JT && window.WH_JOURNAL) window.WH_JOURNAL.append(JT.requisition.id, JT.requisition.title, JT.requisition.body, undefined, JT.requisition.source);  // QJR-3
      return true;
    }
    // active: fill the requisition (37-C11 law). CC-WB2: the quota climbs per
    // repeat (S-2 quotaQ), the whole carried haul of the ore id is turned in
    // (haul grammar), and the pay is exact integer milli-units per S-2.
    var quota = quotaQ(logic.repeatIndex);
    var have = oreCount();
    if (have < quota) {
      toast('Not enough iron ore. (' + have + '/' + quota + ')');
      return true;
    }
    var removed = bag.removeItem(RQ.oreItemId, have);
    if (removed < have) {               // never partially charge (defensive)
      if (removed > 0) bag.addItem(RQ.oreItemId, removed);
      toast('Not enough iron ore. (' + have + '/' + quota + ')');
      return true;
    }
    var pay = payM4(have, logic.repeatIndex);
    var coins = coinsFrom(pay);
    var granted = bag.addItem(RQ.reward.id, coins) || 0;
    var over = have - quota;
    resolve();
    logic.active = false;
    logic.resolvedDay = dayNumber();
    setPapersVisible(false);
    rebuildTallyPins();                 // S-3: rebuilt on resolve
    if (JT && window.WH_JOURNAL) window.WH_JOURNAL.append(JT.firstFill.id, JT.firstFill.title, JT.firstFill.body, undefined, JT.firstFill.source);  // QJR-3
    if (window.WH_AFF) window.WH_AFF.deed('warEffortFill');   // CC-AF1: a fill moves the standing
    toast(over >= 1
      ? (LAD && LAD.overDoneText || 'Requisition filled. The quartermaster pays a bonus for the extra iron.')
      : (RQ.doneText || 'Requisition filled.'));
    return granted > 0 || true;
  }

  function open() { return false; }   // this round the board never holds a modal

  function interactPrompt() {
    if (!near()) return '';
    rollNewDay();
    if (spentToday()) return 'The board is spent until dawn.';
    if (logic.active) {
      var quota = quotaQ(logic.repeatIndex);      // award/turn-in share quotaQ (S-2)
      return 'E - War Board (' + oreCount() + '/' + quota + ' iron ore)';
    }
    return 'E - War Board (Take a requisition)';
  }

  // B-5 persistence: the payload keys; restore merges known shape, missing or
  // foreign payload = no-op (fresh idle board keeps default state). CC-WB2:
  // the payload gains repeatIndex (4 keys), and restores clamp it to a
  // non-negative int (missing/foreign/negative = 0); WB1 3-key payloads
  // (repeatIndex absent) restore clean as repeatIndex 0.
  function capture() {
    return { active: logic.active, postedDay: logic.postedDay, resolvedDay: logic.resolvedDay,
      repeatIndex: logic.repeatIndex };
  }
  function restore(data) {
    if (!data || typeof data !== 'object') return;
    if (typeof data.active !== 'boolean' &&
        typeof data.postedDay !== 'number' &&
        typeof data.resolvedDay !== 'number' &&
        typeof data.repeatIndex !== 'number') {
      return;                                        // foreign payload = no-op
    }
    logic.active = data.active === true;
    logic.postedDay = typeof data.postedDay === 'number' ? data.postedDay : null;
    logic.resolvedDay = typeof data.resolvedDay === 'number' ? data.resolvedDay : null;
    var ri = data.repeatIndex;
    // V-5n clamp law: kept only when a finite non-negative INTEGER; anything
    // else (missing / string / fractional / negative / Infinity) = foreign = 0.
    if (typeof ri !== 'number' || !isFinite(ri) || ri < 0 || Math.floor(ri) !== ri) ri = 0;
    logic.repeatIndex = ri;
    rebuildTallyPins();                              // S-3: rebuilt on restore
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
