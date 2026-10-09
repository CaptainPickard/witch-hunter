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
  var ER = window.WH_CONFIG.combat.er; // EPR1: ER-parity input grammar / backstep / guard raise
  var GATE_EPS = 1e-6;                // EPR1: float slack - a cancel point hit exactly counts as reached

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
    this.backstep = false;            // EPR1: no-direction dodge tap = backwards hop
    this.backstepTimer = 0;
    // EPR1: keyboard Space grammar (tap = dodge on release, hold = sprint),
    // sampled once per sim frame by sampleDodgeInput()
    this.dodgeKeyDown = false;        // raw Space state from key events
    this.dodgePressLatch = false;     // a press since the last sim-frame sample
    this.dodgeHeld = false;           // sampled hold in progress
    this.dodgeHoldMs = 0;             // integer ms held (sum of round(dt * 1000))
    this.dodgeSprint = false;         // hold reached combat.er.dodgeHoldSec
    this.dodgeQueued = false;         // dodge waiting for the swing's dodge cancel point
    this.dodgeDir = { x: 0, z: 0 };   // input direction at the queued release (0 = none)
    this.attacking = false;
    this.attackTimer = 0;
    this.attackDidHit = false;
    this.bobPhase = 0;
    this.idleTime = 0;                // seconds without movement input
    this.idlePhase = 0;               // breathing phase
    this.lungeLeft = 0;               // strike lunge distance remaining
    this.rootMotionApplied = 0;       // EPR1: metres of the swing's rootMotion table applied
    this.rootMotionStage = null;      // EPR1: stage the frame-anchored progress tracks
    this.rootMotionT0 = 0;            // EPR1: first sampled time into that stage
    this.rootMotionSpan = 0;          // EPR1: last-frame time minus rootMotionT0
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
    this.blockActive = false;         // EPR1-A3: guard raised (guardRaiseSec after accept); hit checks read this
    this.guardRaiseTimer = 0;         // EPR1: seconds until blockActive
    this.guardQueued = false;         // EPR1: RMB held in a swing, before its guard cancel point

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
    this.pendingQSwapHand = 'left';   // AB1: the hand pendingQSwap lands in (bar item slots)
    // AB1: getter for the HUD-owned action bar map (game.js sets it; null =
    // CONFIG.actionbar.defaults). Read through actionSlot(i) only.
    this.actionMapSource = null;
    // R-64.4: the picked class's bar defaults (CONFIG.startingClasses[id]
    // .belt); null = CONFIG.actionbar.defaults (no class / old saves).
    this.actionDefaults = null;
    // Order C (2026-10-05) dual-wield casting: fully independent per-hand
    // cast state ('main' = right hand, 'off' = left hand). Both hands may be
    // mid-windup at once; each completes and cools down on its own.
    this.cast = { main: newCastState(), off: newCastState() };
    // two pointers into the ONE belt list (0-based slot index per hand):
    // Digit1-5 sets main, Shift+Digit1-5 sets off
    this.bindings = { main: 0, off: 0 };
    this.belt = V7.belt.defaultSpells.slice();          // spell ids / null
    this.consumables = [{ id: 'healthPotion', charges: V7.consumable.healthPotion.charges }, null];
    this.casterGlows = null;          // { right, left } glow orbs per hand (game.js)
    // Order B (2026-10-05) free per-hand equip: one gear item id (or null)
    // per hand, single instances (an item is in a hand OR the inventory).
    // Combat reads ONLY CONFIG.items[id].kind per hand (Order C:
    // handAction - LMB acts with the right hand, RMB with the left). Belt
    // keys bind spells to hands and never touch the hands.
    this.hands = { right: null, left: null };
    this.inventory = null;            // game.js setupInventory wires the Inventory
    this.itemMeshes = {};             // item id -> its hand mesh (game.js instances)
    this.handMeshes = {};             // stage 2: per-hand item meshes { right, left } (torch: both hands at once)
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

    // v8: pointer-lock mouse bind state (io/specs/mouse-bind-cam-spec.md 5)
    this.mouseBound = false;          // desired/actual bind state, synced via
                                      // pointerlockchange (single source of truth)
    this.mouseChipEl = null;          // HUD chip element, cached in bindInput

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
    // meshRoot is the assets.js ground-align holder; stand-in bob/tilt
    // writes are offsets from its placement, so keep that base.
    this.bodyBaseY = meshRoot.position.y || 0;
    this.bodyBaseX = meshRoot.position.x || 0;
    this.yawFrame.add(this.body);
    if (window.WH_ASSETS.getClips('playerBody').length) {
      // DAG: + the WH_Dag* chain clips from the clip-source GLB (same rig);
      // only dagger move ids reach them (anim.js MOVE_NAMES).
      var dagClips = window.WH_ASSETS.getClips('playerDagClips').filter(function (c) {
        return /^WH_Dag/.test(c.name);
      });
      this.anim = new window.WH_CharacterAnim(meshRoot,
        window.WH_ASSETS.getClips('playerBody').concat(dagClips), { variant: 'sword' });
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

  // S3 tweak: shared scratch for the per-frame torch-carry overlay (avoids
  // per-frame allocations in applyTorchCarryPost). Unit +X axis forever.
  var AX_X = new THREE.Vector3(1, 0, 0);
  var TORCH_Q_SCRATCH = new THREE.Quaternion();

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
    // DAG: the mesh's own weapon def. Right hand = the wielded moveset
    // (this.weaponId, as before - also the WH_DEBUG.equipWeapon mesh swap);
    // a melee item carried LEFT while another melee is wielded right (e.g.
    // longsword left + dagger right) keeps its own moveset's grip + blade
    // axis (longsword -Y vs dagger +Y) instead of the right hand's.
    var leftMv = hand === 'left' && this.hasMeleeRight() &&
      itemDef(itemId) && itemDef(itemId).moveset;
    var wid = leftMv && MV.weapons[leftMv] ? leftMv : this.weaponId;
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
      var gripY = (wm && wm.gripHolderY) ? (wm.gripHolderY[wid] || 0) : 0;
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
        var bladeY = (MV.weapons[wid] || this.getWeaponDef()).bladeAxisY || -1;
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
      // v8: Backquote toggles the pointer-lock mouse bind (spec section 5;
      // Esc is NOT handled here - the native exit resyncs via pointerlockchange).
      // Ahead of the inventory gate so it can always unbind; bindMouse itself
      // refuses while the screen is open.
      if (e.code === 'Backquote' && !e.repeat) self.toggleMouseBind();
      if (self.inputSuspended) return;   // 10-05: inventory screen open
      if (e.code === 'Space') {
        e.preventDefault();
        // EPR1 (A1-A3): the dodge acts on RELEASE (sampleDodgeInput); latch the
        // press so a down+up inside one sim frame still counts as a tap.
        if (!e.repeat) { self.dodgeKeyDown = true; self.dodgePressLatch = true; }
      }
      if (e.code === 'KeyF' && !e.repeat) {
        e.preventDefault();
        if (self.onLockToggle) self.onLockToggle();  // game.js decides engage/break
      }
      // v7: Q = loadout toggle (busy window, resets chain, keeps armed).
      // Order B: swaps the left hand glove <-> shield.
      if (e.code === 'KeyQ' && !e.repeat) self.toggleLoadout();
      // AB1: Digit1-5 = action bar slot select (spell slot -> MAIN binding,
      // item slot -> equip); Shift+Digit1-5 = OFF binding on spell slots
      // (Order C semantics, never touches hands/chain/armed)
      if (e.code.indexOf('Digit') === 0 && !e.repeat) {
        var n = parseInt(e.code.slice(5), 10);
        if (n >= 1 && n <= V7.actionbar.slots) self.selectActionSlot(n - 1, e.shiftKey);
      }
      // v7: R / T = consumable belt slots 1 / 2
      if (e.code === 'KeyR' && !e.repeat) self.useConsumable(0);
      if (e.code === 'KeyT' && !e.repeat) self.useConsumable(1);
    });
    document.addEventListener('keyup', function (e) {
      self.keys[e.code] = false;
      if (e.code === 'Space') self.dodgeKeyDown = false;   // EPR1: release -> sampleDodgeInput
    });
    document.addEventListener('mousedown', function (e) {
      if (self.inputSuspended) return;   // 10-05: clicks belong to the inventory screen
      // Order C: LMB = main-hand action, RMB = off-hand action
      // (CONFIG.equip.twoHand), both through handButton
      if (e.button === 0) {
        // v8: UI clicks (chip and any non-canvas DOM) are UI-only - no attack,
        // no drag start, no auto-rebind. The chip's own click handler toggles
        // bind via the chip path (N6); the canvas auto-rebind path (N5) only
        // ever arms from real canvas-surface presses.
        if (!e.target || e.target.id !== 'wh-canvas') return;
        self.handButton('lmb', true);
        // v8: auto-rebind on a canvas-surface LMB while unbound (spec section 5);
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
      if (e.button === 2) {
        e.preventDefault();
        self.handButton('rmb', true);
      }
    });
    document.addEventListener('mouseup', function (e) {
      if (e.button === 0) {
        self.dragging = false;
        self.handButton('lmb', false);
      }
      // v7: release ends a held block (no-op otherwise)
      if (e.button === 2) self.handButton('rmb', false);
    });
    // v6: RMB must not open the browser context menu
    document.addEventListener('contextmenu', function (e) {
      e.preventDefault();
      e.stopPropagation();
      return false;
    });
    document.addEventListener('mousemove', function (e) {
      if (self.lockTarget) return;            // lock-on owns the camera (keep)
      if (self.inputSuspended) return;        // 10-05: inventory screen open - camera input ignored
      if (self.mouseBound && document.pointerLockElement) {
        var mdx = e.movementX || 0, mdy = e.movementY || 0;
        if (mdx === 0 && mdy === 0) return;
        self.lastManualCamT = performance.now() / 1000;
        self.applyCamDelta(mdx * (MCFG.pointerLockSensMult != null ? MCFG.pointerLockSensMult : 1.0),
                           mdy * (MCFG.pointerLockSensMult != null ? MCFG.pointerLockSensMult : 1.0));
        return;
      }
      if (!self.dragging) return;             // unbound mouse: no drag, no camera
      var dx = e.clientX - self.lastDragX;
      var dy = e.clientY - self.lastDragY;
      self.lastDragX = e.clientX;
      self.lastDragY = e.clientY;
      if (dx !== 0 || dy !== 0) self.lastManualCamT = performance.now() / 1000;
      self.applyCamDelta(dx, dy);
    });
    document.addEventListener('wheel', function (e) {
      if (self.inputSuspended) return;
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
    if (this.inputSuspended) return;  // 10-05 Order A: never lock over the open inventory screen
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
        this.mouseBound ? 'MOUSE: BOUND [`]' : 'MOUSE: UNBOUND [`]';
    }
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
    // EPR1 (A3): a held dodge (>= combat.er.dodgeHoldSec) sprints like Shift
    this.sprinting = !!(k['ShiftLeft'] || k['ShiftRight']) || this.dodgeSprint;
  };

  // 10-05 inventory Order A: suspend / restore player input. Suspending
  // drops an active camera drag and a held guard (RMB release would land
  // on the open screen); anything already in flight (swing, roll, cast
  // windup) plays out. Restore is instant - nothing to rebuild.
  // v8: the open screen owns the cursor - opening it unbinds a bound mouse
  // (CONFIG.mouse.unbindOnUiOpen), closing it rebinds an unbound mouse
  // when CONFIG.mouse.rebindOnUiClose is on.
  Player.prototype.setInputSuspended = function (on) {
    var wasSuspended = this.inputSuspended;
    this.inputSuspended = !!on;
    if (on) {
      this.dragging = false;
      this.endBlock();
      if (MCFG.unbindOnUiOpen) this.unbindMouse();
    } else if (wasSuspended && MCFG.rebindOnUiClose && !this.mouseBound) {
      this.bindMouse();
    }
  };

  // 10-04 (Nicko, souls-style): roll cancels attack RECOVER only - windup
  // and strike are committed. Attack cannot start during roll. v7: also
  // refused during the loadout toggle busy window.
  Player.prototype.tryRoll = function () {
    this.requestDodge(false);
  };

  // EPR1: single dodge entry. allowBackstep = keyboard tap, where a tap
  // with no move direction from neutral is a backstep. During a swing the
  // dodge is queued from any stage and rolls out at the move's dodge cancel
  // point (CONFIG move.cancel.dodge replaces the 10-04 recover-only rule);
  // it replaces a buffered LMB (latest input wins). Refused during a roll /
  // backstep and (v7) during the loadout toggle busy window.
  Player.prototype.requestDodge = function (allowBackstep) {
    if (this.state !== 'alive' || this.rolling || this.backstep || this.toggling) return;
    var dir = this.inputDirWorld();
    if (this.attacking) {
      this.dodgeQueued = true;
      this.dodgeDir.x = dir ? dir.x : 0;
      this.dodgeDir.z = dir ? dir.z : 0;
      this.comboQueued = false;
      this.comboBufferTimer = 0;
      if (this.cancelOpen('dodge')) this.consumeQueuedDodge();
      return;
    }
    if (!dir && allowBackstep) this.startBackstep();
    else this.startRoll(dir);
  };

  // EPR1: fire the queued dodge (dodge point reached, or the swing is over)
  // as a ROLL: live input direction, else the direction at release, else
  // facing. Refused (dead / toggling / stamina) it is dropped, swing kept.
  Player.prototype.consumeQueuedDodge = function () {
    this.dodgeQueued = false;
    if (this.state !== 'alive' || this.toggling) return;
    if (this.stamina < CFG.rollStaminaCost) return;
    var dir = this.inputDirWorld();
    if (!dir && (this.dodgeDir.x !== 0 || this.dodgeDir.z !== 0)) dir = this.dodgeDir;
    if (this.attacking) this.cancelAttack();          // roll out of the swing (chain resets)
    this.startRoll(dir);
  };

  Player.prototype.startRoll = function (dir) {
    if (this.stamina < CFG.rollStaminaCost) return false;
    this.spendStamina(CFG.rollStaminaCost);
    this.rolling = true;
    this.rollTimer = CFG.rollDuration;
    this.iframes = CFG.rollIFrameWindow;
    this.endBlock();                        // v6: roll takes priority over block
    // roll direction: the input direction, or facing when there is none
    var d = new THREE.Vector3(dir ? dir.x : 0, 0, dir ? dir.z : 0);
    if (d.lengthSq() < 0.01) {
      d.set(Math.sin(this.yaw), 0, Math.cos(this.yaw));
    }
    d.normalize();
    this.rollDir.copy(d);
    return true;
  };

  // EPR1 (A2): backstep = procedural backwards hop along facing (update()
  // slides the group; no clip change), short i-frames, chain reset.
  Player.prototype.startBackstep = function () {
    var BS = ER.backstep;
    if (this.stamina < BS.staminaCost) return false;
    this.spendStamina(BS.staminaCost);
    this.backstep = true;
    this.backstepTimer = BS.duration;
    this.iframes = BS.iframes;
    this.endBlock();
    this.endCombo();
    return true;
  };

  // EPR1 (A1-A3, EPR1-A2/A6): keyboard Space grammar, sampled once per sim
  // frame by update(). A press latched since the last frame counts as held
  // for this frame, so a tap inside one frame still registers; its release
  // acts on the next frame. Hold time sums round(dt * 1000) ms per frame
  // (exactly 50 at the 20 Hz clamp): an integer boundary, no float drift.
  // Held >= dodgeHoldSec (inclusive: 7 frames = sprint side) sprints while
  // held and the release does nothing; a shorter hold dodges on release.
  Player.prototype.sampleDodgeInput = function (dt) {
    var down = this.dodgeKeyDown || this.dodgePressLatch;
    var holdMs = Math.round(ER.dodgeHoldSec * 1000);
    this.dodgePressLatch = false;
    if (down) {
      if (!this.dodgeHeld) { this.dodgeHeld = true; this.dodgeHoldMs = 0; }
      this.dodgeHoldMs += Math.round(dt * 1000);
      this.dodgeSprint = this.dodgeHoldMs >= holdMs;
      return;
    }
    if (!this.dodgeHeld) return;
    var tap = this.dodgeHoldMs < holdMs;
    this.dodgeHeld = false;
    this.dodgeHoldMs = 0;
    this.dodgeSprint = false;
    if (tap) this.requestDodge(true);
  };

  // v6: RMB down. Refused while rolling (EPR1: or backstepping), dying/dead,
  // or guard-broken. On success opens the parry window. Cannot re-block until
  // stamina has recovered past guardBreakMinStamina. EPR1 (B3, EPR1-A5):
  // blocking still flips on accept; the hit checks read blockActive, set
  // guardRaiseSec later. During a swing the held RMB is queued and accepted
  // at the move's guard cancel point (the swing plays out underneath).
  Player.prototype.tryBlock = function () {
    if (this.state !== 'alive' || this.rolling || this.attacking) return;
    if (this.toggling) return;              // Order B: the shield is mid-swap until Q lands
    if (!this.hasShieldLeft()) return;      // Order C: a shield in the LEFT hand
    if (this.guardBroken) return;
    if (this.stamina < window.WH_CONFIG.block.guardBreakMinStamina) return;
    if (this.attacking && !this.cancelOpen('guard')) {
      this.guardQueued = true;
      return;
    }
    this.comboQueued = false;               // EPR1: the raised guard wins the buffer
    this.comboBufferTimer = 0;
    this.blocking = true;
    this.blockActive = false;
    this.guardRaiseTimer = ER.guardRaiseSec;
    // L1 Shield / Defense rank: + up to 0.05 s at rank 100 (0 at rank 1)
    this.parryTimer = window.WH_CONFIG.block.parryWindow +
      (window.WH_LEVEL ? window.WH_LEVEL.skillPassive('shieldDefense', 'parryWindow') : 0);
  };

  Player.prototype.endBlock = function () {
    this.blocking = false;
    this.blockButton = null;
    this.blockActive = false;
    this.guardRaiseTimer = 0;
    this.guardQueued = false;
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
    this.selectItemEquip(target, 'left');
  };

  // AB1: the Q swap generalized - put item id into hand through the same
  // busy window (CONFIG.loadout.toggleSeconds), block drop, chain reset and
  // armed banking as Q. Inventory-only source (swap-parity: the outgoing
  // item returns to the inventory when the window lands, update()); not
  // owned = refusal toast, nothing changes. Returns true when the window
  // started.
  Player.prototype.selectItemEquip = function (id, hand) {
    if (this.state !== 'alive' || this.toggling) return false;
    if (!this.inventory || this.inventory.countOf(id) <= 0) {
      return this.refuseEquip(itemName(id) + ' not in inventory');
    }
    this.pendingQSwap = id;
    this.pendingQSwapHand = hand;
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
    return true;
  };

  // ---- AB1: player-mappable action bar ----------------------------------------
  // Entry { kind: 'spell' | 'item', id } in CONFIG.actionbar.slots slots. The
  // HUD (game.js) owns the map + editing; the player owns validation and
  // reads the map only through actionSlot(i).
  var BINDABLE_KINDS = ['melee', 'shield', 'caster', 'torch'];

  // Gear with a hand mount: same mesh rule as equipItem (dormant shields /
  // swords are not bindable), minus CONFIG.actionbar.pickerExclude.
  function isBindableItem(id) {
    var d = itemDef(id);
    if (!d || d.category !== 'gear' || !d.hands || !d.hands.length) return false;
    if (BINDABLE_KINDS.indexOf(d.kind) < 0) return false;
    if (!d.mesh && (d.kind === 'shield' || d.kind === 'melee')) return false;
    return (V7.actionbar.pickerExclude || []).indexOf(id) < 0;
  }

  function isSpellId(id) {
    return Object.prototype.hasOwnProperty.call(V7.spell, id) &&
      !!V7.spell[id] && typeof V7.spell[id] === 'object' && !!V7.spell[id].kind;
  }

  function validActionEntry(e) {
    if (!e || typeof e !== 'object' || typeof e.id !== 'string') return false;
    if (e.kind === 'spell') return isSpellId(e.id);
    if (e.kind === 'item') return isBindableItem(e.id);
    return false;
  }

  // The hand a bar item goes in: CONFIG.equip.nativeHand, else the first
  // allowed hand (shield / torch / glove -> left, longsword -> right).
  function actionHandOf(id) {
    var d = itemDef(id);
    var nat = window.WH_CONFIG.equip.nativeHand[id];
    return nat && d.hands.indexOf(nat) >= 0 ? nat : d.hands[0];
  }

  // Slot i's binding (runtime map entry, or that slot's default when the
  // entry is missing / invalid), or null.
  Player.prototype.actionSlot = function (i) {
    var m = this.actionMapSource ? this.actionMapSource() : null;
    var e = m && m[i];
    if (validActionEntry(e)) return e;
    var d = (this.actionDefaults || V7.actionbar.defaults)[i];
    return validActionEntry(d) ? d : null;
  };

  // Is slot i's spell castable right now (learned + an implement in hand)?
  // false for item slots. The HUD darkens spell slots that fail this.
  Player.prototype.actionSpellLive = function (i) {
    var e = this.actionSlot(i);
    return !!(e && e.kind === 'spell' && this.hasCaster() && this.belt.indexOf(e.id) >= 0);
  };

  // Digit key / bar tap. spell slot: no implement or not learned = refusal
  // flash (like an empty slot), else the Order C belt bind (shift = OFF
  // hand). item slot: shift = 'Not a spell' refusal; held in a hand = no-op;
  // else the Q-swap window into its native hand (selectItemEquip).
  Player.prototype.selectActionSlot = function (i, shift) {
    if (this.state !== 'alive') return;
    if (i < 0 || i >= V7.actionbar.slots) return;
    var e = this.actionSlot(i);
    if (!e) {
      if (this.onCastRefusal) this.onCastRefusal('empty-slot');
      return;
    }
    if (e.kind === 'spell') {
      var b = this.belt.indexOf(e.id);
      if (b < 0 || !this.hasCaster()) {
        if (this.onCastRefusal) this.onCastRefusal(b < 0 ? 'empty-slot' : 'no-implement');
        return;
      }
      // AB1.1 (Nicko 10-06 playtest): with ONE caster hand, a plain select
      // retunes it (offhand-only glove now works). With TWO caster hands
      // (dual gloves), plain = main, Shift = off (Order C per-hand rule
      // preserved, C5 regression avoided). A Shift when the LEFT hand is
      // non-caster is a no-op (nothing to retune there).
      var castRole = null;
      if (this.isCasterHand('left') && this.isCasterHand('right')) {
        castRole = shift ? 'off' : 'main';
      } else if (this.isCasterHand('left')) {
        castRole = 'off';
      } else {
        castRole = 'main';
      }
      this.pressBeltKey(b, castRole);
      return;
    }
    if (shift) { this.refuseEquip('Not a spell'); return; }
    if (this.handOf(e.id)) return;           // already active
    this.selectItemEquip(e.id, actionHandOf(e.id));
  };

  Player.prototype.getActiveLoadout = function () {
    return this.activeLoadout;
  };

  // ---- Order C: per-hand cast state + bindings --------------------------------
  // role 'main' = right hand, 'off' = left hand.
  var ROLE_HAND = { main: 'right', off: 'left' };
  var HAND_ROLE = { right: 'main', left: 'off' };
  var ROLES = ['main', 'off'];

  function newCastState() {
    // windup: seconds left (> 0 = mid-cast), spellId: the spell being cast,
    // cooldown: seconds until this hand may cast again, regrip: this hand's
    // re-grip busy window (new binding / implement just entered the hand)
    return { windup: 0, spellId: null, cooldown: 0, regrip: 0 };
  }

  function roleOf(handOrRole) {
    return HAND_ROLE[handOrRole] || (ROLE_HAND[handOrRole] ? handOrRole : 'main');
  }

  // v7: belt spell selection, Order C: binds belt slot i to one hand ('main'
  // default = Digit1-5, 'off' = Shift+Digit1-5). Magic canon 10-05: spells
  // are knowledge, the belt is 5 quick slots over them; a binding is a
  // pointer into the belt. Starts THAT hand's regrip only while it holds a
  // caster. NEVER touches the combo chain, armed state, or the hands.
  Player.prototype.selectBeltSlot = function (i, role) {
    role = roleOf(role);
    if (this.state !== 'alive') return;
    if (i < 0 || i >= V7.belt.slots) return;
    if (!this.belt[i]) {
      // empty slot refused: HUD flash via callback
      if (this.onCastRefusal) this.onCastRefusal('empty-slot');
      return;
    }
    this.bindings[role] = i;
    if (this.isCasterHand(ROLE_HAND[role])) this.cast[role].regrip = V7.belt.regripSeconds;
    if (this.onSpellSelected) this.onSpellSelected(this.belt[i], role);
  };

  // Digit key (Order B/C): bind that slot's learned spell to the hand.
  // Empty slot = refusal flash; the hand's current slot = no-op. A cast
  // still winding up in THAT hand belongs to the old spell and is dropped.
  Player.prototype.pressBeltKey = function (i, role) {
    role = roleOf(role);
    if (this.state !== 'alive') return;
    if (i < 0 || i >= V7.belt.slots) return;
    if (this.belt[i] && i === this.bindings[role]) return;
    if (this.belt[i]) this.dropPendingCast(role);
    this.selectBeltSlot(i, role);
  };

  // Learned spells (CHARACTER tab list): the belt's filled slots for now.
  // Books / scrolls (learn-on-read) will add to the belt later. main / off
  // = which hand binding points at the slot.
  Player.prototype.getKnownSpells = function () {
    var out = [];
    for (var i = 0; i < this.belt.length; i++) {
      if (this.belt[i]) {
        out.push({ slot: i, id: this.belt[i],
                   main: i === this.bindings.main, off: i === this.bindings.off });
      }
    }
    return out;
  };

  // Spell bound to a hand ('main' / 'off' or 'right' / 'left'), or null.
  Player.prototype.getBoundSpellId = function (role) {
    return this.belt[this.bindings[roleOf(role)]] || null;
  };

  // A cast still in windup belongs to the implement / binding being put
  // away: drop it (no focus spent; deliberate, so no fizzle flash). No role
  // = both hands.
  Player.prototype.dropPendingCast = function (role) {
    var roles = role ? [roleOf(role)] : ROLES;
    for (var r = 0; r < roles.length; r++) {
      var c = this.cast[roles[r]];
      c.windup = 0;
      c.spellId = null;
    }
  };

  // Focus already promised to OTHER hands mid-windup (spent on completion).
  // A new cast must fit beside it, so a focus-starved hand refuses at the
  // press instead of both windups completing on one cast's worth of focus.
  Player.prototype.focusReserved = function (exceptRole) {
    var sum = 0;
    for (var r = 0; r < ROLES.length; r++) {
      var c = this.cast[ROLES[r]];
      if (ROLES[r] !== exceptRole && c.windup > 0 && c.spellId) sum += castCost(c.spellId);
    }
    return sum;
  };

  // L1: x the spell's school-line focus cost passive (x1 at rank 1 / no line)
  function castCost(spellId) {
    var LV = window.WH_LEVEL, line = LV ? LV.spellLine(spellId) : null;
    return V7.spell[spellId].focusCost * CFG.castFocusTaxMult *
      (line ? LV.skillMult(line, 'focusCost') : 1);
  }

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

  // Order C: does this hand ('right' / 'left') hold a casting implement?
  Player.prototype.isCasterHand = function (hand) {
    return kindOf(this.hands[hand]) === 'caster';
  };

  Player.prototype.hasShield = function () {
    return kindOf(this.hands.left) === 'shield' || kindOf(this.hands.right) === 'shield';
  };

  Player.prototype.hasMeleeRight = function () {
    return kindOf(this.hands.right) === 'melee';
  };

  // R-64.3: the item defs in the hands (right, left; empty hands skipped).
  // Both hands count, so dual gloves are two pieces. WH_LEVEL.magicDefense
  // totals item stats over this.
  Player.prototype.equippedItems = function () {
    var out = [];
    ['right', 'left'].forEach(function (h) {
      var d = itemDef(this.hands[h]);
      if (d) out.push(d);
    }, this);
    return out;
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

  // Order C: a shield blocks only from the LEFT hand (right = carried).
  Player.prototype.hasShieldLeft = function () {
    return kindOf(this.hands.left) === 'shield';
  };

  // Order C two-button combat. What a hand's button does, from what the
  // hand holds: right melee -> the attack chain, caster -> cast that hand's
  // binding, left shield -> hold-to-block, anything else -> null (inert).
  Player.prototype.handAction = function (hand) {
    var k = kindOf(this.hands[hand]);
    if (k === 'melee' && hand === 'right') return 'attack';
    if (k === 'caster') return 'cast';
    if (k === 'shield' && hand === 'left') return 'block';
    return null;
  };

  // CONFIG.equip.twoHand maps a button ('lmb' / 'rmb') to 'mainHand' (right)
  // or 'offHand' (left).
  Player.prototype.buttonHand = function (button) {
    return window.WH_CONFIG.equip.twoHand[button] === 'offHand' ? 'left' : 'right';
  };

  // THE dispatch for both combat buttons; mouse (LMB/RMB) and touch
  // (attack/block buttons) both call it. down = press, else release. A
  // release only ends a block that this button started.
  Player.prototype.handButton = function (button, down) {
    var hand = this.buttonHand(button);
    if (!down) {
      if (this.blockButton === button) {
        this.blockButton = null;
        this.endBlock();
      }
      return;
    }
    var a = this.handAction(hand);
    if (a === 'attack') this.tryAttack();
    else if (a === 'cast') this.tryCast(hand);
    else if (a === 'block') {
      this.tryBlock();
      if (this.blocking) this.blockButton = button;
    }
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
  // the item ends up in that hand. D-amend: a melee/shield item with no mesh
  // (dormant buckler / towerShield) is refused unless force (WH_DEBUG only).
  Player.prototype.equipItem = function (id, hand, inventoryOnly, force) {
    var d = itemDef(id);
    if (!d || d.category !== 'gear' || !d.hands) return this.refuseEquip(itemName(id) + ' cannot be equipped');
    if (!d.mesh && (d.kind === 'shield' || d.kind === 'melee') && !force) return this.refuseEquip('No visual - asset pending');
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

  // Boot: move CONFIG.equip.defaultHands items out of the starting kit
  // (R-64.4: or the picked class's hands). inventoryOnly: the same id in
  // both hands (Magician dual gloves) draws two pieces, never a move.
  Player.prototype.equipDefaultHands = function (hands) {
    var dh = hands || window.WH_CONFIG.equip.defaultHands;
    if (dh.right) this.equipItem(dh.right, 'right', true);
    if (dh.left) this.equipItem(dh.left, 'left', true);
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
    if (!this.hasShieldLeft()) this.endBlock();     // Order C: guard = left-hand shield
    // Order C, per hand: an implement leaving drops that hand's windup; an
    // implement entering (new item in the hand) starts that hand's regrip
    if (!this.lastHandItems) this.lastHandItems = { right: null, left: null };
    for (var r = 0; r < ROLES.length; r++) {
      var h = ROLE_HAND[ROLES[r]];
      if (!this.isCasterHand(h)) this.dropPendingCast(ROLES[r]);
      else if (this.hands[h] !== this.lastHandItems[h]) this.cast[ROLES[r]].regrip = V7.belt.regripSeconds;
      this.lastHandItems[h] = this.hands[h];
    }
    var pair = window.WH_CONFIG.equip.qSwap;
    this.activeLoadout = this.hands.left === pair[0] ? 1 : this.hands.left === pair[1] ? 2 : 0;
    this.applyHandVisuals();
    if (this.onHandsChanged) this.onHandsChanged(this.hands);
  };

  // Register an item's hand mesh (game.js instances the GLB). One-time prep
  // here; applyHandVisuals mounts it on whichever hand holds the item.
  // Stage 2: kind 'torch' takes a second instance (twin) - one mesh per hand,
  // so torch + torch shows two torches.
  Player.prototype.setItemMesh = function (id, mesh, twin) {
    if (kindOf(id) === 'torch') {
      var prev = this.handMeshes[id];
      if (prev) {
        if (prev.left && prev.left.parent) prev.left.parent.remove(prev.left);
        if (prev.right && prev.right.parent) prev.right.parent.remove(prev.right);
      }
      this.handMeshes[id] = { left: prepTorch(mesh), right: twin ? prepTorch(twin) : null };
      this.applyHandVisuals();
      return;
    }
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

  // Torch prep (once per mesh, before any mount): slide the inner mesh so
  // the measured grip sits on the holder origin, and hang the hand-light
  // anchor at the flame (CONFIG.assets.torchMount, raw GLB units).
  function prepTorch(mesh) {
    if (!mesh || mesh.userData.whTorchPrepped) return mesh;
    mesh.userData.whTorchPrepped = true;
    var TM = window.WH_CONFIG.assets.torchMount;
    if (mesh.children[0]) mesh.children[0].position.y -= TM.gripHolderY;
    var anchor = new THREE.Object3D();
    anchor.position.y = TM.lightHolderY - TM.gripHolderY;
    mesh.add(anchor);
    mesh.userData.whLightAnchor = anchor;
    mesh.userData.whHand = null;
    mesh.visible = false;
    return mesh;
  }

  // Stage 2: the flame anchor of the torch mesh in this hand (light.js hangs
  // the hand's follow light there), or null when the hand holds no mounted
  // per-hand mesh.
  Player.prototype.handLightAnchor = function (hand) {
    var set = this.handMeshes[this.hands[hand]];
    var m = set ? set[hand] : null;
    return m && m.parent && m.visible ? m.userData.whLightAnchor || null : null;
  };

  // S3 tweak (10-06): raised-arm torch carry. Runs AFTER the mixer each frame
  // (game.js calls it right after syncPlayer): the mixer overwrites every arm
  // bone's quaternion each frame its clip keys that bone (all 13 clips key the
  // arms), so reading quat fresh and writing q_clip * q_carry is a clean
  // per-frame overlay - nothing accumulates, no un-apply. No latched flags
  // (D9): torchCarryW {right,left} is the only state, eased toward
  // torch-in-hand-and-alive ? 1 : 0 over carry.easeSec (both directions).
  // Axis = bone-local +X (measured on combat-chain.glb: limbs run bone-local
  // +Y; both arms' local X ~ world -X, so +X lifts forward+out; right hand
  // mirrors with the SAME sign - computed 19.4deg like left's 20.0deg).
  // Composition order = q_clip * q_carry (carry applied in the bone's
  // post-clip frame) - matches the measured chain m_local * R(lift).
  Player.prototype.applyTorchCarryPost = function (dt) {
    var cfg = window.WH_CONFIG.assets.torchMount.carry;
    if (!cfg || !this.body || !this.anim) return;
    if (!this.torchCarryW) this.torchCarryW = { right: 0, left: 0 };
    for (var hi = 0; hi < 2; hi++) {
      var hand = hi === 0 ? 'right' : 'left';
      var target = this.handOf('torch') === hand && this.state === 'alive' ? 1 : 0;
      var w = this.torchCarryW[hand];
      var step = dt / (cfg.easeSec || 0.25);
      if (w < target) w = Math.min(target, w + step);
      else if (w > target) w = Math.max(target, w - step);
      this.torchCarryW[hand] = w;
      if (w <= 0) continue;
      var ua = boneFor(this.body, hand);
      if (ua) {
        TORCH_Q_SCRATCH.setFromAxisAngle(AX_X, (cfg.liftDeg || 0) * Math.PI / 180 * w);
        ua.quaternion.multiply(TORCH_Q_SCRATCH);
      }
      var fb = this.body.getObjectByName(hand === 'left' ? 'L_Forearm' : 'R_Forearm');
      if (fb && cfg.bendDeg) {
        TORCH_Q_SCRATCH.setFromAxisAngle(AX_X, (cfg.bendDeg || 0) * Math.PI / 180 * w);
        fb.quaternion.multiply(TORCH_Q_SCRATCH);
      }
    }
  };

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
    // stage 2 per-hand meshes: the right/left instance shows iff that hand
    // holds the item (both may - torch + torch)
    for (var pid in this.handMeshes) {
      for (var hi = 0; hi < 2; hi++) {
        var h = hi === 0 ? 'right' : 'left';
        var m = this.handMeshes[pid][h];
        if (!m) continue;
        if (this.hands[h] !== pid) {
          if (m.parent) m.parent.remove(m);
          m.visible = false;
          m.userData.whHand = null;
          continue;
        }
        m.visible = true;
        if (m.userData.whHand === h && m.parent) continue;
        m.userData.whHand = h;
        this.mountTorch(m, h, pid);
      }
    }
  };

  // Stage 2 S3: torch on a skinned hand - raw +Y (butt -> flame) onto the
  // hand-local headAxis at the fist centroid (CONFIG.assets.torchMount,
  // measured for nativeHand.torch, mirrored for the other hand). The rigid
  // stand-in body has no bones: idle anchor on yawFrame, mirrored per hand.
  // S3 tweak (10-06): with the raised-arm carry (applyTorchCarryPost), a
  // straightenAxis turns the shaft to TRUE vertical: qt = setFromUnitVectors
  // (meshY -> straightenAxis) is multiplied UNDER the head-axis q, so
  // meshY -qt-> mesh target -q-> hand target t_hand -rig-> world +Y.
  // Mirrored with the mount for the off hand (verified: L exact vertical,
  // R 0.7deg off - rig asymmetry). No per-frame mesh writes; the eased bone
  // lift animates the whole mount.
  Player.prototype.mountTorch = function (mesh, hand, itemId) {
    if (mesh.parent) mesh.parent.remove(mesh);
    var TM = window.WH_CONFIG.assets.torchMount;
    var bone = boneFor(this.body, hand);
    if (bone) {
      bone.add(mesh);
      var q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0),
        new THREE.Vector3().fromArray(TM.headAxis).normalize());
      if (TM.rollDeg) {
        q.premultiply(new THREE.Quaternion().setFromAxisAngle(
          new THREE.Vector3().fromArray(TM.headAxis).normalize(), TM.rollDeg * Math.PI / 180));
      }
      if (TM.carry && TM.carry.straightenAxis) {
        // mesh-space correction: shaft axis (0,1,0) -> straightenAxis, then
        // q carries it into hand space; q*qt maps meshY all the way to t_hand
        var qt = new THREE.Quaternion().setFromUnitVectors(
          new THREE.Vector3(0, 1, 0),
          new THREE.Vector3().fromArray(TM.carry.straightenAxis).normalize());
        q.multiply(qt);
      }
      var off = new THREE.Vector3().fromArray(TM.offset);
      if (isMirrored(itemId, hand)) {
        mirrorQuat(q);
        mirrorVec(off);
      }
      mesh.quaternion.copy(q);
      mesh.position.copy(off);
    } else {
      var ip = window.WH_CONFIG.moveset.idlePose;
      this.yawFrame.add(mesh);
      mesh.position.set((hand === 'left' ? -1 : 1) * ip.pos[0], ip.pos[1], ip.pos[2]);
      mesh.rotation.set(0, 0, 0);
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

  // v7: cast refusal conditions (AC: roll/attacking-strike/toggle/regrip/
  // guard break/dead/focus). Windup-stage attacks ALLOW the weave cast.
  // Order C: per hand (role 'main' / 'off' or hand 'right' / 'left') - the
  // hand needs its own implement, its own windup/cooldown/regrip clear, and
  // the shared focus pool minus what the other hand has already promised.
  Player.prototype.canCast = function (role) {
    role = roleOf(role);
    var c = this.cast[role];
    if (this.state !== 'alive') return false;
    if (this.rolling || this.toggling || c.regrip > 0) return false;
    if (this.guardBroken) return false;
    if (!this.isCasterHand(ROLE_HAND[role])) return false;   // implement in THIS hand
    if (this.attacking && this.getAttackStage() !== 'windup') return false;
    if (c.cooldown > 0 || c.windup > 0) return false;
    var spellId = this.getBoundSpellId(role);
    if (!spellId) return false;
    return this.focus - this.focusReserved(role) >= castCost(spellId);
  };

  // v7: cast entry. Refusal = HUD flash. Order C: starts THIS hand's windup
  // with its binding; the other hand is untouched.
  // CASTING NEVER RESETS THE CHAIN: comboIndex/comboQueued untouched.
  Player.prototype.tryCast = function (role) {
    role = roleOf(role);
    if (!this.canCast(role)) {
      if (this.onCastRefusal) this.onCastRefusal('cast-refused', role);
      return false;
    }
    var spellId = this.getBoundSpellId(role);
    var c = this.cast[role];
    c.windup = V7.spell[spellId].castWindup;   // fizzle check runs during windup
    c.spellId = spellId;
    return true;
  };

  // Order C: tick both hands' windups (game.js loop, which owns the spawned
  // spells). Returns the completed cast requests (0, 1 or 2 this frame).
  Player.prototype.tickCasts = function (dt) {
    var out = [];
    if (this.state !== 'alive') return out;
    for (var r = 0; r < ROLES.length; r++) {
      var c = this.cast[ROLES[r]];
      if (c.windup <= 0) continue;
      c.windup -= dt;
      if (c.windup > 0) continue;
      c.windup = 0;
      var req = this.completeCast(ROLES[r]);
      if (req) out.push(req);
    }
    return out;
  };

  // v7: windup completion -> spend focus WITH the one-hand tax (weapon in
  // main hand = tax always in this slice), start THIS hand's cooldown.
  // Returns the spawn request { spellId, role, hand, origin, dirX, dirZ }
  // or null; game.js spawns from that hand's glow anchor.
  Player.prototype.completeCast = function (role) {
    role = roleOf(role);
    var c = this.cast[role];
    var spellId = c.spellId;
    c.spellId = null;
    if (!spellId) return null;
    var S = V7.spell[spellId];
    this.spendFocus(castCost(spellId));
    c.cooldown = S.castCooldown;
    // aim at the lock target, else straight ahead of facing
    var dx = Math.sin(this.yaw), dz = Math.cos(this.yaw);
    if (this.lockTarget) {
      var tdx = this.lockTarget.pos.x - this.pos.x;
      var tdz = this.lockTarget.pos.z - this.pos.z;
      var d = Math.sqrt(tdx * tdx + tdz * tdz);
      if (d > 0.001) { dx = tdx / d; dz = tdz / d; }
    }
    return { spellId: spellId, role: role, hand: ROLE_HAND[role],
             origin: this.pos, dirX: dx, dirZ: dz };
  };

  // Order C: windup progress 0..1 for a hand (glow pulse), 0 when idle.
  Player.prototype.castProgress = function (role) {
    var c = this.cast[roleOf(role)];
    if (c.windup <= 0 || !c.spellId) return 0;
    var w = V7.spell[c.spellId].castWindup;
    return w > 0 ? 1 - c.windup / w : 1;
  };

  // v7: damage during a windup fizzles the cast: NO focus spent, no
  // projectile. HUD fizzle flash via callback. Order C: fizzles every hand
  // mid-windup (one flash).
  Player.prototype.cancelCastFizzle = function () {
    var any = false;
    for (var r = 0; r < ROLES.length; r++) {
      if (this.cast[ROLES[r]].windup > 0) any = true;
    }
    if (!any) return false;
    this.dropPendingCast();
    if (this.onFizzle) this.onFizzle();
    return true;
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
  // EPR1-A5: 2 and 3 read blockActive (guard raised guardRaiseSec after the
  // RMB accept), not blocking.
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
    if (this.blockActive && this.parryTimer > 0 && attacker &&
        attacker.enterStagger && attackerInArc) {
      this.spendStamina(BLK.parryStaminaCost);
      attacker.enterStagger(BLK.riposteStaggerDur);
      attacker.riposteArmed = true;          // next player hit does bonus damage
      if (this.anim) this.anim.shieldParry();  // Order D: deflect swipe (presentation)
      this.endBlock();
      if (this.onParry) this.onParry(attacker);
      return false;                          // zero damage
    }

    // 3. block: only if attacker is within the block arc of player facing
    if (this.blockActive && attacker && attacker.pos && attackerInArc) {
      // L1 Shield / Defense rank: block stamina drain reduction (x1 at rank 1)
      var drainMult = window.WH_LEVEL ? window.WH_LEVEL.skillMult('shieldDefense', 'blockDrain') : 1;
      var staminaCost = Math.max(1, Math.round(damage * BLK.staminaCostMult * drainMult));
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
      } else {
        // Order D: shield recoil replaces the chip's generic hit reaction
        if (this.anim && !dead) this.anim.shieldImpact();
        if (this.onBlock) this.onBlock(attacker, chip);
      }
      // L1: was `return applied` (undeclared since a merge - a ReferenceError
      // thrown out of every blocked hit); dead holds takeDamage's applied flag
      return dead;
    }

    // 4. full damage (existing path)
    return this.takeDamage(damage);
  };

  // 10-04 chain gating (Nicko: combo spam -> real chains). Strike/recover
  // presses are BUFFERED for inputBufferSec and fired by update() once the
  // swing reaches its chain window. EPR1 (B5): windup presses are IGNORED
  // before move.bufferFrom x windup and BUFFERED from it (their lifetime
  // starts at the strike); a buffered LMB replaces a queued dodge. A press
  // while idle always starts the chain at chain[0].
  Player.prototype.tryAttack = function () {
    if (this.state !== 'alive' || this.rolling || this.toggling) return;
    if (!this.hasMeleeRight()) return;     // Order B: chain needs melee in the RIGHT hand
    if (this.blocking) return;              // v6: must release RMB to attack
    if (this.attacking) {
      var stage = this.getAttackStage();
      var M = this.attackMove;
      if (stage === 'strike' || stage === 'recover' ||
          (typeof M.bufferFrom === 'number' &&
           this.attackTotal - this.attackTimer + GATE_EPS >= M.bufferFrom * M.windup)) {
        this.comboQueued = true;
        this.comboBufferTimer = MV.inputBufferSec;
        this.dodgeQueued = false;
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
    // L1 Long Blade rank: attack stamina cost reduction (x1 at rank 1).
    // DAG: the wielded weapon's line (WH_LEVEL.weaponLine) - longsword /
    // handAxe = longBlade as before; dagger = shortBlade (no staminaCost
    // passive v1 -> x1, the Long Blade discount does not carry over).
    var cost = M.staminaCost * (window.WH_LEVEL ?
      window.WH_LEVEL.skillMult(window.WH_LEVEL.weaponLine(this.weaponId), 'staminaCost') : 1);
    if (this.stamina < cost) return false;
    this.spendStamina(cost);
    this.attacking = true;
    this.attackMoveId = this.getWeaponDef().chain[idx];
    this.attackMove = M;
    this.attackTotal = M.windup + M.strike + M.recover;
    this.attackTimer = this.attackTotal;
    this.attackSerial++;
    this.attackDidHit = false;
    this.lungeLeft = M.lunge;
    this.rootMotionApplied = 0;             // EPR1: each swing runs its own rootMotion table
    this.rootMotionStage = null;
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
    this.dodgeQueued = false;                // EPR1
    this.chainHits = 0;
    this.recoverFullyElapsed = true;
    this.resetWeaponPose();
  };

  // A swing that ends without chaining (full recover, windup roll-cancel,
  // respawn) closes the chain: the next press is a fresh m1 with no carried
  // chain hits, so comboIndex stays inside 0..cap-1. EPR1: restored - the
  // 33d0d80 definition was lost on origin/dev while toggleLoadout() and
  // respawnAt() still call it (KeyQ threw "endCombo is not a function").
  Player.prototype.endCombo = function () {
    this.recoverFullyElapsed = true;
    this.comboIndex = 0;
    this.chainHits = 0;
    this.comboQueued = false;
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

  // EPR1 cancel matrix: elapsed (s) from which input type col ('dodge' |
  // 'guard' | 'move') may interrupt the current swing = CONFIG
  // move.cancel[col] x (windup + strike + recover). Without the column the
  // pre-EPR1 law holds: dodge from recover start, guard / move never. The
  // light column stays chainOpenSec (update()).
  Player.prototype.getCancelPoint = function (col) {
    var M = this.attackMove;
    if (!M) return 0;
    if (M.cancel && typeof M.cancel[col] === 'number') return M.cancel[col] * this.attackTotal;
    return col === 'dodge' ? M.windup + M.strike : Infinity;
  };

  // True once the current swing has reached its cancel point for col (a
  // point reached exactly, up to float noise, counts as reached).
  Player.prototype.cancelOpen = function (col) {
    if (!this.attacking) return false;
    return this.attackTotal - this.attackTimer + GATE_EPS >= this.getCancelPoint(col);
  };

  Player.prototype.spendStamina = function (amount) {
    this.stamina = Math.max(0, this.stamina - amount);
    this.staminaRegenBlock = CFG.staminaRegenDelay;
  };

  Player.prototype.takeDamage = function (amount) {
    if (this.iframes > 0 || this.state !== 'alive') return false;
    // L1 Ward: damage reduction after the enemy / chip numbers (0 with no
    // points; CONFIG.leveling.statCurves.ward cap 60%)
    if (window.WH_LEVEL) amount *= 1 - window.WH_LEVEL.statTotal('ward');
    this.hp = Math.max(0, this.hp - amount);
    if (this.anim) this.anim.hit();
    // v7: hp loss during a cast windup fizzles the cast (no focus spent)
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
      moveId: this.attackMoveId,
      weaponId: this.weaponId       // DAG: the skill line a landed hit trains
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

  // EPR1 (spec 3.3, C1-C3): attack root motion along facing from the move's
  // FRAME TABLE (CONFIG move.rootMotion[stage] = cumulative forward metres
  // [start, end], times move.lunge). Frame-anchored: a stage's first sim
  // frame sits at its start value and its last at its end value, linear in
  // frame index between, so the stage-change frame adds nothing (20 Hz
  // slashR2L strike = 4 frames: 0 / 0.3 / 0.6 / 0.9 m). The last-frame time
  // is predicted from the current dt; a shortfall lands on the next stage's
  // first frame. Moves without a table keep the legacy strike lunge
  // (move.lunge metres drained over the strike, unchanged).
  Player.prototype.applyRootMotion = function (dt) {
    var M = this.attackMove;
    var ph = this.getAttackPhase();
    if (!M.rootMotion) {
      if (ph.stage !== 'strike' || this.lungeLeft <= 0) return;
      var lungeVel = M.lunge / M.strike;
      var lungeStep = Math.min(lungeVel * dt, this.lungeLeft);
      this.pos.x += Math.sin(this.yaw) * lungeStep;
      this.pos.z += Math.cos(this.yaw) * lungeStep;
      this.lungeLeft -= lungeStep;
      return;
    }
    var seg = M.rootMotion[ph.stage];
    if (!seg) return;
    if (this.rootMotionStage !== ph.stage) {
      this.rootMotionStage = ph.stage;
      this.rootMotionT0 = ph.t;
      this.rootMotionSpan = Math.max(0, Math.floor((ph.dur - ph.t - GATE_EPS) / dt)) * dt;
    }
    var p = this.rootMotionSpan > 0 ?
      Math.min(1, Math.max(0, (ph.t - this.rootMotionT0) / this.rootMotionSpan)) : 1;
    var scale = typeof M.lunge === 'number' ? M.lunge : 1;
    var step = (seg[0] + (seg[1] - seg[0]) * p) * scale - this.rootMotionApplied;
    if (step <= 0) return;
    this.pos.x += Math.sin(this.yaw) * step;
    this.pos.z += Math.cos(this.yaw) * step;
    this.rootMotionApplied += step;
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
    // EPR1 (B3, EPR1-A5): the accepted block turns ACTIVE for the hit checks
    // guardRaiseSec later (3 frames at the 20 Hz clamp).
    if (this.blocking) {
      if (this.guardRaiseTimer > 0) this.guardRaiseTimer = Math.max(0, this.guardRaiseTimer - dt);
      this.blockActive = this.guardRaiseTimer <= 0;
    }
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
      // R-64.1/64.2: 2.0 base * (1 + 0.05 * wisdomPoints) * other mults
      // (blocking 0.5): 0 wis = 2.0/s, 10 wis = 3.0/s, 10 wis blocking = 1.5/s
      var focusMult = window.WH_LEVEL && window.WH_LEVEL.magicRegenMult ?
        window.WH_LEVEL.magicRegenMult() : 1;
      var focusBlockMult = this.blocking ? window.WH_CONFIG.block.blockingRegenMult : 1;
      this.focus = Math.min(this.focusMax,
        this.focus + CFG.focusRegenPerSec * focusMult * focusBlockMult * dt);
    }

    // ---- v7: weave timers ----
    if (this.toggling) {
      this.toggleTimer -= dt;
      if (this.toggleTimer <= 0) {
        this.toggling = false;
        // Order B: the Q swap lands on completion. Inventory-only source,
        // re-checked here (the screen may have moved it meanwhile).
        // AB1: bar item slots land in their own hand (pendingQSwapHand).
        var qItem = this.pendingQSwap;
        this.pendingQSwap = null;
        if (qItem) this.equipItem(qItem, this.pendingQSwapHand || 'left', true);
      }
    }
    // Order C: per-hand regrip + cooldown (windups tick in tickCasts)
    for (var cr = 0; cr < ROLES.length; cr++) {
      var cs = this.cast[ROLES[cr]];
      if (cs.regrip > 0) cs.regrip = Math.max(0, cs.regrip - dt);
      if (cs.cooldown > 0) cs.cooldown = Math.max(0, cs.cooldown - dt);
    }
    // armed finisher window decays; expiry clears armed AND crossArmed
    if (this.armedTimer > 0) {
      this.armedTimer = Math.max(0, this.armedTimer - dt);
      if (this.armedTimer <= 0) this.crossArmed = false;
    }
    // Order C: a guard needs a shield in the LEFT hand
    if (this.blocking && !this.hasShieldLeft()) this.endBlock();

    // EPR1: keyboard Space grammar (dodge on release / sprint while held)
    this.sampleDodgeInput(dt);

    if (this.state === 'dying') {
      this.deathTilt = Math.min(Math.PI / 2, this.deathTilt + dt * 3);
      if (this.body && !this.anim) this.body.rotation.x = -this.deathTilt;
      if (this.anim) this.anim.death();
      if (this.stateTime >= CFG.respawnDelay) this.state = 'dead';
      return;
    }

    if (this.attacking) {
      this.attackTimer -= dt;
      // 10-04: buffered input expires after inputBufferSec. EPR1 (B5): a
      // press buffered in windup (from bufferFrom) starts its lifetime at
      // the strike, so it survives to the chain window.
      if (this.comboQueued && this.getAttackStage() !== 'windup') {
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
      // EPR1 cancel matrix: a queued dodge rolls out at the move's dodge
      // point; a held RMB raises the guard at its guard point while the
      // swing plays out (hits wait for blockActive).
      if (this.dodgeQueued && this.cancelOpen('dodge')) this.consumeQueuedDodge();
      if (this.guardQueued && this.cancelOpen('guard')) this.tryBlock();
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
    // EPR1: inputs still queued once the swing is over (fully recovered or
    // cancelled) act now.
    if (!this.attacking) {
      if (this.dodgeQueued) this.consumeQueuedDodge();
      if (this.guardQueued) this.tryBlock();
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
    } else if (this.backstep) {
      // EPR1 (A2): backwards hop along facing - the group slides, the body
      // keeps its pose (no clip change).
      this.backstepTimer -= dt;
      var bsStep = CFG.walkSpeed * ER.backstep.speedMult * dt;
      this.pos.x -= Math.sin(this.yaw) * bsStep;
      this.pos.z -= Math.cos(this.yaw) * bsStep;
      if (this.backstepTimer <= 0) this.backstep = false;
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
        // L1 Speed: walk / sprint pace only (1 with no points); roll and
        // backstep keep their EPR1 curves
        if (window.WH_LEVEL) speed *= window.WH_LEVEL.statTotal('speed');
        if (sprintingNow) {
          this.spendStamina(CFG.sprintStaminaPerSec * dt);
        }
        if (this.attacking) speed *= this.getWeaponDef().moveMultWhileAttacking[this.getAttackStage()] || 0;
        if (this.blocking) {
          // D-amend: shield weight class (left hand = the blocking shield)
          var sb = (itemDef(this.hands.left) || {}).block;
          speed *= sb && sb.moveMult != null ? sb.moveMult : window.WH_CONFIG.block.moveMult;
        }
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

    // Attack root motion along facing (FSM-owned for both the clip and
    // stand-in paths): EPR1 rootMotion table, or the legacy strike lunge
    // without one (applyRootMotion). Runs before the bounds clamp (C3).
    if (this.attacking) this.applyRootMotion(dt);

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
    // Order E1 (Nicko 10-05): lock-on changes ONLY the camera yaw - it aims
    // so the target sits straight ahead of the player. Anchor, distance and
    // pitch stay exactly the unlocked orbit below (no midpoint re-anchor, no
    // extra zoom), so the player stays framed like unlocked play.
    if (this.lockTarget && this.state === 'alive') {
      var t = this.lockTarget;
      var dx = t.pos.x - this.pos.x;
      var dz = t.pos.z - this.pos.z;
      // camera sits opposite the target relative to the player
      if (dx * dx + dz * dz > 0.000001) {
        var lockLerp = 1 - Math.exp(-LOCK.camLerp * dt);
        this.camYaw += shortestAngle(Math.atan2(dx, dz) + Math.PI - this.camYaw) * lockLerp;
      }
    }
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

    // 10-04 change order (Nicko): FULL camera decoupling - movement NEVER
    // turns the camera. camYaw changes only from mouse drag / camera
    // joystick (both stamp lastManualCamT) and the lock-on yaw aim above.
    // The old v3.1 movement auto-follow is gone. Position follow is the same
    // locked or not (the lock yaw swing is already smoothed by LOCK.camLerp).
    var lerp2 = 1 - Math.exp(-CFG.camFollowLerp * dt);
    this.camera.position.lerp(want, lerp2);
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
    this.backstep = false;                  // EPR1
    this.backstepTimer = 0;
    this.dodgeQueued = false;
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
    this.pendingQSwap = null;              // Order B: hands themselves persist through death
    this.pendingQSwapHand = 'left';
    this.cast = { main: newCastState(), off: newCastState() };   // Order C: both hands
    this.armedTimer = 0;
    this.crossArmed = false;
    this.atkYawOffset = 0;
    this.faceTowards(0, 0);                // respawn faces map center (Nicko 10-03)
    this.yawFrame.rotation.y = this.yaw;
    if (this.anim) this.anim.revive();
    if (this.body && !this.anim) { this.body.rotation.x = 0; this.body.rotation.y = this.atkYawOffset; }
  };

  // AB1: action bar validation, shared with the HUD map loader / picker
  Player.validActionEntry = validActionEntry;
  Player.isBindableItem = isBindableItem;
  Player.isSpellId = isSpellId;

  window.WH_Player = Player;
})();
