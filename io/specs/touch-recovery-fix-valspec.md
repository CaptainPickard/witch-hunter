# VALSPEC TC-FIX-V — Independent Validation for Touch Layer Recovery Fixes

- Validator: Testerbot · 2026-11-07 · Validates io/specs/touch-recovery-fix-spec.md (A1–A7, F1–F4)
- Repo: witch-hunter worktree /tmp/wh-touchfix · branch feat/touch-controls-fix · base 933d024
- Files under test (ONLY these two may differ from base):
  - prototype/js/touch-controls.js
  - prototype/js/journal.js
- Method: static/diff review only (no browser, no harness). Every check states the
  mechanical command or grep that decides PASS/FAIL. Fix is implemented by Devbot; this
  spec is run BY Testerbot AFTER Devbot commits nothing (children NO-GIT — diff is
  working-tree `git diff 933d024 -- ...`).

Pre-flight (P):
- P1 `git -C /tmp/wh-touchfix rev-parse HEAD` == 933d024... and `git status --short` shows
  only `?? io/specs/*` (untracked spec files). No child has committed.
- P2 `git -C /tmp/wh-touchfix diff 933d024 --stat` file list ⊆ {prototype/js/touch-controls.js,
  prototype/js/journal.js, io/specs/*}. Any other path -> FAIL (A7, see V6).

---

## V1 — Drag clamp keeps the FULL element inside the viewport (F1, A1)

Derivation. Positioning is `position:fixed` with `style.left/top` placing the element's
TOP-LEFT corner. Pointer down records `dragOffX = clientX - r.left`,
`dragOffY = clientY - r.top` (startDrag). To keep the full box visible for any element of
size (w,h) in viewport (W,H), the placed top-left point (px) must satisfy:

  leftPx = clamp(ev.clientX - dragOffX, 0, W - w)
  topPx  = clamp(ev.clientY - dragOffY, 0, H - h)
  then written as fractions: leftPx/W*100, topPx/H*100.

(Fraction denominators stay W/H exactly as before; the clamp bounds change is the fix.
NOT acceptable: any residual `+ r.width/2` or `+ r.height/2` center-bias inside the
clamped value — that is the RC1 bug.)

Checks (each mechanically verifiable from `git diff 933d024 -- prototype/js/touch-controls.js`
or the working file):

- V1.1 In `moveDrag`, the horizontal clamp is
  `clamp(ev.clientX - dragOffX, 0, window.innerWidth - r.width)` — exact lower bound `0`,
  exact upper bound `innerWidth - rect.width`. Grep: line contains
  `innerWidth - r.width` inside moveDrag's clamp call. PASS iff present.
- V1.2 In `moveDrag`, the vertical clamp is
  `clamp(ev.clientY - dragOffY, 0, window.innerHeight - r.height)`.
  Grep: `innerHeight - r.height` inside moveDrag. PASS iff present.
- V1.3 `r` is obtained from `controls[dragName].el.getBoundingClientRect()` in moveDrag
  (fresh layout each move, matching the element actually being moved). PASS iff the
  clamp operands reference an `r.width`/`r.height` that is assigned in moveDrag (or
  re-fetched) — not a stale rect from startDrag.
- V1.4 The written CSS is still a PERCENT of viewport: moveDrag ends with
  `c.el.style.left = (x / window.innerWidth * 100) + '%'` and the matching `'%'` top.
  The only changed tokens are the clamp bounds. PASS iff fraction denominators are
  window.innerWidth / window.innerHeight (unchanged shape).
- V1.5 NO center-bias remains: grep moveDrag for `r.width / 2` and `r.height / 2` —
  PASS iff zero matches inside moveDrag (comment text mentioning "center" that was
  removed is fine; live code must be clean).
- V1.6 Off-viewport impossibility (derived, read-only arithmetic): with V1.1/V1.2 held,
  min leftPx = 0 ≥ 0 and max leftPx = W − w ⇒ leftPx + w ≤ W. Top/height by symmetry.
  So at every drag position: 0 ≤ leftPx and leftPx + w ≤ W, 0 ≤ topPx and topPx + h ≤ H.
  PASS iff formulas above are those of the implementation (V1.1–V1.4 all pass).
- V1.7 Comment hygiene: the RC1 comment "keep control CENTER inside the viewport" is
  replaced (e.g. by a "FULL element" wording). Non-blocking nit; PASS not required for gate.

## V2 — Saved-state sanitation at init (F3, A4, A2)

Context: buildControls applies `applySavedState(savedState)` then `applyScale()`;
init() → show() path. Saved x/y are viewport FRACTIONS; element size is px. A fraction in
[0,1] alone cannot guarantee full visibility (RC1 legacy state), so repair must use the
rendered rect.

Checks:

- V2.1 A sanitation pass exists that runs at init AFTER saved state is applied:
  reachable on the init → (show →) buildControls → applySavedState → applyScale path
  (or equivalently re-invoked after applySavedState in buildControls). PASS iff the
  clamp call is transitively after `applySavedState(savedState)` in buildControls.
- V2.2 For EVERY entry in `order` (all 8: stick/cam/sprint/attack/lockon/dodge/block/
  interact), the pass clamps the element fully inside the viewport using its rect:
  `left = clamp(leftPx, 0, window.innerWidth - rect.width)`,
  `top = clamp(topPx, 0, window.innerHeight - rect.height)` (in px, then re-written to
  the '%' form). Grep shows `getBoundingClientRect()` used in the sanitation function
  and both clamp bounds `innerWidth - rect.width` / `innerHeight - rect.height`.
  PASS iff present and applied per-control (no skip except a missing `c` guard).
- V2.3 The written position uses the same fraction conversion as moveDrag
  (px / viewport * 100 + '%'); grep the sanitation function for `'* 100'` (or 100)
  with innerWidth/innerHeight denominators. PASS iff the state written can be re-read
  by fracX/fracY without unit mismatch.
- V2.4 Legacy-state impossibility: a stale save whose stored fraction renders
  partially off-screen (e.g. x=0.98 with w=100 on W=900 ⇒ leftPx 882, right edge 982 > 900)
  is, after init, clamped to leftPx ≤ W − w ⇒ fully visible. Verified by reading the
  call chain (V2.1–V2.3). No manual wipe needed. PASS iff chain complete.
- V2.5 Existing behavior preserved: `applySavedState` still clamps fractions to [0,1]
  before applying (clamp(pos.x,0,1) lines untouched); sanitation is ADDED, not a
  rewrite of loadState/saveState. `saveState`/`loadState`/`fracX`/`fracY` bodies are
  UNCHANGED in the diff. PASS iff `git diff 933d024` shows no hunk touching those
  function bodies (additions in nearby regions are fine).
- V2.6 The sanitation is idempotent/safe before layout: if it uses getBoundingClientRect
  at init time (scripts load at body end), elements must already have their size applied
  (applyScale runs before sanitation, or sanitation itself sets width/height first).
  PASS iff ordering guarantees widths exist before clamps are computed — check the
  function order inside buildControls/init.

## V3 — Edit-bar pointerdown activation, no double-fire (F2, A3, RC2)

Targets: the five edit-bar buttons minus(−), plus(+), lock, Reset, Done in
`buildEditBar` (:331–377 at base). Also confirm the already-fixed 10-03 widgets
(toggle, lock chip) keep their pointerdown+swallow pattern intact.

Checks (grep-driven, work against both the diff and final file):

- V3.1 For each of the five buttons, a `pointerdown` listener exists that invokes the
  SAME action the old click listener ran (nudgeScale(∓0.1) / unlock toggle / reset / done).
  Mechanical: grep buildEditBar for `addEventListener('pointerdown'` with the five
  handler bodies adjacent. PASS iff all five act on pointerdown.
- V3.2 Each five buttons also has a `click` listener that ONLY swallows:
  body is `ev.preventDefault(); ev.stopPropagation();` (no action call).
  PASS iff no edit-bar click listener still invokes an action function (no double-fire).
- V3.3 The pointerdown handler prevents the synthetic click at the source by calling
  ev.preventDefault() (+ stopPropagation) — same shape as the 10-03 toggle fix at
  :195–207. PASS iff each pointerdown begins with preventDefault.
- V3.4 Keep mouse working: the swallowing click listener must not remove keyboard
  access or title/tooltip; the lock button still toggles its glyph/amber class inside
  the pointerdown action (state transitions preserved). PASS iff handler body matches
  the old click body 1:1 (actions unchanged, only the event moved).
- V3.5 Toggle (`buildToggle`) and lock chip (`buildLockChip`) pointerdown+swallow
  listeners are byte-identical to base (no regression): diff hunks must not touch
  :190–207 or :264–279. PASS iff `git diff 933d024 -- prototype/js/touch-controls.js`
  has no hunk inside those ranges.
- V3.6 Control buttons (the round .wh-touch-ctl divs) — their pointerdown/pointerup
  bindings (:400–457) are unchanged: no new click-activation paths added there either.
  PASS iff no diff hunk inside bindControl.

## V4 — Journal search pointerdown focus + guards untouched (F4, A5)

File: prototype/js/journal.js. Baseline facts at base: search input binds only
`input` (:183); keydown guard block :196–207 handles `CFG.openKey` (with
`inSearch = document.activeElement === searchEl`) and `Escape` → closePanel.

Checks:

- V4.1 A `pointerdown` listener is added to `searchEl` whose body calls
  `searchEl.focus({ preventScroll: true })` (must include preventScroll option).
  PASS iff grep finds `searchEl.addEventListener('pointerdown'` and within its body
  the `.focus(` call contains `preventScroll`.
- V4.2 That pointerdown handler does NOT call `e.preventDefault()` (F4 explicitly
  not-prevented so the default focus path still runs). PASS iff handler body lacks
  preventDefault (stopPropagation is also acceptable-free: both absence and
  stopPropagation-only pass; only preventDefault is the fail condition).
- V4.3 Keydown guard block byte-identical: `git diff 933d024 -- prototype/js/journal.js`
  has NO hunk inside :196–207. PASS iff the block (lines from
  `document.addEventListener('keydown'` through the Escape closedPanel/preventDefault
  lines) is untouched.
- V4.4 `input` binding (:183–186) byte-identical. PASS iff diff shows no hunk there.
- V4.5 No new preventDefault introduced on the journal button or panel that could
  starve search focus: journal btn bindings (:159–170) untouched. PASS iff no hunk
  at those lines.

## V5 — Syntax gates (A6)

- V5.1 `node --check prototype/js/touch-controls.js` → exit 0. PASS iff exit 0.
- V5.2 `node --check prototype/js/journal.js` → exit 0. PASS iff exit 0.
- V5.3 Leftover click-activation sweep (A6): grep
  `grep -n "addEventListener('click'" prototype/js/touch-controls.js`
  → every hit is a swallow-only body (V3.2) or the pre-existing control-guard
  swallow; zero clicks that invoke actions on edit-bar. PASS iff clean.
  (journal.js: journal btn's click swallow is pre-existing and untouched — V4.5.)

## V6 — Scope wall (A7)

- V6.1 `git -C /tmp/wh-touchfix diff 933d024 --stat` output lines list ONLY
  prototype/js/touch-controls.js and prototype/js/journal.js (plus untracked io/specs/*).
  Any third tracked path, or any builds/*, index.html, style.css, CONFIG.js, game.js,
  player.js, camp.js, npc.js change → FAIL.
- V6.2 `git -C /tmp/wh-touchfix status --short` contains no modifications outside the
  two permitted files (untracked io/specs/* allowed).
- V6.3 Both files still load in order in index.html (untouched file); no DOM/id
  renames: grep final touch-controls.js for `#wh-touch-toggle`, `#wh-touch-editbar`,
  `#wh-touch-lockchip` ids unchanged; journal.js keeps `#wh-journal-search`.

---

## PASS gates

Gate = ALL of: V1.1–V1.6, V2.1–V2.6, V3.1–V3.6, V4.1–V4.5, V5.1–V5.3, V6.1–V6.3.
V1.7 is advisory. Result record: per-check PASS/FAIL lines + files-read commands used.
On any FAIL → send back to Devbot with the failing V-id; no IO commit before all green.
