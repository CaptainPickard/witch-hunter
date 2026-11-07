// CC-WB3 Devbot smoke harness: mirrors scratch/cc-wb2/wb2_harness.js's shape
// (THREE shim with retained ctor args + fake game + fake inventory) against
// the CC-WB3 harness contract (window/document stub, real CONFIG, WH_StrataEffort,
// capture appends + deeds, reloadModule IIFE freshness).
'use strict';
var out = [];
function check(name, cond, detail) {
  out.push((cond ? 'PASS' : 'FAIL') + ' ' + name + (cond ? '' : (' :: ' + (detail === undefined ? '' : detail))));
  if (!cond) FAILS.push(name);
  return cond;
}
var FAILS = [];

// ---- THREE shim (mesh/group/material with retained args for censuses) ----
function FakeMesh(geo, mat) {
  this.geometry = geo; this.material = mat;
  this.position = { x: 0, y: 0, z: 0, set: function (x, y, z) { this.x = x; this.y = y; this.z = z; } };
  this.rotation = { x: 0, y: 0, z: 0 };
  this.visible = true;
}
FakeMesh.prototype.clone = function () {
  var c = new FakeMesh(this.geometry, this.material);
  c.position = { x: 0, y: 0, z: 0, set: function (x, y, z) { this.x = x; this.y = y; this.z = z; } };
  c.rotation = { x: 0, y: 0, z: 0 };
  c.visible = this.visible;
  return c;
};
function FakeBoxGeometry(w, h, d) { this.type = 'Box'; this.parameters = { width: w, height: h, depth: d }; }
function FakePlaneGeometry(w, h) { this.type = 'Plane'; this.parameters = { width: w, height: h }; }
function FakeGroup() { this.children = []; this.name = ''; this.type = 'Group';
  var self = this;
  this.position = { x: 0, y: 0, z: 0, set: function (x, y, z) { self.position.x = x; self.position.y = y; self.position.z = z; } };
  this.rotation = { x: 0, y: 0, z: 0 };
}
FakeGroup.prototype.add = function () { for (var i = 0; i < arguments.length; i++) this.children.push(arguments[i]); };
FakeGroup.prototype.getObjectByName = function (n) {
  for (var i = 0; i < this.children.length; i++) {
    var c = this.children[i];
    if (c && c.name === n) return c;
    if (c && typeof c.getObjectByName === 'function') { var d = c.getObjectByName(n); if (d) return d; }
  }
  return null;
};
var THREE = {
  DoubleSide: 2,
  Group: FakeGroup,
  Mesh: FakeMesh,
  BoxGeometry: FakeBoxGeometry,
  PlaneGeometry: FakePlaneGeometry,
  MeshStandardMaterial: function (o) {
    this.color = (o && o.color) || null;
    this.emissive = (o && o.emissive) || null;
    this.emissiveIntensity = (o && o.emissiveIntensity) || 0;
    this.roughness = (o && o.roughness) || 0;
    this.metalness = (o && o.metalness) || 0;
    this.side = (o && o.side) || 0;
  }
};
THREE.Color = function (c) { this.hex = c; };

// Headless shims: the target files are browser IIFEs keyed on window.*.
global.window = global;
global.document = { createElement: function (t) { return { tag: t, className: '', textContent: '' }; } };
global.THREE = THREE;

// ---- CONFIG (real file) ----
require('/tmp/wh-worldfeat/prototype/js/CONFIG.js');
var CFG = global.window.WH_CONFIG;

// ---- strata module (real file) ----
require('/tmp/wh-worldfeat/prototype/js/strataeffort.js');
var W = global.window.WH_StrataEffort;

// ---- inventory facade (WB1 smoke shape: stack cap 60, multi-stack) ----
function FakeInv() { this.slots = []; }
FakeInv.prototype.countOf = function (id) {
  return this.slots.reduce(function (n, s) { return n + (s && s.id === id ? s.count : 0); }, 0);
};
FakeInv.prototype.addItem = function (id, count) {
  var left = count, cap = 60;
  for (var i = 0; i < this.slots.length && left > 0; i++) {
    var s = this.slots[i];
    if (!s || s.id !== id || s.count >= cap) continue;
    var room = Math.min(cap - s.count, left); s.count += room; left -= room;
  }
  var start = this.slots.length;
  for (var j = 0; j < start && left > 0; j++) {
    if (this.slots[j]) continue;
    var room2 = Math.min(cap, left); this.slots[j] = { id: id, count: room2 }; left -= room2;
  }
  while (left > 0) { var room3 = Math.min(cap, left); this.slots.push({ id: id, count: room3 }); left -= room3; }
  return count - left;
};
FakeInv.prototype.removeItem = function (id, count) {
  var left = count;
  for (var i = this.slots.length - 1; i >= 0 && left > 0; i--) {
    var s = this.slots[i];
    if (!s || s.id !== id) continue;
    var take = Math.min(s.count, left); s.count -= take; left -= take;
    if (s.count <= 0) this.slots[i] = null;
  }
  return count - left;
};

function FakeScene() { this.children = []; }
FakeScene.prototype.add = function (o) { this.children.push(o); };

// Fresh fake game per test: WB1 smoke shape at the CC-WB3 seat (region G,
// x 6.0 z -782.0). opts: { scene: false } = game.scene === null (headless),
// { day: n } sets the day clock (default 0).
function freshGame(opts) {
  var o = opts || {};
  var inv = new FakeInv();
  var toasts = [];
  var scene = (o.scene === false) ? null : new FakeScene();
  var appends = [], deeds = [];
  global.window.WH_JOURNAL = {
    append: function (id, title, body, day, source) { appends.push({ id: id, title: title, body: body, day: day, source: source }); }
  };
  global.window.WH_AFF = {
    deed: function (id, times) { deeds.push({ id: id, times: times }); }
  };
  var g = {
    dayNight: { day: (typeof o.day === 'number') ? o.day : 0 },
    regionManager: { logic: { activeId: 'lords_hold' } },
    player: { state: 'alive', inputSuspended: false, pos: { x: 6.0, z: -782.0 } },
    inventory: inv,
    scene: scene,
    inventoryUI: { toast: function (t) { toasts.push(t); } }
  };
  return { game: g, inv: inv, toasts: toasts, scene: scene, appends: appends, deeds: deeds };
}

// Full reset of module state between tests: cache-clear + re-require so the
// IIFE re-runs (fresh logic closure per test) — wb2_harness reloadModule shape.
function reloadModule() {
  delete require.cache[require.resolve('/tmp/wh-worldfeat/prototype/js/strataeffort.js')];
  require('/tmp/wh-worldfeat/prototype/js/strataeffort.js');
  return global.window.WH_StrataEffort;
}

module.exports = {
  out: out, check: check, FAILS: FAILS,
  THREE: THREE, CFG: CFG, W: W,
  FakeInv: FakeInv, FakeScene: FakeScene, freshGame: freshGame,
  reloadModule: reloadModule
};
