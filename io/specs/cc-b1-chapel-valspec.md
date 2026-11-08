# CC-B1 · Ruined Chapel — Testerbot VALIDATION SPEC (io/spec — WAKE 34)

Written 2026-11-07 BEFORE Devbot starts. Source of truth for PASS/FAIL:
io/specs/cc-b1-chapel-spec.md rules R1-R9 (read them first). Worktree
/tmp/wh-worldfeat, branch feat/world-visuals, HEAD c78e4e7. NO-GIT: children
never commit/push; no harness runs, no headless browser smoke tests — offline
node/python probes are allowed (that is code QA).

## 0. Pre-round baseline (Testerbot recorded 2026-11-07, evidence for R8/R9)

- `git -C /tmp/wh-worldfeat status --porcelain` → `?? io/specs/cc-b1-chapel-spec.md` ONLY.
  `builds/` does NOT exist at HEAD c78e4e7 → after R8 build, a NEW
  builds/v8-playable.html IS the "output changed vs pre-round" evidence.
- CONFIG.js anchors: regionB at L368 (id darkwood_edge), props at L382,
  locked ruin rows L415-418, lightSockets at L98, scatter.keepOut at L2558,
  assets.js manifest L90-107. Lines drift as Devbot edits — grep, don't hardcode.
- RegionB dressing widths below are trimesh-measured today; probe MUST take
  cc13b WIDTH values verbatim for regionC-validated keys (mossBoulder 1.5,
  stoneCrossTilted 0.7, cemeteryGate 2.4, picketFence 2.0, gravestoneObelisk
  0.6, banditCampfire 1.2, lanternWaymarker 0.4, treeStump 1.0, yewTree 1.4,
  witchwoodTree 1.4, deadTree 1.2) and add ONLY the keys cc13b never held:
  the 7 new assets + churchPewBroken 2.002, ironFenceCorner 0.589, fallenLog
  1.862, livingOak 1.848, reachTreeA 1.558, reachTreeB 1.527, reachTreeC 1.411,
  lanternPostV3 0.585. Trees/reach keep the trunk ratio 0.25 (region-manager
  colliderRadius regex matches livingOak/reachTree).

## W-T. Measured nominal widths (REQUIRED TABLE — measured this session)

Method (re-run exactly, any tester/auditor):
`python3 -c "import trimesh; m=trimesh.load('<glb>', force='scene');
g=m.to_geometry() if isinstance(m,trimesh.Scene) else m; print(g.bounds, g.extents)"`
GLBs read at /tmp/wh-worldfeat/art-direction/3d/assets/church-kit/, scale 1,
units metres, vertex-bbox extents. nominal width = max(extent.x, extent.z).

| asset              | GLB file                     | ext.x | ext.z | height | nominal width | faces |
|--------------------|------------------------------|-------|-------|--------|---------------|-------|
| churchWallWindow   | church-wall-window-pixelated | 1.303 | 0.870 | 1.994  | 1.30          | 2000  |
| churchWindowFrame  | church-window-frame-pixelated| 0.911 | 0.265 | 1.989  | 0.91          | 2000  |
| churchRoofBeam     | church-roof-beam-pixelated   | 1.975 | 0.316 | 0.338  | 1.98          | 2000  |
| churchAltar        | church-altar-pixelated       | 1.993 | 1.411 | 1.161  | 1.99          | 1999  |
| churchPulpit       | church-pulpit-pixelated      | 1.083 | 0.979 | 1.999  | 1.08          | 2000  |
| churchPew          | church-pew-pixelated         | 2.002 | 1.079 | 0.982  | 2.00          | 1999  |
| candelabra         | candelabra-pixelated         | 1.940 | 0.688 | 1.979  | 1.94          | 1999  |

Probe WIDTH additions for NEW assets (copied verbatim into scratch/cc-b1_probe.cjs):
churchWallWindow: 1.30, churchWindowFrame: 0.91, churchRoofBeam: 1.98,
churchAltar: 1.99, churchPulpit: 1.08, churchPew: 2.00, candelabra: 1.94.
(Church-kit kit faces are decimated to ~2k per piece — the tri ledger in R7
relies on the per-GLB face counts above; re-measure if any GLB changes.)
Secondary widths for probe completeness (already-shipped keys cc13b lacked):
churchPewBroken 2.002 (2000 f), ironFenceCorner 0.589 (2000 f), fallenLog
1.862, lanternPostV3 0.585 (2500 f), livingOak 1.848, reachTreeA 1.558,
reachTreeB 1.527, reachTreeC 1.411. Trees/reach/stumps keep trunk ratio 0.25.

