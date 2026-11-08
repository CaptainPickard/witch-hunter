// CC-WD1 seat probe (valspec V-9 law): per new row, WH_GROUND.heightAt and
// slopeTan (0.5 m central differences = the 1 m span G-8 names) on the AMENDED
// den site (spec Amendment A-1, hollow center (-194,-451)); replaces the stale
// (-255,-410) probe from before the site move. scratch/cc-c5/loops_probe.js
// pattern: globalThis.window, vendor three.classic, CONFIG.js, wh-ground.js
// (CORE THREE-free run: no browser, no harness). Exit 0 iff every row in
// |y| <= 26 m (heightfield hMax ceiling) and slope1m <= 31 deg (C4b
// cliff-guard convention).
globalThis.window = globalThis; globalThis.self = globalThis;
const path = require('path');
const R = process.argv[2] || process.cwd();
require(path.join(R, 'prototype/vendor/three.classic.js'));
require(path.join(R, 'prototype/js/CONFIG.js'));
require(path.join(R, 'prototype/js/wh-ground.js'));
const G = window.WH_GROUND;
const RID = 'forest_of_the_old_king';
const rows = [
  // 8 props (spec A-1 final table; rotY/scale not seat-relevant)
  ['deadTree', -190, -446], ['deadTree', -197, -445], ['deadTree', -201, -445],
  ['mossBoulder', -199, -455], ['mossBoulder', -196, -458], ['mossBoulder', -201, -451],
  ['skullPile', -189, -454], ['skullPile', -187, -452], ['buriedCoffin', -186, -456],
  ['rubblePile', -189, -449], ['rubblePile', -186, -446],
  // 4 bonePile gather nodes (regionC.nodes, first C gather nodes)
  ['bonePile', -192.5, -461], ['bonePile', -184, -450],
  ['bonePile', -204, -453.5], ['bonePile', -198.5, -441]
];
let bad = 0;
console.log('WH_GROUND.has(' + RID + ') =', G.has(RID));
for (const r of rows) {
  const y = G.heightAt(RID, r[1], r[2]);
  const deg = Math.atan(G.slopeTan(RID, r[1], r[2])) * 180 / Math.PI;
  const ok = Math.abs(y) <= 26 && deg <= 31;
  if (!ok) bad++;
  console.log((ok ? 'PASS' : 'FAIL') + ' ' + String(r[0]).padEnd(13) +
    ' (' + r[1] + ',' + r[2] + ') y=' + y.toFixed(2) + ' slope1m=' + deg.toFixed(1) + 'deg');
}
console.log(bad === 0 ? 'G-8 SEAT: ALL 15 PASS' : 'G-8 SEAT: ' + bad + ' FAIL');
process.exit(bad === 0 ? 0 : 1);
