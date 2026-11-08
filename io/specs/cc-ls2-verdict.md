# CC-LS2 — Independent Testerbot Validation (valspec V1–V4)

Validator: Testerbot (independent seat). Build author: Devbot (separate seat).
Run time: 2026-11-08 (UTC). Worktree: /tmp/wh-worldfeat, branch feat/world-visuals,
base HEAD b006d5687c6b8d82467bc815b2890ee002db1c71 (short b006d56) — uncommitted state.
Spec: io/specs/cc-ls2-loader-surface-spec.md (sha256 2836d48c…705f5, matches frozen).
Valspec: io/specs/cc-ls2-loader-surface-valspec.md. Pre-fix evidence: io/specs/cc-ls2-prefix-evidence.txt.
All my run logs: scratch/cc-ls2-val/val/ (val-boot-a-final.*, val-boot-b-final.*, + first-pass logs).

---

## V-1 — Change-scope diff check: **PASS**

- `git rev-parse HEAD` = b006d5687c6b8d82467bc815b2890ee002db1c71 (= b006d56 ✔).
- `git diff HEAD --stat` → exactly two tracked files: `prototype/js/assets.js` (+4, 0−)
  and `prototype/builds/v8-playable.html` (+5, 1−; = rebuilt bundle). `git diff --name-only HEAD`
  confirms the set = {assets.js, v8-playable.html}; nothing else tracked modified.
  Untracked additions are gate docs, evidence, and scratch logs (incl. my own scratch/cc-ls2-val/val/).
- assets.js diff (raw-byte repr) = 3 comment lines (CC-LS2 comment) + exactly ONE code line,
  byte-for-byte `pageDir = pageDir.replace(/\/prototype\/$/, '/');` at L228 — matches frozen
  seam text with zero whitespace drift (`git diff -U0` shows no removed/changed pre-existing lines).
- Seam adjacency verified in-bundle: sits inside the `/builds/` strip branch (L93659 → L93663).
- `node --check prototype/js/assets.js` → SYNTAX_OK. No `prototype/art-direction` tree added.

## V-2 — Rebuild determinism sanity: **PASS**

- V-2.1 (HEAD rebuild byte-identical modulo known title-diff): scratch at HEAD via
  `git archive HEAD`, `python3 tools/build_v8.py` run there → sha256 ff0e12a3…93a8d4.
  Diff vs committed HEAD bundle: EXACTLY one line — the build-stamp title line only
  (410cc81 → b006d56: `git rev-parse --short HEAD` resolves differently inside the archive
  because the scratch has no own .git; stub .git → same repo gitdir was used read-only for
  rev-parse/show only). All other 8 lines of the committed-bundle diff are present in the
  scratch rebuild. PASS by valspec's modulo-title allowance.
- V-2.2 (comment line counts): comment line is not standalone in sources — it is glued to the
  preceding code line by the build's line glue; per-line occurrences in rebuilt bundle:
  code line ×1 (expected), glue line ×1 (expected), 3rd comment line standalone ×1 (expected). PASS.
