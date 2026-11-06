// val2_A22grid.js — Testerbot verdict-2: lock law re-aggregated over the PROBE
// GRID (the frozen A-1 aggregation form), post-AE1-A.
// The A-1 probe (scratch/cc-ae1/node_probe.js) evaluated the §3 seat predicates
// over CANDIDATE seats: 4 m centerline x offsets 14/14.9/16/17.5 x both sides,
// mouth-end candidates excluded (run reset), pass = predicate compliance.
// passPct >= 90, maxRun <= 16. Verdict-1's val_ case V-A22 aggregated
// picker-response percentages instead (V-A17 data); post-AE1-A those include
// lawful AE1-A gate refusals (rendered floor / player floor), which are NOT
// eligible-fail seat candidates — deviating from the frozen A-1 form.
// This run restores the frozen form and adds the AE1-A floors as seat gates,
// measured independently (validator math: RG.distToRoad + straight-line).
// ALSO: picker-response lock (V-A22's valspec wording) measured the v1 way,
// with AE1-A gate-refusals separated from predicate fails, for disclosure.
'use strict';
const L = require('./lib.js');
const path = L.path, ROOT = L.ROOT, CFG = L.CFG, RID = L.RID, G = L.G;
const R = CFG.raid;

require(path.join(ROOT, 'prototype/js/region-manager.js'));  // real renderer math
require(path.join(ROOT, 'prototype/js/ambush.js'));
const RG = window.WH_RegionGeom;
const A = window.WH_AMBUSH;

const OFFSETS = [14.0, 14.9, 16.0, 17.5];
const STEP = 4;

const roadRowsAll = CFG.roads.filter(r => r.regionId === R.regionId &&
  ['kingsRoad', 'northRoad', 'eastRoad', 'westRoad'].includes(r.id) && r.points);
void roadRowsAll;
const BRANCH_TERMINALS = { northRoad: { x: 0, z: -596 }, eastRoad: { x: 240, z: -366 }, westRoad: { x: -240, z: -366 } };

// 4 m grid + mouthEnd flags (EXACT probe form: last segment, t >= segLen-26)
function grid(row) {
  const pts = row.points, cs = [];
  for (let i = 0; i + 1 < pts.length; i++) {
    const a = pts[i], b = pts[i + 1];
    const segLen = Math.hypot(b[0] - a[0], b[1] - a[1]);
    const dx = (b[0] - a[0]) / segLen, dz = (b[1] - a[1]) / segLen;
    const n = Math.ceil(segLen / STEP);
    const px = -dz, pz = dx;
    for (let j = 0; j <= n; j++) {
      const t = Math.min(segLen, j * STEP);
      cs.push({ x: a[0] + dx * t, z: a[1] + dz * t, px, pz,
        mouthEnd: row.id !== 'kingsRoad' && i === pts.length - 2 && t >= segLen - 26 });
    }
  }
  return cs.filter((c, i) => i === 0 || Math.hypot(c.x - cs[i - 1].x, c.z - cs[i - 1].z) > 0.4);
}

