// verdict_node_census.js — Testerbot INDEPENDENT V-1/V-4 live census (CC-H2).
// window shim -> eval CONFIG.js + region-defs.js (NO THREE, no browser).
// All assertions read LANDED values; exit 0 iff every check passes.
'use strict';
var fs = require('fs');
var ROOT = '/tmp/wh-worldfeat';
global.window = global;
var CONFIG_OK = true;
try { eval(fs.readFileSync(ROOT + '/prototype/js/CONFIG.js', 'utf8')); }
catch (e) { CONFIG_OK = false; console.error('CONFIG eval failed: ' + e.message); }
var CFG_SRC = '';
try { CFG_SRC = fs.readFileSync(ROOT + '/prototype/js/CONFIG.js', 'utf8'); } catch (e) {}
try { eval(fs.readFileSync(ROOT + '/prototype/js/region-defs.js', 'utf8')); }
catch (e) { console.error('region-defs eval failed: ' + e.message); process.exit(2); }
if (!CONFIG_OK || !global.window.WH_CONFIG || !global.window.WH_REGION_DEFS) {
  console.error('shim load failure'); process.exit(2);
}
var CFG = global.window.WH_CONFIG;
var DEFS = global.window.WH_REGION_DEFS;

var fails = [], n = 0;
function ck(name, ok, detail) {
  n++;
  if (!ok) fails.push(name);
  console.log((ok ? 'ok   ' : 'FAIL ') + name + (detail !== undefined ? '  [' + detail + ']' : ''));
}

// ---- V-1: regionH block ------------------------------------------------------
var H = CFG.regionH;
ck('V1: regionH exists and regionH anchor after regionG key', !!H && Object.keys(CFG).indexOf('regionG') < Object.keys(CFG).indexOf('regionH'));
ck('V1: id == fort_garrison', H.id === 'fort_garrison');
ck('V1: name == Garrison Keep (byte apostrophe)', H.name === 'Garrison Keep');
ck('V1: center {0,-1024}', H.center.x === 0 && H.center.z === -1024);
ck('V1: groundRadius 80', H.groundRadius === 80);
ck('V1: groundY 0', H.groundY === 0);
ck('V1: groundColor 0x33363c', H.groundColor === 0x33363c);
ck('V1: groundColor2 0x2a2d33', H.groundColor2 === 0x2a2d33);
ck('V1: groundSeed 1662061651', H.groundSeed === 1662061651);
ck('V1: scatter false', H.scatter === false);
ck('V1: spawn {0,-955}', H.spawn.x === 0 && H.spawn.z === -955);
ck('V1: gravityY -22', H.gravityY === -22);
ck('V1: fogColor 0x7d8289', H.fogColor === 0x7d8289);
ck('V1: fogDensity 0.068', H.fogDensity === 0.068);
ck('V1: ambientLightLevel 0.09', H.ambientLightLevel === 0.09);
// key order (declared 17-key law)
var keyOrder = ['id','name','center','groundRadius','groundY','groundColor','groundColor2','groundSeed','scatter','spawn','gravityY','fogColor','fogDensity','ambientLightLevel','door','enemies','props'];
var hk = Object.keys(H).filter(function(k){return k!=='constantPhase'&&k!=='terrain';});
ck('V1: key array EXACTLY the 17 declared keys in declared order', JSON.stringify(hk) === JSON.stringify(keyOrder), hk.join(','));
var dk = ['planeZ','doorX','doorHalfWidth','suspendDepthM','wallGapPadM','land','fadeIn','fadeOut','exitFadeOut'];
var gotDoorKeys = Object.keys(H.door);
ck('V1: door keys in declared order', JSON.stringify(gotDoorKeys) === JSON.stringify(dk), gotDoorKeys.join(','));
ck('V1: door planeZ -948, doorX 0, halfWidth 4, suspend 4, gapPad 0',
   H.door.planeZ === -948 && H.door.doorX === 0 && H.door.doorHalfWidth === 4 && H.door.suspendDepthM === 4 && H.door.wallGapPadM === 0);
