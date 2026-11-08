// CC-C5 offline: derive the 12 wolf spawn rows from enemy.js packSlot (lead
// at arc 0, rank = waypointPhase) + pack spread / anchor math. Node only.
globalThis.window = globalThis; globalThis.self = globalThis;
const path = require('path'); const R = process.argv[2];
require(path.join(R, 'prototype/vendor/three.classic.js'));
require(path.join(R, 'prototype/js/CONFIG.js'));
require(path.join(R, 'prototype/js/wh-ground.js'));
require(path.join(R, 'prototype/js/enemy.js'));
const C = window.WH_CONFIG.enemy, PG = window.WH_Enemy.packGeometry, P = C.wolf.pack;
const RID = 'forest_of_the_old_king', G = window.WH_GROUND;
const r1 = v => Math.round(v * 10) / 10;
for (const def of C.wolfPacks) {
  const loop = PG.makeLoop(def.waypoints), rows = [];
  for (let k = 0; k < def.members; k++) {
    const s = PG.packSlot(loop, 0, k, P);
    rows.push({ x: r1(s.x), z: r1(s.z), k });
  }
  const cx = rows.reduce((a, r) => a + r.x, 0) / rows.length, cz = rows.reduce((a, r) => a + r.z, 0) / rows.length;
  const spread = Math.max(...rows.map(r => Math.hypot(r.x - cx, r.z - cz)));
  const s0 = PG.loopProject(loop, cx, cz) + (rows.length - 1) / 2 * P.slotSpacingM;
  console.log('// ' + def.id + ' loop ' + loop.total.toFixed(1) + ' m, spawn spread max ' + spread.toFixed(2) +
    ' m from centroid, build lead s ' + (s0 % loop.total).toFixed(2));
  rows.forEach(r => console.log("      { type: 'wolf', x: " + r.x.toFixed(1) + ', z: ' + r.z.toFixed(1) +
    ", packId: '" + def.id + "', waypointPhase: " + r.k + ' },   // h ' + G.heightAt(RID, r.x, r.z).toFixed(2)));
}
// straight-segment steady-state spread of 4 slots: offsets 0,-6,-12,-18 along, lateral 0,+2,-2,+2
const pts = [0, 1, 2, 3].map(k => [-k * P.slotSpacingM, k === 0 ? 0 : (k % 2 ? 1 : -1) * P.slotLateralM]);
const mx = pts.reduce((a, p) => a + p[0], 0) / 4, my = pts.reduce((a, p) => a + p[1], 0) / 4;
console.log('straight-line slot spread: max dist to centroid', Math.max(...pts.map(p => Math.hypot(p[0] - mx, p[1] - my))).toFixed(2),
  'vs regroupRadius', P.regroupRadius, 'leashFromCentroid', P.leashFromCentroid);
console.log('night sight', C.wolf.sightRadius, 'x', C.wolf.nightBoldnessMult, '=', C.wolf.sightRadius * C.wolf.nightBoldnessMult,
  '(chase at 0.8x:', C.wolf.sightRadius * 0.8, '->', C.wolf.sightRadius * C.wolf.nightBoldnessMult * 0.8, ')');
