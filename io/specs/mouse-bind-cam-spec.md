# IO Spec: Pointer-Lock Mouse Bind Camera (v8)

- Repo: /workspace/witch-hunter (GitHub CaptainPickard/witch-hunter)
- Branch: feat/mouse-bind-cam (branched from dev at HEAD 09712f6)
- Date: 2026-10-05
- Author: IO. This file is the implementation spec OF RECORD. Dispatch-text
  divergences are superseded by this text. Validation spec of record:
  io/specs/mouse-bind-cam-valspec.md (Testerbot authors BEFORE Devbot starts).
- Requested by Nicko 2026-10-05: mouse moves the camera without click-drag on
  keyboard+mouse play; a UI button and a backquote (`) shortcut bind/unbind the
  mouse-to-camera so the cursor is free to click UI (e.g. a future inventory).

## 1. Feature contract (user-facing)

While BOUND:
- Mouse movement rotates the camera continuously with no button held. The OS
  cursor is hidden (browser pointer lock does this natively).
- LMB still attacks, RMB still blocks (or casts when offhand is a spell), wheel
  still zooms. Camera yaw/pitch apply the same sensitivity and clamps as the
  existing drag path.
- Lock-on (KeyF target lock) still owns the camera while a lock target exists;
  bound-mouse motion deltas are ignored while locked (same precedence as today).

While UNBOUND (the initial state):
- OS cursor visible, camera does not respond to plain mouse movement.
- The old click-drag camera still works exactly as today (zero regression).
- Left-clicking the game canvas attacks AND re-binds (auto-rebind), controlled
  by CFG.mouse.autoBindOnCanvasClick (default true).
- Left-clicking any DOM UI element (the toggle chip; future inventory panels)
  does NOT re-bind. This is the standing forward-contract the future inventory
  overlay will rely on: only canvas-surface clicks rebind.

Bind/unbind controls:
- Backquote (`) toggles bind/unbind. No other key changes.
- A HUD chip button (bottom-right, gothic styled) shows `MOUSE: BOUND [`]` or
  `MOUSE: FREE [`]` and toggles on click.
- Esc frees the mouse via the browser's native pointer-lock exit: there is NO
  explicit Esc keydown handler. State sync relies solely on the
  pointerlockchange event (the browser always fires it on Esc).
- If a pointer-lock request fails or is rejected (browser throttle after an Esc
  exit, sandboxed iframe, missing API), the game must not throw an uncaught
  error; state stays FREE and the chip reads FREE.

## 2. Environment constraints (hard)

- No node on the VPS: validation runs via the python playwright driver
  (/usr/local/bin/playwright). Syntax/behavior gate is: organic-interaction run
  with ZERO console errors. Never invoke node or node --check.
- Build via python3 tools/build_v8.py from repo root (new script per section 5).
- Headless pointer-lock caveat: synthetic mouse movement under active pointer
  lock may not produce nonzero movementX/movementY in headless Chromium. If the
  live-locked path cannot be exercised headlessly, the fallback in section 7
  (N2b: real dispatched MouseEvent carrying movementX through the real
  document listener) is the authorized verification vehicle. This pre-authorized
  degradation is an honest-partial PASS per gate rules, recorded as RECORD.
- Working tree has pre-existing entries NOT in scope of this build (do not
  touch, do not commit): modified scratch/treeqa/roundI/decimate.jsonl and
  untracked io/* files (assemble_harness.py, astrabot-brief-*.md, cc-round-*.md,
  cc_opus_prompt.md, check_*.py, compare_*.py, dbg_*.py and friends).

## 3. Current-state precision map (verified at HEAD 09712f6; re-check +/-3 lines)

prototype/js/player.js:
- 100-107: camera orbit constructor fields (camYaw=PI, camPitch=deg2rad(22),
  camDist, dragging, lastDragX/Y, lastManualCamT=-1e9). New bind state fields
  go AFTER the lastManualCamT line (keep-alive: all existing lines stay).
- 245-265: keydown handler (KeyF lock-on toggle, KeyQ loadout, Digit1-5 belt,
  KeyR/KeyT consumables). Backquote branch is ADDED here per section 5.
- 266-268: keyup handler. Untouched.
- 269-285: mousedown (LMB attack + drag start; RMB block/cast via offhand).
  Rebind hook per section 5. KEEP the attack + RMB semantics verbatim.
- 286-290: mouseup (LMB drag end, RMB shield endBlock). Untouched except no
  changes.
- 291-296: contextmenu preventDefault/stopPropagation. Untouched.
- 297-307: mousemove (drag-cam: camYaw -= dx*deg2rad(mouseSensDegPerPx);
  camPitch += dy*deg2rad(mouseSensDegPerPx) clamped to
  deg2rad(camPitchMinDeg)..deg2rad(camPitchMaxDeg), bail when lockTarget set,
  lastManualCamT stamped when dxdy nonzero). This block is REWRITTEN into the
  two-branch shape of section 5; the math must survive verbatim inside the
  shared applyCamDelta helper.
- 308-311: wheel zoom (camDist clamp 3.0..14.0). Untouched.
- lastManualCamT current readers: NONE (write-only vestige of the removed
  10-04 auto-follow). Preservation law: touch pad + mouse paths keep stamping
  it; no new readers required.

prototype/js/CONFIG.js:
- 571-589: player block tail (camMinDistance 3.0, camMaxDistance 14.0,
  camPitchMinDeg -15, camPitchMaxDeg 65, camPitchDistShrink, camFollowLerp,
  mouseSensDegPerPx 0.25, respawnDelay, focus keys). The new top-level
  `mouse` block is inserted AFTER the player block closing `},` (line 589).
  Keep-alive: no existing key may change value or name.
- ~895-899: touch block (sensDegPerPx 0.25 with comment matching
  mouseSensDegPerPx). Untouched. The touch layer self-inits only when
  WH_CONFIG.touch is truthy (touch-controls.js tail); on desktop it stays
  dormant and this feature must not disturb it.

prototype/js/touch-controls.js:
- ~561-590: virtual cam pad writes p.camYaw/p.camPitch/p.lastManualCamT with a
  header comment stating the mouse handler is sole owner of self.dragging.
  FILE MUST BE UNTOUCHED (P3).

prototype/index.html:
- 10-35: #wh-root > #wh-canvas + #wh-hud (bars, fps, res-tuner, region-name,
  gate-hint, lock-reticle at line 28, death-overlay, load-note boot overlay).
  Chip element is inserted INSIDE #wh-hud after the wh-lock-reticle div.
- 39-52: script load order (vendor3, moveset, CONFIG, region-defs, assets,
  anim, spells, player, enemy, region-manager, touch-controls, game).
  Untouched.

prototype/style.css:
- 75-110: #wh-fps (top:12 right:16) and #wh-res-tuner (top:32 right:16,
  pointer-events:none, .dim/.pulse). Chip CSS block goes after this section.
- #wh-hud { position:absolute; inset:0; pointer-events:none; } (lines ~28-31):
  the chip MUST set pointer-events:auto on itself or it is unclickable.

prototype/js/game.js (read-only for this feature):
- 471: camera follow reads p.camYaw (fx/fz). 500: lock-on writes p.camYaw.
- 885: dev yaw write. 883: isLocked() reads player.lockTarget.
- 1050-1069: boot completes, fade overlay, running=true. No camera-input edits.

tools/build_v7.py:
- Template mechanic: index.html -> strip stylesheet links -> inject style.css
  before </head> -> inline each <script src> in order -> rewrite <title>.
  UNTOUCHED (P6). New tools/build_v8.py is a copy with only OUT path and
  title string changed.

## 4. New CONFIG (exact values)

prototype/js/CONFIG.js, new top-level block after the player block:

  mouse: {
    pointerLockSensMult: 1.0,       // bound-mouse multiply on mouseSensDegPerPx
    autoBindOnCanvasClick: true     // LMB on canvas while free: attack + rebind
  },

Sensitivity note for Nicko (playtest tuning): if bound-mouse feels fast vs the
old drag, lower pointerLockSensMult (e.g. 0.8). No other key changes.

## 5. player.js design (exact behavior)

New constructor fields (after lastManualCamT line):
  this.mouseBound = false;          // desired/actual bind state, synced via
                                    // pointerlockchange (single source of truth)
  this.mouseChipEl = null;          // HUD chip element, cached in initInput

New prototypes:
- Player.prototype.applyCamDelta = function (dxPx, dyPx): exactly the current
  drag math from lines 304-306:
    this.camYaw -= dxPx * deg2rad(CFG.mouseSensDegPerPx);
    this.camPitch += dyPx * deg2rad(CFG.mouseSensDegPerPx);
    this.camPitch = Math.max(deg2rad(CFG.camPitchMinDeg),
      Math.min(deg2rad(CFG.camPitchMaxDeg)), this.camPitch);
  Callers also stamp lastManualCamT BEFORE calling when (dx,dy) nonzero
  (keeps the existing stamp-first ordering of line 303).
- Player.prototype.bindMouse = function (): no-op if
  document.pointerLockElement already truthy or if
  !document.body.requestPointerLock (capability miss). Otherwise:
    var el = document.getElementById('wh-canvas');
    var self = this;
    var res = el.requestPointerLock();
    if (res && typeof res.then === 'function') {
      res.then(function () { self.syncMouseChip(); },
               function () { self.syncMouseChip(); });
    }
  (Chrome returns a Promise; Firefox/sync builds return undefined and the
  pointerlockchange event carries the state. Rejection path must swallow the
  error: NO uncaught exception, chip synced truthfully.)
- Player.prototype.unbindMouse = function (): if document.pointerLockElement,
  document.exitPointerLock(). Then syncMouseChip() (event may land after).
- Player.prototype.toggleMouseBind = function ():
  this.mouseBound ? this.unbindMouse() : this.bindMouse();
- Player.prototype.syncMouseChip = function (): this.mouseBound =
  !!document.pointerLockElement; if chip cached, textContent =
  mouseBound ? 'MOUSE: BOUND [`]' : 'MOUSE: FREE [`]' (literal backtick char
  inside brackets).

pointerlockchange wiring (inside initInput, alongside existing listeners):
  document.addEventListener('pointerlockchange', function () {
    self.syncMouseChip();
  });

keydown addition (inside the existing keydown handler per section 3 map,
same !e.repeat guard style as siblings):
  if (e.code === 'Backquote' && !e.repeat) self.toggleMouseBind();
(NO Esc handler. NO preventDefault on Backquote.)

mousedown LMB branch addition (after the existing attack/drag lines, inside
the button===0 branch, BEFORE touching drag behavior):
  if (!self.lockTarget && !self.mouseBound &&
      CFG.mouse && CFG.mouse.autoBindOnCanvasClick &&
      e.target && e.target.id === 'wh-canvas') {
    self.bindMouse();
  }
  (Attack still fires this click - it already did above; drag start only when
  !mouseBound? NO: drag start lines stay untouched. While unbound everything
  behaves exactly as today; the bind request rides along. If the lock engages,
  the mousemove bound path takes over immediately.)

mousemove handler REWRITE (replaces lines 297-307 wholesale):
  document.addEventListener('mousemove', function (e) {
    if (self.lockTarget) return;            // lock-on owns the camera (keep)
    if (self.mouseBound && document.pointerLockElement) {
      var mdx = e.movementX || 0, mdy = e.movementY || 0;
      if (mdx === 0 && mdy === 0) return;
      self.lastManualCamT = performance.now() / 1000;
      self.applyCamDelta(mdx * CFG.mouse.pointerLockSensMult,
                         mdy * CFG.mouse.pointerLockSensMult);
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

mouseup: when mouse bound, LMB mouseup setting dragging=false is harmless and
stays. Unchanged file lines.

Chip click wiring (inside initInput, after pointerlockchange):
  var chip = document.getElementById('wh-mouse-chip');
  if (chip) { this.mouseChipEl = chip; chip.addEventListener('click',
    function (ev) { ev.preventDefault(); self.toggleMouseBind(); }); }

HUD chip guard: chip is inside #wh-hud (pointer-events:none container); the
chip's OWN css sets pointer-events:auto (section 6). While bound, the cursor
is hidden so the chip is reachable only unbound or via keyboard - correct.

## 6. index.html + style.css (exact anchors)

index.html: after the wh-lock-reticle line insert:
      <div id="wh-mouse-chip" title="Backquote toggles mouse bind">MOUSE: FREE [`]</div>

style.css: new block appended after the #wh-res-tuner section:
/* --- mouse bind chip (10-05 Nicko: pointer-lock camera bind toggle) --- */
#wh-mouse-chip {
  position: absolute;
  bottom: 14px;
  right: 16px;
  font-family: monospace;
  font-size: 12px;
  color: #d8d2c0;
  background: rgba(0, 0, 0, 0.45);
  border: 1px solid #6a6350;
  padding: 4px 8px;
  pointer-events: auto;
  cursor: pointer;
  user-select: none;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.9);
}
Placement rationale: bottom-right is collision-free on desktop (fps/tuner are
top-right; bars top-left; gate hint is centered transient).

