// CC-WB1 war-effort requisition board (doc 42 Part 3 entry tier; doc 37-C11
// lifecycle). IO spec io/specs/cc-wb1-warboard-spec.md; module per chest.js
// conventions (IIFE, game couplings, proximity gate, save-wrap payload).
// 2026-11-06 note: the first Devbot build of this file was overwritten by an
// orphaned dispatch; this version is the IO-inline rebuild against the same
// spec + the surviving turn-in smoke (/tmp/wb1_smoke2.js, 34 checks).
// CC-WB4 standing stone (io/specs/cc-wb4-standing-stone-spec.md, 2026-11-08):
// the repeat standing gate (repeatStanding re-post bar) + the three-resolve
// requisition stone tier-up (4x quota cap, x1.3 base pay) on THIS board; the
// state payload gains stoneSeen (S-3), and a standing-stone dressing of
// plinth + pole + pennant rides the board root (S-5, zero new assets).
;(function () {
  'use strict';
  var CFG = window.WH_CONFIG;
  var JT = CFG.journal && CFG.journal.topics;  // QJR-3
  var W = CFG.warEffort || {};
  var RQ = W.requisition || {};
  var game = null, body = null, papers = null, tallyGroup = null;
  var stoneGroup = null;
  // CC-WB4 standing layer (io/specs/cc-wb4-standing-stone-spec.md S-2): ST =
  // the requisition stone block, RS = the repeat standing bar. null = the
  // feature is OFF and the landed WB2 behavior holds verbatim (older-profile
  // safety law; the CONFIG.js shipped this round always carries both).
  var ST = W.stone || null;
  var RS = (typeof W.repeatStanding === 'number') ? W.repeatStanding : null;

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  // B-3 state model: the payload is three keys (B-5) + CC-WB2 repeatIndex
  // + CC-WB4 stoneSeen (S-3: one key, never regresses, no reset path).
  var logic = { postedDay: null, active: false, resolvedDay: null, repeatIndex: 0,
    stoneSeen: false };

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
    // CC-WB2: sub-group INSIDE the board root; pins reuse the board's own
    // iron material (0x6e6a63), NO red, no second emissive.
    var tally = new THREE.Group();       // sub-group INSIDE the board root (S-3)
    tally.name = 'cc-wb2-repeat-tally';
    tally.position.set(0.62, 1.5, 0.09); // board right side, parchment strip free spot
    root.add(tally);
    tallyGroup = tally;
    // CC-WB4 stone dressing (S-5): second sub-group INSIDE the board root;
    // the three meshes are added by rebuildStoneDressing() at r >= 3. Zero
    // new scene roots, no red, no second emissive (board's own materials).
    var stonesub = new THREE.Group();
    stonesub.name = 'cc-wb4-stone-dressing';
    root.add(stonesub);
    stoneGroup = stonesub;
    pinsMat = iron;
    boardMats.oak = oak;
    boardMats.parch = parch;
    rebuildTallyPins();
    rebuildStoneDressing();             // CC-WB4 S-5: r0 = cleared group, byte-silent
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

  // CC-WB4 standing layer (io/specs/cc-wb4-standing-stone-spec.md S-2):
  function stoneActive() {
    return !!(ST && logic.repeatIndex >= ST.thresholdRepeats);
  }

  // S-2.3 stone crossing: ONCE per lifetime, persisted via logic.stoneSeen.
  // Sets the flag, appends the warEffortStone journal topic once (JT/row
  // shape of the landed firstFill append), and toasts ST.crossingToast.
  // Wired at resolve() (fill path) and at restore() (WB2 payloads already
  // past the threshold carry no flag = the crossing legitimately fires there).
  // The crossing pays NO deed - only the fill's landed warEffortFill moves
  // standing (S-5). The flag is set FIRST and the append is guarded, so a
  // missing journal can never wedge the crossing into repeat-firing.
  function stoneCrossing() {
    if (!ST || logic.repeatIndex < ST.thresholdRepeats || logic.stoneSeen) return;
    logic.stoneSeen = true;
    if (JT && window.WH_JOURNAL) {
      window.WH_JOURNAL.append(JT.warEffortStone.id, JT.warEffortStone.title,
        JT.warEffortStone.body, undefined, JT.warEffortStone.source);
    }
    toast(ST.crossingToast);
  }

  // S-5 dressing (zero new assets): three meshes inside a sub-group of the
  // EXISTING board root, mirroring rebuildTallyPins() exactly (clear-then-
  // fill, guard on the group + window.THREE; null ST or r below threshold =
  // cleared group, byte-silent). Plinth carries the EXISTING stone-gray
  // palette token, pole + pennant reuse the board's own oak/parch materials;
  // no red, no second emissive, zero new scene roots.
  var boardMats = { oak: null, parch: null };   // board material registry (S-5)

  function rebuildStoneDressing() {
    var grp = stoneGroup;
    if (!grp || !window.THREE) return;     // headless one-shots skip visuals
    while (grp.children.length) grp.remove(grp.children[0]);
    if (!stoneActive()) return;
    var stone = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.5, 0.45),
      new THREE.MeshStandardMaterial({ color: 0x8a8577, roughness: 1.0 }));
    stone.position.set(-0.55, 0.25, -0.35);
    grp.add(stone);                        // plinth: ground stone base
    var pole = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.8, 0.04),
      boardMats.oak);
    pole.position.set(-0.8, 2.6, 0.1);
    grp.add(pole);                         // pole: rises from the left post cap
    var pennant = new THREE.Mesh(new THREE.PlaneGeometry(0.4, 0.28),
      boardMats.parch);
    pennant.position.set(-0.58, 2.78, 0.1);
    grp.add(pennant);                      // pennant: parchment pane (board's own)
  }

  var seatCfgW = W.boardSeat || {};
  var SEAT = (typeof seatCfgW.x === 'number') ? seatCfgW
    : { x: 5.9, z: -15.5, rotY: 3.14 };
  var LAD = W.ladder || null;          // CC-WB2 (doc 42 Part 2): null = WB1 economics

  // S-2 payout law: integer milli-unit (m4 = 1/10000 coin) money math, no
  // floats in state. baseM4(r) = 5000 + 750*r exact; quotaQ(r) =
  // min(round(6*1.5^r), 18) = round-half-up growth with the 3x cap; the
  // over-band bonus rate k climbs +10%/item (cap +100%), bonuses stack from k=1.
  // CC-WB4 S-2.1 (stone tier, only when ST && r >= ST.thresholdRepeats):
  // quota cap mult lifts to ST.quotaCapMult (cap = mult x base) and base pay
  // lifts x ST.payPct/100 with the exact milli-unit floor; the growth
  // formula, the base and the round() stay UNTOUCHED, so the raise is
  // monotone (r3 20, r4+ pegged 24, never a drop).
  function baseM4(r) {
    r = Math.max(0, Math.floor(r) || 0);
    var m4 = 5000 + 750 * r;
    if (ST && r >= ST.thresholdRepeats && typeof ST.payPct === 'number') {
      m4 = Math.floor(m4 * ST.payPct / 100);
    }
    return m4;
  }
  function quotaQ(r) {
    r = Math.max(0, Math.floor(r) || 0);
    var base = (typeof RQ.oreRequired === 'number') ? RQ.oreRequired : 6;
    var grows = 1 + (LAD ? LAD.repeatQuotaGrowthPct : 0) / 100;
    var q = Math.round(base * Math.pow(grows, r));
    var capQ = LAD ? LAD.repeatQuotaCapMult * base : base;
    if (ST && r >= ST.thresholdRepeats) capQ = ST.quotaCapMult * base;  // CC-WB4
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
      // CC-WB4 S-2.2 standing gate (re-post bar; RS null = feature OFF and
      // the landed WB2 idle branch holds verbatim): beyond the FIRST
      // contract of the ladder (r0 idle stays open to everyone), the board
      // re-posts only while standing meets CONFIG.warEffort.repeatStanding.
      // Press consumed, waiting toast, NO paper, NO day (postedDay stays
      // null); standing recovers by the landed deeds, so never a deadlock.
      if (RS !== null && logic.repeatIndex >= 1) {
        var score = (window.WH_AFF && typeof window.WH_AFF.score === 'function')
          ? window.WH_AFF.score() : 0;
        if (score < RS) {
          toast('The quartermaster waits on your standing. Deeds will speak.');
          return true;
        }
      }
      var added = bag ? (bag.addItem(RQ.itemId, 1) || 0) : 0;
      if (added < 1) { toast('Your satchel is full.'); return true; }
      logic.active = true;
      logic.postedDay = dayNumber();
      var awardQuota = quotaQ(logic.repeatIndex);   // S-2: quota is set at award time
      // CC-WB4 S-2.5: stone tier awards speak the stone voice (the journal
      // requisition topic append is UNCHANGED - QJR-3 rows stay for the board).
      toast(stoneActive() && ST.offerText
        || RQ.offerText || 'The garrison wants iron for the war.');
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
    rebuildStoneDressing();             // CC-WB4 S-5: rebuilt on resolve
    stoneCrossing();                    // CC-WB4 S-2.3: AFTER resolve, BEFORE the done toast
    if (JT && window.WH_JOURNAL) window.WH_JOURNAL.append(JT.firstFill.id, JT.firstFill.title, JT.firstFill.body, undefined, JT.firstFill.source);  // QJR-3
    if (window.WH_AFF) window.WH_AFF.deed('warEffortFill');   // CC-AF1: a fill moves the standing
    // CC-WB4 S-2.5: the fill toast reads the POST-resolve tier - stone tier
    // toasts ST.doneText; the over-band keeps the landed overDoneText
    // preference at ANY tier (over >= 1 wins, as landed).
    toast(over >= 1
      ? (LAD && LAD.overDoneText || 'Requisition filled. The quartermaster pays a bonus for the extra iron.')
      : (stoneActive() && ST.doneText
        || RQ.doneText || 'Requisition filled.'));
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
  // the payload gained repeatIndex; CC-WB4 (S-3) it gains stoneSeen (5-key
  // payload). Restore shape law (S-3, verbatim per spec):
  //   stoneSeen === true  -> flag true
  //   missing / not true  -> flag false (payloads WITHOUT the key read as
  //   never-reached = flag false, NOT foreign). RollNewDay is UNTOUCHED; the
  //   flag never regresses (no key delete, no reset path). WB1/WB2 3-/4-key
  //   payloads restore clean with stoneSeen false.
  function capture() {
    return { active: logic.active, postedDay: logic.postedDay, resolvedDay: logic.resolvedDay,
      repeatIndex: logic.repeatIndex, stoneSeen: logic.stoneSeen };
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
    // CC-WB4 S-3 flag law: the key rides the shape merge - ONLY a literal
    // boolean true sets it; everything else (absent key, null, 1, 'true')
    // restores false. A payload BELOW the threshold cannot carry true
    // (crossing sets it together with r >= threshold); a foreign key in a
    // r >= 3 WB4 payload is a save tamper = the flag reads false.
    logic.stoneSeen = data.stoneSeen === true;
    // CC-WB4 S-2.3: fire the crossing BEFORE the r-qualifying clamp below,
    // while logic.stoneSeen still reads the payload (an r >= threshold
    // payload with the flag ABSENT = a pre-WB4 WB2 save = the crossing
    // legitimately fires here - stoneCrossing() sets the flag, appends the
    // topic once, toasts; the clamp then merely keeps that state).
    stoneCrossing();
    // rQualifies clamp: pre-WB4 saves cannot carry the key, so an
    // r >= threshold payload WITHOUT it must never read "never reached",
    // or every re-restore would re-derive the crossing; the clamp keeps the
    // flag the crossing just set (or true from the payload) - and it is
    // ALWAYS true here, because the crossing above ran for exactly this
    // payload shape. The flag then rides every later capture.
    var rQualifies = ST && ri >= ST.thresholdRepeats;
    if (rQualifies && data.stoneSeen !== true && !logic.stoneSeen) {
      logic.stoneSeen = true;        // unreachable in practice; belt for the law
    }
    rebuildTallyPins();                              // S-3: rebuilt on restore
    rebuildStoneDressing();                          // CC-WB4 S-5: rebuilt on restore
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
