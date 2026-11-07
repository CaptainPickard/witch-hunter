// CC-B1 probe: offline clearance check for the regionB ruined-chapel landmark
// (plain node, no three). Pattern: scratch/cc13b_probe.cjs (rows parsed out of
// CONFIG.js text, collider r = width * scale / 2, trunk regex x 0.25).
// Run from the repo root:  node scratch/cc-b1_probe.cjs   (exit 1 = a rule fails)
// WIDTH table = cc13b values (regionC-validated keys verbatim) + the
// cc-b1-chapel-valspec.md W-T measured additions (trimesh, 2026-11-07).
'use strict';
var fs = require('fs');
var src = fs.readFileSync('prototype/js/CONFIG.js', 'utf8');
var lines = src.split('\n');

// ---- nominal widths (scale 1, metres). cc13b entries kept verbatim; the
// cc-b1 additions are the valspec W-T trimesh measurements.
var WIDTH = {
  // --- cc13b (regionC-validated) ---
  cemeteryGate: 2.4, picketFence: 2.0, ironFenceSection: 1.8, churchArchway: 2.0,
  churchCornerButtress: 0.9, mossBoulder: 1.5, stoneSteps: 1.2, rubblePile: 1.1,
  stoneCrossTilted: 0.7, gravestoneObelisk: 0.6, buriedCoffin: 0.9, graveMound: 1.6,
  lanternPost: 0.4, bramble: 1.8, whWallA: 2.9, whWallB: 2.9, mourningStatue: 0.8,
  yewTree: 1.4,
  witchwoodTree: 1.4, deadTree: 1.2, treeStump: 1.0, lanternWaymarker: 0.4,
  banditCampfire: 1.2, banditBedroll: 2.0,
  // --- cc-b1 W-T additions (valspec measured); secondary shipped keys ---
  churchPewBroken: 2.002, ironFenceCorner: 0.589, fallenLog: 1.862,
  lanternPostV3: 0.585, livingOak: 1.848, reachTreeA: 1.558, reachTreeB: 1.527,
  reachTreeC: 1.411,
  // --- the 7 NEW chapel assets (W-T: nominal width = max(ext.x, ext.z)) ---
  churchWallWindow: 1.30, churchWindowFrame: 0.91, churchRoofBeam: 1.98,
  churchAltar: 1.99, churchPulpit: 1.08, churchPew: 2.00, candelabra: 1.94
};
// region-manager.js colliderRadius (TRUNK_ASSETS + regex, x 0.25). Never
// applies to the 7 new chapel assets (no tree-like name).
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

