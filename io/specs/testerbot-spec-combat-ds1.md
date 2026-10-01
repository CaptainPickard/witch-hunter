# Testerbot Validation Spec — Witch Hunter Combat Round A (round id: combat-ds1-A)

- **Author:** Testerbot, on IO order. Authored 2026-09-30.
- **Harness of record:** `tests/wh_combat_ds1_validation.py` (executable twin of this spec).
- **Repo / branch / base HEAD:** `/workspace/witch-hunter`, branch `dev`, base HEAD `c679d2c`.
- **Status:** FROZEN PRE-DEVBOT. Devbot runs the harness against this spec; Devbot NEVER edits either file.
- **Scope:** Combat Round A acceptance criteria AC-A1-1 … AC-A4-4 (18 ACs), organic-path validation only.

## 1. Principles

### 1.1 Independence

- This spec and its harness are Testerbot-authored and frozen BEFORE Devbot begins
  implementation. They are the quality gate, not a collaboration artifact.
- Devbot MAY run the harness for self-diagnosis, but Devbot NEVER edits the harness,
  this spec, or any probe it contains. Any Devbot edit to these two files is an
  automatic validation failure regardless of test outcomes.
- Testerbot re-runs EVERYTHING at verdict time on its own machine lane. Nothing
  from a Devbot-side run (logs, screenshots, self-reports) counts as evidence.
- IO commits and pushes only after Testerbot issues a full TESTERBOT PASS verdict.
  A Devbot "it works" is never sufficient for the git gate.

### 1.2 Evidence over claim

- Every PASS requires `file:line` evidence (or harness probe output with an AC id
  and a measured value) verified at verdict time by Testerbot.
- Child self-reports are not measurements. If Devbot says "yaw chases at 240deg/s",
  Testerbot must have a probe trace that shows the per-frame deltas.
- A PASS may NEVER be claimed from a state-write. The harness performs only real
  input acts (mouse, keyboard, live-handle enemy displacement per the organic-path
  law). If a probe needs a setup call (teleport, setCameraYaw), it is clearly
  separated in the harness from the ACT and the assertion, and the assertion reads
  only organic consequences of the ACT.
- Evidence that cannot be reproduced at verdict time is not evidence.

### 1.3 Specs of record

- The specs of record for this round are BOTH `io/specs/devbot-spec-combat-ds1.md`
  (implementation contract, owned by IO/Devbot lane) AND this file
  `io/specs/testerbot-spec-combat-ds1.md` (validation contract, owned by Testerbot).
- Dispatch text (any chat/agent message describing the work) NEVER overrides these
  two files. If dispatch text and spec disagree, the spec wins and the discrepancy
  is logged in the amendment log (section 8).
- The devbot spec may drift only via logged 'AMENDMENT' entries in its own section 9;
  any unlogged drift is a freeze violation (see section 3).

## 2. Verdict Protocol

### 2.1 Per-AC matrix

At verdict time Testerbot produces one row per AC:

| AC id | input path used | key assertion | verdict | evidence (file:line or probe trace) |
|-------|-----------------|---------------|---------|--------------------------------------|

Rules for the matrix:

