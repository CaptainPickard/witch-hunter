# CC-H2b VALSPEC — Testerbot validation spec (garrison supply nodes)

Written by IO INLINE (disclosed deviation): two Testerbot valspec children ran
their full censuses then died at max_iterations one step before writing the
file (deleg_69c4ca2d + deleg_5ff29875, 2026-11-07 08:29 + 09:19). Their census
results are folded in and are consistent with IO's. The Testerbot verdict seat
for the BUILT CODE later in the gate is still dispatched independently — only
this valspec document is inline.

Round: CC-H2b. IO spec: io/specs/2026-11-07-cc-h2b-garrison-supply-spec.md.
Census baseline (both children + IO agree): regionH block CONFIG.js lines
1880-2016 (props close at 2016, global scatter block follows 2021); props 66
rows landed; no nodes key exists; gather.js NodeManager (game.js:1831) reads
every region's cfg.nodes generically; nodeTypes bonePile/ironVein landed;
lightSockets-bearing assets banned; whWallA/B without wall: key take one trunk
collider. NodeManager purities it checks: registry warn on unknown type
(gather.js:38), placement pools keyed 'rid:type' (gather.js:49), heightAt seat
(gather.js:60), respawn per def (gather.js:90+).

## Validation procedures (run from /tmp/wh-worldfeat; plain python3/grep only)

V-1 Nodes exact-set check: parse the landed regionH block's nodes rows; assert
    EXACTLY these 11 (type,x,z float-equal, zero extras, zero misses):
      bonePile: (-56,-1032) (-63,-1044) (-50,-1044) (22,-1046) (-20,-992)
                (-13,-986) (13,-986) (44,-996)
      ironVein: (66,-1042) (58,-1050) (44,-1022)
    Cross-check each against scratch/cc-h2b/seat-scan.py's frozen seats AND
    rerun that script on the landed config (it must read the landed rows or
    the frozen tuples; either way assert 15/15 PASS output).
V-2 Props append-in-order check: HEAD props had 66 rows ending with the whWallA
    row at x -14.99 z -945.42. After build: rows 67-70 are EXACTLY
      b6Bones 46,-1076 rotY 2.4 scale 1
      rubblePile 36,-1042 rotY 0 scale 1
      okFenceStonewall -66,-1024 rotY 1.57 scale 1
      graveMound -58,-1008 rotY 0 scale 1
    (count 70, order preserved, no other prop row changed).
V-3 Byte isolation: `git diff HEAD -- prototype/js/CONFIG.js` must show
    insertions ONLY within the regionH block (line range 1880-2016 + the new
    lines; use `git diff -U0` and verify every hunk header references lines
    inside that window). Additionally: `git diff --stat HEAD` must name ONLY
    prototype/js/CONFIG.js + scratch/cc-h2b/seat-scan.py (+ io/specs + io/
    reports + docs/planning doc-66 amendment rows if present); game.js and all
    other prototype/js files byte-identical (git diff --name-only).
V-4 Law checks (grep on CONFIG.js regionH block): (a) no 'torch|whTent|
    whCampkit|banditCampfire|lanternPost' row among the 4 NEW props rows (grep
    the appended lines only, not whole block — landed rows legitimately carry
    them); (b) no new whWallA|whWallB row at all; (c) nodeTypes block untouched
    (git diff shows no hunk touching CONFIG.gather.nodeTypes); (d) no
    lightSockets key added anywhere.
V-5 Engine purity + registries: gather.js nodeTypes warn path will not fire —
    assert every landed node type string is in CONFIG.gather.nodeTypes
    (bonePile, ironVein). Assert region-defs.js registers regionH unchanged
    (makeRegion row present, no diff).
V-6 Build + marker proof: run `python3 tools/build_v8.py` in the worktree
    (exit 0). Then grep prototype/builds/v8-playable.html for: the 11 node
    rows' signature strings (e.g. 'x: -56, z: -1032'), the 4 new prop rows
    ('b6Bones', x: 46, z: -1076'), AND the prior markers unchanged (CC-AF2
    count == 3, WH_AFF count == 24, fort_garrison count == 5, regionH count
    == 7 as measured 2026-11-07 pre-round).
V-7 Save purity: `git diff HEAD -- prototype/js/save.js` empty; no new save
    block keys in CONFIG.js diff hunks (nodes/props are runtime data, not
    save state).
V-8 Verdict: write io/reports/2026-11-07-cc-h2b-validation.md with per-V
    results, PASS/FAIL per criterion, adjudications for any deviation
    (whitespace/comment diffs disclosed, never seats or laws).

## Verdict template

  CC-H2b validation verdict
  V-1..V-8: each PASS/FAIL + evidence line
  Verdict: PASS (zero blocking) / PASS with adjudications / FAIL
  Deviations: listed with ADR ids
