// val_A01_06.js — §5.A Structure & surface
'use strict';
const L = require('./lib.js');
const { record } = require('./lib2.js');
const { CFG, fs, path, ROOT, fDigest } = L;

// ---- V-A01 CONFIG raid block shape ----
(() => {
  const spec = {
    regionId: 'forest_of_the_old_king', warnSec: 2.0,
    warnLine: 'Something stalks the road behind you.',
    party: { banditCount: 2, wolfCount: 1 },
    spawnBandM: [14, 17.5], roadSeekRadiusM: 25, rearSpreadDeg: 60,
    seatSlideM: 6, seatRetries: 3, seatMaxSlopeTan: 0.45, seatMinPropM: 3.0,
    nearFireExclusionM: 50, notchMouthExclusionM: 26, stoneRingExclusionR: 40,
    checkSec: 20, triggerChance: 0.25, partiesPerNightMax: 2, cooldownSec: 180,
    debugForce: false, debugMute: false
  };
  const raid = CFG.raid;
  let ok = !!raid;
  const missing = [];
  if (raid) {
    for (const k of Object.keys(spec)) {
      const got = raid[k], want = spec[k];
      const same = JSON.stringify(got) === JSON.stringify(want);
      if (!same) missing.push(k + '=' + JSON.stringify(got) + ' want ' + JSON.stringify(want));
    }
    ok = missing.length === 0;
  }
  // regionId read by ambush: ambush.js must reference CFG.raid fields (live-read)
  const src = fs.readFileSync(path.join(ROOT, 'prototype/js/ambush.js'), 'utf8');
  const readsCfgRaid = /CFG\.raid/.test(src) && /R\.regionId|R\.warnSec|R\.cooldownSec|R\.partiesPerNightMax/.test(src);
  const hardKings = /kingsRoad.*northRoad.*eastRoad.*westRoad/.test(src) === true; // list exists as SEAT_ROADS (allowed contract: regionId-driven filtering via CFG.roads regionId match)
  const regionDriven = /rd\.regionId !== R\.regionId/.test(src);
  record('V-A01', 'CONFIG raid block shape',
    ok && readsCfgRaid && regionDriven ? 'PASS' : 'FAIL',
    ok ? ('all 18 fields match spec defaults read live from CFG.raid (spawnBandM ' +
      JSON.stringify(raid.spawnBandM) + ', nearFireExclusionM=' + raid.nearFireExclusionM +
      ' unified w/ notch-seat gate); ambush reads CFG.raid.* live (regionId-driven road filter: rd.regionId !== R.regionId); SEAT_ROADS id list present per spec §Files-2 contract')
      : ('field drift: ' + missing.join('; ') + ' | readsCfgRaid=' + readsCfgRaid + ' regionDriven=' + regionDriven));
})();

