# Astrabot report - mouse-bind camera, Order A port + reconcile (2026-10-05)

Brief: io/missions/2026-10-05-astrabot-mousebind-orderA-brief.md
Branch: feat/world-visuals (worktree /tmp/wh-worldfeat)

| Step | Commit | Summary |
|---|---|---|
| 1 port + reconcile | fbe12f8 | feat(input): pointer-lock mouse bind camera, ported + reconciled with inventory Order A |
| 2 build script | f3c2730 | build: tools/build_v8.py (clone of build_v7.py, v8 title + output) |
| 3 bundle | 656beb7 | build: v8 bundle - mouse bind cam on world-visuals + inventory Order A (worktree only) |
| 6 report | (this commit) | docs: this file |

Each commit was pushed to origin/feat/world-visuals right after it was made.
The only verification was `node --check` on the two edited JS files, both before
and after the edits, plus a static grep of the bundle. No harness, pytest or
headless browser was run, and tests/wh_mousebind_validation.py was never
touched or run. Nicko's playtest is the acceptance test.

## Port source

/tmp/wh-mousebindfeat does not exist in this container, so I ported from IO's
reference checkout instead. That is /workspace/witch-hunter on
feat/mouse-bind-cam, which I only read. The implementation sits there as an
uncommitted diff on 09712f6. Its built prototype/builds/v8-playable.html hashes
to sha256 a558e094...23b0 at 2,567,931 bytes, which matches the brief exactly.
So it is the same implementation the brief describes.

The patch did not apply cleanly, because feat/world-visuals had moved on:
inventory Order A, Order C handButton, and CONFIG growth. I ported it hunk by
hunk. A line-level diff of the source patch against the port shows only the
reconciliation lines listed below.

## What landed, per file

- **prototype/js/player.js** (+102 / -4)
  - `var MCFG = window.WH_CONFIG.mouse || {}` (line 12).
  - Constructor state `mouseBound` and `mouseChipEl`.
  - keydown: Backquote calls `toggleMouseBind()` (line 323).
  - mousedown: LMB returns early unless `e.target.id === 'wh-canvas'`
    (line 358). Next comes `handButton('lmb', true)`, which is Order C's LMB.
    The source called `tryAttack()` here, but the target routes LMB through
    handButton. After that, the auto-rebind runs, gated by
    `MCFG.autoBindOnCanvasClick`.
  - mousemove: the pointer-lock branch (line 394) multiplies
    `movementX/Y * pointerLockSensMult`, calls `applyCamDelta` and stamps
    `lastManualCamT`. The drag path is otherwise unchanged and now calls
    `applyCamDelta(dx, dy)`, whose math matches HEAD byte for byte.
  - A `pointerlockchange` listener calls `syncMouseChip`, which is the single
    source of truth. There is no Esc handler.
  - The chip click handler calls `toggleMouseBind`.
  - New prototypes: `applyCamDelta`, `bindMouse`, `unbindMouse`,
    `toggleMouseBind` and `syncMouseChip`. These are verbatim from the source,
    except for the label and the suspend guard.
  - `setInputSuspended` gains the overlay hook (line 495).
- **prototype/js/CONFIG.js** (+10, additive): `WH_CONFIG.mouse` at the root,
  between `player` and `spell`. No existing key was changed.
- **prototype/index.html** (+1): `<div id="wh-mouse-chip" title="Backquote
  toggles mouse bind">MOUSE: UNBOUND [`]</div>` inside #wh-hud, after
  #wh-lock-reticle.
- **prototype/style.css** (+17): the `#wh-mouse-chip` block, verbatim
  (bottom:14px right:16px, gothic palette, pointer-events:auto).
- **tools/build_v8.py** (new): build_v7.py with the v8 docstring, output path
  and title "Witch Hunter v8 - Mouse Bind Cam". It is byte-identical to the
  source branch's build_v8.py plus a trailing newline. build_v7.py is untouched.
- **prototype/builds/v8-playable.html**: built (see Build).

