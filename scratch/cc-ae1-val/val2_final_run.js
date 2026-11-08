// val2_final_run.js — Testerbot verdict-2 FINAL consolidated run: the entire
// case set in ONE node process over the landed worktree (valspec §7), with the
// valspec-§0-sanctioned deterministic re-runs applied as the final record for
// the cases whose v1 drivers left the setup roll to the ambient RNG stream.
// Policy (disclosed in the report): where a case has two records (v1-driver
// run + seeded deterministic run), the verdict-2 record is the DETERMINISTIC
// one; both transcripts stay in tmp/reg_full_records.json.
// Closes with: full-run ambient CONFIG digest equality (V-A30 law scope) and
// Testerbot's V-A23 CONFIG-row digests (valspec §1) measured after EVERYTHING.
'use strict';
const L = require('./lib.js');
const path = L.path, ROOT = L.ROOT;
const digestAtStart = L.oDigest(L.CFG);

// 1) A01..A06 (+ corrected A02/A05)
require('./val_A02_05_fix.js');

// 2) A07..A13 (A13's v1 record superseded by the seeded re-run below)
require('./val_A07_13.js');

// 3) A14..A16 — seeded per §0 (script fires its transcript at require time)
const savedRandom = Math.random;
let a = 20261 >>> 0;
Math.random = function () {
  a |= 0; a = (a + 0x6D2B79F5) | 0;
  let t = Math.imul(a ^ (a >>> 15), 1 | a);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
require('./val_A14_16.js');
Math.random = savedRandom;

// 4) A17..A22 — verdict-1 stream preserved (ambient Math.random restored)
require('./val_A17_22.js');

// 5) A24..A29 (v1 records; A24/A26/A27 superseded by the seeded re-runs below)
require('./val_A24_29.js');

// 6) A30 LAST among v1 files (its digest law scoped to the v1 cases)
require('./val_A30_last.js');

// 7) A31..A33 (v1 records; A31/A32 superseded below)
require('./val_A30_33.js');

// 8) deterministic §0 re-runs (append fresh records with the same ids)
require('./val2_A1230_seeds.js');   // A12, A13, A24, A26, A27, A28, A29, A30, A32
require('./val2_A3132_seed.js');    // A31, A32

// 9) full-run ambient CONFIG digest equality (extends A30's law scope)
const digestAtEnd = L.oDigest(L.CFG);
const digestEqual = digestAtStart === digestAtEnd;

// 10) Testerbot V-A23 — CONFIG row digests (valspec §1 method) after everything
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
    'enemy stats': 'aa43438614187fa84b6e1f748a9ee97c801bec3e28abbc274263e6f5e019d897',
  };
  const stats = {};
  for (const t of ['bandit', 'ghoul', 'wolf', 'coven', 'rotmother', 'rotspawn']) stats[t] = CFG.enemy[t];
  const got = {};
  for (const k of Object.keys(rows)) got[k] = sha(JSON.stringify(rows[k]));
  got['enemy stats'] = sha(JSON.stringify(stats));
  const drift = Object.keys(want).filter(k => got[k] !== want[k]);
  const { record } = require('./lib2.js');
  record('V-A23', 'byte-sacred CONFIG rows vs §1 digests (after the FULL consolidated run)',
    drift.length === 0 ? 'PASS' : 'FAIL',
    drift.length === 0
      ? '13/13 digest rows match valspec §1 byte-exactly (roads, wolfPacks, regionA-E enemies+props, enemy stat rows), measured AFTER every case ran; full-run ambient CONFIG digest equal=' + digestEqual + ' (' + digestAtEnd.slice(0, 12) + '...) — AE1-A touched only the raid block, zero row drift'
      : 'drift in: ' + drift.join(', '));
})();

const { RECORDS } = require('./lib2.js');
if (!digestEqual) {
  RECORDS.push({ id: 'V-A30b', name: 'full-run ambient digest', result: 'FAIL',
    evidence: 'ambient CONFIG digest changed across the consolidated run' });
}

// final record per id = LAST record with that id (deterministic run wins)
const fs = require('fs');
const finalById = {};
for (const r of RECORDS) finalById[r.id] = r;
const finalRecords = Object.values(finalById);
fs.writeFileSync(path.join(L.TMPDIR, 'reg_final_records.json'), JSON.stringify(finalRecords, null, 1));
fs.writeFileSync(path.join(L.TMPDIR, 'reg_all_records_full.json'), JSON.stringify(RECORDS, null, 1));
const npass = finalRecords.filter(r => r.result === 'PASS').length;
console.log('FINAL ' + finalRecords.length + ' cases, PASS ' + npass + ', FAIL ' + (finalRecords.length - npass));
for (const r of finalRecords.sort((x, y) => (parseInt(x.id.slice(4)) || 999) - (parseInt(y.id.slice(4)) || 999))) {
  console.log(r.id + ' ' + r.result);
}
