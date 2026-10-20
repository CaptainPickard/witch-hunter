// CC-C13b probe: offline clearance check for the two regionC stone-ruin
// clusters (plain node, no three). Pattern: scratch/cc-c5/loops_probe.js +
// scratch/extract_rows.cjs (rows parsed out of CONFIG.js text).
// Run from the repo root:  node scratch/cc13b_probe.cjs   (exit 1 = a rule fails)
// Collider radii use NOMINAL widths (scale 1, metres) - the live game reads
// meta.width from each GLB at load; these are collider-edge ESTIMATES.
'use strict';
var fs = require('fs');
var src = fs.readFileSync('prototype/js/CONFIG.js', 'utf8');
var lines = src.split('\n');

// ---- nominal widths (brief table + estimates for the regionC-only assets)
var WIDTH = {
  cemeteryGate: 2.4, picketFence: 2.0, ironFenceSection: 1.8, churchArchway: 2.0,
  churchCornerButtress: 0.9, mossBoulder: 1.5, stoneSteps: 1.2, rubblePile: 1.1,
  stoneCrossTilted: 0.7, gravestoneObelisk: 0.6, buriedCoffin: 0.9, graveMound: 1.6,
  lanternPost: 0.4, bramble: 1.8, whWallA: 2.9, whWallB: 2.9, mourningStatue: 0.8,
  yewTree: 1.4,
  // ESTIMATES (not in the brief table): flagged in the report
  witchwoodTree: 1.4, deadTree: 1.2, treeStump: 1.0, lanternWaymarker: 0.4,
  banditCampfire: 1.2, banditBedroll: 2.0
};
// region-manager.js colliderRadius (TRUNK_ASSETS + regex, x 0.25)
var TRUNK_ASSETS = { livingOak: 1, witchwoodTree: 1, birchTree: 1, deadTree: 1, deadTree2: 1,
  ancientOak: 1, hangingTree: 1, twistedSapling: 1, thornbush: 1, bramble: 1, largeFern: 1,
  deadShrub: 1, mossyStump: 1, hollowStump: 1 };
function colliderR(name, scale) {
  var w = WIDTH[name];
  if (w == null) throw new Error('no nominal width for ' + name);
  var r = w * scale / 2;
  if (TRUNK_ASSETS[name] || /tree|oak|birch|sapling|bush|bramble|fern|shrub|stump/i.test(name)) r *= 0.25;
  return r;
}

