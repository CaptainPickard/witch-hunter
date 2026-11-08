# CC-AD1 Veil Spire crypt mini-delve — Testerbot verdict (2026-11-06)

Testerbot independent validation of commit **6e9f8bc** (`feat(world): CC-AD1 Veil Spire crypt mini-delve - doc 47 strata V1`) in worktree `/tmp/wh-worldfeat`, branch `feat/world-visuals`.

- **Validation law:** `io/specs/cc-ad1-veil-crypt-valspec.md` (284 lines, committed in the very commit under test; style parent `cc-ec1-coven-acolyte-valspec.md`). Read FIRST; every V-check executed against the landed diff.
- **Diff basis (diff-basis variance noted per task law):** `git diff 264c703..6e9f8bc -- prototype/js/CONFIG.js prototype/js/region-defs.js prototype/js/game.js prototype/builds/v8-playable.html scratch/cc-ad1/ io/specs/` — 10 files, +1179/−6: CONFIG.js (+106/−0), region-defs.js (+34/−0), game.js (+3/−3), bundle (+143/−3), scratch/cc-ad1/ (4 new: clearance.py, connection_probe.js, save_roundtrip.js, solve_geometry.py), io/specs/ (2 new). The commit also contains `io/reports/2026-11-06-cc-ad1-valspec.md` (+284) — **confirmed a byte-identical copy of the valspec** (`cmp` clean, exit 0), not a validation report. Validation runs on the diff, not a working-tree change.
- **VERDICT: PASS — 0 blocking.**
- Adjudication per valspec B1–B12 / ED-1…ED-8 tables: no blocking class fired; 3 process-class variances and 2 content-drift variances recorded below with explicit adjudications.

---

## V-1 build + marker ledger

**Build reproduction** (law: copy bundle, rebuild IN the worktree with `tools/build_v8.py`, sha256 compare, restore tree):

```
$ cp prototype/builds/v8-playable.html scratch/cc-ad1-validation-tmp/bundle_committed.html
$ python3 tools/build_v8.py
wrote /tmp/wh-worldfeat/prototype/builds/v8-playable.html 3333512 bytes     (exit 0)
$ sha256sum scratch/cc-ad1-validation-tmp/bundle_committed.html prototype/builds/v8-playable.html
65404e7bde083d9cd8c86961e4053661c53dc2a2ee70f9e4383762c541a3acd2  (both files — IDENTICAL)
$ git checkout -- prototype/builds/v8-playable.html
$ cmp <(git show 6e9f8bc:prototype/builds/v8-playable.html) prototype/builds/v8-playable.html   → exit 0, IDENTICAL
```

- Build exit **0**. **Byte-identity: TRUE** — rebuilt bundle `3333512` bytes, sha256 `65404e7bde083d9cd8c86961e4053661c53dc2a2ee70f9e4383762c541a3acd2`, identical to the copy AND byte-identical to the committed bundle after restore. Working tree left clean (no `prototype/` modifications).
- Committed bundle `grep -c veil_crypt` = **10** (≥ 8 required).
- Post-rebuild bundle marker count = **10** (≥ 8; B12 clean).

## V-2 key-shape census (CONFIG.js regionE block)

Pure-add verified: the CONFIG.js diff carries **0 minus lines** (excluding headers); 1 hunk, +106.

