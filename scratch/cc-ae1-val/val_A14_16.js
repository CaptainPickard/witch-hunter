// val_A14_16.js — §5.C warn-order + spawn mechanics transcript + locked seat
'use strict';
const L = require('./lib.js');
const { record } = require('./lib2.js');
const { CFG } = L;

// one shared seeded run, unmuted + debugForce; frames of dt=0.25 across the warn window
function seedRun() {
  const { tickCase } = require('./lib2.js');
  return tickCase({
    px: 0, pz: -110, yaw: Math.PI,               // kingsRoad mid-forest pose
    knobs: { debugMute: false, debugForce: true },
    drive: (g, A, log) => {
      const frames = [];
      A.tick(0.016);                              // one eligible gate-true frame -> checkT 0.016 (< 20)
      A.tick(CFG.raid.checkSec + 0.016);          // check roll fires (debugForce) -> 'warn' + CUE
      frames.push({ t: 'after-eligible-frame', mode: A.state().mode, toasts: g.inventoryUI.log.length, constructs: log.length });
      const cueFrame = frames[0];
      const seatAtWarn = log.length === 0 ? null : null; // seat not exposed pre-spawn; captured via transcripts below
      // march dt=0.25 frames across the 2.0 s warn window
      let warnTicks = 0, firstConstructMode = null, elapsedAtFirstConstruct = 0;
      const cue = g.inventoryUI.log[0] || null;
      for (let i = 0; i < 20; i++) {
        A.tick(0.25);
        warnTicks++;
        if (log.length > 0 && firstConstructMode === null) {
          firstConstructMode = A.state().mode;
          elapsedAtFirstConstruct = warnTicks * 0.25;
          break;
        }
        if (A.state().mode === 'live') break;
      }
      const st = A.state();
      const transcript = log.map(e => ({ type: e.type, sx: e.sx, sz: e.sz, order: e.order,
        raidMember: e.raidMember, fsm: e.fsm, setYaw: typeof e.setYaw === 'number' ? e.setYaw : undefined }));
      return { g: g, log: log, transcript: transcript, cue: cue, cueFrame: cueFrame,
        firstConstructMode: firstConstructMode, elapsedAtFirstConstruct: elapsedAtFirstConstruct,
        st: st, frames: frames };
    }
  });
}

const run = seedRun();
const parts = [];

// V-A14 — cue BEFORE any construct, exact copy + duration, warn window >= warnSec
(() => {
  const cue = run.cue;
  const v = !!cue && cue.msg === CFG.raid.warnLine &&
    Math.abs(cue.dur - (CFG.raid.warnSec + 0.6)) < 1e-9 &&
    run.cueFrame.constructs === 0 && run.cueFrame.mode === 'warn' &&
    run.firstConstructMode === 'live' &&
    run.elapsedAtFirstConstruct >= CFG.raid.warnSec &&
    g_isWarnOnly(run.g);
  function g_isWarnOnly() { return run.g.inventoryUI.log.length === 1 && run.transcript.length === 3; }
  record('V-A14', 'warn-order: cue BEFORE any enemy construct', v ? 'PASS' : 'FAIL',
    'cue=' + JSON.stringify(run.cue) + ' expected msg=CFG.raid.warnLine (' + CFG.raid.warnLine.length + ' ch), dur=' + (CFG.raid.warnSec + 0.6) +
    ' ;; at cue: mode=' + run.cueFrame.mode + ' constructs=' + run.cueFrame.constructs +
    ' ;; first construct at mode=' + run.firstConstructMode + ' after ' + run.elapsedAtFirstConstruct + ' s >= warnSec ' + CFG.raid.warnSec +
    ' ;; final toasts=' + run.g.inventoryUI.log.length + ' constructs=' + run.transcript.length);
})();

