// val_A30_last.js — V-A30 CONFIG purity: probes the FROZEN CLONE that ambush's
// tick actually binds (window.WH_CONFIG during the case), then verifies the
// ambient CONFIG digest is byte-identical after every case has run. MUST be
// required LAST (after all other case files).
'use strict';
const L = require('./lib.js');
const { record, tickCase } = require('./lib2.js');
const { CFG } = L;

const before = L.oDigest(CFG);
const r = tickCase({ px: 0, pz: -110, yaw: Math.PI, knobs: { debugMute: true, debugForce: true },
  drive: (g, A, log) => {
    const FROZEN = window.WH_CONFIG;          // the deep-frozen clone bound by init
    const frozenBefore = L.oDigest(FROZEN);
    let threw = null;
    try { FROZEN.raid.warnSec = 99; } catch (e) { threw = e.message || String(e); }
    // the machine still runs untouched under the frozen config:
    A.tick(FROZEN.raid.checkSec + 1);
    A.tick(FROZEN.raid.warnSec + 0.1);
    const okTick = A.state().mode === 'live' && log.length === 3;
    const seat = A.pickRaidSeat();
    const frozenAfter = L.oDigest(FROZEN);
    const v = !!threw && okTick && frozenBefore === frozenAfter;
    return { v: v, e: 'mutation attempt on frozen clone threw ("' + threw +
      '"); clone digest unchanged=' + (frozenBefore === frozenAfter) +
      '; init+tick+pickRaidSeat ran untouched under the frozen config (mode=' + A.state().mode +
      ', spawns=' + log.length + ', seat ok=' + seat.ok + ')' };
  } });
const after = L.oDigest(CFG);
const same = before === after;
record('V-A30', 'CONFIG purity under deep-freeze', (r.v && same) ? 'PASS' : 'FAIL',
  r.e + ' ;; ambient CONFIG digest unchanged after ALL cases ran: ' + same +
  ' (digest ' + after.slice(0, 12) + '...)');
