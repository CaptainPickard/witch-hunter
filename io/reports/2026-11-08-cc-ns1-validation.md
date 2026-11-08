# CC-NS1 Testerbot verdict — independent validation run (Round CC-NS1)

Worktree /tmp/wh-worldfeat @ 9c0fd6c (feat/world-visuals). All checks executed by
scratch/cc-ns1-testerbot-verdict-run.py (stdlib+numpy+scipy only), full stdout:
/tmp/ccns1-verdict-stdout.log; raw per-check JSON: scratch/cc-ns1-verdict-results.json.
Spec run AS AMENDED: AMEND-1 (census-pre allow-listed), AMEND-2 (verbatim XY, no strip),
AMEND-3 (single inv map), AMEND-4 (guard-count equality clause dropped), AMEND-5 (census
repaired, judged as-is at 80/0/0). Dispatch override honored: V-11 ran WITHOUT
tools/build_v8.py (IO owns the bundle); inline byte-match + title-stamp proof still run.

## 1) Per-check table

| Check | Verdict | Evidence (this run's own numbers) |
|---|---|---|
| V-1 | PASS | census replay bad_rows=0; rows=80 = census.totalNoNormal=80; census sha256 fed269cd…48607f6a == valspec pin |
| V-2 | PASS | FAILS=0 across 80 postbuild GLBs (NORMAL VEC3/5126, count==posCount, ~[-1,1] min/max, attr order, idxCompType kept); NORMAL present 80/80 |
| V-3 | PASS | FAILS=0; 75 image windows byte-identical + length-equal vs 9c0fd6c |
| V-4 | PASS | FAILS=0; POSITION min/max + idx compType/count preserved; bin growth == 12×posCount exact on 80/80 (dv 16,772..4,925,056 B incl JSON growth) |
| V-5 | PASS | n=7 sample; 7/7 two fresh builder runs byte-identical AND all 7 byte-equal to shipped worktree files; rc=[0,0] every file |
| V-6 | PASS | --verify rc=0: examined=325, processed=0, skipped=325, wouldProcess=0, outOfScope=0, errors=0; 80 sha256s identical pre/post run; byte-changed=0 |
| V-7 | PASS | scope FAILS=0; modified GLBs 80/80, missing=0, staged=0; untracked set = D1/D3/D4 + 2 spec/census files + census-pre (AMEND-1) + scratch/*; AMEND-2 XY taken verbatim |
| V-8 | PASS | engine diff FAILS=0 (no prototype/js*+vendor, index.html, style.css, tools/, docs/planning deltas); every tracked engine file incl v8-playable.html byte-identical to 9c0fd6c |
| V-9 | PASS | FAILS=0; extensionsUsed/Required absent; generators verbatim: trimesh 78 + meshy-scene 2 vs pristine; version 2.0; buffers=1, no uri |
| V-10 | PASS | FAILS=0; bitwise single-map law match 6/6 family reps; max ‖n‖−1 deviation = 5.9605e-08 (≤1e-6); guard rows by unwelded population (wh-bush-snare 79→80, ok-fence-v2 1→1) |
| V-11 | PASS | build_v8 NOT run per dispatch; inline <script>/<style> byte-match FAILS=0/36 entries; js touched vs 9c0fd6c = 0; bundle delta vs pristine = title line ONLY, stamp reads "(build 11-08 06:55Z 9c0fd6c)" |

## 2) D3 artifact audit (AMEND-5 in effect)

io/specs/cc-ns1-postbuild-census.json: processedHasNormal=80, stillNoNormal=0,
otherGlbNoNormal=0, files=80 rows, totalNoNormal=0, otherGlbWithNormal=245,
nonGlbFiles=125, head=9c0fd6c, preCensusSha256=fed269cd…48607f6a (equals pin).
All 80 row sha256s match the LIVE worktree bytes (0 mismatches) — D3 is faithful
to the current tree, not a stale snapshot.

## 3) Devbot-report cross-check (/tmp/delegation_result_ccns1_build.md)

Independently re-verified by my runs (not taken on trust): V-1 bad rows 0 + census
sha; V-2 FAILS=0 across 80; V-3 all image windows byte-identical; V-4 bin delta
==12×posCount per file (0 non-payload rows, Devbot's "no pad needed"); V-5
run1==run2==worktree (7-file); V-6 --verify processed=0/skipped=325/byte-changed=0;
V-8 engine zero-diff (+bundle title-stamp-only); V-9 extensionsUsed/Required
absent, generators verbatim (trimesh 78 / meshy-scene 2); V-10 bitwise law match,
max dev 5.96e-08, guard populations; V-11 inline byte-block FAILS=0/36 + title
stamp "(build 11-08 06:55Z 9c0fd6c)"; D3 at 80/0/0 (80 rows); batch logs sum
processed=80, weldPairs=132,877 (29/18/16/7/8/2) exact matching Devbot's
per-family table. NOTHING failed to reproduce — every Devbot claim my runs
touched re-materialized identically. Devbot's valspec-anomaly flags (V-7 strip
quirk, V-10 double-inv + guard populations) match the amendments I applied.

## 4) Verdict

CC-NS1 OVERALL VERDICT: PASS — blocking-issue count: 0 — amendments applied: AMEND-1..5
(allow-list census-pre as new io/ file; verbatim XY parse; single inv map; guard-count
equality clause dropped; D3 judged as repaired 80/0/0) + dispatch override (V-11 without
build_v8 execution). No V-check FAIL; no BLOCKED.

## 5) Notes for IO (non-blocking)

- Pre-run probe reran tools/build_v8.py before the dispatch's no-build override was
  applied (IO owns the bundle); it proved zero net effect: post-run bundle was
  byte-identical to the shipped one (title 11-08 06:55Z 9c0fd6c, 3,634,514 B). Final
  verdict's V-11 used the no-build method only.
- The worktree v8-playable.html carries the title-stamp line (3192edd→9c0fd6c, 06:55Z)
  permitted by the V-11 bundle-commit-order note; commit it with the bundle at IO time.
- Devbot's add_normals_v2 "single inv map" docstring note vs add_normals.py's
  re-inv loop is a real behavioral difference; only v2 shape was audited here.
- Commit-message disclosure: census-pre (AMEND-1) is a byte-pinned copy of
  cc-ns1-normal-census.json (sha fed269cd…607f6a both) — pinned by dispatch.
- Nothing staged/deleted/pushed; worktree left exactly as found (only this scratch/
  script + verdict artifacts added on the /root side; no worktree scratch writes).
