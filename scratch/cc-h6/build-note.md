# CC-H6 The Remains — build note (Devbot)

Round: CC-H6 (delve strata V5 THE REMAINS, regionL, off the Tithe Vaults)
Worktree: /tmp/wh-worldfeat · branch feat/world-visuals · HEAD e20f61d
Specs: io/specs/cc-h6-remains-spec.md (sec 2/2b/4/5/6 build contract) +
io/specs/cc-h6-remains-valspec.md (CH-1..CH-6, G-01..G-12, SR-1..SR-4)

## Files touched (the complete census)

| File | Change |
|---|---|
| prototype/js/CONFIG.js | +regionL row (sec 2+2b: 13 props incl. 10 re-derived ring rows), +lastchancel enemy row (sec 5), +bodyByType.lastchancel / +animVariantByType.lastchancel |
| prototype/js/region-defs.js | +regions[the_remains] = makeRegion(CFG.regionL, -1) at the line-311 neighbor position, +conn[10] block (J->K grammar mirrored) with the E-mirror sides comment |
| prototype/builds/v8-playable.html | rebuilt via tools/build_v8.py (newest builder; ls tools/ census: build_v7.py, build_v8.py — v8 is the newest) |
| scratch/cc-h6/solve_geometry.py | NEW — CONFIG-ROW-PARSED probe |
| scratch/cc-h6/save_roundtrip.js | NEW — THREE-free save/lair-key probe |

Engine files (enemy.js, region-manager.js, save.js, daynight.js, …): ZERO
edits — verified by `git status --porcelain` (only the 3 files above modified,
only the 2 spec files + scratch/cc-h6/ untracked). NO-GIT honored: nothing
staged, nothing committed, nothing pushed.

## Probes (both run twice, byte-identical)

- python3 scratch/cc-h6/solve_geometry.py → 44/44 sec-6 laws PASS, exit 0,
  G-01..G-12 verbatim + 12 CONFIG-ROW-PARSED parse lines. Digest
  d1a9671073506eb6676d46f924449e6cc79e9241 (run1 == run2, diff empty).
- node scratch/cc-h6/save_roundtrip.js → 18/18 PASS (SR-1..SR-4 incl. the
  lastchancel_cleared_L key round-trip through WH_Enemy.restoreLairs /
  captureLairs + malformed-key negative). Digest
  e532061eb21aea08566c769baedfe02e04f94315 (run1 == run2, diff empty).
- Both files `node --check` clean; CONFIG.js/region-defs.js eval THREE-free.

## Key probe figures (from the LANDED rows)

- Ring: rho spread 0.0000 (worst 0.0025 vs r30 circle), chord max-dev 0.0025
  (law 0.02), rotY ladder exact, lane edge 2.00 m (law 1.0).
- Boss-seat (0,-1060): 7.281 (per-row map) / 7.352 (fixed map), law 6.0.
- Prop floors: raw 4.726 (law 4.0), mutual edge 2.657 (law 2.0).
- Hook K-clearance 7.563 colliders (law 4.0), captain-circle margin 3.50
  (law 2.0), K rows all >= 4.0.
- Lair trio: nest == lairs row == center+y == (0,-1060); conn[10] sides
  K +1 / L -1; planeIn L-only; save key letter L.

## Landed-vs-spec adjudications (letter-vs-landed table; laws stay floors)

1. **Ring rows re-derived at strict 2dp** (sec 2b literals are context):
   chord 18.5410 → scale 9.7630; centers from the exact (90 − 36k)° ladder;
   rotY = 3.14 + k·0.6283 carried at 2dp → rows k=3/k=9 carry 5.02/8.79 (the
   spec table's 5.03/8.80 rounds the exact ladder the wrong way; the probe's
   law-6 asserts the formula and passes on 5.02/8.79). Precedent: CC-H5's
   identical amendment (valspec V-3/N-2 law: rho on the LANDED rows).
2. **stoneSarcophagus seat (0,-1086)** (sec 2b said (0,-1078)): the literal
   bound the boss-seat clear circle at 2.75 m (law 6.0); −1086 restores
   7.281. Amendment per the H5b precedent (probe failure amends the seat,
   never the law).
3. **skullPile east (12,-1090)** (sec 2b said (12,-1084)): the literal sat
   0.11 m from the re-derived k=4 ring band (the table was authored against
   the drifted ring); (12,-1090) gives raw ≥ 4.73.
4. **blightcap pair (±16,-1047)** (sec 2b said (13,-1046) mirrored): the
   literal seats sit 2.30/2.79 m inside the k=9/k=1 band dips (band minimum
   radius 21.4 from center); nearer alternatives are blocked by the
   mossBoulder mutual-2.0 floor; (±16,-1047) clears every band ≥ 4.92 and
   every mutual ≥ 2.98.
5. **guardArcDeg 42** (sec 5 prose gloss says "45 − captain 50"; the sec-5
   FIELD line for lastchancel says guardArcDeg 42) — the field governs;
   probe law 38 pins 42.
6. **Non-changes (adjudicated, none required)**: spawn/land/plane/hook rows
   landed exactly per sec 4 (the J->K block mirrors conn[9] one stratum
   down); the minions cap-0 guard row landed exactly (engine law:
   lairTick reads cfg.minions.interval unguarded, enemy.js ~1285-1290); the
   lair trio agrees at (0,-1060); save key lastchancel_cleared_L round-trips.

## Build

- tools/build_v8.py (newest build_vX) → prototype/builds/v8-playable.html,
  3,518,948 bytes, sha1 ab7972f6b154bbb4bb07cbf6cdf76f38abd8922c,
  stamp `(build 11-07 16:10Z e20f61d)` (deterministic HEAD stamp), the
  regionL rows inlined (the_remains ×4 in the bundle).
- CONFIG.js after: 90ccf383f692ec1bb37063ea7a601514f4d9141b
  (baseline dfcef3bea4e080baa2a7670e407ce7163833842d)
- region-defs.js after: 578850bd9e2d120fe074e8e21b48b2e669fbd5b0
  (baseline 2193a5a53c46d2183c8e065d24da1bd74a72ba6c)

## No-touch census confirmation

`git status --porcelain` after all work shows exactly: M CONFIG.js,
M region-defs.js, M prototype/builds/v8-playable.html (build stamp output),
?? io/specs/cc-h6-remains-*.md (IO's own files), ?? scratch/cc-h6/ (this
round's probes + this note). No *.js engine file, no index.html, no
style.css, no tools/, no memory of any other path touched. Nothing staged,
nothing committed, nothing pushed.
