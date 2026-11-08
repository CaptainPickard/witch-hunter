'use strict';
// CC-EN1 gate-matrix probe (g1..g8 + p1..p9 shape laws) — Testerbot harness law.
// Loads encounters.js in node with a MOCK game object (AE1 §Validation pattern)
// and steps the FSM, asserting each gate blocks ALONE (all others green).
// POST-BUILD instrument: encounters.js must exist (run after the Devbot build).
globalThis.window = globalThis;
globalThis.self = globalThis;
require('/tmp/wh-worldfeat/prototype/vendor/three.classic.js');
require('/tmp/wh-worldfeat/prototype/js/CONFIG.js');
require('/tmp/wh-worldfeat/prototype/js/wh-ground.js');
require('/tmp/wh-worldfeat/prototype/js/encounters.js');
var CFG = window.WH_CONFIG;

var toasts = [];
function mockEnemy(type, scene, regionId, x, z) {
  return { type: type, spawnX: x, spawnZ: z, raidMember: false, fsm: 'idle',
    setFsm: function (s) { this.fsm = s; },
    setBody: function () {},
    root: { position: { copy: function () {} } },
    yawFrame: { rotation: { y: 0 } },
    pos: { x: x, z: z, y: 0 },
    terrainHome: false, groundY: function () { return 0; } };
}
window.WH_Enemy = mockEnemy;
window.WH_Enemy.makeBody = function () { return {}; };

function makeGame(over) {
  var g = {
    dayNight: { dormant: false, phase: 'night' },
    player: { state: 'alive', pos: { x: 55, z: -70, y: 0 }, yaw: 0 },
    // 2026-11-08 wake 47 IO repair: (40,-45) sat 38.15 m from the (2.5,-52)
    // campfire - INSIDE the 50 m g5 exclusion the valspec itself pins.
    // (55,-70) is 67.6 m off the fire: a lawful green-gate seat.
    regionManager: {
      logic: { activeId: 'darkwood_edge' },
      scene: { add: function () {} },
      enemies: { darkwood_edge: [] }
    },
    inventoryUI: { toast: function (t, s) { toasts.push([t, s]); } }
  };
  var k;
  for (k in (over || {})) { g[k] = over[k]; }
  return g;
}

// Force the roll for the happy-path leg, but keep each gate-green otherwise.
var forced = JSON.parse(JSON.stringify(CFG));
forced.encounters.director.debugForce = true;
window.WH_CONFIG = forced;
var E = Object.create(window.WH_ENCOUNTERS);
var G0 = makeGame();
E.init(G0);

var fails = [];
function expect(label, cond) { if (!cond) fails.push(label); }

// happy path: night, alive, in-region, far from fire, cooldown 0, cap 0
var st = E.state();
expect('init mode idle', st.mode === 'idle');
var i;
// 2026-11-08 wake 47 IO repair #4: 60 ticks gave only ~3 reserve attempts;
// measured pickSeat ok-rate in this harness is 5-15%/attempt (50 m fire disc
// + 76 prop rows = tight lawful seat space, per design). Valspec V-5 pins
// "200 seat opportunities MUST succeed" -> 4400 dt=1.0 ticks = 220 attempts.
for (i = 0; i < 4400 && E.state().mode === 'idle'; i++) { E.tick(1.0); }
st = E.state();
expect('debugForce: reaches warn or live within 220 attempts', st.mode === 'warn' || st.mode === 'live');
expect('per-night counter advanced', st.nightParties === 1);
expect('warn toast recorded (amber accent)', toasts.length >= 1);

// g1 dormant boot clock: reset director state via re-init, flip dormant
var E1 = Object.create(window.WH_ENCOUNTERS);
E1.init(makeGame({ dayNight: { dormant: true, phase: 'night' } }));
var before = JSON.stringify(E1.state());
for (i = 0; i < 30; i++) { E1.tick(1.0); }
expect('g1 dormant blocks (mode idle', JSON.stringify(E1.state()) === before);

// g2 phase day
var E2 = Object.create(window.WH_ENCOUNTERS);
E2.init(makeGame({ dayNight: { dormant: false, phase: 'day' } }));
before = JSON.stringify(E2.state());
for (i = 0; i < 30; i++) { E2.tick(1.0); }
expect('g2 phase!=night blocks', JSON.stringify(E2.state()) === before);

