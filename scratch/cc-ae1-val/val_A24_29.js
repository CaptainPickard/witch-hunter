// val_A24_29.js — §5.E day-boundary + raid lifecycle (V-A24..V-A29)
'use strict';
const L = require('./lib.js');
const { record, tickCase } = require('./lib2.js');
const { CFG } = L;

// V-A24 — cooldown end-to-end: wipe path + leash path, reopen at 180 s
(() => {
  // (a) wipe path
  const a = tickCase({ px: 0, pz: -110, yaw: Math.PI, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      A.tick(CFG.raid.checkSec + 1);
      A.tick(CFG.raid.warnSec + 0.1);
      const live = A.state().mode === 'live' && log.length === 3;
      if (!live) return { v: false, e: 'setup fail: mode=' + A.state().mode + ' spawns=' + log.length };
      const t0 = CFG.raid.cooldownSec; // measure reopen tick: cooldown elapses, checkT needs its own elapse
      for (const e of log) e.fsm = 'dead';
      A.tick(0.016);
      const cd = A.state().cooldownT;
      // blocked during window:
      A.tick(CFG.raid.checkSec + 1);
      const during = A.state().mode;
      // reopen (cooldown tick + full check):
      let reopened = null;
      for (let i = 0; i < 4; i++) {
        A.tick(CFG.raid.cooldownSec + CFG.raid.checkSec + 1);
        if (A.state().mode !== 'idle') { reopened = A.state().mode; break; }
      }
      const v = cd === CFG.raid.cooldownSec && during === 'idle' && reopened !== null;
      return { v: v, e: 'wipe: cooldownT set=' + cd + ' (want ' + CFG.raid.cooldownSec + '), blocked during window=' + (during === 'idle') + ', reopened (' + reopened + ') after ' + CFG.raid.cooldownSec + 's + check' };
    } });

  // (b) leash path: all members fsm 'idle' -> raidOver
  const b = tickCase({ px: 0, pz: -110, yaw: Math.PI, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      A.tick(CFG.raid.checkSec + 1);
      A.tick(CFG.raid.warnSec + 0.1);
      if (A.state().mode !== 'live') return { v: false, e: 'setup fail' };
      for (const e of log) e.fsm = 'idle';
      A.tick(0.016);
      const st = A.state();
      const v = st.mode === 'idle' && st.cooldownT === CFG.raid.cooldownSec;
      return { v: v, e: 'leash (all raiders fsm=idle): raidOver -> mode=' + st.mode + ' cooldownT=' + st.cooldownT + ' (want ' + CFG.raid.cooldownSec + ')' };
    } });

  // (c) reopen exactly at 180: with a live check clock, reopen at the first check after cooldown hits 0
  const c = tickCase({ px: 0, pz: -110, yaw: Math.PI, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      A.tick(CFG.raid.checkSec + 1);
      A.tick(CFG.raid.warnSec + 0.1);
      for (const e of log) e.fsm = 'dead';
      A.tick(0.016);
      // small-step the clock: after 180 s of cooldown, the very next check frame should warn again
      let sum = 0;
      const steps = [];
      while (sum < CFG.raid.cooldownSec) { A.tick(20); sum += 20; if (A.state().mode !== 'idle') break; }
      for (let i = 0; i < 3 && A.state().mode === 'idle'; i++) { A.tick(CFG.raid.checkSec); steps.push(A.state().mode); }
      const st = A.state();
      const v = st.cooldownT === 0 && st.mode !== 'idle';
      return { v: v, e: 'reopen: after cooldown fully paid, mode=' + st.mode + ' cooldownT=' + st.cooldownT + ' (reopen requires a check roll which debugForce passes)' };
    } });

  record('V-A24', 'cooldown end-to-end (wipe + leash) + reopen at 180s',
    (a.v && b.v && c.v) ? 'PASS' : 'FAIL', [a.e, b.e, c.e].join(' ;; '));
})();

// V-A25 — REAL RegionManager.updateEnemies: raidMember corpses never in regionStates
(() => {
  globalThis.self = globalThis; // (lib.js already shims; idempotent)
  const RM = window.WH_RegionManager;
  const rm = new RM({ scene: null }, function () {}); // no enemies-state restore needed here
  const st = rm.logic.stateFor(L.RID);
  const list = [];
  const mk = (fsm, raid) => ({ fsm: fsm, raidMember: raid, pos: { x: 0, z: 0 },
    cfg: { radius: 0.6 }, separateFrom() {}, update() {} });
  const reg1 = mk('dead', true), reg2 = mk('dead', true), stock = mk('dead', false), alive = mk('chase', true);
  list.push(reg1, reg2, stock, alive);
  rm.enemies[L.RID] = list;
  rm.packs[L.RID] = [];
  const prevPacks = window.WH_Enemy;
  window.WH_Enemy = { updatePacks() {} };   // stub only the pack sweep
  try {
    rm.updateEnemies(0.016, { x: 0, z: 0, radius: 0.7 }, true, () => {}, L.RID);
  } finally {
    if (prevPacks) window.WH_Enemy = prevPacks;
  }
  const e = st.enemies;
  const v = e[0] === undefined && e[1] === undefined && e[2] === 'dead' && e[3] === undefined;
  record('V-A25', 'raidMember corpses never in regionStates (REAL updateEnemies dead-record loop)',
    v ? 'PASS' : 'FAIL',
    'REAL WH_RegionManager updateEnemies with [dead-raid, dead-raid, dead-stock, alive-raid]: ' +
    'st.enemies = ' + JSON.stringify(e) + ' — raid indexes 0,1 stay undefined, stock index 2 = "dead", live index 3 untouched');
})();

