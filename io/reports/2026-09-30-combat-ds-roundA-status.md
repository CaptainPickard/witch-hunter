# Round A combat overhaul (P0-1/P0-3/P0-6/P0-4) — status

## STEP 0 — sui econ spike1: RESOLVED, nothing in flight
- Verdict already existed from the earlier gate: PASS 12/12 AC, live e2e pre-authorized skipped (faucet) per spec.
- Landed + pushed: commit 260f453 (feat: wh-econ-spike1), origin/dev up to date. Working tree has zero sui/** entries.

## Commit 1 done — docs: c679d2c
- docs/planning/60-combat-audit-dark-souls.md = verbatim 303-line copy of /workspace/reports/witch-hunter/claude-combat-audit-result.md, committed and pushed-ready (first commit, as ordered).
- Audit fully read. All cited file:line evidence re-verified against the live tree — matches everywhere. Two audit claims clarified for the spec: game.js canDamagePlayer (~417) is dead code (real path goes through damagePlayerFromEnemy → resolveIncomingHit), and the audit's numbers are the source for P0-6 (bandit windup 0.7 / active 0.12 / recover 0.8; ghoul 0.45 / 0.12 / 0.5).

## Audit-vs-tree reconciliation (one finding)
- The audit READ the weave-dirty working tree, and the weave workstream's uncommitted edits sit in the same files Round A touches (player.js, game.js, CONFIG.js). Building on a clean tree would desync the audit and the harness.
- Resolution: Round A is built against the weave-dirty tree. Baseline frozen pre-dispatch: 16 entries hashed (5 docs + 4 js + index/style + 2 io/specs-weave + builds/v7-playable.html + spells.js + tests/wh_v7_weave.py + tools/build_v7.py), table at /tmp/wh-weave-baseline-freeze-20260930.txt, embedded in both ds1 specs and the dispatch contexts.

## Round A spec — written and committed-ready alongside validator work
- io/specs/devbot-spec-combat-ds1.md: all four fixes (P0-1 yawFrame structural fix w/ per-line anchor list, P0-3 startAttack + recover-boundary chain consumption, P0-6 enemy attackPhase state machine per audit numbers + telegraphs from phase, P0-4 stage-gated turn/movement/lock-tracking with data-carried rates), 16 ACs all organic-path (real F/LMB/Space events; direct state mutation tests banned), hard fences: no sui/docs/io edits, no git writes by children, weave harness untouched, rebuild via tools/build_v7.py, vanilla-JS style law.
- Gate order: Testerbot dispatched FIRST (deleg_e3f816d8) to author io/specs/testerbot-spec-combat-ds1.md + tests/wh_combat_ds1_validation.py. Devbot dispatch waits for my review of both artifacts.

## Testerbot authoring: run trail (3 dispatched, 2 dead)
- Run 1 (glm-5.3): died reading budget + provider timeouts (150s x3), delivered ZERO files, tree untouched.
- Run 2 (glm-5.3): identical failure: 1 API call, 90s timeout x3, iteration cap, zero files. glm-5.3 deemed model-degraded.
- Run 3: model override gpt-5.6-sol attempted first, rejected by delegation (no OPENAI_API_KEY for openai-api lane), then gpt-6-sol - both 401'd instantly (credential lane, not model).
- NICKO ORDER 2026-09-30 (STOP): do not silently switch profile models to work around API limits or timeouts. When a lane fails, STOP and surface to Nicko. Testerbot config was reverted to glm-5.3/ollama-cloud per that order. Standing rule saved to memory and skills.
- Run 4 (NICKO DIRECTIVE 09-30): Testerbot stays glm-5.3/ollama-cloud (no config change); dispatch through the normal gate; blast radius embedded in dispatch context (43 nodes changed across exactly the 5 target files, 0 additional files impacted within 2 hops, runtime coupling via window globals only). Chunked-write discipline retained.

## Testerbot run 4: DELIVERED (NICKO directive executed)
- Normal gate, glm-5.3/ollama-cloud unchanged, blast radius in context: 21 calls, 519s, both files written, smoke-run 18 executed / 2 PASS / 16 FAIL / 0 crashes / exit 0 - exactly the expected pre-Devbot profile.
- IO independent verification PASSED: sha256 match on both files (e729ddabd685 / 13b5e32726ee), py_compile OK, 18 def ac_* functions, 77 check() call-sites, zero forbidden state-writes in the harness (grep sweep), organic-path ACTs only (mouse/keyboard + sanctioned live-handle displacement), IO's own re-run reproduced 18/2/16/0 zero-crash, devbot-spec anchor re-measured 6f7e14d50859 (matches Testerbot's freeze), spec semantics checked line-by-line against the devbot spec (verdict protocol, honest-partial, flake rules = 2 reruns then block, amendment-log path).
- External git event resolved: HEAD advanced to 395c5d8 (04:18, Meshy-key hygiene fix from the Sep-29 world-audit trail - NOT a gate child). Benign for Round A; recorded in Testerbot spec section 3.3 by Testerbot; Devbot dispatched against 395c5d8.
- Deploy-key rot recurred: git fetch failed 'Permission denied (publickey)' until origin URL re-pointed to the host alias (github-witch-hunter:) AND GIT_SSH_COMMAND points at the IO profile ssh config. Standing fix for witch-hunter pushes.

## Devbot run 1: amendment stop (gate working as designed)
- Devbot (gpt-6-sol) STOPPED before any edit on two spec conflicts: (1) P0-3 consumption boundary `>= cap` allowed comboIndex 3 (undefined move after fallback removal) -> ruled `>= cap - 1`; (2) spec 2.1 sibling attackPhase vs 2.4 per-cfg read contradiction -> ruled NESTED per-type shape with hitArcDeg/trackDegPerSec keys (Testerbot's frozen A4-4 assertion is the authoritative shape).
- Zero files touched by Devbot: census 20, HEAD 395c5d8, all 16 freeze hashes intact. Amendment-stop honored, not punished.
- AMENDMENT D1 logged in BOTH specs: devbot-spec 52b4af42f3f1 (sections 2.3/2.4/2.5 + 3 + 9), testerbot-spec e185751fdae0 (3.2 anchor updated + section 8 entry). Harness stays 13b5e32726ee (untouched).
- Devbot re-dispatched (deleg_99b013de) with D1 summarized in context.

— IO