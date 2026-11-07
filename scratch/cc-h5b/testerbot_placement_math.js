// Testerbot-independent placement math (CC-H5b) — re-derives every B1 floor
// from the live CONFIG tables at RUNTIME TRUTH widths, mirroring the engine's
// colliderRadius (region-manager.js:366-374) + whMeetsCorridor (347-354).
// Reads NOTHING from the IO probe; the WIDTH array below is reproduced from
// the GLB file-space x-extents Testerbot measured independently
// (scratch/cc-h5b/testerbot_glb_xextents.py, printed to 3 decimals).
global.window = {};
eval(require('fs').readFileSync('/tmp/wh-worldfeat/prototype/js/CONFIG.js', 'utf8'));
eval(require('fs').readFileSync('/tmp/wh-worldfeat/prototype/js/region-defs.js', 'utf8'));
var CFG = window.WH_CONFIG, K = CFG.regionK;
var vents = K.hazards.vents;
var props = K.props.filter(function (p) { return p.asset && !p.wall && !p.noCollide && !(p.y > 0.1); });
var enemies = K.enemies || [];
var lair = (K.lairs || [])[0];

// ---- testerbot-measured widths (independent of IO's table; matches to 3 dp) ----
var WIDTHS = {
  mourningStatue: 1.862, okRuinColumn: 0.957, stoneSteps: 1.948,
  skullPile: 2.0, lanternPost: 0.59, blightcap: 1.692, mossBoulder: 1.897
};
// ---- engine law: colliderRadius + TRUNK exclusion ----
var TRUNK_RATIO = 0.25;
var TRUNK_ASSETS = { livingOak:1, witchwoodTree:1, birchTree:1, deadTree:1, deadTree2:1,
  ancientOak:1, hangingTree:1, twistedSapling:1, thornbush:1, bramble:1, largeFern:1,
  deadShrub:1, mossyStump:1, hollowStump:1 };
function colliderRadius(name, width, scale) {
  var r = width * scale / 2;
  if (TRUNK_ASSETS[name] || /tree|oak|birch|sapling|bush|bramble|fern|shrub|stump/i.test(name)) return r * TRUNK_RATIO;
  return r;
}
function whMeetsCorridor(x, z, r) {
  var hw = CFG.chokepoint.width / 2;
  var hd = CFG.world.colliderCorridorHalfDepth;
  var nx = Math.max(CFG.chokepoint.centerX - hw, Math.min(CFG.chokepoint.centerX + hw, x));
  var nz = Math.max(CFG.boundary.z - hd, Math.min(CFG.boundary.z + hd, z));
  var dx = x - nx, dz = z - nz;
  return dx * dx + dz * dz <= r * r;
}
function dist(a, b) { return Math.hypot(a[0] - b[0], a[1] - b[1]); }

