// V-8 probe: day/source stamping through the REAL journal (A8/A9).
// Append with undefined day must stamp game.dayNight.day; source must ride A1 strings.
'use strict';
var H = require('/tmp/qjr3-val-scratch/harness.js');
var pass = 0, fail = 0;
function T(cond, name) { if (cond) { pass++; console.log('  ok  ' + name); } else { fail++; console.log('  FAIL ' + name); } }

global.window = global;
require('/tmp/wh-worldfeat/prototype/js/CONFIG.js');

var J = H.loadJournal();
window.WH_JOURNAL = J;
window.WH_NPC = { questState: function () { return 'available'; } };

var cfg = window.WH_CONFIG;
var g = H.makeGame(13, 'day', false);
J.init({ inventoryUI: { blocked: false, toast: function () {} }, dayNight: g.dayNight });
require('/tmp/wh-worldfeat/prototype/js/wareffort.js');
var WE = window.WH_WarEffort;
WE.init(g);

// award at day 13
T(WE.tryOpen() === true, 'take');
var entries = J.capture().entries;
T(entries[0].day === 13, 'award day stamp = live dayNight.day (13)');
T(entries[0].source === cfg.journal.topics.requisition.source, 'award source = A1 string');

// fill at day 14 (advance the clock)
g.dayNight.day = 14;
g.inventory.addItem('ironOre', 6);
T(WE.tryOpen() === true, 'fill');
entries = J.capture().entries;
T(entries[0].day === 14, 'fill day stamp = LIVE day at event time (14)');
T(entries[0].source === cfg.journal.topics.firstFill.source, 'fill source = A1 string');

// rest at day 15 through the REAL camp module
require('/tmp/wh-worldfeat/prototype/js/camp.js');
var Camp = window.WH_CAMP.Camp;
var toasts = [];
var camp = new Camp({
  scene: new H.THREE.Group(), camera: null, player: g.player,
  cooking: { kitAcquired: true, onKitButton: function () {}, buffs: { clear: function () {} }, clearMealSlot: function () {}, addStation: function (s) { return s; }, removeStation: function () {}, kitBtn: null },
  dayNight: g.dayNight,   // real shared clock: set to day 15 dusk for the gate
  regionManager: function () { return { logic: { activeId: 'hold_outskirts', clampPlayer: function () {} } }; },
  toast: function (t) { toasts.push(t); }, applyBuffStats: function () {}, onOpenChange: function () {},
  profile: { has: function () { return false; }, save: function () { return true; }, restore: function () {} }
});
g.dayNight.day = 15;
g.dayNight.phase = 'dusk';
camp.setMenu(camp.worldCamps[0]);
camp.saveAndHeal();

setTimeout(function () {
  entries = J.capture().entries;
  var rest = entries.filter(function (e) { return e.id === 'camp-first-rest'; })[0];
  T(!!rest, 'camp-first-rest entry exists after real rest');
  if (rest) {
    T(rest.source === cfg.journal.topics.campRest.source, 'rest source = A1 string ("Camp folk")');
    T(rest.day === 15, 'rest day stamp = live day at event time (15, before nextDawn rolls)');
  }
  T(entries.filter(function (e) { return e.id === 'war-effort-requisition'; })[0].title === cfg.journal.topics.requisition.title,
    'titles always CONFIG verbatim');
  console.log('V8-CHECK ' + pass + '/' + (pass + fail));
  process.exit(fail ? 1 : 0);
}, 1500);