## P. Probe contract (scratch/cc-b1_probe.cjs)

Clone scratch/cc13b_probe.cjs structure: plain node (no three), parse
CONFIG.js regionB props/scatter as TEXT (brace-depth, no eval), mirror the
chapel NEW rows in its own table, geometric clearance checks, `process.exit(1)`
with a FAIL list on any rule, exit 0 otherwise. REQUIRED on stdout:
1. A SEAT TABLE, one line per NEW chapel row, columns (pipe-aligned like cc13b):
   `index | asset | x | z | rotY | scale | collider r | flags`.
   index = chapel row ordinal (K1..Kn or numeric); rotY/scale as written in
   CONFIG; collider r = width × scale / 2 (trunk ratio never applies to the
   7 new assets); flags = concatenated keys present on the row, at minimum
   `noCollide` (roof beams), `y<value>` (raised rows), `-` when none.
2. Headline line parsing state: `regionB props L<start>-<end>: N active rows
   parsed (M collider circles…)` — the chapel block excluded on re-runs via
   a `// CC-B1` marker comment, identical to cc13b's skip logic.
3. Per-rule evidence lines (see R1-R6 below) and a final
   `PASS: <summary>` or `FAIL (n): …` block. Exit 0 only when zero fails.
4. Tri ledger line (R7) and keepOut seat check (R6) MUST print even when the
   rest passes. A probe that cannot find the church rows (block not landed
   yet) must exit 1 with `no CC-B1 block in regionB props` — never exit 0.

## V1-R1 LANE (door sweep + protected row clearances)

Spec: every NEW chapel collider circle keeps ≥ 8 m edge distance from the B/C
door window segment (x −4..4, z −86) and from the A/B chokepoint corridor
(x ±6, z −25). No circle covers a gather node within 3 m, enemy spawn within
4 m, banditCampfire (2.5,−52) within 2 m, lanternWaymarker (−6.5,−47) within
1.5 m. Procedure:
- Probe computes for each NEW row: `dist(circle, segment) - r` vs both gate
  segments; prints per-row gate gaps in the seat table's evidence block.
  NOTE: CONFIG marks regionB's south boundary at z +25 while spec R1 says
  z −25 — probe tests the corridor segment at BOTH z −25 and z +25 (the nave
  sits at z −50..−66, > 40 m from either; symmetric test is cheap and safe).
  If this looks wrong to the eye, report it in the verdict, do not edit spec
  or CONFIG.
- Nodes/enemies/fire/waymarker: probe parses regionB `nodes:`/`enemies:` and
  the two light-row seats from CONFIG text; floor = clearance − r; fail below
  spec distances. Nodes (−14.4,−66.6), (−12.7,−48.1), (−17.0,−53.1) ARE within
  the nave footprint → R1 binds here; a FAIL is expected if walls seat over them.
  Measured now: altar (0,−65.5) sits 19.4 m from the B/C door sweep edge; nearest tree-collider gap 12.7 m (livingOak −22.3,−59.2).

## V2-R2 MUTUAL clearances

Spec: wall/window/gable/altar/pulpit pieces ≥ 0.6 m edge-to-edge (colliders
must not overlap), ruined wall gaps ≥ 2.5 m INTENTIONAL (two adjacent wall
rows at ≥ 2.5 mcentre distance with a comment count as PASS if the CONFIG
comment declares the gap); pews ≥ 1.2 m from each other AND from other
pieces; existing locked dressing (mossBoulder 17.1,−52.8; the four fallenLog
rows; treeStump 13.4,−58.7 / 13.0,−55.5 and every other pre-existing regionB
row) resolves ≥ 0.8 m vs NEW circles or the NEW row is re-seated — locked
rows never move. Procedure:
- Probe: pairwise NEW-vs-NEW with asset-class floors (0.6, 0.6, 1.2 pew) and
  NEW-vs-ALL-existing-rows at 0.8; prints every violating pair
  `asset(Lx) — asset(Ly): gap g < floor`. Existing rows parsed from CONFIG
  (they are in the parsed props list already) using cc13b widths + W-T
  additions; the `// CC-B1` marker block is excluded from the existing set.
