// CC-C13b: plain-node mock of wolf-debug.js (no browser) - exercises the chip states
'use strict';
var fs = require('fs'), vm = require('vm');
var code = fs.readFileSync('prototype/js/wolf-debug.js', 'utf8');
function act(w, run) { return { isRunning: function () { return run; }, getEffectiveWeight: function () { return w; } }; }
function body(name) {
  var kids = [{ name: 'wolf_root' }, { name: name }];
  return { name: 'wolfGroup', traverse: function (f) { f(this); kids.forEach(f); } };
}
function run(label, enemies, clips) {
  var el = { style: {} };
  var ctx = {
    window: { location: { search: '?whdbg=1' }, WH_CONFIG: { assets: { bodyByType: { wolf: 'wolfBody' } } },
      WH_ASSETS: { getClips: function () { return new Array(clips); } },
      WH_GAME: { regionManager: { enemies: { forest_of_the_old_king: enemies } } } },
    document: { createElement: function () { return el; }, getElementById: function () { return { appendChild: function () {} }; } },
    URLSearchParams: URLSearchParams, setInterval: function () {}
  };
  vm.runInNewContext(code, ctx);
  console.log('--- ' + label + '\n' + el.textContent);
}
var healthy = { type: 'wolf', fsm: 'chase', animMoveSpeed: 5.2, rigidAnim: null, body: body('Wolf_Mesh'),
  anim: { mixer: { timeScale: 1 },
    getState: function () { return { clip: 'WH_Wolf_Walk', time: 0.43, timeScale: 1.18,
      weights: { WH_Wolf_Walk: 1, WH_Wolf_Idle: 0 }, locomotion: 'walk' }; },
    actions: { WH_Wolf_Idle: act(0, false), WH_Wolf_Walk: act(1, true), WH_Wolf_Run: act(0, false),
      WH_Wolf_Attack1: act(0, false), WH_Wolf_Hit: act(0.25, true), WH_Wolf_Death: act(0, false) } } };
run('healthy wolf', [healthy], 6);
run('0-clips smoking gun (no anim obj)', [{ type: 'wolf', fsm: 'chase', animMoveSpeed: 5.2, rigidAnim: null, body: body('Wolf_Mesh') }], 0);
run('stand-in in play', [{ type: 'wolf', fsm: 'idle', animMoveSpeed: 0, rigidAnim: null, body: body('standin-wolfBody') }], 0);
run('hostile garbage (must not throw)', [null, { type: 'wolf', fsm: 'aggro',
  anim: { getState: function () { throw new Error('x'); }, actions: { WH_Wolf_Hit: {} } },
  body: { traverse: function () { throw new Error('y'); } } }], 3);
