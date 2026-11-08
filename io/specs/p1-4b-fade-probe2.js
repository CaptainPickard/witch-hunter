// P1-4b Testerbot probe v2 (io/specs/p1-4b-occluder-fade-valspec.md V-32..V-35).
// Loads CONFIG.js + region-defs.js + region-manager.js under node with a
// PINNED stub meta; for every WH_REGION_DEFS region prints the projected
// propColliders table (PRE-CHANGE fields) PLUS the veg-classification and
// fadeSeed values DERIVED EXACTLY the way P1-4b must derive them (the
// COLLIDER name-law regex, verbatim from the pre-change source; the
// fadeSeed integer-HashMix law from the IO spec 4) -- so the same script
// diffs clean against post build iff Devbot's law matches.
// Run: node io/specs/p1-4b-fade-probe2.js > out.json
// Values come from the pinned stub meta, the same stub on both runs, so
// the diff is an exact identity check. No git, no network, no npm.
'use strict';
global.window = global;
var LOGS = [];
console.log = function () {
  LOGS.push(Array.prototype.map.call(arguments, String).join(' '));
};
function M() { return { multiplyMatrices: function () {}, invert: function () { return M(); } }; }
global.THREE = {
  Matrix4: M,
  Group: function () { return { add: function () {}, traverse: function () {}, name: '' }; },
  Vector3: function () { return {}; },
  Color: function () { return {}; },
  InstancedMesh: function () { return {}; }
};
window.WH_ASSETS = {
  getMeta: function () { return { height: 6, width: 2, groundMinY: 0 }; },
  instance: function () { return {}; },
  getTemplate: function () { return null; }
};
// No terrain in node: window.WH_GROUND stays undefined, so fy == 0 everywhere.
require('/tmp/wh-worldfeat/prototype/js/CONFIG.js');
require('/tmp/wh-worldfeat/prototype/js/region-defs.js');
require('/tmp/wh-worldfeat/prototype/js/region-manager.js');

var DEFS = window.WH_REGION_DEFS;
var rm = new window.WH_RegionManager({ add: function () {}, remove: function () {} });

// THE COLLIDER name law, copied verbatim from the pre-change source
// (region-manager.js colliderRadius; the same classification whOccluderH
// runs). Devbot must classify fade BY COLLIDER LAW, not by a new list.
function isVegName(name) {
  return /tree|oak|birch|sapling|bush|bramble|fern|shrub|stump/i.test(name);
}

// IO spec 4): seed = row.index mixed with row.name, 0..1, exact steps:
// h0 = 2166136261; for each code unit: h = h XOR code; h = Math.imul(h, 16777619) >>> 0;
// h = h >>> 15; h = Math.imul(h, 2246822519) >>> 0; h = Math.imul(h, 3266489917) >>> 0;
// h = h ^ (h >>> 13); return (h >>> 0) / 4294967295.
function fadeSeed(row) {
  var h0 = 2166136261;
  var s = String(row.index) + '|' + String(row.name);
  var h = h0;
  for (var i = 0; i < s.length; i++) {
    h = h ^ s.charCodeAt(i);
    h = Math.imul(h, 16777619) >>> 0;
  }
  h = h >>> 15;
  h = Math.imul(h, 2246822519) >>> 0;
  h = Math.imul(h, 3266489917) >>> 0;
  h = h ^ (h >>> 13);
  return (h >>> 0) / 4294967295;
}

function projRows(rows) {
  return rows.map(function (c) {
    var veg = isVegName(c.name) ? 1 : 0;
    return { index: c.index, name: c.name, x: c.x, z: c.z, r: c.r, h: c.h === undefined ? null : c.h, fy: c.fy === undefined ? null : c.fy, veg: veg, fadeSeed: fadeSeed(c) };
  });
}

var out = { probe: 'p1-4b-fade-probe2', regions: {}, plans: {} };
Object.keys(DEFS.regions).forEach(function (rid) {
  var t = rm.propColliders(rid);
  var plan = rm.scatterPlan(rid);
  out.regions[rid] = {
    complete: t.complete === true,
    circles: projRows(t.circles),
    exempt: projRows(t.exempt),
    scatterStats: plan.stats
  };
});
var wp = rm.wallPlan();
out.plans.wall = { complete: wp.complete === true, colliderCount: wp.colliders.length, stats: wp.stats };

process.stdout.write(JSON.stringify(out, null, 1) + '\n');
if (process.argv[2] === 'logs') process.stderr.write(LOGS.join('\n') + '\n');
