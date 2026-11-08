'use strict';
// IO one-off: measure pickSeat ok-rate in the matrix harness (repair sizing).
globalThis.window = globalThis; globalThis.self = globalThis;
require('/tmp/wh-worldfeat/prototype/vendor/three.classic.js');
require('/tmp/wh-worldfeat/prototype/js/CONFIG.js');
require('/tmp/wh-worldfeat/prototype/js/wh-ground.js');
require('/tmp/wh-worldfeat/prototype/js/encounters.js');
var CFG = window.WH_CONFIG;
CFG.encounters.director.debugForce = true;
var toasts = [];
function makeGame() {
  return { dayNight: { dormant: false, phase: 'night' },
    player: { state: 'alive', pos: { x: 55, z: -70, y: 0 }, yaw: 0 },
    regionManager: { logic: { activeId: 'darkwood_edge' },
      scene: { add: function () {} }, enemies: { darkwood_edge: [] } },
    inventoryUI: { toast: function (t, s) { toasts.push([t, s]); } } };
}
window.WH_Enemy = function () {};
window.WH_Enemy.makeBody = function () { return {}; };
var E = Object.create(window.WH_ENCOUNTERS);
E.init(makeGame());
var ok = 0, tries = 0;
for (var i = 0; i < 60; i++) {
  var seat = E.pickSeat();
  tries++;
  if (seat && seat.ok) ok++;
}
console.log('pickSeat ok-rate: ' + ok + '/' + tries);