| law | evidence | verdict |
|---|---|---|
| V-2.1 `regionE` mirrors regionD's key set, same order, new values | runtime key-set compare: regionD/regionE top-level keys identical (`id,name,center,groundRadius,groundY,groundColor,groundColor2,groundSeed,scatter,spawn,gravityY,fogColor,fogDensity,ambientLightLevel,door,enemies,props`); regionE carries none of regionD's boss-lair keys (`lairs`,`rotLair` — no lair in a boss-free crypt, consistent with the spec); `door` sub-key sets identical, all 12 | PASS |
| V-2.2 block placed after regionD's close brace, before the Round E comment | `regionE:` at CONFIG.js:1359; regionD block closes 1357; Round E scatter comment at 1455 | PASS |
| V-2.3 `enemies:` two coven rows | `1410: { type: 'coven', x: 5, z: -592 }, 1411: { type: 'coven', x: -6, z: -590 }` — normative world rows per N-2 (crypt-local (5,4)/(−6,6)); the ED-1 slip row (−6,−594) did **not** materialize | PASS |
| V-2.4 `door:` row | planeZ −612, doorX 0, doorHalfWidth 2.4, suspendDepthM 0, wallGapPadM 0, interactM 3.5, interactAt {0,−596}, land {forest_of_the_old_king (0,−596,face 0,−366), veil_crypt (0,−604,face …)}, fadeIn 0.3, fadeOut 0.5, exitFadeOut 0.8, text prompt 'E - Descend into the crypt' | PASS |
| V-2.5 no `constantPhase` row added | absent from the block | PASS |
| V-2.6 8 segment rows ≤ every-2-m | 8 whWall rows (4× whWallA, 4× whWallB) at CONFIG 1419–1426. **Drift note:** rows carry `wall: 7` where the valspec's reference text says `wall: 8` (echoing regionD's model rows: regionD chord 14.89 m / 8 colliders). Law intent = collider spacing ≤ every 2 m; delivered chord = scale 7.35 × 1.899 = **13.96 m / 7 colliders = 1.994 m spacing** — the ≤2 m law holds; clearance reconstructs 56 colliders and ring closure passes (V-14 row 9) | PASS (note) |

## V-3 region-defs.js shape (connections[3])

Diff = **1 hunk, pure-add** (+34/−0), single contiguous insert after the regionD C-side registration (`connections[2].sides` block). Content, in valspec order: (a) regionE registration line, (b) the C↔E tomb-door push, (c) `connections[3].sides[regionC]=-1 / sides[regionE]=+1`. Helper/export block untouched; `connections.length` = **4** (runtime-verified).

- Door row shaped exactly on connections[2]: axis `'z'`, `planeCoord: ED.planeZ` (= −612), `door:` carries **`arch: null`** and **`gatedTo: null`** explicitly (N-3/C0-1 — probe-asserted), `walkFrom: CFG.regionE.id`, `interact: { from: regionC, x: 0, z: −596, radius: 3.5 }`, `land: ED.land`, `doorX/doorHalfWidth/suspendDepthM/wallGapPadM` off `ED`.
- `sides` exactly `regionC −1 / regionE +1`; probe: `sideIn(conn, regionE) === 1`, `sideIn(conn, regionC) === −1`, `planeIn(conn, regionE) === true`, `planeIn(conn, regionC) === false`.

