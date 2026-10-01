# whanim2 — Testerbot Independent Validation (consolidated)

Round: whanim2 (animation runtime intake) | Repo: /workspace/witch-hunter @ HEAD d7e0b4127afe (no commits by build or validation)
Validation runs: Testerbot run 1 (aborted pre-work, port incident — no processes killed, lesson logged), run 2 (deleg_c1a4c947), run 3 (deleg_0d495977), plus IO-completed residual gaps under Testerbot-authored procedures.
Spec pair: io/specs/devbot-spec-whanim2-runtime-anim.md + io/specs/testerbot-spec-whanim2-runtime-anim.md (amendments D-A11-1, D-A12-1, D-A12-2, D-A13-1, D-A7-1 logged inline).

## Per-AC verdicts

| AC | Verdict | Evidence (path) |
|----|---------|-----------------|
| A1 hygiene set-difference | PASS | /tmp/tb_a1_result.json — 9 modified all Devbot-scope, extra_untracked=[], out_of_scope=[] |
| A2 frozen 20 GLB sha256s | PASS | /tmp/tb_a2_result.json — all_ok true, 10 source + 10 rigged bit-identical |
| A3 vendor + script order, no ESM | PASS | /tmp/tb_a3_static.json — skeleton-utils.classic.js vendored; order correct; esm_matches empty |
| A4 clip manifest per character | PASS | run-2 transcript 05:54:27 (A3/A4/A5 all pass) + Devbot self-run per-character clip audit |
| A5 durations (Attack1 0.5s, Hit 0.333s) | PASS | /tmp/tb_a7_final.json (clip_duration 0.5 == attackDuration_cfg 0.5) + A4 evidence |
| A6 walk phase-sync | PASS | /tmp/tb_dynamic_a6_a14.json A6 — phase_err 9.75e-13 %, measured 6.0 m/s vs 6.0 target, crossfades witnessed, return-to-idle |
| A7 strike-boundary + damage coincidence | PASS (D-A7-1) | /tmp/tb_completion_a7_a13.json — seek-law delta 0.025 ≤ 0.03 tol, timeScale 1 across all samples, stage law exact at 0.15s; organic: stage_seq [null,windup,strike,recover,null], damage_all_in_strike TRUE, windup_no_damage TRUE (A10_hit: hp 70→36 inside strike). NOTE: natural un-seeked flow reads clip 0.200 at strike start (windup tail continuation) — cosmetic, deferred feel item, not a blocker |
| A8 enemy windup spans | PASS | /tmp/tb_a8_final.json bandit (ts 0.1786 exact, span ok, wAttack=1 during windup) + /tmp/tb_ghoul_a8.json ghoul (0.4499 vs 0.45, ts 0.2778 exact, phase_seq correct) + run-2 transcript 06:17:56 |
| A9 weapon socket drift | PASS | Devbot resume checkpoint A9_socket: max_local_drift 0.0, socket_parent R_Hand, hand_world_travel 2.446 (real wrist motion) — mechanism probe; run-2 transcript 06:00:52 "A6/A9 PASS" |
| A10 death clamp + corpse settle | PASS | run-2 transcript 06:06:09 (death clamped 1.2s, corpseY 0.01, y frozen, no restarts) + /tmp/tb_completion_a7_a13.json A10_hit (WH_Hit weight seen, returned to locomotion, enemy alive) |
| A11 body-bob retired + props static | PASS | /tmp/tb_a11_final.json — prop_y_drift 0.0 over 127 samples/1.95s sim; body holder y-range 0.0 idle AND walk; walk clip advances (walk_weighted true) while holder static — amendment intent proven |
| A12 four regression suites | PASS | /tmp/tb_a12_v2.log (V2 VERIFY: PASS + asset audit 26/26 both origins), tb_a12_v3.log (V3 ANIM PROBES: PASS both origins), tb_a12_ds1.log (18/18, verdict PASS), tb_a12_weave.log (AC14 echo PASS) — master log tb_a12_master.log |
| A13 console clean + all-URL asset audit | PASS | /tmp/tb_completion_a7_a13.json A13 — root 26/26 200 + zero errors, proxy (/witchhunter) 26/26 200 + zero errors (D-A13-1 live-count rule satisfied) |
| A14 perf guard same-harness | PASS | /tmp/io_a14_perf.json — same harness both trees; post avg 268.56ms vs pre 220.32ms (SwiftShader software rendering); regression +21.9% ≤ 25% gate = PASS. Window variance high (software GL); relative same-harness delta is the gate per valspec |

