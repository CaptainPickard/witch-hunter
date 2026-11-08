// CC-C17v2: WH_GROUND.heightAt for a JSON list of [x, z] (stdin) -> JSON heights. node only.
globalThis.window = globalThis; globalThis.self = globalThis;
const path = require('path'); const ROOT = path.resolve(process.argv[2]);
require(path.join(ROOT, 'prototype/vendor/three.classic.js'));
require(path.join(ROOT, 'prototype/js/CONFIG.js'));
require(path.join(ROOT, 'prototype/js/wh-ground.js'));
const pts = JSON.parse(require('fs').readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(pts.map(p => +window.WH_GROUND.heightAt('forest_of_the_old_king', p[0], p[1]).toFixed(3))));
