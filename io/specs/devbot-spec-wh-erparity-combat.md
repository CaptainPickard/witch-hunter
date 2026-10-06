# EPR1 — Witch Hunter "ER-Parity Combat Values" — IO Implementation Spec

Status: SPEC OF RECORD (pre-Dispatcher). Version 1.0 (2026-10-06). Any
dispatch-text divergence from this file is superseded by THIS text.

## 0. Assignment + environment

- Implementation lane: **Claude Code CLI, model `opus`** (Nicko order 2026-10-06,
  replaces the dispatch-profile default for this round). Print mode `-p`,
  explicit `--model opus`, workdir `/workspace/witch-hunter`.
- Validation: Testerbot writes/owns a validation spec AFTER this spec (gate order
  2). Devbot runs the Testerbot harness during build but NEVER edits it.
- Repo: `/workspace/witch-hunter`, GitHub CaptainPickard/witch-hunter.
  IO is the sole git gatekeeper — **Devbot does NOT commit, stage, or push.**
- Validation law: Playwright headless on VPS (no node). Timing windows are
  SIMULATION-frame counts (the sim advances exactly maxDt per rAF frame at
  headless 2–11 wall fps), never wall seconds. Conventions:
  `io/devops/spec-gated-build-loop/references/playwright-headless-frame-clock-gotchas-2026-09-30.md`
  (window samplers write rows into `window.__IO_*_ROWS` and RETURN INSTANTLY;
  never promise-shaped; install samplers before the input act; organic-path
  inputs only).
- Amendment protocol: a real contract conflict = STOP at first deliverable, file
  an amendment request inside `scratch/erparity-amendments.md` (proposal + exact
  spec line refs). IO rules, amendments land inline in BOTH spec files as
  `AMENDMENT EPR1-A<n> (<date>): ...`. Spec files are the contract of record.

## 1. Branch + census freeze (multi-session gate)

Implementation lands on a FRESH branch cut from origin/dev by Devbot at build
start:

    git fetch origin && git worktree add ../wh-erparity worktree/erparity origin/dev
    (work in ../wh-erparity; the live checkout feat/mouse-bind-cam is NEVER touched)

The main checkout `/workspace/witch-hunter` currently sits on
`feat/mouse-bind-cam` with mid-flight churn owned by another session. Census
freeze (2026-10-06, measured on the live checkout):

- HEAD: `1e5363b` (feat/mouse-bind-cam); origin/dev is the spec's code base.
- Known OTHER-session dirty churn, do NOT touch, do NOT "clean up":
  `prototype/index.html`, `prototype/js/CONFIG.js`, `prototype/js/player.js`,
  `prototype/style.css`, `scratch/treeqa/roundI/decimate.jsonl`, plus untracked
  `io/*` briefs/harness scripts from prior rounds.
- Tree-hygiene verdict shape: set-difference — new non-scope entries fail;
  frozen entries above do not.

## 2. Reference basis (what we are porting, and what we may not)

Source analyzed 2026-10-06: `Funny-Bones/ELDEN-RING-Playermodel-Rust`
(clone kept at `/workspace/_analysis/ELDEN-RING-Playermodel-Rust`, 1 commit,
`23316a8`). It is a from-scratch ELDER-RING-style player-combat SIMULATION in
Rust/Bevy whose `src/sim/` reproduces ER's action-state machine; its Python
`tools/` decode ER's TAE/HKX. **No ER data or assets are in that repo
(gitignored), so nothing there is an animation source.** This round ports
DESIGN VALUES + COMBAT GRAMMAR only — the numbers and event-window model its
`src/sim/tests.rs` (958 lines) proves out — into our JS combat layer.

HARD RULES:
- R1: NO code files from that repo are copied or vendored into witch-hunter.
  Everything we land is written fresh against our JS architecture.
- R2: NO animation change of any kind (see §8 animation invariant). New
  gameplay behavior must run off our EXISTING 24 player clips + procedural
  motion.
- R3: No license on the reference repo — reference reads are fine; no file
  copying (restates R1; applies even to `tools/*.py`).

## 3. Numbers of record (design-time, ER-derived)

Sourcing honesty: the reference repo ships its extracted action table ONLY as
a gitignored output; what follows is (a) behavior the repo's test suite proves
(marked PROVEN), (b) design-time values derived in our analysis of the sim and
of published ER behavior (marked DESIGN). DESIGN values are CONFIG-tunable and
must pass playtest; they are not claimed byte-exact.

