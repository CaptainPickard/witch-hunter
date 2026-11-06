// val2_A17.js — Testerbot verdict-2: V-A17 re-measured under AE1-A semantics.
// The addendum (valspec §9) supersedes the raw-band law: V-A17's band now wears
// the RENDERED-road floor (WH_RegionGeom.distToRoad >= seatMinRoadRenderedM for
// every ok seat from its claimed road) measured over the probe grid
// (4 m x offsets 14/14.9/16/17.5 x both sides x >=100 seeded poses per road).
// Raw-band counts are still COLLECTED (disclosed evidence: the raw band itself
// violates the rendered floor — that is the flaw AE1-A fixes), but the verdict
// predicate is the rendered floor + road-row exclusion + road-seek.
'use strict';
const L = require('./lib.js');
const path = L.path, ROOT = L.ROOT, CFG = L.CFG, RID = L.RID, G = L.G;
const R = CFG.raid;

require(path.join(ROOT, 'prototype/js/region-manager.js'));  // real renderer math
require(path.join(ROOT, 'prototype/js/ambush.js'));
const RG = window.WH_RegionGeom;
const A = window.WH_AMBUSH;

const SEED = 20261;
const OFFSETS = [14.0, 14.9, 16.0, 17.5];
const STEP = 4;
const POSES_PER_ROAD = 100;

const seatRoads = CFG.roads.filter(r => r.regionId === R.regionId &&
  ['kingsRoad', 'northRoad', 'eastRoad', 'westRoad'].includes(r.id) && r.points);
const BRANCH_TERMINALS = { northRoad: { x: 0, z: -596 }, eastRoad: { x: 240, z: -366 }, westRoad: { x: -240, z: -366 } };

function centerSamples(row) {
  const pts = row.points, out = [];
  for (let i = 0; i + 1 < pts.length; i++) {
    const a = pts[i], b = pts[i + 1];
    const len = Math.hypot(b[0] - a[0], b[1] - a[1]);
    const dx = (b[0] - a[0]) / len, dz = (b[1] - a[1]) / len;
    const px = -dz, pz = dx;
    const n = Math.ceil(len / STEP);
    for (let j = 0; j <= n; j++) {
      const t = Math.min(len, j * STEP);
      out.push({ x: a[0] + dx * t, z: a[1] + dz * t, px: px, pz: pz });
    }
  }
  out.sort((p, q) => (p.x - q.x) || (p.z - q.z));
  const cs = [];
  for (const c of out) {
    if (!cs.length || Math.hypot(c.x - cs[cs.length - 1].x, c.z - cs[cs.length - 1].z) > 0.4) cs.push(c);
  }
  return cs;
}

function seatPredicates(x, z) {
  const slope = G.slopeTan(RID, x, z);
  if (!(slope <= R.seatMaxSlopeTan)) return 'slope';
  const props = CFG.regionC.props.filter(p => typeof p.x === 'number');
  for (const p of props) if (Math.hypot(p.x - x, p.z - z) < R.seatMinPropM) return 'prop';
  const fires = CFG.regionC.props.filter(p => p.asset === 'banditCampfire');
  for (const f of fires) if (Math.hypot(f.x - x, f.z - z) < R.nearFireExclusionM) return 'fire';
  if (Math.hypot(0 - x, -366 - z) < R.stoneRingExclusionR) return 'stone';
  return null;
}
function notchExcluded(x, z) {
  for (const k of Object.keys(BRANCH_TERMINALS)) {
    const t = BRANCH_TERMINALS[k];
    if (Math.hypot(t.x - x, t.z - z) < R.notchMouthExclusionM) return k;
  }
  return null;
}
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const enemyLog = [];
const restoreEnemy = L.installEnemyStub(enemyLog);
const SAVED_RANDOM = L.SAVED_RANDOM;

