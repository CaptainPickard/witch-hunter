globalThis.window = globalThis; globalThis.self = globalThis;
const path = require('path');
const R = '/tmp/wh-worldfeat';
require(path.join(R, 'prototype/js/CONFIG.js'));
const props = globalThis.window.WH_CONFIG.regionA.props;
let holes = [];
for (let i = 0; i < props.length; i++) { if (!(i in props)) holes.push(i); }
console.log('WORKTREE length', props.length, '| holes at indexes:', holes.join(',') || 'none');
