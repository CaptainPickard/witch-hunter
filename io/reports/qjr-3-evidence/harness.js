// QJR-3 val harness — shared stubs. Plain node, no harness runs, no browser.
// Stub THREE + minimal DOM so the four real modules boot in node.
'use strict';

var calls = [];
function stubEl(tag) {
  var e = {
    tag: tag, children: [], style: {}, dataset: {},
    _cls: {}, textContent: '',
    classList: {
      add: function (c) { e._cls[c] = true; },
      remove: function (c) { delete e._cls[c]; },
      toggle: function (c, v) { if (v === undefined) { e._cls[c] ? delete e._cls[c] : e._cls[c] = true; } else if (v) { e._cls[c] = true; } else { delete e._cls[c]; } },
      contains: function (c) { return !!e._cls[c]; }
    },
    setAttribute: function () {}, getAttribute: function () { return null; },
    addEventListener: function (t, f) { e._handlers = e._handlers || {}; (e._handlers[t] = e._handlers[t] || []).push(f); },
    removeEventListener: function () {},
    appendChild: function (c) { e.children.push(c); c.parentNode = e; return c; },
    removeChild: function (c) { var i = e.children.indexOf(c); if (i >= 0) e.children.splice(i, 1); return c; },
    querySelector: function () { return null; },
    querySelectorAll: function () { return []; },
    getBoundingClientRect: function () { return { left: 0, top: 0, width: 100, height: 100 }; },
    getRootNode: function () { return e.parentNode || e; },
    closest: function () { return null; },
    focus: function () {}, blur: function () {},
    dispatchEvent: function () { return true; },
    value: '', type: '', tabIndex: 0
  };
  Object.defineProperty(e, 'className', {
    get: function () { return Object.keys(e._cls).join(' '); },
    set: function (v) { e._cls = {}; String(v).split(/\s+/).forEach(function (c) { if (c) e._cls[c] = true; }); }
  });
  Object.defineProperty(e, 'id', { get: function () { return e._id || ''; }, set: function (v) { e._id = v; document._ids[v] = e; }, configurable: true });
  return e;
}

global.window = global;
global.document = {
  _ids: {},
  createElement: function (tag) { return stubEl(tag); },
  getElementById: function (id) { return this._ids[id] || null; },
  addEventListener: function () {}, removeEventListener: function () {},
  body: stubEl('body'),
  activeElement: null
};
// pre-register the hooks camp/journal need at construct time
['wh-root', 'wh-canvas', 'wh-hud'].forEach(function (id) {
  global.document._ids[id] = stubEl('div');
});
Object.defineProperty(global, 'navigator', { value: { userAgent: 'node-stub', maxTouchPoints: 0 }, configurable: true });
global.localStorage = {
  _s: {},
  getItem: function (k) { return this._s[k] === undefined ? null : this._s[k]; },
  setItem: function (k, v) { this._s[k] = String(v); },
  removeItem: function (k) { delete this._s[k]; }
};
global.innerWidth = 1024; global.innerHeight = 768;
global.devicePixelRatio = 1;
global.requestAnimationFrame = function () { return 0; };
global.performance = { now: function () { return Date.now(); } };
global.setTimeout = global.setTimeout; global.clearTimeout = global.clearTimeout;
global.console_error_spy = [];

