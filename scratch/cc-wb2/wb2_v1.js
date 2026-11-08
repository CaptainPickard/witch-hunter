// V-1 CONFIG census one-shot (cc-wb2 valspec). Node ONLY; no browser.
'use strict';
var H = require('/tmp/wb2_harness.js');
var check = H.check, CFG = H.CFG;
H.out.length = 0; H.FAILS.length = 0;

// V-1a: ladder exists with EXACTLY the 7 keys
var lad = CFG.warEffort && CFG.warEffort.ladder;
check('V-1a ladder exists', !!lad && typeof lad === 'object');
if (lad) {
  var keys = Object.keys(lad).sort();
  var want = ['basePay', 'overBonusCapPct', 'overBonusStepPct', 'overDoneText',
    'repeatBasePayStepPct', 'repeatQuotaCapMult', 'repeatQuotaGrowthPct'].sort();
  check('V-1a ladder keys exactly 7-set',
    keys.length === 7 && JSON.stringify(keys) === JSON.stringify(want),
    'keys=' + JSON.stringify(keys));
  // V-1b values EXACT per S-1
  check('V-1b basePay===0.5', lad.basePay === 0.5, String(lad.basePay));
  check('V-1b overBonusStepPct===10', lad.overBonusStepPct === 10, String(lad.overBonusStepPct));
  check('V-1b overBonusCapPct===100', lad.overBonusCapPct === 100, String(lad.overBonusCapPct));
  check('V-1b repeatQuotaGrowthPct===50', lad.repeatQuotaGrowthPct === 50, String(lad.repeatQuotaGrowthPct));
  check('V-1b repeatQuotaCapMult===3', lad.repeatQuotaCapMult === 3, String(lad.repeatQuotaCapMult));
  check('V-1b repeatBasePayStepPct===15', lad.repeatBasePayStepPct === 15, String(lad.repeatBasePayStepPct));
  check('V-1b overDoneText exact S-1 string',
    lad.overDoneText === 'Requisition filled. The quartermaster pays a bonus for the extra iron.',
    JSON.stringify(lad.overDoneText));
  check('V-1b numerics typeof number',
    typeof lad.basePay === 'number' && typeof lad.overBonusStepPct === 'number' &&
    typeof lad.overBonusCapPct === 'number' && typeof lad.repeatQuotaGrowthPct === 'number' &&
    typeof lad.repeatQuotaCapMult === 'number' && typeof lad.repeatBasePayStepPct === 'number');
}

// V-1c: boardSeat + requisition + items.warOrder byte-identical vs pre-build WB1 block
var fs = require('fs');
var preBlock = fs.readFileSync('/tmp/wb2_valspec_preflight/config_warEffort_wb1.txt', 'utf8');
// Re-extract the CURRENT warEffort block the same way (sed anchors recorded
// at pre-build: start line 3382 'window.WH_CONFIG.warEffort = {' through the
// closing '};'). Robust re-derive: capture from source text.
var src = fs.readFileSync('/tmp/wh-worldfeat/prototype/js/CONFIG.js', 'utf8').split('\n');
var start = -1, end = -1;
for (var i = 0; i < src.length; i++) {
  if (start < 0 && /window\.WH_CONFIG\.warEffort\s*=/.test(src[i])) start = i;
  else if (start >= 0 && /^\};\s*$/.test(src[i])) { end = i; break; }
}
check('V-1c warEffort block found in source', start >= 0 && end > start, 'start=' + start + ' end=' + end);
var curBlock = src.slice(start, end + 1).join('\n') + '\n';
var preNorm = preBlock.trim();
var curNorm = curBlock.trim();
// The block MAY legally grow (ladder key ADDITION). Identity law applies to
// the boardSeat/requisition rows INSIDE the block, not to the block total:
// so byte law = the PRE block text, minus its closing '};', must still be a
// substring byte-for-byte of the CURRENT block (pure addition, no edits).
var preBody = preNorm.replace(/\};\s*$/, '').trim();
check('V-1c boardSeat+requisition byte-identical (pure-additive block)',
  curNorm.indexOf(preBody) === 0 || curNorm.indexOf(preBody) >= 0,
  'preBody[0..80]=' + JSON.stringify(preBody.slice(0, 80)) + ' found=' + (curNorm.indexOf(preBody) >= 0));
