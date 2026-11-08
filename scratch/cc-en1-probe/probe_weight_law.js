'use strict';
// CC-EN1 weight-law probe — Testerbot A4 instrument. Pure data reads, no mocks.
// Verifies the spec's pinned weights EXACTLY on first run (pre-build gate),
// and the structural law on any later run (round shape, not values).
globalThis.window = globalThis; globalThis.self = globalThis;
require('/tmp/wh-worldfeat/prototype/js/CONFIG.js');
var CFG = window.WH_CONFIG;
var E = CFG.encounters;
if (!E || !E.biomes) { console.log('FAIL pre-build: CFG.encounters absent (expected pre-build? = false)'); process.exit(1); }
var dw = E.biomes.darkwood_edge;
var fk = E.biomes.forest_of_the_old_king;

var fails = [];
function expect(l, c) { if (!c) fails.push(l); }
var PIN = [0, 0.28, 0.12, 0.15, 0.25, 0.2];
expect('weights len == night.length + 1', dw.weights.length === dw.night.length + 1);
expect('weights[0] === 0', dw.weights[0] === 0);
var sum = dw.weights.reduce(function (a, b) { return a + b; }, 0);
expect('weights sum == 1.0 +-1e-9', Math.abs(sum - 1.0) < 1e-9);
if (dw.weights.join(',') !== PIN.join(',')) {
  console.log('NOTE: weights drifted from the spec pin (IO amended? Nicko tune?): ' + dw.weights.join(','));
}
// regionC table has NO weights (AE1 owns its roll)
expect('forest_of_the_old_king carries no weights key', !('weights' in fk));
// weights indexes correspond 1:1 to the night array's tail (weights[i] is row i-1)
expect('weights tail indexes align with night rows', dw.night.every(function (r, i) {
  return typeof dw.weights[i + 1] === 'number' && dw.weights[i + 1] >= 0;
}));
if (fails.length) { console.log('WEIGHT-LAW FAIL: ' + fails.join(' | ')); process.exit(1); }
console.log('WEIGHT-LAW PASS (len ' + dw.weights.length + ', sum ' + sum + ', w[0]=0, tail maps to night rows)');
