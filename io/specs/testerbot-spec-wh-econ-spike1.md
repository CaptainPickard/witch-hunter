# Testerbot Validation Spec — wh-econ-spike1 (Sui testnet crafting-economy spike)

Spec ID: wh-econ-spike1
Date: 2026-09-30
Author: Testerbot (validation spec; written BEFORE Devbot implementation, per gate order 2)
Validates: /workspace/witch-hunter/io/specs/devbot-spec-wh-econ-spike1.md (sha256 f0958676b5fdc9f50db28d6709a7dc55a06f07c040c5a9ec3182fc02a65e5b04, 87 lines, read in FULL)
Gate: IO -> **Testerbot (this spec)** -> Devbot -> Testerbot (validation report) -> IO (commit+push)
Hard gate: `sui move build` + `sui move test` all-green. TS harness is review-only (AC-11).

---

## 0. Principles of this validation

0. AMENDMENT LOG (IO, 2026-09-30, post Devbot amendment request sui/README.md): A1 - WHItem is address-owned (`key, store`), Registry/TransferPolicy are the only shared objects; original "shared-owned WHItem" was an IO spec error corrected in the devbot spec deliverable 1a. Your AC references to item behavior (serials, lineage, kiosk round-trip) are unaffected. A2 - the seven step keys in YOUR spec (mint, craft, serial, kiosk_list, kiosk_purchase, royalty, provenance) are the contract of record; dispatch-level labels like cli_install are superseded, CLI/publish data lands in top-level `setup` metadata of e2e_result.json and you treat `setup` as informational (not asserted as steps).
1. **Independence.** No AC passes on Devbot self-report. I rerun every buildable/checkable artifact myself and re-derive evidence at verdict time. Devbot's implementation notes are cross-check inputs only.
2. **Evidence at verdict time.** Every per-AC verdict carries file:line evidence re-verified in the validation session, not copied from Devbot's submission.
3. **No silent tolerance.** Anything outside this spec's watch-item allowances fails. Watch-items (§6) are the ONLY pre-authorized tolerances.
4. **Facts about the frozen baseline that contradict the devbot spec are recorded, not papered over** (see §1.2 — the tree is NOT pristine-clean).

---

## 1. Frozen baseline

### 1.1 Repo anchors (measured 2026-09-30 ~02:53 UTC)

| Item | Value |
|---|---|
| Repo root | /workspace/witch-hunter |
| Branch | dev |
| Starting HEAD | `2fa6b15be91c7cf5bb5d8bd71babc9ca39b26371` (short: 2fa6b15, "fix: blade-forward strike poses + darkwood ground texture") |
| Devbot spec sha256 | `f0958676b5fdc9f50db28d6709a7dc55a06f07c040c5a9ec3182fc02a65e5b04` |
| `sui/` directory | DOES NOT EXIST pre-build (verified `ls -d sui` fails) |
| sui CLI | NOT INSTALLED (verified `command -v sui` exit 1; absent from ~/.local/bin and ~/.sui/bin) |
| node/npm | NOT AVAILABLE (verified `command -v node` exit 1) |
| jq | NOT AVAILABLE — JSON checks use python3 (3.12.14, present) |
| python3 | 3.12.14 present; `playwright` module importable (established headless pattern: python sync_playwright, cf. tests/wh_v2_verify.py) |
| grep | GNU grep 3.11, `-P` PCRE supported (verified) |

### 1.2 ACTUAL tree state at HEAD 2fa6b15 — NOT pristine-clean (measured)

The devbot spec line 20 says "tree clean" and line 87 says "status --porcelain empty".
**Measured reality disagrees**: the porcelain output is NOT empty. A parallel workstream
(whproto7-weave) left 17 entries. I freeze them here so AC-10 is enforceable as a
SET-DIFFERENCE, not as a naive empty-tree check.

Frozen status command (fsmonitor/untrackedCache disabled, untracked expanded):

```
git -c core.fsmonitor=false -c core.untrackedCache=false status --porcelain -uall
```

