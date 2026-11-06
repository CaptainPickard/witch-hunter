// val_A02_05_fix.js — corrected re-checks for V-A02 and V-A05; overwrites those records.
'use strict';
const L = require('./lib.js');
const { RECORDS } = require('./lib2.js');
require('./val_A01_06.js'); // seed the full record set, then override A02/A05
const { fs, path, ROOT } = L;

function setRecord(id, name, result, evidence) {
  const prev = RECORDS.find(r => r.id === id);
  if (prev) { prev.name = name; prev.result = result; prev.evidence = evidence; }
}

// ---- V-A02 ambush.js window surface (directive may sit inside the IIFE) ----
(() => {
  const keys = Object.keys(window.WH_AMBUSH);
  const want = ['init', 'tick', 'state', 'pickRaidSeat'];
  const allFn = want.every(k => typeof window.WH_AMBUSH[k] === 'function');
  const src = fs.readFileSync(path.join(ROOT, 'prototype/js/ambush.js'), 'utf8');
  const strict = /['"]use strict['"];/.test(src);
  const domFree = !/\bdocument\.|\bwindow\.addEventListener|\brequestAnimationFrame/.test(src);
  const iife = /\}\)\(\);/.test(src.slice(-120));
  setRecord('V-A02', 'ambush.js window surface',
    keys.length === 4 && allFn && strict && domFree && iife ? 'PASS' : 'FAIL',
    'keys=' + JSON.stringify(keys) + ' allFn=' + allFn + "'use strict' present=" + strict +
    ' (IIFE-scoped directive at ambush.js:' + (src.indexOf("'use strict'") + 1) + ')' +
    ' domFreeAtLoad=' + domFree + ' IIFE=' + iife + ' (node loads w/ window=globalThis shim only)');
})();

// ---- V-A05 region-manager guard line (normalized: comment lines stripped) ----
(() => {
  const cur = fs.readFileSync(path.join(ROOT, 'prototype/js/region-manager.js'), 'utf8');
  const base = fs.readFileSync(path.join(ROOT, 'scratch/cc-ae1-val/region-manager.pre-landing.js'), 'utf8');
  const guarded = cur.includes("if (list[m].fsm === 'dead' && !list[m].raidMember) st.enemies[m] = 'dead';");
  const ccMarker = cur.includes('CC-AE1: raid-member corpses stay TRANSIENT');
  function bodyOf(src) {
    const s = src.indexOf('RegionManager.prototype.updateEnemies =');
    const e = src.indexOf('RegionManager.prototype.getEnemies', s);
    return src.slice(s, e);
  }
  const code = t => t.split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('//'));
  const a = code(bodyOf(base)), b = code(bodyOf(cur));
  const diffs = [];
  for (let i = 0; i < Math.max(a.length, b.length); i++) {
    if (a[i] !== b[i]) diffs.push('base:[' + (a[i] || '<none>') + '] cur:[' + (b[i] || '<none>') + ']');
  }
  const guardOnly = diffs.length === 1 &&
    diffs[0].includes("fsm === 'dead'") && diffs[0].includes('raidMember');
  setRecord('V-A05', 'region-manager guard line only',
    guarded && ccMarker && guardOnly ? 'PASS' : 'FAIL',
    'guardedLine=' + guarded + ' CC-AE1 disclosure comment=' + ccMarker +
    ' ; updateEnemies code-line diff (comments stripped) = ' + diffs.length + ': ' + diffs.join(' | '));
})();
console.log(JSON.stringify(RECORDS.filter(r => ['V-A02', 'V-A05'].includes(r.id))));
