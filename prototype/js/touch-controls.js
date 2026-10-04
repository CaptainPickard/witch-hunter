// Witch Hunter - touch controls layer (2026-10-03, Nicko change order).
// PARALLEL input layer: never removes or shadows mouse/keyboard handlers.
// Self-contained IIFE exposing window.WH_TouchControls (init/show/hide/
// setEditMode), loaded in index.html BEFORE game.js. Pointer Events with
// pointerId tracking so stick + camera sweep + button taps coexist. Tunables
// live in window.WH_CONFIG.touch; placement persists in localStorage as
// viewport FRACTIONS (resize-safe). Darkwood faint outlines; amber (#d8b24a)
// accent on sprint-on/active states only.

(function () {
  'use strict';

  var TC = window.WH_CONFIG.touch;
  var LS_KEY = 'wh-touch-layout-v1';

  var inited = false;
  var visible = false;      // layer shown via toggle button
  var editMode = false;     // placement UI active (no game input injected)
  var unlocked = false;     // unlock icon state inside edit mode
  var scale = TC.scaleDefault || 1.0;
  var firstShow = true;     // first show auto-enters LAYOUT (edit) mode
  var hadSavedLayout = false; // a persisted layout already exists (skip auto-edit)

  var rootEl = null;        // #wh-touch-layer
  var toggleEl = null;      // #wh-touch-toggle (right edge, z 45)
  var editBarEl = null;     // edit toolbar (lock, +/- scale, reset, done)
  var lockChipEl = null;    // always-visible lock chip (re-enter edit mode)
  var controls = {};        // name -> { el, nub }
  var order = ['stick', 'cam', 'sprint', 'attack', 'lockon', 'dodge', 'block', 'interact'];
  var GAME_KEYS = {
    stick: ['KeyW', 'KeyA', 'KeyS', 'KeyD'],
    sprint: ['ShiftLeft']
  };
  var keysWritten = {};      // game-key booleans currently held BY this layer
  var pointers = {};         // pointerId -> { role, name }
  var lastCam = {};          // pointerId -> {x, y} camera drag previous pos
  var stickActiveId = null;
  var stickOrigin = { x: 0, y: 0 };
  var controls_nub_pending = null;
  var dragId = null, dragName = null, dragOffX = 0, dragOffY = 0;
  var savedState = null;

  function el(tag, cls, parent) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (parent) parent.appendChild(e);
    return e;
  }
  function clamp(v, lo, hi) { return v < lo ? lo : (v > hi ? hi : v); }
  function fracX(elm, name) {
    var sv = elm.style.left;
    var f = parseFloat(sv);
    if (isNaN(f)) f = (TC.layout[name] ? TC.layout[name].x * 100 : 50);
    else if (sv.indexOf('px') >= 0) f = f / window.innerWidth * 100;
    return clamp(f / 100, 0, 1);
  }
  function fracY(elm, name) {
    var sv = elm.style.top;
    var f = parseFloat(sv);
    if (isNaN(f)) f = (TC.layout[name] ? TC.layout[name].y * 100 : 50);
    else if (sv.indexOf('px') >= 0) f = f / window.innerHeight * 100;
    return clamp(f / 100, 0, 1);
  }

  function loadState() {
    try {
      var raw = localStorage.getItem(LS_KEY);
      if (!raw) return null;
      var obj = JSON.parse(raw);
      if (!obj || typeof obj !== 'object' || !obj.controls) return null;
      return obj;
    } catch (e) { return null; }
  }
  function saveState() {
    var out = { enabled: visible, scale: scale, controls: {} };
    order.forEach(function (name) {
      var c = controls[name];
      if (!c) return;
      out.controls[name] = { x: fracX(c.el, name), y: fracY(c.el, name) };
    });
    try { localStorage.setItem(LS_KEY, JSON.stringify(out)); } catch (e) {}
  }

  // ---- css -----------------------------------------------------------------
  var CSS = [
    '#wh-touch-toggle {',
    '  position: fixed; right: 8px; top: 50%; transform: translateY(-50%);',
    '  width: 40px; height: 40px; border-radius: 50%;',
    '  border: 2px solid #5a5344; background: rgba(20, 17, 14, 0.8);',
    '  color: #d8b24a; font: 700 20px/36px monospace; text-align: center;',
    '  z-index: 45; cursor: pointer; user-select: none;',
    '  -webkit-user-select: none; touch-action: none; pointer-events: auto;',
    '}',
    '#wh-touch-toggle:hover { border-color: #c9a94a; }',
    '#wh-touch-toggle.active { border-color: #d8b24a; color: #e3d27a;',
    '  box-shadow: 0 0 10px rgba(216, 178, 74, 0.4); }',

    '#wh-touch-lockchip {',
    '  position: fixed; right: 8px; top: calc(50% + 48px);',
    '  width: 40px; height: 40px; border-radius: 50%;',
    '  border: 2px solid #5a5344; background: rgba(20, 17, 14, 0.8);',
    '  color: #d8d2c0; font: 700 18px/36px monospace; text-align: center;',
    '  z-index: 45; cursor: pointer; user-select: none;',
    '  -webkit-user-select: none; touch-action: none; pointer-events: auto;',
    '}',
    '#wh-touch-lockchip:hover { border-color: #c9a94a; }',

    '#wh-touch-layer {',
    '  position: fixed; inset: 0; z-index: 40; pointer-events: none;',
    '  font-family: monospace;',
    '}',

    '.wh-touch-ctl {',
    '  position: fixed; display: flex; flex-direction: column;',
    '  align-items: center; justify-content: center;',
    '  border: 2px solid rgba(90, 83, 68, 0.9);',
    '  background: rgba(20, 17, 14, 0.35); border-radius: 50%;',
    '  color: #d8d2c0; font-family: monospace; text-align: center;',
    '  user-select: none; -webkit-user-select: none; touch-action: none;',
    '  pointer-events: auto; cursor: pointer;',
    '  opacity: ' + (TC.opacity || 0.35) + ';',
    '  transition: opacity 0.15s ease, border-color 0.1s ease;',
    '}',
    '.wh-touch-ctl.touched { opacity: 0.9; }',
    '.wh-touch-ctl.active { border-color: #d8b24a; color: #e3d27a;',
    '  box-shadow: 0 0 12px rgba(216, 178, 74, 0.35); }',
    '.wh-touch-ctl.active .glyph, .wh-touch-ctl.active .lbl { color: #e3d27a; }',
    '.wh-touch-ctl .glyph { font-size: 20px; line-height: 1; pointer-events: none; }',
    '.wh-touch-ctl .lbl { font-size: 9px; letter-spacing: 1px; margin-top: 3px;',
    '  pointer-events: none; text-transform: uppercase; }',

    '#wh-touch-layer.edit .wh-touch-ctl {',
    '  border-style: dashed; border-color: rgba(216, 178, 74, 0.9);',
    '  cursor: move;',
    '}',

    '.wh-touch-ctl.stick .nub { position: absolute; width: 34%; height: 34%;',
    '  border-radius: 50%; border: 2px solid #6a6350;',
    '  background: rgba(106, 99, 80, 0.25); pointer-events: none;',
    '  transform: translate(-50%, -50%); left: 50%; top: 50%; }',
    '.wh-touch-ctl.cam .crosshair { position: absolute; width: 10px; height: 10px;',
    '  border-left: 2px solid #6a6350; border-top: 2px solid #6a6350;',
    '  transform: rotate(45deg); pointer-events: none; }',

    '#wh-touch-editbar {',
    '  position: fixed; bottom: 12px; left: 50%; transform: translateX(-50%);',
    '  display: flex; gap: 8px; z-index: 46; pointer-events: auto;',
    '  user-select: none; -webkit-user-select: none;',
    '}',
    '#wh-touch-editbar button {',
    '  min-width: 40px; height: 36px; padding: 0 10px;',
    '  border: 2px solid #5a5344; border-radius: 18px;',
    '  background: rgba(20, 17, 14, 0.85); color: #d8d2c0;',
    '  font: 700 14px monospace; cursor: pointer; touch-action: none;',
    '}',
    '#wh-touch-editbar button:hover { border-color: #c9a94a; }',
    '#wh-touch-editbar button.amber { border-color: #d8b24a; color: #e3d27a; }'
  ].join('\n');

  function injectCss() {
    var t = document.createElement('style');
    t.id = 'wh-touch-style';
    t.textContent = CSS;
    document.head.appendChild(t);
  }

  // ---- control defs -----------------------------------------------------------
  var DEFS = {
    stick:  { label: 'Move' },
    cam:    { label: 'Camera' },
    sprint: { label: 'Sprint' },
    attack: { glyph: '\u2694', label: 'Attack' },
    lockon: { glyph: '\u2318', label: 'Lock-On' },
    dodge:  { glyph: '\u21C4', label: 'Dodge' },
    block:  { glyph: '\u25CE', label: 'Off Hand' },
    interact: { glyph: '\u25C8', label: 'Use' }
  };
  var LOCKED_GLYPH = '\uD83D\uDD12';      // closed lock
  var UNLOCKED_GLYPH = '\uD83D\uDD13';    // open lock


  function buildToggle() {
    if (toggleEl) return;
    injectCss();
    toggleEl = el('div');
    toggleEl.id = 'wh-touch-toggle';
    toggleEl.textContent = '\u25C7';
    toggleEl.title = 'Touch controls: show/hide';
    document.body.appendChild(toggleEl);
    // Nicko 10-03 bug fix: the old handler swallowed touchstart with
    // preventDefault, which kills the browser's synthetic click on touch
    // devices - the toggle rendered but never opened with thumbs (mouse
    // worked). Now: activate on pointerdown directly (touch AND mouse),
    // then swallow the synthetic click so it can never double-fire.
    toggleEl.addEventListener('pointerdown', function (ev) {
      ev.preventDefault();
      ev.stopPropagation();
      onToggleClick();
    });
    toggleEl.addEventListener('contextmenu', function (ev) {
      ev.preventDefault();
      ev.stopPropagation();
    });
    toggleEl.addEventListener('click', function (ev) {
      ev.preventDefault();
      ev.stopPropagation();
    });
  }

  function buildControls() {
    if (rootEl) return;
    rootEl = el('div');
    rootEl.id = 'wh-touch-layer';
    document.body.appendChild(rootEl);

    order.forEach(function (name) {
      var c = el('div', 'wh-touch-ctl ' + name);
      var d = DEFS[name];
      if (name === 'stick') {
        var nub = el('span', 'nub', c);
        controls_nub_pending = nub;   // wired after controls[name] exists
      }
      if (name === 'cam') el('span', 'crosshair', c);
      if (d.glyph && name !== 'stick') {
        var g = el('span', 'glyph', c);
        g.textContent = d.glyph;
      }
      var L = el('span', 'lbl', c);
      L.textContent = d.label;

      var def = TC.layout[name] || { x: 0.5, y: 0.5 };
      c.style.left = (def.x * 100) + '%';
      c.style.top = (def.y * 100) + '%';

      var entry = { el: c, nub: null };
      if (name === 'stick') entry.nub = controls_nub_pending;
      controls[name] = entry;
      controls_nub_pending = null;

      rootEl.appendChild(c);
      bindControl(c, name);
    });
    if (savedState) applySavedState(savedState);
    applyScale();
  }

  // ---- toggle / show / hide ------------------------------------------------
  function onToggleClick(ev) {
    if (ev) { ev.preventDefault(); ev.stopPropagation(); }
    if (visible) hide(); else show();
  }

  // Persistent lock chip (Nicko 10-03): the edit bar only existed on the
  // auto-edit first show, so once a layout was saved there was NO way back
  // into edit mode and no lock visual at all. This chip always sits under
  // the toggle whenever the layer is visible; it re-opens edit mode.
  function buildLockChip() {
    if (lockChipEl) return;
    lockChipEl = el('div');
    lockChipEl.id = 'wh-touch-lockchip';
    lockChipEl.textContent = UNLOCKED_GLYPH;
    lockChipEl.title = 'Edit controls: move / scale / lock';
    document.body.appendChild(lockChipEl);
    ['mousedown', 'contextmenu'].forEach(function (t) {
      lockChipEl.addEventListener(t, function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
      });
    });
    lockChipEl.addEventListener('pointerdown', function (ev) {
      ev.preventDefault();
      ev.stopPropagation();
      if (!visible) show();
      setEditMode(true);        // edit bar returns; unlock to drag
    });
    lockChipEl.addEventListener('click', function (ev) {
      ev.preventDefault();
      ev.stopPropagation();
    });
  }

  function removeLockChip() {
    if (!lockChipEl) return;
    lockChipEl.parentNode.removeChild(lockChipEl);
    lockChipEl = null;
  }

  function show() {
    buildToggle();
    buildControls();
    buildLockChip();          // Nicko 10-03: edit-mode door always visible
    rootEl.style.display = '';
    visible = true;
    toggleEl.classList.add('active');
    if (firstShow) {
      firstShow = false;
      // Placement happens once: only the very first show with NOTHING stored
      // yet opens edit mode; every later show returns locked in play mode.
      if (!hadSavedLayout) setEditMode(true);
    }
    saveState();
  }

  function hide() {
    if (rootEl) rootEl.style.display = 'none';
    visible = false;
    if (toggleEl) toggleEl.classList.remove('active');
    removeLockChip();         // chip belongs to the visible layer only
    setEditMode(false);
    releaseAll();
    saveState();
  }

  // ---- edit mode -------------------------------------------------------------
  function setEditMode(on) {
    editMode = !!on;
    unlocked = false;
    if (!rootEl) return;
    rootEl.classList.toggle('edit', editMode);
    buildEditBar();
  }

  function buildEditBar() {
    if (editBarEl) { editBarEl.parentNode.removeChild(editBarEl); editBarEl = null; }
    if (!editMode) return;

    editBarEl = el('div');
    editBarEl.id = 'wh-touch-editbar';
    document.body.appendChild(editBarEl);

    var minus = el('button', '', editBarEl);
    minus.textContent = '\u2212';
    minus.title = 'Smaller';
    minus.addEventListener('click', function () { nudgeScale(-0.1); });

    var plus = el('button', '', editBarEl);
    plus.textContent = '+';
    plus.title = 'Bigger';
    plus.addEventListener('click', function () { nudgeScale(0.1); });

    var lockBtn = el('button', '', editBarEl);
    lockBtn.id = 'wh-touch-lockbtn';
    lockBtn.textContent = LOCKED_GLYPH;
    lockBtn.title = unlocked ? 'Lock placement (saves layout)' : 'Unlock placement';
    lockBtn.addEventListener('click', function () {
      unlocked = !unlocked;
      rootEl.classList.toggle('unlocked', unlocked);
      lockBtn.textContent = unlocked ? UNLOCKED_GLYPH : LOCKED_GLYPH;
      if (!unlocked) saveState();   // locking placement saves the layout
      lockBtn.classList.toggle('amber', unlocked);
    });

    var resetBtn = el('button', '', editBarEl);
    resetBtn.textContent = 'Reset';
    resetBtn.title = 'Restore default layout';
    resetBtn.addEventListener('click', function () {
      scale = TC.scaleDefault || 1.0;
      order.forEach(function (name) {
        var c = controls[name];
        if (!c) return;
        var def = TC.layout[name] || { x: 0.5, y: 0.5 };
        c.el.style.left = (def.x * 100) + '%';
        c.el.style.top = (def.y * 100) + '%';
      });
      applyScale();
      saveState();
    });

    var doneBtn = el('button', 'amber', editBarEl);
    doneBtn.textContent = 'Done';
    doneBtn.title = 'Lock placement and play';
    doneBtn.addEventListener('click', function () {
      unlocked = false;
      rootEl.classList.remove('unlocked');
      setEditMode(false);         // locking saves layout (saveState inside)
      saveState();
    });
  }

  function nudgeScale(d) {
    scale = clamp(scale + d, TC.scaleMin || 0.6, TC.scaleMax || 1.6);
    applyScale();
    releaseAll();                 // re-position held pointers for new geometry
    saveState();
  }

  function applyScale() {
    order.forEach(function (name) {
      var c = controls[name];
      if (!c) return;
      var size = (name === 'stick' || name === 'cam')
        ? TC.joystickRadius * 2 * scale
        : TC.buttonSize * scale;
      c.el.style.width = Math.round(size) + 'px';
      c.el.style.height = Math.round(size) + 'px';
    });
  }

  // ---- pointer bindings ----------------------------------------------------------
  function bindControl(elm, name) {
    // Mouse compat events must not reach the document handlers (a real-mouse
    // tap on Attack would otherwise double-fire through document mousedown and
    // start stale camera dragging). Real canvas/mouse input is unaffected.
    ['mousedown', 'mouseup', 'touchstart', 'touchend', 'contextmenu']
      .forEach(function (t) {
        elm.addEventListener(t, function (ev) {
          ev.preventDefault();
          ev.stopPropagation();
        });
      });
    elm.addEventListener('pointerdown', function (ev) {
      if (editMode) { startDrag(ev, name); return; }  // edit: drag only
      if (!visible) return;
      ev.preventDefault();
      ev.stopPropagation();
      if (elm.setPointerCapture) { try { elm.setPointerCapture(ev.pointerId); } catch (e) {} }
      elm.classList.add('touched');
      if (name === 'stick') {
        pointers[ev.pointerId] = { role: 'stick' };
        stickBegin(ev);
      } else if (name === 'cam') {
        pointers[ev.pointerId] = { role: 'cam' };
        lastCam[ev.pointerId] = { x: ev.clientX, y: ev.clientY };
      } else {
        pointers[ev.pointerId] = { role: 'btn', name: name };
        btnPress(name);
      }
    });

    elm.addEventListener('pointermove', function (ev) {
      var p = pointers[ev.pointerId];
      if (!p) return;
      ev.preventDefault();
      if (p.role === 'stick') stickMove(ev);
      else if (p.role === 'cam') camMove(ev);
    });

    elm.addEventListener('pointerup', function (ev) {
      var p = pointers[ev.pointerId];
      if (!p) return;
      delete pointers[ev.pointerId];
      delete lastCam[ev.pointerId];
      elm.classList.remove('touched');
      if (p.role === 'stick') stickEnd();
      else if (p.role === 'cam') camEnd();
      else if (p.role === 'btn') btnRelease(p.name);
    });
    elm.addEventListener('pointercancel', function (ev) {
      var p = pointers[ev.pointerId];
      if (!p) return;
      delete pointers[ev.pointerId];
      delete lastCam[ev.pointerId];
      elm.classList.remove('touched');
      if (p.role === 'stick') stickEnd();
      else if (p.role === 'cam') camEnd();
      else if (p.role === 'btn') btnRelease(p.name);
    });
  }

  // ---- edit-mode dragging (unlocked placement) ---------------------------------
  function startDrag(ev, name) {
    if (!unlocked) return;     // locked placement: controls inert in edit mode
    if (dragId !== null) return;
    dragId = ev.pointerId;
    dragName = name;
    var r = controls[name].el.getBoundingClientRect();
    dragOffX = ev.clientX - r.left;
    dragOffY = ev.clientY - r.top;
    if (ev.target.setPointerCapture) {
      try { ev.target.setPointerCapture(ev.pointerId); } catch (e) {}
    }
  }

  function moveDrag(ev) {
    if (ev.pointerId !== dragId || !dragName) return;
    var c = controls[dragName];
    if (!c) return;
    var r = c.el.getBoundingClientRect();
    // keep control CENTER inside the viewport (never fully off-screen)
    var x = clamp(ev.clientX - dragOffX + r.width / 2, 0, window.innerWidth);
    var y = clamp(ev.clientY - dragOffY + r.height / 2, 0, window.innerHeight);
    c.el.style.left = (x / window.innerWidth * 100) + '%';
    c.el.style.top = (y / window.innerHeight * 100) + '%';
  }

  function endDrag(ev) {
    if (ev.pointerId !== dragId) return;
    dragId = null;
    dragName = null;
    saveState();               // every drag end persists (also saved on lock)
  }

  function bindDocDrag() {
    document.addEventListener('pointermove', moveDrag, { passive: false });
    document.addEventListener('pointerup', endDrag);
    document.addEventListener('pointercancel', endDrag);
    window.addEventListener('blur', function () { releaseAll(); });
    window.addEventListener('resize', function () {
      // %-positions self-adjust; re-clamp fractions into 0..1 after resize
      order.forEach(function (name) {
        var c = controls[name];
        if (!c) return;
        c.el.style.left = clamp(fracX(c.el, name), 0, 1) * 100 + '%';
        c.el.style.top = clamp(fracY(c.el, name), 0, 1) * 100 + '%';
      });
    });
  }

  // ---- stick -> the SAME keys['KeyW/A/S/D'] booleans the keyboard writes -------
  function stickBegin(ev) {
    stickActiveId = ev.pointerId;
    stickOrigin.x = ev.clientX;
    stickOrigin.y = ev.clientY;
    var r = controls.stick.el.getBoundingClientRect();
    stickOrigin.cx = r.left + r.width / 2;
    stickOrigin.cy = r.top + r.height / 2;
    var nub = controls.stick.nub;
    if (nub) { nub.style.left = '50%'; nub.style.top = '50%'; }
  }

  function stickMove(ev) {
    if (ev.pointerId !== stickActiveId) return;
    var R = (TC.joystickRadius || 70) * scale;
    var dx = ev.clientX - stickOrigin.x;
    var dy = ev.clientY - stickOrigin.y;
    var len = Math.sqrt(dx * dx + dy * dy);
    var cl = len > R ? R / len : 1;
    var nx = (dx * cl) / R;
    var ny = (dy * cl) / R;
    var nub = controls.stick.nub;
    if (nub) {
      nub.style.left = (50 + (nx * 33)) + '%';
      nub.style.top = (50 + (ny * 33)) + '%';
    }
    var dz = TC.deadzone || 0.15;
    var mag = Math.sqrt(nx * nx + ny * ny);
    if (mag < dz) {
      writeStickKeys({ KeyW: false, KeyA: false, KeyS: false, KeyD: false });
      return;
    }
    writeStickKeys({
      KeyW: ny < -dz, KeyS: ny > dz,
      KeyA: nx < -dz, KeyD: nx > dz
    });
  }

  function writeStickKeys(on) {
    var p = getPlayer();
    if (!p || !p.keys) return;
    GAME_KEYS.stick.forEach(function (code) {
      var want = !!on[code];
      if (p.keys[code] !== want) p.keys[code] = want;
      keysWritten[code] = want;
    });
  }

  function stickEnd() {
    stickActiveId = null;
    writeStickKeys({ KeyW: false, KeyA: false, KeyS: false, KeyD: false });
    var nub = controls.stick.nub;
    if (nub) { nub.style.left = '50%'; nub.style.top = '50%'; }
  }

  // ---- camera pad -> writes the SAME fields the mousemove handler writes -------
  // (player.js ~242: camYaw/camPitch from px deltas at mouseSensDegPerPx, pitch
  // clamped to camPitchMin/MaxDeg; lastManualCamT stamps manual camera use
  // (10-04: camera yaw is manual-only, the auto-follow it gated is gone - the
  // stamp is kept for debug/future re-enable).
  // Writing those fields directly reuses that exact code path state; drag is
  // NOT touched so the mouse handler stays the sole owner of self.dragging.
  function camMove(ev) {
    var prev = lastCam[ev.pointerId];
    if (!prev) return;
    var dx = ev.clientX - prev.x;
    var dy = ev.clientY - prev.y;
    prev.x = ev.clientX;
    prev.y = ev.clientY;
    var p = getPlayer();
    if (!p || p.lockTarget) return;   // same rule as mouse cam: dead while locked
    if (p.inputSuspended) return;     // 10-05: inventory screen open
    if (dx === 0 && dy === 0) return;
    var sens = ((TC.sensDegPerPx !== undefined) ? TC.sensDegPerPx
      : window.WH_CONFIG.player.mouseSensDegPerPx) * Math.PI / 180;
    p.lastManualCamT = performance.now() / 1000;
    p.camYaw -= dx * sens;
    var C = window.WH_CONFIG.player;
    p.camPitch = clamp(p.camPitch + dy * sens,
      C.camPitchMinDeg * Math.PI / 180,
      C.camPitchMaxDeg * Math.PI / 180);
  }

  function camEnd() {
    // nothing persistent: pointer map entry is removed by the up/cancel handler
  }

  // ---- buttons -----------------------------------------------------------------
  function btnPress(name) {
    var p = getPlayer();
    if (!p || p.inputSuspended) return;   // 10-05: inventory screen open
    if (name === 'attack') {
      // Order C: attack button = LMB path (main-hand action)
      if (p.handButton) p.handButton('lmb', true);
    } else if (name === 'lockon') {
      if (p.onLockToggle) p.onLockToggle();
    } else if (name === 'dodge') {
      if (p.tryRoll) p.tryRoll();
    } else if (name === 'sprint') {
      var on = p.keys['ShiftLeft'] && keysWritten['ShiftLeft'];
      setSprint(!on);
    } else if (name === 'block') {
      // Order C: block button = RMB path (off-hand action: left caster ->
      // cast, left shield -> block on press, endBlock on release = press-hold)
      if (p.handButton) p.handButton('rmb', true);
    } else if (name === 'interact') {
      // S3b: the E key on phone - shared game.js interact() entry point
      if (window.WH_DEBUG && window.WH_DEBUG.interact) window.WH_DEBUG.interact();
    }
  }

  function btnRelease(name) {
    if (name !== 'block' && name !== 'attack') return;
    var p = getPlayer();
    if (!p) return;
    if (p.handButton) p.handButton(name === 'attack' ? 'lmb' : 'rmb', false);
  }

  function setSprint(on) {
    var p = getPlayer();
    if (!p || !p.keys) return;
    p.keys['ShiftLeft'] = !!on;
    keysWritten['ShiftLeft'] = !!on;
    var c = controls.sprint;
    if (c) c.el.classList.toggle('active', !!on);
  }

  // clear every key state we set + block/sprint visuals (hide/blur safety)
  function releaseAll() {
    var p = getPlayer();
    if (p && p.keys) {
      if (keysWritten['ShiftLeft']) { p.keys['ShiftLeft'] = false; keysWritten['ShiftLeft'] = false; }
      GAME_KEYS.stick.forEach(function (code) {
        if (keysWritten[code]) { p.keys[code] = false; keysWritten[code] = false; }
      });
    }
    if (controls.sprint) controls.sprint.el.classList.remove('active');
    var nub = controls.stick && controls.stick.nub;
    if (nub) { nub.style.left = '50%'; nub.style.top = '50%'; }
    pointers = {};
    lastCam = {};
    stickActiveId = null;
  }

  function getPlayer() {
    // WH_DEBUG.player does not exist; the documented accessor is getPlayer()
    // (game.js setupDebugHooks). Guarded so the layer never throws pre-boot.
    try {
      return (window.WH_DEBUG && window.WH_DEBUG.getPlayer &&
              window.WH_DEBUG.getPlayer()) || null;
    } catch (e) { return null; }
  }

  // ---- saved-state application ---------------------------------------------------
  function applySavedState(saved) {
    if (saved.scale && typeof saved.scale === 'number') {
      scale = clamp(saved.scale, TC.scaleMin || 0.6, TC.scaleMax || 1.6);
    }
    order.forEach(function (name) {
      var c = controls[name];
      var pos = saved.controls[name];
      if (!c || !pos) return;
      if (typeof pos.x === 'number' && typeof pos.y === 'number') {
        c.el.style.left = clamp(pos.x, 0, 1) * 100 + '%';
        c.el.style.top = clamp(pos.y, 0, 1) * 100 + '%';
      }
    });
    applyScale();
  }

  // ---- public API ----------------------------------------------------------------
  window.WH_TouchControls = {
    init: function () {
      if (inited) return;
      inited = true;
      bindDocDrag();
      savedState = loadState();
      hadSavedLayout = !!(savedState && savedState.controls &&
        Object.keys(savedState.controls).length);
      buildToggle();            // toggle button always available (z 45)
      // CONFIG.enabled OR a previously-shown saved layer reopens it; layout is
      // applied inside buildControls from savedState. No blind save here, so a
      // freshly saved layout is never clobbered by an empty controls table.
      if (TC.enabled || (savedState && savedState.enabled)) show();
    },
    show: function () { show(); },
    hide: function () { hide(); },
    setEditMode: function (on) { setEditMode(!!on); },
    isVisible: function () { return visible; },
    isEditMode: function () { return editMode; }
  };

  // Auto-init: this script loads at body end (DOM above already parsed) and
  // BEFORE game.js, but getPlayer() defers to WH_DEBUG at interaction time,
  // so boot order is safe. CONFIG.touch missing simply disables the layer.
  if (window.WH_CONFIG && window.WH_CONFIG.touch) {
    window.WH_TouchControls.init();
  }
})();
