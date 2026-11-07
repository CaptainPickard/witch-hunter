// CC-H6 save round-trip (THREE-free): evals CONFIG.js -> region-defs.js ->
// save.js with global.window = {} (the cc-ad1 pattern), then:
//   SR-1 capture rides (regionId, pos) through WH_SAVE.capture,
//   SR-2 restore over the L profile (gates, discover, teleport),
//   SR-3 negative control: dead region id falls back to the activeId,
//   SR-4 lair key round-trip: lastchancel_cleared_L captured by
//        WH_Enemy.captureLairs -> restoreLairs -> re-captured byte-equal.
// Run: node scratch/cc-h6/save_roundtrip.js   (exit 0 = all PASS)
'use strict';
var fs = require('fs');
var path = require('path');

global.window = {};
global.localStorage = { getItem: function () { return null; }, setItem: function () {}, removeItem: function () {} };
global.THREE = undefined;
global.WH_LEVEL = {
  capture: function () { return ({ knownRegions: 'stub' }); },
  restore: function () {},
  discover: function (kind, id) { global.__disc = { kind: kind, id: id }; }
};
global.window.WH_LEVEL = global.WH_LEVEL;   // save.js reads window.WH_LEVEL directly

var ROOT = path.join(__dirname, '..', '..', 'prototype', 'js');
function evalFile(name) { (0, eval)(fs.readFileSync(path.join(ROOT, name), 'utf8')); }
evalFile('CONFIG.js');
evalFile('region-defs.js');
evalFile('enemy.js');
evalFile('save.js');

var CFG = global.window.WH_CONFIG;
var DEFS = global.window.WH_REGION_DEFS;
var SAVE = global.window.WH_SAVE;
var ENEMY = global.window.WH_Enemy;

var kid = CFG.regionK.id, lid = CFG.regionL.id;      // tithe_vaults / the_remains
var A = [];
function ok(label, cond) { A.push({ label: label, pass: !!cond }); }
function mkGame(activeId) {
  return {
    player: {
      hp: 10, hpMax: 100, focus: 5, focusMax: 50, stamina: 3, staminaMax: 40,
      pos: { x: 3, z: 7 }, yaw: 1.2, camYaw: 1.2,
      hands: { right: 'dagger', left: null }, belt: [],
      bindings: { main: 0, off: 0 }, consumables: [],
      getConsumables: function () { return []; },
      toggling: false, toggleTimer: 0, pendingQSwap: null, dropPendingCast: function () {},
      lastHandItems: { right: null, left: null }, handsChanged: function () {},
      equipItem: function () {}, respawnAt: function (x, z) { this.pos = { x: x, z: z }; },
      isCasterHand: function () { return false; }
    },
    inventory: { slots: new Array(CFG.belt.slots + 4).fill(null), changed: function () {} },
    cooking: {
      buffs: { list: function () { return []; }, clear: function () {}, add: function () {} },
      recipes: null, kitAcquired: false, mealDay: -1, channel: null, open: false,
      kitBtn: null, setOpen: function () {}, lastHp: 0
    },
    camp: {
      sites: [], respawn: null, siteSeq: 0, placing: false, stopPlacing: function () {},
      packUp: function (s) { this.sites = this.sites.filter(function (x) { return x !== s; }); },
      place: function (rid, x, z, f) { this.sites.push({ id: 'camp1', regionId: rid, x: x, z: z, f: f, group: null }); }
    },
    dayNight: {
      day: 2, phase: 'day', timeOfDay: 0.5, dormant: false, fresh: false, clock: 100, sky: null, tick: function () {}
    },
    regionManager: { logic: { activeId: activeId }, logic2: null },
    classId: null,
    inventoryUI: null,
    c4: {}
  };
}

// ---- SR-1: capture from inside the remains ---------------------------------
var g1 = mkGame(lid);
var prof = SAVE.capture(g1);
var round = JSON.parse(JSON.stringify(prof));
ok('SR-1 capture regionId = the_remains', round.player.regionId === lid);
ok('SR-1 capture player pos rides through', round.player.pos[0] === 3 && round.player.pos[1] === 7);
ok('SR-1 JSON round-trip shape = v-less profile with 5 block keys',
   ['player', 'inventory', 'cooking', 'camp', 'world'].every(function (k) { return k in round; }));

// ---- SR-2: restore an L profile over a stub living in K ---------------------
var g2 = mkGame(kid);                        // live manager sits in K
g2.inventory.slots[0] = null;
var remainsProfile = JSON.parse(JSON.stringify(prof));
remainsProfile.player.hp = 77; remainsProfile.player.focus = 11; remainsProfile.player.stamina = 22;
remainsProfile.camp.sites = [{ id: 'camp2', regionId: lid, x: 0, z: -1044, face: { x: 0, z: -1 } }];
remainsProfile.camp.respawn = { regionId: lid, x: 0, z: -1044, face: { x: 0, z: -1 } };
SAVE.restore(g2, remainsProfile);
ok('SR-2 restore: validRegion(the_remains) gate passes (save.js:39)',
   !!DEFS.regions[lid]);
