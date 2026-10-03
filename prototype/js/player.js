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
  var MV = window.WH_CONFIG.moveset;  // 10-04: per-weapon moveset framework

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
    this.comboIndex = 0;              // v5: chain position of the current swing
    this.comboQueued = false;         // v5: next chain input buffered (strike/recover)
    this.comboBufferTimer = 0;        // 10-04: seconds the buffered input stays fresh
    this.recoverFullyElapsed = true;  // combat-ds1 P0-3: first swing starts at m1
    this.weaponId = MV.playerWeapon;  // 10-04: key into CONFIG.moveset.weapons
    this.attackMoveId = null;         // 10-04: CONFIG move id of the current swing
    this.attackMove = null;           // 10-04: CONFIG move def (frozen per swing)
    this.attackTotal = 0;             // windup + strike + recover of attackMove
    this.attackSerial = 0;            // increments on every swing start

    // v6: block / parry state
    this.blocking = false;            // RMB held and block accepted
    this.parryTimer = 0;              // seconds left in the parry window
    this.guardBroken = false;         // guard break active (cannot block)
    this.guardBreakTimer = 0;         // seconds left of guard-break stun

    // v7: focus pool (mirrors the stamina pattern)
    this.focus = CFG.focusMax;
    this.focusMax = CFG.focusMax;
    this.focusRegenBlock = 0;         // seconds until focus regen resumes

    // v7: weave / loadout state. Order B: activeLoadout is derived from the
    // left hand for the HUD pips (1 = qSwap[0] glove, 2 = qSwap[1] shield,
    // 0 = anything else); Q swaps the left hand between the two.
    this.activeLoadout = 1;
    this.toggling = false;            // loadout toggle busy window
    this.toggleTimer = 0;
    this.pendingQSwap = null;         // item id Q puts in the left hand on completion
    this.castWindup = 0;              // seconds left of cast windup
    this.castCooldown = 0;            // seconds left of cast cooldown
    this.regripTimer = 0;             // belt re-grip busy window
    this.selectedBeltSlot = 0;        // 0-based index into the 5 belt slots
    this.belt = V7.belt.defaultSpells.slice();          // spell ids / null
    this.consumables = [{ id: 'healthPotion', charges: V7.consumable.healthPotion.charges }, null];
    this.offhandGlow = null;          // emissive sphere mesh on the caster hand (game.js)
    // Order B (2026-10-05) free per-hand equip: one gear item id (or null)
    // per hand, single instances (an item is in a hand OR the inventory).
    // Combat reads ONLY the capability flags hasCaster / hasShield /
    // hasMeleeRight, derived from CONFIG.items[id].kind. Belt keys 1-5 pick
    // the active learned spell and never touch the hands.
    this.hands = { right: null, left: null };
    this.inventory = null;            // game.js setupInventory wires the Inventory
    this.itemMeshes = {};             // item id -> its hand mesh (game.js instances)
    this.sword = null;                // = itemMeshes of the melee item (armed glow)
    this.shield = null;               // = itemMeshes of the shield item

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

    // 10-05 inventory Order A: true while the inventory screen is open.
    // Movement / combat / camera input is ignored; key states keep tracking
    // so held keys resume the instant it closes. The world keeps running.
    this.inputSuspended = false;

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

  // Order B: mounts are measured for an item's NATIVE hand
  // (CONFIG.equip.nativeHand); the other hand gets the hand-local mount
  // mirrored by CONFIG.equip.mirrorScale (S R S for the rotation, S p for
  // the offset - a proper rotation again, roll angles flip sign).
  function isMirrored(itemId, hand) {
    var nat = window.WH_CONFIG.equip.nativeHand[itemId];
    return !!nat && nat !== hand;
  }

  function mirrorQuat(q) {
    var s = window.WH_CONFIG.equip.mirrorScale;
    var S = new THREE.Matrix4().makeScale(s[0], s[1], s[2]);
    var m = new THREE.Matrix4().makeRotationFromQuaternion(q);
    return q.setFromRotationMatrix(S.clone().multiply(m).multiply(S));
  }

  function mirrorVec(v) {
    var s = window.WH_CONFIG.equip.mirrorScale;
    return v.set(v.x * s[0], v.y * s[1], v.z * s[2]);
  }

  function boneFor(body, hand) {
    return body ? body.getObjectByName(hand === 'left' ? 'L_Hand' : 'R_Hand') : null;
  }

  // The skinned hand is the socket. Only stand-ins retain the old rigid pivot.
  // Order B: hand = 'right' | 'left'; the melee mesh mounts on either one.
  Player.prototype.mountWeapon = function (mesh, hand, itemId) {
    var bone = boneFor(this.body, hand);
    if (this.weaponPivot) {
      this.weaponPivot.remove(mesh);
      this.yawFrame.remove(this.weaponPivot);
      this.weaponPivot = null;
    }
    if (mesh.parent) mesh.parent.remove(mesh);
    var wm = window.WH_CONFIG.assets.weaponMount;
    // Grip anchor (Nicko 10-03): the instance is a groundAlign HOLDER whose
    // inner mesh was lifted so the GLB's raw min-Y rests at holder y=0 -
    // which put the sword TIP at/behind the fist (hand on mid-blade, hilt
    // floating behind: "hilt at the opposite end"). Slide the INNER mesh
    // down by the measured grip height in HOLDER-LOCAL Y (the mount
    // rotation maps holder -Y to hand-local +Z grip-forward, so a -Y
    // shift moves the grip ONTO the fist and the tip forward in front).
    // Measured: sword grip at raw y~+0.65 -> holder y 1.637 (CONFIG).
    // Offset is in raw GLB units and scales with the weapon correctly.
    // Order B: applied once per mesh - remounts must not stack it.
    if (!mesh.userData.whGripApplied) {
      mesh.userData.whGripApplied = true;
      var gripY = (wm && wm.gripHolderY) ? (wm.gripHolderY[this.weaponId] || 0) : 0;
      if (gripY && mesh.children[0]) mesh.children[0].position.y -= gripY;
    }
    if (bone) {
      bone.add(mesh);
      mesh.position.set(0, 0, 0);
      // Grip mount (2026-10-03 re-measure): the longsword GLB's blade tip
      // lies along mesh-local -Y, and the fist's grip-forward direction is
      // hand-local +Z, so map -Y -> +Z with a CONSTANT local-space
      // quaternion. The old world-quaternion math sampled the rest pose at
      // setWeapon time, letting the animation pose leak in -- blade ended up
      // parallel to the forearm with the hilt on the wrong end. This mount
      // is pose-independent, so it holds through idle, walk, and swings.
      var mountRotation = new THREE.Quaternion();
      if (wm && wm.enabled) {
        // 10-04: blade axis per weapon (longsword -Y = unchanged mount;
        // handAxe +Y = the bandit axe's measured mapping in enemy.js).
        var bladeY = this.getWeaponDef().bladeAxisY || -1;
        mountRotation.setFromUnitVectors(
          new THREE.Vector3(0, bladeY, 0), new THREE.Vector3(0, 0, 1));
        // Blade-edge tuning roll about the grip axis. Sign verified: rolling
        // about hand-local +Z is a rotation of the mounted blade's own axis,
        // so the roll quaternion composes on the LEFT of the axis mapping
        // (premultiply = applied after the mapping); positive rollDeg is CCW
        // around +Z, right-hand rule. Tuning stays a CONFIG data edit.
        if (wm.rollDeg) {
          mountRotation.premultiply(new THREE.Quaternion().setFromAxisAngle(
            new THREE.Vector3(0, 0, 1), wm.rollDeg * Math.PI / 180));
        }
        if (isMirrored(itemId, hand)) mirrorQuat(mountRotation);
      }
      mesh.quaternion.copy(mountRotation);
      return;
    }
    // rigid stand-in: right hand = the animated pivot, left = mirrored idle anchor
    var ip = window.WH_CONFIG.moveset.idlePose;
    if (hand === 'right') {
      this.weaponPivot = new THREE.Group();
      this.yawFrame.add(this.weaponPivot);
      this.weaponPivot.add(mesh);
      mesh.position.set(0, 0, 0);
      this.swordBase = ip;
      this.resetWeaponPose();
    } else {
      this.yawFrame.add(mesh);
      mesh.position.set(-ip.pos[0], ip.pos[1], ip.pos[2]);
      mesh.rotation.set(ip.rot[0], -ip.rot[1], -ip.rot[2]);
    }
  };

  // 10-04 moveset framework accessors. The weapon def / move defs are read
  // straight from CONFIG.moveset.weapons so live CONFIG edits apply.
  Player.prototype.getWeaponDef = function () {
    return MV.weapons[this.weaponId] || MV.weapons[MV.playerWeapon];
  };

  // Moves per chain (also the landed-hit count that arms the v7 finisher).
  Player.prototype.getChainCap = function () {
    var W = this.getWeaponDef();
    return Math.max(1, Math.min(W.chainCap || W.chain.length, W.chain.length));
  };

  Player.prototype.getChainMove = function (index) {
    var W = this.getWeaponDef();
    return W.moves[W.chain[index]];
  };

  // Swap the active moveset (chain resets). mesh optional: game.js passes the
  // new weapon instance, which replaces the melee item's hand mesh (debug
  // WH_DEBUG.equipWeapon; the melee item itself stays the same item id).
  Player.prototype.equipWeapon = function (id, mesh) {
    if (!MV.weapons[id]) return false;
    this.cancelAttack();
    this.weaponId = id;
    if (mesh) this.setItemMesh(this.meleeItemId(), mesh);
    return true;
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
      if (self.inputSuspended) return;   // 10-05: inventory screen open
      if (e.code === 'Space') {
        e.preventDefault();
        self.tryRoll();
      }
      if (e.code === 'KeyF' && !e.repeat) {
        e.preventDefault();
        if (self.onLockToggle) self.onLockToggle();  // game.js decides engage/break
      }
      // v7: Q = loadout toggle (busy window, resets chain, keeps armed).
      // Order B: swaps the left hand glove <-> shield.
      if (e.code === 'KeyQ' && !e.repeat) self.toggleLoadout();
      // Order B: Digit1-5 = active learned spell (never touches hands/chain/armed)
      if (e.code.indexOf('Digit') === 0 && !e.repeat) {
        var n = parseInt(e.code.slice(5), 10);
        if (n >= 1 && n <= V7.belt.slots) self.pressBeltKey(n - 1);
      }
      // v7: R / T = consumable belt slots 1 / 2
      if (e.code === 'KeyR' && !e.repeat) self.useConsumable(0);
      if (e.code === 'KeyT' && !e.repeat) self.useConsumable(1);
    });
    document.addEventListener('keyup', function (e) {
      self.keys[e.code] = false;
    });
    document.addEventListener('mousedown', function (e) {
      if (self.inputSuspended) return;   // 10-05: clicks belong to the inventory screen
      if (e.button === 0) {
        self.tryAttack();
        if (!self.lockTarget) {
          self.dragging = true;
          self.lastDragX = e.clientX;
          self.lastDragY = e.clientY;
        }
      }
      // v6: RMB hold to block (opens the parry window). Order B: RMB routes
      // by the hands (secondaryAction: caster -> cast, shield -> block).
      if (e.button === 2) {
        e.preventDefault();
        self.secondaryDown();
      }
    });
    document.addEventListener('mouseup', function (e) {
      if (e.button === 0) self.dragging = false;
      // v7: RMB release ends a held block (no-op otherwise)
      if (e.button === 2) self.secondaryUp();
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
      if (self.inputSuspended) return;
      self.camDist += (e.deltaY > 0 ? 1 : -1) * 0.8;
      self.camDist = Math.max(CFG.camMinDistance, Math.min(CFG.camMaxDistance, self.camDist));
    }, { passive: true });
  };

  Player.prototype.collectMoveInput = function () {
    var k = this.inputSuspended ? {} : this.keys;
    var ix = 0, iz = 0;
    if (k['KeyW']) iz -= 1;
    if (k['KeyS']) iz += 1;
    if (k['KeyA']) ix -= 1;
    if (k['KeyD']) ix += 1;
    this.moveInput.x = ix;
    this.moveInput.z = iz;
    this.sprinting = !!(k['ShiftLeft'] || k['ShiftRight']);
  };

  // 10-05 inventory Order A: suspend / restore player input. Suspending
  // drops an active camera drag and a held guard (RMB release would land
  // on the open screen); anything already in flight (swing, roll, cast
  // windup) plays out. Restore is instant - nothing to rebuild.
  Player.prototype.setInputSuspended = function (on) {
    this.inputSuspended = !!on;
    if (on) {
      this.dragging = false;
      this.endBlock();
    }
  };

  // 10-04 (Nicko, souls-style): roll cancels attack RECOVER only - windup
  // and strike are committed. Attack cannot start during roll. v7: also
  // refused during the loadout toggle busy window.
  Player.prototype.tryRoll = function () {
    if (this.state !== 'alive' || this.rolling || this.toggling) return;
    if (this.stamina < CFG.rollStaminaCost) return;
    if (this.attacking) {
      if (this.getAttackStage() !== 'recover') return;  // windup/strike locked
      this.cancelAttack();                              // roll out of recovery
    }
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
    if (this.toggling) return;              // Order B: the shield is mid-swap until Q lands
    if (!this.hasShield()) return;          // Order B: a shield in either hand
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

  // v7: loadout toggle busy window (blocks attack/cast/block/roll), resets
  // the combo chain, KEEPS the armedTimer running; if armed at the toggle
  // moment, banks the cross-finisher. Order B: Q = LEFT-HAND SWAP between
  // CONFIG.equip.qSwap[0] (magic glove) and [1] (round shield): left holds
  // the glove -> the shield goes in, anything else -> the glove goes in.
  // The incoming item must be in the INVENTORY, else a refusal toast and
  // nothing changes (no window, no chain reset). The swap lands when the
  // window completes (update()); the outgoing item returns to the inventory.
  Player.prototype.toggleLoadout = function () {
    if (this.state !== 'alive' || this.toggling) return;
    var pair = window.WH_CONFIG.equip.qSwap;
    var target = this.hands.left === pair[0] ? pair[1] : pair[0];
    if (!this.inventory || this.inventory.countOf(target) <= 0) {
      this.refuseEquip(itemName(target) + ' not in inventory');
      return;
    }
    this.pendingQSwap = target;
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

  // v7: belt spell selection = the ACTIVE LEARNED SPELL (magic canon 10-05:
  // spells are knowledge, the belt is 5 quick slots over them). Starts the
  // regrip window only while a caster is in hand (re-grip applies to
  // nothing otherwise). NEVER touches the combo chain, armed state, or the
  // hands.
  Player.prototype.selectBeltSlot = function (i) {
    if (this.state !== 'alive') return;
    if (i < 0 || i >= V7.belt.slots) return;
    if (!this.belt[i]) {
      // empty slot refused: HUD flash via callback
      if (this.onCastRefusal) this.onCastRefusal('empty-slot');
      return;
    }
    this.selectedBeltSlot = i;
    if (this.hasCaster()) this.regripTimer = V7.belt.regripSeconds;
    // glow color follows the selection (mesh owned by game.js visuals)
    if (this.onSpellSelected) this.onSpellSelected(this.belt[i]);
  };

  // Digit key k (Order B): pick that slot's learned spell. Empty slot =
  // refusal flash; the active spell's own key = no-op. A cast still in
  // windup belongs to the old spell and is dropped.
  Player.prototype.pressBeltKey = function (i) {
    if (this.state !== 'alive') return;
    if (i < 0 || i >= V7.belt.slots) return;
    if (this.belt[i] && i === this.selectedBeltSlot) return;
    if (this.belt[i]) this.dropPendingCast();
    this.selectBeltSlot(i);
  };

  // Learned spells (CHARACTER tab list): the belt's filled slots for now.
  // Books / scrolls (learn-on-read) will add to the belt later.
  Player.prototype.getKnownSpells = function () {
    var out = [];
    for (var i = 0; i < this.belt.length; i++) {
      if (this.belt[i]) out.push({ slot: i, id: this.belt[i], active: i === this.selectedBeltSlot });
    }
    return out;
  };

  // A cast still in windup belongs to the implement being put away: drop it
  // (no focus spent; deliberate, so no fizzle flash).
  Player.prototype.dropPendingCast = function () {
    this.castWindup = 0;
    this.pendingSpellId = null;
  };

  // ---- Order B: hands ---------------------------------------------------------

  function itemDef(id) {
    return id ? (window.WH_CONFIG.items[id] || null) : null;
  }

  function kindOf(id) {
    var d = itemDef(id);
    return d ? d.kind || null : null;
  }

  function itemName(id) {
    var d = itemDef(id);
    return d ? d.name : String(id);
  }

  function otherHand(hand) {
    return hand === 'right' ? 'left' : 'right';
  }

  // capability flags: the single source for every combat gate
  Player.prototype.hasCaster = function () {
    return !!this.casterHand();
  };

  Player.prototype.casterHand = function () {
    if (kindOf(this.hands.left) === 'caster') return 'left';
    if (kindOf(this.hands.right) === 'caster') return 'right';
    return null;
  };

  Player.prototype.hasShield = function () {
    return kindOf(this.hands.left) === 'shield' || kindOf(this.hands.right) === 'shield';
  };

  Player.prototype.hasMeleeRight = function () {
    return kindOf(this.hands.right) === 'melee';
  };

  Player.prototype.handOf = function (id) {
    if (this.hands.right === id) return 'right';
    if (this.hands.left === id) return 'left';
    return null;
  };

  // The melee item whose mesh/moveset the swing code drives: the one in the
  // right hand, else the first melee item in CONFIG.items.
  Player.prototype.meleeItemId = function () {
    if (this.hasMeleeRight()) return this.hands.right;
    var items = window.WH_CONFIG.items;
    for (var id in items) if (items[id].kind === 'melee') return id;
    return null;
  };

  // RMB routing (Order B): the first CONFIG.equip.rmbOrder capability held
  // wins - 'cast' (caster in EITHER hand), 'block' (shield in either hand),
  // or null = RMB does nothing. Mouse and touch both route through here.
  Player.prototype.secondaryAction = function () {
    var order = window.WH_CONFIG.equip.rmbOrder;
    for (var i = 0; i < order.length; i++) {
      if (order[i] === 'caster' && this.hasCaster()) return 'cast';
      if (order[i] === 'shield' && this.hasShield()) return 'block';
    }
    return null;
  };

  Player.prototype.secondaryDown = function () {
    var a = this.secondaryAction();
    if (a === 'cast') this.tryCast();
    else if (a === 'block') this.tryBlock();
  };

  Player.prototype.secondaryUp = function () {
    this.endBlock();
  };

  Player.prototype.refuseEquip = function (text) {
    if (this.onEquipRefusal) this.onEquipRefusal(text);
    return false;
  };

  // Equip item id into hand ('right' | 'left'). Sources: the OTHER hand (a
  // move - never a duplicate) unless inventoryOnly, else the inventory. A
  // displaced item in the target hand returns to the inventory; drawing from
  // the inventory frees a slot for it (gear stacks to 1), a hand-to-hand
  // move needs a free slot or is refused "Inventory full". Returns true when
  // the item ends up in that hand.
  Player.prototype.equipItem = function (id, hand, inventoryOnly) {
    var d = itemDef(id);
    if (!d || d.category !== 'gear' || !d.hands) return this.refuseEquip(itemName(id) + ' cannot be equipped');
    if (d.hands.indexOf(hand) < 0) return this.refuseEquip(d.name + ' cannot go in the ' + hand + ' hand');
    if (this.hands[hand] === id) return true;
    var other = otherHand(hand);
    var fromOther = !inventoryOnly && this.hands[other] === id;
    var inv = this.inventory;
    if (!fromOther && (!inv || inv.countOf(id) <= 0)) return this.refuseEquip(d.name + ' not in inventory');
    var displaced = this.hands[hand];
    if (displaced && fromOther && !inv.hasRoomFor(displaced)) return this.refuseEquip('Inventory full');
    // hands first, inventory second: the inventory's onChange redraw then
    // already sees the final hands
    if (fromOther) this.hands[other] = null;
    this.hands[hand] = id;
    if (!fromOther) inv.removeItem(id, 1);
    if (displaced) inv.addItem(displaced, 1);
    this.handsChanged();
    return true;
  };

  // Hand -> inventory. Refused (toast, item stays) when the inventory is full.
  Player.prototype.unequipHand = function (hand) {
    var id = this.hands[hand];
    if (!id) return false;
    if (!this.inventory || !this.inventory.hasRoomFor(id)) return this.refuseEquip('Inventory full');
    this.hands[hand] = null;
    this.inventory.addItem(id, 1);
    this.handsChanged();
    return true;
  };

  // Boot: move CONFIG.equip.defaultHands items out of the starting kit.
  Player.prototype.equipDefaultHands = function () {
    var dh = window.WH_CONFIG.equip.defaultHands;
    if (dh.right) this.equipItem(dh.right, 'right');
    if (dh.left) this.equipItem(dh.left, 'left');
  };

  // Combat side effects of any hand change, then visuals + listeners.
  Player.prototype.handsChanged = function () {
    var melee = this.hasMeleeRight();
    if (!melee && this.attacking) this.cancelAttack();      // no blade, no swing
    if (melee && this.hands.right !== this.lastRightItem) {
      var mv = itemDef(this.hands.right).moveset;
      if (mv && MV.weapons[mv] && mv !== this.weaponId) {
        this.cancelAttack();
        this.weaponId = mv;
      }
    }
    this.lastRightItem = this.hands.right;
    if (!this.hasShield()) this.endBlock();
    var ch = this.casterHand();
    if (!ch) this.dropPendingCast();
    else if (ch !== this.lastCasterHand) this.regripTimer = V7.belt.regripSeconds;
    this.lastCasterHand = ch;
    var pair = window.WH_CONFIG.equip.qSwap;
    this.activeLoadout = this.hands.left === pair[0] ? 1 : this.hands.left === pair[1] ? 2 : 0;
    this.applyHandVisuals();
    if (this.onHandsChanged) this.onHandsChanged(this.hands);
  };

  // Register an item's hand mesh (game.js instances the GLB). One-time prep
  // here; applyHandVisuals mounts it on whichever hand holds the item.
  Player.prototype.setItemMesh = function (id, mesh) {
    var old = this.itemMeshes[id];
    if (old && old !== mesh) {
      if (old.parent) old.parent.remove(old);
      if (this.weaponPivot && old === this.sword) {
        this.yawFrame.remove(this.weaponPivot);
        this.weaponPivot = null;
      }
    }
    this.itemMeshes[id] = mesh;
    mesh.userData.whHand = null;
    var k = kindOf(id);
    if (k === 'melee') {
      this.sword = mesh;
      this.swordBaseEmissive = null;     // armed-glow base re-sampled per mesh
    } else if (k === 'shield') {
      this.shield = mesh;
      prepShield(mesh);
    }
    this.applyHandVisuals();
  };

  // Shield prep (once per mesh, before any mount): centre the disc on its
  // X/Y and put its back-most point on the holder origin, so the mount
  // offset is where the shield's back meets the fist.
  function prepShield(mesh) {
    var inner = mesh.children[0];
    if (!inner || mesh.userData.whShieldPrepped) return;
    mesh.userData.whShieldPrepped = true;
    mesh.updateMatrixWorld(true);
    var box = new THREE.Box3().setFromObject(inner);
    var s = mesh.scale.x || 1;
    var c = box.getCenter(new THREE.Vector3()).multiplyScalar(1 / s);
    inner.position.x -= c.x;
    inner.position.y -= c.y;
    inner.position.z -= box.min.z / s;
  }

  // Each registered mesh follows its item: mounted on the hand holding it,
  // detached + hidden while the item is in the inventory. Remount only on a
  // hand change (mounts are constant hand-local transforms).
  Player.prototype.applyHandVisuals = function () {
    for (var id in this.itemMeshes) {
      var mesh = this.itemMeshes[id];
      var hand = this.handOf(id);
      if (!hand) {
        if (this.weaponPivot && mesh === this.sword) {
          this.yawFrame.remove(this.weaponPivot);
          this.weaponPivot = null;
        }
        if (mesh.parent) mesh.parent.remove(mesh);
        mesh.visible = false;
        mesh.userData.whHand = null;
        continue;
      }
      mesh.visible = true;
      if (mesh.userData.whHand === hand && mesh.parent) continue;
      mesh.userData.whHand = hand;
      var k = kindOf(id);
      if (k === 'melee') this.mountWeapon(mesh, hand, id);
      else if (k === 'shield') this.mountShield(mesh, hand, id);
    }
  };

  // Mount the round shield on a skinned hand (constant hand-local mount
  // measured offline for L_Hand, CONFIG.assets.shieldMount; mirrored for
  // R_Hand); the rigid stand-in body has no bones, so it falls back to the
  // idle anchor on yawFrame (mirrored per hand).
  Player.prototype.mountShield = function (mesh, hand, itemId) {
    if (mesh.parent) mesh.parent.remove(mesh);
    var SM = window.WH_CONFIG.assets.shieldMount;
    var bone = boneFor(this.body, hand);
    if (bone) {
      bone.add(mesh);
      // raw +Z (boss side) -> faceAxis, raw +Y (disc up) -> upAxis
      var f = new THREE.Vector3().fromArray(SM.faceAxis).normalize();
      var u = new THREE.Vector3().fromArray(SM.upAxis);
      u.addScaledVector(f, -u.dot(f)).normalize();
      var x = new THREE.Vector3().crossVectors(u, f);
      var q = new THREE.Quaternion().setFromRotationMatrix(
        new THREE.Matrix4().makeBasis(x, u, f));
      // rollDeg: same convention as weaponMount (about hand-local +Z, CCW)
      if (SM.rollDeg) {
        q.premultiply(new THREE.Quaternion().setFromAxisAngle(
          new THREE.Vector3(0, 0, 1), SM.rollDeg * Math.PI / 180));
      }
      var off = new THREE.Vector3().fromArray(SM.offset);
      if (isMirrored(itemId, hand)) {
        mirrorQuat(q);
        mirrorVec(off);
      }
      mesh.quaternion.copy(q);
      mesh.position.copy(off);
    } else {
      // stand-in: face outward on its side of the body, outside the weapon anchor
      var ip = window.WH_CONFIG.moveset.idlePose;
      var side = hand === 'left' ? -1 : 1;
      this.yawFrame.add(mesh);
      mesh.rotation.set(0, side * (ip.pos[0] > 0 ? 1 : -1) * Math.PI / 2, 0);
      mesh.position.set(side * ip.pos[0], ip.pos[1], ip.pos[2]);
    }
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
    if (!this.hasCaster()) return false;   // Order B: casting implement in either hand
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

  // 10-04 chain gating (Nicko: combo spam -> real chains). Windup presses
  // are IGNORED; strike/recover presses are BUFFERED for inputBufferSec and
  // fired by update() once the swing reaches its chain window. A press while
  // idle always starts the chain at chain[0].
  Player.prototype.tryAttack = function () {
    if (this.state !== 'alive' || this.rolling || this.toggling) return;
    if (!this.hasMeleeRight()) return;     // Order B: chain needs melee in the RIGHT hand
    if (this.blocking) return;              // v6: must release RMB to attack
    if (this.attacking) {
      var stage = this.getAttackStage();
      if (stage === 'strike' || stage === 'recover') {
        this.comboQueued = true;
        this.comboBufferTimer = MV.inputBufferSec;
      }
      return;
    }
    this.startAttack(0);
  };

  // Starts chain move `nextIndex` (default 0) with its own CONFIG timings.
  Player.prototype.startAttack = function (nextIndex) {
    var idx = (typeof nextIndex === 'number') ? nextIndex : 0;
    if (idx >= this.getChainCap()) idx = 0;
    var M = this.getChainMove(idx);
    if (this.stamina < M.staminaCost) return false;
    this.spendStamina(M.staminaCost);
    this.attacking = true;
    this.attackMoveId = this.getWeaponDef().chain[idx];
    this.attackMove = M;
    this.attackTotal = M.windup + M.strike + M.recover;
    this.attackTimer = this.attackTotal;
    this.attackSerial++;
    this.attackDidHit = false;
    this.lungeLeft = M.lunge;
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
    this.comboIndex = idx;
    if (this.comboIndex === 0) this.chainHits = 0;  // v7: reset hit counter on chain reset
    else this.chainHits = Math.max(this.chainHits, this.comboIndex);  // sync with chain position
    this.comboQueued = false;
    this.comboBufferTimer = 0;
    this.recoverFullyElapsed = false;
    // face camera direction on attack (unless locked: windup tracking handles it)
    if (!this.lockTarget) this.yaw = this.camYaw + Math.PI;
    return true;
  };

  // Ends the current swing and resets the chain (roll-out-of-recover,
  // weapon swap). Armed finisher state is untouched.
  Player.prototype.cancelAttack = function () {
    this.attacking = false;
    this.attackTimer = 0;
    this.lungeLeft = 0;
    this.comboIndex = 0;
    this.comboQueued = false;
    this.comboBufferTimer = 0;
    this.chainHits = 0;
    this.recoverFullyElapsed = true;
    this.resetWeaponPose();
  };

  // 10-04: stage + phase clock of the current swing from its CONFIG move.
  // Returns null or { stage, t (s into stage), dur, p (0..1), durations }.
  Player.prototype.getAttackPhase = function () {
    if (!this.attacking || !this.attackMove) return null;
    var M = this.attackMove;
    var elapsed = this.attackTotal - this.attackTimer;
    var stage, start;
    if (elapsed < M.windup) { stage = 'windup'; start = 0; }
    else if (elapsed < M.windup + M.strike) { stage = 'strike'; start = M.windup; }
    else { stage = 'recover'; start = M.windup + M.strike; }
    var dur = M[stage];
    var t = elapsed - start;
    return { stage: stage, t: t, dur: dur,
             p: dur > 0 ? Math.max(0, Math.min(1, t / dur)) : 1,
             durations: { windup: M.windup, strike: M.strike, recover: M.recover } };
  };

  // v3 D1: attack stage from elapsed time. 'windup' | 'strike' | 'recover' | null.
  Player.prototype.getAttackStage = function () {
    var ph = this.getAttackPhase();
    return ph ? ph.stage : null;
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
  // range, halfAngle, damage, ghoulMult, moveId}. v3: the active window is
  // the whole STRIKE stage (the sweep consumes once). 10-04: range / arc /
  // damage come from the CONFIG move of the CURRENT swing (thrust = narrow
  // and long, slashes = wide and short).
  Player.prototype.consumeAttackSweep = function () {
    if (!this.attacking || this.attackDidHit) return null;
    if (this.getAttackStage() !== 'strike') return null;
    this.attackDidHit = true;
    var M = this.attackMove;
    return {
      origin: this.pos.clone(),
      dir: new THREE.Vector3(Math.sin(this.yaw), 0, Math.cos(this.yaw)),
      range: M.range,
      halfAngle: deg2rad(M.halfAngleDeg),
      damage: M.damage * (this.pendingDamageMult || 1),
      ghoulMult: M.damageGhoulMult || 1,
      moveId: this.attackMoveId
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
        // Order B: the Q swap lands on completion. Inventory-only source,
        // re-checked here (the screen may have moved it meanwhile).
        var qItem = this.pendingQSwap;
        this.pendingQSwap = null;
        if (qItem) this.equipItem(qItem, 'left', true);
      }
    }
    if (this.regripTimer > 0) this.regripTimer = Math.max(0, this.regripTimer - dt);
    if (this.castCooldown > 0) this.castCooldown = Math.max(0, this.castCooldown - dt);
    // armed finisher window decays; expiry clears armed AND crossArmed
    if (this.armedTimer > 0) {
      this.armedTimer = Math.max(0, this.armedTimer - dt);
      if (this.armedTimer <= 0) this.crossArmed = false;
    }
    // Order B: a guard needs a shield in hand
    if (this.blocking && !this.hasShield()) this.endBlock();

    if (this.state === 'dying') {
      this.deathTilt = Math.min(Math.PI / 2, this.deathTilt + dt * 3);
      if (this.body && !this.anim) this.body.rotation.x = -this.deathTilt;
      if (this.anim) this.anim.death();
      if (this.stateTime >= CFG.respawnDelay) this.state = 'dead';
      return;
    }

    if (this.attacking) {
      this.attackTimer -= dt;
      // 10-04: buffered input expires after inputBufferSec.
      if (this.comboQueued) {
        this.comboBufferTimer -= dt;
        if (this.comboBufferTimer <= 0) { this.comboQueued = false; this.comboBufferTimer = 0; }
      }
      // Chain window: a fresh buffered press fires the NEXT chain move once
      // this swing is chainOpenSec into its recover. The last chain move has
      // no early window - it must resolve its full recover (below).
      var ph = this.getAttackPhase();
      var lastMove = this.comboIndex >= this.getChainCap() - 1;
      if (this.comboQueued && !lastMove && ph.stage === 'recover' &&
          ph.t >= this.attackMove.chainOpenSec) {
        this.startAttack(this.comboIndex + 1);
      }
      if (this.attacking && this.attackTimer <= 0) {
        var rebuffered = this.comboQueued;
        this.attacking = false;
        this.recoverFullyElapsed = true;
        this.comboIndex = 0;
        this.chainHits = 0;
        this.comboQueued = false;
        this.comboBufferTimer = 0;
        // chain fully resolved: a still-fresh press starts a new chain
        if (rebuffered) this.startAttack(0);
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
        if (this.attacking) speed *= this.getWeaponDef().moveMultWhileAttacking[this.getAttackStage()] || 0;
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

    // Strike lunge along facing (FSM-owned for both the clip and stand-in
    // paths): velocity = move.lunge / move.strike, dt-scaled so the full
    // lunge drains at any frame rate. Runs before the bounds clamp.
    if (this.attacking && this.getAttackStage() === 'strike' && this.lungeLeft > 0) {
      var lungeVel = this.attackMove.lunge / this.attackMove.strike;
      var lungeStep = Math.min(lungeVel * dt, this.lungeLeft);
      this.pos.x += Math.sin(this.yaw) * lungeStep;
      this.pos.z += Math.cos(this.yaw) * lungeStep;
      this.lungeLeft -= lungeStep;
    }

    if (clampToBounds) clampToBounds(this);
    this.yawFrame.rotation.y = this.yaw;

    // Legacy pivot poses remain only for the rigid stand-in fallback.
    // 10-04: phase clocks come from the current CONFIG move; the pose shape
    // (and its bodyLean/crouch) from WH_MOVESET[move.pose].
    if (this.body && !this.anim) {
      if (this.attacking) {
        var MS = window.WH_MOVESET;
        var aph = this.getAttackPhase();
        var stage = aph.stage;
        var move = MS[this.attackMove.pose] || MS.m1;
        if (stage === 'windup') {
          var we = smooth(aph.p);
          this.body.rotation.x = AW.windupLean * we;           // lean back
          this.atkYawOffset = 0;
          this.body.rotation.y = this.atkYawOffset;
          this.body.rotation.z = 0;
          this.body.position.y = this.bodyBaseY - move.crouch * we;  // per-pose crouch
          this.body.position.x = this.bodyBaseX || 0;
          var pw = MS.interpPose(MS.idle, move.windup, we);
          this.weaponPivot.position.set(pw.pos[0], pw.pos[1], pw.pos[2]);
          this.weaponPivot.rotation.set(pw.rot[0], pw.rot[1], pw.rot[2]);
        } else if (stage === 'strike') {
          var se = 1 - (1 - aph.p) * (1 - aph.p);              // ease-out
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
        } else {                                                // recover
          var re = smooth(aph.p);
          var swing = deg2rad(AW.strikeYawSweepDeg) * 0.5;      // sweep end offset
          this.atkYawOffset = swing * (1 - re);                 // ease back to neutral
          this.body.rotation.y = this.atkYawOffset;
          this.body.rotation.x = move.bodyLean * re;            // per-pose forward-lean settle
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
    if (!this.attacking) this.lungeLeft = 0;

    this.root.position.copy(this.pos);
  };

  Player.prototype.updateCamera = function (dt) {
    // orbit camera behind player
    var target = this.pos.clone();
    target.y += CFG.camHeight;
    // R5 P0-5: distance-by-pitch cap (steeper down-look = closer camera):
    // cap = camMaxDistance * (1 - camPitchDistShrink * max(0, sin(pitch)))
    // effective = clamp(camDist, camMinDistance, cap); camDist (wheel state)
    // is never written here. Camera y floor = ground (y = 0) + clearance.
    var pitchCap = Math.max(CFG.camMinDistance, CFG.camMaxDistance *
      (1 - CFG.camPitchDistShrink * Math.max(0, Math.sin(this.camPitch))));
    var effDist = Math.max(CFG.camMinDistance, Math.min(pitchCap, this.camDist));
    var floorY = CFG.camGroundClearance;
    var offset = new THREE.Vector3(
      Math.sin(this.camYaw) * Math.cos(this.camPitch),
      Math.sin(this.camPitch),
      Math.cos(this.camYaw) * Math.cos(this.camPitch)
    ).multiplyScalar(effDist);
    var want = target.clone().add(offset);
    if (want.y < floorY) want.y = floorY;

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
      if (want.y < floorY) want.y = floorY;
      this.camera.position.lerp(want, lerp);
    } else {
      // 10-04 change order (Nicko): FULL camera decoupling - movement NEVER
      // turns the camera. camYaw changes only from mouse drag / camera
      // joystick (both stamp lastManualCamT); lock-on keeps its own framing
      // above. The old v3.1 movement auto-follow is gone.
      var lerp2 = 1 - Math.exp(-CFG.camFollowLerp * dt);
      this.camera.position.lerp(want, lerp2);
    }
    if (this.camera.position.y < floorY) this.camera.position.y = floorY;
    this.camera.lookAt(target);
  };

  // 2026-10-03 change order (Nicko): spawn faces the map center, not away
  // from it. Orient body yaw toward (tx, tz) and swing camYaw with it so the
  // screen-forward invariant (idle body yaw = camYaw + PI, camera trails the
  // back) stays intact - W still walks screen-forward, now toward the center.
  Player.prototype.faceTowards = function (tx, tz) {
    var dx = tx - this.pos.x, dz = tz - this.pos.z;
    if (dx * dx + dz * dz < 0.0001) return;
    this.yaw = Math.atan2(dx, dz);
    this.camYaw = this.yaw + Math.PI;
    if (this.yawFrame) this.yawFrame.rotation.y = this.yaw;
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
    this.pendingQSwap = null;              // Order B: hands themselves persist through death
    this.castWindup = 0;
    this.castCooldown = 0;
    this.regripTimer = 0;
    this.pendingSpellId = null;
    this.armedTimer = 0;
    this.crossArmed = false;
    this.atkYawOffset = 0;
    this.faceTowards(0, 0);                // respawn faces map center (Nicko 10-03)
    this.yawFrame.rotation.y = this.yaw;
    if (this.anim) this.anim.revive();
    if (this.body && !this.anim) { this.body.rotation.x = 0; this.body.rotation.y = this.atkYawOffset; }
  };

  window.WH_Player = Player;
})();