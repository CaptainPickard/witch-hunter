// V-3 removal law one-shot (cc-wb2): 16-ore case + extra 26-ore case.
'use strict';
var H = require('/tmp/wb2_harness.js');
var check = H.check;
H.out.length = 0; H.FAILS.length = 0;
var ORE = 'ironOre', COIN = 'stolenCoin';

// r0 turn-in with EXACTLY n ore carried (fresh module instance each case):
function rawTurnIn(n, startDay) {
  var W = H.reloadModule();
  var t = H.freshGame();
  W.init(t.game);
  t.game.dayNight.day = startDay;
  W.tryOpen();                       // award paper
  t.inv.addItem(ORE, n);
  var oreBefore = t.inv.countOf(ORE);
  var coinsBefore = t.inv.countOf(COIN);
  W.tryOpen();                       // turn-in
  return {
    removed: oreBefore - t.inv.countOf(ORE),
    coinDelta: t.inv.countOf(COIN) - coinsBefore,
    oreAfter: t.inv.countOf(ORE),
    toasts: t.toasts.slice(),
    capture: W.capture()
  };
}

// THE pinned case (S-6.4): 16 at r0 -> removes 16 (not quota), pays 11
var r16 = rawTurnIn(16, 10);
check('V-3 removal EXACTLY 16 at r0 (haul grammar, no quota truncation)', r16.removed === 16,
  'removed=' + r16.removed);
check('V-3 coins +11 (banked, not spent) at 16', r16.coinDelta === 11, 'got ' + r16.coinDelta);
check('V-3 carried ore after = 0', r16.oreAfter === 0, 'got ' + r16.oreAfter);
check('V-3 resolve recorded (resolvedDay === postedDay === 10)',
  r16.capture.resolvedDay === 10 && r16.capture.postedDay === 10 && r16.capture.active === false,
  JSON.stringify(r16.capture));

// extra: 26 at r0 -> removes 26, +21 (never quota-clamped)
var r26 = rawTurnIn(26, 30);
check('V-3 removal EXACTLY 26 at r0 (26-ore haul)', r26.removed === 26, 'removed=' + r26.removed);
check('V-3 coins +21 at 26 carried', r26.coinDelta === 21, 'got ' + r26.coinDelta);

// control: quota-EXACT turn-in removes exactly the quota too (6)
var r6 = rawTurnIn(6, 50);
check('V-3 control 6 at r0: removed 6', r6.removed === 6, 'removed=' + r6.removed);
check('V-3 control 6 at r0: coins +3', r6.coinDelta === 3, 'got ' + r6.coinDelta);

console.log(H.out.join('\n'));
console.log(H.FAILS.length ? '\nV-3 RESULT: ' + H.FAILS.length + ' FAILURES' : '\nV-3 RESULT: ALL ' + H.out.length + ' CHECKS PASS');
process.exit(H.FAILS.length ? 1 : 0);
