// CC-WB3 strata requisition board (doc 42 Part 3 delve-chain loop; IO spec
// io/specs/cc-wb3-strata-board-spec.md). Generalizes js/wareffort.js (CC-WB1,
// NOT edited this round) onto a second board: same IIFE + WB1 API surface
// (init / tryOpen / interactPrompt / capture / restore / boardPos), same
// one-day contract law, NO WB2 ladder math (fixed CONFIG pay per fill) and no
// over-band - the board buys the CC-C7 delve harvest (rot-silk + rot-gland)
// for a fixed coin reward. Reads CFG.strataEffort ONLY. State rides the save
// wrap (B-5) exactly like the war board.
;(function () {
  'use strict';
  var CFG = window.WH_CONFIG;
  var JT = (CFG.journal && CFG.journal.topics) || null;   // QJR-3 voice, CC-WB3 topic
  var S = CFG.strataEffort || {};
  var game = null, body = null, papers = null;

  // B-3 state model: the payload is exactly three keys (B-5) - NO repeatIndex
  // ladder this round (CC-WB2's ladder stays WB1-only; deliberate scope cut).
  var logic = { postedDay: null, active: false, resolvedDay: null };

  function dayNumber() {
    return (game && game.dayNight && typeof game.dayNight.day === 'number') ? game.dayNight.day : 0;
  }

  // WB1 inv() grammar: game.inventory first, WH_INVENTORY fallback; no slot
  // poking, no facade bypass.
  function inv() {
    var gi = game && game.inventory;
    if (gi && typeof gi.addItem === 'function' && typeof gi.countOf === 'function') return gi;
    return window.WH_INVENTORY || null;
  }
  function matHave(id) {
    var bag = inv();
    return bag && typeof bag.countOf === 'function' ? (bag.countOf(id) || 0) : 0;
  }
  function toast(t) {
    if (game && game.inventoryUI && typeof game.inventoryUI.toast === 'function') {
      game.inventoryUI.toast(t);
    }
  }

  // Board body: the ONLY scene object this round (engine untouched, art law).
  // CC-WB1 board grammar re-dressed per concept-06-siege-council: two oak
  // posts, dark board face, 2 parchment sheets, iron bracket strip, THE ONE
  // amber emissive lantern (0xffb347 - the ONLY emissive; no crimson, no
  // second light). Every node name carries the cc-wb3- prefix.
  function setPapersVisible(v) {
    if (!papers) return;
    for (var i = 0; i < papers.length; i++) papers[i].visible = !!v;
  }

  function buildBody() {
    var root = new THREE.Group();
    root.name = 'cc-wb3-strata-effort-board';
    var oak = new THREE.MeshStandardMaterial({ color: 0x4a3a2a, roughness: 1 });
    var dark = new THREE.MeshStandardMaterial({ color: 0x3d2b1f, roughness: 0.95 });
    var parch = new THREE.MeshStandardMaterial({ color: 0xd2b48c, roughness: 1,
      side: THREE.DoubleSide });
    var iron = new THREE.MeshStandardMaterial({ color: 0x6e6a63, roughness: 0.8, metalness: 0.4 });
    var pl = new THREE.Mesh(new THREE.BoxGeometry(0.18, 2.2, 0.18), oak);   // left post
    pl.name = 'cc-wb3-post-left';
    pl.position.set(-0.8, 1.1, 0); root.add(pl);
    var pr = pl.clone();                                                    // right post
    pr.name = 'cc-wb3-post-right'; pr.position.x = 0.8; root.add(pr);
    var frame = new THREE.Mesh(new THREE.BoxGeometry(1.6, 1.1, 0.12), dark);
    frame.name = 'cc-wb3-board-face';
    frame.position.y = 1.5; root.add(frame);                                // board face
    papers = [];
    for (var i = 0; i < 2; i++) {                                           // 2 parchment sheets
      var p = new THREE.Mesh(new THREE.PlaneGeometry(0.48, 0.62), parch);
      p.name = 'cc-wb3-sheet-' + (i + 1);
      p.position.set(-0.25 + i * 0.5, 1.5 + (i - 0.5) * 0.12, 0.08);
      p.rotation.y = (i - 0.5) * 0.12;                                      // nail slouch jitter
      root.add(p); papers.push(p);
    }
    var strip = new THREE.Mesh(new THREE.BoxGeometry(1.7, 0.09, 0.05), iron);
    strip.name = 'cc-wb3-iron-strip';
    strip.position.set(0, 2.0, 0.08); root.add(strip);                      // iron bracket strip
    var arm = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.05, 0.05), iron);
    arm.name = 'cc-wb3-lantern-arm';
    arm.position.set(0.68, 2.34, 0.1); root.add(arm);                       // lantern arm
    var lamp = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.22, 0.16),
      new THREE.MeshStandardMaterial({ color: 0x332a1a, roughness: 0.6,
        emissive: 0xffb347, emissiveIntensity: 0.9 }));                     // THE one amber accent
    lamp.name = 'cc-wb3-lantern';
    lamp.position.set(0.85, 2.26, 0.1); root.add(lamp);
    root.position.set(SEAT.x, 0, SEAT.z);          // Lord's Hold hub is FLAT: y = 0
    root.rotation.y = SEAT.rotY;                                             // faces west to the gate lane
    game.scene.add(root);
    return root;
  }

  var seatCfg = S.boardSeat || {};
  var SEAT = (typeof seatCfg.x === 'number') ? seatCfg
    : { regionId: 'lords_hold', x: 6.0, z: -782.0, rotY: 4.712 };
  var mats = (S.mats && S.mats.length) ? S.mats
    : [{ id: 'rot-silk', quota: 4 }, { id: 'rot-gland', quota: 2 }];
  var ITEM = S.itemId || 'strataOrder';
  var REWARD = S.reward || { id: 'stolenCoin', count: 5 };

  // Proximity gate (WB1/chest.js law): region-gated, alive + not suspended.
  // Radius PROPOSED 2.6 (chest feel, WB1 verbatim grammar).
  function near() {
    if (!game || !game.player || !game.player.pos) return false;
    if (game.regionManager) {
      var activeId = game.regionManager.logic.activeId;
      if (activeId !== SEAT.regionId) return false;
    }
    var p = game.player.pos;
    var r = 2.6;                       // PROPOSED, chest-feel (WB1 radius)
    return game.player.state === 'alive' && !game.player.inputSuspended &&
      Math.hypot(p.x - SEAT.x, p.z - SEAT.z) <= r;
  }

  // ONE-DAY CONTRACT LAW (WB1 verbatim): one contract per day. Interaction-time
  // roll only - no timers, no tick hook anywhere. A resolved board re-arms at
  // the NEXT dawn.
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
      var added = bag ? (bag.addItem(ITEM, 1) || 0) : 0;
      if (added < 1) { toast('Your satchel is full.'); return true; }
      logic.active = true;
      logic.postedDay = dayNumber();
      toast(S.offerText || 'The quartermaster wants rot-silk and rot-gland from the delve strata below.');
      if (JT && JT.strata && window.WH_JOURNAL) window.WH_JOURNAL.append(JT.strata.id, JT.strata.title, JT.strata.body, undefined, JT.strata.source);  // CC-WB3 award
      return true;
    }
    // active: EVERY mat must meet its quota (A >= q AND B >= q); the toast
    // carries the HAVE counts of the pair at press. Removes EXACTLY quota of
    // each - surplus stays in the bag (no haul law, no over-band this round).
    var haves = [], short = -1;
    for (var i = 0; i < mats.length; i++) {
      haves[i] = matHave(mats[i].id);
      if (short < 0 && haves[i] < mats[i].quota) short = i;
    }
    if (short >= 0 || !bag) {
      toast('Not enough ' + mats[0].id + '/' + mats[1].id + ' for the strata order. (' + haves[0] + '/' + haves[1] + ')');
      return true;
    }
    var taken = [];
    for (var j = 0; j < mats.length; j++) {         // never partially charge (defensive)
      taken[j] = bag.removeItem(mats[j].id, mats[j].quota) || 0;
    }
    for (var k = 0; k < taken.length; k++) {
      if (taken[k] < mats[k].quota) {               // unexpected short removal: put it all back
        for (var n = 0; n < taken.length; n++) {
          if (taken[n] > 0) bag.addItem(mats[n].id, taken[n]);
        }
        toast('Not enough ' + mats[0].id + '/' + mats[1].id + ' for the strata order. (' + haves[0] + '/' + haves[1] + ')');
        return true;
      }
    }
    var granted = bag.addItem(REWARD.id, REWARD.count) || 0;   // fixed CONFIG pay
    logic.active = false;
    logic.resolvedDay = dayNumber();
    setPapersVisible(false);                        // papers hidden on resolve
    if (JT && JT.strata && window.WH_JOURNAL) window.WH_JOURNAL.append(JT.strata.id, JT.strata.title, JT.strata.body, undefined, JT.strata.source);  // CC-WB3 fill
    if (window.WH_AFF) window.WH_AFF.deed('strataFill');   // CC-AF1: a fill moves the standing
    toast(S.doneText || 'Strata requisition filled.');
    return granted >= 0 || true;
  }

  function open() { return false; }   // this round the board never holds a modal

  function interactPrompt() {
    if (!near()) return '';
    rollNewDay();
    if (spentToday()) return 'The board is spent until dawn.';
    if (logic.active) {
      // needs-list from CONFIG counts (no have-counts on this board)
      return 'E - Strata Board (needs ' + mats[0].quota + ' ' + mats[0].id +
        ' + ' + mats[1].quota + ' ' + mats[1].id + ')';
    }
    return 'E - Strata Board (Take a requisition)';
  }

  // B-5 persistence: the payload is EXACTLY 3 keys (repeatIndex-free). Restore
  // merges the known shape; a missing or foreign payload = no-op (fresh idle
  // board keeps default state); per-key V-5n clamps (boolean/number types,
  // anything else = default). Papers visibility resets on restore.
  function capture() {
    return { active: logic.active, postedDay: logic.postedDay, resolvedDay: logic.resolvedDay };
  }
  function restore(data) {
    if (!data || typeof data !== 'object') return;
    if (typeof data.active !== 'boolean' &&
        typeof data.postedDay !== 'number' &&
        typeof data.resolvedDay !== 'number') {
      return;                                        // foreign payload = no-op
    }
    logic.active = data.active === true;
    logic.postedDay = typeof data.postedDay === 'number' ? data.postedDay : null;
    logic.resolvedDay = typeof data.resolvedDay === 'number' ? data.resolvedDay : null;
    setPapersVisible(!spentToday());
  }

  function boardPos() { return { x: SEAT.x, z: SEAT.z }; }

  // HEADLESS-SAFE: visuals only when a scene + THREE exist (node one-shots
  // with game.scene === null skip buildBody entirely; no throw).
  function init(g) {
    game = g;
    if (game && game.scene && window.THREE) body = buildBody();
  }

  window.WH_StrataEffort = { init: init, tryOpen: tryOpen, interactPrompt: interactPrompt,
    capture: capture, restore: restore, boardPos: boardPos };
})();
