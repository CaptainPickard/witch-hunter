// Witch Hunter prototype v2 - third-person player controller.
// D2: movement basis is CAMERA yaw (W = camera forward on screen, S = back,
// A/D = strafe). v1 had the strafe right-vector inverted; fixed.
// D3: souls-style lock-on: camera follow, strafe; idle lock faces the target
// (combat-ds1 P0-4: windup tracking is rate-limited, strike/recover frozen).
// whanim2: skinned bodies are posed by WH_CharacterAnim clips; the procedural
// pose code below is the rigid stand-in fallback. All tunables from CONFIG.

(function () {
  'use strict';

  var CFG = window.WH_CONFIG.player;
  var MCFG = window.WH_CONFIG.mouse || {};   // v8: mouse-bind config lives at
                                             // the WH_CONFIG root (mirrors the
                                             // CONFIG.touch convention)
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

    // v8: pointer-lock mouse bind state (io/specs/mouse-bind-cam-spec.md 5)
    this.mouseBound = false;          // desired/actual bind state, synced via
                                      // pointerlockchange (single source of truth)
    this.mouseChipEl = null;          // HUD chip element, cached in initInput

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
    // meshRoot is the assets.js ground-align holder; stand-in bob/tilt
    // writes are offsets from its placement, so keep that base.
    this.bodyBaseY = meshRoot.position.y || 0;
    this.bodyBaseX = meshRoot.position.x || 0;
    this.yawFrame.add(this.body);
    if (window.WH_ASSETS.getClips('playerBody').length) {
      this.anim = new window.WH_CharacterAnim(meshRoot, window.WH_ASSETS.getClips('playerBody'),
        { variant: 'sword' });
    }
  };

  // The skinned hand is the socket. Only stand-ins retain the old rigid pivot.
  Player.prototype.setWeapon = function (mesh) {
    var hand = this.body && this.body.getObjectByName('R_Hand');
    // 10-04: re-equip drops the previous mesh / stand-in pivot first.
    if (this.sword && this.sword !== mesh && this.sword.parent) this.sword.parent.remove(this.sword);
    if (this.weaponPivot) { this.yawFrame.remove(this.weaponPivot); this.weaponPivot = null; }
    this.sword = mesh;
    this.swordBaseEmissive = null;   // armed-glow base re-sampled per mesh
    if (hand) {
      this.weaponHand = hand;
      hand.add(mesh);
      mesh.position.set(0, 0, 0);
      // Grip mount (2026-10-03 re-measure): the longsword GLB's blade tip
      // lies along mesh-local -Y, and the fist's grip-forward direction is
      // hand-local +Z, so map -Y -> +Z with a CONSTANT local-space
      // quaternion. The old world-quaternion math sampled the rest pose at
      // setWeapon time, letting the animation pose leak in -- blade ended up
      // parallel to the forearm with the hilt on the wrong end. This mount
      // is pose-independent, so it holds through idle, walk, and swings.
      var wm = window.WH_CONFIG.assets.weaponMount;
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
      }
      mesh.quaternion.copy(mountRotation);
      // Grip anchor (Nicko 10-03): the instance is a groundAlign HOLDER whose
      // inner mesh was lifted so the GLB's raw min-Y rests at holder y=0 -
      // which put the sword TIP at/behind the fist (hand on mid-blade, hilt
      // floating behind: "hilt at the opposite end"). Slide the INNER mesh
      // down by the measured grip height in HOLDER-LOCAL Y (the mount
      // rotation maps holder -Y to hand-local +Z grip-forward, so a -Y
      // shift moves the grip ONTO the fist and the tip forward in front).
      // Measured: sword grip at raw y~+0.65 -> holder y 1.637 (CONFIG).
      // Offset is in raw GLB units and scales with the weapon correctly.
      var gripY = (wm && wm.gripHolderY) ? (wm.gripHolderY[this.weaponId] || 0) : 0;
      if (gripY && mesh.children[0]) {
        mesh.children[0].position.y -= gripY;
      }
      return;
    }
    this.weaponPivot = new THREE.Group();
    this.yawFrame.add(this.weaponPivot);
    this.weaponPivot.add(mesh);
    this.swordBase = window.WH_CONFIG.moveset.idlePose;
    this.resetWeaponPose();
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
  // new weapon instance so the hand mount follows the weapon id.
  Player.prototype.equipWeapon = function (id, mesh) {
    if (!MV.weapons[id]) return false;
    this.cancelAttack();
    this.weaponId = id;
    if (mesh) this.setWeapon(mesh);
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
      // v8: Backquote toggles the pointer-lock mouse bind (spec section 5;
      // Esc is NOT handled here - the native exit resyncs via pointerlockchange)
      if (e.code === 'Backquote' && !e.repeat) self.toggleMouseBind();
    });
    document.addEventListener('keyup', function (e) {
      self.keys[e.code] = false;
    });
    document.addEventListener('mousedown', function (e) {
      if (e.button === 0) {
        // v8: UI clicks (chip and any non-canvas DOM) are UI-only - no attack,
        // no drag start, no auto-rebind. The chip's own click handler toggles
        // bind via the chip path (N6); the canvas auto-rebind path (N5) only
        // ever arms from real canvas-surface presses.
        if (!e.target || e.target.id !== 'wh-canvas') return;
        self.tryAttack();
        // v8: auto-rebind on a canvas-surface LMB while free (spec section 5);
        // rides along with the attack - drag-start lines below stay untouched.
        if (!self.lockTarget && !self.mouseBound &&
            MCFG.autoBindOnCanvasClick) {
          self.bindMouse();
        }
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
      if (self.lockTarget) return;            // lock-on owns the camera (keep)
      if (self.mouseBound && document.pointerLockElement) {
        var mdx = e.movementX || 0, mdy = e.movementY || 0;
        if (mdx === 0 && mdy === 0) return;
        self.lastManualCamT = performance.now() / 1000;
        self.applyCamDelta(mdx * (MCFG.pointerLockSensMult != null ? MCFG.pointerLockSensMult : 1.0),
                           mdy * (MCFG.pointerLockSensMult != null ? MCFG.pointerLockSensMult : 1.0));
        return;
      }
      if (!self.dragging) return;             // free mouse: no drag, no camera
      var dx = e.clientX - self.lastDragX;
      var dy = e.clientY - self.lastDragY;
      self.lastDragX = e.clientX;
      self.lastDragY = e.clientY;
      if (dx !== 0 || dy !== 0) self.lastManualCamT = performance.now() / 1000;
      self.applyCamDelta(dx, dy);
    });
    document.addEventListener('wheel', function (e) {
      self.camDist += (e.deltaY > 0 ? 1 : -1) * 0.8;
      self.camDist = Math.max(CFG.camMinDistance, Math.min(CFG.camMaxDistance, self.camDist));
    }, { passive: true });
    // v8: pointer lock state is the single source of truth for mouseBound -
    // fires on bind, on Esc/native exit, on request failure. NO Esc key handler.
    document.addEventListener('pointerlockchange', function () {
      self.syncMouseChip();
    });
    // v8: HUD chip toggle (pointer-events:auto on the chip in style.css)
    var chip = document.getElementById('wh-mouse-chip');
    if (chip) {
      this.mouseChipEl = chip;
      chip.addEventListener('click', function (ev) {
        ev.preventDefault();
        self.toggleMouseBind();
      });
    }
  };

  // v8 pointer-lock mouse bind (io/specs/mouse-bind-cam-spec.md section 5)

  Player.prototype.applyCamDelta = function (dxPx, dyPx) {
    this.camYaw -= dxPx * deg2rad(CFG.mouseSensDegPerPx);
    this.camPitch += dyPx * deg2rad(CFG.mouseSensDegPerPx);
    this.camPitch = Math.max(deg2rad(CFG.camPitchMinDeg),
      Math.min(deg2rad(CFG.camPitchMaxDeg), this.camPitch));
  };

  Player.prototype.bindMouse = function () {
    if (document.pointerLockElement || !document.body.requestPointerLock) return;
    var el = document.getElementById('wh-canvas');
    var self = this;
    var res = null;
    try {
      res = el.requestPointerLock();
    } catch (e) {
      // N7: sync-throw fault injection must never surface uncaught
      this.syncMouseChip();
      return;
    }
    if (res && typeof res.then === 'function') {
      res.then(function () { self.syncMouseChip(); },
               function () { self.syncMouseChip(); });
    }
  };

  Player.prototype.unbindMouse = function () {
    if (document.pointerLockElement) document.exitPointerLock();
    this.syncMouseChip();
  };

  Player.prototype.toggleMouseBind = function () {
    this.mouseBound ? this.unbindMouse() : this.bindMouse();
  };

  Player.prototype.syncMouseChip = function () {
    this.mouseBound = !!document.pointerLockElement;
    if (this.mouseChipEl) {
      this.mouseChipEl.textContent =
        this.mouseBound ? 'MOUSE: BOUND [`]' : 'MOUSE: FREE [`]';
    }
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

  // v7: guard-break choke point (called from resolveIncomingHit when a
  // blocked hit empties stamina, and by game debug hooks). Clears
  // armed/cross state.
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
    // chain reset (spec: toggle resets the active chain; A-1 ruling
    // 2026-10-02: a full reset also ENDS the chain, so an idle toggle no
    // longer starts the next chain at m2 — same bookkeeping as a full
    // recover, without touching the armedTimer/cross banking below)
    this.endCombo();
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
  // Returns true when hp damage (full or chip) was applied.
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
        var dyaw = shortestAngle(Math.atan2(dx, dz) - this.yaw);
        attackerInArc = Math.abs(dyaw) <= deg2rad(BLK.blockArcHalfAngleDeg);
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
      // takeDamage() reports whether hp was applied, not whether the chip
      // killed; the guard break keys off the post-hit state instead.
      var applied = this.takeDamage(chip);
      if (this.stamina <= 0 && this.state === 'alive') {
        this.guardBreak();                   // stun, block off, armed cleared
      } else if (this.onBlock) {
        this.onBlock(attacker, chip);
      }
      return applied;
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

  // Strike root motion along facing: velocity model. The old target-delta
  // formula (strikeLunge * se - (strikeLunge - lungeLeft)) stranded the
  // remainder whenever the STRIKE stage spanned few frames (hitches clamped
  // at maxDt), leaving the lunge at ~0.09 of 0.25. A dt-scaled velocity
  // drains the full lunge at any frame rate, on the clip and stand-in paths.
  Player.prototype.applyStrikeLunge = function (dt) {
    if (this.lungeLeft <= 0) return;
    var lungeVel = AW.strikeLunge / (CFG.attackDuration * AW.strikeFrac);
    var lungeStep = Math.min(lungeVel * dt, this.lungeLeft);
    this.pos.x += Math.sin(this.yaw) * lungeStep;
    this.pos.z += Math.cos(this.yaw) * lungeStep;
    this.lungeLeft -= lungeStep;
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
    this.attackTimer = 0;
    this.attackDidHit = false;
    this.lungeLeft = 0;
    this.endCombo();                        // a death mid-chain must not carry comboIndex/chainHits
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
    this.faceTowards(0, 0);                // respawn faces map center (Nicko 10-03)
    this.yawFrame.rotation.y = this.yaw;
    if (this.anim) this.anim.revive();
    if (this.body && !this.anim) { this.body.rotation.x = 0; this.body.rotation.y = this.atkYawOffset; }
  };

  window.WH_Player = Player;
})();