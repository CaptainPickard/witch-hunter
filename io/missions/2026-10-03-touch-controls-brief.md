# Astrabot Mission Brief - touch controls layer (2026-10-03)

Nicko order (verbatim intent): "add some haptic feedback controls, PARALLEL to
the current mouse and keyboard controls. A UI button which could show the
outline of the thumb circle controls for movement and camera, sprint toggle,
attack, lockon, dodge and block buttons for when we add block that is. When
this UI button is clicked, it shows the faint outlines and icons AND a way to
move them around the screen, locking placement with a lock icon button that
locks and unlocks placement and scaling of the controls themselves."

Baseline: feat/world-visuals @ 8f1143a in worktree /tmp/wh-worldfeat. NO
harness runs - his playtest is the bar. esprima syntax checks only. ONE commit
to feat/world-visuals IN THE WORKTREE (message starts "feat: touch controls"),
then append "## Astrabot findings" and amend. NO pushes. No touching:
/workspace/witch-hunter, servers, io/specs, docs/planning, GLB/PNG binaries,
scratch/. Work method (hard): commit code EARLY, keep responses small, final
report max 8 lines.

## IO pre-read: the exact input map to call (player.js, verified today)
- Movement: `self.keys['KeyW'/'KeyA'/'KeyS'/'KeyD']` boolean map - virtual
  stick writes these four booleans from a direction vector (deadzone ~0.15).
- Camera: mousemove handler at player.js ~242 reads pointer deltas when
  dragging - virtual camera pad feeds the SAME code path: expose the
  existing drag logic by writing the same state it writes (study it first;
  if it reads clientX deltas with a flag, set those fields directly).
- Attack (tap): `self.tryAttack()`
- Lock-on: `self.onLockToggle()`
- Dodge: `self.tryRoll()`
- Block: RMB routing at player.js ~218-231: offhand==='spell' -> tryCast(),
  shield -> tryBlock() on press + endBlock() on release. The virtual block
  button REPLICATES THIS ROUTING EXACTLY (press-hold semantics), so it works
  today for cast and auto-works when block lands. Label it Shield/Cast.
- Sprint: find the sprint key (grep sprint in player.js; likely a keys entry
  read in the update loop). Virtual sprint = TOGGLE button that sets/clears
  that key state persistently, with a visual ON/OFF state on the button.
- NEVER remove or shadow existing mouse/keyboard handlers - parallel layer.

## Feature spec
1. NEW FILE prototype/js/touch-controls.js, loaded in index.html BEFORE
   game.js. Self-contained IIFE like the other files, window.WH_TouchControls
   with init(game)/show/hide/setEditMode.
2. Toggle button: small round icon button, right screen edge middle
   (id wh-touch-toggle, z-index 45 - ABOVE hud bars z and failure note z).
   Click = show/hide the controls layer. First show enters LAYOUT (edit)
   mode automatically so placement happens once; subsequent shows come back
   locked in play mode.
3. Controls (faint outlines + icon glyphs, CSS circles, pixel-look):
   - LEFT thumb circle: movement joystick (dynamic origin under thumb,
     clamped to circle, ghost outline at rest position)
   - RIGHT thumb circle: camera drag pad (any touch inside sweeps yaw/pitch)
   - Buttons: Sprint (toggle w/ ON state), Attack, Lock-on, Dodge, Block
     (block routes like RMB per above). Default bottom cluster right side.
4. EDIT MODE: unlock icon button (small, center-bottom, only visible in
   edit) toggles lock/unlock. When UNLOCKED: every control is draggable
   anywhere on screen (pointer events, touch-action:none, keep within
   viewport), and a +/- pair adjusts GLOBAL scale 0.6-1.6 (persisted).
   Locking saves layout. In edit mode controls do NOT inject game input.
5. Persistence: localStorage key wh-touch-layout-v1 = JSON
   {enabled, scale, controls: {name: {x,y} as FRACTIONS of viewport 0-1}}.
   Fractions not pixels (resize-safe). Load on init; save on lock. A small
   reset-layout button in edit mode restores CONFIG defaults.
6. CONFIG.touch block: { enabled:false (layer hidden until button used),
   opacity: 0.35 (faint), deadzone: 0.15, scaleDefault: 1.0, buttonSize: 64,
   joystickRadius: 70 } - plus the default layout table.
7. Multi-touch: Pointer Events API with pointerId tracking (move + camera
   simultaneously + a button tap). No third-party libs.
8. Style: darkwood palette, faint outlines (CONFIG opacity), amber accent
   only on active/sprint-on states. Do NOT collide with: top-left HUD bars
   (they own top:8 left:8 + failure note top:128), boot overlay z:30.

## Acceptance (Nicko plays, on desktop AND phone via tunnel)
- Toggle button shows/hides the layer; outlines faint, icons readable.
- Move stick walks the player, camera pad sweeps, attack/lock/dodge fire the
  real actions, sprint toggles ON visibly, block button routes cast/block
  correctly per offhand.
- Unlock: everything draggable, +/- rescales all, lock persists placement
  across a page RELOAD (localStorage), reset restores defaults.
- Mouse + keyboard behavior COMPLETELY unchanged while the layer exists.
Player copy law: never the word "free"; no hardcoded agent names.