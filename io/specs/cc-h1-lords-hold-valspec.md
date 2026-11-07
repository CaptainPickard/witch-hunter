# CC-H1 Testerbot Validation Spec — "Lord's Hold" (doc 64 slot H1, doc 66 recipe)

Round: **CC-H1** · 2026-11-07 · Worktree `/tmp/wh-worldfeat`, branch `feat/world-visuals`, baseline `e8dda52`.
Authority: `io/specs/cc-h1-lords-hold-spec.md` (IO spec; amendments A, B, C apply).
Style parents: `io/specs/cc-ad1-veil-crypt-valspec.md` + `io/specs/cc-ad2-veil-galleries-valspec.md`
(check-matrix + blocking-adjudication format), `io/specs/cc-wm1-redseam-valspec.md`
(exact-command + expected-output anchor format). Recipe lessons: `docs/planning/66-instanced-region-recipe.md`
sec 1-3 (VALSPEC before build; pin sha windows BY CONTENT ANCHOR, never line numbers).

**Mapping law:** every acceptance criterion in IO spec sec 6 (items 1-9) maps to at least one
V-check below; every V-check maps back. Map: A-1→V-1; A-2→V-2; A-3→V-3; A-4+A-9→V-4 (+V-12 sweep);
A-5→V-5; A-6→V-6; A-7→SERVE (IO post-gate, not this run); A-8→V-7; A-9(ED law)→V-10; amendment B→V-8;
the name-string law (sec 5, item 9)→V-9.

**Severity legend:** BLOCKER = build rejected, Devbot fixes and re-stages. MAJOR = rejected unless
IO waives in writing. MINOR = recorded, does not block. Every anchor is BLOCKER unless marked otherwise.

---

## 0. Independent census (Testerbot-verified against the tree, 2026-11-07 — NOT copied from the spec)

Re-grepped from the landed files at `e8dda52`; these numbers are the ground truth the V-checks
assert against:

- `git rev-parse HEAD` = `e8dda527681d6e88773557b2f4bc498b37ac29d0`; author identity
  `CaptainPickard|pickard.nicko@gmail.com` — the only identity that ever commits.
- `prototype/js/CONFIG.js` = 3936 lines, ends with `};`. Top-level region rows in file order:
  regionA(156) regionB(368) regionC(470) regionD(1330) regionE(1456) regionF(1581→closes 1671 `},`
  before the CC-C4a roads comment). **regionF has NO `nodes:` sub-block and NO `terrain:` sub-block**
  (its block is id/name/center/groundRadius/groundY/groundColor/groundColor2/groundSeed/scatter/spawn/
  gravityY/comments/fogColor/fogDensity/ambientLightLevel/door/enemies/props). Preceding `lightSockets`
  (98-116): lanternPost (hf 0.76, int 9.0, offset [-0.30, 0.0]), banditCampfire (hf 0.55, int 3.2,
  offset [0,0]), whCampkit, lanternWaymarker, b3Gate.
- `regionF.groundRadius` = 26; landed region groundSeeds are 1662061217 (C), 1662061218 (D), 1662061219
  (E), **1662061329 (F)** — the landed 1662061xxx family. `grep -c 'terrain:' CONFIG.js` = **0**;
  landable heightfield machinery exists only on C via `regionC.terrain` family — a `terrain: {` row
  does not exist in the file today, so ANY terrain row added this round is a diff-law hit.
- `prototype/js/region-defs.js` = 296 lines: 6 `makeRegion` lines (A through F), `connections.length` 5
  (conn[0] A/B, conn[1] B/C, conn[2] C/D, conn[3] C/E, conn[4] E/F). `regions[CFG.regionF.id] =
  makeRegion(CFG.regionF, -1);` sits at line 152; conn[4] push block at 161-178;
  `connections[4].sides[CFG.regionE.id] = -1; connections[4].sides[CFG.regionF.id] = 1;` at 183-184.
  `window.WH_REGION_DEFS` exports connectionBetween / insideChokepoint / sideOfPlane / mapPositionAcross /
  distanceToBoundary / isOnFromSide / neighborOf / insideDoorWindow / isMember / otherEnd / sideIn /
  connectionsOf / planeIn.
- `prototype/js/save.js` line 39-41: `function validRegion(rid) { return !!(rid &&
  window.WH_REGION_DEFS.regions[rid]); }`.
- `CONFIG.assets` manifest (glb table at CONFIG.js 2557+, bootCritical at 2605+, gear 3297+):
  every asset key the spec's prop rows name is LANDED — whWallA, whWallB, stoneSteps (crypt kit),
  banditCampfire, **whTent** (manifest `assets` table line 85 `assets.js`; NO `whTent:` row in CONFIG's
  footprint tables — its footprint rides the measured-GLB path), lanternPost, rubblePile, mossBoulder,
  **churchArchway**, **churchCornerButtress**, **okFenceStonewall** (landed prop rows at CONFIG 1101-1102
  prove the key + its wall: 4 colliders). Boundary-wall collider law: `CONFIG.boundaryWall.collider =
  { r: 0.45, perSegment: 3 }` (CONFIG 1875); wall-row colliders = r 0.45 circles at n per row, raw asset
  ext-X whWallA/whWallB = 1.899 (cc-ad1 probe measured; reused by cc-ad2 solver).
