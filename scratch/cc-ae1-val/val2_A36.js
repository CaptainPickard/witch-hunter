// val2_A36.js — Testerbot verdict-2, case V-A36 (AE1-A player floor, targeted).
// 443-pose grid: every 2 m arc of all 4 seat roads projected onto the RENDERED
// centerline (real WH_RegionGeom.distToRoad from the current region-manager.js).
// Every ok seat from pickRaidSeat must satisfy straight-line
// hypot(seat - pose) >= CFG.raid.minPlayerDistM. Violations counted: 0.
// Authored fresh by Testerbot for verdict 2 against valspec §9. Node-only.
'use strict';
const L = require('./lib.js');
const path = L.path, ROOT = L.ROOT, CFG = L.CFG;
const R = CFG.raid;

require(path.join(ROOT, 'prototype/js/region-manager.js'));  // real renderer math
require(path.join(ROOT, 'prototype/js/ambush.js'));
const RG = window.WH_RegionGeom;

const FAILS = [];
function assert(v, msg) { if (!v) FAILS.push(msg); return v; }
const haveRG = assert(!!RG && typeof RG.distToRoad === 'function',
  'WH_RegionGeom.distToRoad live (current region-manager.js)');

const roadRows = CFG.roads.filter(r => r.regionId === R.regionId &&
  ['kingsRoad', 'northRoad', 'eastRoad', 'westRoad'].includes(r.id) && r.points);

// 2 m arc walk per seat road (validator's own math)
function arcSamples(row) {
  const out = [];
  for (let i = 0; i + 1 < row.points.length; i++) {
    const a = row.points[i], b = row.points[i + 1];
    const len = Math.hypot(b[0] - a[0], b[1] - a[1]);
    const dx = (b[0] - a[0]) / len, dz = (b[1] - a[1]) / len;
    const n = Math.max(1, Math.ceil(len / 2));
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

// project the polyline sample onto the RENDERED centerline: scan the polyline
// normal for the distToRoad minimum (the sway displacement)
function onRoadPose(row, c) {
  let bx = c.x, bz = c.z, bd = Infinity;
  for (let o = -12; o <= 12; o += 0.05) {
    const x = c.x + c.px * o, z = c.z + c.pz * o;
    const d = RG.distToRoad(row, x, z);
    if (d < bd) { bd = d; bx = x; bz = z; }
  }
  return { x: bx, z: bz, d: bd };
}

const enemyLog = [];
const restoreEnemy = L.installEnemyStub(enemyLog);
const SAVED_RANDOM = L.SAVED_RANDOM;
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

if (haveRG) {
  // ---- the 443-pose grid ---------------------------------------------------
  const poses = [];
  const perRoadCount = {};
  for (const row of roadRows) {
    const cs = arcSamples(row);
    let n = 0;
    for (const c of cs) {
      const pOn = onRoadPose(row, c);
      if (pOn.d <= 1.0) { poses.push({ x: pOn.x, z: pOn.z, roadId: row.id }); n++; }
    }
    perRoadCount[row.id] = n;
  }
  assert(poses.length === 126 + 103 + 107 + 107,
    'on-road pose grid == 443 (all 2 m arcs of the 4 seat roads, sway projection): got ' +
    poses.length + ' (' + JSON.stringify(perRoadCount) + ')');
  assert(poses.length > 400, 'pose grid covers every 2 m arc: ' + poses.length);

  // ---- every ok seat >= minPlayerDistM straight-line from the driving pose --
  let picked = 0, viol = 0;
  const notes = [];
  for (const po of poses) {
    const seed = 84000 + Math.abs(Math.round(po.x * 7 + po.z * 13)) % 100000;
    Math.random = mulberry32(seed);
    let s;
    try {
      const g = L.mockGame(po.x, po.z, 0);
      window.WH_AMBUSH.init(g);
      s = window.WH_AMBUSH.pickRaidSeat();
    } finally { Math.random = SAVED_RANDOM; }
    if (!s.ok) continue;
    picked++;
    const pd = Math.hypot(s.x - po.x, s.z - po.z);
    if (pd < R.minPlayerDistM) {
      viol++;
      if (notes.length < 6) notes.push(po.roadId + ' pose(' + po.x.toFixed(1) + ',' + po.z.toFixed(1) +
        ') => seat ' + pd.toFixed(2) + ' m < ' + R.minPlayerDistM);
    }
  }
  assert(picked > 200, 'ok seats collected: ' + picked);
  assert(viol === 0, 'EVERY picked seat >= CFG.raid.minPlayerDistM (' + R.minPlayerDistM +
    ') straight-line from its driving pose' + (notes.length ? ' :: ' + notes.join(' | ') : ''));

  restoreEnemy();
  process.stdout.write(JSON.stringify({
    case: 'V-A36',
    poseGrid: { total: poses.length, perRoad: perRoadCount },
    sweep: { picked: picked, violations: viol, minPlayerDistM: R.minPlayerDistM },
    notes: notes,
    fails: FAILS,
    result: FAILS.length === 0 ? 'PASS' : 'FAIL'
  }, null, 1));
} else {
  process.stdout.write(JSON.stringify({ case: 'V-A36', result: 'FAIL', fails: FAILS }));
  process.exit(1);
}