// ---- (a) regionC props table, parsed from CONFIG.js text
var start = -1;
for (var i = 0; i < lines.length; i++) if (/^\s{2}regionC:\s*\{/.test(lines[i])) { start = i; break; }
var pStart = -1;
for (i = start; i < lines.length; i++) if (/^\s{4}props:\s*\[/.test(lines[i])) { pStart = i; break; }
var depth = 0, pEnd = -1;
for (i = pStart; i < lines.length; i++) {
  var code = lines[i].replace(/\/\/.*$/, '');
  depth += (code.match(/\[/g) || []).length - (code.match(/\]/g) || []).length;
  if (depth === 0) { pEnd = i; break; }
}
function num(l, k) { var m = l.match(new RegExp('\\b' + k + ':\\s*(-?[\\d.]+)')); return m ? parseFloat(m[1]) : null; }
var MARK = 'CC-C13b';
var existing = [], skipFrom = -1;
for (i = pStart; i <= pEnd; i++) {
  if (lines[i].indexOf(MARK) >= 0 && /^\s*\/\//.test(lines[i])) { skipFrom = i; break; } // our own block (re-runs)
  var l = lines[i];
  if (/^\s*\/\//.test(l)) continue;
  var am = l.match(/asset:\s*'([^']+)'/);
  if (!am) continue;
  existing.push({ asset: am[1], x: num(l, 'x'), z: num(l, 'z'), rotY: num(l, 'rotY') || 0,
    scale: num(l, 'scale') == null ? 1 : num(l, 'scale'), wall: num(l, 'wall'),
    noCollide: /noCollide:\s*true/.test(l), line: i + 1 });
}

// ---- (b) the NEW rows (mirror of the CONFIG.js CC-C13b block)
var NEW = [
  // C1 - denTrail mid-point ruin, north of the trail (centerline z -221 at x -95)
  // (draft core (-95,-208) sat ON the shipped boulder pair L900/L901 (-84.8/-90.7, -208):
  //  shifted ~7-9 m west, beyond the 2 m nudge budget - flagged in the report)
  { c: 'C1', asset: 'churchArchway', x: -101.0, z: -207.0, rotY: 2.6, scale: 1.7 },
  { c: 'C1', asset: 'churchCornerButtress', x: -104.5, z: -205.0, rotY: 1.2, scale: 1.5 },
  { c: 'C1', asset: 'stoneSteps', x: -100.5, z: -210.5, rotY: 0.4, scale: 1.1 },
  { c: 'C1', asset: 'rubblePile', x: -98.5, z: -203.5, rotY: 2.9, scale: 1.2 },
  { c: 'C1', asset: 'mossBoulder', x: -104.0, z: -210.0, rotY: 4.1, scale: 1.05 },
  // C2 - spawn glade west ruin
  { c: 'C2', asset: 'rubblePile', x: -31.0, z: -139.0, rotY: 0.8, scale: 1.4 },
  { c: 'C2', asset: 'churchCornerButtress', x: -33.0, z: -143.5, rotY: 2.2, scale: 1.4 },
  { c: 'C2', asset: 'mossBoulder', x: -29.0, z: -144.0, rotY: 5.0, scale: 1.0 },
  { c: 'C2', asset: 'stoneCrossTilted', x: -26.5, z: -146.5, rotY: 3.0, scale: 1.55 }
];

// ---- (c) roads (copied from CONFIG.js roads block)
var ROADS = [
  { id: 'kingsRoad', hw: 2.2, sway: 7, pts: [[0, -88], [-2.5, -104], [4, -138], [2, -168], [4, -215], [-3, -255], [0, -300], [0, -332]] },
  { id: 'stoneApproach', hw: 2.2, sway: 0, pts: [[0, -332], [0, -352]] },
  { id: 'northRoad', hw: 2.2, sway: 6, pts: [[0, -400], [-3, -420], [-12, -460], [5, -500], [-5, -540], [0, -596]] },
  { id: 'eastRoad', hw: 2.2, sway: 6, pts: [[34, -366], [62, -356], [100, -370], [150, -368], [200, -368], [240, -366]] },
  { id: 'westRoad', hw: 2.2, sway: 6, pts: [[-34, -366], [-66, -362], [-100, -370], [-150, -357], [-200, -370], [-240, -366]] },
  { id: 'denTrail', hw: 1.8, sway: 3, pts: [[4, -215], [-20, -218], [-45, -220], [-70, -221], [-95, -221], [-115, -222], [-126, -223]] },
  { id: 'denTrailNotch', hw: 1.8, sway: 0, pts: [[-126, -223], [-136, -223.4]] }
];
var RING = { id: 'stoneRing', hw: 2.2, x: 0, z: -366, r: 34 };
// brief floors (edge clearance after halfWidth); the sway-inclusive floor = 4 + sway
var FLOOR = { denTrail: 5.8, denTrailNotch: 5.8 };
function roadFloor(r) { return Math.max(FLOOR[r.id] || 6.2, 4 + (r.sway || 0)); }

function segDist(px, pz, ax, az, bx, bz) {
  var dx = bx - ax, dz = bz - az, L2 = dx * dx + dz * dz;
  var t = L2 ? Math.max(0, Math.min(1, ((px - ax) * dx + (pz - az) * dz) / L2)) : 0;
  return Math.hypot(px - (ax + t * dx), pz - (az + t * dz));
}
function polyDist(px, pz, pts) {
  var d = Infinity;
  for (var k = 0; k + 1 < pts.length; k++) d = Math.min(d, segDist(px, pz, pts[k][0], pts[k][1], pts[k + 1][0], pts[k + 1][1]));
  return d;
}

// ---- existing colliders (wall rows -> per-segment circles, region-manager style)
var WALL_R = (function () { var m = src.match(/boundaryWall:[\s\S]*?collider:\s*\{\s*r:\s*([\d.]+)/); return m ? parseFloat(m[1]) : 1.0; })();
var circles = [], wallPts = [];
existing.forEach(function (p) {
  if (p.noCollide) return;
  if (p.wall) {
    var len = WIDTH[p.asset] * p.scale, ax = Math.cos(p.rotY), az = -Math.sin(p.rotY);
    for (var k = 0; k < p.wall; k++) {
      var t = ((k + 0.5) / p.wall - 0.5) * len;
      var c = { asset: p.asset + '.seg' + k, x: p.x + ax * t, z: p.z + az * t, r: WALL_R, line: p.line };
      circles.push(c); wallPts.push(c);
    }
    wallPts.push({ x: p.x + ax * len / 2, z: p.z + az * len / 2 }, { x: p.x - ax * len / 2, z: p.z - az * len / 2 });
    return;
  }
  circles.push({ asset: p.asset, x: p.x, z: p.z, r: colliderR(p.asset, p.scale), line: p.line });
});
// wall band = bbox of every outcrop wall segment endpoint + the outcrop dressing rows (x < -130, z -235..-212)
var band = { x0: Infinity, x1: -Infinity, z0: Infinity, z1: -Infinity };
wallPts.concat(existing.filter(function (p) { return p.x < -130 && p.x > -150 && p.z < -212 && p.z > -236; })).forEach(function (q) {
  band.x0 = Math.min(band.x0, q.x); band.x1 = Math.max(band.x1, q.x);
  band.z0 = Math.min(band.z0, q.z); band.z1 = Math.max(band.z1, q.z);
});
function bandDist(x, z) {
  var dx = Math.max(band.x0 - x, 0, x - band.x1), dz = Math.max(band.z0 - z, 0, z - band.z1);
  return Math.hypot(dx, dz);
}
var BAND_FLOOR = 20; // "clear of the outcrop wall rows entirely"

// ---- (d) checks
var fails = [];
function f2(v) { return (v >= 0 ? ' ' : '') + v.toFixed(2); }
console.log('regionC props L' + (pStart + 1) + '-' + (pEnd + 1) + ': ' + existing.length + ' active rows parsed (' +
  circles.length + ' collider circles, wall r ' + WALL_R + ')' + (skipFrom >= 0 ? '; CC-C13b block at L' + (skipFrom + 1) + ' excluded' : ''));
console.log('wall band bbox x ' + band.x0.toFixed(1) + '..' + band.x1.toFixed(1) + ' z ' + band.z0.toFixed(1) + '..' + band.z1.toFixed(1));
console.log('');
console.log('row | asset                | x       z       | colR | prop gap (nearest)              | denTrail | kingsRd | other road (id)         | ring34 | band');
NEW.forEach(function (n, idx) {
  var r = colliderR(n.asset, n.scale);
  var best = { g: Infinity };
  circles.forEach(function (c) {
    var g = Math.hypot(n.x - c.x, n.z - c.z) - r - c.r;
    if (g < best.g) best = { g: g, c: c };
  });
  if (best.g < 6) fails.push(n.c + ' ' + n.asset + ': prop gap ' + best.g.toFixed(2) + ' < 6 (' + best.c.asset + ' L' + best.c.line + ')');
  var rd = {}, other = { g: Infinity, id: '' };
  ROADS.forEach(function (R) {
    var g = polyDist(n.x, n.z, R.pts) - R.hw - r;
    rd[R.id] = g;
    var fl = roadFloor(R);
    if (g < fl) fails.push(n.c + ' ' + n.asset + ': ' + R.id + ' edge gap ' + g.toFixed(2) + ' < ' + fl + ' (sway ' + R.sway + ' incl.)');
    if (R.id !== 'denTrail' && R.id !== 'kingsRoad' && g < other.g) other = { g: g, id: R.id };
  });
  var ringG = Math.abs(Math.hypot(n.x - RING.x, n.z - RING.z) - RING.r) - RING.hw - r;
  if (ringG < 6.2) fails.push(n.c + ' ' + n.asset + ': stoneRing gap ' + ringG.toFixed(2));
  var bd = bandDist(n.x, n.z) - r;
  if (bd < BAND_FLOOR) fails.push(n.c + ' ' + n.asset + ': wall band gap ' + bd.toFixed(2) + ' < ' + BAND_FLOOR);
  var pad = function (s, w) { s = String(s); while (s.length < w) s += ' '; return s; };
  console.log(pad(n.c + '.' + idx, 4) + '| ' + pad(n.asset, 21) + '| ' + pad(n.x.toFixed(1), 8) + pad(n.z.toFixed(1), 8) + '| ' +
    pad(r.toFixed(2), 5) + '| ' + pad(f2(best.g) + ' (' + best.c.asset + ' L' + best.c.line + ')', 32) + '| ' +
    pad(f2(rd.denTrail), 9) + '| ' + pad(f2(rd.kingsRoad), 8) + '| ' + pad(f2(other.g) + ' (' + other.id + ')', 24) + '| ' +
    pad(f2(ringG), 7) + '| ' + f2(bd));
});

// intra-cluster (info only: ruin pieces sit together on purpose)
console.log('');
['C1', 'C2'].forEach(function (cl) {
  var rows = NEW.filter(function (n) { return n.c === cl; }), minG = Infinity, pair = '';
  for (var a = 0; a < rows.length; a++) for (var b = a + 1; b < rows.length; b++) {
    var g = Math.hypot(rows[a].x - rows[b].x, rows[a].z - rows[b].z) - colliderR(rows[a].asset, rows[a].scale) - colliderR(rows[b].asset, rows[b].scale);
    if (g < minG) { minG = g; pair = rows[a].asset + '/' + rows[b].asset; }
  }
  console.log(cl + ' intra-cluster min collider gap ' + minG.toFixed(2) + ' m (' + pair + ') - info only');
});

// CONFIG.js block vs the NEW table (catches a hand-edit drift)
if (skipFrom >= 0) {
  var cfgRows = [];
  for (i = skipFrom + 1; i < pEnd; i++) {
    var am2 = lines[i].match(/asset:\s*'([^']+)'/);
    if (am2) cfgRows.push(am2[1] + '@' + num(lines[i], 'x') + ',' + num(lines[i], 'z') + ',' + num(lines[i], 'rotY') + ',' + num(lines[i], 'scale'));
  }
  var want = NEW.map(function (n) { return n.asset + '@' + n.x + ',' + n.z + ',' + n.rotY + ',' + n.scale; });
  if (cfgRows.join('|') !== want.join('|')) fails.push('CONFIG.js CC-C13b block != probe NEW table');
  else console.log('CONFIG.js CC-C13b block matches the probe table (' + cfgRows.length + ' rows)');
}

console.log('');
if (fails.length) { console.log('FAIL (' + fails.length + '):\n  ' + fails.join('\n  ')); process.exit(1); }
console.log('PASS: every new row clears props >= 6 m, roads (sway-incl.), stoneRing r34 and the wall band.');