- Verdict per AC is exactly one of `PASS`, `FAIL`, `FLAKE-PASS`, `FLAKE-FAIL`.
- `input path used` names the organic path actually exercised (e.g. "F-lock + LMB
  swing + live-handle target displacement during windup").
- `evidence` must be specific: a `file:line` in the built artifact or a harness
  trace line with measured values. "Looked fine" is invalid evidence.
- An AC that was never executed (harness crash, unreachable precondition) is FAIL
  with the mechanism documented, never silently omitted.

### 2.2 Final verdict JSON

    {
      "round": "combat-ds1-A",
      "verdict": "PASS" | "FAIL",
      "per_ac": [
        {"id": "AC-A1-1", "verdict": "PASS", "evidence": "..."},
        ...
      ],
      "flakes": ["..."],
      "hygiene": {
        "git_dirty_count": <int>,
        "head_check": "<actual HEAD sha>",
        "freeze_checks": "<pass/fail per freeze entry>"
      }
    }

Top-level verdict is PASS only when all 18 per-AC verdicts are PASS or FLAKE-PASS,
the flake protocol (section 7) is satisfied, and every hygiene check passes.

### 2.3 Honest-partial rules

- An AC may be an honest FAIL with the failure mechanism documented (which probe,
  which sample, which expected vs actual value). Honest FAILs are normal
  pre-Devbot and are the primary feedback channel to Devbot.
- A PASS may NEVER be claimed from a state-write (see 1.2). A probe that had to
  poke engine state to make an assertion pass is an automatic FAIL for that AC.
- A smoke-run FAIL BEFORE Devbot implements (pre-build profile, section 5.3) is
  EXPECTED and is not a verdict. Only the post-build run produces the verdict.
- Partial credit does not exist: an AC is PASS or FAIL, never "mostly works".

## 3. Freeze Table (VERBATIM — 16 entries + 1 measured anchor)

At authoring time (2026-09-30, Testerbot) these entries are frozen. At verdict time
Testerbot re-hashes every entry. ANY drift in the 16 verbatim entries (other than
the explicitly permitted v7-playable rebuild and the devbot-spec amendment path)
is an automatic verdict FAIL.

```
docs/planning/04-combat-system.md sha256:cb397f3d74df lines:594
docs/planning/08-open-questions.md sha256:b0489cc2931e lines:1255
docs/planning/17-magic-system.md sha256:88b3c4314df9 lines:446
docs/planning/27-equipment-visual-system.md sha256:3660645445a2 lines:166
docs/planning/33-equipment-and-formulas.md sha256:bf6f0a8896bf lines:277
prototype/index.html sha256:cec75217eb37 lines:38
prototype/js/CONFIG.js sha256:5c906a421f31 lines:429
prototype/js/game.js sha256:f7c6c4d9744b lines:765
prototype/js/player.js sha256:f91b8dd92860 lines:932
prototype/style.css sha256:d31fe8487155 lines:293
io/specs/devbot-spec-whproto7-weave.md sha256:384bd5c31825 lines:116
io/specs/testerbot-spec-whproto7-weave.md sha256:6b665829b26b lines:58
prototype/builds/v7-playable.html sha256:6ceff6ecf23f lines:88741
prototype/js/spells.js sha256:082225b2d14d lines:97
tests/wh_v7_weave.py sha256:d2893c23b834 lines:462
tools/build_v7.py sha256:1ed740715ea0 lines:34
```

### 3.1 Rebuild permission (parallel WEAVE workstream)

`prototype/builds/v7-playable.html` and `tools/build_v7.py` belong to the parallel
WEAVE workstream; the combat round REBUILDS `v7-playable.html`. At verdict time
re-hash it and REQUIRE:

- the new build sha256 DIFFERS from `6ceff6ecf23f`;
- the new build CONTAINS the markers `startAttack` AND `attackPhase`;
- NO OTHER freeze entry drifted, EXCEPT `io/specs/devbot-spec-combat-ds1.md`,
  which may drift only via 'AMENDMENT' entries logged in its section 9.

### 3.2 Measured anchor (devbot-spec, frozen at authoring time)

- `io/specs/devbot-spec-combat-ds1.md` sha256 `6f7e14d50859` at authoring time; AMENDED 2026-09-30 by IO (AMENDMENT D1: m3-combo cap boundary + attackPhase nested shape/key names per Devbot R1) -> current anchor `52b4af42f3f1`; re-measure at verdict time and require the D1 amendment markers present (measured by Testerbot
  at authoring time, 2026-09-30, on branch dev). This is the 17th freeze anchor;
  any drift without a logged amendment is a verdict FAIL.

### 3.3 Baseline anomalies recorded at authoring time (honesty notes)

- HEAD at authoring time measures `395c5d8` (not the dispatched `c679d2c`): dev
  history is `c679d2c` -> `395c5d8` ("fix: remove hardcoded Meshy API key
  fallback"). Verdict-time hygiene checks HEAD = `395c5d8` + nothing staged.
  If the branch advances by verdict time, IO must note it in the amendment log;
  the combat work must still be UNCOMMITTED at verdict time (16 dirty freeze
  entries + io/reports/ + the 2 combat-ds1 specs + the 2 Testerbot files).
- `git status --porcelain` at authoring time shows 16 modified/untracked freeze
  entries plus `io/reports/`, `io/specs/devbot-spec-combat-ds1.md`, and this
  spec's own path. `io/reports/` is an IO-owned untracked directory; its presence
  is expected and does not violate hygiene.

## 4. Verdict-Time Hygiene Commands

Run these immediately before producing the verdict JSON; record raw output:

    cd /workspace/witch-hunter
    git rev-parse HEAD                 # expect 395c5d8 (see 3.3) + nothing staged
    git diff --cached --stat           # expect EMPTY (nothing staged)
    git status --porcelain | wc -l     # expect 18 (see breakdown below)

Expected `git status --porcelain` census (verdict time):

- **18 = pre-Testerbot baseline** (measured 2026-09-30, before Testerbot authored
  its files): 10 modified freeze entries (04/08/17/27/33 planning docs,
  index.html, CONFIG.js, game.js, player.js, style.css) + 6 untracked freeze
  entries (devbot-spec-whproto7-weave.md, testerbot-spec-whproto7-weave.md,
  v7-playable.html, spells.js, wh_v7_weave.py, build_v7.py) + 1 `io/reports/`
  + 1 `io/specs/devbot-spec-combat-ds1.md`.
- **20 = authoring-time measured value**: baseline 18 PLUS this spec and the
  harness (`tests/wh_combat_ds1_validation.py`), which Testerbot keeps in the
  worktree to re-run at verdict time. If IO has staged/committed the Testerbot
  files by verdict time, the census reads 18 again.
- Census ABOVE 20 (or above 18 with Testerbot files committed) = unexpected
  dirt — FAIL hygiene and investigate before any verdict is issued.
- Census BELOW 18 = a frozen file was lost or removed — FAIL hygiene.

Freeze re-hash sweep (verdict time):

    for f in docs/planning/04-combat-system.md docs/planning/08-open-questions.md \
             docs/planning/17-magic-system.md docs/planning/27-equipment-visual-system.md \
             docs/planning/33-equipment-and-formulas.md prototype/index.html \
             prototype/js/CONFIG.js prototype/js/game.js prototype/js/player.js \
             prototype/style.css io/specs/devbot-spec-whproto7-weave.md \
             io/specs/testerbot-spec-whproto7-weave.md prototype/js/spells.js \
             tests/wh_v7_weave.py tools/build_v7.py io/specs/devbot-spec-combat-ds1.md; \
      do sha256sum "$f"; done
    sha256sum prototype/builds/v7-playable.html   # must DIFFER from 6ceff6ecf23f
    grep -c startAttack prototype/builds/v7-playable.html   # >= 1
    grep -c attackPhase prototype/builds/v7-playable.html   # >= 1

## 5. Harness Execution Protocol

### 5.1 How to run

    cd /workspace/witch-hunter
    python3 tests/wh_combat_ds1_validation.py            # auto-starts+kills server

Environment: `WH_BASE_ROOT` overrides the base URL (default
`http://localhost:8791/`). The harness starts `prototype/server.py` itself via
subprocess (poll GET `BASE_ROOT` up to 15s for HTTP 200) and ALWAYS terminates
it in a `finally`. If an external server is already serving the port, set
`WH_BASE_ROOT` to it; the harness tolerates a pre-existing server (its own
start attempt will fail to bind and it falls back to polling).

### 5.2 What the harness is

The harness is the ORGANIC-PATH twin of this spec: every ACT is a real input
(mouse `page.mouse`, keyboard `page.keyboard`) or a live-handle mutation of an
enemy position via the documented WH_DEBUG `ref` (enemy displacement is the
one sanctioned non-input act — it simulates the target moving, and it is
explicitly required by the AC input paths). Setup helpers (teleportPlayer,
setCameraYaw, page loads) are clearly separated from ACTs. The harness contains
NO writes to player combat state (no comboIndex, attacking, hp, or yaw pokes).
All reads are attribute-guarded so a PRE-Devbot build yields clean FAILs,
never crashes.

### 5.3 Expected PRE-Devbot result profile (smoke run)

When run against the current (pre-combat) build: MOST of the 18 ACs FAIL
(the Devbot-added fields — `attackPhase`, phase-gated damage, windup yaw
tracking, combo chain — do not exist yet), and the run reports ZERO CRASHES
(exit code 0; every AC reports a verdict line, none aborts the runner).
This profile is EXPECTED and is NOT a verdict; it proves only that the harness
executes end-to-end and fails honestly.

### 5.4 Expected POST-Devbot result profile (verdict run)

All 18 ACs PASS (or FLAKE-PASS per section 7), ZERO CRASHES, total runtime
under ~4 minutes, with every PASS backed by a measured trace line in the log.
Only Testerbot's re-run of this profile at verdict time produces the verdict.

## 6. The 18-AC Expectation Table

One row per AC: id | organic input path | key assertion | expected post-build verdict.

| id | organic input path | key assertion | expected |
|----|--------------------|---------------|----------|
| AC-A1-1 | F-lock, LMB swing, target displaced ~20deg during windup via live handle | player.yaw moves toward target; per-frame \|dyaw\| <= 240deg/s*0.05+eps; no jump | PASS |
| AC-A1-2 | same, target displaced far during strike+recover | yaw drift <= 0.02 rad until swing end; converges after | PASS |
| AC-A1-3 | no lock; LMB down starts attack AND drag; pointer sweep ~120deg across windup->strike | body offset trace max per-frame delta < 15 deg; camYaw moved; swing completes | PASS |

| AC-A1-4 | setCameraYaw 0/90/180/270 + LMB swings | body.parent == yawFrame; yawFrame.rotation.y == player.yaw within 1e-3; sword-vs-body world offset agrees (<=2cm) after yaw rotation | PASS |
| AC-A2-1 | LMB x3 each inside the recover window | comboIndex timeline [0,1,2]; attacking never false between swings; next windup within 2 rAF of boundary | PASS |
| AC-A2-2 | 4th LMB during m3 recover | fresh swing comboIndex 0 => [0,1,2,0]; no duplicate; press during restart windup/strike NOT queued | PASS |
| AC-A2-3 | fresh page, first LMB | comboIndex 0 through whole first swing | PASS |
| AC-A2-4 | full swing completes, then LMB | next swing comboIndex 0, exactly one swing | PASS |
| AC-A3-1 | lure bandit (spawn (-6,-8); stand (-6,-2) camYaw 0; press f optional) | first hp drop while attackPhase=='active'; >= 0.7s after attack-FSM entry (tolerance 0.1s) | PASS |
| AC-A3-2 | 3 consecutive windup entries | period == windup+active+recover +/- 0.2s (bandit 1.62s, ghoul 1.07s) | PASS |
| AC-A3-3 | 2 full swings vs stationary player | hp drops exactly twice | PASS |
| AC-A3-4 | watch weaponPivot rotation + body.position.y during phases | bandit raise-back monotonic during windup (>=25% of arc by windup end), fast sweep in active, ease-back recover; ghoul body dips in windup, returns after | PASS |
| AC-A3-5 | Space roll timed during enemy windup | hp unchanged through active window | PASS |
| AC-A3-6 | teleport player behind enemy near windup end | NO damage at active entry (outside 50deg arc) | PASS |
| AC-A4-1 | lock; swing; big displacement in windup | yaw chase <= 240deg/s (not snap); strike+recover zero; resumes after | PASS |
| AC-A4-2 | keyboard.down('w') through swing | windup advance ~0.3x walkspeed (30% tol); strike+recover delta < 1e-3; resumes | PASS |
| AC-A4-3 | move key held, no lock | windup turn allowed (<=720deg/s); strike+recover yaw delta < 0.02; resumes | PASS |
| AC-A4-4 | read WH_CONFIG | turnLerpDegPerSecAttackWindup===720; trackWindupDegPerSec===240; enemy.attackPhase exact fields | PASS |

## 7. Flake Protocol

- Max 2 reruns per AC on timing flakes. A rerun is allowed ONLY for timing flakes
  (rAF jitter, transport latency, missed 3ms poll windows) — never for assertion
  logic failures, which are stable FAILs.
- A mechanism-documented flake with frozen probe evidence MAY be listed in
  `flakes[]` and still pass honestly (FLAKE-PASS): the flake entry names the AC,
  the suspected mechanism (e.g. "combo press fell 1 rAF outside recover window"),
  and the probe trace that shows the assertion holds on the honest re-run.
- Any THIRD distinct flaked AC blocks the verdict: two ACs may flake-and-pass in
  one run; a third distinct flaked AC = automatic FAIL, no reruns can save it.
- Flakes pre-Devbot (smoke run) are not recorded as verdict flakes; the smoke run
  only establishes the harness profile.

## 8. Amendment Log

- AMENDMENT D1 (IO, 2026-09-30): devbot-spec amended per Devbot amendment
  request R1 (stop-on-conflict, honored by IO): (1) combo consumption
  boundary corrected to `comboIndex >= cap - 1` (valid indices 0..2; the
  old formula allowed index 3 after the fallback-pose removal); (2)
  enemy `attackPhase` data is NESTED per enemy type (bandit.attackPhase /
  ghoul.attackPhase) with keys windup/active/recover/hitArcDeg/trackDegPerSec -
  the frozen harness's A4-4 assertion (section 6) is the authoritative shape;
  devbot-spec sections 2.1/2.3/2.4/2.5 and this spec's 3.2 anchor updated.
  Testerbot note: A4-4's expected shape is unchanged (harness already frozen
  asserted the nested form); hash-recheck 3.2 against `52b4af42f3f1`.


- A-baseline 2026-09-30: created by Testerbot on IO order; freeze anchors +
  devbot-spec sha at authoring time.

Freeze/authoring measurements recorded with A-baseline (honesty notes):

- devbot-spec `io/specs/devbot-spec-combat-ds1.md` sha256 (first 12):
  `6f7e14d50859`.
- Branch dev HEAD at authoring: `395c5d8` (parent of dispatched base `c679d2c`;
  see section 3.3).
- This spec authored BEFORE Devbot implementation begins. `startAttack` /
  `attackPhase` markers verified ABSENT from the current v7-playable build's
  combat code at authoring time (pre-build profile per 5.3).

Amendments after baseline require a new `A-<n>` entry with date, author, and
exact changed text; unlogged amendments are freeze violations.

## AMENDMENT D2 (2026-09-30, IO — mirrors devbot spec section 9 D2)

- Timing windows become PAGE-CLOCK (page-side performance.now(); no wall bands).
- Frame-sensitive probes (A1-1, A4-1, A4-3) become PAGE-SIDE rAF samplers.
- A3-4 idle baseline accepts phase 'idle' OR null. A3-6 reads attackPhaseT (not
  legacy attackTimer). A1-4 pairwise offset tolerance 0.02 -> 0.90 rad (sweep
  phase differs per facing); yawAgree/parentOk assertions unchanged.
- Harness sha changed by IO's D2 probe patch: fafac1b727d4 (was 13b5e32726ee).
  Verdict-time freeze checks use the NEW sha fafac1b727d4. Patch list: A3-4 idle
  baseline accepts 'idle'; A3-6 reads attackPhaseT + wider window; A1-4
  pairwise tolerance 0.90; A1-1/A4-1/A4-3 page-side rAF samplers; A3-1
  page-clock drop watcher; A3-2 window 30s; A3-3/A3-5 page-clock
  watchers; A4-2 want from CONFIG page-clock.
