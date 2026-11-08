// V-2 payout-table one-shot v2 (cc-wb2 valspec): rows a..m EXACT through the
// module public surface. Node only. Toast rows bound per spec S-2:
// overDoneText when x>=1, landed doneText when x==0.
'use strict';
var H = require('/tmp/wb2_harness.js');
var check = H.check;
H.out.length = 0; H.FAILS.length = 0;

var ORE = 'ironOre', COIN = 'stolenCoin', PAPER = 'warOrder';
var DONE_TEXT = 'Requisition filled. The quartermaster marks the board.';
var OVER_TEXT = 'Requisition filled. The quartermaster pays a bonus for the extra iron.';

// ONE turn-in at pinned state (r = repeatIndex at turn-in, ore = carried):
// grows the board across consecutive-day resolutions, each hauling exactly
// that day's quota, then awards and turns in with EXACTLY `ore` carried.
function rowTurnIn(r, ore, baseDay) {
  var W = H.reloadModule();
  var t = H.freshGame();
  var g = t.game;
  W.init(g);
  var d = baseDay;
  g.dayNight.day = d;
  for (var i = 0; i < r; i++) {
    W.tryOpen();                                   // award paper (quotaQ(i))
    var q = [6, 9, 14, 18, 18, 18, 18, 18][Math.min(i, 7)];
    t.inv.addItem(ORE, q);
    W.tryOpen();                                   // resolve -> repeatIndex=i+1
    t.inv.removeItem(ORE, q);
    d++;
    g.dayNight.day = d;
  }
  var coinsBefore = t.inv.countOf(COIN);
  var coinsBeforeAbs = t.inv.countOf(COIN);
  W.interactPrompt();                              // idle prompt
  W.tryOpen();                                     // award paper
  t.inv.addItem(ORE, ore);
  var promptActive = W.interactPrompt();           // active prompt w/ quota
  W.tryOpen();                                     // THE turn-in under test
  return {
    coinDelta: t.inv.countOf(COIN) - coinsBeforeAbs,
    oreAfter: t.inv.countOf(ORE),
    lastToast: t.toasts[t.toasts.length - 1],
    toasts: t.toasts.slice(),
    promptActive: promptActive,
    capture: W.capture(),
    paperCount: t.inv.countOf(PAPER)
  };
}

// rows a..m pinned EXACT (spec table): [label, r, ore, expectedCoins, xBand]
// xBand: 'x0' (exact quota turn-in -> landed doneText) / 'over' (x>=1 -> overDoneText)
var ROWS = [
  ['row a (ore 6,  r0)  x=0 -> 3', 0, 6, 3, 'x0'],
  ['row c (ore 7,  r0)  x=1 -> 4', 0, 7, 4, 'over'],
  ['row d (ore 8,  r0)  x=2 -> 4', 0, 8, 4, 'over'],
  ['row e (ore 10, r0)  x=4 -> 6', 0, 10, 6, 'over'],
  ['row f (ore 16, r0)  x=10 -> 11', 0, 16, 11, 'over'],
  ['row g (ore 17, r0)  x=11 -> 12', 0, 17, 12, 'over'],
  ['row h (ore 26, r0)  x=20 -> 21', 0, 26, 21, 'over'],
  ['row i (ore 9,  r1)  x=0 -> 5', 1, 9, 5, 'x0'],
  ['row j (ore 10, r1)  x=1 -> 6', 1, 10, 6, 'over'],
  ['row k (ore 14, r2)  x=0 -> 9', 2, 14, 9, 'x0'],
  ['row l (ore 18, r3)  x=0 -> 13', 3, 18, 13, 'x0'],
  ['row m (ore 18, r4)  x=0 -> 14', 4, 18, 14, 'x0']
];
ROWS.forEach(function (row) {
  var res = rowTurnIn(row[1], row[2], 10);
  check('V-2f ' + row[0] + ' coin delta EXACT', res.coinDelta === row[3],
    'expected ' + row[3] + ' got ' + res.coinDelta);
  check('V-2f ' + row[0] + ' ore hauled to 0', res.oreAfter === 0,
    'got ' + res.oreAfter);
  check('V-2f ' + row[0] + ' toast text exact (' + row[4] + ')',
    res.lastToast === (row[4] === 'over' ? OVER_TEXT : DONE_TEXT),
    'got ' + JSON.stringify(res.lastToast));
});

// row b (WB1 regression bind): below quota -> NOTHING removed, no pay, and
// the landed WB1 insufficient toast shape; board stays ACTIVE (not spent).
(function () {
  var W = H.reloadModule();
  var t = H.freshGame();
  W.init(t.game);
  t.game.dayNight.day = 10;
  W.tryOpen(); t.inv.addItem(ORE, 5);
  var coinsBefore = t.inv.countOf(COIN), oreBefore = t.inv.countOf(ORE);
  var promptActive = W.interactPrompt();
  var capBefore = W.capture();
  W.tryOpen();
  check('V-2f row b insufficient: coin delta 0', t.inv.countOf(COIN) - coinsBefore === 0,
    'got ' + (t.inv.countOf(COIN) - coinsBefore));
  check('V-2f row b insufficient: ore NOT removed', t.inv.countOf(ORE) === oreBefore,
    'got ' + t.inv.countOf(ORE));
  check('V-2f row b insufficient toast WB1 grammar (5/6)',
    t.toasts.some(function (x) { return /\(5\/6\)/.test(x); }), JSON.stringify(t.toasts));
  check('V-2f row b board stays ACTIVE (no spent-day leak to a rejection)',
    W.capture().active === true && W.capture().resolvedDay === null,
    JSON.stringify(W.capture()));
  // complete on the SAME day still works (WB1 semantics: rejection never burns the day)
  t.inv.addItem(ORE, 1);
  W.tryOpen();
  check('V-2f row b completes after rejection same-day: +3 coins (WB1 economics)',
    t.inv.countOf(COIN) - coinsBefore === 3, 'got ' + (t.inv.countOf(COIN) - coinsBefore));
  check('V-2f row b resolves to spent', /spent until dawn/.test(W.interactPrompt()),
    W.interactPrompt());
})();

// V-2g: landed doneText verbatim on EXACT-quota turn-in (x == 0), already
// covered by rows a/i/k/l/m; here byte-check BOTH CONFIG strings against
// the module's runtime choices:
(function () {
  var CFG = H.CFG;
  check('V-2g CONFIG doneText verbatim',
    CFG.warEffort.requisition.doneText === DONE_TEXT,
    JSON.stringify(CFG.warEffort.requisition.doneText));
  check('V-2g CONFIG ladder.overDoneText verbatim',
    CFG.warEffort.ladder.overDoneText === OVER_TEXT,
    JSON.stringify(CFG.warEffort.ladder.overDoneText));
})();

console.log(H.out.join('\n'));
var fails = H.FAILS;
console.log(fails.length ? '\nV-2 RESULT: ' + fails.length + ' FAILURES' : '\nV-2 RESULT: ALL ' + H.out.length + ' CHECKS PASS');
process.exit(fails.length ? 1 : 0);
