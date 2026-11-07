#!/usr/bin/env node
// CC-H1a post-fix sides/door-law verifier (executable valspec body).
// Asserts on the LANDED files after the CC-H1a fix:
//   1. CFG.regionF.door.planeZ == -662 (south-rim mouth grammar).
//   2. conn[5] sides: C +1 / G -1; conn[4] sides: E -1 / F +1 (law-correct
//      for planes -700 / -662 respectively).
//   3. Per-conn pocket law: sideIn(pocket) == sideOfPlane(pocket's spawn z).
//   4. First-tick probes (REAL RegionManagerLogic): NO cross at any pocket's
//      spawn or own land row (D, E, F, G).
//   5. Walk-back: exit probes at each mouth cross to the parent (D at the
//      outcrop lane, F at plane -662 lane, G at the gate lane).
//   6. F enemy roster unchanged: exactly the two landed ghoul rows.
// Exit 0 only if every assert passes.
(function () {
  'use strict';
  var fs = require('fs');
  var ROOT = '/tmp/wh-worldfeat';
  var windowShim = {};
  global.window = windowShim;
  var cfg = eval(fs.readFileSync(ROOT + '/prototype/js/CONFIG.js', 'utf8') + '; window.WH_CONFIG;');
  windowShim.WH_CONFIG = cfg;
  eval(fs.readFileSync(ROOT + '/prototype/js/region-defs.js', 'utf8'));
  eval(fs.readFileSync(ROOT + '/prototype/js/region-manager.js', 'utf8'));
  var DEFS = windowShim.WH_REGION_DEFS;
  var Logic = windowShim.WH_RegionManagerLogic;
  cfg.boundary = cfg.boundary || { minX: -9999, maxX: 9999, minZ: -9999, maxZ: 9999 };
  cfg.chokepoint = cfg.chokepoint || { centerX: 0, halfWidth: 9999 };
  cfg.preWarm = cfg.preWarm || { distance: 22, hysteresis: 8 };

  var fails = 0;
  function check(name, ok, detail) {
    console.log((ok ? 'PASS' : 'FAIL') + '  ' + name + (detail ? '  [' + detail + ']' : ''));
    if (!ok) fails++;
  }

  // 1. F plane seat
  check('EDIT-1: regionF.door.planeZ == -662', cfg.regionF.door.planeZ === -662,
    'got ' + cfg.regionF.door.planeZ);

  // 2. sides tables
  var c4 = DEFS.connections[4], c5 = DEFS.connections[5];
  check('EDIT-2/conn[5]: sides C=+1', c5.sides.forest_of_the_old_king === 1);
  check('EDIT-2/conn[5]: sides G=-1', c5.sides.lords_hold === -1);
  check('EDIT-3(no-op)/conn[4]: sides E=-1', c4.sides.veil_crypt === -1);
  check('EDIT-3(no-op)/conn[4]: sides F=+1', c4.sides.veil_galleries === 1);
  check('conn[4]: planeCoord == F door planeZ (-662)', c4.planeCoord === cfg.regionF.door.planeZ);
  check('conn[5]: planeCoord == G door planeZ (-700)', c5.planeCoord === cfg.regionG.door.planeZ);

  // 3. pocket sides law on door conns
  var pairs = [
    ['regionD', 2], ['regionE', 3], ['regionF', 4], ['regionG', 5]
  ];
  pairs.forEach(function (p) {
    var key = p[0], idx = p[1];
    var c = DEFS.connections[idx];
    var R = cfg[key];
    var pf = function (z) { return z > c.planeCoord ? 1 : -1; };
    check('conn[' + idx + ']: sideIn(' + R.id + ') == sideOfPlane(spawn ' + R.spawn.z + ')',
      c.sides[R.id] === pf(R.spawn.z), 'sideIn=' + c.sides[R.id]);
    var own = c.door.land && c.door.land[R.id];
    if (own) check('conn[' + idx + ']: sideIn(' + R.id + ') == sideOfPlane(own land ' + own.z + ')',
      c.sides[R.id] === pf(own.z));
  });

  // 4. first-tick probes
  pairs.forEach(function (p) {
    var key = p[0];
    var R = cfg[key];
    var rm = new Logic(R.id);
    var r = rm.tickTransition(R.spawn.x, R.spawn.z);
    check(key + ' spawn first-tick no cross', r.action !== 'cross', 'action=' + r.action);
    var own = null;
    DEFS.connections.forEach(function (c) { if (c.door && c.door.land && c.door.land[R.id]) own = c.door.land[R.id]; });
    if (own) {
      var rm2 = new Logic(R.id);
      var r2 = rm2.tickTransition(own.x, own.z);
      check(key + ' land-row first-tick no cross', r2.action !== 'cross', 'action=' + r2.action);
    }
  });

  // 5. walk-back probes at the mouths
  function crossProbe(key, x, z) {
    var rm = new Logic(cfg[key].id);
    var r = rm.tickTransition(x, z);
    return r.action === 'cross' ? r.newActiveId : null;
  }
  check('D walk-back (outcrop lane) -> forest', crossProbe('regionD', -150.8, -216) === 'forest_of_the_old_king');
  check('F walk-back (south mouth lane) -> veil_crypt', crossProbe('regionF', 0, -662.5) === 'veil_crypt');
  check('G walk-back (gate lane) -> forest', crossProbe('regionG', 0, -699.5) === 'forest_of_the_old_king');

  // 6. F enemy roster unchanged
  check('A-4: F enemies unchanged (2 ghoul rows landed seats)',
    JSON.stringify(cfg.regionF.enemies) === JSON.stringify([
      { type: 'ghoul', x: -6, z: -636 }, { type: 'ghoul', x: 6.5, z: -635.5 }]),
    JSON.stringify(cfg.regionF.enemies));

  console.log(fails === 0 ? 'ALL CONSTRAINTS: PASS' : 'FAILURES: ' + fails);
  process.exit(fails === 0 ? 0 : 1);
})();
