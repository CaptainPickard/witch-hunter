# CC-H4 'The Scar-Reader' — BUILD NOTE (devbot lane, 2026-11-07)

Status: BUILT + probe-green. Worktree /tmp/wh-worldfeat @ HEAD 3253711
(feat/world-visuals). Files changed: CONFIG.js (+69/−2), enemy.js
(+21/−7), assets.js (+5). game.js / region-manager.js byte-identical to
the frozen baseline (sha256 verified). NO commit, NO push, NO build_vX,
NO harness, NO browser (per build law). Spec files untouched.

## 1. lairs-row shape consumed by live code (V-5 / N-2 ruling)

**The row CARRIES `x: 0, z: -709` (regionD legacy shape), NOT the bare shape.**

Evidence chain (read from the worktree, not assumed):
- `region-manager.js` buildRegion (~1909-1912): `regionCfg.enemies.concat(
  regionCfg.lairs || [])`, then `new window.WH_Enemy(e.type, this.scene,
  regionId, e.x, e.z)` — **row `e.x`/`e.z` are consumed directly**.
- `enemy.js` Enemy constructor (~86-98): `this.spawn = { x: spawnX, z:
  spawnZ }`; `this.pos = new THREE.Vector3(spawnX, 0, spawnZ)`.
- Bundled THREE r185 (`prototype/vendor/three.classic.js:4836`):
  `constructor(x = 0, y = 0, z = 0)` — **default parameters, so
  `Vector3(undefined, 0, undefined)` seats the body at world (0,0), NOT
  NaN**. Nothing re-seats a lair boss at the nest (grep: no code moves
  this.spawn to lairNest). `this.spawn = { x: undefined, ... }` would
  additionally write NaN through `Vector3.set()` (line 4865, no default
  params) into `this.pos` on REVIVE.
- The nest itself (pool / crimson light / fog / save letter 'J') is
  INDEPENDENT of row x/z: `lairNest` derives it from
  `CONFIG.enemy.scarreader.lair` (x 0, y = z -9, region 'J') against
  regionJ center (0,-700) — the two shapes agree at world (0,-709).

Conclusion: a bare `{ type: 'scarreader' }` row would spawn her body at
world (0,0,0) — that is region A's ground — and NaN her on revive, while
her lair machinery (tick pool radius, socket id, save letter) still reads
correctly from `.lair`. regionD's rotmother row carries "stale" x/z
(-186,-180.2 — row z says -180.2, lairNest says -174) which confirms the
row position is the LIVE seat and lairNest is the dressing/nest anchor.
Therefore the AMB-2-allowed carriage is MANDATORY here, disclosed per the
spec sec 3b note. Both shapes are regex-tolerated by the probe and the
verifier.

## 2. Tint decision (spec sec 2.3): SKIPPED + DISCLOSED

The optional `tintMaterial`/`tint` hook is NOT landed. Reason (isolation
proof not provable cheaply from static source):
- `assets.js` `instance()` (~840) hands out `cloneTemplate(name, tmpl)`
  (~828). For an unrigged body (no CHARACTERS row) that is
  `tmpl.clone(true)` — THREE's deep Object3D clone.
- THREE r185 `Object3D.clone(true)` (recursive, `clone.recursive` path)
  clones the Object3D hierarchy but **copies material references by
  reference** (Material objects are not duplicated by Object3D.clone).
- Consequence: if setBody tinted the first MeshStandardMaterial without
  cloning it, ONE shared material object would be hit — but only for
  scarreaderBody INSTANCES (the rotmother reads her own separate cached
  template from a separate manifest key → separate cache[name] → separate
  template; same URL loaded twice under different names does not merge in
  `loadByName`, which is per-name with no URL deduplication).
- So the rotmother was never at risk, but proving per-instance isolation
  across all Scar-Reader instances (each `instance('scarreaderBody')`
  shares the one template's materials until a clone happens) requires a
  runtime assertion that static source cannot give. Per the spec: "If
  Devbot cannot prove isolation, SKIP the tint and disclose."
- Disclosed skip = PASS per the valspec; the crimson cue + the scar-pool
  dressing carry the art accent; the body stays the pale rot chassis.
- The `cueDark/cueHot` rows are landed regardless (see §4), and the
  manifest entry is in place with a comment naming the skip; a later
  round can land tint with a clone-based helper (the region-manager
  `whTintObject` precedent at region-manager.js:1704 clones per mesh
  before multiplying — that helper mutates only the instance passed in,
  which setBody could reuse with the same clone-first contract).

## 3. Save generalization (D1-D4)

- `lairOnDeath` (~1301): `LAIR_STATE[L.nest.letter] = { cleared: true,
  day: gameDay(), prefix: (this.cfg.lair && this.cfg.lair.flagPrefix) ||
  undefined }` — the scarreader entry carries prefix 'scarreader'; the
  rotmother's row has no flagPrefix → prefix: undefined (plain entry,
  byte-equal capture output `rotmother_cleared_X`).