console.log('== TESTERBOT INDEPENDENT B1 MATH (runtime truth) ==');
console.log('chokepoint', JSON.stringify(CFG.chokepoint), 'colliderCorridorHalfDepth', CFG.world.colliderCorridorHalfDepth, 'boundary.z', CFG.boundary.z);
var F_RING=1.0, F_ENEMY=5.0, F_PROP=2.0, F_BOSS=6.0, F_LAND=4.0, F_WALKIN=2.5;
var RING_C=[0,-880], R=34, LAND=[0,-856], WALKIN=[0,-864], DISC=34;
var BLAST = K.hazards.blastRadiusM, IDLE = K.hazards.idleSec, WARN = K.hazards.warnSec;
var allPass = true;
vents.forEach(function (v, i) {
  var seat = [v.x, v.z];
  var ringEdge = Math.abs(dist(seat, RING_C) - R);
  var e = Math.min.apply(null, enemies.map(function (en) { return dist(seat, [en.x, en.z]); }));
  var worst = null, exempt = [];
  props.forEach(function (p) {
    var r = colliderRadius(p.asset, WIDTHS[p.asset], p.scale || 1.0);
    if (whMeetsCorridor(p.x, p.z, r)) { exempt.push(p.asset + '@(' + p.x + ',' + p.z + ') r=' + r.toFixed(2)); return; }
    var clear = dist(seat, [p.x, p.z]) - r;
    if (!worst || clear < worst[0]) worst = [clear, p.asset, p.x, p.z, r];
  });
  var b = dist(seat, [lair.x, lair.z]);
  var land = dist(seat, LAND), walkin = dist(seat, WALKIN);
  var inDisc = dist(seat, RING_C) <= DISC;
  var oks = [
    ['ringEdge>=1.0', ringEdge - F_RING], ['enemy>=5.0', e - F_ENEMY],
    ['propEdge>=2.0', worst[0] - F_PROP], ['boss>=6.0', b - F_BOSS],
    ['land>=4.0', land - F_LAND], ['walkin>=2.5', walkin - F_WALKIN],
  ];
  var fails = oks.filter(function (o) { return o[1] < 0; });
  if (fails.length || !inDisc) allPass = false;
  console.log('vent ' + i + ' @(' + v.x + ',' + v.z + '): ringEdge ' + ringEdge.toFixed(2) +
    ' | enemy ' + e.toFixed(2) + ' | propEdge ' + worst[0].toFixed(2) + ' (' + worst[1] + ' r=' + worst[4].toFixed(3) + ')' +
    ' | boss ' + b.toFixed(2) + ' | land ' + land.toFixed(2) + ' | walkin ' + walkin.toFixed(2) +
    ' | inDisc ' + inDisc + (fails.length ? '  FAILS: ' + JSON.stringify(fails.map(function (f) { return f[0]; })) : '  ALL CLEAR'));
  if (exempt.length) console.log('   corridor-exempt at seat distance check: ' + exempt.join(', '));
});

// corridor-cycle: 2-D band overlap + walker timing
console.log('== corridor-cycle (2-D clamp) ==');
var CORR_X = 2.2, Z0 = -880, Z1 = -856;
vents.forEach(function (v, i) {
  var ovx = (v.x - BLAST) < CORR_X && (v.x + BLAST) > -CORR_X;
  var ovz = (v.z + BLAST) >= Z0 && (v.z - BLAST) <= Z1;
  console.log('vent ' + i + ': overlap_x=' + ovx + ' overlap_z=' + ovz + ' => band_overlapped=' + (ovx && ovz) + ' (x-gap ' + Math.max(0, Math.abs(v.x) - BLAST - CORR_X).toFixed(2) + ' m)');
});
var walkT = (Z1 - Z0) / (CFG.player.walkSpeed || 6);
var firstBlast = 0 * 1.3 + IDLE + WARN;
console.log('walker exits band t=' + walkT.toFixed(2) + ' s; first blast window opens t>=' + firstBlast.toFixed(2) + ' s -> ' + (walkT <= firstBlast ? 'CLEAR' : 'VIOLATION'));

// amendment-necessity check at runtime truth (original spec seat)
console.log('== amendment necessity (original seat 2 (-6.0,-894) vs statue (-6,-896)) ==');
var w = WIDTHS.mourningStatue * 1.0; var r = colliderRadius('mourningStatue', w, 1.0);
var d = dist([-6,-894],[-6,-896]) - r;
console.log('original seat edge distance to statue: ' + d.toFixed(3) + ' m (floor 2.0) -> ' + (d < 2.0 ? 'BREACH at truth — amendment necessary' : 'clear'));

// P2 spawn walk-in lane: does the LANE (x in [-2.2,2.2] band) intersect a lethal disc at rest?
console.log('== walk-in lane vs lethal discs (engine corridor law, circles r2) ==');
vents.forEach(function (v, i) {
  var nx = Math.max(-CORR_X, Math.min(CORR_X, v.x));
  var nz = Math.max(Z0, Math.min(Z1, v.z));
  var inside = dist([v.x,v.z],[nx,nz]) <= BLAST;
  console.log('vent ' + i + ': nearest lane point dist=' + dist([v.x,v.z],[nx,nz]).toFixed(2) + ' r=' + BLAST + ' -> lethal circle reaches lane: ' + inside);
});
console.log(allPass ? 'TESTERBOT MATH: ALL B1 FLOORS CLEAR' : 'TESTERBOT MATH: FAILURES PRESENT');
