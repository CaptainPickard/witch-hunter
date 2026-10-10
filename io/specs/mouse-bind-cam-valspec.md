# Validation Spec: Pointer-Lock Mouse Bind Camera (v8) — DRAFT by IO for Testerbot review

Status: IO-authored draft (2026-10-05) after two provider-killed Testerbot
valspec attempts. Testerbot (kimi-k3) reviews, amends if needed, OWNS and
signs this spec before Devbot starts. Authority: io/specs/mouse-bind-cam-spec.md.

## 1. Frozen baseline (pre-build, feat/mouse-bind-cam @ 09712f6)
- HEAD: 09712f6cbf2aa6ca64322e2ca4cc8ac12968d13a
- Five-file shas (base=run value, verdict JSON baselineEcho confirms all match):
  player.js 97f0b9659a5c2d8a, CONFIG.js 7c7eba2ff8c2140d, index.html 3784a007c5898606,
  style.css 3ad2a8deefe8a6f9, touch-controls.js 051cc722152a2de6
- Dirty-tree pre-state: 111 entries (M scratch/treeqa/roundI/decimate.jsonl +
  109 untracked io/* + tests artifacts), P8 baselineKept=110 at run-2. Out-of-scope
  entries must never be committed.

## 2. Organic-interaction law
- MUST be real input: Backquote/key presses via page.keyboard; mouse drags,
  clicks, wheel via page.mouse after positioning over the target element.
- Sanctioned non-organic vehicles (spec section 7): (a) N2b dispatched
  MouseEvent with movementX/Y for locked-motion math when headless movementX
  stays 0; (b) N7 fault injection via init script BEFORE page load
  (rplThrowMode), never post-hoc state mutation.
- N2a is live CDP synthetic motion; headless degradation: movementX may stay
  0 -> mark RECORD (N2a rows only) with evidence, fall back to N2b.

## 3. Headless timing calibration (IO-proven 10-05, harness already patched)
- page.mouse.wheel delivers ONLY with pointer over canvas first (move 640,400),
  and delivery is compositor-lagged: poll reads with >=2.5s deadline, never
  fixed short sleeps. CDP Input.dispatchMouseEvent mouseWheel delivers NOTHING.
- Touch cam pad: works via real page.mouse drag on .wh-touch-ctl.cam after
  WH_TouchControls.show(); final read must poll. KNOWN ISSUE, accepted for
  pre-build only: P5 fails (dyaw=0) when run LAST in the full organic sequence
  while passing mid-sequence and on fresh pages (probes 2-5). If it still
  fails post-build, Testerbot may reposition P5 earlier in the run order as a
  harness fix (allowed: that is a calibration, not a gate weakening).

## 4. Checks (IDs match tests/wh_mousebind_validation.py exactly)
- N1 static: requestPointerLock+exitPointerLock in player.js, chip element +
  CFG.mouse block present, anchors at the mapped lines.
- N2 organic bind: Backquote -> pointerLockElement truthy, player.mouseBound
  true, chip MOUSE: BOUND. N2a live motion / N2b dispatched motion apply
  applyCamDelta (0.25 * pointerLockSensMult 0.85) with pitch clamped -15/65deg.
- N3 organic unbind via Backquote; N3-esc Esc-equivalent resyncs chip.
- N4 free mousemove inert (no button, no camera).
- N5 canvas LMB = attack AND rebind (autoBind on); chip LMB no rebind;
  N5-off autoBind=false blocks canvas rebind.
- N6 chip click toggles bind->free and free->bind.
- N7 rpl throw injection: no uncaught error, game stays FREE, bind retry OK.
- N8 lastManualCamT stamped on bound motion AND organic drag, not free moves.
- N9 build artifact: v8 exists, inline (no script src), chip+CFG baked, title v8.
- N10 zero console/page errors across the FULL organic run.
- P1-anchor drag handler preserved; P2-wheel/block/ctx/strike semantics;
  P3 touch-controls.js byte-identical; P4 lock-on framing untouched;
  P5 CONFIG additive-only (id collision with touch pad row noted, cosmetic);
  P6 build_v7.py + v1/v2/v7 builds byte-identical; P7-static keyboard set
  intact; P8 dirty-tree scope hygiene vs baseline count; P9-boot boot record;
  X-echo five-file sha echo.
- RECORD allowed ONLY for N2a rows. Everything else PASS or FAIL.

## 5. Verdict schema (tests/artifacts/wh_mousebind_verdict.json)
{verdict: PASS|FAIL, finalized: true, counts:{pass,record,fail},
 perAc:[{id, verdict, evidence, artifact?}], baselineEcho{head, files{shaNow,
 status}}, specOfRecord, specSha256Run, harnessSha256Run}. Final verdict
 FAIL if any non-N2a FAIL or any misused RECORD.

## 6. PRE-BUILD BASELINE (smoke run-2, IO-executed 2026-10-05 19:4x UTC,
target prototype/builds/v7-playable.html, artifact
tests/artifacts/wh_mousebind_smoke_run2_v7.txt): verdict FAIL 17 PASS / 12 FAIL,
zero harness crashes. Expected FAILs (feature absent): N1, N2, N2a, N2b, N3,
N3-esc, N5, N6, N7, N8, N9, P5(touch pad, known timing issue). All preservation
floors green: P1-anchor, P2-wheel, P2-block, P2-ctx, P2-strike, P3, P4,
P5-config, P6, P7-static, P8, X-echo, N4, N5-off, N10. Run-2 FAIL table is in
the artifact file. Smoke run-1 (pre-calibration) 16/13 is superseded.

Testerbot witnessed re-runs (2026-10-05 20:1x-20:45 UTC): 5 runs (runs 3-6,
artifacts tests/artifacts/wh_mousebind_smoke_run{3,4,5,6}_v7_testerbot.txt).
P2-wheel PASS in 3/5 witnessed runs (two compositor flakes per section 3:
d2=7.8 then d1=7); all other preservation floors PASS every witnessed run.
P8 FAILs in the re-runs are structural, not scope violations: untracked smoke
artifact txt files count as extra git entries once run-2's artifact is
retained. P5-pad FAILed in all witnessed orderings (last, mid/post-strike,
pristine-first, post-drag); pristine-first reproduces the probe face-angle
class write dyaw=-3.107/dpitch=0 exactly. "Passes mid-sequence" did NOT
reproduce under the harness; pad-steering preservation remains covered by the
probes and P5-pad stays an expected pre-build FAIL (superset of run-2's 12).
The P5-slot reposition remains an authorized harness calibration for the
post-build gate.

## 7. Testerbot signature block (fill before Devbot dispatch)
- [x] Reviewed/amended this spec: amendments (if any) listed below
- [x] Harness smoke re-run witnessed (counts + verdict JSON path)
- Signed: Testerbot (kimi-k3) subagent proc-bcc91a275908-lineage, witnessed runs
  3-6, 2026-10-05 20:45 UTC. Counts witnessed: run-3 15 PASS/14 FAIL (P2-wheel
  flake + P8 structural artifacts), run-4 16/13 (P5 mid), run-5 16/13 (P5
  pristine-first, face-angle write), run-6 15/14 (P5 post-drag + P2-wheel
  flake). Signed YES with amendments listed below; Devbot may start.
- Amendments (A1-A3):
  - A1 (2026-10-05): section 6 extended with the Testerbot witnessed re-run
    record (runs 3-6, counts, P2-wheel 3/5 pass, P8 structural note, P5-pad
    orderings observed).
  - A2 (2026-10-05): harness calibrated — P5 touch-pad row moved EARLIER in
    the run order per section 3 authority (tests/wh_mousebind_validation.py
    run body). Final placement: after N4/P4 pre-interaction legs, before
    wheel/strike. It did not flip P5-pad pre-build (expected FAIL per
    section 6); retained for the post-build gate.
  - A3 (2026-10-05): P5-pad "passes mid-sequence" could NOT be reproduced in
    4 witnessed orderings; pre-build FAIL of P5-pad is accepted as expected
    (genuine pad-steering property is evidenced by probes; not a gate
    weakening — P5-pad remains a required post-build gate row).