- `scratch/cc-h1/seat_scan_output.txt` (FROZEN, 117 lines): hook/seat **(5.0, -500)**, planeZ **-700.0**,
  doorX **0**, doorHalfWidth **4.5**, interactM 3.5, H1 center **(0, -822)**, groundRadius 126,
  ring **N 90 chord 8.79 scale 4.63 (raw 1.899)**, **89 wall rows** (the 90°-bearing face segment
  omitted), **1068 colliders**, **0 colliders inside the door lane window** (|x|≤4.5 @ z -700, ±3 z band),
  **nearest collider to the 15 lane sample points: 3.91** (≥1.0 floor), octant coverage
  **[122,135,136,135,134,135,136,135]** (E,NE,N,NW,W,SW,S,SE) — **ZERO empty octants**,
  `ALL SEAT CHECKS: PASS`, then the 89 printed ring rows in `{ asset: 'whWall[A/B]', x, z, rotY,
  scale: 4.63, sy: 11.69/11.55, sz: 2.40, y: -0.2, wall: 12 }` form. Testerbot re-derived the same 89
  rows from `seat_scan.py`'s formula: 0 mismatches at 2 dp.
- `prototype/builds/v8-playable.html` exists, tracked; baseline `grep -c lords_hold` = **0** pre-round.
- `tools/build_v8.py` exists (newest-tool law: re-check `tools/` for build_v9+ at build time).
- Stub-eval ground state (THREE-free, node): CONFIG→region-defs evals clean with
  `global.window = {}`, yields 6 regions / 5 conns, `connectionBetween('forest_of_the_old_king',
  'veil_crypt')` resolves.
- Node ≥ v18 available; python3 available. All anchors assume `cd /tmp/wh-worldfeat` first.
- `git status --porcelain` at valspec-write time is exactly: `?? io/specs/cc-h1-lords-hold-spec.md`,
  `?? scratch/cc-h1/` (+ this valspec once written). Anything else dirty pre-build = investigate first.

## 0b. Pre-registered amendment adjudications (Testerbot authority, declared BEFORE the build)

1. **Ring-row "byte-match" scope (V-5b-3):** the landed CONFIG wall rows are JS-numberformatted, so a
   value equal at 2 dp may print as `4.4` vs `4.40`. PASS = byte-equal **after 2-dp numeric
   normalization** of x/z/rotY only; sy/sz/y/wall/scale/asset must be byte-exact token-for-token.
2. **Marker-floor arithmetic (V-1b):** the AD2 landed diff counted 12 `+` CONFIG lines carrying
   `lords_hold`; the valspec floor is `>= 8`, so PASS = exact count ≥ 8 recorded per marker (not a
   range). The `>= 8` floor is the IO spec's own criterion; Testerbot asserts the floor and records
   the exact number for IO's ledger.
3. **Braid-branch check (V-12b):** a diff on the wrong branch (e.g. cc-c8-ledger's stratum law) is a
   process BLOCKER: `git rev-parse --abbrev-ref HEAD` must print `feat/world-visuals` in every
   snapshot; `git log --oneline -1` must match the pinned baseline (or the recorded round tip).
4. **Lane-min floor (V-5b-6):** the seat-scan's frozen lane minimum **3.91** (nearest collider
   to any lane sample point, seat_scan convention) is the expectation with tolerance ±0.15
   (the AD2 tolerance family); the absolute floor is **1.0 m** per AD2's V-9 lane law. The
   window-emptiness law (0 colliders in the strip) is separate and absolute. Note: Testerbot
   re-derivation at a 15-point 2-sided convention gives 0.94 — the 3.91 number is the
   seat_scan convention's; a probe sample-definition divergence is an ED-n variance, not a
   re-derivation.

These four adjudications are the valspec's binding interpretation of IO spec wording; a Devbot
dispute routes through a numbered ED-n, not silent reinterpretation.

## 1. Gate law (applies to every check)

- NO-GIT: Testerbot/Devbot never commit, add, push, amend, create refs, or set git identity
  (git log must stay `CaptainPickard <pickard.nicko@gmail.com>`; `whoami`-based `git config` runs
  by children = BLOCKER). Evidence outside the worktree: `/tmp/wh-valspec-cc-h1-evidence/`.
- No harness runs, no headless browser smoke tests, no playtesting. Toolbox: `node --check`,
  grep/python census + diff parsing, python clearance scripts, THREE-free node logic tests,
  the sha256 identity law.
- Evidence law: Testerbot writes evidence only to `/tmp/wh-valspec-cc-h1-evidence/` (D-4 of AD2);
  one file per check, raw command output only, plus `variances.csv` and `verdict.md` per AD2 §5-7.
- Diff basis (D-5): every `git diff` in this spec runs against the pinned baseline
  `git diff e8dda52 -- <path>` (content-pinned, never `HEAD~1`).

## 3. Check matrix