Frozen snapshot hash: `51b2fc6ee7b50d7161caf6bdb24a4de5c917c56bc752e08196552ea5b479b4` (17 lines, 2026-09-30)
Default (io/ collapsed, 15 lines) snapshot hash: `49d3ab7a99e9574cef7f9edbad3187a1df7f820e92305fa7c06abc697541af18`

Frozen 17-entry pre-existing dirty set (all belong to the whproto7-weave workstream — NOT part of this spike, must remain BIT-IDENTICAL after the spike):

```
 M docs/planning/04-combat-system.md
 M docs/planning/08-open-questions.md
 M docs/planning/17-magic-system.md
 M docs/planning/27-equipment-visual-system.md
 M docs/planning/33-equipment-and-formulas.md
 M prototype/index.html
 M prototype/js/CONFIG.js
 M prototype/js/game.js
 M prototype/js/player.js
 M prototype/style.css
?? io/specs/devbot-spec-wh-econ-spike1.md
?? io/specs/devbot-spec-whproto7-weave.md
?? io/specs/testerbot-spec-whproto7-weave.md
?? prototype/builds/v7-playable.html
?? prototype/js/spells.js
?? tests/wh_v7_weave.py
?? tools/build_v7.py
```

Frozen content anchors (drift detectors, all measured 2026-09-30):

- `git diff HEAD -- prototype/ tests/ docs/ tools/ art-direction/ | sha256sum` = `08c544649566c573ecf7ffe9db91b4a81a7a184254d6ceb3301389cc4833e496` (10 files, +752/-15)
- Staged diff: EMPTY (`git diff --cached | sha256sum` = e3b0c442… empty-string sha)
- Untracked io/specs sha256s: devbot-spec-wh-econ-spike1.md = `f0958676…5b04`; devbot-spec-whproto7-weave.md = `384bd5c3182550492cddcec176e334258fa3764ce8ea0098abd3fd83f8fd58a3`; testerbot-spec-whproto7-weave.md = `6b665829b26b1183e33ca683ae4431ef6b7bb41c1e6f0674ec21408b41d22bf2`
- Untracked parallel-workstream sha256s: prototype/builds/v7-playable.html = `6ceff6ec…d3f7`; prototype/js/spells.js = `082225b2…59d`; tests/wh_v7_weave.py = `d2893c23…4c9b`; tools/build_v7.py = `1ed74071…157b`
- Nothing staged; no stashes.

### 1.3 Expected-clean definition for THIS spike (AC-10 operationalized)

At validation time, HEAD must STILL be `2fa6b15be91c7cf5bb5d8bd71babc9ca39b26371`
(Devbot does not commit; IO owns the git gate — a moved HEAD is a protocol violation).