### 3.1 Roll (current → EPR1)

| Field                            | Current CONFIG                     | EPR1 value |
|----------------------------------|------------------------------------|------------|
| rollDuration                     | 0.45 s                             | 0.45 s (unchanged) |
| rollIFrameWindow                 | 0.35 s                             | **0.433 s** (PROVEN: medium roll = 13 i-frames @ 30 Hz) |
| rollStaminaCost                  | 25.0                               | 25.0 (unchanged) |
| roll trigger                     | keypress fires roll                | **roll fires on RELEASE** of dodge key (PROVEN: `roll_comes_out_on_release`, `dodge_without_direction_is_a_backstep`) |
| tap dodge, no move direction     | rolls                              | **BACKSTEP**: quick backwards hop, ~0.30 s, short i-frames 0.20 s, resets chain (PROVEN) |
| hold dodge                       | not implemented                    | **SPRINT while held**; release does NOT roll (PROVEN: `holding_dodge_sprints_and_release_does_not_roll`) |

Roll chain-cancel law unchanged (roll cancels RECOVER only) plus the new
cancel-dodge column in §3.2 may extend which stages roll can interrupt.

### 3.2 Per-input-type cancel matrix (the core of ER-parity)

New CONFIG block `window.WH_CONFIG.combat.er` — per-player-move threshold
table: the EARLIEST point at which each input TYPE may interrupt that action,
mirroring the ER-action model
(`cancel_light/cancel_heavy/cancel_dodge/cancel_jump/cancel_guard/cancel_move`).
We have no heavy/jump yet → columns we use: `light`, `dodge`, `guard`, `move`.
dodge/guard/move are FRACTIONS of each move's total (windup+strike+recover) so
per-move durations stay the drivers (Round D law); the light (chain) column is
the one exception — absolute seconds into recover, preserving current behavior
exactly. Totals: slashR2L = 0.57+0.20+0.73 = 1.50 s; slashL2R = 0.80+0.26+0.61
= 1.67 s; thrust = 0.40+0.43+0.17 = 1.00 s.

| move      | total   | light (chain)                  | dodge | guard | move |
|-----------|---------|--------------------------------|-------|-------|------|
| slashR2L  | 1.50 s  | 0.20 s into recover (as today) | 0.90  | 0.95  | 0.65 |
| slashL2R  | 1.67 s  | 0.26 s into recover (as today) | 0.90  | 0.95  | 0.65 |
| thrust    | 1.00 s  | none (last move)               | 0.90  | 0.95  | 0.80 |

- `guard` column = RMB hold becomes accepted (block raises) once fraction
  reached; guard-raise has a windup delay: block is ACTIVE 0.13 s after accept
  (DESIGN ≈ ER 4-frame guard raise).
- `light` (chain) column is expressed as the EXISTING absolute
  chainOpenSec values (seconds into recover: 0.20 slashR2L, 0.26 slashL2R;
  thrust none) — NOT as a fraction. This preserves current chain behavior
  exactly; fractions are reserved for dodge/guard/move columns.
- `dodge` column = roll-cancel availability: fraction of action after which a
  buffered roll may fire. 0.90 DESIGN for all three moves = late-recover only,
  consistent with "roll may cancel RECOVER only"; the table column re-derives
  that gate as data (eliminates the hardcoded recover-only rule).
- `move` column = walk-speed restore: from this fraction of the action to its
  end, the player walks at 0.5× base walk speed (independent of
  moveMultWhileAttacking, which still gates the earlier stages exactly as
  today: windup 0.3×, strike 0, recover 0). DESIGN values: 0.65 for both
  slashes, 0.80 for thrust.
- Chain behavior preserved: buffered LMB fires the NEXT chain move; chainCap 3;
  last move waits full recover; roll resets chain; chain resets when an action
  ends without chaining (PROVEN: `combo_resets_once_the_animation_is_left`,
  `light_chain_runs_five_deep_then_loops` — our cap stays 3 per current design).
