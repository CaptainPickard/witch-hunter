# Testerbot Validation Spec — CC-AD2 "The Erased Galleries"

## 0. Scope and authority

- Round: **CC-AD2** (world-visuals chain). Worktree: `/tmp/wh-worldfeat`, branch `feat/world-visuals`.
- Authority: `io/specs/cc-ad2-veil-galleries-spec.md` (IO spec, gate step 1). This valspec maps **every acceptance criterion A-1..A-9** of that spec to concrete V-checks. Where wording differs, the IO spec wins.
- Style parent: `io/specs/cc-ad1-veil-crypt-valspec.md` (CC-AD1, landed commit `6e9f8bc`). Chain context: `io/specs/cc-ad1-veil-crypt-spec.md`. Doc 47 strata V2 section is the content authority for strata rows.
- Pre-spec probe: `scratch/cc-ad2/cc-ad2-round-note.md` — its findings define the ground truth Testerbot re-verifies in V-9.
- Engine ground truth fixed for this round:
  - plane logic is **z-hard-coded** — no plane/z changes are licensed;
  - `conn[4]` **reuses the crypt `conn[3]` shape** with `walkFrom veil_galleries`;
  - landed crypt rows live in `prototype/js/CONFIG.js` (regionE block) and `prototype/js/region-defs.js` (`connections[3]`).
- Testerbot delivers a verdict table, per-check evidence with raw command output, and worktree restoration proof. Testerbot **never fixes code**; a FAIL returns to Devbot via IO.
- NO-GIT law: Testerbot never commits, pushes, creates refs, or amends anything. Its entire deliverable is the evidence bundle + verdict.

## 1. Execution order (deterministic)

1. Snapshot: record `git rev-parse HEAD`, `git status --porcelain`, `git stash list` into the evidence dir.
2. V-1, V-2 (rebuild + restore) run **first**, in an isolated copy; worktree must be verified restored before any other check.
3. Static census: V-3, V-4, V-5, V-6, V-7, V-8, V-12.
4. Runtime / behavioral: V-9, V-10, V-11.
5. Package evidence, adjudicate variances, emit verdict table.

## 2. Diff-basis law (governs all V-checks)

- **D-1 — Diff-basis law.** All diff, census, and count checks are evaluated against the **landed diff** (Devbot's round tip vs. the pre-round baseline: the previous round's landed state, i.e. the commit Devbot started from). Testerbot's rebuilt artifacts are never the diff basis.
- **D-2 — Rebuild-in-worktree law.** For the sha256 rebuild identity check (V-1), Testerbot rebuilds the bundle **in an isolated copy of the worktree** (a scratch directory copy, not the live worktree), compares digests, and discards the copy. Rebuild output never mixes with the live tree.
- **D-3 — Restore law.** After any build/rebuild act, Testerbot restores the live worktree and proves it: `git status --porcelain` byte-identical to the D-1 snapshot, `git stash list` unchanged, and the scratch copy deleted from disk. A pre/post snapshot pair is recorded for every check.
- **D-4 — Read-only guarantee.** Testerbot writes evidence only to `/tmp/wh-valspec-cc-ad2-evidence/` (outside the worktree). It never edits `prototype/`, `js/CONFIG.js`, `region-defs.js`, `game.js`, or any spec file.
- **D-5 — Baseline pinning.** The baseline commit is recorded once in the evidence header; every diff command in this spec uses that explicit SHA, never `HEAD~1` or symbolic references that could drift.

## 3. Check matrix — A-1..A-9 → V-checks

| Criterion | V-checks | Check family (from IO spec) | Blocking law |
|---|---|---|---|
| A-1 | V-4 | CONFIG regionF exact key/value census (groundSeed differs; numerics +-0.05) | any missing/extra/differing key = blocking |
| A-2 | V-5 | regionE one-deletion/two-additions diff law | any regionE change outside the declared trio = blocking |
| A-3 | V-6, V-7 | region-defs conn[4] shape census; z-hard-coding guard | any shape deviation beyond licensed fields = blocking; any z/plane edit = blocking |
| A-4 | V-8 | game.js empty-diff law | any diff line = blocking |
| A-5 | V-9 | Probe re-run PASS with CONFIG-parsed rows | any literal-derived row or variance = blocking |
| A-6 | V-1, V-2, V-3 | Build reproduction + sha256 rebuild identity + worktree restore + bundle marker census (>= 8) | any digest mismatch OR marker count < 8 = blocking |
| A-7 | V-10 | Spawn-validator shape checks | any malformed-shape finding = blocking |
| A-8 | V-11 | Chain walkback land-row checks | any direction mismatch = blocking |
| A-9 | V-8, V-12 | game.js empty-diff law + global blast-radius sweep | any diff line in game.js OR any change outside declared files = blocking |

