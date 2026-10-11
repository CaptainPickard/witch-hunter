// 2026-10-11 asset pipeline P5 gate (io/missions/2026-10-11-asset-pipeline.md):
// headless test of prototype/js/assets.js scheduling. Loads the REAL
// moveset.js + CONFIG.js + assets.js into a vm context with a stubbed THREE,
// GLTF loader, DOM and fetch layer, on a virtual clock. The fetch stub models
// the phone pipe: ONE shared link (bytes/s split across the streams in
// flight), Content-Length headers, per-attempt scripted failures, abort.
// Every assert prints PASS/FAIL; exit code 1 on any FAIL.
// Run (repo root): <playwright driver node> scratch/test_loader_scheduling.js
'use strict';
const vm = require('vm');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const JS = path.join(ROOT, 'prototype', 'js');
let passes = 0, fails = 0;
function check(label, ok, detail) {
  if (ok) passes++; else fails++;
  console.log((ok ? 'PASS ' : 'FAIL ') + label + (detail !== undefined ? '  [' + detail + ']' : ''));
}

// ---- THREE / loader / DOM stubs ---------------------------------------------
function makeThree() {
  let uid = 0;
  class Obj {
    constructor() {
      this.uuid = 'u' + (++uid); this.children = []; this.parent = null; this.name = '';
      const pos = { x: 0, y: 0, z: 0, set(x, y, z) { this.x = x; this.y = y; this.z = z; } };
      this.position = pos;
      this.scale = { setScalar() {}, set() {} };
      this.rotation = { y: 0 };
    }
    add(c) { if (c.parent) c.parent.remove(c); c.parent = this; this.children.push(c); return this; }
    remove(c) { const i = this.children.indexOf(c); if (i >= 0) this.children.splice(i, 1); c.parent = null; return this; }
    traverse(fn) { fn(this); this.children.slice().forEach(c => c.traverse(fn)); }
    updateMatrixWorld() {}
    clone() {
      const o = new this.constructor(this.geometry, this.material);
      o.name = this.name; o.position.y = this.position.y;
      this.children.forEach(c => o.add(c.clone(true)));
      return o;
    }
  }
  class Group extends Obj {}
  class Mesh extends Obj {
    constructor(g, m) { super(); this.isMesh = true; this.geometry = g; this.material = m; }
  }
  return {
    Group, Mesh,
    BoxGeometry: class { dispose() { this.disposed = true; } },
    MeshStandardMaterial: class { constructor() { this.isMeshStandardMaterial = true; this.metalness = 0; this.roughness = 1; } dispose() { this.disposed = true; } },
    Box3: class { setFromObject() { this.min = { x: -0.5, y: 0, z: -0.5 }; this.max = { x: 0.5, y: 2, z: 0.5 }; return this; } },
    LoadingManager: class { setURLModifier() {} },
    TextureLoader: class { load(url, onLoad) { T.setTimeout(() => onLoad({}), 0); } },
    DoubleSide: 2, NearestFilter: 1003, LinearMipmapLinearFilter: 1008, SRGBColorSpace: 'srgb'
  };
}
function makeDom(reg) {
  function el(tag) {
    return { tag, style: {}, children: [], textContent: '', id: '', parentNode: null,
      appendChild(c) { c.parentNode = this; this.children.push(c); if (c.id) reg[c.id] = c; return c; } };
  }
  reg['wh-hud'] = el('div');
  return {
    baseURI: 'http://phone.test/witchhunter/index.html',
    getElementById: id => reg[id] || null,
    createElement: el
  };
}

// ---- virtual clock ----------------------------------------------------------
const T = { now: 0, seq: 0, timers: [],
  setTimeout(fn, ms) { const id = ++T.seq; T.timers.push({ id, t: T.now + Math.max(0, ms || 0), fn }); return id; },
  clearTimeout(id) { T.timers = T.timers.filter(x => x.id !== id); } };
function flush() { return new Promise(r => setImmediate(r)).then(() => new Promise(r => setImmediate(r))); }
async function runUntil(cond, limitMs) {
  for (;;) {
    await flush();
    if (cond()) return true;
    if (!T.timers.length) return false;
    T.timers.sort((a, b) => a.t - b.t || a.id - b.id);
    const nx = T.timers.shift();
    if (nx.t > limitMs) { T.timers.unshift(nx); return false; }
    T.now = Math.max(T.now, nx.t);
    nx.fn();
  }
}

