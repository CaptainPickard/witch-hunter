const path = require('path');
globalThis.window = globalThis; globalThis.self = globalThis;
const W = '/tmp/wh-worldfeat/prototype';
require(path.join(W, 'vendor', 'three.classic.js'));
require(path.join(W, 'js', 'CONFIG.js'));
require(path.join(W, 'js', 'wh-ground.js'));
require(path.join(W, 'js', 'ambush.js'));
const CFG = window.WH_CONFIG, AMB = window.WH_AMBUSH;

function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const g = {
  dayNight: { dormant: false, phase: 'night' },
  player: { pos: { x: 0, z: -140, y: 0 }, yaw: 0, state: 'alive' },
  regionManager: {
    logic: { activeId: 'forest_of_the_old_king' },
    enemies: { forest_of_the_old_king: [] },
    scene: { add() {} },
  },
  inventoryUI: { toast(t, s) { console.log('TOAST', t, s); } },
};
AMB.init(g);
Math.random = mulberry32(4);
console.log('seat:', JSON.stringify(AMB.pickRaidSeat()));