NOTE (IO alignment 2026-11-06, gate step 2 close-out): criterion NUMBERS
aligned to the IO spec's §7 list (draft labeled them by theme in a different
order). Criterion SUBSTANCE and V-check scope unchanged. Where numbering ever
disagrees again, the IO spec §7 list is authoritative.

Every criterion maps to at least one check; every check maps to at least one criterion. Unmapped criteria: none.

## 4. V-checks

### V-1 — Build reproduction: sha256 rebuild identity law (A-1)

- **Law:** rebuilding the prototype bundle from the landed tree must reproduce **byte-identical artifacts**; identity is expressed as sha256 equality between the fresh rebuild and the landed copies of the same paths.
- **Method:**
  1. Copy the worktree to a scratch directory (D-2); record `git rev-parse HEAD` and `git status --porcelain` in both.
  2. In the scratch copy, run the documented build command from IO spec §build (same entry Devbot used; the round note records it).
  3. Compute `sha256sum` over every build artifact the spec lists and over the landed copies of the same paths in the live worktree.
  4. Emit a per-file digest table: path, landed sha256, rebuilt sha256, equal true/false.
- **Pass rule:** every row reports `equal: true`. One mismatched digest = blocking variance, round FAIL for A-1.
- **Restore (D-3):** scratch copy deleted; live worktree untouched (it was never written to).

### V-2 — Worktree restoration + hygiene (A-1, D-3)

- **Method:** after V-1 and again at the very end, capture `git status --porcelain`, `git stash list`, `git rev-parse HEAD` and diff them against the §1 snapshot.
- **Pass rule:** byte-identical snapshots; no new untracked files, no modified tracked files, scratch directory gone (`test ! -d <scratch>`).
- **Fail rule:** any delta = blocking variance on the process, reported even if all other checks pass.

### V-3 — Bundle marker census (A-2)