**Shape variances (inside the sanctioned example's neighborhood, adjudicated under ED-3/V-4):** alias named `ED` (vs regionD's `DD` pattern; N-3's normative requirement is what the row CARRIES, not the alias name), and the makeRegion line sits inside the same insert block (after the banner comment) rather than directly after the regionD line — same content, append-only law intact. Both **PASS with note**, ED-3/ED-6 class. No B4 trigger.

## V-4 game.js diff (genericization)

Exactly **3 hunks**, all sanctioned substitutions, nothing else:

```
@@ -1904,7 +1904,7 @@   -var D = CFG.regionD.door;                →  +var D = conn.door;
@@ -2216,7 +2216,7 @@   -text = CFG.regionD.door.text.prompt;     →  +text = denDoorNear().door.text.prompt; // C8/AD1 veil_crypt
@@ -3068,7 +3068,7 @@   -startDenFade(0, CFG.regionD.door.exitFadeOut, null); → +startDenFade(0, tr.conn.door.exitFadeOut, null);
```

- Prompt-chain hunk = RHS substitution only; surrounding context identical, chain order unchanged (no B5).
- Prompt string exact: `'E - Descend into the crypt'` (CONFIG 1402), conn-carried (V-8).
- Per ED-3's sanctioned set (`var D = conn.door` is its own named example; inline `.door.text` vs hoisted local; `tr.conn.door` exitFade): **no deviation** to adjudicate.

## V-5 marker censuses / leak law

`grep -c veil_crypt`: CONFIG.js **7** (≥5 ✓), region-defs.js **2** (≥2 ✓), game.js **1** (≥0 floor ✓) → sum **10**.

**Leak law:** `grep -rl veil_crypt prototype/js/` → CONFIG.js, game.js, region-defs.js **only**. No leak outside the sanctioned set.

## V-6 connection probe (THREE-free, delivered harness)

```
$ node scratch/cc-ad1/connection_probe.js
PASS  connections[3] exists … (29 rows, all PASS)
PASS  forceCross action = cross
PASS  forceCross newActiveId = veil_crypt
PASS  forceCross mappedPos = land row (0, -604)
PASS  activeId now veil_crypt
PASS  tickTransition at land row: no re-cross
PASS  crypt mouth walk-out crosses (action cross)
PASS  walk-out lands on C side land row (0, -596)
PASS  activeId back to regionC
---
connection_probe: 29/29 PASS
(exit 0)
```

Full 29 rows cover every harness shape required: connections[3] identity/from/to, connectionBetween, sideIn ±1, planeIn (crypt true / C false), insideDoorWindow (0 true; ±3.5 false at halfWidth 2.4), arch/gatedTo null carried, walkFrom/interact.from, region registration (spawn (0,−604), center (0,−596), groundRadius 20, props 20 = 3+8+9, enemies 2 coven), forceCross semantics, land-row no-re-cross (C0-3), crypt-mouth walk-out, return to regionC. Harness stubs match the valspec: `window = {}`, localStorage stubs, `THREE = undefined` at eval time; evals CONFIG → region-defs → region-manager.

## V-7 side/plane law

Via the real `WH_RegionManagerLogic` (probe + Testerbot extension): E occupies `z <= planeZ` (side +1), C side −1 (D-symmetry C0-3), plane exists ONLY from the crypt side. Testerbot-added C-side inertness cases (the law's negative half):

```
$ node (Testerbot probe: logic(activeId=C).tickTransition over z −613/−611 at x 0, ±10)
C-side (0,-613) -> action=none | (10,-613) -> none | (-10,-613) -> none | (0,-611) -> none
C-SIDE PLANE INERTNESS: PASS (no plane crossing exists while in regionC)   (exit 0)
```

## V-8 / V-9 / V-10

- **V-8** prompt row conn-carried: CONFIG 1402 defines it; game.js:2219 reads `denDoorNear().door.text.prompt`. Bundle carries both rows (`Enter the den` count in bundle unchanged = 1).
- **V-9 file-set law:** `git diff 264c703..6e9f8bc -- prototype/js/save.js prototype/js/player.js` is **empty** (exit 0, no output); save.js/player.js byte-identical at both ends. Full commit file set = exactly the Allowed set (see B10 table).
- **V-10** `grep -n "CFG.regionD" prototype/js/game.js` → **exit 1, zero matches** (baseline 3 → 0: all three fully genericized, cleaner than ED-4's residual branch). Bundle-level `CFG.regionD` count = 10, fully attributed: npc.js 5 + region-defs.js 5 — both pre-existing, both files outside this round's game.js diff. **No new CFG.regionD read anywhere. B5 clean.**

## V-11 art law

1. `git diff --stat -- prototype/js/assets.js` over the basis → **empty** (no new GLB rows, no pngs, no CHARACTERS).
2. RegionE asset keys exactly the 8 verified manifest keys, counts: whWallA 4, whWallB 4, stoneSarcophagus 1, stoneSteps 2, skullPile 2, blightcap 4, mossBoulder 2, rubblePile 1 — total 20 rows (probe asserts 20).
3. Palette `grep -nE "0xff|0xf[0-9a-f][0-9a-f]"` over regionE block → **exit 1, zero rows**. groundColor 0x121418, groundColor2 0x171a20, fogColor 0x0a0810, ambientLightLevel 0.07 all present; fogDensity 0.13 ≈ d95 13.3 m; the single crimson accent = blightcap caps (asset rows only, no light code).
4. `groundRadius: 20` ✓, `scatter: false` (mirrors den) ✓, `gravityY: -22` (den's value) ✓.

## V-12 syntax gate

```
$ for f in game.js CONFIG.js region-defs.js region-manager.js assets.js; do node --check prototype/js/$f && echo "$f OK"; done
game.js OK | CONFIG.js OK | region-defs.js OK | region-manager.js OK | assets.js OK   → 5/5, exit 0
```
Task-law extension: `node --check` on **save.js** and **player.js** → OK (7/7 across the seven checked files). B9 clean.

## V-13 save round-trip (THREE-free, delivered harness)

```
$ node scratch/cc-ad1/save_roundtrip.js
PASS  capture regionId = veil_crypt
PASS  capture player pos rides through
PASS  JSON round-trip shape = v-less profile with 5 block keys
PASS  restore: validRegion(veil_crypt) gate passes (save.js:39)
PASS  restore: teleport target rid = veil_crypt (save.js:273)
PASS  restore: player pos = saved (3, 7)
PASS  restore: hp clamped to saved 77 (min hpMax)
PASS  restore: focus 11 / stamina 22 restored
PASS  restore: L1 discover fired with veil_crypt
PASS  restore: camp.sites crypt row re-placed through camp.place (saved id drives siteSeq)
PASS  restore: camp.respawn crypt row restored (save.js:264)
PASS  negative: restore with veil_crypt_gone does not throw
PASS  negative: fallback rid = activeId (C stays)
PASS  validRegion(veil_crypt_gone) === false
---
save_roundtrip: 14/14 PASS
$ grep -cn "require('three')\|THREE\.\|puppeteer\|playwright\|browser" scratch/cc-ad1/save_roundtrip.js
0
```

Harness shape source-audited: full-stub `game` surface per the valspec (player hands/belt/bindings/consumables/respawnAt/isCasterHand; cooking.buffs with list/clear/add; camp.place/packUp; dayNight; regionManager.logic; WH_LEVEL). Required assertions 1–6 all present and PASS, including the two negative controls and the three gates as outcomes (sites 253 / respawn 264 / teleport 273). B8 clean.

## V-14 clearance geometry (reproduction + independent re-derivation)

```
$ python3 scratch/cc-ad1/clearance.py
coven rows: 2 | prop rows: 12 | wall rows: 56 | land: (0.0, -604.0)
land -> center (inside r 20)                            8.00 <= 20.0  ok  (margin 12.00)
coven1 -> land (>= 8.0)                                13.00 >=  8.0  ok  (margin 5.00)
coven2 -> land (>= 8.0)                                15.23 >=  8.0  ok  (margin 7.23)
coven1 <-> coven2 (>= 8.0)                             11.18 >=  8.0  ok  (margin 3.18)
coven1 -> nearest wall (>= 4.0, 16-rho law)             9.60 >=  4.0  ok  (margin 5.60)
coven2 -> nearest wall (>= 4.0, 16-rho law)             7.51 >=  4.0  ok  (margin 3.51)
prop stoneSarcophagus -> nearest wall (>= 4.0)         10.00 >=  4.0  ok  (margin 6.00)
prop stoneSarcophagus -> land (>= 6.0)                 14.00 >=  6.0  ok  (margin 8.00)
prop stoneSarcophagus -> coven1 (>= 5.0)                5.39 >=  5.0  ok  (margin 0.39)
prop stoneSarcophagus -> coven2 (>= 5.0)                6.00 >=  5.0  ok  (margin 1.00)
prop stoneSteps       -> nearest wall (>= 4.0)          8.14 >=  4.0  ok  (margin 4.14)
prop stoneSteps       -> land (>= 6.0)                 15.83 >=  6.0  ok  (margin 9.83)
prop stoneSteps       -> coven1 (>= 5.0)                7.10 >=  5.0  ok  (margin 2.10)
prop stoneSteps       -> coven2 (>= 5.0)                5.31 >=  5.0  ok  (margin 0.31)
prop stoneSteps       -> nearest wall (>= 4.0)          8.14 >=  4.0  ok  (margin 4.14)
prop stoneSteps       -> land (>= 6.0)                 15.83 >=  6.0  ok  (margin 9.83)
prop stoneSteps       -> coven1 (>= 5.0)                5.52 >=  5.0  ok  (margin 0.52)
prop stoneSteps       -> coven2 (>= 5.0)                7.23 >=  5.0  ok  (margin 2.23)
prop skullPile        -> nearest wall (>= 4.0)          4.30 >=  4.0  ok  (margin 0.30)
prop skullPile        -> land (>= 6.0)                 11.70 >=  6.0  ok  (margin 5.70)
prop skullPile        -> coven1 (>= 5.0)               17.89 >=  5.0  ok  (margin 12.89)
prop skullPile        -> coven2 (>= 5.0)               11.18 >=  5.0  ok  (margin 6.18)
prop skullPile        -> nearest wall (>= 4.0)          4.60 >=  4.0  ok  (margin 0.60)
prop skullPile        -> land (>= 6.0)                 15.56 >=  6.0  ok  (margin 9.56)
prop skullPile        -> coven1 (>= 5.0)               16.03 >=  5.0  ok  (margin 11.03)
prop skullPile        -> coven2 (>= 5.0)                5.83 >=  5.0  ok  (margin 0.83)
prop blightcap        -> nearest wall (>= 4.0)          4.46 >=  4.0  ok  (margin 0.46)
prop blightcap        -> land (>= 6.0)                 11.88 >=  6.0  ok  (margin 5.88)
prop blightcap        -> coven1 (>= 5.0)                9.60 >=  5.0  ok  (margin 4.60)
prop blightcap        -> coven2 (>= 5.0)               19.47 >=  5.0  ok  (margin 14.47)
prop blightcap        -> nearest wall (>= 4.0)          4.76 >=  4.0  ok  (margin 0.76)
prop blightcap        -> land (>= 6.0)                 18.50 >=  6.0  ok  (margin 12.50)
prop blightcap        -> coven1 (>= 5.0)                5.59 >=  5.0  ok  (margin 0.59)
prop blightcap        -> coven2 (>= 5.0)               12.50 >=  5.0  ok  (margin 7.50)
prop blightcap        -> nearest wall (>= 4.0)          6.00 >=  4.0  ok  (margin 2.00)
prop blightcap        -> land (>= 6.0)                 12.81 >=  6.0  ok  (margin 6.81)
prop blightcap        -> coven1 (>= 5.0)               15.52 >=  5.0  ok  (margin 10.52)
prop blightcap        -> coven2 (>= 5.0)                7.21 >=  5.0  ok  (margin 2.21)
prop blightcap        -> nearest wall (>= 4.0)          4.30 >=  4.0  ok  (margin 0.30)
prop blightcap        -> land (>= 6.0)                 16.28 >=  6.0  ok  (margin 10.28)
prop blightcap        -> coven1 (>= 5.0)                6.00 >=  5.0  ok  (margin 1.00)
prop blightcap        -> coven2 (>= 5.0)               17.12 >=  5.0  ok  (margin 12.12)
prop mossBoulder      -> nearest wall (>= 4.0)          4.28 >=  4.0  ok  (margin 0.28)
prop mossBoulder      -> land (>= 6.0)                  9.01 >=  6.0  ok  (margin 3.01)
prop mossBoulder      -> coven1 (>= 5.0)               18.12 >=  5.0  ok  (margin 13.12)
prop mossBoulder      -> coven2 (>= 5.0)               13.83 >=  5.0  ok  (margin 8.83)
prop mossBoulder      -> nearest wall (>= 4.0)          4.28 >=  4.0  ok  (margin 0.28)
prop mossBoulder      -> land (>= 6.0)                  9.01 >=  6.0  ok  (margin 3.01)
prop mossBoulder      -> coven1 (>= 5.0)               12.18 >=  5.0  ok  (margin 7.18)
prop mossBoulder      -> coven2 (>= 5.0)               20.18 >=  5.0  ok  (margin 15.18)
prop rubblePile       -> nearest wall (>= 4.0)          8.38 >=  4.0  ok  (margin 4.38)
prop rubblePile       -> land (>= 6.0)                  8.60 >=  6.0  ok  (margin 2.60)
prop rubblePile       -> coven1 (>= 5.0)               13.89 >=  5.0  ok  (margin 8.89)
prop rubblePile       -> coven2 (>= 5.0)                9.06 >=  5.0  ok  (margin 4.06)

ALL CONSTRAINTS: PASS            (exit 0, 57/57 rows ok)
```

- Exit 0, every row ok; the four IO §6 numbers verbatim in the constants LAND_MIN 8.0 / WALL_MIN 4.0 / SPAWN_MIN 6.0 / COVEN_MIN 5.0 (plus the literal 8.0 coven↔coven check). All values match the valspec's own Testerbot reference rows (8.00 / 13.00 / 15.23 / 11.18 / 9.60 / 7.51, altar 14.0 / 5.39 / 6.00) — ED-5 never even needed.
- **Tightest margins:** prop→wall 4.28 (margin 0.28, mossBoulder pair), prop→coven 5.31 (0.31, steps→coven2 / 5.39 sarcophagus→coven1), skullPile→wall 4.30 (0.30). All positive, all classes clear.

**Coverage variance, adjudicated:** the delivered script prints table rows 1–8 only; rows 9 (ring closure) and 10 (validRegion re-derivation) have no printed row. Testerbot re-derived both independently (exit-gated scripts in the validation tmp dir, since removed):

```
ROW 9: 56 colliders reconstructed (8 rows × 7, region-manager axis law chord = scale×1.899);
        collider radii 17.96–19.02 m; largest collider-free arc 18.15° with mid-gap at world
        (0.0, −614.4) ≈ the door window (0, −612) within 2.44 m; second-largest arc 6.95° —
        the ONLY gap is the door window → ring CLOSED except the door gap. PASS
ROW 10: regions['veil_crypt'] present from the built registers → validRegion true. PASS (exit 0)
```

Substance of rows 9/10 verified; the missing printed rows are harness-scope drift (expected-class, ED-6 family) — **PASS with note**, not B7 (no FAIL row, ring closed, exit 0).

## V-15/V-16 — B-table adjudication (blocking classes)

| class | verified substance | verdict |
|---|---|---|
| B1 byte-purity | CONFIG.js & region-defs.js diffs: **0 minus lines**, 1 add-only hunk each; no moved/rewritten pre-existing line (minus-line census: CONFIG 0, regiondefs 0, assets 0; game.js's 3 minus lines are the V-4-substitution file, outside B1's scope) | CLEAN |
| B2 padded pass | ledger below: 10 markers, **10 distinct source rows**, max 1 hit per row (≤ 3) | CLEAN |
| B3 placement/keys | V-2.2 verified (1359 within 1357…1455); regionE key present; land/door value classes runtime-verified (probe: spawn=(0,−604), center, r 20) | CLEAN |
| B4 region-defs shape | V-3: key set exact, sides (−1,+1), walkFrom = regionE.id, arch/gatedTo explicitly null, helpers/exports untouched, connections.length 4 | CLEAN |
| B5 game.js | 3 hunks only; chain order unchanged; zero NEW CFG.regionD reads (grep exit 1); prompt strings exact | CLEAN |
| B6 art law | assets.js diff empty; 8/8 keys in manifest; no red/orange hex rows; fog/ambient rows present | CLEAN |
| B7 geometry | 57/57 rows ok; margins match reference exactly; ring closed (re-derived); script runnable, exit 0 | CLEAN |
| B8 save-safety | 14/14 PASS incl. both negative controls; THREE-free census 0; stub surface matches valspec | CLEAN |
| B9 syntax | node --check 5/5 (valspec set) + save.js + player.js = 7/7 | CLEAN |
| B10 file-set | commit touches ONLY: CONFIG.js, region-defs.js, game.js, v8-playable.html, scratch/cc-ad1/* (4), io/specs/* (2), io/reports/* (1) — subset of the Allowed set; save/player/enemy/light/spells/assets/region-manager untouched | CLEAN |
| B11 process | see Process adjudications TA-1…TA-3 below — the Devbot-commit clause did not materialize; re-verification was possible and executed from the committed artifacts | CLEAN w/ recorded variances |
| B12 build | exit 0; post-rebuild marker count 10 (≥ 8) | CLEAN |

**Contributor ledger — `veil_crypt` bundle marker count: 10 (every hit attributed; 10 distinct source rows; max hits/row = 1; ≥ 8 and ≥ 5 satisfied):**

| # | bundle line | source contributor | row character |
|---|---|---|---|
| 1 | 88520 | CONFIG.js:1349 | CC-AD1 banner comment |
| 2 | 88531 | CONFIG.js:1360 | `id: 'veil_crypt'` (registry key — load-bearing) |
| 3 | 88549 | CONFIG.js:1378 | door-shape law comment |
| 4 | 88568 | CONFIG.js:1397 | `door.land.veil_crypt` key (load-bearing) |
| 5 | 88575 | CONFIG.js:1404 | enemies contract comment |
| 6 | 88599 | CONFIG.js:1428 | cavern ring comment |
| 7 | 88608 | CONFIG.js:1437 | dignified-dead comment |
| 8 | 91284 | region-defs.js:114 | region registration comment |
| 9 | 91289 | region-defs.js:119 | connections[3] shape comment |
| 10 | 107027 | game.js:2219 | prompt-chain C8/AD1 comment |

Per-file distribution: CONFIG 7 / region-defs 2 / game 1 — CONFIG-weighted by construction (the registry id and land key live there; V-5.1 floors all pass). Comments surviving into the bundle are legitimate ledger material per N-4 (verified live: per-row comments present at bundle lines 88520–88608).

**Content-drift adjudications (expected-class, recorded):**
- **TA-4** `wall: 7` vs the valspec's `wall: 8` reference rows — law intent (< = every-2-m collider spacing) holds at 1.994 m; ring closure + 56-collider reconstruction independently verified. **PASS with note** (closest class ED-6; not B7 — all V-14 substance passes).
- **TA-5** clearance.py missing printed rows 9/10 — substance independently re-derived PASS. **PASS with note** (ED-6-family harness drift).

**Process adjudications (the disclosed situation, adjudicated not folded):**
- **TA-1 — commit landed BEFORE independent validation.** The gate order in the commit title ("Testerbot validate → IO commit+push") inverted; the trailing "(… summary here)" is literally incomplete in the commit message, corroborating the disclosed outage (prior session died mid-close-out). The commit's landing actor is IO (inline-landing precedent 31d1e64), not Devbot, so B11's letter ("ANY git commit/push by Devbot") did not fire. **PASS with note** — sequencing deviation disclosed here as the record; this report is the missing validation.
- **TA-2 — `io/reports/2026-11-06-cc-ad1-valspec.md` in the commit is a valspec copy, not a report.** `cmp` vs `io/specs/cc-ad1-veil-crypt-valspec.md` clean (exit 0). Consistent with N-1 ("a separate full-rewrite recovery file surfaced at io/reports/…; this file copied over that path is the authoritative version"). The specs copy is byte-identical, so the law validated against is the committed law. **PASS with note.**
- **TA-3 — no Devbot build-note with the four pastes.** io/reports/ carries no CC-AD1 build note (grep: only the valspec copy). B11's operative clause requires the paste absence to prevent re-verification; here everything was re-verified independently from the committed artifacts (probe 29/29, roundtrip 14/14, clearance 57/57 + rows 9/10 re-derived, ledger re-derived from the diff) — stronger evidence than a note's pastes. Harness files were committed inside scratch/cc-ad1/ contrary to their "new file, untracked, NO-GIT" delivery note; mitigation: they are the exact artifacts re-run here, and they live in the Allowed file set. **PASS with note** (variance recorded; no blocking class fired; re-gate not required — nothing blocking was discovered, and Nicko's playtest remains the final acceptance bar per the valspec's last line).

## IO post-gate slice (handoff)

IO runs these after the flip (Testerbot does not own the flip; SERVED bytes, never the repo copy):

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://172.16.5.1:8793/current/prototype/builds/v8-playable.html
curl -s http://172.16.5.1:8793/current/prototype/builds/v8-playable.html | grep -c veil_crypt
```

**Pass law:** HTTP **200** AND served-bytes `veil_crypt` count **≥ 8**. A 200-with-0-count means the flip is stale → IO re-runs the flip and re-verifies. Nicko's playtest remains the final acceptance bar.

---

**Testerbot summary:** PASS — 0 blocking (B1–B12 all clean; no ED-triggering content deviation; 5 recorded PASS-with-note adjudications TA-1…TA-5). Key numbers: bundle markers 10/10 contributors distinct (max 1/row); clearance 57/57 ok, tightest margin 0.28 m, reference values reproduced exactly; syntax 7/7 (valspec 5/5 + save.js + player.js); probe 29/29; roundtrip 14/14 (THREE-free census 0); build byte-identity TRUE (sha256 65404e7b…, 3,333,512 bytes); connections.length 4; C-side plane inertness PASS.
