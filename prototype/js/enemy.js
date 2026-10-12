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

  // CC-C7: a row carrying a brief-style `pattern` (rotmother / rotspawn) is
  // mapped ONCE onto the engine keys every FSM branch reads (hp -> hpMax,
  // dmg -> attackDamage, speed -> moveSpeed + chaseSpeed, aggro ->
  // sightRadius; boss-slam: slamRadius / slamArcDeg / slam* phase edges ->
  // attackRange + attackPhase). Every other row is returned as-is.
  var DERIVED = {};
  function deriveCfg(row) {
    var c = {};
    for (var k in row) c[k] = row[k];
    c.hpMax = row.hp;
    c.attackDamage = row.dmg;
    c.moveSpeed = row.speed;
    c.chaseSpeed = row.speed;          // brief: one speed (the slow lumber / the crawl)
    c.sightRadius = row.aggro;
    if (row.pattern === 'boss-slam') {
      c.attackRange = row.slamRadius;  // the AoE reach the active-entry check reads
      c.attackPhase = { windup: row.slamWindup, active: row.slamActive, recover: row.slamRecover,
        hitArcDeg: row.slamArcDeg / 2, trackDegPerSec: row.slamTrackDegPerSec };   // hitArcDeg = HALF-angle
    }
    return c;
  }

  function cfgFor(type) {
    var row = CFG[type];
    if (!row) return CFG.bandit;
    if (!row.pattern) return row;
    return DERIVED[type] || (DERIVED[type] = deriveCfg(row));
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

  // CC-C5 NIGHT BOLDNESS: the landed clock's phase only (no new state)
  function isNight() {
    var dn = window.WH_GAME ? window.WH_GAME.dayNight : null;
    return !!dn && dn.phase === 'night';
  }

  // Sight radius this frame: x nightBoldnessMult at night for a type that
  // carries one (wolf); every other type reads cfg.sightRadius unchanged.
  function sightFor(enemy) {
    var m = enemy.cfg.nightBoldnessMult;
    return m && isNight() ? enemy.cfg.sightRadius * m : enemy.cfg.sightRadius;
  }

  // CC-C5: type -> manifest body (CONFIG.enemy.bodyByType; unknown -> the
  // old ternary's ghoulBody). region-manager buildRegion reads it too.
  function bodyNameFor(type) {
    return (CFG.bodyByType && CFG.bodyByType[type]) || 'ghoulBody';
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
    // DAGBLEED: null | { dps, ticks, next } - damage per second, ticks left,
    // seconds to the next tick (set by game.applyBleedToEnemy; transient)
    this.bleed = null;
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
    // CC-C5: live-enemy ground feed (guard per home region: A/B have no
    // heightfield, so their pos.y / root y stay exactly as before)
    this.terrainHome = !!(window.WH_GROUND && window.WH_GROUND.has(homeRegionId));
    // CC-C5 pack state (DERIVED by WH_Enemy.buildPacks at region build,
    // never persisted; null / false for every non-pack enemy)
    this.pack = null;                  // the pack record this member belongs to
    this.packGoal = null;              // { x, z, speed, gain } patrol slot / regroup / anchor
    this.packRegroup = false;          // beyond leashFromCentroid: running back, refuses pulls
    // CC-C7 rot nest (null / 0 for every other enemy): slam cooldown, the
    // mother's per-build lair record (nest, spawner, dressing), the spawn's
    // master, and the RIGID_CLIPS placeholder player (setBody)
    this.slamCd = 0;
    this.lair = this.cfg.pattern === 'boss-slam' && this.cfg.lair ? newLair(this.cfg) : null;
    this.master = null;
    this.withered = false;             // died with its master (no kill: no loot / XP)
    this.rigidAnim = null;
  }

  // CC-C5: the home region's ground under the enemy (0 off-terrain)
  Enemy.prototype.groundY = function () {
    return this.terrainHome ? window.WH_GROUND.heightAt(this.homeRegionId, this.pos.x, this.pos.z) : 0;
  };

  Enemy.prototype.setBody = function (meshRoot) {
    if (this.body) this.yawFrame.remove(this.body);
    var bodyName = bodyNameFor(this.type);
    // CC-C7: a row with a literal `scale` (rot bodies) overrides the
    // height-normalized holder scale of region-manager buildRegion / makeBody
    // (same pin law: holder y = -groundMinY x scale, so the feet stay on root)
    if (this.cfg.scale) {
      meshRoot.scale.setScalar(this.cfg.scale);
      meshRoot.position.y = -(window.WH_ASSETS.groundMinY(bodyName) * this.cfg.scale);
    }
    this.body = meshRoot;
    this.bodyBaseY = meshRoot.position.y || 0;
    this.bodyBaseRotX = meshRoot.rotation.x || 0;   // Order D deflect overlay base
    this.bodyBaseRotY = meshRoot.rotation.y || 0;
    this.bodyScale = meshRoot.scale.x;               // CC-C7: RIGID_CLIPS grow base
    this.yawFrame.add(this.body);
    // CC-C7: an unrigged body (0 clips) of a type with a RIGID_CLIPS row
    // plays the placeholder set; everything else keeps the old paths
    this.rigidAnim = !window.WH_ASSETS.getClips(bodyName).length && CFG.rigidAnimByType &&
      CFG.rigidAnimByType[this.type] && window.WH_RigidAnim ?
      new window.WH_RigidAnim(CFG.rigidAnimByType[this.type]) : null;
    if (window.WH_ASSETS.getClips(bodyName).length) {
      // 10-05: ghouls play the Mixamo zombie set, bandits the Mixamo axe set.
      // CC-C5: wolves the WH_Wolf_* set (CONFIG.enemy.animVariantByType;
      // unknown types keep the old 'bandit' fallback).
      this.anim = new window.WH_CharacterAnim(meshRoot, window.WH_ASSETS.getClips(bodyName),
        { variant: (CFG.animVariantByType && CFG.animVariantByType[this.type]) || 'bandit' });
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
    // CC-C5: a corpse restored by a region rebuild never ran a live update -
    // stand it on its ground before it is posed / measured (A/B: never)
    if (this.terrainHome && this.corpseFinalY === null) this.pos.y = this.groundY();
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
        this.root.position.y = 0;      // measure the body offset over a y = 0 root
        this.root.updateMatrixWorld(true);
        var finalMinY = new THREE.Box3().setFromObject(this.root).min.y;
        // CC-C4 y-feed: the corpse settles on its region's ground (A/B: + 0)
        var G = window.WH_GROUND;
        var groundY = G && G.has(this.homeRegionId) ? G.heightAt(this.homeRegionId, this.pos.x, this.pos.z) : 0;
        this.corpseFinalY = (isFinite(finalMinY) ? -finalMinY + 0.01 : 0) + groundY;
      }
      if (this.corpseFinalY !== null) {
        this.root.position.y = this.corpseFinalY;
        this.deadFall = 1;
      }
      return;
    }
    if (this.corpseFinalY === null) {
      this.root.position.copy(this.pos);
      this.root.position.y = 0;          // CC-C5: measure over y = 0 (pos.y = ground in C)
      this.yawFrame.rotation.y = this.yaw;
      if (this.rigidAnim) {
        // CC-C7: drop the RIGID_CLIPS pose (feet-pivot shift, sway, grow)
        // and the slam cue before the fall is measured
        this.body.position.x = 0;
        this.body.position.z = 0;
        this.body.rotation.z = 0;
        this.body.scale.setScalar(this.bodyScale);
        this.slamCueShow(0, 0);
      }
      this.body.position.y = this.bodyBaseY || 0;
      this.body.rotation.set(-Math.PI / 2, 0, 0);
      // Include the equipped axe: the validation box spans the whole corpse.
      var minY = new THREE.Box3().setFromObject(this.root).min.y;
      // A root translation has the opposite sign to the measured minimum.
      // CC-C5: + the ground term (A/B: pos.y 0), as the rigged path above.
      this.corpseFinalY = (isFinite(minY) ? -minY + 0.01 : 0) + this.pos.y;
    }
    if (this.settleTime < 0 && this.deadFall >= 1) this.settleTime = 0;
    if (this.settleTime < 0) {
      this.deadFall = Math.min(1, this.deadFall + dt * 2.5);
      this.body.rotation.x = -this.deadFall * Math.PI / 2;
      // CC-C5: falls from its ground (A/B: pos.y 0 = deadFall x corpseFinalY)
      this.root.position.y = this.pos.y + this.deadFall * (this.corpseFinalY - this.pos.y);
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
    // CC-C7: the nest runs whether she lives or not (save-flag sync, 3-day
    // re-arm, spawner, dressing) - before the dead early-out below
    if (this.lair && regionManager) this.lairTick(dt, playerPos, playerAlive, regionManager);
    if (this.fsm === 'dead') {
      this.updateDeathVisual(dt);
      return;
    }
    this.fsmTime += dt;
    if (this.slamCd > 0) this.slamCd = Math.max(0, this.slamCd - dt);   // CC-C7 (boss-slam only)
    // DAGBLEED: bleed ticks (CONFIG.combat.bleed.tickSec) go through
    // takeDamage so the hit feedback + death/corpse flow fire as for any hit
    // (no fromDir: no knockback, no guard arc). A lethal tick ends the update.
    if (this.bleed) {
      var BL = window.WH_CONFIG.combat.bleed;
      this.bleed.next -= dt;
      if (this.bleed.next <= 0) {
        var tickDmg = this.bleed.dps * BL.tickSec;
        this.bleed.ticks -= 1;
        this.bleed.next += BL.tickSec;
        if (this.bleed.ticks <= 0) this.bleed = null;
        if (this.takeDamage(tickDmg, null)) return;
      }
    }
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
    var sight = sightFor(this);          // CC-C5: x nightBoldnessMult at night (wolf)

    // ---- transitions ----
    // v6: parry stagger. Full lockdown while riposteStaggerTimer runs: no FSM
    // transitions, no movement, no attacks, no turn. Return to chase (or idle
    // if the player is far) when it expires.
    if (this.riposteStaggerTimer > 0) {
      this.riposteStaggerTimer = Math.max(0, this.riposteStaggerTimer - dt);
      if (this.riposteStaggerTimer <= 0) {
        this.setFsm(distToPlayer <= sight ? 'chase' : 'idle');
      } else {
        // decay bob so the layered cycle does not freeze mid-pose
        this.bobPhase += dt * 3;
        // Order D: frozen stance (no walk-in-place on the clip) + recoil
        this.animMoveSpeed = 0;
        if (this.body) {
          this.root.position.x = this.pos.x;
          this.root.position.z = this.pos.z;
          // CC-C5: the recoil slides over the hills (terrain homes only)
          if (this.terrainHome) this.root.position.y = this.pos.y = this.groundY();
          if (this.rigidAnim) {
            // CC-C7: frozen upright - drop the RIGID_CLIPS feet-pivot shift
            this.body.position.set(0, this.bodyBaseY || 0, 0);
            this.body.rotation.z = 0;
            this.body.scale.setScalar(this.bodyScale);
            if (this.lair) this.updateSlamCue(dt);
          }
          this.applyDeflectPose(this.anim ? this.bodyBaseRotX : 0,
            this.anim ? this.bodyBaseRotY : 0);
        }
        return;              // frozen: no transitions, no movement, no attacks
      }
    }
    if (this.fsm === 'stagger') {
      // CC-C5: a regrouping pack member shrugs the hit off and keeps running
      // to its pack (solo-pull refusal); everyone else chases as before
      if (this.fsmTime >= this.cfg.staggerTime) this.setFsm(this.packRegroup ? 'idle' : 'chase');
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
            // CC-C7 boss-slam: the same check IS the AoE (attackRange =
            // slamRadius 3.2, half-angle 90 = the 180-deg front arc).
            var inArc = distToPlayer <= this.cfg.attackRange + window.WH_CONFIG.player.radius &&
                Math.abs(hitYaw) <= phase.hitArcDeg * Math.PI / 180;
            var slamP = this.cfg.slamCooldown ? livePlayer() : null;
            var hpBefore = slamP ? slamP.hp : 0;
            if (inArc) {
              canDamagePlayer(this.cfg.attackDamage, this);
            }
            if (this.cfg.slamCooldown) this.slamImpact(inArc, slamP, hpBefore, toPlayerX, toPlayerZ, distToPlayer);
          }
        } else if (this.attackPhase === 'active') {
          if (this.attackPhaseT >= phase.active) {
            this.attackPhase = 'recover';
            this.attackPhaseT = 0;
          }
        } else if (this.attackPhase === 'recover' && this.attackPhaseT >= phase.recover) {
          // AI1: one swing per decision - the bandit returns to the loop
          // CC-C7: a slammer never chains - back to the lumber chase while
          // slamCooldown runs (brief sec 3: slow chase between heavy slams)
          if (!ai1 && !this.cfg.slamCooldown && distToPlayer <= this.cfg.attackRange * 1.4) {
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
      // CC-C5: nobody solo-pulls - a regrouping pack member refuses every pull
      var canPull = !this.packRegroup;
      if (canPull && playerAlive && distToPlayer <= sight) {
        this.setFsm('aggro');            // idle/aggro both walk home below
      }
      if (canPull && playerAlive && distToPlayer <= sight * 0.8) {
        this.setFsm('chase');
      }
      if (ai1) {
        this.ai1Press = false;
        this.ai1GuardActive = false;   // disengaged: no posture left raised
        // AI1 R2: inside alwaysKnowsRadius the bandit engages even in darkness
        if (canPull && playerAlive && distToPlayer < ai1.alwaysKnowsRadius) this.setFsm('chase');
      }
    } else if (this.fsm === 'chase') {
      if (!playerAlive || distToPlayer > this.cfg.leashRadius || distToSpawn > this.cfg.leashRadius) {
        this.setFsm('idle');           // leash: disengage, walk home
      } else if (ai1) {
        this.ai1Decide(dt, ai1, distToPlayer);
      } else if (distToPlayer <= (this.cfg.engageRange || this.cfg.attackRange) && !(this.slamCd > 0) &&
                 !(this.rigidAnim && this.rigidAnim.riseT >= 0)) {
        // CC-C7: engageRange (boss-slam) starts the slam inside the AoE;
        // slamCd gates the cadence (0 for every other type: unchanged); a
        // rot body still rising (spare clip) cannot swing yet
        // v3: ghoul telegraphs the strike with a short forward hop
        // CC-C7: + any type with cfg.lunge (rot spawn's tiny lunge)
        if ((this.type === 'ghoul' || this.cfg.lunge) && ANIM.ghoulHop.duration > 0) {
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
      if (this.packGoal) {
        // CC-C5: a pack member walks its patrol slot (eased: no stop-go),
        // runs to the centroid while regrouping, or walks to the hunt anchor
        // (goals written by WH_Enemy.updatePacks before this update)
        var g = this.packGoal;
        var gdx = g.x - this.pos.x, gdz = g.z - this.pos.z;
        var gd = Math.sqrt(gdx * gdx + gdz * gdz);
        if (gd > 0.3) {
          moveSpeed = g.gain ? Math.min(g.speed, gd * g.gain) : g.speed;
          dirX = gdx / gd;
          dirZ = gdz / gd;
        }
      } else if (distToSpawn > 0.5) {
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
    // CC-C5 LIVE-ENEMY GROUND FEED (deferred from CC-C4): a terrain home
    // stands the enemy on its ground (pos.y, like the player's y-feed, so the
    // HP bar / lock reticle ride it too); A/B never write it (stays 0).
    if (this.terrainHome) this.pos.y = this.groundY();

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
        // CC-C5: + the ground term (A/B: pos.y 0). The body pin (holder y =
        // -groundMinY x scale) seats the paws / feet ON the root, and this
        // path returns before the idle re-level below: no double apply.
        this.root.position.y = hopYAnim + this.pos.y;
        this.applyDeflectPose(this.bodyBaseRotX, this.bodyBaseRotY);
        return;
      }
      this.body.rotation.y = 0;
      // CC-C7: unrigged rot bodies play the RIGID_CLIPS placeholder set
      // (their own pose + feet pivot; no layered cycle, no idle re-level)
      if (this.rigidAnim) {
        this.applyRigidPose(dt, moveSpeed);
        return;
      }
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
        this.root.position.y = hopY + eBob * 0.4 + this.pos.y;   // CC-C5 ground term (A/B 0)
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
      // CC-C5: re-level onto the SAME ground term (pos.y; A/B 0 = as before),
      // not onto y = 0 - else a stand-in on a hill would be pulled under it.
      if (this.fsm === 'idle' && this.hopTimer < 0) {
        var idleMinY = new THREE.Box3().setFromObject(this.root).min.y;
        if (isFinite(idleMinY)) this.root.position.y -= idleMinY - this.pos.y;
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
      if (this.lungeSlotFree()) this.ai1StartAttack();
      else this.ai1Press = false;      // CC-C5 relay: no slot - back to the orbit
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
      if (!this.lungeSlotFree()) return;   // CC-C5 relay: keep circling until a slot frees
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
    // CC-C7: superArmor (Rot Mother) keeps the swing through a hit
    if (!this.cfg.superArmor) {
      this.attackPhase = 'idle';
      this.attackPhaseT = 0;
    }
    if (this.hp <= 0) {
      this.hp = 0;
      this.attackPhase = 'idle';         // CC-C7: death ends a superArmor swing too
      this.attackPhaseT = 0;
      this.bleed = null;                 // DAGBLEED: death clears the bleed
      this.setFsm('dead');
      if (this.anim) this.anim.death();
      // CC-C7: the nest clears (save flag + day) and her spawn wither
      if (this.lair) this.lairOnDeath();
      // stage 2: the one kill entry point (melee sweep + firebolt both land
      // here) - game.js stores the CONFIG.drops roll on the corpse (S4)
      if (Enemy.onKilled) Enemy.onKilled(this);
      return true;
    }
    if (this.anim) this.anim.hit();
    // v3: hit stagger visual (0.15s lean-back + knockback)
    this.staggerTimer = ANIM.stagger.visualDuration;
    // CC-C7 superArmor: the flinch visual only - no knockback, no stagger
    // state (damage itself went through unchanged above)
    if (this.cfg.superArmor) return false;
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

  // ---- CC-C5 WOLF PACKS (doc 62 sec 5.1) ------------------------------------
  // Contained here (no new script file: index.html stays untouched). A pack =
  // the alive enemies whose CONFIG row carries its packId, on a closed
  // waypoint loop (CONFIG.enemy.wolfPacks). Pack FSM: patrol / regroup / hunt.
  // Everything below is DERIVED at buildRegion from the alive / dead list and
  // otherwise ephemeral: region persistence only stores the dead, so a
  // partial kill + region swap (or save / load) rebuilds packs of survivors.

  // Closed loop: points, cumulative arc length per vertex, total length.
  function makeLoop(points) {
    var cum = [0], total = 0;
    for (var i = 0; i < points.length; i++) {
      var a = points[i], b = points[(i + 1) % points.length];
      total += Math.sqrt((b[0] - a[0]) * (b[0] - a[0]) + (b[1] - a[1]) * (b[1] - a[1]));
      cum.push(total);
    }
    return { pts: points, cum: cum, total: total };
  }

  // Point + unit travel direction at arc length s (wraps both ways).
  function loopAt(loop, s) {
    var n = loop.pts.length;
    s = ((s % loop.total) + loop.total) % loop.total;
    var i = 0;
    while (i < n - 1 && loop.cum[i + 1] <= s) i++;
    var a = loop.pts[i], b = loop.pts[(i + 1) % n];
    var len = loop.cum[i + 1] - loop.cum[i];
    var t = len > 0 ? (s - loop.cum[i]) / len : 0;
    var tx = len > 0 ? (b[0] - a[0]) / len : 0, tz = len > 0 ? (b[1] - a[1]) / len : 1;
    return { x: a[0] + (b[0] - a[0]) * t, z: a[1] + (b[1] - a[1]) * t, tx: tx, tz: tz };
  }

  // Arc length of the loop point nearest (x, z).
  function loopProject(loop, x, z) {
    var n = loop.pts.length, best = Infinity, bestS = 0;
    for (var i = 0; i < n; i++) {
      var a = loop.pts[i], b = loop.pts[(i + 1) % n];
      var len = loop.cum[i + 1] - loop.cum[i];
      if (!(len > 0)) continue;
      var tx = (b[0] - a[0]) / len, tz = (b[1] - a[1]) / len;
      var t = Math.max(0, Math.min(len, (x - a[0]) * tx + (z - a[1]) * tz));
      var px = a[0] + tx * t - x, pz = a[1] + tz * t - z;
      var d2 = px * px + pz * pz;
      if (d2 < best) { best = d2; bestS = loop.cum[i] + t; }
    }
    return bestS;
  }

  // Patrol slot of rank r behind the lead at arc length s: rank x
  // slotSpacingM back along the loop, odd ranks slotLateralM to the right
  // of travel, even ranks (> 0) to the left (rank 0 rides the line).
  function packSlot(loop, s, rank, P) {
    var q = loopAt(loop, s - rank * P.slotSpacingM);
    var side = rank === 0 ? 0 : (rank % 2 ? 1 : -1) * P.slotLateralM;
    return { x: q.x - q.tz * side, z: q.z + q.tx * side };
  }

  function packEngaged(e) {
    return e.fsm === 'chase' || e.fsm === 'attack' || e.fsm === 'stagger';
  }

  // buildRegion: enemies[i] was spawned from rows[i]. Returns the region's
  // packs (alive members only, ranked by row waypointPhase), [] for A/B.
  Enemy.buildPacks = function (enemies, rows, regionId) {
    var packs = [];
    (CFG.wolfPacks || []).forEach(function (def) {
      if (def.regionId !== regionId) return;
      var ranked = [];
      for (var i = 0; i < enemies.length; i++) {
        if (rows[i] && rows[i].packId === def.id && enemies[i].fsm !== 'dead') {
          ranked.push({ e: enemies[i], phase: rows[i].waypointPhase || 0 });
        }
      }
      if (!ranked.length) return;
      ranked.sort(function (a, b) { return a.phase - b.phase; });
      var members = ranked.map(function (r) { return r.e; });
      var pack = { id: def.id, def: def, P: members[0].cfg.pack || CFG.wolf.pack, loop: makeLoop(def.waypoints),
        members: members, mode: 'patrol', s: 0, anchor: null, cx: 0, cz: 0, alive: members.length };
      members.forEach(function (e) {
        e.pack = pack;
        e.packGoal = { x: e.pos.x, z: e.pos.z, speed: 0, gain: 0 };
        e.packRegroup = false;
      });
      // the lead slot starts so the survivors' slots straddle their centroid
      var cx = 0, cz = 0;
      members.forEach(function (e) { cx += e.pos.x; cz += e.pos.z; });
      pack.s = loopProject(pack.loop, cx / members.length, cz / members.length) +
        (members.length - 1) / 2 * pack.P.slotSpacingM;
      packs.push(pack);
    });
    return packs;
  };

  function updatePack(pack, dt) {
    var P = pack.P, alive = [], i, e;
    for (i = 0; i < pack.members.length; i++) {
      if (pack.members[i].fsm !== 'dead') alive.push(pack.members[i]);
    }
    pack.alive = alive.length;
    if (!alive.length) { pack.mode = 'gone'; return; }
    var cx = 0, cz = 0;
    for (i = 0; i < alive.length; i++) { cx += alive[i].pos.x; cz += alive[i].pos.z; }
    cx /= alive.length;
    cz /= alive.length;
    pack.cx = cx;
    pack.cz = cz;

    // PACK-PULLS-PACK (binding): the first member in combat (a regrouping
    // straggler never counts) pulls every alive member within packAggroSpread
    // onto the same target. The hunt anchor (leash origin) = the lead slot's
    // loop point, so a hunt never drags the pack beyond leashRadius of its loop.
    var trigger = null;
    for (i = 0; i < alive.length; i++) {
      if (packEngaged(alive[i]) && !alive[i].packRegroup) { trigger = alive[i]; break; }
    }
    if (trigger && pack.mode !== 'hunt') {
      var home = loopAt(pack.loop, pack.s);
      pack.mode = 'hunt';
      pack.anchor = { x: home.x, z: home.z };
      for (i = 0; i < alive.length; i++) {
        e = alive[i];
        e.spawn.x = home.x;
        e.spawn.z = home.z;
        e.packRegroup = false;
        var tdx = e.pos.x - trigger.pos.x, tdz = e.pos.z - trigger.pos.z;
        if (!packEngaged(e) && tdx * tdx + tdz * tdz <= P.packAggroSpread * P.packAggroSpread) {
          e.setFsm('chase');
        }
      }
    } else if (!trigger && pack.mode === 'hunt') {
      // the hunt is over (leashed / player dead / gone): resume the loop
      // where the pack stands (slots straddle the centroid again)
      pack.mode = 'patrol';
      pack.anchor = null;
      pack.s = loopProject(pack.loop, cx, cz) + (alive.length - 1) / 2 * P.slotSpacingM;
    }

    if (pack.mode === 'hunt') {
      // members out of the fight walk back to the hunt anchor
      for (i = 0; i < alive.length; i++) {
        e = alive[i];
        e.packGoal.x = pack.anchor.x;
        e.packGoal.z = pack.anchor.z;
        e.packGoal.speed = e.cfg.moveSpeed;
        e.packGoal.gain = 0;
      }
      return;
    }

    // PATROL / REGROUP: cohesion around the alive centroid, then the slots
    var regroup = false, hold = false;
    for (i = 0; i < alive.length; i++) {
      e = alive[i];
      var dcx = e.pos.x - cx, dcz = e.pos.z - cz;
      var dc = Math.sqrt(dcx * dcx + dcz * dcz);
      if (dc > P.leashFromCentroid) e.packRegroup = true;
      else if (dc <= P.regroupRadius) e.packRegroup = false;
      if (e.packRegroup) {
        regroup = true;
        e.packGoal.x = cx;
        e.packGoal.z = cz;
        e.packGoal.speed = e.cfg.chaseSpeed;    // Run back to the pack
        e.packGoal.gain = 0;
        continue;
      }
      var slot = packSlot(pack.loop, pack.s, i, P);
      var sdx = slot.x - e.pos.x, sdz = slot.z - e.pos.z;
      if (sdx * sdx + sdz * sdz > P.slotHoldM * P.slotHoldM) hold = true;
      e.packGoal.x = slot.x;
      e.packGoal.z = slot.z;
      e.packGoal.speed = e.cfg.moveSpeed;       // Walk the loop
      e.packGoal.gain = P.slotGain;
    }
    pack.mode = regroup ? 'regroup' : 'patrol';
    // the lead slot waits for stragglers / regroupers, else walks the loop
    if (!regroup && !hold) pack.s += alive[0].cfg.moveSpeed * P.patrolPace * dt;
    // leash origin rides the lead slot while the pack is not hunting
    var lead = loopAt(pack.loop, pack.s);
    for (i = 0; i < alive.length; i++) {
      alive[i].spawn.x = lead.x;
      alive[i].spawn.z = lead.z;
    }
  }

  // Once per frame from region-manager updateEnemies, BEFORE the members'
  // own updates (they read packGoal / packRegroup / spawn this frame).
  Enemy.updatePacks = function (packs, dt) {
    if (!packs) return;
    for (var i = 0; i < packs.length; i++) updatePack(packs[i], dt);
  };

  // RELAY LUNGE: a pack member may start a lunge only while fewer than
  // pack.membersInFlight packmates are in windup / snap (the rest orbit in
  // the strafe band until a slot frees). Members update in order and read
  // live fsm, so a lunge started this frame already counts. Non-pack: free.
  Enemy.prototype.lungeSlotFree = function () {
    var pack = this.pack;
    if (!pack) return true;
    var n = 0;
    for (var i = 0; i < pack.members.length; i++) {
      var m = pack.members[i];
      if (m !== this && m.fsm === 'attack' &&
          (m.attackPhase === 'windup' || m.attackPhase === 'active')) n++;
    }
    return n < pack.P.membersInFlight;
  };

  // ---- CC-C7 ROT MOTHER NEST (doc 62 sec 5.2, R-62.4) -----------------------
  // io/missions/2026-10-12-cc-c7-rotmother-behavior.md. Contained here like
  // the packs (no new script file). The mother is an ordinary CONFIG row
  // (CC-C8: regionD.lairs, built after the den's enemy rows); her lair
  // record is per build, the CLEARED flag is
  // module state persisted through the additive save block 'lairs'
  // ({ rotmother_cleared_<region>: dayOfDeath }, game.js save hooks). Her rot
  // spawn are runtime enemies appended to the region list after every row
  // (never CONFIG rows, never restored: a rebuild starts them from zero).

  var LAIR_STATE = {};                 // region letter -> { cleared, day }

  function lairFlag(letter) { return 'rotmother_cleared_' + letter; }

  function gameDay() {
    var dn = window.WH_GAME ? window.WH_GAME.dayNight : null;
    return dn ? dn.day : 0;
  }

  // brief lair { x, y, region } = region-local (x, z) in CONFIG['region' +
  // region]. CC-C8: re-homed to 'D' (the den); letter = the SAVE-key letter
  // (lair.flag, 'C': rotmother_cleared_C stays byte-equal across the move)
  function lairNest(cfg) {
    var R = window.WH_CONFIG['region' + cfg.lair.region];
    return { x: R.center.x + cfg.lair.x, z: R.center.z + cfg.lair.y,
      letter: cfg.lair.flag || cfg.lair.region, regionId: R.id, dress: R.rotLair || null };
  }

  function newLair(cfg) {
    return { nest: lairNest(cfg), built: false, entered: false, spawnT: 0,
      minions: [], group: null, fog: [], cue: null, cueFlash: 0 };
  }

  // Save flag sync + 3-day re-arm + minion spawner + dressing, every frame of
  // the active region (alive or dead).
  Enemy.prototype.lairTick = function (dt, playerPos, playerAlive, rm) {
    var L = this.lair, N = L.nest, cfg = this.cfg;
    if (!L.built && this.root.parent) this.buildLair();
    var st = LAIR_STATE[N.letter];
    var dx = playerPos.x - N.x, dz = playerPos.z - N.z;
    var dNest = Math.sqrt(dx * dx + dz * dz);
    if (this.fsm === 'dead') {
      if (!st || !st.cleared) {
        // the profile says she lives (LOAD of a pre-kill save): stand her up
        this.revive(rm, false);
      } else if (gameDay() - st.day >= cfg.rearm.days &&
                 (!L.entered || dNest <= cfg.rearm.radius)) {
        // RE-ARM, once per cycle: first entry after day +3 (she is simply
        // back when the region builds) or the player within rearm.radius
        // while already here (she rises out of the nest). The next kill
        // re-rolls her loot (storeCorpseLoot rolls at every death).
        st.cleared = false;
        this.revive(rm, L.entered);
      }
    } else if (st && st.cleared) {
      // a cleared nest restored into a fresh build: her corpse, no kill
      this.hp = 0;
      this.attackPhase = 'idle';
      this.setFsm('dead');
      this.deadFall = 1;
    }
    L.entered = true;
    // MINION SPAWNER (brief sec 4): she lives + the player inside lairRadius
    // -> 1 rot spawn per interval from range m around her, cap alive
    var M = cfg.minions;
    var alive = 0;
    for (var i = 0; i < L.minions.length; i++) if (L.minions[i].fsm !== 'dead') alive++;
    if (this.fsm !== 'dead' && playerAlive && dNest <= cfg.lairRadius) {
      L.spawnT = Math.min(M.interval, L.spawnT + dt);
      if (L.spawnT >= M.interval && alive < M.cap && this.spawnMinion(rm, playerPos)) L.spawnT = 0;
    } else {
      L.spawnT = 0;
    }
    this.pruneMinions(dt, rm);
    this.lairDressingTick(dt, dNest);
  };

  // Death entry (takeDamage only - a restored corpse never runs it): flag +
  // day, then dieOnMasterDeath withers every live spawn (no kill: no loot /
  // XP, so a dying mother is not a minion piñata).
  Enemy.prototype.lairOnDeath = function () {
    var L = this.lair;
    LAIR_STATE[L.nest.letter] = { cleared: true, day: gameDay() };
    L.spawnT = 0;
    this.slamCd = 0;
    if (this.cfg.minions.dieOnMasterDeath) {
      for (var i = 0; i < L.minions.length; i++) {
        var m = L.minions[i];
        if (m.fsm === 'dead') continue;
        m.hp = 0;
        m.bleed = null;
        m.attackPhase = 'idle';
        m.withered = true;
        m.setFsm('dead');
      }
    }
  };

  // Stand the mother back up at the nest (re-arm / profile sync). rise =
  // play the RIGID_CLIPS spare (she grows out of the nest in view).
  Enemy.prototype.revive = function (rm, rise) {
    // unlooted loot rots away with the old corpse: hand it to a sink so the
    // corpse glow fades through the public loot path (never re-awarded)
    var CL = window.WH_GAME ? window.WH_GAME.corpseLoot : null;
    if (CL && this.corpseLoot && this.corpseLoot.length) {
      CL.loot(this, { addItem: function (id, n) { return n; } });
    }
    this.corpseLoot = null;
    this.hp = this.hpMax;
    this.setFsm('idle');
    this.attackPhase = 'idle';
    this.attackPhaseT = 0;
    this.deadFall = 0;
    this.corpseFinalY = null;
    this.settleTime = -1;
    this.staggerTimer = 0;
    this.riposteStaggerTimer = 0;
    this.riposteArmed = false;
    this.bleed = null;
    this.slamCd = 0;
    this.pos.set(this.spawn.x, 0, this.spawn.z);
    if (this.terrainHome) this.pos.y = this.groundY();
    if (this.body) {
      this.body.rotation.set(this.bodyBaseRotX, this.bodyBaseRotY, 0);
      this.body.position.set(0, this.bodyBaseY, 0);
      this.body.scale.setScalar(this.bodyScale);
      this.root.position.copy(this.pos);
    }
    if (rise && this.rigidAnim) this.rigidAnim.rise(this.cfg.riseSec);
    // the session dead mark (region-manager per-index state) goes too, so a
    // later rebuild of this region does not lay her down again
    var list = rm.enemies[this.homeRegionId] || [];
    var idx = list.indexOf(this);
    if (idx >= 0) delete rm.logic.stateFor(this.homeRegionId).enemies[idx];
  };

  // The region-manager buildRegion body steps for a runtime enemy (setBody
  // then applies the row scale + the holder pin).
  Enemy.makeBody = function (type) {
    var name = bodyNameFor(type);
    var body = window.WH_ASSETS.instance(name);
    body.children[0].position.y += window.WH_ASSETS.groundMinY(name);
    return body;
  };

  // One rot spawn, range m from her at a random bearing, facing the player.
  Enemy.prototype.spawnMinion = function (rm, playerPos) {
    var list = rm.enemies[this.homeRegionId];
    var parent = this.root.parent;
    if (!list || !parent) return false;
    var M = this.cfg.minions;
    var a = Math.random() * Math.PI * 2;
    var m = new Enemy(M.asset, null, this.homeRegionId,
      this.pos.x + Math.cos(a) * M.range, this.pos.z + Math.sin(a) * M.range);
    m.master = this;
    m.yaw = Math.atan2(playerPos.x - m.pos.x, playerPos.z - m.pos.z);
    m.setBody(Enemy.makeBody(M.asset));
    if (m.terrainHome) m.pos.y = m.groundY();
    m.root.position.copy(m.pos);
    m.yawFrame.rotation.y = m.yaw;
    if (m.rigidAnim) m.rigidAnim.rise(m.cfg.riseSec);
    list.push(m);
    parent.add(m.root);
    this.lair.minions.push(m);
    return true;
  };

  // Spawn corpses leave once looted / empty and corpseLingerSec dead, and
  // never more than maxCorpses lie around (oldest first; its unlooted loot
  // goes with it - corpse-loot drops a body that left the list).
  Enemy.prototype.pruneMinions = function (dt, rm) {
    var L = this.lair, list = rm.enemies[this.homeRegionId] || [];
    var dead = [], removed = false, i, m;
    for (i = 0; i < L.minions.length; i++) {
      m = L.minions[i];
      if (m.fsm !== 'dead') continue;
      m.deadT = (m.deadT || 0) + dt;
      dead.push(m);
    }
    var drop = [];
    for (i = 0; i < dead.length; i++) {
      m = dead[i];
      var empty = !m.corpseLoot || !m.corpseLoot.length;
      if ((empty && m.deadT >= m.cfg.corpseLingerSec) || dead.length - i > m.cfg.maxCorpses) drop.push(m);
    }
    for (i = 0; i < drop.length; i++) {
      m = drop[i];
      var at = list.indexOf(m);
      if (at >= 0) list.splice(at, 1);
      if (m.root.parent) m.root.parent.remove(m.root);   // shared template geometry: no dispose
      L.minions.splice(L.minions.indexOf(m), 1);
      removed = true;
    }
    if (removed) {
      // the per-index dead marks past the CONFIG rows belonged to spawn
      // (a rebuild never restores them); keep the session state tidy
      var hc = window.WH_REGION_DEFS.regions[this.homeRegionId].cfg;
      var rows = hc.enemies.length + (hc.lairs ? hc.lairs.length : 0);   // CC-C8: + the lair rows (her)
      var se = rm.logic.stateFor(this.homeRegionId).enemies;
      Object.keys(se).forEach(function (k) { if (Number(k) >= rows) delete se[k]; });
    }
  };

  // ---- nest dressing: rot-ground pool + fog cards (region group children,
  // disposed with the region like every prop); the rot-light is a static
  // socket (Enemy.lairSockets -> game.js light pool) ----
  function hashNoise(seed, x, y) {
    var h = (seed ^ (x * 374761393) ^ (y * 668265263)) | 0;
    h = Math.imul(h ^ (h >>> 13), 1274126177);
    return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
  }

  function hexRgb(c) { return [(c >> 16) & 255, (c >> 8) & 255, c & 255]; }

  // 64 px NEAREST canvas: dark swamp mottling + specks, alpha feathered to 0
  // at the rim in hard pixel steps (the pixel-art ground family)
  function poolCanvas(P) {
    var S = 64, cv = document.createElement('canvas');
    cv.width = cv.height = S;
    var g = cv.getContext('2d'), img = g.createImageData(S, S);
    var c1 = hexRgb(P.color), c2 = hexRgb(P.color2), c3 = hexRgb(P.speck);
    for (var y = 0; y < S; y++) {
      for (var x = 0; x < S; x++) {
        var u = (x + 0.5) / S * 2 - 1, v = (y + 0.5) / S * 2 - 1;
        var r = Math.sqrt(u * u + v * v);
        var n = hashNoise(P.textureSeed, x >> 1, y >> 1);
        var c = n < 0.08 ? c3 : (n < 0.5 ? c1 : c2);
        var edge = Math.max(0, Math.min(1, (1 - r) / P.edgeFeather));
        var o = (y * S + x) * 4;
        img.data[o] = c[0]; img.data[o + 1] = c[1]; img.data[o + 2] = c[2];
        img.data[o + 3] = Math.round(Math.round(edge * 4) / 4 * 235);   // 4 alpha steps
      }
    }
    g.putImageData(img, 0, 0);
    return cv;
  }

  function fogCanvas() {
    var S = 64, cv = document.createElement('canvas');
    cv.width = cv.height = S;
    var g = cv.getContext('2d');
    var grad = g.createRadialGradient(S / 2, S / 2, 0, S / 2, S / 2, S / 2);
    grad.addColorStop(0, 'rgba(255,255,255,0.9)');
    grad.addColorStop(0.5, 'rgba(255,255,255,0.35)');
    grad.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = grad;
    g.fillRect(0, 0, S, S);
    return cv;
  }

  // The rot-ground pool mesh at (cx, cz), params P (radius / segments /
  // rings / lift / colours / textureSeed / edgeFeather): center + rings x
  // segments, every vertex on the region's ground + lift. CC-C8: shared by
  // the nest (buildLair) and the outcrop stains (region-manager).
  function rotPoolMesh(rid, cx, cz, P) {
    var G = window.WH_GROUND;
    var hAt = function (x, z) { return G && G.has(rid) ? G.heightAt(rid, x, z) : 0; };
    var pos = [], uvs = [], idx = [];
    pos.push(cx, hAt(cx, cz) + P.lift, cz);
    uvs.push(0.5, 0.5);
    for (var r = 1; r <= P.rings; r++) {
      var rr = P.radius * r / P.rings;
      for (var s = 0; s < P.segments; s++) {
        var a = s / P.segments * Math.PI * 2;
        var x = cx + Math.cos(a) * rr, z = cz + Math.sin(a) * rr;
        pos.push(x, hAt(x, z) + P.lift, z);
        uvs.push(0.5 + (x - cx) / (2 * P.radius), 0.5 - (z - cz) / (2 * P.radius));
      }
    }
    for (s = 0; s < P.segments; s++) idx.push(0, 1 + (s + 1) % P.segments, 1 + s);
    for (r = 1; r < P.rings; r++) {
      var o0 = 1 + (r - 1) * P.segments, o1 = 1 + r * P.segments;
      for (s = 0; s < P.segments; s++) {
        var s1 = (s + 1) % P.segments;
        idx.push(o0 + s, o0 + s1, o1 + s, o0 + s1, o1 + s1, o1 + s);
      }
    }
    var geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(pos), 3));
    geo.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(uvs), 2));
    geo.setIndex(idx);
    geo.computeVertexNormals();
    var tex = new THREE.CanvasTexture(poolCanvas(P));
    tex.magFilter = THREE.NearestFilter;
    tex.minFilter = THREE.NearestFilter;
    tex.generateMipmaps = false;
    tex.colorSpace = THREE.SRGBColorSpace;
    var pool = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
      color: 0xffffff, map: tex, roughness: 0.85, metalness: 0.0,
      transparent: true, depthWrite: false, side: THREE.DoubleSide,
      polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1
    }));
    pool.name = 'rot-pool';
    return pool;
  }

  Enemy.prototype.buildLair = function () {
    var L = this.lair, N = L.nest, D = N.dress;
    L.built = true;
    if (!D || typeof document === 'undefined') return;
    var G = window.WH_GROUND, rid = this.homeRegionId;
    var hAt = function (x, z) { return G && G.has(rid) ? G.heightAt(rid, x, z) : 0; };
    var group = new THREE.Group();
    group.name = 'rot-lair';
    var P = D.pool;
    group.add(rotPoolMesh(rid, N.x, N.z, P));
    // fog cards: slow orbits around the nest, yaw-billboarded each frame
    var F = D.fog, fogTex = new THREE.CanvasTexture(fogCanvas());
    var fogGeo = new THREE.PlaneGeometry(F.width, F.height);
    var fogMat = new THREE.MeshBasicMaterial({ map: fogTex, color: F.color, transparent: true,
      opacity: F.opacity, depthWrite: false, side: THREE.DoubleSide });
    var baseY = hAt(N.x, N.z);
    for (var k = 0; k < F.cards; k++) {
      var card = new THREE.Mesh(fogGeo, fogMat);
      card.name = 'rot-fog';
      card.userData.orbit = {
        r: F.radiusMin + (F.radiusMax - F.radiusMin) * hashNoise(P.textureSeed, k, 1),
        a: Math.PI * 2 * k / F.cards,
        w: F.driftSpeed * (hashNoise(P.textureSeed, k, 2) < 0.5 ? -1 : 1) * (0.6 + 0.8 * hashNoise(P.textureSeed, k, 3)),
        h: F.heightMin + (F.heightMax - F.heightMin) * hashNoise(P.textureSeed, k, 4),
        ph: Math.PI * 2 * hashNoise(P.textureSeed, k, 5)
      };
      card.position.set(N.x, baseY + card.userData.orbit.h, N.z);
      group.add(card);
      L.fog.push(card);
    }
    L.fogBaseY = baseY;
    L.group = group;
    this.root.parent.add(group);
  };

  Enemy.prototype.lairDressingTick = function (dt, dNest) {
    var L = this.lair, D = L.nest.dress;
    if (!L.group || !D) return;
    L.group.visible = dNest <= D.cullM;
    // CC-C8: the green fog is hers like the light - gone while the nest is
    // cleared (the den is a black empty vault), back on the re-arm
    var st = LAIR_STATE[L.nest.letter], lit = !(st && st.cleared);
    for (var f = 0; f < L.fog.length; f++) L.fog[f].visible = lit;
    if (!lit || dNest > D.fog.showWithinM) return;
    var cam = window.WH_GAME ? window.WH_GAME.camera : null;
    var N = L.nest;
    for (var i = 0; i < L.fog.length; i++) {
      var c = L.fog[i], o = c.userData.orbit;
      o.a += o.w * dt;
      o.ph += dt * 0.7;
      c.position.set(N.x + Math.cos(o.a) * o.r, L.fogBaseY + o.h + Math.sin(o.ph) * 0.15,
        N.z + Math.sin(o.a) * o.r);
      if (cam) c.rotation.y = Math.atan2(cam.position.x - c.position.x, cam.position.z - c.position.z);
    }
  };

  // ---- the slam: telegraph cue (ground sector under the 180-deg arc) +
  // impact effects (poison-lite + knockback through game.js) ----
  var CUE_DARK = null, CUE_HOT = null;
  Enemy.prototype.buildSlamCue = function () {
    var R = this.cfg.slamRadius, half = this.cfg.slamArcDeg / 2 * Math.PI / 180;
    var SEG = 16, RINGS = 3, pos = [0, 0, 0], idx = [];
    for (var r = 1; r <= RINGS; r++) {
      for (var s = 0; s <= SEG; s++) {
        var a = -half + 2 * half * s / SEG;
        pos.push(Math.sin(a) * R * r / RINGS, 0, Math.cos(a) * R * r / RINGS);   // yawFrame local: +Z = her front
      }
    }
    for (s = 0; s < SEG; s++) idx.push(0, 1 + s, 2 + s);
    for (r = 1; r < RINGS; r++) {
      var o0 = 1 + (r - 1) * (SEG + 1), o1 = 1 + r * (SEG + 1);
      for (s = 0; s < SEG; s++) idx.push(o0 + s, o1 + s, o0 + s + 1, o0 + s + 1, o1 + s, o1 + s + 1);
    }
    var geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(pos), 3));
    geo.setIndex(idx);
    var cue = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: 0x101a08, transparent: true,
      opacity: 0, depthWrite: false, side: THREE.DoubleSide,
      polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 }));
    cue.name = 'rot-slam-cue';
    cue.visible = false;
    cue.frustumCulled = false;          // vertices are re-seated every frame it shows
    this.yawFrame.add(cue);
    this.lair.cue = cue;
    if (!CUE_DARK) { CUE_DARK = new THREE.Color(0x101a08); CUE_HOT = new THREE.Color(0xa8d84a); }
  };

  // heat 0..1 (dark shadow -> sickly green), opacity 0 hides it
  Enemy.prototype.slamCueShow = function (heat, opacity) {
    var cue = this.lair ? this.lair.cue : null;
    if (!cue) return;
    cue.visible = opacity > 0.01;
    if (!cue.visible) return;
    cue.material.opacity = opacity;
    cue.material.color.copy(CUE_DARK).lerp(CUE_HOT, heat);
    // seat every vertex on the ground under it (yawFrame local -> world)
    var G = window.WH_GROUND, rid = this.homeRegionId, terr = G && G.has(rid);
    var p = cue.geometry.attributes.position, arr = p.array;
    var c = Math.cos(this.yaw), sn = Math.sin(this.yaw), rootY = this.root.position.y;
    for (var i = 0; i < arr.length; i += 3) {
      var wx = this.pos.x + arr[i] * c + arr[i + 2] * sn;
      var wz = this.pos.z - arr[i] * sn + arr[i + 2] * c;
      arr[i + 1] = (terr ? G.heightAt(rid, wx, wz) : 0) - rootY + 0.1;
    }
    p.needsUpdate = true;
  };

  Enemy.prototype.updateSlamCue = function (dt) {
    if (!this.lair) return;
    if (!this.lair.cue) this.buildSlamCue();
    var L = this.lair;
    if (this.fsm === 'attack' && this.attackPhase === 'windup') {
      var f = Math.min(1, this.attackPhaseT / this.cfg.attackPhase.windup);
      this.slamCueShow(f * 0.6, 0.2 + 0.45 * f);
    } else if (this.fsm === 'attack' && this.attackPhase === 'active') {
      this.slamCueShow(1, 0.8);
    } else if (L.cueFlash > 0) {
      L.cueFlash = Math.max(0, L.cueFlash - dt);
      this.slamCueShow(1, 0.8 * L.cueFlash / 0.35);
    } else {
      this.slamCueShow(0, 0);
    }
  };

  // Active entry of a boss-slam (after the shared AoE check): cooldown,
  // cue flash, and - only on a slam that LANDED (hp dropped, no guard up,
  // not parried / rolled through) - poison-lite + knockback.
  Enemy.prototype.slamImpact = function (inArc, P, hpBefore, toX, toZ, dist) {
    this.slamCd = this.cfg.slamCooldown;
    if (this.lair) this.lair.cueFlash = 0.35;
    var G = window.WH_GAME;
    if (!inArc || !P || !G || !(P.hp < hpBefore) || P.blockActive) return;
    if (G.applyPlayerPoison) G.applyPlayerPoison(this.cfg.poison, this.cfg.poisonText);
    if (G.knockbackPlayer && dist > 0.001) {
      G.knockbackPlayer(toX / dist, toZ / dist, this.cfg.slamKnockbackM, this.cfg.slamKnockbackSec);
    }
  };

  // RIGID_CLIPS pose onto the body holder. The holder origin sits at the raw
  // mesh origin (bodyBaseY above the feet), so pitch is re-pivoted about the
  // FEET: shift = (0, -h (1 - cos), h sin) keeps the ground point planted.
  Enemy.prototype.applyRigidPose = function (dt, moveSpeed) {
    var pz = this.rigidAnim.pose(this, dt, moveSpeed);
    if (!pz) return;
    var hopY = 0;
    if (this.hopTimer >= 0) {
      var hf = this.hopTimer / ANIM.ghoulHop.duration;
      hopY = 4 * hf * (1 - hf) * ANIM.ghoulHop.height;
    }
    var h = (this.bodyBaseY || 0) * pz.grow;
    this.body.scale.setScalar(this.bodyScale * pz.grow);
    this.body.rotation.set(pz.rotX, pz.rotY, pz.rotZ);
    this.body.position.set(pz.swayX, h * Math.cos(pz.rotX), h * Math.sin(pz.rotX));
    this.root.position.y = this.pos.y + hopY + pz.lift;
    this.applyDeflectPose(this.body.rotation.x, this.body.rotation.y, true);
    if (this.lair) this.updateSlamCue(dt);
  };

  // Save block (game.js wraps WH_SAVE): { rotmother_cleared_C: dayOfDeath }
  // while cleared; an armed nest writes nothing. Restore REPLACES the state
  // (last save wins: a profile without the block = every nest armed).
  Enemy.captureLairs = function () {
    var out = {};
    Object.keys(LAIR_STATE).forEach(function (letter) {
      var st = LAIR_STATE[letter];
      if (st && st.cleared) out[lairFlag(letter)] = st.day;
    });
    return out;
  };
  Enemy.restoreLairs = function (block) {
    LAIR_STATE = {};
    if (!block || typeof block !== 'object') return;
    Object.keys(block).forEach(function (k) {
      var m = /^rotmother_cleared_([A-Z])$/.exec(k);
      var day = block[k];
      if (m && typeof day === 'number' && isFinite(day)) LAIR_STATE[m[1]] = { cleared: true, day: Math.floor(day) };
    });
  };

  // Rot-light sockets of the region's nests (game.js computeFireSockets:
  // the bandit-campfire socket pipeline, tinted, no flame card). CC-C8: the
  // light is HERS - none while the nest is cleared (her death sets the
  // flag), lit again the moment the re-arm clears it.
  Enemy.lairSockets = function (regionId) {
    var out = [];
    Object.keys(CFG).forEach(function (type) {
      var row = CFG[type];
      if (!row || row.pattern !== 'boss-slam' || !row.lair) return;
      var N = lairNest(row);
      if (N.regionId !== regionId || !N.dress || !N.dress.light) return;
      var st = LAIR_STATE[N.letter];
      if (st && st.cleared) return;
      var G = window.WH_GROUND;
      var gy = G && G.has(regionId) ? G.heightAt(regionId, N.x, N.z) : 0;
      out.push({ id: 'rotLair@' + N.x + ',' + N.z, x: N.x, y: gy + N.dress.light.height, z: N.z,
        intensity: N.dress.light.intensity, weight: 1, color: N.dress.light.color, noCard: true });
    });
    return out;
  };

  // debug / validation read-out (WH_DEBUG-friendly, no side effects)
  Enemy.lairState = function () {
    var out = {};
    Object.keys(LAIR_STATE).forEach(function (k) { out[k] = { cleared: LAIR_STATE[k].cleared, day: LAIR_STATE[k].day }; });
    return out;
  };

  Enemy.bodyNameFor = bodyNameFor;
  Enemy.rotPoolMesh = rotPoolMesh;      // CC-C8: region-manager outcrop stains
  // pure loop helpers (offline spawn-row derivation, scratch/cc-c5)
  Enemy.packGeometry = { makeLoop: makeLoop, loopAt: loopAt, loopProject: loopProject, packSlot: packSlot };

  Enemy.onKilled = null;              // stage 2: fn(enemy), set by game.js (corpse loot)

  window.WH_Enemy = Enemy;
  window.WH_ENEMY_TYPES = ['bandit', 'ghoul', 'wolf', 'rotmother', 'rotspawn'];
})();