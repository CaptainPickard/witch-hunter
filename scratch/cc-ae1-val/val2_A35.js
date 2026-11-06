// val2_A35.js — Testerbot verdict-2, case V-A35 (AE1-A rendered-road floor).
// REAL renderer math: requires the CURRENT worktree region-manager.js so
// window.WH_RegionGeom.distToRoad is whRoadLine's Catmull-Rom + sway geometry
// (NOT a re-implementation). Authored fresh by Testerbot for verdict 2
// against valspec §9 (binding). Node-only; public WH_AMBUSH surface only.
'use strict';
const L = require('./lib.js');
const fs = L.fs, path = L.path, ROOT = L.ROOT, CFG = L.CFG;
const R = CFG.raid;

// Load the current worktree region-manager.js AFTER CONFIG (real helper),
// then ambush.js (lazy-reads window.WH_RegionGeom inside seatWhy).
require(path.join(ROOT, 'prototype/js/region-manager.js'));
require(path.join(ROOT, 'prototype/js/ambush.js'));
const RG = window.WH_RegionGeom;

const FAILS = [];
function assert(v, msg) { if (!v) FAILS.push(msg); return v; }

if (!assert(!!RG && typeof RG.distToRoad === 'function',
  'WH_RegionGeom.distToRoad live from current region-manager.js')) {
  process.stdout.write(JSON.stringify({ case: 'V-A35', result: 'FAIL', fails: FAILS }));
  process.exit(1);
}

// 2 m arc walk per seat road (validator's own math).
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

// Point ON the RENDERED centerline near polyline sample c: scan along the
// polyline normal for the distToRoad minimum (the sway displacement).
function onRoadPose(row, c) {
  let bx = c.x, bz = c.z, bd = Infinity;
  for (let o = -12; o <= 12; o += 0.05) {
    const x = c.x + c.px * o, z = c.z + c.pz * o;
    const d = RG.distToRoad(row, x, z);
    if (d < bd) { bd = d; bx = x; bz = z; }
  }
  return { x: bx, z: bz, d: bd };
}

const roadRows = CFG.roads.filter(r => r.regionId === R.regionId &&
  ['kingsRoad', 'northRoad', 'eastRoad', 'westRoad'].includes(r.id) && r.points);

// record-only enemy stub (spawn grammar safety; pickRaidSeat never constructs)
const enemyLog = [];
const restoreEnemy = L.installEnemyStub(enemyLog);

// drive pickRaidSeat with a fresh mock game; mulberry32 seeded per pose,
// restored in-finally (valspec §0 seeded-determinism law)
const SAVED_RANDOM = L.SAVED_RANDOM;
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function drive(pose, seed) {
  const g = L.mockGame(pose.x, pose.z, pose.yaw === undefined ? 0 : pose.yaw);
  window.WH_AMBUSH.init(g);
  const r = window.WH_AMBUSH.pickRaidSeat();
  return r;
}
// seeded drive: init under seed, pick under the SAME seed stream (deterministic)
function driveSeeded(pose, seed) {
  Math.random = mulberry32(seed);
  try { return drive(pose, seed); }
  finally { Math.random = SAVED_RANDOM; }
}

