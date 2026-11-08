// CC-WM1 seat probe v2 (A-1 law, amended tables): moved seats + all 8 veins vs
// WH_GROUND terrain. globalThis shim + CONFIG + wh-ground, heightAt + slopeTan.
globalThis.window = globalThis; globalThis.self = globalThis;
const path = require('path');
const R = '/tmp/wh-worldfeat';
require(path.join(R, 'prototype/vendor/three.classic.js'));
require(path.join(R, 'prototype/js/CONFIG.js'));
require(path.join(R, 'prototype/js/wh-ground.js'));
const G = window.WH_GROUND;
const RID = 'forest_of_the_old_king';
const rows = [
  // 8 ironVein seats (amended: vein5 = 63.5,-582)
  ['ironVein', 53, -577], ['ironVein', 55.5, -573.5], ['ironVein', 61, -572], ['ironVein', 64, -575.5],
  ['ironVein', 63.5, -582], ['ironVein', 57, -584], ['ironVein', 51.5, -581.5], ['ironVein', 50, -574],
  // moved props: 3 rubblePile + deadTree leaner W
  ['rubblePile', 55, -584.5], ['rubblePile', 52, -572.5], ['rubblePile', 62, -577], ['deadTree', 47, -585],
];
let bad = 0;
console.log('WH_GROUND.has(' + RID + ') =', G.has(RID));
for (const r of rows) {
  const y = G.heightAt(RID, r[1], r[2]);
  const deg = Math.atan(G.slopeTan(RID, r[1], r[2])) * 180 / Math.PI;
  const ok = Math.abs(y) <= 26 && deg <= 31;
  if (!ok) bad++;
  console.log((ok ? 'PASS' : 'FAIL') + ' ' + String(r[0]).padEnd(11) +
    ' (' + r[1] + ',' + r[2] + ') y=' + y.toFixed(2) + ' slope1m=' + deg.toFixed(1) + 'deg');
}
console.log(bad === 0 ? 'WM1 SEAT v2: ALL ' + rows.length + ' PASS' : 'WM1 SEAT v2: ' + bad + ' FAIL');
process.exit(bad === 0 ? 0 : 1);
