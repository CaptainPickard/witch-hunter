// CC-AE1 Testerbot validation — shared node shim + module loader.
// Every val_XX case script requires this first. NO-GIT law: no git commands here.
'use strict';
const fs = require('fs');
const path = require('path');
const ROOT = '/tmp/wh-worldfeat';
const TMPDIR = path.join(ROOT, 'scratch/cc-ae1-val/tmp');
fs.mkdirSync(TMPDIR, { recursive: true });

globalThis.window = globalThis;
globalThis.self = globalThis;
if (typeof globalThis.document === 'undefined') {
  globalThis.document = {
    createElement: () => ({ style: {}, setAttribute() {}, appendChild() {}, addEventListener() {} }),
    addEventListener() {}, body: { appendChild() {} }
  };
}
if (typeof globalThis.requestAnimationFrame === 'undefined') {
  globalThis.requestAnimationFrame = () => 0;
}

require(path.join(ROOT, 'prototype/vendor/three.classic.js'));
require(path.join(ROOT, 'prototype/js/CONFIG.js'));
require(path.join(ROOT, 'prototype/js/wh-ground.js'));
const CFG = window.WH_CONFIG;
const G = window.WH_GROUND;
const RID = typeof CFG.raid === 'object' && CFG.raid ? CFG.raid.regionId : 'forest_of_the_old_king';
const SAVED_RANDOM = Math.random;

// digest a live object subtree deterministically (valspec §1 method)
function oDigest(o) { return require('crypto').createHash('sha256').update(JSON.stringify(o)).digest('hex'); }
function fDigest(p) { return require('crypto').createHash('sha256').update(fs.readFileSync(path.join(ROOT, p))).digest('hex'); }

// mulberry32 seeded PRNG — injected onto Math.random; returns [fn, restore]
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function useRand(a) {
  Math.random = mulberry32(a);
  return () => { Math.random = SAVED_RANDOM; };
}

// deep freeze with cycle guard; returns count of frozen nodes
function deepFreeze(o, seen) {
  seen = seen || new Set();
  let n = 0;
  if (o && typeof o === 'object' && !seen.has(o)) {
    seen.add(o); Object.freeze(o); n = 1;
    for (const k of Object.keys(o)) n += deepFreeze(o[k], seen);
  }
  return n;
}
function deepClone(o) { return JSON.parse(JSON.stringify(o)); }

// mock game for WH_AMBUSH (valspec SHARED-SETUP)
function mockGame(px, pz, yaw) {
  const g = {
    dayNight: { dormant: false, phase: 'night' },
    player: { pos: new THREE.Vector3(px, 0, pz), yaw: yaw === undefined ? Math.PI : yaw, state: 'alive' },
    regionManager: { logic: { activeId: RID }, enemies: {}, scene: { added: [] } },
    inventoryUI: { log: [], toast(msg, dur) { this.log.push({ msg: msg, dur: dur }); } }
  };
  g.regionManager.enemies[RID] = [];
  return g;
}

// record-only WH_Enemy stub; construction log kept per case
function installEnemyStub(log) {
  const Prev = window.WH_Enemy;
  function Stub(type, scene, regionId, sx, sz) {
    this.type = type; this.sx = sx; this.sz = sz; this.order = log.length;
    log.push(this);
    this.fsm = null; this.raidMember = undefined; this.packId = undefined;
    this.terrainHome = null;
    this.pos = new THREE.Vector3(sx, 0, sz); this.pos.y = 0;
    this.setFsm = (f) => { this.fsm = f; };
    this.setBody = (b) => { this.body = b; };
    this.groundY = () => 0;
    this.root = { position: { copy(v) { this._copied = v; } } };
    this.yawFrame = { rotation: { y: 0 } };
    Object.defineProperty(this, 'setYaw', { get() { return this.yawFrame.rotation.y; } });
  }
  Stub.makeBody = t => ({ type: t });
  window.WH_Enemy = Stub;
  return () => { window.WH_Enemy = Prev; };
}

// road polyline geometry (validator's own math — not ambush internals)
function polyGeom(row) {
  const pts = row.points, segs = [];
  let arc = 0;
  for (let i = 0; i + 1 < pts.length; i++) {
    const ax = pts[i][0], az = pts[i][1], bx = pts[i + 1][0], bz = pts[i + 1][1];
    const len = Math.hypot(bx - ax, bz - az);
    const dx = len > 1e-9 ? (bx - ax) / len : 0, dz = len > 1e-9 ? (bz - az) / len : 0;
    segs.push({ ax: ax, az: az, dx: dx, dz: dz, len: len, arc0: arc });
    arc += len;
  }
  return { segs: segs, total: arc };
}
function pointOnPoly(g, s) {
  if (s <= 0) s = 0;
  if (s > g.total) s = g.total;
  for (let i = 0; i < g.segs.length; i++) {
    const sg = g.segs[i];
    if (s <= sg.arc0 + sg.len || i === g.segs.length - 1) {
      const t = Math.min(Math.max(s - sg.arc0, 0), sg.len);
      return { x: sg.ax + sg.dx * t, z: sg.az + sg.dz * t, px: -sg.dz, pz: sg.dx };
    }
  }
  return null;
}
function distToCenterline(g, x, z) {
  let best = Infinity;
  for (const sg of g.segs) {
    const t = Math.min(Math.max(((x - sg.ax) * sg.dx + (z - sg.az) * sg.dz) / (sg.len || 1), 0), sg.len);
    const d = Math.hypot(sg.ax + sg.dx * t - x, sg.az + sg.dz * t - z);
    if (d < best) best = d;
  }
  return best;
}
// 4 m centerline samples on one road row (probe grid)
function centerSamples(row, step) {
  step = step || 4;
  const g = polyGeom(row), out = [];
  for (let s = 0; s <= g.total + 1e-9; s += step) {
    const p = pointOnPoly(g, s);
    if (p) out.push({ x: p.x, z: p.z, arc: s, px: p.px, pz: p.pz });
  }
  return out;
}

// the probe's law sets for seat predicates
function seatRoadRows() { return CFG.roads.filter(r => ['kingsRoad', 'northRoad', 'eastRoad', 'westRoad'].includes(r.id)); }
function regionCProps() { return CFG.regionC.props.filter(p => p.x !== undefined); }
function campfireRows() { return CFG.regionC.props.filter(p => p.asset === 'banditCampfire').map(p => [p.x, p.z]); }
const STONE = [0, -366];
// seat-validation fire set = regionC banditCampfire rows (ambush seatFireRows);
// player gate g5 set = all-CONFIG banditCampfire rows (per valspec V-A11 setup)
function allFireRows() {
  const out = [];
  for (const rk of Object.keys(CFG)) {
    const reg = CFG[rk];
    if (reg && typeof reg === 'object' && Array.isArray(reg.props)) {
      for (const p of reg.props) if (p.asset === 'banditCampfire' && p.x !== undefined) out.push([p.x, p.z]);
    }
  }
  return out;
}

module.exports = {
  fs, path, ROOT, TMPDIR, window, CFG, G, RID, SAVED_RANDOM,
  oDigest, fDigest, mulberry32, useRand, deepFreeze, deepClone,
  mockGame, installEnemyStub,
  polyGeom, pointOnPoly, distToCenterline, centerSamples,
  seatRoadRows, regionCProps, campfireRows, allFireRows, STONE
};