// minimal THREE stub: the shapes wareffort/camp touch at init only
global.THREE = function () {};
global.THREE.Group = function () { this.children = []; this.position = new V3(); this.rotation = { x: 0, y: 0, z: 0 }; this.name = ''; };
global.THREE.Group.prototype.add = function (c) { this.children.push(c); c.parent = this; return this; };
global.THREE.Group.prototype.remove = function (c) { var i = this.children.indexOf(c); if (i >= 0) this.children.splice(i, 1); };
global.THREE.Group.prototype.clone = function () { return new global.THREE.Group(); };
global.THREE.Group.prototype.traverse = function (f) { f(this); this.children.forEach(function (k) { if (k.traverse) k.traverse(f); }); };
global.THREE.Mesh = function (geo, mat) { this.geometry = geo; this.material = mat; this.children = []; this.position = new V3(); this.rotation = { x: 0, y: 0, z: 0 }; this.visible = true; this.name = ''; };
global.THREE.Mesh.prototype = Object.create(global.THREE.Group.prototype, { isMesh: { value: true } });
global.THREE.DoubleSide = 2;
function V3() { this.x = 0; this.y = 0; this.z = 0; }
V3.prototype.set = function (x, y, z) { this.x = x; this.y = y; this.z = z; return this; };
V3.prototype.setScalar = function (s) { this.x = this.y = this.z = s; return this; };
V3.prototype.setHex = function (h) { this._hex = h; return this; };
global.THREE.Vector3 = V3;
global.THREE.Vector2 = function () { this.x = 0; this.y = 0; };
global.THREE.Vector2.prototype.set = function (x, y) { this.x = x; this.y = y; return this; };
global.THREE.Plane = function () { this.constant = 0; };
global.THREE.Plane.prototype.set = function () { return this; };
global.THREE.Raycaster = function () { this.ray = { intersectPlane: function () { return null; } }; };
global.THREE.Raycaster.prototype.setFromCamera = function () {};
global.THREE.BoxGeometry = function () { };
global.THREE.PlaneGeometry = function () { };
global.THREE.MeshStandardMaterial = function (o) { Object.assign(this, o || {}); };
global.THREE.MeshStandardMaterial.prototype = { color: new V3() };
global.THREE.MeshBasicMaterial = function (o) { Object.assign(this, o || {}); };
global.THREE.MeshBasicMaterial.prototype = { color: { setHex: function () {} }, clone: function () { return this; } };
global.WH_ASSETS = { instance: function () { return new global.THREE.Group(); } };

// ---- game stub: dayNight + inventory + inventoryUI toast recorder ----
function makeGame(day, phase, dormant) {
  var toastsLog = [];
  var bag = {};
  return {
    dayNight: { day: day, phase: phase, dormant: !!dormant, beginCycle: function () { this._began = true; }, nextDawn: function () { this.day += 1; }, prepareWake: function () {} },
    inventory: {
      addItem: function (id, n) { bag[id] = (bag[id] || 0) + n; return n; },
      removeItem: function (id, n) { var have = bag[id] || 0; var take = Math.min(have, n); bag[id] = have - take; return take; },
      countOf: function (id) { return bag[id] || 0; },
      _bag: bag
    },
    inventoryUI: {
      blocked: false,
      toast: function (t) { toastsLog.push(t); }
    },
    player: { pos: { x: 5.9, z: -15.5 }, state: 'alive', inputSuspended: false, yaw: 0, setInputSuspended: function (v) { this.suspended = v; } },
    scene: new global.THREE.Group(),
    regionManager: { logic: { activeId: 'hold_outskirts', clampPlayer: function () {} } },
    _toasts: toastsLog
  };
}

// ---- real journal + a "recorder" journal stub (records append args verbatim) ----
function loadJournal() {
  var req = '/tmp/wh-worldfeat/prototype/js/journal.js';
  delete require.cache[req];
  require(req);
  return global.window.WH_JOURNAL;
}
function makeRecorder() {
  // journal recorder stub: mirrors wh_j.append signature, dedupes by id,
  // newest first, stamps game day — so probes can assert call shape AND dedupe.
  var j = { entries: [], born: true, isOpen: function () { return false; }, isBorn: function () { return true; } };
  j.append = function (id, title, body, day, source) {
    j._calls = (j._calls || 0) + 1;   // every invocation, dedupe or not
    j._raw = j._raw || [];
    j._raw.push(Array.prototype.slice.call(arguments));   // verbatim args for letter-level asserts
    var sid = String(id);
    for (var i = 0; i < j.entries.length; i++) { if (j.entries[i].id === sid) return 'dupe'; }
    j.entries.unshift({ id: sid, title: String(title), body: String(body), day: (day === undefined ? (j._g && j._g.dayNight && j._g.dayNight.day || 0) : day), source: String(source) });
    j._appended = (j._appended || 0) + 1;
    return 'ok';
  };
  j.appendCount = function () { return j._appended || 0; };
  j.callCount = function () { return j._calls || 0 };
  j.reset = function () { j.entries = []; j._appended = 0; j._calls = 0; j._raw = []; };
  j.raw = function () { return j._raw || []; };
  j.lastRaw = function () { return (j._raw || [])[(j._raw || []).length - 1]; };
  return j;
}

module.exports = { makeGame: makeGame, loadJournal: loadJournal, makeRecorder: makeRecorder, stubEl: stubEl, THREE: global.THREE };
