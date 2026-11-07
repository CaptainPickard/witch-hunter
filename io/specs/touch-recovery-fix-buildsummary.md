# Devbot Build Summary — TC-FIX1 Touch Layer Recovery Fixes

- Builder: Devbot · 2026-11-07 · Validates io/specs/touch-recovery-fix-spec.md (F1–F4, A1–A7)
- Worktree: /tmp/wh-touchfix · branch feat/touch-controls-fix · base 933d024 (HEAD unchanged, NO-GIT honored)
- Files changed (ONLY these two): prototype/js/touch-controls.js, prototype/js/journal.js
- Line numbers below are FINAL post-edit files (grep line refs included for Testerbot).

## F1 — moveDrag FULL-element clamp (RC1). Final lines 512–526.

In `moveDrag` (was base :480–481, now :523–524):

- `var r = c.el.getBoundingClientRect();` refreshed per move at :518 (fresh layout — V1.3 pass).
- Horizontal clamp: `var x = clamp(ev.clientX - dragOffX, 0, window.innerWidth - r.width);` (:523).
- Vertical clamp: `var y = clamp(ev.clientY - dragOffY, 0, window.innerHeight - r.height);` (:524).
- Percent write unchanged: `c.el.style.left = (x / window.innerWidth * 100) + '%';` (:525), top analog (:526) — V1.4 pass.
- Center-bias tokens `r.width / 2` / `r.height / 2` fully removed from moveDrag (V1.5 pass, zero awk matches).
- RC1 "keep control CENTER inside the viewport" comment replaced with FULL-element wording (:519–522) — V1.7 advisory pass.
- Off-viewport impossibility: verified by simulation — drag targets (2000,1500), (−500,−500), (450,200), (899,399) for a 100×100 box in 900×400 viewport all yield leftPx∈[0, W−w], topPx∈[0, H−h] (max rightEdge = 900 = W).

## F2 — Edit-bar bar pointerdown activation + click swallow (RC2). buildEditBar, final lines 332–418.

Five buttons rebuilt to the proven buildToggle (:195–207) pattern — pointerdown activates with
`ev.preventDefault(); ev.stopPropagation();` then the SAME action body as the old click handler 1:1;
a `click` listener whose body is ONLY swallow (`preventDefault` + `stopPropagation`, no action call):

| Button | pointerdown (action) | click (swallow only) |
|---|---|---|
| minus | :340–344 → `nudgeScale(-0.1)` | :345–348 |
| plus | :353–357 → `nudgeScale(0.1)` | :358–361 |
| lock | :367–375 → toggle unlocked/glyph/amber/save | :376–379 |
| Reset | :384–396 → scale default + loop + applyScale + saveState | :398–401 |
| Done | :406–412 → unlock off + setEditMode(false) + saveState | :414–417 |

- V3.1 pass (5 pointerdown actions), V3.2 pass (5 swallow-only clicks; sweep below), V3.3 pass (each pointerdown begins with preventDefault), V3.4 pass (action bodies 1:1 with base; titles/keyboard untouched; lock keeps glyph+amber transitions).
- V3.5 pass: buildToggle (:195–207) and buildLockChip (:271–279) hunks absent from diff.
- V3.6 pass: bindControl untouched (no hunk in its region of the diff).

## F3 — Init-time sanitation of stale layouts (A4, A2). Final lines 711–744, wired at :245.

- New `sanitizeLayout()` at :730–743, called in buildControls at :245 — ORDER: `applySavedState(savedState)` (:243) → `applyScale()` (:244) → `sanitizeLayout()` (:245), so sizes exist before clamps (V2.6 pass) and the pass is transitively after applied saved state on the init → show → buildControls path (V2.1 pass).
- Per-control (all 8 in `order`, only a missing-`c` guard skips; V2.2 pass):
  - reads the saved fraction back via existing `fracX`/`fracY` (:733–734),
  - refreshes `rect = c.el.getBoundingClientRect()` (:736),
  - clamps in PIXELS: `leftPx = clamp(fx * window.innerWidth, 0, window.innerWidth - rect.width)` (:737), top analog(:738),
  - rewrites the same '%' fraction form: `(leftPx / window.innerWidth * 100) + '%'` (:739–740) — re-readable by fracX/fracY, no unit mismatch (V2.3 pass).
- `saveState()` at :742 persists the repaired layout immediately.
- V2.5 pass: `applySavedState` still clamps fractions to [0,1] (:672–673 intact); `loadState`/`saveState`/`fracX`/`fracY` bodies untouched by the diff.
- Legacy-state repair verified by simulation: stale x=0.98/y=0.97 for a 100×100 control on 900×400 becomes leftPx=800/topPx=300 → rightEdge 900 ≤ W, bottomEdge 400 ≤ H; round-trip fraction 0.8889 re-reads identically. No manual localStorage wipe needed (V2.4 pass).