- `captureLairs` (~1678): `out[(st.prefix || 'rotmother') +
  '_cleared_' + letter] = st.day`.
- `restoreLairs` (~1686): regex `/^([a-z][a-z0-9]*)_cleared_([A-Z])$/`
  accepting ANY lowercase prefix; old `rotmother_cleared_C` keys match
  with group 1 = 'rotmother'. The LOADED prefix is stored on the entry
  (`prefix: m[1]`), so a re-capture re-emits the same key shape the
  profile came with (stable round-trip, AMB-6).
- All LAIR_STATE read sites audited: lairTick (st.cleared/st.day),
  lairDressingTick (st.cleared), lairSockets (st.cleared),
  captureLairs (st.cleared/st.prefix/st.day), restoreLairs (writer).
  None require the prefix field to exist; plain entries keep working
  (D4).
- Verifier round-trip (static port of the exact new logic, run against
  real shapes): capture emits `scarreader_cleared_J` + byte-equal
  `rotmother_cleared_C`; restore of a PRE-H4 save `{rotmother_cleared_C:4}`
  yields prefix 'rotmother' and re-capture byte-equal; both keys round-trip.
  0 failures across all D-family checks.

## 4. Cue decision note (V-17/18, R1, AMB-3)

- `buildSlamCue`'s lazy init line (~1601) is BYTE-UNCHANGED:
  `if (!CUE_DARK) { CUE_DARK = new THREE.Color(0x101a08); CUE_HOT = new
  THREE.Color(0xa8d84a); }` (verified by diff — the line is untouched).
