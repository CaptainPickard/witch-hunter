// V-2 (A1) probe: topics shape + verbatim copy, run against the REAL CONFIG.js.
'use strict';
var pass = 0, fail = 0;
function T(cond, name) { if (cond) { pass++; console.log('  ok  ' + name); } else { fail++; console.log('  FAIL ' + name); } }

global.window = global;
require('/tmp/wh-worldfeat/prototype/js/CONFIG.js');
var J = window.WH_CONFIG.journal;
var topics = J.topics;

// shape: exactly the 5 keys we know (3 QJR-3 + rescue/complete), no others
var keys = Object.keys(topics);
T(JSON.stringify(keys.slice().sort()) === JSON.stringify(['campRest', 'complete', 'firstFill', 'requisition', 'rescue']),
  'topic keys exactly {campRest,complete,firstFill,requisition,rescue}');

// no id collisions
var ids = keys.map(function (k) { return topics[k].id; });
T(new Set(ids).size === 5, 'no id collisions among 5 topics');
T(!JSON.stringify(topics).includes("'quest-findDaughter'"), "no id: 'quest-findDaughter' literal");

// pre-existing topics preserved byte-shaped
T(topics.rescue.id === 'rescue-findDaughter', 'rescue id intact');
T(topics.complete.id === 'quest-findDaughter-complete', 'complete id intact');

// verbatim copy per A1 — expected rows (escaped exactly as the spec shows)
var spec = {
  requisition: {
    id: 'war-effort-requisition',
    title: 'Requisition papers',
    source: 'The quartermaster',
    body: "I took requisition papers from the war board. The quartermaster wants iron for the front - full quota pays coin, excess pays a bonus. The garrison's hunger grows with every report from the pass."
  },
  firstFill: {
    id: 'war-effort-first-fill',
    title: 'Iron delivered',
    source: 'The quartermaster',
    body: 'Haul delivered at the war board. The quartermaster marked the tally and paid coin for the quota, a bonus for the extra. The garrison feeds the forge, the forge feeds the war.'
  },
  campRest: {
    id: 'camp-first-rest',
    title: 'Taken in at the camp',
    source: 'Camp folk',
    body: "The camp folk shared their fire and patched my wounds - for coin or kindness, they did not say. They whisper about the barrow west of the dead trees, the Old King's Barrow, where the mist keeps its own accounts."
  }
};
['requisition', 'firstFill', 'campRest'].forEach(function (k) {
  var t = topics[k];
  T(t.id === spec[k].id, k + '.id verbatim (' + t.id + ')');
  T(t.title === spec[k].title, k + '.title verbatim');
  T(t.source === spec[k].source, k + '.source verbatim');
  T(t.body === spec[k].body, k + '.body verbatim');
  // em-dash/hyphen law: bodies spell the separator as a plain hyphen
  if (k !== 'firstFill') T(!/\u2014|\u2013/.test(t.body), k + '.body hyphen (no em-dash)');
});

// day/source law support: A9 — these appends pass no day arg (checked in probes);
// check journal.text seeds untouched
T(J.text.dayStamp === 'Day {day} - {source}', 'journal.dayStamp untouched');
T(J.text.seedBody === "Farmer Aldric: the Old King's Barrow, west past the dead trees. Bring her home.", 'seed body intact (barrow lore still anchored by QJR-3 campRest wording)');

console.log('V2-CHECK ' + pass + '/' + (pass + fail));
process.exit(fail ? 1 : 0);
