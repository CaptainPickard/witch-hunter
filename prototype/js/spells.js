// Witch Hunter prototype v7 "Weave Slice" - spell registry + projectiles.
// window.WH_SPELLS: registry of bound spells (ONE spell in this slice:
// Firebolt) plus the Firebolt projectile class. IIFE + window globals,
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

  // ---- registry --------------------------------------------------------------

  window.WH_SPELLS = {
    Firebolt: Firebolt,
    // Spawn helper: returns the new bolt or null if the spell id is unknown.
    spawn: function (scene, spellId, origin, dirX, dirZ) {
      if (!SPELLS[spellId]) return null;
      return new Firebolt(scene, spellId, origin, dirX, dirZ);
    },
    getSpellConfig: function (spellId) { return SPELLS[spellId] || null; }
  };
})();