- Buffer windows per move (fraction of action when presses start being
  LISTENED for): windup presses remain IGNORED EXCEPT from bufferFrom; DESIGN
  bufferFrom 0.5 for all three moves (mid-windup onward = ER's generous
  chain buffering). buffer lifetime stays `inputBufferSec: 0.65`.
  (PROVEN shape: presses BEFORE the input window are lost;
  `queued_attack_fires_exactly_at_the_cancel_frame`.)

### 3.3 Attack root motion (DESIGN table, sim-frame driven)

Replace the single `lunge` constant with a per-move FRAME TABLE of cumulative
forward metres from impact-aligned motion (ER grammar: step-IN during strike,
drift-stop in recover, never during windup):

| move     | windup | strike | recover |
|----------|--------|--------|---------|
| slashR2L | 0.0    | 0→0.9  | 0.9→1.0 |
| slashL2R | 0.0    | 0→0.9  | 0.9→1.0 |
| thrust   | 0.0    | 0→1.5  | 1.5→1.7 |

Interpolate linearly within strike/recover; the old `lunge` field stays in
CONFIG as a legacy multiplier of the table's total (default 1.0). The table is
data in CONFIG. Movement is root-motion added to the player's stage-velocity
model (`moveMultWhileAttacking` still gates walk input entirely).

## 4. Precision map (edit points; verify anchor ±3 lines before each edit)

- `prototype/js/CONFIG.js` — moveset block spans ~lines 828–889
  (`window.WH_CONFIG.moveset`, `inputBufferSec` at 845, weapons at 846, moves
  855–886). EDIT: add `window.WH_CONFIG.combat.er` block + per-move
  `cancel`/`bufferFrom`/`rootMotion` fields inside the existing weapons.moves
  entries (slashR2L 856, slashL2R 860, thrust 865, handAxe 878/882 gains the
  same COLUMNS but DESIGN values only if trivially derivable — see F3).
  DO-NOT-ALTER within this zone: `chain`, `chainCap`, `damage`, `range`,
  `halfAngleDeg`, `staminaCost`, `damageGhoulMult`, `pose`, existing
  `windup/strike/recover/chainOpenSec` seconds (cancel matrix consumes them,
  never rewrites them), `banditStageMult`, `enemyWeapon`, touch block (894+).
- `prototype/js/player.js` (~1208 lines) — roll sites: state fields ~50–54
  (`rolling/rollTimer/rollDir`), `tryRoll` ~416 (`IFrames = CONFIG.rollIFrameWindow`
  at 426, roll-dir logic 428–434), roll-cancel-of-recover comment ~413–415;
  input wiring: dodge keydown site ~257; block sites: `tryBlock` ~440,
  RMB routes ~300–311; stagger/guard-break fields ~72–81. EDIT: (a) release-vs-
  hold dodge state machine (edge-detected press timestamp: release <0.35 s hold
  = roll or backstep; hold >=0.35 s = sprint until release, no roll on release)
  (b) backstep state (procedural hop: 0.30 s backwards at 0.9× walk speed,
  i-frames 0.20 s) (c) buffered-roll consumption via cancel.dodge
  column (d) guard-raise delay 0.13 s between `blocking=true` accept and block
  ACTIVE (hit checks must read the delayed active flag) (e) root-motion table
  consumer.
- `prototype/js/anim.js` (~297 lines) — `MOVE_NAMES` ~lines 10–30 with
  `MOVE_FALLBACK_NAMES` right after; `seekAttack` ~178–250; stage-boundary
  mapping. EDIT: NOTHING for clips. The stage clock stays CONFIG-driven.
  Root-motion may visually separate root from a fixed animation — acceptable
  at EPR1 (blend the body's move-mult pose as today; motion rides the group,
  clip rides the skeleton, unchanged wiring).
- `prototype/js/moveset.js` (50 lines) — EDIT: none (pose keyframes untouched).
- `prototype/js/enemy.js` (475) — EDIT: none (bandit attackPhase block
  CONFIG 671–676 untouched). Watch-item only: enemy's windup-track law
  ("only windup may track") is independent of our player-facing cancels.
- `prototype/index.html` — EDIT: none (no new files; CONFIG/player/anim are
  already script includes). Build-script bump happens at landing, not in build.

## 5. Acceptance criteria

