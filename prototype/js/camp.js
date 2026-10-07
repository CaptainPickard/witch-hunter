// Witch Hunter prototype - camps (C3, io/missions/2026-10-06-cc-c3-sleep-tent.md).
// A camp = MODULE ROWS (CONFIG.camp.modules / worldCamps): one prop + one
// interact hook each. 'cook' registers a cooking station row through
// WH_COOKING Cooking.addStation (same row shape as the bandit fire - CAMP
// GROWTH LAW); 'sleep' opens the TENT MENU (Save / Save and Heal / C4 Load). Future
// modules (chest, bench, warp) = a new row + a new hook.
// The manager owns: the deploy gate (cooking.kitAcquired), placement mode
// (red ghost on the ground, clearance check = the gather-node rules), the
// deployed sites (session-only) and their scene groups - added straight to
// the scene, never to a region group, so region dispose / rebuild can not
// eat a site - plus the world camps (the Region B bandit bedroll) and the
// respawn point the death flow honors (game.js respawnPlayer).
// TUTORIAL LAW: Save and Heal is the ONLY caller of dayNight.beginCycle()
// (first rest ever = day 1 dawn); later rests roll the day (nextDawn).
// Exposes window.WH_CAMP = { Camp } (game.js owns the one instance).

(function () {
  'use strict';

  var CFG = window.WH_CONFIG;
  var K = CFG.camp;

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  // ---- pieces --------------------------------------------------------------------
  // Placeholder tent (CONFIG.camp.tentPlaceholder): two dark canvas panels
  // meeting at a ridge pole, open ends along local z (door = +z). Geometry
  // and the solid materials are shared by every tent.
  var tentGeo = null, tentMats = null;
  function buildTent(ghostMat) {
    var T = K.tentPlaceholder;
    var hw = T.width / 2;
    var slant = Math.sqrt(hw * hw + T.height * T.height);
    var ang = Math.atan2(T.height, hw);
    if (!tentGeo) {
      tentGeo = {
        panel: new THREE.BoxGeometry(slant, 0.05, T.length),
        pole: new THREE.BoxGeometry(0.08, 0.08, T.length + 0.3)
      };
      tentMats = {
        canvas: new THREE.MeshStandardMaterial({ color: T.color, roughness: 1, metalness: 0 }),
        pole: new THREE.MeshStandardMaterial({ color: T.poleColor, roughness: 1, metalness: 0 })
      };
    }
    var g = new THREE.Group();
    [-1, 1].forEach(function (s) {
      var p = new THREE.Mesh(tentGeo.panel, ghostMat || tentMats.canvas);
      p.position.set(s * hw / 2, T.height / 2, 0);
      p.rotation.z = -s * ang;
      g.add(p);
    });
    var pole = new THREE.Mesh(tentGeo.pole, ghostMat || tentMats.pole);
    pole.position.y = T.height + 0.02;
    g.add(pole);
    return g;
  }

  // One CONFIG.camp.assets piece: a manifest GLB (scaled like a prop) or the
  // procedural tent. ghostMat swaps every material on the clone.
  function makePiece(key, ghostMat) {
    var A = K.assets[key];
    var obj = A.glb ? window.WH_ASSETS.instance(A.glb) : buildTent(ghostMat);
    obj.scale.setScalar(A.scale);
    if (ghostMat && A.glb) {
      obj.traverse(function (o) { if (o.isMesh) o.material = ghostMat; });
    }
    return obj;
  }

  // Site frame: f = unit vector from the site center toward the player at
  // placement; group yaw = atan2(f.x, f.z) maps local +z onto f, so a module
  // offset [right, back] sits at local (right, 0, -back).
  function siteYaw(f) { return Math.atan2(f.x, f.z); }

  function moduleWorld(cx, cz, f, row) {
    var r = row.offset[0], b = row.offset[1];
    return { x: cx + f.z * r - f.x * b, z: cz - f.x * r - f.z * b };
  }

  function buildSiteGroup(cx, cz, f, ghostMat) {
    var g = new THREE.Group();
    g.name = ghostMat ? 'camp-ghost' : 'camp-site';
    g.position.set(cx, 0, cz);
    g.rotation.y = siteYaw(f);
    K.modules.forEach(function (row) {
      var obj = makePiece(row.asset, ghostMat);
      obj.position.set(row.offset[0], 0, -row.offset[1]);
      obj.rotation.y = row.rotY || 0;
      g.add(obj);
    });
    return g;
  }

  // ---- Camp manager --------------------------------------------------------------
  // opts: { scene, camera, player, cooking, dayNight, regionManager() getter,
  //         toast(text), applyBuffStats(), onOpenChange(open) }
  function Camp(opts) {
    var self = this;
    this.scene = opts.scene;
    this.camera = opts.camera;
    this.player = opts.player;
    this.cooking = opts.cooking;
    this.dayNight = opts.dayNight;
    this.rm = opts.regionManager;
    this.toast = opts.toast;
    this.applyBuffStats = opts.applyBuffStats;
    this.onOpenChange = opts.onOpenChange || function () {};
    // C4 save profile (game.js over js/save.js WH_SAVE): { has(), save(camp), restore() }
    this.profile = opts.profile || null;
    this.sites = [];                  // deployed kits (C4: the save profile stores them)
    this.siteSeq = 0;
    this.worldCamps = K.worldCamps.map(function (wc) {
      return { id: wc.id, regionId: wc.regionId, world: true, group: null,
        modules: wc.modules.map(function (row) { return { row: row, x: row.x, z: row.z }; }),
        respawn: { regionId: wc.regionId, x: wc.respawn.x, z: wc.respawn.z,
                   face: wc.face, campId: wc.id } };
    });
    this.respawn = null;              // { regionId, x, z, face, campId } (Save / Save and Heal)
    this.placing = false;
    this.placeRegion = null;
    this.ghost = null;
    this.ghostPos = { x: 0, z: 0 };
    this.ghostF = { x: 0, z: 1 };
    this.pointer = null;              // last pointer client px while placing
    this.pointerDirty = false;
    this.menuCamp = null;             // camp the tent menu is open on
    this.resting = false;             // Save and Heal fade in flight
    this.raycaster = new THREE.Raycaster();
    this.ndc = new THREE.Vector2();
    this.ground = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
    this.hitPt = new THREE.Vector3();
    this.clampV = new THREE.Vector3();
    this.buildMenu();
    this.buildPlaceBar();
    this.fadeEl = el('div');
    this.fadeEl.id = 'wh-sleep-fade';
    this.fadeEl.style.transitionDuration = K.sleepFadeSec + 's';
    document.getElementById('wh-root').appendChild(this.fadeEl);
    this.cooking.onKitButton = function () { self.togglePlacing(); };
    document.addEventListener('keydown', function (e) { self.onKey(e); });
    document.addEventListener('pointermove', function (e) {
      if (!self.placing) return;
      self.pointer = { x: e.clientX, y: e.clientY };
      self.pointerDirty = true;
    });
    // canvas press while placing: the ghost jumps there; a mouse click also
    // confirms (touch taps only move it - the PLACE button confirms).
    // preventDefault drops the compatibility mousedown, so a confirm that
    // lifts the input suspension never lands as a sword swing.
    document.getElementById('wh-canvas').addEventListener('pointerdown', function (e) {
      if (!self.placing) return;
      e.preventDefault();
      self.pointer = { x: e.clientX, y: e.clientY };
      self.followPointer();
      if (e.pointerType === 'mouse' && e.button === 0) self.confirm();
    });
  }

  Camp.prototype.activeId = function () { return this.rm().logic.activeId; };

  Camp.prototype.camps = function () { return this.worldCamps.concat(this.sites); };

  // ---- interact (game.js interact chain: after cook stations, before gather) -----

  // nearest 'sleep' module within CONFIG.camp.interactRadius -> { camp, module }
  Camp.prototype.nearestSleep = function (x, z, regionId) {
    var best = null, bestD2 = K.interactRadius * K.interactRadius;
    this.camps().forEach(function (c) {
      if (c.regionId !== regionId) return;
      c.modules.forEach(function (m) {
        if (m.row.hook !== 'sleep') return;
        var dx = m.x - x, dz = m.z - z, d2 = dx * dx + dz * dz;
        if (d2 <= bestD2) { bestD2 = d2; best = { camp: c, module: m }; }
      });
    });
    return best;
  };

  Camp.prototype.interactSleep = function (hit) {
    this.setMenu(hit.camp);
  };

  // ---- tent menu (DOM modal, cook-panel pattern; buttons = touch rows) ------------

  Camp.prototype.buildMenu = function () {
    var self = this, T = K.text;
    var root = el('div');
    root.id = 'wh-camp-menu';
    var panel = el('div', 'inv-panel camp-menu-panel');
    root.appendChild(panel);
    panel.appendChild(el('div', 'inv-title', T.menuTitle));
    var rows = el('div', 'cook-btns camp-menu-btns');
    // C4: LOAD row (CONFIG.save.text.load), dim while no save exists
    [[T.save, function () { self.save(); }],
     [T.saveHeal, function () { self.saveAndHeal(); }],
     [CFG.save.text.load, function () { self.load(); }, 'load'],
     [T.cancel, function () { self.setMenu(null); }]].forEach(function (b) {
      var btn = el('button', 'cook-btn camp-menu-btn', b[0]);
      btn.type = 'button';
      btn.tabIndex = -1;
      btn.addEventListener('click', b[1]);
      rows.appendChild(btn);
      if (b[2] === 'load') self.loadBtn = btn;
    });
    panel.appendChild(rows);
    panel.appendChild(el('div', 'inv-hint', 'Esc cancel'));
    document.getElementById('wh-root').appendChild(root);
    this.menuEl = root;
  };

  // camp = open on it, null = close
  Camp.prototype.setMenu = function (camp) {
    var open = !!camp;
    if (!!this.menuCamp === open && this.menuCamp === camp) return;
    var was = !!this.menuCamp;
    this.menuCamp = camp || null;
    if (open && this.loadBtn) this.loadBtn.classList.toggle('dim', !this.hasSave());
    this.menuEl.classList.toggle('open', open);
    if (was !== open) this.onOpenChange(open);
  };

  Camp.prototype.hasSave = function () {
    return !!(this.profile && this.profile.has());
  };

  // C4: both save rows write the profile FIRST (respawn = this camp's), then
  // run their existing behavior unchanged.
  Camp.prototype.writeProfile = function (c) {
    return !!(this.profile && this.profile.save(c));
  };

  // Save: respawn point only. No heal, no buff / meal change, no clock change.
  Camp.prototype.save = function () {
    var c = this.menuCamp;
    if (!c) return;
    var saved = this.writeProfile(c);
    this.setRespawn(c);
    this.setMenu(null);
    this.toast(saved ? CFG.save.text.saved + ' ' + K.text.savedToast : K.text.savedToast);
  };

  // C4 LOAD: no save = refusal toast (menu stays); else the menu closes and
  // the last saved profile replaces the live state.
  Camp.prototype.load = function () {
    if (!this.menuCamp || this.resting) return;
    if (!this.hasSave()) { this.toast(CFG.save.text.noSave); return; }
    this.setMenu(null);
    this.profile.restore();
  };

  Camp.prototype.setRespawn = function (c) {
    var r = c.respawn;
    this.respawn = { regionId: r.regionId, x: r.x, z: r.z,
      face: r.face ? { x: r.face.x, z: r.face.z } : null, campId: r.campId };
  };

  // Save and Heal: the rest life cycle under a short fade to black (input
  // stays suspended through the fade; the world keeps running).
  // C3.1 WAKE-SNAP: prepareWake() pre-warms the dawn pano while the screen
  // is black; the rest rolls to HELD dawn (daynight wakeBlendSec) and the
  // wake pano hard-commits behind the fade - you open your eyes at dawn.
  Camp.prototype.saveAndHeal = function () {
    var c = this.menuCamp;
    if (!c || this.resting) return;
    var self = this, ms = K.sleepFadeSec * 1000;
    // C4.1 (IO amend, doc 35 law "camps save on completion"): the profile
    // write moved to AFTER rest() - the checkpoint is the WAKE state
    // (healed, dawn, meal cleared, respawn here), not the pre-rest state.
    // LOAD after a rest must NOT undo the rest.
    this.resting = true;
    this.menuEl.classList.remove('open');   // menu gone, suspension held
    if (this.dayNight.prepareWake) this.dayNight.prepareWake();
    this.fadeEl.classList.add('on');
    setTimeout(function () {
      if (self.player.state === 'alive') {
        self.rest(c);
        if (self.writeProfile(c)) self.toast(CFG.save.text.saved);   // C4.1: wake-state checkpoint
      }
      self.fadeEl.classList.remove('on');
      setTimeout(function () {
        self.resting = false;
        self.menuCamp = null;
        self.onOpenChange(false);
      }, ms);
    }, ms);
  };

  // The rest itself (order matters, mission D4).
  Camp.prototype.rest = function (c) {
    var p = this.player, dn = this.dayNight;
    this.cooking.buffs.clear();       // 1) every buff ends; hpMax drops back (clamps hp)
    this.applyBuffStats();
    p.hp = p.hpMax;                   // 2) full heal + stamina
    p.stamina = p.staminaMax;
    this.cooking.clearMealSlot();     // 3) the day's meal slot is empty
    this.setRespawn(c);               // 4) respawn point
    if (dn.dormant) dn.beginCycle();  // 5) first rest ever = day 1 dawn (tutorial law)
    else dn.nextDawn();               //    later rests = the next day's dawn
    // campfire fuel: untouched everywhere (kit fire + world fires)
    this.toast(K.text.restedToast.replace('{day}', dn.day));
  };

  // ---- placement ----------------------------------------------------------------

  Camp.prototype.buildPlaceBar = function () {
    var self = this;
    var bar = el('div', 'cook-btns');
    bar.id = 'wh-camp-place';
    [['PLACE', function () { self.confirm(); }],
     ['CANCEL', function () { self.stopPlacing(); }]].forEach(function (b) {
      var btn = el('button', 'cook-btn', b[0]);
      btn.type = 'button';
      btn.tabIndex = -1;
      btn.addEventListener('pointerdown', function (e) {
        e.preventDefault();
        e.stopPropagation();
        b[1]();
      });
      btn.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); });
      bar.appendChild(btn);
    });
    document.getElementById('wh-root').appendChild(bar);
    this.placeBar = bar;
  };

  Camp.prototype.togglePlacing = function () {
    if (this.placing) this.stopPlacing();
    else this.startPlacing();
  };

  // CAMP button: the kit is the only gate; no other modal may be open.
  Camp.prototype.startPlacing = function () {
    var p = this.player;
    if (!this.cooking.kitAcquired || p.state !== 'alive' || p.inputSuspended) return;
    this.placing = true;
    this.placeRegion = this.activeId();
    this.pointer = null;
    this.pointerDirty = false;
    if (!this.ghost) {
      this.ghostMat = new THREE.MeshBasicMaterial({ color: K.deploy.ghostColor,
        transparent: true, opacity: K.deploy.ghostOpacity, depthWrite: false });
      this.ghost = buildSiteGroup(0, 0, { x: 0, z: 1 }, this.ghostMat);
      this.scene.add(this.ghost);
    }
    var fx = Math.sin(p.yaw), fz = Math.cos(p.yaw);
    this.setGhost(p.pos.x + fx * K.deploy.startAheadM, p.pos.z + fz * K.deploy.startAheadM);
    this.ghost.visible = true;
    this.placeBar.classList.add('open');
    if (this.cooking.kitBtn) this.cooking.kitBtn.classList.add('active');
    this.onOpenChange(true);
    this.toast(K.text.placingToast);
  };

  // cancel / done: silent
  Camp.prototype.stopPlacing = function () {
    if (!this.placing) return;
    this.placing = false;
    if (this.ghost) this.ghost.visible = false;
    this.placeBar.classList.remove('open');
    if (this.cooking.kitBtn) this.cooking.kitBtn.classList.remove('active');
    this.onOpenChange(false);
  };

  // ghost center: within maxReachM of the player, inside the active
  // region's playable bounds (plane + rim, the player clamp); the kit faces
  // the player
  Camp.prototype.setGhost = function (x, z) {
    var p = this.player.pos, R = K.deploy.maxReachM;
    var dx = x - p.x, dz = z - p.z, d = Math.sqrt(dx * dx + dz * dz);
    if (d > R) { x = p.x + dx / d * R; z = p.z + dz / d * R; }
    var v = this.clampV.set(x, 0, z);
    this.rm().logic.clampPlayer(v);
    dx = p.x - v.x; dz = p.z - v.z; d = Math.sqrt(dx * dx + dz * dz);
    if (d > 0.01) this.ghostF = { x: dx / d, z: dz / d };
    this.ghostPos = { x: v.x, z: v.z };
    this.ghost.position.set(v.x, 0, v.z);
    this.ghost.rotation.y = siteYaw(this.ghostF);
    // FIX 10-06b: the ghost colors LIVE - green = a valid spot, red = the
    // same clearance check confirm() will run (no red spot is placeable).
    var pts = K.modules.map(function (row) {
      return moduleWorld(this.ghostPos.x, this.ghostPos.z, this.ghostF, row);
    }, this);
    this.ghostWhy = this.refuseReason(this.placeRegion, pts);
    if (this.ghostMat) {
      this.ghostMat.color.setHex(this.ghostWhy ?
        K.deploy.ghostColor : (K.deploy.ghostOkColor || 0x3ad26a));
    }
  };

  // raycast the pointer to the ground plane y = 0 (sky = keep the last spot)
  Camp.prototype.followPointer = function () {
    this.pointerDirty = false;
    if (!this.pointer) return;
    var r = document.getElementById('wh-canvas').getBoundingClientRect();
    this.ndc.set((this.pointer.x - r.left) / r.width * 2 - 1,
      -((this.pointer.y - r.top) / r.height) * 2 + 1);
    this.raycaster.setFromCamera(this.ndc, this.camera);
    if (this.raycaster.ray.intersectPlane(this.ground, this.hitPt)) {
      this.setGhost(this.hitPt.x, this.hitPt.z);
    }
  };

  // click / E / PLACE: clearance check -> place, or refusal toast (ghost stays)
  // FIX 10-06b: the check re-runs here with the live result the ghost already
  // showed (this.ghostWhy) - the red / green preview IS the verdict.
  Camp.prototype.confirm = function () {
    if (!this.placing) return false;
    var c = this.ghostPos, f = this.ghostF;
    var pts = K.modules.map(function (row) { return moduleWorld(c.x, c.z, f, row); });
    var why = this.refuseReason(this.placeRegion, pts);
    if (why) {
      this.toast(K.text.refuseToast.replace('{why}', K.text.why[why] || why));
      return true;
    }
    this.place(this.placeRegion, c.x, c.z, f);
    this.stopPlacing();
    this.toast(K.text.placedToast);
    return true;
  };

  // The gather-node placement rules (CONFIG.gather.placement) + the scatter's
  // gate / rim rows (CONFIG.scatter.clear) + keep-out ellipses + the dirt
  // path band, tested at every module of the kit. Returns a CONFIG.camp.text
  // .why key, or null = open ground.
  Camp.prototype.refuseReason = function (rid, pts) {
    var GP = CFG.gather.placement, SC = CFG.scatter.clear, D = K.deploy;
    var GEO = window.WH_RegionGeom;
    var reg = window.WH_REGION_DEFS.regions[rid], cfg = reg.cfg;
    var rm = this.rm();
    var plane = CFG.boundary.z;
    var DP = CFG.world.dirtPath;
    var treeRe = new RegExp(GP.treeMatch, 'i');
    var keepOut = (CFG.scatter.keepOut || []).filter(function (k) { return k.regionId === rid; });
    var trees = rm.scatterPlan(rid).trees;
    var enemies = rm.getEnemies(rid).filter(function (e) { return e.fsm !== 'dead'; });
    var spacing = GP.spacingM[rid] || 0;
    var camps = this.camps().filter(function (c) { return c.regionId === rid; });
    if (this.sites.length >= D.maxSites) {
      var packed = this.sites[0];    // packs up on this deploy: not in the way
      camps = camps.filter(function (c) { return c !== packed; });
    }
    function near(p, x, z, m) {
      var dx = p.x - x, dz = p.z - z;
      return dx * dx + dz * dz < m * m;
    }
    for (var i = 0; i < pts.length; i++) {
      var p = pts[i], j;
      if (Math.sqrt(p.x * p.x + p.z * p.z) > GEO.playRadius() - SC.edgeM) return 'edge';
      if (reg.side === 1 ? p.z < plane + SC.edgeM : p.z > plane - SC.edgeM) return 'edge';
      if (near(p, CFG.chokepoint.centerX, plane, SC.gateM) || GEO.meetsCorridor(p.x, p.z, 0)) return 'gate';
      if (DP && DP.regionId === rid && GEO.distToPath(DP, p.x, p.z) < DP.halfWidth + D.pathBand) return 'path';
      for (j = 0; j < keepOut.length; j++) {
        var kx = (p.x - keepOut[j].x) / keepOut[j].rx, kz = (p.z - keepOut[j].z) / keepOut[j].rz;
        if (kx * kx + kz * kz < 1) return 'keepOut';
      }
      if (near(p, reg.spawn.x, reg.spawn.z, GP.spawnM)) return 'spawn';
      for (j = 0; j < cfg.props.length; j++) {
        var pr = cfg.props[j], isTree = treeRe.test(pr.asset);
        if (near(p, pr.x, pr.z, isTree ? GP.treePropM : GP.propM)) return isTree ? 'tree' : 'prop';
      }
      for (j = 0; j < trees.length; j++) {
        if (near(p, trees[j].x, trees[j].z, GP.treePropM)) return 'tree';
      }
      for (j = 0; j < (cfg.enemies || []).length; j++) {
        if (near(p, cfg.enemies[j].x, cfg.enemies[j].z, GP.enemyM)) return 'enemy';
      }
      for (j = 0; j < enemies.length; j++) {
        if (near(p, enemies[j].pos.x, enemies[j].pos.z, GP.enemyM)) return 'enemy';
      }
      for (j = 0; j < (cfg.nodes || []).length; j++) {
        if (near(p, cfg.nodes[j].x, cfg.nodes[j].z, spacing)) return 'node';
      }
      for (j = 0; j < camps.length; j++) {
        for (var k = 0; k < camps[j].modules.length; k++) {
          var m = camps[j].modules[k];
          if (near(p, m.x, m.z, GP.propM)) return 'camp';
        }
      }
    }
    return null;
  };

  // Deploy a kit site: one scene group (not region content), the fire module
  // registers its cooking station row, maxSites packs up the oldest.
  Camp.prototype.place = function (rid, cx, cz, f) {
    while (this.sites.length >= K.deploy.maxSites) this.packUp(this.sites[0]);
    var site = { id: 'camp' + (++this.siteSeq), regionId: rid, x: cx, z: cz,
      f: { x: f.x, z: f.z }, world: false, group: null, stations: [], modules: [] };
    var yaw = siteYaw(f);
    var self = this;
    K.modules.forEach(function (row) {
      var w = moduleWorld(cx, cz, f, row);
      site.modules.push({ row: row, x: w.x, z: w.z });
      if (row.hook === 'cook') {
        var st = row.station;
        site.stations.push(self.cooking.addStation({ id: site.id + ':' + row.id,
          kind: st.kind, regionId: rid, asset: K.assets[row.asset].glb,
          x: w.x, z: w.z, startLit: st.startLit }));
      }
    });
    // respawn: the menu anchor's door side, respawnStepM out (fire ring stays clear)
    var anchor = site.modules.filter(function (m) { return m.row.menuAnchor; })[0] || site.modules[0];
    var dy = yaw + (anchor.row.rotY || 0);
    var fire = site.modules.filter(function (m) { return m.row.hook === 'cook'; })[0];
    site.respawn = { regionId: rid,
      x: anchor.x + Math.sin(dy) * K.respawnStepM, z: anchor.z + Math.cos(dy) * K.respawnStepM,
      face: fire ? { x: fire.x, z: fire.z } : { x: cx, z: cz }, campId: site.id };
    this.sites.push(site);
    return site;
  };

  Camp.prototype.packUp = function (site) {
    if (site.group) this.scene.remove(site.group);   // shared template meshes: nothing to dispose
    var self = this;
    site.stations.forEach(function (st) { self.cooking.removeStation(st); });
    this.sites.splice(this.sites.indexOf(site), 1);
  };

  // ---- per frame ----------------------------------------------------------------

  Camp.prototype.update = function () {
    var rid = this.activeId();
    var self = this;
    // camps render only in their region: built on first need, then just
    // shown / hidden (region swaps never touch them)
    this.camps().forEach(function (c) {
      var on = c.regionId === rid;
      if (on && !c.group) {
        if (c.world) {
          c.group = new THREE.Group();
          c.group.name = 'camp-world-' + c.id;
          c.modules.forEach(function (m) {
            var obj = makePiece(m.row.asset, null);
            obj.position.set(m.x, 0, m.z);
            obj.rotation.y = m.row.rotY || 0;
            c.group.add(obj);
          });
        } else {
          c.group = buildSiteGroup(c.x, c.z, c.f, null);
        }
        self.scene.add(c.group);
      }
      if (c.group) c.group.visible = on;
    });
    var p = this.player;
    if (this.placing) {
      // death or a region change while placing: cancel silently
      if (p.state !== 'alive' || rid !== this.placeRegion) this.stopPlacing();
      else if (this.pointerDirty) this.followPointer();
    }
    if (this.menuCamp && !this.resting && p.state !== 'alive') this.setMenu(null);
  };

  // kit fire props of a region, shaped like CONFIG region props for the
  // light-pool socket pass (game.js computeFireSockets)
  Camp.prototype.fireProps = function (rid) {
    var out = [];
    this.sites.forEach(function (s) {
      if (s.regionId !== rid) return;
      var yaw = siteYaw(s.f);
      s.modules.forEach(function (m) {
        if (m.row.hook !== 'cook') return;
        var A = K.assets[m.row.asset];
        out.push({ asset: A.glb, x: m.x, z: m.z, rotY: yaw + (m.row.rotY || 0), scale: A.scale });
      });
    });
    return out;
  };

  // E key route (game.js): true = the camp consumed the press
  Camp.prototype.onInteractKey = function () {
    if (this.placing) { this.confirm(); return true; }
    return false;
  };

  Camp.prototype.onKey = function (e) {
    if (e.code !== 'Escape' || e.repeat) return;
    if (this.placing) { e.preventDefault(); this.stopPlacing(); }
    else if (this.menuCamp && !this.resting) { e.preventDefault(); this.setMenu(null); }
  };

  // WH_DEBUG.camp summary
  Camp.prototype.debugState = function () {
    return {
      kitAcquired: this.cooking.kitAcquired,
      placing: this.placing,
      placeRegion: this.placeRegion,
      ghost: this.placing ? { x: this.ghostPos.x, z: this.ghostPos.z } : null,
      menuOpen: !!this.menuCamp,
      resting: this.resting,
      respawn: this.respawn,
      sites: this.sites.map(function (s) {
        return { id: s.id, regionId: s.regionId, x: s.x, z: s.z,
          fuel: s.stations.map(function (st) { return st.fuel; }),
          modules: s.modules.map(function (m) { return { id: m.row.id, x: m.x, z: m.z }; }) };
      }),
      worldCamps: this.worldCamps.map(function (c) {
        return { id: c.id, regionId: c.regionId,
          modules: c.modules.map(function (m) { return { id: m.row.id, x: m.x, z: m.z }; }) };
      })
    };
  };

  window.WH_CAMP = {
    Camp: Camp
  };
})();
