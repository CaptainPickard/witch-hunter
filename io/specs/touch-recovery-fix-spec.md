# IO SPEC — Touch Layer Recovery Fixes (TC-FIX1)

- Repo: witch-hunter, branch feat/touch-controls-fix (worktree /tmp/wh-touchfix), base 933d024
- Author: IO · 2026-11-07 · Gate: Testerbot valspec -> Devbot -> Testerbot -> IO commit
- Scope walls: ONLY prototype/js/touch-controls.js + prototype/js/journal.js.
  NO edits to CONFIG.js, game.js, player.js, style.css, index.html, builds/*.
  NO-GIT for all children. No harness runs, no headless browser smoke.

## Nicko bug reports (2026-11-07, playtest on phone)

B1: Editing button placement lets buttons shift completely off screen;
    state persists in localStorage; only wiping the saved layout recovers.
B2: The touch UI becomes unresponsive (edit bar / buttons ignore taps),
    requiring a page reload to recover.

## Root causes (IO analysis)

RC1 (B1): moveDrag() clamps the control CENTER to [0, viewport] but writes
that clamped center into style.left/top, which position the element's
TOP-LEFT corner. A control can therefore sit up to a full (width-1) px
off the right/bottom edge. endDrag() persists the bad position
immediately -> reload restores the same off-screen state.
RC2 (B2): Edit-bar buttons (lock/reset/done, +/-) bind 'click' only.
On Nicko's device the 10-03 fix proved click is unreliable for these
round div buttons (pointerdown + preventDefault kills synthetic click);
toggle + lock chip were fixed on 10-03 but the edit bar was missed.
User gets stuck: edit bar buttons unresponsive; if locked placement plus
off-screen controls -> unrecoverable without reset.

## Fixes REQUIRED

F1 (touch-controls.js): drag math must clamp the TOP-LEFT/positioned point
so the FULL element stays inside the viewport:
  left = clamp(pointerX - dragOffX, 0, innerWidth - rect.width) / innerWidth
  top  = clamp(pointerY - dragOffY, 0, innerHeight - rect.height) / innerHeight
(centering offset already included via dragOff from getBoundingClientRect).
F2 (touch-controls.js): edit-bar buttons + toggle + lock chip use pointerdown
for activation (same proven 10-03 pattern: pointerdown activates, then a
'click' listener swallows the synthetic click). Keep mouse working.
F3 (touch-controls.js): load-time sanitation — at init, after applying saved
state, clamp each control fully inside the viewport (top-left >= 0 px,
bottom-right <= innerWidth/innerHeight). Repairs Nicko's existing
localStorage without a manual wipe.
F4 (journal.js): on the search input, add pointerdown (not prevented) that
calls searchEl.focus({preventScroll:true}) so the virtual keyboard opens
on touch devices reliably (input currently relies on default focus path,
which the layer's global stopPropagation noise can starve).
NOTE: keep search keydown guard + Escape behaviors byte-identical.

## Acceptance criteria

A1: moveDrag keeps every control fully on-screen during drag (no px
    outside viewport at any drag position; verify math + code).
A2: Layout state after drag-end can never contain x/y that render
    partially off-screen (check saveState round-trip through loadState
    + F3 clamp).
A3: Every edit-bar button responds on pointerdown AND on desktop click;
    no double-activation (click swallowed).
A4: Stale saved state with an off-screen control is auto-repaired at
    init; after repair all controls fully visible.
A5: journal search focus path calls .focus() on pointerdown; keyboard
    opens on touch; existing keydown guards unchanged.
A6: node --check passes on both files; grep shows no leftover 'click'
    activation on edit-bar buttons without its swallow.
A7: Zero diff outside the two permitted files.