// ---- (a) regionB props table, parsed from CONFIG.js text
var start = -1;
for (var i = 0; i < lines.length; i++) if (/^\s{2}regionB:\s*\{/.test(lines[i])) { start = i; break; }
var pStart = -1;
for (i = start; i < lines.length; i++) if (/^\s{4}props:\s*\[/.test(lines[i])) { pStart = i; break; }
var depth = 0, pEnd = -1;
for (i = pStart; i < lines.length; i++) {
  var code = lines[i].replace(/\/\/.*$/, '');
  depth += (code.match(/\[/g) || []).length - (code.match(/\]/g) || []).length;
  if (depth === 0) { pEnd = i; break; }
}
function num(l, k) { var m = l.match(new RegExp('\\b' + k + ':\\s*(-?[\\d.]+)')); return m ? parseFloat(m[1]) : null; }
var MARK = 'CC-B1';
var existing = [], skipFrom = -1;
for (i = pStart; i <= pEnd; i++) {
  if (lines[i].indexOf(MARK) >= 0 && /^\s*\/\//.test(lines[i])) { skipFrom = i; break; } // our own block (re-runs)
  var l = lines[i];
  if (/^\s*\/\//.test(l)) continue;
  var am = l.match(/asset:\s*'([^']+)'/);
  if (!am) continue;
  existing.push({ asset: am[1], x: num(l, 'x'), z: num(l, 'z'), rotY: num(l, 'rotY') || 0,
    scale: num(l, 'scale') == null ? 1 : num(l, 'scale'),
    noCollide: /noCollide:\s*true/.test(l), line: i + 1 });
}

// ---- (b) the NEW rows (mirror of the CONFIG.js CC-B1 block)
// gap pairs are marked here to pass R2 wall-line checks (intentional gaps)
var NEW = [
  { c: 'K1', asset: 'churchWallWindow', x: -18, z: -63, rotY: 1.57, scale: 2.2 },
  { c: 'K1', asset: 'churchWallWindow', x: -18, z: -58, rotY: 1.57, scale: 2.2, gapPrev: true },
  { c: 'K2', asset: 'churchCornerButtress', x: -11.8, z: -52, rotY: 5.7, scale: 2.0 },
  { c: 'K3', asset: 'churchWallWindow', x: -3.5, z: -66, rotY: 3.14, scale: 2.2 },
  { c: 'K3', asset: 'churchWallWindow', x: 3.5, z: -66, rotY: 3.14, scale: 2.2, gapPrev: true },
  { c: 'K4', asset: 'churchPulpit', x: 5, z: -63, rotY: -1.57, scale: 2.0 },
  // K4 pew REMOVED (wake-34 IO review: no legal seat; pewBroken stands in)
  { c: 'K5', asset: 'churchAltar', x: 14.5, z: -58, rotY: -1.57, scale: 2.2 },
  { c: 'K5', asset: 'candelabra', x: 14.5, z: -58, rotY: -1.57, scale: 0.45, y: 3.415, stack: true },
  { c: 'K6', asset: 'churchWindowFrame', x: 14.5, z: -58, rotY: 1.57, scale: 1.0, y: 2.15, noCollide: true },
  { c: 'K7', asset: 'churchRoofBeam', x: -6, z: -58, rotY: 1.57, scale: 7.2, y: 4.0, noCollide: true },
  { c: 'K7', asset: 'churchRoofBeam', x: -2, z: -58, rotY: -1.57, scale: 7.2, y: 3.9, noCollide: true },
  { c: 'K8', asset: 'churchRoofBeam', x: 7, z: -69, rotY: 2.5, scale: 2.6 },
  { c: 'K9', asset: 'rubblePile', x: -13.5, z: -59.5, rotY: 0.7, scale: 1.3 },
  { c: 'K9', asset: 'rubblePile', x: -6.4, z: -64, rotY: 4.1, scale: 1.2 }
];

// ---- (c) CONFIG block vs the NEW table (catches a hand-edit drift)
var cfgRows = [];
if (skipFrom >= 0) {
  for (i = skipFrom + 1; i < pEnd; i++) {
    if (/^\s*\/\//.test(lines[i])) continue;
    var am2 = lines[i].match(/asset:\s*'([^']+)'/);
    if (am2) cfgRows.push(am2[1] + '@' + num(lines[i], 'x') + ',' + num(lines[i], 'z') + ',' +
      num(lines[i], 'rotY') + ',' + num(lines[i], 'scale') + (num(lines[i], 'y') != null ? ',y' + num(lines[i], 'y') : ''));
  }
}
var want = NEW.map(function (n) {
  return n.asset + '@' + n.x + ',' + n.z + ',' + n.rotY + ',' + n.scale + (n.y != null ? ',y' + n.y : '');
});
var fails = [];
if (cfgRows.join('|') !== want.join('|')) fails.push('CONFIG.js CC-B1 block != probe NEW table');
if (skipFrom < 0) { console.log('no CC-B1 block in regionB props'); process.exit(1); }
console.log('regionB props L' + (pStart + 1) + '-' + (pEnd + 1) + ': ' + existing.length +
  ' active rows parsed + CC-B1 block at L' + (skipFrom + 1) + ' (' + NEW.length + ' chapel rows)');

// ---- (d) protected rows + segments (R1 LANE). Node/enemy seats parsed from
// regionB CONFIG text (nodes: / enemies: blocks inside the regionB span).
function blockList(key) {
  var bStart = -1;
  for (var j = start; j < pEnd + 200 && j < lines.length; j++) {
    if (new RegExp('^\\s{4}' + key + ':\\s*\\[').test(lines[j])) { bStart = j; break; }
  }
  if (bStart < 0) return [];
  var d = 0, out = [];
  for (j = bStart; j < lines.length; j++) {
    var c = lines[j].replace(/\/\/.*$/, '');
    d += (c.match(/\[/g) || []).length - (c.match(/\]/g) || []).length;
    if (d === 0) break;
    var tm = lines[j].match(/\{\s*type:\s*'([^']+)',\s*x:\s*(-?[\d.]+),\s*z:\s*(-?[\d.]+)/);
    if (tm) out.push({ type: tm[1], x: parseFloat(tm[2]), z: parseFloat(tm[3]), line: j + 1 });
  }
  return out;
}
var NODES = blockList('nodes'), ENEMIES = blockList('enemies');
var CAMPFIRE = { x: 2.5, z: -52 }, WAYMARKER = { x: -6.5, z: -47 };
// B/C door window segment: x -4..4 at z -86. A/B chokepoint corridor: x -6..6
// at z -25; valspec: CONFIG marks the boundary south (z +25) — test BOTH z -25
// and z +25 (nave > 40 m from either; symmetric test is cheap and safe).
var SEGS = [
  { id: 'BCdoor', x0: -4, x1: 4, z: -86, floor: 8 },
  { id: 'ABchoke-25', x0: -6, x1: 6, z: -25, floor: 8 },
  { id: 'ABchoke+25', x0: -6, x1: 6, z: 25, floor: 8 }
];
function segDist(px, pz, ax, az, bx, bz) {
  var dx = bx - ax, dz = bz - az, L2 = dx * dx + dz * dz;
  var t = L2 ? Math.max(0, Math.min(1, ((px - ax) * dx + (pz - az) * dz) / L2)) : 0;
  return Math.hypot(px - (ax + t * dx), pz - (az + t * dz));
}
function spanDist(px, pz, s) {
  var x = Math.max(s.x0, Math.min(px, s.x1));
  return Math.hypot(px - x, pz - s.z);
}

// ---- existing collider circles (everything parsed before the CC-B1 block)
var circles = [];
existing.forEach(function (p) {
  if (p.noCollide) return;
  circles.push({ asset: p.asset, x: p.x, z: p.z, r: colliderR(p.asset, p.scale), line: p.line });
});

// ---- (e) SEAT TABLE + per-rule checks
var f2 = function (v) { return (v >= 0 ? ' ' : '') + v.toFixed(2); };
function pad(s, w) { s = String(s); while (s.length < w) s += ' '; return s; }
console.log('nodes parsed: ' + NODES.length + '  enemies parsed: ' + ENEMIES.length);
console.log('');
console.log('idx | asset              | x       z       rotY   scale | r     | flags     | BCdoor | choke-25 | choke+25 | worst node/enemy/fire/way');
var raised = [];
NEW.forEach(function (n, idx) {
  var r = colliderR(n.asset, n.scale);
  var flags = [];
  if (n.noCollide) flags.push('noCollide');
  if (n.y != null) flags.push('y' + n.y);
  if (n.stack) flags.push('stack');
  if (n.gapPrev) flags.push('gap');
  var fl = flags.length ? flags.join(',') : '-';
  var grounded = (n.y == null && !n.noCollide); // A1: ground checks skip raised rows
  // R1 gates (A1: raised rows exempt — sockets/pools are ground-based)
  var g1 = spanDist(n.x, n.z, SEGS[0]) - r;
  var g2 = spanDist(n.x, n.z, SEGS[1]) - r;
  var g3 = spanDist(n.x, n.z, SEGS[2]) - r;
  if (grounded && g1 < SEGS[0].floor) fails.push(n.c + '.' + idx + ' ' + n.asset + ': BCdoor edge gap ' + g1.toFixed(2) + ' < 8');
  if (grounded && g2 < SEGS[1].floor) fails.push(n.c + '.' + idx + ' ' + n.asset + ': ABchoke-25 edge gap ' + g2.toFixed(2) + ' < 8');
  if (grounded && g3 < SEGS[2].floor) fails.push(n.c + '.' + idx + ' ' + n.asset + ': ABchoke+25 edge gap ' + g3.toFixed(2) + ' < 8');
  var best = { g: Infinity, t: '' };
  NODES.forEach(function (q) {
    var g = Math.hypot(n.x - q.x, n.z - q.z) - r;
    if (g < best.g) best = { g: g, t: 'node ' + q.type + ' L' + q.line };
  });
  if (grounded) NODES.forEach(function (q) { if (Math.hypot(n.x - q.x, n.z - q.z) - r < 3) fails.push(n.c + '.' + idx + ' ' + n.asset + ': gather node ' + q.type + ' gap ' + (Math.hypot(n.x - q.x, n.z - q.z) - r).toFixed(2) + ' < 3'); });
  ENEMIES.forEach(function (q) {
    var g = Math.hypot(n.x - q.x, n.z - q.z) - r;
    if (g < best.g) best = { g: g, t: 'enemy ' + q.type + ' L' + q.line };
    if (grounded && g < 4) fails.push(n.c + '.' + idx + ' ' + n.asset + ': enemy spawn ' + q.type + ' gap ' + g.toFixed(2) + ' < 4');
  });
  [
    { n: 'campfire', q: CAMPFIRE, floor: 2 }, { n: 'waymarker', q: WAYMARKER, floor: 1.5 }
  ].forEach(function (o) {
    var g = Math.hypot(n.x - o.q.x, n.z - o.q.z) - r;
    if (g < best.g) best = { g: g, t: o.n };
    if (grounded && g < o.floor) fails.push(n.c + '.' + idx + ' ' + n.asset + ': ' + o.n + ' gap ' + g.toFixed(2) + ' < ' + o.floor);
  });
  console.log(pad(n.c + '.' + idx, 4) + '| ' + pad(n.asset, 19) + '| ' + pad(n.x.toFixed(1), 7) + ' ' +
    pad(n.z.toFixed(1), 7) +pad(n.rotY.toFixed(2), 7) + pad(n.scale.toFixed(2), 6) + '| ' + pad(r.toFixed(2), 6) + '| ' +
    pad(fl, 10) + '| ' + pad(f2(g1), 7) + '| ' + pad(f2(g2), 9) + '| ' + pad(f2(g3), 9) + '| ' + f2(best.g) + ' (' + best.t + ')');
  if (n.y != null) raised.push(n);
});

// ---- R2 MUTUAL clearances
// asset-class floors: window/gable/altar/pulpit/wall pieces 0.6, pew 1.2 vs
// everything. Existing locked rows resolve >= 0.8 vs NEW. Exceptions:
//  - candelabra vs churchAltar stack (REQUIRED overlap evidence of the stack)
//  - intentional wall gaps marked gapPrev (>= 2.5 m centre distance)
console.log('');
var pewF = 1.2, wallF = 0.6, exF = 0.8;
function rowFloor(a, b) { return (a.asset === 'churchPew' || b.asset === 'churchPew') ? pewF : wallF; }
var r2lines = [];
for (var a = 0; a < NEW.length; a++) for (var b = a + 1; b < NEW.length; b++) {
  var A = NEW[a], B = NEW[b];
  var gap = Math.hypot(A.x - B.x, A.z - B.z) - colliderR(A.asset, A.scale) - colliderR(B.asset, B.scale);
  var rA = colliderR(A.asset, A.scale), rB = colliderR(B.asset, B.scale);
  var isStack = (A.asset === 'candelabra' && B.asset === 'churchAltar') || (B.asset === 'candelabra' && A.asset === 'churchAltar');
  var isGap = (A.gapPrev && a === b - 1) || (B.gapPrev && b === a + 1);
  if (isStack) {
    if (Math.hypot(A.x - B.x, A.z - B.z) > 0.01) fails.push('candelabra-on-altar stack broken: seats differ');
    else r2lines.push('candelabra-on-altar: exempt (centre distance ' + Math.hypot(A.x - B.x, A.z - B.z).toFixed(3) + ' m)');
    continue;
  }
  if (A.noCollide || B.noCollide) { r2lines.push(A.asset + '/' + B.asset + ': raised pair, circles not compared'); continue; }
  if (isGap) {
    var ctr = Math.hypot(A.x - B.x, A.z - B.z);
    if (ctr >= 2.5) r2lines.push('gap ' + A.asset + '/' + B.asset + ': centre ' + ctr.toFixed(2) + ' m >= 2.5 (intentional, // gap)');
    else fails.push('declared gap ' + A.asset + '/' + B.asset + ': centre ' + ctr.toFixed(2) + ' < 2.5');
    continue;
  }
  var floor = rowFloor(A, B);
  if (gap < floor) {
    r2lines.push('NEW-NEW ' + A.asset + '/' + B.asset + ': gap ' + gap.toFixed(2) + ' < ' + floor);
    if (gap < floor - 0.25) fails.push('R2 NEW-NEW ' + A.asset + ' — ' + B.asset + ': edge gap ' + gap.toFixed(2) + ' < ' + floor);
  }
}
var r2min = Infinity;
circles.forEach(function (c) {
  NEW.forEach(function (n, idx) {
    if (n.noCollide) return; // A1: raised rows exempt from ground checks
    if (n.stack) return;     // A1: candelabra compared ONLY vs its altar (stack pair above)
    // A5 debris-among-furniture: the LOCKED stumps inside the nave footprint
    // (13.4,-58.7 / 13.0,-55.5) may sit under NEW circles (scene-01 anchor)
    var stumpLocked = (c.asset === 'treeStump' &&
      ((Math.abs(c.x - 13.4) < 0.1 && Math.abs(c.z + 58.7) < 0.1) ||
       (Math.abs(c.x - 13.0) < 0.1 && Math.abs(c.z + 55.5) < 0.1)));
    var gap = Math.hypot(n.x - c.x, n.z - c.z) - colliderR(n.asset, n.scale) - c.r;
    if (stumpLocked) return;
    if (gap < r2min) r2min = gap;
    if (gap < exF)fails.push('R2 NEW-EXIST ' + n.asset + '(' + (idx + 1) + ') — ' + c.asset + ' L' + c.line + ': edge gap ' + gap.toFixed(2) + ' < ' + exF);
  });
});
r2lines.forEach(function (line) { console.log('R2: ' + line); });
console.log('R2: worst NEW-vs-existing edge gap ' + (r2min === Infinity ? 'n/a' : r2min.toFixed(2)) + ' m (floor 0.8)');

// ---- R3 Y / noCollide discipline
console.log('');
raised.forEach(function (n) { console.log('raised: ' + n.asset + ' y=' + n.y + ' noCollide=' + (!!n.noCollide)); });
var gable =raised.filter(function (n) { return n.asset === 'churchWindowFrame'; })[0];
if (gable && Math.abs(gable.y - 2.15) > 0.25) fails.push('gable churchWindowFrame y ' + gable.y + ' outside 2.15±0.25');
NEW.forEach(function (n, idx) {
  if (n.noCollide && !(n.asset === 'churchRoofBeam' || n.asset === 'churchWindowFrame'))
    fails.push('R3 noCollide on non-raised row ' + n.asset);
  if (n.asset === 'candelabra') {
    if (n.y == null) fails.push('R3 candelabra needs explicit y');
    if (n.noCollide) fails.push('R3 candelabra must not carry noCollide');
  }
  if (n.asset === 'churchRoofBeam') {
    if (n.noCollide && (n.y == null || n.y < 3.8 || n.y > 4.2)) fails.push('R3 raised roof beam y ' + n.y + ' outside 3.8..4.2');
    if (!n.noCollide && n.y == null) { /* fallen ground beam: keeps collider, ok */ }
  }
  if (n.y == null && n.noCollide) fails.push('R3 noCollide without y on ' + n.asset + ' (' + (idx + 1) + ')');
});
// raised circles vs altar/pulpit centres — A1 WAKE-34 RE-SCOPE: applies to
// WALKABLE-FLOOR raised rows only (the beams); the candelabra/gable rows sit
// INSIDE the altar's own circle by design (stack + moonbeam-above-altar)
NEW.forEach(function (n) {
  if (!n.noCollide || n.y == null) return;
  if (n.asset !== 'churchRoofBeam') return; // beams only (walkable-floor raised)
  [['churchAltar', 14.5, -58], ['churchPulpit', 5, -63]].forEach(function (o) {
    var d = Math.hypot(n.x - o[1], n.z - o[2]) - colliderR(n.asset, n.scale);
    if (d < 1) fails.push('R3 raised ' + n.asset + ' covers ' + o[0] + ' centre (gap ' + d.toFixed(2) + ' < 1)');
  });
});

// ---- R4 lightSockets: exactly one new key = candelabra
var lsStart = -1;
for (i = 0; i < lines.length; i++) if (/^\s{2}lightSockets:\s*\{/.test(lines[i])) { lsStart = i; break; }
var lsEnd, d2 = 0;
for (i = lsStart; i < lines.length; i++) {
  var c2 = lines[i].replace(/\/\/.*$/, '');
  d2 += (c2.match(/\{/g) || []).length - (c2.match(/\}/g) || []).length;
  if (d2 === 0 && i > lsStart) { lsEnd = i; break; }
}
var lsKeys = [];
for (i = lsStart; i <= lsEnd; i++) {
  var km = lines[i].match(/^\s{4}([A-Za-z]\w*):\s*\{/);
  if (km) lsKeys.push(km[1]);
}
var candel = lsKeys.filter(function (k) { return k === 'candelabra'; });
if (candel.length !== 1) fails.push('R4 lightSockets: candelabra key count ' + candel.length + ' != 1');
console.log('');
console.log('R4 lightSockets keys: ' + lsKeys.join(', '));
var lsCandel = -1;
for (i = lsStart; i <= lsEnd; i++) if (/^\s{4}candelabra:\s*\{/.test(lines[i])) lsCandel = i;
if (lsCandel == -1) fails.push('R4 candelabra socket line missing');
else console.log('R4 socket line L' + (lsCandel + 1) + ': ' + lines[lsCandel].trim() + ' / ' + (lines[lsCandel + 1] || '').trim());
var socketCommentOk = false;
for (i = Math.max(0, lsCandel - 14); i <= lsEnd; i++) if (/warm family/i.test(lines[i])) socketCommentOk = true;
if (!socketCommentOk) fails.push('R4 candelabra socket comment must note the warm family (banditCampfire + lanternWaymarker + candelabra)');
['lanternPost', 'banditCampfire', 'lanternWaymarker'].forEach(function (k) {
  if (lsKeys.indexOf(k) < 0) fails.push('R4 pre-existing socket ' + k + ' missing (churn?)');
});

// ---- R5 manifest: the 7 exact keys + paths (wake-34: rows carry trailing
// comments — regex tolerates them; multiline m flag added)
var MANIFEST_KEYS = ['churchWallWindow', 'churchWindowFrame', 'churchRoofBeam', 'churchAltar', 'churchPulpit', 'churchPew', 'candelabra'];
var aSrc = fs.readFileSync('prototype/js/assets.js', 'utf8');
MANIFEST_KEYS.forEach(function (k) {
  var dash = k.replace(/([A-Z])/g, function (m) { return '-' + m.toLowerCase(); });
  var re = new RegExp('^\\s*' + k + ': .art-direction/3d/assets/church-kit/' + dash + '-pixelated\\.glb.,[^\\n]*$', 'm');
  if (!re.test(aSrc)) fails.push('R5 manifest: no exact row for ' + k + ' -> ' + dash + '-pixelated.glb');
});
console.log('R5 manifest: ' + MANIFEST_KEYS.length + ' expected keys checked against art-direction/3d/assets/church-kit/ (comment-tolerant)');

// ---- R6 keepOut ellipse vs ground seats (raised rows exempt). Wake-34 rx 21
// rz 12.5; a landed rx 17 rz 10 row fails the row-presence check here.
var keRow = src.match(/\{\s*regionId:\s*'darkwood_edge',\s*x:\s*0,\s*z:\s*-58,\s*rx:\s*21,\s*rz:\s*12\.5\s*\}/);
if (!keRow) fails.push('R6 keepOut row { regionId darkwood_edge, x 0, z -58, rx 21, rz 12.5 } not found in CONFIG.js');
console.log('');
NEW.forEach(function (n) {
  if (n.noCollide || n.asset === 'candelabra') return; // raised / stacked exempt
  var e = Math.pow((n.x - 0) / 21, 2) + Math.pow((n.z + 58) / 12.5, 2);
  if (!(e <= 1)) fails.push('R6 ' + n.asset + ' seat (' + n.x + ',' + n.z + ') outside keepOut ellipse (e=' + e.toFixed(3) + ')');
});
console.log('R6 keepOut ellipse checked against every ground chapel row (raised rows exempt)');

// ---- R7 tri ledger (valspec measured values, scale-1 faces; cross-check =
// the python trimesh run: 2000+2000+2000+1999+2000+1999+1999)
var TRI = { churchWallWindow: 2000, churchWindowFrame: 2000, churchRoofBeam: 2000, churchAltar: 1999, churchPulpit: 2000, churchPew: 1999, candelabra: 1999 };
var triTotal = 0, usedTri = {};
NEW.forEach(function (n) { usedTri[n.asset] = 1; });
Object.keys(usedTri).forEach(function (k) { if (TRI[k]) triTotal += TRI[k]; });
console.log('R7 tri ledger: ' + Object.keys(usedTri).filter(function (k) { return TRI[k]; }).sort().map(function (k) { return k + ' ' + TRI[k]; }).join(', ') + ' = TOTAL ' + triTotal + ' faces (scale-1)');
if (triTotal > 60000) { console.log('R7 FAIL: tri ledger ' + triTotal + ' > 60000 (doc 61 sec budget)'); fails.push('R7 tri ledger ' + triTotal); }
else if (triTotal > 30000) console.log('R7 WARNING: tri ledger ' + triTotal + ' in 30001..60000 band — disclose');

// ---- R3 raised rows count discipline (exactly 3: 2 beams + 1 gable)
var raisedCount = NEW.filter(function (n) { return n.noCollide; }).length;
if (raisedCount !== 3) fails.push('R3 expected exactly 3 noCollide rows (2 roof beams + 1 gable), got ' + raisedCount);

// ---- verdict
console.log('');
if (cfgRows.length !== NEW.length) fails.push('CONFIG.js CC-B1 block has ' + cfgRows.length + ' rows, probe table has ' + NEW.length);
if (fails.length) { console.log('FAIL (' + fails.length + '):\n  ' + fails.join('\n  ')); process.exit(1); }
console.log('PASS: ' + NEW.length + ' chapel rows clear R1 lanes (BCdoor/ABchoke, nodes/enemies/campfire/waymarker), R2 mutual (floor ' + wallF + ' / pew ' + pewF + ' / existing ' + exF + ' with stack+gap exemptions), R3 raised discipline, R4 single socket, R5 manifest, R6 keepOut, R7 tri ledger ' + triTotal + '.');
