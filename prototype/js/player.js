// Witch Hunter prototype v1 - third-person player controller.
// Transform-only procedural animation (assets are unrigged): walk bob, attack
// swing rotation, roll tumble. All tunables from CONFIG.

(function () {
  'use strict';

  var CFG = window.WH_CONFIG.player;

  function deg2rad(d) { return d * Math.PI / 180; }

  function Player(scene, camera) {
    this.scene = scene;
    this.camera = camera;

    // state
    this.hp = CFG.hpMax;
    this.hpMax = CFG.hpMax;
    this.stamina = CFG.staminaMax;
    this.staminaMax = CFG.staminaMax;
    this.staminaRegenBlock = 0;       // seconds until regen resumes
    this.iframes = 0;                 // seconds of i-frames remaining
    this.state = 'alive';             // alive | dying | dead
    this.stateTime = 0;
    this.pos = new THREE.Vector3(0, 0, 0);
    this.velY = 0;
    this.yaw = 0;                     // body facing (radians)
    this.moveInput = { x: 0, z: 0 };  // camera-relative, set by game input
    this.sprinting = false;
    this.rolling = false;
    this.rollTimer = 0;
    this.rollDir = new THREE.Vector3(0, 0, 1);
    this.attacking = false;
    this.attackTimer = 0;
    this.attackDidHit = false;
    this.bobPhase = 0;

    // camera orbit state
    this.camYaw = Math.PI;            // looking toward -z (into region A)
    this.camPitch = deg2rad(22);
    this.camDist = CFG.camDistance;
    this.dragging = false;
    this.lastDragX = 0;
    this.lastDragY = 0;

    // visual root (body added by game after assets load)
    this.root = new THREE.Group();
    this.body = null;
    this.deathTilt = 0;

    this.bindInput();
  }

  Player.prototype.setBody = function (meshRoot) {
    if (this.body) this.root.remove(this.body);
    this.body = meshRoot;
    this.root.add(this.body);
  };

  Player.prototype.bindInput = function () {
    var self = this;
    this.keys = {};
    document.addEventListener('keydown', function (e) {
      self.keys[e.code] = true;
      if (e.code === 'Space') {
        e.preventDefault();
        self.tryRoll();
      }
    });
    document.addEventListener('keyup', function (e) {
      self.keys[e.code] = false;
    });
    document.addEventListener('mousedown', function (e) {
      if (e.button === 0) {
        self.tryAttack();
        self.dragging = true;
        self.lastDragX = e.clientX;
        self.lastDragY = e.clientY;
      }
    });
    document.addEventListener('mouseup', function (e) {
      if (e.button === 0) self.dragging = false;
    });
    document.addEventListener('mousemove', function (e) {
      if (!self.dragging) return;
      var dx = e.clientX - self.lastDragX;
      var dy = e.clientY - self.lastDragY;
      self.lastDragX = e.clientX;
      self.lastDragY = e.clientY;
      self.camYaw -= dx * deg2rad(CFG.mouseSensDegPerPx);
      self.camPitch += dy * deg2rad(CFG.mouseSensDegPerPx);
      self.camPitch = Math.max(deg2rad(CFG.camPitchMinDeg), Math.min(deg2rad(CFG.camPitchMaxDeg), self.camPitch));
    });
    document.addEventListener('wheel', function (e) {
      self.camDist += (e.deltaY > 0 ? 1 : -1) * 0.8;
      self.camDist = Math.max(CFG.camMinDistance, Math.min(CFG.camMaxDistance, self.camDist));
    }, { passive: true });
  };

  Player.prototype.collectMoveInput = function () {
    var k = this.keys;
    var ix = 0, iz = 0;
    if (k['KeyW']) iz -= 1;
    if (k['KeyS']) iz += 1;
    if (k['KeyA']) ix -= 1;
    if (k['KeyD']) ix += 1;
    this.moveInput.x = ix;
    this.moveInput.z = iz;
    this.sprinting = !!(k['ShiftLeft'] || k['ShiftRight']);
  };

  Player.prototype.tryRoll = function () {
    if (this.state !== 'alive' || this.rolling || this.attacking) return;
    if (this.stamina < CFG.rollStaminaCost) return;
    this.spendStamina(CFG.rollStaminaCost);
    this.rolling = true;
    this.rollTimer = CFG.rollDuration;
    this.iframes = CFG.rollIFrameWindow;
    // roll direction: current move input direction, or facing if idle
    var dir = new THREE.Vector3(this.moveInput.x, 0, this.moveInput.z);
    if (dir.lengthSq() < 0.01) {
      dir.set(Math.sin(this.yaw), 0, Math.cos(this.yaw));
    }
    dir.normalize();
    this.rollDir.copy(dir);
  };

  Player.prototype.tryAttack = function () {
    if (this.state !== 'alive' || this.rolling || this.attacking) return;
    if (this.stamina < CFG.attackStaminaCost) return;
    this.spendStamina(CFG.attackStaminaCost);
    this.attacking = true;
    this.attackTimer = CFG.attackDuration;
    this.attackDidHit = false;
    // face camera direction on attack
    this.yaw = this.camYaw + Math.PI;
  };

  Player.prototype.spendStamina = function (amount) {
    this.stamina = Math.max(0, this.stamina - amount);
    this.staminaRegenBlock = CFG.staminaRegenDelay;
  };

  Player.prototype.takeDamage = function (amount) {
    if (this.iframes > 0 || this.state !== 'alive') return false;
    this.hp = Math.max(0, this.hp - amount);
    if (this.hp <= 0) {
      this.state = 'dying';
      this.stateTime = 0;
    }
    return true;
  };

  // Returns attack sweep state for the combat layer: null or {origin, dir,
  // range, halfAngle, damage}.
  Player.prototype.consumeAttackSweep = function () {
    if (!this.attacking || this.attackDidHit) return null;
    // hit lands midway through the swing
    if (this.attackTimer > CFG.attackDuration * 0.5) return null;
    this.attackDidHit = true;
    var halfAngle = deg2rad(CFG.attackArcHalfAngleDeg);
    return {
      origin: this.pos.clone(),
      dir: new THREE.Vector3(Math.sin(this.yaw), 0, Math.cos(this.yaw)),
      range: CFG.attackRange,
      halfAngle: halfAngle,
      damage: CFG.attackDamage
    };
  };

  Player.prototype.update = function (dt, clampToBounds) {
    this.stateTime += dt;

    // timers
    if (this.iframes > 0) this.iframes = Math.max(0, this.iframes - dt);
    if (this.staminaRegenBlock > 0) {
      this.staminaRegenBlock -= dt;
    } else if (this.stamina < this.staminaMax) {
      this.stamina = Math.min(this.staminaMax, this.stamina + CFG.staminaRegenPerSec * dt);
    }

    if (this.state === 'dying') {
      this.deathTilt = Math.min(Math.PI / 2, this.deathTilt + dt * 3);
      if (this.body) this.body.rotation.x = -this.deathTilt;
      if (this.stateTime >= CFG.respawnDelay) this.state = 'dead';
      return;
    }

    if (this.attacking) {
      this.attackTimer -= dt;
      if (this.attackTimer <= 0) this.attacking = false;
    }

    var displacement = new THREE.Vector3(0, 0, 0);

    if (this.rolling) {
      this.rollTimer -= dt;
      // roll = quick translation + tumble
      var step = this.rollDir.clone().multiplyScalar(CFG.rollSpeed * dt);
      this.pos.add(step);
      if (this.body) this.body.rotation.x = (1 - this.rollTimer / CFG.rollDuration) * Math.PI * 2;
      if (this.rollTimer <= 0) {
        this.rolling = false;
        if (this.body) this.body.rotation.x = 0;
      }
    } else {
      // camera-relative movement
      this.collectMoveInput();
      var mx = this.moveInput.x, mz = this.moveInput.z;
      if (mx !== 0 || mz !== 0) {
        var len = Math.sqrt(mx * mx + mz * mz);
        mx /= len; mz /= len;
        var speed = (this.sprinting && this.stamina > 0) ? CFG.sprintSpeed : CFG.walkSpeed;
        if (this.sprinting && this.stamina > 0) {
          this.spendStamina(CFG.sprintStaminaPerSec * dt);
        }
        if (this.attacking) speed *= 0.3;   // slow while swinging
        // camera yaw basis: forward = camera forward projected on xz
        var fx = Math.sin(this.camYaw + Math.PI), fz = Math.cos(this.camYaw + Math.PI);
        var rx = Math.cos(this.camYaw + Math.PI), rz = -Math.sin(this.camYaw + Math.PI);
        // forward is -z input; right is +x input
        this.pos.x += (fx * (-mz) + rx * mx) * speed * dt;
        this.pos.z += (fz * (-mz) + rz * mx) * speed * dt;
        // turn body toward movement direction
        var targetYaw = Math.atan2(fx * (-mz) + rx * mx, fz * (-mz) + rz * mx);
        var maxTurn = deg2rad(CFG.turnLerpDegPerSec) * dt;
        var dyaw = targetYaw - this.yaw;
        while (dyaw > Math.PI) dyaw -= Math.PI * 2;
        while (dyaw < -Math.PI) dyaw += Math.PI * 2;
        this.yaw += Math.max(-maxTurn, Math.min(maxTurn, dyaw));
        // walk bob
        this.bobPhase += dt * (this.sprinting ? 14 : 9);
        if (this.body) {
          this.body.position.y = Math.abs(Math.sin(this.bobPhase)) * 0.12;
          this.body.rotation.z = Math.sin(this.bobPhase) * 0.04;
        }
      } else {
        if (this.body) { this.body.position.y = 0; this.body.rotation.z = 0; }
      }
    }

    if (clampToBounds) clampToBounds(this);

    // attack swing rotation (procedural)
    if (this.body) {
      if (this.attacking) {
        var t = 1 - this.attackTimer / CFG.attackDuration;   // 0..1
        var swing = Math.sin(t * Math.PI) * deg2rad(110);
        this.body.rotation.y = this.yaw;
        // arm-swing approximated by whole-body pitch/roll nudge
        this.body.rotation.x = -swing * 0.25;
      } else if (!this.rolling) {
        this.body.rotation.x = 0;
        this.body.rotation.y = this.yaw;
      }
    }

    this.root.position.copy(this.pos);
  };

  Player.prototype.updateCamera = function (dt) {
    // orbit camera behind player
    var target = this.pos.clone();
    target.y += CFG.camHeight;
    var offset = new THREE.Vector3(
      Math.sin(this.camYaw) * Math.cos(this.camPitch),
      Math.sin(this.camPitch),
      Math.cos(this.camYaw) * Math.cos(this.camPitch)
    ).multiplyScalar(this.camDist);
    var want = target.clone().add(offset);
    var lerp = 1 - Math.exp(-CFG.camFollowLerp * dt);
    this.camera.position.lerp(want, lerp);
    this.camera.lookAt(target);
  };

  Player.prototype.respawnAt = function (x, z) {
    this.pos.set(x, 0, z);
    this.hp = this.hpMax;
    this.stamina = this.staminaMax;
    this.state = 'alive';
    this.stateTime = 0;
    this.rolling = false;
    this.attacking = false;
    this.iframes = 0;
    this.deathTilt = 0;
    if (this.body) { this.body.rotation.x = 0; this.body.rotation.y = this.yaw; }
  };

  window.WH_Player = Player;
})();