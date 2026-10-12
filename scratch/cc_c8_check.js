// CC-C8 headless validation checker (Testerbot). node scratch/cc_c8_check.js
// vm-evals CONFIG.js + region-defs.js + region-manager.js (logic half only)
// with a window stub, scans GLB headers for tris / x-extent, greps sources
// for line evidence, node --check on every edited js, scope-audits the diff.
// No harness, no browser, no game run, no network.
var fs = require('fs'), vm = require('vm'), cp = require('child_process');
var BASE = process.argv[2] || 'a631fa6', HEAD = process.argv[3] || 'eae8cbe', C7 = 'bef33f1';
var J = 'prototype/js/';
function src(f) { return fs.readFileSync(J + f, 'utf8').split('\n'); }
function L(f, re) {
  var out = [];
  src(f).forEach(function (l, i) { if (re.test(l)) out.push(i + 1); });
  return out.length ? out.join(',') : 'NONE';
}
function has(f, re) { return L(f, re) !== 'NONE'; }
var res = [];
function check(id, name, ok, ev) { res.push({ id: id, name: name, ok: !!ok, ev: ev }); }
function eq(a, b) { return JSON.stringify(a) === JSON.stringify(b); }
function near(a, b, t) { return Math.abs(a - b) <= (t || 1e-6); }
function git(a) { return cp.execFileSync('git', a, { encoding: 'utf8', maxBuffer: 64 << 20 }); }

// ---- load HEAD config + defs + manager logic ---------------------------------
var ctx = { window: {}, console: console }; ctx.window.window = ctx.window; vm.createContext(ctx);
['CONFIG.js', 'region-defs.js', 'region-manager.js'].forEach(function (f) {
  vm.runInContext('(function(window){' + fs.readFileSync(J + f, 'utf8') + '\n}).call(window, window);', ctx);
});
var W = ctx.window, C = W.WH_CONFIG, DEFS = W.WH_REGION_DEFS, RD = C.regionD, RC = C.regionC;
// C7 config for byte-equal comparison
var c7 = { window: {} }; vm.createContext(c7);
vm.runInContext(git(['show', C7 + ':prototype/js/CONFIG.js']), c7);
var C7C = c7.window.WH_CONFIG;
var c7base = { window: {} }; vm.createContext(c7base);
vm.runInContext(git(['show', BASE + ':prototype/js/CONFIG.js']), c7base);
var CB = c7base.window.WH_CONFIG;

// ---- GLB scan (tris + raw x extent) ------------------------------------------
var manifest = {};
src('assets.js').forEach(function (l) {
  var m = /^\s+(\w+): '(art-direction\/[^']+\.glb)'/.exec(l);
  if (m) manifest[m[1]] = m[2];
});
var glbCache = {};
function glb(key) {
  if (glbCache[key]) return glbCache[key];
  var p = manifest[key];
  if (!p || !fs.existsSync(p)) return (glbCache[key] = { tris: NaN, extX: NaN, path: p || '?' });
  var b = fs.readFileSync(p), n = b.readUInt32LE(12), j = JSON.parse(b.slice(20, 20 + n).toString());
  var tris = 0, mn = 1e9, mx = -1e9;
  (j.meshes || []).forEach(function (m) {
    m.primitives.forEach(function (pr) {
      if ((pr.mode === undefined ? 4 : pr.mode) !== 4) return;
      tris += Math.floor(j.accessors[pr.indices !== undefined ? pr.indices : pr.attributes.POSITION].count / 3);
      var a = j.accessors[pr.attributes.POSITION];
      if (a.min) { mn = Math.min(mn, a.min[0]); mx = Math.max(mx, a.max[0]); }
    });
  });
  return (glbCache[key] = { tris: tris, extX: mx - mn, path: p });
}
function triSum(rows) { return rows.reduce(function (s, r) { return s + glb(r.asset).tris; }, 0); }