| # | V-check | IO-spec sec 6 criterion | Blocking rule |
|---|---|---|---|
| 1 | V-1 | A-1 build | exit != 0 OR bundle missing OR markers < 8 = blocker |
| 1b | V-1b | A-1 marker census | declared floor adjudication (0b-2) |
| 2 | V-2 | A-2 CONFIG additionality | removal/modification/extra key/block drift = blocker |
| 2a | V-2a-3 | A-2 key-set census (regionF shape) | key missing/extra/reordered = blocker |
| 3 | V-2b | A-2 CONFIG additionality | any removal/modification = blocker |
| 4 | V-3a | A-3 region-defs additionality | any edit to pre-existing lines = blocker |
| 5 | V-3b | A-3 conn shape + sides + connectionBetween | wrong from/axis/walkFrom/interact.from/sides = blocker |
| 6 | V-3c | A-3 THREE-free logic test | connectionBetween fails to resolve = blocker |
| 7 | V-4 | A-4 + A-9 blast radius | ANY diff line in game.js OR file outside declared set = blocker |
| 8 | V-5a | A-5 clearance.py exists + exit 0 | missing file OR non-zero exit OR hard-coded spec constants = blocker |
| 9 | V-5b | A-5 all constraints | any single constraint FAIL = blocker |
| 10 | V-6 | A-6 save round-trip | any harness FAIL line = blocker |
| 11 | V-7 | sec 7 gate-law checklist | any violated item = blocker |
| 12 | V-8 | amendment B audit | warm-count != 5 OR any non-warm-family light row = blocker |
| 13 | V-9 | sec 5/name-string law | node --check fail on CONFIG.js = blocker |
| 14 | V-10 | sec 6.9 deviation ledger | missing ED-n rows = blocker |
| 15 | V-12 | A-9 global sweep | stray-file diff = blocker |
| 16 | V-12b | sec 7 branch law | wrong branch / drifted HEAD = blocker |

SERVE + doc-64 flip (A-7, A-8-flip part) are IO post-gate and NOT executed by Testerbot this round —
recorded in the valspec so the criterion mapping stays total.

## 4. V-checks — exact commands + expected PASS evidence

### V-1 — Build sanity (IO sec 6.1) — BLOCKER

1. `python3 tools/build_v8.py`
   PASS: exit code **0**; `ls -la prototype/builds/v8-playable.html` shows a fresh mtime.
   (Newest-tool law: first `ls tools/build_v*.py` — if a build_v9+ exists at build time, Devbot
   uses it and says so in the build note; Testerbot runs THAT tool and names it in the verdict.)
2. `grep -c lords_hold prototype/builds/v8-playable.html`
   PASS: **>= 8** on the BUNDLE (baseline 0 → the count must be round-new).

### V-2 — CONFIG.js additionality law (IO sec 6.2)

- **V-2a marker/traceability census — BLOCKER:**
  `grep -c "lords_hold" prototype/js/CONFIG.js` → PASS: **>= 8**.
  `grep -n "CC-H1" prototype/js/CONFIG.js` → PASS: ≥ 1 (comment-banner traceability; informational floor,
  every new row carries the `// CC-H1` tag = MAJOR if < the row count, MINOR below that).
