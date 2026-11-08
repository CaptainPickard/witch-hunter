// V-5 persistence one-shot (cc-wb2): payload exact keys, round-trip, clamps,
// WB1 3-key restore, hostile restore inputs.
'use strict';
var H = require('/tmp/wb2_harness.js');
var check = H.check;
H.out.length = 0; H.FAILS.length = 0;
var ORE = 'ironOre';

// fresh board that just resolved once (r1) and captured
function resolvedBoard(day) {
  var W = H.reloadModule();
  var t = H.freshGame();
  W.init(t.game);
  t.game.dayNight.day = day;
  W.tryOpen();
  t.inv.addItem(ORE, 6);
  W.tryOpen();
  return { W: W, t: t, payload: W.capture() };
}

// V-5l: capture keys EXACTLY the 4-key set
var rb = resolvedBoard(10);
var keys = Object.keys(rb.payload);
check('V-5l capture keys === {active, postedDay, resolvedDay, repeatIndex}',
  keys.length === 4 &&
  ['active', 'postedDay', 'resolvedDay', 'repeatIndex'].every(function (k) { return keys.indexOf(k) >= 0; }),
  'keys=' + JSON.stringify(keys));
check('V-5l resolved capture values', rb.payload.active === false &&
  rb.payload.postedDay === 10 && rb.payload.resolvedDay === 10 && rb.payload.repeatIndex === 1,
  JSON.stringify(rb.payload));

// V-5m: strict round-trip restore(payload)->capture() deep equal for R=0,1,7,18
[0, 1, 7, 18].forEach(function (R) {
  var W = H.reloadModule();
  var t = H.freshGame();
  W.init(t.game);
  t.game.dayNight.day = 20;
  var payload = { active: true, postedDay: 20, resolvedDay: null, repeatIndex: R };
  W.restore(JSON.parse(JSON.stringify(payload)));
  var c = W.capture();
  var ok = c.active === true && c.postedDay === 20 && c.resolvedDay === null && c.repeatIndex === R;
  check('V-5m round-trip R=' + R, ok, 'capture=' + JSON.stringify(c));
});

// V-5n: clamp law (hostile repeatIndex values -> 0, no throw)
[[-3, 'negative int'],
  ['7', 'string number'],
  [2.5, 'fractional'],
  [Infinity, 'Infinity'],
  ['x', 'junk string'],
  [true, 'boolean true'],
  [null, 'null'],
  [{}, 'object'],
  [[], 'array']].forEach(function (pair) {
  var val = pair[0], label = pair[1];
  var W = H.reloadModule();
  var t = H.freshGame();
  W.init(t.game);
  t.game.dayNight.day = 30;
  var threw = null;
  try { W.restore({ active: true, postedDay: 30, resolvedDay: null, repeatIndex: val }); } catch (e) { threw = e; }
  var c = W.capture();
  check('V-5n clamp repeatIndex ' + label + ' (' + JSON.stringify(val) + ') -> 0, no throw',
    c.repeatIndex === 0 && c.active === true && !threw,
    'capture=' + JSON.stringify(c) + ' threw=' + threw);
});

// missing key entirely -> 0
(function () {
  var W = H.reloadModule();
  W.restore({ active: true, postedDay: 31, resolvedDay: null });
  check('V-5n missing repeatIndex key -> 0', W.capture().repeatIndex === 0,
    JSON.stringify(W.capture()));
})();

// V-5o: WB1 3-key payload loads clean, repeatIndex 0
(function () {
  var W = H.reloadModule();
  var t = H.freshGame();
  W.init(t.game);
  t.game.dayNight.day = 40;
  W.restore({ active: true, postedDay: 40, resolvedDay: null });   // WB1 shape
  var c = W.capture();
  check('V-5o WB1 3-key restore: repeatIndex 0', c.repeatIndex === 0, JSON.stringify(c));
  check('V-5o WB1 3-key restore: state kept (active, postedDay)',
    c.active === true && c.postedDay === 40, JSON.stringify(c));
  var p = W.interactPrompt();
  check('V-5o WB1 3-key restore: active prompt works at quota 6',
    /E - War Board \(0\/6 iron ore\)/.test(p), JSON.stringify(p));
  // WB1 spent profile
  W.restore({ active: false, postedDay: 40, resolvedDay: 40 });
  check('V-5o WB1 spent profile: prompt dawn line',
    /spent until dawn/.test(W.interactPrompt()), JSON.stringify(W.interactPrompt()));
  check('V-5o WB1 spent profile: repeatIndex 0', W.capture().repeatIndex === 0);
})();

// V-5p: hostile restore inputs — no throw, state clean
[['null', null], ['undefined', undefined], ['garbage string', 'garbage'],
  ['empty array', []], ['number 42', 42], ['false', false]].forEach(function (pair) {
  var W = H.reloadModule();
  var t = H.freshGame();
  W.init(t.game);
  t.game.dayNight.day = 50;
  var before = W.capture();
  var threw = null;
  try { W.restore(pair[1]); } catch (e) { threw = e; }
  var after = W.capture();
  check('V-5p restore(' + pair[0] + ') no throw, state clean/idle',
    !threw && after.active === false && after.resolvedDay === null,
    'before=' + JSON.stringify(before) + ' after=' + JSON.stringify(after) + ' threw=' + threw);
});

console.log(H.out.join('\n'));
console.log(H.FAILS.length ? '\nV-5 RESULT: ' + H.FAILS.length + ' FAILURES' : '\nV-5 RESULT: ALL ' + H.out.length + ' CHECKS PASS');
process.exit(H.FAILS.length ? 1 : 0);
