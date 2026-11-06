globalThis.window = globalThis; globalThis.self = globalThis;
// C1 probe: CONFIG.items.warOrder row (exact id/name/glyph/fields).
const path = require('path');
const R = '/tmp/wh-worldfeat';
require(path.join(R, 'prototype/vendor/three.classic.js'));
require(path.join(R, 'prototype/js/CONFIG.js'));
const it = window.WH_CONFIG.items.warOrder;
console.log('warOrder row:', JSON.stringify(it));
const ok = !!it && it.id === 'warOrder' && it.name === 'War Order' && it.glyph === 'WO' &&
  it.category === 'valuable' && it.stackCap === 99 && it.material === true &&
  typeof it.flavor === 'string' && it.flavor.length > 0;
console.log('C1 PASS:', ok);
process.exit(ok ? 0 : 1);
