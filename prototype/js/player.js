// Witch Hunter prototype v2 - third-person player controller.
// D2: movement basis is CAMERA yaw (W = camera forward on screen, S = back,
// A/D = strafe). v1 had the strafe right-vector inverted; fixed.
// D3: souls-style lock-on: hard yaw track to target, camera follow, strafe.
// Transform-only procedural animation (assets are unrigged). All tunables
// from CONFIG.

(function () {
  'use strict';

  var CFG = window.WH_CONFIG.player;
  var LOCK = window.WH_CONFIG.lockOn;
  var ANIM = window.WH_CONFIG.anim;
  var AW = ANIM.attack;
  var WL = ANIM.walk;

  function deg2rad(d) { return d * Math.PI / 180; }
  function smooth(p) { return p * p * (3 - 2 * p); }   // smoothstep ease

  function shortestAngle(a) {
    while (a > Math.PI) a -= Math.PI * 2;
    while (a < -Math.PI) a += Math.PI * 2;
    return a;
  }

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
    this.moveDirWorld = { x: 0, z: 0 }; // last world-space move dir (roll basis)
    this.sprinting = false;
    this.rolling = false;
    this.rollTimer = 0;
    this.rollDir = new THREE.Vector3(0, 0, 1);
    this.attacking = false;
    this.attackTimer = 0;
    this.attackDidHit = false;
    this.bobPhase = 0;
    this.idleTime = 0;                // seconds without movement input
    this.idlePhase = 0;               // breathing phase
    this.lungeLeft = 0;               // strike lunge distance remaining

    // camera orbit state
    this.camYaw = Math.PI;            // looking toward -z (into region A)
    this.camPitch = deg2rad(22);
    this.camDist = CFG.camDistance;
    this.dragging = false;
    this.lastDragX = 0;
    this.lastDragY = 0;

    // lock-on state (D3)
    this.lockTarget = null;           // enemy object or null

    // visual root (body added by game after assets load)
    this.root = new THREE.Group();
    this.body = null;
    this.deathTilt = 0;

    this.bindInput();
  }

  Player.prototype.setBody = function (meshRoot) {
    if (this.body) this.root.remove(this.body);
    this.body = meshRoot;
    // Bob/tilt animation writes body.position.y absolutely; wrap the
    // ground-aligned template in an inner holder so animation only moves
    // the holder and the template's own ground offset is preserved.
    this.bodyBaseY = meshRoot.position.y || 0;
    this.bodyBaseX = meshRoot.position.x || 0;
    this.root.add(this.body);
  };

  // Weapon attach (v3): the sword is driven as a separate child so body lean
  // and sword arc read together. game.js calls this after preload.
  Player.prototype.setWeapon = function (mesh) {
    this.sword = mesh;
    this.swordBase = {
      x: mesh.position.x || 0,
      y: mesh.position.y || 0,
      z: mesh.position.z || 0,
      rz: mesh.rotation.z || 0,
      ry: mesh.rotation.y || 0
    };
  };

  Player.prototype.resetWeaponPose = function () {
    if (!this.sword) return;
    this.sword.position.set(this.swordBase.x, this.swordBase.y, this.swordBase.z);
    this.sword.rotation.z = this.swordBase.rz;
    this.sword.rotation.y = this.swordBase.ry;
  };

  // Bob offset: call from the walk animation in place of absolute writes.
  // Composes with groundAlign: only ever ADDS offsets to the stored base.
  // leanX: body.rotation.x (forward+). yawAdd: added to body yaw (yaw osc).
  // swayX: lateral body.position.x offset (body space).
  Player.prototype.setBodyBob = function (bobY, tiltZ, leanX, yawAdd, swayX) {
    if (!this.body) return;
    this.body.position.y = this.bodyBaseY + bobY;
    this.body.position.x = (this.bodyBaseX || 0) + (swayX || 0);
    if (tiltZ !== undefined) this.body.rotation.z = tiltZ;
    if (leanX !== undefined) this.body.rotation.x = leanX;
    if (yawAdd !== undefined) this.body.rotation.y = this.yaw + yawAdd;
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
      if (e.code === 'KeyF' && !e.repeat) {
        e.preventDefault();
        if (self.onLockToggle) self.onLockToggle();  // game.js decides engage/break
      }
    });
    document.addEventListener('keyup', function (e) {
      self.keys[e.code] = false;
    });
    document.addEventListener('mousedown', function (e) {
      if (e.button === 0) {
        self.tryAttack();
        if (!self.lockTarget) {
          self.dragging = true;
          self.lastDragX = e.clientX;
          self.lastDragY = e.clientY;
        }
      }
    });
    document.addEventListener('mouseup', function (e) {
      if (e.button === 0) self.dragging = false;
    });
    document.addEventListener('mousemove', function (e) {
      if (!self.dragging || self.lockTarget) return;   // mouse cam disabled while locked
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

  // v3: roll cancels attack during WINDUP only (souls-like); attack cannot
  // start during roll.
  Player.prototype.tryRoll = function () {
    if (this.state !== 'alive' || this.rolling) return;
    if (this.attacking) {
      if (this.getAttackStage() !== 'windup') return;   // strike/recover locked
      this.attacking = false;                           // cancel in windup
      this.attackTimer = 0;
      this.lungeLeft = 0;
      this.resetWeaponPose();
    }
    if (this.stamina < CFG.rollStaminaCost) return;
    this.spendStamina(CFG.rollStaminaCost);
    this.rolling = true;
    this.rollTimer = CFG.rollDuration;
    this.iframes = CFG.rollIFrameWindow;
    // roll direction: current move input direction, or facing if idle
    var dir = new THREE.Vector3(this.moveDirWorld.x, 0, this.moveDirWorld.z);
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
    this.lungeLeft = AW.strikeLunge;
    // face camera direction on attack (unless locked: hard track handles it)
    if (!this.lockTarget) this.yaw = this.camYaw + Math.PI;
  };

  // v3 D1: attack stage from elapsed time. 'windup' | 'strike' | 'recover' | null.
  Player.prototype.getAttackStage = function () {
    if (!this.attacking) return null;
    var elapsed = CFG.attackDuration - this.attackTimer;
    var windupEnd = CFG.attackDuration * AW.windupFrac;
    var strikeEnd = CFG.attackDuration * (AW.windupFrac + AW.strikeFrac);
    if (elapsed < windupEnd) return 'windup';
    if (elapsed < strikeEnd) return 'strike';
    return 'recover';
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
  // range, halfAngle, damage}. v3: the active window is the whole STRIKE
  // stage (hit lands midway through the swing; the sweep consumes once).
  Player.prototype.consumeAttackSweep = function () {
    if (!this.attacking || this.attackDidHit) return null;
    if (this.getAttackStage() !== 'strike') return null;
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

  // D3: hard yaw track toward the lock target each frame while locked.
  Player.prototype.updateLockTracking = function () {
    if (!this.lockTarget || this.state !== 'alive') return;
    var t = this.lockTarget;
    var dx = t.pos.x - this.pos.x;
    var dz = t.pos.z - this.pos.z;
    if (dx * dx + dz * dz < 0.0001) return;
    this.yaw = Math.atan2(dx, dz);
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

    // D3: while locked, body yaw hard-tracks the target
    this.updateLockTracking();

    var displacement = new THREE.Vector3(0, 0, 0);
    var moving = false;
    var sprintingNow = false;

    if (this.rolling) {
      this.rollTimer -= dt;
      // roll = quick translation + eased full tumble (v3)
      var step = this.rollDir.clone().multiplyScalar(CFG.rollSpeed * dt);
      this.pos.add(step);
      if (this.body) {
        var rp = 1 - this.rollTimer / CFG.rollDuration;
        this.body.rotation.x = smooth(rp) * Math.PI * 2;
        this.body.rotation.z = 0;
      }
      if (this.rollTimer <= 0) {
        this.rolling = false;
        if (this.body) { this.body.rotation.x = 0; this.body.rotation.z = 0; }
        this.resetWeaponPose();
      }
    } else {
      // camera-relative movement
      this.collectMoveInput();
      var mx = this.moveInput.x, mz = this.moveInput.z;
      if (mx !== 0 || mz !== 0) {
        moving = true;
        sprintingNow = this.sprinting && this.stamina > 0;
        var len = Math.sqrt(mx * mx + mz * mz);
        mx /= len; mz /= len;
        var speed = sprintingNow ? CFG.sprintSpeed : CFG.walkSpeed;
        if (sprintingNow) {
          this.spendStamina(CFG.sprintStaminaPerSec * dt);
        }
        if (this.attacking) speed *= 0.3;   // slow while swinging
        // camera yaw basis: camera forward projected on xz plane.
        // Camera sits at yaw = camYaw BEHIND the player, so camera forward
        // (what W moves toward) is (sin(camYaw + PI), cos(camYaw + PI)).
        var fx = Math.sin(this.camYaw + Math.PI), fz = Math.cos(this.camYaw + Math.PI);
        // screen-right = cross(up, cameraBack) = (-fz, fx)
        var rx = -fz, rz = fx;
        var wx = fx * (-mz) + rx * mx;
        var wz = fz * (-mz) + rz * mx;
        this.pos.x += wx * speed * dt;
        this.pos.z += wz * speed * dt;
        // remember world move dir (roll basis)
        this.moveDirWorld.x = wx;
        this.moveDirWorld.z = wz;
        // turn body toward movement direction (skip while locked: hard track)
        if (!this.lockTarget) {
          var targetYaw = Math.atan2(wx, wz);
          var maxTurn = deg2rad(CFG.turnLerpDegPerSec) * dt;
          var dyaw = shortestAngle(targetYaw - this.yaw);
          this.yaw += Math.max(-maxTurn, Math.min(maxTurn, dyaw));
        }
        // ---- v3 D2: layered walk/sprint cycle ----
        this.idleTime = 0;
        this.bobPhase += dt * (sprintingNow ? WL.bobFreqSprint : WL.bobFreqWalk);
        if (this.body) {
          var amp = sprintingNow ? WL.sprintAmpMult : 1;
          var bob = Math.abs(Math.sin(this.bobPhase)) * WL.bobAmp * amp;
          // foot-phase dip: 2x freq, smaller (two dips per cycle)
          bob += Math.abs(Math.sin(this.bobPhase * WL.footDipFreqMult)) * WL.footDipAmp * amp;
          // forward lean proportional to speed (walk vs sprint)
          var lean = (sprintingNow ? WL.leanSprint : WL.leanWalk) * (this.attacking ? 0.5 : 1);
          // lateral sway at half bob frequency + counter-roll
          var sway = Math.sin(this.bobPhase * WL.swayFreqMult) * WL.swayAmp * amp;
          var roll = Math.sin(this.bobPhase * WL.swayFreqMult) * -WL.counterRollAmp * amp;
          // yaw oscillation at bob frequency (arm-swing substitute)
          var yawOsc = Math.sin(this.bobPhase) * WL.yawOscAmp * amp;
          this.setBodyBob(bob, roll, lean, yawOsc, sway);
        }
      } else {
        this.moveDirWorld.x = 0;
        this.moveDirWorld.z = 0;
        // ---- v3 D2: idle breathing after idleDelay ----
        this.idleTime += dt;
        if (this.body) {
          if (this.idleTime >= WL.idleDelay) {
            this.idlePhase += dt * (Math.PI * 2 / WL.idlePeriod);
            this.setBodyBob(
              (Math.sin(this.idlePhase) * 0.5 + 0.5) * WL.idleBobAmp, 0,
              0, Math.sin(this.idlePhase * 0.5) * WL.idleYawAmp, 0);
          } else {
            this.setBodyBob(0, 0, 0, 0, 0);
          }
        }
      }
    }

    if (clampToBounds) clampToBounds(this);

    // ---- v3 D1: three-stage attack pose + strike lunge ----
    if (this.body) {
      if (this.attacking) {
        var stage = this.getAttackStage();
        var yawBase = this.yaw;
        if (stage === 'windup') {
          var wp = (CFG.attackDuration - this.attackTimer) /
                   (CFG.attackDuration * AW.windupFrac);       // 0..1
          var we = smooth(wp);
          this.body.rotation.x = AW.windupLean * we;           // lean back
          this.body.rotation.y = yawBase;
          this.body.rotation.z = 0;
          this.body.position.y = this.bodyBaseY - AW.windupCrouch * we;  // crouch
          this.body.position.x = this.bodyBaseX || 0;
          if (this.sword) {
            this.sword.rotation.z = this.swordBase.rz + AW.windupSwordRaise * we;
          }
        } else if (stage === 'strike') {
          var sp = (CFG.attackDuration * AW.windupFrac + CFG.attackDuration * AW.strikeFrac
                    - this.attackTimer) /
                   (CFG.attackDuration * AW.strikeFrac);        // 0..1
          var se = 1 - (1 - sp) * (1 - sp);                     // ease-out
          // horizontal yaw sweep through the stage (start behind right shoulder)
          this.body.rotation.y = yawBase - deg2rad(AW.strikeYawSweepDeg) * 0.5
                                 + deg2rad(AW.strikeYawSweepDeg) * se;
          this.body.rotation.x = 0;
          this.body.rotation.z = 0;
          this.body.position.y = this.bodyBaseY;
          this.body.position.x = this.bodyBaseX || 0;
          if (this.sword) {
            // raise -> level then sweep through the horizontal arc
            this.sword.rotation.z = this.swordBase.rz +
              AW.windupSwordRaise * (1 - se) +
              deg2rad(AW.strikeSwordSweepDeg) * se - deg2rad(AW.strikeSwordSweepDeg) * 0.5 * se;
          }
          // forward lunge along facing: velocity model. The old target-delta
          // formula (strikeLunge * se - (strikeLunge - lungeLeft)) strands
          // the remainder whenever the STRIKE stage spans few frames
          // (hitches clamped at maxDt), leaving the lunge at ~0.09 of 0.25.
          // A dt-scaled velocity drains the full lunge at any frame rate.
          if (this.lungeLeft > 0) {
            var strikeSpan = CFG.attackDuration * AW.strikeFrac;
            var lungeVel = AW.strikeLunge / strikeSpan;
            var lungeStep = Math.min(lungeVel * dt, this.lungeLeft);
            this.pos.x += Math.sin(this.yaw) * lungeStep;
            this.pos.z += Math.cos(this.yaw) * lungeStep;
            this.lungeLeft -= lungeStep;
          }
        } else {                                                // recover
          var rEnd = CFG.attackDuration * (AW.windupFrac + AW.strikeFrac);
          var rp2 = Math.min(1, Math.max(0,
            (CFG.attackDuration - this.attackTimer - rEnd) /
            (CFG.attackDuration - rEnd)));                      // 0..1
          var re = smooth(rp2);
          var swing = deg2rad(AW.strikeYawSweepDeg) * 0.5;      // sweep end offset
          this.body.rotation.y = yawBase + swing * (1 - re);    // ease back to neutral
          this.body.rotation.x = AW.recoverLean * re;           // forward-lean settle
          this.body.rotation.z = 0;
          this.body.position.y = this.bodyBaseY;
          this.body.position.x = this.bodyBaseX || 0;
          if (this.sword) {
            this.sword.rotation.z = this.swordBase.rz + AW.windupSwordRaise * (1 - re);
          }
        }
      } else if (!this.rolling) {
        this.body.rotation.x = 0;
        this.body.rotation.y = this.yaw;
        this.body.rotation.z = 0;
        this.body.position.x = this.bodyBaseX || 0;
        if (this.sword) this.resetWeaponPose();
      }
    }
    if (!this.attacking) this.lungeLeft = 0;

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

    if (this.lockTarget && this.state === 'alive') {
      // D3: camera follows so the target stays framed. Aim camera yaw so the
      // target is straight ahead of the player; pull back a bit for framing.
      var t = this.lockTarget;
      var dx = t.pos.x - this.pos.x;
      var dz = t.pos.z - this.pos.z;
      var dist = Math.sqrt(dx * dx + dz * dz);
      // camera should sit opposite the target relative to the player
      var wantYaw = dist > 0.001 ? Math.atan2(dx, dz) + Math.PI : this.camYaw;
      var wantDist = Math.min(CFG.camMaxDistance,
        Math.max(this.camDist, dist + LOCK.camExtraDistance));
      var lerp = 1 - Math.exp(-LOCK.camLerp * dt);
      this.camYaw += shortestAngle(wantYaw - this.camYaw) * lerp;
      // frame slightly above midpoint between player and target
      target.x = (this.pos.x + t.pos.x) / 2;
      target.z = (this.pos.z + t.pos.z) / 2;
      var midDist = dist / 2;
      offset.set(
        Math.sin(this.camYaw) * Math.cos(this.camPitch),
        Math.sin(this.camPitch),
        Math.cos(this.camYaw) * Math.cos(this.camPitch)
      ).multiplyScalar(Math.max(CFG.camMinDistance, midDist + LOCK.camExtraDistance));
      want = target.clone().add(offset);
      this.camera.position.lerp(want, lerp);
    } else {
      var lerp2 = 1 - Math.exp(-CFG.camFollowLerp * dt);
      this.camera.position.lerp(want, lerp2);
    }
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
    this.lockTarget = null;
    if (this.body) { this.body.rotation.x = 0; this.body.rotation.y = this.yaw; }
  };

  window.WH_Player = Player;
})();