function measureRoads() {
  const out = {};
  for (const rd of seatRoads) {
    const cs = centerSamples(rd);
    const rnd = mulberry32(SEED + rd.id.length * 7919 + rd.points.length);
    const poses = [];
    for (let i = 0; i < POSES_PER_ROAD; i++) {
      const c = cs[Math.floor(rnd() * cs.length)];
      const jitterAlong = (rnd() * 2 - 1) * (R.roadSeekRadiusM / 2);
      const jitterLat = (rnd() * 2 - 1) * 8;
      const px = c.x + c.pz * jitterLat;
      const pz = c.z + c.px * jitterLat;
      const pts = rd.points;
      const segIdx = Math.min(pts.length - 2, Math.max(0, Math.floor((c.x + c.z) % Math.max(1, pts.length - 1))));
      const a = pts[segIdx], b = pts[segIdx + 1];
      const len = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
      const dx = (b[0] - a[0]) / len, dz = (b[1] - a[1]) / len;
      poses.push({ x: px + dx * jitterAlong, z: pz + dz * jitterAlong, yaw: rnd() * Math.PI * 2 });
    }
    let ok = 0, fail = 0, mouth = 0, bandViolRaw = 0, renderFloorViol = 0, roadRowViol = 0, seekFail = 0;
    let maxRun = 0, run = 0, worstRender = Infinity, worstRawOff = -Infinity;
    const violations = [];
    for (const pose of poses) {
      Math.random = mulberry32(SEED + Math.round(pose.x * 3.1 + pose.z * 5.7) % 100000);
      const game = L.mockGame(pose.x, pose.z, pose.yaw);
      A.init(game);
      let r;
      try { r = A.pickRaidSeat(); } finally { Math.random = SAVED_RANDOM; }
      if (!r.ok) {
        if (r.why === 'no-road') seekFail++;
        else { fail++; run++; maxRun = Math.max(maxRun, run); }
        continue;
      }
      run = 0;
      const claimedRoad = seatRoads.find(row => row.id === r.roadId);
      if (!claimedRoad) { roadRowViol++; continue; }
      // RAW band (disclosed; no longer the verdict predicate)
      const off = L.distToCenterline(L.polyGeom(claimedRoad), r.x, r.z);
      const inBand = off >= R.spawnBandM[0] - 1e-6 && off <= R.spawnBandM[1] + 1e-6;
      if (!inBand) bandViolRaw++;
      if (off > worstRawOff) worstRawOff = off;
      // RENDERED floor (the AE1-A verdict predicate)
      const rd = RG.distToRoad(claimedRoad, r.x, r.z);
      if (rd < R.seatMinRoadRenderedM) {
        renderFloorViol++;
        if (rd < worstRender) worstRender = rd;
        if (violations.length < 6) violations.push(r.roadId + ' seat(' + r.x.toFixed(1) + ',' + r.z.toFixed(1) + ') renderD ' + rd.toFixed(2) + ' slide ' + r.slide);
      }
      if (rd >= R.seatMinRoadRenderedM) {
        const why = seatPredicates(r.x, r.z);
        const mouthRow = notchExcluded(r.x, r.z);
        if (why === null && mouthRow === null) ok++;
        else if (mouthRow !== null) mouth++;
        else { fail++; run++; maxRun = Math.max(maxRun, run); }
      }
    }
    const elig = ok + fail;
    out[rd.id] = { poses: poses.length, eligible: elig, ok: ok, fail: fail, mouth: mouth,
      passPct: +((100 * ok / (elig || 1)).toFixed(1)), maxRun: maxRun, seekFail: seekFail,
      bandViolRaw: bandViolRaw, renderFloorViol: renderFloorViol, roadRowViol: roadRowViol,
      worstRender: worstRender === Infinity ? null : +worstRender.toFixed(2),
      violations: violations };
  }
  return out;
}

const m = measureRoads();
restoreEnemy();

let bandViol = 0, roadViol = 0, seekFails = 0, poses = 0;
const perRoad = [];
for (const k of Object.keys(m)) {
  bandViol += m[k].renderFloorViol; roadViol += m[k].roadRowViol; seekFails += m[k].seekFail; poses += m[k].poses;
  perRoad.push(k + ' renderFloorViol=' + m[k].renderFloorViol + ' bandViolRaw=' + m[k].bandViolRaw +
    ' seekFail=' + m[k].seekFail + ' passPct=' + m[k].passPct + ' maxRun=' + m[k].maxRun);
}
const v = bandViol === 0 && roadViol === 0;

process.stdout.write(JSON.stringify({
  case: 'V-A17-v2 (AE1-A semantics)',
  verdict: v ? 'PASS' : 'FAIL',
  perRoad: m,
  summary: { poses: poses, renderFloorViol: bandViol, roadRowViol: roadViol, seekFails: seekFails, perRoadLine: perRoad.join(' ; ') }
}, null, 1));
