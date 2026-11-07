#!/usr/bin/env node
// Independent tick‑probe for CC‑H1a validation (Testerbot).

(function () {
  'use strict';
  const fs = require('fs');
  const ROOT = '/tmp/wh-worldfeat';
  const win = {};
  global.window = win;
  // Load CONFIG and expose as WH_CONFIG
  const cfg = eval(fs.readFileSync(ROOT + '/prototype/js/CONFIG.js', 'utf8') + '; window.WH_CONFIG;');
  win.WH_CONFIG = cfg;
  // Load region definitions and manager logic
  eval(fs.readFileSync(ROOT + '/prototype/js/region-defs.js', 'utf8'));
  eval(fs.readFileSync(ROOT + '/prototype/js/region-manager.js', 'utf8'));
  const DEFS = win.WH_REGION_DEFS;
  const Logic = win.WH_RegionManagerLogic;

  function check(name, ok, detail) {
    console.log((ok ? 'PASS' : 'FAIL') + '  ' + name + (detail ? '  [' + detail + ']' : ''));
    if (!ok) process.exitCode = 1;
  }

  // 1. plane check
  check('planeZ == -662', cfg.regionF.door.planeZ === -662);

  // 2. sides tables
  const c4 = DEFS.connections[4];
  const c5 = DEFS.connections[5];
  check('conn[5] C +1', c5.sides[cfg.regionC.id] === 1);
  check('conn[5] G -1', c5.sides[cfg.regionG.id] === -1);
  check('conn[4] E -1', c4.sides[cfg.regionE.id] === -1);
  check('conn[4] F +1', c4.sides[cfg.regionF.id] === 1);

  // 3. first‑tick no‑cross for each door region
  const doorRegions = ['regionD', 'regionE', 'regionF', 'regionG'];
  doorRegions.forEach(key => {
    const R = cfg[key];
    const rm = new Logic(R.id);
    const r = rm.tickTransition(R.spawn.x, R.spawn.z);
    check(key + ' spawn first‑tick no‑cross', r.action !== 'cross');
    // Find own land row if present
    let own = null;
    DEFS.connections.forEach(c => {
      if (c.door && c.door.land && c.door.land[R.id]) {
        own = c.door.land[R.id];
      }
    });
    if (own) {
      const rm2 = new Logic(R.id);
      const r2 = rm2.tickTransition(own.x, own.z);
      check(key + ' land first‑tick no‑cross', r2.action !== 'cross');
    }
  });

  // 4. walk‑back crossing checks
  function crossProbe(regionKey, x, z) {
    const rm = new Logic(cfg[regionKey].id);
    const r = rm.tickTransition(x, z);
    return r.action === 'cross' ? r.newActiveId : null;
  }
  check('D walk-back to forest', crossProbe('regionD', -150.8, -216.2) === 'forest_of_the_old_king');
  check('F walk‑back → veil_crypt', crossProbe('regionF', 0, -662.5) === 'veil_crypt');
  check('G walk‑back → forest_of_the_old_king', crossProbe('regionG', 0, -699.5) === 'forest_of_the_old_king');

  // 5. enemy roster unchanged
  const expected = JSON.stringify([
    {type:'ghoul',x:-6,z:-636},
    {type:'ghoul',x:6.5,z:-635.5}
  ]);
  check('F enemies unchanged', JSON.stringify(cfg.regionF.enemies) === expected);

  console.log('ALL CONSTRAINTS: PASS');
  process.exit(process.exitCode || 0);
})();