- EXEMPT pair: candelabra vs churchAltar — spec seats candelabra ON the
  altar (same x/z on purpose, scale 1.0). Probe must exclude this pair
  from R2 (print `candelabra-on-altar: exempt`) and include it in R4 checks.
- Wall-line gaps: for churchWallWindow rows sharing a face (same nominal
  plane per spec seat), probe prints the sorted gap list; gaps ≥ 2.5 m are
  PASS only if that row pair's CONFIG line carries an inline `// gap`
  comment; a silent 1.0-2.4 m gap fails. Verdict quotes the 3 worst gaps.

## V3-R3 NO-COLLIDE discipline (AMENDED io 2026-11-07 wake 34: THREE raised
rows — two churchRoofBeam + one churchWindowFrame; the valspec was authored
before the spec's geometry pass finalised them)

Spec: `noCollide: true` ONLY on raised rows — the two churchRoofBeam rows
(y 3.8..4.2) and the one gable churchWindowFrame row (y ≈ 2.15, same x/z as
the altar). Ground rows carry no noCollide key (incl. the fallen rafter);
raised rows carry explicit y; the candelabra row carries explicit y with NO
noCollide (the altar stack). Procedure:
- `grep -n "noCollide" prototype/js/CONFIG.js` → every hit inside regionB
  chapel block must sit on a `churchRoofBeam` or `churchWindowFrame` row.
  Any hit on another chapel asset = FAIL.
- Three raised rows: y in-spec (beams 3.8..4.2; window 2.15±0.25), noCollide
  true, rotY per spec. The fallen ground beam KEEPS its collider (no
  noCollide, no y). Candelabra: explicit y, no noCollide. Probe flags
  mismatch.
- Probe prints per-raised-row line `raised: <asset> y=<y> noCollide=<bool>`.

## V4-R4 LIGHT socket

Spec: exactly ONE new lightSockets key = `candelabra`, with a comment noting
the warm-family grammar (banditCampfire + lanternWaymarker + candelabra, all
three ≤ 25 m apart, single-accent rule). Procedure:
- `grep -n "candelabra" prototype/js/CONFIG.js` → ≥ 3 hits: the prop row
  (altar seat), the lightSockets key, and possibly the comment. Exactly one
  NEW key inside lightSockets block (parse L98 block braces): count
  `heightFraction` lines before/after; delta must be exactly +1.
- Socket shape: `candelabra: { heightFraction: <0..1>, intensity: <num>,
  offset: [<num>, <num>] }` (PROPOSED values 0.55 / 5.5 / [0,0] — Nicko
  tunes; only shape is validated).
- `git -C /tmp/wh-worldfeat diff -- prototype/js/CONFIG.js | grep "^[+-]" | grep -i lightsocket`:
  only the added candelabra key (+ its comment) may appear — any touched
  lanternPost/banditCampfire/whCampkit/lanternWaymarker line = FAIL (churn).

## V5-R5 MANIFEST

7 new keys in prototype/js/assets.js, exact paths, nothing else. Procedure:
- `grep -n "church-kit" prototype/js/assets.js` → expect exactly these NEW
  lines (order irrelevant), each `key: 'art-direction/3d/assets/church-kit/<f>-pixelated.glb',`:
  churchWallWindow/church-wall-window, churchWindowFrame/church-window-frame,
  churchRoofBeam/church-roof-beam, churchAltar/church-altar,
  churchPulpit/church-pulpit, churchPew/church-pew, candelabra/candelabra.
- DO-NOT-TOUCH set present & unchanged (archway, buttress, pewBroken, rubble,
  ironFenceSection, ironFenceCorner, lanternPost→lantern-post-v3).
- `git diff -- prototype/js/assets.js | grep "^[+-]"`: exactly 7 `+` lines in
  the manifest, ZERO `-` lines (no renames/removals). Each added path must
  exist on disk: `ls art-direction/3d/assets/church-kit/<f>-pixelated.glb`
  for each (all 7 VERIFIED on disk 2026-11-07).

## V-WAKE34 AMENDMENTS (io, 2026-11-07 ~22:00Z — after first Devbot pass;
these supersede conflicting earlier lines)

