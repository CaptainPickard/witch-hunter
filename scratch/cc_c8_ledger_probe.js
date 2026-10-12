// CC-C8 offline tri-ledger probe for region C (Testerbot; node only, no game
// run). The CC-C7 probe (scratch/cc-c7/ledger_probe.js) re-pointed at the C8
// layout: drawn-tri upper bound at every 2 m grid point within R m of
// (LX, LZ): non-outcrop props inside cullDistanceM, outcrop rows (own cullM)
// inside their cullM, the outcrop stains, scatter cells inside scatterCullM
// + r, terrain + roads. The rot mother + 3 spawn bodies are GONE from C (den).
// usage: node scratch/cc_c8_ledger_probe.js <repoRoot> LX LZ [R]
globalThis.window = globalThis; globalThis.self = globalThis;
const path = require('path'); const ROOT = path.resolve(process.argv[2]);
require(path.join(ROOT, 'prototype/vendor/three.classic.js'));
require(path.join(ROOT, 'prototype/js/CONFIG.js'));
require(path.join(ROOT, 'prototype/js/wh-ground.js'));
require(path.join(ROOT, 'prototype/js/region-defs.js'));
require(path.join(ROOT, 'prototype/js/region-manager.js'));
const C = window.WH_CONFIG, G = window.WH_GROUND, RID = 'forest_of_the_old_king', RC = C.regionC;
// GLB-header tris (C7 probe table + the C8 kit, scratch/cc_c8_check.js scan)
const T = {"yewTree": 28243, "witchwoodTree": 28084, "treeStump": 8109, "mourningStatue": 21384, "cemeteryGate": 20585, "mossBoulder": 21599, "lanternPost": 2500, "deadTree": 30174, "banditCampfire": 3792, "banditBedroll": 4666, "rubblePile": 2000, "fallenLog": 20788, "b6Bones": 10889,
  bushA: 2321, bushB: 2836, whBushSnare: 3000, bramble: 2288, grassTuft: 848, whWallA: 4118, whWallB: 4375, graveMound: 2000};
const M = {"bushA": {"width": 1.775, "height": 0.962}, "bushB": {"width": 1.813, "height": 1.488}, "bramble": {"width": 1.778, "height": 1.797}, "whBushSnare": {"width": 1.896, "height": 1.621}, "grassTuft": {"width": 1.463, "height": 1.859}, "yewTree": {"width": 1.011, "height": 1.894}, "witchwoodTree": {"width": 0.642, "height": 1.889}, "deadTree": {"width": 1.38, "height": 1.896}, "mossBoulder": {"width": 1.897, "height": 1.402}, "treeStump": {"width": 1.898, "height": 1.827}};
const meta = function (n) { return M[n] ? { width: M[n].width, height: M[n].height, groundMinY: 0 } : { width: 1.5, height: 1.5, groundMinY: 0 }; };
meta.heightAt = function (x, z) { return G.heightAt(RID, x, z); };
const missing = [...new Set(RC.props.map(p => p.asset).filter(a => T[a] === undefined))];
const plan = window.WH_ScatterPlan(RID, meta);
const cells = [];
Object.keys(plan.instances).forEach(name => {
  if (T[name] === undefined) missing.push('scatter:' + name);
  const by = {};
  plan.instances[name].forEach(it => { const k = Math.floor(it.x / RC.scatterCellM) + ':' + Math.floor(it.z / RC.scatterCellM); (by[k] = by[k] || []).push(it); });
  Object.values(by).forEach(list => { let cx = 0, cz = 0, r = 0; list.forEach(q => { cx += q.x; cz += q.z; }); cx /= list.length; cz /= list.length;
    list.forEach(q => { r = Math.max(r, Math.hypot(q.x - cx, q.z - cz)); }); cells.push({ x: cx, z: cz, r, tris: list.length * (T[name] || 0) }); });
});
const LX = +process.argv[3], LZ = +process.argv[4], RAD = +(process.argv[5] || 170);
const RL = RC.rotLair;
const stainTris = RL.stains.length * RL.pool.segments * (1 + 2 * (RL.pool.rings - 1)) + 2;
const TERRAIN = 39200, ROADS = 2256 + 180;
let best = { t: 0 }, bestBase = { t: 0 };
const cx0 = RC.center.x, cz0 = RC.center.z, CULL = RC.cullDistanceM;
for (let x = LX - RAD; x <= LX + RAD; x += 2) for (let z = LZ - RAD; z <= LZ + RAD; z += 2) {
  if (Math.hypot(x - LX, z - LZ) > RAD || Math.hypot(x - cx0, z - cz0) > 278.5) continue;
  let t = TERRAIN + ROADS, tb;
  for (const p of RC.props) if (!p.cullM && Math.hypot(p.x - x, p.z - z) <= CULL) t += T[p.asset] || 0;
  for (const c of cells) if (Math.hypot(c.x - x, c.z - z) <= RC.scatterCullM + c.r) t += c.tris;
  tb = t;
  for (const p of RC.props) if (p.cullM && Math.hypot(p.x - x, p.z - z) <= p.cullM) t += T[p.asset] || 0;
  if (Math.hypot(RL.stains[0].x - x, RL.stains[0].z - z) <= RL.cullM) t += stainTris;
  if (t > best.t) best = { t, x, z };
  if (tb > bestBase.t) bestBase = { t: tb, x, z };
}
console.log('missing tri rows:', missing.length ? missing.join(',') : 'none');
console.log('outcrop rows (cullM):', RC.props.filter(p => p.cullM).length, 'tris', RC.props.filter(p => p.cullM).reduce((s, p) => s + T[p.asset], 0), '+ stains', stainTris);
console.log('worst within ' + RAD + ' m of (' + LX + ',' + LZ + ') WITHOUT outcrop:', bestBase.t, '(' + (bestBase.t / 2e4).toFixed(1) + '% of 2M) at', bestBase.x, bestBase.z);
console.log('worst within ' + RAD + ' m of (' + LX + ',' + LZ + ') C8 LAYOUT   :', best.t, '(' + (best.t / 2e4).toFixed(1) + '% of 2M) at', best.x, best.z);