- **Method:** count required markers in the **built bundle** (the artifact from V-1's landed state), e.g. `veil_galleries` occurrences, the region display-name marker ("The Erased Galleries"), strata/doc-47 label markers, and any marker the IO spec A-2 census row declares. Use `grep -c` / Python `str.count` — no eyeballing.
- **Pass rule:** every declared marker count exactly equals the IO spec's declared number;Testerbot copies the declared counts into the verdict table so the numbers are asserted, not assumed.
- **Fail rule:** any count mismatch = blocking; Testerbot prints observed vs. declared per marker.

### V-4 — CONFIG.js regionF exact key/value census (A-3)

- **Method:**
  1. Load `prototype/js/CONFIG.js` and extract the complete new **regionF** block introduced by the landed diff.
  2. Parse it (node / JSON-ish parse of the object literal) and dump every key with its exact value as JSON into the evidence file.
  3. Compare field-by-field against the IO spec A-3 census table: key name, key count, and each value verbatim (strings byte-exact, numbers value-exact, arrays element-exact).
- **Pass rule:** key count == table row count; zero missing keys; zero extra keys; zero differing values. "Extra key" is as blocking as a wrong value.
- **Evidence:** the dumped census JSON plus a unified diff against the expected table.

### V-5 — CONFIG.js regionE one-deletion / two-additions law (A-3)

- **Law:** the landed diff of the regionE (crypt) block versus the pinned baseline (D-5) must contain **exactly one deletion line and two addition lines** — the crypt rows updated to hand off to the new region — and nothing else.
- **Method:**
  1. `git diff <baseline>..HEAD -- prototype/js/CONFIG.js`.
  2. Parse hunks; isolate lines intersecting the regionE block; count `+` and `-` lines ignoring the hunk headers themselves.
  3. Classify each line and match content (not just count) against the trio the IO spec declares (the deleted row; the two added rows, which must align with V-10's spawn expectations).
- **Pass rule:** count is exactly 1 deletion + 2 additions **and** each line matches its declared content. Any other regionE change — an extra edit, a changed value, a reordered row — is blocking.

### V-6 — region-defs.js `conn[4]` shape census (A-5)

- **Law:** `connections[4]` must **reuse the crypt `connections[3]` shape**: identical key sequence, same field count, values differing **only** in the fields the IO spec licenses (per spec: at most the target / walkFrom / land fields it declares). `connections[3]` itself must be untouched.
- **Method:**
  1. Parse `prototype/js/region-defs.js`; dump `connections[3]` and `connections[4]` as JSON.
  2. Deep-compare: assert identical key enumeration and order; list every field where values differ.
  3. Assert each differing field is in the IO spec's licensed list; assert `conn[4].walkFrom` is exactly the literal `veil_galleries` (literal preservation — no normalization).
  4. `git diff <baseline>..HEAD -- prototype/js/region-defs.js`: zero changed lines under `connections[3]`.
- **Pass rule:** shapes identical except for licensed fields; walkFrom literal exact; conn[3] diff hunk count == 0. Any unlicensed differing field = blocking.

### V-7 — Plane-logic z-hard-coding guard (A-5)

- **Law:** plane logic is z-hard-coded; the round must not touch z logic, plane geometry, or any plane-logic path, and `conn[4]` must not introduce a z-type field.
- **Method:**
  1. Enumerate the landed diff's touched files and hunks; flag any hunk intersecting plane-logic code (per the round note's engine context).
  2. Inspect `conn[4]` (from V-6's dump) for any z-like field; assert absent.
- **Pass rule:** zero diff lines in plane-logic paths; no z field in conn[4]. Any hit = blocking.

### V-8 — game.js empty-diff law (A-4 and A-9)

- **Law:** the landed diff for `prototype/js/game.js` must be **empty**: zero lines added, zero removed, and `sha256sum prototype/js/game.js` at the round tip equals its sha256 at the pinned baseline.
- **Method:** `git diff --stat <baseline>..HEAD -- prototype/js/game.js` → expect empty; compute both digests and assert equality.
- **Pass rule:** empty diff stat AND equal digests. Both A-4 and A-9 verdict rows cite this check's evidence. A single byte = blocking.

### V-9 — Probe re-run PASS with CONFIG-parsed rows (A-6)

- **Law:** every probe row in `scratch/cc-ad2/cc-ad2-round-note.md` that the probe previously parsed from literals must now parse from **CONFIG / region-defs** (CONFIG-parsed rows), and the re-run verdict must be PASS with zero variance rows.
- **Method:**
  1. Re-run the probe procedure documented in the round note against the post-build state.
  2. For each row record its source of truth: `CONFIG-parsed` (from CONFIG.js / region-defs.js) or `literal` (hard-coded).
  3. Assert every row is CONFIG-parsed; assert zero variance rows; assert final probe verdict PASS.
- **Evidence:** full probe output file; per-row source-of-truth tally.
- **Pass rule:** all rows CONFIG-parsed, zero variance, verdict PASS. One literal-derived row = blocking.

### V-10 — Spawn-validator shape checks (A-7)

- **IO method amendment (2026-11-06, gate step 5; remedied variance BV-002):**
  there is NO standalone validator CLI — the spawn validator
  (`validateSpawnSides`) is runtime-only inside the engine. The licensed
  execution is the STATIC substitute: (a) CONFIG-parsed shape census of the
  regionF spawn row and the two appended regionE rows per spec §2/§3 (no
  literals), plus (b) the CONFIG-parsed probe covering the validator's
  per-region engine laws (props/enemies inside play radius minus margin;
  spawn clear of collider circles; ghoul holdable spacings — via a static
  supplement of the law values). Runtime validator execution is NOT required
  for A-7; a future valspec may re-license it if the engine exposes a CLI.
- **Method:**
  1. Run the spawn validator on the new region spawn row (the validator entry documented in the IO spec / round note).
  2. Assert the validator reports the `veil_galleries` spawn row well-formed against the spawn-shape schema (region id, position fields, entry semantics per spec A-7).
  3. Cross-check the two added regionE rows from V-5: the spawn handoff rows must be exactly what the validator consumes; no orphan references.
- **Pass rule:** validator exits clean (exit code 0 per its convention); zero malformed-shape findings; handoff rows consistent with V-5's trio. Any finding = blocking.

### V-11 — Chain walkback land-row checks (A-8)

- **Method:**
  1. Walk back from `veil_galleries` to the crypt (regionE) over `conn[4]` → `connections[3]`, using the chain walkback procedure in IO spec A-8.
  2. Assert, per direction (galleries→crypt and crypt→galleries): landing region id correct; land-row identity matches the CONFIG/region-defs rows parsed in V-4/V-6 (not literals); no stale landing coordinates.
  3. Record observed vs. expected land rows in a two-direction table.
- **Pass rule:** both directions produce the declared land rows; a mismatch in either direction = blocking.

### V-12 — Global blast-radius sweep (A-9)

- **Method:**
  1. `git diff --name-status <baseline>..HEAD`: every touched file must be in the IO spec's declared file set (expected: build/bundle artifacts, `prototype/js/CONFIG.js`, `prototype/js/region-defs.js`; `game.js` must appear with zero lines per V-8).
  2. Within CONFIG.js and region-defs.js, assert changes are confined to the regionF block, the regionE trio (V-5), and connections[4] — no changes in unrelated blocks or other connection entries.
  3. Verify no spec, scratch, or prototype files other than the declared set were modified.
- **Pass rule:** zero files outside the declared set; zero hunks outside the licensed regions. Any hit = blocking (A-9).

## 5. Blocking-variance adjudication format

Every observed deviation is recorded as one row in `variances.csv` (evidence dir), in exactly this format:

```
BV-ID | UTC timestamp (from `date -u`) | V-check | criterion | observed value | declared/expected value | classification (blocking|non-blocking) | adjudication reasoning | resolution owner
```

- **Classification rules:** a variance is **non-blocking** only if BOTH hold: (a) it is pure formatting/whitespace/parsing-artifact with byte-identical parsed semantics, AND (b) the IO spec text explicitly licenses it. Everything else is blocking.
- **Adjudication:** Testerbot classifies and writes the row; it does not silently resolve. Blocking rows route to Devbot (code fix) or IO (spec amendment); Testerbot's round verdict is then FAIL pending the fix and a fresh run.
- **Owners used:** `Devbot` (code defect), `IO` (spec ambiguity), `Testerbot` (harness error — re-run required).
- BV-IDs are sequential: `BV-001`, `BV-002`, …

## 6. Verdict PASS/FAIL table

Emitted as the final evidence file `verdict.md`, one row per check (criterion columns follow §3):

```
| Check | Criteria | Result | Evidence file | Variances |
| V-1 | A-6 | PASS | ev/v1-digest-table.txt | none |
| V-2 | A-6 | PASS | ev/v2-snapshot-pair.txt | none |
| V-3 | A-6 | PASS | ev/v3-marker-counts.txt | none |
| V-4 | A-1 | PASS | ev/v4-regionf-census.json | none |
| V-5 | A-2 | PASS | ev/v5-regione-trio.txt | none |
| V-6 | A-3 | PASS | ev/v6-conn4-census.json | none |
| V-7 | A-3 | PASS | ev/v7-z-guard.txt | none |
| V-8 | A-4, A-9 | PASS | ev/v8-gamejs-empty.txt | none |
| V-9 | A-5 | PASS | ev/v9-probe-rerun.log | none |
| V-10 | A-7 | PASS | ev/v10-spawn-validator.log | none |
| V-11 | A-8 | PASS | ev/v11-walkback-lands.md | none |
| V-12 | A-9 | PASS | ev/v12-blast-radius.txt | none |
```

- **Round verdict = PASS** iff every V-check row is PASS **and** `variances.csv` contains zero blocking rows **and** V-2's final restore proof is clean.
- **Round verdict = FAIL** if any check row is FAIL, any blocking variance exists, or the restore law (D-3) was violated. The verdict line states which criteria gate the FAIL.
- A criterion with no mapping coverage, or a check whose evidence file is missing/empty, is FAIL by construction — the verdict may not be PASS on partial evidence.

## 7. Evidence bundle

- Directory: `/tmp/wh-valspec-cc-ad2-evidence/` (outside the worktree, per D-4). One file per check named `ev/vN-*.ext` as listed in §6, plus `snapshot-before.txt`, `snapshot-after.txt`, `variances.csv`, `verdict.md`, and the pinned baseline SHA in `header.txt`.
- Every evidence file carries the raw command line(s) that produced it and their raw output; no hand-written summaries in place of output.
- Final report to IO: verdict table + variances + restore proof, nothing else.
