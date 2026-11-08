'use strict';
// CC-EN1 pre-build baseline + post-build census probe (Testerbot).
// Loads the engine bundle minimally in node (no DOM, no browser) and prints the
// pinned numbers the valspec freezes. Usage: node probe_config_baseline.js [post]
//   no arg  = pre-build baseline mode (asserts WH_ENCOUNTERS absent)
//   'post'  = post-build mode (asserts WH_ENCOUNTERS present + table laws)
globalThis.window = globalThis;
globalThis.self = globalThis;
require('/tmp/wh-worldfeat/prototype/vendor/three.classic.js');
require('/tmp/wh-worldfeat/prototype/js/CONFIG.js');
require('/tmp/wh-worldfeat/prototype/js/wh-ground.js');
var CFG = window.WH_CONFIG;
var post = (process.argv[2] === 'post');

function enc() { return CFG.encounters; }

console.log('== world ==');
console.log('world.groundRadius:', CFG.world.groundRadius, 'PLAYER-MARGIN:', CFG.world.playerMargin,
  'playableR:', CFG.world.groundRadius - CFG.world.playerMargin);
console.log('boundary.z:', CFG.boundary.z);
console.log('scatter.clear.nodeM:', CFG.scatter.clear.nodeM, 'scatter.clear.enemyM:', CFG.scatter.clear.enemyM);
var ko = null;
for (var i = 0; i < CFG.scatter.keepOut.length; i++) {
  if (CFG.scatter.keepOut[i].regionId === 'darkwood_edge') ko = CFG.scatter.keepOut[i];
}
console.log('regionB keepOut row:', JSON.stringify(ko), 'keepOut rows total:', CFG.scatter.keepOut.length);

console.log('== regionB baseline ==');
console.log('props:', CFG.regionB.props.length, 'nodes:', CFG.regionB.nodes.length,
  'enemies:', CFG.regionB.enemies.length, 'types:', CFG.regionB.enemies.map(function (e) { return e.type; }).join(','));
var fires = CFG.regionB.props.filter(function (p) { return p.asset === 'banditCampfire'; });
console.log('fires:', fires.length, JSON.stringify(fires.map(function (f) { return [f.x, f.z]; })));
console.log('WG has darkwood_edge:', window.WH_GROUND.has('darkwood_edge'));
console.log('WG.has forest_of_the_old_king:', window.WH_GROUND.has('forest_of_the_old_king'));

console.log('== enemy kit ==');
console.log(['bandit', 'ghoul', 'wolf', 'coven'].map(function (t) { return t + '=' + !!CFG.enemy[t]; }).join(' '));
console.log('WH_Enemy:', typeof window.WH_Enemy, 'makeBody:', window.WH_Enemy ? typeof window.WH_Enemy.makeBody : 'n/a (late load: encounters.js reads it at tick, not load)');

if (!post) {
  console.log('== PRE-BUILD assertions ==');
  console.log('WH_ENCOUNTERS absent before build:', typeof window.WH_ENCOUNTERS === 'undefined');
  console.log('CFG.encounters absent before build:', !enc());
  process.exit((typeof window.WH_ENCOUNTERS === 'undefined' && !enc()) ? 0 : 1);
}

console.log('== POST-BUILD census ==');
var ok = true;
function chk(label, cond) { ok = ok && !!cond; console.log((cond ? 'PASS ' : 'FAIL ') + label); }
var E = enc();
chk('CFG.encounters exists', !!E);
chk('director regionId darkwood_edge', E && E.director && E.director.regionId === 'darkwood_edge');
var dw = E && E.biomes && E.biomes.darkwood_edge;
chk('darkwood_edge biome table exists', !!dw);
var nightFams = dw ? dw.night.map(function (r) { return r.family; }).sort() : [];
chk('night families == [1,2,3,5,8]', JSON.stringify(nightFams) === JSON.stringify([1, 2, 3, 5, 8]));
chk('weights len == night.length+1', dw && dw.weights.length === dw.night.length + 1);
var wsum = dw ? dw.weights.reduce(function (a, b) { return a + b; }, 0) : -1;
chk('weights sum == 1.0 (+-1e-9)', Math.abs(wsum - 1.0) <= 1e-9);
chk('weights[0] === 0', dw && dw.weights[0] === 0);
var kit = { bandit: 1, ghoul: 1, wolf: 1, coven: 1 };
var typesOk = dw && dw.night.concat(dw.day).every(function (row) {
  return row.comp.every(function (c) { return kit[c.type] && c.n >= 1 && c.n <= 3; });
});
chk('every comp type in live kit, 1<=n<=3', typesOk);
var hasDay3 = dw && dw.day.length === 1 && dw.day[0].family === 3;
chk('day rows: exactly family 3', hasDay3);
var pend = dw && dw.pending && Object.keys(dw.pending).join(',');
chk('pending notes present (F2 + F4/F6/F7 family names): ' + pend, dw && Object.keys(dw.pending).length >= 1);
var fk = E && E.biomes && E.biomes.forest_of_the_old_king;
var fkRow = fk && fk.night && fk.night[0];
chk('regionC table: 1 night row, family 4, live cc-ae1', fkRow && fkRow.family === 4 && fkRow.live === 'cc-ae1');
chk('regionC table pending notes (F1-lair-pair + EN1-4 F6/F7 story; >=1, join has F1)',
  fk && fk.pending && Object.keys(fk.pending).length >= 1 &&
  Object.keys(fk.pending).join(',').indexOf('F1') >= 0);
var rng = require('fs').readFileSync('/tmp/wh-worldfeat/prototype/js/encounters.js', 'utf8');
var rollCount = (rng.match(/Math\.random/g) || []).length;
chk('encounters.js Math.random call sites <= 4 (2 functions, band jitters allowed)', rollCount <= 4);
chk('raidMember assigned at spawn', rng.indexOf('raidMember = true') >= 0 || rng.indexOf('raidMember=true') >= 0);

console.log(ok ? 'CENSUS OVERALL PASS' : 'CENSUS OVERALL FAIL');
process.exit(ok ? 0 : 1);