// belt-and-braces: JSON identity of the three key trees vs a WB1 runtime
var preLad = preBlock.indexOf('ladder') >= 0;
var w = CFG.warEffort;
var seatWanted = { regionId: 'hold_outskirts', x: 5.9, z: -15.5, rotY: 3.14 };
check('V-1c boardSeat JSON exact',
  JSON.stringify(w.boardSeat) === JSON.stringify(seatWanted), JSON.stringify(w.boardSeat));
check('V-1c requisition JSON exact',
  JSON.stringify(w.requisition) === JSON.stringify({
    itemId: 'warOrder', oreItemId: 'ironOre', oreRequired: 6,
    reward: { id: 'stolenCoin', count: 3 }, title: 'War Requisition',
    offerText: 'The garrison wants iron for the war. Bring 6 iron ore to this board.',
    doneText: 'Requisition filled. The quartermaster marks the board.'
  }), JSON.stringify(w.requisition));
check('V-1c items.warOrder intact',
  CFG.items.warOrder && CFG.items.warOrder.glyph === 'WO' &&
  CFG.items.warOrder.category === 'document', JSON.stringify(CFG.items && CFG.items.warOrder));
check('V-1c rotYFacesRoadNorth kept true', w.rotYFacesRoadNorth === true);
check('V-1c lsKey kept', w.lsKey === 'wh_wareffort_v1');

// V-1d: git diff census — ONLY CONFIG.js + wareffort.js (+ build artifact)
var cp = require('child_process');
function git(args) {
  return cp.execSync('git ' + args + ' 2>&1', { cwd: '/tmp/wh-worldfeat' }).toString();
}
var stat = git('--no-pager diff --stat');
console.log('--- git diff --stat ---');
console.log(stat);
var statLines = stat.split('\n').filter(function (l) { return l.trim() && !/files? changed/.test(l) && !/insertion|deletion/.test(l) || /\|/.test(l); });
ok_stat: {
  var offenders = [];
  var allowed = [/prototype\/js\/CONFIG\.js/, /prototype\/js\/wareffort\.js/, /prototype\/builds\/v8-playable\.html/];
  stat.split('\n').forEach(function (l) {
    if (!l.trim() || /\|/.test(l) === false) return;
    if (!allowed.some(function (re) { return re.test(l); })) offenders.push(l);
  });
  check('V-1d diff--stat files only {CONFIG,wareffort,build}', offenders.length === 0,
    'offenders=' + JSON.stringify(offenders));
}
var hunks = git('--no-pager diff -U0 -- prototype/js/game.js prototype/index.html');
check('V-1d game.js+index.html NO hunks', hunks.trim() === '', 'got=' + hunks.slice(0, 200));
var names = git('--no-pager diff --name-only').split('\n').filter(function (l) { return l.trim(); });
check('V-1d name-only census exact', names.length === 3 &&
  names.indexOf('prototype/js/CONFIG.js') >= 0 && names.indexOf('prototype/js/wareffort.js') >= 0 &&
  names.indexOf('prototype/builds/v8-playable.html') >= 0, 'names=' + JSON.stringify(names));

// V-1e: CONFIG.js parses clean in isolation
var parse = '';
try {
  parse = cp.execSync('node -e "global.window=global; require(\'/tmp/wh-worldfeat/prototype/js/CONFIG.js\'); console.log(\'CONFIG-PARSE-OK\')" 2>&1').toString();
} catch (e) { parse = String(e.stdout || '') + String(e.stderr || e.message || ''); }
check('V-1e CONFIG parses clean', /CONFIG-PARSE-OK/.test(parse), parse.slice(0, 200));

console.log(H.out.join('\n'));
var fails = H.FAILS;
console.log(fails.length ? '\nV-1 RESULT: ' + fails.length + ' FAILURES' : '\nV-1 RESULT: ALL ' + H.out.length + ' CHECKS PASS');
process.exit(fails.length ? 1 : 0);
