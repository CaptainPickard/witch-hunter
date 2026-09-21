// Witch Hunter prototype v1 - enemies: bandit and ghoul FSMs.
// FSM: idle -> aggro -> chase -> attack -> (hurt stagger) -> death.
// Enemies are per-region instance state; they never cross region boundaries
// (hold at boundary margin). All tunables from CONFIG.

(function () {
  'use strict';

  var CFG = window.WH_CONFIG.enemy;

  function cfgFor(type) {
    return CFG[type] || CFG.bandit;
  }

  function Enemy(type, scene, homeRegionId, spawnX, spawnZ) {
    this.type = type;
    this.cfg = cfgFor(type);
    this.homeRegionId = homeRegionId;
    this.spawn = { x: spawnX, z: spawnZ };
    this.hp = this.cfg.hpMax;
    this.hpMax = this.cfg.hpMax;
    this.fsm = 'idle';                 // idle | aggro | chase | attack | stagger | dead
    this.fsmTime = 0;
    this.attackTimer = 0;              // cooldown remaining
    this.pos = new THREE.Vector3(spawnX, 0, spawnZ);
    this.yaw = Math.random() * Math.PI * 2;
    this.bobPhase = Math.random() * Math.PI * 2;
    this.root = new THREE.Group();
    this.body = null;
    this.deadFall = 0;                 // death fall-over progress
  }

  Enemy.prototype.setBody = function (meshRoot) {
    if (this.body) this.root.remove(this.body);
    this.body = meshRoot;
    this.root.add(this.body);
  };

  // FSM sense/aggression update. playerPos: THREE.Vector3, canDamagePlayer:
  // callback(amount) applies damage through the combat layer if player is
  // vulnerable (returns true if it landed). boundary: {z, holdMargin} clamps
  // movement to home side.
  Enemy.prototype.update = function (dt, playerPos, playerAlive, canDamagePlayer, boundary, regionManager) {
    if (this.fsm === 'dead') return;
    this.fsmTime += dt;

    var toPlayerX = playerPos.x - this.pos.x;
    var toPlayerZ = playerPos.z - this.pos.z;
    var distToPlayer = Math.sqrt(toPlayerX * toPlayerX + toPlayerZ * toPlayerZ);
    var distToSpawn = Math.sqrt(
      (this.pos.x - this.spawn.x) * (this.pos.x - this.spawn.x) +
      (this.pos.z - this.spawn.z) * (this.pos.z - this.spawn.z)
    );

    // ---- transitions ----
    if (this.fsm === 'stagger') {
      if (this.fsmTime >= this.cfg.staggerTime) this.setFsm('chase');
    } else if (this.fsm === 'attack') {
      this.attackTimer -= dt;
      if (distToPlayer > this.cfg.attackRange * 1.4) {
        this.setFsm('chase');
      } else if (this.attackTimer <= 0 && playerAlive) {
        canDamagePlayer(this.cfg.attackDamage);
        this.attackTimer = this.cfg.attackCooldown;
      }
      if (!playerAlive) this.setFsm('idle');
    } else if (this.fsm === 'idle' || this.fsm === 'aggro') {
      if (playerAlive && distToPlayer <= this.cfg.sightRadius) {
        this.setFsm(this.fsm === 'idle' ? 'aggro' : 'aggro');
      } else if (distToSpawn > this.cfg.leashRadius) {
        // will walk home below
      }
      if (playerAlive && distToPlayer <= this.cfg.sightRadius * 0.8) {
        this.setFsm('chase');
      }
    } else if (this.fsm === 'chase') {
      if (!playerAlive || distToPlayer > this.cfg.leashRadius || distToSpawn > this.cfg.leashRadius) {
        this.setFsm('idle');           // leash: disengage, walk home
      } else if (distToPlayer <= this.cfg.attackRange) {
        this.setFsm('attack');
        this.attackTimer = 0;
      }
    }

    // ---- movement per state ----
    var moveSpeed = 0;
    var dirX = 0, dirZ = 0;

    if (this.fsm === 'chase') {
      moveSpeed = this.cfg.chaseSpeed;
      if (distToPlayer > 0.001) {
        dirX = toPlayerX / distToPlayer;
        dirZ = toPlayerZ / distToPlayer;
      }
    } else if (this.fsm === 'idle' || this.fsm === 'aggro') {
      if (distToSpawn > 0.5) {
        moveSpeed = this.cfg.moveSpeed;
        dirX = (this.spawn.x - this.pos.x) / distToSpawn;
        dirZ = (this.spawn.z - this.pos.z) / distToSpawn;
      }
    } else if (this.fsm === 'attack') {
      // stand ground, face player
      moveSpeed = 0;
    }

    if (moveSpeed > 0) {
      this.pos.x += dirX * moveSpeed * dt;
      this.pos.z += dirZ * moveSpeed * dt;
      this.yaw = Math.atan2(dirX, dirZ);
      this.bobPhase += dt * (moveSpeed > this.cfg.moveSpeed ? 11 : 7);
    }

    // ---- boundary hold: enemies never cross into the other region ----
    if (boundary && regionManager) {
      regionManager.clampEnemyToHomeSide(this, boundary);
    }

    // ---- visual ----
    if (this.body) {
      this.root.position.copy(this.pos);
      this.body.rotation.y = this.yaw;
      if (this.fsm === 'dead') {
        this.deadFall = Math.min(1, this.deadFall + dt * 2.5);
        this.body.rotation.x = -this.deadFall * Math.PI / 2;
        this.root.position.y = -this.deadFall * 0.3;
      } else {
        this.root.position.y = Math.abs(Math.sin(this.bobPhase)) * 0.08;
      }
    }
  };

  Enemy.prototype.setFsm = function (next) {
    if (this.fsm === next) return;
    this.fsm = next;
    this.fsmTime = 0;
  };

  Enemy.prototype.takeDamage = function (amount) {
    if (this.fsm === 'dead') return false;
    this.hp -= amount;
    if (this.hp <= 0) {
      this.hp = 0;
      this.setFsm('dead');
      return true;
    }
    this.setFsm('stagger');
    return false;
  };

  // Circle push-out against a list of other circles (enemies + player).
  // others: [{pos: THREE.Vector3, radius: number}]
  Enemy.prototype.separateFrom = function (others, strength, dt) {
    for (var i = 0; i < others.length; i++) {
      var o = others[i];
      var dx = this.pos.x - o.pos.x;
      var dz = this.pos.z - o.pos.z;
      var minDist = this.cfg.radius + o.radius;
      var d2 = dx * dx + dz * dz;
      if (d2 >= minDist * minDist || d2 === 0) continue;
      var d = Math.sqrt(d2);
      var push = (minDist - d) * strength * dt;
      this.pos.x += (dx / d) * push;
      this.pos.z += (dz / d) * push;
      if (o.pushedBy !== undefined) {
        o.pos.x -= (dx / d) * push * 0.5;
        o.pos.z -= (dz / d) * push * 0.5;
      }
    }
  };

  window.WH_Enemy = Enemy;
  window.WH_ENEMY_TYPES = ['bandit', 'ghoul'];
})();