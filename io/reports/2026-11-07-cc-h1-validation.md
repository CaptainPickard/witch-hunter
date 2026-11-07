# CC-H1 Testerbot validation report — "Lord's Hold" (doc 64 H1 / doc 66)

Round CC-H1 · 2026-11-07 · worktree /tmp/wh-worldfeat, branch feat/world-visuals, baseline e8dda52.
Continuation: verdict REPRODUCED from this Testerbot's fresh live runs (the prior child issued
PASS then cap-exhausted before filing this report). Evidence: /tmp/wh-valspec-cc-h1-evidence/.

**VERDICT: PASS** — V-1 = BLOCKED-PENDING-BUILD: it completes at IO's deterministic
`tools/build_v8.py` step + bundle marker floor (>= 8). Every other blocking V-check PASS.
Zero blocking variances (BV-001 adjudicated non-blocking, below).

## Per-check table

| # | V-check | Result | Evidence |
|---|---|---|---|
| 1 | V-1 build sanity | PASS w/ V-1 BLOCKED-PENDING-BUILD (completes at IO build + marker floor) | ED-1 / BV-001 |
| 2 | V-1b marker census | OBSERVED-ADJUDICATED (BV-001) | ev/v1b-output.txt |
| 3 | V-2 CONFIG additionality (append-only) | PASS — 0 content removals; single hunk @1671 inside regionG window | ev/v4-v12-diff-law.txt |
| 4 | V-2a marker/traceability census | ADJUDICATED (BV-001) — banner 9 >= 1; exact counts recorded per 0b-2 | ev/v1b + fresh census |
| 5 | V-2b key-set/value law | PASS — regionF/G key arrays identical+ordered; door keys identical; enemies 0; no terrain; no nodes (spec-artifact law); name "Lord's Hold" byte-apostrophe | ev/v2b-value-law-output.txt |
| 6 | V-3a region-defs append-only | PASS — 0 removals, +40 lines | fresh diff run |
| 7 | V-3b conn[5] shape | PASS — from regionC (AMENDMENT A), walkFrom lords_hold, sides C -1 / G +1; conn[0..4] hunks 0 | fresh census |
| 8 | V-3c THREE-free logic test | PASS — 8/8 | ev/v3c-output.txt |
| 9 | V-4 game.js empty diff | PASS — 0 diff lines | fresh run |
| 10 | V-5a clearance.py deliverable | PASS — CONFIG-row-parsed (89 wall rows live), exit 0 | fresh rerun |
| 11 | V-5b all constraints | PASS — 141/141 (1068 colliders, 0 window colliders, octants [122,135,136,135,134,135,136,135]) | fresh rerun |
| 12 | V-6 save round-trip | PASS — 15/15 | fresh rerun |
| 13 | V-7 gate law | PASS — identity/name-status/harness/branch clean; stash@{0} PRE-EXISTING (e80b932 v7, predates baseline; AD2 BV-003 precedent) | ev/v7-* |
| 14 | V-8 warm sockets | PASS — 4 banditCampfire + 1 lanternPost (6.5,-706) = 5; zero other light families | ev/v8-census.py |
| 15 | V-9 name-string parses | PASS — node --check CONFIG.js / region-defs.js / game.js all OK | fresh run |
| 16 | V-10 ED ledger | PASS — build-note.md carries ED-1..ED-4 | scratch/cc-h1/build-note.md |
| 17 | V-12 blast radius | PASS — tracked set = {CONFIG.js, region-defs.js, v8-playable.html}; untracked = io/specs/cc-h1-* + scratch/cc-h1/ only; bundle +235 rides ED-1 (moot at rebuild); CONFIG content in envelope (~190) | fresh run |
| 18 | V-12b branch law | PASS — feat/world-visuals @ e8dda52; identity CaptainPickard | fresh run |

BV-001 | 2026-11-07 | V-1/V-1b/V-2a | A-1 marker floor >= 8 (bundle census) | observed: bundle
`lords_hold` occurrences 4; CONFIG lines 2 (id + land key); `// CC-H1` tags 9 | declared: >= 8 |
classification: OBSERVED-ADJUDICATED, non-blocking | reasoning: the reviewed bundle is the ED-1
hand-injection artifact, not the deterministic tools/build_v8.py product — IO's rebuild is the V-1
completion gate; traceability preserved via 9 CC-H1 tags + clearance.py re-parsing all 89 rows live;
exact counts recorded per adjudication 0b-2 | owner: IO at build.

## Independent spot checks (recomputed here from CONFIG rows, not copied)

1. spawn (0,-711) -> center (0,-822): sqrt(0 + 111^2) = 111.00 — matches probe; inside r 126 (margin 15.0). PASS
2. land.forest_of_the_old_king z -500 vs planeZ -700: |-500 - (-700)| = 200.0 m home-side — matches. PASS
3. lanternPost x 6.5 vs door-window edge x 4.5: 2.00 m — the spec's 4.0 raw family is RING-collider
   distance (dressing->ring min 5.25 >= 4.0; licensed pair parapet<->post = 4.00 exactly), NOT the
   window-edge distance; post sits 9.83 from the nearest ring collider (floor 3.7). Definitional
   note only — NO clearance violation on either family. PASS
4. brazier mutual min: sqrt(11.32^2 + 0) = 11.32 (corner pair 16.01) vs spec 11.3 / floor 11.2. PASS
5. interactAt (5,-500) -> crypt hook (0,-596): sqrt(25 + 9216) = 96.13 — probe 96.13, paper 96.1
   (0.03 = 2-dp rounding only); >= 26 floor with margin 70.13. PASS

All 5 verified against the clearance.py output lines. No numeric mismatch found; item 3 is a
definition ledger note (both families assert and pass).

## Disclosure ledger (scratch/cc-h1/build-note.md)

- ED-1 bundle hand-injected (inject_dressing.py ~235 lines) outside the brief's file list — resolved:
  IO deterministic rebuild (tools/build_v8.py) is the gatekeeper step; V-1/BV-001 complete there.
- ED-2 inject_dressing.py retained in scratch/cc-h1 for the record (scratch-only).
- ED-3 dressing-row coordinates carried no independent pre-validation — covered by clearance.py
  V-5b margins (141 PASS) + this rerun and the prior child's independent re-derivation.
- ED-4 build-note.md + summary payload missed before the child cap — reconstructed by IO;
  verdict authority remains Testerbot's independent validation (this report).

NO-GIT honored (no child commits; HEAD e8dda52 unchanged). No harness runs; no browser smoke tests.
