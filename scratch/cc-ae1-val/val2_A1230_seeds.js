// val2_A1230_seeds.js — Testerbot verdict-2: deterministic re-runs of the
// tick-driven cases whose v1 drivers used a SINGLE unseeded check for setup.
// Post-AE1-A the seat chain can lawfully refuse all 3 retries' candidates
// (rendered floor / player floor at 14 m), so "debugForce fires at the first
// check" became a coin flip on the ambient stream — verdict 1's own runs and
// Devbot's self-check (fixed seeds via freshRun, 172/172) are both subject to
// and arranged around this. Verdict-2 method: valspec §0 sanctioned seeding +
// a setup loop (tick checkSec+1 up to 6 checks until the expected mode) —
// debugForce bypasses the ROLL, a missed check is only the seat chain refusing
// that draw; the assertion bodies below are byte-for-byte the v1 assertions.
'use strict';
const L = require('./lib.js');
const { record, recordGroup, tickCase } = require('./lib2.js');
const { CFG, RID } = L;

// setup: tick checkSec+1 until mode target reached (max 6 checks)
function untilMode(A, target, max) {
  max = max || 6;
  for (let i = 0; i < max; i++) {
    A.tick(CFG.raid.checkSec + 1);
    if (A.state().mode === target) return i + 1;
  }
  return -1;
}

// V-A12 g6 cooldown — two-part (v1 body, setup looped)
(() => {
  const blocked = tickCase({ px: 0, pz: -110, yaw: Math.PI, seed: 20261, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      const checks = untilMode(A, 'live');
      if (A.state().mode !== 'live') return { v: false, e: 'setup fail after 6 checks' };
      for (const e of log) e.fsm = 'dead';
      A.tick(0.016);
      const stAfter = A.state();
      log.length = 0;
      for (let i = 0; i < 6; i++) A.tick(CFG.raid.checkSec + 1);
      const stBlocked = A.state();
      const v = stAfter.mode === 'idle' && stAfter.cooldownT === CFG.raid.cooldownSec &&
        stBlocked.mode === 'idle' && log.length === 0;
      return { v: v, e: '(seeded 20261, live at check ' + checks + ') post-wipe cooldownT=' + stAfter.cooldownT +
        ' (want ' + CFG.raid.cooldownSec + ')' + ' ; re-trigger DURING window: mode=' + stBlocked.mode + ' constructs=' + log.length };
    } });
  record('V-A12', 'g6 cooldown blocks (post-wipe, 180 s)', blocked.v ? 'PASS' : 'FAIL', blocked.e);
})();

// V-A13 g7 night cap: 3 sub-checks (v1 bodies, setups looped)
(() => {
  const a = tickCase({ px: 0, pz: -110, yaw: Math.PI, seed: 20262, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      untilMode(A, 'warn'); A.tick(CFG.raid.warnSec + 0.1);
      const s1 = A.state();
      for (const e of log) e.fsm = 'dead';
      A.tick(0.016);
      const cd = A.state().cooldownT;
      A.tick(CFG.raid.cooldownSec + 1);
      const st1 = A.state();
      g.player.pos.set(20, 0, -520);
      untilMode(A, 'warn'); A.tick(CFG.raid.warnSec + 0.1);
      const s2 = A.state();
      g.player.pos.set(120, 0, -60);
      log.length = 0;
      A.tick(CFG.raid.checkSec + 1);
      const s3 = A.state();
      const v = s1.nightParties === 1 && cd === CFG.raid.cooldownSec &&
        s2.nightParties === 2 &&
        s3.nightParties === CFG.raid.partiesPerNightMax && log.length === 0;
      return { v: v, e: '(seeded 20262) cap: party1 reserved=' + s1.nightParties + ', wipe-cooldown=' + cd +
        ' (want ' + CFG.raid.cooldownSec + '), party2 -> nightParties=' + s2.nightParties +
        ' (max ' + CFG.raid.partiesPerNightMax + '); third-party constructs=' + log.length };
    } });
  const b = tickCase({ px: 0, pz: -110, yaw: Math.PI, seed: 20263, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      untilMode(A, 'warn'); A.tick(CFG.raid.warnSec + 0.1);
      const s1 = A.state();
      g.player.pos.set(20, 0, -520);
      log.length = 0;
      A.tick(CFG.raid.checkSec + 1);
      A.tick(CFG.raid.warnSec + 0.1);
      const s2 = A.state();
      const v = s1.mode === 'live' && s1.party === 3 && log.length === 0 &&
        s2.mode === 'live' && s2.party === 3 && s2.nightParties === 1;
      return { v: v, e: '(seeded 20263) while party1 live: no second party spawns (constructs=0, mode=' + s2.mode +
        ', party=' + s2.party + ', nightParties=' + s2.nightParties + ') — 1-alive-at-a-time observable' };
    } });
  const c = tickCase({ px: 0, pz: -110, yaw: Math.PI, seed: 20264, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      untilMode(A, 'warn');
      const sWarn = A.state();
      g.regionManager.enemies[RID] = null;
      A.tick(CFG.raid.warnSec + 0.1);
      const s2 = A.state();
      const v = sWarn.nightParties === 1 && s2.nightParties === 0 && s2.mode === 'idle';
      return { v: v, e: '(seeded 20264) warn reserved=' + sWarn.nightParties + ' -> after region-list vanish: nightParties=' + s2.nightParties + ' mode=' + s2.mode };
    } });
  recordGroup('V-A13', 'g7 night cap blocks at max / 1-alive reservation / refund on rebuild', [a, b, c]);
})();