// ---- shared-link fetch simulator ----------------------------------------------
// spec(name, attempt) -> { size, contentLength (bool, default true),
//   mode: 'ok' | 'hangBeforeHeaders' | 'hangAfterHeaders' | 'status404',
//   rateBps (optional per-stream cap), parseError (bool) }
function makeSim(linkBps, spec) {
  const sim = { streams: new Set(), ticking: false, attempts: {}, events: [], inFlight: new Map(),
    aborts: {}, starts: {}, maxCrit: 0, maxDef: 0, maxAll: 0, deferredStartBootState: [] };
  function enc(name, n) {
    const a = new Uint8Array(n);
    const s = Buffer.from(name + '\0');
    a.set(s.subarray(0, Math.min(n, s.length)));
    return a;
  }
  function tick() {
    const live = [...sim.streams].filter(s => s.waiting && !s.stalled);
    if (!sim.streams.size) { sim.ticking = false; return; }
    const share = live.length ? linkBps * 0.1 / live.length : 0;
    live.forEach(s => {
      const cap = s.rateBps ? s.rateBps * 0.1 : Infinity;
      const n = Math.min(s.remaining, Math.floor(Math.min(share, cap)));
      if (s.remaining <= 0) { const w = s.waiting; s.waiting = null; sim.streams.delete(s); s.end(); w({ done: true }); return; }
      if (n <= 0) return;
      const chunk = s.first ? enc(s.name, n) : new Uint8Array(n);
      s.first = false; s.remaining -= n;
      const w = s.waiting; s.waiting = null; w({ done: false, value: chunk });
    });
    T.setTimeout(tick, 100);
  }
  function startTicker() { if (!sim.ticking) { sim.ticking = true; T.setTimeout(tick, 100); } }
  sim.fetch = function (url, opts) {
    if (!/\.glb$/.test(url)) {
      return Promise.resolve({ ok: true, status: 200, headers: { get: () => null },
        body: { cancel: () => Promise.resolve() } });
    }
    const name = sim.byUrl[url];
    const n = sim.attempts[name] = (sim.attempts[name] || 0) + 1;
    const sp = Object.assign({ mode: 'ok', contentLength: true }, spec(name, n));
    (sim.starts[name] = sim.starts[name] || []).push(T.now);
    const crit = sim.isCrit(name);
    if (!crit) sim.deferredStartBootState.push(sim.W().WH_ASSETS.bootState());
    sim.inFlight.set(name, crit);
    const c = [...sim.inFlight.values()];
    sim.maxCrit = Math.max(sim.maxCrit, c.filter(Boolean).length);
    sim.maxDef = Math.max(sim.maxDef, c.filter(x => !x).length);
    sim.maxAll = Math.max(sim.maxAll, c.length);
    sim.events.push({ t: T.now, name, ev: 'start', n });
    let ended = false;
    function end(ev) { if (ended) return; ended = true; sim.inFlight.delete(name); sim.events.push({ t: T.now, name, ev }); }
    return new Promise((resolve, reject) => {
      let stream = null;
      const signal = opts && opts.signal;
      if (signal) signal.addEventListener('abort', () => {
        (sim.aborts[name] = sim.aborts[name] || []).push(T.now);
        end('abort');
        const err = new Error('The operation was aborted.'); err.name = 'AbortError';
        if (stream) { sim.streams.delete(stream); if (stream.waiting) { const w = stream.waiting; stream.waiting = null; w(Promise.reject(err)); } }
        else reject(err);
      });
      if (sp.mode === 'hangBeforeHeaders') return;
      T.setTimeout(() => {
        if (ended) return;
        if (sp.mode === 'status404') { end('error'); resolve({ ok: false, status: 404, statusText: 'Not Found', headers: { get: () => null } }); return; }
        stream = { name, remaining: sp.size, first: true, waiting: null, rateBps: sp.rateBps,
          stalled: sp.mode === 'hangAfterHeaders', end: () => end('done') };
        sim.streams.add(stream);
        startTicker();
        resolve({ ok: true, status: 200,
          headers: { get: h => (/content-length/i.test(h) && sp.contentLength) ? String(sp.size) : null },
          body: { getReader: () => ({ read: () => new Promise(w => { stream.waiting = w; }) }) } });
      }, 50);
    });
  };
  return sim;
}

