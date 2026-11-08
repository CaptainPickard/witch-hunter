// V-5 probe: camp saveAndHeal dusk gate through the REAL camp.js.
// Covers: refused daytime rest captures nothing; dusk rest captures once;
// plain save() fires nothing; load fires nothing.
'use strict';
var H = require('/tmp/qjr3-val-scratch/harness.js');
var pass = 0, fail = 0;
function T(cond, name) { if (cond) { pass++; console.log('  ok  ' + name); } else { fail++; console.log('  FAIL ' + name); } }

global.window = global;
require('/tmp/wh-worldfeat/prototype/js/CONFIG.js');

var rec = H.makeRecorder();
rec._g = { dayNight: { day: 9 } };   // recorder day source
global.window.WH_JOURNAL = rec;

// load real camp.js
require('/tmp/wh-worldfeat/prototype/js/camp.js');
var Camp = window.WH_CAMP.Camp;
T(!!Camp, 'WH_CAMP.Camp exported');

var cfg = window.WH_CONFIG;

function mkCamp(phase, day, dormant, toasts) {
  rec._g.dayNight.day = day;   // keep the recorder clock in sync with the probe's game
  var g = H.makeGame(day, phase, dormant);
  g.scene = new H.THREE.Group();
  var camp = new Camp({
    scene: g.scene,
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
  camp.player = g.player;
  return { camp: camp, g: g };
}

function count(id) { return rec.entries.filter(function (e) { return e.id === id; }).length; }
var worldCamp = cfg.camp.worldCamps[0];

// === 1. daytime refused rest captures nothing ===
rec.reset();
var toasts1 = [];
var A = mkCamp('day', 9, false, toasts1);
A.camp.setMenu(A.camp.worldCamps[0]);
T(A.camp.menuCamp === A.camp.worldCamps[0], 'menu open on world camp (day)');
var n0 = rec.appendCount();
A.camp.saveAndHeal();
T(toasts1[toasts1.length - 1] === cfg.camp.text.sleepGate, 'daytime refusal toast = sleepGate');
T(rec.appendCount() === n0, 'DAYTIME REFUSED REST: journal NOT written');
T(count('camp-first-rest') === 0, 'no camp-first-rest entry after daytime refusal');
T(!A.camp.resting, 'not resting (gate returned early)');

// === 2. dusk rest captures ONCE, verbatim ===
rec.reset();
var toasts2 = [];
var B = mkCamp('dusk', 9, false, toasts2);
B.camp.setMenu(B.camp.worldCamps[0]);
var n1 = rec.appendCount();
B.camp.saveAndHeal();
T(rec.appendCount() === n1 + 1, 'dusk rest appended exactly once');
T(count('camp-first-rest') === 1, 'camp-first-rest entry present');
var e = rec.entries[0];
T(e.id === 'camp-first-rest', 'entry id camp-first-rest');
T(e.title === cfg.journal.topics.campRest.title, 'title === CONFIG verbatim');
T(e.body === cfg.journal.topics.campRest.body, 'body === CONFIG verbatim');
T(e.source === cfg.journal.topics.campRest.source, 'source === CONFIG verbatim ("Camp folk")');
T(e.day === 9, 'day = live dayNight.day (9)');
T(rec.lastRaw()[3] === undefined, 'A9 letter: campRest append day arg positionally UNDEFINED');
T(B.camp.resting, 'rest lifecycle started (fade in flight)');
// fade timers: 0.6s each; wait them out and re-check no second write
setTimeout(function () {
  T(count('camp-first-rest') === 1, 'no second write after rest completes');
  T(!B.camp.resting, 'resting cleared after wake');
  T(toasts2.some(function (t) { return t.indexOf('You wake at dawn') === 0; }), 'rested toast fired');

  // === 3. night rest also passes the gate (second camp, dedupe check via recorder) ===
  rec.reset();
  var toasts3 = [];
  var C = mkCamp('night', 10, false, toasts3);
  C.camp.setMenu(C.camp.worldCamps[0]);
  C.camp.saveAndHeal();
  T(count('camp-first-rest') === 1, 'night rest appends too (dedupe collapses the second id)');

  // === 4. plain save() fires NOTHING (at dusk, per valspec letter) ===
  rec.reset();
  rec._g.dayNight.day = 11;
  var toasts4 = [];
  var D = mkCamp('dusk', 11, false, toasts4);
  D.camp.setMenu(D.camp.worldCamps[0]);
  D.camp.save();
  T(rec.callCount() === 0, 'plain save(): journal NOT written');
  T(count('camp-first-rest') === 0, 'no camp-first-rest from save()');
  T(toasts4[toasts4.length - 1] !== undefined && toasts4[toasts4.length - 1].indexOf('Respawn point set') >= 0,
    'save toast fired (CONFIG saved + respawn-set combo)');

  // === 5. load fires NOTHING ===
  rec.reset();
  rec._g.dayNight.day = 12;
  var toasts5 = [];
  var E = mkCamp('day', 12, false, toasts5);
  E.hasSave = function () { return true; };   // force the load row path
  E.camp.setMenu(E.camp.worldCamps[0]);
  E.camp.load();
  T(rec.appendCount() === 0, 'load(): journal NOT written');
  T(count('camp-first-rest') === 0, 'no camp-first-rest from load()');

  console.log('V5-CHECK ' + pass + '/' + (pass + fail));
  process.exit(fail ? 1 : 0);
}, 1500);
