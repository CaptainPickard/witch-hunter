// val_A07_13.js — §5.B gate matrix (V-A07..V-A13) + V-A24 cooldown pre-step is NOT here.
'use strict';
const L = require('./lib.js');
const { record, recordGroup } = require('./lib2.js');
const { CFG, RID, G } = L;

function healFires() {
  return L.allFireRows().filter(f => !(f[0] === -60 && f[1] === -186));
}

// generic blocked-check drive: break one gate, tick ~6 frames
function blockedDrive(breaker) {
  return (g, A, log) => {
    breaker(g);
    for (let i = 0; i < 6; i++) A.tick(CFG.raid.checkSec + 1);
    const st = A.state();
    const v = st.mode === 'idle' && log.length === 0 && g.inventoryUI.log.length === 0 && st.nightParties === 0;
    return { v: v, e: 'blocked: mode=' + st.mode + ' constructs=' + log.length +
      ' toasts=' + g.inventoryUI.log.length + ' nightParties=' + st.nightParties + ' cooldownT=' + st.cooldownT };
  };
}

// generic heal-check drive: heal, debugForce, tick ~6 frames
function healedDrive(healer) {
  return (g, A, log) => {
    if (healer) healer(g);
    for (let i = 0; i < 6; i++) A.tick(CFG.raid.checkSec + 1);
    const st = A.state();
    const v = st.mode === 'live' && log.length === 3;
    return { v: v, e: 'healed+debugForce: mode=' + st.mode + ' constructs=' + log.length +
      ' types=' + log.map(e => e.type).join(',') + ' toasts=' + g.inventoryUI.log.length };
  };
}

function gateCase(id, name, breaker, healer, evNote) {
  const { tickCase } = require('./lib2.js');
  const blocked = tickCase({ px: 0, pz: -110, yaw: Math.PI, knobs: { debugMute: true }, drive: blockedDrive(breaker) });
  const healed = tickCase({ px: 0, pz: -110, yaw: Math.PI, knobs: { debugMute: true, debugForce: true }, drive: healedDrive(healer) });
  record(id, name, blocked.v && healed.v ? 'PASS' : 'FAIL',
    blocked.e + ' ;; ' + healed.e + (evNote ? ' ;; ' + evNote : ''));
}

// V-A07 g1 dormant
gateCase('V-A07', 'g1 dormant blocks',
  g => { g.dayNight.dormant = true; },
  g => { g.dayNight.dormant = false; });

// V-A08 g2 phase
gateCase('V-A08', 'g2 phase=day blocks',
  g => { g.dayNight.phase = 'day'; },
  g => { g.dayNight.phase = 'night'; });

// V-A09 g3 player dead
gateCase('V-A09', 'g3 player dead blocks',
  g => { g.player.state = 'dead'; },
  g => { g.player.state = 'alive'; });

// V-A10 g4 wrong region
gateCase('V-A10', 'g4 wrong region blocks',
  g => { g.regionManager.logic.activeId = 'regionB'; },
  g => { g.regionManager.logic.activeId = RID; });

// V-A11 g5 fire proximity (player gate, unified 50)
gateCase('V-A11', 'g5 fire proximity blocks (unified 50)',
  g => { g.player.pos.set(-60 + 40, 0, -186); },
  g => { g.player.pos.set(0, 0, -110); },
  'player-gate set = ALL CONFIG banditCampfire rows (spec); seat-gate set = regionC rows (§Files-2); both thresholded by nearFireExclusionM=' + CFG.raid.nearFireExclusionM);

// V-A12 g6 cooldown — two-part: blocked-at-cap and post-wipe cooldown window
(() => {
  const { tickCase } = require('./lib2.js');
  const blocked = tickCase({ px: 0, pz: -110, yaw: Math.PI, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      A.state().cooldownT = 999; // state() returns a fresh snapshot every call — this is a no-op by design
      // do it properly: complete a raid, then observe the cooldown window
      for (let i = 0; i < 6; i++) A.tick(CFG.raid.checkSec + 1);   // -> live (3 spawned)
      if (A.state().mode !== 'live') return { v: false, e: 'pre-set failed: mode=' + A.state().mode };
      for (const e of log) e.fsm = 'dead';
      A.tick(0.016);                                                // -> idle + cooldownT
      const stAfter = A.state();
      // re-arm with debugForce while cooldown runs: must NOT re-trigger
      log.length = 0;
      for (let i = 0; i < 6; i++) A.tick(CFG.raid.checkSec + 1);
      const stBlocked = A.state();
      const v = stAfter.mode === 'idle' && stAfter.cooldownT === CFG.raid.cooldownSec &&
        stBlocked.mode === 'idle' && log.length === 0;
      return { v: v, e: 'post-wipe cooldownT=' + stAfter.cooldownT + ' (want ' + CFG.raid.cooldownSec + ')' +
        ' ; re-trigger DURING window: mode=' + stBlocked.mode + ' constructs=' + log.length };
    } });
  record('V-A12', 'g6 cooldown blocks (post-wipe, 180 s)', blocked.v ? 'PASS' : 'FAIL', blocked.e);
})();

