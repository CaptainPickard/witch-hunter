// val2_A1416_seed.js — Testerbot verdict-2: val_A14_16.js requires a SEEDED
// Math.random for the V-A14 transcript run to fire at the first check.
// Deterministic pickRaidSeat (valspec §0 law) needs the seed for the cue-frame
// seat search to resolve. This wrapper: install enemy stub FIRST (matching the
// v1 standalone runs), seed Math.random BEFORE loading val_A14_16.js, and
// require it. Its records land via lib2's shared RECORDS; the caller captures
// the A14/A15/A16 subset. Evidence identical in form to the v1 run.
'use strict';
const L = require('./lib.js');
const path = L.path, ROOT = L.ROOT;
require(path.join(ROOT, 'prototype/js/region-manager.js'));
const stubLog = [];
const restore = L.installEnemyStub(stubLog);
let a = 20261 >>> 0;
Math.random = function () {
  a |= 0; a = (a + 0x6D2B79F5) | 0;
  let t = Math.imul(a ^ (a >>> 15), 1 | a);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
require('./val_A14_16.js');
const recs = require('./lib2.js').RECORDS.filter(r => /^V-A1[456]$/.test(r.id));
console.log(JSON.stringify(recs));
