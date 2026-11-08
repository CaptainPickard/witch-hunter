# CC-WM1 'Redseam' Testerbot Validation Verdict

Testerbot, 2026-11-06. Repo `/tmp/wh-worldfeat` (worktree, branch `feat/world-visuals`).
Validated the landed candidate change in `prototype/js/CONFIG.js` against
`io/specs/cc-wm1-redseam-spec.md` (amended in place, WM1-A1..A4) and
`io/specs/cc-wm1-redseam-valspec.md`. NO-GIT honored (read-only: status/diff/show
only, zero mutations, zero builds that write tracked files, zero harness runs).

- **FINAL VERDICT: PASS**
- Blocking code findings: **0**
- Non-blocking findings: **4** (1 required valspec amendment; 3 MINOR notes)

---

## 1. Per-criterion verdict table

Severity context: valspec says every anchor is BLOCKER unless stated otherwise.
For the two anchors carrying stale truth values (D-1, E-4), the instruction that
the AMENDED spec is authoritative is applied: the code is judged against the
amended spec, and the valspec line is reported as a required amendment.

| Anchor | Verdict | Evidence (one line) |
|---|---|---|
| **F** git-status law | **PASS** | `git status --porcelain`: only `.js` dirty = `prototype/js/CONFIG.js` (untracked spec/scratch docs don't match `\.js$`). |
| **I-1** nodeTypes append-only | **PASS** | Removed pre-existing nodeType rows in diff = **0**; `+ ,ironVein:` added below bonePile. |
| **I-2** items append-only | **PASS** | Removed ingredient lines = **0**; added = **1** (`ironOre:`). |
| **I-3** nodes append-only | **PASS** | Removed `\{ type: 'bonePile'` = **0**; added bonePile = **0**; added `\{ type: 'ironVein'` = **8**. |
| **I-4** props append-only | **PASS** | Removed `\{ asset:` = **0**; added = **14**. |
| **I-5** enemies append-only | **PASS** | Removed enemy rows = **0**; added wolf/coven = **0**; added (comma-first) bandit = **3**. |
| **I-6** file-wide zero deletions | **PASS** | `git diff --stat`: `1 file changed, 41 insertions(+)` — zero `-` content lines file-wide (the only leading-`-` text is the `--- a/...` diff header). |
| **A-1** ironVein row exists, 9 code hits | **PASS** | Code (non-comment-only) ironVein lines = **9**: 8 contiguous seat rows at **lines 1234–1241** + nodeTypes key row at **line 3609** (inside nodeTypes block span 3597–3611). Line drift vs valspec's stale pre-edit numbers explained by the 18 lines appended above it. |
| **A-2** nodeTypes.ironVein fields | **PASS** | `name:'Iron Vein'`, `rarity:'common'`, `yield:{id:'ironOre',count:3}`, `respawnSec:240`, `glowColor:0x8f5a33`, `scale:1.15` — all six present, field-body contains no extras. |
| **A-3** glow decimal cross-check | **PASS** | `0x8f5a33` = **9394739** (documentation anchor, informational). |
| **A-4** nodeTypes census | **PASS** | 6 keys, sorted: `[herbBundle, deadwoodPile, mushroomCluster, graveMoss, bonePile, ironVein]`; ironVein appended after bonePile. |
| **B-1** ironOre hits ≥ 2 | **PASS** | Exactly **2**: items row (line 3153) + yield ref `id:'ironOre'` (line 3609). |
| **B-2** ironOre fields | **PASS** | Has `id:'ironOre'`, `name:'Iron Ore'`, `glyph:'IO'`, `category:'ingredient'`; absent: weight/stackCap/flavor/useHint. |
| **B-3** ingredient census = 6 | **PASS** | Sorted: `[boneShard, deadwood, forestHerb, graveMoss, ironOre, wildMushroom]` (5 pre-existing + ironOre); ironOre sits after boneShard, before the C1 cooked-food block. |
| **C-1** 8 ironVein exact coords | **PASS** | Order-insensitive set-equality with census seats — all 8 exact: (53,-577) (55.5,-573.5) (61,-572) (64,-575.5) (63.5,-582) (57,-584) (51.5,-581.5) (50,-574). |
| **C-2** bonePile byte-sacred | **PASS** | 8 bonePile rows present and byte-identical to HEAD (`git show HEAD:` comparison: zero removed/retyped rows). |
| **C-3** nodes census | **PASS** | regionC.nodes = **16** real rows (8 bonePile + 8 ironVein), array dense, no holes. |
| **C-4** site clearance envelope | **PASS** | All 8 veins: min dist to any prop **3.04 m** (>1.5), to any bonePile **187.24 m** (>4), to any non-squatter enemy **78.72 m** (>12). Squatters exempted per CONTESTED-site law (IO repair 2026-11-06) — E-4 governs them. |
| **D-1** 14 prop rows exact | **PASS** (code) / **AMEND NEEDED** (valspec truth) | Landed file matches the **amended-spec W-4 final table** and the authoritative census exactly-once for all 14 rows, incl. rubble S **(57.5,-588)** and W **(51.5,-570)**. Verbatim replay of the valspec D-1 script fails exactly its 2 truth rows with the WM1-A3-era seats `'55','-584.5'` and `'52','-572.5'` (0 occurrences in the landed file) — superseded by **WM1-A4**; valspec lines ~392/394 (D-1 expected list rows 8/10) require amendment. The valspec's `props rows total: 45` is its own single-space shape census and holds verbatim (40+5 strict rows); the true row census is **237** (HEAD 223 + 14). |
| **D-2** insertion point | **PASS** | Anchor `rubblePile', x: 202, z: -440` unique (**line 1193**); the CC-WM1 banner + all 14 redseam asset rows sit contiguously after it, before the props-array close (line 1211) — appended at array tail per spec. |
| **D-3** no other prop touched | **PASS** | Diff: `-` asset rows = **0**; `+` asset rows = **14**. |
| **E-1** 3 squatters exact coords | **PASS** | Rows (comma-first, per line-644 style) at (56.5,-580.5) (61.5,-580) (59,-574.5); file-wide bandits 29 → **32**. |
| **E-2** regionC enemies census | **PASS** | **55 rows**: 28 wolf + 25 bandit + 2 coven (= ground truth). Pre-edit 52 (28/22/2) verified at HEAD. |
| **E-3** no pre-existing enemy touched | **PASS** | `-` enemy rows = 0; `+` wolf/coven = 0; `+` bandit = 3. |
| **E-4** interior spacing | **PASS** (code) / **AMEND NEEDED** (valspec seats) | All five bars hold on the landed seats (numbers in §3). Verbatim valspec E-4 fails only via its two stale rubble truth coordinates: vein (57,-584)→stale rubble (55,-584.5) = **2.06 m** and vein (50,-574)→stale rubble (52,-572.5) = **2.50 m** violate its ≥2.5 m vein-prop bar **at the stale seats** — evidence the WM1-A4 amendment (which moved both rubble rows away) is not yet in the valspec. |
| **G** build law | **PASS-by-replica** (see §5) | `tools/build_v8.py` NOT executed (would overwrite the tracked build artifact; Testerbot avoids overwriting tracked files). In-memory replica of build_v8.py's exact logic (§5): parse+succeed, would write 3,374,766 bytes with **30** `CC-WM1` markers (**≥ 26** amended floor). Tracked `v8-playable.html` still pre-round (0 markers): expected — the diff is uncommitted; the sanctioned build is IO's landing step. |
| **H** node one-shot runtime smoke | **PASS** | Verbatim run (scratch/cc-wm1/testerbot_smoke.js): exit **0**; 8 vein lines all `OK` (y=2.78–3.21, |y|≤26; d=213.9–225.3 ≤ 280 from (0,-366)); `nodeTypes.ironVein: OK`; `items.ironOre: OK`; final line `H PASS — 8 vein seats on-terrain, |y|<=26, d<=280 from (0,-366), ironVein+ironOre wired`. |

## 2. Cross-wiring checks (XW)

`yield.id → CONFIG.items` for all 6 nodeTypes: herbBundle→forestHerb (line 3111),
deadwoodPile→deadwood (3112), mushroomCluster→wildMushroom (3113), graveMoss→graveMoss
(3114), bonePile→boneShard (3115), **ironVein→ironOre (3153)** — all yield ids exist;
nodeTypes key `ironVein` == nodes-row type `ironVein` == the gather key. Runtime require
chain (H) resolves both objects. All consistent. (Beyond-valspec bonus checks
weight/stackCap/flavor/useHint absence also verified on ironOre.)

## 3. Independent WM1-A3/W-5/W-6 clearance recomputation (Testerbot math, fresh)

All recomputed from the landed file, not copied from any spec comment. Bars:
squatter↔vein ≥ 2.8; squatter↔prop ≥ 1.8; squatter↔squatter > 4.3; vein↔prop ≥ 2.5;
vein↔vein > 4.2; veins↔bones > 4; veins↔non-squatter enemies > 12.

| Quantity | Computed | Verdict |
|---|---|---|
| squatter↔vein min | **2.8284 m** — squatter 2 (61.5,-580) ↔ vein 5 (63.5,-582) | ≥ 2.8 ✓ (spec W-5 claims 2.83) |
| squatter↔squatter | S1–S2 **5.025**, S2–S3 **6.042**, S1–S3 **6.500** | spec band 4.3–6.5 ✓ (all three inside) |
| vein↔vein nearest-pair | **4.2426 m** — vein 1 (53,-577) ↔ vein 8 (50,-574) (next: 4.3002, 51.5,-581.5↔53,-577) | > 4.2 ✓ (spec claims ≥ 4.24) |
| vein↔prop min (all 237 regionC props) | **3.0414 m** — vein 5 (63.5,-582) ↔ mossBoulder (64,-585) | ≥ 2.5 ✓ |
| squatter↔prop min (all 237 props) | **1.8028 m** — squatter 2 (61.5,-580) ↔ center rubblePile (60.5,-578.5) | ≥ 1.8 ✓ (= A4's annotated 1.80 pair) |
| A4 claim: rubble S (57.5,-588) min-vein | **4.0311 m** (↔ vein 6 (57,-584)) | spec claim 4.03 ✓ |
| A4 claim: rubble W (51.5,-570) min-vein | **4.2720 m** (↔ vein 8 (50,-574)) | spec claim 4.27 ✓ |
| A4 claim: rubble W min-prop | **8.2462 m** (↔ treeStump (49.5,-578)) | spec claim 8.25 ✓ |
| A3 claim: vein 5 to squatter 2 "2.83→7.16" | **7.1615 m** | ✓ |
| veins↔bonePile min | **187.24 m** | > 4 ✓ |
| veins↔non-squatter enemy min | **78.72 m** (nearest: wolf-pack loop area enemy (-6.9,-519.6)); nearest enemy of ANY kind to a squatter: 85.77 m (-6.9,-519.6 ↔ squatter 3) | > 12 ✓ |
| veins↔campfires (W-6: fires ≥30 m from frozen seat) | vein↔nearest of 7 banditCampfires **89.01 m**; squatter↔nearest campfire **93.13 m** (fire (144.2,-536.9)) | ✓ (no campfire row added this round — none in the scar) |
| node-road (readable-from-road band 54–60) | frozen seat (58,-577.5) → northRoad polyline **59.42 m** (in band) ✓; min vein→road centerline **51.76 m** (worst-case with swayAmp 6 half-width margin ≥ 45.8 m clear of the 2.2 m half-width) | ✓ / info |

## 4. Ground-truth census conformance (IO-measured, task-authoritative)

- regionC.nodes = 16 dense rows: 8 bonePile (pre-existing WD1/ED1) + 8 ironVein at the
  8 census coords — **exact match** (C-1/C-3).
- regionC.enemies = 55: 28 wolf, 25 bandit (22 pre-existing + 3 squatters at the 3
  census coords), 2 coven — **exact match** (E-1/E-2).
- regionC.props = 237 incl. the 14 new (7 mossBoulder, 3 rubblePile, 2 treeStump,
  2 deadTree leaners) at the census coords — **exact match** (line-bounded count:
  223 at HEAD → 237; HEAD rows all byte-present; zero re-typed rows).
- `CONFIG.items.ironOre` and `CONFIG.gather.nodeTypes.ironVein` field-for-field —
  **exact match** incl. `yield.count:3`, `respawnSec:240`, `glowColor:0x8f5a33`,
  `scale:1.15`.
- Enemies census note: two comma-first rows (`,{ type: 'coven', x: -118.4, z: -238.2 }`
  and the new `,{ type: 'bandit', x: 56.5, z: -580.5 }`) are invisible to
  line-start-counting greps; counters must use `grep -oE "type: '[a-z]+'"` or
  match `,{`. My census (with that fix) reproduces 55 exactly.

## 5. Section G evidence (build law, executed WITHOUT overwriting)

- `tools/build_v8.py` (34 lines, read in full): regex-inlines style.css + every
  `<script src>` in index.html order into `prototype/builds/v8-playable.html`,
  retitles, writes. Executed **in memory** (no `OUT.write_text`): all five js files
  + style parse under the script-order regex; assembled artifact = **3,374,766
  bytes**; `CC-WM1` marker count in the assembled text = **30** ≥ 26 floor.
  Marker composition: 25 new rows individually tagged `// CC-WM1` (8 nodes +
  3 bandits + 14 props) + 5 banner/comment mentions = 30. PASS by replica;
  exit-0 equivalence is sound (the script's only failure modes are missing input
  files or a regex miss — neither occurs).
- The tracked `prototype/builds/v8-playable.html` (3,370,962 bytes) is
  pre-round (0 markers): the landed diff is **uncommitted working-tree state**, so
  the artifact is naturally stale. Building is IO's landing step (NO-GIT +
  no-overwrite for Testerbot); after IO commits and runs `tools/build_v8.py`,
  `grep -c "CC-WM1"` should read 30.

## 6. Non-blocking findings (amendments / notes)

1. **AMENDMENT REQUIRED (valspec, non-code): D-1 and E-4 truth tables carry
   WM1-A3-era rubble seats superseded by WM1-A4.** Valspec D-1 expected rows
   8/10 — `('rubblePile','55','-584.5','2.1','1.20')` (≈ line 392) and
   `('rubblePile','52','-572.5','3.3','1.10')` (≈ line 394) — and E-4's props
   list ` (55, -584.5) … (52, -572.5) ` (≈ lines 538–544) must become the
   amended-spec/A4 final seats `(57.5,-588)` and `(51.5,-570)`. Evidence the
   code is right and the valspec is stale: (a) amended spec W-4 final table
   annotates those seats with WM1-A4 clearances (4.03/1.80 and 4.27/8.25), all
   independently reverified above; (b) the valspec's own REPAIR BANNER (line
   ~777) lists only WM1-A3 supersessions, i.e. it predates A4; (c) running the
   valspec E-4 script verbatim fails **only** via those two stale coordinates
   (violations 2.06 m and 2.50 m), which vanish at the A4 seats. Also amend the
   REPAIR BANNER/`SPEC-CONFLICTS` note and the valspec's pre-edit line-number
   snapshot (CONFIG.js is now 3840 lines; anchors self-locate by comment strings
   so no anchor breaks).
