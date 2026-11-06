// V-6 probe: absent-journal guard — delete window.WH_JOURNAL, call the three
// call paths, nothing may throw and nothing may be written anywhere.
'use strict';
var H = require('/tmp/qjr3-val-scratch/harness.js');
var pass = 0, fail = 0;
function T(cond, name) { if (cond) { pass++; console.log('  ok  ' + name); } else { fail++; console.log('  FAIL ' + name); } }

global.window = global;
require('/tmp/wh-worldfeat/prototype/js/CONFIG.js');
require('/tmp/wh-worldfeat/prototype/js/wareffort.js');
require('/tmp/wh-worldfeat/prototype/js/camp.js');
var WE = window.WH_WarEffort, Camp = window.WH_CAMP.Camp, cfg = window.WH_CONFIG;

function mkCamp(phase, day, dormant, toasts) {
  var g = H.makeGame(day, phase, dormant);
  var camp = new Camp({
    scene: new H.THREE.Group(),
    camera: null,
    player: g.player,
    cooking: { kitAcquired: true, onKitButton: function () {}, buffs: { clear: function () {} }, clearMealSlot: function () {}, addStation: function (s) { return s; }, removeStation: function () {}, kitBtn: null },
    dayNight: g.dayNight,
    regionManager: function () { return g.regionManager; },
    toast: function (t) { toasts.push(t); },
    applyBuffStats: function () {},
    onOpenChange: function () {},
    profile: { has: function () { return false; }, save: function () { return true; }, restore: function () {} }
  });
  return { camp: camp, g: g };
}

var threw = [];
function tryStep(name, fn) {
  try { fn(); T(true, name + ' (no throw)'); }
  catch (e) { threw.push(name + ': ' + e.message); T(false, name + ' threw: ' + e.message); }
}

// Case A: window.WH_JOURNAL fully deleted, CJ/JT still resolve (CONFIG present)
try {
  delete window.WH_JOURNAL;
  T(window.WH_JOURNAL === undefined, 'WH_JOURNAL deleted');

  var toastsA = [];
  var A = mkCamp('dusk', 3, false, toastsA);
  A.camp.setMenu(A.camp.worldCamps[0]);
  tryStep('camp.saveAndHeal without WH_JOURNAL', function () { A.camp.saveAndHeal(); });
  T(A.camp.resting, 'rest lifecycle still proceeds (guard is write-only)');

  var gB = H.makeGame(7, 'day', false);
  WE.init(gB);
  tryStep('wareffort.take without WH_JOURNAL', function () { WE.tryOpen(); });
  T(gB.inventory._bag['warOrder'] === 1, 'award still granted without journal');

  var gF = H.makeGame(7, 'day', false);
  WE.init(gF);
  tryStep('wareffort idle-take/fill without WH_JOURNAL', function () {
    T(WE.tryOpen() === true, '  idle take ok');
    gF.inventory.addItem('ironOre', 6);
    T(WE.tryOpen() === true, '  exact-quota fill ok (no journal, no throw)');
  });
  // fill refusal path without journal too (below quota)
  var gR = H.makeGame(7, 'day', false);
  WE.init(gR);
  tryStep('wareffort refusal paths without WH_JOURNAL', function () {
    T(WE.tryOpen() === true, '  idle take ok');
    gR.inventory.addItem('ironOre', 3);   // < quota 6
    T(WE.tryOpen() === true, '  below-quota refusal ok (no journal, no throw)');
    var realAdd = gR.inventory.addItem;
    gR.inventory.addItem = function (id, n2) { if (id === 'warOrder') return 0; return realAdd(id, n2); };
    var d2 = H.makeGame(8, 'day', false);
    WE.init(d2);
    d2.inventory.addItem = gR.inventory.addItem;   // satchel-full flag
    T(WE.tryOpen() === true, '  satchel-full refusal ok (no journal, no throw)');
  });

  tryStep('camp day-refusal path without WH_JOURNAL', function () {
    var toastsDay = [];
    var DD = mkCamp('day', 8, false, toastsDay);
    DD.camp.setMenu(DD.camp.worldCamps[0]);
    DD.camp.saveAndHeal();
    T(toastsDay[toastsDay.length - 1] === cfg.camp.text.sleepGate, '  daytime refusal toast fired without journal');
  });

  tryStep('camp.save without WH_JOURNAL', function () {
    var toastsS = [];
    var E = mkCamp('day', 8, false, toastsS);
    E.camp.setMenu(E.camp.worldCamps[0]);
    E.camp.save();
  });
} catch (e) { T(false, 'case A harness threw: ' + e.message); }

