// Witch Hunter prototype v7 "Weave Slice" - spell registry + projectiles.
// window.WH_SPELLS: registry of bound spells (Firebolt projectile; 10-04
// Radiance follow-light) plus their classes. IIFE + window globals,
// no ES modules, no class syntax (prototype convention). All numbers
// from CONFIG. Firebolt damage routes through the existing enemy
// takeDamage (no stagger from spells in this slice).

(function () {
  'use strict';

  var SPELLS = window.WH_CONFIG.spell;

  // ---- Firebolt projectile ---------------------------------------------------

  // Simple straight-flying bolt with a range-limited lifetime. Collision is
  // a 2D circle test vs enemy positions (enemy.pos, radius from CONFIG).
  // Calls enemy.takeDamage ONCE on hit, then dies.
  function Firebolt(scene, spellId, origin, dirX, dirZ) {
    var S = SPELLS[spellId];
    this.spellId = spellId;
    this.config = S;
    this.pos = new THREE.Vector3(origin.x, origin.y, origin.z);
    this.dirX = dirX;
    this.dirZ = dirZ;
    this.speed = S.speed;
    this.hitRadius = S.hitRadius;
    this.maxRange = S.maxRange;
    this.damage = S.damage;
    this.traveled = 0;
    this.alive = true;

    // small emissive sphere (school-colored) as the bolt body
    this.mesh = new THREE.Mesh(
      new THREE.SphereGeometry(0.18, 8, 6),
      new THREE.MeshBasicMaterial({ color: S.schoolColor })
    );
    this.mesh.position.copy(this.pos);
    scene.add(this.mesh);
    this.scene = scene;
  }

  // update(dt, enemies): advance, lifetime-check, collide vs enemy circles.
  Firebolt.prototype.update = function (dt, enemies) {
    if (!this.alive) return false;
    // v7: hit flash countdown -> die when expired
    if (this.spent) {
      this.hitFlash -= dt;
      if (this.hitFlash <= 0) { this.die(); return false; }
      return true;     // still alive during flash, no more movement/collision
    }
    var step = this.speed * dt;
    this.pos.x += this.dirX * step;
    this.pos.z += this.dirZ * step;
    this.traveled += step;
    this.mesh.position.copy(this.pos);
    if (this.traveled >= this.maxRange) {
      this.die();
      return false;
    }
    if (enemies) {
      for (var i = 0; i < enemies.length; i++) {
        var e = enemies[i];
        if (e.fsm === 'dead') continue;
        var dx = e.pos.x - this.pos.x;
        var dz = e.pos.z - this.pos.z;
        var rr = this.hitRadius + (e.cfg ? e.cfg.radius : 0.7);
        if (dx * dx + dz * dz <= rr * rr) {
          var fromDir = { x: this.dirX, z: this.dirZ };
          e.takeDamage(this.damage, fromDir);
          this.spent = true;           // v7: can't damage again
          this.hitFlash = 0.15;        // brief alive period for visual + debug visibility
          return true;                  // keep ticking (alive) during flash
        }
      }
    }
    return true;    // still flying
  };

  Firebolt.prototype.die = function () {
    this.alive = false;
    if (this.mesh) {
      this.scene.remove(this.mesh);
      this.mesh = null;
    }
  };

  // ---- Radiance follow-light (10-04, Nicko) ---------------------------------

  // Emissive orb + its OWN PointLight (never the prop light pool), parented
  // to the player's yawFrame so it follows without per-frame world math.
  // Lifetime is independent of the left hand: only timer expiry ends it.
  // A recast calls refresh() on the same effect (never a second light).
  // Expiry fades out, then PARKS the effect (orb hidden, light at 0) rather
  // than removing the light: a scene light-count change recompiles every lit
  // material, so the one dedicated light stays and the next cast reuses it.
  function RadianceEffect(scene, spellId) {
    var S = SPELLS[spellId];
    this.spellId = spellId;
    this.config = S;
    this.scene = scene;
    this.group = new THREE.Group();
    this.orb = new THREE.Mesh(
      new THREE.SphereGeometry(S.orbRadius, S.orbSegments[0], S.orbSegments[1]),
      new THREE.MeshBasicMaterial({ color: S.glowColor, transparent: true, opacity: 0 })
    );
    this.light = new THREE.PointLight(S.lightColor, 0, S.lightDistance, S.lightDecay);
    this.group.add(this.orb);
    this.group.add(this.light);
    scene.add(this.group);            // until attach() re-parents it
    this.active = false;
    this.remaining = 0;
    this.envelope = 0;                // 0..1 fade-in level
    this.bobPhase = 0;
    this.refresh();
  }

  // Cast / recast: full duration again, fade back up from the current level.
  RadianceEffect.prototype.refresh = function () {
    if (!this.active) this.envelope = 0;
    this.active = true;
    this.remaining = this.config.durationSeconds;
    this.orb.visible = true;
  };

  // Follow anchor = the player's yawFrame (pattern of the deleted R2 lantern).
  RadianceEffect.prototype.attach = function (player) {
    if (!player || !player.yawFrame) return;
    if (this.group.parent !== player.yawFrame) player.yawFrame.add(this.group);
    var off = this.config.anchorOffset;
    this.group.position.set(off[0], off[1], off[2]);
  };

  // Returns true while lit.
  RadianceEffect.prototype.update = function (dt) {
    if (!this.active) return false;
    var S = this.config;
    this.remaining = Math.max(0, this.remaining - dt);
    this.envelope = Math.min(1, this.envelope + dt / S.fadeInSeconds);
    var level = this.envelope * Math.min(1, this.remaining / S.fadeOutSeconds);
    this.bobPhase += dt * Math.PI * 2 * S.bobHz;
    var bob = Math.sin(this.bobPhase) * S.bobAmp;
    this.orb.position.y = bob;
    this.light.position.y = bob;
    this.orb.material.opacity = level;
    this.light.intensity = S.lightIntensity * level;
    if (this.remaining <= 0) {
      this.park();
      return false;
    }
    return true;
  };

  RadianceEffect.prototype.park = function () {
    this.active = false;
    this.remaining = 0;
    this.envelope = 0;
    this.orb.visible = false;
    this.light.intensity = 0;
  };

  // ---- registry --------------------------------------------------------------

  window.WH_SPELLS = {
    Firebolt: Firebolt,
    RadianceEffect: RadianceEffect,
    // Spawn helper: CONFIG kind 'followLight' -> RadianceEffect handle,
    // anything else -> Firebolt. null if the spell id is unknown.
    spawn: function (scene, spellId, origin, dirX, dirZ) {
      if (!SPELLS[spellId]) return null;
      if (SPELLS[spellId].kind === 'followLight') return new RadianceEffect(scene, spellId);
      return new Firebolt(scene, spellId, origin, dirX, dirZ);
    },
    getSpellConfig: function (spellId) { return SPELLS[spellId] || null; }
  };
})();