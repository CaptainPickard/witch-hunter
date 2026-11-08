// CC-EC1 integrated end-to-end pass: coven fires at a player 5m away; replicate
// game.js's EXACT enemy-bolt keep-alive loop (extracted verbatim by eval) and
// assert: single magicDefense call, reduced damage 14 -> round(14*0.75) = 11,
// bare {isSpell,pos} attacker with no enterStagger.
(function () {
  var fs = require('fs'), vm = require('vm');
  global.window = global;
  var V3 = function (x, y, z) { this.x = x || 0; this.y = y || 0; this.z = z || 0; };
  function mk() { return { set: function () {}, copy: function () {} }; }
  global.THREE = {
    Vector3: V3, Group: function () { this.children = []; this.position = mk(); this.rotation = { y: 0 }; this.add = function () {}; this.remove = function () {}; },
    Mesh: function (g, m) { this.geometry = g; this.material = m; this.position = mk(); this.scale = { setScalar: function () {} }; this.visible = true; },
    SphereGeometry: function (r) { this.radius = r; },
    MeshBasicMaterial: function (p) { this.parameters = p; this.color = p && p.color; this.opacity = 0; this.transparent = true; },
    Box3: function () { this.min = {}; this.setFromObject = function () {}; },
    Quaternion: function () { this.setFromAxisAngle = function () {}; this.premultiply = function () {}; this.copy = function () {}; }
  };
  vm.runInThisContext(fs.readFileSync('prototype/js/CONFIG.js', 'utf8'));
  var scene = { add: function () {}, remove: function () {} };
  var mdCalls = 0, incoming = [];
  global.WH_LEVEL = { magicDefense: function () { mdCalls++; return 0.25; } };
  window.WH_GAME = {
    scene: scene,
    player: { state: 'alive', pos: new V3(5, 0, 0), resolveIncomingHit: function (d, a) { incoming.push({ d: d, a: a }); return true; } }
  };
  window.WH_GROUND = { has: function () { return false; }, heightAt: function () { return 0; } };
  vm.runInThisContext(fs.readFileSync('prototype/js/spells.js', 'utf8'));
  vm.runInThisContext(fs.readFileSync('prototype/js/enemy.js', 'utf8'));
  var src = fs.readFileSync('prototype/js/game.js', 'utf8');
  var loopSrc = src.match(/if \(game\.enemyBolts\.length > 0\) \{[\s\S]*?\n    \}/)[0];
  var game = { enemyBolts: [], player: window.WH_GAME.player };
  global.game = game;
  global.dt = 1 / 30;
  var Enemy = window.WH_Enemy;
  window.WH_Enemy.onEnemyBolt = function (b) { game.enemyBolts.push(b); };
  var cov = new Enemy('coven', scene, 'C', 0, 0); cov.pos.y = 0;
  var frames = 0;
  // hook BEFORE the first update could spawn anything
  window.WH_Enemy.onEnemyBolt = function (b) { game.enemyBolts.push(b); };
  while (cov.fsm !== 'attack' && frames < 120) { cov.update(dt, { x: 5, y: 0, z: 0 }, true, function () {}, null, null); frames++; }
  while (game.enemyBolts.length === 0 && frames < 300) { cov.update(dt, { x: 5, y: 0, z: 0 }, true, function () {}, null, null); frames++; }
  var boltArrival = game.enemyBolts.length === 1;
  var hitFrame = -1;
  for (var f = 0; f < 200 && hitFrame < 0; f++) {
    cov.update(dt, { x: 5, y: 0, z: 0 }, true, function () {}, null, null);
    // verbatim game.js loop (vars resolve against this scope)
    eval(loopSrc);
    if (incoming.length) hitFrame = f;
  }
  var h = incoming[0];
  var exp = Math.round(14 * (1 - 0.25));
  var pass = 0, fail = 0;
  function chk(n, c, d) { if (c) { pass++; console.log('ok   ' + n); } else { fail++; console.log('FAIL ' + n + (d ? ' :: ' + d : '')); } }
  chk('bolt lands in game.enemyBolts via onEnemyBolt', boltArrival);
  chk('player hit ~0.3s after spawn (5m @16u/s)', hitFrame >= 8 && hitFrame <= 12, 'hitFrame=' + hitFrame);
  chk('magicDefense called EXACTLY once', mdCalls === 1, 'calls=' + mdCalls);
  chk('reduced damage round(14*0.75)=11', h.d === exp, 'seen=' + h.d + ' exp=' + exp);
  chk('attacker bare {isSpell, pos} - no methods', h.a.isSpell === true && typeof h.a.pos.x === 'number' && !h.a.enterStagger && Object.keys(h.a).length === 2, JSON.stringify(Object.keys(h.a)));
  console.log('integrated: ' + pass + ' ok, ' + fail + ' fail');
  process.exit(fail ? 1 : 0);
})();