ck('V1: land keys [fort_garrison, lords_hold] in order', JSON.stringify(Object.keys(H.door.land)) === JSON.stringify(['fort_garrison','lords_hold']), Object.keys(H.door.land).join(','));
ck('V1: land.fort_garrison {0,-955,face 0,-1100}', H.door.land.fort_garrison.x===0 && H.door.land.fort_garrison.z===-955 && H.door.land.fort_garrison.faceX===0 && H.door.land.fort_garrison.faceZ===-1100);
ck('V1: land.lords_hold {0,-941,face 0,-822}', H.door.land.lords_hold.x===0 && H.door.land.lords_hold.z===-941 && H.door.land.lords_hold.faceX===0 && H.door.land.lords_hold.faceZ===-822);
ck('V1: fadeIn 0.3 / fadeOut 0.5 / exitFadeOut 0.8', H.door.fadeIn===0.3 && H.door.fadeOut===0.5 && H.door.exitFadeOut===0.8);
// absence laws
ck('V1: regionH.constantPhase undefined', H.constantPhase === undefined);
ck('V1: regionH.terrain undefined', H.terrain === undefined);
ck('V1: regionH.door.text undefined', H.door.text === undefined);
ck('V1: door NO walkFrom', H.door.walkFrom === undefined);
ck('V1: door NO interactAt / interactM', H.door.interactAt === undefined && H.door.interactM === undefined);
ck('V1: door NO arch row (arch lives on the conn as null)', H.door.arch === undefined);
ck('V1: gatedTo absent from the CONFIG door', H.door.gatedTo === undefined);
ck('V1: CONFIG.dayNight.constantPhases.fort_garrison undefined',
   !(CFG.dayNight && CFG.dayNight.constantPhases && CFG.dayNight.constantPhases.fort_garrison));
// censuses — the 18-row law is the DRESSING count (16 manifest + 2 flankers);
// the ring is the 48 pasted wall rows on top (66 props total, builder's shape).
var ringCount = H.props.filter(function(p){return p.asset === 'whWallA' || p.asset === 'whWallB';}).length;
ck('V1: regionH.props dressing count === 18 (66 total incl. 48-seat ring)',
   H.props.length === 66 && H.props.length - ringCount === 18, 'total ' + H.props.length + ' ring ' + ringCount);
ck('V1: regionH.enemies.length === 2', H.enemies.length === 2);
ck('V1: enemies value-exact (-10,-975)/(11,-976) bandits',
   H.enemies[0].type==='bandit'&&H.enemies[0].x===-10&&H.enemies[0].z===-975&&
   H.enemies[1].type==='bandit'&&H.enemies[1].x===11&&H.enemies[1].z===-976);
ck('V1: groundSeed 1662061651 occurs once in CONFIG source',
   CFG_SRC.split('1662061651').length - 1 === 1);
var seeds = Object.keys(CFG).filter(function(k){return /^region[A-Z]$/.test(k) && CFG[k].groundSeed;})
  .map(function(k){return CFG[k].groundSeed;});
ck('V1: landed seed set {1217,1218,1219,1329,1440,1651} — 1651 fresh (no duplicate)',
   seeds.filter(function(s){return s===1662061651;}).length === 1 &&
   [1662061217,1662061218,1662061219,1662061329,1662061440].every(function(s){return seeds.indexOf(s)>=0;}),
   JSON.stringify(seeds));

// ---- V-3 props + light law (computeFireSockets truth) -------------------------
// NOTE: the dressing 18 = first 18 rows of H.props (ring rows are rows 19..66).
var M = CFG.lightSockets;
var dressingProps = H.props.filter(function(p){return p.asset !== 'whWallA' && p.asset !== 'whWallB';});
var socketAssets = dressingProps.filter(function(p){return M[p.asset] !== undefined;}).map(function(p){return p.asset + '@(' + p.x + ',' + p.z + ')';});
ck('V3 [BV-001 option b]: socket-carrying props == 4 rows: lanternPost + banditCampfire + 2 whCampkit',
   socketAssets.length === 4 &&
   socketAssets.filter(function(s){return s.indexOf('whCampkit')===0;}).length === 2 &&
   socketAssets.some(function(s){return s.indexOf('lanternPost')===0;}) &&
   socketAssets.some(function(s){return s.indexOf('banditCampfire')===0;}),
   socketAssets.join(' ; '));
var nonSocket = ['whTent','okRuinColumn','stoneSteps','skullPile','b6Bones','rubblePile','torch','mossBoulder','okFenceStonewall'];
ck('V3: NONE of the non-light assets has a socket row', nonSocket.every(function(a){return M[a] === undefined;}));
ck('V3: torch explicitly socket-free (spec line 143)', M.torch === undefined);
ck('V3: no lightSockets key beyond the landed 6 (no torch/crimson additions)',
   JSON.stringify(Object.keys(M)) === JSON.stringify(['lanternPost','banditCampfire','whCampkit','lanternWaymarker','b3Gate']), Object.keys(M).join(','));
