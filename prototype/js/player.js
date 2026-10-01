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
  var V7 = window.WH_CONFIG;          // v7 sections: spell/belt/loadout/armed/consumable

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
    this.atkYawOffset = 0;            // combat-ds1 P0-1: pose yaw relative to facing frame
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
    this.comboIndex = 0;              // v5: which chain move comes next
    this.comboQueued = false;         // v5: next chain input buffered in recover
    this.recoverFullyElapsed = true;  // combat-ds1 P0-3: first swing starts at m1

    // v6: block / parry state
    this.blocking = false;            // RMB held and block accepted
    this.parryTimer = 0;              // seconds left in the parry window
    this.guardBroken = false;         // guard break active (cannot block)
    this.guardBreakTimer = 0;         // seconds left of guard-break stun

    // v7: focus pool (mirrors the stamina pattern)
    this.focus = CFG.focusMax;
    this.focusMax = CFG.focusMax;
    this.focusRegenBlock = 0;         // seconds until focus regen resumes

    // v7: weave / loadout state. activeLoadout 1 = weapon+spell,
    // 2 = weapon+shield. The offhand implement is derived from it.
    this.activeLoadout = 1;
    this.offhand = 'spell';           // 'spell' | 'shield' (derived)
    this.toggling = false;            // loadout toggle busy window
    this.toggleTimer = 0;
    this.castWindup = 0;              // seconds left of cast windup
    this.castCooldown = 0;            // seconds left of cast cooldown
    this.regripTimer = 0;             // belt re-grip busy window
    this.selectedBeltSlot = 0;        // 0-based index into the 5 belt slots
    this.belt = ['firebolt', null, null, null, null];   // spell ids / null
    this.consumables = [{ id: 'healthPotion', charges: V7.consumable.healthPotion.charges }, null];
    this.offhandGlow = null;          // emissive sphere mesh at the left anchor

    // v7: armed finisher state (doc 04 ruling part A)
    this.armedTimer = 0;              // > 0 = armed finisher ready
    this.crossArmed = false;          // cross-finisher ready (armed at toggle)
    this.chainHits = 0;              // v7: hits landed in current chain (for arming)

    // camera orbit state
    this.camYaw = Math.PI;            // looking toward -z (into region A)
    this.camPitch = deg2rad(22);
    this.camDist = CFG.camDistance;
    this.dragging = false;
    this.lastDragX = 0;
    this.lastDragY = 0;
    this.lastManualCamT = -1e9;       // timestamp of last manual camera drag

    // lock-on state (D3)
    this.lockTarget = null;           // enemy object or null

    // visual root (body added by game after assets load)
    this.root = new THREE.Group();
    this.yawFrame = new THREE.Group();
    this.root.add(this.yawFrame);
    this.body = null;
    this.deathTilt = 0;

    this.bindInput();
  }

  Player.prototype.setBody = function (meshRoot) {
    if (this.body) this.yawFrame.remove(this.body);
    this.body = meshRoot;
    // Bob/tilt animation writes body.position.y absolutely; wrap the
    // ground-aligned template in an inner holder so animation only moves
    // the holder and the template's own ground offset is preserved.
    this.bodyBaseY = meshRoot.position.y || 0;
    this.bodyBaseX = meshRoot.position.x || 0;
    this.yawFrame.add(this.body);
    if (window.WH_ASSETS.getClips('playerBody').length) {
      this.anim = new window.WH_CharacterAnim(meshRoot, window.WH_ASSETS.getClips('playerBody'));
    }
  };

  // The skinned hand is the socket. Only stand-ins retain the old rigid pivot.
  Player.prototype.setWeapon = function (mesh) {
    var hand = this.body && this.body.getObjectByName('R_Hand');
    this.sword = mesh;
    if (hand) {
      this.weaponHand = hand;
      hand.add(mesh);
      mesh.position.set(0, 0, 0);
      // Sword asset points +Y along the blade; reverse it in the hand. At the
      // strike pose the animated hand's +Y aims +Z, so the tip leads -Z.
      mesh.rotation.set(0, 0, Math.PI);
      return;
    }
    this.weaponPivot = new THREE.Group();
    this.yawFrame.add(this.weaponPivot);
    this.weaponPivot.add(mesh);
    this.swordBase = window.WH_CONFIG.moveset.idlePose;
    this.resetWeaponPose();
  };

  Player.prototype.resetWeaponPose = function () {
    if (!this.weaponPivot || !this.swordBase) return;
    var p = this.swordBase;
    this.weaponPivot.position.set(p.pos[0], p.pos[1], p.pos[2]);
    this.weaponPivot.rotation.set(p.rot[0], p.rot[1], p.rot[2]);
  };

  // Bob offset: call from the walk animation in place of absolute writes.
  // Composes with groundAlign: only ever ADDS offsets to the stored base.
  // leanX: body.rotation.x (forward+). yawAdd: added to body yaw (yaw osc).
  // swayX: lateral body.position.x offset (body space).
  Player.prototype.setBodyBob = function (bobY, tiltZ, leanX, yawAdd, swayX) {
    if (!this.body || this.anim) return;
    this.body.position.y = this.bodyBaseY + bobY;
    this.body.position.x = (this.bodyBaseX || 0) + (swayX || 0);
    if (tiltZ !== undefined) this.body.rotation.z = tiltZ;
    if (leanX !== undefined) this.body.rotation.x = leanX;
    if (yawAdd !== undefined) this.body.rotation.y = (yawAdd || 0) + (this.atkYawOffset || 0);
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
      // v7: Q = loadout toggle (busy window, resets chain, keeps armed)
      if (e.code === 'KeyQ' && !e.repeat) self.toggleLoadout();
      // v7: Digit1-5 = belt spell selection (never touches chain/armed)
      if (e.code.indexOf('Digit') === 0 && !e.repeat) {
        var n = parseInt(e.code.slice(5), 10);
        if (n >= 1 && n <= V7.belt.slots) self.selectBeltSlot(n - 1);
      }
      // v7: R / T = consumable belt slots 1 / 2
      if (e.code === 'KeyR' && !e.repeat) self.useConsumable(0);
      if (e.code === 'KeyT' && !e.repeat) self.useConsumable(1);
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
      // v6: RMB hold to block (opens the parry window)
      if (e.button === 2) {
        e.preventDefault();
        // v7: RMB routes by offhand implement: spell -> cast, shield -> block
        if (self.offhand === 'spell') self.tryCast();
        else self.tryBlock();
      }
    });
    document.addEventListener('mouseup', function (e) {
      if (e.button === 0) self.dragging = false;
      // v7: RMB release ends block only when the implement is a shield
      if (e.button === 2 && self.offhand === 'shield') self.endBlock();
    });
    // v6: RMB must not open the browser context menu
    document.addEventListener('contextmenu', function (e) {
      e.preventDefault();
      e.stopPropagation();
      return false;
    });
    document.addEventListener('mousemove', function (e) {
      if (!self.dragging || self.lockTarget) return;   // mouse cam disabled while locked
      var dx = e.clientX - self.lastDragX;
      var dy = e.clientY - self.lastDragY;
      self.lastDragX = e.clientX;
      self.lastDragY = e.clientY;
      if (dx !== 0 || dy !== 0) self.lastManualCamT = performance.now() / 1000;
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
  // start during roll. v7: also refused during the loadout toggle busy window.
  Player.prototype.tryRoll = function () {
    if (this.state !== 'alive' || this.rolling || this.toggling) return;
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
    this.endBlock();                        // v6: roll takes priority over block
    // roll direction: current move input direction, or facing if idle
    var dir = new THREE.Vector3(this.moveDirWorld.x, 0, this.moveDirWorld.z);
    if (dir.lengthSq() < 0.01) {
      dir.set(Math.sin(this.yaw), 0, Math.cos(this.yaw));
    }
    dir.normalize();
    this.rollDir.copy(dir);
  };

  // v6: RMB down. Refused while rolling, attacking (any stage), staggered
  // (dying/dead), or guard-broken. On success opens the parry window.
  // Cannot re-block until stamina has recovered past guardBreakMinStamina.
  Player.prototype.tryBlock = function () {
    if (this.state !== 'alive' || this.rolling || this.attacking) return;
    if (this.guardBroken) return;
    if (this.stamina < window.WH_CONFIG.block.guardBreakMinStamina) return;
    this.blocking = true;
    this.parryTimer = window.WH_CONFIG.block.parryWindow;
  };

  Player.prototype.endBlock = function () {
    this.blocking = false;
    this.parryTimer = 0;
  };

  Player.prototype.isBlocking = function () {
    return this.blocking;
  };

  Player.prototype.getParryWindowRemaining = function () {
    return Math.max(0, this.parryTimer);
  };

  Player.prototype.isGuardBroken = function () {
    return this.guardBroken;
  };

  // ====================== v7 WEAVE SLICE ======================================

  // v7: guard-break choke point (called from resolveIncomingHit via
  // onGuardBreak and by game debug hooks). Clears armed/cross state.
  Player.prototype.guardBreak = function () {
    this.guardBroken = true;
    this.guardBreakTimer = window.WH_CONFIG.block.guardBreakStun;
    this.endBlock();
    this.stamina = 0;
    this.armedTimer = 0;                 // counterplay: stagger clears armed
    this.crossArmed = false;
    if (this.onGuardBreak) this.onGuardBreak();
  };

  // v7: loadout toggle I <-> II. Busy window blocks attack/cast/block/roll.
  // Resets the combo chain; KEEPS the armedTimer running; if armed at the
  // toggle moment, banks the cross-finisher.
  Player.prototype.toggleLoadout = function () {
    if (this.state !== 'alive' || this.toggling) return;
    this.endBlock();                     // shield grip is dropped by the swap
    this.toggling = true;
    this.toggleTimer = V7.loadout.toggleSeconds;
    // chain reset (spec: toggle resets the active chain)
    this.comboIndex = 0;
    this.comboQueued = false;
    this.recoverFullyElapsed = false;
    // armed survives the toggle inside its window; cross-finisher banks
    if (this.armedTimer > 0) this.crossArmed = true;
  };

  Player.prototype.getActiveLoadout = function () {
    return this.activeLoadout;
  };

  // v7: belt spell selection (Digit1-5). Swaps the bound spell, starts the
  // regrip window. NEVER touches the combo chain or armed state.
  Player.prototype.selectBeltSlot = function (i) {
    if (this.state !== 'alive') return;
    if (i < 0 || i >= V7.belt.slots) return;
    if (!this.belt[i]) {
      // empty slot refused: HUD flash via callback
      if (this.onCastRefusal) this.onCastRefusal('empty-slot');
      return;
    }
    this.selectedBeltSlot = i;
    this.regripTimer = V7.belt.regripSeconds;
    // glow color follows the selection (mesh owned by game.js visuals)
    if (this.onSpellSelected) this.onSpellSelected(this.belt[i]);
  };

  Player.prototype.getSelectedSpellId = function () {
    return this.belt[this.selectedBeltSlot];
  };

  // v7: RMB-cast refusal conditions (AC: roll/attacking-strike/toggle/regrip/
  // guard break/dead/focus). Windup-stage attacks ALLOW the weave cast.
  Player.prototype.canCast = function () {
    if (this.state !== 'alive') return false;
    if (this.rolling || this.toggling || this.regripTimer > 0) return false;
    if (this.guardBroken) return false;
    if (this.offhand !== 'spell') return false;
    if (this.attacking && this.getAttackStage() !== 'windup') return false;
    if (this.castCooldown > 0 || this.castWindup > 0) return false;
    var spellId = this.getSelectedSpellId();
    if (!spellId) return false;
    var S = V7.spell[spellId];
    return this.focus >= S.focusCost * CFG.castFocusTaxMult;
  };

  // v7: cast entry (RMB with spell implement). Refusal = HUD flash.
  // CASTING NEVER RESETS THE CHAIN: comboIndex/comboQueued untouched.
  Player.prototype.tryCast = function () {
    if (!this.canCast()) {
      if (this.onCastRefusal) this.onCastRefusal('cast-refused');
      return;
    }
    var spellId = this.getSelectedSpellId();
    var S = V7.spell[spellId];
    this.castWindup = S.castWindup;      // fizzle check runs during windup
    this.pendingSpellId = spellId;
  };

  // v7: windup completion -> spawn the Firebolt, spend focus WITH the
  // one-hand tax (weapon in main hand = tax always in this slice),
  // start the cast cooldown. Called by game.js (which owns projectiles).
  // Returns the spawn request or null.
  Player.prototype.completeCast = function () {
    var spellId = this.pendingSpellId;
    this.pendingSpellId = null;
    if (!spellId) return null;
    var S = V7.spell[spellId];
    var cost = S.focusCost * CFG.castFocusTaxMult;
    this.spendFocus(cost);
    this.castCooldown = S.castCooldown;
    // aim at the lock target, else straight ahead of facing
    var dx = Math.sin(this.yaw), dz = Math.cos(this.yaw);
    if (this.lockTarget) {
      var tdx = this.lockTarget.pos.x - this.pos.x;
      var tdz = this.lockTarget.pos.z - this.pos.z;
      var d = Math.sqrt(tdx * tdx + tdz * tdz);
      if (d > 0.001) { dx = tdx / d; dz = tdz / d; }
    }
    return { spellId: spellId, origin: this.pos, dirX: dx, dirZ: dz };
  };

  // v7: damage during castWindup fizzles the cast: NO focus spent,
  // no projectile. HUD fizzle flash via callback.
  Player.prototype.cancelCastFizzle = function () {
    if (this.castWindup > 0) {
      this.castWindup = 0;
      this.pendingSpellId = null;
      if (this.onFizzle) this.onFizzle();
      return true;
    }
    return false;
  };

  Player.prototype.spendFocus = function (amount) {
    this.focus = Math.max(0, this.focus - amount);
    this.focusRegenBlock = CFG.focusRegenDelay;
  };

  // v7: consumable belt slots (R = slot 0 health potion, T = slot 1 empty).
  Player.prototype.useConsumable = function (slot) {
    if (this.state !== 'alive') return;
    var c = this.consumables[slot];
    if (!c || c.charges <= 0) {
      if (this.onCastRefusal) this.onCastRefusal('no-consumable');
      return;
    }
    if (c.id === 'healthPotion') {
      var P = V7.consumable.healthPotion;
      if (this.hp >= this.hpMax) {
        if (this.onCastRefusal) this.onCastRefusal('hp-full');
        return;
      }
      this.hp = Math.min(this.hpMax, this.hp + P.heal);
      c.charges -= 1;
      if (this.onPotion) this.onPotion();
    }
  };

  Player.prototype.getConsumables = function () {
    return this.consumables.map(function (c) {
      return c ? { id: c.id, charges: c.charges } : null;
    });
  };

  // v7: belt accessor for HUD/debug (array of 5 spell ids / null)
  Player.prototype.getBelt = function () {
    return this.belt.slice();
  };

  // v6: single choke point for ALL incoming enemy damage. Order:
  // 1. roll i-frames win (handled in takeDamage below)
  // 2. parry window open -> enemy attack canceled, enemy staggered
  // 3. blocking + attacker in block arc -> chip damage + stamina drain,
  //    guard break when stamina empties
  // 4. otherwise full damage
  Player.prototype.resolveIncomingHit = function (damage, attacker) {
    if (this.state !== 'alive') return false;
    if (this.iframes > 0) return false;      // roll i-frames win (existing)
    var BLK = window.WH_CONFIG.block;

    // v6 fix round 1: attacker angle computed once, reused by both the parry
    // and block arc gates (spec: parry, like block, is front-arc only).
    var attackerInArc = false;
    if (attacker && attacker.pos) {
      var dx = attacker.pos.x - this.pos.x;
      var dz = attacker.pos.z - this.pos.z;
      if (dx * dx + dz * dz > 0.0001) {
        var ang = Math.atan2(dx, dz);
        var dyaw = ang - this.yaw;
        while (dyaw > Math.PI) dyaw -= Math.PI * 2;
        while (dyaw < -Math.PI) dyaw += Math.PI * 2;
        var halfAngle = BLK.blockArcHalfAngleDeg * Math.PI / 180;
        attackerInArc = Math.abs(dyaw) <= halfAngle;
      }
    }

    // 2. parry: timing window open AND attacker in the block arc (spec:
    // attacker behind + blocking = full damage, no parry).
    if (this.blocking && this.parryTimer > 0 && attacker &&
        attacker.enterStagger && attackerInArc) {
      this.spendStamina(BLK.parryStaminaCost);
      attacker.enterStagger(BLK.riposteStaggerDur);
      attacker.riposteArmed = true;          // next player hit does bonus damage
      this.endBlock();
      if (this.onParry) this.onParry(attacker);
      return false;                          // zero damage
    }

    // 3. block: only if attacker is within the block arc of player facing
    if (this.blocking && attacker && attacker.pos && attackerInArc) {
      var staminaCost = Math.max(1, Math.round(damage * BLK.staminaCostMult));
      this.stamina = Math.max(0, this.stamina - staminaCost);
      this.staminaRegenBlock = CFG.staminaRegenDelay;
      var chip = damage * (1 - BLK.absorb);
      var dead = this.takeDamage(chip);
      if (this.stamina <= 0 && !dead) {
        // guard break: stun, block disabled until stamina recovers
        this.guardBroken = true;
        this.guardBreakTimer = BLK.guardBreakStun;
        this.endBlock();
        this.stamina = 0;
        if (this.onGuardBreak) this.onGuardBreak();
      } else if (this.onBlock) {
        this.onBlock(attacker, chip);
      }
      return !dead;                          // blocked (or killed by chip)
    }

    // 4. full damage (existing path)
    return this.takeDamage(damage);
  };

  // combat-ds1 P0-3: only recover presses queue; the chain starts at the
  // recover point instead of waiting for the entire recovery to elapse.
  Player.prototype.tryAttack = function () {
    if (this.state !== 'alive' || this.rolling || this.toggling) return;
    if (this.blocking) return;              // v6: must release RMB to attack
    if (this.attacking) {
      if (this.getAttackStage() === 'recover') this.comboQueued = true;
      return;                                // windup/strike buffer is Round B
    }
    this.startAttack();
  };

  Player.prototype.startAttack = function (nextIndex) {
    if (this.stamina < CFG.attackStaminaCost) return false;
    this.spendStamina(CFG.attackStaminaCost);
    this.attacking = true;
    this.attackTimer = CFG.attackDuration;
    this.attackDidHit = false;
    this.lungeLeft = AW.strikeLunge;
    // v7: armed finisher consumption (armedTimer > 0 = attack at 1.5x;
    // crossArmed = cross-finisher at 2.0x; both consumed on this attack)
    this.pendingArmedMult = 1;
    if (this.armedTimer > 0 && this.crossArmed) {
      this.pendingDamageMult = V7.armed.crossDamageMult;
      this.crossArmed = false;
      this.armedTimer = 0;
    } else if (this.armedTimer > 0) {
      this.pendingDamageMult = V7.armed.damageMult;
      this.armedTimer = 0;
    } else {
      this.pendingDamageMult = 1;
    }
    var cap = window.WH_CONFIG.moveset.comboChainCap;
    this.comboIndex = (typeof nextIndex === 'number') ? nextIndex :
      (this.recoverFullyElapsed ? 0 : Math.min(this.comboIndex + 1, cap));
    if (this.comboIndex === 0) this.chainHits = 0;  // v7: reset hit counter on chain reset
    else this.chainHits = Math.max(this.chainHits, this.comboIndex);  // sync with chain position
    this.comboQueued = false;
    this.recoverFullyElapsed = false;
    // face camera direction on attack (unless locked: windup tracking handles it)
    if (!this.lockTarget) this.yaw = this.camYaw + Math.PI;
    return true;
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
    if (this.anim) this.anim.hit();
    // v7: hp loss during castWindup fizzles the cast (no focus spent)
    this.cancelCastFizzle();
    if (this.hp <= 0) {
      this.state = 'dying';
      this.stateTime = 0;
      // v7: dying/dead clears armed state
      this.armedTimer = 0;
      this.crossArmed = false;
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
      damage: CFG.attackDamage * (this.pendingDamageMult || 1)
    };
  };

  // combat-ds1 P0-4: lock yaw is rate-limited in windup and fixed through
  // strike/recover; idle lock still faces the target directly.
  Player.prototype.updateLockTracking = function (dt) {
    if (!this.lockTarget || this.state !== 'alive') return;
    var stage = this.getAttackStage();
    if (stage === 'strike' || stage === 'recover') return;
    var t = this.lockTarget;
    var dx = t.pos.x - this.pos.x;
    var dz = t.pos.z - this.pos.z;
    if (dx * dx + dz * dz < 0.0001) return;
    var targetYaw = Math.atan2(dx, dz);
    if (stage === 'windup') {
      var maxTurn = deg2rad(LOCK.trackWindupDegPerSec) * dt;
      var delta = shortestAngle(targetYaw - this.yaw);
      this.yaw += Math.max(-maxTurn, Math.min(maxTurn, delta));
    } else {
      this.yaw = targetYaw;
    }
  };

  Player.prototype.update = function (dt, clampToBounds) {
    this.stateTime += dt;

    // timers
    if (this.iframes > 0) this.iframes = Math.max(0, this.iframes - dt);
    // v6: block/parry timers. Blocking ends on roll or on state loss.
    if (this.parryTimer > 0) this.parryTimer = Math.max(0, this.parryTimer - dt);
    if (this.guardBroken) {
      this.guardBreakTimer -= dt;
      if (this.guardBreakTimer <= 0) this.guardBroken = false;
    }
    if (this.blocking && (this.rolling || this.state !== 'alive')) this.endBlock();
    if (this.staminaRegenBlock > 0) {
      this.staminaRegenBlock -= dt;
    } else if (this.stamina < this.staminaMax) {
      // v6: regen continues while blocking at a reduced rate
      var regenMult = this.blocking ? window.WH_CONFIG.block.blockingRegenMult : 1;
      this.stamina = Math.min(this.staminaMax,
        this.stamina + CFG.staminaRegenPerSec * regenMult * dt);
    }

    // ---- v7: focus regen (mirrors the stamina pattern) ----
    if (this.focusRegenBlock > 0) {
      this.focusRegenBlock -= dt;
    } else if (this.focus < this.focusMax) {
      this.focus = Math.min(this.focusMax,
        this.focus + CFG.focusRegenPerSec * dt);
    }

    // ---- v7: weave timers ----
    if (this.toggling) {
      this.toggleTimer -= dt;
      if (this.toggleTimer <= 0) {
        this.toggling = false;
        this.activeLoadout = 3 - this.activeLoadout;  // v7: flip 1<->2 on toggle complete
        this.offhand = this.activeLoadout === 2 ? 'shield' : 'spell';
      }
    }
    if (this.regripTimer > 0) this.regripTimer = Math.max(0, this.regripTimer - dt);
    if (this.castCooldown > 0) this.castCooldown = Math.max(0, this.castCooldown - dt);
    // armed finisher window decays; expiry clears armed AND crossArmed
    if (this.armedTimer > 0) {
      this.armedTimer = Math.max(0, this.armedTimer - dt);
      if (this.armedTimer <= 0) this.crossArmed = false;
    }
    // offhand implement derived from the active loadout (1 = spell, 2 = shield)
    this.offhand = this.activeLoadout === 2 ? 'shield' : 'spell';
    if (this.blocking && this.offhand !== 'shield') this.endBlock();

    if (this.state === 'dying') {
      this.deathTilt = Math.min(Math.PI / 2, this.deathTilt + dt * 3);
      if (this.body && !this.anim) this.body.rotation.x = -this.deathTilt;
      if (this.anim) this.anim.death();
      if (this.stateTime >= CFG.respawnDelay) this.state = 'dead';
      return;
    }

    if (this.attacking) {
      this.attackTimer -= dt;
      // combat-ds1 P0-3: consume on every recover frame, including the
      // final one; an accepted press immediately starts the next windup.
      if (this.getAttackStage() === 'recover' && this.comboQueued) {
        var cap = window.WH_CONFIG.moveset.comboChainCap;
        var next = (this.comboIndex >= cap - 1) ? 0 : this.comboIndex + 1;
        this.startAttack(next);
      }
      if (this.attackTimer <= 0) {
        this.attacking = false;
        this.recoverFullyElapsed = true;
        this.comboIndex = 0;
        this.chainHits = 0;
        this.comboQueued = false;
      }
    }

    this.updateLockTracking(dt);
    this.atkYawOffset = 0;

    var displacement = new THREE.Vector3(0, 0, 0);
    var moving = false;
    var sprintingNow = false;
    this.animMoveSpeed = 0;

    if (this.rolling) {
      this.rollTimer -= dt;
      // roll = quick translation + eased full tumble (v3)
      var step = this.rollDir.clone().multiplyScalar(CFG.rollSpeed * dt);
      this.pos.add(step);
      this.animMoveSpeed = CFG.rollSpeed;
      if (this.body && !this.anim) {
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
        // v6: blocking forces walk pace (sprint not allowed while blocking)
        sprintingNow = this.sprinting && this.stamina > 0 && !this.blocking;
        var len = Math.sqrt(mx * mx + mz * mz);
        mx /= len; mz /= len;
        var speed = sprintingNow ? CFG.sprintSpeed : CFG.walkSpeed;
        if (sprintingNow) {
          this.spendStamina(CFG.sprintStaminaPerSec * dt);
        }
        if (this.attacking) speed *= this.getAttackStage() === 'windup' ? 0.3 : 0;
        if (this.blocking) speed *= window.WH_CONFIG.block.moveMult;  // v6
        this.animMoveSpeed = speed;
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
          var maxTurn = deg2rad(this.attacking
            ? (this.getAttackStage() === 'windup' ? CFG.turnLerpDegPerSecAttackWindup : 0)
            : CFG.turnLerpDegPerSec) * dt;
          var dyaw = shortestAngle(targetYaw - this.yaw);
          this.yaw += Math.max(-maxTurn, Math.min(maxTurn, dyaw));
        }
        // ---- v3 D2: layered walk/sprint cycle ----
        this.idleTime = 0;
        this.bobPhase += dt * (sprintingNow ? WL.bobFreqSprint : WL.bobFreqWalk);
        if (this.body && !this.anim) {
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
        if (this.body && !this.anim) {
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
    this.yawFrame.rotation.y = this.yaw;

    // Legacy pivot poses remain only for the rigid stand-in fallback.
    if (this.body && !this.anim) {
      if (this.attacking) {
        var stage = this.getAttackStage();
        var MS = window.WH_MOVESET;
        var move = [MS.m1, MS.m2, MS.m3][this.comboIndex];
        if (stage === 'windup') {
          var wp = (CFG.attackDuration - this.attackTimer) /
                   (CFG.attackDuration * AW.windupFrac);       // 0..1
          var we = smooth(wp);
          this.body.rotation.x = AW.windupLean * we;           // lean back
          this.atkYawOffset = 0;
          this.body.rotation.y = this.atkYawOffset;
          this.body.rotation.z = 0;
          this.body.position.y = this.bodyBaseY - AW.windupCrouch * we;  // crouch
          this.body.position.x = this.bodyBaseX || 0;
          var pw = MS.interpPose(MS.idle, move.windup, we);
          this.weaponPivot.position.set(pw.pos[0], pw.pos[1], pw.pos[2]);
          this.weaponPivot.rotation.set(pw.rot[0], pw.rot[1], pw.rot[2]);
        } else if (stage === 'strike') {
          var sp = (CFG.attackDuration * AW.windupFrac + CFG.attackDuration * AW.strikeFrac
                    - this.attackTimer) /
                   (CFG.attackDuration * AW.strikeFrac);        // 0..1
          var se = 1 - (1 - sp) * (1 - sp);                     // ease-out
          // horizontal yaw sweep through the stage (start behind right shoulder)
          this.atkYawOffset = -deg2rad(AW.strikeYawSweepDeg) * 0.5
                              + deg2rad(AW.strikeYawSweepDeg) * se;
          this.body.rotation.y = this.atkYawOffset;
          this.body.rotation.x = 0;
          this.body.rotation.z = 0;
          this.body.position.y = this.bodyBaseY;
          this.body.position.x = this.bodyBaseX || 0;
          var ps = MS.interpPose(move.windup, move.strike, se);
          this.weaponPivot.position.set(ps.pos[0], ps.pos[1], ps.pos[2]);
          this.weaponPivot.rotation.set(ps.rot[0], ps.rot[1], ps.rot[2]);
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
          this.atkYawOffset = swing * (1 - re);                 // ease back to neutral
          this.body.rotation.y = this.atkYawOffset;
          this.body.rotation.x = AW.recoverLean * re;           // forward-lean settle
          this.body.rotation.z = 0;
          this.body.position.y = this.bodyBaseY;
          this.body.position.x = this.bodyBaseX || 0;
          var pr = MS.interpPose(move.strike, MS.idle, re);
          this.weaponPivot.position.set(pr.pos[0], pr.pos[1], pr.pos[2]);
          this.weaponPivot.rotation.set(pr.rot[0], pr.rot[1], pr.rot[2]);
        }
      } else if (!this.rolling) {
        this.body.rotation.x = 0;
        this.body.rotation.y = this.atkYawOffset;
        this.body.rotation.z = 0;
        this.body.position.x = this.bodyBaseX || 0;
        if (this.sword) this.resetWeaponPose();
      }
    }
    // Lunge displacement remains FSM-owned even when the clip supplies the pose.
    if (this.anim && this.attacking && this.getAttackStage() === 'strike' && this.lungeLeft > 0) {
      var lungeVel = AW.strikeLunge / (CFG.attackDuration * AW.strikeFrac);
      var lungeStep = Math.min(lungeVel * dt, this.lungeLeft);
      this.pos.x += Math.sin(this.yaw) * lungeStep;
      this.pos.z += Math.cos(this.yaw) * lungeStep;
      this.lungeLeft -= lungeStep;
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
      // v3.1: souls-style auto-follow. While moving (and not within the
      // manual-override window after a mouse drag), ease camera yaw toward
      // the player's facing so A/D strafing orbits the camera with you.
      // Idle and lock-on are untouched.
      var nowT = performance.now() / 1000;
      var manualOverride = (nowT - this.lastManualCamT) < CFG.camAutoFollowDelay;
      var moving = (this.moveDirWorld.x !== 0 || this.moveDirWorld.z !== 0);
      if (moving && !manualOverride) {
        var followYaw = Math.atan2(this.moveDirWorld.x, this.moveDirWorld.z) + Math.PI;
        var lerpF = 1 - Math.exp(-CFG.camAutoFollowRate * dt);
        this.camYaw += shortestAngle(followYaw - this.camYaw) * lerpF;
      }
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
    this.endBlock();                        // v6: clear block state
    this.guardBroken = false;
    this.guardBreakTimer = 0;
    this.deathTilt = 0;
    this.lockTarget = null;
    // v7: clear weave/armed transient state on respawn
    this.focus = this.focusMax;
    this.focusRegenBlock = 0;
    this.toggling = false;
    this.toggleTimer = 0;
    this.castWindup = 0;
    this.castCooldown = 0;
    this.regripTimer = 0;
    this.pendingSpellId = null;
    this.armedTimer = 0;
    this.crossArmed = false;
    this.atkYawOffset = 0;
    this.yawFrame.rotation.y = this.yaw;
    if (this.anim) this.anim.revive();
    if (this.body && !this.anim) { this.body.rotation.x = 0; this.body.rotation.y = this.atkYawOffset; }
  };

  window.WH_Player = Player;
})();