## CONFIG keys (WH_CONFIG.mouse)

| Key | Default | Effect |
|---|---|---|
| pointerLockSensMult | 0.85 | Multiplies the bound mouse against `player.mouseSensDegPerPx` (0.25), so bound sens = 0.2125 deg/px |
| autoBindOnCanvasClick | true | LMB on the game view while unbound fires the main-hand action AND re-binds |
| unbindOnUiOpen | true | NEW (reconcile). Opening the inventory screen unbinds a bound mouse so the screen is clickable |
| rebindOnUiClose | false | NEW (brief 1b knob). Closing the screen rebinds an unbound mouse |

## 1b - key collision: separate key, NO collision

The inventory opens with `KeyI` and closes with `KeyI` / `Escape`
(CONFIG.inventoryUI). The INV button is bottom-left. Nothing in the target
binds Backquote; a grep for Backquote, pointerLock and wh-mouse-chip came up
empty before the port.

The rebind knob was **implemented, not parked**. The overlay already exposes
its open and close moments cleanly. `InventoryUI.setOpen` calls
`onOpenChange(open)`, and game.js:965 forwards that to
`player.setInputSuspended(open)`, which lives in player.js. Both overlay hooks
therefore live in player.js, with no edits to inventory.js or game.js.

## 1c - chip position: no reposition needed

The chip stays at bottom:14px right:16px, because nothing from Order A sits at
the bottom-right:

- The INV button is at bottom-left (16 / 20).
- The belt is at bottom-center.
- #wh-toast is at bottom 70px, inside #wh-hud, so it is click-through and
  does not overlap.
- The touch layer (z 40) and its camera pad at (0.82, 0.72) stack above the
  chip and do not overlap it.

When the inventory modal is open it covers the whole screen (z 20), including
the chip. That is by design for a modal and is not a corner collision.

## Judgment calls

1. **Backquote runs ahead of the inventory input gate**, so it can always
   unbind. `bindMouse` refuses while the screen is open, so while the
   inventory is open Backquote can only unbind, never lock.
2. **unbindOnUiOpen (default true) is an addition the brief did not name.**
   Without it, pressing I while bound (the normal state with auto-bind) opens
   the screen under a hidden, locked cursor, which breaks AC F. Setting it to
   false restores the brief's literal behaviour.
3. **The bound-camera path is ignored while the screen is open.** This follows
   Order A's own rule that "camera input is ignored". It also covers the
   frames between `exitPointerLock()` and `pointerlockchange`. The drag path
   could not run there anyway, because suspend clears `dragging`.
4. Comments only: "free" became "unbound" in the three comments that name
   the bind state, and `initInput` became `bindInput` (the real function
   name). None of this changes the code.
5. The ported comments cite io/specs/mouse-bind-cam-spec.md. That spec is NOT
   on feat/world-visuals; it lives in IO's reference checkout. Law 7 freezes
   io/specs/, so I did not port it.
6. The bundle was built from a `git archive` snapshot of f3c2730 rather than
   the live tree. c10b0f9 (the C1 cooking brief) points another session at
   this same worktree, and the snapshot keeps any uncommitted edits from it
   out of v8. The live tree was clean at build time anyway.
7. `node` is not on PATH, so I used Playwright's bundled node runtime
   (/usr/local/lib/python3.12/site-packages/playwright/driver/node, v24.21.0)
   for `--check` only. No browser was launched.
8. This report is written in scratch/ even though law 7 freezes it, because
   ORDER A step 6 orders this file explicitly. It is a new file, and no
   existing scratch/ file was touched.

## Build

- `prototype/builds/v8-playable.html`: 2,705,871 bytes,
  **sha256 4e75f738e296b194ae2a70d3641822076dc27a4c60c742d3c633e95115cb28c8**.