Expected porcelain at validation time =

    frozen pre-existing 17-entry set (§1.2, bit-identical)
  + additions under sui/** (the entire spike)
  + io/specs/testerbot-spec-wh-econ-spike1.md (this file, written pre-build)
  + io/specs/devbot-spec-wh-econ-spike1.md (already in the frozen set; content must equal frozen sha256)

NOTHING else. Expected-clean check (exact commands I run at verdict time):

```
cd /workspace/witch-hunter
test "$(git rev-parse HEAD)" = "2fa6b15be91c7cf5bb5d8bd71babc9ca39b26371" || echo "FAIL: HEAD moved"
git -c core.fsmonitor=false -c core.untrackedCache=false status --porcelain -uall > /tmp/wh_spike1_porcelain.txt
# python3 set-difference: observed - frozen must be a subset of {sui/**, io/specs/testerbot-spec-wh-econ-spike1.md}
# frozen - observed must be empty (no pre-existing entry disappeared: files must not be reverted/stolen)
git diff HEAD -- prototype/ tests/ docs/ tools/ art-direction/ | sha256sum   # must equal 08c544649566c573ecf7ffe9db91b4a81a7a184254d6ceb3301389cc4833e496
sha256sum io/specs/devbot-spec-wh-econ-spike1.md                              # must equal f0958676b5fdc9f50db28d6709a7dc55a06f07c040c5a9ec3182fc02a65e5b04
```

Tree-hygiene diff scope (the only allowed change surface): `sui/**` + `io/specs/testerbot-spec-wh-econ-spike1.md` + `io/specs/devbot-spec-wh-econ-spike1.md`. `prototype/`, `tests/`, `docs/`, `tools/`, `art-direction/` must show ZERO delta vs the frozen §1.2 state — including the pre-existing untracked files in them.

---

## 2. Per-AC validation procedures (independent methods I run myself)

Every command below is executed by ME in the validation session, post-build. jq is absent on this VPS — all JSON handling is python3. The sui binary may live in a suiup-variant path (§6.3); I resolve it with `command -v sui || ls ~/.local/bin/sui ~/.sui/bin/sui 2>/dev/null` before running.

### AC-1 — `sui move build` succeeds, zero warnings (strictness equivalent)

Method: independent rerun, exit code + output scan.
```
cd /workspace/witch-hunter/sui/move/wh-items
sui move build 2>&1 | tee /tmp/wh_spike1_ac1_build.log
test ${PIPESTATUS[0]} -eq 0                                  # exit 0
grep -ci "warning" /tmp/wh_spike1_ac1_build.log             # must be 0
grep -c "error" /tmp/wh_spike1_ac1_build.log                # must be 0
```
FAIL if: nonzero exit, any warning/error line, or `build` directory/publish artifacts committed (check AC-10 surface; `build/` under sui/ is acceptable ONLY inside sui/** and must not contain secrets).
Evidence: exit code, byte count of build log, warning count = 0.

### AC-2 — `sui move test` all-green, >=10 tests incl. the 8 listed behaviors

Method: independent rerun + suite-floor diff (§3).
```
cd /workspace/witch-hunter/sui/move/wh-items
sui move test 2>&1 | tee /tmp/wh_spike1_ac2_test.log
test ${PIPESTATUS[0]} -eq 0
grep -E "Test result:.*passed" /tmp/wh_spike1_ac2_test.log  # parse pass count
grep -ci "FAIL\|error" /tmp/wh_spike1_ac2_test.log           # must be 0
python3 - <<'EOF'   # extract test fn names + count, diff vs suite floor §3
import re,pathlib
names=[]
for p in pathlib.Path('.').rglob('*.move'):
    for m in re.finditer(r'#\[test(?:_variants\(\)\))?\]\s*(?:public\s+)?(?:entry\s+)?fun\s+(\w+)', p.read_text()):
        names.append((str(p), m.group(1)))
print(len(names)); [print(n) for n in names]
EOF
```
PASS requires: exit 0, zero FAIL lines, parsed passed-count >= 10, and every one of the 8 mandatory behaviors (§3) matched by >=1 observed test.
Evidence: log path, pass count, observed name list, floor-diff result (missing/renamed/added).

### AC-3 — README documents exact e2e flow, exact commands, expected e2e_result.json shape

Method: full read by me (read_file) + grep-level structural checks, and cross-check that every documented command references files that actually exist.
```
grep -n "sui move build\|sui move test\|suiup\|faucet\|SUI_TESTNET_MNEMONIC\|SUI_TESTNET_FAUCET_URL" sui/README.md
grep -n "e2e_result.json" sui/README.md
grep -n -i "proves\|does not prove" sui/README.md
# every referenced path in README must exist: extract and stat them (python3)
```
PASS requires: prereqs incl. suiup install steps + `sui --version`; env setup (SUI_TESTNET_MNEMONIC/SUI_TESTNET_FAUCET_URL); faucet funding; run commands; expected outputs; expected e2e_result.json shape showing the 7 step names; a "what this spike proves / does not prove" section. Every command in README must match a real path in sui/ (no aspirational commands).
Evidence: README line numbers for each required element.

### AC-4 — e2e_result.json: exactly 7 step names, per-step booleans + tx digests

Method: python3 schema check on the actual JSON Devbot produced (artifact at sui/ts/…, or content returned in implementation notes if faucet-blocked).
```
python3 - <<'EOF'
import json,sys
d=json.load(open(sys.argv[1]))
steps={"mint","craft","serial","kiosk_list","kiosk_purchase","royalty","provenance"}
assert set(d["steps"].keys())==steps, d["steps"].keys()
for k,v in d["steps"].items():
    assert isinstance(v.get("ok"),bool) or v.get("status") in ("ok","skipped_faucet")
    # digest must be a real 64-hex tx digest OR null; fabricated digests = FAIL
    dg=v.get("digest")
    assert dg is None or (isinstance(dg,str) and len(dg)==64 and all(c in "0123456789abcdef" for c in dg))
print("AC4 schema OK")
EOF
```
PASS requires: exact 7 step names (no more, no fewer — `set == steps`, not superset); per-step machine-checkable boolean; digest per step (null allowed ONLY under the §6.2 skipped_faucet protocol — a null digest MUST co-occur with a skipped_faucet marker and never with ok:true). Fabricated digests on skipped steps = integrity FAIL.
Evidence: JSON path, per-step table reproduced in verdict.

### AC-5 — RoyaltyRule at 5% default, in Move, tested (rule present + distribution in purchase simulation)

Method: grep-level source proof + test presence + independent rerun.
```
grep -rn "RoyaltyRule" sui/move/wh-items/sources/           # rule added in code, not just docs
grep -rnE "0\.05|[0-9]+ *%|500" sui/move/wh-items/sources/  # 5% default literal (or basis-point form)
grep -rni "royalt" sui/move/wh-items/tests/                # royalty test(s) exist
# rerun: sui move test (AC-2 run already proves them green)
```
PASS requires: RoyaltyRule present in TransferPolicy setup in sources at 5% default (any canonical literal form: 0.05, 500 bp, or sui::royalty default param — the value must be identifiable as 5%), lock rule for Family::Decor present (`grep -rn "lock" sui/move/wh-items/sources/` cross-checked), and >=1 green test proving rule presence + distribution flow in a kiosk purchase simulation.
Evidence: file:line for RoyaltyRule literal, lock rule, test fn name + green rerun.

### AC-6 — serial numbers monotonic per family, tested

Method: source review + test presence + rerun.
```
grep -rn "Registry" sui/move/wh-items/sources/              # shared Registry with per-family counters
grep -rniE "serial.*(monoton|increas)|monoton.*serial" sui/move/wh-items/tests/
grep -rn "serial" sui/move/wh-items/sources/ | head -20
```
PASS requires: serial allocation via shared Registry, monotonic per family (independent counters per family — cross-family independence visible in source or test), >=1 green test asserting strict monotonicity across >=2 consecutive crafts.
Evidence: file:line of counter increment, test fn name + green rerun.

### AC-7 — craft-failure band exists, materials partially consumed (sink), tested

Method: source review + test presence + rerun.
```
grep -rniE "fail(ure)?_band|failure" sui/move/wh-items/sources/ | head -20
grep -rniE "fail" sui/move/wh-items/tests/ | head -20
```
PASS requires: documented failure probability band in the band table; on failure: no WHItem minted AND a defined strict-subset of input materials consumed (sink) — not all, not none, unless explicitly documented as a valid edge and asserted in test; >=1 green test.
Evidence: file:line of failure branch + material consumption, test fn name + green rerun.

### AC-8 — timing band multipliers monotonic (higher band → weakly better odds), tested

Method: constant-curve review + test presence + rerun.
```
grep -rniE "timing_band|band_multiplier" sui/move/wh-items/sources/ | head -30
grep -rniE "monoton" sui/move/wh-items/tests/ | head -10
```
PASS requires: documented constant curve mapping timing_band (u8, 0–100) → band multipliers; monotonic non-decreasing affix probability with band (never guarantees — capped <1.0); craft is private entry with `timing_band: u8` param, no public fun with Random/RandomGenerator args (`grep -rn "public" sui/move/wh-items/sources/` audited); >=1 green test asserting weak monotonicity (exhaustive multiplier-table check or statistical roll sampling).
Evidence: file:line of curve table, test fn name + green rerun.

### AC-9 — provenance: item lineage records input material ids, tested

Method: source review + test presence + rerun.
```
grep -rn "lineage" sui/move/wh-items/sources/ | head -20
grep -rniE "provenance|lineage" sui/move/wh-items/tests/ | head -10
```
PASS requires: WHItem.lineage populated with crafted-from material object ids at craft; >=1 green test asserting lineage grows/records input material ids across a craft (and ideally a craft-from-item chain).
Evidence: file:line of lineage write, test fn name + green rerun.

### AC-10 — tree hygiene (see §1.3)

Method: independent git set-difference against the frozen baseline.
Commands: exactly those in §1.3, plus:
```
git -c core.fsmonitor=false -c core.untrackedCache=false status --porcelain -uall \
  | grep -vE "^\s*[AM?]+ (sui/|io/specs/(testerbot-spec-wh-econ-spike1|devbot-spec-wh-econ-spike1)\.md)" \
  | grep -vE "frozen-17-listing"   # or the python3 set-diff; any residual line = FAIL
ls sui/ts/node_modules 2>/dev/null    # must NOT exist (node_modules not committed)
find sui -name "*.log" -o -name "build" -type d | head   # build artifacts review (allowed inside sui/ but no secrets)
```
PASS requires: HEAD unchanged at 2fa6b15…; observed-minus-frozen == exactly sui/** + this spec file; frozen-minus-observed == empty; protected-dirs diff sha256 == `08c544649566c573ecf7ffe9db91b4a81a7a184254d6ceb3301389cc4833e496`; devbot spec sha256 unchanged; no node_modules staged.
Evidence: porcelain output, set-diff result, all sha256 anchors restated in verdict.

### AC-11 — no node run required; TS harness review-only; Move simulated-e2e proves roll math

Method: review-only (I do NOT and CANNOT run node — verified absent). Checks:
```
ls sui/ts/                        # package.json + lockfile present
grep -n "SUI_TESTNET_MNEMONIC\|SUI_TESTNET_FAUCET_URL" sui/ts/*.ts
grep -rnE "mnemonic|private ?key" sui/ts/*.ts | head    # values must come from env, never literals (ties to §4)
grep -c "step" sui/ts/*.ts        # the 7-step flow present in code (mint..provenance)
grep -rniE "simulated|e2e" sui/move/wh-items/tests/    # Move-side simulated e2e test exists
```
PASS requires: sui/ts exists with package.json + lockfile committed; harness reads env for mnemonic/faucet (no literals); code visibly drives all 7 steps and prints machine-readable e2e_result.json; Move-side simulated-e2e test exercising the same roll math exists AND is green in my AC-2 rerun. TS execution is explicitly NOT gated here (§6.1) — inability to run it is never a failure. Note: `tests/util/playwright-validate.mjs` named in the devbot spec does NOT exist; the established repo pattern is python sync_playwright (tests/wh_v2_verify.py) — if Devbot adds a TS syntax-check helper inside sui/, it lands in-scope (sui/**) and is acceptable; any change to tests/ is NOT.
Evidence: file list, grep hits with line numbers, simulated-e2e test name + green rerun.

### AC-12 — Sui CLI version recorded; no upgrade caps; package published immutable

Method: independent version check + grep + best-effort on-chain check.
```
sui --version                    # my own run; compare vs version recorded in sui/README.md + implementation notes
grep -rni "upgrade" sui/move/wh-items/sources/ sui/move/wh-items/Move.toml    # UpgradeCap must be absent
grep -rn "sui --version\|Sui CLI" sui/README.md
# best-effort (network-flaky VPS, NOT a hard gate): sui client object <package_id> to confirm package exists + no upgrade cap object id referenced
```
PASS requires: exact `sui --version` string recorded in sui/README.md (and echoed in implementation notes) matching my own run output; ZERO UpgradeCap usage/retention in Move sources or publish flow; package published immutable (package ID reported; on-chain immutability check is best-effort given faucet/network watch-item, but absence of upgrade caps in code is a hard check).
Evidence: my version output vs recorded string, grep results, package ID from implementation notes.

---

## 3. Suite floor — expected Move test names (10+, preservation-diffable)

The devbot spec requires >=10 dedicated Move tests including the 8 listed behaviors
(7 from deliverable 1h + the simulated-e2e roll-math test from Constraints/AC-11).
These are the test names I EXPECT to find (behavior-mapped; name-matching is heuristic
grep, not literal — but every expected test must map 1:1 to an observed one):

| # | Expected test name (representative) | Mandatory behavior | Match heuristic |
|---|---|---|---|
| 1 | `test_craft_success_band` | craft success band produces WHItem | `craft.*success\|success.*band` |
| 2 | `test_craft_failure_band_sink` | failure band: no item, materials partially consumed | `fail` in tests/ |
| 3 | `test_timing_band_monotonicity` | higher band → weakly better odds | `monoton` in tests/ |
| 4 | `test_serial_monotonic_per_family` | serial monotonicity per family | `serial` + `monoton` |
| 5 | `test_royalty_rule_present` | RoyaltyRule present (5%) + distribution in purchase sim | `royalt` in tests/ |
| 6 | `test_kiosk_list_purchase_round_trip` | kiosk list + purchase round trip | `kiosk.*(list\|purchase)` |
| 7 | `test_provenance_lineage_growth` | provenance chain growth (lineage records material ids) | `provenance\|lineage` |
| 8 | `test_simulated_e2e_roll_math` | simulated e2e exercising same roll math (AC-11) | `simulated\|e2e` |
| 9 | `test_burn_salvage_emits_event` | burn/salvage entry emits event, destroys item (quality bar) | `burn\|salvage` |
| 10 | `test_display_per_family` | Display object per family with name/description/image_url/attributes | `display` |
| 11 | `test_timing_band_bounds_rejected` | edge: invalid timing_band (>100) handled gracefully | `bound\|invalid` |

Floor rules:
- Rows 1–8 are MANDATORY behaviors (AC-2/AC-11/AC-5–AC-9 depend on them). Missing any = AC-2 FAIL plus the corresponding AC FAIL.
- Rows 9–11 are expected (burn/salvage is required by the devbot spec quality bar; display objects are deliverable 1f; edge-case handling is my standing checklist). Missing row 9 = AC FAIL against the quality bar. Missing 10–11 = noted deficiency; blocks only if it drops the suite below 10.
- Suite count floor: >=10 tests observed in my rerun (AC-2).
- **Renames must be justified**: any expected-name↔observed-name mismatch must be explained in Devbot's submission (one line per rename, with the mapping), and the behavior must still be covered. Unjustified renames = AC-2 FAIL (evidence-tampering smell). Silently dropping a behavior and re-adding under a vaguer name = FAIL.
- Preservation is diffable: I record the full observed-name list at validation time and diff it against this table in the verdict JSON.

---

## 4. Secrets-grep plan (positive control OUTSIDE the repo)

Threat: a committed mnemonic, private key (bech32 `suiprivkey1…`), or funded-key secret anywhere in sui/. The spike legitimately touches wallet material — this check is mandatory, not optional.

Patterns (grep -P, GNU grep 3.11 verified):
```
suiprivkey1[a-z0-9]{20,}                                   # Sui bech32 private key
(?i)(api[_-]?key|secret|mnemonic|private[_-]?key)\s*[:=]\s*['"][^'"]{8,}['"]   # assigned literals
SUI_TESTNET_MNEMONIC\s*=\s*['"][^'"]{12,}['"]              # mnemonic literal (12+ word strings)
(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])                       # 64-hex blobs (review each hit; tx digests/ids are FALSE POSITIVES — triage, don't blind-fail)
```

Positive control — planted OUTSIDE the repo before the grep (proves the pattern set actually detects):
```
cat > /tmp/wh_spike1_secrets_control.txt <<'EOF'
# POSITIVE CONTROL — planted by Testerbot 2026-09-30. DELIBERATELY FAKE. Never a real key.
suiprivkey1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq
SUI_TESTNET_MNEMONIC='control fiction twelve words never used anywhere real'
api_key = "fake-positive-control-not-real-12345678"
EOF
```

Execution order (control FIRST, repo SECOND, same pattern set):
```
grep -rP -f /tmp/wh_spike1_patterns.txt /tmp/wh_spike1_secrets_control.txt  # MUST match >=1 (control works)
grep -rP -f /tmp/wh_spike1_patterns.txt /workspace/witch-hunter/sui/ || echo "CLEAN"
# 64-hex triage: every hit outside sui/ts/*.json digests reviewed manually
```

PASS requires:
- Control file yields >=1 match per pattern class it contains (else the grep itself is broken → fix and re-run; never pass on a broken control).
- Zero true-secret matches inside sui/. 64-hex hits are triaged: tx digests/package ids/object ids in e2e_result.json or logs are public data (false positives); any hit adjacent to "mnemonic|key|secret" wording = FAIL.
- `.env`, `*.key`, mnemonic files inside sui/ = FAIL even if empty-looking (env must be read from process env, per devbot spec deliverable 2a).

---

## 5. Verdict JSON shape (my report format)

```json
{
  "spec_id": "wh-econ-spike1",
  "validated_at": "<ISO-8601 of validation session>",
  "verdict": "PASS | FAIL",
  "baseline": {
    "head_at_validation": "2fa6b15be91c7cf5bb5d8bd71babc9ca39b26371",
    "head_unchanged": true,
    "devbot_spec_sha256": "f0958676b5fdc9f50db28d6709a7dc55a06f07c040c5a9ec3182fc02a65e5b04",
    "preexisting_porcelain_sha256_frozen": "51b2fc6ee7b50d7161caf6bdb24a4de5c917c56bc752e08196552ea5b479b4",
    "tree_hygiene": {
      "result": "PASS | FAIL",
      "command": "git -c core.fsmonitor=false -c core.untrackedCache=false status --porcelain -uall (set-diffed vs frozen)",
      "allowed_additions_observed": ["sui/...", "io/specs/testerbot-spec-wh-econ-spike1.md"],
      "out_of_scope_changes": [],
      "preexisting_entries_bit_identical": true,
      "protected_dirs_diff_sha256": "08c544649566c573ecf7ffe9db91b4a81a7a184254d6ceb3301389cc4833e496",
      "node_modules_committed": false
    }
  },
  "ac_results": {
    "AC-1": {"result": "PASS|FAIL", "method": "independent rerun", "command": "sui move build", "evidence": [{"file": "sui/move/wh-items/...", "line": 0, "note": "exit 0, warnings 0"}]},
    "AC-2": {"result": "PASS|FAIL", "method": "independent rerun + suite-floor diff", "evidence": ["pass_count", "floor_diff"]},
    "AC-3": {"result": "PASS|FAIL", "evidence": [{"file": "sui/README.md", "line": 0, "note": "element -> line map"}]},
    "AC-4": {"result": "PASS|FAIL", "evidence": [{"file": "e2e_result.json", "line": 0, "note": "7 steps, booleans, digests"}]},
    "AC-5": {"result": "PASS|FAIL", "evidence": [{"file": "sources/...", "line": 0, "note": "RoyaltyRule 5% literal + test"}]},
    "AC-6": {"result": "PASS|FAIL", "evidence": [{"file": "tests/...", "line": 0, "note": "serial monotonic test"}]},
    "AC-7": {"result": "PASS|FAIL", "evidence": [{"file": "tests/...", "line": 0, "note": "craft-failure sink test"}]},
    "AC-8": {"result": "PASS|FAIL", "evidence": [{"file": "tests/...", "line": 0, "note": "timing monotonicity test"}]},
    "AC-9": {"result": "PASS|FAIL", "evidence": [{"file": "tests/...", "line": 0, "note": "provenance/lineage test"}]},
    "AC-10": {"result": "PASS|FAIL", "evidence": ["set-diff output", "sha256 anchors"]},
    "AC-11": {"result": "PASS|FAIL", "evidence": [{"file": "sui/ts/...", "line": 0, "note": "review-only checks + simulated-e2e green"}]},
    "AC-12": {"result": "PASS|FAIL", "evidence": [{"file": "sui/README.md", "line": 0, "note": "version recorded vs sui --version; UpgradeCap grep 0"}]}
  },
  "suite": {
    "frozen_floor_count": 10,
    "observed_count": 0,
    "floor_met": false,
    "names_observed": [],
    "floor_diff": {"missing_behaviors": [], "renames": [], "justified": true, "added": []}
  },
  "secrets": {
    "patterns_file": "/tmp/wh_spike1_patterns.txt",
    "matches_in_sui": 0,
    "triage_notes": "",
    "positive_control": {"path": "/tmp/wh_spike1_secrets_control.txt", "matched": true, "match_count": 0}
  },
  "watch_items": {
    "ts_runtime": "review_only_no_node_failure_by_design",
    "faucet": {"status": "ok | skipped_faucet", "retries_documented": 0, "steps_marked": [], "no_fabricated_digests": true},
    "suiup_install": {"path": "", "sui_version": ""}
  },
  "amendments": []
}
```

Rules: every `evidence` entry carries file:line re-verified in THIS validation session. Suite `observed_count` is from MY rerun, compared against the frozen floor (10) and the §3 expected-name table. PASS requires ALL AC-1..AC-12 PASS; any FAIL → verdict FAIL with per-issue line-numbered detail returned to Devbot via IO.

---

## 6. Watch-items (pre-authorized tolerances — the ONLY ones)

### 6.1 TS runtime inability — review-only, NEVER a failure
This VPS has no node (verified). AC-11 explicitly gates on review + Move-side simulated-e2e, not TS execution. I will NOT run the TS harness, NOT fail any AC for TS-runtime inability, and NOT treat missing TS execution results as a gap — provided the §2/AC-11 review checks pass. If Devbot claims TS execution results anyway, that claim is out-of-scope and unverified (flagged, not failed).

### 6.2 Faucet flake — skipped_faucet protocol
Faucet is flaky from VPS IPs. Protocol (from devbot spec §87): after 3 DOCUMENTED retries fail, mint/craft (and downstream kiosk_list/kiosk_purchase/royalty — they need funded wallets) steps are marked `skipped_faucet` in e2e_result.json instead of failing the environment. I verify: (a) 3 retry attempts are documented in implementation notes; (b) affected steps carry the skipped_faucet marker with ok not asserted true; (c) digests for skipped steps are null — **fabricated digests on skipped steps are an integrity FAIL regardless of faucet state**; (d) serial/provenance steps may still be Move-test-proven. The Move suite remains the hard gate: faucet failure NEVER converts into a Move-test failure, and NEVER into a pass either — it only narrows AC-4 to schema validation.

### 6.3 suiup install path variance
suiup may install to ~/.local/bin/sui or ~/.sui/bin/sui depending on installer version; PATH propagation varies across shells. I resolve the binary location myself and record the path + `sui --version` in the verdict. Path variance is NOT a failure. Version variance only matters for AC-12's recorded-vs-run match — a recorded version that does not match the binary that actually builds/tests = FAIL (that's a truthfulness issue, not an environment one).

---

## 7. AMENDED-in-flight protocol

If Devbot requests ANY change to either spec mid-build (scope, AC wording, suite floor, step names, secrets scope, watch-items, anything): it does NOT get absorbed silently.

1. Devbot halts the affected work and states the requested amendment + reason to IO.
2. **IO amends BOTH specs** (devbot-spec-wh-econ-spike1.md AND this file) — never Devbot, never Testerbot unilaterally.
3. This file records the amendment in the `amendments` array (what/when/why/who) and bumps the frozen anchors it touches (e.g., devbot spec sha256 in §1.2/§1.3).
4. Devbot re-confirms against the amended pair; I validate ONLY against the amended specs.
5. A submission whose behavior matches a request that was never amended into the specs = FAIL on spec-compliance grounds, even if the code itself is good.

No silent drift. No "Devbot said it was fine". The two specs are the only contract.

---

## 8. Out-of-scope for this validation (I do not test)

- Performance/latency/optimization (not in spec).
- Mainnet behavior (spec forbids mainnet; zero mainnet work expected — any mainnet code found = FAIL under testnet-only lock).
- Nicko-facing communication, commit/push (IO owns the git gate), architecture redesign.
- The parallel whproto7-weave workstream's dirty files (§1.2) — I only verify they are UNTOUCHED.

**Verdict ladder: all 12 AC PASS -> "VALIDATION PASSED - READY FOR COMMIT+PUSH" to IO. Any FAIL -> line-numbered issue report to Devbot via IO, full re-validation on resubmit (previous pass never carries over).**

---

_Last updated: 2026-09-30 by Testerbot. Pre-build gate. This file + the devbot spec are the only allowed non-sui changes (AC-10)._