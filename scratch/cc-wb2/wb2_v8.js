// V-8 runtime surface one-shot (cc-wb2): CONFIG clean-require; WH_WarEffort
// exact 6 public functions.
'use strict';
var H = require('/tmp/wb2_harness.js');
var check = H.check;
H.out.length = 0; H.FAILS.length = 0;

// V-8/1: CONFIG require-clean (fresh process proof, real file)
var cp = require('child_process');
var parseOut = '';
try {
  parseOut = cp.execSync(
    'node -e "global.window=global; require(\'/tmp/wh-worldfeat/prototype/js/CONFIG.js\');" 2>&1 && echo CONFIG-OK',
    { cwd: '/tmp' }).toString();
} catch (e) { parseOut = String(e.stdout || '') + String(e.stderr || e.message); }
check('V-8 CONFIG require-clean', /CONFIG-OK/.test(parseOut) && !/Error|error/.test(parseOut),
  parseOut.slice(0, 300));

// V-8/2: wareffort require-clean (fresh process, THREE shim inline)
var wOut = '';
try {
  wOut = cp.execSync(
    'node -e "global.window=global; global.THREE={DoubleSide:2,Group:function(){this.children=[]},Mesh:function(g,m){this.geometry=g;this.material=m},BoxGeometry:function(){},PlaneGeometry:function(){},MeshStandardMaterial:function(o){this.color=o&&o.color}};' +
    'global.window.WH_CONFIG={}; require(\'/tmp/wh-worldfeat/prototype/js/CONFIG.js\'); ' +
    'require(\'/tmp/wh-worldfeat/prototype/js/wareffort.js\');" 2>&1 && echo WAREFFORT-OK',
    { cwd: '/tmp' }).toString();
} catch (e) { wOut = String(e.stdout || '') + String(e.stderr || e.message); }
check('V-8 wareffort require-clean', /WAREFFORT-OK/.test(wOut), wOut.slice(0, 300));

// V-8/3: public surface EXACT 6 functions
var W = H.reloadModule();
var keys = Object.keys(W).sort();
var want = ['boardPos', 'capture', 'init', 'interactPrompt', 'restore', 'tryOpen'].sort();
check('V-8 surface keys exactly the WB1 6', keys.length === 6 && JSON.stringify(keys) === JSON.stringify(want),
  'keys=' + JSON.stringify(keys));
check('V-8 every key typeof function',
  keys.every(function (k) { return typeof W[k] === 'function'; }), JSON.stringify(keys));
// signatures: arity census (call-shape) — init(g), tryOpen(), interactPrompt(),
// capture(), restore(data), boardPos()
check('V-8 arity census init(1)/tryOpen(0)/interactPrompt(0)/capture(0)/restore(1)/boardPos(0)',
  W.init.length === 1 && W.tryOpen.length === 0 && W.interactPrompt.length === 0 &&
  W.capture.length === 0 && W.restore.length === 1 && W.boardPos.length === 0,
  'arities=' + JSON.stringify([W.init.length, W.tryOpen.length, W.interactPrompt.length, W.capture.length, W.restore.length, W.boardPos.length]));

// behaviors still work after the edit (call-level smoke through public API)
var t = H.freshGame();
W.init(t.game);
check('V-8 behavior: init built the board root', t.scene.children.length === 1 &&
  t.scene.children[0].name === 'cc-wb1-war-effort-board', 'children=' + t.scene.children.length);
check('V-8 behavior: boardPos', JSON.stringify(W.boardPos()) === JSON.stringify({ x: 5.9, z: -15.5 }),
  JSON.stringify(W.boardPos()));
check('V-8 behavior: idle prompt WB1 verbatim',
  W.interactPrompt() === 'E - War Board (Take a requisition)', JSON.stringify(W.interactPrompt()));
check('V-8 behavior: capture shape (3 or 4 keys at idle)',
  (function () {
    var c = W.capture();
    var k = Object.keys(c);
    return (k.length === 3 || k.length === 4) && k.indexOf('active') >= 0;
  })(), JSON.stringify(W.capture()));

console.log(H.out.join('\n'));
console.log(H.FAILS.length ? '\nV-8 RESULT: ' + H.FAILS.length + ' FAILURES' : '\nV-8 RESULT: ALL ' + H.out.length + ' CHECKS PASS');
process.exit(H.FAILS.length ? 1 : 0);