- Title: "Witch Hunter v8 - Mouse Bind Cam".
- The static grep finds the chip markup `>MOUSE: UNBOUND [`]</div>`, the
  ternary `'MOUSE: BOUND [`]' : 'MOUSE: UNBOUND [`]'`, unbindOnUiOpen,
  rebindOnUiClose, the pointerlockchange listener and the Backquote handler.
  It finds 0 matches for `MOUSE: FREE` and 0 leftover `<script src=`.
- The hash differs from the source branch's v8 (a558e094...), as expected,
  because this build sits on world-visuals + inventory Order A.

## Acceptance criteria (playtest pending; traces are static)

| AC | Expected in play | Static trace |
|---|---|---|
| A mouse steers with no button held | Yes, once bound. The game boots UNBOUND, because browsers only grant pointer lock on a click or key press. One click on the game view, or a Backquote press, binds it. | bindMouse -> `#wh-canvas.requestPointerLock()` -> pointerlockchange -> `mouseBound = true`. mousemove then takes the pointer-lock branch -> `applyCamDelta(movement * 0.85)`. Pitch is clamped to -15..65. |
| B Backquote unbinds, cursor shows, HUD clicks do not attack | Yes | Backquote -> `unbindMouse` -> `exitPointerLock` -> pointerlockchange -> UNBOUND. A LMB whose target is not #wh-canvas returns before handButton. This covers the chip and the INV button; the INV button also swallows its own mousedown. Note that decorative HUD (bars, belt, FPS) is pointer-events:none, i.e. click-through, so a click there counts as a game-view click. |
| C Backquote or a canvas click rebinds; Esc unbinds | Yes | Backquote -> `bindMouse` (keydown counts as a user gesture). A canvas LMB while unbound -> handButton + `bindMouse` (autoBindOnCanvasClick). Esc is the browser's native lock exit, and pointerlockchange resyncs the chip. |
| D chip toggles, reads MOUSE: BOUND / MOUSE: UNBOUND | Yes, with one physical caveat | A chip click calls `toggleMouseBind`. While bound, the browser captures the OS cursor, so the chip cannot be clicked. Unbind with Backquote or Esc; the label updates on every lock change. |
| E WASD / attack / roll unchanged; touch unaffected | Yes | keydown only gains the Backquote line, and collectMoveInput, Space, F, Q, Digit and R/T are untouched. LMB on the canvas still calls `handButton('lmb', true)`. RMB, mouseup, wheel and contextmenu are untouched. touch-controls.js and CONFIG.touch are untouched, and the touch layer stacks above the chip. |
| F inventory opens and is clickable | Yes. I is its own key, with no collision. | I -> `setOpen(true)` -> `setInputSuspended(true)` -> `unbindMouse()`, so the cursor shows and the grid and tabs are clickable. Closing (I / Esc) leaves the mouse UNBOUND by default. Backquote, the chip or a game-view click then rebinds. |

## Playtest notes for Nicko

- **Touch (from the brief, 1d):** touch pad steering should be unaffected. If
  it is not, that is a real bug.
- **Re-lock after Esc:** browsers can refuse a re-lock right after an Esc
  exit. If that happens, the chip just stays UNBOUND; press Backquote or click
  again.
- **rebindOnUiClose = true:** closing with I rebinds. Closing with Esc may be
  refused by the browser, because Esc is not a user-gesture key, and the chip
  then stays UNBOUND.
- **Click-to-rebind also swings,** by design ("attack + rebind"). Set
  `autoBindOnCanvasClick: false` to rebind only with Backquote or the chip.
- **Sudden camera snap:** if the camera ever snaps on the first move after
  binding, report it. Some browser/OS setups spike movementX/Y on lock, and a
  per-event clamp knob would be a small follow-up.

## Not done / parked

- Nothing from ORDER A is parked.
- Order B scope was not touched.
- Repointing the WebUI playtest button to v8 is IO's step (spec gate 4) and
  was not done.
- I did not touch the 8793 host container or the host's /tmp checkouts.
- Coordination: the C1 cooking brief (c10b0f9) tells that session to STOP and
  report if the feat tip moved outside io/missions. These commits move it
  (prototype/, tools/), so expect that report.