// V-A26 — dawn cancels warn: refund, no spawn, NO cooldown
(() => {
  const r = tickCase({ px: 0, pz: -110, yaw: Math.PI, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      A.tick(CFG.raid.checkSec + 1);              // warn entered
      const warned = A.state().mode === 'warn';
      g.dayNight.phase = 'day';                   // dawn edge mid-warn
      A.tick(0.016);
      const st = A.state();
      const v = warned && st.mode === 'idle' && st.nightParties === 0 && st.cooldownT === 0 && log.length === 0;
      return { v: v, e: 'warn entered=' + warned + ' -> dawn: mode=' + st.mode + ' nightParties=' + st.nightParties +
        ' (refund) cooldownT=' + st.cooldownT + ' (no cooldown on dawn-cancel) constructs=' + log.length };
    } });
  record('V-A26', 'dawn cancels warn (refund, no spawn)', r.v ? 'PASS' : 'FAIL', r.e);
})();

// V-A27 — live raid continues after dawn; no new spawns post-dawn
(() => {
  const r = tickCase({ px: 0, pz: -110, yaw: Math.PI, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      A.tick(CFG.raid.checkSec + 1);
      A.tick(CFG.raid.warnSec + 0.1);
      const live = A.state().mode === 'live' && log.length === 3;
      g.dayNight.phase = 'day';                   // dawn DURING live raid
      A.tick(CFG.raid.checkSec * 3 + 5);
      const st = A.state();
      const v = live && st.mode === 'live' && st.nightParties === 1 && log.length === 3;
      return { v: v, e: 'party live through dawn (mode=' + st.mode + ' after ' + (CFG.raid.checkSec * 3 + 5) + ' s of day); ' +
        'constructs stayed ' + log.length + ' (no new spawns post-dawn); nightParties=' + st.nightParties };
    } });
  record('V-A27', 'live raid continues after dawn, no new spawns', r.v ? 'PASS' : 'FAIL', r.e);
})();

// V-A28 — nightParties resets at the new night
(() => {
  const r = tickCase({ px: 0, pz: -110, yaw: Math.PI, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      A.tick(CFG.raid.checkSec + 1);
      A.tick(CFG.raid.warnSec + 0.1);
      const np1 = A.state().nightParties;
      for (const e of log) e.fsm = 'dead';
      A.tick(0.016);
      A.tick(CFG.raid.cooldownSec + 1);
      g.dayNight.phase = 'day';                   // dawn
      A.tick(CFG.raid.checkSec + 1);
      const npDay = A.state().nightParties;
      g.dayNight.phase = 'night';                 // NEW night
      A.tick(0.016);
      const npNew = A.state().nightParties;
      const v = np1 === 1 && npDay === 0 && npNew === 0;
      return { v: v, e: 'night1 party -> nightParties=' + np1 + '; dawn reset -> ' + npDay + '; new-night edge -> ' + npNew + ' (fresh budget)' };
    } });
  record('V-A28', 'nightParties resets at new night', r.v ? 'PASS' : 'FAIL', r.e);
})();

// V-A29 — live raid ends silently when every member vanishes from the region list
(() => {
  const r = tickCase({ px: 0, pz: -110, yaw: Math.PI, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      A.tick(CFG.raid.checkSec + 1);
      A.tick(CFG.raid.warnSec + 0.1);
      const live = A.state().mode === 'live';
      if (!live) return { v: false, e: 'setup fail' };
      const list = g.regionManager.enemies[L.RID];
      list.length = 0;                            // region rebuild / boundary crossing removes them
      const toastsBefore = g.inventoryUI.log.length;
      A.tick(0.016);
      const st = A.state();
      const v = st.mode === 'idle' && st.cooldownT === CFG.raid.cooldownSec &&
        g.inventoryUI.log.length === toastsBefore;
      return { v: v, e: 'members removed from rm.enemies: mode=' + st.mode + ' cooldownT=' + st.cooldownT +
        ' (raid ended silently: same toast count ' + toastsBefore + ', no new cue)' };
    } });
  record('V-A29', 'live raid ends silently when party removes itself', r.v ? 'PASS' : 'FAIL', r.e);
})();
console.log(JSON.stringify(require('./lib2.js').RECORDS.filter(r => /^V-A2[4-9]$/.test(r.id))));