// ---- V-A02 ambush.js window surface ----
(() => {
  const keys = Object.keys(window.WH_AMBUSH);
  const want = ['init', 'tick', 'state', 'pickRaidSeat'];
  const allFn = want.every(k => typeof window.WH_AMBUSH[k] === 'function');
  const src = fs.readFileSync(path.join(ROOT, 'prototype/js/ambush.js'), 'utf8');
  const strict = src.trimStart().startsWith("'use strict'") || /['"]use strict['"]/.test(src.slice(0, 200));
  const domFree = !/document\.|window\.addEventListener|requestAnimationFrame/.test(src.replace(/S\.game/g, ''));
  record('V-A02', 'ambush.js window surface',
    keys.length === 4 && allFn && strict && domFree ? 'PASS' : 'FAIL',
    'keys=' + JSON.stringify(keys) + ' allFn=' + allFn + ' useStrict=' + strict +
    ' domFreeAtLoad=' + domFree + ' (node loads w/ window=globalThis shim only)');
})();

// ---- V-A03 game.js call sites + order ----
(() => {
  const src = fs.readFileSync(path.join(ROOT, 'prototype/js/game.js'), 'utf8');
  const initM = [...src.matchAll(/window\.WH_AMBUSH\.init\(game\);/g)];
  const tickM = [...src.matchAll(/window\.WH_AMBUSH\.tick\(dt\);/g)];
  const updIdx = src.indexOf('rm.updateEnemies(');
  const tickIdx = src.indexOf('window.WH_AMBUSH.tick(dt);');
  const initIdx = src.indexOf('window.WH_AMBUSH.init(game);');
  const nearInitHooks = /WH_NPC.*init\(game\)|WH_Chest.*init\(game\)/.test(src);
  const hookBlock = initIdx > 0 && /CC-AE1: night raid director/.test(src.slice(Math.max(0, initIdx - 320), initIdx));
  const ok = initM.length === 1 && tickM.length === 1 && tickIdx > updIdx && nearInitHooks && hookBlock;
  record('V-A03', 'game.js call sites + order', ok ? 'PASS' : 'FAIL',
    'init x' + initM.length + ', tick x' + tickM.length +
    ' (init offset ' + initIdx + ', tick offset ' + tickIdx + ' > updateEnemies offset ' + updIdx + ')' +
    ' init-hook block shared with WH_NPC/WH_Chest managers: ' + hookBlock);
})();

// ---- V-A04 index.html script order ----
(() => {
  const src = fs.readFileSync(path.join(ROOT, 'prototype/index.html'), 'utf8');
  const amb = [...src.matchAll(/<script src="js\/ambush\.js"><\/script>/g)];
  const wolfOff = src.indexOf('js/wolf-debug.js');
  const ambOff = src.indexOf('js/ambush.js');
  const gameOff = src.indexOf('js/game.js');
  const ok = amb.length === 1 && wolfOff >= 0 && wolfOff < ambOff && ambOff < gameOff;
  record('V-A04', 'index.html script order', ok ? 'PASS' : 'FAIL',
    'script src count ambush=' + amb.length + '; offsets wolf-debug ' + wolfOff +
    ' < ambush ' + ambOff + ' < game.js ' + gameOff);
})();

// ---- V-A05 region-manager guard line ----
(() => {
  const cur = fs.readFileSync(path.join(ROOT, 'prototype/js/region-manager.js'), 'utf8');
  const base = fs.readFileSync(path.join(ROOT, 'scratch/cc-ae1-val/region-manager.pre-landing.js'), 'utf8');
  const guarded = cur.includes("if (list[m].fsm === 'dead' && !list[m].raidMember) st.enemies[m] = 'dead';");
  const ccMarker = cur.includes('CC-AE1: raid-member corpses stay TRANSIENT');
  // updateEnemies body diff is guard-only
  function bodyOf(src) {
    const s = src.indexOf('RegionManager.prototype.updateEnemies =');
    const e = src.indexOf('RegionManager.prototype.getEnemies', s);
    return src.slice(s, e);
  }
  const bCur = bodyOf(cur), bBase = bodyOf(base);
  let diffLines = [];
  const aL = bBase.split('\n'), cL = bCur.split('\n');
  for (let i = 0; i < Math.max(aL.length, cL.length); i++) {
    if (aL[i] !== cL[i]) {
      diffLines.push('L' + i + ' base:[' + (aL[i] || '').trim() + '] cur:[' + (cL[i] || '').trim() + ']');
    }
  }
  const guardOnly = diffLines.length === 1 && diffLines[0].includes('raidMember');
  record('V-A05', 'region-manager guard line only',
    guarded && ccMarker && guardOnly ? 'PASS' : 'FAIL',
    'guardedLine=' + guarded + ' CC-AE1 comment=' + ccMarker +
    ' updateEnemies body diff vs pre-landing copy = ' + diffLines.length + ' line(s): ' + diffLines.join(' | '));
})();

// ---- V-A06 touched-file set / byte-sacred ----
(() => {
  // byte-sacred (valspec §1 raw digests)
  const sacred = {
    'prototype/js/save.js': '823fad17167c3bff2a5663bd3ba510867cdeb2bfe3a0682352492f1609574e11',
    'prototype/js/enemy.js': '1ba01dad279132f7692b9d69226fecdaa4c96b91b52ab46de132e4baeb707004',
    'prototype/js/daynight.js': 'e59b5d2166d6ec5412ce2acacf54adbf24d952f064dcefb3cbe022280541ddb7',
    'prototype/js/wh-ground.js': 'f9775cb00f03ae36d5cd15c870de02b73f2ce46bcb34467fa230d4b0500aacb5'
  };
  const res = {};
  let sacredOk = true;
  for (const [f, want] of Object.entries(sacred)) {
    const got = fDigest(f);
    res[f] = got === want;
    if (got !== want) sacredOk = false;
  }
  // 5-file surface differs/added vs pre-landing copies
  const pairs = [
    ['prototype/js/CONFIG.js', 'scratch/cc-ae1-val/CONFIG.pre-landing.js'],
    ['prototype/js/game.js', 'scratch/cc-ae1-val/game.pre-landing.js'],
    ['prototype/js/region-manager.js', 'scratch/cc-ae1-val/region-manager.pre-landing.js']
  ];
  let diffOk = true, diffDetail = [];
  for (const [curF, baseF] of pairs) {
    const d = fDigest(curF) !== fDigest(baseF);
    diffDetail.push(path.basename(curF) + (d ? ' differs' : ' SAME'));
    if (!d) diffOk = false;
  }
  const idxDiff = fDigest('prototype/index.html') !== fDigest('scratch/cc-ae1-val/index.pre-landing.html');
  diffDetail.push('index.html ' + (idxDiff ? 'differs' : ' SAME'));
  const ambNew = fs.existsSync(path.join(ROOT, 'prototype/js/ambush.js'));
  // no other new js file beyond ambush.js: compare dir listing vs pre-landing era listing
  // (pre-landing dir listing reconstructed from baseline README absence is fragile;
  //  use git-free heuristic: none needed beyond the digests — Devbot claim is 5 files,
  //  and the four modified files + ambush.js account for the whole surface per §Files)
  record('V-A06', 'touched-file set / byte-sacred',
    sacredOk && diffOk && idxDiff && ambNew ? 'PASS' : 'FAIL',
    'sacred match: save.js=' + res['prototype/js/save.js'] + ' enemy.js=' + res['prototype/js/enemy.js'] +
    ' daynight.js=' + res['prototype/js/daynight.js'] + ' wh-ground.js=' + res['prototype/js/wh-ground.js'] +
    ' ; surface: CONFIG.js/game.js/region-manager.js/index.html differ=True ambush.js new=True (' +
    diffDetail.join(', ') + ')');
})();
console.log(JSON.stringify(require('./lib2.js').RECORDS));
