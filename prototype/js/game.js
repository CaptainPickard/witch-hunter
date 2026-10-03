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
    shakeSeed: 0,                     // per-pulse random phase
    firebolts: [],                    // v7: live Firebolt projectiles
    radiances: []                     // 10-04: the ONE Radiance effect (max 1, kept parked)
  };
  window.WH_GAME = game;

  // ---- renderer / scene ------------------------------------------------------

  // R3 P0-4: internal-pixel law - drawing buffer = window px / div; style.css
  // keeps the displayed size (pixel-locked upscale). Boot + resize share it.
  function internalSize() {
    var div = CFG.renderer.internalResDiv || 1;
    return {
      w: Math.max(1, Math.round(window.innerWidth / div)),
      h: Math.max(1, Math.round(window.innerHeight / div))
    };
  }

  // ---- 10-03 pixel-fidelity tuner (change order: colored pixels too large) ----
  // F1 steps the internal buffer finer, F2 chunkier, through {1..4} live:
  // renderer.setSize re-inits the drawing buffer (resize handler already does
  // the same thing on window resizes), CSS keeps the on-screen size, so only
  // the pixel granularity of the 3D buffer changes mid-run.
  game.resTuner = {
    steps: [1, 2, 3, 4],
    readoutTimer: null
  };

  function applyResDiv(div) {
    CFG.renderer.internalResDiv = div;
    if (!game.renderer) return;   // pre-boot keypress: CONFIG already updated
    var isz = internalSize();
    game.renderer.setSize(isz.w, isz.h, false);   // updateStyle=false - CSS keeps display size
  }

  function showResReadout() {
    var wrap = document.getElementById('wh-res-tuner');
    var read = document.getElementById('wh-res-readout');
    if (!wrap || !read) return;
    var d = CFG.renderer.internalResDiv;
    var label = d === 1 ? 'full res' : 'px x' + d;
    read.textContent = 'Pixel fidelity: ' + d + ' (' + label + ')';
    wrap.classList.remove('dim');
    wrap.classList.add('pulse');
    clearTimeout(game.resTuner.readoutTimer);
    game.resTuner.readoutTimer = setTimeout(function () {
      wrap.classList.add('dim');
    }, 2500);
  }

  function stepResDiv(dir) {
    var steps = game.resTuner.steps;
    var d = CFG.renderer.internalResDiv;
    var i = steps.indexOf(d);
    if (i < 0) {   // hand-edited config value: snap to nearest known stepper
      for (i = 0; i < steps.length && steps[i] < d; i++) {}
    }
    i = Math.min(steps.length - 1, Math.max(0, i + dir));
    if (steps[i] !== d) applyResDiv(steps[i]);
    showResReadout();
  }

  function bindResTunerKeys() {
    document.addEventListener('keydown', function (e) {
      if (e.code === 'F1') {
        e.preventDefault();   // stop browser help overlay
        if (!e.repeat) stepResDiv(-1);
      } else if (e.code === 'F2') {
        e.preventDefault();
        if (!e.repeat) stepResDiv(1);
      }
    });
  }

  function setupRenderer() {
    var canvas = document.getElementById('wh-canvas');
    var renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: false });
    // R3 P0-4: pixelation requires dpr 1 (supersedes maxPixelRatio);
    // updateStyle=false so CSS drives the display size.
    var isz = internalSize();
    renderer.setPixelRatio(1);
    renderer.setSize(isz.w, isz.h, false);
    // R1: sRGB output (validated Witch Hunter 3D setting)
    if (CFG.renderer.outputColorSpaceSRGB && THREE.SRGBColorSpace) {
      renderer.outputColorSpace = THREE.SRGBColorSpace;
    }
    // R2 P0-3: Neutral tonemap so fog stays brightest; ACES fallback for
    // older/no Neutral builds (vanilla var function only).
    if (THREE.NeutralToneMapping) {
      renderer.toneMapping = THREE.NeutralToneMapping;   // r185 property exists (verified)
    } else if (THREE.ACESFilmicToneMapping) {
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
    }
    renderer.toneMappingExposure = CFG.renderer.toneMappingExposure;
    renderer.shadowMap.enabled = CFG.renderer.shadowMapEnabled;
    return renderer;
  }

  function setupScene() {
    var scene = new THREE.Scene();
    // 10-03 order 4: near-black background - sky luminance comes from the
    // dome rig; fog color no longer fills the world via scene.background.
    scene.background = new THREE.Color(0x05070f);
    scene.fog = new THREE.FogExp2(CFG.regionA.fogColor, CFG.regionA.fogDensity);
    return scene;
  }

  // R2 P0-3: moon-and-lantern night rig. AmbientLight removed - the hemisphere
  // is now the only fill. Pool creation (R2-3) slots into this function later;
  // no pool code lives here in this chunk.
  function setupLights() {
    var L = CFG.lighting;
    var hemi = new THREE.HemisphereLight(L.hemiSkyColor, L.hemiGroundColor,
      L.hemiBaseIntensity);
    game.scene.add(hemi);
    game.hemiLight = hemi;

    // Moon: directional clamped to the -z side (azimuth from +/-z axis, deg),
    // elevation 25-35 deg. Aimed via target at world origin.
    var az = (L.moonAzimuthDeg || 0) * Math.PI / 180;
    var el = (L.moonElevationDeg || 30) * Math.PI / 180;
    var dir = L.moonDirectionDistance || 60;
    var moon = new THREE.DirectionalLight(L.moonColor, L.moonIntensity);
    moon.position.set(
      Math.round(Math.sin(az) * Math.cos(el) * dir * 10) / 10,
      Math.round(Math.sin(el) * dir * 10) / 10,
      -Math.round(Math.cos(az) * Math.cos(el) * dir * 10) / 10
    );
    moon.target.position.set(0, 0, 0);
    game.scene.add(moon);
    game.scene.add(moon.target);
    game.moonLight = moon;

    // Player lantern: PointLight parented into the player chain. Attach target
    // is game.player.yawFrame when available, else game.player.root (boot order
    // note: setupLights runs before the player exists; the lantern lights the
    // scene rig at boot and re-parents below).
    var lantern = new THREE.PointLight(L.lanternColor, L.lanternIntensity,
      L.lanternDistance, L.lanternDecay);
    var attach = (game.player && (game.player.yawFrame || game.player.root)) ||
      game.scene;
    var off = L.lanternAnchorOffset;
    lantern.position.set(off[0], off[1], off[2]);
    attach.add(lantern);
    game.lantern = lantern;

    // R2 P1-8: fixed pool of 4 PointLights + flame cards, created ONCE at boot
    // BEFORE the first render so the shader light count never changes (M-19).
    var P = CFG.lightPool;
    game.lightPool = [];
    game.flameCards = [];
    game.lightPoolT = 0;
    var texLoader = new THREE.TextureLoader();
    var emberTex = texLoader.load(window.WH_ASSETS.resolveUrl(
      'art-direction/3d/assets/textures/particles/particle-ember.png'));
    for (var pi = 0; pi < P.size; pi++) {
      var pl = new THREE.PointLight(P.color, 0, P.distance, P.decay);
      game.scene.add(pl);
      game.lightPool.push(pl);
      var cardMat = new THREE.SpriteMaterial({ map: emberTex,
        blending: THREE.AdditiveBlending, transparent: true, depthWrite: false });
      var card = new THREE.Sprite(cardMat);
      card.scale.set(0.55, 0.77, 1);
      card.visible = false;
      game.scene.add(card);
      game.flameCards.push(card);
    }
  }

  // R2 P0-3: re-parent the lantern into the player's yawFrame once the player
  // body exists (left-hip anchor = left side of the character, yawFrame space,
  // so the light turns with the player). Called from boot after setBody().
  function attachPlayerLantern() {
    var L = CFG.lighting;
    if (!game.lantern || !game.player || !game.player.yawFrame) return;
    if (game.lantern.parent !== game.player.yawFrame) {
      game.player.yawFrame.add(game.lantern);
    }
    var off = L.lanternAnchorOffset;
    game.lantern.position.set(off[0], off[1], off[2]);
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
    // 2026-10-03 boot loading screen: title + REAL progress bar overlay.
    // The bar is the fraction of manifest assets settled (loaded OR
    // stand-in); assets.js fires one tick per asset settle.
    game.hud.bootBar = document.getElementById('wh-boot-bar');
    game.hud.bootBarFill = document.getElementById('wh-boot-bar-fill');
    game.hud.bootSub = document.getElementById('wh-boot-sub');
    game.hud.bootAssetsDone = 0;
    game.hud.bootAssetsTotal = Object.keys(window.WH_ASSETS.MANIFEST).length;
    window.WH_ASSETS.setBootProgressCb(function () {
      game.hud.bootAssetsDone++;
      game.hud.bootBarFill.style.width =
        Math.round(100 * game.hud.bootAssetsDone / game.hud.bootAssetsTotal) + '%';
      game.hud.bootSub.textContent = 'Loading assets... ' +
        game.hud.bootAssetsDone + ' / ' + game.hud.bootAssetsTotal;
    });
    // v6: block/parry feedback cues, DOM only. The stamina bar already exists
    // in index.html and reflects the drain via updateHud.
    var flash = document.createElement('div');
    flash.id = 'wh-block-flash';
    document.getElementById('wh-hud').appendChild(flash);
    game.hud.blockFlash = flash;
    var gbText = document.createElement('div');
    gbText.id = 'wh-guard-break-text';
    gbText.textContent = 'GUARD BROKEN';
    document.getElementById('wh-hud').appendChild(gbText);
    game.hud.guardBreakText = gbText;
    game.hud.flashTimer = 0;
    game.hud.flashTimerMax = 0;

    // v7: focus bar above the stamina bar (same bar style, blue fill)
    var focusLabel = document.createElement('div');
    focusLabel.className = 'bar-label';
    focusLabel.textContent = 'Focus';
    focusLabel.id = 'wh-focus-label';
    focusLabel.style.textTransform = 'none';  // v7: keep case for test visibility
    document.getElementById('wh-bars').appendChild(focusLabel);
    var focusOuter = document.createElement('div');
    focusOuter.className = 'bar-outer';
    focusOuter.id = 'wh-focus-bar-outer';
    var focusFill = document.createElement('div');
    focusFill.className = 'bar-fill focus';
    focusFill.id = 'wh-focus-bar';
    focusOuter.appendChild(focusFill);
    document.getElementById('wh-bars').appendChild(focusOuter);
    game.hud.focusBar = focusFill;

    // v7: bottom-center belt row: 5 spell slots | divider | 2 consumables
    // | divider | 2 loadout pips I/II
    var belt = document.createElement('div');
    belt.id = 'wh-belt';
    var B = CFG.belt;
    game.hud.beltSlots = [];
    for (var s = 0; s < B.slots; s++) {
      var slot = document.createElement('div');
      slot.className = 'belt-slot';
      slot.textContent = String(s + 1);
      belt.appendChild(slot);
      game.hud.beltSlots.push(slot);
    }
    var div1 = document.createElement('div');
    div1.className = 'belt-divider spell-divider';
    belt.appendChild(div1);
    game.hud.consSlots = [];
    var consKeys = ['R', 'T'];
    for (var c = 0; c < B.consumableSlots; c++) {
      var cslot = document.createElement('div');
      cslot.className = 'belt-slot consumable';
      cslot.textContent = consKeys[c] || '';
      belt.appendChild(cslot);
      game.hud.consSlots.push(cslot);
    }
    var div2 = document.createElement('div');
    div2.className = 'belt-divider';
    belt.appendChild(div2);
    game.hud.loadoutPips = [];
    for (var l = 0; l < 2; l++) {
      var pip = document.createElement('div');
      pip.className = 'loadout-pip';
      pip.textContent = l === 0 ? 'I' : 'II';
      belt.appendChild(pip);
      game.hud.loadoutPips.push(pip);
    }
    document.getElementById('wh-hud').appendChild(belt);
    game.hud.belt = belt;

    // v7: offhand spell glow (left-hand anchor, school-colored emissive)
    game.spellGlow = new THREE.Mesh(
      new THREE.SphereGeometry(0.12, 8, 6),
      new THREE.MeshBasicMaterial({ color: 0xff7722 })
    );
    game.spellGlow.visible = false;
  }

  // Order B glove placeholder (no glove mesh yet). anchor 'hand': child of
  // the skinned hand bone at CONFIG.equip.casterGlow.handOffset (L_Hand-
  // local fist centroid, mirrored for R_Hand), so it rides the animation.
  // anchor 'idlePose' (or the rigid stand-in): the old yawFrame anchor =
  // the weapon idle pose mirrored for the left hand.
  function updateCasterGlow(p) {
    var G = CFG.equip.casterGlow;
    var hand = p.casterHand();
    var glow = game.spellGlow;
    glow.visible = !!hand;
    if (!hand) return;
    var sid = p.getSelectedSpellId();
    if (sid && CFG.spell[sid]) glow.material.color.setHex(CFG.spell[sid].schoolColor);
    var bone = G.anchor === 'hand' && p.body
      ? p.body.getObjectByName(hand === 'left' ? 'L_Hand' : 'R_Hand', true) : null;
    if (bone) {
      if (glow.parent !== bone) bone.add(glow);
      var o = G.handOffset, m = hand === 'left' ? [1, 1, 1] : CFG.equip.mirrorScale;
      glow.position.set(o[0] * m[0], o[1] * m[1], o[2] * m[2]);
    } else {
      if (glow.parent !== p.yawFrame) p.yawFrame.add(glow);
      var ip = CFG.moveset.idlePose;
      glow.position.set((hand === 'left' ? -1 : 1) * ip.pos[0], ip.pos[1], ip.pos[2]);
    }
  }

  // v6: HUD screen-edge flash pulse (DOM opacity, no WebGL work).
  function flashScreen(durationSec, kind) {
    var el = game.hud.blockFlash;
    el.classList.remove('parry', 'block', 'guardbreak');
    void el.offsetWidth;                     // restart the CSS transition
    el.classList.add(kind);
    game.hud.flashTimer = durationSec;
    game.hud.flashTimerMax = durationSec;
    el.style.opacity = '1';
  }

  function updateBlockHud(dt) {
    if (game.hud.flashTimer > 0) {
      game.hud.flashTimer = Math.max(0, game.hud.flashTimer - dt);
      var el = game.hud.blockFlash;
      var frac = game.hud.flashTimerMax > 0
        ? game.hud.flashTimer / game.hud.flashTimerMax : 0;
      el.style.opacity = String(frac);
      if (game.hud.flashTimer <= 0) el.style.opacity = '0';
    }
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
    // v7: armed state = weapon emissive pulse while armedTimer > 0
    if (p.sword && p.sword.material) {
      if (!p.swordBaseEmissive && p.sword.material.emissive) {
        p.swordBaseEmissive = {
          hex: p.sword.material.emissive.getHex(),
          intensity: p.sword.material.emissiveIntensity !== undefined
            ? p.sword.material.emissiveIntensity : 1
        };
      }
      if (p.armedTimer > 0) {
        var pulse = 0.5 + 0.5 * Math.sin(performance.now() / 1000 * 8);
        var armedHex = p.crossArmed ? 0xffd24a : 0xff7722;  // gold cross / orange armed
        p.sword.material.emissive.setHex(armedHex);
        if (p.sword.material.emissiveIntensity !== undefined) {
          p.sword.material.emissiveIntensity = 0.4 + pulse * 0.9;
        }
      } else if (p.swordBaseEmissive) {
        p.sword.material.emissive.setHex(p.swordBaseEmissive.hex);
        if (p.sword.material.emissiveIntensity !== undefined) {
          p.sword.material.emissiveIntensity = p.swordBaseEmissive.intensity;
        }
      }
    }
    // v7: focus bar
    if (game.hud.focusBar) {
      game.hud.focusBar.style.width = (p.focus / p.focusMax * 100) + '%';
    }
    // v7: belt HUD state (selected tint, active pip)
    if (game.hud.belt) {
      // Order B: tint = the ACTIVE learned spell (always shown, so belt
      // keys confirm even with no caster); no caster in hand dims the spell
      // slots and badges the divider (CSS #wh-belt.stowed)
      var stowed = !p.hasCaster();
      game.hud.belt.classList.toggle('stowed', stowed);
      var spellId = p.getSelectedSpellId();
      var SC = spellId ? CFG.spell[spellId].schoolColor : null;
      var hex = SC ? '#' + ('000000' + SC.toString(16)).slice(-6) : '';
      for (var i = 0; i < game.hud.beltSlots.length; i++) {
        var el = game.hud.beltSlots[i];
        var has = !!p.belt[i];
        var sel = (i === p.selectedBeltSlot);
        el.classList.toggle('filled', has);
        el.classList.toggle('selected', sel);
        el.style.borderColor = (sel && SC) ? hex : '';
        el.style.color = (sel && SC) ? hex : '';
      }
      for (var ci = 0; ci < game.hud.consSlots.length; ci++) {
        var cs = game.hud.consSlots[ci];
        var cc = p.consumables[ci];
        cs.classList.toggle('filled', !!(cc && cc.charges > 0));
      }
      for (var pi = 0; pi < game.hud.loadoutPips.length; pi++) {
        game.hud.loadoutPips[pi].classList.toggle(
          'active', p.activeLoadout === pi + 1);
      }
    }
    // v7 spell glow. Order B: the magic glove's placeholder visual - shown
    // on the hand holding the caster (school color of the active spell).
    if (game.spellGlow && p.yawFrame) updateCasterGlow(p);
    updateBlockHud(dt);   // v6: flash decay

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
    // R5 P0-5: prop colliders run after the plane + rim clamp on EVERY frame
    // (including frames where it fired); a push-out landing past the plane
    // or rim is re-clamped once.
    if (rm.pushOutOfProps(player.pos, CFG.player.radius)) {
      blocked = rm.logic.clampPlayer(player.pos) || blocked;
    }
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

  // v6: all enemy damage routes through the block/parry choke point.
  function damagePlayerFromEnemy(amount, attacker) {
    game.player.resolveIncomingHit(amount, attacker);
  }

  // R2 P0-3: region lighting = fog swap + hemi fill scaled to the region's
  // ambientLightLevel (fill = hemiBaseIntensity * ambientLightLevel). The old
  // keyLight is gone; moon and lantern are region-independent.
  function applyRegionLighting(regionId) {
    var region = window.WH_REGION_DEFS.regions[regionId];
    // 10-03 order 4: background stays near-black (sky dome owns the view);
    // fog keeps its regional color/density for the ground haze.
    game.scene.fog.color = new THREE.Color(region.fogColor);
    game.scene.fog.density = region.fogDensity;
    if (game.hemiLight) {
      // B reads darker: 1.15x the already-cut base fill (order 4)
      var mult = regionId === CFG.regionB.id ?
        (CFG.lighting.regionBFillMult || 1.0) : 1.0;
      var fill = CFG.lighting.hemiBaseIntensity * region.ambientLightLevel * mult;
      game.hemiLight.intensity = fill;
    }
  }

  // 10-03 order 4: starry night sky. Dome sphere (BackSide, fog:false,
  // depthWrite off) with a vertical-gradient shader; 600 Points stars on the
  // dome; moon = additive glow sprite + core disc billboard at the directional
  // moon's direction. World-anchored via skyTick (player walks, dome stays).
  function setupSky() {
    var S = CFG.sky;
    var group = new THREE.Group();
    group.name = 'sky-rig';

    var domeMat = new THREE.ShaderMaterial({
      side: THREE.BackSide,
      depthWrite: false,
      fog: false,
      uniforms: {
        zenith: { value: new THREE.Color(S.zenithColor) },
        band: { value: new THREE.Color(S.horizonBand) },
        glow: { value: new THREE.Color(S.horizonGlow) },
        glowStop: { value: S.horizonGlowStop }
      },
      vertexShader: [
        'varying vec3 vDir;',
        'void main() {',
        '  vDir = normalize(position);',
        '  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);',
        '}'
      ].join('\n'),
      fragmentShader: [
        'varying vec3 vDir;',
        'uniform vec3 zenith;',
        'uniform vec3 band;',
        'uniform vec3 glow;',
        'uniform float glowStop;',
        'void main() {',
        '  float h = clamp(vDir.y, -1.0, 1.0);',          // -1 nadir .. 1 zenith
        '  float t = clamp(h * 2.2, 0.0, 1.0);',          // band -> zenith ramp
        '  vec3 col = mix(band, zenith, t);',
        // pale ash glow hugging the horizon (fog meets sky), gone by glowStop
        '  float g = (1.0 - smoothstep(0.0, ' + S.horizonGlowStop.toFixed(2) +
          ', abs(h) * 5.0)) * 0.5;',
        '  col = mix(col, glow, clamp(g, 0.0, 1.0));',
        '  gl_FragColor = vec4(col, 1.0);',
        '}'
      ].join('\n')
    });
    var dome = new THREE.Mesh(new THREE.SphereGeometry(S.domeRadius, 32, 20), domeMat);
    dome.renderOrder = -10;           // draw first; stars/moon after
    group.add(dome);

    // stars: Points with per-star size/color/phase attributes, sizeAttenuation
    // off (angular size like real stars), additive so overlaps stay soft.
    function buildStarTexture() {
      var c = document.createElement('canvas');
      c.width = 16; c.height = 16;
      var x = c.getContext('2d');
      x.fillStyle = '#ffffff';
      // blocky plus shape (pixel-art star, NEAREST)
      x.fillRect(7, 3, 2, 10);
      x.fillRect(3, 7, 10, 2);
      var t = new THREE.CanvasTexture(c);
      t.magFilter = THREE.NearestFilter;
      t.minFilter = THREE.NearestFilter;
      t.generateMipmaps = false;
      return t;
    }
    var starGeo = new THREE.BufferGeometry();
    var pos = [], col = [], siz = [], phs = [];
    var seedState = 1188;
    function sRand() {   // mulberry-ish deterministic
      seedState = (seedState * 1103515245 + 12345) & 0x7fffffff;
      return seedState / 0x7fffffff;
    }
    var cPalette = S.starColors.map(function (h) { return new THREE.Color(h); });
    for (var i = 0; i < S.starCount; i++) {
      // distribute on the upper dome (y from -0.08 to near 1), avoid nadir
      var u = sRand() * 2 - 1;                 // cos theta
      var yy = Math.max(-0.08, Math.pow(Math.abs(u), 0.65) * (u < 0 ? -1 : 1));
      var theta = Math.acos(Math.max(-1, Math.min(1, yy)));
      var phi = sRand() * Math.PI * 2;
      var st = Math.sin(theta);
      pos.push(S.domeRadius * 0.98 * st * Math.cos(phi),
               S.domeRadius * 0.98 * yy,
               S.domeRadius * 0.98 * st * Math.sin(phi));
      var c = cPalette[Math.floor(sRand() * cPalette.length)];
      col.push(c.r, c.g, c.b);
      siz.push(S.starSizeMin + sRand() * (S.starSizeMax - S.starSizeMin));
      phs.push(sRand() < S.twinklePct / 100 ? sRand() * 6.28 : -1.0);
    }
    starGeo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    starGeo.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
    starGeo.setAttribute('aSize', new THREE.Float32BufferAttribute(siz, 1));
    starGeo.setAttribute('aPhase', new THREE.Float32BufferAttribute(phs, 1));
    var starMat = new THREE.ShaderMaterial({
      transparent: true,
      depthWrite: false,
      fog: false,
      blending: THREE.AdditiveBlending,
      uniforms: {
        map: { value: buildStarTexture() },
        time: { value: 0 }
      },
      vertexShader: [
        'attribute float aSize;',
        'attribute float aPhase;',
        'uniform float time;',
        'varying vec3 vColor;',
        'varying float vTw;',
        'void main() {',
        '  vColor = color;',
        '  vTw = aPhase < 0.0 ? 1.0 : (0.55 + 0.45 * sin(time * 1.7 + aPhase));',
        '  vec4 mv = modelViewMatrix * vec4(position, 1.0);',
        '  gl_PointSize = aSize * vTw;',
        '  gl_Position = projectionMatrix * mv;',
        '}'
      ].join('\n'),
      fragmentShader: [
        'uniform sampler2D map;',
        'varying vec3 vColor;',
        'varying float vTw;',
        'void main() {',
        '  vec4 tx = texture2D(map, gl_PointCoord);',
        '  gl_FragColor = vec4(vColor * vTw, 1.0) * tx;',
        '}'
      ].join('\n'),
      vertexColors: true
    });
    starMat.vertexColors = true;
    var stars = new THREE.Points(starGeo, starMat);
    stars.renderOrder = -9;
    group.add(stars);

    // moon: additive glow sprite + core disc billboard at the moon direction
    var az = (CFG.lighting.moonAzimuthDeg || S.moonAzimuthDeg) * Math.PI / 180;
    var el = (CFG.lighting.moonElevationDeg || S.moonElevationDeg) * Math.PI / 180;
    var moonDir = new THREE.Vector3(
      Math.sin(az) * Math.cos(el),
      Math.sin(el),
      -Math.cos(az) * Math.cos(el));   // -z side like the directional rig
    var moonPos = moonDir.clone().multiplyScalar(S.moonDistance);

    function moonSprite(hex, size, opacity) {
      var c = document.createElement('canvas');
      c.width = 64; c.height = 64;
      var x = c.getContext('2d');
      var g = x.createRadialGradient(32, 32, 4, 32, 32, 32);
      g.addColorStop(0, 'rgba(255,255,255,' + opacity + ')');
      g.addColorStop(0.5, 'rgba(255,255,255,' + (opacity * 0.35) + ')');
      g.addColorStop(1, 'rgba(255,255,255,0)');
      x.fillStyle = g;
      x.fillRect(0, 0, 64, 64);
      var t = new THREE.CanvasTexture(c);
      t.colorSpace = THREE.SRGBColorSpace;
      var m = new THREE.SpriteMaterial({
        map: t, color: hex, transparent: true, opacity: 1,
        blending: THREE.AdditiveBlending, depthWrite: false, fog: false
      });
      var sp = new THREE.Sprite(m);
      sp.scale.set(size, size, 1);
      sp.position.copy(moonPos);
      return sp;
    }
    var glow = moonSprite(S.moonGlowColor, S.moonSizePx * 3.2, 0.5);
    glow.renderOrder = -8;
    var core = moonSprite(S.moonColor, S.moonSizePx, 1.0);
    core.renderOrder = -7;
    group.add(glow);
    group.add(core);

    game.sky = { group: group, stars: stars, starMat: starMat };
    game.scene.add(group);
  }

  // per-frame: stars twinkle clock (dome/moon are camera-distance invariant)
  function skyTick() {
    if (game.sky && game.sky.starMat) {
      game.sky.starMat.uniforms.time.value = performance.now() / 1000;
    }
  }

  // Hand-held GLB instance at its measured size (2026-10-03: longsword
  // 1.988m GLB -> 1.05m hand-held via CONFIG.assets.weaponScale; 10-04
  // roundShield via weaponTargetHeight.roundShield / disc height).
  function instanceHandMesh(name) {
    var mesh = window.WH_ASSETS.instance(name);
    if (!mesh) return null;
    mesh.scale.setScalar(window.WH_ASSETS.weaponScale(name));
    return mesh;
  }

  // 10-04 debug path (WH_DEBUG.equipWeapon): swap the melee moveset
  // (CONFIG.moveset.weapons[id]) and its hand mesh.
  function equipPlayerWeapon(id) {
    if (!CFG.moveset.weapons[id]) return false;
    var mesh = instanceHandMesh(id);
    if (!mesh) return false;
    return game.player.equipWeapon(id, mesh);
  }

  // Order B: one mesh per gear item with a CONFIG.items[id].mesh asset (the
  // magic glove has none yet - its placeholder is the spell glow). The
  // player mounts each on whichever hand holds it, hidden while stowed.
  function setupHandMeshes() {
    for (var id in CFG.items) {
      var d = CFG.items[id];
      if (d.category !== 'gear' || !d.mesh) continue;
      var mesh = instanceHandMesh(d.mesh);
      if (mesh) game.player.setItemMesh(id, mesh);
    }
  }

  // 10-04: Radiance cast. Max one: a recast refreshes the existing effect
  // (timer back to full, fade back up), even after it expired and parked.
  function castRadiance(spellId) {
    var fx = game.radiances[0];
    if (fx) {
      fx.refresh();
    } else {
      fx = window.WH_SPELLS.spawn(game.scene, spellId);
      if (!fx) return;
      game.radiances.push(fx);
    }
    fx.attach(game.player);
  }

  // ---- 10-05 inventory (Order A) ------------------------------------------------
  // The player's Inventory + the I-key screen. Opening the screen suspends
  // player movement/combat/camera input (player.setInputSuspended); the
  // world keeps running.
  function setupInventory() {
    var INV = window.WH_INVENTORY;
    game.inventory = new INV.Inventory();
    INV.active = game.inventory;
    game.player.inventory = game.inventory;
    // fresh-spawn kit (CONFIG.inventory.startingItems), then Order B pulls
    // CONFIG.equip.defaultHands out of it into the hands (glove left,
    // longsword right). Boot only - death keeps inventory + hands.
    game.inventory.fillStartingItems();
    game.player.equipDefaultHands();
    var p = game.player;
    game.inventoryUI = new INV.InventoryUI({
      inventory: game.inventory,
      onOpenChange: function (open) { p.setInputSuspended(open); },
      onDrop: dropFromSlot,
      // Order B CHARACTER tab: the UI only calls these, player owns the rules
      equip: {
        hands: function () { return p.hands; },
        equip: function (id, hand) { return p.equipItem(id, hand); },
        unequip: function (hand) { return p.unequipHand(hand); },
        spells: function () { return p.getKnownSpells(); },
        selectSpell: function (slot) { p.pressBeltKey(slot); }
      }
    });
    p.onEquipRefusal = function (text) {
      game.inventoryUI.toast(text);
      flashScreen(CFG.block.blockFlashSeconds, 'block');
    };
    p.onHandsChanged = function () { game.inventoryUI.render(); };
    game.worldItems = new INV.WorldItems(game.scene);
    document.addEventListener('keydown', function (e) {
      if (e.code !== CFG.inventoryUI.pickupKey || e.repeat) return;
      if (game.player.inputSuspended || game.player.state !== 'alive') return;
      tryPickup();
    });
  }

  // G on the selected stack: 1 unit, or the whole stack with Shift.
  // drop.mode 'void' deletes it; 'physical' puts one item entity carrying
  // the dropped count at the player's feet + scatter.
  function dropFromSlot(slotIndex, wholeStack) {
    var s = game.inventory.slotAt(slotIndex);
    if (!s) return;
    var taken = game.inventory.removeFromSlot(slotIndex, wholeStack ? s.count : 1);
    var D = CFG.inventory.drop;
    if (D.mode === 'void') {
      game.inventoryUI.toast('Dropped ' + window.WH_INVENTORY.itemDef(taken.id).name +
        ' x' + taken.count);
      return;
    }
    // uniform point in the scatter disc, then the player's own bounds +
    // prop push-out so a drop never lands somewhere it cannot be walked to
    var ang = Math.random() * Math.PI * 2;
    var r = D.scatterRadius * Math.sqrt(Math.random());
    var p = game.player.pos;
    var at = new THREE.Vector3(p.x + Math.sin(ang) * r, 0, p.z + Math.cos(ang) * r);
    var rm = game.regionManager;
    rm.logic.clampPlayer(at);
    if (rm.pushOutOfProps(at, CFG.player.radius)) rm.logic.clampPlayer(at);
    game.worldItems.spawn(taken.id, taken.count, at.x, at.z, rm.logic.activeId);
  }

  // E: nearest item entity within pickupRadius goes into the inventory
  // (stack-join first). Whatever does not fit stays on the ground.
  function tryPickup() {
    var p = game.player.pos;
    var ent = game.worldItems.nearest(p.x, p.z, CFG.inventory.drop.pickupRadius,
      game.regionManager.logic.activeId);
    if (!ent) return;
    var added = game.inventory.addItem(ent.id, ent.count);
    var name = window.WH_INVENTORY.itemDef(ent.id).name;
    if (added <= 0) {
      game.inventoryUI.toast('Inventory full');
      return;
    }
    ent.count -= added;
    if (ent.count <= 0) {
      game.worldItems.remove(ent);
      game.inventoryUI.toast('Picked up ' + name + ' x' + added);
    } else {
      game.inventoryUI.toast('Inventory full');
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
      getAssetMeta: function (name) { return window.WH_ASSETS.getMeta(name); },
      getLightPool: function () {
        return (game.lightPool || []).map(function (l, i) {
          return { i: i, intensity: l.intensity, socketId: l.whSocketId || null,
                   x: l.position.x, y: l.position.y, z: l.position.z };
        });
      },
      getLightSockets: function () { return game.lastSockets || []; },
      getAnimState: function (entity) {
        var target = entity === undefined || entity === 'player' ? game.player : entity;
        if (typeof entity === 'number') target = game.regionManager.getEnemies(
          game.regionManager.logic.activeId)[entity];
        if (target && target.ref) target = target.ref;
        return target && target.anim ? target.anim.getState() : null;
      },
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
      getComboIndex: function () { return game.player.comboIndex; },
      getCurrentMove: function () {
        var p = game.player;
        var M = p.attackMove || p.getChainMove(p.comboIndex);
        return window.WH_MOVESET[M.pose] || window.WH_MOVESET.m1;
      },
      // 10-04 moveset framework hooks
      getMoveDef: function () {
        var p = game.player;
        return { weapon: p.weaponId, moveId: p.attackMoveId, move: p.attackMove,
                 phase: p.getAttackPhase() };
      },
      equipWeapon: function (id) { return equipPlayerWeapon(id); },
      isRolling: function () { return game.player.rolling; },
      getEnemy: function (idx) {
        var list = game.regionManager.getEnemies(game.regionManager.logic.activeId);
        var e = list[idx];
        if (!e) return null;
        return { type: e.type, fsm: e.fsm, hp: e.hp,
                 x: e.pos.x, y: e.root.position.y, z: e.pos.z,
                 staggerTimer: e.staggerTimer, ref: e };
      },
      // v6 block/parry hooks
      isBlocking: function () { return game.player.blocking; },
      getParryWindowRemaining: function () {
        return game.player.getParryWindowRemaining();
      },
      forceGuardBreak: function () {
        var p = game.player;
        p.guardBroken = true;
        p.guardBreakTimer = CFG.block.guardBreakStun;
        p.endBlock();
        p.stamina = 0;
        // v7: guard break counterplay clears armed finisher state
        p.armedTimer = 0;
        p.crossArmed = false;
        if (p.onGuardBreak) p.onGuardBreak();
      },
      isGuardBroken: function () { return game.player.guardBroken; },
      forceStagger: function (idx, dur) {
        var list = game.regionManager.getEnemies(game.regionManager.logic.activeId);
        var e = list[idx];
        if (!e) return false;
        e.enterStagger(dur || CFG.block.riposteStaggerDur);
        return true;
      },
      isEnemyStaggered: function (idx) {
        var list = game.regionManager.getEnemies(game.regionManager.logic.activeId);
        var e = list[idx];
        return !!(e && e.isStaggered && e.isStaggered());
      },
      getEnemyRiposteArmed: function (idx) {
        var list = game.regionManager.getEnemies(game.regionManager.logic.activeId);
        var e = list[idx];
        return !!(e && e.riposteArmed);
      },
      tryBlock: function () { game.player.tryBlock(); },
      endBlock: function () { game.player.endBlock(); },
      // v7 weave hooks
      getFocus: function () { return game.player.focus; },
      setFocus: function (v) { game.player.focus = v; game.player.focusRegenBlock = 0.1; },  // v7: brief regen pause for debug stability
      getBelt: function () { return game.player.getBelt(); },
      selectBeltSlot: function (i) { game.player.selectBeltSlot(i); },
      pressBeltKey: function (i) { game.player.pressBeltKey(i); },
      // Order B hand hooks
      getHands: function () {
        var p = game.player;
        return { right: p.hands.right, left: p.hands.left,
                 caster: p.hasCaster(), shield: p.hasShield(), meleeRight: p.hasMeleeRight(),
                 rmb: p.secondaryAction() };
      },
      equipItem: function (id, hand) { return game.player.equipItem(id, hand); },
      unequipHand: function (hand) { return game.player.unequipHand(hand); },
      getActiveLoadout: function () { return game.player.activeLoadout; },
      toggleLoadout: function () { game.player.toggleLoadout(); },
      getCastState: function () {
        var p = game.player;
        return {
          windup: p.castWindup,
          cooldown: p.castCooldown,
          regrip: p.regripTimer,
          toggling: p.toggling
        };
      },
      getRadianceState: function () {
        var fx = game.radiances[0];
        return {
          active: !!(fx && fx.active),
          remainingSeconds: fx ? fx.remaining : 0,
          lightIntensity: fx ? fx.light.intensity : 0
        };
      },
      getArmedState: function () {
        var p = game.player;
        return { timer: p.armedTimer, cross: p.crossArmed };
      },
      getFirebolts: function () {
        return game.firebolts.map(function (f) {
          return { x: f.pos.x, z: f.pos.z, alive: f.alive };
        });
      },
      // 10-05 inventory hooks (AC E setup: addItem('longsword', 24) fills
      // every slot - gear stacks to 1)
      getInventory: function () {
        var out = [];
        game.inventory.forEachSlot(function (sl) { out.push(sl); });
        return out;
      },
      addItem: function (id, count) { return game.inventory.addItem(id, count); },
      getWorldItems: function () {
        return game.worldItems.list.map(function (it) {
          return { id: it.id, count: it.count, x: it.x, z: it.z, regionId: it.regionId };
        });
      },
      isInventoryOpen: function () { return !!(game.inventoryUI && game.inventoryUI.open); },
      useConsumable: function (slot) { game.player.useConsumable(slot); },
      getConsumables: function () { return game.player.getConsumables(); },
      getCombo: function () {
        return { index: game.player.comboIndex, queued: game.player.comboQueued,
                 buffer: game.player.comboBufferTimer, moveId: game.player.attackMoveId };
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
    setupSky();           // 10-03 order 4: starry night dome + stars + moon
    setupHud();
    bindResTunerKeys();   // 10-03 F1/F2 pixel-fidelity keys
    showResReadout();     // visible at boot so the knob is discoverable; dims after 2.5s

    game.player = new window.WH_Player(game.scene, game.camera);
    game.player.offhandGlow = game.spellGlow;  // v7: expose glow mesh on player for debug hooks
    game.scene.add(game.player.root);
    // D3: player delegates the F-key toggle to the game's lock-on logic
    game.player.onLockToggle = toggleLockOn;

    // v7: weave HUD feedback callbacks
    game.player.onCastRefusal = function () {
      flashScreen(CFG.block.blockFlashSeconds, 'block');
    };
    game.player.onFizzle = function () {
      flashScreen(CFG.block.parryFlashSeconds, 'parry');
    };
    game.player.onSpellSelected = function (spellId) {
      var SC = CFG.spell[spellId];
      if (SC && game.spellGlow) {
        game.spellGlow.material.color.setHex(SC.schoolColor);
      }
    };
    game.player.onPotion = function () {
      flashScreen(CFG.block.blockFlashSeconds, 'block');
    };

    // v6: block/parry HUD feedback callbacks (player must exist first)
    game.player.onParry = function () {
      flashScreen(CFG.block.parryFlashSeconds, 'parry');
    };
    game.player.onBlock = function () {
      flashScreen(CFG.block.blockFlashSeconds, 'block');
    };
    game.player.onGuardBreak = function () {
      flashScreen(CFG.block.guardBreakFlashSeconds, 'guardbreak');
      var el = game.hud.guardBreakText;
      el.classList.add('visible');
      clearTimeout(game._guardBreakTimer);
      game._guardBreakTimer = setTimeout(function () {
        el.classList.remove('visible');
      }, CFG.block.guardBreakTextSeconds * 1000);
      triggerShake();   // v3 shake hook exists, spec asks for it on guard break
    };

    setupDebugHooks();

    window.WH_ASSETS.preloadAll().then(function () {
      // player body + weapon. Normalize to CFG.world.characterHeight
      // (raw Meshy characters are 2.0 tall; the pixelated variants of some
      // props differ, so normalize by measured height).
      var pBody = window.WH_ASSETS.instance('playerBody');
      var pScale = CFG.world.characterHeight /
        (window.WH_ASSETS.groundHeight('playerBody') || CFG.world.characterHeight);
      pBody.scale.setScalar(pScale);
      pBody.position.y = -(window.WH_ASSETS.groundMinY('playerBody') * pScale);
      // The animated holder owns this scaled lift; do not apply it twice.
      pBody.children[0].position.y += window.WH_ASSETS.groundMinY('playerBody');
      game.player.setBody(pBody);
      attachPlayerLantern();   // R2 P0-3: lantern now player-parented (left-hip anchor)
      // v3: register the weapon with the player so attack stages drive its
      // pose. 10-04: which weapon = CONFIG.moveset.playerWeapon.
      setupHandMeshes();    // Order B: longsword + shield meshes, mounted per hand
      setupInventory();     // 10-05 inventory Order A (+ Order B default hands)

      // initial region A
      game.regionManager = new window.WH_RegionManager(game.scene);
      game.regionManager.buildRegion(CFG.regionA.id, false);
      var region = window.WH_REGION_DEFS.regions[CFG.regionA.id];
      game.player.pos.set(region.spawn.x, 0, region.spawn.z);
      game.player.faceTowards(0, 0);     // boot spawn faces map center (Nicko 10-03)
      applyRegionLighting(CFG.regionA.id);
      showRegionName(region.name);
      // 2026-10-03: smooth fade-out of the boot overlay from CONFIG
      // (hud.bootOverlayFadeMs); .hidden also releases pointer-events, and
      // game.hud.loadNote stays in the DOM for any later reuse.
      var fadeMs = (CFG.hud && typeof CFG.hud.bootOverlayFadeMs === 'number') ?
        CFG.hud.bootOverlayFadeMs : 900;
      game.hud.loadNote.style.transition =
        'opacity ' + (fadeMs / 1000) + 's ease';
      game.hud.loadNote.classList.add('hidden');

      game.running = true;
      game.lastFrame = performance.now();
      requestAnimationFrame(loop);
    });
  }

  // R2 P1-8: light socket registry. Static sockets come from the CONFIG props
  // of the ACTIVE region only (pre-warmed groups excluded by definition);
  // firebolts contribute dynamic sockets. IO amendments: sockets derive from
  // CONFIG tables (no scene walk; region-manager.js untouched) and bolt y
  // comes from the bolt's own pos (Vector3).
  function computeSockets() {
    var out = [];
    var rm = game.regionManager;
    if (!rm) return out;
    var reg = window.WH_REGION_DEFS.regions[rm.logic.activeId];
    var props = reg && reg.cfg && reg.cfg.props ? reg.cfg.props : [];
    var S = CFG.lightSockets;
    for (var i = 0; i < props.length; i++) {
      var p = props[i];
      var sd = S[p.asset];
      if (!sd) continue;
      var h = window.WH_ASSETS.groundHeight(p.asset) * p.scale * sd.heightFraction;
      out.push({ id: p.asset + '@' + p.x + ',' + p.z, x: p.x, y: h, z: p.z,
                 intensity: sd.intensity, weight: 1 });
    }
    var bolts = game.firebolts || [];
    for (var j = 0; j < bolts.length; j++) {
      var b = bolts[j];
      if (!b || !b.alive) continue;
      out.push({ id: 'firebolt#' + j, x: b.pos.x, y: b.pos.y, z: b.pos.z,
                 intensity: 1.8, weight: 0.6 });
    }
    return out;
  }

  // R2 P0-3 (fix during validation): lantern flicker — the CONFIG band
  // (lanternFlickerPct 5) was previously unused; apply the audit's
  // deterministic two-sine wobble (no Math.random per spec) to the lantern.
  // Game-time driven via performance.now so it advances even at SwiftShader
  // low fps. Amplitude = lanternIntensity * flickerPct/100 (±0.325 @6.5).
  function lanternTick() {
    if (!game.lantern) return;
    var LT = CFG.lighting;
    var pct = LT.lanternFlickerPct !== undefined
      ? LT.lanternFlickerPct : 0;
    if (!pct) return;
    var t = performance.now() / 1000;
    var w = 0.6 * Math.sin(7.3 * t) + 0.4 * Math.sin(3.1 * t + 1.7);
    var base = LT.lanternIntensity !== undefined ? LT.lanternIntensity : 6.5;
    game.lantern.intensity = base * (1 + w * pct / 100);
  }

  // R2 P1-8: nearest-socket handoff. One pass per frame: sort sockets by
  // weighted distance to the player, take the first 4, fade each pool slot
  // toward its target (faster rate on target change = handoff).
  function poolTick(dt) {
    if (!game.lightPool) return;
    game.lightPoolT += dt;
    var sockets = computeSockets();
    game.lastSockets = sockets;
    var px = game.player ? game.player.pos.x : 0;
    var pz = game.player ? game.player.pos.z : 0;
    for (var s = 0; s < sockets.length; s++) {
      var sk = sockets[s];
      var dx = sk.x - px, dz = sk.z - pz;
      sk.d = Math.sqrt(dx * dx + dz * dz) / sk.weight;
    }
    sockets.sort(function (a, b) { return a.d - b.d; });
    var chosen = sockets.slice(0, CFG.lightPool.size);
    for (var i = 0; i < game.lightPool.length; i++) {
      var l = game.lightPool[i];
      var tgt = chosen[i];
      var want = tgt ? tgt.intensity : 0;
      var changed = (l.whSocketId || '') !== (tgt ? tgt.id : '');
      var k = 1 - Math.exp(-dt / (changed ? 0.12 : CFG.lightPool.handoffFadeSec));
      l.intensity += (want - l.intensity) * k;
      if (tgt) {
        l.position.set(tgt.x, tgt.y, tgt.z);
        l.whSocketId = tgt.id;
      }
      var card = game.flameCards[i];
      if (card) {
        var on = !!tgt && l.intensity > 0.06;
        card.visible = on;
        if (on) card.position.set(tgt.x,
          tgt.y + 0.06 * Math.sin(2.1 * game.lightPoolT + i * 1.7), tgt.z);
      }
    }
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

    // ---- v7: cast windup tick (fires the bolt at windup end) ----
    if (game.player.castWindup > 0 && game.player.state === 'alive') {
      game.player.castWindup -= dt;
      if (game.player.castWindup <= 0) {
        game.player.castWindup = 0;
        var req = game.player.completeCast();
        if (req && window.WH_SPELLS && CFG.spell[req.spellId].kind === 'followLight') {
          castRadiance(req.spellId);
        } else if (req && window.WH_SPELLS) {
          var bolt = window.WH_SPELLS.spawn(
            game.scene, req.spellId,
            { x: req.origin.x, y: 1.2, z: req.origin.z },
            req.dirX, req.dirZ);
          if (bolt) game.firebolts.push(bolt);
        }
      }
    }

    // ---- 10-04: Radiance tick. Independent of the left hand, roll, toggle,
    // and player state (keeps following through death + respawn). ----
    for (var ra = 0; ra < game.radiances.length; ra++) game.radiances[ra].update(dt);

    // 10-05: dropped item entities (spin + active-region visibility)
    game.worldItems.update(dt, rm.logic.activeId);

    // ---- v7: projectile update + collision vs enemies ----
    if (game.firebolts.length > 0) {
      var activeEnemies = rm.getEnemies(rm.logic.activeId);
      var keep = [];
      for (var fb = 0; fb < game.firebolts.length; fb++) {
        var b = game.firebolts[fb];
        if (b.alive && b.update(dt, activeEnemies)) keep.push(b);
      }
      game.firebolts = keep;
    }
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
      function (amount, attacker) { damagePlayerFromEnemy(amount, attacker); },
      rm.logic.activeId);

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
        var dmg = sweep.damage * (e.type === 'ghoul' ? sweep.ghoulMult : 1);
        // v6: riposte - staggered enemies take bonus damage, flag consumed
        if (e.riposteArmed && e.isStaggered && e.isStaggered()) {
          dmg *= CFG.block.riposteMult;
          e.riposteArmed = false;
        }
        // v3: pass hit direction (player -> enemy) for stagger knockback
        var hitDir = dist > 0.001 ? { x: dx / dist, z: dz / dist } : null;
        e.takeDamage(dmg, hitDir);
        // v7: 3rd chain strike landing (consumeAttackSweep consumed) arms
        // the armed finisher window. Use chainHits counter (robust to
        // comboIndex resets from recoverFullyElapsed). 10-04: threshold is
        // the active weapon's chainCap (longsword 3 = unchanged).
        game.player.chainHits = (game.player.chainHits || 0) + 1;
        if (game.player.chainHits >= game.player.getChainCap()) {
          game.player.armedTimer = CFG.armed.windowSeconds;
        }
        // v3 D4: shake pulse on landed melee hits, while locked-on only
        if (game.player.lockTarget) triggerShake();
      }
    }

    // Animation is presentation-only: sample the FSM after combat has consumed
    // its strike window, then advance every mixer before rendering.
    if (game.player.anim) game.player.anim.syncPlayer(game.player, dt);
    var animRegions = Object.keys(rm.enemies);
    for (var ar = 0; ar < animRegions.length; ar++) {
      var animList = rm.enemies[animRegions[ar]];
      for (var ae = 0; ae < animList.length; ae++) {
        if (animList[ae].anim) animList[ae].anim.syncEnemy(animList[ae], dt);
      }
    }

    // lock-on break conditions + reticle (D3)
    updateLockOn();

    game.player.updateCamera(dt);
    applyCameraShake(dt);
    poolTick(dt);   // R2: fixed light pool nearest-socket handoff
    lanternTick();  // R2: lantern wobble (CONFIG lanternFlickerPct)
    skyTick();      // 10-03 order 4: star twinkle clock
    updateHud(dt);
    game.renderer.render(game.scene, game.camera);
  }

  window.addEventListener('resize', function () {
    if (!game.renderer) return;
    game.camera.aspect = window.innerWidth / window.innerHeight;
    game.camera.updateProjectionMatrix();
    var isz = internalSize();   // R3 P0-4: same internal-pixel law as boot
    game.renderer.setSize(isz.w, isz.h, false);
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();