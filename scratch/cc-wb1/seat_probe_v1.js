globalThis.window = globalThis; globalThis.self = globalThis;
const path = require('path');
const R = '/tmp/wh-worldfeat';
require(path.join(R, 'prototype/vendor/three.classic.js'));
require(path.join(R, 'prototype/js/CONFIG.js'));
require(path.join(R, 'prototype/js/wh-ground.js'));
const G = window.WH_GROUND, RID = 'hold_outskirts';
const rows = [
  ['boardA', 6.7, -14.5], ['boardB', 10.7, -14.5],
  ['boardA2', 8, -16], ['nearestNeighborGap', 6.7, -14.5],
  // reference rows: nearest props for clearance math
  ['ref_mossBoulder', 10.5, -14.5], ['ref_boulder2', 5.5, 8.5],
  ['ref_lanternPost', 4, -2]
];
let bad = 0;
for (const r of rows) {
  const y = G.heightAt(RID, r[1], r[2]);
  const deg = Math.atan(G.slopeTan(RID, r[1], r[2])) * 180 / Math.PI;
  const ok = y !== undefined && isFinite(y);
  if (!ok) bad++;
  console.log((ok?'PASS':'FAIL') + ' ' + String(r[0]).padEnd(18) + '(' + r[1] + ',' + r[2] + ') y=' + (y===undefined?'undef':y.toFixed(2)) + ' slope1m=' + (deg===undefined||!isFinite(deg)?'undef':deg.toFixed(1)+'deg'));
}
console.log(bad===0 ? 'WB1 SEAT v1: ALL ' + rows.length + ' PROBED' : 'WB1: ' + bad + ' FAIL');