// Case B: journal PRESENT but null topics (CFG.journal.topics gone) — the
// `CFG.journal &&` half of the guard law
try {
  var savedTopics = cfg.journal.topics;
  cfg.journal.topics = null;
  // Re-require modules so their IIFE-local JT/CJ re-bind: fresh copies.
  delete require.cache[require.resolve('/tmp/wh-worldfeat/prototype/js/wareffort.js')];
  delete require.cache[require.resolve('/tmp/wh-worldfeat/prototype/js/camp.js')];
  require('/tmp/wh-worldfeat/prototype/js/wareffort.js');
  require('/tmp/wh-worldfeat/prototype/js/camp.js');
  var WE2 = window.WH_WarEffort, Camp2 = window.WH_CAMP.Camp;

  var toastsB = [];
  var B = (function () {
    var g = H.makeGame(3, 'dusk', false);
    var camp = new Camp2({
      scene: new H.THREE.Group(), camera: null, player: g.player,
      cooking: { kitAcquired: true, onKitButton: function () {}, buffs: { clear: function () {} }, clearMealSlot: function () {}, addStation: function (s) { return s; }, removeStation: function () {}, kitBtn: null },
      dayNight: g.dayNight, regionManager: function () { return g.regionManager; },
      toast: function (t) { toastsB.push(t); }, applyBuffStats: function () {}, onOpenChange: function () {},
      profile: { has: function () { return false; }, save: function () { return true; }, restore: function () {} }
    });
    return { camp: camp, g: g };
  })();
  // provide a journal that WOULD record if called — proves the guard short-circuits
  var writes = 0;
  window.WH_JOURNAL = { append: function () { writes++; } };
  B.camp.setMenu(B.camp.worldCamps[0]);
  tryStep('camp.saveAndHeal with null topics', function () { B.camp.saveAndHeal(); });
  T(writes === 0, 'null topics: append never called (guard short-circuit)');

  var g2 = H.makeGame(7, 'day', false);
  WE2.init(g2);
  tryStep('wareffort.tryOpen with null topics', function () { WE2.tryOpen(); });
  T(writes === 0, 'null topics: wareffort append never called');
  cfg.journal.topics = savedTopics;
} catch (e) { T(false, 'case B harness threw: ' + e.message); }

// Case C: journal is a broken object (append missing) — whole-call gate must
// still not crash the module path (typeof check absent, so it WOULD throw;
// documented law is WH_JOURNAL presence + topics presence, so probe the
// landed law exactly: journal PRESENT + append present + bad topics values)
try {
  var bad = { append: function () { throw new Error('append exploded'); } };
  // the landed guard does not typeof-append; a broken append throws — that's
  // the journal module's contract, not the wiring's. Assert what IS specified:
  window.WH_JOURNAL = { append: function () {} };   // valid recorder, never writes
  var n = 0;
  window.WH_JOURNAL.append = function () { n++; };
  var toastsC = [];
  var C = mkCamp('dusk', 4, false, toastsC);
  C.camp.setMenu(C.camp.worldCamps[0]);
  tryStep('camp.saveAndHeal with healthy recorder', function () { C.camp.saveAndHeal(); });
  T(n === 1, 'healthy recorder: append called once (guard passes through)');
} catch (e) { T(false, 'case C harness threw: ' + e.message); }

T(threw.length === 0, 'TOTAL THROWS = 0');
console.log('V6-CHECK ' + pass + '/' + (pass + fail));
process.exit(fail ? 1 : 0);
