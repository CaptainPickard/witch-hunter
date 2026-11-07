# CC-H5 THE TITHE VAULTS — Testerbot validation verdict (2026-11-07)

Validator: Testerbot (independent re-run; not a rubber stamp of the build note).
Base worktree: /tmp/wh-worldfeat @ HEAD 1f7f904daab17d30fa410b3b528fadaf11e52d62 (CC-H4 frozen baseline).
Inputs executed/read: spec, valspec, build note, probe source reviewed end-to-end, live files eval'd twice (config + region-defs), HEAD-pair evals from `git show 1f7f904`.

**VERDICT: PASS-with-disclosures** — 0 blocking adjudications. The five disclosed seat fixes satisfy the laws they re-seat against (independently re-derived below, not accepted from the note).

---

## Probe (V-3 execution, fresh)

- Run 1: `python3 scratch/cc-h5/solve_geometry.py` from worktree root — exit 0, **289 checks, 0 failures**.
- Run 2 (N-2 determinism): identical output, `diff` of the two transcripts empty.
- Probe design audit (N-2 anti-hardcode): node-evals the LIVE CONFIG.js + region-defs.js (fs.readFileSync + eval), generic recursive walk for every groundSeed/textureSeed, ring colliders rebuilt per the region-manager whPropColliders law (r = CONFIG.boundaryWall.collider.r (0.45, line 2588) circles along each whWall row's local X, wall-count circles, WIDTH map 'whWallA'/'whWallB' 1.899). Source scan for the spec's drifted z-literals (867.48 / -907.22 / -852.78): **zero hits** — no hard-coded spec numbers. Boss-seat width map is the cc-h3 lineage measured-extents map (region-manager colliderRadius contract `r = width * scale / 2`, region-manager.js:366-367), disclosed in the probe output as required.
- Independent validator re-derivations (no probe code reuse) matched the probe on every headline number: lane edge 1.5483 m, d95 10.8176, ring max-rho deviation 0.0049, chord spread 0.0124, K-rim/J-south gap 106.0, boss clear 6.8515 (binding okRuinColumn, footprint 0.957085*2.40/2), nest-vs-spawn 16.0 exact.

Checks executed: 289 (probe, every line counted) + 57 `- PASS`-line validator checks in this report (all assert-batch results recorded line-by-line; each batch line may assert several fields; batch scripts are quoted so any count can be re-run) = **346 discrete PASS results minimum, zero FAIL**.

## BV-0 PRE-STATE

- PASS. HEAD sha 1f7f904daab17d30fa410b3b528fadaf11e52d62; `git status --porcelain` = exactly 6 paths: M CONFIG.js, M region-defs.js, ?? io/reports/2026-11-07-cc-h5-tithe-vaults-build.md, ?? io/specs/cc-h5-tithe-vaults-spec.md, ?? io/specs/cc-h5-tithe-vaults-valspec.md, ?? scratch/cc-h5/ — the expected dirty set, nothing else.
- PASS. `git diff 1f7f904 --name-only` = prototype/js/CONFIG.js (237 lines: +235/-2), prototype/js/region-defs.js (+28/-0).
- PASS. HEAD pre-counts: zealot=0, tithe=0 in CONFIG; zealot=0 in region-defs. Live post-counts: zealot=14 (3 enemy rows + 2 body-map rows + zealot-type refs inside the rows/minions/loot-composition — recorded, composition consistent); tithe=14; region-defs zealot strings = **0**.
- PASS. `node --check` CONFIG.js rc=0 and region-defs.js rc=0 post-build (BV-0 syntax).

## V-0 CONFIG PARSES + regionK/zealot/tithecaptain ROWS COMPLETE

- PASS. Exactly one `^  regionK: {` block (CONFIG.js:2227); exactly one `id: 'tithe_vaults'`.
- PASS. regionK key set from the parse = EXACTLY the 19 spec-sec-3 keys (id, name, center, groundRadius, groundY, groundColor, groundColor2, groundSeed, scatter, spawn, gravityY, fogColor, fogDensity, ambientLightLevel, door, enemies, lairs, rotLair, props). No extra, no missing.
- PASS. Zealot row keys = exactly the 13 sec-2.1 keys (hpMax, moveSpeed, chaseSpeed, attackDamage, attackRange, attackCooldown, sightRadius, leashRadius, staggerTime, radius, aggroPingInterval, attackPhase, ai1). Spot: hpMax 60.0, sightRadius 16.0, ai1.guardArcDeg 50.
- PASS. tithecaptain row keys = exactly the 28 sec-2.2 keys. Spot: pattern 'boss-slam', slamArcDeg 100, slamTrackDegPerSec 110, scale 2.1, ai1.guardArcDeg 45, cueHot 0xd84a4a.
- PASS. Body maps: bodyByType.zealot='banditBody', animVariantByType.zealot='bandit', bodyByType.tithecaptain='banditBody', animVariantByType.tithecaptain='bandit' (sec 2.3 symmetry law).

## V-1 conn[9] SHAPE

- PASS. `D.connections.length` = 10 (was 9 at HEAD); `connectionBetween(J,K)` and `connectionBetween(K,J)` both resolve to connections[9].
- PASS. conn.from='veil_spire_approach', conn.to='tithe_vaults', axis 'z', planeCoord === K.door.planeZ === **-848**.
- PASS. doorX 0, doorHalfWidth 2.2, suspendDepthM 0, wallGapPadM 0, arch null, gatedTo null.
- PASS. walkFrom='tithe_vaults' (one-sided); interact from J (7.5, -678) r 3.5; land deep-equal {J: (2,-682) face (2,-700); K: (0,-856) face (0,-880)}.
- PASS. AMENDMENT A fades 0.3 / 0.5 / 0.8; prompt byte-exact 'E - Descend into the tithe vaults', distinct from conn[8]'s.
- PASS. `makeRegion(CFG.regionK, -1)` registered exactly once (region-defs.js:311).

## V-2 SIDES TABLE

- PASS. sideIn(conn9,K) === sideOfPlane(conn9, K spawn -856) === -1; sideIn(conn9,J) === +1; eval'd sides table {veil_spire_approach: 1, tithe_vaults: -1}.
- PASS. planeIn(J) = false, planeIn(K) = true (one-sided law).
- PASS. Source lines present: region-defs.js:334 `connections[9].sides[CFG.regionJ.id] = +1;` and :335 `connections[9].sides[CFG.regionK.id] = -1;` — quoted next to conn[8]'s precedent pair at :306-307 (`connections[8].sides[CFG.regionF.id] = -1;` / `connections[8].sides[CFG.regionJ.id] = +1;`).
- Geometry check (my own, independent): every landed walk-plane sits 2.0 m inside its destination disc's near rim — E -612/rim -576(north side by orientation), F -662 vs rim -614... the operative K pattern: K rim north = -880+34 = **-846**, plane -848 = 2 m inside. J's disc north rim -660 (J own plane -738 = its conn[8] walk-out, 2 m south of J south rim -740). Pattern-consistent; -844 would sit OUTSIDE K's rim.

## V-3 CLEARANCE PROBE (fresh)

- PASS. Ring integrity: 10 whWall rows, A/B alternating starting A (asset order verified from the parse), every row wall:10, scale 11.067, sy 11.69(A)/11.55(B), sz 2.40, y -0.2; 100 colliders r 0.45. Landed centers on the r34 circle around (0,-880): all 10 rows rho 34.0000–34.0049 (<= 0.05); north (0,-846) and south (0,-914) exact; chord spread 0.0124 <= 0.02. rotY literals 3.14 + k*0.6283 at 2dp (3.14, 3.77, 4.40, 5.03, 5.65, 6.28, 6.91, 7.54, 8.17, 8.80), strictly monotonic, row-2 x +19.98 (x-sign north→east positive).
- PASS. Door lane: nearest ring collider edge to the |x| <= 2.2 lane = **1.5483 m >= 1.0** (my independent re-derivation from the landed rows with r=0.45 circles: nearest circle (-1.051, -846.002), edge distance 1.5483 — matches probe and the disclosed 2.00-0.45 arithmetic); zero colliders in the +/-0.5 window.
- PASS. Plane-inside-disc + spawn pair: plane -848 < rim -846; spawn (0,-856) 8.0 m south of the plane; land K (0,-856) 8 m south of plane, faceZ -880 (south-facing); walk-EXIT faces the vault interior.
- PASS. K enemies: exactly 5 rows (zealot (-15,-863), (15,-863), (0,-865); ghoul (-11,-892), (11,-892)); mutuals >= 12.5 (PASS), each >= 8.0 from spawn AND from land K (same seat), ring walk-clear >= 4.45 (34 - rho), wall-edge >= 4.0, >= 5.0 from every non-ring prop row.
- PASS. Boss seat (0,-872) = the lairs ROW seat: clear circle **6.8515 >= 6.0** (AMEND-1 floor), binding okRuinColumn (footprint 0.9571, scale 2.40 → collider r 1.1485 at 8.0 m). No category excluded (all props + ring + enemies).
- PASS. nest-vs-spawn (0,-872)→(0,-856) = **16.0 exactly** (N-4 arithmetic figure).
- PASS. J-side hook (7.5,-678): nearest J prop **9.6047 >= 4.5**; >= 5.0 from J enemies and J lair/scar-reader seats; >= 4.5 from J land rows; |7.5| > 2.2 → outside J's conn[8] walk-out lane.
- PASS. Land-in (2,-682): out of BOTH J lane windows (|z-(-662)| = 20 > 0.5, |z-(-738)| = 56 > 0.5 — the lane-WINDOW law, not a bare |x| test); |dz| to J's walk-out plane -662 = **20.0 exact**; -682 < -662 (J interior side per J grammar); rho from J center within J's disc.
- PASS. K-tol band: K rim north -846 vs J ring south point -740 → **106.0 m** (within 0.5 of the 106 figure).
- Non-ring-prop census: mourningStatue x4, stoneSteps x2, okRuinColumn x3, lanternPost x1, blightcap x2, skullPile x2, mossBoulder x1 = 15; +10 ring = 25 props.

## V-4 regionJ BLOCK BYTE-IDENTICAL

- PASS. awk-extract cmp HEAD vs live: `cmp /tmp/j_head.txt /tmp/j_new.txt` **clean** (regionJ byte-identical, anchored `  regionJ: {`).
- PASS. J props 25 rows at both HEAD and live; tally identical: {mourningStatue 4, stoneSteps 2, okRuinColumn 3, blightcap 2, lanternPost 1, skullPile 2, mossBoulder 1, whWallA 5, whWallB 5} (N-3d catch). J enemies 2 + scar-reader lair unchanged (HEAD-pair census).
- PASS. makeRegion(CFG.regionJ, -1) exactly one hit, unchanged shape.

## V-5 FRESH SEED + REGION CONSTANTS

- PASS. Generic seed walk (eval'd, not a hard-coded list): **22 seed keys**; regionK.groundSeed=448271909 and NO other line carries 448271909. Inventory walked: C 1662061217, D 1662061218, E 1662061219, F 1662061329, G 1662061440, H 1662061651, I 1662061654, J 1662061763, J.rotLair.pool.textureSeed **20261107**, K.rotLair.pool.textureSeed 448271910, roads x9 20261008 (groundSeed list matches the valspec's HEAD inventory exactly).
- PASS. K constants: groundY 0, scatter false, gravityY -22, groundRadius 34.
- PASS. K pool textureSeed 448271910 recorded; K ≠ J live (20261107 vs 448271910); the valspec's FINAL law constrains only the groundSeed. (Stale valspec head-inventory note adjudicated under Disclosures.)

## V-6 ONE CRIMSON ACCENT FAMILY

- PASS. lanternPost === 1, blightcap === 2. Remaining non-ring assets exactly {mourningStatue x4, stoneSteps x2, okRuinColumn x3, skullPile x2, mossBoulder x1}; non-ring 15, total props 25 (matches the valspec FINAL count).
- PASS. rotLair dressing hex-verified from the parse: light.color 14176336 = 0xd85050; pool.color 1707794 = 0x1a0f12; pool.color2 2756886 = 0x2a1116; pool.speck 5906472 = 0x5a2028; pool.radius 8; pool.rings 5; fog.showWithinM 70; cullM 170. All six asserted values exact.

## V-7 regionI + connections[0..8] BYTE-IDENTICAL

- PASS. regionI block extract cmp HEAD vs live: **clean**.
- PASS. conn span (file start through `connections[8].sides[CFG.regionJ.id] = +1;`, line 307 in BOTH versions — line numbers coincide because the round appended only after it): cmp **clean**; all new round text (registration :311, conn[9] push, sides :334-335) sits strictly AFTER the conn[8] J-sides line.
- PASS. `grep -c "connections\[9\]"` = 2 (the two sides lines); makeRegion I/J/K each exactly one hit.

## V-8 SURFACE DISCIPLINE

- PASS. Dirty set = the 6 allowed paths only (see BV-0). No enemy.js / game.js / save.js / region-manager.js / daynight.js / index.html / assets / CSS / builds changes.
- PASS. `git diff 1f7f904` over the named no-touch files: **EMPTY**.
- PASS. hazard count HEAD 0 → live 0 (delta zero; trap not landed).
- PASS. prototype/builds/ untouched.

## V-9 ZEALOT WIRED ENGINE-SIDE WITHOUT ENGINE EDITS

- PASS. C.enemy.zealot truthy; key list carries NO `pattern` key and NO `slam*` keys (hasPattern false, hasSlamKeys []) → cfgFor fall-through returns the row as-is, ai1 survives with guardArcDeg 50.
- PASS. Body/anim rows asserted in V-0 (bandit chassis symmetry).
- PASS. enemy.js consumption quoted for the record: `:152 this.lair = this.cfg.pattern === 'boss-slam' && this.cfg.lair ? newLair(this.cfg) : null;` (zealot → lair null); ai1For (≈:51) reads `enemy.cfg.ai1` independent of pattern. No engine change needed or made (V-8's empty diff proves it).

## V-10 TITHECAPTAIN WIRED

- PASS. pattern 'boss-slam' (spot re-recorded from the parse).
- PASS. lairNest ENGINE formula eval: L.region 'K' → C['regionK'] resolved; nest = {x: 0 + L.x, z: -880 + L.y} = **(0, -872)**; lairs row {type:'tithecaptain', x:0, z:-872} exists; **match === true** (sign law: lair.x → center.x, lair.y → center.z).
- PASS. Save-letter composition: L.flagPrefix 'tithecaptain' + lair region 'K' → `tithecaptain_cleared_K` (enemy.js:1691 `lairFlagPrefixed` composition law, static assert; scarreader_cleared_J precedent shape).
- PASS. minions {asset 'zealot', cap 2, interval 7, range 5, dieOnMasterDeath true}. loot deep-includes [{mat:'stolenCoin', n:[1,3]}]; C.items.stolenCoin = {id:'stolenCoin', name:'Stolen Coin', glyph:'SC', category 'valuable', stackCap 999}.
- PASS. ai1 guardArcDeg 45 (smaller window than the zealot's 50). rearm {days 3, trigger 'proximity', radius 14}; lairRadius 16.

## V-11 FOG/DARKNESS MATH

- PASS. fogDensity 0.16; d95 = sqrt(-ln 0.05)/0.16 = **10.8176** in [10.77, 10.87].
- PASS. J density 0.15 recorded (J d95 from the parse = 11.5391; chain K < J holds); ambient STRICT chain 0.045 < 0.05 < 0.055 (K < J < F).
- PASS. K.fogColor 657424 = **0x0a0810**, identical to J's landed fogColor 657424 (veil family).

## V-12 ZEALOT SEATS LIVE ONLY IN K; NO K/J ROW COLLISION

- PASS. Region census from the eval: regionK zealot = **3**, every other region = **0**; K also carries ghoul x2 + LAIR:tithecaptain x1 (5 enemy rows / 1 lair). HEAD-pair census identical for all ten pre-existing regions (only regionK added).
- PASS. region-defs.js zealot strings = 0; CONFIG grep composition recorded (14 = 3 type rows + 2 body-map rows + in-row references).
- PASS. K-originated seats vs J's landed rows all above their V-3 floors (hook 9.6047 m to nearest J prop; land/window checks in V-3).
- PASS. Structural z-order: all K rows z <= -846 (max = the north ring row (0,-846)); all J rows z >= -740 (min = J's south ring point (0,-740)); 106 m gap holds structurally.

## N-1 row-key drift — PASS

Every sec-2 key asserted by name against the parsed rows (V-0); the four body-map rows exact; zealot keeps hpMax-shape keys (hpMax, moveSpeed, sightRadius — matches the trash-row engine grammar, not pattern-row hp/dmg/speed); guardArcDeg 50 vs 45 distinguishes the rows — no cross-row copy-drift.

## N-2 ring-row drift — PASS

Probe re-derives all ten rows from LANDED CONFIG rows (rho == 34.0 ± 0.05 all 10: max deviation 0.0049 — north/south rows exact; chord uniformity 0.0124 <= 0.02); asserts against the circle law, never the sec-3 literals (anti-hardcode scan zero hits); double-run determinism diff clean; rotY monotonic with north→east x-positive.

## N-3 J contamination — PASS

(a) regionJ block cmp byte-identical; (b) conn span 0..8 cmp byte-identical (new text only after the conn[8] J-sides line); (c) census zealot 3-in-K / 0-elsewhere; (d) J asset tally HEAD == live exact. No hook/land rows inside J (they ride regionK.door + conn[9]).

## N-4 lairNest sign — PASS

Engine-formula nest (0,-872) equal to the lairs row (match true — a (0,-888) or (0,-880) mistake shape would fail this equality); nest-vs-spawn = 16.0 exact (±0.5 law); boss-seat clear circle computed AT the row seat (probe: `seat = point(K['lairs'][0])`) = 6.8515 >= 6.0.

## N-5 sideIn sign — PASS

sides[K] = -1 (NOT conn[8]'s +1 copy mistake), sides[J] = +1; sideIn(K) === sideOfPlane(K spawn -856) === -1; sideIn(J) === +1; planeIn(J) false / planeIn(K) true; source-line pair present (rd :334-335) and conn[8] precedent pair (:306-307) quoted above. Geometry rationale verified from the parse: K interior (-880/-856) SOUTH of plane -848 (sideOfPlane z > planeCoord ? 1 : -1 → -1); J interior NORTH of it (+1); J is the pocket parent (conn[7]/conn[8] convention).

## BV-6 BUILD VALIDATION

- `grep -c tithe_vaults prototype/builds/v8-playable.html` = **0** → no pre-built bundle with tithe markers at verdict time (the on-disk v8 bundle is HEAD's CC-H4 artifact, sha256 195a7bc90d017823ea3ec81f6729acca04354de2a194374cdc1668586c797cae). Per the valspec: record "no pre-built bundle at verdict time — IO builds at close-out"; the verdict rests on BV-0, V-0..V-12 and N-1..N-5.

---

## Build-note disclosure verification (claims treated as claims, re-checked)

1. **Walk-out plane -844 → -848 (fix 1)**: VERIFIED ACCURATE and law-compliant. -844 is outside K's rim (-846) — my independent rim table from the parse shows every landed plane 2 m inside its disc; -848 restores the 1.5483 m lane-edge figure (re-derived from landed rows, matches note's 2.00-0.45 arithmetic). Valspec V-1's -844 figure and V-3's 12 m figures are the superseded spec-literal form; the valspec's OWN law (plane < center + r; spawn south of plane) HOLDS at -848.
2. **N-5 enemy-seat rescue (fix 2)**: VERIFIED. K enemies landed at (-15,-863)/(15,-863)/(0,-865); all V-3 enemy floors hold post-move (probe mutual/spawn/prop/wall floors green); north center zealot (0,-865) sits exactly 9.0 m from the landing row (0,-856) = ADJ-E's defended floor.
3. **Colossus (0,-876) → (0,-880) (fix 3)**: VERIFIED. Boss-seat clear 6.8515 >= 6.0 at the row seat; N-4 16.0 exact (856→876 = 20 would have failed; the landed config pairs the -880 colossus with the -872 nest correctly).
4. **Ring rows re-derived to the strict circle (fix 4)**: VERIFIED. Landed rows on r34 within 0.0049; chord spread 0.0124; sec-3 z-literals treated as context per the correction ledger (a). The one skullPile nudge (6,-908)→(8,-908) preserves the 4.0 prop-mutual floor (probe green).
5. **Spawn/ping-pong (fix 5)**: VERIFIED. Spawn (0,-856) = 8.0 m south of the -848 plane (not on the plane line); exit face -880 (south-facing); no re-trigger geometry.
6. **ADJ-D ai1-vs-boss-slam**: VERIFIED from HEAD enemy.js source (ai1For reads cfg.ai1 with no pattern branch; pattern branches exist only at :34 (deriveCfg) and :152 (lair); the ai1For call sits inside the update flow (:357) before slam-specific branches; the guard takeDamage hook keys `this.cfg.ai1`). Contingency did not fire; no IO escalation needed.
7. **Stale valspec seed inventory**: VERIFIED as the build note describes — valspec's head-inventory line listed J's pool textureSeed as 448271910, but the live parse shows J.rotLair.pool.textureSeed = **20261107**; K pool 448271910 = K groundSeed + 1, unique among pools. V-5's law (groundSeed uniqueness) unaffected: 448271909 unique among all 22 walked seeds. Non-blocking record.
8. **Footprint/collider law**: VERIFIED — region-manager.js:366-367 `colliderRadius(name, width, scale)` = width*scale/2, meta-driven; no trunk-ratio asset appears in K's tally (mossBoulder present, no tree assets); the disclosed map (blightcap 1.6921 / lanternPost 0.5854 / mossBoulder 1.8974 / mourningStatue 1.8620 / okRuinColumn 0.9571 / skullPile 2.0000 / stoneSteps 1.9483 / whWallA|B 1.8990) is the map the probe prints.
9. **CONFIG deletions**: exactly 2 `-` lines, both the disclosed body-map rows (scarreader body-map comment line + animVariantByType row this round extends). CONFIG.js +235/-2; region-defs.js +28/-0 (additions-only).
10. **J blocks byte-identity claim ("J blocks regionJ/regionI + conn[7]/[8] byte-identical")**: VERIFIED by cmp ×3 (regionJ block, regionI block, conn span 0..8).

## Adjudications (non-blocking; zero blocking)

- **Plane -848 vs valspec's stated -844 (+ lane/12 m figure deltas)**: NON-BLOCKING. Disclosed engine-law fix; the valspec's own inside-disc law and pair law PASS at -848 (verified independently); every V-1/V-3 assert re-derived from the LANDED value.
- **N-5 flank seats re-seated, colossus moved to (0,-880), ring rows on the strict circle, skullPile nudge**: NON-BLOCKING. All disclosed; all floors they re-seat against verified green post-move.
- **ADJ-E 12 m → 8 m**: NON-BLOCKING. Disclosed consequence of fix 1; ADJ-E's defended floor (landing row → nearest enemy 9.0 m) intact; spawn not on the plane line.
- **Stale valspec head-inventory textureSeed note (J 20261107 not 448271910)**: NON-BLOCKING. Valspec inventory line is a stale head-time note; the LIVE law (groundSeed uniqueness + record) passes.
- **Sec-5 'every K prop >= 32' figure**: handled per correction ledger (b) — recorded informational (whole-ring minimum reading passes; nearest-prop floor 5.0 governs and passes at 20.0 m for the colossus).
- **V-11's J d95 annotation (11.6179)**: the valspec's prose figure is slightly off the strict math (11.5391 from density 0.15); recorded from the parse as instructed; no assert binds on it. NON-BLOCKING.
- **rotY literals at 2dp (5.03 vs analytic 5.0249)**: sub-cent-rounding noise on the 3.14 + k*0.6283 lattice; the operative laws (rho on-circle, bearing step via the probe's 0.002 rad check, monotonic rotY, x-sign) all PASS. NON-BLOCKING.
- **No pre-built bundle at verdict time**: per valspec BV-6 path — IO builds at close-out.
- **Probe footprint-map disclosure**: the boss-seat computation runs on the measured-extents width map (cc-h3 lineage), printed in the probe output as required by the valspec. Expected non-blocking class.

## Result

All 13 V-items PASS, all 5 N-items PASS, BV-0 and BV-6 per their paths, zero blocking adjudications, probe fresh-run 289/0 deterministic exit 0, five disclosed seat fixes verified accurate against the laws, all five build-note disclosures verified against source/parse.

**VERDICT: PASS-with-disclosures**