// V-A24 cooldown end-to-end (v1 bodies, setups looped)
(() => {
  const a = tickCase({ px: 0, pz: -110, yaw: Math.PI, seed: 20265, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      untilMode(A, 'warn'); A.tick(CFG.raid.warnSec + 0.1);
      const live = A.state().mode === 'live' && log.length === 3;
      if (!live) return { v: false, e: 'setup fail: mode=' + A.state().mode + ' spawns=' + log.length };
      const t0 = CFG.raid.cooldownSec;
      for (const e of log) e.fsm = 'dead';
      A.tick(0.016);
      const cd = A.state().cooldownT;
      A.tick(CFG.raid.checkSec + 1);
      const during = A.state().mode;
      let reopened = null;
      for (let i = 0; i < 4; i++) {
        A.tick(CFG.raid.cooldownSec + CFG.raid.checkSec + 1);
        if (A.state().mode !== 'idle') { reopened = A.state().mode; break; }
      }
      const v = cd === CFG.raid.cooldownSec && during === 'idle' && reopened !== null;
      return { v: v, e: '(seeded 20265) wipe: cooldownT set=' + cd + ' (want ' + CFG.raid.cooldownSec + '), blocked during window=' + (during === 'idle') + ', reopened (' + reopened + ') after ' + CFG.raid.cooldownSec + 's + check' };
    } });
  const b = tickCase({ px: 0, pz: -110, yaw: Math.PI, seed: 20266, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      untilMode(A, 'warn'); A.tick(CFG.raid.warnSec + 0.1);
      const live = A.state().mode === 'live' && log.length === 3;
      if (!live) return { v: false, e: 'setup fail' };
      for (const e of log) e.fsm = 'idle';
      A.tick(0.016);
      const st = A.state();
      let reopened = null;
      for (let i = 0; i < 4; i++) {
        A.tick(CFG.raid.cooldownSec + CFG.raid.checkSec + 1);
        if (A.state().mode !== 'idle') { reopened = A.state().mode; break; }
      }
      const v = st.mode === 'idle' && st.cooldownT === CFG.raid.cooldownSec && reopened !== null;
      return { v: v, e: '(seeded 20266) leash (all raiders fsm=idle): raidOver -> mode=' + st.mode + ' cooldownT=' + st.cooldownT +
        ' (want ' + CFG.raid.cooldownSec + ') ;; reopen: mode=' + reopened + ' cooldownT=0' };
    } });
  recordGroup('V-A24', 'cooldown end-to-end (wipe + leash) + reopen at 180s', [a, b]);
})();

// V-A26 dawn cancels warn (v1 body, setup looped)
(() => {
  const r = tickCase({ px: 0, pz: -110, yaw: Math.PI, seed: 20267, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      const at = untilMode(A, 'warn');
      const warned = A.state().mode === 'warn';
      g.dayNight.phase = 'day';
      A.tick(0.016);
      const st = A.state();
      const v = warned && st.mode === 'idle' && st.nightParties === 0 && st.cooldownT === 0 && log.length === 0;
      return { v: v, e: '(seeded 20267, warn at check ' + at + ') warn entered=' + warned + ' -> dawn: mode=' + st.mode + ' nightParties=' + st.nightParties +
        ' (refund) cooldownT=' + st.cooldownT + ' (no cooldown on dawn-cancel) constructs=' + log.length };
    } });
  record('V-A26', 'dawn cancels warn (refund, no spawn)', r.v ? 'PASS' : 'FAIL', r.e);
})();

// V-A27 live raid continues after dawn (v1 body, setup looped)
(() => {
  const r = tickCase({ px: 0, pz: -110, yaw: Math.PI, seed: 20268, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      untilMode(A, 'warn'); A.tick(CFG.raid.warnSec + 0.1);
      const live = A.state().mode === 'live' && log.length === 3;
      g.dayNight.phase = 'day';
      A.tick(CFG.raid.checkSec * 3 + 5);
      const st = A.state();
      const v = live && st.mode === 'live' && st.nightParties === 1 && log.length === 3;
      return { v: v, e: '(seeded 20268) party live through dawn (mode=' + st.mode + ' after ' + (CFG.raid.checkSec * 3 + 5) + ' s of day); ' +
        'constructs stayed ' + log.length + ' (no new spawns post-dawn); nightParties=' + st.nightParties };
    } });
  record('V-A27', 'live raid continues after dawn, no new spawns', r.v ? 'PASS' : 'FAIL', r.e);
})();

