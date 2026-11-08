# ASTRABOT MISSION BRIEF - Mouse-bind camera (pointer-lock), Order A

Dateline: 2026-10-05, from IO. Standing order context (Nicko, verbatim):
"Stop everything, no more harness runs, I have said this before. I validate
by play testing. You have been working on this one feature all day, 6 hours.
I want you to dispatch astrabot to fix this."

Feature origin (Nicko, verbatim, 2026-10-05): "For the Witch Hunter project,
when I play with the mouse and keyboard, I want the mouse to automatically
move the camera without clicking and dragging. Also, I want a UI button and a
keyboard shortcut, like \u0060 to bind and unbind the mouse and camera,
so when I want to click around the screen (like opening the inventory), the
camera unbinds from the mouse."

You are Astrabot, running as a Claude Code print-mode agent in the
witch-hunter repo worktree /tmp/wh-worldfeat (branch feat/world-visuals).
Report file, commits, and pushes as in previous missions. A second worktree
at /tmp/wh-mousebindfeat (branch feat/mouse-bind-cam) ALREADY CONTAINS the
full implementation (see section 1 - it is DONE to the 26/29-green level).
Your job is FINISH + INTEGRATE: port it, reconcile the chip with the new
inventory Order A UI, verify build, report. Nicko plays the result.

## 0. LAWS (hard, no exceptions)

