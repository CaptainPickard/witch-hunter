// CC-ED1 seat probe (pre-spec, A-1 law): the mirrored east layout rows vs
// WH_GROUND terrain before IO freezes the spec. Mirror law: east rows =
// west_hollow_den rows x-flipped through the den center (mouth stays loop-side:
// west mouth faces its loop point S; east loop point lies S of the east site).
globalThis.window = globalThis; globalThis.self = globalThis;
const path = require('path');
const R = '/tmp/wh-worldfeat';
require(path.join(R, 'prototype/vendor/three.classic.js'));
require(path.join(R, 'prototype/js/CONFIG.js'));
require(path.join(R, 'prototype/js/wh-ground.js'));
const G = window.WH_GROUND;
const RID = 'forest_of_the_old_king';
const rows = [
  // 11 props (x-flip of west A-1 table)
  ['deadTree', 206, -440], ['deadTree', 213, -439], ['deadTree', 217, -440],
  ['mossBoulder', 215, -449], ['mossBoulder', 208, -452], ['mossBoulder', 217, -445],
  ['skullPile', 205, -448], ['skullPile', 203, -446],
  ['buriedCoffin', 202, -450],
  ['rubblePile', 205, -443], ['rubblePile', 202, -440],
  // 4 bonePile gather nodes (node 2 nudged rel -10.5 so G-6b is 3.5 not 3.0)
  ['bonePile', 208.5, -455], ['bonePile', 199.5, -446],
  ['bonePile', 220, -447.5], ['bonePile', 214.5, -435]
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
console.log(bad === 0 ? 'ED1 PRE-SPEC SEAT: ALL 15 PASS' : 'ED1 PRE-SPEC SEAT: ' + bad + ' FAIL');
process.exit(bad === 0 ? 0 : 1);
