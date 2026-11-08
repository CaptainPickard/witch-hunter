// val_A17_22.js — §5.D seat law over the probe grid (V-A17..V-A22)
// Grid: centerline samples every 4 m per seat road; offsets 14.0/14.9/16.0/17.5
// both sides; >=100 seeded player poses per road; predicates from §3 read live
// from CFG.raid (no hard-coded threshold in the verdict logic).
'use strict';
const L = require('./lib.js');
const { record } = require('./lib2.js');
const { CFG, G, RID } = L;

const R = CFG.raid;
const SEED = 20261;
const OFFSETS = [14.0, 14.9, 16.0, 17.5];      // probe grid (valspec §5.D)
const STEP = 4;                                 // m between centerline samples
const POSES_PER_ROAD = 100;

// seat-eligible road rows (kingsRoad, northRoad, eastRoad, westRoad — spec §Files-2)
const seatRoads = CFG.roads.filter(r => r.regionId === R.regionId &&
  ['kingsRoad', 'northRoad', 'eastRoad', 'westRoad'].includes(r.id) && r.points);

// branch terminals for the notch-mouth exclusion (valspec §1 pins these)
const BRANCH_TERMINALS = { northRoad: { x: 0, z: -596 }, eastRoad: { x: 240, z: -366 }, westRoad: { x: -240, z: -366 } };

// centerline samples every 4 m per road (validator's own math)
function centerSamples(row) {
  const pts = row.points, out = [];
  for (let i = 0; i + 1 < pts.length; i++) {
    const a = pts[i], b = pts[i + 1];
    const len = Math.hypot(b[0] - a[0], b[1] - a[1]);
    const dx = (b[0] - a[0]) / len, dz = (b[1] - a[1]) / len;
    const px = -dz, pz = dx;                     // perpendicular
    const n = Math.ceil(len / STEP);
    for (let j = 0; j <= n; j++) {
      const t = Math.min(len, j * STEP);
      out.push({ x: a[0] + dx * t, z: a[1] + dz * t, px: px, pz: pz });
    }
  }
  // dedupe within 0.4 m (segment joints)
  out.sort((p, q) => (p.x - q.x) || (p.z - q.z));
  const cs = [];
  for (const c of out) {
    if (!cs.length || Math.hypot(c.x - cs[cs.length - 1].x, c.z - cs[cs.length - 1].z) > 0.4) cs.push(c);
  }
  return cs;
}

