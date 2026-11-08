// CC-C7 headless validation checker (Testerbot). node scratch/cc_c7_check.js
// vm-evals CONFIG.js with a window stub + greps sources for line evidence.
var fs = require('fs'), vm = require('vm'), cp = require('child_process');
var J = 'prototype/js/';
function src(f) { return fs.readFileSync(J + f, 'utf8').split('\n'); }
function lines(f, re) {
  var out = [];
  src(f).forEach(function (l, i) { if (re.test(l)) out.push(i + 1); });
  return out;
}
var res = [];
function check(id, name, ok, ev) { res.push({ id: id, name: name, ok: !!ok, ev: ev }); }

var ctx = { window: {} }; vm.createContext(ctx);
vm.runInContext(fs.readFileSync(J + 'CONFIG.js', 'utf8'), ctx);
var C = ctx.window.WH_CONFIG, M = C.enemy.rotmother, S = C.enemy.rotspawn;
function eq(a, b) { return JSON.stringify(a) === JSON.stringify(b); }

// (a)
var aM = [
  ['hp', M.hp === 460], ['speed', M.speed === 1.6],
  ['lair', M.lair.x === -175 && M.lair.y === 95 && M.lair.region === 'C'],
  ['slamCooldown', M.slamCooldown === 3.4], ['slamWindup', M.slamWindup === 1.15],
  ['poison', eq(M.poison, { dps: 3.5, duration: 4.0, slow: 0.45 })],
  ['rearm', M.rearm.days === 3 && M.rearm.radius === 14 && M.rearm.trigger === 'proximity'],
  ['loot', eq(M.loot, [{ mat: 'rot-silk', n: [2, 4] }, { mat: 'rot-gland', n: [1, 2] }])],
  ['minions', M.minions.cap === 3 && M.minions.interval === 7 && M.minions.range === 6 &&
    M.minions.dieOnMasterDeath === true && M.minions.asset === 'rotspawn']
];
var aS = [['hp', S.hp === 26], ['dmg', S.dmg === 5], ['speed', S.speed === 2.4],
  ['aggro', S.aggro === 14], ['scale', S.scale === 0.8]];