ok('SR-2 restore: teleport target rid = the_remains (save.js:273)',
   remainsProfile.player.regionId === lid && !!DEFS.regions[remainsProfile.player.regionId]);
ok('SR-2 restore: player pos = saved (3, 7)', g2.player.pos.x === 3 && g2.player.pos.z === 7);
ok('SR-2 restore: hp clamped to saved 77 (min hpMax)', g2.player.hp === 77);
ok('SR-2 restore: focus 11 / stamina 22 restored', g2.player.focus === 11 && g2.player.stamina === 22);
ok('SR-2 restore: L1 discover fired with the_remains',
   global.__disc && global.__disc.id === lid);
ok('SR-2 restore: camp.sites remains row re-placed through camp.place (saved id drives siteSeq)',
   g2.camp.sites.some(function (s) { return s.regionId === lid; }) && g2.camp.siteSeq >= 1);
ok('SR-2 restore: camp.respawn remains row restored (save.js:264)',
   g2.camp.respawn && g2.camp.respawn.regionId === lid && g2.camp.respawn.x === 0 && g2.camp.respawn.z === -1044);

// ---- SR-3: negative control: a dead region id falls back --------------------
var g3 = mkGame(kid);
var deadProfile = JSON.parse(JSON.stringify(prof));
deadProfile.player.regionId = 'the_remains_gone';
var threw = false;
try { SAVE.restore(g3, deadProfile); } catch (e) { threw = true; }
ok('SR-3 negative: restore with the_remains_gone does not throw', !threw);
ok('SR-3 negative: fallback rid = activeId (K stays)',
   g3.player.pos.x === 3 && g3.player.pos.z === 7);
ok('SR-3 validRegion(the_remains_gone) === false',
   !DEFS.regions['the_remains_gone']);

// ---- SR-4: the CC-H6 lair key: lastchancel_cleared_L ------------------------
// Enemy law (enemy.js): lairOnDeath files LAIR_STATE[L.nest.letter] with
// prefix from cfg.lair.flagPrefix; captureLairs emits (prefix||rotmother) +
// '_cleared_' + letter; restoreLairs REPLACES the whole LAIR_STATE table
// (it is the profile-load entry: LAIR_STATE = {} first), so the load shape
// restores every cleared-key in ONE pass.
var lairsBlock = ENEMY.captureLairs();
ok('SR-4 pre-clear capture has NO lastchancel_cleared_L key',
   !('lastchancel_cleared_L' in lairsBlock));
ENEMY.restoreLairs({ lastchancel_cleared_L: 2 });
lairsBlock = ENEMY.captureLairs();
ok('SR-4 restoreLairs({lastchancel_cleared_L: 2}) then captureLairs => key present at day 2',
   lairsBlock.lastchancel_cleared_L === 2);
// The load shape: BOTH keys (the landed K key + the new L key) restore in
// one pass and re-capture byte-equal (letter = the flag.region letter).
ENEMY.restoreLairs({ tithecaptain_cleared_K: 4, lastchancel_cleared_L: 2 });
lairsBlock = ENEMY.captureLairs();
ok('SR-4 load shape: one pass restores tithecaptain_cleared_K + lastchancel_cleared_L, re-capture byte-equal',
   lairsBlock.tithecaptain_cleared_K === 4 && lairsBlock.lastchancel_cleared_L === 2 &&
   JSON.stringify(lairsBlock) === '{"tithecaptain_cleared_K":4,"lastchancel_cleared_L":2}');
// negative: malformed keys are dropped by the loader regex, nothing throws.
var threw4 = false;
try { ENEMY.restoreLairs({ 'not-a-lair-key': 1, LASTCHANCEL_lowercase_l: 1,
                           tithecaptain_cleared_K: 4, lastchancel_cleared_L: 2 }); } catch (e) { threw4 = true; }
lairsBlock = ENEMY.captureLairs();
ok('SR-4 negative: malformed lair keys are dropped (no throw, no invented keys)',
   !threw4 && !('not-a-lair-key' in lairsBlock) && !('LASTCHANCEL' in lairsBlock) &&
   lairsBlock.lastchancel_cleared_L === 2 && lairsBlock.tithecaptain_cleared_K === 4);

var fails = A.filter(function (a) { return !a.pass; });
A.forEach(function (a) { console.log((a.pass ? 'PASS  ' : 'FAIL  ') + a.label); });
console.log('---');
console.log('save_roundtrip: ' + (A.length - fails.length) + '/' + A.length + ' PASS');
process.exit(fails.length ? 1 : 0);
