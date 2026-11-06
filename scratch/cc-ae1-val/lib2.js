// lib2.js — ambush loader + case recorder (requires lib.js first)
'use strict';
const { path, ROOT, window, CFG, RID, SAVED_RANDOM } = require('./lib.js');

// record-only WH_Enemy stub is installed by cases that need it; ambush.js itself
// never touches WH_Enemy at load or init.
require(path.join(ROOT, 'prototype/js/region-manager.js')); // V-A25: REAL updateEnemies
require(path.join(ROOT, 'prototype/js/ambush.js'));
const A = window.WH_AMBUSH;

const RECORDS = [];
function record(id, name, result, evidence) {
  RECORDS.push({ id: id, name: name, result: result, evidence: evidence || '' });
}
// composite ids like V-A14..16 are one record each in the report
function recordGroup(id, name, parts) {
  const fails = parts.filter(p => p.v === false);
  const ev = parts.map(p => p.e).join(' ;; ');
  record(id, name, fails.length === 0 ? 'PASS' : 'FAIL', ev);
}

// knob plumbing: set CFG.raid.debugForce/debugMute for ONE init, restoring
// window.WH_CONFIG afterwards. Uses a deep clone frozen ON window.WH_CONFIG;
// ambush.init() re-binds CFG (its first line), so ambient CONFIG is restored
// while the case's frozen clone stays bound inside the ambush closure.
function withKnobs(knobs, fn) {
  const savedDesc = Object.getOwnPropertyDescriptor(window, 'WH_CONFIG');
  const savedCfg = window.WH_CONFIG;
  const clone = JSON.parse(JSON.stringify(savedCfg));
  for (const k of Object.keys(knobs)) clone.raid[k] = knobs[k];
  const frozenCount = require('./lib.js').deepFreeze(clone);
  // freeze the clone only — the LIVE ambient CFG must never be frozen (report
  // digest integrity for V-A23); frozen clone guarantees purity inside the case
  window.WH_CONFIG = clone;
  try {
    return fn(clone, frozenCount);
  } finally {
    if (savedDesc) Object.defineProperty(window, 'WH_CONFIG', savedDesc);
    else window.WH_CONFIG = savedCfg;
  }
}

// run one SHARED-SETUP tick case; returns {v, e}
// pose: [px, pz, yaw]; knobs: {debugMute, debugForce} or null (defaults true mute)
// drive: fn(game, A, enemyLog) -> runs after init, custom per case
function tickCase(opts) {
  const lib = require('./lib.js');
  const enemyLog = [];
  const restoreEnemy = lib.installEnemyStub(enemyLog);
  const savedRand = Math.random;
  if (opts.seed !== undefined) {
    // mulberry32, restored in finally (the case's rng is deterministic)
    let a = opts.seed >>> 0;
    Math.random = function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const g = lib.mockGame(opts.px, opts.pz, opts.yaw);
  let out;
  try {
    const knobs = opts.knobs === undefined ? { debugMute: true } : opts.knobs;
    let r;
    const fnRun = () => {
      window.WH_AMBUSH.init(g);
      return opts.drive(g, window.WH_AMBUSH, enemyLog);
    };
    if (knobs) r = withKnobs(knobs, fnRun);
    else r = fnRun();
    out = r;
  } catch (e) {
    out = { v: false, e: 'exception: ' + e.message };
  } finally {
    Math.random = savedRand;
    restoreEnemy();
  }
  return out;
}

module.exports = { A, RECORDS, record, recordGroup, withKnobs, tickCase };
