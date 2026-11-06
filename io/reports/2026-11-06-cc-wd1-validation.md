# CC-WD1 'West Wolfpack Den Site' — Testerbot INDEPENDENT VALIDATION REPORT
Gate step 4 · 2026-11-06 · Worktree /tmp/wh-worldfeat @ feat/world-visuals (HEAD 49106ea = origin)
Validator: Testerbot (independent; build note NOT trusted — every claim re-derived)
Law: io/specs/cc-wd1-west-wolfpack-den-valspec.md; Round spec: io/specs/cc-wd1-west-wolfpack-den-spec.md (Amendment A-1 = final site (-194,-451), 11 props + 4 nodes)

## Verdict table (V-0..V-12)

| class | scope | result |
|---|---|---|
| V-0 | baseline recording, censuses, sha | PASS |
| V-1 | build + bundle marker ledger | PASS |
| V-2 | CONFIG diff shape (pure-add law) | PASS |
| V-3 | gather.js 2-line terrain seat | PASS |
| V-4 | node --check 7 files | PASS |
| V-5 | asset/type legality | PASS |
| V-6 | wolfPacks byte-purity + censuses | PASS (ADJ-1 window drift) |
| V-7 | file-set law + save safety + NO-GIT | PASS |
| V-8 | clearance geometry G-1..G-7 (+G-2n) | PASS (ADJ-2 G-6a=4.27) |
| V-9 | seat probe G-8 (15 rows) | PASS |
| V-10 | art law (no warm accents/lights) | PASS |
| V-11 | build note + process law | PASS (notes, non-blocking) |
| V-12 | adjudication rubric | PASS |

**VERDICT: PASS — 13/13 classes, 0 blocking, 3 adjudications resolved (ADJ-1/ADJ-2/ADJ-3), 4 non-blocking notes (N-1..N-4).**

---