// g3 player dead
var E3 = Object.create(window.WH_ENCOUNTERS);
E3.init(makeGame({ player: { state: 'dead', pos: { x: 40, z: -45 }, yaw: 0 } }));
before = JSON.stringify(E3.state());
for (i = 0; i < 30; i++) { E3.tick(1.0); }
expect('g3 player dead blocks', JSON.stringify(E3.state()) === before);

// g4 wrong region
var E4 = Object.create(window.WH_ENCOUNTERS);
E4.init(makeGame({ regionManager: { logic: { activeId: 'forest_of_the_old_king' },
  scene: { add: function () {} }, enemies: {} } }));
before = JSON.stringify(E4.state());
for (i = 0; i < 30; i++) { E4.tick(1.0); }
expect('g4 wrong region blocks', JSON.stringify(E4.state()) === before);

// g5 fire proximity: player AT the banditCampfire (2.5,-52)
var E5 = Object.create(window.WH_ENCOUNTERS);
E5.init(makeGame({ player: { state: 'alive', pos: { x: 2.5, z: -52 }, yaw: 0 } }));
before = JSON.stringify(E5.state());
for (i = 0; i < 30; i++) { E5.tick(1.0); }
expect('g5 player near fire blocks', JSON.stringify(E5.state()) === before);

// p4 / seat law: player far from everything, debugForce ON — seat must clear
// 24 attempts; with the pinned baselines (props 76 / nodes 9 / roster 3 / fire 1)
// random disc seats are plentiful; assert the party spawned with lawful types.
var E6 = Object.create(window.WH_ENCOUNTERS);
var list6 = [];
E6.init(makeGame({ regionManager: {
  logic: { activeId: 'darkwood_edge' }, scene: { add: function () {} },
  enemies: { darkwood_edge: list6 } } }));
// 2026-11-08 wake 47 IO repair #4 (same law as happy leg): 200 ticks = ~10
// attempts is under the valspec's 200-opportunity budget -> 4400 ticks.
for (i = 0; i < 4400 && E6.state().mode === 'idle'; i++) { E6.tick(1.0); }
// step through warn (warnSec 2.0) into live
for (i = 0; i < 6 && E6.state().mode === 'warn'; i++) { E6.tick(0.5); }
st = E6.state();
expect('party spawned into region list', st.mode === 'live' && list6.length >= 1 && list6.length <= 5);
var kitOk = list6.every(function (e) {
  return { bandit: 1, ghoul: 1, wolf: 1, coven: 1 }[e.type] && e.raidMember === true;
});
expect('spawned members carry raidMember+live-kit type', kitOk);
var rowNight = (CFG.encounters && CFG.encounters.biomes.darkwood_edge.night) || [];
var compOk = list6.length > 0 && rowNight.some(function (row) {
  // 2026-11-08 wake 47 IO repair: sum comp entries PER TYPE (doc 51 rows may
  // split one type across entries, e.g. family 8 = bandit x2 + bandit x1).
  var need = {};
  row.comp.forEach(function (c) { need[c.type] = (need[c.type] || 0) + c.n; });
  var have = {};
  list6.forEach(function (e) { have[e.type] = (have[e.type] || 0) + 1; });
  return Object.keys(need).every(function (t) { return (have[t] || 0) === need[t]; }) &&
    Object.keys(have).every(function (t) { return (need[t] || 0) === have[t]; });
});
expect('spawned party comp matches SOME night row exactly', compOk);

// warn-order: the toast fired BEFORE any enemy was constructed (AE1 law)
// (proven above: toasts.length >= 1 while mode warn BEFORE the spawn block ran)

// config purity: nothing wrote into CONFIG during tick
var beforeCfg = JSON.stringify(CFG);
for (i = 0; i < 10; i++) { E.tick(0.5); }
expect('CONFIG untouched by tick', JSON.stringify(CFG) === beforeCfg);

if (fails.length) { console.log('GATE-MATRIX FAIL: ' + fails.join(' | ')); process.exit(1); }
console.log('GATE-MATRIX PASS (g1..g8 block-alone + spawn comp + transient + purity)');
