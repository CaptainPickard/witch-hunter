// V-6 tally pins one-shot (cc-wb2): pin census 1/4, restore 10 -> 8 cap,
// restore 3 -> 3; ONE board root only; pins are iron (no red, no extra
// emissive).
'use strict';
var H = require('/tmp/wb2_harness.js');
var check = H.check;
H.out.length = 0; H.FAILS.length = 0;
var ORE = 'ironOre';

function freshW() { return H.reloadModule(); }

// find the tally sub-group inside the board root: it must be a Group-type
// child of the root whose children are the pins. Devbot likely names it
// 'cc-wb2-tally' (marker law); we accept any Group child of the root that
// grows with resolves, but check the NAME for the marker census too.
function rootOf(scene) { return scene.children.filter(function (c) { return c && c.name === 'cc-wb1-war-effort-board'; }); }
function tallyCandidate(root) {
  var groups = root.children.filter(function (c) {
    return c && c.type === 'Group' && c.children && c.children.some(function (g) {
      // a pin: a Box mesh 0.05x0.05x0.12 with iron material
      return g && g.geometry && g.geometry.type === 'Box' &&
        g.geometry.parameters && Math.abs(g.geometry.parameters.width - 0.05) < 1e-9 &&
        Math.abs(g.geometry.parameters.height - 0.05) < 1e-9 &&
        Math.abs(g.geometry.parameters.depth - 0.12) < 1e-9;
    });
  });
  return groups[0] || null;
}
function pinCount(root) {
  var tally = tallyCandidate(root);
  if (!tally) return null;
  return tally.children.filter(function (c) {
    return c && c.geometry && c.geometry.type === 'Box' && c.geometry.parameters &&
      c.geometry.parameters.width === 0.05 && c.geometry.parameters.height === 0.05 &&
      c.geometry.parameters.depth === 0.12;
  }).length;
}

// --- resolves -> pins (1 and 4) ---
var chain = [[1, 1], [4, 4]];
chain.forEach(function (pair) {
  var W = freshW();
  var t = H.freshGame();
  var g = t.game;
  W.init(g);
  var d = 10;
  g.dayNight.day = d;
  for (var i = 0; i < pair[0]; i++) {
    W.tryOpen();
    var q = [6, 9, 14, 18][Math.min(i, 3)];
    t.inv.addItem(ORE, q);
    W.tryOpen();
    t.inv.removeItem(ORE, q);
    d++;
    g.dayNight.day = d;
  }
  var roots = rootOf(t.scene);
  check('V-6r board root count EXACTLY 1 after ' + pair[0] + ' resolves', roots.length === 1,
    'roots=' + roots.length);
  var root = roots[0];
  check('V-6r root name UNCHANGED after resolves',
    root.name === 'cc-wb1-war-effort-board', root.name);
  var pins = pinCount(root);
  check('V-6q pins after ' + pair[0] + ' resolves === ' + pair[1], pins === pair[1],
    'pins=' + pins);
  if (pins > 0) {
    var tally = tallyCandidate(root);
    var ironPin = tally.children[0];
    var col = ironPin.material && ironPin.material.color;
    check('V-6q pin material iron 0x6e6a63',
      col === 0x6e6a63 || (col && col.hex === 0x6e6a63),
      'color=' + (ironPin.material && ironPin.material.color));
  }
});

// --- restore-driven pins: repeatIndex 10 -> 8 cap; repeatIndex 3 -> 3 ---
[[10, 8], [3, 3], [8, 8]].forEach(function (pair) {
  var W = freshW();
  var t = H.freshGame();
  var g = t.game;
  W.init(g);
  g.dayNight.day = 99;
  W.restore({ active: false, postedDay: 99, resolvedDay: 99, repeatIndex: pair[0] });
  var roots = rootOf(t.scene);
  check('V-6q restore repeatIndex ' + pair[0] + ': roots 1', roots.length === 1);
  var pins = rootOf(t.scene).length ? pinCount(roots[0]) : null;
  check('V-6q pins after restore repeatIndex ' + pair[0] + ' === ' + pair[1], pins === pair[1],
    'pins=' + pins);
});

// new-day reset leaves pins (S-3: rebuild on resolve/restore only)
(function () {
  var W = freshW();
  var t = H.freshGame();
  var g = t.game;
  W.init(g);
  var d = 10;
  g.dayNight.day = d;
  for (var i = 0; i < 4; i++) {
    W.tryOpen();
    t.inv.addItem(ORE, [6, 9, 14, 18][i]);
    W.tryOpen();
    t.inv.removeItem(ORE, [6, 9, 14, 18][i]);
    d++;
    g.dayNight.day = d;
  }
  var root = rootOf(t.scene)[0];
  var before = pinCount(root);
  g.dayNight.day = d + 5;
  W.interactPrompt();                              // rollNewDay fires
  var after = pinCount(root);
  check('V-6 new-day reset LEAVES pins (4 stay 4)', before === 4 && after === 4,
    'before=' + before + ' after=' + after);
})();

console.log(H.out.join('\n'));
console.log(H.FAILS.length ? '\nV-6 RESULT: ' + H.FAILS.length + ' FAILURES' : '\nV-6 RESULT: ALL ' + H.out.length + ' CHECKS PASS');
process.exit(H.FAILS.length ? 1 : 0);
