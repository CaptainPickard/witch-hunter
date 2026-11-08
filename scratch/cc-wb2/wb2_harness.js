// CC-WB2 Testerbot shared harness (loaded by every V-group one-shot).
// Node CommonJS; mirrors the landed /tmp/wb1_smoke.js shape (THREE shim +
// fake game + fake inventory). Lives OUTSIDE the worktree (law: the only
// worktree write is the verdict report).
'use strict';
var out = [];
function check(name, cond, detail) {
  out.push((cond ? 'PASS' : 'FAIL') + ' ' + name + (cond ? '' : (' :: ' + (detail === undefined ? '' : detail))));
  if (!cond) FAILS.push(name);
  return cond;
}
var FAILS = [];

// ---- THREE shim (mesh/group/material with retained args for census) ----
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
FakeGroup.prototype.remove = function (o) {
  var i = this.children.indexOf(o);
  if (i >= 0) this.children.splice(i, 1);
};
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
    this.color = (o && o.color) || ((THREE.Color && new THREE.Color(o ? o.color : 0)) || null);
    this.emissive = (o && o.emissive) || null;
    this.emissiveIntensity = (o && o.emissiveIntensity) || 0;
    this.roughness = (o && o.roughness) || 0;
    this.metalness = (o && o.metalness) || 0;
    this.side = (o && o.side) || 0;
  }
};
THREE.Color = function (c) { this.hex = c; };
THREE.MeshStandardMaterial.prototype = Object.create({});

// module.exports-less browser shim: the target files are browser IIFEs keyed
// on window.*; CONFIG.js assigns window.WH_CONFIG; wareffort.js assigns
// window.WH_WarEffort.
global.window = global;
global.THREE = THREE;

// ---- CONFIG (real file) ----
require('/tmp/wh-worldfeat/prototype/js/CONFIG.js');
var CFG = global.window.WH_CONFIG;

// ---- wareffort module (real file) ----
require('/tmp/wh-worldfeat/prototype/js/wareffort.js');
var W = global.window.WH_WarEffort;

// ---- inventory facade (/tmp/wb1_smoke.js shape: stack cap 60, multi-stack) ----
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

// Fresh fake game; W.init(game) each time the test needs a fresh board
function freshGame(coinsArr) {
  var inv = new FakeInv();
  var toasts = [];
  var scene = new FakeScene();
  var g = {
    dayNight: { day: 0 },
    regionManager: { logic: { activeId: 'hold_outskirts' } },
    player: { state: 'alive', inputSuspended: false, pos: { x: 5.9, z: -15.5 } },
    inventory: inv,
    scene: scene,
    inventoryUI: { toast: function (t) { toasts.push(t); } }
  };
  return { game: g, inv: inv, toasts: toasts, scene: scene };
}

// Full reset of module state between tests: re-require with cache clear so
// the IIFE re-runs (logic object + closure freshness per test).
function reloadModule() {
  delete require.cache[require.resolve('/tmp/wh-worldfeat/prototype/js/wareffort.js')];
  require('/tmp/wh-worldfeat/prototype/js/wareffort.js');
  return global.window.WH_WarEffort;
}

// Drive the board to a resolved turn-in at state (r = repeatIndex) with
// EXACTLY `ore` carried, then report coin delta + removal. Day must be set
// fresh so the spent-day law doesn't block: use a NEW day per attempt.
function driveTurnIn(r, ore, dayCounter, startDay) {
  // r = the repeatIndex the board SHOULD have before this turn-in
  // (r >= 0). We resolve one day at a time (WB1 day law) to grow repeatIndex.
  var t = freshGame();
  var g = t.game, inv = t.inv;
  var Wl = global.window.WH_WarEffort;
  Wl.init(g);
  var d = startDay;
  g.dayNight.day = d;
  // resolve chain: (r times) award, load quota, turn in -> repeatIndex = r
  for (var i = 0; i < r; i++) {
    Wl.tryOpen();                            // award paper
    Wl.tryOpen();                            // turn-in at the current quota (carrying quota ore added just below)
    // fill ore: quotaQ(r) >= 6..18, cap 60/stack
    var need = [6, 9, 14, 18][Math.min(i, 3)] || 18;
    inv.addItem('ironOre', need);
    inv.removeItem('warOrder', 1);            // keep the bag tidy: paper stays 1 but turn-in consumes nothing
    Wl.tryOpen();                              // fill the contract -> resolves -> repeatIndex = i+1
    d++;
    g.dayNight.day = d;                        // new day: board re-arms
  }
  // now at repeatIndex == r the NEXT award is armed; carry exactly `ore`:
  return { t: t, day: d, W: Wl };
}

module.exports = {
  out: out, check: check, FAILS: FAILS,
  THREE: THREE, CFG: CFG, W: W,
  FakeInv: FakeInv, FakeScene: FakeScene, freshGame: freshGame,
  reloadModule: reloadModule, driveTurnIn: driveTurnIn
};