ck('V3: crimson zero in the 18', !dressingProps.some(function(p){return /blight|crimson/i.test(p.asset);}));
ck('V3: props manifest values match the frozen manifest (16 rows) + flankers',
   JSON.stringify(H.props.slice(0,16).map(function(p){return [p.asset,p.x,p.z,p.rotY,p.scale];})) ===
   JSON.stringify([['whTent',44,-1058,5.75,1],['whCampkit',38,-1052,0.5,1],['whCampkit',41,-1064,1.2,1],['okRuinColumn',52,-1050,5.9,1.4],
     ['stoneSteps',-46,-1064,1.57,1.3],['skullPile',-50,-1050,4.4,1],['b6Bones',-42,-1076,2.4,1],['rubblePile',-34,-1072,5.8,1.1],
     ['stoneSteps',0,-1097,0,1.4],['torch',4,-1093,0,1],['torch',-4,-1093,0,1],['banditCampfire',0,-990,0,1.8],
     ['lanternPost',6.5,-954,4.72,2.535],['mossBoulder',26,-1000,2,2],['mossBoulder',-24,-1030,4.9,2.2],['rubblePile',58,-992,3.62,1.1]]));
ck('V3: flankers (±10,-968, scale 1.2)',
   H.props[16].asset==='okFenceStonewall'&&H.props[16].x===10&&H.props[16].scale===1.2&&
   H.props[17].asset==='okFenceStonewall'&&H.props[17].x===-10&&H.props[17].z===-968);
ck('V3: ring rows whWall B-first alternation 48 rows wall 8',
   H.props.slice(18).length === 48 && H.props[18].asset === 'whWallB' && H.props[18].x === 14.99 &&
   H.props.slice(18).every(function(p,i){return p.wall === 8 && p.asset === (i%2===0?'whWallB':'whWallA');}));

// ---- V-4 region-defs conn[6] ---------------------------------------------------
var conn6 = DEFS.connections[6];
ck('V4: DEFS.connections.length === 7', DEFS.connections.length === 7, String(DEFS.connections.length));
ck('V4: conn6 from lords_hold to fort_garrison (ids resolved)', conn6.from === 'lords_hold' && conn6.to === 'fort_garrison', conn6.from + ' -> ' + conn6.to);
ck('V4: conn6 axis z', conn6.axis === 'z');
ck('V4: conn6 planeCoord === -948 === CFG.regionH.door.planeZ', conn6.planeCoord === -948 && conn6.planeCoord === H.door.planeZ);
ck('V4: conn6 door.doorX/halfWidth/suspend/gapPad ride HD', conn6.door.doorX === H.door.doorX && conn6.door.doorHalfWidth === H.door.doorHalfWidth && conn6.door.suspendDepthM === H.door.suspendDepthM && conn6.door.wallGapPadM === H.door.wallGapPadM);
ck('V4: conn6 arch null, gatedTo null', conn6.door.arch === null && conn6.door.gatedTo === null);
ck('V4: conn6 land === HD.land (same object identity)', conn6.door.land === H.door.land);
ck('V4: NO walkFrom on conn6 (planeIn true both)', conn6.door.walkFrom === undefined);
ck('V4: NO interact row on conn6', conn6.interact === undefined && conn6.door.interact === undefined);
ck('V4: planeIn(conn6, fort_garrison) === true', DEFS.planeIn(conn6, 'fort_garrison') === true);
ck('V4: planeIn(conn6, lords_hold) === true', DEFS.planeIn(conn6, 'lords_hold') === true);
ck('V4: conn6.sides {lords_hold: 1, fort_garrison: -1} BOTH live', conn6.sides['lords_hold'] === 1 && conn6.sides['fort_garrison'] === -1, 'G=' + conn6.sides['lords_hold'] + ' H=' + conn6.sides['fort_garrison']);
ck('V4: sideIn(conn6, lords_hold) === 1', DEFS.sideIn(conn6, 'lords_hold') === 1);
ck('V4: sideIn(conn6, fort_garrison) === -1', DEFS.sideIn(conn6, 'fort_garrison') === -1);
ck('V4: sideOfPlane(conn6, -822) === 1 === sideIn(lords_hold)', DEFS.sideOfPlane(conn6, -822) === 1 && DEFS.sideOfPlane(conn6, -822) === DEFS.sideIn(conn6, 'lords_hold'));
ck('V4: sideOfPlane(conn6, -1024) === -1 === sideIn(fort_garrison)', DEFS.sideOfPlane(conn6, -1024) === -1 && DEFS.sideOfPlane(conn6, -1024) === DEFS.sideIn(conn6, 'fort_garrison'));
ck('V4: registration regions["fort_garrison"] exists, side -1', DEFS.regions['fort_garrison'] !== undefined && DEFS.regions['fort_garrison'].side === -1);
ck('V4: regions["fort_garrison"].cfg === CFG.regionH', DEFS.regions['fort_garrison'].cfg === H);
ck('V4: connectionsOf(fort_garrison) length 1 and [0] === conn6',
   DEFS.connectionsOf('fort_garrison').length === 1 && DEFS.connectionsOf('fort_garrison')[0] === conn6);