## Screenshot QA (§4) — IO-executed per Testerbot protocol

Directory: tests/artifacts/whanim2-qa/{human-hunter-male,undead-ghoul-male}/ (24 frames, REST/Walk 8+23/Attack 5+9/Death 36, front+side, rendered from the rigged GLBs + VERIFY PASS per render).

- Undead ghoul: attack windup f5 = genuine articulated windup (arm raised high overhead, torso coiled/weight-shifted, stable planted base) — vision reads it as "dynamic, asymmetrical... windup of an attack". Walk side f23 = real stride (front leg planted, rear leg heel-lifted ball-of-foot contact, knee bend). PASS.
- Human hunter: walk side f23 = real stride (lead leg planted heel-strike, trailing leg heel raised high with knee bend — "wide, active walking gait"). Attack windup f5 = arm raised high with grip pose + torso coil, no T-pose, no mesh collapse, draping intact. Front walk frames read near-neutral (the stride is depth-wise in perspective at 8/23 = contact/passing phases) — pixel-objective diff confirms movement (6.8% pixels differ bbox around legs/torso). PASS with cosmetic note.
- Walk pair objective diffs: human 6.8%/5.9%, ghoul 6.2%/6.1% pixel-change between paired frames — limbs demonstrably move.
- No T-pose or mesh collapse in any frame (all 24 rendered + vision-read).

## Honest-partial arithmetic (valspec §3)

Zero FAIL-class ACs. Zero hygiene breaches. Zero fabricated reads — every verdict cites an on-disk evidence file or verbatim transcript line. A7 carries one documented cosmetic note (windup-tail continuation in un-seeked natural flow). A14 passes on the gate's own relative-same-harness terms with the software-rendering caveat recorded.

## Secrets clean

Positive-control scan (3/3 planted patterns fire) + in-repo scan = 0 matches (run-3 transcript 06:50:31, verbatim in transcript). tb_dbg_reg.json (stray platform state, not evidence) excluded from all citations.

## Suite counts

- wh_v2_verify: PASS (26 asset fetches 200 both origins)
- wh_v3_anim_probes: PASS (both origins, zero console errors)
- wh_combat_ds1_validation: 18/18 checks, verdict PASS
- wh_v7_weave: 18/18 incl. AC14 regression echo, PASS

## VERDICT

```json
{
  "round": "whanim2",
  "per_ac": {
    "A1": "PASS", "A2": "PASS", "A3": "PASS", "A4": "PASS", "A5": "PASS",
    "A6": "PASS", "A7": "PASS", "A8": "PASS", "A9": "PASS", "A10": "PASS",
    "A11": "PASS", "A12": "PASS", "A13": "PASS", "A14": "PASS"
  },
  "evidence": [
    "/tmp/tb_a1_result.json", "/tmp/tb_a2_result.json", "/tmp/tb_a3_static.json",
    "/tmp/tb_dynamic_a6_a14.json", "/tmp/tb_completion_a7_a13.json",
    "/tmp/tb_a8_final.json", "/tmp/tb_ghoul_a8.json", "/tmp/tb_a11_final.json",
    "/tmp/tb_a12_master.log", "/tmp/tb_a12_v2.log", "/tmp/tb_a12_v3.log",
    "/tmp/tb_a12_ds1.log", "/tmp/tb_a12_weave.log", "/tmp/io_a14_perf.json",
    "/workspace/witch-hunter/tests/artifacts/whanim2-qa/"
  ],
  "suite": {"checks_passed": 70, "checks_failed": 0},
  "regressions": {"v2": "PASS", "v3": "PASS", "ds1": "PASS 18/18", "weave": "PASS 18/18"},
  "secrets_clean": true,
  "verdict": "PASS",
  "notes": "A7 windup-tail cosmetic continuation deferred to feel round per D-A7-1; A14 +21.9% under SwiftShader ≤25% gate; screenshots show real stride/windup articulation on both species; all assets bit-identical to frozen hashes."
}
```

Ready for IO commit + push.