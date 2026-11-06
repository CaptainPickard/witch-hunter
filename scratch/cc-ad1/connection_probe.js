// CC-AD1 connection probe (valspec V7): THREE-free chain CONFIG.js ->
// region-defs.js -> region-manager.js, then assertions on connections[3],
// region registration, and the forceCross / tickTransition semantics.
// Run: node scratch/cc-ad1/connection_probe.js   (exit 0 = all PASS)
'use strict';
var fs = require('fs');
var path = require('path');

global.window = {};
global.localStorage = { getItem: function () { return null; }, setItem: function () {}, removeItem: function () {} };
// region-manager reads THREE at lazy call sites only (V0/C0-7): module scope is THREE-free.
global.THREE = undefined;

var ROOT = path.join(__dirname, '..', '..', 'prototype', 'js');
function evalFile(name) {
  var src = fs.readFileSync(path.join(ROOT, name), 'utf8');
  // eval in global scope so window.* exports land on globalThis
  (0, eval)(src);
}
evalFile('CONFIG.js');
evalFile('region-defs.js');
evalFile('region-manager.js');

var A = [];                       // assertion ledger
function ok(label, cond) { A.push({ label: label, pass: !!cond }); }

var CFG = global.window.WH_CONFIG;
var DEFS = global.window.WH_REGION_DEFS;

var cid = CFG.regionC.id;                       // forest_of_the_old_king
var eid = CFG.regionE.id;                       // veil_crypt
var conn = DEFS.connections[3];
ok('connections[3] exists', !!conn);
ok('connections[3].from = regionC', conn && conn.from === cid);
ok('connections[3].to = regionE', conn && conn.to === eid);
ok('connectionBetween(C, veil_crypt) = conn',
   DEFS.connectionBetween(cid, eid) === conn);
ok('sideIn(conn, regionE) === 1', DEFS.sideIn(conn, eid) === 1);
ok('sideIn(conn, regionC) === -1', DEFS.sideIn(conn, cid) === -1);
ok('planeIn(conn, regionE) === true (walkFrom crypt)',
   DEFS.planeIn(conn, eid) === true);
ok('planeIn(conn, regionC) === false (no plane while in C)',
   DEFS.planeIn(conn, cid) === false);
ok('insideDoorWindow(conn, 0) true (x = doorX)', DEFS.insideDoorWindow(conn, 0) === true);
ok('insideDoorWindow(conn, +3.5) false (halfWidth 2.4)', DEFS.insideDoorWindow(conn, 3.5) === false);
ok('insideDoorWindow(conn, -3.5) false', DEFS.insideDoorWindow(conn, -3.5) === false);
ok('arch: null carried (C0-1)', conn && conn.door && conn.door.arch === null);
ok('gatedTo: null carried (C0-1)', conn && conn.door && conn.door.gatedTo === null);
ok('walkFrom = regionE id', conn && conn.door && conn.door.walkFrom === eid);
ok('interact.from = regionC id', conn && conn.door && conn.door.interact && conn.door.interact.from === cid);

// region registration
var reg = DEFS.regions[eid];
ok('regions[veil_crypt] registered', !!reg);
ok('spawn = land row (0, -604)', reg && reg.spawn && reg.spawn.x === 0 && reg.spawn.z === -604);
ok('center = (0, -596)', reg && reg.center && reg.center.x === 0 && reg.center.z === -596);
ok('groundRadius = 20', reg && reg.groundRadius === 20);
ok('props count = 20 (3 albetar + 8 ring + 9 dressing)',
   reg && reg.cfg && Array.isArray(reg.cfg.props) && reg.cfg.props.length === 20);
ok('enemies = 2 coven rows',
   reg && reg.cfg && Array.isArray(reg.cfg.enemies) && reg.cfg.enemies.length === 2 &&
   reg.cfg.enemies.every(function (e) { return e.type === 'coven'; }));

// ---- forceCross / tickTransition semantics (logic level, C0-7 real manager) ----
var Logic = global.window.WH_RegionManagerLogic;
var logic = new Logic(cid);

// case 1: player on the C side near the interact hook (notch mouth world (0, -596))
// forceCross maps to the crypt land row (0, -604).
var res = logic.forceCross(conn);
ok('forceCross action = cross', res && res.action === 'cross');
ok('forceCross newActiveId = veil_crypt', res && res.newActiveId === eid);
ok('forceCross mappedPos = land row (0, -604)',
   res && res.mappedPos && res.mappedPos.x === 0 && res.mappedPos.z === -604);
ok('activeId now veil_crypt', logic.activeId === eid);

// case 2 (C0-3): landing row must NOT immediately re-cross back to C.
var tr2 = logic.tickTransition(0, -604);
ok('tickTransition at land row: no re-cross', !tr2 || tr2.action === null || tr2.action === 'none' || tr2.action === 'prewarm');

// case 3: while INSIDE the crypt, the mouth plane crosses back to C within the window.
var tr3 = logic.tickTransition(0, -613);
ok('crypt mouth walk-out crosses (action cross)', tr3 && tr3.action === 'cross');
ok('walk-out lands on C side land row (0, -596)',
   tr3 && tr3.mappedPos && tr3.mappedPos.x === 0 && tr3.mappedPos.z === -596);
ok('activeId back to regionC', logic.activeId === cid);

var fails = A.filter(function (a) { return !a.pass; });
A.forEach(function (a) { console.log((a.pass ? 'PASS  ' : 'FAIL  ') + a.label); });
console.log('---');
console.log('connection_probe: ' + (A.length - fails.length) + '/' + A.length + ' PASS');
process.exit(fails.length ? 1 : 0);