// V-A13 g7 night cap: 3 sub-checks
(() => {
  const { tickCase } = require('./lib2.js');
  const poses = [[0, -110], [20, -520], [120, -60]]; // kingsRoad / northRoad / eastRoad poses
  // (a) cap at 2: party1 -> wipe -> cooldown 180 -> party2 -> third blocked
  const a = tickCase({ px: 0, pz: -110, yaw: Math.PI, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      A.tick(CFG.raid.checkSec + 1);                 // party 1 warns
      A.tick(CFG.raid.warnSec + 0.1);                // party 1 spawns (3)
      const s1 = A.state();
      for (const e of log) e.fsm = 'dead';           // wipe party 1
      A.tick(0.016);                                 // raidOver -> cooldown
      const cd = A.state().cooldownT;
      A.tick(CFG.raid.cooldownSec + 1);              // cooldown elapses
      const st1 = A.state();
      g.player.pos.set(20, 0, -520);
      A.tick(CFG.raid.checkSec + 1);                 // party 2 warns
      A.tick(CFG.raid.warnSec + 0.1);                // party 2 spawns (3)
      const s2 = A.state();
      g.player.pos.set(120, 0, -60);
      log.length = 0;
      A.tick(CFG.raid.checkSec + 1);
      const s3 = A.state();
      const v = s1.nightParties === 1 && cd === CFG.raid.cooldownSec &&
        s2.nightParties === 2 &&
        s3.nightParties === CFG.raid.partiesPerNightMax && log.length === 0;
      return { v: v, e: 'cap: party1 reserved=' + s1.nightParties + ', wipe-cooldown=' + cd +
        ' (want ' + CFG.raid.cooldownSec + '), party2 -> nightParties=' + s2.nightParties +
        ' (max ' + CFG.raid.partiesPerNightMax + '); third-party constructs=' + log.length };
    } });
  // (b) 1 alive at a time: while party 1 is LIVE, a second trigger attempt does
  //     nothing observable until the live raid ends (mode gate; the cap also holds)
  const b = tickCase({ px: 0, pz: -110, yaw: Math.PI, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      A.tick(CFG.raid.checkSec + 1);
      A.tick(CFG.raid.warnSec + 0.1);      // party 1 live (3)
      const s1 = A.state();
      g.player.pos.set(20, 0, -520);
      log.length = 0;
      A.tick(CFG.raid.checkSec + 1);
      A.tick(CFG.raid.warnSec + 0.1);
      const s2 = A.state();
      const v = s1.mode === 'live' && s1.party === 3 && log.length === 0 &&
        s2.mode === 'live' && s2.party === 3 && s2.nightParties === 1;
      return { v: v, e: 'while party1 live: no second party spawns (constructs=0, mode=' + s2.mode +
        ', party=' + s2.party + ', nightParties=' + s2.nightParties + ') — 1-alive-at-a-time observable' };
    } });
  // (c) counter refunds on dead-region rebuild (region list vanish)
  const c = tickCase({ px: 0, pz: -110, yaw: Math.PI, knobs: { debugMute: true, debugForce: true },
    drive: (g, A, log) => {
      A.tick(CFG.raid.checkSec + 1);
      const sWarn = A.state();
      g.regionManager.enemies[RID] = null;  // region rebuilt under us
      A.tick(CFG.raid.warnSec + 0.1);
      const s2 = A.state();
      const v = sWarn.nightParties === 1 && s2.nightParties === 0 && s2.mode === 'idle';
      return { v: v, e: 'warn reserved=' + sWarn.nightParties + ' -> after region-list vanish: nightParties=' + s2.nightParties + ' mode=' + s2.mode };
    } });
  recordGroup('V-A13', 'g7 night cap blocks at max / 1-alive reservation / refund on rebuild', [a, b, c]);
})();
console.log(JSON.stringify(require('./lib2.js').RECORDS.filter(r => /^V-A(07|08|09|10|11|12|13)$/.test(r.id))));