// ---- boot a fresh vm with the real sources ------------------------------------
function boot(opts) {
  T.now = 0; T.timers = []; T.seq = 0;
  const reg = {};
  const logs = [];
  const win = {};
  win.window = win;
  win.THREE = makeThree();
  win.document = makeDom(reg);
  win.console = { log: m => logs.push(String(m)), warn: m => logs.push(String(m)), error: m => logs.push(String(m)) };
  win.setTimeout = T.setTimeout; win.clearTimeout = T.clearTimeout;
  win.Date = { now: () => T.now };
  win.AbortController = AbortController;
  win.URL = URL; win.Math = Math; win.JSON = JSON; win.Uint8Array = Uint8Array; win.Buffer = Buffer;
  win.Map = Map; win.Promise = Promise; win.Error = Error; win.parseInt = parseInt; win.Blob = Blob;
  const ctx = vm.createContext(win);
  ['moveset.js', 'CONFIG.js'].forEach(f =>
    vm.runInContext(fs.readFileSync(path.join(JS, f), 'utf8'), ctx, { filename: f }));
  const realAssetsCfg = JSON.parse(JSON.stringify(win.WH_CONFIG.assets));
  if (opts.cfg) Object.assign(win.WH_CONFIG.assets, opts.cfg(win.WH_CONFIG.assets));
  const ANIMS = { playerBody: 43, banditBody: 6, ghoulBody: 6, playerDagClips: 9 };
  const sim = opts.sim;
  win.WHGLTFLoader = class {
    register() {}
    parse(buf, p, onLoad, onErr) {
      const b = new Uint8Array(buf);
      let name = '';
      for (let i = 0; i < Math.min(64, b.length) && b[i]; i++) name += String.fromCharCode(b[i]);
      const sp = opts.parseSpec ? opts.parseSpec(name) : {};
      T.setTimeout(() => {
        if (sp.parseError) { onErr(new Error('THREE.GLTFLoader: Unsupported binary glTF header')); return; }
        const scene = new win.THREE.Group();
        scene.name = 'gltf-root-' + name;
        scene.add(new win.THREE.Mesh({ attributes: { position: 1, normal: 1 }, dispose() {} }, { dispose() {} }));
        onLoad({ scene, animations: new Array(ANIMS[name] || 0).fill({}) });
      }, 0);
    }
  };
  win.WHSkeletonUtils = { clone: t => t.clone(true) };
  win.fetch = sim.fetch;
  vm.runInContext(fs.readFileSync(path.join(JS, 'assets.js'), 'utf8'), ctx, { filename: 'assets.js' });
  const A = win.WH_ASSETS;
  sim.byUrl = {};
  Object.keys(A.RESOLVED).forEach(n => { sim.byUrl[A.RESOLVED[n]] = n; });
  const critSet = new Set(A.CRITICAL);
  sim.isCrit = n => critSet.has(n);
  sim.W = () => win;
  return { win, A, reg, logs, realAssetsCfg };
}

const SIZE = {};
(function realSizes() {
  const src = fs.readFileSync(path.join(JS, 'assets.js'), 'utf8');
  const re = /^\s+(\w+): '(art-direction\/[^']+\.glb)'/gm;
  let m;
  while ((m = re.exec(src))) {
    try { SIZE[m[1]] = fs.statSync(path.join(ROOT, m[2])).size; } catch (e) { SIZE[m[1]] = 500000; }
  }
})();

