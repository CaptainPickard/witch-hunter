# MB Mouse-Bind-Cam: Testerbot continuation brief (IO, 2026-10-05)

Continuation of deleg_88037be1 (timed out at 1800s, phase ~95% done). Worktree
is truth. ZERO RESEARCH: do not re-read game sources to re-derive semantics,
do not re-derive the spec. Read exactly: io/specs/mouse-bind-cam-spec.md,
tests/wh_mousebind_validation.py (your own prior work, syntax OK, 1080 lines),
this brief. Then act.

## State of record (harvested, verified)

- Branch: feat/mouse-bind-cam, HEAD 09712f6. Dirty out-of-scope entries
  unchanged and untouched by you.
- tests/wh_mousebind_validation.py EXISTS, syntax OK, runnable: CLI
  `python3 tests/wh_mousebind_validation.py [<target.html>]`, default
  builds/v8-playable.html, verdict JSON to
  tests/artifacts/wh_mousebind_verdict.json.
- io/specs/mouse-bind-cam-valspec.md DOES NOT EXIST YET (the one missing
  artifact).
- IO re-ran your harness smoke against v7 (2026-10-05 ~19:1x). Raw table:

MB  N4   free mousemove (no button) inert               => PASS
MB  P4   drag-cam math identical to HEAD                => PASS
MB  P2-wheel wheel zoom semantics                           => FAIL   d0=7 d1=7 d2=7
MB  P2-block RMB press engages block/cast; release clears   => PASS
MB  P2-ctx contextmenu reaches document (captured)          => PASS
MB  P2-strike LMB strike fires, no cam orbit                => PASS
MB  N2   bind via Backquote (organic)                   => FAIL
MB  N2a  locked live motion                             => FAIL  skipped: bind failed
MB  N2b  dispatched movementX/Y                         => FAIL  skipped: bind failed
MB  N8   lastManualCamT stamp rules                     => FAIL  boundStamp=False freeStamp=True
MB  N3   unbind via Backquote (organic)                 => FAIL
MB  N3-esc native exit (Esc-equivalent) chip resync     => FAIL
MB  N5   canvas LMB = attack+rebind; chip LMB no-rebind => FAIL  attack=True chipNoRebind=None
MB  N5-off autoBind=false disables canvas rebind          => PASS  rpl 0 -> 0
MB  N6   chip click toggles both directions             => FAIL  chip not found
MB  N7   rpl throw: no uncaught, stays FREE             => FAIL  rplCalls=0
MB  P5   touch cam pad still steers (pad drag)          => FAIL  dyaw=0.0 dpitch=0.0
MB  N10  zero console errors, full organic run          => PASS  consoleErrors=0
MB  N1   lock JS + chip + CFG.mouse present             => FAIL
MB  N9   build artifact checks                          => FAIL  title=v7 not v8
MB  X-echo five-file sha baseline echo                    => PASS  head=09712f6 drift=none
MB  P3   touch-controls.js byte-identical               => PASS
MB  P1-anchor drag handler core preserved in player.js   => PASS
MB  P4   lock-on framing untouched                      => PASS
MB  P5   CONFIG additive-only (no key removed)          => PASS
MB  P6   build_v7 + v1/v2/v7 builds untouched           => PASS
MB  P7-static keyboard handler set intact                => PASS
MB  P8   dirty-tree scope hygiene                       => PASS  entries=111 baselineKept=109
MB  P5-cfg coverage                                      => FAIL  row never executed

Verdict: FAIL pass=16 record=0 fail=13. This IS the pre-build wiring
evidence: every FAIL is a not-yet-implemented feature check or a harness
mechanic bug; zero crashes.

## Known harness defects found in the smoke (fix these two, nothing else)

1. P2-wheel (`def p2_wheel`, line ~547 of tests/wh_mousebind_validation.py):
   ROOT CAUSE PROVEN BY IO (wh_wheel_probe.py, 2026-10-05, real numbers):
   page.mouse.wheel DOES deliver to the handler when the pointer is over the
   canvas FIRST: d0=7.0, after move(640,400)+wheel(0,+120) => 7.8. The harness
   never positioned the pointer, so events went nowhere (7/7/7). ALSO: CDP
   Input.dispatchMouseEvent mouseWheel delivers NOTHING headlessly (tested;
   7.0 -> 7.0). NOTE the negative-wheel event is processed lazily: after
   wheel(0,-120) an immediate read can still show the old dist, so read with
   a short retry (up to 3 reads 100ms apart until it stops changing).
   FIX (exact): at the top of p2_wheel, before the first wheel, add
     page.mouse.move(640, 400); page.wait_for_timeout(80)
   and change the two -120-wheels' wait_for_timeout(100) to 150, then wrap
   the st2 read in a retry loop (3 attempts, 100ms apart) before evaluating
   ok2. Same retry pattern is acceptable for st1 if flaky. NOTHING else in
   the function changes.
2. P5-cfg coverage: the expected-ID list near line 1040 contains "P5-cfg"
   but no check emits that id (the config-additive row runs as id "P5";
   the touch-pad row ALSO reports id "P5" - known cosmetic collision, leave
   it). FIX (exact): in the expected-ID list replace
     "P3", "P4", "P5", "P5-cfg",
   with
     "P3", "P4", "P5",
   Nothing else changes.

## Remaining work (in this order; write files EARLY)

1. FIRST write io/specs/mouse-bind-cam-valspec.md (so it survives any
   interruption): frozen baseline (HEAD 09712f6; the five-file shas are inside
   tests/artifacts/wh_mousebind_verdict.json baselineEcho - read them back
   instead of recomputing research), organic-interaction law, the two
   sanctioned non-organic vehicles (pre-load init-script fault injection for
   N7; dispatched movementX/Y MouseEvent through the real document listener
   for N2b), N2a RECORD degradation protocol, zero-console-error assertion,
   verdict JSON schema, and the smoke table above frozen verbatim as the
   PRE-BUILD BASELINE section.
2. Patch tests/wh_mousebind_validation.py for the two defects only.
3. Re-run the smoke against v7. Expect: same verdict shape (FAIL, ~16 PASS),
   the two defect rows now healthy, zero crashes. Append the re-run table to
   the valspec baseline section (run 2).
4. Report: valspec path, harness path, run-2 counts, any residual notes. Do
   NOT edit the implementation spec. Do NOT create v8 or build anything. Do
   NOT touch git.