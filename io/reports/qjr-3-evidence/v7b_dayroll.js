// V-7b probe (G7 second half): day-roll re-award through the REAL journal —
// new-day re-award + re-fill must NOT mint dupes (A10 across days).
'use strict';
var H = require('/tmp/qjr3-val-scratch/harness.js');
var pass = 0, fail = 0;
function T(cond, name) { if (cond) { pass++; console.log('  ok  ' + name); } else { fail++; console.log('  FAIL ' + name); } }

global.window = global;
require('/tmp/wh-worldfeat/prototype/js/CONFIG.js');
var J = H.loadJournal();
window.WH_JOURNAL = J;
window.WH_NPC = { questState: function () { return 'available'; } };
require('/tmp/wh-worldfeat/prototype/js/wareffort.js');
var WE = window.WH_WarEffort;
var cfg = window.WH_CONFIG;

var g = H.makeGame(12, 'day', false);
J.init({ inventoryUI: { blocked: false, toast: function () {} }, dayNight: g.dayNight });
WE.init(g);

// day 12: award + fill
T(WE.tryOpen() === true, 'd12 take');
g.inventory.addItem('ironOre', 6);
T(WE.tryOpen() === true, 'd12 fill');
var n1 = J.capture().entries.length;
T(n1 === 2, '2 entries after d12 take+fill (got ' + n1 + ')');

// day roll to 13: nextDawn advances day, board re-arms (resolvedDay 12 < 13)
g.dayNight.day = 13;
T(J.capture().entries.filter(function (e) { return e.id === 'war-effort-requisition'; }).length === 1,
  'pre-roll: requisition exactly once');

// re-award on day 13 — must NOT mint a dupe row. Journal law (A10): dedupe is
// by id and the ORIGINAL entry survives (append returns on collision — journal.js
// L84-89), so the day-13 attempt is a silent no-write. Assert exactly that.
T(WE.tryOpen() === true, 'd13 re-take accepted');
var ids = J.capture().entries.map(function (e) { return e.id; });
T(ids.filter(function (i) { return i === 'war-effort-requisition'; }).length === 1,
  'd13 re-award: requisition STILL exactly once (no dupe after day roll)');
var reqEntry = J.capture().entries.filter(function (e) { return e.id === 'war-effort-requisition'; })[0];
T(reqEntry.day === 12,
  'original requisition row survives untouched (day stays 12 — journal keep-first dedupe law)');
T(ids.filter(function (i) { return i === 'war-effort-first-fill'; }).length === 1,
  'firstFill untouched');

// re-fill on day 13 (quota 9 at repeatIndex 1)
g.inventory.addItem('ironOre', 10);
T(WE.tryOpen() === true, 'd13 re-fill accepted');
ids = J.capture().entries.map(function (e) { return e.id; });
T(ids.filter(function (i) { return i === 'war-effort-first-fill'; }).length === 1,
  'd13 re-fill: firstFill STILL exactly once (no dupe after day roll)');
T(J.capture().entries.length === 2, 'total entries still 2 after the day rolled and both events replayed');

console.log('V7b-CHECK ' + pass + '/' + (pass + fail));
process.exit(fail ? 1 : 0);