- `slamCueShow` (~1605) resolves colors PER-ELEMENT per AMENDMENT R1:
  `dark = (this.cfg && this.cfg.cueDark) ? CUE_DARK.clone().setHex(
  this.cfg.cueDark) : CUE_DARK` and the mirror for hot/cueHot. A missing
  key falls back to the SHARED constant for that element alone — a row
  with neither renders the exact current green pair (rotmother path
  byte-equal in behavior; no undefined lerp is possible since a fallback
  always exists). The `.clone().setHex()` pattern avoids mutating the
  shared constants themselves (setHex on the shared Color would poison
  the rotmother's cue globally).
- scarreader row carries `cueDark: 0x1a0508, cueHot: 0xd84a4a` (crimson
  telegraph, concept-08 family). The buildSlamCue MATERIAL constructor
  color (0x101a08) stays as-is — it is only the pre-show color; slamCueShow
  overwrites it on every visible frame.

## 5. Probe — BOTH raw stdouts (byte-identical, exit 0 twice)

Probe file: `scratch/cc-h3/scc_lair_probe.py` (NEW, python3 stdlib only;
parses CONFIG.js worktree text reusing the cc-h3
solve_geometry.py collider footprint table; NO THREE/node/browser/
harness/build_vX; string-aware brace scanner because CONFIG boss rows
carry brace-bearing comments/strings). Run from /tmp/wh-worldfeat twice
back-to-back; diff = 0 bytes (cmp-verified).

RUN 1 stdout:
```
(a) nest parse: regionJ center (0,-700) + lair x 0 y -9 -> world (0,-709)
(a) nest parses to world (0,-709): PASS computed (0,-709)
(b) regionJ prop parse: 15 non-ring rows, 10 ring rows (90 ring colliders)
(b) clear circle centered AT nest (0,-709): 6.6848 m  (binding: mourningStatue at (-7,-712) at (-7.00,-712.00))
(b) clear circle >= 6.0 m: PASS 6.6848 m
(c) REPORT: props inside slam reach r 7.5 (2, reported not failed):
      VIOLATOR mourningStatue at (-7,-712) at (-7.00,-712.00): edge 6.68 m inside reach 7.5
      VIOLATOR mourningStatue at (7,-712) at (7.00,-712.00): edge 6.68 m inside reach 7.5
(d) ghouls at [(-15, -708), (15, -708)] vs nest (0,-709): 15.0333 m, 15.0333 m
(d) both ghouls >= 8.0 m from nest: PASS distances 15.033 / 15.033 m
socket rows: rotmother(lair region D), scarreader(lair region J)
(e) lairSockets census (per boss-slam row, no save block = armed):
      D -> boss rotmother socket id rotLair@-186,-174 (rotLair.light present: True)
      J -> boss scarreader socket id rotLair@0,-709 (rotLair.light present: True)
(e) exactly one scarreader socket in regionJ: PASS regionJ count 1
(e) regionJ socket id rotLair@0,-709: PASS got ['rotLair@0,-709']
(e) exactly one rotmother socket in regionD: PASS regionD count 1
(e) zero duplicate rotLair@ ids: PASS
(e) AMB-1 gate: no socket count changed outside regionJ(+D baseline 1): PASS lair-row regions census {'D': 1, 'J': 1}
(e) every socket backed by rotLair.light: PASS
(f) textureSeed 20261107 occurs 1x in CONFIG.js; seed families (count per value): {20261008: 9, 20261012: 1, 20261013: 1, 20261107: 1}
(f) textureSeed 20261107 unique (exactly 1 occurrence): PASS
--- failures: 0 ---
SUCCESS: all structural checks pass
```

RUN 2 stdout: BYTE-IDENTICAL to run 1 (diff empty, verified by cmp).
Raw run-2 capture, verbatim, for the record:

```
(a) nest parse: regionJ center (0,-700) + lair x 0 y -9 -> world (0,-709)
(a) nest parses to world (0,-709): PASS computed (0,-709)
(b) regionJ prop parse: 15 non-ring rows, 10 ring rows (90 ring colliders)
(b) clear circle centered AT nest (0,-709): 6.6848 m  (binding: mourningStatue at (-7,-712) at (-7.00,-712.00))
(b) clear circle >= 6.0 m: PASS 6.6848 m
(c) REPORT: props inside slam reach r 7.5 (2, reported not failed):
      VIOLATOR mourningStatue at (-7,-712) at (-7.00,-712.00): edge 6.68 m inside reach 7.5
      VIOLATOR mourningStatue at (7,-712) at (7.00,-712.00): edge 6.68 m inside reach 7.5
(d) ghouls at [(-15, -708), (15, -708)] vs nest (0,-709): 15.0333 m, 15.0333 m
(d) both ghouls >= 8.0 m from nest: PASS distances 15.033 / 15.033 m
socket rows: rotmother(lair region D), scarreader(lair region J)
(e) lairSockets census (per boss-slam row, no save block = armed):
      D -> boss rotmother socket id rotLair@-186,-174 (rotLair.light present: True)
      J -> boss scarreader socket id rotLair@0,-709 (rotLair.light present: True)
(e) exactly one scarreader socket in regionJ: PASS regionJ count 1
(e) regionJ socket id rotLair@0,-709: PASS got ['rotLair@0,-709']
(e) exactly one rotmother socket in regionD: PASS regionD count 1
(e) zero duplicate rotLair@ ids: PASS
(e) AMB-1 gate: no socket count changed outside regionJ(+D baseline 1): PASS lair-row regions census {'D': 1, 'J': 1}
(e) every socket backed by rotLair.light: PASS
(f) textureSeed 20261107 occurs 1x in CONFIG.js; seed families (count per value): {20261008: 9, 20261012: 1, 20261013: 1, 20261107: 1}
(f) textureSeed 20261107 unique (exactly 1 occurrence): PASS
--- failures: 0 ---
SUCCESS: all structural checks pass
```

Numbers: nest (0,-709) exact; clear circle 6.6848 m >= 6.0 (binding
obstacle = mourningStatue row at (-7,-712), the intended blocker);
ghouls 15.0333 m each >= 8.0; sockets 1+1 with zero dupes; seed families
{20261008 x9 pre-existing path tiles, 20261012 den pool, 20261013 den
stains, 20261107 scar pool} — 20261107 occurs exactly once.

## 6. Independent verifier (beyond the probe)

A second static verifier (HEAD-vs-worktree git show diff) checked: all
10 regions' key sets unchanged except regionJ gaining exactly
{lairs, rotLair}; all pre-existing CONFIG.enemy rows byte-identical
(bandit, ghoul, wolf, coven, rotmother, rotspawn, animVariantByType,
hpbars...); bodyByType/rigidAnimByType gained only scarreader;
CHARACTERS map byte-identical; assets manifest scarreaderBody row exact;
game.js + region-manager.js byte-identical; deeds/xpSources gained only
kill_scarreader (8 / 200); WH_ENEMY_TYPES order preserved + gained
scarreader; capture/restore round-trip (above). exit 0.

## 7. Deviations

1. **Lairs row shape = x/z carriage** (`{ type: 'scarreader', x: 0,
   z: -709 }`) instead of the AMB-2 bare default. Disclosed in §1 —
   the bare shape would seat her body at world (0,0). The spec's own
   Engine FACT note sanctions exactly this disclosure path.
2. **Tint hook skipped** (spec sec 2.3 optional): disclosed in §2.
No other deviations. No spec defects requiring amendment requests.

## 8. Amendment requests

None. The specs were followed literally; both engine-fact disclosures
(shape + tint) route through paths the specs themselves pre-authorized.

## 9. Git state

Uncommitted (IO commits): M CONFIG.js, M assets.js, M enemy.js;
?? scratch/cc-h3/scc_lair_probe.py, scratch/cc-h4/ (baseline, IO-frozen),
io/specs/*.md (IO-owned). Read-only git used only (git show / status /
diff / log).
