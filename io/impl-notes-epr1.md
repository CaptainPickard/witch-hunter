# EPR1 "ER-Parity Combat Values" - implementation notes (F1)

Devbot (Claude Code, opus), 2026-10-06. Worktree /workspace/wh-erparity-test at
0c72f53 (= io/epr1-contract; prototype/ identical to origin/dev b94a35c). Contract:
io/specs/devbot-spec-wh-erparity-combat.md (EPR1-A1..A7) + IO dispatch addendum
2026-10-06. Changed: prototype/js/CONFIG.js, prototype/js/player.js, this file;
game.js / anim.js / enemy.js / touch-controls.js / assets untouched. Line refs
are post-patch.

Session limits: Edit/Write were denied in the Devbot session, so code and notes
shipped as an unapplied, unrun patch. The valspec, harness source and pre-build
logs were unreadable (outside the worktree; io/epr1-contract carries only the
impl spec). The harness contract was read from the compiled
scratch/erparity/__pycache__/wh_erparity_validation.cpython-312.pyc (source
mtime 2026-10-06 17:15 UTC). Section 11 verdicts are predictions, not a run.

## 1. AMENDED-BY-IO REQUIRED

1. bufferFrom vs harness press timing (B2, B5, C1/C2). Shipped per impl spec 3.2 /
   B5: an LMB in windup is ignored before bufferFrom x windup and buffered from it
   (0.5 -> slashR2L 0.285 s, slashL2R 0.40 s, thrust 0.20 s). The harness
   BUFFERED-PRESS probes press LMB early in windup: B2 right after
   wait_for_stage(windup) (elapsed ~0.00 s), B5 400 ms wall later, C1's third LMB
   300 ms wall into slashL2R windup. At 2-11 headless fps that is 0.00-0.22 s of
   sim, before bufferFrom, so the press is correctly ignored: B2/B5 never chain and
   C1 never reaches the thrust ("insufficient samples": C1 fails, C2 is never
   evaluated, although the slashR2L root motion meets the C1 bars). Options:
   (a) harness: wait_elapsed_at_least(page, MOVES[m]['buffer_from']) before each
   windup LMB; (b) DESIGN data: bufferFrom: 0 on the three longsword moves (no
   code change; makes B5's "ignored before bufferFrom" clause vacuous).
2. B1e never equips the shield. RMB routes by offhand (v7) and the boot loadout is
   spell, so B1e's RMB is a refused cast and no blocking row can appear; blocking
   with the spell offhand would break D1 / EPR1-A7. Harness fix: KeyQ, wait for
   offhand === 'shield' (as D1 does), then swing. The guard column is implemented
   on the shield route.
3. F1 file name. Dispatch: io/impl-notes-epr1.md; impl spec F1 and the harness
   F1 / E3 allow-list: io/erparity-impl-notes.md. This file follows the impl spec
   (precedence); a rename needs the harness allow-list updated too.
4. Amendment record. Impl spec section 0 files requests in
   scratch/erparity-amendments.md; the dispatch forbids scratch/ and asks for them
   here, so they live here only (F2 is informational in the harness).

## 2. Frame conversions (game clock 1 / maxDt = 20 Hz, 0.05 s per frame)

| gate | s | frames | as shipped |
|---|---|---|---|
| Space tap / hold split | 0.35 | 7 | integer ms: each sampled frame adds round(dt*1000) = 50; >= 350 = sprint (7 frames, inclusive) |
| guard raise -> blockActive | 0.13 | 2.6 | float timer; active on the 3rd frame after accept |
| roll i-frames | 0.433 | 8.66 | 9 rows with iframes > 0 from the roll's first frame |
| roll | 0.45 | 9 | unchanged |
| backstep / its i-frames | 0.30 / 0.20 | 6 / 4 | float timers |
| parry window | 0.25 | 5 | from accept (unchanged); usable once blockActive, ~2 frames |
| inputBufferSec | 0.65 | 13 | from the press; a windup-buffered press from its strike start |

Cancel points: elapsed s -> first 20 Hz sample at or after it (LMB-started swing).
GATE_EPS = 1e-6 s, so a point hit exactly (0.05-step float noise) counts.

| move | total | light = chainOpenSec | dodge .90 | guard .95 | move | bufferFrom .5 x windup |
|---|---|---|---|---|---|---|
| slashR2L | 1.50 | 0.97 -> 1.00 | 1.35 -> 1.35 | 1.425 -> 1.45 | .65: 0.975 -> 1.00 | 0.285 -> 0.30 |
| slashL2R | 1.67 | 1.32 -> 1.35 | 1.503 -> 1.55 | 1.587 -> 1.60 | .65: 1.086 -> 1.10 | 0.40 -> 0.40 |
| thrust | 1.00 | none (last move) | 0.90 -> 0.90 | 0.95 -> 0.95 | .80: 0.80 -> 0.80 | 0.20 -> 0.20 |

## 3. Cancel matrix as shipped (CONFIG.js:860-904, 909-925)

    slashR2L, slashL2R: lunge: 1.0, cancel: { dodge: 0.90, guard: 0.95, move: 0.65 },
      bufferFrom: 0.5, rootMotion: { windup: [0, 0], strike: [0, 0.9], recover: [0.9, 1.0] }
    thrust: lunge: 1.0, cancel: { dodge: 0.90, guard: 0.95, move: 0.80 },
      bufferFrom: 0.5, rootMotion: { windup: [0, 0], strike: [0, 1.5], recover: [1.5, 1.7] }
    light column = the existing chainOpenSec (0.20 / 0.26 / thrust none), unchanged.
    handAxe hack / chop (F3): cancel { dodge 0.90, guard 0.95, move 0.65 }; no
      bufferFrom (windup LMB still ignored), no rootMotion (legacy lunge metres).
    window.WH_CONFIG.combat.er = { dodgeHoldSec 0.35, guardRaiseSec 0.13,
      moveCancelWalkMult 0.5, backstep { duration 0.30, speedMult 0.9, iframes 0.20,
      staminaCost 20 } }; player.rollIFrameWindow 0.433 (CONFIG.js:559).
    A move without a column keeps the pre-EPR1 law (getCancelPoint): dodge from
      the recover start, guard and move never.

## 4. Buffer semantics

- Space (keyboard only): keydown latches dodgePressLatch and sets dodgeKeyDown
  (auto-repeat ignored); keyup clears dodgeKeyDown. sampleDodgeInput() runs once
  per update before the swing logic: a latched or down key counts as held for
  that frame; the first frame that samples it up is the release. Held < 350 ms ->
  tap -> requestDodge(true) on that frame. Held >= 350 ms (EPR1-A2 inclusive
  side) -> dodgeSprint while held (sprinting = Shift || dodgeSprint); release does
  nothing. A down+up inside one frame = one held frame, released on the next.
- Dodge queue (dodgeQueued; dodgeDir = input at release): set by a dodge request
  during a swing, from ANY stage (bufferFrom is LMB-only; B1 taps Space in
  windup). Fires in update() at cancelOpen('dodge'), at once if requested past
  the point, or when the swing is over; always a roll (dodge column = roll
  cancel) along live input, else the input at release, else facing. Cleared by
  firing, an LMB buffer (latest input wins), cancelAttack, respawn; dropped if
  dead / toggling / stamina < 25 at the point (the swing is kept).
- LMB buffer (existing comboQueued / comboBufferTimer): strike / recover presses
  unchanged (B2 byte-identical in effect); windup presses at or after
  bufferFrom x windup are buffered, earlier ones ignored. A windup-buffered press
  does not age during windup (its 0.65 s starts at the strike), so it reaches the
  chain window. Cleared by expiry, chain fire, swing end (a fresh press starts a
  new chain), cancelAttack / endCombo, a dodge request, a guard accept.
- Guard queue (guardQueued): RMB with the shield during a swing before its guard
  point queues (tryBlock); update() accepts it at cancelOpen('guard') or when the
  swing ends: blocking = true, parryTimer = 0.25, raise 0.13 s, while the swing
  plays out. Cleared by accept, refusal at accept time, and every endBlock (RMB
  release, roll, backstep, toggle, guard break, respawn).

## 5. blockActive symbol (EPR1-A3)

Player FIELD this.blockActive (player.js:91), per the addendum; no game.js hook
(read it as WH_DEBUG.getPlayer().blockActive). blocking keeps its v6/v7 accept
semantics (isBlocking, parry-timer start, block moveMult, regen, sprint gate).
Both hit-check sites in resolveIncomingHit read blockActive (EPR1-A5: parry
:687, block :698). The raise runs in update() (:977-982); parryWindow stays 0.25.

## 6. Root motion (spec 3.3, C1-C3)

applyRootMotion (player.js:936) runs from update() before clampToBounds (:1188,
C3). Per stage: cumulative forward metres [start, end] x move.lunge (1.0) along
facing. Frame-anchored: a stage's first sim frame sits on its start value and its
last on its end value, linear in frame index between; the stage-change frame adds
nothing. 20 Hz rows: slashR2L windup 0, strike 0 / 0.3 / 0.6 / 0.9, recover
0.9 -> 1.0 over 14 frames; thrust strike 0 -> 1.5 over 9 frames, recover 1.5 /
1.6 / 1.7. Reason: C1/C2 measure each stage from its first to its last row; a
continuous-time linear table shows only ~0.675 m of slashR2L's 0.9 m there
(4 strike rows = 3 intervals), outside the +-0.08 m bar. The last-frame time is
predicted from the current dt; any shortfall lands on the next stage's first
frame. Moves without a table keep the legacy velocity lunge (handAxe).
Clip composition: wiring unchanged - motion rides the group, clips ride the
skeleton (spec section 4). Against the old lunge the group sits +0.10 m further at
strike end (0.8 -> 0.9, 1.4 -> 1.5; inside the 0.2 m sweep budget) and the
recover now drifts +0.1 / +0.2 m under an in-place recover clip. No
compensation code; the look is a playtest item.

## 7. Touch path (EPR1-A7)

touch-controls.js unchanged. Its dodge button calls tryRoll() = "roll now"
(requestDodge(false)): never a backstep, no tap / hold gesture; during a swing it
queues to the dodge point like any dodge. Shift (keyboard, or the touch sprint
toggle writing keys.ShiftLeft) stays the sprint key. Its block button calls
tryBlock / endBlock: blocking is set immediately when idle; during a swing it now
queues to the guard point (it used to be refused).

## 8. Per-AC map (player.js unless noted)

- A1: keydown latch :271, keyup :290, sampleDodgeInput :443 -> requestDodge :376
  -> startRoll :405 (direction inputDirWorld :352).
- A2: requestDodge (no direction, keyboard) -> startBackstep :424 (endCombo
  :802); hop in update() :1097-1104; CONFIG combat.er.backstep.
- A3: sampleDodgeInput hold -> dodgeSprint; collectMoveInput :347; a release after
  >= 350 ms does nothing.
- A4: CONFIG.js:559 rollIFrameWindow 0.433; startRoll :410.
- B1: getCancelPoint :837, cancelOpen :846. dodge: requestDodge :376 + gate
  :1052; guard: tryBlock :467 + gate :1053; move: walk :1122-1125; light: chain
  window :1045-1048 (unchanged).
- B2: chain window and strike / recover buffering unchanged (:1045-1048, :724).
- B3: blockActive :91, raise :977-982, accept :478-481, hit checks :687 / :698.
- B4: walk restore :1122-1125 (0.5 x walkSpeed from cancel.move).
- B5: tryAttack windup clause :730-732; windup-press lifetime hold :1036.
- C1 / C2: applyRootMotion :936, call :1188; CONFIG rootMotion.
- C3: root motion runs before clampToBounds (:1188 -> :1190).
- D1: v6/v7 paths kept: an idle tryBlock accepts at once with the parry window,
  guardBreak -> endBlock, toggleLoadout (+ restored endCombo :802), RMB offhand
  routing (mousedown unchanged); casts are refused during a backstep as in a
  roll (:564).
- E1: no asset / anim.js / MOVE_NAMES change.
- E2: section 10.
- E3: CONFIG.js, player.js, io/erparity-impl-notes.md only.
- F1: this file. F2: not created (1.4). F3: handAxe columns (CONFIG.js:898, :903).

## 9. Known deviations, interpretations, risks

- EPR1-A6: the hold split uses an integer accumulator (round(dt*1000) ms per
  sampled frame), not a raw frame counter. At the 20 Hz clamp that is exactly
  "hold frames >= 7"; at 60 fps a raw counter would split at 0.117 s. A literal
  frame counter is a one-line change if IO prefers it.
- Root motion is frame-anchored (section 6); the stage-change frame carries none.
- A no-direction dodge queued during a swing rolls along facing (B1 expects a
  roll); the backstep is the neutral tap only (A2).
- A guard accepted at the guard point leaves the swing running (B1e reads the
  first blocking row's elapsed, which needs attacking).
- A1 harness timing: f_up is read after keyup and rows with f <= f_up count as
  early. If a rAF frame lands between the harness's Space down and up (a
  few-ms window) the first post-release row counts as early: small flake risk.
- B1 needs its 400 ms Space hold to stay under 7 frames (holds at 2-11 fps; breaks above ~15 fps).
- Pre-existing defect fixed: Player.prototype.endCombo (from 33d0d80) is missing
  on origin/dev while toggleLoadout() and respawnAt() call it, so KeyQ threw a
  TypeError (a harness pageerror / crash). Restored verbatim at :802; separable.

## 10. E2 floor (read-only analysis, nothing run)

- ds1 and the v7 main body load builds/v7-playable.html (inlined bundle from
  2026-10-04 with pre-Round-D CONFIG), so EPR1 is invisible to them until the
  bundle is rebuilt at landing: no new FAIL from them during the build.
- v2 never attacks, dodges or blocks: unaffected.
- v3 (live code): cancel and walk already fail; stages unchanged. lunge: today the
  first strike frame moves 0.2 m; the frame-anchored table moves 0 there and
  0.3 m on the next frame, so it flips only if the probe's poll window ends
  exactly on the first strike frame.
- v7 AC8 (cross-finisher) and AC13 (zero console errors) fail today because KeyQ
  throws; endCombo removes that cause once the bundle carries it.
- ds1 reuses whatever already listens on 8791; it must serve this worktree.
  After a bundle rebuild the Round D swings (2.3x longer) alone break ds1
  wall-clock budgets (A1-1, A1-2, A1-3, A2-1/2/4, A4-1, A4-3): re-freeze the
  floor on a rebuilt pre-EPR1 bundle to separate those from EPR1.

## 11. Harness prediction (compiled harness, not run)

A1 PASS (flake risk, 9), A2 PASS, A3 PASS, A4 PASS, B1 PASS, B1e FAIL (1.2),
B2 FAIL (1.1), B3 PASS, B4 PASS, B5 FAIL (1.1), C1 FAIL (1.1; C2 not evaluated),
C3 PASS, D1 PASS, E1 PASS, E2 PASS expected (10), E3 PASS, F1 PASS, F2 info,
F3 PASS. The exit code also needs zero page errors (KeyQ no longer throws).
