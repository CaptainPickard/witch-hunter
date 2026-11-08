globalThis.window = globalThis; globalThis.self = globalThis;
const path = require('path');
const W = '/tmp/wh-worldfeat/prototype';
require(path.join(W, 'vendor', 'three.classic.js'));
require(path.join(W, 'js', 'CONFIG.js'));
try {
  require(path.join(W, 'js', 'enemy.js'));
  console.log('enemy.js loaded OK, WH_Enemy =', typeof window.WH_Enemy,
    'updatePacks:', typeof window.WH_Enemy.updatePacks);
} catch (e) {
  console.log('enemy.js load FAILED:', e.message);
}
