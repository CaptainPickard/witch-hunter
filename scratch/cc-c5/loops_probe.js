// CC-C5 offline loop design probe: terrain height/slope along candidate wolf
// loops, prop clearance, road crossings, radius from C center. Node only.
globalThis.window = globalThis; globalThis.self = globalThis;
const path = require('path'); const R = process.argv[2];
require(path.join(R, 'prototype/vendor/three.classic.js'));
require(path.join(R, 'prototype/js/CONFIG.js'));
require(path.join(R, 'prototype/js/wh-ground.js'));
const C = window.WH_CONFIG, G = window.WH_GROUND, RID = 'forest_of_the_old_king';
const cx = 0, cz = -366;
const props = C.regionC.props.filter(p => p.x !== undefined);
const roads = C.roads.filter(r => r.regionId === RID && r.points);
function segX(a, b, c, d) { // segment intersection
  const r = [b[0]-a[0], b[1]-a[1]], s = [d[0]-c[0], d[1]-c[1]];
  const den = r[0]*s[1]-r[1]*s[0]; if (Math.abs(den) < 1e-9) return false;
  const t = ((c[0]-a[0])*s[1]-(c[1]-a[1])*s[0])/den, u = ((c[0]-a[0])*r[1]-(c[1]-a[1])*r[0])/den;
  return t >= 0 && t <= 1 && u >= 0 && u <= 1;
}
const loops = JSON.parse(process.argv[3]);
for (const L of loops) {
  const w = L.wp; let len = 0, maxR = 0, maxSlope = 0, hMin = 1e9, hMax = -1e9, minProp = 1e9, propName = '';
  const crossings = new Set();
  for (let i = 0; i < w.length; i++) {
    const a = w[i], b = w[(i+1) % w.length];
    const dl = Math.hypot(b[0]-a[0], b[1]-a[1]); len += dl;
    for (const rd of roads) for (let k = 0; k + 1 < rd.points.length; k++)
      if (segX(a, b, rd.points[k], rd.points[k+1])) crossings.add(rd.id);
    const n = Math.ceil(dl / 0.5);
    for (let j = 0; j <= n; j++) {
      const x = a[0] + (b[0]-a[0])*j/n, z = a[1] + (b[1]-a[1])*j/n;
      maxR = Math.max(maxR, Math.hypot(x-cx, z-cz));
      const h = G.heightAt(RID, x, z); hMin = Math.min(hMin, h); hMax = Math.max(hMax, h);
      maxSlope = Math.max(maxSlope, G.slopeTan(RID, x, z));
      for (const p of props) { const d = Math.hypot(p.x-x, p.z-z); if (d < minProp) { minProp = d; propName = p.asset + '@' + p.x + ',' + p.z + ' s' + p.scale; } }
    }
  }
  console.log(L.id, 'len', len.toFixed(1), 'maxR', maxR.toFixed(1), 'h', hMin.toFixed(2)+'..'+hMax.toFixed(2),
    'maxSlopeDeg', (Math.atan(maxSlope)*180/Math.PI).toFixed(1), 'minProp', minProp.toFixed(1), propName,
    'roads', [...crossings].join(','));
}