A1 GROUND-VS-RAISED: probe/vaidation must NOT run R1/R2 ground checks on
rows carrying a y key or noCollide (raised rows: candelabra, gable
churchWindowFrame, both churchRoofBeam). Raised-vs-raised pairs are not
compared at all (R3's 1 m interior rule for altar/pulpit centres still
applies). The candelabra is compared ONLY against its altar (stack
exemption evidence) — never against unrelated rows.
A2 RAFTER CAMPFIRE: the campfire ≥ 2 m / waymarker ≥ 1.5 m rules bind GROUND
chapel rows (incl. the fallen rafter). Raised rows are exempt (socket pool
is ground-based; the beams host no light).
A3 KEEP-OUT SIZE: ellipse is rx 21 rz 12.5 at (0, −58) — spec amended; probe
ellipse check must pass the x −17.5 wall rows and the SW buttress. If the
landed row still says rx 17 rz 10, UPDATE the CONFIG row to rx 21 rz 12.5
and note it in the report.
A4 MANIFEST EVIDENCE (R5): the 7 rows landed in assets.js L107-116 (verified
io, exact paths byte-correct). The first-pass probe's R5 mis-parse (expected
`key: 'path',` but landed rows may carry trailing comments) is a PROBE bug:
fix the parser to accept optional trailing comments; evidence remains the
grep of each key + path in assets.js.
A5 DEBRIS-AMONG-FURNITURE (R2(d)): NEW pieces vs LOCKED treeStump rows
(13.4,−58.7) and (13.0,−55.5) may overlap circles (scene-01 anchor law;
spec amended with explicit exemption). All other NEW-vs-existing pairs keep
the 0.8 m floor.
A6 SEAT FIXES REQUIRED (nudge + inline `// CC-B1 seat nudge: reason`):
  - churchPew (5.5,−62) vs LOCKED churchArchway (8,−58) edge gap 0.72 < 0.8
    → move pew to (5.0,−62.5) or another seat restoring ≥ 0.8.
  - west wall windows vs gather nodes graveMoss/bonePile (2.95/3.00/0.25)
    → shift windows EAST to x −16.5 (or re-space z) so every node gap ≥ 3.
  - fallen rafter (−9,−55) vs bandit campfire gap 0.37 < 2 and vs bandit
    enemy spawn < 4 → move rafter to ≈ (−11,−56.5) (still west nave, clear
    of campfire 2 m, nodes 3 m, reachTreeC edge 0.8 m via A5-exempt stumps
    only).
  - rubblePile (−7,−63) fell 0.64 < 0.8 vs fallenLog → nudge to (−7.5,−62.5)
    or similar.
  - churchCornerButtress (−13.5,−54.5) vs reachTreeC (−10.9,−55.8) edge
    0.17 < 0.8 → BUT reachTreeC (L395) is auto-scatter seeded flora that
    predates CC-B1 INSIDE the future keepOut: shift the buttress WEST/SOUTH
    (≈ (−15,−53.5)) to restore ≥ 0.8; keepOut rx 21 still covers it.
A7 RE-RUN + COMPLETE THE ROUND: after fixes, `node scratch/cc-b1_probe.cjs`
must exit 0 (fail only on parser artifacts, if any, disclosed inline), then
`python3 tools/build_v8.py`, then write io/specs/cc-b1-chapel-buildsummary.md
(seats as landed, every nudge + reason, probe output, build bytes + stamp
line, tri ledger 13,997, deviations).

## V6-R6 SCATTER keep-out (original lines follow; A3 supersedes sizes)

Spec: one ellipse appended to CONFIG.scatter.keepOut (block at ~L2558):
`{ regionId: 'darkwood_edge', x: 0, z: -58, rx: 17, rz: 10 }`; every
wall/window/gable/altar/pulpit/pew seat inside it. Procedure:
- Probe ellipse test on those rows: ((x−0)/rx)² + ((z+58)/rz)² ≤ 1; prints
  per-row `in-ellipse: yes/no`. Roof beams exempt (raised / ground debris).
- `grep -n "darkwood_edge" prototype/js/CONFIG.js` → keepOut row present
  inside scatter.keepOut (NOT the regionB id line at L369); evidence line
  quoted in verdict. RegionB pre-existing keepOut (hold_outskirts L2560)
  untouched; `git diff` shows only one added keepOut line.

## V7-R7 TRI LEDGER

