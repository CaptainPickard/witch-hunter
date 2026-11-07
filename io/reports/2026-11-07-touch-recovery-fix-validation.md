# Validation Report — TC-FIX-V Touch Layer Recovery Fixes

Testerbot · 2026-11-07 · valspec: io/specs/touch-recovery-fix-valspec.md · base 933d024
Method: static review + `git diff 933d024` + node arithmetic sim (io/scratch/clamp-sim.js). No commit made.

## Verdict: **PASS** — 0 blocking, 0 non-blocking findings

## Pre-flight
- P1 PASS — HEAD = 933d024 ("build: v8 bundle (worktree) - CC-WB3 strata board stamp"); status = M×2 + untracked io/specs/* + io/scratch/clamp-sim.js only. No child committed.
- P2 PASS — `git diff 933d024 --stat`:
  `prototype/js/journal.js | 7 ++++`, `prototype/js/touch-controls.js | 82 +++++...---`
  2 files changed, 81 insertions(+), 8 deletions(-). No third path (matches Devbot claim exactly).

## V1 — Drag clamp (F1, A1): ALL PASS
- V1.1 PASS — :523 `var x = clamp(ev.clientX - dragOffX, 0, window.innerWidth - r.width);` exact bounds 0 / innerWidth−r.width.
- V1.2 PASS — :524 `var y = clamp(ev.clientY - dragOffY, 0, window.innerHeight - r.height);`.
- V1.3 PASS — :518 `var r = c.el.getBoundingClientRect();` inside moveDrag (fresh layout each move; startDrag's rect is only used for the grab offset).
- V1.4 PASS — :525-526 writes `(x / window.innerWidth * 100) + '%'` and `(y / window.innerHeight * 100) + '%'` (diff shows those lines untouched — only clamp bounds changed).
- V1.5 PASS — grep `r.width / 2` matches only :558-559 in stickBegin (unrelated stick origin, unchanged from base). Zero center-bias in moveDrag (diff: `+ r.width / 2` / `+ r.height / 2` removed).
- V1.6 PASS — node sim (clamp-sim.js): raw x=1150 w=120 W=1280 → leftPx 1150, right edge 1270 ≤ 1280 fully visible; raw x=1260 → clamped 1160, right edge exactly 1280; invariant sweep x∈[−50,1400] ⇒ 0 ≤ leftPx and leftPx+w ≤ W for ALL raw x (vertical sweep same). Persisted 90.625% re-reads to exactly 1160 px.
- V1.7 PASS (advisory) — old "keep control CENTER…" comment replaced by "TC-FIX1 (RC1): clamp the placed TOP-LEFT point so the FULL element stays inside the viewport" (:519-522).

## V2 — Saved-state sanitation (F3, A4, A2): ALL PASS
- V2.1 PASS — buildControls: :243 `if (savedState) applySavedState(savedState);` → :244 `applyScale();` → :245 `sanitizeLayout();` → later shown via init(:758)→show(:291)→buildControls. Transitively after saved state.
- V2.2 PASS — sanitizeLayout (:730-743) iterates `order` (all 8: stick,cam,sprint,attack,lockon,dodge,block,interact :29) with only a `if (!c) return;` guard; uses `var rect = c.el.getBoundingClientRect();` (:736) and clamps into `[0, window.innerWidth - rect.width]` / `[0, window.innerHeight - rect.height]` (:737-738).
- V2.3 PASS — :739-740 writes `(leftPx / window.innerWidth * 100) + '%'` — same px/viewport*100 form as moveDrag; saveState reads positions back through the same fracX/fracY, so no unit mismatch.
- V2.4 PASS — node sim: stale fx=0.98 → leftPx 1254.4 on W=1280 w=120 (right edge 1374.4 OFF-SCREEN) → sanitized to 1160 (right edge 1280, fully visible); valspec's W=900 w=100 case: 882 (edge 982 > 900) → 800 (edge 900). Roundtrip %→px exact; idempotent (second pass = no-op).
- V2.5 PASS — applySavedState (:706-720, incl. `clamp(pos.x,0,1)*100+'%'`), loadState (:65-73), saveState (:74-82), fracX/fracY (:50-63) all byte-identical to base: diff hunks only at @@242, @@331, @@365, @@476, @@676. None touch those bodies.
- V2.6 PASS — sanitation runs after `applyScale()` (:244), which sets explicit per-element px width/height (:427-437), so getBoundingClientRect reports real sizes when clamps compute. Scripts load at body end (documented :767-769).

## V3 — Edit-bar pointerdown activation (F2, A3, RC2): ALL PASS
- V3.1 PASS — all five buttons bind pointerdown invoking the same action the old click ran: minus→nudgeScale(−0.1) :340-344; plus→nudgeScale(+0.1) :353-357; lock→unlocked toggle + glyph + amber + saveState-on-lock :367-375 (body 1:1 with old click body); Reset→scale reset + defaults + applyScale + saveState :384-397; Done→unlocked=false + setEditMode(false) + saveState :406-413.
- V3.2 PASS — each also has a swallow-only click listener (body = preventDefault+stopPropagation, no action): :345-348, :358-361, :376-379, :398-401, :414-417.
- V3.3 PASS — every pointerdown handler begins with `ev.preventDefault(); ev.stopPropagation();` — same shape as the 10-03 buildToggle fix (:195-199).
- V3.4 PASS — title/tooltip attributes untouched; lock handler preserves glyph transition and `classList.toggle('amber', unlocked)`.
- V3.5 PASS — buildToggle (:182-208) and buildLockChip (:258-281) hunks absent from the diff (touch-controls hunks are @@242, @@331(buildEditBar), @@365, @@476, @@676 — none in/around :190-207 or :264-279).
- V3.6 PASS — bindControl (:440-498) has zero diff hunks; no new click-activation there.

## Double-activation hazard (RC2 corollary): PASS
Sweep `addEventListener('click'` in touch-controls.js → 7 hits (:204 toggle, :277 lockchip, :345/:358/:376/:398/:414 edit-bar); every body is swallow-only (preventDefault+stopPropagation, no action call). Actions run exclusively in pointerdown → exactly one activation per pointer gesture.

## V4 — Journal search focus (F4, A5): ALL PASS
- V4.1 PASS — journal.js :191-193 `searchEl.addEventListener('pointerdown', function () { searchEl.focus({ preventScroll: true }); });` (preventScroll present).
- V4.2 PASS — handler body has no preventDefault (and no stopPropagation) — default focus path unobstructed.
- V4.3 PASS — journal.js diff is a single hunk @@ -184,6 +184,13 (insertion only between the `input` listener and `searchWrap.appendChild`); keydown guard :203-214 (openKey/inSearch check + Escape→closePanel) byte-identical.
- V4.4 PASS — `input` binding :183-186 outside the single hunk, untouched.
- V4.5 PASS — journal btn bindings :159-169 (pointerdown→openPanel + mousedown/click/contextmenu swallow) untouched — no new preventDefault starvation vector.

## V5 — Syntax gates (A6): ALL PASS
- V5.1 PASS — `node --check prototype/js/touch-controls.js` exit 0.
- V5.2 PASS — `node --check prototype/js/journal.js` exit 0.
- V5.3 PASS — click sweep above: zero click listeners invoke actions on the edit bar (all swallow-only); pre-existing toggle/lockchip swallows intact; journal.js has no new click listeners.

## V6 — Scope wall (A7): ALL PASS
- V6.1 PASS — diff --stat lists only the two permitted files.
- V6.2 PASS — status shows only those 2 modified + untracked io/specs/* and io/scratch/clamp-sim.js (validation artifacts, untracked).
- V6.3 PASS — prototype/index.html: `js/journal.js` :72, `js/touch-controls.js` :74, untouched (0-line diff); ids `#wh-touch-toggle` / `#wh-touch-editbar` / `#wh-touch-lockchip` / `#wh-journal-search` all still assigned (:186/:329/:261/:180 journal:180).

## Gate summary
V1.1-V1.6 ✓ · V2.1-V2.6 ✓ · V3.1-V3.6 ✓ · V4.1-V4.5 ✓ · V5.1-V5.3 ✓ · V6.1-V6.3 ✓ · V1.7 ✓ (advisory met)
**Result: PASS (0 blocking, 0 non-blocking). All 31 checks green. No deviations from spec.**
