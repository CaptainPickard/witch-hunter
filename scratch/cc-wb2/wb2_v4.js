// V-4 ladder repeat one-shot (cc-wb2): quota sequence 6/9/14/18/18, prompt
// shape, repeatIndex law across the new-day reset, row m peg check.
'use strict';
var H = require('/tmp/wb2_harness.js');
var check = H.check;
H.out.length = 0; H.FAILS.length = 0;
var ORE = 'ironOre', COIN = 'stolenCoin';

// Grow the board to repeatIndex r across consecutive days, each resolution
// carrying EXACTLY that day's quota (quota grows per the ladder). After the
// chain, the board is IDLE on day baseDay + r; then award the next paper and
// return the ACTIVE prompt (shows the r-quota) + capture + turn-in facts.
function reachRepeat(r, baseDay) {
  var W = H.reloadModule();
  var t = H.freshGame();
  var g = t.game;
  W.init(g);
  var d = baseDay;
  g.dayNight.day = d;
  var quotas = [];
  for (var i = 0; i < r; i++) {
    W.tryOpen();                                   // award (quotaQ(i) contract)
    var q = [6, 9, 14, 18, 18, 18, 18, 18][Math.min(i, 7)];
    quotas.push(W.interactPrompt());
    t.inv.addItem(ORE, q);
    W.tryOpen();                                   // resolve -> repeatIndex i+1
    t.inv.removeItem(ORE, q);
    d++;
    g.dayNight.day = d;                            // new day re-arms the board
  }
  return { W: W, t: t, quotas: quotas, finalDay: d, coinsBeforeProbe: t.inv.countOf(COIN) };
}

// V-4h: quota sequence via prompt + accept-threshold probes
var want = [6, 9, 14, 18, 18];
for (var r = 0; r < want.length; r++) {
  var env = reachRepeat(r, 100);
  var W = env.W, t = env.t;
  // board idle at day 100+r; award the paper:
  W.tryOpen();
  var prompt0 = W.interactPrompt();                // shows (n/quota)
  var q = want[r];
  var mZero = /\(0\/(\d+) iron ore\)/.exec(prompt0);
  var shown = mZero ? parseInt(mZero[1], 10) : -1;
  check('V-4h prompt quota at r' + r + ' === ' + q, shown === q,
    'prompt=' + JSON.stringify(prompt0) + ' shown=' + shown);
  // accept-threshold exactness: q-1 insufficient, q accepted
  t.inv.addItem(ORE, q - 1);
  W.tryOpen();
  var lastToast = t.toasts[t.toasts.length - 1] || '';
  var qm1ok = new RegExp('\\(' + (q - 1) + '\\/' + q + '\\)').test(lastToast) &&
    t.inv.countOf(ORE) === q - 1 && t.inv.countOf(COIN) === env.coinsBeforeProbe;
  check('V-4h r' + r + ' turn-in at q-1=' + (q - 1) + ' rejected (insufficient toast, no removal)',
    qm1ok,
    'lastToast=' + JSON.stringify(lastToast) + ' ore=' + t.inv.countOf(ORE) + ' coins=' + t.inv.countOf(COIN));
  t.inv.addItem(ORE, 1);                            // now exactly q
  W.tryOpen();
  check('V-4h r' + r + ' turn-in at exactly q=' + q + ' accepted', W.capture().active === false,
    'capture=' + JSON.stringify(W.capture()));
}

// V-4i prompt template byte-kept (landed WB1 shape, ladder number only)
(function () {
  var env = reachRepeat(1, 200);                    // r1 board idle @ day 201
  var W = env.W, t = env.t;
  W.tryOpen();
  var p = W.interactPrompt();
  check('V-4i prompt template exactly landed shape (r1, quota 9)',
    p === 'E - War Board (0/9 iron ore)', JSON.stringify(p));
  t.inv.addItem(ORE, 3);
  p = W.interactPrompt();
  check('V-4i prompt count slot updates', p === 'E - War Board (3/9 iron ore)', JSON.stringify(p));
  // idle prompt shape (WB1 verbatim)
  var env2 = reachRepeat(0, 300);
  W = env2.W; t = env2.t;
  check('V-4i idle prompt WB1 verbatim', W.interactPrompt() === 'E - War Board (Take a requisition)',
    JSON.stringify(W.interactPrompt()));
})();

// V-4j: repeatIndex survives the new-day reset; increments at resolve only
(function () {
  var W = H.reloadModule();
  var t = H.freshGame();
  var g = t.game;
  W.init(g);
  g.dayNight.day = 400;
  check('V-4j r starts 0', W.capture().repeatIndex === 0, JSON.stringify(W.capture()));
  W.tryOpen(); t.inv.addItem(ORE, 6); W.tryOpen();  // resolve #1
  check('V-4j after resolve #1 repeatIndex === 1', W.capture().repeatIndex === 1,
    JSON.stringify(W.capture()));
  // NO day change: award again on the SAME day must be blocked (spent)
  var spent = /spent until dawn/.test(W.interactPrompt());
  check('V-4j same-day spent law intact', spent, JSON.stringify(W.interactPrompt()));
  // new day: reset path must NOT touch repeatIndex
  g.dayNight.day = 401;
  var pIdle = W.interactPrompt();                   // fires rollNewDay
  check('V-4j prompt re-armed after rollover', /Take a requisition/.test(pIdle), JSON.stringify(pIdle));
  check('V-4j repeatIndex STILL 1 after new-day reset', W.capture().repeatIndex === 1,
    JSON.stringify(W.capture()));
  // resolve #2 on day 401
  W.tryOpen(); t.inv.addItem(ORE, 9); W.tryOpen();
  check('V-4j after resolve #2 repeatIndex === 2', W.capture().repeatIndex === 2,
    JSON.stringify(W.capture()));
  // and the NEXT day's award STILL shows the r2 quota (not 3)
  g.dayNight.day = 402;
  W.interactPrompt();
  W.tryOpen();
  var p3 = W.interactPrompt();
  check('V-4j award after 2 resolves shows quota 14 (r2 not r3)', /\(0\/14 iron ore\)/.test(p3),
    JSON.stringify(p3));
})();

// V-4k row m peg: at r4, ore 18 (x === 0): +14 coins pinned
(function () {
  var W = H.reloadModule();
  var t = H.freshGame();
  var g = t.game;
  W.init(g);
  var d = 500;
  g.dayNight.day = d;
  // resolve chain to repeatIndex 4 (each resolve on its own day, quota ore)
  var quotaSeries = [6, 9, 14, 18];
  for (var i = 0; i < 4; i++) {
    W.tryOpen();
    t.inv.addItem(ORE, quotaSeries[i]);
    W.tryOpen();
    t.inv.removeItem(ORE, quotaSeries[i]);
    d++;
    g.dayNight.day = d;
  }
  // now repeatIndex 4; award + carry EXACTLY 18 + turn in
  var coinsBefore = t.inv.countOf(COIN);
  W.tryOpen();
  t.inv.addItem(ORE, 18);
  W.tryOpen();
  var delta = t.inv.countOf(COIN) - coinsBefore;
  check('V-4k row m (r4, ore 18) coin delta EXACTLY 14', delta === 14, 'got ' + delta);
})();

console.log(H.out.join('\n'));
console.log(H.FAILS.length ? '\nV-4 RESULT: ' + H.FAILS.length + ' FAILURES' : '\nV-4 RESULT: ALL ' + H.out.length + ' CHECKS PASS');
process.exit(H.FAILS.length ? 1 : 0);
