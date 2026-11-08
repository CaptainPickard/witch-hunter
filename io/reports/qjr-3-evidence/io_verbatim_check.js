// IO inline check: A1 verbatim — spec lines vs landed CONFIG topics.
'use strict';
var fs = require('fs');
var spec = fs.readFileSync('/tmp/wh-worldfeat/io/specs/qjr-3-content-wiring-spec.md', 'utf8');
var cfg = fs.readFileSync('/tmp/wh-worldfeat/prototype/js/CONFIG.js', 'utf8');

// Pull A1 block from the spec (between 'A1.' and 'A2.')
var a1 = spec.slice(spec.indexOf('A1.'), spec.indexOf('A2.'));
function specField(topic, key) {
  var seg = a1.slice(a1.indexOf('  ' + topic + ':'), a1.indexOf('  ' + (topic === 'requisition' ? 'firstFill' : topic === 'firstFill' ? 'campRest' : 'A2') + ':'));
  var re = new RegExp("(?:^|\\n)\\s*" + key + ":\\s*(?:'((?:[^'\\\\]|\\\\.)*)'|\"((?:[^\"\\\\]|\\\\.)*)\")");
  var m = seg.match(re);
  return m ? (m[1] !== undefined ? m[1] : m[2]) : null;
}

// Pull landed topic object from CONFIG between the topic's key and the next known key
function cfgField(topic, key) {
  var next = { requisition: 'firstFill', firstFill: 'campRest', campRest: 'rescue' }[topic];
  var seg = cfg.slice(cfg.indexOf('\n    ' + topic + ': {'), cfg.indexOf('\n    ' + next + ': {'));
  var re = new RegExp("(?:^|\\n)\\s*" + key + ":\\s*(?:'((?:[^'\\\\]|\\\\.)*)'|\"((?:[^\"\\\\]|\\\\.)*)\")");
  var m = seg.match(re);
  return m ? (m[1] !== undefined ? m[1] : m[2]) : null;
}

var topics = ['requisition', 'firstFill', 'campRest'];
var keys = [['id', { requisition: 'war-effort-requisition', firstFill: 'war-effort-first-fill', campRest: 'camp-first-rest' }],
            ['title', null], ['source', null], ['body', null]];
var fails = 0, total = 0;
topics.forEach(function (t) {
  keys.forEach(function (pair) {
    var k = pair[0], forced = pair[1] && pair[1][_t];
    var sv = specField(t, k), cv = cfgField(t, k), _t = t;
    total++;
    if (sv === null) { console.log(t + '.' + k + ': SPEC-NOT-PARSED'); fails++; return; }
    if (forced && sv !== forced) { console.log(t + '.' + k + ': SPEC-ID-UNEXPECTED ' + sv); fails++; }
    if (cv === sv) { console.log(t + '.' + k + ': VERBATIM'); } else {
      console.log(t + '.' + k + ': MISMATCH');
      console.log('  spec=' + JSON.stringify(sv)); console.log('  cfg =' + JSON.stringify(cv));
      fails++;
    }
  });
});
console.log('VERBATIM ' + (total - fails) + '/' + total + (fails === 0 ? '  PASS' : '  FAIL'));
process.exit(fails === 0 ? 0 : 1);
