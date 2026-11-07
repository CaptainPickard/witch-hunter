// CC-WB3 A2 flow one-shot: idle award + exact-quota turn-in. Pattern:
// scratch/cc-wb2/wb2_harness.js via ./wb3_harness.js.
'use strict';
var H = require('/tmp/wh-worldfeat/scratch/cc-wb3/wb3_harness.js');
var check = H.check;
var W = H.reloadModule();

// ---- A2/1 idle press: +1 strataOrder, active, postedDay, offer toast, journal ----
var t = H.freshGame({ day: 5 });
W.init(t.game);
t.inv.addItem('rot-silk', 4);
t.inv.addItem('rot-gland', 2);
var okPress = W.tryOpen();
check('A2.1 press consumed (true) at the board', okPress === true, String(okPress));
check('A2.1 idling press adds EXACTLY 1 strataOrder', t.inv.countOf('strataOrder') === 1,
  'strataOrder=' + t.inv.countOf('strataOrder'));
check('A2.1 mats untouched on award (silk 4 / gland 2)',
  t.inv.countOf('rot-silk') === 4 && t.inv.countOf('rot-gland') === 2,
  'silk=' + t.inv.countOf('rot-silk') + ' gland=' + t.inv.countOf('rot-gland'));
var caps = W.capture();
check('A2.1 active true after award', caps.active === true, JSON.stringify(caps));
check('A2.1 postedDay === day (5)', caps.postedDay === 5, JSON.stringify(caps));
check('A2.1 offerText toast fired',
  t.toasts.indexOf(H.CFG.strataEffort.offerText) >= 0, JSON.stringify(t.toasts));
check('A2.1 journal append on award (strata topic id)',
  t.appends.length === 1 && t.appends[0].id === 'strata-requisition', JSON.stringify(t.appends));

// ---- A2/2 active press with 9 silk + 2 gland: removes EXACTLY 4/2, pays 5 ----
t.inv.addItem('rot-silk', 5);           // surplus top-up (total 9 silk)
var okFill = W.tryOpen();
check('A2.2 fill press consumed (true)', okFill === true, String(okFill));
check('A2.2 removes EXACTLY 4 rot-silk (surplus 5 untouched)', t.inv.countOf('rot-silk') === 5,
  'silk after=' + t.inv.countOf('rot-silk'));
check('A2.2 removes EXACTLY 2 rot-gland', t.inv.countOf('rot-gland') === 0,
  'gland after=' + t.inv.countOf('rot-gland'));
check('A2.2 adds EXACTLY 5 stolenCoin', t.inv.countOf('stolenCoin') === 5,
  'coins=' + t.inv.countOf('stolenCoin'));
check('A2.2 paper persists (WB1 law: the turn-in consumes nothing of the paper)',
  t.inv.countOf('strataOrder') === 1,
  'strataOrder=' + t.inv.countOf('strataOrder'));
caps = W.capture();
check('A2.2 resolvedDay === postedDay (5)', caps.resolvedDay === caps.postedDay && caps.resolvedDay === 5,
  JSON.stringify(caps));
check('A2.2 active false, repeatIndex-free payload',
  caps.active === false && Object.keys(caps).length === 3,
  'keys=' + JSON.stringify(Object.keys(caps)));
check('A2.2 papers hidden after resolve', (function () {
  var board = t.scene.children[0];
  var hidden = 0;
  for (var i = 0; i < board.children.length; i++) {
    var c = board.children[i];
    if (c && c.name && c.name.indexOf('cc-wb3-sheet-') >= 0 && c.visible === false) hidden++;
  }
  return hidden === 2;   // both parchment sheets
})(), 'sheets=' + JSON.stringify(t.scene.children[0].children.map(function (c) { return { n: c.name, v: c.visible }; })));
check('A2.2 doneText toast fired',
  t.toasts.indexOf(H.CFG.strataEffort.doneText) >= 0, JSON.stringify(t.toasts));
check('A2.2 journal fill append (2 total, both strata topic)',
  t.appends.length === 2 && t.appends[1].id === 'strata-requisition', JSON.stringify(t.appends));
check('A2.2 deed strataFill fired once', t.deeds.length === 1 && t.deeds[0].id === 'strataFill',
  JSON.stringify(t.deeds));

// ---- A2/3 capture key-set EXACTLY {active, postedDay, resolvedDay} ----
check('A2.3 capture key-set exact 3 keys',
  JSON.stringify(Object.keys(caps).sort()) === JSON.stringify(['active', 'postedDay', 'resolvedDay']),
  JSON.stringify(Object.keys(caps)));

// ---- fresh board: award does NOT grant coins early ----
var W2 = H.reloadModule();
var t2 = H.freshGame({ day: 7 });
W2.init(t2.game);
W2.tryOpen();
check('A2.4 award alone grants no coins',
  t2.inv.countOf('stolenCoin') === 0, 'coins=' + t2.inv.countOf('stolenCoin'));

H.out.forEach(function (l) { console.log(l); });
console.log('A2 ' + (H.FAILS.length ? 'FAIL(' + H.FAILS.length + ')' : 'PASS') + ' checks=' + H.out.length);
process.exit(H.FAILS.length ? 1 : 0);