1. NO automated harness runs. NO headless-browser smoke runs. NO pytest
   harness re-runs of tests/wh_mousebind_validation.py (it stays on the
   feat/mouse-bind-cam branch as historical record; it MUST NOT be run -
   Nicko's playtest is the ONLY acceptance test. Syntax checks only.)
2. One change order at a time; commit + push each completed sub-step.
3. All tunables in CONFIG - no magic numbers in game code.
4. Art law: pixelated (512 NEAREST + 5-bit posterize), raw meshes, darkwood
   palette, one accent per frame. No new GLBs unless ordered.
5. Player copy: never the word "free" (chip label MUST NOT read MOUSE: FREE -
   use MOUSE: UNBOUND); no hardcoded agent names.
6. JS syntax check (node --check) is the ONLY verification allowed after
   edits. NO harness runs even to "confirm" - law 1.
7. Do NOT modify: tests/, io/specs/, scratch/, docs/, art-direction/3d/,
   prototype/js/touch-controls.js, prototype/js/game.js, CONFIG.touch.
   Allowed files: prototype/js/player.js, prototype/js/CONFIG.js (additive
   only), prototype/index.html, prototype/style.css, tools/build_v8.py (new,
   clone of tools/build_v7.py), prototype/builds/v8-playable.html (built),
   plus EXPLICIT inventory-UI integration touches in files Order A
   inventory already owns (hud-inventory render block only if the chip must
   move - prefer CONFIG positioning, not file surgery).
8. Worktrees: this brief lives in /tmp/wh-worldfeat (feat/world-visuals,
   has Order A inventory UI). The mouse-bind implementation lives in
   /tmp/wh-mousebindfeat (feat/mouse-bind-cam). Port FROM the latter INTO
   the former. The /workspace/witch-hunter checkout on feat/mouse-bind-cam
   is IO's reference copy - read-only for you.

## 1. Current mechanics (verified by IO - do not re-research)

### 1a. The complete mouse-bind implementation (from feat/mouse-bind-cam)

git diff exists in /tmp/wh-mousebindfeat (branch feat/mouse-bind-cam).
Summary of what landed (26 of 29 harness rows green before the harness was
decommissioned mid-session; zero page errors in every run; ALL behavioral
legs verified correct in isolation by IO probes):

- prototype/js/player.js (84 insertions):
  - MCFG alias: var MCFG = window.WH_CONFIG.mouse || {}; (line ~13)
  - State: this.mouseBound = false; this.mouseChipEl = null; (constructor,
    after lastManualCamT line ~line 111)
  - keydown: if (e.code === 'Backquote' && !e.repeat) self.toggleMouseBind();
  - mousedown: EARLY RETURN unless e.target.id === 'wh-canvas' (UI clicks
    cannot attack/drag/auto-rebind); then tryAttack(); auto-rebind gated by
    MCFG.autoBindOnCanvasClick.
  - mousemove: branch (1) mouseBound && document.pointerLockElement ->
    movementX/Y * MCFG.pointerLockSensMult -> applyCamDelta, stamp
    lastManualCamT; (2) else legacy drag path -> applyCamDelta (HEAD math
    byte-identical: applyCamDelta(dx,dy) preserves camYaw -= dx*deg2rad(...),
    camPitch += dy*deg2rad(...), pitch clamped camPitchMinDeg/MaxDeg).
  - New prototypes: applyCamDelta(dxPx,dyPx), bindMouse() (requestPointerLock
    on #wh-canvas, try/catch hardens sync throws, promise .then syncs chip),
    unbindMouse(), toggleMouseBind(), syncMouseChip() (mouseBound =
    !!document.pointerLockElement; chip textContent MOUSE: BOUND / MOUSE:
    UNBOUND).
  - pointerlockchange listener -> syncMouseChip (single source of truth; NO
    Esc key handler - native exit resyncs).
  - chip click handler (cached #wh-mouse-chip) -> toggleMouseBind.
- prototype/js/CONFIG.js: WH_CONFIG.mouse = { pointerLockSensMult: 0.85,
  autoBindOnCanvasClick: true } at ROOT (sibling of touch/spell - NOT inside
  player).
- prototype/index.html: <div id="wh-mouse-chip" title="Backquote toggles
  mouse bind">MOUSE: UNBOUND [...]</div> inside #wh-hud.
- prototype/style.css: #wh-mouse-chip absolute, bottom:14px right:16px,
  monospace, pointer-events:auto, cursor:pointer, gothic palette (#d8d2c0 on
  rgba(0,0,0,0.45), border #6a6350).
- tools/build_v8.py: clone of build_v7.py, title 'Witch Hunter v8 - Mouse
  Bind Cam', writes prototype/builds/v8-playable.html.
- Built artifact v8-playable.html exists (2,567,931 bytes,
  sha256 a558e09422ffc19682bcebc468779960d4106a73ef748f36d9b30882701c23b0).

### 1b. Key-collision check (RESOLVED BY IO - no collision)

VERIFIED 2026-10-05: Order A's inventory opens with KeyI and closes with
KeyI/Escape (CONFIG.inventoryUI openKey/closeKeys); it does NOT use
Backquote. NO collision exists. Implement instead the small closing-knob:
CONFIG.mouse.rebindOnUiClose (default false to start) - when true, closing
any UI overlay while the mouse is unbound rebinds the mouse. Do not wire
inventory events for this beyond reading the overlay's close moment IF it
exposes one cleanly; if wiring would require editing inventory.js, SKIP the
knob entirely (report it as parked) - the chip + Backquote toggle fully
satisfy the order as written.

### 1c. Chip label collision check
If Order A's inventory overlays any element near bottom-right (chip sits at
bottom:14px right:16px), reposition the chip via CSS ONLY (top-right under
wh-fps/wh-res-tuner is acceptable: top:52px right:16px) - never edit
inventory files for this.

### 1d. P5-pad finding (INFORMATION ONLY - no action required)
The decommissioned harness had one residual row that failed in-run but
passed on pristine pages (touch cam pad steering). IO probes proved game
behavior correct in isolation; suspicion is harness-self-interference (the
whMBTest moveLog capture listener), which no longer matters because the
harness is retired. Playtest note for Nicko: touch pad steering SHOULD be
unaffected; if it is not, that is a REAL bug to report.

## 2. ORDER (A/B) - scope

### ORDER A (this brief):
1. Port the mouse-bind implementation (1a) from feat/mouse-bind-cam worktree
   into feat/world-visuals (the /tmp/wh-worldfeat tree), preserving the
   diff EXACTLY except for the three reconciliation points: (1a-chip-label)
   MOUSE: UNBOUND not MOUSE: FREE; (1b) the \u0060/inventory key collision
   resolution; (1c) chip reposition only if needed.
2. Create tools/build_v8.py (clone of build_v7.py pattern, v8 title).
3. Build prototype/builds/v8-playable.html.
4. node --check on edited JS files ONLY.
5. Commit + push to feat/world-visuals.
6. Write scratch/mousebind_orderA_report.md: what landed, per-file, CONFIG
   keys, which 1b variant was found (collision vs separate key), judgment
   calls, build sha256.

### ORDER B - do NOT implement (fenced out):
- Inventory grid expansion, character tab, per-hand equip changes (Order B
  brief exists as a ledger entry - separate mission).
- Touch control layout changes.
- Any new art/assets.
- Any harness resurrection.

## 3. Acceptance criteria (Nicko playtest)

- A: Mouse (no button held) steers the camera smoothly on its own.
- B: \u0060 unbinds the mouse; OS cursor visible; clicking HUD does not attack.
- C: \u0060 rebinds (or auto-rebind occurs per CONFIG) and camera follows mouse
  again; Esc also unbinds.
- D: The chip toggles bind/unbind on click, reads MOUSE: BOUND / MOUSE:
  UNBOUND.
- E: Keyboard WASD/attack/roll all unchanged; touch controls unaffected.
- F: Inventory (Order A) opens and is clickable with the unbound mouse (or
  with its own key if no collision existed).

Report requirement: scratch/mousebind_orderA_report.md (see ORDER A step 6).