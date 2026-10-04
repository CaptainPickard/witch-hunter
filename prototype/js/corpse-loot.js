// Witch Hunter prototype - corpse loot container (Order S4, 2026-10-05).
// A kill's CONFIG.drops roll is stored on the body as enemy.corpseLoot =
// [{ id, count }]; game.js interact() loots it (box pickup > corpse > node).
// While the list is non-empty the corpse shows a soft additive gold glow
// (camera billboard + flat ground pool) and a recycled pool of unlit sparks
// rising off it; an emptied corpse fades the effect out and is plain forever.
// NO PointLights - the light budget is fixed (CONFIG.corpseLoot comment).
// Effects live in the scene (not the region group) and are disposed here as
// soon as their enemy leaves the region manager's lists (region rebuild /
// unload): the unlooted loot vanishes with the corpse (playtest rule).
// Exposes window.WH_CORPSE_LOOT = { Manager }.

(function () {
  'use strict';

  var CFG = window.WH_CONFIG;
  var C = CFG.corpseLoot;

  // Soft radial falloff, shared by every glow / spark (never disposed).
  function radialTexture(size, stops) {
    var cv = document.createElement('canvas');
    cv.width = cv.height = size;
    var g = cv.getContext('2d');
    var grad = g.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
    for (var i = 0; i < stops.length; i++) grad.addColorStop(stops[i][0], stops[i][1]);
    g.fillStyle = grad;
    g.fillRect(0, 0, size, size);
    var tex = new THREE.CanvasTexture(cv);
    tex.colorSpace = THREE.SRGBColorSpace;
    return tex;
  }

  // getRegionManager: fn() -> WH_RegionManager (built after the inventory)
  function Manager(scene, getRegionManager) {
    this.scene = scene;
    this.getRM = getRegionManager;
    this.fx = [];                     // one record per corpse with a live effect
    this.clock = 0;
    this.glowTex = radialTexture(128, [[0, 'rgba(255,255,255,1)'], [0.25, 'rgba(255,255,255,0.55)'],
                                       [0.6, 'rgba(255,255,255,0.12)'], [1, 'rgba(255,255,255,0)']]);
    this.sparkTex = radialTexture(32, [[0, 'rgba(255,255,255,1)'], [0.4, 'rgba(255,255,255,0.6)'],
                                       [1, 'rgba(255,255,255,0)']]);
    this.groundGeo = new THREE.CircleGeometry(1, 24);
    this.groundGeo.rotateX(-Math.PI / 2);
  }

  // Kill: store the rolled items on the body and start its effect.
  Manager.prototype.attach = function (enemy, items) {
    enemy.corpseLoot = items.slice();
    if (!items.length) return;
    var S = C.sparks;
    var glowMat = new THREE.SpriteMaterial({
      map: this.glowTex, color: C.glowColor, transparent: true, opacity: 0,
      blending: THREE.AdditiveBlending, depthWrite: false
    });
    var glow = new THREE.Sprite(glowMat);
    glow.scale.setScalar(C.glowScale);
    var ground = null;
    if (C.groundGlow.opacity > 0) {
      ground = new THREE.Mesh(this.groundGeo, new THREE.MeshBasicMaterial({
        map: this.glowTex, color: C.glowColor, transparent: true, opacity: 0,
        blending: THREE.AdditiveBlending, depthWrite: false,
        polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2
      }));
      ground.scale.setScalar(C.groundGlow.radius);
    }
    // sparks: world-space positions, per-spark brightness baked into the
    // vertex colour (additive: black = invisible), so no per-frame allocation
    var geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(S.count * 3), 3));
    geo.setAttribute('color', new THREE.BufferAttribute(new Float32Array(S.count * 3), 3));
    var points = new THREE.Points(geo, new THREE.PointsMaterial({
      map: this.sparkTex, size: S.size, sizeAttenuation: true, vertexColors: true,
      transparent: true, blending: THREE.AdditiveBlending, depthWrite: false
    }));
    points.frustumCulled = false;     // positions move every frame
    var rec = {
      enemy: enemy, glow: glow, ground: ground, points: points,
      state: 'delay', t: 0, alpha: 0, center: null,
      phase: Math.random() * Math.PI * 2,
      sparks: [], sparkColor: new THREE.Color(S.color)
    };
    for (var i = 0; i < S.count; i++) {
      rec.sparks.push({ x: 0, y: 0, z: 0, vx: 0, vz: 0, age: 0, life: 1, sway: 0 });
    }
    glow.visible = points.visible = false;
    if (ground) ground.visible = false;
    this.scene.add(glow);
    this.scene.add(points);
    if (ground) this.scene.add(ground);
    this.fx.push(rec);
  };

  function respawnSpark(sp, c, stagger) {
    var S = C.sparks;
    var a = Math.random() * Math.PI * 2;
    var r = S.spawnRadius * Math.sqrt(Math.random());
    sp.x = c.x + Math.sin(a) * r;
    sp.z = c.z + Math.cos(a) * r;
    sp.y = c.y + Math.random() * 0.1;
    sp.vx = (Math.random() * 2 - 1) * S.drift;
    sp.vz = (Math.random() * 2 - 1) * S.drift;
    sp.sway = Math.random() * Math.PI * 2;
    sp.life = S.lifetimeSec * (1 + (Math.random() * 2 - 1) * S.lifetimeJitter);
    // first fill: spread ages so the column is already populated
    sp.age = stagger ? Math.random() * sp.life : 0;
    sp.y += sp.age * S.riseSpeed;
  }

  Manager.prototype.dispose = function (rec) {
    this.scene.remove(rec.glow);
    this.scene.remove(rec.points);
    rec.glow.material.dispose();
    rec.points.geometry.dispose();
    rec.points.material.dispose();
    if (rec.ground) {
      this.scene.remove(rec.ground);
      rec.ground.material.dispose();
    }
  };

  Manager.prototype.isAlive = function (enemy) {
    var list = this.getRM().enemies[enemy.homeRegionId];
    return !!list && list.indexOf(enemy) >= 0;
  };

  Manager.prototype.update = function (dt, activeId) {
    this.clock += dt;
    var S = C.sparks;
    for (var i = this.fx.length - 1; i >= 0; i--) {
      var rec = this.fx[i];
      var e = rec.enemy;
      // corpse gone (region rebuilt / unloaded): its loot goes with it
      if (!this.isAlive(e)) {
        e.corpseLoot = null;
        this.dispose(rec);
        this.fx.splice(i, 1);
        continue;
      }
      rec.t += dt;
      if (rec.state === 'delay') {
        // wait out appearDelaySec AND the death settle, then measure the
        // body's centre once (the fall direction moves the torso off root)
        if (rec.t < C.appearDelaySec || e.corpseFinalY === null) continue;
        e.root.updateMatrixWorld(true);
        rec.center = new THREE.Box3().setFromObject(e.root).getCenter(new THREE.Vector3());
        rec.center.y = Math.max(0.05, Math.min(rec.center.y, 0.6));
        rec.glow.position.set(rec.center.x, C.glowHeight, rec.center.z);
        if (rec.ground) rec.ground.position.set(rec.center.x, 0.03, rec.center.z);
        for (var k = 0; k < rec.sparks.length; k++) respawnSpark(rec.sparks[k], rec.center, true);
        rec.state = 'live';
        rec.t = 0;
      }
      if (rec.state === 'live') {
        rec.alpha = Math.min(1, rec.t / C.fadeInSec);
      } else {                        // 'fading' (looted empty)
        rec.alpha = Math.max(0, 1 - rec.t / C.fadeOutSec);
        if (rec.alpha <= 0) {
          this.dispose(rec);
          this.fx.splice(i, 1);
          continue;
        }
      }
      var vis = e.homeRegionId === activeId;
      rec.glow.visible = rec.points.visible = vis;
      if (rec.ground) rec.ground.visible = vis;
      if (!vis) continue;

      var breath = 0.5 + 0.5 * Math.sin(2 * Math.PI * this.clock / C.glowPulseSec + rec.phase);
      var pulse = C.glowPulseMin + (1 - C.glowPulseMin) * breath;
      rec.glow.material.opacity = C.glowOpacity * pulse * rec.alpha;
      rec.glow.scale.setScalar(C.glowScale * (0.92 + 0.08 * breath));
      if (rec.ground) rec.ground.material.opacity = C.groundGlow.opacity * pulse * rec.alpha;

      var pos = rec.points.geometry.attributes.position;
      var col = rec.points.geometry.attributes.color;
      var pa = pos.array, ca = col.array, sc = rec.sparkColor;
      for (var j = 0; j < rec.sparks.length; j++) {
        var sp = rec.sparks[j];
        sp.age += dt;
        if (sp.age >= sp.life) {
          if (rec.state === 'live') respawnSpark(sp, rec.center, false);
          else sp.age = sp.life;      // fading: no new sparks
        }
        sp.sway += dt * 2.1;
        sp.x += (sp.vx + Math.sin(sp.sway) * S.drift * 0.5) * dt;
        sp.z += (sp.vz + Math.cos(sp.sway * 0.8) * S.drift * 0.5) * dt;
        sp.y += S.riseSpeed * dt;
        // fade in at the body, out at the top
        var b = Math.sin(Math.PI * Math.min(1, sp.age / sp.life)) * rec.alpha;
        pa[j * 3] = sp.x; pa[j * 3 + 1] = sp.y; pa[j * 3 + 2] = sp.z;
        ca[j * 3] = sc.r * b; ca[j * 3 + 1] = sc.g * b; ca[j * 3 + 2] = sc.b * b;
      }
      pos.needsUpdate = true;
      col.needsUpdate = true;
    }
  };

  function hasLoot(e) {
    return e.fsm === 'dead' && !!e.corpseLoot && e.corpseLoot.length > 0;
  }

  // Corpse centre for reach checks: measured centre once settled, else x/z.
  Manager.prototype.centerOf = function (e) {
    for (var i = 0; i < this.fx.length; i++) {
      if (this.fx[i].enemy === e && this.fx[i].center) return this.fx[i].center;
    }
    return e.pos;
  };

  // Nearest unlooted corpse in the active region within radius, or null.
  Manager.prototype.nearest = function (x, z, radius, activeId) {
    var list = this.getRM().enemies[activeId] || [];
    var best = null, bestD2 = radius * radius;
    for (var i = 0; i < list.length; i++) {
      var e = list[i];
      if (!hasLoot(e)) continue;
      var c = this.centerOf(e);
      var dx = c.x - x, dz = c.z - z, d2 = dx * dx + dz * dz;
      if (d2 <= bestD2) { best = e; bestD2 = d2; }
    }
    return best;
  };

  // Move every entry that fits into inv (stack-join via addItem); the rest
  // stays on the body. Returns { taken: [{ id, count }], remaining: n }.
  // An emptied corpse starts its fade-out and is skipped forever after.
  Manager.prototype.loot = function (enemy, inv) {
    var taken = [];
    var keep = [];
    for (var i = 0; i < enemy.corpseLoot.length; i++) {
      var it = enemy.corpseLoot[i];
      var added = inv.addItem(it.id, it.count);
      if (added > 0) taken.push({ id: it.id, count: added });
      if (it.count - added > 0) keep.push({ id: it.id, count: it.count - added });
    }
    enemy.corpseLoot = keep;
    if (!keep.length) {
      for (var k = 0; k < this.fx.length; k++) {
        var rec = this.fx[k];
        if (rec.enemy !== enemy || rec.state === 'fading') continue;
        // fade from wherever the fade-in got to; looted before it ever
        // showed ('delay', no centre) = dispose on the next update
        rec.t = rec.center ? (1 - rec.alpha) * C.fadeOutSec : C.fadeOutSec;
        rec.state = 'fading';
      }
    }
    return { taken: taken, remaining: keep.length };
  };

  window.WH_CORPSE_LOOT = { Manager: Manager };
})();