AC IDs: A=CONFIG data, B=roll redesign, C=cancel/buffer matrix, D=root motion,
E=preservation/harness, F=deliverables. All timed ACs are SIM-FRAME counts
(harness converts the seconds above at the GAME's rAF frame clock — dt clamped
at maxDt = 0.05 s/frame (20 Hz sim; CONFIG.js maxDt) — ±2 game frames
tolerance, per Testerbot valspec §1. Design-frame provenance (e.g. roll i-frames
= ER 13 frames @ 30 Hz = 0.4333 s) stays in the DESIGN section seconds column;
seconds are the number of record.

> AMENDMENT EPR1-A1 (2026-10-06, responding to Testerbot valspec §9.1 — frame
> basis): harness frame math uses the game frame clock 1/maxDt = 20 Hz. The
> "30 Hz" phrasing in this section originally referred to ER design-frame
> provenance only. RULING: seconds are the number of record everywhere;
> frame counts in gates are game frames (seconds / 0.05).
>
> AMENDMENT EPR1-A2 (2026-10-06, Testerbot §9.2 — roll boundary): the 0.35 s
> hold threshold is INCLUSIVE on the sprint side: a Space hold of exactly
> 0.35 s (7.0 game frames) releases as SPRINT (no roll). Taps strictly
> under 0.35 s roll on release. The winning side must be stated in F1 impl
> notes.
>
> AMENDMENT EPR1-A5 (2026-10-06, Devbot pre-flight 2): BOTH hit-check sites in
> `resolveIncomingHit` read the delayed flag: the parry check (player.js:559)
> AND the block/absorb check (player.js:570) switch from `this.blocking` to
> `this.blockActive`. Guard-raise (0.13 s) is subtracted from the effective
> parry window naturally (parry needs raise-completed state); the 0.25 s
> CONFIG parryWindow value itself is UNCHANGED (D1). `this.blocking` keeps
> its v6/v7 semantics (RMB accept); only hit-check reads change.
>
> AMENDMENT EPR1-A6 (2026-10-06, Devbot pre-flight 3): the 0.35 s hold
> boundary is evaluated in SIM FRAMES (accumulate dt-clamped frames; hold
> frames >= 7 -> sprint on release, tap < 7 -> roll on release). No
> floating-point accumulation of 0.05 s steps for the boundary decision.
>
> AMENDMENT EPR1-A7 (2026-10-06, Devbot pre-flight 5): touch-controls.js
> compatibility is binding: `tryRoll()` keeps meaning "roll now" (its dodge
> button maps to an immediate dodge, not a tap/hold gesture), Shift remains
> the sprint key, and `tryBlock/endBlock` keep setting `blocking`
> immediately. The tap/hold state machine applies to the KEYBOARD Space
> handler only. State the touch path treatment in F1 impl notes.

- A1 (PROVEN port): roll fires on dodge-key RELEASE when held <0.35 s with a
  move direction; direction = input direction at release.
- A2 (PROVEN port): dodge tap with NO move direction = backstep (not roll):
  backward hop 0.30 s, iframes 0.20 s, chain reset, stamina cost 20 (DESIGN).
- A3 (PROVEN port): holding dodge >=0.35 s = sprint held; releasing never
  produces a roll (release <0.35 s after sprint-start counts as tap only if
  total hold <0.35 s — total-hold rule, PROVEN wording).
- A4: rollIFrameWindow 0.433 s verified (13 sim-frames @ 30 Hz).
- B1 (matrix): for each of the 3 moves × 4 columns, a buffered input fired
  exactly at the cancel fraction takes effect at that frame (organic
  key/mouse events; direct state mutation banned as a test act), and the same
  input 1 sim-frame BEFORE the cancel point is ignored/queued per current
  chain rules (no mid-stage skips).
- B2: chainOpenSec behavior is byte-identical in effect to pre-EPR1 for
  slashR2L (0.20 s into recover) and slashL2R (0.26 s): regressions here fail
  the round (existing chain tests must stay green — preservation E2).
- B3: guard-raise delay: RMB press during an action ≥guard fraction raises
  block only after cancel-guard fires; ACTIVE 0.13 s later; hit checks before
  ACTIVE do not see blocking. SYMBOL CONTRACT (AMENDMENT EPR1-A3, 2026-10-06,
  responding to Testerbot valspec §9.4): the implementation must expose the
  raised/active distinction as a player field named `blockActive` OR via a
  debug hook `getBlockActive()`; whichever it ships, F1 impl notes must
  declare the choice. The harness-side probe accepts either symbol.
- B4: move-cancel: from the move fraction onward the player walks at 0.5×
  base walk speed while the action's remaining stages play (walk-speed
  restore, NOT moveMult multiplication — moveMultWhileAttacking stays 0
  through strike/recover for stages before the cancel point).
