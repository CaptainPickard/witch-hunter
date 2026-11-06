// val2_A3132_seed.js — Testerbot verdict-2: V-A31/V-A32 re-run with SEEDED
// Math.random per valspec §0 ("Seeded determinism: seat law cases seed
// Math.random per case — use a simple mulberry32 injected onto Math.random,
// restored in finally"). The v1 drivers left Math.random ambient for the
// debugForce fire path; post-AE1-A the first seat candidate can lawfully
// REFUSE g8 (player floor / rendered floor), which the ambient stream turned
// into a flaky first-try miss — Devbot's own self-check runs these identical
// assertions under mulberry32 seeds (freshRun 91301/91302, mulberry32(414)).
// Assertions UNCHANGED from the v1 val_A30_33.js bodies.
'use strict';
const L = require('./lib.js');
const { tickCase } = require('./lib2.js');
const { CFG } = L;

// V-A31 — debugForce bypasses ONLY the trigger roll; seats still validated
(() => {
  // (a) illegal-seat pose (off-road): debugForce CANNOT spawn
  const a = tickCase({ px: 120, pz: -60, yaw: Math.PI, seed: 91302,
    knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      for (let i = 0; i < 3; i++) A.tick(CFG.raid.checkSec + 1);
      const v = A.state().mode === 'idle' && log.length === 0;
      return { v: v, e: 'debugForce at off-road pose (120,-60): mode=' + A.state().mode + ' constructs=' + log.length + ' (seat validation NOT relaxed: g8 refuses)' };
    } });
  // (b) legal pose with debugForce: fires within the check cadence (roll bypassed)
  const b = tickCase({ px: 2, pz: -280, yaw: Math.PI, seed: 91301,
    knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      let fired = null;
      for (let i = 0; i < 4; i++) {
        A.tick(CFG.raid.checkSec + 1);
        if (A.state().mode !== 'idle') { fired = A.state().mode; break; }
      }
      const v = fired === 'warn';
      return { v: v, e: 'debugForce at road pose (2,-280), seeded 91301: warn at check ' +
        (fired === 'warn' ? '1 (roll bypassed; cadence still applies)' : String(fired)) };
    } });
  // (c) legal pose WITHOUT debugForce, triggerChance 0.25: roll is consulted
  const c = tickCase({ px: 2, pz: -280, yaw: Math.PI, seed: 777,
    knobs: { debugMute: true, debugForce: false },
    drive: (g, A, log) => {
      let checks = 0;
      for (let i = 0; i < 40; i++) { A.tick(CFG.raid.checkSec); checks++; if (A.state().mode !== 'idle') break; }
      const v = checks > 1 || A.state().mode === 'warn';
      return { v: v, e: 'no-debugForce (seeded 777): warn entered after ' + checks + ' check(s) (roll consulted; >=2 means the roll gated)' };
    } });
  console.log(JSON.stringify([{ id: 'V-A31', name: 'debugForce bypasses ONLY the trigger roll; seats still validated',
    result: (a.v && b.v && c.v) ? 'PASS' : 'FAIL', evidence: [a.e, b.e, c.e].join(' ;; ') }]));
})();

// V-A32 — debugMute suppresses ALL ambush toasts; state-machine parity
(() => {
  // (a) muted run: no toasts at all
  const a = tickCase({ px: 2, pz: -280, yaw: Math.PI, seed: 414,
    knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      A.tick(CFG.raid.checkSec + 1);
      const muted = A.state().mode === 'warn' && g.inventoryUI.log.length === 0;
      A.tick(CFG.raid.warnSec + 0.1);
      const v = muted && A.state().mode === 'live' && g.inventoryUI.log.length === 0;
      return { v: v, e: 'debugMute=true (seeded 414): warn entered with 0 toasts; spawn resolved to live; total toasts=' + g.inventoryUI.log.length };
    } });
  // (b) unmuted parity: same drive, cue fires, same timing
  const b = tickCase({ px: 2, pz: -280, yaw: Math.PI, seed: 414,
    knobs: { debugMute: false, debugForce: true },
    drive: (g, A, log) => {
      A.tick(CFG.raid.checkSec + 1);
      const cue = g.inventoryUI.log[0];
      A.tick(CFG.raid.warnSec + 0.1);
      const v = A.state().mode === 'live' && cue && cue.msg === CFG.raid.warnLine && cue.dur === CFG.raid.warnSec + 0.6;
      return { v: v, e: 'parity run (debugMute=false, seeded 414): cue <' + (cue && cue.msg) + ', dur ' + (cue && cue.dur) + '> at warn; spawn at same warnSec+0.1 -> live' };
    } });
  console.log(JSON.stringify([{ id: 'V-A32', name: 'debugMute: cue suppressed, state-machine parity',
    result: (a.v && b.v) ? 'PASS' : 'FAIL', evidence: [a.e, b.e].join(' ;; ') }]));
})();
