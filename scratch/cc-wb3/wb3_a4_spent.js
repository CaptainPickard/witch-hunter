// CC-WB3 A4 spent-day one-shot: after a fill the same-day press is consumed
// with ZERO changes; fake day+1 re-arms the award path; and again.
'use strict';
var H = require('/tmp/wh-worldfeat/scratch/cc-wb3/wb3_harness.js');
var check = H.check;
var W = H.reloadModule();

var t = H.freshGame({ day: 10 });
W.init(t.game);

// drive to a resolved fill on day 10
W.tryOpen();                                          // award (paper 1)
t.inv.addItem('rot-silk', 4);
t.inv.addItem('rot-gland', 2);
W.tryOpen();                                          // fill
var caps = W.capture();
check('A4.1 resolved on day 10 (resolvedDay === postedDay === 10, active false)',
  caps.postedDay === 10 && caps.resolvedDay === 10 && caps.active === false, JSON.stringify(caps));

// ---- same-day press consumed, ZERO changes ----
var silk = t.inv.countOf('rot-silk'), gland = t.inv.countOf('rot-gland');
var paper = t.inv.countOf('strataOrder'), coins = t.inv.countOf('stolenCoin');
var toastsN = t.toasts.length, appendsN = t.appends.length, deedsN = t.deeds.length;
var ok = W.tryOpen();
check('A4.2 spent press CONSUMED (returns true, no cascade)', ok === true, String(ok));
check('A4.3 zero inventory changes',
  t.inv.countOf('rot-silk') === silk && t.inv.countOf('rot-gland') === gland &&
  t.inv.countOf('strataOrder') === paper && t.inv.countOf('stolenCoin') === coins,
  'silk=' + t.inv.countOf('rot-silk') + ' gland=' + t.inv.countOf('rot-gland') +
  ' paper=' + t.inv.countOf('strataOrder') + ' coins=' + t.inv.countOf('stolenCoin'));
caps = W.capture();
check('A4.4 zero state changes', caps.active === false && caps.resolvedDay === 10 && caps.postedDay === 10,
  JSON.stringify(caps));
check('A4.5 spent prompt', W.interactPrompt() === 'The board is spent until dawn.',
  JSON.stringify(W.interactPrompt()));
check('A4.6 no new journal/deed churn on the spent press',
  t.appends.length === appendsN && t.deeds.length === deedsN,
  'appends=' + t.appends.length + ' deeds=' + t.deeds.length);

// ---- fake day+1: re-arms the AWARD path ----
t.game.dayNight.day = 11;
var promptAfterRoll = W.interactPrompt();             // interaction-time rollNewDay
W.tryOpen();
caps = W.capture();
check('A4.7 day+1 re-arms: active true, postedDay = NEW day (11)',
  caps.active === true && caps.postedDay === 11 && caps.resolvedDay === null, JSON.stringify(caps));
check('A4.8 prompt after re-arm is the idle award prompt',
  promptAfterRoll === 'E - Strata Board (Take a requisition)', JSON.stringify(promptAfterRoll));
check('A4.9 award path fired again (+1 paper on top of the kept one, old coins stay)',
  t.inv.countOf('strataOrder') === 2 && t.inv.countOf('stolenCoin') === coins,
  'paper=' + t.inv.countOf('strataOrder') + ' coins=' + t.inv.countOf('stolenCoin'));

// fill again on the new day, then day+1 once more -> re-arms again
t.inv.addItem('rot-silk', 4);
t.inv.addItem('rot-gland', 2);
W.tryOpen();                                          // fill day 11
caps = W.capture();
check('A4.10 refilled on day 11', caps.resolvedDay === 11 && caps.active === false, JSON.stringify(caps));
t.game.dayNight.day = 12;
W.tryOpen();
caps = W.capture();
check('A4.11 second re-arm after fill (active, postedDay 12)',
  caps.active === true && caps.postedDay === 12, JSON.stringify(caps));

H.out.forEach(function (l) { console.log(l); });
console.log('A4 ' + (H.FAILS.length ? 'FAIL(' + H.FAILS.length + ')' : 'PASS') + ' checks=' + H.out.length);
process.exit(H.FAILS.length ? 1 : 0);
