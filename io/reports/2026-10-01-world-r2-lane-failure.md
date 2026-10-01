# World R2 lane failure — 2026-10-01 (auto-finisher job 2c7556f7f609)

## What happened

The Testerbot authoring lane died 3 times in a row this tick while trying to
author `tests/wh_world_r2_validation.py`:

1. ** deleg_6808bae4 (08:14-08:19Z)** — dispatched with "read your valspec +
   write the harness" framing. Wrapper timeout at 420s killed the child
   mid-read (last activity 08:17:08Z, no file written, no edits).
2. ** deleg_5a70e50e (08:21Z)** — retry with the full method table inlined so
   the child needed zero reads. Child API call died provider-side
   ("non-streaming API call timed out after 90s x3 retries", 0 tool calls,
   0 tokens). NOT a prompt-size failure per se; the provider timed out
   before the child's first LLM call completed.

Per mission law (Testerbot lane fail = STOP everything, no fallbacks, no
model switching, leave the job running to retry next hour), the pipeline
stopped here. This report is required output of that rule.

## What DID land this tick (real, verified)

- Anim-gate condition went TRUE: dev @ dc697ce (whanim2) pushed to
  origin/dev; guarded paths clean. Asset batch tail confirmed closed
  (B1/B6/B2/B3/B-tex all committed on feat/world-visuals; B4/B5 parked).
- feat/world-visuals rebased onto dev: merge commit 26e7a60 (clean, no
  conflicts) in rebuilt worktree /tmp/wh-worldfeat (after /tmp wipe killed
  the old worktree dir).
- Gate specs committed (46454c5): io/specs/devbot-spec-wh-world-r2.md +
  io/specs/testerbot-spec-wh-world-r2.md (Testerbot-authored, 350 lines,
  8 amendment notes — includes standIn-vacuous note and write-free fog-mask
  variant for L10).
- **Devbot implemented R2 completely** (chunks A+B, uncommitted at the
  time): ~208 insertions across CONFIG.js / game.js / assets.js — relight
  (P0-3: hemi-only fill, moon dir light, player lantern w/ flicker,
  Neutral tone mapping, exposure 1.15) + light pool (P1-8: 4 PointLights +
  flame cards + socket registry + handoff fade + getLightPool/
  getLightSockets hooks + 2 new socket props banditCampfire/
  lanternWaymarker in region B).
- Preservation: local-only commit **8765ded** on feat/world-visuals
  ("WIP LOCAL ONLY, NEVER PUSH"). It is NOT pushed. Branch tip is this WIP
  commit; next tick must treat it as unvalidated code, not landed work.

## Why the lane died (assessment)

- The 420s wrapper cap on delegate_task is too tight for "read 350-line
  spec + author 500+ line harness" as one child task. Chunk A/B Devbot
  children succeeded only when IO pre-verified and inlined every anchor.
- The successful pattern (chunk A 137s, chunk B 267s, valspec authoring
  334s, all under the cap) = zero-read, write-only dispatches with the full
  content plan inline.
- The harness authoring task is the remaining big write. Next tick should
  split it the same way: Testerbot-child writes ONLY the harness skeleton
  (one write_file from an IO-inlined method table), then a second child or
  the same child next tick runs it against the live worktree and produces
  the verdict JSON.

UPDATE 09:46Z - FIFTH death, identical provider signature. Dispatch
deleg_c0b7cc03 (09:42-09:46Z, 277s) was the runbook-chunked write-only
authoring task: ~14KB inline method table, zero reads permitted, single
write_file deliverable, budget < 5 min. The child's model API call died
provider-side ("Non-streaming API call timed out after 90s with no
response, 3 retries") with ZERO tool calls and ZERO tokens - the child
never got its first LLM call through. The dispatch shape matched the
historically successful pattern (chunk B was 267s, valspec authoring
334s), so this is provider degradation for subagent non-streaming calls
this hour, not a prompt-size issue. Harness file confirmed absent after
the dispatch (tests/wh_world_r2_validation.py does not exist). Pipeline
stays stopped per mission law; no model switch, no fallback. Job remains
armed for the next hourly tick.

UPDATE 10:58Z - SIXTH death, identical provider signature. Dispatch
deleg_1199c263 (10:53-10:58Z, 277s) again the runbook-chunked write-only
authoring task: ~12.4KB inline method table, zero reads permitted, single
write_file deliverable. Child's first LLM call died provider-side
("Non-streaming API call timed out after 90s with no response, 3 retries"),
zero tool calls, zero tokens, harness file confirmed absent in worktree
after the dispatch. Same shape as deleg_c0b7cc03. Now 3 consecutive
provider-timeout deaths on this exact dispatch shape.

Running total: 6 authoring-lane deaths (2x wrapper timeout 420s,
4x provider 90s non-streaming timeout). Parent-session provider calls
(streaming, this job's own model) work fine all hour - the instability
is specific to the delegation child path on glm/ollama-cloud.
Dispatch log: /root/.hermes/profiles/io/cache/delegation/live/deleg_1199c263/task-0.log

## Next tick runbook (pick up here)

1. Do NOT re-run R2 implementation — 8765ded holds it. Verify worktree +
   branch state first (worktree may need re-add from the branch).
2. Dispatch Testerbot stage 1 as a write-only chunk: author
   tests/wh_world_r2_validation.py from the method table (now also embedded
   in this report's companion: the valspec section list). Budget it well
   under 420s: forbid all reads except one py_compile + one grep.
3. Stage 2 (separate tick if needed): run the harness
   (WH_R2_PORT=8792, python3 tests/wh_world_r2_validation.py), capture
   verdict JSON, then IO commits harness + verdict + R2 docs together
   (surgical: harness/tests + io/specs already in; verdict + report).
4. If Testerbot returns PASS: commit message drops the WIP marker via a
   follow-up "validated" commit on feat/world-visuals; push feat branch
   only (never dev). If FAIL: retune protocol per valspec (one numeric
   retune pre-authorized), else STOP and keep job armed.
5. R1 floor harness must run green (A1-A8) before PASS is final.

— IO, auto-finisher job 2c7556f7f609, 2026-10-01 08:30Z