var aFail = aM.concat(aS).filter(function (x) { return !x[1]; }).map(function (x) { return x[0]; });
var row = C.regionC.enemies.filter(function (e) { return e.type === 'rotmother'; });
var worldOk = row.length === 1 && row[0].x === C.regionC.center.x + M.lair.x && row[0].z === C.regionC.center.z + M.lair.y;
check('a', 'CONFIG rows exact', aFail.length === 0 && worldOk,
  'CONFIG.js rotmother L' + lines('CONFIG.js', /^\s+rotmother: \{/) + ', rotspawn L' + lines('CONFIG.js', /^\s+rotspawn: \{/) +
  ', regionC row L' + lines('CONFIG.js', /type: 'rotmother'/) + ' (world ' + (row[0] && row[0].x) + ',' + (row[0] && row[0].z) +
  ' = center+lair: ' + worldOk + ')' + (aFail.length ? ' FAILED: ' + aFail : ''));

// (b)
var b = {
  cfg: M.slamRadius === 3.2 && M.slamArcDeg === 180,
  derive: lines('enemy.js', /c\.attackRange = row\.slamRadius/).length && lines('enemy.js', /hitArcDeg: row\.slamArcDeg \/ 2/).length,
  arc: lines('enemy.js', /distToPlayer <= this\.cfg\.attackRange \+ window\.WH_CONFIG\.player\.radius/).length,
  impact: lines('enemy.js', /this\.slamImpact\(inArc/).length,
  poison: lines('enemy.js', /G\.applyPlayerPoison\(this\.cfg\.poison/).length,
  knock: lines('enemy.js', /G\.knockbackPlayer\(toX \/ dist/).length,
  refresh: lines('game.js', /game\.poison = \{ dps: def\.dps, slow: def\.slow/).length,
  slow: lines('game.js', /var k = 1 - game\.poison\.slow/).length
};
check('b', 'slam AoE 180/3.2 + knockback + poison', Object.keys(b).every(function (k) { return b[k]; }),
  'CONFIG slamRadius L' + lines('CONFIG.js', /slamRadius: 3\.2/) + ' slamArcDeg L' + lines('CONFIG.js', /slamArcDeg: 180/) +
  '; enemy.js deriveCfg L' + lines('enemy.js', /c\.attackRange = row\.slamRadius|hitArcDeg: row\.slamArcDeg/) +
  ', arc test L' + lines('enemy.js', /distToPlayer <= this\.cfg\.attackRange \+|Math\.abs\(hitYaw\) <= phase\.hitArcDeg/) +
  ', slamImpact call L' + lines('enemy.js', /this\.slamImpact\(inArc/) + ', def L' + lines('enemy.js', /prototype\.slamImpact = /) +
  ', poison L' + lines('enemy.js', /G\.applyPlayerPoison\(this\.cfg\.poison/) + ', knockback L' + lines('enemy.js', /G\.knockbackPlayer\(toX/) +
  '; game.js applyPlayerPoison L' + lines('game.js', /function applyPlayerPoison/) + ' (refresh L' + lines('game.js', /game\.poison = \{ dps: def\.dps/) +
  '), slow L' + lines('game.js', /var k = 1 - game\.poison\.slow/) + ', knockbackPlayer L' + lines('game.js', /function knockbackPlayer/) +
  ', tick L' + lines('game.js', /function poisonTick/));

// (c)
var c = {
  gate: lines('enemy.js', /this\.fsm !== 'dead' && playerAlive && dNest <= cfg\.lairRadius/),
  interval: lines('enemy.js', /L\.spawnT >= M\.interval && alive < M\.cap/),
  count: lines('enemy.js', /if \(L\.minions\[i\]\.fsm !== 'dead'\) alive\+\+/),
  range: lines('enemy.js', /Math\.cos\(a\) \* M\.range/),
  die: lines('enemy.js', /if \(this\.cfg\.minions\.dieOnMasterDeath\)/),
  dieCall: lines('enemy.js', /if \(this\.lair\) this\.lairOnDeath\(\)/)
};
check('c', 'minion spawner 7s/6m/cap3/dieOnMasterDeath',
  Object.keys(c).every(function (k) { return c[k].length; }) && M.lairRadius === 14,
  'enemy.js gate L' + c.gate + ', interval+cap L' + c.interval + ', alive count L' + c.count + ', 6 m ring L' + c.range +
  ', wither L' + c.die + ' (called from death L' + c.dieCall + '); CONFIG lairRadius 14 L' + lines('CONFIG.js', /lairRadius: 14/));

// (d)
var d = {
  flag: lines('enemy.js', /return 'rotmother_cleared_' \+ letter/),
  rearm: lines('enemy.js', /gameDay\(\) - st\.day >= cfg\.rearm\.days/),
  prox: lines('enemy.js', /dNest <= cfg\.rearm\.radius/),
  once: lines('enemy.js', /st\.cleared = false;/),
  setDay: lines('enemy.js', /LAIR_STATE\[L\.nest\.letter\] = \{ cleared: true, day: gameDay\(\) \}/),
  cap: lines('enemy.js', /Enemy\.captureLairs = /), rest: lines('enemy.js', /Enemy\.restoreLairs = /),
  saveWrap: lines('game.js', /data\.lairs = window\.WH_Enemy\.captureLairs\(\)|stored\.lairs = window\.WH_Enemy\.captureLairs\(\)|window\.WH_Enemy\.restoreLairs\(data\.lairs\)/)
};
check('d', 're-arm flag/+3 day/14 m', Object.keys(d).every(function (k) { return d[k].length; }),
  'enemy.js lairFlag L' + d.flag + ', death day stamp L' + d.setDay + ', +3 day test L' + d.rearm + ', 14 m proximity L' + d.prox +
  ', clear-once L' + d.once + ', captureLairs L' + d.cap + ', restoreLairs L' + d.rest + '; game.js WH_SAVE wrap L' + d.saveWrap);

// (e)
var I = C.items, e1 = I['rot-silk'], e2 = I['rot-gland'];
check('e', 'rot-silk + rot-gland registry + drop-log',
  e1 && e2 && e1.dropLog && e2.dropLog && e1.flavor && e2.flavor && lines('game.js', /d && d\.dropLog && !game\.dropLogSeen/).length,
  "CONFIG.js items L" + lines('CONFIG.js', /'rot-silk':|'rot-gland':/) + ' dropLog L' + lines('CONFIG.js', /dropLog: 'Rot-/) +
  '; game.js drop-log consumer L' + lines('game.js', /d && d\.dropLog && !game\.dropLogSeen/) + ', typed loot roll L' + lines('game.js', /function rollTypeLoot|rollTypeLoot\(typeCfg\.loot\)/));

// (f)
var ctxA = { window: { WH_CONFIG: C }, THREE: {} }; ctxA.window.THREE = {}; vm.createContext(ctxA);
var RC = null;
try { vm.runInContext(fs.readFileSync(J + 'anim.js', 'utf8'), ctxA); RC = ctxA.window.WH_RigidAnim && ctxA.window.WH_RigidAnim.CLIPS; } catch (err) { RC = null; }
var fOk, fEv;
if (RC) {
  var mn = RC.rotmother.names, sn = RC.rotspawn.names;
  fOk = ['idle', 'walk', 'attack', 'hit', 'death', 'spare'].every(function (k) { return mn[k]; }) &&
    ['idle', 'walk', 'attack', 'death'].every(function (k) { return sn[k]; }) &&
    RC.rotmother.clipScale === 1.0 && RC.rotspawn.clipScale === 1.3;
  fEv = 'evaluated: mother ' + JSON.stringify(mn) + ' spawn ' + JSON.stringify(sn);
} else {
  fOk = lines('anim.js', /RM_Idle.*RM_Lumber.*RM_Slam.*RM_Hit/).length && lines('anim.js', /RS_Idle.*RS_Crawl.*RS_Lunge/).length &&
    lines('anim.js', /clipScale: 1\.0,/).length && lines('anim.js', /clipScale: 1\.3,/).length;
  fEv = 'regex (anim.js eval needs THREE)';
}
check('f', 'RIGID_CLIPS placeholder set', fOk,
  'anim.js RIGID_CLIPS L' + lines('anim.js', /var RIGID_CLIPS = \{/) + ', mother names L' + lines('anim.js', /RM_Idle/) +
  ' clipScale 1.0 L' + lines('anim.js', /clipScale: 1\.0,/) + ', spawn names L' + lines('anim.js', /RS_Idle/) +
  ' clipScale 1.3 L' + lines('anim.js', /clipScale: 1\.3,/) + '; CONFIG rigidAnimByType L' + lines('CONFIG.js', /rigidAnimByType:/) + ' [' + fEv + ']');

// (g)
var files = cp.execSync('git diff --name-only a948290..bef33f1').toString().trim().split('\n');
var allowed = [/^prototype\/js\/(CONFIG|data|enemy|game|anim)\.js$/, /^prototype\/builds\/[^/]+\.html$/, /^io\/missions\//, /lair.*\.json$/];
var forbidden = [/^docs\/planning\//, /^art-direction\//, /style\.css$/, /(^|\/)index\.html$/,
  /\/(save|daynight|camp|player|cooking)\.js$/];
var forb = files.filter(function (f) { return forbidden.some(function (r) { return r.test(f); }); });
var other = files.filter(function (f) { return !allowed.some(function (r) { return r.test(f); }) && forb.indexOf(f) < 0; });
check('g', 'scope audit', forb.length === 0,
  'files: ' + files.join(', ') + ' | FORBIDDEN touched: ' + (forb.join(', ') || 'none') + ' | other (flagged): ' + (other.join(', ') || 'none'));

// (h)
var node = process.execPath, js = files.filter(function (f) { return /\.js$/.test(f); }), bad = [];
js.forEach(function (f) { try { cp.execFileSync(node, ['--check', f], { stdio: 'pipe' }); } catch (err) { bad.push(f); } });
check('h', 'node --check edited js', bad.length === 0, js.join(', ') + (bad.length ? ' FAILED: ' + bad : ' all OK'));

res.forEach(function (r) { console.log((r.ok ? 'PASS' : 'FAIL') + ' | ' + r.id + ' | ' + r.name + ' | ' + r.ev); });