2. **MINOR (spec-comment nit):** amended spec W-4/rubble S row annotation
   "WM1-A4: 4.03 m min-vein, **1.80 m min-squatter**" — computed min-squatter for
   that row is **7.57 m**; the 1.80 m figure belongs to the **center** rubble row
   (60.5,-578.5 ↔ squatter 2 = 1.8028 m). The Landed CONFIG comment on the center
   row carries the 1.80 correctly. No bar is violated on any row (min over all
   237 props = 1.8028 ≥ 1.8); purely a misattributed annotation.
3. **MINOR (info):** min vein→road-centerline 51.76 m sits 2.2 m below the
   54–60 m "readable-from-road" band for node seats; no bar in the spec/valspec
   governs veins↔road (the band is a site-seat law), so this is recorded
   informationally only.
4. **MINOR (info):** valspec D-1's `props rows total: 45` is a single-space
   shape census (pre-existing aligned/extras rows don't match its regex; true
   row count 237). It passes verbatim post-edit, so no action is needed; noted
   so future rounds don't confuse shape counts with row counts. Similarly the
   valspec's INDEPENDENT CENSUS line numbers are pre-edit snapshots (e.g.
   enemies close 646 → now 653; props close 1187 → now 1212) — all its anchors
   self-locate by comment strings and work as designed.

