// P1-4b Testerbot probe (io/specs/p1-4b-occluder-fade-valspec.md V-10 / V-23).
// Dumps the collider tables of EVERY region in WH_REGION_DEFS to stdout as one
// JSON document, projected onto the PRE-CHANGE row fields
// (index,name,x,z,r,h,fy) so a pre-change baseline and a post-change run diff
// byte-for-byte when row identity and order are preserved. New fields
// (veg/fadeSeed) added by P1-4b are invisible to the diff on purpose — they
// are verified by V-8/V-9 greps, not here. Values (r/h) come from the STUB
// getMeta below (GLB meta is a game-runtime artifact and is not reproducible
// in node); the same stub is used on both runs, which is what makes the diff
// an exact identity check. Run: node io/specs/p1-4b-fade-probe.js > out.json
// No git, no network, no npm, no browser. Read-only on the repo.
'use strict';
global.window = global;

// Engine console logs ([WH scatter]/[WH wall]) are captured, not printed:
// stdout must be ONLY the JSON (process.argv[2] = 'logs' prints them after).
var LOGS = [];
console.log = function () {
  LOGS.push(Array.prototype.map.call(arguments, String).join(' '));
};

// Static THREE stub: enough for region-manager to load; whBuildInstanced is
// never called on this path (no mesh builds happen in the probe).
function M() { return { multiplyMatrices: function () {}, invert: function () { return M(); } }; }
global.THREE = {
  Matrix4: M,
  Group: function () { return { add: function () {}, traverse: function () {}, name: '' }; },
  Vector3: function () { return {}; },
  Color: function () { return {}; },
  InstancedMesh: function () { return {}; }
};

// PINNED stub meta (do not edit between baseline and post runs):
// height 6, width 2 for every asset; vegetation trunks then compute
// r = 2*scale/2*0.25, h = 6*scale*0.45; mass rows r = scale, h = 6*scale.
window.WH_ASSETS = {
  getMeta: function () { return { height: 6, width: 2, groundMinY: 0 }; },
  instance: function () { return {}; },
  getTemplate: function () { return null; }
};
// No terrain in node: window.WH_GROUND stays undefined, so fy == 0 for every
// row in the probe. Same on both runs.

require('/tmp/wh-worldfeat/prototype/js/CONFIG.js');
require('/tmp/wh-worldfeat/prototype/js/region-defs.js');
require('/tmp/wh-worldfeat/prototype/js/region-manager.js');

var DEFS = window.WH_REGION_DEFS;
var rm = new window.WH_RegionManager({ add: function () {}, remove: function () {} });

function projRows(rows) {
  return rows.map(function (c) {
    return { index: c.index, name: c.name, x: c.x, z: c.z, r: c.r, h: c.h === undefined ? null : c.h, fy: c.fy === undefined ? null : c.fy };
  });
}

var out = { probe: 'p1-4b-fade-probe', regions: {}, plans: {} };
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
out.plans.wall = {
  complete: wp.complete === true,
  colliderCount: wp.colliders.length,
  stats: wp.stats
};

process.stdout.write(JSON.stringify(out, null, 1) + '\n');
if (process.argv[2] === 'logs') {
  process.stderr.write(LOGS.join('\n') + '\n');
}