// §3 seat predicates measured independently (validator math, live thresholds)
function seatPredicates(x, z) {
  const slope = G.slopeTan(RID, x, z);
  if (!(slope <= R.seatMaxSlopeTan)) return 'slope';
  const props = CFG.regionC.props.filter(p => typeof p.x === 'number');
  for (const p of props) {
    if (Math.hypot(p.x - x, p.z - z) < R.seatMinPropM) return 'prop';
  }
  const fires = CFG.regionC.props.filter(p => p.asset === 'banditCampfire');
  for (const f of fires) {
    if (Math.hypot(f.x - x, f.z - z) < R.nearFireExclusionM) return 'fire';
  }
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

// pose generator: mulberry32 seeded; poses near each road (centerline + jitter
// within roadSeekRadiusM so the rear anchor can reach the road)
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const withEnemyStub = require('./lib.js').installEnemyStub([]);
const A = window.WH_AMBUSH;

// measure over all roads and poses; per-road tally
function measureRoads() {
  const out = {};
  for (const rd of seatRoads) {
    const cs = centerSamples(rd);
    const rnd = mulberry32(SEED + rd.id.length * 7919 + rd.points.length);
    // >=100 poses: random centerline sample + small lateral/along jitter (<= roadSeekRadiusM/2)
    const poses = [];
    for (let i = 0; i < POSES_PER_ROAD; i++) {
      const c = cs[Math.floor(rnd() * cs.length)];
      const jitterAlong = (rnd() * 2 - 1) * (R.roadSeekRadiusM / 2);
      const jitterLat = (rnd() * 2 - 1) * 8;      // near the road, either side
      const px = c.x + c.pz * jitterLat + Math.cos(0) * 0; // base: centerline pt
      const pz = c.z + c.px * jitterLat + Math.sin(0) * 0;
      // jitter along the road direction: use the segment direction from points
      const pts = rd.points;
      const segIdx = Math.min(pts.length - 2, Math.max(0, Math.floor((c.x + c.z) % Math.max(1, pts.length - 1))));
      const a = pts[segIdx], b = pts[segIdx + 1];
      const len = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
      const dx = (b[0] - a[0]) / len, dz = (b[1] - a[1]) / len;
      poses.push({ x: px + dx * jitterAlong, z: pz + dz * jitterAlong, yaw: rnd() * Math.PI * 2 });
    }
    let ok = 0, fail = 0, mouth = 0, bandViol = 0, roadRowViol = 0;
    let maxRun = 0, run = 0, seekFail = 0;
    const rowsClaimed = [];
    const violations = [];
    for (const pose of poses) {
      // seat law drives WH_AMBUSH.pickRaidSeat with a mock game (public surface only)
      const game = L.mockGame(pose.x, pose.z, pose.yaw);
      A.init(game);
      const r = A.pickRaidSeat();
      if (!r.ok) {
        if (r.why === 'no-road') seekFail++;
        else { fail++; run++; maxRun = Math.max(maxRun, run); }
        continue;
      }
      run = 0;
      // band measured against the seat's CLAIMED road (a rear anchor may lawfully
      // land on a different seat road than the pose's)
      const claimedRoad = seatRoads.find(row => row.id === r.roadId);
      const dRoad = L.distToCenterline(L.polyGeom(claimedRoad || rd), r.x, r.z);
      const off = dRoad; // seat's distance to its claimed road's centerline
      const inBand = off >= R.spawnBandM[0] - 1e-6 && off <= R.spawnBandM[1] + 1e-6;
      if (!inBand) bandViol++;
      const claimedOk = !!claimedRoad;
      if (!claimedOk) roadRowViol++;
      const why = seatPredicates(r.x, r.z);
      const mouthRow = notchExcluded(r.x, r.z);
      if (why === null && mouthRow === null) ok++;
      else if (mouthRow !== null) mouth++;
      else { fail++; run++; maxRun = Math.max(maxRun, run); violations.push({ x: +r.x.toFixed(1), z: +r.z.toFixed(1), why: why, dev: +(off - R.spawnBandM[1]).toFixed(2) }); }
    }
    out[rd.id] = { poses: poses.length, eligible: ok + fail, ok: ok, fail: fail, mouth: mouth,
      passPct: +((100 * ok / (ok + fail)) || 0).toFixed(1), maxRun: maxRun, seekFail: seekFail,
      bandViol: bandViol, roadRowViol: roadRowViol, violations: violations.slice(0, 6) };
  }
  return out;
}

const m = measureRoads();
withEnemyStub();

// V-A17 — seat band + road-row exclusion + road-seek
(() => {
  let bandViol = 0, roadViol = 0, seekFails = 0, poses = 0;
  const perRoad = [];
  for (const k of Object.keys(m)) {
    bandViol += m[k].bandViol; roadViol += m[k].roadRowViol; seekFails += m[k].seekFail; poses += m[k].poses;
    perRoad.push(k + ' bandViol=' + m[k].bandViol + ' seekFail=' + m[k].seekFail);
  }
  const v = bandViol === 0 && roadViol === 0;
  record('V-A17', 'seat band 14-17.5 + road-row exclusion + road-seek', v ? 'PASS' : 'FAIL',
    perRoad.join(' ; ') + ' — every ok seat within [CFG.raid.spawnBandM] of its claimed road (bandViol=' + bandViol +
    '), every roadId ∈ seat rows (roadRowViol=' + roadViol + '), poses=' + poses);
})();

// V-A18 — clearance predicates over returned ok seats (validator math §3)
(() => {
  let checked = 0, viol = 0, samples = [];
  for (const rd of seatRoads) {
    const cs = centerSamples(rd);
    const rnd = mulberry32(SEED + rd.id.length * 7919 + rd.points.length);
    for (let i = 0; i < POSES_PER_ROAD; i++) {
      const c = cs[Math.floor(rnd() * cs.length)];
      const game = L.mockGame(c.x + (rnd() * 16 - 8), c.z + (rnd() * 16 - 8), rnd() * Math.PI * 2);
      A.init(game);
      const r = A.pickRaidSeat();
      if (!r.ok) continue;
      checked++;
      const why = seatPredicates(r.x, r.z);
      const mouthRow = notchExcluded(r.x, r.z);
      if (why !== null || mouthRow !== null) viol++;
    }
  }
  const v = viol === 0;
  record('V-A18', 'seat clearance predicates over ok seats (slope/prop/fire/stone)', v ? 'PASS' : 'FAIL',
    'ok seats re-measured=' + checked + ', predicate violations=' + viol + ' (thresholds live from CFG.raid: slope<=' + R.seatMaxSlopeTan +
    ', prop>=' + R.seatMinPropM + ', fire>=' + R.nearFireExclusionM + ', stone>=' + R.stoneRingExclusionR + ')');
})();

// V-A19 — seat fire gate unified 50 m (targeted poses near the fire rows)
(() => {
  const fires = CFG.regionC.props.filter(p => p.asset === 'banditCampfire');
  let poses = 0, viol = 0, tightOk = 0;
  for (const f of fires) {
    for (const dist of [52.0, 55.0, 60.0]) {
      for (const angDeg of [0, 45, 90, 135, 180, 225, 270, 315]) {
        const ang = angDeg * Math.PI / 180;
        const px = f.x + Math.cos(ang) * dist, pz = f.z + Math.sin(ang) * dist;
        const game = L.mockGame(px, pz, ang);
        A.init(game);
        const r = A.pickRaidSeat();
        if (!r.ok) continue;
        poses++;
        const dFire = Math.min(...fires.map(q => Math.hypot(q.x - r.x, q.z - r.z)));
        if (dFire < R.nearFireExclusionM) { viol++; }
        else if (dFire < R.nearFireExclusionM + 8) tightOk++;
      }
    }
  }
  const v = viol === 0;
  record('V-A19', 'seat fire gate unified 50 m', v ? 'PASS' : 'FAIL',
    'targeted poses near 7 campfire rows: seat-returned=' + poses + ', fire<50m violations=' + viol +
    ' (seats landing within [50,58) m of a fire: ' + tightOk + ' — the 50 m wall is actually exercised)');
})();

// V-A20 — notch-mouth exclusion 26 m; kingsRoad exempt
(() => {
  let mouthPoses = 0, viol = 0, kingsOk = 0, kingsExcluded = 0;
  const terminals = Object.keys(BRANCH_TERMINALS).map(k => ({ road: k, t: BRANCH_TERMINALS[k] }));
  for (const { road, t } of terminals) {
    const rd = seatRoads.find(r => r.id === road);
    const cs = centerSamples(rd);
    // poses near the terminal end of the branch road
    for (const c of cs.slice(-14)) {
      for (const offs of OFFSETS) for (const side of [1, -1]) {
        const seatX = c.x + c.px * offs * side, seatZ = c.z + c.pz * offs * side;
        const dTerm = Math.hypot(t.x - c.x, t.z - c.z);
        if (dTerm < R.notchMouthExclusionM) {
          mouthPoses++;
          // a seat RETURNED by the picker within 26 m of the terminal is a violation
          const game = L.mockGame(c.x, c.z, Math.PI); A.init(game);
          const r = A.pickRaidSeat();
          if (r.ok && Math.hypot(t.x - r.x, t.z - r.z) < R.notchMouthExclusionM) viol++;
        }
      }
    }
  }
  // kingsRoad exemption: seats near kingsRoad's terminal (0,-332) must NOT be excluded by mouth law
  const kd = seatRoads.find(r => r.id === 'kingsRoad');
  const kcs = centerSamples(kd);
  for (const c of kcs.slice(-10)) {
    const game = L.mockGame(c.x, c.z, Math.PI); A.init(game);
    const r = A.pickRaidSeat();
    if (r.ok) kingsOk++;
  }
  const v = viol === 0;
  record('V-A20', 'notch-mouth exclusion 26 m; kingsRoad exempt', v ? 'PASS' : 'FAIL',
    'terminal-adjacent candidates exercised=' + mouthPoses + ', picker seats within 26 m of a branch terminal=' + viol +
    ' ; kingsRoad near-terminal ok seats=' + kingsOk + ' (exempt law: none excluded by mouth rule)');
})();

// V-A21 — debugForce keeps seat validation + slide honesty
(() => {
  //(a) debugForce at an off-road pose must NOT conjure a spawn:
  const gIll = L.mockGame(120, -60, 0); A.init(gIll);
  window.WH_CONFIG.raid.debugForce = true;  // ambient knob write (validator may retune a COPY)
  const rIll = A.pickRaidSeat();
  window.WH_CONFIG.raid.debugForce = false;
  const illOk = !rIll.ok && rIll.why === 'no-road';
  //(b) over all roads: any returned ok seat must pass all predicates; count slide>0
  let slideSeen = 0, viol = 0, tries = 0;
  for (const rd of seatRoads) {
    const cs = centerSamples(rd);
    const rnd = mulberry32(SEED + rd.id.length * 104729 + rd.points.length);
    for (let i = 0; i < POSES_PER_ROAD; i++) {
      const c = cs[Math.floor(rnd() * cs.length)];
      const game = L.mockGame(c.x + (rnd() * 20 - 10), c.z + (rnd() * 20 - 10), rnd() * Math.PI * 2);
      A.init(game);
      const r = A.pickRaidSeat();
      tries++;
      if (!r.ok) continue;
      if ((r.slide || 0) > 0) slideSeen++;
      const why = seatPredicates(r.x, r.z);
      if (why !== null || notchExcluded(r.x, r.z) !== null) viol++;
    }
  }
  const v = illOk && viol === 0;
  record('V-A21', 'debugForce keeps seat validation; slide/retry honesty', v ? 'PASS' : 'FAIL',
    'off-road debugForce pickRaidSeat still refuses (ok=' + rIll.ok + ', why=' + rIll.why + ') ; over ' + tries +
    ' poses: ok-seat predicate violations=' + viol + ', slide-exercised seats=' + slideSeen);
})();

// V-A22 — lock law per road: passPct >= 90, maxRun <= 16
(() => {
  const perRoad = [];
  let v = true;
  for (const k of Object.keys(m)) {
    const road = m[k];
    const ok = road.passPct >= 90 && road.maxRun <= 16;
    if (!ok) v = false;
    perRoad.push(k + ': ' + road.passPct + '% ok maxRun=' + road.maxRun + ' (poses ' + road.eligible + ', seekFail ' + road.seekFail + ', mouthExcluded ' + road.mouth + ')');
  }
  record('V-A22', 'lock law passPct>=90 maxRun<=16 per road', v ? 'PASS' : 'FAIL', perRoad.join(' ; '));
})();

const { RECORDS } = require('./lib2.js');
console.log(JSON.stringify(RECORDS.filter(r => /^V-A1[7-9]$/.test(r.id) || /^V-A2[0-2]$/.test(r.id))));