Sum of face counts of every CONSUMED GLB at scale 1; target ≤ 30000; hard
fail > 60000; 30001-60000 = WARNING disclose. Consumed this round = the 7 new
GLBs. Procedure:
```
python3 - <<'EOF'
import trimesh
base='/tmp/wh-worldfeat/art-direction/3d/assets/church-kit/'
fs=['church-wall-window','church-window-frame','church-roof-beam','church-altar',
    'church-pulpit','church-pew','candelabra']
tot=0
for f in fs:
    m=trimesh.load(base+f+'-pixelated.glb', force='scene')
    g=m.to_geometry() if isinstance(m,trimesh.Scene) else m
    n=int(g.faces.shape[0]); tot+=n; print(f, n)
print('TOTAL', tot)
EOF
```
Baseline measured today (sum verified by running the block above):
2000+2000+2000+1999+2000+1999+1999 = 13997 faces → R7 PASS at target. FAIL LINE (print verbatim in verdict on breach):
`R7 FAIL: tri ledger <N> > 60000 (doc 61 sec budget) — landmark may not ship
at this cost; cut pieces or accept engine cost with a disclosed WARN ticket`.
If Devbot's seat scales up any piece, the LEDGER STILL USES SCALE-1 faces
(scale is an engine-side uniform; it does not change vertex count).
Cross-check: probe prints the same 7-per-asset table + TOTAL; numbers must
match the python run exactly (mismatch = probe stale or GLB swapped).

## V8-R8 JS SANITY + BUILD

- `node --check prototype/js/CONFIG.js && node --check prototype/js/assets.js`
  → exit 0 (CONFIG references window? node --check validates syntax only —
  safe). A parse error = immediate R8 FAIL, stop.
- `cd /tmp/wh-worldfeat && python3 tools/build_v8.py` → prints
  `wrote builds/v8-playable.html <bytes>`. Baseline: builds/ ABSENT at HEAD
  c78e4e7, so the file's EXISTENCE + non-zero bytes = output changed.
  Record bytes + sha256 in the verdict.
- Stamp: title carries HEAD sha c78e4e7 (NO-GIT → sha unchanged; fail only if the
  build errors or the html is missing/empty).
- Grep the BUILT html — each must hit (counts are minimums):
  - `grep -c "churchWallWindow" builds/v8-playable.html` ≥ 2 (manifest+rows)
  - same ≥ 2 for churchWindowFrame, churchRoofBeam, churchAltar, churchPulpit,
    churchPew
  - `grep -c "candelabra" builds/v8-playable.html` ≥ 3 (manifest+row+socket)
  - `grep -c "darkwood_edge" builds/v8-playable.html` ≥ 2 (region id + keepOut)
  - `grep -c "regionId: 'darkwood_edge', x: 0, z: -58" builds/v8-playable.html`
    ≥ 1 (the keepOut row landed verbatim)
  - `grep -c "candelabra: {" builds/v8-playable.html` ≥ 1 (lightSockets entry)
  Any miss → name the missing key in the verdict; do not re-run build to paper
  over it (build failure is a Devbot defect, not a test artifact).

## V9-R9 FILE CHURN

`cd /tmp/wh-worldfeat && git status --porcelain` → allowlist ONLY:
- `M prototype/js/CONFIG.js`
- `M prototype/js/assets.js`
- `?? scratch/cc-b1_probe.cjs`
- `?? io/specs/cc-b1-chapel-spec.md` (spec file, pre-existing untracked)
- `?? io/specs/cc-b1-chapel-valspec.md`
- `?? io/reports/cc-b1-chapel-buildsummary.md`
- `?? io/reports/cc-b1-chapel-verdict.md`
Any other path (engine js, tools/, docs/, art-direction/, builds/ is
git-ignored — if it shows, it is a tracked-build anomaly, report it) =
R9 FAIL: quote `git status --porcelain | grep -v -E "CONFIG.js|assets.js|
cc-b1_probe|specs/.*cc-b1|reports/.*cc-b1"` output verbatim as the violation
evidence. Engine-behaviour smuggles: also run
`git diff --stat` — touched files must be exactly CONFIG.js + assets.js.

## Verdict contract (io/reports/cc-b1-chapel-verdict.md)

- Header: date, HEAD, spec+valspec paths, probe output block (verbatim).
- One section per rule R1-R9: verdict line `R<n>: PASS` / `R<n>: FAIL — <why>`
  + the evidence lines named above (seat table, gap pairs, grep counts,
  ledger TOTAL, keepOut row, status output).
- Final line exactly: `VERDICT: PASS` or `VERDICT: FAIL (R# R# …)`.