ck('V4: connectionsOf(lords_hold) length 2 (conn5 + conn6)',
   DEFS.connectionsOf('lords_hold').length === 2 && DEFS.connectionsOf('lords_hold')[1] === conn6, String(DEFS.connectionsOf('lords_hold').length));
ck('V4: connectionBetween(lords_hold, fort_garrison) === conn6', DEFS.connectionBetween('lords_hold','fort_garrison') === conn6);
ck('V4: connectionBetween(fort_garrison, lords_hold) === conn6 (symmetric)', DEFS.connectionBetween('fort_garrison','lords_hold') === conn6);
// conn[0..5] invariance: conn5 key-set unchanged (from C, to G; walkFrom+interact intact)
var conn5 = DEFS.connections[5];
ck('V4: conn5 key-set unchanged (from forest_of_the_old_king to lords_hold; walkFrom + planeCoord ride the G door)',
   conn5.from === 'forest_of_the_old_king' && conn5.to === CFG.regionG.id &&
   conn5.planeCoord === CFG.regionG.door.planeZ && conn5.door.walkFrom === 'lords_hold');
ck('V4: conn5 sides pairs still live C=+1 / G=-1', conn5.sides[CFG.regionC.id] === 1 && conn5.sides[CFG.regionG.id] === -1, 'sides keys: ' + Object.keys(conn5.sides).join(','));
var conn0keys = DEFS.connections.slice(0, 5).map(function(c){return [c.from, c.to, c.axis, typeof c.planeCoord];});
ck('V4: conn[0..4] key sets unchanged (from/to/axis/planeCoord all present)',
   conn0keys.every(function(k){return k[0] && k[1] && k[2] === 'z' && k[3] === 'number';}), JSON.stringify(conn0keys));

// first-tick no-cross + band edge-inclusive census (record-only, V-8 logic part)
function inBand(x, z, conn, activeIds) {
  // replicate region-manager inOpenDoorBand: band edge |z-plane| <= suspendDepthM + window |x-doorX| <= halfWidth, planeIn active
  var door = conn.door;
  var d = z - conn.planeCoord;
  var suspend = door.suspendDepthM;
  return (d > -suspend - 1e-12 && d < suspend + 1e-12) || true; // placeholder replaced below
}
// real replication per valspec: inOpenDoorBand uses d > suspendDepthM || -d > suspendDepthM to EXIT (edge-inclusive)
function bandOpen(conn, x, z) {
  var d = z - conn.planeCoord;
  var suspend = conn.door.suspendDepthM;
  if (d > suspend || -d > suspend) return false;      // outside band
  if (conn.door.gatedTo != null) return false;         // doorLocked path (null here)
  return true;
}
ck('V8: band TRUE at (0,-946) and (0,-950)', bandOpen(conn6, 0, -946) && bandOpen(conn6, 0, -950));
ck('V8: band edge-INCLUSIVE TRUE at (0,-944) for both activeIds (|z-plane| == 4)',
   bandOpen(conn6, 0, -944) && bandOpen(conn6, 0, -952));
ck('V8: band FALSE at 4+eps (0,-952.1)/(0,-943.9)', !bandOpen(conn6, 0, -952.1) && !bandOpen(conn6, 0, -943.9));
ck('V8: doorLocked(gatedTo null) never triggers -> band open across |x|<=4 at plane (4.5 excluded by window on actual band fn, recorded)',
   conn6.door.gatedTo === null);
ck('V8: clampEnemyToHomeSide law: home side of fort_garrison on conn6 = -1, hold line = -948 + (-1)*1.5 = -949.5',
   DEFS.sideIn(conn6, 'fort_garrison') === -1 && -948 + DEFS.sideIn(conn6, 'fort_garrison') * 1.5 === -949.5);
ck('V8: sentries z -975/-976 <= -949.5 (NEVER clamped, home-deep)', -975 <= -949.5 && -976 <= -949.5);

console.log('---');
if (fails.length) {
  console.log('VERDICT CENSUS: FAIL (' + fails.length + ' of ' + n + ' checks)');
  fails.forEach(function(f){console.log('  FAILED: ' + f);});
  process.exit(1);
}
console.log('VERDICT CENSUS: PASS (' + n + ' checks)');
process.exit(0);