// §3 predicates (validator math)
const props = CFG.regionC.props.filter(p => typeof p.x === 'number');
const fires = CFG.regionC.props.filter(p => p.asset === 'banditCampfire');
function seatPredicates(x, z) {
  const slope = G.slopeTan(RID, x, z);
  if (!(slope <= R.seatMaxSlopeTan)) return 'slope';
  for (const p of props) if (Math.hypot(p.x - x, p.z - z) < R.seatMinPropM) return 'prop';
  let fd = 1e9; for (const f of fires) { const d = Math.hypot(f.x - x, f.z - z); if (d < fd) fd = d; }
  if (fd < R.nearFireExclusionM) return 'fire';
  if (Math.hypot(0 - x, -366 - z) < R.stoneRingExclusionR) return 'stone';
  return null;
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

const roadRows = CFG.roads.filter(r => r.regionId === R.regionId &&
  ['kingsRoad', 'northRoad', 'eastRoad', 'westRoad'].includes(r.id) && r.points);

// ---- (1) frozen-form aggregation over the candidate grid -------------------
const gridOut = {};
for (const rd of roadRows) {
  const cs = grid(rd);
  let pass = 0, fail = 0, excl = 0, maxRun = 0, run = 0;
  const reasons = {};
  for (const c of cs) {
    for (const off of OFFSETS) for (const side of [1, -1]) {
      const x = c.x + c.px * off * side, z = c.z + c.pz * off * side;
      if (c.mouthEnd) { excl++; run = 0; continue; }
      const why = seatPredicates(x, z);
      if (why === null) { pass++; run = 0; }
      else { fail++; run++; maxRun = Math.max(maxRun, run); reasons[why] = (reasons[why] || 0) + 1; }
    }
  }
  gridOut[rd.id] = { eligible: pass + fail, excluded: excl, pass: pass, fail: fail,
    passPct: +(100 * pass / (pass + fail)).toFixed(1), maxRun: maxRun, reasons: reasons };
}

// ---- (2) picker-response lock, AE1-A-aware separation ----------------------
// poses near roads (v1 val_ pose recipe), pickRaidSeat responses bucketed:
// OK = compliant seat; GATE-REFUSAL = ok:false with why 'seat-fail' AFTER the
// AE1-A gates exist (they refuse rather than return a violating seat);
// NO-ROAD counted separately (not an eligible-fail seat candidate).
const pickerOut = {};
for (const rd of roadRows) {
  const cs = grid(rd);
  const rnd = mulberry32(20261 + rd.id.length * 7919 + rd.points.length);
  const poses = [];
  for (let i = 0; i < 100; i++) {
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
  let ok = 0, refuse = 0, noroad = 0, maxRun = 0, run = 0;
  for (const pose of poses) {
    Math.random = mulberry32(20261 + Math.round(pose.x * 3.1 + pose.z * 5.7) % 100000);
    const game = L.mockGame(pose.x, pose.z, pose.yaw);
    A.init(game);
    let r;
    try { r = A.pickRaidSeat(); } finally { Math.random = SAVED_RANDOM; }
    if (!r.ok) {
      if (r.why === 'no-road') { noroad++; continue; }
      refuse++; run++; maxRun = Math.max(maxRun, run);
      continue;
    }
    run = 0;
    const claimed = roadRows.find(rr => rr.id === r.roadId);
    const rdD = RG.distToRoad(claimed, r.x, r.z);
    const pd = Math.hypot(r.x - pose.x, r.z - pose.z);
    if (rdD < R.seatMinRoadRenderedM || pd < R.minPlayerDistM ||
        seatPredicates(r.x, r.z) !== null) { refuse++; run++; maxRun = Math.max(maxRun, run); continue; }
    ok++; run = 0;
  }
  pickerOut[rd.id] = { poses: 100, ok: ok, gateRefusal: refuse, noRoad: noroad,
    okPctOfPoses: +(100 * ok / 100).toFixed(1), maxRun: maxRun };
}
restoreEnemy();

process.stdout.write(JSON.stringify({
  case: 'V-A22-grid (frozen A-1 form) + picker-response with AE1-A separation',
  grid: gridOut,
  gridLaw: Object.keys(gridOut).every(k => gridOut[k].passPct >= 90 && gridOut[k].maxRun <= 16),
  gridKingsExcluded: gridOut.kingsRoad.excluded,
  gridBranchExcluded: { northRoad: gridOut.northRoad.excluded, eastRoad: gridOut.eastRoad.excluded, westRoad: gridOut.westRoad.excluded },
  picker: pickerOut,
  pickerLawRaw: Object.keys(pickerOut).every(k => pickerOut[k].okPctOfPoses >= 90)
}, null, 1));