## V-0 Baseline recording — PASS
HEAD (49106ea) extracted to /tmp and compared against working tree.
- `git show HEAD:prototype/js/CONFIG.js | sha256sum` → 8197e89a9...; working-tree CONFIG sha → 5b064ce4b...; gather sha → 492d63370... (pre/post differ exactly by this round).
- HEAD line counts: CONFIG 3587 → working 3618 (+31); gather 178 → 178.
- HEAD censuses reproduced independently: `grep -c "'west'"` = 6; `grep -c "type: 'wolf'"` = 28 (both HEAD and post); 7 wolfPacks rows; regionC props array [810,1166) = 232 rows = 221 pre + 11 new (Testerbot full tolerant census — matches valspec 221 exactly); regionC fires = 7 at CONFIG rows 998/1004/1010/1069–1072 (the valspec's exact enumeration); west waypoints = 8; C roads = 9; regionB bonePile nodes = 4 (455–458); 'no nodes: in regionC at HEAD' confirmed — `nodes:` keys at HEAD sit only at 345 (regionA) and 449 (regionB); HEAD bundle = 108,008 lines / head bonePile grep 5 (4 regionB nodes + 1 nodeTypes row).

## V-1 Build + bundle marker ledger — PASS
- `python3 tools/build_v8.py` → exit 0, "wrote ... 3336413 bytes" (byte-exact match to the build note's final bundle figure). Post-build `git diff --stat prototype/builds/v8-playable.html` = 33 insertions(+), 2 deletions(-): exactly the CONFIG +31 hunk and the gather.js seat ×2 (the original props-close `],` is reused as the nodes-array close, so the bundle shows +33/−2 with no third surface — the ED-3-sanctioned in-bundle shape).
- `grep -c west_hollow_den prototype/builds/v8-playable.html` → 17 (≥ 6 and > baseline 0).
- Per-row distribution (awk gsub per line): NO line carries more than 1 hit — 17 hits over 17 distinct source lines (2 banner comments + 11 prop rows + 4 node rows). Contributors = 17 ≥ 4; max per-row = 1 ≤ 3. B2/bloat law holds with margin.

## V-2 CONFIG diff shape — PASS
- `git diff prototype/js/CONFIG.js | grep -c "^-[^-]"` → 0; `grep -c "^+[^+]"` → 31 (pure-add, B1 byte-purity holds: zero deleted/context-rewritten lines).
- Hunks: `grep -c "^@@"` = 1 anchored (at CONFIG 1145) + 1 in-bundle splice; the insertion sits at the props tail with the original `],` reused above `nodes:` (ED-3 sanctioned boundary).
- Row law: every new prop row is `{ asset, x, z, rotY, scale }` exactly — `git diff | grep "^+" | grep '"y:"'` → no match (y: never set on a new row; B3 holds).
- Set law: new asset rows = deadTree ×3 (−190,−446 / −197,−445 / −201,−445), mossBoulder ×3 (−199,−455 / −196,−458 / −201,−451), skullPile ×2 (−189,−454 / −187,−452), buriedCoffin ×1 (−186,−456), rubblePile ×2 (−189,−449 / −186,−446) = 11; node rows = 4 × `{ type: 'bonePile', x, z }` (−192.5,−461 / −184,−450 / −204,−453.5 / −198.5,−441). Coordinates byte-identical tospec A-1 final table.
- Banner law: both banner comments (props-block 8-line and nodes-block 3-line) carry the literal `west_hollow_den`.

## V-3 gather.js terrain seat — PASS
- `git diff prototype/js/gather.js | grep -c "^-[^-]"` → 2; `grep -c "^+[^+]"` → 2; hunks = 2 context-window headers over ONE logical seat change set (makeNode ~60, reshuffle ~146).
- Pre-images byte-verbatim vs HEAD: `    holder.position.set(x, 0, z);` and `    node.mesh.position.set(pick.x, 0, pick.z);` (extracted from HEAD at 57–62 / 131–148 — exact match; no other line in either region touched).
- Seat semantics: both added lines read `window.WH_GROUND && window.WH_GROUND.has(regionId) ? window.WH_GROUND.heightAt(regionId, x, z) : 0` — makeNode uses its own `regionId` parameter (signature untouched); reshuffle reads `node.regionId` (established node property — HEAD reshuffle already keys `this.pools[node.regionId + ':' + node.type]`). `has()` guard present at both sites ⇒ regionA/B flat pools (no heightfield) keep y=0 (N-3 no-op verified by guard construction).
- No logic drift: CONFIG.gather.marker rows byte-identical (no marker hunk in the diff); marker bob (`marker.position.y` sin loop), respawn timing, harvest, pools untouched — the diff contains ONLY the two y-arguments.
- `node --check prototype/js/gather.js` → OK.
- Execution proof (Testerbot probe tb_node_probe.js): the REAL NodeManager (require'd from the worktree) against regionA/regionB/regionC region-defs-shaped maps captured 27 makeNode seats, including all 4 regionC bonePile rows seated at the CONFIG coordinates with mesh y == WH_GROUND.heightAt to the printed precision:
  PASS (-192.5,−461) y=1.761 | PASS (−184,−450) y=1.892 | PASS (−204,−453.5) y=1.220 | PASS (−198.5,−441) y=1.617 — 4/4.

## V-4 Syntax gate — PASS
`for f in CONFIG.js gather.js game.js save.js region-manager.js region-defs.js assets.js; do node --check ...; done` → all seven print OK, exit 0.

## V-5 Asset and node-type legality — PASS
- `git diff --stat -- prototype/js/assets.js` → empty (no GLB/pngs/manifest edits; B6).
- New asset keys ∈ {deadTree, mossBoulder, skullPile, buriedCoffin, rubblePile} — all five in the manifest (assets.js 32/64/72/21/99).
- New node `type:` = bonePile ×4; bonePile pre-exists in CONFIG.gather.nodeTypes (CONFIG 3387–3388: name 'Bone Pile', rarity common, yield boneShard ×2, respawnSec 150). Zero new nodeType/economy/item/recipe/loot rows in the diff.
- Runtime proof: NodeManager's unknown-type guard path (`console.warn '[gather] unknown node type'`) never fired in the flow probe — regionC's 4 rows all resolved to kits.

## V-6 wolfPacks byte-purity + censuses — PASS (ADJ-1)
- **ADJ-1 (window drift, per valspec clause + task adjudication (a)):** the valspec's sed window (2159,2179) predates build geometry; the A-1 +31 CONFIG lines shift wolfPacks to 2190–2210. At the true post-A-1 window: `sed -n '2190,2210p' prototype/js/CONFIG.js | sha256sum` → **2e2afb6097e39a166f58107231e3f74cfbdfe77f06e383a658db5b20a8dfd1bd** — byte-exact match to the V-0 recorded law value. Window contents verified to span exactly `wolfPacks: [` … `],` with all 7 pack rows (east/west/north/sw/se/ss/nw2) and all waypoints visible inside; the stale window's sha (820a16c6…) covers shifted content and is discarded per the drift clause.
- `git diff prototype/js/CONFIG.js | grep -n "wolfPacks\|waypoint\|packId"` → **no output** (grep exit 1): no hunk touches the wolf system. The west pack keeps its exact 8 waypoints (byte-identical set re-extracted: (-190,-420)(-215,-418)(-224,-388)(-224,-362)(-200,-358)(-178,-340)(-166,-372)(-172,-402)).
- Censuses: `'west'` = 6 (rows 580–583, 780, 2194 — the valspec's named rows, shifted +31 for 2194 vs 2163); `type: 'wolf'` = 28; 7 wolfPacks rows; 28 enemies rows = 7 packs × 4 members verified by packId (east/north/nw2/se/ss/sw/west ×4). Zero new wolf/pack/behavior rows in the diff (B7).

## V-7 File-set law + save safety + NO-GIT — PASS
- `git status --short`: modified = {prototype/builds/v8-playable.html, prototype/js/CONFIG.js, prototype/js/gather.js} only; untracked = {io/reports/cc-wd1-build-note.md, io/specs/cc-wd1-*.md ×2, scratch/cc-wd1/}. GO-list files all empty: save.js / game.js / enemy.js / region-manager.js / region-defs.js / assets.js / wh-ground.js diffs = 0 lines each (N-4 covers the io/specs pair).
- `git diff prototype/js/save.js | wc -l` → 0 (no save surface; A-8).
- NO-GIT: nothing staged (`git diff --cached` empty), HEAD 49106ea = origin branch tip, zero new commits.
- Bundle is a deterministic artifact of the two source diffs (rebuild was content-stable; diff stayed 33+/2−).

## V-8 Clearance geometry — PASS (ADJ-2)
- `python3 scratch/cc-wd1/clearance.py` → exit 0; every row PASS; values reproduced EXACTLY as pasted in the build note (Δ = 0.00 ≤ 0.05): G-1 22.66 ≥ 5 · G-2 25.96 ≥ 25 · G-2n 22.66 ≥ 20 · G-3 80.97 ≥ 20 · G-4 72.81 ≥ 30 · G-5a 202.47 ≥ 3 · G-5b 23.15 ≥ 4 · G-5c 2.83 ≥ 2.5 · G-6a 4.27 ≥ 4 · G-6b 3.61 ≥ 3 · G-6c 13.66 ≥ 6 · G-6d 10.97 ≤ 12 · G-7 221.97 ≤ 262.
- **Testerbot independent re-derivation (two probes, deliberately stricter):** scratch/cc-wd1/tb_independent_check.py (own parser, own math) and scratch/cc-wd1/tb_full_census.py (tolerant-spacing census = the valspec's full sets: 221 pre-props, 7 fires, 28 wolves, 9 roads). Every margin PASS on the full sets: G-3 **67.94** (7-fire census — stricter than the script's 80.97, see N-2), G-5a **64.25** (full 221-row pre-prop set), G-5b 23.15, G-6a 4.27, G-6b 3.61, G-6c 13.66, G-6d 10.97, G-7 221.97. Direction-of-error audit: the script's omitted rows (see N-2) are all FARTHER from the den than the binding pairs, so script undercounting never inflated a margin.
- **ADJ-2 (G-6a nodes-vs-tree 4.27 m, per task adjudication (b)):** REAL AND CORRECT — the 4.27 m pair is mouth-approach node (−198.5,−441) ↔ thicket-mouth deadTree (−197,−445), the by-design NE approach element named in the A-1 node comment ("thicket mouth approach NE"); second-nearest tree = deadTree (−201,−445) at 4.72 m. A-1 re-derived the bar engine-aligned to CONFIG.gather.placement (treePropM 4 / propM 3): 4.27 ≥ 4.0 meets the amended law. NOT a blocker.
- G-7: union max distance from C center (0,−366) = 221.97 ≤ 262 (site ~40 m inside cap; no N-2 rim-radial tension on the A-1 site).

## V-9 Seat probe (G-8) — PASS
- `node scratch/cc-wd1/seat_probe.js` → exit 0; `WH_GROUND.has('forest_of_the_old_king') = true`; all 15 rows PASS, values byte-identical to the build note (≤ 0.05 m / ≤ 0.5° tolerance — here Δ = 0): y ∈ [1.22, 1.98] (|y| ≤ 26), slope1m ∈ [0.6°, 9.0°] (≤ 31°). Largest slope: mossBoulder (−201,−451) at 9.0°.
- Probe legality: CORE THREE-free pattern verified — globalThis.window shim, vendored three.classic.js, CONFIG.js, wh-ground.js; real WH_GROUND.heightAt/slopeTan (wh-ground.js exports at 373: has/build/heightAt/footY/mesh/slopeTan/…; slopeTan = ±0.5 m central differences = the 1 m span G-8 names). No browser/puppeteer artifact.
- Cross-check: the flow probe's NodeManager-seated mesh y values (1.761/1.892/1.220/1.617) match heightAt calls exactly — the seat line actually fires in the live code path.

## V-10 Art law — PASS
- `git diff prototype/js/CONFIG.js | grep "^+" | grep -inE "lantern|campfire|startLit|light:|color|0xff|0xf[0-9a-f][0-9a-f]|ember|torch"` → **no output** (exit 1): no lantern/campfire/startLit/light/color/glow/hex rows in ANY added line. Warm accent stays on the hunter (concept-05 anchor law).
- bonePile glowColor 0xbbbbaa (CONFIG 3388) pre-existing nodeTypes row — not this round's (present at HEAD 3356; note's "CONFIG 3356" cites pre-diff numbering, consistent with the +31 shift).

## V-11 Build note + process law — PASS
- io/reports/cc-wd1-build-note.md exists and contains every required paste: exact `git diff --stat` per file (CONFIG 31+, gather "4 +++---" = 2+/2−), bundle marker ledger (17 hits, per-contributor enumeration), FULL clearance table, FULL seat-probe output, numbered deviations ED-9/ED-10. Every paste re-verified by Testerbot — all reproduced exactly except one summary figure (N-1).
- scratch/cc-wd1/clearance.py + seat_probe.js present, runnable, exit 0 (V-8/V-9).
- No harness/browser/puppeteer artifacts anywhere in the diff, scratch, or note. NO-GIT honored: zero staged entries, zero commits/pushes.
- **ADJ-3 (ED-9.IO fold, per task adjudication (c)):** the note discloses folding an inherited 3-line wrapped ternary (4 add/2 del) into the valspec's EXACTLY-2-lines shape pre-validation. Judged on the CURRENT diff's merits: the landed form IS the sanctioned ED-6 inline-ternary shape, 2 del/2 add, verbatim pre-images, guard semantics verified live (flow probe), zero collateral hunks. ED-6 governs exactly this variance — an explicitly sanctioned expected-class deviation. No violation; the fold itself needed no sanction beyond disclosure (PRIMARY law <20 lines, no logic change, disclosed — all three hold).
- ED-10 (recorded): the V-6 window drift — adjudicated at ADJ-1 above.

## V-12 Adjudication rubric — PASS
Ran in valspec order (1→9). Zero-vs-list rule: no blocking item discovered unrecorded. All builder-recorded deviations adjudicated expected-class (ED-9 via ADJ-3, ED-10 via ADJ-1). Every check green, zero blocking ⇒ **PASS**.

---

## Deviations ledger (final)

Adjudications (all resolved; none blocking):
- **ADJ-1 = ED-10 (V-6 window drift):** lawful per the valspec's window-drift clause + task adjudication (a): sha256 at the true post-A-1 window (2190,2210) = 2e2afb60…, byte-exact vs the V-0 recorded value. RESOLVED.
- **ADJ-2 (G-6a = 4.27 m):** mouth-approach node ↔ mouth deadTree by design; meets the A-1 engine-aligned ≥ 4.0 bar (treePropM). Per task adjudication (b): not a failure. RESOLVED.
- **ADJ-3 = ED-9 (IO fold of the inherited seat ternary):** current-diff form = sanctioned ED-6 shape, 2/2/2 hunks, semantics live-verified. RESOLVED.

Non-blocking notes:
- **N-1 (note cosmetic):** the build note's diff-stat summary prints "33 insertions(+), 3 deletions(-)" for the two source files; the re-derived truth is 33 insertions(+), **2** deletions(-) (gather.js 2+/2−, CONFIG 31+/0−). One-character slip in a summary line; every load-bearing paste exact. No action.
- **N-2 (tool census bug — harmless, disclosed):** clearance.py's anchored prop regex `\{ asset: 'X', x: …` misses rows with double spaces after commas (fires at CONFIG 998/1004/1010 use "',   x:'"), so its census sees 5 fires and 385−… pre-props instead of the valspec's 7/221. Direction-of-error verified: the dropped fires (−60,−186), (95,−236), (−140,−506) are all ≥ 148 m from the den (binding fire pair = −106.1,−472.1 @ 67.94 m), and the dropped pre-props sit far from the den (G-5a full-set 64.25 vs script 202.47 — script value was conservative in the WRONG direction but still ≥ limit either way). Testerbot's stricter full-set recompute passes every margin. Optional future hardening: `\s+` after commas in clearance.py. Not blocking.
- **N-3 (flat-pool no-op):** regionA/regionB/hold_outskirts pools carry no heightfield ⇒ `has()` false ⇒ y=0; guard construction + flow probe (regionA/B seats unchanged) confirm no behavioral change outside regionC.
- **N-4 (untracked io/specs pair):** git status also lists the round's own governing docs (cc-wd1 spec + valspec) as untracked; they are gate-1 authorship artifacts staged for validation by orchestration, not build output — no GO-list file is touched and all enumerated NO-GO targets (save/game/enemy/region-manager/region-defs/assets/wh-ground) are byte-empty. Not a V-7 breach of substance; recorded for the IO commit step (which will fold them into the round commit).

## Commands run (key outputs)
1. git status -sb / --short / diff --stat → file set per V-7; HEAD 49106ea = origin.
2. git show HEAD:… (baseline extraction + sha256) → pre-shas recorded; post differs only by this round.
3. git diff CONFIG.js | counts → 0−/31+/1 hunk; grep '"y:"' → none; grep asset/type rows → 11 props + 4 nodes, exact A-1 coordinates.
4. git diff gather.js | counts → 2−/2+/2 hunks; HEAD pre-images extracted and byte-compared; guard/regionId sources verified in body.
5. node --check ×7 → all OK.
6. assets/save/game diffs → empty ×7 targets. git diff --cached → empty.
7. sed -n '2190,2210p' CONFIG.js | sha256sum → 2e2afb60… (law value); stale-window sha 820a16c6… discarded per drift clause.
8. git diff | grep wolfPacks|waypoint|packId → empty; censuses 6/28/7/8/9 (independent, packId-tagged).
9. python3 tools/build_v8.py → exit 0, 3,336,413 bytes; bundle diff 33+/2−; grep -c west_hollow_den → 17; per-row max 1.
10. python3 scratch/cc-wd1/clearance.py → exit 0, 13/13 PASS, values == build note paste.
11. node scratch/cc-wd1/seat_probe.js → exit 0, 15/15 PASS, values == build note paste.
12. Testerbot scratch probes (new, this gate): tb_independent_check.py → CLEARED 13/13 (own parser); tb_full_census.py → CLEARED 13/13 (full tolerant sets 221/7/28/9); tb_node_probe.js → 4/4 NodeManager flow seats == heightAt; tb_census_diag.py / tb_miss_diag.py / tb_scope_diag.py / tb_fires_diag.py → census discrepancy forensics (N-2 provenance).

## Final verdict

VERDICT: PASS — 13/13 classes green, 0 blocking deviations, 3 adjudications resolved (window-drift sha equality; G-6a 4.27 m by-design mouth approach; ED-9 fold judged on merits), 4 non-blocking notes recorded. The round is ready for IO's post-gate slice (build+commit+push → serve → Nicko playtest).
