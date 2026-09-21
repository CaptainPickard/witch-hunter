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
    transitionFlash: 0
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
      loadNote: document.getElementById('wh-load-note')
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
      if (p.state === 'dead') respawnPlayer();
    } else {
      setDeathOverlay(false);
    }
  }

  function respawnPlayer() {
    var rid = game.regionManager.logic.activeId;
    var region = window.WH_REGION_DEFS.regions[rid];
    game.player.respawnAt(region.spawn.x, region.spawn.z);
    setDeathOverlay(false);
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
      getConfig: function () { return CFG; }
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

    setupDebugHooks();

    window.WH_ASSETS.preloadAll().then(function () {
      // player body + weapon
      game.player.setBody(window.WH_ASSETS.instance('playerBody'));
      var sword = window.WH_ASSETS.instance('longsword');
      sword.scale.setScalar(0.9);
      game.player.root.add(sword);

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
        e.takeDamage(dmg);
      }
    }

    game.player.updateCamera(dt);
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