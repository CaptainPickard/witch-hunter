# CC-AD2 — Testerbot Independent Validation Verdict (filed by IO)

Source: /tmp/wh-valspec-cc-ad2-evidence/verdict.md (Testerbot, 2026-11-06).
This file copies the verdict into the repo for the round record. The
transient /tmp evidence dir is NOT durable; this filing is.

- Validator seat: Testerbot (independent dispatch; round author/devbot is a
  different seat).
- Date (UTC): 2026-11-06 (dispatch stamp Fri Nov 6 15:33:41 UTC 2026).
- HEAD at validation start: 42e34c5 (full: 42e34c574c42bd306804cc475094f5bd3c550717)
- Baseline (D-5, pinned): f1f5eb7 (full: f1f5eb7ddd55cfa48bcb81240cb9458d4190a8e6)
- Valspec executed: io/specs/cc-ad2-veil-galleries-valspec.md V-1..V-12
- Laws obeyed: no harness runs / no headless browser smoke tests /
  no automated playability checks (static census + CONFIG-parsed probe only);
  NO-GIT obeyed (read-only git); D-4 obeyed (worktree byte-identical
  pre/post, one pre-existing v7-era stash untouched); scratch copy deleted.

## Verdict table (V-1..V-12)

| Check | Criteria | Result | Evidence file | Variances |
| V-1 | A-6 | PASS | ev/v1-build-log.txt | none |
| V-2 | A-6 | PASS | ev/v2-restore-proof.txt | BV-003 (non-blocking, pre-existing stale artifact) |
| V-3 | A-6 | PASS | ev/v3-marker-counts.txt | none |
| V-4 | A-1 | PASS | ev/v4-regionf-census.json | none |
| V-5 | A-2 | PASS | ev/v5-regione-trio.txt | BV-001 (non-blocking, pre-adjudicated by IO) |
| V-6 | A-3 | PASS | ev/v6-conn4-census.json | none |
| V-7 | A-3 | PASS | ev/v7-z-guard.txt | none |
| V-8 | A-4, A-9 | PASS | ev/v8-gamejs-empty.txt | none |
| V-9 | A-5 | PASS | ev/v9-probe-rerun.log | none |
| V-10 | A-7 | PASS | ev/v10-spawn-validator.log | BV-002 (non-blocking, method deviation licensed by IO note) |
| V-11 | A-8 | PASS | ev/v11-walkback-lands.txt | none |
| V-12 | A-9 | PASS | ev/v12-blast-radius.txt | none |

## Verdict line

ROUND VERDICT: **PASS**

Reasoning: every V-check row PASS (12/12); variances.csv contains zero
BLOCKING rows (3 rows, all non-blocking: BV-001 mourner-seat drift
pre-adjudicated by IO in scratch/cc-ad2/io-adjudication.md; BV-002
spawn-validator method deviation executed per the binding IO method note
(static substitute — no runtime validator CLI exists); BV-003 pre-existing
stale debris from the earlier dead CC-AD2 dispatch inside the transient
evidence dir, removed, not a round artifact); V-2 final restore proof clean
(porcelain byte-identical pre/post, stash@{0} v7-era untouched, scratch dir
gone). All three gate conditions hold.

## Headline numbers

- V-1: rebuild in isolated scratch copy, exit 0, bundle 3,370,962 bytes,
  sha256 17200e06aa3fd612f6874dbf62223f161c92d2a9b05d5ff0d6078b4463dd3f50 ==
  landed artifact (byte-identical).
- V-3: markers 'veil_galleries' = 9 (>= 8 declared); 'The Erased Galleries'
  = 1 (>= 1).
- V-4: regionF 17-key census exact on every declared value (id veil_galleries,
  center (0,-640), r 26, groundSeed 1662061329 fresh, fog 0x0a0810 @ 0.145,
  ambient 0.055, 2 ghouls, door/land rows per spec §2).
- V-5: exactly 1 deletion (whWallB (-8.3,-612.0)) + 2 additions (mourner pair
  at the IO-adjudicated seats); 19/19 common regionE prop rows preserved.
- V-6/V-7: connections[4] shape-identical to connections[3] except licensed
  fields; zero plane/z-logic lines touched; conn[3] untouched.
- V-8: game.js diff EMPTY (blob SHA equal baseline->tip).
- V-9: probe re-run ALL CONSTRAINTS: PASS, 85 checks, CONFIG-parsed source of
  truth audited (zero literal-derived F rows).
- V-10: static spawn-shape check + probe law coverage (spawn 12.76 m clear of
  nearest ring collider; props/enemies inside play radius; ghoul spacing
  12.51 m) — method as licensed by IO.
- V-11: two-direction chain walkback lands verified CONFIG-parsed (E land
  (0,-604); F land (0,-650), 10 m inside the mouth plane >= 8 law).
- V-12: blast radius = declared set only (bundle, CONFIG.js, region-defs.js)
  plus round-authored io/specs x2 + scratch/cc-ad2 x4 (round commit files).

## Post-verdict IO acts (gate step 5)

- BV-002 remedy: valspec V-10 amended with the licensed static substitute
  method (IO method amendment block, 2026-11-06).
- BV-003 remedy: stale 2.6 GB dead-dispatch worktree copy removed from the
  transient evidence dir (disk reclaimed; no git-state write; git state
  re-verified identical after).
- Verdict filed to io/reports/2026-11-06-cc-ad2-validation.md (this file).
