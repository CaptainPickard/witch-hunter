// CC-WB3 A3 shortfall one-shot: 2 silk + 2 gland press removes NOTHING,
// grants NOTHING, state unchanged; toast carries the HAVE counts.
'use strict';
var H = require('/tmp/wh-worldfeat/scratch/cc-wb3/wb3_harness.js');
var check = H.check;
var W = H.reloadModule();

var t = H.freshGame({ day: 3 });
t.scene.children.pop();   // drop the board body; keep the scene container harmless
W.init(t.game);

// idle award first (this press DOES move state: +1 paper)
W.tryOpen();
var paperAfterAward = t.inv.countOf('strataOrder');
var capsAfterAward = W.capture();
check('A3.1 setup: award succeeded (paper 1, active)',
  paperAfterAward === 1 && capsAfterAward.active === true, JSON.stringify(capsAfterAward));

// shortfall load: 2 silk (quota 4) + 2 gland (quota 2)
t.inv.addItem('rot-silk', 2);
t.inv.addItem('rot-gland', 2);
var sacks = t.inv.countOf('rot-silk'), glands = t.inv.countOf('rot-gland');
var papers = t.inv.countOf('strataOrder');

var ok = W.tryOpen();
check('A3.2 shortfall press consumed (true)', ok === true, String(ok));
check('A3.3 NOTHING removed (silk 2 / gland 2 stay)',
  t.inv.countOf('rot-silk') === sacks && t.inv.countOf('rot-gland') === glands,
  'silk=' + t.inv.countOf('rot-silk') + ' gland=' + t.inv.countOf('rot-gland'));
check('A3.4 NOTHING granted (paper +0, coins 0)',
  t.inv.countOf('strataOrder') === papers && t.inv.countOf('stolenCoin') === 0,
  'paper=' + t.inv.countOf('strataOrder') + ' coins=' + t.inv.countOf('stolenCoin'));
var caps = W.capture();
check('A3.5 state unchanged (active still true, no resolvedDay)',
  caps.active === true && caps.resolvedDay === null && caps.postedDay === capsAfterAward.postedDay,
  JSON.stringify(caps));
check('A3.6 toast is the exact shortfall string with HAVE counts',
  t.toasts[t.toasts.length - 1] === 'Not enough rot-silk/rot-gland for the strata order. (2/2)',
  JSON.stringify(t.toasts));

// have-count interpolation: 3/2 variant
var W2 = H.reloadModule();
var t2 = H.freshGame({ day: 4 });
W2.init(t2.game);
W2.tryOpen();
t2.inv.addItem('rot-silk', 3);
t2.inv.addItem('rot-gland', 2);
W2.tryOpen();
check('A3.7 toast interpolates this press (3/2)',
  t2.toasts[t2.toasts.length - 1] === 'Not enough rot-silk/rot-gland for the strata order. (3/2)',
  JSON.stringify(t2.toasts));

H.out.forEach(function (l) { console.log(l); });
console.log('A3 ' + (H.FAILS.length ? 'FAIL(' + H.FAILS.length + ')' : 'PASS') + ' checks=' + H.out.length);
process.exit(H.FAILS.length ? 1 : 0);
