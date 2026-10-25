// CC-C10 ledger3 = a COPY of scratch/cc-c17/ledger2_probe.js (that file stays
// byte-identical) with T += okFarmBarn (max(IO 29500, GLB header 29,499)) and
// farmerBody (GLB header 28,024; the NPC is not a props row - ledger3.py feeds
// it through the argv[6] extra-rows hook at CONFIG.regionC.npc x/z/cullM).
// Original header follows.
// CC-C17v2 tri ledger (node only, no game run). The CC-C8 probe
// (scratch/cc_c8_ledger_probe.js) verbatim in method - repo stubs: three
// classic + CONFIG + wh-ground + region-defs + region-manager loaded under a
// window=globalThis stub; WH_ScatterPlan gives the real scatter cells - with
// the tri table extended by (a) the 4 C13b kit assets the C8 table missed
// (IO counts: churchArchway 4000, churchCornerButtress 2000, stoneSteps 5000,
// stoneCrossTilted 4000) and (b) the CC-C17 old_king assets at
// max(IO table, GLB-header measure) per asset (conservative).
// usage: node ledger2_probe.js <repoRoot> LX LZ [R] [extraRows.json]
//   extraRows.json (optional) = candidate rows appended to regionC.props
//   (site scans); the binding run passes none (rows live in CONFIG).
globalThis.window = globalThis; globalThis.self = globalThis;
const path = require('path'); const fs = require('fs'); const ROOT = path.resolve(process.argv[2]);
require(path.join(ROOT, 'prototype/vendor/three.classic.js'));
require(path.join(ROOT, 'prototype/js/CONFIG.js'));
require(path.join(ROOT, 'prototype/js/wh-ground.js'));
require(path.join(ROOT, 'prototype/js/region-defs.js'));
require(path.join(ROOT, 'prototype/js/region-manager.js'));
const C = window.WH_CONFIG, G = window.WH_GROUND, RID = 'forest_of_the_old_king', RC = C.regionC;
const T = {"youngDeadTree": 3630, "yewTree": 28243, "witchwoodTree": 28084, "treeStump": 8109, "mourningStatue": 21384, "cemeteryGate": 20585, "mossBoulder": 21599, "lanternPost": 2500, "deadTree": 30174, "banditCampfire": 3792, "banditBedroll": 4666, "rubblePile": 2000, "fallenLog": 20788, "b6Bones": 10889,
  bushA: 2321, bushB: 2836, whBushSnare: 3000, bramble: 2288, grassTuft: 848, whWallA: 4118, whWallB: 4375, graveMound: 2000,
  // (a) C13b kit (IO counts, binding)
  churchArchway: 4000, churchCornerButtress: 2000, stoneSteps: 5000, stoneCrossTilted: 4000,
  // C8 den furniture (assets.js manifest comment counts)
  blightcap: 5786, skullPile: 4733,
  // (b) CC-C17 old_king: max(IO table, GLB header measure scratch/cc-c17/glb_measure.py)
  okFarmCottage: 28632, okFarmWell: 11481, okTreeOak: 28721, okTreePine: 23999, okFencePost: 2866,
  okFenceGate: 6700, okFenceStonewall: 9000, okFenceCornerV2: 2500, okRuinArch: 7900, okRuinColumn: 5200,
  // (c) CC-C10: barn max(IO 29500, header 29499); farmer = raw dwarf smith header (scratch/cc-c10/glb_header.txt)
  okFarmBarn: 29500, farmerBody: 28024};
const M = {"bushA": {"width": 1.775, "height": 0.962}, "bushB": {"width": 1.813, "height": 1.488}, "bramble": {"width": 1.778, "height": 1.797}, "whBushSnare": {"width": 1.896, "height": 1.621}, "grassTuft": {"width": 1.463, "height": 1.859}, "yewTree": {"width": 1.011, "height": 1.894}, "witchwoodTree": {"width": 0.642, "height": 1.889}, "deadTree": {"width": 1.38, "height": 1.896}, "mossBoulder": {"width": 1.897, "height": 1.402}, "treeStump": {"width": 1.898, "height": 1.827}};
const meta = function (n) { return M[n] ? { width: M[n].width, height: M[n].height, groundMinY: 0 } : { width: 1.5, height: 1.5, groundMinY: 0 }; };
meta.heightAt = function (x, z) { return G.heightAt(RID, x, z); };
if (process.argv[6]) RC.props = RC.props.concat(JSON.parse(fs.readFileSync(process.argv[6], 'utf8')));
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
let best = { t: 0 };
// optional: WH_FIELD=<file> dumps every grid point's total (placement search aid)
const FIELD = process.env.WH_FIELD ? [] : null;
const cx0 = RC.center.x, cz0 = RC.center.z, CULL = RC.cullDistanceM;
for (let x = LX - RAD; x <= LX + RAD; x += 2) for (let z = LZ - RAD; z <= LZ + RAD; z += 2) {
  if (Math.hypot(x - LX, z - LZ) > RAD || Math.hypot(x - cx0, z - cz0) > 278.5) continue;
  let t = TERRAIN + ROADS;
  for (const p of RC.props) if (Math.hypot(p.x - x, p.z - z) <= (p.cullM || CULL)) t += T[p.asset] || 0;
  for (const c of cells) if (Math.hypot(c.x - x, c.z - z) <= RC.scatterCullM + c.r) t += c.tris;
  if (Math.hypot(RL.stains[0].x - x, RL.stains[0].z - z) <= RL.cullM) t += stainTris;
  if (t > best.t) best = { t, x, z };
  if (FIELD) FIELD.push([x, z, t]);
}
if (FIELD) fs.writeFileSync(process.env.WH_FIELD, JSON.stringify(FIELD));
console.log(JSON.stringify({ centre: [LX, LZ], R: RAD, props: RC.props.length, missing, worst: best.t, pct: +(best.t / 2e4).toFixed(2), at: [best.x, best.z] }));
