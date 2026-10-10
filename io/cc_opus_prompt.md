# TASK: Witch Hunter COMBAT — independent integrity review + implement/refactor (Claude Code, Opus)

You are an independent senior reviewer with FULL implementation authority. Repo: /workspace/witch-hunter, branch dev, HEAD 8f777bb. Working tree may show untracked debris under io/ — that is session scratch, ignore it, do NOT clean or delete it.

## Context

Witch Hunter is a Three.js r185 third-person souls-like prototype (vanilla JS, IIFE/window globals, NO ES modules, NO class syntax in game code, no build tools). The combat stack spans three rounds, all Testerbot-validated and committed:

- combat-ds1-A (02ca0ac): attackPhase FSM (bandit 0.7/0.12/0.8, ghoul 0.45/0.12/0.5, hitArc 50, track 180), windup-only tracking (turnLerpDegPerSecAttackWindup 720, lockOn.trackWindupDegPerSec 240), yawFrame structural group, movement locks (speed*0.3 windup, *0 strike/recover, lunge 0.25 kept), m1-m2-m3 combo chain with buffered presses, armed finisher (3-hit chain -> 3.5s window -> 1.5x), cross-finisher (Q toggle while armed -> 2.0x), corpseFinalY settle, telegraphs (bandit raise-back, ghoul crouch-dip + hop).
- weave-v7 (same commit): focus pool (max 100, tax 1.25), Firebolt (cost 8, dmg 12, speed 40, windup 0.25s, cd 0.3s, range 30, fizzle on windup damage), 5+2 magic belt (Digit1-5 select, empty refusal flash), loadout I/II (Q, s=0.8 busy window, chain reset, armed survives -> cross-finisher), guard break clears armed, HUD focus bar + belt row, spells.js registry.
- whanim2/whanim3 (dc697ce -> 8f777bb): AnimationMixer state machine (idle/walk/run/WH_Attack1/WH_Hit/WH_Death, crossfades 0.18/0.08), skinned instancing via WHSkeletonUtils.clone, weapons mounted on the R_Hand bone socket (whanim3: measured tip-forward orientation), attack-stage seek law (clip time synced to FSM boundary), GLTFLoader LoadingManager URL-modifier converting embedded-texture blob: URLs to data: URIs (CSP-immune texture intake).

Specs of record (read section 9 amendment logs — D1-D5 in devbot-spec-combat-ds1.md, D2-WEAVE in devbot-spec-whproto7-weave.md, A1/A2/A3IO in testerbot-spec-whanim3-swingsight.md — they explain why the code looks the way it does, e.g. socket-first readers, sim-frame counting, SwiftShader dilation rulings):
- io/specs/devbot-spec-combat-ds1.md
- io/specs/testerbot-spec-combat-ds1.md
- io/specs/devbot-spec-whproto7-weave.md
- io/specs/testerbot-spec-whproto7-weave.md
- io/specs/devbot-spec-whanim3-swingsight.md
- Audit basis: docs/planning/60-combat-audit-dark-souls.md
- Status reports: io/reports/2026-10-01-combat-ds1-weave-v7-status.md, io/reports/2026-10-02-whanim3-swingsight-round-report.md

Test harnesses (Playwright sync API, headless chromium --enable-unsafe-swiftshader; they self-manage their servers; sim-frame windows because the box renders 2-11 fps under SwiftShader):
- tests/wh_combat_ds1_validation.py   18 ACs — exit 0 iff 18/18
- tests/wh_v7_weave.py                18 checks — V7 WEAVE: PASS
- tests/wh_v2_verify.py               V2 VERIFY: PASS (26-asset audit, both origins)
- tests/wh_v3_anim_probes.py          V3 ANIM PROBES: PASS
- tests/wh_whanim3_validation.py      6 ACs (includes the floor subprocesses)

Known environment laws (violating these in new code = defect):
- Organic-path validation: real key/mouse events; state-reads via window.WH_DEBUG / WH_GAME are fine; state-mutating page code only as setup acts, never as PASS evidence.
- Vanilla JS law: IIFE + window globals; no ESM; no class syntax; no rigging code outside the committed pipeline.
- Vendored files (prototype/vendor/three.classic.js, gltf-loader.classic.js, skeleton-utils.classic.js) are FROZEN — never edit them.
- GLB assets are bit-frozen; never regenerate or re-export.
- No node/npm on this box; verify JS syntax via python3 -m py_compile on harness files and runtime boots in Playwright (page errors must be zero).