## F4 — Journal search pointerdown focus (A5). prototype/js/journal.js, final lines 188–194.

- Added (diff's single journal hunk, insertion after the input listener at base :183–186):
  `searchEl.addEventListener('pointerdown', function () { searchEl.focus({ preventScroll: true }); });` (:191–193).
- NO preventDefault in the handler (V4.2 pass) — default focus path still runs.
- V4.3 pass: keydown guard block (base :196–207, `CFG.openKey` + `inSearch` + Escape → closePanel) byte-identical — the diff hunk (@@ −184,6 +184,13) carries none of those lines.
- V4.4 pass: `input` binding (:183–186, now :190–193 region context) unchanged.
- V4.5 pass: journal btn bindings (base :159–170) untouched — no diff hunk there.

## Gate outputs

```
$ node --check prototype/js/touch-controls.js   (exit 0)
$ node --check prototype/js/journal.js          (exit 0)
  -> both exit 0 under node v22.23.4; "SYNTAX OK"

$ git diff 933d024 --stat
 prototype/js/journal.js        |  7 ++++
 prototype/js/touch-controls.js | 82 +++++++++++++++++++++++++++++++++++++-----
 2 files changed, 81 insertions(+), 8 deletions(-)
  -> ONLY the two permitted files (io/specs/* untracked, not in --stat); V6.1/V6.2 pass.
     `git status --short`: only the two M files + untracked io/specs/*. No third path. V6 pass.

V5.3 click sweep — `grep -n "addEventListener('click'" prototype/js/touch-controls.js`:
 :204 (toggle), :277 (lock chip) - pre-existing 10-03 swallow-only, untouched
 :345 :358 :376 :398 :414 (minus/plus/lock/reset/done) - new swallow-only bodies
 => zero click listeners invoke an action; V5.3 clean.

V6.3 — #wh-touch-toggle / #wh-touch-editbar / #wh-touch-lockchip / #wh-journal-search ids unchanged; both scripts untouched in index.html load order.
```

## Diff hunk inventory (V3.5/V3.6 region proof)

touch-controls.js hunks (all in permitted regions):
- @@ −242,6 +242,7 @@ — buildControls tail: sanitizeLayout() call added
- @@ −331,29 +332,58 @@ — buildEditBar: minus + plus rebuilt
- @@ −365,16 +395,26 @@ — buildEditBar: lock + reset rebuilt
- @@ −476,9 +516,12 @@ — moveDrag: F1 clamp
- @@ −676,6 +719,29 @@ — sanitizeLayout() function added after applySavedState
journal.js hunks: exactly one — @@ −184,6 +184,13 @@ (pointerdown focus insert; keydown/input/btn regions untouched)

## A1–A7 checklist

- [x] A1 PASS — moveDrag clamps the placed top-left into [0, innerWidth − rect.width] × [0, innerHeight − rect.height] (:523–524); full-element containment math verified by simulation (V1.1–V1.6).
- [x] A2 PASS — drag-end state originates only from the F1 clamp; even a stale fraction is clamped again at init by F3 with fresh rects before any save (V2.2–V2.4; round-trip verified). Off-screen save/render impossible in either path.
- [x] A3 PASS — all five edit-bar buttons act on pointerdown (:340/:353/:367/:384/:406) and desktop mouse fires the same pointerdown once; every synthetic click is swallow-only (V3.1–V3.5, V5.3).
- [x] A4 PASS — sanitizeLayout (:730) runs at init after applySavedState + applyScale, clamps all 8 controls in px with getBoundingClientRect, and persists via saveState() (:742); stale 0.98-fraction save verified repaired by simulation.
- [x] A5 PASS — journal search pointerdown → focus({preventScroll:true}) with no preventDefault (:191–193); keydown guards byte-identical (V4.1–V4.3).
- [x] A6 PASS — `node --check` exit 0 on both files (V5.1/V5.2); click sweep clean (V5.3).
- [x] A7 PASS — `git diff 933d024 --stat` lists ONLY prototype/js/touch-controls.js and prototype/js/journal.js (V6.1–V6.3); NO-GIT honored: HEAD still 933d024, nothing committed or pushed.

## Known limitations (none blocking)

- sanitizeLayout relies on layout being settled when buildControls first runs (scripts load at body end, applyScale sets px sizes synchronously first — V2.6 ordering satisfied). Fonts that change glyph metrics after load cannot shrink a control; sizes here are px-fixed, so this is not a risk in practice.
- V1.7 comment-hygiene and all V-checks pass; no FAIL lines expected from Testerbot.
