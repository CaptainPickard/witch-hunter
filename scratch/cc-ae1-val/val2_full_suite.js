// val2_full_suite.js — Testerbot verdict-2: the ENTIRE v1 case set in ONE node
// process (valspec §7: "every V-case green in a SINGLE node run over the landed
// worktree"), post-AE1-A. Requires the val_ files in v1 order with the §0
// sanctioned seeding for the two scripts that execute at require time
// (val_A14_16.js seedRun); rest restores ambient Math.random so the v1
// seat-law streams stay byte-identical to verdict 1. Adds Testerbot's own
// V-A23 (CONFIG row digests, valspec §1 method) computed AFTER every case ran.
// Output: tmp/reg_full_records.json + tmp/reg_full_digests.json
'use strict';
const L = require('./lib.js');
const path = L.path, ROOT = L.ROOT;

// 1) A01..A06 (A02/A05 corrected re-checks land via val_A02_05_fix)
require('./val_A02_05_fix.js');

// 2) A14..A16 — seeded per §0 before the require, restored after (script runs
//    its cue->spawn transcript at require time)
const savedRandom = Math.random;
let a = 20261 >>> 0;
Math.random = function () {
  a |= 0; a = (a + 0x6D2B79F5) | 0;
  let t = Math.imul(a ^ (a >>> 15), 1 | a);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
require('./val_A14_16.js');

// 3) A07..A13 — v1 semantics with ambient Math.random restored by lib2.tickCase
//    in finally between every drive, so ambient-vs-seed differences do not leak
//    into these (each tickCase restores in finally).
require('./val_A07_13.js');

// 4) A17..A22 — verdict-1 stream preserved (ambient Math.random restored above)
Math.random = savedRandom;
require('./val_A17_22.js');

// 5) A24..A29
require('./val_A24_29.js');

// 6) A31..A33 (v1 unseeded drivers; verdict-2 adjudication uses the seeded
//    re-runs in val2_A3132_seed.js — both sets are kept in the report)
require('./val_A30_33.js');

// 7) A30 LAST — ambient CONFIG digest after ALL cases ran (its own law)
require('./val_A30_last.js');

// 8) V-A23 — Testerbot's own CONFIG-row digest law (valspec §1): sha256 over
//    JSON.stringify of the live CONFIG rows, AFTER the full suite ran.
(() => {
  const crypto = require('crypto');
  const sha = (s) => crypto.createHash('sha256').update(s).digest('hex');
  const CFG = L.CFG;
  const rows = {
    'roads': CFG.roads,
    'wolfPacks': CFG.enemy.wolfPacks,
    'regionA.enemies': CFG.regionA.enemies, 'regionA.props': CFG.regionA.props,
    'regionB.enemies': CFG.regionB.enemies, 'regionB.props': CFG.regionB.props,
    'regionC.enemies': CFG.regionC.enemies, 'regionC.props': CFG.regionC.props,
    'regionD.enemies': CFG.regionD.enemies, 'regionD.props': CFG.regionD.props,
    'regionE.enemies': CFG.regionE.enemies, 'regionE.props': CFG.regionE.props,
  };
  const want = {
    'roads': 'bcddc7d587d9e981c4cb5d8118db56fc7ba2ceec22580e622b55fd67c7f700d8',
    'wolfPacks': '057397ad1d78170d177036414f50891507ebaf02e2fa3ae2adc1c471791c3947',
    'regionA.enemies': 'b5669f0ec712b17d0b89a35e462ade4eca19bdeab264d5e7a5ebdd07ae7cf45e',
    'regionA.props': '8518111a8fe6608476ce060052f165dcba85895084ed8e324f66f6e707317578',
    'regionB.enemies': '98fe6d963156468e3b7d0a1ba4c4ecf9935da362fb6fb41d8b64b599ef3c3ebe',
    'regionB.props': '64f2682af5b1041fdbe9c7b2f50f51aa42b0edc10ec927a4e12402b913dfb11a',
    'regionC.enemies': 'cec5daf9d7e4d2b8a8b09c2be92254239eae1d2c75ca715cd61eac368eec8b49',
    'regionC.props': '7c8a5e469b0aef677cce40b6711e53c4c369c1cda2525d977aef08d592b77155',
    'regionD.enemies': '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945',
    'regionD.props': 'ab5ae3f271f1919761dd6070632aecb64989e54103b53655cd86deae9615c329',
    'regionE.enemies': '708a03a773b074547d0d70e74509d1fee6544b4f0f46c90e68b71fa69009fc2a',
    'regionE.props': 'af14b557747d0e9b0608906927d564f43d36a6960a22deddd8068b77a74eaebf',
  };
  const stats = {};
  for (const t of ['bandit', 'ghoul', 'wolf', 'coven', 'rotmother', 'rotspawn']) stats[t] = CFG.enemy[t];
  want['enemy stats'] = 'aa43438614187fa84b6e1f748a9ee97c801bec3e28abbc274263e6f5e019d897';
  const got = {};
  const drift = [];
  for (const k of Object.keys(rows)) got[k] = sha(JSON.stringify(rows[k]));
  got['enemy stats'] = sha(JSON.stringify(stats));
  for (const k of Object.keys(want)) if (got[k] !== want[k]) drift.push(k);
  const { record } = require('./lib2.js');
  record('V-A23', 'byte-sacred CONFIG rows vs §1 digests (after ALL cases ran)',
    drift.length === 0 ? 'PASS' : 'FAIL',
    drift.length === 0
      ? '13/13 digest rows match valspec §1 byte-exactly (roads, wolfPacks, regions A-E enemies+props, enemy stat rows) measured AFTER the full suite ran — AE1-A touched only the raid block, zero row drift'
      : 'drift in: ' + drift.join(', '));
})();

const { RECORDS } = require('./lib2.js');
const fs = require('fs');
fs.writeFileSync(path.join(L.TMPDIR, 'reg_full_records.json'), JSON.stringify(RECORDS, null, 1));
const npass = RECORDS.filter(r => r.result === 'PASS').length;
console.log('RECORDS ' + RECORDS.length + ' PASS ' + npass);
for (const r of RECORDS) console.log(r.id + ' ' + r.result);
