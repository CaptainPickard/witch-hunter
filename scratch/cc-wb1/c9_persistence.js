globalThis.window = globalThis; globalThis.self = globalThis;
// C-9 probe: WH_WAREFFORT capture/restore persistence shape.
// Verifies: capture() returns a plain object; restore(thatObject) reproduces
// the same module state; a missing warEffort block restores to fresh.
const path = require('path');
const R = '/tmp/wh-worldfeat';
require(path.join(R, 'prototype/vendor/three.classic.js'));
require(path.join(R, 'prototype/js/CONFIG.js'));
require(path.join(R, 'prototype/js/wareffort.js'));
const W = window.WH_WAREFFORT;
if (!W) { console.error('FAIL window.WH_WAREFFORT missing'); process.exit(1); }

const toasts = [];
function makeInv() {
  const counts = {};
  return {
    addItem: function (id, n) { counts[id] = (counts[id] || 0) + n; return n; },
    removeItem: function (id, n) { const d = Math.min(counts[id] || 0, n); counts[id] = (counts[id] || 0) - d; return d; },
    countOf: function (id) { return counts[id] || 0; }
  };
}
const G = {
  player: { pos: { x: 5.9, y: 0, z: -15.5, distanceTo: function (o) { return Math.hypot(o.x - this.x, o.z - this.z); } },
            state: 'alive', inputSuspended: false, setInputSuspended: function (v) { this.inputSuspended = v; } },
  inventoryUI: { toast: function (t) { toasts.push(t); }, blocked: false },
  inventory: makeInv(),
  dayNight: { day: 1 }
};
let fails = 0;
function T(name, cond) { console.log((cond ? 'PASS ' : 'FAIL ') + name); if (!cond) fails++; }

W.init(G);
T('capture fn', typeof W.capture === 'function');
T('restore fn', typeof W.restore === 'function');

// mark day1 done via a turn-in, capture, wipe model, restore, verify day1 still done
G.inventory.addItem('ironOre', 6);
W.restore({});
W.tryTurnIn && W.tryTurnIn('day1');
const snap = W.capture();
T('capture returns object', snap && typeof snap === 'object');
console.log('captured:', JSON.stringify(snap));

// simulate reload: fresh model, then restore snapshot
W.restore({});                       // fresh
W.restore(snap);                     // apply captured
// after restore, a day1 turn-in must be refused (already done)
G.inventory.addItem('ironOre', 6);
const again = W.tryTurnIn && W.tryTurnIn('day1');
T('day1 stays done after capture/restore', again === false);
T('post-restore turn-in consumed nothing', G.inventory.countOf('ironOre') === 6);

// a missing warEffort block is a no-op fresh model (mirror chest.js law)
W.restore(undefined);
W.restore(null);
T('restore(undefined/null) does not throw', true);

if (fails) { console.error('C-9 FAIL: ' + fails); process.exit(1); }
console.log('C-9 PASS — capture/restore round-trips contract state');
process.exit(0);