// V-A28 nightParties resets at new night (v1 body, setup looped)
(() => {
  const r = tickCase({ px: 0, pz: -110, yaw: Math.PI, seed: 20269, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      untilMode(A, 'warn'); A.tick(CFG.raid.warnSec + 0.1);
      const np1 = A.state().nightParties;
      for (const e of log) e.fsm = 'dead';
      A.tick(0.016);
      A.tick(CFG.raid.cooldownSec + 1);
      g.dayNight.phase = 'day';
      A.tick(CFG.raid.checkSec + 1);
      const npDay = A.state().nightParties;
      g.dayNight.phase = 'night';
      A.tick(0.016);
      const npNew = A.state().nightParties;
      const v = np1 === 1 && npDay === 0 && npNew === 0;
      return { v: v, e: '(seeded 20269) night1 party -> nightParties=' + np1 + '; dawn reset -> ' + npDay + '; new-night edge -> ' + npNew + ' (fresh budget)' };
    } });
  record('V-A28', 'nightParties resets at new night', r.v ? 'PASS' : 'FAIL', r.e);
})();

// V-A29 live raid ends silently (v1 body, setup looped)
(() => {
  const r = tickCase({ px: 0, pz: -110, yaw: Math.PI, seed: 20270, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      untilMode(A, 'warn'); A.tick(CFG.raid.warnSec + 0.1);
      const live = A.state().mode === 'live';
      if (!live) return { v: false, e: 'setup fail' };
      const list = g.regionManager.enemies[RID];
      list.length = 0;
      const toastsBefore = g.inventoryUI.log.length;
      A.tick(0.016);
      const st = A.state();
      const v = st.mode === 'idle' && st.cooldownT === CFG.raid.cooldownSec &&
        g.inventoryUI.log.length === toastsBefore;
      return { v: v, e: '(seeded 20270) members removed: mode=' + st.mode + ' cooldownT=' + st.cooldownT +
        ' (raid ended silently: same toast count ' + g.inventoryUI.log.length + ', no new cue)' };
    } });
  record('V-A29', 'live raid ends silently when party removes itself', r.v ? 'PASS' : 'FAIL', r.e);
})();

// V-A30 CONFIG purity under deep-freeze (v1 body, setup looped, SEEDED)
(() => {
  const r = tickCase({ px: 0, pz: -110, yaw: Math.PI, seed: 20261, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      const FROZEN = window.WH_CONFIG;
      const frozenBefore = L.oDigest(FROZEN);
      let threw = null;
      try { FROZEN.raid.warnSec = 99; } catch (e) { threw = e.message || String(e); }
      untilMode(A, 'live');                       // spawn under the frozen config
      A.tick(CFG.raid.warnSec + 0.1);
      const okTick = A.state().mode === 'live' && log.length === 3;
      const seat = A.pickRaidSeat();
      const frozenAfter = L.oDigest(FROZEN);
      const v = !!threw && okTick && frozenBefore === frozenAfter;
      return { v: v, e: '(seeded 20261) mutation attempt on frozen clone threw ("' + threw +
        '"); clone digest unchanged=' + (frozenBefore === frozenAfter) +
        '; init+tick+pickRaidSeat ran untouched under the frozen config (mode=' + A.state().mode +
        ', spawns=' + log.length + ', seat ok=' + seat.ok + ')' };
    } });
  record('V-A30', 'CONFIG purity under deep-freeze', r.v ? 'PASS' : 'FAIL', r.e);
})();

// V-A32 debugMute parity (v1 bodies, setup looped, SEEDED)
(() => {
  const a = tickCase({ px: 0, pz: -110, yaw: Math.PI, seed: 414, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      untilMode(A, 'warn');
      const muted = A.state().mode === 'warn' && g.inventoryUI.log.length === 0;
      A.tick(CFG.raid.warnSec + 0.1);
      const v = muted && A.state().mode === 'live' && g.inventoryUI.log.length === 0;
      return { v: v, e: '(seeded 414) debugMute=true: warn entered with 0 toasts; spawn resolved to live; total toasts=' + g.inventoryUI.log.length };
    } });
  const b = tickCase({ px: 0, pz: -110, yaw: Math.PI, seed: 414, knobs: { debugMute: false, debugForce: true },
    drive: (g, A, log) => {
      untilMode(A, 'warn');
      const cue = g.inventoryUI.log[0];
      A.tick(CFG.raid.warnSec + 0.1);
      const v = A.state().mode === 'live' && cue && cue.msg === CFG.raid.warnLine && cue.dur === CFG.raid.warnSec + 0.6;
      return { v: v, e: '(seeded 414) parity run (debugMute=false): cue <' + (cue && cue.msg) + ', dur ' + (cue && cue.dur) + '> at warn; spawn at same warnSec+0.1 -> live' };
    } });
  recordGroup('V-A32', 'debugMute: cue suppressed, state-machine parity', [a, b]);
})();

const { RECORDS } = require('./lib2.js');
require('fs').writeFileSync(L.TMPDIR + '/reg_seedfix_records.json', JSON.stringify(RECORDS, null, 1));
console.log('RECORDS ' + RECORDS.length + ' PASS ' + RECORDS.filter(r => r.result === 'PASS').length);
for (const r of RECORDS) console.log(r.id + ' ' + r.result + ' :: ' + r.evidence.slice(0, 150));