## 7. Acceptance criteria (validation spec must cover each, numbered N1-N10)

- N1 Bind: pressing Backquote requests pointer lock on the canvas; document
  .pointerLockElement truthy; mouseBound true; chip text MOUSE: BOUND [`].
- N2 Bound motion applies the applyCamDelta math; two verification vehicles:
  N2a is the live-locked synthetic-motion variant (RECORD-eligible when
  headless movementX stays 0), N2b is the dispatched-event variant.
  camYaw/camPitch with applyCamDelta math (sens 0.25 * pointerLockSensMult)
  and pitch clamps at the -15/65 deg bounds. Headless degradation: if movementX
  stays 0 under CDP synthetic motion, mark N2a RECORD with evidence and run
  N2b.
- N2b Bound motion (dispatched): dispatched MouseEvent on document with
  movementX/movementY set (while mouseBound true and pointerLockElement
  truthy) alters camYaw/camPitch per the same math; a dispatched zero-movement
  event does not stamp lastManualCamT.
- N3 Unbind: pressing ` again (or Esc) exits lock; mouseBound false; chip
  MOUSE: FREE [`]. Esc path is validated via pointerlockchange only.
- N4 Free-mouse inertness: while unbound and no button held, synthetic
  mousemove must not change camYaw/camPitch.
- N5 Auto-rebind: unbound LMB click with target wh-canvas fires tryAttack AND
  requests lock; unbound LMB click on the chip (or any non-canvas DOM) does NOT
  request lock. CFG.mouse.autoBindOnCanvasClick=false disables the rebind
  (config-driven, tested both ways).
- N6 Chip click toggles both directions.
- N7 Failure hardening: with requestPointerLock stubbed to throw (or return a
  rejected Promise), press `: no uncaught console error, mouseBound stays
  false, chip FREE. (Fault-injection stub installed BEFORE the keypress is the
  sanctioned vehicle; not a state-mutation violation.)
- N8 lastManualCamT: stamps on nonzero bound motion and nonzero drag; zero
  deltas never stamp.
- N9 Build: python3 tools/build_v8.py writes prototype/builds/v8-playable.html
  containing: the chip id, the CFG.mouse block, inline scripts with NO leftover
  <script src=, title Witch Hunter v8 - Mouse Bind Cam.
- N10 Console hygiene: the full organic interaction run (boot -> move -> attack
  -> bind -> move -> unbind -> chip click -> attack) ends with ZERO console
  errors.

Organic-path law: N1-N6, N8, N10 must be driven by real page.keyboard /
page.mouse input through the page's own listeners. The ONLY sanctioned
non-organic acts: the N7 fault-injection stub (installed pre-dispatch) and the
N2b synthesized event (dispatched through the real document listener).

## 8. Preservation floor (P1-P8, validated as invariants)

- P1 Unbound drag-cam math identical to HEAD (applyCamDelta body equals the
  old mousemove math, same sens/clamps).
- P2 LMB attack, RMB block/cast, contextmenu block, wheel zoom semantics
  unchanged.
- P3 touch-controls.js byte-identical to HEAD.
- P4 Lock-on camera framing untouched (game.js 500 path; mousemove early
  return on lockTarget preserved in both branches).
- P5 CONFIG additive-only: no existing key renamed/reordered/retyped.
- P6 tools/build_v7.py byte-identical; builds/v1|v2|v7-playable.html untouched.
- P7 Keyboard semantics unchanged for KeyF/KeyQ/Digit1-5/KeyR/KeyT/Shift/WASD.
- P8 Out-of-scope dirty-tree entries (section 2 list) untouched by the build.

## 9. Gate sequence and ownership

1. Testerbot authors io/specs/mouse-bind-cam-valspec.md + the validation
   harness tests/wh_mousebind_validation.py FIRST, smoke-runs it against the
   PRE-build tree (expected mostly-FAIL, zero crashes, failure MESSAGES
   recorded as honest wiring evidence), freezes the baseline (HEAD, tree
   entries, P-floor observations).
2. Devbot implements ONLY this spec + the Testerbot validation spec (specs of
   record). Devbot runs the harness during build but NEVER edits it. Devbot
   does NOT commit. Devbot runs tools/build_v8.py and reports changed files.
3. Testerbot independently validates: full N1-N10 + P1-P8, verdict JSON with
   file:line evidence verified to exist at verdict time.
4. IO reviews, commits on feat/mouse-bind-cam, pushes dev:dev after PASS, then
   repoints the WebUI playtest button to v8.

Amendment protocol: mid-flight changes are logged AMENDMENT A<n> (<date>) in
BOTH spec files; anchors re-frozen; running children steered with the ruling
text inlined.