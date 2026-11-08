// V-7 probe: capture/restore roundtrip — take + fill + rest on the REAL
// journal.js; capture, restore into a fresh journal; entries survive exactly
// once, no phantom dupes; warEffort capture/restore schema intact.
'use strict';
var H = require('/tmp/qjr3-val-scratch/harness.js');
var pass = 0, fail = 0;
function T(cond, name) { if (cond) { pass++; console.log('  ok  ' + name); } else { fail++; console.log('  FAIL ' + name); } }

global.window = global;
require('/tmp/wh-worldfeat/prototype/js/CONFIG.js');
var J = H.loadJournal();
window.WH_JOURNAL = J;
require('/tmp/wh-worldfeat/prototype/js/wareffort.js');
var WE = window.WH_WarEffort;

// quest available so update() doesn't seed
window.WH_NPC = { questState: function () { return 'available'; } };

J.init({ inventoryUI: { blocked: false, toast: function () {} }, dayNight: { day: 5 } });

var g = H.makeGame(5, 'day', false);
WE.init(g);

// take + fill
T(WE.tryOpen() === true, 'take');
J.update(1);   // unlock edge (quest still available=false → seed) — no: questState 'available' blocks seed. fine.
g.inventory.addItem('ironOre', 6);
T(WE.tryOpen() === true, 'fill');

// rest: real camp.js + real journal
require('/tmp/wh-worldfeat/prototype/js/camp.js');
var Camp = window.WH_CAMP.Camp;
var toasts = [];
var gC = H.makeGame(6, 'dusk', false);
var camp = new Camp({
  scene: new H.THREE.Group(), camera: null, player: gC.player,
  cooking: { kitAcquired: true, onKitButton: function () {}, buffs: { clear: function () {} }, clearMealSlot: function () {}, addStation: function (s) { return s; }, removeStation: function () {}, kitBtn: null },
  dayNight: gC.dayNight, regionManager: function () { return gC.regionManager; },
  toast: function (t) { toasts.push(t); }, applyBuffStats: function () {}, onOpenChange: function () {},
  profile: { has: function () { return false; }, save: function () { return true; }, restore: function () {} }
});
camp.setMenu(camp.worldCamps[0]);
camp.saveAndHeal();

setTimeout(function () {
  // three distinct entries expected
  var ids = J.capture().entries.map(function (e) { return e.id; });
  T(ids.length === 3, '3 entries after take+fill+rest (got ' + ids.length + ': ' + ids.join(',') + ')');
  T(ids.filter(function (i) { return i === 'war-effort-requisition'; }).length === 1, 'requisition once');
  T(ids.filter(function (i) { return i === 'war-effort-first-fill'; }).length === 1, 'firstFill once');
  T(ids.filter(function (i) { return i === 'camp-first-rest'; }).length === 1, 'campRest once');
  // newest-first: campRest, firstFill, requisition
  T(ids[0] === 'camp-first-rest' && ids[1] === 'war-effort-first-fill' && ids[2] === 'war-effort-requisition',
    'newest-first order campRest>firstFill>requisition');

  var block = J.capture();
  T(typeof block.born === 'boolean' && Array.isArray(block.entries) && Object.keys(block).length === 2,
    'capture block = {born, entries} client-only (born=false is correct: no seed path taken)');

  // warEffort payload unchanged shape
  var w = WE.capture();
  T(JSON.stringify(Object.keys(w).slice().sort()) === JSON.stringify(['active', 'postedDay', 'repeatIndex', 'resolvedDay']), 'warEffort capture keys unchanged (4, no journal pollution)');

  // restore into a FRESH journal instance
  delete require.cache[require.resolve('/tmp/wh-worldfeat/prototype/js/journal.js')];
  delete window.WH_JOURNAL;
  var J2 = H.loadJournal();
  J2.init({ inventoryUI: { blocked: false, toast: function () {} }, dayNight: { day: 6 } });
  J2.restore(block);
  var ids2 = J2.capture().entries.map(function (e) { return e.id; });
  T(JSON.stringify(ids2) === JSON.stringify(ids), 'roundtrip: entries survive exactly, order preserved');
  T(ids2.filter(function (i) { return i === 'camp-first-rest'; }).length === 1, 'no phantom dupes after restore');

  // replay the same events into the restored game — dedupe must hold
  var g3 = H.makeGame(7, 'day', false);
  WE2(); function WE2() { }
  // restore warEffort state too (active false after fill)
  WE.restore(w);
  WE.init(g3);
  T(WE.tryOpen() === true, 'post-restore take');
  T(J2.capture().entries.filter(function (e) { return e.id === 'war-effort-requisition'; }).length === 1,
    'repeat take after restore: STILL exactly one requisition (dedupe across save/load)');

  // camp payload schema: sites/respawn keys ride unchanged (rest ran through real camp rest())
  T(gC.dayNight.day === 7, 'camp rest rolled day 6 -> 7 (rest lifecycle ran)');

  // G6 letter: camp profile payload key-shape from the LIVE (touched) camp.js
  // must equal the ZERO-TOUCH HEAD blob's shape on identical fake deps.
  var fs = require('fs');
  var cp = require('child_process');
  var headCamp = cp.execSync('git -C /tmp/wh-worldfeat show HEAD:prototype/js/camp.js', { encoding: 'utf8' });
  fs.writeFileSync('/tmp/qjr3-val-scratch/camp_HEAD_blob.js', headCamp);
  delete require.cache[require.resolve('/tmp/qjr3-val-scratch/camp_HEAD_blob.js')];
  // run the HEAD blob in a sandboxed window so it does not clobber the live WH_CAMP
  var savedCamp = window.WH_CAMP;
  window.WH_CAMP = undefined;
  require('/tmp/qjr3-val-scratch/camp_HEAD_blob.js');
  var CampHead = window.WH_CAMP.Camp;
  window.WH_CAMP = savedCamp;
  function mkBoth(Cl) {
    var gg = H.makeGame(20, 'dusk', false);
    var cc = new Cl({
      scene: new H.THREE.Group(), camera: null, player: gg.player,
      cooking: { kitAcquired: true, onKitButton: function () {}, buffs: { clear: function () {} }, clearMealSlot: function () {}, addStation: function (s) { return s; }, removeStation: function () {}, kitBtn: null },
      dayNight: gg.dayNight, regionManager: function () { return gg.regionManager; },
      toast: function () {}, applyBuffStats: function () {}, onOpenChange: function () {},
      profile: { has: function () { return true; }, save: function (c) { captured = c; return true; }, restore: function () {} }
    });
    var captured = null;
    cc.setMenu(cc.worldCamps[0]);
    cc.save();
    var r = captured && captured.respawn ? Object.keys(captured.respawn).slice().sort().join(',') : 'none';
    return { capturedKeys: captured ? Object.keys(captured).slice().sort().join(',').replace(/site|placeBar|anchorBar|ghost|mesh|group/g, 'OBJ') : 'none', respawnKeys: r };
  }
  var liveShape = mkBoth(Camp);
  var headShape = mkBoth(CampHead);
  T(liveShape.respawnKeys === headShape.respawnKeys && liveShape.respawnKeys !== 'none',
    'camp profile respawn payload keys identical live vs HEAD blob (' + liveShape.respawnKeys + ')');

  console.log('V7-CHECK ' + pass + '/' + (pass + fail));
  process.exit(fail ? 1 : 0);
}, 1500);