## Assignment

PHASE 1 — INTEGRITY REVIEW (report-only). Read the combat surface end to end: prototype/js/player.js (990 lines), enemy.js (443), game.js (783), CONFIG.js (452), assets.js (317), anim.js (189), spells.js (97), moveset.js (48). Produce a findings table with file:line, severity (BLOCKER/MAJOR/MINOR/NIT), and class:
1. Correctness against the specs of record above (timings, multipliers, windows — any drift between code and spec numbers).
2. Structural integrity: the yawFrame/atkYawOffset sweep (verify the 1.2 rad/frame D2 ruling is respected everywhere), weaponPivot-vs-R_Hand-socket dual paths (stand-in fallback vs skinned), corpse/death settle, NaN poisoning surfaces (probes once shipped dy-as-dz; check no cfg-key mismatches remain).
3. Dead code + stale comments (e.g. setWeapon-era comments that the socket era superseded), duplicated logic, unused CONFIG keys.
4. Robustness: division-by-zero/NaN in the physics paths, race windows in the combo buffer, dispose/teardown gaps on region transitions, error-swallowing try/catch that hides real failures.
5. Refactor opportunities ranked by value/risk: within-file consolidation only — NO cross-file architectural rewrites; NO changes that alter any spec-fixed timing/math value.

PHASE 2 — IMPLEMENT (fix what Phase 1 found, subject to hard rules):
- Fix all BLOCKER + MAJOR findings. MINOR/NIT at your discretion. Refactor per the ranked list where risk is LOW (bars in the harnesses must stay green).
- Every fix must preserve the spec-pinned numbers exactly: FSM windows, multipliers (1.5x/2.0x), tax 1.25, dmg 12, heal 40, chain cap 3, armed window 3.5s, loadout toggle 0.8s, tracking 720/240, lunge 0.25, movement locks 0.3/*0.
- If a fix would change a spec-pinned value or touch vendored files/GLBs/anim clip data, STOP and record it as a proposed amendment instead of implementing.
- Organic-path law applies to any verification you write.

PHASE 3 — VERIFY (mandatory):
1. python3 -m py_compile on every file you touched plus the harnesses.
2. Run IN ORDER and require all green (each takes 4-16 min; use generous timeouts, they self-manage servers on 8791):
   python3 tests/wh_combat_ds1_validation.py   -> 18/18, 0 crashes
   python3 tests/wh_v7_weave.py                -> V7 WEAVE: PASS (18/18, regress=True)
   python3 tests/wh_v2_verify.py               -> V2 VERIFY: PASS
   python3 tests/wh_v3_anim_probes.py          -> V3 ANIM PROBES: PASS
3. Do NOT edit the harnesses to make tests pass. If a failure appears, root-cause it: harness artifact (known classes: fixture bleed between ACs, SwiftShader frame starvation — rerun once before suspecting code) vs real regression (fix your code). Record every adjudication with evidence.
4. Rebuild the single-file bundle: python3 tools/build_v7.py (byte-identity with itself on rerun; must contain CharacterAnim + the intake hook).

PHASE 4 — DELIVERABLES (all mandatory):
- /tmp/cc_review_findings.md — Phase 1 table (file:line, severity, class, verdict each: FIXED / WONTFIX-with-reason / AMENDMENT-PROPOSED).
- /tmp/cc_review_refactor.md — what you refactored and why, with before/after line counts per file.
- /tmp/cc_review_results.md — the four suite outputs' summary lines + exit codes from YOUR runs, plus the build byte-identity check.
- /tmp/cc_review_summary.md — executive summary: total findings by severity, what shipped, what was deliberately left, any proposed amendments needing IO ruling.

HARD RULES:
- Do NOT commit or push. Do NOT git stash/clean/restore. Leave your changes as an uncommitted working tree for review.
- Do NOT touch: sui/, docs/planning/ (read-only reference), art-direction/ (GLBs frozen), prototype/vendor/, tools/ except running build_v7.py, tests/ EXCEPT if a harness has a proven harness-artifact bug that blocks honest verification — in that case document it in /tmp/cc_review_summary.md and make the minimal fix, clearly marked HARNESS-FIX with the evidence.
- Do NOT change spec-pinned numbers (see PHASE 2).
- If the working tree already has uncommitted modifications beyond io/ debris when you start, record them in /tmp/cc_review_summary.md immediately and do not revert them.

Report format when done: paste the executive summary (cc_review_summary.md) as your final message.