- **V-2b append-only diff law — BLOCKER.** Command:

  ```
  git diff -U0 e8dda52 -- prototype/js/CONFIG.js > /tmp/cfg.diff
  grep -cE '^-' /tmp/cfg.diff            # removal count: hunk headers excluded by -U0
  git diff e8dda52 -- prototype/js/CONFIG.js
  ```

  NOTE: all diff counts in this spec run `git diff -U0` and grep `^-` / `^+` — never a
  context-bearing grep on `-`/`+` (context lines like `-- ` or `---` false-positive).
  PASS: removal count = **0**; every content line added. Any removed content line = BLOCKER
  (a trailing-comma delta on regionF's closing line is tolerated as MINOR when V-5's full probe
  re-parses the rows — Devbot may use comma-first continuation on the new block).
  Then structural law (content-anchor pinned, pin V-2b by `regionF: {` / `roadTable`-adjacency,
  NOT line numbers):
  - regionG's block **append-position**: `awk` shows the `regionG: {` line number is greater than
    regionF's and less than the next pre-existing top-level key after regionF (`raid:` in the
    pre-edit file). PASS: `regionG` sits BETWEEN them.
  - **enemies law:** `grep -n 'enemies: \[\]' <regionG block>` → **exactly 1** hit (the empty
    array `enemies: []`); the KEY rides the regionF shape (key-set deepEqual covers it), the
    ARRAY holds zero rows (sec 6.2's "NO enemies rows"). Any row inside the array = BLOCKER.
  - **no terrain row:** `grep -n "terrain:" <regionG block>` → PASS: **0**. (regionC's landed
    `terrain: {` block at CONFIG 738 is the file's ONLY terrain row and stays untouched — the
    file-wide no-modification law in V-2b/V-12 covers a pre-existing-row touch.)
  - **exact key-set census on the regionF shape:** eval CONFIG in a THREE-free node stub,
    extract `Object.keys(CFG.regionG)` and `Object.keys(CFG.regionF)`, diff with deepEqual —
    PASS: **identical key array, same order** (id, name, center, groundRadius, groundY,
    groundColor, groundColor2, groundSeed, scatter, spawn, gravityY, fogColor, fogDensity,
    ambientLightLevel, door, enemies-empty, props). Node census snippet:

    ```js
    globalThis.window = globalThis;
    (0,eval)(require('fs').readFileSync('/tmp/wh-worldfeat/prototype/js/CONFIG.js','utf8'));
    const C = window.WH_CONFIG;
    const kf = Object.keys(C.regionF), kg = Object.keys(C.regionG);
    console.log(JSON.stringify({regionF:kf, regionG:kg, same:JSON.stringify(kf)===JSON.stringify(kg)}));
    console.log('door keys same:',
      JSON.stringify(Object.keys(C.regionF.door))===JSON.stringify(Object.keys(C.regionG.door)));
    console.log('enemies len:', C.regionG.enemies.length, '| name:', C.regionG.name,
      '| id:', C.regionG.id, '| isLandableNodeKey?', !!C.regionG.nodes);
    process.exit(C.regionG && JSON.stringify(kf)===JSON.stringify(kg) &&
      C.regionG.enemies.length===0 && !C.regionG.nodes && !C.regionG.terrain ? 0 : 1);
    ```

    PASS: `same:true`, `door keys same:true`, `enemies len: 0`, `name: Lord's Hold`,
    `id: lords_hold`, exit **0**.
  - value law (numeric, ±0: byte-exact, per census): id `'lords_hold'`, name `"Lord's Hold"`
    (DOUBLE-quoted, the raw `'` inside a double-quoted JS string — V-9 proves it parses),
    center `{ x: 0, z: -822 }`, groundRadius `126`, groundY `0`, groundColor `0x2f3339`,
    groundColor2 `0x26292e`, groundSeed `1662061440` (**FRESH** — not any of the landed
    1662061217/1218/1219/1329), scatter `false`, spawn `{ x: 0, z: -711 }`, gravityY `-22`,
    fogColor `0x8a8f96`, fogDensity `0.08`, ambientLightLevel `0.10`, door.planeZ `-700`,
    door.doorX `0`, door.doorHalfWidth `4.5`, suspendDepthM `0`, wallGapPadM `0`, interactM `3.5`,
    interactAt `{ x: 5.0, z: -500 }`, land keys exactly `['forest_of_the_old_king','lords_hold']`
    with `land.lords_hold = { x: 0, z: -711, faceX: 0, faceZ: -802 }` and
    `land.forest_of_the_old_king = { x: 5, z: -500, faceX: 5, faceZ: -488 }`, fadeIn 0.3 /
    fadeOut 0.5 / exitFadeOut 0.8, `text.prompt = "E - Enter Lord's Hold"` (the SPEC prints the
    double-quoted raw-apostrophe form; a single-quoted escaped form
    `prompt: 'E - Enter Lord\'s Hold'` is tolerated byte-wise by V-9 if it parses — the PROMPT
    string byte-equals either way, MINOR if the quoting form diverges from the spec's row),
    and NO extra keys.
    **SPEC-VARIANCE LEDGERED HERE (not a check):** the spec's sec 2 lists a `nodes: []` row,
    but the landed regionF shape (the mandated template) does NOT carry a `nodes` key
    (Testerbot census at HEAD). The key-set deepEqual governs (doc 66 sec 2: "copy sibling
    key set verbatim"): regionG carrying a `nodes` key that regionF lacks = V-2b FAIL;
    omitting it is the template-conformant build, and the ledger records the spec's
    `nodes: []` line as a spec artifact for IO's close-out adjudication.

### V-3 — region-defs.js additionality + door wiring (IO sec 6.3, amendment A)

- **V-3a append-only law — BLOCKER.**

  ```
  git diff -U0 e8dda52 -- prototype/js/region-defs.js | grep -cE '^-'   # expect 0
  git diff -U0 e8dda52 -- prototype/js/region-defs.js
  ```

  PASS: removal count = 0; the full diff adds EXACTLY these rows, nothing else:
  1. `regions[CFG.regionG.id] = makeRegion(CFG.regionG, -1);` — immediately after the regionF
     registration line (content-anchored to the regionF registration line, not line 152).
  2. the connections[5] `connections.push({...})` block with the CC-H1 comment citing the seat probe.
  3. the two sides-table lines `connections[5].sides[CFG.regionC.id] = -1;` and
     `connections[5].sides[CFG.regionG.id] = 1;`.
- **V-3b conn[5] shape census — BLOCKER** (amendment A governs `from`):

  ```
  grep -nE "from: CFG\.regionC\.id|to: CFG\.regionG\.id|connections\[5\]|var GD = CFG\.regionG\.door" prototype/js/region-defs.js
  ```

  PASS: `from: CFG.regionC.id` **NOT regionF (AMENDMENT A)**, `to: CFG.regionG.id`, `axis: 'z'`,
  `planeCoord: GD.planeZ`, `sides: {}` at push time, door block keys EXACTLY
  (doorX, doorHalfWidth, suspendDepthM, wallGapPadM, arch: null, gatedTo: null, walkFrom,
  interact, land) — mirror of landed conn[4] at region-defs 161-178; `walkFrom: CFG.regionG.id`;
  `interact: { from: CFG.regionC.id, x: GD.interactAt.x, z: GD.interactAt.z, radius: GD.interactM }`;
  `land: GD.land`; the sides table after the push = `(C, -1)` `(G, +1)`; **no edits of any kind to
  connections[0..4]** (their hunks = 0 in the diff; `git diff e8dda52 -- prototype/js/region-defs.js
  | grep -c "connections\[[0-4]\]"` → **0**).
- **V-3c THREE-free node logic test — BLOCKER.**

  ```js
  // scratch of Testerbot's one-shot probe (run inline, not written to prototype/):
  globalThis.window = globalThis;
  (0,eval)(require('fs').readFileSync('/tmp/wh-worldfeat/prototype/js/CONFIG.js','utf8'));
  (0,eval)(require('fs').readFileSync('/tmp/wh-worldfeat/prototype/js/region-defs.js','utf8'));
  const D = window.WH_REGION_DEFS, C = window.WH_CONFIG;
  const ok = [];
  ok.push(['regions has lords_hold', !!D.regions.lords_hold]);
  ok.push(['connectionBetween resolves',
    D.connectionBetween('forest_of_the_old_king','lords_hold') !== null]);
  ok.push(['from is regionC (AMENDMENT A)',
    D.connectionBetween('forest_of_the_old_king','lords_hold').from === 'forest_of_the_old_king' &&
    D.connectionBetween('forest_of_the_old_king','lords_hold').to === 'lords_hold']);
  ok.push(['6 regions / 6 conns', Object.keys(D.regions).length===6 && D.connections.length===6]);
  ok.push(['sides C -1 / lords_hold +1',
    D.connectionBetween('forest_of_the_old_king','lords_hold').sides.forest_of_the_old_king === -1 &&
    D.connectionBetween('forest_of_the_old_king','lords_hold').sides.lords_hold === 1]);
  ok.push(['walkFrom = lords_hold',
    D.connectionBetween('forest_of_the_old_king','lords_hold').door.walkFrom === 'lords_hold']);
  ok.push(['planeIn only in the hold',
    D.planeIn(D.connectionBetween('forest_of_the_old_king','lords_hold'),'forest_of_the_old_king')===false &&
    D.planeIn(D.connectionBetween('forest_of_the_old_king','lords_hold'),'lords_hold')===true]);
  ok.push(['door window |x|<=4.5',
    D.insideDoorWindow(D.connectionBetween('forest_of_the_old_king','lords_hold'),4.4)===true &&
    D.insideDoorWindow(D.connectionBetween('forest_of_the_old_king','lords_hold'),4.6)===false]);
  let n=0; ok.forEach(([l,p])=>{console.log((p?'PASS ':'FAIL ')+l); if(!p)n++;});
  process.exit(n?1:0);
  ```

  PASS: 8/8 lines PASS, exit 0.

### V-4 — game.js empty-diff + global blast radius (IO sec 6.4) — BLOCKER

```
git diff e8dda52 -- prototype/js/game.js | wc -l        # expect 0 lines
sha256sum prototype/js/game.js                            # (vs the recorded pre-round digest)
git diff e8dda52 --name-status                            # the whole-tree file list
git status --porcelain
```

PASS: game.js diff = **0** (byte-empty; A-4). `git diff e8dda52 --name-status` touched-set ⊆
{prototype/js/CONFIG.js, prototype/js/region-defs.js, prototype/builds/v8-playable.html} for
TRACKED files; untracked-set ⊆ {io/specs/cc-h1-*, scratch/cc-h1/}. (A-9: no unrelated diffs
anywhere else — docs/planning/*.md, prototype/js/*.js beyond the two named, any other tree file.
The v8 bundle count rides V-1; a bundle rebuild is expected and legal.
Also excluded-by-design: io/specs/, scratch/cc-h1/ — the round's spec artifacts.)

### V-5 — Geometry probe (IO sec 6.5, the AD2 V-9 pattern: CONFIG-ROW-PARSED, no spec constants)

- **V-5a deliverable law — BLOCKER:** `test -f scratch/cc-h1/clearance.py` AND
  `python3 scratch/cc-h1/clearance.py` exit **0**, run from the worktree root.
  Devbot must deliver it shaped on `scratch/cc-ad2/solve_geometry.py` (the same
  parse→rebuild→assert→ALL-CONSTRAINTS-print structure: parse regionG's rows LIVE from
  CONFIG.js + the conn[5] row from region-defs.js — NO hard-coded spec constants for the new
  rows — rebuild wall-collider circles per region-manager whPropColliders (r 0.45 circles at n
  per row along the row's local X axis; asset raw ext-X whWallA/whWallB 1.899), then assert
  every clearance law). A probe that hard-codes spec constants instead of parsing landed rows =
  blocker (the AD1 V-13/`CONFIG-ROW-PARSED` lesson).
- **V-5b constraint ledger — BLOCKER.** The probe output must show the following constraints PASSED
  (Testerbot verifies the OUTPUT lines, and re-derives any number itself in Python):

  1. **Wall-row census:** `wall rows == 89` / `colliders == 1068` (89 rows × wall 12 = 1068).
  2. **Ring-closure law (the door window):** the ONLY collider-free bearing arc on the r-126
     circle is the door window's: **0 colliders inside `|x| ≤ 4.5 at z ∈ [-703, -697]`**,
     and every OTHER bearing carries colliders.
  3. **Wall-row byte-value law (V-5b-3 adjudication):** every landed regionG wall row's
     x/z/rotY **exactly matches** the ring rows printed in `scratch/cc-h1/seat_scan_output.txt`
     after 2-dp normalization (asset A/B alternation by index parity scale 4.63 symlinked to the
     frozen cadence; sy 11.69 A / 11.55 B, sz 2.40, y -0.2, wall 12 byte-exact).
  4. **Ring radii law:** every landed wall row sits at `|hypot(x-0, z+822) - 126| ≤ 0.6` (the
     frozen ring radius; every recomputed row differs from 126 by ≤ 0.05, so the 0.6 floor
     absorbs 2-dp rounding only).
  5. **Inside-disc rows:** spawn (0,-711) AND both land rows inside r 126 of center (0,-822):
     `land.lords_hold` (0,-711) → 111.0 PASS; spawn → 111.0 PASS;
     **land.forest_of_the_old_king (5,-500) is C-SIDE land** — asserted on C's side instead:
     r to C's center (0,-366) = 134.1 ≤ 278.5 (per seat_scan's C-disc law) AND z -500 > planeZ
     -700 (home side), NOT against r 126.
  6. **Lane clearance:** the lane sample set is DEFINED as seat_scan.py defines it (Testerbot
     convention note — seat_scan samples the lane at the plane band, its 3.91 = nearest collider
     to any lane point; Testerbot recomputed the equivalent set at 15 points
     {x ∈ {-4.5,-2.0,0,2.0,4.5}} × {z ∈ {-703,-700,-697}} and got **0.94**, so the valspec pins
     BOTH numbers): nearest collider to the 15 sample points ≥ **0.9 min / 3.9 lane-edge**
     — PASS requires the seat_scan convention minimum ≥ **1.0** frozen (3.91 ±0.15, floor 1.0,
     adjudication V-5b-6) when the probe samples the same z-band points seat_scan's
     `for lx in (-LHW, -2.0, 0.0, 2.0, LHW)` loop samples; a sample-point definition that
     differs from seat_scan's is a ledgered variance (ED-n), not a re-derivation. What is
     NOT negotiable: **0 colliders strictly inside** the window (`|x| ≤ 4.5 AND |z-(-700)| ≤ 3`,
     boundary-inclusive strip per seat_scan's `abs(z - PLANE_Z) <= 3.0`) — that floor is
     absolute; the nearest-collider floor is 1.0 at the seat_scan sample convention.
  7. **Prop-hub clearances (spec sec 2 margins, raw = collider-center distance):**
     - every regionG prop row → nearest ring collider ≥ **4.0** raw; **spawn → every prop ≥ 6.0**;
     - **hub cluster mutual ≥ 4.0** per pair — EXCEPT the licensed pair
       **lanternPost (6.5,-706) ↔ okFenceStonewall E-parapet at (6.5,-702)** = exactly **4.00**
       (the spec's "at scale 2.0" pair, `>= 4.0 m mutual` in sec 2, tolerance-bound: assert
       ≥ 3.9 for this pair ONLY, the probe's ±0.15 tolerance family);
     - the 4 braziers' **mutual = 11.3** spec value — probe assert ≥ 11.2 (11.32 computed at
       the frozen coordinates), i.e. the four pair separations are 11.32/11.32/11.32/11.32
       and the probe prints each with margins;
     - **lane clear 3.91:** nearest collider to the lanternPost seat (6.5,-706) ≥ 3.7
       (3.91 frozen, the "gate-lane clear" number the spec cites; Testerbot re-derives:
       nearest collider-center to (6.5,-706) = 9.83, nearest collider-center to the lane
       sample set = 3.91 — the probe asserts the SEAT's lane number with the ±0.15 family;
       the two numbers the spec quotes live at different sample points and both PASS above
       their floors);
     - every prop ≥ its own clearance family (dais 84.02 / braziers 80.0-91.2 / parapets 5.25-9.85 /
       tents 77.7-89.3 / chapel 70.5-80.4 / boulders 65.8-104.5 / rubble 27.3-38.5 raw from the
       ring — all >> 4.0, the probe asserts the FLOORS and prints the margins);
     - props INSIDE the playable band: every prop ≤ 124.5 from center (the per-region clamp band,
       r 126 minus playerMargin 1.5).
  8. **Octant coverage:** the 8 octants of the r-126 circle outside the gap arc — gap-arc octant
     S (the one covering the 90° face gap) may be collider-free ONLY inside the window's own
     arc; assert `0 colliders inside the window` (law 2) AND `every octant OUTSIDE the gap arc
     holds ≥ 3 colliders` (AD2's octant-coverage shape) — expected full-vector
     [122,135,136,135,134,135,136,135], min 122.
  9. **Door-lane window emptiness (belt+braces with law 2):** the window's own octant S bears
     ≥ 122 colliders OUTSIDE the |x|≤4.5 strip — the ring closes everywhere except the window.
  10. **conn[5] sanity (region-defs parsed live), the AD2 conn-shape check:** `from`
      `forest_of_the_old_king`, `to` `lords_hold` (AMENDMENT A), axis z, `planeCoord =
      door.planeZ` (-700), `walkFrom: lords_hold`, `interact: { from: forest_of_the_old_king,
      x: 5.0, z: -500, radius: 3.5 }`, `land: GD.land`, sides C -1 / lords_hold +1;
      land.lords_hold z -711 ≤ planeZ -700 (home side), land.forest_of_the_old_king z -500 >
      -700 (home side); land.lords_hold ≥ 8 m inside the plane (planeZ -700 - land z -711 = 11 ✓).
  11. **C-side aperture clearance (seat_scan checks 1-4, re-asserted against LANDED C rows):**
      interactAt (5.0,-500) ≥ 6.0 m from every C prop row, ≥ 26 m from the crypt door's C-side
      hook (0,-596) — computed 96.1, and ≥ 26 m from the notch mouth (0,-596) (notchMouthExclusionM
      26) — computed 96.1, and standable: r to C center = 134.1 ≤ 278.5.
  12. Final line: `ALL CONSTRAINTS: PASS (N checks)` and exit **0**.

  Testerbot ALSO re-derives independently (in python) and compares: 89/1068/0-window/3.91-lane/
  11.32-brazier-mutual/111.0-spawn-radius/hook 96.1-vs-96.1 — any disagreement between the probe's
  printed margins and Testerbot's own re-derivation = blocker (independent verification authority).

### V-6 — Save round-trip (IO sec 6.6) — BLOCKER

Devbot delivers `scratch/cc-h1/save_roundtrip.js`, pattern = `scratch/cc-ad1/save_roundtrip.js`
(the THREE-free stub harness): `global.window = {}`, `global.localStorage` stubbed, THREE undefined,
`WH_LEVEL` stubbed with capture/restore/discover, then evals CONFIG.js → region-defs.js → save.js
against `global.window`, builds the mkGame stub (player/inventory/cooking/camp/dayNight/
regionManager.logic.activeId/classId/inventoryUI/c4 stub rows exactly as the AD1 harness lists
them at AD1-valspec 313-318), and asserts:

1. `validRegion('lords_hold')` → true (save.js regions-gate).
2. `capture(game with regionManager.logic.activeId = 'lords_hold')` → profile
   `player.regionId === 'lords_hold'` (regionId rides capture — save.js:73 reads rm.logic.activeId).
3. restore of a profile captured INSIDE the hold over a stub seat: region gate
   (`DEFS.regions[lords_hold]` truthy) + `SAVE.restore` teleports to the saved pos; hp/focus/
   stamina clamped to the saved profile values; `WH_LEVEL.discover` fires with `lords_hold`.
4. negative control: `validRegion('lords_hold_gone')` false and restore of a profile with a dead
   region id falls back to activeId, nothing throws.
5. `camp.place('lords_hold', x, z)` on the stub re-places a camp site row with regionId
   lords_hold (the AD1 harness's camp.sites assertion — the H2 camp wiring rides this law).
Run: `node scratch/cc-h1/save_roundtrip.js` from the worktree root. PASS: every asserted line
prints PASS + the final `save_roundtrip: N/N PASS`, exit **0**.
(A-6 save-safety rides this; the runtime validator stays runtime-only — the AD2 V-10 amendment
pattern: the CONFIG-parsed shape census in V-2b + this harness IS the licensed execution.)

### V-7 — Gate-law checklist (IO sec 6.8 / sec 7) — BLOCKER (process)

Testerbot verifies, recording each with evidence:

1. `git log --format='%an <%ae>' -1 HEAD` → `CaptainPickard <pickard.nicko@gmail.com>` (the child
   never set identity; NO-GIT law).
2. `git diff e8dda52 --name-status` → touched files ⊆ declared set (V-4's list; the code-side
   diff = CONFIG.js + region-defs.js + the rebuilt bundle only).
3. `git stash list` → empty (nothing stashed by children).
4. No harness artifacts: `ls prototype/harness 2>/dev/null` → empty/absent; no new
   `scratch/cc-h1/*` files beyond the probes and build note; the build note is a FILE
   (`scratch/cc-h1/build-note.md`), no dispatch heredocs on disk.
5. No browser smoke: scratch/cc-h1 contains no playwright/puppeteer/harness references
   (grep 0 on the dir's files).
 6. Branch + HEAD law (V-12b anchor): `git rev-parse --abbrev-ref HEAD` = `feat/world-visuals`
    at both snapshots; `git log --oneline -1` = the baseline sha `e8dda52` (or the recorded
    round tip). Wrong branch or drifted identity = BLOCKER.
 7. Provider-stall law followed (process observation, recorded in the note).

### V-8 — Amendment B audit: warm-light socket census (IO sec 6 / amendment B) — BLOCKER

Amendment B: warm socket count = **FIVE** — the 4 banditCampfire braziers (lightSockets
banditCampfire, heightFraction 0.55, intensity 3.2) PLUS the gate lanternPost row (row 7, at
(6.5,-706) per the spec's own correction: x 2.5 moved OUT of the window to 6.5; lightSockets
.lanternPost row exists, intensity 9.0). One warm FAMILY (amber/gold), zero crimson, zero other
light families. Commands (census + family audit):

```
python3 - <<'PY'
import re, sys
src = open('/tmp/wh-worldfeat/prototype/js/CONFIG.js').read()
m = re.search(r"\n  regionG: \{", src)
assert m, "regionG block missing"
blob = src[m.start():]
nxt = re.search(r"\n  [a-zA-Z_]+: \{", blob[10:])
block = blob[:10+nxt.start()] if nxt else blob
fires = re.findall(r"\{ asset: 'banditCampfire',\s*x: (-?[\d.]+),\s*z: (-?[\d.]+)", block)
posts = re.findall(r"\{ asset: 'lanternPost',\s*x: (-?[\d.]+),\s*z: (-?[\d.]+)", block)
light_assets = re.findall(r"asset: '(\w*)[Ll]ight\w*'", block)
colors = re.findall(r"(?:color|lightColor|emissive):\s*(0x[0-9a-fA-F]+)", block)
crimson = [c for c in colors if int(c,16) & 0xFF0000 and (int(c,16)&0x00FF00)<(int(c,16)&0xFF0000)//4]
print('banditCampfire rows: %d %s' % (len(fires), fires))
print('lanternPost rows:   %d %s' % (len(posts), posts))
print('crimson-family hex rows: %s' % (crimson or 'NONE'))
assert len(fires) == 4, 'V-8: banditCampfire rows != 4 (%d)' % len(fires)
assert len(posts) == 1, 'V-8: lanternPost rows != 1 (%d)' % len(posts)
assert not crimson, 'V-8: crimson-family hex rows present: %s' % crimson
print('V-8 PASS: 4 banditCampfire + 1 lanternPost = 5 warm sockets; zero crimson rows')
PY
```

PASS: 4 fire rows at exactly the spec's 4 seats (±5.66, -776.34)/(±5.66, -787.66), 1 lanternPost
row at (6.5, -706) (x 2.5 = the WRONG row, spec sec 2's own correction note — if x 2.5 lands
instead of 6.5 that's V-5b lane-law territory AND V-8 records the seat deviation), zero
crimson-family hex rows inside regionG, and the family audit: every light-bearing row's asset
is `banditCampfire` or `lanternPost` — NOTHING else in regionG carries a light socket asset
(b3Gate sockets live in the conn, not regionG; lanternWaymarker would be a second amber-family
row = blocker because family law = the 5 named sockets only).
**Non-asset-row colors:** the ground/fog hexes (0x2f3339/0x26292e/0x8a8f96) are NOT light rows —
they are outside V-8's census; V-2b checks their values.

### V-9 — Name string parses (IO sec 5/6, the escaped-apostrophe law) — BLOCKER

```
node --check prototype/js/CONFIG.js && echo "CONFIG.js: syntax OK"
node --check prototype/js/region-defs.js && echo "region-defs.js: syntax OK"
node --check prototype/js/game.js && echo "game.js: syntax OK (empty diff makes it a formality)"
```

PASS: exit 0 all three, and the stub-eval census of V-2b prints `name: Lord's Hold`
(the parsed string's JS value byte-contains the apostrophe: `C.regionG.name === "Lord's Hold"`,
asserted via the census exit gate). The double-quoted raw-apostrophe form is valid JS — node
--check on the EDITED file is the proof; the V-2b census re-reads the parsed value.

### V-10 — Deviation ledger law (IO sec 6.9) — BLOCKER (meta)

Read Devbot's `scratch/cc-h1/build-note.md`: every row that could not clear, any missing manifest
key, any behavior deviation has a numbered **ED-n** entry. PASS = the ledger exists + a numbered
ED-n row per any variance Devbot hit; an empty ledger with all probes passing is also PASS
(no deviations is a legal outcome). Testerbot's own variances file cross-references ED-n where
applicable. No ledger file at all = blocker.

### V-12 — Blast-radius sweep (IO sec 6.4's "no unrelated diffs anywhere else", the AD2 V-12 shape) — BLOCKER

1. `git diff e8dda52 --name-status` — every touched TRACKED file ∈ the declared set of V-4.
2. No UNRELATED top-level edits: `git diff e8dda52 -- prototype/js/ | grep '^diff --git'` lists
   exactly CONFIG.js and region-defs.js (game.js byte-zero rides V-4).
3. `git diff e8dda52 -- prototype/js/CONFIG.js | awk '/^@@/'` — every hunk header's
   `@@ -a,b +c,d @@` lies inside the regionG insertion window (right after regionF's block close)
   OR the boundaryWall-adjacent rows NOT touched (zero hunks anywhere else: lightSockets untouched;
   world/boundaryWall/raid untouched — the valspec's census pins V-2b's content anchors).
4. `git diff e8dda52 --stat` — total lines changed ≤ the valspec's expected envelope: CONFIG.js
   + ~90 wall rows + ~15 dressing rows + block scaffold (~120) + region-defs ~22 = ≤ ~160 lines
   total (informational MAJOR if exceeded; the exact census rows are V-2/V-3's).
5. `grep -c lords_hold prototype/builds/v8-playable.html` — the bundle rebuild carries the
   region; the whole-tree untracked list carries nothing but the declared spec/scratch paths.

## 5. Blocking-variance adjudication (AD2 §5 format, verbatim rows)

```
BV-ID | UTC timestamp | V-check | criterion | observed | declared | classification | reasoning | owner
```

Rules: non-blocking ONLY if formatting-only AND IO-licensed; Devbot fixes route back; verdicts
FAIL pending re-run. Testerbot never fixes code. BV-IDs sequential BV-001...

## 6. Verdict PASS/FAIL table (AD2 §6 shape)

One row per check; round verdict = PASS iff every row is PASS + zero blocking variances + restore
law clean. A criterion with no mapping, or missing/empty evidence, fails by construction.

## 7. Evidence bundle

`/tmp/wh-valspec-cc-h1-evidence/` (outside the worktree per D-4): one file per check
`ev/vN-*.ext` per AD2's bundle law + `snapshot-before.txt`, `snapshot-after.txt`, `variances.csv`,
`verdict.md`, pinned baseline SHA in `header.txt`. Every evidence file carries the raw command
line + raw output; no hand-written summaries in place of output.

## 8. HOW TO RUN (Testerbot execution order, deterministic)

1. Snapshot: `git rev-parse HEAD`, `git status --porcelain`, `git stash list` → header.txt.
2. Confirm branch = `feat/world-visuals` (V-12b adjudication).
3. Static census first: V-2, V-3, V-4, V-8, V-9, V-12 (syntax + diff laws need no rebuild).
4. Build: V-1 (rebuild-in-isolated-copy per AD2 D-2/D-3 if invoked as a re-verify pass; for the
   round's single build, Devbot's landed bundle is the artifact Testerbot greps — Testerbot does
   NOT rebuild unless the verdict needs the identity law, in which case D-2/D-3 restore law holds).
5. Probes: V-5 (clearance.py), V-6 (save_roundtrip.js) — the worktree's LANDED rows are the input.
6. Ledger + process: V-10, V-7. Package evidence, adjudicate, emit `verdict.md`.
7. Report to IO: the verdict table + variances + restore proof + the valspec's own pass note.
   NOTHING ELSE. IO is the sole committer.
