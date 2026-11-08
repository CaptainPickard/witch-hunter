# CC-EN1 Validation Report — Wilderness Encounter Tables V1

**Validator:** Testerbot | **Date:** 2026-11-08 | **Worktree:** /tmp/wh-worldfeat (branch feat/world-visuals, HEAD 45c0299, Devbot changes uncommitted)
**Valspec:** /tmp/wh-worldfeat/io/specs/cc-en1-valspec.md | **All checks re-run independently; Devbot's report used only as claim list.**

## Verdict table

| Check | Verdict | Blocking | Evidence |
|---|---|---|---|
| V-1 Syntax (CONFIG/encounters/game) | PASS | — | `node --check` exit 0 on all three |
| V-2 Diff surface | PASS | — | git status: 4 modified prototype files; untracked = spec×3 + encounters.js + scratch/cc-en1-probe/; game.js +2 WH_ENCOUNTERS lines (L3078 init, L3615 tick); index.html +1 encounters.js script tag; region-manager diff empty |
| V-3 probe_config_baseline.js post | PASS | — | CENSUS OVERALL PASS (13/13 PASS lines) |
| V-4 probe_weight_law.js + re-sum | PASS | — | WEIGHT-LAW PASS; independent re-sum: weights [0,0.28,0.12,0.15,0.25,0.2] len 6 == night(5)+1, sum == 1.0, w[0]==0, day rows == family 3 only |
| V-5 g1..g8/p1..p9 anchors + probe_gates_matrix.js | **FAIL (non-blocking, instrument flake)** | no | g1..g8/p1..p9 anchors ≥1 each; g1..g5 block-alone legs PASS deterministically; debugMute honored (0 toasts in 200 ticks w/ debugForce+debugMute); probe's debugForce happy leg passes ~30% of runs (3/10 in Testerbot's sweep) — flaky by construction, see deviation note |
| V-6 probe_transient_law.js | PASS | — | TRANSIENT-LAW PASS (guard line present, 0 raidMember dead rows recorded, 1 stock row recorded, raidMember=true assigned at spawn) |
| V-7 Art law greps | PASS | — | zero `new THREE.*` geometry/Mesh/material/light constructions (grep no match); exactly one `function toast` (L242); no toastWarn/toastEnd/other toast identifiers; debugMute honored at L243 |
| V-8 RNG law | PASS | — | exactly 4 Math.random sites: L92+L94 (pickSeat angle+band), L205 (spawnParty bearing), L269 (tick roll); zero in memberClear; zero in CONFIG |
| V-9 Build determinism | PASS | — | `python3 tools/build_v8.py` run TWICE; both sha256 = c745c5455f2f9a2cab93d4974d0120a1061612572f0a66222c7c441b948e27e0 (== Devbot's reported); bundle greps CC-EN1 ≥2, window.WH_ENCOUNTERS ≥4 |
| V-10 Worktree surface | PASS | — | `git diff --cached --name-only` empty; no staged files |
| V-11 region-manager.js sha | PASS | — | sha256 c7e31520f775b2e07388db710d079be35a3810b5ab104e90ab64cd8bfe1bc2ee — unchanged (leading c7e31520775b2e as spec'd) |

## §6 IO instrument-repair review

All three §6 repairs verified against normative law; none exceed it:

1. **probe_config_baseline pending-keys assertion** (`== [F2,F4]` → `>= 1 && F1/F2 present`): spec EN1-4 grew the census to add F6/F7 pending keys after the probes were authored; code's regionB pending = [F2-tainted-glade-wailcaster, F4-road-life, F6-riches, F7-wanderers], regionC pending = [F1-lair-pair, F6-riches, F7-wanderers]. Repaired assertion is a superset-check of the normative law (≥1 lawful pending key incl. F2/F1). Within law.
2. **probe_transient_law dead-state**: repair lets a raidMember row that is *dead-before-record* still pass provided regionStates never gains a raidMember corpse row. Normative law = transient corpses never recorded. Verified: 0 raidMember rows in regionStates, 1 stock row recorded. Within law.
3. **probe_gates_matrix happy-leg fixture (40,-45) → (55,-70)** + comp-splitting compare: valspec itself pins the 50 m fire exclusion (g5); (40,-45) sat 38.15 m inside the exclusion so the pre-amendment fixture could never be green. (55,-70) is 55.5 m — clear. Comp compare now sums per-type (family 8 = bandit×2 + bandit×1). Both within normative law.

## Deviation (blocking: none)

**probe_gates_matrix happy leg is flaky by construction.** Spec L166: "debugForce bypasses ONLY the roll (seats still validate)" — Devbot's encounters.js follows this. pickSeat succeeds ≈15% per call (200-call sample: 30 ok / 170 fail) because p6 (z ≤ boundary.z − 6 = −31) rejects ~83% of the random disc and p3's 50 m fire exclusion around (2.5,−52) erases most of the remaining B-side band. The probe's happy leg demands a warn within 60 ticks = 3 checkSec windows = 3 pickSeat calls → P(fail) ≈ 0.85³ ≈ 61%. Testerbot measured 3 pass / 10 probe runs. The g1..g5 block-alone legs, the comp-match leg, debugMute leg, and CONFIG-purity leg are all deterministic and PASS. The code meets the spec's normative law; the instrument assertion ("within 60 ticks") is probabilistic, not deterministic. Recorded as FAIL on the probe as written, **non-blocking** under the verdict scale. IO adjudication: either accept (normative law met; rerun probe until pass is dishonest) or issue an IO repair pin (e.g. seed a deterministic RNG, or let debugForce also force the first lawful seat — a spec-law change requiring IO amendment, not a Devbot fix).

## Conclusion

**OVERALL: PASS** — zero blocking fails. 10/11 checks PASS outright; V-5 fails only on a disclosed, non-blocking instrument-side flake while the shipped code satisfies every normative law in the valspec.

Suggested commit message (IO executes the git gate; Testerbot does not commit):
`feat(encounters): CC-EN1 wilderness encounter tables V1 — night director over darkwood_edge (g1..g8, p1..p9, transient raidMember, RNG law 4 sites), CONFIG.encounters block + game.js 2-line hook + index.html script tag; bundle sha c745c545`
