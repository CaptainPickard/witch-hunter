// measure-node.js — CPU-side numbers for SPIKE-LOG.md (no browser, no renderer, no game).
// Runs the SAME core as the demo (region-c-spike.js exports it when there is no document).
// Usage (repo root): <node> scratch/region-c-spike/measure-node.js
'use strict';
var path = require('path');
require(path.join(__dirname, '../../prototype/vendor/three.classic.js'));
var R = require(path.join(__dirname, 'region-c-spike.js'));

function f(v, d) { return v.toFixed(d); }

// A4 determinism: rebuild twice and hash the vertex heights.
function gridHash(T) {
  var h = 2166136261, u = new Uint32Array(T.grid.buffer);
  for (var i = 0; i < u.length; i++) h = Math.imul(h ^ u[i], 16777619);
  return (h >>> 0).toString(16);
}

var hs = [];
for (var z = -279; z < 280; z += 2) for (var x = -279; x < 280; x += 2) hs.push(R.heightA(x, z));
var hsum = R.summarise(hs);
console.log('height  p50 ' + f(hsum.p50, 2) + ' p90 ' + f(hsum.p90, 2) + ' p99 ' + f(hsum.p99, 2) + ' max ' + f(hsum.max, 2) +
  ' · spawn h(0,0) ' + f(R.heightA(0, 0), 3));

console.log('\n| S | verts | terrain tris | build ms (node) | grid hash run1 | run2 |');
R.S_CANDIDATES.forEach(function (S) {
  R.buildTerrain(S); // warm JIT
  var T1 = R.buildTerrain(S), T2 = R.buildTerrain(S);
  console.log('| ' + S + ' | ' + T1.verts + ' | ' + T1.tris + ' | ' + f(T2.buildMs, 1) + ' | ' + gridHash(T1) + ' | ' + gridHash(T2) + ' |');
});

console.log('\n| S | strategy | max diff vs C | mean diff | us/call (node) |');
var res = {};
R.S_CANDIDATES.forEach(function (S) {
  var T = R.buildTerrain(S), job = R.compareJob(T, 1000, 50);
  job.step(0);
  var r = res[S] = job.result();
  R.SAMPLER_KEYS.forEach(function (k) {
    var row = r.rows[k];
    console.log('| ' + S + ' | ' + R.SAMPLER_NAMES[k] + ' | ' + (k === 'C' ? 'ref' : f(row.max, 5)) + ' | ' +
      (k === 'C' ? 'ref' : f(row.mean, 5)) + ' | ' + f(row.us, 3) + ' |');
  });
  console.log('| ' + S + ' | verdict | ' + r.verdict.pick + ' | fallback ' + r.verdict.order.slice(1).join('>') + ' | misses ' + r.misses + ' |');
});

var sa = R.slopeStatsAnalytic(2);
console.log('\nslope deg analytic (step 2, n=' + sa.n + '): p50 ' + f(sa.p50, 1) + ' p90 ' + f(sa.p90, 1) + ' p99 ' + f(sa.p99, 1) + ' max ' + f(sa.max, 1));
R.S_CANDIDATES.forEach(function (S) {
  var q = R.slopeStatsFacets(R.buildTerrain(S));
  console.log('slope deg facets S=' + S + ' (n=' + q.n + '): p50 ' + f(q.p50, 1) + ' p90 ' + f(q.p90, 1) + ' p99 ' + f(q.p99, 1) + ' max ' + f(q.max, 1));
});
var cf = R.CLIMB_FACTOR;
console.log('\nclimbFactor ' + cf + ': run cap ' + f(Math.atan(cf) * 180 / Math.PI, 1) + ' deg, walk cap ' +
  f(Math.atan(cf * R.RUN_SPEED / R.WALK_SPEED) * 180 / Math.PI, 1) + ' deg');