(async function main() {
  // ===== 1. CONFIG rows + timeout clamp ==========================================
  {
    const sim = makeSim(1e6, n => ({ size: SIZE[n] }));
    const { A, realAssetsCfg: C } = boot({ sim });
    check('CONFIG.assets.assetTimeoutMsPerMb = 6000', C.assetTimeoutMsPerMb === 6000, C.assetTimeoutMsPerMb);
    check('CONFIG.assets.assetTimeoutMinMs = 20000', C.assetTimeoutMinMs === 20000, C.assetTimeoutMinMs);
    check('CONFIG.assets.assetTimeoutMaxMs = 120000', C.assetTimeoutMaxMs === 120000, C.assetTimeoutMaxMs);
    check('CONFIG.assets.criticalPoolSize = 4 / streamPoolSize = 6',
      C.criticalPoolSize === 4 && C.streamPoolSize === 6, C.criticalPoolSize + '/' + C.streamPoolSize);
    check('bootCritical: every name is a manifest asset (no drops)',
      A.CRITICAL.length === C.bootCritical.length, A.CRITICAL.length + '/' + C.bootCritical.length);
    check('bootCritical + deferred partition the manifest',
      A.CRITICAL.length + A.DEFERRED.length === Object.keys(A.MANIFEST).length,
      A.CRITICAL.length + ' + ' + A.DEFERRED.length + ' = ' + Object.keys(A.MANIFEST).length);
    const cases = [[0, 20000], [1e6, 20000], [3.4e6, 20400], [6.4e6, 38400],
      [6448742, 38692], [19.9e6, 119400], [20e6, 120000], [90e6, 120000]];
    cases.forEach(([b, want]) => {
      const got = A.timeoutForBytes(b);
      check('timeout = clamp(6000 x ' + (b / 1e6) + ' MB, 20 s, 120 s) = ' + want + ' ms', got === want, got);
    });
  }

  // ===== 2. phone-pipe boot: 1 MB/s shared link, real sizes, real CONFIG ============
  let newBootMs = 0;
  {
    const sim = makeSim(1e6, n => ({ size: SIZE[n] }));
    const { A } = boot({ sim });
    let barrierAt = -1, allAt = -1, barrierState = null, deferredSettledAtBarrier = 0;
    A.preloadAll().then(() => {
      barrierAt = T.now;
      barrierState = A.bootState();
      deferredSettledAtBarrier = A.DEFERRED.filter(n => !A.isPending(n)).length;
    });
    A.whenAllSettled().then(() => { allAt = T.now; });
    await runUntil(() => allAt >= 0, 900000);
    newBootMs = barrierAt;
    const startOrder = sim.events.filter(e => e.ev === 'start' && e.n === 1).map(e => e.name);
    const critStarts = startOrder.filter(n => sim.isCrit(n));
    check('criticals start in CONFIG.bootCritical order',
      JSON.stringify(critStarts) === JSON.stringify(A.CRITICAL), critStarts.slice(0, 4).join(','));
    const firstDef = startOrder.findIndex(n => !sim.isCrit(n));
    check('every critical starts before any deferred asset',
      firstDef === -1 || startOrder.slice(firstDef).every(n => !sim.isCrit(n)), 'first deferred at #' + firstDef);
    check('no deferred fetch starts before ALL criticals settled',
      sim.deferredStartBootState.length > 0 &&
      sim.deferredStartBootState.every(s => s.done === s.total),
      sim.deferredStartBootState.map(s => s.done + '/' + s.total).join(' '));
    check('critical pool cap respected (max concurrent critical fetches <= 4)', sim.maxCrit <= 4 && sim.maxCrit === 4, sim.maxCrit);
    check('stream pool cap respected (max concurrent deferred fetches <= 6)', sim.maxDef <= 6, sim.maxDef);
    check('never more than 6 GLB fetches in flight', sim.maxAll <= 6, sim.maxAll);
    check('boot barrier fires once criticals settled (bootState done == total)',
      barrierState && barrierState.done === barrierState.total, barrierState && barrierState.done + '/' + barrierState.total);
    check('boot barrier fires on criticals ONLY (deferred still in flight at barrier)',
      deferredSettledAtBarrier < A.DEFERRED.length && barrierAt < allAt,
      'deferred settled at barrier ' + deferredSettledAtBarrier + '/' + A.DEFERRED.length +
      ', barrier ' + (barrierAt / 1000).toFixed(1) + ' s < all ' + (allAt / 1000).toFixed(1) + ' s');
    const standIns = Object.keys(A.MANIFEST).filter(n => A.isFailed(n));
    check('1 MB/s phone pipe: 0 stand-ins with capped pools + size-scaled timeouts',
      standIns.length === 0, standIns.join(',') || '0 stand-ins, ' + A.loadedCount() + ' loaded');
    const retried = Object.keys(sim.attempts).filter(n => sim.attempts[n] > 1);
    check('1 MB/s phone pipe: no retries needed', retried.length === 0, retried.join(',') || 'none');
  }

  // ===== 3. legacy emulation: flat 20 s + all-parallel on the same pipe =============
  {
    const sim = makeSim(1e6, n => ({ size: SIZE[n] }));
    const { A } = boot({ sim, cfg: c => ({ bootCritical: Object.keys(SIZE),
      criticalPoolSize: 99, assetTimeoutMsPerMb: 0, assetTimeoutMinMs: 20000, assetTimeoutMaxMs: 20000 }) });
    let done = false;
    A.preloadAll().then(() => { done = true; });
    await runUntil(() => done, 900000);
    const standIns = Object.keys(A.MANIFEST).filter(n => A.isFailed(n));
    check('legacy config (50 parallel, flat 20 s) on the same pipe reproduces the phone stand-ins',
      standIns.length > 0 && A.isFailed('playerBody'),
      standIns.length + ' stand-ins incl. ' + standIns.slice(0, 5).join(','));
  }

  // ===== 4. scaled timeout + retries inherit + abort ===============================
  {
    // playerBody 6.4 MB: attempt 1 headers then silence, attempt 2 no headers
    // at all, attempt 3 streams at 200 KB/s (32 s > the old flat 20 s).
    const sim = makeSim(10e6, (n, k) => n !== 'playerBody' ? { size: 100000 } :
      k === 1 ? { size: 6.4e6, mode: 'hangAfterHeaders' } :
      k === 2 ? { size: 6.4e6, mode: 'hangBeforeHeaders' } :
      { size: 6.4e6, rateBps: 200000 });
    const { A } = boot({ sim, cfg: () => ({ bootCritical: ['playerBody'] }) });
    let done = false;
    A.preloadAll().then(() => { done = true; });
    await runUntil(() => done, 900000);
    const st = sim.starts.playerBody, ab = sim.aborts.playerBody || [];
    check('attempt 1 (6.4 MB Content-Length, stalled) aborted at clamp(6000 x 6.4) = 38400 ms',
      ab[0] - st[0] === 38400, ab[0] - st[0]);
    check('retry backoff unchanged (750 ms x attempt#)', st[1] - ab[0] === 750, st[1] - ab[0]);
    check('retry inherits the scaled timeout (attempt 2, no headers yet: still 38400 ms, not 20000)',
      ab[1] - st[1] === 38400, ab[1] - st[1]);
    check('timed-out fetches are aborted (signal fired per timeout)', ab.length === 2, ab.length);
    check('attempt 3 streaming 6.4 MB at 200 KB/s (~32 s) loads (flat 20 s would have killed it)',
      A.isLoaded('playerBody') && !A.isFailed('playerBody'), 'attempts ' + sim.attempts.playerBody);
    check('retry law: max 3 attempts (1 + bodyRetryCount 2)', sim.attempts.playerBody === 3, sim.attempts.playerBody);
  }

  // ===== 5. unknown size + 404 + parse failure classes ===============================
  {
    const sim = makeSim(10e6, (n, k) =>
      n === 'banditBody' ? { size: 6e6, contentLength: false, rateBps: 250000 } :
      n === 'ghoulBody' ? { size: 1e5, mode: 'status404' } : { size: 100000 });
    const { A, reg } = boot({ sim, cfg: () => ({ bootCritical: ['banditBody', 'ghoulBody', 'yewTree'] }),
      parseSpec: n => ({ parseError: n === 'yewTree' }) });
    let done = false;
    A.preloadAll().then(() => { done = true; });
    await runUntil(() => done, 900000);
    check('no Content-Length: deadline tracks bytes received (6 MB @ 250 KB/s = 24 s loads)',
      A.isLoaded('banditBody') && !A.isFailed('banditBody') && sim.attempts.banditBody === 1,
      'attempts ' + sim.attempts.banditBody);
    check('404 retries then stand-in (3 attempts)', sim.attempts.ghoulBody === 3 && A.isFailed('ghoulBody'), sim.attempts.ghoulBody);
    check('parse error does NOT retry (1 attempt, stand-in)', sim.attempts.yewTree === 1 && A.isFailed('yewTree'), sim.attempts.yewTree);
    const note = reg['wh-asset-fail-note'];
    check('failed CRITICAL assets on the loud red line',
      !!note && /ghoulBody/.test(note.textContent) && /yewTree/.test(note.textContent), note && note.textContent.slice(0, 60));
  }

  // ===== 6. late swap of deferred assets after the barrier ============================
  {
    const sim = makeSim(1e6, (n, k) =>
      n === 'ironFenceCorner' ? { size: 1e5, mode: 'status404' } :
      n === 'bushA' ? { size: 250000, rateBps: 20000 } : { size: 60000 });
    const { A, reg, logs } = boot({ sim, cfg: () => ({ bootCritical: ['longsword'] }) });
    let barrier = false, all = false;
    A.preloadAll().then(() => { barrier = true; });
    A.whenAllSettled().then(() => { all = true; });
    await runUntil(() => barrier, 900000);
    const pendingAtBarrier = A.isPending('bushA');
    const h = A.instance('bushA');
    h.position.set(5, 0, 7);
    const fenceH = A.instance('ironFenceCorner');
    const sword = A.instance('longsword');
    check('after the barrier a deferred asset is still pending', pendingAtBarrier, 'bushA pending');
    check('instance(pending) hands out a stand-in placeholder, NOT marked failed',
      /standin-bushA/.test(h.children[0].children[0].name) && !A.isFailed('bushA'), h.children[0].children[0].name);
    check('instance(critical) after the barrier = the real clone',
      sword.children[0].name === 'gltf-root-longsword', sword.children[0].name);
    await runUntil(() => all, 900000);
    check('late arrival physically swaps the stand-in (same holder, real root)',
      h.children.length === 1 && h.children[0].name === 'gltf-root-bushA', h.children[0].name);
    check('late swap keeps the caller placement transform', h.position.x === 5 && h.position.z === 7,
      h.position.x + ',' + h.position.z);
    check('late swap logged', logs.some(l => /late swap: bushA replaced 1 stand-in/.test(l)));
    check('failed deferred asset keeps its stand-in, marked failed',
      A.isFailed('ironFenceCorner') && /standin-ironFenceCorner/.test(fenceH.children[0].children[0].name));
    const note = reg['wh-asset-fail-note'], late = reg['wh-asset-fail-late'];
    check('failed deferred asset NOT on the loud critical line, on the dim streamed line',
      !!note && note.textContent === '' && !!late && /ironFenceCorner/.test(late.textContent),
      late && late.textContent.slice(0, 50));
  }

  // ===== 7. boot progress: bytes + plain-language stall line ===========================
  {
    const sim = makeSim(1e6, n => n === 'playerBody' ? { size: 6.4e6, rateBps: 100000 } : { size: 50000 });
    const { A } = boot({ sim, cfg: () => ({ bootCritical: ['playerBody', 'longsword'] }) });
    const states = [];
    A.setBootProgressCb(s => states.push(JSON.parse(JSON.stringify(s))));
    let done = false;
    A.preloadAll().then(() => { done = true; });
    await runUntil(() => done, 900000);
    const mid = states.find(s => s.stall && s.stall.elapsedMs >= 30000);
    check('progress reports bytes received for criticals',
      states.some(s => s.loadedBytes > 1e6 && s.knownBytes >= 6.4e6), states.length + ' updates');
    check('stall line data: slow asset loaded/total/elapsed past stallLineAfterMs',
      !!mid && mid.stall.name === 'playerBody' && mid.stall.total === 6.4e6 && mid.stall.loaded > 0,
      mid && ('slow link: still working, ' + (mid.stall.loaded / 1e6).toFixed(1) + ' MB of ' +
        (mid.stall.total / 1e6).toFixed(1) + ' MB, ' + Math.round(mid.stall.elapsedMs / 1000) + ' s elapsed'));
    check('final progress update = all criticals settled', states.length && states[states.length - 1].done === 2,
      states.length && states[states.length - 1].done + '/2');
  }

  console.log('\nphone-pipe sim (1 MB/s shared): boot barrier at ' + (newBootMs / 1000).toFixed(1) + ' s');
  console.log(passes + ' PASS, ' + fails + ' FAIL');
  process.exit(fails ? 1 : 0);
})().catch(e => { console.log('FAIL harness error: ' + (e && e.stack || e)); process.exit(1); });
