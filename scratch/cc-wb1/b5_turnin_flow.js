globalThis.window = globalThis; globalThis.self = globalThis;
// B-4/B-5/B-7 probe: turn-in behavior for day-rows (iron once, coins daily, day-3 re-sign).
// Drives WH_WAREFFORT with a controllable day clock + inventory shim.
const path = require('path');
const R = '/tmp/wh-worldfeat';
require(path.join(R, 'prototype/vendor/three.classic.js'));
require(path.join(R, 'prototype/js/CONFIG.js'));
require(path.join(R, 'prototype/js/wareffort.js'));
const W = window.WH_WAREFFORT;
if (!W) { console.error('FAIL window.WH_WAREFFORT missing'); process.exit(1); }

// minimal inventory shim exposing the pinned accessors (valspec B-7.1: WH_INVENTORY.addItem/removeItem/countOf)
function makeInv() {
  const counts = {};
  return {
    addItem: function (id, n) { counts[id] = (counts[id] || 0) + n; return n; },
    removeItem: function (id, n) { const d = Math.min(counts[id] || 0, n); counts[id] = (counts[id] || 0) - d; return d; },
    countOf: function (id) { return counts[id] || 0; },
    _counts: counts
  };
}

const toasts = [];
const dayNight = { day: 0 };
const G = {
  player: { pos: { x: 5.9, y: 0, z: -15.5, distanceTo: function (o) { return Math.hypot(o.x - this.x, o.z - this.z); } },
            state: 'alive', inputSuspended: false, setInputSuspended: function (v) { this.inputSuspended = v; } },
  inventoryUI: { toast: function (t) { toasts.push(t); }, blocked: false },
  inventory: null,
  dayNight: dayNight
};

let fails = 0;
function T(name, cond) { console.log((cond ? 'PASS ' : 'FAIL ') + name); if (!cond) fails++; }

W.init(G);

// mandated turn-in entry (valspec): W.tryTurnIn(dayKey) performs that day's turn-in
// against game.inventory + CONFIG.warEffort rows; returns true if a contract was active.
T('tryTurnIn fn', typeof W.tryTurnIn === 'function');

// ---- Day 1: iron contract (one-time) ----
dayNight.day = 1;
G.inventory = makeInv();
G.inventory.addItem('ironOre', 6);
W.restore({});                       // fresh model
const r1 = W.tryTurnIn('day1');
T('day1 turn-in returns true', r1 === true);
T('day1 consumed 6 ironOre', G.inventory.countOf('ironOre') === 0);
T('day1 granted warOrder', G.inventory.countOf('warOrder') === 1);
T('day1 toast fired', toasts.some(t => /war order/i.test(t)));
// repeating day1 must be refused (one-time)
G.inventory.addItem('ironOre', 6);
const stateBefore = JSON.stringify(G.inventory._counts);
const r1b = W.tryTurnIn('day1');
T('day1 second turn-in refused (returns false)', r1b === false);
T('day1 second turn-in consumed nothing', G.inventory.countOf('ironOre') === 6);

// ---- Day 2: coins contract (daily, repeatable same day? spec = daily => one per day) ----
dayNight.day = 2;
G.inventory = makeInv();
G.inventory.addItem('stolenCoin', 12);
W.restore({ day1: { done: true } });   // continue after day1 done, day2 open
const r2 = W.tryTurnIn('day2');
T('day2 turn-in returns true', r2 === true);
T('day2 consumed 12 stolenCoin', G.inventory.countOf('stolenCoin') === 0);
T('day2 granted warOrder', G.inventory.countOf('warOrder') === 1);
G.inventory.addItem('stolenCoin', 12);
const r2b = W.tryTurnIn('day2');
T('day2 same-day repeat refused', r2b === false);

// ---- Day 3: coins contract + re-sign path ----
dayNight.day = 3;
G.inventory = makeInv();
G.inventory.addItem('stolenCoin', 12);
W.restore({ day1: { done: true }, day2: { doneDay: 2 } });
const r3 = W.tryTurnIn('day3');
T('day3 turn-in returns true', r3 === true);
T('day3 consumed 12 stolenCoin', G.inventory.countOf('stolenCoin') === 0);
T('day3 has re-sign / renewal entry', typeof W.resign === 'function' || typeof W.renew === 'function' || !!W.day3Available);

// ---- Wrong-day turn-in refused ----
dayNight.day = 1;
G.inventory = makeInv();
G.inventory.addItem('stolenCoin', 12);
W.restore({});
const rWrong = W.tryTurnIn('day2');
T('day2 row on day1 refused', rWrong === false);
T('wrong-day coins untouched', G.inventory.countOf('stolenCoin') === 12);

if (fails) { console.error('B-5 FAIL: ' + fails); process.exit(1); }
console.log('B-5 PASS — iron one-time, coins daily, day-3 re-sign path present, wrong-day refused');
process.exit(0);