- V-2.3 (current-worktree rebuild byte-identical to dev's committed work):
  snapshotted dev bytes BEFORE rebuild (a5070038…dfa2e), ran `python3 tools/build_v8.py`
  in the worktree, byte-compare vs snapshot → IDENTICAL_TO_DEV_BYTES (same sha AFTER).
  Also confirmed rebuilt bundle sha = dev-modified `HEAD:` blob sha of assets-containing bundle.
  Determinism LAW satisfied: my rebuild of the exact same inputs == dev's bytes.

## V-3 — Boot-checks, both surfaces, 88xx, with 404-sanity: **PASS**

- Ports: 8810 = plain static serve of repo ROOT (python http.server) →
  A3a URL http://127.0.0.1:8810/prototype/builds/v8-playable.html;
  8811 = quirk serve (prototype/server.py) → A3b URL http://127.0.0.1:8811/builds/v8-playable.html.
  Both served the SAME rebuilt bundle (current worktree bytes).
- 404-sanity of the serving conditions (curl):
  - 8810: `/prototype/art-direction/3d/assets/weapons/dagger-curved-pixelated.glb` → **404**
    (the pre-fix-bug URL; misresolution would 404), `/art-direction/...` → **200**, page → 200.
  - 8811: page → 200; `/art-direction/...` → 200 (quirk serve serves both).
- Tool: valspec harnesses first (cc_ls2_boot.js / cc_ls2_boot_dev.js), then a tightened
  variant (cc_ls2_boot_val.js: scores ONLY HTTP ≥400 responses for 404-sanity; argv fix;
  explicit MAIN-RESP). Chromium headless-shell-1243 (playwright-core 1.65.0). No simulation.
- A3a (8810, tightened run, exit 0): MAIN-RESP 200;
  `boot barrier: 51 critical assets settled (0 stand-ins); streaming 29 more`;
  `loaded 80 assets, 0 stand-ins`; SUBSTITUTION-LINES 0; HTTP4XX-TOTAL 0; GLB-HTTP4XX 0;
  pageerrors 0. ALL-GATES: PASS.
- A3b (8811, tightened rerun, exit 0): MAIN-RESP 200; same two lines; SUBSTITUTION-LINES 0;
  HTTP4XX-TOTAL 0; GLB-HTTP4XX 0; pageerrors 0. ALL-GATES: PASS.
- Cross-evidence (serve access logs, independent of the browser): 8810 log shows the
  404-vs-200 fingerprint pair (01:29:02) and only 200s thereafter; 8811 log shows every
  art request 200 during the boot — zero 404s server-side on either surface.
- Harness artifacts explained (not gate breaches): (a) first-pass a-run's single
  `REQFAILED …/v8-playable.html` = chromium navigation-race cancellation of the main doc;
  page demonstrably booted (both gate lines + full stream logged; serve log shows 200).
  (b) b-run ERR_ABORTED lines = in-flight request cancellations (loader race/dedupe);
  serve log shows those paths served 200. (c) b-run exit-code 2 in the first pass was my own
  harness-arg misuse (passed URL as the argv3 OUT path → ENOENT on writeFileSync 'http://…')
  — fixed in the rerun; gates inside that log still printed PASS. (d) `STANDIN-WARNINGS: 2`
  in that log = the two summary lines matching /stand-in/ regex; 0 actual `substitution:` lines.

## V-4 — Pre-fix failing-evidence file: **PASS**

- io/specs/cc-ls2-prefix-evidence.txt EXISTS (sha256 871d1cd3…9a0d09).
- Header intact: capture time 2026-11-08T01:22:34Z; worktree /tmp/wh-worldfeat
  HEAD b006d5687c6b8d82467bc815b2890ee002db1c71; UNFIXED resolveUrl bundle built at 410cc81;
  plain static serve of repo ROOT (port 8801); harness cc_ls2_boot.js.
- Pre-fix spec sha256 recorded = 2836d48c…705f5 → matches my measured sha of the FROZEN
  spec file today (byte-identical spec when evidence was captured). ✔
- Failure fingerprints (verified by grep, counts exact):
  - `boot barrier: 51 critical assets settled (51 stand-ins)` ✔ (line 12 + line 31)
  - `loaded 0 assets, 80 stand-ins` ✔ (line 13 + line 32)
  - 15 unique `NET: 404 /prototype/art-direction/...` misdirected-URL lines ✔ (line 51: total 40 HTTP 4xx)
  - 13 shown `substitution: procedural stand-in` lines (stated ≥12 of 80 total) ✔
  - `pageerrors=0` ✔
- The evidence proves the test FAILS pre-fix (404s + 51 stand-ins + 0 loaded) — i.e. the boot
  check genuinely discriminates the bug. ✔

---

## Base-line anomaly (noted, NOT a defect of this round)

Commit b006d56 itself commits a build bundle (`prototype/builds/v8-playable.html`, +5/−1 diff
vs its parent, title stamp `(…410cc81)`), i.e. HEAD's own baseline already contains a
prior build's bytes. This is outside CC-LS2's uncommitted delta (round's code change =
assets.js only, verified in V-1). Flagging for the release owner because commit + build
in one commit is unusual for this repo's law (separate build commit); no action taken by me.

## Verdict summary

| Valspec item | Result |
|---|---|
| V-1 change-scope (single seam, single file + rebuilt bundle only) | PASS |
| V-2 HEAD-rebuild byte-identity (modulo known title-diff) | PASS |
| V-2.2 comment-line presence in rebuilt bundle | PASS |
| V-2.3 worktree-rebuild == dev's committed work (bytes) | PASS |
| V-3a boot @8810 plain-serve root (barrier 51/0, loaded 80/0, 0 subst, 0 4xx, 0 pageerrors) | PASS |
| V-3b boot @8811 quirk serve, no regression (same gates) | PASS |
| V-4 pre-fix evidence exists + shows 404 / 51-stand-ins failure | PASS |

FINAL VERDICT: PASS

— Testerbot (independent), 2026-11-08. No tracked files modified by validator; no git
history operations performed (NO-GIT); all serves on 88xx ports and stopped after the run.
