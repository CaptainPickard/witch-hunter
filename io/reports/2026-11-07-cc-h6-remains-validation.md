# CC-H6 The Remains — Validation Report (Testerbot recovery run)

**Date:** 2026-11-07 · **Worktree:** /tmp/wh-worldfeat · **Branch:** feat/world-visuals · **Baseline (HEAD):** `e20f61d` ("build: v8 bundle (worktree) - CC-H5b hazards stamp")

**What:** Independent lean validation of the CC-H6 "The Remains" build (regionL,
delve strata V5 off the Tithe Vaults) against
`io/specs/cc-h6-remains-valspec.md` (CH-1..CH-6, G-01..G-12 G-laws via
`scratch/cc-h6/solve_geometry.py`, SR-1..SR-4 via `scratch/cc-h6/save_roundtrip.js`).
**Where:** this file = `io/reports/2026-11-07-cc-h6-remains-validation.md`
(the valspec's report-first target). **Report-before-verdict order honored** —
the verdict section is intentionally LAST in this file, per the valspec's
RUNBOOK report-first law.

**Continuation-of-deleg_05d8eb5f statement + why:** the prior Testerbot child
(deleg_05d8eb5f) completed the independent CC-H6 validation work itself
(probes re-run fresh, greps, adjudication) and recorded
VERDICT: PASS — CH-1..CH-6 6/6, G 12/12, SR 4/4, deviations 5/5, census
clean — but exhausted its iteration budget BEFORE writing this report file,
so the report-first law was unmet and its verbose summary was trimmed. This
recovery run therefore re-executes the entire verification fresh (nothing is
carried on its word alone): every digest, PASS count, exit code, grep and
parsed assert below is evidence produced in THIS session against the landed
worktree. Per the no-harness-playtest gate: static probe + code QA only, no
headless game runs, no browser smoke; final acceptance remains Nicko's
playtest.

---

## 1. Baseline + census (fresh, this session)

- `git log -1 --oneline` → `e20f61d build: v8 bundle (worktree) - CC-H5b
  hazards stamp`, branch `feat/world-visuals`.
- `git status --porcelain | wc -l` = **6** — exactly the expected build-delta
  + ledger set:
  - ` M prototype/builds/v8-playable.html`
  - ` M prototype/js/CONFIG.js`
  - ` M prototype/js/region-defs.js`
  - `?? io/specs/cc-h6-remains-spec.md`
  - `?? io/specs/cc-h6-remains-valspec.md`
  - `?? scratch/cc-h6/`
  No engine file, no index.html, no assets, no tools/, no unregistered path.
- `git diff e20f61d -- prototype/js/enemy.js game.js save.js region-manager.js
  daynight.js index.html` → **0 lines** (empty engine/surface diff).
- `git diff --cached --stat | wc -l` = **0** — NO-GIT honored (nothing staged,
  committed, or pushed; IO stays sole git gatekeeper).

## 2. Fresh probe evidence (both runs twice, determinism)

| Probe | Run | Exit | PASS lines | sha1 |
|---|---|---|---|---|
| `python3 scratch/cc-h6/solve_geometry.py` (`/tmp/geo1.txt`) | 1 | 0 | 44 (44/44 laws) | `d1a9671073506eb6676d46f924449e6cc79e9241` |
| `python3 scratch/cc-h6/solve_geometry.py` (`/tmp/geo2.txt`) | 2 | 0 | 44 | `d1a9671073506eb6676d46f924449e6cc79e9241` |
| `node scratch/cc-h6/save_roundtrip.js` (`/tmp/sr1.txt`) | 1 | 0 | 18 (18/18) | `e532061eb21aea08566c769baedfe02e04f94315` |
| `node scratch/cc-h6/save_roundtrip.js` (`/tmp/sr2.txt`) | 2 | 0 | 18 | `e532061eb21aea08566c769baedfe02e04f94315` |

**Byte identity:** `diff -q /tmp/geo1.txt /tmp/geo2.txt` → identical
(GEODIFF-IDENTICAL); `diff -q /tmp/sr1.txt /tmp/sr2.txt` → identical
(SRDIFF-IDENTICAL). Both run2 digests equal run1 — deterministic, matching
Devbot's recorded digests `d1a967…` / `e532061e…` exactly.

Both probes carry the CONFIG-ROW-PARSED banner (geo1 lines 1–8 quote the live
parse: regionL id/center/spawn/props 23, enemy.lastchancel, regionK anchor,
conn[10]); no hard-coded spec constants (landed values are parsed at runtime).

Bundle: `prototype/builds/v8-playable.html` sha1
`ab7972f6b154bbb4bb07cbf6cdf76f38abd8922c`, 3,518,948 bytes, stamp
`(build 11-07 16:10Z e20f61d)` present, `the_remains` ×4 inlined.

## 3. CH-1..CH-6 — contract quote + evidence (one line each)

Valspec quotes are verbatim from `io/specs/cc-h6-remains-valspec.md`; evidence
cites my fresh geo1 G-law lines / sr1 lines / greps as printed.

| CH | Valspec contract (quoted) | Evidence (this session) |
|---|---|---|
| CH-1 | "Key-set LAW: `Object.keys(regionL)` == `Object.keys(regionK)` minus `traps` minus `rotLair` … enemies deep-= [] ; lairs deep-= `[{type:'lastchancel', x:0, z:-1060}]` (length 1)" | LAW-34 "keyset law: L == K minus the K-only rotLair/hazards" PASS (geo1:58); LAW-31 "lair trio (regionL lairs x/z == nest == CONFIG.enemy.lastchancel.lair x/y)" PASS (geo1:55); parse line 1: "lairs 1", id the_remains, center (0,-1064) |
| CH-2 | "Ring is RE-DERIVED, not literal-copied: rho == 30.0 +- 0.05 for all 10 rows; adjacent-chord uniformity <= 0.02" | G-02 "chord uniformity: 0.0025 max-dev from mean 18.5410 (law<=0.02)" PASS (geo1:10); G-03 "rho circle: all rows on r 30.0+-0.05 … worst 0.0025" PASS (geo1:11); G-04 lane edge "2.00 m (law>=1.0)" PASS (geo1:12) |
| CH-3 | "`connections.length === 11`; from === `'tithe_vaults'`; to === `'the_remains'` … `sides[K] === +1 and sides[L] === -1` … `planeIn(conn,'tithe_vaults') === false`, `planeIn(conn,'the_remains') === true`" | LAW-25/26/27 sides+planeIn+both-directions PASS (geo1:49–51); fresh THREE-free node eval → `connections.length=11 conn10=tithe_vaults->the_remains`; parse line 8: "count 11 … sides tithe_vaults +1 / the_remains -1 … walkFrom the_remains" |
| CH-4 | "Lair self-consistency (ENGINE truth = enemy.js:1245 lairNest): nest = `regionL.center + {x: lair.x, z: lair.y}` EQUALS regionL.lairs[0] {x,z}" + minions crash guard "`cap === 0 AND interval is a finite number`" | LAW-13 "boss seat PARSED triple agrees (lairs row == nest == center+y, z -1060)" PASS (geo1:37); LAW-38 "minions cap-0 guard PRESENT: {asset zealot, cap 0, interval 999.0, range 5.0} + NO dieOnMasterDeath" PASS (geo1:62); LAW-39 unguarded-read crash shape "impossible on this row" PASS (geo1:63); `grep -c "cap: 0"` inside the lastchancel CONFIG block (lines 3375–3414) = 1 |
| CH-5 | "boss-seat clear circle >= 6.0 AT the parsed lairs seat … · L land/spawn >= 8.0 south of plane -1036 on the home side" | G-06 "boss-seat clear 6.0 at (0,-1060): 7.2807 m binding: stoneSteps at (-2.40,-1068.00)" PASS (geo1:14); LAW-12 7.3522 / LAW-11 fixed-map 7.3522 both ≥ 6.0 (geo1:35–36); LAW-14 "L land (0,-1044) == L spawn row" PASS (geo1:38); LAW-27–29 home-side/containment PASS (geo1:48–53) |
| CH-6 | "`git diff e20f61d -- prototype/js/enemy.js game.js save.js region-manager.js daynight.js index.html` EMPTY … confined to … regionL + lastchancel + body-map rows" + census "grep -c lastchancel prototype/js/enemy.js stays 0" | Empty diff = 0 lines (measured); lastchancel grep in enemy.js = **0** (exit-1/no-hits, correct); dirty-set/NO-GIT as sec 1; LAW-42 body maps banditBody/bandit PASS (geo1:66); LAW-35 "seed 559043117 differs from every other landed groundSeed" PASS (geo1:59); LAW-32 "NO rotLair and NO hazards (clean chamber)" PASS (geo1:56) |

## 4. G-01..G-12 + SR-1..SR-4 (fresh, verbatim contract shapes)

All 12 G lines and all 18 SR PASS lines printed PASS in both runs (geo1
lines 9–20: G-01..G-12; geo1:25–68 the 44 law lines; sr1:1–18 SR-1..SR-4
sub-lines, incl. "SR-4 restoreLairs({lastchancel_cleared_L: 2}) then
captureLairs => key present at day 2" and the malformed-key negative).
Summary lines: `solve_geometry (cc-h6): 44/44 laws PASS; FAIL: 0` and
`save_roundtrip: 18/18 PASS`.

## 5. Landed-vs-spec deviations adjudication (from build-note.md; 5, all non-blocking)

| # | Deviation (build-note) | Adjudication |
|---|---|---|
| 1 | Ring re-derived strict-2dp; rotY k=3/9 landed 5.02/8.79 vs sec-2b literals 5.03/8.80 | OK — literal is CONTEXT (valspec A2/H5 SPEC-FIG-FIX); law is rho/chord on landed rows. Probe LAW-6 "rotY == 3.14 + k*0.6283 2dp ladder" PASS on landed values (geo1:30) |
| 2 | stoneSarcophagus seat (0,-1086) vs sec-2b literal (0,-1078) | OK — the literal gave 2.75 m < boss-seat law 6.0; seat amendment restores 7.2807/7.3522 ≥ 6.0 (G-06/LAW-11/12). Probe-amends-seat-never-law precedent (H5b) |
| 3 | skullPile east (12,-1090) vs literal (12,-1084) | OK — literal sat 0.11 m from the re-derived k=4 band; landed gives prop raw min 4.7260 ≥ 4.0 (G-05, geo1:13) |
| 4 | blightcap pair (±16,-1047) vs literal (13,-1046) mirrored | OK — literal dipped into k=9/k=1 bands; landed clears every band ≥ 4.92, mutual ≥ 2.6569 ≥ 2.0 (LAW-9/10 PASS) |
| 5 | guardArcDeg 42 vs sec-5 prose "45" gloss | OK — the FIELD line governs (valspec table INITIAL); probe LAW-38/parse pin guardArc 42 |

In every case the LAW floors hold on the landed rows; deltas are confined to
spec letters the valspec itself classifies as INITIAL/context. 5/5 adjudicated,
0 blocking. Non-changes (build-note item 6): spawn/land/plane/hook rows and
the cap-0 minions guard row landed exactly per sec 4 — re-confirmed by G-07
("K (2,-858) nearest wall seg 9.50 m … L (0,-1044) == spawn row"), LAW-38,
LAW-43 and the fresh connections eval.

## 6. Census result

Clean: dirty set = exactly the 3 modified + 2 spec + 1 untracked-dir entries
(sec 1); engine/surface diffs empty; nothing staged; probes + build note are
the only new scratch artifacts. Bundle carries the regionL rows (the_remains
×4) and the deterministic HEAD stamp.

## 7. Bundle

`prototype/builds/v8-playable.html` — sha1 `ab7972f6b154bbb4bb07cbf6cdf76f38abd8922c`
(3,518,948 bytes), stamp `(build 11-07 16:10Z e20f61d)`, built by
tools/build_v8.py (newest builder) per build-note.

## VERDICT

**PASS.**
- CH-1..CH-6: **6/6** (each evidenced in sec 3)
- G-laws: **44/44 PASS**, FAIL: 0, exit 0, run×2 byte-identical
  (sha1 d1a9671073506eb6676d46f924449e6cc79e9241 — matches Devbot's recorded digest)
- SR: **18/18 PASS**, exit 0, run×2 byte-identical
  (sha1 e532061eb21aea08566c769baedfe02e04f94315 — matches Devbot's recorded digest)
- Deviations: **5/5 adjudicated, 0 blocking** (law floors hold)
- Census: **clean** (6/6 expected dirty entries, no engine diffs, NO-GIT honored)
- Self-checks: connections.length = 11 (THREE-free eval); `lastchancel` hits
  in enemy.js = 0; `cap: 0` in lastchancel CONFIG block = 1; `node --check`
  CONFIG.js + region-defs.js exit 0.

Nothing above differed from the valspec contract. Acceptance bar remains
Nicko's playtest of the v8 bundle (no-harness gate).

— Testerbot recovery run for CC-H6 (continuation of deleg_05d8eb5f), 2026-11-07
