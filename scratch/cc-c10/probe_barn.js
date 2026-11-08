// CC-C10 barn probe (node only, no game run; the ledger2_probe repo-stub
// pattern: window = globalThis + three.classic + CONFIG + wh-ground +
// region-defs + region-manager). Gates (valspec A7): barn >= 26 m from every
// OTHER regionC.props row and every camp fire (banditCampfire rows + C cook
// stations), >= 8 m from every C road centreline, <= 60 m from the cottage
// (150.5, -256.7). RECORD: seat span / slope, wolf-loop + enemy distances,
// nearest scatter instance.
// usage:
//   node probe_barn.js <repoRoot> scan          deterministic grid scan (1 m, no RNG):
//                                               the gate-clear slot nearest the cottage
//                                               (ties: lower seat span, then x, then z)
//   node probe_barn.js <repoRoot> row '<json>'  check one candidate row (pre-paste)
//   node probe_barn.js <repoRoot>               check the okFarmBarn row(s) live in CONFIG
globalThis.window = globalThis; globalThis.self = globalThis;
const path = require('path'); const ROOT = path.resolve(process.argv[2]);
require(path.join(ROOT, 'prototype/vendor/three.classic.js'));
require(path.join(ROOT, 'prototype/js/CONFIG.js'));
require(path.join(ROOT, 'prototype/js/wh-ground.js'));
require(path.join(ROOT, 'prototype/js/region-defs.js'));
require(path.join(ROOT, 'prototype/js/region-manager.js'));
const C = window.WH_CONFIG, G = window.WH_GROUND, RID = 'forest_of_the_old_king', RC = C.regionC;
const COTTAGE = [150.5, -256.7], GATE_PROPS = 26, GATE_FIRES = 26, GATE_ROAD = 8, MAX_COTTAGE = 60;
const FOOT_R = 5;   // barn half-footprint at the chosen scale (~1.9 x 5.5 / 2)

const segD = (x, z, a, b) => { const ex = b[0] - a[0], ez = b[1] - a[1], L = ex * ex + ez * ez;
  const t = L ? Math.max(0, Math.min(1, ((x - a[0]) * ex + (z - a[1]) * ez) / L)) : 0;
  return Math.hypot(x - (a[0] + ex * t), z - (a[1] + ez * t)); };
const roads = C.roads.filter(r => r.regionId === RID);
const fires = RC.props.filter(p => p.asset === 'banditCampfire').map(p => ['banditCampfire', p.x, p.z])
  .concat(C.cooking.stations.filter(s => !s.regionId || s.regionId === RID).map(s => [s.id, s.x, s.z]));
const loops = C.enemy.wolfPacks.filter(p => p.regionId === RID);

function measure(x, z, skipBarn) {
  let props = { d: 1e9 }, road = { d: 1e9 }, fire = { d: 1e9 }, loop = { d: 1e9 }, enemy = { d: 1e9 };
  RC.props.forEach(p => { if (skipBarn && p.asset === 'okFarmBarn') return;
    const d = Math.hypot(p.x - x, p.z - z); if (d < props.d) props = { d, who: p.asset + '@' + p.x + ',' + p.z }; });
  roads.forEach(r => { let d;
    if (r.ring) d = Math.abs(Math.hypot(x - r.ring.x, z - r.ring.z) - r.ring.r);
    else { d = 1e9; for (let i = 0; i + 1 < r.points.length; i++) d = Math.min(d, segD(x, z, r.points[i], r.points[i + 1])); }
    if (d < road.d) road = { d, who: r.id }; });
  fires.forEach(f => { const d = Math.hypot(f[1] - x, f[2] - z); if (d < fire.d) fire = { d, who: f[0] + '@' + f[1] + ',' + f[2] }; });
  loops.forEach(p => { const w = p.waypoints; for (let i = 0; i < w.length; i++) {
    const d = segD(x, z, w[i], w[(i + 1) % w.length]); if (d < loop.d) loop = { d, who: p.id }; } });
  RC.enemies.forEach(e => { const d = Math.hypot(e.x - x, e.z - z); if (d < enemy.d) enemy = { d, who: e.type + '@' + e.x + ',' + e.z }; });
  const hs = [[0, 0], [FOOT_R, 0], [-FOOT_R, 0], [0, FOOT_R], [0, -FOOT_R]].map(o => G.heightAt(RID, x + o[0], z + o[1]));
  const span = Math.max(...hs) - Math.min(...hs);
  const slopeDeg = Math.atan(span / FOOT_R) * 180 / Math.PI;
  const cottage = Math.hypot(x - COTTAGE[0], z - COTTAGE[1]);
  const pass = props.d >= GATE_PROPS && fire.d >= GATE_FIRES && road.d >= GATE_ROAD && cottage <= MAX_COTTAGE;
  return { x, z, cottage, props, fire, road, loop, enemy, y: hs[0], span, slopeDeg, pass };
}
const r1 = v => Math.round(v * 10) / 10;
function fmt(m) {
  return { at: [m.x, m.z], cottage: r1(m.cottage), props: [r1(m.props.d), m.props.who], fires: [r1(m.fire.d), m.fire.who],
    roads: [r1(m.road.d), m.road.who], wolfLoops: [r1(m.loop.d), m.loop.who], enemies: [r1(m.enemy.d), m.enemy.who],
    groundY: +m.y.toFixed(2), seatSpanM: +m.span.toFixed(2), seatSlopeDeg: +m.slopeDeg.toFixed(1), PASS: m.pass };
}
function nearestScatter(x, z) {
  const meta = n => ({ width: 1.5, height: 1.5, groundMinY: 0 });
  meta.heightAt = (qx, qz) => G.heightAt(RID, qx, qz);
  const plan = window.WH_ScatterPlan(RID, meta); let best = { d: 1e9 };
  Object.keys(plan.instances).forEach(n => plan.instances[n].forEach(it => {
    const d = Math.hypot(it.x - x, it.z - z); if (d < best.d) best = { d: r1(d), who: n }; }));
  return best;
}

const mode = process.argv[3];
if (mode === 'scan') {
  let best = null, n = 0;
  for (let x = COTTAGE[0] - MAX_COTTAGE; x <= COTTAGE[0] + MAX_COTTAGE; x += 1)
    for (let z = COTTAGE[1] - MAX_COTTAGE; z <= COTTAGE[1] + MAX_COTTAGE; z += 1) {
      const m = measure(x, z, true); if (!m.pass) continue; n++;
      if (!best || m.cottage < best.cottage - 1e-9 ||
          (Math.abs(m.cottage - best.cottage) < 1e-9 && m.span < best.span)) best = m;
    }
  console.log(JSON.stringify({ mode: 'scan', clearSlots: n, best: best && fmt(best) }));
} else if (mode === 'row') {
  const row = JSON.parse(process.argv[4]); RC.props = RC.props.concat([row]);
  const m = measure(row.x, row.z, true);
  console.log(JSON.stringify({ mode: 'row', row, probe: fmt(m), scatterNearest: nearestScatter(row.x, row.z) }));
} else {
  const rows = RC.props.filter(p => p.asset === 'okFarmBarn');
  rows.forEach(row => console.log(JSON.stringify({ mode: 'config', row, probe: fmt(measure(row.x, row.z, true)),
    scatterNearest: nearestScatter(row.x, row.z) })));
  console.log(JSON.stringify({ okFarmBarnRows: rows.length, ALL_PASS: rows.length === 1 && rows.every(r => measure(r.x, r.z, true).pass) }));
}
