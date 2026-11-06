// V-9 ledger one-shot: WHOLE-WORD grep for pact/creditor/Undersovran/debt in
// SOURCES only, warEffort-bound (CONFIG.warEffort block + wareffort.js).
'use strict';
var H = require('/tmp/wb2_harness.js');
var cp = require('child_process');
H.out.length = 0; H.FAILS.length = 0;
var out = cp.execSync('grep -inw \'pact\\|creditor\\|Undersovran\\|debt\' /tmp/wh-worldfeat/prototype/js/wareffort.js; echo "---"; awk \'/window.WH_CONFIG.warEffort = {/,/^};/\' /tmp/wh-worldfeat/prototype/js/CONFIG.js | grep -inw \'pact\\|creditor\\|Undersovran\\|debt\'; true', {shell:'/bin/bash'}).toString();
var wareHit = out.split('---')[0].trim();
var cfgHit = out.split('---')[1] || '';
cfgHit = cfgHit.trim();
H.check('V-9 zero whole-word forbidden terms in wareffort.js', wareHit === '', JSON.stringify(wareHit));
H.check('V-9 zero whole-word forbidden terms in CONFIG.warEffort block', cfgHit === '', JSON.stringify(cfgHit));
// And the built artifact CC-WB2 sections only (the ladder block + module body
// extracted from the build, NOT other modules):
var built = require('fs').readFileSync('/tmp/wh-worldfeat/prototype/builds/v8-playable.html','utf8');
var ladderStart = built.indexOf('ladder: {');
var modStart = built.indexOf('CC-WB1 war-effort requisition board');
var modEnd = built.indexOf('window.WH_WarEffort', modStart) + 2000;
var sections = (ladderStart >= 0 ? built.slice(ladderStart, ladderStart + 900) : '') +
  (modStart >= 0 ? built.slice(modStart, modEnd) : '');
var bad = ['pact','creditor','Undersovran','debt'].filter(function (w) {
  var re = new RegExp('\\b' + w + '\\b', 'i');
  return re.test(sections);
});
H.check('V-9 built CC-WB2 sections zero forbidden terms', bad.length === 0, JSON.stringify(bad));
console.log(H.out.join('\n'));
console.log(H.FAILS.length ? 'V-9 RESULT: ' + H.FAILS.length + ' FAILURES' : 'V-9 RESULT: ALL ' + H.out.length + ' CHECKS PASS');
process.exit(H.FAILS.length ? 1 : 0);