- B5: bufferFrom: LMB pressed before bufferFrom is IGNORED (still true after
  EPR1); LMB at bufferFrom during windup is BUFFERED and fires its chain move
  at the light cancel point. VALIDATION NOTE (AMENDMENT EPR1-A4, 2026-10-06,
  Testerbot valspec §9.3 concurred): pre-build, windup presses are dropped
  wholesale (tryAttack windup-drop), so the 1-frame-early sub-gate has no
  pre/post discriminator — it is a post-build correctness gate only; the
  discriminating pre-build signal for B5 is the at-bufferFrom buffering
  behavior itself.
- C1 (root motion): during slashR2L strike, cumulative forward displacement
  tracks the table 0→0.9 m (±0.08 m at strike end); windup = zero forward
  travel; recover adds to 1.0 m and drift-stops.
- C2: thrust strike 0→1.5 m; no root motion on any other axis (lateral yaw
  sweep unchanged).
- C3: root motion does not fire while `moving` blocked by walls (level clamp
  unchanged — assert no underground/clip through the existing level clamp).
- D1: backstep + roll + sprint states exhaustively preserve v6/v7 semantics:
  block-open parry window, guard-break recovery, touch layer off-state,
  toggling block, offhand spell route.
- E1 (animation invariant): player combat GLB untouched — assets.js expected
  clip count 24 check still passes; `MOVE_NAMES` + `MOVE_FALLBACK_NAMES`
  untouched; three WH_SS_* names resolve; authored WH_SlashR2L/L2R/Thrust
  clips REMAIN in the GLB (rollback law intact).
- E2 (suite floor): the existing combat/playwright harness profile passes with
  zero NEW failing test IDs vs the dispatch-time capture (Testerbot freezes
  suite floor + hashes at dispatch; freeze-time hashes informational).
- E3 (tree hygiene): only §4-named files change in the round worktree; other
  workstream churn untouched; census §1 holds (set-difference).
- F1: implementation notes file `io/erparity-impl-notes.md`: per-AC map with
  file:line evidence, the cancel fractions table as implemented, any DESIGN
  value adjusted with rationale (allowed — all DESIGN values are tunable and
  flagged), open questions.
- F2: `scratch/erparity-amendments.md` created IF (and only if) an amendment
  was requested; else absent.
- F3 (handAxe note, non-blocking): handAxe gains the cancel COLUMNS with
  neutral values (light=chainOpenSec-as-is; dodge/guard fractions mirroring
  longsword), OR a one-line note in F1 stating column-deferral — either is a
  PASS.

## 6. Test-quality law (binding for the validation spec)

- Organic-path only: real keyboard/mouse events through the page's input
  pipeline. No direct state mutation as a test act (established WH law).
- Window samplers: `window.__IO_<name>_ROWS` + INSTANT return; installed
  before the act; drained via short evaluates. Sim-frame arithmetic only.
- Enemy positioning via live-handle displacement (set BOTH `e.pos` and
  `e.root.position`; verify by reading `lockTarget.pos` back).

## 7. Out of scope (explicitly NOT this round)

- Enemy retuning, new enemy moves, block/parry damage math changes.
- Charged heavies, jump attacks, guard counters, crouch movesets, aerial
  combat, hit-reaction severity tiers, equip-load tiers (roll i-frame table
  stays single-tier medium).
- Any animation/GLB work, any new asset pipeline work.
- The in-flight mouse-bind/camera/weave workstreams.

## 8. Animation invariant statement (why "no new animations")

EPR1 ports timing/cancel/root-motion BEHAVIOR: everything lands on our existing
24-clip combat-sword GLB and procedural states. The stage clock that plays our
clips is the same one ER's event model maps onto; per-action windows are data.
Root motion is authored motion on the group transform — no new clip required.

## 9. Open playtest items (for the verdict, not blockers)

- 0.35 s tap/hold split, backstep distance/feel, move-cancel 0.5× and
  bufferFrom 0.5, root-motion magnitudes: all DESIGN, all expected to need
  taste passes after playtest (Nicko).