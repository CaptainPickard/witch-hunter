// Witch Hunter prototype v1 - enemies: bandit and ghoul FSMs.
// FSM: idle -> aggro -> chase -> attack -> (hurt stagger) -> death.
// Enemies are per-region instance state; they never cross region boundaries
// (hold at boundary margin). All tunables from CONFIG.

(function () {
  'use strict';

  var CFG = window.WH_CONFIG.enemy;
  var ANIM = window.WH_CONFIG.anim;

  function smooth(p) { return p * p * (3 - 2 * p); }   // smoothstep ease

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
    this.settleTime = -1;              // death settle bounce timer (-1 = off)
    this.staggerTimer = 0;             // v3 hit-stagger visual timer
    this.hopTimer = -1;                // ghoul lunge hop timer (-1 = off)
    this.hopDir = { x: 0, z: 0 };      // hop direction at takeoff
    this.hopOriginY = 0;               // root y at takeoff (for arc baseline)
    // v6: parry stagger / riposte state
    this.riposteStaggerTimer = 0;      // > 0 = staggered and vulnerable
    this.riposteArmed = false;         // next player hit does riposte damage
  }

  Enemy.prototype.setBody = function (meshRoot) {
    if (this.body) this.root.remove(this.body);
    this.body = meshRoot;
    this.bodyBaseY = meshRoot.position.y || 0;
    this.root.add(this.body);
    // v5: bandits carry a hand axe on a weapon pivot (idle pose, 1.1x scale)
    if (this.type === 'bandit' && window.WH_ASSETS &&
        window.WH_ASSETS.instance && window.WH_CONFIG.moveset) {
      var axe = window.WH_ASSETS.instance('handAxe');
      if (axe) {
        axe.scale.setScalar(0.8);
        this.weaponPivot = new THREE.Group();
        this.root.add(this.weaponPivot);
        this.weaponPivot.add(axe);
        var ip = window.WH_CONFIG.moveset.idlePose;
        this.axeIdle = { pos: [ip.pos[0] * 1.1, ip.pos[1] * 1.1, ip.pos[2] * 1.1],
                         rot: [ip.rot[0], ip.rot[1], ip.rot[2]] };
        this.weaponPivot.position.set(
          this.axeIdle.pos[0], this.axeIdle.pos[1], this.axeIdle.pos[2]);
        this.weaponPivot.rotation.set(
          this.axeIdle.rot[0], this.axeIdle.rot[1], this.axeIdle.rot[2]);
      }
    }
  };

  // FSM sense/aggression update. playerPos: THREE.Vector3, canDamagePlayer:
  // callback(amount, attacker) applies damage through the combat layer if the
  // player is vulnerable (returns true if it landed). boundary: {z, holdMargin} clamps
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
    // v6: parry stagger. Full lockdown while riposteStaggerTimer runs: no FSM
    // transitions, no movement, no attacks, no turn. Return to chase (or idle
    // if the player is far) when it expires.
    if (this.riposteStaggerTimer > 0) {
      this.riposteStaggerTimer = Math.max(0, this.riposteStaggerTimer - dt);
      if (this.riposteStaggerTimer <= 0) {
        this.setFsm(distToPlayer <= this.cfg.sightRadius ? 'chase' : 'idle');
      } else {
        // decay bob so the layered cycle does not freeze mid-pose
        this.bobPhase += dt * 3;
        return;              // frozen: no transitions, no movement, no attacks
      }
    }
    if (this.fsm === 'stagger') {
      if (this.fsmTime >= this.cfg.staggerTime) this.setFsm('chase');
    } else if (this.fsm === 'attack') {
      this.attackTimer -= dt;
      if (distToPlayer > this.cfg.attackRange * 1.4) {
        this.setFsm('chase');
      } else if (this.attackTimer <= 0 && playerAlive) {
        canDamagePlayer(this.cfg.attackDamage, this);
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
        // v3: ghoul telegraphs the strike with a short forward hop
        if (this.type === 'ghoul' && ANIM.ghoulHop.duration > 0) {
          this.hopTimer = 0;
          this.hopDir = distToPlayer > 0.001
            ? { x: toPlayerX / distToPlayer, z: toPlayerZ / distToPlayer }
            : { x: 0, z: 0 };
        }
        this.setFsm('attack');
        this.attackTimer = 0;
      }
    }

    // v3: hit-stagger visual timer runs down regardless of FSM
    if (this.staggerTimer > 0) this.staggerTimer = Math.max(0, this.staggerTimer - dt);

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
    } else {
      // decay toward 0 so the layered cycle does not freeze mid-pose
      this.bobPhase += dt * 3;
    }

    // v3: ghoul lunge hop progress (0.25 over 0.25s, fired at chase->attack)
    if (this.hopTimer >= 0) {
      this.hopTimer += dt;
      if (this.hopTimer >= ANIM.ghoulHop.duration) {
        this.hopTimer = -1;
      } else {
        // horizontal drift along takeoff direction
        var hopSpeed = ANIM.ghoulHop.height * 1.6 / ANIM.ghoulHop.duration; // ~reach
        this.pos.x += this.hopDir.x * hopSpeed * dt;
        this.pos.z += this.hopDir.z * hopSpeed * dt;
      }
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
        if (this.settleTime < 0 && this.deadFall >= 1) {
          this.settleTime = 0;           // fall finished: start settle bounce
        }
        if (this.settleTime < 0) {
          this.deadFall = Math.min(1, this.deadFall + dt * 2.5);
          this.body.rotation.x = -this.deadFall * Math.PI / 2;
          this.root.position.y = -this.deadFall * 0.3;
        } else {
          // v3: settle bounce - overshoot above final sink, then settle
          this.settleTime += dt;
          var sp = Math.min(1, this.settleTime / ANIM.death.settleDuration);
          var decay = Math.exp(-sp * 5);
          var bounce = Math.sin(sp * Math.PI * 2) * ANIM.death.settleOvershoot * decay;
          this.body.rotation.x = -Math.PI / 2;
          this.root.position.y = -0.3 + bounce;
        }
      } else {
        // v3 D3: layered walk cycle with per-type amplitude multipliers
        var mult = ANIM.enemyWalk[this.type] ||
                   { bob: 1, sway: 1, lean: 1, yawOsc: 1 };
        var movingNow = moveSpeed > 0;
        var eBob = Math.abs(Math.sin(this.bobPhase)) * 0.09 * mult.bob;
        eBob += Math.abs(Math.sin(this.bobPhase * 2)) * 0.04 * mult.bob;
        var eSway = movingNow ? Math.sin(this.bobPhase * 0.5) * 0.05 * mult.sway : 0;
        var eRoll = movingNow ? Math.sin(this.bobPhase * 0.5) * -0.05 * mult.sway : 0;
        var eYawOsc = movingNow ? Math.sin(this.bobPhase) * 0.06 * mult.yawOsc : 0;
        var eLean = 0;
        if (movingNow) {
          eLean = (moveSpeed > this.cfg.moveSpeed ? 0.16 : 0.08) * mult.lean;
        }
        // ghoul hop arc: parabolic root y above ground baseline
        var hopY = 0;
        if (this.hopTimer >= 0) {
          var hp = this.hopTimer / ANIM.ghoulHop.duration;
          hopY = 4 * hp * (1 - hp) * ANIM.ghoulHop.height;
        }
        // hit stagger: lean-back + slight crouch while staggerTimer is active
        var stagT = this.staggerTimer > 0
          ? this.staggerTimer / ANIM.stagger.visualDuration : 0;
        var stagLean = stagT > 0 ? ANIM.stagger.leanBack * stagT : 0;
        this.root.position.y = hopY + eBob * 0.4;
        this.body.rotation.x = eLean + stagLean;
        this.body.rotation.z = eRoll;
        this.body.position.x = eSway;
        this.body.rotation.y = this.yaw + eYawOsc;
        if (stagT > 0) {
          // crouch dip proportional to stagger intensity
          this.body.position.y = (this.bodyBaseY || 0) - 0.06 * stagT;
        } else {
          this.body.position.y = this.bodyBaseY || 0;
        }
        // v5: bandit axe swing. attackTimer counts down the cooldown; sweep
        // rotation.y 90deg early in the cooldown window (the strike window).
        if (this.weaponPivot && this.axeIdle) {
          if (this.fsm === 'attack' && this.attackTimer > 0 &&
              this.attackTimer <= this.cfg.attackCooldown) {
            var cd = this.cfg.attackCooldown || 1;
            var swingT = 1 - this.attackTimer / cd;        // 0..1 since strike
            var sw = Math.min(1, swingT / 0.4);            // 90deg sweep in first 40%
            var back = smooth(Math.min(1, Math.max(0, (swingT - 0.4) / 0.6)));
            this.weaponPivot.rotation.y = this.axeIdle.rot[1] -
              (Math.PI / 2) * sw + (Math.PI / 2) * back;
          } else {
            this.weaponPivot.rotation.y = this.axeIdle.rot[1];
          }
        }
      }
    }
  };

  Enemy.prototype.setFsm = function (next) {
    if (this.fsm === next) return;
    this.fsm = next;
    this.fsmTime = 0;
  };

  // v6: parry stagger. Cancels the current attack state entirely (bandit and
  // ghoul share this base class), locks the enemy in place for the duration,
  // and arms the riposte flag on the next player hit.
  Enemy.prototype.enterStagger = function (duration) {
    this.riposteStaggerTimer = duration;
    this.riposteArmed = true;
    this.hopTimer = -1;                  // cancel any mid-hop lunge
    this.setFsm('stagger');
  };

  Enemy.prototype.isStaggered = function () {
    return this.riposteStaggerTimer > 0;
  };

  Enemy.prototype.takeDamage = function (amount, fromDir) {
    if (this.fsm === 'dead') return false;
    this.hp -= amount;
    if (this.hp <= 0) {
      this.hp = 0;
      this.setFsm('dead');
      return true;
    }
    // v3: hit stagger visual (0.15s lean-back + knockback)
    this.staggerTimer = ANIM.stagger.visualDuration;
    if (ANIM.stagger.knockback > 0 && fromDir) {
      var kLen = Math.sqrt(fromDir.x * fromDir.x + fromDir.z * fromDir.z);
      if (kLen > 0.001) {
        var kPush = ANIM.stagger.knockback * ANIM.stagger.visualDuration;
        this.pos.x += (fromDir.x / kLen) * kPush;
        this.pos.z += (fromDir.z / kLen) * kPush;
      }
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