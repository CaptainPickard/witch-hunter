globalThis.window = globalThis; globalThis.self = globalThis;
// B-1 probe: CONFIG.warEffort key, board/prop/scar rows, day1/day2/day3 contract rows,
// regionA prop seat + rotation, regionC enemy count unchanged.
const path = require('path');
const R = '/tmp/wh-worldfeat';
require(path.join(R, 'prototype/vendor/three.classic.js'));
require(path.join(R, 'prototype/js/CONFIG.js'));
const CF = window.WH_CONFIG;
const W = CF.warEffort;
let fails = [];
function T(name, cond) { console.log((cond ? 'PASS ' : 'FAIL ') + name); if (!cond) fails.push(name); }

// CONFIG.warEffort key exists
T('warEffort key exists', !!W);
if (W) {
  // day rows: iron = one-time day 1, coins = daily day 2/3 (per spec B-5 day1/day2/day3 rows expected)
  T('day1 contract row', !!(W.day1 || W.contracts && W.contracts.day1 || W.contracts && W.contracts[0]));
  // board / prop / scar content rows (names flexible - checked against module next)
  console.log('warEffort keys:', Object.keys(W).join(','));
  // prompt / title / lines / toasts strings present somewhere in the block
  const blob = JSON.stringify(W);
  T('prompt string', /E - |board/i.test(blob));
  T('turned-in toast with {id} var', /\{id\}/.test(blob));
  T('expiry toast with {name}', /\{name\}/.test(blob));
}
// regionA board prop row: seat (5.9,-15.5) rotY 3.14, asset warBoard
const A = CF.regionA;
const board = (A.props || []).find(p => p.asset === 'warBoard');
T('regionA warBoard prop', !!board);
if (board) T('seat 5.9,-15.5 rotY 3.14', board.x === 5.9 && board.z === -15.5 && board.rotY === 3.14);
// regionC bandit count unchanged: this run's HEAD already includes CC-WM1 +14 scar props and
// 3 bandit squatters? Spec law C says the three squatters keep patrolling and B-1 requires
// no bandit-count change. The WB1 diff must not add/remove enemies: record current count as the
// byte-sacred baseline. Read the current enemies once from git HEAD later; here we only count.
const C = CF.regionC;
console.log('regionC enemy count (baseline):', (C.enemies || []).length);
console.log('regionC id:', C.id);
process.exit(fails.length ? 1 : 0);
