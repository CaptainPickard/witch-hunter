// Testerbot's own independent conn[8] probe (does NOT reuse Devbot's probe).
const fs = require('fs');
global.window = {};
eval(fs.readFileSync('prototype/js/CONFIG.js', 'utf8'));
const CFG = window.WH_CONFIG;

// region-defs.js is an IIFE relying on global `window`; run it via indirect eval.
const defs = fs.readFileSync('prototype/js/region-defs.js', 'utf8');
(1, eval)(defs);

// the IIFE assigned to window.WH_REGION_DEFS presumably; find it
let out = {};
out.keys = Object.keys(window).filter(k => /REGION|DEFS|Logic|DEF/i.test(k));
out.logicKeys = window.WHConfig ? Object.keys(window.WHConfig) : undefined;

// Logic object: find the one with sideOfPlane
let Logic = null;
for (const k of Object.keys(window)) {
  const v = window[k];
  if (v && typeof v === 'object' && typeof v.sideOfPlane === 'function') { Logic = v; out.logicName = k; }
}
let Defs = null;
for (const k of Object.keys(window)) {
  const v = window[k];
  if (v && typeof v === 'object' && Array.isArray(v.connections)) { Defs = v; out.defsName = k; }
}

const conns = Defs.connections;
out.connCount = conns.length;
const c = conns[8];
out.conn8 = JSON.parse(JSON.stringify(c, (k, v) => v === undefined ? '<<undef>>' : v));
out.fromIsF = c.from === CFG.regionF.id && c.from === 'veil_galleries';
out.toIsJ = c.to === CFG.regionJ.id && c.to === 'veil_spire_approach';
out.planeCoord = c.planeCoord;

out.sidesF = c.sides['veil_galleries'];
out.sidesJ = c.sides['veil_spire_approach'];
out.sideOfPlane_Jinterior = Logic.sideOfPlane(c, -730);
out.sideIn_J = Logic.sideIn(c, 'veil_spire_approach');
out.sideOfPlane_Finterior = Logic.sideOfPlane(c, -640);
out.planeIn_F = Logic.planeIn(c, 'veil_galleries');
out.planeIn_J = Logic.planeIn(c, 'veil_spire_approach');

out.lookupFwd = Defs.connectionBetween('veil_galleries', 'veil_spire_approach') === c;
out.lookupRev = Defs.connectionBetween('veil_spire_approach', 'veil_galleries') === c;

console.log(JSON.stringify(out, null, 1));
