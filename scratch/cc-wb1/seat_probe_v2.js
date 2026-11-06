globalThis.window = globalThis; globalThis.self = globalThis;
const path = require('path');
const R = '/tmp/wh-worldfeat';
require(path.join(R, 'prototype/vendor/three.classic.js'));
require(path.join(R, 'prototype/js/CONFIG.js'));
require(path.join(R, 'prototype/js/wh-ground.js'));
const G = window.WH_GROUND, RID = 'hold_outskirts';
console.log('WH_GROUND.has(' + RID + ') =', G.has(RID));
const seats = [['boardA', 6.7, -14.5], ['boardB', 10.7, -14.5]];
for (const s of seats) {
  const y = G.heightAt(RID, s[1], s[2]);
  console.log(s[0], 'y=', y.toFixed(3), 'slope=', (Math.atan(G.slopeTan(RID, s[1], s[2]))*180/Math.PI).toFixed(2)+'deg');
}
// clearance: board seat A (6.7,-14.5) vs CONFIG regionA rows + enemies + nodes
const A = window.WH_CONFIG.regionA;
const pts = [];
(A.props||[]).forEach(p => pts.push(['prop:'+p.asset, p.x, p.z]));
(A.enemies||[]).forEach(e => pts.push(['enemy:'+e.type, e.x, e.z]));
(A.nodes||[]).forEach(n => pts.push(['node:'+n.type, n.x, n.z]));
for (const s of seats) {
  let best = null, bd = Infinity;
  for (const p of pts) {
    const d = Math.hypot(p[1]-s[1], p[2]-s[2]);
    if (d < bd) { bd = d; best = p; }
  }
  console.log(s[0], 'nearest:', best[0], best[1]+','+best[2], 'd=', bd.toFixed(2)+'m');
}
// distance boardA -> spawn and -> redseam center approx
console.log('dist boardA->spawn(2.5,74):', Math.hypot(6.7-2.5, -14.5-74).toFixed(1)+'m');
console.log('dist boardA->redseam(57.5,-579):', Math.hypot(6.7-57.5, -14.5+579).toFixed(1)+'m');