// ---- assertion (1): the raw flaw still reproduces WITHOUT the gates --------
// band grid: every 2 m arc x offsets 14/14.9/16/17.5 x both sides; player
// ON the rendered road at the sway displacement (full bulge included).
let totalSeats = 0, renderFloorViol = 0;
let worstRender = Infinity, worstRow = '';
const perRowRaw = {};
for (const row of roadRows) {
  const cs = arcSamples(row);
  let worstThis = Infinity, violThis = 0;
  for (const c of cs) {
    const pOn = onRoadPose(row, c);            // player ON the rendered road
    for (const off of [14.0, 14.9, 16.0, 17.5]) {
      for (const side of [1, -1]) {
        const x = c.x + c.px * off * side, z = c.z + c.pz * off * side;
        totalSeats++;
        const rd = RG.distToRoad(row, x, z);   // REAL renderer distance
        if (rd < R.seatMinRoadRenderedM) {
          renderFloorViol++; violThis++;
          if (rd < worstThis) worstThis = rd;
          if (rd < worstRender) { worstRender = rd; worstRow = row.id; }
        }
      }
    }
  }
  perRowRaw[row.id] = { worstRender: +worstThis.toFixed(2), viol: violThis };
}
const worstFamRender = +worstRender.toFixed(2);
assert(totalSeats > 3000, 'raw band grid size ' + totalSeats + ' > 3000');
assert(worstFamRender < R.seatMinRoadRenderedM,
  'raw flaw reproduces: worst raw-band renderD ' + worstFamRender + ' on ' +
  worstRow + ' < seatMinRoadRenderedM ' + R.seatMinRoadRenderedM);
assert(renderFloorViol > 0, 'raw-band render-floor violations = ' + renderFloorViol);

// ---- assertion (2): every ok seat from pickRaidSeat clears both floors -----
// poses ON the rendered road across all 4 seat roads, 2 m arcs, sway bulges
// included; verdict-1 worst family (k=28, mag~6.5) inside this sweep.
let picked = 0, seatFloorViol = 0, seatPairViol = 0, slidToCompliance = 0;
const seatNotes = [];
for (const row of roadRows) {
  const cs = arcSamples(row);
  for (let ci = 26; ci < cs.length; ci++) {          // k=28 family included
    const c = cs[ci];
    const pOn = onRoadPose(row, c);
    if (pOn.d > 1.0) continue;                        // want poses ON rendered road
    const r = driveSeeded(pOn, 72000 + ci);
    if (!r.ok) continue;                              // refused seats carry no law
    picked++;
    const claimed = roadRows.find(rr => rr.id === r.roadId);
    const rd = RG.distToRoad(claimed, r.x, r.z);      // REAL renderer distance
    if (rd < R.seatMinRoadRenderedM) {
      seatFloorViol++;
      if (seatNotes.length < 6) seatNotes.push(row.id + ' pose(' + pOn.x.toFixed(1) + ',' + pOn.z.toFixed(1) +
        ') => seat(' + r.x.toFixed(1) + ',' + r.z.toFixed(1) + ') renderD ' + rd.toFixed(2) + ' slide ' + r.slide);
    }
    const pd = Math.hypot(r.x - pOn.x, r.z - pOn.z);
    if (pd < R.minPlayerDistM) seatPairViol++;
    if (r.slide > 0 && rd >= R.seatMinRoadRenderedM && pd >= R.minPlayerDistM) slidToCompliance++;
  }
}
assert(picked > 200, 'ok seats collected from on-road poses: ' + picked);
assert(seatFloorViol === 0, 'every picked seat >= seatMinRoadRenderedM (' +
  R.seatMinRoadRenderedM + ') from its claimed road' +
  (seatNotes.length ? ' :: ' + seatNotes.join(' | ') : ''));
assert(seatPairViol === 0, 'every picked seat >= minPlayerDistM (' +
  R.minPlayerDistM + ') straight-line from the driving pose');
assert(slidToCompliance > 0, 'slide law remediated raw-band violations: ' +
  slidToCompliance + ' picks slid to compliance');

restoreEnemy();

process.stdout.write(JSON.stringify({
  case: 'V-A35',
  rawGrid: { totalSeats: totalSeats, renderFloorViol: renderFloorViol, worstFamRender: worstFamRender, worstRow: worstRow, perRow: perRowRaw },
  fixSweep: { picked: picked, seatFloorViol: seatFloorViol, seatPairViol: seatPairViol, slidToCompliance: slidToCompliance },
  floors: { seatMinRoadRenderedM: R.seatMinRoadRenderedM, minPlayerDistM: R.minPlayerDistM },
  fails: FAILS,
  result: FAILS.length === 0 ? 'PASS' : 'FAIL'
}, null, 1));
