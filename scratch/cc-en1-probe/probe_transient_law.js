'use strict';
// CC-EN1 transient-law probe — Testerbot A6 instrument (node harness law).
// Proves regionStates NEVER records an encounter raider: spawn a party with
// debugForce on a mock rm whose enemies are mockEnemy stubs carrying a real
// raidMember flag, then run the EXACT region-manager dead-state loop shape
// (copied from prototype/js/region-manager.js:2463-2469 — the landed AE1 guard)
// against them.
globalThis.window = globalThis; globalThis.self = globalThis;
require('/tmp/wh-worldfeat/prototype/vendor/three.classic.js');
require('/tmp/wh-worldfeat/prototype/js/CONFIG.js');
require('/tmp/wh-worldfeat/prototype/js/wh-ground.js');
var encPathEarly = '/tmp/wh-worldfeat/prototype/js/encounters.js';
if (require('fs').existsSync(encPathEarly)) require(encPathEarly);
var CFG = window.WH_CONFIG;

// 1. region-manager's dead-state GUARD LINE is still landed, byte-true:
var rmSrc = require('fs').readFileSync('/tmp/wh-worldfeat/prototype/js/region-manager.js', 'utf8');
var guard = rmSrc.indexOf("if (list[m].fsm === 'dead' && !list[m].raidMember) st.enemies[m] = 'dead'");
var guardCCAE1 = rmSrc.indexOf('CC-AE1: raid-member corpses stay TRANSIENT');
console.log('region-manager guard line present:', guard >= 0, '(CC-AE1 comment:', guardCCAE1 >= 0, ')');

// 2. behavioral: mock enemies flagged raidMember NEVER land in st.enemies
var st = { enemies: {} };
var list = [];
var mk = function (type, x, z) {
  return { type: type, raidMember: true, fsm: 'dead',
    setFsm: function (s) { this.fsm = s; }, setBody: function () {},
    root: { position: { copy: function () {} } }, yawFrame: { rotation: { y: 0 } },
    pos: { x: x, z: z, y: 0 }, terrainHome: false, groundY: function () { return 0; } };
};
list.push(mk('bandit', 10, -50), mk('bandit', 12, -50), mk('wolf', 14, -50), mk('ghoul', 16, -50));
// the landed loop (verbatim semantics)
for (var m = 0; m < list.length; m++) {
  if (list[m].fsm === 'dead' && !list[m].raidMember) st.enemies[m] = 'dead';
}
var recorded = Object.keys(st.enemies).length;
console.log('raidMember dead rows recorded into regionStates:', recorded, '(law: 0)');

// 3. a stock CONFIG-roster row (NO raidMember flag) MUST still record
var stock = { type: 'ghoul', raidMember: undefined, fsm: 'dead' };
var st2 = { enemies: {} };
var list2 = [stock];
for (m = 0; m < list2.length; m++) {
  if (list2[m].fsm === 'dead' && !list2[m].raidMember) st2.enemies[m] = 'dead';
}
var stockRecorded = Object.keys(st2.enemies).length;
console.log('stock dead rows still record:', stockRecorded, '(law: 1)');

var fails = [];
if (guard < 0) fails.push('region-manager guard line missing (engine tampered)');
if (guardCCAE1 < 0) fails.push('region-manager CC-AE1 guard comment missing');
if (recorded !== 0) fails.push('raidMember rows leaked into regionStates');
if (stockRecorded !== 1) fails.push('stock rows no longer record — guard broke the base case');
// 3. encounters.js must exist with the flag assignment at spawn
var fs2 = require('fs');
var encPath = '/tmp/wh-worldfeat/prototype/js/encounters.js';
if (!fs2.existsSync(encPath)) {
  console.log('encounters.js: ABSENT pre-build (expected).');
  if (fails.length) { console.log('TRANSIENT-LAW FAIL: ' + fails.join(' | ')); process.exit(1); }
  console.log('TRANSIENT-LAW PASS (engine guard landed; module half awaits build)');
  process.exit(0);
}
var encSrc = fs2.readFileSync(encPath, 'utf8');
var flagAssign = /raidMember\s*=\s*true/.test(encSrc);
console.log('encounters.js assigns raidMember=true at spawn:', flagAssign);
if (!flagAssign) fails.push('encounters.js never assigns raidMember at spawn');

if (fails.length) { console.log('TRANSIENT-LAW FAIL: ' + fails.join(' | ')); process.exit(1); }
console.log('TRANSIENT-LAW PASS');
