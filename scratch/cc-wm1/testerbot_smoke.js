// CC-WM1 Testerbot H: node one-shot runtime smoke (no browser)
globalThis.window = globalThis;
require('/tmp/wh-worldfeat/prototype/vendor/three.classic.js');
require('/tmp/wh-worldfeat/prototype/js/CONFIG.js');
require('/tmp/wh-worldfeat/prototype/js/wh-ground.js');

const C = window.WH_CONFIG;
const G = window.WH_GROUND;
if (!C) { console.error('FAIL: WH_CONFIG missing'); process.exit(1); }
if (!G || typeof G.heightAt !== 'function') {
  console.error('FAIL: WH_GROUND.heightAt missing'); process.exit(1);
}

const veins = [
  [53, -577], [55.5, -573.5], [61, -572], [64, -575.5],
  [63.5, -582], [57, -584], [51.5, -581.5], [50, -574],
];
const RX = 0, RZ = -366;         // region C centre per census/spec
let bad = 0;
for (const [x, z] of veins) {
  const y = G.heightAt('forest_of_the_old_king', x, z);
  const d = Math.hypot(x - RX, z - RZ);
  const ok = Number.isFinite(y) && Math.abs(y) <= 26 && d <= 280;
  console.log(`vein (${x}, ${z})  y=${y.toFixed(2)}  d=${d.toFixed(1)}  ${ok ? 'OK' : 'FAIL'}`);
  if (!ok) bad++;
}
// Bonus assertions: node type & item wired up
const nt = C.gather.nodeTypes.ironVein;
const it = C.items.ironOre;
console.log('nodeTypes.ironVein:', nt ? 'OK' : 'MISSING');
console.log('items.ironOre:     ', it ? 'OK' : 'MISSING');
if (!nt || !it) bad++;

// Testerbot extras: regionC.nodes density + census via the real runtime object
const rnodes = C.regionC.nodes;
const dense = Array.isArray(rnodes) && rnodes.length === 16 && rnodes.every(n => n && n.type && Number.isFinite(n.x) && Number.isFinite(n.z));
const byType = {};
rnodes.forEach(n => { byType[n.type] = (byType[n.type] || 0) + 1; });
console.log(`regionC.nodes runtime census: len=${rnodes.length} dense=${dense} types=${JSON.stringify(byType)}`);
if (!dense || byType.ironVein !== 8 || byType.bonePile !== 8) bad++;

// cross-wiring: every nodeType yield id must exist in CONFIG.items
for (const [k, v] of Object.entries(C.gather.nodeTypes)) {
  const has = !!(C.items[v.yield.id]);
  console.log(`yield cross-wire ${k} -> ${v.yield.id}: ${has ? 'OK' : 'BROKEN'}`);
  if (!has) bad++;
}

if (bad) { console.error(`H FAIL: ${bad} checks failed`); process.exit(1); }
console.log('H PASS — 8 vein seats on-terrain, |y|<=26, d<=280 from (0,-366), ironVein+ironOre wired');
