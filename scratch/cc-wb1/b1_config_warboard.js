globalThis.window = globalThis; globalThis.self = globalThis;
// B-1 probe: CONFIG.warEffort schema (shape mandated by valspec), regionA
// warBoard prop seat/rot, regionC bandit census unchanged (25 = HEAD baseline).
const path = require('path');
const R = '/tmp/wh-worldfeat';
require(path.join(R, 'prototype/vendor/three.classic.js'));
require(path.join(R, 'prototype/js/CONFIG.js'));
const CF = window.WH_CONFIG;
const W = CF.warEffort;
let fails = 0;
function T(name, cond) { console.log((cond ? 'PASS ' : 'FAIL ') + name); if (!cond) fails++; }

T('warEffort key', !!W);
if (W) {
  T('board block', !!W.board);
  T('prompt string', typeof W.prompt === 'string' && /^\s*E - /.test(W.prompt));
  T('title string', typeof W.title === 'string' && W.title.length > 0);
  // mandated day rows: day1/day2/day3 contract descriptors
  T('day1 row', typeof W.day1 === 'object' && !!W.day1);
  T('day2 row', typeof W.day2 === 'object' && !!W.day2);
  T('day3 row', typeof W.day3 === 'object' && !!W.day3);
  const blob = JSON.stringify(W);
  T('turned-in toast has {id}', /\{id\}/.test(blob));
  T('expiry toast has {name}', /\{name\}/.test(blob));
  // contract day shapes: day1 = iron (one-time), day2/day3 = coins (daily)
  if (W.day1) T('day1 gives ironOre', /ironOre/.test(JSON.stringify(W.day1)));
  if (W.day2) T('day2 stolenCoin', /stolenCoin/.test(JSON.stringify(W.day2)));
  if (W.day3) T('day3 stolenCoin', /stolenCoin/.test(JSON.stringify(W.day3)));
}
// regionA board prop seat
const A = CF.regionA;
const board = (A.props || []).find(p => p.asset === 'warBoard');
T('regionA warBoard prop', !!board);
if (board) {
  T('seat x=5.9', board.x === 5.9);
  T('seat z=-15.5', board.z === -15.5);
  T('rotY=3.14', board.rotY === 3.14);
}
// regionC bandit census unchanged: HEAD baseline = 25 bandit rows in regionC (22 pre-WM1 + 3 WM1 squatters)
const regionC_enemy_count = (CF.regionC.enemies || []).length;
const regionC_bandits = (CF.regionC.enemies || []).filter(e => e.type === 'bandit').length;
console.log('regionC enemies total (baseline 55):', regionC_enemy_count);
console.log('regionC bandits (baseline 25):', regionC_bandits);
T('regionC bandit count unchanged (25)', regionC_bandits === 25);
T('regionA has NO nodes from this round - regionA node count baseline 14', (CF.regionA.nodes || []).length === 14);
process.exit(fails ? 1 : 0);
