// Witch Hunter prototype v1 - main loop, camera, HUD, bootstrapping.
// Exposes window.WH_DEBUG = { player position, activeRegionId,
// prewarmedRegionId, regionStates summary, plus test helpers } (D4b-5).

(function () {
  'use strict';

  var CFG = window.WH_CONFIG;

  var game = {
    renderer: null,
    scene: null,
    camera: null,
    player: null,
    regionManager: null,
    clock: null,
    hud: {},
    running: false,
    lastFrame: 0,
    fpsFrames: 0,
    fpsTime: 0,
    fpsValue: 0,
    transitionFlash: 0,
    shakeTimer: 0,                    // v3 camera shake remaining seconds
    shakeSeed: 0                      // per-pulse random phase
  };
  window.WH_GAME = game;

  // ---- renderer / scene ------------------------------------------------------

  function setupRenderer() {
    var canvas = document.getElementById('wh-canvas');
    var renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: false });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, CFG.renderer.maxPixelRatio));
    renderer.setSize(window.innerWidth, window.innerHeight);
    // R1: sRGB output (validated Witch Hunter 3D setting)
    if (CFG.renderer.outputColorSpaceSRGB && THREE.SRGBColorSpace) {
      renderer.outputColorSpace = THREE.SRGBColorSpace;
    }
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = CFG.renderer.toneMappingExposure;
    renderer.shadowMap.enabled = CFG.renderer.shadowMapEnabled;
    return renderer;
  }

  function setupScene() {
    var scene = new THREE.Scene();
    scene.background = new THREE.Color(CFG.regionA.fogColor);
    scene.fog = new THREE.FogExp2(CFG.regionA.fogColor, CFG.regionA.fogDensity);
    return scene;
  }

  function setupLights() {
    var L = CFG.lighting;
    var amb = new THREE.AmbientLight(L.ambientColor, L.ambientIntensity);
    game.scene.add(amb);
    var hemi = new THREE.HemisphereLight(L.hemiSkyColor, L.hemiGroundColor, L.hemiIntensity);
    game.scene.add(hemi);
    var key = new THREE.DirectionalLight(L.keyColor, L.keyIntensity);
    key.position.set(30, 60, 20);
    game.scene.add(key);
    game.keyLight = key;
  }

  // ---- HUD -------------------------------------------------------------------

  function setupHud() {
    game.hud = {
      hpBar: document.getElementById('wh-hp-bar'),
      stamBar: document.getElementById('wh-stam-bar'),
      regionName: document.getElementById('wh-region-name'),
      gateHint: document.getElementById('wh-gate-hint'),
      fps: document.getElementById('wh-fps'),
      death: document.getElementById('wh-death-overlay'),
      loadNote: document.getElementById('wh-load-note'),
      reticle: document.getElementById('wh-lock-reticle')
    };
  }

  function showRegionName(name) {
    var el = game.hud.regionName;
    el.textContent = name;
    el.classList.add('visible');
    clearTimeout(game._regionNameTimer);
    game._regionNameTimer = setTimeout(function () {
      el.classList.remove('visible');
    }, CFG.hud.regionNameFadeSeconds * 1000);
  }

  function setGateHint(visible) {
    game.hud.gateHint.classList.toggle('visible', visible);
  }

  function setDeathOverlay(visible) {
    game.hud.death.classList.toggle('visible', visible);
  }

  function updateHud(dt) {
    var p = game.player;
    game.hud.hpBar.style.width = (p.hp / p.hpMax * 100) + '%';
    game.hud.stamBar.style.width = (p.stamina / p.staminaMax * 100) + '%';

    // fps
    game.fpsFrames++;
    game.fpsTime += dt;
    if (game.fpsTime >= CFG.hud.fpsUpdateInterval) {
      game.fpsValue = Math.round(game.fpsFrames / game.fpsTime);
      game.hud.fps.textContent = 'FPS: ' + game.fpsValue;
      game.fpsFrames = 0;
      game.fpsTime = 0;
    }

    // death flow
    if (p.state === 'dying' || p.state === 'dead') {
      setDeathOverlay(true);
      if (p.lockTarget) breakLockOn();   // lock breaks on player death
      if (p.state === 'dead') respawnPlayer();
    } else {
      setDeathOverlay(false);
    }
  }

  function respawnPlayer() {
    var rid = game.regionManager.logic.activeId;
    var region = window.WH_REGION_DEFS.regions[rid];
    breakLockOn();
    game.player.respawnAt(region.spawn.x, region.spawn.z);
    setDeathOverlay(false);
  }

  // ---- lock-on (D3) ------------------------------------------------------------

  // Best candidate: nearest alive enemy of the ACTIVE region within
  // maxDistance and inside a facing cone around the CAMERA forward direction.
  function pickLockTarget() {
    var L = CFG.lockOn;
    var p = game.player;
    var enemies = game.regionManager.getEnemies(game.regionManager.logic.activeId);
    // camera forward projected on xz
    var fx = Math.sin(p.camYaw + Math.PI), fz = Math.cos(p.camYaw + Math.PI);
    var halfCone = (L.facingConeDeg / 2) * Math.PI / 180;
    var best = null, bestDist = Infinity;
    for (var i = 0; i < enemies.length; i++) {
      var e = enemies[i];
      if (e.fsm === 'dead') continue;
      var dx = e.pos.x - p.pos.x, dz = e.pos.z - p.pos.z;
      var dist = Math.sqrt(dx * dx + dz * dz);
      if (dist > L.maxDistance || dist < 0.001) continue;
      var ang = Math.atan2(dx, dz);
      var dyaw = ang - Math.atan2(fx, fz);
      while (dyaw > Math.PI) dyaw -= Math.PI * 2;
      while (dyaw < -Math.PI) dyaw += Math.PI * 2;
      if (Math.abs(dyaw) > halfCone) continue;
      if (dist < bestDist) { bestDist = dist; best = e; }
    }
    return best;
  }

  function toggleLockOn() {
    if (game.player.lockTarget) breakLockOn();
    else engageLockOn();
  }

  function engageLockOn() {
    var p = game.player;
    if (p.state !== 'alive' || !game.regionManager) return;
    var t = pickLockTarget();
    if (!t) return;   // no candidate: do not engage
    p.lockTarget = t;
    // snap camera behind the player relative to the target immediately
    var dx = t.pos.x - p.pos.x, dz = t.pos.z - p.pos.z;
    if (dx * dx + dz * dz > 0.0001) p.camYaw = Math.atan2(dx, dz) + Math.PI;
  }

  function breakLockOn() {
    game.player.lockTarget = null;
  }

  // Break conditions: target death, range hysteresis, region change.
  function updateLockOn() {
    var p = game.player;
    if (!p.lockTarget) { setReticleVisible(false); return; }
    var t = p.lockTarget;
    var L = CFG.lockOn;
    var activeId = game.regionManager.logic.activeId;
    var dead = t.fsm === 'dead' || t.hp <= 0;
    var wrongRegion = t.homeRegionId !== activeId;
    var dx = t.pos.x - p.pos.x, dz = t.pos.z - p.pos.z;
    var dist = Math.sqrt(dx * dx + dz * dz);
    if (dead || wrongRegion || dist > L.maxDistance * L.hysteresis) {
      breakLockOn();
      setReticleVisible(false);
      return;
    }
    setReticleVisible(true);
    updateReticle(t);
  }

  // Project the target to screen space and position the reticle div.
  function updateReticle(target) {
    var v = new THREE.Vector3(
      target.pos.x, target.pos.y + CFG.lockOn.reticleOffsetY, target.pos.z);
    v.project(game.camera);
    var el = game.hud.reticle;
    if (v.z > 1 || v.z < -1) { el.style.display = 'none'; return; }
    var sx = (v.x * 0.5 + 0.5) * window.innerWidth;
    var sy = (-v.y * 0.5 + 0.5) * window.innerHeight;
    el.style.display = 'block';
    el.style.left = Math.round(sx) + 'px';
    el.style.top = Math.round(sy) + 'px';
  }

  function setReticleVisible(visible) {
    game.hud.reticle.style.display = visible ? 'block' : 'none';
  }

  // ---- boundary / region flow ------------------------------------------------

  // Player boundary clamp + region transitions. Passed into player.update.
  function clampPlayerToBounds(player) {
    var rm = game.regionManager;
    var conn = window.WH_REGION_DEFS.connections[0];
    if (!conn) return;
    var blocked = rm.logic.clampPlayer(player.pos);
    if (blocked) return;
    // near gate: show hint when close to the chokepoint on the A side
    var distGate = Math.abs(player.pos.x - CFG.chokepoint.centerX);
    var nearBoundary = Math.abs(player.pos.z - CFG.boundary.z) < CFG.preWarm.distance;
    setGateHint(nearBoundary && distGate < CFG.chokepoint.width * 2);
  }

  // ---- camera shake (v3 D4) ---------------------------------------------------

  // Subtle shake pulse while locked-on; amplitude decays over shake duration.
  function triggerShake() {
    game.shakeTimer = CFG.anim.shake.duration;
    game.shakeSeed = Math.random() * Math.PI * 2;
  }

  function applyCameraShake(dt) {
    if (game.shakeTimer <= 0) return;
    var S = CFG.anim.shake;
    game.shakeTimer = Math.max(0, game.shakeTimer - dt);
    var k = game.shakeTimer / S.duration;          // 1 -> 0 linear decay
    var amp = S.amplitude * k;
    var t = performance.now() / 1000 + game.shakeSeed;
    game.camera.position.x += Math.sin(t * 47) * amp;
    game.camera.position.y += Math.cos(t * 53) * amp * 0.6;
  }

  function canDamagePlayer(amount) {
    game.player.takeDamage(amount);
  }

  function applyRegionLighting(regionId) {
    var region = window.WH_REGION_DEFS.regions[regionId];
    game.scene.background = new THREE.Color(region.fogColor);
    game.scene.fog.color = new THREE.Color(region.fogColor);
    game.scene.fog.density = region.fogDensity;
    if (game.keyLight) {
      game.keyLight.intensity = CFG.lighting.keyIntensity * region.ambientLightLevel;
    }
  }

  // ---- WH_DEBUG hooks ----------------------------------------------------------

  function setupDebugHooks() {
    window.WH_DEBUG = {
      version: 'v1',
      getPlayerPosition: function () {
        var p = game.player.pos;
        return { x: p.x, y: p.y, z: p.z };
      },
      get activeRegionId() { return game.regionManager.logic.activeId; },
      get prewarmedRegionId() { return game.regionManager.logic.prewarmedId; },
      get regionStates() { return game.regionManager.debugSummary(); },
      getSceneChildCount: function () { return game.scene.children.length; },
      getRegionGroupVisibility: function (regionId) {
        var g = game.regionManager.groups[regionId];
        return g ? g.visible : null;
      },
      getEnemies: function (regionId) {
        var list = game.regionManager.getEnemies(
          regionId || game.regionManager.logic.activeId);
        return list.map(function (e) {
          return { type: e.type, fsm: e.fsm, hp: e.hp, x: e.pos.x, z: e.pos.z };
        });
      },
      getPlayer: function () { return game.player; },
      getRegionManager: function () { return game.regionManager; },
      // test helpers
      teleportPlayer: function (x, z) { game.player.pos.set(x, 0, z); },
      killPlayer: function () { game.player.hp = 0; game.player.takeDamage(1); },
      respawnPlayer: function () { game.player.state = 'dead'; },
      forceTick: function () { /* rAF runs continuously; no-op for compat */ },
      getStamina: function () { return game.player.stamina; },
      setStamina: function (v) { game.player.stamina = v; },
      // D3 lock-on hooks
      getLockTarget: function () {
        var t = game.player.lockTarget;
        if (!t) return null;
        return { type: t.type, fsm: t.fsm, hp: t.hp,
                 x: t.pos.x, z: t.pos.z, homeRegionId: t.homeRegionId };
      },
      isLocked: function () { return !!game.player.lockTarget; },
      setCameraYaw: function (deg) {
        game.player.camYaw = deg * Math.PI / 180;
      },
      engageLockOn: function () { engageLockOn(); },
      breakLockOn: function () { breakLockOn(); },
      getConfig: function () { return CFG; },
      // v3 animation hooks
      getAttackStage: function () { return game.player.getAttackStage(); },
      triggerAttack: function () { game.player.tryAttack(); },
      isRolling: function () { return game.player.rolling; },
      getEnemy: function (idx) {
        var list = game.regionManager.getEnemies(game.regionManager.logic.activeId);
        var e = list[idx];
        if (!e) return null;
        return { type: e.type, fsm: e.fsm, hp: e.hp,
                 x: e.pos.x, y: e.root.position.y, z: e.pos.z,
                 staggerTimer: e.staggerTimer, ref: e };
      }
    };
  }

  // ---- boot -------------------------------------------------------------------

  function boot() {
    game.renderer = setupRenderer();
    game.scene = setupScene();
    game.camera = new THREE.PerspectiveCamera(
      60, window.innerWidth / window.innerHeight, 0.1, 500);
    setupLights();
    setupHud();

    game.player = new window.WH_Player(game.scene, game.camera);
    game.scene.add(game.player.root);
    // D3: player delegates the F-key toggle to the game's lock-on logic
    game.player.onLockToggle = toggleLockOn;

    setupDebugHooks();

    window.WH_ASSETS.preloadAll().then(function () {
      // player body + weapon. Normalize to CFG.world.characterHeight
      // (raw Meshy characters are 2.0 tall; the pixelated variants of some
      // props differ, so normalize by measured height).
      var pBody = window.WH_ASSETS.instance('playerBody');
      var pScale = CFG.world.characterHeight /
        (window.WH_ASSETS.groundHeight('playerBody') || CFG.world.characterHeight);
      pBody.scale.setScalar(pScale);
      game.player.setBody(pBody);
      var sword = window.WH_ASSETS.instance('longsword');
      sword.scale.setScalar(0.9);
      game.player.root.add(sword);
      // v3: register the sword with the player so attack stages drive its pose
      game.player.setWeapon(sword);

      // initial region A
      game.regionManager = new window.WH_RegionManager(game.scene);
      game.regionManager.buildRegion(CFG.regionA.id, false);
      var region = window.WH_REGION_DEFS.regions[CFG.regionA.id];
      game.player.pos.set(region.spawn.x, 0, region.spawn.z);
      applyRegionLighting(CFG.regionA.id);
      showRegionName(region.name);
      game.hud.loadNote.classList.add('hidden');

      game.running = true;
      game.lastFrame = performance.now();
      requestAnimationFrame(loop);
    });
  }

  // ---- main loop ----------------------------------------------------------------

  function loop(now) {
    requestAnimationFrame(loop);
    var dtMs = now - game.lastFrame;
    game.lastFrame = now;
    if (document.hidden) return;      // pause on tab-blur (V5.3)
    var dt = Math.min(dtMs / 1000, CFG.loop.maxDt);   // dt clamp
    if (dt <= 0) return;

    var rm = game.regionManager;

    // player + transition logic
    game.player.update(dt, clampPlayerToBounds);
    var tr = rm.tickTransition(game.player.pos.x, game.player.pos.z);
    if (tr.action === 'cross') {
      // position already mapped by logic; apply to player
      game.player.pos.set(tr.mappedPos.x, 0, tr.mappedPos.z);
      applyRegionLighting(tr.newActiveId);
      showRegionName(window.WH_REGION_DEFS.regions[tr.newActiveId].name);
      setGateHint(false);
    }

    // enemies (active region only)
    rm.updateEnemies(dt, game.player.pos, game.player.state === 'alive',
      canDamagePlayer, rm.logic.activeId);

    // attack sweep vs enemies
    var sweep = game.player.consumeAttackSweep();
    if (sweep) {
      var enemies = rm.getEnemies(rm.logic.activeId);
      for (var i = 0; i < enemies.length; i++) {
        var e = enemies[i];
        if (e.fsm === 'dead') continue;
        var dx = e.pos.x - sweep.origin.x;
        var dz = e.pos.z - sweep.origin.z;
        var dist = Math.sqrt(dx * dx + dz * dz);
        if (dist > sweep.range) continue;
        var ang = Math.atan2(dx, dz);
        var dyaw = ang - game.player.yaw;
        while (dyaw > Math.PI) dyaw -= Math.PI * 2;
        while (dyaw < -Math.PI) dyaw += Math.PI * 2;
        if (Math.abs(dyaw) > sweep.halfAngle) continue;
        var dmg = sweep.damage * (e.type === 'ghoul' ? CFG.player.attackDamageGhoulBonus : 1);
        // v3: pass hit direction (player -> enemy) for stagger knockback
        var hitDir = dist > 0.001 ? { x: dx / dist, z: dz / dist } : null;
        e.takeDamage(dmg, hitDir);
        // v3 D4: shake pulse on landed melee hits, while locked-on only
        if (game.player.lockTarget) triggerShake();
      }
    }

    // lock-on break conditions + reticle (D3)
    updateLockOn();

    game.player.updateCamera(dt);
    applyCameraShake(dt);
    updateHud(dt);
    game.renderer.render(game.scene, game.camera);
  }

  window.addEventListener('resize', function () {
    if (!game.renderer) return;
    game.camera.aspect = window.innerWidth / window.innerHeight;
    game.camera.updateProjectionMatrix();
    game.renderer.setSize(window.innerWidth, window.innerHeight);
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();