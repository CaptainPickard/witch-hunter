// V-3/V-4 probe: award + fill events through the REAL wareffort.js with a
// stubbed journal recorder. Covers: exact-quota fill, over-band fill (single
// site), satchel-full refusal, below-quota refusal, second-take dedupe.
'use strict';
var H = require('/tmp/qjr3-val-scratch/harness.js');
var pass = 0, fail = 0;
function T(cond, name) { if (cond) { pass++; console.log('  ok  ' + name); } else { fail++; console.log('  FAIL ' + name); } }

// load real CONFIG for topic references
global.window = global;
require('/tmp/wh-worldfeat/prototype/js/CONFIG.js');

var rec = H.makeRecorder();
rec._g = { dayNight: { day: 7 } };   // recorder day source = the game the probes present
global.window.WH_JOURNAL = rec;   // stubbed journal recorder

// load real wareffort
require('/tmp/wh-worldfeat/prototype/js/wareffort.js');
var WE = window.WH_WarEffort;
T(!!WE, 'WH_WarEffort exported');

// fresh game near the board
var g = H.makeGame(7, 'day', false);
g.scene = new H.THREE.Group();
WE.init(g);
T(g._toasts.length === 0, 'no toasts at init');
T(rec.callCount() === 0, 'no journal writes at init');

// helper: count entries by id
function count(id) { return rec.entries.filter(function (e) { return e.id === id; }).length; }
function lastToast() { return g._toasts[g._toasts.length - 1]; }

// === 1. award: idle take fires requisition once, verbatim ===
T(WE.tryOpen() === true, 'take accepted (idle)');
T(count('war-effort-requisition') === 1, 'award appended requisition exactly once');
var e0 = rec.entries[0];
T(e0.title === window.WH_CONFIG.journal.topics.requisition.title, 'award title === CONFIG verbatim');
T(e0.body === window.WH_CONFIG.journal.topics.requisition.body, 'award body === CONFIG verbatim');
T(e0.source === window.WH_CONFIG.journal.topics.requisition.source, 'award source === CONFIG verbatim');
T(e0.day === 7, 'award day = live dayNight.day (7)');
T(rec.lastRaw()[3] === undefined, 'A9 letter: award append day arg positionally UNDEFINED');
T(lastToast() === 'The garrison wants iron for the war. Bring 6 iron ore to this board.', 'offer toast fires');

// === 2. exact-quota fill fires firstFill once ===
g.inventory.addItem('ironOre', 6);
var nBefore = rec.callCount();
T(WE.tryOpen() === true, 'fill accepted (exact quota)');
T(rec.callCount() === nBefore + 1, 'fill: exactly one append call');
T(count('war-effort-first-fill') === 1, 'firstFill appended once');
var e1 = rec.entries[0];
T(e1.id === 'war-effort-first-fill', 'fill entry id firstFill');
T(e1.title === window.WH_CONFIG.journal.topics.firstFill.title, 'fill title === CONFIG verbatim');
T(e1.source === window.WH_CONFIG.journal.topics.firstFill.source, 'fill source === CONFIG verbatim');
T(rec.lastRaw()[3] === undefined, 'A9 letter: fill append day arg positionally UNDEFINED');
T(count('war-effort-requisition') === 1, 'requisition still exactly once after fill');

// === 3. same-day re-take is consumed by spentToday — no journal write ===
var nB = rec.callCount();
var r3 = WE.tryOpen();
T(r3 === true, 'spentToday press consumed');
T(rec.callCount() === nB, 'spentToday: no journal write');
T(count('war-effort-requisition') === 1 && count('war-effort-first-fill') === 1, 'still 1+1 entries');

// === 4. next day: satchel-full refusal — award path must not journal ===
g.dayNight.day = 8;
rec._g.dayNight.day = 8;
// satchel-full: the paper addItem returns 0
var realAdd = g.inventory.addItem;
g.inventory.addItem = function (id, n) { if (id === 'warOrder') return 0; return realAdd(id, n); };
var nC = rec.callCount();
T(WE.tryOpen() === true, 'satchel-full take: press consumed, refusal');
T(lastToast() === 'Your satchel is full.', 'satchel-full toast');
T(rec.callCount() === nC, 'satchel-full: journal NOT written');
g.inventory.addItem = realAdd;   // restore

// === 5. second take dedupes by id (journal idempotence, A10) ===
T(WE.tryOpen() === true, 'second take accepted');
T(rec.callCount() === nC + 1, 'second award: one append call');
T(count('war-effort-requisition') === 1, 'dedupe: requisition still exactly 1');
T(rec.entries.filter(function (e) { return e.id === 'war-effort-requisition'; })[0].day === 7,
  'original requisition entry survives intact (day 7, newest-first unchanged)');

// === 6. below-quota refusal fires nothing ===
g.inventory.addItem('ironOre', 8);   // quota at repeatIndex 1 = 9; have 8 < 9
var nD = rec.callCount();
T(WE.tryOpen() === true, 'below-quota turn-in consumed');
T(lastToast().indexOf('Not enough iron ore') === 0, 'below-quota toast');
T(rec.callCount() === nD, 'below-quota: journal NOT written');
T(count('war-effort-first-fill') === 1, 'firstFill still exactly 1');

// === 7. over-band fill: quota 9, carry 12 → ONE call, one entry ===
g.inventory.addItem('ironOre', 4);   // 12 total, over the 9 quota
var nE = rec.callCount();
T(WE.tryOpen() === true, 'over-band fill accepted');
T(rec.callCount() === nE + 1, 'over-band fill: exactly ONE append call');
T(count('war-effort-first-fill') === 1, 'over-band: firstFill still exactly one entry (no double-write)');
var eF = rec.entries.filter(function (e) { return e.id === 'war-effort-first-fill'; })[0];
T(!!eF && eF.day === 7, 'over-band entry is the ORIGINAL firstFill (id dedupe, not a second row)');

console.log('V3/V4-CHECK ' + pass + '/' + (pass + fail));
process.exit(fail ? 1 : 0);
