// CC-WM1 micro-relief bowl probe: 5 m grid around the candidate center
// (58,-577): WH_GROUND y + slope per cell, to place the quarried bank arc on
// the high side and the campfire/veins on the bowl floor. Run: node scratch/cc-wm1/bowl_probe.js
globalThis.window = globalThis; globalThis.self = globalThis;
const path = require('path');
const R = '/tmp/wh-worldfeat';
require(path.join(R, 'prototype/vendor/three.classic.js'));
require(path.join(R, 'prototype/js/CONFIG.js'));
require(path.join(R, 'prototype/js/wh-ground.js'));
const G = window.WH_GROUND; const RID = 'forest_of_the_old_king';
for (let z = -589; z <= -565; z += 3) {
  let line = 'z=' + String(z).padStart(4) + ': ';
  for (let x = 46; x <= 70; x += 3) {
    const y = G.heightAt(RID, x, z);
    const deg = Math.atan(G.slopeTan(RID, x, z)) * 180 / Math.PI;
    line += `(${x},${y.toFixed(1)},${deg.toFixed(0)}) `;
  }
  console.log(line);
}
