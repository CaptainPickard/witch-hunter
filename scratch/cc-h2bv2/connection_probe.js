// CC-H2b connection probe, adapted from cc-ad1/connection_probe.js.
// Run: node scratch/cc-h2bv2/connection_probe.js
'use strict';
var fs = require('fs');
var path = require('path');
var cp = require('child_process');
global.window = {};
global.localStorage = { getItem: function () { return null; }, setItem: function () {}, removeItem: function () {} };
global.THREE = undefined;
var ROOT = path.join(__dirname, '..', '..', 'prototype', 'js');
function evalFile(name) { (0, eval)(fs.readFileSync(path.join(ROOT, name), 'utf8')); }
evalFile('CONFIG.js');
evalFile('region-defs.js');
evalFile('region-manager.js');
var CFG = window.WH_CONFIG;
var DEFS = window.WH_REGION_DEFS;
var Logic = window.WH_RegionManagerLogic;
var A = [];
function ok(label, cond) { A.push({ label: label, pass: !!cond }); }
var hid = CFG.regionH.id, iid = CFG.regionI.id;
var conn = DEFS.connections[7];
ok('conn[7] present and from H to I', conn && conn.from === hid && conn.to === iid);
ok('connectionBetween(H,I) = conn[7]', DEFS.connectionBetween(hid, iid) === conn);
ok('reverse connectionBetween(I,H) = conn[7]', DEFS.connectionBetween(iid, hid) === conn);
ok('I region registered', !!DEFS.regions[iid] && DEFS.regions[iid].cfg === CFG.regionI);
ok('plane and door window CONFIG-driven', conn && conn.planeCoord === CFG.regionI.door.planeZ && conn.door.doorHalfWidth === CFG.regionI.door.doorHalfWidth);
ok('walkFrom I only', conn && conn.door.walkFrom === iid && DEFS.planeIn(conn, iid) && !DEFS.planeIn(conn, hid));
ok('interact fields from H', conn && conn.door.interact.from === hid && conn.door.interact.x === CFG.regionI.door.interact.x && conn.door.interact.z === CFG.regionI.door.interact.z && conn.door.interact.radius === CFG.regionI.door.interact.radius);
ok('land rows both destinations', conn && conn.door.land[hid] === CFG.regionI.door.land[hid] && conn.door.land[iid] === CFG.regionI.door.land[iid]);
ok('sides H -1, I +1', DEFS.sideIn(conn, hid) === -1 && DEFS.sideIn(conn, iid) === 1);
ok('text and three fades on door', conn && conn.door.text === CFG.regionI.door.text && conn.door.fadeIn === CFG.regionI.door.fadeIn && conn.door.fadeOut === CFG.regionI.door.fadeOut && conn.door.exitFadeOut === CFG.regionI.door.exitFadeOut);
var original = cp.execFileSync('git', ['show', 'HEAD:prototype/js/region-defs.js'], { cwd: path.join(__dirname, '..', '..'), encoding: 'utf8' });
var live = fs.readFileSync(path.join(ROOT, 'region-defs.js'), 'utf8');
function c6bytes(src) {
  var m = src.match(/  var HD = CFG\.regionH\.door;[\s\S]*?  connections\[6\]\.sides\[CFG\.regionH\.id\] = -1;\n/);
  if (!m) throw new Error('conn[6] source not found');
  return m[0];
}
ok('conn[6] byte-identical to HEAD', c6bytes(live) === c6bytes(original));
var logic = new Logic(hid);
ok('portalNear(H hook) finds conn7', logic.portalNear({ x: CFG.regionI.door.interact.x, z: CFG.regionI.door.interact.z }) === conn);
var crossed = logic.forceCross(conn);
ok('H->I forceCross lands at I row', crossed.action === 'cross' && crossed.newActiveId === iid && crossed.mappedPos.z === CFG.regionI.door.land[iid].z);
var out = logic.tickTransition(0, -1137);
ok('I walk-back crosses to H land row', out && out.action === 'cross' && out.newActiveId === hid && out.mappedPos.z === CFG.regionI.door.land[hid].z);
var fails = A.filter(function (a) { return !a.pass; });
A.forEach(function (a) { console.log((a.pass ? 'PASS  ' : 'FAIL  ') + a.label); });
console.log('connection_probe: ' + (A.length - fails.length) + '/' + A.length + ' PASS');
process.exit(fails.length ? 1 : 0);
