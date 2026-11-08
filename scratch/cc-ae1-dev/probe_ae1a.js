// AE1-A design probe (Devbot scratch): measure rendered-road distances for
// every 2m-arc / 14-17.5m offset seat candidate over the 4 seat roads, with
// REAL region-manager.js loaded (WH_RegionGeom = the renderer's own math).
// Also: the worst seat-to-player-on-rendered-road pair distance.
'use strict';
globalThis.window = globalThis; globalThis.self = globalThis;
const path = require('path');
const W = '/tmp/wh-worldfeat';
require(path.join(W, 'prototype/vendor/three.classic.js'));
require(path.join(W, 'prototype/js/CONFIG.js'));
require(path.join(W, 'prototype/js/wh-ground.js'));
require(path.join(W, 'prototype/js/region-manager.js'));
require(path.join(W, 'prototype/js/ambush.js'));
const CFG0 = window.WH_CONFIG;
const RG = window.WH_RegionGeom;
const RID = 'forest_of_the_old_king';
const cfg = JSON.parse(JSON.stringify(CFG0));
const R = cfg.raid;

function seats(row) {
  const segs = row.points, out = [];
  for (let i = 0; i + 1 < segs.length; i++) {
    const a = segs[i], b = segs[i + 1];
    const len = Math.hypot(b[0] - a[0], b[1] - a[1]);
    const dx = (b[0] - a[0]) / len, dz = (b[1] - a[1]) / len;
    const n = Math.ceil(len / 2);
    for (let j = 0; j <= n; j++) {
      const t = Math.min(len, j * 2);
      out.push({ x: a[0] + dx * t, z: a[1] + dz * t, px: -dz, pz: dx });
    }
  }
  const cs = [];
  for (const c of out) {
    if (!cs.length || Math.hypot(c.x - cs[cs.length - 1].x, c.z - cs[cs.length - 1].z) > 0.4) cs.push(c);
  }
  return cs;
}

// point on the RENDERED centerline near polyline sample c: scan the polyline
// normal for the RG.distToRoad minimum
function onRoadPose(row, c) {
  let bx = 0, bz = 0, bd = Infinity;
  for (let o = -12; o <= 12; o += 0.05) {
    const x = c.x + c.px * o, z = c.z + c.pz * o;
    const d = RG.distToRoad(row, x, z);
    if (d < bd) { bd = d; bx = x; bz = z; }
  }
  return { x: bx, z: bz, d: bd };
}

const report = {};
for (const row of CFG0.roads.filter(r => r.regionId === RID && r.points &&
  ['kingsRoad', 'northRoad', 'eastRoad', 'westRoad'].includes(r.id))) {
  const cs = seats(row);
  let bandOK = 0, bandViol = 0, worstSeat = 1e9, worstSeatAt = '';
  let worstPair = 1e9, worstPairAt = '';
  for (let i = 0; i < cs.length; i++) {
    const c = cs[i];
    for (const off of [14.0, 14.9, 16.0, 17.5]) for (const side of [1, -1]) {
      const x = c.x + c.px * off * side, z = c.z + c.pz * off * side;
      const rd = RG.distToRoad(row, x, z);
      if (rd >= R.seatMinRoadRenderedM) bandOK++; else bandViol++;
      if (rd < worstSeat) { worstSeat = rd; worstSeatAt = `arc${i} off${off} s${side}`; }
      const p = onRoadPose(row, c);
      const pd = Math.hypot(p.x - x, p.z - z);
      if (pd < worstPair) { worstPair = pd; worstPairAt = `arc${i} off${off} s${side}`; }
    }
  }
  report[row.id] = { samples: cs.length * 8, bandOK, bandViol,
    worstSeatRenderD: +worstSeat.toFixed(2), worstSeatAt,
    worstPairD: +worstPair.toFixed(2), worstPairAt };
}
console.log(JSON.stringify(report, null, 1));
