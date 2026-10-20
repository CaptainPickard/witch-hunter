// CC-C17v2: dump the live CONFIG rows the probes need (regionC props/enemies,
// wolfPacks, cooking stations, C roads, rotLair) to JSON. node only, no game run.
globalThis.window = globalThis; globalThis.self = globalThis;
const path = require('path'); const ROOT = path.resolve(process.argv[2]);
require(path.join(ROOT, 'prototype/js/CONFIG.js'));
const C = window.WH_CONFIG, RID = 'forest_of_the_old_king';
const out = {
  props: C.regionC.props,
  enemies: C.regionC.enemies,
  packs: C.enemy.wolfPacks.filter(p => p.regionId === RID),
  stations: C.cooking.stations.filter(s => !s.regionId || s.regionId === RID),
  roads: C.roads.filter(r => r.regionId === RID),
  rotLair: C.regionC.rotLair,
  denDoor: C.regionC.denDoor || null,
};
process.stdout.write(JSON.stringify(out));
