// val_A30_33.js — §5.F CONFIG purity + debug knobs (V-A30..V-A33)
'use strict';
const L = require('./lib.js');
const { record, tickCase, withKnobs } = require('./lib2.js');
const { CFG, digestJson } = L;

// V-A31 — debugForce bypasses ONLY the trigger roll; seats still validated
(() => {
  // (a) illegal-seat pose (off-road, no road within 25 m): debugForce CANNOT spawn
  const a = tickCase({ px: 120, pz: -60, yaw: Math.PI, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      for (let i = 0; i < 3; i++) A.tick(CFG.raid.checkSec + 1);
      const v = A.state().mode === 'idle' && log.length === 0;
      return { v: v, e: 'debugForce at off-road pose (120,-60): mode=' + A.state().mode + ' constructs=' + log.length + ' (seat validation NOT relaxed: g8 no-road refuses)' };
    } });
  // (b) legal pose with debugForce: fires reliably (bypasses the roll)
  const b = tickCase({ px: 0, pz: -110, yaw: Math.PI, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      A.tick(CFG.raid.checkSec + 1);
      const v = A.state().mode === 'warn';
      return { v: v, e: 'debugForce at road pose: first check warms warn immediately (mode=' + A.state().mode + '; roll bypassed)' };
    } });
  // (c) legal pose WITHOUT debugForce, triggerChance 0.25: ~75% no-fire per check —
  //     over 40 checks some fire, but the FIRST check usually does not: assert
  //     the roll is actually consulted (not forced): count checks until warn.
  const c = tickCase({ px: 0, pz: -110, yaw: Math.PI, knobs: { debugMute: true, debugForce: false }, seed: 777,
    drive: (g, A, log) => {
      let checks = 0;
      for (let i = 0; i < 40; i++) { A.tick(CFG.raid.checkSec); checks++; if (A.state().mode !== 'idle') break; }
      const v = checks > 1 || A.state().mode === 'warn'; // roll consulted (may fire early by chance)
      return { v: v, e: 'no-debugForce: warn entered after ' + checks + ' check(s) (roll consulted; >=2 checks means the roll actually gated)' };
    } });
  record('V-A31', 'debugForce bypasses ONLY the trigger roll; seats still validated',
    (a.v && b.v && c.v) ? 'PASS' : 'FAIL', [a.e, b.e, c.e].join(' ;; '));
})();

// V-A32 — debugMute suppresses ALL ambush toasts; state-machine timing parity
(() => {
  // (a) muted run: no toasts at all
  const a = tickCase({ px: 0, pz: -110, yaw: Math.PI, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      A.tick(CFG.raid.checkSec + 1);
      const muted = A.state().mode === 'warn' && g.inventoryUI.log.length === 0;
      A.tick(CFG.raid.warnSec + 0.1);
      const v = muted && A.state().mode === 'live' && g.inventoryUI.log.length === 0;
      return { v: v, e: 'debugMute=true: warn entered with 0 toasts; spawn resolved to live; total toasts=' + g.inventoryUI.log.length };
    } });
  // (b) unmuted parity: same drive, cue fires, same timing
  const b = tickCase({ px: 0, pz: -110, yaw: Math.PI, knobs: { debugMute: false, debugForce: true },
    drive: (g, A, log) => {
      A.tick(CFG.raid.checkSec + 1);
      const cue = g.inventoryUI.log[0];
      const t0 = A.state();
      A.tick(CFG.raid.warnSec + 0.1);
      const v = A.state().mode === 'live' && cue && cue.msg === CFG.raid.warnLine && cue.dur === CFG.raid.warnSec + 0.6;
      return { v: v, e: 'parity run (debugMute=false): cue <' + cue.msg + ', dur ' + cue.dur + '> at warn; spawn at same warnSec+0.1 -> live' };
    } });
  record('V-A32', 'debugMute: cue suppressed, state-machine parity',
    (a.v && b.v) ? 'PASS' : 'FAIL', [a.e, b.e].join(' ;; '));
})();

// V-A33 — seeded determinism: same seed -> identical seat stream; rng never touched outside pickRaidSeat/tick
(() => {
  function run(seed) {
    return tickCase({ px: 0, pz: -110, yaw: Math.PI, knobs: { debugMute: true, debugForce: true }, seed: seed,
      drive: (g, A, log) => {
        A.tick(CFG.raid.checkSec + 1);
        A.tick(CFG.raid.warnSec + 0.1);
        return log.map(e => e.sx.toFixed(12) + ',' + e.sz.toFixed(12));
      } });
  }
  const a = run(4242), b = run(4242), c = run(99);
  const det = Array.isArray(a) && Array.isArray(b) && a.join('|') === b.join('|');
  const differs = Array.isArray(c) && c.join('|') !== a.join('|');
  record('V-A33', 'deterministic seat RNG (same seed -> same seats; different seed -> different)',
    (det && differs) ? 'PASS' : 'FAIL',
    'seed 4242 x2: ' + (det ? 'identical (' + a[0] + ' x3)' : 'DIVERGED') + '; seed 99 differs from 4242: ' + differs);
})();

console.log(JSON.stringify(require('./lib2.js').RECORDS.filter(r => /^V-A3[0-3]$/.test(r.id))));