// V-A15 — spawn mechanics transcript
(() => {
  const t = run.transcript;
  const orderOk = t.length === 3 && t.map(e => e.type).join(',') === 'bandit,bandit,wolf';
  const raidOk = t.every(e => e.raidMember === true);
  const fsmOk = t.every(e => e.fsm === 'chase');
  const cfgScan = t.every(e => !seatOnAnyRow(e.sx, e.sz));
  function seatOnAnyRow(x, z) {
    for (const rk of ['regionA', 'regionB', 'regionC', 'regionD', 'regionE']) {
      const reg = L.CFG[rk];
      if (!reg || !Array.isArray(reg.enemies)) continue;
      for (const r of reg.enemies) {
        if (r && r.x !== undefined && Math.abs(r.x - x) < 1e-6 && Math.abs(r.z - z) < 1e-6) return true;
      }
    }
    return false;
  }
  // yaw law: the spawn grammar sets e.yaw = atan2(px - sx, pz - sz) and copies
  // it to e.yawFrame.rotation.y. Stub now captures that. Assert BOTH the spec
  // identity (yaw == atan2(px-sx,pz-sz) at spawn coords) AND the rear-arc
  // bearing of the SEAT (|seat−player| bearing within rearSpreadDeg of yaw+PI).
  const g = run.g;
  const seat0 = { x: t[0].sx, z: t[0].sz };
  const yawOk = t.every(e => {
    if (typeof e.setYaw !== 'number') return false;
    const want = Math.atan2(g.player.pos.x - e.sx, g.player.pos.z - e.sz);
    return Math.abs(e.setYaw - want) < 1e-9;
  });
  const bearing = Math.atan2(seat0.x - g.player.pos.x, seat0.z - g.player.pos.z);
  const want = g.player.yaw + Math.PI;
  let d = bearing - want;
  while (d > Math.PI) d -= 2 * Math.PI;
  while (d < -Math.PI) d += 2 * Math.PI;
  const rearOk = Math.abs(d) <= (CFG.raid.rearSpreadDeg * Math.PI / 180) + 1e-9;
  const oneSeat = t.every(e => e.sx === seat0.x && e.sz === seat0.z);
  const noPackId = t.every(e => e.packId === undefined);
  const v = orderOk && raidOk && fsmOk && cfgScan && rearOk && yawOk && oneSeat && noPackId;
  record('V-A15', 'spawn mechanics transcript', v ? 'PASS' : 'FAIL',
    'order=' + t.map(e => e.type).join(',') + ' raidMember x3=' + raidOk + " setFsm('chase') x3=" + fsmOk +
    ' packId undefined x3=' + noPackId + ' no CONFIG row at seat=' + cfgScan +
    ' yaw==atan2(px-sx,pz-sz) x3=' + yawOk +
    ' seat=' + seat0.x.toFixed(1) + ',' + seat0.z.toFixed(1) + ' seatBearingDeviation=' + (d * 180 / Math.PI).toFixed(1) +
    ' deg (rear-arc jitter law, +-' + CFG.raid.rearSpreadDeg + ') singleSeat=' + oneSeat);
})();

// V-A16 — party seats on ONE locked seat; player move between warn and spawn is inert
(() => {
  const t = run.transcript;
  const g = run.g;
  const seat0 = { x: t[0].sx, z: t[0].sz };
  // (run continued): move the player NOW and trigger a SECOND party after the
  // first ends — its seat must be picked from the NEW pos at ITS warn time.
  const second = tickSecondParty(g, seat0);
  record('V-A16', 'party seats on ONE locked seat; seat locked at warn time', second.v ? 'PASS' : 'FAIL',
    'party1: all 3 stubs at seat ' + seat0.x.toFixed(2) + ',' + seat0.z.toFixed(2) + ' (single seat) ;; ' + second.e);
})();

// second-party check: after wipe + cooldown, move player, verify new seat matches new warn-time pos
function tickSecondParty(g, seat0) {
  const A = window.WH_AMBUSH;
  const { CFG: C } = require('./lib.js');
  const { tickCase } = require('./lib2.js');
  const RID_ = require('./lib.js').RID;
  // two INDEPENDENT seeded runs (same seed 20261): identical except the
  // post-cue player move. If the spawn state were taken at SPAWN time (not
  // warn time), the divergent move would change the seat between runs.
  function runOne(postCue) {
    return tickCase({ px: 0, pz: -110, yaw: Math.PI, knobs: { debugMute: true, debugForce: true },
      seed: 20261,
      drive: (gg, AA, log) => {
        AA.tick(C.raid.checkSec + 1);          // cue (kingsRoad pose; seed fixed by harness)
        if (AA.state().mode !== 'warn') throw new Error('run never warned: ' + AA.state().mode);
        if (postCue) gg.player.pos.set(-150, 0, -60);   // divergent AFTER cue
        AA.tick(C.raid.warnSec + 0.1);         // spawn
        return log.map(e => e.sx.toFixed(6) + ',' + e.sz.toFixed(6) + ':' + e.type);
      } });
  }
  const seatA = runOne(false);
  const seatB = runOne(true);
  const a = Array.isArray(seatA) ? seatA : seatA.log || [];
  const b = Array.isArray(seatB) ? seatB : seatB.log || [];
  const one = a.length === 3 && b.length === 3;
  const single = one && a.every(s => s.split(':')[0] === a[0].split(':')[0]);
  const locked = one && a.join('|') === b.join('|');
  return { v: one && single && locked,
    e: 'two seeded runs (seed 20261): seats identical across divergent post-cue player path=' + locked +
      ' (' + (a[0] || '-') + ' x3), single-seat=' + single +
      '; spawn state taken at WARN time (player pos at warn start locks seat + bearing)' };
}
console.log(JSON.stringify(require('./lib2.js').RECORDS.filter(r => /^V-A1[456]$/.test(r.id))));
