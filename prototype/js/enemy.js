// Witch Hunter prototype v1 - enemies: bandit and ghoul FSMs.
// FSM: idle -> aggro -> chase -> attack -> (hurt stagger) -> death.
// Enemies are per-region instance state; they never cross region boundaries
// (hold at boundary margin). All tunables from CONFIG.

(function () {
  'use strict';

  var CFG = window.WH_CONFIG.enemy;
  var ANIM = window.WH_CONFIG.anim;

  function smooth(p) { return p * p * (3 - 2 * p); }   // smoothstep ease

  function wrapAngle(a) {
    while (a > Math.PI) a -= Math.PI * 2;
    while (a < -Math.PI) a += Math.PI * 2;
    return a;
  }

  function cfgFor(type) {
    return CFG[type] || CFG.bandit;
  }

  // AI1: the decision-loop rows, or null when the type opts out (ghoul
  // guardMode 0) - a null here makes every AI1 branch skip.
  function ai1For(enemy) {
    var a = enemy.cfg.ai1;
    return a && a.guardMode !== 0 ? a : null;
  }

  // AI1: the live player (read-only; attacking / getAttackStage / guardBroken)
  function livePlayer() {
    return window.WH_GAME ? window.WH_GAME.player : null;
  }

  // AI1 R6: a cast windup running in either hand
  function playerCasting(P) {
    return !!P.cast && ((P.cast.main && P.cast.main.windup > 0) ||
      (P.cast.off && P.cast.off.windup > 0));
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
    this.attackTimer = 0;              // legacy cooldown field (phase FSM owns cadence)
    this.attackPhase = 'idle';         // combat-ds1 P0-6: windup | active | recover | idle
    this.attackPhaseT = 0;
    this.pos = new THREE.Vector3(spawnX, 0, spawnZ);
    this.yaw = Math.random() * Math.PI * 2;
    this.bobPhase = Math.random() * Math.PI * 2;
    this.root = new THREE.Group();
    this.yawFrame = new THREE.Group();
    this.root.add(this.yawFrame);
    this.body = null;
    this.deadFall = 0;                 // death fall-over progress
    this.corpseFinalY = null;          // measured once at death start
    this.settleTime = -1;              // death settle bounce timer (-1 = off)
    this.staggerTimer = 0;             // v3 hit-stagger visual timer
    this.hopTimer = -1;                // ghoul lunge hop timer (-1 = off)
    this.hopDir = { x: 0, z: 0 };      // hop direction at takeoff
    this.hopOriginY = 0;               // root y at takeoff (for arc baseline)
    // v6: parry stagger / riposte state
    this.riposteStaggerTimer = 0;      // > 0 = staggered and vulnerable
    this.riposteArmed = false;         // next player hit does riposte damage
    // Order D: shield deflect recoil (presentation overlay, see deflect())
    this.deflectTimer = 0;
    this.deflectDir = { x: 0, z: 0 };
    // AI1: bandit decision-loop state (ephemeral, never persisted - R10)
    this.ai1Tick = 0;                  // seconds to the next decision tick
    this.ai1Orbit = Math.random() < 0.5 ? 1 : -1;   // strafe orbit direction
    this.ai1FlipT = 0;                 // seconds since the last orbit flip
    this.ai1Press = false;             // closing in to swing (opening / bias roll)
    this.ai1Strafing = false;          // inside strafeBandOuter this frame
    this.ai1GuardActive = false;       // guard posture raised (takeDamage mitigation)
    this.ai1GuardT = 0;                // seconds the guard has been held
  }

  Enemy.prototype.setBody = function (meshRoot) {
    if (this.body) this.yawFrame.remove(this.body);
    this.body = meshRoot;
    this.bodyBaseY = meshRoot.position.y || 0;
    this.bodyBaseRotX = meshRoot.rotation.x || 0;   // Order D deflect overlay base
    this.bodyBaseRotY = meshRoot.rotation.y || 0;
    this.yawFrame.add(this.body);
    var bodyName = this.type === 'bandit' ? 'banditBody' : 'ghoulBody';
    if (window.WH_ASSETS.getClips(bodyName).length) {
      // 10-05: ghouls play the Mixamo zombie set, bandits the Mixamo axe set.
      this.anim = new window.WH_CharacterAnim(meshRoot, window.WH_ASSETS.getClips(bodyName),
        { variant: this.type === 'ghoul' ? 'zombie' : 'bandit' });
    }
    // Rigged bandits carry the axe on the animated hand, not a world pivot.
    var hand = meshRoot.getObjectByName('R_Hand');
    if (this.type === 'bandit' && hand) {
      var heldAxe = window.WH_ASSETS.instance('handAxe');
      // Measured sizing (2026-10-03): 2.004m GLB -> 0.6m hand-held (scale
      // ~0.299) via CONFIG.assets.weaponScale; replaces hardcoded 0.8.
      heldAxe.scale.setScalar(window.WH_ASSETS.weaponScale('handAxe'));
      hand.add(heldAxe);
      heldAxe.position.set(0, 0, 0);
      // Grip mount (2026-10-03 re-measure): the axe GLB's bit/mass points
      // along mesh-local +Y (radial profile: near +Y 0.224 vs near -Y
      // 0.115), so map +Y -> hand-local +Z (grip forward) so the bit leads.
      // Same constant local-space knob as the player sword: pose-independent
      // and shared with CONFIG.assets.weaponMount (rollDeg tuning lives
      // there). The pivot fallback below keeps the idlePose table (its
      // skinned basis never existed).
      var wm = window.WH_CONFIG.assets.weaponMount;
      var axeMount = new THREE.Quaternion();
      if (wm && wm.enabled) {
        axeMount.setFromUnitVectors(
          new THREE.Vector3(0, 1, 0), new THREE.Vector3(0, 0, 1));
        // Roll about hand-local +Z: composed on the LEFT of the axis mapping
        // so it spins the mounted axe about its own grip axis (applied after
        // the mapping); positive rollDeg = CCW around +Z, right-hand rule.
        if (wm.rollDeg) {
          axeMount.premultiply(new THREE.Quaternion().setFromAxisAngle(
            new THREE.Vector3(0, 0, 1), wm.rollDeg * Math.PI / 180));
        }
      }
      heldAxe.quaternion.copy(axeMount);
      this.heldAxe = heldAxe;                      // Order D deflect knock
      this.heldAxeBaseQuat = axeMount.clone();
    }
    // Rigid stand-in fallback retains its original weapon pivot.
    if (!hand && this.type === 'bandit' && window.WH_ASSETS &&
        window.WH_ASSETS.instance && window.WH_CONFIG.moveset) {
      var axe = window.WH_ASSETS.instance('handAxe');
      if (axe) {
        axe.scale.setScalar(0.8);
        this.weaponPivot = new THREE.Group();
        this.yawFrame.add(this.weaponPivot);
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

  // The FSM stops on death, but the visual fall must continue to settle.
  Enemy.prototype.updateDeathVisual = function (dt) {
    if (!this.body) return;
    // A rig without WH_Death (CharacterAnim warns) takes the rigid fall below.
    if (this.anim && this.anim.actions.death) {
      // deadFall 1 before the clip ever ran = corpse restored by a region
      // rebuild: pose it at the clip end instead of replaying the death.
      this.anim.death(this.deadFall >= 1);
      this.root.position.copy(this.pos);
      this.yawFrame.rotation.y = this.yaw;
      var deathAction = this.anim.actions.death;
      if (this.corpseFinalY === null &&
          deathAction.time >= deathAction.getClip().duration - 0.001) {
        this.root.position.y = 0;
        this.root.updateMatrixWorld(true);
        var finalMinY = new THREE.Box3().setFromObject(this.root).min.y;
        this.corpseFinalY = isFinite(finalMinY) ? -finalMinY + 0.01 : 0;
      }
      if (this.corpseFinalY !== null) {
        this.root.position.y = this.corpseFinalY;
        this.deadFall = 1;
      }
      return;
    }
    if (this.corpseFinalY === null) {
      this.root.position.copy(this.pos);
      this.yawFrame.rotation.y = this.yaw;
      this.body.position.y = this.bodyBaseY || 0;
      this.body.rotation.set(-Math.PI / 2, 0, 0);
      // Include the equipped axe: the validation box spans the whole corpse.
      var minY = new THREE.Box3().setFromObject(this.root).min.y;
      // A root translation has the opposite sign to the measured minimum.
      this.corpseFinalY = isFinite(minY) ? -minY + 0.01 : 0;
    }
    if (this.settleTime < 0 && this.deadFall >= 1) this.settleTime = 0;
    if (this.settleTime < 0) {
      this.deadFall = Math.min(1, this.deadFall + dt * 2.5);
      this.body.rotation.x = -this.deadFall * Math.PI / 2;
      this.root.position.y = this.deadFall * this.corpseFinalY;
    } else {
      this.settleTime += dt;
      var sp = Math.min(1, this.settleTime / ANIM.death.settleDuration);
      var decay = Math.exp(-sp * 5);
      var bounce = Math.sin(sp * Math.PI * 2) * ANIM.death.settleOvershoot * decay;
      this.body.rotation.x = -Math.PI / 2;
      this.root.position.y = this.corpseFinalY + bounce;
    }
  };

  // FSM sense/aggression update. playerPos: THREE.Vector3, canDamagePlayer:
  // callback(amount, attacker) routes damage through the combat layer
  // (block/parry/i-frames; its return value is unused). boundary:
  // {z, holdMargin} clamps movement to home side.
  Enemy.prototype.update = function (dt, playerPos, playerAlive, canDamagePlayer, boundary, regionManager) {
    if (this.fsm === 'dead') {
      this.updateDeathVisual(dt);
      return;
    }
    this.fsmTime += dt;
    // Order D: deflect pushback runs before the parry-stagger freeze so a
    // parried enemy still recoils
    if (this.deflectTimer > 0) {
      var dfl = window.WH_CONFIG.block;
      var dstep = Math.min(dt, this.deflectTimer);
      var dspeed = dfl.deflect.pushback / Math.max(1e-4, dfl.deflectEnemyRecoilSec);
      this.pos.x += this.deflectDir.x * dspeed * dstep;
      this.pos.z += this.deflectDir.z * dspeed * dstep;
      this.deflectTimer = Math.max(0, this.deflectTimer - dt);
      if (boundary && regionManager) regionManager.clampEnemyToHomeSide(this, boundary);
    }

    var toPlayerX = playerPos.x - this.pos.x;
    var toPlayerZ = playerPos.z - this.pos.z;
    var distToPlayer = Math.sqrt(toPlayerX * toPlayerX + toPlayerZ * toPlayerZ);
    var distToSpawn = Math.sqrt(
      (this.pos.x - this.spawn.x) * (this.pos.x - this.spawn.x) +
      (this.pos.z - this.spawn.z) * (this.pos.z - this.spawn.z)
    );
    var ai1 = ai1For(this);

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
        // Order D: frozen stance (no walk-in-place on the clip) + recoil
        this.animMoveSpeed = 0;
        if (this.body) {
          this.root.position.x = this.pos.x;
          this.root.position.z = this.pos.z;
          this.applyDeflectPose(this.anim ? this.bodyBaseRotX : 0,
            this.anim ? this.bodyBaseRotY : 0);
        }
        return;              // frozen: no transitions, no movement, no attacks
      }
    }
    if (this.fsm === 'stagger') {
      if (this.fsmTime >= this.cfg.staggerTime) this.setFsm('chase');
    } else if (this.fsm === 'attack') {
      if (!playerAlive) {
        this.setFsm('idle');
        this.attackPhase = 'idle';
        this.attackPhaseT = 0;
      } else {
        var phase = this.cfg.attackPhase;
        this.attackPhaseT += dt;
        if (this.attackPhase === 'windup') {
          // combat-ds1 P0-6: only windup may track; freeze facing for the hit.
          if (distToPlayer > 0.001) {
            var deltaYaw = wrapAngle(Math.atan2(toPlayerX, toPlayerZ) - this.yaw);
            var maxYaw = phase.trackDegPerSec * Math.PI / 180 * dt;
            this.yaw += Math.max(-maxYaw, Math.min(maxYaw, deltaYaw));
          }
          if (this.attackPhaseT >= phase.windup) {
            this.attackPhase = 'active';
            this.attackPhaseT = 0;
            // One damage opportunity at active entry; range and facing must
            // both hold after tracking ends. The callback owns parry/i-frames.
            var hitYaw = wrapAngle(Math.atan2(toPlayerX, toPlayerZ) - this.yaw);
            // A-2 ruling 2026-10-02: hitArcDeg is a HALF-angle (±50°), per
            // the audit of record (doc 60 L221 arcHalfDeg 50); D1 renamed
            // the key only. /180 == *deg/2 in radians.
            if (distToPlayer <= this.cfg.attackRange + window.WH_CONFIG.player.radius &&
                Math.abs(hitYaw) <= phase.hitArcDeg * Math.PI / 180) {
              canDamagePlayer(this.cfg.attackDamage, this);
            }
          }
        } else if (this.attackPhase === 'active') {
          if (this.attackPhaseT >= phase.active) {
            this.attackPhase = 'recover';
            this.attackPhaseT = 0;
          }
        } else if (this.attackPhase === 'recover' && this.attackPhaseT >= phase.recover) {
          // AI1: one swing per decision - the bandit returns to the loop
          if (!ai1 && distToPlayer <= this.cfg.attackRange * 1.4) {
            this.attackPhase = 'windup';
            this.attackPhaseT = 0;
          } else {
            this.setFsm('chase');
            this.attackPhase = 'idle';
            this.attackPhaseT = 0;
          }
        }
      }
    } else if (this.fsm === 'idle' || this.fsm === 'aggro') {
      if (playerAlive && distToPlayer <= this.cfg.sightRadius) {
        this.setFsm('aggro');            // idle/aggro both walk home below
      }
      if (playerAlive && distToPlayer <= this.cfg.sightRadius * 0.8) {
        this.setFsm('chase');
      }
      if (ai1) {
        this.ai1Press = false;
        this.ai1GuardActive = false;   // disengaged: no posture left raised
        // AI1 R2: inside alwaysKnowsRadius the bandit engages even in darkness
        if (playerAlive && distToPlayer < ai1.alwaysKnowsRadius) this.setFsm('chase');
      }
    } else if (this.fsm === 'chase') {
      if (!playerAlive || distToPlayer > this.cfg.leashRadius || distToSpawn > this.cfg.leashRadius) {
        this.setFsm('idle');           // leash: disengage, walk home
      } else if (ai1) {
        this.ai1Decide(dt, ai1, distToPlayer);
      } else if (distToPlayer <= this.cfg.attackRange) {
        // v3: ghoul telegraphs the strike with a short forward hop
        if (this.type === 'ghoul' && ANIM.ghoulHop.duration > 0) {
          this.hopTimer = 0;
          this.hopDir = distToPlayer > 0.001
            ? { x: toPlayerX / distToPlayer, z: toPlayerZ / distToPlayer }
            : { x: 0, z: 0 };
        }
        this.setFsm('attack');
        this.attackPhase = 'windup';
        this.attackPhaseT = 0;
      }
    }

    // v3: hit-stagger visual timer runs down regardless of FSM
    if (this.staggerTimer > 0) this.staggerTimer = Math.max(0, this.staggerTimer - dt);

    // ---- movement per state ----
    var moveSpeed = 0;
    var dirX = 0, dirZ = 0;
    var ai1Face = false;               // AI1: face the player, not the step

    if (this.fsm === 'chase') {
      moveSpeed = this.cfg.chaseSpeed;
      if (distToPlayer > 0.001) {
        dirX = toPlayerX / distToPlayer;
        dirZ = toPlayerZ / distToPlayer;
      }
      // AI1 R3: in the strafe band the bandit circles tangentially (one
      // persistent orbit direction) and gives ground inside the inner edge;
      // beyond the band, or pressing an attack, the chase above closes in.
      if (ai1 && this.ai1GuardActive) {
        // AI1 R7: guard posture - root halts, body turns to face the player
        moveSpeed = 0;
        ai1Face = distToPlayer > 0.001;
      } else if (ai1 && this.ai1Strafing && !this.ai1Press && distToPlayer > 0.001) {
        var radial = distToPlayer < ai1.strafeBandInner ? -1 : 0;
        var sx = -dirZ * this.ai1Orbit + dirX * radial;
        var sz = dirX * this.ai1Orbit + dirZ * radial;
        var sLen = Math.sqrt(sx * sx + sz * sz);
        dirX = sx / sLen;
        dirZ = sz / sLen;
        moveSpeed = this.cfg.moveSpeed * ai1.strafeSpeedMult;
        ai1Face = true;
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
    if (ai1Face) this.yaw = Math.atan2(toPlayerX, toPlayerZ);

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
    this.animMoveSpeed = moveSpeed;
    if (this.body) {
      this.root.position.copy(this.pos);
      this.yawFrame.rotation.y = this.yaw;
      if (this.anim) {
        // The clip supplies gait, sway, crouch and hit poses. The existing
        // ghoul hop is a gameplay telegraph and stays on the world root.
        var hopYAnim = 0;
        if (this.hopTimer >= 0) {
          var hopFraction = this.hopTimer / ANIM.ghoulHop.duration;
          hopYAnim = 4 * hopFraction * (1 - hopFraction) * ANIM.ghoulHop.height;
        }
        this.root.position.y = hopYAnim;
        this.applyDeflectPose(this.bodyBaseRotX, this.bodyBaseRotY);
        return;
      }
      this.body.rotation.y = 0;
      // v3 D3: layered walk cycle with per-type amplitude multipliers
      if (this.fsm !== 'dead') {
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
        this.body.rotation.y = eYawOsc;
        if (stagT > 0) {
          // crouch dip proportional to stagger intensity
          this.body.position.y = (this.bodyBaseY || 0) - 0.06 * stagT;
        } else {
          this.body.position.y = this.bodyBaseY || 0;
        }
        if (this.type === 'ghoul' && this.fsm === 'attack' &&
            this.attackPhase === 'windup') {
          // The hop stays on the root; the crouch telegraphs the hit below it.
          var dip = Math.min(1, this.attackPhaseT / this.cfg.attackPhase.windup);
          this.body.position.y -= 0.08 * dip;
        }
        // combat-ds1 P0-6: slow windup raise, fast active sweep, recover.
        if (this.weaponPivot && this.axeIdle) {
          if (this.fsm === 'attack' && this.attackPhase === 'windup') {
            var raise = Math.min(1, this.attackPhaseT / this.cfg.attackPhase.windup);
            this.weaponPivot.rotation.y = this.axeIdle.rot[1] + (Math.PI / 8) * raise;
          } else if (this.fsm === 'attack' && this.attackPhase === 'active') {
            var sweep = Math.min(1, this.attackPhaseT / this.cfg.attackPhase.active);
            this.weaponPivot.rotation.y = this.axeIdle.rot[1] + Math.PI / 8 -
              (Math.PI * 5 / 8) * sweep;
          } else if (this.fsm === 'attack' && this.attackPhase === 'recover') {
            var recovery = smooth(Math.min(1, this.attackPhaseT / this.cfg.attackPhase.recover));
            this.weaponPivot.rotation.y = this.axeIdle.rot[1] - (Math.PI / 2) * (1 - recovery);
          } else {
            this.weaponPivot.rotation.y = this.axeIdle.rot[1];
          }
        }
        this.applyDeflectPose(this.body.rotation.x, this.body.rotation.y, true);
      }
      // Idle patrol poses can tilt the low mesh below or above the floor.
      if (this.fsm === 'idle' && this.hopTimer < 0) {
        var idleMinY = new THREE.Box3().setFromObject(this.root).min.y;
        if (isFinite(idleMinY)) this.root.position.y -= idleMinY;
      }
    }
  };

  Enemy.prototype.setFsm = function (next) {
    if (this.fsm === next) return;
    this.fsm = next;
    this.fsmTime = 0;
  };

  // AI1 R3-R5: the bandit decision loop, run from the chase state. Movement
  // stays in update (this only sets ai1Strafing / ai1Press / ai1Orbit); every
  // swing enters the EXISTING attack phase FSM via ai1StartAttack.
  Enemy.prototype.ai1Decide = function (dt, ai, dist) {
    this.ai1Strafing = dist <= ai.strafeBandOuter;
    this.ai1FlipT += dt;
    if (this.ai1FlipT >= ai.strafeDirFlipSeconds) {
      this.ai1Orbit = -this.ai1Orbit;
      this.ai1FlipT = 0;
    }
    var P = livePlayer();
    // R6-R7: a raised guard holds until the player is back to no-attack /
    // no-cast, capped at guardSecondsMax; while it holds, no decision tick
    if (this.ai1GuardActive) {
      this.ai1GuardT += dt;
      if (!P || !(P.attacking || playerCasting(P)) || this.ai1GuardT >= ai.guardSecondsMax) {
        this.ai1DropGuard();
      } else {
        return;
      }
    }
    // a press swings the moment it reaches attackRadius
    if (this.ai1Press && dist <= ai.attackRadius) {
      this.ai1StartAttack();
      return;
    }
    if (!this.ai1Strafing) {
      this.ai1Tick = 0;                // decide on the first frame back in the band
      return;
    }
    this.ai1Tick -= dt;
    if (this.ai1Tick > 0) return;
    this.ai1Tick = ai.decisionSeconds;
    // a. still recoiling -> skip the tick
    if (this.deflectTimer > 0 || this.staggerTimer > 0) return;
    // b. R6 guard trigger: the player's swing in windup / strike (not
    // recover) or a cast windup, inside guardRespondRadius; one roll per tick
    var stage = P && P.attacking ? P.getAttackStage() : null;
    if (P && dist < ai.guardRespondRadius &&
        (stage === 'windup' || stage === 'strike' || playerCasting(P)) &&
        Math.random() < ai.guardChance) {
      this.ai1GuardActive = true;
      this.ai1GuardT = 0;
      this.ai1Press = false;
      return;
    }
    // c. R5 opening: guard broken, or the player recovering inside reach,
    // or the attack bias roll. Out of reach it presses (closes in) first.
    var opening = !!P && (P.guardBroken ||
      (dist <= ai.attackRadius && P.attacking && P.getAttackStage() === 'recover'));
    if (opening || Math.random() < ai.attackBias) {
      if (dist <= ai.attackRadius) this.ai1StartAttack();
      else this.ai1Press = true;
    }
    // d. otherwise keep circling (update steers the orbit / spacing)
  };

  // AI1 R7: lower the guard; the orbit flips and the loop decides at once
  Enemy.prototype.ai1DropGuard = function () {
    this.ai1GuardActive = false;
    this.ai1GuardT = 0;
    this.ai1Orbit = -this.ai1Orbit;
    this.ai1FlipT = 0;
    this.ai1Tick = 0;
  };

  // AI1: enter the existing attack phase FSM exactly as the chase branch
  // does; the orbit flips after each attack (R3).
  Enemy.prototype.ai1StartAttack = function () {
    this.ai1Press = false;
    this.ai1Orbit = -this.ai1Orbit;
    this.ai1FlipT = 0;
    this.setFsm('attack');
    this.attackPhase = 'windup';
    this.attackPhaseT = 0;
  };

  // v6: parry stagger. Cancels the current attack state entirely (bandit and
  // ghoul share this base class), locks the enemy in place for the duration,
  // and arms the riposte flag on the next player hit.
  Enemy.prototype.enterStagger = function (duration) {
    this.ai1GuardActive = false;         // AI1 R7: stagger always clears guard
    this.riposteStaggerTimer = duration;
    this.riposteArmed = true;
    this.hopTimer = -1;                  // cancel any mid-hop lunge
    this.attackPhase = 'idle';          // combat-ds1 P0-6: no phase leaks after parry
    this.attackPhaseT = 0;
    this.setFsm('stagger');
  };

  // Order D: a blocked / parried swing visibly bounces off the shield. The
  // attack FSM timing is untouched (presentation + a small CONFIG pushback):
  // for deflectEnemyRecoilSec the body twists toward its weapon side and
  // leans back, the weapon knocks outward, and the root slides away.
  Enemy.prototype.deflect = function (fromPos) {
    if (this.fsm === 'dead') return;
    this.ai1GuardActive = false;         // AI1 R7: deflect always clears guard
    this.deflectTimer = window.WH_CONFIG.block.deflectEnemyRecoilSec;
    var dx = this.pos.x - fromPos.x;
    var dz = this.pos.z - fromPos.z;
    var d = Math.sqrt(dx * dx + dz * dz);
    this.deflectDir = d > 0.001 ? { x: dx / d, z: dz / d } : { x: 0, z: 0 };
  };

  // Writes body rotation = base + recoil offset (absolute, so it never
  // accumulates) and the hand-held axe knock. Offsets are 0 once the timer ends.
  // pivotFresh: the stand-in weaponPivot was re-posed this frame (additive ok).
  Enemy.prototype.applyDeflectPose = function (baseX, baseY, pivotFresh) {
    var B = window.WH_CONFIG.block;
    var k = this.deflectTimer > 0 ? this.deflectTimer / B.deflectEnemyRecoilSec : 0;
    var env = smooth(Math.min(1, k));          // snaps on at contact, eases out
    var deg = Math.PI / 180;
    if (this.body) {
      // facing is local +Z: -rotation.y swings the right (weapon) side back,
      // -rotation.x tips the head backward
      this.body.rotation.y = baseY - B.deflect.yawDeg * deg * env;
      this.body.rotation.x = baseX - B.deflect.leanBackDeg * deg * env;
    }
    var knock = B.deflect.weaponKnockDeg * deg * env;
    if (this.heldAxe && this.heldAxeBaseQuat) {
      this.heldAxe.quaternion.copy(this.heldAxeBaseQuat);
      if (knock) {
        this.heldAxe.quaternion.premultiply(new THREE.Quaternion().setFromAxisAngle(
          new THREE.Vector3(1, 0, 0), knock));   // about hand-local X
      }
    } else if (this.weaponPivot && pivotFresh) {
      this.weaponPivot.rotation.y -= knock;
    }
  };

  Enemy.prototype.isStaggered = function () {
    return this.riposteStaggerTimer > 0;
  };

  Enemy.prototype.takeDamage = function (amount, fromDir) {
    // AI1 R7 (Nicko Q1): a raised guard takes ai1.guardDamageMult from its
    // front arc. Melee and firebolt both pass fromDir along attacker ->
    // enemy (the knockback below pushes along +fromDir), so the hit comes
    // FROM bearing -fromDir, measured against yaw with wrapAngle like hitYaw.
    if (this.ai1GuardActive && fromDir && this.cfg.ai1) {
      var guardYaw = wrapAngle(Math.atan2(-fromDir.x, -fromDir.z) - this.yaw);
      if (Math.abs(guardYaw) <= this.cfg.ai1.guardArcDeg * Math.PI / 180) {
        amount *= this.cfg.ai1.guardDamageMult;
      }
    }
    if (this.fsm === 'dead') return false;
    this.hp -= amount;
    // A hit cancels the swing (stagger or death): no phase leak, as in
    // enterStagger. The next attack entry re-arms windup.
    this.attackPhase = 'idle';
    this.attackPhaseT = 0;
    if (this.hp <= 0) {
      this.hp = 0;
      this.setFsm('dead');
      if (this.anim) this.anim.death();
      // stage 2: the one kill entry point (melee sweep + firebolt both land
      // here) - game.js stores the CONFIG.drops roll on the corpse (S4)
      if (Enemy.onKilled) Enemy.onKilled(this);
      return true;
    }
    if (this.anim) this.anim.hit();
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
  // others: [{pos: THREE.Vector3, radius: number}]. Only this enemy moves.
  // A non-finite distance (a NaN position written from outside) is skipped
  // so it cannot spread to every neighbour through the push.
  Enemy.prototype.separateFrom = function (others, strength, dt) {
    for (var i = 0; i < others.length; i++) {
      var o = others[i];
      var dx = this.pos.x - o.pos.x;
      var dz = this.pos.z - o.pos.z;
      var minDist = this.cfg.radius + o.radius;
      var d2 = dx * dx + dz * dz;
      if (!(d2 > 0 && d2 < minDist * minDist)) continue;
      var d = Math.sqrt(d2);
      var push = (minDist - d) * strength * dt;
      this.pos.x += (dx / d) * push;
      this.pos.z += (dz / d) * push;
    }
  };

  Enemy.onKilled = null;              // stage 2: fn(enemy), set by game.js (corpse loot)

  window.WH_Enemy = Enemy;
  window.WH_ENEMY_TYPES = ['bandit', 'ghoul'];
})();