// CC-C10 farmer probe (node only, no game run; ledger2_probe repo-stub pattern).
// Valspec A1: farmer (x, z) within 25 m of the cottage (150.5, -256.7), >= 1.5 m
// from every regionC.props row (RECORD min), heightAt at the farmer, slope over a
// 1 m ring (RECORD, <= 20 deg expected), distance to the C centre (<= 270).
// usage: node probe_npc.js <repoRoot> ['<json {x,z}>']   (no json = CONFIG.regionC.npc)
globalThis.window = globalThis; globalThis.self = globalThis;
const path = require('path'); const ROOT = path.resolve(process.argv[2]);
require(path.join(ROOT, 'prototype/vendor/three.classic.js'));
require(path.join(ROOT, 'prototype/js/CONFIG.js'));
require(path.join(ROOT, 'prototype/js/wh-ground.js'));
const C = window.WH_CONFIG, G = window.WH_GROUND, RID = C.regionC.id, RC = C.regionC;
const COTTAGE = [150.5, -256.7];
const npc = process.argv[3] ? JSON.parse(process.argv[3]) : RC.npc;
const x = npc.x, z = npc.z, r1 = v => Math.round(v * 100) / 100;
let near = { d: 1e9 };
RC.props.forEach(p => { const d = Math.hypot(p.x - x, p.z - z); if (d < near.d) near = { d, who: p.asset + '@' + p.x + ',' + p.z }; });
const h0 = G.heightAt(RID, x, z);
let slope = 0;
for (let a = 0; a < 16; a++) {
  const t = a * Math.PI / 8, h = G.heightAt(RID, x + Math.cos(t), z + Math.sin(t));
  slope = Math.max(slope, Math.atan(Math.abs(h - h0)) * 180 / Math.PI);
}
const cottage = Math.hypot(x - COTTAGE[0], z - COTTAGE[1]);
const centre = Math.hypot(x - RC.center.x, z - RC.center.z);
const out = {
  source: process.argv[3] ? 'candidate' : 'CONFIG.regionC.npc', at: [x, z], rotY: npc.rotY,
  heightAt: r1(h0), footY_r0_4: r1(G.footY(RID, x, z, 0.4)), slope1mDeg: r1(slope),
  cottageM: r1(cottage), nearestProp: [r1(near.d), near.who], centreM: r1(centre),
  interactM: npc.interactM, cullM: npc.cullM,
  PASS: cottage <= 25 && near.d >= 1.5 && slope <= 20 && centre <= 270
};
console.log(JSON.stringify(out));
