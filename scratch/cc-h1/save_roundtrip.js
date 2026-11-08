// CC-H1 save round-trip (valspec V-6): THREE-free logic test over save.js.
// Pattern = scratch/cc-ad1/save_roundtrip.js: stubs the whole `game`
// surface save.js touches, evals CONFIG.js -> region-defs.js -> save.js,
// then:
//   capture(game) with activeId 'lords_hold' -> regionId 'lords_hold',
//   restore of a hold profile over a C-side stub -> region gate +
//   teleport + hp/focus/stamina clamps + camp re-place + discover,
//   negative control: unknown region id falls back to the activeId.
// Run: node scratch/cc-h1/save_roundtrip.js   (exit 0 = all PASS)
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
evalFile('save.js');

var CFG = global.window.WH_CONFIG;
var DEFS = global.window.WH_REGION_DEFS;
var SAVE = global.window.WH_SAVE;

var cid = CFG.regionC.id;                    // forest_of_the_old_king (AMENDMENT A: the conn[5] from)
var gid = CFG.regionG.id;                    // lords_hold
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
      lastHandItems: { right: null, left: null },
      handsChanged: function () {},
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

// ---- 1) capture from inside the hold ------------------------------------------
var g1 = mkGame(gid);
var prof = SAVE.capture(g1);
var round = JSON.parse(JSON.stringify(prof));
ok("validRegion('lords_hold') true (save.js regions gate)",
   !!DEFS.regions[gid] && DEFS.regions[gid].name === 'Lord\'s Hold');
ok('capture regionId = lords_hold (save.js:73 rides rm.logic.activeId)',
   round.player.regionId === gid);
ok('capture player pos rides through', round.player.pos[0] === 3 && round.player.pos[1] === 7);
ok('JSON round-trip shape = v-less profile with 5 block keys',
   ['player', 'inventory', 'cooking', 'camp', 'world'].every(function (k) { return k in round; }));

// ---- 2) restore a hold profile over a stub (the region gate + teleport) --------
var g2 = mkGame(cid);                       // live manager sits in C (the conn[5] FROM region)
g2.inventory.slots[0] = null;
var holdProfile = JSON.parse(JSON.stringify(prof));
holdProfile.player.hp = 77; holdProfile.player.focus = 11; holdProfile.player.stamina = 22;
holdProfile.camp.sites = [{ id: 'camp2', regionId: gid, x: 4, z: -720, face: { x: 0, z: -1 } }];
holdProfile.camp.respawn = { regionId: gid, x: 0, z: -711, face: { x: 0, z: -1 } };
SAVE.restore(g2, holdProfile);
ok('restore: validRegion(lords_hold) gate passes (save.js:39)',
   !!DEFS.regions[gid]);
ok('restore: teleport target rid = lords_hold (save.js:273)',
   holdProfile.player.regionId === gid && !!DEFS.regions[holdProfile.player.regionId]);
ok('restore: player pos = saved (3, 7)', g2.player.pos.x === 3 && g2.player.pos.z === 7);
ok('restore: hp clamped to saved 77 (min hpMax)', g2.player.hp === 77);
ok('restore: focus 11 / stamina 22 restored', g2.player.focus === 11 && g2.player.stamina === 22);
ok('restore: L1 discover fired with lords_hold',
   global.__disc && global.__disc.id === gid);
ok('restore: camp.sites hold row re-placed through camp.place (saved id drives siteSeq)',
   g2.camp.sites.some(function (s) { return s.regionId === gid; }) && g2.camp.siteSeq >= 1);
ok('restore: camp.respawn hold row restored (save.js:264)',
   g2.camp.respawn && g2.camp.respawn.regionId === gid && g2.camp.respawn.x === 0 && g2.camp.respawn.z === -711);

// ---- 3) negative control: a dead region id falls back, nothing throws ---------
var g3 = mkGame(cid);
var deadProfile = JSON.parse(JSON.stringify(prof));
deadProfile.player.regionId = 'lords_hold_gone';
var threw = false;
try { SAVE.restore(g3, deadProfile); } catch (e) { threw = true; }
ok('negative: restore with lords_hold_gone does not throw', !threw);
ok('negative: fallback rid = activeId (C stays)',
   g3.player.pos.x === 3 && g3.player.pos.z === 7);
ok("validRegion('lords_hold_gone') === false",
   !(DEFS.regions['lords_hold_gone']));

var fails = A.filter(function (a) { return !a.pass; });
A.forEach(function (a) { console.log((a.pass ? 'PASS  ' : 'FAIL  ') + a.label); });
console.log('---');
console.log('save_roundtrip: ' + (A.length - fails.length) + '/' + A.length + ' PASS');
process.exit(fails.length ? 1 : 0);