## 7. Probes and artifacts (Testerbot workspace `scratch/cc-wm1/`)

- `testerbot_master.py` — master ledger: all valspec anchors F, I-1..I-6, A-1..A-4,
  B-1..B-3, C-1..C-4, D-1..D-3, E-1..E-4, XW + independent WM1-A3/A4 math.
  Final ledger: 28 PASS / 0 code FAIL (the two documented valspec-truth probes are
  reported as amendments, not code failures).
- `testerbot_smoke.js` — Section H verbatim (window shim + three.classic.js +
  CONFIG.js + wh-ground.js): exit 0, all OK lines.
- `clearance_wm1.py`, `seat_probe_v2.js`, `bowl_probe.js`, `site_scan.py`,
  `census_check.py` — pre-existing IO/Devbot scratch, left untouched.

No file outside `scratch/cc-wm1/` and this verdict file was written; no git
mutation; no tracked file touched; no harness/browser run.

## 8. Verdict

**PASS** — blocking count **0**. The landed CC-WM1 candidate exactly implements
the amended (WM1-A1..A4-final) spec: all 5 append-only blocks intact (41
insertions, 0 deletions), every census, seat, and config field matches the
authoritative ground truth, every interior/edge clearance bar holds with margin,
cross-wiring is wired through the real require chain, and the build law passes
by replica with the marker floor exceeded (30 ≥ 26). One valspec amendment
(D-1/E-4 rubble truth tables → WM1-A4 seats) is requested for the record; it
does not block. IO may proceed: run `tools/build_v8.py` post-commit (expected
marker count 30) and commit.