// ============================================================================
// (a) regionD + connection + regionC changes
var conn = (DEFS.connections || []).filter(function (c) {
  return (c.from === RC.id && c.to === RD.id) || (c.from === RD.id && c.to === RC.id);
});
var cn = conn[0];
var c7RotRow = C7C.regionC.enemies.filter(function (e) { return e.type === 'rotmother'; }).length;
var nowRotRow = RC.enemies.filter(function (e) { return e.type === 'rotmother'; }).length;
var RL = RC.rotLair;
var a = {
  regionD: !!RD && RD.id === 'rot_den' && RD.groundRadius === 34 && RD.ambientLightLevel === 0.06 &&
    RD.fogColor === 0x05070a && RD.fogDensity === 0.12 && RD.name === "The Rot Mother's Den" &&
    RD.center.x === -175 && RD.center.z === -271,
  registered: !!DEFS.regions.rot_den && DEFS.regions.rot_den.cfg === RD && DEFS.regions.rot_den.ambientLightLevel === 0.06,
  door: conn.length === 1 && !!cn.door && cn.axis === 'z' && cn.sides[RC.id] === -1 && cn.sides[RD.id] === 1,
  rowGone: c7RotRow === 1 && nowRotRow === 0 && RC.enemies.length === CB.regionC.enemies.length - 1,
  lairGains: !!RL && Array.isArray(RL.stains) && RL.stains.length === 4 && RL.stains[0].radius === 5 &&
    eq(RL.stains.slice(1).map(function (s) { return s.radius; }), [1.8, 1.4, 1.0]) && !!RL.void,
  lairLoses: !!RL && RL.light === undefined && RL.fog === undefined && RL.pool && RL.pool.radius === undefined,
  outcrop: RC.props.filter(function (p) { return p.cullM === 120; }).length === 25,
  keepOut: RC.scatterOverrides.keepOut.some(function (k) { return k.x === -136 && k.z === -219 && k.rx === 22 && k.rz === 18; })
};
check('a', 'regionD + C<->D door + C row gone + rotLair reshaped', Object.keys(a).every(function (k) { return a[k]; }),
  'CONFIG regionD L' + L('CONFIG.js', /^  regionD: \{/) + " (id rot_den L" + L('CONFIG.js', /id: 'rot_den'/) +
  ', groundRadius 34 L' + L('CONFIG.js', /groundRadius: 34,/) + ', fog 0x05070a/0.12 L' + L('CONFIG.js', /fogColor: 0x05070a,|fogDensity: 0\.12,/) +
  ', ambient 0.06 L' + L('CONFIG.js', /ambientLightLevel: 0\.06,/) + '); region-defs register L' + L('region-defs.js', /regions\[CFG\.regionD\.id\]/) +
  ', door conn push L' + L('region-defs.js', /connections\.push\(\{/) + ' sides C-1/D+1 L' + L('region-defs.js', /connections\[2\]\.sides/) +
  ' (vm: ' + conn.length + ' conn, door=' + !!(cn && cn.door) + ', planeZ ' + (cn && cn.planeCoord) + '); C enemies ' +
  CB.regionC.enemies.length + '->' + RC.enemies.length + ' (rotmother rows ' + c7RotRow + '->' + nowRotRow + ', removal note L' +
  L('CONFIG.js', /the CC-C7 rotmother row \(index 22\) is GONE/) + '); C rotLair L' + L('CONFIG.js', /^    rotLair: \{/).split(',')[0] +
  ' stains L' + L('CONFIG.js', /^      stains: \[/) + ' void L' + L('CONFIG.js', /^      void: \{/) + ', no light/fog/pool.radius in C (vm); outcrop rows (cullM 120) = ' +
  RC.props.filter(function (p) { return p.cullM === 120; }).length + '; keepOut L' + L('CONFIG.js', /x: -136, z: -219, rx: 22, rz: 18/) +
  (Object.keys(a).filter(function (k) { return !a[k]; }).length ? ' FAILED: ' + Object.keys(a).filter(function (k) { return !a[k]; }) : ''));

// ============================================================================
// (b) den build rows
var P = RD.props;
var ring = P.filter(function (p) { return /^whWall/.test(p.asset); });
var bould = P.filter(function (p) { return p.asset === 'mossBoulder'; });
var furn = { stoneSteps: 0, skullPile: 0, blightcap: 0, graveMound: 0 };
P.forEach(function (p) { if (furn[p.asset] !== undefined) furn[p.asset]++; });
var nestSacs = P.filter(function (p) {
  return p.asset === 'graveMound' && near(Math.hypot(p.x + 175, p.z + 265), 7.5, 0.6);
}).length;
var DL = RD.rotLair;
// ring geometry: radius, sy (heightM 9 x?), gap at den-local (0,-24)
var ringR = ring.map(function (p) { return Math.hypot(p.x - RD.center.x, p.z - RD.center.z); });
var wallW = glb('whWallA').extX, wallWB = glb('whWallB').extX;
var WR = C.boundaryWall.collider.r, PR = C.player.radius;
function circles(p) {
  var w = (p.asset === 'whWallB' ? wallWB : wallW) * p.scale, ax = Math.cos(p.rotY), az = -Math.sin(p.rotY), out = [];
  for (var k = 0; k < p.wall; k++) { var t = ((k + 0.5) / p.wall - 0.5) * w; out.push({ x: p.x + ax * t, z: p.z + az * t }); }
  return out;
}
var allC = []; ring.forEach(function (p) { allC = allC.concat(circles(p)); });
// sort circles by angle around the center; find the largest angular gap = the mouth
allC.forEach(function (c) { c.ang = Math.atan2(c.z - RD.center.z, c.x - RD.center.x); });
allC.sort(function (p, q) { return p.ang - q.ang; });
var gaps = allC.map(function (c, i) { var n = allC[(i + 1) % allC.length]; return { a: c, b: n, d: Math.hypot(n.x - c.x, n.z - c.z) }; });
gaps.sort(function (p, q) { return q.d - p.d; });
var mouth = gaps[0], second = gaps[1];
var mouthMid = { x: (mouth.a.x + mouth.b.x) / 2, z: (mouth.a.z + mouth.b.z) / 2 };
var mouthClear = mouth.d - 2 * WR;          // edge-to-edge between the end collider circles
var otherClear = second.d - 2 * WR;         // the widest non-mouth hole
var seatLine = L('region-manager.js', /obj\.position\.set\(p\.x, whGroundFeed\(regionId, p\.x, p\.z\) \+ \(p\.y \|\| 0\), p\.z\)/);
var b = {
  ring10: ring.length === 10 && ring.every(function (p) { return p.wall > 0; }),
  ringR24: ringR.every(function (r) { return near(r, 23.5, 1.0); }),
  boulders9: bould.length === 9,
  furniture: furn.stoneSteps === 4 && furn.skullPile === 2 && furn.blightcap === 6 && furn.graveMound === 8,
  nestSacs5: nestSacs === 5,
  pool10: DL.pool.radius === 10, light16: DL.light.intensity === 1.6 && DL.light.height === 1.2 && DL.light.color === 0x7fbf4f,
  // the gap exists at den-local (0,-24) and is at least the brief's 4.6 m; its width vs 4.6 is a
  // reported deviation. Functional rule: the player-centre lane through it lies inside the door window.
  gapAtMouth: near(mouthMid.x, -175, 0.5) && near(mouthMid.z - RD.center.z, -24, 1.5) && mouthClear >= 4.6,
  laneInWindow: (mouth.d / 2 - WR - PR) <= RD.door.doorHalfWidth,
  closed: otherClear < 2 * PR,
  seat: seatLine !== 'NONE' && P.every(function (p) { return p.noCollide === undefined; }),
  flat: RD.terrain === undefined && RD.groundY === 0
};
check('b', 'den build rows', Object.keys(b).every(function (k) { return b[k]; }),
  'CONFIG regionD.props L' + L('CONFIG.js', /cavern ring: 10 segments/) + '..; ring ' + ring.length + ' segs (r ' +
  Math.min.apply(null, ringR).toFixed(1) + '-' + Math.max.apply(null, ringR).toFixed(1) + ', sy 11.55/11.69, wall 8 each), boulders ' + bould.length +
  ', stoneSteps ' + furn.stoneSteps + ' skullPile ' + furn.skullPile + ' blightcap ' + furn.blightcap + ' graveMound ' + furn.graveMound +
  ' (5 nest ring r7.5 + 3 brood); nest pool r ' + DL.pool.radius + ' L' + L('CONFIG.js', /pool: \{ radius: 10,/) + ', light ' + DL.light.intensity +
  '/h ' + DL.light.height + ' L' + L('CONFIG.js', /light: \{ height: 1\.2, intensity: 1\.6/) + '; exit gap (collider edge-to-edge) ' + mouthClear.toFixed(2) + ' m (player-centre lane +-' + (mouth.d / 2 - WR - PR).toFixed(2) + ' vs door window +-' + RD.door.doorHalfWidth + ')' +
  ' m centred (' + mouthMid.x.toFixed(2) + ',' + mouthMid.z.toFixed(2) + ') = den-local z ' + (mouthMid.z - RD.center.z).toFixed(2) +
  '; widest other hole ' + otherClear.toFixed(2) + ' m < player body ' + (2 * PR) + '; seat region-manager L' + seatLine +
  ' (every prop row, flat disc: no terrain row, groundY 0)' +
  (Object.keys(b).filter(function (k) { return !b[k]; }).length ? ' FAILED: ' + Object.keys(b).filter(function (k) { return !b[k]; }) : ''));

// ============================================================================
// (c) lair re-home + byte-equal params
var M = C.enemy.rotmother, M7 = C7C.enemy.rotmother;
function strip(o, k) { var c = JSON.parse(JSON.stringify(o)); k.forEach(function (x) { delete c[x]; }); return c; }
var restEq = eq(strip(M, ['lair']), strip(M7, ['lair']));
var spawnEq = eq(C.enemy.rotspawn, C7C.enemy.rotspawn);
var homeRid = W.WH_CONFIG['region' + M.lair.region].id;
var nestW = { x: RD.center.x + M.lair.x, z: RD.center.z + M.lair.y };
var c = {
  home: homeRid === 'rot_den', local: M.lair.x === 0 && M.lair.y === 6, world: nestW.x === -175 && nestW.z === -265,
  lairRow: RD.lairs.length === 1 && RD.lairs[0].type === 'rotmother' && RD.lairs[0].x === -175 && RD.lairs[0].z === -265,
  flag: M.lair.flag === 'C' && has('enemy.js', /letter: cfg\.lair\.flag \|\| cfg\.lair\.region/) && has('enemy.js', /'rotmother_cleared_'/),
  params: restEq && spawnEq
};
check('c', 'lair homeRegionId rot_den, nest (0,+6)=(-175,-265), params byte-equal C7', Object.keys(c).every(function (k) { return c[k]; }),
  'CONFIG rotmother.lair L' + L('CONFIG.js', /lair: \{ x: 0, y: 6, region: 'D', flag: 'C' \}/) + ' -> region ' + homeRid + ' world (' + nestW.x + ',' + nestW.z +
  '); regionD.lairs row L' + L('CONFIG.js', /\{ type: 'rotmother', x: -175\.0, z: -265\.0 \}/) + '; enemy.js lairNest letter=flag L' +
  L('enemy.js', /letter: cfg\.lair\.flag \|\| cfg\.lair\.region/) + ', lairFlag L' + L('enemy.js', /'rotmother_cleared_'/) +
  '; vm deep-equal vs ' + C7 + ': rotmother minus lair = ' + restEq + ' (spawner/minions, rearm 3d/14m, loot, poison, slam), rotspawn = ' + spawnEq +
  '; region-manager lair rows instanced after enemies L' + L('region-manager.js', /var enemyRows = regionCfg\.enemies\.concat\(regionCfg\.lairs/));

// ============================================================================
// (d) E-to-enter + walk-back crossing, headless logic sim
var DD = RD.door, sim = {};
var Logic = null;
// RegionManagerLogic is file-private; reach it through the exported manager if any
var RM = W.WH_RegionManager || W.WH_REGION_MANAGER || null;
Logic = W.WH_RegionManagerLogic || null;
if (!Logic && RM && RM.Logic) Logic = RM.Logic;
if (Logic) {
  var lg = new Logic(RC.id);
  sim.cNoPlane = lg.tickTransition(-175, -297).action !== 'cross';                // C side: the line is no crossing
  sim.portalFar = lg.portalNear({ x: DD.interactAt.x + 3.6, z: DD.interactAt.z }) === null;
  var pc = lg.portalNear({ x: DD.interactAt.x + 3.4, z: DD.interactAt.z });
  sim.portalNear = !!pc && pc === cn;
  var fc = lg.forceCross(pc);
  sim.forceCross = fc.action === 'cross' && fc.newActiveId === 'rot_den' && lg.activeId === 'rot_den' &&
    fc.mappedPos.x === -175 && fc.mappedPos.z === -292.6;
  sim.noPortalInD = lg.portalNear({ x: DD.interactAt.x, z: DD.interactAt.z }) === null;
  var t1 = lg.tickTransition(-175, -294); sim.insideNoCross = t1.action !== 'cross';
  var t2 = lg.tickTransition(-175, -296);
  sim.walkOut = t2.action === 'cross' && t2.newActiveId === RC.id && t2.mappedPos.x === DD.land.forest_of_the_old_king.x &&
    t2.mappedPos.z === DD.land.forest_of_the_old_king.z && lg.activeId === RC.id;
  var t3 = lg.tickTransition(t2.mappedPos.x, t2.mappedPos.z); sim.noBounce = t3.action !== 'cross';
  // outside the window from inside D: no crossing
  var lg2 = new Logic(RD.id); sim.windowOnly = lg2.tickTransition(-180, -296).action !== 'cross';
  // hysteresis never disposes C's pre-warm inside the ring (deepest point r 22.8 north)
  var deep = Math.abs((RD.center.z + 22.8) - cn.planeCoord);
  sim.hystInRing = deep < C.preWarm.distance + C.preWarm.hysteresis;
} else sim.logicFound = false;
var fade = DD.fadeIn === 0.3 && DD.fadeOut === 0.5 && DD.exitFadeOut === 0.8 && near(DD.fadeIn + DD.fadeOut, 0.8);
var pauseRe = /paused\s*=\s*true|game\.paused|openMenu|showMenu|pauseGame/;
var denBlock = src('game.js').slice(Number(L('game.js', /function tryDenDoor/)) - 1, Number(L('game.js', /function denFadeTick/)) + 16).join('\n');
var d = {
  promptCfg: DD.interactM === 3.5 && DD.text.prompt === 'E - Enter the den' && cn.door.interact.radius === 3.5,
  promptWire: has('game.js', /text = CFG\.regionD\.door\.text\.prompt/) && has('game.js', /tryDenDoor\(\) \|\| tryDoorway\(\)/),
  fade: fade, exitFade: has('game.js', /startDenFade\(0, CFG\.regionD\.door\.exitFadeOut, null\)/),
  noPause: !pauseRe.test(denBlock),
  sim: Object.keys(sim).length > 1 && Object.keys(sim).every(function (k) { return sim[k]; })
};
check('d', 'E-to-enter 3.5 m + 0.8 s fade + walk-back exit, no pause/menu', Object.keys(d).every(function (k) { return d[k]; }),
  'CONFIG door L' + L('CONFIG.js', /^    door: \{/).split(',').pop() + ' (interactM 3.5 L' + L('CONFIG.js', /interactM: 3\.5,/).split(',').pop() +
  ', fadeIn 0.3 + fadeOut 0.5 = 0.8, exitFadeOut 0.8 L' + L('CONFIG.js', /exitFadeOut: 0\.8/) + ', prompt L' + L('CONFIG.js', /'E - Enter the den'/) +
  '); game.js interact chain L' + L('game.js', /tryDenDoor\(\) \|\| tryDoorway\(\)/) + ', tryDenDoor L' + L('game.js', /function tryDenDoor/) +
  ' (forceCross at the dip peak L' + L('game.js', /applyCross\(game\.regionManager\.forceCross\(conn\)\)/) + '), prompt L' +
  L('game.js', /text = CFG\.regionD\.door\.text\.prompt/) + ', fade on #wh-death-overlay L' + L('game.js', /function startDenFade/) + '/' + L('game.js', /function denFadeTick/) +
  ', tick call L' + L('game.js', /denFadeTick\(dt\);/) + ', walk-out dip L' + L('game.js', /startDenFade\(0, CFG\.regionD\.door\.exitFadeOut/) +
  '; region-manager portalNear L' + L('region-manager.js', /prototype\.portalNear = /) + ', logic forceCross L' + L('region-manager.js', /RegionManagerLogic\.prototype\.forceCross/) +
  ', live forceCross L' + L('region-manager.js', /^  RegionManager\.prototype\.forceCross/) + ', planeIn filter L' + L('region-manager.js', /DEFS\.planeIn\(c, self\.activeId\)/) +
  '; no pause/menu token in the den-door block; logic sim ' + JSON.stringify(sim));

// ============================================================================
// (e) darkness
var K = C.dayNight.constantPhases && C.dayNight.constantPhases.rot_den;
var e = {
  constRow: !!K && K.lightIntensity === 0 && K.exposureMult === 0.75 && K.stars === 0.15 && K.discOpacity === 0.2 &&
    K.hemiFillMult === 1.0 && K.fog.rot_den.color === 0x05070a && K.fog.rot_den.density === 0.12,
  hemi006: RD.ambientLightLevel === 0.06 && has('game.js', /var fill = CFG\.lighting\.hemiBaseIntensity \* region\.ambientLightLevel \* mult/),
  dnBranch: has('daynight.js', /function constantRow\(areaId\)/) && has('daynight.js', /if \(constantRow\(areaId\)\) return;/) &&
    has('daynight.js', /if \(constantRow\(this\.area\)\) \{/) && has('daynight.js', /copyRow\(this\.state, K\)/),
  noClockChange: has('daynight.js', /coreTick\.call\(this, dt\);/),
  noRegionLightOnBodies: !/rotmother|rotspawn/.test(git(['diff', BASE, HEAD, '--', J + 'game.js']).split('\n').filter(function (l) { return /^\+/.test(l) && /light/i.test(l); }).join('\n')),
  lightDies: has('enemy.js', /var st = LAIR_STATE\[N\.letter\];/) && has('enemy.js', /if \(st && st\.cleared\) return;/),
  fogDies: has('enemy.js', /lit = !\(st && st\.cleared\)/),
  rearmRelight: has('enemy.js', /st\.cleared = false;/) && has('game.js', /window\.WH_Enemy\.lairSockets\(rm\.logic\.activeId\)/) &&
    has('game.js', /var out = computeFireSockets\(\);/)
};
check('e', 'always-dark phase + her/no region light + light dies/relights', Object.keys(e).every(function (k) { return e[k]; }),
  'CONFIG dayNight.constantPhases.rot_den L' + L('CONFIG.js', /^    rot_den: \{/) + ' (lightIntensity 0 = moon 0, exposureMult 0.75 L' + L('CONFIG.js', /exposureMult: 0\.75,$/) +
  ', stars 0.15, discOpacity 0.2 L' + L('CONFIG.js', /discColor: 0xdfe7f2, discGlowColor: 0xa8bce6, discOpacity: 0\.2/) + ', hemiFillMult 1 x regionD 0.06 via game.js L' +
  L('game.js', /var fill = CFG\.lighting\.hemiBaseIntensity \* region\.ambientLightLevel/) + '); daynight.js constantRow L' + L('daynight.js', /function constantRow/) +
  ', setArea skip L' + L('daynight.js', /if \(constantRow\(areaId\)\) return;/) + ', SkyPool.tick underlay L' + L('daynight.js', /if \(constantRow\(this\.area\)\) \{/) +
  ', DayNight.tick copyRow L' + L('daynight.js', /copyRow\(this\.state, K\)/) + ' after untouched coreTick L' + L('daynight.js', /coreTick\.call\(this, dt\);/) +
  '; nest light: lairSockets cleared-skip L' + L('enemy.js', /if \(st && st\.cleared\) return;/) + ' polled per frame by computeSockets L' + L('game.js', /var out = computeFireSockets\(\);/) +
  ' -> lairSockets L' + L('game.js', /lairSockets\(rm\.logic\.activeId\)/) + '; death flag L' + L('enemy.js', /LAIR_STATE\[L\.nest\.letter\] = \{ cleared: true/) +
  ', re-arm clears L' + L('enemy.js', /st\.cleared = false;/) + ', fog cards gate L' + L('enemy.js', /lit = !\(st && st\.cleared\)/) +
  '; no region light row targets rotmother/rotspawn (only the nest socket + the player torch/firebolt sockets)');

// ============================================================================
// (f) save round-trip (flag) + per-index den roster + pre-C8 load
var saveDiff = git(['diff', '--stat', BASE, HEAD, '--', J + 'save.js']).trim();
var f = {
  flagKey: M.lair.flag === 'C' && has('enemy.js', /\/\^rotmother_cleared_\(\[A-Z\]\)\$\//),
  capture: has('enemy.js', /out\[lairFlag\(letter\)\] = st\.day;/) && has('game.js', /data\.lairs = window\.WH_Enemy\.captureLairs\(\)/),
  restore: has('game.js', /window\.WH_Enemy\.restoreLairs\(data\.lairs\)/),
  armedDefault: has('enemy.js', /if \(!block \|\| typeof block !== 'object'\) return;/),
  roster: has('enemy.js', /var rows = hc\.enemies\.length \+ \(hc\.lairs \? hc\.lairs\.length : 0\)/) && RD.enemies.length === 0,
  denRegionValid: has('save.js', /window\.WH_REGION_DEFS\.regions\[rid\]/) && !!DEFS.regions.rot_den,
  saveUntouched: saveDiff === ''
};
check('f', 'save: cleared flag + den roster + pre-C8 compat', Object.keys(f).every(function (k) { return f[k]; }),
  'flag key letter C kept (rotmother_cleared_C, byte-equal to C7): enemy.js lairNest L' + L('enemy.js', /letter: cfg\.lair\.flag/) +
  ', captureLairs L' + L('enemy.js', /Enemy\.captureLairs = /) + ' / restoreLairs L' + L('enemy.js', /Enemy\.restoreLairs = /) +
  ' (missing block = all armed L' + L('enemy.js', /if \(!block \|\| typeof block !== 'object'\) return;/) + '); game.js WH_SAVE wrap capture L' +
  L('game.js', /data\.lairs = window\.WH_Enemy\.captureLairs\(\)/) + ' restore L' + L('game.js', /window\.WH_Enemy\.restoreLairs\(data\.lairs\)/) +
  '; den roster: regionD.enemies [] + lairs[0] = index 0 (region-manager L' + L('region-manager.js', /var enemyRows = regionCfg\.enemies\.concat/) +
  '), spawn-prune boundary counts lair rows enemy.js L' + L('enemy.js', /var rows = hc\.enemies\.length \+ \(hc\.lairs/) +
  '; per-index dead state is session state (save.js L8: enemies never saved) as in C7; save.js validRegion accepts rot_den (L' +
  L('save.js', /window\.WH_REGION_DEFS\.regions\[rid\]/) + '); save.js diff: ' + (saveDiff || 'none'));

// ============================================================================
// (g) scope
var files = git(['diff', '--name-only', BASE, HEAD]).trim().split('\n');
var allowed = [/^prototype\/js\/(CONFIG|region-defs|region-manager|assets|enemy|game)\.js$/, /^prototype\/builds\/v8-playable\.html$/,
  /^io\/missions\//, /^scratch\//];
var forbidden = [/save\.js$/, /player\.js$/, /camp\.js$/, /cooking\.js$/, /style\.css$/, /index\.html$/, /^docs\/planning\//];
var flagged = files.filter(function (x) { return !allowed.some(function (r) { return r.test(x); }); });
var forb = files.filter(function (x) { return forbidden.some(function (r) { return r.test(x); }); });
var dnStat = git(['diff', '--numstat', BASE, HEAD, '--', J + 'daynight.js']).trim();
var dnRemoved = git(['diff', BASE, HEAD, '--', J + 'daynight.js']).split('\n').filter(function (l) { return /^-[^-]/.test(l); }).length;
check('g', 'scope audit ' + BASE + '..' + HEAD, forb.length === 0 && flagged.every(function (x) { return x === J + 'daynight.js'; }),
  files.length + ' files: ' + files.join(', ') + '; FORBIDDEN touched: ' + (forb.join(', ') || 'none') + '; outside the sec-8g allowed list: ' +
  (flagged.join(', ') || 'none') + (dnStat ? ' (daynight numstat ' + dnStat.replace(/\s+/g, ' ') + ', removed lines ' + dnRemoved + ')' : ''));

// ============================================================================
// (h) node --check + bundle + tris ledger
var edited = files.filter(function (x) { return /\.js$/.test(x); });
var nc = edited.map(function (x) {
  try { cp.execFileSync(process.execPath, ['--check', x], { stdio: 'pipe' }); return [x, 'OK']; }
  catch (err) { return [x, 'FAIL ' + String(err.stderr).slice(0, 200)]; }
});
var bundle = fs.readFileSync('prototype/builds/v8-playable.html', 'utf8');
var inBundle = ['CONFIG.js', 'region-defs.js', 'region-manager.js', 'assets.js', 'enemy.js', 'game.js', 'daynight.js'].map(function (x) {
  return [x, bundle.indexOf(fs.readFileSync(J + x, 'utf8')) >= 0];
});
var bundleBytes = fs.statSync('prototype/builds/v8-playable.html').size;
var outcrop = RC.props.filter(function (p) { return p.cullM === 120; });
var oldBones = CB.regionC.props.filter(function (p) { return p.asset === 'b6Bones'; });
var trisOut = triSum(outcrop), trisDen = triSum(P), trisBones = triSum(oldBones);
var stainTris = RL.stains.length * (RL.pool.segments * (1 + 2 * (RL.pool.rings - 1))) + 2;
var poolTris = DL.pool.segments * (1 + 2 * (DL.pool.rings - 1));
var bodies = glb('rotmotherBody').tris;
var newTris = trisOut + trisDen + stainTris + poolTris;
var h = {
  nodeCheck: nc.every(function (x) { return x[1] === 'OK'; }),
  bundle: inBundle.every(function (x) { return x[1]; }) && bundleBytes === 3251738,
  ledger: newTris <= 40000
};
var perAsset = {};
outcrop.concat(P).forEach(function (p) { perAsset[p.asset] = glb(p.asset).tris; });
check('h', 'node --check + bundle + tris ledger', Object.keys(h).every(function (k) { return h[k]; }),
  'node --check: ' + nc.map(function (x) { return x[0].replace(J, '') + ' ' + x[1]; }).join(', ') + '; bundle v8-playable.html ' + bundleBytes +
  ' B, every edited js inlined verbatim: ' + inBundle.every(function (x) { return x[1]; }) + '; GLB-header tris: outcrop ' + outcrop.length + ' rows = ' + trisOut +
  ', den ' + P.length + ' rows = ' + trisDen + ', pools/stains/void ~' + (stainTris + poolTris) + ' -> NEW ' + newTris + ' (target <= 40,000); removed from C: 6 b6Bones = ' +
  trisBones + ' -> net C ' + (trisOut + stainTris - trisBones) + '; per-asset ' + JSON.stringify(perAsset));

// ---- report ------------------------------------------------------------------
res.forEach(function (r) { console.log((r.ok ? 'PASS' : 'FAIL') + ' | ' + r.id + ' | ' + r.name + ' | ' + r.ev); });
var blocking = res.filter(function (r) { return !r.ok; });
console.log('VERDICT: ' + (blocking.length ? 'FAIL (' + blocking.map(function (r) { return r.id; }).join(',') + ')' : 'PASS'));
console.log('META wallExtX A ' + wallW.toFixed(3) + ' B ' + wallWB.toFixed(3) + ' mouthEnds ' + JSON.stringify([mouth.a, mouth.b]) +
  ' planeZ ' + (cn && cn.planeCoord) + ' window +-' + (cn && cn.door.doorHalfWidth) + ' playerR ' + PR + ' colliderR ' + WR + ' rotmotherBody tris ' + bodies);
process.exit(blocking.length ? 1 : 0);
