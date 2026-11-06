globalThis.window = globalThis; globalThis.self = globalThis;
// B-2 probe: board panel open/close state machine + toasts (module-level, shim).
// Requires js/wareffort.js to exist. Drives the module's open path with a fake game.
const path = require('path');
const R = '/tmp/wh-worldfeat';
require(path.join(R, 'prototype/vendor/three.classic.js'));
require(path.join(R, 'prototype/js/CONFIG.js'));
require(path.join(R, 'prototype/js/wareffort.js'));
const W = window.WH_WAREFFORT;
if (!W) { console.error('FAIL window.WH_WAREFFORT missing'); process.exit(1); }

// fake game surface the module may read (mirrors chest.js minimal):
const toasts = [];
const G = {
  player: { pos: { x: 5.9, y: 0, z: -15.5, distanceTo: function (o) { return Math.hypot(o.x - this.x, o.z - this.z); } },
            state: 'alive', inputSuspended: false, setInputSuspended: function (v) { this.inputSuspended = v; } },
  inventoryUI: { toast: function (t) { toasts.push(t); }, blocked: false },
  inventory: { slots: [] },
  warEffort: null
};

let fails = 0;
function T(name, cond) { console.log((cond ? 'PASS ' : 'FAIL ') + name); if (!cond) fails++; }

// expected module surface (valspec-mandated):
T('init fn', typeof W.init === 'function');
T('interactPrompt fn', typeof W.interactPrompt === 'function');
T('tryBoard fn', typeof W.tryBoard === 'function');
T('capture fn', typeof W.capture === 'function');
T('restore fn', typeof W.restore === 'function');
T('close fn', typeof W.close === 'function');

W.init(G);

// interactPrompt only near board (within CONFIG.camp.chest.interactM equivalent - spec uses a boarded range; accept <=3m)
const nearTxt = W.interactPrompt();
console.log('prompt near board:', JSON.stringify(nearTxt));
T('prompt near board non-empty', typeof nearTxt === 'string' && nearTxt.length > 0);

// move away -> no prompt
G.player.pos.x = 100; G.player.pos.z = 100;
T('prompt far = null/empty', !W.interactPrompt());
G.player.pos.x = 5.9; G.player.pos.z = -15.5;

// open
const opened = W.tryBoard();
T('tryBoard returns true near board', opened === true);
T('panel open state', W.isOpen && W.isOpen() === true);
T('input suspended on open', G.player.inputSuspended === true);
T('inventoryUI.blocked on open', G.inventoryUI.blocked === true);

// close
W.close();
T('close clears open', !W.isOpen || W.isOpen() === false);
T('input unsuspended on close', G.player.inputSuspended === false);

// interactPrompt while open -> panel close hint (spec: Esc close)
W.tryBoard();
const openPrompt = W.interactPrompt();
console.log('prompt while open:', JSON.stringify(openPrompt));
W.close();

if (fails) { console.error('B-2 FAIL: ' + fails); process.exit(1); }
console.log('B-2 PASS — board panel state machine + prompts behave');
process.exit(0);
